#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_tablet_hub.py — /controller/tablet/ ausbauen (01.11.2026)

Zweiter Thin-Page-Fund aus der Messung zu GSC-Lauf 8: `/controller/tablet/` hatte
131 Woerter, waehrend seine Geschwister bei 482 (mini-gamepad) bis 1138 (android)
liegen.

Beim Bauen sind zwei aeltere Fehler aufgefallen, beide schwerer als die Wortzahl:

1. Der Hinweiskasten der Seite empfahl fuer Tablets zwei namentlich genannte
   Modelle als "Bluetooth-Standalone". Das zweite ist ein Teleskop-Clip UND die
   erste Karte derselben Seite, die Seite widersprach sich also. Beim ersten
   widerspricht sich der Datenkern (claim nennt iPad, worksOn fuehrt kein
   `tablet`) -- das ist eine offene Datenfrage, keine erledigte. Der Kasten ist
   entfernt, `verify.py` Abschnitt 7 haelt ihn repoweit draussen, und der genaue
   Wortlaut steht bewusst nur dort: Ein Gate, dessen Suchtext im geprueften Baum
   steht, meldet sich selbst.

2. `blog/controller-fuer-tablet/` behauptete live und im FAQPage-Schema, unterhalb
   des G8 Plus fuehre kein Modell eine Tablet-Angabe, und driftfreie Sticks plus
   Tablet-Freigabe verbinde "genau ein Modell". Beides ist falsch (Kishi Ultra
   63 Euro mit 8-Zoll-Angabe; Kishi V3 Pro mit TMR-Sticks). Vier Stellen
   korrigiert, drei VERBOTEN-Eintraege dagegen.

Eigenschaften (wie P-18/P-19):
  · IDEMPOTENT  — Marker-Block, bei jedem Lauf ersetzt.
  · §A1         — jede Zahl aus products.json oder aus einem benannten Beleg,
                  Drift- und Mass-Gate dagegen.
  · §A4         — ItemList aus der sichtbaren Kartenreihenfolge, FAQPage aus den
                  erzeugten details-Bloecken.
  · §A5         — zwei Eigenschaften stehen NICHT in products.json: das Laden
                  waehrend des Spielens und die Groessengrenze. Sie kommen aus
                  `LADEN` und `GROESSE`, je mit Datei und Suchtext, und der
                  Generator prueft Anwesenheit UND Umgebung des Belegs.
  · P-19        — Zahlwort, Substantiv und Verb kommen aus derselben Zahl.

Was KEIN Gate dieser Datei pruefen kann (P-19 GRENZE, beim Bau aufgelistet, damit
ein Pruefer sie in einem Durchgang findet). Sechs Saetze ohne Zahl und ohne
Produktverhaeltnis; Drift-, Mass- und Aussagen-Gate greifen an ihnen nicht:
  1. "Am Tablet liegt dieses Kabel im Weg, wo es am Handy kaum auffaellt."
     — eine Aussage ueber Handhabung, nicht ueber ein Datenfeld.
  2. "Beides zusammen heisst: ein iPad mini oder ein kleines Android-Tablet ja,
     ein grosses Tablet nein." — folgt aus 8 Zoll und 215 mm, aber die Schwelle
     "gross" steht nirgends.
  3. "Bei langen Sitzungen am Tablet ist das der Unterschied zwischen
     Weiterspielen und Pause." — plausibel, unbelegt.
  4. "Die Auswahl ist klein" — eine Wertung der Zahl drei, keine Messung.
  5. "Da gehen die Modelle auseinander" — Ueberleitung.
  6. "Miss dein Geraet nach, bevor du bestellst, und rechne eine Huelle mit ein."
     — ein Rat, kein Produktfakt.
Diese sechs sind durch Lesen geprueft, nicht durch eine Maschine. Wer sie aendert,
prueft sie wieder durch Lesen.

Aufruf:  python3 scripts/gen_tablet_hub.py [--check]
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import produktdaten as pd                                       # noqa: E402
from seitenbau import (absatz, anteil, beleg_umgebung,  # noqa: E402
                       check_units, eur, faq_block,
                       faqpage_schema, gross, itemlist_schema, mz,
                       rest_phrase, und_liste, vb, zw)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(ROOT, 'assets', 'data', 'products.json')
DATEI = 'controller/tablet/index.html'

