# Voca v1.0.5 Windows 验收报告

- **报告日期**：2026-10-17
- **被测版本**：Voca v1.0.5（`state.appVersion="1.0.5"`、`schemaVersion=4`、窗口标题 `Voca v1.0.5 — …`、`assemblyIdentity 1.0.5.0`、PE `Image Version` 1.5、PE `Subsystem` 2 GUI）
- **范围**：本轮**只做 Windows**。Android 无限期暂停，不构建、不交付、不验收；`build_all.sh` 默认跳过 APK 步骤，需要时 `VOCA_ANDROID=1` 显式开启。
- **口径**：每项标注「已实测 / 推断 / 未验证」。

## 一、测试环境

| 项目 | 实测值 |
| :--- | :--- |
| 操作系统 | Windows 11 内部版本 26200，x64，单显示器 150%（DPI 144） |
| WebView2 Runtime | 155.0.4283.60（注册表 `EdgeUpdate\Clients\{F3017226-…}`） |
| 宿主浏览器内核（实测回读） | `Edg/155.0.4283.62` |
| 编译器 | MinGW-w64 gcc 8.1.0 / Binutils 2.30 |
| 驱动方式 | Chrome DevTools Protocol（`WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=…`）+ Win32 窗口枚举 |

---

## 二、需求一：单词学习页排序方式

### 2.1 控件位置与选项

`#sortSelect` 从最右侧图标簇移到「双语 / 只看英文 / 只看中文」与「列表视图 / 沉浸卡片」两组之间。实测几何（1600×950）：语言组右边界 900 → 排序框 1139–1302 → 视图组左边界 1312，三者同一行，排序框 163×35 px。

**在真实 `Voca.exe`（原生 WebView2 宿主）内复测**（1707×996，`devicePixelRatio=1.5`）：语言组右边界 898 → 排序框 1247–1410 → 视图组左边界 1420，`between=true`，排序框显示「初始序列」，横向溢出 0。截图见 `_verify/shots/v105_native_header_strip.png`。

> 记录一个测量陷阱：用 Win32 `PrintWindow` 抓宿主窗口时，头部右侧控件簇**不会出现在位图里**（WebView2 的合成表面对 PrintWindow 不完整），看起来像控件丢了。同一时刻用 CDP 读取的几何证明控件在位。凡涉及 WebView2 内容的观感判断，必须以 CDP 截图或真实操作为准，不能用 `PrintWindow`。

选项与文案：

| value | 显示文字 | 来源 |
| :--- | :--- | :--- |
| `initial` | 初始序列 | 需求指定 |
| `random` | 随机序列 | 需求指定 |
| `az` | 字母升序 A→Z | 需求指定 |
| `hard_first` | 不会的单词排前面 | 需求指定 |
| `easy_first` | 易掌握的单词排前面 | **v1.0.3 起已有，本轮保留** |

> 需求写的是"四种"。第五项 `easy_first` 是既有功能，删掉它会直接减少一个可用能力，属于与本次需求无关的改动，因此保留并在此说明；若要删，请明确指示。

### 2.2 排序结果实测

前 6 词（CET-4 List 1）：

| 模式 | 实测顺序 | 判定 |
| :--- | :--- | :--- |
| 初始序列 | area, pattern, sunrise, consumer, political, pig | 与词表原始顺序一致 |
| 随机序列 | serious, interference, potential, touch, commitment, public | 与初始不同；重复切换两次结果**完全相同**（种子 `planShuffleSeed + listIndex + 7`），不会边背边跳序 |
| 字母升序 | abnormal, accompany, accomplish, accumulate, acquire, adjust | 逐位 `localeCompare` 单调不减 ✓ |
| 不会的单词排前面 | sunrise(3), pattern(2), area(1), consumer(0), political(0), pig(0) | 递减 ✓，最高分置顶 |
| 易掌握的单词排前面 | 0,0,0,0,0,0 | 递增 ✓（低不会度在前） |

