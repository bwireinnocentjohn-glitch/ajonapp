import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# Insert new helpers + intents bank BEFORE exComposeReply
# ============================================================
marker = "function exComposeReply("
idx = html.find(marker)
if idx == -1:
    print("ERR exComposeReply not found"); sys.exit(1)
line_start = html.rfind("\n", 0, idx) + 1

NEW_HELPERS = r'''
/* ============================================================
   Expert brain v2 — word-boundary matching + intents bank
   ============================================================ */
function exHasWord(hay, word) {
  if (!hay || !word) return false;
  var i = 0, len = word.length;
  while ((i = hay.indexOf(word, i)) !== -1) {
    var b = (i === 0) ? " " : hay.charAt(i - 1);
    var a = (i + len >= hay.length) ? " " : hay.charAt(i + len);
    if (!/[a-z0-9]/.test(b) && !/[a-z0-9]/.test(a)) return true;
    i += len;
  }
  return false;
}

var EX_INTENTS = [
  { kw:["save","saving","savings","keep money","keep cash"],
    r:[
      "\uD83D\uDCB0 Saving is discipline, not a miracle.\n\nRule: save BEFORE you spend, never after.\n\n\u2022 Sell \u2192 take 10% out immediately\n\u2022 Open a separate pocket today\n\u2022 Never touch savings for small things",
      "\uD83D\uDCB0 Three saving steps:\n1. Separate pocket for savings \u2014 today.\n2. Every sale \u2192 10% moves there instantly.\n3. Only touch it for emergencies or growth.",
      "\uD83D\uDCB0 The rich count daily. The poor count yearly.\n\nTrack every shilling that leaves your pocket tonight. You cannot save what you do not track."
    ]
  },
  { kw:["price","pricing","charge","how much"],
    r:[
      "\uD83D\uDCB0 Pricing rule:\n1. Calculate full cost (materials + time + transport)\n2. Add 30% margin minimum\n3. Never price below cost\n\nFair price beats cheap price every season.",
      "\uD83D\uDCB0 Root is not the price. Root is pricing from fear, not value.\n\nShow the outcome, not the product. Tell 3 buyers the price with confidence today.",
      "\uD83D\uDCB0 Do not compete on price alone. You will run out of price.\n\nAdd value: faster delivery, better packaging, personal service."
    ]
  },
  { kw:["start","starting","begin","first step"],
    r:[
      "\uD83D\uDE80 Start small. Start scared. Start today.\n\n\u2022 Buy the smallest starter kit\n\u2022 Sell to 3 people face to face\n\u2022 Learn one product deeply this week",
      "\uD83D\uDE80 The first step is the only step you control.\n\nDo one small action within 30 minutes. Not tomorrow. Today.",
      "\uD83D\uDE80 Start where you are. Use what you have. Do what you can.\n\nPerfection is a beautiful excuse to do nothing."
    ]
  },
  { kw:["customer","customers","buyer","buyers","client","clients"],
    r:[
      "\uD83E\uDD1D Your first 10 customers are your real teachers.\n\n\u2022 Ask what they wish you sold better\n\u2022 Learn their names\n\u2022 Give a small surprise at every sale",
      "\uD83E\uDD1D Ten loyal customers beat a hundred random buyers.\n\nBuild a customer, not a sale.",
      "\uD83E\uDD1D Customers forget what you said. They remember how you made them feel.\n\nServe with joy. Every time."
    ]
  },
  { kw:["marketing","advertise","promote","advert"],
    r:[
      "\uD83D\uDCE3 One clear message, repeated many times, beats many messages once.\n\n\u2022 Pick one message\n\u2022 Repeat it 20 times this week\n\u2022 Best ads are happy customers",
      "\uD83D\uDCE3 Word of mouth is the cheapest ad.\n\nDeliver one great experience \u2192 get five new customers.",
      "\uD83D\uDCE3 Do not sell to everyone. Serve someone well.\n\nEmpty shelves teach nobody."
    ]
  },
  { kw:["staff","employee","worker","hire","hiring"],
    r:[
      "\uD83D\uDC65 Systems first, people second.\n\n\u2022 Write the job in 5 steps\n\u2022 Test one worker for 2 weeks\n\u2022 Pay fairly. Train deeply. Respect always.",
      "\uD83D\uDC65 One worker paid well beats five paid badly.\n\nEmployees copy what you do, not what you say.",
      "\uD83D\uDC65 Do not hire hands you cannot trust with your name.\n\nTrust but verify. Verify but respect."
    ]
  },
  { kw:["competition","competitor","rival"],
    r:[
      "\uD83C\uDFC1 Do not copy. Study.\n\n\u2022 Talk to 5 old customers this week\n\u2022 Add one service they cannot copy\n\u2022 Serve regulars like family",
      "\uD83C\uDFC1 Root is not the competitor. Root is you got comfortable before they arrived.",
      "\uD83C\uDFC1 Raise your value, not your volume.\n\nFair price beats cheap price."
    ]
  },
  { kw:["record","records","books","bookkeeping","receipt"],
    r:[
      "\uD83D\uDCD3 Write it down. Memory is a liar.\n\nBuy a notebook today. 3 columns: cost, sale, cash left.",
      "\uD83D\uDCD3 If numbers do not excite you, they will exhaust you.\n\nCount cash at 9pm every night.",
      "\uD83D\uDCD3 A handwritten book of sales beats a head full of memory."
    ]
  },
  { kw:["discipline","routine","consistent","consistency"],
    r:[
      "\uD83D\uDCAA Discipline is the only partner that stays.\n\n\u2022 Set fixed wake-up time\n\u2022 Write 3 daily tasks the night before\n\u2022 Open your shop at same time daily",
      "\uD83D\uDCAA Motivation is boda. Discipline is tarmac.\n\nShow up daily. That alone beats 90%.",
      "\uD83D\uDCAA A schedule is a promise you keep to yourself.\n\nDo the boring things daily. The boring things compound."
    ]
  },
  { kw:["family","wife","husband","children"],
    r:[
      "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Give them a plan, not just cash.\n\n\u2022 Open a separate family pocket\n\u2022 Give fixed amount monthly, not on demand\n\u2022 Explain your plan tonight",
      "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Pay yourself first. Then help.\n\nA business that divides a family will fail.",
      "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Root is not family pressure. Root is family has needs but no plan."
    ]
  },
  { kw:["fear","afraid","scared","worry","worried"],
    r:[
      "\uD83D\uDE30 Fear is a liar that speaks fluent truth.\n\nStart scared. Finish proud.",
      "\uD83D\uDE30 Root is not fear of losing money. Root is you have not separated dream from pocket yet.",
      "\uD83D\uDE30 Courage is acting WITH fear, not without it.\n\nDo one small brave thing today."
    ]
  },
  { kw:["fail","failed","failure","lose money","lost"],
    r:[
      "\uD83D\uDCA3 Failure is the school that never closes.\n\nWrite 3 lessons from the failure tonight. Try again with smaller scale.",
      "\uD83D\uDCA3 Regret is more expensive than risk.\n\nTry. Fail. Learn. Try again. The cycle IS the business.",
      "\uD83D\uDCA3 You will be told no 100 times before you hear a profitable yes.\n\nRejection is data, not damage."
    ]
  },
  { kw:["motivate","motivation","inspire","encourage"],
    r:[
      "\uD83D\uDCAA Every rich person you see was once a poor person who did not quit.",
      "\uD83D\uDE80 Fall seven times, stand up eight.",
      "\uD83C\uDF1F Your current situation is not your final destination."
    ]
  },
  { kw:["capital","startup","start money","start with"],
    r:[
      "\uD83D\uDCB0 Learn to grow 50k before you touch 500k.\n\nBuy smallest starter kit today. Sell to 3 people today.",
      "\uD83D\uDCB0 Root is not small money. Root is you have not practised with small money yet.",
      "\uD83D\uDCB0 Test small, scale big.\n\nSmall capital teaches more than big capital."
    ]
  },
  { kw:["loan","debt","borrow"],
    r:[
      "\uD83D\uDCB3 Debt for growth is a bridge. Debt for comfort is a noose.\n\nBorrow to buy stock, not shoes.",
      "\uD83D\uDCB3 Root is not the debt. Root is the reason the debt was taken.",
      "\uD83D\uDCB3 Write exactly what the loan is for tonight.\n\nCalculate monthly repayment before signing."
    ]
  },
  { kw:["business idea","idea","suggest a business","what business"],
    r:["__RANDOM_BUSINESS__"]
  }
];

function exMatchIntent(q) {
  var low = " " + String(q || "").toLowerCase().replace(/[^a-z0-9]+/g, " ") + " ";
  for (var i = 0; i < EX_INTENTS.length; i++) {
    var intent = EX_INTENTS[i];
    for (var j = 0; j < intent.kw.length; j++) {
      if (low.indexOf(" " + intent.kw[j] + " ") > -1) return intent;
    }
  }
  return null;
}

function exMatchThanks(q) {
  var low = String(q || "").toLowerCase().trim();
  return /^(thanks|thank you|thx|webale|asante)/.test(low);
}
function exMatchAck(q) {
  var low = String(q || "").toLowerCase().trim().replace(/[!?.]+/g, "");
  return low === "ok" || low === "okay" || low === "sure" || low === "yes" ||
         low === "yeah" || low === "k" || low === "alright" ||
         low === "got it" || low === "cool" || low === "fine";
}

/* New business matcher: requires a title-word match */
function exMatchBusiness(q) {
  if (typeof ALL_BUSINESSES === "undefined" || !ALL_BUSINESSES.length) return null;
  var low = String(q || "").toLowerCase();
  var words = low.split(/[^a-z0-9]+/).filter(function(w){ return w.length >= 4; });
  if (!words.length) return null;
  var best = null, bestScore = 0;
  for (var i = 0; i < ALL_BUSINESSES.length; i++) {
    var b = ALL_BUSINESSES[i];
    var titleLow = String(b.t || "").toLowerCase();
    /* must have a title-word hit */
    var titleHits = 0;
    for (var w = 0; w < words.length; w++) {
      if (exHasWord(titleLow, words[w])) titleHits++;
    }
    if (titleHits < 1) continue;
    var hay = (titleLow + " " + (b.tagline || "") + " " + (b.sell || "") + " " + (b.buy || "")).toLowerCase();
    var score = titleHits * 4;
    for (var w2 = 0; w2 < words.length; w2++) {
      if (exHasWord(hay, words[w2])) score += 1;
    }
    if (titleLow && low.indexOf(titleLow) > -1) score += 20;
    if (score > bestScore) { bestScore = score; best = b; }
  }
  return bestScore >= 4 ? best : null;
}
'''

