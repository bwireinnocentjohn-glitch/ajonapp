import io, sys, os

JS = 'www/js/expertBrain.js'
HTML = 'www/index.html'

if not os.path.exists(JS):
    print("ERROR: expertBrain.js not found"); sys.exit(1)
if not os.path.exists(HTML):
    print("ERROR: index.html not found"); sys.exit(1)

with io.open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. Replace suggestion pool in exRenderSuggestions inside index.html
# ============================================================
NEW_POOL_START = 'var pool = ['
NEW_POOL_END = '];'

if "how do I start fish farming?" in html and "how do I make herbal soap?" not in html:
    start = html.find(NEW_POOL_START, html.find("function exRenderSuggestions"))
    if start != -1:
        end = html.find(NEW_POOL_END, start) + 2
        NEW_POOL = '''var pool = [
    "how do I make liquid soap?",
    "how do I make herbal soap?",
    "how do I make neem soap?",
    "how do I make aloe vera soap?",
    "how do I make black soap?",
    "how do I make turmeric soap?",
    "how do I make charcoal soap?",
    "how do I make bar soap?",
    "how do I make detergent powder?",
    "how do I make bleach?",
    "how do I make toilet cleaner?",
    "how do I make floor cleaner?",
    "how do I make dish soap?",
    "how do I make air freshener?",
    "how do I make candles?",
    "how do I make beeswax candles?",
    "how do I make charcoal briquettes?",
    "how do I make sawdust briquettes?",
    "how do I make coconut shell charcoal?",
    "how do I make banana peel briquettes?",
    "how do I grow mushrooms?",
    "how do I start cricket farming?",
    "how do I start bee farming?",
    "how do I start stingless bee farming?",
    "how do I make bee pollen?",
    "how do I make propolis?",
    "how do I make beehive?",
    "how do I make beeswax lip balm?",
    "how do I make beeswax food wraps?",
    "how do I make recycled paper?",
    "how do I make paper from old books?",
    "how do I make banana fibre paper?",
    "how do I make papyrus pads?",
    "how do I make jeans bags?",
    "how do I make denim wallets?",
    "how do I make denim aprons?",
    "how do I make t-shirt rugs?",
    "how do I make patchwork clothes?",
    "how do I recycle glass bottles?",
    "how do I make glass tumblers?",
    "how do I make glass lamps?",
    "how do I make glass vases?",
    "how do I make glass jewellery?",
    "how do I make plastic pavers?",
    "how do I make plastic tiles?",
    "how do I make plastic bricks?",
    "how do I make plastic fence posts?",
    "how do I make interlocking bricks?",
    "how do I make compressed earth blocks?",
    "how do I make clay stove?",
    "how do I make rocket stove?",
    "how do I make solar cooker?",
    "how do I make solar water heater?",
    "how do I make solar phone charger?",
    "how do I make bicycle charger?",
    "how do I make pedal washing machine?",
    "how do I make pedal water pump?",
    "how do I make biogas?",
    "how do I make compost?",
    "how do I make vermicompost?",
    "how do I make BSF frass?",
    "how do I make neem pesticide?",
    "how do I make tephrosia pesticide?",
    "how do I make wood ash pesticide?",
    "how do I make banana liquid fertilizer?",
    "how do I make bone meal?",
    "how do I make ceramic water filter?",
    "how do I make clay water filter?",
    "how do I make moringa water purifier?",
    "how do I make fruit jam?",
    "how do I make tomato sauce?",
    "how do I make chilli sauce?",
    "how do I make honey?",
    "how do I make coffee?",
    "how do I make chocolate?",
    "how do I make peanut butter?",
    "how do I make yoghurt?",
    "how do I make cheese?",
    "how do I make bread?",
    "how do I make cakes?",
    "how do I make cupcakes?",
    "how do I make muffins?",
    "how do I make samosa?",
    "how do I make chapati?",
    "how do I make rolex?",
    "how do I make chips?",
    "how do I make mandazi?",
    "how do I make popcorn?",
    "what is cash flow?",
    "what is profit margin?",
    "what is break-even?",
    "what is a KPI?",
    "what is caustic soda?",
    "what is BSF?",
    "what is CAC?",
    "what is LTV?",
    "give me a business idea",
    "how do I save money?",
    "how do I price my product?",
    "how do I get customers?",
    "how do I advertise?",
    "should I hire a worker?",
    "how do I beat competition?",
    "should I keep records?",
    "how do I stay disciplined?",
    "I am scared to start",
    "I failed at business",
    "motivate me",
    "tell me a joke",
    "tell me a fact",
    "share a bible verse"
];'''
        html = html[:start] + NEW_POOL + html[end:]
        print("1. Suggestion pool expanded with eco-friendly + all categories")
    else:
        print("WARN: suggestion pool start not found")
elif "how do I make herbal soap?" in html:
    print("1. Eco suggestions already present")
else:
    print("WARN: pattern not matched")

# ============================================================
# 2. Boost search to include category names for eco keywords
# ============================================================
OLD_MATCH = "var hay = (biz.name + \" \" + biz.category + \" \" + biz.whyNow2026 + \" \" + (biz.tags||[]).join(\" \")).toLowerCase();"
NEW_MATCH = "var hay = (biz.name + \" \" + biz.category + \" \" + (biz.whyNow||biz.whyNow2026||\"\") + \" \" + (biz.tags||[]).join(\" \")).toLowerCase();"

if OLD_MATCH in js:
    js = js.replace(OLD_MATCH, NEW_MATCH, 1)
    print("2. Search haystack updated (whyNow or whyNow2026)")
else:
    print("2. Search haystack already safe")

with io.open(JS, 'w', encoding='utf-8') as f:
    f.write(js)
with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("")
print("SUCCESS. Final wrap patch applied.")
