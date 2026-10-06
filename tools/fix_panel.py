import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<section class="panel" id="panel-chat">')
if start == -1:
    print("ERROR: panel-chat not found"); sys.exit(1)
end = html.find('</section>', start)
if end == -1:
    print("ERROR: closing </section> not found"); sys.exit(1)
end += len('</section>')

# Single-backslash escapes -> Python writes real unicode chars to the file
new_panel = '''<section class="panel" id="panel-chat">
      <div class="chat-header-bar">
        <div class="chat-avatars">
          <span class="chat-ava ajon-ava"><img src="images/ajon-avatar.webp" alt="" onerror="this.style.display='none';this.parentNode.textContent='\U0001F9D1\U0001F3FE\u200D\U0001F3EB';"></span>
          <span class="chat-ava pasie-ava"><img src="images/pasie-avatar.webp" alt="" onerror="this.style.display='none';this.parentNode.textContent='\U0001F9D1\U0001F3FE\u200D\U0001F33E';"></span>
        </div>
        <div class="chat-header-info">
          <div class="chat-title">Mzee Ajon <span class="live-pulse">\u25CF</span> Live</div>
          <div class="chat-subtitle">Teaching Pasie from Busia</div>
        </div>
        <button id="soundToggleBtn" class="chat-hdr-btn" onclick="toggleAssistSound()" title="Sound on/off">\U0001F50A</button>
        <button class="chat-hdr-btn" onclick="clearAssistantChat()" title="Clear chat">\U0001F5D1\uFE0F</button>
      </div>
      <div class="chat-msgs" id="assistMsgs"></div>
    </section>'''

html = html[:start] + new_panel + html[end:]

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print("DONE. Panel header fixed with real unicode characters.")
