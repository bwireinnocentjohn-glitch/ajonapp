import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

def replace_bracket_block(src, start_marker, open_ch, close_ch, new_block):
    start = src.find(start_marker)
    if start == -1: return src, False
    open_pos = src.find(open_ch, start)
    if open_pos == -1: return src, False
    depth = 0; i = open_pos
    while i < len(src):
        ch = src[i]
        if ch == open_ch: depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return src[:start] + new_block + src[i+1:], True
        i += 1
    return src, False

# ============================================================
# 1. Status span: Earth spinning in place
# ============================================================
old_span = '<span class="expert-status" id="expertStatus"><span class="expert-earth" aria-hidden="true"></span> Ready</span>'
new_span = '<span class="expert-status" id="expertStatus"><span class="expert-earth"><span class="expert-earth-sphere"></span></span> Ready</span>'
if old_span in html:
    html = html.replace(old_span, new_span)
    print("1. Status span updated")
elif 'expert-earth-sphere' in html:
    print("1. Already updated")
else:
    # try the older version without span
    old2 = '<span class="expert-status" id="expertStatus">&#x1F7E2; Ready</span>'
    if old2 in html:
        html = html.replace(old2, new_span)
        print("1. Status span updated (from plain dot)")
    else:
        print("1. WARN: status span not found")

# ============================================================
# 2. Earth CSS — self-spinning globe in fixed position
# ============================================================
EARTH_CSS = """
/* ========== Expert Earth globe — spinning on its own axis ========== */
.expert-status {
  display: inline-flex !important;
  align-items: center;
  gap: 6px;
}
.expert-earth {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  overflow: hidden;
  flex: 0 0 auto;
  vertical-align: middle;
  position: relative;
  background: radial-gradient(circle at 32% 32%, #5bb6ff 0%, #1c56a8 48%, #05132e 100%);
  box-shadow:
    inset -6px -5px 10px rgba(0,0,0,.85),
    inset 3px 3px 6px rgba(150,215,255,.5),
    0 0 10px rgba(0,200,83,.65),
    0 0 3px rgba(90,180,255,.6);
  animation: earthGlow 3s ease-in-out infinite;
}
.expert-earth-sphere {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-image:
    radial-gradient(circle at 4px 5px, #2f9d47 0%, #2f9d47 3px, transparent 3.5px),
    radial-gradient(circle at 14px 3px, #2f9d47 0%, #2f9d47 4px, transparent 4.5px),
    radial-gradient(circle at 22px 11px, #2f9d47 0%, #2f9d47 3px, transparent 3.5px),
    radial-gradient(circle at 7px 14px, #2f9d47 0%, #2f9d47 3px, transparent 3.5px),
    radial-gradient(circle at 28px 6px, #2f9d47 0%, #2f9d47 3px, transparent 3.5px),
    radial-gradient(circle at 16px 16px, #2f9d47 0%, #2f9d47 2.5px, transparent 3px),
    radial-gradient(circle at 2px 17px, #2f9d47 0%, #2f9d47 3px, transparent 3.5px),
    radial-gradient(circle at 20px 1px, #2f9d47 0%, #2f9d47 2px, transparent 2.5px);
  background-size: 34px 100%;
  background-repeat: repeat-x;
  animation: earthAxialSpin 6s linear infinite;
}
.expert-earth-sphere::after {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  border-radius: 50%;
  background:
    radial-gradient(circle at 28% 22%, rgba(255,255,255,.32) 0%, transparent 42%),
    radial-gradient(circle at 100% 100%, rgba(0,0,0,.7) 0%, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(0,0,0,.5) 0%, transparent 50%);
  pointer-events: none;
}
@keyframes earthAxialSpin {
  from { background-position:   0px 0; }
  to   { background-position: -34px 0; }
}
@keyframes earthGlow {
  0%, 100% { box-shadow:
    inset -6px -5px 10px rgba(0,0,0,.85),
    inset 3px 3px 6px rgba(150,215,255,.5),
    0 0 8px rgba(0,200,83,.55),
    0 0 3px rgba(90,180,255,.5); }
  50% { box-shadow:
    inset -6px -5px 10px rgba(0,0,0,.85),
    inset 3px 3px 6px rgba(150,215,255,.7),
    0 0 14px rgba(0,200,83,.85),
    0 0 5px rgba(90,180,255,.8); }
}
"""

