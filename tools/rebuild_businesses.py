import io, sys, os, glob, importlib.util

HTML = 'www/index.html'
BANKS_DIR = 'tools/banks'

if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
if not os.path.exists(BANKS_DIR):
    os.makedirs(BANKS_DIR)

all_businesses = []
bank_files = sorted(glob.glob(os.path.join(BANKS_DIR, 'bank_*.py')))
for bf in bank_files:
    name = os.path.basename(bf).replace('.py', '')
    spec = importlib.util.spec_from_file_location(name, bf)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    lst = getattr(mod, 'BUSINESSES', [])
    all_businesses.extend(lst)
    print("Loaded " + str(len(lst)) + " from " + name)

# Normalize every entry to exactly 17 fields
def normalize(b):
    b = tuple(b)
    if len(b) < 17:
        # Pad with sensible defaults
        defaults = ("Untitled", "💰", "food", 0, 0, "Varies", "Local markets",
                    "Local markets", "Business opportunity", "Materials from local market",
                    "Basic tools", "Research the market.", "Buy in bulk", "Don't rush",
                    "Slow~Better plan", "Local~Direct", "Start small today.")
        b = b + defaults[len(b):]
    return b[:17]

all_businesses = [normalize(b) for b in all_businesses]

print("Total: " + str(len(all_businesses)) + " businesses")

def esc(s):
    return str(s).replace("\\", "\\\\").replace('"', '\\"')

def to_js(b):
    b = normalize(b)
    fields = [esc(b[0]), esc(b[1]), esc(b[2]), str(b[3]), str(b[4]),
              esc(b[5]), esc(b[6]), esc(b[7]), esc(b[8]), esc(b[9]),
              esc(b[10]), esc(b[11]), esc(b[12]), esc(b[13]),
              esc(b[14]), esc(b[15]), esc(b[16])]
    return '["' + '","'.join(fields) + '"]'

entries = ",\n".join(to_js(b) for b in all_businesses)

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('var RAW_BUSINESSES = [')
if start == -1:
    print("ERROR: RAW_BUSINESSES not found"); sys.exit(1)
fn_idx = html.find('function expandBusiness', start)
if fn_idx == -1:
    print("ERROR: expandBusiness not found"); sys.exit(1)
end_arr = html.rfind('];', start, fn_idx)
if end_arr == -1:
    print("ERROR: closing ]; not found"); sys.exit(1)

new_array = 'var RAW_BUSINESSES = [\n' + entries + '\n];\n\n'
html = html[:start] + new_array + html[fn_idx:]

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS. Rebuilt index.html with " + str(len(all_businesses)) + " businesses.")
