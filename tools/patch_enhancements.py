import io, sys, os
HTML = 'www/index.html'
CSS_F = 'tools/enhancements.css'
JS_F = 'tools/enhancements.js'
DRY = '--dry-run' in sys.argv

with io.open(HTML, 'r', encoding='utf-8') as f: html = f.read()

if "__EXPERT_ENHANCEMENTS_V1__" in html:
    print("Enhancements already applied."); sys.exit(0)

required = ["function boot(", "hideSplash", "askExpert", "renderTutorials",
            "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__", "__HYBRID_EXPERT_V7__"]
for fn in required:
    if fn not in html: print("ERROR: " + fn + " missing"); sys.exit(1)
print("0. Required markers present")

with io.open(CSS_F, 'r', encoding='utf-8') as f: css = f.read()
with io.open(JS_F, 'r', encoding='utf-8') as f: js = f.read()

sidx = html.rfind('</style>')
if sidx == -1: print("ERROR: </style> missing"); sys.exit(1)
html = html[:sidx] + "\n" + css + "\n" + html[sidx:]
print("1. CSS injected before last </style>")

if "</body>" not in html: print("ERROR: </body> missing"); sys.exit(1)
BLOCK = "<script>\n" + js + "\n</script>\n<!-- __EXPERT_ENHANCEMENTS_V1__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("2. JS injected before </body>")

for fn in required + ["__EXPERT_ENHANCEMENTS_V1__"]:
    if fn not in html: print("ERROR: " + fn + " lost"); sys.exit(1)
print("3. All markers intact")

if DRY:
    print(""); print("DRY RUN OK. Would write %d bytes." % len(html)); sys.exit(0)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f: f.write(html)
os.replace(tmp, HTML)
print(""); print("SUCCESS. Enhancements V1 installed.")
