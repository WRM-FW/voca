#!/usr/bin/env python3
"""
Builds the Voca v1.0.1 Default Built-in Lexicon from Google Drive's 'Voca-词库数据包' (voca.db)
while preserving full backward compatibility with v1.0.0 word annotations and user records.
"""
import os
import json
import sqlite3
from generate_vocab_db_part1 import CET4_CET6_WORDS
from generate_vocab_db_part2 import MORE_WORDS

def build_compact_lexicon():
    # 1. Load v1.0.0 rich annotations (233 words with WordNet en_def, synonyms, bilingual examples, mnemonics)
    rich_map = {}
    for idx, item in enumerate(CET4_CET6_WORDS + MORE_WORDS, start=1):
        word, uk, us, cn, en, syn, ex_en, ex_cn, tip, books, freq = item
        w_norm = word[0].lower() + word[1:] if word in ("Available", "Sustain") else word
        rich_map[w_norm.lower()] = {
            "v1_id": f"voca_{idx:04d}",
            "uk": uk,
            "us": us,
            "en": en,
            "syn": syn,
            "ex_en": ex_en,
            "ex_cn": ex_cn,
            "tip": tip,
        }

    # 2. Load voca.db (38,855 rows across 8 exam books: zk, gk, cet4, cet6, ky, toefl, ielts, gre)
    conn = sqlite3.connect(os.path.abspath(os.path.join( os.path.dirname(__file__), "..", "..", "windows", "data", "voca.db")))
    cur = conn.cursor()
    books_meta = []
    for bid, bname, bsub, bcnt, bsort in cur.execute("SELECT id, name, subtitle, word_count, sort_order FROM book ORDER BY sort_order").fetchall():
        books_meta.append({
            "id": bid,
            "name": bname,
            "subtitle": bsub,
            "count": bcnt,
            "sort": bsort
        })

    rows = cur.execute("SELECT id, book, headword, phonetic, pos, meaning, rank FROM word ORDER BY id").fetchall()
    conn.close()

    # Deduplicate unique headwords while preserving exact (book, row_id) pairs and ordering
    word_index_map = {}
    unique_words = []
    book_word_indices = {b["id"]: [] for b in books_meta}

    for row_id, book, hw, ph, pos, meaning, rank in rows:
        if hw not in word_index_map:
            u_idx = len(unique_words)
            word_index_map[hw] = u_idx
            # Normalize multiline meaning to clean semicolon/line separated string
            clean_mean = "；".join([line.strip() for line in (meaning or "").splitlines() if line.strip()])
            ph_str = f"/{ph.strip('/')}/" if (ph and ph.strip()) else ""
            # Format compact entry: [headword, phonetic, meaning, rank]
            unique_words.append([hw, ph_str, clean_mean, rank if rank is not None else 999999])
        else:
            u_idx = word_index_map[hw]
        book_word_indices[book].append([u_idx, row_id])

    payload = {
        "version": "1.0.1",
        "source": "ECDICT Open Corpus (MIT License, Copyright (c) 2025 Linwei)",
        "totalRows": len(rows),
        "uniqueCount": len(unique_words),
        "books": books_meta,
        "words": unique_words,
        "bookMap": book_word_indices,
        "rich": rich_map
    }

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "v103_lexicon_payload.json"))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Built v101_lexicon_payload.json: {os.path.getsize(out_path)} bytes ({len(rows)} total rows, {len(unique_words)} unique headwords, {len(rich_map)} rich annotations)")

if __name__ == "__main__":
    build_compact_lexicon()
