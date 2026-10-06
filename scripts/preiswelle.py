#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""preiswelle.py — zieht geaenderte Produktwerte in den Fliesstext nach.

Warum es dieses Skript gibt
---------------------------
Beim Vollabgleich am 06.10.2026 haben sich 12 Preise und 29 Bewertungen geaendert.
Die Generatoren haben Karten, Schemas und Detailseiten sofort nachgezogen -- den
REDAKTIONELLEN TEXT kann keiner von ihnen anfassen. `audit_prosa.py` hat danach
418 veraltete Stellen gemeldet, und es gab kein Werkzeug, sie zu schreiben:
`sync_product_values.py --rename` ersetzt nur vollstaendige Bewertungs-Strings der
Form "4,2 (1.953)", im Text steht aber "4,2 von 5 Sternen aus 1.953 Bewertungen".

Das ist der Grund, warum der preis-loop zweieinhalb Monate stillstand: Die Datenpflege
war billig, das Nachziehen der Prosa war Handarbeit in dreistelliger Zahl.

Warum eine Ersetzung ohne Zuordnung falsch waere
------------------------------------------------
Ein globales Suchen-und-Ersetzen auf "50 €" trifft auch "Controller unter 50 €" -- eine
Budget-Schwelle, die nichts mit dem EasySMX M15 zu tun hat. Gemessen: 10 der 30
geaenderten Werte sind gleichzeitig der AKTUELLE Wert eines anderen Produkts
(der alte Preis des Ultimate 2C ist heute der Preis des MGP-BT2).

Deshalb wird jede Fundstelle ZUGEORDNET, bevor sie geschrieben wird, und zwar mit
derselben Regel, mit der `audit_prosa.py` prueft: `naechstes_produkt()` nimmt den
Produktnamen, der am dichtesten davor steht. Stimmt er nicht mit dem Produkt ueberein,
dessen alter Wert dort steht, wird NICHT geschrieben, sondern berichtet. Getrennte
Muster fuer Pruefer und Schreiber sind in diesem Repo zweimal auseinandergelaufen
(siehe sync_product_values.py) -- hier gibt es nur eins, importiert.

Die Tabelle wird nicht gepflegt, sondern abgeleitet: products.json im Arbeitsbaum gegen
products.json in HEAD. Nach dem Commit ist sie leer und das Skript ein No-Op. Damit kann
es nicht gegen eine veraltete Eingabe laufen.

Aufruf:
  python3 scripts/preiswelle.py --check    nur berichten
  python3 scripts/preiswelle.py            schreiben
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit_prosa as ap   # noqa: E402  -- EINE Zuordnungsregel, dieselbe wie im Audit

CHECK = '--check' in sys.argv


def _bew(p):
    for k, v in (p.get('specs') or []):
        if k == 'Bew.':
            m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', str(v))
            return (m.group(1), m.group(2)) if m else (None, None)
    return (None, None)


def _preis(p):
    m = re.search(r'(\d+)', str(p.get('price') or '').replace('.', ''))
    return m.group(1) if m else None


def tabelle():
    """{slug: {art: [alt, neu]}} aus dem Unterschied zu HEAD."""
    roh = subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:assets/data/products.json'],
                         capture_output=True, text=True)
    if roh.returncode != 0:
        raise SystemExit('preiswelle: products.json aus HEAD nicht lesbar — '
                         'ohne den Vorzustand gibt es keine alten Werte')
    vorher = {p['slug']: p for p in json.loads(roh.stdout)}
    jetzt = json.load(open(os.path.join(ROOT, 'assets/data/products.json'),
                           encoding='utf-8'))
    aus = {}
    for p in jetzt:
        a = vorher.get(p['slug'])
        if not a:
            continue          # neues Produkt, hat keinen alten Wert im Text
        paare = {}
        if _preis(a) != _preis(p) and _preis(a) and _preis(p):
            paare['preis'] = [_preis(a), _preis(p)]
        sa, ca = _bew(a)
        sn, cn = _bew(p)
        if sa and sn and sa != sn:
            paare['sterne'] = [sa, sn]
        if ca and cn and ca != cn:
            paare['anzahl'] = [ca, cn]
        if paare:
            aus[p['slug']] = paare
    return aus


