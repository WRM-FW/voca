#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates Part 2 of Voca v1.0.3 HTML Application:
- High-DPI 256x256 brand icon in sidebar (v1.0.3 badge).
- Removed '英英模式' (en_en) button from #langModeGroup (retains 双语 / 只看英文 / 只看中文).
- Removed all '掌握度' (mastery) UI elements, keeping only '不会程度' (unfamiliarity 0..5).
- Redesigned '#dictModal' ("查看词典详细与编辑"):
  - Deleted '英英释义与同义词拓展' and '双语语境例句与助记' blocks.
  - Integrated Online Dictionary lookup panel supporting Eudic (https://dict.eudic.net/dicts/en/@word@) and WordReference (https://www.wordreference.com/enzh/@word@) with honest online/offline/error/not-found feedback.
- Added '#settingOnlineDict' persistent selector in '偏好设置与帮助'.
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

HTML_PART2_TEMPLATE = r"""
<div class="app-layout">
  <!-- Desktop Sidebar: Settings docked at the bottom of the sidebar -->
  <aside class="sidebar">
    <div class="brand-box">
      <img class="brand-logo" src="data:image/png;base64,__ICON_256_B64__" alt="Voca Logo">
      <div>
        <div class="brand-title">Voca <span class="brand-badge">v1.0.3</span></div>
        <div class="brand-sub">艾宾浩斯双平台背单词工坊</div>
      </div>
    </div>

    <nav class="nav-list" id="desktopNav">
      <button class="nav-btn active" data-tab="learn" id="navBtnLearn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
        <span>单词学习</span>
        <span class="nav-pill" id="pillActiveCount">0</span>
      </button>
      <button class="nav-btn" data-tab="plan" id="navBtnPlan">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        <span>艾宾浩斯计划表</span>
        <span class="nav-pill" id="pillPlanDone">0%</span>
      </button>
      <button class="nav-btn" data-tab="train" id="navBtnTrain">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        <span>专项强化训练</span>
        <span class="nav-pill">拼词/滚动</span>
      </button>
      <button class="nav-btn" data-tab="notebook" id="navBtnNotebook">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <span>生词本与熟词表</span>
        <span class="nav-pill" id="pillStarCount">0</span>
      </button>
      <button class="nav-btn" data-tab="data" id="navBtnData">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        <span>词库导入与PDF导出</span>
      </button>
      <button class="nav-btn nav-btn-bottom" data-tab="settings" id="navBtnSettings">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        <span>偏好设置与帮助</span>
      </button>
    </nav>
  </aside>

  <!-- Main Workspace -->
  <div class="main-area">
    <!-- Top Global Toolbar -->
    <header class="top-header">
      <div class="header-left">
        <select id="bookSelect" class="ctrl-select" title="选择当前内置词书 (共38,855词条)">
          <option value="cet4" selected>四级核心 (CET-4 · 3,849词)</option>
          <option value="cet6">六级核心 (CET-6 · 5,407词)</option>
          <option value="ky">考研核心 (硕士统考 · 4,801词)</option>
          <option value="zk">中考核心 (初中必备 · 1,603词)</option>
          <option value="gk">高考核心 (高中必备 · 3,677词)</option>
          <option value="toefl">托福核心 (TOEFL · 6,974词)</option>
          <option value="ielts">雅思核心 (IELTS · 5,040词)</option>
          <option value="gre">GRE 核心 (GRE高阶 · 7,504词)</option>
          <option value="core233">Voca 深度双解精编词库 (233词)</option>
          <option value="custom">用户自定义导入词库</option>
        </select>

        <select id="listSelect" class="ctrl-select" title="选择当前 List 分组"></select>

        <!-- Requirement 5: Language Mode Switcher (双语 / 只看英文 / 只看中文; 英英模式已移除) -->
        <div class="seg-group" id="langModeGroup">
          <button class="seg-btn active" data-lang="bilingual">双语</button>
          <button class="seg-btn" data-lang="en_only">只看英文</button>
          <button class="seg-btn" data-lang="cn_only">只看中文</button>
        </div>
      </div>

      <div class="header-right">
        <!-- View Switcher: List View vs Card View -->
        <div class="seg-group" id="layoutModeGroup">
          <button class="seg-btn active" data-layout="list">列表视图</button>
          <button class="seg-btn" data-layout="card">沉浸卡片</button>
        </div>

        <!-- Requirement 2: Sort options based on Unfamiliarity (不会程度), Mastery removed -->
        <select id="sortSelect" class="ctrl-select" title="当前List内部排序">
          <option value="initial">初始排列</option>
          <option value="az">按字母 A→Z</option>
          <option value="random">随机打乱</option>
          <option value="hard_first">不会程度从高到低</option>
          <option value="easy_first">不会程度从低到高</option>
        </select>

        <button class="btn btn-sm" id="quickThemeBtn" title="切换显示主题 (晨曦白 / 纯黑OLED / 羊皮纸)">主题: 晨曦白</button>
      </div>
    </header>

    <main class="page-container">
      <!-- ==================== VIEW 1: LEARN & LIST STUDIO ==================== -->
      <section class="view-section active" id="view-learn">
        <div class="mode-hint-banner" id="modeFirstTimeBanner">
          <span id="modeFirstTimeText">💡 提示：点击遮罩区域即可发音或窥显隐藏内容。</span>
          <button class="btn btn-sm" id="btnDismissModeBanner">我知道了</button>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label"><span>当前 List 待学</span><span style="color:var(--brand-primary);">越背越小</span></div>
            <div class="stat-val" id="statCurrentListCount">0</div>
            <div class="stat-sub" id="statCurrentListSub">本组已移除熟词 0 个</div>
          </div>
          <div class="stat-card">
            <div class="stat-label"><span>当前词库总进度</span><span>熟词率</span></div>
            <div class="stat-val" id="statBookProgress">0%</div>
            <div class="stat-sub" id="statBookSub">总词数 0 · 已熟 0</div>
          </div>
          <div class="stat-card">
            <div class="stat-label"><span>生词本强化</span><span>★ 收藏</span></div>
            <div class="stat-val" id="statStarredTotal">0</div>
            <div class="stat-sub">点★加入生词本</div>
          </div>
          <div class="stat-card">
            <div class="stat-label"><span>艾宾浩斯计划</span><span id="statPlanConfigTag">15组/30天</span></div>
            <div class="stat-val" id="statPlanCheckins">0</div>
            <div class="stat-sub" id="statTodayTaskHint">点击计划表可跳转对应 List</div>
          </div>
        </div>

        <!-- Action Strip above word list -->
        <div class="learn-toolbar">
          <div class="learn-toolbar-left">
            <input type="search" id="wordSearchInput" class="search-input" placeholder="搜索当前List单词或释义...">
            <span style="font-size:0.78rem; color:var(--text-muted);" id="clickRuleHint">左键/轻触单词行：不会程度+1并发音 · 右键点击：不会程度-1</span>
          </div>
          <div class="learn-toolbar-right">
            <button class="btn btn-sm btn-primary" id="btnCheckinCurrentList">✓ 完成本组打卡</button>
            <button class="btn btn-sm" id="btnOpenMasteredDrawer">熟词恢复 (<span id="inlineMasteredCnt">0</span>)</button>
            <button class="btn btn-sm" id="btnPrintCurrentList">🖨️ 导出本组 PDF</button>
          </div>
        </div>

        <!-- Subview A: Classic List View -->
        <div id="learnListContainer" class="word-list-wrap"></div>
        <div id="learnListPagination" style="display:none; justify-content:center; align-items:center; gap:12px; margin-top:14px;">
          <button class="btn btn-sm" id="btnLoadMoreWords">加载更多单词...</button>
          <button class="btn btn-sm" id="btnShowAllWordsInList">显示本 List 全部单词</button>
        </div>

        <!-- Subview B: Immersive Card View (Retains only Unfamiliarity, Mastery removed) -->
        <div id="learnCardContainer" style="display:none;">
          <div class="immersive-stage" id="immersiveCardStage">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
              <span style="font-size:0.82rem; font-weight:700; color:var(--text-muted);" id="cardPosIndicator">1 / 15</span>
              <div style="display:flex; gap:6px; flex-wrap:wrap;">
                <button class="btn btn-sm" id="cardBtnStar">★ 生词本</button>
                <button class="btn btn-sm" id="cardBtnMaster">✕ 标为熟词</button>
                <button class="btn btn-sm" id="cardBtnDict">📖 词典详情</button>
              </div>
            </div>

            <div style="padding:6px 0; text-align:center;">
              <div class="card-word-title" id="cardHeadword" title="点击朗读发音（只看中文模式下点击可窥显英文并发音）">abandon</div>
              <div class="card-phonetic-bar" style="margin-top:6px;">
                <span id="cardPhoneticText">/əˈbændən/</span>
                <button class="btn btn-sm" id="cardBtnSpeak">🔊 朗读发音</button>
              </div>
              <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin-top:8px; flex-wrap:wrap;">
                <span style="font-size:0.80rem; color:var(--text-muted); display:inline-flex; align-items:center; gap:6px;">
                  不会程度: <span id="cardUnfamDots" class="unfam-dots"></span> (<span id="cardUnfamNum">0</span>/5)
                </span>
              </div>
            </div>

            <div class="card-section-box" id="cardMeaningBox" style="cursor:pointer;" title="点击切换窥显释义并朗读发音">
              <div style="font-size:1.12rem; font-weight:700; color:var(--text-primary);" id="cardCnDef"></div>
            </div>

            <div class="card-section-box" id="cardExampleBox">
              <div style="font-size:0.95rem; font-weight:600; color:var(--text-primary); margin-bottom:4px;" id="cardExEn"></div>
              <div style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:8px;" id="cardExCn"></div>
              <div style="font-size:0.79rem; color:var(--amber-mark); background:var(--amber-soft); padding:6px 10px; border-radius:8px;" id="cardMnemonic"></div>
            </div>

            <div class="card-bottom-nav">
              <div class="card-prev-next-wrap">
                <button class="btn" id="cardBtnPrev">← 上一词 (J)</button>
                <button class="btn" id="cardBtnNext">下一词 (K) →</button>
              </div>
              <div class="card-unfam-controls">
                <button class="btn btn-sm" id="cardBtnUnfamDown" title="降低不会程度 (-1)">不会程度 -1</button>
                <button class="btn btn-sm btn-primary" id="cardBtnUnfamUp" title="加深不会程度 (+1)">不会程度 +1</button>
                <button class="btn btn-sm" id="cardBtnUnfamReset" title="重置不会程度为 0">重置不会度</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== VIEW 2: CUSTOMIZABLE EBBINGHAUS PLAN MATRIX ==================== -->
      <section class="view-section" id="view-plan">
        <div class="stat-card" style="margin-bottom:16px; padding:18px 20px;">
          <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-start; gap:12px;">
            <div>
              <h2 style="font-size:1.22rem; font-weight:800;" id="planHeaderTitle">艾宾浩斯遗忘曲线学习计划表（支持自由定义 List 个数与学习周期天数）</h2>
              <p style="font-size:0.84rem; color:var(--text-muted); margin-top:4px; white-space:normal;">
                💡 <strong>自定义与无损保护说明</strong>：您可以自由设定任意 <strong>List 数量 (1~365)</strong> 与 <strong>学习周期天数 (1~730)</strong>。调整参数后系统将重新均匀划分词书并自适应生成每日新学与 5 轮艾宾浩斯复习日程，<strong>所有已背单词的不会程度、生词本、熟词表及打卡记录 100% 保留不丢失</strong>。
              </p>
            </div>
            <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
              <button class="btn btn-sm btn-primary" id="btnPrintPlanSchedule">🖨️ 导出计划表 PDF/打印版</button>
              <button class="btn btn-sm" id="btnResetPlanChecks">重置打卡记录</button>
            </div>
          </div>

          <div class="plan-custom-bar">
            <label style="font-size:0.85rem; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
              自定义 List 个数:
              <input type="number" id="planListCountInput" class="ctrl-input-num" min="1" max="365" step="1" value="15" title="自由输入 List 总数 (1 ~ 365)">
              <span style="font-size:0.78rem; color:var(--text-muted); font-weight:500;">组</span>
            </label>

            <label style="font-size:0.85rem; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
              自定义学习周期天数:
              <input type="number" id="planCycleDaysInput" class="ctrl-input-num" min="1" max="730" step="1" value="30" title="自由输入学习总周期天数 (1 ~ 730)">
              <span style="font-size:0.78rem; color:var(--text-muted); font-weight:500;">天</span>
            </label>

            <label style="font-size:0.85rem; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
              词序分配:
              <select id="planOrderModeSelect" class="ctrl-select">
                <option value="shuffle">乱序版本 (随机均分)</option>
                <option value="az">正序版本 (A-Z均分)</option>
                <option value="original">原序版本 (保持考纲词频序)</option>
              </select>
            </label>

            <button class="btn btn-primary btn-sm" id="btnApplyCustomPlan">✓ 应用自定义计划配置</button>

            <div class="plan-preset-pills" id="planPresetPills">
              <span style="font-size:0.76rem; color:var(--text-muted);">快捷填充:</span>
              <button type="button" class="preset-pill-btn" data-n="7" data-d="14">7组/14天</button>
              <button type="button" class="preset-pill-btn" data-n="10" data-d="25">10组/25天</button>
              <button type="button" class="preset-pill-btn active" data-n="15" data-d="30">15组/30天</button>
              <button type="button" class="preset-pill-btn" data-n="21" data-d="36">21组/36天</button>
              <button type="button" class="preset-pill-btn" data-n="30" data-d="45">30组/45天</button>
            </div>
          </div>

          <div style="font-size:0.80rem; color:var(--brand-primary); font-weight:600; margin-top:8px;" id="planFormulaSummary">
            当前计划参数：共 15 个 List（每组约 257 词）· 总周期 30 天 · 艾宾浩斯复习间隔：+1天, +2天, +4天, +7天, +15天
          </div>
        </div>

        <div class="stat-card" style="margin-bottom:16px; padding:16px 20px; border-left:4px solid var(--brand-primary);">
          <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px;">
            <div>
              <div style="font-size:0.82rem; font-weight:700; color:var(--brand-primary);">当前聚焦日程 (Day <span id="planActiveDayNum">1</span> / <span id="planTotalDaysSpan">30</span>)</div>
              <div style="font-size:1.00rem; font-weight:700; margin-top:3px; white-space:normal;" id="planActiveDaySummary">今日新学: List 1 · 今日待复习: 无</div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <label style="font-size:0.82rem; font-weight:600;">聚焦日程:
                <select id="planDayPicker" class="ctrl-select"></select>
              </label>
            </div>
          </div>
        </div>

        <div class="matrix-table-wrap">
          <table class="matrix-table">
            <thead>
              <tr id="ebbinghausTableHeadRow">
                <th style="width:76px;">天数</th>
                <th style="width:130px;">初记新学</th>
                <th id="thRev1">复习周期 1 (+1天)</th>
                <th id="thRev2">复习周期 2 (+2天)</th>
                <th id="thRev3">复习周期 3 (+4天)</th>
                <th id="thRev4">复习周期 4 (+7天)</th>
                <th id="thRev5">复习周期 5 (+15天)</th>
                <th style="width:110px;">当日完成度</th>
              </tr>
            </thead>
            <tbody id="ebbinghausTableBody"></tbody>
          </table>
        </div>
      </section>

      <!-- ==================== VIEW 3: SPECIALIZED TRAINING (拼词 + 滚动) ==================== -->
      <section class="view-section" id="view-train">
        <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px; margin-bottom:16px;">
          <div class="seg-group" id="trainSubModeGroup">
            <button class="seg-btn active" data-tmode="spell">🔤 拼词模式 (5卡片点选+键盘)</button>
            <button class="seg-btn" data-tmode="scroll">📜 自动滚动模式</button>
          </div>

          <div style="display:flex; align-items:center; gap:10px;">
            <label style="font-size:0.84rem; font-weight:600;">训练词源:
              <select id="trainSourceSelect" class="ctrl-select">
                <option value="current_list">当前选中 List</option>
                <option value="starred">生词本重难词</option>
              </select>
            </label>
          </div>
        </div>

        <!-- Training Mode A: 5-Card Spelling + Keyboard Typing -->
        <div id="trainPanelSpell" class="spell-stage">
          <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; margin-bottom:12px;">
            <span style="font-size:0.82rem; font-weight:700; color:var(--text-muted);" id="spellProgressText">拼词挑战 1 / 15</span>
            <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
              <label style="font-size:0.78rem; color:var(--text-secondary); display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
                <input type="checkbox" id="spellAutoAdvanceToggle" checked> 自动下一词
              </label>
              <button class="btn btn-sm" id="spellBtnAddHard" title="加深该词不会程度 (+1)">+1 不会程度</button>
              <button class="btn btn-sm" id="spellBtnHint">💡 提示</button>
              <button class="btn btn-sm" id="spellBtnSpeak">🔊 发音</button>
            </div>
          </div>

          <div style="background:var(--bg-elevated); border-radius:14px; padding:14px; margin-bottom:14px;">
            <div style="font-size:1.15rem; font-weight:800; color:var(--text-primary); word-break:break-word;" id="spellCnPrompt">v. 放弃，遗弃；n. 放任</div>
            <div style="font-size:0.86rem; color:var(--text-muted); margin-top:4px;" id="spellIpaPrompt">/əˈbændən/</div>
            <div style="font-size:0.86rem; color:var(--text-secondary); margin-top:8px; word-break:break-word;" id="spellClozePrompt">They had to _______ their car in the deep snow.</div>
          </div>

          <div class="spell-slots" id="spellSlotsBox"></div>

          <div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:6px;">
            请点选下方 5 个字母卡片，或直接使用键盘输入字母（退格键删除，回车键确认）：
          </div>
          <div class="five-cards-row" id="spellFiveCardsBox"></div>

          <div style="display:flex; justify-content:center; gap:10px; margin-top:14px;">
            <button class="btn" id="spellBtnPrev">← 上一词</button>
            <button class="btn btn-primary" id="spellBtnSubmit">确认 / 下一词 (Enter) →</button>
          </div>
        </div>

        <!-- Training Mode B: Auto-Scroll Mode -->
        <div id="trainPanelScroll" style="display:none;">
          <div class="stat-card" style="margin-bottom:12px; display:flex; flex-direction:row; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px;">
            <div>
              <span style="font-weight:800;">📜 自动循环滚动记忆流</span>
              <span style="font-size:0.80rem; color:var(--text-muted); margin-left:6px;">悬停或触摸列表自动暂停，支持左/右键调节不会程度、标星或查在线词典</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <label style="font-size:0.82rem; font-weight:600;">速度:
                <select id="scrollSpeedSelect" class="ctrl-select">
                  <option value="1">慢速 (0.6x)</option>
                  <option value="2" selected>适中 (1.0x)</option>
                  <option value="3">快速 (1.6x)</option>
                  <option value="5">极速刷词 (2.5x)</option>
                </select>
              </label>
              <button class="btn btn-primary btn-sm" id="scrollBtnToggle">▶ 开启自动滚动</button>
            </div>
          </div>

          <div id="scrollViewport" style="max-height:540px; overflow-y:auto; border:1px solid var(--border-color); border-radius:16px; background:var(--bg-surface);">
            <div id="scrollListContent"></div>
          </div>
        </div>
      </section>

      <!-- ==================== VIEW 4: NOTEBOOK & MASTERED (生词本与熟词表) ==================== -->
      <section class="view-section" id="view-notebook">
        <div style="display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:12px; margin-bottom:14px;">
          <div class="seg-group" id="nbSubTabGroup">
            <button class="seg-btn active" data-nbtab="starred">★ 生词本 (<span id="nbStarCountTab">0</span>)</button>
            <button class="seg-btn" data-nbtab="mastered">✓ 熟词表 (<span id="nbMasterCountTab">0</span>)</button>
          </div>

          <div id="nbStarredControls" style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
            <select id="nbSortSelect" class="ctrl-select" title="生词本排序方式">
              <option value="newest">从新到旧 (最新收藏在前)</option>
              <option value="oldest">从旧到新 (最早收藏在前)</option>
              <option value="az">按字母从 A 到 Z</option>
              <option value="za">按字母从 Z 到 A</option>
              <option value="random">随机乱序排列</option>
            </select>
            <button class="btn btn-sm btn-primary" id="btnAddCustomWordModal">+ 手动添加新单词</button>
            <button class="btn btn-sm" id="btnPrintStarredBook">🖨️ 导出生词本 PDF</button>
          </div>

          <div id="nbMasteredControls" style="display:none; align-items:center; gap:8px;">
            <button class="btn btn-sm" id="btnRestoreAllMastered">↺ 批量恢复全部熟词到词库</button>
          </div>
        </div>

        <div class="stat-card" style="margin-bottom:14px; font-size:0.82rem; color:var(--text-secondary); white-space:normal;" id="nbRuleBanner">
          💡 <strong>生词本联动机制</strong>：在生词本中修改单词的中文释义，主词库中的释义会同步更新；若将单词移出生词本，其释义将自动恢复为词典原始释义。
        </div>

        <div id="notebookListContainer" class="word-list-wrap"></div>
      </section>

      <!-- ==================== VIEW 5: OFFLINE DATA, IMPORT/EXPORT, PDF & MIGRATION GUIDE ==================== -->
      <section class="view-section" id="view-data">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:16px; margin-bottom:18px;">
          <!-- Card 1: Custom Lexicon Import -->
          <div class="stat-card" style="padding:18px;">
            <h3 style="font-size:1.08rem; font-weight:800; margin-bottom:6px;">📥 外部自定义词库导入</h3>
            <p style="font-size:0.82rem; color:var(--text-muted); margin-bottom:12px; white-space:normal;">
              软件已默认内置 8 大考试词书（共 38,855 词条，无需手动导入）。如需补充额外专业词汇，支持导入 CSV / TSV / TXT / JSON 文件（自动识别 UTF-8 与 GBK/GB18030 编码）。
            </p>
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
              <label class="btn btn-primary btn-sm" style="cursor:pointer;">
                选择本地词表 (.csv/.txt/.json)
                <input type="file" id="fileImportLexicon" accept=".csv,.tsv,.txt,.json" style="display:none;">
              </label>
              <button class="btn btn-sm" id="btnLoadSampleCustomWords">导入5个示例高阶词</button>
            </div>
            <textarea id="pasteImportTextarea" rows="4" placeholder="格式：单词, 音标, 中文释义, 英文例句, 例句翻译&#10;例如：serendipity, /ˌserənˈdɪpəti/, n. 机缘巧合, Finding it was pure serendipity., 发现它纯属机缘巧合。" style="width:100%; border-radius:10px; border:1px solid var(--border-strong); background:var(--bg-elevated); color:var(--text-primary); padding:10px; font-size:0.82rem; margin-bottom:10px;"></textarea>
            <button class="btn btn-sm" id="btnParsePasteImport">解析并导入粘贴内容</button>
          </div>

          <!-- Card 2: Multi-Page PDF & Printable Sheet Generator -->
          <div class="stat-card" style="padding:18px;">
            <h3 style="font-size:1.08rem; font-weight:800; margin-bottom:6px;">🖨️ 多页 PDF 导出、打印与 HTML 导出</h3>
            <p style="font-size:0.82rem; color:var(--text-muted); margin-bottom:12px; white-space:normal;">
              支持生成多页 A4 排版文档，完整导出全部词条与计划表（自动分页、跨页表头重复、行防截断），支持<strong>直接导出多页 .pdf 文件</strong>、<strong>调用系统打印/另存为 PDF</strong> 以及<strong>下载独立 .html 文件</strong>。
            </p>
            <div style="display:flex; flex-direction:column; gap:8px;">
              <button class="btn" id="btnExportPdfSchedule">📅 导出「自定义艾宾浩斯学习计划表」PDF/打印版</button>
              <button class="btn" id="btnExportPdfListBilingual">📋 导出「当前 List 完整单词表（双语对照版）」</button>
              <button class="btn" id="btnExportPdfListQuiz">✍️ 导出「当前 List 完整默写自测卷（隐中/隐英）」</button>
              <button class="btn" id="btnExportPdfStarred">⭐ 导出「生词本重难词汇总手册」</button>
            </div>
          </div>

          <!-- Card 3: Local Data Backup & Restore -->
          <div class="stat-card" style="padding:18px;">
            <h3 style="font-size:1.08rem; font-weight:800; margin-bottom:6px;">💾 本地数据持久化备份与恢复</h3>
            <p style="font-size:0.82rem; color:var(--text-muted); margin-bottom:12px; white-space:normal;">
              所有学习进度、自定义计划参数、不会程度、生词本、熟词表、在线词典偏好及自定义词库均实时保存在本地双引擎（LocalStorage + IndexedDB）中，完全兼容 v1.0.0 / v1.0.1 / v1.0.2 备份文件。
            </p>
            <div style="background:var(--bg-elevated); border-radius:10px; padding:10px 12px; font-size:0.79rem; margin-bottom:12px; white-space:normal;" id="storageDiagnosticBox">
              存储引擎状态：LocalStorage (正常) · IndexedDB VocaDB_v1 (正常) · Schema v1.0.3
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:8px;">
              <button class="btn btn-primary btn-sm" id="btnExportBackupJson">⬇ 导出完整学习备份 (.json)</button>
              <label class="btn btn-sm" style="cursor:pointer;">
                ⬆ 从备份文件恢复数据
                <input type="file" id="fileRestoreBackupJson" accept=".json" style="display:none;">
              </label>
              <button class="btn btn-sm" id="btnExportLexiconCsv">导出当前词库 CSV</button>
            </div>
          </div>
        </div>

        <!-- Card 4: Comprehensive Data Storage Paths, v1.0.2 -> v1.0.3 Upgrade & Migration Guide -->
        <div class="stat-card" id="dataMigrationGuideCard" style="padding:20px; line-height:1.7;">
          <h3 style="font-size:1.12rem; font-weight:800; margin-bottom:12px;">📂 v1.0.2 → v1.0.3 版本升级、数据存储路径与跨平台迁移说明</h3>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:14px; font-size:0.83rem; color:var(--text-secondary);">
            <div style="background:var(--bg-elevated); padding:14px 16px; border-radius:12px; border:1px solid var(--border-color); white-space:normal;">
              <div style="font-weight:800; color:var(--text-primary); margin-bottom:6px;">1. 用户数据实际存放位置及相对路径</div>
              <p>• <strong>Windows 平台</strong>（参照位置：解压后的 <code>windows/</code> 目录，即 <code>Voca.exe</code> 所在同级文件夹）：<br>
                - 运行时用户学习数据（不会程度、生词本、熟词表、自定义计划、在线词典设置、打卡进度）：存放在相对路径 <code>./data/profile/Default/Local Storage/leveldb/</code> 与 <code>./data/profile/Default/IndexedDB/</code>。<br>
                - 默认内置离线 SQLite 词库文件：存放在相对路径 <code>./data/voca.db</code>。<br>
                - 应用前端与跨平台统一字体包：存放在相对路径 <code>./app/index.html</code> 与 <code>./app/fonts/</code>。</p>
              <p style="margin-top:6px;">• <strong>Android 平台</strong>（参照位置：Android 系统内部存储应用私有沙箱根目录 <code>/data/data/com.voca.app/</code>）：<br>
                - 运行时用户学习数据：存放在相对路径 <code>./app_webview/Default/Local Storage/</code> 与 <code>./app_webview/Default/IndexedDB/</code>。<br>
                - 内置词库与统一字体包：封装于 APK 安装包内部只读资产路径 <code>assets/index.html</code> 与 <code>assets/fonts/</code>。</p>
            </div>

            <div style="background:var(--bg-elevated); padding:14px 16px; border-radius:12px; border:1px solid var(--border-color); white-space:normal;">
              <div style="font-weight:800; color:var(--text-primary); margin-bottom:6px;">2. v1.0.2 升级至 v1.0.3 数据保留与跨平台迁移</div>
              <p>• <strong>升级前准备与数据自动迁移机制</strong>：升级前建议先点击上方「⬇ 导出完整学习备份 (.json)」保存一份备份。v1.0.3 启动时会自动检测 v1.0.2 存档（Schema v3 → v4），自动清理已废弃的「掌握度 (`mastery`)」与「英英模式 (`en_en`)」字段，同时 <strong>100% 无损保留</strong>所有单词的「不会程度 (`unfam`)」、生词本、熟词表、自定义释义、笔记、艾宾浩斯计划表参数与打卡记录。</p>
              <p style="margin-top:6px;">• <strong>已支持的迁移方式</strong>：<br>
                1) <strong>通用 JSON 备份迁移（推荐，支持 Windows ⇄ Android 互传）</strong>：在旧版或原设备导出 <code>.json</code> 备份，在新版或新设备点击「⬆ 从备份文件恢复数据」即可一键迁移并验证。<br>
                2) <strong>Windows 同平台升级/迁移</strong>：将旧版 <code>windows/data/profile/</code> 文件夹复制到 v1.0.3 的 <code>windows/data/profile/</code> 下即可直接继承全部数据。</p>
              <p style="margin-top:6px; color:var(--amber-mark);">• <strong>明确的实际限制（不支持项）</strong>：不支持云端账号自动同步；且因操作系统权限与底层 LevelDB 格式差异，<strong>不支持</strong>将 Windows 的 <code>./data/profile/</code> 目录直接拷贝至 Android 手机恢复。</p>
            </div>

            <div style="background:var(--bg-elevated); padding:14px 16px; border-radius:12px; border:1px solid var(--border-color); white-space:normal;">
              <div style="font-weight:800; color:var(--text-primary); margin-bottom:6px;">3. 覆盖安装、重新安装与卸载对本地数据的影响</div>
              <p>• <strong>Windows</strong>：保留 <code>./data/profile/</code> 并替换 <code>Voca.exe</code> 与 <code>./app/</code> 属于覆盖升级，数据完整保留；若删除整个 <code>windows/</code> 文件夹（卸载），则 <code>./data/profile/</code> 中的本地数据会一并被删除。</p>
              <p style="margin-top:6px;">• <strong>Android</strong>：使用同签名 APK 直接覆盖安装时系统自动保留数据；若因签名变更需先卸载再重装，或执行「卸载应用 / 清除数据」，Android 系统会彻底清空 <code>/data/data/com.voca.app/</code>，<strong>因此卸载前请务必先导出 .json 备份文件</strong>。</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== VIEW 6: SETTINGS & HELP ==================== -->
      <section class="view-section" id="view-settings">
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(300px, 1fr)); gap:18px;">
          <!-- Preferences -->
          <div class="stat-card" style="padding:20px; display:flex; flex-direction:column; gap:14px;">
            <h3 style="font-size:1.1rem; font-weight:800;">⚙️ 学习与词典偏好设置</h3>

            <!-- Requirement 4: Persistent Online Dictionary Selection Setting -->
            <label style="font-size:0.86rem; font-weight:700; color:var(--brand-primary);">📖 在线词典查询来源选择（用于「查看词典详细与编辑」弹窗，重启后持久生效）
              <select id="settingOnlineDict" class="ctrl-select" style="width:100%; margin-top:6px;">
                <option value="eudic" selected>欧路词典 (https://dict.eudic.net/dicts/en/@word@)</option>
                <option value="wordreference">WordReference 英汉词典 (https://www.wordreference.com/enzh/@word@)</option>
              </select>
            </label>

            <!-- Requirement 2: Row Click Behavior based on Unfamiliarity (不会程度) -->
            <label style="font-size:0.86rem; font-weight:600;">单词行鼠标/触控点击行为设置（管理「不会程度」）
              <select id="settingRowClickMode" class="ctrl-select" style="width:100%; margin-top:6px;">
                <option value="unfam_lr" selected>1. 不会程度模式：左键/轻触加深不会程度(+1)并发音 · 右键降低不会程度(-1)</option>
                <option value="left_sound_right_unfam">2. 分区模式 A：点击左半部仅发音，右半部加深不会程度(+1) · 右键降低(-1)</option>
                <option value="right_sound_left_unfam">3. 分区模式 B：点击右半部仅发音，左半部加深不会程度(+1) · 右键降低(-1)</option>
                <option value="sound_only">4. 纯发音模式：点击仅朗读发音（不改变不会程度）</option>
              </select>
            </label>

            <label style="font-size:0.86rem; font-weight:600;">英语发音口音偏好
              <select id="settingAccentMode" class="ctrl-select" style="width:100%; margin-top:6px;">
                <option value="en-US">美式发音 (American English)</option>
                <option value="en-GB">英式发音 (British English)</option>
                <option value="en-AU">澳式发音 (Australian English)</option>
              </select>
            </label>

            <label style="font-size:0.86rem; font-weight:600;">音标显示设置
              <select id="settingPhoneticDisplay" class="ctrl-select" style="width:100%; margin-top:6px;">
                <option value="both">显示完整音标</option>
                <option value="us">优先美式音标 (US)</option>
                <option value="uk">优先英式音标 (UK)</option>
                <option value="hide">隐藏音标</option>
              </select>
            </label>

            <label style="font-size:0.86rem; font-weight:600;">显示外观主题 (三套精选护眼主题)
              <select id="settingThemeSelect" class="ctrl-select" style="width:100%; margin-top:6px;">
                <option value="daylight">晨曦白 (Daylight Clean)</option>
                <option value="oled">纯黑OLED (Pure Black OLED)</option>
                <option value="paper">羊皮纸 (Warm Paper)</option>
              </select>
            </label>

            <label style="font-size:0.86rem; font-weight:600;">全局文字大小
              <select id="settingFontScale" class="ctrl-select" style="width:100%; margin-top:6px;">
                <option value="small">紧凑小号 (90%)</option>
                <option value="standard" selected>标准适中 (100%)</option>
                <option value="large">舒适大字 (112%)</option>
                <option value="xlarge">超大护眼 (125%)</option>
              </select>
            </label>

            <label style="font-size:0.86rem; font-weight:600; display:flex; align-items:center; gap:8px; cursor:pointer;">
              <input type="checkbox" id="settingSoundFxToggle" checked> 开启多邻国风格微交互合成音效 (Web Audio)
            </label>
          </div>

          <!-- Shortcuts & Architecture Info -->
          <div class="stat-card" style="padding:20px; display:flex; flex-direction:column; gap:12px; white-space:normal;">
            <h3 style="font-size:1.1rem; font-weight:800;">⌨️ 操作指南、在线词典与开源授权 (v1.0.3)</h3>
            <div style="font-size:0.83rem; color:var(--text-secondary); line-height:1.7;">
              <div>• <strong>左键/点击单词行</strong>：加深该词不会程度 (+1，上限 5/5) 并朗读发音</div>
              <div>• <strong>右键点击单词行</strong>：降低该词不会程度 (-1，下限 0/5)</div>
              <div>• <strong>点击 📖 按钮</strong>：打开「查看词典详细与编辑」弹窗，自动调用所选在线词典（欧路词典 / WordReference）查询当前单词</div>
              <div>• <strong>Space (空格键)</strong>：朗读当前卡片单词发音</div>
              <div>• <strong>J / ← 与 K / →</strong>：沉浸卡片模式下切换上一词 / 下一词</div>
              <div>• <strong>1 / 2 / 3 键</strong>：快速切换 双语 / 只看英文 / 只看中文 模式</div>
            </div>
            <div style="border-top:1px solid var(--border-color); padding-top:12px; font-size:0.82rem; color:var(--text-muted);">
              <strong>字体、词库与在线词典声明 (v1.0.3)</strong>：<br>
              1) <strong>跨平台内嵌字体</strong>：内置 <strong>Inter</strong> 与 <strong>Noto Sans CJK SC</strong> (SIL Open Font License 1.1) WOFF2 字体包。<br>
              2) <strong>内置词库授权</strong>：内置「Voca-词库数据包」共 <strong>38,855</strong> 条词条，源自开源词典 <strong>ECDICT</strong>（MIT License）。<br>
              3) <strong>在线词典集成</strong>：支持按需实时查询 <strong>欧路词典 (dict.eudic.net)</strong> 与 <strong>WordReference 英汉词典 (wordreference.com)</strong>，在线词典网页内容版权归各词典平台所有。
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</div>

<!-- Mobile Bottom Navigation -->
<nav class="mobile-bottom-nav" id="mobileNav">
  <button class="mob-nav-btn active" data-tab="learn"><span>📚</span><span>背单词</span></button>
  <button class="mob-nav-btn" data-tab="plan"><span>📅</span><span>计划表</span></button>
  <button class="mob-nav-btn" data-tab="train"><span>⚡</span><span>训练</span></button>
  <button class="mob-nav-btn" data-tab="notebook"><span>⭐</span><span>生词本</span></button>
  <button class="mob-nav-btn" data-tab="data"><span>📥</span><span>导词/PDF</span></button>
  <button class="mob-nav-btn" data-tab="settings"><span>⚙️</span><span>设置</span></button>
</nav>

<!-- ==================== REQUIREMENT 3 & 4: REDESIGNED DICTIONARY & EDIT MODAL ==================== -->
<div class="modal-backdrop" id="dictModal">
  <div class="modal-panel">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
      <div>
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <h3 style="font-size:1.45rem; font-weight:800;" id="modalDictWord">abandon</h3>
          <span class="brand-badge" id="modalActiveDictBadge">欧路词典</span>
        </div>
        <div style="font-size:0.86rem; color:var(--text-muted);" id="modalDictIpa">/əˈbændən/</div>
      </div>
      <div style="display:flex; gap:6px; flex-wrap:wrap;">
        <button class="btn btn-sm" id="modalBtnSpeakWord">🔊 发音</button>
        <button class="btn btn-sm" id="modalBtnCopyWord">📋 复制</button>
        <button class="btn btn-sm" id="modalBtnCloseDict">✕ 关闭</button>
      </div>
    </div>

    <div style="display:flex; flex-direction:column; gap:12px;">
      <!-- Online Dictionary Content Block (Replaces the 2 deleted blocks: '英英释义与同义词拓展' and '双语语境例句与助记') -->
      <div class="dict-online-box" id="modalOnlineDictSection">
        <div class="dict-online-header">
          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span style="font-size:0.80rem; font-weight:800; color:var(--text-primary);">🌐 在线词典查询来源：</span>
            <div class="seg-group" id="modalDictSourceGroup">
              <button type="button" class="seg-btn active" data-dict="eudic" id="modalBtnSourceEudic">欧路词典</button>
              <button type="button" class="seg-btn" data-dict="wordreference" id="modalBtnSourceWR">WordReference 英汉</button>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
            <button type="button" class="btn btn-sm" id="modalBtnReloadDict">🔄 重新查询</button>
            <a class="btn btn-sm" id="modalDictExternalLink" href="https://dict.eudic.net/dicts/en/abandon" target="_blank" rel="noopener noreferrer">↗ 浏览器打开源页面</a>
          </div>
        </div>

        <div style="font-size:0.75rem; color:var(--text-muted); word-break:break-all;">
          查询地址：<code id="modalDictUrlCode">https://dict.eudic.net/dicts/en/abandon</code>
        </div>

        <!-- Honest Real-Time Status Banner (Loading / Success / Word Not Found / Offline / Network Error) -->
        <div class="dict-status-banner dict-status-loading" id="modalDictStatusBanner">
          ⏳ 正在查询在线词典...
        </div>

        <!-- Parsed Online Dictionary Content Box (Shown when HTML/API response is parsed or when displaying honest fallback diagnostics) -->
        <div class="dict-parsed-entries" id="modalDictParsedContent"></div>

        <!-- Live Online Dictionary Embedded View (Automatically hidden when offline or unreachable so blank/failed pages are never disguised as normal results) -->
        <div class="dict-iframe-wrap" id="modalDictIframeWrap" style="display:none;">
          <iframe id="modalOnlineDictIframe" title="在线词典详情视图" referrerpolicy="no-referrer"></iframe>
        </div>
      </div>

      <!-- Editable Chinese Definition (Linked with Notebook) -->
      <div class="card-section-box">
        <div style="font-size:0.76rem; font-weight:700; color:var(--text-muted); margin-bottom:4px;">中文释义（支持自定义修改，生词本联动）</div>
        <input type="text" id="modalEditCnInput" style="width:100%; padding:8px 10px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-surface); color:var(--text-primary); font-size:0.95rem; font-weight:600;">
      </div>

      <!-- Personal Learning Note -->
      <div class="card-section-box">
        <div style="font-size:0.76rem; font-weight:700; color:var(--text-muted); margin-bottom:6px;">个人学习笔记</div>
        <input type="text" id="modalEditNoteInput" placeholder="添加个人助记、真题搭配或易混辨析..." style="width:100%; padding:8px 10px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-surface); color:var(--text-primary); font-size:0.86rem;">
      </div>

      <!-- Unfamiliarity Controls & Save (Mastery removed per Requirement 2) -->
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; padding-top:4px;">
        <div style="font-size:0.80rem; color:var(--text-muted); display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
          <span>不会程度：<strong id="modalUnfamVal">0</strong>/5</span>
          <button class="btn btn-sm" id="modalBtnUnfamDown" title="降低不会程度 (-1)">-1</button>
          <button class="btn btn-sm" id="modalBtnUnfamUp" title="加深不会程度 (+1)">+1</button>
          <button class="btn btn-sm" id="modalBtnResetUnfam">重置不会度</button>
        </div>
        <button class="btn btn-primary btn-sm" id="modalBtnSaveEdit">💾 保存修改并加入生词本</button>
      </div>
    </div>
  </div>
</div>

<!-- Modal: Add Custom Word -->
<div class="modal-backdrop" id="addWordModal">
  <div class="modal-panel">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <h3 style="font-size:1.25rem; font-weight:800;">+ 手动添加新单词</h3>
      <button class="btn btn-sm" id="btnCloseAddWordModal">✕ 关闭</button>
    </div>
    <div style="display:flex; flex-direction:column; gap:10px;">
      <input type="text" id="newWordSpell" placeholder="英文单词 (必填，如 resilience)" style="padding:9px 12px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-elevated); color:var(--text-primary);">
      <input type="text" id="newWordIpa" placeholder="音标 (选填，如 /rɪˈzɪliəns/)" style="padding:9px 12px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-elevated); color:var(--text-primary);">
      <input type="text" id="newWordCn" placeholder="中文释义 (必填，如 n. 韧性，恢复力)" style="padding:9px 12px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-elevated); color:var(--text-primary);">
      <input type="text" id="newWordExEn" placeholder="英文例句 (选填)" style="padding:9px 12px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-elevated); color:var(--text-primary);">
      <input type="text" id="newWordExCn" placeholder="例句中文翻译 (选填)" style="padding:9px 12px; border-radius:8px; border:1px solid var(--border-strong); background:var(--bg-elevated); color:var(--text-primary);">
      <button class="btn btn-primary" id="btnConfirmAddWord">确认添加到词库与生词本</button>
    </div>
  </div>
</div>

<!-- Modal: Multi-Page PDF / Print / HTML Preview Sheet -->
<div class="modal-backdrop" id="printModal">
  <div class="modal-panel" style="max-width:900px;">
    <div class="no-print" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px; border-bottom:1px solid var(--border-color); padding-bottom:10px;">
      <div>
        <h3 style="font-size:1.12rem; font-weight:800;" id="printModalTitle">多页 PDF / 打印版预览</h3>
        <div style="font-size:0.76rem; color:var(--text-muted);" id="printModalMeta">支持完整多页导出、跨页表头重复与行防截断</div>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:8px;">
        <button class="btn btn-primary btn-sm" id="btnDownloadDirectPdf">⬇ 直接导出多页 PDF (.pdf)</button>
        <button class="btn btn-sm" id="btnTriggerBrowserPrint">🖨️ 调用系统打印 / 另存为 PDF</button>
        <button class="btn btn-sm" id="btnDownloadPrintHtml">⬇ 下载独立 HTML (.html)</button>
        <button class="btn btn-sm" id="btnClosePrintModal">✕ 关闭</button>
      </div>
    </div>
    <div id="printSheetBody" style="font-size:0.85rem; line-height:1.6;"></div>
  </div>
</div>

<div id="dedicatedPrintRoot"></div>
<div class="toast-container" id="toastContainer"></div>
"""

HTML_PART2 = HTML_PART2_TEMPLATE.replace("__ICON_256_B64__", ASSETS["icon_256_b64"])

if __name__ == "__main__":
    print("make_html_v103_part2 ready, length:", len(HTML_PART2))
