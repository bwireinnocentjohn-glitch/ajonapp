import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__UNLOCK_V2__" in html:
    print("Already applied. Exiting."); sys.exit(0)

# Safe emoji variables
ROCKET = chr(0x1F680)
MONEY = chr(0x1F4B0)
CALL  = chr(0x1F4DE)
COIN  = chr(0x1FA99)
STAR  = chr(0x2B50)
GEM   = chr(0x1F48E)
MEDAL = chr(0x1F948)

changed = []

# ============================================================
# 1. Round switch + Loan notice in Unlock panel
# ============================================================
old_panel = '<section class="panel" id="panel-video"><div id="videoArea"></div></section>'

new_panel = ('<section class="panel" id="panel-video">\n'
'      <div class="unlock-top-controls">\n'
'        <div class="loan-switch-wrap">\n'
'          <span class="loan-switch-label">' + MONEY + ' Loan Notice</span>\n'
'          <button class="round-switch on" id="loanSwitch" onclick="toggleLoanNotice()" aria-label="Toggle loan notice">\n'
'            <span class="round-knob"></span>\n'
'          </button>\n'
'        </div>\n'
'      </div>\n'
'      <div class="loan-notice-card" id="loanNoticeCard">\n'
'        <div class="loan-icon">' + MONEY + '</div>\n'
'        <div class="loan-body">\n'
'          <div class="loan-title">Get A Business Loan</div>\n'
'          <div class="loan-text">From <b>50,000 UGX</b> to <b>1,200,000 UGX</b>. Start paying after 30 days. Remember to pay in time for your loan amount to increase.</div>\n'
'          <a class="loan-cta" href="tel:+256768207738">' + CALL + ' Call CEO to Apply</a>\n'
'        </div>\n'
'      </div>\n'
'      <div id="videoArea"></div>\n'
'    </section>')

if old_panel in html:
    html = html.replace(old_panel, new_panel, 1)
    changed.append("1. Round switch + Loan notice added to Unlock tab")

# ============================================================
# 2. Update shareWhatsApp to give 1000 coins
# ============================================================
old_share = '''function shareWhatsApp() {
  var msg = "Install The Ajon 1500+ Business App, With Free Data Buddle for 30 days, learn from Expert and Divorce From Poverty, At 5000/= 30 days Fully";
  var url = "https://wa.me/?text=" + encodeURIComponent(msg);
  try { window.open(url, "_blank"); } catch(e) { try { location.href = url; } catch(x) {} }
  try {
    var c = getCoins() + 1;
    writeJSON("ajon_coins", c);
  } catch(e) {}
}'''

new_share = '''function shareWhatsApp() {
  var msg = "Install The Ajon 1500+ Business App, With Free Data Buddle for 30 days, learn from Expert and Divorce From Poverty, At 5000/= 30 days Fully";
  var url = "https://wa.me/?text=" + encodeURIComponent(msg);
  try { window.open(url, "_blank"); } catch(e) { try { location.href = url; } catch(x) {} }
  try {
    var c = getCoins() + 1000;
    writeJSON("ajon_coins", c);
    try { alert("''' + ROCKET + ''' +1000 coins added! Total: " + c + " coins\\n\\n" + getCoinTier(c).label); } catch(x) {}
  } catch(e) {}
}

function getCoinTier(coins) {
  coins = Number(coins) || 0;
  if (coins >= 1000000) return { name: "DIAMOND", label: "''' + GEM + ''' DIAMOND tier — 1,000,000+ coins", color: "#5bc0eb" };
  if (coins >= 100000) return { name: "GOLD", label: "''' + MEDAL + ''' GOLD tier — 100,000+ coins", color: "#ffb300" };
  if (coins >= 1000) return { name: "SILVER", label: "''' + STAR + ''' SILVER tier — 1,000+ coins", color: "#c0c0c0" };
  return { name: "BRONZE", label: "BRONZE tier — earn 1,000+ to level up", color: "#cd7f32" };
}

function toggleLoanNotice() {
  var sw = byId("loanSwitch");
  var card = byId("loanNoticeCard");
  if (!sw || !card) return;
  var on = sw.classList.contains("on");
  if (on) {
    sw.classList.remove("on");
    card.classList.add("hidden");
    try { writeJSON("ajon_loan_notice", 0); } catch(e) {}
  } else {
    sw.classList.add("on");
    card.classList.remove("hidden");
    try { writeJSON("ajon_loan_notice", 1); } catch(e) {}
  }
}

function initLoanNoticeState() {
  try {
    var saved = readJSON("ajon_loan_notice", 1);
    var sw = byId("loanSwitch");
    var card = byId("loanNoticeCard");
    if (!sw || !card) return;
    if (saved) {
      sw.classList.add("on");
      card.classList.remove("hidden");
    } else {
      sw.classList.remove("on");
      card.classList.add("hidden");
    }
  } catch(e) {}
}'''

