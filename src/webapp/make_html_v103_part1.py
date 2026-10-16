#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates Part 1 of Voca v1.0.3 HTML Application:
- Multi-size High-DPI <link rel="icon"> tags (256/192/128/64/48/32/16 + voca.ico) so Windows taskbar & titlebar icons in --app mode are never downsampled to 16x16.
- Embedded cross-platform @font-face (VocaSans Inter + VocaSansCJK Noto Sans CJK SC).
- Removed Mastery (.mastery-badge, data-mastery) styles; enhanced Unfamiliarity (.unfam-badge, data-unfam) styles.
- Online Dictionary modal styles (status banner, parsed entry cards, responsive iframe container).
- Mobile portrait 3-button language mode grid (bilingual / en_only / cn_only, with en_en removed).
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_FILE = os.environ.get("VOCA_EMBEDDED_ASSETS", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "assets", "embedded_assets.json")))
if not os.path.exists(ASSETS_FILE):
    alt_file = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "assets", "embedded_assets.json"))
    if os.path.exists(alt_file):
        ASSETS_FILE = alt_file

with open(ASSETS_FILE, "r", encoding="utf-8") as f:
    ASSETS = json.load(f)

HTML_PART1_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="daylight" data-font="standard">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#0B3B8C">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>Voca v1.0.3 — 离线艾宾浩斯背单词工坊 (Windows &amp; Android)</title>
<!-- Multi-Resolution Taskbar & Window Icons (Fixes Chromium --app 16x16 favicon downsampling blur on Windows Taskbar) -->
<link rel="shortcut icon" type="image/x-icon" href="voca.ico">
<link rel="icon" type="image/png" sizes="256x256" href="data:image/png;base64,__ICON_256_B64__">
<link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,__ICON_192_B64__">
<link rel="icon" type="image/png" sizes="128x128" href="data:image/png;base64,__ICON_128_B64__">
<link rel="icon" type="image/png" sizes="64x64" href="data:image/png;base64,__ICON_64_B64__">
<link rel="icon" type="image/png" sizes="48x48" href="data:image/png;base64,__ICON_48_B64__">
<link rel="icon" type="image/png" sizes="32x32" href="data:image/png;base64,__ICON_32_B64__">
<link rel="icon" type="image/png" sizes="16x16" href="data:image/png;base64,__ICON_16_B64__">
<link rel="apple-touch-icon" sizes="192x192" href="data:image/png;base64,__ICON_192_B64__">
<style>
/* ==================== CROSS-PLATFORM UNIFIED EMBEDDED FONTS ==================== */
@font-face {
  font-family: 'VocaSans';
  src: url("data:font/woff2;base64,__INTER_REG_B64__") format("woff2"),
       url("fonts/Inter-Regular.woff2") format("woff2");
  font-weight: 400 600;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'VocaSans';
  src: url("data:font/woff2;base64,__INTER_BOLD_B64__") format("woff2"),
       url("fonts/Inter-Bold.woff2") format("woff2");
  font-weight: 700 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: 'VocaSansCJK';
  src: url("data:font/woff2;base64,__NOTO_FULL_CJK_B64__") format("woff2"),
       url("fonts/NotoSansCJKsc-Full.woff2") format("woff2");
  font-weight: 400 900;
  font-style: normal;
  font-display: swap;
}

:root, [data-theme="daylight"] {
  --font-unified: 'VocaSans', 'VocaSansCJK', sans-serif;
  --bg-main: #F4F7FA;
  --bg-surface: #FFFFFF;
  --bg-elevated: #F8FAFC;
  --bg-muted: #EEF2F6;
  --bg-glass: rgba(255, 255, 255, 0.90);
  --text-primary: #0F172A;
  --text-secondary: #334155;
  --text-muted: #64748B;
  --border-color: #E2E8F0;
  --border-strong: #CBD5E1;
  --brand-primary: #059669;
  --brand-accent: #10B981;
  --brand-soft: #D1FAE5;
  --brand-text: #065F46;
  --blue-mark: #2563EB;
  --blue-soft: #DBEAFE;
  --amber-mark: #D97706;
  --amber-soft: #FEF3C7;
  --rose-mark: #E11D48;
  --rose-soft: #FFE4E6;
  --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.05);
  --shadow-md: 0 8px 24px -4px rgba(15, 23, 42, 0.08);
  --shadow-lg: 0 20px 32px -8px rgba(15, 23, 42, 0.12);
}