START = ('<!-- TAB-EXT:START (generiert von scripts/gen_tablet_hub.py, '
         'nicht von Hand editieren) -->')
END = '<!-- TAB-EXT:END -->'
CSS_START = '<!-- TAB-CSS:START -->'
CSS_END = '<!-- TAB-CSS:END -->'

CSS = (
    CSS_START + '\n<style>\n'
    '.tab-ext p{color:var(--ink-soft);line-height:1.7;margin-bottom:14px}\n'
    '.tab-ext h3{margin-top:26px;margin-bottom:6px}\n'
    '.tab-table{width:100%;border-collapse:collapse;margin:18px 0;font-size:14px}\n'
    '.tab-table th,.tab-table td{padding:11px 13px;border:1px solid var(--line);text-align:left}\n'
    '.tab-table th{background:var(--navy);color:#fff;font-weight:700;font-size:13px}\n'
    '.tab-table tr:nth-child(even) td{background:var(--surface-2)}\n'
    '.tab-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}\n'
    '.tab-note{color:var(--ink-soft);font-size:.9rem;margin-top:10px}\n'
    '</style>\n' + CSS_END
)

GLOBAL_KLASSEN = {'section', 'container', 'faq-list', 'faq-item', 'faq-a'}

FREIE_ZAHLEN = {'5'}        # "von 5 Sternen"

# Jede Aussage dieser Seite, die NICHT aus einem products.json-Feld faellt, steht
# hier als Beleg-Paar (Wert, Datei, Suchtext). Der Generator prueft bei jedem Lauf:
# Der Suchtext steht an seiner Fundstelle, seine UMGEBUNG passt zur Richtung der
# Aussage, und in products.json wird nur im Objekt DIESES Produkts gesucht.
#
# Warum zwei Tabellen und nicht nur eine: Der erste Entwurf las fuer beide
# Eigenschaften nur `claim` und schrieb daraus "fuer das uebrige Modell steht dazu
# nichts in unseren Daten". Fuer das Laden wurde das in Runde 1 korrigiert, fuer die
# GROESSE blieb derselbe Mechanismus stehen -- und dort war die Luecke groesser:
# Der V3 Pro traegt seine 8 Zoll im Amazon-Beleg vom 30.09., der G8 Plus seine
# 215 mm in den eigenen Metas, und `blog/controller-fuer-tablet/` nennt die 8 Zoll
# des V3 Pro seit dem 30.09. live und im FAQPage-Schema. Die Seite haette also
# eine Abwesenheit behauptet, die die Nachbarseite als ausdrueckliche Angabe fuehrt.
# "Wer nur die Stelle korrigiert, die der Pruefer genannt hat, hat den Pruefer
# bedient und nicht den Fehler" (P-18 Mechanismus 3).
LADEN = {
    'razer-kishi-ultra': (
        True, 'assets/data/products.json', 'Laden beim Spielen'),
    'gamesir-g8-plus': (
        True, 'controller/universal/gamesir-g8-plus-review/index.html',
        '✓ Pass-Through-Charging'),
    'razer-kishi-v3-pro': (
        False, 'controller/universal/razer-kishi-v3-pro-review/index.html',
        '✗ Kein Pass-Through-Charging'),
}

GROESSE = {
    'razer-kishi-ultra': (
        '8 Zoll', 'assets/data/products.json', 'iPad mini bis 8 Zoll'),
    # Quelle der Angabe ist der Amazon-Beleg vom 30.09. (ASIN B0F2JGV9NK, Titel
    # "und Tablets 8\"", Feature "Fuer iPads & Android-Tablets bis zu 8 Zoll",
    # dokumentiert in brain/03-research/raw/amazon/2026-09-30-datenkern-klaerung.md
    # samt Abwaegung gegen eine widersprechende 13-Zoll-Angabe derselben Seite).
    # Der Beleg ZEIGT aber auf den Blog-Artikel, nicht auf den Vault: `brain/` ist
    # lebendes Gedaechtnis, kein Deploy-Artefakt, und die Idempotenzprobe arbeitet
    # in einer Kopie OHNE `brain/`. Ein Seiten-Generator, der zur Laufzeit an einem
    # Vault-Pfad haengt, laesst sich aus einem Deploy-Checkout nicht mehr ausfuehren.
    'razer-kishi-v3-pro': (
        '8 Zoll', 'blog/controller-fuer-tablet/index.html',
        'iPads und Android-Tablets bis 8 Zoll'),
    # Die 215 mm stehen in KEINEM products.json-Feld und in keiner Beleg-Datei,
    # nur im Urteil und in den Metas der eigenen Testseite. Der Suchtext ist
    # deshalb auf "Brücke bis 215 mm" gekuerzt (trifft beides, nicht nur die
    # Metas), und der Text schreibt die Angabe der Testseite zu, statt sie
    # "belegt" zu nennen.
    'gamesir-g8-plus': (
        '215 mm', 'controller/universal/gamesir-g8-plus-review/index.html',
        'Brücke bis 215 mm'),
}


