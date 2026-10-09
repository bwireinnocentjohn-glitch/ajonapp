/* __API_DEBUG_V1__ */
(function(){
  "use strict";
  if (window.__ajonApiDebug) return;
  window.__ajonApiDebug = true;

  function pill(msg, ok){
    var p = document.getElementById("ajonApiPill");
    if (!p) {
      p = document.createElement("div");
      p.id = "ajonApiPill";
      p.style.cssText = "position:fixed;bottom:8px;left:8px;right:8px;" +
        "background:rgba(0,0,0,.85);color:#fff;padding:8px 12px;" +
        "border-radius:10px;font-family:monospace;font-size:11px;" +
        "font-weight:700;z-index:99999;pointer-events:none;" +
        "text-align:center;line-height:1.4;white-space:pre-wrap;";
      document.body.appendChild(p);
    }
    p.style.borderLeft = "4px solid " + (ok ? "#00c853" : "#ff5252");
    p.textContent = msg;
    clearTimeout(p._t);
    p._t = setTimeout(function(){ if (p.parentNode) p.parentNode.removeChild(p); }, 20000);
  }

  var origFetch = window.fetch;
  window.fetch = function(url, opts){
    var u = String(url || "");
    if (u.indexOf("api.groq.com") === -1 && u.indexOf("generativelanguage.googleapis.com") === -1) {
      return origFetch.apply(this, arguments);
    }
    var tag = u.indexOf("groq") > -1 ? "GROQ" : "GEMINI";
    pill("[" + tag + "] requesting...", true);
    var started = Date.now();
    return origFetch.apply(this, arguments).then(function(r){
      var ms = Date.now() - started;
      if (r.ok) pill("[" + tag + "] OK " + r.status + " (" + ms + "ms)", true);
      else      pill("[" + tag + "] HTTP " + r.status + " (" + ms + "ms)", false);
      return r;
    }).catch(function(err){
      var ms = Date.now() - started;
      pill("[" + tag + "] FAILED (" + ms + "ms)\n" + (err && err.message ? err.message : String(err)), false);
      throw err;
    });
  };

  try { console.log("[API Debug] installed"); } catch(e){}
})();
