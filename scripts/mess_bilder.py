#!/usr/bin/env python3
"""Misst die echten Pixelmasse aller im Repo eingebundenen Bilder.

Hintergrund: width/height an <img> werden von Hand getippt und veralten still,
wenn die Bildquelle wechselt. Am 30.09.2026 standen an vier Amazon-Bildern die
Masse der frueher dort liegenden lokalen Pressebilder (z.B. 1920x700 an einem
1500x1500-Banner) -- schlechtes CLS und eine Falschangabe im Markup.

Dieses Script schreibt die gemessenen Masse nach assets/data/bildmasse.json.
verify.py prueft jedes deklarierte width/height-Paar gegen diese Datei und
meldet Abweichungen sowie fehlende Eintraege. Damit bleibt verify.py offline
lauffaehig und die Masse trotzdem belegt.

Aufruf:  python3 scripts/mess_bilder.py          (nur fehlende messen)
         python3 scripts/mess_bilder.py --alle   (alles neu messen)
         python3 scripts/mess_bilder.py --check  (Belegstand gegen die Wirklichkeit)

--check ist noetig, weil verify.py offline laufen muss: Es beweist dort nur
"HTML passt zu bildmasse.json", nie "bildmasse.json passt zu den echten Bildern".
Ohne diesen Modus waere die Belegdatei ein unbelegter Beleg -- dieselbe Form wie der
Generator-Abgleich, der anfangs nur Datei == Generator bewies und nie
Generator == products.json.
"""
import glob
import json
import os
import re
import struct
import subprocess
import sys
import urllib.request

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KARTE = os.path.join(WURZEL, 'assets', 'data', 'bildmasse.json')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' \
     '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'


def bildquellen():
    """Alle src-Werte von <img>-Tags, die width UND height deklarieren."""
    gefunden = set()
    for f in glob.glob(os.path.join(WURZEL, '**', '*.html'), recursive=True):
        rel = os.path.relpath(f, WURZEL)
        if rel.startswith(('brain' + os.sep, 'node_modules' + os.sep)):
            continue
        for tag in re.findall(r'<img[^>]*>', open(f, encoding='utf-8').read()):
            if not (re.search(r'\bwidth="\d+"', tag) and re.search(r'\bheight="\d+"', tag)):
                continue
            m = re.search(r'src="([^"]+)"', tag)
            if m:
                gefunden.add(m.group(1))
    return sorted(gefunden)


def masse_aus_bytes(daten):
    """Breite/Hoehe aus den Kopfbytes lesen: PNG, GIF, JPEG, WebP."""
    if daten[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', daten[16:24])
    if daten[:6] in (b'GIF87a', b'GIF89a'):
        return struct.unpack('<HH', daten[6:10])
    if daten[:4] == b'RIFF' and daten[8:12] == b'WEBP':
        if daten[12:16] == b'VP8X':
            b = daten[24:30]
            return (1 + int.from_bytes(b[0:3], 'little'),
                    1 + int.from_bytes(b[3:6], 'little'))
        if daten[12:16] == b'VP8 ':
            return struct.unpack('<HH', daten[26:30])
        if daten[12:16] == b'VP8L':
            b = int.from_bytes(daten[21:25], 'little')
            return (1 + (b & 0x3FFF), 1 + ((b >> 14) & 0x3FFF))
        return None
    if daten[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(daten):
            if daten[i] != 0xFF:
                i += 1
                continue
            marker = daten[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            laenge = int.from_bytes(daten[i + 2:i + 4], 'big')
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack('>HH', daten[i + 5:i + 9])
                return (w, h)
            i += 2 + laenge
    return None


def miss(src):
    if src.startswith('http'):
        req = urllib.request.Request(src, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            return masse_aus_bytes(r.read())
    pfad = os.path.join(WURZEL, src.lstrip('/'))
    if not os.path.exists(pfad):
        return None
    with open(pfad, 'rb') as fh:
        masse = masse_aus_bytes(fh.read())
    if masse:
        return masse
    # SVG und Exoten: macOS sips als Rueckfallebene
    try:
        aus = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', pfad],
                             capture_output=True, text=True, timeout=20).stdout
        w = re.search(r'pixelWidth:\s*(\d+)', aus)
        h = re.search(r'pixelHeight:\s*(\d+)', aus)
        if w and h:
            return (int(w.group(1)), int(h.group(1)))
    except Exception:
        pass
    return None


def pruefe():
    """Jeden Eintrag neu messen und gegen den Belegstand halten."""
    if not os.path.exists(KARTE):
        print(f'FEHLER: {KARTE} fehlt')
        return 1
    karte = json.load(open(KARTE, encoding='utf-8'))
    quellen = bildquellen()
    fehler = 0
    for src in sorted(set(quellen) | set(karte)):
        if src not in karte:
            print(f'  FEHLT im Beleg: {src}')
            fehler += 1
            continue
        if src not in quellen:
            print(f'  verwaist (nirgends mit Massangabe eingebunden): {src}')
            fehler += 1
            continue
        try:
            masse = miss(src)
        except Exception as e:
            print(f'  NICHT MESSBAR {src}: {e}')
            fehler += 1
            continue
        if not masse:
            print(f'  NICHT MESSBAR {src}')
            fehler += 1
        elif list(masse) != karte[src]:
            print(f'  ABWEICHUNG {src}: Beleg {karte[src][0]}x{karte[src][1]}, '
                  f'gemessen {masse[0]}x{masse[1]}')
            fehler += 1
    print(f'\n{len(karte)} Eintraege geprueft, {fehler} Abweichung(en)')
    return 1 if fehler else 0


def main():
    if '--check' in sys.argv:
        return pruefe()
    alle_neu = '--alle' in sys.argv
    karte = {}
    if os.path.exists(KARTE) and not alle_neu:
        karte = json.load(open(KARTE, encoding='utf-8'))
    quellen = bildquellen()
    neu = fehler = 0
    for src in quellen:
        if src in karte and not alle_neu:
            continue
        try:
            masse = miss(src)
        except Exception as e:
            print(f'  FEHLER {src}: {e}')
            fehler += 1
            continue
        if not masse:
            print(f'  ungemessen {src}')
            fehler += 1
            continue
        karte[src] = list(masse)
        neu += 1
        print(f'  {masse[0]}x{masse[1]}  {src}')
    # Eintraege wegwerfen, deren Bild nirgends mehr mit Massangabe steht
    verwaist = [k for k in karte if k not in quellen]
    for k in verwaist:
        del karte[k]
        print(f'  entfernt (nicht mehr eingebunden) {k}')
    json.dump(karte, open(KARTE, 'w', encoding='utf-8'),
              indent=2, ensure_ascii=False, sort_keys=True)
    print(f'\n{len(karte)} Bilder in bildmasse.json '
          f'({neu} neu gemessen, {len(verwaist)} entfernt, {fehler} Fehler)')
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())
