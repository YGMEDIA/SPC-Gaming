#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rundreise-Probe: Jede Vergleichsseite mit Rahmenfeldern muss sich aus ihrer Definition
NEU erzeugen lassen -- zeichengleich (bis auf die Asset-Version, die bump_asset_version.py
nachsetzt) und mit 0 Befunden, beim Schreiblauf und beim Nachlauf.

Warum es diese Probe gibt: Ein Pruefdurchgang hat sie erfunden und damit zwei Defekte
gefunden, die kein Gate sah -- eine doppelte Ueberschrift und eine lokale CSS-Dublette,
beide nur im Pfad, der eine NEUE Seite anlegt. Dieser Pfad laeuft im Alltag nie, weil die
sieben Seiten existieren. Also prueft ihn eine Probe.
"""
import io, os, re, shutil, subprocess, sys, tempfile, importlib.util, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
    if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'scripts' else os.getcwd()
os.chdir(ROOT)

spiegel = tempfile.mkdtemp(prefix='rundreise-')
for n in ('scripts', 'assets', 'vergleich', 'controller', 'produkte', 'marken', 'blog'):
    if os.path.isdir(n):
        shutil.copytree(n, os.path.join(spiegel, n))
for n in ('index.html', 'sitemap.xml', 'CNAME', '.nojekyll', '404.html', 'llms.txt'):
    if os.path.exists(n):
        shutil.copy2(n, spiegel)

spec = importlib.util.spec_from_file_location('gv', 'scripts/gen_vergleich.py')
mod = importlib.util.module_from_spec(spec)
sys.argv = ['gv', '--check']
spec.loader.exec_module(mod)
MIT_RAHMEN = [v for v in mod.VERGLEICHE if 'titel' in v]
norm = lambda s: re.sub(r'\?v=[0-9a-f]+', '', s)

def lauf(*args):
    r = subprocess.run([sys.executable, 'scripts/gen_vergleich.py', *args],
                       cwd=spiegel, capture_output=True, text=True)
    m = re.search(r'(\d+) Befund\(e\)', r.stdout + r.stderr)
    return int(m.group(1)) if m else -1

falsch = 0
for v in MIT_RAHMEN:
    ziel = os.path.join(spiegel, v['datei'])
    orig = io.open(ziel, encoding='utf-8').read()
    os.remove(ziel)
    nb, nb2 = lauf(), lauf('--check')
    neu = io.open(ziel, encoding='utf-8').read()
    gleich = norm(neu) == norm(orig)
    ok = nb == 0 and nb2 == 0 and gleich
    falsch += (not ok)
    print(f"{'ok ' if ok else '>>>'} {v['datei'].split('/')[1][:28]:30} "
          f"Neuanlage {nb} Befund(e) · Nachlauf {nb2} · zeichengleich {gleich}")
    if not gleich:
        for l in [x for x in difflib.unified_diff(norm(orig).split('\n'),
                                                  norm(neu).split('\n'), lineterm='')
                  if x[:1] in '+-'][:8]:
            print('      ', l[:116])

shutil.rmtree(spiegel)
print(f"\n{len(MIT_RAHMEN)} Seiten mit Rahmenfeldern geprueft, {falsch} falsch "
      f"(Vorschrift: loeschen, neu erzeugen, gegen den Repo-Stand diffen; "
      f"Asset-Version normalisiert)")
sys.exit(1 if falsch else 0)
