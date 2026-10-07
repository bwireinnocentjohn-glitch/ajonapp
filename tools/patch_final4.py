import io, sys, os

HTML = 'www/index.html'
WF = '.github/workflows/build.yml'

if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

def replace_function(src, func_name, new_func):
    marker = 'function ' + func_name + '('
    start = src.find(marker)
    if start == -1: return src, False
    brace = src.find('{', start)
    if brace == -1: return src, False
    depth = 0; i = brace
    while i < len(src):
        ch = src[i]
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + new_func + src[i+1:], True
        i += 1
    return src, False

# ============================================================
# FIX 1 — Unlock tab title: "Unlock All 500 Ideas" -> "Unlock All 1500+ Ideas"
# ============================================================
pairs = [
    ("Unlock All 500 Ideas", "Unlock All 1500+ Ideas"),
    ("Unlock All 500 ideas", "Unlock All 1500+ ideas"),
    ("Unlock 500 Ideas", "Unlock 1500+ Ideas"),
    ("500 Ideas", "1500+ Ideas"),
]
n = 0
for old, new in pairs:
    c = html.count(old)
    if c:
        html = html.replace(old, new)
        n += c
print("1. Unlock title: " + str(n) + " replacements")

# ============================================================
# FIX 2 — Price: 10,000 -> 15,000
# ============================================================
price_pairs = [
    ("amount: 10000", "amount: 15000"),
    ("amount:10000", "amount:15000"),
    ("10,000 UGX", "15,000 UGX"),
    ("10000 UGX", "15000 UGX"),
]
n2 = 0
for old, new in price_pairs:
    c = html.count(old)
    if c:
        html = html.replace(old, new)
        n2 += c
print("2. Price: " + str(n2) + " replacements")

# ============================================================
# FIX 3 — Category filter + renderCatBar (bulletproof)
# ============================================================
new_filter = '''function filterCat(cat) {
  try {
    cat = String(cat == null ? "all" : cat);
    currentCategory = cat;
    var chips = document.querySelectorAll(".cat-chip");
    for (var i = 0; i < chips.length; i++) {
      if (chips[i].getAttribute("data-cat") === cat) chips[i].classList.add("active");
      else chips[i].classList.remove("active");
    }
    tutOffset = 0;
    try { currentItems = []; } catch(e) {}
    renderTutorials(true);
  } catch (e) { try { console.log("filterCat error:", e); } catch(x) {} }
}'''
html, ok = replace_function(html, "filterCat", new_filter)
print("3a. filterCat: " + ("OK" if ok else "NOT FOUND"))

new_cat = '''function renderCatBar() {
  var bar = byId("catBar");
  if (!bar) return;
  var h = '<div class="cat-chip active" data-cat="all">All</div>';
  for (var i = 0; i < CATEGORIES.length; i++) {
    h += '<div class="cat-chip" data-cat="' + CATEGORIES[i].id + '">' + CATEGORIES[i].name + '</div>';
  }
  bar.innerHTML = h;
  if (bar._ajonCat) return;
  bar._ajonCat = true;
  bar.addEventListener("click", function(ev){
    try {
      var t = ev.target;
      while (t && t !== bar && !t.classList.contains("cat-chip")) t = t.parentNode;
      if (!t || t === bar) return;
      ev.preventDefault();
      ev.stopPropagation();
      var cat = t.getAttribute("data-cat");
      if (!cat) return;
      filterCat(cat);
    } catch(e) { try { console.log("cat click err:", e); } catch(x){} }
  }, true);
}'''
html, ok = replace_function(html, "renderCatBar", new_cat)
print("3b. renderCatBar: " + ("OK" if ok else "NOT FOUND"))

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

# ============================================================
# FIX 4 — Workflow: icon generation in correct order
# ============================================================
try:
    with io.open(WF, 'r', encoding='utf-8') as f:
        wf = f.read()

    # Remove any existing icon step first
    lines = wf.split("\n")
    cleaned = []
    skip = False
    for line in lines:
        if "Generate app icons" in line or "capacitor/assets generate" in line:
            skip = True
            continue
        if skip:
            if line.strip().startswith("- name:"):
                skip = False
                cleaned.append(line)
            # else skip this line
            continue
        cleaned.append(line)
    wf = "\n".join(cleaned)

    # Insert icon step right after "Sync web assets" step
    ICON_STEP = """      - name: Generate app icons
        run: npx --yes @capacitor/assets generate --android --assetPath resources || echo "icon assets skipped"

"""
    marker = "      - name: Make gradlew executable"
    if "Sync web assets" in wf and marker in wf and "capacitor/assets generate" not in wf:
        wf = wf.replace(marker, ICON_STEP + marker, 1)
        print("4. Workflow: icon step inserted after cap sync")
    else:
        print("4. Workflow: icon step already in place or marker missing")

    with io.open(WF, 'w', encoding='utf-8') as f:
        f.write(wf)
except Exception as e:
    print("4. Workflow update failed: " + str(e))

# ============================================================
# FIX 5 — Create resources folder if missing
# ============================================================
try:
    if not os.path.exists("resources"):
        os.makedirs("resources")
        print("5. resources/ folder created")
    else:
        print("5. resources/ already exists")
except Exception as e:
    print("5. resources/ create failed: " + str(e))

print("")
print("SUCCESS. Final 4 fixes applied.")
