import io, sys, os

HTML = 'www/index.html'
CSS_F = 'tools/safe_live.css'
JS_F = 'tools/safe_live.js'

if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__SAFE_LIVE_V2__" in html:
    print("Already applied. Exiting."); sys.exit(0)

if not os.path.exists(CSS_F) or not os.path.exists(JS_F):
    print("ERROR: CSS or JS file missing"); sys.exit(1)

with io.open(CSS_F, 'r', encoding='utf-8') as f:
    css = f.read()
with io.open(JS_F, 'r', encoding='utf-8') as f:
    js = f.read()

# Sanity before
for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment"]:
    if fn not in html:
        print("ERROR: " + fn + " missing - abort"); sys.exit(1)

# 1. CSS before last </style>
sidx = html.rfind('</style>')
if sidx == -1:
    print("ERROR: </style> not found"); sys.exit(1)
html = html[:sidx] + "\n" + css + "\n" + html[sidx:]

# 2. JS before </body>
if "</body>" not in html:
    print("ERROR: </body> not found"); sys.exit(1)
SCRIPT = "<script>\n" + js + "\n</script>\n<!-- __SAFE_LIVE_V2__ -->\n"
html = html.replace("</body>", SCRIPT + "</body>", 1)

# Sanity after
for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment"]:
    if fn not in html:
        print("ERROR: " + fn + " lost during patch - aborting write"); sys.exit(1)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("SUCCESS. Safe live v2 installed.")
