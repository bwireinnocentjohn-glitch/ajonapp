import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__ajonFinalVerifyV1" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

FINAL_JS = '''
/* ==========================================================
   Ajon — Final boot verification + self-heal
   ========================================================== */
(function(){
  if (window.__ajonFinalVerifyV1) return;
  window.__ajonFinalVerifyV1 = true;

  var CRITICAL = [
    "showTab","filterCat","renderCatBar","renderTutorials",
    "hasFullAccess","isSubscribed","isTrialActive","canAccess",
    "trialMinutesLeft","renderPayment","updateTrialBar",
    "ensureSubscriptionStatus","startSubscriptionCheck",
    "askExpert","expertOnEnter","expertOnLeave",
    "openAssistantTab","startAssistantChat","pauseAssistantChat","clearAssistantChat",
    "toggleFav","saveNote","renderNotes","openTutorial","closeDetail",
    "writeJSON","readJSON","escapeHTML","fmt"
  ];

  function verify(){
    try {
      var missing = [];
      for (var i = 0; i < CRITICAL.length; i++) {
        if (typeof window[CRITICAL[i]] !== "function") missing.push(CRITICAL[i]);
      }
      if (missing.length) {
        try { console.warn("[Ajon] Missing functions: " + missing.join(", ")); } catch(e){}
      } else {
        try { console.log("[Ajon] Boot OK. All critical functions present."); } catch(e){}
      }
    } catch(e){}

    try { if (typeof renderPayment === "function") renderPayment(); } catch(e){}
    try { if (typeof updateTrialBar === "function") updateTrialBar(); } catch(e){}
    try { if (typeof ensureSubscriptionStatus === "function") ensureSubscriptionStatus(); } catch(e){}
    try { if (typeof startSubscriptionCheck === "function") startSubscriptionCheck(); } catch(e){}

    try {
      var chatPanel = document.getElementById("panel-chat");
      if (chatPanel && chatPanel.classList.contains("active")) {
        if (typeof hasFullAccess === "function" && !hasFullAccess()) {
          if (typeof openAssistantTab === "function") openAssistantTab();
        }
      }
    } catch(e){}

    try {
      var aiPanel = document.getElementById("panel-ai");
      if (aiPanel && aiPanel.classList.contains("active")) {
        if (typeof expertGate === "function") expertGate();
      }
    } catch(e){}
  }

  if (document.readyState === "complete") {
    setTimeout(verify, 900);
  } else {
    window.addEventListener("load", function(){ setTimeout(verify, 900); });
  }
})();
'''

idx = html.rfind('</script>')
if idx == -1:
    print("ERR: </script> not found"); sys.exit(1)
html = html[:idx] + FINAL_JS + '\n' + html[idx:]

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS. Final verification layer installed.")
