# 第三方资源、字体、词库与品牌资产授权核查清单 (THIRD_PARTY_NOTICES)

本文件对 Voca v1.0.3 仓库中包含的自有代码、构建产物、内置词库、内嵌字体、应用图标及外部在线服务逐项区分，说明其许可证状态与公开边界。

各项结论的核查方式（二进制解析、逐文件比对、真机实测）见 `docs/05_Voca_v1.0.3_Windows宿主机真机复验报告_20261017.md`。

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

## 二、受第三方服务条款约束的部分（不构成开源授权）

### 5. 在线词典查询服务（欧路词典 & WordReference 英汉词典）
- **调用地址**：
  - 欧路词典：`https://dict.eudic.net/dicts/en/@word@`
  - WordReference 英汉词典：`https://www.wordreference.com/enzh/@word@`
- **授权与边界说明**：
  - Voca **未在代码库或安装包中抓取、打包或分发**欧路词典或 WordReference 的任何受版权保护词库数据；
  - 软件仅在用户主动打开「查看词典详细与编辑」弹窗时，由客户端向上述公开网页地址发起实时查询展示；
  - 在线词典返回的网页内容、词条释义与例句版权分别归属于 **欧路软件 (Eudic.net)** 与 **WordReference.com LLC**，受其各自网站服务条款约束，不得用于批量爬虫抓取或商业售卖。
- **2026-10-17 真机实测到的服务侧限制（影响功能，非授权问题）**：
  - 欧路词典返回 `x-frame-options: SAMEORIGIN`，浏览器会拒绝把该页面渲染进 Voca 的内嵌 `<iframe>`（实测 `net::ERR_BLOCKED_BY_RESPONSE`）；同时该站点响应头带 `access-control-allow-origin: *`，因此 Voca 通过 `fetch` 解析出的**文本释义可正常显示**，只有内嵌视图不可用。
  - WordReference 对本机请求返回 **HTTP 418（curl）/ 403 Forbidden（浏览器内嵌框）**，属站点反爬策略；Voca 当前的状态检测把这种被拦截的连接报成绿色「已连接」横幅，属**已知缺陷**，详见 `README.md` 第七节与 `docs/05`。

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
