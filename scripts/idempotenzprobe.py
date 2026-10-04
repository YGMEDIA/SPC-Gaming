#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft, dass jeder Generator und jeder Sync dasselbe Ergebnis liefert, dreimal.

Warum als Skript im Repo: Die Zahl stand im Protokoll als "elf Generatoren je dreimal
idempotent". Der Pruefer hat zwoelf gezaehlt (`gen_*` 6 plus `sync_*` 6) -- beide Zahlen
sind mit verschiedenen Definitionen richtig, und genau das ist der Fehler: eine Zahl ohne
Messvorschrift. Die Vorschrift steht jetzt hier, und die Menge wird ERMITTELT, nicht
aufgezaehlt -- aber nach der HAUSKONVENTION, nicht nach "jedes Skript, das schreibt": Ein
Schreiber heisst `gen_*` oder `sync_*` (oder `bump_asset_version.py`), und wer einen so
anlegt, ist automatisch dabei. Ein Schreiber mit anderem Namen faellt still heraus; hier
stand lange die weitere Fassung, waehrend die Ausgabe des Laufs die richtige nannte
(R29).

Dieselbe Klasse ein Stockwerk tiefer, und deshalb steht hier keine Liste mehr: Danach
stand hier eine HANDGEZAEHLTE Aufzaehlung der Skripte, die ausserhalb der Vorschrift
liegen -- fuenf Namen, falsch in beide Richtungen (R30). `verify.py` war genannt, hat aber
gar keinen `__main__`-Guard und gehoert damit nicht in die Menge; fuenf andere fehlten.
Und der beruhigende Nachsatz "alle sind Pruefer oder Proben und schreiben nur in Kopien"
deckte ausgerechnet die zwei, fuer die er nicht gilt: `indexnow_ping.py` meldet
Sitemap-URLs an Bing, `md_to_pdf.py` schreibt eine Datei ins Repo. Die Menge wird jetzt
ERMITTELT und bei jedem Lauf ausgegeben, mit dem Weg nach aussen je Name -- eine Zahl ohne
Messvorschrift war der Fehler, eine Namensliste ohne Messvorschrift ist derselbe.

Geprueft werden zwei Eigenschaften, und die zweite ist die wichtigere:
  idempotent    Lauf 2 und 3 aendern nichts mehr gegenueber Lauf 1.
  baumstabil    Lauf 1 aendert schon nichts -- der committete Stand IST die Ausgabe der
                Generatoren. Ohne das waere "idempotent" wertlos: Ein Skript, das die
                Seiten bei jedem Lauf gleich kaputt macht, ist auch idempotent.

Aufruf:  python3 scripts/idempotenzprobe.py
         python3 scripts/idempotenzprobe.py --nur gen_hubs

