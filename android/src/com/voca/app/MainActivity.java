package com.voca.app;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Voca Android host (v1.1.2).
 *
 * Mirrors the Windows WebView2 host for the single-file Voca web app:
 *  - serves assets/index.html with bridge.js injected ahead of the app, so
 *    the page sees the same window.chrome.webview channel as on Windows;
 *  - dict-fetch: hidden WebView scrapes the page, posts dict-fetch-result;
 *  - dict-show / dict-rect / dict-hide: a second WebView overlaid exactly on
 *    the rect the page reports (CSS px x dpr = physical px), dict-shown ack;
 *  - window.open (dictionary window): full-screen overlay WebView + close
 *    bar, acked with {voca:"dict-window"};
 *  - blob: downloads are handed over by bridge.js and saved to Downloads.
 */
public class MainActivity extends Activity {

    private static final int REQ_FILE_CHOOSER = 7101;

    private FrameLayout root;
    private WebView web;
    private WebView overlay;
    private LinearLayout overlayBar;
    private WebView fetchWeb;
    private Handler ui;
    private ValueCallback<Uri[]> fileCallback;
    private String bridgeJs;
    private boolean overlayForDictWindow;
    private boolean dictShownAckPending;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        ui = new Handler(Looper.getMainLooper());
        bridgeJs = readAssetText("bridge.js");