# ---------------------------------------------------------------- Datenschicht

def load_products():
    with open(PRODUCTS, encoding='utf-8') as f:
        data = json.load(f)
    return data['products'] if isinstance(data, dict) and 'products' in data else data


def zeile(p):
    r, c = pd.bewertung(p)
    return {'p': p, 'slug': pd.text(p, 'slug'), 'name': f'{pd.text(p, "brand")} '
            f'{pd.text(p, "name")}'.strip(), 'detail': pd.text(p, 'detail'),
            'preis': pd.preis_zahl(p), 'rating': r, 'count': c,
            'stock': pd.stock(p), 'claim': pd.text(p, 'claim'),
            'specs': pd.spec_paare(p)}


def tablet_rows(products):
    """Die Controller, die products.json als tablet-tauglich fuehrt.

    Quelle ist `worksOn`, nicht `platform`: Zwei der drei stehen unter
    platform=universal und waeren ueber die Plattform nicht zu finden.
    """
    sel = [zeile(p) for p in products
           if 'tablet' in (p.get('worksOn') or []) and pd.text(p, 'type') == 'controller']
    fehlend = [r['slug'] for r in sel if r['preis'] is None or r['rating'] is None]
    if fehlend:
        raise SystemExit(f'FEHLER: Preis oder Bewertung fehlt bei {fehlend}')
    if len(sel) < 2:
        raise SystemExit(
            f'FEHLER: nur {len(sel)} tablet-taugliche Controller. Diese Seite '
            f'vergleicht durchgehend und braucht mindestens zwei.')
    return sorted(sel, key=lambda r: r['preis'])


def spec_of(row, anfang, default=''):
    return pd.spec_wie(row['p'], anfang, default)


def link(row):
    return f'<a href="{row["detail"]}">{row["name"]}</a>'


def kabellos(rows):
    """Modelle, deren Verbindungsfeld eine Funkstrecke nennt."""
    return [r for r in rows
            if re.search(r'(?i)\bBT\b|bluetooth|kabellos', spec_of(r, 'Verb'))]


def laedt_mit(rows):
    """Modelle, fuer die das Durchladen belegt ist."""
    return [r for r in rows if LADEN.get(r['slug'], (None,))[0] is True]


def laedt_nicht(rows):
    """Modelle, fuer die sein Fehlen belegt ist."""
    return [r for r in rows if LADEN.get(r['slug'], (None,))[0] is False]


def beleg_raum(datei, row):
    """Der Text, in dem ein Beleg stehen darf.

    Fuer products.json ist das NUR das Objekt dieses Produkts. Die erste Fassung
    durchsuchte die ganze Datei -- dieselbe Luecke, durch die in P-18 "Chroma 12
    LEDs" (Phone Cooler) ein Merkmal des Kishi V3 Pro belegen durfte.
    """
    if datei.endswith('products.json'):
        return json.dumps(row['p'], ensure_ascii=False)
    pfad = os.path.join(ROOT, datei)
    if not os.path.exists(pfad):
        raise SystemExit(f'FEHLER: Beleg-Datei {datei} fehlt')
    return open(pfad, encoding='utf-8').read()


