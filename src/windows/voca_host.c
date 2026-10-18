/*
 * Voca v1.0.5 Windows host: native Win32 window + WebView2.
 *
 * Why this exists. Since v1.0.0 Voca.exe was only a launcher that opened
 * `msedge.exe --app=...`. In that mode the taskbar button icon is produced by
 * Chromium from the page favicon, and Chromium stores app-window favicons at a
 * hard 16x16 before handing them to the shell. At 125%/150%/200% display scaling
 * Windows then upscales that 16px bitmap, which is why the taskbar icon looked
 * soft in every release. Measured on a real 150% host: declaring 20/24/28/36/40
 * favicons, declaring only a 24px icon, declaring no icon at all, and setting
 * --app-user-model-id with a Start-Menu shortcut all produced the same
 * 16-upsampled bitmap. Nothing that ships inside index.html or Voca.exe's
 * .rsrc can change that.
 *
 * A native window owns its own icon instead. We load the exact pixel size the
 * shell asks for at this window's DPI straight out of the multi-frame voca.ico,
 * so no resampling happens at all.
 *
 * If the WebView2 runtime is unavailable we fall back to the old Edge --app
 * launch so the app still starts.
 */
#define WIN32_LEAN_AND_MEAN
#define _WIN32_WINNT 0x0A00
#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <objbase.h>
#include <wchar.h>
#include <stdio.h>
#include <windows.h>


/* initguid.h makes the DEFINE_GUID calls in WebView2.h emit definitions, not
   just declarations, so IsEqualGUID can compare against them. */
#include <initguid.h>
#include "WebView2.h"

typedef void *VocaDpiContext;
#ifndef DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
#define DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 ((VocaDpiContext)-4)
#endif

static const wchar_t *kAppUserModelId = L"Voca.Offline.WordTrainer.v1";
static const wchar_t *kWindowClassName = L"Voca.MainWindow";
static const wchar_t *kDictClassName   = L"Voca.DictWindow";

/* WordReference runs an Anubis JS proof-of-work gate. It passes for a top-level frame
   but never completes inside our iframe (third-party cookies), so dictionary lookups that
   need it open in this second, Voca-owned WebView2 window instead of the system browser. */
static HWND          g_dict_window   = NULL;
static ICoreWebView2Controller *g_dict_controller = NULL;
static ICoreWebView2           *g_dict_webview    = NULL;
static wchar_t       g_dict_uri[4096] = L"";

static HWND          g_main_window   = NULL;
static HINSTANCE     g_instance      = NULL;
static ICoreWebView2Controller *g_controller = NULL;
static ICoreWebView2           *g_webview    = NULL;
/* The runtime does not keep its own reference to the environment across the
   pending CreateCoreWebView2Controller call, so releasing it from the create
   callback crashes inside EmbeddedBrowserWebView.dll. Hold it for the app's
   lifetime and drop it on WM_DESTROY. */
static ICoreWebView2Environment *g_environment = NULL;
static HICON         g_icon_small = NULL, g_icon_big = NULL;
static HICON         g_dict_icon_small = NULL, g_dict_icon_big = NULL;
static wchar_t       g_log_path[MAX_PATH] = L"";
static wchar_t       g_crash_path[MAX_PATH] = L"";
static void Stage(const wchar_t *what, long code) {
    if (!g_log_path[0]) return;      /* routine tracing is opt-in only */
    FILE *f = _wfopen(g_log_path, L"a");
    if (!f) return;
    fwprintf(f, L"%s code=0x%08lX\n", what, (unsigned long)code);
    fclose(f);
}
static wchar_t       g_root_dir[MAX_PATH] = L"";   /* directory containing Voca.exe */
static wchar_t       g_html_path[MAX_PATH] = L"";  /* <root>\app\index.html          */

/* ---------------------------------------------------------------- helpers */

static LONG WINAPI CrashLog(struct _EXCEPTION_POINTERS *ep) {
    FILE *f = _wfopen(g_crash_path, L"a");
    if (f) {
        DWORD code = ep && ep->ExceptionRecord ? ep->ExceptionRecord->ExceptionCode : 0;
        void *addr = ep && ep->ExceptionRecord ? ep->ExceptionRecord->ExceptionAddress : NULL;
        MEMORY_BASIC_INFORMATION mbi;
        wchar_t mod[256] = L"?";
        if (addr && VirtualQuery(addr, &mbi, sizeof(mbi))) {
            GetModuleFileNameW((HMODULE)mbi.AllocationBase, mod, 256);
        }
        fwprintf(f, L"!! EXCEPTION code=0x%08lX addr=%p module=%s\n",
                 (unsigned long)code, addr, mod);
        fclose(f);
    }
    return EXCEPTION_CONTINUE_SEARCH;
}

