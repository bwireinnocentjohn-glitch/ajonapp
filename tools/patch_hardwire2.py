import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "window.buildExpertReply" in html:
    print("Already hardwired. Exiting.")
    sys.exit(0)

# Find the single-line call inside askExpert
OLD = 'var replies = exComposeReply(q);'
if OLD not in html:
    print("ERROR: 'var replies = exComposeReply(q);' not found")
    sys.exit(1)

# Build replacement without any unicode escapes
SMILE = chr(0x1F642)

NEW = ('var replies = null;\n'
'      try {\n'
'        if (typeof window.buildExpertReply === "function") {\n'
'          replies = window.buildExpertReply(q);\n'
'        }\n'
'      } catch(e) { try { console.log("[Expert] brain error:", e); } catch(x) {} }\n'
'      if (!replies || !replies.length) {\n'
'        try { replies = exComposeReply(q); }\n'
'        catch(e) { replies = ["I am here. ' + SMILE + ' Please try again."]; }\n'
'      }')

html = html.replace(OLD, NEW, 1)
print("1. exComposeReply call wrapped with buildExpertReply priority")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("")
print("SUCCESS. Hardwire applied.")