# Die Einheit MUSS am Wert stehen. Ohne sie waere "45" in "45 Grad" oder in einer ASIN
# ein Treffer. Die Formen sind aus dem Bestand abgelesen, nicht erfunden:
#   Preis   "80 €" · "32 Euro" · "(ca. 63 €," · "ab 50 €"
#   Sterne  "4,2 von 5 Sternen" · "4,1 von 5)" · "3,5 Sterne" · "4,4/5"
#   Anzahl  "aus 706 Bewertungen" · "erst 57 Bewertungen" · "1.953 Rezensionen"
EINHEIT = {
    'preis': r'\s{0,2}(?:€|Euro\b)',
    'sterne': r'\s{0,2}(?:von\s*5|Sterne|/\s*5)',
    'anzahl': r'\s{0,2}(?:Bewertungen|Bewertung\b|Rezensionen)',
}


def _muster(art, wert):
    """Der alte Wert als eigenstaendige Zahl, mit Einheit dahinter.

    Die Zifferngrenzen sind nicht Kosmetik: ohne sie trifft "88 €" in "188 €" und
    "4,4" in "14,4". Genau diese Klasse hat am 04.10. fuenf Gates gleichzeitig
    unterlaufen (siehe Protokoll B10).
    """
    if art == 'anzahl':
        # Tausenderpunkt optional, der Text schreibt "1.953" und "1953"
        kern = re.escape(wert).replace(r'\.', r'\.?')
    else:
        kern = re.escape(wert).replace(',', '[.,]')
    return re.compile(r'(?<![\d.,])' + kern + r'(?![\d.,])' + EINHEIT[art])


def _ersatz(art, alt, neu, treffer):
    """Der neue Text fuer eine Fundstelle, in der SCHREIBWEISE der alten.

    "1.953" wird "1.977", "1953" wird "1977" -- der Tausenderpunkt bleibt so, wie die
    Seite ihn setzt. Ebenso das Dezimalzeichen bei Sternen: "4.1" bleibt "4.2".
    """
    gefunden = treffer.group(0)
    zahl = re.match(r'[\d.,]+', gefunden).group(0)
    rest = gefunden[len(zahl):]
    if art == 'anzahl':
        return (neu if '.' in zahl else neu.replace('.', '')) + rest
    if ',' in zahl:
        return neu + rest
    return neu.replace(',', '.') + rest


def seiten():
    return ap.seiten()


def _produkt_danach(text, ende, weite=70):
    """Das Produkt, dessen Name am dichtesten NACH der Fundstelle steht.

    Spiegelbild zu `ap.naechstes_produkt()`. Ohne diese Richtung bleibt jede Stelle
    unzugeordnet, an der der Wert vor dem Namen steht -- "ab 45 € (GameSir X5 Lite)"
    oder eine Tabellenzeile "88 € Razer Kishi V3". `audit_prosa.py` kennt denselben
    Fall und nennt ihn in der Meldung "(Wert vor dem Namen)"; die Weite ist enger als
    die 140 davor, weil nach dem Wert der naechste Satz schon ueber das naechste
    Produkt sprechen kann.
    """
    fenster = text[ende:ende + weite]
    bester, pos = None, len(fenster) + 1
    for n in ap.NAMEN:
        i = fenster.find(n)
        if 0 <= i < pos:
            bester, pos = ap.ALIAS[n], i
    return ap.bySlug.get(bester) if bester else None


def _norm(zahl, art):
    """Eine im Text gefundene Zahl in der Schreibweise des Datenkerns.

    Der Text schreibt "1953" oder "1.953", "4.2" oder "4,2"; products.json fuehrt
    "1.953" und "4,2". Ohne diese Normalisierung vergleicht der Abgleich unten
    Schreibweisen statt Werte und erklaert jede zweite Stelle fuer veraltet.
    """
    if art == 'anzahl':
        n = zahl.replace('.', '')
        return f'{int(n):,}'.replace(',', '.') if n.isdigit() else zahl
    return zahl.replace('.', ',')


def _wert_von(p, art):
    """Der heutige Wert dieses Produkts in der Art, wie der Text ihn schreibt."""
    if art == 'preis':
        return _preis(p)
    return _bew(p)[0] if art == 'sterne' else _bew(p)[1]


_GC_SCHLUESSEL = re.compile(r'^"([a-z0-9-]+)":\s*dict\(', re.M)