def pruefe_beleg(row, positiv, datei, suchtext, was):
    """Suchtext vorhanden UND Umgebung passend zur Richtung der Aussage (§A5 (3))."""
    raum = beleg_raum(datei, row)
    if suchtext not in raum:
        raise SystemExit(
            f'FEHLER: der Beleg "{suchtext}" steht nicht in {datei} '
            f'({was}, {row["slug"]}) -- die Aussage auf der Tablet-Seite waere '
            f'dann ungedeckt.')
    negativ = beleg_umgebung(raum, suchtext)
    # NUR Negationen. "nur" und "bis" sind einschraenkend, aber nicht verneinend:
    # "iPad mini bis 8 Zoll" haette sonst als Abwesenheitsbeleg gezaehlt.
    einschraenkend = re.search(r'\b(?:kein|keine|keinen|nicht|ohne)\b',
                               suchtext, re.I)
    if positiv and negativ:
        raise SystemExit(
            f'FEHLER: der Beleg "{suchtext}" fuer {was}/{row["slug"]} steht in '
            f'{datei} in einer Nachteils-Umgebung -- er belegt das Gegenteil.')
    if not positiv and negativ is False and not einschraenkend:
        raise SystemExit(
            f'FEHLER: der Beleg "{suchtext}" fuer {was}/{row["slug"]} steht in '
            f'{datei} NICHT in einer Nachteils-Umgebung -- er belegt keine '
            f'Abwesenheit.')


def check_belege(rows):
    """Jedes Urteil braucht seinen Beleg, und jedes Modell beide Urteile.

    Ein neues tablet-taugliches Produkt zwingt damit zur Entscheidung, statt
    stillschweigend in eine Menge "sagt nichts" zu fallen.
    """
    for tabelle_, was in ((LADEN, 'Laden'), (GROESSE, 'Groesse')):
        fehlt = [r['slug'] for r in rows if r['slug'] not in tabelle_]
        if fehlt:
            raise SystemExit(
                f'FEHLER: fuer {fehlt} fehlt ein {was}-Beleg. Entweder belegen '
                f'(Datei + Suchtext) oder den Absatz anpassen -- nicht als '
                f'Schweigen durchlaufen lassen (§A5).')
    for r in rows:
        wert, datei, text = LADEN[r['slug']]
        pruefe_beleg(r, wert is True, datei, text, 'Laden')
        wert, datei, text = GROESSE[r['slug']]
        pruefe_beleg(r, True, datei, text, 'Groesse')


# Was ein Mass misst. Der Groessen-Absatz erklaerte den Unterschied zwischen Zoll
# und Millimeter in einem festen Satz -- bei nur EINER Massgruppe stand dort eine
# Erklaerung fuer ein Mass, das gar nicht vorkommt, dazu "in verschiedenen Massen"
# und "Beides zusammen". Jetzt kommt die Erklaerung aus den vorhandenen Gruppen.
# Jeder Eintrag traegt sein EIGENES Verb. Die erste Fassung sparte es beim
# zweiten Teilsatz ein ("Millimeter die Geraetebreite") -- eine Ellipse, die nur
# trug, solange der Zoll-Eintrag zuerst stand. Die Reihenfolge kommt aber aus
# `gruppen`, und die entsteht in PREIS-Reihenfolge: Faellt der G8 Plus unter den
# Kishi Ultra, stuende dort "Millimeter die Geraetebreite, Zoll misst die
# Bildschirmdiagonale", und bei einer einzigen mm-Gruppe ein verbloses Fragment.
# Eine Ellipse ist auch eine Beugung von Hand (P-19).
MASS_ERKLAERT = {
    'Zoll': 'Zoll misst die Bildschirmdiagonale',
    'mm': 'Millimeter misst die Gerätebreite',
}


def mass_einheit(wert):
    einheit = wert.split()[-1]
    if einheit not in MASS_ERKLAERT:
        raise SystemExit(
            f'FEHLER: unbekanntes Mass "{einheit}" in GROESSE. Ohne Erklaerung in '
            f'MASS_ERKLAERT kann der Absatz es nicht einordnen.')
    return einheit


# Welcher Pfad welche Quelle ist. Kein Sammelzweig: Ein Beleg aus `vergleich/`
# oder `marken/` waere stillschweigend als "Testseite" ausgegeben worden, waehrend
# `mass_einheit()` zwei Zeilen weiter bei Unbekanntem korrekt abbricht.
QUELLE_LABEL = (
    ('assets/data/products.json', 'unserem Datenkern'),
    ('blog/', 'unserem Tablet-Ratgeber'),
    ('controller/', 'unseren Testseiten'),
    ('produkte/', 'unseren Datenblättern'),
)


def quelle_label(datei):
    """Woher eine Angabe stammt, in der Sprache der Seite."""
    for praefix, label in QUELLE_LABEL:
        if datei.startswith(praefix):
            return label
    raise SystemExit(
        f'FEHLER: fuer den Beleg-Pfad "{datei}" gibt es kein Quellen-Label. '
        f'Ohne Label wuerde die Seite die Herkunft falsch benennen -- '
        f'QUELLE_LABEL ergaenzen.')


