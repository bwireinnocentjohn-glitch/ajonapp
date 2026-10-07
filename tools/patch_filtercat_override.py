import io, sys, os

HTML = 'www/index.html'
if not os.path.exists(HTML):
    print("ERROR: www/index.html not found"); sys.exit(1)
with io.open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

if "__ajonFilterOverrideV1" in html:
    print("Already applied. Exiting.")
    sys.exit(0)

OVERRIDE = r'''
/* ==========================================================
   filterCat — authoritative override
   Declared after all other scripts so it wins every time.
   ========================================================== */
(function(){
  if (window.__ajonFilterOverrideV1) return;
  window.__ajonFilterOverrideV1 = true;

  function safeRender() {
    try {
      var fn = window.renderTutorials;
      if (typeof fn === "function") { fn(true); return true; }
    } catch (e) {}
    return false;
  }

  function safeRenderFallback() {
    /* If renderTutorials is not global, try calling through the app's closure
       via a click on the search clear path — but safest is to just call it
       through window if available, else silently do nothing. */
    try {
      if (typeof renderTutorials === "function") { renderTutorials(true); return true; }
    } catch (e) {}
    return false;
  }

  window.filterCat = function(cat) {
    try {
      cat = String(cat == null ? "all" : cat).toLowerCase();
      /* Validate against known categories if CATEGORIES exists */
      try {
        if (typeof CATEGORIES !== "undefined" && cat !== "all") {
          var ok = false;
          for (var k = 0; k < CATEGORIES.length; k++) {
            if (CATEGORIES[k].id === cat) { ok = true; break; }
          }
          if (!ok) cat = "all";
        }
      } catch(e) {}

      /* Set currentCategory if the variable is accessible */
      try { currentCategory = cat; } catch(e) {}

      /* Update chip active classes */
      var chips = document.querySelectorAll(".cat-chip");
      for (var i = 0; i < chips.length; i++) {
        if (chips[i].getAttribute("data-cat") === cat) chips[i].classList.add("active");
        else chips[i].classList.remove("active");
      }

      /* Reset scroll offset if accessible */
      try { tutOffset = 0; } catch(e) {}
      try { currentItems = []; } catch(e) {}

      /* Re-render */
      var done = safeRender();
      if (!done) safeRenderFallback();
    } catch (e) {
      try { console.log("filterCat override error:", e); } catch(x) {}
    }
  };

  /* Rebind existing chips on load */
  function rebind() {
    try {
      var chips = document.querySelectorAll(".cat-chip");
      for (var i = 0; i < chips.length; i++) {
        (function(chip){
          chip.onclick = function(ev){
            if (ev) { ev.preventDefault(); ev.stopPropagation(); }
            var c = chip.getAttribute("data-cat");
            if (c) window.filterCat(c);
            return false;
          };
        })(chips[i]);
      }
    } catch(e) {}
  }

  if (document.readyState === "complete") {
    setTimeout(rebind, 500);
  } else {
    window.addEventListener("load", function(){ setTimeout(rebind, 500); });
  }
})();
'''

idx = html.rfind('</script>')
if idx == -1:
    print("ERR: </script> not found"); sys.exit(1)
html = html[:idx] + OVERRIDE + '\n' + html[idx:]

with io.open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print("SUCCESS. filterCat override installed.")
