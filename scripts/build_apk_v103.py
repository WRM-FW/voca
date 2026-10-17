#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voca v1.0.4 Android APK Builder (Pure Python AXML + ARSC + Dalvik DEX + APK v1/v2 Signer).
Version constants for the current release:
1. AndroidManifest.xml versionCode=5, versionName="1.0.4".
2. Adds `<uses-permission android:name="android.permission.INTERNET" />` so Android WebView can query online dictionaries (Eudic & WordReference) when online, while core vocabulary features remain 100% offline.
3. Embeds crisp centered 192x192 rounded-rectangle V+Book icon (`res/drawable/ic_launcher.png`).
4. Signs with both JAR v1 and APK Signature Scheme v2 (`0x7109871a`).
"""
import os
import base64
import struct
import zlib
import hashlib
import subprocess
import tempfile

from build_exe_v103 import get_voca_v103_icon_png, ASSETS_DIR
def uleb128(val: int) -> bytes:
    out = bytearray()
    while True:
        b = val & 0x7F
        val >>= 7
        if val != 0:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)

def align4(data: bytes) -> bytes:
    rem = len(data) % 4
    return data if rem == 0 else data + b"\x00" * (4 - rem)

def build_classes_dex() -> bytes:
    strings = sorted(set([
        "<init>", "I", "L",
        "Landroid/app/Activity;", "Landroid/content/Context;", "Landroid/os/Bundle;",
        "Landroid/view/View;", "Landroid/webkit/WebChromeClient;", "Landroid/webkit/WebSettings;",
        "Landroid/webkit/WebView;", "Landroid/webkit/WebViewClient;",
        "Lcom/voca/app/MainActivity;", "Ljava/lang/String;",
        "MainActivity.java", "V", "VL", "VZ", "Z", "ZI",
        "canGoBack", "file:///android_asset/index.html", "getSettings", "goBack",
        "loadUrl", "onBackPressed", "onCreate", "requestWindowFeature",
        "setAllowFileAccess", "setContentView", "setDatabaseEnabled",
        "setDomStorageEnabled", "setJavaScriptEnabled", "setWebChromeClient",
        "setWebViewClient", "webView",
    ]))
    str_idx = {s: i for i, s in enumerate(strings)}

    type_descriptors = sorted([
        "I", "Landroid/app/Activity;", "Landroid/content/Context;", "Landroid/os/Bundle;",
        "Landroid/view/View;", "Landroid/webkit/WebChromeClient;", "Landroid/webkit/WebSettings;",
        "Landroid/webkit/WebView;", "Landroid/webkit/WebViewClient;",
        "Lcom/voca/app/MainActivity;", "Ljava/lang/String;", "V", "Z",
    ], key=lambda d: str_idx[d])
    type_idx = {d: i for i, d in enumerate(type_descriptors)}

    raw_protos = [
        ("V", "V", ()),
        ("VL", "V", ("Landroid/content/Context;",)),
        ("VL", "V", ("Landroid/os/Bundle;",)),
        ("VL", "V", ("Landroid/view/View;",)),
        ("VL", "V", ("Landroid/webkit/WebChromeClient;",)),
        ("VL", "V", ("Landroid/webkit/WebViewClient;",)),
        ("VL", "V", ("Ljava/lang/String;",)),
        ("VZ", "V", ("Z",)),
        ("L", "Landroid/webkit/WebSettings;", ()),
        ("Z", "Z", ()),
        ("ZI", "Z", ("I",)),
    ]
    protos = sorted(raw_protos, key=lambda p: (type_idx[p[1]], tuple(type_idx[t] for t in p[2])))
    proto_idx = {(p[1], p[2]): i for i, p in enumerate(protos)}

    fields = [("Lcom/voca/app/MainActivity;", "Landroid/webkit/WebView;", "webView")]
    field_idx = {f: i for i, f in enumerate(fields)}

    raw_methods = [
        ("Landroid/app/Activity;", ("V", ()), "<init>"),
        ("Landroid/app/Activity;", ("V", ()), "onBackPressed"),
        ("Landroid/app/Activity;", ("V", ("Landroid/os/Bundle;",)), "onCreate"),
        ("Landroid/app/Activity;", ("Z", ("I",)), "requestWindowFeature"),
        ("Landroid/app/Activity;", ("V", ("Landroid/view/View;",)), "setContentView"),
        ("Landroid/webkit/WebChromeClient;", ("V", ()), "<init>"),
        ("Landroid/webkit/WebSettings;", ("V", ("Z",)), "setAllowFileAccess"),
        ("Landroid/webkit/WebSettings;", ("V", ("Z",)), "setDatabaseEnabled"),
        ("Landroid/webkit/WebSettings;", ("V", ("Z",)), "setDomStorageEnabled"),
        ("Landroid/webkit/WebSettings;", ("V", ("Z",)), "setJavaScriptEnabled"),
        ("Landroid/webkit/WebView;", ("V", ("Landroid/content/Context;",)), "<init>"),
        ("Landroid/webkit/WebView;", ("Z", ()), "canGoBack"),
        ("Landroid/webkit/WebView;", ("Landroid/webkit/WebSettings;", ()), "getSettings"),
        ("Landroid/webkit/WebView;", ("V", ()), "goBack"),
        ("Landroid/webkit/WebView;", ("V", ("Ljava/lang/String;",)), "loadUrl"),
        ("Landroid/webkit/WebView;", ("V", ("Landroid/webkit/WebChromeClient;",)), "setWebChromeClient"),
        ("Landroid/webkit/WebView;", ("V", ("Landroid/webkit/WebViewClient;",)), "setWebViewClient"),
        ("Landroid/webkit/WebViewClient;", ("V", ()), "<init>"),
        ("Lcom/voca/app/MainActivity;", ("V", ()), "<init>"),
        ("Lcom/voca/app/MainActivity;", ("V", ()), "onBackPressed"),
        ("Lcom/voca/app/MainActivity;", ("V", ("Landroid/os/Bundle;",)), "onCreate"),
    ]
    methods = sorted(raw_methods, key=lambda m: (type_idx[m[0]], str_idx[m[2]], proto_idx[m[1]]))
    method_idx = {(m[0], m[2], m[1]): i for i, m in enumerate(methods)}

    def make_code_item(registers_size: int, ins_size: int, outs_size: int, insns_words: list) -> bytes:
        insns_bytes = b"".join(struct.pack("<H", w) for w in insns_words)
        hdr = struct.pack("<HHHHII", registers_size, ins_size, outs_size, 0, 0, len(insns_words))
        return align4(hdr + insns_bytes)

    m_act_init = method_idx[("Landroid/app/Activity;", "<init>", ("V", ()))]
    code_init = make_code_item(1, 1, 1, [0x1070, m_act_init, 0x0000, 0x000E])

    f_wv = field_idx[("Lcom/voca/app/MainActivity;", "Landroid/webkit/WebView;", "webView")]
    m_wv_can_go_back = method_idx[("Landroid/webkit/WebView;", "canGoBack", ("Z", ()))]
    m_wv_go_back = method_idx[("Landroid/webkit/WebView;", "goBack", ("V", ()))]
    m_act_back = method_idx[("Landroid/app/Activity;", "onBackPressed", ("V", ()))]
    code_back = make_code_item(2, 1, 1, [
        0x1054, f_wv,
        0x0038, 14,
        0x106E, m_wv_can_go_back, 0x0000,
        0x000A,
        0x0038, 8,
        0x1054, f_wv,
        0x106E, m_wv_go_back, 0x0000,
        0x000E,
        0x106F, m_act_back, 0x0001,
        0x000E,
    ])

    m_act_oncreate = method_idx[("Landroid/app/Activity;", "onCreate", ("V", ("Landroid/os/Bundle;",)))]
    m_act_req_feat = method_idx[("Landroid/app/Activity;", "requestWindowFeature", ("Z", ("I",)))]
    t_wv = type_idx["Landroid/webkit/WebView;"]
    m_wv_init = method_idx[("Landroid/webkit/WebView;", "<init>", ("V", ("Landroid/content/Context;",)))]
    m_wv_settings = method_idx[("Landroid/webkit/WebView;", "getSettings", ("Landroid/webkit/WebSettings;", ()))]
    m_ws_js = method_idx[("Landroid/webkit/WebSettings;", "setJavaScriptEnabled", ("V", ("Z",)))]
    m_ws_dom = method_idx[("Landroid/webkit/WebSettings;", "setDomStorageEnabled", ("V", ("Z",)))]
    m_ws_file = method_idx[("Landroid/webkit/WebSettings;", "setAllowFileAccess", ("V", ("Z",)))]
    m_ws_db = method_idx[("Landroid/webkit/WebSettings;", "setDatabaseEnabled", ("V", ("Z",)))]
    t_wvc = type_idx["Landroid/webkit/WebViewClient;"]
    m_wvc_init = method_idx[("Landroid/webkit/WebViewClient;", "<init>", ("V", ()))]
    m_wv_client = method_idx[("Landroid/webkit/WebView;", "setWebViewClient", ("V", ("Landroid/webkit/WebViewClient;",)))]
    t_wcc = type_idx["Landroid/webkit/WebChromeClient;"]
    m_wcc_init = method_idx[("Landroid/webkit/WebChromeClient;", "<init>", ("V", ()))]
    m_wv_chrome = method_idx[("Landroid/webkit/WebView;", "setWebChromeClient", ("V", ("Landroid/webkit/WebChromeClient;",)))]
    s_url = str_idx["file:///android_asset/index.html"]
    m_wv_load = method_idx[("Landroid/webkit/WebView;", "loadUrl", ("V", ("Ljava/lang/String;",)))]
    m_act_content = method_idx[("Landroid/app/Activity;", "setContentView", ("V", ("Landroid/view/View;",)))]

    # CRITICAL FIX: Call requestWindowFeature(1) BEFORE super.onCreate(savedInstanceState)!
    code_oncreate = make_code_item(5, 2, 2, [
        0x1112,                              # const/4 v1, 1 (Window.FEATURE_NO_TITLE)
        0x206E, m_act_req_feat, 0x0013,      # invoke-virtual {v3, v1}, Activity.requestWindowFeature(I)Z
        0x206F, m_act_oncreate, 0x0043,      # invoke-super {v3, v4}, Activity.onCreate(Bundle)V
        0x0022, t_wv,                        # new-instance v0, WebView
        0x2070, m_wv_init, 0x0030,           # invoke-direct {v0, v3}, WebView.<init>(Context)V
        0x305B, f_wv,                        # iput-object v0, v3, this.webView
        0x106E, m_wv_settings, 0x0000,       # invoke-virtual {v0}, WebView.getSettings()
        0x010C,                              # move-result-object v1
        0x1212,                              # const/4 v2, 1
        0x206E, m_ws_js, 0x0021,             # invoke-virtual {v1, v2}, setJavaScriptEnabled(true)
        0x206E, m_ws_dom, 0x0021,            # invoke-virtual {v1, v2}, setDomStorageEnabled(true)
        0x206E, m_ws_file, 0x0021,           # invoke-virtual {v1, v2}, setAllowFileAccess(true)
        0x206E, m_ws_db, 0x0021,             # invoke-virtual {v1, v2}, setDatabaseEnabled(true)
        0x0122, t_wvc,                       # new-instance v1, WebViewClient
        0x1070, m_wvc_init, 0x0001,          # invoke-direct {v1}, WebViewClient.<init>()V
        0x206E, m_wv_client, 0x0010,         # invoke-virtual {v0, v1}, setWebViewClient(v1)
        0x0122, t_wcc,                       # new-instance v1, WebChromeClient
        0x1070, m_wcc_init, 0x0001,          # invoke-direct {v1}, WebChromeClient.<init>()V
        0x206E, m_wv_chrome, 0x0010,         # invoke-virtual {v0, v1}, setWebChromeClient(v1)
        0x011A, s_url,                       # const-string v1, "file:///android_asset/index.html"
        0x206E, m_wv_load, 0x0010,           # invoke-virtual {v0, v1}, loadUrl(v1)
        0x206E, m_act_content, 0x0003,       # invoke-virtual {v3, v0}, setContentView(v0)
        0x000E,                              # return-void
    ])

    hdr_size = 0x70
    string_ids_off = hdr_size
    type_ids_off = string_ids_off + len(strings) * 4
    proto_ids_off = type_ids_off + len(type_descriptors) * 4
    field_ids_off = proto_ids_off + len(protos) * 12
    method_ids_off = field_ids_off + len(fields) * 8
    class_defs_off = method_ids_off + len(methods) * 8
    data_off = class_defs_off + 32
    data_buf = bytearray()

    type_list_offsets = {}
    unique_param_tuples = sorted(set(p[2] for p in protos if len(p[2]) > 0), key=lambda t: tuple(type_idx[x] for x in t))
    for pt in unique_param_tuples:
        while len(data_buf) % 4 != 0:
            data_buf.append(0)
        type_list_offsets[pt] = data_off + len(data_buf)
        data_buf.extend(struct.pack("<I", len(pt)))
        for td in pt:
            data_buf.extend(struct.pack("<H", type_idx[td]))

    while len(data_buf) % 4 != 0:
        data_buf.append(0)
    code_init_off = data_off + len(data_buf)
    data_buf.extend(code_init)
    code_back_off = data_off + len(data_buf)
    data_buf.extend(code_back)
    code_oncreate_off = data_off + len(data_buf)
    data_buf.extend(code_oncreate)

    string_data_offsets = []
    for s in strings:
        string_data_offsets.append(data_off + len(data_buf))
        raw_utf8 = s.encode("utf-8")
        data_buf.extend(uleb128(len(s)) + raw_utf8 + b"\x00")

    class_data_off = data_off + len(data_buf)
    m_main_init = method_idx[("Lcom/voca/app/MainActivity;", "<init>", ("V", ()))]
    m_main_back = method_idx[("Lcom/voca/app/MainActivity;", "onBackPressed", ("V", ()))]
    m_main_oncreate = method_idx[("Lcom/voca/app/MainActivity;", "onCreate", ("V", ("Landroid/os/Bundle;",)))]

    data_buf.extend(
        uleb128(0) + uleb128(1) + uleb128(1) + uleb128(2) +
        uleb128(f_wv) + uleb128(0x0002) +
        uleb128(m_main_init) + uleb128(0x10001) + uleb128(code_init_off) +
        uleb128(m_main_back) + uleb128(0x0001) + uleb128(code_back_off) +
        uleb128(m_main_oncreate - m_main_back) + uleb128(0x0004) + uleb128(code_oncreate_off)
    )

    while len(data_buf) % 4 != 0:
        data_buf.append(0)
    map_off = data_off + len(data_buf)
    map_items = [
        (0x0000, 1, 0),
        (0x0001, len(strings), string_ids_off),
        (0x0002, len(type_descriptors), type_ids_off),
        (0x0003, len(protos), proto_ids_off),
        (0x0004, len(fields), field_ids_off),
        (0x0005, len(methods), method_ids_off),
        (0x0006, 1, class_defs_off),
        (0x1001, len(unique_param_tuples), type_list_offsets[unique_param_tuples[0]]),
        (0x2001, 3, code_init_off),
        (0x2002, len(strings), string_data_offsets[0]),
        (0x2000, 1, class_data_off),
        (0x1000, 1, map_off),
    ]
    data_buf.extend(struct.pack("<I", len(map_items)))
    for t_code, count, offset in map_items:
        data_buf.extend(struct.pack("<HHII", t_code, 0, count, offset))

    file_size = data_off + len(data_buf)
    data_size = len(data_buf)

    string_ids_bytes = b"".join(struct.pack("<I", off) for off in string_data_offsets)
    type_ids_bytes = b"".join(struct.pack("<I", str_idx[d]) for d in type_descriptors)
    proto_ids_bytes = b"".join(struct.pack("<III", str_idx[p[0]], type_idx[p[1]], type_list_offsets.get(p[2], 0)) for p in protos)
    field_ids_bytes = b"".join(struct.pack("<HHI", type_idx[f[0]], type_idx[f[1]], str_idx[f[2]]) for f in fields)
    method_ids_bytes = b"".join(struct.pack("<HHI", type_idx[m[0]], proto_idx[m[1]], str_idx[m[2]]) for m in methods)
    class_defs_bytes = struct.pack(
        "<IIIIIIII",
        type_idx["Lcom/voca/app/MainActivity;"], 0x0001, type_idx["Landroid/app/Activity;"],
        0, str_idx["MainActivity.java"], 0, class_data_off, 0
    )
    header_without_hashes = struct.pack(
        "<IIIIIIIIIIIIIIIIIIII",
        file_size, hdr_size, 0x12345678, 0, 0, map_off,
        len(strings), string_ids_off, len(type_descriptors), type_ids_off,
        len(protos), proto_ids_off, len(fields), field_ids_off,
        len(methods), method_ids_off, 1, class_defs_off, data_size, data_off
    )
    body_after_sig = header_without_hashes + string_ids_bytes + type_ids_bytes + proto_ids_bytes + field_ids_bytes + method_ids_bytes + class_defs_bytes + bytes(data_buf)
    sha1_sig = hashlib.sha1(body_after_sig).digest()
    adler_val = zlib.adler32(sha1_sig + body_after_sig) & 0xFFFFFFFF
    return b"dex\n035\x00" + struct.pack("<I", adler_val) + sha1_sig + body_after_sig


def build_resources_arsc() -> bytes:
    def make_utf16_pool(strs: list) -> bytes:
        blobs, offs, cur = [], [], 0
        for s in strs:
            offs.append(cur)
            b = struct.pack("<H", len(s)) + s.encode("utf-16le") + b"\x00\x00"
            blobs.append(b)
            cur += len(b)
        pdata = align4(b"".join(blobs))
        s_start = 28 + len(strs) * 4
        return struct.pack("<HHIIIIII", 0x0001, 28, s_start + len(pdata), len(strs), 0, 0, s_start, 0) + b"".join(struct.pack("<I", o) for o in offs) + pdata

    global_pool = make_utf16_pool(["res/drawable/ic_launcher.png"])
    type_pool = make_utf16_pool(["drawable"])
    key_pool = make_utf16_pool(["ic_launcher"])
    type_spec_chunk = struct.pack("<HHIBBHI", 0x0202, 16, 20, 1, 0, 0, 1) + struct.pack("<I", 0)
    res_config = struct.pack("<I", 48) + b"\x00" * 44
    entry_bytes = struct.pack("<HHI", 8, 0, 0) + struct.pack("<HBBI", 8, 0, 0x03, 0)
    type_chunk = struct.pack("<HHIBBHII", 0x0201, 68, 68 + 4 + len(entry_bytes), 1, 0, 0, 1, 72) + res_config + struct.pack("<I", 0) + entry_bytes
    pkg_name_u16 = "com.voca.app".encode("utf-16le").ljust(256, b"\x00")
    pkg_body = type_pool + key_pool + type_spec_chunk + type_chunk
    pkg_chunk = struct.pack("<HHII256sIIIII", 0x0200, 288, 288 + len(pkg_body), 0x7F, pkg_name_u16, 288, 1, 288 + len(type_pool), 1, 0) + pkg_body
    total_size = 12 + len(global_pool) + len(pkg_chunk)
    return struct.pack("<HHII", 0x0002, 12, total_size, 1) + global_pool + pkg_chunk

def get_section_chunk_digests(data: bytes) -> list:
    """Split a section into 1 MB chunks and return list of sha256(0xa5 || uint32(len) || chunk)."""
    CHUNK_SIZE = 1024 * 1024
    digests = []
    offset = 0
    while offset < len(data):
        chunk = data[offset:offset + CHUNK_SIZE]
        digests.append(hashlib.sha256(b"\xa5" + struct.pack("<I", len(chunk)) + chunk).digest())
        offset += CHUNK_SIZE
    return digests



def build_android_manifest_axml_v103() -> bytes:
    res_attrs = [
        ("theme", 0x01010000), ("label", 0x01010001), ("icon", 0x01010002),
        ("name", 0x01010003), ("exported", 0x01010010), ("configChanges", 0x0101001f),
        ("minSdkVersion", 0x0101020c), ("versionCode", 0x0101021b), ("versionName", 0x0101021c),
        ("targetSdkVersion", 0x01010270), ("hardwareAccelerated", 0x010102d3),
    ]
    extra_strings = [
        "android", "http://schemas.android.com/apk/res/android", "", "manifest",
        "package", "com.voca.app", "1.0.4", "uses-sdk", "uses-permission",
        "android.permission.INTERNET", "application", "Voca",
        "activity", "com.voca.app.MainActivity", "intent-filter", "action",
        "android.intent.action.MAIN", "category", "android.intent.category.LAUNCHER",
    ]
    all_strings = [a[0] for a in res_attrs] + extra_strings
    s_idx = {s: i for i, s in enumerate(all_strings)}

    str_blobs, offsets, cur_off = [], [], 0
    for s in all_strings:
        offsets.append(cur_off)
        blob = struct.pack("<H", len(s)) + s.encode("utf-16le") + b"\x00\x00"
        str_blobs.append(blob)
        cur_off += len(blob)
    pool_data = align4(b"".join(str_blobs))
    strings_start = 28 + len(all_strings) * 4
    sp_chunk = struct.pack("<HHIIIIII", 0x0001, 28, strings_start + len(pool_data), len(all_strings), 0, 0, strings_start, 0) + b"".join(struct.pack("<I", o) for o in offsets) + pool_data

    res_map_body = b"".join(struct.pack("<I", r[1]) for r in res_attrs)
    res_map_chunk = struct.pack("<HHI", 0x0180, 8, 8 + len(res_map_body)) + res_map_body

    NS_ANDROID = s_idx["http://schemas.android.com/apk/res/android"]
    PFX_ANDROID = s_idx["android"]
    NO_IDX = 0xFFFFFFFF

    def make_start_ns(line: int) -> bytes:
        return struct.pack("<HHIIIII", 0x0100, 16, 24, line, NO_IDX, PFX_ANDROID, NS_ANDROID)
    def make_end_ns(line: int) -> bytes:
        return struct.pack("<HHIIIII", 0x0101, 16, 24, line, NO_IDX, PFX_ANDROID, NS_ANDROID)
    def make_attr(ns: int, name_str: str, raw_val_str, val_type: int, data_val: int) -> bytes:
        raw_i = s_idx[raw_val_str] if raw_val_str is not None else NO_IDX
        return struct.pack("<IIIHBBI", ns, s_idx[name_str], raw_i, 8, 0, val_type, data_val)
    def make_start_el(line: int, name_str: str, attrs: list) -> bytes:
        attr_bytes = b"".join(attrs)
        node_hdr = struct.pack("<HHIII", 0x0102, 16, 36 + len(attr_bytes), line, NO_IDX)
        attr_ext = struct.pack("<IIHHHHHH", NO_IDX, s_idx[name_str], 20, 20, len(attrs), 0, 0, 0)
        assert len(node_hdr) == 16 and len(attr_ext) == 20
        return node_hdr + attr_ext + attr_bytes
    def make_end_el(line: int, name_str: str) -> bytes:
        return struct.pack("<HHIIIII", 0x0103, 16, 24, line, NO_IDX, NO_IDX, s_idx[name_str])

    nodes = [
        make_start_ns(2),
        make_start_el(2, "manifest", [
            make_attr(NS_ANDROID, "versionCode", None, 0x10, 5),
            make_attr(NS_ANDROID, "versionName", "1.0.4", 0x03, s_idx["1.0.4"]),
            make_attr(NO_IDX, "package", "com.voca.app", 0x03, s_idx["com.voca.app"]),
        ]),
        make_start_el(5, "uses-permission", [
            make_attr(NS_ANDROID, "name", "android.permission.INTERNET", 0x03, s_idx["android.permission.INTERNET"]),
        ]),
        make_end_el(5, "uses-permission"),
        make_start_el(6, "uses-sdk", [
            make_attr(NS_ANDROID, "minSdkVersion", None, 0x10, 19),
            make_attr(NS_ANDROID, "targetSdkVersion", None, 0x10, 28),
        ]),
        make_end_el(6, "uses-sdk"),
        make_start_el(8, "application", [
            make_attr(NS_ANDROID, "theme", None, 0x01, 0x01030006),
            make_attr(NS_ANDROID, "label", "Voca", 0x03, s_idx["Voca"]),
            make_attr(NS_ANDROID, "icon", None, 0x01, 0x7F010000),
            make_attr(NS_ANDROID, "hardwareAccelerated", None, 0x12, 0xFFFFFFFF),
        ]),
        make_start_el(12, "activity", [
            make_attr(NS_ANDROID, "label", "Voca", 0x03, s_idx["Voca"]),
            make_attr(NS_ANDROID, "name", "com.voca.app.MainActivity", 0x03, s_idx["com.voca.app.MainActivity"]),
            make_attr(NS_ANDROID, "exported", None, 0x12, 0xFFFFFFFF),
            make_attr(NS_ANDROID, "configChanges", None, 0x11, 0x000004A0),
        ]),
        make_start_el(16, "intent-filter", []),
        make_start_el(17, "action", [make_attr(NS_ANDROID, "name", "android.intent.action.MAIN", 0x03, s_idx["android.intent.action.MAIN"])]),
        make_end_el(17, "action"),
        make_start_el(18, "category", [make_attr(NS_ANDROID, "name", "android.intent.category.LAUNCHER", 0x03, s_idx["android.intent.category.LAUNCHER"])]),
        make_end_el(18, "category"),
        make_end_el(16, "intent-filter"),
        make_end_el(12, "activity"),
        make_end_el(8, "application"),
        make_end_el(2, "manifest"),
        make_end_ns(2),
    ]
    body = sp_chunk + res_map_chunk + b"".join(nodes)
    return struct.pack("<HHI", 0x0003, 8, 8 + len(body)) + body

def build_signed_apk_v103(apk_path: str, html_content: bytes):
    manifest_xml = build_android_manifest_axml_v103()
    resources_arsc = build_resources_arsc()
    classes_dex = build_classes_dex()
    icon_png = get_voca_v103_icon_png(192)

    fonts_dir = os.path.join(ASSETS_DIR, "fonts")
    font_entries = []
    for fn in ["Inter-Regular.woff2", "Inter-Bold.woff2", "NotoSansCJKsc-Full.woff2"]:
        with open(os.path.join(fonts_dir, fn), "rb") as bf:
            font_entries.append((f"assets/fonts/{fn}", bf.read(), False))

    files_to_pack = [
        ("AndroidManifest.xml", manifest_xml, True),
        ("resources.arsc", resources_arsc, False),
        ("classes.dex", classes_dex, True),
        ("res/drawable/ic_launcher.png", icon_png, False),
        ("assets/index.html", html_content, True),
    ] + font_entries

    with tempfile.TemporaryDirectory() as tmp:
        key_pem = os.path.join(tmp, "key.pem")
        cert_pem = os.path.join(tmp, "cert.pem")
        cert_der = os.path.join(tmp, "cert.der")
        pub_der = os.path.join(tmp, "pub.der")

        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", key_pem, "-out", cert_pem, "-days", "10000",
            "-subj", "/CN=Voca Offline Studio/O=Voca/C=CN"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["openssl", "x509", "-in", cert_pem, "-outform", "DER", "-out", cert_der], check=True)
        subprocess.run(["openssl", "pkey", "-in", key_pem, "-pubout", "-outform", "DER", "-out", pub_der], check=True)

        mf_header = "Manifest-Version: 1.0\r\nCreated-By: 1.0.4 (Voca Builder)\r\n\r\n"
        mf_sections = []
        sf_sections = []
        for fname, fbytes, _ in files_to_pack:
            b64_sha256 = base64.b64encode(hashlib.sha256(fbytes).digest()).decode("ascii")
            entry_block = f"Name: {fname}\r\nSHA-256-Digest: {b64_sha256}\r\n\r\n"
            mf_sections.append(entry_block)
            sf_b64 = base64.b64encode(hashlib.sha256(entry_block.encode("utf-8")).digest()).decode("ascii")
            sf_sections.append(f"Name: {fname}\r\nSHA-256-Digest: {sf_b64}\r\n\r\n")

        manifest_mf = (mf_header + "".join(mf_sections)).encode("utf-8")
        mf_main_b64 = base64.b64encode(hashlib.sha256(manifest_mf).digest()).decode("ascii")
        cert_sf = (
            "Signature-Version: 1.0\r\nCreated-By: 1.0.4 (Voca Builder)\r\n"
            f"SHA-256-Digest-Manifest: {mf_main_b64}\r\nX-Android-APK-Signed: 2\r\n\r\n" +
            "".join(sf_sections)
        ).encode("utf-8")

        sf_file = os.path.join(tmp, "CERT.SF")
        rsa_file = os.path.join(tmp, "CERT.RSA")
        with open(sf_file, "wb") as f:
            f.write(cert_sf)
        subprocess.run(["openssl", "cms", "-sign", "-binary", "-noattr", "-in", sf_file, "-signer", cert_pem, "-inkey", key_pem, "-outform", "DER", "-out", rsa_file], check=True)
        with open(rsa_file, "rb") as f:
            cert_rsa = f.read()

        all_entries = files_to_pack + [
            ("META-INF/MANIFEST.MF", manifest_mf, True),
            ("META-INF/CERT.SF", cert_sf, True),
            ("META-INF/CERT.RSA", cert_rsa, True),
        ]

        local_records = bytearray()
        cd_records = bytearray()
        cd_count = 0

        for fname, raw_data, compress in all_entries:
            fname_bytes = fname.encode("utf-8")
            crc = zlib.crc32(raw_data) & 0xFFFFFFFF
            uncomp_size = len(raw_data)
            if compress:
                cobj = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
                comp_data = cobj.compress(raw_data) + cobj.flush()
                method = 8
            else:
                comp_data = raw_data
                method = 0

            comp_size = len(comp_data)
            local_hdr_offset = len(local_records)
            extra = b""
            if not compress:
                data_start = local_hdr_offset + 30 + len(fname_bytes)
                pad_len = (4 - (data_start % 4)) % 4
                extra = b"\x00" * pad_len

            lfh = struct.pack("<IHHHHHIIIHH", 0x04034B50, 20, 0, method, 0, 0x5521, crc, comp_size, uncomp_size, len(fname_bytes), len(extra)) + fname_bytes + extra
            local_records.extend(lfh + comp_data)
            cdh = struct.pack("<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, 0, method, 0, 0x5521, crc, comp_size, uncomp_size, len(fname_bytes), 0, 0, 0, 0, 0, local_hdr_offset) + fname_bytes
            cd_records.extend(cdh)
            cd_count += 1

        eocd_for_digest = struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, cd_count, cd_count, len(cd_records), len(local_records), 0)
        all_chunk_digests = (
            get_section_chunk_digests(bytes(local_records)) +
            get_section_chunk_digests(bytes(cd_records)) +
            get_section_chunk_digests(eocd_for_digest)
        )
        top_digest = hashlib.sha256(
            b"\x5a" + struct.pack("<I", len(all_chunk_digests)) + b"".join(all_chunk_digests)
        ).digest()

        with open(cert_der, "rb") as f:
            cert_der_bytes = f.read()
        with open(pub_der, "rb") as f:
            pub_der_bytes = f.read()

        def len_prefixed(b: bytes) -> bytes:
            return struct.pack("<I", len(b)) + b

        digest_entry = struct.pack("<I", 0x0103) + len_prefixed(top_digest)
        signed_data = len_prefixed(len_prefixed(digest_entry)) + len_prefixed(len_prefixed(cert_der_bytes)) + len_prefixed(b"")

        sd_file = os.path.join(tmp, "signed_data.bin")
        sig_file = os.path.join(tmp, "sig.bin")
        with open(sd_file, "wb") as f:
            f.write(signed_data)
        subprocess.run(["openssl", "dgst", "-sha256", "-sign", key_pem, "-out", sig_file, sd_file], check=True)
        with open(sig_file, "rb") as f:
            sig_bytes = f.read()

        sig_entry = struct.pack("<I", 0x0103) + len_prefixed(sig_bytes)
        signer_block = len_prefixed(signed_data) + len_prefixed(len_prefixed(sig_entry)) + len_prefixed(pub_der_bytes)
        v2_value = len_prefixed(len_prefixed(signer_block))
        pair_payload = struct.pack("<I", 0x7109871A) + v2_value
        id_val_pair = struct.pack("<Q", len(pair_payload)) + pair_payload
        block_size_field = len(id_val_pair) + 8 + 16
        apk_sig_block = struct.pack("<Q", block_size_field) + id_val_pair + struct.pack("<Q", block_size_field) + b"APK Sig Block 42"

        new_cd_offset = len(local_records) + len(apk_sig_block)
        final_eocd = struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, cd_count, cd_count, len(cd_records), new_cd_offset, 0)
        os.makedirs(os.path.dirname(os.path.abspath(apk_path)), exist_ok=True)
        with open(apk_path, "wb") as f:
            f.write(bytes(local_records) + apk_sig_block + bytes(cd_records) + final_eocd)

    print(f"Built v1.0.4 signed APK: {apk_path} ({os.path.getsize(apk_path):,} bytes)")
