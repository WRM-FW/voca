# Changelog

All notable changes to the **Voca** project are documented in this file.

## [1.0.4] - 2026-10-17

### Added
- **Native Windows host (`src/windows/voca_host.c`)**: Voca.exe is now a real Win32 window hosting an embedded WebView2 control instead of a launcher that opens `msedge.exe --app=...`. Built by `scripts/build_host_v104.py` (gcc + windres) from `src/windows/voca_host.rc` / `voca_host.exe.manifest`. The host declares `PerMonitorV2`, sets its own `AppUserModelID` (`Voca.Offline.WordTrainer.v1`), and **re-picks the icon frame for the current DPI on `WM_DPICHANGED`**. If the WebView2 runtime is missing it falls back to the old Edge launch and says why.
- **Third online dictionary source: 爱词霸 (`iciba.com`)** — selectable in Settings and in the dictionary modal, and embeddable inside the app window.
- **DPI-exact favicon ladder**: `<link rel="icon">` now declares 16/20/24/28/32/36/40/48/64/128/192/256 so any shell that *does* honour favicons gets a native-size bitmap.
- **Android/touch UI rebuilt as a separate shell.** `<head>` runs a capability probe (`(pointer: coarse)`, `(hover: none)`, UA + viewport width) and toggles `html.ui-mobile` / `html.ui-desktop`. The touch shell gets a fixed 6-item bottom navigation, per-view headings instead of the desktop header, a 2-column stat grid (1 column at ≤360px, 3 on tablet/landscape), viewport-relative modals, safe-area insets, `100dvh`, and `@media (hover: hover) and (pointer: fine)` guards around every hover-only affordance. The desktop presentation is unchanged.
- **Long-press word row = 不会程度 −1** on touch (`LONG_PRESS_MS = 480`, `LONG_PRESS_SLOP = 12` px, with a build-up highlight and a click-suppression window so the tap that follows a released hold cannot double-fire). This replaces the right-click gesture a finger cannot perform.
- **Touch export copy-out and paste restore.** The shipped WebView shell has no `DownloadListener`/`onShowFileChooser`, so on the touch shell a `.json` backup or word-list CSV is mirrored into a "导出内容" box with a copy button, and restoring accepts pasted backup text. PDF and standalone-HTML exports now state plainly that they cannot be saved on Android instead of reporting success.
- `docs/06` root-cause report for the taskbar icon; `docs/07` online-dictionary capability report; `docs/08` v1.0.4 dual-platform test report.

### Fixed
- **Windows taskbar icon blur — actually fixed this time.** v1.0.3's 8-frame `.rsrc`/`.ico` work could not have helped: in `msedge --app` mode Chromium owns the window icon and pins it to 16x16 before the shell scales it, so at 150% the taskbar drew an upscaled 16px bitmap. Measured across 16 variants (declaring 20/24/28/36/40, declaring only 24, declaring nothing, reordering `<link>`s, `--app-user-model-id` + a Start-Menu `.lnk` with `IconLocation`) every one produced the *same* 16-upsampled bitmap. The native host loads the exact size the shell asks for straight from `voca.ico`; the live `ICON_SMALL` is now **pixel-identical** to `assets/icons/icon_24.png` (mean channel delta `0.00`, was `12.94`). See `docs/06`.
- **Extra Edge browser window on first launch.** Root cause measured: the portable profile triggered machine-level Edge extensions to install into it and open their welcome pages in a full tabbed window (title literally `正在加载扩展... 和另外 2 个页面` / `感谢您安装 AdGuard！`), plus an Edge sync-promotion popup. The host now passes `--no-first-run --no-default-browser-check --disable-extensions --disable-sync` (and no longer needs a browser at all in WebView2 mode); visible browser windows on a fresh first launch went from **2 to 1**.
- **Online dictionary false success reporting removed.** The `mode:"no-cors"` reachability probe treated any HTTP error as success (opaque responses expose no status), so WordReference's `403 Forbidden` was shown under a green "✓ 已连接" banner and Eudic's blocked iframe under a green "✓ 已成功获取". Every failure path now reports `error`/`warn`/`info` honestly. See `docs/07`.
- **Eudic dictionary now actually works.** `/dicts/en/` sends `x-frame-options: SAMEORIGIN` (iframe always blocked) and replaces some Chinese characters in the gloss with `<img>` tags; switched to `/mdicts/en/`, which has no framing header, sends `access-control-allow-origin: *`, and carries the complete gloss.
- **Eudic parser never matched.** It queried `#ExpFCChild`; the real container is `#FCchild` (and `#SPECchild`), and `querySelector` is case-sensitive — so the panel had silently degraded to the `<meta name="description">` boilerplate for every word. Verified fixed on 8 real headwords across CET-4 and GRE.
- **Dictionary area sizing.** `.dict-iframe-wrap` `310px` → `clamp(240px, 46vh, 660px)`, `.dict-parsed-entries` `240px` → `clamp(104px, 22vh, 300px)`, `.modal-panel` `90vh` → `min(90vh, calc(100dvh - 24px))`, plus `overscroll-behavior: contain`. Verified to fit the viewport with zero horizontal overflow at 1600x1000 / 1280x800 / 1024x700 / 820x620.
- `WordReference` now states plainly that the site's `frame-ancestors` allowlist forbids embedding and offers one-click navigation to the source page, instead of showing a dead frame.
- **Desktop-only wording no longer leaks onto phones.** The click-rule hint, the auto-scroll hint and the shortcut list are now shell-aware (`.d-only` / `.m-only`): the touch shell says 轻触/长按 and drops the Space / J-K / 1-2-3 keyboard rows. The narrow 320px and 360px widths now render one stat card per row instead of wrapping labels mid-word.
- **`Voca.exe` was linked as a *console* subsystem binary** (PE `Subsystem` = 3), so double-clicking it also opened a black console window. `scripts/build_host_v104.py` passed `-municode` but not `-mwindows`; it now passes both and the shipped binary reports `Subsystem` = 2 (GUI).
- **`ICON_BIG` never took effect**, so Alt+Tab and the taskbar preview drew an upscaled 24px bitmap. Two causes stacked: `ApplyWindowIcons()` ran inside `WM_CREATE` (still inside `CreateWindowExW`, where the class-icon initialisation undoes it), and `WM_SETICON(ICON_SMALL2)` was sent *after* `ICON_BIG`, which makes `DefWindowProc` point the big slot at the small icon too. Icons are now applied after the window exists with `ICON_BIG` written last; live readback at 150% is `ICON_SMALL`/`ICON_SMALL2` = 24×24 and `ICON_BIG` = 48×48, each **pixel-identical** to its source frame (mean channel delta `0.0000`). See `docs/06` §8.

