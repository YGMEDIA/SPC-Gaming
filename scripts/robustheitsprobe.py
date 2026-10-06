#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Messvorschrift hinter der Aussage "N Defektformen, keine bricht ab".

Warum als Skript im Repo und nicht als Zahl in STATUS: Die Behauptung "`verify.py` ist
sauber" stand dort zweimal und war zweimal falsch. Danach stand eine Zahl da, und drei
Messungen ergaben drei Ergebnisse, weil niemand dieselbe Menge gemessen hat. Der
zwanzigste Pruefbericht hat angemerkt, dass die Vorschrift nur im Session-Scratchpad lag
und nach der Session nicht reproduzierbar war. Jetzt laeuft sie hier, jeder kann sie
nachfahren, und die Zahl in der Doku ist ihre Ausgabe.

Was gemessen wird: Jedes Feld von products.json bekommt einen falschen Typ, ueber ALLE
Produkte gleichzeitig (eine Probe an einem Produkt erreicht die Stellen hinter Filtern
nicht -- so sind in Runde 17 drei von fuenf Abbruchstellen unentdeckt geblieben). Dazu
Sonderformen, die kein Feldtyp beschreibt.

Drei Ergebnisse sind moeglich, und nur das erste ist in Ordnung:
  gemeldet      verify.py laeuft durch und nennt den Fehler  (richtig)
  ABBRUCH       verify.py stirbt mit Traceback               (alles dahinter ungeprueft)
  HAENGT        verify.py endet nicht                        (schlimmer: nicht mal ein
                                                              Exit-Code, keine Meldung)
  STUMM GRUEN   verify.py bleibt gruen                       (der Defekt geht live)

Aufruf:  python3 scripts/robustheitsprobe.py
         python3 scripts/robustheitsprobe.py --kurz   (nur die Zusammenfassung)

Das Skript arbeitet in einer KOPIE unter einem temporaeren Verzeichnis und laesst das Repo
unberuehrt. Es gehoert nicht in CI: ein Durchlauf startet verify.py einmal je Defektform
PLUS einmal fuer den unveraenderten Schlusslauf. Hier stand die Zahl der Defektformen
(117) als Zahl der Starts, also eine zu wenig (R30) -- die Anzahl gibt jetzt der Lauf aus.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from produktdaten import (TEXTFELDER, LISTENFELDER,   # noqa: E402
                          OBJEKTFELDER)

# Die Feldliste wird GELESEN, nicht gepflegt. Sie stand hier als eigene Kopie mit 15
# Namen, und am 06.10.2026 kam `stock` in den Datenkern -- die Probe hat es nicht
# geprueft und trotzdem "117 Defektformen, keine bricht ab" gemeldet. Das ist genau die
# Klasse, die `produktdaten.py` fuer den Datenkern selbst schliesst ("ein Feld, das in
# keiner Liste steht, ist selbst ein Befund"): eine zweite, handgepflegte Liste derselben
# Sache. Ein neues Feld erweitert die Probe jetzt von allein, und die Zahl der
# Defektformen wird vom Lauf ausgegeben statt getippt.
FELDER = list(TEXTFELDER) + list(LISTENFELDER) + list(OBJEKTFELDER)
WERTE = [('Zahl', 7), ('Liste', ['a', 'b']), ('None', None), ('Objekt', {'x': 1}),
         ('leer', ''), ('bool', True), ('float', 1.5)]
