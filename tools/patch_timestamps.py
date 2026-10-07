import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__ajonTimestampsV1" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

# 1. Replace exAddBubble + exTypeInto + askExpert with version that adds time
OLD_MARKERS = ["function exAddBubble(speaker, text) {"]
if OLD_MARKERS[0] not in html:
    print("WARN: exAddBubble not found")
else:
    # Find function block
    start = html.find("function exAddBubble(")
    brace = html.find("{", start)
    depth = 0; i = brace
    while i < len(html):
        ch = html[i]
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1; break
        i += 1

    NEW_ADD = '''function exAddBubble(speaker, text) {
  var box = byId("expertMsgs");
  if (!box) return null;
  var div = document.createElement("div");
  div.className = "expert-bubble " + (speaker === "me" ? "me" : "ex");
  var body = document.createElement("div");
  body.className = "expert-bubble-body";
  body.textContent = String(text || "");
  var meta = document.createElement("div");
  meta.className = "expert-bubble-time";
  var now = new Date();
  var hh = now.getHours();
  var mm = now.getMinutes();
  var ampm = hh >= 12 ? "PM" : "AM";
  hh = hh % 12; if (hh === 0) hh = 12;
  if (mm < 10) mm = "0" + mm;
  meta.textContent = hh + ":" + mm + " " + ampm;
  div.appendChild(body);
  div.appendChild(meta);
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return body; /* return the text container so typing works on it */
}'''
    html = html[:start] + NEW_ADD + html[end:]
    print("1. exAddBubble updated with timestamp")

# 2. Replace exTypeInto to accept container element directly
start2 = html.find("function exTypeInto(")
if start2 != -1:
    brace2 = html.find("{", start2)
    depth = 0; i = brace2
    while i < len(html):
        ch = html[i]
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end2 = i + 1; break
        i += 1

    NEW_TYPE = '''function exTypeInto(el, text, done) {
  if (!el) { if (done) done(); return; }
  var full = String(text || "");
  var i = 0;
  el.textContent = "";
  function tick() {
    if (i >= full.length) { if (done) done(); return; }
    el.textContent += full.charAt(i);
    var box = byId("expertMsgs");
    if (box) box.scrollTop = box.scrollHeight;
    i++;
    setTimeout(tick, 12);
  }
  tick();
}'''
    html = html[:start2] + NEW_TYPE + html[end2:]
    print("2. exTypeInto updated (faster, cleaner)")

# 3. Add CSS for timestamp
CSS = """
/* ========== Expert bubble timestamp (WhatsApp style) ========== */
.expert-bubble { display: flex; flex-direction: column; gap: 3px; }
.expert-bubble-body { white-space: pre-wrap; word-break: break-word; }
.expert-bubble-time {
  font-size: 10px;
  opacity: .7;
  text-align: right;
  font-weight: 600;
  letter-spacing: .2px;
  margin-top: 2px;
}
.expert-bubble.me .expert-bubble-time { color: #003d14; opacity: .75; }
.expert-bubble.ex .expert-bubble-time { color: #8fdfa5; opacity: .75; }
.expert-bubble.typing .expert-bubble-body { color: #00c853; letter-spacing: 3px; font-size: 20px; }
"""
if ".expert-bubble-time" not in html:
    idx = html.rfind('</style>')
    if idx == -1:
        print("ERR </style>"); sys.exit(1)
    html = html[:idx] + CSS + '\n' + html[idx:]
    print("3. Timestamp CSS added")

# 4. Marker
if "__ajonTimestampsV1" not in html:
    marker = "/* ===== End of expert timestamps patch ===== */\nwindow.__ajonTimestampsV1 = true;\n"
    idx2 = html.rfind('</script>')
    if idx2 != -1:
        html = html[:idx2] + marker + html[idx2:]
        print("4. Marker added")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Timestamps + typing installed.")
