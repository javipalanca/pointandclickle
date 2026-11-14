/* Point & Clickle · usage statistics, in the style of the Point and Click Museum. Two destinations:
   - Own statistics (/api/stats/, games/stats.py): daily counters of views, games, wins, shares, referrers and
     devices. No cookies, nothing stored in the browser, no identifiers, no IPs kept, nothing sent to third
     parties, so no consent is needed and every visit counts. Batched with navigator.sendBeacon. Staff see them
     at /stats/. Off when the browser asks not to be tracked (GPC / DNT), like the museum's.
   - Google Analytics 4 with Consent Mode v2 "advanced": gtag always loads with analytics_storage "denied", so
     visitors who have not accepted send cookieless pings (no _ga cookie, no client id) that GA uses to model
     them in its reports; accepting the cookie banner grants storage. The choice is kept in localStorage and can
     be changed from the footer ("Cookies"). With GPC / DNT: no Google at all and no banner.
   - Other scripts call CLK.track(name, params); it never throws.
   - Add ?ga_debug=1 to any URL to see the events in GA's DebugView for the rest of the session.

   Measurement plan (GA4 recommended events where one fits; nothing typed by the player is sent except the
   autocomplete search, which is a game title):
     page_view        every page (gtag config)                 page_type, game_mode, puzzle_number, visitor_type
     level_start      first guess of a game                    level_name (daily|random|archive), puzzle_number
     guess            each guess                               game_mode, attempt, correct, from_list
     level_end        a game is won or lost                    level_name, success, attempts, puzzle_number
     post_score       a game is won or lost                    score (1-6, 0 = lost), level_name
     unlock_achievement  daily streak of 3, 7, 14, 30, 100    achievement_id (streak_N)
     select_content   a screenshot (frame) is opened          content_type=frame, content_id (1-6), game_mode
     search           autocomplete search, 1.5 s after typing  search_term, results_found
     view_solution    the solution is shown                    game_mode, trigger (end|link|resume)
     modal_open       statistics / how to play / result       modal
     share            result shared                            method (x|whatsapp|telegram|clipboard), content_type, item_id
     museum_click     a link to the Point and Click Museum      placement (header|banner|result|howto|footer|faq)
     outbound_click   any link out of the site                 link_domain, link_url, link_text, region
     donate_click     the PayPal button                        region
     random_game      a random game is requested               from (page_type)
     archive_day      a day is opened from the archive         day, puzzle_number
     ui_click         any click on a control                   element, link_text, region, section_id, x_pct, y_pct, page_y_pct, viewport
     section_view     a section stays 1.5 s on screen          section_id
     scroll_depth     25/50/75/100 % of the page               percent
     web_vitals       LCP, CLS, INP, FCP, TTFB on leaving      metric_name, metric_value, metric_rating
     exception        JavaScript errors (5 per page at most)   description, fatal
     consent          the banner is answered                   granted (only sent when granted)
   User properties (only with consent): visitor_type, device_class, daily_streak (band), daily_played (band),
   consent_version.

   Own statistics (metric · label): view · page type, device · mobile|tablet|desktop, referrer · domain or
   "direct", game_start · daily|random|archive, game_win / game_loss · same, daily_attempts · 1-6 or X,
   share · method, museum_click · placement, random_game, archive_day, donate_click. */
