/* __HYBRID_EXPERT_V2__ */
(function(){
  "use strict";
  if (window.__ajonHybridExpertV2) return;
  window.__ajonHybridExpertV2 = true;

  var CONFIG = {
    GROQ_KEY:   "PASTE_YOUR_GROQ_KEY_HERE",
    GEMINI_KEY: "PASTE_YOUR_GEMINI_KEY_HERE",
    GROQ_URL:   "https://api.groq.com/openai/v1/chat/completions",
    GROQ_MODEL: "llama-3.3-70b-versatile",
    GEMINI_URL: "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
    CACHE_PREFIX: "ajon_qa_v1_",
    CACHE_MAX: 500,
    CACHE_TTL_MS: 30 * 24 * 60 * 60 * 1000,
    TIMEOUT_MS: 45000,
    NOTICE: "\uD83D\uDCDA Here is what I know right now:",
    SYS: "You are Mr Expert, a wise African business and life mentor for the AJON app. Answer in 1-10 sentences. Be practical, kind, and give actionable advice. If the question is about making a product, name all key steps. Avoid longer essays."
  };

  try {
    var gk = localStorage.getItem("ajon_groq_key");
    var mk = localStorage.getItem("ajon_gemini_key");
    if (gk) CONFIG.GROQ_KEY = gk;
    if (mk) CONFIG.GEMINI_KEY = mk;
  } catch(e){}

  window.setExpertKeys = function(groq, gemini){
    try {
      if (groq   != null) { CONFIG.GROQ_KEY   = String(groq);   localStorage.setItem("ajon_groq_key",   CONFIG.GROQ_KEY); }
      if (gemini != null) { CONFIG.GEMINI_KEY = String(gemini); localStorage.setItem("ajon_gemini_key", CONFIG.GEMINI_KEY); }
      console.log("[Hybrid V2] Keys saved. Groq:", !!CONFIG.GROQ_KEY, "Gemini:", !!CONFIG.GEMINI_KEY);
      return true;
    } catch(e){ return false; }
  };

  function normKey(q){
    return String(q||"").toLowerCase().replace(/[^a-z0-9 ]/g,"").trim().replace(/\s+/g," ").slice(0, 120);
  }
  function cacheKey(q){
    try { return CONFIG.CACHE_PREFIX + btoa(normKey(q)).replace(/=/g,""); }
    catch(e){ return CONFIG.CACHE_PREFIX + normKey(q); }
  }
  function cacheGet(q){
    try {
      var k = cacheKey(q);
      var raw = localStorage.getItem(k);
      if (!raw) return null;
      var o = JSON.parse(raw);
      if (!o || !o.t) return null;
      if (o.ts && (Date.now() - o.ts) > CONFIG.CACHE_TTL_MS) {
        try { localStorage.removeItem(k); } catch(e){}
        return null;
      }
      o.hits = (o.hits||0) + 1;
      try { localStorage.setItem(k, JSON.stringify(o)); } catch(e){}
      return o.t;
    } catch(e){ return null; }
  }
  function cacheSet(q, text){
    try {
      var k = cacheKey(q);
      var o = { q: normKey(q), t: String(text||""), ts: Date.now(), hits: 0 };
      localStorage.setItem(k, JSON.stringify(o));
      pruneCache();
    } catch(e){}
  }
  function pruneCache(){
    try {
      var keys = [];
      for (var i=0; i<localStorage.length; i++){
        var k = localStorage.key(i);
        if (k && k.indexOf(CONFIG.CACHE_PREFIX) === 0) keys.push(k);
      }
      if (keys.length <= CONFIG.CACHE_MAX) return;
      var items = [];
      for (var j=0; j<keys.length; j++){
        try { items.push({ k: keys[j], o: JSON.parse(localStorage.getItem(keys[j]))||{} }); } catch(e){}
      }
      items.sort(function(a,b){
        var ha=a.o.hits||0, hb=b.o.hits||0;
        if (ha!==hb) return ha-hb;
        return (a.o.ts||0)-(b.o.ts||0);
      });
      var drop = items.slice(0, items.length - CONFIG.CACHE_MAX);
      for (var d=0; d<drop.length; d++){ try { localStorage.removeItem(drop[d].k); } catch(e){} }
    } catch(e){}
  }

  function fetchTO(url, opts, ms){
    return new Promise(function(resolve, reject){
      var ctl = null;
      try { ctl = new AbortController(); } catch(e){}
      var finished = false;
      var timer = setTimeout(function(){
        if (finished) return; finished = true;
        if (ctl) try { ctl.abort(); } catch(e){}
        reject(new Error("timeout"));
      }, ms);
      var o = {};
      for (var k in opts) if (opts.hasOwnProperty(k)) o[k] = opts[k];
      if (ctl) o.signal = ctl.signal;
      fetch(url, o).then(function(r){
        if (finished) return; finished = true;
        clearTimeout(timer); resolve(r);
      }).catch(function(err){
        if (finished) return; finished = true;
        clearTimeout(timer); reject(err);
      });
    });
  }

  function callGroq(q){
    if (!CONFIG.GROQ_KEY || CONFIG.GROQ_KEY.indexOf("PASTE_") === 0) {
      return Promise.reject(new Error("no groq key"));
    }
    return fetchTO(CONFIG.GROQ_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + CONFIG.GROQ_KEY
      },
      body: JSON.stringify({
        model: CONFIG.GROQ_MODEL,
        messages: [
          { role: "system", content: CONFIG.SYS },
          { role: "user", content: q }
        ],
        temperature: 0.6,
        max_tokens: 220
      })
    }, CONFIG.TIMEOUT_MS).then(function(r){
      if (!r.ok) throw new Error("groq " + r.status);
      return r.json();
    }).then(function(j){
      var txt = j && j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
      if (!txt) throw new Error("groq empty");
      return String(txt).trim();
    });
  }

  function callGemini(q){
    if (!CONFIG.GEMINI_KEY || CONFIG.GEMINI_KEY.indexOf("PASTE_") === 0) {
      return Promise.reject(new Error("no gemini key"));
    }
    var url = CONFIG.GEMINI_URL + "?key=" + encodeURIComponent(CONFIG.GEMINI_KEY);
    return fetchTO(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: q }] }],
        systemInstruction: { parts: [{ text: CONFIG.SYS }] },
        generationConfig: { temperature: 0.6, maxOutputTokens: 220 }
      })
    }, CONFIG.TIMEOUT_MS).then(function(r){
      if (!r.ok) throw new Error("gemini " + r.status);
      return r.json();
    }).then(function(j){
      var c = j && j.candidates && j.candidates[0] && j.candidates[0].content;
      var txt = c && c.parts && c.parts[0] && c.parts[0].text;
      if (!txt) throw new Error("gemini empty");
      return String(txt).trim();
    });
  }

  if (typeof window.buildExpertReply === "function" && !window.__ajonOriginalBuildExpertReply) {
    window.__ajonOriginalBuildExpertReply = window.buildExpertReply;
  }

  var turnToken = 0;

  function fireBackgroundAPI(q, myTurn){
    callGroq(q).then(function(t){
      handleAPIResult(q, t, myTurn);
    }).catch(function(){
      return callGemini(q).then(function(t){
        handleAPIResult(q, t, myTurn);
      }).catch(function(){ /* silent — local already shown */ });
    });
  }

  function handleAPIResult(q, text, myTurn){
    if (myTurn !== turnToken) return;
    if (!text) return;
    cacheSet(q, text);
    try {
      var b = exAddBubble("ex", "");
      window.EXPERT.msgs.push({ s: "ex", t: text });
      exTypeInto(b, text, function(){});
    } catch(e){}
  }

  function install(){
    var helpers = ["byId","exAddBubble","exHideQuote","exTypeInto"];
    for (var i=0; i<helpers.length; i++){
      if (typeof window[helpers[i]] !== "function") {
        try { console.warn("[Hybrid V2] missing helper:", helpers[i]); } catch(e){}
        return false;
      }
    }
    if (typeof window.EXPERT === "undefined" || !window.EXPERT) {
      try { console.warn("[Hybrid V2] EXPERT missing"); } catch(e){}
      return false;
    }

    window.askExpert = function(){
      var myTurn = ++turnToken;
      try {
        if (typeof hasFullAccess === "function" && !hasFullAccess()) { expertGate(); return; }
        if (window.EXPERT.busy) return;
        var inp = byId("aiInput");
        if (!inp) return;
        var q = String(inp.value || "").trim();
        if (!q) { inp.focus(); return; }
        inp.value = "";
        window.EXPERT.busy = true;
        exHideQuote();
        exAddBubble("me", q);
        window.EXPERT.msgs.push({ s: "me", t: q });

        /* 1. CACHE HIT — instant, no notice */
        var cached = cacheGet(q);
        if (cached) {
          var b1 = exAddBubble("ex", "");
          window.EXPERT.msgs.push({ s: "ex", t: cached });
          exTypeInto(b1, cached, function(){ window.EXPERT.busy = false; });
          return;
        }

        /* 2. LOCAL ANSWER — shown immediately */
        var localReplies = null;
        try {
          if (typeof window.__ajonOriginalBuildExpertReply === "function") {
            localReplies = window.__ajonOriginalBuildExpertReply(q);
          }
        } catch(e){}
        if (!localReplies || !localReplies.length) {
          localReplies = [
            "I am here. \uD83D\uDE42 Let me help you.",
            "Try asking: 'how do I make soap?' or 'how do I make honey?'",
            "Or a business term like 'cash flow' or 'profit margin'."
          ];
        }
        localReplies = [CONFIG.NOTICE + "\n\n" + localReplies[0]].concat(localReplies.slice(1));

        var idx = 0;
        function sendLocal(){
          if (myTurn !== turnToken) return;
          if (idx >= localReplies.length) {
            window.EXPERT.busy = false;
            /* 3. API in background — takes as long as it needs (up to 45s) */
            fireBackgroundAPI(q, myTurn);
            return;
          }
          var txt = localReplies[idx];
          var bb = exAddBubble("ex", "");
          window.EXPERT.msgs.push({ s: "ex", t: txt });
          exTypeInto(bb, txt, function(){ idx++; setTimeout(sendLocal, 120); });
        }
        sendLocal();
      } catch(err){
        try { console.log("[Hybrid V2] sync error", err); } catch(e){}
        try { if (window.EXPERT) window.EXPERT.busy = false; } catch(e){}
      }
    };

    try { console.log("[Ajon Hybrid V2] installed"); } catch(e){}
    return true;
  }

  var tries = 0;
  function attempt(){
    if (install()) return;
    tries++;
    if (tries < 20) setTimeout(attempt, 500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", attempt);
  } else {
    setTimeout(attempt, 400);
  }
})();
