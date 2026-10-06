import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

has_v6 = "var CHAT_TOPICS" in html
has_v7 = "function pickBusinessForTopic" in html

print("v6 present: " + str(has_v6))
print("v7 present: " + str(has_v7))

# ---------- 1. Force loop to call buildPasieFinal / buildAjonFinal ----------
import re

# Replace any call variant in the loop
html = re.sub(r'var pasieBubbles = [a-zA-Z_0-9]+\(\);',
              'var pasieBubbles = buildPasieFinal();', html)
html = re.sub(r'var ajonBubbles = [a-zA-Z_0-9]+\(\);',
              'var ajonBubbles = buildAjonFinal();', html)
print("Loop redirected to buildPasieFinal / buildAjonFinal.")

# ---------- 2. If v6 missing, append minimal v6 ----------
if not has_v6:
    print("WARNING: v6 code missing. Please run patch_v6.py first, then this again.")
    sys.exit(1)

# ---------- 3. If v7 missing, append it ----------
if not has_v7:
    print("WARNING: v7 code missing. Please run patch_v7.py first, then this again.")
    sys.exit(1)

# ---------- 4. Ensure clear resets v6/v7 state ----------
old = 'BRAIN.currentTopicId = "fear";\n  BRAIN.lastTopics = [];'
if old in html and "BRAIN._bizIdx = {};" not in html:
    html = html.replace(old,
        'BRAIN.currentTopicId = "fear";\n  BRAIN.lastTopics = [];\n  BRAIN._bizIdx = {};\n  BRAIN.lastBusinessIds = [];\n  BRAIN.lastAjonPrinciple = null;\n  BRAIN.pendingBusiness = null;', 1)
    print("Clear resets extended.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Loop now uses buildPasieFinal / buildAjonFinal.")
