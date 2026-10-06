import io, sys, os, re, base64, struct, wave, math

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# --- Generate click WAV (short high tick) ---
def make_wav(freq, dur_ms, rate=22050, decay=45):
    buf = io.BytesIO()
    w = wave.open(buf, 'wb')
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
    n = int(rate * dur_ms / 1000)
    frames = []
    for i in range(n):
        env = math.exp(-i / decay)
        val = int(32767 * 0.55 * env * math.sin(2 * math.pi * freq * i / rate))
        frames.append(struct.pack('<h', val))
    w.writeframes(b''.join(frames)); w.close()
    return base64.b64encode(buf.getvalue()).decode()

CLICK_B64 = make_wav(1900, 12, 22050, 40)
NOTIFY_B64 = make_wav(1200, 90, 22050, 500)

NEW_JS = r'''
/* ===== Step 1d: bulletproof sound + ultra-short bubbles + slow typing ===== */
var TYPING_CLICK_B64 = "data:audio/wav;base64,__CLICK__";
var NOTIFY_B64 = "data:audio/wav;base64,__NOTIFY__";
var clickAudioProto = null;
var notifyAudioProto = null;

function primeAudio() {
  try {
    if (!clickAudioProto) clickAudioProto = new Audio(TYPING_CLICK_B64);
    if (!notifyAudioProto) notifyAudioProto = new Audio(NOTIFY_B64);
    clickAudioProto.volume = 0;
    notifyAudioProto.volume = 0;
    var p1 = clickAudioProto.play();
    if (p1 && p1.then) p1.then(function(){ clickAudioProto.pause(); clickAudioProto.currentTime = 0; clickAudioProto.volume = 0.55; }).catch(function(){});
    var p2 = notifyAudioProto.play();
    if (p2 && p2.then) p2.then(function(){ notifyAudioProto.pause(); notifyAudioProto.currentTime = 0; notifyAudioProto.volume = 0.6; }).catch(function(){});
  } catch (e) {}
}
try {
  document.addEventListener("touchstart", primeAudio, true);
  document.addEventListener("click", primeAudio, true);
  document.addEventListener("keydown", primeAudio, true);
} catch (e) {}

function playClickV4() {
  if (!assistSoundOn) return;
  try {
    var a = new Audio(TYPING_CLICK_B64);
    a.volume = 0.55;
    var pr = a.play();
    if (pr && pr.catch) pr.catch(function(){});
  } catch (e) {}
}
function playNotifyV4() {
  if (!assistSoundOn) return;
  try {
    var a = new Audio(NOTIFY_B64);
    a.volume = 0.65;
    var pr = a.play();
    if (pr && pr.catch) pr.catch(function(){});
  } catch (e) {}
}

function chunkV4(text, maxLen) {
  maxLen = maxLen || 55;
  var t = String(text || "");
  var paragraphs = t.split(/\n+/);
  var out = [];
  for (var p = 0; p < paragraphs.length; p++) {
    var block = paragraphs[p].replace(/\s+/g, " ").trim();
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

function sendSplitMessagesV4(speaker, arr, token) {
  return new Promise(function (resolve) {
    var box = byId("assistMsgs");
    if (!box) return resolve(false);
    var flat = [];
    for (var i = 0; i < arr.length; i++) {
      var parts = chunkV4(arr[i], 55);
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
      var msPerChar = 180 + Math.random() * 80;
      function step() {
        if (token !== chatToken || !BRAIN.isRunning) {
          bubble.classList.remove("typing-cursor"); return resolve(false);
        }
        if (i >= text.length) {
          bubble.classList.remove("typing-cursor");
          idx++;
          setTimeout(typeOne, 1500 + Math.random() * 900);
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

var SHORT_DIAG = {
  fear: "Root is your dream and your pocket are mixed. Separate them today.",
  pricing: "Root is you price from fear, not from value.",
  pricing_value: "Root is you are not showing the value clearly.",
  value: "Root is you show the product, not the outcome.",
  retention: "Root is you gave them no reason to return.",
  customer_care: "Root is you serve with resentment. Serve with joy.",
  complaints: "Root is you treat complaints as attack, not gift.",
  cash_flow: "Root is money leaves faster than it arrives. Track it.",
  profit_margin: "Root is your hidden costs. Find them.",
  unit_economics: "Root is one unit loses money. Fix the unit first.",
  breakeven: "Root is you don't know your floor.",
  savings: "Root is every shilling finds a mouth before a home.",
  debt: "Root is not debt. Root is why you took it.",
  discipline: "Root is no routine. Discipline is born from routine.",
  focus: "Root is too many yeses. Every extra yes is a slow no.",
  family: "Root is family has needs but no plan.",
  records: "Root is trusting your head over a book.",
  trust: "Root is you have no system yet. Only good intentions.",
  competition: "Root is you got comfortable before they came.",
  supplier: "Root is only one source. That makes you weak.",
  expansion: "Root is the original isn't stable yet.",
  hiring: "Root is you want hands without a system.",
  brand: "Root is people don't know what to feel about you.",
  quality: "Root is no routine protects quality daily.",
  consistency: "Root is no schedule. A schedule is a promise.",
  positioning: "Root is you haven't chosen your market position.",
  differentiation: "Root is you haven't named your difference.",
  cost_cutting: "Root is you haven't audited every receipt this month.",
  scaling: "Root is stability, not scale. Stable small first.",
  second_branch: "Root is the first branch isn't strong enough to hold alone."
};

function shortDiag(topic) {
  return SHORT_DIAG[topic] || "Root is not the story. Root is the pattern behind it.";
}

var SHORT_ACTIONS = [
  "Write your real numbers in a small book today.",
  "Talk to 3 real customers face to face today.",
  "Count your cash box tonight. Cost vs profit.",
  "Buy the smallest starter kit. Test before you scale.",
  "Charge fair price. Do not bargain below cost.",
  "Record every shilling that leaves your pocket.",
  "Serve one customer like they are your only one.",
  "Show your customer the outcome, not the product."
];

function buildPasieQuestionV4() {
  var lvl = BRAIN.level;
  var emotion = BRAIN.currentEmotion;
  var cap = BRAIN.capital;
  var loc = BRAIN.location;
  var emoji = EMOTION_EMOJI[emotion] || "\uD83D\uDE42";
  var topicLabel = BRAIN_TOPIC_LABELS[BRAIN.currentTopic] || BRAIN.currentTopic.replace(/_/g, " ");
  var out = [];

  if (BRAIN.pasieLastResult) {
    out.push(String(BRAIN.pasieLastResult).slice(0, 50));
    BRAIN.pasieLastResult = null;
  }

  var openers = {
    1: ["Mzee I am scared to start " + emoji,
        "Mzee I have " + fmt(cap) + " UGX only.",
        "Mzee my heart is heavy today " + emoji],
    2: ["Mzee customers stopped coming " + emoji,
        "Mzee my supplier raised price.",
        "Mzee someone copied my shop."],
    3: ["Mzee money keeps vanishing " + emoji,
        "Mzee family keeps asking for business money.",
        "Mzee I work all day end with nothing."],
    4: ["Mzee should I hire a worker? " + emoji,
        "Mzee I want a second stall.",
        "Mzee a shop wants goods on credit."],
    5: ["Mzee my brand grows slow " + emoji,
        "Mzee people now ask me advice.",
        "Mzee I am teaching my cousin."],
    6: ["Mzee my learners are doing well " + emoji,
        "Mzee what comes after teaching?"]
  }[lvl] || ["Mzee help me today " + emoji];
  out.push(openers[Math.floor(Math.random() * openers.length)]);

  if (lvl === 1) out.push("I live in " + loc + ". Main fear: " + topicLabel + ".");
  else if (lvl === 2) out.push("Only 2 out of 20 bought. Worry: " + topicLabel + ".");
  else if (lvl === 3) out.push("Books don't match cash. Topic: " + topicLabel + ".");
  else if (lvl === 4) out.push(fmt(cap) + " UGX. Hire or expand?");
  else if (lvl === 5) out.push("Weakest: " + topicLabel + ".");
  else out.push("Next after teaching: " + topicLabel + "?");

  out.push(emoji + " " + (
    emotion === "tired" ? "I am tired." :
    emotion === "hopeful" ? "I still hope." :
    emotion === "determined" ? "I won't quit." :
    "I am worried."
  ));
  return out;
}

function buildAjonReplyV4(pasieJoinedText) {
  var topic = BRAIN.currentTopic;
  var out = [];

  out.push(AJON_OPENERS[Math.floor(Math.random() * AJON_OPENERS.length)]);
  out.push(shortDiag(topic));

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
      out.push("Capital: " + fmt(idea.capital) + " UGX. Skill: " + idea.skill + ".");
    }
  }

  if (BRAIN.chatCount % 5 === 4 && typeof ALL_BUSINESSES !== "undefined" && ALL_BUSINESSES.length) {
    var idx = Math.floor(Math.random() * ALL_BUSINESSES.length);
    var b = ALL_BUSINESSES[idx];
    out.push("Study: " + b.t + ". Start " + fmt(b.cost) + " UGX, profit " + fmt(b.profit) + ".");
  }

  if (BRAIN.chatCount % 4 === 1) {
    var fact = pickFresh(BRAIN_FUNNY_FACTS, BRAIN.lastFacts, 15);
    BRAIN.lastFacts.push(fact);
    if (BRAIN.lastFacts.length > 30) BRAIN.lastFacts = BRAIN.lastFacts.slice(-30);
    out.push("Fun fact: " + fact);
  }

  out.push(SHORT_ACTIONS[Math.floor(Math.random() * SHORT_ACTIONS.length)]);
  out.push("Tonight count cash. Cost vs profit.");

  var proverb = pickFresh(BRAIN_PROVERBS, BRAIN.lastProverbs, 20);
  BRAIN.lastProverbs.push(proverb);
  if (BRAIN.lastProverbs.length > 40) BRAIN.lastProverbs = BRAIN.lastProverbs.slice(-40);
  out.push(proverb);

  out.push("What will you finish before 6pm?");
  return out;
}
'''
NEW_JS = NEW_JS.replace("__CLICK__", CLICK_B64).replace("__NOTIFY__", NOTIFY_B64)

