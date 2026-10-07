import io, sys, os

HTML = 'www/index.html'
JS = 'www/js/expertBrain.js'

if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()
with io.open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

SMILE = chr(0x1F642)  # 🙂  — built at runtime, no escape issues

# ============================================================
# 1. Hardwire askExpert to try buildExpertReply FIRST
# ============================================================
OLD = '''setTimeout(function(){
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      var replies = exComposeReply(q);
      var idx = 0;'''

NEW = ('setTimeout(function(){\n'
'      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);\n'
'      var replies = null;\n'
'      try {\n'
'        if (typeof window.buildExpertReply === "function") {\n'
'          replies = window.buildExpertReply(q);\n'
'        }\n'
'      } catch(e) { try{console.log("[Expert] brain error:", e);}catch(x){} }\n'
'      if (!replies || !replies.length) {\n'
'        try { replies = exComposeReply(q); }\n'
'        catch(e) { replies = ["I am here. ' + SMILE + ' Please try again."]; }\n'
'      }\n'
'      var idx = 0;')

if OLD in html:
    html = html.replace(OLD, NEW, 1)
    print("1. askExpert hardwired to buildExpertReply")
elif 'window.buildExpertReply' in html:
    print("1. Already hardwired")
else:
    print("WARN: askExpert block not found")

# ============================================================
# 2. Score boost + stopFilter in expertBrain.js
# ============================================================
if "SCORE_BOOST_V2" not in js:
    OLD_SCORE = 'if (nameLow.length >= 4 && q.indexOf(nameLow) > -1) s += 80;'
    NEW_SCORE = ('if (nameLow.length >= 4 && q.indexOf(nameLow) > -1) s += 80;\n\n'
'    /* SCORE_BOOST_V2 — query-side phrase priority */\n'
'    if (words.length >= 1) {\n'
'      var nameTokens = nameLow.split(/[^a-z0-9]+/).filter(function(t){ return t.length >= 3; });\n'
'      var qSet = {};\n'
'      for (var k = 0; k < words.length; k++) qSet[words[k]] = 1;\n'
'      var nameMatched = 0;\n'
'      for (var n = 0; n < nameTokens.length; n++) {\n'
'        if (qSet[nameTokens[n]] || q.indexOf(nameTokens[n]) > -1) nameMatched++;\n'
'      }\n'
'      if (nameTokens.length > 0 && nameMatched === nameTokens.length) s += 40;\n'
'      else s += nameMatched * 5;\n'
'    }')

    if OLD_SCORE in js:
        js = js.replace(OLD_SCORE, NEW_SCORE, 1)
        print("2. scoreBiz boosted")
    else:
        print("WARN: scoreBiz line not found")

if "STOPS_V2" not in js and "STOPS " not in js:
    insert_after = "function norm(t){"
    idx = js.find(insert_after)
    if idx != -1:
        brace = js.find('{', idx)
        depth = 0; i = brace
        while i < len(js):
            ch = js[i]
            if ch == '{': depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1; break
            i += 1
        stop_fn = ('\n\n'
'  var STOPS_V2 = {"how":1,"do":1,"what":1,"is":1,"the":1,"a":1,"an":1,"can":1,'
'"i":1,"my":1,"me":1,"you":1,"we":1,"they":1,"he":1,"she":1,'
'"to":1,"for":1,"of":1,"in":1,"on":1,"at":1,"by":1,"with":1,'
'"and":1,"or":1,"but":1,"if":1,"so":1,"this":1,"that":1,"these":1,"those":1,'
'"it":1,"its":1,"be":1,"am":1,"are":1,"was":1,"were":1,"been":1,'
'"make":1,"makes":1,"making":1,"made":1,'
'"start":1,"starts":1,"starting":1,'
'"want":1,"wants":1,"need":1,"needs":1,'
'"give":1,"gives":1,"get":1,"gets":1,'
'"help":1,"please":1,"tell":1,"show":1,"teach":1,"explain":1,'
'"about":1,"from":1,"into":1,"than":1,"then":1,'
'"any":1,"all":1,"some":1,"more":1,"most":1,'
'"good":1,"best":1,"great":1,"nice":1};\n\n'
'  function stopFilter(s){\n'
'    return String(s||"").split(" ").filter(function(w){\n'
'      return w.length >= 2 && !STOPS_V2[w];\n'
'    });\n'
'  }\n')
        js = js[:end] + stop_fn + js[end:]
        print("2b. stopFilter added")
    else:
        print("WARN: norm function not found")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
with io.open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

print("")
print("SUCCESS. Expert hardwire applied.")