static void GetRootDir(void) {
    wchar_t buf[MAX_PATH];
    DWORD n = GetModuleFileNameW(NULL, buf, MAX_PATH);
    if (n == 0 || n >= MAX_PATH) { wcscpy_s(buf, MAX_PATH, L"."); }
    for (long i = (long)n - 1; i >= 0; --i) {
        if (buf[i] == L'\\' || buf[i] == L'/') { buf[i] = 0; break; }
    }
    _snwprintf_s(g_root_dir, MAX_PATH, _TRUNCATE, L"%s", buf);
    _snwprintf_s(g_html_path, MAX_PATH, _TRUNCATE, L"%s\\app\\index.html", g_root_dir);
    _snwprintf_s(g_crash_path, MAX_PATH, _TRUNCATE, L"%s\\voca_crash.log", g_root_dir);
    /* A portable app must not drop a log file next to itself on every run. */
    wchar_t tr[8];
    DWORD tn = GetEnvironmentVariableW(L"VOCA_TRACE", tr, 8);
    if (tn && tn < 8) _snwprintf_s(g_log_path, MAX_PATH, _TRUNCATE, L"%s\\host_trace.log", g_root_dir);
    SetCurrentDirectoryW(g_root_dir);
}

static UINT WindowDpi(HWND hwnd) {
    HMODULE u = GetModuleHandleW(L"user32.dll");
    FARPROC p = u ? GetProcAddress(u, "GetDpiForWindow") : NULL;
    if (p) return (UINT)((UINT (WINAPI *)(HWND))p)(hwnd);
    HDC dc = GetDC(hwnd);
    UINT dpi = (UINT)GetDeviceCaps(dc, LOGPIXELSX);
    ReleaseDC(hwnd, dc);
    return dpi ? dpi : 96;
}

static int SmIconCx(UINT dpi) {
    HMODULE u = GetModuleHandleW(L"user32.dll");
    FARPROC p = u ? GetProcAddress(u, "GetSystemMetricsForDpi") : NULL;
    if (p) return (int)((int (WINAPI *)(int, UINT))p)(SM_CXSMICON, dpi);
    return GetSystemMetrics(SM_CXSMICON);
}

static int BigIconCx(UINT dpi) {
    HMODULE u = GetModuleHandleW(L"user32.dll");
    FARPROC p = u ? GetProcAddress(u, "GetSystemMetricsForDpi") : NULL;
    if (p) return (int)((int (WINAPI *)(int, UINT))p)(SM_CXICON, dpi);
    return GetSystemMetrics(SM_CXICON);
}

/* Load one frame out of the multi-size .ico at exactly the size the shell wants. */
static HICON LoadIcoFrame(const wchar_t *ico_path, int px) {
    HICON h = (HICON)LoadImageW(NULL, ico_path, IMAGE_ICON, px, px,
                                LR_LOADFROMFILE | LR_DEFAULTCOLOR);
    if (!h) h = (HICON)LoadImageW(NULL, ico_path, IMAGE_ICON, px, px, LR_LOADFROMFILE);
    return h;
}

/* Pixel width of an HICON, for the opt-in trace. */
static long IconPx(HICON h) {
    if (!h) return -1;
    ICONINFO ii;
    if (!GetIconInfo(h, &ii)) return -2;
    long w = 0;
    if (ii.hbmColor) {
        BITMAP bm;
        if (GetObjectW(ii.hbmColor, sizeof(bm), &bm)) w = bm.bmWidth;
        DeleteObject(ii.hbmColor);
    }
    if (ii.hbmMask) DeleteObject(ii.hbmMask);
    return w;
}

