/* __VIEW_FEED_V1__ */
(function(){
  "use strict";
  if (window.__ajonViewFeed) return;
  window.__ajonViewFeed = true;

  var MAX_IMAGES = 200;
  var STOP_AFTER_MISSES = 5;
  var CURRENT_MODE = "view";

  function byId(id){ return document.getElementById(id); }

  function installStyles(){
    try {
      if (byId("ajonViewFeedStyles")) return;
      var s = document.createElement("style");
      s.id = "ajonViewFeedStyles";
      s.textContent =
        ".ajon-subtab-bar{display:flex;gap:8px;padding:10px 12px 4px;overflow-x:auto;scrollbar-width:none;}" +
        ".ajon-subtab-bar::-webkit-scrollbar{display:none;}" +
        ".ajon-subtab-btn{flex:0 0 auto;background:transparent;border:1px solid rgba(0,200,83,.35);color:#a7f3d0;font-size:13px;font-weight:800;letter-spacing:.3px;padding:8px 16px;border-radius:999px;cursor:pointer;font-family:inherit;transition:all .15s;}" +
        ".ajon-subtab-btn:active{transform:scale(.96);}" +
        ".ajon-subtab-btn.active{background:linear-gradient(135deg,#00c853,#00a844);color:#fff;border-color:#00a844;box-shadow:0 3px 12px rgba(0,200,83,.4);}" +
        "#ajonViewFeed{display:none;padding:8px 12px 24px;}" +
        "#ajonViewFeed.active{display:block;}" +
        ".ajon-view-card{background:#000;border:0;border-radius:12px;overflow:hidden;margin-bottom:14px;box-shadow:0 4px 14px rgba(0,0,0,.7);position:relative;aspect-ratio:16/9;}" +
        ".ajon-view-card img{width:100%;height:100%;object-fit:cover;display:block;background:#000;}" +
        ".ajon-view-empty{text-align:center;padding:60px 20px;color:#8aa;font-size:13px;line-height:1.6;}" +
        ".ajon-view-empty b{color:#a7f3d0;display:block;font-size:15px;margin-bottom:6px;}";
      document.head.appendChild(s);
    } catch(e){}
  }

  function installSubTabBar(){
    try {
      var panel = byId("panel-tutorials");
      if (!panel) return false;
      if (panel.querySelector(".ajon-subtab-bar")) return true;

      var bar = document.createElement("div");
      bar.className = "ajon-subtab-bar";
      bar.id = "ajonSubTabBar";
      bar.innerHTML =
        '<button class="ajon-subtab-btn active" data-mode="view" type="button">\uD83D\uDDBC See</button>' +
        '<button class="ajon-subtab-btn" data-mode="tutorials" type="button">\uD83D\uDCDA Tutorials</button>';

      panel.insertBefore(bar, panel.firstChild);

      var feed = document.createElement("div");
      feed.id = "ajonViewFeed";
      feed.innerHTML = '<div class="ajon-view-empty"><b>Loading images...</b>They will appear here shortly.</div>';
      panel.insertBefore(feed, bar.nextSibling);

      var btns = bar.querySelectorAll(".ajon-subtab-btn");
      for (var i=0; i<btns.length; i++){
        (function(b){
          b.onclick = function(ev){
            ev.preventDefault(); ev.stopPropagation();
            setMode(b.getAttribute("data-mode"));
          };
        })(btns[i]);
      }
      return true;
    } catch(e){ return false; }
  }

  function setMode(mode){
    try {
      CURRENT_MODE = mode;
      var panel = byId("panel-tutorials");
      if (!panel) return;

      var btns = panel.querySelectorAll(".ajon-subtab-btn");
      for (var i=0; i<btns.length; i++){
        btns[i].classList.toggle("active", btns[i].getAttribute("data-mode") === mode);
      }

      var feed = byId("ajonViewFeed");
      if (feed) feed.classList.toggle("active", mode === "view");

      var kids = panel.children;
      for (var k=0; k<kids.length; k++){
        var el = kids[k];
        if (el.id === "ajonSubTabBar") continue;
        if (el.id === "ajonViewFeed") continue;
        if (mode === "view"){
          el.setAttribute("data-ajon-hidden", "1");
          el.style.display = "none";
        } else {
          if (el.getAttribute("data-ajon-hidden") === "1"){
            el.style.display = "";
            el.removeAttribute("data-ajon-hidden");
          }
        }
      }

      if (mode === "view") buildFeed();
    } catch(e){}
  }

  function shuffle(arr){
    for (var i = arr.length - 1; i > 0; i--){
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
    return arr;
  }

  function detectImages(){
    return new Promise(function(resolve){
      var found = [];
      var misses = 0;
      var i = 1;
      function next(){
        if (i > MAX_IMAGES || misses >= STOP_AFTER_MISSES) return resolve(found);
        var url = "view/" + i + ".webp";
        var img = new Image();
        img.onload = function(){ found.push(url); misses = 0; i++; next(); };
        img.onerror = function(){ misses++; i++; next(); };
        img.src = url;
      }
      next();
    });
  }

  var cachedList = null;

  function buildFeed(){
    try {
      var feed = byId("ajonViewFeed");
      if (!feed) return;

      if (cachedList && cachedList.length){
        renderList(feed, cachedList);
        return;
      }

      feed.innerHTML = '<div class="ajon-view-empty"><b>Loading images...</b>They will appear here shortly.</div>';
      detectImages().then(function(list){
        cachedList = list;
        renderList(feed, list);
      }).catch(function(){
        feed.innerHTML = '<div class="ajon-view-empty"><b>No images found</b></div>';
      });
    } catch(e){}
  }

  function renderList(feed, list){
    if (!list.length){
      feed.innerHTML = '<div class="ajon-view-empty"><b>No images yet</b></div>';
      return;
    }
    var ordered = shuffle(list.slice());
    var html = "";
    for (var i=0; i<ordered.length; i++){
      html += '<div class="ajon-view-card"><img loading="lazy" decoding="async" src="' + ordered[i] + '" alt=""></div>';
    }
    feed.innerHTML = html;
  }

  var tries = 0;
  function attempt(){
    tries++;
    installStyles();
    if (installSubTabBar()){
      setTimeout(function(){ setMode("view"); }, 200);
      try { console.log("[View Feed] installed"); } catch(e){}
      return;
    }
    if (tries < 30) setTimeout(attempt, 500);
  }

  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", function(){ setTimeout(attempt, 900); });
  } else {
    setTimeout(attempt, 900);
  }

  if (typeof window.showTab === "function" && !window.showTab._ajonViewFeed){
    var origShowTab = window.showTab;
    var wrappedShowTab = function(name){
      var r = origShowTab.apply(this, arguments);
      try {
        if (name === "tutorials"){
          setTimeout(function(){
            installSubTabBar();
            setMode(CURRENT_MODE);
          }, 120);
        }
      } catch(e){}
      return r;
    };
    wrappedShowTab._ajonViewFeed = true;
    window.showTab = wrappedShowTab;
  }
})();
