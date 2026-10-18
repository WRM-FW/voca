#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voca v1.0.3 Windows Native PE32+ (x86_64 GUI) Executable Builder.
Upgrades in v1.0.3 (Taskbar & High-DPI Icon Blur Fix):
1. Embeds all 8 Windows DPI icon frames into .rsrc (RT_ICON IDs 1..8 + RT_GROUP_ICON ID 1):
   - ID 1: 256x256 (PNG stream for Windows High-DPI shell & large icons)
   - ID 2..8: 128x128, 64x64, 48x48, 40x40, 32x32, 24x24, 16x16 (Standard Win32 32-bit BGRA BITMAPINFOHEADER DIBs + 1-bit AND masks for 100%/125%/150%/175%/200%/250% taskbar, titlebar, Alt+Tab, and shortcuts)
2. Embeds RT_MANIFEST (Type 24, ID 1) declaring PerMonitorV2 High-DPI awareness so Windows never bitmap-stretches the window or icon.
3. Passes `--start-maximized` and `SW_SHOWMAXIMIZED` (3) to ShellExecuteW.
"""
import os
import shutil
import struct
import subprocess
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.environ.get("VOCA_ASSETS_DIR", os.path.abspath(os.path.join(SCRIPT_DIR, "..", "assets")))
if not os.path.exists(ASSETS_DIR):
    alt_assets = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "assets"))
    if os.path.exists(alt_assets):
        ASSETS_DIR = alt_assets

def get_voca_v103_icon_png(size: int) -> bytes:
    p = os.path.join(ASSETS_DIR, "icons", f"icon_{size}.png")
    with open(p, "rb") as f:
        return f.read()

def get_voca_v103_icon_dib(size: int) -> bytes:
    p = os.path.join(ASSETS_DIR, "icons", f"icon_{size}.dib")
    with open(p, "rb") as f:
        return f.read()

def create_ico_file(ico_path: str):
    src_ico = os.path.join(ASSETS_DIR, "voca.ico")
    os.makedirs(os.path.dirname(os.path.abspath(ico_path)), exist_ok=True)
    shutil.copy2(src_ico, ico_path)

def align(val: int, alignment: int) -> int:
    return (val + alignment - 1) & ~(alignment - 1)

def pad_bytes(data: bytes, alignment: int) -> bytes:
    rem = len(data) % alignment
    return data if rem == 0 else data + b"\x00" * (alignment - rem)

def utf16le_z(s: str) -> bytes:
    return s.encode("utf-16le") + b"\x00\x00"

def build_rsrc_section(rsrc_rva: int) -> bytes:
    """
    Build a Win32 PE .rsrc section containing:
    - RT_ICON (Type 3): IDs 1..8 for sizes [256 (PNG), 128, 64, 48, 40, 32, 24, 16 (32-bit BGRA DIBs)]
    - RT_GROUP_ICON (Type 14): ID 1 referencing RT_ICON IDs 1..8
    - RT_MANIFEST (Type 24): ID 1 declaring PerMonitorV2 High-DPI awareness
    """
    icon_sizes = [256, 128, 64, 48, 40, 32, 24, 16]
    icon_payloads = []
    for sz in icon_sizes:
        if sz == 256:
            icon_payloads.append(get_voca_v103_icon_png(256))
        else:
            icon_payloads.append(get_voca_v103_icon_dib(sz))

    # GRPICONDIR header + 8 GRPICONDIRENTRY (14 bytes each)
    grp_icon = bytearray(struct.pack("<HHH", 0, 1, len(icon_sizes)))
    for idx, (sz, blob) in enumerate(zip(icon_sizes, icon_payloads), start=1):
        bw = 0 if sz == 256 else sz
        bh = 0 if sz == 256 else sz
        grp_icon.extend(struct.pack("<BBBBHHIH", bw, bh, 0, 0, 1, 32, len(blob), idx))
    grp_icon_bytes = bytes(grp_icon)

    manifest_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
        '<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0" xmlns:asmv3="urn:schemas-microsoft-com:asm.v3">\r\n'
        '  <assemblyIdentity version="1.0.5.0" processorArchitecture="amd64" name="Voca.Desktop.App" type="win32"/>\r\n'
        '  <description>Voca v1.0.5 Offline Ebbinghaus Vocabulary Application</description>\r\n'
        '  <asmv3:application>\r\n'
        '    <asmv3:windowsSettings>\r\n'
        '      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true/pm</dpiAware>\r\n'
        '      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2, PerMonitor</dpiAwareness>\r\n'
        '    </asmv3:windowsSettings>\r\n'
        '  </asmv3:application>\r\n'
        '</assembly>\r\n'
    ).encode("utf-8")

    # Resource tree layout:
    # Root Dir (offset 0): 3 entries (Type 3 RT_ICON, Type 14 RT_GROUP_ICON, Type 24 RT_MANIFEST) -> 16 + 3*8 = 40 bytes
    # Type 3 Dir (offset 40): 8 entries (IDs 1..8) -> 16 + 8*8 = 80 bytes (ends at 120)
    # Type 14 Dir (offset 120): 1 entry (ID 1) -> 16 + 1*8 = 24 bytes (ends at 144)
    # Type 24 Dir (offset 144): 1 entry (ID 1) -> 16 + 1*8 = 24 bytes (ends at 168)
    # 10 Language Dirs (offsets 168 + k*24 for k=0..9): each 24 bytes -> 240 bytes (ends at 408)
    # 10 Data Entries (offsets 408 + k*16 for k=0..9): each 16 bytes -> 160 bytes (ends at 568)
    # Raw Payload Data starts at offset 568!

    DIR_FLAG = 0x80000000
    root_dir = struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 3)
    root_dir += struct.pack("<II", 3, DIR_FLAG | 40)
    root_dir += struct.pack("<II", 14, DIR_FLAG | 120)
    root_dir += struct.pack("<II", 24, DIR_FLAG | 144)

    type3_dir = bytearray(struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 8))
    for i in range(8):
        lang_off = 168 + i * 24
        type3_dir.extend(struct.pack("<II", i + 1, DIR_FLAG | lang_off))

    type14_dir = struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 1) + struct.pack("<II", 1, DIR_FLAG | (168 + 8 * 24))
    type24_dir = struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 1) + struct.pack("<II", 1, DIR_FLAG | (168 + 9 * 24))

    lang_dirs = bytearray()
    for k in range(10):
        de_off = 408 + k * 16
        lang_dirs.extend(struct.pack("<IIHHHH", 0, 0, 0, 0, 0, 1) + struct.pack("<II", 0x0409, de_off))

    all_raw_items = icon_payloads + [grp_icon_bytes, manifest_xml]
    data_entries = bytearray()
    raw_blob = bytearray()
    cur_raw_off = 568

    for item in all_raw_items:
        data_entries.extend(struct.pack("<IIII", rsrc_rva + cur_raw_off, len(item), 0, 0))
        padded = pad_bytes(item, 8)
        raw_blob.extend(padded)
        cur_raw_off += len(padded)

    header_tree = root_dir + bytes(type3_dir) + type14_dir + type24_dir + bytes(lang_dirs) + bytes(data_entries)
    assert len(header_tree) == 568, f"Expected 568 bytes, got {len(header_tree)}"
    return header_tree + bytes(raw_blob)

def build_voca_exe(out_path: str):
    rdata_rva = 0x2000
    hn_buf = bytearray()

    def add_ascii_z(s: str) -> int:
        off = 0x0A0 + len(hn_buf)
        hn_buf.extend(s.encode("ascii") + b"\x00")
        if len(hn_buf) % 2 != 0:
            hn_buf.append(0)
        return rdata_rva + off

    def add_hint_name(name: str) -> int:
        off = 0x0A0 + len(hn_buf)
        hn_buf.extend(struct.pack("<H", 0) + name.encode("ascii") + b"\x00")
        if len(hn_buf) % 2 != 0:
            hn_buf.append(0)
        return rdata_rva + off

    rva_kernel32_name = add_ascii_z("KERNEL32.dll")
    rva_shell32_name = add_ascii_z("SHELL32.dll")
    rva_GetModuleFileNameW = add_hint_name("GetModuleFileNameW")
    rva_SetCurrentDirectoryW = add_hint_name("SetCurrentDirectoryW")
    rva_ExitProcess = add_hint_name("ExitProcess")
    rva_ShellExecuteW = add_hint_name("ShellExecuteW")

    assert 0x0A0 + len(hn_buf) <= 0x140
    hn_buf.extend(b"\x00" * (0x140 - (0x0A0 + len(hn_buf))))

    iat_kernel32 = struct.pack("<QQQQ", rva_GetModuleFileNameW, rva_SetCurrentDirectoryW, rva_ExitProcess, 0)
    iat_shell32 = struct.pack("<QQ", rva_ShellExecuteW, 0)
    ilt_kernel32 = iat_kernel32
    ilt_shell32 = iat_shell32

    idt = (
        struct.pack("<IIIII", rdata_rva + 0x030, 0, 0, rva_kernel32_name, rdata_rva + 0x000) +
        struct.pack("<IIIII", rdata_rva + 0x050, 0, 0, rva_shell32_name, rdata_rva + 0x020) +
        struct.pack("<IIIII", 0, 0, 0, 0, 0) +
        b"\x00\x00\x00\x00"
    )
    assert len(iat_kernel32) + len(iat_shell32) + len(ilt_kernel32) + len(ilt_shell32) + len(idt) == 0x0A0

    str_buf = bytearray()
    def add_wstr(s: str) -> int:
        off = 0x140 + len(str_buf)
        str_buf.extend(utf16le_z(s))
        while len(str_buf) % 8 != 0:
            str_buf.append(0)
        return rdata_rva + off

    rva_w_open = add_wstr("open")
    rva_w_msedge = add_wstr("msedge.exe")
    rva_w_chrome = add_wstr("chrome.exe")
    rva_w_rel_html = add_wstr("\\app\\index.html")
    rva_w_arg_prefix = add_wstr("--app=\"")
    rva_w_arg_mid = add_wstr("\" --start-maximized --high-dpi-support=1 --user-data-dir=\"")
    rva_w_arg_suffix = add_wstr("\\data\\profile\"")
    rva_w_arg_tail = add_wstr(" --no-first-run --no-default-browser-check --disable-extensions --disable-sync")

    rdata_raw = iat_kernel32 + iat_shell32 + ilt_kernel32 + ilt_shell32 + idt + bytes(hn_buf) + bytes(str_buf)

    rva_dir_buf = 0x3000
    rva_html_buf = 0x3400
    rva_args_buf = 0x3800

    asm_code = f"""
    .intel_syntax noprefix
    .text
    .globl _start
