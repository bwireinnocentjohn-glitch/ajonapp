/* __EXPERT_ENHANCEMENTS_V1__ */
(function(){
  "use strict";
  if (window.__ajonEnhV9) return;
  window.__ajonEnhV9 = true;

  var DAILY_LIMIT_STANDARD = Infinity;  /* UNLIMITED — no daily cap */
  function byId(id){ return document.getElementById(id); }
  function $(s){ return document.querySelector(s); }
  function now(){ return Date.now(); }

  function toast(msg, ms){
    var t = byId("ajonEnhToast");
    if (!t){
      t = document.createElement("div");
      t.id = "ajonEnhToast";
      t.style.cssText = "position:fixed;bottom:120px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#a7f3d0,#34d399);color:#052e16;padding:9px 16px;border-radius:999px;font-size:12px;font-weight:900;z-index:99999;opacity:0;transition:opacity .2s;pointer-events:none;max-width:80vw;text-align:center;box-shadow:0 4px 14px rgba(52,211,153,.45);";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = "1";
    clearTimeout(t._tid);
    t._tid = setTimeout(function(){ t.style.opacity = "0"; }, ms || 2000);
  }

  /* ================= VIEWPORT ================= */
  function installViewportFix(){
    try {
      if (!window.visualViewport) return;
      var vv = window.visualViewport;
      function apply(){
        try {
          var kb = Math.max(0, window.innerHeight - vv.height - vv.offsetTop);
          var b = document.body;
          if (b){
            b.style.paddingBottom = kb > 20 ? (kb + 4) + "px" : "0px";
            b.style.transition = "padding-bottom .15s ease-out";
          }
          try { if (vv.height) window.scrollTo(0, 0); } catch(e){}
        } catch(e){}
      }
      vv.addEventListener("resize", apply);
      vv.addEventListener("scroll", apply);
      window.addEventListener("orientationchange", function(){ setTimeout(apply, 200); });
      apply();
    } catch(e){}
  }

  /* ================= TIER (unlimited now) ================= */
  function detectTier(){
    try {
      var cands = ["ajon_plan","ajon_tier","ajon_sub_type","ajon_subscription","ajon_membership","ajon_sub_tier"];
      for (var i=0;i<cands.length;i++){
        var v = null;
        try { v = localStorage.getItem(cands[i]); } catch(e){}
        if (!v) continue;
        v = String(v).toLowerCase();
        if (/master|15000|unlimited|premium|vip/.test(v)) return "master";
        if (/standard|5000|basic|pro/.test(v)) return "standard";
      }
      var amt = 0;
      try { amt = Number(localStorage.getItem("ajon_sub_amount") || localStorage.getItem("ajon_sub_price") || localStorage.getItem("ajon_sub_paid") || 0); } catch(e){}
      if (amt >= 15000) return "master";
      if (amt >= 5000) return "standard";
      var subEnd = 0;
      try { subEnd = Number(localStorage.getItem("ajon_sub_end_v12") || localStorage.getItem("ajon_sub_end_v11") || localStorage.getItem("ajon_sub_end_v10") || localStorage.getItem("ajon_sub_end_v9") || 0); } catch(e){}
      if (subEnd > now()) return "standard";
      return "none";
    } catch(e){ return "none"; }
  }

  function installTapDetector(){
    try {
      if (window.__ajonTapDetected) return;
      window.__ajonTapDetected = true;
      document.addEventListener("click", function(ev){
        try {
          var el = ev.target, hops = 0;
          while (el && el !== document.body && hops < 6){
            if (el.tagName === "BUTTON" || el.tagName === "A") break;
            el = el.parentNode; hops++;
          }
          if (!el || el === document.body) return;
          var txt = (el.innerText || el.textContent || "").toLowerCase();
          if (!txt) return;
          if (txt.indexOf("15000") > -1 || txt.indexOf("15,000") > -1 || txt.indexOf("master") > -1 || txt.indexOf("unlimited") > -1 || txt.indexOf("vip") > -1){
            try { localStorage.setItem("ajon_plan","master"); } catch(e){}
            try { localStorage.setItem("ajon_sub_amount","15000"); } catch(e){}
            setTimeout(updateTierBadge, 100);
          } else if (txt.indexOf("5000") > -1 || txt.indexOf("5,000") > -1 || txt.indexOf("standard") > -1 || txt.indexOf("basic") > -1){
            try { localStorage.setItem("ajon_plan","standard"); } catch(e){}
            try { localStorage.setItem("ajon_sub_amount","5000"); } catch(e){}
            setTimeout(updateTierBadge, 100);
          }
        } catch(e){}
      }, true);
    } catch(e){}
  }

  function updateTierBadge(){
    try {
      var hdr = document.querySelector(".expert-header");
      if (!hdr) return;
      var old = hdr.querySelector(".ajon-tier-badge-header");
      if (old) old.parentNode.removeChild(old);
      var badge = document.createElement("span");
      badge.className = "ajon-tier-badge-header master";
      badge.textContent = "\u267E\uFE0F";
      badge.setAttribute("aria-label", "Unlimited questions");
      var badgeEl = hdr.querySelector(".expert-badge");
      var earth   = hdr.querySelector(".expert-earth");
      if (badgeEl && badgeEl.parentNode === hdr){
        if (earth && earth.parentNode === hdr) hdr.insertBefore(badge, earth);
        else badgeEl.parentNode.insertBefore(badge, badgeEl.nextSibling);
      } else {
        hdr.appendChild(badge);
      }
    } catch(e){}
  }

  /* ================= ARROW ================= */
  function installArrow(){
    try {
      var btn = document.querySelector(".expert-send-btn");
      if (!btn || btn._ajonArrow) return;
      btn._ajonArrow = true;
      btn.textContent = "\u2191";
      btn.setAttribute("aria-label", "Send");
    } catch(e){}
  }

  /* ================= THINKING ================= */
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

  /* ================= TEXTAREA ================= */
  function autoGrow(ta){
    try {
      if (!ta || ta.tagName !== "TEXTAREA") return;
      ta.style.height = "auto";
      var h = ta.scrollHeight;
      if (h < 20) h = 20;
      if (h > 100) h = 100;
      ta.style.height = h + "px";
    } catch(e){}
  }
  function bindTA(ta){
    if (ta._ajonBound) return;
    ta._ajonBound = true;
    ta.addEventListener("input", function(){ autoGrow(ta); });
    ta.addEventListener("focus", function(){
      autoGrow(ta);
      setTimeout(function(){ try { ta.scrollIntoView({block:"nearest"}); } catch(e){} }, 250);
    });
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

  /* ================= FORMAT ================= */
  function esc(s){ return String(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function formatText(raw){
    var s = esc(raw);
    s = s.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    var lines = s.split("\n"), out = [], boldDone = false;
    for (var i=0;i<lines.length;i++){
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

  /* ================= COPY ================= */
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

  /* ================= IMAGE CHAIN (4 sources) ================= */
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

  function attachImg(bubble, src){
    try {
      if (!bubble || !src) return false;
      if (bubble.querySelector("img.ajon-thumb")) return false;
      var img = document.createElement("img");
      img.className = "ajon-thumb";
      img.alt = "";
      img.referrerPolicy = "no-referrer";
      img.loading = "lazy";
      img.onerror = function(){
        try { img.className = "ajon-thumb-fail"; } catch(e){}
      };
      img.src = src;
      bubble.appendChild(img);
      return true;
    } catch(e){ return false; }
  }

  function tryWikipediaImage(q){
    return new Promise(function(resolve, reject){
      var url = "https://en.wikipedia.org/w/api.php?" + new URLSearchParams({
        action: "query", generator: "search", gsrsearch: q, gsrlimit: "3",
        prop: "pageimages", piprop: "thumbnail|original", pithumbsize: "480",
        format: "json", origin: "*"
      });
      fetch(url).then(function(r){ return r.json(); }).then(function(j){
        var pages = j && j.query && j.query.pages;
        if (!pages) return reject("no pages");
        var arr = [];
        for (var k in pages){ if (pages.hasOwnProperty(k)) arr.push(pages[k]); }
        for (var i=0;i<arr.length;i++){
          var p = arr[i];
          if (p.thumbnail && p.thumbnail.source){
            var u = String(p.thumbnail.source);
            if (u.indexOf("//") === 0) u = "https:" + u;
            return resolve(u);
          }
        }
        reject("no thumb");
      }).catch(reject);
    });
  }

  function tryCommonsImage(q){
    return new Promise(function(resolve, reject){
      var url = "https://commons.wikimedia.org/w/api.php?" + new URLSearchParams({
        action: "query", generator: "search", gsrsearch: q,
        gsrnamespace: "6", gsrlimit: "5",
        prop: "imageinfo", iiprop: "url|mime", iiurlwidth: "480",
        format: "json", origin: "*"
      });
      fetch(url).then(function(r){ return r.json(); }).then(function(j){
        var pages = j && j.query && j.query.pages;
        if (!pages) return reject("no pages");
        var arr = [];
        for (var k in pages){ if (pages.hasOwnProperty(k)) arr.push(pages[k]); }
        for (var i=0;i<arr.length;i++){
          var p = arr[i];
          var info = p.imageinfo && p.imageinfo[0];
          if (!info) continue;
          var u = info.thumburl || info.url;
          if (!u) continue;
          if (u.indexOf("//") === 0) u = "https:" + u;
          var mime = String(info.mime || "");
          if (mime && mime.indexOf("image/") !== 0) continue;
          if (/\.(svg|pdf|ogv|webm|ogg|tiff?)$/i.test(u)) continue;
          return resolve(u);
        }
        reject("no image");
      }).catch(reject);
    });
  }

  function tryOpenverseImage(q){
    return new Promise(function(resolve, reject){
      var url = "https://api.openverse.org/v1/images/?q=" + encodeURIComponent(q) + "&page_size=3";
      fetch(url).then(function(r){ return r.json(); }).then(function(j){
        var results = j && j.results;
        if (!results || !results.length) return reject("no results");
        for (var i=0;i<results.length;i++){
          var r = results[i];
          var u = r.thumbnail || r.url;
          if (u) return resolve(u);
        }
        reject("no url");
      }).catch(reject);
    });
  }

  function pollinationsUrl(q, model){
    var clean = String(q||"").replace(/[^\w\s]/g, " ").replace(/\s+/g, " ").trim().slice(0, 180);
    var prompt = clean + ", illustration, high quality, detailed";
    return "https://image.pollinations.ai/prompt/" + encodeURIComponent(prompt)
      + "?width=480&height=320&nologo=true&model=" + (model || "flux")
      + "&seed=" + Math.floor(Math.random() * 1000000);
  }

  function fetchResponseImage(question, bubble){
    try {
      if (!question || !bubble || bubble._thumbTry) return;
      bubble._thumbTry = true;
      var sources = [
        function(){ return tryWikipediaImage(question); },
        function(){ return tryCommonsImage(question); },
        function(){ return tryOpenverseImage(question); },
        function(){ return Promise.resolve(pollinationsUrl(question, "flux")); },
        function(){ return Promise.resolve(pollinationsUrl(question, "turbo")); }
      ];
      var i = 0;
      function run(){
        if (i >= sources.length) return;
        sources[i]().then(function(url){
          if (!url) throw new Error("empty");
          attachImg(bubble, url);
        }).catch(function(){
          i++;
          run();
        });
      }
      run();
    } catch(e){}
  }

  function watchNewBubbles(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c || c._ajonObsV9) return;
      c._ajonObsV9 = true;
      var obs = new MutationObserver(function(muts){
        for (var i=0;i<muts.length;i++){
          for (var j=0;j<muts[i].addedNodes.length;j++){
            var n = muts[i].addedNodes[j];
            if (n.nodeType !== 1) continue;
            var cls = n.className || "";
            if (cls.indexOf("ajon-thinking") > -1) continue;
            if (/user|me\b|sent/i.test(cls)) continue;
            if (!/bubble|msg|ex-/i.test(cls)) continue;
            ensureCopyBtn(n);
            if (!n._thumbTry && lastQuestion){
              var txt = (n.innerText || n.textContent || "").trim();
              if (txt.length > 40){
                var q = lastQuestion;
                setTimeout(function(){ fetchResponseImage(q, n); }, 700);
              }
            }
          }
        }
      });
      obs.observe(c, { childList: true, subtree: false });
    } catch(e){}
  }

  /* Safety net: scan for last bubble without image every 6s */
  function imageSafetyNet(){
    setInterval(function(){
      try {
        var c = byId("expertMsgs") || $(".expert-msgs");
        if (!c || !lastQuestion) return;
        var bubbles = c.querySelectorAll("[class*='bubble'], [class*='msg']");
        if (!bubbles.length) return;
        for (var i = bubbles.length - 1; i >= 0; i--){
          var b = bubbles[i];
          if (b.classList && b.classList.contains("ajon-thinking")) continue;
          if (/user|me\b|sent/i.test(b.className || "")) continue;
          if (b._thumbTry) return;
          var txt = (b.innerText || b.textContent || "").trim();
          if (txt.length < 40) return;
          fetchResponseImage(lastQuestion, b);
          return;
        }
      } catch(e){}
    }, 6000);
  }

  function addCopyToExisting(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (!c) return;
      var nodes = c.children;
      for (var i=0;i<nodes.length;i++){
        var n = nodes[i];
        if (!n.classList) continue;
        if (n.classList.contains("ajon-thinking")) continue;
        if (/user|me\b|sent/i.test(n.className || "")) continue;
        ensureCopyBtn(n);
      }
    } catch(e){}
  }

  /* ================= CLEAR CHAT ================= */
  function doClear(){
    try {
      var c = byId("expertMsgs") || $(".expert-msgs");
      if (c) c.innerHTML = "";
      try { if (window.EXPERT) window.EXPERT.msgs = []; } catch(e){}
      try { if (typeof window.clearAssistantChat === "function") window.clearAssistantChat(); } catch(e){}
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
      var row = document.querySelector(".expert-input-row");
      if (!row || row.querySelector(".ajon-clear-btn")) return;
      var btn = document.createElement("button");
      btn.className = "ajon-clear-btn";
      btn.type = "button";
      btn.textContent = "\uD83D\uDDD1";
      btn.setAttribute("aria-label", "Clear chat");
      btn.onclick = function(ev){
        ev.stopPropagation();
        if (!confirm("Clear this chat?")) return;
        doClear();
      };
      row.appendChild(btn);
    } catch(e){}
  }
  function watchQuoteCard(){
    try {
      var qc = byId("expertQuoteCard");
      if (!qc || qc._ajonQuoteWatch) return;
      qc._ajonQuoteWatch = true;
      var sync = function(){
        try {
          var btn = document.querySelector(".ajon-clear-btn");
          if (!btn) return;
          var hidden = qc.classList.contains("hidden") || qc.style.display === "none" || qc.offsetParent === null;
          if (hidden) btn.classList.remove("hidden-by-quote");
          else btn.classList.add("hidden-by-quote");
        } catch(e){}
      };
      try {
        var obs = new MutationObserver(sync);
        obs.observe(qc, { attributes: true, attributeFilter: ["class","style"] });
      } catch(e){}
      setInterval(sync, 1500);
      sync();
    } catch(e){}
  }

  /* ================= IMAGE ATTACH (vision) ================= */
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
    try { if (typeof window.__ajonGetKeys === "function"){ var k = window.__ajonGetKeys(); if (k) return k; } } catch(e){}
    var o = { groq:"", gemini:"" };
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
      systemInstruction: { parts: [{ text: "You are Mr Expert, a wise African business mentor. Describe the image briefly, then give practical advice in 3-5 sentences." }]},
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
      if (window.EXPERT && window.EXPERT.busy) return;
      try { window.EXPERT.busy = true; } catch(e){}
      try { exHideQuote(); } catch(e){}
      var lbl = (txt || "Sent an image") + "  \uD83D\uDDBC\uFE0F";
      try { exAddBubble("me", lbl); } catch(e){}
      try { window.EXPERT.msgs.push({ s:"me", t:lbl }); } catch(e){}
      if (inp) inp.value = "";
      setTimeout(function(){ try { autoGrow(inp); } catch(e){} }, 50);
      var typing = null;
      try { typing = exShowTyping(); } catch(e){}
      callVision(txt, img.base64, img.mime).then(function(text){
        try { if (typing && typing.parentNode) typing.parentNode.removeChild(typing); } catch(e){}
        var bb = exAddBubble("ex", "");
        try { window.EXPERT.msgs.push({ s:"ex", t:text }); } catch(e){}
        try { exTypeInto(bb, text, function(){ try { window.EXPERT.busy = false; } catch(e){} }); } catch(e){}
      }).catch(function(){
        try { if (typing && typing.parentNode) typing.parentNode.removeChild(typing); } catch(e){}
        var msg = "I couldn't analyze that image right now. Please try a smaller photo or check your connection.";
        try {
          var eb = exAddBubble("ex", "");
          try { window.EXPERT.msgs.push({ s:"ex", t:msg }); } catch(e){}
          exTypeInto(eb, msg, function(){ try { window.EXPERT.busy = false; } catch(e){} });
        } catch(e){ try { window.EXPERT.busy = false; } catch(e){} }
      });
    } catch(e){ try { window.EXPERT.busy = false; } catch(e){} }
  }

  /* ================= LIMIT (UNLIMITED) ================= */
  function hookAskLimit(){
    try {
      if (typeof window.askExpert !== "function" || window.askExpert._ajonLimitWrap) return;
      var orig = window.askExpert;
      var w = function(){
        if (currentImage) return sendImage();
        return orig.apply(this, arguments);
      };
      w._ajonLimitWrap = true;
      window.askExpert = w;
    } catch(e){}
  }

  /* ================= VOICE ================= */
  var MIC = { listening: false, webRec: null };
  function setMic(on){
    MIC.listening = !!on;
    try {
      var b = document.querySelector(".ajon-mic-btn");
      if (!b) return;
      if (on){ b.classList.add("listening"); b.textContent = "\u23F9"; }
      else { b.classList.remove("listening"); b.textContent = "\uD83C\uDFA4"; }
    } catch(e){}
  }
  function fillInput(t){
    try {
      var inp = byId("aiInput");
      if (!inp || !t) return;
      var v = String(inp.value || "").trim();
      inp.value = v ? (v + " " + t) : t;
      try { autoGrow(inp); } catch(e){}
      try { inp.focus(); } catch(e){}
    } catch(e){}
  }
  function getSpeech(){
    try {
      var C = window.Capacitor;
      if (C && C.Plugins && C.Plugins.SpeechRecognition) return C.Plugins.SpeechRecognition;
    } catch(e){}
    return null;
  }
  function stopVoice(){
    try {
      var p = getSpeech();
      if (p && typeof p.stop === "function"){ p.stop().catch(function(){}); }
    } catch(e){}
    try { if (MIC.webRec){ MIC.webRec.stop(); MIC.webRec = null; } } catch(e){}
    setMic(false);
  }
  function startWebVoice(){
    try {
      var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR){ toast("Voice not supported"); setMic(false); return; }
      var rec = new SR();
      rec.lang = "en-US";
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      MIC.webRec = rec;
      rec.onresult = function(ev){
        try { var t = ev.results[0][0].transcript; setMic(false); if (t) fillInput(t); } catch(e){ setMic(false); }
      };
      rec.onerror = function(ev){
        setMic(false);
        var m = ev && ev.error ? ev.error : "unknown";
        if (m === "not-allowed" || m === "service-not-allowed") toast("Microphone permission denied");
        else toast("Voice error: " + m);
      };
      rec.onend = function(){ setMic(false); MIC.webRec = null; };
      setMic(true);
      toast("Listening...");
      rec.start();
    } catch(e){ setMic(false); toast("Voice failed"); }
  }
  function startVoice(){
    if (MIC.listening) return stopVoice();
    var p = getSpeech();
    if (p && typeof p.start === "function"){
      try {
        var pr = p.requestPermissions ? p.requestPermissions() : Promise.resolve({});
        pr.then(function(perm){
          var granted = perm && (perm.speechRecognition === "granted" || perm.recordAudio === "granted" || perm.microphone === "granted");
          if (!granted && perm && (perm.speechRecognition === "denied" || perm.recordAudio === "denied")){
            toast("Microphone permission denied"); return;
          }
          setMic(true);
          toast("Listening...");
          p.start({ language: "en-US", maxResults: 1, partialResults: false, popup: false })
            .then(function(res){
              setMic(false);
              var t = res && res.matches && res.matches[0];
              if (t) fillInput(t);
            })
            .catch(function(){ setMic(false); startWebVoice(); });
        }).catch(function(){ startWebVoice(); });
        return;
      } catch(e){}
    }
    startWebVoice();
  }
  function installMicBtn(){
    try {
      var row = document.querySelector(".expert-input-row");
      if (!row || row.querySelector(".ajon-mic-btn")) return;
      var btn = document.createElement("button");
      btn.className = "ajon-mic-btn";
      btn.type = "button";
      btn.textContent = "\uD83C\uDFA4";
      btn.onclick = function(ev){ ev.stopPropagation(); ev.preventDefault(); startVoice(); };
      var attach = row.querySelector(".ajon-attach-btn");
      if (attach && attach.parentNode === row) attach.parentNode.insertBefore(btn, attach.nextSibling);
      else row.insertBefore(btn, row.firstChild);
    } catch(e){}
  }

  /* ================= LONG PRESS SAVE ================= */
  function trySave(text){
    if (typeof window.saveNote === "function"){
      try { window.saveNote(text); return true; } catch(e){
        try { window.saveNote({ text: text, body: text, content: text }); return true; } catch(e2){}
      }
    }
    if (typeof window.addNote === "function"){ try { window.addNote(text); return true; } catch(e){} }
    if (typeof window.ajonSaveNote === "function"){ try { window.ajonSaveNote(text); return true; } catch(e){} }
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

  /* ================= INIT ================= */
  function init(){
    installViewportFix();
    installTapDetector();
    installArrow();
    installThinking();
    upgradeInput();
    hookAskTrack();
    hookAskLimit();
    installAttachBtn();
    installMicBtn();
    installClearBtn();
    watchQuoteCard();
    watchNewBubbles();
    addCopyToExisting();
    attachLongPress();
    updateTierBadge();
    imageSafetyNet();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else setTimeout(init, 300);

  setTimeout(function(){
    installArrow();
    installThinking();
    hookAskTrack();
    hookAskLimit();
    installAttachBtn();
    installMicBtn();
    installClearBtn();
    try { var el = byId("aiInput"); if (el && el.tagName === "INPUT") upgradeInput(); } catch(e){}
    watchNewBubbles();
    attachLongPress();
    updateTierBadge();
  }, 2500);

  try { console.log("[Ajon Enhancements V9] loaded — unlimited, 5-source image chain"); } catch(e){}
})();
