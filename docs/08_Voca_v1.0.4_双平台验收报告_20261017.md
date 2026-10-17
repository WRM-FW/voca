# Voca v1.0.4 双平台验收报告与已知限制说明

- **报告日期**：2026-10-17
- **被测版本**：Voca v1.0.4（`state.appVersion = "1.0.4"`，`schemaVersion = 4`，Android `versionCode=5` / `versionName=1.0.4`，EXE `assemblyIdentity` 与 PE `Image Version` = 1.0.4）
- **验收原则**：每项结论都标注「已实测 / 推断 / 未验证」。未实际执行的测试一律写「未验证」并给出原因，不以构建成功或代码改动代替功能验收。

## 一、测试环境

| 项目 | 实测值 |
| :--- | :--- |
| 操作系统 | Windows 11，内部版本 26200，x64，单显示器 150% 缩放（DPI 144） |
| WebView2 Runtime | **155.0.4283.60**（读自注册表 `EdgeUpdate\Clients\{F3017226-…}`） |
| 用于前端验证的浏览器 | Microsoft Edge 155.0.4283.45（headless=new，Chrome DevTools Protocol） |
| 编译器 | MinGW-w64 gcc 8.1.0 / Binutils 2.30（`windres` + `gcc`） |
| Python | 3.11（`build_all.sh` 自动挑选能 `import PIL, fontTools, brotli, cryptography` 的解释器） |
| OpenSSL | 3.5.6（APK v1/v2 签名） |
| Android 设备 | **无**（`adb devices` 为空），Android 端全部为前端级验证 |

## 二、六项需求验收结论

| # | 需求 | 结论 | 依据 |
| :--- | :--- | :--- | :--- |
| 1 | 删除「重置不会度」及全部入口 | **已完成并实测** | 构建产物 `index.html` 中 `cardBtnUnfamReset` / `modalBtnResetUnfam` / `brand-sub` 共 **0** 次出现；不会程度 +1/−1、生词本、复习计划、打卡在真机与 CDP 会话中均正常。 |
| 2 | 在线词典修复 + 显示区自适应 | **已完成并实测**（WordReference 受站点策略限制，只能跳转） | 见第四节与 `docs/07`。 |
| 3 | Windows 首次启动多开 Edge 窗口 | **已完成并实测** | 见第三节。 |
| 4 | Windows 任务栏图标模糊 | **已完成并实测**；本轮另发现并修复两个残留缺陷 | 见第二节。 |
| 5 | 删除左上角「艾宾浩斯双平台背单词工坊」 | **已完成并实测** | 真机截图确认品牌区只剩 logo + `Voca` + `v1.0.4` 徽标，无空档；窗口标题与其他文案未改。 |
| 6 | Android UI 重做 | **前端层已完成并实测；容器层未验证** | 见第五、六节。 |

---

## 三、Windows 原生宿主与图标（含本轮新发现）

`docs/06` 已证明：v1.0.3 的 Edge `--app` 架构下任务栏图标被 Chromium 固定为 16px 后再放大，前端与 `.rsrc` 都改不动，因此 v1.0.4 换成原生 Win32 + WebView2 宿主。本轮在该宿主上又查出并修复了两个**独立**缺陷：

### 3.1 `Voca.exe` 被链接成控制台子系统（已修复并实测）

- **现象**：`Voca.exe` 的 PE `Subsystem` 字段实测为 **3（IMAGE_SUBSYSTEM_WINDOWS_CUI）**。从资源管理器双击会额外出现一个黑色控制台窗口。
- **根因**：`scripts/build_host_v104.py` 传了 `-municode`（入口 `wWinMain`）但没传 `-mwindows`，gcc 因此按控制台子系统链接。
- **修复**：链接参数加入 `-mwindows`。
- **复验**：重编后 `Subsystem = 2（GUI）`，`machine = 0x8664`；窗口枚举脚本在启动后只看到 1 个新窗口，此前那次运行里出现的 `CASCADIA_HOSTING_WINDOW_CLASS` 控制台宿主窗口不再出现。

### 3.2 `ICON_BIG` 从未真正生效（已修复并实测）

