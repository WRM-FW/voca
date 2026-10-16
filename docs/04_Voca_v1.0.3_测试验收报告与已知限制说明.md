# Voca v1.0.3 测试验收报告与已知限制说明

## 一、测试环境说明

- **操作系统与构建环境**：Linux x86_64 (`4.19.0-gvisor`)，Python `3.11`，GNU Binutils (`as`, `objcopy`, `objdump`)，OpenSSL `3.0`
- **前端与交互自动化测试环境**：Chromium `154.0.8037.92` + Selenium WebDriver (`scripts/run_e2e_v103.py`)
- **二进制结构校验工具**：`scripts/verify_apk_deep.py`（AOSP 二进制 AXML / ARSC / DEX / APK v1+v2 签名校验器）、Win32 ICO/PE `.rsrc` 二进制帧解析器、`objdump`

---

## 二、八项核心验收指标实测结果

| 序号 | 验收项目 | 实测方法与验证数据 | 结果 |
| :--- | :--- | :--- | :--- |
| **1** | **Windows 任务栏图标与多尺寸清晰度** | 二进制解析验证 `voca.ico` 与 `Voca.exe` `.rsrc` 均包含 `256(PNG)` 及 `128/64/48/40/32/24/16(32-bit BGRA DIB)` 共 8 个标准帧，且包含 `PerMonitorV2` 清单与 `--high-dpi-support=1`；HTML 含 9 个多尺寸 `<link rel="icon">`，`.brand-logo` 原始分辨率达 `256×256` | **已通过（二进制与渲染树已验证；物理 Windows 桌面任务栏观感待宿主机确认）** |
| **2** | **掌握度移除与不会程度功能验证** | DOM 扫描确认 `.mastery-badge`、`[data-mastery]`、`mastery_asc` 等元素数量为 `0`；实测单词行左键点击 2 次不会程度由 `0 → 2`，右键点击 1 次由 `2 → 1`；沉浸卡片 `+1 / -1 / 重置` 变化为 `1 → 2 → 1 → 0` | **已通过（已实测验证）** |
| **3** | **词典详情弹窗查询与异常/离线处理** | 1) 离线环境下打开弹窗，自动隐藏 `<iframe>`（`display: none`）并显示红色错误横幅说明原因，绝不伪装空白页；<br>2) 注入欧路与 WordReference 响应及含空格词条 `take off`，验证 URL 正确编码为 `.../enzh/take%20off` 且准确解析展示词条释义；<br>3) 查询未收录词 `nonexistent_xyz_999` 准确展示黄色「词条不存在」提示 | **已通过（已实测验证）** |
| **4** | **两个旧内容区块删除验证** | 检查 `#dictModal` DOM 与文本，确认 `#modalDictEn`、`#modalDictSyn`、`#modalDictExEn`、`#modalDictExCn`、「英英释义与同义词拓展」「双语语境例句与助记」均已彻底删除（计数为 `0`） | **已通过（已实测验证）** |
| **5** | **在线词典选择设置与持久化保存** | 在「偏好设置与帮助」将 `#settingOnlineDict` 切换为 `wordreference`，验证 `state.settings.onlineDict` 持久保存并在模拟重启与打开词典弹窗时自动生效 | **已通过（已实测验证）** |
| **6** | **英英模式移除与其他学习模式验证** | 验证 `#langModeGroup` 仅含 `['bilingual', 'en_only', 'cn_only']` 三个按钮，无 `en_en` 入口；测试「只看英文」与「只看中文」遮罩窥显与发音均正常 | **已通过（已实测验证）** |
| **7** | **README 升级与数据迁移说明一致性** | 逐项核对 `README.md` 与界面内 `#dataMigrationGuideCard` 的相对路径（Windows `./data/profile/`、Android `/data/data/com.voca.app/app_webview/Default/`）、备份恢复流程及跨平台限制说明，与代码实现完全一致 | **已通过（已实测验证）** |
| **8** | **v1.0.2 原有用户数据升级兼容验证** | 注入含 `schemaVersion: 3`、`langMode: "en_en"`、`intraSort: "mastery_asc"`、`mastery: 4`、`unfam: 3`、`starred: true`、`customCn`、`note` 及 `18组/36天` 计划的 v1.0.2 存档，升级后验证 `schemaVersion` 升为 `4`、`mastery` 已剥离、`langMode` 转为 `bilingual`、其余所有个人学习记录 100% 无损保留 | **已通过（已实测验证）** |

