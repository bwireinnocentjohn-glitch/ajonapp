import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__FINAL_POLISH__" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

# Safe emoji building
MIDDOT = chr(0x22EE)
CROSS  = chr(0x2715)
COIN   = chr(0x1FA99)
MOBILE = chr(0x1F4F1)
CHECK  = chr(0x2713)
BULLET = chr(0x2022)

# ============================================================
# 1. Add three-dot button in header (inside hdr-right)
# ============================================================
old_hdr = '<div class="netdot" id="netDot"></div>'
if old_hdr in html and "hdr-menu-btn" not in html:
    new_hdr = ('<div class="netdot" id="netDot"></div>\n'
               '      <button class="hdr-menu-btn" onclick="openCreditsModal()" title="Credits">'
               + MIDDOT + '</button>')
    html = html.replace(old_hdr, new_hdr, 1)
    print("1. Credits three-dot button added to header")

# ============================================================
# 2. Add WhatsApp share button below cat-bar
# ============================================================
old_cat = '<div class="cat-bar" id="catBar"></div>'
if old_cat in html and "wa-share-btn" not in html:
    new_cat = (old_cat + '\n'
               '      <div class="wa-share-bar">\n'
               '        <button class="wa-share-btn" onclick="shareWhatsApp()">'
               + MOBILE + ' Share Ajon on WhatsApp</button>\n'
               '      </div>')
    html = html.replace(old_cat, new_cat, 1)
    print("2. WhatsApp share button added below cat-bar")

# ============================================================
# 3. Add credits modal before </body>
# ============================================================
CREDITS_MODAL = '''
<div class="credits-modal" id="creditsModal">
  <div class="credits-inner">
    <button class="credits-close" onclick="closeCreditsModal()">''' + CROSS + '''</button>
    <h3>AJON</h3>
    <p class="credits-sub">African Jobs Natured</p>
    <div class="credits-line">Sponsored by</div>
    <div class="credits-bullet">''' + BULLET + ''' Mt Cc Limited</div>
    <div class="credits-bullet">''' + BULLET + ''' Mater Production J</div>
    <div class="credits-bullet">''' + BULLET + ''' Matrix Miy</div>
    <div class="credits-line">CEO</div>
    <div class="credits-bullet">''' + BULLET + ''' B.Innocent.J</div>
    <div class="credits-line">Marketing Manager</div>
    <div class="credits-bullet">''' + BULLET + ''' Patience N.</div>
    <div class="credits-line">Service Engineers</div>
    <div class="credits-bullet">''' + BULLET + ''' Ajon Inno</div>
    <div class="credits-bullet">''' + BULLET + ''' Mater Dei</div>
    <div class="credits-bullet">''' + BULLET + ''' End' Lamb</div>
    <div class="credits-line">Product took 368 days</div>
    <div class="credits-line">Made in Company by GitiSee High Tech Computers</div>
    <div class="credits-divider"></div>
    <div class="credits-notice-title">Copyright</div>
    <div class="credits-notice">Reserved</div>
    <div class="credits-notice-title">Notice</div>
    <div class="credits-notice">This Application's Content Should not be reproduced in Any Means, Without Written Agreement from the CEO, The Company, AJON Community and All Contributers to the App Development. This software Should stay as it's. Copyright Laws Shall Apply to Whoever Miss handle the software as Written Above.</div>
    <div class="credits-notice">By Using the Software You Agree to the terms And Conditions of The AJON Inc, AJON Ltd, AJON Engineering Company.</div>
    <div class="credits-notice">Thanks for Using this Software, We wish success as you keep Using the Ajon App.</div>
    <div class="credits-divider"></div>
    <div class="credits-notice-title">Rights Reserved</div>
    <div class="credits-notice">AJON Copyright owner</div>
    <div class="credits-url">www.ajon.com</div>
  </div>
</div>
'''

if "</body>" in html and "credits-modal" not in html:
    html = html.replace("</body>", CREDITS_MODAL + "\n</body>", 1)
    print("3. Credits modal added")

