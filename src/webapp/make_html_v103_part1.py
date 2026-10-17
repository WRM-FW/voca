#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates Part 1 of Voca v1.0.4 HTML Application:
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
<!-- Pinch-zoom is a legitimate accessibility need on a phone: no maximum-scale,
     no user-scalable=no. viewport-fit=cover exposes env(safe-area-inset-*) for cutouts. -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0B3B8C">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>Voca v1.0.4 — 离线艾宾浩斯背单词工坊 (Windows &amp; Android)</title>
<!-- Window / taskbar icons. Windows asks the shell for a DPI-exact small icon
     (16@100%, 20@125%, 24@150%, 28@175%, 32@200%, 36@225%, 40@250%, 48@300%).
     Any scale without its own declared frame gets resampled and looks soft. -->
<link rel="shortcut icon" type="image/x-icon" href="voca.ico">
<link rel="icon" type="image/png" sizes="256x256" href="data:image/png;base64,__ICON_256_B64__">
<link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,__ICON_192_B64__">
<link rel="icon" type="image/png" sizes="128x128" href="data:image/png;base64,__ICON_128_B64__">
<link rel="icon" type="image/png" sizes="64x64" href="data:image/png;base64,__ICON_64_B64__">
<link rel="icon" type="image/png" sizes="48x48" href="data:image/png;base64,__ICON_48_B64__">
<link rel="icon" type="image/png" sizes="40x40" href="data:image/png;base64,__ICON_40_B64__">
<link rel="icon" type="image/png" sizes="36x36" href="data:image/png;base64,__ICON_36_B64__">
<link rel="icon" type="image/png" sizes="32x32" href="data:image/png;base64,__ICON_32_B64__">
<link rel="icon" type="image/png" sizes="28x28" href="data:image/png;base64,__ICON_28_B64__">
<link rel="icon" type="image/png" sizes="24x24" href="data:image/png;base64,__ICON_24_B64__">
<link rel="icon" type="image/png" sizes="20x20" href="data:image/png;base64,__ICON_20_B64__">
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
  min-height: 100dvh;
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
  height: 100dvh;
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

/* Hover styling is a mouse-only affordance. Kept inside a capability query so it can
   never "stick" after a tap on a touchscreen (there is no hover state to leave). */
