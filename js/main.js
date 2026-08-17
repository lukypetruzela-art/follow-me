// FOLLOW-ME — základní interakce webu
// 1) mobilní menu, 2) vizuální jazykový přepínač (bez reálného i18n),
// 3) jemný "reveal" scroll efekt (respektuje prefers-reduced-motion)

(function () {
  "use strict";

  /* ---------- mobile menu ---------- */
  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("mobileMenu");

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var isOpen = menu.classList.toggle("open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      document.body.style.overflow = isOpen ? "hidden" : "";
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        menu.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
    });
  }

  /* ---------- language switcher (visual only) ---------- */
  var langButtons = document.querySelectorAll(".nav-lang button");
  langButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      langButtons.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      // Poznámka pro vývojáře: skutečný překlad obsahu (CZ/EN/PL/DE)
      // zatím není zapojen — tlačítka jen naznačují cílový interakční vzor.
    });
  });

  /* ---------- reveal on scroll ---------- */
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var revealEls = document.querySelectorAll(".reveal");

  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  } else {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach(function (el) { observer.observe(el); });
  }
})();