# ============================================================
# 4. Add CSS
# ============================================================
CSS = '''
/* ===== Final polish CSS ===== */
.hdr-menu-btn {
  background: transparent;
  border: 1px solid rgba(0,200,83,.4);
  color: #00c853;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  font-size: 18px;
  font-weight: 900;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  margin-left: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hdr-menu-btn:active { background: rgba(0,200,83,.15); }
.credits-modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  z-index: 200; background: rgba(0,0,0,.92);
  display: none; align-items: center; justify-content: center;
  padding: 20px;
}
.credits-modal.open { display: flex; }
.credits-inner {
  background: #0f0f0f;
  border: 1px solid #00c853;
  border-radius: 16px;
  padding: 20px;
  max-width: 480px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  position: relative;
}
.credits-close {
  position: absolute; top: 10px; right: 10px;
  background: transparent; border: 0; color: #fff;
  font-size: 20px; cursor: pointer; padding: 4px 10px;
}
.credits-inner h3 {
  color: #00c853; font-size: 22px; font-weight: 900;
  letter-spacing: 3px; margin-bottom: 4px; text-align: center;
}
.credits-sub { color: #8f8f8f; text-align: center; font-size: 12px; margin-bottom: 16px; letter-spacing: 1px; }
.credits-line { color: #00c853; font-weight: 800; font-size: 12px; margin-top: 10px; letter-spacing: .5px; text-transform: uppercase; }
.credits-bullet { color: #e6e6e6; font-size: 13px; margin-top: 4px; }
.credits-divider { height: 1px; background: rgba(0,200,83,.3); margin: 14px 0; }
.credits-notice-title { color: #ffb300; font-weight: 800; font-size: 12px; letter-spacing: .5px; margin-top: 10px; text-transform: uppercase; }
.credits-notice { color: #c8c8c8; font-size: 12px; line-height: 1.6; margin-top: 6px; }
.credits-url { color: #00c853; text-align: center; font-weight: 800; font-size: 13px; margin-top: 14px; letter-spacing: 1px; }

.wa-share-bar { margin: 4px 16px 12px; }
.wa-share-btn {
  display: block; width: 100%;
  background: linear-gradient(135deg, #25D366, #128C7E);
  color: #fff; font-weight: 800; font-size: 13.5px;
  border: 0; border-radius: 12px;
  padding: 12px 16px; font-family: inherit; cursor: pointer;
  box-shadow: 0 4px 14px rgba(37,211,102,.35);
}
.wa-share-btn:active { transform: scale(.97); }

.coins-badge {
  display: inline-block;
  background: linear-gradient(135deg, #2a1a00, #1a0f00);
  border: 1px solid #ffb300;
  color: #ffb300;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 12.5px;
  font-weight: 800;
  margin-bottom: 14px;
  letter-spacing: .3px;
}
.coins-badge b { color: #fff; }

.tier-card {
  background: #0f0f0f;
  border: 1px solid rgba(0,200,83,.4);
  border-radius: 16px;
  padding: 18px 16px;
  width: 100%;
  max-width: 440px;
  margin-bottom: 14px;
  position: relative;
}
.tier-card.master {
  border: 2px solid #00c853;
  box-shadow: 0 6px 24px rgba(0,200,83,.2);
}
.tier-card h3 {
  font-size: 18px; font-weight: 900; letter-spacing: 2px;
  color: #00c853; margin-bottom: 6px; text-align: center;
}
.tier-price { text-align: center; font-size: 24px; font-weight: 900; color: #fff; margin-bottom: 4px; }
.tier-price small { font-size: 12px; color: #8f8f8f; font-weight: 700; }
.tier-sub { text-align: center; font-size: 11.5px; color: #ffb300; font-weight: 800; letter-spacing: 1px; margin-bottom: 12px; text-transform: uppercase; }
.tier-perks { list-style: none; padding: 0; margin: 0 0 14px; }
.tier-perks li { color: #dcdcdc; font-size: 12.5px; padding: 4px 0 4px 18px; position: relative; line-height: 1.5; }
.tier-perks li:before { content: "''' + CHECK + '''"; position: absolute; left: 0; top: 4px; color: #00c853; font-weight: 900; }
.best-badge {
  position: absolute; top: -10px; right: 14px;
  background: #00c853; color: #000;
  font-size: 10px; font-weight: 900;
  letter-spacing: .8px;
  padding: 4px 10px; border-radius: 999px;
}
.tier-btn {
  display: block; width: 100%;
  background: linear-gradient(135deg, #00c853, #009624);
  color: #fff; font-weight: 800; font-size: 14.5px;
  border: 0; border-radius: 12px;
  padding: 13px 16px; font-family: inherit; cursor: pointer;
  letter-spacing: .3px;
}
'''