SONDERFORMEN = [
    ('spec 1-elementig', lambda d: [x['specs'].append(['K']) for x in d]),
    ('spec 3-elementig', lambda d: [x['specs'].append(['A', 'B', 'C']) for x in d]),
    ('spec-Wert None', lambda d: [x.update(specs=[[k, None] for k, v in x['specs']]) for x in d]),
    ('spec-Wert Liste', lambda d: [x.update(specs=[[k, [v]] for k, v in x['specs']]) for x in d]),
    ('worksOn [1,2]', lambda d: [x.update(worksOn=[1, 2]) for x in d]),
    ('worksOn [None]', lambda d: [x.update(worksOn=[None]) for x in d]),
    ('gallery [7]', lambda d: [x.update(gallery=[7]) for x in d]),
    ('unbekanntes Feld', lambda d: [x.update(neuesFeld='x') for x in d]),
    ('Eintrag kein Objekt', lambda d: d.append('kaputt')),
    ('leeres Array', lambda d: d.clear()),
    ('name nur Leerzeichen', lambda d: [x.update(name='  ') for x in d]),
    ('ein name leer', lambda d: d[0].update(name='')),
]
# 240 s: Der Haenger aus Runde 19 (ein leeres `name`) lief ueber 600 s. Ohne Grenze
# haengt diese Probe genauso wie das Gate, das sie pruefen soll.
GRENZE = 240


def lauf(arbeit):
    try:
        r = subprocess.run(['python3', 'scripts/verify.py'], cwd=arbeit,
                           capture_output=True, text=True, timeout=GRENZE)
    except subprocess.TimeoutExpired:
        return 'HAENGT', f'kein Ende nach {GRENZE} s'
    aus = r.stderr + r.stdout
    if not re.search(r'(GRÜN|ROT) —', aus):
        z = re.findall(r'(?:verify|kompat|produktdaten|audit_prosa|lesezeit|dom_baum)'
                       r'\.py", line (\d+)', aus)
        letzte = [x for x in aus.strip().splitlines() if x.strip()]
        return 'ABBRUCH', f'Z{z[-1] if z else "?"}: {letzte[-1][:70] if letzte else ""}'
    if r.returncode == 0:
        return 'STUMM GRUEN', 'verify bleibt gruen'
    return 'gemeldet', ''


def main():
    kurz = '--kurz' in sys.argv
    arbeit = tempfile.mkdtemp(prefix='spc-robustheit-')
    try:
        shutil.copytree(ROOT, os.path.join(arbeit, 'repo'),
                        ignore=shutil.ignore_patterns('.git', 'node_modules', 'brain',
                                                      'SPC-Gaming-Visuals',
                                                      '__pycache__'))
        arbeit = os.path.join(arbeit, 'repo')
        pfad = os.path.join(arbeit, 'assets/data/products.json')
        basis = json.load(open(pfad, encoding='utf-8'))
        befunde, n = [], 0

        def probe(etikett, bauen):
            nonlocal n
            d = json.loads(json.dumps(basis))
            bauen(d)
            json.dump(d, open(pfad, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            art, wie = lauf(arbeit)
            n += 1
            if art != 'gemeldet':
                befunde.append(f'{art}: {etikett} ({wie})')
            if not kurz:
                print(f'  {art:11s} {etikett}')

        for feld in FELDER:
            for wname, wert in WERTE:
                probe(f'{feld}={wname}',
                      lambda d, f=feld, w=wert: [x.update({f: w}) for x in d
                                                 if isinstance(x, dict)])
        for name, fn in SONDERFORMEN:
            probe(name, fn)

        json.dump(basis, open(pfad, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        art, _ = lauf(arbeit)
        print(f'\n{n} Defektformen geprueft, je ueber alle {len(basis)} Produkte '
              f'({n + 1} verify.py-Starts: je Form einer plus der Schlusslauf)')
        print(f'{len(befunde)} Befund(e); unveraenderter Stand: '
              f'{"gruen" if art == "STUMM GRUEN" else art}')
        for b in befunde:
            print(f'  {b}')
        # Der unveraenderte Stand MUSS gruen sein, sonst messen die Proben gegen einen
        # schon roten Lauf und jedes "gemeldet" waere bedeutungslos.
        return 1 if (befunde or art != 'STUMM GRUEN') else 0
    finally:
        shutil.rmtree(os.path.dirname(arbeit), ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
