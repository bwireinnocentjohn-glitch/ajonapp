import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# Helper: replace a JS function by matching braces (no regex)
# ============================================================
def replace_function(src, func_name, new_func_text):
    marker = 'function ' + func_name + '('
    start = src.find(marker)
    if start == -1:
        return src, False
    brace_start = src.find('{', start)
    if brace_start == -1:
        return src, False
    depth = 0
    i = brace_start
    n = len(src)
    while i < n:
        ch = src[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                return src[:start] + new_func_text + src[end:], True
        i += 1
    return src, False

# ============================================================
# 1. Counters: 500+ -> 1500+
# ============================================================
pairs = [
    ("500+ Ways To Make Money", "1500+ Ways To Make Money"),
    ("500+ Ways", "1500+ Ways"),
    ("500+ business ideas", "1500+ business ideas"),
    ("500+ ideas", "1500+ ideas"),
    ("500+ businesses", "1500+ businesses"),
    ("500+ tutorials", "1500+ tutorials"),
    ("Unlock 500+", "Unlock 1500+"),
    ("1500 business ideas", "1500+ business ideas"),
]
count_total = 0
for old, new in pairs:
    c = html.count(old)
    if c:
        html = html.replace(old, new)
        count_total += c
print("1. Counters replaced: " + str(count_total) + " places.")

# ============================================================
# 2. renderCatBar
# ============================================================
new_renderCatBar = '''function renderCatBar() {
  var bar = byId("catBar"); if (!bar) return;
  var html = '<div class="cat-chip active" data-cat="all">All</div>';
  for (var i = 0; i < CATEGORIES.length; i++) {
    html += '<div class="cat-chip" data-cat="' + CATEGORIES[i].id + '">' + CATEGORIES[i].name + '</div>';
  }
  bar.innerHTML = html;
  if (bar._ajonBound) return;
  bar._ajonBound = true;
  bar.addEventListener("click", function(ev){
    var chip = ev.target;
    while (chip && chip !== bar && !chip.classList.contains("cat-chip")) {
      chip = chip.parentNode;
    }
    if (!chip || chip === bar) return;
    ev.preventDefault();
    var cat = chip.getAttribute("data-cat");
    if (!cat) return;
    var chips = bar.querySelectorAll(".cat-chip");
    for (var j = 0; j < chips.length; j++) {
      chips[j].classList.toggle("active", chips[j].getAttribute("data-cat") === cat);
    }
    filterCat(cat);
  }, false);
}'''

html, ok = replace_function(html, "renderCatBar", new_renderCatBar)
print("2. renderCatBar: " + ("rewritten" if ok else "NOT FOUND"))

# ============================================================
# 3. toggleFav — use raw string with real emoji chars
# ============================================================
heart_full = "\u2764\ufe0f"
heart_empty = "\U0001F90D"

new_toggleFav = '''function toggleFav(id, ev) {
  if (ev && ev.stopPropagation) ev.stopPropagation();
  if (ev && ev.preventDefault) ev.preventDefault();
  var nid = Number(id);
  var idx = favs.indexOf(nid);
  var nowFav;
  if (idx > -1) { favs.splice(idx, 1); nowFav = false; }
  else { favs.push(nid); nowFav = true; }
  writeJSON(LS_FAV, favs);
  var iconFull = "%s";
  var iconEmpty = "%s";
  var btns = document.querySelectorAll('.fav[data-fav="' + nid + '"]');
  for (var k = 0; k < btns.length; k++) {
    btns[k].textContent = nowFav ? iconFull : iconEmpty;
    btns[k].classList.add("pop");
    (function(b){ setTimeout(function(){ b.classList.remove("pop"); }, 460); })(btns[k]);
  }
}''' % (heart_full, heart_empty)

html, ok = replace_function(html, "toggleFav", new_toggleFav)
print("3. toggleFav: " + ("rewritten" if ok else "NOT FOUND"))

# ============================================================
# 4. Exit handler
# ============================================================
EXIT_JS = """
/* ========== Robust exit confirmation ========== */
(function(){
  if (window.__ajonExitV2) return;
  window.__ajonExitV2 = true;

  var lastBack = 0;
  function doExit() {
    try {
      if (window.Capacitor && Capacitor.Plugins && Capacitor.Plugins.App && Capacitor.Plugins.App.exitApp) {
        Capacitor.Plugins.App.exitApp();
        return true;
      }
    } catch(e) {}
    try {
      if (navigator.app && navigator.app.exitApp) {
        navigator.app.exitApp();
        return true;
      }
    } catch(e) {}
    try { window.close(); return true; } catch(e) {}
    return false;
  }

  function askExit() {
    var now = Date.now();
    if (now - lastBack < 1500) { doExit(); return; }
    lastBack = now;
    var yes = false;
    try { yes = window.confirm("Exit Ajon? Tap OK to close."); } catch(e) { yes = true; }
    if (yes) doExit();
    else { try { history.pushState({a:1}, "", ""); } catch(e) {} }
  }

  try { history.pushState({a:1}, "", ""); } catch(e) {}

  window.addEventListener("popstate", function(e) {
    askExit();
  });

  document.addEventListener("keydown", function(e) {
    if (e.key === "Backspace" || e.keyCode === 8) {
      var t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      e.preventDefault();
      askExit();
    }
  }, false);
})();
"""
idx = html.rfind('</script>')
if idx == -1:
    print("ERR </script>"); sys.exit(1)
html = html[:idx] + EXIT_JS + '\n' + html[idx:]
print("4. Exit handler upgraded.")

# ============================================================
# 5. Back button CSS
# ============================================================
BACK_CSS = """
/* ========== Back button improvements ========== */
.back-btn {
  width: 42px !important;
  height: 42px !important;
  border-radius: 12px !important;
  background: linear-gradient(135deg, #00c853, #009624) !important;
  border: 2px solid #00ff99 !important;
  color: #ffffff !important;
  font-size: 22px !important;
  font-weight: 900 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: 0 3px 10px rgba(0,200,83,.45) !important;
  cursor: pointer !important;
  line-height: 1 !important;
  padding: 0 !important;
  flex: 0 0 auto !important;
}
.back-btn:active {
  transform: scale(.94) !important;
  box-shadow: 0 1px 4px rgba(0,200,83,.3) !important;
}
"""
idx2 = html.rfind('</style>')
if idx2 == -1:
    print("ERR </style>"); sys.exit(1)
html = html[:idx2] + BACK_CSS + '\n' + html[idx2:]
print("5. Back button CSS added.")

# ============================================================
# Save
# ============================================================
with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. All fixes applied.")