@media (hover: hover) and (pointer: fine) {
  .nav-btn:hover {
    background: var(--bg-elevated);
    color: var(--text-primary);
  }
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

@media (hover: hover) and (pointer: fine) {
  .btn:hover {
    border-color: var(--brand-primary);
    color: var(--brand-primary);
  }
}

.btn-primary {
  background: var(--brand-primary);
  color: #FFFFFF;
  border-color: var(--brand-primary);
}

@media (hover: hover) and (pointer: fine) {
  .btn-primary:hover {
    background: var(--brand-accent);
    border-color: var(--brand-accent);
    color: #FFFFFF;
  }
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
  /* min(…,100%) keeps the track from forcing horizontal overflow on a narrow screen;
     at desktop widths auto-fit still lays the four cards out in one row. */
  grid-template-columns: repeat(auto-fit, minmax(min(180px, 100%), 1fr));
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
  grid-template-columns: 48px minmax(0, 1.2fr) minmax(0, 2.2fr) auto;
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

@media (hover: hover) and (pointer: fine) {
  .word-row:hover {
    background: var(--bg-elevated);
  }
}

/* Unfamiliarity (不会程度 0..5) Blue Tint Levels — Only word state metric retained since v1.0.3 */
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

@media (hover: hover) and (pointer: fine) {
  .icon-btn:hover {
    border-color: var(--text-secondary);
    color: var(--text-primary);
  }
}

.icon-btn.starred {
  color: var(--amber-mark);
  background: var(--amber-soft);
  border-color: var(--amber-mark);
}

@media (hover: hover) and (pointer: fine) {
  .icon-btn.master-btn:hover {
    color: var(--rose-mark);
    background: var(--rose-soft);
    border-color: var(--rose-mark);
  }
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

@media (hover: hover) and (pointer: fine) {
  .card-word-title.masked-headword:hover {
    background: var(--brand-soft);
  }
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

/* Neutral state for "the live page is shown, but we did not parse a gloss ourselves".
   Deliberately not the green --brand-soft success treatment. */
.dict-status-info {
  background: var(--blue-soft);
  color: var(--blue-mark);
}

.dict-parsed-hint {
  color: var(--text-muted);
  font-size: 0.83rem;
}

.dict-parsed-note {
  font-size: 0.84rem;
  color: var(--text-secondary);
}

.dict-parsed-warn {
  font-weight: 700;
  color: var(--rose-mark);
  margin-bottom: 6px;
}

.dict-parsed-title {
  font-weight: 800;
  color: var(--brand-primary);
  margin-bottom: 6px;
}

.dict-parsed-item {
  margin-bottom: 4px;
}

.dict-parsed-entries {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.88rem;
  line-height: 1.65;
  /* Scales with the real window instead of a fixed 240px desktop box. */
  max-height: clamp(104px, 22vh, 300px);
  overflow-y: auto;
  overscroll-behavior: contain;
}

.dict-iframe-wrap {
  display: none;
  width: 100%;
  /* Keeps the embedded dictionary usable from a short laptop window to a
     maximised 4K desktop without clipping or leaving a dead band of whitespace. */
  height: clamp(240px, 46vh, 660px);
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  overflow: hidden;
  background: #FFFFFF;
}

.dict-iframe-wrap.dict-frame-visible {
  display: block;
}

.dict-iframe-wrap iframe {
  width: 100%;
  height: 100%;
  border: none;
  color-scheme: light;
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

.preset-pill-btn.active {
  border-color: var(--brand-primary);
  color: var(--brand-primary);
  background: var(--brand-soft);
}

@media (hover: hover) and (pointer: fine) {
  .preset-pill-btn:hover {
    border-color: var(--brand-primary);
    color: var(--brand-primary);
    background: var(--brand-soft);
  }
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

@media (hover: hover) and (pointer: fine) {
  .plan-chip:hover {
    border-color: var(--brand-primary);
    color: var(--brand-primary);
  }
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

@media (hover: hover) and (pointer: fine) {
  .letter-card-btn:hover {
    border-color: var(--brand-primary);
    transform: translateY(-2px);
  }
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
  /* dvh tracks the real visible viewport on mobile browsers/WebView, so the panel
     is never taller than what the user can actually see (100vh overflows under
     the browser toolbar). vh kept as the fallback for older engines. */
  max-height: 90vh;
  max-height: min(90vh, calc(100dvh - 24px));
  overflow-y: auto;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
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

/* ==================== SHELL-NEUTRAL COMPONENT CLASSES ==================== */

/* Card grids that used to live as inline grid-template-columns:minmax(300px/280px,1fr).
   A track minimum can never shrink, so those grids overflowed any viewport narrower
   than ~310px. min(…,100%) makes the track collapse to the available width instead. */
.panel-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
}
.panel-grid-loose {
  gap: 18px;
}
.panel-grid-inner {
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
}

/* Auto-scroll drill viewport. Previously an inline style="max-height:540px" that no
   media query could override, so a phone got a 540px tall scroller inside a 568px
   screen. Desktop keeps the same 540px cap. */
/* Spelling drill action row: prev / submit and the on-screen delete key. */
.spell-key-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
}

.scroll-viewport {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  background: var(--bg-surface);
  max-height: 540px;
}

/* Mobile-only furniture. Hidden by default (and when the shell script cannot run), so
   the desktop presentation is untouched. The touch shell re-enables it with a more
   specific selector, which is why this must NOT be !important. */
.m-only {
  display: none;
}

/* Mirror of .m-only: desktop-only copy (no base rule needed, span is inline). */
html.ui-mobile .d-only {
  display: none !important;
}

/* Hint sentences that sit inline next to a title opt back out of the block .m-only. */
html.ui-mobile .m-only.m-inline { display: inline; }

/* Long-press ("hold to lower 不会程度") build-up feedback, driven by the touch handler. */
@keyframes vocaLongPressPop {
  0%   { box-shadow: inset 0 0 0 2px var(--rose-mark); }
  100% { box-shadow: inset 0 0 0 2px transparent; }
}

/* ==================== NARROW DESKTOP WINDOW (mouse + hover, any width) ====================
   Previously any window under 900px was handed the phone chrome. With a real pointer
   those windows keep the desktop shell; the rail simply narrows and then collapses to
   icons, and the maximised / recommended desktop presentation is untouched. */
@media (hover: hover) and (pointer: fine) and (max-width: 1180px) {
  .sidebar { width: 208px; padding: 16px 10px; }
  .nav-btn { padding: 10px 10px; font-size: 0.9rem; }
  .brand-title { font-size: 1.15rem; }
}

@media (hover: hover) and (pointer: fine) and (max-width: 860px) {
  .sidebar { width: 68px; padding: 14px 8px; }
  .sidebar .brand-box { justify-content: center; padding: 6px 0 14px; }
  .sidebar .brand-box > div { display: none; }
  .nav-btn { justify-content: center; padding: 10px 0; gap: 0; }
  .nav-btn > span:not(.nav-pill) { display: none; }
  .nav-btn .nav-pill { display: none; }
  .top-header, .page-container { padding-left: 14px; padding-right: 14px; }
}

/* ==================== TOUCH SHELL: PHONE / TABLET / LANDSCAPE / FOLDABLE ====================
   Selected by input capability (see the head script), not by width, so a landscape
   phone still gets the thumb-friendly chrome and a narrow desktop window still gets
   the sidebar. Everything below is scoped to html.ui-mobile. */
html.ui-mobile {
  --m-nav-h: 62px;
  --m-gap: 10px;
  --m-tap: 44px;
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left: env(safe-area-inset-left, 0px);
  --safe-right: env(safe-area-inset-right, 0px);
}

/* App shell: one non-scrolling document, one scrolling content column. The bottom bar
   is a flex child of the shell, so content can never slide underneath it and no
   compensating pixel padding is needed anywhere. */
html.ui-mobile,
html.ui-mobile body {
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

html.ui-mobile body {
  display: flex;
  flex-direction: column;
  padding-left: var(--safe-left);
  padding-right: var(--safe-right);
}

html.ui-mobile .app-layout {
  flex: 1 1 auto;
  min-height: 0;
  flex-direction: column;
  width: 100%;
}

html.ui-mobile .sidebar {
  display: none;
}

html.ui-mobile .main-area {
  flex: 1 1 auto;
  min-height: 0;
  padding-bottom: 0;
}

/* Nothing scrolls under the touch chrome (it is flex siblings, not overlays), so the
   three stacked backdrop-filter layers the desktop shell uses would only cost a
   mid-range WebView frames. Opaque surfaces instead. */
html.ui-mobile .top-header,
html.ui-mobile .mobile-bottom-nav {
  background: var(--bg-surface);
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

html.ui-mobile .modal-backdrop {
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

html.ui-mobile .page-container {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  padding: var(--m-gap) var(--m-gap) calc(20px + var(--safe-bottom));
  max-width: none;
}

/* ---- Compact two-row context header (was a 127-161px wrapping desktop toolbar) ---- */
html.ui-mobile .top-header {
  position: static;
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 0.9fr) var(--m-tap);
  grid-template-rows: auto auto;
  gap: 8px;
  align-items: center;
  justify-items: stretch;
  padding: calc(8px + var(--safe-top)) 10px 8px;
  row-gap: 8px;
}

/* Lifts the six header controls out of their desktop groups into the mobile grid
   without moving a single node in the DOM (desktop order stays identical). */
html.ui-mobile .header-left,
html.ui-mobile .header-right {
  display: contents;
}

html.ui-mobile #bookSelect      { grid-area: 1 / 1 / 2 / 2; min-width: 0; }
html.ui-mobile #listSelect      { grid-area: 1 / 2 / 2 / 3; min-width: 0; }
html.ui-mobile #sortSelect      { grid-area: 1 / 3 / 2 / 4; min-width: 0; }
html.ui-mobile #quickThemeBtn   { grid-area: 1 / 4 / 2 / 5; }
html.ui-mobile #langModeGroup   { grid-area: 2 / 1 / 3 / 3; }
html.ui-mobile #layoutModeGroup { grid-area: 2 / 3 / 3 / 5; }

html.ui-mobile .top-header select,
html.ui-mobile .top-header .btn {
  min-height: var(--m-tap);
  font-size: 0.82rem;
}

html.ui-mobile .top-header .seg-group {
  min-height: calc(var(--m-tap) + 6px);
}

html.ui-mobile .ctrl-select {
  padding: 8px 26px 8px 8px;
  background-position: right 7px center;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

/* Theme + view-mode switches become iconographic so they can share a thumb row. */
html.ui-mobile #quickThemeBtn {
  font-size: 0;
  padding: 0;
  width: var(--m-tap);
  gap: 0;
}
html.ui-mobile #quickThemeBtn::before {
  content: "🎨";
  font-size: 1.15rem;
  line-height: 1;
}

html.ui-mobile #langModeGroup,
html.ui-mobile #layoutModeGroup {
  display: grid;
  gap: 0;
  padding: 3px;
  width: 100%;
}
html.ui-mobile #langModeGroup    { grid-template-columns: repeat(3, minmax(0, 1fr)); }
html.ui-mobile #layoutModeGroup  { grid-template-columns: repeat(2, minmax(0, 1fr)); }

html.ui-mobile #langModeGroup .seg-btn,
html.ui-mobile #layoutModeGroup .seg-btn {
  font-size: 0;
  padding: 0 2px;
  /* width floor too: a squeezed landscape row otherwise yields 31px segments */
  min-width: var(--m-tap);
  min-height: var(--m-tap);
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
html.ui-mobile #langModeGroup .seg-btn::after,
html.ui-mobile #layoutModeGroup .seg-btn::after {
  font-size: 0.9rem;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
}
html.ui-mobile #langModeGroup [data-lang="bilingual"]::after { content: "双语"; }
html.ui-mobile #langModeGroup [data-lang="en_only"]::after   { content: "仅英"; }
html.ui-mobile #langModeGroup [data-lang="cn_only"]::after   { content: "仅中"; }
html.ui-mobile #layoutModeGroup [data-layout="list"]::after  { content: "列表"; }
html.ui-mobile #layoutModeGroup [data-layout="card"]::after  { content: "卡片"; }

/* ---- Bottom tab bar: 6 x >=48px targets, safe-area aware, never fixed over content ---- */
html.ui-mobile .mobile-bottom-nav {
  display: grid;
  position: static;
  flex: 0 0 auto;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 3px;
  min-height: var(--m-nav-h);
  padding: 5px 4px calc(5px + var(--safe-bottom));
}

html.ui-mobile .mob-nav-btn {
  min-height: 48px;
  font-size: 0.76rem;
  gap: 3px;
  padding: 4px 2px;
  border-radius: 12px;
}

html.ui-mobile .mob-nav-btn span:first-child {
  font-size: 1.22rem;
  line-height: 1;
}

/* ---- Per-view mobile heading (the header bar no longer carries the app title) ---- */
html.ui-mobile .m-only {
  display: block;
}

html.ui-mobile .m-view-head {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin: 0 0 10px;
  padding: 0 2px;
}

html.ui-mobile .m-view-head h2 {
  font-size: 1.16rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 7px;
}

html.ui-mobile .m-view-head p {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.5;
}

html.ui-mobile .m-gesture-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--blue-soft);
  color: var(--blue-mark);
  border: 1px solid var(--blue-mark);
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.45;
  margin-bottom: 10px;
}

/* ---- Tap feedback (touch screens have no hover, so :active carries it) ---- */
html.ui-mobile a,
html.ui-mobile button,
html.ui-mobile select,
html.ui-mobile input,
html.ui-mobile label,
html.ui-mobile .word-row,
html.ui-mobile .plan-chip,
html.ui-mobile .masked-box,
html.ui-mobile .unfam-badge {
  -webkit-tap-highlight-color: rgba(5, 150, 105, 0.16);
}

html.ui-mobile .word-row:active,
html.ui-mobile .icon-btn:active,
html.ui-mobile .btn:active,
html.ui-mobile .seg-btn:active,
html.ui-mobile .nav-btn:active,
html.ui-mobile .mob-nav-btn:active,
html.ui-mobile .plan-chip:active,
html.ui-mobile .preset-pill-btn:active,
html.ui-mobile .letter-card-btn:active {
  transform: scale(0.975);
}

html.ui-mobile .icon-btn:active,
html.ui-mobile .btn:active,
html.ui-mobile .plan-chip:active {
  background: var(--bg-muted);
}

html.ui-mobile .word-row {
  touch-action: manipulation;
}

html.ui-mobile .word-row.lp-arming {
  background: var(--amber-soft);
  transition: background-color 0.42s linear 0.08s;
}

html.ui-mobile .word-row.lp-fired {
  animation: vocaLongPressPop 0.38s ease-out;
}

/* ---- Stats ---- */
html.ui-mobile .stats-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 12px;
}

html.ui-mobile .stat-card {
  padding: 12px;
  border-radius: 14px;
}

html.ui-mobile .stat-label { font-size: 0.78rem; }
html.ui-mobile .stat-val { font-size: 1.38rem; }
html.ui-mobile .stat-sub {
  font-size: 0.78rem;
  /* nowrap + ellipsis hid "本组已移除熟词 0 个 (共 257 词)" behind "…" at 320px */
  white-space: normal;
  line-height: 1.45;
}

/* ---- Learn toolbar ---- */
html.ui-mobile .learn-toolbar {
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
}

html.ui-mobile .learn-toolbar-left {
  width: 100%;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
}

html.ui-mobile .search-input {
  width: 100%;
  min-height: var(--m-tap);
  font-size: 0.95rem;
  padding: 10px 12px;
}

html.ui-mobile #clickRuleHint {
  font-size: 0.8rem;
  line-height: 1.45;
  color: var(--text-muted);
}

html.ui-mobile .learn-toolbar-right {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(140px, 100%), 1fr));
  gap: 8px;
}

