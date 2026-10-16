# Contributing to Voca

感谢关注 **Voca** 双平台离线背单词项目。

## 一、目录与改动约定

- `src/webapp/`：前端全部源码。改界面、样式或交互逻辑请编辑 `make_html_v103_part1.py`（样式与 `<head>`）、`part2.py`（DOM 模板）、`part3.py`（JavaScript 状态机 + 组装），**不要手改编译产物 `index.html`**（`windows/app/index.html`、`src/webapp/index.html`、`src/android/app/src/main/assets/index.html` 三处由 `build_all.sh` 同步覆盖）。
- `src/windows/`：Windows 启动器的 **C 参考实现** (`voca_launcher.c`) 与可选的 CMake 构建。**发布用的 `Voca.exe` 不由它编译**，而由 `scripts/build_exe_v103.py` 用内联汇编 + 手写 PE 头与 `.rsrc` 生成（为了精确控制 8 帧图标目录与 `RT_MANIFEST`）。改动启动行为时两份都要考虑。
- `src/android/`：Android WebView 容器工程源码（`MainActivity.java`、`AndroidManifest.xml`、`build.gradle`）。注意发布 APK 同样由 `scripts/build_apk_v103.py` 纯 Python 生成 AXML/ARSC/DEX 并签名，`build.gradle` 是等价的 Gradle 侧参考。
- `src/lexicon/`：词库提取、清洗与构建源码。
- `scripts/`：资产构建、PE/APK 构建、校验与端到端测试脚本。
- `assets/`、`windows/data/`：图标源帧、WOFF2 子集、词库与许可文本。

## 二、构建

```bash
pip install -r requirements.txt
bash scripts/build_all.sh
```

- 默认**跳过**图标/字体重生成（`build_assets_v103.py` 硬编码 Debian 系上游字体路径 `/usr/share/fonts/opentype/...`）。要重建资产请显式 `VOCA_BUILD_ASSETS=1 bash scripts/build_all.sh` 并先装好 `fonts-inter`、`fonts-noto-cjk`。
- 构建 `Voca.exe` 需要 GNU Binutils（`as`、`objcopy`）与 OpenSSL；构建 APK 只需要 Python + OpenSSL。
- 产物 `windows/Voca.exe` 与 `android/*.apk` 已在 `.gitignore` 中排除，**不要提交进 git 树**，发布走 GitHub Release。

## 三、提交前的验证清单

1. `bash scripts/build_all.sh` 全程无报错。
2. `python3 scripts/verify_apk_deep.py` 通过（APK 的 AXML/ARSC/DEX 结构与 v1/v2 签名的密码学校验）。
3. `python3 scripts/run_e2e_v103.py` 通过（Chromium 端到端功能与旧版本存档迁移测试）。
4. 在仓库副本上重跑构建并与前一次产物做逐字节比对，确认改动没有引入不可复现的输出（时间戳、随机数、绝对路径）。
5. 全仓扫描确认未引入本机绝对路径、私钥、令牌或未声明许可证的第三方资产。
6. 涉及 UI/图标/布局的改动，必须在真实缩放的桌面上看渲染结果，不能只看二进制断言。

## 四、说明与边界

- 在线词典（欧路 / WordReference）只是客户端实时查询，**不要在代码或安装包中抓取、缓存或分发对方词库数据**，那会违反对方服务条款。
- 新增第三方词库/字体/图标资源时，必须在 `THIRD_PARTY_NOTICES.md` 增补来源、许可证与分发边界，并随附许可全文。
- 已知缺陷与未验证项记录在 `README.md` 第七节；实测依据在 `docs/05_Voca_v1.0.3_Windows宿主机真机复验报告_20261017.md`。修掉其中任何一条时，请同时更新这两处。
