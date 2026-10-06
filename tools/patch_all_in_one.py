import io, sys, os, json

HTML = 'www/index.html'
PKG = 'package.json'
WF = '.github/workflows/build.yml'

if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

def replace_function(src, func_name, new_func):
    marker = 'function ' + func_name + '('
    start = src.find(marker)
    if start == -1:
        return src, False
    brace = src.find('{', start)
    if brace == -1:
        return src, False
    depth = 0
    i = brace
    while i < len(src):
        ch = src[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + new_func + src[i+1:], True
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
]
n = 0
for old, new in pairs:
    c = html.count(old)
    if c:
        html = html.replace(old, new)
        n += c
print("1. Counters replaced: " + str(n))

# ============================================================
# 2. Category bar — inline onclick + delegation (both)
# ============================================================
new_cat = '''function renderCatBar() {
  var bar = byId("catBar"); if (!bar) return;
  var html = '<div class="cat-chip active" data-cat="all" onclick="filterCat(\\'all\\')">All</div>';
  for (var i = 0; i < CATEGORIES.length; i++) {
    html += '<div class="cat-chip" data-cat="' + CATEGORIES[i].id + '" onclick="filterCat(\\'' + CATEGORIES[i].id + '\\')">' + CATEGORIES[i].name + '</div>';
  }
  bar.innerHTML = html;
  if (bar._ajonBound) return;
  bar._ajonBound = true;
  bar.addEventListener("click", function(ev){
    var chip = ev.target;
    while (chip && chip !== bar && !chip.classList.contains("cat-chip")) chip = chip.parentNode;
    if (!chip || chip === bar) return;
    var cat = chip.getAttribute("data-cat");
    if (!cat) return;
    var chips = bar.querySelectorAll(".cat-chip");
    for (var j = 0; j < chips.length; j++) {
      chips[j].classList.toggle("active", chips[j].getAttribute("data-cat") === cat);
    }
    try { filterCat(cat); } catch (e) { console.log("filterCat err", e); }
  }, false);
}'''
html, ok = replace_function(html, "renderCatBar", new_cat)
print("2. renderCatBar: " + ("OK" if ok else "NOT FOUND"))

# ============================================================
# 3. filterCat — defensive
# ============================================================
new_filter = '''function filterCat(cat) {
  try {
    currentCategory = cat;
    var chips = document.querySelectorAll(".cat-chip");
    for (var i = 0; i < chips.length; i++) {
      chips[i].classList.toggle("active", chips[i].getAttribute("data-cat") === cat);
    }
    tutOffset = 0;
    renderTutorials(true);
  } catch (e) { console.log("filterCat error:", e); }
}'''
html, ok = replace_function(html, "filterCat", new_filter)
print("3. filterCat: " + ("OK" if ok else "NOT FOUND"))

# ============================================================
# 4. Favorites — bulletproof toggleFav + isFav
# ============================================================
new_isFav = '''function isFav(id) {
  try {
    if (!Array.isArray(favs)) favs = [];
    return favs.indexOf(Number(id)) > -1;
  } catch (e) { return false; }
}'''
html, ok = replace_function(html, "isFav", new_isFav)
print("4a. isFav: " + ("OK" if ok else "NOT FOUND"))

# toggleFav uses String.fromCodePoint — no unicode escapes needed
new_toggle = '''function toggleFav(id, ev) {
  if (ev && ev.stopPropagation) ev.stopPropagation();
  if (ev && ev.preventDefault) ev.preventDefault();
  try {
    if (!Array.isArray(favs)) favs = [];
    var nid = Number(id);
    var idx = favs.indexOf(nid);
    var nowFav;
    if (idx > -1) { favs.splice(idx, 1); nowFav = false; }
    else { favs.push(nid); nowFav = true; }
    writeJSON(LS_FAV, favs);
    var iconFull = String.fromCodePoint(0x2764, 0xFE0F);
    var iconEmpty = String.fromCodePoint(0x1F90D);
    var btns = document.querySelectorAll('.fav[data-fav="' + nid + '"]');
    for (var k = 0; k < btns.length; k++) {
      btns[k].textContent = nowFav ? iconFull : iconEmpty;
      btns[k].classList.add("pop");
      (function(b){ setTimeout(function(){ b.classList.remove("pop"); }, 460); })(btns[k]);
    }
  } catch (e) { console.log("toggleFav error:", e); }
}'''
html, ok = replace_function(html, "toggleFav", new_toggle)
print("4b. toggleFav: " + ("OK" if ok else "NOT FOUND"))

