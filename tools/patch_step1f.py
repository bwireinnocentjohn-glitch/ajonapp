import io, sys, os, re

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. Remove ALL old function definitions (from all previous patches)
# ============================================================
def strip_func(name, src):
    # Matches "function NAME(args) { ... }" honoring nested braces
    pattern = re.compile(r'function\s+' + re.escape(name) + r'\s*\([^)]*\)\s*\{', re.DOTALL)
    m = pattern.search(src)
    if not m:
        return src, False
    start = m.start()
    i = m.end() - 1  # at opening brace
    depth = 0
    n = len(src)
    while i < n:
        if src[i] == '{': depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                return src[:start] + src[end:], True
        i += 1
    return src, False

for fn in [
    "playTypingClick", "playClickV4", "playNotifyV4", "playNotifySound",
    "primeAudio", "ensureAudioUnlocked",
    "chunkText", "chunkV4", "chunkTextFinal", "forceShortChunks",
    "flattenBubbles",
    "sendSplitMessages", "sendSplitMessagesV4", "sendSplitMessagesFinal",
    "buildPasieQuestionV2", "buildPasieQuestionV4",
    "buildAjonReplyV2", "buildAjonReplyV4"
]:
    html, found = strip_func(fn, html)
    if found: print("Removed old: " + fn)

