# Voca v1.0.3 Windows 宿主机真机复验报告（20261017）

本报告是 v1.0.3 公开发布前的**真机复验**，用于补齐 `docs/04` 中标注为"需在宿主机确认"的项目。全部数据由本机实测采集，未做任何推断性描述。

## 一、复验环境

| 项目 | 实测值 |
| :--- | :--- |
| 操作系统 | Windows 11，内部版本 `10.0.26200`，x64 |
| 显示缩放 | 主屏逻辑分辨率 1707 x 1067（物理 2560 x 1600，**150% 缩放**） |
| 浏览器内核 | `Edg/155.0.4283.45`（Chromium 155.0.8059.40） |
| Python | 3.11.9 |
| GNU Binutils | 2.30（MinGW-w64 8.1.0 发行包内） |
| OpenSSL | 3.5.6 |
| Android 验证工具 | Android SDK build-tools `35.0.0`（`apksigner`、`aapt2`） |
| Android 真机 / 模拟器 | **无**（`adb devices` 列表为空） |

复验手段：`Voca.exe` 真实启动 + Win32 `PrintWindow` 窗口截图；Edge `--headless=new` + Chrome DevTools Protocol 驱动 `windows/app/index.html` 做交互与持久化断言；自写 PE `.rsrc` / ICO / APK 二进制解析器；Android SDK 官方 `apksigner` 与 `aapt2` 校验发布 APK；在仓库副本上执行 `scripts/build_all.sh` 做逐字节复现比对。

---

## 二、Windows 版实测结果（11 项）

| # | 验收项 | 实测方法与数据 | 结果 |
| :--- | :--- | :--- | :--- |
| 1 | `Voca.exe` 真实启动 | 双击等价启动后，`msedge.exe` PID 42604 命令行实测为 `--app="...\windows\app\index.html" --start-maximized --high-dpi-support=1 --user-data-dir="...\windows\data\profile"`；顶层窗口标题 `Voca v1.0.3 — 离线艾宾浩斯背单词工坊 (Windows & Android)`（45 字符），窗口矩形 `-7,-7,1714,1026` 即最大化 | **通过** |
| 2 | 便携用户数据目录 | 启动前 `windows/data/profile` 不存在，启动后自动创建，实测 796 个文件 / 75.9 MB（Chromium profile 本体），学习数据落在其中 `Default/Local Storage/leveldb` 与 `Default/IndexedDB` | **通过** |
| 3 | 标题栏 16px 图标清晰度（150% 缩放） | `PrintWindow` 抓取真实窗口位图后放大检视：标题栏 16x16 的 V+书本图标边缘清晰、无灰边糊块；侧边栏 `.brand-logo` 原始分辨率实测 `256x256` | **通过** |
| 4 | PE 图标资源结构 | 自写 PE 解析器：`machine=0x8664`、`PE32+`、`subsystem=2 (GUI)`；`.rsrc` 含 `RT_ICON` 8 帧（ID 1..8）、`RT_GROUP_ICON` ID=1 `count=8`，8 条目录项的宽高/planes=1/bpp=32/字节数与实际 RT_ICON 载荷**逐条一致且无悬空 ID**；8 帧 sha256 与 `windows/voca.ico` 的 8 帧**完全相同**；`RT_MANIFEST` 711 字节含 `PerMonitorV2, PerMonitor` 与 `true/pm`，无 `requireAdministrator` | **通过** |
| 5 | 前端加载与脚本报错 | Edge headless 加载 `index.html`，CDP 全程监听 `Runtime.exceptionThrown` / `Log.entryAdded(error)` / `console.error`：页面错误 **0**、控制台错误 **0** | **通过** |
| 6 | 三档视口布局 | 1600x950、1024x640、390x844 下 `documentElement.scrollWidth == innerWidth`（1600/1024/390 均相等），无横向溢出；`body` 计算字体 `VocaSans, VocaSansCJK, sans-serif`，`document.fonts` 三个族状态均为 `loaded` | **通过** |
| 7 | 「掌握度」与「英英模式」删除 | DOM 扫描 `.mastery-badge, [data-mastery], #modalDictEn, #modalDictSyn, #modalDictExEn, #modalDictExCn` 计数 **0**；`[data-sort="mastery_asc"]` 不存在；`#langModeGroup` 按钮文本仅 `双语 / 只看英文 / 只看中文` | **通过** |
| 8 | 不会程度加减交互 | 对首行 `area`（`data-wid=w_cet4_5290`）派发事件，读 `data-unfam` 与徽章文本：`0/5` 左键 -> `1/5` 左键 -> `2/5` 右键 -> `1/5`；随后 `localStorage` 已写入 | **通过** |
| 9 | 数据持久化（真实刷新） | 写入 `unfam=5 / starred / note / customCn / onlineDict=wordreference / planListCount=22 / planCycleDays=45 / planChecks 两组` 后 `Page.navigate` 重新加载同一 URL：全部字段原样读回，`schemaVersion` 仍为 4，存档 JSON 实测 383,305 字节 | **通过** |
| 10 | v1.0.2 (Schema v3) 存档迁移 | 用 `__VOCA_RELOAD_FROM_PRELOAD__` 注入含 `langMode:"en_en"`、`intraSort:"mastery_asc"`、`rowClickMode:"mastery_lr"`、`mastery:4`、`unfam:3`、`starred`、`customCn`、`note`、`18组/36天`、`theme:paper`、`accent:en-GB` 的 v1.0.2 存档：迁移后 `schemaVersion=4`、`appVersion=1.0.3`、`langMode=bilingual`、`intraSort=hard_first`、`rowClickMode=unfam_lr`、`unfam=3` 保留、`mastery` 字段已剥离、`customCn`/`note`/`starredAt`/`planChecks`/`theme`/`fontScale`/`accent` 全部无损 | **通过** |
| 11 | 内置词库与备份入口 | 界面实测「四级核心 (CET-4 · 3,849词)」「List 1 (257/257词)」，导航计数 257；按钮存在 `⬇ 导出完整学习备份 (.json)`、`导出当前词库 CSV`、`🖨️ 导出本组 PDF`、`🖨️ 导出计划表 PDF/打印版` | **通过** |

