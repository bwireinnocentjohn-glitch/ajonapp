import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__AJON_BRIDGE_V1__" in html:
    print("Already applied. Exiting."); sys.exit(0)

BRIDGE = '''<script>
/* __AJON_BRIDGE_V1__ - final wiring for all features */
(function(){
  "use strict";
  function $(id){ return document.getElementById(id); }
  function getCoins(){
    try { return Number(localStorage.getItem("ajon_coins")) || 0; }
    catch(e){ return 0; }
  }
  function setCoins(n){
    try { localStorage.setItem("ajon_coins", String(Number(n)||0)); }
    catch(e){}
  }
  function esc(s){
    return String(s||"").replace(/[&<>"']/g, function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}[c];
    });
  }

  function getCoinTier(coins){
    coins = Number(coins) || 0;
    if (coins >= 1000000) return { name:"DIAMOND", label:"DIAMOND tier (1,000,000+ coins)", color:"#5bc0eb" };
    if (coins >= 100000)  return { name:"GOLD",    label:"GOLD tier (100,000+ coins)",    color:"#ffb300" };
    if (coins >= 1000)    return { name:"SILVER",  label:"SILVER tier (1,000+ coins)",    color:"#c0c0c0" };
    return { name:"BRONZE", label:"BRONZE tier - earn 1,000+ to level up", color:"#cd7f32" };
  }

  window.getCoins = getCoins;
  window.setCoins = setCoins;
  window.getCoinTier = getCoinTier;

  /* CREDITS */
  window.openCreditsModal = function(){
    var m = $("creditsModal");
    if (m) m.classList.add("open");
  };
  window.closeCreditsModal = function(){
    var m = $("creditsModal");
    if (m) m.classList.remove("open");
  };

  /* LOAN SWITCH */
  window.toggleLoanNotice = function(){
    var sw = $("loanSwitch");
    var card = $("loanNoticeCard");
    if (!sw || !card) return;
    var on = sw.classList.contains("on");
    if (on) {
      sw.classList.remove("on");
      card.classList.add("hidden");
      try { localStorage.setItem("ajon_loan_notice","0"); } catch(e){}
    } else {
      sw.classList.add("on");
      card.classList.remove("hidden");
      try { localStorage.setItem("ajon_loan_notice","1"); } catch(e){}
    }
  };
  window.initLoanNoticeState = function(){
    var sw = $("loanSwitch");
    var card = $("loanNoticeCard");
    if (!sw || !card) return;
    try {
      var saved = localStorage.getItem("ajon_loan_notice");
      if (saved === "0") { sw.classList.remove("on"); card.classList.add("hidden"); }
      else { sw.classList.add("on"); card.classList.remove("hidden"); }
    } catch(e){}
  };

  /* WHATSAPP SHARE */
  window.shareWhatsApp = function(){
    var msg = "Install The Ajon 1500+ Business App, With Free Data Buddle for 30 days, learn from Expert and Divorce From Poverty, At 5000/= 30 days Fully";
    var url = "https://wa.me/?text=" + encodeURIComponent(msg);
    try { window.open(url, "_blank"); } catch(e) { try { location.href = url; } catch(x){} }
    var c = getCoins() + 1000;
    setCoins(c);
    var tier = getCoinTier(c);
    setTimeout(function(){
      try { alert("+1000 coins added!\\n\\nTotal: " + c + " coins\\n" + tier.label); } catch(x){}
    }, 200);
  };

  /* NOTES SUB-TABS */
  window.switchNotesView = function(view){
    try {
      var btns = document.querySelectorAll(".notes-sub-btn");
      for (var i=0; i<btns.length; i++){
        btns[i].classList.toggle("active", btns[i].getAttribute("data-notes") === view);
      }
      var ed = $("notesEditorView");
      var qz = $("notesQuizView");
      if (ed) ed.classList.toggle("hidden", view !== "editor");
      if (qz) qz.classList.toggle("hidden", view !== "quiz");
      if (view === "quiz" && typeof window.quizRenderCoins === "function") window.quizRenderCoins();
    } catch(e){}
  };

  /* QUIZ */
  var QZ = { streak:0, best:0, round:1, current:null, busy:false, used:[] };
  var BANK = [
    {q:"You buy 10kg tomatoes at 15,000 UGX. You sell at 20,000 UGX. What is your profit?", a:["5,000 UGX","10,000 UGX","15,000 UGX","20,000 UGX"], c:0, ex:"Profit = Sales minus Cost = 20,000 - 15,000 = 5,000 UGX."},
    {q:"Start with 50,000 UGX. After 30 days you have 80,000 UGX. Profit?", a:["20,000 UGX","30,000 UGX","80,000 UGX","50,000 UGX"], c:1, ex:"Profit = 80,000 - 50,000 = 30,000 UGX."},
    {q:"A customer buys on credit and never pays. This is called:", a:["Profit","Bad debt","Capital","Equity"], c:1, ex:"Unpaid credit becomes bad debt."},
    {q:"Rent of 10,000 every month is a:", a:["Fixed cost","Variable cost","Profit","Loss"], c:0, ex:"Rent does not change - it is fixed."},
    {q:"Cash flow means:", a:["Profit at year end","Money moving in and out daily","Stock on shelf","Debt owed"], c:1, ex:"Cash flow is daily movement."},
    {q:"Best reply to a discount request?", a:["Give discount","Say no","Add value instead","Raise price"], c:2, ex:"Add value - protects margin."},
    {q:"50,000 loan at 20% monthly. Repay after 30 days?", a:["50,000","55,000","60,000","70,000"], c:2, ex:"Interest = 10,000. Total = 60,000."},
    {q:"Working capital is:", a:["Stock + Cash - Debts","Profit","Loan","Salary"], c:0, ex:"Working capital = daily running money."},
    {q:"100 units a day x 500 UGX each. Daily profit?", a:["500","5,000","50,000","500,000"], c:2, ex:"100 x 500 = 50,000."},
    {q:"Break-even point means:", a:["Sales equal costs","Highest profit","Lowest loss","Zero cash"], c:0, ex:"Break-even = cover costs."},
    {q:"Best way to keep loyal customers?", a:["Lowest price","Add value and good service","Close early","Ignore complaints"], c:1, ex:"Small surprises keep customers."},
    {q:"50,000 profit, 40,000 spent on food. Savings?", a:["10,000","40,000","50,000","90,000"], c:0, ex:"50,000 - 40,000 = 10,000."},
    {q:"CAC stands for:", a:["Cost of goods","Customer Acquisition Cost","Cash at close","Capital"], c:1, ex:"CAC = cost to get one customer."},
    {q:"5kg sugar at 4,500/kg. Total cost?", a:["9,000","18,000","22,500","25,000"], c:2, ex:"5 x 4,500 = 22,500."},
    {q:"More cash out than in means:", a:["Positive","Negative cash flow","Break even","Profit"], c:1, ex:"Negative cash flow - danger."}
  ];

  window.quizRenderCoins = function(){
    var e1 = $("quizCoins"), e2 = $("quizStreak"), e3 = $("quizRound");
    if (e1) e1.textContent = getCoins();
    if (e2) e2.textContent = QZ.streak;
    if (e3) e3.textContent = QZ.round;
  };

  function pickQuiz(){
    var pool = [];
    for (var i=0; i<BANK.length; i++) if (QZ.used.indexOf(i) === -1) pool.push(i);
    if (!pool.length) { QZ.used = []; for (var k=0; k<BANK.length; k++) pool.push(k); }
    var idx = pool[Math.floor(Math.random() * pool.length)];
    QZ.used.push(idx);
    return BANK[idx];
  }

  function nextQuizQ(){
    QZ.busy = false;
    QZ.current = pickQuiz();
    window.quizRenderCoins();
    var card = $("quizCard");
    if (!card) return;
    var q = QZ.current;
    var h = '<div class="quiz-q">' + QZ.round + '. ' + esc(q.q) + '</div>';
    h += '<div class="quiz-answers">';
    for (var i=0; i<q.a.length; i++){
      h += '<button class="quiz-ans" onclick="submitQuiz(' + i + ')">' + esc(q.a[i]) + '</button>';
    }
    h += '</div><div id="quizFeedback"></div>';
    card.innerHTML = h;
  }

  window.startQuiz = function(){
    QZ.used = []; QZ.streak = 0; QZ.round = 1;
    nextQuizQ();
  };

  window.submitQuiz = function(picked){
    if (QZ.busy) return;
    QZ.busy = true;
    var q = QZ.current;
    var buttons = document.querySelectorAll("#quizCard .quiz-ans");
    for (var i=0; i<buttons.length; i++){
      buttons[i].disabled = true;
      if (i === q.c) buttons[i].classList.add("correct");
      else if (i === picked) buttons[i].classList.add("wrong");
    }
    var fb = $("quizFeedback");
    if (picked === q.c){
      QZ.streak++;
      if (QZ.streak > QZ.best) QZ.best = QZ.streak;
      var reward = 100 + (QZ.streak >= 3 ? 50 : 0);
      setCoins(getCoins() + reward);
      if (fb) { fb.className = "quiz-feedback"; fb.innerHTML = '<b>Correct! +' + reward + ' coins</b><br>' + esc(q.ex); }
    } else {
      QZ.streak = 0;
      if (fb) { fb.className = "quiz-feedback bad"; fb.innerHTML = '<b>Wrong answer</b><br>' + esc(q.ex); }
    }
    window.quizRenderCoins();
    var nxt = document.createElement("button");
    nxt.className = "quiz-next";
    nxt.textContent = "Next Question";
    nxt.onclick = function(){ QZ.round++; nextQuizQ(); };
    var c = $("quizCard");
    if (c) c.appendChild(nxt);
  };

  /* TRIAL TICK + LOCK ENFORCER */
  function enforceTrial(){
    try {
      var installTime = null;
      try { installTime = JSON.parse(localStorage.getItem("ajon_install_v10")); } catch(e){}
      if (!installTime) {
        try { installTime = JSON.parse(localStorage.getItem("ajon_install_v9")); } catch(e){}
      }
      if (!installTime) {
        try { installTime = JSON.parse(localStorage.getItem("ajon_install_v11")); } catch(e){}
      }
      if (!installTime) {
        try { installTime = JSON.parse(localStorage.getItem("ajon_install_v12")); } catch(e){}
      }

      var bar = document.getElementById("trialBar");
      if (!bar) return;

      var subEnd = 0;
      try { subEnd = Number(localStorage.getItem("ajon_sub_end_v10")) || 0; } catch(e){}
      if (!subEnd) { try { subEnd = Number(localStorage.getItem("ajon_sub_end_v11")) || 0; } catch(e){} }
      if (!subEnd) { try { subEnd = Number(localStorage.getItem("ajon_sub_end_v9")) || 0; } catch(e){} }
      if (!subEnd) { try { subEnd = Number(localStorage.getItem("ajon_sub_end_v12")) || 0; } catch(e){} }

      if (subEnd > Date.now()) {
        var dl = Math.ceil((subEnd - Date.now()) / 86400000);
        bar.innerHTML = '<div class="trial-bar">Full access - ' + dl + ' days remaining</div>';
        return;
      }

      if (installTime) {
        var trialMs = 5 * 60 * 1000;
        var left = trialMs - (Date.now() - installTime);
        if (left > 0) {
          var s = Math.ceil(left / 1000);
          var m = Math.floor(s / 60);
          var sec = s % 60;
          var t = m + ":" + (sec < 10 ? "0" : "") + sec;
          bar.innerHTML = '<div class="trial-bar">Free preview: <span class="time">' + t + '</span> - enjoy all tutorials</div>';
          return;
        }
      }

      bar.innerHTML = '<div class="trial-bar">Preview ended - Unlock 1500+ ideas in the Unlock tab</div>';
    } catch(e){}
  }

  function init(){
    try { window.initLoanNoticeState(); } catch(e){}
    enforceTrial();
    setInterval(enforceTrial, 1000);
    try { console.log("[Ajon Bridge] Loaded and enforcing."); } catch(e){}
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
</script>
'''

if "</body>" in html:
    html = html.replace("</body>", BRIDGE + "\n</body>", 1)
    print("Bridge script added before </body>")
else:
    print("ERROR: </body> not found"); sys.exit(1)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

print("")
print("SUCCESS. Bridge installed.")
