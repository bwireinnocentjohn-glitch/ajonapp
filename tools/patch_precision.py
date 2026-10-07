import io, sys, os

JS = 'www/js/expertBrain.js'
HTML = 'www/index.html'

if not os.path.exists(JS):
    print("ERROR: expertBrain.js not found"); sys.exit(1)
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(JS, 'r', encoding='utf-8') as f:
    js = f.read()
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
# 1. Add STOPS + stopFilter to expertBrain.js (once)
# ============================================================
if "var STOPS =" not in js:
    syn_start = js.find("var SYN = {")
    if syn_start != -1:
        syn_end = js.find("};", syn_start) + 2
        INSERT = '''

  var STOPS = {
    "how":1,"do":1,"what":1,"is":1,"the":1,"a":1,"an":1,"can":1,
    "i":1,"my":1,"me":1,"you":1,"we":1,"they":1,"he":1,"she":1,
    "to":1,"for":1,"of":1,"in":1,"on":1,"at":1,"by":1,"with":1,
    "and":1,"or":1,"but":1,"if":1,"so":1,
    "this":1,"that":1,"these":1,"those":1,"it":1,"its":1,
    "be":1,"am":1,"are":1,"was":1,"were":1,"been":1,
    "make":1,"makes":1,"making":1,"made":1,
    "start":1,"starts":1,"starting":1,
    "want":1,"wants":1,"need":1,"needs":1,
    "give":1,"gives":1,"get":1,"gets":1,
    "help":1,"please":1,"tell":1,"show":1,"teach":1,"explain":1,
    "about":1,"from":1,"into":1,"than":1,"then":1,
    "any":1,"all":1,"some":1,"more":1,"most":1,
    "good":1,"best":1,"great":1,"nice":1
  };

  function stopFilter(s){
    return String(s||"").split(" ").filter(function(w){
      return w.length >= 2 && !STOPS[w];
    });
  }
'''
        js = js[:syn_end] + INSERT + js[syn_end:]
        print("1. STOPS + stopFilter added")
    else:
        print("WARN: SYN not found")
else:
    print("1. STOPS already present")

# ============================================================
# 2. Replace scoreBiz with phrase-priority version
# ============================================================
new_score = '''function scoreBiz(biz, qRaw){
    var q = norm(qRaw);
    var words = stopFilter(q);
    var nameLow = String(biz.name||"").toLowerCase();
    var hay = (biz.name + " " + biz.category + " " + (biz.whyNow||biz.whyNow2026||"") + " " + (biz.tags||[]).join(" ")).toLowerCase();
    var s = 0;

    if (words.length >= 2) {
      var phrase = words.join(" ");
      if (nameLow.indexOf(phrase) > -1) s += 100;
      else if (hay.indexOf(phrase) > -1) s += 20;
    }

    var nameHits = 0, hayHits = 0;
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      if (nameLow.indexOf(w) > -1) nameHits++;
      else if (hay.indexOf(w) > -1) hayHits++;
    }
    if (words.length > 0 && nameHits === words.length) s += 60;
    s += nameHits * 15;
    s += hayHits * 2;

    if (nameLow.length >= 4 && q.indexOf(nameLow) > -1) s += 80;

    return s;
  }'''

js, ok = replace_function(js, "scoreBiz", new_score)
print("2. scoreBiz: " + ("replaced" if ok else "NOT FOUND"))

# ============================================================
# 3. Raise the search threshold (drop noise)
# ============================================================
if "if (s >= 2) scored.push" in js:
    js = js.replace("if (s >= 2) scored.push", "if (s >= 8) scored.push")
    print("3. Threshold raised to 8")
elif "if (s >= 10) scored.push" in js:
    print("3. Threshold already 10")
else:
    print("3. WARN: threshold pattern not found")

with io.open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

# ============================================================
# 4. Random suggestion selection in index.html
# ============================================================
OLD_SEL = '''  var out = [];
  for (var i = 0; i < 6; i++) out.push(pool[(EXPERT.sugsIdx + i) % pool.length]);
  EXPERT.sugsIdx = (EXPERT.sugsIdx + 6) % pool.length;'''

NEW_SEL = '''  var picked = {};
  var out = [];
  var attempts = 0;
  while (out.length < 6 && attempts < 300) {
    attempts++;
    var ri = Math.floor(Math.random() * pool.length);
    if (!picked[ri]) { picked[ri] = 1; out.push(pool[ri]); }
  }'''

if OLD_SEL in html:
    html = html.replace(OLD_SEL, NEW_SEL, 1)
    print("4. Suggestion selection randomised")
else:
    print("4. WARN: suggestion selection pattern not found")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("")
print("SUCCESS. Precision + diverse suggestions applied.")
