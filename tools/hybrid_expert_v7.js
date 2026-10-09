/* __HYBRID_EXPERT_V7__ */
(function(){
  "use strict";
  if (window.__ajonHybridExpertV7) return;
  window.__ajonHybridExpertV7 = true;

  var CONFIG = {
    GROQ_KEY:   "PASTE_YOUR_GROQ_KEY_HERE",
    GEMINI_KEY: "PASTE_YOUR_GEMINI_KEY_HERE",
    GROQ_URL:   "https://api.groq.com/openai/v1/chat/completions",
    GROQ_MODEL: "openai/gpt-oss-120b",
    GEMINI_URL: "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
    CACHE_PREFIX: "ajon_qa_v5_",
    CACHE_MAX: 800,
    CACHE_TTL_MS: 60 * 24 * 60 * 60 * 1000,
    REQ_TIMEOUT_MS: 120000,
    WIKI_TIMEOUT_MS: 12000,
    MAX_TOKENS: 600,
    SYS: "You are Mr Expert, a wise African business and life mentor for the AJON app. Give a thorough practical answer in 3 to 5 sentences. Include specific steps or numbers when possible. Add one short real-life example if relevant. Be warm, direct, and avoid fluff."
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
      console.log("[Hybrid V7] Keys saved.");
      return true;
    } catch(e){ return false; }
  };

  /* ---------- CACHE ---------- */
  function normKey(q){ return String(q||"").toLowerCase().replace(/[^a-z0-9 ]/g,"").trim().replace(/\s+/g," ").slice(0,120); }
  function cacheKey(q){ try { return CONFIG.CACHE_PREFIX + btoa(normKey(q)).replace(/=/g,""); } catch(e){ return CONFIG.CACHE_PREFIX + normKey(q); } }
  function cacheGet(q){
    try {
      var k = cacheKey(q);
      var raw = localStorage.getItem(k);
      if (!raw) return null;
      var o = JSON.parse(raw);
      if (!o || !o.t) return null;
      if (o.ts && (Date.now() - o.ts) > CONFIG.CACHE_TTL_MS) { try { localStorage.removeItem(k); } catch(e){} return null; }
      o.hits = (o.hits||0) + 1;
      try { localStorage.setItem(k, JSON.stringify(o)); } catch(e){}
      return { text: o.t, src: o.src || "api" };
    } catch(e){ return null; }
  }
  function cacheSet(q, text, src){
    try {
      var k = cacheKey(q);
      var o = { q: normKey(q), t: String(text||""), ts: Date.now(), hits: 0, src: src || "api" };
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

  /* ---------- FETCH WITH TIMEOUT ---------- */
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

  /* ---------- WIKIPEDIA (only when suitable) ---------- */
  function isWikiSuitable(q){
    try {
      var s = String(q||"").toLowerCase().trim();
      if (!s) return false;
      var starters = ["what is","what are","what was","who is","who was","who are",
        "where is","where was","where are","when was","when did","when is",
        "history of","tell me about","explain","define","meaning of",
        "how does","how did","how do"];
      for (var i=0; i<starters.length; i++){
        if (s.indexOf(starters[i]) === 0) return true;
      }
      return false;
    } catch(e){ return false; }
  }

  function wikiSearch(q){
    var url = "https://en.wikipedia.org/w/api.php?" + new URLSearchParams({
      action: "query", list: "search", srsearch: q, format: "json",
      origin: "*", srlimit: "3"
    });
    return fetchTO(url, { method: "GET" }, CONFIG.WIKI_TIMEOUT_MS).then(function(r){
      if (!r.ok) throw new Error("wiki search " + r.status);
      return r.json();
    }).then(function(j){
      var hits = j && j.query && j.query.search;
      if (!hits || !hits.length) throw new Error("wiki no results");
      return hits;
    });
  }

  function wikiSummary(title){
    var url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + encodeURIComponent(title);
    return fetchTO(url, { method: "GET" }, CONFIG.WIKI_TIMEOUT_MS).then(function(r){
      if (!r.ok) throw new Error("wiki summary " + r.status);
      return r.json();
    }).then(function(j){
      if (!j || !j.extract) throw new Error("wiki empty");
      if (j.type === "disambiguation" || j.type === "no-extract") throw new Error("wiki thin");
      var extract = String(j.extract).trim();
      if (extract.length < 200) throw new Error("wiki short");
      return { title: j.title || title, extract: extract };
    });
  }

  function relevanceScore(question, title, extract){
    try {
      var qw = String(question||"").toLowerCase().match(/[a-z]{4,}/g) || [];
      if (qw.length === 0) return 0;
      var t = String(title||"").toLowerCase();
      var e = String(extract||"").toLowerCase();
      var hits = 0;
      for (var i=0; i<qw.length; i++){
        if (t.indexOf(qw[i]) > -1 || e.indexOf(qw[i]) > -1) hits++;
      }
      var score = hits / qw.length;
      if (t.indexOf(qw[0]) > -1) score += 0.15;
      return score;
    } catch(e){ return 0; }
  }

  function callWikipedia(q){
    return wikiSearch(q).then(function(hits){
      var best = null;
      var chain = Promise.resolve();
      hits.slice(0,3).forEach(function(h){
        chain = chain.then(function(){
          if (best) return;
          return wikiSummary(h.title).then(function(page){
            var score = relevanceScore(q, page.title, page.extract);
            if (score >= 0.5) best = { text: page.extract, score: score };
          }).catch(function(){});
        });
      });
      return chain.then(function(){
        if (!best) throw new Error("wiki weak match");
        return best.text;
      });
    });
  }

  /* ---------- GROQ ---------- */
  function callGroq(q){
    if (!CONFIG.GROQ_KEY || CONFIG.GROQ_KEY.indexOf("PASTE_") === 0) return Promise.reject(new Error("no groq"));
    return fetchTO(CONFIG.GROQ_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + CONFIG.GROQ_KEY },
      body: JSON.stringify({
        model: CONFIG.GROQ_MODEL,
        messages: [{ role: "system", content: CONFIG.SYS }, { role: "user", content: q }],
        temperature: 0.6, max_tokens: CONFIG.MAX_TOKENS
      })
    }, CONFIG.REQ_TIMEOUT_MS).then(function(r){
      if (!r.ok) throw new Error("groq " + r.status);
      return r.json();
    }).then(function(j){
      var txt = j && j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
      if (!txt) throw new Error("groq empty");
      return String(txt).trim();
    });
  }

  /* ---------- GEMINI ---------- */
  function callGemini(q){
    if (!CONFIG.GEMINI_KEY || CONFIG.GEMINI_KEY.indexOf("PASTE_") === 0) return Promise.reject(new Error("no gemini"));
    var url = CONFIG.GEMINI_URL + "?key=" + encodeURIComponent(CONFIG.GEMINI_KEY);
    return fetchTO(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: q }] }],
        systemInstruction: { parts: [{ text: CONFIG.SYS }] },
        generationConfig: { temperature: 0.6, maxOutputTokens: CONFIG.MAX_TOKENS }
      })
    }, CONFIG.REQ_TIMEOUT_MS).then(function(r){
      if (!r.ok) throw new Error("gemini " + r.status);
      return r.json();
    }).then(function(j){
      var c = j && j.candidates && j.candidates[0] && j.candidates[0].content;
      var txt = c && c.parts && c.parts[0] && c.parts[0].text;
      if (!txt) throw new Error("gemini empty");
      return String(txt).trim();
    });
  }

  /* ---------- ONLINE CHAIN ---------- */
  function onlineAnswer(q){
    var start = Promise.reject(new Error("start"));
    if (isWikiSuitable(q)) {
      start = callWikipedia(q).then(function(t){
        return { text: t, source: "wiki" };
      });
    }
    return start.catch(function(){
      return callGroq(q).then(function(t){
        return { text: t, source: "groq" };
      });
    }).catch(function(){
      return callGemini(q).then(function(t){
        return { text: t, source: "gemini" };
      });
    }).catch(function(){
      return { text: null, source: "none" };
    });
  }

  function isGenericFallback(replies){
    try {
      if (!replies || !replies.length) return true;
      var blob = replies.join(" ").toLowerCase();
      var signals = ["i am here","let me help you","try asking:","try asking ","i don't know","i dont know","i'm not sure","not sure about","i have no answer","no information"];
      for (var i=0; i<signals.length; i++) if (blob.indexOf(signals[i]) > -1) return true;
      if (blob.replace(/\s+/g,"").length < 60) return true;
      return false;
    } catch(e){ return false; }
  }

  if (typeof window.buildExpertReply === "function" && !window.__ajonOriginalBuildExpertReply) {
    window.__ajonOriginalBuildExpertReply = window.buildExpertReply;
  }

  var turnToken = 0;

  function appendBubble(text){
    try {
      var b = exAddBubble("ex", "");
      window.EXPERT.msgs.push({ s: "ex", t: text });
      exTypeInto(b, text, function(){});
    } catch(e){}
  }

  function sendLocalReplies(replies, myTurn){
    var idx = 0;
    function next(){
      if (myTurn !== turnToken) return;
      if (idx >= replies.length) { try { window.EXPERT.busy = false; } catch(e){} return; }
      var txt = replies[idx];
      var bb = exAddBubble("ex", "");
      window.EXPERT.msgs.push({ s: "ex", t: txt });
      exTypeInto(bb, txt, function(){ idx++; setTimeout(next, 120); });
    }
    next();
  }

  function install(){
    var helpers = ["byId","exAddBubble","exShowTyping","exTypeInto","exHideQuote"];
    for (var i=0; i<helpers.length; i++){
      if (typeof window[helpers[i]] !== "function") { try { console.warn("[V7] missing:", helpers[i]); } catch(e){} return false; }
    }
    if (typeof window.EXPERT === "undefined" || !window.EXPERT) { try { console.warn("[V7] EXPERT missing"); } catch(e){} return false; }

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

        /* 1. CACHE HIT */
        var cached = cacheGet(q);
        if (cached && cached.text) {
          var b1 = exAddBubble("ex", "");
          window.EXPERT.msgs.push({ s: "ex", t: cached.text });
          exTypeInto(b1, cached.text, function(){ window.EXPERT.busy = false; });
          var isOnline0 = true;
          try { isOnline0 = navigator.onLine !== false; } catch(e){}
          if (cached.src === "local" && isOnline0) {
            onlineAnswer(q).then(function(result){
              if (result && result.text) {
                cacheSet(q, result.text, result.source);
                if (myTurn === turnToken) appendBubble(result.text);
              }
            }).catch(function(){});
          }
          return;
        }

        /* 2. Build local reply */
        var localReplies = null;
        try { if (typeof window.__ajonOriginalBuildExpertReply === "function") localReplies = window.__ajonOriginalBuildExpertReply(q); } catch(e){}
        if (!localReplies || !localReplies.length) {
          localReplies = [
            "I am here. \uD83D\uDE42 Let me help you.",
            "Try asking: 'how do I make soap?' or 'how do I make honey?'",
            "Or a business term like 'cash flow' or 'profit margin'."
          ];
        }

        var isOnline = true;
        try { isOnline = navigator.onLine !== false; } catch(e){}

        /* 3. OFFLINE -> local instantly, no notice */
        if (!isOnline) {
          sendLocalReplies(localReplies, myTurn);
          if (!isGenericFallback(localReplies)) cacheSet(q, localReplies.join("\n\n"), "local");
          return;
        }

        /* 4. ONLINE -> Wikipedia (if suitable) -> Groq -> Gemini -> local. Silent. */
        var typing = exShowTyping();
        onlineAnswer(q).then(function(result){
          if (myTurn !== turnToken) return;
          if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
          if (result && result.text) {
            cacheSet(q, result.text, result.source);
            var bb = exAddBubble("ex", "");
            window.EXPERT.msgs.push({ s: "ex", t: result.text });
            exTypeInto(bb, result.text, function(){ try { window.EXPERT.busy = false; } catch(e){} });
          } else {
            sendLocalReplies(localReplies, myTurn);
            if (!isGenericFallback(localReplies)) cacheSet(q, localReplies.join("\n\n"), "local");
          }
        }).catch(function(){
          if (myTurn !== turnToken) return;
          if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
          sendLocalReplies(localReplies, myTurn);
          if (!isGenericFallback(localReplies)) cacheSet(q, localReplies.join("\n\n"), "local");
        });
      } catch(err){
        try { console.log("[V7] err", err); } catch(e){}
        try { if (window.EXPERT) window.EXPERT.busy = false; } catch(e){}
      }
    };

    try { console.log("[Ajon Hybrid V7] Wikipedia-suitable -> Groq -> Gemini -> local. Silent."); } catch(e){}
    return true;
  }

  var tries = 0;
  function attempt(){ if (install()) return; tries++; if (tries < 20) setTimeout(attempt, 500); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", attempt);
  else setTimeout(attempt, 400);
})();
