# Voca v1.0.3 — 离线艾宾浩斯背单词（Windows & Android）

**Voca** 是一款离线单机的艾宾浩斯遗忘曲线背单词软件，同一套前端同时跑在 Windows 桌面与 Android 手机上。背诵、计划表生成、生词本管理、拼词/滚动训练、多页 PDF 导出全部 **100% 离线**可用，不注册账号、不上传数据；「查看词典详细与编辑」模块额外提供按需的在线词典查询。

- 内置 **38,855 条**词条，覆盖中考 / 高考 / 四级 / 六级 / 考研 / 托福 / 雅思 / GRE 八大词书（源自开源词典 [ECDICT](https://github.com/skywind3000/ECDICT)，MIT）。
- 学习状态以 **不会程度 0~5** 单一维度管理，左键加深、右键降低，配合自定义组数与周期的艾宾浩斯计划表与每日打卡。
- 完整学习状态可一键导出为 `.json` 备份，Windows 与 Android **双向互通**。

## 版本成熟度：请先看这一节

| 平台 | 定位 | 依据 |
| :--- | :--- | :--- |
| **Windows** | **当前推荐版本** | 已在真实 Windows 11（内部版本 26200、150% 缩放、Edge 155）上完成启动、图标渲染、界面布局、不会程度交互、数据持久化、v1.0.2 存档迁移等 11 项真机复验，全部通过。 |
| **Android** | **实验版 / 开发中，暂不推荐作为主力使用版本** | 仅通过 Android SDK 官方 `apksigner`（v1+v2 签名有效）与 `aapt2`（清单、版本、启动 Activity 解析正常）的结构校验，以及前端与字体逐字节一致性校验。**发布前没有任何可用的 Android 真机或模拟器，安装、启动、WebView 兼容、返回键、发音、PDF 导出均未实测**，兼容范围未知。 |

Windows 版同样有未修完的缺陷（在线词典内嵌视图、`Esc` 关闭弹窗等），见 [第七节 已知问题](#七已知问题)。

## 下载

编译好的产物只放在 **GitHub Releases**，不提交进 git 树。请到 [Releases](../../releases) 页面下载：

| 资产 | 平台 | 说明 |
| :--- | :--- | :--- |
| `Voca_v1.0.3_Windows_x64.zip` | **Windows（推荐）** | 免安装绿色包，含 `Voca.exe`、`windows/app/`、`windows/data/` |
| `Voca_v1.0.3_release.apk` | Android（实验版） | `versionCode=4`，`versionName=1.0.3`，自签证书 |
| `Voca_v1.0.3_source.zip` | 源码 | 与 `v1.0.3` 标签的源码快照等价 |

Windows 与 Android 内嵌的前端 `index.html` 已实测 sha256 相同（`ae4394052ce5aa0b…`），即两端行为基准一致；差异只在容器层。

---

## 一、主要功能与适用场景

| 模块 | 能力 |
| :--- | :--- |
| 单词学习 | 双语 / 只看英文 / 只看中文三种遮罩模式；左键点击单词行加深不会程度 (+1) 并发音，右键降低 (-1)；4 种点击分区模式可切换 |
| 艾宾浩斯计划表 | 任意组数 N 与任意周期天数 D 的自定义计划，三种排组方式，逐日打卡与进度百分比 |
| 专项强化训练 | 拼词挑战与滚动速认 |
| 生词本与熟词表 | 收藏生词、自定义中文释义、个人笔记、标熟移除、批量恢复 |
| 词库导入与 PDF 导出 | 自定义词表 CSV 导入、当前词库 CSV 导出、多页 A4 计划表/词库 PDF 与打印版离线导出、完整学习状态 `.json` 备份与恢复 |
| 词典详细与编辑 | 内置精编双解词库（233 条，项目自编）+ 按需在线查询欧路词典 / WordReference 英汉词典（**当前有服务侧限制，见第七节**） |
| 偏好设置 | 主题（daylight / oled / paper）、字号、英美音、在线词典来源选择，全部本地持久化 |

适用场景：需要长期背应试词汇、又不想把学习进度交给云端账号的人；在没网的自习室、飞机、宿舍里用；以及希望同时在电脑和手机上背、进度能互相搬运的人。

---

## 二、Windows 版：下载、安装、启动与升级（推荐版本）

### 2.1 运行要求
- **64 位 Windows**（`Voca.exe` 实测为 PE32+ x86_64 GUI 程序，链接的 Windows 版本 6.00）。
- 需要已安装 **Microsoft Edge 或 Google Chrome**。`Voca.exe` 本身不是完整应用，而是一个原生启动器：它以 `--app=<安装目录>\app\index.html --start-maximized --high-dpi-support=1 --user-data-dir=<安装目录>\data\profile` 拉起 Edge（找不到则退回 Chrome，都找不到则退回用系统默认浏览器打开 `index.html`）。
- 无需管理员权限：清单里只有 `PerMonitorV2` 高 DPI 声明，没有 `requireAdministrator`。

### 2.2 安装与启动
1. 解压 ZIP 到任意目录（例如 `D:\Voca_v1.0.3\`），**保持目录结构不变**——启动器按自身所在目录定位 `app\index.html` 与 `data\profile`。
2. 打开 `windows/` 文件夹，双击 **`Voca.exe`**。
3. 程序以最大化独立窗口启动，任务栏与标题栏为 8 级高清图标。需要桌面入口时，右键 `windows/Voca.exe` → 发送到 → 桌面快捷方式。
4. 首次启动会在 `windows/data/profile/` 下生成浏览器配置目录（实测约 76 MB，属正常），这是**你的学习数据所在地**，见第五节。

### 2.3 升级到新版本
- **推荐做法（同目录继承）**：解压新版后，用新版的 `Voca.exe` 与 `windows/app/` 覆盖旧版同名内容，**保留旧版 `windows/data/profile/` 不动**，学习数据自动延续。
- **或者（备份恢复）**：旧版里点「词库导入与PDF导出」→「⬇ 导出完整学习备份 (.json)」，新版里点「⬆ 从备份文件恢复数据」。
- **不要**直接删除整个 `windows/` 文件夹后再装新版，那会连 `data/profile/` 一起删掉。

---

## 三、Android 版：获取、安装要求与当前限制（实验版）

> **本版本尚不成熟，暂不推荐作为主要使用版本。** 下面写的是已核实的事实与未核实的边界，不要把"结构校验通过"读成"能正常用"。

### 3.1 已核实
- `apksigner verify`：v1 (JAR) 与 v2 (APK Signature Scheme v2) 签名**均验证通过**；单一签名者 `CN=Voca Offline Studio, O=Voca, C=CN`，RSA 2048，证书 SHA-256 `53ddf4bf80d0a262d77dfed58e8c50cc3c67ffadaf7fc02111e0812b020ea9cd`。
- `aapt2 dump badging`：`com.voca.app`，`versionCode=4`，`versionName=1.0.3`，`minSdkVersion=19`，`targetSdkVersion=28`，声明 `android.permission.INTERNET`，启动 Activity `com.voca.app.MainActivity`，图标 `res/drawable/ic_launcher.png`（192x192 RGBA）。
- APK 内 `assets/index.html` 与三个 WOFF2 字体，与仓库源码树逐字节一致。

### 3.2 安装步骤
1. 从 Release 下载 `Voca_v1.0.3_release.apk` 传到手机。
2. 因为是**自签名**且未上架应用商店，需要允许「安装未知来源应用」。
3. 清单声明的最低系统是 Android 4.4（API 19）。

### 3.3 未验证与限制
- **未在任何真机或模拟器上安装、启动或运行过**（发布环境无可用 Android 设备，`adb devices` 为空）。安装成功率、WebView 渲染、发音、返回键、PDF 导出、不同厂商 ROM 的差异全部**未验证**。
- `targetSdkVersion=28` 远低于当前商店要求，在 Android 13/14/15 上侧载会出现系统风险提示，且部分新行为按旧 target 兼容模式运行。
- **签名密钥不持久**：构建脚本每次在临时目录现生成自签证书后即销毁。因此你自行重建的 APK 与 Release 版签名不一致（实测证书 SHA-256 从 `53ddf4bf…` 变成 `46f126b5…`），**覆盖安装会报签名冲突**，只能先卸载再装，而卸载会清空数据 —— 所以升级前务必先导 `.json` 备份。
- 数据在应用私有沙箱 `/data/data/com.voca.app/` 内，无 Root 的手机无法用文件管理器直接取出，只能靠 `.json` 备份导出。

---

## 四、开发环境、依赖、构建与测试

### 4.1 仓库结构

```text
.
├── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md
├── THIRD_PARTY_NOTICES.md      # 第三方组件/词库/字体/图标授权核查清单
├── requirements.txt            # Python 构建与测试依赖
├── .gitignore
├── src/
│   ├── webapp/                 # 前端构建源码（真正的前端在这里改）
│   │   ├── make_html_v103_part1.py   # 样式与 <head>
│   │   ├── make_html_v103_part2.py   # DOM 模板
│   │   ├── make_html_v103_part3.py   # JavaScript 状态机 + 组装 index.html
│   │   └── index.html                # 构建同步产物（勿手改）
│   ├── windows/voca_launcher.c       # 启动器 Win32 C 参考实现（见下方说明）
│   ├── windows/CMakeLists.txt        # 可选：用编译器构建上述 C 版启动器
│   ├── android/                # Android 壳层工程（MainActivity.java / AndroidManifest.xml / build.gradle）
│   └── lexicon/                # 词库提取、清洗与构建源码
├── scripts/
│   ├── build_all.sh            # 一键构建与验证
│   ├── build_assets_v103.py    # 图标裁剪、Win32 DIB 生成、WOFF2 子集（需 VOCA_BUILD_ASSETS=1）
│   ├── build_exe_v103.py       # 生成 Voca.exe（内联汇编 + 手写 PE .rsrc）
│   ├── build_apk_v103.py       # 生成并签名 APK（纯 Python AXML/ARSC/DEX + v1/v2 签名）
│   ├── verify_apk_deep.py      # APK 二进制结构与签名深度校验（依赖 cryptography）
│   └── run_e2e_v103.py         # Selenium 端到端测试
├── assets/                     # 图标源帧、WOFF2 子集、OFL 许可、内嵌资产清单
├── windows/                    # 前端与词库运行资源（Voca.exe 由构建生成，不入库）
│   ├── app/ (index.html, voca.ico, fonts/)
│   └── data/ (voca.db, voca_lexicon.*, schema.sql, LICENSE-ECDICT.txt, 词库数据包说明.md)
├── android/                    # APK 由构建生成，不入库
└── docs/                       # 版本说明、迁移指南、许可合规、验收报告
```

**关于 `src/windows/voca_launcher.c`**：它是启动器的**参考实现**，便于阅读与用标准工具链自行构建。**发布用的 `Voca.exe` 不由它编译**，而由 `scripts/build_exe_v103.py` 内联汇编 + 手写 PE 头与 `.rsrc` 生成（这样才能精确控制 8 帧图标目录与 `RT_MANIFEST`）。改启动器行为时请同时改两处，或明确以哪份为准。

### 4.2 环境与依赖
- **Python** >= 3.10，`pip install -r requirements.txt`（Pillow、fonttools、brotli、pypdf、selenium、cryptography）。
- **构建 `Voca.exe` 需要 GNU Binutils**（`as`、`objcopy`）与 **OpenSSL**；Linux 上随发行版安装，Windows 上实测 MinGW-w64 的 Binutils 2.30 + OpenSSL 3.5.6 可用。
- **构建 APK 只需 Python + OpenSSL**（AXML/ARSC/DEX 与签名都是纯 Python 生成，不需要 Android SDK）。
- 只有当你要**重新生成字体子集**时才需要上游 OTF/TTC 源（Debian/Ubuntu 的 `fonts-inter`、`fonts-noto-cjk`）。`assets/fonts/` 已预置生成好的 WOFF2，默认构建不碰它们。

### 4.3 一键构建

```bash
bash scripts/build_all.sh
```

依次执行：前端组装 → `Voca.exe` → 签名 APK → APK 深度校验。图标/字体资产重生成为**可选**步骤，需要显式开启：

```bash
VOCA_BUILD_ASSETS=1 bash scripts/build_all.sh   # 会调用 build_assets_v103.py，依赖上游字体源
```

脚本全部使用相对仓库根目录的路径，且不依赖任何开发机私有目录；实测在 Linux 与 Windows(Git Bash) 下均可跑通。

### 4.4 复现性与验证

在仓库完整副本上执行 `bash scripts/build_all.sh`，与 Release 产物逐字节比对（2026-10-17 于 Windows 11 实测）：

| 产物 | 结果 |
| :--- | :--- |
| `windows/app/index.html` 及其两处同步副本、`voca.ico`、`embedded_assets.json` | **逐字节一致** |
| `windows/Voca.exe` | 同尺寸，**仅 3 字节差异**：`.text` 段 `ret` 之后 2 字节对齐填充（`00 00` vs `90 90`）与随之变化的 `.text` VirtualSize，由 GNU Binutils 版本差异造成，机器码与资源段完全相同 |
| `android/Voca_v1.0.3_release.apk` | ZIP 内 8 个载荷条目**逐字节一致**，唯一差异是 `META-INF/CERT.RSA`（自签证书每次现生成） |

### 4.5 测试
```bash
python3 scripts/verify_apk_deep.py     # APK 二进制结构 + v1/v2 签名密码学校验
python3 scripts/run_e2e_v103.py        # Selenium + Chromium 端到端功能与存档迁移测试
```
`run_e2e_v103.py` 需要本机有 Chrome/Chromium 与可用的 WebDriver。

---

## 五、用户数据：位置、备份与迁移

### 5.1 数据实际存放位置

| 平台 | 学习数据路径 | 内置词库与程序资源 | 访问方式 |
| :--- | :--- | :--- | :--- |
| **Windows** | `<解压目录>/windows/data/profile/Default/Local Storage/leveldb/`<br>`<解压目录>/windows/data/profile/Default/IndexedDB/` | `<解压目录>/windows/data/voca.db`<br>`<解压目录>/windows/app/index.html`<br>`<解压目录>/windows/app/fonts/` | 便携式本地目录（`--user-data-dir`），可直接在资源管理器里查看、复制、备份 |
| **Android** | `/data/data/com.voca.app/app_webview/Default/Local Storage/`<br>`/data/data/com.voca.app/app_webview/Default/IndexedDB/` | APK 内部只读资产：`assets/index.html`、`assets/fonts/` | 受系统沙箱保护，无 Root 无法用文件管理器访问 |

### 5.2 备份（强烈建议在升级或换机前做一次）
1. 进入 **「词库导入与PDF导出」**；
2. 点 **「⬇ 导出完整学习备份 (.json)」**；
3. 把生成的 `voca_backup_*.json` 存到安全位置。

恢复：同一张卡片里点 **「⬆ 从备份文件恢复数据」** 并选中该 `.json`。

### 5.3 跨平台迁移（Windows ⇄ Android）
只支持 `.json` 备份文件双向搬运：源平台导出 → 用数据线/聊天工具传到目标平台 → 目标平台导入。实测存档 JSON 约 380 KB，完整包含不会程度、生词本、自定义释义、笔记、熟词状态、自定义导入词、计划参数与打卡记录。

**不支持**：
- 云端自动同步 —— Voca 是纯离线单机软件，没有账号体系。
- 直接拷 LevelDB 目录跨系统互通 —— Windows 的 `data/profile/` 与 Android 的 `app_webview/` 虽同为 Chromium 存储，但受文件锁、权限沙箱与 LevelDB 元数据差异影响，不能互拷。

### 5.4 覆盖安装、重装与卸载的影响
- **覆盖安装**（Windows 保留 `data/profile/` 只更新程序文件；Android 用同一签名密钥构建的 APK 覆盖安装）：数据不丢。
- **删除整个 `windows/` 目录**：`data/profile/` 一并删除，数据丢失。
- **Android 卸载或「清除存储空间」**：系统彻底销毁 `/data/data/com.voca.app/`，数据丢失。**卸载前必须先导出 `.json`**。
- 仓库与 Release 包**不含任何个人学习数据**：`.gitignore` 已排除 `windows/data/profile/`。

### 5.5 从 v1.0.2 升级（Schema v3 → v4）
v1.0.3 内置向下兼容迁移器 `migrateStateIfNeeded`，读取 v1.0.0/v1.0.1/v1.0.2 存档时：
- **100% 保留**：不会程度 `unfam`(0~5)、生词本收藏 `starred`、自定义释义 `customCn`、笔记 `note`、熟词移除 `mastered`、自定义导入 `customWords`、计划参数 `planListCount`/`planCycleDays`/`planOrderMode`、打卡 `planChecks`、主题/字号/口音。
- **自动清理与映射**：废弃的 `mastery` 字段被剥离；已删除的 `en_en` 模式自动切到 `bilingual`；排序 `mastery_asc` 映射为 `hard_first`；点击模式 `mastery_lr` 映射为 `unfam_lr`。
- 以上迁移路径已在真机注入 v1.0.2 存档实测通过，逐项结果见 `docs/05` 第二节第 10 项。

---

## 六、开源许可证与第三方资源

- **项目自有源码与自编词库**（`src/`、`scripts/`、`docs/`、`voca_lexicon.*`）：**MIT License**，见 `LICENSE`。233 条精编双解词条的英文释义、同义词、例句与助记为项目自编。
- **内置词库 `voca.db`**：源自 [ECDICT](https://github.com/skywind3000/ECDICT)，**MIT License**，许可全文见 `windows/data/LICENSE-ECDICT.txt`。
- **内嵌字体**（Inter、Noto Sans CJK SC 的 WOFF2 子集）：**SIL Open Font License 1.1**，全文见 `assets/LICENSE-OFL-1.1.txt`。
- **软件图标**：仓库所有者自有资产，已确认著作权与再分发授权。
- **在线词典**：不打包、不分发对方数据，仅客户端实时访问，受欧路软件与 WordReference 各自服务条款约束。

逐项核查与边界见 **`THIRD_PARTY_NOTICES.md`** 与 `docs/03`。

---

## 七、已知问题

按影响程度排序。前三条是 2026-10-17 真机复验新发现或新确认的，测量数据在 `docs/05`。

1. **在线词典的「内嵌视图」实际不可用。** 欧路词典返回 `x-frame-options: SAMEORIGIN`，浏览器会拒绝把它渲染进 Voca 的 `<iframe>`（实测 `net::ERR_BLOCKED_BY_RESPONSE`），画面是浏览器的破图占位；由于该站点带 `access-control-allow-origin: *`，弹窗顶部的**文本释义解析仍然正常**。也就是说：能读到释义，看不到原页内嵌预览。
2. **WordReference 查询失败却提示成功。** 本机实测该站返回 `403 Forbidden`（内嵌框）/ `HTTP 418`（命令行），Voca 却显示绿色「✓ 已连接」横幅。根因是 `make_html_v103_part3.py` 用 `mode:"no-cors"` 探测连通性，跨域 opaque 响应看不到状态码，任何 HTTP 错误都会被当成成功。**这不是"已修好的诚实检测"** —— v1.0.3 发布说明里那句「绝不将空白页或失败状态伪装为正常查询结果」在联网真机环境下不成立，本次发布只更正文档、未改代码。可用替代路径：弹窗右上「↗ 浏览器打开源页面」。
3. **Android APK 无法平滑升级。** 签名密钥每次构建临时生成后即销毁，自行重建的 APK 与 Release 版签名不一致，覆盖安装报签名冲突；换正式版需要长期保存一份固定的签名密钥。
4. **弹窗 `Esc` 快捷键不生效。** 真机派发 `Escape` 后 `#dictModal` 仍为 `display:flex`；右上角「✕ 关闭」按钮可用。
5. **`targetSdkVersion=28` 偏低。** 在 Android 13/14/15 上侧载会有系统风险提示，且无法上架应用商店。
6. **`voca.db` 音标不是严格 IPA。** ECDICT 沿用自身标注体系（如 `state` 标作 `/steit/` 而非 `/steɪt/`），影响认读精度；`pos` 字段是词性频次统计而非词性标签。详见 `windows/data/词库数据包说明.md`。
7. **未覆盖的验证项**：100%/125%/200%/250% 缩放与多屏混合 DPI 下的任务栏观感、发音听感、未收录词条 404 路径的真机复测、以及 Android 端全部运行时行为。

## 八、版本计划

| 版本 | 内容 | 状态 |
| :--- | :--- | :--- |
| 1.0.0 | 双平台离线首版 | 已发布 |
| 1.0.1 | 内置 38,855 词条词库、APK 二进制结构修复 | 已发布 |
| 1.0.2 | 自由计划参数、离线 PDF 导出、WOFF2 字体子集、Android 竖版重排 | 已发布 |
| **1.0.3** | 8 级 DPI 图标与 `PerMonitorV2`、移除掌握度只留不会程度、双在线词典集成、在线词典来源持久化、移除英英模式 | **当前版本** |
| 1.0.4（计划） | 修在线词典状态检测（区分 4xx/被拦截与真成功）、去掉内嵌视图或改为可判定方案、`Esc` 关闭弹窗、持久化 APK 签名密钥、提高 `targetSdkVersion` | 未开始 |

## 九、反馈渠道

- 缺陷与功能请求：[GitHub Issues](../../issues)。请附上平台与系统版本、复现步骤，以及（涉及数据时）是否已导出 `.json` 备份。
- 代码贡献：见 `CONTRIBUTING.md`；提交前请跑 `build_all.sh` + `verify_apk_deep.py` + `run_e2e_v103.py`。
- 本项目按 MIT 许可提供，**不提供任何担保**；Android 版尤其请按"实验软件、可能丢数据"的前提使用。
