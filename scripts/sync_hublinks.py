#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setzt den Rueckweg-Block (B7) in die handgepflegten Review-Seiten.

Dieselbe Aufteilung wie bei B1: Die 29 generierten /produkte/-Seiten bekommen den Block
von gen_pages.py, die 13 handgepflegten Review-Seiten unter /controller/ von hier. BEIDE
Wege rufen `hublinks.hublinks_html()` -- eine Quelle fuer die Regel, eine fuer die
Zuordnung, eine fuers Escaping.

Warum ueberhaupt: Gemessen am 04.10.2026 verlinken alle vier Marken-Hubs lueckenlos ihre
Produkte, und alle 14 Produkte dieser Marken verlinken NICHT zurueck. Dieselbe
Einseitigkeit bei den Plattform-Hubs (29 von 42 Produktseiten ohne einen einzigen
Plattform-Link). Die Begruendung steht ausfuehrlich im Docstring von hublinks.py.

Aufruf:  python3 scripts/sync_hublinks.py
         python3 scripts/sync_hublinks.py --check   (nur melden, nichts schreiben)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

from gen_hubs import esc                      # dieselbe Escaping-Regel wie die Karten
from hublinks import (taxonomie_karte, hublinks_html, block, entferne, MARKER,
                      ist_stub)
from produktdaten import text as pfeld

# Der Block gehoert ans ENDE DER INHALTSSPALTE, nicht zwischen die Spalten. Meine erste
# Fassung setzte ihn direkt vor `<aside` -- und damit als dritte Zelle in ein
# zweispaltiges CSS-Grid (`.review-grid`). Im Browser stand er dann oben rechts in der
# Seitenleiste neben dem Kurz-Urteil. Gefunden hat das die Sichtpruefung im Browser, kein
# Gate: HTML und Linkziele waren die ganze Zeit korrekt.
#
# Gemessen ueber alle 13 Review-Seiten: Beim `<aside` sind genau zwei <div> offen
# (`container`, `review-grid`), die Inhaltsspalte ist also bereits geschlossen. Ihr
# schliessendes `</div>` steht unmittelbar davor -- auf 9 Seiten direkt, auf 4 mit einem
# HTML-Kommentar dazwischen ("<!-- Sticky CTA Sidebar -->"). Deshalb wird rueckwaerts
# ueber Leerraum UND Kommentare gelaufen, statt ein Muster zu raten.
ANKER = '<aside'


def einfuegepunkt(s):
    """Index VOR dem </div>, das die Inhaltsspalte schliesst, oder None.

    Gezaehlt wird auf dem Text OHNE Kommentare und auf Element-Starts (`<aside\\b`). Die
    erste Fassung zaehlte `'<aside'` im Rohtext -- ein HTML-Kommentar, der das Wort
    erwaehnt, machte die Pruefung rot, und zwar mit einer Meldung, die in die falsche
    Richtung zeigte ("davor kein </div>", obwohl es da war). Der Kommentar zwei Zeilen
    weiter oben erklaert, dass rueckwaerts UEBER Kommentare gelaufen wird; die Zaehlung
    hat genau diese Vorsorge zunichte gemacht.
    """
    ohne_k = re.sub(r'<!--.*?-->', lambda m: ' ' * len(m.group(0)), s, flags=re.S)
    treffer = [m.start() for m in re.finditer(r'<aside\b', ohne_k)]
    if len(treffer) != 1:
        return None
    i = treffer[0]
    while True:
        rest = s[:i].rstrip()
        if rest.endswith('-->'):
            j = rest.rfind('<!--')
            if j < 0:
                return None
            i = j
            continue
        if not rest.endswith('</div>'):
            return None
        return len(rest) - len('</div>')


def zielseiten():
    """Die handgepflegten Produktseiten: alles ausser /produkte/ (die baut gen_pages)."""
    items = json.load(open('assets/data/products.json', encoding='utf-8'))
    aus = []
    for p in items:
        detail = (pfeld(p, 'detail') or '').strip('/')
        if not detail or detail.startswith('produkte/'):
            continue
        f = detail + '/index.html'
        if os.path.exists(f):
            aus.append((p, f))
    return aus


def main():
    nur_pruefen = '--check' in sys.argv
    karte, ohne_h1 = taxonomie_karte()
    geaendert, befunde, ohne_hub = 0, [], []
    for u in ohne_h1:
        befunde.append(f'{u} ist eine Uebersicht ohne <h1> — ohne sie gibt es keine '
                       f'Beschriftung, und der Rueckweg wuerde die nackte URL als '
                       f'Satzbaustein zeigen')

    for p, f in zielseiten():
        s = open(f, encoding='utf-8').read()
        inhalt = hublinks_html(pfeld(p, 'detail'), karte, esc)
        if not inhalt:
            # Kein Hub fuehrt dieses Produkt. Das ist ein BEFUND, kein stilles
            # Ueberspringen: Eine Produktseite, die in keiner Uebersicht steht, ist fuer
            # den Leser nur ueber die Suche erreichbar.
            ohne_hub.append(pfeld(p, 'slug'))
            continue
        ohne = entferne(s)
        stelle = einfuegepunkt(ohne)
        if stelle is None:
            _n = len(re.findall(r'<aside\b',
                                re.sub(r'<!--.*?-->', ' ', ohne, flags=re.S)))
            befunde.append(
                f'{f}: das Ende der Inhaltsspalte ist nicht bestimmbar — '
                + (f'`<aside>` kommt {_n}x vor, erwartet genau 1'
                   if _n != 1 else 'davor steht kein `</div>`'))
            continue
        neu = ohne[:stelle] + block(inhalt) + '\n' + ohne[stelle:]
        if neu != s:
            geaendert += 1
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)
            print(f'  {"wuerde geaendert" if nur_pruefen else "gesetzt"}: {f}')

    for b in befunde:
        print(f'  FEHLER: {b}')
    for s in ohne_hub:
        print(f'  FEHLER: {s} steht in keiner Uebersicht — die Produktseite ist dann nur '
              f'ueber die Suche erreichbar')
    n = len(zielseiten())
    print(f'\n{n} handgepflegte Produktseiten, {geaendert} '
          f'{"abweichend" if nur_pruefen else "gesetzt"}, '
          f'{len(befunde) + len(ohne_hub)} Befund(e)')
    if befunde or ohne_hub:
        return 1
    if nur_pruefen and geaendert:
        print('  Fix: python3 scripts/sync_hublinks.py')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
