import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

changed = False

# ============================================================
# 1. Notes estimate notice
# ============================================================
if "notes-estimate-notice" not in html:
    anchor = '<section class="panel" id="panel-notes">'
    if anchor in html:
        notice = anchor + '''
      <div class="notes-estimate-notice">
        <div class="notice-icon">&#x26A0;&#xFE0F;</div>
        <div class="notice-text">
          <strong>Please Note</strong>
          Prices, Capital and Profits in the Businesses are close estimates.
          Please check daily prices before starting a business.
        </div>
      </div>'''
        html = html.replace(anchor, notice, 1)
        print("1. Notes notice HTML inserted")
        changed = True
    else:
        print("WARN: panel-notes anchor not found")

    CSS_NOTICE = """
/* ========== Notes estimate notice ========== */
.notes-estimate-notice {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin: 14px 16px 6px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #2a1a00, #1a0f00);
  border-left: 4px solid #ffb300;
  border-radius: 12px;
  box-shadow: 0 4px 14px rgba(255,179,0,.15);
}
.notes-estimate-notice .notice-icon { font-size: 22px; line-height: 1; flex: 0 0 auto; }
.notes-estimate-notice .notice-text { font-size: 12.5px; color: #f3e4c8; line-height: 1.55; font-weight: 500; }
.notes-estimate-notice .notice-text strong {
  display: block; color: #ffb300; font-size: 12px; font-weight: 900;
  letter-spacing: .4px; margin-bottom: 3px; text-transform: uppercase;
}
"""
    idx = html.rfind('</style>')
    if idx != -1:
        html = html[:idx] + CSS_NOTICE + '\n' + html[idx:]
        print("1b. Notes notice CSS added")
        changed = True
else:
    print("1. Notes notice already present")

# ============================================================
# 2. Emergency contact on creator card
# ============================================================
if "0793787131" not in html and "+256793787131" not in html:
    # Try to insert after main creator-tel anchor
    marker = 'href="tel:+256768207738">'
    idx = html.find(marker)
    inserted = False
    if idx != -1:
        # Find closing </a> after this
        end = html.find("</a>", idx)
        if end != -1:
            end += 4  # include </a>
            insert = ('<div class="creator-tel-label">Emergency / Any Query</div>'
                      '<a class="creator-tel creator-tel-alt" href="tel:+256793787131">\U0001F4DE 0793 787 131</a>')
            html = html[:end] + insert + html[end:]
            print("2. Emergency contact inserted after main phone")
            changed = True
            inserted = True
    if not inserted:
        # Fallback: insert before mission text
        mission = '<div class="mission">'
        if mission in html:
            insert = ('<div class="creator-tel-label">Emergency / Any Query</div>'
                      '<a class="creator-tel" href="tel:+256793787131">\U0001F4DE 0793 787 131</a>')
            html = html.replace(mission, insert + mission, 1)
            print("2. Emergency contact inserted before mission text")
            changed = True
        else:
            print("WARN: could not find insertion point for emergency contact")

    CSS_EMERG = """
/* ========== Emergency contact ========== */
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
.creator-tel.creator-tel-alt:active { background: rgba(255,179,0,.25); }
"""
    if ".creator-tel-label" not in html:
        idx2 = html.rfind('</style>')
        if idx2 != -1:
            html = html[:idx2] + CSS_EMERG + '\n' + html[idx2:]
            print("2b. Emergency CSS added")
            changed = True
else:
    print("2. Emergency contact already present")

if changed:
    with io.open(HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print("")
    print("SUCCESS. Both patches saved.")
else:
    print("")
    print("Nothing to change. Both already present.")