static void ApplyWindowIconsInto(HWND hwnd, HICON *slot_small, HICON *slot_big) {
    wchar_t ico[MAX_PATH];
    _snwprintf_s(ico, MAX_PATH, _TRUNCATE, L"%s\\app\\voca.ico", g_root_dir);
    if (GetFileAttributesW(ico) == INVALID_FILE_ATTRIBUTES)
        _snwprintf_s(ico, MAX_PATH, _TRUNCATE, L"%s\\voca.ico", g_root_dir);
    if (GetFileAttributesW(ico) == INVALID_FILE_ATTRIBUTES) return;

    UINT dpi = WindowDpi(hwnd);
    int small_px = SmIconCx(dpi);
    int big_px   = BigIconCx(dpi);

    HICON hs = LoadIcoFrame(ico, small_px);
    HICON hb = LoadIcoFrame(ico, big_px);
    if (!hs) hs = LoadIcoFrame(ico, 16);
    if (!hb) hb = LoadIcoFrame(ico, 32);
    if (!hb) hb = hs;
    if (!hs) hs = hb;

    /* Each window owns its own slots so a DPI change frees the right handles. */
    if (*slot_small && *slot_small != hs) DestroyIcon(*slot_small);
    if (*slot_big && *slot_big != hb && *slot_big != hs) DestroyIcon(*slot_big);
    *slot_small = hs;
    *slot_big   = hb;

    /* Setting ICON_SMALL2 after ICON_BIG makes DefWindowProc leave both slots on the small icon. */
    SendMessageW(hwnd, WM_SETICON, ICON_SMALL, (LPARAM)hs);
    SendMessageW(hwnd, WM_SETICON, ICON_SMALL2,(LPARAM)hs);
    SendMessageW(hwnd, WM_SETICON, ICON_BIG,   (LPARAM)hb);
    Stage(L"icons_set", (long)((small_px << 16) | (big_px & 0xFFFF)));
    Stage(L"icons_readback", (long)((IconPx((HICON)SendMessageW(hwnd, WM_GETICON, ICON_SMALL, 0)) << 8)
                                    | (IconPx((HICON)SendMessageW(hwnd, WM_GETICON, ICON_BIG, 0)) & 0xFF)));
}

static void ApplyWindowIcons(HWND hwnd) {
    if (hwnd == g_main_window) ApplyWindowIconsInto(hwnd, &g_icon_small, &g_icon_big);
    else ApplyWindowIconsInto(hwnd, &g_dict_icon_small, &g_dict_icon_big);
}

/* WebView2 needs a file URL; file:// paths must use forward slashes. */
static void HtmlFileUrl(wchar_t *out, size_t cap) {
    wchar_t tmp[MAX_PATH + 16];
    _snwprintf_s(tmp, MAX_PATH + 16, _TRUNCATE, L"%s", g_html_path);
    for (wchar_t *p = tmp; *p; ++p) if (*p == L'\\') *p = L'/';
    _snwprintf_s(out, cap, _TRUNCATE, L"file:///%s", tmp);
}

static BOOL DirExists(const wchar_t *p) {
    DWORD a = GetFileAttributesW(p);
    return (a != INVALID_FILE_ATTRIBUTES) && (a & FILE_ATTRIBUTE_DIRECTORY);
}

static void EnsureDirTree(const wchar_t *path) {
    wchar_t acc[MAX_PATH];
    wchar_t *p;
    if (path[0] == 0) return;
    wcscpy_s(acc, MAX_PATH, path);
    for (p = acc; *p; ++p) {
        if (*p == L'\\' || *p == L'/') {
            *p = 0;
            if (acc[0]) CreateDirectoryW(acc, NULL);
            *p = L'\\';
        }
    }
    CreateDirectoryW(acc, NULL);
}

static void CopyTree(const wchar_t *from, const wchar_t *to) {
    wchar_t pattern[MAX_PATH];
    WIN32_FIND_DATAW fd;
    HANDLE h;
    EnsureDirTree(to);
    _snwprintf_s(pattern, MAX_PATH, _TRUNCATE, L"%s\\*", from);
    h = FindFirstFileW(pattern, &fd);
    if (h == INVALID_HANDLE_VALUE) return;
    do {
        wchar_t sf[MAX_PATH], st[MAX_PATH];
        if (!wcscmp(fd.cFileName, L".") || !wcscmp(fd.cFileName, L"..")) continue;
        _snwprintf_s(sf, MAX_PATH, _TRUNCATE, L"%s\\%s", from, fd.cFileName);
        _snwprintf_s(st, MAX_PATH, _TRUNCATE, L"%s\\%s", to, fd.cFileName);
        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) CopyTree(sf, st);
        else {
            SetFileAttributesW(st, FILE_ATTRIBUTE_NORMAL);
            CopyFileW(sf, st, FALSE);
        }
    } while (FindNextFileW(h, &fd));
    FindClose(h);
}

/*
 * v1.0.3 kept its learning data in the Chromium profile written by
 *     msedge --app=... --user-data-dir=<root>\data\profile
 * that is, under data\profile\Default\Local Storage and ...\Default\IndexedDB.
 *
 * WebView2 never reads <UDF>\Default: it uses its own <UDF>\EBWebView\Default. Verified
 * on this host - pointing the native host straight at an old profile left localStorage
 * empty. So on the first native run we mirror the two web-storage trees into EBWebView
 * and keep using the same data\profile folder, which also means the documented data
 * location does not change between 1.0.3 and 1.0.4.
 */