### Removed
- **「重置不会度」**: both buttons (`#cardBtnUnfamReset`, `#modalBtnResetUnfam`) and their handlers are gone. Left-click +1 / right-click −1, the immersive-card ±1 controls and the modal ±1 controls are unchanged, and no stored `unfam` value is affected.
- The top-left **`艾宾浩斯双平台背单词工坊`** subtitle (`.brand-sub`) is deleted; the brand block collapses to the logo + version badge with no leftover gap, and no other app name, window title or feature copy was touched.

### Changed
- Version stamped `1.0.4` throughout: HTML `<title>` and sidebar badge, `state.appVersion`, PDF/HTML export headers and filenames, backup filename, `AndroidManifest.xml` (`versionCode=5`, `versionName="1.0.4"`), `build.gradle`, APK signer `Created-By`, EXE `assemblyIdentity` and `Image Version`.
- **`schemaVersion` stays at `4`.** No persisted field was added, removed or renamed, so v1.0.0–v1.0.3 archives load unchanged; verified end-to-end by writing a v1.0.3-shaped archive through the old Edge shell, closing it, and reading every field back in the native host.
- Windows build: `build_all.sh` now compiles the native host and stages `WebView2Loader.dll` beside `Voca.exe`; falls back to the legacy launcher if no C toolchain is present.
- Build reproducibility: `build_all.sh` probes for a Python that can actually import the build deps (on Windows `python3` is usually the Microsoft Store alias, a *different* interpreter from `python`), and passes paths to the builders via environment variables instead of interpolating shell paths into Python source.
- The host's step-by-step trace log is now **opt-in**: `windows/host_trace.log` is only written when the `VOCA_TRACE` environment variable is set, so a portable app no longer drops a file next to itself on every run. Crash reporting keeps its own always-on `windows/voca_crash.log`.

### Known Issues (1.0.4)
1. WordReference content still cannot be shown inside Voca — only via one-click navigation. This is the site's own `frame-ancestors` allowlist plus absent CORS headers.
2. New runtime dependency: Microsoft Edge WebView2 Runtime (preinstalled on Windows 11 and Windows 10 2004+). Without it Voca falls back to an external browser window and the taskbar icon goes soft again.
3. Android APK is still unverified on any real device or emulator; `targetSdkVersion=28`; signing key is regenerated per build so self-rebuilt APKs cannot upgrade-install over the released one.
4. The Android shell has no `DownloadListener`, `onShowFileChooser`, print channel or edge-to-edge insets. Note that `src/android/.../MainActivity.java` is a *reference* shell: the released `classes.dex` is hand-assembled by `scripts/build_apk_v103.py`, so editing that Java file does not change the APK.
5. Dictionary modal has no `Esc`-to-close.
6. `voca.db` phonetics follow ECDICT's notation, not strict IPA.
7. Icon/DPI verification covers 150% on a single monitor only; 100%/125%/175%/200%/225%/250% and mixed-DPI multi-monitor are untested.
8. `VOCA_BUILD_ASSETS=1` degrades the small icon frames, because `assets/icons/master_icon.png` is a 512px derivative rather than a 2048px master.

---

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
