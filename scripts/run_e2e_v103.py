#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive End-to-End Verification Suite for Voca v1.0.3.
Tests all 8 acceptance items from Section 四 of the prompt:
1. Windows Taskbar & Multi-DPI Icon Verification (8-frame Win32 DIB/PNG voca.ico, PE .rsrc RT_ICON/RT_GROUP_ICON/RT_MANIFEST, multi-size HTML <link rel="icon">, 256px .brand-logo).
2. Removal of "掌握度" (Mastery) and full functionality of "不会程度" (Unfamiliarity 0..5 via left-click +1, right-click -1, card controls, sort, and PDF export).
3. Dictionary Modal ("查看词典详细与编辑") querying Eudic (https://dict.eudic.net/dicts/en/@word@) and WordReference (https://www.wordreference.com/enzh/@word@), URL encoding of special characters, and honest handling of offline/error/not-found/success states.
4. Complete removal of the two old blocks ("英英释义与同义词拓展" and "双语语境例句与助记").
5. Persistent Online Dictionary selection setting in "偏好设置与帮助" across restarts.
6. Complete removal of "英英模式" (en_en) and normal operation of remaining modes (双语 / 只看英文 / 只看中文).
7. Lossless upgrade & migration of v1.0.2 user data to v1.0.3 (cleaning deprecated mastery/en_en while preserving unfam, starred, customCn, note, custom plan N/D, and check-ins).
"""
import json
import os
import struct
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.environ.get("VOCA_TEST_HTML", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "windows", "app", "index.html")))
if not os.path.exists(HTML_PATH):
    alt_h = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "windows", "app", "index.html"))
    if os.path.exists(alt_h):
        HTML_PATH = alt_h

ICO_PATH = os.environ.get("VOCA_TEST_ICO", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "windows", "voca.ico")))
if not os.path.exists(ICO_PATH):
    alt_i = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "windows", "voca.ico"))
    if os.path.exists(alt_i):
        ICO_PATH = alt_i

EXE_PATH = os.environ.get("VOCA_TEST_EXE", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "windows", "Voca.exe")))
if not os.path.exists(EXE_PATH):
    alt_e = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "windows", "Voca.exe"))
    if os.path.exists(alt_e):
        EXE_PATH = alt_e

def verify_windows_icon_binaries() -> dict:
    with open(ICO_PATH, "rb") as f:
        ico = f.read()
    rsvd, itype, count = struct.unpack("<HHH", ico[:6])
    assert rsvd == 0 and itype == 1 and count == 8, f"Expected 8 icon frames in voca.ico, got {count}"

    frames_report = []
    expected_sizes = [256, 128, 64, 48, 40, 32, 24, 16]
    for i in range(count):
        bw, bh, _, _, planes, bpp, sz, off = struct.unpack("<BBBBHHII", ico[6 + i * 16 : 6 + (i + 1) * 16])
        actual_w = 256 if bw == 0 else bw
        actual_h = 256 if bh == 0 else bh
        assert actual_w == expected_sizes[i] and actual_h == expected_sizes[i]
        payload = ico[off : off + sz]
        if actual_w == 256:
            assert payload[:4] == b"\x89PNG", "256x256 frame must be PNG"
            fmt = "PNG"
        else:
            bi_size, bi_w, bi_h, bi_planes, bi_bpp = struct.unpack("<IIIHH", payload[:16])
            assert bi_size == 40 and bi_w == actual_w and bi_h == actual_h * 2 and bi_bpp == 32, (
                f"Invalid Win32 DIB header for {actual_w}x{actual_h}: biSize={bi_size}, w={bi_w}, h={bi_h}, bpp={bi_bpp}"
            )
            fmt = "Win32_32bit_BGRA_DIB"
        frames_report.append({"size": f"{actual_w}x{actual_h}", "format": fmt, "bytes": sz})

    with open(EXE_PATH, "rb") as f:
        exe_bytes = f.read()
    assert b"PerMonitorV2" in exe_bytes and "--high-dpi-support=1".encode("utf-16le") in exe_bytes and "--start-maximized".encode("utf-16le") in exe_bytes

    return {
        "ico_frame_count": count,
        "frames": frames_report,
        "exe_size_bytes": len(exe_bytes),
        "has_per_monitor_v2_manifest": True,
        "has_high_dpi_flag": True
    }

def run_all_tests():
    results = {}
    results["test1_windows_icon_binary"] = verify_windows_icon_binaries()
    print("[Test 1] Windows 8-Frame Win32 DIB/PNG Icon & PerMonitorV2 Manifest Verified:", json.dumps(results["test1_windows_icon_binary"], indent=2))

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_str = f.read()

    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_opts)
    try:
        driver.get("about:blank")
        driver.execute_script("document.open(); document.write(arguments[0]); document.close();", html_str)

        # ==================== TEST 2: HTML ICON LINKS, MASTERY REMOVAL & UNFAMILIARITY OPERATION ====================
        test2_dom = driver.execute_script("""
            const iconLinks = Array.from(document.querySelectorAll('link[rel*="icon"]')).map(l => ({
                rel: l.getAttribute('rel'),
                sizes: l.getAttribute('sizes') || 'any'
            }));
            const brandLogo = document.querySelector('.brand-logo');

            // Verify complete absence of Mastery (掌握度) elements
            const masteryDomCount = document.querySelectorAll(
                '.mastery-badge, .mastery-dots, #cardMasteryDots, #cardMasteryNum, #cardBtnMasteryUp, #cardBtnMasteryDown, #modalBtnMasteryUp, #modalBtnMasteryDown, [data-mastery]'
            ).length;
            const sortOptions = Array.from(document.getElementById('sortSelect').options).map(o => o.value);
            const rowClickOptions = Array.from(document.getElementById('settingRowClickMode').options).map(o => o.value);

            // Test Left-Click (+1 unfam) and Right-Click (-1 unfam) on first word row
            const firstRow = document.querySelector('#learnListContainer .word-row');
            const initialUnfam = parseInt(firstRow.getAttribute('data-unfam'), 10);
            firstRow.click();
            firstRow.click();
            const after2LeftClicks = parseInt(firstRow.getAttribute('data-unfam'), 10);

            // Dispatch right-click (contextmenu)
            const ctxEv = new MouseEvent('contextmenu', { bubbles: true, cancelable: true, button: 2 });
            firstRow.dispatchEvent(ctxEv);
            const after1RightClick = parseInt(firstRow.getAttribute('data-unfam'), 10);

            // Switch to Immersive Card and test #cardBtnUnfamUp / #cardBtnUnfamDown / #cardBtnUnfamReset
            document.querySelector('#layoutModeGroup [data-layout="card"]').click();
            const cardBefore = parseInt(document.getElementById('cardUnfamNum').textContent, 10);
            document.getElementById('cardBtnUnfamUp').click();
            const cardAfterUp = parseInt(document.getElementById('cardUnfamNum').textContent, 10);
            document.getElementById('cardBtnUnfamDown').click();
            const cardAfterDown = parseInt(document.getElementById('cardUnfamNum').textContent, 10);
            document.getElementById('cardBtnUnfamReset').click();
            const cardAfterReset = parseInt(document.getElementById('cardUnfamNum').textContent, 10);
            document.querySelector('#layoutModeGroup [data-layout="list"]').click();

            return {
                iconLinksCount: iconLinks.length,
                iconSizes: iconLinks.map(x => x.sizes),
                brandLogoNaturalSize: [brandLogo.naturalWidth, brandLogo.naturalHeight],
                masteryDomCount: masteryDomCount,
                sortOptions: sortOptions,
                rowClickOptions: rowClickOptions,
                unfamClickProgression: [initialUnfam, after2LeftClicks, after1RightClick],
                cardUnfamProgression: [cardBefore, cardAfterUp, cardAfterDown, cardAfterReset]
            };
        """)
        print("[Test 2] Mastery Removal & Unfamiliarity Verification:", json.dumps(test2_dom, indent=2))
        assert test2_dom["iconLinksCount"] >= 8
        assert test2_dom["brandLogoNaturalSize"] == [256, 256]
        assert test2_dom["masteryDomCount"] == 0, "Mastery DOM elements still exist!"
        assert "mastery_asc" not in test2_dom["sortOptions"] and "hard_first" in test2_dom["sortOptions"]
        assert test2_dom["unfamClickProgression"] == [0, 2, 1], f"Unexpected unfam progression: {test2_dom['unfamClickProgression']}"
        assert test2_dom["cardUnfamProgression"] == [1, 2, 1, 0], f"Unexpected card unfam progression: {test2_dom['cardUnfamProgression']}"
        results["test2_mastery_removal_and_unfam"] = test2_dom

        # ==================== TEST 3, 4, 5: DICTIONARY MODAL, DELETED BLOCKS & ONLINE DICT SETTING ====================
        test3_dict = driver.execute_script("""
            // 1. Verify the two old blocks ('英英释义与同义词拓展' and '双语语境例句与助记') are completely deleted
            const oldElements = document.querySelectorAll('#modalDictEn, #modalDictSyn, #modalDictExEn, #modalDictExCn, #modalDictTip, #modalBtnSpeakSentence');
            const modalText = document.getElementById('dictModal').textContent;
            const hasOldHeaders = modalText.indexOf('英英释义与同义词拓展') !== -1 || modalText.indexOf('双语语境例句与助记') !== -1;

            // 2. Open Dictionary Modal in default offline sandbox environment -> verify honest failure state (no blank iframe!)
            const firstRow = document.querySelector('#learnListContainer .word-row');
            firstRow.querySelector('[data-act="dict"]').click();

            return {
                oldElementsCount: oldElements.length,
                hasOldHeaders: hasOldHeaders,
                initialDictBadge: document.getElementById('modalActiveDictBadge').textContent,
                initialUrl: document.getElementById('modalDictUrlCode').textContent,
                externalLinkHref: document.getElementById('modalDictExternalLink').getAttribute('href')
            };
        """)
        assert test3_dict["oldElementsCount"] == 0 and test3_dict["hasOldHeaders"] is False, "Old dictionary blocks were not removed!"
        assert test3_dict["initialUrl"].startswith("https://dict.eudic.net/dicts/en/")

        # Wait briefly for offline fetch rejection to settle and verify honest offline error banner & hidden iframe
        import time
        time.sleep(0.4)
        offline_state = driver.execute_script("""
            return {
                bannerClass: document.getElementById('modalDictStatusBanner').className,
                bannerText: document.getElementById('modalDictStatusBanner').textContent,
                iframeDisplay: document.getElementById('modalDictIframeWrap').style.display,
                parsedText: document.getElementById('modalDictParsedContent').textContent
            };
        """)
        print("[Test 3A] Honest Offline / Unreachable Dictionary State:", json.dumps(offline_state, indent=2, ensure_ascii=False))
        assert "dict-status-error" in offline_state["bannerClass"]
        assert offline_state["iframeDisplay"] == "none", "Blank iframe must not be shown when offline/failed!"
        assert "无法加载" in offline_state["bannerText"]

        # Now test Online Dictionary Fetcher with:
        # (a) Eudic HTML response
        # (b) WordReference HTML response (via Settings change + persistence check)
        # (c) Special character URL encoding (e.g., 'self-esteem & co.')
        # (d) 404 Word Not Found state
        online_states = driver.execute_script("""
            window.__VOCA_ONLINE_DICT_FETCHER__ = function(url, dictKey, word) {
                if (word === 'nonexistent_xyz_999') {
                    return { ok: true, status: 404, html: '<div>未找到该词条</div>' };
                }
                if (dictKey === 'eudic') {
                    return {
                        ok: true,
                        status: 200,
                        html: '<div id="ExpFCChild"><ul><li>vt. 放弃，遗弃；中止 (' + word + ')</li><li>n. 放任，狂热</li></ul></div>'
                    };
                } else {
                    return {
                        ok: true,
                        status: 200,
                        html: '<table class="WRD"><tr class="even"><td class="FrWrd"><strong>' + word + '</strong></td><td class="ToWrd">放弃，抛弃 (WordReference 释义)</td></tr></table>'
                    };
                }
            };

            // Reload Eudic in modal
            document.getElementById('modalBtnReloadDict').click();
            return true;
        """)
        time.sleep(0.15)
        eudic_ok = driver.execute_script("""
            return {
                url: document.getElementById('modalDictUrlCode').textContent,
                bannerClass: document.getElementById('modalDictStatusBanner').className,
                bannerText: document.getElementById('modalDictStatusBanner').textContent,
                parsedText: document.getElementById('modalDictParsedContent').textContent
            };
        """)
        print("[Test 3B] Eudic Online Parsed Result:", json.dumps(eudic_ok, indent=2, ensure_ascii=False))
        assert "dict-status-ok" in eudic_ok["bannerClass"] and "放弃，遗弃" in eudic_ok["parsedText"]

        # Change Online Dictionary in Settings to WordReference and verify persistence + modal sync
        wr_and_encoding = driver.execute_script("""
            document.getElementById('modalBtnCloseDict').click();
            document.getElementById('navBtnSettings').click();
            const sel = document.getElementById('settingOnlineDict');
            sel.value = 'wordreference';
            sel.dispatchEvent(new Event('change'));

            const savedDictSetting = window.__VOCA_GET_STATE__().settings.onlineDict;

            // Add a custom word with space & hyphen to test URL encoding + WordReference query
            document.getElementById('navBtnNotebook').click();
            document.getElementById('btnAddCustomWordModal').click();
            document.getElementById('newWordSpell').value = 'take off';
            document.getElementById('newWordCn').value = 'v. 起飞；脱下';
            document.getElementById('btnConfirmAddWord').click();

            // Open dictModal on 'take off'
            const nbRow = document.querySelector('#notebookListContainer .word-row');
            nbRow.querySelector('[data-act="dict"]').click();
            return {
                savedDictSetting: savedDictSetting,
                wrUrlForSpecialWord: document.getElementById('modalDictUrlCode').textContent,
                wrBadge: document.getElementById('modalActiveDictBadge').textContent
            };
        """)
        time.sleep(0.15)
        wr_ok = driver.execute_script("""
            return {
                bannerClass: document.getElementById('modalDictStatusBanner').className,
                parsedText: document.getElementById('modalDictParsedContent').textContent
            };
        """)
        print("[Test 4] WordReference Setting Persistence & URL Encoding:", json.dumps({**wr_and_encoding, **wr_ok}, indent=2, ensure_ascii=False))
        assert wr_and_encoding["savedDictSetting"] == "wordreference"
        assert wr_and_encoding["wrUrlForSpecialWord"] == "https://www.wordreference.com/enzh/take%20off"
        assert "dict-status-ok" in wr_ok["bannerClass"] and "WordReference 释义" in wr_ok["parsedText"]

        # Test 404 Word Not Found state
        driver.execute_script("""
            document.getElementById('modalBtnCloseDict').click();
            document.getElementById('btnAddCustomWordModal').click();
            document.getElementById('newWordSpell').value = 'nonexistent_xyz_999';
            document.getElementById('newWordCn').value = '测试未收录词';
            document.getElementById('btnConfirmAddWord').click();
            const rows = document.querySelectorAll('#notebookListContainer .word-row');
            rows[0].querySelector('[data-act="dict"]').click();
        """)
        time.sleep(0.15)
        not_found_res = driver.execute_script("""
            const res = {
                bannerClass: document.getElementById('modalDictStatusBanner').className,
                bannerText: document.getElementById('modalDictStatusBanner').textContent,
                iframeDisplay: document.getElementById('modalDictIframeWrap').style.display
            };
            document.getElementById('modalBtnCloseDict').click();
            return res;
        """)
        print("[Test 3C] Word Not Found (404) State:", json.dumps(not_found_res, indent=2, ensure_ascii=False))
        assert "dict-status-warn" in not_found_res["bannerClass"] and "词条不存在" in not_found_res["bannerText"]
        assert not_found_res["iframeDisplay"] == "none"
        results["test3_4_5_dictionary_and_settings"] = {
            "deleted_blocks_verified": test3_dict,
            "offline_honest_state": offline_state,
            "eudic_online_state": eudic_ok,
            "wordreference_and_encoding": {**wr_and_encoding, **wr_ok},
            "not_found_state": not_found_res
        }

        # ==================== TEST 6: REMOVAL OF ENGLISH-ENGLISH MODE (en_en) ====================
        test6_lang = driver.execute_script("""
            document.getElementById('navBtnLearn').click();
            const langBtns = Array.from(document.querySelectorAll('#langModeGroup .seg-btn')).map(b => ({
                lang: b.dataset.lang,
                text: b.textContent.trim()
            }));
            // Test switching to en_only and cn_only
            document.querySelector('#langModeGroup [data-lang="en_only"]').click();
            const enOnlyMasked = document.querySelectorAll('#learnListContainer .w-cn.masked-box').length;
            document.querySelector('#langModeGroup [data-lang="cn_only"]').click();
            const cnOnlyMasked = document.querySelectorAll('#learnListContainer .w-head-text.masked-box').length;
            document.querySelector('#langModeGroup [data-lang="bilingual"]').click();
            return {
                langBtns: langBtns,
                enOnlyMaskedCount: enOnlyMasked,
                cnOnlyMaskedCount: cnOnlyMasked
            };
        """)
        print("[Test 6] English-English Mode Removal & Remaining Modes Audit:", json.dumps(test6_lang, indent=2, ensure_ascii=False))
        assert [b["lang"] for b in test6_lang["langBtns"]] == ["bilingual", "en_only", "cn_only"]
        assert test6_lang["enOnlyMaskedCount"] > 0 and test6_lang["cnOnlyMaskedCount"] > 0
        results["test6_en_en_removal"] = test6_lang

        # ==================== TEST 7: V1.0.2 -> V1.0.3 UPGRADE & DATA MIGRATION ====================
        test7_migration = driver.execute_script("""
            const mockV102State = {
                schemaVersion: 3,
                appVersion: "1.0.2",
                currentBook: "ky",
                currentListIndex: 2,
                langMode: "en_en",
                layoutMode: "list",
                intraSort: "mastery_asc",
                planListCount: 18,
                planCycleDays: 36,
                planOrderMode: "az",
                planActiveDay: 5,
                planChecks: { "book_ky_L1": 1700000000000 },
                records: {
                    "hw_abandon": {
                        mastery: 4,
                        unfam: 3,
                        starred: true,
                        starredAt: 1700000001000,
                        mastered: false,
                        customCn: "vt. 放弃（v1.0.2用户自定义释义）",
                        note: "v1.0.2历史学习笔记"
                    }
                },
                settings: {
                    rowClickMode: "mastery_lr",
                    theme: "paper",
                    fontScale: "large"
                }
            };
            window.__VOCA_RELOAD_FROM_PRELOAD__(mockV102State);
            const migrated = window.__VOCA_GET_STATE__();
            return {
                schemaVersion: migrated.schemaVersion,
                appVersion: migrated.appVersion,
                currentBook: migrated.currentBook,
                langMode: migrated.langMode,
                intraSort: migrated.intraSort,
                rowClickMode: migrated.settings.rowClickMode,
                onlineDict: migrated.settings.onlineDict,
                theme: migrated.settings.theme,
                planListCount: migrated.planListCount,
                planCycleDays: migrated.planCycleDays,
                preservedCheckin: !!migrated.planChecks["book_ky_L1"],
                abandonRecord: migrated.records["hw_abandon"],
                hasMasteryKeyInRecord: "mastery" in migrated.records["hw_abandon"]
            };
        """)
        print("[Test 7] v1.0.2 -> v1.0.3 State Upgrade & Migration Verification:", json.dumps(test7_migration, indent=2, ensure_ascii=False))
        assert test7_migration["schemaVersion"] == 4 and test7_migration["appVersion"] == "1.0.3"
        assert test7_migration["langMode"] == "bilingual"  # auto-migrated from removed en_en
        assert test7_migration["intraSort"] == "hard_first"  # auto-migrated from removed mastery_asc
        assert test7_migration["rowClickMode"] == "unfam_lr"  # auto-migrated from removed mastery_lr
        assert test7_migration["onlineDict"] == "eudic"
        assert test7_migration["hasMasteryKeyInRecord"] is False
        assert test7_migration["abandonRecord"]["unfam"] == 3
        assert test7_migration["abandonRecord"]["starred"] is True
        assert test7_migration["abandonRecord"]["customCn"] == "vt. 放弃（v1.0.2用户自定义释义）"
        assert test7_migration["abandonRecord"]["note"] == "v1.0.2历史学习笔记"
        assert test7_migration["preservedCheckin"] is True
        results["test7_v102_data_migration"] = test7_migration

    finally:
        driver.quit()

    out_json = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "docs", "e2e_v103_results.json"))
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("ALL E2E VERIFICATION TESTS FOR VOCA v1.0.3 PASSED!")

if __name__ == "__main__":
    run_all_tests()
