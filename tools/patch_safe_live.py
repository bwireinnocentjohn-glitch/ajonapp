import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__SAFE_LIVE_V1__" in html:
    print("Already applied. Exiting."); sys.exit(0)

# Sanity: make sure app still has boot
if "hideSplash" not in html or "function boot(" not in html:
    print("ERROR: main app appears damaged. Restore from backup first.")
    sys.exit(1)

CSS = """
/* ===== SAFE LIVE V1 ===== */
.expert-watch {
  font-family: ui-monospace, Menlo, monospace;
  font-size: 11px;
  font-weight: 800;
  color: #00c853;
  background: rgba(0,200,83,.1);
  border: 1px solid rgba(0,200,83,.35);
  border-radius: 999px;
  padding: 3px 9px;
  letter-spacing: .3px;
  margin-left: 6px;
  flex: 0 0 auto;
  display: inline-block;
}
.likes-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(0,200,83,.1);
  border: 1px solid rgba(0,200,83,.35);
  color: #00c853;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 800;
  margin: 4px 0 8px;
  letter-spacing: .3px;
}
.kb-toggle {
  background: linear-gradient(135deg,#4ecdc4,#44a08d);
  border: 0;
  color: #fff;
  border-radius: 10px;
  width: 42px;
  height: 42px;
  font-size: 18px;
  cursor: pointer;
  flex: 0 0 auto;
  padding: 0;
  line-height: 1;
}
.kb-toggle:active { transform: scale(.95); }
.helper-kb {
  display: none;
  flex-direction: column;
  gap: 6px;
  padding: 8px;
  height: 300px;
  overflow: hidden;
  background: linear-gradient(135deg,#c9f0e0,#aee3f0);
  border: 1px solid #7cc5b8;
  border-radius: 14px;
  margin: 6px 12px 12px;
  box-shadow: 0 6px 18px rgba(0,0,0,.35);
}
.helper-kb.open { display: flex; }
.helper-kb-view { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 6px; }
.helper-kb-view.hidden { display: none; }
.helper-kb-sug { flex: 0 0 auto; display: flex; gap: 5px; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; }
.helper-kb-sug::-webkit-scrollbar { display: none; }
.kb-sug {
  flex: 0 0 auto; background: #fff; border: 1px solid #7cc5b8; color: #0d5e4f;
  border-radius: 8px; padding: 6px 11px; font-size: 12px; font-weight: 700;
  cursor: pointer; font-family: inherit;
}
.kb-sug:active { background: #a8e6d4; }
.kb-pred { flex: 1 1 auto; display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 1fr; gap: 5px; overflow-y: auto; }
.kb-pred-btn {
  background: #fff; border: 1px solid #7cc5b8; color: #0d5e4f; border-radius: 8px;
  padding: 6px 4px; font-size: 12px; font-weight: 700; cursor: pointer;
  font-family: inherit; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.kb-pred-btn:active { background: #a8e6d4; }
.kb-calc { flex: 1 1 auto; display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: 1fr; gap: 5px; }
.kb-calc-display {
  grid-column: 1 / -1; background: #fff; border: 1px solid #7cc5b8; border-radius: 10px;
  padding: 8px 10px; text-align: right; font-family: ui-monospace, Menlo, monospace;
  font-size: 15px; font-weight: 800; color: #0d5e4f; overflow: hidden;
  white-space: nowrap; text-overflow: ellipsis;
}
.calc-btn {
  background: #fff; border: 1px solid #7cc5b8; color: #0d5e4f; border-radius: 8px;
  padding: 0; font-size: 15px; font-weight: 800; cursor: pointer; font-family: inherit;
}
.calc-btn:active { background: #a8e6d4; }
.calc-btn.op { background: #d8f0e8; }
.calc-btn.eq { background: linear-gradient(135deg,#4ecdc4,#44a08d); color: #fff; border-color: #44a08d; }
.calc-btn.cmd { background: #ffe0dc; color: #b3261e; border-color: #f4a09a; }
.calc-btn.wide { grid-column: span 2; }
.helper-kb-ctrl { flex: 0 0 auto; display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; }
.kb-ctrl {
  background: #fff; border: 1px solid #7cc5b8; color: #0d5e4f; border-radius: 8px;
  padding: 9px 0; font-size: 15px; font-weight: 800; cursor: pointer; font-family: inherit;
}
.kb-ctrl:active { background: #a8e6d4; }
.kb-ctrl.flip { background: linear-gradient(135deg,#4ecdc4,#44a08d); color: #fff; border-color: #44a08d; }
"""

