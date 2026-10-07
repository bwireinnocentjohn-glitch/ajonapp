import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Nav rename
c = html.count('<span>Helper</span>')
html = html.replace('<span>Helper</span>', '<span>Expert</span>')
print("1. Nav renamed: " + str(c))

# 2. Replace panel-ai
start = html.find('<section class="panel" id="panel-ai">')
end = html.find('</section>', start) + len('</section>')
if start == -1 or end == -1:
    print("ERR panel-ai"); sys.exit(1)

NEW_PANEL = r'''<section class="panel" id="panel-ai">
  <div class="expert-lock" id="expertLock" style="display:none;">
    <div class="expert-lock-icon">&#x1F512;</div>
    <div class="expert-lock-title">Expert Locked</div>
    <p class="expert-lock-text">Unlock all 1500+ ways of making money &#x1F4B0;</p>
    <button class="btn" onclick="showTab('video')">&#x1F48E; Go to Unlock</button>
  </div>
  <div class="expert-main" id="expertMain">
    <div class="expert-header">
      <span class="expert-badge">&#x1F9E0; Mr Expert</span>
      <span class="expert-status" id="expertStatus">&#x1F7E2; Ready</span>
    </div>
    <div class="expert-sugs" id="expertSugs"></div>
    <div class="expert-msgs" id="expertMsgs"></div>
    <div class="expert-quote-card" id="expertQuoteCard">
      <span class="quote-icon" id="expertQuoteIcon">&#x2728;</span>
      <span class="quote-text" id="expertQuoteText">Preparing your daily wisdom...</span>
    </div>
    <div class="expert-input-row">
      <input id="aiInput" type="text" placeholder="Ask Mr Expert anything..." autocomplete="off">
      <button class="btn expert-send-btn" onclick="askExpert()">Ask Expert</button>
    </div>
  </div>
</section>'''
html = html[:start] + NEW_PANEL + html[end:]
print("2. Panel-ai replaced")

# 3. CSS
CSS = """
/* ========== Expert Tab ========== */
#panel-ai.active {
  display: flex !important;
  flex-direction: column;
  height: 100%;
  padding-bottom: 0;
}
.expert-main { display: flex; flex-direction: column; height: 100%; min-height: 0; }
.expert-header { display: flex; gap: 8px; padding: 10px 14px 6px; align-items: center; flex: 0 0 auto; }
.expert-badge { background: linear-gradient(135deg,#00c853,#009624); color: #000; font-weight: 800; padding: 5px 12px; border-radius: 999px; font-size: 12px; }
.expert-status { font-size: 11.5px; color: #00c853; margin-left: auto; font-weight: 700; }
.expert-sugs { display: flex; gap: 8px; padding: 6px 12px 10px; overflow-x: auto; scrollbar-width: none; flex: 0 0 auto; }
.expert-sugs::-webkit-scrollbar { display: none; }
.sug-chip { flex: 0 0 auto; padding: 8px 14px; border-radius: 999px; background: #1a1a1a; border: 1px solid rgba(0,200,83,.45); color: #00c853; font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap; font-family: inherit; }
.sug-chip:active { background: #003d14; }
.expert-msgs { flex: 1 1 auto; min-height: 0; overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 6px 12px 12px; display: flex; flex-direction: column; gap: 8px; }
.expert-bubble { padding: 10px 13px; border-radius: 14px; font-size: 13.5px; line-height: 1.55; max-width: 88%; white-space: pre-wrap; word-wrap: break-word; animation: slideUp .25s ease both; }
.expert-bubble.me { align-self: flex-end; background: #00c853; color: #000; font-weight: 600; border-bottom-right-radius: 5px; }
.expert-bubble.ex { align-self: flex-start; background: #142e1c; color: #e6f7ea; border-left: 3px solid #00c853; border-bottom-left-radius: 5px; }
.expert-bubble.typing { color: #00c853; letter-spacing: 3px; font-size: 20px; padding: 8px 16px; }
.expert-quote-card { margin: 6px 12px 8px; padding: 10px 14px; background: linear-gradient(135deg,#001a0a,#003d14); border: 1px solid #00c853; border-radius: 12px; display: flex; gap: 10px; align-items: flex-start; transition: all .3s ease; flex: 0 0 auto; }
.expert-quote-card.hidden { opacity: 0; max-height: 0; padding: 0; margin: 0; border: 0; overflow: hidden; pointer-events: none; }
.quote-icon { font-size: 20px; flex: 0 0 auto; line-height: 1; }
.quote-text { font-size: 12.5px; color: #e6f7ea; line-height: 1.5; font-weight: 600; }
.expert-input-row { display: flex; gap: 8px; padding: 8px 12px 14px; border-top: 1px solid rgba(0,200,83,.35); background: #0a0a0a; flex: 0 0 auto; }
.expert-input-row input { flex: 1; min-width: 0; padding: 12px 14px; border-radius: 12px; background: #1a1a1a; color: #fff; border: 1px solid #00c853; font-family: inherit; font-size: 14px; outline: none; }
.expert-input-row input::placeholder { color: #7a7a7a; }
.expert-send-btn { width: auto !important; padding: 12px 16px !important; font-size: 14px !important; flex: 0 0 auto; }
.expert-lock { padding: 40px 22px; text-align: center; }
.expert-lock-icon { font-size: 60px; margin-bottom: 12px; line-height: 1; }
.expert-lock-title { font-size: 22px; font-weight: 900; color: #00c853; margin-bottom: 10px; }
.expert-lock-text { font-size: 14px; color: #c8c8c8; margin-bottom: 20px; line-height: 1.55; }
"""
idx = html.rfind('</style>')
if idx == -1: print("ERR </style>"); sys.exit(1)
html = html[:idx] + CSS + '\n' + html[idx:]
print("3. CSS added")

