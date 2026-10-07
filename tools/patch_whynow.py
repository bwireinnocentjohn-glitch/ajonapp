import io, sys, os

JS = 'www/js/expertBrain.js'
if not os.path.exists(JS):
    print("ERROR: expertBrain.js not found"); sys.exit(1)
with io.open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

if "__ajonWhyNowV1" in js:
    print("Already patched. Exiting.")
    sys.exit(0)

# Replace the display line to use whyNow OR whyNow2026, and drop the (2026) label
old = 'out.push("\\uD83C\\uDFAF Why It Works Now (2026): " + biz.whyNow2026);'
new = 'var _why = biz.whyNow || biz.whyNow2026 || "Strong daily demand in local markets.";\n    out.push("\\uD83C\\uDFAF Why It Sells Well: " + _why);'

if old in js:
    js = js.replace(old, new, 1)
    print("1. Display label updated (no year)")
elif "Why It Sells Well:" in js:
    print("1. Already updated")
else:
    # Try a looser match
    idx = js.find("Why It Works Now")
    if idx != -1:
        # Find the full line
        line_start = js.rfind("\n", 0, idx) + 1
        line_end = js.find("\n", idx)
        js = js[:line_start] + 'out.push("\\uD83C\\uDFAF Why It Sells Well: " + (biz.whyNow || biz.whyNow2026 || "Strong daily demand in local markets."));' + js[line_end:]
        print("1. Display label updated (loose)")
    else:
        print("WARN: 'Why It Works Now' line not found")

js = js + "\n/* __ajonWhyNowV1 */\n"

with io.open(JS, 'w', encoding='utf-8') as f:
    f.write(js)
print("SUCCESS. Engine patched.")
