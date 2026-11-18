# Voca v1.0.6 全词库双语例句验收报告（2026-11-18）

## 本版解决的问题

v1.0.5 中只有 233 个 curated「rich」词条带人工例句；其余单词在列表视图里显示的
例句来自前端 `synthesizeContextProfile()` 的统一模板句
（"Mastering the precise usage of '…' in context improves academic reading and writing."），
每个词都一样，不是该词的真实用法示例。

## 变更

1. 为其余 **14,710** 个不重复单词逐词编写一条英文例句 + 中文翻译，编写依据为
   各词在 ECDICT 词库中的中文释义主词性与主义项；例句存入
   `src/lexicon/v103_lexicon_payload.json` 新增的 `examples` 字段
   （`{headword 小写: [ex_en, ex_cn]}`）。原 233 条 rich 例句保持不变、优先级不变。
2. 前端 `hydrateUniqueWord()` 改为从 `VOCA_PACK.examples` 取例句；
   `synthesizeContextProfile()` 删除模板例句，只再生成词性/词频 tip 行。
3. 版本号全量升至 1.0.6（前端标题/徽章/`appVersion`/导出文件名与备份版本、
   构建脚本横幅、`assemblyIdentity` 1.0.6.0、`Image Version` 1.6）；
   `schemaVersion` 保持 4，旧存档兼容口径不变。Android 继续暂停，未刷新其资产。

## 验证（数据级，对随版交付的 payload 与组装后 index.html 实测）

| 检查项 | 结果 |
| :--- | :--- |
| 不重复单词总数 | 14,942 |
| 能解析到非空双语例句的单词 | 14,942 / 14,942（rich 233 + examples 14,710） |
| 模板句残留（payload 与 index.html） | 0 |
| 例句为空/格式异常 | 0 |
| 英文例句未含目标词或其词干 | 15 例，均为不规则/规则变形（threw、shook、denied、wrung、slew、decried、besought、rent、deified、honing 等），逐条复核为正确用法 |
| 重复例句 | 0（初检发现 2 组共用句，已改写） |
| 中文翻译无中文字符 | 0 |
| 组装后 HTML 内两段 `<script>` 的 JS 语法（node --check） | 均通过 |
| 按 v1.0.6 hydrate 逻辑对全库模拟解析 | ok 14,942 / empty 0 / template 0 |
| 前端组装方式 | 仓库自带 `make_html_v103_part3.py`（与 `build_all.sh` 第 2 步相同），产物同步到 `windows/app/index.html` 与 `src/webapp/index.html`（各 6,304,897 字节） |

截图中 CET-4 List 1 前 10 词抽查：affection / algebra / area / attention /
auxiliary / bare / brass / business / cement / centre 均已显示各自的真实双语例句。

## 未覆盖与已知限制

- 14,710 条新例句经机器校验（覆盖、含词、去重、格式），未经人工逐条校对，
  个别句子可能存在措辞不够地道之处。
- `Voca.exe` 未在本轮重建：仓库交付口径为源码 + 组装后前端，Windows 二进制
  仍由在 Windows 上运行 `build_all.sh` 产生。
- 仓库自带 `run_e2e_v103.py` 需要 Selenium + Windows 产物（Voca.exe/voca.ico），
  本轮环境不具备，未运行；本报告的验证为数据级与逻辑模拟级。
- `windows/data/voca.db` 的 `word` 表本身没有例句列，例句的唯一数据源是前端
  payload，本轮未改动数据库结构。
