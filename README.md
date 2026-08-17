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
Jména pilotů (Tomáš, Bohdan, Lubo, Jarda, Jiří), pozice ve formaci, registrace
strojů (OK-KNR, OK-MPR, OK-LPR, OK-SEN), typy letadel, LKZA a souřadnice,
e-mail a Facebook — vychází z aktuálně dostupného obsahu na follow-me.cz.

## Co je potřeba doplnit / ověřit s klientem
- **Fotografie.** Všechny portréty pilotů a fotky ve strojích/galerii jsou
  zatím abstraktní SVG/CSS placeholdery v barvách značky — ne skutečné
  snímky. Jakmile dodáte fotoarchiv, nahradíme je 1:1 ve stejném ořezu.
- **Chybějící čísla.** U Bohdana (výška/váha/hodiny), Jardy (věk/hodiny) a
  Jiřího (věk/hodiny/přesná pozice) starý web čísla neuváděl — na webu jsou
  proto pomlčky místo vymyšlených hodnot.
- **Pátý pilot.** Web nyní počítá s pěti piloty (Tomáš, Bohdan, Lubo, Jarda,
  Jiří), protože pátý profil byl na starém webu skutečně publikován. Pozici
  Jiřího ve formaci (slot/záloha) je potřeba s týmem potvrdit.
- **Kalendář akcí.** Sekce Events je hotová komponenta, ale bez vymyšlených
  dat — termíny je potřeba doplnit podle aktuálního kalendáře.
- **Jazykové mutace.** Přepínač CZ/EN/PL/DE je zatím jen vizuální — reálný
  vícejazyčný obsah není zapojený.

## Technické poznámky
- Fonty: Oswald (display), Inter (body), IBM Plex Mono (technická data) —
  načítané z Google Fonts.
- Responzivní od mobilu po velké monitory, `prefers-reduced-motion` je
  respektováno.
- Bez frameworku — čistý HTML/CSS/JS, snadno se předá jakémukoli vývojáři
  k napojení na CMS.