# ============================================================
# 5. Chat state key bump
# ============================================================
for k in ['"ajon_chat_v9"','"ajon_chat_v8"','"ajon_chat_v5"','"ajon_chat_v10"']:
    if k in html:
        html = html.replace(k, '"ajon_chat_v11"')
print("5. Chat state key -> v11")

# ============================================================
# 6. Exit handler — remove old, add new
# ============================================================
for marker in [
    "/* ========== Robust exit confirmation ========== */",
    "/* ===== Exit confirmation ===== */",
    "/* ========== Exit confirmation (Capacitor aware) ========== */",
    "/* ========== Exit confirmation ========== */",
]:
    while marker in html:
        i = html.find(marker)
        e = html.find("})();", i)
        if e == -1: break
        html = html[:i] + html[e+5:]

EXIT_JS = """
/* ========== Exit confirmation ========== */
(function(){
  if (window.__ajonExitV5) return;
  window.__ajonExitV5 = true;

  var lastBack = 0;

  function doExit() {
    try {
      if (window.Capacitor && Capacitor.Plugins && Capacitor.Plugins.App && Capacitor.Plugins.App.exitApp) {
        Capacitor.Plugins.App.exitApp();
        return;
      }
    } catch(e) {}
    try { if (navigator.app && navigator.app.exitApp) { navigator.app.exitApp(); return; } } catch(e) {}
    try { window.close(); } catch(e) {}
  }

  function askExit() {
    var now = Date.now();
    if (now - lastBack < 1200) { doExit(); return; }
    lastBack = now;
    var yes = false;
    try { yes = window.confirm("Exit Ajon? Tap OK to close."); } catch(e) { yes = true; }
    if (yes) doExit();
    else { try { history.pushState({a:1}, "", ""); } catch(e) {} }
  }

  /* PRIMARY: Capacitor native back button */
  function wireCapacitor() {
    try {
      if (window.Capacitor && Capacitor.Plugins && Capacitor.Plugins.App && Capacitor.Plugins.App.addListener) {
        Capacitor.Plugins.App.addListener("backButton", function(){ askExit(); });
        return true;
      }
    } catch(e) {}
    return false;
  }

  /* Wait for Capacitor to be ready (it may load after us) */
  var tries = 0;
  var waitId = setInterval(function(){
    tries++;
    if (wireCapacitor() || tries > 40) clearInterval(waitId);
  }, 100);

  /* WEB FALLBACK: popstate + keydown */
  try { history.pushState({a:1}, "", ""); } catch(e) {}
  window.addEventListener("popstate", function(){ askExit(); });
  document.addEventListener("keydown", function(e){
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
if idx == -1: print("ERR </script>"); sys.exit(1)
html = html[:idx] + EXIT_JS + '\n' + html[idx:]
print("6. Exit handler installed")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

# ============================================================
# 7. package.json — add @capacitor/app + assets
# ============================================================
try:
    with io.open(PKG, 'r', encoding='utf-8') as f:
        pkg = json.load(f)
    pkg.setdefault("dependencies", {})
    pkg["dependencies"]["@capacitor/app"] = "6.0.0"
    pkg.setdefault("devDependencies", {})
    pkg["devDependencies"]["@capacitor/assets"] = "3.0.5"
    with io.open(PKG, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2)
    print("7. package.json updated")
except Exception as e:
    print("7. package.json update failed: " + str(e))

# ============================================================
# 8. Workflow — add icon generation step
# ============================================================
try:
    with io.open(WF, 'r', encoding='utf-8') as f:
        wf = f.read()
    if "capacitor-assets generate" not in wf and "capacitor/assets" not in wf:
        add = '''      - name: Generate app icons
        run: npx @capacitor/assets generate --android || echo "Icon gen skipped"

'''
        marker = "      - name: Add Capacitor Android platform"
        if marker in wf:
            wf = wf.replace(marker, add + marker, 1)
            with io.open(WF, 'w', encoding='utf-8') as f:
                f.write(wf)
            print("8. Workflow: icon step added")
        else:
            print("8. Workflow: marker not found")
    else:
        print("8. Workflow: already has icon step")
except Exception as e:
    print("8. Workflow update failed: " + str(e))

print("")
print("SUCCESS. All fixes applied.")