_start:
    sub rsp, 0x38

    # 1. GetModuleFileNameW(NULL, dirBuf, 500)
    .byte 0x48, 0x8d, 0x1d, 0xf5, 0xff, 0xff, 0xff
    sub rbx, 0x1000
    xor rcx, rcx
    lea rdx, [rbx + {rva_dir_buf}]
    mov r8d, 500
    call QWORD PTR [rbx + {rdata_rva + 0x000}]

    # Strip filename from dirBuf
    lea rdi, [rbx + {rva_dir_buf}]
    mov ecx, eax
1:
    test ecx, ecx
    jz 2f
    dec ecx
    movzx eax, WORD PTR [rdi + rcx*2]
    cmp ax, 0x5c
    je 3f
    cmp ax, 0x2f
    je 3f
    jmp 1b
3:
    mov WORD PTR [rdi + rcx*2], 0
2:
    # 2. SetCurrentDirectoryW(dirBuf)
    lea rcx, [rbx + {rva_dir_buf}]
    call QWORD PTR [rbx + {rdata_rva + 0x008}]

    # 3. Build htmlBuf = dirBuf + "\\app\\index.html"
    lea rdi, [rbx + {rva_html_buf}]
    lea rsi, [rbx + {rva_dir_buf}]
    call copy_wstr
    lea rsi, [rbx + {rva_w_rel_html}]
    call copy_wstr

    # 4. Build argsBuf
    lea rdi, [rbx + {rva_args_buf}]
    lea rsi, [rbx + {rva_w_arg_prefix}]
    call copy_wstr
    lea rsi, [rbx + {rva_html_buf}]
    call copy_wstr
    lea rsi, [rbx + {rva_w_arg_mid}]
    call copy_wstr
    lea rsi, [rbx + {rva_dir_buf}]
    call copy_wstr
    lea rsi, [rbx + {rva_w_arg_suffix}]
    call copy_wstr
    lea rsi, [rbx + {rva_w_arg_tail}]
    call copy_wstr

    # 5. Try ShellExecuteW(NULL, L"open", L"msedge.exe", argsBuf, dirBuf, SW_SHOWMAXIMIZED=3)
    xor rcx, rcx
    lea rdx, [rbx + {rva_w_open}]
    lea r8, [rbx + {rva_w_msedge}]
    lea r9, [rbx + {rva_args_buf}]
    lea rax, [rbx + {rva_dir_buf}]
    mov QWORD PTR [rsp + 0x20], rax
    mov QWORD PTR [rsp + 0x28], 3
    call QWORD PTR [rbx + {rdata_rva + 0x020}]
    cmp rax, 32
    jg launch_ok

    # 6. Fallback 1: Try chrome.exe with argsBuf (SW_SHOWMAXIMIZED=3)
    xor rcx, rcx
    lea rdx, [rbx + {rva_w_open}]
    lea r8, [rbx + {rva_w_chrome}]
    lea r9, [rbx + {rva_args_buf}]
    lea rax, [rbx + {rva_dir_buf}]
    mov QWORD PTR [rsp + 0x20], rax
    mov QWORD PTR [rsp + 0x28], 3
    call QWORD PTR [rbx + {rdata_rva + 0x020}]
    cmp rax, 32
    jg launch_ok

    # 7. Fallback 2: Open htmlBuf directly via ShellExecuteW (SW_SHOWMAXIMIZED=3)
    xor rcx, rcx
    lea rdx, [rbx + {rva_w_open}]
    lea r8, [rbx + {rva_html_buf}]
    xor r9, r9
    lea rax, [rbx + {rva_dir_buf}]
    mov QWORD PTR [rsp + 0x20], rax
    mov QWORD PTR [rsp + 0x28], 3
    call QWORD PTR [rbx + {rdata_rva + 0x020}]