### 与 `docs/04` 的差异修正
`docs/04` 第二节第 1 项原标注"物理 Windows 桌面任务栏观感待宿主机确认"，本报告第 1/2/3/4 项已在真实 Windows 11 26200 + 150% 缩放下确认**标题栏图标与 PE 资源结构**；`docs/04` 第 3 项关于"离线/失败绝不伪装为正常查询结果"的结论**在本机不成立**，见下节。

---

## 三、在线词典模块真机实测（发现缺陷）

对 `#dictModal` 逐一来实测，同时用 CDP `Network.responseReceived` / `Network.loadingFailed` 抓底层响应：

| 场景 | 实测 |
| :--- | :--- |
| 欧路词典，正常词条 `area` | 站点响应 `200`，响应头含 `x-frame-options: SAMEORIGIN` 与 `access-control-allow-origin: *`。内嵌 `<iframe>` 文档加载被浏览器拒绝：`Document :: net::ERR_BLOCKED_BY_RESPONSE`，画面显示浏览器破图占位；但弹窗顶部的**文本释义解析成功**并显示绿色「✓ 已成功获取【欧路词典】中"area"的词典内容」 |
| WordReference，正常词条 `area` | 浏览器内嵌框显示站点返回的「**403 Forbidden nginx/1.31.6**」页面；`fetch` 探测得到 `RESP 418`；弹窗却显示绿色「✓ 已连接【WordReference 英汉词典】在线词典页面」，并把本地释义拼进提示文案 |
| 命令行独立复核 | `curl` 直连：`https://dict.eudic.net/dicts/en/apple` -> `HTTP/1.1 200`（含 `x-frame-options: SAMEORIGIN`）；`https://www.wordreference.com/enzh/apple` -> `HTTP/1.1 418` |