# Remove old Earth CSS block if present
if '.expert-earth' in html and 'earthAxialSpin' not in html:
    start = html.find('/* ========== Expert Earth globe')
    if start == -1:
        start = html.find('.expert-earth {')
    if start != -1:
        # find the end of our earth css (next closing of the last @keyframes)
        end = html.find('@keyframes earthSpin', start)
        if end != -1:
            end_close = html.find('}', html.find('{', html.find('{', end)+1)+1) + 1
            html = html[:start] + html[end_close:]

if 'earthAxialSpin' not in html:
    idx = html.rfind('</style>')
    if idx == -1: print("ERR </style>"); sys.exit(1)
    html = html[:idx] + EARTH_CSS + '\n' + html[idx:]
    print("2. Earth CSS installed")
else:
    print("2. Earth CSS already current")

# ============================================================
# 3. EX_INTENTS — expanded
# ============================================================
NEW_INTENTS = r'''var EX_INTENTS = [
  { kw:["save","saving","savings","keep money","keep cash","store money","put aside"],
    r:[
      "\uD83D\uDCB0 Saving is discipline, not a miracle.\n\nRule: save BEFORE you spend, never after.\n\n\u2022 Sell \u2192 take 10% out immediately\n\u2022 Open a separate pocket today\n\u2022 Never touch savings for small things",
      "\uD83D\uDCB0 Three saving steps:\n1. Separate pocket for savings \u2014 today.\n2. Every sale \u2192 10% moves there instantly.\n3. Only touch it for emergencies or growth.",
      "\uD83D\uDCB0 The rich count daily. The poor count yearly.\n\nTrack every shilling that leaves your pocket tonight. You cannot save what you do not track."
    ]
  },
  { kw:["price","pricing","charge","how much","rate","cost of my product"],
    r:[
      "\uD83D\uDCB0 Pricing rule:\n1. Calculate full cost (materials + time + transport)\n2. Add 30% margin minimum\n3. Never price below cost\n\nFair price beats cheap price every season.",
      "\uD83D\uDCB0 Root is not the price. Root is pricing from fear, not value.\n\nShow the outcome, not the product. Tell 3 buyers the price with confidence today.",
      "\uD83D\uDCB0 Do not compete on price alone. You will run out of price.\n\nAdd value: faster delivery, better packaging, personal service."
    ]
  },
  { kw:["start","starting","begin","beginner","first step","start small","launch"],
    r:[
      "\uD83D\uDE80 Start small. Start scared. Start today.\n\n\u2022 Buy the smallest starter kit\n\u2022 Sell to 3 people face to face\n\u2022 Learn one product deeply this week",
      "\uD83D\uDE80 The first step is the only step you control.\n\nDo one small action within 30 minutes. Not tomorrow. Today.",
      "\uD83D\uDE80 Start where you are. Use what you have. Do what you can.\n\nPerfection is a beautiful excuse to do nothing."
    ]
  },
  { kw:["customer","customers","buyer","buyers","client","clients","shoppers"],
    r:[
      "\uD83E\uDD1D Your first 10 customers are your real teachers.\n\n\u2022 Ask what they wish you sold better\n\u2022 Learn their names\n\u2022 Give a small surprise at every sale",
      "\uD83E\uDD1D Ten loyal customers beat a hundred random buyers.\n\nBuild a customer, not a sale.",
      "\uD83E\uDD1D Customers forget what you said. They remember how you made them feel.\n\nServe with joy. Every time."
    ]
  },
  { kw:["marketing","advertise","advertising","promote","promotion","brand awareness"],
    r:[
      "\uD83D\uDCE3 One clear message, repeated many times, beats many messages once.\n\n\u2022 Pick one message\n\u2022 Repeat it 20 times this week\n\u2022 Best ads are happy customers",
      "\uD83D\uDCE3 Word of mouth is the cheapest ad.\n\nDeliver one great experience \u2192 get five new customers.",
      "\uD83D\uDCE3 Do not sell to everyone. Serve someone well.\n\nEmpty shelves teach nobody."
    ]
  },
  { kw:["staff","employee","worker","hire","hiring","team","employees"],
    r:[
      "\uD83D\uDC65 Systems first, people second.\n\n\u2022 Write the job in 5 steps\n\u2022 Test one worker for 2 weeks\n\u2022 Pay fairly. Train deeply. Respect always.",
      "\uD83D\uDC65 One worker paid well beats five paid badly.\n\nEmployees copy what you do, not what you say.",
      "\uD83D\uDC65 Do not hire hands you cannot trust with your name.\n\nTrust but verify. Verify but respect."
    ]
  },
  { kw:["competition","competitor","rival","copy","someone opened"],
    r:[
      "\uD83C\uDFC1 Do not copy. Study.\n\n\u2022 Talk to 5 old customers this week\n\u2022 Add one service they cannot copy\n\u2022 Serve regulars like family",
      "\uD83C\uDFC1 Root is not the competitor. Root is you got comfortable before they arrived.",
      "\uD83C\uDFC1 Raise your value, not your volume.\n\nFair price beats cheap price."
    ]
  },
  { kw:["record","records","books","bookkeeping","receipt","accounting","ledger"],
    r:[
      "\uD83D\uDCD3 Write it down. Memory is a liar.\n\nBuy a notebook today. 3 columns: cost, sale, cash left.",
      "\uD83D\uDCD3 If numbers do not excite you, they will exhaust you.\n\nCount cash at 9pm every night.",
      "\uD83D\uDCD3 A handwritten book of sales beats a head full of memory."
    ]
  },
  { kw:["discipline","routine","consistent","consistency","lazy","habit","focus"],
    r:[
      "\uD83D\uDCAA Discipline is the only partner that stays.\n\n\u2022 Set fixed wake-up time\n\u2022 Write 3 daily tasks the night before\n\u2022 Open your shop at same time daily",
      "\uD83D\uDCAA Motivation is boda. Discipline is tarmac.\n\nShow up daily. That alone beats 90%.",
      "\uD83D\uDCAA A schedule is a promise you keep to yourself.\n\nDo the boring things daily. The boring things compound."
    ]
  },
  { kw:["family","wife","husband","children","mother","father","relatives"],
    r:[
      "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Give them a plan, not just cash.\n\n\u2022 Open a separate family pocket\n\u2022 Give fixed amount monthly, not on demand\n\u2022 Explain your plan tonight",
      "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Pay yourself first. Then help.\n\nA business that divides a family will fail.",
      "\uD83D\uDC68\u200D\uD83D\uDC69\u200D\uD83D\uDC67 Root is not family pressure. Root is family has needs but no plan."
    ]
  },
  { kw:["fear","afraid","scared","worry","worried","anxious","nervous"],
    r:[
      "\uD83D\uDE30 Fear is a liar that speaks fluent truth.\n\nStart scared. Finish proud.",
      "\uD83D\uDE30 Root is not fear of losing money. Root is you have not separated dream from pocket yet.",
      "\uD83D\uDE30 Courage is acting WITH fear, not without it.\n\nDo one small brave thing today."
    ]
  },
  { kw:["fail","failed","failure","lose money","lost money","loss"],
    r:[
      "\uD83D\uDCA3 Failure is the school that never closes.\n\nWrite 3 lessons from the failure tonight. Try again with smaller scale.",
      "\uD83D\uDCA3 Regret is more expensive than risk.\n\nTry. Fail. Learn. Try again. The cycle IS the business.",
      "\uD83D\uDCA3 You will be told no 100 times before you hear a profitable yes.\n\nRejection is data, not damage."
    ]
  },
  { kw:["motivate","motivation","inspire","encourage","push me"],
    r:[
      "\uD83D\uDCAA Every rich person you see was once a poor person who did not quit.",
      "\uD83D\uDE80 Fall seven times, stand up eight.",
      "\uD83C\uDF1F Your current situation is not your final destination."
    ]
  },
  { kw:["capital","startup money","start money","start with","small money"],
    r:[
      "\uD83D\uDCB0 Learn to grow 50k before you touch 500k.\n\nBuy smallest starter kit today. Sell to 3 people today.",
      "\uD83D\uDCB0 Root is not small money. Root is you have not practised with small money yet.",
      "\uD83D\uDCB0 Test small, scale big.\n\nSmall capital teaches more than big capital."
    ]
  },
  { kw:["loan","debt","borrow","credit","lender"],
    r:[
      "\uD83D\uDCB3 Debt for growth is a bridge. Debt for comfort is a noose.\n\nBorrow to buy stock, not shoes.",
      "\uD83D\uDCB3 Root is not the debt. Root is the reason the debt was taken.",
      "\uD83D\uDCB3 Write exactly what the loan is for tonight.\n\nCalculate monthly repayment before signing."
    ]
  },
  { kw:["whatsapp","status","tiktok","instagram","online sell","sell online"],
    r:[
      "\uD83D\uDCF1 Your WhatsApp is your shop window.\n\n\u2022 Add business name and photo\n\u2022 Post 3 products in status daily\n\u2022 Show prices clearly",
      "\uD83D\uDCF1 One platform done well beats five done badly.\n\nPick WhatsApp or TikTok. Master it for 90 days.",
      "\uD83D\uDCF1 Online selling is simple:\n1. Take clear photos\n2. Post at same times daily\n3. Reply within 5 minutes"
    ]
  },
  { kw:["complaint","complaints","angry customer","unhappy customer","refund"],
    r:[
      "\uD83D\uDE22 Complaints are gifts in ugly wrapping.\n\nApologise fast. Correct faster. Within 24 hours.",
      "\uD83D\uDE22 Win the customer, not the argument.\n\nA refund now protects a customer forever.",
      "\uD83D\uDE22 Ask one complaining customer: what would fix this?\n\nThen do it."
    ]
  },
  { kw:["quality","standard","defect","returned product"],
    r:[
      "\u2B50 Quality is a habit, not an act.\n\n\u2022 Write 5 quality checks\n\u2022 Do them every single sale\n\u2022 Test before delivery",
      "\u2B50 Root is not quality being hard. Root is no routine protects it daily.",
      "\u2B50 Every shilling saved on cheap quality costs ten shillings in reputation later."
    ]
  },
  { kw:["trust","reputation","respect","honest"],
    r:[
      "\uD83E\uDD1D Money follows trust. Trust follows consistency.\n\nDeliver what you promised, plus one small surprise.",
      "\uD83E\uDD1D Your name is your first brand. Protect it.",
      "\uD83E\uDD1D A promise kept is a customer kept.\n\nA promise broken is a review online you cannot delete."
    ]
  },
  { kw:["no time","busy","overworked","too many things"],
    r:[
      "\u23F0 You do not lack time. You lack priority.\n\n\u2022 Write tomorrow's top 3 tasks tonight\n\u2022 Do #1 before phone\n\u2022 Say no to the rest",
      "\u23F0 Do the important before the urgent.\n\nMost urgent things are other people's emergencies.",
      "\u23F0 Time is the only currency you cannot earn back.\n\nSpend it like money."
    ]
  },
  { kw:["where does money go","money disappears","money vanishing","leak"],
    r:[
      "\uD83D\uDD0D Money does not vanish. It leaks.\n\nTrack every shilling for 7 days. You will find 3 leaks.",
      "\uD83D\uDD0D Root is not low sales. Root is money leaves faster than it enters.",
      "\uD83D\uDD0D Small leaks sink big ships.\n\nBuy a small notebook today. Write every coin that leaves."
    ]
  },
  { kw:["expand","expansion","grow","growth","second branch","scale"],
    r:[
      "\uD83C\uDFD7\uFE0F Root is not scale. Root is stability.\n\nStable small, then stable bigger, then stable biggest.",
      "\uD83C\uDFD7\uFE0F One shop done well is worth ten done badly.\n\nCheck if first shop is leaking before opening a second.",
      "\uD83C\uDFD7\uFE0F Expand when you have 3 months of costs saved.\n\nNot when you feel excited."
    ]
  },
  { kw:["location","where to sell","place","where sell"],
    r:[
      "\uD83D\uDCCD Location is a business decision, not a rent decision.\n\nCount foot traffic tomorrow morning. 1 hour.",
      "\uD83D\uDCCD Location is never the problem. Trust is.\n\nA good location with bad service dies fast.",
      "\uD83D\uDCCD Small town, big trust. Big town, big noise.\n\nChoose the market you can own."
    ]
  },
  { kw:["brand","branding","logo","name for my business"],
    r:[
      "\uD83C\uDFF7\uFE0F Root is not needing a logo. Root is people do not know what to feel about your name.\n\nPick one feeling. Premium or cheap. Friendly or fast.",
      "\uD83C\uDFF7\uFE0F Reputation is your real capital.\n\nEvery customer is a walking review.",
      "\uD83C\uDFF7\uFE0F Show up daily. Consistency IS the brand."
    ]
  },
  { kw:["bargain","bargaining","negotiate","negotiation","discount"],
    r:[
      "\uD83E\uDD1D Never negotiate on price alone. Add value instead.\n\n\u2022 Set your lowest price tonight\n\u2022 Offer a small extra, not a discount\n\u2022 Walk away if below cost",
      "\uD83E\uDD1D A customer who only wants cheap will leave for cheaper.\n\nAttract value seekers.",
      "\uD83E\uDD1D Fair price beats cheap price every season."
    ]
  },
  { kw:["partner","partnership","co-founder","joint"],
    r:[
      "\uD83E\uDD1D Partners need contracts, not just trust.\n\nWrite terms on one page today.",
      "\uD83E\uDD1D Choose partner for skill, not friendship.\n\nList what skills you lack today.",
      "\uD83E\uDD1D A business that divides a family will fail. A business that unites one will rise."
    ]
  },
  { kw:["goal","goals","vision","plan","planning","target"],
    r:[
      "\uD83C\uDFAF Write the goal where you see it every morning.\n\n\u2022 1 goal for this week\n\u2022 3 tasks daily\n\u2022 Review every Sunday",
      "\uD83C\uDFAF Hope is not a plan. So write the plan.",
      "\uD83C\uDFAF Vague goals produce vague results.\n\nWrite one clear goal tonight."
    ]
  },
  { kw:["tired","burnout","exhausted","rest","break"],
    r:[
      "\uD83D\uDE34 Rest is strategy, not laziness.\n\n\u2022 Block 4 hours this Sunday\n\u2022 No phone for 2 of those hours\n\u2022 Sleep 8 hours tonight",
      "\uD83D\uDE34 A tired mind makes bad deals.\n\nRest today so you can win tomorrow.",
      "\uD83D\uDE34 Do not push through exhaustion. Push through the plan, but rest the body."
    ]
  },
  { kw:["success","succeed","win","won","proud","congratulate"],
    r:[
      "\uD83C\uDF89 Congratulations! Now celebrate small and build bigger.\n\nWrite down what worked. Repeat it.",
      "\uD83C\uDF89 Every win is a teacher.\n\nWhat made this one work? Do more of that.",
      "\uD83C\uDF89 Success is not the finish line. It is the fuel for the next mountain."
    ]
  },
  { kw:["rich","wealth","millionaire","get rich"],
    r:[
      "\uD83D\uDCB0 Real wealth takes years. Fake wealth takes weeks.\n\nStart small. Stay consistent. Compound.",
      "\uD83D\uDCB0 The rich count daily. The poor count yearly.\n\nChange your count, change your wealth.",
      "\uD83D\uDCB0 Wealth is built in silence and advertised in results."
    ]
  },
  { kw:["business idea","idea","suggest a business","what business","new business","opportunity"],
    r:["__RANDOM_BUSINESS__"]
  }
];'''