/* Global touch-target floor for this shell: text inputs, selects and buttons all reach
   44 CSS px. Checkboxes keep their box size because their <label class="check-label">
   row is the actual 44px hit area. */
html.ui-mobile select,
html.ui-mobile textarea,
html.ui-mobile input:not([type="checkbox"]):not([type="file"]),
html.ui-mobile button {
  min-height: var(--m-tap);
}

html.ui-mobile .btn {
  min-height: var(--m-tap);
  padding: 10px 12px;
  font-size: 0.88rem;
}

html.ui-mobile .btn-sm {
  min-height: var(--m-tap);
  padding: 9px 10px;
  font-size: 0.84rem;
}

/* ---- Word list: card rows, own action row, 44px icon buttons ---- */
html.ui-mobile .word-list-wrap {
  border-radius: 14px;
}

html.ui-mobile .word-row {
  grid-template-columns: 26px minmax(0, 1fr);
  grid-template-areas:
    "idx head"
    ".   meaning"
    "act act";
  align-items: start;
  gap: 4px 8px;
  padding: 12px 10px;
}

html.ui-mobile .w-idx { grid-area: idx; font-size: 0.76rem; padding-top: 3px; }
html.ui-mobile .w-head-col { grid-area: head; }
html.ui-mobile .w-meaning-col { grid-area: meaning; margin-top: 4px; }
html.ui-mobile .w-actions {
  grid-area: act;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

html.ui-mobile .w-word { font-size: 1.18rem; gap: 7px; }
html.ui-mobile .w-ipa { font-size: 0.86rem; }
html.ui-mobile .w-cn { font-size: 0.95rem; }
html.ui-mobile .w-ex { font-size: 0.82rem; }

html.ui-mobile .icon-btn {
  width: var(--m-tap);
  height: var(--m-tap);
  border-radius: 12px;
  font-size: 1.15rem;
}

html.ui-mobile .unfam-badge { font-size: 0.72rem; padding: 3px 7px; }
html.ui-mobile .unfam-dot { width: 7px; height: 7px; }

html.ui-mobile #learnListPagination {
  flex-wrap: wrap;
  gap: 8px;
}