"use strict";
(function () {
  var GA = (document.body && document.body.dataset.ga) || "";
  var PAGE = (document.body && document.body.dataset.page) || "page";
  var KEY = "clk-consent";
  var web = /^https?:$/.test(location.protocol);
  var optOut = navigator.globalPrivacyControl === true || navigator.doNotTrack === "1" || window.doNotTrack === "1";
  var ga = false;

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } },
    del: function (k) { try { localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  };
  var debug = (function () {
    try {
      if (/[?&]ga_debug=1/.test(location.search)) sessionStorage.setItem("clk-ga-debug", "1");
      return sessionStorage.getItem("clk-ga-debug") === "1";
    } catch (e) { return false; }
  })();
  var viewport = function () { return innerWidth < 600 ? "mobile" : innerWidth < 1024 ? "tablet" : "desktop"; };
  var band = function (n) { return n >= 100 ? "100+" : n >= 30 ? "30-99" : n >= 7 ? "7-29" : n >= 3 ? "3-6" : n >= 1 ? "1-2" : "0"; };
  var dailyStats = function () { try { return JSON.parse(store.get("stats")) || {}; } catch (e) { return {}; } };
  var cfg = function () {
    var el = document.getElementById("game-config");
    try { return el ? JSON.parse(el.textContent) : {}; } catch (e) { return {}; }
  };

  function send(name, params) {
    if (!ga) return;
    var c = cfg();
    window.gtag("event", name, Object.assign({ page_type: PAGE }, c.mode ? { game_mode: c.kind || c.mode } : {},
      debug ? { debug_mode: true } : {}, params || {}));
  }
  /* ---------- own statistics: anonymous daily counters, no cookies ---------- */
  var STATS_URL = (document.body && document.body.dataset.stats) || "";
  var own = web && !!STATS_URL && !optOut;
  var queue = [], timer = null;
  function flush() {
    if (!own || !queue.length) return;
    var body = JSON.stringify({ e: queue.splice(0, 20) });
    try {
      if (!(navigator.sendBeacon && navigator.sendBeacon(STATS_URL, new Blob([body], { type: "text/plain" }))))
        fetch(STATS_URL, { method: "POST", body: body, keepalive: true, headers: { "Content-Type": "text/plain" } }).catch(function () {});
    } catch (e) { /* statistics never break the game */ }
    if (queue.length) flush();
  }
  function stat(metric, label) {
    if (!own) return;
    queue.push([metric, String(label == null ? "" : label).toLowerCase().slice(0, 64)]);
    if (queue.length >= 20) flush();
    else if (!timer) timer = setTimeout(function () { timer = null; flush(); }, 4000);
  }
  /* the game's GA events, counted in the own statistics as well */
  function toStats(name, p) {
    p = p || {};
    var kind = cfg().kind || "";
    if (name === "level_start") stat("game_start", p.level_name || kind);
    else if (name === "level_end") {
      stat(p.success ? "game_win" : "game_loss", p.level_name || kind);
      if ((p.level_name || kind) === "daily") stat("daily_attempts", p.success ? p.attempts : "x");
    } else if (name === "share") stat("share", p.method);
    else if (name === "museum_click") stat("museum_click", p.placement);
    else if (name === "random_game") stat("random_game", p.from || PAGE);
    else if (name === "archive_day") stat("archive_day", "");
    else if (name === "donate_click") stat("donate_click", "");
  }
  (function () {
    stat("view", PAGE);
    stat("device", viewport());
    var ref = "direct";
    try { if (document.referrer) { var r = new URL(document.referrer); ref = r.host === location.host ? "" : r.hostname.replace(/^www\./, ""); } } catch (e) { /* bad referrer */ }
    if (ref) stat("referrer", ref);
  })();
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });
  addEventListener("pagehide", flush);

  /* public: CLK.track(name, params) → own statistics and GA */
  function track(name, params) {
    try {
      toStats(name, params);
      if (ga) send(name, params);
    } catch (e) { /* analytics never break the game */ }
  }
  function setUser(props) { try { if (ga) window.gtag("set", "user_properties", props); } catch (e) { /* ignore */ } }
  window.CLK = { track: track, setUser: setUser, band: band };

  /* ---------- automatic measurement: clicks, sections, scroll, vitals, errors ---------- */
  var REGIONS = [["#consentBox", "consent"], [".modal", "modal"], [".site-header", "header"], [".site-footer", "footer"], ["main", "main"]];
  var regionOf = function (el) { for (var i = 0; i < REGIONS.length; i++) if (el.closest(REGIONS[i][0])) return REGIONS[i][1]; return "other"; };
  var textOf = function (el) {
    return (el.getAttribute("aria-label") || el.textContent || el.getAttribute("title") || el.getAttribute("alt") || "").replace(/\s+/g, " ").trim().slice(0, 40);
  };
  var nameOf = function (el) { return el.dataset.ga || (el.id ? "#" + el.id : "") || [el.tagName.toLowerCase()].concat([].slice.call(el.classList, 0, 2)).join("."); };
  var sectionOf = function (el) { var s = el.closest("section[id], [id].modal"); return s ? s.id : ""; };
  var lastClick = 0;

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (a) {
      var u = null;
      try { u = new URL(a.href, location.href); } catch (_) { /* not a URL */ }
      if (a.dataset.museum) track("museum_click", { placement: a.dataset.museum });
      if (u && /^https?:$/.test(u.protocol) && u.host !== location.host) {
        track("outbound_click", { link_domain: u.hostname.replace(/^www\./, ""), link_url: (u.origin + u.pathname).slice(0, 100),
          link_text: textOf(a), region: regionOf(a) });
      } else if (u && u.host === location.host) {
        if (/^\/random\/$/.test(u.pathname)) track("random_game", { from: PAGE });
        var day = a.dataset.day;
        if (day) track("archive_day", { day: day, puzzle_number: parseInt(((a.querySelector("b") || {}).textContent || "").replace("#", ""), 10) || 0 });
      }
    }
    if (e.target.closest && e.target.closest("#donate-form button")) track("donate_click", { region: "footer" });
    if (!ga || performance.now() - lastClick < 250) return;
    var el = e.target.closest && e.target.closest("a, button, summary, [role=button], input, label, .btn-social");
    if (!el) return;
    lastClick = performance.now();
    var doc = document.documentElement.scrollHeight || 1;
    var five = function (v) { return Math.max(0, Math.min(100, Math.round(v / 5) * 5)); };
    send("ui_click", { element: nameOf(el), link_text: el.tagName === "INPUT" ? "" : textOf(el), region: regionOf(el), section_id: sectionOf(el),
      x_pct: five(100 * e.clientX / innerWidth), y_pct: five(100 * e.clientY / innerHeight), page_y_pct: five(100 * (e.clientY + scrollY) / doc), viewport: viewport() });
  }, true);

  var maxScroll = 0, reached = {};
  function scrolled() {
    var h = document.documentElement.scrollHeight - innerHeight;
    maxScroll = Math.max(maxScroll, h > 0 ? Math.round(100 * scrollY / h) : 100);
    [25, 50, 75, 100].forEach(function (q) { if (ga && maxScroll >= q && !reached[q]) { reached[q] = true; send("scroll_depth", { percent: q }); } });
  }
  addEventListener("scroll", scrolled, { passive: true });

  function watchSections() {
    if (!("IntersectionObserver" in window)) return;
    var seen = {}, timers = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var id = en.target.id;
        if (seen[id]) return;
        if (en.isIntersecting) timers[id] = setTimeout(function () { seen[id] = true; io.unobserve(en.target); send("section_view", { section_id: id }); }, 1500);
        else { clearTimeout(timers[id]); delete timers[id]; }
      });
    }, { threshold: 0.5 });
    document.querySelectorAll("main section[id], main [id].museum-plaque, main .cabinet").forEach(function (el) {
      if (!el.id) el.id = "screen";
      io.observe(el);
    });
  }

  /* Core Web Vitals, measured as the web-vitals library does, sent when the page is hidden */
  var vitals = {}, nav = (performance.getEntriesByType && performance.getEntriesByType("navigation")[0]) || {};
  function observe(type, fn, opts) {
    try { new PerformanceObserver(function (l) { l.getEntries().forEach(fn); }).observe(Object.assign({ type: type, buffered: true }, opts || {})); } catch (e) { /* unsupported */ }
  }
  if (nav.responseStart > 0) vitals.TTFB = nav.responseStart;
  observe("paint", function (e) { if (e.name === "first-contentful-paint") vitals.FCP = e.startTime; });
  observe("largest-contentful-paint", function (e) { vitals.LCP = e.startTime; });
  var cls = 0, win = 0, winStart = 0, winLast = 0;
  observe("layout-shift", function (e) {
    if (e.hadRecentInput) return;
    if (win && e.startTime - winLast < 1000 && e.startTime - winStart < 5000) win += e.value;
    else { win = e.value; winStart = e.startTime; }
    winLast = e.startTime; cls = Math.max(cls, win); vitals.CLS = cls;
  });
  observe("event", function (e) { if (e.interactionId) vitals.INP = Math.max(vitals.INP || 0, e.duration); }, { durationThreshold: 40 });
  observe("first-input", function (e) { vitals.INP = Math.max(vitals.INP || 0, e.duration); });
  var sentVitals = false;
  function leave() {
    if (sentVitals || !ga) return;
    sentVitals = true;
    var T = { LCP: [2500, 4000], INP: [200, 500], CLS: [0.1, 0.25], FCP: [1800, 3000], TTFB: [800, 1800] };
    Object.keys(vitals).forEach(function (name) {
      var raw = vitals[name], v = name === "CLS" ? Math.round(raw * 1000) : Math.round(raw);
      send("web_vitals", { metric_name: name, metric_value: v, value: v, non_interaction: true,
        metric_rating: raw <= T[name][0] ? "good" : raw > T[name][1] ? "poor" : "needs-improvement", transport_type: "beacon" });
    });
  }
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") leave(); });
  addEventListener("pagehide", leave);

  var errors = 0;
  addEventListener("error", function (e) {
    if (errors++ >= 5 || !e.message) return;
    track("exception", { description: (String(e.filename || "").split("/").pop().split("?")[0] + ":" + (e.lineno || 0) + " " + e.message).slice(0, 100), fatal: false });
  });
  addEventListener("unhandledrejection", function (e) {
    if (errors++ >= 5) return;
    track("exception", { description: ("promise: " + String((e.reason && e.reason.message) || e.reason)).slice(0, 100), fatal: false });
  });

  /* ---------- Google Analytics: Consent Mode v2, advanced ---------- */
  if (!GA || !web || optOut) return;        // GPC / DNT: no Google and no banner
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("consent", "default", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied",
    ad_personalization: "denied", wait_for_update: 500 });
  window.gtag("set", "ads_data_redaction", true);

  function visitorType() {
    try {
      var n = +(localStorage.getItem("clk-visits") || 0);
      if (!sessionStorage.getItem("clk-visit")) { sessionStorage.setItem("clk-visit", "1"); localStorage.setItem("clk-visits", String(++n)); }
      return n > 1 ? "returning" : "new";
    } catch (e) { return "unknown"; }
  }
  /* with consent only: storage for the visitor type, user properties */
  function grant() {
    var s = dailyStats();
    window.gtag("consent", "update", { analytics_storage: "granted" });
    window.gtag("set", "user_properties", { visitor_type: visitorType(), device_class: viewport(),
      daily_streak: band(s["Current Streak"] || 0), daily_played: band(s["Played"] || 0), consent_version: "2" });
  }
  function deny() {
    window.gtag("consent", "update", { analytics_storage: "denied" });
    var domain = location.hostname.split(".").slice(-2).join(".");
    document.cookie.split(";").map(function (c) { return c.trim().split("=")[0]; }).filter(function (n) { return /^_ga/.test(n); }).forEach(function (n) {
      [location.hostname, "." + domain, ""].forEach(function (d) { document.cookie = n + "=; Max-Age=0; path=/" + (d ? "; domain=" + d : ""); });
    });
    store.del("clk-visits");
  }

  var choice = store.get(KEY);
  if (choice === "granted") grant();         // before config, so the first hit already carries the choice
  var c0 = cfg();
  window.gtag("js", new Date());
  window.gtag("config", GA, Object.assign({ page_title: document.title, content_group: PAGE, page_type: PAGE,
    game_mode: c0.kind || "", puzzle_number: c0.number || undefined,
    allow_google_signals: false, allow_ad_personalization_signals: false }, debug ? { debug_mode: true } : {}));
  var tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA);
  document.head.appendChild(tag);
  ga = true;
  watchSections();
  scrolled();

  var box = null;
  function hide() { if (box) { box.remove(); box = null; } }
  function choose(granted) {
    store.set(KEY, granted ? "granted" : "denied");
    if (granted) { grant(); send("consent", { granted: true }); } else deny();
    hide();
  }
  function ask() {
    if (box) return;
    box = document.createElement("div");
    box.className = "pconsent px";
    box.id = "consentBox";
    box.setAttribute("role", "region");
    box.setAttribute("aria-label", "Cookies");
    box.innerHTML = "<p>May we use Google Analytics cookies to see how the game is played? Without them we only keep anonymous counts, and the game works the same.</p>" +
      '<div class="consent-actions"><button class="pbtn small brass" type="button" data-c="1">Accept</button>' +
      '<button class="pbtn small" type="button" data-c="0">Decline</button></div>';
    box.addEventListener("click", function (e) { var b = e.target.closest("button[data-c]"); if (b) choose(b.dataset.c === "1"); });
    document.body.appendChild(box);
  }
  var btn = document.getElementById("consentOpen");
  if (btn) btn.addEventListener("click", ask);
  if (choice !== "granted" && choice !== "denied") ask();
})();