- **现象**：外部探针读 `WM_GETICON`，`ICON_SMALL` / `ICON_BIG` / `ICON_SMALL2` **返回同一个 HICON 句柄**，且都是 24×24。也就是说 Alt+Tab 与任务栏预览拿到的是 24px 位图放大后的结果。
- **排查过程**（每一步都有实测数据，不是猜测）：
  1. 用 `LoadImageW` 直接对 `windows/app/voca.ico` 按 16/20/24/32/40/48/64/128/256 逐尺寸加载，全部返回**精确尺寸**的图标 → `.ico` 的 8 帧目录没问题。
  2. 在宿主里加临时探针，实测 `ApplyWindowIcons` 收到的请求尺寸正确（`small_px=24`、`big_px=48`），`hs` 与 `hb` 是**两个不同的非空句柄** → 加载与判空逻辑没问题。
  3. 排除「类图标被提前 `DestroyIcon`」的猜想：四个句柄值互不相同，且移除 `DestroyIcon(wc.hIcon/hIconSm)` 后现象不变。
  4. 在 `CreateWindowExW` **之后**单独设一次 `WM_SETICON(ICON_BIG, 48px)`，回读立刻变成 48 → 说明问题出在写入时机或写入顺序。
  5. 把 `ApplyWindowIcons` 从 `WM_CREATE` 移到 `CreateWindowExW` 返回之后，回读仍是 24；此时三条 `WM_SETICON` 的顺序是 `SMALL → BIG → SMALL2`。
  6. 调整为 `SMALL → SMALL2 → BIG`（即让 `ICON_BIG` 是最后一次写入），回读 `0x1830` = 小 24 / 大 48 → **定位到 `WM_SETICON(ICON_SMALL2)` 在 `ICON_BIG` 之后发送会让两个槽位都落到小图标上**。
- **修复**：`ApplyWindowIcons()` 改为在 `CreateWindowExW` 返回后调用（`WM_DPICHANGED` 时重设），并把 `ICON_BIG` 放在最后一条 `WM_SETICON`。
- **复验（以实际显示效果为验收依据）**：从运行中的窗口取回三个图标句柄并逐像素比对源帧：

| 槽位 | 实测尺寸 | 与源帧比对 |
| :--- | :--- | :--- |
| `ICON_SMALL` | 24×24 | 与 `assets/icons/icon_24.png` **逐像素相同**（mean channel delta `0.0000`） |
| `ICON_SMALL2` | 24×24 | 同上，`0.0000` |
| `ICON_BIG` | 48×48 | 与 `assets/icons/icon_48.png` **逐像素相同**，`0.0000` |

  修复前三者都是 24×24。

### 3.3 其他宿主侧确认

- `windows/Voca.exe` 内嵌的 8 帧 `RT_ICON` 与 `windows/voca.ico` 的 8 帧**逐字节相同**（帧 sha256 集合完全一致，无缺帧无多余帧）。
- 窗口类名 `Voca.MainWindow`，标题 `Voca v1.0.4 — 离线艾宾浩斯背单词工坊 (Windows & Android)`，`PerMonitorV2` + `asInvoker`。
- 宿主自检日志改为**默认关闭**：仅当环境变量 `VOCA_TRACE` 存在时才写 `windows/host_trace.log`。实测不带该变量运行一次后，日志文件的大小与修改时间均未变化。崩溃日志独立为 `voca_crash.log`，始终保留。

---

## 四、首次启动窗口计数（需求 3）

方法：启动前后各枚举一次全部可见顶层窗口，取差集。用 `VOCA_UDF` 环境变量把用户数据目录指向一个**全新空目录**来复现真正的首次启动。

| 场景 | 新增可见窗口 | 结论 |
| :--- | :--- | :--- |
| v1.0.4 原生宿主 + 全新数据目录（首次启动） | `Voca.MainWindow` × 1，**额外浏览器窗口 0** | 通过 |
| v1.0.4 原生宿主 + 已有数据目录（后续启动） | 同上 | 通过 |

**正常行为与异常行为的区分**：v1.0.3 多开的那个窗口标题是 `正在加载扩展... 和另外 2 个页面` / `感谢您安装 AdGuard！`，属于 Edge 自身的首次运行扩展安装与同步推广流程，与 Voca 的学习功能无关（详见 `docs/05`）。v1.0.4 在 WebView2 模式下**根本不启动外部浏览器进程窗口**，因此该异常从架构上不再可能出现；`--no-first-run --no-default-browser-check --disable-extensions --disable-sync` 这组参数现在只在「WebView2 缺失 → 退回 Edge/Chrome 兼容模式」这条路径上仍然生效。

**未验证**：WebView2 Runtime 完全缺失的机器上的兼容模式实测（本机装有 Runtime，无法在不卸载系统组件的前提下复现；卸载属于影响共享环境的操作，未执行）。

---

## 五、在线词典与 Android 端功能

### 5.1 在线词典（真实站点、真实查询）

在最终构建产物上重跑，全部为真实网络请求：