if ".hdr-menu-btn" not in html:
    idx = html.rfind('</style>')
    if idx != -1:
        html = html[:idx] + CSS + '\n' + html[idx:]
        print("4. Final polish CSS added")

# ============================================================
# 5. Replace renderPayment with two-tier version
# ============================================================
marker = "function renderPayment("
start = html.find(marker)
if start != -1:
    brace = html.find("{", start)
    depth = 0; i = brace; end = -1
    while i < len(html):
        ch = html[i]
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: end = i + 1; break
        i += 1
    if end != -1:
        NEW_RENDER = '''function renderPayment() { /* __FINAL_POLISH__ */
  var area = byId("videoArea");
  if (!area) return;
  var coins = 0;
  try { coins = readJSON("ajon_coins", 0) || 0; } catch(e) {}
  var coinsHtml = '<div style="text-align:center;"><div class="coins-badge">''' + COIN + ''' Coins: <b>' + coins + '</b> \\u2014 Share more to earn</div></div>';

  if (!isDateValid()) {
    area.innerHTML = '<div class="paywall-wrap">' + coinsHtml +
      '<div class="paywall-card"><div class="paywall-lock">\\u23F0</div>' +
      '<div class="paywall-title">Set Correct Date</div>' +
      '<p class="paywall-sub">Please set automatic date and time in phone settings.</p>' +
      '<div class="paywall-instructions">' +
      '<div class="line"><span class="ic">\\u2192</span><div>Open <strong>Settings</strong>.</div></div>' +
      '<div class="line"><span class="ic">\\u2192</span><div><strong>System \\u2192 Date &amp; Time</strong>.</div></div>' +
      '<div class="line"><span class="ic">\\u2192</span><div>Turn on <strong>Set automatically</strong>.</div></div>' +
      '</div></div></div>';
    return;
  }

  if (isSubscribed()) {
    var daysLeft = Math.ceil((subscriptionEndDate - Date.now()) / (1000 * 60 * 60 * 24));
    var hoursLeft = Math.ceil((subscriptionEndDate - Date.now()) / (1000 * 60 * 60));
    var human = daysLeft >= 1 ? daysLeft + " days" : hoursLeft + " hours";
    area.innerHTML = '<div class="paywall-wrap">' + coinsHtml +
      '<div class="paywall-active-card">' +
      '<h3>\\u2705 Unlocked</h3>' +
      '<div class="num">' + human + '</div><div class="lbl">REMAINING</div>' +
      '<div class="exp">Valid until <strong>' + escapeHTML(formatDateShort(subscriptionEndDate)) + '</strong></div>' +
      '<div class="paywall-divider"></div>' +
      '<div class="paywall-perks">' +
      '<div class="pr"><span class="tick">\\u2713</span>All 1500+ businesses</div>' +
      '<div class="pr"><span class="tick">\\u2713</span>Expert unlimited</div>' +
      '<div class="pr"><span class="tick">\\u2713</span>Assistant unlimited</div>' +
      '<div class="pr"><span class="tick">\\u2713</span>Notes + PDF export</div></div></div></div>';
    return;
  }

  var trialLeft = trialMinutesLeft();
  var trialMsg = trialLeft > 0
    ? '<div class="paywall-instructions" style="background:linear-gradient(135deg,#001a0a,#003d14);border-color:rgba(0,200,83,.55);"><div style="text-align:center;font-size:13px;color:#00c853;font-weight:800;">\\uD83C\\uDF81 Free preview: ' + formatTrialTime(trialLeft) + ' left</div></div>'
    : '';

  area.innerHTML = '<div class="paywall-wrap">' + coinsHtml + trialMsg +
    '<div class="tier-card">' +
    '<h3>SENIOR</h3>' +
    '<div class="tier-price">5,000 UGX <small>/ 30 days</small></div>' +
    '<div class="tier-sub">For Starter</div>' +
    '<ul class="tier-perks">' +
    '<li>Free data bundle for this app daily</li>' +
    '<li>Access to 500 businesses only, categorized well</li>' +
    '<li>Expert answers 200 questions per day limit</li>' +
    '<li>PDF export</li>' +
    '<li>No Supplier contacts</li>' +
    '<li>Motivation quotes yes</li>' +
    '<li>Chats and Expert answers</li>' +
    '</ul>' +
    '<button class="tier-btn" onclick="selectTier(\\'senior\\')">Pay 5,000 UGX</button>' +
    '</div>' +
    '<div class="tier-card master">' +
    '<div class="best-badge">BEST VALUE</div>' +
    '<h3>MASTER</h3>' +
    '<div class="tier-price">15,000 UGX <small>/ 30 days</small></div>' +
    '<div class="tier-sub">Full Property</div>' +
    '<ul class="tier-perks">' +
    '<li>Free data bundle for 30 days</li>' +
    '<li>All 1500 businesses unlocked</li>' +
    '<li>Expert UNLIMITED + remembers yesterday</li>' +
    '<li>Assistant tab real chat unlimited</li>' +
    '<li>Supplier directory: phone numbers + price</li>' +
    '<li>Voice button Luganda</li>' +
    '<li>Save to Notes + Make PDF Business Plan</li>' +
    '<li>No limit, no ads</li>' +
    '</ul>' +
    '<button class="tier-btn" onclick="selectTier(\\'master\\')">Pay 15,000 UGX</button>' +
    '</div>' +
    '<div id="verifySection"></div>' +
    '</div>';
}

function selectTier(tier) {
  var verifyEl = byId("verifySection");
  if (!verifyEl) return;
  var price = (tier === "senior") ? "5,000" : "15,000";
  var expiryTime = currentHourEndsAt();
  var expiryText = new Date(expiryTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  verifyEl.innerHTML = '<div class="paywall-card" style="margin-top:14px;">' +
    '<div class="paywall-title">Verify ' + tier.toUpperCase() + '</div>' +
    '<div class="paywall-instructions">' +
    '<div class="line"><span class="ic">1.</span><div>Pay <strong>' + price + ' UGX</strong> to MTN <span class="num">' + PAYMENT_INFO.phone + '</span> Name <strong>' + PAYMENT_INFO.name + '</strong>.</div></div>' +
    '<div class="line"><span class="ic">2.</span><div>After payment, <strong>beep or call</strong> to get the current hour password.</div></div>' +
    '<div class="line"><span class="ic">3.</span><div>Enter the password below and tap <strong>Verify</strong>.</div></div>' +
    '</div>' +
    '<div class="paywall-hint">Password refreshes hourly. Current expires at <strong style="color:#00c853;">' + expiryText + '</strong>.</div>' +
    '<div class="paywall-input-row"><input id="txInput" type="text" placeholder="Enter hourly password" autocomplete="off" autocapitalize="off" spellcheck="false"></div>' +
    '<button id="verifyBtn" onclick="verifyPassword()">Verify and Unlock 30 Days</button>' +
    '<div id="statusMsg"></div>' +
    '</div>';
  setTimeout(function(){
    var inp = byId("txInput");
    if (inp) inp.focus();
  }, 100);
}
'''
        html = html[:start] + NEW_RENDER + html[end:]
        print("5. renderPayment replaced with two-tier version")