static void MigrateLegacyWebStorage(const wchar_t *udf) {
    wchar_t done[MAX_PATH], eb_ls[MAX_PATH], legacy_ls[MAX_PATH];
    wchar_t legacy_idb[MAX_PATH], eb_idb[MAX_PATH];
    FILE *f;

    _snwprintf_s(done, MAX_PATH, _TRUNCATE, L"%s\\Voca.migrated", udf);
    if (GetFileAttributesW(done) != INVALID_FILE_ATTRIBUTES) return;

    _snwprintf_s(eb_ls,      MAX_PATH, _TRUNCATE, L"%s\\EBWebView\\Default\\Local Storage", udf);
    _snwprintf_s(legacy_ls,  MAX_PATH, _TRUNCATE, L"%s\\Default\\Local Storage", udf);
    _snwprintf_s(legacy_idb, MAX_PATH, _TRUNCATE, L"%s\\Default\\IndexedDB", udf);
    _snwprintf_s(eb_idb,     MAX_PATH, _TRUNCATE, L"%s\\EBWebView\\Default\\IndexedDB", udf);

    if (DirExists(legacy_ls) && !DirExists(eb_ls))   CopyTree(legacy_ls, eb_ls);
    if (DirExists(legacy_idb) && !DirExists(eb_idb)) CopyTree(legacy_idb, eb_idb);

    f = _wfopen(done, L"w");
    if (f) { fwprintf(f, L"voca 1.0.5: legacy web storage mirrored into EBWebView\n"); fclose(f); }
}

/* Always data\profile, so the path documented for users never changed. */
static void ChooseUserDataFolder(wchar_t *out, size_t cap) {
    wchar_t legacy[MAX_PATH];
    {
        /* Override used by the verification harness; unset in normal operation. */
        wchar_t ov[512];
        DWORD on = GetEnvironmentVariableW(L"VOCA_UDF", ov, 512);
        if (on && on < 512) {
            if (ov[0] == L'.') _snwprintf_s(out, cap, _TRUNCATE, L"%s\\%s", g_root_dir, ov + 2);
            else _snwprintf_s(out, cap, _TRUNCATE, L"%s", ov);
            return;
        }
    }
    _snwprintf_s(legacy, MAX_PATH, _TRUNCATE, L"%s\\data\\profile", g_root_dir);
    _snwprintf_s(out, cap, _TRUNCATE, L"%s", legacy);
}

/* ------------------------------------------------------- WebView2 callbacks */

static HRESULT STDMETHODCALLTYPE Env_QueryInterface(ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler *self,
                                                         REFIID riid, void **pp) {
    if (!pp) return E_POINTER;
    *pp = NULL;
    if (IsEqualGUID(riid, &IID_IUnknown) ||
        IsEqualGUID(riid, &IID_ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler)) {
        *pp = (void *)self;
        return S_OK;
    }
    return E_NOINTERFACE;
}
static ULONG STDMETHODCALLTYPE Env_AddRef(ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler *self) { (void)self; return 1; }
static ULONG STDMETHODCALLTYPE Env_Release(ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler *self) { (void)self; return 1; }

static HRESULT CreateWebView(ICoreWebView2Environment *env, HWND hwnd);

static HRESULT STDMETHODCALLTYPE Env_Invoke(ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler *self,
                                            HRESULT result, ICoreWebView2Environment *env) {
    (void)self;
    Stage(L"env-callback", (long)result);
    if (FAILED(result) || !env) {
        PostMessageW(g_main_window, WM_APP + 7, 0, (LPARAM)result);
        return result;
    }
    g_environment = env;
    env->lpVtbl->AddRef(env);
    HRESULT hr = CreateWebView(env, g_main_window);
    return hr;
}

static ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandlerVtbl env_vtbl = {
    Env_QueryInterface, Env_AddRef, Env_Release, Env_Invoke
};
static struct { ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandlerVtbl *lpVtbl; } g_env_handler = { &env_vtbl };

