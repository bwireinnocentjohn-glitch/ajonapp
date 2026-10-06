import io, sys, os, re

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ========== A. Add new CSS overrides ==========
CSS_ADD = r'''
/* ========== Step 1c: distinct bubbles + tighter grouping ========== */
.bubble.ajon {
  background: #1a3a24 !important;
  color: #e6f7ea !important;
  border-left: 3px solid #00c853 !important;
}
.bubble.pasie {
  background: #006b4f !important;
  color: #ffffff !important;
  border-right: 3px solid #00ff99 !important;
}
.bubble-row.pasie .bubble-name { color: #00ff99 !important; }
.bubble-row.ajon .bubble-name { color: #00c853 !important; }
.bubble { font-size: 14px; line-height: 1.55; }
.bubble-row { margin-bottom: 2px; }
'''
idx = html.rfind('</style>')
if idx == -1: print("ERR </style>"); sys.exit(1)
html = html[:idx] + CSS_ADD + '\n' + html[idx:]
print("A. CSS overrides injected.")

# ========== B. Inject new aggressive chunker + louder sound + slower typing ==========
NEW_JS = r'''
/* ========== Step 1c overrides ========== */
function forceShortChunks(text, maxLen) {
  maxLen = maxLen || 65;
  var out = [];
  var blocks = String(text || "").split(/\n+/);
  for (var b = 0; b < blocks.length; b++) {
    var block = blocks[b].trim();
    if (!block) continue;
    if (block.length <= maxLen) { out.push(block); continue; }
    var sentences = block.match(/[^.!?]+[.!?]+/g) || [block];
    for (var s = 0; s < sentences.length; s++) {
      var sen = sentences[s].trim();
      if (!sen) continue;
      if (sen.length <= maxLen) { out.push(sen); continue; }
      var words = sen.split(/\s+/);
      var cur = "";
      for (var w = 0; w < words.length; w++) {
        if (!cur) { cur = words[w]; continue; }
        if ((cur + " " + words[w]).length <= maxLen) cur += " " + words[w];
        else { out.push(cur); cur = words[w]; }
      }
      if (cur) out.push(cur);
    }
  }
  return out;
}

function playTypingClick() {
  if (!assistSoundOn) return;
  try {
    if (!audioCtx) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      audioCtx = new Ctx();
    }
    if (audioCtx.state === "suspended") audioCtx.resume();
    var now = audioCtx.currentTime;
    var osc = audioCtx.createOscillator();
    var gain = audioCtx.createGain();
    osc.connect(gain); gain.connect(audioCtx.destination);
    osc.type = "sine";
    osc.frequency.setValueAtTime(2400 + Math.random() * 600, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.22, now + 0.003);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.045);
    osc.start(now);
    osc.stop(now + 0.05);
  } catch (e) {}
}

function sendSplitMessages(speaker, arr, token) {
  return new Promise(function (resolve) {
    var box = byId("assistMsgs");
    if (!box) return resolve(false);
    var flat = [];
    for (var i = 0; i < arr.length; i++) {
      var parts = forceShortChunks(arr[i], 65);
      for (var j = 0; j < parts.length; j++) {
        if (parts[j]) flat.push(parts[j]);
      }
    }
    var idx = 0;
    function typeOne() {
      if (token !== chatToken || !BRAIN.isRunning) return resolve(false);
      if (idx >= flat.length) return resolve(true);
      var text = flat[idx];
      var row = makeBubbleRow(speaker, null, true);
      box.appendChild(row);
      var bubble = row.querySelector(".bubble");
      var i = 0;
      var msPerChar = 110 + Math.random() * 55;
      function step() {
        if (token !== chatToken || !BRAIN.isRunning) {
          bubble.classList.remove("typing-cursor");
          return resolve(false);
        }
        if (i >= text.length) {
          bubble.classList.remove("typing-cursor");
          idx++;
          setTimeout(typeOne, 1400 + Math.random() * 800);
          return;
        }
        bubble.innerHTML = escapeHTML(text.substring(0, i + 1)).replace(/\n/g, "<br>");
        box.scrollTop = box.scrollHeight;
        playTypingClick();
        i++;
        setTimeout(step, msPerChar);
      }
      step();
    }
    typeOne();
  });
}
'''
idx = html.rfind('</script>')
if idx == -1: print("ERR </script>"); sys.exit(1)
html = html[:idx] + NEW_JS + '\n' + html[idx:]
print("B. New chunker + louder sound + slower typing injected.")

# ========== C. Extend thinking times ==========
old = 'await sleep(2900 + Math.random() * 1700);'
new = 'await sleep(3800 + Math.random() * 2200);'
if old in html:
    html = html.replace(old, new, 1); print("C1. Pasie thinking extended.")

old = 'await sleep(5800 + Math.random() * 2800);'
new = 'await sleep(7000 + Math.random() * 3000);'
if old in html:
    html = html.replace(old, new, 1); print("C2. Ajon thinking extended.")

old = 'scheduleNextTurn(token, 8000 + Math.random() * 5000);'
new = 'scheduleNextTurn(token, 10000 + Math.random() * 6000);'
if old in html:
    html = html.replace(old, new, 1); print("C3. Inter-turn delay extended.")

# ========== D. Ensure audio unlock is available at boot ==========
if "ensureAudioUnlocked();" not in html:
    old = '    loadBrainState();'
    new = '    loadBrainState();\n    if (typeof ensureAudioUnlocked === "function") ensureAudioUnlocked();'
    if old in html:
        html = html.replace(old, new, 1); print("D. Audio unlock called at boot.")
else:
    print("D. Audio unlock already at boot.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Step 1c applied.")
