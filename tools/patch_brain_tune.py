import io, sys, os, tempfile

JS = 'www/js/expertBrain.js'
if not os.path.exists(JS):
    print("ERROR: expertBrain.js not found"); sys.exit(1)

with io.open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

changed = False

# ============================================================
# FIX A: rare-word frequency map (once)
# ============================================================
if "NAME_WORD_FREQ" not in js:
    old = "var BIZ = window.BIZ_BATCH || [];\n  var WIS = window.WISDOM_BATCH || [];"
    new = ('var BIZ = window.BIZ_BATCH || [];\n'
'  var WIS = window.WISDOM_BATCH || [];\n\n'
'  var NAME_WORD_FREQ = null;\n'
'  function buildNameFreq() {\n'
'    if (NAME_WORD_FREQ) return;\n'
'    NAME_WORD_FREQ = {};\n'
'    for (var i = 0; i < BIZ.length; i++) {\n'
'      var toks = String(BIZ[i].name || "").toLowerCase().split(/[^a-z0-9]+/).filter(function(t){ return t.length >= 4; });\n'
'      var seen = {};\n'
'      for (var j = 0; j < toks.length; j++) {\n'
'        if (!seen[toks[j]]) { NAME_WORD_FREQ[toks[j]] = (NAME_WORD_FREQ[toks[j]] || 0) + 1; seen[toks[j]] = 1; }\n'
'      }\n'
'    }\n'
'  }\n'
'  buildNameFreq();')
    if old in js:
        js = js.replace(old, new, 1)
        print("A. NAME_WORD_FREQ precomputed")
        changed = True
    else:
        print("WARN A: BIZ declaration not matched")

# ============================================================
# FIX B: rare-word boost in scoreBiz
# ============================================================
if "rareBoost" not in js:
    old = ('var nameHits = 0, hayHits = 0;\n'
'    for (var i = 0; i < words.length; i++) {\n'
'      var w = words[i];\n'
'      if (nameLow.indexOf(w) > -1) nameHits++;\n'
'      else if (hay.indexOf(w) > -1) hayHits++;\n'
'    }')
    new = ('var nameHits = 0, hayHits = 0, rareBoost = 0;\n'
'    for (var i = 0; i < words.length; i++) {\n'
'      var w = words[i];\n'
'      if (nameLow.indexOf(w) > -1) {\n'
'        nameHits++;\n'
'        var freq = (NAME_WORD_FREQ && NAME_WORD_FREQ[w]) || 99;\n'
'        if (freq <= 2) rareBoost += 60;\n'
'        else if (freq <= 5) rareBoost += 25;\n'
'      } else if (hay.indexOf(w) > -1) hayHits++;\n'
'    }')
    if old in js:
        js = js.replace(old, new, 1)
        print("B. rare-word boost added")
        changed = True
    else:
        print("WARN B: scoreBiz loop not matched")

if "s += rareBoost" not in js:
    old = "s += nameHits * 15;\n    s += hayHits * 2;"
    new = "s += nameHits * 15;\n    s += hayHits * 2;\n    s += rareBoost;"
    if old in js:
        js = js.replace(old, new, 1)
        print("B2. rareBoost applied to score")
        changed = True
    else:
        print("WARN B2: score sum not matched")

# ============================================================
# FIX C: terms database + term check FIRST in buildExpertReply
# ============================================================
if "BRAIN_TERMS" not in js:
    terms_block = '''

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
'''
    anchor = "  function buildExpertReply"
    idx = js.find(anchor)
    if idx != -1:
        js = js[:idx] + terms_block + "\n\n" + js[idx:]
        print("C. BRAIN_TERMS dict inserted")
        changed = True
    else:
        print("WARN C: buildExpertReply anchor not found")

# ============================================================
# FIX D: check term FIRST inside buildExpertReply
# ============================================================
if "brainMatchTerm(query)" not in js:
    old = "      /* 1. Business search */"
    new = ('      /* 0. Term lookup (defined phrases FIRST) */\n'
'      var termHit = brainMatchTerm(query);\n'
'      if (termHit) {\n'
'        var def = BRAIN_TERMS[termHit];\n'
'        return ["\\uD83D\\uDCD8 " + termHit.charAt(0).toUpperCase() + termHit.slice(1) + ":\\n\\n" + def];\n'
'      }\n\n'
'      /* 1. Business search */')
    if old in js:
        js = js.replace(old, new, 1)
        print("D. buildExpertReply: term check moved FIRST")
        changed = True
    else:
        print("WARN D: business search comment not found")

# ============================================================
# Safe write — never truncate
# ============================================================
if changed:
    tmp = JS + ".tmp"
    with io.open(tmp, 'w', encoding='utf-8') as f:
        f.write(js)
    os.replace(tmp, JS)
    print("")
    print("SUCCESS. Brain tuning applied.")
else:
    print("")
    print("Nothing changed.")