def quellen_satz(rows):
    """Nennt die Herkunft der Groessenangaben, wenn sie nicht alle im Datenkern steht.

    Die 215 mm des G8 Plus stehen in KEINEM products.json-Feld und in keiner
    Beleg-Datei, nur im Urteil und in den Metas seiner Testseite; die 8 Zoll des
    V3 Pro stammen aus einem Amazon-Beleg und stehen im Ratgeber. Beides pauschal
    "belegt" zu nennen verwaessert das Wort (§A1/§A5). Die Seite sagt deshalb, wo
    die Angabe steht.
    """
    nach_quelle = {}
    for r in rows:
        nach_quelle.setdefault(quelle_label(GROESSE[r['slug']][1]), []).append(r)
    if set(nach_quelle) == {'unserem Datenkern'}:
        return ''
    return ('Die Angaben stammen aus '
            + und_liste(f'{q} ({und_liste(x["name"] for x in rs)})'
                        for q, rs in nach_quelle.items()) + '.')


def groessen_gruppen(rows):
    """Die belegten Groessengrenzen, nach Mass gruppiert.

    Zoll misst die Bildschirmdiagonale, Millimeter die Geraetebreite: zwei
    verschiedene Masse, die nicht zusammengezaehlt werden duerfen.
    """
    gruppen = {}
    for r in rows:
        gruppen.setdefault(GROESSE[r['slug']][0], []).append(r)
    return gruppen


# ---------------------------------------------------------------- Textschicht

def tabelle(rows):
    tr = []
    for r in rows:
        tr.append(
            f'      <tr><td>{link(r)}</td><td>{eur(r["preis"])}</td>'
            f'<td>{spec_of(r, "Verb")}</td>'
            f'<td>{pd.sterne_text(r["rating"])} ({pd.anzahl_text(r["count"])})</td>'
            f'<td>{pd.STOCK_LABEL.get(r["stock"], "")}</td></tr>')
    return (
        '    <div class="tab-wrap"><table class="tab-table">\n'
        '      <thead><tr><th scope="col">Modell</th><th scope="col">Preis</th>'
        '<th scope="col">Verbindung</th><th scope="col">Bewertung</th>'
        '<th scope="col">Verfügbar</th></tr></thead>\n'
        '      <tbody>\n' + '\n'.join(tr) + '\n      </tbody>\n'
        '    </table></div>\n'
        '    <p class="tab-note">Gelistet sind die Controller, die unser Datenkern '
        'ausdrücklich als tablet-tauglich führt. Preise und Bewertungen stammen aus '
        'unserem letzten Amazon-Abgleich.</p>\n'
    )