# 1) Inject new JS before last </script>
idx = html.rfind('</script>')
if idx == -1: print("ERR </script>"); sys.exit(1)
html = html[:idx] + NEW_JS + '\n' + html[idx:]
print("1. V4 functions injected.")

# 2) Redirect loop to V4 builders
html = html.replace('var pasieMsgArr = buildPasieQuestionV2();',
                    'var pasieMsgArr = buildPasieQuestionV4();', 1)
html = html.replace('var ajonMsgArr = buildAjonReplyV2(pasieMsgArr.join(" "));',
                    'var ajonMsgArr = buildAjonReplyV4(pasieMsgArr.join(" "));', 1)

# 3) Redirect loop to V4 sender (only call sites, not definitions)
html = html.replace('= await sendSplitMessages(', '= await sendSplitMessagesV4(')
print("2. Loop redirected to V4.")

# 4) Replace notify sounds in loop
html = html.replace('  playNotifySound();\n  BRAIN.messages.push({ s: "pasie"',
                    '  playNotifyV4();\n  BRAIN.messages.push({ s: "pasie"', 1)
html = html.replace('  playNotifySound();\n  BRAIN.messages.push({ s: "ajon"',
                    '  playNotifyV4();\n  BRAIN.messages.push({ s: "ajon"', 1)
print("3. Notify sound switched to V4.")

# 5) Prime audio on openAssistantTab
old = 'function openAssistantTab() {\n  var box = byId("assistMsgs");\n  if (!box) return;'
new = 'function openAssistantTab() {\n  primeAudio();\n  var box = byId("assistMsgs");\n  if (!box) return;'
if old in html:
    html = html.replace(old, new, 1); print("4. primeAudio called on tab open.")
else:
    print("4. WARN: openAssistantTab signature not matched.")

# 6) Slow the inter-bubble delay even more
html = html.replace('setTimeout(typeOne, 1500 + Math.random() * 900);',
                    'setTimeout(typeOne, 1800 + Math.random() * 1000);')
print("5. Inter-bubble delay bumped.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Step 1d applied.")
