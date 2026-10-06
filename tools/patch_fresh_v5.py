import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('var BRAIN_PRINCIPLES = [')
if start == -1:
    print("ERROR: brain start not found"); sys.exit(1)
body_pos = html.rfind('</body>')
end = html.rfind('</script>', start, body_pos)
if end == -1:
    print("ERROR: closing </script> not found"); sys.exit(1)
print("Removing old chat brain: " + str(end - start) + " bytes")

NEW_BRAIN = r'''

/* =====================================================================
   AJON CHAT v5 — Fresh short messages + notification sound per message
   ===================================================================== */

var BRAIN_STATE_KEY = "ajon_chat_v5";
var BRAIN = {
  chatCount: 0, level: 1, capital: 86000, location: "Busia",
  isRunning: false, isPaused: true, messages: [],
  pasieResult: null
};
var assistSoundOn = true;
var chatTimer = null;
var chatToken = 0;

/* ---- Notification sound: single primed Audio element ---- */
var _notifyAudio = null;
var _notifyPrimed = false;
var NOTIFY_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAABErAAABAAgAZGF0YQAAAAA=";

function primeAssistAudio() {
  if (_notifyPrimed) return;
  _notifyPrimed = true;
  try {
    if (!_notifyAudio) _notifyAudio = new Audio(NOTIFY_WAV);
    _notifyAudio.volume = 0.001;
    var p = _notifyAudio.play();
    if (p && p.then) p.then(function () {
      try { _notifyAudio.pause(); _notifyAudio.currentTime = 0; _notifyAudio.volume = 0.6; } catch (e) {}
    }).catch(function () {});
    else { try { _notifyAudio.pause(); _notifyAudio.currentTime = 0; _notifyAudio.volume = 0.6; } catch (e) {} }
  } catch (e) {}
}

try {
  document.addEventListener("touchstart", primeAssistAudio, true);
  document.addEventListener("click", primeAssistAudio, true);
  document.addEventListener("keydown", primeAssistAudio, true);
} catch (e) {}

function playNotify() {
  if (!assistSoundOn) return;
  try {
    if (!audioCtx) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    }
    if (audioCtx) {
      if (audioCtx.state === "suspended") audioCtx.resume();
      var now = audioCtx.currentTime;
      var o1 = audioCtx.createOscillator();
      var g1 = audioCtx.createGain();
      o1.connect(g1); g1.connect(audioCtx.destination);
      o1.type = "sine"; o1.frequency.setValueAtTime(880, now);
      g1.gain.setValueAtTime(0.0001, now);
      g1.gain.exponentialRampToValueAtTime(0.28, now + 0.01);
      g1.gain.exponentialRampToValueAtTime(0.0001, now + 0.10);
      o1.start(now); o1.stop(now + 0.12);
      var o2 = audioCtx.createOscillator();
      var g2 = audioCtx.createGain();
      o2.connect(g2); g2.connect(audioCtx.destination);
      o2.type = "sine"; o2.frequency.setValueAtTime(1245, now + 0.09);
      g2.gain.setValueAtTime(0.0001, now + 0.09);
      g2.gain.exponentialRampToValueAtTime(0.28, now + 0.10);
      g2.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
      o2.start(now + 0.09); o2.stop(now + 0.25);
      return;
    }
  } catch (e) {}
  try {
    if (!_notifyAudio) _notifyAudio = new Audio(NOTIFY_WAV);
    var a = _notifyAudio.cloneNode();
    a.volume = 0.6;
    var pr = a.play();
    if (pr && pr.catch) pr.catch(function () {});
  } catch (e) {}
}

/* ---- Content banks (short strings, max ~50 chars each) ---- */
var EMOJIS = {
  scared: "\uD83D\uDE30", hopeful: "\uD83D\uDE42", tired: "\uD83D\uDE29",
  worried: "\uD83D\uDE1F", determined: "\uD83D\uDCAA", proud: "\uD83D\uDE0A"
};
var EMOTION_KEYS = Object.keys(EMOJIS);

var AJON_OPENERS = [
  "My child, sit down.",
  "Listen to me carefully.",
  "Good question. Hear me.",
  "I hear you. Now hear me.",
  "Let me tell you the truth."
];

var AJON_DIAGS = [
  "Root is dream mixed with pocket.",
  "Root is fear of loss, not loss.",
  "Root is no system. Only hopes.",
  "Root is pricing from fear.",
  "Root is no records, only memory.",
  "Root is too many yeses. No focus.",
  "Root is no daily routine.",
  "Root is family needs, no plan.",
  "Root is one supplier. Weak.",
  "Root is you got comfortable.",
  "Root is waiting for perfect step.",
  "Root is counting profit, ignoring cost.",
  "Root is service without love.",
  "Root is saving after, not before.",
  "Root is counting yearly, not daily."
];

var AJON_PRINCIPLES = [
  "Money follows trust.",
  "Trust follows consistency.",
  "Small profit repeated beats big.",
  "Save before you spend.",
  "Cash in hand beats credit.",
  "Fair price beats cheap price.",
  "Show up daily. That wins.",
  "Count cash every night.",
  "One well beats ten holes.",
  "Write it down. Memory lies.",
  "Fix the unit, then volume.",
  "Discipline stays. Motivation leaves.",
  "Buy in bulk or buy in pain.",
  "Reputation is real capital.",
  "Slow is smooth. Smooth is fast."
];

var AJON_ACTIONS = [
  "Write your numbers in a book today.",
  "Talk to 3 buyers today.",
  "Count your cash box tonight.",
  "Buy smallest starter kit today.",
  "Set one fair price. Never below cost.",
  "Record every shilling that leaves.",
  "Fix one leak before you grow.",
  "Serve one customer like your only one."
];

var AJON_PROVERBS = [
  "Slow is smooth. Smooth is fast.",
  "Start ugly. Refine daily.",
  "Show up. Show up. Show up.",
  "Small deeds done beat big plans.",
  "The market rewards patience.",
  "Discipline is born of routine.",
  "Fail. Learn. Try again.",
  "Consistency beats talent weekly.",
  "Write the goal where you see it.",
  "Prepare in peace for war."
];

var AJON_CLOSERS = [
  "What will you finish before 6pm?",
  "Tell me tomorrow what you did.",
  "Ask yourself tonight: did I do it?",
  "Count tomorrow. Tell me the number."
];

var PASIE_OPENERS = [
  "Mzee I am scared.",
  "Mzee I have only {cap} UGX.",
  "Mzee my heart is heavy.",
  "Mzee I feel alone in this.",
  "Mzee they say I am too young."
];

var PASIE_BODIES = [
  "I live in {loc}.",
  "Only 2 of 20 bought.",
  "My supplier raised price.",
  "Someone copied my shop.",
  "Money keeps vanishing.",
  "Family keeps asking for money.",
  "I work all day, end with nothing.",
  "I want five businesses at once.",
  "Should I hire a worker?",
  "I want a second stall.",
  "A shop wants goods on credit.",
  "My brand grows too slowly.",
  "I am teaching my cousin now."
];

var PASIE_CLOSERS = [
  "What do I do first?",
  "Tell me the truth, Mzee.",
  "Where did I go wrong?",
  "What is my first step?",
  "Am I on the right path?"
];

function ajon_pick(arr, key) {
  var i = Math.floor(Math.random() * arr.length);
  if (arr.length > 1 && i === BRAIN[key]) i = (i + 1) % arr.length;
  BRAIN[key] = i;
  return arr[i];
}

function ajon_fill(t) {
  return String(t)
    .replace(/\{cap\}/g, fmt(BRAIN.capital))
    .replace(/\{loc\}/g, BRAIN.location);
}

function ajon_chunk(text, maxLen) {
  maxLen = maxLen || 50;
  text = String(text || "").trim();
  if (!text) return [];
  if (text.length <= maxLen) return [text];
  var words = text.split(/\s+/);
  var out = [], cur = "";
  for (var i = 0; i < words.length; i++) {
    if (!cur) { cur = words[i]; continue; }
    if ((cur + " " + words[i]).length <= maxLen) cur += " " + words[i];
    else { out.push(cur); cur = words[i]; }
  }
  if (cur) out.push(cur);
  return out;
}

function ajon_buildPasie() {
  var out = [];
  var emoji = EMOJIS[BRAIN.currentEmotion] || "\uD83D\uDE42";
  if (BRAIN.pasieResult) { out.push(BRAIN.pasieResult); BRAIN.pasieResult = null; }
  out.push(ajon_fill(ajon_pick(PASIE_OPENERS, "lp1")) + " " + emoji);
  out.push(ajon_fill(ajon_pick(PASIE_BODIES, "lp2")));
  out.push(ajon_pick(PASIE_CLOSERS, "lp3"));
  return out;
}

function ajon_buildAjon() {
  var out = [];
  out.push(ajon_pick(AJON_OPENERS, "la1"));
  out.push(ajon_pick(AJON_DIAGS, "la2"));
  out.push("Principle: " + ajon_pick(AJON_PRINCIPLES, "la3"));
  out.push(ajon_pick(AJON_ACTIONS, "la4"));
  out.push(ajon_pick(AJON_PROVERBS, "la5"));
  out.push(ajon_pick(AJON_CLOSERS, "la6"));
  return out;
}

function ajon_makeRow(speaker, text, withCursor) {
  var isAjon = speaker === "ajon";
  var name = isAjon ? "Mzee Ajon" : "Pasie";
  var cls = isAjon ? "ajon" : "pasie";
  var emoji = isAjon ? "\uD83E\uDDD1\uD83C\uDFFE\u200D\uD83C\uDFEB" : "\uD83E\uDDD1\uD83C\uDFFE\u200D\uD83C\uDF3E";
  var div = document.createElement("div");
  div.className = "bubble-row " + cls;
  div.innerHTML =
    '<div class="bubble-avatar">' + emoji + '</div>' +
    '<div class="bubble-body">' +
      '<div class="bubble-name">' + name + '</div>' +
      '<div class="bubble ' + cls + (withCursor ? " typing-cursor" : "") + '"></div>' +
    '</div>';
  if (text !== null && text !== undefined) {
    div.querySelector(".bubble").innerHTML = escapeHTML(text).replace(/\n/g, "<br>");
  }
  return div;
}

function ajon_showTyping(speaker) {
  var box = byId("assistMsgs");
  if (!box) return null;
  var isAjon = speaker === "ajon";
  var name = isAjon ? "Mzee Ajon" : "Pasie";
  var cls = isAjon ? "ajon" : "pasie";
  var emoji = isAjon ? "\uD83E\uDDD1\uD83C\uDFFE\u200D\uD83C\uDFEB" : "\uD83E\uDDD1\uD83C\uDFFE\u200D\uD83C\uDF3E";
  var div = document.createElement("div");
  div.className = "bubble-row " + cls + " typing-row";
  div.innerHTML =
    '<div class="bubble-avatar">' + emoji + '</div>' +
    '<div class="bubble-body">' +
      '<div class="bubble-name">' + name + ' <span class="typing-mini">typing</span></div>' +
      '<div class="bubble ' + cls + ' bubble-typing">' +
        '<span class="dot"></span><span class="dot"></span><span class="dot"></span>' +
      '</div>' +
    '</div>';
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

function ajon_send(speaker, bubbles, token) {
  return new Promise(function (resolve) {
    var box = byId("assistMsgs");
    if (!box) return resolve(false);
    var flat = [];
    for (var i = 0; i < bubbles.length; i++) {
      var parts = ajon_chunk(bubbles[i], 50);
      for (var j = 0; j < parts.length; j++) if (parts[j]) flat.push(parts[j]);
    }
    var idx = 0;
    function typeOne() {
      if (token !== chatToken || !BRAIN.isRunning) return resolve(false);
      if (idx >= flat.length) return resolve(true);
      var text = flat[idx];
      var row = ajon_makeRow(speaker, null, true);
      box.appendChild(row);
      var bubble = row.querySelector(".bubble");
      var i = 0;
      var speed = 220 + Math.random() * 80;
      function step() {
        if (token !== chatToken || !BRAIN.isRunning) {
          bubble.classList.remove("typing-cursor");
          return resolve(false);
        }
        if (i >= text.length) {
          bubble.classList.remove("typing-cursor");
          playNotify();
          idx++;
          setTimeout(typeOne, 1200 + Math.random() * 500);
          return;
        }
        bubble.innerHTML = escapeHTML(text.substring(0, i + 1));
        box.scrollTop = box.scrollHeight;
        i++;
        setTimeout(step, speed);
      }
      step();
    }
    typeOne();
  });
}

function ajon_sleep(ms) {
  return new Promise(function (r) { setTimeout(r, ms); });
}

function loadBrainState() {
  try {
    var raw = localStorage.getItem(BRAIN_STATE_KEY);
    if (raw) {
      var s = JSON.parse(raw);
      BRAIN.chatCount = s.chatCount || 0;
      BRAIN.capital = s.capital || 86000;
      BRAIN.level = s.level || 1;
      BRAIN.messages = s.messages || [];
    }
  } catch (e) {}
  BRAIN.isRunning = false;
  BRAIN.isPaused = true;
}

function saveBrainState() {
  try {
    localStorage.setItem(BRAIN_STATE_KEY, JSON.stringify({
      chatCount: BRAIN.chatCount,
      capital: BRAIN.capital,
      level: BRAIN.level,
      messages: BRAIN.messages.slice(-40)
    }));
  } catch (e) {}
}

function pauseAssistantChat() {
  BRAIN.isRunning = false;
  BRAIN.isPaused = true;
  chatToken++;
  if (chatTimer) { clearTimeout(chatTimer); chatTimer = null; }
  var rows = document.querySelectorAll(".typing-row");
  for (var i = 0; i < rows.length; i++) if (rows[i].parentNode) rows[i].parentNode.removeChild(rows[i]);
}

function openAssistantTab() {
  primeAssistAudio();
  var box = byId("assistMsgs");
  if (!box) return;
  if (!hasFullAccess()) {
    box.innerHTML = '<div class="coming-soon"><span class="bigicon">\uD83D\uDD12</span><h3>Assistant Locked</h3><p>Unlock to watch Ajon teach Pasie.</p></div>';
    return;
  }
  if (box.querySelector(".coming-soon")) box.innerHTML = "";
  if (box.children.length === 0 && BRAIN.messages.length > 0) {
    for (var i = 0; i < BRAIN.messages.length; i++) {
      var m = BRAIN.messages[i];
      var parts = String(m.t).split("\n");
      for (var j = 0; j < parts.length; j++) {
        if (parts[j]) box.appendChild(ajon_makeRow(m.s, parts[j], false));
      }
    }
  }
  if (!BRAIN.isRunning) startAssistantChat();
}

function startAssistantChat() {
  if (!hasFullAccess()) return;
  if (BRAIN.isRunning) return;
  BRAIN.isRunning = true;
  BRAIN.isPaused = false;
  chatToken++;
  runTurn(chatToken);
}

async function runTurn(token) {
  if (token !== chatToken || !BRAIN.isRunning) return;
  var box = byId("assistMsgs");
  if (!box) return;

  var t1 = ajon_showTyping("pasie");
  await ajon_sleep(1800 + Math.random() * 1000);
  if (token !== chatToken || !BRAIN.isRunning) { if (t1 && t1.parentNode) t1.parentNode.removeChild(t1); return; }
  if (t1 && t1.parentNode) t1.parentNode.removeChild(t1);

  BRAIN.currentEmotion = EMOTION_KEYS[Math.floor(Math.random() * EMOTION_KEYS.length)];
  var pasieBubbles = ajon_buildPasie();
  var ok1 = await ajon_send("pasie", pasieBubbles, token);
  if (!ok1) return;
  BRAIN.messages.push({ s: "pasie", t: pasieBubbles.join("\n"), ts: Date.now() });
  if (BRAIN.messages.length > 40) BRAIN.messages = BRAIN.messages.slice(-40);
  saveBrainState();

  await ajon_sleep(1400);
  if (token !== chatToken || !BRAIN.isRunning) return;

  var t2 = ajon_showTyping("ajon");
  await ajon_sleep(2500 + Math.random() * 1500);
  if (token !== chatToken || !BRAIN.isRunning) { if (t2 && t2.parentNode) t2.parentNode.removeChild(t2); return; }
  if (t2 && t2.parentNode) t2.parentNode.removeChild(t2);

  var ajonBubbles = ajon_buildAjon();
  var ok2 = await ajon_send("ajon", ajonBubbles, token);
  if (!ok2) return;
  BRAIN.messages.push({ s: "ajon", t: ajonBubbles.join("\n"), ts: Date.now() });
  if (BRAIN.messages.length > 40) BRAIN.messages = BRAIN.messages.slice(-40);

  BRAIN.chatCount++;
  BRAIN.capital += Math.floor(Math.random() * 5000) + 1500;
  if (BRAIN.chatCount >= 300) BRAIN.level = 6;
  else if (BRAIN.chatCount >= 150) BRAIN.level = 5;
  else if (BRAIN.chatCount >= 80) BRAIN.level = 4;
  else if (BRAIN.chatCount >= 40) BRAIN.level = 3;
  else if (BRAIN.chatCount >= 15) BRAIN.level = 2;
  else BRAIN.level = 1;

  var results = [
    "Mzee I saved 12,000 yesterday.",
    "Mzee I found 8,000 leaking.",
    "Mzee two old customers came back.",
    "Mzee I talked to 3 buyers.",
    "Mzee I wrote my numbers in a book."
  ];
  BRAIN.pasieResult = Math.random() < 0.6
    ? results[Math.floor(Math.random() * results.length)]
    : null;
  saveBrainState();

  chatTimer = setTimeout(function () {
    if (token !== chatToken) return;
    runTurn(token);
  }, 5500 + Math.random() * 3500);
}

function clearAssistantChat() {
  if (!hasFullAccess()) return;
  pauseAssistantChat();
  BRAIN.messages = [];
  BRAIN.chatCount = 0;
  BRAIN.level = 1;
  BRAIN.capital = 86000;
  BRAIN.pasieResult = null;
  saveBrainState();
  var box = byId("assistMsgs");
  if (box) box.innerHTML = "";
  setTimeout(function () { startAssistantChat(); }, 600);
}

function toggleAssistSound() {
  assistSoundOn = !assistSoundOn;
  var b = byId("soundToggleBtn");
  if (b) b.textContent = assistSoundOn ? "\uD83D\uDD0A" : "\uD83D\uDD07";
}
function updateSoundButton() {
  var b = byId("soundToggleBtn");
  if (b) b.textContent = assistSoundOn ? "\uD83D\uDD0A" : "\uD83D\uDD07";
}
function avatarFallback(img, emoji) {
  try {
    var span = document.createElement("span");
    span.className = "avatar-emoji";
    span.textContent = emoji;
    img.parentNode.replaceChild(span, img);
  } catch (e) {}
}
'''

html = html[:start] + NEW_BRAIN + html[end:]

# Ensure sound button starts as ON
html = html.replace('id="soundToggleBtn" class="chat-hdr-btn" onclick="toggleAssistSound()" title="Sound on/off">\U0001F507',
                    'id="soundToggleBtn" class="chat-hdr-btn" onclick="toggleAssistSound()" title="Sound on/off">\U0001F50A')

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("SUCCESS. Fresh chat v5 (with notification sound) installed.")
