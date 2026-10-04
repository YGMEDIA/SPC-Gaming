#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Messvorschrift hinter "die Bestenlisten-Gates greifen" (B6).

Warum als Skript und nicht als Satz in STATUS: Weil "das Gate greift" in diesem Repo
schon mehrfach gestimmt hat und trotzdem falsch war -- ein Gate, das NUR rot wird, kann
die falsche Regel haben. Der zwanzigste bis fuenfundzwanzigste Pruefbericht haben
viermal dieselbe Klasse gebracht: ein Loch UND ein Fehlalarm aus derselben Zeile. Seither
gilt in beide Richtungen:

    jeder Defekt MUSS rot werden        (sonst geht er live)
    jedes legitime Refactoring MUSS gruen bleiben
                                        (sonst verteidigt das Gate den Fehler gegen
                                         Korrektur -- Mechanismus 6)

Geprueft werden die vier Gates, die mit B6 entstanden sind:
  · gen_bestenliste.py --check   (Seite weicht von products.json ab)
  · Sortier-Regel ausserhalb des BESTEN-Blocks
  · ItemList-Reihenfolge gegen die Karten-Reihenfolge
  · §A6-Schwelle: kein Produkt unter 3,8 Sternen auf einer Bestenliste

Jeder Fall bekommt eine FRISCHE Kopie des Repos. Ohne das messen die spaeteren Faelle
gegen den Schaden der frueheren -- genau so hat ein kontaminiertes Probe-Verzeichnis in
Runde 22 kurzzeitig geglaubt, der Finder empfehle Android-Modelle an iPhone-Nutzer.

Aufruf:  python3 scripts/besten_batterie.py
         python3 scripts/besten_batterie.py --kurz
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GESAMT = 'controller/beste/index.html'
BUDGET = 'vergleich/beste-budget-controller/index.html'
GEN = 'scripts/gen_bestenliste.py'
IPHONE = 'vergleich/beste-iphone-controller/index.html'
JSON = 'assets/data/products.json'


def _block(h):
    a, b = h.index('<!-- BESTEN:START -->'), h.index('<!-- BESTEN:END -->')
    return h[a:b]


def _erste_karte_preis(h):
    """Der Preis der ersten Karte, so wie er in der price-row steht."""
    m = re.search(r'<span class="price">(\d+) €', _block(h))
    return m.group(1) if m else None


def _tausche_erste_zwei_im_schema(h):
    """Nur die ItemList umsortieren, die Karten stehen lassen."""
    def um(m):
        e = re.findall(r'\{"@type": "ListItem".*?\}(?=, \{"@type": "ListItem"|\])', m.group(0))
        if len(e) < 2:
            return m.group(0)
        getauscht = [e[1], e[0]] + e[2:]
        # Positionen neu durchnummerieren, damit NUR die Reihenfolge der Produkte kippt
        for i, _ in enumerate(getauscht):
            getauscht[i] = re.sub(r'"position": \d+', f'"position": {i + 1}', getauscht[i])
        return m.group(0)[:m.group(0).index('[') + 1] + ', '.join(getauscht) + ']}'
    return re.sub(r'\{"@context": "https://schema\.org", "@type": "ItemList".*?\]\}',
                  um, h, flags=re.S)


