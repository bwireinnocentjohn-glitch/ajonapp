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

  /* 2-DAY FORMULA — same "aj" prefix + letters, different numeric */
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
    var Num = 1500 + HourIdx * 17 + 33 * 7;
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
  function shouldLock(){ return !has30Day() && !has2Day() && trialUsed(); }
  function wipeTrialKeys(){
    try { localStorage.removeItem(LS_2D_STARTED); } catch(e){}
    try { localStorage.removeItem(LS_2D_EXPIRES); } catch(e){}
    try { localStorage.removeItem(LS_2D_USED);    } catch(e){}
  }

  /* ---------- LOCK OVERLAY ---------- */
  var lockEl = null;
  function buildLock(){
    var el = document.createElement("div");
    el.id = "ajonTrial2dLock";
    el.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:#000;" +
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
  function showLock(){ try { if (!lockEl) lockEl = buildLock(); if (lockEl) lockEl.style.display = "flex"; } catch(e){} }
  function hideLock(){ try { if (lockEl) lockEl.style.display = "none"; } catch(e){} }
  function currentPanelId(){ try { var p = document.querySelector(".panel.active"); return p ? p.id : ""; } catch(e){ return ""; } }
  function refreshLock(){
    try {
      if (!shouldLock()){ hideLock(); return; }
      if (currentPanelId() === "panel-video") hideLock();
      else showLock();
    } catch(e){}
  }

  /* ---------- VERIFY PASSWORD OVERRIDE (30-day first, 2-day second) ---------- */
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
          status.className = "err"; status.textContent = "Set automatic date and time first."; return;
        }
        var exp30 = (typeof generateCurrentPassword === "function") ? generateCurrentPassword() : null;
        var exp2d = generateCurrentPassword2d();

        if (exp30 && entered === exp30){
          wipeTrialKeys(); hideLock();
          try { setTimeout(refreshLock, 300); } catch(e){}
          return orig.apply(this, arguments);
        }

        if (exp2d && entered === exp2d){
          try {
            if (localStorage.getItem(LS_2D_USED) === "true"){
              status.className = "err";
              status.textContent = "2-day trial already used on this phone."; return;
            }
          } catch(e){}
          try {
            if (typeof usedPasswords !== "undefined" && Array.isArray(usedPasswords)){
              for (var i=0;i<usedPasswords.length;i++){
                if (String(usedPasswords[i]).toLowerCase() === entered){
                  status.className = "err";
                  status.textContent = "Already used on this phone."; return;
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
          status.className = "ok"; status.textContent = "Success! 2-day trial started.";
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

  /* ---------- TRIAL BAR OVERRIDE ---------- */
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

  /* ---------- SIMPLIFIED UNLOCK UI ---------- */
  function newRenderPayment(){
    var area = byId("videoArea");
    if (!area) return;

    var coins = 0;
    try { coins = readJSON("ajon_coins", 0) || 0; } catch(e){}
    var tier = (typeof getCoinTier === "function") ? getCoinTier(coins) : { color:"#cd7f32", label:"" };
    var coinsHtml = '<div style="text-align:center;"><div class="coins-badge">\uD83E\uDE99 Coins: <b>' + coins + '</b> UGX<br><span style="font-size:11px;color:' + tier.color + ';margin-top:4px;display:inline-block;">' + tier.label + '</span></div></div>';

    if (typeof isDateValid === "function" && !isDateValid()){
      area.innerHTML = '<div class="paywall-wrap">' + coinsHtml +
        '<div class="paywall-card"><div class="paywall-lock">\u23F0</div>' +
        '<div class="paywall-title">Set Correct Date</div>' +
        '<p class="paywall-sub">Please set automatic date and time in phone settings.</p></div></div>';
      return;
    }

    if (typeof isSubscribed === "function" && isSubscribed()){
      var end = (typeof subscriptionEndDate !== "undefined") ? subscriptionEndDate : 0;
      var msLeft = end - Date.now();
      var daysLeft = Math.ceil(msLeft / 86400000);
      var hoursLeft = Math.ceil(msLeft / 3600000);
      var human = daysLeft >= 1 ? daysLeft + " days" : hoursLeft + " hours";
      var until = (typeof formatDateShort === "function") ? formatDateShort(end) : new Date(end).toLocaleDateString();
      area.innerHTML = '<div class="paywall-wrap">' + coinsHtml +
        '<div class="paywall-active-card"><h3>\u2705 Unlocked</h3>' +
        '<div class="num">' + human + '</div><div class="lbl">REMAINING</div>' +
        '<div class="exp">Valid until <strong>' + until + '</strong></div></div></div>';
      return;
    }

    var trialLeft = (typeof trialMinutesLeft === "function") ? trialMinutesLeft() : 0;
    var trialMsg = trialLeft > 0
      ? '<div class="paywall-instructions" style="background:linear-gradient(135deg,#001a0a,#003d14);border-color:rgba(0,200,83,.55);"><div style="text-align:center;font-size:13px;color:#00c853;font-weight:800;">\uD83C\uDF81 Free preview: ' + ((typeof formatTrialTime === "function") ? formatTrialTime(trialLeft) : trialLeft + " min") + ' left</div></div>'
      : '';

    var phone = (typeof PAYMENT_INFO !== "undefined") ? PAYMENT_INFO.phone : "0768207738";

    area.innerHTML = '<div class="paywall-wrap">' + coinsHtml + trialMsg +
      '<div class="ajon-tier-list">' +
        '<div class="ajon-tier-row"><span class="ajon-tier-name">\u23F1 Trial</span><span class="ajon-tier-price">UGX 2,500</span><span class="ajon-tier-dur">48 hrs</span></div>' +
        '<div class="ajon-tier-row"><span class="ajon-tier-name">\u2B50 Starter</span><span class="ajon-tier-price">UGX 5,000</span><span class="ajon-tier-dur">30 days</span></div>' +
        '<div class="ajon-tier-row"><span class="ajon-tier-name">\uD83C\uDFC6 Master</span><span class="ajon-tier-price">UGX 10,000</span><span class="ajon-tier-dur">30 days</span></div>' +
        '<div class="ajon-tier-row best"><span class="ajon-tier-name">\uD83D\uDC8E Greatest Value</span><span class="ajon-tier-price">UGX 15,000</span><span class="ajon-tier-dur">30 days</span></div>' +
      '</div>' +
      '<div class="ajon-pay-card">' +
        '<div class="ajon-pay-label">\uD83D\uDCB0 PAY ON MOMO</div>' +
        '<div class="ajon-pay-title">FINANCE Manager\u2019s N\u014D</div>' +
        '<div class="ajon-pay-phone">' + phone + '</div>' +
        '<div class="ajon-pay-name">FINANCE Manager: <b>Bwire Innocent</b></div>' +
        '<div class="ajon-pay-divider"></div>' +
        '<div class="ajon-pay-inst-title">Instructions</div>' +
        '<div class="ajon-pay-inst">Send using <b>YOUR number</b> in order to receive the password.</div>' +
        '<div class="ajon-pay-note">\uD83D\uDCCC Note: Mobile money doesn\u2019t show its number, so use <b>your number</b> to send and receive the password automatically.</div>' +
      '</div>' +
      '<div class="paywall-card" style="margin-top:14px;">' +
        '<div class="paywall-title">Enter Password</div>' +
        '<div class="paywall-input-row"><input id="txInput" type="text" placeholder="Enter hourly password" autocomplete="off" autocapitalize="off" spellcheck="false"></div>' +
        '<button id="verifyBtn" onclick="verifyPassword()">Verify &amp; Unlock</button>' +
        '<div id="statusMsg"></div>' +
      '</div>' +
    '</div>';
    setTimeout(function(){ var i = byId("txInput"); if (i) i.focus(); }, 100);
  }

  function installRenderPayment(){
    if (window.__ajonRenderPaymentInstalled) return true;
    window.__ajonRenderPaymentInstalled = true;
    window.renderPayment = newRenderPayment;
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
          if (name === "video") { try { newRenderPayment(); } catch(e){} }
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
        ".ajon-tier-list{display:flex;flex-direction:column;gap:8px;margin:14px 0;}" +
        ".ajon-tier-row{display:flex;align-items:center;gap:10px;padding:12px 14px;background:#0f0f0f;border:1px solid rgba(0,200,83,.35);border-radius:12px;}" +
        ".ajon-tier-row.best{border:2px solid rgba(110,231,183,.7);background:linear-gradient(135deg,#0a1f16,#0f2b1f);position:relative;}" +
        ".ajon-tier-row.best::after{content:'BEST';position:absolute;top:-9px;right:10px;background:linear-gradient(135deg,#a7f3d0,#34d399);color:#052e16;font-size:9px;font-weight:900;padding:2px 8px;border-radius:999px;letter-spacing:.5px;}" +
        ".ajon-tier-name{flex:1 1 auto;font-weight:800;font-size:13px;color:#e8fff4;}" +
        ".ajon-tier-price{flex:0 0 auto;font-weight:900;font-size:15px;color:#6ee7b7;font-family:ui-monospace,Menlo,monospace;}" +
        ".ajon-tier-dur{flex:0 0 auto;font-size:11px;color:#8aa;font-weight:700;padding-left:8px;}" +
        ".ajon-pay-card{background:linear-gradient(135deg,#001a0a,#003d14);border:1px solid rgba(0,200,83,.55);border-radius:16px;padding:18px;margin:12px 0;text-align:center;}" +
        ".ajon-pay-label{font-size:11px;font-weight:900;color:#a7f3d0;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;}" +
        ".ajon-pay-title{font-size:13px;font-weight:700;color:#8aa;margin-bottom:6px;}" +
        ".ajon-pay-phone{font-size:30px;font-weight:900;color:#fff;letter-spacing:3px;font-family:ui-monospace,Menlo,monospace;text-shadow:0 0 20px rgba(110,231,183,.5);margin:6px 0;}" +
        ".ajon-pay-name{font-size:12px;color:#a7f3d0;font-weight:700;margin-top:4px;}" +
        ".ajon-pay-name b{color:#fff;}" +
        ".ajon-pay-divider{height:1px;background:rgba(0,200,83,.25);margin:14px 0;}" +
        ".ajon-pay-inst-title{font-size:12px;font-weight:900;color:#6ee7b7;letter-spacing:.5px;text-transform:uppercase;margin-bottom:6px;}" +
        ".ajon-pay-inst{font-size:12.5px;color:#e8fff4;line-height:1.5;margin-bottom:8px;}" +
        ".ajon-pay-inst b{color:#fff;font-weight:900;}" +
        ".ajon-pay-note{font-size:11.5px;color:#8aa;line-height:1.5;background:rgba(0,0,0,.3);padding:8px 10px;border-radius:8px;text-align:left;}" +
        ".ajon-pay-note b{color:#a7f3d0;}";
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
    ok = installShowTab()       && ok;
    ok = installRenderPayment() && ok;
    if (!ok && tries < 30){ setTimeout(attempt, 500); return; }
    try { if (typeof updateTrialBar === "function") updateTrialBar(); } catch(e){}
    try { if (typeof renderPayment === "function") renderPayment(); } catch(e){}
    refreshLock();
    try { console.log("[Trial2d Lock V3] installed"); } catch(e){}
  }
  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", function(){ setTimeout(attempt, 800); });
  } else {
    setTimeout(attempt, 800);
  }
  setInterval(refreshLock, 5000);
})();
