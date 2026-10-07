import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

def replace_function(src, func_name, new_func):
    marker = 'function ' + func_name + '('
    start = src.find(marker)
    if start == -1: return src, False
    brace = src.find('{', start)
    if brace == -1: return src, False
    depth = 0; i = brace
    while i < len(src):
        ch = src[i]
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return src[:start] + new_func + src[i+1:], True
        i += 1
    return src, False

# ============================================================
# FIX 1 — isSubscribed: defensive against NaN/null/undefined
# ============================================================
new_isSub = '''function isSubscribed() {
  try {
    if (typeof subscriptionEndDate !== "number") return false;
    if (isNaN(subscriptionEndDate)) return false;
    if (subscriptionEndDate <= 0) return false;
    return subscriptionEndDate > Date.now();
  } catch (e) { return false; }
}'''
html, ok = replace_function(html, "isSubscribed", new_isSub)
print("1. isSubscribed: " + ("OK" if ok else "NOT FOUND"))

# ============================================================
# FIX 2 — clearAssistantChat: only chat-specific keys removed
# ============================================================
new_clear = '''function clearAssistantChat() {
  if (!hasFullAccess()) return;
  try { pauseAssistantChat(); } catch(e) {}
  /* Only remove chat-specific keys. Preserve trial, subscription, favorites, notes, config. */
  try {
    var chatKeys = [
      "ajon_chat_v12","ajon_chat_v11","ajon_chat_v10","ajon_chat_v9",
      "ajon_chat_v8","ajon_chat_v5",
      "ajon_brain_state_v3","ajon_brain_state_v2"
    ];
    for (var i = 0; i < chatKeys.length; i++) {
      try { localStorage.removeItem(chatKeys[i]); } catch(e) {}
    }
  } catch (e) {}
  /* Reset in-memory chat state only */
  try {
    if (typeof BRAIN !== "undefined") {
      BRAIN.messages = [];
      BRAIN.chatCount = 0;
      BRAIN.level = 1;
      BRAIN.capital = 86000;
      BRAIN.pasieResult = null;
      BRAIN.currentTopicId = null;
      BRAIN.lastTopics = [];
      BRAIN.lastPrinciple = null;
      BRAIN.pendingBiz = null;
      BRAIN.bizIdx = {};
      BRAIN.rotIdx = {};
      BRAIN.lastMode = "question";
    }
  } catch (e) {}
  /* Clear only the visible DOM area of the assistant tab */
  try {
    var box = byId("assistMsgs");
    if (box) box.innerHTML = "";
  } catch (e) {}
  setTimeout(function () {
    try { startAssistantChat(); } catch(e) {}
  }, 700);
}'''
html, ok = replace_function(html, "clearAssistantChat", new_clear)
print("2. clearAssistantChat: " + ("SAFE" if ok else "NOT FOUND"))

# ============================================================
# FIX 3 — renderCatBar: direct .onclick property (most reliable)
# ============================================================
new_cat = '''function renderCatBar() {
  var bar = byId("catBar");
  if (!bar) return;
  var h = '<div class="cat-chip active" data-cat="all">All</div>';
  for (var i = 0; i < CATEGORIES.length; i++) {
    h += '<div class="cat-chip" data-cat="' + CATEGORIES[i].id + '">' + CATEGORIES[i].name + '</div>';
  }
  bar.innerHTML = h;
  var chips = bar.querySelectorAll(".cat-chip");
  for (var k = 0; k < chips.length; k++) {
    (function(chip){
      chip.onclick = function(ev){
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        var c = chip.getAttribute("data-cat");
        if (c) { try { window.filterCat(c); } catch(e) {} }
        return false;
      };
      chip.addEventListener("click", function(ev){
        if (ev) { ev.preventDefault(); ev.stopPropagation(); }
        var c = chip.getAttribute("data-cat");
        if (c) { try { window.filterCat(c); } catch(e) {} }
      }, false);
    })(chips[k]);
  }
}'''
html, ok = replace_function(html, "renderCatBar", new_cat)
print("3. renderCatBar: " + ("SAFE" if ok else "NOT FOUND"))

