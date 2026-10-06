import io, sys, os

HTML = 'www/index.html'
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
# FIX 1 — Category sort buttons (event delegation)
# ============================================================
new_cat = '''function renderCatBar() {
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
    while (chip && chip !== bar && !chip.classList.contains("cat-chip")) chip = chip.parentNode;
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
html, ok = replace_function(html, "renderCatBar", new_cat)
print("1. Categories: " + ("FIXED" if ok else "NOT FOUND"))

# ============================================================
# FIX 2 — Assistant chat stuck repeating
#   2a. Bump state key so old state auto-clears on next launch
#   2b. Rewrite nextTopicV9 with bigger pool for no loops
# ============================================================
for old_key in ['"ajon_chat_v9"', '"ajon_chat_v8"', '"ajon_chat_v5"']:
    if old_key in html:
        html = html.replace(old_key, '"ajon_chat_v10"')
        print("2a. State key bumped to v10.")

new_next = '''function nextTopicV9() {
  var tid = BRAIN.currentTopicId || TOPIC_IDS[0];
  var t = TOPICS[tid];
  var recent = BRAIN.lastTopics || [];
  var pool = TOPIC_IDS.filter(function(x){ return recent.indexOf(x) === -1; });
  if (!pool.length) pool = TOPIC_IDS.slice();
  if (t && t.next && t.next.length) {
    var fresh = t.next.filter(function (x) { return recent.indexOf(x) === -1 && TOPICS[x]; });
    if (fresh.length) {
      var nxt = fresh[Math.floor(Math.random() * fresh.length)];
      BRAIN.lastTopics = recent.concat([nxt]).slice(-20);
      return nxt;
    }
  }
  var pick = pool[Math.floor(Math.random() * pool.length)];
  BRAIN.lastTopics = recent.concat([pick]).slice(-20);
  return pick;
}'''
html, ok = replace_function(html, "nextTopicV9", new_next)
print("2b. nextTopicV9: " + ("FIXED" if ok else "NOT FOUND"))

# ============================================================
# FIX 3 — Exit notification (Capacitor backButton)
# Remove old handlers, install new one
# ============================================================
# Remove any previous exit handler blocks we added
for marker in [
    "/* ========== Robust exit confirmation ========== */",
    "/* ===== Exit confirmation ===== */",
    "/* ========== Exit confirmation (Capacitor aware) ========== */",
]:
    while marker in html:
        i = html.find(marker)
        e = html.find("})();", i)
        if e == -1: break
        html = html[:i] + html[e+5:]

EXIT_JS = """
/* ========== Exit confirmation ========== */
(function(){
  if (window.__ajonExitV4) return;
  window.__ajonExitV4 = true;

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
    var yes = false;
    try { yes = window.confirm("Exit Ajon? Tap OK to close."); } catch(e) { yes = true; }
    if (yes) doExit();
    else { try { history.pushState({a:1}, "", ""); } catch(e) {} }
  }

  /* Capacitor native back button (most reliable) */
  try {
    if (window.Capacitor && Capacitor.Plugins && Capacitor.Plugins.App) {
      Capacitor.Plugins.App.addListener("backButton", function(){ askExit(); });
    }
  } catch(e) {}

  /* Web fallback */
  try { history.pushState({a:1}, "", ""); } catch(e) {}
  window.addEventListener("popstate", askExit);
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
print("3. Exit handler: FIXED")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Only 3 fixes applied.")
