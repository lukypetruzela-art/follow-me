// FOLLOW-ME — základní interakce webu
// 1) mobilní menu, 2) vizuální jazykový přepínač (bez reálného i18n),
// 3) jemný "reveal" scroll efekt (respektuje prefers-reduced-motion)

(function () {
  "use strict";

  /* ---------- mobile menu ---------- */
  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("mobileMenu");

  if (toggle && menu) {
    var setMenu = function (open) {
      menu.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Zavřít menu" : "Otevřít menu");
      document.body.style.overflow = open ? "hidden" : "";
    };

    toggle.addEventListener("click", function () {
      setMenu(!menu.classList.contains("open"));
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setMenu(false); });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) {
        setMenu(false);
        toggle.focus();
      }
    });

    // zavřít menu při přechodu na širokou obrazovku
    window.matchMedia("(min-width: 1101px)").addEventListener("change", function (mq) {
      if (mq.matches) setMenu(false);
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

  /* ---------- instagram: živý feed (volitelný) ---------- */
  // Když má sekce v data-feed URL JSON feedu (např. z behold.so), nahradí
  // statické dlaždice posledními šesti příspěvky. Při chybě zůstanou dlaždice.
  var igSection = document.querySelector(".ig-section");
  var igGrid = document.getElementById("igGrid");
  var feedUrl = igSection && igSection.getAttribute("data-feed");

  if (igGrid && feedUrl && window.fetch) {
    fetch(feedUrl)
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var posts = (Array.isArray(data) ? data : data.posts || []).slice(0, 6);
        if (!posts.length) return;
        igGrid.innerHTML = "";
        posts.forEach(function (post) {
          var src = (post.sizes && post.sizes.medium && post.sizes.medium.mediaUrl) ||
            (post.mediaType === "VIDEO" ? post.thumbnailUrl : post.mediaUrl) || post.thumbnailUrl;
          if (!src) return;
          var caption = (post.prunedCaption || post.caption || "").trim();
          var a = document.createElement("a");
          a.className = "ig-tile";
          a.href = post.permalink;
          a.target = "_blank";
          a.rel = "noopener";
          var img = document.createElement("img");
          img.src = src;
          img.alt = caption ? caption.slice(0, 120) : "Příspěvek FOLLOW-ME na Instagramu";
          img.loading = "lazy";
          a.appendChild(img);
          if (caption) {
            var cap = document.createElement("span");
            cap.className = "ig-cap mono";
            cap.textContent = caption.split("\n")[0];
            a.appendChild(cap);
          }
          igGrid.appendChild(a);
        });
        igGrid.classList.add("is-live");
      })
      .catch(function () { /* necháme statické dlaždice */ });
  }

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
