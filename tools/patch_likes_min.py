import io, sys, os

HTML = 'www/index.html'
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__LIKES_MIN__" in html:
    print("Already applied."); sys.exit(0)

# Sanity: abort if main app functions missing
for fn in ["function boot(", "hideSplash", "renderTutorials"]:
    if fn not in html:
        print("ERROR: " + fn + " missing - abort"); sys.exit(1)

INJECT = (
"<style>\n"
".likes-badge { display: inline-flex; align-items: center; gap: 4px; "
"background: rgba(0,200,83,.1); border: 1px solid rgba(0,200,83,.35); "
"color: #00c853; border-radius: 999px; padding: 3px 10px; font-size: 11px; "
"font-weight: 800; margin: 4px 0 8px; letter-spacing: .3px; }\n"
"</style>\n"
"<script>\n"
"/* __LIKES_MIN__ */\n"
"(function(){\n"
"try {\n"
"  var installTime = Number(localStorage.getItem('ajon_likes_t')) || Date.now();\n"
"  localStorage.setItem('ajon_likes_t', String(installTime));\n"
"  function upd(){\n"
"    var cards = document.querySelectorAll('.card');\n"
"    for (var i = 0; i < cards.length; i++){\n"
"      var card = cards[i];\n"
"      var title = card.querySelector('.card-title');\n"
"      if (!title) continue;\n"
"      var t = title.textContent.trim();\n"
"      var h = 0;\n"
"      for (var j = 0; j < t.length; j++){ h = ((h<<5)-h)+t.charCodeAt(j); h |= 0; }\n"
"      h = Math.abs(h);\n"
"      var base = 10000 + (h % 10000);\n"
"      var rate = 20000 + (h % 50000);\n"
"      var hours = (Date.now() - installTime) / 3600000;\n"
"      var likes = base + Math.floor(hours * rate);\n"
"      var txt = '\u2764\uFE0F ' + (likes >= 1000 ? (likes/1000).toFixed(1)+'k' : String(likes)) + ' likes';\n"
"      var ex = card.querySelector('.likes-badge');\n"
"      if (ex) { ex.textContent = txt; continue; }\n"
"      var badge = document.createElement('div');\n"
"      badge.className = 'likes-badge';\n"
"      badge.textContent = txt;\n"
"      var chip = card.querySelector('.chip');\n"
"      if (chip && chip.parentNode === card) chip.parentNode.insertBefore(badge, chip.nextSibling);\n"
"      else title.parentNode.insertBefore(badge, title.nextSibling);\n"
"    }\n"
"  }\n"
"  setInterval(upd, 3000);\n"
"  upd();\n"
"} catch(e) { console.log('likes min err', e); }\n"
"})();\n"
"</script>\n"
)

if "</body>" not in html:
    print("ERROR: </body> missing"); sys.exit(1)

html = html.replace("</body>", INJECT + "</body>", 1)

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)
print("SUCCESS. Likes badge added.")
