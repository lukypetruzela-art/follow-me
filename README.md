# FOLLOW-ME — web (prototyp / v1)

Statický web (HTML/CSS/JS, bez buildu). Otevřete `index.html` v prohlížeči
nebo nahrajte celou složku na jakýkoli hosting.

## Struktura
```
index.html        — celý jednostránkový web (hero, team, machines, formation,
                     gallery, events, fly with us, contact)
css/style.css      — design systém (barvy, typografie, komponenty)
js/main.js         — mobilní menu, vizuální jazykový přepínač, reveal animace
```

## Co je reálný obsah
Jména pilotů (Tomáš, Bob, Lubo, Jarda, Jiří), pozice ve formaci, registrace
strojů (OK-KNR, OK-MPR, OK-LPR, OK-SEN), typy letadel, LKZA a souřadnice,
e-mail a Facebook — vychází z aktuálně dostupného obsahu na follow-me.cz.
Portrétní fotky pilotů jsou reálné snímky dodané klientem, zpracované do
jednotného retro duotone stylu (viz níže).

## Fotografie pilotů
Pět dodaných portrétů (`assets/images/pilots/*.jpg`) prošlo stejným
zpracováním: převod do stupňů šedi, zvýšený kontrast, duotone remap do
barev webu (černá → teplá hliníková), jemné filmové zrno a vinětace — aby
seděly do industriální/archivní nálady webu a zároveň vypadaly jednotně, i
když byly pořízené každá jinde a jindy. Zdrojové barevné fotky nejsou v
repozitáři, jen zpracovaný výstup.

## Co je potřeba doplnit / ověřit s klientem
- **Fotky strojů a galerie.** Portréty pilotů už jsou reálné; fotky ve
  strojích a galerii jsou zatím abstraktní CSS placeholdery v barvách
  značky. Jakmile dodáte fotoarchiv letadel/akcí, nahradíme je stejným
  postupem jako portréty.
- **Chybějící čísla.** U Boba (výška/váha/hodiny), Jardy (věk/hodiny) a
  Jiřího (věk/hodiny/přesná pozice) starý web čísla neuváděl — na webu jsou
  proto pomlčky místo vymyšlených hodnot.
- **Pátý pilot.** Web nyní počítá s pěti piloty (Tomáš, Bob, Lubo, Jarda,
  Jiří), protože pátý profil byl na starém webu skutečně publikován. Pozici
  Jiřího ve formaci (slot/záloha) je potřeba s týmem potvrdit.
- **Kalendář akcí.** Sekce Events je hotová komponenta, ale bez vymyšlených
  dat — termíny je potřeba doplnit podle aktuálního kalendáře.
- **Jazykové mutace.** Přepínač CZ/EN/PL/DE je v `index.html` zakomentovaný,
  dokud nebudou hotové překlady — nefunkční tlačítka by návštěvníky mátla.
- **Fotky formace.** Dvě reálné fotky (formace ve vzduchu, OK-KNR na trávě)
  jsou v `assets/images/gallery/` — použité v galerii, v pásu s citátem a
  v sekci Instagram. Ostatní dlaždice galerie jsou zatím zástupné.
- **Instagram.** Sekce `#instagram` odkazuje na @follow_me_airshow_team.
  Pro živý feed založte zdroj na behold.so a jeho JSON URL vložte do atributu
  `data-feed` u `.ig-section` — web pak sám ukáže posledních 6 příspěvků.

## Technické poznámky
- Fonty: Oswald (display), Inter (body), IBM Plex Mono (technická data) —
  načítané z Google Fonts.
- Responzivní od mobilu po velké monitory, `prefers-reduced-motion` je
  respektováno.
- Bez frameworku — čistý HTML/CSS/JS, snadno se předá jakémukoli vývojáři
  k napojení na CMS.


## Jazykové verze
- **Čeština je hlavní** (`index.html`, adresa `/`). Angličtina je v `en/index.html` (adresa `/en/`).
- `en/index.html` se needituje ručně — vytváří ho skript z české verze:
  ```
  python3 tools/build_en.py
  ```
  Po změně českého textu doplňte jeho anglický překlad do `tools/build_en.py`
  a skript spusťte. Když nějaký text nemá překlad, skript skončí chybou a
  vypíše ho.

## Kalendář akcí (administrace)
- Akce jsou v `data/events.json`, web z nich sám vypíše budoucí termíny
  (česky i anglicky). Proběhlé akce se nezobrazují.
- Administrace: **`/admin`** — přihlášení heslem, přidání / úprava / smazání,
  tlačítko „Uložit a zveřejnit“. Uložení vytvoří commit v GitHubu a Vercel web
  do minuty znovu nasadí.
- Jednorázové nastavení ve Vercelu (Project → Settings → Environment Variables):
  | Proměnná | Hodnota |
  |---|---|
  | `ADMIN_PASSWORD` | heslo do administrace, aspoň 12 znaků |
  | `GITHUB_TOKEN` | fine-grained token: jen repozitář `follow-me`, oprávnění **Contents: Read and write** |

  Token: GitHub → Settings → Developer settings → Personal access tokens →
  Fine-grained tokens → Generate new token → Repository access: *Only select
  repositories* → `follow-me` → Permissions: *Contents → Read and write*.
  Po uložení proměnných ve Vercelu dejte **Redeploy**.

## Instagram (živý feed)
Sekce `#instagram` umí ukazovat posledních 6 příspěvků přes službu Behold.
JSON adresu feedu vložte do atributu `data-feed` u `<section class="ig-section">`
v `index.html` a spusťte `python3 tools/build_en.py`.