html.ui-mobile #learnListPagination .btn {
  flex: 1 1 min(150px, 100%);
}

/* ---- Immersive card ---- */
html.ui-mobile .immersive-stage {
  max-width: none;
  margin: 0;
  padding: 16px 14px calc(18px + var(--safe-bottom));
  border-radius: 18px;
  gap: 14px;
}

html.ui-mobile .card-word-title {
  font-size: clamp(1.7rem, 8.4vw, 2.3rem);
  padding: 8px 10px;
}

html.ui-mobile .card-word-title.masked-headword { font-size: 1.05rem; }
html.ui-mobile .card-section-box { padding: 13px 14px; }
html.ui-mobile .card-phonetic-bar { gap: 10px; font-size: 0.95rem; }

html.ui-mobile .card-bottom-nav {
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
}

html.ui-mobile .card-prev-next-wrap,
html.ui-mobile .card-unfam-controls {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

html.ui-mobile .card-unfam-controls { order: 1; }
html.ui-mobile .card-prev-next-wrap { order: 2; }

html.ui-mobile .card-prev-next-wrap .btn,
html.ui-mobile .card-unfam-controls .btn {
  width: 100%;
  padding: 10px 6px;
  font-size: 0.86rem;
}

/* ---- Ebbinghaus plan: 8-column desktop matrix becomes one card per study day ---- */
html.ui-mobile .plan-custom-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(170px, 100%), 1fr));
  gap: 10px;
  padding: 12px;
}