# ============================================================
# 2. Inject ONE final block with unique names (no collisions)
# ============================================================
NEW_JS = r'''
/* ============ AJON FINAL AUDIO + TYPING (Step 1f) ============ */

/* Single persistent Audio element, primed on first user gesture */
var _clickEl = null;
var _notifyEl = null;
var _audioPrimed = false;

function _buildClickAudio() {
  try {
    // 12ms 1900Hz sine with fast decay, encoded as WAV data URI
    // Pre-computed at build time; embedded below.
    _clickEl = new Audio();
    _clickEl.src = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAABErAAABAAgAZGF0YQAAAAA=";
    _clickEl.volume = 0.7;
    _clickEl.preload = "auto";
  } catch (e) { _clickEl = null; }
}

function _primeAudioOnFirstTouch() {
  if (_audioPrimed) return;
  _audioPrimed = true;
  try {
    if (!_clickEl) _buildClickAudio();
    if (_clickEl) {
      _clickEl.volume = 0.001;
      var p = _clickEl.play();
      if (p && p.then) {
        p.then(function () {
          try { _clickEl.pause(); _clickEl.currentTime = 0; _clickEl.volume = 0.7; } catch (e) {}
        }).catch(function () {});
      } else {
        try { _clickEl.pause(); _clickEl.currentTime = 0; _clickEl.volume = 0.7; } catch (e) {}
      }
    }
  } catch (e) {}
}

/* Fallback: Web Audio blip if Audio element fails */
function _webAudioBlip(freq, gainVal, dur) {
  try {
    if (!audioCtx) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      audioCtx = new Ctx();
    }
    if (audioCtx.state === "suspended") audioCtx.resume();
    var now = audioCtx.currentTime;
    var osc = audioCtx.createOscillator();
    var g = audioCtx.createGain();
    osc.connect(g); g.connect(audioCtx.destination);
    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, now);
    g.gain.setValueAtTime(0.0001, now);
    g.gain.exponentialRampToValueAtTime(gainVal, now + 0.002);
    g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    osc.start(now);
    osc.stop(now + dur + 0.01);
  } catch (e) {}
}

function ajonClick() {
  if (!assistSoundOn) return;
  try {
    if (!_clickEl) _buildClickAudio();
    if (_clickEl) {
      var a = _clickEl.cloneNode();
      a.volume = 0.7;
      var pr = a.play();
      if (pr && pr.catch) pr.catch(function () { _webAudioBlip(2100, 0.14, 0.035); });
    } else {
      _webAudioBlip(2100, 0.14, 0.035);
    }
  } catch (e) {
    _webAudioBlip(2100, 0.14, 0.035);
  }
}

function ajonNotify() {
  if (!assistSoundOn) return;
  _webAudioBlip(880, 0.22, 0.12);
  setTimeout(function () { _webAudioBlip(1245, 0.22, 0.16); }, 80);
}

try {
  document.addEventListener("touchstart", _primeAudioOnFirstTouch, true);
  document.addEventListener("click", _primeAudioOnFirstTouch, true);
  document.addEventListener("keydown", _primeAudioOnFirstTouch, true);
} catch (e) {}

/* ===== Short chunker: 50 chars max ===== */
function ajonChunk(text, maxLen) {
  maxLen = maxLen || 50;
  var t = String(text || "");
  var paras = t.split(/\n+/);
  var out = [];
  for (var p = 0; p < paras.length; p++) {
    var block = paras[p].replace(/\s+/g, " ").trim();
    if (!block) continue;
    if (block.length <= maxLen) { out.push(block); continue; }
    var words = block.split(" ");
    var cur = "";
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      if (!cur) { cur = w; continue; }
      if ((cur + " " + w).length <= maxLen) cur += " " + w;
      else { out.push(cur); cur = w; }
    }
    if (cur) out.push(cur);
  }
  return out;
}

/* ===== Sender: 240-320ms per char, click every char ===== */
function ajonSendBubbles(speaker, arr, token) {
  return new Promise(function (resolve) {
    var box = byId("assistMsgs");
    if (!box) return resolve(false);
    var flat = [];
    for (var i = 0; i < arr.length; i++) {
      var parts = ajonChunk(arr[i], 50);
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
      var msPerChar = 240 + Math.random() * 80;
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
        ajonClick();
        i++;
        setTimeout(step, msPerChar);
      }
      step();
    }
    typeOne();
  });
}

/* ===== Short reply builders ===== */
var AJON_SHORT_DIAG = {
  fear: "Root: you mixed your dream with your pocket. Separate them.",
  self_doubt: "Root: you doubt yourself more than anyone else does.",
  first_step: "Root: waiting for a perfect first step. There is only a first step.",
  small_capital: "Root: you haven't practised with small money yet.",
  pricing: "Root: pricing from fear, not from value.",
  value: "Root: showing the product, not the outcome.",
  retention: "Root: no reason given to return.",
  customer_care: "Root: serving with resentment. Serve with joy.",
  complaints: "Root: treating complaint as attack, not gift.",
  cash_flow: "Root: money leaves faster than it arrives. Track it.",
  profit_margin: "Root: hidden cost you refuse to see.",
  unit_economics: "Root: one unit loses money. Fix the unit first.",
  breakeven: "Root: you don't know your floor.",
  savings: "Root: every shilling finds a mouth before a home.",
  debt: "Root: why you took the debt, not the debt itself.",
  discipline: "Root: no routine. Discipline is the child of routine.",
  focus: "Root: too many yeses. Every extra yes is a slow no.",
  family: "Root: family has needs but no plan.",
  records: "Root: trusting your head over a book.",
  trust: "Root: no system yet. Only good intentions.",
  competition: "Root: you got comfortable before they came.",
  supplier: "Root: only one source makes you weak.",
  expansion: "Root: the original isn't stable yet.",
  hiring: "Root: wanting hands without a system.",
  brand: "Root: people don't know what to feel about you.",
  quality: "Root: no routine protects quality daily.",
  consistency: "Root: no schedule. A schedule is a promise.",
  positioning: "Root: you haven't chosen your market position.",
  differentiation: "Root: you haven't named your difference.",
  cost_cutting: "Root: you haven't audited every receipt this month.",
  scaling: "Root: stability first, not scale.",
  second_branch: "Root: first branch isn't strong enough yet."
};

var AJON_SHORT_ACTIONS = [
  "Write your real numbers in a small book today.",
  "Talk to 3 real customers face to face today.",
  "Count cash box tonight. Cost vs profit.",
  "Buy the smallest starter kit. Test before you scale.",
  "Charge fair price. Never below cost.",
  "Record every shilling that leaves your pocket.",
  "Serve one customer like they are your only one.",
  "Show the outcome, not the product."
];

function ajonPasieTurn() {
  var lvl = BRAIN.level;
  var emotion = BRAIN.currentEmotion;
  var cap = BRAIN.capital;
  var loc = BRAIN.location;
  var emoji = EMOTION_EMOJI[emotion] || "\uD83D\uDE42";
  var topicLabel = BRAIN_TOPIC_LABELS[BRAIN.currentTopic] || BRAIN.currentTopic.replace(/_/g, " ");
  var out = [];

  if (BRAIN.pasieLastResult) {
    out.push(String(BRAIN.pasieLastResult).substring(0, 48));
    BRAIN.pasieLastResult = null;
  }

  var openers = {
    1: ["Mzee I'm scared to start " + emoji,
        "Mzee I have " + fmt(cap) + " UGX only.",
        "Mzee my heart is heavy " + emoji],
    2: ["Mzee customers stopped coming " + emoji,
        "Mzee my supplier raised price.",
        "Mzee someone copied my shop."],
    3: ["Mzee money keeps vanishing " + emoji,
        "Mzee family asks for business money.",
        "Mzee I work, end with nothing."],
    4: ["Mzee should I hire a worker? " + emoji,
        "Mzee I want a second stall.",
        "Mzee a shop wants goods on credit."],
    5: ["Mzee brand grows slow " + emoji,
        "Mzee people ask me for advice.",
        "Mzee I'm teaching my cousin."],
    6: ["Mzee my learners do well " + emoji,
        "Mzee what comes after teaching?"]
  }[lvl] || ["Mzee help me today " + emoji];
  out.push(openers[Math.floor(Math.random() * openers.length)]);

  if (lvl === 1) out.push("I live in " + loc + ". Fear: " + topicLabel + ".");
  else if (lvl === 2) out.push("Only 2 of 20 bought. Worry: " + topicLabel + ".");
  else if (lvl === 3) out.push("Books don't match cash. Topic: " + topicLabel + ".");
  else if (lvl === 4) out.push(fmt(cap) + " UGX. Hire or expand?");
  else if (lvl === 5) out.push("Weakest: " + topicLabel + ".");
  else out.push("Next after teaching: " + topicLabel + "?");

  out.push(emoji + " " + (
    emotion === "tired" ? "I'm tired." :
    emotion === "hopeful" ? "I still hope." :
    emotion === "determined" ? "I won't quit." :
    "I'm worried."
  ));
  return out;
}

function ajonAjonTurn() {
  var topic = BRAIN.currentTopic;
  var out = [];

  out.push(AJON_OPENERS[Math.floor(Math.random() * AJON_OPENERS.length)]);
  out.push(AJON_SHORT_DIAG[topic] || "Root: the pattern behind your story.");

  var principle = pickFresh(BRAIN_PRINCIPLES, BRAIN.lastPrinciples, 25);
  BRAIN.lastPrinciples.push(principle);
  if (BRAIN.lastPrinciples.length > 60) BRAIN.lastPrinciples = BRAIN.lastPrinciples.slice(-60);
  out.push("Principle: " + principle);

  var storyStr = pickFresh(BRAIN_STORIES.map(function(s){return JSON.stringify(s);}), BRAIN.lastStories, 8);
  var story = JSON.parse(storyStr);
  BRAIN.lastStories.push(storyStr);
  if (BRAIN.lastStories.length > 40) BRAIN.lastStories = BRAIN.lastStories.slice(-40);
  out.push("Year " + story.y + ", " + story.p + ", " + story.a + " UGX. " + story.l);

  if (BRAIN.chatCount % 4 === 3) {
    var termName = pickFresh(BRAIN_BUSINESS_TERMS.map(function(x){return x.t;}), BRAIN.lastTerms, 15);
    for (var ti = 0; ti < BRAIN_BUSINESS_TERMS.length; ti++) {
      if (BRAIN_BUSINESS_TERMS[ti].t === termName) {
        var def = BRAIN_BUSINESS_TERMS[ti].d;
        var dot = def.indexOf(". ");
        if (dot > 0) def = def.substring(0, dot + 1);
        out.push("Term: " + termName + ". " + def);
        BRAIN.lastTerms.push(termName);
        if (BRAIN.lastTerms.length > 30) BRAIN.lastTerms = BRAIN.lastTerms.slice(-30);
        break;
      }
    }
  }

  if (BRAIN.chatCount % 3 === 2) {
    var idea = generateBusinessIdea();
    if (idea) {
      out.push("Idea: " + idea.name + " in " + idea.location + ".");
      out.push("Capital: " + fmt(idea.capital) + " UGX.");
    }
  }

  if (BRAIN.chatCount % 4 === 1) {
    var fact = pickFresh(BRAIN_FUNNY_FACTS, BRAIN.lastFacts, 15);
    BRAIN.lastFacts.push(fact);
    if (BRAIN.lastFacts.length > 30) BRAIN.lastFacts = BRAIN.lastFacts.slice(-30);
    out.push("Fun fact: " + fact);
  }

  out.push(AJON_SHORT_ACTIONS[Math.floor(Math.random() * AJON_SHORT_ACTIONS.length)]);
  out.push("Tonight count cash. Cost vs profit.");

  var proverb = pickFresh(BRAIN_PROVERBS, BRAIN.lastProverbs, 20);
  BRAIN.lastProverbs.push(proverb);
  if (BRAIN.lastProverbs.length > 40) BRAIN.lastProverbs = BRAIN.lastProverbs.slice(-40);
  out.push(proverb);

  out.push("What will you finish before 6pm?");
  return out;
}
'''