def _seiten_eigner(f, text, start):
    """Das Produkt, dem die Stelle KRAFT IHRES ORTES gehoert, oder None.

    Zwei Orte haben einen eindeutigen Besitzer, auch wenn in der Naehe kein Name steht:

      · Eine Produkt- oder Review-Seite. Im Urteilstext steht der Preis ohne Namen
        ("Starker Allrounder für 46 €"), und in der Redaktions-Score-Zeile steht die
        Bewertung 200 Zeilen vom Namen entfernt. `audit_prosa.pruefe_detailpreise()`
        benennt diesen Fall ausdruecklich: „Auf einer Produktseite ist der Bezug
        eindeutig."
      · `scripts/gen_content.py`. Die Datei ist nach Slug gegliedert ("ozkak-6finger":
        dict(...)), der Besitzer ist also der zuletzt geoeffnete Block. Ohne diese Regel
        blieb die Haelfte aller Prosa-Werte der Site unerreichbar, weil der Quelltext
        den Produktnamen gar nicht wiederholt.

    Diese Regel greift NUR, wenn in der Naehe ueberhaupt kein Produktname steht --
    sonst gewinnt der Name. Ein Vergleichssatz auf der eigenen Seite ("der Kishi V3
    kostet 78 €") wird dadurch nicht dem Seitenprodukt zugeschlagen.
    """
    rel = f.replace(os.sep, '/')
    if rel.endswith('scripts/gen_content.py') or rel == 'scripts/gen_content.py':
        treffer = [m for m in _GC_SCHLUESSEL.finditer(text) if m.start() < start]
        return ap.bySlug.get(treffer[-1].group(1)) if treffer else None
    ordner = os.path.dirname(rel)
    for p in ap.items:
        d = (p.get('detail') or '').strip('/')
        if d and d == ordner:
            return p
    return None


def eigner(text, start, ende, f=None):
    """Das Produkt, dem ein Wert an dieser Stelle gehoert, oder None.

    Dieselbe Regel wie im Audit: der naechste Produktname davor; nur wenn davor keiner
    steht, der naechste dahinter. Die Reihenfolge ist nicht beliebig -- "Der G8 Galileo
    kostet 68 €, der Kishi V3 kostet mehr" hat vor dem Wert den richtigen und dahinter
    den falschen Namen. Steht in der Naehe gar kein Name, entscheidet der Ort.
    """
    return (ap.naechstes_produkt(text, start)
            or _produkt_danach(text, ende)
            or (_seiten_eigner(f, text, start) if f else None))


