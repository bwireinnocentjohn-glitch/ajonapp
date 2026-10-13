/* __VIEW_FEED_V1__ */
(function(){
  "use strict";
  if (window.__ajonViewFeed) return;
  window.__ajonViewFeed = true;

  var TOTAL_IMAGES = 89;
  var BATCH_SIZE   = 5;
  var CURRENT_MODE = "view";
  var LIKES_KEY    = "ajon_view_userlikes";
  var FAVS_KEY     = "ajon_view_favs";
  var INSTALL_KEY  = "ajon_view_install_t_v2";

  var LIKE_MIN     = 2000;
  var LIKE_MAX     = 59100;
  var LIKE_RANGE   = LIKE_MAX - LIKE_MIN;
  var GROWTH_PER_MIN = 500;

  function byId(id){ return document.getElementById(id); }

  var installT = 0;
  try { installT = Number(localStorage.getItem(INSTALL_KEY)) || 0; } catch(e){}
  if (!installT){
    installT = Date.now();
    try { localStorage.setItem(INSTALL_KEY, String(installT)); } catch(e){}
  }

  function hashOf(n){
    var x = ((n + 1) * 2654435761) >>> 0;
    x = (x ^ (x >>> 16)) >>> 0;
    x = Math.imul(x, 2246822519) >>> 0;
    x = (x ^ (x >>> 13)) >>> 0;
    return x;
  }
  function startLikes(idx){ return LIKE_MIN + (hashOf(idx) % (LIKE_RANGE + 1)); }
  function computeLikes(idx){
    var mins = Math.floor((Date.now() - installT) / 60000);
    return startLikes(idx) + mins * GROWTH_PER_MIN;
  }
  function fmtLikes(n){
    if (n >= 1000000) return (n/1000000).toFixed(1) + "M";
    if (n >= 1000)    return (n/1000).toFixed(1) + "k";
    return String(n);
  }
  function loadLiked(){ try { return JSON.parse(localStorage.getItem(LIKES_KEY)) || {}; } catch(e){ return {}; } }
  function saveLiked(o){ try { localStorage.setItem(LIKES_KEY, JSON.stringify(o)); } catch(e){} }
  function loadFavs(){ try { return JSON.parse(localStorage.getItem(FAVS_KEY)) || {}; } catch(e){ return {}; } }
  function saveFavs(o){ try { localStorage.setItem(FAVS_KEY, JSON.stringify(o)); } catch(e){} }

  function installStyles(){
    try {
      var old = byId("ajonViewFeedStyles");
      if (old) old.parentNode.removeChild(old);
      var s = document.createElement("style");
      s.id = "ajonViewFeedStyles";
      s.textContent =
        /* --- sub-tab chips --- */
        ".ajon-subtab-bar{display:flex;gap:8px;padding:10px 12px 8px;overflow-x:auto;scrollbar-width:none;}" +
        ".ajon-subtab-bar::-webkit-scrollbar{display:none;}" +
        ".ajon-subtab-btn{flex:0 0 auto;background:transparent;border:1px solid rgba(0,200,83,.35);color:#a7f3d0;font-size:13px;font-weight:800;letter-spacing:.3px;padding:8px 16px;border-radius:999px;cursor:pointer;font-family:inherit;transition:all .15s;}" +
        ".ajon-subtab-btn:active{transform:scale(.96);}" +
        ".ajon-subtab-btn.active{background:linear-gradient(135deg,#00c853,#00a844);color:#fff;border-color:#00a844;box-shadow:0 3px 12px rgba(0,200,83,.4);}" +

        /* --- feed container --- */
        "#ajonViewFeed{display:none;padding:6px 12px 24px;}" +
        "#ajonViewFeed.active{display:block;}" +

        /* --- card wrapper --- */
        ".ajon-view-item{margin-bottom:4px;border-radius:0;overflow:hidden;background:#000;box-shadow:0 3px 12px rgba(0,0,0,.55);border:1px solid rgba(0,200,83,.10);}" +

        /* --- 16:9 card via padding-bottom (universal support) --- */
        ".ajon-view-card{position:relative;width:100%;height:0;padding-bottom:56.25%;overflow:hidden;background:#000;border-radius:0;}" +
        ".ajon-view-card img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:cover;object-position:center;display:block;background:#000;" +
          "image-rendering:auto;transform:translateZ(0) scale(1.005);-webkit-backface-visibility:hidden;backface-visibility:hidden;will-change:transform;filter:contrast(1.04) saturate(1.06) brightness(1.01);}" +

        /* --- meta bar with neon line --- */
        ".ajon-view-meta{position:relative;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 14px;background:linear-gradient(180deg,#0a0a0a 0%,#050505 100%);}" +
        ".ajon-view-meta::before{content:'';position:absolute;top:0;left:12px;right:12px;height:2px;border-radius:2px;" +
          "background:linear-gradient(90deg,rgba(110,231,183,0) 0%,rgba(110,231,183,.75) 25%,rgba(52,211,153,1) 50%,rgba(110,231,183,.75) 75%,rgba(110,231,183,0) 100%);" +
          "box-shadow:0 0 8px rgba(52,211,153,.55),0 0 18px rgba(52,211,153,.25);}" +

        ".ajon-view-meta-left{display:flex;align-items:center;gap:9px;min-width:0;flex:1 1 auto;}" +
        ".ajon-view-meta-right{display:flex;align-items:center;gap:8px;flex:0 0 auto;}" +

        /* --- like button --- */
        ".ajon-view-like{width:32px;height:32px;border-radius:50%;background:rgba(0,200,83,.06);border:1px solid rgba(0,200,83,.22);color:#6ee7b7;" +
          "font-size:14px;line-height:1;padding:0;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;flex:0 0 auto;" +
          "transition:transform .12s,background .15s,box-shadow .25s;}" +
        ".ajon-view-like>span{display:block;line-height:1;transform:translateY(-.5px);}" +
        ".ajon-view-like:active{transform:scale(.9);}" +
        ".ajon-view-like.liked{background:rgba(255,82,82,.14);color:#ff5252;border-color:rgba(255,82,82,.42);box-shadow:0 0 14px rgba(255,82,82,.35);}" +

        /* --- count text: thin and premium --- */
        ".ajon-view-count{font-size:12.5px;font-weight:500;color:rgba(167,243,208,.82);letter-spacing:.35px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:inherit;}" +
        ".ajon-view-count b{color:#eafff5;font-weight:600;letter-spacing:.4px;}" +

        /* --- fav button --- */
        ".ajon-view-fav{width:32px;height:32px;border-radius:50%;background:rgba(255,183,77,.05);border:1px solid rgba(255,183,77,.22);color:rgba(255,183,77,.88);" +
          "font-size:13px;line-height:1;padding:0;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;flex:0 0 auto;" +
          "transition:transform .12s,background .15s,box-shadow .25s;}" +
        ".ajon-view-fav>span{display:block;line-height:1;transform:translateY(-.5px);}" +
        ".ajon-view-fav:active{transform:scale(.9);}" +
        ".ajon-view-fav.saved{background:rgba(255,183,77,.16);color:#ffb74d;border-color:rgba(255,183,77,.5);box-shadow:0 0 14px rgba(255,183,77,.35);}" +

        /* --- empty / sentinel / hot badge --- */
        ".ajon-view-empty{text-align:center;padding:60px 20px;color:#8aa;font-size:13px;line-height:1.6;}" +
        ".ajon-view-empty b{color:#a7f3d0;display:block;font-size:15px;margin-bottom:6px;}" +
        ".ajon-view-sentinel{height:12px;}" +
        ".ajon-view-badge{position:absolute;top:10px;left:10px;background:linear-gradient(135deg,#ff5252,#c62828);color:#fff;font-size:9.5px;font-weight:900;padding:3px 9px;border-radius:999px;letter-spacing:.6px;box-shadow:0 3px 12px rgba(255,82,82,.5);}";
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
        '<button class="ajon-subtab-btn active" data-mode="view" type="button">\uD83D\uDDBC View</button>' +
        '<button class="ajon-subtab-btn" data-mode="tutorials" type="button">\uD83D\uDCDA Tutorials</button>';

      panel.insertBefore(bar, panel.firstChild);

      var feed = document.createElement("div");
      feed.id = "ajonViewFeed";
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

  var currentObserver = null;

  function makeCard(idx){
    var wrap = document.createElement("div");
    wrap.className = "ajon-view-item";

    var card = document.createElement("div");
    card.className = "ajon-view-card";

    var img = document.createElement("img");
    img.loading = "lazy";
    img.decoding = "async";
    img.alt = "";
    img.onerror = function(){ try { wrap.style.display = "none"; } catch(e){} };
    img.src = "view/" + idx + ".webp";
    card.appendChild(img);

    if (startLikes(idx) > 48000){
      var badge = document.createElement("span");
      badge.className = "ajon-view-badge";
      badge.textContent = "\uD83D\uDD25 HOT";
      card.appendChild(badge);
    }

    var meta = document.createElement("div");
    meta.className = "ajon-view-meta";

    var left = document.createElement("div");
    left.className = "ajon-view-meta-left";

    var likeBtn = document.createElement("button");
    likeBtn.className = "ajon-view-like";
    likeBtn.type = "button";
    likeBtn.setAttribute("aria-label", "Like");
    var likeSpan = document.createElement("span");
    if (loadLiked()[idx]){ likeBtn.classList.add("liked"); likeSpan.textContent = "\u2764\uFE0F"; }
    else                  { likeSpan.textContent = "\uD83E\uDD0D"; }
    likeBtn.appendChild(likeSpan);

    var count = document.createElement("span");
    count.className = "ajon-view-count";
    function refreshCount(){
      var base = computeLikes(idx);
      if (loadLiked()[idx]) base += 1;
      count.innerHTML = "<b>" + fmtLikes(base) + "</b> likes";
    }
    refreshCount();

    likeBtn.onclick = function(ev){
      ev.stopPropagation(); ev.preventDefault();
      var s = loadLiked();
      if (s[idx]){ delete s[idx]; likeBtn.classList.remove("liked"); likeSpan.textContent = "\uD83E\uDD0D"; }
      else       { s[idx] = 1;    likeBtn.classList.add("liked");    likeSpan.textContent = "\u2764\uFE0F"; }
      saveLiked(s);
      refreshCount();
    };

    var right = document.createElement("div");
    right.className = "ajon-view-meta-right";

    var favBtn = document.createElement("button");
    favBtn.className = "ajon-view-fav";
    favBtn.type = "button";
    favBtn.setAttribute("aria-label", "Save");
    var favSpan = document.createElement("span");
    favSpan.textContent = "\u2B50";
    favBtn.appendChild(favSpan);
    if (loadFavs()[idx]) favBtn.classList.add("saved");
    favBtn.onclick = function(ev){
      ev.stopPropagation(); ev.preventDefault();
      var f = loadFavs();
      if (f[idx]){ delete f[idx]; favBtn.classList.remove("saved"); }
      else       { f[idx] = 1;    favBtn.classList.add("saved"); }
      saveFavs(f);
    };

    left.appendChild(likeBtn);
    left.appendChild(count);
    right.appendChild(favBtn);
    meta.appendChild(left);
    meta.appendChild(right);
    wrap.appendChild(card);
    wrap.appendChild(meta);
    return wrap;
  }

  function buildFeed(){
    try {
      var feed = byId("ajonViewFeed");
      if (!feed) return;
      if (TOTAL_IMAGES === 0){
        feed.innerHTML = '<div class="ajon-view-empty"><b>No images yet</b></div>';
        return;
      }
      var list = [];
      for (var i = 1; i <= TOTAL_IMAGES; i++) list.push(i);
      shuffle(list);

      if (currentObserver){ try { currentObserver.disconnect(); } catch(e){} currentObserver = null; }

      feed.innerHTML = "";
      var sentinel = document.createElement("div");
      sentinel.className = "ajon-view-sentinel";
      feed.appendChild(sentinel);

      var idx = 0;
      function loadBatch(){
        var end = Math.min(idx + BATCH_SIZE, list.length);
        for (var i = idx; i < end; i++) feed.insertBefore(makeCard(list[i]), sentinel);
        idx = end;
        if (idx >= list.length){
          try { if (sentinel.parentNode) sentinel.parentNode.removeChild(sentinel); } catch(e){}
          if (currentObserver){ try { currentObserver.disconnect(); } catch(e){} currentObserver = null; }
        }
      }
      loadBatch();
      try {
        currentObserver = new IntersectionObserver(function(entries){
          for (var i = 0; i < entries.length; i++) if (entries[i].isIntersecting) loadBatch();
        }, { rootMargin: "300px" });
        currentObserver.observe(sentinel);
      } catch(e){
        while (idx < list.length) loadBatch();
      }
    } catch(e){}
  }

  var tries = 0;
  function attempt(){
    tries++;
    installStyles();
    if (installSubTabBar()){
      setTimeout(function(){ setMode("view"); }, 200);
      try { console.log("[View Feed] installed - " + TOTAL_IMAGES + " images"); } catch(e){}
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
          setTimeout(function(){ installSubTabBar(); setMode(CURRENT_MODE); }, 120);
        }
      } catch(e){}
      return r;
    };
    wrappedShowTab._ajonViewFeed = true;
    window.showTab = wrappedShowTab;
  }
})();