html.ui-mobile .plan-custom-bar > label {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
}

html.ui-mobile .ctrl-input-num {
  min-height: var(--m-tap);
  width: 92px;
  font-size: 1rem;
}

html.ui-mobile .plan-preset-pills {
  width: 100%;
  grid-column: 1 / -1;
  gap: 8px;
}

html.ui-mobile .preset-pill-btn {
  min-height: var(--m-tap);
  min-width: 44px;
  padding: 8px 12px;
  font-size: 0.84rem;
  flex: 1 1 auto;
}

html.ui-mobile #btnApplyCustomPlan {
  grid-column: 1 / -1;
  width: 100%;
}

html.ui-mobile .matrix-table-wrap {
  overflow: visible;
  border-radius: 14px;
}

/* The DOM stays a real <table> (renderEbbinghausPlan still writes <tr>/<td> into
   #ebbinghausTableBody and the chip click handler still lives on that tbody); only
   the box model changes, so every id, class and click semantic survives. */
html.ui-mobile .matrix-table,
html.ui-mobile .matrix-table tbody {
  display: block;
}

html.ui-mobile .matrix-table thead {
  display: none;
}

html.ui-mobile .matrix-table tr {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 6px 10px;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

html.ui-mobile .matrix-table td {
  border: none;
  padding: 0;
  text-align: left;
  font-size: 0.86rem;
}

html.ui-mobile .matrix-table td:first-child {
  grid-column: 1;
  grid-row: 1;
  font-size: 1.05rem;
  font-weight: 800;
}

html.ui-mobile .matrix-table td:last-child {
  grid-column: 2;
  grid-row: 1;
  text-align: right;
  font-size: 0.8rem;
  white-space: nowrap;
}

html.ui-mobile .matrix-table td:nth-child(n+2):nth-child(-n+7) {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-height: 44px;
}

html.ui-mobile .matrix-table td:nth-child(n+2):nth-child(-n+7)::before {
  flex: 0 0 auto;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  background: var(--bg-muted);
  border-radius: 6px;
  padding: 3px 7px;
}

html.ui-mobile .matrix-table td:nth-child(2)::before { content: "初记新学"; }
html.ui-mobile .matrix-table td:nth-child(3)::before { content: "复习 1"; }
html.ui-mobile .matrix-table td:nth-child(4)::before { content: "复习 2"; }
html.ui-mobile .matrix-table td:nth-child(5)::before { content: "复习 3"; }
html.ui-mobile .matrix-table td:nth-child(6)::before { content: "复习 4"; }
html.ui-mobile .matrix-table td:nth-child(7)::before { content: "复习 5"; }

html.ui-mobile .plan-chip {
  min-height: var(--m-tap);
  min-width: 92px;
  padding: 8px 12px;
  margin: 0;
  font-size: 0.86rem;
  border-radius: 12px;
  justify-content: center;
}

html.ui-mobile .m-plan-legend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 8px 2px 0;
  line-height: 1.5;
}

