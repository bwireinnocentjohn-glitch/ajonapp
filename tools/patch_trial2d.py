import io, sys, os
HTML = 'www/index.html'
JS_F = 'tools/trial2d_lock.js'
DRY = '--dry-run' in sys.argv

with io.open(HTML, 'r', encoding='utf-8') as f: html = f.read()

marker = "<!-- __TRIAL2D_LOCK_V1__ -->"
mi = html.find(marker)
if mi != -1:
    so = html.rfind("<script>", 0, mi)
    if so != -1:
        end = mi + len(marker)
        if end < len(html) and html[end] == '\n': end += 1
        html = html[:so] + html[end:]
        print("1. Removed previous Trial2d block")

required = ["function boot(", "hideSplash", "askExpert", "renderTutorials",
            "renderPayment", "verifyPassword", "generateCurrentPassword",
            "__HYBRID_EXPERT_V7__", "__EXPERT_ENHANCEMENTS_V1__", "__LIKES_MIN__"]
for fn in required:
    if fn not in html: print("ERROR: " + fn + " missing"); sys.exit(1)
print("2. Required markers present")

with io.open(JS_F, 'r', encoding='utf-8') as f: js = f.read()
if "</body>" not in html: print("ERROR: </body> missing"); sys.exit(1)

BLOCK = "<script>\n" + js + "\n</script>\n<!-- __TRIAL2D_LOCK_V1__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("3. JS injected")

for fn in required + ["__TRIAL2D_LOCK_V1__"]:
    if fn not in html: print("ERROR: " + fn + " lost"); sys.exit(1)
print("4. All markers intact")

if DRY:
    print(""); print("DRY RUN OK. Would write %d bytes." % len(html)); sys.exit(0)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f: f.write(html)
os.replace(tmp, HTML)
print(""); print("SUCCESS. Trial2d installed.")
