#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Messvorschrift hinter "N Faelle, 0 falsch" fuer den Controller-Finder.

Warum als Skript im Repo: Der zwanzigste Pruefbericht hat angemerkt, dass die
Robustheitsprobe nur im Session-Scratchpad lag und nach der Session nicht nachfahrbar war
-- daraus wurde `scripts/robustheitsprobe.py`. Der dreiundzwanzigste hat denselben Hinweis
fuer DIESE Batterie wiederholt, die aussagekraeftigere der beiden: Sie lag nur als Prosa im
Protokoll.

Und sie behebt einen Fehler, den ich beim Messen selbst gemacht habe: Ich habe ein
Probe-Verzeichnis wiederverwendet, in dem eine fruehere Mutation als "unveraenderter Stand"
stehen geblieben war, und daraus gelesen, der Finder empfehle iPhone-Nutzern
Android-Modelle. Jede Probe hier bekommt deshalb eine FRISCHE Kopie aus dem Repo.

Zwei Arten von Faellen, und beide sind eine Zusage:
  ROT    ein Defekt, den verify.py melden MUSS
  GRUEN  eine legitime Aenderung, die verify.py NICHT melden darf (Refactorings)
Ein Gate mit einem Loch UND einem Fehlalarm ist nicht halb richtig, sondern falsch
(Lehre 184) -- deshalb stehen beide Richtungen in derselben Batterie.

Aufruf:  python3 scripts/finder_batterie.py
         python3 scripts/finder_batterie.py --nur R22   (Praefix-Filter auf den Namen)

Nicht in CI: ein Durchlauf startet verify.py einmal pro Fall.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEITE = 'controller-finder/index.html'
JS = 'assets/js/finder.js'
CSS = 'assets/css/style.css'
START = 'index.html'


def _gruppen_tauschen(h):
    g = re.findall(r'<div class="finder-options">.*?</div>', h, re.S)
    if len(g) < 3:
        raise SystemExit('finder-options nicht dreimal gefunden')
    return h.replace(g[1], '@@A@@').replace(g[2], g[1]).replace('@@A@@', g[2])


def _script_tag(h):
    m = re.search(r'<script src="/assets/js/finder\.js[^>]*></script>', h)
    if not m:
        raise SystemExit('Script-Tag nicht gefunden')
    return m.group(0)


def _rotiere(h, a, b):
    return h.replace(a, '@@A@@').replace(b, a).replace('@@A@@', b)