# (Etikett, Datei, Mutation, Erwartung)
FAELLE = [
    # ---- Defekte: MUESSEN rot werden -------------------------------------------------
    ('Preis einer Karte von Hand geaendert', GESAMT,
     lambda h: h.replace(f'<span class="price">{_erste_karte_preis(h)} €',
                         '<span class="price">99 €', 1), 'ROT'),
    ('Bewertung in der Faktenzeile geaendert', GESAMT,
     lambda h: h.replace('4,2 Sterne</strong> aus 706', '4,9 Sterne</strong> aus 706', 1),
     'ROT'),
    ('Anzahl in der Faktenzeile geaendert', GESAMT,
     lambda h: h.replace('aus 706 Bewertungen', 'aus 7.060 Bewertungen', 1), 'ROT'),
    # Die erste Fassung ersetzte nur das OEFFNENDE Tag der zweiten Karte: Danach standen
    # 9 <article>-Oeffner gegen 10 Schliesser, und data-product blieb im Dokument. Der
    # Fall wurde rot, aber nicht an dem, was sein Etikett behauptet. Dieselbe Klasse, die
    # das Protokoll zu B5 als Lehre fuehrt.
    ('eine ganze Karte aus dem Block entfernt', GESAMT,
     lambda h: h.replace(re.search(r'<article class="pcard">.*?</article>\n',
                                   _block(h), re.S).group(0), '', 1), 'ROT'),
    ('BESTEN-Block ganz entfernt', GESAMT,
     lambda h: h[:h.index('<!-- BESTEN:START -->')]
     + h[h.index('<!-- BESTEN:END -->') + len('<!-- BESTEN:END -->'):], 'ROT'),
    ('Sortier-Regel zusaetzlich ausserhalb des Blocks', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Sortiert nach unserem Gesamt-Urteil: Preis, Sticks, '
                         'Ergonomie und Kompatibilitaet.</p>\n<!-- BESTEN:START -->', 1),
     'ROT'),
    ('ItemList aus dem Block entfernt', GESAMT,
     lambda h: re.sub(r'<script type="application/ld\+json">\{"@context": '
                      r'"https://schema\.org", "@type": "ItemList".*?</script>', '', h,
                      flags=re.S), 'ROT'),
    ('ItemList-Reihenfolge weicht von den Karten ab', GESAMT,
     _tausche_erste_zwei_im_schema, 'ROT'),
    # Zwei Faelle statt einem: Die erste Fassung ersetzte das ERSTE '"position": 2' der
    # Datei und traf damit die BreadcrumbList, nicht die ItemList -- und blieb gruen. Die
    # Luecke war nicht der Fall, sondern das fehlende Gate (verify.py prueft die Folge
    # jetzt fuer jede Liste jeder Seite). Beide Formen stehen seitdem hier.
    ('ItemList-Positionen nicht aufsteigend', GESAMT,
     lambda h: h[:h.index('<!-- BESTEN:START -->')]
     + _block(h).replace('"position": 2', '"position": 7', 1)
     + h[h.index('<!-- BESTEN:END -->'):], 'ROT'),
    ('BreadcrumbList-Positionen nicht aufsteigend', GESAMT,
     lambda h: h[:h.index('<!-- BESTEN:START -->')].replace('"position": 2',
                                                            '"position": 7', 1)
     + h[h.index('<!-- BESTEN:START -->'):], 'ROT'),
    ('numberOfItems stimmt nicht', GESAMT,
     lambda h: h.replace('"numberOfItems": 10', '"numberOfItems": 9', 1), 'ROT'),
    ('Produkt unter der §A6-Schwelle in die Liste', GEN,
     lambda q: q.replace("('backbone-pro', 'Wireless', '', ''),",
                         "('backbone-pro', 'Wireless', '', ''),\n"
                         # turtle-beach-atom: 3,5 Sterne, der einzige Controller unter
                         # der §A6-Schwelle (gemessen 04.10.2026, 1 von 28).
                         "            ('turtle-beach-atom', '', '', ''),"), 'ROT'),
    ('unbekannter Slug in der Liste', GEN,
     lambda q: q.replace("('gamesir-x2s', '', '', ''),",
                         "('gibtsnicht', '', '', ''),"), 'ROT'),
    ('Faktenzeile aus einer Karte entfernt', GESAMT,
     lambda h: re.sub(r'<p class="pcard-fakten">.*?</p>\n', '', h, count=1), 'ROT'),
    ('Budget-Liste: Preis einer Karte geaendert', BUDGET,
     lambda h: h.replace('<span class="price">45 €', '<span class="price">44 €', 1),
     'ROT'),
    ('Gleichstands-Satz zu Alleinstellung verkuerzt', IPHONE,
     lambda h: h.replace('Die beste Bewertung teilen sich zwei:',
                         'Die beste Bewertung hat allein:'), 'ROT'),
    ('Ehrlichkeits-Abschnitt entfernt', GESAMT,
     lambda h: re.sub(r'<div class="besten-ehrlich">.*?</div>', '', h, flags=re.S), 'ROT'),

    # ---- Legitim: MUSS gruen bleiben --------------------------------------------------
    ('LEGITIM unveraendert', GESAMT, lambda h: h, 'GRUEN'),
    ('LEGITIM Reihenfolge redaktionell getauscht, neu generiert', GEN,
     lambda q: q.replace("('razer-kishi-v3', 'Premium', 'badge-top', ''),\n"
                         "            ('backbone-one-2', 'iOS-Klassiker', 'badge-top', ''),",
                         "('backbone-one-2', 'iOS-Klassiker', 'badge-top', ''),\n"
                         "            ('razer-kishi-v3', 'Premium', 'badge-top', ''),"),
     'GRUEN_NACH_GENERATOR'),
    ('LEGITIM Badge umbenannt, neu generiert', GEN,
     lambda q: q.replace("'Preistipp', 'badge-budget'", "'Preis-Tipp', 'badge-budget'"),
     'GRUEN_NACH_GENERATOR'),
    # Stand hier bis zum ersten Pruefbericht als LEGITIM/GRUEN und hat damit einen Defekt
    # ZERTIFIZIERT: Nach dem Entfernen standen viermal "Top 10" ueber neun Karten.
    ('Position entfernt, Top-N-Zusage bleibt stehen', GEN,
     lambda q: q.replace("            ('gamesir-x2s', '', '', ''),\n", ''), 'ROT'),
    # Der zugehoerige GRUENE Fall. Der Kommentar oben hat ihn behauptet, bevor es ihn gab
    # -- der zweite Pruefbericht hat das gefunden: eine Probe, die in einem Kommentar
    # existiert, ist keine Probe. Hier wird die Position entfernt UND die Zusage
    # mitgezogen, in allen vier Texten der Seite.
    ('LEGITIM Position entfernt, Top-N ueberall mitgezogen', GEN,
     lambda q: q.replace("            ('gamesir-x2s', '', '', ''),\n", '')
     .replace("'topn': 10,", "'topn': 9,"), 'GRUEN_NACH_GENERATOR_UND_TEXT'),
    # Fehlalarm-Richtung des Top-N-Gates: Ein Querverweis auf die Schwesterseite traegt
    # deren Titel ("... Top 5") als LINKTEXT auf der Top-10-Seite. Die erste Fassung des
    # Gates machte das rot und haette damit B7 (interne Verlinkung) blockiert.
    ('LEGITIM Querverweis-Link mit "Top 5" auf der Top-10-Seite', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Nur Android? <a href="/vergleich/beste-android-controller/">'
                         'Beste Android Controller Top 5</a></p>\n<!-- BESTEN:START -->',
                         1), 'GRUEN'),
    ('LEGITIM "Top 3" im Fliesstext ohne Zusage', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Die Top 3 dieser Liste haben wir selbst gekauft.</p>\n'
                         '<!-- BESTEN:START -->', 1), 'GRUEN'),
    # Loch-Richtung des Sortier-Gates: der alte Handsatz OHNE "und" -- Komma-Aufzaehlung
    # derselben vier Kriterien, inklusive "Ergonomie". Die zweite Gate-Fassung liess ihn
    # durch, also genau den Befund, der B6 erzwungen hat.
    ('alter Sortier-Satz ohne "und", mit Komma-Aufzaehlung', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p class="sec-sub">Sortiert nach unserem Gesamt-Urteil: Preis, '
                         'Sticks, Ergonomie, Kompatibilitaet.</p>\n<!-- BESTEN:START -->',
                         1), 'ROT'),
    ('Sortier-Satz mit "sowie" statt "und"', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Sortiert nach Preis, Sticks sowie Kompatibilitaet.</p>\n'
                         '<!-- BESTEN:START -->', 1), 'ROT'),
    ('LEGITIM "Sortiert nach Veroeffentlichung" mit "und" im Satz', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Sortiert nach Veroeffentlichung findest du unsere Tests und '
                         'Ratgeber im Blog.</p>\n<!-- BESTEN:START -->', 1), 'GRUEN'),
    ('LEGITIM Dreier-Gleichstand, Text zieht mit', JSON,
     lambda j: j.replace('"4,2 (355)"', '"4,4 (355)"', 1),
     'GLEICHSTAND_DREI'),
    # ROT_B6 statt ROT: Diese drei Defekte liegen in products.json, und dort wird auch
    # gen_brand_sections rot -- ein Fall, der aus dem FALSCHEN Grund rot wird, beweist
    # ueber das gemeinte Gate nichts. Verlangt wird deshalb, dass gen_bestenliste --check
    # den Befund SELBST nennt.
    ('Position ohne lesbare Bewertung', JSON,
     lambda j: j.replace('"4,2 (706)"', '"keine Angabe"', 1), 'ROT_B6'),
    ('Preis unlesbar', JSON,
     lambda j: j.replace('"price": "80 €"', '"price": "auf Anfrage"', 1), 'ROT_B6'),
    ('Bew. mit Punkt statt Komma bei Platz 1', JSON,
     lambda j: j.replace('"4,2 (706)"', '"4.2 (706)"', 1), 'ROT_B6'),
    # ROT_NACH_GENERATOR: erst regenerieren, DANN muss verify rot sein. Sonst beweist der
    # Fall nur, dass die Datei vom Generator abweicht -- nicht, dass der Sprung auffaellt.
    ('Kartenebene auf h3, neu generiert (Ueberschriften-Sprung)', GEN,
     lambda q: q.replace("'kartenebene': 'h2',    # diese Seite hat keine andere h2; "
                         "h3 waere ein Sprung", "'kartenebene': 'h3',"),
     'ROT_NACH_GENERATOR'),
    ('LEGITIM Ueberschrift der Seite geaendert', GESAMT,
     lambda h: h.replace('Die Top 10 im Überblick', 'Die Rangliste im Überblick'),
     'GRUEN'),
    ('LEGITIM Absatz ausserhalb des Blocks, ohne Sortier-Satz', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Alle Preise sind UVP-Angaben.</p>\n<!-- BESTEN:START -->', 1),
     'GRUEN'),
    ('LEGITIM das Wort "sortiert" im Fliesstext', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<p>Die FAQ unten ist nach Haeufigkeit sortiert.</p>\n'
                         '<!-- BESTEN:START -->', 1), 'GRUEN'),
    ('LEGITIM Sortier-Satz im Kommentar ausserhalb', GESAMT,
     lambda h: h.replace('<!-- BESTEN:START -->',
                         '<!-- Sortiert nach: siehe Generator -->\n<!-- BESTEN:START -->',
                         1), 'GRUEN'),
]