def haupttext(rows, n_ctrl):
    n = len(rows)
    guenstig, teuer = rows[0], rows[-1]
    funk = kabellos(rows)
    gruppen = groessen_gruppen(rows)
    herkunft = quellen_satz(rows)
    mit, ohne = laedt_mit(rows), laedt_nicht(rows)
    steigend = ([r['rating'] for r in rows]
                == sorted(r['rating'] for r in rows))
    return (
        f'    <p>Die Auswahl ist klein, und das ist die erste ehrliche Auskunft dieser '
        f'Seite: <strong>Unser Datenkern führt {anteil(n, n_ctrl, "Controller")} '
        f'ausdrücklich als tablet-tauglich.</strong> Die Spanne reicht von '
        f'{eur(guenstig["preis"])} bis {eur(teuer["preis"])}.</p>\n'
        + absatz(
            f'<strong>Hier zahlt sich der höhere Preis aus</strong>, anders als bei '
            f'unseren Kühlern und Triggern: Vom günstigsten zum teuersten Modell '
            f'steigt die Bewertung durchgehend mit, von '
            f'{pd.sterne_text(guenstig["rating"])} beim {link(guenstig)} auf '
            f'{pd.sterne_text(teuer["rating"])} beim {link(teuer)}. Das ist bei '
            f'{zw(n)} Modellen kein Gesetz. Bei unseren Kühlern und Triggern ist es '
            f'jeweils umgekehrt: Dort ist das teuerste Produkt das am schlechtesten '
            f'bewertete.' if steigend else '')
        + f'    <p><strong>Am Tablet entscheidet das Kabel mit.</strong> '
          f'{gross(anteil(len(funk), n, "Modelle"))} '
          f'{vb(len(funk), "koppelt", "koppeln")} sich auch kabellos: '
          f'{und_liste(link(r) for r in funk)} ({spec_of(funk[0], "Verb")}).'
        + (f' {gross(rest_phrase(n - len(funk), "Modell", "Modelle"))} '
           f'{vb(n - len(funk), "hängt", "hängen")} per USB-C am Gerät. Am Tablet '
           f'liegt dieses Kabel im Weg, wo es am Handy kaum auffällt.'
           if n - len(funk) else '')
        + '</p>\n'
        + absatz(
            f'<strong>Lädt das Tablet beim Spielen weiter?</strong> Da gehen die '
            f'Modelle auseinander, und bei langen Sitzungen am großen Display ist das '
            f'der Unterschied zwischen Weiterspielen und Pause. Belegt ist das '
            f'Durchladen für {und_liste(link(r) for r in mit)}; '
            f'bei {und_liste(link(r) for r in ohne)} nennt unser Test ausdrücklich '
            f'dessen Fehlen.'
            if mit and ohne else '')
        + absatz(
            f'<strong>Die Größe ist die eigentliche Hürde.</strong> '
            f'{gross(anteil(n, n, "Modelle"))} nennen eine Grenze'
            + (', aber in verschiedenen Maßen' if len(gruppen) > 1 else '')
            + ': '
            + ', '.join(f'{mass} {"beim" if len(rs) == 1 else "bei"} '
                        f'{und_liste(link(r) for r in rs)}'
                        for mass, rs in gruppen.items())
            + '. '
            + ', '.join(MASS_ERKLAERT[mass_einheit(m)] for m in gruppen) + '. '
            + (herkunft + ' ' if herkunft else '')
            + 'Für ein iPad mini oder ein kleines Android-Tablet reicht das, für '
              'ein großes Tablet nicht. Miss dein Gerät nach, bevor du bestellst, '
              'und rechne eine Hülle mit ein.')
    )


def faqs(rows, n_ctrl):
    n = len(rows)
    guenstig, teuer = rows[0], rows[-1]
    funk = kabellos(rows)
    gruppen = groessen_gruppen(rows)
    mit, ohne = laedt_mit(rows), laedt_nicht(rows)
    beste = max(rows, key=lambda r: r['rating'])
    fragen = [
        ('Welche Controller passen an ein Tablet?',
         f'{gross(anteil(n, n_ctrl, "Controller"))} unseres Sortiments führen wir '
         f'als tablet-tauglich: '
         + ' · '.join(f'{r["name"]} ({eur(r["preis"])}, '
                      f'{pd.sterne_text(r["rating"])} Sterne)' for r in rows) + '.'),
        ('Welcher davon ist der beste?',
         f'Nach der Bewertungslage der {zw(n)} führt der {beste["name"]} mit '
         f'{pd.sterne_text(beste["rating"])} Sternen aus '
         f'{pd.anzahl_text(beste["count"])} Bewertungen bei {eur(beste["preis"])}. '
         f'Er ist zugleich der teuerste der {zw(n)}, hier gehen Preis und Bewertung '
         f'also zusammen.'),
    ]
    fragen.append(
        ('Passt ein Clip-Controller an ein iPad?',
         'Das hängt von der Größe ab, und für jedes Modell ist eine Grenze '
         'genannt: '
         + ', '.join(f'{mass} {"beim" if len(rs) == 1 else "bei"} '
                     f'{und_liste(r["name"] for r in rs)}'
                     for mass, rs in gruppen.items())
         + '. Für ein iPad mini oder ein kleines Android-Tablet reicht das, für ein '
           'großes Tablet nicht.'))
    if funk:
        fragen.append(
            ('Geht das auch kabellos?',
             f'{gross(anteil(len(funk), n, "Modelle"))} '
             f'{vb(len(funk), "koppelt", "koppeln")} sich kabellos: '
             f'{und_liste(r["name"] for r in funk)} '
             f'({spec_of(funk[0], "Verb")}).'
             + (f' {gross(rest_phrase(n - len(funk), "Modell", "Modelle"))} '
                f'{vb(n - len(funk), "wird", "werden")} per USB-C angeschlossen.'
                if n - len(funk) else '')))
    if mit and ohne:
        fragen.append(
            ('Lädt das Tablet beim Spielen weiter?',
             f'Für {und_liste(r["name"] for r in mit)} ist das Durchladen belegt, '
             f'bei {und_liste(r["name"] for r in ohne)} nennt unser Test ausdrücklich '
             f'dessen Fehlen. '
             f'Bei langen Sitzungen am Tablet ist das der Unterschied zwischen '
             f'Weiterspielen und Pause.'))
    return fragen