| 词典 | 词条 | 状态横幅 | 内嵌框 | 判定 |
| :--- | :--- | :--- | :--- | :--- |
| 欧路词典 | `area` | `✓ 已获取【欧路词典】中"area"的词典释义，并在下方内嵌原站词典页`（`dict-status-ok`） | `display:block` | 通过 |
| 爱词霸 | `area` | `ℹ 已内嵌【爱词霸英汉词典】词条页面（该站释义由脚本渲染，Voca 不抓取其文本）`（`dict-status-info`） | `display:block` | 通过（如实标注为 info，不冒充已解析） |
| WordReference | `area` | `⚠ 【WordReference 英汉词典】无法在 Voca 窗口内显示，仅能跳转到源站`（`dict-status-warn`） | `display:none` | 通过（站点策略所致，非缺陷伪装） |
| 任意 | 断网（`navigator.onLine=false`） | `⚠️ 未能获取【欧路词典】在线内容：当前设备处于离线状态…`（`dict-status-error`） | `none` | 通过 |

四种异常态用注入的 fetcher 钩子做确定性验证（`window.__VOCA_ONLINE_DICT_FETCHER__`），确认「空白页」与「404」不会被记为成功：

| 注入结果 | 状态 | 文案 | 内嵌框 |
| :--- | :--- | :--- | :--- |
| `{ok:true, status:404}` | `warn` | `⚠️ 词条不存在：【欧路词典】未收录单词"area"` | `none` |
| `{ok:false, error:'模拟断网'}` | `error` | `⚠️ 未能获取【欧路词典】在线内容：模拟断网` | `none` |
| 含 `#FCchild` 的真实结构 | `ok` | `✓ 已获取…` | `block` |
| `{ok:true, status:200, html:空白页}` | `info` | `ℹ 已内嵌…（该站释义由脚本渲染，Voca 不抓取其文本）` | `block` |

显示区自适应（窗口尺寸变化时不截断、不溢出、不留无谓空白）：

| 视口 | 内嵌框高 | 释义区高 | 弹窗高 | 是否贴合视口 | 横向溢出 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1600×1000 | 460 | 80 | 900（top 50 / bottom 950） | 是 | 0 |
| 1280×800 | 368 | 80 | 720（40 / 760） | 是 | 0 |
| 1024×700 | 322 | 80 | 630（35 / 665） | 是 | 0 |
| 820×620 | 285 | 80 | 558（31 / 589） | 是 | 0 |

**未验证**：`eudic/abandon` 这一条在本轮探针中返回 `no row for abandon` —— 探针只在当前 List（CET-4 List 1，257 词）里找行，`abandon` 不在其中。这是**测试脚本的取词范围限制，不是产品缺陷**；`docs/07` 记录的 8 个真实词条（含 GRE 词）解析结果仍然有效。

### 5.2 Android 触屏视口验收（真实 Chromium + CDP）

外壳由能力探测选择，不靠 UA 猜。9 个视口全部实测：

| 视口 | `data-ui` | 侧栏 | 底部导航 | 横向溢出 | 启动渲染 | JS 错误 | 可交互控件 | <44px 控件 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 320×568 | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 360×640 | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 390×844 | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 412×915 | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 844×390（横屏） | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 740×360（横屏） | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 768×1024（平板） | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 1024×768（平板横屏） | mobile | none | grid | 0 | 正常 | 0 | 500 | **0** |
| 1600×950（桌面） | desktop | flex | none | 0 | 正常 | 0 | 494 | 374（桌面外壳用鼠标指针，34px 图标按钮属正常） |

统计：6 个页签全部可达；统计卡在 ≤360px 为单列（首卡宽度占容器 100%）、手机竖屏双列、平板/横屏三列；`.d-only` 键盘快捷键说明在触屏下隐藏 3 行、桌面下显示 4 行；`.m-only` 在触屏下显示 13 处、桌面下 0 处。

点击规则提示文案随外壳切换（不再是手机上写着"右键"）：

- 触屏：`轻触单词行：不会程度+1并发音 · 长按：不会程度-1`
- 桌面：`左键/轻触单词行：不会程度+1并发音 · 右键点击：不会程度-1`

**未验证**：长按 480ms 手势在真实手指按压下的手感与误触率、`document.execCommand('copy')` 在 Android WebView 中的成功率（headless Chromium 无窗口焦点时返回 false，见 5.3）。

### 5.3 Android 导出与恢复（触屏外壳内的替代通路）