不会程度是通过**真实点击单词行**产生的（行 1 点 1 次、行 2 点 2 次、行 3 点 3 次），不是直接改内存。

组合行为：

| 场景 | 实测 |
| :--- | :--- |
| 搜索框输入 `a` + 字母升序 | 命中 120 行，结果仍严格升序（abnormal, accompany, accomplish, accumulate, acquire…） |
| 切到沉浸卡片再切回列表 | `intraSort` 与下拉框选中值均为 `hard_first`，未丢失 |
| v1.0.4 存档里 `intraSort=easy_first` | 1.0.5 读取后状态与下拉框都是 `easy_first` |
| 存档里放一个未知值 `mastery_asc_legacy_unknown` | **修复前**下拉框显示空白；**修复后**归一化为 `initial`，列表正常渲染 120 行 |

### 2.3 布局实测（5 档宽度）

| 视口 | 头部高度 | 排序框可见 | 横向溢出 | 观感 |
| :--- | :--- | :--- | :--- | :--- |
| 1600×950 | 61 px | 是 | 0 | 单行：词书 · List · 语言组 ── 排序 · 视图组 · 主题 |
| 1400×900 | 61 px | 是 | 0 | 单行，语言组与排序框间距 39 px |
| 1200×800 | 109 px | 是 | 0 | 两行：第一行词书/List/语言组，第二行排序/视图组/主题 |
| 1024×700 | 109 px | 是 | 0 | 同上 |
| 900×640 | 109 px | 是 | 0 | 同上 |

≤1200 px 换行是 `.top-header` 既有行为（控件总数与总宽度未变，本轮只调整了同一容器内的先后次序），不是本次引入。全程无裁剪、无横向滚动条、无控件重叠。

---

## 三、需求二：WordReference 英汉查询

### 3.1 上一版结论是错的，已撤回

v1.0.4 的 `docs/07` 写着"WR 的 200 响应带 `x-frame-options: SAMEORIGIN` 与 CSP `frame-ancestors` 白名单，Voca 不在白名单内，所以内容不可能出现在窗口里"。复查发现两个测量错误：

1. **测量环境是 headless Chromium**，WR 对它直接 418 → **403**（页面标题就是 `403 Forbidden`），根本没拿到词典文档。
2. 记录到的那两个头来自 **`favicon.ico` 等静态资源**，不是词典页。

非 headless 重测（`_verify/wr_headers_test.mjs`、`_verify/wr_iframe_deep.mjs`）：

| 场景 | 实测 |
| :--- | :--- |
| 顶层导航 `enzh/area` | 418 质询 → JS 解题 → **200**，标题 `area - WordReference.com 英汉词典`，正文 13,931 字符 |
| 该 200 文档的响应头 | **无 `x-frame-options`、无 CSP** |
| 同站页面里的 iframe 嵌 `enzh/abandon` | 通过，正文 5,062 字符 |
| **`file://` 页面里的 iframe** 嵌 `enzh/run` | 帧能渲染，但**永远停在**「正在确认你是不是机器人！/ 加载中…」 |
| `fetch()` | `TypeError: Failed to fetch`（无 CORS 头） |

**真正的故障原因**：Anubis 的人机验证只在**顶层框架**里能完成。Voca 的弹窗 iframe 是跨站子帧，拿不到验证 cookie，所以卡死；而跨域读取又被 CORS 禁止。所以既不能内嵌也不能抓取，但**顶层打开是可行的**。

### 3.2 修复方案与实测

在原生宿主里实现 WebView2 的 `NewWindowRequested`：页面 `window.open()` 时，宿主开一个自己的顶层窗口 `Voca.DictWindow`（同一用户数据目录，因此验证 cookie 复用），导航到该 URL，并通过 `PostWebMessageAsJson` 回执给页面；页面收到回执才把弹窗标成成功。**没有回执就不谎报。**

在**发布的 `Voca.exe`** 内端到端实测（CDP + Win32 窗口枚举）：

