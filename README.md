# Voca v1.0.4 — 离线艾宾浩斯背单词（Windows & Android）

**Voca** 是一款离线单机的艾宾浩斯遗忘曲线背单词软件，同一套前端同时跑在 Windows 桌面与 Android 手机上。背诵、计划表生成、生词本管理、拼词/滚动训练、多页 PDF 导出全部 **100% 离线**可用，不注册账号、不上传数据；「查看词典详细与编辑」模块额外提供按需的在线词典查询。

- 内置 **38,855 条**词条，覆盖中考 / 高考 / 四级 / 六级 / 考研 / 托福 / 雅思 / GRE 八大词书（源自开源词典 [ECDICT](https://github.com/skywind3000/ECDICT)，MIT）。
- 学习状态以 **不会程度 0~5** 单一维度管理：桌面左键加深 / 右键降低，手机轻触加深 / 长按降低；配合自定义组数与周期的艾宾浩斯计划表与每日打卡。
- 完整学习状态可一键导出为 `.json` 备份，Windows 与 Android **双向互通**。

## 版本成熟度：请先看这一节

| 平台 | 定位 | 依据 |
| :--- | :--- | :--- |
| **Windows** | **当前推荐版本** | 原生 Win32 + WebView2 宿主，已在真实 Windows 11（内部版本 26200、150% 缩放、WebView2 Runtime 155）完成启动、任务栏图标像素级比对、界面布局、不会程度交互、数据持久化、v1.0.2/v1.0.3 存档迁移、在线词典真实查询共 20+ 项复验，全部通过。 |
| **Android** | **实验版 / 开发中，暂不推荐作为主力使用版本** | 前端已通过真实 Chromium 手机视口（CDP）在 8 个分辨率下的布局、触控目标与功能验证；APK 通过官方 `apksigner`（v1+v2 签名有效）与 `aapt2` 结构校验。**但发布环境没有任何 Android 真机或模拟器（`adb devices` 为空），安装、启动、系统 WebView 渲染、返回键、发音、剪贴板均未实测**，兼容范围未知。 |

Windows 版仍有未修完的缺陷（弹窗 `Esc`、WordReference 无法内嵌），见 [第七节 已知问题](#七已知问题)。

## v1.0.4 相对 v1.0.3 的变化

1. **Windows 宿主从「Edge `--app` 外部窗口」换成原生 Win32 + WebView2 窗口**。这是任务栏图标模糊的真正修复：旧架构下窗口图标由浏览器进程决定，前端与 `.rsrc` 都改不动它。
2. **在线词典修复**：删除会把任何 HTTP 错误伪装成「✓ 已连接」的 `mode:"no-cors"` 探测；改用可解析接口 + 真实状态判定；新增爱词霸；WordReference 按对方站点策略只保留「打开源页面」。
3. **删除「重置不会度」功能及其全部入口**（不影响任何已保存的不会程度数值、学习记录与复习流程）。
4. **删除窗口左上角的「艾宾浩斯双平台背单词工坊」副标题**。
5. **修复 Windows 首次启动额外弹出一个 Edge 窗口**（禁用扩展与同步推广：`--no-first-run --no-default-browser-check --disable-extensions --disable-sync`）。
6. **Android 端 UI 重新设计**：能力探测的触屏外壳（底部六项导航、逐页标题、单列/双列自适应、长按手势、安全区与 `100dvh`），以及触屏专用的导出复制框与粘贴恢复入口。

## 下载

编译好的产物只放在 **GitHub Releases**，不提交进 git 树。请到 [Releases](https://github.com/WRM-FW/voca/releases) 页面下载：

| 资产 | 平台 | 说明 |
| :--- | :--- | :--- |
| `Voca_v1.0.4_Windows_x64.zip` | **Windows（推荐）** | 免安装绿色包，含 `Voca.exe`、`WebView2Loader.dll`、`windows/app/`、`windows/data/` |
| `Voca_v1.0.4_release.apk` | Android（实验版） | `versionCode=5`，`versionName=1.0.4`，自签证书 |
| `Voca_v1.0.4_source.zip` | 源码 | 与 `v1.0.4` 标签的源码快照等价 |

Windows 与 Android 内嵌的前端 `index.html` 构建自同一份源码、同一套生成器，两端行为基准一致；差异只在容器层。

---

## 一、主要功能与适用场景

| 模块 | 能力 |
| :--- | :--- |
| 单词学习 | 双语 / 只看英文 / 只看中文三种遮罩模式；桌面左键加深不会程度 (+1) 并发音、右键降低 (-1)，触屏轻触 +1、长按 -1；4 种点击分区模式可切换 |
| 艾宾浩斯计划表 | 任意组数 N 与任意周期天数 D 的自定义计划，三种排组方式，逐日打卡与进度百分比 |
| 专项强化训练 | 拼词挑战与滚动速认 |
| 生词本与熟词表 | 收藏生词、自定义中文释义、个人笔记、标熟移除、批量恢复 |
| 词库导入与 PDF 导出 | 自定义词表 CSV 导入与粘贴导入、当前词库 CSV 导出、多页 A4 计划表/词库 PDF 与打印版离线导出、完整学习状态 `.json` 备份与恢复 |
| 词典详细与编辑 | 内置精编双解词库（233 条，项目自编）+ 按需在线查询欧路词典 / 爱词霸 / WordReference（各站能力不同，见第七节） |
| 偏好设置 | 主题（daylight / oled / paper）、字号、英美音、在线词典来源选择，全部本地持久化 |

适用场景：需要长期背应试词汇、又不想把学习进度交给云端账号的人；在没网的自习室、飞机、宿舍里用；以及希望同时在电脑和手机上背、进度能互相搬运的人。

---

## 二、Windows 版：下载、安装、启动与升级（推荐版本）

### 2.1 运行要求
- **64 位 Windows 10 1803 及以上 / Windows 11**（`Voca.exe` 为 PE32+ x86_64 GUI 程序）。
- 需要 **Microsoft Edge WebView2 Runtime**（Win11 与近年更新的 Win10 已内置；也可从微软官网安装 "Evergreen Bootstrapper"）。`Voca.exe` 是原生 Win32 宿主，通过 `WebView2Loader.dll` 加载该运行时。
- **`WebView2Loader.dll` 必须与 `Voca.exe` 放在同一目录**，缺它会直接退到兼容模式。
- 若运行时不可用，程序会弹出提示并**退回用系统 Edge/Chrome 的 `--app` 窗口打开**（功能一致，但任务栏图标由浏览器接管、会显得偏软）。
- 无需管理员权限：清单只有 `PerMonitorV2` 高 DPI 声明与 `asInvoker`。

### 2.2 安装与启动
1. 解压 ZIP 到任意目录（例如 `D:\Voca_v1.0.4\`），**保持目录结构不变**——宿主按自身所在目录定位 `app\index.html`、`data\profile` 与 `WebView2Loader.dll`。
2. 打开 `windows/` 文件夹，双击 **`Voca.exe`**。
3. 程序以最大化原生窗口启动，标题栏与任务栏图标按当前 DPI 精确取帧（100% 取 16px、150% 取 24px、200% 取 32px…），拖动到不同缩放的显示器会自动换帧。需要桌面入口时，右键 `windows/Voca.exe` → 发送到 → 桌面快捷方式。
4. 首次启动会在 `windows/data/profile/` 下生成 WebView2 用户数据目录（实测约 50~90 MB，主要是浏览器缓存，属正常），学习数据本身只占其中几百 KB，见第五节。

### 2.3 升级到新版本
- **推荐做法（同目录继承）**：解压新版后，用新版的 `Voca.exe`、`WebView2Loader.dll` 与 `windows/app/` 覆盖旧版同名内容，**保留旧版 `windows/data/profile/` 不动**，学习数据自动延续。
- v1.0.3 及更早版本用的是 Edge `--app` 外壳，数据落在 `data/profile/Default/`；v1.0.4 的 WebView2 读的是 `data/profile/EBWebView/Default/`。宿主启动时会自动把前者镜像到后者一次（幂等，带 `Voca.migrated` 哨兵文件），无需手工搬运。
- **或者（备份恢复）**：旧版里点「词库导入与PDF导出」→「⬇ 导出完整学习备份 (.json)」，新版里点「⬆ 从备份文件恢复数据」。
- **不要**直接删除整个 `windows/` 文件夹后再装新版，那会连 `data/profile/` 一起删掉。

---

## 三、Android 版：获取、安装要求与当前限制（实验版）

> **本版本尚不成熟，暂不推荐作为主要使用版本。** 下面写的是已核实的事实与未核实的边界，不要把"结构校验通过"读成"能正常用"。

### 3.1 已核实
- `apksigner verify`：v1 (JAR) 与 v2 (APK Signature Scheme v2) 签名**均验证通过**；单一签名者 `CN=Voca Offline Studio, O=Voca, C=CN`，RSA 2048。
- `aapt2 dump badging`：`com.voca.app`，`versionCode=5`，`versionName=1.0.4`，`minSdkVersion=19`，`targetSdkVersion=28`，声明 `android.permission.INTERNET`，启动 Activity `com.voca.app.MainActivity`。
- APK 内 `assets/index.html` 与三个 WOFF2 字体，与仓库源码树逐字节一致。
- 前端在真实 Chromium 手机视口（320×568 / 360×640 / 390×844 / 412×915 / 844×390 / 740×360 / 768×1024 / 1024×768）下验证：触屏外壳正确选中、6 个页签全部可达、500 个可交互控件**无一小于 44px**、横向溢出 0、无 JS 报错。

### 3.2 Android 端 UI 说明
v1.0.4 的 Android 界面不是 Windows 界面的缩放版，而是按触屏重排的一套外壳，由 `<head>` 里的能力探测（`(pointer: coarse)` / `(hover: none)` / UA + 视口宽度）在 `html.ui-mobile` 与 `html.ui-desktop` 之间选择：

- 底部 6 项固定导航（背单词 / 计划表 / 训练 / 生词本 / 导词·PDF / 设置），侧边栏在触屏下不出现。
- 每页有自己的标题与说明；统计卡在手机竖屏 2 列、≤360px 单列、平板/横屏 3 列自适应。
- **长按单词行 = 不会程度 −1**（等效桌面右键，带 480ms 蓄力反馈与 12px 位移取消阈值）。
- 弹窗按视口高度自适应（`min(90vh, 100dvh - 24px)`），词典内容区可独立滚动且不会顶破窗口。
- 安全区（`env(safe-area-inset-*)`）与横屏矮视口有专门规则。

### 3.3 安装步骤
1. 从 Release 下载 `Voca_v1.0.4_release.apk` 传到手机。
2. 因为是**自签名**且未上架应用商店，需要允许「安装未知来源应用」。
3. 清单声明的最低系统是 Android 4.4（API 19）。

### 3.4 未验证与限制
- **未在任何真机或模拟器上安装、启动或运行过**（发布环境无可用 Android 设备）。安装成功率、系统 WebView 渲染、发音、返回键、剪贴板、不同厂商 ROM 的差异全部**未验证**。
- `targetSdkVersion=28` 远低于当前商店要求，在 Android 13/14/15 上侧载会出现系统风险提示。
- **签名密钥不持久**：构建脚本每次在临时目录现生成自签证书后即销毁。因此你自行重建的 APK 与 Release 版签名不一致，**覆盖安装会报签名冲突**，只能先卸载再装，而卸载会清空数据 —— 所以升级前务必先导 `.json` 备份。
- 数据在应用私有沙箱 `/data/data/com.voca.app/` 内，无 Root 的手机无法用文件管理器直接取出，只能靠 `.json` 备份导出。
- **APK 的 WebView 壳层没有实现文件选择器、下载监听与打印通道**（`src/android/.../MainActivity.java` 是只含三个方法的参考壳层，且发布 APK 的 `classes.dex` 由 `scripts/build_apk_v103.py` 手写生成，改 Java 不影响 APK）。为此 v1.0.4 在触屏外壳里补了网页侧的替代路径：
  - 导出的 `.json` 备份与词库 CSV 会显示在「导出内容」框里，点「复制到剪贴板」或长按全选后自行保存；
  - 恢复可把备份文本粘贴到「从粘贴内容恢复备份」；
  - 自定义词表另有「粘贴导入」框；
  - **PDF 与独立 HTML 导出在 Android 上会明确提示无法保存**，不再假装成功。这些能力需要在 Windows 版使用。

---

## 四、开发环境、依赖、构建与测试

### 4.1 仓库结构

```text
.
├── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md  THIRD_PARTY_NOTICES.md
├── requirements.txt            # Python 构建与测试依赖
├── .gitignore  .gitattributes
├── src/
│   ├── webapp/                 # 前端构建源码（真正的前端在这里改）
│   │   ├── make_html_v103_part1.py   # 样式与 <head>（含触屏/桌面外壳能力探测）
│   │   ├── make_html_v103_part2.py   # DOM 模板
│   │   ├── make_html_v103_part3.py   # JavaScript 状态机 + 组装 index.html
│   │   └── index.html                # 构建同步产物（勿手改）
│   ├── windows/
│   │   ├── voca_host.c               # v1.0.4 原生 Win32 + WebView2 宿主（发布用）
│   │   ├── voca_host.rc              # .rsrc：RT_ICON / RT_GROUP_ICON / RT_MANIFEST
│   │   ├── voca_host.exe.manifest    # PerMonitorV2 + asInvoker
│   │   ├── voca_launcher.c           # 旧 Edge --app 启动器（兼容模式参考实现）
│   │   └── CMakeLists.txt
│   ├── android/                # Android 壳层工程（MainActivity.java / AndroidManifest.xml / build.gradle）
│   └── lexicon/                # 词库提取、清洗与构建源码
├── third_party/webview2/       # 随仓库附带的 WebView2 头文件与 WebView2Loader.dll（BSD-3）
├── scripts/
│   ├── build_all.sh            # 一键构建与验证
│   ├── build_assets_v103.py    # 图标裁剪、DIB 生成、WOFF2 子集（需 VOCA_BUILD_ASSETS=1）
│   ├── build_host_v104.py      # 用 gcc/windres 编译原生 WebView2 宿主 Voca.exe
│   ├── build_exe_v103.py       # 生成旧版 Edge --app 启动器（内联汇编 + 手写 PE .rsrc）
│   ├── build_apk_v103.py       # 生成并签名 APK（纯 Python AXML/ARSC/DEX + v1/v2 签名）
│   ├── verify_apk_deep.py      # APK 二进制结构与签名深度校验（依赖 cryptography）
│   └── run_e2e_v103.py         # Selenium 端到端测试
├── assets/                     # 图标源帧、WOFF2 子集、OFL 许可、内嵌资产清单
├── windows/                    # 前端与词库运行资源（Voca.exe / WebView2Loader.dll 由构建生成，不入库）
│   ├── app/ (index.html, voca.ico, fonts/)
│   └── data/ (voca.db, voca_lexicon.*, schema.sql, LICENSE-ECDICT.txt, 词库数据包说明.md)
├── android/                    # APK 由构建生成，不入库
└── docs/                       # 版本说明、迁移指南、许可合规、验收与根因报告
```

**关于两份 Windows 宿主实现**：发布用的 `Voca.exe` 由 `scripts/build_host_v104.py` 用 **gcc + windres 真实编译** `src/windows/voca_host.c`（v1.0.4 起）。`src/windows/voca_launcher.c` 与 `scripts/build_exe_v103.py` 是 v1.0.3 的 Edge `--app` 启动器，保留作为 WebView2 不可用时的兼容模式参考，不再是主产物。

### 4.2 环境与依赖
- **Python** >= 3.10，`pip install -r requirements.txt`（Pillow、fonttools、brotli、pypdf、selenium、cryptography）。
  Windows 上 `python3` 常是 Microsoft Store 的 app-execution alias，与 `python` 不是同一个解释器；`build_all.sh` 会自动挑选第一个能 `import PIL, fontTools, brotli, cryptography` 的解释器，也可用 `VOCA_PYTHON=/path/to/python` 指定。
- **构建 `Voca.exe` 需要 C 工具链**：`gcc` 与 `windres`（实测 MinGW-w64 8.1.0 / Binutils 2.30）。WebView2 的头文件与 `WebView2Loader.dll` 已随仓库放在 `third_party/webview2/`，**不需要联网获取 SDK**。缺少工具链时 `build_all.sh` 会跳过原生宿主并退回构建旧版启动器，同时打印原因。
- **运行 `Voca.exe` 需要 WebView2 Runtime**（见 2.1）。
- **构建 APK 只需 Python + OpenSSL**（AXML/ARSC/DEX 与签名都是纯 Python 生成，不需要 Android SDK）。
- 只有当你要**重新生成字体子集与小图标帧**时才需要上游 OTF/TTC 源（Debian/Ubuntu 的 `fonts-inter`、`fonts-noto-cjk`）。`assets/` 已预置生成好的 WOFF2 与图标帧，默认构建不碰它们。注意：`assets/icons/master_icon.png` 目前只有 512×512，`VOCA_BUILD_ASSETS=1` 重裁会让 16/20/24px 小帧变糊，除非你替换成 2048×2048 母图。

### 4.3 一键构建

```bash
bash scripts/build_all.sh
```

依次执行：前端组装 → 签名 APK → 原生 WebView2 宿主 → APK 深度校验。图标/字体资产重生成是**可选**步骤：

```bash
VOCA_BUILD_ASSETS=1 bash scripts/build_all.sh   # 会调用 build_assets_v103.py，依赖上游字体源
```

脚本全部使用相对仓库根目录的路径，且不依赖任何开发机私有目录；实测在 Windows(Git Bash) 下可跑通，Linux 路径未在本轮复验。

### 4.4 复现性与验证

在仓库完整副本上执行 `bash scripts/build_all.sh`，与 Release 产物逐字节比对（2026-10-17 于 Windows 11 实测）：

| 产物 | 结果 |
| :--- | :--- |
| `windows/app/index.html` 及其两处同步副本、`voca.ico`、`embedded_assets.json` | 见 `docs/08` 第 6.2 节 |
| `windows/Voca.exe` | 由 gcc 真实编译，同版本源码可复现；`--no-insert-timestamp` 已固定时间戳字段 |
| `android/Voca_v1.0.4_release.apk` | 两次连续构建的 11 个条目中，**唯一有差异的是 `META-INF/CERT.RSA`**（自签证书每次现生成），其余载荷逐字节一致 |

### 4.5 测试
```bash
python3 scripts/verify_apk_deep.py     # APK 二进制结构 + v1/v2 签名密码学校验
python3 scripts/run_e2e_v103.py        # Selenium + Chromium 端到端功能与存档迁移测试
```
`run_e2e_v103.py` 需要本机有 Chrome/Chromium 与可用的 WebDriver。本轮 v1.0.4 的触屏视口验收使用 Node 内置 WebSocket 直连 Chrome DevTools Protocol 完成，脚本未纳入 `scripts/`，方法与结果记录在 `docs/08`。

---

## 五、用户数据：位置、备份与迁移

### 5.1 数据实际存放位置

| 平台 | 学习数据路径 | 内置词库与程序资源 | 访问方式 |
| :--- | :--- | :--- | :--- |
| **Windows (v1.0.4)** | `<解压目录>/windows/data/profile/EBWebView/Default/Local Storage/leveldb/`<br>`<解压目录>/windows/data/profile/EBWebView/Default/IndexedDB/` | `<解压目录>/windows/data/voca.db`<br>`<解压目录>/windows/app/index.html`<br>`<解压目录>/windows/app/fonts/` | 便携式本地目录，可直接在资源管理器里查看、复制、备份 |
| **Windows (v1.0.3 及更早)** | `<解压目录>/windows/data/profile/Default/…`（宿主启动时自动镜像一次到新路径） | 同上 | 同上 |
| **Android** | `/data/data/com.voca.app/app_webview/Default/Local Storage/`<br>`/data/data/com.voca.app/app_webview/Default/IndexedDB/` | APK 内部只读资产：`assets/index.html`、`assets/fonts/` | 受系统沙箱保护，无 Root 无法用文件管理器访问 |

学习记录本身很小（实测 Local Storage 单条日志几百字节 ~ 数十 KB，备份 JSON 约 380 KB）；`profile/` 目录的体积主要是浏览器缓存（ShaderCache、组件下载缓存等），不属于学习数据。

### 5.2 备份（强烈建议在升级或换机前做一次）
1. 进入 **「词库导入与PDF导出」**；
2. 点 **「⬇ 导出完整学习备份 (.json)」**；
3. Windows：把生成的 `voca_backup_*.json` 存到安全位置。Android：在「导出内容」框点「复制到剪贴板」，粘贴到备忘录或任意文本文件后保存。

恢复：Windows 点 **「⬆ 从备份文件恢复数据」** 选中该 `.json`；Android 把备份文本粘贴到 **「从粘贴内容恢复备份」** 的输入框再点按钮。

### 5.3 跨平台迁移（Windows ⇄ Android）
只支持 `.json` 备份文件双向搬运：源平台导出 → 用数据线/聊天工具传到目标平台 → 目标平台导入。实测存档 JSON 约 380 KB（含全部 3,849 词的进度时约 667 KB），完整包含不会程度、生词本、自定义释义、笔记、熟词状态、自定义导入词、计划参数与打卡记录。

**不支持**：
- 云端自动同步 —— Voca 是纯离线单机软件，没有账号体系。
- 直接拷 LevelDB 目录跨系统互通 —— Windows 的 `data/profile/` 与 Android 的 `app_webview/` 虽同为 Chromium 存储，但受文件锁、权限沙箱与 LevelDB 元数据差异影响，不能互拷。

### 5.4 覆盖安装、重装与卸载的影响
- **覆盖安装**（Windows 保留 `data/profile/` 只更新程序文件；Android 用同一签名密钥构建的 APK 覆盖安装）：数据不丢。
- **删除整个 `windows/` 目录**：`data/profile/` 一并删除，数据丢失。
- **Android 卸载或「清除存储空间」**：系统彻底销毁 `/data/data/com.voca.app/`，数据丢失。**卸载前必须先导出 `.json`**。
- 仓库与 Release 包**不含任何个人学习数据**：`.gitignore` 已排除 `windows/data/profile/`。

### 5.5 从 v1.0.0 ~ v1.0.3 升级（数据兼容性）
- **存档结构未变**：v1.0.4 仍是 `schemaVersion: 4`，v1.0.0/v1.0.1/v1.0.2 的存档由 `migrateStateIfNeeded` 迁移（v3→v4：剥离废弃 `mastery`、`en_en`→`bilingual`、`mastery_asc`→`hard_first`、`mastery_lr`→`unfam_lr`），v1.0.3 存档直接读取。
- **「重置不会度」被删除不影响数据**：该功能只是把界面上一个批量清零的按钮去掉，不会程度数值、生词本、复习计划全部原样保留。
- **Windows 换了宿主**：数据目录从 `profile/Default/` 变为 `profile/EBWebView/Default/`，宿主自动镜像一次（见 2.3）。
- 以上路径已实测：注入 v1.0.2 存档迁移逐项正确；v1.0.3 旧存档在 v1.0.4 原生宿主中启动后进度、生词本、计划参数、主题全部读回。

---

## 六、开源许可证与第三方资源

- **项目自有源码与自编词库**（`src/`、`scripts/`、`docs/`、`voca_lexicon.*`）：**MIT License**，见 `LICENSE`。233 条精编双解词条的英文释义、同义词、例句与助记为项目自编。
- **内置词库 `voca.db`**：源自 [ECDICT](https://github.com/skywind3000/ECDICT)，**MIT License**，许可全文见 `windows/data/LICENSE-ECDICT.txt`。
- **内嵌字体**（Inter、Noto Sans CJK SC 的 WOFF2 子集）：**SIL Open Font License 1.1**，全文见 `assets/LICENSE-OFL-1.1.txt`。
- **WebView2 SDK 头文件与 `WebView2Loader.dll`**（`third_party/webview2/`）：Microsoft，**BSD 3-Clause**，见 `third_party/webview2/LICENSE.txt`。
- **软件图标**：仓库所有者自有资产，已确认著作权与再分发授权。
- **在线词典**：不打包、不分发对方数据，仅客户端实时访问，受欧路、爱词霸与 WordReference 各自服务条款约束。

逐项核查与边界见 **`THIRD_PARTY_NOTICES.md`** 与 `docs/03`。

---

## 七、已知问题

按影响程度排序。测量与根因数据见 `docs/05`、`docs/06`、`docs/07`、`docs/08`。

1. **Android APK 从未在真机或模拟器上运行过。** 所有 Android 端结论来自真实 Chromium 手机视口下的前端验证与 APK 二进制结构校验，容器层行为未验证。
2. **Android 无法保存导出文件。** APK 壳层缺少 `DownloadListener` / `onShowFileChooser` / 打印通道，v1.0.4 用网页侧「复制导出内容 + 粘贴恢复」绕过，但 **PDF 与独立 HTML 导出在 Android 上不可用**（会明确提示，不再谎报成功）。
3. **WordReference 只能「在浏览器中打开源页面」。** 该站的 `frame-ancestors` 白名单不含本站来源，且跨域读取被 CORS 拒绝，因此无法内嵌也无法抓取释义。欧路（`dict.eudic.net/mdicts/`）与爱词霸可正常查询。
4. **弹窗 `Esc` 快捷键不生效。** 真机派发 `Escape` 后弹窗仍显示；右上角「✕ 关闭」按钮可用。
5. **APK 签名密钥不持久**，自行重建的 APK 与 Release 版签名不一致，覆盖安装会报签名冲突。
6. **`targetSdkVersion=28` 偏低**，在 Android 13/14/15 上侧载会有系统风险提示，且无法上架应用商店。
7. **`voca.db` 音标不是严格 IPA。** ECDICT 沿用自身标注体系（如 `state` 标作 `/steit/` 而非 `/steɪt/`），影响认读精度；`pos` 字段是词性频次统计而非词性标签。详见 `windows/data/词库数据包说明.md`。
8. **未覆盖的验证项**：100%/125%/200%/250% 缩放与多屏混合 DPI 下的任务栏观感（仅在 150% 单屏做过像素级比对）、发音听感、Linux 下的一键构建、WebView2 Runtime 缺失机器上的兼容模式实测。

## 八、版本计划

| 版本 | 内容 | 状态 |
| :--- | :--- | :--- |
| 1.0.0 ~ 1.0.2 | 双平台离线首版、38,855 词条词库、APK 二进制修复、自由计划参数、离线 PDF 导出、WOFF2 子集 | 已发布 |
| 1.0.3 | 8 级 DPI 图标与 `PerMonitorV2`、移除掌握度只留不会程度、双在线词典集成、移除英英模式 | 已发布 |
| **1.0.4** | 原生 Win32 + WebView2 宿主（真正修复任务栏图标）、在线词典根因修复与三源改造、删除「重置不会度」与左上角副标题、修复首次启动多开 Edge 窗口、Android 触屏外壳重做、v1.0.3→v1.0.4 数据自动迁移 | **当前版本** |
| 1.0.5（计划） | Android 壳层补齐 `DownloadListener` / `onShowFileChooser` / 打印与 `Esc` 关闭弹窗、持久化 APK 签名密钥、提高 `targetSdkVersion`、在真机上复验 Android 全链路 | 未开始 |

## 九、反馈渠道

- 缺陷与功能请求：[GitHub Issues](https://github.com/WRM-FW/voca/issues)。请附上平台与系统版本、复现步骤，以及（涉及数据时）是否已导出 `.json` 备份。
- 代码贡献：见 `CONTRIBUTING.md`；提交前请跑 `build_all.sh` + `verify_apk_deep.py` + `run_e2e_v103.py`。
- 本项目按 MIT 许可提供，**不提供任何担保**；Android 版尤其请按"实验软件、可能丢数据"的前提使用。