| 操作 | 实测结果 |
| :--- | :--- |
| 导出完整学习备份 `.json` | 复制框显示，文件名 `voca_backup_v1.0.4_2026-10-17.json`，内容 **682,961 字符**，提示 `已生成 完整学习备份，请在「导出内容」框复制保存` |
| 导出词库 CSV | 复制框显示 `voca_cet4_export.csv`，257,560 字符 |
| 点「复制到剪贴板」 | headless 环境返回 `复制失败，请长按文本框手动全选`（`file://` 非安全上下文，`navigator.clipboard` 不存在，`execCommand('copy')` 在无焦点时失败）。**真机行为未验证**，但已提供手动全选兜底且提示语如实。 |
| 导出 PDF | 明确拒绝：`Android 版无法保存该文件，请在 Windows 版导出…`；PDF 本体生成正常（9 页 / 2,846,578 字节），只是不落盘 |
| 导出独立 HTML | 同样明确拒绝，不再谎报成功 |
| 粘贴恢复 | 把导出的 682,961 字符备份贴进恢复框 → `✓ 学习数据备份已完整恢复（来自粘贴内容）`，`planCycleDays` 由人为改坏的 77 回到备份里的 30，`planListCount` 由 9 回到 15，`schema=4`、`appVersion=1.0.4` |

**根因说明**：发布 APK 的 `classes.dex` 由 `scripts/build_apk_v103.py` 手写 Dalvik 字节码生成，只含 `MainActivity` 的 `<init>` / `onCreate` / `onBackPressed` 三个方法；`src/android/.../MainActivity.java` 是 Gradle 侧的参考壳层，**改它不会改变 APK**。因此 v1.0.4 在网页侧补齐了通路，并在 `MainActivity.java` 顶部以注释写明这四项容器缺口（文件选择器、下载监听、打印、安全区），避免读者误以为已经实现。

---

## 六、构建、产物完整性与数据兼容

### 6.1 一键构建

`bash scripts/build_all.sh` 全程通过：前端组装 → 签名 APK → 原生 WebView2 宿主 → APK 深度校验（AXML / ARSC / DEX / v1 JAR / v2 Merkle + RSA-SHA256 全部验证通过）。

### 6.2 产物清单（2026-10-17 最终构建）

| 文件 | 字节 | SHA-256（前 24 位） |
| :--- | ---: | :--- |
| `windows/app/index.html` | 4,253,569 | `c624adc24c908b443ae954c4` |
| `src/webapp/index.html` | 4,253,569 | `c624adc24c908b443ae954c4`（与上**逐字节相同**） |
| `src/android/app/src/main/assets/index.html` | 4,253,569 | `c624adc24c908b443ae954c4`（同上） |
| APK 内 `assets/index.html` | 4,253,569 | `c624adc24c908b443ae954c4`（**从 APK 里解出来再哈希，与 Windows 侧完全一致**） |
| `windows/Voca.exe` | 218,112 | `b1240d4856d30d3cc94ae815`（PE32+ x86_64，GUI 子系统） |
| `windows/WebView2Loader.dll` | 165,968 | `462b36fd1be6ca9f7563466a`（必须与 `Voca.exe` 同目录） |
| `windows/voca.ico` | 178,404 | `7a30cd86e9c7883e8a48335e`（8 帧，与 EXE 内嵌帧逐字节相同） |
| `android/Voca_v1.0.4_release.apk` | 3,507,805 | `6e2823167ec8dda8aece9a03` |

APK 载荷共 11 个条目：`AndroidManifest.xml`、`resources.arsc`、`classes.dex`、`res/drawable/ic_launcher.png`、`assets/index.html`、3 个 WOFF2 字体、`META-INF/{MANIFEST.MF,CERT.SF,CERT.RSA}`。

### 6.2.1 Release 资产下载往返校验（已执行）

从 GitHub Release 把三个资产重新下载回本地并逐个比对：

- 三个资产文件（`Voca_v1.0.4_Windows_x64.zip`、`Voca_v1.0.4_release.apk`、`Voca_v1.0.4_source.zip`）下载回来的 **SHA-256 与上传前逐一相同**。
- 下载包内部件再比对（这些值与文档内容无关，因此可长期引用）：

| 下载包内文件 | SHA-256（前 24 位） | 结论 |
| :--- | :--- | :--- |
| `Voca_v1.0.4_Windows_x64.zip` → `Voca.exe` | `b1240d4856d30d3cc94ae815` | = 真机跑过启动、图标像素比对与词典实测的那个二进制 |
| 同上 → `WebView2Loader.dll` | `462b36fd1be6ca9f7563466a` | 与构建产物一致 |
| 同上 → `windows/app/index.html` | `c624adc24c908b443ae954c4` | 与构建产物一致 |
| 同上 → `windows/voca.ico` | `7a30cd86e9c7883e8a48335e` | 与构建产物一致 |
| `Voca_v1.0.4_release.apk` → `assets/index.html` | `c624adc24c908b443ae954c4` | **与 Windows 侧逐字节相同** |
| `Voca_v1.0.4_source.zip` | 91 个条目 | 与 `v1.0.4` 标签的 git 树文件数一致，不含编译产物 |

