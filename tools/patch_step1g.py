import io, sys, os

HTML = 'www/index.html'

# Find the most recent working backup
BACKUPS = [
    'www/index.step1f.bak.html',
    'www/index.step1d.bak.html',
    'www/index.step1c.bak.html',
    'www/index.step1b.bak.html',
    'www/index.step1.backup.html',
]
BACKUP = None
for b in BACKUPS:
    if os.path.exists(b):
        BACKUP = b
        break

if not BACKUP:
    print("ERROR: no backup found. Available files:")
    for f in os.listdir('www'):
        print("  - " + f)
    sys.exit(1)

print("Restoring from: " + BACKUP)
with io.open(BACKUP, 'r', encoding='utf-8') as f:
    html = f.read()

if "assistMsgs" not in html or "chat-header-bar" not in html:
    print("ERROR: backup missing chat elements"); sys.exit(1)

OVERRIDES = r'''
/* ============ AJON STEP 1g: safe overrides ============ */

(function setupAudioUnlock() {
  var ctx = null;
  function unlock() {
    try {
      if (!ctx) {
        var C = window.AudioContext || window.webkitAudioContext;
        if (C) ctx = new C();
      }
      if (ctx && ctx.state === "suspended") ctx.resume();
      if (ctx) {
        var b = ctx.createBuffer(1, 1, 22050);
        var s = ctx.createBufferSource();
        s.buffer = b;
        s.connect(ctx.destination);
        s.start(0);
      }
    } catch (e) {}
  }
  document.addEventListener("touchstart", unlock, true);
  document.addEventListener("click", unlock, true);
  document.addEventListener("keydown", unlock, true);
  window.__ajonGetCtx = function () {
    if (!ctx) unlock();
    return ctx;
  };
})();

function playClickV4() {
  if (typeof assistSoundOn !== "undefined" && !assistSoundOn) return;
  try {
    var c = window.__ajonGetCtx();
    if (!c) return;
    var now = c.currentTime;
    var o = c.createOscillator();
    var g = c.createGain();
    o.connect(g); g.connect(c.destination);
    o.type = "sine";
    o.frequency.value = 2100;
    g.gain.setValueAtTime(0.0001, now);
    g.gain.exponentialRampToValueAtTime(0.14, now + 0.002);
    g.gain.exponentialRampToValueAtTime(0.0001, now + 0.032);
    o.start(now);
    o.stop(now + 0.04);
  } catch (e) {}
}

function playNotifyV4() {
  if (typeof assistSoundOn !== "undefined" && !assistSoundOn) return;
  try {
    var c = window.__ajonGetCtx();
    if (!c) return;
    var now = c.currentTime;
    var o = c.createOscillator();
    var g = c.createGain();
    o.connect(g); g.connect(c.destination);
    o.type = "sine";
    o.frequency.setValueAtTime(900, now);
    o.frequency.setValueAtTime(1200, now + 0.08);
    g.gain.setValueAtTime(0.0001, now);
    g.gain.exponentialRampToValueAtTime(0.2, now + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, now + 0.18);
    o.start(now);
    o.stop(now + 0.2);
  } catch (e) {}
}

function ajonSplit(t, maxLen) {
  maxLen = maxLen || 48;
  var s = String(t || "").replace(/\s+/g, " ").trim();
  if (!s) return [];
  if (s.length <= maxLen) return [s];
  var out = [];
  var words = s.split(" ");
  var cur = "";
  for (var i = 0; i < words.length; i++) {
    var w = words[i];
    if (!cur) { cur = w; continue; }
    if ((cur + " " + w).length <= maxLen) cur += " " + w;
    else { out.push(cur); cur = w; }
  }
  if (cur) out.push(cur);
  return out;
}

function sendSplitMessagesV4(speaker, arr, token) {
  return new Promise(function (resolve) {
    var box = byId("assistMsgs");
    if (!box) return resolve(false);
    var flat = [];
    for (var i = 0; i < arr.length; i++) {
      var parts = ajonSplit(arr[i], 48);
      for (var j = 0; j < parts.length; j++) if (parts[j]) flat.push(parts[j]);
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
      var msPerChar = 200 + Math.random() * 60;
      function step() {
        if (token !== chatToken || !BRAIN.isRunning) {
          bubble.classList.remove("typing-cursor"); return resolve(false);
        }
        if (i >= text.length) {
          bubble.classList.remove("typing-cursor");
          idx++;
          setTimeout(typeOne, 1400 + Math.random() * 700);
          return;
        }
        bubble.innerHTML = escapeHTML(text.substring(0, i + 1)).replace(/\n/g, "<br>");
        box.scrollTop = box.scrollHeight;
        playClickV4();
        i++;
        setTimeout(step, msPerChar);
      }
      step();
    }
    typeOne();
  });
}

function buildPasieQuestionV4() {
  var lvl = BRAIN.level;
  var emotion = BRAIN.currentEmotion;
  var cap = BRAIN.capital;
  var loc = BRAIN.location;
  var emoji = EMOTION_EMOJI[emotion] || "\uD83D\uDE42";
  var topicLabel = BRAIN_TOPIC_LABELS[BRAIN.currentTopic] || BRAIN.currentTopic.replace(/_/g, " ");
  var out = [];
  if (BRAIN.pasieLastResult) {
    out.push(String(BRAIN.pasieLastResult).substring(0, 45));
    BRAIN.pasieLastResult = null;
  }
  var opener = "";
  if (lvl === 1) opener = "Mzee I'm scared to start " + emoji;
  else if (lvl === 2) opener = "Mzee customers stopped coming " + emoji;
  else if (lvl === 3) opener = "Mzee money keeps vanishing " + emoji;
  else if (lvl === 4) opener = "Mzee should I hire a worker? " + emoji;
  else if (lvl === 5) opener = "Mzee brand grows slow " + emoji;
  else opener = "Mzee what comes after teaching?";
  out.push(opener);
  out.push("I have " + fmt(cap) + " UGX in " + loc + ".");
  out.push("Topic: " + topicLabel + ".");
  out.push(emoji + " " + (
    emotion === "tired" ? "I'm tired." :
    emotion === "hopeful" ? "I still hope." :
    emotion === "determined" ? "I won't quit." :
    "I'm worried."
  ));
  return out;
}

function buildAjonReplyV4() {
  var topic = BRAIN.currentTopic;
  var out = [];
  out.push(AJON_OPENERS[Math.floor(Math.random() * AJON_OPENERS.length)]);
  var diag = (typeof AJON_DIAGNOSIS !== "undefined" && AJON_DIAGNOSIS[topic]) || "Root is deeper than your story.";
  var firstPeriod = diag.indexOf(". ");
  out.push(firstPeriod > 0 ? diag.substring(0, firstPeriod + 1) : diag);
  var principle = pickFresh(BRAIN_PRINCIPLES, BRAIN.lastPrinciples, 25);
  BRAIN.lastPrinciples.push(principle);
  if (BRAIN.lastPrinciples.length > 60) BRAIN.lastPrinciples = BRAIN.lastPrinciples.slice(-60);
  out.push("Principle: " + principle);
  var storyStr = pickFresh(BRAIN_STORIES.map(function(s){return JSON.stringify(s);}), BRAIN.lastStories, 8);
  var story = JSON.parse(storyStr);
  BRAIN.lastStories.push(storyStr);
  if (BRAIN.lastStories.length > 40) BRAIN.lastStories = BRAIN.lastStories.slice(-40);
  out.push("Year " + story.y + ", " + story.p + ". " + story.l);
  if (BRAIN.chatCount % 4 === 1) {
    var fact = pickFresh(BRAIN_FUNNY_FACTS, BRAIN.lastFacts, 15);
    BRAIN.lastFacts.push(fact);
    if (BRAIN.lastFacts.length > 30) BRAIN.lastFacts = BRAIN.lastFacts.slice(-30);
    out.push("Fact: " + fact);
  }
  out.push("Write your real numbers today.");
  out.push("Talk to 3 real customers.");
  var proverb = pickFresh(BRAIN_PROVERBS, BRAIN.lastProverbs, 20);
  BRAIN.lastProverbs.push(proverb);
  if (BRAIN.lastProverbs.length > 40) BRAIN.lastProverbs = BRAIN.lastProverbs.slice(-40);
  out.push(proverb);
  out.push("What will you finish before 6pm?");
  return out;
}
'''

idx = html.rfind('</script>')
if idx == -1:
    print("ERR: no </script>"); sys.exit(1)
html = html[:idx] + OVERRIDES + '\n' + html[idx:]

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("")
print("SUCCESS. Working chat restored + overrides applied.")
print("Chat will now be short, slow, and with click sound.")
