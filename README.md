# Voca — 离线艾宾浩斯背单词

**Voca** 是一款离线单机的艾宾浩斯遗忘曲线背单词软件（Windows）。背诵、计划表生成、生词本管理、拼词训练、多页 PDF 导出全部 **100% 离线**可用：不注册账号、不上传数据，学习进度只存在你自己的电脑里。仅「在线词典查询」在你主动使用时按需联网。

## 特色功能

### 📚 词库

- 内置 **43,304 条词条 / 14,956 个不重复单词**，共 **9 本词书**：中考、高考、四级核心、**四级完整词表（4,449 词，按词表原序收入）**、六级、考研、托福、雅思、GRE。词库源自开源词典 [ECDICT](https://github.com/skywind3000/ECDICT)（MIT）。
- **每个单词都配有双语例句**，全库覆盖率 100%，离线可查。

### 🧠 学习与记忆

- 学习状态以 **不会程度 0~5** 单一维度管理，规则固定、不用配置：左键/轻触 = +1 并发音，右键/长按 = −1。
- **艾宾浩斯计划表**：你只需设定 List 个数，每天新学 1 个 List，天数由软件按遗忘曲线间隔（+1 / +2 / +4 / +7 / +15 天）自动排期，共 List 数 + 15 天；逐日打卡、进度百分比一目了然。词序可在「原序版本 / 乱序版本」之间切换。
- 学习页提供双语 / 只看英文 / 只看中文三种遮罩模式，列表与沉浸卡片两种视图，以及初始序列、随机序列、字母升序、不会的排前面、易掌握的排前面 5 种排序；全库搜索可跨词书定位任意单词并跳转高亮。
- **专项训练**：拼词挑战，针对拼写弱项强化。
- **生词本**：收藏生词、自定义中文释义、个人笔记、标熟移除、批量恢复。

### 📖 词典

- 单词详情弹窗打开即显示本地词库的释义与例句，不用等网络。
- 在线词典三源按需查询：欧路词典、爱词霸直接在弹窗内显示，WordReference 在 Voca 自己的词典窗口中打开。
- 发音支持美式 / 英式两种口音。

### 📥 导入与导出

- **词库导入**：支持 CSV / TSV / TXT / JSON 文件（自动识别 UTF-8 与 GBK/GB18030 编码），也支持把文本直接粘贴进来解析导入。
- **Agent 导入**：把你找到的任意格式词库文件（PDF / Word / 表格 / 网页 / 图片）连同软件内置的一段提示词发给你的 AI Agent，它会生成符合 Voca 格式的 `voca_import.csv`，下载回来即可导入。
- **多页 A4 导出**：艾宾浩斯学习计划表、当前 List 双语对照词表、默写自测卷（隐中/隐英）、生词本重难词手册，均可导出为 PDF 或打印版，也可下载为独立 HTML。
- **完整备份**：全部学习状态（不会程度、生词本、自定义释义、笔记、计划与打卡记录）一键导出为 `.json`，随时恢复；也支持粘贴文本恢复。

### 💾 数据可靠

- 存档只保存非默认的学习记录，体积小、写入快，并带防抖保存与退出落盘。
- 本地存储损坏时自动从备份存储恢复，并把坏数据另存留痕，不让进度无声丢失。
- 全部数据都在程序目录内（便携式），拷贝文件夹即可整机迁移。

### 🎨 界面与偏好

- 简约现代的界面：浅色 / 深色主题一致，卡片轻边框、胶囊分段控件、细分割线。
- 三种主题（daylight / oled / paper）、字号、发音口音等偏好全部本地持久化。
- 原生 Win32 + WebView2 宿主：`PerMonitorV2` 高 DPI 适配，任务栏图标按当前缩放精确取帧；免安装，解压即用。

## 下载与安装

编译好的产物只放在 **GitHub Releases**，不提交进 git 树。请到 [Releases](https://github.com/WRM-FW/voca/releases) 页面下载：

| 资产 | 说明 |
| :--- | :--- |
| `Voca_v1.0.8_Windows_x64.zip` | 免安装绿色包，含 `Voca.exe`、`WebView2Loader.dll`、`windows/app/`、`windows/data/` |
| `Voca_v1.0.8_source.zip` | 源码包，与 `v1.0.8` 标签的源码快照等价 |

### 运行要求

- **64 位 Windows 10 1803 及以上 / Windows 11**（`Voca.exe` 为 PE32+ x86_64 GUI 程序）。
- 需要 **Microsoft Edge WebView2 Runtime**（Win11 与近年更新的 Win10 已内置；也可从微软官网安装 "Evergreen Bootstrapper"）。`Voca.exe` 是原生 Win32 宿主，通过 `WebView2Loader.dll` 加载该运行时；**`WebView2Loader.dll` 必须与 `Voca.exe` 放在同一目录**。
- 若运行时不可用，程序会弹出提示并退回用系统 Edge/Chrome 的 `--app` 窗口打开（功能一致）。
- 无需管理员权限。

### 安装与启动

1. 解压 ZIP 到任意目录，**保持目录结构不变**——宿主按自身所在目录定位 `app\index.html`、`data\profile` 与 `WebView2Loader.dll`。
2. 打开 `windows/` 文件夹，双击 **`Voca.exe`**。需要桌面入口时，右键 `Voca.exe` → 发送到 → 桌面快捷方式。
3. 首次启动会在 `windows/data/profile/` 下生成 WebView2 用户数据目录（主要是浏览器缓存，属正常），学习数据本身只占其中很小一部分。

### 升级

- 解压新版后，用新版的 `Voca.exe`、`WebView2Loader.dll` 与 `windows/app/` 覆盖旧版同名内容，**保留旧版 `windows/data/profile/` 不动**，学习数据自动延续。
- 或者：旧版里导出完整学习备份（`.json`），新版里从备份文件恢复。
- **不要**直接删除整个 `windows/` 文件夹后再装新版，那会连 `data/profile/` 一起删掉。

## 用户数据

- 学习数据位于 `<解压目录>/windows/data/profile/EBWebView/Default/` 下的 Local Storage 与 IndexedDB 中，是便携式本地目录，可直接查看、复制、备份。
- 仓库与 Release 包**不含任何个人学习数据**：`.gitignore` 已排除 `windows/data/profile/`。
- Voca 没有账号体系，不支持云端同步；换机请用 `.json` 备份搬运。

## 开发与构建

### 仓库结构

```text
.
├── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md  THIRD_PARTY_NOTICES.md
├── requirements.txt            # Python 构建与测试依赖
├── src/
│   ├── webapp/                 # 前端构建源码（真正的前端在这里改）
│   │   ├── make_html_v103_part1.py   # 样式与 <head>
│   │   ├── make_html_v103_part2.py   # DOM 模板
│   │   ├── make_html_v103_part3.py   # JavaScript 状态机 + 组装 index.html
│   │   └── index.html                # 构建同步产物（勿手改）
│   ├── windows/
│   │   ├── voca_host.c               # 原生 Win32 + WebView2 宿主（发布用）
│   │   ├── voca_host.rc              # .rsrc：RT_ICON / RT_GROUP_ICON / RT_MANIFEST
│   │   ├── voca_host.exe.manifest    # PerMonitorV2 + asInvoker
│   │   └── voca_launcher.c           # 旧 Edge --app 启动器（兼容模式参考实现）
│   └── lexicon/                # 词库提取、清洗与构建源码
├── third_party/webview2/       # 随仓库附带的 WebView2 头文件与 WebView2Loader.dll（BSD-3）
├── scripts/
│   ├── build_all.sh            # 一键构建与验证
│   ├── build_assets_v103.py    # 图标裁剪、DIB 生成、WOFF2 子集（需 VOCA_BUILD_ASSETS=1）
│   ├── build_host_v104.py      # 用 gcc/windres 编译原生 WebView2 宿主 Voca.exe
│   ├── build_exe_v103.py       # 生成旧版 Edge --app 启动器（兼容模式参考实现）
│   └── run_e2e_v103.py         # Selenium 端到端测试
├── assets/                     # 图标源帧、WOFF2 子集、OFL 许可、内嵌资产清单
├── windows/                    # 前端与词库运行资源（Voca.exe / WebView2Loader.dll 由构建生成，不入库）
│   ├── app/ (index.html, voca.ico, fonts/)
│   └── data/ (voca.db, voca_lexicon.*, schema.sql, LICENSE-ECDICT.txt, 词库数据包说明.md)
└── docs/                       # 设计说明、迁移指南、许可合规与验收报告
```

发布用的 `Voca.exe` 由 `scripts/build_host_v104.py` 用 **gcc + windres 真实编译** `src/windows/voca_host.c`。`src/windows/voca_launcher.c` 与 `scripts/build_exe_v103.py` 是早期的 Edge `--app` 启动器，保留作为 WebView2 不可用时的兼容模式参考，不再是主产物。

### 环境与依赖

- **Python** >= 3.10，`pip install -r requirements.txt`（Pillow、fonttools、brotli、pypdf、selenium、cryptography）。
- **构建 `Voca.exe` 需要 C 工具链**：`gcc` 与 `windres`（MinGW-w64）。WebView2 的头文件与 `WebView2Loader.dll` 已随仓库放在 `third_party/webview2/`，**不需要联网获取 SDK**。缺少工具链时 `build_all.sh` 会跳过原生宿主并退回构建旧版启动器，同时打印原因。
- 只有当你要**重新生成字体子集与小图标帧**时才需要上游 OTF/TTC 源（Debian/Ubuntu 的 `fonts-inter`、`fonts-noto-cjk`）。`assets/` 已预置生成好的 WOFF2 与图标帧，默认构建不碰它们。

### 一键构建与测试

```bash
bash scripts/build_all.sh               # 前端组装 → Windows 图标 → 原生 WebView2 宿主
VOCA_BUILD_ASSETS=1 bash scripts/build_all.sh   # 额外重生成图标帧与 WOFF2 子集，依赖上游字体源
python3 scripts/run_e2e_v103.py         # Selenium + Chromium 端到端功能与存档迁移测试
```

脚本全部使用相对仓库根目录的路径，不依赖任何开发机私有目录。

## 开源许可证与第三方资源

- **项目自有源码**（`src/`、`scripts/`、`docs/`）：**MIT License**，见 `LICENSE`。
- **内置词库 `voca.db`**：源自 [ECDICT](https://github.com/skywind3000/ECDICT)，**MIT License**，许可全文见 `windows/data/LICENSE-ECDICT.txt`。
- **内嵌字体**（Inter、Noto Sans CJK SC 的 WOFF2 子集）：**SIL Open Font License 1.1**，全文见 `assets/LICENSE-OFL-1.1.txt`。
- **WebView2 SDK 头文件与 `WebView2Loader.dll`**（`third_party/webview2/`）：Microsoft，**BSD 3-Clause**，见 `third_party/webview2/LICENSE.txt`。
- **软件图标**：仓库所有者自有资产，已确认著作权与再分发授权。
- **在线词典**：不打包、不分发对方数据，仅客户端实时访问，受欧路、爱词霸与 WordReference 各自服务条款约束。

逐项核查与边界见 **`THIRD_PARTY_NOTICES.md`**。

## 已知限制

1. **`Voca.exe` 未代码签名**，Windows 可能弹出 SmartScreen 提示。
2. **词库音标沿用 ECDICT 记法**，不是严格 IPA（如 `state` 标作 `/steit/` 而非 `/steɪt/`）；`pos` 字段是词性频次统计而非词性标签。详见 `windows/data/词库数据包说明.md`。
3. **WordReference 的词条显示在 Voca 自己的「在线词典窗口」里，而不是弹窗内嵌**：该站的人机验证只在顶层框架能完成，首次查询需数秒，站点限流时窗口可能显示质询页或 403。欧路与爱词霸直接在弹窗内显示。
4. **词典窗口没有自带的前进/后退/刷新按钮**（可用 Alt+← 后退），关闭后下次查询会重新打开。
5. 新增词条的例句经机器校验，未经人工逐条校对。

## 反馈

- 缺陷与功能请求：[GitHub Issues](https://github.com/WRM-FW/voca/issues)。请附上系统版本、复现步骤，以及（涉及数据时）是否已导出 `.json` 备份。
- 代码贡献：见 `CONTRIBUTING.md`；提交前请跑 `build_all.sh` 与 `run_e2e_v103.py`。
- 本项目按 MIT 许可提供，**不提供任何担保**。
