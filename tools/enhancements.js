/* __EXPERT_ENHANCEMENTS_V1__ */
(function(){
  "use strict";
  if (window.__ajonExpertEnhancements) return;
  window.__ajonExpertEnhancements = true;

  function byId(id){ return document.getElementById(id); }
  function $(s){ return document.querySelector(s); }

  /* ---------- TOAST ---------- */
  function toast(msg){
    var t = byId("ajonEnhToast");
    if (!t){
      t = document.createElement("div");
      t.id = "ajonEnhToast";
      t.style.cssText = "position:fixed;bottom:150px;left:50%;transform:translateX(-50%);background:#00c853;color:#00220e;padding:8px 16px;border-radius:999px;font-size:13px;font-weight:800;z-index:99999;opacity:0;transition:opacity .25s;pointer-events:none;";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = "1";
    clearTimeout(t._tid);
    t._tid = setTimeout(function(){ t.style.opacity = "0"; }, 1600);
  }

  /* ---------- 4. ARROW SEND BUTTON ---------- */
  function installArrowButton(){
    try {
      var btn = document.querySelector(".expert-send-btn");
      if (!btn) return false;
      if (btn._ajonArrow) return true;
      btn._ajonArrow = true;
      btn.textContent = "\u2191";
      btn.setAttribute("aria-label", "Send");
      return true;
    } catch(e){ return false; }
  }

  /* ---------- 5. ANIMATED THINKING ---------- */
  function installThinkingOverride(){
    try {
      if (typeof window.exShowTyping !== "function") return false;
      if (window.exShowTyping._ajonEnh) return true;
      var orig = window.exShowTyping;
      var wrapped = function(){
        try {
          var container = byId("expertMsgs") || document.querySelector(".expert-msgs");
          if (!container) return orig.apply(this, arguments);
          var wrap = document.createElement("div");
          wrap.className = "ajon-thinking";
          wrap.innerHTML = '<span class="ajon-think-dot"></span>'
            + '<span class="ajon-think-dot"></span>'
            + '<span class="ajon-think-dot"></span>'
            + '<span class="ajon-think-text">Am Thinking Dear</span>';
          container.appendChild(wrap);
          try { container.scrollTop = container.scrollHeight; } catch(e){}
          return wrap;
        } catch(e){
          return orig.apply(this, arguments);
        }
      };
      wrapped._ajonEnh = true;
      window.exShowTyping = wrapped;
      return true;
    } catch(e){ return false; }
  }

  /* ---------- 1. AUTO-GROW TEXTAREA ---------- */
  var FALLBACK_WORDS = ["soap","honey","beeswax","oil","compost","biogas","solar","candle",
    "yoghurt","bread","cake","juice","jam","tea","spice","paper","grow","make","sell",
    "start","price","profit","capital","mask","brush","ghee","jelly","cheese","butter",
    "ginger","garlic","aloe","neem","shea","coconut","mushroom","bees","rabbit","chicken",
    "fish","goat","pig","charcoal","herbal","detergent","bleach","filter","stove","sauce"];

  function upgradeInput(){
    try {
      var inp = byId("aiInput");
      if (!inp) return false;
      if (inp.tagName === "TEXTAREA") return true;

      var ta = document.createElement("textarea");
      ta.id = "aiInput";
      ta.className = inp.className || "";
      ta.placeholder = inp.placeholder || "Ask Mr Expert anything...";
      ta.autocomplete = "off";
      ta.rows = 1;
      ta.value = inp.value || "";
      for (var i = 0; i < inp.attributes.length; i++){
        var at = inp.attributes[i];
        if (at.name.indexOf("data-") === 0) ta.setAttribute(at.name, at.value);
      }

      inp.parentNode.replaceChild(ta, inp);

      function autoGrow(){
        try {
          ta.style.height = "auto";
          var h = Math.min(ta.scrollHeight, 140);
          ta.style.height = h + "px";
        } catch(e){}
      }
      ta.addEventListener("input", autoGrow);
      ta.addEventListener("focus", autoGrow);
      setTimeout(autoGrow, 50);

      // Enter sends, Shift+Enter newline
      ta.addEventListener("keydown", function(ev){
        if (ev.key === "Enter" && !ev.shiftKey && !ev.ctrlKey && !ev.metaKey){
          ev.preventDefault();
          try { if (typeof window.askExpert === "function") window.askExpert(); } catch(e){}
        }
      });

      // Local word prediction (V7's listener was on the removed element)
      ta.addEventListener("input", function(){
        try {
          var pred = byId("helperKbPred");
          if (!pred) return;
          var parts = (ta.value || "").split(/\s+/);
          var q = (parts[parts.length - 1] || "").toLowerCase();
          var matches = [];
          if (q){
            for (var m = 0; m < FALLBACK_WORDS.length; m++){
              if (FALLBACK_WORDS[m].indexOf(q) === 0) matches.push(FALLBACK_WORDS[m]);
              if (matches.length >= 12) break;
            }
          }
          if (!matches.length) matches = FALLBACK_WORDS.slice(0, 12);
          var html = "";
          for (var k = 0; k < matches.length; k++){
            html += '<button class="kb-pred-btn" type="button" onclick="helperKbInsertWord(\''
              + matches[k] + '\')">' + matches[k] + '</button>';
          }
          pred.innerHTML = html;
        } catch(e){}
      });

      return true;
    } catch(e){ return false; }
  }

  /* ---------- 3. RICH FORMATTING ---------- */
  function formatText(raw){
    var s = String(raw || "");
    s = s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    s = s.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    var lines = s.split("\n");
    var out = [];
    for (var i = 0; i < lines.length; i++){
      var line = lines[i];
      var trimmed = line.replace(/^\s+|\s+$/g, "");
      if (!trimmed){ out.push(""); continue; }
      var isBullet = /^\s*[-*•]\s+/.test(line);
      if (isBullet) {
        out.push("&nbsp;&nbsp;• " + trimmed.replace(/^\s*[-*•]\s+/, ""));
        continue;
      }
      var isHeading = false;
      try {
        if (/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/u.test(trimmed)) isHeading = true;
        if (/:$/.test(trimmed)) isHeading = true;
        if (/^\d+\.\s/.test(trimmed)) isHeading = false; /* keep numbered as-is */
        if (/^(Step|Steps|Example|Tip|Warning):?/i.test(trimmed)) isHeading = true;
      } catch(e){}
      if (isHeading && trimmed.indexOf("<b>") !== 0){
        out.push("<b>" + trimmed + "</b>");
      } else {
        out.push(trimmed);
      }
    }
    return out.join("\n").replace(/\n/g, "<br>");
  }

  function formatBubble(bubble, originalText){
    try {
      if (!bubble || bubble._ajonFormatted) return;
      bubble._ajonFormatted = true;
      bubble.innerHTML = formatText(originalText);
    } catch(e){}
  }

  /* ---------- 6. WIKI THUMBNAILS ---------- */
  function installThumbInterceptor(){
    try {
      if (window.__ajonThumbFetch) return true;
      window.__ajonThumbFetch = true;
      window.__ajonLastWikiThumb = null;

      var origFetch = window.fetch;
      window.fetch = function(url, opts){
        var u = String(url || "");
        var isWikiSummary = u.indexOf("wikipedia.org/api/rest_v1/page/summary/") > -1;
        if (isWikiSummary) window.__ajonLastWikiThumb = null;
        var p = origFetch.apply(this, arguments);
        if (isWikiSummary){
          return p.then(function(r){
            try {
              r.clone().json().then(function(j){
                if (j && j.thumbnail && j.thumbnail.source){
                  var src = String(j.thumbnail.source);
                  if (src.indexOf("//") === 0) src = "https:" + src;
                  window.__ajonLastWikiThumb = { url: src, ts: Date.now() };
                }
              }).catch(function(){});
            } catch(e){}
            return r;
          });
        }
        return p;
      };

      // Clear thumb at start of every new question
      if (typeof window.askExpert === "function" && !window.askExpert._ajonThumbWrapped){
        var origAsk = window.askExpert;
        var w = function(){
          window.__ajonLastWikiThumb = null;
          return origAsk.apply(this, arguments);
        };
        w._ajonThumbWrapped = true;
        window.askExpert = w;
      }
      return true;
    } catch(e){ return false; }
  }

  function attachThumbToLastBubble(){
    try {
      var thumb = window.__ajonLastWikiThumb;
      if (!thumb || (Date.now() - thumb.ts) > 15000) return;
      var container = byId("expertMsgs") || document.querySelector(".expert-msgs");
      if (!container) return;
      var bubbles = container.querySelectorAll(".ex-bubble, .msg-ex, .bubble");
      var last = bubbles.length ? bubbles[bubbles.length - 1] : null;
      if (!last || last._ajonThumbAttached) return;
      last._ajonThumbAttached = true;
      var img = document.createElement("img");
      img.className = "ajon-thumb";
      img.src = thumb.url;
      img.alt = "";
      img.loading = "lazy";
      last.appendChild(img);
      window.__ajonLastWikiThumb = null;
    } catch(e){}
  }

  /* ---------- HOOK exTypeInto ---------- */
  function hookTypeInto(){
    try {
      if (typeof window.exTypeInto !== "function") return false;
      if (window.exTypeInto._ajonEnh) return true;
      var orig = window.exTypeInto;
      var wrapped = function(bubble, text, done){
        var wrappedDone = function(){
          try { formatBubble(bubble, text); } catch(e){}
          try { setTimeout(attachThumbToLastBubble, 200); } catch(e){}
          if (typeof done === "function") done();
        };
        return orig.call(this, bubble, text, wrappedDone);
      };
      wrapped._ajonEnh = true;
      window.exTypeInto = wrapped;
      return true;
    } catch(e){ return false; }
  }

  /* ---------- 2. LONG-PRESS SAVE ---------- */
  function saveBubbleToNotes(bubble){
    try {
      var text = String(bubble.innerText || bubble.textContent || "").trim();
      if (!text) return;
      // Include thumbnail URL if present
      var img = bubble.querySelector("img.ajon-thumb");
      if (img && img.src) text += "\n[image] " + img.src;

      if (typeof window.saveNote === "function"){
        try { window.saveNote(text); toast("Saved to notes"); return; } catch(e){}
      }
      var key = "ajon_saved_messages";
      var arr = [];
      try { arr = JSON.parse(localStorage.getItem(key)) || []; } catch(e){}
      arr.push({ t: text, ts: Date.now() });
      if (arr.length > 200) arr = arr.slice(-200);
      try { localStorage.setItem(key, JSON.stringify(arr)); } catch(e){}
      toast("Saved");
    } catch(e){}
  }

  function attachLongPress(){
    try {
      var container = byId("expertMsgs") || document.querySelector(".expert-msgs");
      if (!container || container._ajonLP) return false;
      container._ajonLP = true;

      var pressTimer = null;
      var pressTarget = null;

      function findBubble(el){
        var cur = el;
        while (cur && cur !== container){
          if (cur.parentNode === container) return cur;
          cur = cur.parentNode;
        }
        return null;
      }

      function start(ev){
        var b = findBubble(ev.target);
        if (!b) return;
        if (b.classList && b.classList.contains("ajon-thinking")) return;
        pressTarget = b;
        clearTimeout(pressTimer);
        pressTimer = setTimeout(function(){
          saveBubbleToNotes(pressTarget);
          pressTarget = null;
        }, 650);
      }
      function cancel(){ clearTimeout(pressTimer); pressTarget = null; }

      container.addEventListener("touchstart", start, { passive: true });
      container.addEventListener("touchend", cancel);
      container.addEventListener("touchmove", cancel);
      container.addEventListener("touchcancel", cancel);
      container.addEventListener("mousedown", start);
      container.addEventListener("mouseup", cancel);
      container.addEventListener("mouseleave", cancel);
      container.addEventListener("contextmenu", function(ev){
        var b = findBubble(ev.target);
        if (b){
          ev.preventDefault();
          saveBubbleToNotes(b);
        }
      });
      return true;
    } catch(e){ return false; }
  }

  /* ---------- INIT + RETRY ---------- */
  function init(){
    installArrowButton();
    installThinkingOverride();
    upgradeInput();
    hookTypeInto();
    installThumbInterceptor();
    attachLongPress();
  }

  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 500);
  }

  // Retry for DOM that renders late (tab switching, etc.)
  var tries = 0;
  var iv = setInterval(function(){
    tries++;
    installArrowButton();
    installThinkingOverride();
    hookTypeInto();
    installThumbInterceptor();
    try {
      var el = byId("aiInput");
      if (el && el.tagName === "INPUT") upgradeInput();
    } catch(e){}
    attachLongPress();
    if (tries >= 15) clearInterval(iv);
  }, 900);

  try { console.log("[Ajon Enhancements V1] loaded"); } catch(e){}
})();
