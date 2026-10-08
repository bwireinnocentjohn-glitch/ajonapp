import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__QUIZ_V1__" in html:
    print("Already applied. Exiting."); sys.exit(0)

NOTE   = chr(0x1F4DD)
MONEY  = chr(0x1F4B0)
CHECK  = chr(0x2713)
CROSS  = chr(0x2717)
ROCKET = chr(0x1F680)
SQ     = chr(39)   # single quote

changed = []

# ============================================================
# 1. Insert sub-tabs + wrapper opening after panel-notes
# ============================================================
old_start = '<section class="panel" id="panel-notes">'
idx = html.find(old_start)
if idx != -1:
    sub_tabs = (
        '\n      <div class="notes-sub-tabs">\n'
        '        <button class="notes-sub-btn active" data-notes="editor" onclick="switchNotesView(' + SQ + 'editor' + SQ + ')">' + NOTE + ' Notes</button>\n'
        '        <button class="notes-sub-btn" data-notes="quiz" onclick="switchNotesView(' + SQ + 'quiz' + SQ + ')">' + MONEY + ' Dream Money Game</button>\n'
        '      </div>\n'
        '      <div class="notes-view" id="notesEditorView">\n'
    )
    insert_pos = idx + len(old_start)
    html = html[:insert_pos] + sub_tabs + html[insert_pos:]

    # Find closing </section> of this panel
    close_idx = html.find('</section>', insert_pos)
    if close_idx != -1:
        quiz_html = (
            '</div>\n'
            '      <div class="notes-view hidden" id="notesQuizView">\n'
            '        <div class="quiz-header">\n'
            '          <div class="quiz-title">' + MONEY + ' Dream Money</div>\n'
            '          <div class="quiz-sub">Answer money questions. Earn coins. Level up.</div>\n'
            '        </div>\n'
            '        <div class="quiz-stats">\n'
            '          <div class="quiz-stat"><span class="quiz-stat-label">Coins</span><span class="quiz-stat-val" id="quizCoins">0</span></div>\n'
            '          <div class="quiz-stat"><span class="quiz-stat-label">Streak</span><span class="quiz-stat-val" id="quizStreak">0</span></div>\n'
            '          <div class="quiz-stat"><span class="quiz-stat-label">Round</span><span class="quiz-stat-val" id="quizRound">1</span></div>\n'
            '        </div>\n'
            '        <div class="quiz-card" id="quizCard">\n'
            '          <button class="btn" onclick="startQuiz()">' + ROCKET + ' Start Game</button>\n'
            '        </div>\n'
            '      </div>\n      '
        )
        html = html[:close_idx] + quiz_html + html[close_idx:]
        changed.append("1. Notes sub-tabs + quiz view added")

# ============================================================
# 2. CSS
# ============================================================
CSS = (
'\n/* ===== Notes sub-tabs + Money Quiz ===== */\n'
'.notes-sub-tabs { display: flex; gap: 8px; padding: 12px 16px 8px; background: #0a0a0a; border-bottom: 1px solid rgba(0,200,83,.25); }\n'
'.notes-sub-btn { flex: 1; background: #1a1a1a; border: 1px solid rgba(0,200,83,.35); color: #a8a8a8; border-radius: 10px; padding: 9px 8px; font-size: 12.5px; font-weight: 800; font-family: inherit; cursor: pointer; letter-spacing: .2px; }\n'
'.notes-sub-btn.active { background: linear-gradient(135deg,#00c853,#009624); color: #000; border-color: #00c853; }\n'
'.notes-view.hidden { display: none; }\n'
'.quiz-header { padding: 16px 16px 10px; text-align: center; }\n'
'.quiz-title { font-size: 22px; font-weight: 900; color: #00c853; letter-spacing: 1px; margin-bottom: 4px; }\n'
'.quiz-sub { font-size: 12px; color: #8f8f8f; font-weight: 600; }\n'
'.quiz-stats { display: flex; gap: 8px; padding: 6px 16px 14px; }\n'
'.quiz-stat { flex: 1; background: #1a1a1a; border: 1px solid rgba(0,200,83,.35); border-radius: 10px; padding: 8px 6px; text-align: center; }\n'
'.quiz-stat-label { display: block; font-size: 10px; color: #8f8f8f; letter-spacing: .5px; text-transform: uppercase; margin-bottom: 2px; }\n'
'.quiz-stat-val { font-size: 16px; font-weight: 900; color: #00c853; }\n'
'.quiz-card { background: #141414; border: 1px solid rgba(0,200,83,.35); border-left: 4px solid #00c853; border-radius: 14px; padding: 16px; margin: 0 16px 16px; }\n'
'.quiz-q { font-size: 14.5px; color: #fff; font-weight: 700; line-height: 1.5; margin-bottom: 14px; }\n'
'.quiz-answers { display: flex; flex-direction: column; gap: 8px; }\n'
'.quiz-ans { background: #1f1f1f; border: 1px solid rgba(0,200,83,.35); border-radius: 10px; padding: 11px 13px; color: #e6e6e6; font-size: 13.5px; font-weight: 600; font-family: inherit; cursor: pointer; text-align: left; }\n'
'.quiz-ans:active { background: #003d14; }\n'
'.quiz-ans.correct { background: #003d14; border-color: #00c853; color: #00c853; }\n'
'.quiz-ans.wrong { background: #2a0a00; border-color: #ff3d00; color: #ff3d00; }\n'
'.quiz-ans:disabled { cursor: default; opacity: .85; }\n'
'.quiz-feedback { margin-top: 12px; padding: 10px 12px; border-radius: 10px; background: #0f2a17; border-left: 3px solid #00c853; font-size: 12.5px; color: #e6f7ea; line-height: 1.55; }\n'
'.quiz-feedback.bad { background: #2a0a00; border-left-color: #ff3d00; color: #ffd7c2; }\n'
'.quiz-feedback b { color: #00c853; }\n'
'.quiz-feedback.bad b { color: #ff3d00; }\n'
'.quiz-next { display: block; width: 100%; margin-top: 12px; background: linear-gradient(135deg,#00c853,#009624); color: #fff; font-weight: 800; font-size: 14px; border: 0; border-radius: 10px; padding: 12px 16px; font-family: inherit; cursor: pointer; letter-spacing: .3px; }\n'
'.quiz-next:active { transform: scale(.97); }\n'
)
if ".notes-sub-tabs" not in html:
    sidx = html.rfind('</style>')
    if sidx != -1:
        html = html[:sidx] + CSS + html[sidx:]
        changed.append("2. Quiz CSS added")