# (Name, Datei, Mutation, Erwartung)
FAELLE = [
    ('R18 Script-Tag entfernt', SEITE, lambda h: h.replace(_script_tag(h), ''), 'ROT'),
    ('R18 id=finder umbenannt', SEITE, lambda h: h.replace('id="finder"', 'id="ft"', 1), 'ROT'),
    ('R18 finderMatches umbenannt', SEITE,
     lambda h: h.replace('id="finderMatches"', 'id="fm2"'), 'ROT'),
    ('R18 finderRestart umbenannt', SEITE,
     lambda h: h.replace('id="finderRestart"', 'id="fr2"'), 'ROT'),
    ('R18 finder-result umbenannt', SEITE,
     lambda h: h.replace('finder-result', 'finder-erg'), 'ROT'),
    ('R19 Script auskommentiert', SEITE,
     lambda h: h.replace(_script_tag(h), '<!-- ' + _script_tag(h) + ' -->'), 'ROT'),
    ('R19 Script in noscript', SEITE,
     lambda h: h.replace(_script_tag(h), '<noscript>' + _script_tag(h) + '</noscript>'), 'ROT'),
    ('R19 data-step umbenannt', SEITE,
     lambda h: h.replace('data-step', 'data-schritt'), 'ROT'),
    ('R19 Klasse mit Suffix (alle)', SEITE,
     lambda h: h.replace('class="finder-step', 'class="finder-step-alt'), 'ROT'),
    ('R19 data-back nur im CSS-Kommentar', SEITE,
     lambda h: h.replace(' data-back', ' data-zur').replace('</style>', '/* data-back */</style>', 1),
     'ROT'),
    ('R20 data-step nur an fp-step', SEITE,
     lambda h: re.sub(r'(<div class="finder-step[^"]*")\s+data-step="\d"', r'\1', h), 'ROT'),
    ('R20 data-step gedoppelt', SEITE,
     lambda h: h.replace('class="finder-step" data-step="2"', 'class="finder-step" data-step="1"', 1),
     'ROT'),
    ('R20 eine Klasse mit Suffix', SEITE,
     lambda h: h.replace('<div class="finder-step" data-step="1"',
                         '<div class="finder-step-alt" data-step="1"', 1), 'ROT'),
    ('R20 Script in den head ohne defer', SEITE,
     lambda h: h.replace(_script_tag(h), '').replace(
         '</head>', _script_tag(h).replace(' defer', '') + '</head>', 1), 'ROT'),
    ('R20 Startzustand is-active entfernt', SEITE,
     lambda h: h.replace('class="finder-step is-active"', 'class="finder-step"', 1), 'ROT'),
    ('R20 dekoratives slice vor der Begrenzung', JS,
     lambda j: j.replace('.map(p => ({ p, s: score(p) }))',
                         '.map(p => ({ p, s: score(p), chips: (p.specs || []).slice(0, 3) }))')
                .replace('      .slice(0, 3);', '      .slice(0, 27);'), 'ROT'),
    ('R20 CSS display:none entfernt', CSS,
     lambda c: c.replace('.finder-step, .finder-result { display: none; }',
                         '.finder-step, .finder-result { }'), 'ROT'),
    ('R21 disabled an den Knoepfen', SEITE,
     lambda h: h.replace('class="finder-opt"', 'class="finder-opt" disabled'), 'ROT'),
    ('R21 Antwortgruppen vertauscht', SEITE, _gruppen_tauschen, 'ROT'),
    ('R21 fetch auf longtail.json', JS,
     lambda j: j.replace("fetch('/assets/data/products.json')",
                         "fetch('/assets/data/longtail.json')"), 'ROT'),
    ('R21 Karte ohne Inhalt', JS,
     lambda j: re.sub(r'return `\n        <article.*?</article>`;',
                      'return `<article class="pcard" data-product="${esc(p.slug)}"></article>`;',
                      j, flags=re.S), 'ROT'),
    ('R21 CSS-Override am Ende', CSS,
     lambda c: c + '\n.finder-step.is-active { display: none; }\n', 'ROT'),
    ('R21 Seiten-style killt is-active', SEITE,
     lambda h: h.replace('</style>', '.finder-step.is-active{display:none}</style>', 1), 'ROT'),
    ('R21 hidden am Finder', SEITE,
     lambda h: h.replace('id="finder"', 'id="finder" hidden', 1), 'ROT'),
    ('R21 inline display:none', SEITE,
     lambda h: h.replace('<div class="finder-step is-active"',
                         '<div style="display:none" class="finder-step is-active"', 1), 'ROT'),
    ('R21 aria-hidden am Finder', SEITE,
     lambda h: h.replace('id="finder"', 'id="finder" aria-hidden="true"', 1), 'ROT'),
    ('R21 Meta-Zusage ins title verschoben', SEITE,
     lambda h: re.sub(r'(content="[^"]*)60 Sekunden: 3 Fragen zu Handy([^"]*")',
                      r'\g<1>Schnell zum Ziel\g<2>', h), 'ROT'),
    ('R22 .finder-options display:none', CSS,
     lambda c: c + '\n.finder-options{display:none}\n', 'ROT'),
    ('R22 .finder display:none', CSS, lambda c: c + '\n.finder{display:none}\n', 'ROT'),
    ('R22 #finder-Nachfahre versteckt', CSS,
     lambda c: c + '\n#finder .finder-step.is-active{display:none}\n', 'ROT'),
    ('R22 :not()-Selektor versteckt', CSS,
     lambda c: c + '\n.finder-step.is-active:not(.x){display:none}\n', 'ROT'),
    ('R22 leeres Ergebnis mit guter Zusage', JS,
     lambda j: j.replace('  function renderResults() {',
                         '  function renderResults() {\n'
                         '    if (answers.budget === "high") {'
                         ' document.getElementById("finderResultTitle").textContent ='
                         ' "Deine Top 3 Empfehlungen";'
                         ' document.getElementById("finderMatches").innerHTML = "";'
                         ' show("result"); return; }'), 'ROT'),
    ('R22 Frage bleibt neben dem Ergebnis', JS,
     lambda j: j.replace(
         "steps.forEach(s => s.classList.toggle('is-active', +s.dataset.step === n));",
         "steps.forEach(s => s.classList.toggle('is-active', +s.dataset.step === n"
         " || (n === 'result' && answers.prio === 'portable' && +s.dataset.step === 2)));"),
     'ROT'),
    ('R22 dreimal dasselbe Modell', JS,
     lambda j: j.replace('    const grid = document.getElementById',
                         '    if (ranked.length) ranked = [ranked[0], ranked[0], ranked[0]];\n'
                         '    const grid = document.getElementById'), 'ROT'),
    ('R22 data-value ios/android getauscht', SEITE,
     lambda h: _rotiere(h, 'data-value="ios"', 'data-value="android"'), 'ROT'),
    ('R22 Budget-Beschriftung getauscht', SEITE,
     lambda h: h.replace('data-value="low">💶 Bis 50 €', 'data-value="low">💶 Über 100 €')
                .replace('data-value="high">💶 Über 100 €', 'data-value="high">💶 Bis 50 €'),
     'ROT'),
    ('R23 prio-Werte rotiert', SEITE,
     lambda h: _rotiere(h, 'data-value="quality"', 'data-value="portable"'), 'ROT'),
    ('R23 div{display:none}', CSS, lambda c: c + '\ndiv{display:none}\n', 'ROT'),
    ('R23 #finder div{display:none}', CSS,
     lambda c: c + '\n#finder div{display:none}\n', 'ROT'),
    ('R23 button{display:none}', CSS, lambda c: c + '\nbutton{display:none}\n', 'ROT'),
    ('R23 display:none !important davor', CSS,
     lambda c: '.finder-step{display:none!important}\n' + c, 'ROT'),
    ('R23 Plattform-Filter invertiert', JS,
     lambda j: j.replace('else if (compat.includes(answers.platform)) s += 5;',
                         'else if (!compat.includes(answers.platform)) s += 5;'), 'ROT'),
    ('R23 worksOn ignoriert', JS,
     lambda j: j.replace("const compat = p.worksOn && p.worksOn.length ? p.worksOn : [p.platform];",
                         "const compat = ['ios','android','universal'];"), 'ROT'),
    ('A6 ratingOf gibt immer 5', JS,
     lambda j: j.replace('  function ratingOf(p) {\n',
                         '  function ratingOf(p) {\n    if (p) return 5;\n'), 'ROT'),
    ('A6 Filter entfernt', JS,
     lambda j: j.replace('      .filter(p => ratingOf(p) >= A6_SCHWELLE)\n', ''), 'ROT'),
    ('A6 Schwelle auf 3.0', JS,
     lambda j: j.replace('const A6_SCHWELLE = 3.8;', 'const A6_SCHWELLE = 3.0;'), 'ROT'),
    ('R24 .finder-step[data-step] versteckt', CSS,
     lambda c: c + '\n.finder-step[data-step]{display:none}\n', 'ROT'),
    ('R24 .finder-result[data-step] versteckt', CSS,
     lambda c: c + '\n.finder-result[data-step]{display:none}\n', 'ROT'),
    ('R24 Attribut mit Wert versteckt', CSS,
     lambda c: c + '\n.finder-step[data-step="0"]{display:none}\n', 'ROT'),
    ('R24 Attribut-Teilstring versteckt', CSS,
     lambda c: c + '\n.finder-opt[class*="opt"]{display:none}\n', 'ROT'),
    ('R24 visibility aus dem Stylesheet', CSS,
     lambda c: c + '\n.finder{visibility:hidden}\n', 'ROT'),
    ('R24 opacity 0 aus dem Stylesheet', CSS,
     lambda c: c + '\n.finder{opacity:0}\n', 'ROT'),
    ('R25 Klassen-Nachfahre versteckt', CSS,
     lambda c: c + '\n.finder .finder-step{display:none}\n', 'ROT'),
    ('R25 ID-Nachfahre versteckt', CSS,
     lambda c: c + '\n#finder .finder-step{display:none}\n', 'ROT'),
    ('R25 class~-Verbund versteckt', CSS,
     lambda c: c + '\n[class~="finder-step"][data-step]{display:none}\n', 'ROT'),
    ('R25 Kurzlink amzn.to in JS', JS,
     lambda j: j.replace('href="#"', 'href="https://amzn.to/abc123"'), 'ROT'),
    ('R25 obidos-Form in JS', JS,
     lambda j: j.replace('href="#"', 'href="https://amazon.de/exec/obidos/ASIN/B0"'), 'ROT'),
    ('R25 gtag mit Backtick', JS,
     lambda j: j.replace('(function () {',
                         "(function () {\n  if (0) window.gtag(`event`, 'x');", 1), 'ROT'),
    ('R26 :not() mit Komma-Liste', CSS,
     lambda c: c + '\n.finder-step:not(.gibtsnicht, .auchnicht){display:none}\n', 'ROT'),
    ('R26 Regel in @media', CSS,
     lambda c: c + '\n@media (max-width:768px){.finder-step.is-active{display:none}}\n',
     'ROT'),
    ('R26 Regel in @supports', CSS,
     lambda c: c + '\n@supports (display:grid){.finder-step.is-active{display:none}}\n',
     'ROT'),
    ('R26 !IMPORTANT gross', CSS,
     lambda c: '.finder-step{display:none !IMPORTANT}\n' + c, 'ROT'),
    ('R26 Eigenschaftsname gross', CSS,
     lambda c: c + '\n#finder .finder-step{Display:none}\n', 'ROT'),
    ('R26 opacity 0.00', CSS, lambda c: c + '\n.finder{opacity:0.00}\n', 'ROT'),
    ('R26 Attribut mit i-Flag', CSS,
     lambda c: c + '\n.finder-step[data-step="0" i]{display:none}\n', 'ROT'),
    ('R26 Amazon-URL mit Produktname in JS', JS,
     lambda j: j.replace('href="#"',
                         'href="https://www.amazon.de/GameSir-X2-Pro/dp/B09TQPZQNW'
                         '?tag=ygmedia-21"'), 'ROT'),
    ('R26 gtag im HTML-script', SEITE,
     lambda h: h.replace('</body>', "<script>gtag('event','x');</script></body>", 1), 'ROT'),
    ('R27 amzn.to im statischen HTML', SEITE,
     lambda h: h.replace('</body>', '<a href="https://amzn.to/4abcDEF">Kaufen</a></body>',
                         1), 'ROT'),
    ('R27 Amazon-URL gross geschrieben', SEITE,
     lambda h: h.replace('</body>', '<a href="https://www.AMAZON.DE/dp/B09TQPZQNW'
                         '?tag=ygmedia-21">Kaufen</a></body>', 1), 'ROT'),
    ('R27 Zeilenumbruch nach <a', SEITE,
     lambda h: h.replace('</body>', '<a\n  href="https://www.amazon.de/dp/B09TQPZQNW'
                         '?tag=ygmedia-21">Kaufen</a></body>', 1), 'ROT'),
    ('R27 Amazon-URL im inline script', SEITE,
     lambda h: h.replace('</body>', '<script>var u="https://www.amazon.de/dp/B0'
                         '?tag=ygmedia-21";</script></body>', 1), 'ROT'),
    ('R27 gtag im onclick-Attribut', SEITE,
     lambda h: h.replace('class="finder-opt"',
                         'onclick="gtag(\'event\',\'klick\')" class="finder-opt"', 1),
     'ROT'),
    ('R27 :is() versteckt', CSS,
     lambda c: c + '\n.finder-step:is(.is-active){display:none}\n', 'ROT'),
    ('R27 zwei Deklarationen, none zuletzt', CSS,
     lambda c: c + '\n.finder-step.is-active{display:block;display:none}\n', 'ROT'),
    ('R27 Preisfrage-Zahl von Hand geaendert', 'blog/was-kostet-ein-handy-controller/index.html',
     lambda h: h.replace('30 und 190', '30 und 240'), 'ROT'),
    ('R28 :has() am aktiven Schritt', CSS,
     lambda c: c + '\n.finder-step.is-active:has(.x){display:none}\n', 'ROT'),
    ('R28 :has() am Container', CSS,
     lambda c: c + '\n#finder:has(.x){display:none}\n', 'ROT'),
    ('R28 Amazon-URL in script mit data-json', SEITE,
     lambda h: h.replace('</body>', '<script data-json="1">var u="https://www.amazon.de/'
                         'dp/B0?tag=ygmedia-21";</script></body>', 1), 'ROT'),
    ('R28 Amazon-URL in script id=jsonld-helper', SEITE,
     lambda h: h.replace('</body>', '<script id="jsonld-helper">var u="https://'
                         'www.amazon.de/dp/B0?tag=ygmedia-21";</script></body>', 1), 'ROT'),
    ('R28 href mit einfachen Anfuehrungszeichen', SEITE,
     lambda h: h.replace('</body>', "<a href='https://www.amazon.de/dp/B0?tag=ygmedia-21'>"
                         "Kaufen</a></body>", 1), 'ROT'),
    ('R28 gtag im unquotierten onclick', SEITE,
     lambda h: h.replace('class="finder-opt"',
                         "onclick=gtag('event','x') class=\"finder-opt\"", 1), 'ROT'),
    ('R29 verschachteltes :is(:not())', CSS,
     lambda c: c + '\n.finder-step:is(:not(.gibtsnicht)){display:none}\n', 'ROT'),
    ('R29 :has() mit !important gewinnt', CSS,
     lambda c: c + '\n.finder-step:has(.x){display:none!important}\n', 'ROT'),
    # --- Faelle, die GRUEN bleiben muessen ---
    ('LEGITIM :not(:is()) als Refactoring', CSS,
     lambda c: c.replace(
         '.finder-step, .finder-result { display: none; }',
         '.finder-step:not(:is(.is-active)), .finder-result:not(:is(.is-active))'
         ' { display: none; }'), 'GRUEN'),
    ('LEGITIM :has() verliert gegen !important', CSS,
     lambda c: c.replace('.finder-step.is-active, .finder-result.is-active { display: block;',
                         '.finder-step.is-active, .finder-result.is-active'
                         ' { display: block !important;')
                + '\n.finder-step:has(.x){display:none}\n', 'GRUEN'),
    ('LEGITIM :has() an fremdem Element', CSS,
     lambda c: c + '\n.irgendwas:has(.x){display:none}\n', 'GRUEN'),
    ('LEGITIM A8-Doku im onclick-Kommentar', SEITE,
     lambda h: h.replace('class="finder-opt"',
                         'onclick="/* nie gtag(\'event\') */ void 0" class="finder-opt"',
                         1), 'GRUEN'),
    ('LEGITIM Amazon-Suchlink auf der Seite', SEITE,
     lambda h: h.replace('</body>', '<a href="https://www.amazon.de/s?k=controller">'
                         'Suche</a></body>', 1), 'GRUEN'),
    ('LEGITIM Amazon-URL im JSON-LD', SEITE,
     lambda h: h.replace('</body>', '<script type="application/ld+json">{"@type":"Offer",'
                         '"url":"https://www.amazon.de/dp/B0?tag=ygmedia-21"}</script>'
                         '</body>', 1), 'GRUEN'),
    ('LEGITIM :where() verliert an Spezifitaet', CSS,
     lambda c: c + '\n.finder-step:where(.is-active){display:none}\n', 'GRUEN'),
    ('LEGITIM :not() mit Nachfahre innen', CSS,
     lambda c: c + '\n.finder-step:not(.finder .is-active){display:none}\n', 'GRUEN'),
    ('LEGITIM :not() mit Komma-Liste, trifft nicht', CSS,
     lambda c: c.replace(
         '.finder-step, .finder-result { display: none; }',
         '.finder-step:not(.is-active, .is-done),'
         ' .finder-result:not(.is-active, .is-done) { display: none; }'), 'GRUEN'),
    ('LEGITIM Regel in @media, trifft nicht', CSS,
     lambda c: c + '\n@media print{.irgendwas{display:none}}\n', 'GRUEN'),
    ('LEGITIM opacity 1', CSS, lambda c: c + '\n.finder{opacity:1}\n', 'GRUEN'),
    ('LEGITIM Amazon-Hilfe-Link auf der Seite', SEITE,
     lambda h: h.replace('</body>', '<a href="https://www.amazon.de/gp/help/customer/'
                         'display.html?nodeId=201909010">Datenschutz</a></body>', 1),
     'GRUEN'),
    ('LEGITIM gtag-Doku in HTML-Prosa', SEITE,
     lambda h: h.replace('</body>', "<p>Wir benutzen nie gtag('event', ...).</p></body>",
                         1), 'GRUEN'),
    # Drei davon waren Fehlalarme des Gates, nicht Defekte: eine Umsortierung, die
    # :not()-Fassung derselben Regeln, und `[data-tier~="2"]` an einem fremden Element.
    # Die Spezifitaetszaehlung in scripts/css_kaskade.py hat sie geloest.
    ('LEGITIM :not()-Fassung der Finder-Regeln', CSS,
     lambda c: c.replace(
         '.finder-step, .finder-result { display: none; }',
         '.finder-step:not(.is-active), .finder-result:not(.is-active) { display: none; }'),
     'GRUEN'),
    ('LEGITIM [data-tier~=] an fremdem Element', CSS,
     lambda c: c + '\n.pf-group[data-tier~="2"]{opacity:0}\n', 'GRUEN'),
    ('LEGITIM anhaengender A8-Kommentar', JS,
     lambda j: j.replace('(function () {',
                         "(function () {\n  var z = 1;   // NICHT gtag('event', ...)"
                         " benutzen", 1), 'GRUEN'),
    ('LEGITIM A3-Regel im Kommentar', JS,
     lambda j: j.replace('(function () {',
                         "(function () {\n  // Kauflinks nur in main.js aus data-asin ->"
                         " amazon.de/dp/[ASIN]?tag=ygmedia-21", 1), 'GRUEN'),
    # Zwei davon sind Regeln, die NICHTS TREFFEN: `.finder-result` fuehrt kein `id`, und
    # `[class~="finder-step"]` ALLEIN hat nur Spezifitaet (0,1,0) und verliert gegen
    # `.finder-step.is-active`. Beide waren erst meine eigenen falschen Probe-Erwartungen
    # -- die Erwartung gehoert so geprueft wie das Gate.
    # Korrektur R25: Die Begruendung fuer den `[class~=]`-Fall war vorher falsch. Das
    # Gate hat die Regel damals gar nicht gewichtet, sondern an `~` zerschnitten und
    # verworfen -- die Doku erklaerte also ein Loch als Feature. Seit der
    # Spezifitaetszaehlung trifft die Begruendung wirklich zu.
    ('LEGITIM Regeln vertauscht (Spezifitaet entscheidet)', CSS,
     lambda c: c.replace(
         '.finder-step, .finder-result { display: none; }\n'
         '.finder-step.is-active, .finder-result.is-active { display: block;'
         ' animation: finderIn .35s ease; }',
         '.finder-step.is-active, .finder-result.is-active { display: block;'
         ' animation: finderIn .35s ease; }\n'
         '.finder-step, .finder-result { display: none; }'), 'GRUEN'),
    ('LEGITIM [id] trifft das Ergebnis nicht', CSS,
     lambda c: c + '\n.finder-result[id]{display:none}\n', 'GRUEN'),
    ('LEGITIM [class~=] verliert an Spezifitaet', CSS,
     lambda c: c + '\n[class~="finder-step"]{display:none}\n', 'GRUEN'),
    ('LEGITIM unveraendert', None, None, 'GRUEN'),
    ('LEGITIM CSS auf #finder-Nachfahren', CSS,
     lambda c: c.replace('.finder-step, .finder-result { display: none; }',
                         '#finder .finder-step, #finder .finder-result { display: none; }')
                .replace('.finder-step.is-active, .finder-result.is-active {',
                         '#finder .finder-step.is-active, #finder .finder-result.is-active {'),
     'GRUEN'),
    ('LEGITIM div.-Praefix', CSS,
     lambda c: c.replace('.finder-step, .finder-result { display: none; }',
                         'div.finder-step, div.finder-result { display: none; }'), 'GRUEN'),
    ('LEGITIM Kindkombinator', CSS,
     lambda c: c.replace('.finder-step, .finder-result { display: none; }',
                         '.finder > .finder-step, .finder > .finder-result { display: none; }'),
     'GRUEN'),
    ('LEGITIM flex statt block', CSS,
     lambda c: c.replace('.finder-step.is-active, .finder-result.is-active { display: block;',
                         '.finder-step.is-active, .finder-result.is-active { display: flex;'),
     'GRUEN'),
    ('LEGITIM unbeteiligte Zusatzregel', CSS,
     lambda c: c + '\n.irgendwas-anderes{display:none}\n', 'GRUEN'),
    ('LEGITIM is-active konsistent umbenannt', None, None, 'GRUEN'),
    ('LEGITIM Spec-Chip-slice auf 5', JS,
     lambda j: j.replace('(p.specs || []).slice(0, 3)', '(p.specs || []).slice(0, 5)'),
     'GRUEN'),
]


