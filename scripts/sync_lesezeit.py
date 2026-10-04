#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zieht jede genannte Lesezeit auf den tatsaechlichen Textumfang nach (§A1-Prinzip).

Die Zahl steht an drei Stellen: in der Byline des Artikels selbst, in seiner Karte auf
/blog/ und -- bei den drei hervorgehobenen Artikeln -- in seiner Karte auf der Startseite.
Quelle ist immer der Artikel: seine eigene Wortzahl bestimmt seine Minuten, und die Karten
uebernehmen genau diese Minuten. Damit kann eine Karte nicht mehr etwas anderes behaupten
als die Seite, auf die sie zeigt.

Die Rechenregel selbst steht in lesezeit.py, geteilt mit gen_preisfrage.py und verify.py.

Aufruf:  python3 scripts/sync_lesezeit.py
         python3 scripts/sync_lesezeit.py --check   (nur melden, nichts schreiben)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from lesezeit import minuten, BYLINE, KARTE  # noqa: E402

# Byline- und Karten-Muster kommen aus lesezeit.py, geteilt mit verify.py.
# Listenseiten, die Lesezeiten fremder Artikel zeigen.
LISTEN = ['blog/index.html', 'index.html']


def artikelseiten():
    return [f for f in sorted(glob.glob('blog/*/index.html'))
            if BYLINE.search(open(f, encoding='utf-8').read())]


def unerfasst():
    """Blog-Seiten, die eine Lesezeit nennen, die BYLINE aber nicht findet.

    Ohne diese Pruefung meldet das Script seinen eigenen Blindfleck als Erfolg: Der
    Pruefer hat am 01.10. eine Byline-Klasse umbenannt, worauf hier "18 Artikel mit
    Lesezeit ... 0 Abweichungen" stand und der Exit-Code 0 blieb, waehrend die Seite
    eine falsche Zahl trug. 19 ist keine Zahl, die dieses Script kannte -- es hat
    gezaehlt, was es findet, und das Gefundene fuer vollstaendig erklaert.
    """
    aus = []
    for f in sorted(glob.glob('blog/*/index.html')):
        h = open(f, encoding='utf-8').read()
        if 'Lesezeit' in h and not BYLINE.search(h):
            aus.append(f)
    return aus


def soll_je_pfad():
    """Pfad ('/blog/slug/') -> Minuten, berechnet aus dem Artikel selbst.

    Zweiter Rueckgabewert: die Seiten, fuer die sich keine Minuten bestimmen lassen. Sie
    muessen in den Exit-Code durchschlagen, sonst meldet dieses Script seinen eigenen
    Fehler als Erfolg -- derselbe Fehler, den `unerfasst()` schon einmal hatte.
    """
    ohne = []
    s = {}
    for f in artikelseiten():
        m = minuten(open(f, encoding='utf-8').read())
        if m is None:
            # Ohne <main> gibt minuten() None zurueck. Die erste Fassung liess die Seite
            # dann stumm aus dem Soll fallen, und der Byline-Durchlauf griff danach
            # unbedingt zu: KeyError mit Traceback statt einer Meldung.
            print(f'  FEHLER: {f} hat kein <main>-Element, die Lesezeit laesst sich '
                  f'nicht bestimmen')
            ohne.append(f)
            continue
        s['/' + os.path.dirname(f) + '/'] = m
    return s, ohne


def main():
    nur_pruefen = '--check' in sys.argv
    soll, ohne_main = soll_je_pfad()
    geaendert, abweichungen = 0, []

    # 1. Die Byline jedes Artikels auf seine eigene Wortzahl ziehen.
    for f in artikelseiten():
        t = open(f, encoding='utf-8').read()
        if '/' + os.path.dirname(f) + '/' not in soll:
            continue  # oben schon gemeldet
        m = soll['/' + os.path.dirname(f) + '/']
        neu = BYLINE.sub(lambda x: x.group(1) + str(m) + x.group(3), t, count=1)
        if neu != t:
            alt = BYLINE.search(t).group(2)
            abweichungen.append(f'{f}: Byline sagt {alt}, Text ergibt {m}')
            geaendert += 1
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)

    # 2. Jede Karte auf die Minuten des Artikels ziehen, auf den sie zeigt.
    for f in LISTEN:
        if not os.path.exists(f):
            continue
        t = open(f, encoding='utf-8').read()
        treffer = []

        def ersetze(x):
            ziel = soll.get(x.group(1))
            if ziel is None or int(x.group(2)) == ziel:
                return x.group(0)
            treffer.append(f'{f}: Karte {x.group(1)} sagt {x.group(2)}, '
                           f'der Artikel ergibt {ziel}')
            return x.group(0).replace(f'>{x.group(2)}{x.group(3)}',
                                      f'>{ziel}{x.group(3)}')

        neu = KARTE.sub(ersetze, t)
        if neu != t:
            abweichungen += treffer
            geaendert += 1
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)

    for a in abweichungen:
        print(f'  {a}')
    blind = unerfasst()
    for f in blind:
        print(f'  FEHLER: {f} nennt eine Lesezeit, die das Byline-Muster nicht findet — '
              f'diese Seite wird NICHT nachgezogen')
    print(f'{len(soll)} Artikel mit Lesezeit, Regel: 200 Woerter pro Minute')
    print(f"{geaendert} Datei(en) {'waeren geaendert' if nur_pruefen else 'nachgezogen'}, "
          f'{len(abweichungen)} Abweichung(en), {len(blind)} unerfasst, '
          f'{len(ohne_main)} ohne <main>')
    return 1 if (blind or ohne_main or (nur_pruefen and geaendert)) else 0


if __name__ == '__main__':
    sys.exit(main())
