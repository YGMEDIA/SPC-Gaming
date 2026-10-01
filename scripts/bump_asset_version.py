#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zieht die Versionsparameter aller eingebundenen CSS/JS-Assets auf ihren Inhalts-Hash nach.

main.js traegt den Footer mit Impressum, Datenschutz und Affiliate-Hinweis. Ohne
Versionsparameter behalten wiederkehrende Besucher eine alte Fassung, bis ihr Cache
ablaeuft - bei rechtlich relevanten Texten ist das nicht hinnehmbar.

Ab 30.09.2026 gilt das fuer JEDES Asset, nicht nur main.js: style.css bestimmt, ob die
Pflichtangaben ueberhaupt lesbar sind, und finder.js / hub-render.js / produkte.js
rendern Preise und Produktkarten. Eine veraltete Fassung davon zeigt alte Preise, also
genau den Fehler, gegen den das ganze products.json-Gate gebaut ist.

Nach jeder Aenderung an einem Asset einmal laufen lassen; verify.py prueft es.
"""
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Jede Datei, die eine Seite ueber <link> oder <script> nachlaedt.
ASSETS = ['assets/css/style.css', 'assets/js/main.js', 'assets/js/finder.js',
          'assets/js/hub-render.js', 'assets/js/produkte.js']
# Auch die Generatoren tragen die Pfade als Literal, sonst schreibt der naechste Lauf
# die alte Version zurueck.
ZIELE = sorted(glob.glob('**/index.html', recursive=True)) + \
        (['404.html'] if os.path.exists('404.html') else []) + \
        ['scripts/gen_pages.py', 'scripts/gen_longtail.py', 'scripts/gen_hubs.py',
         'scripts/gen_preisfrage.py']


def hashes():
    h = {}
    for a in ASSETS:
        if os.path.exists(a):
            h[a] = hashlib.sha256(open(a, 'rb').read()).hexdigest()[:8]
    return h


def main():
    h = hashes()
    fehlt = [a for a in ASSETS if a not in h]
    if fehlt:
        print('WARNUNG: nicht gefunden: ' + ', '.join(fehlt))
    geaendert = 0
    for f in ZIELE:
        if not os.path.exists(f):
            continue
        t = open(f, encoding='utf-8').read()
        neu = t
        for pfad, digest in h.items():
            neu = re.sub(re.escape('/' + pfad) + r'(?:\?v=[0-9a-f]+)?(?=["\'])',
                         f'/{pfad}?v={digest}', neu)
        if neu != t:
            open(f, 'w', encoding='utf-8').write(neu)
            geaendert += 1
    for pfad, digest in sorted(h.items()):
        print(f'  {pfad}?v={digest}')
    print(f'{geaendert} Datei(en) nachgezogen')
    return 0


if __name__ == '__main__':
    sys.exit(main())
