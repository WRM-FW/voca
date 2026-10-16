-- Voca 词库 (voca.db) 表结构
-- 该库可同时存放词典数据与应用运行时的用户数据表，此处只列出词典部分。

CREATE TABLE book(
    id         TEXT PRIMARY KEY,      -- 词库标识
    name       TEXT NOT NULL,         -- 中文名，如「四级核心」
    subtitle   TEXT,                  -- 副标题
    word_count INTEGER NOT NULL,      -- 词条数
    sort_order INTEGER NOT NULL       -- 展示顺序
);

CREATE TABLE word(
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    book     TEXT    NOT NULL,        -- 所属词库
    headword TEXT    NOT NULL,        -- 单词
    phonetic TEXT,                    -- 音标（ECDICT 通用标注体系，形如 /əˈgeinst/）
    pos      TEXT,                    -- ECDICT 的词性频次统计，如 v:15/n:85
    meaning  TEXT    NOT NULL,        -- 中文释义，多个义项以换行分隔
    rank     INTEGER                  -- 词频序，越小越常用；缺失为大数
);
-- 同一单词出现在多本词库中时是多行（各自独立的 id），学习进度因此天然按词库隔离。
