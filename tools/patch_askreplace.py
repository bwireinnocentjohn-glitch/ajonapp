import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__ajonAskV2" in html:
    print("Already replaced. Exiting.")
    sys.exit(0)

# Find "function askExpert(" and match braces
marker = "function askExpert("
start = html.find(marker)
if start == -1:
    print("ERROR: function askExpert not found")
    # Show nearby context
    idx = html.find("askExpert")
    if idx != -1:
        print("Found 'askExpert' at position " + str(idx))
        print("Context: " + html[max(0,idx-100):idx+200])
    sys.exit(1)

brace = html.find("{", start)
if brace == -1:
    print("ERROR: opening brace not found"); sys.exit(1)

depth = 0
i = brace
end = -1
while i < len(html):
    ch = html[i]
    if ch == "{": depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1

if end == -1:
    print("ERROR: matching closing brace not found"); sys.exit(1)

SMILE = chr(0x1F642)

NEW = ('function askExpert() { /* __ajonAskV2 */\n'
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
'        replies = ["I am here. ' + SMILE + ' Try asking about a business like \'soap\', \'beekeeping\', \'solar cooker\', or a term like \'cash flow\'."];\n'
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
print("1. askExpert function fully replaced")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("")
print("SUCCESS. New askExpert installed (hardwired to buildExpertReply).")