        root = new FrameLayout(this);
        web = new WebView(this);
        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        WebSettings ws = web.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);
        ws.setDatabaseEnabled(true);
        ws.setAllowFileAccess(true);
        ws.setSupportMultipleWindows(true);
        ws.setJavaScriptCanOpenWindowsAutomatically(true);
        ws.setMediaPlaybackRequiresUserGesture(false);
        ws.setTextZoom(100);
        web.addJavascriptInterface(new Bridge(), "VocaAndroidBridge");
        web.setWebViewClient(new MainClient());
        web.setWebChromeClient(new MainChrome());
        web.loadUrl("file:///android_asset/index.html");
    }

    // ------------------------------------------------------------------ util

    private String readAssetText(String name) {
        try (InputStream in = getAssets().open(name)) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return out.toString("UTF-8");
        } catch (Exception e) {
            return "";
        }
    }

    private void deliver(String json) {
        ui.post(() -> web.evaluateJavascript(
                "window.__VOCA_DELIVER__ && window.__VOCA_DELIVER__("
                        + JSONObject.quote(json) + ")", null));
    }

    private void toast(String msg) {
        ui.post(() -> Toast.makeText(this, msg, Toast.LENGTH_SHORT).show());
    }

    // --------------------------------------------------------------- overlay

    private WebView ensureOverlay() {
        if (overlay != null) return overlay;
        overlay = new WebView(this);
        WebSettings s = overlay.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        overlay.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView v, String url) {
                if (dictShownAckPending) {
                    dictShownAckPending = false;
                    ui.postDelayed(() -> deliver("{\"voca\":\"dict-shown\",\"ok\":true}"), 350);
                }
            }

            @Override
            public void onReceivedError(WebView v, WebResourceRequest req,
                                        android.webkit.WebResourceError err) {
                if (req.isForMainFrame() && dictShownAckPending) {
                    dictShownAckPending = false;
                    deliver("{\"voca\":\"dict-shown\",\"ok\":false}");
                }
            }
        });
        overlay.setVisibility(View.GONE);
        root.addView(overlay, new FrameLayout.LayoutParams(0, 0));

        overlayBar = new LinearLayout(this);
        overlayBar.setGravity(Gravity.END | Gravity.CENTER_VERTICAL);
        overlayBar.setBackgroundColor(Color.argb(235, 24, 28, 32));
        Button close = new Button(this);
        close.setText("✕ 关闭词典");
        close.setTextColor(Color.WHITE);
        close.setBackgroundColor(Color.TRANSPARENT);
        close.setOnClickListener(v -> hideOverlay(true));
        overlayBar.addView(close);
        overlayBar.setVisibility(View.GONE);
        FrameLayout.LayoutParams bp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(48));
        bp.gravity = Gravity.TOP;
        root.addView(overlayBar, bp);
        return overlay;
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private void placeOverlay(double x, double y, double w, double h, double dpr) {
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                (int) Math.round(w * dpr), (int) Math.round(h * dpr));
        lp.leftMargin = (int) Math.round(x * dpr);
        lp.topMargin = (int) Math.round(y * dpr);
        overlay.setLayoutParams(lp);
    }

    private void hideOverlay(boolean fromUser) {
        if (overlay != null) {
            overlay.setVisibility(View.GONE);
            overlay.loadUrl("about:blank");
        }
        if (overlayBar != null) overlayBar.setVisibility(View.GONE);
        if (fromUser && overlayForDictWindow) {
            // Nothing to ack on close; the page polls the open ack only.
        }
        overlayForDictWindow = false;
        dictShownAckPending = false;
    }

    /** Full-screen dictionary window for window.open (dict-window flow). */
    private void openDictWindow(String url) {
        ensureOverlay();
        overlayForDictWindow = true;
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
        lp.topMargin = dp(48);
        overlay.setLayoutParams(lp);
        overlayBar.setVisibility(View.VISIBLE);
        overlay.setVisibility(View.VISIBLE);
        overlay.loadUrl(url);
        deliver("{\"voca\":\"dict-window\"}");
    }

    // ---------------------------------------------------------------- fetch

    private void doDictFetch(int id, String url) {
        ui.post(() -> {
            if (fetchWeb == null) {
                fetchWeb = new WebView(this);
                WebSettings s = fetchWeb.getSettings();
                s.setJavaScriptEnabled(true);
                s.setDomStorageEnabled(true);
            }
            final boolean[] done = {false};
            fetchWeb.setWebViewClient(new WebViewClient() {
                @Override
                public void onPageFinished(WebView v, String u) {
                    ui.postDelayed(() -> {
                        if (done[0]) return;
                        v.evaluateJavascript("document.documentElement.outerHTML", val -> {
                            if (done[0]) return;
                            done[0] = true;
                            try {
                                String html = (val == null || "null".equals(val))
                                        ? "" : new org.json.JSONArray("[" + val + "]").getString(0);
                                JSONObject r = new JSONObject();
                                r.put("voca", "dict-fetch-result");
                                r.put("id", id);
                                r.put("ok", html.length() > 0);
                                r.put("html", html);
                                deliver(r.toString());
                            } catch (Exception e) {
                                deliver("{\"voca\":\"dict-fetch-result\",\"id\":" + id + ",\"ok\":false}");
                            }
                        });
                    }, 1200);
                }
            });
            fetchWeb.loadUrl(url);
            ui.postDelayed(() -> {
                if (!done[0]) {
                    done[0] = true;
                    deliver("{\"voca\":\"dict-fetch-result\",\"id\":" + id + ",\"ok\":false,\"error\":\"timeout\"}");
                }
            }, 20000);
        });
    }

    // ------------------------------------------------------------ downloads

    private void saveDownload(String name, String mime, String base64) {
        new Thread(() -> {
            try {
                byte[] data = Base64.decode(base64, Base64.DEFAULT);
                String safe = (name == null || name.trim().isEmpty()) ? "voca-export" : name.trim();
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentValues cv = new ContentValues();
                    cv.put(MediaStore.Downloads.DISPLAY_NAME, safe);
                    if (mime != null && !mime.isEmpty()) cv.put(MediaStore.Downloads.MIME_TYPE, mime);
                    cv.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                    cv.put(MediaStore.Downloads.IS_PENDING, 1);
                    ContentResolver cr = getContentResolver();
                    Uri uri = cr.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                    if (uri == null) throw new Exception("insert failed");
                    try (OutputStream os = cr.openOutputStream(uri)) {
                        os.write(data);
                    }
                    cv.clear();
                    cv.put(MediaStore.Downloads.IS_PENDING, 0);
                    cr.update(uri, cv, null, null);
                } else {
                    java.io.File dir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
                    java.io.File f = new java.io.File(dir, safe);
                    try (java.io.FileOutputStream os = new java.io.FileOutputStream(f)) {
                        os.write(data);
                    }
                }
                toast("已保存到下载目录：" + safe);
            } catch (Exception e) {
                toast("保存失败：" + e.getMessage());
            }
        }).start();
    }

    // --------------------------------------------------------------- bridge

    public class Bridge {
        @JavascriptInterface
        public void postMessage(String json) {
            try {
                JSONObject m = new JSONObject(json);
                String kind = m.optString("voca", "");
                switch (kind) {
                    case "dict-fetch":
                        doDictFetch(m.optInt("id", 0), m.optString("url", ""));
                        break;
                    case "dict-show": {
                        String url = m.optString("url", "");
                        double x = m.optDouble("x", 0), y = m.optDouble("y", 0);
                        double w = m.optDouble("w", 0), h = m.optDouble("h", 0);
                        double dpr = m.optDouble("dpr", 1);
                        ui.post(() -> {
                            ensureOverlay();
                            overlayForDictWindow = false;
                            overlayBar.setVisibility(View.GONE);
                            placeOverlay(x, y, w, h, dpr);
                            dictShownAckPending = true;
                            overlay.setVisibility(View.VISIBLE);
                            overlay.loadUrl(url);
                        });
                        break;
                    }
                    case "dict-rect": {
                        double x = m.optDouble("x", 0), y = m.optDouble("y", 0);
                        double w = m.optDouble("w", 0), h = m.optDouble("h", 0);
                        double dpr = m.optDouble("dpr", 1);
                        ui.post(() -> {
                            if (overlay != null && overlay.getVisibility() == View.VISIBLE
                                    && !overlayForDictWindow) {
                                placeOverlay(x, y, w, h, dpr);
                            }
                        });
                        break;
                    }
                    case "dict-hide":
                        ui.post(() -> hideOverlay(false));
                        break;
                    default:
                        break;
                }
            } catch (Exception ignored) {
            }
        }

        @JavascriptInterface
        public void saveFile(String name, String mime, String base64) {
            saveDownload(name, mime, base64);
        }
    }

    // -------------------------------------------------------------- clients

    private class MainClient extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest req) {
            String url = req.getUrl().toString();
            if (url.endsWith("/index.html") || url.equals("file:///android_asset/")) {
                try {
                    String html = readAssetText("index.html");
                    int headEnd = html.indexOf('>', html.indexOf("<head")) + 1;
                    String patched = html.substring(0, headEnd)
                            + "<script>" + bridgeJs + "</script>"
                            + html.substring(headEnd);
                    return new WebResourceResponse("text/html", "UTF-8",
                            new ByteArrayInputStream(patched.getBytes(StandardCharsets.UTF_8)));
                } catch (Exception ignored) {
                }
            }
            return super.shouldInterceptRequest(v, req);
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest req) {
            String url = req.getUrl().toString();
            if (url.startsWith("http://") || url.startsWith("https://")) {
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
                } catch (Exception ignored) {
                }
                return true;
            }
            return false;
        }
    }

    private class MainChrome extends WebChromeClient {
        @Override
        public boolean onCreateWindow(WebView v, boolean isDialog, boolean isUserGesture,
                                      android.os.Message resultMsg) {
            WebView popup = new WebView(MainActivity.this);
            popup.getSettings().setJavaScriptEnabled(true);
            WebView.WebViewTransport transport = (WebView.WebViewTransport) resultMsg.obj;
            transport.setWebView(popup);
            resultMsg.sendToTarget();
            popup.setWebViewClient(new WebViewClient() {
                @Override
                public boolean shouldOverrideUrlLoading(WebView pv, WebResourceRequest req) {
                    openDictWindow(req.getUrl().toString());
                    pv.destroy();
                    return true;
                }
            });
            return true;
        }

        @Override
        public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> callback,
                                         FileChooserParams params) {
            if (fileCallback != null) fileCallback.onReceiveValue(null);
            fileCallback = callback;
            try {
                Intent intent = params.createIntent();
                startActivityForResult(intent, REQ_FILE_CHOOSER);
            } catch (Exception e) {
                fileCallback = null;
                return false;
            }
            return true;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_FILE_CHOOSER && fileCallback != null) {
            Uri[] results = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null) {
                results = new Uri[]{data.getData()};
            }
            fileCallback.onReceiveValue(results);
            fileCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (overlay != null && overlay.getVisibility() == View.VISIBLE) {
            boolean wasDictWindow = overlayForDictWindow;
            hideOverlay(true);
            if (!wasDictWindow) {
                web.evaluateJavascript(
                        "var b=document.getElementById('modalBtnCloseDict'); if(b) b.click();", null);
            }
            return;
        }
        if (web.canGoBack()) {
            web.goBack();
            return;
        }
        super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        if (web != null) web.destroy();
        if (overlay != null) overlay.destroy();
        if (fetchWeb != null) fetchWeb.destroy();
        super.onDestroy();
    }
}