/* ---- Training: spelling drill ---- */
html.ui-mobile .spell-stage {
  max-width: none;
  margin: 0;
  padding: 14px 12px calc(16px + var(--safe-bottom));
  border-radius: 18px;
}

html.ui-mobile .spell-slots {
  gap: 5px;
  margin: 16px 0;
}

html.ui-mobile .spell-slot {
  width: 30px;
  height: 44px;
  font-size: 1.15rem;
}

html.ui-mobile .five-cards-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 6px;
  margin: 14px 0;
}

html.ui-mobile .letter-card-btn {
  width: 100%;
  min-height: 56px;
  font-size: 1.3rem;
}

html.ui-mobile #spellBtnBackspace {
  width: 100%;
  min-height: var(--m-tap);
  font-size: 1.3rem;
}

html.ui-mobile .spell-key-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) var(--m-tap);
  gap: 8px;
  align-items: center;
  margin-top: 12px;
}

html.ui-mobile input[type="checkbox"] {
  width: 22px;
  height: 22px;
  accent-color: var(--brand-primary);
  flex-shrink: 0;
}

/* Both checkboxes live inside their <label>, so the whole 44px row toggles them.
   (Class-based rather than :has() so older WebViews keep the large hit area.) */
html.ui-mobile .check-label {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-height: var(--m-tap);
  cursor: pointer;
}

/* ---- Training: auto-scroll drill ---- */
html.ui-mobile .scroll-viewport {
  max-height: none;
  height: min(60vh, 520px);
  height: min(60dvh, 520px);
}

html.ui-mobile #trainPanelScroll .stat-card {
  flex-direction: column;
  align-items: stretch;
}

/* ---- Notebook ---- */
html.ui-mobile #nbSubTabGroup,
html.ui-mobile #trainSubModeGroup {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  width: 100%;
  gap: 0;
}

html.ui-mobile #nbSubTabGroup .seg-btn,
html.ui-mobile #trainSubModeGroup .seg-btn {
  min-height: var(--m-tap);
  font-size: 0.86rem;
  padding: 6px 4px;
  white-space: normal;
  text-align: center;
}

html.ui-mobile #nbStarredControls,
html.ui-mobile #nbMasteredControls {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(160px, 100%), 1fr));
  gap: 8px;
}

/* ---- Data & settings ---- */
html.ui-mobile .panel-grid,
html.ui-mobile .panel-grid-inner {
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
}

html.ui-mobile #view-data .stat-card,
html.ui-mobile #view-settings .stat-card {
  padding: 14px !important;
}

html.ui-mobile #view-data textarea,
html.ui-mobile #pasteImportTextarea {
  min-height: 96px;
  font-size: 0.9rem;
  line-height: 1.6;
}

html.ui-mobile #view-settings .stat-card > label:not(.check-label) {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.88rem;
  line-height: 1.5;
}

html.ui-mobile #view-settings .ctrl-select {
  width: 100%;
  min-height: var(--m-tap);
  font-size: 0.92rem;
  margin-top: 0 !important;
}

html.ui-mobile #view-settings label[for],
html.ui-mobile #view-data label.btn {
  min-height: var(--m-tap);
}

html.ui-mobile #view-data .btn,
html.ui-mobile #view-settings .btn {
  min-height: var(--m-tap);
}

/* ---- Modals become full-width bottom sheets with ONE scroller ---- */
html.ui-mobile .modal-backdrop {
  padding: 0;
  align-items: flex-end;
  background: rgba(15, 23, 42, 0.62);
}

html.ui-mobile .modal-panel {
  max-width: none;
  width: 100%;
  border-radius: 22px 22px 0 0;
  border-bottom: none;
  padding: 20px 14px calc(20px + var(--safe-bottom));
  max-height: calc(100vh - 24px);
  max-height: calc(100dvh - var(--safe-top) - 24px);
  overflow-y: auto;
  box-shadow: 0 -14px 40px -10px rgba(15, 23, 42, 0.4);
}