| 查询词 | 弹窗横幅 | 词典窗口 | 该窗口实际内容 |
| :--- | :--- | :--- | :--- |
| pattern | `✓ 已在 Voca 词典窗口中打开【WordReference 英汉词典】"pattern"`（`dict-status-ok`） | 第 1 次查询：Voca 顶层窗口 1 → 2 | `…/enzh/pattern`，标题 `pattern - WordReference.com 英汉词典`，「主要翻译」含 SC 花样 / 图案 + 例句「你喜欢我衬衣上的图案吗？」 |
| sunrise | 同上（sunrise） | 窗口数保持 **2**，`Voca.DictWindow` 数量 **1**（复用，不叠加） | `…/enzh/sunrise`，SC 黎明 / 拂晓 + 例句 |
| consumer | 同上（consumer） | 2 / 1 | `…/enzh/consumer`，SC 消费者 + 例句 |

窗口类名与标题实测：`24800|Voca.DictWindow|Voca · 在线词典窗口 (WordReference)` 与 `24800|Voca.MainWindow|Voca v1.0.5 — …`，同一进程，两个顶层窗口。

### 3.3 尺寸变化下的显示

把词典窗口缩到 **620×520** 后实测：`innerWidth=620`、`innerHeight=520`、`scrollWidth - innerWidth = -15`（**无横向溢出**）、翻译表格仍在渲染；截图未见截断或错位。放大回原尺寸同样正常。宿主侧 `WM_SIZE` 会重设 WebView2 边界，`WM_DPICHANGED` 会重设窗口位置与图标。

### 3.4 回归检查

- 欧路 `area`：`✓ 已获取…并在下方内嵌原站词典页`（`dict-status-ok`），iframe 正常 —— 未受影响。
- 爱词霸 `area`：`ℹ 已内嵌…（该站释义由脚本渲染，Voca 不抓取其文本）`（`dict-status-info`）—— 未受影响。
- 断网：`dict-status-error`；404：`dict-status-warn`；空白页：`dict-status-info`；真实解析成功：`dict-status-ok` —— 四种状态全部仍正确。
- 弹窗自适应 1600×1000 / 1280×800 / 1024×700 / 820×620：`fitsViewport` 全为 true，横向溢出 0。
- **在普通浏览器里打开 `index.html`（无 WebView2 通道）**：WR 走降级分支，横幅 `⚠ …无法嵌进本弹窗，需在词典窗口或浏览器中打开`，正文说明在 Voca.exe 里开词典窗口、在浏览器里开新标签 —— 不再谎称成功。
- 窗口图标回归（`ApplyWindowIcons` 本轮重构成按窗口分槽）：`ICON_SMALL` 24×24 与 `icon_24.png` **逐像素相同**、`ICON_BIG` **48×48** 与 `icon_48.png` **逐像素相同**、`ICON_SMALL2` 24×24 相同，delta 均为 `0.0000`。

---

## 四、数据兼容与产物完整性

### 4.1 v1.0.4 → v1.0.5 无损往返（实测）

用应用自身的交互路径造数据（点击改不会程度、★ 收藏、自定义释义、笔记、改计划参数与主题等），导出备份 → **清空 localStorage** → 重新加载 → 通过「从粘贴内容恢复备份」还原，逐项比对：

| 字段 | 恢复前 | 恢复后 | 一致 |
| :--- | :--- | :--- | :--- |
| `area` 不会程度 / 自定义释义 / 笔记 | 2 / 自定义释义-测试 / NOTE-α | 2 / 自定义释义-测试 / NOTE-α | ✓ |
| `pattern` 不会程度 | 1 | 1 | ✓ |
| `sunrise` 收藏 | true | true | ✓ |
| `planListCount` / `planCycleDays` / `planOrderMode` | 21 / 45 / original | 21 / 45 / original | ✓ |
| `theme` / `accent` / `fontScale` / `onlineDict` / `soundFx` | paper / en-US / xlarge / iciba / false | 同左 | ✓ |
| `intraSort` | hard_first | hard_first | ✓ |
| 收藏总数 | 1 | 1 | ✓ |
| `schemaVersion` | 4 | 4 | ✓ |

