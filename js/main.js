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

  /* ---------- video reel: smyčka úseku z YouTube ---------- */
  var reel = document.querySelector(".reel");
  var reduceMotionReel = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reel && !reduceMotionReel) {
    var vid = reel.getAttribute("data-video");
    var start = parseFloat(reel.getAttribute("data-start")) || 0;
    var end = parseFloat(reel.getAttribute("data-end")) || start + 10;
    var bar = document.getElementById("reelBar");
    var tc = document.getElementById("reelTc");
    var player = null;
    var ticker = null;

    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    var tick = function () {
      if (!player || !player.getCurrentTime) return;
      var t = player.getCurrentTime();
      if (t >= end || t < start - 1) { player.seekTo(start, true); t = start; }
      bar.style.width = Math.max(0, Math.min(1, (t - start) / (end - start))) * 100 + "%";
      tc.textContent = pad(Math.floor(t / 60)) + ":" + pad(Math.floor(t % 60));
    };

    var createPlayer = function () {
      player = new window.YT.Player("reelPlayer", {
        videoId: vid,
        host: "https://www.youtube-nocookie.com",
        playerVars: {
          autoplay: 1, mute: 1, controls: 0, disablekb: 1, fs: 0, rel: 0,
          playsinline: 1, iv_load_policy: 3, start: Math.floor(start)
        },
        events: {
          onReady: function (e) { e.target.mute(); e.target.playVideo(); },
          onStateChange: function (e) {
            if (e.data === window.YT.PlayerState.PLAYING) {
              reel.classList.add("is-playing");
              if (!ticker) ticker = setInterval(tick, 200);
            } else if (e.data === window.YT.PlayerState.ENDED) {
              e.target.seekTo(start, true);
              e.target.playVideo();
            }
          }
        }
      });
    };

    var loadApi = function () {
      if (window.YT && window.YT.Player) { createPlayer(); return; }
      var prev = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = function () { if (prev) prev(); createPlayer(); };
      var tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      document.head.appendChild(tag);
    };

    // video načíst až když se sekce blíží k obrazovce
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { io.disconnect(); loadApi(); }
      }, { rootMargin: "300px" });
      io.observe(reel);
    } else {
      loadApi();
    }

    // šetřit výkon: pauza, když je smyčka mimo obrazovku
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        if (!player || !player.playVideo) return;
        if (entries[0].isIntersecting) player.playVideo(); else player.pauseVideo();
      }).observe(reel);
    }
  }

  /* ---------- galerie: další fotky + prohlížeč ---------- */
  var moreBtn = document.getElementById("galleryMoreBtn");
  var moreGrid = document.getElementById("galleryMore");
  if (moreBtn && moreGrid) {
    moreBtn.addEventListener("click", function () {
      var show = moreGrid.hidden;
      moreGrid.hidden = !show;
      moreBtn.setAttribute("aria-expanded", show ? "true" : "false");
      moreBtn.textContent = show ? "MÉNĚ FOTEK ↑" : "DALŠÍ FOTKY (" + moreGrid.children.length + ") ↓";
    });
  }

  var lb = document.getElementById("lightbox");
  var tiles = Array.prototype.slice.call(document.querySelectorAll("a.g-tile"));
  if (lb && lb.showModal && tiles.length) {
    var lbImg = document.getElementById("lbImg");
    var lbCap = document.getElementById("lbCap");
    var lbCount = document.getElementById("lbCount");
    var current = 0;

    var show = function (i) {
      current = (i + tiles.length) % tiles.length;
      var t = tiles[current];
      var img = t.querySelector("img");
      lbImg.src = t.getAttribute("href");
      lbImg.alt = img ? img.alt : "";
      lbCap.textContent = t.getAttribute("data-caption") || "";
      lbCount.textContent = (current + 1) + " / " + tiles.length;
    };

    tiles.forEach(function (t, i) {
      t.addEventListener("click", function (e) {
        e.preventDefault();
        show(i);
        lb.showModal();
      });
    });

    document.getElementById("lbPrev").addEventListener("click", function () { show(current - 1); });
    document.getElementById("lbNext").addEventListener("click", function () { show(current + 1); });
    document.getElementById("lbClose").addEventListener("click", function () { lb.close(); });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(current - 1);
      if (e.key === "ArrowRight") show(current + 1);
    });

    // přejetí prstem na mobilu
    var touchX = null;
    lb.addEventListener("touchstart", function (e) { touchX = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (touchX === null) return;
      var dx = e.changedTouches[0].clientX - touchX;
      if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
      touchX = null;
    });
  }

  /* ---------- kalendář akcí z data/events.json ---------- */
  // Akce se spravují v /admin. Zobrazují se jen budoucí; když žádné nejsou,
  // zůstane v tabulce výchozí řádek „Kalendář připravujeme“ z HTML.
  var eventsBody = document.getElementById("eventsBody");
  if (eventsBody && window.fetch) {
    var en = document.documentElement.lang === "en";
    var base = eventsBody.getAttribute("data-src") || "data/events.json";
    var LABEL = en
      ? { confirmed: "CONFIRMED", tbc: "TO BE CONFIRMED", cancelled: "CANCELLED", date: "Date", place: "Location", event: "Event", status: "Status", more: "Event website" }
      : { confirmed: "POTVRZENO", tbc: "BUDE UPŘESNĚNO", cancelled: "ZRUŠENO", date: "Datum", place: "Místo", event: "Akce", status: "Stav", more: "Web akce" };
    var fmtDate = function (iso) {
      var p = iso.split("-");
      return en ? +p[2] + " " + ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][+p[1] - 1] + " " + p[0]
                : +p[2] + ". " + +p[1] + ". " + p[0];
    };
    var fmtRange = function (e) {
      if (!e.dateTo) return fmtDate(e.date);
      var a = e.date.split("-"), b = e.dateTo.split("-");
      if (!en && a[0] === b[0] && a[1] === b[1]) return +a[2] + ".–" + fmtDate(e.dateTo);
      return fmtDate(e.date) + " – " + fmtDate(e.dateTo);
    };
    var cell = function (label, child) {
      var td = document.createElement("td");
      td.setAttribute("data-label", label);
      if (typeof child === "string") td.textContent = child; else td.appendChild(child);
      return td;
    };
    var today = new Date().toISOString().slice(0, 10);

    fetch(base, { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (list) {
        var upcoming = (Array.isArray(list) ? list : []).filter(function (e) {
          return e && e.date && (e.dateTo || e.date) >= today;
        }).sort(function (a, b) { return a.date.localeCompare(b.date); });
        if (!upcoming.length) return;
        eventsBody.innerHTML = "";
        upcoming.forEach(function (e) {
          var tr = document.createElement("tr");
          if (e.status === "cancelled") tr.className = "is-cancelled";
          var name = document.createElement("span");
          var strong = document.createElement("span");
          strong.className = "ev-name";
          strong.textContent = e.name;
          name.appendChild(strong);
          if (e.note) {
            var note = document.createElement("span");
            note.className = "ev-note";
            note.textContent = e.note;
            name.appendChild(note);
          }
          if (e.link) {
            var a = document.createElement("a");
            a.href = e.link; a.target = "_blank"; a.rel = "noopener";
            a.className = "ev-link";
            a.textContent = LABEL.more + " ↗";
            name.appendChild(a);
          }
          var pill = document.createElement("span");
          pill.className = "status-pill " + ({ confirmed: "ok", tbc: "tbd", cancelled: "cancel" }[e.status] || "tbd");
          pill.textContent = LABEL[e.status] || LABEL.tbc;
          tr.appendChild(cell(LABEL.date, fmtRange(e)));
          tr.appendChild(cell(LABEL.place, e.location || "—"));
          tr.appendChild(cell(LABEL.event, name));
          tr.appendChild(cell(LABEL.status, pill));
          eventsBody.appendChild(tr);
        });
      })
      .catch(function () { /* necháme výchozí řádek */ });
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
