import io, sys, os

HTML = 'www/index.html'
P1 = 'tools/facts_pack_1.txt'
P2 = 'tools/facts_pack_2.txt'

if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)
if not os.path.exists(P1) or not os.path.exists(P2):
    print("ERROR: fact packs missing"); sys.exit(1)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__QUOTE_FACTS_BIG__" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

with io.open(P1, 'r', encoding='utf-8') as f:
    pack1 = f.read().rstrip().rstrip(',')
with io.open(P2, 'r', encoding='utf-8') as f:
    pack2 = f.read().rstrip().rstrip(',')

start = html.find("var EX_QUOTES = [")
if start == -1:
    print("ERROR: EX_QUOTES not found"); sys.exit(1)
close_idx = html.find("];", start)
if close_idx == -1:
    print("ERROR: closing ]; not found"); sys.exit(1)
last_brace = html.rfind("}", start, close_idx)
if last_brace == -1:
    print("ERROR: no entry inside array"); sys.exit(1)

INJECT = (",\n\n  /* __QUOTE_FACTS_BIG__ */\n  " + pack1 +
          ",\n  " + pack2 + "\n")

html = html[:last_brace+1] + INJECT + html[last_brace+1:]

tmp = HTML + ".tmp"
with io.open(tmp, 'w', encoding='utf-8') as f:
    f.write(html)
os.replace(tmp, HTML)

total = pack1.count("{i:") + pack2.count("{i:")
print("SUCCESS. " + str(total) + " new facts added to quote card.")
