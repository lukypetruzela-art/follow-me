// FOLLOW-ME — základní interakce webu
// 1) mobilní menu, 2) vizuální jazykový přepínač (bez reálného i18n),
// 3) jemný "reveal" scroll efekt (respektuje prefers-reduced-motion)

(function () {
  "use strict";

  // jazyk stránky: hlavní verze je česká, anglická je v /en/
  var EN = document.documentElement.lang === "en";
  var T = EN
    ? { open: "Open menu", close: "Close menu", igPost: "FOLLOW-ME post on Instagram", less: "FEWER PHOTOS ↑", more: "MORE PHOTOS" }
    : { open: "Otevřít menu", close: "Zavřít menu", igPost: "Příspěvek FOLLOW-ME na Instagramu", less: "MÉNĚ FOTEK ↑", more: "DALŠÍ FOTKY" };

  /* ---------- mobile menu ---------- */
  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("mobileMenu");

  if (toggle && menu) {
    var setMenu = function (open) {
      menu.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? T.close : T.open);
      document.body.style.overflow = open ? "hidden" : "";
      var f = document.getElementById("inviteFab"); if (f) f.style.visibility = open ? "hidden" : "";
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

  /* ---------- instagram: hlavní galerie (živý feed přes Behold) ---------- */
  // Když má sekce v data-feed JSON adresu feedu z behold.so, nahradí statické
  // dlaždice posledními 4 příspěvky (první velký, poslední dlaždice „Sledujte nás“).
  // Při chybě nebo bez adresy zůstane výběr fotek z HTML.
  var igSection = document.querySelector(".ig-section");
  var igGrid = document.getElementById("igGrid");
  var feedUrl = igSection && igSection.getAttribute("data-feed");
  var NS_SVG = "http://www.w3.org/2000/svg";
  var badge = function (type) {
    var svg = document.createElementNS(NS_SVG, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("class", "ig-badge");
    svg.setAttribute("aria-hidden", "true");
    var path = document.createElementNS(NS_SVG, "path");
    path.setAttribute("fill", "currentColor");
    path.setAttribute("d", type === "VIDEO"
      ? "M8 5.5v13l11-6.5z"
      : "M7 3h12a2 2 0 0 1 2 2v12h-2V5H7zM3 7h12a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2z");
    svg.appendChild(path);
    return svg;
  };
  var fmtNum = function (n) { return Number(n).toLocaleString(EN ? "en-GB" : "cs-CZ"); };

  if (igGrid && feedUrl && window.fetch) {
    fetch(feedUrl)
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        var posts = (Array.isArray(data) ? data : data.posts || []).filter(function (p) { return p && p.permalink; });
        // dva řádky: 1 velký příspěvek (2 × 2) + 3 malé + dlaždice „Sledujte nás“
        if (posts.length < 4) return;
        posts = posts.slice(0, 4);
        var cta = igGrid.querySelector(".ig-cta");
        igGrid.innerHTML = "";
        posts.forEach(function (post, i) {
          var big = i === 0;
          var sizes = post.sizes || {};
          var pick = (big ? (sizes.large || sizes.medium) : (sizes.medium || sizes.small)) || {};
          var src = pick.mediaUrl || (post.mediaType === "VIDEO" ? post.thumbnailUrl : post.mediaUrl) || post.thumbnailUrl;
          if (!src) return;
          var caption = (post.prunedCaption || post.caption || "").trim();
          var a = document.createElement("a");
          a.className = "ig-tile" + (big ? " is-big" : "");
          a.href = post.permalink;
          a.target = "_blank";
          a.rel = "noopener";
          var img = document.createElement("img");
          img.src = src;
          img.alt = caption ? caption.split("\n")[0].slice(0, 140) : T.igPost;
          img.loading = "lazy";
          a.appendChild(img);
          if (post.mediaType === "VIDEO" || post.mediaType === "CAROUSEL_ALBUM") a.appendChild(badge(post.mediaType));
          if (post.timestamp) {
            var d = new Date(post.timestamp);
            if (!isNaN(d)) {
              var date = document.createElement("span");
              date.className = "ig-date mono";
              date.textContent = d.toLocaleDateString(EN ? "en-GB" : "cs-CZ", { day: "numeric", month: "short", year: "numeric" });
              a.appendChild(date);
            }
          }
          var hover = document.createElement("span");
          hover.className = "ig-hover";
          var cap = document.createElement("span");
          cap.className = "ig-cap mono";
          cap.textContent = caption || T.igPost;
          hover.appendChild(cap);
          a.appendChild(hover);
          igGrid.appendChild(a);
        });
        if (cta) igGrid.appendChild(cta);
        igGrid.classList.add("is-live");
        var foot = document.getElementById("igFoot");
        if (foot) foot.textContent = EN ? "Latest posts from our Instagram." : "Nejnovější příspěvky z našeho Instagramu.";
        if (data.profilePictureUrl) document.getElementById("igAvatar").src = data.profilePictureUrl;
        if (data.followersCount != null) {
          document.getElementById("igFollowers").textContent = fmtNum(data.followersCount);
          var cnt = data.mediaCount != null ? data.mediaCount : null;
          var cntBox = document.getElementById("igCount");
          if (cnt != null) cntBox.textContent = fmtNum(cnt); else cntBox.parentNode.hidden = true;
          document.getElementById("igStats").hidden = false;
        }
      })
      .catch(function () { /* necháme výběr fotek z HTML */ });
  }

  /* ---------- galerie: další fotky + prohlížeč ---------- */
  var moreBtn = document.getElementById("galleryMoreBtn");
  var moreGrid = document.getElementById("galleryMore");
  if (moreBtn && moreGrid) {
    moreBtn.addEventListener("click", function () {
      var show = moreGrid.hidden;
      moreGrid.hidden = !show;
      moreBtn.setAttribute("aria-expanded", show ? "true" : "false");
      moreBtn.textContent = show ? T.less : T.more + " (" + moreGrid.children.length + ") ↓";
    });
  }

  var lb = document.getElementById("lightbox");
  if (lb && lb.showModal) {
    var lbImg = document.getElementById("lbImg");
    var lbCap = document.getElementById("lbCap");
    var lbCount = document.getElementById("lbCount");
    var tiles = [];
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

    // každá skupina fotek se prochází zvlášť: výběr v galerii Instagram a fotoarchiv
    document.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("a.g-tile, a[data-lightbox]") : null;
      if (!t) return;
      e.preventDefault();
      var sel = t.matches("a[data-lightbox]") ? 'a[data-lightbox="' + t.getAttribute("data-lightbox") + '"]' : "a.g-tile";
      tiles = Array.prototype.slice.call(document.querySelectorAll(sel)).filter(function (x) { return x.offsetParent !== null || x.hasAttribute("data-lightbox"); });
      show(Math.max(0, tiles.indexOf(t)));
      lb.showModal();
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
  // Akce se spravují v /admin. Jeden soubor napájí tabulku, odpočet v úvodu
  // i mapu sezóny. Zobrazují se jen budoucí akce; když žádné nejsou, zůstane
  // v tabulce výchozí řádek „Kalendář připravujeme“ z HTML.
  var en = EN;
  var eventsBody = document.getElementById("eventsBody");
  var LABEL = en
    ? { confirmed: "CONFIRMED", tbc: "TO BE CONFIRMED", cancelled: "CANCELLED", date: "Date", place: "Location", event: "Event", status: "Status", more: "Event website" }
    : { confirmed: "POTVRZENO", tbc: "BUDE UPŘESNĚNO", cancelled: "ZRUŠENO", date: "Datum", place: "Místo", event: "Akce", status: "Stav", more: "Web akce" };
  var MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  var fmtDate = function (iso) {
    var p = iso.split("-");
    return en ? +p[2] + " " + MONTHS[+p[1] - 1] + " " + p[0] : +p[2] + ". " + +p[1] + ". " + p[0];
  };
  var fmtRange = function (e) {
    if (!e.dateTo) return fmtDate(e.date);
    var a = e.date.split("-"), b = e.dateTo.split("-");
    if (a[0] === b[0] && a[1] === b[1]) {
      return en ? +a[2] + "–" + fmtDate(e.dateTo) : +a[2] + ".–" + fmtDate(e.dateTo);
    }
    return fmtDate(e.date) + " – " + fmtDate(e.dateTo);
  };
  var pad2 = function (n) { return (n < 10 ? "0" : "") + n; };
  var now = new Date();
  var today = now.getFullYear() + "-" + pad2(now.getMonth() + 1) + "-" + pad2(now.getDate());
  var dataSrc = (eventsBody && eventsBody.getAttribute("data-src")) || "data/events.json";

  var eventsPromise = window.fetch
    ? fetch(dataSrc)
        .then(function (r) { return r.ok ? r.json() : []; })
        .then(function (list) {
          return (Array.isArray(list) ? list : []).filter(function (e) {
            return e && e.date && (e.dateTo || e.date) >= today;
          }).sort(function (a, b) { return a.date.localeCompare(b.date); });
        })
        .catch(function () { return []; })
    : Promise.resolve([]);

  // tabulka
  var cell = function (label, child) {
    var td = document.createElement("td");
    td.setAttribute("data-label", label);
    if (typeof child === "string") td.textContent = child; else td.appendChild(child);
    return td;
  };
  eventsPromise.then(function (upcoming) {
    if (!eventsBody || !upcoming.length) return;
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
  });

  /* ---------- příští vystoupení (odpočet v úvodu) ---------- */
  var nextBox = document.getElementById("nextEvent");
  var daysLabel = function (d) {
    if (en) return d === 0 ? "TODAY" : d === 1 ? "TOMORROW" : "IN " + d + " DAYS";
    if (d === 0) return "DNES";
    if (d === 1) return "ZÍTRA";
    return "ZA " + d + (d >= 2 && d <= 4 ? " DNY" : " DNÍ");
  };
  eventsPromise.then(function (upcoming) {
    var next = upcoming.filter(function (e) { return e.status !== "cancelled"; })[0];
    if (!nextBox) return;
    if (!next) { nextBox.hidden = true; return; }
    var t0 = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    var p = next.date.split("-");
    var days = Math.round((Date.UTC(+p[0], +p[1] - 1, +p[2]) - t0) / 86400000);
    document.getElementById("neName").textContent = next.name;
    document.getElementById("neMeta").textContent = fmtRange(next) + (next.location ? " · " + next.location : "");
    document.getElementById("neCount").textContent = days < 0 ? (en ? "HAPPENING NOW" : "PRÁVĚ PROBÍHÁ") : daysLabel(days);
    nextBox.classList.remove("is-pending"); nextBox.removeAttribute("aria-hidden"); nextBox.removeAttribute("tabindex");
  });

  /* ---------- mapa sezóny ---------- */
  var pins = document.getElementById("mapPins");
  if (pins) {
    var NS = "http://www.w3.org/2000/svg";
    var LON0 = +pins.getAttribute("data-lon0"), LAT1 = +pins.getAttribute("data-lat1");
    var K = +pins.getAttribute("data-k"), COS = +pins.getAttribute("data-cos");
    var proj = function (lat, lng) { return [(lng - LON0) * COS * K, (LAT1 - lat) * K]; };
    var el = function (tag, attrs, parent) {
      var n = document.createElementNS(NS, tag);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      (parent || pins).appendChild(n);
      return n;
    };
    // síť poledníků a rovnoběžek jako na letecké mapě
    var vb = pins.viewBox.baseVal;
    for (var lon = 11; lon <= 24; lon++) {
      var x = proj(50, lon)[0];
      el("line", { x1: x, y1: 0, x2: x, y2: vb.height, "class": "grid" });
      if (lon % 2 === 0) el("text", { x: x + 2, y: vb.height - 4, "class": "grid-t" }).textContent = lon + "°E";
    }
    for (var lat = 47; lat <= 53; lat++) {
      var y = proj(lat, 11)[1];
      el("line", { x1: 0, y1: y, x2: vb.width, y2: y, "class": "grid" });
      el("text", { x: 3, y: y - 2, "class": "grid-t" }).textContent = lat + "°N";
    }
    var HOME = { lat: 49.9283, lng: 18.0783 };
    var hp = proj(HOME.lat, HOME.lng);
    var routes = el("g", {});
    var pinLayer = el("g", {});

    eventsPromise.then(function (upcoming) {
      var located = upcoming.filter(function (e) { return typeof e.lat === "number" && typeof e.lng === "number"; });
      located.forEach(function (e) {
        var p = proj(e.lat, e.lng);
        var dx = p[0] - hp[0], dy = p[1] - hp[1];
        var mx = (hp[0] + p[0]) / 2 - dy * 0.18, my = (hp[1] + p[1]) / 2 + dx * 0.18;
        el("path", { d: "M" + hp[0] + " " + hp[1] + " Q" + mx + " " + my + " " + p[0] + " " + p[1], "class": "route" }, routes);
        var g = el("g", { "class": "pin" + (e.status === "cancelled" ? " cancelled" : ""), tabindex: "0" }, pinLayer);
        el("circle", { cx: p[0], cy: p[1], r: 4, "class": "p" }, g);
        var left = p[0] > vb.width - 120;
        var anchor = left ? "end" : "start", tx = p[0] + (left ? -8 : 8);
        el("text", { x: tx, y: p[1] + 3, "text-anchor": anchor }, g).textContent = fmtRange(e);
        el("text", { x: tx, y: p[1] + 14, "text-anchor": anchor, "class": "pin-name" }, g).textContent = e.name;
        el("title", {}, g).textContent = e.name + " — " + fmtRange(e) + (e.location ? ", " + e.location : "");
        g.addEventListener("click", function () { var t = document.getElementById("events"); if (t) t.scrollIntoView({ behavior: "smooth" }); });
      });
      var home = el("g", { "class": "pin home" }, pinLayer);
      el("circle", { cx: hp[0], cy: hp[1], r: 5, "class": "pulse" }, home);
      el("circle", { cx: hp[0], cy: hp[1], r: 5, "class": "p" }, home);
      el("text", { x: hp[0] + 8, y: hp[1] + 15 }, home).textContent = "LKZA";
      // mapa se ukáže, až když je co ukázat (aspoň jedna akce se souřadnicemi)
      var mapBox = document.getElementById("seasonMap");
      if (mapBox && located.length) mapBox.hidden = false;
    });
  }

  /* ---------- interaktivní formace ---------- */
  var fdNodes = document.querySelectorAll(".fd-node");
  var fdItems = document.querySelectorAll(".formation-item[data-pos]");
  var setPos = function (pos) {
    [].forEach.call(fdNodes, function (n) { n.classList.toggle("is-active", n.getAttribute("data-pos") === pos); });
    [].forEach.call(fdItems, function (n) { n.classList.toggle("is-active", n.getAttribute("data-pos") === pos); });
  };
  [].forEach.call(fdNodes, function (n) {
    var pos = n.getAttribute("data-pos");
    var go = function () {
      var card = document.getElementById(n.getAttribute("data-pilot"));
      if (card) { card.scrollIntoView({ behavior: "smooth", block: "center" }); history.replaceState(null, "", "#" + card.id); }
    };
    n.addEventListener("mouseenter", function () { setPos(pos); });
    n.addEventListener("focus", function () { setPos(pos); });
    n.addEventListener("mouseleave", function () { setPos(null); });
    n.addEventListener("blur", function () { setPos(null); });
    n.addEventListener("click", go);
    n.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
  });
  [].forEach.call(fdItems, function (n) {
    n.addEventListener("mouseenter", function () { setPos(n.getAttribute("data-pos")); });
    n.addEventListener("mouseleave", function () { setPos(null); });
  });

  /* ---------- poptávka vystoupení ---------- */
  // Bez serveru: složí přehledný e-mail a otevře ho v poštovním programu návštěvníka.
  var form = document.getElementById("inviteForm");
  if (form) {
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var bad = [];
      [].forEach.call(form.querySelectorAll("[required]"), function (f) {
        var ok = f.value.trim() && (f.type !== "email" || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.value.trim()));
        f.classList.toggle("is-invalid", !ok);
        if (!ok) bad.push(f);
      });
      document.getElementById("inviteError").hidden = !bad.length;
      if (bad.length) { bad[0].focus(); return; }
      var v = function (n) { return (form.elements[n].value || "").trim(); };
      var date = v("date") ? fmtDate(v("date")) : "";
      var L = en
        ? ["Event", "Type", "Date", "Location", "Name", "Organisation", "Email", "Phone", "Message", "Event enquiry"]
        : ["Akce", "Typ", "Datum", "Místo", "Jméno", "Organizace", "E-mail", "Telefon", "Zpráva", "Poptávka vystoupení"];
      var lines = [
        L[0] + ": " + v("event"), L[1] + ": " + v("type"), L[2] + ": " + date, L[3] + ": " + v("place"), "",
        L[4] + ": " + v("name"), L[5] + ": " + (v("org") || "—"), L[6] + ": " + v("email"), L[7] + ": " + (v("phone") || "—")
      ];
      if (v("msg")) lines.push("", L[8] + ":", v("msg"));
      var subject = L[9] + ": " + v("event") + " (" + date + ")";
      window.location.href = "mailto:follow-me@email.cz?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
    form.addEventListener("input", function (e) { e.target.classList.remove("is-invalid"); });
  }

  /* ---------- lišta po odrolování ---------- */
  var navBar = document.querySelector(".nav");
  if (navBar) {
    var onScroll = function () { navBar.classList.toggle("is-scrolled", window.scrollY > 40); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- slideshow fotogalerie ---------- */
  var ss = document.getElementById("slideshow");
  if (ss) {
    var slides = [].slice.call(ss.querySelectorAll(".ss-slide"));
    var dots = [].slice.call(ss.querySelectorAll(".ss-dot"));
    var bar = ss.querySelector(".ss-progress span");
    var idx = 0, timer = null, DELAY = 6000;
    var loadSlide = function (s) {
      var img = s.querySelector("img");
      if (img && img.dataset.src) {
        img.srcset = img.dataset.srcset; img.src = img.dataset.src;
        delete img.dataset.src; delete img.dataset.srcset;
      }
    };
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var go = function (i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) {
        var on = k === idx;
        s.classList.toggle("is-active", on);
        if (on) { s.removeAttribute("aria-hidden"); s.removeAttribute("tabindex"); }
        else { s.setAttribute("aria-hidden", "true"); s.setAttribute("tabindex", "-1"); }
        if (on) loadSlide(s);
      });
      dots.forEach(function (d, k) { d.classList.toggle("is-active", k === idx); d.setAttribute("aria-selected", k === idx ? "true" : "false"); });
      // přednačíst další fotku
      loadSlide(slides[(idx + 1) % slides.length]);
      restart();
    };
    var restart = function () {
      clearTimeout(timer);
      ss.classList.remove("is-playing"); void bar.offsetWidth;
      if (reduce || ss.dataset.paused) return;
      ss.style.setProperty("--ss-time", DELAY + "ms");
      ss.classList.add("is-playing");
      timer = setTimeout(function () { go(idx + 1); }, DELAY);
    };
    var pause = function (on) { if (on) ss.dataset.paused = "1"; else delete ss.dataset.paused; restart(); };
    ss.querySelector(".ss-prev").addEventListener("click", function () { go(idx - 1); });
    ss.querySelector(".ss-next").addEventListener("click", function () { go(idx + 1); });
    dots.forEach(function (d, k) { d.addEventListener("click", function () { go(k); }); });
    ss.addEventListener("mouseenter", function () { pause(true); });
    ss.addEventListener("mouseleave", function () { pause(false); });
    ss.addEventListener("focusin", function () { pause(true); });
    ss.addEventListener("focusout", function () { pause(false); });
    ss.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") go(idx - 1);
      if (e.key === "ArrowRight") go(idx + 1);
    });
    var sx = null;
    ss.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; pause(true); }, { passive: true });
    ss.addEventListener("touchend", function (e) {
      if (sx !== null) { var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(idx + (dx < 0 ? 1 : -1)); }
      sx = null; pause(false);
    });
    // přehrávat jen když je slideshow na obrazovce
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { pause(!en[0].isIntersecting); }, { threshold: 0.3 }).observe(ss);
    } else { restart(); }
  }

  /* ---------- plovoucí tlačítko poptávky ---------- */
  // Schová se, když je na obrazovce formulář poptávky nebo otevřené mobilní menu.
  var fab = document.getElementById("inviteFab");
  var inviteSec = document.getElementById("invite");
  if (fab && inviteSec && "IntersectionObserver" in window) {
    new IntersectionObserver(function (en) {
      fab.classList.toggle("is-hidden", en[0].isIntersecting);
    }, { threshold: 0.15 }).observe(inviteSec);
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
