import io, sys, os
HTML = 'www/index.html'
JS_F = 'tools/enhancements.js'
DRY = '--dry-run' in sys.argv

with io.open(HTML, 'r', encoding='utf-8') as f: html = f.read()

js_marker = "<!-- __EXPERT_ENHANCEMENTS_V1__ -->"
mi = html.find(js_marker)
if mi != -1:
    so = html.rfind("<script>", 0, mi)
    if so != -1:
        end = mi + len(js_marker)
        if end < len(html) and html[end] == '\n': end += 1
        html = html[:so] + html[end:]
        print("1. Removed old enhancement JS")

for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials",
           "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__", "__HYBRID_EXPERT_V7__"]:
    if fn not in html: print("ERROR: " + fn + " missing"); sys.exit(1)
print("2. Required markers present")

with io.open(JS_F, 'r', encoding='utf-8') as f: js = f.read()
if "</body>" not in html: print("ERROR: </body> missing"); sys.exit(1)
BLOCK = "<script>\n" + js + "\n</script>\n<!-- __EXPERT_ENHANCEMENTS_V1__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("3. New JS injected")

if DRY:
    print(""); print("DRY RUN OK. Would write %d bytes." % len(html)); sys.exit(0)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f: f.write(html)
os.replace(tmp, HTML)
print(""); print("SUCCESS. V9 installed.")
