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
    ('Najeďte na pozici — klepnutím přejdete na kartu pilota.', 'Hover over a position — click to jump to the pilot’s file.'),
    ('<h3 class="display">Mapa sezóny</h3>', '<h3 class="display">Season Map</h3>'),
    ('<span class="lg lg-home"></span>Domovské letiště LKZA <span class="lg lg-ev"></span>Vystoupení', '<span class="lg lg-home"></span>Home base LKZA <span class="lg lg-ev"></span>Displays'),
    ('aria-label="Mapa vystoupení v sezóně"', 'aria-label="Map of this season’s displays"'),
    ('Místa vystoupení se na mapě objeví, jakmile budou v kalendáři.', 'Display locations will appear on the map as soon as they are in the calendar.'),
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
    ('<a href="#gallery">Galerie</a>', '<a href="#gallery">Gallery</a>'),
    ('<a href="#events">Kalendář</a>', '<a href="#events">Events</a>'),
    ('<a href="#fly">Létejte s námi</a>', '<a href="#fly">Fly with us</a>'),
    ('<a href="#contact">Kontakt</a>', '<a href="#contact">Contact</a>'),
    ('<div class="nav-lang mono" role="navigation" aria-label="Jazyk">\n    <a href="./" class="active" lang="cs" aria-current="page">CZ</a><span aria-hidden="true">/</span>\n    <a href="en/" lang="en" hreflang="en">EN</a>',
     '<div class="nav-lang mono" role="navigation" aria-label="Language">\n    <a href="../" lang="cs" hreflang="cs">CZ</a><span aria-hidden="true">/</span>\n    <a href="./" class="active" lang="en" aria-current="page">EN</a>'),
    ('<div class="mm-lang mono"><a href="./" class="active" aria-current="page">CZ</a><a href="en/" lang="en" hreflang="en">EN</a></div>',
     '<div class="mm-lang mono"><a href="../" lang="cs" hreflang="cs">CZ</a><a href="./" class="active" aria-current="page">EN</a></div>'),
    ('aria-label="FOLLOW-ME na Instagramu"', 'aria-label="FOLLOW-ME on Instagram"'),
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

    # ---------- video
    ('aria-label="Video formace FOLLOW-ME"', 'aria-label="FOLLOW-ME formation video"'),
    ('REC · ZÁZNAM Z AIRSHOW', 'REC · AIRSHOW FOOTAGE'),
    ('<span class="reel-caption mono">FORMACE V AKCI</span>', '<span class="reel-caption mono">FORMATION IN ACTION</span>'),
    ('PŘEHRÁT CELÉ VIDEO ▸', 'WATCH THE FULL VIDEO ▸'),

    # ---------- tým
    ('<b>FOLLOW-ME</b> je formační tým, který od svého domovského letiště LKZA v Zábřehu u Hlučína — mezi Ostravou a Opavou — pravidelně vzlétá ve čtyřčlenné sestavě strojů Zlín Z-226 a Z-326. Piloti přezdívkami mezi sebou nešetří, veřejně je ale nepoužívají — na webu je tedy potkáte pod jmény, ne pod volacími znaky.',
     '<b>FOLLOW-ME</b> is a formation team that regularly takes off from its home airfield, LKZA in Zábřeh near Hlučín — between Ostrava and Opava — as a four-ship of Zlín Z-226 and Z-326 aircraft. The pilots have no shortage of nicknames for one another, but they keep them off the record — so on this site you will meet them by name, not by call sign.'),
    ('Stroje z produkce otrokovické továrny Moravan už dnes nemají akrobatické oprávnění — přesto formace trénuje předvedenou sestavu tak přesně a tak těsně, jak to jde. Za dobu, kdy se tým drží ve vzduchu, navštívil řadu airshow po celé zemi i za hranicemi a ukázal divákům padesátileté veterány, kteří dnes vypadají lépe, než když poprvé opustili výrobní halu.',
     'Built by the Moravan factory in Otrokovice, these aircraft are no longer cleared for aerobatics — yet the formation trains its display routine as precisely and as tightly as it can. Over the years the team has flown at airshows across the country and abroad, showing crowds fifty-year-old veterans that look better today than the day they first rolled out of the factory.'),
    ('<h2>Posádka — karty pilotů</h2>', '<h2>Crew — Pilot Files</h2>'),
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
    ('Čtyři stroje z produkce otrokovické továrny Moravan. Padesát let staré, a přesto pořád ve vzduchu — stáří tu není slabina, je to kvalita.',
     'Four aircraft built by the Moravan factory in Otrokovice. Fifty years old and still flying — here, age isn’t a weakness, it’s a mark of quality.'),
    ('<span class="k">VÝR. ČÍSLO</span>', '<span class="k">SERIAL</span>'),
    ('<span class="k">DODÁNO</span>', '<span class="k">DELIVERED</span>'),
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
    ('Registrace vznikla z iniciál pilota (LP) a společného „R“ celé formace. Prochází dlouhodobou restaurací, kterou z velké části financují nášivky na rukávu dopravního kapitána.',
     'The registration comes from the pilot’s initials (LP) plus the “R” shared by the whole formation. It is undergoing a long-term restoration, funded largely by the stripes on an airline captain’s sleeve.'),
    ('První a jediný postavený kus modifikace „MF“ — na rozdíl od standardních 326 nese kovovou stavitelnou vrtuli místo dřevěné, kvůli čemuž musel být posunut i kokpit. Zkušební lety proběhly na začátku listopadu 1997, do Aeroklubu Zábřeh dorazila 15. listopadu. Kromě formace slouží i k vlekání kluzáků a přežila i tvrdší kontakt s matkou zemí na břiše trupu.',
     'The first and only example of the “MF” variant ever built. Unlike the standard 326, it carries a metal variable-pitch propeller instead of a wooden one, which meant the cockpit had to be moved as well. Test flights took place in early November 1997, and the aircraft arrived at the Zábřeh aero club on 15 November. Besides flying in the formation it tows gliders — and it has even survived a firm meeting with Mother Earth on its belly.'),

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
    ('50+ LET OD OTROKOVIC · POŘÁD VE VZDUCHU', '50+ YEARS SINCE OTROKOVICE · STILL FLYING'),

    # ---------- galerie
    ('<h2>Galerie</h2>', '<h2>Gallery</h2>'),
    ('DALŠÍ FOTKY (', 'MORE PHOTOS ('),
    ('aria-label="Fotogalerie"', 'aria-label="Photo gallery"'),
    ('aria-label="Předchozí fotka"', 'aria-label="Previous photo"'),
    ('aria-label="Další fotka"', 'aria-label="Next photo"'),
    ('aria-label="Zavřít"', 'aria-label="Close"'),

    # ---------- instagram
    ('ŽIVĚ Z LETIŠTĚ', 'LIVE FROM THE FLIGHT LINE'),
    ('Zákulisí tréninků, přelety airshow a stroje z blízka. Nejčerstvější záběry z kokpitu i z ranveje dáváme na Instagram.',
     'Behind the scenes at training, airshow fly-bys and the aircraft up close. Our latest shots from the cockpit and the runway go straight to Instagram.'),
    ('SLEDOVAT NA INSTAGRAMU →', 'FOLLOW US ON INSTAGRAM →'),

    # ---------- kalendář
    ('<h2>Kalendář vystoupení</h2>', '<h2>Display Calendar</h2>'),
    ('<tr><th>Datum</th><th>Místo</th><th>Akce</th><th>Stav</th></tr>', '<tr><th>Date</th><th>Location</th><th>Event</th><th>Status</th></tr>'),
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
    ('Posaďte se do stroje, který létá už přes padesát let. Uslyšíte motor naostro, ucítíte drak letadla v zatáčce a uvidíte Moravu z kokpitu tak, jak ji vidí jen piloti. Napište nám a domluvíme si termín.',
     'Climb aboard an aircraft that has been flying for more than fifty years. Hear the engine up close, feel the airframe working through a turn and see Moravia from the cockpit the way only pilots do. Drop us a line and we’ll find a date.'),
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
    "BOX · ZESPODU · © JAKBALPHOTO": "BOX · FROM BELOW · © JAKBALPHOTO",
    "BOX · ČTYŘI STROJE": "BOX · FOUR AIRCRAFT",
    "DIAMANT · NA OKRAJI MRAKU": "DIAMOND · ON THE EDGE OF A CLOUD",
    "DIAMANT · V OBŘÍCH MRACÍCH": "DIAMOND · AMONG TOWERING CLOUDS",
    "DIAMANT · Z ODSTAVENÉHO STROJE": "DIAMOND · SEEN FROM A PARKED AIRCRAFT",
    "DOMA · NAD HANGÁREM LKZA": "HOME · OVER THE LKZA HANGAR",
    "ECHELON · DIAGONÁLA": "ECHELON · DIAGONAL",
    "ECHELON · MODRÉ NEBE": "ECHELON · BLUE SKY",
    "ECHELON · MODRÉ NEBE · © JAKBALPHOTO": "ECHELON · BLUE SKY · © JAKBALPHOTO",
    "ECHELON · NAD LETIŠTĚM": "ECHELON · OVER THE AIRFIELD",
    "ECHELON · NAD MRAKEM": "ECHELON · ABOVE THE CLOUD",
    "ECHELON · NAD SMRKEM": "ECHELON · OVER THE SPRUCE",
    "ECHELON · PROTI MRAKŮM": "ECHELON · AGAINST THE CLOUDS",
    "ECHELON · SILUETY": "ECHELON · SILHOUETTES",
    "ECHELON · TMAVÉ NEBE": "ECHELON · DARK SKY",
    "ECHELON · V BOUŘKOVÝCH MRACÍCH": "ECHELON · IN THE STORM CLOUDS",
    "ECHELON · V TAHU · FOTO MICHAŁ BANACH": "ECHELON · PULLING G · PHOTO MICHAŁ BANACH",
    "ECHELON · ČTYŘI STROJE": "ECHELON · FOUR AIRCRAFT",
    "HEAD-ON · DIAMANT": "HEAD-ON · DIAMOND",
    "LESZNO 2016 · TĚSNÁ ŘADA · FOTO TOMASZ BARTKOWIAK": "LESZNO 2016 · TIGHT LINE · PHOTO TOMASZ BARTKOWIAK",
    "LESZNO 2016 · VEDLE SEBE · FOTO TOMASZ BARTKOWIAK": "LESZNO 2016 · SIDE BY SIDE · PHOTO TOMASZ BARTKOWIAK",
    "LESZNO 2016 · Z BOKU · FOTO TOMASZ BARTKOWIAK": "LESZNO 2016 · SIDE VIEW · PHOTO TOMASZ BARTKOWIAK",
    "NAD MRAKY · FOTO MICHAŁ BANACH": "ABOVE THE CLOUDS · PHOTO MICHAŁ BANACH",
    "OK-KNR + OK-LPR · ZATÁČKA": "OK-KNR + OK-LPR · IN THE TURN",
    "OK-KNR + OK-LPR · ZESPODU": "OK-KNR + OK-LPR · FROM BELOW",
    "OK-KNR + OK-LPR · ZEZADU": "OK-KNR + OK-LPR · FROM BEHIND",
    "OK-KNR NAD OK-LPR": "OK-KNR ABOVE OK-LPR",
    "OK-KNR · KOKPIT": "OK-KNR · COCKPIT",
    "OK-KNR · POD MRAKY": "OK-KNR · UNDER THE CLOUDS",
    "OK-KNR · S PILOTEM": "OK-KNR · PILOT ON BOARD",
    "OK-KNR · Z TRÁVY": "OK-KNR · FROM THE GRASS",
    "OK-LPR + OK-KNR · PÁR": "OK-LPR + OK-KNR · PAIR",
    "OK-LPR POD OK-KNR": "OK-LPR BELOW OK-KNR",
    "OK-LPR · PŘED STARTEM": "OK-LPR · BEFORE TAKE-OFF",
    "OK-MPR · DETAIL": "OK-MPR · DETAIL",
    "OK-MPR · KOKPIT A VRTULNÍK": "OK-MPR · COCKPIT AND HELICOPTER",
    "OK-MPR · OCAS 263": "OK-MPR · TAIL 263",
    "OK-MPR · PŘED BOUŘKOU": "OK-MPR · BEFORE THE STORM",
    "OK-MPR · ZE VZDUCHU": "OK-MPR · AIR TO AIR",
    "PŘED STARTEM · ČTYŘI STROJE": "BEFORE TAKE-OFF · ALL FOUR",
    "STACK · POHLED ZESPODU": "STACK · FROM BELOW",
    "STACK · TMAVÉ NEBE": "STACK · DARK SKY",
    "Z KOKPITU · OK-MPR A OK-LPR": "FROM THE COCKPIT · OK-MPR AND OK-LPR",
    "Z KOKPITU · ZA VEDOUCÍM": "FROM THE COCKPIT · BEHIND THE LEADER",
    "ZÁPAD SLUNCE · Z KOKPITU": "SUNSET · FROM THE COCKPIT",
}

