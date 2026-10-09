/* __EXPERT_ENHANCEMENTS_V1__ */
(function(){
  "use strict";
  if (window.__ajonEnhV3) return;
  window.__ajonEnhV3 = true;

  function byId(id){ return document.getElementById(id); }
  function $(s){ return document.querySelector(s); }

  function toast(msg, ms){
    var t = byId("ajonEnhToast");
    if (!t){
      t = document.createElement("div");
      t.id = "ajonEnhToast";
      t.style.cssText = "position:fixed;bottom:170px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#a7f3d0,#34d399);color:#052e16;padding:10px 18px;border-radius:999px;font-size:13px;font-weight:900;z-index:99999;opacity:0;transition:opacity .25s;pointer-events:none;box-shadow:0 4px 14px rgba(52,211,153,.5);";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = "1";
    clearTimeout(t._tid);
    t._tid = setTimeout(function(){ t.style.opacity = "0"; }, ms || 1700);
  }

  /* ========== 1. Arrow send button ========== */
  function installArrow(){
    try {
      var btn = document.querySelector(".expert-send-btn");
      if (!btn || btn._ajonArrow) return;
      btn._ajonArrow = true;
      btn.textContent = "\u2191";
      btn.setAttribute("aria-label", "Send");
    } catch(e){}
  }

  /* ========== 2. Animated thinking ========== */
  function installThinking(){
    try {
      if (typeof window.exShowTyping !== "function" || window.exShowTyping._ajonEnh) return;
      var orig = window.exShowTyping;
      var w = function(){
        try {
          var c = byId("expertMsgs") || $(".expert-msgs");
          if (!c) return orig.apply(this, arguments);
          var el = document.createElement("div");
          el.className = "ajon-thinking";
          el.innerHTML = '<span class="ajon-think-dot"></span><span class="ajon-think-dot"></span><span class="ajon-think-dot"></span><span class="ajon-think-text">Am Thinking Dear</span>';
          c.appendChild(el);
          try { c.scrollTop = c.scrollHeight; } catch(e){}
          return el;
        } catch(e){ return orig.apply(this, arguments); }
      };
      w._ajonEnh = true;
      window.exShowTyping = w;
    } catch(e){}
  }

  /* ========== 3. Textarea + auto-grow ========== */
  var WORDS = ["soap","honey","beeswax","oil","compost","biogas","solar","candle","yoghurt","bread","cake","juice","jam","tea","spice","paper","grow","make","sell","start","price","profit","capital","mask","brush","ghee","jelly","cheese","butter","ginger","garlic","aloe","neem","shea","coconut","mushroom","bees","rabbit","chicken","fish","goat","pig","charcoal","herbal","detergent","bleach","filter","stove","sauce"];

  function autoGrow(ta){
    try {
      if (!ta || ta.tagName !== "TEXTAREA") return;
      ta.style.height = "auto";
      var h = ta.scrollHeight;
      if (h < 28) h = 28;
      if (h > 140) h = 140;
      ta.style.height = h + "px";
    } catch(e){}
  }

  function bindTA(ta){
    if (ta._ajonBound) return;
    ta._ajonBound = true;
    ta.addEventListener("input", function(){ autoGrow(ta); });
    ta.addEventListener("focus", function(){ autoGrow(ta); });
    ta.addEventListener("keydown", function(ev){
      if (ev.key === "Enter" && !ev.shiftKey){
        ev.preventDefault();
        try { if (typeof window.askExpert === "function") window.askExpert(); } catch(e){}
      }
    });
    ta.addEventListener("input", function(){
      try {
        var pred = byId("helperKbPred");
        if (!pred) return;
        var parts = (ta.value || "").split(/\s+/);
        var q = (parts[parts.length - 1] || "").toLowerCase();
        var m = [];
        if (q){
          for (var i = 0; i < WORDS.length; i++){
            if (WORDS[i].indexOf(q) === 0) m.push(WORDS[i]);
            if (m.length >= 12) break;
          }
        }
        if (!m.length) m = WORDS.slice(0, 12);
        var h = "";
        for (var k = 0; k < m.length; k++){
          h += '<button class="kb-pred-btn" type="button" onclick="helperKbInsertWord(\'' + m[k] + '\')">' + m[k] + '</button>';
        }
        pred.innerHTML = h;
      } catch(e){}
    });
  }

  function upgradeInput(){
    try {
      var inp = byId("aiInput");
      if (!inp) return;
      if (inp.tagName === "TEXTAREA"){ autoGrow(inp); return; }
      var ta = document.createElement("textarea");
      ta.id = "aiInput";
      ta.className = inp.className || "";
      ta.placeholder = inp.placeholder || "Ask Mr Expert anything...";
      ta.autocomplete = "off";
      ta.rows = 1;
      ta.value = inp.value || "";
      // inline styles as backup (CSS also applies)
      ta.style.background = "transparent";
      ta.style.color = "#e8fff4";
      ta.style.border = "0";
      ta.style.outline = "none";
      ta.style.resize = "none";
      ta.style.padding = "9px 4px";
      ta.style.width = "auto";
      ta.style.flex = "1 1 auto";
      ta.style.minWidth = "0";
      ta.style.maxHeight = "140px";
      ta.style.minHeight = "28px";
      ta.style.fontFamily = "inherit";
      ta.style.fontSize = "14px";
      ta.style.lineHeight = "1.4";
      ta.style.boxSizing = "border-box";
      inp.parentNode.replaceChild(ta, inp);
      bindTA(ta);
      autoGrow(ta);
      setTimeout(function(){ autoGrow(ta); }, 60);
    } catch(e){}
  }

  /* ========== 4. Rich formatting ========== */
  function esc(s){ return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

  function formatText(raw){
    var s = esc(raw);
    s = s.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    var lines = s.split("\n");
    var out = [];
    var boldDone = false;
    for (var i = 0; i < lines.length; i++){
      var line = lines[i];
      var trimmed = line.replace(/^\s+|\s+$/g, "");
      if (!trimmed){ out.push(""); continue; }
      if (/^[-*•]\s+/.test(trimmed)){
        out.push("&nbsp;&nbsp;&nbsp;• " + trimmed.replace(/^[-*•]\s+/, ""));
        continue;
      }
      var num = trimmed.match(/^(\d+)[.)]\s+(.*)$/);
      if (num){
        out.push("&nbsp;&nbsp;&nbsp;" + num[1] + ". " + num[2]);
        continue;
      }
      var isHead = false;
      try {
        if (/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}]/u.test(trimmed)) isHead = true;
        if (/^(Step|Steps|Example|Tip|Warning|Note|Ingredients|Overview|Summary|Materials|Tools|What you need|How to|Result|Benefits):?/i.test(trimmed)) isHead = true;
        if (trimmed.length < 70 && /:$/.test(trimmed)) isHead = true;
      } catch(e){}
      if (!boldDone && trimmed.length < 140 && /[.!?]$/.test(trimmed) && trimmed.split(/\s+/).length <= 20){
        out.push("<b>" + trimmed + "</b>");
        boldDone = true;
        continue;
      }
      if (isHead && trimmed.indexOf("<b>") !== 0){
        out.push("<b>" + trimmed + "</b>");
      } else {
        out.push(trimmed);
      }
    }
    return out.join("\n").replace(/\n/g, "<br>");
  }

  function formatBubble(bubble, originalText){
    try {
      if (!bubble || bubble._ajonFmt) return;
      bubble._ajonFmt = true;
      var imgs = bubble.querySelectorAll("img.ajon-thumb");
      var saved = [];
      for (var i = 0; i < imgs.length; i++) saved.push(imgs[i]);
      bubble.innerHTML = formatText(originalText);
      for (var j = 0; j < saved.length; j++) bubble.appendChild(saved[j]);
    } catch(e){}
  }

  function hookTypeInto(){
    try {
      if (typeof window.exTypeInto !== "function" || window.exTypeInto._ajonV3) return;
      var orig = window.exTypeInto;
      var w = function(bubble, text, done){
        var wrappedDone = function(){
          try { formatBubble(bubble, text); } catch(e){}
          if (typeof done === "function") done();
        };
        return orig.call(this, bubble, text, wrappedDone);
      };
      w._ajonV3 = true;
      window.exTypeInto = w;
    } catch(e){}
  }

  /* ========== 5. Wiki thumbnails (reliable - own fetch) ========== */
  var lastQuestion = "";

  function hookAskToTrack(){
    try {
      if (typeof window.askExpert !== "function" || window.askExpert._ajonTrackQ) return;
      var orig = window.askExpert;
      var w = function(){
        try {
          var inp = byId("aiInput");
          if (inp) lastQuestion = String(inp.value || "").trim();
        } catch(e){}
        return orig.apply(this, arguments);
      };
      w._ajonTrackQ = true;
      window.askExpert = w;
    } catch(e){}
  }

  function isFactual(q){
    var s = String(q || "").toLowerCase().trim();
    if (!s) return false;
    var starters = ["what is","what are","what was","who is","who was","who are",
      "where is","where was","where are","when was","when did","when is",
      "history of","tell me about","explain","define","meaning of"];
    for (var i = 0; i < starters.length; i++) if (s.indexOf(starters[i]) === 0) return true;
    return false;
  }

  function attachImg(bubble, src){
    try {
      if (!bubble || bubble.querySelector("img.ajon-thumb")) return;
      var img = document.createElement("img");
      img.className = "ajon-thumb";
      img.src = src;
      img.alt = "";
      img.loading = "lazy";
      bubble.appendChild(img);
    } catch(e){}
  }

  function fetchWikiThumb(question, bubble){
    try {
      if (!question || !bubble || bubble._thumbTry) return;
      bubble._thumbTry = true;
      var sUrl = "https://en.wikipedia.org/w/api.php?" + new URLSearchParams({
        action: "query", list: "search", srsearch: question,
        format: "json", origin: "*", srlimit: "1"
      });
      fetch(sUrl).then(function(r){ return r.json(); }).then(function(j){
        var hits = j && j.query && j.query.search;
        if (!hits || !hits.length) throw new Error("no hit");
        var title = hits[0].title;
        var sumUrl = "https://en.wikipedia.org/api/rest_v1/page/summary/" + encodeURIComponent(title);
        return fetch(sumUrl).then(function(r){ return r.json(); }).then(function(s){
          if (s && s.thumbnail && s.thumbnail.source){
            var src = String(s.thumbnail.source);
            if (src.indexOf("//") === 0) src = "https:" + src;
            attachImg(bubble, src);
          }
        });
      }).catch(function(){});
    } catch(e){}
  }

  function watchForNewBubbles(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c || c._ajonObs) return;
      c._ajonObs = true;
      var obs = new MutationObserver(function(muts){
        for (var i = 0; i < muts.length; i++){
          for (var j = 0; j < muts[i].addedNodes.length; j++){
            var n = muts[i].addedNodes[j];
            if (n.nodeType !== 1) continue;
            var cls = n.className || "";
            if (cls.indexOf("ajon-thinking") > -1) continue;
            if (!/bubble|msg|ex-/i.test(cls)) continue;
            (function(node){
              setTimeout(function(){
                try {
                  var txt = (node.innerText || node.textContent || "").trim();
                  if (txt.length < 200) return;
                  if (!isFactual(lastQuestion)) return;
                  fetchWikiThumb(lastQuestion, node);
                } catch(e){}
              }, 1000);
            })(n);
          }
        }
      });
      obs.observe(c, { childList: true, subtree: false });
    } catch(e){}
  }

  /* ========== 6. Long-press save to notes ========== */
  function tryAllNoteSavers(text){
    var saved = false;
    // try function signatures
    if (typeof window.saveNote === "function"){
      try { window.saveNote(text); saved = true; } catch(e){
        try { window.saveNote({ text: text, body: text, content: text }); saved = true; } catch(e2){}
      }
    }
    if (!saved && typeof window.addNote === "function"){
      try { window.addNote(text); saved = true; } catch(e){}
    }
    if (!saved && typeof window.ajonSaveNote === "function"){
      try { window.ajonSaveNote(text); saved = true; } catch(e){}
    }
    // always ALSO write to backup keys so it shows up somewhere
    var keys = ["ajon_notes","ajonNotes","notes","ajon_saved_messages","ajon_expert_saved_notes"];
    for (var i = 0; i < keys.length; i++){
      try {
        var raw = localStorage.getItem(keys[i]);
        var arr = raw ? JSON.parse(raw) : [];
        if (!Array.isArray(arr)) arr = [];
        arr.push({ t: text, text: text, body: text, content: text, ts: Date.now(), date: new Date().toISOString() });
        if (arr.length > 500) arr = arr.slice(-500);
        localStorage.setItem(keys[i], JSON.stringify(arr));
      } catch(e){}
    }
    return saved;
  }

  function saveBubble(bubble){
    try {
      var text = String(bubble.innerText || bubble.textContent || "").trim();
      if (!text){ toast("Nothing to save"); return; }
      var img = bubble.querySelector("img.ajon-thumb");
      if (img && img.src) text += "\n[image] " + img.src;
      tryAllNoteSavers(text);
      toast("Saved to notes \u2713");
    } catch(e){
      toast("Save failed");
    }
  }

  function attachLongPress(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c || c._ajonLP) return;
      c._ajonLP = true;
      var timer = null, target = null;
      function findBubble(el){
        var cur = el;
        while (cur && cur !== c){
          if (cur.parentNode === c) return cur;
          cur = cur.parentNode;
        }
        return null;
      }
      function start(ev){
        var b = findBubble(ev.target);
        if (!b) return;
        if (b.classList && b.classList.contains("ajon-thinking")) return;
        target = b;
        try { b.classList.add("ajon-pressing"); } catch(e){}
        clearTimeout(timer);
        timer = setTimeout(function(){
          try { if (target) target.classList.remove("ajon-pressing"); } catch(e){}
          if (target) saveBubble(target);
          target = null;
        }, 600);
      }
      function cancel(){
        clearTimeout(timer);
        if (target){ try { target.classList.remove("ajon-pressing"); } catch(e){} }
        target = null;
      }
      c.addEventListener("touchstart", start, { passive: true });
      c.addEventListener("touchend", cancel);
      c.addEventListener("touchmove", cancel);
      c.addEventListener("touchcancel", cancel);
      c.addEventListener("mousedown", start);
      c.addEventListener("mouseup", cancel);
      c.addEventListener("mouseleave", cancel);
      c.addEventListener("contextmenu", function(ev){
        var b = findBubble(ev.target);
        if (b){ ev.preventDefault(); saveBubble(b); }
      });
    } catch(e){}
  }

  /* ========== INIT ========== */
  function init(){
    installArrow();
    installThinking();
    upgradeInput();
    hookTypeInto();
    hookAskToTrack();
    watchForNewBubbles();
    attachLongPress();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else setTimeout(init, 500);

  var tries = 0;
  var iv = setInterval(function(){
    tries++;
    installArrow();
    installThinking();
    hookTypeInto();
    hookAskToTrack();
    watchForNewBubbles();
    try {
      var el = byId("aiInput");
      if (el && el.tagName === "INPUT") upgradeInput();
    } catch(e){}
    attachLongPress();
    if (tries >= 15) clearInterval(iv);
  }, 900);

  try { console.log("[Ajon Enhancements V3] loaded"); } catch(e){}
})();