html = html[:line_start] + NEW_HELPERS + "\n" + html[line_start:]
print("Helpers + intents inserted.")

# ============================================================
# Replace exComposeReply with new version
# ============================================================
idx2 = html.find("function exComposeReply(")
if idx2 == -1:
    print("ERR exComposeReply not found 2"); sys.exit(1)
brace = html.find("{", idx2)
depth = 0
i = brace
while i < len(html):
    ch = html[i]
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break
    i += 1

NEW_COMPOSE = r'''function exComposeReply(q) {
  try {
    var clean = exCorrectTypos(String(q || "").trim());
    if (!clean) return ["Please type a question. \uD83D\uDE42"];

    if (exMatchGreeting(clean)) {
      return [EX_GREET_REPLY[Math.floor(Math.random() * EX_GREET_REPLY.length)]];
    }
    if (exMatchThanks(clean)) {
      return ["You are welcome! \uD83D\uDE4F Keep pushing. Ask me anytime."];
    }
    if (exMatchAck(clean)) {
      return ["Good! \uD83D\uDCAA Now go and take one small action today."];
    }
    if (exIsJokeRequest(clean)) {
      return [EX_JOKES[Math.floor(Math.random() * EX_JOKES.length)]];
    }
    if (exIsFactRequest(clean)) {
      return [EX_FACTS[Math.floor(Math.random() * EX_FACTS.length)]];
    }
    if (exIsQuoteRequest(clean)) {
      var qq = EX_QUOTES[Math.floor(Math.random() * EX_QUOTES.length)];
      return [qq.i + " " + qq.t];
    }

    /* 1. Business term (specific phrases first) */
    var termKey = exMatchTerm(clean);
    if (termKey) {
      return ["\uD83D\uDCD8 " + termKey.charAt(0).toUpperCase() + termKey.slice(1) + ":\n\n" + EX_TERMS[termKey]];
    }

    /* 2. Intents (saving, pricing, starting, etc.) */
    var intent = exMatchIntent(clean);
    if (intent) {
      if (intent.r.length === 1 && intent.r[0] === "__RANDOM_BUSINESS__") {
        if (typeof ALL_BUSINESSES !== "undefined" && ALL_BUSINESSES.length) {
          var rb = ALL_BUSINESSES[Math.floor(Math.random() * ALL_BUSINESSES.length)];
          var rbout = [];
          rbout.push("\uD83D\uDCA1 Here is one idea for you: " + rb.emoji + " " + rb.t);
          if (rb.tagline) rbout.push(rb.tagline);
          rbout.push("Start: " + fmt(rb.cost) + " UGX");
          rbout.push("Profit: " + fmt(rb.profit) + " UGX per batch");
          if (rb.buy) rbout.push("\uD83D\uDED2 Buy from: " + rb.buy);
          if (rb.sell) rbout.push("\uD83C\uDFEA Sell at: " + rb.sell);
          if (rb.steps && rb.steps[0]) rbout.push("\uD83D\uDD27 Step 1: " + String(rb.steps[0]).substring(0, 160));
          rbout.push("\uD83D\uDCDA See full steps in the Tutorials tab.");
          return [rbout.join("\n")];
        }
      } else {
        return [intent.r[Math.floor(Math.random() * intent.r.length)]];
      }
    }

    /* 3. Business match (now safe with word boundaries) */
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

    /* 4. Encouragement */
    if (exMatchEncourage(clean)) {
      return [EX_ENCOURAGE[Math.floor(Math.random() * EX_ENCOURAGE.length)]];
    }

    /* 5. Fallback — wise response */
    var quote = EX_QUOTES[Math.floor(Math.random() * EX_QUOTES.length)];
    var lc = clean.toLowerCase();
    if (/\b(what|how|why|where|when|which|who)\b/.test(lc)) {
      return [
        "Good question. \uD83E\uDD14 Let me share wisdom.",
        quote.i + " " + quote.t,
        "\uD83D\uDCA1 I can help with:\n\u2022 Businesses \u2014 try 'soap', 'honey', 'cricket', 'oil'\n\u2022 Terms \u2014 try 'cash flow', 'profit margin'\n\u2022 Life \u2014 try 'motivate me', 'tell me a joke', 'bible verse'\nAsk me more specifically."
      ];
    }
    return [
      "I am here. \uD83D\uDE42",
      quote.i + " " + quote.t,
      "\uD83D\uDCA1 Try: 'how do I save money?' or 'tell me about soap business' or 'what is cash flow?'"
    ];
  } catch (e) {
    return ["I am here. \uD83D\uDE42 Please try asking again."];
  }
}'''

html = html[:idx2] + NEW_COMPOSE + html[end:]
print("exComposeReply replaced.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Expert wisdom v2 installed.")