# ============================================================
# 6. Add JS helpers before last </script>
# ============================================================
HELPERS = '''
/* ===== Final polish JS ===== */
function openCreditsModal() {
  var m = byId("creditsModal");
  if (m) m.classList.add("open");
}
function closeCreditsModal() {
  var m = byId("creditsModal");
  if (m) m.classList.remove("open");
}
function getCoins() {
  try { return readJSON("ajon_coins", 0) || 0; } catch(e) { return 0; }
}
function shareWhatsApp() {
  var msg = "Install The Ajon 1500+ Business App, With Free Data Buddle for 30 days, learn from Expert and Divorce From Poverty, At 5000/= 30 days Fully";
  var url = "https://wa.me/?text=" + encodeURIComponent(msg);
  try { window.open(url, "_blank"); } catch(e) { try { location.href = url; } catch(x) {} }
  try {
    var c = getCoins() + 1;
    writeJSON("ajon_coins", c);
  } catch(e) {}
}
'''
if "openCreditsModal" not in html:
    idx = html.rfind('</script>')
    if idx != -1:
        html = html[:idx] + HELPERS + '\n' + html[idx:]
        print("6. Credits + share JS added")

# ============================================================
# Safe write
# ============================================================
tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("")
print("SUCCESS. Final polish applied.")