def lauf():
    tab = tabelle()
    items = ap.items
    # Welche alten Werte sind heute der Wert eines ANDEREN Produkts? Nur fuer die
    # Berichtszeile -- geschrieben wird ohnehin nur mit Zuordnung.
    aktuell = {'preis': {_preis(p) for p in items},
               'sterne': {_bew(p)[0] for p in items},
               'anzahl': {_bew(p)[1] for p in items}}

    geschrieben, offen = {}, []
    stimmt = gedeckt = 0   # richtig abgelehnt / nicht beweisbar, siehe unten
    for f in seiten():
        roh = open(f, encoding='utf-8').read()
        # Zuordnung auf dem MASKIERTEN Text, damit Tags und URLs den Bezug nicht
        # vortaeuschen -- genau wie im Audit. maskiere_tags() ersetzt laengentreu,
        # Offsets gelten also auch im Rohtext. maskiere_urls() wird hier NICHT
        # benutzt: es ersetzt eine URL durch EIN Zeichen und verschiebt damit alles
        # dahinter (sein Docstring behauptet das Gegenteil; das ist ein eigener Befund).
        # Reihenfolge: Kommentare ZUERST, auf dem Rohtext. Andersherum zerstoert
        # maskiere_tags() die Python-String-Literale, tokenize scheitert, und die
        # ganze Datei faellt aus -- siehe den Docstring von maskiere_kommentare().
        try:
            masked = ap.maskiere_tags(ap.maskiere_kommentare(roh, f))
        except ap.NichtLesbar as e:
            offen.append((f, 1, 'Quelle', 'nicht parsebar', str(e), '', '', ''))
            continue
        assert len(masked) == len(roh)
        # Erst JEDE Fundstelle einmal sammeln, dann je Stelle EINMAL entscheiden.
        # Die erste Fassung hat pro Regel entschieden und jede Regel, die eine Stelle
        # korrekt NICHT beansprucht, als "ohne Zuordnung" gemeldet: 512 Meldungen,
        # von denen 500 Artefakte waren. Eine Stelle ist offen, wenn KEINE Regel sie
        # beansprucht -- nicht, wenn eine einzelne es nicht tut.
        stellen = {}
        for slug, paare in tab.items():
            if slug not in ap.bySlug:
                continue
            for art, (alt, neu) in paare.items():
                for m in _muster(art, alt).finditer(masked):
                    stellen.setdefault((m.start(), m.end()), []).append(
                        (slug, art, alt, neu, m))
        plan = []
        for (anfang, ende), bewerber in sorted(stellen.items()):
            wem = eigner(masked, anfang, ende, f)
            treffer = [b for b in bewerber if wem is not None and b[0] == wem['slug']]
            if len(treffer) == 1:
                slug, art, alt, neu, m = treffer[0]
                plan.append((anfang, ende, _ersatz(art, alt, neu, m), slug, art))
            elif len(treffer) > 1:
                # Zwei Werte DESSELBEN Produkts passen auf dieselbe Stelle (etwa Preis
                # und Bewertungszahl mit gleicher Ziffernfolge). Raten verboten.
                offen.append((f, masked[:anfang].count('\n') + 1, 'mehrdeutig',
                              '/'.join(b[1] for b in treffer), masked[anfang:ende], '?',
                              wem['slug'],
                              re.sub(r'\s+', ' ', masked[max(0, anfang - 80):ende + 40])))
            else:
                slug, art, alt, neu, _m = bewerber[0]
                wert = masked[anfang:ende]
                zahl = re.match(r'[\d.,]+', wert).group(0)
                # Eine abgelehnte Stelle ist nicht automatisch ein offener Punkt. Drei
                # Faelle, und nur der dritte braucht eine Entscheidung:
                #
                # 1 Der Wert gehoert einem Produkt, dessen AKTUELLER Wert er ist.
                #   "40 €" neben dem ShanWan (heute 40 €) ist richtig, auch wenn 40 €
                #   gestern der Preis des Trust GXT war. Richtig abgelehnt, still.
                # 2 Kein Produktname in der Naehe, aber der Wert ist irgendwo im
                #   Sortiment aktuell. Das sind Budget-Schwellen ("unter 50 €") und
                #   Aufzaehlungen. Hier kann dieses Skript nichts beweisen; zustaendig
                #   ist audit_prosa.py, das solche Stellen als Seitenwert prueft.
                # 3 Alles andere: der Wert ist NIRGENDS aktuell. Dann ist er veraltet
                #   und muss von Hand entschieden werden.
                if wem is not None and _wert_von(wem, art) == _norm(zahl, art):
                    stimmt += 1
                elif wem is None and _norm(zahl, art) in aktuell[art]:
                    gedeckt += 1
                else:
                    offen.append((f, masked[:anfang].count('\n') + 1, slug, art, alt, neu,
                                  (wem or {}).get('slug') or '(kein Produktname in der Naehe)',
                                  re.sub(r'\s+', ' ', masked[max(0, anfang - 80):ende + 40])))
        if not plan:
            continue
        # Zwei Regeln duerfen nicht dieselbe Stelle beanspruchen. Passiert es, ist die
        # Tabelle widerspruechlich und das Schreiben waere geraten.
        plan.sort()
        for (a1, e1, *_), (a2, *_rest) in zip(plan, plan[1:]):
            if a2 < e1:
                raise SystemExit(f'preiswelle: {f} — zwei Regeln beanspruchen dieselbe '
                                 f'Stelle ({a1}..{e1} und ab {a2}); die Tabelle ist '
                                 f'widerspruechlich, es wird nichts geschrieben')
        neu_text = roh
        for anfang, ende, ersatz, slug, art in reversed(plan):
            neu_text = neu_text[:anfang] + ersatz + neu_text[ende:]
            geschrieben.setdefault((slug, art), 0)
            geschrieben[(slug, art)] += 1
        if not CHECK:
            open(f, 'w', encoding='utf-8').write(neu_text)

    print(f'{len(tab)} Produkt(e) mit geaenderten Werten gegenueber HEAD')
    for (slug, art), n in sorted(geschrieben.items()):
        alt, neu = tab[slug][art]
        kollision = ' (Wert kollidiert, nur mit Zuordnung geschrieben)' \
            if alt in aktuell[art] else ''
        print(f'  {slug:28s} {art:7s} {alt:>7s} -> {neu:<7s} {n:3d} Stelle(n)'
              f'{kollision}')
    print(f'\n{sum(geschrieben.values())} Stelle(n) '
          f'{"zu schreiben" if CHECK else "geschrieben"} · {stimmt} richtig abgelehnt '
          f'(Wert gehoert dem Produkt, das danebensteht) · {gedeckt} ohne Produktbezug, '
          f'Wert im Sortiment aktuell (zustaendig: audit_prosa.py) · {len(offen)} offen')
    if offen:
        print('\nOhne Zuordnung — jede einzeln entscheiden, NICHT blind ersetzen:')
        for f, z, slug, art, alt, neu, wem, ctx in offen:
            print(f'  ? {f}:{z}  {alt} ({art}, alt bei {slug}) steht bei {wem}')
            if '--text' in sys.argv:
                print(f'      …{ctx}…')
    return 1 if offen else 0


if __name__ == '__main__':
    sys.exit(lauf())
