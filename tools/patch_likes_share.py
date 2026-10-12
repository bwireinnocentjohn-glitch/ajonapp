import io, sys, os, re

HTML = 'www/index.html'
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()
orig = html
changes = []

# ---- Likes: wider spread ----
new_base = "var base = 800 + (h % 480000);"
if new_base in html:
    print("Likes base: already updated")
else:
    m = re.search(r'var base\s*=\s*\d+\s*\+\s*\(h\s*%\s*\d+\);', html)
    if m:
        html = html.replace(m.group(0), new_base, 1)
        print("Likes base: patched -> 800 to 480,800")
        changes.append("base")
    else:
        print("WARN: likes base not found")

new_rate = "var rate = 300 + (h % 8000);"
if new_rate in html:
    print("Likes rate: already updated")
else:
    m = re.search(r'var rate\s*=\s*\d+\s*\+\s*\(h\s*%\s*\d+\);', html)
    if m:
        html = html.replace(m.group(0), new_rate, 1)
        print("Likes rate: patched -> 300 to 8,300/hr")
        changes.append("rate")
    else:
        print("WARN: likes rate not found")

# ---- WhatsApp button label ----
new_label = "Share Ajon on WhatsApp to Access More</button>"
if new_label in html:
    print("WhatsApp label: already updated")
elif "Share Ajon on WhatsApp</button>" in html:
    html = html.replace("Share Ajon on WhatsApp</button>", new_label, 1)
    print("WhatsApp label: patched")
    changes.append("label")
else:
    print("WARN: WhatsApp label not found")

# ---- WhatsApp message ----
new_msg = "Download Ajon 1500+ Businesses App from ajonapp.netlify.app only 7mbs and Access Lessons Without Data Cost, At only 2500/= Trial, And have Access to a Soft Business Loan After, Mastering The Business of Your Choice."
if "ajonapp.netlify.app" in html:
    print("WhatsApp message: already updated")
else:
    m = re.search(r'(var\s+msg\s*=\s*)"([^"]*)"', html)
    if m:
        html = html[:m.start(2)] + new_msg + html[m.end(2):]
        print("WhatsApp message: patched")
        changes.append("msg")
    else:
        print("WARN: WhatsApp message not found")

if not changes:
    print("\nNo changes made.")
    sys.exit(0)

tmp = HTML + '.tmp'
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)
print("\nSUCCESS. Applied: " + ", ".join(changes))
