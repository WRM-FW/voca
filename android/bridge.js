// Voca Android bridge polyfill — injected by MainActivity ahead of the app.
// Reproduces the WebView2 `window.chrome.webview` channel the frontend uses
// on Windows, backed by the native VocaAndroidBridge JavascriptInterface,
// and routes blob: downloads to native storage (WebView cannot save them).
(function () {
  if (window.chrome && window.chrome.webview) return;
  var listeners = [];
  window.__VOCA_DELIVER__ = function (json) {
    var data;
    try { data = JSON.parse(json); } catch (e) { data = json; }
    var ev = { data: data };
    listeners.slice().forEach(function (fn) { try { fn(ev); } catch (e) {} });
  };
  window.chrome = {
    webview: {
      postMessage: function (msg) {
        var s;
        try { s = (typeof msg === "string") ? msg : JSON.stringify(msg); } catch (e) { return; }
        if (window.VocaAndroidBridge && VocaAndroidBridge.postMessage) {
          VocaAndroidBridge.postMessage(s);
        }
      },
      addEventListener: function (type, fn) {
        if (type === "message" && typeof fn === "function") listeners.push(fn);
      },
      removeEventListener: function (type, fn) {
        var i = listeners.indexOf(fn);
        if (i >= 0) listeners.splice(i, 1);
      }
    }
  };

  var blobs = {};
  var origCreate = URL.createObjectURL.bind(URL);
  URL.createObjectURL = function (blob) {
    var u = origCreate(blob);
    try { blobs[u] = blob; } catch (e) {}
    return u;
  };
  // The app exports by clicking a DETACHED anchor, whose click never
  // bubbles to the document — intercept the prototype method as well.
  var origAnchorClick = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    var href = this.getAttribute && (this.getAttribute("href") || "");
    if (this.hasAttribute && this.hasAttribute("download") && href.indexOf("blob:") === 0 && blobs[href]) {
      saveBlob(this.getAttribute("download") || "voca-export", blobs[href]);
      return;
    }
    return origAnchorClick.apply(this, arguments);
  };
  function saveBlob(name, blob) {
    var reader = new FileReader();
    reader.onload = function () {
      var res = String(reader.result || "");
      var b64 = res.substring(res.indexOf(",") + 1);
      if (window.VocaAndroidBridge && VocaAndroidBridge.saveFile) {
        VocaAndroidBridge.saveFile(name, blob.type || "application/octet-stream", b64);
      }
    };
    reader.readAsDataURL(blob);
  }

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[download]") : null;
    if (!a) return;
    var href = a.getAttribute("href") || "";
    if (href.indexOf("blob:") !== 0) return;
    var blob = blobs[href];
    if (!blob) return;
    e.preventDefault();
    e.stopPropagation();
    saveBlob(a.getAttribute("download") || "voca-export", blob);
  }, true);
})();
