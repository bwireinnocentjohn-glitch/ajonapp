import io, sys, os

HTML = 'www/index.html'
JS   = 'tools/api_debug.js'

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__API_DEBUG_V1__" in html:
    print("Already applied."); sys.exit(0)

for fn in ["function boot(", "hideSplash", "askExpert", "__HYBRID_EXPERT_V2__"]:
    if fn not in html:
        print("ERROR: " + fn + " missing - abort"); sys.exit(1)

with io.open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

if "</body>" not in html:
    print("ERROR: </body> missing"); sys.exit(1)

BLOCK = "<script>\n" + js + "\n</script>\n<!-- __API_DEBUG_V1__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)
print("SUCCESS. API debug injected.")
