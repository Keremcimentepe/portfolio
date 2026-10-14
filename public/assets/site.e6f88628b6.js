// Small enhancements only; the page works fully without JavaScript.
(function () {
  var root = document.documentElement;
  var media = window.matchMedia("(prefers-color-scheme: dark)");
  var PAPER = { light: "#f7f8fa", dark: "#0f151e" };

  function current() {
    var t = root.getAttribute("data-theme");
    return t === "light" || t === "dark" ? t : media.matches ? "dark" : "light";
  }

  // Theme toggle ---------------------------------------------------------
  var toggle = document.querySelector(".theme-toggle");
  function syncToggle() {
    var theme = current();
    if (toggle) {
      toggle.setAttribute(
        "aria-label",
        theme === "dark" ? toggle.dataset.labelLight : toggle.dataset.labelDark
      );
    }
    if (root.hasAttribute("data-theme")) {
      document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) {
        m.setAttribute("content", PAPER[theme]);
      });
    }
  }
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {}
      syncToggle();
    });
  }
  if (media.addEventListener) media.addEventListener("change", syncToggle);
  syncToggle();

  // Keep the visitor's place when switching language (sections share ids).
  var lang = document.querySelector(".lang");
  if (lang) {
    lang.addEventListener("click", function () {
      if (/^#[a-z-]+$/.test(location.hash)) lang.href = lang.getAttribute("href").split("#")[0] + location.hash;
    });
  }

  // Copy e-mail address --------------------------------------------------
  var copy = document.querySelector(".copy-btn");
  if (copy && navigator.clipboard && window.isSecureContext) {
    var status = document.querySelector(".copy-status");
    var label = copy.textContent;
    var timer;
    copy.hidden = false;
    copy.addEventListener("click", function () {
      navigator.clipboard.writeText(copy.dataset.copy).then(function () {
        copy.textContent = copy.dataset.done;
        if (status) status.textContent = copy.dataset.done;
        clearTimeout(timer);
        timer = setTimeout(function () {
          copy.textContent = label;
          if (status) status.textContent = "";
        }, 2000);
      });
    });
  }
})();
