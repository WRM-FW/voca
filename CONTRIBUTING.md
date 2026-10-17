# Contributing to Voca

感谢关注 **Voca** 双平台离线背单词项目。

## 一、目录与改动约定

- `src/webapp/`：前端全部源码。改界面、样式或交互逻辑请编辑 `make_html_v103_part1.py`（样式与 `<head>`）、`part2.py`（DOM 模板）、`part3.py`（JavaScript 状态机 + 组装），**不要手改编译产物 `index.html`**（`windows/app/index.html`、`src/webapp/index.html`、`src/android/app/src/main/assets/index.html` 三处由 `build_all.sh` 同步覆盖）。
- `src/windows/`：**v1.0.4 起发布用的 `Voca.exe` 是真实编译产物** —— `voca_host.c` + `voca_host.rc` + `voca_host.exe.manifest`，由 `scripts/build_host_v104.py` 调 gcc/windres 构建，WebView2 的头文件与 `WebView2Loader.dll` 随仓库放在 `third_party/webview2/`。`voca_launcher.c` 与 `scripts/build_exe_v103.py` 是 v1.0.3 的 Edge `--app` 启动器，只在没有 C 工具链或没有 WebView2 Runtime 时作为兼容路径保留；改启动行为时请说明改的是哪一份。
- `src/android/`：Android WebView 容器工程源码（`MainActivity.java`、`AndroidManifest.xml`、`build.gradle`）。**注意：发布 APK 的 `classes.dex` 由 `scripts/build_apk_v103.py` 手写 Dalvik 字节码生成，改 `MainActivity.java` 不会影响 APK**；该文件是 Gradle 侧的等价参考壳层，需要新容器能力（文件选择器、下载、打印、安全区）时，两处都要改或明确改用 Gradle 构建。
- `src/lexicon/`：词库提取、清洗与构建源码。
- `scripts/`：资产构建、PE/APK 构建、校验与端到端测试脚本。
- `assets/`、`windows/data/`：图标源帧、WOFF2 子集、词库与许可文本。

## 二、构建

```bash
pip install -r requirements.txt
bash scripts/build_all.sh
```

- 默认**跳过**图标/字体重生成（`build_assets_v103.py` 硬编码 Debian 系上游字体路径 `/usr/share/fonts/opentype/...`）。要重建资产请显式 `VOCA_BUILD_ASSETS=1 bash scripts/build_all.sh` 并先装好 `fonts-inter`、`fonts-noto-cjk`。
- 构建 `Voca.exe` 需要 C 工具链 **`gcc` + `windres`**（实测 MinGW-w64 8.1.0）；没有工具链时 `build_all.sh` 会打印原因并退回构建旧版启动器。构建 APK 只需要 Python + OpenSSL。运行 `Voca.exe` 需要 **Microsoft Edge WebView2 Runtime**。
- Windows 上 `python3` 常常是 Microsoft Store 的 app-execution alias，与 `python` 是两个不同解释器；`build_all.sh` 会自动挑选能 `import PIL, fontTools, brotli, cryptography` 的那个，也可 `VOCA_PYTHON=/path/to/python` 指定。
- 产物 `windows/Voca.exe`、`windows/WebView2Loader.dll` 与 `android/*.apk` 已在 `.gitignore` 中排除，**不要提交进 git 树**，发布走 GitHub Release。

## 三、提交前的验证清单

1. `bash scripts/build_all.sh` 全程无报错。
2. `python3 scripts/verify_apk_deep.py` 通过（APK 的 AXML/ARSC/DEX 结构与 v1/v2 签名的密码学校验）。
3. `python3 scripts/run_e2e_v103.py` 通过（Chromium 端到端功能与旧版本存档迁移测试）。
4. 在仓库副本上重跑构建并与前一次产物做逐字节比对，确认改动没有引入不可复现的输出（时间戳、随机数、绝对路径）。
5. 全仓扫描确认未引入本机绝对路径、私钥、令牌或未声明许可证的第三方资产。
6. 涉及 UI/图标/布局的改动，必须在真实缩放的桌面上看渲染结果，不能只看二进制断言。
7. 涉及触屏外壳（`html.ui-mobile`、`@media (pointer: coarse)`、`.m-only` / `.d-only`）的改动，必须用真实 Chromium 的手机视口复验：至少覆盖 320×568、360×640、390×844、844×390、1024×768，检查外壳选中是否正确、横向溢出为 0、可交互控件不小于 44px。桌面外壳不得因此变化。
8. 不要把"能打开页面"当成"功能可用"的验收依据：涉及网络查询、导出、下载的路径，要看到真实返回内容或落盘结果，或明确标注为未验证。

## 四、说明与边界

- 在线词典（欧路 / 爱词霸 / WordReference）只是客户端实时查询，**不要在代码或安装包中抓取、缓存或分发对方词库数据**，那会违反对方服务条款。三个源的能力不同：欧路的 `/mdicts/en/` 允许跨域读取且无框架限制，爱词霸可内嵌，WordReference 的 `frame-ancestors` 白名单禁止内嵌 —— 新增来源前先实测响应头。
- 新增第三方词库/字体/图标资源时，必须在 `THIRD_PARTY_NOTICES.md` 增补来源、许可证与分发边界，并随附许可全文。
- 已知缺陷与未验证项记录在 `README.md` 第七节；实测依据在 `docs/` 下的 `05`（v1.0.3 真机复验）、`06`（任务栏图标根因）、`07`（在线词典实测）、`08`（v1.0.4 双平台验收）。修掉其中任何一条时，请同时更新这两处。