static HRESULT STDMETHODCALLTYPE Nw_QueryInterface(ICoreWebView2NewWindowRequestedEventHandler *self,
                                                   REFIID riid, void **pp) {
    if (!pp) return E_POINTER;
    *pp = NULL;
    if (IsEqualGUID(riid, &IID_IUnknown) ||
        IsEqualGUID(riid, &IID_ICoreWebView2NewWindowRequestedEventHandler)) {
        *pp = (void *)self;
        return S_OK;
    }
    return E_NOINTERFACE;
}
static ULONG STDMETHODCALLTYPE Nw_AddRef(ICoreWebView2NewWindowRequestedEventHandler *self) { (void)self; return 1; }
static ULONG STDMETHODCALLTYPE Nw_Release(ICoreWebView2NewWindowRequestedEventHandler *self) { (void)self; return 1; }
static HRESULT STDMETHODCALLTYPE Nw_Invoke(ICoreWebView2NewWindowRequestedEventHandler *self,
                                           ICoreWebView2 *sender,
                                           ICoreWebView2NewWindowRequestedEventArgs *args) {
    (void)self; (void)sender;
    LPWSTR uri = NULL;
    if (FAILED(args->lpVtbl->get_Uri(args, &uri)) || !uri) return S_OK;
    Stage(L"new-window", 0);
    /* Handled without supplying a CoreWebView2: we route the target into our own window. */
    args->lpVtbl->put_Handled(args, TRUE);
    PostMessageW(g_main_window, WM_APP + 8, 0, (LPARAM)uri);   /* ownership moves to the handler */
    return S_OK;
}
static ICoreWebView2NewWindowRequestedEventHandlerVtbl nw_vtbl = {
    Nw_QueryInterface, Nw_AddRef, Nw_Release, Nw_Invoke
};
static struct { ICoreWebView2NewWindowRequestedEventHandlerVtbl *lpVtbl; } g_new_window_handler = { &nw_vtbl };

static HRESULT STDMETHODCALLTYPE Ctl_QueryInterface(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self,
                                                         REFIID riid, void **pp) {
    if (!pp) return E_POINTER;
    *pp = NULL;
    if (IsEqualGUID(riid, &IID_IUnknown) ||
        IsEqualGUID(riid, &IID_ICoreWebView2CreateCoreWebView2ControllerCompletedHandler)) {
        *pp = (void *)self;
        return S_OK;
    }
    return E_NOINTERFACE;
}
static ULONG STDMETHODCALLTYPE Ctl_AddRef(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self) { (void)self; return 1; }
static ULONG STDMETHODCALLTYPE Ctl_Release(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self) { (void)self; return 1; }
static HRESULT STDMETHODCALLTYPE Ctl_Invoke(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self,
                                            HRESULT result, ICoreWebView2Controller *controller) {
    (void)self;
    if (FAILED(result) || !controller) {
        PostMessageW(g_main_window, WM_APP + 7, 1, (LPARAM)result);
        return result;
    }
    Stage(L"ctl-callback", (long)result);
    g_controller = controller;
    Stage(L"c1-addref", 0);
    g_controller->lpVtbl->AddRef(g_controller);
    RECT rc; GetClientRect(g_main_window, &rc);
    Stage(L"c2-bounds", (long)(rc.right - rc.left));
    g_controller->lpVtbl->put_Bounds(g_controller, rc);
    Stage(L"c3-getwebview", 0);
    g_controller->lpVtbl->get_CoreWebView2(g_controller, &g_webview);
    Stage(L"c4-got", (long)(g_webview != NULL));
    if (g_webview) {
        EventRegistrationToken tok;
        g_webview->lpVtbl->add_NewWindowRequested(
            g_webview, (ICoreWebView2NewWindowRequestedEventHandler*)&g_new_window_handler, &tok);
        Stage(L"nw-registered", 0);
        wchar_t url[MAX_PATH + 32];
        HtmlFileUrl(url, MAX_PATH + 32);
        Stage(L"c5-navigate", 0);
        g_webview->lpVtbl->Navigate(g_webview, url);
        Stage(L"c6-navigated", 0);
    }
    Stage(L"c7-show", 0);
    ShowWindow(g_main_window, SW_SHOWMAXIMIZED);
    UpdateWindow(g_main_window);
    Stage(L"c8-return", 0);
    return S_OK;
}
static ICoreWebView2CreateCoreWebView2ControllerCompletedHandlerVtbl ctl_vtbl = {
    Ctl_QueryInterface, Ctl_AddRef, Ctl_Release, Ctl_Invoke
};
static struct { ICoreWebView2CreateCoreWebView2ControllerCompletedHandlerVtbl *lpVtbl; } g_ctl_handler = { &ctl_vtbl };

static HRESULT CreateWebView(ICoreWebView2Environment *env, HWND hwnd) {
    return env->lpVtbl->CreateCoreWebView2Controller(
        env, hwnd, (ICoreWebView2CreateCoreWebView2ControllerCompletedHandler*)&g_ctl_handler);
}

