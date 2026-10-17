# Voca v1.0.4 任务栏图标根因定位与修复报告（20261017）

本报告记录 v1.0.4 如何**彻底**解决 Windows 任务栏图标模糊，以及为什么 v1.0.3 的修复方向注定无效。全部结论来自真机测量，不是推断。

## 一、复验环境

Windows 11 内部版本 26200 / x64 / 单屏 2560x1600 @ **150% 缩放**（逻辑 1707x1067）；`Edg/155.0.4283.45`；WebView2 Runtime `155.0.4283.60`；MinGW-w64 gcc 8.1.0（GNU Binutils 2.30）。

测量手段：Win32 `WM_GETICON` 取出窗口实际交给任务栏的 HICON，用 `GetIconInfo` + `GetObject` 读出位图真实像素尺寸，再 `Icon.ToBitmap()` 导出为 PNG 与仓库资产逐像素比对。

## 二、v1.0.3 的修复为什么无效

v1.0.3 把力气全花在**图标文件**上：8 帧 `voca.ico`、`Voca.exe` 的 `.rsrc`（`RT_ICON` ID 1..8 + `RT_GROUP_ICON` 8 条目录项）、`PerMonitorV2` 清单。

本次先用 PE 解析器逐条核对，确认这些资源**本身完全正确**：

```
RT_ICON: 8 frames -> 256(PNG) 128 64 48 40 32 24 16，全部 32bpp BITMAPINFOHEADER
RT_GROUP_ICON id=1 reserved=0 type=1 count=8   (6 + 8*14 = 118 字节，目录项完整)
  每条的 size / nID 与实际 RT_ICON 载荷逐条一致，无悬空 ID
8 帧 sha256 与 windows/voca.ico 的 8 帧完全相同
```

然后测量真机窗口实际使用的图标：

```
ICON_SMALL (which=0) = 24x24      ICON_BIG (which=1) = 48x48
```

把这张 24x24 与仓库资产比对：

| 比较对象 | 平均通道差 |
| :--- | ---: |
| `assets/icons/icon_24.png`（我们手工调优的 24 帧） | **12.94** |
| `assets/icons/icon_16.png` 放大到 24 | **2.47** |

**结论：任务栏用的是 16px 帧放大出来的图，`.rsrc` 里那张正确的 24 帧根本没被用到。**

原因：`Voca.exe` 只是一个把 `msedge.exe --app=<index.html>` 拉起来的启动器。在 Edge 应用窗口模式下，**窗口图标归 Chromium 管**，Chromium 从页面 favicon 取图并**固定先压成 16×16** 再交给 shell；Windows 按 DPI 把它放大到 24px（150%）。exe 自己的 `.rsrc` 图标只影响资源管理器里的文件图标，不影响任务栏按钮。

## 三、穷尽验证：改 HTML 也救不了

为排除"是不是我们 favicon 声明得不对"，做了 **16 个变体**，每个都真机启动 Edge、取回 `ICON_SMALL`、比对像素：

| 变体 | 声明内容 | 结果 |
| :--- | :--- | :--- |
| a_16_last | 256…16（16 在最后） | 24x24，等于 16 放大 |
| b_16_first | 16 在最前 | **同上，位图 sha 完全相同** |
| c_no16 | 删掉 16x16 声明 | **同上** |
| d_only24 | 只声明一个 24x24 | **同上** |
| e/f/g | 只声明 24+256、删 `shortcut icon` 等 | **同上** |
| i_none | **完全不声明任何图标** | 仍是 24x24（此时才变成通用图标，证明 HTML 确实参与） |
| p_24_48_256 | 只声明 24/48/256 | 24x24，仍等于 16 放大 |
| aumid1 | 加 `--app-user-model-id` + 开始菜单 `.lnk`（`IconLocation` 指向 voca.ico） | **位图与之前完全一致（sha e923b7dab2）** |

十个 HTML 变体产出的 `ICON_SMALL` **位图 sha256 全部相同**。也就是说：只要窗口是 `msedge --app` 建的，无论 favicon 怎么声明、无论有没有注册 AppUserModelID，任务栏拿到的都是那张 16px 放大的图。

**这是一条无法通过图标文件绕过的架构性限制。**

## 四、修复方案：换成原生窗口宿主

`src/windows/voca_host.c`：一个真正的 Win32 窗口 + WebView2 控件。窗口自己拥有图标，因此可以**直接向 `.ico` 要 shell 指定的那个像素尺寸**，全程零重采样：

```c
dpi      = GetDpiForWindow(hwnd);
small_px = GetSystemMetricsForDpi(SM_CXSMICON, dpi);   // 150% -> 24
big_px   = GetSystemMetricsForDpi(SM_CXICON,    dpi);   // 150% -> 48
hs = LoadImageW(ico, IMAGE_ICON, small_px, small_px, LR_LOADFROMFILE);
hb = LoadImageW(ico, IMAGE_ICON, big_px,   big_px,   LR_LOADFROMFILE);
SendMessageW(hwnd, WM_SETICON, ICON_SMALL/ICON_BIG/ICON_SMALL2, ...);
```

配套措施：
- `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` + `RT_MANIFEST` 双保险；
- `WM_DPICHANGED` 里按新 DPI **重新取帧**并重新 `WM_SETICON`，拖到不同缩放的副屏不会变糊；
- `SetCurrentProcessExplicitAppUserModelID("Voca.Offline.WordTrainer.v1")`，让任务栏按钮独立成组，不与 Edge 浏览器窗口混在一起；
- `.rc` 仍编入 8 帧 `RT_GROUP_ICON`（资源管理器/快捷方式/Alt-Tab 用），单一来源 `assets/voca.ico`。

