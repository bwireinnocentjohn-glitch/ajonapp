/* __EXPERT_ENHANCEMENTS_V1__ */
(function(){
  "use strict";
  if (window.__ajonEnhV5) return;
  window.__ajonEnhV5 = true;

  function byId(id){ return document.getElementById(id); }
  function $(s){ return document.querySelector(s); }
  function now(){ return Date.now(); }

  var DAILY_LIMIT_STANDARD = 20;

  function toast(msg, ms){
    var t = byId("ajonEnhToast");
    if (!t){
      t = document.createElement("div");
      t.id = "ajonEnhToast";
      t.style.cssText = "position:fixed;bottom:170px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#a7f3d0,#34d399);color:#052e16;padding:10px 18px;border-radius:999px;font-size:13px;font-weight:900;z-index:99999;opacity:0;transition:opacity .25s;pointer-events:none;box-shadow:0 4px 14px rgba(52,211,153,.5);max-width:80vw;text-align:center;";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = "1";
    clearTimeout(t._tid);
    t._tid = setTimeout(function(){ t.style.opacity = "0"; }, ms || 2200);
  }

  /* ================= TIER DETECTION ================= */
  function detectTier(){
    try {
      var candidates = ["ajon_plan","ajon_tier","ajon_sub_type","ajon_subscription","ajon_membership","ajon_sub_tier"];
      for (var i=0; i<candidates.length; i++){
        var v = null;
        try { v = localStorage.getItem(candidates[i]); } catch(e){}
        if (!v) continue;
        v = String(v).toLowerCase();
        if (/master|15000|unlimited|premium|vip/.test(v)) return "master";
        if (/standard|5000|basic|pro/.test(v)) return "standard";
      }
      var amt = 0;
      try {
        amt = Number(localStorage.getItem("ajon_sub_amount") || localStorage.getItem("ajon_sub_price") || localStorage.getItem("ajon_sub_paid") || 0);
      } catch(e){}
      if (amt >= 15000) return "master";
      if (amt >= 5000) return "standard";

      var title = "";
      try { title = String(localStorage.getItem("ajon_sub_title") || "").toLowerCase(); } catch(e){}
      if (/master|unlimited/.test(title)) return "master";

      var subEnd = 0;
      try {
        subEnd = Number(
          localStorage.getItem("ajon_sub_end_v12") ||
          localStorage.getItem("ajon_sub_end_v11") ||
          localStorage.getItem("ajon_sub_end_v10") ||
          localStorage.getItem("ajon_sub_end_v9") ||
          0
        );
      } catch(e){}
      if (subEnd > now()) return "standard";
      return "none";
    } catch(e){ return "none"; }
  }

  /* ============ TAP DETECTOR (Unlock tab) ============ */
  function installTapDetector(){
    try {
      if (window.__ajonTapDetected) return;
      window.__ajonTapDetected = true;
      document.addEventListener("click", function(ev){
        try {
          var el = ev.target;
          var hops = 0;
          while (el && el !== document.body && hops < 6){
            if (el.tagName === "BUTTON" || el.tagName === "A"){
              break;
            }
            el = el.parentNode;
            hops++;
          }
          if (!el || el === document.body) return;
          var txt = (el.innerText || el.textContent || "").toLowerCase();
          if (!txt) return;
          if (txt.indexOf("15000") > -1 || txt.indexOf("15,000") > -1 || txt.indexOf("master") > -1 || txt.indexOf("unlimited") > -1 || txt.indexOf("vip") > -1){
            try { localStorage.setItem("ajon_plan", "master"); } catch(e){}
            try { localStorage.setItem("ajon_sub_amount", "15000"); } catch(e){}
            setTimeout(updateTierBadge, 100);
          } else if (txt.indexOf("5000") > -1 || txt.indexOf("5,000") > -1 || txt.indexOf("standard") > -1 || txt.indexOf("basic") > -1){
            try { localStorage.setItem("ajon_plan", "standard"); } catch(e){}
            try { localStorage.setItem("ajon_sub_amount", "5000"); } catch(e){}
            setTimeout(updateTierBadge, 100);
          }
        } catch(e){}
      }, true);
    } catch(e){}
  }

  /* ============ DAILY COUNTER ============ */
  function dailyKey(){
    var d = new Date();
    return "ajon_expert_daily_" + d.getFullYear() + "_" + (d.getMonth()+1) + "_" + d.getDate();
  }
  function dailyCount(){
    try { return Number(localStorage.getItem(dailyKey())) || 0; } catch(e){ return 0; }
  }
  function dailyBump(){
    try {
      var n = dailyCount() + 1;
      localStorage.setItem(dailyKey(), String(n));
      try {
        for (var i=0; i<localStorage.length; i++){
          var k = localStorage.key(i);
          if (k && k.indexOf("ajon_expert_daily_") === 0 && k !== dailyKey()){
            localStorage.removeItem(k);
          }
        }
      } catch(e){}
      return n;
    } catch(e){ return 0; }
  }
  function dailyRemaining(){
    var tier = detectTier();
    if (tier === "master") return Infinity;
    var c = dailyCount();
    return Math.max(0, DAILY_LIMIT_STANDARD - c);
  }

  /* ============ TIER BADGE ============ */
  function updateTierBadge(){
    try {
      var row = document.querySelector(".expert-input-row");
      if (!row) return;
      var old = row.querySelector(".ajon-tier-badge");
      if (old) old.parentNode.removeChild(old);
      var tier = detectTier();
      if (tier === "none") return;
      var b = document.createElement("span");
      b.className = "ajon-tier-badge";
      if (tier === "master"){
        b.classList.add("master");
        b.textContent = "\u267E\uFE0F MASTER";
      } else {
        var left = dailyRemaining();
        if (left <= 3) b.classList.add("low");
        b.textContent = "\u23F1 " + left + "/" + DAILY_LIMIT_STANDARD;
      }
      row.appendChild(b);
    } catch(e){}
  }

  /* ============ ARROW SEND ============ */
  function installArrow(){
    try {
      var btn = document.querySelector(".expert-send-btn");
      if (!btn || btn._ajonArrow) return;
      btn._ajonArrow = true;
      btn.textContent = "\u2191";
      btn.setAttribute("aria-label", "Send");
    } catch(e){}
  }

  /* ============ ANIMATED THINKING ============ */
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

  /* ============ TEXTAREA + AUTOGROW ============ */
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
      inp.parentNode.replaceChild(ta, inp);
      bindTA(ta);
      autoGrow(ta);
      setTimeout(function(){ autoGrow(ta); }, 60);
    } catch(e){}
  }

  /* ============ RICH FORMAT ============ */
  function esc(s){ return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function formatText(raw){
    var s = esc(raw);
    s = s.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    var lines = s.split("\n");
    var out = []; var boldDone = false;
    for (var i=0; i<lines.length; i++){
      var line = lines[i];
      var t = line.replace(/^\s+|\s+$/g, "");
      if (!t){ out.push(""); continue; }
      if (/^[-*•]\s+/.test(t)){ out.push("&nbsp;&nbsp;&nbsp;• " + t.replace(/^[-*•]\s+/, "")); continue; }
      var num = t.match(/^(\d+)[.)]\s+(.*)$/);
      if (num){ out.push("&nbsp;&nbsp;&nbsp;" + num[1] + ". " + num[2]); continue; }
      var isHead = false;
      try {
        if (/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}]/u.test(t)) isHead = true;
        if (/^(Step|Steps|Example|Tip|Warning|Note|Ingredients|Overview|Summary|Materials|Tools|How to|Result|Benefits):?/i.test(t)) isHead = true;
        if (t.length < 70 && /:$/.test(t)) isHead = true;
      } catch(e){}
      if (!boldDone && t.length < 140 && /[.!?]$/.test(t) && t.split(/\s+/).length <= 20){
        out.push("<b>" + t + "</b>"); boldDone = true; continue;
      }
      if (isHead && t.indexOf("<b>") !== 0) out.push("<b>" + t + "</b>");
      else out.push(t);
    }
    return out.join("\n").replace(/\n/g, "<br>");
  }
  function formatBubble(bubble, originalText){
    try {
      if (!bubble || bubble._ajonFmt) return;
      bubble._ajonFmt = true;
      var keep = bubble.querySelectorAll("img.ajon-thumb, button.ajon-copy-btn");
      var saved = []; for (var i=0;i<keep.length;i++) saved.push(keep[i]);
      bubble.innerHTML = formatText(originalText);
      for (var j=0;j<saved.length;j++) bubble.appendChild(saved[j]);
    } catch(e){}
  }

  /* ============ COPY BUTTON ============ */
  function copyText(text){
    try {
      if (navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(text).then(function(){ toast("Copied \u2713"); }).catch(function(){ fallbackCopy(text); });
      } else fallbackCopy(text);
    } catch(e){ fallbackCopy(text); }
  }
  function fallbackCopy(text){
    try {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      document.execCommand("copy"); document.body.removeChild(ta);
      toast("Copied \u2713");
    } catch(e){ toast("Copy failed"); }
  }
  function ensureCopyBtn(bubble){
    try {
      if (!bubble || bubble._copyBtn) return;
      if (bubble.classList && bubble.classList.contains("ajon-thinking")) return;
      if (/user|me\b|sent/i.test(bubble.className || "")) return;
      bubble._copyBtn = true;
      bubble.classList.add("ajon-bubble-rel");
      var btn = document.createElement("button");
      btn.className = "ajon-copy-btn";
      btn.type = "button";
      btn.textContent = "\uD83D\uDCCB";
      btn.onclick = function(ev){
        ev.stopPropagation(); ev.preventDefault();
        var t = "";
        try {
          var clone = bubble.cloneNode(true);
          var c = clone.querySelector(".ajon-copy-btn"); if (c) c.parentNode.removeChild(c);
          t = String(clone.innerText || clone.textContent || "").trim();
        } catch(e){ t = String(bubble.innerText || "").trim(); }
        if (t) copyText(t);
      };
      bubble.appendChild(btn);
    } catch(e){}
  }

  /* ============ WIKI IMAGES (robust) ============ */
  var lastQuestion = "";

  function hookAskTrack(){
    try {
      if (typeof window.askExpert !== "function" || window.askExpert._ajonTrackQ) return;
      var orig = window.askExpert;
      var w = function(){
        try { var inp = byId("aiInput"); if (inp) lastQuestion = String(inp.value || "").trim(); } catch(e){}
        return orig.apply(this, arguments);
      };
      w._ajonTrackQ = true;
      window.askExpert = w;
    } catch(e){}
  }

  function attachImg(bubble, src, fallbackSrc){
    try {
      if (!bubble || bubble.querySelector("img.ajon-thumb")) return;
      var img = document.createElement("img");
      img.className = "ajon-thumb";
      img.alt = "";
      img.loading = "lazy";
      img.onerror = function(){
        try {
          if (fallbackSrc && img.src !== fallbackSrc){
            img.src = fallbackSrc;
            fallbackSrc = null;
            return;
          }
          img.className = "ajon-thumb-fail";
        } catch(e){}
      };
      img.src = src;
      bubble.appendChild(img);
    } catch(e){}
  }

  function fetchWikiThumb(question, bubble){
    try {
      if (!question || !bubble || bubble._thumbTry) return;
      bubble._thumbTry = true;
      var sUrl = "https://en.wikipedia.org/w/api.php?" + new URLSearchParams({
        action: "query", list: "search", srsearch: question,
        format: "json", origin: "*", srlimit: "3"
      });
      fetch(sUrl).then(function(r){ return r.json(); }).then(function(j){
        var hits = j && j.query && j.query.search;
        if (!hits || !hits.length) throw new Error("no hit");
        var titles = hits.map(function(h){ return h.title; });
        var chain = Promise.reject(new Error("start"));
        titles.forEach(function(t){
          chain = chain.catch(function(){
            var sumUrl = "https://en.wikipedia.org/api/rest_v1/page/summary/" + encodeURIComponent(t);
            return fetch(sumUrl).then(function(r){ return r.json(); }).then(function(s){
              if (!s) throw new Error("no summary");
              var thumb = s.thumbnail && s.thumbnail.source;
              var orig  = s.originalimage && s.originalimage.source;
              if (!thumb && !orig) throw new Error("no image");
              var t1 = thumb ? String(thumb) : String(orig);
              var t2 = orig ? String(orig) : null;
              if (t1.indexOf("//") === 0) t1 = "https:" + t1;
              if (t2 && t2.indexOf("//") === 0) t2 = "https:" + t2;
              attachImg(bubble, t1, t2);
              return true;
            });
          });
        });
        return chain;
      }).catch(function(){});
    } catch(e){}
  }

  function watchNewBubbles(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c || c._ajonObsV5) return;
      c._ajonObsV5 = true;
      var obs = new MutationObserver(function(muts){
        for (var i=0; i<muts.length; i++){
          for (var j=0; j<muts[i].addedNodes.length; j++){
            var n = muts[i].addedNodes[j];
            if (n.nodeType !== 1) continue;
            var cls = n.className || "";
            if (cls.indexOf("ajon-thinking") > -1) continue;
            if (/user|me\b|sent/i.test(cls)) continue;
            if (!/bubble|msg|ex-/i.test(cls)) continue;
            (function(node){
              setTimeout(function(){
                try {
                  ensureCopyBtn(node);
                  if (node.querySelector("img.ajon-thumb")) return;
                  if (!lastQuestion) return;
                  var txt = (node.innerText || node.textContent || "").trim();
                  if (txt.length < 40) return;
                  fetchWikiThumb(lastQuestion, node);
                } catch(e){}
              }, 800);
            })(n);
          }
        }
      });
      obs.observe(c, { childList: true, subtree: false });
    } catch(e){}
  }

  function addCopyToExisting(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c) return;
      var nodes = c.children;
      for (var i=0; i<nodes.length; i++){
        var n = nodes[i];
        if (!n.classList) continue;
        if (n.classList.contains("ajon-thinking")) continue;
        if (/user|me\b|sent/i.test(n.className || "")) continue;
        ensureCopyBtn(n);
      }
    } catch(e){}
  }

  /* ============ CLEAR CHAT ============ */
  function doClear(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (c) c.innerHTML = "";
      try { if (window.EXPERT) window.EXPERT.msgs = []; } catch(e){}
      var cleared = false;
      try { if (typeof window.clearAssistantChat === "function"){ window.clearAssistantChat(); cleared = true; } } catch(e){}
      setTimeout(function(){
        try {
          if (typeof exAddBubble === "function"){
            var w = "Hello! \uD83D\uDE0A I am Mr Expert. Ask me anything about business or life.";
            exAddBubble("ex", w);
            if (window.EXPERT && window.EXPERT.msgs) window.EXPERT.msgs.push({ s: "ex", t: w });
          }
        } catch(e){}
      }, 80);
      toast("Chat cleared");
    } catch(e){ toast("Clear failed"); }
  }
  function installClearBtn(){
    try {
      var panel = $(".expert-main") || byId("expertMain");
      if (!panel || panel.querySelector(".ajon-clear-btn")) return;
      try { panel.style.position = "relative"; } catch(e){}
      var btn = document.createElement("button");
      btn.className = "ajon-clear-btn";
      btn.type = "button";
      btn.textContent = "\uD83D\uDDD1";
      btn.onclick = function(ev){
        ev.stopPropagation();
        if (!confirm("Clear this chat?")) return;
        doClear();
      };
      panel.appendChild(btn);
    } catch(e){}
  }

  /* ============ IMAGE ATTACH + VISION ============ */
  var currentImage = null;

  function installAttachBtn(){
    try {
      var row = document.querySelector(".expert-input-row");
      if (!row || row.querySelector(".ajon-attach-btn")) return;
      var btn = document.createElement("button");
      btn.className = "ajon-attach-btn";
      btn.type = "button";
      btn.textContent = "\uD83D\uDCCE";
      btn.onclick = openPicker;
      row.appendChild(btn);
    } catch(e){}
  }
  function openPicker(){
    try {
      var inp = document.createElement("input");
      inp.type = "file"; inp.accept = "image/*"; inp.style.display = "none";
      inp.onchange = function(ev){
        try {
          var f = ev.target.files && ev.target.files[0];
          if (!f) return;
          if (f.size > 4 * 1024 * 1024){ toast("Image too large (max 4 MB)"); return; }
          var r = new FileReader();
          r.onload = function(){
            try {
              var d = String(r.result || "");
              var c = d.indexOf(",");
              if (c < 0) return;
              currentImage = { base64: d.slice(c+1), mime: f.type || "image/jpeg", previewUrl: d };
              showPreview();
            } catch(e){}
          };
          r.readAsDataURL(f);
        } catch(e){}
      };
      document.body.appendChild(inp);
      inp.click();
      setTimeout(function(){ try { document.body.removeChild(inp); } catch(e){} }, 60000);
    } catch(e){ toast("Could not open gallery"); }
  }
  function showPreview(){
    try {
      removePreview();
      var row = document.querySelector(".expert-input-row");
      if (!row || !currentImage) return;
      var img = document.createElement("img");
      img.className = "ajon-img-preview";
      img.src = currentImage.previewUrl;
      img.alt = "";
      row.appendChild(img);
      var clr = document.createElement("button");
      clr.className = "ajon-img-clear";
      clr.type = "button";
      clr.textContent = "\u2715";
      clr.onclick = function(ev){ ev.stopPropagation(); currentImage = null; removePreview(); };
      row.appendChild(clr);
    } catch(e){}
  }
  function removePreview(){
    try {
      var r = document.querySelector(".expert-input-row");
      if (!r) return;
      var a = r.querySelector(".ajon-img-preview"); if (a) a.parentNode.removeChild(a);
      var b = r.querySelector(".ajon-img-clear");   if (b) b.parentNode.removeChild(b);
    } catch(e){}
  }
  function getKeys(){
    try {
      if (typeof window.__ajonGetKeys === "function"){
        var k = window.__ajonGetKeys();
        if (k) return k;
      }
    } catch(e){}
    var o = { groq: "", gemini: "" };
    try { o.groq = localStorage.getItem("ajon_groq_key") || ""; } catch(e){}
    try { o.gemini = localStorage.getItem("ajon_gemini_key") || ""; } catch(e){}
    return o;
  }
  function callVision(text, b64, mime){
    var k = getKeys();
    if (!k.gemini || k.gemini.indexOf("PASTE_") === 0) return Promise.reject(new Error("no key"));
    var url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=" + encodeURIComponent(k.gemini);
    var body = {
      contents: [{ role: "user", parts: [
        { text: text || "Describe this image briefly and suggest how I can use it for business in Uganda." },
        { inlineData: { mimeType: mime || "image/jpeg", data: b64 } }
      ]}],
      systemInstruction: { parts: [{ text: "You are Mr Expert, a wise African business mentor. Describe the image briefly, then give practical advice in 3-5 sentences. Warm, direct, actionable." }]},
      generationConfig: { temperature: 0.6, maxOutputTokens: 600 }
    };
    return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function(r){ if (!r.ok) throw new Error("vision " + r.status); return r.json(); })
      .then(function(j){
        var c = j && j.candidates && j.candidates[0] && j.candidates[0].content;
        var t = c && c.parts && c.parts[0] && c.parts[0].text;
        if (!t) throw new Error("empty");
        return String(t).trim();
      });
  }
  function sendImage(){
    try {
      var inp = byId("aiInput");
      var txt = String(inp ? inp.value : "").trim();
      var img = currentImage;
      currentImage = null; removePreview();
      if (!img) return;
      if (typeof hasFullAccess === "function" && !hasFullAccess()){ expertGate(); return; }
      var check = enforceLimit();
      if (!check.ok){ return; }
      if (window.EXPERT && window.EXPERT.busy) return;
      try { window.EXPERT.busy = true; } catch(e){}
      try { exHideQuote(); } catch(e){}
      var lbl = (txt || "Sent an image") + "  \uD83D\uDDBC\uFE0F";
      try { exAddBubble("me", lbl); } catch(e){}
      try { window.EXPERT.msgs.push({ s: "me", t: lbl }); } catch(e){}
      if (inp) inp.value = "";
      setTimeout(function(){ try { autoGrow(inp); } catch(e){} }, 50);
      var typing = null;
      try { typing = exShowTyping(); } catch(e){}
      callVision(txt, img.base64, img.mime).then(function(text){
        try { if (typing && typing.parentNode) typing.parentNode.removeChild(typing); } catch(e){}
        var bb = exAddBubble("ex", "");
        try { window.EXPERT.msgs.push({ s: "ex", t: text }); } catch(e){}
        try { exTypeInto(bb, text, function(){ try { window.EXPERT.busy = false; } catch(e){} }); } catch(e){}
        dailyBump(); updateTierBadge();
      }).catch(function(){
        try { if (typing && typing.parentNode) typing.parentNode.removeChild(typing); } catch(e){}
        var msg = "I couldn't analyze that image right now. Please try a smaller photo or check your connection.";
        try {
          var eb = exAddBubble("ex", "");
          try { window.EXPERT.msgs.push({ s: "ex", t: msg }); } catch(e){}
          exTypeInto(eb, msg, function(){ try { window.EXPERT.busy = false; } catch(e){} });
        } catch(e){ try { window.EXPERT.busy = false; } catch(e){} }
      });
    } catch(e){ try { window.EXPERT.busy = false; } catch(e){} }
  }

  /* ============ DAILY LIMIT ============ */
  function enforceLimit(){
    var tier = detectTier();
    if (tier === "master") return { ok: true };
    var c = dailyCount();
    if (c >= DAILY_LIMIT_STANDARD){
      toast("Daily limit reached (" + DAILY_LIMIT_STANDARD + "/day). Tap the 15,000/= Master plan in Unlock for unlimited.", 4000);
      return { ok: false };
    }
    return { ok: true };
  }

  /* ============ WRAP askExpert (limits + image) ============ */
  function hookAskLimit(){
    try {
      if (typeof window.askExpert !== "function" || window.askExpert._ajonLimitWrap) return;
      var orig = window.askExpert;
      var w = function(){
        if (currentImage) return sendImage();
        try {
          if (typeof hasFullAccess === "function" && !hasFullAccess()) return orig.apply(this, arguments);
        } catch(e){}
        var check = enforceLimit();
        if (!check.ok) return;
        try { dailyBump(); updateTierBadge(); } catch(e){}
        return orig.apply(this, arguments);
      };
      w._ajonLimitWrap = true;
      window.askExpert = w;
    } catch(e){}
  }

  /* ============ LONG PRESS SAVE ============ */
  function trySave(text){
    if (typeof window.saveNote === "function"){
      try { window.saveNote(text); return true; } catch(e){
        try { window.saveNote({ text: text, body: text, content: text }); return true; } catch(e2){}
      }
    }
    if (typeof window.addNote === "function"){
      try { window.addNote(text); return true; } catch(e){}
    }
    if (typeof window.ajonSaveNote === "function"){
      try { window.ajonSaveNote(text); return true; } catch(e){}
    }
    return false;
  }
  function saveBubble(bubble){
    try {
      var t = "";
      try {
        var clone = bubble.cloneNode(true);
        var c = clone.querySelector(".ajon-copy-btn"); if (c) c.parentNode.removeChild(c);
        t = String(clone.innerText || clone.textContent || "").trim();
      } catch(e){ t = String(bubble.innerText || "").trim(); }
      if (!t){ toast("Nothing to save"); return; }
      var img = bubble.querySelector("img.ajon-thumb");
      if (img && img.src) t += "\n[image] " + img.src;
      trySave(t);
      var keys = ["ajon_notes","ajonNotes","notes","ajon_saved_messages","ajon_expert_saved_notes"];
      for (var i=0;i<keys.length;i++){
        try {
          var raw = localStorage.getItem(keys[i]);
          var arr = raw ? JSON.parse(raw) : [];
          if (!Array.isArray(arr)) arr = [];
          arr.push({ t: t, text: t, ts: now(), date: new Date().toISOString() });
          if (arr.length > 500) arr = arr.slice(-500);
          localStorage.setItem(keys[i], JSON.stringify(arr));
        } catch(e){}
      }
      toast("Saved to notes \u2713");
    } catch(e){ toast("Save failed"); }
  }
  function attachLongPress(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c || c._ajonLP) return;
      c._ajonLP = true;
      var timer = null, target = null;
      function findBubble(el){
        var cur = el;
        while (cur && cur !== c){ if (cur.parentNode === c) return cur; cur = cur.parentNode; }
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

  /* ============ INIT ============ */
  function init(){
    installTapDetector();
    installArrow();
    installThinking();
    upgradeInput();
    hookAskTrack();
    hookAskLimit();
    installAttachBtn();
    installClearBtn();
    watchNewBubbles();
    addCopyToExisting();
    attachLongPress();
    updateTierBadge();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else setTimeout(init, 500);

  var tries = 0;
  var iv = setInterval(function(){
    tries++;
    installArrow();
    installThinking();
    hookAskTrack();
    hookAskLimit();
    installAttachBtn();
    installClearBtn();
    watchNewBubbles();
    addCopyToExisting();
    try { var el = byId("aiInput"); if (el && el.tagName === "INPUT") upgradeInput(); } catch(e){}
    attachLongPress();
    updateTierBadge();
    if (tries >= 20) clearInterval(iv);
  }, 900);

  try { console.log("[Ajon Enhancements V5] loaded"); } catch(e){}
})();