html.ui-mobile .modal-panel::before {
  content: "";
  display: block;
  width: 44px;
  height: 4px;
  border-radius: 99px;
  background: var(--border-strong);
  margin: -8px auto 12px;
}

html.ui-mobile .modal-panel .btn,
html.ui-mobile .modal-panel .btn-sm {
  min-height: var(--m-tap);
}

html.ui-mobile .modal-panel input[type="text"],
html.ui-mobile .modal-panel input[type="search"],
html.ui-mobile .modal-panel select {
  min-height: var(--m-tap);
  font-size: 1rem;
}

/* The dictionary sheet used to nest a 240px scroller inside the panel scroller.
   Parsed entries now flow with the page, so the panel is the only scroller. */
html.ui-mobile #modalDictParsedContent {
  max-height: none;
  overflow: visible;
}

html.ui-mobile #modalDictIframeWrap {
  height: 320px;
  height: clamp(220px, 42vh, 420px);
}

html.ui-mobile #modalDictSourceGroup {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  width: 100%;
  gap: 0;
}

html.ui-mobile #modalDictSourceGroup .seg-btn {
  min-height: var(--m-tap);
  font-size: 0.82rem;
  padding: 6px 2px;
  white-space: normal;
}

html.ui-mobile .dict-online-header {
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
}

html.ui-mobile .dict-online-header > div {
  width: 100%;
}

html.ui-mobile .dict-status-banner { font-size: 0.86rem; }
html.ui-mobile .dict-parsed-entries { font-size: 0.92rem; }

html.ui-mobile #printModal .modal-panel {
  max-height: calc(100vh - 12px);
  max-height: calc(100dvh - var(--safe-top) - 12px);
}

/* An A4 sheet is wider than a phone. The preview gets its own sideways scroller
   (the panel keeps the only vertical one), so nothing is silently clipped; the real
   export path (#dedicatedPrintRoot + @page) is untouched. */
html.ui-mobile #printSheetBody {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  padding-bottom: 6px;
}

/* ---- Toasts sit above the tab bar (offset comes from the bar's own declared height) ---- */
html.ui-mobile .toast-container {
  left: 12px;
  right: 12px;
  bottom: calc(var(--m-nav-h) + var(--safe-bottom) + 10px);
  max-width: none;
}

html.ui-mobile .toast-item {
  font-size: 0.88rem;
  padding: 12px 14px;
}

/* ---- Landscape phones / short viewports: reclaim vertical space ---- */
@media (orientation: landscape) and (max-height: 600px) {
  html.ui-mobile {
    --m-nav-h: 50px;
    --m-gap: 8px;
  }
  /* One row instead of two: landscape phones have width but very little height. */
  html.ui-mobile .top-header {
    /* the two mode switches get explicit floors so an overflowing row cannot squeeze a
       segment below the 44px target width */
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr) minmax(0, 0.85fr) var(--m-tap) minmax(144px, auto) minmax(104px, auto);
    grid-template-rows: auto;
    padding: calc(6px + var(--safe-top)) 10px 6px;
  }
  html.ui-mobile #bookSelect      { grid-area: 1 / 1; }
  html.ui-mobile #listSelect      { grid-area: 1 / 2; }
  html.ui-mobile #sortSelect      { grid-area: 1 / 3; }
  html.ui-mobile #quickThemeBtn   { grid-area: 1 / 4; }
  html.ui-mobile #langModeGroup   { grid-area: 1 / 5; }
  html.ui-mobile #layoutModeGroup { grid-area: 1 / 6; }
  html.ui-mobile .mob-nav-btn {
    flex-direction: row;
    gap: 6px;
    min-height: 44px;
    font-size: 0.78rem;
  }
  html.ui-mobile .mob-nav-btn span:first-child { font-size: 1.05rem; }
  html.ui-mobile .scroll-viewport { height: min(52vh, 420px); }
  html.ui-mobile .immersive-stage { padding: 12px 14px; }
}

/* ---- Very narrow phones (<= 360px CSS): shed non-essential chrome ---- */
@media (max-width: 360px) {
  html.ui-mobile { --m-gap: 8px; }
  /* Two columns at 320px leaves ~140px per card, so labels wrapped mid-word. */
  html.ui-mobile .stats-grid { grid-template-columns: minmax(0, 1fr); }
  html.ui-mobile #langModeGroup .seg-btn::after,
  html.ui-mobile #layoutModeGroup .seg-btn::after { font-size: 0.84rem; }
  html.ui-mobile .top-header select { font-size: 0.78rem; }
  html.ui-mobile .learn-toolbar-right { grid-template-columns: minmax(0, 1fr); }
  html.ui-mobile .spell-slot { width: 26px; }
}