/* -------------------------------------------------- secondary dictionary window */

static void DictWindow_PostAck(const wchar_t *uri);

static HRESULT STDMETHODCALLTYPE Dctl_QueryInterface(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self,
                                                     REFIID riid, void **pp) {
    if (!pp) return E_POINTER;
    *pp = NULL;
    if (IsEqualGUID(riid, &IID_IUnknown) ||
        IsEqualGUID(riid, &IID_ICoreWebView2CreateCoreWebView2ControllerCompletedHandler)) {
        *pp = (void *)self;
        return S_OK;
    }
    return E_NOINTERFACE;
}
static ULONG STDMETHODCALLTYPE Dctl_AddRef(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self) { (void)self; return 1; }
static ULONG STDMETHODCALLTYPE Dctl_Release(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self) { (void)self; return 1; }
static HRESULT STDMETHODCALLTYPE Dctl_Invoke(ICoreWebView2CreateCoreWebView2ControllerCompletedHandler *self,
                                             HRESULT result, ICoreWebView2Controller *controller) {
    (void)self;
    Stage(L"dict-ctl", (long)result);
    if (FAILED(result) || !controller || !g_dict_window) return S_OK;
    g_dict_controller = controller;
    controller->lpVtbl->AddRef(controller);
    RECT rc; GetClientRect(g_dict_window, &rc);
    controller->lpVtbl->put_Bounds(controller, rc);
    g_dict_controller->lpVtbl->get_CoreWebView2(g_dict_controller, &g_dict_webview);
    if (g_dict_webview && g_dict_uri[0]) {
        g_dict_webview->lpVtbl->Navigate(g_dict_webview, g_dict_uri);
        DictWindow_PostAck(g_dict_uri);
        g_dict_uri[0] = 0;
    }
    return S_OK;
}
static ICoreWebView2CreateCoreWebView2ControllerCompletedHandlerVtbl dctl_vtbl = {
    Dctl_QueryInterface, Dctl_AddRef, Dctl_Release, Dctl_Invoke
};
static struct { ICoreWebView2CreateCoreWebView2ControllerCompletedHandlerVtbl *lpVtbl; } g_dict_ctl_handler = { &dctl_vtbl };

static LRESULT CALLBACK DictWndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {
    case WM_CREATE:
        g_dict_window = hwnd;
        ApplyWindowIcons(hwnd);
        return 0;
    case WM_SIZE:
        if (g_dict_controller) { RECT rc; GetClientRect(hwnd, &rc); g_dict_controller->lpVtbl->put_Bounds(g_dict_controller, rc); }
        return 0;
    case WM_DPICHANGED: {
        RECT *r = (RECT *)lp;
        SetWindowPos(hwnd, NULL, r->left, r->top, r->right - r->left, r->bottom - r->top, SWP_NOZORDER | SWP_NOACTIVATE);
        ApplyWindowIcons(hwnd);
        return 0;
    }
    case WM_DESTROY:
        if (g_dict_webview)   { g_dict_webview->lpVtbl->Release(g_dict_webview);     g_dict_webview = NULL; }
        if (g_dict_controller) { g_dict_controller->lpVtbl->Release(g_dict_controller); g_dict_controller = NULL; }
        if (g_dict_icon_small) { DestroyIcon(g_dict_icon_small); g_dict_icon_small = NULL; }
        if (g_dict_icon_big && g_dict_icon_big != g_dict_icon_small) { DestroyIcon(g_dict_icon_big); }
        g_dict_icon_big = NULL;
        g_dict_window = NULL;
        return 0;
    }
    return DefWindowProcW(hwnd, msg, wp, lp);
}

static void DictWindow_PostAck(const wchar_t *uri) {
    if (!g_webview) return;
    wchar_t json[4300];
    wchar_t esc[4096];
    size_t j = 0;
    for (size_t i = 0; uri[i] && j + 2 < 4096; ++i) {
        if (uri[i] == L'"' || uri[i] == L'\\') esc[j++] = L'\\';
        esc[j++] = uri[i];
    }
    esc[j] = 0;
    _snwprintf_s(json, 4300, _TRUNCATE, L"{\"voca\":\"dict-window\",\"uri\":\"%s\"}", esc);
    g_webview->lpVtbl->PostWebMessageAsJson(g_webview, json);
}