**结论**：
1. 「内嵌视图」在两个词典源上**都不可用**（欧路被 SAMEORIGIN 拒绝，WordReference 被站点反爬拦截），实际可用的只有欧路的文本释义解析。
2. WordReference 路径存在**误报成功**：站点的 403/418 被 Voca 判成"已连接"并显示绿色横幅，与本次发布前 `README.md` 旧版「v1.0.3 核心更新亮点」第 3 条「绝不将空白页或失败状态伪装为正常查询结果」的表述相反（该句已在发布版本中更正为已知问题）。根因是 `src/webapp/make_html_v103_part3.py` 用 `mode: "no-cors"` 探测，跨域响应为 opaque 时 `status` 不可见，任何 HTTP 错误码都会被当成成功。
3. 本次发布**未修改代码**（按发布前决定：如实记为已知问题）。修复方向已在 `README.md` 第七节列出。

---

## 四、可复现构建实测（在仓库副本上执行）

在 `Voca_DualPlatform` 的完整副本上运行 `bash scripts/build_all.sh`，与发布产物逐字节比对：

| 产物 | 发布版 | 本机重建 | 结论 |
| :--- | ---: | ---: | :--- |
| `windows/app/index.html` | 4,192,694 B | 4,192,694 B | **逐字节一致** |
| `src/webapp/index.html`（构建同步副本） | 4,192,694 B | 4,192,694 B | **逐字节一致** |
| `src/android/app/src/main/assets/index.html` | 4,192,694 B | 4,192,694 B | **逐字节一致** |
| `windows/voca.ico` | 178,404 B | 178,404 B | **逐字节一致** |
| `assets/embedded_assets.json` | 1,748,642 B | 1,748,642 B | **逐字节一致** |
| `windows/Voca.exe` | 186,368 B | 186,368 B | **仅 3 字节差异**：`.text` 段 `ret` 之后 2 字节对齐填充（发布版 `00 00`，Binutils 2.30 重建为 `90 90`）及其引起的 `.text` VirtualSize 1 字节；机器码与资源段完全相同，属上游汇编器版本差异，不影响行为 |
| `android/Voca_v1.0.3_release.apk` | 3,482,189 B | 3,482,189 B | **ZIP 内 8 个载荷条目（AndroidManifest.xml / resources.arsc / classes.dex / ic_launcher.png / assets/index.html / 3 个字体）逐字节一致**；唯一差异是 `META-INF/CERT.RSA`（自签证书每次现生成） |