`appVersion` 由 1.0.4 升到 1.0.5，`schemaVersion` 保持 4：**未新增、删除或改名任何持久化字段**，v1.0.0 ~ v1.0.4 存档均可直接读取。

### 4.2 产物

| 文件 | 字节 | SHA-256（前 24 位） |
| :--- | ---: | :--- |
| `windows/app/index.html` | 4,256,649 | `5d726bddf2f5b7eb7d116ded` |
| `src/webapp/index.html` | 4,256,649 | `5d726bddf2f5b7eb7d116ded`（与上**逐字节相同**） |
| `windows/Voca.exe` | 220,672 | `0fd96ca61540b830804a6f89`（PE32+ x86_64，`Subsystem=2` GUI） |
| `windows/WebView2Loader.dll` | 165,968 | `462b36fd1be6ca9f7563466a`（与 v1.0.4 相同） |
| `windows/voca.ico` | 178,404 | `7a30cd86e9c7883e8a48335e`（与 v1.0.4 相同） |
| `src/android/app/src/main/assets/index.html` | 4,253,569 | `c624adc24c908b443ae954c4` —— **仍是 v1.0.4 那份，本轮构建未改动它** |

`bash scripts/build_all.sh` 全程通过：前端组装 → 图标 → 原生宿主；第 4 步打印 `Android build skipped (paused since v1.0.5). Re-enable with VOCA_ANDROID=1.`，且 `git status` 确认 `src/android/` 无任何改动 —— Android 树与已发布的 v1.0.4 APK 保持一致。

**未验证**：APK 相关的一切（本轮未构建）；Linux 下构建；非 150% 缩放与多屏混合 DPI；WebView2 Runtime 缺失时的兼容模式；发音听感。

---

## 五、本轮改动清单

| 文件 | 改动 |
| :--- | :--- |
| `src/webapp/make_html_v103_part2.py` | 排序框移位与改名；WR 相关文案与授权声明更正；词典外链按钮改名「↗ 词典窗口打开源页面」 |
| `src/webapp/make_html_v103_part3.py` | `wantsDictWindow` 能力位；`chrome.webview` 回执监听与 `openInVocaDictWindow()`；`renderDictWindowOpened()`；`renderOpenOnly()` 措辞更正；`intraSort` 载入归一化；查询序号防竞态；版本戳 |
| `src/windows/voca_host.c` | `Voca.DictWindow` 窗口类与生命周期；`NewWindowRequested` 处理；`PostWebMessageAsJson` 回执；`ApplyWindowIcons` 拆成按窗口分槽；`WM_APP+8`；主窗口销毁时连带关闭词典窗口；版本戳 |
| `src/windows/voca_host.rc` / `.exe.manifest` | 版本戳 1.0.5.0 |
| `scripts/build_all.sh` | Android 步骤改为 `VOCA_ANDROID=1` 显式开启；补回兼容模式回退路径缺失的 `VOCA_OUT_EXE`；版本戳 |
| `scripts/build_exe_v103.py` / `build_host_v104.py` | 版本戳 |
| `docs/07`、`THIRD_PARTY_NOTICES.md` | 撤回并更正 WordReference 的错误结论 |

## 六、尚未解决的问题

1. 词典窗口是"裸"浏览面：没有我们自己的前进/后退/刷新按钮（可用 Alt+← 后退），关掉后下次查询会重新开一个。
2. WR 首次查询仍需数秒人机验证；站点限流时窗口可能显示质询页或 403。
3. 弹窗仍不支持 `Esc` 关闭（1.0.4 遗留）。
4. `Voca.exe` 未代码签名，SmartScreen 仍提示未知发布者。
5. `voca.db` 音标沿用 ECDICT 标注体系，非严格 IPA。
6. 图标与 DPI 证据仍只有 150% 单屏。
7. Android 全部已知问题原样保留（本轮未动）。