JS = r'''
/* __SAFE_LIVE_V1__ */
(function(){
  "use strict";
  function byId(id){ return document.getElementById(id); }
  function $(s){ return document.querySelector(s); }
  function $$(s){ return document.querySelectorAll(s); }

  /* ============ LIKES ============ */
  var LK_KEY = "ajon_likes_install_v4";
  var installTime = 0;
  try { installTime = Number(localStorage.getItem(LK_KEY)) || 0; } catch(e){}
  if (!installTime) {
    installTime = Date.now();
    try { localStorage.setItem(LK_KEY, String(installTime)); } catch(e){}
  }
  function hashTitle(s){
    s = String(s||""); var h = 0;
    for (var i=0; i<s.length; i++){ h = ((h<<5)-h)+s.charCodeAt(i); h |= 0; }
    return Math.abs(h);
  }
  function formatLikes(n){
    n = Math.max(0, Number(n)||0);
    if (n >= 1000000) return (n/1000000).toFixed(1)+"M";
    if (n >= 1000) return (n/1000).toFixed(1)+"k";
    return String(Math.floor(n));
  }
  function computeLikes(title){
    var seed = hashTitle(title);
    var base = 10000 + (seed % 10000);
    var ratePerHour = 20000 + (seed % 50000);
    var elapsedHours = (Date.now() - installTime) / 3600000;
    return base + Math.floor(elapsedHours * ratePerHour);
  }
  function ensureLikeBadges(){
    try {
      var cards = $$(".card");
      for (var i=0; i<cards.length; i++){
        var card = cards[i];
        var titleEl = card.querySelector(".card-title");
        if (!titleEl) continue;
        var title = titleEl.textContent.trim();
        var likes = computeLikes(title);
        var text = "\u2764\uFE0F " + formatLikes(likes) + " likes";
        var existing = card.querySelector(".likes-badge");
        if (existing) { existing.textContent = text; continue; }
        var badge = document.createElement("div");
        badge.className = "likes-badge";
        badge.textContent = text;
        var chip = card.querySelector(".chip");
        if (chip && chip.parentNode === card) {
          chip.parentNode.insertBefore(badge, chip.nextSibling);
        } else {
          titleEl.parentNode.insertBefore(badge, titleEl.nextSibling);
        }
      }
    } catch(e){}
  }

  /* ============ WATCH ============ */
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

  /* ============ KEYBOARD + CALCULATOR ============ */
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
        renderPred("", true);
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
    try { ensureLikeBadges(); } catch(e){}
    try { ensureWatch(); } catch(e){}
    try { bindInputPredict(); } catch(e){}

    try {
      var list = byId("tutList");
      if (list && !list._ajonSafeObs) {
        list._ajonSafeObs = new MutationObserver(function(){
          try { ensureLikeBadges(); } catch(e){}
        });
        list._ajonSafeObs.observe(list, { childList:true, subtree:true });
      }
    } catch(e){}

    setInterval(function(){ try { ensureLikeBadges(); } catch(e){} }, 5000);
    setInterval(function(){ try { ensureWatch(); } catch(e){} }, 1000);
    setInterval(function(){ try { if (KB.open && KB.mode === "words" && Math.random() < 0.15) renderQuick(); } catch(e){} }, 8000);

    try { console.log("[Ajon Safe Live] Loaded"); } catch(e){}
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    setTimeout(init, 400);
  }
})();
'''

# === 1. Insert CSS before last </style> ===
sidx = html.rfind('</style>')
if sidx == -1:
    print("ERROR: </style> not found"); sys.exit(1)
html = html[:sidx] + CSS + "\n" + html[sidx:]
print("1. CSS added before last </style>")

# === 2. Insert new SCRIPT right before </body> ===
if "</body>" not in html:
    print("ERROR: </body> not found"); sys.exit(1)
SCRIPT_TAG = "<script>\n" + JS + "\n</script>\n<!-- __SAFE_LIVE_V1__ -->\n"
html = html.replace("</body>", SCRIPT_TAG + "</body>", 1)
print("2. New <script> added before </body>")

# === 3. Sanity check: main functions untouched ===
for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment"]:
    if fn not in html:
        print("ERROR: " + fn + " missing — aborting write"); sys.exit(1)
print("3. Main app functions verified intact")

# === 4. Atomic write ===
tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("")
print("SUCCESS. Safe live features installed.")
