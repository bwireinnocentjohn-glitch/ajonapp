import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "brain_biz.js" in html:
    print("Already patched. Exiting.")
    sys.exit(0)

# 1. Add script tags before </body>
SCRIPTS = '''
<script src="js/brain_biz.js"></script>
<script src="js/brain_wisdom.js"></script>
<script src="js/expertBrain.js"></script>
'''
if "</body>" in html:
    html = html.replace("</body>", SCRIPTS + "</body>", 1)
    print("1. Script tags added before </body>")

# 2. Add override at end of main script (before last </script>)
OVERRIDE = '''
/* ===== Expert Brain integration: redirect exComposeReply to buildExpertReply ===== */
(function(){
  if (window.__ajonBrainBridge) return;
  window.__ajonBrainBridge = true;

  function bridge(){
    try {
      if (typeof exComposeReply !== "function") return;
      if (exComposeReply.__ajonBridged) return;
      var orig = exComposeReply;
      var wrapped = function(q){
        try {
          if (typeof window.buildExpertReply === "function") {
            var r = window.buildExpertReply(q);
            if (r && r.length) return r;
          }
        } catch(e) {}
        return orig(q);
      };
      wrapped.__ajonBridged = true;
      exComposeReply = wrapped;
      try { window.exComposeReply = wrapped; } catch(e) {}
      try { console.log("[Ajon Brain] exComposeReply bridged to buildExpertReply"); } catch(e) {}
    } catch(e) {}
  }

  if (document.readyState === "complete") setTimeout(bridge, 300);
  else window.addEventListener("load", function(){ setTimeout(bridge, 300); });
})();
'''
idx = html.rfind('</script>')
if idx == -1:
    print("ERR: </script>"); sys.exit(1)
html = html[:idx] + OVERRIDE + '\n' + html[idx:]
print("2. Bridge override added")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Brain loading wired.")