# 4. Expert brain
BRAIN = r'''

/* ==========================================================
   EXPERT TAB — Mr Expert Brain
   ========================================================== */
var EXPERT = { msgs: [], askCount: 0, busy: false, quoteTimer: null, quoteIdx: 0, sugsIdx: 0, vocab: null };

var EX_GREET = ["hi","hey","hello","hie","hallo","howdy","sup","yo","good morning","good evening","good afternoon","morning","evening","hi there","hello there"];

var EX_GREET_REPLY = [
  "Hello my friend! \uD83D\uDE0A I am Mr Expert. How can I help you today?",
  "Welcome! \uD83D\uDE4F Ask me anything about business or life.",
  "Hi there! \uD83D\uDCAA Ready to help. What is on your mind?",
  "Greetings! \uD83D\uDE04 I am Mr Expert. Tell me what you want to learn.",
  "Hey! \uD83D\uDC4B I am here. What can I teach you today?",
  "Hello! \u2728 Let us build something together. What do you need?"
];

var EX_QUOTES = [
  {i:"\uD83D\uDCAA", t:"Small daily actions beat big plans."},
  {i:"\uD83D\uDE4F", t:"Commit to the Lord whatever you do, and he will establish your plans. \u2014 Proverbs 16:3"},
  {i:"\uD83C\uDF31", t:"Start where you are. Use what you have. Do what you can."},
  {i:"\uD83C\uDFAF", t:"Discipline is the bridge between goals and results."},
  {i:"\uD83D\uDCA1", t:"Every expert was once a beginner who did not quit."},
  {i:"\uD83E\uDD1D", t:"Money follows trust. Trust follows consistency."},
  {i:"\uD83D\uDD25", t:"Do not wait for perfect. Start imperfect today."},
  {i:"\uD83D\uDEE1\uFE0F", t:"The Lord is my shepherd; I shall not want. \u2014 Psalm 23:1"},
  {i:"\uD83D\uDE4C", t:"I can do all things through Christ who strengthens me. \u2014 Philippians 4:13"},
  {i:"\uD83D\uDCDA", t:"Learn one thing today. Apply it today."},
  {i:"\uD83D\uDCB0", t:"Save before you spend. Not after."},
  {i:"\uD83C\uDF1F", t:"Your reputation is your real capital."},
  {i:"\uD83E\uDDE0", t:"Real wealth takes years. Fake wealth takes weeks."},
  {i:"\uD83D\uDD4A\uFE0F", t:"Trust in the Lord with all your heart. \u2014 Proverbs 3:5"},
  {i:"\uD83D\uDE80", t:"Fall seven times, stand up eight."},
  {i:"\uD83C\uDF08", t:"Every storm ends. Every sunrise comes."},
  {i:"\uD83D\uDC9A", t:"Kindness costs nothing, pays everything."},
  {i:"\uD83D\uDC51", t:"Do the boring things daily. The boring things compound."},
  {i:"\uD83D\uDD11", t:"The best time to start was yesterday. Second best is now."},
  {i:"\uD83C\uDF3B", t:"A journey of a thousand miles begins with one step."},
  {i:"\uD83D\uDCA3", t:"Failure is the school that never closes."},
  {i:"\uD83D\uDCAB", t:"Profit is seed, not fruit."},
  {i:"\u2B50", t:"Consistency beats talent every single week."},
  {i:"\uD83C\uDFAF", t:"Focus is choosing one thing and refusing the rest."},
  {i:"\uD83D\uDEE4\uFE0F", t:"Build like a carpenter. Measure twice, cut once."}
];

var EX_FACTS = [
  "\uD83D\uDC1D A snail can sleep for 3 years. Your customer will not wait 3 days.",
  "\uD83C\uDF6F Honey never spoils. Your reputation can, in one day.",
  "\uD83C\uDF4C Bananas are berries. Strawberries are not. Marketing is perception.",
  "\uD83D\uDC1B Ants can lift 50 times their body weight. So can a determined person with a small loan.",
  "\uD83D\uDC18 Elephants are the only animals that cannot jump. But they travel far.",
  "\uD83E\uDD88 Sharks existed before trees. Loyalty existed before marketing.",
  "\uD83C\uDF3E Some bamboo grows 91cm a day. Discipline is the bamboo of business.",
  "\uD83D\uDD4A Sea otters hold hands while sleeping. Partners in business should too.",
  "\uD83C\uDF4D Pineapples take 2 years to grow. Great businesses are not overnight.",
  "\uD83D\uDC22 Some turtles can breathe through their rear ends. Businesses find strange ways to survive.",
  "\uD83D\uDC0B A day on Venus is longer than its year. A slow week feels longer in business.",
  "\uD83D\uDC05 The strongest muscle is the tongue. Words build or break businesses.",
  "\uD83D\uDC19 Octopuses have 3 hearts. A good business needs at least two.",
  "\uD83C\uDF44 Mushrooms grow in the dark. Great ideas grow without applause.",
  "\uD83D\uDC1D Cows have best friends. Your staff have teams too.",
  "\uD83C\uDF3B The world's oldest business is over 1,400 years old. Longevity comes from service.",
  "\uD83C\uDF0A Sea urchins can live 200 years. Patience is a business skill.",
  "\uD83E\uDD8B Butterflies taste with their feet. Your customer tastes your business with every interaction."
];

var EX_JOKES = [
  "\uD83D\uDE02 Why did the businessman bring a ladder to work? He heard sales were going up.",
  "\uD83D\uDE01 My wallet is like an onion. Opening it makes me cry.",
  "\uD83D\uDE04 I told my customer 'money back guarantee.' He asked for the money before he paid.",
  "\uD83E\uDD23 My business plan is simple: make money. Simple, but not easy.",
  "\uD83D\uDE06 My account balance is like my hairline. Going, going, gone.",
  "\uD83D\uDE05 Bank called to say I have insufficient funds. I said, tell me something I do not know."
];

var EX_ENCOURAGE = [
  "Do not give up. \uD83D\uDCAA The market rewards those who stay.",
  "You are closer than you think. Keep going. \uD83C\uDF1F",
  "Every rich person you see was once a poor person who did not quit. \uD83D\uDC51",
  "Take a deep breath. Then take one small action. That is enough. \uD83C\uDF3F",
  "You are not alone. Many have walked this path. \uD83E\uDD1D",
  "Failure is data. Not damage. \uD83D\uDCCA",
  "Rest tonight. Tomorrow you start again. \uD83C\uDF19",
  "Your current situation is not your final destination. \uD83D\uDE80"
];

var EX_TERMS = {
  "cash flow": "The daily movement of money in and out of your business. Not the same as profit. A business can be profitable on paper and still die from cash shortage.",
  "profit": "What is left after all costs. Money in minus money out.",
  "profit margin": "The percentage of money you keep after costs. Sell at 10,000, cost 7,000, margin is 30%.",
  "capital": "The money and assets you use to run your business. Your starter money.",
  "caustic soda": "A strong chemical (sodium hydroxide). In soap making it turns oil into soap. Always wear gloves and never add water to it directly.",
  "sulphonic acid": "A soap-making chemical that adds cleaning power and foam. Add slowly while stirring.",
  "texapon": "A foaming agent used in liquid soap. Makes the soap foam when you shake it.",
  "glycerine": "A natural moisturiser. Used in soap, cosmetics, and skincare.",
  "fragrance": "A pleasant smell added to soap, candles, or cosmetics.",
  "breakeven": "The point where sales equal costs. Below it you lose. Above it you profit.",
  "unit economics": "The profit or loss on ONE item. If one unit loses money, selling more only makes it worse.",
  "working capital": "Money available for daily running. Stock plus cash minus debts.",
  "inventory turnover": "How fast your stock sells and is replaced. Fast = fresh cash. Slow = dead money.",
  "fixed cost": "A cost that does not change with sales. Rent, licence, salary.",
  "variable cost": "A cost that changes with every sale. Materials, packaging, transport.",
  "markup": "What you add on top of cost. Different from margin.",
  "sunk cost": "Money already spent that cannot come back. Do not let it force bad decisions.",
  "opportunity cost": "What you give up when you choose something else.",
  "leverage": "Using resources you do not own to grow faster. Money, people, tools.",
  "compounding": "Small growth repeated that snowballs. 1,000 saved monthly grows into millions.",
  "supply chain": "Everyone between raw material and customer.",
  "bottleneck": "The one step slowing everything else. Fix it first.",
  "kpi": "Key Performance Indicator. The one number you watch daily.",
  "cac": "Customer Acquisition Cost. Money spent to get one customer.",
  "ltv": "Lifetime Value. Total money a customer spends with you over years.",
  "churn": "Customers who leave and never come back.",
  "brand equity": "The extra value your name carries beyond the product.",
  "positioning": "Where your business sits in the customer's mind. Cheap, premium, fast, safe.",
  "usp": "Unique Selling Point. The one thing you offer that others do not.",
  "target market": "The specific group you serve best. Trying to serve everyone serves nobody.",
  "segmentation": "Dividing your market into groups with different needs.",
  "funnel": "The path from stranger to buyer. Awareness, interest, decision, action.",
  "conversion rate": "Percentage of viewers who buy. 100 visitors, 4 buyers = 4%.",
  "aov": "Average Order Value. Total sales divided by number of orders.",
  "upsell": "Selling a bigger or better version of what the customer wanted.",
  "cross-sell": "Selling a related product next to the main one.",
  "bootstrapping": "Growing with your own money and customer revenue.",
  "angel investor": "A person who invests early in exchange for equity.",
  "venture capital": "A fund that invests big money in high-growth businesses.",
  "equity": "Ownership of the business.",
  "dilution": "Your ownership percentage shrinking when others invest.",
  "exit strategy": "The plan for how you eventually sell or step back.",
  "pivot": "A serious change in product, market, or model based on learning.",
  "mvp": "Minimum Viable Product. The smallest version that tests your idea.",
  "scaling": "Growing the business without breaking it.",
  "franchising": "Letting others use your brand and system for a fee.",
  "dropshipping": "Selling products you do not stock. Supplier ships direct.",
  "private label": "Your own brand on a product made by someone else.",
  "b2b": "Business to Business. You sell to other businesses.",
  "b2c": "Business to Consumer. You sell to individual people.",
  "due diligence": "Careful checking before a deal. Numbers, reputation, records.",
  "runway": "How many months your cash can keep the business alive.",
  "burn rate": "How fast you spend cash each month.",
  "gross profit": "Sales minus cost of goods sold.",
  "net profit": "What remains after all costs, taxes, and interest.",
  "stpp": "A chemical in detergent powder that softens water and boosts cleaning power.",
  "sodium hypochlorite": "The active chemical in bleach (Jik). Kills germs and whitens.",
  "beeswax": "Natural wax made by bees. Used in candles, lip balm, and food wraps.",
  "shea butter": "A fat from shea nuts. Used in cosmetics for skin and hair.",
  "castor oil": "A thick oil from castor seeds. Used in hair growth products.",
  "jojoba oil": "A light oil from jojoba seeds. Used in skin and hair products.",
  "neem": "A tree with medicinal and pesticide uses. Kills pests naturally.",
  "moringa": "A tree with highly nutritious leaves. Called the miracle tree.",
  "bsf": "Black Soldier Fly. Larvae convert food waste into animal feed.",
  "mushroom spawn": "The 'seed' for growing mushrooms. Buy from NARO Kawanda.",
  "hydroponics": "Growing plants in water with nutrients, not soil."
};

function exLevenshtein(a, b) {
  if (a === b) return 0;
  if (Math.abs(a.length - b.length) > 2) return 99;
  var al = a.length, bl = b.length;
  if (!al) return bl; if (!bl) return al;
  var row = [], i, j;
  for (j = 0; j <= bl; j++) row[j] = j;
  for (i = 1; i <= al; i++) {
    var prev = row[0];
    row[0] = i;
    for (j = 1; j <= bl; j++) {
      var cur = row[j];
      row[j] = Math.min(row[j] + 1, row[j-1] + 1, prev + (a.charCodeAt(i-1) === b.charCodeAt(j-1) ? 0 : 1));
      prev = cur;
    }
  }
  return row[bl];
}

function exBuildVocab() {
  if (EXPERT.vocab) return;
  var set = {}, i, k;
  try {
    if (typeof ALL_BUSINESSES !== "undefined") {
      for (i = 0; i < ALL_BUSINESSES.length; i++) {
        var parts = String(ALL_BUSINESSES[i].t || "").toLowerCase().split(/[^a-z0-9]+/);
        for (k = 0; k < parts.length; k++) if (parts[k].length >= 6) set[parts[k]] = 1;
      }
    }
  } catch (e) {}
  for (var key in EX_TERMS) {
    var kp = key.split(/\s+/);
    for (k = 0; k < kp.length; k++) if (kp[k].length >= 6) set[kp[k]] = 1;
  }
  EXPERT.vocab = Object.keys(set);
}

function exCorrectTypos(text) {
  try {
    exBuildVocab();
    if (!EXPERT.vocab.length) return text;
    var words = text.split(/(\s+)/);
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      if (!w || /^\s+$/.test(w)) continue;
      var clean = w.replace(/[^a-zA-Z0-9]/g, "");
      if (clean.length < 6) continue;
      var lower = clean.toLowerCase();
      var best = null, bestD = 3;
      for (var j = 0; j < EXPERT.vocab.length; j++) {
        var d = exLevenshtein(lower, EXPERT.vocab[j]);
        if (d < bestD) { bestD = d; best = EXPERT.vocab[j]; if (d === 1) break; }
      }
      if (best && bestD <= 2) words[i] = w.replace(clean, best);
    }
    return words.join("");
  } catch (e) { return text; }
}

function exMatchGreeting(q) {
  var low = q.toLowerCase().trim().replace(/[!?.]+$/, "");
  for (var i = 0; i < EX_GREET.length; i++) if (low === EX_GREET[i]) return true;
  return false;
}

function exMatchBusiness(q) {
  if (typeof ALL_BUSINESSES === "undefined") return null;
  var low = q.toLowerCase();
  var words = low.split(/\s+/).filter(function(w){ return w.length >= 3; });
  if (!words.length) return null;
  var best = null, bestScore = 0;
  for (var i = 0; i < ALL_BUSINESSES.length; i++) {
    var b = ALL_BUSINESSES[i];
    var hay = (b.t + " " + (b.tagline || "") + " " + (b.sell || "")).toLowerCase();
    var score = 0;
    for (var w = 0; w < words.length; w++) if (hay.indexOf(words[w]) > -1) score += 2;
    if (b.t && low.indexOf(b.t.toLowerCase()) > -1) score += 10;
    if (score > bestScore) { bestScore = score; best = b; }
  }
  return bestScore >= 2 ? best : null;
}

function exMatchTerm(q) {
  var low = q.toLowerCase();
  var keys = Object.keys(EX_TERMS);
  var best = null, bestScore = 0;
  for (var i = 0; i < keys.length; i++) {
    var k = keys[i];
    if (low.indexOf(k) > -1) {
      var s = k.length;
      if (s > bestScore) { bestScore = s; best = k; }
    }
  }
  return best;
}

function exMatchEncourage(q) {
  var low = q.toLowerCase();
  var words = ["sad","tired","give up","quit","stress","worried","fear","fail","depressed","hopeless","lonely","angry","hate"];
  for (var i = 0; i < words.length; i++) if (low.indexOf(words[i]) > -1) return true;
  return false;
}

function exIsJokeRequest(q) { var l = q.toLowerCase(); return l.indexOf("joke") > -1 || l.indexOf("funny") > -1 || l.indexOf("laugh") > -1; }
function exIsFactRequest(q) { var l = q.toLowerCase(); return l.indexOf("fact") > -1 || l.indexOf("did you know") > -1; }
function exIsQuoteRequest(q) { var l = q.toLowerCase(); return l.indexOf("quote") > -1 || l.indexOf("motivate") > -1 || l.indexOf("inspire") > -1 || l.indexOf("bible") > -1 || l.indexOf("verse") > -1; }

function exComposeReply(q) {
  try {
    var clean = exCorrectTypos(String(q || "").trim());
    if (!clean) return ["Please type a question. \uD83D\uDE42"];
    if (exMatchGreeting(clean)) return [EX_GREET_REPLY[Math.floor(Math.random() * EX_GREET_REPLY.length)]];
    if (exIsJokeRequest(clean)) return [EX_JOKES[Math.floor(Math.random() * EX_JOKES.length)]];
    if (exIsFactRequest(clean)) return [EX_FACTS[Math.floor(Math.random() * EX_FACTS.length)]];
    if (exIsQuoteRequest(clean)) { var q1 = EX_QUOTES[Math.floor(Math.random() * EX_QUOTES.length)]; return [q1.i + " " + q1.t]; }
    var termKey = exMatchTerm(clean);
    if (termKey) return ["\uD83D\uDCD8 " + termKey.charAt(0).toUpperCase() + termKey.slice(1) + ":\n" + EX_TERMS[termKey]];
    var biz = exMatchBusiness(clean);
    if (biz) {
      var out = [];
      out.push(biz.emoji + " " + biz.t);
      if (biz.tagline) out.push(biz.tagline);
      out.push("Start cost: " + fmt(biz.cost) + " UGX");
      out.push("Sales: " + fmt(biz.sales) + " UGX");
      out.push("Profit: " + fmt(biz.profit) + " UGX per batch");
      if (biz.buy) out.push("\uD83D\uDED2 Buy from: " + biz.buy);
      if (biz.sell) out.push("\uD83C\uDFEA Sell at: " + biz.sell);
      if (biz.steps && biz.steps.length) {
        out.push("\uD83D\uDD27 First steps:");
        out.push("1. " + String(biz.steps[0]).substring(0, 160));
        if (biz.steps[1]) out.push("2. " + String(biz.steps[1]).substring(0, 160));
      }
      out.push("\uD83D\uDCDA Open the Tutorials tab for the full " + biz.t + " steps.");
      return [out.join("\n")];
    }
    if (exMatchEncourage(clean)) return [EX_ENCOURAGE[Math.floor(Math.random() * EX_ENCOURAGE.length)]];
    var quote = EX_QUOTES[Math.floor(Math.random() * EX_QUOTES.length)];
    return [
      "I hear you. \uD83D\uDE42 Let me share something useful.",
      quote.i + " " + quote.t,
      "\uD83D\uDCA1 Try asking me about a business name (like 'soap' or 'cricket farming'), or a business term (like 'cash flow')."
    ];
  } catch (e) { return ["I am here. \uD83D\uDE42 Please try asking again."]; }
}

function exAddBubble(speaker, text) {
  var box = byId("expertMsgs");
  if (!box) return null;
  var div = document.createElement("div");
  div.className = "expert-bubble " + (speaker === "me" ? "me" : "ex");
  div.textContent = String(text || "");
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

function exShowTyping() {
  var box = byId("expertMsgs");
  if (!box) return null;
  var div = document.createElement("div");
  div.className = "expert-bubble ex typing";
  div.textContent = "\u25CF\u25CF\u25CF";
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

function exTypeInto(el, text, done) {
  if (!el) { if (done) done(); return; }
  var full = String(text || "");
  var i = 0;
  el.textContent = "";
  function tick() {
    if (i >= full.length) { if (done) done(); return; }
    el.textContent += full.charAt(i);
    var box = byId("expertMsgs");
    if (box) box.scrollTop = box.scrollHeight;
    i++;
    setTimeout(tick, 14);
  }
  tick();
}

function exRenderSuggestions() {
  var bar = byId("expertSugs");
  if (!bar) return;
  var pool = [
    "how do I make soap?","what is cash flow?","give me a business idea","how do I start small?",
    "what is caustic soda?","tell me a joke","share a bible verse","how do I price my product?",
    "what is profit margin?","how do I keep customers?","what is break-even?","how do I save money?",
    "give me motivation","what is caustic?","tell me a fact","how do I sell on WhatsApp?",
    "what is a KPI?","how do I handle complaints?","what is BSF farming?","how do I manage staff?"
  ];
  var out = [];
  for (var i = 0; i < 6; i++) out.push(pool[(EXPERT.sugsIdx + i) % pool.length]);
  EXPERT.sugsIdx = (EXPERT.sugsIdx + 6) % pool.length;
  var html = "";
  for (var j = 0; j < out.length; j++) {
    html += '<div class="sug-chip" data-q="' + out[j].replace(/"/g, "&quot;") + '">' + out[j] + '</div>';
  }
  bar.innerHTML = html;
  if (!bar._ajonBound) {
    bar._ajonBound = true;
    bar.addEventListener("click", function(ev){
      var t = ev.target;
      while (t && t !== bar && !t.classList.contains("sug-chip")) t = t.parentNode;
      if (!t || t === bar) return;
      ev.preventDefault();
      var q = t.getAttribute("data-q");
      var inp = byId("aiInput");
      if (inp) inp.value = q;
      askExpert();
    }, false);
  }
}

function exRotateQuote() {
  var card = byId("expertQuoteCard");
  if (!card || card.classList.contains("hidden")) return;
  var q = EX_QUOTES[EXPERT.quoteIdx % EX_QUOTES.length];
  EXPERT.quoteIdx++;
  var icon = byId("expertQuoteIcon");
  var txt = byId("expertQuoteText");
  if (icon) icon.textContent = q.i;
  if (txt) txt.textContent = q.t;
}

function exShowQuote() { var c = byId("expertQuoteCard"); if (c) c.classList.remove("hidden"); exRotateQuote(); }
function exHideQuote() { var c = byId("expertQuoteCard"); if (c) c.classList.add("hidden"); }
function exStartQuoteTimer() {
  if (EXPERT.quoteTimer) clearInterval(EXPERT.quoteTimer);
  EXPERT.quoteTimer = setInterval(function(){ exRotateQuote(); }, 15000);
}

function askExpert() {
  try {
    if (!hasFullAccess()) { expertGate(); return; }
    if (EXPERT.busy) return;
    var inp = byId("aiInput");
    if (!inp) return;
    var q = String(inp.value || "").trim();
    if (!q) { inp.focus(); return; }
    inp.value = "";
    EXPERT.busy = true;
    exHideQuote();
    exAddBubble("me", q);
    EXPERT.msgs.push({ s: "me", t: q });
    var typing = exShowTyping();
    setTimeout(function(){
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      var replies = exComposeReply(q);
      var idx = 0;
      function sendNext() {
        if (idx >= replies.length) { EXPERT.busy = false; return; }
        var text = replies[idx];
        var bubble = exAddBubble("ex", "");
        EXPERT.msgs.push({ s: "ex", t: text });
        exTypeInto(bubble, text, function(){ idx++; setTimeout(sendNext, 250); });
      }
      sendNext();
    }, 600 + Math.random() * 500);
  } catch (e) { EXPERT.busy = false; }
}

function expertGate() {
  var lock = byId("expertLock");
  var main = byId("expertMain");
  if (hasFullAccess()) {
    if (lock) lock.style.display = "none";
    if (main) main.style.display = "flex";
    return false;
  }
  if (lock) lock.style.display = "block";
  if (main) main.style.display = "none";
  return true;
}

function expertOnEnter() {
  try {
    if (expertGate()) return;
    exRenderSuggestions();
    var box = byId("expertMsgs");
    if (box && box.children.length === 0) {
      exAddBubble("ex", "Hello! \uD83D\uDE0A I am Mr Expert. Ask me anything about business or life.");
    }
    exShowQuote();
    exStartQuoteTimer();
    var inp = byId("aiInput");
    if (inp) setTimeout(function(){ try { inp.focus(); } catch(e){} }, 80);
  } catch (e) {}
}

function expertOnLeave() {
  try { if (EXPERT.quoteTimer) { clearInterval(EXPERT.quoteTimer); EXPERT.quoteTimer = null; } } catch (e) {}
}

try { exBuildVocab(); } catch (e) {}
'''
idx = html.rfind('</script>')
if idx == -1: print("ERR </script>"); sys.exit(1)
html = html[:idx] + BRAIN + '\n' + html[idx:]
print("4. Expert brain injected")

