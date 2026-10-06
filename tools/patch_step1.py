import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found. Run from ~/ajon-app"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "sendSplitMessages" in html:
    print("Step 1 already applied. Skipping.")
    sys.exit(0)

NEW_JS = r'''
/* ========== Step 1: chat polish V2 ========== */
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
    osc.frequency.setValueAtTime(1700 + Math.random() * 500, now);
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.018, now + 0.004);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.035);
    osc.start(now);
    osc.stop(now + 0.04);
  } catch (e) {}
}

function firstSentences(s, n) {
  if (!s) return "";
  var parts = String(s).split(/\.\s+/);
  if (parts.length <= n) return s;
  return parts.slice(0, n).join(". ") + ".";
}

function buildPasieQuestionV2() {
  var lvl = BRAIN.level;
  var emotion = BRAIN.currentEmotion;
  var cap = BRAIN.capital;
  var loc = BRAIN.location;
  var emoji = EMOTION_EMOJI[emotion] || "\uD83D\uDE42";
  var topicLabel = BRAIN_TOPIC_LABELS[BRAIN.currentTopic] || BRAIN.currentTopic.replace(/_/g, " ");
  var out = [];

  if (BRAIN.pasieLastResult) {
    out.push(firstSentences(BRAIN.pasieLastResult, 2));
    BRAIN.pasieLastResult = null;
  }

  var openers = {
    1: ["Mzee, I'm scared to start " + emoji,
        "Mzee, I only have " + fmt(cap) + " UGX.",
        "Mzee, my heart is heavy today " + emoji],
    2: ["Mzee, my customers are not returning " + emoji,
        "Mzee, my supplier raised the price again.",
        "Mzee, someone opened the same shop next to mine."],
    3: ["Mzee, money keeps disappearing from my book.",
        "Mzee, my family keeps asking for business money.",
        "Mzee, I work all day and end with nothing " + emoji],
    4: ["Mzee, should I hire my first worker? " + emoji,
        "Mzee, I want a second stall.",
        "Mzee, a big shop wants credit from me."],
    5: ["Mzee, my brand grows but slow " + emoji,
        "Mzee, everyone now asks me for advice.",
        "Mzee, I am teaching my cousin now."],
    6: ["Mzee, my learners are doing well " + emoji,
        "Mzee, what comes after teaching?"]
  }[lvl] || ["Mzee, I need advice today " + emoji];
  out.push(openers[Math.floor(Math.random() * openers.length)]);

  var situation = "";
  if (lvl === 1) situation = "I live in " + loc + ". My mind is on " + topicLabel + ". What do I do today?";
  else if (lvl === 2) situation = "I sell in " + loc + ". Only " + (Math.floor(Math.random()*4)+1) + " out of " + (Math.floor(Math.random()*20)+5) + " bought yesterday. Main worry: " + topicLabel + ".";
  else if (lvl === 3) situation = "My books and cash don't match. Family pressure is high. " + topicLabel + " is a mess.";
  else if (lvl === 4) situation = "I have " + fmt(cap) + " UGX and space for one more stall in " + loc + ". Hire, expand, or save?";
  else if (lvl === 5) situation = topicLabel + " is still my weakest point. Focus there or push supply?";
  else situation = "Teaching " + topicLabel + " taught me more than expected. What next?";
  out.push(situation);

  out.push(emoji + " " + (
    emotion === "tired" ? "I feel tired today." :
    emotion === "hopeful" ? "I still have hope." :
    emotion === "determined" ? "I won't give up." :
    emotion === "worried" ? "I am worried, Mzee." :
    "Tell me the truth."
  ));

  return out;
}

function buildAjonReplyV2(pasieJoinedText) {
  var topic = BRAIN.currentTopic;
  var out = [];

  out.push(AJON_OPENERS[Math.floor(Math.random() * AJON_OPENERS.length)]);

  var diagnosis = AJON_DIAGNOSIS[topic] || AJON_DIAGNOSIS.default;
  out.push(firstSentences(diagnosis, 2));

  var principle = pickFresh(BRAIN_PRINCIPLES, BRAIN.lastPrinciples, 25);
  BRAIN.lastPrinciples.push(principle);
  if (BRAIN.lastPrinciples.length > 60) BRAIN.lastPrinciples = BRAIN.lastPrinciples.slice(-60);
  out.push("Principle: " + principle);

  var storyStr = pickFresh(BRAIN_STORIES.map(function(s){return JSON.stringify(s);}), BRAIN.lastStories, 8);
  var story = JSON.parse(storyStr);
  BRAIN.lastStories.push(storyStr);
  if (BRAIN.lastStories.length > 40) BRAIN.lastStories = BRAIN.lastStories.slice(-40);
  out.push("In " + story.y + " at " + story.p + ", I had " + story.a + " UGX selling " + story.b + ". " + story.l);

  if (BRAIN.chatCount % 4 === 3) {
    var termName = pickFresh(BRAIN_BUSINESS_TERMS.map(function(x){return x.t;}), BRAIN.lastTerms, 15);
    for (var ti = 0; ti < BRAIN_BUSINESS_TERMS.length; ti++) {
      if (BRAIN_BUSINESS_TERMS[ti].t === termName) {
        out.push("Term today: " + termName + ". " + firstSentences(BRAIN_BUSINESS_TERMS[ti].d, 2));
        BRAIN.lastTerms.push(termName);
        if (BRAIN.lastTerms.length > 30) BRAIN.lastTerms = BRAIN.lastTerms.slice(-30);
        break;
      }
    }
  }

  if (BRAIN.chatCount % 3 === 2) {
    var idea = generateBusinessIdea();
    if (idea) {
      out.push("Idea for you: " + idea.name + " in " + idea.location + ". Capital " + fmt(idea.capital) + " UGX.");
      out.push("Step 1 today: buy smallest kit. Step 2 tomorrow: talk to 5 buyers. Step 3 this week: deliver first order.");
    }
  }

  if (BRAIN.chatCount % 5 === 4 && typeof ALL_BUSINESSES !== "undefined" && ALL_BUSINESSES.length) {
    var idx = Math.floor(Math.random() * ALL_BUSINESSES.length);
    var b = ALL_BUSINESSES[idx];
    out.push("Study idea: " + b.emoji + " " + b.t + ". Start " + fmt(b.cost) + " UGX, profit " + fmt(b.profit) + " UGX per batch.");
    out.push("Buy from " + b.buy + ". Sell at " + b.sell + ".");
  }

  if (BRAIN.chatCount % 4 === 1) {
    var fact = pickFresh(BRAIN_FUNNY_FACTS, BRAIN.lastFacts, 15);
    BRAIN.lastFacts.push(fact);
    if (BRAIN.lastFacts.length > 30) BRAIN.lastFacts = BRAIN.lastFacts.slice(-30);
    out.push("Fun fact: " + fact);
  }

  out.push("Do 2 things now: 1) Write your real numbers in a book. 2) Talk to 3 customers face to face today.");
  out.push("Tonight: count your cash box. Separate cost from profit.");

  var proverb = pickFresh(BRAIN_PROVERBS, BRAIN.lastProverbs, 20);
  BRAIN.lastProverbs.push(proverb);
  if (BRAIN.lastProverbs.length > 40) BRAIN.lastProverbs = BRAIN.lastProverbs.slice(-40);
  out.push("Remember: " + proverb);
  out.push("What will you finish before 6pm today? I will ask tomorrow.");

  return out;
}

function sendSplitMessages(speaker, arr, token) {
  return new Promise(function (resolve) {
    var box = byId("assistMsgs");
    if (!box) return resolve(false);
    var idx = 0;
    function typeOne() {
      if (token !== chatToken || !BRAIN.isRunning) return resolve(false);
      if (idx >= arr.length) return resolve(true);
      var text = String(arr[idx] || "").trim();
      if (!text) { idx++; return typeOne(); }
      var row = makeBubbleRow(speaker, null, true);
      box.appendChild(row);
      var bubble = row.querySelector(".bubble");
      var i = 0;
      var msPerChar = 50 + Math.random() * 22;
      function step() {
        if (token !== chatToken || !BRAIN.isRunning) {
          bubble.classList.remove("typing-cursor");
          return resolve(false);
        }
        if (i >= text.length) {
          bubble.classList.remove("typing-cursor");
          idx++;
          setTimeout(typeOne, 800 + Math.random() * 400);
          return;
        }
        bubble.innerHTML = escapeHTML(text.substring(0, i + 1)).replace(/\n/g, "<br>");
        box.scrollTop = box.scrollHeight;
        if (i % 3 === 0) playTypingClick();
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
if idx == -1:
    print("ERROR: </script> not found"); sys.exit(1)
html = html[:idx] + NEW_JS + '\n' + html[idx:]
print("1. New functions injected.")

# Loop patch A: Pasie question
old = '  var pasieMsg = buildPasieQuestion();\n  var ok1 = await typeMessageLetterByLetter("pasie", pasieMsg, token);'
new = '  var pasieMsgArr = buildPasieQuestionV2();\n  var ok1 = await sendSplitMessages("pasie", pasieMsgArr, token);'
if old in html:
    html = html.replace(old, new, 1); print("2. Pasie loop patched.")
else:
    print("2. WARN Pasie loop exact not matched; trying fallback")
    html = html.replace('var pasieMsg = buildPasieQuestion();', 'var pasieMsgArr = buildPasieQuestionV2();', 1)
    html = html.replace('var ok1 = await typeMessageLetterByLetter("pasie", pasieMsg, token);', 'var ok1 = await sendSplitMessages("pasie", pasieMsgArr, token);', 1)
    print("2. Pasie loop patched (fallback).")

# Loop patch B: push Pasie message
old = 'BRAIN.messages.push({ s: "pasie", t: pasieMsg, ts: Date.now() });'
new = 'BRAIN.messages.push({ s: "pasie", t: pasieMsgArr.join("\\n\\n"), ts: Date.now() });'
if old in html:
    html = html.replace(old, new, 1); print("3. Pasie push patched.")

# Loop patch C: Ajon build
old = '  var ajonMsg = buildAjonReply(pasieMsg);'
new = '  var ajonMsgArr = buildAjonReplyV2(pasieMsgArr.join(" "));'
if old in html:
    html = html.replace(old, new, 1); print("4. Ajon build patched.")

# Loop patch D: Ajon typing
old = '  var ok2 = await typeMessageLetterByLetter("ajon", ajonMsg, token);'
new = '  var ok2 = await sendSplitMessages("ajon", ajonMsgArr, token);'
if old in html:
    html = html.replace(old, new, 1); print("5. Ajon type patched.")

# Loop patch E: push Ajon message
old = 'BRAIN.messages.push({ s: "ajon", t: ajonMsg, ts: Date.now() });'
new = 'BRAIN.messages.push({ s: "ajon", t: ajonMsgArr.join("\\n\\n"), ts: Date.now() });'
if old in html:
    html = html.replace(old, new, 1); print("6. Ajon push patched.")

# Timing extensions
old = 'await sleep(1800 + Math.random() * 1200);'
new = 'await sleep(2400 + Math.random() * 1500);'
if old in html:
    html = html.replace(old, new, 1); print("7. Pasie thinking extended.")

old = 'await sleep(3200 + Math.random() * 1800);'
new = 'await sleep(5000 + Math.random() * 2500);'
if old in html:
    html = html.replace(old, new, 1); print("8. Ajon thinking extended.")

old = 'scheduleNextTurn(token, 3200 + Math.random() * 3000);'
new = 'scheduleNextTurn(token, 6000 + Math.random() * 4000);'
if old in html:
    html = html.replace(old, new, 1); print("9. Inter-turn delay extended.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Step 1 applied to www/index.html.")
