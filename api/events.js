// FOLLOW-ME — API pro správu kalendáře akcí (Vercel serverless funkce).
// GET  /api/events  → aktuální seznam akcí + sha souboru (jen pro admina)
// PUT  /api/events  → uloží seznam akcí jako commit do GitHubu, Vercel pak web znovu nasadí
//
// Nastavení ve Vercelu (Settings → Environment Variables):
//   ADMIN_PASSWORD  heslo do administrace (aspoň 12 znaků)
//   GITHUB_TOKEN    fine-grained token jen pro repozitář follow-me, oprávnění Contents: Read and write
//   GITHUB_REPO     volitelně, výchozí "lukypetruzela-art/follow-me"
//   GITHUB_BRANCH   volitelně, výchozí "main"

const crypto = require("crypto");

const FILE = "data/events.json";
const STATUSES = ["confirmed", "tbc", "cancelled"];
const DATE = /^\d{4}-\d{2}-\d{2}$/;

const sha256 = (s) => crypto.createHash("sha256").update(String(s)).digest();
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

function checkPassword(given) {
  const expected = process.env.ADMIN_PASSWORD || "";
  if (expected.length < 12 || !given) return false;
  // porovnání v konstantním čase
  return crypto.timingSafeEqual(sha256(given), sha256(expected));
}

function clean(str, max) {
  return String(str == null ? "" : str).replace(/[\u0000-\u001f]/g, " ").trim().slice(0, max);
}

function validate(list) {
  if (!Array.isArray(list)) throw new Error("Data musí být seznam akcí.");
  if (list.length > 200) throw new Error("Maximálně 200 akcí.");
  return list.map((e, i) => {
    const n = i + 1;
    const date = clean(e.date, 10);
    const dateTo = clean(e.dateTo, 10);
    const name = clean(e.name, 120);
    const location = clean(e.location, 120);
    const status = STATUSES.includes(e.status) ? e.status : "tbc";
    const link = clean(e.link, 300);
    const note = clean(e.note, 200);
    if (!DATE.test(date) || isNaN(Date.parse(date))) throw new Error(`Akce ${n}: chybí nebo je špatně datum.`);
    if (dateTo && (!DATE.test(dateTo) || dateTo < date)) throw new Error(`Akce ${n}: datum „do“ je špatně.`);
    if (!name) throw new Error(`Akce ${n}: chybí název.`);
    if (link && !/^https:\/\/[^\s"<>]+$/.test(link)) throw new Error(`Akce ${n}: odkaz musí začínat https://`);
    const id = /^[a-z0-9-]{1,40}$/.test(e.id || "") ? e.id : crypto.randomBytes(6).toString("hex");
    const out = { id, date, name, location, status };
    if (dateTo && dateTo !== date) out.dateTo = dateTo;
    const lat = Number(e.lat), lng = Number(e.lng);
    if (e.lat != null && e.lat !== "" && e.lng != null && e.lng !== "") {
      if (!(lat >= 35 && lat <= 65 && lng >= -15 && lng <= 40)) throw new Error(`Akce ${n}: souřadnice jsou mimo Evropu.`);
      out.lat = Math.round(lat * 10000) / 10000;
      out.lng = Math.round(lng * 10000) / 10000;
    }
    if (link) out.link = link;
    if (note) out.note = note;
    return out;
  }).sort((a, b) => a.date.localeCompare(b.date));
}

async function github(path, options = {}) {
  const repo = process.env.GITHUB_REPO || "lukypetruzela-art/follow-me";
  const res = await fetch(`https://api.github.com/repos/${repo}/${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "follow-me-admin",
      ...(options.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  return { status: res.status, body };
}

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Robots-Tag", "noindex");

  if (!process.env.ADMIN_PASSWORD || !process.env.GITHUB_TOKEN) {
    return res.status(500).json({ error: "Administrace není nastavená (chybí proměnné ve Vercelu)." });
  }
  if (!checkPassword(req.headers["x-admin-password"])) {
    await wait(1000); // zpomalí zkoušení hesel
    return res.status(401).json({ error: "Špatné heslo." });
  }

  const branch = process.env.GITHUB_BRANCH || "main";

  if (req.method === "GET") {
    const r = await github(`contents/${FILE}?ref=${branch}`);
    if (r.status === 404) return res.json({ events: [], sha: null });
    if (r.status !== 200) return res.status(502).json({ error: "GitHub neodpovídá (zkontrolujte GITHUB_TOKEN)." });
    let events = [];
    try { events = JSON.parse(Buffer.from(r.body.content, "base64").toString("utf8")); } catch (e) {}
    return res.json({ events, sha: r.body.sha });
  }

  if (req.method === "PUT") {
    let events;
    let sha;
    try {
      const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body || {};
      events = validate(body.events);
      sha = body.sha || undefined;
    } catch (e) {
      return res.status(400).json({ error: e.message });
    }
    const content = Buffer.from(JSON.stringify(events, null, 2) + "\n", "utf8").toString("base64");
    const r = await github(`contents/${FILE}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Kalendář akcí: úprava z administrace", content, sha, branch }),
    });
    if (r.status === 409 || r.status === 422) {
      return res.status(409).json({ error: "Kalendář mezitím upravil někdo jiný. Načtěte ho znovu." });
    }
    if (r.status !== 200 && r.status !== 201) {
      return res.status(502).json({ error: "Uložení do GitHubu selhalo (zkontrolujte GITHUB_TOKEN)." });
    }
    return res.json({ events, sha: r.body.content && r.body.content.sha });
  }

  res.setHeader("Allow", "GET, PUT");
  return res.status(405).json({ error: "Nepodporovaná metoda." });
};
