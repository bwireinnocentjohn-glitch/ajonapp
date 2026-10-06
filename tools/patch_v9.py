import io, sys, os, re

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ---- Find old brain start ----
markers = [
    'var BRAIN_STATE_KEY = "ajon_chat_v8"',
    'var BRAIN_STATE_KEY = "ajon_chat_v5"',
    'var BRAIN_STATE_KEY = "ajon_brain_state',
    'var BRAIN_PRINCIPLES = [',
    'var CHAT_TOPICS',
    'var TOPIC_DATA',
    'var RAW_TOPICS',
    'var BRAIN = {'
]
start = -1
for m in markers:
    i = html.find(m)
    if i != -1:
        if start == -1 or i < start: start = i
if start == -1:
    print("ERROR: no old brain marker"); sys.exit(1)

body = html.rfind('</body>')
end = html.rfind('</script>', start, body)
if end == -1:
    print("ERROR: </script> not found"); sys.exit(1)
print("Removing old brain: " + str(end - start) + " bytes")

NEW_BRAIN = r'''

/* =====================================================================
   AJON CHAT v9 — Mr Ajon & Pesie, clean linked Q&A
   ===================================================================== */

var BRAIN_STATE_KEY = "ajon_chat_v9";
var BRAIN = {
  chatCount: 0, level: 1, capital: 86000, location: "Busia",
  isRunning: false, isPaused: true, messages: [],
  currentTopicId: null, lastTopics: [], lastPrinciple: null,
  pendingBiz: null, bizIdx: {}, rotIdx: {}, lastMode: "question"
};
var assistSoundOn = true;
var chatTimer = null;
var chatToken = 0;
var audioCtx = null;

/* ---------- Sound (kept ON, beep per message) ---------- */
function playNotify() {
  if (!assistSoundOn) return;
  try {
    if (!audioCtx) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    }
    if (!audioCtx) return;
    if (audioCtx.state === "suspended") audioCtx.resume();
    var now = audioCtx.currentTime;
    var o1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
    o1.connect(g1); g1.connect(audioCtx.destination);
    o1.type = "sine";
    o1.frequency.setValueAtTime(880, now);
    g1.gain.setValueAtTime(0.0001, now);
    g1.gain.exponentialRampToValueAtTime(0.42, now + 0.012);
    g1.gain.exponentialRampToValueAtTime(0.0001, now + 0.11);
    o1.start(now); o1.stop(now + 0.13);
    var o2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
    o2.connect(g2); g2.connect(audioCtx.destination);
    o2.type = "sine";
    o2.frequency.setValueAtTime(1245, now + 0.09);
    g2.gain.setValueAtTime(0.0001, now + 0.09);
    g2.gain.exponentialRampToValueAtTime(0.42, now + 0.10);
    g2.gain.exponentialRampToValueAtTime(0.0001, now + 0.23);
    o2.start(now + 0.09); o2.stop(now + 0.26);
  } catch (e) {}
}
function playNotifySound() { playNotify(); }
function resumeAudio() {
  try {
    if (!audioCtx) {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    }
    if (audioCtx && audioCtx.state === "suspended") audioCtx.resume();
  } catch (e) {}
}
try {
  ["touchstart","touchend","click","keydown"].forEach(function(ev){
    document.addEventListener(ev, resumeAudio, true);
  });
} catch (e) {}

/* ---------- Data ---------- */
var EMOJIS = {
  scared:"\uD83D\uDE30", hopeful:"\uD83D\uDE42", tired:"\uD83D\uDE29",
  worried:"\uD83D\uDE1F", determined:"\uD83D\uDCAA", proud:"\uD83D\uDE0A",
  curious:"\uD83E\uDD14", thankful:"\uD83D\uDE4F"
};
var EMOTION_KEYS = Object.keys(EMOJIS);

var MR_AJON_OPENERS = [
  "My child, sit down.",
  "Listen carefully.",
  "Good question.",
  "I hear you. Now hear me.",
  "Let me tell you the truth."
];
var MR_AJON_CLOSERS = [
  "What will you finish before 6pm?",
  "Tell me tomorrow what you did.",
  "Ask yourself tonight: did I do it?",
  "Count tomorrow. Tell me the number.",
  "Now go and do it today."
];
var PESIE_ACKS = [
  "Oh! I see now. \uD83D\uDE42",
  "Eeeh Mr Ajon, I understand. \uD83D\uDE4F",
  "Yes, now I get it! \uD83D\uDE0A",
  "Wooow, thank you Mr Ajon. \uD83D\uDE4C",
  "Okay, I see the point. \uD83D\uDC4D",
  "Eeh! I never thought of it like that. \uD83D\uDE2E",
  "Mr Ajon, this makes sense now. \uD83D\uDE42",
  "Aha, I understand clearly. \uD83D\uDC4C",
  "Mr Ajon, you have opened my eyes. \uD83D\uDC40",
  "Okay Mr Ajon, I hear you well. \uD83D\uDE4F"
];
var PESIE_WONDERS = [
  "Mr Ajon, I wonder why...",
  "Hmm, Mr Ajon...",
  "I keep thinking about this...",
  "Mr Ajon, something is on my mind.",
  "Wait, Mr Ajon, one more thing..."
];
var MR_AJON_CONFIRMS = [
  "That's it, my child.",
  "Exactly.",
  "Yes. Now go and do it.",
  "You heard it. Now act.",
  "Correct. Do not forget it.",
  "Good. Your turn to move.",
  "Now you know. Now you do.",
  "Go and practise it today.",
  "That is the way.",
  "Remember it. Then use it."
];
var PROVERBS = [
  "Slow is smooth. Smooth is fast.",
  "Start ugly. Refine daily.",
  "Small deeds done beat big plans.",
  "The market rewards patience.",
  "Discipline is born of routine.",
  "Fail. Learn. Try again.",
  "Consistency beats talent weekly.",
  "Reputation travels faster than boda.",
  "One well gives water. Ten holes give dust.",
  "Show up daily. That alone wins."
];

/* ---------- 100 linked topics ---------- */
/* Format: [id, question, answer, principle, action, next1|next2] */
var RAW_TOPICS = [
["fear","I am scared to start. 😰","Root is fear of small dreams.|Start small, then grow.","Fear is a tax you pay for dreaming small.","Do one small thing today.","capital|first_step"],
["capital","I have only {cap} UGX. 😟","Root is big dream, small wallet.|That is normal at start.","Learn to grow 50k before 500k.","Buy smallest starter kit today.","pricing|records"],
["first_step","What is my first step? 🤔","Root is wanting certainty before action.|Just start.","The first step is the only one you control.","Do one small action in 30 minutes.","pricing|records"],
["pricing","What price should I charge? 💰","Root is pricing from fear, not value.|Cost plus margin is price.","Fair price beats cheap price.","Calculate full cost today.","value|customer_care"],
["value","How do I show value? 🌟","Root is selling product not outcome.|Show the result.","People buy feelings, not features.","Show one outcome today.","brand|retention"],
["customer_care","Customers complain a lot. 😞","Root is serving without love.|Complaints are gifts.","Service is the product.","Apologise fast, correct faster.","retention|trust"],
["retention","Customers don't come back. 😕","Root is no reason to return.|Give a reason.","Ten loyal beat a hundred random.","Call 5 old customers today.","trust|word_of_mouth"],
["trust","Nobody trusts me yet. 😔","Root is no system yet.|Consistency builds trust.","Money follows trust.","Deliver one order 1 hour early.","brand|records"],
["brand","My brand is too small. 📛","Root is no clear feeling about you.|Pick one feeling.","Reputation is your real capital.","Ask 5 customers what they feel.","word_of_mouth|retention"],
["word_of_mouth","No money for ads. 📢","Root is current customers aren't talking.|Deliver unforgettable service.","Word of mouth is the cheapest ad.","Ask best customer for 1 referral.","retention|brand"],
["records","I don't keep records. 📓","Root is trusting head over book.|Buy a small book today.","Write it down. Memory is a liar.","Write sales, cost, cash left today.","cash_flow|savings"],
["cash_flow","Money keeps vanishing. 💸","Root is money leaves faster than enters.|Track every shilling.","Cash in hand beats credit.","Write every sale and cost today.","savings|unit_economics"],
["unit_economics","Profit is too small. 📉","Root is one unit loses money.|Fix the unit first.","Fix unit before volume.","Calculate cost of one product today.","savings|debt"],
["savings","I never save. 🐖","Root is every shilling finds a mouth.|Save before spending.","Save before you spend.","Take 10% out the moment you sell.","debt|emergency"],
["emergency","No backup money. 🚨","Root is no cushion for hard days.|Build one month of savings.","Save in harvest for dry months.","Save 500 UGX daily for 30 days.","savings|debt"],
["debt","Should I take a loan? 💳","Root is why the debt is taken.|Debt for stock, not shoes.","Debt for growth is a bridge.","Write what the loan is for today.","savings|records"],
["family","Family keeps asking for money. 👨‍👩‍👧","Root is family has needs, no plan.|Give a plan, not just cash.","Pay yourself first. Then help.","Open separate family pocket today.","savings|discipline"],
["discipline","I have no routine. 🥱","Root is no routine protecting discipline.|A schedule is a promise.","Discipline is the only partner that stays.","Set fixed wake-up time 30 days.","focus|morning_routine"],
["morning_routine","I waste my mornings. ☀️","Root is letting the day start you.|You start the day.","You start the day. The day doesn't start you.","Plan 3 tasks tonight for tomorrow.","focus|records"],
["focus","I want five businesses. 🎯","Root is too many good ones, no decision.|One deep well beats ten holes.","One deep well beats ten holes.","Circle ONE idea. Say no to two for 90 days.","discipline|hiring"],
["competition","Someone copied my shop. 🏪","Root is you got comfortable.|Study them, don't copy.","Do not copy. Study.","Talk to 5 old customers today.","value|brand"],
["supplier","My supplier raised price. 📦","Root is only one source makes you weak.|Two sources turn supplier into partner.","Two sources turn supplier into partner.","Find a second supplier this week.","records|savings"],
["hiring","Should I hire? 👨‍🔧","Root is wanting hands without system.|Systems first, people second.","Systems first, people second.","Write the job in 5 steps today.","expansion|records"],
["expansion","Should I open another branch? 🏬","Root is scale, not stability.|Stable small first.","One shop done well beats ten done badly.","Check if first shop is leaking today.","hiring|savings"],
["teaching","Can I teach my cousin? 👨‍🎓","Root is you teach what you practise.|Teaching sharpens you.","Teaching forces you to become what you teach.","Teach one lesson this week.","brand|community"],
["community","How do I help my community? 🤝","Root is quiet help beats loud help.|Teach one, multiply forever.","Your neighbour's success is proof, not threat.","Teach one person one thing today.","teaching|legacy"],
["legacy","What am I building for? 🏛️","Root is what outlives you is what you build.|Legacy is service.","Legacy is service, not riches.","Write your one-sentence mission tonight.","teaching|brand"],
["quality","How do I keep quality? ⭐","Root is no routine protects quality.|Write 5 quality checks.","Quality is a habit, not an act.","Do quality checks every sale.","consistency|reputation"],
["consistency","I am not consistent. 🔄","Root is no schedule. A schedule is a promise.|Show up daily.","Show up daily. That beats 90%.","Pick one fixed daily action tonight.","discipline|routine"],
["differentiation","I look same as others. 🎭","Root is no named difference.|Name one thing only you do.","Differentiate or die cheap.","Name one unique thing today.","positioning|brand"],
["positioning","Which market should I serve? 🎪","Root is trying to serve everyone.|Cheap OR premium. Not both.","Confused positioning sells nothing.","Pick cheap OR premium today.","value|differentiation"],
["packaging","My packaging is plain. 🎁","Root is wrapper not matching value.|Improve one package.","Change the wrapper, change the price.","Improve one package this week.","brand|value"],
["labelling","Should I label products? 🏷️","Root is no name recognition.|Print 20 labels.","Labels are silent salesmen.","Print 20 labels this week.","brand|packaging"],
["delivery","Delivery is a headache. 🛵","Root is no clear delivery promise.|Promise slow, deliver fast.","Promise slow, deliver fast.","Set delivery window today.","trust|customer_care"],
["negotiation","How do I negotiate? 🤝","Root is no walk-away point.|Set your lowest price.","Never negotiate on price alone.","Set lowest price tonight.","pricing|value"],
["credit","Should I sell on credit? 📝","Root is no credit rules.|Max 2 people, 50% up front.","Credit given slowly is credit never lost.","Write credit rules today.","cash_flow|records"],
["bulk_buying","Should I buy in bulk? 📦","Root is bulk without turnover math.|Only what sells in 30 days.","Buy in bulk or buy in pain.","Calculate turnover for one product.","cash_flow|unit_economics"],
["transport","Transport eats my profit. 🚚","Root is no cost per trip.|Consolidate trips.","Cost per delivery first.","Calculate cost per delivery today.","supplier|unit_economics"],
["theft","Stock keeps disappearing. 🕵️","Root is no counting system.|Count daily.","Count daily. Numbers reveal everything.","Count stock morning and night.","records|staff_loyalty"],
["licenses","Do I need a license? 📜","Root is fear of paperwork.|Get one at a time.","A licensed business sleeps well.","Ask local office today.","trust|legacy"],
["taxes","Should I pay tax? 💼","Root is no tax planning.|Save 10% of sales.","Tax is the price of a market.","Save 10% of sales monthly.","records|savings"],
["location","Is my location good? 📍","Root is location by rent, not traffic.|Count foot traffic.","Location is a business decision.","Count foot traffic tomorrow morning.","foot_traffic|rent"],
["foot_traffic","How many people pass? 👣","Root is no traffic numbers.|Count for 1 hour.","Foot traffic is free advertising.","Count passers-by for 1 hour today.","location|records"],
["rent","My rent is too high. 🏠","Root is no written agreement.|Ask for fixed rent.","Put every agreement in writing.","Ask landlord for 6-month fixed rent.","location|records"],
["advertisement","How do I advertise? 📣","Root is advertising where customers aren't.|One clear message.","One message repeated beats many once.","Pick one message today.","brand|word_of_mouth"],
["social_media","Should I use social media? 📱","Root is posting randomly.|One platform done well.","One platform done well beats five done badly.","Pick one platform tonight.","brand|word_of_mouth"],
["whatsapp_selling","Can I sell on WhatsApp? 💬","Root is no professional profile.|Add business name and photo.","Your WhatsApp is your shop window.","Update profile today.","social_media|brand"],
["online_shop","Should I open online shop? 🛒","Root is trying tech before product.|Take 10 product photos.","Sell the same online and offline.","Take 10 clear photos today.","whatsapp_selling|delivery"],
["seasons","Some months are slow. 📅","Root is no savings from peak season.|Save 20% of peak profit.","Save in harvest for dry season.","Save 20% of peak profit.","savings|emergency"],
["rain_season","Rain kills my sales. 🌧️","Root is no rain plan.|Buy a rain cover.","Plan for rain like it's certain.","Buy a rain cover today.","seasons|savings"],
["dry_season","Dry season is tough. 🌵","Root is no dry-season product.|Add dry-season product.","Every season has a market.","Add one dry-season product today.","seasons|savings"],
["festive_season","Should I stock for Christmas? 🎄","Root is buying on emotion.|Buy 20% more, not 200%.","Buy 20% more, not 200% more.","Check last year's festive sales tonight.","seasons|records"],
["school_season","School season is busy. 🎒","Root is no school calendar plan.|Talk to school heads.","Align with the school calendar.","Talk to 2 school heads this week.","seasons|bulk_buying"],
["market_days","Market days are best. 🛒","Root is no prep for market days.|Stock extra day before market.","Prepare for market day like a festival.","Start 1 hour early on market day.","seasons|records"],
["profit_margin","My margin is small. 📊","Root is price low or cost high.|Aim for 30% margin.","Aim for 30% margin minimum.","Calculate margin on 3 products today.","pricing|unit_economics"],
["break_even","What is break-even? ⚖️","Root is not knowing your floor.|Know your break-even by heart.","Know your break-even by heart.","Calculate monthly fixed cost tonight.","unit_economics|profit_margin"],
["fixed_cost","Fixed costs hurt. 💼","Root is fixed costs not matched to sales.|Cut one this month.","Every fixed cost is a bet.","List fixed costs today.","break_even|savings"],
["variable_cost","Materials cost too much. 🧾","Root is no cost per unit.|Find 2 cheaper suppliers.","Cut cost without cutting quality.","Find 2 cheaper suppliers today.","supplier|bulk_buying"],
["inventory","How much stock to keep? 📦","Root is no min/max rule.|Keep 2 weeks of fast sellers.","Fast turnover beats high margin.","Set min/max for top 5 products.","stock_counting|records"],
["turnover","Money stuck in stock. 🔒","Root is slow sellers blocking cash.|Calculate turnover.","Fast turnover beats high margin.","Calculate turnover for one product.","inventory|dead_stock"],
["dead_stock","Some stock never sells. 💀","Root is holding hope on dead items.|Discount 30%.","Dead stock is dead money.","Discount 30% off dead items today.","cash_flow|inventory"],
["stock_counting","Do I need to count stock? 🔢","Root is trusting memory over count.|Count at 9pm.","Count daily. Numbers don't lie.","Count at 9pm tonight.","records|theft"],
["staff_loyalty","How do I keep good workers? 🧑‍🏭","Root is pay below market.|Pay fairly, train deeply.","Pay fairly. Train deeply. Respect always.","Raise pay for one worker this month.","salary|hiring"],
["salary","What should I pay? 💵","Root is no clear job description.|Write the job in 5 lines.","Pay for the job, not the person.","Write the job in 5 lines today.","hiring|staff_loyalty"],
["bonus","Should I give bonus? 🎉","Root is bonus without clear targets.|Bonus for extra, not base.","Fix base pay. Then bonus.","Write 3 clear bonus targets today.","salary|staff_loyalty"],
["motivation","I lose motivation. 😔","Root is no clear why.|Write your why.","Motivation is boda. Discipline is tarmac.","Write your why on the wall today.","discipline|focus"],
["team","Should I build a team? 👥","Root is no system before team.|Write 3 roles you need.","Systems first, team second.","Write 3 roles you need tonight.","hiring|records"],
["partnership","Should I partner? 🤝","Root is partnership without written terms.|Write terms on paper.","Partners need contracts, not just trust.","Write terms on one page today.","contract|cofounder"],
["cofounder","Should I get a co-founder? 👬","Root is no clear skill complement.|Choose for skill, not friendship.","Choose partner for skill, not friendship.","List skills you lack today.","partnership|equity"],
["contract","Should I sign contract? 📄","Root is trusting words over paper.|Write it down.","A written agreement protects both.","Write one-page contract today.","partnership|trust"],
["business_plan","Do I need a plan? 📝","Root is confusion between plan and paper.|Write 90-day plan.","A plan is a promise in numbers.","Write 90-day plan on one page tonight.","goal_setting|records"],
["goal_setting","How do I set goals? 🎯","Root is vague goals.|Write 1 clear goal.","Vague goals produce vague results.","Write one goal for this week tonight.","business_plan|routine"],
["vision","What is my vision? 🔭","Root is no 5-year picture.|Write 5-year vision.","Write your 5-year vision on one page.","Write 5-year vision tonight.","mission|legacy"],
["time_management","I don't have time. ⏰","Root is no priority list.|Do important before urgent.","Do the important before the urgent.","Write tomorrow's top 3 tasks tonight.","priority|routine"],
["priority","What should I do first? 🥇","Root is no clear ranking.|Rank by money impact.","Rank by money impact, not noise.","Rank tasks tonight, do top 3.","time_management|focus"],
["patience","How long until profit? 🕰️","Root is expecting fast returns.|Commit to 90 days.","Real wealth takes years.","Commit to 90 days without quitting.","discipline|long_term"],
["long_term","How do I think long-term? 🌳","Root is survival mode blocking vision.|Write 1-year goal.","Small habits compound.","Write 1-year goal tonight.","vision|savings"],
["hard_work","Is hard work enough? 💪","Root is working IN not ON.|Write 3 things only you can do.","Work hard AND smart.","Write 3 things only you can do today.","smart_work|systems"],
["smart_work","How do I work smart? 🧠","Root is no system.|Write one process.","Systems beat sweat.","Write one process on paper today.","systems|routine"],
["systems","What is a system? 🔧","Root is reliance on memory.|Write 5 steps for one task.","Write it down. Repeat it.","Write 5 steps for one task today.","routine|process"],
["routine","Do I need a routine? 📆","Root is no anchor activities.|Set 3 morning steps.","A routine is a promise to yourself.","Set 3 morning steps tonight.","discipline|systems"],
["network","How do I build network? 🌐","Root is no active networking.|Help 1 person today.","Give first. Network follows.","Help one person today, free.","mentor|community"],
["mentor","Do I need a mentor? 🧓","Root is waiting for perfect mentor.|Pick 3 questions to ask one.","Mentors come to those who act.","Pick 3 questions tonight.","network|learning"],
["learning","How do I keep learning? 📚","Root is no daily input.|Learn 1 thing daily.","Learn 1 thing. Apply 1 thing.","Read 10 pages today.","reading|practice"],
["reading","Should I read books? 📖","Root is reading without application.|Read to apply, not finish.","Read to apply, not to finish.","Read 10 pages tonight.","learning|mentor"],
["practice","Why do I forget? 🧪","Root is learning without doing.|Practise daily.","Practice turns knowledge into skill.","Practise one skill 15 minutes today.","learning|discipline"],
["failure","I failed at business. 💔","Root is treating failure as end.|Write 3 lessons.","Failure is the school that never closes.","Write 3 lessons from the failure tonight.","recovery|resilience"],
["recovery","How do I recover? 🌱","Root is rebuilding too fast.|Start small.","Start small. Start today.","Pick one small action tonight.","savings|resilience"],
["resilience","How do I keep going? 🌊","Root is no small wins remembered.|Write 3 wins.","Fall seven times, stand up eight.","Write 3 wins from this month tonight.","failure|motivation"],
["courage","I am afraid to try. 🦁","Root is waiting for fear to leave.|Do one brave thing.","Courage is acting with fear.","Do one small brave thing today.","fear|first_step"],
["humility","How do I stay humble? 🙏","Root is comparing downward.|Say thank you to 3 people.","Humility opens doors money cannot.","Say thank you to 3 people today.","gratitude|legacy"],
["honesty","Is honesty profitable? ✅","Root is short-term gain vs long-term trust.|Write your values.","Honesty builds what lies destroy.","Write your values on paper tonight.","trust|reputation"],
["kindness","Does kindness sell? 💚","Root is confusion between kindness and weakness.|Do one kind thing.","Kindness costs nothing, pays everything.","Do one kind thing for a customer today.","customer_care|reputation"],
["gratitude","How do I stay grateful? 🌻","Root is comparison to others.|Write 3 things you're grateful for.","Gratitude turns what you have into enough.","Write 3 things tonight.","humility|joy"],
["joy","Where is joy in business? 😊","Root is only chasing, never celebrating.|Celebrate one small win.","Joy is in the small things.","Celebrate one small win today.","gratitude|celebration"],
["celebration","Should I celebrate? 🎊","Root is only chasing next goal.|Celebrate tonight.","Celebrate wins. They fuel the next mountain.","Celebrate one win tonight.","joy|gratitude"],
["peace","I feel stressed. 🧘","Root is no boundaries.|Set 1 hour without business.","Your peace is worth more than any argument.","Set 1 hour daily without business.","rest|health"],
["anger","I get angry easily. 😠","Root is no pause before reaction.|Pause 3 seconds.","Raise your voice, lose the sale.","Pause 3 seconds before speaking today.","peace|discipline"],
["envy","I envy other businesses. 😒","Root is comparing your chapter 1 to their chapter 20.|Focus on your own growth.","Your neighbour's success is proof, not threat.","Write 3 wins you had this month tonight.","focus|gratitude"],
["anxiety","I feel anxious daily. 😰","Root is no plan for worst case.|Write worst-case plan.","Prepare for worst. Enjoy the best.","Write worst-case plan tonight.","emergency|peace"],
["health","How do I stay healthy? 🏃","Root is health last priority.|Walk 20 minutes today.","A sick body builds no empire.","Walk 20 minutes today.","energy|rest"],
["rest","How do I rest? 😴","Root is confusing rest with laziness.|Block 4 hours this Sunday.","Rest is strategy, not laziness.","Block 4 hours this Sunday for rest.","health|peace"],
["sleep","I don't sleep enough. 🛌","Root is phone before bed.|Phone off at 10pm.","Sleep is when the body repairs.","Phone off at 10pm tonight.","health|rest"],
["review","How often should I review? 🔍","Root is only working, not measuring.|Review weekly.","Review weekly, adjust monthly.","Review one week's numbers tonight.","records|routine"],
["feedback","Should I ask for feedback? 💬","Root is fear of criticism.|Ask 3 customers one question.","Feedback is food, not fire.","Ask 3 customers one question today.","review|improvement"],
["improvement","How do I improve? 📈","Root is no clear metric.|Pick one thing to improve.","1% better every day is 37x per year.","Pick one thing to improve this week.","practice|learning"],
["change","Things keep changing. 🔄","Root is resisting change.|Learn one new skill.","Change or be changed.","Learn one new skill this month.","adaptation|innovation"],
["problem_solving","How do I solve problems? 🧩","Root is no clear problem statement.|Solve one problem well.","Solve one problem well, then the next.","Write the problem in one line tonight.","focus|systems"],
["decision_making","How do I decide? 🤔","Root is waiting for perfect choice.|Set a 24-hour deadline.","A decision today beats a perfect one in a week.","Set a 24-hour deadline for one decision.","focus|discipline"],
["risk","Should I take risk? 🎲","Root is no small risk testing.|Bet small, learn fast.","Bet small. Learn fast. Scale up.","Set max loss you can handle tonight.","backup_plan|insurance"],
["backup_plan","What if things fail? 🛟","Root is only one revenue source.|Find one backup.","Every business needs a second source.","Find one backup supplier this month.","emergency|risk"],
["crisis","How do I handle crisis? 🚨","Root is no crisis protocol.|Write a crisis plan.","Plan in peace for war.","Write a crisis plan tonight.","emergency|risk"],
["reputation","How do I build reputation? 🌟","Root is no consistent quality.|Deliver one extra value.","Reputation is built in drops, lost in buckets.","Deliver one extra value today.","trust|brand"],
["purpose","What is my purpose? 🧭","Root is no clear why.|Write your purpose.","Purpose is being useful to others.","Write your purpose in one line tonight.","mission|legacy"],
["hope","I feel hopeless. 🌤️","Root is only looking at today.|Write one hope.","Hope is not a plan. But it fuels one.","Write one hope for this year tonight.","purpose|faith"],
["faith","How does faith fit business? 🕊️","Root is faith as Sunday-only.|Pray before opening.","Work like the market depends on you. Pray like it depends on God.","Pray before opening today.","purpose|hope"]
];

var TOPICS = {};
var TOPIC_IDS = [];
for (var _ti = 0; _ti < RAW_TOPICS.length; _ti++) {
  var r = RAW_TOPICS[_ti];
  TOPICS[r[0]] = {
    id: r[0],
    q: r[1],
    a: r[2].split("|"),
    p: r[3],
    act: r[4],
    next: r[5].split("|")
  };
  TOPIC_IDS.push(r[0]);
}

/* ---------- Topic-linked business keywords ---------- */
var TOPIC_BIZ_KEYWORDS = {
  food:["food","drink","bake","cook","juice","candy","oil"],
  pricing:["retail","premium","shop"],
  capital:["small","home","budget","village"],
  fear:["beginner","small","starter"],
  first_step:["home","small","budget"],
  value:["premium","quality"],
  customer_care:["retail","service","shop"],
  retention:["retail","premium","brand"],
  trust:["retail","quality"],
  brand:["premium","brand","export"],
  word_of_mouth:["retail","village","urban"],
  records:["retail","small"],
  cash_flow:["wholesale","bulk","commercial"],
  unit_economics:["bulk","commercial","wholesale"],
  savings:["home","small"],
  emergency:["home","small"],
  debt:["commercial","bulk","medium"],
  family:["home","village","small"],
  discipline:["home","small","medium"],
  morning_routine:["home","retail","small"],
  focus:["premium","niche","medium"],
  competition:["premium","niche","urban"],
  supplier:["wholesale","bulk","commercial"],
  hiring:["medium","commercial","urban"],
  expansion:["commercial","urban","wholesale"],
  teaching:["community","village","small"],
  community:["community","village"],
  legacy:["premium","brand","export"]
};

/* ---------- Utility ---------- */
function pickRot(arr, key) {
  if (!arr || !arr.length) return "";
  if (BRAIN.rotIdx[key] === undefined) BRAIN.rotIdx[key] = Math.floor(Math.random() * arr.length);
  var v = arr[BRAIN.rotIdx[key] % arr.length];
  BRAIN.rotIdx[key] = (BRAIN.rotIdx[key] + 1) % arr.length;
  return v;
}
function fillT(t) {
  return String(t || "")
    .replace(/\{cap\}/g, fmt(BRAIN.capital))
    .replace(/\{loc\}/g, BRAIN.location);
}
function chunkMsg(text, maxLen) {
  maxLen = maxLen || 55;
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
function pickBusinessForTopic(topicId) {
  if (typeof ALL_BUSINESSES === "undefined" || !ALL_BUSINESSES.length) return null;
  var keywords = TOPIC_BIZ_KEYWORDS[topicId] || [];
  var candidates = [];
  for (var i = 0; i < ALL_BUSINESSES.length; i++) {
    var b = ALL_BUSINESSES[i];
    var hay = ((b.t || "") + " " + (b.tagline || "")).toLowerCase();
    for (var k = 0; k < keywords.length; k++) {
      if (hay.indexOf(keywords[k]) > -1) { candidates.push(b); break; }
    }
  }
  if (!candidates.length) candidates = ALL_BUSINESSES;
  var key = "biz_" + topicId;
  if (BRAIN.bizIdx[key] === undefined) BRAIN.bizIdx[key] = Math.floor(Math.random() * candidates.length);
  var b2 = candidates[BRAIN.bizIdx[key] % candidates.length];
  BRAIN.bizIdx[key] = (BRAIN.bizIdx[key] + 1) % candidates.length;
  return b2;
}
function shortStep(s, n) {
  if (!s) return "";
  s = String(s).replace(/\*\*/g, "").trim();
  n = n || 48;
  if (s.length <= n) return s;
  var w = s.split(/\s+/);
  var cur = "";
  for (var i = 0; i < w.length; i++) {
    if (!cur) { cur = w[i]; continue; }
    if ((cur + " " + w[i]).length <= n) cur += " " + w[i];
    else break;
  }
  return cur + "...";
}

/* ---------- Pesie turn: 1 bubble ---------- */
function buildPesieTurn() {
  var tid = BRAIN.currentTopicId;
  if (!tid) {
    tid = TOPIC_IDS[Math.floor(Math.random() * TOPIC_IDS.length)];
    BRAIN.currentTopicId = tid;
  }
  var t = TOPICS[tid];
  if (!t) { t = TOPICS[TOPIC_IDS[0]]; BRAIN.currentTopicId = t.id; }

  var roll = Math.random();
  var out = [];

  if (BRAIN.lastMode === "question" && roll < 0.30) {
    /* Pesie acknowledges or wonders */
    BRAIN.lastMode = (roll < 0.18) ? "ack" : "wonder";
    out.push(pickRot(PESIE_ACKS, "ack"));
    return out;
  }
  if (BRAIN.lastMode === "ack" && roll < 0.20) {
    BRAIN.lastMode = "ack";
    out.push(pickRot(PESIE_ACKS, "ack"));
    return out;
  }

  /* Default: Pesie asks ONE question */
  BRAIN.lastMode = "question";
  var q = fillT(t.q);
  /* Occasionally prepend context */
  if (BRAIN.lastPrinciple && roll > 0.85) {
    q = "You said: " + BRAIN.lastPrinciple + " " + q;
  }
  out.push(q);
  return out;
}

/* ---------- Mr Ajon turn: 2-5 bubbles ---------- */
function buildMrAjonTurn() {
  var tid = BRAIN.currentTopicId || TOPIC_IDS[0];
  var t = TOPICS[tid] || TOPICS[TOPIC_IDS[0]];
  var out = [];

  if (BRAIN.lastMode === "ack") {
    out.push(pickRot(MR_AJON_CONFIRMS, "conf"));
    if (Math.random() < 0.5) {
      out.push("Remember: " + t.p);
    }
    return out;
  }

  if (BRAIN.lastMode === "wonder") {
    out.push(pickRot(MR_AJON_OPENERS, "op"));
    out.push(fillT(pickRot(t.a, "a_" + tid)));
    out.push("Principle: " + t.p);
    out.push(fillT(t.act));
    return out;
  }

  /* Default: question → 3-5 bubbles */
  out.push(pickRot(MR_AJON_OPENERS, "op"));
  var a1 = fillT(pickRot(t.a, "a_" + tid));
  out.push(a1);
  var a2 = fillT(pickRot(t.a, "a2_" + tid));
  if (a2 && a2 !== a1) out.push(a2);
  out.push("Principle: " + t.p);
  out.push(fillT(t.act));

  /* Business every 4th question */
  if (BRAIN.chatCount % 4 === 2 || BRAIN.pendingBiz) {
    var b = BRAIN.pendingBiz || pickBusinessForTopic(tid);
    BRAIN.pendingBiz = null;
    if (b) {
      out.push("Idea: " + b.t + " in " + (b.location || "your area") + ".");
      out.push("Start " + fmt(b.cost) + " UGX. Profit " + fmt(b.profit) + ".");
      if (b.steps && b.steps[0]) out.push("S1: " + shortStep(b.steps[0], 46));
    }
  }

  /* Cap at 5 */
  if (out.length > 5) out = out.slice(0, 5);
  if (out.length < 2) out.push(pickRot(MR_AJON_CLOSERS, "cl"));
  else if (out.length === 4) out.push(pickRot(MR_AJON_CLOSERS, "cl"));
  return out;
}

/* ---------- Next topic ---------- */
function nextTopicV9() {
  var tid = BRAIN.currentTopicId || TOPIC_IDS[0];
  var t = TOPICS[tid];
  if (!t || !t.next || !t.next.length) {
    return TOPIC_IDS[Math.floor(Math.random() * TOPIC_IDS.length)];
  }
  var recent = BRAIN.lastTopics || [];
  var fresh = t.next.filter(function (x) { return recent.indexOf(x) === -1 && TOPICS[x]; });
  if (!fresh.length) fresh = t.next.filter(function (x) { return TOPICS[x]; });
  if (!fresh.length) return TOPIC_IDS[Math.floor(Math.random() * TOPIC_IDS.length)];
  var nxt = fresh[Math.floor(Math.random() * fresh.length)];
  BRAIN.lastTopics = (recent.concat([nxt])).slice(-10);
  return nxt;
}

/* ---------- DOM helpers ---------- */
function ajon_makeRow(speaker, text, withCursor) {
  var isAjon = speaker === "ajon";
  var name = isAjon ? "Mr Ajon" : "Pesie";
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
    div.querySelector(".bubble").innerHTML = escapeHTML(text);
  }
  return div;
}
function ajon_showTyping(speaker) {
  var box = byId("assistMsgs");
  if (!box) return null;
  var isAjon = speaker === "ajon";
  var name = isAjon ? "Mr Ajon" : "Pesie";
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
      var parts = chunkMsg(bubbles[i], 55);
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
      var speed = 90 + Math.random() * 40;
      function step() {
        if (token !== chatToken || !BRAIN.isRunning) {
          bubble.classList.remove("typing-cursor");
          return resolve(false);
        }
        if (i >= text.length) {
          bubble.classList.remove("typing-cursor");
          playNotify();
          idx++;
          setTimeout(typeOne, 900 + Math.random() * 400);
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
function ajon_sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

/* ---------- State ---------- */
function loadBrainState() {
  try {
    var raw = localStorage.getItem(BRAIN_STATE_KEY);
    if (raw) {
      var s = JSON.parse(raw);
      BRAIN.chatCount = s.chatCount || 0;
      BRAIN.capital = s.capital || 86000;
      BRAIN.level = s.level || 1;
      BRAIN.messages = s.messages || [];
      BRAIN.currentTopicId = s.currentTopicId || null;
      BRAIN.lastTopics = s.lastTopics || [];
      BRAIN.lastPrinciple = s.lastPrinciple || null;
      BRAIN.lastMode = s.lastMode || "question";
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
      messages: BRAIN.messages.slice(-40),
      currentTopicId: BRAIN.currentTopicId,
      lastTopics: BRAIN.lastTopics.slice(-10),
      lastPrinciple: BRAIN.lastPrinciple,
      lastMode: BRAIN.lastMode
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
  resumeAudio();
  var box = byId("assistMsgs");
  if (!box) return;
  if (!hasFullAccess()) {
    box.innerHTML = '<div class="coming-soon"><span class="bigicon">\uD83D\uDD12</span><h3>Assistant Locked</h3><p>Unlock to watch Mr Ajon teach Pesie.</p></div>';
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

  /* 1. Pesie typing dots */
  var t1 = ajon_showTyping("pasie");
  await ajon_sleep(1400 + Math.random() * 800);
  if (token !== chatToken || !BRAIN.isRunning) { if (t1 && t1.parentNode) t1.parentNode.removeChild(t1); return; }
  if (t1 && t1.parentNode) t1.parentNode.removeChild(t1);

  /* 2. Pesie sends 1 bubble */
  var pesieBubbles = buildPesieTurn();
  var ok1 = await ajon_send("pasie", pesieBubbles, token);
  if (!ok1) return;
  BRAIN.messages.push({ s: "pasie", t: pesieBubbles.join("\n"), ts: Date.now() });

  /* 3. Wait */
  await ajon_sleep(900);
  if (token !== chatToken || !BRAIN.isRunning) return;

  /* 4. Mr Ajon typing dots */
  var t2 = ajon_showTyping("ajon");
  await ajon_sleep(1800 + Math.random() * 1200);
  if (token !== chatToken || !BRAIN.isRunning) { if (t2 && t2.parentNode) t2.parentNode.removeChild(t2); return; }
  if (t2 && t2.parentNode) t2.parentNode.removeChild(t2);

  /* 5. Mr Ajon sends 2-5 bubbles */
  var ajonBubbles = buildMrAjonTurn();
  var ok2 = await ajon_send("ajon", ajonBubbles, token);
  if (!ok2) return;
  BRAIN.messages.push({ s: "ajon", t: ajonBubbles.join("\n"), ts: Date.now() });

  /* Capture last principle */
  for (var ai = 0; ai < ajonBubbles.length; ai++) {
    var line = String(ajonBubbles[ai]);
    if (line.indexOf("Principle: ") === 0) {
      BRAIN.lastPrinciple = line.substring(11);
      break;
    }
  }

  /* Advance state */
  BRAIN.chatCount++;
  if (BRAIN.lastMode === "question") {
    BRAIN.currentTopicId = nextTopicV9();
  }
  BRAIN.capital += Math.floor(Math.random() * 4000) + 1200;
  if (BRAIN.chatCount >= 300) BRAIN.level = 6;
  else if (BRAIN.chatCount >= 150) BRAIN.level = 5;
  else if (BRAIN.chatCount >= 80) BRAIN.level = 4;
  else if (BRAIN.chatCount >= 40) BRAIN.level = 3;
  else if (BRAIN.chatCount >= 15) BRAIN.level = 2;
  else BRAIN.level = 1;

  if (BRAIN.messages.length > 40) BRAIN.messages = BRAIN.messages.slice(-40);
  saveBrainState();

  /* Next turn after delay */
  chatTimer = setTimeout(function () {
    if (token !== chatToken) return;
    runTurn(token);
  }, 5000 + Math.random() * 3000);
}

function clearAssistantChat() {
  if (!hasFullAccess()) return;
  pauseAssistantChat();
  try {
    var keys = [];
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.indexOf("ajon_") === 0) keys.push(k);
    }
    for (var j = 0; j < keys.length; j++) localStorage.removeItem(keys[j]);
  } catch (e) {}
  BRAIN.messages = [];
  BRAIN.chatCount = 0;
  BRAIN.level = 1;
  BRAIN.capital = 86000;
  BRAIN.currentTopicId = null;
  BRAIN.lastTopics = [];
  BRAIN.lastPrinciple = null;
  BRAIN.pendingBiz = null;
  BRAIN.bizIdx = {};
  BRAIN.rotIdx = {};
  BRAIN.lastMode = "question";
  var box = byId("assistMsgs");
  if (box) box.innerHTML = "";
  setTimeout(function () { startAssistantChat(); }, 700);
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

# ---- Global rename: Mzee Ajon → Mr Ajon, Pasie → Pesie ----
html = html.replace("Mzee Ajon", "Mr Ajon")
html = re.sub(r'\bPasie\b', 'Pesie', html)
html = html.replace("images/pasie-avatar.webp", "images/pesie-avatar.webp")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS. v9 installed: Mr Ajon & Pesie, clean Q&A flow.")
