#!/usr/bin/env python3
"""Vytvoří anglickou verzi webu (en/index.html) z české hlavní stránky (index.html).

Použití:  python3 tools/build_en.py

Hlavní je česká verze. Po každé změně textu v index.html doplňte překlad sem
a skript spusťte znovu. Když nějaký český text v index.html nenajde, skončí
chybou a vypíše, který — anglická verze tak nikdy nezůstane napůl česká.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://follow-me-blond.vercel.app"

# (český text, anglický text) — mezery a zalomení řádků nehrají roli
TEXT = [
    # ---------- hlavička
    ('<html lang="cs">', '<html lang="en">'),
    ('<title>FOLLOW-ME — formační letecký tým · LKZA Zábřeh</title>',
     '<title>FOLLOW-ME — Formation Display Team · LKZA Zábřeh, Czech Republic</title>'),
    ('content="FOLLOW-ME — formační tým čtyř historických strojů Zlín Z-226 a Z-326. Domovská základna LKZA, Zábřeh u Hlučína."',
     'content="FOLLOW-ME is a formation display team flying four vintage Zlín Z-226 and Z-326 aircraft. Home base: LKZA, Zábřeh near Hlučín, Czech Republic."'),
    ('content="FOLLOW-ME — pět pilotů. čtyři stroje. jedna formace."',
     'content="FOLLOW-ME — five pilots. four aircraft. one formation."'),
    ('content="Formační letecký tým historických strojů Zlín Z-226 / Z-326. LKZA Zábřeh u Hlučína."',
     'content="Formation display team flying vintage Zlín Z-226 / Z-326 aircraft. LKZA Zábřeh, Czech Republic."'),
    ('<meta property="og:locale" content="cs_CZ">',
     '<meta property="og:locale" content="en_GB">\n<meta property="og:locale:alternate" content="cs_CZ">'),

    ('<meta property="og:url" content="https://follow-me-blond.vercel.app/">', '<meta property="og:url" content="https://follow-me-blond.vercel.app/en/">'),
    ('/assets/images/og/og-cs.jpg"', '/assets/images/og/og-en.jpg"'),
    ('content="Čtyři stroje formace FOLLOW-ME v šikmé řadě před bouřkovými mraky"', 'content="Four FOLLOW-ME aircraft in echelon against storm clouds"'),

    # ---------- příští vystoupení, formace, mapa, poptávka
    ('<!-- Příští vystoupení: vyplní se samo z kalendáře (data/events.json). -->', '<!-- Next display: filled in automatically from data/events.json. -->'),
    ('</span>PŘÍŠTÍ VYSTOUPENÍ</span>', '</span>NEXT DISPLAY</span>'),
    ('aria-label="Schéma formace"', 'aria-label="Formation diagram"'),
    ('aria-label="Pozice 01 – vedoucí: Tomáš, OK-KNR"', 'aria-label="Position 01 – leader: Tomáš, OK-KNR"'),
    ('aria-label="Pozice 02 – pravé křídlo: Bob, OK-MPR"', 'aria-label="Position 02 – right wing: Bob, OK-MPR"'),
    ('aria-label="Pozice 03 – levé křídlo: Lubo, OK-LPR"', 'aria-label="Position 03 – left wing: Lubo, OK-LPR"'),
    ('aria-label="Pozice 04 – slot: Jarda, OK-SEN"', 'aria-label="Position 04 – slot: Jarda, OK-SEN"'),
    ('<h3 class="display">Mapa sezóny</h3>', '<h3 class="display">Season Map</h3>'),
    ('<span class="lg lg-home"></span>Domovské letiště LKZA <span class="lg lg-ev"></span>Vystoupení', '<span class="lg lg-home"></span>Home base LKZA <span class="lg lg-ev"></span>Displays'),
    ('aria-label="Mapa vystoupení v sezóně"', 'aria-label="Map of this season’s displays"'),
    ('Pořádáte leteckou akci? Pozvěte nás →', 'Organising an air event? Invite us →'),
    ('</span>PRO POŘADATELE</span>', '</span>FOR EVENT ORGANISERS</span>'),
    ('Pozvěte nás na vaši akci', 'Invite us to your event'),
    ('Letecký den, výročí letiště, firemní akce nebo přelet nad městem — čtyři historické Trenery ve formaci zvládnou na obloze i na zemi. Vyplňte pár údajů a my se vám ozveme.',
     'An air show, an airfield anniversary, a corporate event or a flypast over town — four vintage Trenérs in formation steal the show in the air and on the ground. Fill in a few details and we’ll get back to you.'),
    ('Formulář otevře váš e-mail s předvyplněnou zprávou na follow-me@email.cz.', 'The form opens your email app with a pre-filled message to follow-me@email.cz.'),
    ('<span class="mono">Jméno a příjmení *</span>', '<span class="mono">Full name *</span>'),
    ('<span class="mono">Organizace</span>', '<span class="mono">Organisation</span>'),
    ('<span class="mono">E-mail *</span>', '<span class="mono">Email *</span>'),
    ('<span class="mono">Telefon</span>', '<span class="mono">Phone</span>'),
    ('<span class="mono">Název akce *</span>', '<span class="mono">Event name *</span>'),
    ('<span class="mono">Typ akce</span>', '<span class="mono">Event type</span>'),
    ('<option>Letecký den</option>', '<option>Air show</option>'),
    ('<option>Výročí / den otevřených dveří letiště</option>', '<option>Airfield anniversary / open day</option>'),
    ('<option>Firemní nebo soukromá akce</option>', '<option>Corporate or private event</option>'),
    ('<option>Přelet nad akcí</option>', '<option>Flypast over an event</option>'),
    ('<option>Jiné</option>', '<option>Other</option>'),
    ('<span class="mono">Datum *</span>', '<span class="mono">Date *</span>'),
    ('<span class="mono">Místo / letiště *</span>', '<span class="mono">Location / airfield *</span>'),
    ('placeholder="např. Hradec Králové (LKHK)"', 'placeholder="e.g. Hradec Králové (LKHK)"'),
    ('<span class="mono">Zpráva</span>', '<span class="mono">Message</span>'),
    ('placeholder="Program, předpokládaný čas vystoupení, počet diváků…"', 'placeholder="Programme, expected display time, expected crowd size…"'),
    ('ODESLAT POPTÁVKU →', 'SEND ENQUIRY →'),
    ('Vyplňte prosím povinná pole označená hvězdičkou.', 'Please fill in the required fields marked with an asterisk.'),

    # ---------- menu
    ('<nav class="nav" aria-label="Hlavní menu">', '<nav class="nav" aria-label="Main menu">'),
    ('<a href="#team">Tým</a>', '<a href="#team">Team</a>'),
    ('<a href="#machines">Stroje</a>', '<a href="#machines">Aircraft</a>'),
    ('<a href="#formation">Formace</a>', '<a href="#formation">Formation</a>'),
    ('<a href="#instagram">Galerie</a>', '<a href="#instagram">Gallery</a>'),
    ('<a href="#events">Kalendář</a>', '<a href="#events">Events</a>'),
    ('<a href="#fly">Létejte s námi</a>', '<a href="#fly">Fly with us</a>'),
    ('<a href="#contact">Kontakt</a>', '<a href="#contact">Contact</a>'),
    ('<div class="nav-lang mono" role="navigation" aria-label="Jazyk">\n    <a href="./" class="active" lang="cs" aria-current="page">CZ</a><span aria-hidden="true">/</span>\n    <a href="en/" lang="en" hreflang="en">EN</a>',
     '<div class="nav-lang mono" role="navigation" aria-label="Language">\n    <a href="../" lang="cs" hreflang="cs">CZ</a><span aria-hidden="true">/</span>\n    <a href="./" class="active" lang="en" aria-current="page">EN</a>'),
    ('<div class="mm-lang mono"><a href="./" class="active" aria-current="page">CZ</a><a href="en/" lang="en" hreflang="en">EN</a></div>',
     '<div class="mm-lang mono"><a href="../" lang="cs" hreflang="cs">CZ</a><a href="./" class="active" aria-current="page">EN</a></div>'),
    ('aria-label="Instagram FOLLOW-ME"', 'aria-label="Instagram FOLLOW-ME"'),
    ('aria-label="Otevřít menu"', 'aria-label="Open menu"'),

    # ---------- úvod
    ('aria-label="Znak FOLLOW-ME — Slezský aeroklub Zábřeh"', 'aria-label="FOLLOW-ME emblem — Silesian Aero Club Zábřeh"'),
    ('PĚT PILOTŮ.<br>\n      ČTYŘI STROJE.<br>\n      <span class="thin">JEDNA FORMACE.</span>',
     'FIVE PILOTS.<br>\n      FOUR MACHINES.<br>\n      <span class="thin">ONE FORMATION.</span>'),
    ('Formační tým historických strojů Zlín Z-226 a Z-326 z produkce Otrokovic. <b>Domovská základna LKZA, Zábřeh u Hlučína.</b>',
     'A formation display team flying vintage Zlín Z-226 and Z-326 aircraft, built in Otrokovice. <b>Home base: LKZA, Zábřeh near Hlučín.</b>'),
    ('<span class="label">DOMOVSKÉ LETIŠTĚ</span>', '<span class="label">HOME BASE</span>'),
    ('<span class="label">POSÁDKA</span>\n      <span class="value">05 PILOTŮ</span>', '<span class="label">CREW</span>\n      <span class="value">05 PILOTS</span>'),
    ('<span class="label">STROJE</span>', '<span class="label">AIRCRAFT</span>'),
    ('<span class="label">STAV</span>', '<span class="label">STATUS</span>'),
    ('</span>AKTIVNÍ FORMACE</span>', '</span>ACTIVE FORMATION</span>'),


    # ---------- tým
    ('<b>FOLLOW-ME</b> je formační tým, který od svého domovského letiště LKZA v Zábřehu u Hlučína — mezi Ostravou a Opavou — pravidelně vzlétá ve čtyřčlenné sestavě strojů Zlín Z-226 a Z-326. Piloti přezdívkami mezi sebou nešetří, veřejně je ale nepoužívají — na webu je tedy potkáte pod jmény, ne pod volacími znaky.',
     '<b>FOLLOW-ME</b> is a formation team that regularly takes off from its home airfield, LKZA in Zábřeh near Hlučín — between Ostrava and Opava — as a four-ship of Zlín Z-226 and Z-326 aircraft. The pilots have no shortage of nicknames for one another, but they keep them off the record — so on this site you will meet them by name, not by call sign.'),
    ('Stroje z produkce otrokovické továrny Moravan už dnes nemají akrobatické oprávnění — přesto formace trénuje předvedenou sestavu tak přesně a tak těsně, jak to jde. Za dobu, kdy se tým drží ve vzduchu, navštívil řadu airshow po celé zemi i za hranicemi a ukázal divákům přes šedesát let staré veterány, kteří dnes vypadají lépe, než když poprvé opustili výrobní halu.',
     'Built by the Moravan factory in Otrokovice, these aircraft are no longer cleared for aerobatics — yet the formation trains its display routine as precisely and as tightly as it can. Over the years the team has flown at airshows across the country and abroad, showing crowds veterans more than sixty years old that look better today than the day they first rolled out of the factory.'),
    ('<h2>Posádka</h2>', '<h2>Crew</h2>'),
    ('<span class="pilot-role-tag mono">VEDOUCÍ</span>', '<span class="pilot-role-tag mono">LEADER</span>'),
    ('<span class="pilot-role-tag mono">PRAVÉ KŘÍDLO</span>', '<span class="pilot-role-tag mono">RIGHT WING</span>'),
    ('<span class="pilot-role-tag mono">LEVÉ KŘÍDLO</span>', '<span class="pilot-role-tag mono">LEFT WING</span>'),
    ('<span class="pilot-role-tag mono">SLOT / ZÁLOHA</span>', '<span class="pilot-role-tag mono">SLOT / RESERVE</span>'),
    ('KARTA PILOTA / 05 — ZÁLOHA', 'PILOT FILE / 05 — RESERVE'),
    ('<span class="k">ŠKOLA</span><span class="v">ČVUT</span>', '<span class="k">UNIVERSITY</span><span class="v">CTU PRAGUE</span>'),
    ('<span class="k">POZICE</span><span class="v">SLOT</span>', '<span class="k">ROLE</span><span class="v">SLOT</span>'),

    # Tomáš
    ('Vedoucí formace — číslo <b>jedna</b>, navigace, komunikace, velení formace.',
     'Formation leader — number <b>one</b>: navigation, radio and command of the formation.'),
    ('Za knipl usedl poprvé ve čtrnácti na Blaníku. Dnes svoje účty platí jako kapitán-examinátor u dopravní společnosti, v malých strojích nalétá zhruba <b>50 hodin ročně</b>. V sestavě drží vedení, navigaci a komunikaci — jeho jediným cílem je létat tak čistě, aby na zádech kombinézy nezůstal otisk dvojky, která mu sedí za zády.',
     'He first took the stick at fourteen, in a Blaník glider. Today he pays the bills as a captain and examiner with an airline, and logs around <b>50 hours a year</b> in smaller aircraft. In the formation he handles the lead, navigation and radio — and his one aim is to fly so smoothly that number two, tucked in right behind him, never leaves a print on the back of his flight suit.'),
    ('žlutý s černou kostkou, stejnou, jakou nosí i vozy s nápisem „Follow me“',
     'yellow with black checks — the same pattern worn by airport “Follow me” cars'),
    # Bob
    ('Pravé křídlo — číslo <b>dvě</b>, ten, kdo drží pozici nalepený vpravo od jedničky.',
     'Right wing — number <b>two</b>, the one glued to the leader’s right.'),
    ('Létat se učil na Z-142 v devadesátých letech a od té doby zůstává věrný jen ryzí krvi řady Z-26. Civilně je ředitelem, na Treneru odlétá zhruba <b>50 až 100 hodin ročně</b>. Jeho úkolem v sestavě je držet se za jedničkou za každou cenu — otázka, jestli se na ni nespoléhá až moc, zůstává mezi piloty stálým vtipem. O stříbrný <b>OK-MPR</b> pečuje s péčí, která hraničí s posedlostí leštěním.',
     'He learned to fly on the Z-142 in the 1990s and has stayed loyal to the pure-bred Z-26 line ever since. A company director by day, he flies some <b>50 to 100 hours a year</b> in the Trenér. His job in the formation is to stay with number one at all costs — and whether he leans on the leader a little too much remains a running joke among the pilots. He looks after the silver <b>OK-MPR</b> with a devotion that borders on an obsession with polishing.'),
    ('stříbrný s červeno-bílou šachovnicí, sériové číslo 263',
     'silver with red-and-white checks, serial number 263'),
    # Lubo
    ('Levé křídlo — číslo <b>tři</b>, pozice, na které se prvotřídnost nedá fingovat.',
     'Left wing — number <b>three</b>, a position where you simply can’t fake top-class flying.'),
    ('První kroky udělal na spolehlivé Z-142, pak vystřídal několik typů, až se dostal ke dvoumotorovému dopravnímu letounu. Čtyři zlaté nášivky na rukávu kapitánské uniformy mu zároveň platí restaurování vlastního veterána — na Treneru tak nalétá jen kolem <b>20 hodin ročně</b>, nižší nálet musí vyvážit citem a promáčenou kombinézou. Je jediný člen týmu, který nepochází a nežije na moravském východě. Dřív sedával v <b>OK-SEN</b>, dnes létá s <b>OK-LPR</b> — registrace vznikla z jeho iniciál LP a stejného „R“ jako u zbytku formace.',
     'He started out on the dependable Z-142 and worked his way through several types to a twin-engine airliner. The four gold stripes on his captain’s sleeve also pay for the restoration of his own vintage aircraft — so he logs only about <b>20 hours a year</b> in the Trenér and makes up for it with feel and a sweat-soaked flight suit. He is the only member of the team who neither comes from nor lives in eastern Moravia. He used to fly <b>OK-SEN</b>; today he flies <b>OK-LPR</b> — a registration made from his initials, LP, plus the same “R” as the rest of the formation.'),
    ('světle zelený s vínovou šachovnicí, sériové číslo 020',
     'light green with maroon checks, serial number 020'),
    # Jarda
    ('Slot — číslo <b>čtyři</b>, „tail-end-charlie“ formace.',
     'Slot — number <b>four</b>, the formation’s “tail-end Charlie”.'),
    ('Do sestavy přibyl jako poslední a na pozici čtyřky si zvykl rychle a beze slov — doslova. Létá přesně a na rozdíl od upovídané dvojky a trojky v éteru mlčí. Civilně je vedoucím létání na domovském aeroklubu. V sestavě usedá do modro-žlutého <b>OK-SEN</b>, i když se proslýchá, že by raději usedl za žlutý ocas OK-KNR ve svém milovaném Brigadýru — tuhle úchylku si ale nechává většinou pro sebe.',
     'The last to join the team, he settled into the number-four slot quickly and without a word — literally. He flies with precision and, unlike the chatty numbers two and three, keeps quiet on the radio. Away from the formation he runs flight operations at the home aero club. In the display he flies the blue-and-yellow <b>OK-SEN</b>, though rumour has it he would rather be sitting behind the yellow tail of OK-KNR in his beloved Brigadýr — a quirk he mostly keeps to himself.'),
    ('modro-žlutý s černo-žlutou šachovnicí, první kus modifikace „MF“',
     'blue and yellow with black-and-yellow checks, the first “MF” variant ever built'),
    # Jiří
    ('Slot pilot, letecká rodina, technik od fochu.',
     'Slot pilot from a flying family, and an engineer to the core.'),
    ('Vystudoval strojní inženýrství na ČVUT a dnes vede firmu SKV Electronics and Mechanics, která staví stroje na míru. Je letovým instruktorem — na motorových letadlech i na kluzácích — a sám postavil dva ultralighty. S manželkou Janou, mistryní světa ve standardní třídě kluzáků z roku 2005 a několikanásobnou mistryní republiky, tvoří opravdovou leteckou rodinu; letectví propadl i jejich syn Jan. Sám má za sebou sólovou akrobacii v reprezentaci a titul juniorského mistra republiky. Ve volném čase lítá s RC modely, jezdí na kole, hraje tenis a jako obyvatel podhůří vyráží na běžky i sjezdovky.',
     'He studied mechanical engineering at the Czech Technical University in Prague and now runs SKV Electronics and Mechanics, a company that builds custom machinery. He is a flight instructor on both powered aircraft and gliders, and has built two ultralights himself. With his wife Jana — the 2005 Standard Class gliding world champion and a multiple Czech national champion — he makes up a true flying family; their son Jan has caught the flying bug too. He himself flew solo aerobatics for the national team and is a former Czech junior champion. In his spare time he flies RC models, cycles, plays tennis and, living in the foothills, heads out for cross-country and downhill skiing.'),

    # ---------- stroje
    ('<h2>Stroje</h2>', '<h2>Aircraft</h2>'),
    ('Čtyři stroje z produkce otrokovické továrny Moravan. Přes šedesát let staré, a přesto pořád ve vzduchu — stáří tu není slabina, je to kvalita.',
     'Four aircraft built by the Moravan factory in Otrokovice. More than sixty years old and still flying — here, age isn’t a weakness, it’s a mark of quality.'),
    ('<span class="k">VÝR. ČÍSLO</span>', '<span class="k">SERIAL</span>'),
    ('<span class="v">01 / VEDOUCÍ</span>', '<span class="v">01 / LEAD</span>'),
    ('<span class="v">02 / PRAVÉ</span>', '<span class="v">02 / RIGHT</span>'),
    ('<span class="v">03 / LEVÉ</span>', '<span class="v">03 / LEFT</span>'),
    ('<b>VEDOUCÍ FORMACE</b></div>', '<b>FORMATION LEAD</b></div>'),
    ('<b>PRAVÉ KŘÍDLO</b></div>', '<b>RIGHT WING</b></div>'),
    ('<b>LEVÉ KŘÍDLO</b></div>', '<b>LEFT WING</b></div>'),
    ('Žluto-černá kostkovaná MS, podle které formaci na zemi pozná i naprostý laik — stejné barvy nosí i doprovodná vozidla s nápisem „Follow me“. Vede formaci na pozici lídra.',
     'The yellow-and-black chequered MS that even a complete newcomer can pick out on the ground — the same colours worn by the airport “Follow me” cars that guide aircraft on the apron. It flies at the head of the formation.'),
    ('Stříbrný stroj s červeno-bílou šachovnicí, udržovaný s péčí hraničící s posedlostí leštěním. Létá na pravém křídle formace, přilepený k lídrovi za každého počasí.',
     'A silver aircraft with red-and-white checks, kept with a care that borders on an obsession with polishing. It flies on the formation’s right wing, glued to the leader in all weathers.'),
    ('První a jediný postavený kus modifikace „MF“ — na rozdíl od standardních 326 nese kovovou stavitelnou vrtuli místo dřevěné, kvůli čemuž musel být posunut i kokpit. Zkušební lety proběhly na začátku listopadu 1997, do Aeroklubu Zábřeh dorazila 15. listopadu. Kromě formace slouží i k vlekání kluzáků a přežila i tvrdší kontakt s matkou zemí na břiše trupu.',
     'The first and only example of the “MF” variant ever built. Unlike the standard 326, it carries a metal variable-pitch propeller instead of a wooden one, which meant the cockpit had to be moved as well. Test flights took place in early November 1997, and the aircraft arrived at the Zábřeh aero club on 15 November. Besides flying in the formation it tows gliders — and it has even survived a firm meeting with Mother Earth on its belly.'),

    # ---------- historie strojů
    ('<span>HISTORIE STROJE</span>', '<span>AIRCRAFT HISTORY</span>'),
    ('Tento Zlin 226 byl stvořen v roce 1957 v Otrokovicích pod výrobním číslem 103. Letecký život započal coby verze Z-226T a brzy získal logickou přezdívku <b>Kanár</b>. Když procházíme sadu starých palubních deníků, vidíme mnoho známých jmen. Poté, co již se svým motorem Walter Minor VI a tandemovým uspořádáním kabiny nebyl „moderní“ a nehodil se do výcvikových plánů mladých ani starých členů Svazarmu či budoucích žokejů MiGu-21, byl demontován, zčásti kanibalizován a odstaven do rohu hangáru. Ano, přesně do toho vlevo, nad kterým měly hnízdo poštolky…',
     'This Zlin 226 was built in 1957 in Otrokovice as serial number 103. It began its flying life as a Z-226T and soon earned the obvious nickname <b>Kanár</b> – the Canary. Leaf through its old logbooks and you will find plenty of familiar names. Once its Walter Minor VI engine and tandem cockpit were no longer “modern” and it no longer fitted the training plans of young and old Svazarm members or future MiG-21 jockeys, it was dismantled, partly cannibalised and pushed into a corner of the hangar. Yes, that very corner on the left, where the kestrels had their nest…'),
    ('V roce 1998 odvezl Tomáš s bráchou Danem zbytky Kanára k našemu příteli Milanovi do Holešova, aby jej ti šikovní chlapi od firmy Zlin-Avion podrobili generální opravě… lépe řečeno kompletní renovaci a přestavbě na čtyřválcovou Z-126T. („Asi jsme měli obavy z ropné krize.“ :)',
     'In 1998 Tomáš and his brother Dan took what was left of the Canary to our friend Milan in Holešov, so that the skilled crew at Zlin-Avion could give it a general overhaul… or rather a complete restoration and conversion into a four-cylinder Z-126T. (“We must have been worried about an oil crisis.” :)'),
    ('S brumlajícím Minorem IV se několikrát řítil mezi alpskými štíty či čeřil vlny moře… jeho čas však nadešel v roce 2007, kdy již bylo jasné, že při skupinovém létání je dýchavičný Walter špatným kamarádem pro šestiválce se stříkačkami a automatickými vrtulemi V-503. Opět tedy odletěl do hangáru Zlin-Avion k našemu dvornímu inženýrovi, tentokrát již do Otrokovic, kde jej excelentním způsobem zbavili staré pohonné jednotky a jako vždy elegantně „naroubovali“ nových 180 koní s kovovou vrtulí V-503A.',
     'With its humming Minor IV it raced between Alpine peaks and skimmed the waves of the sea more than once… but its time came in 2007, when it was clear that in formation flying the short-winded Walter was a poor companion for six-cylinder engines with fuel injection and V-503 constant-speed propellers. So once again it flew to the Zlin-Avion hangar and our in-house engineer, this time in Otrokovice, where they expertly removed the old powerplant and, as elegantly as ever, “grafted on” a new 180 horsepower with a metal V-503A propeller.'),
    ('I když je Kanár již deset let od generální opravy, asi nikdo kolem něj neprojde bez povšimnutí. Naopak lidé znalí ani po podrobnější prohlídce nevěří, že může stále tak dobře vypadat. Je to prostě sporťáček!',
     'Even though the Canary is now ten years past its overhaul, hardly anyone walks past it without a second look. People who know aircraft can’t believe, even after a closer inspection, that it still looks this good. It’s simply a little sports car!'),
    ('Empéerka je o něco mladší… roll-out v Otrokovicích se konal na podzim roku 1958. OK-MPR byl přidělen Slováckému aeroklubu v Kunovicích, kde poctivě sloužil až do konce sedmdesátých let. Byl zbarven tehdy obvyklou stříbrnou barvou, zkombinovanou s barevnými doplňky překrytu kabiny a koncových oblouků. Jaká to byla barva, se dnes už nikdo nepamatuje, ale dá se předpokládat, že to byla modrá.',
     '“Em-Pe-Er” is a little younger… it rolled out in Otrokovice in the autumn of 1958. OK-MPR was assigned to the Slovácko Aero Club in Kunovice, where it served faithfully until the end of the 1970s. It wore the silver finish usual at the time, combined with coloured trim on the canopy frame and wingtips. Nobody remembers today what colour it was, but it was most likely blue.'),
    ('Někdy v roce 1969, po obnovení motorového provozu v kunovickém aeroklubu (od roku 1963 to byla pouze „aerovleková stanice“), letoun dostal nový oranžový nátěr, podobný jako ostatní Trenéry v Kunovicích, které ale měly jiné barevné kombinace (OK-HLK, -IGT, -LHA, -MGE). Na počátku osmdesátých let byl OK-MPR přidělen do aeroklubu Brno-Medlánky, kde poctivě vlekal až do svého zrušení a vymazání z leteckého rejstříku.',
     'Around 1969, when powered flying resumed at the Kunovice aero club (from 1963 it had been only a “glider-towing station”), the aircraft received a new orange paint scheme, similar to the other Trenérs in Kunovice, which wore different colour combinations (OK-HLK, -IGT, -LHA, -MGE). In the early 1980s OK-MPR moved to the Brno-Medlánky aero club, where it towed gliders faithfully until it was retired and struck off the aircraft register.'),
    ('Letoun získalo Technické muzeum v Brně a na nádvoří kláštera voršilek v Orlí ulici, kde bylo sídlo muzea, jej bylo možno vídat chřadnout na dvorku řadu let spolu s MiGem-19. S Technickým muzeem pak později putoval do nového areálu v Králově Poli. Naštěstí ne všichni lidé souhlasí s názorem, že nejlepší je mít stará letadla zamknutá v muzejních sbírkách.',
     'The aircraft was acquired by the Technical Museum in Brno, and for many years it could be seen wasting away in the courtyard of the Ursuline convent on Orlí Street, the museum’s home at the time, alongside a MiG-19. It later moved with the museum to its new site in Královo Pole. Fortunately, not everyone agrees that old aircraft are best kept locked away in museum collections.'),
    ('Po renovaci do standardu Z-226MS u firmy Zlin-Avion se po mnoha smutných letech dne 23. 3. 2005 kolem třetí hodiny odpoledne opět vznesl. Jeho povrch díky stříbrné perleti <b>Alfa Romeo Nuvola</b> duhově zářil v jarním slunci. Šachovnicové doplňky v červené barvě Ferrari působily přímo výstražně.',
     'After restoration to Z-226MS standard at Zlin-Avion, and after many sad years, it took to the air again on 23 March 2005 at around three in the afternoon. Thanks to its <b>Alfa Romeo Nuvola</b> silver pearl finish, its surface shimmered in the spring sunshine, and the chequered trim in Ferrari red looked positively alarming.'),
    ('Stejně jako při letu s Kanárem si v OK-MPR můžete vychutnat sílu a zvuk dobře vyladěného motoru a vrtule, který žene letoun rychlostí 240 km/h v horizontu při průměrné spotřebě nepřesahující 35 l/hod. Je to prostě sporťáček!',
     'Just as in the Canary, in OK-MPR you can enjoy the power and sound of a well-tuned engine and propeller, driving the aircraft at 240 km/h in level flight while burning no more than 35 litres an hour on average. It’s simply a little sports car!'),
    ('LPRka spatřila světlo světa v roce 1957 v Otrokovicích s nápisem OK-KMX. V době svého stvoření byl její kokpit rovněž o něco chudší, než jak můžete vídat nyní, neboť v rodném listu stálo původně tovární označení Z-226 B. Tím bylo tomuto stroji dáno do vínku převážně vlekání větroňů. OK-KMX mohli spatřit návštěvníci například na letištích aeroklubu Náchod a Vrchlabí. Letecký rejstřík se o OK-KMX přestal zajímat roku 1991.',
     '“El-Pe-Er” first saw the light of day in 1957 in Otrokovice, registered OK-KMX. When it was built its cockpit was also rather more basic than it is today, as its birth certificate originally read Z-226 B – a variant destined mainly for towing gliders. Visitors could see OK-KMX at the Náchod and Vrchlabí aero club airfields, among others. The aircraft register lost interest in OK-KMX in 1991.'),
    ('Na podzim roku 2008 se odstavené KMXky v Kunovicích ujal Lubo, stroj opět putoval k dvornímu inženýrovi Milimu a na jaře 2009 opustila brány otrokovické firmy Zlin-Avion 226ka verze MS s názvem OK-LPR. Jarní sluníčko se odráželo od metalického povrchu zeleno-červeného kabátu, který světu jasně dával najevo, že skupinka má nový přírůstek – sporťáček.',
     'In the autumn of 2008 Lubo took on the grounded KMX in Kunovice. Once again the aircraft went to our in-house engineer Mili, and in the spring of 2009 a 226 in MS configuration, now named OK-LPR, rolled out through the gates of Zlin-Avion in Otrokovice. The spring sunshine glinted off its metallic green-and-red coat, telling the world loud and clear that the team had a new addition – a little sports car.'),
    ('Tento Zlin Z-326 sjel z výrobní linky pod číslem 893 v roce 1963. Zbývající měsíce třiašedesátého strávil poněkud neleteckým životem – zůstal „skladem“ na letišti ve Vyškově. Další rok působil ve stejně aktivní pozici, jen trochu opodál, domovem se mu stala Brno-Slatina. Konečně 8. června 1965 se objevil někdo, kdo by vzal 893ku do vzduchu.',
     'This Zlin Z-326 rolled off the production line as serial number 893 in 1963. It spent the rest of that year leading a rather un-aviation-like life – it stayed “in stock” at Vyškov airfield. The following year it held an equally active position just a little further away, at Brno-Slatina. Finally, on 8 June 1965, someone turned up to take 893 into the air.'),
    ('Na základě objednávky na deset strojů Z-326 se na trupu objevuje francouzská registrace F-BMQR a letoun začíná kariéru v letecké škole Chartres. O více než čtvrt století později se 893ka, tentokrát demontovaná na prvočinitele, vrací zpět do vlasti. Píše se rok 1992.',
     'As part of an order for ten Z-326s, the French registration F-BMQR appeared on its fuselage and the aircraft began a career at the flying school in Chartres. More than a quarter of a century later, 893 – this time taken apart down to its last components – returned home. The year was 1992.'),
    ('Po čtyřletém spánku se do stroje pouští parta ze Zlin-Avionu. Provedou jej dlouhou cestou totální generální opravy a konverze, na jejímž konci ze vrat hangáru vyjíždí modrožlutá kráska (kdo tohle vymyslel? :) nesoucí označení Z-326MF. To znamená, že na rozdíl od standardní třistadvacetšestky, která molekuly vzduchu rozháněla pomocí dřevěné vrtule, se na MFce zaleskly kovové listy automaticky stavitelné pětsettrojky (V-503) na přírubě motoru M 137. Hlavní kokpit se na této historicky první MFce musel kvůli centráži posunout dozadu.',
     'After a four-year slumber, the Zlin-Avion crew set to work on it. They took it through the long road of a total overhaul and conversion, at the end of which a blue-and-yellow beauty rolled out of the hangar doors (who came up with that? :) bearing the designation Z-326MF. This means that, unlike the standard 326, which pushed the air molecules aside with a wooden propeller, the MF gleams with the metal blades of a V-503 constant-speed propeller on the flange of its M 137 engine. On this very first MF the main cockpit had to be moved back to keep the centre of gravity right.'),
    ('Zálet provedla posádka ve složení Ing. Vlček a Pavel Paseka ve dnech 4. a 5. 11. 1997. Imatrikulací v režii inspektorů Úřadu M. Tošovského a Ing. Jirky Bláhy prošla o pět dní později. Dne 15. 11. si nový stroj vyzvedává s úsměvem na rtu náš kamarád Jirka Hořínka (dovedeme si představit tu misi mezi Holešovem a Zábřehem :). Od tohoto dne věrně slouží Aeroklubu Zábřeh, kde se používá také pro aerovleky.',
     'The test flights were flown by Ing. Vlček and Pavel Paseka on 4 and 5 November 1997, and the aircraft passed its registration inspection, run by inspectors M. Tošovský and Ing. Jirka Bláha, five days later. On 15 November our friend Jirka Hořínka collected the new aircraft with a smile on his face (we can just imagine that mission between Holešov and Zábřeh :). Since that day it has served the Zábřeh aero club faithfully, where it is also used for glider towing.'),
    ('Za ta léta již utržil několik šrámů, včetně velmi, ale velmi intimního kontaktu břicha s matičkou zemí, ale stále je to fešák. Zajímavý marking OK-SEN si mohli vychutnat také účastníci sletu Zlínů ve švýcarském Samedanu nedaleko St. Moritz, kam jej spolehlivě přivezl skupinář Mili. (Letiště Samedan leží ukryto v Alpách a honosí se slušnou nadmořskou výškou… nebudu napovídat, pro zajímavost mrkněte do mapy.)',
     'Over the years it has picked up a few scars, including a very, very intimate encounter between its belly and Mother Earth, but it is still a handsome thing. The eye-catching OK-SEN markings were also admired by those attending the Zlin fly-in at Samedan in Switzerland, near St. Moritz, where formation pilot Mili flew it reliably all the way. (Samedan airfield lies tucked away in the Alps and boasts a rather respectable elevation… we won’t give it away – have a look at the map.)'),
    ('Registrace vznikla z iniciál pilota (LP) a společného „R“ celé formace. Původně OK-KMX z roku 1957 — po renovaci u Zlin-Avionu létá od jara 2009 v metalickém zeleno-červeném kabátě.',
     'The registration comes from the pilot’s initials (LP) plus the “R” shared by the whole formation. Originally OK-KMX, built in 1957 — after restoration at Zlin-Avion it has flown since spring 2009 in a metallic green-and-red coat.'),
    ('<!-- Plovoucí tlačítko poptávky: vidět pořád, schová se jen u samotného formuláře. -->', '<!-- Floating enquiry button. -->'),
    ('<span>POZVĚTE NÁS K VÁM</span>', '<span>INVITE US TO YOUR EVENT</span>'),
    # ---------- formace
    ('<h2>Formace</h2>', '<h2>Formation</h2>'),
    ('01 · VEDOUCÍ</text>', '01 · LEAD</text>'),
    ('03 · LEVÉ</text>', '03 · LEFT</text>'),
    ('02 · PRAVÉ</text>', '02 · RIGHT</text>'),
    ('<h3 class="display">Vedoucí</h3>', '<h3 class="display">Leader</h3>'),
    ('<h3 class="display">Pravé křídlo</h3>', '<h3 class="display">Right Wing</h3>'),
    ('<h3 class="display">Levé křídlo</h3>', '<h3 class="display">Left Wing</h3>'),
    ('Vede formaci, drží navigaci a komunikaci s okolím. Jeho úkolem je létat tak čistě a předvídatelně, aby zbytek formace věděl přesně, co bude dělat dál.',
     'Leads the formation and handles navigation and radio. The job is to fly so smoothly and predictably that the rest of the formation always knows exactly what comes next.'),
    ('Drží se těsně vpravo od lídra, kopíruje každý jeho pohyb. Odstup od sousedního stroje se počítá v metrech, ne v desítkách metrů.',
     'Holds tight on the leader’s right and mirrors every move. The gap to the next aircraft is measured in metres, not tens of metres.'),
    ('Zrcadlová pozice ke dvojce, vlevo od lídra. Nejnáročnější na cit, protože chyba se tady nedá zamaskovat.',
     'The mirror image of number two, on the leader’s left. The position that demands the finest touch — there is nowhere to hide a mistake.'),
    ('„Tail-end-charlie“ — sedí za lídrem a snáší turbulenci od zbytku sestavy. Přesnost bez chatování v éteru.',
     'The “tail-end Charlie” — sits behind the leader and rides out the turbulence from the rest of the formation. Precision without the radio chatter.'),
    ('<span class="bright">TOHLE NEJSOU LETADLA V MUZEU.</span><br>\n    <span class="fade">JSOU TO STROJE, KTERÉ POŘÁD LÍTAJÍ.</span>',
     '<span class="bright">THESE AREN’T MUSEUM PIECES.</span><br>\n    <span class="fade">THEY’RE AIRCRAFT THAT STILL FLY.</span>'),
    ('60+ LET OD OTROKOVIC · POŘÁD VE VZDUCHU', '60+ YEARS SINCE OTROKOVICE · STILL FLYING'),

    # ---------- galerie
    ('<h2>Fotogalerie</h2>', '<h2>Photo Gallery</h2>'),
    ('aria-label="Předchozí fotka"', 'aria-label="Previous photo"'),
    ('aria-label="Další fotka"', 'aria-label="Next photo"'),
    ('aria-label="Zavřít"', 'aria-label="Close"'),

    # ---------- instagram
    ('ŽIVĚ Z LETIŠTĚ', 'LIVE FROM THE FLIGHT LINE'),
    ('Zákulisí tréninků, přelety airshow a stroje z blízka. Nejčerstvější záběry z kokpitu i z ranveje dáváme na Instagram.',
     'Behind the scenes at training, airshow fly-bys and the aircraft up close. Our latest shots from the cockpit and the runway go straight to Instagram.'),
    ('SLEDOVAT NA INSTAGRAMU</a>', 'FOLLOW US ON INSTAGRAM</a>'),
    ('</b> sledujících</span>', '</b> followers</span>'),
    ('</b> příspěvků</span>', '</b> posts</span>'),
    ('Výběr z našich fotek — nejnovější příspěvky najdete na Instagramu.', 'A selection of our photos — for the latest posts, head over to Instagram.'),
    ('aria-label="Fotogalerie">', 'aria-label="Photo gallery">'),
    ('aria-label="Výběr fotky"', 'aria-label="Choose a photo"'),
    ('aria-label="Fotka 1"', 'aria-label="Photo 1"'),
    ('aria-label="Fotka 2"', 'aria-label="Photo 2"'),
    ('aria-label="Fotka 3"', 'aria-label="Photo 3"'),
    ('aria-label="Fotka 4"', 'aria-label="Photo 4"'),
    ('aria-label="Fotka 5"', 'aria-label="Photo 5"'),
    ('DALŠÍ FOTKY NA INSTAGRAMU →', 'MORE PHOTOS ON INSTAGRAM →'),
    ('Fotogalerie ↓</a>', 'Photo gallery ↓</a>'),
    ('''<!-- Hlavní galerie. Po propojení s Instagramem (Behold) vložte JSON adresu feedu
     do data-feed a mřížka se sama naplní posledními příspěvky. Do té doby ukazuje
     výběr 4 fotek níže; po kliknutí se otevřou v prohlížeči fotek. -->''', '<!-- Main gallery: see the Czech version for setup notes. -->'),

    # ---------- kalendář
    ('<h2>Kalendář vystoupení</h2>', '<h2>Display Calendar</h2>'),
    ('<tr><th scope="col">Datum</th><th scope="col">Místo</th><th scope="col">Akce</th><th scope="col">Stav</th></tr>', '<tr><th scope="col">Date</th><th scope="col">Location</th><th scope="col">Event</th><th scope="col">Status</th></tr>'),
    ('<td data-label="Datum">2027</td>', '<td data-label="Date">2027</td>'),
    ('<td data-label="Místo">—</td>', '<td data-label="Location">—</td>'),
    ('<td data-label="Akce">Kalendář sezóny 2027 připravujeme. Aktuality najdete na',
     '<td data-label="Event">The 2027 season calendar is coming soon. For the latest news, follow us on'),
    ('rel="noopener">Instagramu</a> a <a', 'rel="noopener">Instagram</a> and <a'),
    ('rel="noopener">Facebooku</a>.</td>', 'rel="noopener">Facebook</a>.</td>'),
    ('<td data-label="Stav"><span class="status-pill tbd">BUDE UPŘESNĚNO</span>',
     '<td data-label="Status"><span class="status-pill tbd">TO BE CONFIRMED</span>'),

    # ---------- létejte s námi + kontakt
    ('<h2 class="display">Chcete létat?</h2>', '<h2 class="display">Want to fly?</h2>'),
    ('Posaďte se do stroje, který létá už přes šedesát let. Uslyšíte motor naostro, ucítíte drak letadla v zatáčce a uvidíte Moravu z kokpitu tak, jak ji vidí jen piloti. Napište nám a domluvíme si termín.',
     'Climb aboard an aircraft that has been flying for more than sixty years. Hear the engine up close, feel the airframe working through a turn and see Moravia from the cockpit the way only pilots do. Drop us a line and we’ll find a date.'),
    ('NAPSAT TÝMU →', 'EMAIL THE TEAM →'),
    ('<h2 class="display">Domovská základna</h2>', '<h2 class="display">Home base</h2>'),
    ('Formaci nejčastěji potkáte nad letištěm LKZA — Zábřeh u Hlučína, mezi Ostravou a Opavou. Fanoušci satelitních map si mohou souřadnice rovnou zadat do vyhledávače.',
     'You’ll most often find the formation over LKZA airfield — Zábřeh near Hlučín, between Ostrava and Opava. Satellite-map fans can paste the coordinates straight into a search engine.'),
    ('<span class="k">LETIŠTĚ</span><span class="v">LKZA — ZÁBŘEH U HLUČÍNA</span>', '<span class="k">AIRFIELD</span><span class="v">LKZA — ZÁBŘEH NEAR HLUČÍN</span>'),
    ('<span class="k">SOUŘADNICE</span>', '<span class="k">COORDINATES</span>'),
    ('<span class="k">E-MAIL</span>', '<span class="k">EMAIL</span>'),
    ('<span class="k">AEROKLUB</span>', '<span class="k">AERO CLUB</span>'),
    ('FOLLOW-ME · FORMAČNÍ LETECKÝ TÝM · LKZA', 'FOLLOW-ME · FORMATION DISPLAY TEAM · LKZA'),
    ('<a href="#top">Nahoru ↑</a>', '<a href="#top">Top ↑</a>'),
    ('<a href="mailto:follow-me@email.cz">E-mail</a>', '<a href="mailto:follow-me@email.cz">Email</a>'),
    ('class="footer-admin" rel="nofollow">Administrace</a>', 'class="footer-admin" rel="nofollow">Admin</a>'),
]

# Popisky stejného textu na více místech (karty, technické údaje)
EVERYWHERE = [
    ('<span class="k">NAROZEN</span>', '<span class="k">BORN</span>'),
    ('<span class="k">VÝŠKA</span>', '<span class="k">HEIGHT</span>'),
    ('<span class="k">VÁHA</span>', '<span class="k">WEIGHT</span>'),
    ('<span class="k">NÁLET (H)</span>', '<span class="k">HOURS</span>'),
    ('<span class="k">POZICE</span>', '<span class="k">POSITION</span>'),
    ('<div class="machine-foot mono"><span>ÚLOHA</span>', '<div class="machine-foot mono"><span>ROLE</span>'),
    ('KARTA PILOTA / ', 'PILOT FILE / '),
    (' — STROJ: ', ' — AIRCRAFT: '),
]

CAPTIONS = {
    "ŘADA · NAD LESEM · FOTO JAKUB VANĚK": "LINE ASTERN · OVER THE FOREST · PHOTO JAKUB VANĚK",
    "DIAMANT · NAD KRAJINOU · FOTO JAKUB VANĚK": "DIAMOND · OVER THE COUNTRYSIDE · PHOTO JAKUB VANĚK",
    "ŘADA · ZEPŘEDU": "LINE ASTERN · HEAD-ON",
    "ECHELON · NAD VĚTRNÍKY": "ECHELON · OVER THE WIND FARM",
    "ČTYŘI STROJE · ZE VZDUCHU": "ALL FOUR · AIR TO AIR",
    "OK-MPR + OK-KNR · ZÁPAD SLUNCE": "OK-MPR + OK-KNR · SUNSET",
    "OK-KNR · TĚSNÁ FORMACE · FOTO CARLILL PHOTOGRAPHY": "OK-KNR · CLOSE FORMATION · PHOTO CARLILL PHOTOGRAPHY",
    "OK-KNR · PŘED BOUŘKOU": "OK-KNR · BEFORE THE STORM",
    "ECHELON · V BOUŘKOVÝCH MRACÍCH": "ECHELON · IN THE STORM CLOUDS",
}

ALTS = {
    "Zlín Z-326MF OK-SEN za letu z boku, tmavě modrý se žlutou šachovnicí, nad krajinou": "Zlín Z-326MF OK-SEN in flight, side view, dark blue with yellow checks, over the countryside",
    "Zlín Z-226MS OK-LPR za letu z boku, světle zelený s vínovou šachovnicí, pilot v kokpitu": "Zlín Z-226MS OK-LPR in flight, side view, light green with maroon checks, pilot in the cockpit",
    "OK-KNR, OK-SEN, OK-MPR a OK-LPR těsně za sebou nad lesem": "OK-KNR, OK-SEN, OK-MPR and OK-LPR tucked in line astern over a forest",
    "Čtyři stroje v diamantu nad lesem a poli": "Four aircraft in diamond formation over forest and fields",
    "Čtyři stroje v řadě za sebou zepředu, v čele OK-KNR, pod nimi krajina": "Four aircraft in line astern seen head-on, OK-KNR leading, countryside below",
    "Čtyři stroje v šikmé řadě nad poli a větrnými elektrárnami": "Four aircraft in echelon over fields and wind turbines",
    "OK-LPR, OK-KNR, OK-SEN a OK-MPR z boku nad krajinou": "OK-LPR, OK-KNR, OK-SEN and OK-MPR side-on over the countryside",
    "OK-MPR z boku a OK-KNR v náklonu při západu slunce": "OK-MPR side-on and OK-KNR banking at sunset",
    "OK-KNR s pilotem v kokpitu, za ním těsně OK-SEN, OK-MPR a OK-LPR": "OK-KNR with the pilot in the cockpit, OK-SEN, OK-MPR and OK-LPR tucked in close",
    "OK-KNR zezadu na trávě, nad ním bouřková oblaka": "OK-KNR from behind on the grass beneath storm clouds",
    "Formace FOLLOW-ME nad hangárem Slezského aeroklubu Zábřeh": "The FOLLOW-ME formation over the Silesian Aero Club Zábřeh hangar",
    "OK-KNR, OK-SEN, OK-MPR a OK-LPR v šikmé řadě před bouřkovými mraky": "OK-KNR, OK-SEN, OK-MPR and OK-LPR in echelon against storm clouds",
    "Portrét pilota Boba": "Portrait of pilot Bob",
    "Portrét pilota Jardy": "Portrait of pilot Jarda",
    "Portrét pilota Jiřího": "Portrait of pilot Jiří",
    "Portrét pilota Luba": "Portrait of pilot Lubo",
    "Portrét pilota Tomáše": "Portrait of pilot Tomáš",
    "Zlín Z-226MS OK-KNR z boku na trávě s pilotem v kokpitu": "Zlín Z-226MS OK-KNR side-on on the grass with the pilot in the cockpit",
    "Zlín Z-226MS OK-MPR za letu z boku, stříbrný s červeno-bílou šachovnicí": "Zlín Z-226MS OK-MPR in flight, side view, silver with red-and-white checks",
}


def flexible(text):
    """Vzor, který ignoruje rozdíly v mezerách a zalomení řádků."""
    parts = [re.escape(p) for p in re.split(r"\s+", text.strip())]
    return re.compile(r"\s+".join(parts))


def main():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    out = src
    missing = []

    for cz, en in TEXT:
        pat = flexible(cz)
        out, n = pat.subn(lambda m, en=en: en, out)
        if n == 0:
            missing.append(cz[:90])
    for cz, en in EVERYWHERE:
        if cz not in out:
            missing.append(cz)
        out = out.replace(cz, en)
    for cz, en in CAPTIONS.items():
        a = f'data-caption="{cz}"'
        if a not in out:
            missing.append("popisek: " + cz)
        out = out.replace(a, f'data-caption="{en}"')
        out = out.replace(f'<span class="g-label mono">{cz}</span>', f'<span class="g-label mono">{en}</span>')
        out = out.replace(f'<span class="ig-cap mono">{cz}</span>', f'<span class="ig-cap mono">{en}</span>')
        out = out.replace(f'<span class="ss-cap mono">{cz}</span>', f'<span class="ss-cap mono">{en}</span>')
    for cz, en in ALTS.items():
        a = f'alt="{cz}"'
        if a not in out:
            missing.append("alt: " + cz)
        out = out.replace(a, f'alt="{en}"')

    # nepřeložené popisky a alt texty, které v seznamech chybí
    for kind, rx in (("popisek", r'data-caption="([^"]*)"'), ("alt", r' alt="([^"]+)"')):
        known = set(CAPTIONS.values()) if kind == "popisek" else set(ALTS.values())
        for value in re.findall(rx, out):
            if value not in known and re.search(r"[ěščřžýáíéůúňťďĚŠČŘŽÝÁÍÚŮ]", value) and "Ł" not in value and "Zlín" not in value:
                missing.append(f"{kind} bez překladu: {value}")

    if missing:
        print("Chybí překlad pro tyto texty z index.html:", file=sys.stderr)
        for m in dict.fromkeys(missing):
            print("  -", m, file=sys.stderr)
        sys.exit(1)

    # cesty: anglická verze leží o složku hlouběji
    out = re.sub(r'(?<=["\s,])(assets|css|js)/', r"../\1/", out)
    out = out.replace('<tbody id="eventsBody">', '<tbody id="eventsBody" data-src="../data/events.json">')
    out = out.replace('<link rel="preload" href="data/events.json"', '<link rel="preload" href="../data/events.json"')
    out = out.replace(f'<link rel="icon"', f'<link rel="canonical" href="{SITE}/en/">\n<link rel="icon"', 1)

    target = ROOT / "en" / "index.html"
    target.parent.mkdir(exist_ok=True)
    header = "<!-- Vygenerováno skriptem tools/build_en.py z index.html — needitujte ručně. -->\n"
    target.write_text(out.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + header, 1), encoding="utf-8")
    print("Hotovo:", target.relative_to(ROOT))


if __name__ == "__main__":
    main()
