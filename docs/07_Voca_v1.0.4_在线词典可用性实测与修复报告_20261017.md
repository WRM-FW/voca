# Voca v1.0.4 在线词典可用性实测与修复报告（20261017）

v1.0.3 发布说明里"具备诚实的网络与词条状态检测……绝不将空白页或失败状态伪装为正常查询结果"这句话，经真机联网复验**不成立**。本报告给出根因、逐条实测数据与 v1.0.4 的实际修复。

## 一、测试环境

Windows 11 26200 / x64，真实外网出口，`Edg/155.0.4283.45`。方法：CDP 驱动真实页面加载 `index.html`，同时监听 `Network.responseReceived` / `Network.loadingFailed` 抓底层响应头与失败原因；另用 Python 直连各端点核对响应头；截图留证。

## 二、三家站点的真实能力边界（实测响应头）

| 端点 | HTTP | `x-frame-options` | CSP `frame-ancestors` | `access-control-allow-origin` | 能否内嵌 | 能否抓取解析 |
| :--- | ---: | :--- | :--- | :--- | :--- | :--- |
| `dict.eudic.net/dicts/en/<w>` | 200 | **SAMEORIGIN** | — | `*` | **否** | 是 |
| `dict.eudic.net/mdicts/en/<w>` | 200 | **无** | 无 | `*` | **是** | 是 |
| `www.iciba.com/word?w=<w>` | 200 | **无** | 无 | `*` | **是** | 否（释义由脚本渲染，HTML 里没有） |
| `www.wordreference.com/enzh/<w>` | 200（需先过反爬） | **SAMEORIGIN** | **`'self' https://wordreference.com https://*.wordreference.com https://lextutor.ca …`** | 无 | **否** | **否** |

关键取证（WordReference 成功响应 200 的完整头）：

```
x-frame-options: SAMEORIGIN
content-security-policy: frame-ancestors 'self' https://wordreference.com
    https://*.wordreference.com https://lextutor.ca https://*.lextutor.ca
    https://cssps.gouv.qc.ca ... https://exam.net https://*.exam.net;
server: nginx/1.31.6
```

**`frame-ancestors` 是一份明确的白名单，Voca 不在其中。** 加上没有 CORS 头，所以 WordReference 的词条内容在"纯客户端、不引第三方代理"的架构下**不可能**出现在 Voca 窗口内。这不是 Voca 的 bug。

另外 WordReference 首访会返回 HTTP **418**，响应体是一段 JS 反爬挑战（Anubis）：设置 `nginx_wr_human=1` cookie 后 reload。实测该挑战在**顶层标签页**能通过（真实浏览器拿到 173KB 完整词条），但在跨站 iframe 里失败（本机 headless 下甚至直接 403）。

## 三、v1.0.3 为什么显示"假成功"

`make_html_v103_part3.py` 的原逻辑：先用 `mode:"cors"` 抓页面，**失败后**再用 `mode:"no-cors"` 探一次连通性，探测不抛异常就渲染绿色横幅并显示 iframe：

```js
fetch(targetUrl, { method:"GET", mode:"no-cors", ... })
  .then(function() {                       // opaque 响应 -> 看不到 status
    statusBanner.className = "... dict-status-ok";   // 于是 403/418 也算成功
    statusBanner.textContent = "✓ 已连接…";
    iframeEl.src = targetUrl;              // 而 iframe 里其实是破图/403
  })
```

`no-cors` 的响应是 opaque 的，`status` 不可读，**任何 HTTP 错误码都会走进 `.then`**。v1.0.3 截图证据：WordReference 内嵌框显示「403 Forbidden nginx/1.31.6」，上方却是绿色「✓ 已连接」；欧路内嵌框是浏览器破图占位，上方是绿色「✓ 已成功获取」。

同时还有一个隐藏缺陷：欧路解析器找的是 `#ExpFCChild`，而页面实际 id 是 **`#ExpFCChild` 不存在、真实容器是 `#FCchild`（mdicts）/ `#ExpFCchild` 拼写大小写不符（dicts）**。`querySelector` 区分大小写，所以**从来没命中过**，面板一直在退化成 `<meta name="description">` 的模板句（"『欧路词典』为您提供area的用法讲解…"）。

补充发现：`/dicts/` 页面把释义里**部分汉字替换成 `<img>` 标签**做反爬，所以即使解析成功，纯文本也是残缺的（实测 `n. 面积；区，地区；` 缺了"域"）。`/mdicts/` 无此问题。

## 四、v1.0.4 的实际改动