即：**发布出去的 Windows 可执行文件就是本次实测的那一个**，不是重新构建的近似品。（ZIP 自身的哈希会随 `docs/` 内容变动，故不在此固定其字面值。）

**APK 的 SHA-256 不是稳定值**：签名证书每次构建在临时目录现生成后即销毁。本轮实测两次连续构建：条目列表相同（11 项），**唯一有差异的条目是 `META-INF/CERT.RSA`**，其余 10 项（含 `classes.dex` 与 `assets/index.html`）逐字节相同。字节数随证书 DER 长度在 3,507,805 / 3,507,806 之间浮动。除 APK 外，`index.html`、`Voca.exe`、`WebView2Loader.dll`、`voca.ico` 的哈希在两次完整构建之间完全复现。

### 6.3 v1.0.3 → v1.0.4 数据兼容

- **存档结构未变**：`schemaVersion` 仍为 `4`，未新增/删除/改名任何持久化字段，v1.0.3 存档直接读取，v1.0.0~v1.0.2 走既有 v3→v4 迁移器。
- **删除「重置不会度」不动数据**：只删按钮与事件处理，`records[*].unfam` 的读写路径完全保留。
- **Windows 换宿主带来的路径变化**：旧 Edge 外壳写 `data/profile/Default/`，WebView2 读 `data/profile/EBWebView/Default/`。宿主启动时把 `Default/Local Storage` 与 `Default/IndexedDB` 镜像到 `EBWebView/Default/` 下，用 `Voca.migrated` 哨兵文件保证幂等。
- **实测**：v1.0.3 形状的存档在 v1.0.4 原生宿主中启动后，进度、生词本、自定义释义、笔记、计划参数、主题全部原样读回；v1.0.2 存档的迁移项（`mastery` 剥离、`en_en`→`bilingual`、`mastery_asc`→`hard_first`、`mastery_lr`→`unfam_lr`）逐项正确。

---

## 七、未验证清单（不得当作已通过）

| 项目 | 状态 | 原因 |
| :--- | :--- | :--- |
| Android 真机/模拟器上的安装、启动、渲染、返回键、发音、剪贴板 | **未验证** | 环境内无任何 Android 设备（`adb devices` 为空），也无模拟器。 |
| 100% / 125% / 175% / 200% / 225% / 250% 缩放与多屏混合 DPI 下的图标观感 | **未验证** | 本机只有一块 150% 显示器；改系统缩放或插多屏属于影响用户桌面环境的操作，未执行。逻辑上 `WM_DPICHANGED` 会重新取帧，但只有 150% 有像素级证据。 |
| WebView2 Runtime 缺失时的兼容模式（提示框 + 退回 Edge/Chrome） | **未验证** | 需要卸载系统组件，未执行。 |
| 发音听感、TTS 音色 | **未验证** | 无音频采集手段。 |
| Linux 下的一键构建 | **未验证** | 本轮全程在 Windows Git Bash 执行。 |
| `VOCA_BUILD_ASSETS=1` 资产重生成 | **未验证（且已知会退化）** | 需要上游 OTF/TTC 源；且 `assets/icons/master_icon.png` 只有 512px，重裁会让 16/20/24px 小帧变糊。 |
| `scripts/run_e2e_v103.py` Selenium 端到端 | **未运行** | 本轮改用 Node 内置 WebSocket 直连 CDP，未安装 WebDriver。 |

---

## 八、遗留问题（与 `README.md` 第七节一致）

1. WordReference 无法内嵌或抓取（站点 `frame-ancestors` 白名单 + 无 CORS 头），只保留一键跳转。
2. 弹窗没有 `Esc` 关闭。
3. Android 容器层缺 `DownloadListener` / `onShowFileChooser` / 打印通道 / 安全区，PDF 与独立 HTML 导出在 Android 上不可用。
4. APK 签名密钥每次构建临时生成，自重建的 APK 无法覆盖安装。
5. `targetSdkVersion=28` 偏低。
6. `voca.db` 音标沿用 ECDICT 标注体系，非严格 IPA。
7. 新增运行时依赖：Microsoft Edge WebView2 Runtime。
