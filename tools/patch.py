import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: " + HTML + " not found. Run from ~/ajon-app")
    sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f: html = f.read()
with io.open('tools/style.css', 'r', encoding='utf-8') as f: css_add = f.read()
with io.open('tools/brain.js', 'r', encoding='utf-8') as f: brain_js = f.read()

# ---- 1. Replace panel-chat section ----
start = html.find('<section class="panel" id="panel-chat">')
if start == -1:
    print("ERROR: panel-chat not found"); sys.exit(1)
end = html.find('</section>', start)
if end == -1:
    print("ERROR: closing </section> not found"); sys.exit(1)
end += len('</section>')

new_panel = '''<section class="panel" id="panel-chat">
      <div class="chat-header-bar">
        <div class="chat-avatars">
          <span class="chat-ava ajon-ava"><img src="images/ajon-avatar.webp" alt="" onerror="this.style.display='none';this.parentNode.textContent='\\U0001F9D1\\U0001F3FE\\u200D\\U0001F3EB';"></span>
          <span class="chat-ava pasie-ava"><img src="images/pasie-avatar.webp" alt="" onerror="this.style.display='none';this.parentNode.textContent='\\U0001F9D1\\U0001F3FE\\u200D\\U0001F33E';"></span>
        </div>
        <div class="chat-header-info">
          <div class="chat-title">Mzee Ajon <span class="live-pulse">\\u25CF</span> Live</div>
          <div class="chat-subtitle">Teaching Pasie from Busia</div>
        </div>
        <button id="soundToggleBtn" class="chat-hdr-btn" onclick="toggleAssistSound()" title="Sound on/off">\\U0001F50A</button>
        <button class="chat-hdr-btn" onclick="clearAssistantChat()" title="Clear chat">\\U0001F5D1\\uFE0F</button>
      </div>
      <div class="chat-msgs" id="assistMsgs"></div>
    </section>'''

html = html[:start] + new_panel + html[end:]
print("1. Panel-chat replaced.")

# ---- 2. Inject CSS before </style> ----
idx = html.rfind('</style>')
if idx == -1: print("ERROR: </style> not found"); sys.exit(1)
html = html[:idx] + css_add + '\n' + html[idx:]
print("2. CSS injected.")

# ---- 3. Inject brain JS before last </script> ----
idx = html.rfind('</script>')
if idx == -1: print("ERROR: </script> not found"); sys.exit(1)
html = html[:idx] + '\n' + brain_js + '\n' + html[idx:]
print("3. Brain JS injected.")

# ---- 4. Patch showTab to pause/open assistant ----
old_show = '''  if (name === "tutorials") { tutOffset = 0; renderTutorials(true); }
  if (name === "video") renderPayment();
  if (name === "notes") renderNotes();
  if (name === "ai") { updateNet(); var inp = byId("aiInput"); if (inp) setTimeout(function () { try { inp.focus(); } catch (e) {} }, 50); }'''

new_show = '''  if (name === "tutorials") { pauseAssistantChat(); tutOffset = 0; renderTutorials(true); }
  else if (name === "video") { pauseAssistantChat(); renderPayment(); }
  else if (name === "notes") { pauseAssistantChat(); renderNotes(); }
  else if (name === "ai") { pauseAssistantChat(); updateNet(); var inp = byId("aiInput"); if (inp) setTimeout(function () { try { inp.focus(); } catch (e) {} }, 50); }
  else if (name === "chat") { setTimeout(function () { openAssistantTab(); }, 200); }'''

if old_show in html:
    html = html.replace(old_show, new_show, 1)
    print("4. showTab patched.")
else:
    print("4. WARNING: showTab block not found. Trying looser match...")
    marker = 'if (name === "tutorials") { tutOffset = 0; renderTutorials(true); }'
    if marker in html:
        html = html.replace(
            marker,
            'if (name === "tutorials") { pauseAssistantChat(); tutOffset = 0; renderTutorials(true); }',
            1)
        marker2 = 'if (name === "ai") { updateNet(); var inp = byId("aiInput"); if (inp) setTimeout(function () { try { inp.focus(); } catch (e) {} }, 50); }'
        if marker2 in html:
            html = html.replace(
                marker2,
                marker2 + '\n  else if (name === "chat") { setTimeout(function () { openAssistantTab(); }, 200); }',
                1)
        print("4. showTab patched (loose).")
    else:
        print("4. FATAL: could not patch showTab.")

# ---- 5. Patch boot to load brain state ----
old_boot = '''    TUTORIALS = ALL_BUSINESSES;
    renderCatBar();'''
new_boot = '''    TUTORIALS = ALL_BUSINESSES;
    loadBrainState();
    renderCatBar();'''
if old_boot in html:
    html = html.replace(old_boot, new_boot, 1)
    print("5. boot patched.")
else:
    print("5. WARNING: boot block not found.")

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("")
print("SUCCESS. www/index.html is now patched.")