# ---------------------------------------------------------------- Gates

def allowed_numbers(rows, n_ctrl):
    ok = set(FREIE_ZAHLEN) | {str(n_ctrl)}
    for r in rows:
        ok.add(str(r['preis']))
        ok.add(pd.sterne_text(r['rating']))
        ok.add(pd.anzahl_text(r['count']))
        ok.add(str(r['count']))
        for _k, v in r['specs']:
            ok |= set(re.findall(r'\d+(?:[.,]\d+)?', v))
        ok |= set(re.findall(r'\d+(?:[.,]\d+)?', r['claim']))
        # Belegte Angaben ausserhalb von products.json zaehlen mit, aber nur die
        # aus dem Beleg DIESES Produkts.
        ok |= set(re.findall(r'\d+(?:[.,]\d+)?',
                             LADEN[r['slug']][2] + ' ' + GROESSE[r['slug']][2]))
    for n in range(0, len(rows) + 1):
        ok.add(str(n))
    return ok


def check_numbers(block, rows, n_ctrl):
    """§A1: jede Zahl aus products.json. Einheiten zusaetzlich als Paar."""
    belegt = ' '.join(LADEN[r['slug']][2] + ' ' + GROESSE[r['slug']][2] for r in rows)
    check_units(block, rows, [], DATEI, belegt)
    plain = re.sub(r'<[^>]+>', ' ', block)
    for nm in sorted({r['name'] for r in rows}
                     | {pd.text(r['p'], 'name') for r in rows}, key=len, reverse=True):
        plain = plain.replace(nm, ' ')
    plain = re.sub(r'\b(iPad|iPhone|iOS|Android|USB)[\s-]*C?\s*\d*', ' ', plain)
    ok = allowed_numbers(rows, n_ctrl)
    gefunden = re.findall(r'(?<![\w,.-])(\d+(?:[.,]\d+)?)(?![\w,.-])', plain)
    unbelegt = sorted({g for g in gefunden if g not in ok})
    if unbelegt:
        raise SystemExit(f'DRIFT-GATE ({DATEI}): Zahl(en) ohne Deckung in '
                         f'products.json: {", ".join(unbelegt)}')


def check_claims(rows, alle):
    """Die Vergleichsaussagen nachrechnen, nicht nur ihre Zahlen."""
    f = []
    funk = kabellos(rows)
    if not funk:
        f.append('kein tablet-taugliches Modell koppelt mehr kabellos, der Absatz '
                 'über das Kabel trägt dann nicht')
    if len(set(spec_of(r, 'Verb') for r in funk)) > 1:
        f.append('die kabellosen Modelle nennen verschiedene Verbindungsarten, der '
                 'Text zeigt aber nur die des ersten')
    mit, ohne = laedt_mit(rows), laedt_nicht(rows)
    # Kein Gate auf die Mengenstaerken: Der Absatz zaehlt beide Seiten auf und
    # entfaellt, wenn eine davon leer ist. Ein Gate haette hier nur den naechsten
    # belegten Eintrag in LADEN blockiert.
    # Kein Gate auf die Zahl der Groessenangaben: Der Absatz gruppiert nach Mass und
    # zaehlt beide Gruppen auf. Genau dieses Gate hat in Runde 1 verhindert, dass die
    # belegten Grenzen des V3 Pro und des G8 Plus ueberhaupt eingetragen werden
    # konnten -- ein Gate, das die Korrektur blockiert, hat die falsche Regel.
    beste = max(rows, key=lambda r: r['rating'])
    if beste is not rows[-1]:
        f.append('der bestbewertete ist nicht mehr der teuerste, die FAQ-Antwort '
                 '"hier gehen Preis und Bewertung zusammen" trägt nicht')
    # Der Querverweis auf die Zubehoer-Seiten: dort ist das teuerste das schlechteste.
    for platform in ('kuehler', 'trigger'):
        gruppe = [zeile(p) for p in alle
                  if pd.text(p, 'platform') == platform
                  and pd.text(p, 'type') == 'zubehoer' and pd.bewertung(p)[0]]
        teuerst = max(gruppe, key=lambda r: r['preis'])
        if teuerst is not min(gruppe, key=lambda r: r['rating']):
            f.append(f'bei {platform} ist das teuerste Produkt nicht mehr das am '
                     f'schlechtesten bewertete, der Querverweis trägt nicht')
    if f:
        raise SystemExit('AUSSAGEN-GATE: Der Text behauptet etwas, das die Daten nicht '
                         'mehr hergeben:\n   ' + '\n   '.join(f))


