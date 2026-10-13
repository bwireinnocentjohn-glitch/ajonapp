/* __DAILY_MOTIVATION_V1__ */
(function(){
  "use strict";
  if (window.__ajonDailyMotivation) return;
  window.__ajonDailyMotivation = true;

  var KEY_LAST = "ajon_motiv_date_v1";

  var QUOTES = [
    "Every expert was once a beginner who refused to quit.",
    "Small daily efforts beat one big burst of motivation.",
    "Your first customer is worth more than 100 ideas. Go find them.",
    "Money grows where discipline lives. Track every coin.",
    "The best time to start was yesterday. Next best is now.",
    "Failure is feedback. Every loss teaches what to fix.",
    "If you cannot find a door, build one. That is what entrepreneurs do.",
    "Do not wait for perfect conditions. Start with what you have.",
    "A customer who trusts you brings 5 more. Treat them like gold.",
    "Learn one skill deeply. It will feed you for years.",
    "Save 10% of everything you earn. Future you will thank you.",
    "Competition means there is demand. Stand out, do not run away.",
    "Your reputation is your most valuable asset. Guard it.",
    "Ideas are cheap. Execution is priceless.",
    "Consistency beats talent when talent is inconsistent.",
    "A business plan on paper is worth more than a dream in your head.",
    "Charge what you are worth. Discounting kills profit.",
    "If your product is good, word of mouth is your best ad.",
    "Wake up one hour earlier. That is 365 extra hours a year.",
    "Your phone is a factory. Use it to build, not just to scroll.",
    "Every shilling saved is a shilling earned twice.",
    "Hire slow, fire fast. Your team defines your business.",
    "Feedback is free consulting. Ask your customers.",
    "Sell solutions, not products. People buy outcomes.",
    "Cash flow is oxygen. Profit is food. Both matter.",
    "Learn to say no to bad deals. Time is your capital.",
    "The customer is not always right, but they are always the boss.",
    "Reinvest your first profits. Growth compounds.",
    "A small business with good books beats a big one without.",
    "Talk to 10 customers before you build anything.",
    "Your first 100 customers will teach you everything.",
    "Price for value. Cheap attracts cheap.",
    "If it does not make money, it is a hobby, not a business.",
    "Every problem you solve is a product you can sell.",
    "Partner with people who lift you, not drain you.",
    "Record every transaction. Numbers do not lie.",
    "Africa's biggest untapped market is the one in your village.",
    "Learn from those ahead of you. A mentor is faster than trial.",
    "Your customer's complaint is a gift with a bow on top.",
    "Doubt kills more dreams than failure ever will.",
    "Start small. Start now. Start scared. But start.",
    "Debt can be a tool or a trap. Choose wisely.",
    "Your time has value. Stop giving it away for free.",
    "The business that adapts survives. The one that does not, dies.",
    "Do one thing every day that scares your competition.",
    "Build trust like a bank account. Deposit daily.",
    "Great businesses are built on boring, consistent work.",
    "Think in years, not days. Wealth is a long game.",
    "Wealth flows to those who solve real problems.",
    "Tomorrow's success is decided by today's habits."
  ];

  function todayKey(){
    var d = new Date();
    return d.getFullYear() + "-" + (d.getMonth()+1) + "-" + d.getDate();
  }

  function pickQuote(){
    try {
      var idx = Math.floor(Math.random() * QUOTES.length);
      return QUOTES[idx];
    } catch(e){ return QUOTES[0]; }
  }

  function showModal(){
    try {
      if (document.getElementById("ajonMotivModal")) return;
      var q = pickQuote();
      var t = document.createElement("div");
      t.id = "ajonMotivModal";
      t.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:2147483644;display:flex;align-items:center;justify-content:center;padding:24px;font-family:inherit;";
      t.innerHTML =
        '<div style="background:linear-gradient(135deg,#001a0a,#003d14);border:1px solid rgba(0,200,83,.55);border-radius:20px;max-width:380px;width:100%;padding:26px 22px;text-align:center;box-shadow:0 10px 40px rgba(0,200,83,.3);">' +
          '<div style="font-size:44px;margin-bottom:10px;">\uD83D\uDCA1</div>' +
          '<div style="color:#a7f3d0;font-size:11px;font-weight:900;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;">Daily Motivation</div>' +
          '<div style="color:#fff;font-size:16px;font-weight:700;line-height:1.55;margin-bottom:16px;">&ldquo;' + q + '&rdquo;</div>' +
          '<div style="color:#6ee7b7;font-size:13px;line-height:1.6;margin-bottom:20px;padding:12px 14px;background:rgba(0,0,0,.35);border-radius:10px;">Learn the business of your choice and apply for a soft business loan today.</div>' +
          '<button id="ajonMotivOk" type="button" style="background:linear-gradient(135deg,#a7f3d0,#34d399);color:#052e16;border:0;border-radius:999px;padding:12px 30px;font-size:14px;font-weight:900;cursor:pointer;letter-spacing:.4px;font-family:inherit;box-shadow:0 6px 22px rgba(52,211,153,.5);">Got it</button>' +
        '</div>';
      document.body.appendChild(t);
      var ok = t.querySelector("#ajonMotivOk");
      if (ok) ok.onclick = function(){
        try { localStorage.setItem(KEY_LAST, todayKey()); } catch(e){}
        try { document.body.removeChild(t); } catch(e){}
      };
    } catch(e){}
  }

  setTimeout(function(){
    try {
      var last = localStorage.getItem(KEY_LAST);
      if (last === todayKey()) return;
      setTimeout(showModal, 2500);
    } catch(e){}
  }, 1500);
})();