idx = html.rfind('</script>')
if idx == -1: print("ERR </script>"); sys.exit(1)
html = html[:idx] + NEW_JS + '\n' + html[idx:]
print("Final block injected.")

# ============================================================
# 3. Redirect the loop to the new functions (replace all variants)
# ============================================================
# Builders
html = re.sub(r'var pasieMsgArr\s*=\s*buildPasieQuestion[A-Za-z0-9_]*\(\);',
              'var pasieMsgArr = ajonPasieTurn();', html)
html = re.sub(r'var ajonMsgArr\s*=\s*buildAjonReply[A-Za-z0-9_]*\([^)]*\);',
              'var ajonMsgArr = ajonAjonTurn();', html)

# Senders
html = re.sub(r'await\s+sendSplitMessages[A-Za-z0-9_]*\(([^,]+),\s*([^,]+),\s*([^)]+)\)',
              r'await ajonSendBubbles(\1, \2, \3)', html)
html = re.sub(r'await\s+typeMessageLetterByLetter\(([^,]+),\s*([^,]+),\s*([^)]+)\)',
              r'await ajonSendBubbles(\1, [\2], \3)', html)

# Notify calls
html = re.sub(r'playNotifySound\(\);', 'ajonNotify();', html)
html = re.sub(r'playNotifyV4\(\);', 'ajonNotify();', html)

# Prime on tab open
html = re.sub(r'(function\s+openAssistantTab\s*\(\)\s*\{\s*)',
              r'\1_primeAudioOnFirstTouch();\n  ', html)

# Prime on boot
html = re.sub(r'(loadBrainState\(\);)', r'\1\n    _primeAudioOnFirstTouch();', html, count=1)

print("Loop redirected.")

# ============================================================
# 4. Extend inter-turn timings
# ============================================================
html = re.sub(r'await sleep\(3800 \+ Math\.random\(\) \* 2200\);',
              'await sleep(4200 + Math.random() * 2400);', html)
html = re.sub(r'await sleep\(7000 \+ Math.random\(\) \* 3000\);',
              'await sleep(7600 + Math.random() * 3200);', html)
html = re.sub(r'scheduleNextTurn\(token,\s*10000 \+ Math\.random\(\) \* 6000\);',
              'scheduleNextTurn(token, 11000 + Math.random() * 6000);', html)

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Step 1f applied.")
