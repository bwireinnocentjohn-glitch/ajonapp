/* __SAFE_LIVE_V2__ */
(function(){
  "use strict";
  function byId(id){ return document.getElementById(id); }
  function $(s){ return document.querySelector(s); }

  /* ===== WATCH (expert header only) ===== */
  function ensureWatch(){
    try {
      var hdr = $(".expert-header");
      if (!hdr) return;
      var w = hdr.querySelector(".expert-watch");
      if (!w) {
        w = document.createElement("span");
        w.className = "expert-watch";
        hdr.appendChild(w);
      }
      var d = new Date();
      var hh = d.getHours(), mm = d.getMinutes(), ss = d.getSeconds();
      var ap = hh >= 12 ? "PM" : "AM";
      hh = hh % 12; if (hh === 0) hh = 12;
      if (mm < 10) mm = "0"+mm;
      if (ss < 10) ss = "0"+ss;
      w.textContent = "\uD83D\uDD50 " + hh + ":" + mm + ":" + ss + " " + ap;
    } catch(e){}
  }

  /* ===== KEYBOARD + CALCULATOR (expert input row + main) ===== */
  var WORDS_RAW = ["soap","honey","beeswax","oil","compost","biogas","solar","candle",
    "yoghurt","bread","cake","samosa","juice","jam","tea","spice","paper","glass",
    "plastic","grow","make","sell","start","price","profit","capital","mask","brush",
    "ghee","jelly","cheese","butter","peanut","ginger","garlic","turmeric","aloe",
    "neem","shea","coconut","cricket","mushroom","bees","rabbit","chicken","fish",
    "goat","pig","liquid","bar","black","charcoal","herbal","detergent","bleach",
    "briquette","filter","stove","sauce","sugar","candy","snack","yarn"];
  var WORDS = []; var seenW = {};
  for (var wi=0; wi<WORDS_RAW.length; wi++) if (!seenW[WORDS_RAW[wi]]) { seenW[WORDS_RAW[wi]]=1; WORDS.push(WORDS_RAW[wi]); }

  var KB = { open:false, mode:"words", expr:"" };

  function ensureKbToggle(){
    try {
      var row = $(".expert-input-row");
      if (!row) return;
      if (row.querySelector(".kb-toggle")) return;
      var btn = document.createElement("button");
      btn.className = "kb-toggle";
      btn.type = "button";
      btn.textContent = "\u2328\uFE0F";
      btn.onclick = function(){ window.kbToggle(); };
      row.appendChild(btn);
    } catch(e){}
  }

  function ensureKbPanel(){
    try {
      var main = $(".expert-main");
      if (!main) return;
      var panel = byId("helperKb");
      if (!panel) {
        panel = document.createElement("div");
        panel.id = "helperKb";
        panel.className = "helper-kb";
        main.appendChild(panel);
      }
      if (!panel.querySelector(".helper-kb-ctrl")) {
        panel.innerHTML =
          '<div class="helper-kb-view" id="helperKbWords">' +
          '  <div class="helper-kb-sug" id="helperKbSug"></div>' +
          '  <div class="kb-pred" id="helperKbPred"></div>' +
          '</div>' +
          '<div class="helper-kb-view hidden" id="helperKbCalc">' +
          '  <div class="kb-calc" id="kbCalcGrid"></div>' +
          '</div>' +
          '<div class="helper-kb-ctrl">' +
          '  <button class="kb-ctrl" type="button" onclick="helperKbCopy()" title="Copy">\uD83D\uDCCB</button>' +
          '  <button class="kb-ctrl" type="button" onclick="helperKbPaste()" title="Paste">\uD83D\uDCE5</button>' +
          '  <button class="kb-ctrl" type="button" onclick="helperKbSpace()" title="Space">\u2423</button>' +
          '  <button class="kb-ctrl" type="button" onclick="helperKbBack()" title="Backspace">\u232B</button>' +
          '  <button class="kb-ctrl flip" id="helperKbFlipBtn" type="button" onclick="helperKbFlip()" title="Flip">\uD83D\uDD22</button>' +
          '</div>';
        renderQuick();
        renderPred("");
        renderCalcGrid();
      }
    } catch(e){}
  }

  function renderQuick(){
    try {
      var wrap = byId("helperKbSug"); if (!wrap) return;
      var start = Math.floor(Math.random() * WORDS.length);
      var out = "";
      for (var i=0; i<6; i++) {
        var w = WORDS[(start+i) % WORDS.length];
        out += '<button class="kb-sug" type="button" onclick="helperKbInsertWord(\'' + w + '\')">' + w + '</button>';
      }
      wrap.innerHTML = out;
    } catch(e){}
  }

  function renderPred(query){
    try {
      var wrap = byId("helperKbPred"); if (!wrap) return;
      var q = String(query||"").toLowerCase().trim();
      var matches = [];
      if (q) {
        for (var i=0; i<WORDS.length; i++) {
          if (WORDS[i].indexOf(q) === 0) matches.push(WORDS[i]);
          if (matches.length >= 12) break;
        }
        if (!matches.length) {
          for (var k=0; k<WORDS.length; k++) {
            if (WORDS[k].indexOf(q) > -1) matches.push(WORDS[k]);
            if (matches.length >= 12) break;
          }
        }
      } else {
        for (var j=0; j<WORDS.length && j<12; j++) matches.push(WORDS[j]);
      }
      if (!matches.length) matches = WORDS.slice(0, 12);
      var out = "";
      for (var m=0; m<matches.length; m++) {
        out += '<button class="kb-pred-btn" type="button" onclick="helperKbInsertWord(\'' + matches[m] + '\')">' + matches[m] + '</button>';
      }
      wrap.innerHTML = out;
    } catch(e){}
  }

  function renderCalcGrid(){
    try {
      var grid = byId("kbCalcGrid"); if (!grid) return;
      grid.innerHTML =
        '<div class="kb-calc-display" id="kbCalcDisplay">0</div>' +
        '<button class="calc-btn cmd" type="button" onclick="calcInput(\'C\')">C</button>' +
        '<button class="calc-btn cmd" type="button" onclick="calcInput(\'%\')">%</button>' +
        '<button class="calc-btn cmd" type="button" onclick="calcInput(\'BACK\')">\u232B</button>' +
        '<button class="calc-btn op" type="button" onclick="calcInput(\'/\')">\u00F7</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'7\')">7</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'8\')">8</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'9\')">9</button>' +
        '<button class="calc-btn op" type="button" onclick="calcInput(\'*\')">\u00D7</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'4\')">4</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'5\')">5</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'6\')">6</button>' +
        '<button class="calc-btn op" type="button" onclick="calcInput(\'-\')">\u2212</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'1\')">1</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'2\')">2</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'3\')">3</button>' +
        '<button class="calc-btn op" type="button" onclick="calcInput(\'+\')">+</button>' +
        '<button class="calc-btn wide" type="button" onclick="calcInput(\'0\')">0</button>' +
        '<button class="calc-btn" type="button" onclick="calcInput(\'.\')">.</button>' +
        '<button class="calc-btn eq" type="button" onclick="calcInput(\'=\')">=</button>' +
        '<button class="calc-btn eq wide" type="button" onclick="calcUse()">USE</button>';
    } catch(e){}
  }

  window.kbToggle = function(){
    var panel = byId("helperKb"); if (!panel) return;
    KB.open = !KB.open;
    panel.classList.toggle("open", KB.open);
    if (KB.open && KB.mode === "words") {
      var inp = byId("aiInput");
      renderPred(inp ? inp.value : "");
    }
  };

  window.helperKbInsertWord = function(w){
    var inp = byId("aiInput"); if (!inp) return;
    var v = inp.value || "";
    var parts = v.split(/(\s+)/);
    var replaced = false;
    for (var i = parts.length - 1; i >= 0; i--) {
      if (parts[i] && !/^\s+$/.test(parts[i])) { parts[i] = w; replaced = true; break; }
    }
    inp.value = (replaced ? parts.join("") : v) + " ";
    inp.focus();
    renderPred(w);
  };

  window.helperKbCopy = function(){
    var inp = byId("aiInput"); if (!inp || !inp.value) return;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(inp.value);
        toast("Copied");
      } else {
        inp.select(); document.execCommand("copy"); toast("Copied");
      }
    } catch(e) {
      try { inp.select(); document.execCommand("copy"); toast("Copied"); } catch(x){}
    }
  };

  window.helperKbPaste = function(){
    var inp = byId("aiInput"); if (!inp) return;
    inp.focus();
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        navigator.clipboard.readText().then(function(t){
          if (t) inp.value = (inp.value || "") + t;
          renderPred(inp.value || "");
          toast("Pasted");
        }).catch(function(){ toast("Long-press input to paste"); });
      } else {
        toast("Long-press input to paste");
      }
    } catch(e) { toast("Long-press input to paste"); }
  };

  window.helperKbSpace = function(){ var inp = byId("aiInput"); if (inp) { inp.value = (inp.value||"") + " "; inp.focus(); } };
  window.helperKbBack = function(){ var inp = byId("aiInput"); if (inp) { inp.value = (inp.value||"").slice(0,-1); inp.focus(); renderPred(inp.value||""); } };

  window.helperKbFlip = function(){
    var words = byId("helperKbWords"), calc = byId("helperKbCalc"), btn = byId("helperKbFlipBtn");
    if (!words || !calc) return;
    if (KB.mode === "words") {
      KB.mode = "calc";
      words.classList.add("hidden");
      calc.classList.remove("hidden");
      if (btn) btn.textContent = "\u2328\uFE0F";
    } else {
      KB.mode = "words";
      calc.classList.add("hidden");
      words.classList.remove("hidden");
      if (btn) btn.textContent = "\uD83D\uDD22";
      var inp = byId("aiInput"); renderPred(inp ? inp.value : "");
    }
  };

  function calcEval(expr){
    if (!expr) return "0";
    expr = String(expr).replace(/[+\-*/.%\s]+$/, "");
    if (!expr) return "0";
    if (!/^[0-9+\-*/().%\s]+$/.test(expr)) return "Error";
    try {
      var r = Function('"use strict"; return (' + expr + ')')();
      if (typeof r !== "number" || !isFinite(r)) return "Error";
      return String(Math.round(r * 1000000) / 1000000);
    } catch(e) { return "Error"; }
  }
  window.calcInput = function(k){
    if (k === "C") KB.expr = "";
    else if (k === "BACK") KB.expr = KB.expr.slice(0,-1);
    else if (k === "=") KB.expr = String(calcEval(KB.expr));
    else KB.expr += k;
    var d = byId("kbCalcDisplay"); if (d) d.textContent = KB.expr || "0";
  };
  window.calcUse = function(){
    var inp = byId("aiInput"); if (!inp) return;
    inp.value = (inp.value || "") + String(calcEval(KB.expr));
    inp.focus(); toast("Sent to input");
  };

  function toast(msg){
    var t = byId("ajonToastSafe");
    if (!t) {
      t = document.createElement("div");
      t.id = "ajonToastSafe";
      t.style.cssText = "position:fixed;bottom:150px;left:50%;transform:translateX(-50%);background:#4ecdc4;color:#00332a;padding:8px 16px;border-radius:999px;font-size:13px;font-weight:800;z-index:9999;opacity:0;transition:opacity .2s;pointer-events:none;";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = "1";
    clearTimeout(t._tid);
    t._tid = setTimeout(function(){ t.style.opacity = "0"; }, 1400);
  }

  function bindInputPredict(){
    try {
      var inp = byId("aiInput");
      if (!inp || inp._ajonSafe) return;
      inp._ajonSafe = true;
      inp.addEventListener("input", function(){
        if (!KB.open || KB.mode !== "words") return;
        var parts = (inp.value || "").split(/\s+/);
        var last = parts.length ? parts[parts.length-1] : "";
        renderPred(last);
      });
    } catch(e){}
  }

  function init(){
    try { ensureKbToggle(); } catch(e){}
    try { ensureKbPanel(); } catch(e){}
    try { ensureWatch(); } catch(e){}
    try { bindInputPredict(); } catch(e){}

    setInterval(function(){ try { ensureWatch(); } catch(e){} }, 1000);
    setInterval(function(){ try { if (KB.open && KB.mode === "words" && Math.random() < 0.15) renderQuick(); } catch(e){} }, 8000);

    try { console.log("[Ajon Safe Live V2] Loaded"); } catch(e){}
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 400);
  }
})();
