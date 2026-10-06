import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

NEW_JS = r'''

/* =====================================================================
   v7 — Topic-linked business discussion + continuity memory
   ===================================================================== */

var TOPIC_BUSINESS_KEYWORDS = {
  fear:           ["beginner", "small scale", "starter"],
  capital:        ["small scale", "budget", "village"],
  first_step:     ["home-based", "small scale", "budget"],
  pricing:        ["retail", "premium", "value"],
  value:          ["premium", "quality"],
  customer_care:  ["retail", "service", "shop"],
  retention:      ["retail", "premium", "brand"],
  trust:          ["retail", "quality"],
  brand:          ["brand", "premium", "export"],
  word_of_mouth:  ["retail", "village", "urban"],
  records:        ["retail", "small scale"],
  cash_flow:      ["wholesale", "bulk", "commercial"],
  unit_economics: ["bulk", "commercial", "wholesale"],
  savings:        ["home-based", "small scale"],
  emergency:      ["home-based", "small scale"],
  debt:           ["commercial", "bulk", "medium scale"],
  family:         ["home-based", "village", "small scale"],
  discipline:     ["home-based", "small scale", "medium"],
  morning_routine:["home-based", "retail", "small scale"],
  focus:          ["premium", "niche", "medium scale"],
  competition:    ["premium", "niche", "urban"],
  supplier:       ["wholesale", "bulk", "commercial"],
  hiring:         ["medium scale", "commercial", "urban"],
  expansion:      ["commercial", "urban", "wholesale"],
  teaching:       ["community", "village", "small scale"],
  community:      ["community", "village"],
  legacy:         ["premium", "brand", "export"]
};

if (!BRAIN._bizIdx) BRAIN._bizIdx = {};
if (!BRAIN.lastBusinessIds) BRAIN.lastBusinessIds = [];
if (!BRAIN.lastAjonPrinciple) BRAIN.lastAjonPrinciple = null;
if (!BRAIN.pendingBusiness) BRAIN.pendingBusiness = null;

function pickBusinessForTopic(topicId) {
  if (typeof ALL_BUSINESSES === "undefined" || !ALL_BUSINESSES.length) return null;
  var keywords = TOPIC_BUSINESS_KEYWORDS[topicId] || [];
  var candidates = [];
  for (var i = 0; i < ALL_BUSINESSES.length; i++) {
    var b = ALL_BUSINESSES[i];
    var hay = ((b.t || "") + " " + (b.tagline || "") + " " + (b.sell || "")).toLowerCase();
    for (var k = 0; k < keywords.length; k++) {
      if (hay.indexOf(keywords[k]) > -1) { candidates.push(b); break; }
    }
  }
  if (!candidates.length) candidates = ALL_BUSINESSES;
  var key = "biz_" + topicId;
  if (BRAIN._bizIdx[key] === undefined) BRAIN._bizIdx[key] = Math.floor(Math.random() * candidates.length);
  var b = candidates[BRAIN._bizIdx[key] % candidates.length];
  BRAIN._bizIdx[key] = (BRAIN._bizIdx[key] + 1) % candidates.length;
  return b;
}

function shortStep(s, maxLen) {
  if (!s) return "";
  s = String(s).replace(/\*\*/g, "").trim();
  maxLen = maxLen || 55;
  if (s.length <= maxLen) return s;
  var words = s.split(/\s+/);
  var cur = "";
  for (var i = 0; i < words.length; i++) {
    if (!cur) { cur = words[i]; continue; }
    if ((cur + " " + words[i]).length <= maxLen) cur += " " + words[i];
    else break;
  }
  return cur + "...";
}

function buildPasieFinal() {
  var arr = buildPasieV6();

  if (BRAIN.lastAjonPrinciple && Math.random() < 0.35 && arr.length) {
    arr.unshift("Mzee you said: " + BRAIN.lastAjonPrinciple + ".");
  }

  if (Math.random() < 0.22) {
    var topicId = BRAIN.currentTopicId || "fear";
    var biz = pickBusinessForTopic(topicId);
    if (biz) {
      BRAIN.pendingBusiness = biz;
      arr.push("Mzee, tell me about " + biz.t + ".");
    }
  }
  return arr;
}

function buildAjonFinal() {
  var arr = buildAjonV6();

  if (BRAIN.pendingBusiness) {
    var biz = BRAIN.pendingBusiness;
    BRAIN.pendingBusiness = null;
    arr.push(biz.t + " — start cost " + fmt(biz.cost) + " UGX.");
    arr.push("Profit " + fmt(biz.profit) + " UGX per batch.");
    if (biz.buy) arr.push("Buy from " + String(biz.buy).substring(0, 48) + ".");
    if (biz.sell) arr.push("Sell at " + String(biz.sell).substring(0, 48) + ".");
  }

  for (var i = 0; i < arr.length; i++) {
    if (String(arr[i]).indexOf("Principle: ") === 0) {
      BRAIN.lastAjonPrinciple = String(arr[i]).substring(11);
      break;
    }
  }

  if (BRAIN.chatCount % 4 === 2) {
    var topicId2 = BRAIN.currentTopicId || "fear";
    var biz2 = pickBusinessForTopic(topicId2);
    if (biz2) {
      arr.push("Idea: " + biz2.t + " in " + biz2.location + ".");
      arr.push("Step 1 today: " + (biz2.steps && biz2.steps[0] ? shortStep(biz2.steps[0], 50) : "Buy smallest starter kit."));
      BRAIN.lastBusinessIds = (BRAIN.lastBusinessIds.concat([biz2.id])).slice(-15);
    }
  }

  if (BRAIN.chatCount % 8 === 4) {
    var topicId3 = BRAIN.currentTopicId || "fear";
    var biz3 = pickBusinessForTopic(topicId3);
    if (biz3) {
      arr.push("Study " + biz3.t + " deeper in Tutorials tab.");
      if (biz3.steps && biz3.steps[1]) arr.push("Step 2: " + shortStep(biz3.steps[1], 50));
      if (biz3.steps && biz3.steps[2]) arr.push("Step 3: " + shortStep(biz3.steps[2], 50));
    }
  }

  return arr;
}
'''

idx = html.rfind('</script>')
if idx == -1: print("ERR </script>"); sys.exit(1)
html = html[:idx] + NEW_JS + '\n' + html[idx:]

# Redirect loop to final builders
html = html.replace('var pasieBubbles = buildPasieV6();', 'var pasieBubbles = buildPasieFinal();', 1)
html = html.replace('var ajonBubbles = buildAjonV6();', 'var ajonBubbles = buildAjonFinal();', 1)

# Extend clear to reset v7 state
old_clear = 'BRAIN.currentTopicId = "fear";\n  BRAIN.lastTopics = [];'
new_clear = 'BRAIN.currentTopicId = "fear";\n  BRAIN.lastTopics = [];\n  BRAIN._bizIdx = {};\n  BRAIN.lastBusinessIds = [];\n  BRAIN.lastAjonPrinciple = null;\n  BRAIN.pendingBusiness = null;'
if old_clear in html:
    html = html.replace(old_clear, new_clear, 1)
    print("Clear resets extended.")
else:
    print("WARN: clear pattern not found, trying looser")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS. v7 installed: topic-linked business discussion + continuity.")