Arbeitet in einer Kopie, laesst das Repo unberuehrt. Nicht in CI: dauert mehrere Minuten.
"""
import glob
import hashlib
import re
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# WELCHE Skripte geprueft werden, nach Regel statt nach Liste -- aber mit einer harten
# Sperre davor. Die erste Fassung nahm "jedes scripts/*.py mit __main__ ausser den
# Pruefskripten" und hat damit `indexnow_ping.py` eingesammelt: Das meldet ohne Argumente
# ALLE Sitemap-URLs an Bing, also eine nach aussen wirkende Aktion, dreimal. Ich habe den
# Lauf nach etwa 20 Sekunden abgebrochen, bevor er alphabetisch dort war -- beweisen laesst
# sich das nicht, und genau deshalb steht die Sperre jetzt hier und nicht in meinem Kopf.
#
# Zwei Bedingungen, beide notwendig:
#   1. Der Name folgt der Hauskonvention fuer Schreiber: `gen_*`, `sync_*` oder
#      `bump_asset_version.py`. Ein neuer Generator ist damit automatisch dabei.
#   2. Das Skript importiert KEINE Netzbibliothek. Was nach draussen wirkt, wird nicht
#      dreimal probehalber ausgefuehrt.
# `subprocess` ist dabei: ein Shell-Aufruf (`curl`, `git push`) wirkt genauso
# nach aussen wie ein urlopen. `__import__` macht die Datei unentscheidbar.
# Jede Bibliothek, die nach aussen wirken kann. Geprueft wird per PRAEFIX, nicht per
# exakter Wurzelgleichheit: `urllib3` ist nicht `urllib` und ging damit durch (R27),
# dieselbe Klasse traf `aiohttp`, `multiprocessing`, `xmlrpc.client`, `pty` und `asyncio`.
NETZ = ('urllib', 'requests', 'httpx', 'aiohttp', 'http', 'socket', 'ssl',
        'ftplib', 'smtplib', 'poplib', 'imaplib', 'telnetlib', 'webbrowser', 'xmlrpc',
        'subprocess', 'multiprocessing', 'asyncio', 'pty', 'paramiko', 'boto3')
# Aufrufe, die einen Prozess starten oder dynamisch importieren. `os.posix_spawn` fehlte,
# weil die Praefixpruefung auf `os.spawn` lief (R27).
PROZESS = ('os.system', 'os.popen', 'os.startfile', 'os.exec', 'os.spawn',
           'os.posix_spawn', 'os.fork', 'pty.spawn', 'importlib.import_module',
           '__import__', 'asyncio.create_subprocess', 'subprocess.')

ARGUMENTE = {'gen_pages.py': ['--regen']}   # sonst schreibt es nur neue Seiten


def _schreiber(name):
    return (name.startswith(('gen_', 'sync_')) or name == 'bump_asset_version.py')


# Untermodule, die trotz Netz-Wurzel nichts nach aussen tun: reine Zeichenarbeit. Ohne
# diese Ausnahme waere ein Generator, der URLs kodiert, still aus der Idempotenzprobe
# gefallen -- mit falscher Begruendung in der Ausgabe (R28, latenter Fehlalarm).
REIN = ('urllib.parse', 'urllib.error', 'http.cookies', 'http.HTTPStatus',
        'http.cookiejar', 'email.utils')


def _netz_treffer(name):
    """Netz- oder Prozess-Bibliothek? Per PRAEFIX auf der Wurzel, mit Ausnahmen."""
    if any(name == r or name.startswith(r + '.') for r in REIN):
        return False
    wurzel = name.split('.')[0]
    return any(wurzel == m or wurzel.startswith(m) for m in NETZ)


def _netzmodule(quelle, pfad=None, tiefe=0, gesehen=None):
    """Welche Wege nach aussen dieses Skript hat -- auch ueber Hilfsmodule.

    Vier Fassungen, vier Befunde:
      R24  Keine Sperre. Ein Skript, das Sitemap-URLs an Bing meldet, waere dreimal
           gelaufen; nur ein Abbruch nach 20 Sekunden hat das verhindert.
      R25  Die Sperre verlangte den Namen DIREKT hinter `import` und traf damit
           `import json, re, sys, os, urllib.request` nicht -- also genau das Skript, um
           das es ging.
      R26  Fuenf weitere Wege: `os.system`, ein TRANSITIVER Import, `importlib`,
           `import a; import urllib`, eine Fortsetzungszeile.
      R27  Acht weitere: `urllib3` (nicht gleich `urllib`), `aiohttp`, `multiprocessing`,
           `xmlrpc.client`, `pty.spawn`, `asyncio`-Subprozesse, `os.posix_spawn` -- und,
           dieselbe Klasse wie R25, `import os as x; x.system(...)`.
    Jetzt: Importe per `ast`, Praefixpruefung, ALIAS-Verfolgung, Prozess-Aufrufe ueber
    eine eigene Liste, lokale Hilfsmodule bis Tiefe 3 (die Kette gen_pages -> kompat ->
    produktdaten existiert schon).
    """
    import ast
    if gesehen is None:
        gesehen = set()
    gefunden = set()
    try:
        baum = ast.parse(quelle)
    except SyntaxError:
        return ['nicht parsebar']
    lokale, alias = [], {}
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            for a in knoten.names:
                alias[a.asname or a.name.split('.')[0]] = a.name
                if _netz_treffer(a.name):
                    gefunden.add(a.name)
                elif _ist_lokal(a.name.split('.')[0]):
                    lokale.append(a.name.split('.')[0])
        elif isinstance(knoten, ast.ImportFrom) and knoten.module:
            if _netz_treffer(knoten.module):
                gefunden.add(knoten.module)
            elif _ist_lokal(knoten.module.split('.')[0]):
                lokale.append(knoten.module.split('.')[0])
            for a in knoten.names:
                alias[a.asname or a.name] = knoten.module + '.' + a.name
        elif isinstance(knoten, ast.Call):
            _n = _aufrufname(knoten.func)
            _teile = _n.split('.')
            if _teile and _teile[0] in alias:
                _n = alias[_teile[0]] + ('.' + '.'.join(_teile[1:]) if _teile[1:] else '')
            if any(_n == p or _n.startswith(p) for p in PROZESS):
                gefunden.add(_n + ' (Weg nach aussen)')
    if tiefe < 3:
        for m in dict.fromkeys(lokale):
            if m in gesehen:
                continue
            gesehen.add(m)
            p = os.path.join(ROOT, 'scripts', m + '.py')
            if os.path.exists(p):
                for x in _netzmodule(open(p, encoding='utf-8').read(), p, tiefe + 1,
                                     gesehen):
                    gefunden.add(f'{x} (ueber {m}.py)')
    return sorted(gefunden)


def _hat_guard(quelle):
    """Hat das Modul einen `if __name__ == "__main__"`-Guard? Per AST.

    Die erste Fassung war `'__main__' not in quelle`, also ein Substring ueber Kommentare
    und Docstrings: Ein `gen_*.py`, dessen Docstring "braucht noch einen __main__-Guard"
    sagt, galt als geguardet -- und das Melden des fehlenden Guards ist der Zweck dieser
    Pruefung (R27). Dieselbe Klasse, die zwei Runden vorher fuer §A8 und §A3 geschlossen
    wurde, 110 Zeilen ueber einer AST-Pruefung.
    """
    import ast
    try:
        baum = ast.parse(quelle)
    except SyntaxError:
        return False
    return any(isinstance(k, ast.If) and '__main__' in ast.dump(k.test)
               for k in baum.body)


def _laeuft_beim_import(quelle):
    """Tut dieses Modul beim Import schon etwas? Per AST.

    Ein Aufruf auf Modulebene (ausserhalb von def/class) laeuft beim Import mit. Genau
    das ist der Unterschied zwischen einer Bibliothek und einem Schreiber ohne Guard --
    und `sync_new_products.py` war das Zweite, wurde aber als Erstes ausgeschlossen (R26).

    R27 hat zwei Loecher und einen Fehlalarm gezeigt: ein `Assign`, dessen Wert ein
    LOKALER Schreiber ist; ein `if` auf Modulebene mit einem Aufruf darin; und jedes
    `try:` zaehlte mit, womit eine echte Bibliothek mit `try: import x` als "schreibt ohne
    Guard" gemeldet wurde.
    """
    import ast
    try:
        baum = ast.parse(quelle)
    except SyntaxError:
        return True     # nicht entscheidbar -> nicht als Bibliothek durchwinken
    for knoten in baum.body:
        if isinstance(knoten, ast.Expr) and isinstance(knoten.value, ast.Call):
            return True
        if isinstance(knoten, (ast.For, ast.While, ast.With)):
            return True
        if isinstance(knoten, ast.Try):
            for _k in knoten.body:
                if isinstance(_k, ast.Expr) and isinstance(_k.value, ast.Call):
                    return True
                if isinstance(_k, (ast.For, ast.While, ast.With)):
                    return True
        if isinstance(knoten, ast.If) and '__main__' not in ast.dump(knoten.test):
            for _k in ast.walk(knoten):
                if isinstance(_k, ast.Expr) and isinstance(_k.value, ast.Call):
                    return True
        if isinstance(knoten, ast.Assign) and isinstance(knoten.value, ast.Call):
            _n = _aufrufname(knoten.value.func)
            if _n in ('open',) or _n.startswith(('os.', 'shutil.', 'subprocess.')) \
                    or re.match(r'^(?:sync|gen|write|schreib)', _n):
                return True
    return False


def _ist_lokal(name):
    return os.path.exists(os.path.join(ROOT, 'scripts', name + '.py'))


def _aufrufname(knoten):
    import ast
    if isinstance(knoten, ast.Name):
        return knoten.id
    if isinstance(knoten, ast.Attribute):
        return _aufrufname(knoten.value) + '.' + knoten.attr
    return ''


def kandidaten():
    """Die zu pruefenden Schreiber, plus die Begruendung je Ausschluss."""
    aus, raus, ohne_guard = [], [], []
    for p in sorted(glob.glob(os.path.join(ROOT, 'scripts', '*.py'))):
        name = os.path.basename(p)
        quelle = open(p, encoding='utf-8').read()
        if not _schreiber(name):
            continue
        # Ein Schreiber ohne __main__-Guard ist keine Bibliothek, sondern ein
        # Schreiber ohne Guard -- und genau diese Klasse hat das Repo am 30.09. schon
        # einmal getroffen (gen_longtail.py). Die erste Fassung hat ihn mit falscher
        # Begruendung ausgeschlossen (R26: sync_new_products.py schreibt auf Top-Level).
        # Er wird jetzt GEPRUEFT und der fehlende Guard gemeldet.
        if not _hat_guard(quelle):
            if _laeuft_beim_import(quelle):
                ohne_guard.append(name)
            else:
                raus.append((name, 'Bibliothek, tut beim Import nichts'))
                continue
        netz = _netzmodule(quelle, p)
        if netz:
            raus.append((name, f'wirkt nach aussen ({", ".join(netz)})'))
            continue
        aus.append(name)
    return aus, raus, ohne_guard


def ausserhalb():
    """Die Skripte, die ausfuehrbar sind, aber NICHT unter die Vorschrift fallen.

    Hier stand bis R30 eine getippte Liste mit fuenf Namen, und sie war in beide
    Richtungen falsch. Die Menge ist ableitbar -- ausfuehrbar heisst `__main__`-Guard,
    ausserhalb heisst `_schreiber()` ist falsch -- also wird sie abgeleitet. Ausgegeben
    wird dazu der Weg nach aussen je Name, damit der Satz "das sind alles harmlose
    Pruefer" nicht noch einmal ungeprueft daneben stehen kann.
    """
    aus = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'scripts', '*.py'))):
        name = os.path.basename(p)
        if _schreiber(name):
            continue
        quelle = open(p, encoding='utf-8').read()
        if not _hat_guard(quelle):
            continue
        aus.append((name, _netzmodule(quelle, p)))
    return aus


def baumhash(ordner):
    h = hashlib.sha256()
    for wurzel, _, dateien in sorted(os.walk(ordner)):
        if any(x in wurzel for x in ('/.git', '/node_modules', '/brain', '__pycache__')):
            continue
        for f in sorted(dateien):
            p = os.path.join(wurzel, f)
            h.update(os.path.relpath(p, ordner).encode())
            with open(p, 'rb') as fh:
                h.update(fh.read())
    return h.hexdigest()[:12]


def main():
    nur = sys.argv[sys.argv.index('--nur') + 1] if '--nur' in sys.argv else None
    rumpf = tempfile.mkdtemp(prefix='spc-idem-')
    befunde, n = [], 0
    try:
        liste, raus, ohne_guard = kandidaten()
        for _name, _grund in raus:
            print(f'    uebersprungen: {_name:26s} {_grund}')
        for _name in ohne_guard:
            print(f'    HINWEIS: {_name} schreibt ohne `if __name__ == "__main__"`-Guard '
                  f'— beim Import laeuft es mit')
            befunde.append(f'{_name}: schreibt ohne __main__-Guard')
        for name in liste:
            if nur and not name.startswith(nur):
                continue
            arbeit = os.path.join(rumpf, name)
            shutil.copytree(ROOT, arbeit,
                            ignore=shutil.ignore_patterns('.git', 'node_modules', 'brain',
                                                          '__pycache__'))
            vor = baumhash(arbeit)
            hs, exits = [], []
            for _ in range(3):
                r = subprocess.run(['python3', 'scripts/' + name] + ARGUMENTE.get(name, []),
                                   cwd=arbeit, capture_output=True, text=True, timeout=600)
                exits.append(r.returncode)
                hs.append(baumhash(arbeit))
            idem = len(set(hs)) == 1
            stabil = hs[0] == vor
            if any(exits):
                befunde.append(f'{name}: exit {exits}')
            if not idem:
                befunde.append(f'{name}: NICHT idempotent ({hs})')
            if not stabil:
                befunde.append(f'{name}: der committete Stand ist NICHT die Ausgabe '
                               f'(vor {vor}, nach {hs[0]})')
            print(f'{"ok " if idem and stabil and not any(exits) else ">>>"} '
                  f'{name:26s} idempotent={idem} baumstabil={stabil} exits={exits}')
            shutil.rmtree(arbeit, ignore_errors=True)
            n += 1
        print(f'\n{n} Skripte geprueft (Vorschrift: scripts/gen_*.py, scripts/sync_*.py '
              f'und bump_asset_version.py, die beim Lauf Dateien schreiben und keinen Weg '
              f'nach aussen haben), {len(befunde)} Befund(e)')
        for b in befunde:
            print(f'  {b}')
        _aussen = ausserhalb()
        print(f'\nAusserhalb der Vorschrift liegen {len(_aussen)} ausfuehrbare Skripte '
              f'(`__main__`, aber nicht `gen_*`/`sync_*`). Sie werden NICHT dreimal '
              f'gestartet:')
        for _name, _netz in _aussen:
            print(f'  {_name:22s} {", ".join(_netz) if _netz else "kein Weg nach aussen"}')
        return 1 if befunde else 0
    finally:
        shutil.rmtree(rumpf, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