launch_ok:
    xor ecx, ecx
    call QWORD PTR [rbx + {rdata_rva + 0x010}]
    ret

copy_wstr:
4:
    movzx eax, WORD PTR [rsi]
    mov WORD PTR [rdi], ax
    test ax, ax
    jz 5f
    add rsi, 2
    add rdi, 2
    jmp 4b
5:
    ret
"""
    with tempfile.TemporaryDirectory() as tmp:
        s_file = os.path.join(tmp, "voca.s")
        o_file = os.path.join(tmp, "voca.o")
        bin_file = os.path.join(tmp, "voca.bin")
        with open(s_file, "w") as f:
            f.write(asm_code)
        subprocess.run(["as", "--64", s_file, "-o", o_file], check=True)
        subprocess.run(["objcopy", "-O", "binary", "-j", ".text", o_file, bin_file], check=True)
        with open(bin_file, "rb") as f:
            text_raw = f.read()

    rsrc_rva = 0x4000
    rsrc_raw = build_rsrc_section(rsrc_rva)

    file_align = 0x200
    sect_align = 0x1000
    image_base = 0x00400000

    text_file = pad_bytes(text_raw, file_align)
    rdata_file = pad_bytes(rdata_raw, file_align)
    data_file = b"\x00" * 0x1000
    rsrc_file = pad_bytes(rsrc_raw, file_align)

    dos_header = bytearray(0x80)
    dos_header[0:2] = b"MZ"
    struct.pack_into("<H", dos_header, 0x02, 0x90)
    struct.pack_into("<H", dos_header, 0x04, 3)
    struct.pack_into("<H", dos_header, 0x08, 4)
    struct.pack_into("<H", dos_header, 0x10, 0xB8)
    struct.pack_into("<H", dos_header, 0x18, 0x40)
    struct.pack_into("<I", dos_header, 0x3C, 0x80)

    pe_sig = b"PE\x00\x00"
    num_sections = 4
    opt_hdr_size = 240
    coff_hdr = struct.pack(
        "<HHIIIHH",
        0x8664,
        num_sections,
        0x67100300,
        0, 0,
        opt_hdr_size,
        0x0022
    )

    size_of_headers = 0x400
    size_of_image = 0x4000 + align(len(rsrc_raw), sect_align)
    opt_hdr = bytearray(240)
    struct.pack_into("<HBBIIIIIQIIHHHHHHIIIIHHQQQQII", opt_hdr, 0,
        0x020B,
        14, 0,
        len(text_file),
        len(rdata_file) + len(rsrc_file),
        0x1000,
        0x1000,
        0x1000,
        image_base,
        sect_align,
        file_align,
        6, 0,
        1, 5,                   # Image Version 1.5 (v1.0.5)
        6, 0,
        0,
        size_of_image,
        size_of_headers,
        0,
        2,                      # IMAGE_SUBSYSTEM_WINDOWS_GUI
        0x0140,
        0x100000, 0x1000,
        0x100000, 0x1000,
        0,
        16
    )

    struct.pack_into("<II", opt_hdr, 112 + 1 * 8, rdata_rva + 0x060, 60)
    struct.pack_into("<II", opt_hdr, 112 + 2 * 8, rsrc_rva, len(rsrc_raw))
    struct.pack_into("<II", opt_hdr, 112 + 12 * 8, rdata_rva, 0x030)

    def make_sect_hdr(name: bytes, virt_size: int, rva: int, raw_size: int, raw_ptr: int, chars: int) -> bytes:
        return struct.pack(
            "<8sIIIIIIHHI",
            name.ljust(8, b"\x00"),
            virt_size, rva, raw_size, raw_ptr,
            0, 0, 0, 0, chars
        )

    ptr_text = 0x400
    ptr_rdata = ptr_text + len(text_file)
    ptr_data = ptr_rdata + len(rdata_file)
    ptr_rsrc = ptr_data + len(data_file)

    sh_text = make_sect_hdr(b".text", len(text_raw), 0x1000, len(text_file), ptr_text, 0x60000020)
    sh_rdata = make_sect_hdr(b".rdata", len(rdata_raw), 0x2000, len(rdata_file), ptr_rdata, 0x40000040)
    sh_data = make_sect_hdr(b".data", 0x1000, 0x3000, len(data_file), ptr_data, 0xC0000040)
    sh_rsrc = make_sect_hdr(b".rsrc", len(rsrc_raw), 0x4000, len(rsrc_file), ptr_rsrc, 0x40000040)

    headers = pad_bytes(bytes(dos_header) + pe_sig + coff_hdr + bytes(opt_hdr) + sh_text + sh_rdata + sh_data + sh_rsrc, size_of_headers)
    exe_bytes = headers + text_file + rdata_file + data_file + rsrc_file

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(exe_bytes)
    print(f"Built v1.0.5 Windows EXE (8-DPI icons + PerMonitorV2 manifest): {out_path} ({len(exe_bytes):,} bytes)")

if __name__ == "__main__":
    build_voca_exe(os.path.abspath(os.path.join(SCRIPT_DIR, "..", "windows", "Voca.exe")))
