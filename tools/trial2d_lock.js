/* __TRIAL2D_LOCK_V1__ */
(function(){
  "use strict";
  if (window.__ajonTrial2dLock) return;
  window.__ajonTrial2dLock = true;

  var LS_2D_STARTED = "ajon_trial2d_startedAt";
  var LS_2D_EXPIRES = "ajon_trial2d_expiresAt";
  var LS_2D_USED    = "ajon_trial2d_used";
  var TRIAL_HOURS   = 48;

  function byId(id){ return document.getElementById(id); }
  function now(){ return Date.now(); }

  /* 2-DAY FORMULA — same "aj" prefix + same letters. Only numeric is different (smaller). */
  function generateCurrentPassword2d(){
    var d = new Date();
    var Year = d.getFullYear();
    var Month = d.getMonth();
    var Day = d.getDate();
    var Hour = d.getHours();
    if (Year < 2026) return null;
    var MonthIndex = (Year - 2026) * 12 + Month;
    if (MonthIndex < 0) return null;
    var DayIdx  = MonthIndex * 31 + Day;
    var HourIdx = DayIdx * 24 + Hour;
    var Num = 1500 + HourIdx * 17 + 33 * 7;   /* 1731 + 17*hour — never collides with 30-day */
    var L1 = String.fromCharCode(97 + ((Year - 2026) % 26));
    var L2 = String.fromCharCode(97 + (Month % 26));
    var L3 = String.fromCharCode(97 + (Day % 26));
    var L4 = String.fromCharCode(97 + Hour);
    var Last = (HourIdx * 7 + Year % 10) % 9 + 1;
    return ("aj" + Num + L1 + L2 + L3 + L4 + Last).toLowerCase();
  }
  window.generateCurrentPassword2d = generateCurrentPassword2d;

  function has30Day(){
    try {
      var e = Number(
        localStorage.getItem("ajon_sub_end_v12") ||
        localStorage.getItem("ajon_sub_end_v11") ||
        localStorage.getItem("ajon_sub_end_v10") ||
        localStorage.getItem("ajon_sub_end_v9") || 0
      );
      return e > now();
    } catch(err){ return false; }
  }
  function has2Day(){
    try { return Number(localStorage.getItem(LS_2D_EXPIRES) || 0) > now(); }
    catch(err){ return false; }
  }
  function trialUsed(){
    try { return localStorage.getItem(LS_2D_USED) === "true"; } catch(err){ return false; }
  }
  function shouldLock(){
    return !has30Day() && !has2Day() && trialUsed();
  }
  function wipeTrialKeys(){
    try { localStorage.removeItem(LS_2D_STARTED); } catch(e){}
    try { localStorage.removeItem(LS_2D_EXPIRES); } catch(e){}
    try { localStorage.removeItem(LS_2D_USED);    } catch(e){}
  }
  window.__ajonWipeTrialKeys = wipeTrialKeys;

  /* ---------- LOCK OVERLAY ---------- */
  var lockEl = null;
  function buildLock(){
    var el = document.createElement("div");
    el.id = "ajonTrial2dLock";
    el.style.cssText =
      "position:fixed;top:0;left:0;right:0;bottom:0;background:#000;" +
      "z-index:2147483645;display:none;align-items:center;justify-content:center;" +
      "flex-direction:column;gap:22px;padding:24px;text-align:center;font-family:inherit;";
    el.innerHTML =
      '<div style="font-size:80px;line-height:1;filter:drop-shadow(0 0 18px rgba(52,211,153,.5));">\uD83D\uDD12</div>' +
      '<div style="color:#fff;font-size:22px;font-weight:900;letter-spacing:.4px;">Your Trial Has Ended</div>' +
      '<div style="color:#8aa;font-size:14px;max-width:320px;line-height:1.6;">Your 2-day trial has expired. Tap below to unlock full access.</div>' +
      '<button id="ajonTrial2dGo" type="button" style="background:linear-gradient(135deg,#a7f3d0,#34d399);color:#052e16;border:0;border-radius:999px;padding:15px 28px;font-size:15px;font-weight:900;letter-spacing:.4px;cursor:pointer;box-shadow:0 6px 22px rgba(52,211,153,.5);font-family:inherit;">\uD83D\uDD13 Go to Unlock Tab</button>';
    document.body.appendChild(el);
    var go = el.querySelector("#ajonTrial2dGo");
    if (go) go.onclick = function(ev){
      ev.stopPropagation(); ev.preventDefault();
      try { if (typeof showTab === "function") showTab("video"); } catch(e){}
      hideLock();
    };
    return el;
  }
  function showLock(){
    try {
      if (!lockEl) lockEl = buildLock();
      if (lockEl) lockEl.style.display = "flex";
    } catch(e){}
  }
  function hideLock(){
    try { if (lockEl) lockEl.style.display = "none"; } catch(e){}
  }
  function currentPanelId(){
    try { var p = document.querySelector(".panel.active"); return p ? p.id : ""; }
    catch(e){ return ""; }
  }
  function refreshLock(){
    try {
      if (!shouldLock()){ hideLock(); return; }
      if (currentPanelId() === "panel-video") hideLock();
      else showLock();
    } catch(e){}
  }

  /* ---------- VERIFY PASSWORD OVERRIDE ---------- */
  function installVerify(){
    if (typeof window.verifyPassword !== "function") return false;
    if (window.verifyPassword._ajon2d) return true;
    var orig = window.verifyPassword;
    var wrapped = function(){
      try {
        var input = byId("txInput");
        var status = byId("statusMsg");
        if (!input || !status) return orig.apply(this, arguments);
        var entered = String(input.value || "").trim().toLowerCase();
        if (!entered) return orig.apply(this, arguments);
        if (typeof isDateValid === "function" && !isDateValid()){
          status.className = "err";
          status.textContent = "Set automatic date and time first.";
          return;
        }
        var exp30 = (typeof generateCurrentPassword === "function") ? generateCurrentPassword() : null;
        var exp2d = generateCurrentPassword2d();

        /* 30-day FIRST — if match, wipe trial keys (never lock a 30-day user) */
        if (exp30 && entered === exp30){
          wipeTrialKeys();
          hideLock();
          try { setTimeout(refreshLock, 300); } catch(e){}
          return orig.apply(this, arguments);
        }

        /* 2-day SECOND */
        if (exp2d && entered === exp2d){
          try {
            if (localStorage.getItem(LS_2D_USED) === "true"){
              status.className = "err";
              status.textContent = "2-day trial already used on this phone.";
              return;
            }
          } catch(e){}
          try {
            if (typeof usedPasswords !== "undefined" && Array.isArray(usedPasswords)){
              for (var i=0;i<usedPasswords.length;i++){
                if (String(usedPasswords[i]).toLowerCase() === entered){
                  status.className = "err";
                  status.textContent = "Already used on this phone.";
                  return;
                }
              }
              usedPasswords.push(entered);
              if (usedPasswords.length > 500) usedPasswords = usedPasswords.slice(-500);
              if (typeof writeJSON === "function" && typeof LS_USED_PW !== "undefined"){
                try { writeJSON(LS_USED_PW, usedPasswords); } catch(e){}
              }
            }
          } catch(e){}
          var t = now();
          try {
            localStorage.setItem(LS_2D_STARTED, String(t));
            localStorage.setItem(LS_2D_EXPIRES, String(t + TRIAL_HOURS * 3600 * 1000));
            localStorage.setItem(LS_2D_USED, "true");
          } catch(e){}
          status.className = "ok";
          status.textContent = "Success! 2-day trial started.";
          try { if (typeof updateTrialBar === "function") updateTrialBar(); } catch(e){}
          hideLock();
          setTimeout(function(){
            try { alert("2-day trial started! Enjoy full access for 48 hours."); } catch(e){}
            try { if (typeof renderPayment === "function") renderPayment(); } catch(e){}
          }, 400);
          return;
        }

        return orig.apply(this, arguments);
      } catch(err){
        try { console.log("[Trial2d] verify error", err); } catch(e){}
        return orig.apply(this, arguments);
      }
    };
    wrapped._ajon2d = true;
    window.verifyPassword = wrapped;
    return true;
  }

  /* ---------- TRIAL BAR ---------- */
  function installTrialBar(){
    if (typeof window.updateTrialBar !== "function") return false;
    if (window.updateTrialBar._ajon2d) return true;
    var orig = window.updateTrialBar;
    var wrapped = function(){
      try {
        if (has30Day()) return orig.apply(this, arguments);
        if (has2Day()){
          var bar = byId("trialBar");
          if (bar){
            var exp = Number(localStorage.getItem(LS_2D_EXPIRES) || 0);
            var msLeft = exp - now();
            if (msLeft > 0){
              var h = Math.floor(msLeft / 3600000);
              var m = Math.floor((msLeft % 3600000) / 60000);
              bar.innerHTML = '<div class="trial-bar" style="background:rgba(52,211,153,.15);color:#a7f3d0;">\u23F1 2-Day Trial: <span class="time" style="color:#fff;">' + h + 'h ' + m + 'm</span> remaining</div>';
              return;
            }
          }
        }
      } catch(e){}
      return orig.apply(this, arguments);
    };
    wrapped._ajon2d = true;
    window.updateTrialBar = wrapped;
    return true;
  }

  /* ---------- VERIFY CARD (paywall-contact + bold digits) ---------- */
  function renderVerifyCard(tier){
    var verifyEl = byId("verifySection");
    if (!verifyEl) return;
    var price, label, duration;
    if (tier === "trial2d")    { price = "2,500";  label = "2-DAY TRIAL";  duration = "2 Days"; }
    else if (tier === "mid")   { price = "10,000"; label = "30-DAY MID";  duration = "30 Days"; }
    else if (tier === "senior"){ price = "5,000";  label = "SENIOR";      duration = "30 Days"; }
    else                       { price = "15,000"; label = "MASTER";      duration = "30 Days"; }
    var expiryTime = (typeof currentHourEndsAt === "function") ? currentHourEndsAt() : now();
    var expiryText = new Date(expiryTime).toLocaleTimeString([], { hour:"2-digit", minute:"2-digit" });
    var phone = (typeof PAYMENT_INFO !== "undefined") ? PAYMENT_INFO.phone : "";
    var name  = (typeof PAYMENT_INFO !== "undefined") ? PAYMENT_INFO.name  : "";
    verifyEl.innerHTML =
      '<div class="paywall-card" style="margin-top:14px;">' +
        '<div class="paywall-title">Verify ' + label + '</div>' +
        '<div class="paywall-instructions">' +
          '<div class="line"><span class="ic">1.</span><div>Pay <strong>' + price + ' UGX</strong> to MTN <span class="num">' + phone + '</span> Name <strong>' + name + '</strong>.</div></div>' +
          '<div class="line"><span class="ic">2.</span><div>After payment, <strong>beep or call</strong> to get the current hour password.</div></div>' +
          '<div class="line"><span class="ic">3.</span><div>Enter the password below and tap <strong>Verify</strong>.</div></div>' +
        '</div>' +
        '<div class="paywall-contact">' +
          '<div class="paywall-contact-label">\uD83D\uDCF1 Payment Contact</div>' +
          '<div class="paywall-contact-phone">' + phone + '</div>' +
          '<div class="paywall-contact-name">' + name + '</div>' +
        '</div>' +
        '<div class="paywall-hint">Password refreshes hourly. Current expires at <strong style="color:#00c853;">' + expiryText + '</strong>.</div>' +
        '<div class="paywall-input-row"><input id="txInput" type="text" placeholder="Enter hourly password" autocomplete="off" autocapitalize="off" spellcheck="false"></div>' +
        '<button id="verifyBtn" onclick="verifyPassword()">Verify and Unlock ' + duration + '</button>' +
        '<div id="statusMsg"></div>' +
      '</div>';
    setTimeout(function(){ var i = byId("txInput"); if (i) i.focus(); }, 100);
  }

  function installSelectTier(){
    if (typeof window.selectTier !== "function") return false;
    if (window.selectTier._ajon2d) return true;
    var orig = window.selectTier;
    var wrapped = function(tier){
      if (tier === "trial2d" || tier === "mid"){
        try { renderVerifyCard(tier); return; } catch(e){}
      }
      var r = orig.apply(this, arguments);
      try {
        setTimeout(function(){
          try {
            var verifyEl = byId("verifySection");
            if (!verifyEl) return;
            if (verifyEl.querySelector(".paywall-contact")) return;
            var phone = (typeof PAYMENT_INFO !== "undefined") ? PAYMENT_INFO.phone : "";
            var name  = (typeof PAYMENT_INFO !== "undefined") ? PAYMENT_INFO.name  : "";
            var hint = verifyEl.querySelector(".paywall-hint");
            if (!hint) return;
            var box = document.createElement("div");
            box.className = "paywall-contact";
            box.innerHTML = '<div class="paywall-contact-label">\uD83D\uDCF1 Payment Contact</div><div class="paywall-contact-phone">' + phone + '</div><div class="paywall-contact-name">' + name + '</div>';
            hint.parentNode.insertBefore(box, hint);
          } catch(e){}
        }, 40);
      } catch(e){}
      return r;
    };
    wrapped._ajon2d = true;
    window.selectTier = wrapped;
    return true;
  }

  /* ---------- INJECT EXTRA TIER BUTTONS ---------- */
  function injectTierButtons(){
    try {
      var panel = byId("panel-video");
      if (!panel) return;
      if (panel.querySelector('[data-ajon-tier-2d]')) return;
      var buttons = panel.querySelectorAll("button");
      var stBtns = [];
      for (var i=0;i<buttons.length;i++){
        var oc = buttons[i].getAttribute("onclick") || "";
        if (oc.indexOf("selectTier") > -1) stBtns.push(buttons[i]);
      }
      if (!stBtns.length) return;
      var template = stBtns[0];
      var parent = template.parentNode;
      if (!parent) return;
      var last = stBtns[stBtns.length - 1];

      function mk(tierId, label){
        var b = document.createElement("button");
        if (template.className) b.className = template.className;
        b.type = "button";
        b.setAttribute("data-ajon-tier-2d", tierId);
        b.textContent = label;
        b.style.marginTop = "6px";
        b.onclick = function(ev){
          ev.preventDefault(); ev.stopPropagation();
          try { window.selectTier(tierId); } catch(e){}
        };
        return b;
      }
      parent.insertBefore(mk("trial2d", "2,500/= (2 Days)"), last);
      parent.insertBefore(mk("mid", "10,000/= (30 Days)"), last);
    } catch(e){}
  }

  function installRenderPayment(){
    if (typeof window.renderPayment !== "function") return false;
    if (window.renderPayment._ajon2d) return true;
    var orig = window.renderPayment;
    var wrapped = function(){
      var r = orig.apply(this, arguments);
      try { setTimeout(injectTierButtons, 60); } catch(e){}
      return r;
    };
    wrapped._ajon2d = true;
    window.renderPayment = wrapped;
    return true;
  }

  /* ---------- SHOWTAB HOOK ---------- */
  function installShowTab(){
    if (typeof window.showTab !== "function") return false;
    if (window.showTab._ajon2d) return true;
    var orig = window.showTab;
    var wrapped = function(name){
      var r = orig.apply(this, arguments);
      try {
        setTimeout(function(){
          refreshLock();
          if (name === "video") injectTierButtons();
        }, 60);
      } catch(e){}
      return r;
    };
    wrapped._ajon2d = true;
    window.showTab = wrapped;
    return true;
  }

  /* ---------- STYLES ---------- */
  function installStyles(){
    try {
      if (byId("ajonTrial2dStyles")) return;
      var s = document.createElement("style");
      s.id = "ajonTrial2dStyles";
      s.textContent =
        ".paywall-instructions .num{font-weight:900 !important;color:#69f0ae !important;font-size:16px !important;letter-spacing:1px !important;}" +
        ".paywall-contact{margin:12px 0;padding:12px 14px;border-radius:12px;background:rgba(0,200,83,.10);border:1px solid rgba(0,200,83,.35);text-align:center;}" +
        ".paywall-contact-label{font-size:11px;font-weight:800;color:#a7f3d0;letter-spacing:.6px;text-transform:uppercase;margin-bottom:6px;}" +
        ".paywall-contact-phone{font-size:22px;font-weight:900;color:#fff;letter-spacing:2.5px;font-family:ui-monospace,Menlo,monospace;}" +
        ".paywall-contact-name{font-size:12px;color:#8aa;margin-top:4px;font-weight:700;}";
      document.head.appendChild(s);
    } catch(e){}
  }

  /* ---------- INIT ---------- */
  var tries = 0;
  function attempt(){
    tries++;
    installStyles();
    var ok = true;
    ok = installVerify()        && ok;
    ok = installTrialBar()      && ok;
    ok = installSelectTier()    && ok;
    ok = installShowTab()       && ok;
    ok = installRenderPayment() && ok;
    if (!ok && tries < 30){ setTimeout(attempt, 500); return; }
    try { if (typeof updateTrialBar === "function") updateTrialBar(); } catch(e){}
    try { injectTierButtons(); } catch(e){}
    refreshLock();
    try { console.log("[Trial2d Lock V2] installed"); } catch(e){}
  }
  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", function(){ setTimeout(attempt, 800); });
  } else {
    setTimeout(attempt, 800);
  }
  setInterval(refreshLock, 5000);
})();