[data-theme="oled"] {
  --bg-main: #000000;
  --bg-surface: #0A0A0C;
  --bg-elevated: #141418;
  --bg-muted: #08080A;
  --bg-glass: rgba(10, 10, 12, 0.94);
  --text-primary: #F4F4F6;
  --text-secondary: #A1A1AA;
  --text-muted: #71717A;
  --border-color: #222228;
  --border-strong: #3F3F46;
  --brand-primary: #10B981;
  --brand-accent: #34D399;
  --brand-soft: rgba(16, 185, 129, 0.16);
  --brand-text: #6EE7B7;
  --blue-mark: #38BDF8;
  --blue-soft: rgba(56, 189, 248, 0.20);
  --amber-mark: #FACC15;
  --amber-soft: rgba(250, 204, 21, 0.18);
  --rose-mark: #F43F5E;
  --rose-soft: rgba(244, 63, 94, 0.20);
  --shadow-sm: none;
  --shadow-md: 0 0 0 1px #222228;
  --shadow-lg: 0 12px 28px rgba(0, 0, 0, 0.9);
}

[data-theme="paper"] {
  --bg-main: #F5EFE2;
  --bg-surface: #FCF9F2;
  --bg-elevated: #F2E9D8;
  --bg-muted: #EAE0CC;
  --bg-glass: rgba(252, 249, 242, 0.92);
  --text-primary: #2C221E;
  --text-secondary: #52433B;
  --text-muted: #7D6B5D;
  --border-color: #E0D5C1;
  --border-strong: #C9B99F;
  --brand-primary: #0D7A5F;
  --brand-accent: #129474;
  --brand-soft: #D7EFE7;
  --brand-text: #085843;
  --blue-mark: #2B5B84;
  --blue-soft: #DCE8F2;
  --amber-mark: #B45309;
  --amber-soft: #FDE68A;
  --rose-mark: #BE123C;
  --rose-soft: #FECDD3;
  --shadow-sm: 0 1px 2px rgba(44, 34, 30, 0.06);
  --shadow-md: 0 6px 20px -4px rgba(44, 34, 30, 0.09);
  --shadow-lg: 0 16px 28px -6px rgba(44, 34, 30, 0.14);
}

[data-font="small"] { --font-scale: 0.90; }
[data-font="standard"] { --font-scale: 1.00; }
[data-font="large"] { --font-scale: 1.12; }
[data-font="xlarge"] { --font-scale: 1.25; }

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  -webkit-tap-highlight-color: transparent;
  font-family: var(--font-unified);
}

html, body {
  width: 100%;
  height: 100%;
  font-family: var(--font-unified);
  background-color: var(--bg-main);
  color: var(--text-primary);
  font-size: calc(15px * var(--font-scale, 1));
  line-height: 1.55;
  overflow-x: hidden;
  font-variant-numeric: tabular-nums;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.app-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  max-width: none;
  margin: 0;
}

.sidebar {
  width: 256px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 20px 14px;
  position: sticky;
  top: 0;
  height: 100vh;
  flex-shrink: 0;
  z-index: 30;
}

.brand-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 10px 18px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.brand-logo {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  flex-shrink: 0;
  object-fit: contain;
  display: block;
  image-rendering: -webkit-optimize-contrast;
}

.brand-title {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.brand-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 6px;
  background: var(--brand-soft);
  color: var(--brand-text);
}

.brand-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-height: 0;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 11px;
  width: 100%;
  padding: 11px 13px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
  transition: all 0.16s ease;
}

.nav-btn-bottom {
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid var(--border-color);
  border-radius: 0 0 12px 12px;
}

.nav-btn:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.nav-btn.active {
  background: var(--brand-soft);
  color: var(--brand-primary);
  font-weight: 700;
}

.nav-btn svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-pill {
  margin-left: auto;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 99px;
  background: var(--bg-muted);
  color: var(--text-secondary);
}

.nav-btn.active .nav-pill {
  background: var(--brand-primary);
  color: #FFFFFF;
}

.main-area {
  flex: 1;
  min-width: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  padding-bottom: 48px;
}

