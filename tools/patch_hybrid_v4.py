import io, sys, os

HTML = 'www/index.html'
JS_F = 'tools/hybrid_expert_v4.js'
DRY = '--dry-run' in sys.argv

if not os.path.exists(HTML):
    print("ERROR: index.html missing"); sys.exit(1)
if not os.path.exists(JS_F):
    print("ERROR: hybrid_expert_v4.js missing"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__HYBRID_EXPERT_V4__" in html:
    print("V4 already applied. Exiting."); sys.exit(0)

required = ["function boot(", "hideSplash", "askExpert", "renderTutorials",
            "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__"]
for fn in required:
    if fn not in html:
        print("ERROR: " + fn + " missing - abort"); sys.exit(1)
print("0. All required markers present")

for v in ["V2", "V3"]:
    mark = "<!-- __HYBRID_EXPERT_" + v + "__ -->"
    mi = html.find(mark)
    if mi != -1:
        so = html.rfind("<script>", 0, mi)
        if so != -1:
            end = mi + len(mark)
            if end < len(html) and html[end] == '\n':
                end += 1
            html = html[:so] + html[end:]
            print("1. Removed old " + v + " block")

with io.open(JS_F, 'r', encoding='utf-8') as f:
    js = f.read()

if "</body>" not in html:
    print("ERROR: </body> not found"); sys.exit(1)

BLOCK = "<script>\n" + js + "\n</script>\n<!-- __HYBRID_EXPERT_V4__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("2. V4 script injected")

for fn in required + ["__HYBRID_EXPERT_V4__"]:
    if fn not in html:
        print("ERROR: " + fn + " lost - abort"); sys.exit(1)
print("3. All markers intact after patch")

if DRY:
    print("")
    print("DRY RUN OK. Would have written %d bytes." % len(html))
    sys.exit(0)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)
print("")
print("SUCCESS. Hybrid V4 installed.")
