import io, sys, os
HTML = 'www/index.html'
JS_F = 'tools/hybrid_expert_v7.js'
DRY = '--dry-run' in sys.argv

with io.open(HTML, 'r', encoding='utf-8') as f: html = f.read()

if "__HYBRID_EXPERT_V7__" in html:
    print("V7 already applied."); sys.exit(0)

required = ["function boot(", "hideSplash", "askExpert", "renderTutorials",
            "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__"]
for fn in required:
    if fn not in html: print("ERROR: " + fn + " missing"); sys.exit(1)
print("0. Required markers present")

for v in ["V2","V3","V4","V5","V6"]:
    mark = "<!-- __HYBRID_EXPERT_" + v + "__ -->"
    mi = html.find(mark)
    if mi != -1:
        so = html.rfind("<script>", 0, mi)
        if so != -1:
            end = mi + len(mark)
            if end < len(html) and html[end] == '\n': end += 1
            html = html[:so] + html[end:]
            print("1. Removed old " + v)

mark = "<!-- __API_DEBUG_V1__ -->"
mi = html.find(mark)
if mi != -1:
    so = html.rfind("<script>", 0, mi)
    if so != -1:
        end = mi + len(mark)
        if end < len(html) and html[end] == '\n': end += 1
        html = html[:so] + html[end:]
        print("2. Removed API debug pill")

with io.open(JS_F, 'r', encoding='utf-8') as f: js = f.read()
if "</body>" not in html: print("ERROR: </body> missing"); sys.exit(1)

BLOCK = "<script>\n" + js + "\n</script>\n<!-- __HYBRID_EXPERT_V7__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("3. V7 injected")

for fn in required + ["__HYBRID_EXPERT_V7__"]:
    if fn not in html: print("ERROR: " + fn + " lost"); sys.exit(1)
print("4. Markers intact")

if DRY:
    print(""); print("DRY RUN OK. Would write %d bytes." % len(html)); sys.exit(0)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f: f.write(html)
os.replace(tmp, HTML)
print(""); print("SUCCESS. Hybrid V7 installed.")
