import io, sys, os, re

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__REMOVED_OLD_BRAIN__" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

# Find askExpert function
marker = "function askExpert("
start = html.find(marker)
if start == -1:
    print("ERROR: askExpert not found"); sys.exit(1)

brace = html.find("{", start)
if brace == -1:
    print("ERROR: opening brace not found"); sys.exit(1)

depth = 0; i = brace; end = -1
while i < len(html):
    ch = html[i]
    if ch == "{": depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            end = i + 1; break
    i += 1

if end == -1:
    print("ERROR: closing brace not found"); sys.exit(1)

SMILE = chr(0x1F642)

NEW = ('function askExpert() { /* __REMOVED_OLD_BRAIN__ */\n'
'  try {\n'
'    if (typeof hasFullAccess === "function" && !hasFullAccess()) { expertGate(); return; }\n'
'    if (EXPERT.busy) return;\n'
'    var inp = byId("aiInput");\n'
'    if (!inp) return;\n'
'    var q = String(inp.value || "").trim();\n'
'    if (!q) { inp.focus(); return; }\n'
'    inp.value = "";\n'
'    EXPERT.busy = true;\n'
'    exHideQuote();\n'
'    exAddBubble("me", q);\n'
'    EXPERT.msgs.push({ s: "me", t: q });\n'
'    var typing = exShowTyping();\n'
'    setTimeout(function(){\n'
'      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);\n'
'      var replies = null;\n'
'      try {\n'
'        if (typeof window.buildExpertReply === "function") {\n'
'          replies = window.buildExpertReply(q);\n'
'        }\n'
'      } catch(e) { try { console.log("[Expert] brain error:", e); } catch(x) {} }\n'
'      if (!replies || !replies.length) {\n'
'        replies = [\n'
'          "I am here. ' + SMILE + ' Let me help you.",\n'
'          "Try asking: \'how do I make soap?\' or \'how do I make honey?\'",\n'
'          "Or a business term like \'cash flow\' or \'profit margin\'."\n'
'        ];\n'
'      }\n'
'      var idx = 0;\n'
'      function sendNext() {\n'
'        if (idx >= replies.length) { EXPERT.busy = false; return; }\n'
'        var text = replies[idx];\n'
'        var bubble = exAddBubble("ex", "");\n'
'        EXPERT.msgs.push({ s: "ex", t: text });\n'
'        exTypeInto(bubble, text, function(){\n'
'          idx++;\n'
'          setTimeout(sendNext, 250);\n'
'        });\n'
'      }\n'
'      sendNext();\n'
'    }, 600 + Math.random() * 500);\n'
'  } catch (e) { EXPERT.busy = false; }\n'
'}')

html = html[:start] + NEW + html[end:]

# Safe write
tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("SUCCESS. Old brain bypassed in askExpert.")