if old_share in html:
    html = html.replace(old_share, new_share, 1)
    changed.append("2. Share gives +1000 coins + tier helper + toggle added")

# ============================================================
# 3. Update coins badge inside renderPayment to show tier
# ============================================================
old_coins = '''var coinsHtml = '<div style="text-align:center;"><div class="coins-badge">''' + COIN + ''' Coins: <b>' + coins + '</b> \\u2014 Share more to earn</div></div>';'''

new_coins = '''var tier = getCoinTier(coins);
  var coinsHtml = '<div style="text-align:center;"><div class="coins-badge">''' + COIN + ''' Coins: <b>' + coins + '</b> UGX<br><span style="font-size:11px;color:' + tier.color + ';margin-top:4px;display:inline-block;">' + tier.label + '</span></div></div>';'''

if old_coins in html:
    html = html.replace(old_coins, new_coins, 1)
    changed.append("3. Coins badge shows tier + UGX equivalence")

# ============================================================
# 4. CSS for switch + loan card
# ============================================================
CSS = '''
/* ===== Unlock tab: switch + loan notice ===== */
.unlock-top-controls {
  padding: 12px 16px 6px;
  display: flex;
  justify-content: flex-end;
}
.loan-switch-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #1a1a1a;
  border: 1px solid rgba(0,200,83,.4);
  border-radius: 999px;
  padding: 6px 12px;
}
.loan-switch-label {
  font-size: 12px;
  font-weight: 800;
  color: #00c853;
  letter-spacing: .3px;
}
.round-switch {
  width: 44px;
  height: 24px;
  border-radius: 999px;
  background: #333;
  border: 0;
  position: relative;
  cursor: pointer;
  padding: 0;
  transition: background .2s;
  flex: 0 0 auto;
}
.round-switch.on { background: #00c853; }
.round-knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: transform .2s;
  box-shadow: 0 2px 4px rgba(0,0,0,.3);
}
.round-switch.on .round-knob { transform: translateX(20px); }

.loan-notice-card {
  margin: 4px 16px 14px;
  padding: 14px;
  background: linear-gradient(135deg,#001a0a,#003d14);
  border: 1px solid #00c853;
  border-radius: 14px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.loan-notice-card.hidden { display: none; }
.loan-icon {
  font-size: 32px;
  line-height: 1;
  flex: 0 0 auto;
  filter: drop-shadow(0 0 10px rgba(0,200,83,.5));
}
.loan-title {
  font-size: 15px;
  font-weight: 900;
  color: #00c853;
  letter-spacing: .3px;
  margin-bottom: 6px;
}
.loan-text {
  font-size: 12.5px;
  color: #e6f7ea;
  line-height: 1.55;
  margin-bottom: 10px;
}
.loan-text b { color: #00c853; }
.loan-cta {
  display: inline-block;
  background: linear-gradient(135deg,#00c853,#009624);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  padding: 9px 14px;
  border-radius: 999px;
  text-decoration: none;
  letter-spacing: .3px;
}
.loan-cta:active { transform: scale(.97); }
'''
if ".round-switch" not in html:
    idx = html.rfind('</style>')
    if idx != -1:
        html = html[:idx] + CSS + '\n' + html[idx:]
        changed.append("4. CSS added")

# ============================================================
# 5. Call initLoanNoticeState on boot
# ============================================================
old_boot = '    startTrialTick();'
new_boot = '    startTrialTick();\n    try { if (typeof initLoanNoticeState === "function") initLoanNoticeState(); } catch(e) {}'
if old_boot in html and "initLoanNoticeState()" not in html.split("startTrialTick();")[1][:150]:
    html = html.replace(old_boot, new_boot, 1)
    changed.append("5. Boot hooked to init loan notice")

# ============================================================
# Marker
# ============================================================
if "__UNLOCK_V2__" not in html:
    idx = html.rfind('</script>')
    if idx != -1:
        html = html[:idx] + '\n/* __UNLOCK_V2__ */\n' + html[idx:]
        changed.append("6. Marker added")

# Safe write
tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("Changes:")
for c in changed:
    print("  " + c)
print("")
print("SUCCESS. Unlock tab additions applied.")