ALTS = {
    "Detail šachovnicového ocasu OK-MPR, v pozadí ocasy OK-LPR a OK-SEN": "Close-up of OK-MPR’s chequered tail, with the tails of OK-LPR and OK-SEN behind",
    "Diamant zepředu: čtyři stroje letí přímo k fotografovi": "Diamond head-on: four aircraft flying straight towards the camera",
    "Diamant čtyř strojů na okraji bílého mraku": "A diamond of four aircraft on the edge of a white cloud",
    "Formace FOLLOW-ME nad hangárem Slezského aeroklubu Zábřeh": "The FOLLOW-ME formation over the Silesian Aero Club Zábřeh hangar",
    "Formace box zespodu: OK-MPR, OK-KNR, OK-SEN a OK-LPR": "Box formation from below: OK-MPR, OK-KNR, OK-SEN and OK-LPR",
    "Formace box: OK-MPR, OK-KNR, OK-LPR a OK-SEN": "Box formation: OK-MPR, OK-KNR, OK-LPR and OK-SEN",
    "Formace na obloze, v popředí konec křídla odstaveného letadla": "The formation in the sky, with the wingtip of a parked aircraft in the foreground",
    "Formace nad hangárem Slezského aeroklubu Zábřeh": "The formation over the Silesian Aero Club Zábřeh hangar",
    "Formace zespodu: OK-KNR, OK-SEN, OK-MPR a OK-LPR těsně nad sebou": "The formation from below: OK-KNR, OK-SEN, OK-MPR and OK-LPR stacked closely together",
    "Kokpit OK-MPR, v pozadí vrtulník a bouřkový mrak": "OK-MPR’s cockpit, with a helicopter and a storm cloud behind",
    "Malý diamant čtyř strojů uprostřed obřích kupovitých mraků": "A small diamond of four aircraft amid towering cumulus clouds",
    "OK-KNR a OK-LPR těsně u sebe, pohled zespodu": "OK-KNR and OK-LPR in close formation, seen from below",
    "OK-KNR a OK-LPR v náklonu těsně vedle sebe": "OK-KNR and OK-LPR banking side by side",
    "OK-KNR a OK-LPR zezadu, OK-LPR těsně za OK-KNR": "OK-KNR and OK-LPR from behind, with OK-LPR tucked in behind OK-KNR",
    "OK-KNR letí nad OK-LPR, pohled z boku": "OK-KNR flying above OK-LPR, side view",
    "OK-KNR na letišti pod bouřkovými mraky": "OK-KNR on the airfield under storm clouds",
    "OK-KNR sám na travnatém letišti pod šedými mraky": "OK-KNR alone on a grass airfield under grey clouds",
    "OK-KNR vyfocený zespodu z vysoké trávy": "OK-KNR photographed from low down in tall grass",
    "OK-KNR z boku na trávě s pilotem v kokpitu, v pozadí další stroje": "OK-KNR side-on on the grass with the pilot in the cockpit and the other aircraft behind",
    "OK-KNR, OK-SEN, OK-MPR a OK-LPR naskládané nad sebou": "OK-KNR, OK-SEN, OK-MPR and OK-LPR stacked one above the other",
    "OK-KNR, OK-SEN, OK-MPR a OK-LPR v těsné řadě, Leszno Air Picnic 2016": "OK-KNR, OK-SEN, OK-MPR and OK-LPR in a tight line, Leszno Air Picnic 2016",
    "OK-KNR, OK-SEN, OK-MPR a OK-LPR v šikmé řadě před bouřkovými mraky": "OK-KNR, OK-SEN, OK-MPR and OK-LPR in echelon against storm clouds",
    "OK-LPR a OK-KNR v těsném páru": "OK-LPR and OK-KNR in a close pair",
    "OK-LPR a OK-KNR v těsném páru z boku": "OK-LPR and OK-KNR in a close pair, side view",
    "OK-LPR pojíždí po trávě s roztočenou vrtulí": "OK-LPR taxiing on the grass with its propeller turning",
    "OK-LPR, OK-KNR, OK-SEN a OK-MPR v diagonální řadě": "OK-LPR, OK-KNR, OK-SEN and OK-MPR in a diagonal line",
    "OK-LPR, OK-MPR, OK-SEN a OK-KNR v ostré zatáčce zespodu": "OK-LPR, OK-MPR, OK-SEN and OK-KNR in a steep turn, seen from below",
    "OK-LPR, OK-MPR, OK-SEN a OK-KNR z boku, Leszno Air Picnic 2016": "OK-LPR, OK-MPR, OK-SEN and OK-KNR from the side, Leszno Air Picnic 2016",
    "OK-MPR a nad ním OK-LPR, záběr z letadla nad krajinou s rybníky": "OK-MPR with OK-LPR above, shot air-to-air over a landscape of ponds",
    "OK-MPR na trávě pod bouřkovým mrakem": "OK-MPR on the grass beneath a storm cloud",
    "OK-MPR shora nad travnatou plochou, vlevo ocas OK-KNR, vpravo křídlo OK-LPR": "OK-MPR from above over grass, with OK-KNR’s tail on the left and OK-LPR’s wing on the right",
    "OK-SEN shora nad dálnicí, záběr z letadla": "OK-SEN from above over a motorway, shot air-to-air",
    "Otevřený kokpit a vrtule OK-KNR pod bouřkovými mraky": "OK-KNR’s open cockpit and propeller under storm clouds",
    "Portrét pilota Boba": "Portrait of pilot Bob",
    "Portrét pilota Jardy": "Portrait of pilot Jarda",
    "Portrét pilota Jiřího": "Portrait of pilot Jiří",
    "Portrét pilota Luba": "Portrait of pilot Lubo",
    "Portrét pilota Tomáše": "Portrait of pilot Tomáš",
    "Příď a vrtule OK-MPR u hangáru": "OK-MPR’s nose and propeller by the hangar",
    "Silueta OK-LPR přímo pod OK-KNR, pohled zespodu": "Silhouette of OK-LPR directly below OK-KNR, seen from below",
    "Silueta letadla FOLLOW-ME při západu slunce, záběr z kokpitu druhého stroje": "A FOLLOW-ME aircraft silhouetted at sunset, shot from the cockpit of another",
    "Siluety strojů před sluncem, pohled z kokpitu": "Aircraft silhouetted against the sun, seen from the cockpit",
    "Všechny čtyři stroje na trávě s roztočenými vrtulemi pod zataženou oblohou": "All four aircraft on the grass with propellers turning under an overcast sky",
    "Zlín Z-226MS OK-KNR z boku na trávě s pilotem v kokpitu": "Zlín Z-226MS OK-KNR side-on on the grass with the pilot in the cockpit",
    "Zlín Z-226MS OK-LPR za letu, světle zelený s vínovou šachovnicí": "Zlín Z-226MS OK-LPR in flight, light green with maroon checks",
    "Zlín Z-226MS OK-MPR za letu z boku, stříbrný s červeno-bílou šachovnicí": "Zlín Z-226MS OK-MPR in flight, side view, silver with red-and-white checks",
    "Zlín Z-326MF OK-SEN shora, žlutý s modrou pravou polovinou křídla": "Zlín Z-326MF OK-SEN from above, yellow with a blue right wing",
    "Čtyři stroje FOLLOW-ME nad kupovitými mraky: OK-LPR, OK-KNR, OK-SEN a OK-MPR": "Four FOLLOW-ME aircraft above cumulus clouds: OK-LPR, OK-KNR, OK-SEN and OK-MPR",
    "Čtyři stroje v řadě jako siluety proti mrakům": "Four aircraft in line, silhouetted against the clouds",
    "Čtyři stroje v řadě na modrém nebi": "Four aircraft in line against a blue sky",
    "Čtyři stroje v řadě nad bílým mrakem": "Four aircraft in line above a white cloud",
    "Čtyři stroje v řadě nad letištěm na modrém nebi": "Four aircraft in line over the airfield against a blue sky",
    "Čtyři stroje v řadě nad letištěm pod bouřkovými mraky": "Four aircraft in line over the airfield beneath storm clouds",
    "Čtyři stroje v řadě nad vrcholkem smrku": "Four aircraft in line above the top of a spruce tree",
    "Čtyři stroje v řadě před mraky, pohled zepředu": "Four aircraft in line against the clouds, head-on",
    "Čtyři stroje v šikmé řadě před tmavými mraky": "Four aircraft in echelon against dark clouds",
    "Čtyři stroje v šikmé řadě: OK-KNR, OK-SEN, OK-MPR a OK-LPR": "Four aircraft in echelon: OK-KNR, OK-SEN, OK-MPR and OK-LPR",
    "Čtyři stroje vedle sebe, Leszno Air Picnic 2016": "Four aircraft side by side, Leszno Air Picnic 2016",
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
    out = out.replace(f'<link rel="icon"', f'<link rel="canonical" href="{SITE}/en/">\n<link rel="icon"', 1)

    target = ROOT / "en" / "index.html"
    target.parent.mkdir(exist_ok=True)
    header = "<!-- Vygenerováno skriptem tools/build_en.py z index.html — needitujte ručně. -->\n"
    target.write_text(out.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + header, 1), encoding="utf-8")
    print("Hotovo:", target.relative_to(ROOT))


if __name__ == "__main__":
    main()
