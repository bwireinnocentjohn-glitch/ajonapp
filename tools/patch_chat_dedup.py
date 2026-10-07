import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. Bump chat state key -> v12 (clears stale chat on next launch)
# ============================================================
bumped = False
for k in ['"ajon_chat_v11"','"ajon_chat_v10"','"ajon_chat_v9"','"ajon_chat_v8"','"ajon_chat_v5"']:
    if k in html:
        html = html.replace(k, '"ajon_chat_v12"')
        bumped = True
        print("1. State key " + k + " -> v12")
if not bumped:
    print("1. WARN: no old state key found")

# ============================================================
# 2. Add dedup wrapper (runs after everything else loads)
# ============================================================
DEDUP_JS = r'''
/* ===== Chat: dedupe similar bubbles within a single turn ===== */
(function(){
  if (window.__ajonChatDedupV2) return;
  window.__ajonChatDedupV2 = true;

  function keyOf(s) {
    var t = String(s || "").toLowerCase().replace(/[^a-z0-9 ]/g, " ").trim();
    var w = t.split(/\s+/).filter(function(x){ return x.length > 0; });
    return w.slice(0, 4).join(" ");
  }

  function wrap(fn) {
    if (typeof window[fn] !== "function") return;
    var orig = window[fn];
    window[fn] = function(){
      var arr = orig.apply(this, arguments);
      if (!arr || !arr.length) return arr;
      var seen = {}, out = [];
      for (var i = 0; i < arr.length; i++) {
        var k = keyOf(arr[i]);
        if (!k) { out.push(arr[i]); continue; }
        if (!seen[k]) { seen[k] = 1; out.push(arr[i]); }
      }
      return out;
    };
  }

  var names = [
    "ajon_buildAjon","ajon_buildAjon2","buildAjonV6","buildAjonFinal",
    "buildAjonReply","buildAjonReplyV2","buildAjonReplyV4",
    "ajon_buildPasie","ajon_buildPasie2","buildPasieV6","buildPasieFinal",
    "buildPasieQuestion","buildPasieQuestionV2","buildPasieQuestionV4",
    "ajonPasieTurn","ajonAjonTurn","ajon_buildAjon","ajon_buildPasie"
  ];
  for (var i = 0; i < names.length; i++) wrap(names[i]);

  /* Also safe-guard the sender: drop empty/short duplicates in flat arrays */
  function wrapSender(fn) {
    if (typeof window[fn] !== "function") return;
    var orig = window[fn];
    window[fn] = function(speaker, arr, token){
      if (Array.isArray(arr) && arr.length > 1) {
        var seen = {}, out = [];
        for (var i = 0; i < arr.length; i++) {
          var k = keyOf(arr[i]);
          if (!k) { out.push(arr[i]); continue; }
          if (!seen[k]) { seen[k] = 1; out.push(arr[i]); }
        }
        arr = out;
      }
      return orig.call(this, speaker, arr, token);
    };
  }
  ["ajon_send","sendSplitMessages","sendSplitMessagesV4","sendSplitMessagesFinal","sendSplitMessagesV2"]
    .forEach(wrapSender);
})();
'''

idx = html.rfind('</script>')
if idx == -1:
    print("ERR </script>"); sys.exit(1)
html = html[:idx] + DEDUP_JS + '\n' + html[idx:]
print("2. Dedup wrapper installed")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Chat dedup + state bump applied.")
