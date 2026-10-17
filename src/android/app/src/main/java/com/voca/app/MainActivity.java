/*
 * Reference Android shell. The shipped APK is assembled by scripts/build_apk_v103.py,
 * which hand-emits classes.dex for exactly these three methods; editing this file does
 * NOT change the APK. To build with the extra behaviour below, use the Gradle project
 * (src/android/app) against a real Android SDK and a device.
 *
 * Known gaps that the web layer works around instead (see the "导出内容" copy-out box
 * and "从粘贴内容恢复备份" in the data view):
 *   - WebChromeClient.onShowFileChooser is not implemented, so <input type=file> is inert.
 *   - No DownloadListener, so a[download] never writes a file.
 *   - No PrintManager path, so window.print() does nothing.
 *   - No edge-to-edge insets, so env(safe-area-inset-*) resolves to 0 on gesture-nav devices.
 */
package com.voca.app;

import android.app.Activity;
import android.os.Bundle;
import android.view.Window;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        super.onCreate(savedInstanceState);

        WebView wv = new WebView(this);
        WebSettings ws = wv.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setAllowFileAccess(true);
        ws.setDatabaseEnabled(true);

        wv.setWebViewClient(new WebViewClient());
        wv.setWebChromeClient(new WebChromeClient());
        wv.loadUrl("file:///android_asset/index.html");
        setContentView(wv);
        this.webView = wv;
    }

    @Override
    public void onBackPressed() {
        if (this.webView != null && this.webView.canGoBack()) {
            this.webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
