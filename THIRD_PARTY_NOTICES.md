# 第三方资源、字体、词库与品牌资产授权核查清单 (THIRD_PARTY_NOTICES)

本文件对 Voca v1.0.4 仓库中包含的自有代码、构建产物、内置词库、内嵌字体、应用图标及外部在线服务逐项区分，说明其许可证状态与公开边界。

各项结论的核查方式（二进制解析、逐文件比对、真机实测）见 `docs/05`（v1.0.3 真机复验）、`docs/06`（图标根因）、`docs/07`（在线词典取证）与 `docs/08`（v1.0.4 双平台验收）。

---

## 一、明确可公开开源与再分发的部分

### 1. 项目自有源代码与数据 (`src/`, `scripts/`, `docs/`, `windows/data/voca_lexicon.*`)
- **来源**：Voca 项目独立编写的跨平台前端代码、Windows 启动器源码、Android 壳层源码、自动化构建校验脚本，以及项目自编的 233 条「精编双解」词库内容（英文释义、同义词、双语例句、词根助记均为项目自写，未摘录任何第三方词典）。
- **许可证**：**MIT License**（见根目录 `LICENSE`）。
- **开源与商用状态**：可自由公开至 GitHub、修改、分发及商用。

### 2. 默认内置词库 (`windows/data/voca.db`)
- **来源**：38,855 词条，覆盖中考、高考、四级、六级、考研、托福、雅思、GRE 八大词书，提取自开源词典项目 [ECDICT](https://github.com/skywind3000/ECDICT)（`Copyright (c) 2025 Linwei`），按 `tag` 字段筛选、清洗音标字符、去重后重建。
- **许可证**：**MIT License**，许可全文随附于 `windows/data/LICENSE-ECDICT.txt`。
- **开源与商用状态**：在保留该版权声明与许可全文的前提下，允许随 GitHub 仓库与 Release 公开分发及商用。
- **构建与字段说明、已知不足**：见 `windows/data/词库数据包说明.md`。

### 3. 跨平台内嵌字体子集 (`assets/fonts/*.woff2`, `windows/app/fonts/*.woff2`)
- **来源**：
  1. `Inter-Regular.woff2` / `Inter-Bold.woff2`：提取自 [Inter Font Project](https://github.com/rsms/inter)（`Copyright (c) 2016-2024 The Inter Project Authors`）。
  2. `NotoSansCJKsc-Full.woff2`：提取自 [Noto CJK Project](https://github.com/notofonts/noto-cjk)（`Copyright (c) 2014-2024 Google LLC & Adobe Inc.`）。
- **许可证**：**SIL Open Font License 1.1 (OFL-1.1)**，许可全文随附于 `assets/LICENSE-OFL-1.1.txt`。
- **开源与商用状态**：根据 SIL OFL 1.1，允许对字体子集化、内嵌捆绑至软件并随仓库公开分发（不得单独出售字体文件本身）。
- **注意**：仓库内只分发子集化后的 WOFF2，不分发上游 OTF/TTC 原件；如需重新生成子集，请按 `README.md` 第五节自行安装上游字体。

### 4. 软件品牌图标 (`assets/icons/`, `assets/voca.ico`, `windows/voca.ico`, `android/.../ic_launcher.png`)
- **来源**：仓库所有者自有的 `V+书本负形图标` 设计资产，经居中裁剪、Lanczos 下采样与 Win32 DIB 编码生成全套多尺寸图标。
- **授权状态**：**已由仓库所有者确认拥有完整著作权与再分发授权**（2026-10-17 确认）。
- **公开与商用注意事项**：图标随项目以 MIT 许可证分发；如需替换为其他自制图标，替换 `assets/icons/master_icon.png` 后执行 `VOCA_BUILD_ASSETS=1 python3 scripts/build_assets_v103.py`，再重新构建即可。

---

### 5. WebView2 SDK 与运行时（v1.0.4 新增）
- **来源**：`third_party/webview2/` 内的 `WebView2.h`、`WebView2EnvironmentOptions.h` 与 `runtimes/win-x64/WebView2Loader.dll`，取自 NuGet 包 `Microsoft.Web.WebView2`（Microsoft Corporation）。
- **许可证**：**BSD 3-Clause**，全文见 `third_party/webview2/LICENSE.txt`，已按条款保留版权声明与免责条款。
- **分发方式**：头文件仅用于编译；`WebView2Loader.dll`（165,968 字节）**必须与 `Voca.exe` 同目录随 Windows 发布包分发**。运行时本体（`EmbeddedBrowserWebView.dll`）由系统已安装的 **Microsoft Edge WebView2 Runtime** 提供，本仓库不打包、不复制该运行时。
- **依赖说明**：缺少 WebView2 Runtime 时 `Voca.exe` 会退回 `msedge --app` 模式启动，功能不丢失但任务栏图标会重新变软。

---

## 二、受第三方服务条款约束的部分（不构成开源授权）

### 6. 在线词典查询服务（欧路词典、爱词霸、WordReference）
- **调用地址**：
  - 欧路词典：解析与内嵌均用 `https://dict.eudic.net/mdicts/en/@word@`
  - 爱词霸：`https://www.iciba.com/word?w=@word@`
  - WordReference 英汉词典：`https://www.wordreference.com/enzh/@word@`（仅跳转，不在应用内加载）
  - 其中 `@word@` 由客户端 `encodeURIComponent` 编码后替换。
- **授权与边界说明**：
  - Voca **未在代码库或安装包中抓取、缓存或分发**任何一家的词库数据；
  - 仅在用户主动打开「查看词典详细与编辑」弹窗时，由客户端向上述公开地址发起实时请求展示；
  - 返回内容的版权归各平台所有，受其服务条款约束，**不得用于批量爬虫抓取或商业售卖**；
  - 三家均为公开查询页，Voca 不绕过其登录、付费或反爬机制。
- **2026-10-17 真机实测到的服务侧限制（影响功能，非授权问题）**：
  - 欧路 `/dicts/en/` 带 `x-frame-options: SAMEORIGIN` → 内嵌必被浏览器拒绝（`net::ERR_BLOCKED_BY_RESPONSE`），且释义中部分汉字被替换为 `<img>`；改用 `/mdicts/en/`（无该头、带 `access-control-allow-origin: *`、释义完整）后内嵌与解析都可用。
  - 爱词霸无 `X-Frame-Options` 可内嵌，但释义由脚本渲染，服务端 HTML 中无文本可解析 —— 因此 Voca 只显示页面、不声称解析成功。
  - **WordReference 部署 Anubis 人机验证**：首个请求返回 HTTP 418 的 JS 质询页，通过后 200 的词典文档本身**不带** `x-frame-options` 也不带 CSP（带这两个头的是 `favicon.ico` 等静态资源）。但该质询只在**顶层框架**里能完成：嵌进 Voca（`file://` 源）的 iframe 会永远停在验证页，`fetch()` 又因无 CORS 头读不到响应。因此 v1.0.5 由 Voca 自己的原生宿主开一个**顶层 WebView2 词典窗口**加载该页，而不是把用户丢给系统浏览器，也不引入任何第三方代理去绕过验证。
  - 逐条响应头取证与修复细节见 `docs/07_Voca_v1.0.4_在线词典可用性实测与修复报告_20261017.md`。

---

## 三、发布前自查结论

| 检查项 | 结论 |
| :--- | :--- |
| 代码、构建脚本 | MIT，自有，可公开 |
| 词库 `voca.db` | ECDICT MIT，许可全文已随附，可公开 |
| 精编词库 `voca_lexicon.*` | 项目自编，MIT，可公开（原「源自 WordNet」表述已于本次发布更正，项目未使用 WordNet 数据） |
| 字体 WOFF2 子集 | OFL-1.1，许可全文已随附，可随软件捆绑分发 |
| 图标 | 仓库所有者自有，已确认可公开 |
| 在线词典 | 不打包、不分发数据；仅客户端实时访问，受对方服务条款约束 |
| API 密钥 / 令牌 / 个人信息 / 机器专属绝对路径 | 全仓库扫描未发现有效命中：Windows 与 Unix 用户目录绝对路径、GitHub token 前缀、AWS AKIA 前缀、各类私钥块均无匹配（`assets/embedded_assets.json` 中的 `AKIA` 子串来自 Base64 图像数据，`voca_lexicon_payload.json` 中的数字串为词条索引，均非凭据） |
| APK 签名私钥 | **未提交进仓库**：`scripts/build_apk_v103.py` 每次构建在临时目录用 `openssl` 现生成自签证书，构建结束即销毁 |