static void DictWindow_Show(const wchar_t *uri) {
    if (!uri || !uri[0]) return;
    UINT dpi = g_main_window ? WindowDpi(g_main_window) : 96;
    if (!g_dict_window) {
        int w = MulDiv(1100, dpi, 96), h = MulDiv(820, dpi, 96);
        g_dict_window = CreateWindowExW(0, kDictClassName,
            L"Voca · 在线词典窗口 (WordReference)", WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT, CW_USEDEFAULT, w, h, NULL, NULL, g_instance, NULL);
        if (!g_dict_window) return;
    }
    ShowWindow(g_dict_window, SW_SHOWNORMAL);
    UpdateWindow(g_dict_window);
    SetForegroundWindow(g_dict_window);
    if (g_dict_webview) {
        g_dict_webview->lpVtbl->Navigate(g_dict_webview, uri);
        DictWindow_PostAck(uri);
        return;
    }
    wcscpy_s(g_dict_uri, 4096, uri);
    if (g_environment && !g_dict_controller)
        g_environment->lpVtbl->CreateCoreWebView2Controller(
            g_environment, g_dict_window,
            (ICoreWebView2CreateCoreWebView2ControllerCompletedHandler*)&g_dict_ctl_handler);
}


static HRESULT StartWebView2(HWND hwnd) {
    HMODULE loader = LoadLibraryExW(L"WebView2Loader.dll", NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!loader) loader = LoadLibraryW(L"WebView2Loader.dll");
    if (!loader) return HRESULT_FROM_WIN32(GetLastError());
    FARPROC fn = GetProcAddress(loader, "CreateCoreWebView2EnvironmentWithOptions");
    if (!fn) { FreeLibrary(loader); return HRESULT_FROM_WIN32(ERROR_PROC_NOT_FOUND); }
    wchar_t udf[MAX_PATH];
    ChooseUserDataFolder(udf, MAX_PATH);
    EnsureDirTree(udf);
    MigrateLegacyWebStorage(udf);
    Stage(L"env-call", 0);
    return ((HRESULT (WINAPI *)(LPCWSTR, LPCWSTR, ICoreWebView2EnvironmentOptions*,
                                ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler*))fn)(
        NULL, udf, NULL, (ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler*)&g_env_handler);
}

/* ------------------------------------------------------- old-shell fallback */

static void FallbackToEdgeShell(HRESULT why) {
    wchar_t args[4096], url[MAX_PATH + 32];
    HtmlFileUrl(url, MAX_PATH + 32);
    wchar_t udf[MAX_PATH];
    ChooseUserDataFolder(udf, MAX_PATH);
    _snwprintf_s(args, 4096, _TRUNCATE,
        L"--app=\"%s\" --start-maximized --high-dpi-support=1 --user-data-dir=\"%s\" "
        L"--no-first-run --no-default-browser-check --disable-extensions --disable-sync",
        g_html_path, udf);
    HINSTANCE r = ShellExecuteW(NULL, L"open", L"msedge.exe", args, g_root_dir, SW_SHOWMAXIMIZED);
    if ((INT_PTR)r <= 32) {
        r = ShellExecuteW(NULL, L"open", L"chrome.exe", args, g_root_dir, SW_SHOWMAXIMIZED);
        if ((INT_PTR)r <= 32)
            ShellExecuteW(NULL, L"open", g_html_path, NULL, g_root_dir, SW_SHOWNORMAL);
    }
    wchar_t msg[512];
    _snwprintf_s(msg, 512, _TRUNCATE,
        L"Voca 无法启动内置的 WebView2 界面（错误 0x%08lX），\n已改用系统 Edge/Chrome 窗口打开。\n\n"
        L"注意：在外部浏览器窗口模式下，任务栏图标会由浏览器接管并显得偏软；\n"
        L"安装 Microsoft Edge WebView2 Runtime 后可恢复原生窗口与清晰图标。",
        (unsigned long)why);
    MessageBoxW(NULL, msg, L"Voca - 已使用兼容模式启动", MB_OK | MB_ICONWARNING);
}

/* ------------------------------------------------------------- window proc */

static LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp) {
    switch (msg) {
    case WM_CREATE:
        g_main_window = hwnd;
        return 0;
    case WM_APP + 7:
        FallbackToEdgeShell((HRESULT)(LONG_PTR)lp);
        DestroyWindow(hwnd);
        return 0;
    case WM_APP + 8:
        DictWindow_Show((const wchar_t *)lp);
        CoTaskMemFree((void *)lp);
        return 0;
    case WM_SIZE:
        if (g_controller) {
            RECT rc; GetClientRect(hwnd, &rc);
            g_controller->lpVtbl->put_Bounds(g_controller, rc);
        }
        return 0;
    case WM_DPICHANGED: {
        RECT *r = (RECT *)lp;
        SetWindowPos(hwnd, NULL, r->left, r->top, r->right - r->left, r->bottom - r->top,
                     SWP_NOZORDER | SWP_NOACTIVATE);
        ApplyWindowIcons(hwnd);   /* re-pick the icon frame for the new scale */
        return 0;
    }
    case WM_SETFOCUS:
        if (g_controller) g_controller->lpVtbl->put_IsVisible(g_controller, TRUE);
        return 0;
    case WM_CLOSE:
        DestroyWindow(hwnd);
        return 0;
    case WM_DESTROY:
        if (g_dict_window) { DestroyWindow(g_dict_window); g_dict_window = NULL; }
        if (g_webview)      { g_webview->lpVtbl->Release(g_webview); g_webview = NULL; }
        if (g_environment)  { g_environment->lpVtbl->Release(g_environment); g_environment = NULL; }
        if (g_controller)   { g_controller->lpVtbl->Release(g_controller); g_controller = NULL; }
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, msg, wp, lp);
}

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrev, PWSTR cmd, int show) {
    (void)hPrev; (void)cmd; (void)show;
    g_instance = hInstance;

    HMODULE u = GetModuleHandleW(L"user32.dll");
    FARPROC dpi_ctx = u ? GetProcAddress(u, "SetProcessDpiAwarenessContext") : NULL;
    if (dpi_ctx)
        ((BOOL (WINAPI *)(VocaDpiContext))dpi_ctx)(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    else
        SetProcessDPIAware();

    AddVectoredExceptionHandler(1, CrashLog);
    SetCurrentProcessExplicitAppUserModelID(kAppUserModelId);
    GetRootDir();
    Stage(L"boot", 0);
    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);


    WNDCLASSEXW wc = {0};
    wc.cbSize        = sizeof(wc);
    wc.style         = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc   = WndProc;
    wc.hInstance     = hInstance;
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = kWindowClassName;
    {
        wchar_t ico[MAX_PATH];
        _snwprintf_s(ico, MAX_PATH, _TRUNCATE, L"%s\\app\\voca.ico", g_root_dir);
        if (GetFileAttributesW(ico) == INVALID_FILE_ATTRIBUTES)
            _snwprintf_s(ico, MAX_PATH, _TRUNCATE, L"%s\\voca.ico", g_root_dir);
        if (GetFileAttributesW(ico) != INVALID_FILE_ATTRIBUTES) {
            wc.hIcon    = LoadIcoFrame(ico, GetSystemMetrics(SM_CXICON));
            wc.hIconSm  = LoadIcoFrame(ico, GetSystemMetrics(SM_CXSMICON));
            if (!wc.hIcon) wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
        } else {
            wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
        }
    }
    RegisterClassExW(&wc);

    WNDCLASSEXW dc = wc;
    dc.lpfnWndProc   = DictWndProc;
    dc.lpszClassName = kDictClassName;
    RegisterClassExW(&dc);

    UINT dpi0 = 96;
    {
        HMODULE sh = LoadLibraryW(L"shcore.dll");
        FARPROC gf = sh ? GetProcAddress(sh, "GetDpiForSystem") : NULL;
        if (gf) dpi0 = (UINT)((UINT (WINAPI *)(void))gf)();
        if (!dpi0) dpi0 = 96;
    }
    int w = MulDiv(1280, dpi0, 96), h = MulDiv(860, dpi0, 96);

    g_main_window = CreateWindowExW(
        0, kWindowClassName,
        L"Voca v1.0.5 — 离线艾宾浩斯背单词工坊 (Windows & Android)",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, w, h,
        NULL, NULL, hInstance, NULL);
    if (!g_main_window) return 2;
    /* Class icons are owned by the window class for the process lifetime, so they are
       deliberately not destroyed here. The per-window icons must be applied only after
       CreateWindowExW has returned: a WM_SETICON sent from inside WM_CREATE is undone by
       the class-icon initialisation that finishes the create, which is exactly how the
       48px taskbar/Alt-Tab icon went missing. */
    ApplyWindowIcons(g_main_window);

    Stage(L"window-created", 0);
    HRESULT start = StartWebView2(g_main_window);
    Stage(L"env-create-returned", (long)start);
    if (FAILED(start)) {
        FallbackToEdgeShell(start);
        return 0;
    }

    /* The controller callback reveals the window; do not hide it afterwards. */
    MSG m;
    while (GetMessageW(&m, NULL, 0, 0)) { TranslateMessage(&m); DispatchMessageW(&m); }
    CoUninitialize();
    return (int)m.wParam;
}
