import io, sys, os, re

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ---- 1. Faster typing: 110-160ms per char ----
old = 'var speed = 220 + Math.random() * 80;'
new = 'var speed = 110 + Math.random() * 50;'
if old in html:
    html = html.replace(old, new, 1)
    print("1. Typing speed: 110-160ms/char.")

# ---- 2. Global persistent AudioContext + robust playNotify ----
new_notify = '''/* ===== Robust audio: global ctx + resume on any interaction ===== */
var globalAudioCtx = null;
function getAudioCtx() {
  if (globalAudioCtx) return globalAudioCtx;
  try {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (Ctx) globalAudioCtx = new Ctx();
  } catch (e) {}
  return globalAudioCtx;
}
function resumeAudio() {
  var c = getAudioCtx();
  if (c && c.state === "suspended") {
    try { c.resume(); } catch (e) {}
  }
}
try {
  ["touchstart","touchend","click","keydown"].forEach(function(ev){
    document.addEventListener(ev, resumeAudio, true);
  });
} catch (e) {}

function playNotify() {
  if (!assistSoundOn) return;
  var c = getAudioCtx();
  if (!c) return;
  if (c.state === "suspended") { try { c.resume(); } catch (e) {} }
  try {
    var now = c.currentTime;
    var o1 = c.createOscillator(), g1 = c.createGain();
    o1.connect(g1); g1.connect(c.destination);
    o1.type = "sine";
    o1.frequency.setValueAtTime(880, now);
    g1.gain.setValueAtTime(0.0001, now);
    g1.gain.exponentialRampToValueAtTime(0.45, now + 0.008);
    g1.gain.exponentialRampToValueAtTime(0.0001, now + 0.13);
    o1.start(now); o1.stop(now + 0.15);
    var o2 = c.createOscillator(), g2 = c.createGain();
    o2.connect(g2); g2.connect(c.destination);
    o2.type = "sine";
    o2.frequency.setValueAtTime(1245, now + 0.10);
    g2.gain.setValueAtTime(0.0001, now + 0.10);
    g2.gain.exponentialRampToValueAtTime(0.45, now + 0.11);
    g2.gain.exponentialRampToValueAtTime(0.0001, now + 0.26);
    o2.start(now + 0.10); o2.stop(now + 0.30);
  } catch (e) {}
}'''

# Replace the entire old playNotify block (from "function playNotify" to its closing brace)
pat = re.compile(r'function playNotify\s*\(\s*\)\s*\{.*?\n\}', re.DOTALL)
if pat.search(html):
    html = pat.sub(new_notify, html, count=1)
    print("2. playNotify upgraded.")
else:
    print("2. WARN: playNotify not found")

# ---- 3. Call resumeAudio when opening Assist + on tab switch ----
old = 'function openAssistantTab() {\n  primeAssistAudio();'
new = 'function openAssistantTab() {\n  if (typeof resumeAudio === "function") resumeAudio();\n  primeAssistAudio();'
if old in html:
    html = html.replace(old, new, 1)
    print("3. Assist tab resumes audio.")

old2 = 'function showTab(name) {'
new2 = 'function showTab(name) {\n  if (typeof resumeAudio === "function") resumeAudio();'
if old2 in html:
    html = html.replace(old2, new2, 1)
    print("4. Tab switch resumes audio.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Speed + sound patched.")
