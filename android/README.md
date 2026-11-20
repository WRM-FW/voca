# Voca for Android

WebView host for the Voca single-file web app, mirroring the Windows host:
the page runs with its built-in mobile shell (`html.ui-mobile`: bottom tab
bar, touch targets, gesture hints), and `bridge.js` — injected ahead of the
app by `MainActivity` — reproduces the `window.chrome.webview` channel so
the WordReference overlay/fetch protocol works exactly as on Windows.
Blob downloads are saved to the system Downloads folder; file imports use
the system file picker. App data (localStorage) stays on the device.

## Build

```bash
# one-time: JDK 17 + Android SDK (platforms;android-34, build-tools;34.0.0)
bash build_apk.sh            # writes ~/workspace/voca-v106/release/Voca_v1.1.2.apk
```

The signing keystore lives outside the repo
(`~/workspace/voca-v106/android-signing/voca.keystore`, created on first
build). Keep it: a different key cannot update an installed copy in place.

## Install

Copy the APK to the phone and open it (allow "install unknown apps" for the
file manager once). Android 10+ (minSdk 29). No account, no network needed
except the online dictionary.
