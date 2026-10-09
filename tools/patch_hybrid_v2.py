import io, sys, os

HTML = 'www/index.html'
JS_F = 'tools/hybrid_expert_v2.js'

if not os.path.exists(HTML):
    print("ERROR: index.html missing"); sys.exit(1)
if not os.path.exists(JS_F):
    print("ERROR: hybrid_expert_v2.js missing"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__HYBRID_EXPERT_V2__" in html:
    print("V2 already applied. Exiting."); sys.exit(0)

for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__"]:
    if fn not in html:
        print("ERROR: " + fn + " missing - abort"); sys.exit(1)

# Remove V1 script block if present
v1mark = "<!-- __HYBRID_EXPERT_V1__ -->"
mi = html.find(v1mark)
if mi != -1:
    so = html.rfind("<script>", 0, mi)
    if so != -1:
        end = mi + len(v1mark)
        if end < len(html) and html[end] == '\n':
            end += 1
        html = html[:so] + html[end:]
        print("1. V1 script removed")
else:
    print("1. V1 not present (fresh install)")

with io.open(JS_F, 'r', encoding='utf-8') as f:
    js = f.read()

if "</body>" not in html:
    print("ERROR: </body> not found"); sys.exit(1)

BLOCK = "<script>\n" + js + "\n</script>\n<!-- __HYBRID_EXPERT_V2__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("2. V2 script injected")

for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__"]:
    if fn not in html:
        print("ERROR: " + fn + " lost - abort"); sys.exit(1)
print("3. All safety markers intact.")

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("")
print("SUCCESS. Hybrid V2 installed.")
