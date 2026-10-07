import io, sys, os, re

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "window.buildExpertReply" in html:
    print("Already hardwired. Exiting.")
    sys.exit(0)

SMILE = chr(0x1F642)

# Regex: match var replies=exComposeReply(q); with any spacing
pat = re.compile(r'var\s+replies\s*=\s*exComposeReply\s*\(\s*q\s*\)\s*;')

if pat.search(html):
    replacement = ('var replies = null;\n'
'      try {\n'
'        if (typeof window.buildExpertReply === "function") {\n'
'          replies = window.buildExpertReply(q);\n'
'        }\n'
'      } catch(e) { try { console.log("[Expert] brain error:", e); } catch(x) {} }\n'
'      if (!replies || !replies.length) {\n'
'        try { replies = exComposeReply(q); }\n'
'        catch(e) { replies = ["I am here. ' + SMILE + ' Please try again."]; }\n'
'      }')
    html = pat.sub(replacement, html, count=1)
    print("1. Match found and wrapped with buildExpertReply")
    with io.open(HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print("SUCCESS. Hardwire applied.")
else:
    print("PATTERN NOT FOUND. Lines containing exComposeReply:")
    for i, line in enumerate(html.split("\n")):
        if "exComposeReply" in line:
            print("  line " + str(i+1) + ": " + line[:200])
    print("")
    print("Copy the line output above and send it back.")