def lauf(arbeit):
    r = subprocess.run([sys.executable, 'scripts/verify.py'], cwd=arbeit,
                       capture_output=True, text=True, timeout=300)
    aus = r.stderr + r.stdout
    if not re.search(r'(GRÜN|ROT) —', aus):
        letzte = [x for x in aus.strip().splitlines() if x.strip()]
        return 'ABBRUCH', (letzte[-1][:90] if letzte else '')
    if r.returncode == 0:
        return 'GRUEN', ''
    zeilen = [x for x in aus.splitlines() if 'FEHLER' in x]
    return 'ROT', (zeilen[0].strip()[:95] if zeilen else '')


def main():
    kurz = '--kurz' in sys.argv
    rumpf = tempfile.mkdtemp(prefix='spc-besten-')
    falsch, ungegriffen = 0, 0
    try:
        for etikett, datei, mutation, soll in FAELLE:
            arbeit = os.path.join(rumpf, re.sub(r'\W+', '_', etikett)[:40])
            shutil.copytree(ROOT, arbeit,
                            ignore=shutil.ignore_patterns('.git', 'node_modules', 'brain',
                                                      'SPC-Gaming-Visuals',
                                                          '__pycache__'))
            pfad = os.path.join(arbeit, datei)
            vorher = open(pfad, encoding='utf-8').read()
            try:
                nachher = mutation(vorher)
            except Exception as e:
                print(f'>>> {etikett}: Mutation selbst kaputt ({e})')
                falsch += 1
                shutil.rmtree(arbeit, ignore_errors=True)
                continue
            # Eine Mutation, die nicht greift, prueft NICHTS -- und sah bisher aus wie
            # ein bestandener Fall. Dieselbe Falle wie bei den Finder-Proben (R17).
            if nachher == vorher and soll != 'GRUEN':
                print(f'>>> {etikett}: Mutation hat nicht gegriffen (Datei unveraendert)')
                ungegriffen += 1
                shutil.rmtree(arbeit, ignore_errors=True)
                continue
            open(pfad, 'w', encoding='utf-8').write(nachher)

            erwartet = soll
            if soll == 'GRUEN_NACH_GENERATOR':
                # Redaktionelle Aenderung in LISTEN: Erst MUSS --check rot sein (die
                # Seite passt nicht mehr), nach dem Generatorlauf MUSS alles gruen sein.
                r1 = subprocess.run([sys.executable, 'scripts/gen_bestenliste.py',
                                     '--check'], cwd=arbeit, capture_output=True,
                                    text=True, timeout=180)
                if r1.returncode == 0:
                    print(f'>>> {etikett}: --check bleibt gruen, obwohl LISTEN geaendert '
                          f'wurde — das Gate merkt die Aenderung nicht')
                    falsch += 1
                    shutil.rmtree(arbeit, ignore_errors=True)
                    continue
                subprocess.run([sys.executable, 'scripts/gen_bestenliste.py'], cwd=arbeit,
                               capture_output=True, text=True, timeout=180)
                subprocess.run([sys.executable, 'scripts/bump_asset_version.py'],
                               cwd=arbeit, capture_output=True, text=True, timeout=180)
                erwartet = 'GRUEN'

            if soll == 'ROT_B6':
                r1 = subprocess.run([sys.executable, 'scripts/gen_bestenliste.py',
                                     '--check'], cwd=arbeit, capture_output=True,
                                    text=True, timeout=180)
                if r1.returncode == 0 or 'FEHLER' not in (r1.stdout + r1.stderr):
                    print(f'>>> {etikett}: gen_bestenliste --check meldet NICHTS '
                          f'(rc={r1.returncode}) — ein anderes Gate wuerde den Lauf rot '
                          f'machen, dieses nicht')
                    falsch += 1
                    shutil.rmtree(arbeit, ignore_errors=True)
                    continue
                erwartet = 'ROT'

            if soll == 'GRUEN_NACH_GENERATOR_UND_TEXT':
                # Zusaetzlich die vier Textstellen der Seite nachziehen, so wie ein
                # Mensch es taete. Erst DANN muss alles gruen sein.
                subprocess.run([sys.executable, 'scripts/gen_bestenliste.py'], cwd=arbeit,
                               capture_output=True, text=True, timeout=180)
                _f = os.path.join(arbeit, GESAMT)
                _s = open(_f, encoding='utf-8').read().replace('Top 10', 'Top 9')
                open(_f, 'w', encoding='utf-8').write(_s)
                subprocess.run([sys.executable, 'scripts/bump_asset_version.py'],
                               cwd=arbeit, capture_output=True, text=True, timeout=180)
                erwartet = 'GRUEN'

            if soll == 'GLEICHSTAND_DREI':
                # Drei gleichauf: Der Lauf muss gruen sein UND der Absatz darf nicht
                # mehr von "zwei" oder "beide" sprechen. Ein Gate kann Mengenwoerter
                # nicht pruefen (P-13 Mechanismus 7), also liest die Probe den Text.
                #
                # VOLLE Nachzieh-Kette, nicht nur der eine Generator: Eine geaenderte
                # Bewertung steht auch im Schema der Produktseite, in den Marken-Hubs und
                # in den Karten. Die erste Fassung dieser Probe lief nur
                # gen_bestenliste.py und wurde dann an `produkte/trust-gxt-rgb/:
                # Schema ratingValue "4.2"` rot -- ein Fall, der aus dem falschen Grund
                # rot wird, beweist nichts (dieselbe Lehre wie ROT_B6, eine Runde spaeter
                # in der anderen Richtung).
                for _s in ('sync_product_values.py', 'gen_pages.py', 'gen_hubs.py',
                           'gen_brand_sections.py', 'gen_preisfrage.py',
                           'gen_longtail.py', 'gen_bestenliste.py', 'sync_kompat.py',
                           'sync_lesezeit.py', 'bump_asset_version.py'):
                    subprocess.run([sys.executable, 'scripts/' + _s]
                                   + (['--regen'] if _s == 'gen_pages.py' else []),
                                   cwd=arbeit, capture_output=True, text=True,
                                   timeout=300)
                _ip = open(os.path.join(arbeit, IPHONE), encoding='utf-8').read()
                _abs = re.search(r'<div class="besten-ehrlich">.*?</div>', _ip, re.S)
                _txt = re.sub(r'<[^>]+>', ' ', _abs.group(0)) if _abs else ''
                if 'teilen sich drei' not in _txt or 'beide' in _txt:
                    print(f'>>> {etikett}: Dreier-Gleichstand, der Absatz sagt aber '
                          f'nicht "drei" oder noch "beide": {_txt[:150]}')
                    falsch += 1
                    shutil.rmtree(arbeit, ignore_errors=True)
                    continue
                erwartet = 'GRUEN'

            if soll == 'ROT_NACH_GENERATOR':
                subprocess.run([sys.executable, 'scripts/gen_bestenliste.py'], cwd=arbeit,
                               capture_output=True, text=True, timeout=180)
                subprocess.run([sys.executable, 'scripts/bump_asset_version.py'],
                               cwd=arbeit, capture_output=True, text=True, timeout=180)
                erwartet = 'ROT'

            art, wie = lauf(arbeit)
            ok = (art == erwartet)
            if not ok:
                falsch += 1
            if not kurz or not ok:
                print(f'{"ok " if ok else ">>>"} {art:8s} | {etikett:52s} | soll '
                      f'{erwartet:6s} | {wie}')
            shutil.rmtree(arbeit, ignore_errors=True)

        n_rot = sum(1 for f in FAELLE if f[3].startswith('ROT'))
        n_gruen = len(FAELLE) - n_rot
        print(f'\n{len(FAELLE)} Faelle ({n_rot} muessen rot werden, {n_gruen} muessen '
              f'gruen bleiben), {falsch} falsch, {ungegriffen} nicht gegriffen')
        return 1 if (falsch or ungegriffen) else 0
    finally:
        shutil.rmtree(rumpf, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