# ============================================================
# 3. Quiz JS (raw string — Python does not interpret \u escapes)
# ============================================================
QUIZ_JS = r'''
/* ===== Money Quiz (Dream Money Game) ===== */
var QUIZ = {
  coins: 0,
  streak: 0,
  bestStreak: 0,
  round: 1,
  current: null,
  busy: false,
  usedIds: []
};

var QUIZ_BANK = [
  {q:"You buy 10kg tomatoes at 15,000 UGX. You sell at 20,000 UGX. What is your profit?",
   a:["5,000 UGX","10,000 UGX","15,000 UGX","20,000 UGX"], c:0,
   ex:"Profit = Sales minus Cost = 20,000 - 15,000 = 5,000 UGX."},
  {q:"You start a business with 50,000 UGX. After 30 days you have 80,000 UGX. What is your profit?",
   a:["20,000 UGX","30,000 UGX","80,000 UGX","50,000 UGX"], c:1,
   ex:"Profit = 80,000 - 50,000 = 30,000 UGX."},
  {q:"A customer buys on credit and never pays. What is this called?",
   a:["Profit","Bad debt","Capital","Equity"], c:1,
   ex:"Unpaid credit becomes bad debt - money lost."},
  {q:"You pay 10,000 for rent every month. Is this a fixed or variable cost?",
   a:["Fixed","Variable","Profit","Loss"], c:0,
   ex:"Rent does not change with sales - it is fixed."},
  {q:"Cash flow means:",
   a:["Total profit at year end","Money moving in and out daily","Stock on shelf","Debt owed to you"], c:1,
   ex:"Cash flow is daily movement - not the same as profit."},
  {q:"A customer wants a 5,000 UGX discount. Best reply?",
   a:["Give the discount at once","Say no","Add value instead (extra service)","Increase price"], c:2,
   ex:"Add value instead of dropping price - protects margin."},
  {q:"You take a 50,000 UGX loan at 20 percent monthly interest. Repayment after 30 days?",
   a:["50,000","55,000","60,000","70,000"], c:2,
   ex:"Interest = 50,000 x 20% = 10,000. Total = 60,000."},
  {q:"What is working capital?",
   a:["Stock plus Cash minus Debts","Profit only","Loan amount","Your salary"], c:0,
   ex:"Working capital = money available for daily running."},
  {q:"If you sell 100 units a day and each unit earns 500 UGX, what is your daily profit?",
   a:["500","5,000","50,000","500,000"], c:2,
   ex:"100 x 500 = 50,000 UGX per day."},
  {q:"Your break-even point is:",
   a:["Sales equal costs","Profit is highest","Loss is smallest","Cash is zero"], c:0,
   ex:"Break-even = sales exactly cover costs."},
  {q:"Best way to keep loyal customers?",
   a:["Give lowest price","Add surprises and good service","Close early","Ignore complaints"], c:1,
   ex:"Small surprises and great service keep customers."},
  {q:"You make 50,000 profit. You spend 40,000 on food. What remains for savings?",
   a:["10,000","40,000","50,000","90,000"], c:0,
   ex:"50,000 - 40,000 = 10,000 to save."},
  {q:"What is CAC?",
   a:["Cost of goods sold","Customer Acquisition Cost","Cash at closing","Capital add"], c:1,
   ex:"CAC = money spent to get one customer."},
  {q:"You buy 5kg sugar at 4,500 per kg. Total cost?",
   a:["9,000","18,000","22,500","25,000"], c:2,
   ex:"5 x 4,500 = 22,500 UGX."},
  {q:"More cash going out than in. This is:",
   a:["Positive cash flow","Negative cash flow","Break even","Profit"], c:1,
   ex:"More out than in = negative cash flow - danger zone."}
];

function quizRenderCoins() {
  try {
    var total = (typeof getCoins === "function") ? getCoins() : 0;
    var el1 = byId("quizCoins");
    var el2 = byId("quizStreak");
    var el3 = byId("quizRound");
    if (el1) el1.textContent = total;
    if (el2) el2.textContent = QUIZ.streak;
    if (el3) el3.textContent = QUIZ.round;
  } catch(e) {}
}

function startQuiz() {
  QUIZ.usedIds = [];
  QUIZ.streak = 0;
  QUIZ.round = 1;
  nextQuizQ();
}

function pickQuiz() {
  var pool = [];
  for (var i = 0; i < QUIZ_BANK.length; i++) {
    if (QUIZ.usedIds.indexOf(i) === -1) pool.push(i);
  }
  if (!pool.length) {
    QUIZ.usedIds = [];
    for (var k = 0; k < QUIZ_BANK.length; k++) pool.push(k);
  }
  var idx = pool[Math.floor(Math.random() * pool.length)];
  QUIZ.usedIds.push(idx);
  return { idx: idx, q: QUIZ_BANK[idx] };
}

function nextQuizQ() {
  QUIZ.busy = false;
  QUIZ.current = pickQuiz();
  quizRenderCoins();
  var card = byId("quizCard");
  if (!card) return;
  var q = QUIZ.current.q;
  var h = '<div class="quiz-q">' + QUIZ.round + '. ' + escapeHTML(q.q) + '</div>';
  h += '<div class="quiz-answers">';
  for (var i = 0; i < q.a.length; i++) {
    h += '<button class="quiz-ans" onclick="submitQuiz(' + i + ')">' + escapeHTML(q.a[i]) + '</button>';
  }
  h += '</div><div id="quizFeedback"></div>';
  card.innerHTML = h;
}

function submitQuiz(picked) {
  if (QUIZ.busy) return;
  QUIZ.busy = true;
  var q = QUIZ.current.q;
  var buttons = document.querySelectorAll("#quizCard .quiz-ans");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].disabled = true;
    if (i === q.c) buttons[i].classList.add("correct");
    else if (i === picked) buttons[i].classList.add("wrong");
  }
  var fb = byId("quizFeedback");
  if (picked === q.c) {
    QUIZ.streak++;
    if (QUIZ.streak > QUIZ.bestStreak) QUIZ.bestStreak = QUIZ.streak;
    var reward = 100 + (QUIZ.streak >= 3 ? 50 : 0);
    try {
      var total = (typeof getCoins === "function" ? getCoins() : 0) + reward;
      writeJSON("ajon_coins", total);
    } catch(e) {}
    if (fb) { fb.className = "quiz-feedback"; fb.innerHTML = '<b>Correct! +' + reward + ' coins</b><br>' + escapeHTML(q.ex); }
  } else {
    QUIZ.streak = 0;
    if (fb) { fb.className = "quiz-feedback bad"; fb.innerHTML = '<b>Wrong answer</b><br>' + escapeHTML(q.ex); }
  }
  quizRenderCoins();
  var nxt = document.createElement("button");
  nxt.className = "quiz-next";
  nxt.textContent = "Next Question";
  nxt.onclick = function () { QUIZ.round++; nextQuizQ(); };
  var card = byId("quizCard");
  if (card) card.appendChild(nxt);
}

function switchNotesView(view) {
  try {
    var btns = document.querySelectorAll(".notes-sub-btn");
    for (var i = 0; i < btns.length; i++) {
      btns[i].classList.toggle("active", btns[i].getAttribute("data-notes") === view);
    }
    var ed = byId("notesEditorView");
    var qz = byId("notesQuizView");
    if (ed) ed.classList.toggle("hidden", view !== "editor");
    if (qz) qz.classList.toggle("hidden", view !== "quiz");
    if (view === "quiz") quizRenderCoins();
  } catch(e) {}
}
'''

if "QUIZ_BANK" not in html:
    idx2 = html.rfind('</script>')
    if idx2 != -1:
        html = html[:idx2] + '\n' + QUIZ_JS + '\n' + html[idx2:]
        changed.append("3. Quiz JS added")

if "__QUIZ_V1__" not in html:
    idx3 = html.rfind('</script>')
    if idx3 != -1:
        html = html[:idx3] + '\n/* __QUIZ_V1__ */\n' + html[idx3:]
        changed.append("4. Marker added")

# Safe atomic write
tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("Changes:")
for c in changed:
    print("  " + c)
print("")
print("SUCCESS. Money Quiz added to Notes tab.")
