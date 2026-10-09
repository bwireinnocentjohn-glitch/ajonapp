import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html missing"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__SAFE_LIVE_V4__" in html:
    print("V4 already applied. Exiting."); sys.exit(0)

for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment", "__LIKES_MIN__"]:
    if fn not in html:
        print("ERROR: " + fn + " missing - abort"); sys.exit(1)

def strip_block(marker_css, marker_html):
    global html
    # strip CSS block
    ci = html.find(marker_css)
    if ci != -1:
        ce = html.find("</style>", ci)
        if ce != -1:
            html = html[:ci] + html[ce:]
            print("   removed CSS " + marker_css)
    # strip script block
    mi = html.find(marker_html)
    if mi != -1:
        so = html.rfind("<script>", 0, mi)
        if so != -1:
            end = mi + len(marker_html)
            if end < len(html) and html[end] == '\n':
                end += 1
            html = html[:so] + html[end:]
            print("   removed script " + marker_html)

print("1. Removing old V2/V3 leftovers...")
strip_block("/* __SAFE_LIVE_V2__ */", "<!-- __SAFE_LIVE_V2__ -->")
strip_block("/* __SAFE_LIVE_V3__ */", "<!-- __SAFE_LIVE_V3__ -->")

# ---- Likes rate patch ----
print("2. Patching likes rate...")
old_rate = "var rate = 20000 + (h % 50000);"
new_rate = "var rate = 6000;"
if old_rate in html:
    html = html.replace(old_rate, new_rate)
    print("   rate -> 6000/hr (1k per 10 min)")
else:
    print("   rate already patched or not found")

old_iv = "setInterval(upd, 3000);"
new_iv = "setInterval(upd, 1000);"
if old_iv in html:
    html = html.replace(old_iv, new_iv)
    print("   interval -> 1000ms (smooth)")
else:
    print("   interval already patched or not found")

# ---- Inject V4 CSS ----
print("3. Injecting V4 CSS...")
with io.open('tools/v4.css', 'r', encoding='utf-8') as f:
    css = f.read()
sidx = html.rfind('</style>')
if sidx == -1:
    print("ERROR: </style> not found"); sys.exit(1)
html = html[:sidx] + "\n" + css + "\n" + html[sidx:]

# ---- Inject V4 script ----
print("4. Injecting V4 script...")
with io.open('tools/v4.js', 'r', encoding='utf-8') as f:
    js = f.read()
if "</body>" not in html:
    print("ERROR: </body> not found"); sys.exit(1)
SCRIPT = "<script>\n" + js + "\n</script>\n<!-- __SAFE_LIVE_V4__ -->\n"
html = html.replace("</body>", SCRIPT + "</body>", 1)

# ---- Sanity after ----
for fn in ["function boot(", "hideSplash", "askExpert", "renderTutorials", "renderPayment", "__LIKES_MIN__"]:
    if fn not in html:
        print("ERROR: " + fn + " lost - abort"); sys.exit(1)
print("5. Main app functions intact")

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("")
print("SUCCESS. V4 installed.")