# ---------------------------------------------------------------- Anwendung

def apply_to_file(path, rows, n_ctrl):
    with open(path, encoding='utf-8') as f:
        original = f.read()
    html = original
    html = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', html, flags=re.S)
    html = re.sub(re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?', '', html, flags=re.S)

    if '</head>' not in html or '</main>' not in html:
        raise SystemExit(f'FEHLER: kein </head> oder </main> in {path}')
    html = html.replace('</head>', CSS + '\n</head>', 1)

    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not canonical:
        raise SystemExit(f'FEHLER: kein canonical in {path}')

    prosa = ('  <section class="section"><div class="container tab-ext" '
             'style="max-width:820px">\n'
             '    <h2>Controller für Tablet und iPad: Darauf kommt es an</h2>\n'
             + haupttext(rows, n_ctrl)
             + f'    <h3>{gross(anteil(len(rows), len(rows), "Modelle"))} im '
               f'Vergleich</h3>\n'
             + tabelle(rows)
             + '  </div></section>\n')
    faq = faq_block(faqs(rows, n_ctrl), 'Häufige Fragen zu Tablet-Controllern',
                    'tab-ext')
    inhalt = prosa + faq
    block = (f'{START}\n{inhalt}'
             f'<script type="application/ld+json">\n'
             f'{itemlist_schema(html, rows, "Controller für Tablet und iPad 2026", canonical.group(1))}\n'
             f'</script>\n'
             f'<script type="application/ld+json">\n{faqpage_schema(inhalt)}\n</script>\n'
             f'{END}\n')
    html = html.replace('</main>', block + '</main>', 1)

    assert html.count(START) == 1 and html.count(END) == 1, 'Block nicht genau einmal da'
    assert html.count(CSS_START) == 1 and html.count(CSS_END) == 1, 'CSS nicht einmal da'
    erzeugt = re.search(re.escape(START) + r'(.*?)' + re.escape(END), html, re.S).group(1)
    for klasse in sorted({c for attr in re.findall(r'class="([^"]+)"', erzeugt)
                          for c in attr.split()}):
        if klasse not in GLOBAL_KLASSEN:
            assert f'.{klasse}' in CSS, f'CSS-Regel fehlt fuer .{klasse}'
    assert erzeugt.count('<details class="faq-item">') == erzeugt.count('"@type": "Question"'), \
        'FAQ/Schema-Drift'
    assert '—' not in erzeugt, 'Em-Dash im erzeugten Text (verboten laut CLAUDE.md)'
    assert '<p></p>' not in erzeugt, 'leerer Absatz im erzeugten Text'
    check_numbers(erzeugt, rows, n_ctrl)
    return original, html


def main():
    check = '--check' in sys.argv
    produkte = load_products()
    rows = tablet_rows(produkte)
    n_ctrl = sum(1 for p in produkte if pd.text(p, 'type') == 'controller')
    check_belege(rows)
    check_claims(rows, produkte)

    pfad = os.path.join(ROOT, DATEI)
    original, html = apply_to_file(pfad, rows, n_ctrl)
    geaendert = html != original
    if geaendert and not check:
        with open(pfad, 'w', encoding='utf-8') as f:
            f.write(html)
    woerter = len(re.sub(r'\s+', ' ', re.sub(
        r'<[^>]+>', ' ', re.sub(r'(?is)<(script|style|nav|footer|head)\b.*?</\1>', ' ',
                                re.search(r'<main>(.*)</main>', html, re.S).group(1)))).split())
    print(f'  {DATEI:<34} {woerter:>4} Wörter · '
          f'{html.count(chr(60) + "details class=" + chr(34) + "faq-item")} FAQs · '
          f'{"geändert" if geaendert else "unverändert"}')
    print(f'\n[{"--check" if check else "geschrieben"}] '
          f'{1 if geaendert else 0} Datei(en)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
