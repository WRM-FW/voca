# Voca v1.0.3 版本升级与跨平台数据迁移指南

本文档与项目根目录 `README.md` 第五节「用户数据：位置、备份与迁移」保持一致，提供从 v1.0.2（及更早版本）升级至 v1.0.3 的可执行步骤与路径说明。

## 一、各平台数据存储位置速查

1. **Windows 平台**（相对于 `windows/` 目录，即 `Voca.exe` 所在目录）：
   - 用户学习记录存储目录：`./data/profile/Default/Local Storage/leveldb/` 与 `./data/profile/Default/IndexedDB/`
   - 内置 SQLite 词库：`./data/voca.db`
2. **Android 平台**（相对于系统沙箱根目录 `/data/data/com.voca.app/`）：
   - 用户学习记录存储目录：`./app_webview/Default/Local Storage/` 与 `./app_webview/Default/IndexedDB/`
   - 内置词库与前端资源：APK 内 `assets/index.html`

## 二、可执行升级与迁移步骤

1. **升级前备份**：在旧版进入「词库导入与PDF导出」→ 点击「⬇ 导出完整学习备份 (.json)」。
2. **执行升级**：
   - Windows 可直接将旧版 `windows/data/profile/` 文件夹复制到新版 `windows/data/profile/`，或在新版中导入 `.json` 备份；
   - Android 安装 `Voca_v1.0.3_release.apk` 后，在「词库导入与PDF导出」中点击「⬆ 从备份文件恢复数据」选择 `.json` 备份文件。
3. **验证升级结果**：确认状态栏显示 `Schema v1.0.3`，且不会程度、生词本、熟词表、自定义计划参数与打卡记录全部正常。

## 三、Android 侧特别注意（2026-10-17 真机复验后补充）

- 本仓库的 APK 由 `scripts/build_apk_v103.py` 构建，**签名证书每次构建临时生成后即销毁**，不是长期密钥。因此只有官方 Release 提供的 `Voca_v1.0.3_release.apk`（证书 SHA-256 `53ddf4bf80d0a262d77dfed58e8c50cc3c67ffadaf7fc02111e0812b020ea9cd`）之间可以互相覆盖安装；自行重建的产物与它签名不一致，覆盖安装会报签名冲突，只能先卸载再装。
- **卸载会彻底销毁 `/data/data/com.voca.app/`**，所以 Android 端任何升级动作之前必须先导出 `.json` 备份。
- 上述「先备份再动」的规则同样适用于从 v1.0.2 升到 v1.0.3。
- 另需说明：Android 端至今**未在任何真机或模拟器上实测过安装与启动**，本节步骤是按清单声明与前端实现推导的，尚未被验证。