---

## 三、已知限制与未在容器内直接验证项说明

> **本节的容器内结论已被 `docs/05_Voca_v1.0.3_Windows宿主机真机复验报告_20261017.md` 的真机实测部分取代或修正。** 发布依据请以 `docs/05` 为准；本节保留作为容器内构建期的原始记录。

1. **宿主机物理 Windows 任务栏与真实外网连接环境说明**：
   - 当前构建与测试环境为无外网连接的 Linux 隔离容器。我们已通过二进制结构校验器与 Headless Chromium 完整验证了 8 级 Win32 DIB/PNG 图标帧、`PerMonitorV2` 清单、URL 编码、HTML 解析器以及离线/404/成功状态切换逻辑；
   - **在物理 Windows 10/11 桌面不同 DPI 缩放（100%/125%/150%/200%）下的任务栏真实视觉效果**，以及**在具备真实互联网连接的环境下直接访问 `dict.eudic.net` 与 `www.wordreference.com` 的实时网络响应**，标记为需在您的宿主机与联网设备上做最终体验确认的项目。
   - **【20261017 真机更新】** 已在 Windows 11 26200 / 150% 缩放 / Edge 155 真机复验：`Voca.exe` 启动、可移植 `data/profile` 创建、标题栏 16px 图标清晰度、PE 资源结构、前端零报错、三档视口布局、不会程度交互、真实刷新持久化、v1.0.2 存档迁移全部通过；100%/125%/200%/250% 缩放与多屏混合 DPI 仍未覆盖。
2. **第三方在线词典网站的跨站嵌入策略 (`X-Frame-Options` / `CSP`) 限制**：
   - 部分在线词典页面在部分浏览器中可能带有 `X-Frame-Options` 或 CORS 限制。Voca v1.0.3 已内置双层处理机制：支持解析词条内容并在弹窗右上角提供「↗ 浏览器打开源页面」一键直达按钮，且当处于离线或连接失败时明确提示用户。
   - **【20261017 真机更正】** 上述「离线或连接失败时明确提示」在真机联网环境下**不成立**：欧路词典带 `x-frame-options: SAMEORIGIN`，内嵌 `<iframe>` 必然被浏览器拒绝（`net::ERR_BLOCKED_BY_RESPONSE`），只有文本释义解析可用；WordReference 对本机返回 403/418，却被弹窗判为绿色「已连接」。详见 `docs/05` 第三节与 `README.md` 第七节已知问题。
3. **【20261017 新增】Android 端从未在真实设备上运行过**：容器内只做了 AXML/ARSC/DEX 与 v1+v2 签名的二进制校验，发布前本机亦无可用真机或模拟器（`adb devices` 为空）。APK 的安装、启动、WebView 兼容、返回键、发音与 PDF 导出**均为未验证**，Android 版本因此定位为实验版。
4. **【20261017 新增】APK 签名密钥不持久**：`scripts/build_apk_v103.py` 每次构建临时生成自签证书后即销毁，自行重建的 APK 与 Release 版签名不一致，覆盖安装会报签名冲突。
5. **【20261017 新增】弹窗 `Esc` 快捷键未生效**：真机 CDP 派发 `Escape` 后 `#dictModal` 仍为 `display:flex`；右上「✕ 关闭」按钮可用，故仅为快捷键覆盖缺口。
