#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schreibt das Finder-Zeitversprechen an alle sieben Stellen (B12).

Die Zahl steht in zeitversprechen.py, die Stellen auch. Dieses Script setzt sie und
meldet jede Stelle, deren Muster nicht mehr genau einmal passt -- das ist der Fall, in
dem jemand die Zusage entfernt oder umformuliert hat.

Aufruf:  python3 scripts/sync_zeitversprechen.py
         python3 scripts/sync_zeitversprechen.py --check   (nur melden, nichts schreiben)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

from zeitversprechen import SEKUNDEN, STELLEN, pruefe, setze


def main():
    nur_pruefen = '--check' in sys.argv
    dateien = sorted({d for d, _, _ in STELLEN})
    geaendert, befunde = 0, []

    for datei in dateien:
        if not os.path.exists(datei):
            befunde.append(f'{datei}: Seite fehlt, traegt aber eine Zusage')
            continue
        alt = open(datei, encoding='utf-8').read()
        neu = setze(datei, alt)
        if neu != alt:
            geaendert += 1
            if not nur_pruefen:
                open(datei, 'w', encoding='utf-8').write(neu)
            print(f'  {"wuerde geaendert" if nur_pruefen else "gesetzt"}: {datei}')
        befunde += pruefe(datei, neu)[0]

    for b in befunde:
        print(f'  FEHLER: {b}')
    print(f'\n{len(STELLEN)} Zusagen auf {len(dateien)} Seiten, Quelle: {SEKUNDEN} '
          f'Sekunden, {geaendert} Datei(en) '
          f'{"abweichend" if nur_pruefen else "geschrieben"}, {len(befunde)} Befund(e)')
    if befunde:
        return 1
    if nur_pruefen and geaendert:
        print('  Fix: python3 scripts/sync_zeitversprechen.py')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