# ============================================================
# FIX 4 — filterCat: normalized + defensive
# ============================================================
new_filter = '''function filterCat(cat) {
  try {
    cat = String(cat == null ? "all" : cat).toLowerCase();
    if (cat !== "all") {
      var known = false;
      for (var k = 0; k < CATEGORIES.length; k++) {
        if (CATEGORIES[k].id === cat) { known = true; break; }
      }
      if (!known) cat = "all";
    }
    currentCategory = cat;
    var chips = document.querySelectorAll(".cat-chip");
    for (var i = 0; i < chips.length; i++) {
      if (chips[i].getAttribute("data-cat") === cat) chips[i].classList.add("active");
      else chips[i].classList.remove("active");
    }
    tutOffset = 0;
    try { currentItems = []; } catch(e) {}
    renderTutorials(true);
  } catch (e) {
    try { console.log("filterCat error:", e); } catch(x) {}
  }
}
try { window.filterCat = filterCat; } catch(e) {}'''
html, ok = replace_function(html, "filterCat", new_filter)
print("4. filterCat: " + ("SAFE" if ok else "NOT FOUND"))

# ============================================================
# FIX 5 — ensureSubscriptionStatus + periodic checker
# ============================================================
SUB_CHECK = '''
/* ============================================================
   Subscription expiry enforcement — locks app after 30 days
   ============================================================ */
var _ajonSubTimer = null;
var _ajonLastKnownSub = -1;

function ensureSubscriptionStatus() {
  try {
    /* Defensive: force number */
    if (typeof subscriptionEndDate !== "number" || isNaN(subscriptionEndDate)) {
      subscriptionEndDate = 0;
    }
    var now = Date.now();
    var subscribedNow = subscriptionEndDate > now;
    var changed = (subscribedNow !== (_ajonLastKnownSub === 1));
    _ajonLastKnownSub = subscribedNow ? 1 : 0;

    /* When subscription just expired, kick out of gated tabs */
    if (changed && !subscribedNow) {
      try { if (typeof pauseAssistantChat === "function") pauseAssistantChat(); } catch(e) {}
      try {
        var panelChat = byId("panel-chat");
        var panelAi = byId("panel-ai");
        if (panelChat && panelChat.classList.contains("active")) {
          try { showTab("tutorials"); } catch(e) {}
        }
        if (panelAi && panelAi.classList.contains("active")) {
          try { if (typeof expertGate === "function") expertGate(); } catch(e) {}
        }
      } catch(e) {}
    }
    /* Refresh UI so locks/unlocks reflect reality */
    try { if (typeof updateTrialBar === "function") updateTrialBar(); } catch(e) {}
    try { if (typeof renderPayment === "function") renderPayment(); } catch(e) {}
    try {
      /* If subscription expired, re-render tutorials so locked cards appear */
      if (changed && !subscribedNow) {
        if (typeof tutOffset !== "undefined") tutOffset = 0;
        if (typeof renderTutorials === "function") renderTutorials(true);
      }
    } catch(e) {}
  } catch (e) {}
}

function startSubscriptionCheck() {
  try {
    if (_ajonSubTimer) clearInterval(_ajonSubTimer);
    _ajonSubTimer = setInterval(ensureSubscriptionStatus, 60000);
  } catch(e) {}
}

/* Re-check when app returns to foreground */
try {
  document.addEventListener("visibilitychange", function () {
    try { if (!document.hidden) ensureSubscriptionStatus(); } catch(e) {}
  });
} catch(e) {}
'''
if "ensureSubscriptionStatus" not in html:
    idx = html.rfind('</script>')
    if idx == -1: print("ERR </script>"); sys.exit(1)
    html = html[:idx] + SUB_CHECK + '\n' + html[idx:]
    print("5. Subscription checker installed")
else:
    print("5. Subscription checker already present")

# ============================================================
# FIX 6 — Hook the subscription check into boot
# ============================================================
old_boot_marker = "    startTrialTick();"
new_boot_marker = '''    startTrialTick();
    try { if (typeof ensureSubscriptionStatus === "function") ensureSubscriptionStatus(); } catch(e) {}
    try { if (typeof startSubscriptionCheck === "function") startSubscriptionCheck(); } catch(e) {}'''
if old_boot_marker in html and "startSubscriptionCheck()" not in html.split("startTrialTick();")[1][:200]:
    html = html.replace(old_boot_marker, new_boot_marker, 1)
    print("6. Boot hooked into subscription check")
else:
    print("6. Boot hook already in place or marker missing")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Hard fix applied.")