.top-header {
  position: sticky;
  top: 0;
  z-index: 25;
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  padding: 12px 26px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.ctrl-select, .ctrl-input-num {
  background-color: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  padding: 7px 12px;
  font-size: 0.88rem;
  font-weight: 600;
  font-family: var(--font-unified);
}

.ctrl-select {
  appearance: none;
  padding-right: 30px;
  cursor: pointer;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2.5'><polyline points='6 9 12 15 18 9'/></svg>");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.ctrl-input-num {
  width: 82px;
  text-align: center;
}

.ctrl-input-num:focus, .ctrl-select:focus {
  outline: 2px solid var(--brand-primary);
  border-color: var(--brand-primary);
}

.seg-group {
  display: inline-flex;
  background: var(--bg-muted);
  padding: 3px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.seg-btn {
  border: none;
  background: transparent;
  color: var(--text-secondary);
  padding: 5px 11px;
  border-radius: 7px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.seg-btn.active {
  background: var(--bg-surface);
  color: var(--brand-primary);
  box-shadow: var(--shadow-sm);
  font-weight: 700;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 0.86rem;
  font-weight: 600;
  border: 1px solid var(--border-color);
  background: var(--bg-surface);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  text-decoration: none;
}

.btn:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.btn-primary {
  background: var(--brand-primary);
  color: #FFFFFF;
  border-color: var(--brand-primary);
}

.btn-primary:hover {
  background: var(--brand-accent);
  border-color: var(--brand-accent);
  color: #FFFFFF;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.78rem;
  border-radius: 8px;
}

.page-container {
  padding: 20px 26px;
  max-width: none;
  width: 100%;
  margin: 0;
}

.view-section {
  display: none;
}

.view-section.active {
  display: block;
}

.mode-hint-banner {
  background: var(--brand-soft);
  border: 1px solid var(--brand-primary);
  color: var(--brand-text);
  border-radius: 12px;
  padding: 10px 16px;
  margin-bottom: 14px;
  display: none;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 0.84rem;
  font-weight: 600;
}

.mode-hint-banner.visible {
  display: flex;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}

.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.stat-label {
  font-size: 0.78rem;
  color: var(--text-muted);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
}

.stat-val {
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.stat-sub {
  font-size: 0.74rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.learn-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.learn-toolbar-left, .learn-toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-input {
  padding: 7px 12px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: var(--bg-surface);
  color: var(--text-primary);
  font-size: 0.86rem;
  width: 240px;
}

.word-list-wrap {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.word-row {
  display: grid;
  grid-template-columns: 48px minmax(190px, 1.2fr) minmax(240px, 2.2fr) auto;
  align-items: center;
  gap: 12px;
  padding: 13px 18px;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.14s ease;
  cursor: pointer;
  user-select: none;
  position: relative;
}

.word-row:last-child {
  border-bottom: none;
}

.word-row:hover {
  background: var(--bg-elevated);
}

/* Unfamiliarity (不会程度 0..5) Blue Tint Levels — Only word state metric retained in v1.0.3 */
.word-row[data-unfam="1"] { border-left: 4px solid rgba(37, 99, 235, 0.35); }
.word-row[data-unfam="2"] { border-left: 4px solid rgba(37, 99, 235, 0.55); background: rgba(37, 99, 235, 0.03); }
.word-row[data-unfam="3"] { border-left: 4px solid rgba(37, 99, 235, 0.75); background: rgba(37, 99, 235, 0.06); }
.word-row[data-unfam="4"] { border-left: 4px solid rgba(37, 99, 235, 0.90); background: rgba(37, 99, 235, 0.09); }
.word-row[data-unfam="5"] { border-left: 4px solid #1D4ED8; background: rgba(37, 99, 235, 0.13); }

.w-idx {
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--text-muted);
  text-align: center;
}

.w-head-col {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.w-word {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  word-break: break-word;
}

.w-ipa {
  font-size: 0.84rem;
  color: var(--text-muted);
  font-family: var(--font-unified);
  font-weight: 500;
}

.unfam-dots {
  display: inline-flex;
  gap: 3px;
  align-items: center;
}

.unfam-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-strong);
}

.unfam-dot.lit {
  background: var(--blue-mark);
}

.unfam-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 6px;
  background: var(--bg-muted);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.unfam-badge.has-unfam {
  background: var(--blue-soft);
  color: var(--blue-mark);
}

.w-meaning-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.w-cn {
  font-size: 0.94rem;
  color: var(--text-secondary);
  font-weight: 500;
  word-break: break-word;
}

.w-ex {
  font-size: 0.79rem;
  color: var(--text-muted);
  word-break: break-word;
}

.masked-box {
  filter: blur(6px);
  background: var(--bg-muted);
  border-radius: 6px;
  padding: 2px 6px;
  transition: filter 0.18s ease, background 0.18s ease;
  user-select: none;
}

.masked-box.peeked {
  filter: none;
  background: transparent;
}

.w-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  border: 1px solid var(--border-color);
  background: var(--bg-surface);
  color: var(--text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 0.95rem;
}

.icon-btn:hover {
  border-color: var(--text-secondary);
  color: var(--text-primary);
}

.icon-btn.starred {
  color: var(--amber-mark);
  background: var(--amber-soft);
  border-color: var(--amber-mark);
}

.icon-btn.master-btn:hover {
  color: var(--rose-mark);
  background: var(--rose-soft);
  border-color: var(--rose-mark);
}

/* Immersive Card View */
.immersive-stage {
  max-width: 760px;
  margin: 12px auto;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 34px 32px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

.card-word-title {
  font-size: 2.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  text-align: center;
  padding: 8px 14px;
  border-radius: 14px;
  word-break: break-word;
  transition: background-color 0.15s ease;
}

.card-word-title.masked-headword {
  font-size: 1.2rem;
  background: var(--bg-elevated);
  border: 1px dashed var(--brand-primary);
  color: var(--brand-primary);
  cursor: pointer;
}

.card-word-title.masked-headword:hover {
  background: var(--brand-soft);
}

.card-phonetic-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 14px;
  color: var(--text-muted);
  font-size: 0.96rem;
  font-family: var(--font-unified);
  flex-wrap: wrap;
}

.card-section-box {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 16px 18px;
}

.card-bottom-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding-top: 6px;
  flex-wrap: wrap;
}

.card-unfam-controls {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

/* Online Dictionary Modal Styles (Requirement 3 & 4) */
.dict-online-box {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dict-online-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 8px;
}

.dict-status-banner {
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.5;
}

.dict-status-loading {
  background: var(--blue-soft);
  color: var(--blue-mark);
}

.dict-status-ok {
  background: var(--brand-soft);
  color: var(--brand-text);
}

.dict-status-warn {
  background: var(--amber-soft);
  color: var(--amber-mark);
}

.dict-status-error {
  background: var(--rose-soft);
  color: var(--rose-mark);
}

.dict-parsed-entries {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.88rem;
  line-height: 1.65;
  max-height: 240px;
  overflow-y: auto;
}

.dict-iframe-wrap {
  width: 100%;
  height: 310px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  overflow: hidden;
  background: #FFFFFF;
}

.dict-iframe-wrap iframe {
  width: 100%;
  height: 100%;
  border: none;
}

/* Ebbinghaus Custom Config Panel & Schedule Matrix Table */
.plan-custom-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  background: var(--bg-elevated);
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  margin-top: 12px;
}

.plan-preset-pills {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.preset-pill-btn {
  padding: 4px 9px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 99px;
  border: 1px solid var(--border-strong);
  background: var(--bg-surface);
  color: var(--text-secondary);
  cursor: pointer;
}

.preset-pill-btn:hover, .preset-pill-btn.active {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  background: var(--brand-soft);
}

.matrix-table-wrap {
  overflow-x: auto;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  -webkit-overflow-scrolling: touch;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
}

.matrix-table th, .matrix-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  text-align: center;
}

.matrix-table th {
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-weight: 700;
}

.plan-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.80rem;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid var(--border-strong);
  background: var(--bg-surface);
  color: var(--text-primary);
  transition: all 0.15s ease;
  margin: 2px;
}

.plan-chip:hover {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.plan-chip.done {
  background: var(--brand-soft);
  border-color: var(--brand-primary);
  color: var(--brand-text);
}

/* 5-Card Spelling Challenge */
.spell-stage {
  max-width: 700px;
  margin: 0 auto;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 22px;
  padding: 28px 26px;
  box-shadow: var(--shadow-md);
  text-align: center;
}

.spell-slots {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
}

.spell-slot {
  width: 40px;
  height: 48px;
  border-bottom: 3px solid var(--border-strong);
  background: var(--bg-elevated);
  border-radius: 8px 8px 2px 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.spell-slot.filled {
  border-bottom-color: var(--brand-primary);
  color: var(--brand-primary);
  background: var(--brand-soft);
}

.spell-slot.current {
  border-bottom-color: var(--blue-mark);
  box-shadow: 0 0 0 2px var(--blue-soft);
}

.five-cards-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 18px 0;
  flex-wrap: wrap;
}

.letter-card-btn {
  width: 58px;
  height: 64px;
  border-radius: 14px;
  border: 2px solid var(--border-strong);
  border-bottom-width: 4px;
  background: var(--bg-surface);
  color: var(--text-primary);
  font-size: 1.45rem;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.1s ease, border-color 0.15s ease, background 0.15s ease;
}

.letter-card-btn:hover {
  border-color: var(--brand-primary);
  transform: translateY(-2px);
}

.letter-card-btn:active {
  transform: translateY(2px);
  border-bottom-width: 2px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  z-index: 60;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-backdrop.open {
  display: flex;
}

.modal-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  max-width: 720px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 22px 24px;
  box-shadow: var(--shadow-lg);
}

.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 80;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: calc(100vw - 32px);
}

.toast-item {
  background: var(--text-primary);
  color: var(--bg-surface);
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 0.86rem;
  font-weight: 600;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 10px;
  word-break: break-word;
}

.mobile-bottom-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-glass);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-top: 1px solid var(--border-color);
  z-index: 45;
  padding: 5px 6px calc(6px + env(safe-area-inset-bottom, 0px));
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 2px;
}

.mob-nav-btn {
  border: none;
  background: transparent;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 5px 2px;
  border-radius: 10px;
  cursor: pointer;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mob-nav-btn.active {
  color: var(--brand-primary);
  background: var(--brand-soft);
  font-weight: 700;
}

#dedicatedPrintRoot {
  display: none;
}

/* ==================== ANDROID PORTRAIT LAYOUT OPTIMIZATION (<= 900px) ==================== */
@media (max-width: 900px) {
  .sidebar {
    display: none;
  }
  .mobile-bottom-nav {
    display: grid;
  }
  .main-area {
    padding-bottom: calc(74px + env(safe-area-inset-bottom, 0px));
  }
  .top-header {
    padding: 8px 10px;
    gap: 6px;
  }
  .header-left, .header-right {
    width: 100%;
    gap: 6px;
    justify-content: space-between;
  }
  #bookSelect {
    flex: 1 1 54%;
    min-width: 0;
    font-size: 0.80rem;
    padding: 6px 24px 6px 8px;
  }
  #listSelect {
    flex: 1 1 40%;
    min-width: 0;
    font-size: 0.80rem;
    padding: 6px 24px 6px 8px;
  }
  /* 3 language modes after removing en_en */
  #langModeGroup {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  #langModeGroup .seg-btn {
    padding: 5px 4px;
    font-size: 0.78rem;
    text-align: center;
  }
  #layoutModeGroup {
    flex: 0 0 auto;
  }
  #layoutModeGroup .seg-btn {
    padding: 5px 8px;
    font-size: 0.75rem;
  }
  #sortSelect {
    flex: 1 1 auto;
    min-width: 0;
    font-size: 0.76rem;
    padding: 5px 22px 5px 8px;
  }
  #quickThemeBtn {
    padding: 5px 8px;
    font-size: 0.74rem;
  }
  .page-container {
    padding: 10px 10px;
  }
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin-bottom: 12px;
  }
  .stat-card {
    padding: 10px 12px;
    border-radius: 12px;
  }
  .stat-label {
    font-size: 0.71rem;
  }
  .stat-val {
    font-size: 1.20rem;
  }
  .stat-sub {
    font-size: 0.68rem;
  }
  .learn-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .learn-toolbar-left {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
  .search-input {
    width: 100%;
    font-size: 0.84rem;
  }
  #clickRuleHint {
    font-size: 0.71rem !important;
    line-height: 1.35;
  }
  .learn-toolbar-right {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
  }
  .learn-toolbar-right .btn {
    width: 100%;
    padding: 7px 4px;
    font-size: 0.73rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .word-row {
    grid-template-columns: 26px minmax(0, 1fr) auto;
    gap: 8px;
    padding: 10px 10px;
  }
  .w-idx {
    font-size: 0.72rem;
    align-self: start;
    padding-top: 3px;
  }
  .w-head-col {
    grid-column: 2 / 3;
  }
  .w-meaning-col {
    grid-column: 2 / 4;
    margin-top: 2px;
  }
  .w-actions {
    grid-column: 3 / 4;
    grid-row: 1 / 2;
    align-self: start;
    gap: 4px;
  }
  .icon-btn {
    width: 32px;
    height: 32px;
    font-size: 0.88rem;
  }
  .w-word {
    font-size: 1.05rem;
    gap: 6px;
  }
  .w-cn {
    font-size: 0.88rem;
  }
  .w-ex {
    font-size: 0.75rem;
  }
  .immersive-stage {
    padding: 16px 14px;
    border-radius: 18px;
    gap: 12px;
    margin: 4px auto;
  }
  .card-word-title {
    font-size: clamp(1.45rem, 6.2vw, 2.0rem);
    padding: 6px 8px;
  }
  .card-section-box {
    padding: 12px 14px;
  }
  .card-bottom-nav {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .card-unfam-controls {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
    order: 1;
  }
  .card-unfam-controls .btn {
    width: 100%;
    padding: 8px 4px;
    font-size: 0.76rem;
  }
  .card-prev-next-wrap {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    order: 2;
  }
  .spell-stage {
    padding: 16px 12px;
    border-radius: 16px;
  }
  .spell-slots {
    gap: 5px;
    margin: 14px 0;
  }
  .spell-slot {
    width: 28px;
    height: 36px;
    font-size: 1.10rem;
  }
  .five-cards-row {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 6px;
    margin: 14px 0;
  }
  .letter-card-btn {
    width: 100%;
    height: 52px;
    font-size: 1.25rem;
    border-radius: 10px;
  }
  .modal-backdrop {
    padding: 8px;
  }
  .modal-panel {
    padding: 14px;
    max-height: 90vh;
    border-radius: 16px;
  }
  .toast-container {
    bottom: 76px;
    right: 12px;
    left: 12px;
  }
}

/* ==================== MULTI-PAGE PDF EXPORT & PRINT ENGINE ==================== */
@page {
  size: A4 portrait;
  margin: 12mm 10mm 14mm 10mm;
}

@media print {
  html, body {
    width: 100% !important;
    height: auto !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
    font-size: 10pt !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
  .app-layout,
  .sidebar,
  .top-header,
  .mobile-bottom-nav,
  .modal-backdrop,
  .toast-container,
  .no-print {
    display: none !important;
  }
  #dedicatedPrintRoot {
    display: block !important;
    position: static !important;
    width: 100% !important;
    height: auto !important;
    overflow: visible !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
  }
  #dedicatedPrintRoot .print-doc-wrap {
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  #dedicatedPrintRoot table {
    width: 100% !important;
    border-collapse: collapse !important;
    table-layout: fixed !important;
    page-break-inside: auto !important;
    break-inside: auto !important;
    font-size: 9.5pt !important;
  }
  #dedicatedPrintRoot thead {
    display: table-header-group !important;
  }
  #dedicatedPrintRoot tfoot {
    display: table-footer-group !important;
  }
  #dedicatedPrintRoot tr {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    page-break-after: auto !important;
  }
  #dedicatedPrintRoot th,
  #dedicatedPrintRoot td {
    border: 1px solid #94A3B8 !important;
    padding: 5px 7px !important;
    word-break: break-word !important;
    overflow-wrap: anywhere !important;
    vertical-align: middle !important;
    color: #0F172A !important;
  }
  #dedicatedPrintRoot th {
    background-color: #F1F5F9 !important;
    font-weight: 700 !important;
  }
}
</style>
</head>
<body>
"""

HTML_PART1 = (
    HTML_PART1_TEMPLATE
    .replace("__ICON_256_B64__", ASSETS["icon_256_b64"])
    .replace("__ICON_192_B64__", ASSETS["icon_192_b64"])
    .replace("__ICON_128_B64__", ASSETS["icon_128_b64"])
    .replace("__ICON_64_B64__", ASSETS["icon_64_b64"])
    .replace("__ICON_48_B64__", ASSETS["icon_48_b64"])
    .replace("__ICON_32_B64__", ASSETS["icon_32_b64"])
    .replace("__ICON_16_B64__", ASSETS["icon_16_b64"])
    .replace("__INTER_REG_B64__", ASSETS["inter_regular_woff2_b64"])
    .replace("__INTER_BOLD_B64__", ASSETS["inter_bold_woff2_b64"])
    .replace("__NOTO_FULL_CJK_B64__", ASSETS["noto_full_cjk_woff2_b64"])
)

if __name__ == "__main__":
    print("make_html_v103_part1 ready, length:", len(HTML_PART1))
