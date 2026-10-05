#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setzt den B10-Hinweis in die handgepflegten Review-Seiten.

Dieselbe Aufteilung wie bei B1 und B7: Die 29 generierten /produkte/-Seiten bekommen den
Block von gen_pages.py, die 13 handgepflegten Reviews unter /controller/ von hier. BEIDE
rufen `guenstiger.html()` -- eine Quelle fuer die Regel, eine fuers Escaping.

Von den sechs Produkten, auf die die Regel heute zutrifft, liegen vier hier
(gamesir-g8-plus, backbone-one-ps, gamesir-x2s, razer-kishi-v3-pro) und zwei unter
/produkte/. Die uebrigen neun Review-Seiten bekommen KEINEN Block -- der Hinweis gilt
nur, wo es wirklich ein guenstigeres, besser bewertetes Geschwister gibt.

Aufruf:  python3 scripts/sync_guenstiger.py
         python3 scripts/sync_guenstiger.py --check   (nur melden, nichts schreiben)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

from gen_hubs import esc                      # dieselbe Escaping-Regel wie die Karten
from guenstiger import html as guenstiger_html, block, MARKER
from produktdaten import text as pfeld

# Vor der Einordnungs-Box, also an derselben Stelle, an der B1 seinen
# Kompatibilitaets-Block setzt. Das ist die erste inhaltliche Aussage der Seite, und ein
# guenstigeres, besser bewertetes Geschwister gehoert vor das Urteil, nicht dahinter:
# Wer erst nach dem Kurz-Urteil erfaehrt, dass es ein besseres Angebot gibt, hat die
# Entscheidung schon getroffen.
ANKER = '<div class="verdict-box">'

ANF, END = f'<!-- {MARKER}:START -->', f'<!-- {MARKER}:END -->'


def entferne(s):
    return re.sub(rf'{re.escape(ANF)}.*?{re.escape(END)}\n?\s*', '', s, flags=re.S)


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
    return items, aus


def main():
    nur_pruefen = '--check' in sys.argv
    items, seiten = zielseiten()
    geaendert, befunde, mit_block = 0, [], 0

    for p, f in seiten:
        s = open(f, encoding='utf-8').read()
        inhalt = guenstiger_html(p, items, esc)
        ohne = entferne(s)
        if not inhalt:
            # Kein guenstigeres, besser bewertetes Geschwister: Der Block gehoert WEG.
            # Ein stehengebliebener Hinweis waere schlimmer als keiner -- er behauptet
            # ein Angebot, das es nicht mehr gibt.
            neu = ohne
        else:
            if ANKER not in ohne:
                befunde.append(f'{f}: Anker "{ANKER}" fehlt')
                continue
            if ohne.count(ANKER) != 1:
                befunde.append(f'{f}: Anker "{ANKER}" kommt {ohne.count(ANKER)}x vor, '
                               f'erwartet genau 1')
                continue
            neu = ohne.replace(ANKER, block(inhalt) + '\n          ' + ANKER, 1)
            mit_block += 1
        if neu != s:
            geaendert += 1
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)
            print(f'  {"wuerde geaendert" if nur_pruefen else "gesetzt"}: {f}')

    for b in befunde:
        print(f'  FEHLER: {b}')
    print(f'\n{len(seiten)} handgepflegte Produktseiten, {mit_block} mit Hinweis, '
          f'{geaendert} {"abweichend" if nur_pruefen else "geschrieben"}, '
          f'{len(befunde)} Befund(e)')
    if befunde:
        return 1
    if nur_pruefen and geaendert:
        print('  Fix: python3 scripts/sync_guenstiger.py')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
