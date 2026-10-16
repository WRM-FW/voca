# Changelog

All notable changes to the **Voca** project are documented in this file.

## [1.0.3] - 2026-10-17

### Fixed
- **Windows Taskbar & High-DPI Icon Blurriness**: Replaced single-size 64x64 favicon and 2-frame PNG `.rsrc` with an 8-frame Win32-compliant icon resource table (`256x256` PNG + `128/64/48/40/32/24/16` 32-bit BGRA `BITMAPINFOHEADER` DIB frames + 1-bit AND masks), added `PerMonitorV2` High-DPI manifest (`RT_MANIFEST`), added `--high-dpi-support=1` launch flag, and declared multi-size `<link rel="icon">` tags (`256x256` down to `16x16`) in `index.html`.

### Changed
- **Word State Management**: Removed "掌握度" (`mastery`) UI badges, buttons, sort option (`mastery_asc`), CSV/PDF columns, and state fields; retained and streamlined "不会程度" (`unfam`, 0..5) via left-click (+1), right-click (-1), immersive card buttons, and dictionary modal controls.
- **Dictionary Detail & Edit Modal (`#dictModal`)**: Removed the legacy "英英释义与同义词拓展" and "双语语境例句与助记" sections; integrated live lookup for **欧路词典 (`dict.eudic.net`)** and **WordReference 英汉词典 (`wordreference.com`)** with proper `@word@` URL encoding and honest offline/error/not-found feedback.
- **Online Dictionary Setting**: Added persistent online dictionary selector (`#settingOnlineDict`) in Settings, synced with `#dictModal` and preserved across restarts.
- **Repository Structure**: Organized full repository with `LICENSE`, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `requirements.txt`, `.gitignore`, and relative-path build scripts for GitHub open-source release readiness.

### Removed
- **English-English Mode (`en_en`)**: Removed the "英英模式" toolbar button, keyboard shortcut `4`, and rendering branches; legacy `en_en` state automatically migrates to `bilingual`.

### Documentation, Compliance & Build Reproducibility (发布前真机复验后的更正，2026-10-17)
- **新增 `docs/05_Voca_v1.0.3_Windows宿主机真机复验报告_20261017.md`**：在真实 Windows 11 (26200) / 150% 缩放 / Edge 155 上完成 11 项 Windows 复验（启动、可移植 profile、标题栏 16px 图标、PE `.rsrc` 8 帧与 `RT_GROUP_ICON` 一致性、零脚本报错、三档视口无溢出、不会程度加减、真实刷新持久化、v1.0.2 存档迁移、词库与备份入口）与逐字节复现构建比对；Android 侧仅 `apksigner` + `aapt2` 结构校验通过，**安装与运行标记为未验证**（无可用设备）。
- **更正在线词典状态描述**：真机实测欧路词典带 `x-frame-options: SAMEORIGIN`（内嵌 `<iframe>` 被拒，仅文本释义解析可用）、WordReference 返回 `403/418` 却被判为绿色「已连接」。原「绝不将空白页或失败状态伪装为正常查询结果」的表述已在 README 与 `docs/04` 更正为已知问题；**本版本未修改代码**。
- **更正精编词库来源声明**：`voca_lexicon.json` / `voca_lexicon.db` 的 233 条英文释义、同义词、例句与助记为**项目自编**，原 `THIRD_PARTY_NOTICES.md` 中「释义源自 Princeton WordNet 3.1」的表述已删除，项目未使用 WordNet 数据。
- **图标授权确认**：`assets/icons/`、`voca.ico`、`ic_launcher.png` 的著作权与再分发授权已由仓库所有者确认，`THIRD_PARTY_NOTICES.md` 与 `docs/03` 相应从「待确认」改为已确认。
- **构建可复现性修复**：`build_all.sh` 第 1 步（图标/字体重生成）改为 `VOCA_BUILD_ASSETS=1` 显式开启，避免在非 Debian 系环境因硬编码 `/usr/share/fonts/opentype/...` 直接失败；第 3/4 步改为通过环境变量传路径，修掉 MSYS/Git Bash 下 `/d/...` 被 Windows Python 解析成 `D:\d\...` 而静默写错位置的问题；`make_html_v103_part3.py` 固定 `newline="\n"`，消除 Windows 下重建产物多出的 10,716 字节 CRLF 差异。
- **`requirements.txt` 补 `cryptography`**：`scripts/verify_apk_deep.py` 依赖它但原先未声明。
- **`CONTRIBUTING.md` 更正构建事实**：说明发布用 `Voca.exe`/APK 由 `scripts/` 下的纯 Python 构建器生成，`src/windows/voca_launcher.c` 与 `src/android/.../build.gradle` 是参考实现。
- **仓库形态调整**：`windows/Voca.exe` 与 `android/*.apk` 加入 `.gitignore`，二进制产物改为只随 GitHub Release 分发。

### Known Issues (1.0.3，按影响排序)
1. 在线词典内嵌视图在两个词典源上都不可用（详见 README 第七节第 1 条）。
2. WordReference 查询失败时误报绿色「已连接」。
3. APK 签名密钥每次构建临时生成，自行重建的 APK 与 Release 版签名不一致，覆盖安装报冲突。
4. 词典弹窗 `Esc` 快捷键不生效（「✕ 关闭」按钮可用）。
5. `targetSdkVersion=28` 偏低，Android 13+ 侧载有系统风险提示。
6. `voca.db` 音标沿用 ECDICT 标注体系，非严格 IPA。
7. 未覆盖验证：100%/125%/200%/250% 缩放与多屏混合 DPI、发音听感、未收录词 404 路径真机复测、Android 全部运行时行为。

---

## [1.0.2] - 2026-10-16

### Added
- Free-form Ebbinghaus schedule customization supporting arbitrary List count ($N$) and study cycle days ($D$).
- Direct offline multi-page A4 `.pdf` binary exporter alongside multi-page `@media print` and standalone `.html` export.
- Embedded cross-platform WOFF2 font subsets (`Inter` + `Noto Sans CJK SC`) for unified Windows and Android typography.

### Changed
- Docked "偏好设置与帮助" at the bottom of the Windows left sidebar and configured default maximized window startup.
- Redesigned Android portrait (`<= 900px`) layout with 2x2 stats grid, ergonomic word cards, and single-row 5-card spelling buttons.
- Updated application icon to the rounded-rectangle V+Book design.

---

## [1.0.1] - 2026-10-16

### Added
- Integrated the 38,855-entry built-in vocabulary database (`voca.db` covering 8 exam books: 中考/高考/四级/六级/考研/托福/雅思/GRE).
- Added data storage path and cross-platform migration documentation in the Data view.

### Fixed
- Fixed Android APK `ResXMLTree_attrExt` 20-byte alignment, `Activity.requestWindowFeature` lifecycle order, and APK Signature Scheme v2 Merkle tree digest.
- Fixed immersive card click-to-peek and pronunciation behavior.

---

## [1.0.0] - 2026-10-16

### Added
- Initial dual-platform offline release of Voca for Windows (`Voca.exe`) and Android (`Voca.apk`).
