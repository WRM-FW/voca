#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voca v1.0.4 Windows native host builder.

Builds Voca.exe from src/windows/voca_host.c (Win32 + WebView2) with its icon and
PerMonitorV2 manifest compiled from src/windows/voca_host.rc, and stages the
WebView2Loader.dll that the host dlopen()s at runtime.

Why this replaced the old hand-assembled launcher: the pre-1.0.4 Voca.exe only ran
`msedge.exe --app=...`, and in that mode Chromium owns the taskbar button icon and
pins it to a 16x16 favicon before handing it to the shell - which is why the icon
looked soft at every display scale despite v1.0.3 shipping a correct 8-frame .ico.
A native window sets its own icon at the exact size the shell requests.
"""
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
WIN_DIR = os.path.join(ROOT, "src", "windows")
OUT_DIR = os.path.join(ROOT, "windows")
SDK_DIR = os.path.join(ROOT, "third_party", "webview2")
INC_DIR = os.path.join(SDK_DIR, "include")
LOADER_DLL = os.path.join(SDK_DIR, "runtimes", "win-x64", "WebView2Loader.dll")


def which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def run(cmd, **kw):
    print("   $", " ".join(str(c) for c in cmd))
    return subprocess.run(cmd, check=True, **kw)


def build(cc=None, windres=None):
    cc = cc or which("gcc", "x86_64-w64-mingw32-gcc", "cc")
    windres = windres or which("windres", "x86_64-w64-mingw32-windres", "windres.exe")
    if not cc or not windres:
        return None, "no gcc / windres found on PATH"
    for p, what in ((INC_DIR, "WebView2 SDK headers"), (LOADER_DLL, "WebView2Loader.dll")):
        if not os.path.exists(p):
            return None, f"missing {what} at {p}"

    obj = os.path.join(WIN_DIR, "voca_host_res.o")
    exe = os.path.join(OUT_DIR, "Voca.exe")
    os.makedirs(OUT_DIR, exist_ok=True)

    run([windres, "-i", os.path.join(WIN_DIR, "voca_host.rc"),
         "-o", obj, "--output-format=coff"])
    # -mwindows sets SUBSYSTEM_WINDOWS_GUI; without it Explorer shows a console window.
    run([cc, "-std=gnu11", "-O2", "-municode", "-mwindows", "-DUNICODE", "-D_UNICODE",
         # -isystem so the vendored WebView2.h does not spam warnings
         "-isystem", INC_DIR,
         os.path.join(WIN_DIR, "voca_host.c"), obj,
         "-o", exe,
         "-lole32", "-luuid", "-luser32", "-lgdi32", "-lshell32", "-lwinhttp",
         "-static", "-static-libgcc", "-static-libstdc++",
         "-Wl,-Bstatic", "-Wl,--no-insert-timestamp",
         "-s"],
        stderr=subprocess.STDOUT)
    if os.path.exists(obj):
        os.remove(obj)

    staged = os.path.join(OUT_DIR, "WebView2Loader.dll")
    shutil.copy2(LOADER_DLL, staged)
    return exe, staged


if __name__ == "__main__":
    print("[host] Building Voca v1.0.4 native WebView2 host ...")
    try:
        exe, dll = build()
    except subprocess.CalledProcessError as e:
        print("[host] compiler failed:", e)
        sys.exit(1)
    if not exe:
        print("[host] ABORT:", dll)
        print("       Install a MinGW-w64 gcc + windres, or vendor third_party/webview2.")
        sys.exit(1)
    print(f"[host] Voca.exe            {os.path.getsize(exe):,} bytes")
    print(f"[host] WebView2Loader.dll  {os.path.getsize(dll):,} bytes  (must ship beside Voca.exe)")
