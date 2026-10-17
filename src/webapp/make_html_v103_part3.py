#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates Part 3 of Voca v1.0.4 HTML Application (JavaScript Engine) and assembles Voca_App_v103.html.
Upgrades in v1.0.3:
1. Removed '掌握度' (mastery) across state, UI, sorting, immersive card, spelling, CSV, and PDF exports; retained '不会程度' (unfam 0..5) with left-click (+1) and right-click (-1).
2. Removed '英英模式' (en_en) from language modes, hints, rendering, and keyboard shortcuts; auto-migrates legacy 'en_en' state to 'bilingual'.
3. Redesigned Dictionary & Edit Modal (#dictModal):
   - Removed '英英释义与同义词拓展' and '双语语境例句与助记' blocks.
   - Integrated Eudic (https://dict.eudic.net/dicts/en/@word@) and WordReference (https://www.wordreference.com/enzh/@word@) with proper URL encoding, HTML entry parsing, live embedded view, and honest offline/error/not-found handling.
4. Added persistent Online Dictionary selection setting (state.settings.onlineDict: 'eudic' | 'wordreference') synced between Settings and Dictionary Modal.
5. Lossless state migration from v1.0.0 / v1.0.1 / v1.0.2 to v1.0.3 (Schema v4).
"""
import os
from make_html_v103_part1 import HTML_PART1
from make_html_v103_part2 import HTML_PART2

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CORE233_PATH = os.environ.get("VOCA_CORE233_JSON", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "windows", "data", "voca_lexicon.json")))
if not os.path.exists(CORE233_PATH):
    alt_c = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "windows", "data", "voca_lexicon.json"))
    if os.path.exists(alt_c):
        CORE233_PATH = alt_c

PACK_PATH = os.environ.get("VOCA_PACK_JSON", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "lexicon", "v103_lexicon_payload.json")))
if not os.path.exists(PACK_PATH):
    alt_p = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "lexicon", "v103_lexicon_payload.json"))
    if os.path.exists(alt_p):
        PACK_PATH = alt_p

with open(CORE233_PATH, "r", encoding="utf-8") as f:
    core233_json_str = f.read()

with open(PACK_PATH, "r", encoding="utf-8") as f:
    v103_pack_json_str = f.read()

JS_ENGINE = r"""
(function() {
  "use strict";

  const STORAGE_KEY = "voca_offline_state_v1";
  const IDB_NAME = "VocaDB_v1";
  const IDB_STORE = "app_state";
  const VALID_THEMES = ["daylight", "oled", "paper"];
  const VALID_LANG_MODES = ["bilingual", "en_only", "cn_only"];
  const VALID_ONLINE_DICTS = ["eudic", "iciba", "wordreference"];

  // Per-source capability flags below are NOT guesses: each was measured against the live site
  // on 2026-10-17 (response headers + real Chromium frame load). See docs/06.
  //   eudic /dicts  -> x-frame-options: SAMEORIGIN (frame always blocked), access-control-allow-origin: *
  //   eudic /mdicts -> no x-frame-options (frame renders), access-control-allow-origin: *
  //   iciba         -> no x-frame-options (frame renders), access-control-allow-origin: *
  //   wordreference -> 200 carries x-frame-options: SAMEORIGIN *and* CSP frame-ancestors 'self'
  //                    https://wordreference.com https://*.wordreference.com <third-party allowlist>
  //                    plus an Anubis JS anti-bot gate. Content cannot be framed or fetched.
  const ONLINE_DICT_SOURCES = {
    eudic: {
      key: "eudic",
      name: "欧路词典",
      // /dicts/en/ answers with x-frame-options: SAMEORIGIN and replaces some Chinese
      // characters inside the gloss with <img> tags, so a text extract of it is
      // incomplete. /mdicts/en/ has no framing header, sends access-control-allow-origin: *,
      // and carries the full gloss in #FCchild - so one URL serves both purposes.
      parseUrl: "https://dict.eudic.net/mdicts/en/@word@",
      embedUrl: "https://dict.eudic.net/mdicts/en/@word@",
      canEmbed: true,
      canFetch: true,
    },
    iciba: {
      key: "iciba",
      name: "爱词霸英汉词典",
      parseUrl: "https://www.iciba.com/word?w=@word@",
      embedUrl: "https://www.iciba.com/word?w=@word@",
      canEmbed: true,
      canFetch: true,
    },
    wordreference: {
      key: "wordreference",
      name: "WordReference 英汉词典",
      parseUrl: "https://www.wordreference.com/enzh/@word@",
      embedUrl: "",
      canEmbed: false,
      canFetch: false,
    }
  };

  const defaultState = {
    schemaVersion: 4,
    appVersion: "1.0.4",
    currentBook: "cet4",
    currentListIndex: 0,
    langMode: "bilingual",      // bilingual | en_only | cn_only (en_en removed in v1.0.3)
    layoutMode: "list",         // list | card
    intraSort: "initial",       // initial | az | random | hard_first | easy_first
    planListCount: 15,
    planCycleDays: 30,
    planOrderMode: "shuffle",   // shuffle | az | original
    planShuffleSeed: 20261016,
    planActiveDay: 1,
    planChecks: {},
    records: {},                // wordKey -> { unfam: 0..5, starred: false, starredAt: 0, mastered: false, customCn: "", note: "" }
    customWords: [],
    modeHintsShown: {
      en_only: false,
      cn_only: false
    },
    settings: {
      onlineDict: "eudic",      // eudic | iciba | wordreference
      rowClickMode: "unfam_lr", // unfam_lr | left_sound_right_unfam | right_sound_left_unfam | sound_only
      accent: "en-US",
      phoneticDisplay: "both",  // both | us | uk | hide
      theme: "daylight",        // daylight | oled | paper
      fontScale: "standard",    // small | standard | large | xlarge
      soundFx: true,
      spellAutoAdvance: true
    }
  };

  let state = JSON.parse(JSON.stringify(defaultState));
  let bookCache = {};
  let wordLookupById = {};
  let currentLists = [];
  let activeWords = [];
  let listRenderLimit = 120;
  let cardCursor = 0;
  let cardHeadwordPeeked = false;
  let cardMeaningPeeked = false;

  let currentTrainSubMode = "spell";
  let spellList = [];
  let spellCursor = 0;
  let spellTyped = "";
  let spellFiveOptions = [];

  let scrollFrameId = null;
  let scrollLastTick = 0;
  let scrollRunning = false;
  let scrollPausedByHover = false;
  let scrollPausedByTouch = false;

  // Touch devices have no hover, so the long press that lowers 不会程度 needs its own
  // gesture record. One record per physical hold, tagged with who consumed it, so the
  // native contextmenu a WebView raises for the same hold can never decrement twice.
  let holdSeq = 0;
  let activeHold = null;          // { seq, row, startedAt, consumedBy: null | "gesture" | "contextmenu" }
  let suppressClickUntil = 0;
  let lastTouchAt = 0;
  const LONG_PRESS_MS = 480;
  const LONG_PRESS_SLOP = 12;
  const TOUCH_ECHO_MS = 1500;

  function isTouchShell() {
    // Provided by the input-capability script in <head>. Defaults to "not touch", which
    // keeps the desktop right-click behaviour if that script is ever absent.
    try { return !!(window.__VOCA_IS_TOUCH__ && window.__VOCA_IS_TOUCH__()); } catch (e) { return false; }
  }

  let nbActiveSubTab = "starred";
  let currentModalWordId = null;
  let currentDictAbortCtrl = null;
  let lastPrintHtmlContent = "";
  let lastPrintTitle = "Voca_Print_Sheet";
  let lastPrintDocData = null;

  // ==================== 1. PERSISTENCE & V1.0.0/V1.0.1/V1.0.2 -> V1.0.3 MIGRATION ====================
  function sanitizePlanParams(rawN, rawD) {
    let n = parseInt(rawN, 10);
    if (isNaN(n) || n < 1) n = 15;
    if (n > 365) n = 365;

    let d = parseInt(rawD, 10);
    if (isNaN(d) || d < 1) d = n + 15;
    if (d > 730) d = 730;
    return { n: n, d: d };
  }

  function migrateStateIfNeeded(loaded) {
    const merged = Object.assign({}, defaultState, loaded || {});
    merged.settings = Object.assign({}, defaultState.settings, (loaded && loaded.settings) || {});
    merged.modeHintsShown = {
      en_only: !!(loaded && loaded.modeHintsShown && loaded.modeHintsShown.en_only),
      cn_only: !!(loaded && loaded.modeHintsShown && loaded.modeHintsShown.cn_only)
    };
    merged.records = {};
    merged.planChecks = (loaded && loaded.planChecks) || {};
    merged.customWords = Array.isArray(loaded && loaded.customWords) ? loaded.customWords : [];

    // 1. Validate Theme
    if (VALID_THEMES.indexOf(merged.settings.theme) === -1) {
      merged.settings.theme = "oled";
    }

    // 2. Migrate removed 'en_en' (英英模式) to 'bilingual'
    if (VALID_LANG_MODES.indexOf(merged.langMode) === -1) {
      merged.langMode = "bilingual";
    }

    // 3. Validate Online Dictionary Setting
    if (VALID_ONLINE_DICTS.indexOf(merged.settings.onlineDict) === -1) {
      merged.settings.onlineDict = "eudic";
    }

    // 4. Migrate legacy Row Click Modes (from mastery-based v1.0.1/v1.0.2 to unfam-based v1.0.3)
    const clickModeMap = {
      mastery_lr: "unfam_lr",
      both: "unfam_lr",
      left_sound_right_mark: "left_sound_right_unfam",
      right_sound_left_mark: "right_sound_left_unfam"
    };
    if (clickModeMap[merged.settings.rowClickMode]) {
      merged.settings.rowClickMode = clickModeMap[merged.settings.rowClickMode];
    }
    const validClickModes = ["unfam_lr", "left_sound_right_unfam", "right_sound_left_unfam", "sound_only"];
    if (validClickModes.indexOf(merged.settings.rowClickMode) === -1) {
      merged.settings.rowClickMode = "unfam_lr";
    }

    // 5. Migrate legacy Intra-List Sort ('mastery_asc' -> 'hard_first')
    if (merged.intraSort === "mastery_asc") {
      merged.intraSort = "hard_first";
    }

    // 6. Migrate legacy Book IDs
    const bookMigrationMap = {
      all: "cet4",
      kaoyan: "ky",
      academic: "ielts"
    };
    if (bookMigrationMap[merged.currentBook]) {
      merged.currentBook = bookMigrationMap[merged.currentBook];
    }

    // 7. Clean & migrate word records: strip removed 'mastery' field while preserving unfam, starred, mastered, customCn, note
    const rawRecords = (loaded && loaded.records) || {};
    Object.keys(rawRecords).forEach(function(k) {
      const r = rawRecords[k];
      if (r && typeof r === "object") {
        let unfamVal = typeof r.unfam === "number" ? r.unfam : 0;
        unfamVal = Math.max(0, Math.min(5, Math.round(unfamVal)));
        merged.records[k] = {
          unfam: unfamVal,
          starred: !!r.starred,
          starredAt: r.starredAt || 0,
          mastered: !!r.mastered,
          customCn: String(r.customCn || ""),
          note: String(r.note || "")
        };
      }
    });

    // 8. Sanitize Plan Params
    const rawN = (loaded && loaded.planListCount) ? loaded.planListCount : 15;
    const rawD = (loaded && loaded.planCycleDays) ? loaded.planCycleDays : (parseInt(rawN, 10) + 15);
    const cleanND = sanitizePlanParams(rawN, rawD);
    merged.planListCount = cleanND.n;
    merged.planCycleDays = cleanND.d;

    if (merged.planActiveDay > merged.planCycleDays || merged.planActiveDay < 1) {
      merged.planActiveDay = 1;
    }

    merged.schemaVersion = 4;
    merged.appVersion = "1.0.4";
    return merged;
  }

  function loadFromLocalStorage() {
    if (window.__VOCA_PRELOAD_STATE__) {
      state = migrateStateIfNeeded(window.__VOCA_PRELOAD_STATE__);
      return;
    }
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        state = migrateStateIfNeeded(JSON.parse(raw));
      }
    } catch (err) {
      console.warn("LocalStorage read fallback:", err);
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (err) {
      console.warn("LocalStorage write warning:", err);
    }
    saveToIndexedDB(state);
    updateStorageDiagnostics();
  }

  function initIndexedDB() {
    try {
      if (!window.indexedDB) return;
      const req = window.indexedDB.open(IDB_NAME, 1);
      req.onupgradeneeded = function(ev) {
        const db = ev.target.result;
        if (!db.objectStoreNames.contains(IDB_STORE)) {
          db.createObjectStore(IDB_STORE);
        }
      };
      req.onsuccess = function(ev) {
        const db = ev.target.result;
        try {
          const tx = db.transaction(IDB_STORE, "readonly");
          const getReq = tx.objectStore(IDB_STORE).get("main");
          getReq.onsuccess = function() {
            let hasLs = false;
            try { hasLs = !!localStorage.getItem(STORAGE_KEY); } catch (e) {}
            if (getReq.result && !hasLs) {
              state = migrateStateIfNeeded(getReq.result);
              rebuildCustomBookCache();
              applySettingsToDOM();
              refreshAllViews();
            }
          };
        } catch (e) {}
      };
    } catch (err) {}
  }

  function saveToIndexedDB(dataCopy) {
    try {
      if (!window.indexedDB) return;
      const req = window.indexedDB.open(IDB_NAME, 1);
      req.onsuccess = function(ev) {
        const db = ev.target.result;
        try {
          const tx = db.transaction(IDB_STORE, "readwrite");
          tx.objectStore(IDB_STORE).put(JSON.parse(JSON.stringify(dataCopy)), "main");
        } catch (e) {}
      };
    } catch (err) {}
  }

  // Headword-keyed record lookup (Unfamiliarity-only in v1.0.3, no mastery field)
  function getRecord(wordId) {
    const w = wordLookupById[wordId];
    const hwKey = w ? ("hw_" + w.word.toLowerCase()) : wordId;
    const legacyId = (w && w.v1_id) ? w.v1_id : null;

    if (!state.records[hwKey]) {
      const existing = state.records[wordId] || (legacyId && state.records[legacyId]);
      if (existing) {
        state.records[hwKey] = {
          unfam: typeof existing.unfam === "number" ? Math.max(0, Math.min(5, existing.unfam)) : 0,
          starred: !!existing.starred,
          starredAt: existing.starredAt || 0,
          mastered: !!existing.mastered,
          customCn: String(existing.customCn || ""),
          note: String(existing.note || "")
        };
      } else {
        state.records[hwKey] = {
          unfam: 0,
          starred: false,
          starredAt: 0,
          mastered: false,
          customCn: "",
          note: ""
        };
      }
    }
    if ("mastery" in state.records[hwKey]) {
      delete state.records[hwKey].mastery;
    }
    return state.records[hwKey];
  }

  // ==================== 2. AUDIO & SPEECH SYNTHESIS ENGINE ====================
  let audioCtx = null;
  function playTone(type) {
    if (!state.settings.soundFx) return;
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      if (!audioCtx) audioCtx = new Ctx();
      if (audioCtx.state === "suspended") audioCtx.resume();
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      if (type === "tap") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(520, now);
        osc.frequency.exponentialRampToValueAtTime(660, now + 0.06);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.07);
        osc.start(now);
        osc.stop(now + 0.07);
      } else if (type === "down") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(330, now + 0.06);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.07);
        osc.start(now);
        osc.stop(now + 0.07);
      } else if (type === "success") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(587.33, now);
        osc.frequency.setValueAtTime(880, now + 0.08);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.24);
        osc.start(now);
        osc.stop(now + 0.24);
      } else if (type === "error") {
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.linearRampToValueAtTime(165, now + 0.14);
        gain.gain.setValueAtTime(0.10, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
        osc.start(now);
        osc.stop(now + 0.16);
      }
    } catch (e) {}
  }

  function speakText(text, langOverride, onEndCallback) {
    try {
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = langOverride || state.settings.accent || "en-US";
        utter.rate = 0.95;
        if (onEndCallback) {
          utter.onend = onEndCallback;
          utter.onerror = onEndCallback;
        }
        window.speechSynthesis.speak(utter);
        return;
      }
    } catch (e) {}
    playTone("tap");
    if (onEndCallback) setTimeout(onEndCallback, 450);
  }

  function showToast(msg) {
    const box = document.getElementById("toastContainer");
    if (!box) return;
    const item = document.createElement("div");
    item.className = "toast-item";
    item.textContent = msg;
    box.appendChild(item);
    setTimeout(function() {
      if (item.parentNode) item.parentNode.removeChild(item);
    }, 2600);
  }

  // ==================== 3. LEXICON HYDRATION & CUSTOM LIST PARTITIONING ====================
  function synthesizeContextProfile(hw, cnMeaning, rank) {
    const posMatches = cnMeaning.match(/\b(n|v|vt|vi|a|adj|adv|prep|conj|pron|num|art|aux|interj)\./g) || [];
    return {
      ex_en: "Mastering the precise usage of '" + hw + "' in context improves academic reading and writing.",
      ex_cn: "在语境中准确掌握“" + hw + "”的用法有助于提升学术读写能力。",
      tip: "词性结构: " + (posMatches.length ? posMatches.join(" / ") : "核心考纲词") + " · 词频序: " + ((rank && rank < 900000) ? rank : "考纲精选")
    };
  }

  function hydrateUniqueWord(uIdx, rowId, bookId) {
    const tuple = VOCA_PACK.words[uIdx];
    const hw = tuple[0];
    const ph = tuple[1] || "/-/";
    const cn = tuple[2] || "";
    const rank = tuple[3] || 999999;
    const wid = "w_" + bookId + "_" + rowId;
    if (wordLookupById[wid]) return wordLookupById[wid];

    const rich = VOCA_PACK.rich[hw.toLowerCase()];
    let wObj;
    if (rich) {
      wObj = {
        id: wid,
        v1_id: rich.v1_id,
        seq: rowId,
        word: hw,
        uk: rich.uk || ph,
        us: rich.us || ph,
        cn: cn,
        ex_en: rich.ex_en,
        ex_cn: rich.ex_cn,
        tip: rich.tip,
        rank: rank
      };
    } else {
      const synth = synthesizeContextProfile(hw, cn, rank);
      wObj = {
        id: wid,
        v1_id: null,
        seq: rowId,
        word: hw,
        uk: ph,
        us: ph,
        cn: cn,
        ex_en: synth.ex_en,
        ex_cn: synth.ex_cn,
        tip: synth.tip,
        rank: rank
      };
    }
    wordLookupById[wid] = wObj;
    return wObj;
  }

  function rebuildCustomBookCache() {
    CORE233_VOCAB.forEach(function(w) {
      w.v1_id = w.id;
      wordLookupById[w.id] = w;
    });
    (state.customWords || []).forEach(function(w) {
      wordLookupById[w.id] = w;
    });
    bookCache["core233"] = CORE233_VOCAB.slice();
    bookCache["custom"] = (state.customWords || []).length > 0 ? state.customWords.slice() : CORE233_VOCAB.slice(0, 20);
  }

  function getBookWords(bookId) {
    if (bookCache[bookId]) return bookCache[bookId].slice();
    const pairs = VOCA_PACK.bookMap[bookId];
    if (!pairs) return CORE233_VOCAB.slice();
    const list = new Array(pairs.length);
    for (let i = 0; i < pairs.length; i++) {
      list[i] = hydrateUniqueWord(pairs[i][0], pairs[i][1], bookId);
    }
    bookCache[bookId] = list;
    return list.slice();
  }

  function getAllKnownWordsForNotebook() {
    const result = [];
    const seenHw = {};
    function addPool(arr) {
      arr.forEach(function(w) {
        const k = w.word.toLowerCase();
        if (!seenHw[k]) {
          seenHw[k] = true;
          result.push(w);
        }
      });
    }
    addPool(getBookWords(state.currentBook));
    addPool(CORE233_VOCAB);
    addPool(state.customWords || []);
    return result;
  }

  function seededShuffle(arr, seed) {
    const copy = arr.slice();
    let s = seed || 20261016;
    for (let i = copy.length - 1; i > 0; i--) {
      s = (s * 1664525 + 1013904223) % 4294967296;
      const j = s % (i + 1);
      const tmp = copy[i];
      copy[i] = copy[j];
      copy[j] = tmp;
    }
    return copy;
  }

  function buildListsForCurrentBook() {
    let pool = getBookWords(state.currentBook);
    if (state.planOrderMode === "az") {
      pool.sort(function(a, b) { return a.word.localeCompare(b.word); });
    } else if (state.planOrderMode === "shuffle") {
      pool = seededShuffle(pool, state.planShuffleSeed);
    } else {
      pool.sort(function(a, b) { return (a.seq || 0) - (b.seq || 0); });
    }

    const total = pool.length;
    const requestedN = Math.max(1, Math.min(365, parseInt(state.planListCount, 10) || 15));
    const numLists = Math.max(1, Math.min(total || 1, requestedN));
    currentLists = [];
    const baseSize = Math.floor(total / numLists);
    const rem = total % numLists;
    let offset = 0;
    for (let i = 0; i < numLists; i++) {
      const sz = baseSize + (i < rem ? 1 : 0);
      currentLists.push(pool.slice(offset, offset + sz));
      offset += sz;
    }
    if (state.currentListIndex >= currentLists.length || state.currentListIndex < 0) {
      state.currentListIndex = 0;
    }
  }

  function computeCustomEbbinghausSchedule() {
    const N = currentLists.length || Math.max(1, parseInt(state.planListCount, 10) || 15);
    const D = Math.max(1, Math.min(730, parseInt(state.planCycleDays, 10) || (N + 15)));

    let learnDays = N;
    if (D <= N) {
      if (D === 1) {
        learnDays = 1;
      } else if (D <= 4) {
        learnDays = D - 1;
      } else {
        const tailReserve = Math.max(1, Math.min(15, Math.floor(D * 0.30)));
        learnDays = Math.max(1, D - tailReserve);
      }
    }

    const tailDays = Math.max(0, D - learnDays);

    let intervals = [1, 2, 4, 7, 15];
    if (tailDays === 15) {
      intervals = [1, 2, 4, 7, 15];
    } else if (tailDays >= 5) {
      const baseCurve = [1, 2, 4, 7, 15];
      const scaled = [];
      for (let i = 0; i < 5; i++) {
        let val = Math.max(1, Math.round((baseCurve[i] * tailDays) / 15));
        if (i === 4) val = tailDays;
        if (i > 0 && val <= scaled[i - 1]) {
          val = scaled[i - 1] + 1;
        }
        scaled.push(val);
      }
      scaled[4] = tailDays;
      for (let i = 3; i >= 0; i--) {
        if (scaled[i] >= scaled[i + 1]) {
          scaled[i] = Math.max(1, scaled[i + 1] - 1);
        }
      }
      intervals = scaled;
    } else if (tailDays >= 1) {
      intervals = [1, 2, 4, 7, 15];
    } else {
      intervals = [0, 1, 2, 4, 7];
    }

    const dayNewMap = {};
    for (let d = 1; d <= D; d++) dayNewMap[d] = [];

    const basePerDay = Math.floor(N / learnDays);
    const extraDays = N % learnDays;
    let nextListNum = 1;
    for (let d = 1; d <= learnDays; d++) {
      const countToday = basePerDay + (d <= extraDays ? 1 : 0);
      for (let k = 0; k < countToday; k++) {
        if (nextListNum <= N) {
          dayNewMap[d].push(nextListNum++);
        }
      }
    }

    const rows = [];
    for (let d = 1; d <= D; d++) {
      const newLists = dayNewMap[d] || [];
      const revCols = [[], [], [], [], []];
      for (let sIdx = 0; sIdx < 5; sIdx++) {
        const gap = intervals[sIdx];
        if (gap === 0 && sIdx === 0 && D === 1) {
          revCols[sIdx] = newLists.slice();
        } else if (gap >= 1 && d - gap >= 1 && d - gap <= learnDays) {
          revCols[sIdx] = (dayNewMap[d - gap] || []).slice();
        }
      }
      rows.push({
        day: d,
        newLists: newLists,
        revCols: revCols
      });
    }

    return {
      N: N,
      D: D,
      learnDays: learnDays,
      intervals: intervals,
      rows: rows
    };
  }

  function getEffectiveCnDef(w) {
    const rec = getRecord(w.id);
    if (rec && rec.starred && rec.customCn && rec.customCn.trim() !== "") {
      return rec.customCn.trim();
    }
    return w.cn;
  }

  function getPhoneticString(w) {
    const mode = state.settings.phoneticDisplay;
    if (mode === "hide") return "";
    if (mode === "us") return (w.us || w.uk || "");
    if (mode === "uk") return (w.uk || w.us || "");
    if (w.uk && w.us && w.uk !== w.us) return "UK " + w.uk + " · US " + w.us;
    return w.us || w.uk || "";
  }

  // ==================== 4. ONE-TIME MODE HINTS (en_only & cn_only; en_en removed) ====================
  function triggerModeFirstTimeHintIfNeeded(mode) {
    const banner = document.getElementById("modeFirstTimeBanner");
    const textEl = document.getElementById("modeFirstTimeText");
    if (!banner || !textEl) return;

    const hintMessages = {
      en_only: "💡 首次进入「只看英文」模式：在列表或沉浸卡片中，直接点击被遮罩的中文区域即可窥显释义并朗读发音（此提示仅首次显示）。",
      cn_only: "💡 首次进入「只看中文」模式：在列表或沉浸卡片中，点击顶部的「点击此处发音/窥显」区域即可朗读发音并显示英文单词（此提示仅首次显示）。"
    };

    if (hintMessages[mode] && !state.modeHintsShown[mode]) {
      state.modeHintsShown[mode] = true;
      saveState();
      textEl.textContent = hintMessages[mode];
      banner.classList.add("visible");
      showToast(hintMessages[mode]);
    } else if (mode === "bilingual") {
      banner.classList.remove("visible");
    }
  }

  // ==================== 5. RENDER LEARN & LIST VIEW + IMMERSIVE CARD VIEW ====================
  function renderListSelector() {
    const sel = document.getElementById("listSelect");
    sel.innerHTML = "";
    currentLists.forEach(function(lst, idx) {
      const unmastered = lst.filter(function(w) { return !getRecord(w.id).mastered; }).length;
      const opt = document.createElement("option");
      opt.value = String(idx);
      opt.textContent = "List " + (idx + 1) + " (" + unmastered + "/" + lst.length + "词)";
      if (idx === state.currentListIndex) opt.selected = true;
      sel.appendChild(opt);
    });
  }

  function getSortedActiveWords() {
    const rawList = currentLists[state.currentListIndex] || [];
    const query = (document.getElementById("wordSearchInput").value || "").trim().toLowerCase();
    let filtered = rawList.filter(function(w) {
      if (getRecord(w.id).mastered) return false;
      if (!query) return true;
      return (
        w.word.toLowerCase().indexOf(query) !== -1 ||
        getEffectiveCnDef(w).toLowerCase().indexOf(query) !== -1
      );
    });

    if (state.intraSort === "az") {
      filtered.sort(function(a, b) { return a.word.localeCompare(b.word); });
    } else if (state.intraSort === "random") {
      filtered = seededShuffle(filtered, state.planShuffleSeed + state.currentListIndex + 7);
    } else if (state.intraSort === "hard_first") {
      filtered.sort(function(a, b) {
        return (getRecord(b.id).unfam || 0) - (getRecord(a.id).unfam || 0);
      });
    } else if (state.intraSort === "easy_first") {
      filtered.sort(function(a, b) {
        return (getRecord(a.id).unfam || 0) - (getRecord(b.id).unfam || 0);
      });
    }
    return filtered;
  }

  function isListCompleted(listNum) {
    const lst = currentLists[listNum - 1] || [];
    if (lst.length > 0) {
      const allDone = lst.every(function(w) {
        return !!getRecord(w.id).mastered;
      });
      if (allDone) return true;
    }
    return !!state.planChecks["book_" + state.currentBook + "_L" + listNum] || !!state.planChecks["d" + listNum + "_new_L" + listNum];
  }

  function renderStatsAndPills() {
    const rawList = currentLists[state.currentListIndex] || [];
    const masteredInList = rawList.filter(function(w) { return getRecord(w.id).mastered; }).length;
    const remainInList = rawList.length - masteredInList;

    const bookPool = getBookWords(state.currentBook);
    const masteredInBook = bookPool.filter(function(w) { return getRecord(w.id).mastered; }).length;
    const pct = bookPool.length ? Math.round((masteredInBook / bookPool.length) * 100) : 0;

    let totalStarred = 0;
    let totalMasteredAll = 0;
    Object.keys(state.records).forEach(function(k) {
      const r = state.records[k];
      if (r) {
        if (r.starred) totalStarred++;
        if (r.mastered) totalMasteredAll++;
      }
    });

    let completedListsCount = 0;
    for (let i = 1; i <= currentLists.length; i++) {
      if (isListCompleted(i)) completedListsCount++;
    }
    const planPct = currentLists.length ? Math.min(100, Math.round((completedListsCount / currentLists.length) * 100)) : 0;

    document.getElementById("statCurrentListCount").textContent = String(remainInList);
    document.getElementById("statCurrentListSub").textContent = "本组已移除熟词 " + masteredInList + " 个 (共 " + rawList.length + " 词)";
    document.getElementById("statBookProgress").textContent = pct + "%";
    document.getElementById("statBookSub").textContent = "当前词书 " + bookPool.length + " 词 · 已熟 " + masteredInBook + " 词";
    document.getElementById("statStarredTotal").textContent = String(totalStarred);
    document.getElementById("statPlanConfigTag").textContent = currentLists.length + "组/" + state.planCycleDays + "天";
    document.getElementById("statPlanCheckins").textContent = completedListsCount + " / " + currentLists.length + " 组";

    document.getElementById("pillActiveCount").textContent = String(remainInList);
    document.getElementById("pillStarCount").textContent = String(totalStarred);
    document.getElementById("pillPlanDone").textContent = planPct + "%";
    document.getElementById("inlineMasteredCnt").textContent = String(totalMasteredAll);
  }

  function makeUnfamDotsHtml(level) {
    let html = '<span class="unfam-dots" title="不会程度: ' + level + '/5">';
    for (let i = 1; i <= 5; i++) {
      html += '<span class="unfam-dot' + (i <= level ? " lit" : "") + '"></span>';
    }
    html += "</span>";
    return html;
  }

  function makeUnfamBadgeHtml(level) {
    const lv = level || 0;
    const cls = lv > 0 ? "unfam-badge has-unfam" : "unfam-badge";
    return (
      '<span class="' + cls + '" title="不会程度: ' + lv + '/5 (左键点击+1 / 右键点击-1)">' +
        makeUnfamDotsHtml(lv) +
        ' <span class="unfam-num">不会度 ' + lv + '/5</span>' +
      '</span>'
    );
  }

  function renderLearnView() {
    buildListsForCurrentBook();
    renderListSelector();
    activeWords = getSortedActiveWords();
    renderStatsAndPills();

    const listBox = document.getElementById("learnListContainer");
    const pagBox = document.getElementById("learnListPagination");
    const cardBox = document.getElementById("learnCardContainer");

    if (state.layoutMode === "card") {
      listBox.style.display = "none";
      pagBox.style.display = "none";
      cardBox.style.display = "block";
      renderImmersiveCard();
      return;
    }

    listBox.style.display = "block";
    cardBox.style.display = "none";

    if (activeWords.length === 0) {
      pagBox.style.display = "none";
      listBox.innerHTML = '<div style="padding:42px 20px; text-align:center; color:var(--text-muted);">🎉 当前 List 的单词已全部标为熟词或无匹配结果！可切换下一个 List 或在「熟词表」中恢复。</div>';
      return;
    }

    const slice = activeWords.slice(0, listRenderLimit);
    let html = "";
    slice.forEach(function(w, idx) {
      const rec = getRecord(w.id);
      const ipa = getPhoneticString(w);
      const cn = getEffectiveCnDef(w);
      const wordMasked = state.langMode === "cn_only" ? " masked-box" : "";
      const meanMasked = state.langMode === "en_only" ? " masked-box" : "";

      const meaningBody =
        '<div class="w-cn' + meanMasked + '" data-peek="1">' + escapeHtml(cn) + '</div>' +
        '<div class="w-ex">' + escapeHtml(w.ex_en) + '</div>';

      html +=
        '<div class="word-row" data-wid="' + w.id + '" data-unfam="' + (rec.unfam || 0) + '">' +
          '<div class="w-idx">' + (idx + 1) + '</div>' +
          '<div class="w-head-col">' +
            '<div class="w-word">' +
              '<span class="w-head-text' + wordMasked + '" data-peek="1">' + escapeHtml(w.word) + '</span> ' +
              makeUnfamBadgeHtml(rec.unfam || 0) +
            '</div>' +
            (ipa ? '<div class="w-ipa">' + escapeHtml(ipa) + '</div>' : '') +
          '</div>' +
          '<div class="w-meaning-col">' + meaningBody + '</div>' +
          '<div class="w-actions">' +
            '<button class="icon-btn' + (rec.starred ? ' starred' : '') + '" data-act="star" data-wid="' + w.id + '" title="加入/移出生词本">★</button>' +
            '<button class="icon-btn master-btn" data-act="master" data-wid="' + w.id + '" title="标为熟词(从列表中移除)">✕</button>' +
            '<button class="icon-btn" data-act="dict" data-wid="' + w.id + '" title="查看词典详细与编辑">📖</button>' +
          '</div>' +
        '</div>';
    });
    listBox.innerHTML = html;

    if (activeWords.length > listRenderLimit) {
      pagBox.style.display = "flex";
      document.getElementById("btnLoadMoreWords").textContent =
        "加载更多单词 (已显示 " + slice.length + " / " + activeWords.length + ")";
    } else {
      pagBox.style.display = "none";
    }
  }

  function renderImmersiveCard() {
    const headEl = document.getElementById("cardHeadword");
    const cnEl = document.getElementById("cardCnDef");
    const exEnEl = document.getElementById("cardExEn");
    const exCnEl = document.getElementById("cardExCn");
    const mnemEl = document.getElementById("cardMnemonic");

    if (activeWords.length === 0) {
      headEl.className = "card-word-title";
      headEl.textContent = "本组已全部标为熟词 🎉";
      document.getElementById("cardPhoneticText").textContent = "可切换至下一组 List 或在熟词表中恢复";
      cnEl.textContent = "";
      exEnEl.textContent = "";
      exCnEl.textContent = "";
      mnemEl.textContent = "";
      return;
    }
    if (cardCursor >= activeWords.length) cardCursor = 0;
    if (cardCursor < 0) cardCursor = activeWords.length - 1;

    const w = activeWords[cardCursor];
    const rec = getRecord(w.id);

    document.getElementById("cardPosIndicator").textContent =
      "List " + (state.currentListIndex + 1) + " · 第 " + (cardCursor + 1) + " / " + activeWords.length + " 词";
    document.getElementById("cardPhoneticText").textContent = getPhoneticString(w);
    document.getElementById("cardUnfamDots").innerHTML = makeUnfamDotsHtml(rec.unfam || 0);
    document.getElementById("cardUnfamNum").textContent = String(rec.unfam || 0);

    if (state.langMode === "cn_only" && !cardHeadwordPeeked) {
      headEl.className = "card-word-title masked-headword";
      headEl.textContent = "🔒 点击此处发音并窥显英文单词";
    } else {
      headEl.className = "card-word-title";
      headEl.textContent = w.word;
    }

    if (state.langMode === "en_only") {
      cnEl.style.display = "block";
      if (!cardMeaningPeeked) {
        cnEl.textContent = "🔒 点击此处窥显中文释义并朗读发音";
        exCnEl.style.display = "none";
      } else {
        cnEl.textContent = getEffectiveCnDef(w);
        exCnEl.style.display = "block";
        exCnEl.textContent = w.ex_cn;
      }
      exEnEl.textContent = w.ex_en;
      mnemEl.textContent = "💡 " + (w.tip || "");
    } else {
      cnEl.style.display = "block";
      cnEl.textContent = getEffectiveCnDef(w);
      exEnEl.textContent = w.ex_en;
      exCnEl.style.display = "block";
      exCnEl.textContent = w.ex_cn;
      mnemEl.textContent = "💡 " + (w.tip || "");
    }

    const starBtn = document.getElementById("cardBtnStar");
    starBtn.textContent = rec.starred ? "★ 已收藏" : "☆ 生词本";
    starBtn.className = rec.starred ? "btn btn-sm btn-primary" : "btn btn-sm";
  }

  // ==================== 6. CUSTOM EBBINGHAUS PLAN RENDERER ====================
  function renderEbbinghausPlan() {
    buildListsForCurrentBook();
    const sched = computeCustomEbbinghausSchedule();
    const N = sched.N;
    const D = sched.D;
    const intervals = sched.intervals;

    const nInput = document.getElementById("planListCountInput");
    const dInput = document.getElementById("planCycleDaysInput");
    if (nInput && document.activeElement !== nInput) nInput.value = String(state.planListCount);
    if (dInput && document.activeElement !== dInput) dInput.value = String(state.planCycleDays);
    document.getElementById("planOrderModeSelect").value = state.planOrderMode;

    document.querySelectorAll("#planPresetPills .preset-pill-btn").forEach(function(btn) {
      const bn = parseInt(btn.dataset.n, 10);
      const bd = parseInt(btn.dataset.d, 10);
      btn.classList.toggle("active", bn === state.planListCount && bd === state.planCycleDays);
    });

    for (let sIdx = 0; sIdx < 5; sIdx++) {
      const th = document.getElementById("thRev" + (sIdx + 1));
      if (th) {
        th.textContent = "复习周期 " + (sIdx + 1) + " (+" + intervals[sIdx] + "天)";
      }
    }

    const bookTotal = getBookWords(state.currentBook).length;
    const avgWords = Math.ceil(bookTotal / N);
    document.getElementById("planFormulaSummary").textContent =
      "当前生效配置：共 " + N + " 个 List（每组约 " + avgWords + " 词，总词数 " + bookTotal + " 词）· 学习周期 " + D + " 天（前 " + sched.learnDays + " 天完成首轮新学）· 艾宾浩斯复习间隔：" +
      intervals.map(function(g) { return "+" + g + "天"; }).join(", ");

    document.getElementById("planTotalDaysSpan").textContent = String(D);

    if (state.planActiveDay > D || state.planActiveDay < 1) {
      state.planActiveDay = 1;
    }

    const picker = document.getElementById("planDayPicker");
    picker.innerHTML = "";
    for (let d = 1; d <= D; d++) {
      const opt = document.createElement("option");
      opt.value = String(d);
      opt.textContent = "Day " + d + " / " + D;
      if (d === state.planActiveDay) opt.selected = true;
      picker.appendChild(opt);
    }

    const tbody = document.getElementById("ebbinghausTableBody");
    let rowsHtml = "";

    sched.rows.forEach(function(row) {
      const day = row.day;
      let totalTasks = 0;
      let doneTasks = 0;

      function renderCellChips(listNums) {
        if (!listNums || listNums.length === 0) {
          return '<span style="color:var(--text-muted);">—</span>';
        }
        return listNums.map(function(listNum) {
          totalTasks++;
          const isDone = isListCompleted(listNum);
          if (isDone) doneTasks++;
          return (
            '<button class="plan-chip' + (isDone ? ' done' : '') + '" data-listnum="' + listNum + '" title="点击跳转至 List ' + listNum + ' 单词学习界面">' +
              (isDone ? '✓ ' : '→ ') + 'List ' + listNum +
            '</button>'
          );
        }).join(" ");
      }

      const cNew = renderCellChips(row.newLists);
      const cRevs = row.revCols.map(function(colLists) { return renderCellChips(colLists); });

      const rowPct = totalTasks ? Math.round((doneTasks / totalTasks) * 100) : 100;
      const highlightStyle = day === state.planActiveDay ? ' style="background:var(--brand-soft);"' : '';

      rowsHtml +=
        '<tr' + highlightStyle + '>' +
          '<td style="font-weight:800;">Day ' + day + '</td>' +
          '<td>' + cNew + '</td>' +
          '<td>' + cRevs[0] + '</td>' +
          '<td>' + cRevs[1] + '</td>' +
          '<td>' + cRevs[2] + '</td>' +
          '<td>' + cRevs[3] + '</td>' +
          '<td>' + cRevs[4] + '</td>' +
          '<td style="font-weight:700; color:' + (rowPct === 100 ? 'var(--brand-primary)' : 'var(--text-secondary)') + ';">' + doneTasks + '/' + totalTasks + ' (' + rowPct + '%)</td>' +
        '</tr>';

      if (day === state.planActiveDay) {
        const newLabel = row.newLists.length ? row.newLists.map(function(n) { return "List " + n; }).join(", ") : "无(复习巩固期)";
        const allRevLists = [];
        row.revCols.forEach(function(col) {
          col.forEach(function(lid) {
            if (allRevLists.indexOf(lid) === -1) allRevLists.push(lid);
          });
        });
        const revLabel = allRevLists.length ? allRevLists.map(function(n) { return "List " + n; }).join(", ") : "无";

        document.getElementById("planActiveDayNum").textContent = String(day);
        document.getElementById("planActiveDaySummary").textContent =
          "新学: " + newLabel + " · 艾宾浩斯复习: " + revLabel;
        document.getElementById("statTodayTaskHint").textContent =
          "Day " + day + "/" + D + ": 新学 " + (row.newLists.length ? newLabel : "0组") + " · 复习 " + allRevLists.length + " 组";
      }
    });

    tbody.innerHTML = rowsHtml;
  }

  // ==================== 7. SPECIALIZED TRAINING (拼词 + 滚动) ====================
  function getTrainingPool() {
    const src = document.getElementById("trainSourceSelect").value;
    if (src === "starred") {
      const starred = getAllKnownWordsForNotebook().filter(function(w) { return getRecord(w.id).starred; });
      if (starred.length > 0) return starred;
    }
    const listPool = (currentLists[state.currentListIndex] || []).filter(function(w) {
      return !getRecord(w.id).mastered;
    });
    return listPool.length > 0 ? listPool : getBookWords(state.currentBook).slice(0, 20);
  }

  function generateFiveCardOptions(correctChar, seedNum) {
    const alphabet = "abcdefghijklmnopqrstuvwxyz";
    const lower = correctChar.toLowerCase();
    const opts = [lower];
    let s = seedNum || 97;
    while (opts.length < 5) {
      s = (s * 1103515245 + 12345) & 0x7fffffff;
      const ch = alphabet[s % 26];
      if (opts.indexOf(ch) === -1) opts.push(ch);
    }
    return seededShuffle(opts, seedNum + 31);
  }

  function initSpellingSession(resetIdx) {
    spellList = getTrainingPool();
    if (resetIdx || spellCursor >= spellList.length) spellCursor = 0;
    spellTyped = "";
    renderSpellingStage();
  }

  function renderSpellingStage() {
    if (!spellList.length) return;
    const w = spellList[spellCursor];
    const target = w.word.trim();

    document.getElementById("spellProgressText").textContent =
      "拼词挑战 " + (spellCursor + 1) + " / " + spellList.length + " · 不会程度: " + (getRecord(w.id).unfam || 0) + "/5";
    document.getElementById("spellCnPrompt").textContent = getEffectiveCnDef(w);
    document.getElementById("spellIpaPrompt").textContent = getPhoneticString(w);

    const escapedTarget = target.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(escapedTarget, "ig");
    document.getElementById("spellClozePrompt").textContent = (w.ex_en || "").replace(regex, "_______");

    const slotsBox = document.getElementById("spellSlotsBox");
    let slotsHtml = "";
    for (let i = 0; i < target.length; i++) {
      const ch = spellTyped[i] || "";
      const cls = i < spellTyped.length ? "spell-slot filled" : (i === spellTyped.length ? "spell-slot current" : "spell-slot");
      slotsHtml += '<div class="' + cls + '">' + escapeHtml(ch) + '</div>';
    }
    slotsBox.innerHTML = slotsHtml;

    const cardsBox = document.getElementById("spellFiveCardsBox");
    if (spellTyped.length < target.length) {
      const nextChar = target[spellTyped.length];
      spellFiveOptions = generateFiveCardOptions(nextChar, (w.seq || 1) * 31 + spellTyped.length * 17);
      let cHtml = "";
      spellFiveOptions.forEach(function(letter) {
        cHtml += '<button class="letter-card-btn" data-letter="' + escapeHtml(letter) + '">' + escapeHtml(letter) + '</button>';
      });
      cardsBox.innerHTML = cHtml;
    } else {
      cardsBox.innerHTML = '<div style="grid-column:1/-1; color:var(--brand-primary); font-weight:800; font-size:1.05rem;">✓ 拼写正确！请按回车或点击下一词</div>';
    }
  }

  function handleSpellCharInput(ch) {
    if (!spellList.length) return;
    const w = spellList[spellCursor];
    const target = w.word.trim();
    if (spellTyped.length >= target.length) return;

    const expected = target[spellTyped.length].toLowerCase();
    if (ch.toLowerCase() === expected) {
      spellTyped += target[spellTyped.length];
      playTone("tap");
      renderSpellingStage();
      if (spellTyped.length === target.length) {
        playTone("success");
        speakText(w.word);
        if (document.getElementById("spellAutoAdvanceToggle").checked) {
          setTimeout(function() {
            spellCursor = (spellCursor + 1) % spellList.length;
            spellTyped = "";
            renderSpellingStage();
          }, 650);
        }
      }
    } else {
      playTone("error");
      showToast("字母不匹配，请再试一次 (提示: " + expected.toUpperCase() + ")");
    }
  }

  // Shared by the hardware Backspace key and the on-screen ⌫ key: a soft keyboard does
  // not reliably expose either, and a phone player needs a visible delete.
  function spellBackspace() {
    if (spellTyped.length > 0) {
      spellTyped = spellTyped.slice(0, -1);
      playTone("down");
      renderSpellingStage();
    }
  }

  function renderAutoScrollList() {
    const pool = getTrainingPool().slice(0, 150);
    const box = document.getElementById("scrollListContent");
    let html = "";
    pool.forEach(function(w, idx) {
      const rec = getRecord(w.id);
      html +=
        '<div class="word-row" data-wid="' + w.id + '" data-unfam="' + (rec.unfam || 0) + '">' +
          '<div class="w-idx">' + (idx + 1) + '</div>' +
          '<div class="w-head-col">' +
            '<div class="w-word">' + escapeHtml(w.word) + ' ' + makeUnfamBadgeHtml(rec.unfam || 0) + '</div>' +
            '<div class="w-ipa">' + escapeHtml(getPhoneticString(w)) + '</div>' +
          '</div>' +
          '<div class="w-meaning-col">' +
            '<div class="w-cn">' + escapeHtml(getEffectiveCnDef(w)) + '</div>' +
          '</div>' +
          '<div class="w-actions">' +
            '<button class="icon-btn' + (rec.starred ? ' starred' : '') + '" data-act="star" data-wid="' + w.id + '">★</button>' +
            '<button class="icon-btn" data-act="dict" data-wid="' + w.id + '">📖</button>' +
          '</div>' +
        '</div>';
    });
    box.innerHTML = html;
  }

  function toggleAutoScroll(forceStop) {
    const btn = document.getElementById("scrollBtnToggle");
    if (scrollRunning || forceStop) {
      scrollRunning = false;
      if (scrollFrameId !== null) { cancelAnimationFrame(scrollFrameId); scrollFrameId = null; }
      scrollLastTick = 0;
      btn.textContent = "▶ 开启自动滚动";
      return;
    }
    scrollRunning = true;
    btn.textContent = "⏸ 暂停自动滚动";
    const vp = document.getElementById("scrollViewport");
    scrollLastTick = 0;
    // One step per real animation frame instead of setInterval(35ms): no competing
    // timers on a mid-range WebView, and the speed is expressed as px per tick-normalised
    // frame so 60Hz and 120Hz screens drift at the same rate.
    scrollFrameId = requestAnimationFrame(function step(ts) {
      if (!scrollRunning) { scrollFrameId = null; return; }
      scrollFrameId = requestAnimationFrame(step);
      if (document.hidden) { scrollLastTick = ts; return; }
      const dt = scrollLastTick ? Math.min(120, ts - scrollLastTick) : 16;
      scrollLastTick = ts;
      if (scrollPausedByHover || scrollPausedByTouch) return;
      const spd = parseInt(document.getElementById("scrollSpeedSelect").value, 10) || 2;
      vp.scrollTop += spd * (dt / 35);
      if (vp.scrollTop + vp.clientHeight >= vp.scrollHeight - 2) {
        vp.scrollTop = 0;
      }
    });
  }

  // ==================== 8. NOTEBOOK (生词本) & MASTERED (熟词表) ====================
  function renderNotebookView() {
    const allKnown = getAllKnownWordsForNotebook();
    const starredWords = allKnown.filter(function(w) { return getRecord(w.id).starred; });
    const masteredWords = allKnown.filter(function(w) { return getRecord(w.id).mastered; });

    document.getElementById("nbStarCountTab").textContent = String(starredWords.length);
    document.getElementById("nbMasterCountTab").textContent = String(masteredWords.length);

    const box = document.getElementById("notebookListContainer");

    if (nbActiveSubTab === "starred") {
      document.getElementById("nbStarredControls").style.display = "flex";
      document.getElementById("nbMasteredControls").style.display = "none";
      const sortMode = document.getElementById("nbSortSelect").value;
      if (sortMode === "newest") {
        starredWords.sort(function(a, b) { return (getRecord(b.id).starredAt || 0) - (getRecord(a.id).starredAt || 0); });
      } else if (sortMode === "oldest") {
        starredWords.sort(function(a, b) { return (getRecord(a.id).starredAt || 0) - (getRecord(b.id).starredAt || 0); });
      } else if (sortMode === "az") {
        starredWords.sort(function(a, b) { return a.word.localeCompare(b.word); });
      } else if (sortMode === "za") {
        starredWords.sort(function(a, b) { return b.word.localeCompare(a.word); });
      } else if (sortMode === "random") {
        starredWords.sort(function(a, b) { return (((a.seq || 1) * 17) % 31) - (((b.seq || 1) * 17) % 31); });
      }

      if (starredWords.length === 0) {
        box.innerHTML = '<div style="padding:40px 20px; text-align:center; color:var(--text-muted);">生词本暂无单词。在学习列表中点击 ★ 或点击上方「+ 手动添加新单词」即可收藏。</div>';
        return;
      }

      let html = "";
      starredWords.forEach(function(w, idx) {
        const rec = getRecord(w.id);
        html +=
          '<div class="word-row" data-wid="' + w.id + '" data-unfam="' + (rec.unfam || 0) + '">' +
            '<div class="w-idx">' + (idx + 1) + '</div>' +
            '<div class="w-head-col">' +
              '<div class="w-word">' + escapeHtml(w.word) + ' ' + makeUnfamBadgeHtml(rec.unfam || 0) + '</div>' +
              '<div class="w-ipa">' + escapeHtml(getPhoneticString(w)) + '</div>' +
            '</div>' +
            '<div class="w-meaning-col">' +
              '<div class="w-cn">' + escapeHtml(getEffectiveCnDef(w)) + '</div>' +
              (rec.note ? '<div class="w-ex" style="color:var(--amber-mark);">笔记: ' + escapeHtml(rec.note) + '</div>' : '<div class="w-ex">' + escapeHtml(w.ex_en) + '</div>') +
            '</div>' +
            '<div class="w-actions">' +
              '<button class="btn btn-sm" data-act="dict" data-wid="' + w.id + '">词典/编辑</button>' +
              '<button class="icon-btn starred" data-act="star" data-wid="' + w.id + '" title="从生词本移除(恢复原释义)">★</button>' +
            '</div>' +
          '</div>';
      });
      box.innerHTML = html;
    } else {
      document.getElementById("nbStarredControls").style.display = "none";
      document.getElementById("nbMasteredControls").style.display = "flex";
      if (masteredWords.length === 0) {
        box.innerHTML = '<div style="padding:40px 20px; text-align:center; color:var(--text-muted);">熟词表暂无单词。在学习列表中点击 ✕ 可将已熟记的单词移入此处，让词库越背越小。</div>';
        return;
      }
      let html = "";
      masteredWords.forEach(function(w, idx) {
        html +=
          '<div class="word-row" data-wid="' + w.id + '">' +
            '<div class="w-idx">' + (idx + 1) + '</div>' +
            '<div class="w-head-col"><div class="w-word">' + escapeHtml(w.word) + '</div></div>' +
            '<div class="w-meaning-col"><div class="w-cn">' + escapeHtml(w.cn) + '</div></div>' +
            '<div class="w-actions">' +
              '<button class="btn btn-sm" data-act="unmaster" data-wid="' + w.id + '">↺ 恢复</button>' +
            '</div>' +
          '</div>';
      });
      box.innerHTML = html;
    }
  }

  // ==================== 9. ONLINE DICTIONARY INTEGRATION & EDIT MODAL (Requirement 3 & 4) ====================
  function buildOnlineDictUrl(rawWord, dictKey, purpose) {
    const src = ONLINE_DICT_SOURCES[dictKey] || ONLINE_DICT_SOURCES.eudic;
    const template = (purpose === "embed" ? src.embedUrl : src.parseUrl) || src.parseUrl;
    const cleanWord = String(rawWord || "").trim();
    const encodedWord = encodeURIComponent(cleanWord);
    return template.replace("@word@", encodedWord);
  }

  function stripNoise(root) {
    if (!root || !root.querySelectorAll) return;
    root.querySelectorAll("img, script, style, ins, iframe, .dictimgtoword, .guanggao").forEach(function (n) {
      if (n.parentNode) n.parentNode.removeChild(n);
    });
  }

  function parseOnlineDictionaryHtml(htmlText, dictKey, headword) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, "text/html");
    const bodyText = doc.body ? doc.body.textContent : htmlText;
    const lowerText = bodyText.toLowerCase();
    const blocks = [];
    function push(t) {
      const s = String(t == null ? "" : t).replace(/\s+/g, " ").trim();
      if (!s || s.length < 2) return;
      if (blocks.indexOf(s) !== -1) return;
      if (blocks.length >= 12) return;
      blocks.push(s);
    }

    if (dictKey === "eudic") {
      // mdicts puts the 英汉-汉英 gloss in #FCchild (and specialist glosses in #SPECchild).
      // v1.0.3 looked for "#ExpFCChild" — the /dicts/ page's id, with a capital C — which
      // never matched anything, so the panel silently fell back to the boilerplate
      // <meta name="description"> text.
      const primary = ["#FCchild", "#SPECchild", "#FC", "#SPEC"];
      for (let i = 0; i < primary.length && blocks.length === 0; i++) {
        const box = doc.querySelector(primary[i]);
        if (!box) continue;
        stripNoise(box);
        const items = box.querySelectorAll(".exp, li, p");
        if (items.length) {
          items.forEach(function (el) { push(el.textContent); });
        } else {
          push(box.textContent);
        }
      }
      if (blocks.length === 0) {
        doc.querySelectorAll(".expDiv .exp, #FC .exp").forEach(function (el) { push(el.textContent); });
      }
      if (blocks.length === 0) {
        doc.querySelectorAll("#phrase").forEach(function (el) {
          const a = el.querySelector("a");
          const e = el.querySelector(".exp");
          if (a && e) push(a.textContent + " — " + e.textContent);
        });
      }
      // A missing headword still answers 200 but renders the #page-status notice and
      // no #FCchild, so absence of parsed glosses plus that marker is the not-found signal.
      const missingMarker = !!doc.querySelector("#page-status") ||
        /未收录|没有找到|未找到|抱歉|suggest/i.test(bodyText.slice(0, 4000));
      return { notFound: blocks.length === 0 && missingMarker, entries: blocks };
    }

    if (dictKey === "iciba") {
      // iciba renders its entries client-side from an XHR; the served HTML carries no
      // gloss text, so there is nothing to parse. The caller shows the live frame instead.
      return { notFound: false, entries: [], parseable: false };
    }

    // WordReference enzh parser (kept for the injected test fetcher; the live app never
    // frames or fetches this host — see ONLINE_DICT_SOURCES.canEmbed / canFetch).
    if (
      doc.querySelector("#noEntryFound") ||
      lowerText.indexOf("no translation found") !== -1 ||
      lowerText.indexOf("未找到任何翻译") !== -1
    ) {
      return { notFound: true, entries: [] };
    }
    const rows = doc.querySelectorAll("table.WRD tr.even, table.WRD tr.odd");
    rows.forEach(function (tr) {
      const fromW = tr.querySelector(".FrWrd");
      const toW = tr.querySelector(".ToWrd");
      const frEx = tr.querySelector(".FrEx");
      const toEx = tr.querySelector(".ToEx");
      if (fromW || toW) {
        push((fromW ? fromW.textContent : "") + " → " + (toW ? toW.textContent : ""));
      } else if (frEx || toEx) {
        push("例: " + (frEx ? frEx.textContent : "") + " " + (toEx ? toEx.textContent : ""));
      }
    });
    if (blocks.length === 0) {
      const art = doc.querySelector("#articleWRD");
      if (art) push(art.textContent);
    }
    return { notFound: blocks.length === 0, entries: blocks };
  }

  function queryOnlineDictionaryForModal(w) {
    if (!w) return;
    if (currentDictAbortCtrl) {
      try { currentDictAbortCtrl.abort(); } catch (e) {}
    }

    const dictKey = VALID_ONLINE_DICTS.indexOf(state.settings.onlineDict) !== -1 ? state.settings.onlineDict : "eudic";
    const dictCfg = ONLINE_DICT_SOURCES[dictKey];
    const parseUrl = buildOnlineDictUrl(w.word, dictKey, "parse");
    const embedUrl = dictCfg.canEmbed ? buildOnlineDictUrl(w.word, dictKey, "embed") : "";
    const pageUrl = dictCfg.embedUrl && dictCfg.embedUrl !== dictCfg.parseUrl ? parseUrl : parseUrl;

    document.getElementById("modalActiveDictBadge").textContent = dictCfg.name;
    document.getElementById("modalDictUrlCode").textContent = parseUrl;
    document.getElementById("modalDictExternalLink").href = parseUrl;

    document.querySelectorAll("#modalDictSourceGroup .seg-btn").forEach(function(btn) {
      btn.classList.toggle("active", btn.dataset.dict === dictKey);
    });

    const statusBanner = document.getElementById("modalDictStatusBanner");
    const parsedBox = document.getElementById("modalDictParsedContent");
    const iframeWrap = document.getElementById("modalDictIframeWrap");
    const iframeEl = document.getElementById("modalOnlineDictIframe");

    function clearFrame() {
      iframeWrap.classList.remove("dict-frame-visible");
      iframeWrap.style.display = "none";
      iframeEl.src = "about:blank";
    }
    function showFrame(url) {
      iframeEl.src = url;
      iframeWrap.style.display = "";
      iframeWrap.classList.add("dict-frame-visible");
    }
    function localRefHtml() {
      return '<div style="margin-top:8px; padding-top:8px; border-top:1px dashed var(--border-color);">' +
        '<strong>📚 本地离线词库基础参考（非在线返回结果）</strong>：<br>' +
        '<span>单词：<strong>' + escapeHtml(w.word) + '</strong> ' + escapeHtml(getPhoneticString(w)) + '</span><br>' +
        '<span>本地释义：' + escapeHtml(w.cn) + '</span>' +
      '</div>';
    }

    // Reset view to loading state (never leave a stale frame or a blank box on screen)
    clearFrame();
    statusBanner.className = "dict-status-banner dict-status-loading";
    statusBanner.textContent = "⏳ 正在查询【" + dictCfg.name + "】词条“" + w.word + "”...";
    parsedBox.innerHTML = '<div class="dict-parsed-hint">正在连接远程词典服务，请稍候...</div>';

    function renderFallbackFailure(reasonText) {
      clearFrame();
      statusBanner.className = "dict-status-banner dict-status-error";
      statusBanner.textContent = "⚠️ 未能获取【" + dictCfg.name + "】在线内容：" + reasonText;
      parsedBox.innerHTML =
        '<div class="dict-parsed-note">' +
          '<div class="dict-parsed-warn">在线词典未返回内容（空白页与失败状态一律不记为查询成功）：</div>' +
          '<div>• <strong>目标地址</strong>：<code>' + escapeHtml(parseUrl) + '</code></div>' +
          '<div>• <strong>失败原因</strong>：' + escapeHtml(reasonText) + '</div>' +
          localRefHtml() +
        '</div>';
    }

    function renderNotFoundState() {
      clearFrame();
      statusBanner.className = "dict-status-banner dict-status-warn";
      statusBanner.textContent = "⚠️ 词条不存在：【" + dictCfg.name + "】未收录单词“" + w.word + "”";
      parsedBox.innerHTML =
        '<div class="dict-parsed-note">' +
          '<div>在线词典已响应，但未查询到匹配“<strong>' + escapeHtml(w.word) + '</strong>”的词条。可检查拼写，或切换其他在线词典重试。</div>' +
          localRefHtml() +
        '</div>';
    }

    function renderParsedSuccess(entries) {
      statusBanner.className = "dict-status-banner dict-status-ok";
      statusBanner.textContent = "✓ 已获取【" + dictCfg.name + "】中“" + w.word + "”的词典释义" +
        (embedUrl ? "，并在下方内嵌原站词典页" : "");
      let listHtml = '<div class="dict-parsed-title">📖 ' + escapeHtml(dictCfg.name) + ' — ' + escapeHtml(w.word) + ' 词条释义：</div>';
      entries.forEach(function (item, idx) {
        listHtml += '<div class="dict-parsed-item">' + (idx + 1) + '. ' + escapeHtml(item) + '</div>';
      });
      parsedBox.innerHTML = listHtml;
      if (embedUrl) { showFrame(embedUrl); } else { clearFrame(); }
    }

    // The site renders entries client-side, so Voca shows the live page and says so plainly
    // instead of inventing a "parsed" success it cannot substantiate.
    function renderEmbedOnly() {
      statusBanner.className = "dict-status-banner dict-status-info";
      statusBanner.textContent = "ℹ 已内嵌【" + dictCfg.name + "】词条页面（该站释义由脚本渲染，Voca 不抓取其文本）";
      parsedBox.innerHTML =
        '<div class="dict-parsed-note"><div>下方为 <code>' + escapeHtml(embedUrl) + '</code> 的实时页面。' +
        '若页面未显示，多为该站当日限流，可点右上角「↗ 浏览器打开源页面」。</div>' + localRefHtml() + '</div>';
      showFrame(embedUrl);
    }

    // WordReference answers 200 with x-frame-options: SAMEORIGIN plus a CSP frame-ancestors
    // allowlist that does not include Voca, and it has no CORS headers. Framing and fetching
    // are both impossible, so the only honest state is "open it yourself" — never a green tick.
    function renderOpenOnly(reason) {
      clearFrame();
      statusBanner.className = "dict-status-banner dict-status-warn";
      statusBanner.textContent = "⚠ 【" + dictCfg.name + "】无法在 Voca 窗口内显示，仅能跳转到源站";
      parsedBox.innerHTML =
        '<div class="dict-parsed-note">' +
          '<div class="dict-parsed-warn">' + escapeHtml(reason) + '</div>' +
          '<div style="margin-top:6px;">• 源站地址：<code>' + escapeHtml(parseUrl) + '</code></div>' +
          '<div style="margin-top:6px;">• 请点右上角 <strong>「↗ 浏览器打开源页面」</strong> 在新标签页查看全文。' +
          '首次访问该站需通过其反爬校验，若提示 403/418 请稍后重试或更换网络。</div>' +
          localRefHtml() +
        '</div>';
    }

    if (typeof window.__VOCA_ONLINE_DICT_FETCHER__ === "function") {
      Promise.resolve()
        .then(function() {
          return window.__VOCA_ONLINE_DICT_FETCHER__(parseUrl, dictKey, w.word);
        })
        .then(function(res) {
          if (!res || res.ok === false) {
            renderFallbackFailure((res && res.error) || "网络请求失败或服务器未响应");
            return;
          }
          if (res.status === 404) {
            renderNotFoundState();
            return;
          }
          const parsed = parseOnlineDictionaryHtml(res.html || "", dictKey, w.word);
          if (parsed.notFound) {
            renderNotFoundState();
          } else if (parsed.parseable === false || !parsed.entries.length) {
            renderEmbedOnly();
          } else {
            renderParsedSuccess(parsed.entries);
          }
        })
        .catch(function(err) {
          renderFallbackFailure("请求异常 (" + (err && err.message ? err.message : "Network Error") + ")");
        });
      return;
    }

    if (typeof navigator !== "undefined" && navigator.onLine === false) {
      renderFallbackFailure("当前设备处于离线状态 (navigator.onLine = false)，无法连接外部在线词典服务器。");
      return;
    }

    if (!dictCfg.canFetch) {
      renderOpenOnly(dictCfg.name + " 的响应头声明了 frame-ancestors 白名单与 SAMEORIGIN，且不开放跨域读取，" +
                     "因此词条内容无法在 Voca 窗口内呈现。");
      return;
    }

    if (typeof AbortController !== "undefined") {
      currentDictAbortCtrl = new AbortController();
    }
    const signal = currentDictAbortCtrl ? currentDictAbortCtrl.signal : undefined;
    const timeoutId = setTimeout(function() {
      if (currentDictAbortCtrl) {
        try { currentDictAbortCtrl.abort(); } catch (e) {}
      }
    }, 9000);

    fetch(parseUrl, { method: "GET", mode: "cors", credentials: "omit", signal: signal })
      .then(function(resp) {
        clearTimeout(timeoutId);
        if (resp.status === 404) {
          renderNotFoundState();
          return null;
        }
        if (!resp.ok) {
          throw new Error("HTTP " + resp.status);
        }
        return resp.text();
      })
      .then(function(htmlText) {
        if (htmlText === null) return;
        const parsed = parseOnlineDictionaryHtml(htmlText, dictKey, w.word);
        if (parsed.parseable === false) {
          renderEmbedOnly();
        } else if (parsed.notFound) {
          renderNotFoundState();
        } else if (!parsed.entries.length) {
          // Page answered but yielded no gloss and no explicit "missing" marker: say so
          // rather than showing an empty box under a green tick.
          renderEmbedOnly();
        } else {
          renderParsedSuccess(parsed.entries);
        }
      })
      .catch(function(err) {
        clearTimeout(timeoutId);
        const why = err && /abort/i.test(err.name || "")
          ? "请求超时或被取消"
          : "跨域策略 (CORS) 拒绝读取，或该词典服务器当前无法访问";
        renderFallbackFailure(why);
      });
  }

  function openDictModal(wordId) {
    const w = wordLookupById[wordId];
    if (!w) return;
    currentModalWordId = wordId;
    const rec = getRecord(wordId);

    document.getElementById("modalDictWord").textContent = w.word;
    document.getElementById("modalDictIpa").textContent = getPhoneticString(w);
    document.getElementById("modalEditCnInput").value = getEffectiveCnDef(w);
    document.getElementById("modalEditNoteInput").value = rec.note || "";
    document.getElementById("modalUnfamVal").textContent = String(rec.unfam || 0);

    document.getElementById("dictModal").classList.add("open");
    queryOnlineDictionaryForModal(w);
    speakText(w.word);
  }

  // ==================== 10. MULTI-PAGE PDF EXPORT, PRINT & HTML EXPORT ====================
  function parseCustomTextLines(rawText) {
    const lines = rawText.split(/\r?\n/).map(function(l) { return l.trim(); }).filter(Boolean);
    let added = 0;
    lines.forEach(function(line, idx) {
      if (idx === 0 && /^(word|id)[,;\t]/i.test(line)) return;
      const parts = line.indexOf("\t") !== -1 ? line.split("\t") : line.split(",");
      if (parts.length < 2) return;
      const spell = (parts[0] || "").trim();
      if (!spell) return;
      const ipa = parts.length >= 3 ? (parts[1] || "").trim() : "/-/";
      const cn = parts.length >= 3 ? (parts[2] || "").trim() : (parts[1] || "").trim();
      const exEn = (parts[3] || ("Context example for " + spell + ".")).trim();
      const exCn = (parts[4] || "").trim();
      const tip = (parts[5] || "用户自定义导入词条").trim();

      const newId = "custom_" + Date.now() + "_" + (state.customWords.length + added + 1);
      const wObj = {
        id: newId,
        seq: 50000 + state.customWords.length + added + 1,
        word: spell,
        uk: ipa,
        us: ipa,
        cn: cn,
        ex_en: exEn,
        ex_cn: exCn,
        tip: tip,
        books: ["custom"],
        freq: 5
      };
      state.customWords.push(wObj);
      wordLookupById[newId] = wObj;
      added++;
    });
    if (added > 0) {
      rebuildCustomBookCache();
      state.currentBook = "custom";
      document.getElementById("bookSelect").value = "custom";
      saveState();
      refreshAllViews();
      showToast("成功导入 " + added + " 个自定义词条！");
    } else {
      showToast("未识别到有效词条，请检查每行格式：单词, 音标, 释义");
    }
  }

  function openPrintPreviewModal(title, bodyHtml, docData) {
    lastPrintTitle = title;
    lastPrintHtmlContent = bodyHtml;
    lastPrintDocData = docData || null;
    document.getElementById("printModalTitle").textContent = title;
    const estPages = docData ? Math.max(1, Math.ceil(docData.rows.length / docData.rowsPerPage)) : 1;
    document.getElementById("printModalMeta").textContent =
      "共 " + (docData ? docData.rows.length : 0) + " 行记录 · 预计 A4 分页 " + estPages + " 页（支持完整多页 PDF 导出、系统打印与 HTML 导出）";
    document.getElementById("printSheetBody").innerHTML = bodyHtml;
    document.getElementById("dedicatedPrintRoot").innerHTML = bodyHtml;
    document.getElementById("printModal").classList.add("open");
  }

  function buildPrintableScheduleHtml() {
    buildListsForCurrentBook();
    const sched = computeCustomEbbinghausSchedule();
    const N = sched.N;
    const D = sched.D;
    const intervals = sched.intervals;
    const subtitle = "词库: " + state.currentBook.toUpperCase() + " · 自定义 List 数: " + N + " 组 · 自定义学习周期: " + D + " 天 · 复习间隔: " + intervals.map(function(g) { return "+" + g + "天"; }).join("/");

    const headers = [
      "天数",
      "初记新学",
      "复习1 (+" + intervals[0] + "天)",
      "复习2 (+" + intervals[1] + "天)",
      "复习3 (+" + intervals[2] + "天)",
      "复习4 (+" + intervals[3] + "天)",
      "复习5 (+" + intervals[4] + "天)",
      "完成状态 / 打卡签名"
    ];
    const colWidths = [0.09, 0.14, 0.12, 0.12, 0.12, 0.12, 0.12, 0.17];
    const pdfRows = [];

    let html =
      '<div class="print-doc-wrap" style="padding:6px;">' +
      '<h2 style="text-align:center; margin-bottom:4px; font-size:1.25rem;">Voca v1.0.4 自定义艾宾浩斯背单词计划表</h2>' +
      '<p style="text-align:center; color:#475569; font-size:0.82rem; margin-bottom:12px;">' + escapeHtml(subtitle) + '</p>' +
      '<table style="width:100%; border-collapse:collapse; font-size:0.80rem;" border="1" cellspacing="0" cellpadding="6">' +
      '<thead><tr style="background:#F1F5F9;">' +
      headers.map(function(h) { return '<th>' + escapeHtml(h) + '</th>'; }).join("") +
      '</tr></thead><tbody>';

    sched.rows.forEach(function(row) {
      const nw = row.newLists.length ? row.newLists.map(function(n) { return (isListCompleted(n) ? "✓ " : "") + "List " + n; }).join(", ") : "—";
      const revs = row.revCols.map(function(col) {
        return col.length ? col.map(function(n) { return (isListCompleted(n) ? "✓ " : "") + "List " + n; }).join(", ") : "—";
      });
      const allListsToday = row.newLists.concat(row.revCols[0], row.revCols[1], row.revCols[2], row.revCols[3], row.revCols[4]);
      const doneCnt = allListsToday.filter(function(n) { return isListCompleted(n); }).length;
      const statusStr = allListsToday.length ? (doneCnt + "/" + allListsToday.length + (doneCnt === allListsToday.length ? " ✓已完成" : " [   ]")) : "—";

      pdfRows.push(["Day " + row.day, nw, revs[0], revs[1], revs[2], revs[3], revs[4], statusStr]);

      html +=
        '<tr><td style="text-align:center; font-weight:700;">Day ' + row.day + '</td>' +
        '<td style="text-align:center;">' + escapeHtml(nw) + '</td>' +
        revs.map(function(r) { return '<td style="text-align:center;">' + escapeHtml(r) + '</td>'; }).join("") +
        '<td style="text-align:center;">' + escapeHtml(statusStr) + '</td></tr>';
    });

    html += '</tbody></table></div>';

    return {
      html: html,
      docData: {
        title: "Voca v1.0.4 自定义艾宾浩斯背单词计划表",
        subtitle: subtitle,
        headers: headers,
        colWidths: colWidths,
        rows: pdfRows,
        rowsPerPage: 26
      }
    };
  }

  function buildPrintableWordListHtml(wordsArr, title, quizMode) {
    const fullList = wordsArr.slice();
    const subtitle = "词库: " + state.currentBook.toUpperCase() + " · 共 " + fullList.length + " 词 · 生成自 Voca v1.0.4 离线背单词工坊";
    const headers = ["序号", "英文单词", "国际音标 (IPA)", "中文释义与词性", "不会程度"];
    const colWidths = [0.07, 0.22, 0.20, 0.41, 0.10];
    const pdfRows = [];

    let html =
      '<div class="print-doc-wrap" style="padding:6px;">' +
      '<h2 style="text-align:center; margin-bottom:4px; font-size:1.25rem;">' + escapeHtml(title) + '</h2>' +
      '<p style="text-align:center; color:#475569; font-size:0.82rem; margin-bottom:12px;">' + escapeHtml(subtitle) + '</p>' +
      '<table style="width:100%; border-collapse:collapse; font-size:0.82rem;" border="1" cellspacing="0" cellpadding="6">' +
      '<thead><tr style="background:#F1F5F9;">' +
      '<th style="width:46px;">序号</th><th style="width:155px;">英文单词</th><th style="width:135px;">国际音标 (IPA)</th><th>中文释义与词性</th><th style="width:72px;">不会程度</th>' +
      '</tr></thead><tbody>';

    fullList.forEach(function(w, i) {
      const rec = getRecord(w.id);
      const wordText = quizMode ? "____________________" : w.word;
      const ipaText = getPhoneticString(w);
      const cnText = quizMode ? "________________________________________" : getEffectiveCnDef(w);
      const unfamText = quizMode ? "[   / 5 ]" : ((rec.unfam || 0) + " / 5");

      pdfRows.push([String(i + 1), wordText, ipaText, cnText, unfamText]);

      html +=
        '<tr><td style="text-align:center;">' + (i + 1) + '</td>' +
        '<td style="font-weight:700;">' + escapeHtml(wordText) + '</td>' +
        '<td>' + escapeHtml(ipaText) + '</td>' +
        '<td>' + escapeHtml(cnText) + '</td>' +
        '<td style="text-align:center;">' + escapeHtml(unfamText) + '</td></tr>';
    });

    html += '</tbody></table></div>';

    return {
      html: html,
      docData: {
        title: title,
        subtitle: subtitle,
        headers: headers,
        colWidths: colWidths,
        rows: pdfRows,
        rowsPerPage: 25
      }
    };
  }

  function generateMultiPagePdfBinary(docData) {
    const PAGE_W_PX = 1240;
    const PAGE_H_PX = 1754;
    const MARGIN_X = 64;
    const MARGIN_TOP = 68;
    const MARGIN_BOTTOM = 72;
    const CONTENT_W = PAGE_W_PX - MARGIN_X * 2;

    const allRows = (docData && docData.rows && docData.rows.length > 0)
      ? docData.rows
      : [["1", "—", "—", "暂无数据记录", "—"]];
    const headers = (docData && docData.headers) || ["序号", "项目", "内容"];
    const colWidths = (docData && docData.colWidths) || headers.map(function() { return 1 / headers.length; });

    const measureCanvas = document.createElement("canvas");
    measureCanvas.width = 200;
    measureCanvas.height = 50;
    const mCtx = measureCanvas.getContext("2d");
    const fontStack = "'VocaSans', 'VocaSansCJK', 'Noto Sans CJK SC', sans-serif";

    function wrapTextLines(ctx, text, maxW) {
      const s = String(text || "");
      if (!s) return [""];
      const lines = [];
      let cur = "";
      for (let i = 0; i < s.length; i++) {
        const ch = s[i];
        const test = cur + ch;
        if (ctx.measureText(test).width > maxW && cur.length > 0) {
          lines.push(cur);
          cur = ch;
        } else {
          cur = test;
        }
      }
      if (cur) lines.push(cur);
      return lines.slice(0, 3);
    }

    mCtx.font = "500 18px " + fontStack;
    const colPxWidths = colWidths.map(function(w) { return Math.floor(w * CONTENT_W); });
    const diffW = CONTENT_W - colPxWidths.reduce(function(a, b) { return a + b; }, 0);
    colPxWidths[colPxWidths.length - 1] += diffW;

    const pages = [];
    let currentPageRows = [];
    const FIRST_PAGE_TABLE_TOP = MARGIN_TOP + 102;
    const NEXT_PAGE_TABLE_TOP = MARGIN_TOP + 54;
    const TABLE_HEADER_H = 42;
    const MAX_Y = PAGE_H_PX - MARGIN_BOTTOM;

    let curY = FIRST_PAGE_TABLE_TOP + TABLE_HEADER_H;

    allRows.forEach(function(rowCells) {
      let maxLines = 1;
      const wrappedCells = rowCells.map(function(cellText, cIdx) {
        const lines = wrapTextLines(mCtx, cellText, colPxWidths[cIdx] - 18);
        if (lines.length > maxLines) maxLines = lines.length;
        return lines;
      });
      const rowH = Math.max(38, maxLines * 23 + 14);

      if (curY + rowH > MAX_Y && currentPageRows.length > 0) {
        pages.push(currentPageRows);
        currentPageRows = [];
        curY = NEXT_PAGE_TABLE_TOP + TABLE_HEADER_H;
      }
      currentPageRows.push({
        wrappedCells: wrappedCells,
        rowH: rowH
      });
      curY += rowH;
    });
    if (currentPageRows.length > 0 || pages.length === 0) {
      pages.push(currentPageRows);
    }

    const totalPages = pages.length;
    const jpegBytesPerPage = [];

    for (let pIdx = 0; pIdx < totalPages; pIdx++) {
      const canvas = document.createElement("canvas");
      canvas.width = PAGE_W_PX;
      canvas.height = PAGE_H_PX;
      const ctx = canvas.getContext("2d");

      ctx.fillStyle = "#FFFFFF";
      ctx.fillRect(0, 0, PAGE_W_PX, PAGE_H_PX);

      let tableTop = NEXT_PAGE_TABLE_TOP;
      if (pIdx === 0) {
        tableTop = FIRST_PAGE_TABLE_TOP;
        ctx.fillStyle = "#0F172A";
        ctx.font = "800 30px " + fontStack;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(docData.title || "Voca 导出文档", PAGE_W_PX / 2, MARGIN_TOP);

        ctx.fillStyle = "#475569";
        ctx.font = "500 18px " + fontStack;
        ctx.fillText(docData.subtitle || "", PAGE_W_PX / 2, MARGIN_TOP + 44);
      } else {
        ctx.fillStyle = "#475569";
        ctx.font = "700 18px " + fontStack;
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText((docData.title || "Voca") + " （续表）", MARGIN_X, MARGIN_TOP + 12);
      }

      let xCursor = MARGIN_X;
      ctx.fillStyle = "#F1F5F9";
      ctx.fillRect(MARGIN_X, tableTop, CONTENT_W, TABLE_HEADER_H);
      ctx.strokeStyle = "#94A3B8";
      ctx.lineWidth = 1.5;

      for (let cIdx = 0; cIdx < headers.length; cIdx++) {
        const cw = colPxWidths[cIdx];
        ctx.strokeRect(xCursor, tableTop, cw, TABLE_HEADER_H);
        ctx.fillStyle = "#0F172A";
        ctx.font = "700 18px " + fontStack;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(headers[cIdx], xCursor + cw / 2, tableTop + TABLE_HEADER_H / 2);
        xCursor += cw;
      }

      let yCursor = tableTop + TABLE_HEADER_H;
      const pageRows = pages[pIdx];
      pageRows.forEach(function(rObj, rIdx) {
        const rh = rObj.rowH;
        if (rIdx % 2 === 1) {
          ctx.fillStyle = "#F8FAFC";
          ctx.fillRect(MARGIN_X, yCursor, CONTENT_W, rh);
        }
        let rx = MARGIN_X;
        for (let cIdx = 0; cIdx < rObj.wrappedCells.length; cIdx++) {
          const cw = colPxWidths[cIdx];
          ctx.strokeStyle = "#CBD5E1";
          ctx.lineWidth = 1;
          ctx.strokeRect(rx, yCursor, cw, rh);

          const lines = rObj.wrappedCells[cIdx];
          ctx.fillStyle = "#0F172A";
          ctx.font = (cIdx === 1 ? "700 " : "500 ") + "17px " + fontStack;
          const isCenter = (cIdx === 0 || cIdx === rObj.wrappedCells.length - 1 || headers.length >= 7);
          ctx.textAlign = isCenter ? "center" : "left";
          ctx.textBaseline = "top";

          const blockH = lines.length * 22;
          let lineY = yCursor + Math.max(6, (rh - blockH) / 2);
          lines.forEach(function(ln) {
            const tx = isCenter ? (rx + cw / 2) : (rx + 9);
            ctx.fillText(ln, tx, lineY);
            lineY += 22;
          });
          rx += cw;
        }
        yCursor += rh;
      });

      ctx.fillStyle = "#64748B";
      ctx.font = "600 16px " + fontStack;
      ctx.textAlign = "center";
      ctx.textBaseline = "bottom";
      ctx.fillText(
        "Voca v1.0.4 离线艾宾浩斯背单词工坊  ·  第 " + (pIdx + 1) + " / " + totalPages + " 页",
        PAGE_W_PX / 2,
        PAGE_H_PX - 26
      );

      const dataUrl = canvas.toDataURL("image/jpeg", 0.90);
      const b64 = dataUrl.split(",")[1];
      const binStr = atob(b64);
      const u8 = new Uint8Array(binStr.length);
      for (let i = 0; i < binStr.length; i++) {
        u8[i] = binStr.charCodeAt(i);
      }
      jpegBytesPerPage.push(u8);
    }

    const chunks = [];
    let byteOffset = 0;
    const xrefOffsets = [0];

    function pushAscii(str) {
      const u8 = new Uint8Array(str.length);
      for (let i = 0; i < str.length; i++) {
        u8[i] = str.charCodeAt(i) & 0xff;
      }
      chunks.push(u8);
      byteOffset += u8.length;
    }

    function pushBytes(u8) {
      chunks.push(u8);
      byteOffset += u8.length;
    }

    pushAscii("%PDF-1.4\n%\xE2\xE3\xCF\xD3\n");

    xrefOffsets[1] = byteOffset;
    pushAscii("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n");

    const kidsRefs = [];
    for (let i = 0; i < totalPages; i++) {
      kidsRefs.push((3 + i * 3) + " 0 R");
    }
    xrefOffsets[2] = byteOffset;
    pushAscii("2 0 obj\n<< /Type /Pages /Kids [ " + kidsRefs.join(" ") + " ] /Count " + totalPages + " >>\nendobj\n");

    for (let i = 0; i < totalPages; i++) {
      const pageObjId = 3 + i * 3;
      const contentObjId = 4 + i * 3;
      const imgObjId = 5 + i * 3;
      const jpg = jpegBytesPerPage[i];
      const imgName = "/Im" + i;

      xrefOffsets[pageObjId] = byteOffset;
      pushAscii(
        pageObjId + " 0 obj\n" +
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] " +
        "/Resources << /XObject << " + imgName + " " + imgObjId + " 0 R >> >> " +
        "/Contents " + contentObjId + " 0 R >>\nendobj\n"
      );

      const contentCmd = "q\n595.28 0 0 841.89 0 0 cm\n" + imgName + " Do\nQ\n";
      xrefOffsets[contentObjId] = byteOffset;
      pushAscii(
        contentObjId + " 0 obj\n<< /Length " + contentCmd.length + " >>\nstream\n" +
        contentCmd + "endstream\nendobj\n"
      );

      xrefOffsets[imgObjId] = byteOffset;
      pushAscii(
        imgObjId + " 0 obj\n" +
        "<< /Type /XObject /Subtype /Image /Width " + PAGE_W_PX + " /Height " + PAGE_H_PX +
        " /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length " + jpg.length + " >>\nstream\n"
      );
      pushBytes(jpg);
      pushAscii("\nendstream\nendobj\n");
    }

    const totalObjs = 2 + totalPages * 3 + 1;
    const xrefStart = byteOffset;
    pushAscii("xref\n0 " + totalObjs + "\n0000000000 65535 f \n");
    for (let id = 1; id < totalObjs; id++) {
      const offStr = String(xrefOffsets[id]).padStart(10, "0");
      pushAscii(offStr + " 00000 n \n");
    }
    pushAscii(
      "trailer\n<< /Size " + totalObjs + " /Root 1 0 R >>\nstartxref\n" +
      xrefStart + "\n%%EOF\n"
    );

    const outPdf = new Uint8Array(byteOffset);
    let pos = 0;
    for (let i = 0; i < chunks.length; i++) {
      outPdf.set(chunks[i], pos);
      pos += chunks[i].length;
    }

    return {
      pdfBytes: outPdf,
      pageCount: totalPages,
      totalRows: allRows.length
    };
  }

  function isTouchShellUi() {
    return !!(window.__VOCA_IS_TOUCH__ && window.__VOCA_IS_TOUCH__());
  }

  function showTouchExport(filename, text, mimeType) {
    const box = document.getElementById("touchExportBox");
    const area = document.getElementById("touchExportTextarea");
    if (!box || !area) return false;
    document.getElementById("touchExportName").textContent = filename;
    document.getElementById("touchExportKind").textContent = mimeType || "text/plain";
    area.value = text;
    box.style.display = "block";
    box.scrollIntoView({ block: "start" });
    return true;
  }

  /* The shipped Android WebView installs no DownloadListener, so a[download] is a silent
     no-op there. Fire it anyway (a real mobile browser still saves the file) and always
     mirror text payloads into the copy-out box on the touch shell. */
  function downloadFileBlob(filename, contentData, mimeType) {
    const type = mimeType || "text/plain;charset=utf-8";
    let outcome = "file";
    if (isTouchShellUi()) {
      const copyable = typeof contentData === "string" &&
        /^(application\/json|text\/csv|text\/plain)/.test(type);
      if (!copyable) {
        showToast("Android 版无法保存该文件，请在 Windows 版导出；备份可改用「导出完整学习备份 (.json)」");
        return "blocked";
      }
      if (contentData.length > 2000000) {
        showToast("内容约 " + Math.round(contentData.length / 1024) + " KB，超出 Android 版可复制上限，请在 Windows 版导出");
        return "blocked";
      }
      showTouchExport(filename, contentData, type);
      outcome = "copy";
    }
    const blob = new Blob([contentData], { type: type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function() {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 200);
    return outcome;
  }

  function announceExport(outcome, filename, desktopMsg) {
    if (outcome === "blocked") return;
    if (outcome === "copy") showToast("已生成 " + filename + "，请在「导出内容」框复制保存");
    else showToast(desktopMsg);
  }

  function updateStorageDiagnostics() {
    const box = document.getElementById("storageDiagnosticBox");
    if (!box) return;
    const recCount = Object.keys(state.records || {}).length;
    const customCount = (state.customWords || []).length;
    const dictName = (ONLINE_DICT_SOURCES[state.settings.onlineDict] || ONLINE_DICT_SOURCES.eudic).name;
    box.textContent =
      "本地双引擎状态：LocalStorage (已同步) · IndexedDB VocaDB_v1 (已同步) · Schema v1.0.4 · 内置词条 38,855 条 · 学习记录 " +
      recCount + " 条 · 自定义词条 " + customCount + " 条 · 在线词典: " + dictName;
  }

  function applySettingsToDOM() {
    let theme = state.settings.theme || "daylight";
    if (VALID_THEMES.indexOf(theme) === -1) {
      theme = "oled";
      state.settings.theme = "oled";
    }
    const fontScale = state.settings.fontScale || "standard";
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-font", fontScale);

    const themeNames = { daylight: "晨曦白", oled: "纯黑OLED", paper: "羊皮纸" };
    document.getElementById("quickThemeBtn").textContent = "主题: " + (themeNames[theme] || "晨曦白");

    document.getElementById("bookSelect").value = state.currentBook;
    document.getElementById("sortSelect").value = state.intraSort;
    document.getElementById("settingOnlineDict").value = state.settings.onlineDict || "eudic";
    document.getElementById("settingRowClickMode").value = state.settings.rowClickMode || "unfam_lr";
    document.getElementById("settingAccentMode").value = state.settings.accent;
    document.getElementById("settingPhoneticDisplay").value = state.settings.phoneticDisplay;
    document.getElementById("settingThemeSelect").value = theme;
    document.getElementById("settingFontScale").value = fontScale;
    document.getElementById("settingSoundFxToggle").checked = !!state.settings.soundFx;

    document.querySelectorAll("#langModeGroup .seg-btn").forEach(function(b) {
      b.classList.toggle("active", b.dataset.lang === state.langMode);
    });
    document.querySelectorAll("#layoutModeGroup .seg-btn").forEach(function(b) {
      b.classList.toggle("active", b.dataset.layout === state.layoutMode);
    });

    const touchShell = !!(window.__VOCA_IS_TOUCH__ && window.__VOCA_IS_TOUCH__());
    const clickHints = {
      unfam_lr: touchShell ? "轻触单词行：不会程度+1并发音 · 长按：不会程度-1"
                           : "左键/轻触单词行：不会程度+1并发音 · 右键点击：不会程度-1",
      left_sound_right_unfam: touchShell ? "点击左半部：仅发音 · 右半部：不会程度+1 · 长按：不会程度-1"
                                         : "点击左半部：仅发音 · 右半部：不会程度+1 · 右键：不会程度-1",
      right_sound_left_unfam: touchShell ? "点击右半部：仅发音 · 左半部：不会程度+1 · 长按：不会程度-1"
                                         : "点击右半部：仅发音 · 左半部：不会程度+1 · 右键：不会程度-1",
      sound_only: "点击单词行：仅朗读发音（不改变不会程度）"
    };
    document.getElementById("clickRuleHint").textContent = clickHints[state.settings.rowClickMode] || clickHints.unfam_lr;
  }

  function refreshAllViews() {
    renderLearnView();
    renderEbbinghausPlan();
    renderNotebookView();
    initSpellingSession(false);
    renderAutoScrollList();
    updateStorageDiagnostics();
  }

  function escapeHtml(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // ==================== 11. EVENT LISTENERS ====================
  function bindEvents() {
    function switchTab(tabId) {
      document.querySelectorAll(".view-section").forEach(function(sec) {
        sec.classList.toggle("active", sec.id === "view-" + tabId);
      });
      document.querySelectorAll("#desktopNav .nav-btn, #mobileNav .mob-nav-btn").forEach(function(btn) {
        btn.classList.toggle("active", btn.dataset.tab === tabId);
      });
      if (tabId !== "train") {
        toggleAutoScroll(true);
      }
      refreshAllViews();
    }

    document.getElementById("desktopNav").addEventListener("click", function(e) {
      const btn = e.target.closest(".nav-btn");
      if (btn && btn.dataset.tab) switchTab(btn.dataset.tab);
    });
    document.getElementById("mobileNav").addEventListener("click", function(e) {
      const btn = e.target.closest(".mob-nav-btn");
      if (btn && btn.dataset.tab) switchTab(btn.dataset.tab);
    });

    document.getElementById("btnDismissModeBanner").addEventListener("click", function() {
      document.getElementById("modeFirstTimeBanner").classList.remove("visible");
    });

    document.getElementById("bookSelect").addEventListener("change", function(e) {
      state.currentBook = e.target.value;
      state.currentListIndex = 0;
      listRenderLimit = 120;
      cardCursor = 0;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      saveState();
      refreshAllViews();
    });

    document.getElementById("listSelect").addEventListener("change", function(e) {
      state.currentListIndex = parseInt(e.target.value, 10) || 0;
      listRenderLimit = 120;
      cardCursor = 0;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      saveState();
      refreshAllViews();
    });

    document.getElementById("langModeGroup").addEventListener("click", function(e) {
      const btn = e.target.closest(".seg-btn");
      if (!btn || VALID_LANG_MODES.indexOf(btn.dataset.lang) === -1) return;
      state.langMode = btn.dataset.lang;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      document.querySelectorAll("#langModeGroup .seg-btn").forEach(function(b) {
        b.classList.toggle("active", b.dataset.lang === state.langMode);
      });
      saveState();
      triggerModeFirstTimeHintIfNeeded(state.langMode);
      renderLearnView();
    });

    document.getElementById("layoutModeGroup").addEventListener("click", function(e) {
      const btn = e.target.closest(".seg-btn");
      if (!btn) return;
      state.layoutMode = btn.dataset.layout;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      document.querySelectorAll("#layoutModeGroup .seg-btn").forEach(function(b) {
        b.classList.toggle("active", b.dataset.layout === state.layoutMode);
      });
      saveState();
      triggerModeFirstTimeHintIfNeeded(state.langMode);
      renderLearnView();
    });

    document.getElementById("sortSelect").addEventListener("change", function(e) {
      state.intraSort = e.target.value;
      saveState();
      renderLearnView();
    });

    document.getElementById("quickThemeBtn").addEventListener("click", function() {
      const idx = (VALID_THEMES.indexOf(state.settings.theme) + 1) % VALID_THEMES.length;
      state.settings.theme = VALID_THEMES[idx];
      applySettingsToDOM();
      saveState();
    });

    document.getElementById("wordSearchInput").addEventListener("input", function() {
      listRenderLimit = 120;
      renderLearnView();
    });

    document.getElementById("btnLoadMoreWords").addEventListener("click", function() {
      listRenderLimit += 150;
      renderLearnView();
    });
    document.getElementById("btnShowAllWordsInList").addEventListener("click", function() {
      listRenderLimit = 100000;
      renderLearnView();
    });

    function updateRowUnfamDOM(row, rec) {
      row.setAttribute("data-unfam", String(rec.unfam || 0));
      const badge = row.querySelector(".unfam-badge");
      if (badge) {
        badge.outerHTML = makeUnfamBadgeHtml(rec.unfam || 0);
      }
    }

    // Left-click handler on Word Rows (Requirement 2: Manages Unfamiliarity 不会程度 +1)
    function handleWordListLeftClick(e) {
      // Android synthesises a click after a long press; swallowing that echo is what keeps
      // "hold to lower" from immediately raising the same word back up again.
      if (Date.now() < suppressClickUntil) {
        if (e.stopPropagation) e.stopPropagation();
        return;
      }
      const actBtn = e.target.closest("[data-act]");
      if (actBtn) {
        e.stopPropagation();
        const act = actBtn.dataset.act;
        const wid = actBtn.dataset.wid;
        const rec = getRecord(wid);
        const wObj = wordLookupById[wid];
        if (act === "star") {
          rec.starred = !rec.starred;
          rec.starredAt = rec.starred ? Date.now() : 0;
          if (!rec.starred) {
            rec.customCn = "";
          }
          playTone("tap");
          saveState();
          refreshAllViews();
          showToast(rec.starred ? "★ 已加入生词本" : "已从生词本移除（释义已恢复默认）");
        } else if (act === "master") {
          rec.mastered = true;
          playTone("success");
          saveState();
          refreshAllViews();
          showToast("✓ 已移入熟词表：「" + (wObj ? wObj.word : "") + "」，词库更精简了！");
        } else if (act === "unmaster") {
          rec.mastered = false;
          playTone("tap");
          saveState();
          refreshAllViews();
          showToast("↺ 已恢复单词到学习词库");
        } else if (act === "dict") {
          openDictModal(wid);
        }
        return;
      }

      const peekEl = e.target.closest("[data-peek]");
      if (peekEl && peekEl.classList.contains("masked-box")) {
        e.stopPropagation();
        peekEl.classList.toggle("peeked");
        const rowForPeek = peekEl.closest(".word-row");
        if (rowForPeek && rowForPeek.dataset.wid && wordLookupById[rowForPeek.dataset.wid]) {
          speakText(wordLookupById[rowForPeek.dataset.wid].word);
        }
        return;
      }

      const row = e.target.closest(".word-row");
      if (!row || !row.dataset.wid) return;
      const wid = row.dataset.wid;
      const w = wordLookupById[wid];
      if (!w) return;
      const rec = getRecord(wid);

      const rect = row.getBoundingClientRect();
      const isLeftHalf = (e.clientX - rect.left) < (rect.width / 2);
      const mode = state.settings.rowClickMode || "unfam_lr";

      speakText(w.word);

      if (mode === "unfam_lr" || mode === "left_sound_right_unfam" || mode === "right_sound_left_unfam") {
        let shouldIncUnfam = true;
        if (mode === "left_sound_right_unfam" && isLeftHalf) shouldIncUnfam = false;
        if (mode === "right_sound_left_unfam" && !isLeftHalf) shouldIncUnfam = false;

        if (shouldIncUnfam) {
          if ((rec.unfam || 0) < 5) {
            rec.unfam = (rec.unfam || 0) + 1;
            saveState();
            updateRowUnfamDOM(row, rec);
          } else {
            showToast("「" + w.word + "」不会程度已达上限 (5/5)");
          }
        }
      }
    }

    // Right-click handler on Word Rows (Requirement 2: Decreases Unfamiliarity 不会程度 -1)
    function handleWordListRightClick(e) {
      if (e.target.closest("[data-act]")) return;
      const row = e.target.closest(".word-row");
      if (!row || !row.dataset.wid) return;
      if (e.preventDefault) e.preventDefault();

      // On a touch device the WebView raises contextmenu for the same hold the long-press
      // gesture owns. Honour it only when it is the sole signal for that hold; a genuine
      // right-click from a mouse attached to the same device still works.
      if (isTouchShell() && activeHold && activeHold.row === row &&
          (Date.now() - activeHold.startedAt) < TOUCH_ECHO_MS) {
        if (activeHold.consumedBy === "gesture") return;
        activeHold.consumedBy = "contextmenu";
      }

      const wid = row.dataset.wid;
      const w = wordLookupById[wid];
      if (!w) return;
      const rec = getRecord(wid);

      if ((rec.unfam || 0) > 0) {
        rec.unfam = (rec.unfam || 0) - 1;
        playTone("down");
        saveState();
        updateRowUnfamDOM(row, rec);
      } else {
        playTone("down");
        showToast("「" + w.word + "」不会程度已为最低 (0/5)");
      }
    }

    // ---- Touch long press == desktop right click (不会程度 -1) ----
    function clearLongPressVisual() {
      if (activeHold && activeHold.row) activeHold.row.classList.remove("lp-arming");
    }

    // A released hold whose timer never fired must be disarmed. Without this, a quick
    // tap (+1) would still be followed 480ms later by an unintended -1.
    function cancelHoldTimer() {
      if (activeHold && activeHold.timer) {
        clearTimeout(activeHold.timer);
        activeHold.timer = null;
      }
    }

    function fireLongPress(hold) {
      if (!hold || hold.consumedBy) return;
      suppressClickUntil = Date.now() + 900;
      handleWordListRightClick({ target: hold.row, preventDefault: function() {} });
      // Claim the hold only AFTER the decrement: the shared handler reads this flag to
      // drop the contextmenu echo, and setting it first would have made it skip the
      // gesture itself.
      hold.consumedBy = "gesture";
      if (hold.row) {
        hold.row.classList.remove("lp-arming");
        hold.row.classList.add("lp-fired");
        const fired = hold.row;
        setTimeout(function() { fired.classList.remove("lp-fired"); }, 420);
      }
    }

    function touchPoint(list) {
      const t = list && list[0];
      return t ? { x: t.clientX, y: t.clientY } : null;
    }

    function handleWordListTouchStart(e) {
      lastTouchAt = Date.now();
      if (e.touches && e.touches.length !== 1) return;
      const row = e.target.closest(".word-row");
      if (!row || !row.dataset.wid) return;
      // ★ / ✕ / 📖 keep their own tap semantics; a hold on a button is not a -1 gesture.
      if (e.target.closest("[data-act]")) return;
      clearLongPressVisual();
      activeHold = {
        seq: ++holdSeq,
        row: row,
        point: touchPoint(e.touches),
        startedAt: Date.now(),
        consumedBy: null
      };
      row.classList.add("lp-arming");
      const seq = activeHold.seq;
      activeHold.timer = setTimeout(function() {
        activeHold.timer = null;
        if (activeHold && activeHold.seq === seq) fireLongPress(activeHold);
      }, LONG_PRESS_MS);
    }

    function handleWordListTouchMove(e) {
      if (!activeHold || !activeHold.row) return;
      const p = touchPoint(e.touches);
      const start = activeHold.point;
      if (!p || !start) return;
      if (Math.abs(p.x - start.x) > LONG_PRESS_SLOP || Math.abs(p.y - start.y) > LONG_PRESS_SLOP) {
        // the finger is scrolling the list, not holding one row
        cancelHoldTimer();
        clearLongPressVisual();
        activeHold.consumedBy = "cancelled";
      }
    }

    function handleWordListTouchEnd() {
      cancelHoldTimer();
      clearLongPressVisual();
    }

    ["learnListContainer", "notebookListContainer", "scrollListContent"].forEach(function(cid) {
      const el = document.getElementById(cid);
      el.addEventListener("click", handleWordListLeftClick);
      el.addEventListener("contextmenu", handleWordListRightClick);
      el.addEventListener("touchstart", handleWordListTouchStart, { passive: true });
      el.addEventListener("touchmove", handleWordListTouchMove, { passive: true });
      el.addEventListener("touchend", handleWordListTouchEnd, { passive: true });
      el.addEventListener("touchcancel", handleWordListTouchEnd, { passive: true });
    });

    document.getElementById("btnCheckinCurrentList").addEventListener("click", function() {
      const listNum = state.currentListIndex + 1;
      state.planChecks["book_" + state.currentBook + "_L" + listNum] = Date.now();
      state.planChecks["d" + listNum + "_new_L" + listNum] = Date.now();
      playTone("success");
      saveState();
      refreshAllViews();
      showToast("🎉 已完成 List " + listNum + " 学习打卡！");
    });

    document.getElementById("btnOpenMasteredDrawer").addEventListener("click", function() {
      nbActiveSubTab = "mastered";
      document.querySelectorAll("#nbSubTabGroup .seg-btn").forEach(function(b) {
        b.classList.toggle("active", b.dataset.nbtab === "mastered");
      });
      switchTab("notebook");
    });

    document.getElementById("btnPrintCurrentList").addEventListener("click", function() {
      const wordsArr = currentLists[state.currentListIndex] || [];
      const built = buildPrintableWordListHtml(wordsArr, "Voca · List " + (state.currentListIndex + 1) + " 单词背诵清单", false);
      openPrintPreviewModal("List " + (state.currentListIndex + 1) + " 单词背诵表", built.html, built.docData);
    });

    // Immersive Card Controls (Unfamiliarity-only)
    document.getElementById("cardHeadword").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (!w) return;
      if (state.langMode === "cn_only" && !cardHeadwordPeeked) {
        cardHeadwordPeeked = true;
        renderImmersiveCard();
      }
      speakText(w.word);
    });

    document.getElementById("cardBtnSpeak").addEventListener("click", function() {
      if (activeWords[cardCursor]) speakText(activeWords[cardCursor].word);
    });

    document.getElementById("cardMeaningBox").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (!w) return;
      if (state.langMode === "en_only" && !cardMeaningPeeked) {
        cardMeaningPeeked = true;
        renderImmersiveCard();
      }
      speakText(w.word);
    });

    document.getElementById("cardBtnPrev").addEventListener("click", function() {
      cardCursor--;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      renderImmersiveCard();
      if (activeWords[cardCursor]) speakText(activeWords[cardCursor].word);
    });

    document.getElementById("cardBtnNext").addEventListener("click", function() {
      cardCursor++;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      renderImmersiveCard();
      if (activeWords[cardCursor]) speakText(activeWords[cardCursor].word);
    });

    document.getElementById("cardBtnUnfamUp").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (!w) return;
      const rec = getRecord(w.id);
      if ((rec.unfam || 0) < 5) {
        rec.unfam = (rec.unfam || 0) + 1;
        playTone("tap");
        saveState();
        renderImmersiveCard();
      } else {
        showToast("不会程度已达上限 (5/5)");
      }
    });

    document.getElementById("cardBtnUnfamDown").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (!w) return;
      const rec = getRecord(w.id);
      if ((rec.unfam || 0) > 0) {
        rec.unfam = (rec.unfam || 0) - 1;
        playTone("down");
        saveState();
        renderImmersiveCard();
      } else {
        showToast("不会程度已为最低 (0/5)");
      }
    });

    document.getElementById("cardBtnStar").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (!w) return;
      const rec = getRecord(w.id);
      rec.starred = !rec.starred;
      rec.starredAt = rec.starred ? Date.now() : 0;
      playTone("tap");
      saveState();
      renderImmersiveCard();
      renderStatsAndPills();
    });

    document.getElementById("cardBtnMaster").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (!w) return;
      getRecord(w.id).mastered = true;
      cardHeadwordPeeked = false;
      cardMeaningPeeked = false;
      playTone("success");
      saveState();
      renderLearnView();
    });

    document.getElementById("cardBtnDict").addEventListener("click", function() {
      const w = activeWords[cardCursor];
      if (w) openDictModal(w.id);
    });

    // Custom Ebbinghaus Plan Events
    function applyCustomPlanInputs() {
      const rawN = document.getElementById("planListCountInput").value;
      const rawD = document.getElementById("planCycleDaysInput").value;
      const clean = sanitizePlanParams(rawN, rawD);
      state.planListCount = clean.n;
      state.planCycleDays = clean.d;
      document.getElementById("planListCountInput").value = String(clean.n);
      document.getElementById("planCycleDaysInput").value = String(clean.d);
      if (state.planActiveDay > clean.d) {
        state.planActiveDay = 1;
      }
      saveState();
      refreshAllViews();
      playTone("success");
      showToast("✓ 已应用自定义计划：" + clean.n + " 个 List · " + clean.d + " 天周期（学习记录已无损保留）");
    }

    document.getElementById("btnApplyCustomPlan").addEventListener("click", applyCustomPlanInputs);
    document.getElementById("planListCountInput").addEventListener("change", applyCustomPlanInputs);
    document.getElementById("planCycleDaysInput").addEventListener("change", applyCustomPlanInputs);

    document.getElementById("planPresetPills").addEventListener("click", function(e) {
      const btn = e.target.closest(".preset-pill-btn");
      if (!btn) return;
      document.getElementById("planListCountInput").value = btn.dataset.n;
      document.getElementById("planCycleDaysInput").value = btn.dataset.d;
      applyCustomPlanInputs();
    });

    document.getElementById("planOrderModeSelect").addEventListener("change", function(e) {
      state.planOrderMode = e.target.value;
      if (state.planOrderMode === "shuffle") {
        state.planShuffleSeed = Date.now() % 1000000;
      }
      saveState();
      refreshAllViews();
    });

    document.getElementById("planDayPicker").addEventListener("change", function(e) {
      state.planActiveDay = parseInt(e.target.value, 10) || 1;
      saveState();
      renderEbbinghausPlan();
    });

    document.getElementById("ebbinghausTableBody").addEventListener("click", function(e) {
      const chip = e.target.closest(".plan-chip");
      if (!chip) return;
      const listNum = parseInt(chip.dataset.listnum, 10);
      if (listNum >= 1) {
        state.currentListIndex = listNum - 1;
        listRenderLimit = 120;
        cardCursor = 0;
        cardHeadwordPeeked = false;
        cardMeaningPeeked = false;
        saveState();
        switchTab("learn");
        showToast("📖 已定位并打开 List " + listNum + " 单词学习内容");
      }
    });

    document.getElementById("btnResetPlanChecks").addEventListener("click", function() {
      state.planChecks = {};
      saveState();
      refreshAllViews();
      showToast("已重置计划表打卡记录（单词不会程度与生词本保持不变）");
    });

    document.getElementById("btnPrintPlanSchedule").addEventListener("click", function() {
      const built = buildPrintableScheduleHtml();
      openPrintPreviewModal("自定义艾宾浩斯学习计划表", built.html, built.docData);
    });

    // Specialized Training Sub-modes
    document.getElementById("trainSubModeGroup").addEventListener("click", function(e) {
      const btn = e.target.closest(".seg-btn");
      if (!btn) return;
      currentTrainSubMode = btn.dataset.tmode;
      document.querySelectorAll("#trainSubModeGroup .seg-btn").forEach(function(b) {
        b.classList.toggle("active", b.dataset.tmode === currentTrainSubMode);
      });
      document.getElementById("trainPanelSpell").style.display = currentTrainSubMode === "spell" ? "block" : "none";
      document.getElementById("trainPanelScroll").style.display = currentTrainSubMode === "scroll" ? "block" : "none";
      toggleAutoScroll(true);
    });

    document.getElementById("trainSourceSelect").addEventListener("change", function() {
      initSpellingSession(true);
      renderAutoScrollList();
    });

    document.getElementById("spellFiveCardsBox").addEventListener("click", function(e) {
      const btn = e.target.closest(".letter-card-btn");
      if (btn && btn.dataset.letter) {
        handleSpellCharInput(btn.dataset.letter);
      }
    });
    document.getElementById("spellBtnHint").addEventListener("click", function() {
      if (!spellList.length) return;
      const target = spellList[spellCursor].word.trim();
      if (spellTyped.length < target.length) {
        handleSpellCharInput(target[spellTyped.length]);
      }
    });
    document.getElementById("spellBtnAddHard").addEventListener("click", function() {
      if (!spellList.length) return;
      const w = spellList[spellCursor];
      const rec = getRecord(w.id);
      rec.unfam = Math.min(5, (rec.unfam || 0) + 1);
      saveState();
      renderSpellingStage();
      showToast("已加深「" + w.word + "」的不会程度 (" + rec.unfam + "/5)");
    });
    document.getElementById("spellBtnSpeak").addEventListener("click", function() {
      if (spellList[spellCursor]) speakText(spellList[spellCursor].word);
    });
    document.getElementById("spellBtnPrev").addEventListener("click", function() {
      if (!spellList.length) return;
      spellCursor = (spellCursor - 1 + spellList.length) % spellList.length;
      spellTyped = "";
      renderSpellingStage();
    });
    document.getElementById("spellBtnSubmit").addEventListener("click", function() {
      if (!spellList.length) return;
      spellCursor = (spellCursor + 1) % spellList.length;
      spellTyped = "";
      renderSpellingStage();
    });

    document.getElementById("spellBtnBackspace").addEventListener("click", spellBackspace);

    document.getElementById("scrollBtnToggle").addEventListener("click", function() {
      toggleAutoScroll(false);
    });
    const svp = document.getElementById("scrollViewport");
    svp.addEventListener("mouseenter", function() {
      // A tap also raises compatibility mouse events. Their matching mouseleave never
      // comes, so trusting them on a touch device would freeze the stream permanently.
      if (isTouchShell() || (Date.now() - lastTouchAt) < 900) return;
      scrollPausedByHover = true;
    });
    svp.addEventListener("mouseleave", function() { scrollPausedByHover = false; });
    // The panel copy promises "悬停或触摸列表自动暂停". Hover only exists on a mouse, so
    // press-to-pause is what makes the promise true on a phone (without this the
    // auto-scrolling stream cannot be stopped with a finger at all).
    svp.addEventListener("touchstart", function() {
      lastTouchAt = Date.now();
      scrollPausedByTouch = true;
      scrollPausedByHover = false;
    }, { passive: true });
    svp.addEventListener("touchend", function() { scrollPausedByTouch = false; }, { passive: true });
    svp.addEventListener("touchcancel", function() { scrollPausedByTouch = false; }, { passive: true });

    // Notebook & Mastered Events
    document.getElementById("nbSubTabGroup").addEventListener("click", function(e) {
      const btn = e.target.closest(".seg-btn");
      if (!btn) return;
      nbActiveSubTab = btn.dataset.nbtab;
      document.querySelectorAll("#nbSubTabGroup .seg-btn").forEach(function(b) {
        b.classList.toggle("active", b.dataset.nbtab === nbActiveSubTab);
      });
      renderNotebookView();
    });
    document.getElementById("nbSortSelect").addEventListener("change", renderNotebookView);
    document.getElementById("btnRestoreAllMastered").addEventListener("click", function() {
      Object.keys(state.records).forEach(function(k) {
        state.records[k].mastered = false;
      });
      saveState();
      refreshAllViews();
      showToast("已将全部熟词恢复至词库");
    });
    document.getElementById("btnPrintStarredBook").addEventListener("click", function() {
      const starred = getAllKnownWordsForNotebook().filter(function(w) { return getRecord(w.id).starred; });
      const built = buildPrintableWordListHtml(starred, "Voca · 生词本重难点强化手册", false);
      openPrintPreviewModal("生词本重难词汇总表", built.html, built.docData);
    });

    // Add Custom Word Modal
    document.getElementById("btnAddCustomWordModal").addEventListener("click", function() {
      document.getElementById("addWordModal").classList.add("open");
    });
    document.getElementById("btnCloseAddWordModal").addEventListener("click", function() {
      document.getElementById("addWordModal").classList.remove("open");
    });
    document.getElementById("btnConfirmAddWord").addEventListener("click", function() {
      const spell = document.getElementById("newWordSpell").value.trim();
      const cn = document.getElementById("newWordCn").value.trim();
      if (!spell || !cn) {
        showToast("请填写英文单词与中文释义");
        return;
      }
      const ipa = document.getElementById("newWordIpa").value.trim() || "/-/";
      const exEn = document.getElementById("newWordExEn").value.trim() || ("Example sentence for " + spell + ".");
      const exCn = document.getElementById("newWordExCn").value.trim() || "";
      const newId = "custom_" + Date.now();
      const wObj = {
        id: newId,
        seq: 60000 + state.customWords.length + 1,
        word: spell,
        uk: ipa,
        us: ipa,
        cn: cn,
        ex_en: exEn,
        ex_cn: exCn,
        tip: "用户手动添加词条",
        books: ["custom"],
        freq: 5
      };
      state.customWords.push(wObj);
      wordLookupById[newId] = wObj;
      const rec = getRecord(newId);
      rec.starred = true;
      rec.starredAt = Date.now();
      rebuildCustomBookCache();
      saveState();
      refreshAllViews();
      document.getElementById("addWordModal").classList.remove("open");
      document.getElementById("newWordSpell").value = "";
      document.getElementById("newWordCn").value = "";
      showToast("已成功添加「" + spell + "」并收入生词本！");
    });

    // Dictionary Modal Actions (Requirement 3 & 4)
    document.getElementById("modalBtnCloseDict").addEventListener("click", function() {
      document.getElementById("dictModal").classList.remove("open");
    });
    document.getElementById("modalBtnSpeakWord").addEventListener("click", function() {
      const w = wordLookupById[currentModalWordId];
      if (w) speakText(w.word);
    });
    document.getElementById("modalBtnCopyWord").addEventListener("click", function() {
      const w = wordLookupById[currentModalWordId];
      if (!w) return;
      try {
        const ta = document.createElement("textarea");
        ta.value = w.word;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        showToast("已复制单词: " + w.word);
      } catch (e) {}
    });

    // Switch Online Dictionary inside Modal (syncs with persistent setting!)
    document.getElementById("modalDictSourceGroup").addEventListener("click", function(e) {
      const btn = e.target.closest(".seg-btn");
      if (!btn || VALID_ONLINE_DICTS.indexOf(btn.dataset.dict) === -1) return;
      state.settings.onlineDict = btn.dataset.dict;
      applySettingsToDOM();
      saveState();
      const w = wordLookupById[currentModalWordId];
      if (w) queryOnlineDictionaryForModal(w);
    });

    document.getElementById("modalBtnReloadDict").addEventListener("click", function() {
      const w = wordLookupById[currentModalWordId];
      if (w) queryOnlineDictionaryForModal(w);
    });

    document.getElementById("modalBtnUnfamUp").addEventListener("click", function() {
      if (!currentModalWordId) return;
      const rec = getRecord(currentModalWordId);
      rec.unfam = Math.min(5, (rec.unfam || 0) + 1);
      document.getElementById("modalUnfamVal").textContent = String(rec.unfam);
      saveState();
      refreshAllViews();
    });
    document.getElementById("modalBtnUnfamDown").addEventListener("click", function() {
      if (!currentModalWordId) return;
      const rec = getRecord(currentModalWordId);
      rec.unfam = Math.max(0, (rec.unfam || 0) - 1);
      document.getElementById("modalUnfamVal").textContent = String(rec.unfam);
      saveState();
      refreshAllViews();
    });
    document.getElementById("modalBtnSaveEdit").addEventListener("click", function() {
      if (!currentModalWordId) return;
      const rec = getRecord(currentModalWordId);
      rec.customCn = document.getElementById("modalEditCnInput").value.trim();
      rec.note = document.getElementById("modalEditNoteInput").value.trim();
      rec.starred = true;
      if (!rec.starredAt) rec.starredAt = Date.now();
      saveState();
      refreshAllViews();
      document.getElementById("dictModal").classList.remove("open");
      showToast("已保存释义与笔记，并同步至生词本与主词库");
    });

    // Data Import / Export / Print Center
    document.getElementById("btnLoadSampleCustomWords").addEventListener("click", function() {
      const sampleText = [
        "serendipity, /ˌserənˈdɪpəti/, n. 意外发现珍奇事物的本领；机缘巧合, Finding that rare book was pure serendipity., 淘到那本珍稀书纯属机缘巧合。, 源自童话《锡兰三王子》",
        "epiphany, /ɪˈpɪfəni/, n. 顿悟，醍醐灌顶的领悟, She had an epiphany about how memory curves work., 她对记忆曲线原理有了顿悟。, 词根：epi+phan(显现)",
        "quintessential, /ˌkwɪntɪˈsenʃl/, adj. 最典型的，精髓的, Spaced repetition is the quintessential memory method., 间隔重复是最典型的记忆法。, 词根：第五元素/精华",
        "eloquent, /ˈeləkwənt/, adj. 雄辩的，有说服力的, She gave an eloquent defense of open-source software., 她做了雄辩的辩护。, 词根：e(出)+loqu(说)",
        "magnanimous, /mæɡˈnænɪməs/, adj. 宽宏大量的，慷慨的, The team was magnanimous in sharing their research., 团队慷慨地分享了研究成果。, 词根：magn(大)+anim(心魂)"
      ].join("\n");
      document.getElementById("pasteImportTextarea").value = sampleText;
      parseCustomTextLines(sampleText);
    });

    document.getElementById("btnParsePasteImport").addEventListener("click", function() {
      parseCustomTextLines(document.getElementById("pasteImportTextarea").value);
    });

    document.getElementById("fileImportLexicon").addEventListener("change", function(e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(ev) {
        const buf = ev.target.result;
        let text = "";
        try {
          const decUtf8 = new TextDecoder("utf-8", { fatal: true });
          text = decUtf8.decode(buf);
        } catch (err) {
          const decGbk = new TextDecoder("gb18030");
          text = decGbk.decode(buf);
        }
        if (file.name.toLowerCase().endsWith(".json")) {
          try {
            const arr = JSON.parse(text);
            if (Array.isArray(arr)) {
              arr.forEach(function(item, i) {
                const spell = item.word || item.headword;
                if (spell) {
                  const newId = "custom_json_" + Date.now() + "_" + i;
                  const cn = item.cn || item.meaning || item.definition || "";
                  const wObj = {
                    id: newId,
                    seq: 70000 + i,
                    word: spell,
                    uk: item.uk || item.phonetic || "/-/",
                    us: item.us || item.phonetic || "/-/",
                    cn: cn,
                    ex_en: item.ex_en || "",
                    ex_cn: item.ex_cn || "",
                    tip: item.tip || "",
                    books: ["custom"],
                    freq: 5
                  };
                  state.customWords.push(wObj);
                  wordLookupById[newId] = wObj;
                }
              });
              rebuildCustomBookCache();
              state.currentBook = "custom";
              document.getElementById("bookSelect").value = "custom";
              saveState();
              refreshAllViews();
              showToast("成功从 JSON 导入 " + arr.length + " 个词条");
              return;
            }
          } catch (ex) {}
        }
        parseCustomTextLines(text);
      };
      reader.readAsArrayBuffer(file);
    });

    // Multi-Page PDF / Print / HTML Export Buttons
    document.getElementById("btnExportPdfSchedule").addEventListener("click", function() {
      const built = buildPrintableScheduleHtml();
      openPrintPreviewModal("自定义艾宾浩斯学习计划表", built.html, built.docData);
    });
    document.getElementById("btnExportPdfListBilingual").addEventListener("click", function() {
      const arr = currentLists[state.currentListIndex] || [];
      const built = buildPrintableWordListHtml(arr, "Voca · List " + (state.currentListIndex + 1) + " 双语对照表", false);
      openPrintPreviewModal("当前 List 双语背诵表", built.html, built.docData);
    });
    document.getElementById("btnExportPdfListQuiz").addEventListener("click", function() {
      const arr = currentLists[state.currentListIndex] || [];
      const built = buildPrintableWordListHtml(arr, "Voca · List " + (state.currentListIndex + 1) + " 默写测试卷", true);
      openPrintPreviewModal("当前 List 默写自测卷", built.html, built.docData);
    });
    document.getElementById("btnExportPdfStarred").addEventListener("click", function() {
      const starred = getAllKnownWordsForNotebook().filter(function(w) { return getRecord(w.id).starred; });
      const built = buildPrintableWordListHtml(starred, "Voca · 生词本重点词汇手册", false);
      openPrintPreviewModal("生词本汇总打印表", built.html, built.docData);
    });

    document.getElementById("btnClosePrintModal").addEventListener("click", function() {
      document.getElementById("printModal").classList.remove("open");
    });

    document.getElementById("btnDownloadDirectPdf").addEventListener("click", function() {
      if (!lastPrintDocData) return;
      const res = generateMultiPagePdfBinary(lastPrintDocData);
      const safeName = lastPrintTitle.replace(/[^\w\u4e00-\u9fa5\-]+/g, "_") + "_v1.0.4.pdf";
      window.__LAST_GENERATED_PDF_INFO__ = {
        filename: safeName,
        pageCount: res.pageCount,
        totalRows: res.totalRows,
        byteLength: res.pdfBytes.byteLength
      };
      announceExport(downloadFileBlob(safeName, res.pdfBytes, "application/pdf"), safeName,
        "✓ 已成功生成并导出 " + res.pageCount + " 页 PDF 文档 (" + safeName + ")");
    });

    document.getElementById("btnTriggerBrowserPrint").addEventListener("click", function() {
      document.getElementById("dedicatedPrintRoot").innerHTML = lastPrintHtmlContent;
      window.print();
    });

    document.getElementById("btnDownloadPrintHtml").addEventListener("click", function() {
      const standalone =
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'><title>" + escapeHtml(lastPrintTitle) + "</title>" +
        "<style>" +
        "@page { size: A4 portrait; margin: 12mm 10mm 14mm 10mm; }" +
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif; color: #0F172A; background: #FFFFFF; margin: 16px; }" +
        "table { width: 100%; border-collapse: collapse; page-break-inside: auto; }" +
        "thead { display: table-header-group; }" +
        "tr { page-break-inside: avoid; break-inside: avoid; }" +
        "th, td { border: 1px solid #94A3B8; padding: 6px 8px; word-break: break-word; }" +
        "th { background: #F1F5F9; }" +
        "</style></head><body>" + lastPrintHtmlContent + "</body></html>";
      const safeHtmlName = lastPrintTitle.replace(/[^\w\u4e00-\u9fa5\-]+/g, "_") + "_v1.0.4.html";
      window.__LAST_GENERATED_HTML_INFO__ = {
        filename: safeHtmlName,
        byteLength: standalone.length
      };
      announceExport(downloadFileBlob(safeHtmlName, standalone, "text/html;charset=utf-8"), safeHtmlName,
        "✓ 已下载独立 HTML 导出文件 (" + safeHtmlName + ")");
    });

    // Backup & Restore (Compatible with v1.0.0, v1.0.1, v1.0.2, v1.0.3)
    document.getElementById("btnExportBackupJson").addEventListener("click", function() {
      const backupObj = {
        app: "Voca Offline Vocabulary Studio",
        version: "1.0.4",
        exportedAt: new Date().toISOString(),
        state: state
      };
      announceExport(downloadFileBlob("voca_backup_v1.0.4_" + new Date().toISOString().slice(0, 10) + ".json", JSON.stringify(backupObj, null, 2), "application/json;charset=utf-8"),
        "完整学习备份", "已导出完整本地学习备份 (.json)");
    });

    function applyBackupJsonText(text, sourceLabel) {
      try {
        const parsed = JSON.parse(text);
        const rawState = parsed.state || parsed;
        if (rawState && typeof rawState === "object") {
          state = migrateStateIfNeeded(rawState);
          rebuildCustomBookCache();
          applySettingsToDOM();
          saveState();
          refreshAllViews();
          showToast("✓ 学习数据备份已完整恢复（" + sourceLabel + "）");
          return true;
        }
      } catch (err) { /* fall through to the shared failure toast */ }
      showToast("备份内容解析失败，请确认是完整的 .json 备份文本");
      return false;
    }

    document.getElementById("fileRestoreBackupJson").addEventListener("change", function(e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(ev) { applyBackupJsonText(ev.target.result, "来自文件 " + file.name); };
      reader.readAsText(file);
    });

    document.getElementById("btnParsePasteRestore").addEventListener("click", function() {
      const box = document.getElementById("pasteRestoreTextarea");
      const text = (box.value || "").trim();
      if (!text) { showToast("请先粘贴备份 JSON 内容"); return; }
      if (applyBackupJsonText(text, "来自粘贴内容")) box.value = "";
    });

    document.getElementById("btnCopyTouchExport").addEventListener("click", function() {
      const box = document.getElementById("touchExportTextarea");
      box.removeAttribute("readonly");
      box.select();
      box.setSelectionRange(0, box.value.length);
      let ok = false;
      try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
      box.setAttribute("readonly", "readonly");
      if (ok) showToast("✓ 已复制，可粘贴到备忘录保存");
      else if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(box.value).then(
          function() { showToast("✓ 已复制到剪贴板"); },
          function() { showToast("复制失败，请长按文本框手动全选"); });
      } else {
        showToast("复制失败，请长按文本框手动全选");
      }
    });

    // CSV Export (Unfamiliarity retained, Mastery removed)
    document.getElementById("btnExportLexiconCsv").addEventListener("click", function() {
      const pool = getBookWords(state.currentBook);
      const rows = [["word", "phonetic", "cn_def", "unfamiliar_level", "starred", "mastered"]];
      pool.forEach(function(w) {
        const r = getRecord(w.id);
        rows.push([
          w.word, w.us || w.uk, getEffectiveCnDef(w),
          String(r.unfam || 0), r.starred ? "1" : "0", r.mastered ? "1" : "0"
        ]);
      });
      const csvContent = "\uFEFF" + rows.map(function(r) {
        return r.map(function(cell) { return '"' + String(cell || "").replace(/"/g, '""') + '"'; }).join(",");
      }).join("\r\n");
      announceExport(downloadFileBlob("voca_" + state.currentBook + "_export.csv", csvContent, "text/csv;charset=utf-8"),
        "词库 CSV", "已导出当前词库 CSV 文件");
    });

    // Settings Controls (Requirement 4: Persistent Online Dictionary Selection)
    document.getElementById("settingOnlineDict").addEventListener("change", function(e) {
      const val = e.target.value;
      if (VALID_ONLINE_DICTS.indexOf(val) !== -1) {
        state.settings.onlineDict = val;
        applySettingsToDOM();
        saveState();
        const dictName = ONLINE_DICT_SOURCES[val].name;
        showToast("✓ 已切换默认在线词典为：" + dictName + "（已持久保存）");
      }
    });
    document.getElementById("settingRowClickMode").addEventListener("change", function(e) {
      state.settings.rowClickMode = e.target.value;
      applySettingsToDOM();
      saveState();
    });
    document.getElementById("settingAccentMode").addEventListener("change", function(e) {
      state.settings.accent = e.target.value;
      saveState();
      speakText("vocabulary", state.settings.accent);
    });
    document.getElementById("settingPhoneticDisplay").addEventListener("change", function(e) {
      state.settings.phoneticDisplay = e.target.value;
      saveState();
      refreshAllViews();
    });
    document.getElementById("settingThemeSelect").addEventListener("change", function(e) {
      state.settings.theme = e.target.value;
      applySettingsToDOM();
      saveState();
    });
    document.getElementById("settingFontScale").addEventListener("change", function(e) {
      state.settings.fontScale = e.target.value;
      applySettingsToDOM();
      saveState();
    });
    document.getElementById("settingSoundFxToggle").addEventListener("change", function(e) {
      state.settings.soundFx = e.target.checked;
      saveState();
    });

    // Global Keyboard Shortcuts (Shortcut '4' for en_en removed per Requirement 5)
    window.addEventListener("keydown", function(e) {
      const tag = (e.target && e.target.tagName) ? e.target.tagName.toUpperCase() : "";
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      const trainViewActive = document.getElementById("view-train").classList.contains("active");
      if (trainViewActive && currentTrainSubMode === "spell") {
        if (/^[a-zA-Z]$/.test(e.key)) {
          e.preventDefault();
          handleSpellCharInput(e.key);
          return;
        } else if (e.key === "Backspace") {
          e.preventDefault();
          spellBackspace();
          return;
        } else if (e.key === "Enter") {
          e.preventDefault();
          document.getElementById("spellBtnSubmit").click();
          return;
        }
      }

      const learnViewActive = document.getElementById("view-learn").classList.contains("active");
      if (!learnViewActive) return;

      if (e.key === " ") {
        e.preventDefault();
        const w = activeWords[cardCursor] || activeWords[0];
        if (w) speakText(w.word);
      } else if (e.key === "j" || e.key === "J" || e.key === "ArrowLeft") {
        if (state.layoutMode === "card") {
          document.getElementById("cardBtnPrev").click();
        }
      } else if (e.key === "k" || e.key === "K" || e.key === "ArrowRight") {
        if (state.layoutMode === "card") {
          document.getElementById("cardBtnNext").click();
        }
      } else if (e.key === "1") {
        document.querySelector('#langModeGroup [data-lang="bilingual"]').click();
      } else if (e.key === "2") {
        document.querySelector('#langModeGroup [data-lang="en_only"]').click();
      } else if (e.key === "3") {
        document.querySelector('#langModeGroup [data-lang="cn_only"]').click();
      }
    });
  }

  window.__VOCA_GET_STATE__ = function() { return state; };
  window.__VOCA_RELOAD_FROM_PRELOAD__ = function(preloadObj) {
    window.__VOCA_PRELOAD_STATE__ = preloadObj;
    loadFromLocalStorage();
    rebuildCustomBookCache();
    applySettingsToDOM();
    refreshAllViews();
  };

  let appBooted = false;
  function bootVocaApp() {
    if (appBooted) return;
    appBooted = true;
    // Windows kiosk convenience. Never on a touch shell: a phone WebView is already
    // full-bleed and resizeTo there is meaningless (and would fight the user's own
    // window on a small desktop window).
    try {
      if (!isTouchShell() && window.screen && window.screen.availWidth > 900 && window.outerWidth < window.screen.availWidth * 0.9) {
        window.moveTo(0, 0);
        window.resizeTo(window.screen.availWidth, window.screen.availHeight);
      }
    } catch (e) {}
    loadFromLocalStorage();
    initIndexedDB();
    rebuildCustomBookCache();
    applySettingsToDOM();
    bindEvents();
    refreshAllViews();
  }

  if (document.readyState === "loading") {
    window.addEventListener("DOMContentLoaded", bootVocaApp);
  } else {
    bootVocaApp();
  }
})();
"""

full_html = (
    HTML_PART1 +
    HTML_PART2 +
    "\n<script>\nconst CORE233_VOCAB = " + core233_json_str + ";\n" +
    "const VOCA_PACK = " + v103_pack_json_str + ";\n" +
    JS_ENGINE +
    "\n</script>\n</body>\n</html>\n"
)

out_html_tmp = os.environ.get("VOCA_OUT_HTML", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "windows", "app", "index.html")))
with open(out_html_tmp, "w", encoding="utf-8", newline="\n") as f:
    f.write(full_html)

print("Assembled %s: %d chars / %d bytes" % (
    out_html_tmp, len(full_html), os.path.getsize(out_html_tmp)))
