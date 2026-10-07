import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "notes-estimate-notice" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

# ---- 1. Insert notice HTML right after panel-notes opening ----
anchor = '<section class="panel" id="panel-notes">'
if anchor not in html:
    print("ERR: panel-notes not found"); sys.exit(1)

notice_html = anchor + '''
      <div class="notes-estimate-notice">
        <div class="notice-icon">&#x26A0;&#xFE0F;</div>
        <div class="notice-text">
          <strong>Please Note</strong>
          Prices, Capital and Profits in the Businesses are close estimates.
          Please check daily prices before starting a business.
        </div>
      </div>'''

html = html.replace(anchor, notice_html, 1)
print("1. Notice HTML inserted into Notes tab")

# ---- 2. Add CSS for the notice ----
CSS = """
/* ========== Notes tab: estimate notice ========== */
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
  animation: slideUp .35s ease both;
}
.notes-estimate-notice .notice-icon {
  font-size: 22px;
  line-height: 1;
  flex: 0 0 auto;
  margin-top: 1px;
}
.notes-estimate-notice .notice-text {
  font-size: 12.5px;
  color: #f3e4c8;
  line-height: 1.55;
  font-weight: 500;
}
.notes-estimate-notice .notice-text strong {
  display: block;
  color: #ffb300;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .4px;
  margin-bottom: 3px;
  text-transform: uppercase;
}
"""

idx = html.rfind('</style>')
if idx == -1:
    print("ERR: </style> not found"); sys.exit(1)
html = html[:idx] + CSS + '\n' + html[idx:]
print("2. CSS added")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Notice added to Notes tab.")