# 5. showTab patch
old_tab = '''  if (name === "tutorials") { pauseAssistantChat(); tutOffset = 0; renderTutorials(true); }
  else if (name === "video") { pauseAssistantChat(); renderPayment(); }
  else if (name === "notes") { pauseAssistantChat(); renderNotes(); }
  else if (name === "ai") { pauseAssistantChat(); updateNet(); var inp = byId("aiInput"); if (inp) setTimeout(function () { try { inp.focus(); } catch (e) {} }, 50); }
  else if (name === "chat") { setTimeout(function () { openAssistantTab(); }, 200); }'''

new_tab = '''  if (name === "tutorials") { pauseAssistantChat(); if (typeof expertOnLeave === "function") expertOnLeave(); tutOffset = 0; renderTutorials(true); }
  else if (name === "video") { pauseAssistantChat(); if (typeof expertOnLeave === "function") expertOnLeave(); renderPayment(); }
  else if (name === "notes") { pauseAssistantChat(); if (typeof expertOnLeave === "function") expertOnLeave(); renderNotes(); }
  else if (name === "ai") { pauseAssistantChat(); updateNet(); if (typeof expertOnEnter === "function") setTimeout(expertOnEnter, 120); }
  else if (name === "chat") { if (typeof expertOnLeave === "function") expertOnLeave(); setTimeout(function () { openAssistantTab(); }, 200); }'''

if old_tab in html:
    html = html.replace(old_tab, new_tab, 1)
    print("5. showTab patched")
else:
    print("5. WARN: showTab block not found")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Expert tab installed.")
