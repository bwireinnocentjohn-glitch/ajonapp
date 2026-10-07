/* ==========================================================
   Ajon Expert Brain — search + teach engine
   Uses window.BIZ_BATCH and window.WISDOM_BATCH
   ========================================================== */
(function(){
  if (window.__ajonExpertBrainV1) return;
  window.__ajonExpertBrainV1 = true;

  var BIZ = window.BIZ_BATCH || [];
  var WIS = window.WISDOM_BATCH || [];

  var NAME_WORD_FREQ = null;
  function buildNameFreq() {
    if (NAME_WORD_FREQ) return;
    NAME_WORD_FREQ = {};
    for (var i = 0; i < BIZ.length; i++) {
      var toks = String(BIZ[i].name || "").toLowerCase().split(/[^a-z0-9]+/).filter(function(t){ return t.length >= 4; });
      var seen = {};
      for (var j = 0; j < toks.length; j++) {
        if (!seen[toks[j]]) { NAME_WORD_FREQ[toks[j]] = (NAME_WORD_FREQ[toks[j]] || 0) + 1; seen[toks[j]] = 1; }
      }
    }
  }
  buildNameFreq();

  /* Synonyms map */
  var SYN = {
    "bsf":"black soldier fly", "black soldier":"black soldier fly",
    "cricket":"cricket", "crickets":"cricket",
    "boda":"motorcycle", "rolex":"chapati egg",
    "power bank":"battery bank", "incubator":"hatchery",
    "mushroom":"oyster mushroom", "poultry":"chicken",
    "wifi":"internet", "mommy":"money", "capita":"capital",
    "cassava":"cassava", "posho":"maize flour",
    "soap":"soap", "candle":"candle", "brick":"briquette",
    "briquette":"briquette", "charcoal":"briquette"
  };

  var STOPS = {
    "how":1,"do":1,"what":1,"is":1,"the":1,"a":1,"an":1,"can":1,
    "i":1,"my":1,"me":1,"you":1,"we":1,"they":1,"he":1,"she":1,
    "to":1,"for":1,"of":1,"in":1,"on":1,"at":1,"by":1,"with":1,
    "and":1,"or":1,"but":1,"if":1,"so":1,
    "this":1,"that":1,"these":1,"those":1,"it":1,"its":1,
    "be":1,"am":1,"are":1,"was":1,"were":1,"been":1,
    "make":1,"makes":1,"making":1,"made":1,
    "start":1,"starts":1,"starting":1,
    "want":1,"wants":1,"need":1,"needs":1,
    "give":1,"gives":1,"get":1,"gets":1,
    "help":1,"please":1,"tell":1,"show":1,"teach":1,"explain":1,
    "about":1,"from":1,"into":1,"than":1,"then":1,
    "any":1,"all":1,"some":1,"more":1,"most":1,
    "good":1,"best":1,"great":1,"nice":1
  };

  function stopFilter(s){
    return String(s||"").split(" ").filter(function(w){
      return w.length >= 2 && !STOPS[w];
    });
  }


  function norm(t){
    t = String(t||"").toLowerCase()
      .replace(/[^a-z0-9\s]/g," ")
      .replace(/\s+/g," ").trim();
    var words = t.split(" ");
    for (var i=0;i<words.length;i++){
      if (SYN[words[i]]) words[i] = SYN[words[i]];
    }
    return words.join(" ");
  }

  function scoreBiz(biz, qRaw){
    var q = norm(qRaw);
    var words = stopFilter(q);
    var nameLow = String(biz.name||"").toLowerCase();
    var hay = (biz.name + " " + biz.category + " " + (biz.whyNow||biz.whyNow2026||"") + " " + (biz.tags||[]).join(" ")).toLowerCase();
    var s = 0;

    if (words.length >= 2) {
      var phrase = words.join(" ");
      if (nameLow.indexOf(phrase) > -1) s += 100;
      else if (hay.indexOf(phrase) > -1) s += 20;
    }

    var nameHits = 0, hayHits = 0, rareBoost = 0;
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      if (nameLow.indexOf(w) > -1) {
        nameHits++;
        var freq = (NAME_WORD_FREQ && NAME_WORD_FREQ[w]) || 99;
        if (freq <= 2) rareBoost += 60;
        else if (freq <= 5) rareBoost += 25;
      } else if (hay.indexOf(w) > -1) hayHits++;
    }
    if (words.length > 0 && nameHits === words.length) s += 60;
    s += nameHits * 15;
    s += hayHits * 2;
    s += rareBoost;

    if (nameLow.length >= 4 && q.indexOf(nameLow) > -1) s += 80;

    /* SCORE_BOOST_V2 — query-side phrase priority */
    if (words.length >= 1) {
      var nameTokens = nameLow.split(/[^a-z0-9]+/).filter(function(t){ return t.length >= 3; });
      var qSet = {};
      for (var k = 0; k < words.length; k++) qSet[words[k]] = 1;
      var nameMatched = 0;
      for (var n = 0; n < nameTokens.length; n++) {
        if (qSet[nameTokens[n]] || q.indexOf(nameTokens[n]) > -1) nameMatched++;
      }
      if (nameTokens.length > 0 && nameMatched === nameTokens.length) s += 40;
      else s += nameMatched * 5;
    }

    return s;
  }

  function searchBusinesses(query){
    var q = norm(query);
    if (!q) return [];
    var scored = [];
    for (var i=0;i<BIZ.length;i++){
      var s = scoreBiz(BIZ[i], q);
      if (s >= 8) scored.push({biz:BIZ[i], score:s});
    }
    scored.sort(function(a,b){ return b.score - a.score; });
    return scored.slice(0,3).map(function(x){ return x.biz; });
  }

  function searchWisdom(query){
    var q = norm(query);
    if (!q) return null;
    var best = null, bestScore = 0;
    for (var i=0;i<WIS.length;i++){
      var w = WIS[i];
      var s = 0;
      for (var j=0;j<w.keywords.length;j++){
        if (q.indexOf(norm(w.keywords[j])) > -1) s += 3;
      }
      if (q.indexOf(w.intent) > -1) s += 5;
      if (s > bestScore){ bestScore = s; best = w; }
    }
    return bestScore >= 3 ? best : null;
  }

  function fmtBiz(biz){
    var out = [];
    out.push(biz.emoji + " " + biz.name.toUpperCase() + " \u2014 " + biz.capital + " Start \u2014 " + biz.timeToMoney + " to first money");
    out.push("");
    var _why = biz.whyNow || biz.whyNow2026 || "Strong daily demand in local markets.";
    out.push("\uD83C\uDFAF Why It Sells Well: " + _why);
    out.push("");
    out.push("\uD83D\uDCB0 Capital Breakdown:");
    for (var i=0;i<biz.capitalBreakdown.length;i++) out.push("\u2022 " + biz.capitalBreakdown[i]);
    out.push("");
    out.push("\uD83D\uDEE0\uFE0F 5 Steps To Start Today:");
    for (var j=0;j<biz.steps.length;j++) out.push((j+1) + ". " + biz.steps[j]);
    out.push("");
    out.push("\uD83D\uDCC8 Profit Math:");
    out.push(biz.profitMath);
    out.push("");
    out.push("\uD83C\uDFEA Where To Sell Tomorrow Morning:");
    out.push(biz.market);
    out.push("");
    out.push("\u26A0\uFE0F 3 Mistakes That Kill Beginners:");
    for (var k=0;k<Math.min(3,biz.mistakes.length);k++) out.push((k+1) + ". " + biz.mistakes[k]);
    out.push("");
    out.push("\uD83D\uDE80 How To Scale:");
    out.push(biz.scaling);
    out.push("");
    out.push("\u2705 Your Task Before 6pm Today:");
    out.push(biz.homework);
    return out.join("\n");
  }

  function fmtWisdom(w){
    var out = [];
    out.push("\uD83D\uDCA1 " + w.principle);
    out.push("");
    out.push(w.explanation);
    out.push("");
    out.push("\uD83D\uDD27 3 Steps:");
    for (var i=0;i<w.steps.length;i++) out.push((i+1) + ". " + w.steps[i]);
    out.push("");
    out.push("\uD83C\uDF0D Example: " + w.example);
    return out.join("\n");
  }



  var BRAIN_TERMS = {
    "cash flow": "The daily movement of money in and out of your business. Not the same as profit. Track every shilling leaving your pocket tonight.",
    "profit margin": "The percentage of money you keep after costs. Sell at 10,000, cost 7,000, margin is 30%.",
    "break even": "The point where sales equal costs. Below it you lose. Above it you profit. Know your floor.",
    "kpi": "Key Performance Indicator. The one number you watch daily. Sales, repeat buyers, cash in hand.",
    "usp": "Unique Selling Point. The one thing you offer that others do not.",
    "cac": "Customer Acquisition Cost. Money spent to get one customer.",
    "ltv": "Lifetime Value. Total money a customer spends with you over years.",
    "churn": "Customers who leave and never come back.",
    "roi": "Return on Investment. What you gain from what you spent.",
    "b2b": "Business to Business. You sell to other businesses.",
    "b2c": "Business to Consumer. You sell to individual people.",
    "mvp": "Minimum Viable Product. The smallest version that tests your idea.",
    "caustic soda": "Sodium hydroxide. Strong chemical. In soap it turns oil into soap. Always wear gloves.",
    "shea butter": "Fat from shea nuts. Used in cosmetics for skin and hair.",
    "bsf": "Black Soldier Fly. Larvae convert food waste into animal feed.",
    "gross profit": "Sales minus cost of goods sold.",
    "net profit": "What remains after all costs, taxes, and interest.",
    "fixed cost": "A cost that does not change with sales. Rent, licence, salary.",
    "variable cost": "A cost that changes with every sale. Materials, packaging, transport.",
    "working capital": "Money available for daily running. Stock plus cash minus debts."
  };

  function brainMatchTerm(q) {
    var low = " " + String(q || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim() + " ";
    var keys = Object.keys(BRAIN_TERMS);
    var best = null, bestLen = 0;
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (low.indexOf(" " + k + " ") > -1 || low.indexOf(" " + k) > -1) {
        if (k.length > bestLen) { bestLen = k.length; best = k; }
      }
    }
    return best;
  }


  function buildExpertReply(q){
    try {
      var query = String(q||"").trim();
      if (!query) return null;

      /* 0. Term lookup (defined phrases FIRST) */
      var termHit = brainMatchTerm(query);
      if (termHit) {
        var def = BRAIN_TERMS[termHit];
        return ["\uD83D\uDCD8 " + termHit.charAt(0).toUpperCase() + termHit.slice(1) + ":\n\n" + def];
      }

      /* 1. Business search */
      var bizzes = searchBusinesses(query);
      if (bizzes.length) {
        var out = [fmtBiz(bizzes[0])];
        if (bizzes.length > 1) {
          out.push("\uD83D\uDCA1 Other related: " + bizzes.slice(1).map(function(b){ return b.emoji + " " + b.name; }).join(" | "));
        }
        return out;
      }

      /* 2. Wisdom search */
      var w = searchWisdom(query);
      if (w) return [fmtWisdom(w)];

      /* 3. Not found - return null so old logic runs */
      return null;
    } catch (e) {
      return null;
    }
  }

  /* Expose to window */
  window.searchBusinesses = searchBusinesses;
  window.searchWisdom = searchWisdom;
  window.buildExpertReply = buildExpertReply;
  window.fmtBiz = fmtBiz;

  /* Memory (minimal) */
  try {
    window.getBrainMemory = function(){
      try { return JSON.parse(localStorage.getItem("ajon_brain_mem")||"[]"); }
      catch(e){ return []; }
    };
    window.saveBrainMemory = function(q, id){
      try {
        var m = window.getBrainMemory();
        m.unshift({q:q, id:id, t:Date.now()});
        if (m.length > 20) m = m.slice(0,20);
        localStorage.setItem("ajon_brain_mem", JSON.stringify(m));
      } catch(e){}
    };
  } catch(e){}

  try { console.log("[Ajon Brain] Loaded " + BIZ.length + " businesses, " + WIS.length + " wisdom entries"); } catch(e){}
})();

/* __ajonWhyNowV1 */
