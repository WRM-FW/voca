/*
 * Voca v1.0.3 Windows Native Desktop Launcher (Win32 API / Unicode)
 * Launches Voca maximized / full-screen by default with PerMonitorV2 High-DPI support
 * and 8-frame Win32 DIB/PNG icon resources.
 */
#include <windows.h>
#include <shellapi.h>

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow) {
    WCHAR dirBuf[512];
    WCHAR htmlBuf[512];
    WCHAR argsBuf[1024];

    DWORD len = GetModuleFileNameW(NULL, dirBuf, 500);
    for (int i = (int)len - 1; i >= 0; i--) {
        if (dirBuf[i] == L'\\' || dirBuf[i] == L'/') {
            dirBuf[i] = L'\0';
            break;
        }
    }
    SetCurrentDirectoryW(dirBuf);

    wsprintfW(htmlBuf, L"%s\\app\\index.html", dirBuf);
    wsprintfW(argsBuf, L"--app=\"%s\" --start-maximized --high-dpi-support=1 --user-data-dir=\"%s\\data\\profile\" --no-first-run --no-default-browser-check --disable-extensions --disable-sync", htmlBuf, dirBuf);

    HINSTANCE res = ShellExecuteW(NULL, L"open", L"msedge.exe", argsBuf, dirBuf, SW_SHOWMAXIMIZED);
    if ((INT_PTR)res <= 32) {
        res = ShellExecuteW(NULL, L"open", L"chrome.exe", argsBuf, dirBuf, SW_SHOWMAXIMIZED);
        if ((INT_PTR)res <= 32) {
            ShellExecuteW(NULL, L"open", htmlBuf, NULL, dirBuf, SW_SHOWMAXIMIZED);
        }
    }
    ExitProcess(0);
    return 0;
}
