// Analytics consent: the Google tag loads only after the visitor chooses Allow.
// The choice is kept in localStorage; with no choice yet, the banner asks, unless
// the browser sends a Global Privacy Control signal, which counts as Decline.
(function () {
  var KEY = "analytics-consent";
  var ID = "G-T6KK7PB43N";
  var banner = document.querySelector("[data-consent]");
  var statuses = document.querySelectorAll("[data-consent-status]");

  function read() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function write(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
  }

  function loadTag() {
    window["ga-disable-" + ID] = false;
    if (document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date());
    gtag("config", ID);
    var script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
    document.head.appendChild(script);
  }

  // Stops a tag already running on this page and removes its cookies.
  function stopTag() {
    window["ga-disable-" + ID] = true;
    var host = location.hostname;
    ["_ga", "_ga_" + ID.slice(2)].forEach(function (name) {
      [host, "." + host.replace(/^www\./, "")].forEach(function (domain) {
        document.cookie = name + "=; Max-Age=0; path=/; domain=" + domain;
      });
      document.cookie = name + "=; Max-Age=0; path=/";
    });
  }

  var LABELS = {
    granted: "Allowed",
    denied: "Declined",
    gpc: "Declined by your browser’s Global Privacy Control setting",
    none: "Not chosen yet",
  };

  function show(state) {
    Array.prototype.forEach.call(statuses, function (el) { el.textContent = LABELS[state]; });
  }

  function apply(choice) {
    if (choice === "granted") loadTag();
    else stopTag();
    show(choice);
  }

  var choice = read();
  if (choice === "granted") {
    apply("granted");
  } else if (choice === "denied") {
    show("denied");
  } else if (navigator.globalPrivacyControl === true) {
    show("gpc");
  } else {
    show("none");
    if (banner) banner.hidden = false;
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-consent-choice]");
    if (!button) return;
    var value = button.getAttribute("data-consent-choice");
    write(value);
    apply(value);
    if (banner) banner.hidden = true;
  });
})();