构建过程发现并已修的两个脚本问题（不影响运行产物，只影响"照着说明能否跑通"）：
1. `scripts/build_all.sh` 第 1 步无条件调用 `scripts/build_assets_v103.py`，而该脚本硬编码 `/usr/share/fonts/opentype/inter/Inter-Regular.otf`、`/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 等 Debian 系路径，在非 Debian/Linux（含 Windows、macOS、其他发行版）会直接失败。现改为默认跳过、`VOCA_BUILD_ASSETS=1` 显式开启。
2. `build_all.sh` 第 3/4 步把 `$ROOT_DIR` 直接插进 Python 源码字符串，在 MSYS/Git Bash 下路径形如 `/d/Users/...`，Windows 版 Python 会把它解析成当前盘符下的 `D:\d\Users\...`，静默写到错误位置。现改为通过环境变量传路径。
3. `src/webapp/make_html_v103_part3.py` 以文本模式写 `index.html`，在 Windows 上产生 CRLF，导致重建产物比发布版多 10,716 字节（行数差）。现固定 `newline="\n"`。
4. `requirements.txt` 缺 `cryptography`（`scripts/verify_apk_deep.py` 第 15 行 `from cryptography import x509` 依赖它），已补。

---

## 五、Android 版实测结果

| 验收项 | 实测方法与数据 | 结果 |
| :--- | :--- | :--- |
| APK 签名（官方工具） | `apksigner verify --verbose --print-certs`：`Verified using v1 scheme (JAR signing): true`、`Verified using v2 scheme: true`、v3/v3.1/v4/SourceStamp 均 false；单一签名者 `CN=Voca Offline Studio, O=Voca, C=CN`，RSA 2048，证书 SHA-256 `53ddf4bf80d0a262d77dfed58e8c50cc3c67ffadaf7fc02111e0812b020ea9cd` | **通过** |
| APK 结构（官方工具） | `aapt2 dump badging`：`package name='com.voca.app' versionCode='4' versionName='1.0.3'`、`uses-permission android.permission.INTERNET`、`minSdkVersion 19`、`targetSdkVersion 28`、`launchable-activity com.voca.app.MainActivity`、`application-icon-160 res/drawable/ic_launcher.png`（实测 192x192 RGBA） | **通过** |
| APK 内前端与字体 | 解包比对：`assets/index.html`（4,192,694 B）与仓库 `windows/app/index.html`、`src/android/.../index.html` **sha256 相同**；三个 WOFF2 与 `assets/fonts/` 逐字节相同 | **通过** |
| **能否安装到设备** | 本机无 Android 真机、无模拟器，`adb devices` 为空 | **未验证**（缺少可用测试设备） |
| **能否启动与运行** | 同上 | **未验证** |
| **兼容性范围** | 未在任何 Android 版本上实测 | **未验证** |
| 覆盖安装升级 | 构建脚本每次现生成自签证书（本次重建证书 SHA-256 为 `46f126b51e6c71739af56cf2419f61c4fe52d5a64d3200f65dc7fc36c83ec495`，与发布版 `53ddf4bf…` 不同），因此后续自行构建的 APK 与 Release 版**签名不一致，覆盖安装会报签名冲突** | **已知限制**（见 README 第七节第 3 条） |

`docs/04` 第三节把 Android 侧描述为"已在容器内验证"，实际容器内只做了二进制结构校验，**从未在真实 Android 系统上安装或运行过**。本报告将该项明确降级为未验证。

---

## 六、发布包与仓库一致性

- 发布 APK 内嵌的 `index.html` 与仓库源码树三处副本 sha256 一致（`ae4394052ce5aa0b…`）。
- `Voca.exe` 内嵌的 8 个图标帧与 `windows/voca.ico`、`assets/voca.ico` 的 8 帧 sha256 一致。
- 版本标识实测一致：HTML `<title>` 与 `state.appVersion` = `1.0.3`，`schemaVersion` = 4；APK `versionName=1.0.3 / versionCode=4`；EXE 清单 `assemblyIdentity version="1.0.3.0"`、`Image Version 1.3`。
- 复验结束后已删除测试期间生成的 `windows/data/profile/`（796 文件 / 75.9 MB），发布包与仓库树不含任何个人学习数据。

## 七、未覆盖项清单

1. Android 端全部运行时行为（安装、启动、WebView 兼容、返回键、PDF 导出、发音）—— 无设备。
2. 多显示器不同 DPI 混合缩放（100%/125%/200%/250%）下的任务栏观感 —— 本机仅 150% 单屏。
3. 未收录词条（404）路径的本机复测 —— 弹窗在本机未能切换到新词条（需先关闭弹窗，实测关闭逻辑见下条），该项仍沿用 `docs/04` 的容器内结论。
4. 弹窗 `Esc` 关闭：CDP 派发 `Escape` 键盘事件后 `#dictModal` 仍为 `display:flex`，**未通过**；界面右上「✕ 关闭」按钮存在且可用，故仅为快捷键覆盖缺口，不影响关闭操作。
5. 音频发音（TTS / `speechSynthesis`）在 headless 与真机下均未做听感验证。
6. 38,855 词条 `voca.db` 与 ECDICT 上游 release 的逐条差异审计 —— 未执行，仅核对了构建流程说明与 MIT 许可随附情况。