## 五、修复后的实测验收

真机启动 `Voca.exe`（v1.0.4 原生宿主），取回窗口图标与资产比对：

| 项目 | v1.0.3（Edge shell） | **v1.0.4（原生宿主）** |
| :--- | :--- | :--- |
| `ICON_SMALL` 尺寸 | 24x24 | 24x24 |
| 与 `icon_24.png` 的平均通道差 | 12.94 | **0.00（逐像素完全相同）** |
| 与 `icon_16.png`→24 的平均通道差 | **2.47**（说明用的是 16 放大） | 11.28 |
| 窗口类 | `Chrome_WidgetWin_1`（Edge 建的） | **`Voca.MainWindow`（我们建的）** |
| Edge 进程数 | 10~22 | 宿主自身 1 个主进程 + WebView2 子进程 |

**平均通道差 0.00 = 任务栏拿到的就是我们手工调优的那张 24px 图，没有任何缩放。** 这是本报告里唯一的"修好了"的证据形式。

标题栏与窗口截图见 `_verify/hosttest/host7_window.png` 与 `_verify/shots/host7_icon24_8x.png`（8 倍最近邻放大，边缘清晰、V+书本负形可辨）。

## 六、仍未覆盖与新的代价

1. **只在本机 150% 单屏验证。** 100%/125%/175%/200%/225%/250% 与多屏混合 DPI 下 `WM_DPICHANGED` 重新取帧的逻辑已实现，但**未实测**。
2. **新增运行依赖**：需要 **Microsoft Edge WebView2 Runtime**（Windows 11 与 Windows 10 2004+ 一般预装）。缺失时宿主自动退回旧的 `msedge --app` 方式启动并弹窗说明——功能可用，但图标退回偏软状态。
3. **`WebView2Loader.dll` 必须与 `Voca.exe` 同目录发布**（165,968 字节，BSD-3 许可，见 `THIRD_PARTY_NOTICES.md`）。
4. **`Voca.exe` 仍未做代码签名**，SmartScreen 仍会提示未知发布者。
5. 图标在**任务栏**上的最终观感仍建议由使用者在真机上目视确认一次；本报告给出的是像素级证据而非观感结论。

## 七、如果将来要更进一步

当前方案已让任务栏图标像素级正确。若还想让 Windows 把它当成一个"已安装应用"（开始菜单项、通知、固定到任务栏的独立图标），需要走 Edge 的 PWA 安装路径（要求 https 源 + Web App Manifest），对一款 `file://` 离线单机软件来说收益有限，暂不列入计划。

---

## 八、同日补充：原生宿主上又查出的两个残留缺陷（2026-10-17 晚）

本文第二~五节的结论（`ICON_SMALL` 与 `assets/icons/icon_24.png` 逐像素相同）当时是成立的，但**不完整**：只测了小图标槽位。后续对 v1.0.4 最终构建做完整窗口图标复验时，又发现并修复了两个独立缺陷。

### 8.1 `Voca.exe` 被链接成控制台子系统

PE `Subsystem` 实测为 `3`（CUI），从资源管理器双击会额外弹出一个黑色控制台窗口。根因是 `scripts/build_host_v104.py` 只传了 `-municode` 而没传 `-mwindows`。修复后 `Subsystem = 2`（GUI），启动后新增可见窗口只有 `Voca.MainWindow` 一个。

### 8.2 `ICON_BIG` 从未生效，Alt+Tab 与任务栏预览拿到的是 24px 放大图

外部探针读 `WM_GETICON` 发现 `ICON_SMALL` / `ICON_BIG` / `ICON_SMALL2` **返回同一个句柄且都是 24×24**。逐层排查（`LoadImageW` 逐尺寸实测 8 帧全部精确 → 宿主内探针确认 `hs`/`hb` 是两个不同的非空句柄、请求尺寸 24/48 正确 → 排除类图标被提前 `DestroyIcon` → 在 `CreateWindowExW` 之后单独设 `ICON_BIG` 立刻生效）后定位到两个叠加原因：

1. `ApplyWindowIcons()` 原本在 `WM_CREATE` 里调用，而 `WM_CREATE` 还在 `CreateWindowExW` 内部，此时设的 `ICON_BIG` 会被创建流程收尾时的类图标初始化覆盖；
2. 三条 `WM_SETICON` 的顺序是 `SMALL → BIG → SMALL2`，**最后发 `ICON_SMALL2` 会让大图标槽位也落到小图标上**。

修复：改为 `CreateWindowExW` 返回后调用，并把 `ICON_BIG` 放最后。复验（以实际句柄回读与逐像素比对为验收依据）：

| 槽位 | 修复前 | 修复后 | 与源帧比对 |
| :--- | :--- | :--- | :--- |
| `ICON_SMALL` | 24×24 | 24×24 | 与 `assets/icons/icon_24.png` 逐像素相同（delta `0.0000`） |
| `ICON_SMALL2` | 24×24（同一句柄） | 24×24 | 同上 |
| `ICON_BIG` | **24×24（同一句柄）** | **48×48** | 与 `assets/icons/icon_48.png` 逐像素相同（delta `0.0000`） |

DPI 144 下宿主自检日志：`icons_set=0x00180030`（请求 24/48）、`icons_readback=0x00001830`（回读 24/48）。修复前回读是 `0x00001818`。

完整过程与数据见 `docs/08` 第三节。