html, ok = replace_bracket_block(html, "var EX_INTENTS = [", "[", "]", NEW_INTENTS)
print("3. EX_INTENTS: " + ("OK" if ok else "NOT FOUND"))

# ============================================================
# 4. Extend EX_TERMS
# ============================================================
NEW_TERMS = '''
Object.assign(EX_TERMS, {
  "cash flow positive": "When money coming in is more than money going out. The goal of every business.",
  "cash flow negative": "When money going out is more than money coming in. Danger zone.",
  "working capital": "Money available for daily running. Stock plus cash minus debts.",
  "opportunity cost": "What you give up when you choose something else.",
  "compounding": "Small growth repeated that snowballs over time. 1000 saved monthly grows to millions.",
  "word of mouth": "Free marketing from happy customers telling others. The cheapest and strongest ad.",
  "customer loyalty": "When customers keep buying from you instead of competitors. Earned through consistency.",
  "customer lifetime value": "Total money one customer spends with you over years. High LTV pays for marketing.",
  "cash on delivery": "Customer pays when the goods arrive. Common for online sellers in Uganda.",
  "layaway": "Customer pays in installments before receiving the goods.",
  "supplier credit": "When your supplier gives you goods now and you pay later. Powerful but dangerous.",
  "reserve fund": "Money set aside for emergencies. Should cover 3 months of costs.",
  "product market fit": "When what you sell matches what customers want to buy. The most important milestone.",
  "social proof": "Evidence that others trust you. Reviews, testimonials, photos of happy customers.",
  "lead generation": "Finding people who might become customers. Before they buy.",
  "sales funnel": "The path from stranger to buyer: awareness, interest, decision, action.",
  "average order value": "Total sales divided by number of orders. Raise it with bundles.",
  "churn rate": "Percentage of customers who leave and never come back.",
  "stakeholder": "Anyone with interest in your business. Owners, staff, customers, suppliers.",
  "niche market": "A small, focused segment of a larger market. Easier to own.",
  "pipeline": "List of potential customers in different stages of buying.",
  "beta customer": "An early customer who tests your product before public launch.",
  "seed capital": "The first small amount of money used to start a business.",
  "bootstrapped": "Started and grown with your own money, no outside investors.",
  "value proposition": "The clear reason a customer should buy from you instead of others.",
  "pain point": "A problem your customer has that your product solves.",
  "market segmentation": "Dividing your market into groups with different needs.",
  "differentiation": "Being meaningfully different so price becomes less important.",
  "cost leadership": "Being the cheapest and still profitable. Needs huge volume.",
  "premium pricing": "Charging higher than competitors because of quality or brand.",
  "penetration pricing": "Starting with very low prices to grab market share, then raising.",
  "loss leader": "A product sold at a loss to attract customers who buy other things."
});
'''
if 'Object.assign(EX_TERMS' not in html:
    start_terms = html.find("var EX_TERMS = {")
    if start_terms != -1:
        after = html.find("function exLevenshtein", start_terms)
        close = html.rfind("};", start_terms, after)
        if close != -1:
            html = html[:close+2] + "\n" + NEW_TERMS + "\n" + html[close+2:]
            print("4. EX_TERMS extended")
        else:
            print("4. WARN close not found")
    else:
        print("4. WARN not found")
