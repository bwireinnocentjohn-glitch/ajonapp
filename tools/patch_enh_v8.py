import io, sys, os
HTML = 'www/index.html'
CSS_F = 'tools/enhancements.css'
JS_F = 'tools/enhancements.js'
DRY = '--dry-run' in sys.argv

with io.open(HTML, 'r', encoding='utf-8') as f: html = f.read()

css_marker = "/* __EXPERT_ENHANCEMENTS_V1__ */"
ci = html.find(css_marker)
if ci != -1:
    ce = html.find("</style>", ci)
    if ce != -1:
        html = html[:ci] + html[ce:]
        print("1. Removed old enhancement CSS")

js_marker = "<!-- __EXPERT_ENHANCEMENTS_V1__ -->"
mi = html.find(js_marker)
if mi != -1:
    so = html.rfind("<script>", 0, mi)
    if so != -1:
        end = mi + len(js_marker)
        if end < len(html) and html[end] == '\n': end += 1
        html = html[:so] + html[end:]
        print("2. Removed old enhancement JS")

needle = "  /* ---------- CACHE ---------- */"
expose  = "  window.__ajonGetKeys = function(){ return { groq: CONFIG.GROQ_KEY, gemini: CONFIG.GEMINI_KEY }; };\n\n  /* ---------- CACHE ---------- */"
if "window.__ajonGetKeys" not in html and needle in html:
    html = html.replace(needle, expose, 1)
    print("3. V7 key getter exposed")

for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials",
           "renderPayment", "__LIKES_MIN__", "__SAFE_LIVE_V4__", "__HYBRID_EXPERT_V7__"]:
    if fn not in html: print("ERROR: " + fn + " missing"); sys.exit(1)
print("4. Required markers present")

with io.open(CSS_F, 'r', encoding='utf-8') as f: css = f.read()
with io.open(JS_F, 'r', encoding='utf-8') as f: js = f.read()

sidx = html.rfind('</style>')
if sidx == -1: print("ERROR: </style> missing"); sys.exit(1)
html = html[:sidx] + "\n" + css + "\n" + html[sidx:]
print("5. CSS injected")

if "</body>" not in html: print("ERROR: </body> missing"); sys.exit(1)
BLOCK = "<script>\n" + js + "\n</script>\n<!-- __EXPERT_ENHANCEMENTS_V1__ -->\n"
html = html.replace("</body>", BLOCK + "</body>", 1)
print("6. JS injected")

if DRY:
    print(""); print("DRY RUN OK. Would write %d bytes." % len(html)); sys.exit(0)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f: f.write(html)
os.replace(tmp, HTML)
print(""); print("SUCCESS. Enhancements V8 installed.")