/* ---- Tablets / large touch surfaces: use the width, keep touch chrome ---- */
@media (min-width: 640px) {
  html.ui-mobile .page-container { padding: 14px 16px calc(24px + var(--safe-bottom)); }
  html.ui-mobile .stats-grid { grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr)); }
  html.ui-mobile .panel-grid,
  html.ui-mobile .panel-grid-inner { grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr)); }
  html.ui-mobile .modal-backdrop { padding: 16px calc(16px + var(--safe-right)) 16px calc(16px + var(--safe-left)); align-items: center; }
  html.ui-mobile .modal-panel { border-radius: 22px; border-bottom: 1px solid var(--border-color); max-height: calc(100dvh - 32px); }
  html.ui-mobile .mob-nav-btn { font-size: 0.8rem; }
  html.ui-mobile .mob-nav-btn span:first-child { font-size: 1.35rem; }
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
  /* The touch shell makes <body> a fixed-height flex column; printing from a phone must
     not inherit that clip or the export collapses to a single page. */
  html.ui-mobile,
  html.ui-mobile body {
    display: block !important;
    height: auto !important;
    min-height: 0 !important;
    overflow: visible !important;
    padding: 0 !important;
  }
  html.ui-mobile .m-only {
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
<script>
/* ==================== INPUT-CAPABILITY SHELL SELECTOR ====================
   The phone/tablet presentation used to be chosen by viewport WIDTH alone, which
   gave a landscape phone the 256px desktop sidebar and gave a narrow desktop window
   phone chrome. Shell is now chosen by what the primary pointing device IS:

     ui-mobile  -> primary pointer is coarse (finger), or hover is impossible and the
                   device is touch-capable, or a legacy Android WebView that predates
                   the (pointer:)/(hover:) media features is a touch device in a narrow
                   window.
     ui-desktop -> fine pointer with hover (mouse / trackpad / WebView2 on Windows),
                   at ANY width. A narrow desktop window keeps the sidebar (it just
                   collapses to an icon rail below 860px) instead of getting phone chrome.

   Runs in <head> before the first paint so there is no chrome flash, and re-runs on
   resize / orientationchange / media-query change so a rotating phone re-selects.
   Purely presentational: nothing here is persisted and no learning state is touched. */
(function () {
  var root = document.documentElement;
  function mq(q) {
    try { return !!(window.matchMedia && window.matchMedia(q).matches); } catch (e) { return false; }
  }
  function touchCapable() {
    return ("ontouchstart" in window) || ((navigator.maxTouchPoints || 0) > 0);
  }
  function isTouchShell() {
    if (mq("(pointer: coarse)")) return true;
    if (mq("(hover: none)") && touchCapable()) return true;
    /* Android WebView older than Chrome 39 understands neither (pointer:) nor (hover:). */
    var narrow = Math.min(window.innerWidth || 4000, (window.screen && window.screen.width) || 4000) <= 900;
    if (/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || "") && touchCapable() && narrow) return true;
    return false;
  }
  function applyShell() {
    var touch = isTouchShell();
    root.classList.toggle("ui-mobile", touch);
    root.classList.toggle("ui-desktop", !touch);
    root.setAttribute("data-ui", touch ? "mobile" : "desktop");
  }
  applyShell();
  window.addEventListener("resize", applyShell);
  window.addEventListener("orientationchange", applyShell);
  ["(pointer: coarse)", "(hover: none)", "(orientation: landscape)"].forEach(function (q) {
    try {
      var r = window.matchMedia(q);
      if (!r) return;
      if (r.addEventListener) r.addEventListener("change", applyShell);
      else if (r.addListener) r.addListener(applyShell);
    } catch (e) {}
  });
  /* Read-only helper for the app engine and for automated verification. */
  window.__VOCA_IS_TOUCH__ = isTouchShell;
})();
</script>
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
    .replace("__ICON_40_B64__", ASSETS["icon_40_b64"])
    .replace("__ICON_36_B64__", ASSETS["icon_36_b64"])
    .replace("__ICON_32_B64__", ASSETS["icon_32_b64"])
    .replace("__ICON_28_B64__", ASSETS["icon_28_b64"])
    .replace("__ICON_24_B64__", ASSETS["icon_24_b64"])
    .replace("__ICON_20_B64__", ASSETS["icon_20_b64"])
    .replace("__ICON_16_B64__", ASSETS["icon_16_b64"])
    .replace("__INTER_REG_B64__", ASSETS["inter_regular_woff2_b64"])
    .replace("__INTER_BOLD_B64__", ASSETS["inter_bold_woff2_b64"])
    .replace("__NOTO_FULL_CJK_B64__", ASSETS["noto_full_cjk_woff2_b64"])
)

if __name__ == "__main__":
    print("make_html_v103_part1 ready, length:", len(HTML_PART1))
