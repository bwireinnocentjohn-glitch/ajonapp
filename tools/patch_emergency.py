import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "0793787131" in html or "+256793787131" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

old = '<a class="creator-tel" href="tel:+256768207738">\U0001F4DE +256 768 207 738</a>'
# Try alternate encodings of the same anchor
candidates = [
    '<a class="creator-tel" href="tel:+256768207738">\U0001F4DE +256 768 207 738</a>',
    '<a class="creator-tel" href="tel:+256768207738">&#x1F4DE; +256 768 207 738</a>',
    '<a class="creator-tel" href="tel:+256768207738">' + "\U0001F4DE" + ' +256 768 207 738</a>',
]

new = ('<a class="creator-tel" href="tel:+256768207738">\U0001F4DE +256 768 207 738</a>'
       '<div class="creator-tel-label">Emergency / Any Query</div>'
       '<a class="creator-tel creator-tel-alt" href="tel:+256793787131">\U0001F4DE 0793 787 131</a>')

found = False
for cand in candidates:
    if cand in html:
        html = html.replace(cand, new, 1)
        found = True
        print("Creator card contact updated")
        break

if not found:
    # Loose fallback: patch any anchor with the old number
    old2 = 'href="tel:+256768207738">'
    idx = html.find(old2)
    if idx != -1:
        # find the closing </a>
        end = html.find("</a>", idx)
        if end != -1:
            block_end = end + 4
            full_old = html[idx-30:block_end]  # rough capture
            # safer: rebuild by replacing only the closing </a> after our href
            new_tail = ('href="tel:+256768207738">\U0001F4DE +256 768 207 738</a>'
                        '<div class="creator-tel-label">Emergency / Any Query</div>'
                        '<a class="creator-tel creator-tel-alt" href="tel:+256793787131">\U0001F4DE 0793 787 131</a>')
            html = html[:idx] + new_tail + html[block_end:]
            found = True
            print("Creator card contact updated (loose)")
    if not found:
        print("WARN: creator-tel anchor not matched. Adding emergency contact as new block.")

# If neither worked, append a safety block before the mission text
if not found:
    mission_anchor = '<div class="mission">'
    if mission_anchor in html:
        insert = ('<div class="creator-tel-label">Emergency / Any Query</div>'
                  '<a class="creator-tel" href="tel:+256793787131">\U0001F4DE 0793 787 131</a>')
        html = html.replace(mission_anchor, insert + mission_anchor, 1)
        print("Emergency contact inserted before mission text")
    else:
        print("WARN: could not find insertion point")

# ---- CSS for the new label + alt tel ----
CSS = """
/* ========== Creator card: emergency contact ========== */
.creator-tel-label {
  display: block;
  font-size: 10.5px;
  color: #ffb300;
  font-weight: 800;
  letter-spacing: .8px;
  text-transform: uppercase;
  margin: 4px 0 6px;
  opacity: .9;
}
.creator-tel.creator-tel-alt {
  background: rgba(255,179,0,.12);
  border-color: rgba(255,179,0,.5);
  color: #ffb300;
}
.creator-tel.creator-tel-alt:active {
  background: rgba(255,179,0,.25);
}
"""
if ".creator-tel-label" not in html:
    idx2 = html.rfind('</style>')
    if idx2 == -1:
        print("ERR </style>"); sys.exit(1)
    html = html[:idx2] + CSS + '\n' + html[idx2:]
    print("CSS added")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Emergency contact added.")