else:
    print("4. Already extended")

# ============================================================
# 5. Suggestion pool — 60 rotating
# ============================================================
NEW_SUGS = r'''function exRenderSuggestions() {
  var bar = byId("expertSugs");
  if (!bar) return;
  var pool = [
    "how do I save money?",
    "how do I price my product?",
    "how do I start small?",
    "how do I get customers?",
    "how do I advertise?",
    "should I hire a worker?",
    "how do I beat competition?",
    "should I keep records?",
    "how do I stay disciplined?",
    "my family wants money",
    "I am scared to start",
    "I failed at business",
    "motivate me",
    "I need capital",
    "should I take a loan?",
    "give me a business idea",
    "what is caustic soda?",
    "what is cash flow?",
    "what is profit margin?",
    "what is break-even?",
    "what is a KPI?",
    "what is BSF farming?",
    "what is shea butter?",
    "how do I make soap?",
    "how do I start beekeeping?",
    "how do I start cricket farming?",
    "tell me about mushroom farming",
    "how do I make cooking oil?",
    "how do I grow tomatoes?",
    "how do I raise chicken?",
    "tell me a joke",
    "tell me a fact",
    "share a bible verse",
    "tell me something funny",
    "did you know something?",
    "how do I manage debt?",
    "how do I keep customers coming back?",
    "how do I sell on WhatsApp?",
    "how do I handle complaints?",
    "how do I find my first customer?",
    "should I expand my business?",
    "how do I choose a location?",
    "should I take a business partner?",
    "how do I set goals?",
    "I feel tired today",
    "how do I become rich?",
    "how do I build trust?",
    "how do I improve quality?",
    "how do I negotiate a price?",
    "where does my money go?",
    "what is customer loyalty?",
    "what is customer lifetime value?",
    "what is working capital?",
    "what is word of mouth?",
    "what is a value proposition?",
    "how do I make liquid soap?",
    "how do I start a bakery?",
    "how do I rear rabbits?",
    "how do I make peanut butter?",
    "how do I start fish farming?"
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
}'''

start_sug = html.find("function exRenderSuggestions(")
if start_sug != -1:
    open_pos = html.find("{", start_sug)
    depth = 0; i = open_pos; end_sug = -1
    while i < len(html):
        ch = html[i]
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: end_sug = i + 1; break
        i += 1
    if end_sug != -1:
        html = html[:start_sug] + NEW_SUGS + html[end_sug:]
        print("5. exRenderSuggestions: OK")
    else:
        print("5. WARN closing brace")
else:
    print("5. WARN not found")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Expert v5 installed.")