1. **按站点能力驱动**，不再靠猜：每个源显式声明 `canEmbed` / `canFetch`，值来自上表实测。
2. **欧路改用 `/mdicts/en/<w>`**：既无 `X-Frame-Options`（内嵌真的能渲染），又带 `ACAO:*`（文本也能抓），且释义完整。
3. **修正解析选择器**：`#FCchild` / `#SPECchild`（小写 child），并加 `#page-status` 作为缺词信号；解析前剥离 `<img>`/`<script>`/`<style>`。
4. **新增"爱词霸"作为第二个可内嵌源**：无 XFO，可内嵌；因其释义由脚本渲染，横幅用**中性 info 态**并明说"Voca 不抓取其文本"，不给绿色对勾。
5. **WordReference 改为诚实的 warn 态**：不显示 iframe，直接说明"该站 `frame-ancestors` 白名单禁止内嵌且不开放跨域读取"，并提供一键跳转源站。
6. **删掉 `no-cors` 假探测**：抓不到就是抓不到，报 `error` 态并附原因（CORS 拒绝 / 超时 / 离线），同时展示本地离线释义作为参考且明确标注"非在线返回结果"。
7. **空结果不再算成功**：页面 200 但解析不到释义且无缺词标记时，走 info（只内嵌、不宣称已解析）。
8. **展示区自适应**：`.dict-iframe-wrap` 由固定 `310px` 改为 `clamp(240px, 46vh, 660px)`，`.dict-parsed-entries` 由 `240px` 改为 `clamp(104px, 22vh, 300px)`，`.modal-panel` 用 `min(90vh, calc(100dvh - 24px))`，并加 `overscroll-behavior: contain` 消除弹窗内套滚动的冲突。

## 五、修复后的实测结果

### 5.1 真实联网、真实词条（8 个词，两本词书）

| 词 | 词书 | 状态 | 实际解析到的释义 | 内嵌 |
| :--- | :--- | :--- | :--- | :--- |
| area | CET-4 | `dict-status-ok` | `n. 面积；区域，地区；范围` | mdicts 200，`block` |
| pattern | CET-4 | `dict-status-ok` | `n. 型，样式 / 花样，图案 / 方式，形式 / 榜样，典范 / vt. 模仿；仿制 / 以图案装饰` | 同上 |
| sunrise | CET-4 | `dict-status-ok` | `n. 日出(时分); 黎明` | 同上 |
| consumer | CET-4 | `dict-status-ok` | `n. 用户，顾客；消费者` | 同上 |
| political | CET-4 | `dict-status-ok` | `adj. 政治的；政党的，党派的；对政治有兴趣的…` | 同上 |
| aspect | GRE | `dict-status-ok` | `n. 方面 / 方位, 朝向 / 面貌, 模样, 神态` | — |
| swallow | GRE | `dict-status-ok` | `vt. 忍受；吞没 / vi. 吞下；咽下 / n. 燕子；一次吞咽的量` | — |
| threat | GRE | `dict-status-ok` | `n. 威胁, 恐吓 / 可能造成威胁的人[事,想法] / 恶兆, 兆头` | — |

底层网络日志：`dict.eudic.net/mdicts/en/<w>` 一律 `200` 且 **无 `x-frame-options`**，**没有** `net::ERR_BLOCKED_BY_RESPONSE`（v1.0.3 的 `/dicts/` 必然出现该失败码）。

### 5.2 四种异常状态

| 场景 | 状态类 | 横幅 | iframe |
| :--- | :--- | :--- | :--- |
| 离线（`navigator.onLine=false`） | `dict-status-error` | 「未能获取…当前设备处于离线状态」 | 隐藏 |
| 词条不存在（404） | `dict-status-warn` | 「词条不存在：未收录单词…」 | 隐藏 |
| 网络/请求失败 | `dict-status-error` | 「未能获取…：<原因>」 | 隐藏 |
| WordReference（策略禁止） | `dict-status-warn` | 「无法在 Voca 窗口内显示，仅能跳转到源站」 | 隐藏 |
| 爱词霸（脚本渲染，无可解析文本） | `dict-status-info` | 「已内嵌…Voca 不抓取其文本」 | 显示 |

**没有任何一种失败路径会显示绿色对勾。**

### 5.3 尺寸自适应（欧路弹窗保持打开，逐档改窗口大小）

| 视口 | 内嵌框高 | 弹窗高 | 是否完整落在视口内 | 横向溢出 |
| :--- | ---: | ---: | :--- | ---: |
| 1600x1000 | 460px | 900px | 是（top 50 / bottom 950 ≤ 1000） | 0 |
| 1280x800 | 368px | 720px | 是（40 / 760 ≤ 800） | 0 |
| 1024x700 | 322px | 630px | 是（35 / 665 ≤ 700） | 0 |
| 820x620 | 285px | 558px | 是（31 / 589 ≤ 620） | 0 |

内嵌框高度随视口连续变化（46vh），不再固定 310px；四档均无裁切、无横向溢出、无大片空白。

## 六、仍未解决 / 未验证

1. **WordReference 依旧不能在窗口内看内容**，只能一键跳转。这是对方站点策略，除非引入服务端代理（会把用户查询词经第三方转发，与"纯离线单机"定位冲突），否则无解。
2. 爱词霸与欧路的**页面结构可能随时变更**；解析器已加"解析不到就不报成功"的兜底，但释义条目会变少或退回 info 态。
3. **未测试**：欧路/爱词霸对高频访问的限流与验证码；`file://` 源下个别浏览器对跨站 cookie 的限制是否影响爱词霸脚本渲染。
4. **未测试**：WordReference 在已存在 `nginx_wr_human` cookie 的情况下，顶层跳转能否稳定直达词条。
5. 词典弹窗 `Esc` 关闭在 v1.0.4 仍未实现（v1.0.3 已知问题，未列入本次范围）。