def _umbenennen(arbeit):
    """Sonderfall: is-active in JS, CSS und Markup zugleich umbenennen."""
    for datei, alt, neu in ((JS, "'is-active'", "'is-on'"),
                            (CSS, '.is-active', '.is-on'),
                            (SEITE, 'is-active', 'is-on')):
        p = os.path.join(arbeit, datei)
        # ERST lesen, DANN schreiben. Die erste Fassung stand als Einzeiler
        # `open(p,'w').write(open(p).read().replace(...))` da -- `open(p,'w')` leert die
        # Datei, bevor das innere `open(p).read()` sie liest, also landeten drei LEERE
        # Dateien im Probelauf. Der Fall "legitime Umbenennung" wurde dadurch rot
        # gemeldet, und zwar mit 12 Folgefehlern. Die Batterie hat einen Fehler in der
        # Batterie gefunden.
        roh = open(p, encoding='utf-8').read()
        open(p, 'w', encoding='utf-8').write(roh.replace(alt, neu))


def main():
    nur = None
    if '--nur' in sys.argv:
        nur = sys.argv[sys.argv.index('--nur') + 1]
    rumpf = tempfile.mkdtemp(prefix='spc-finder-')
    falsch, n = [], 0
    try:
        for name, datei, fn, soll in FAELLE:
            if nur and not name.startswith(nur):
                continue
            # FRISCHE Kopie je Fall. Ein wiederverwendetes Verzeichnis hat mich am
            # 02.10. eine Mutation als "unveraenderten Stand" lesen lassen.
            arbeit = os.path.join(rumpf, f'f{n}')
            shutil.copytree(ROOT, arbeit,
                            ignore=shutil.ignore_patterns('.git', 'node_modules', 'brain',
                                                      'SPC-Gaming-Visuals',
                                                          '__pycache__'))
            if name == 'LEGITIM is-active konsistent umbenannt':
                _umbenennen(arbeit)
            elif fn:
                p = os.path.join(arbeit, datei)
                roh = open(p, encoding='utf-8').read()
                neu = fn(roh)
                if neu == roh:
                    falsch.append(f'{name}: Mutation hat nichts geaendert')
                    n += 1
                    continue
                open(p, 'w', encoding='utf-8').write(neu)
            if datei in (JS, CSS) or name == 'LEGITIM is-active konsistent umbenannt':
                subprocess.run(['python3', 'scripts/bump_asset_version.py'], cwd=arbeit,
                               capture_output=True)
            r = subprocess.run(['python3', 'scripts/verify.py'], cwd=arbeit,
                               capture_output=True, text=True, timeout=300)
            aus = r.stderr + r.stdout
            fertig = bool(re.search(r'(GRÜN|ROT) —', aus))
            ist = ('ABBRUCH' if not fertig else ('ROT' if r.returncode else 'GRUEN'))
            rel = [x.strip() for x in aus.splitlines()
                   if 'FEHLER' in x and re.search(r'§A[1-8]|§B|§D', x)]
            print(f'{"ok " if ist == soll else ">>>"} {ist:7s} | {name:42s} | '
                  f'{len(rel):3d} | {(rel[0][7:76] if rel else "-")}')
            if ist != soll:
                falsch.append(f'{name} (soll {soll}, ist {ist})')
            shutil.rmtree(arbeit, ignore_errors=True)
            n += 1
        print(f'\n{n} Faelle geprueft, {len(falsch)} falsch')
        for f in falsch:
            print(f'  {f}')
        return 1 if falsch else 0
    finally:
        shutil.rmtree(rumpf, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
