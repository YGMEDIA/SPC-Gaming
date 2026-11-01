#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_zubehoer_sections.py — Zubehoer-Ast ausbauen (01.11.2026)

Baut die vier Seiten des Zubehoer-Asts von Thin Pages auf Standard aus:

    /zubehoer/                41 Woerter
    /zubehoer/handy-kuehler/ 163 Woerter   <- staerkste Seite der Site (GSC-Lauf 8)
    /zubehoer/finger-sleeves/168 Woerter
    /zubehoer/trigger/       294 Woerter

Anlass ist GSC-Lauf 8 (brain/03-research/raw/gsc/2026-11-01.md): handy-kuehler
traegt mit 18 Impressionen/28T die meiste Nachfrage der ganzen Site, das
Kuehler-Cluster 17 Prozent aller Impressionen. Dasselbe Muster wie Lauf 6
(mini-gamepad, 118 W) und Lauf 7 (vier Marken-Seiten, 59-138 W).

Eigenschaften (dieselben sechs Pflicht-Mechanismen wie P-18):
  · IDEMPOTENT  — der Block steht zwischen Markern und wird je Lauf ersetzt.
  · §A1         — jede Zahl stammt aus products.json. Das Drift-Gate laesst nur
                  Zahlen durch, die in den Daten DIESER Kategorie vorkommen.
  · §A4         — ItemList und FAQPage werden aus dem finalen HTML gerendert,
                  Schema und sichtbarer Text koennen nicht auseinanderlaufen.
  · §A5         — keine Aussage ohne Deckung. Was products.json nicht sagt,
                  steht nicht auf der Seite.
  · §A6         — die Kategorien sind schwach bewertet, und das steht da:
                  vier der 14 Artikel liegen unter 3,8 Sternen.
  · AUSSAGEN-GATE — die Vergleichssaetze ("der teuerste ist der schlechtest
                  bewertete") werden gegen die Daten nachgerechnet, nicht nur
                  ihre Zahlen. Genau diese Klasse kippte am 30.09. zweimal.

Aufruf:  python3 scripts/gen_zubehoer_sections.py [--check]
         --check schreibt nichts, meldet nur, ob die Dateien aktuell waeren.
"""

import json
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import produktdaten as pd                                    # noqa: E402
from gen_bestenliste import vollname                         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(ROOT, 'assets', 'data', 'products.json')

# Der Marker steht im ausgelieferten HTML, also gilt hier dieselbe Regel wie fuer
# die Copy: kein Em-Dash. Das `assert` unten prueft nur den Inhalt ZWISCHEN den
# Markern und haette den Kommentar nie erwischt (Pruefbericht 01.11., Hinweis 10).
START = ('<!-- ZUB-EXT:START (generiert von scripts/gen_zubehoer_sections.py, '
         'nicht von Hand editieren) -->')
END = '<!-- ZUB-EXT:END -->'
CSS_START = '<!-- ZUB-CSS:START -->'
CSS_END = '<!-- ZUB-CSS:END -->'

# Seiten-CSS nach dem Muster der Marken-Hubs. Nur bestehende Design-Tokens aus
# style.css; .faq-item/.faq-a/.faq-list sind dort bereits global definiert.
CSS = (
    CSS_START + '\n<style>\n'
    '.zub-ext p{color:var(--ink-soft);line-height:1.7;margin-bottom:14px}\n'
    '.zub-ext h3{margin-top:26px;margin-bottom:6px}\n'
    '.zub-table{width:100%;border-collapse:collapse;margin:18px 0;font-size:14px}\n'
    '.zub-table th,.zub-table td{padding:11px 13px;border:1px solid var(--line);text-align:left}\n'
    '.zub-table th{background:var(--navy);color:#fff;font-weight:700;font-size:13px}\n'
    '.zub-table tr:nth-child(even) td{background:var(--surface-2)}\n'
    '.zub-table tr.is-weak td{background:var(--surface-2);color:var(--ink-dim)}\n'
    '.zub-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}\n'
    '.zub-note{color:var(--ink-soft);font-size:.9rem;margin-top:10px}\n'
    '</style>\n' + CSS_END
)

# Jede CSS-Klasse, die der Generator ins Markup schreibt, braucht oben eine Regel.
# Ausgenommen sind Klassen, die style.css global fuehrt (gemessen, nicht geraten).
GLOBAL_KLASSEN = {'section', 'container', 'faq-list', 'faq-item', 'faq-a'}

# Zahlen, die weder Preis noch Bewertung noch Spec sind. Jede weitere Zahl im Text
# muss aus products.json kommen.
FREIE_ZAHLEN = {
    '5',      # "von 5 Sternen"
    '3,8',    # die §A6-Schwelle aus der Constitution
    '2026',   # Jahreszahl
}

KATEGORIEN = {
    'kuehler': dict(
        datei='zubehoer/handy-kuehler/index.html',
        wort='Handy-Kühler', plural='Handy-Kühler', dativ='Handy-Kühlern',
        ratgeber='/blog/handy-kuehler-sinnvoll/',
        listenname='Handy-Kühler im Sortiment 2026'),
    'finger-sleeves': dict(
        datei='zubehoer/finger-sleeves/index.html',
        wort='Finger Sleeves', plural='Sets', dativ='Finger Sleeves',
        ratgeber='/blog/finger-sleeves-sinnvoll/',
        listenname='Finger Sleeves im Sortiment 2026'),
    'trigger': dict(
        datei='zubehoer/trigger/index.html',
        wort='Trigger', plural='Trigger-Sets', dativ='Trigger-Aufsätzen',
        ratgeber='/blog/trigger-erlaubt-pubg/',
        listenname='Trigger-Aufsätze im Sortiment 2026'),
}

HUB = 'zubehoer/index.html'

# Die Prosa-Form der vier Verfuegbarkeitswerte. `pd.STOCK_LABEL` traegt die Form fuer
# die Tabelle ("Nur gebraucht"), fuer einen Satz braucht es eine Praedikativform.
# Geschrieben wird sie hier, aber NICHT frei: Die Schluessel werden gegen den Datenkern
# geprueft, damit ein fuenfter Wert nicht stillschweigend als "nicht kaufbar" durchgeht.
#
# Der Befund dahinter: `stock != 'ja'` wurde als "nicht kaufbar" formuliert, waehrend
# die Tabelle derselben Seite "Nur gebraucht" bzw. "Nur Drittanbieter" zeigte. Beide
# Werte sind im Datenkern in Gebrauch (Turtle Beach Atom, ShanWan metallisch-braun),
# die Seite haette sich also selbst widersprochen (Pruefbericht 01.11., Blocker 3).
STOCK_PROSA = {
    'nein': 'derzeit nicht kaufbar',
    'gebraucht': 'derzeit nur gebraucht erhältlich',
    'drittanbieter': 'derzeit nur über Drittanbieter erhältlich',
}
if set(STOCK_PROSA) | {'ja'} != set(pd.STOCK_LABEL):
    raise SystemExit(
        'FEHLER: STOCK_PROSA deckt andere Werte ab als produktdaten.STOCK_LABEL '
        f'({sorted(set(STOCK_PROSA) | {"ja"})} gegen {sorted(pd.STOCK_LABEL)}) -- '
        'ein neuer stock-Wert braucht hier seine eigene Formulierung')


def lage(row):
    """Wie die Verfuegbarkeit dieses Produkts im Fliesstext heisst."""
    return STOCK_PROSA[row['stock']]


ZAHLWORT = {1: 'ein', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf', 6: 'sechs',
            7: 'sieben', 8: 'acht', 9: 'neun', 10: 'zehn', 11: 'elf', 12: 'zwölf',
            13: 'dreizehn', 14: 'vierzehn'}


def zw(n):
    """Zahlwort vor einem Substantiv: "ein Set", "zwei Sets"."""
    _keine_null(n, 'zw')
    return ZAHLWORT.get(n, str(n))


def zwn(n):
    """Zahlwort ALLEIN stehend: "eins der vier Sets", nicht "ein der vier Sets".

    Dieselbe Zahl, zwei Formen. Die erste Fassung nutzte ueberall zw() und schrieb
    damit auf drei Seiten "Ein der sieben Sets liegt unter 3,8 Sternen".
    """
    _keine_null(n, 'zwn')
    return 'eins' if n == 1 else ZAHLWORT.get(n, str(n))


def eur(n):
    """Euro-Betrag ohne Nachkommastellen, so wie products.json ihn fuehrt."""
    return f'{n} €'


def komma(x, dec=2):
    """Deutsche Schreibweise, kaufmaennisch gerundet.

    f'{0.175:.2f}' gibt '0.17' — die Binaerdarstellung von 0,175 liegt knapp
    darunter. Der Preis pro Huelse (7 € / 40 Stueck) stand damit um einen Cent
    unter dem, was ein Leser nachrechnet. Decimal rundet die Zahl, nicht ihre
    Naeherung.
    """
    q = Decimal(1).scaleb(-dec)
    return str(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)).replace('.', ',')


# ---------------------------------------------------------------- Datenschicht

def load_products():
    with open(PRODUCTS, encoding='utf-8') as f:
        data = json.load(f)
    return data['products'] if isinstance(data, dict) and 'products' in data else data


def gross(text):
    """Ersten Buchstaben gross, Rest unangetastet. `str.capitalize()` kleint den
    Rest und haette aus "Ein Set" ein "Ein set" gemacht."""
    return text[:1].upper() + text[1:]


def mz(n, singular, plural):
    """Zahlwort plus Substantiv im richtigen Numerus: "ein Set", "zwei Sets".

    Das Substantiv kommt OHNE Artikel. Mit "das Set" als Singular lieferte die
    Funktion "ein das Set" -- ein Aufrufer-Fehler, aber einer, der sich wiederholt,
    wenn er nicht hier steht.
    """
    _keine_null(n, 'mz')
    return f'{zw(n)} {singular}' if n == 1 else f'{zw(n)} {plural}'


def mz_dativ(n, singular, plural):
    """Dasselbe im Dativ: "einem Set", "zwei Sets"."""
    _keine_null(n, 'mz_dativ')
    return f'einem {singular}' if n == 1 else f'{zw(n)} {plural}'


def _keine_null(k, wo):
    """Null ist keine Mengenangabe, sondern ein anderer Satz.

    `anteil(0, 3, "Geräte")` lieferte "0 der drei Geräte", und der Satz drumherum war
    dann inhaltlich leer: Nichts ist "unbequem", wenn kein Produkt unter der Schwelle
    liegt, und die graue Markierung in der Tabelle verwiese auf nichts. Eine Null-Form
    zu erfinden waere die falsche Antwort gewesen; der Satz gehoert weggelassen. Die
    Helfer brechen deshalb ab, damit niemand den leeren Fall stillschweigend
    formuliert (Pruefbericht 01.11., Runde 4).
    """
    if k == 0:
        raise SystemExit(
            f'FEHLER: {wo}(0, ...) aufgerufen. Ein Satz ueber eine leere Menge gehoert '
            f'weggelassen, nicht mit "null" formuliert -- siehe tablet_satz/ohne_satz.')


def anteil(k, n, plural):
    """"vier der sieben Sets", bei Vollstaendigkeit "alle sieben Sets".

    Gibt KLEIN zurueck. Die erste Fassung schrieb immer gross und lieferte damit
    mitten im Satz "Weil Zwei der drei Modelle ...". Wo ein Satz beginnt, steht
    `gross()` jetzt an der Aufrufstelle, und man sieht dort, dass es gewollt ist.
    """
    _keine_null(k, 'anteil')
    return f'alle {zw(n)} {plural}' if k == n else f'{zwn(k)} der {zw(n)} {plural}'


def die_mz(n, singular, plural):
    """"das eine Set" / "die drei Sets" -- bestimmter Artikel plus Zahlwort.

    Nur fuer saechliche Substantive (Set, Gerät). Entstanden, weil der
    Material-Satz seine beiden Haelften unterschiedlich gebaut hatte: Die
    Polyester-Haelfte hatte einen Singular-Zweig, die andere nicht, und schrieb
    bei einem Set "Die ein Sets ohne Polyesterfaser steht bei 4,4 Sternen".
    """
    _keine_null(n, 'die_mz')
    return f'das eine {singular}' if n == 1 else f'die {zw(n)} {plural}'


def vb(n, singular, plural):
    """Verbform zur Zahl. Der Pruefbericht hat drei Stellen gefunden, an denen
    Substantiv und Verb fest im Text standen, waehrend die Zahl aus den Daten kam:
    "bei ein Sets steht", "ein nennen gar keine", "drei hat zwei". Alle drei waren
    heute richtig und beim naechsten Abgleich falsch. Ein Gate haette die Zahl nur
    festgenagelt und damit die naechste korrekte Datenpflege blockiert; die Grammatik
    gehoert an die Zahl, nicht in ein Gate (P-13 Mechanismus 6)."""
    _keine_null(n, 'vb')
    return singular if n == 1 else plural


def zeile(p):
    """Eine Produktzeile mit allem, was der Text braucht. Alles aus produktdaten.py,
    nichts hier nachgebaut — die Regeln fuer Preis, Bewertung und Verfuegbarkeit
    gehoeren an EINE Stelle (Lehre aus verify.py Abschnitt 6)."""
    r, c = pd.bewertung(p)
    return {
        'p': p,
        'slug': pd.text(p, 'slug'),
        'name': vollname(p),
        'kurz': pd.text(p, 'name'),
        'detail': pd.text(p, 'detail'),
        'preis': pd.preis_zahl(p),
        'rating': r,
        'count': c,
        'stock': pd.stock(p),
        'claim': pd.text(p, 'claim'),
        'specs': pd.spec_paare(p),
    }


def rows_of(products, platform):
    """Die Produkte einer Zubehoer-Kategorie, aufsteigend nach Preis."""
    sel = [zeile(p) for p in products
           if pd.text(p, 'type') == 'zubehoer' and pd.text(p, 'platform') == platform]
    fehlend = [r['slug'] for r in sel if r['preis'] is None or r['rating'] is None]
    if fehlend:
        raise SystemExit(f'FEHLER: {platform}: Preis oder Bewertung fehlt bei {fehlend}')
    # Die Seiten vergleichen durchgehend: "das teuerste ist das am schlechtesten
    # bewertete", "der bestbewertete liegt preislich in der Mitte", "ein Vergleich von
    # drei gegen eins". Mit einem einzigen Produkt ist davon kein Satz mehr wahr, und
    # sieben Mengenangaben stuenden als "ein Sets" da. Die Antwort darauf ist kein
    # Singular-Zweig an sieben Stellen, sondern ein anderer Seitentyp -- deshalb bricht
    # der Generator hier ab, statt eine Einproduktseite zu schreiben.
    if len(sel) < 2:
        raise SystemExit(
            f'FEHLER: Kategorie "{platform}" fuehrt nur {len(sel)} Produkt. Diese Seite '
            f'ist durchgehend vergleichend gebaut und braucht mindestens zwei. Bei einem '
            f'Produkt gehoert dorthin ein anderer Seitentyp, keine gebeugte Zahl.')
    return sorted(sel, key=lambda r: r['preis'])


def spec_of(row, anfang, default=''):
    return pd.spec_wie(row['p'], anfang, default)


def stueckzahl(row):
    """"10 Stück" -> 10. Nur fuer Finger Sleeves; ohne Angabe None."""
    m = re.search(r'(\d+)', spec_of(row, 'Set'))
    return int(m.group(1)) if m else None


def link(row):
    return f'<a href="{row["detail"]}">{row["name"]}</a>'


def absatz(inhalt):
    """Ein <p> nur, wenn es etwas einzurahmen gibt.

    Der Rahmen stand fest und nur sein Inhalt unter Bedingung: Waren Schwellen-
    und Material-Satz beide leer, blieb ein <p></p> stehen, und `.zub-ext p` macht
    daraus eine sichtbare Luecke von 14 Pixeln.
    """
    return f'    <p>{inhalt}</p>\n' if inhalt.strip() else ''


def spanne(gruppe):
    """"bei 4,2 Sternen" oder "zwischen 4,2 und 4,4 Sternen"."""
    lo = min(r['rating'] for r in gruppe)
    hi = max(r['rating'] for r in gruppe)
    if lo == hi:
        return f'bei {pd.sterne_text(lo)} Sternen'
    return f'zwischen {pd.sterne_text(lo)} und {pd.sterne_text(hi)} Sternen'


def best(rows):
    return max(rows, key=lambda r: r['rating'])


def schlechtest(rows):
    return min(rows, key=lambda r: r['rating'])


def teuerst(rows):
    return max(rows, key=lambda r: r['preis'])


def guenstigst(rows):
    return min(rows, key=lambda r: r['preis'])


def ohne_akku_belegt(rows):
    """Produkte, deren Daten AUSDRUECKLICH sagen, dass kein Akku verbaut ist.

    Der Satz hiess zuerst "keiner der drei bringt einen eigenen Akku mit". Belegt
    ist das bei zweien (Spec "USB (kein Akku)" und Claim "hat keinen Akku"); beim
    dritten nennt products.json nur ein Netzteil und schweigt zum Akku. Eine
    dokumentierte Abwesenheit zu behaupten, wo die Quelle schweigt, ist derselbe
    Fehlertyp, der in diesem Projekt dreimal live gegangen ist (§A5).
    """
    return [r for r in rows
            if 'kein Akku' in ' '.join(v for _k, v in r['specs'])
            or 'keinen Akku' in r['claim']]


def schwache(rows):
    """Produkte unter der §A6-Schwelle von 3,8 Sternen."""
    return [r for r in rows if r['rating'] < 3.8]


def nicht_kaufbar(rows):
    return [r for r in rows if r['stock'] != 'ja']


# ---------------------------------------------------------------- Textschicht

def tabelle(rows, spalte3, wert3):
    """Die Produkttabelle einer Kategorie. Dritte Spalte je Kategorie verschieden,
    die ersten beiden und die letzten zwei sind ueberall gleich."""
    tr = []
    for r in rows:
        weak = ' class="is-weak"' if r['rating'] < 3.8 else ''
        verf = pd.STOCK_LABEL.get(r['stock'], '')
        tr.append(
            f'      <tr{weak}><td>{link(r)}</td><td>{eur(r["preis"])}</td>'
            f'<td>{wert3(r)}</td>'
            f'<td>{pd.sterne_text(r["rating"])} ({pd.anzahl_text(r["count"])})</td>'
            f'<td>{verf}</td></tr>')
    return (
        '    <div class="zub-wrap"><table class="zub-table">\n'
        f'      <thead><tr><th scope="col">Modell</th><th scope="col">Preis</th>'
        f'<th scope="col">{spalte3}</th><th scope="col">Bewertung</th>'
        f'<th scope="col">Verfügbar</th></tr></thead>\n'
        '      <tbody>\n' + '\n'.join(tr) + '\n      </tbody>\n'
        '    </table></div>\n'
        '    <p class="zub-note">Preise und Bewertungen stammen aus unserem letzten '
        'Amazon-Abgleich und stehen so in unserem Datenkern.'
        + (f' Grau hinterlegt ist, was unter {komma(3.8, 1)} Sternen liegt: Diese '
           f'Modelle empfehlen wir nicht, wir führen sie, damit die Lücke sichtbar '
           f'bleibt.' if any(r['rating'] < 3.8 for r in rows) else '')
        + '</p>\n'
    )


def kuehler_text(rows, L):
    n = len(rows)
    bst, sch = best(rows), schlechtest(rows)
    teu, gue = teuerst(rows), guenstigst(rows)
    schw = schwache(rows)
    ohne_akku = ohne_akku_belegt(rows)
    akku = L('ozkak-trigger-set')
    return (
        f'    <p>Wir führen {zw(n)} Handy-Kühler, von {eur(gue["preis"])} bis '
        f'{eur(teu["preis"])}. '
        + (f'Die wichtigste Zahl dieser Seite ist unbequem: '
           f'<strong>{gross(anteil(len(schw), n, "Geräte"))} '
           f'{vb(len(schw), "liegt", "liegen")} unter {komma(3.8, 1)} Sternen</strong>, '
           f'und das teuerste Gerät ist zugleich das am schlechtesten bewertete.'
           if schw else
           f'Auffällig ist vor allem eins: Das teuerste Gerät ist zugleich das am '
           f'schlechtesten bewertete.')
        + f' Der {link(teu)} kostet {eur(teu["preis"])} und steht bei '
          f'{pd.sterne_text(teu["rating"])} aus {pd.anzahl_text(teu["count"])} '
          f'Bewertungen.</p>\n'
        f'    <p>Am besten kommt der {link(bst)} weg: '
        f'{pd.sterne_text(bst["rating"])} aus {pd.anzahl_text(bst["count"])} Bewertungen '
        f'bei {eur(bst["preis"])}. Er liegt preislich in der Mitte, nicht oben. Wer also '
        f'nach der Regel "teurer gleich besser" kauft, landet in dieser Kategorie beim '
        f'falschen Gerät.</p>\n'
        f'    <p><strong>Zwei Dinge gelten {"für beide" if n == 2 else "für alle " + zw(n)}:'
        f'</strong> Sie arbeiten mit '
        f'einem Peltier-Element, kühlen also aktiv herunter statt nur Luft zu bewegen. '
        f'Und sie hängen am Kabel: Alle {zw(n)} beziehen ihren Strom über USB. '
        f'{gross(zwn(len(ohne_akku)))} von ihnen '
        f'{vb(len(ohne_akku), "sagt", "sagen")} ausdrücklich, dass kein eigener Akku '
        f'verbaut ist, bei {mz_dativ(n - len(ohne_akku), "Gerät", "Geräten")} nennen '
        f'unsere Daten ein Netzteil als Stromquelle. '
        f'Wer Kühlung und Akku in einem Gerät sucht, findet das in unserem Zubehör nur '
        f'beim <a href="{akku["detail"]}">{vollname(akku)}</a>, einem Trigger-Griff für '
        f'{eur(pd.preis_zahl(akku))} aus der '
        f'<a href="/zubehoer/trigger/">Trigger-Kategorie</a>.</p>\n'
        f'    <p>Ob sich das überhaupt lohnt, hängt stärker vom Spiel ab als vom Gerät. '
        f'Wir haben das in einem eigenen Artikel auseinandergenommen: '
        f'<a href="/blog/handy-kuehler-sinnvoll/">Handy-Kühler: sinnvoll oder '
        f'Hype?</a></p>\n'
    )


def sleeves_text(rows, L, alle):
    n = len(rows)
    bst, sch = best(rows), schlechtest(rows)
    teu, gue = teuerst(rows), guenstigst(rows)
    schw = schwache(rows)
    pro = {r['slug']: r['preis'] / stueckzahl(r) for r in rows if stueckzahl(r)}
    teuerst_stueck = max(pro, key=pro.get)
    guenstigst_stueck = min(pro, key=pro.get)
    zweiter = sorted(alle, key=lambda r: -r['count'])[1]
    # Der Material-Vergleich zaehlt MATERIALIEN, nicht Bewertungen. Vorher stand hier
    # "ein Vergleich von {n - len(schw)} gegen {len(schw)}", also die Mengen der
    # Bewertungsschwelle: Heute sind beide zufaellig gleich, weil genau das
    # Polyester-Set unter 3,8 liegt. Faellt ein zweites Set unter die Schwelle, haette
    # der Satz "zwei gegen zwei" gesagt und damit einen Vergleich beschrieben, den der
    # Satz davor gar nicht zieht (Pruefbericht 01.11., Runde 5).
    poly = [r for r in rows if 'Polyester' in spec_of(r, 'Material')]
    andere = [r for r in rows if r not in poly]
    material_satz = ''
    if poly and andere:
        # "Gefaelle" ist eine Aussage ueber die Daten, keine Ueberschrift: Sie gilt nur,
        # solange die beiden Bewertungsspannen sich nicht ueberlappen. Ohne diese
        # Unterscheidung haette der Satz bei 3,6-4,2 gegen 4,2-4,4 weiter ein Gefaelle
        # behauptet und im Schlussteil einen "Unterschied", den es nicht gibt.
        getrennt = (max(r['rating'] for r in poly)
                    < min(r['rating'] for r in andere))
        material_satz = (
            (f'Beim Material zeigt unsere Datenlage ein Gefälle, das zu dieser '
             f'Preisrechnung passt: ' if getrennt else
             f'Beim Material liegen die Bewertungen näher beieinander: ')
            + f'{gross(die_mz(len(andere), "Set", "Sets"))} ohne Polyesterfaser '
              f'{vb(len(andere), "steht", "stehen")} {spanne(andere)}, '
              f'{die_mz(len(poly), "Set", "Sets")} aus Polyesterfaser '
              f'{vb(len(poly), "liegt", "liegen")} {spanne(poly)}.'
            + (f' Das ist ein Vergleich von {zwn(len(andere))} gegen '
               f'{zwn(len(poly))}, also kein Beweis, aber der Unterschied steht in den '
               f'Bewertungen.' if getrennt else ''))
    ts = next(r for r in rows if r['slug'] == teuerst_stueck)
    gs = next(r for r in rows if r['slug'] == guenstigst_stueck)
    return (
        f'    <p>Das meistbewertete Produkt unserer ganzen Seite ist kein Controller für '
        f'{eur(teuerst(alle)["preis"])}, sondern ein Beutel Stoffhülsen: Das Set {link(bst)} '
        f'trägt {pd.anzahl_text(bst["count"])} Amazon-Bewertungen und steht bei '
        f'{pd.sterne_text(bst["rating"])} Sternen. Das zweitmeistbewertete unserer '
        f'{zw(len(alle))} Produkte liegt bei {pd.anzahl_text(zweiter["count"])} '
        f'Bewertungen: {zweiter["name"]}.</p>\n'
        f'    <p>Wir führen {zw(n)} Sets von {eur(gue["preis"])} bis '
        f'{eur(teu["preis"])}. Der Preis pro Set sagt dabei wenig, weil die Packungen '
        f'unterschiedlich groß sind. Pro Hülse gerechnet reicht die Spanne von '
        f'{komma(pro[guenstigst_stueck])} bis {komma(pro[teuerst_stueck])} Euro, und '
        f'hier wird es interessant: <strong>Das teuerste Set pro Hülse ist das am besten '
        f'bewertete, das günstigste pro Hülse das am schlechtesten bewertete.</strong> '
        f'Das Set {link(ts)} kostet {eur(ts["preis"])} für {stueckzahl(ts)} Hülsen, '
        f'also {komma(pro[ts["slug"]])} Euro je Stück, bei '
        f'{pd.sterne_text(ts["rating"])} Sternen. Das Set {link(gs)} kostet '
        f'{eur(gs["preis"])} für {stueckzahl(gs)} Hülsen, also '
        f'{komma(pro[gs["slug"]])} Euro je Stück, bei '
        f'{pd.sterne_text(gs["rating"])}.</p>\n'
        + absatz(
            (f'{gross(anteil(len(schw), n, "Sets"))} '
             f'{vb(len(schw), "liegt", "liegen")} unter {komma(3.8, 1)} Sternen. '
             if schw else '')
            + material_satz)
        + '    <p>Wofür die Hülsen überhaupt gut sind und wann sie nichts bringen, '
          'steht hier: <a href="/blog/finger-sleeves-sinnvoll/">Helfen Gaming Finger '
          'Sleeves wirklich?</a></p>\n'
    )


def trigger_text(rows, L):
    n = len(rows)
    bst = best(rows)
    teu, gue = teuerst(rows), guenstigst(rows)
    schw = schwache(rows)
    weg = nicht_kaufbar(rows)
    handy, tablet, ohne = handydicken(rows)
    tief, hoch, hoch_set = dicken_spanne(handy)
    obergrenze_satz = obergrenze(handy, hoch_set)
    tablet_satz = (f' {gross(mz(len(tablet), "Set", "Sets"))} '
                   f'{vb(len(tablet), "nennt", "nennen")} statt einer Handydicke eine '
                   f'Tablet-Angabe.') if tablet else ''
    # "darunter" setzt mehrere voraus; bei genau einem Set heisst es "und zwar".
    zusatz = ('' if best(rows) not in ohne else
              ', und zwar beim bestbewerteten' if len(ohne) == 1 else
              ', darunter beim bestbewerteten')
    ohne_satz = (f' Bei {mz_dativ(len(ohne), "Set", "Sets")} steht in unseren Daten gar '
                 f'keine Maßangabe{zusatz}.') if ohne else ''
    # Ohne Tablet-Fall und ohne Luecke gibt es nichts zu beklagen.
    # NICHT `lage` nennen: so hiess die lokale Variable zuerst und hat die Funktion
    # `lage()` aus dem Modulkopf verdeckt. Ein Namensstreit, der erst beim Lauf auffiel.
    datenlage = ('und hier ist unsere Datenlage lückenhaft'
                 if (tablet or ohne) else 'und unsere Daten decken das ab')
    vier = [r for r in rows if ausloeser(r) == 4]
    zwei = [r for r in rows if ausloeser(r) == 2]
    return (
        f'    <p>Trigger lösen ein Problem, das in PUBG Mobile sonst nichts anderes '
        f'löst: '
        f'Das Spiel sperrt Controller im normalen Matchmaking, Aufsätze, die physisch '
        f'auf das Display drücken, nicht. Wir führen {zw(n)} Sets von '
        f'{eur(gue["preis"])} bis {eur(teu["preis"])}'
        + (f', das günstigste davon ist {lage(weg[0])}' if weg else '')
        + '.</p>\n'
        f'    <p>Dasselbe Muster wie bei den Kühlern: <strong>Das teuerste Set ist das am '
        f'schlechtesten bewertete.</strong> Der {link(teu)} kostet {eur(teu["preis"])} '
        f'und steht bei {pd.sterne_text(teu["rating"])} aus '
        f'{pd.anzahl_text(teu["count"])} Bewertungen. Vorn liegt der {link(bst)} mit '
        f'{pd.sterne_text(bst["rating"])} aus {pd.anzahl_text(bst["count"])} Bewertungen '
        f'bei {eur(bst["preis"])}. Er ist das einzige unserer {zw(n)} Sets mit Lüfter und '
        f'Akku, deckt also die Kühlfrage gleich mit ab.</p>\n'
        + f'    <p><strong>Zwei oder vier Auslöser?</strong> '
          f'{gross(anteil(len(vier), n, "Sets"))} {vb(len(vier), "hat", "haben")} vier'
        + (f', {zwn(len(zwei))} {vb(len(zwei), "hat", "haben")} zwei' if zwei else '')
        + f'. Vier Auslöser sind die Voraussetzung für die 6-Finger-Steuerung.'
        + (' Zwei reichen, wenn nur Schießen und Zielen auf die Schultern wandern '
           'sollen.' if zwei else '')
        + '</p>\n'
        f'    <p><strong>Die Handydicke entscheidet, ob das Set überhaupt passt</strong>, '
        f'{datenlage}: {gross(anteil(len(handy), n, "Sets"))} '
        f'{vb(len(handy), "nennt", "nennen")} eine Handydicke, die Angaben '
        f'reichen von {tief} bis {hoch} Millimetern. {obergrenze_satz}'
        f'{tablet_satz}{ohne_satz} Miss dein Handy mit Hülle nach, bevor du bestellst: '
        f'Eine dicke Schutzhülle ist der häufigste Grund, warum ein Aufsatz nicht '
        f'greift.</p>\n'
        + (f'    <p>{gross(anteil(len(schw), n, "Sets"))} '
           f'{vb(len(schw), "liegt", "liegen")} unter {komma(3.8, 1)} Sternen und '
           f'{vb(len(schw), "ist", "sind")} deshalb in der Tabelle grau '
           f'hinterlegt.</p>\n' if schw else '')
        + '    <p>Welche Spiele Trigger erlauben und welche nicht, steht hier: '
          '<a href="/blog/trigger-erlaubt-pubg/">Sind Trigger bei PUBG Mobile '
          'erlaubt?</a></p>\n'
    )


def obergrenze(handy, hoch_set):
    """Der Nebensatz zur groessten Spanne.

    Gehoert sie einem Set, das man nicht bestellen kann, sagt der Satz das und nennt
    die Grenze unter den lieferbaren. Sonst nennt er nur das Set. Das ersetzt ein
    Gate, das vorher strenger war als der Text selbst und beim naechsten
    Lieferstatus-Wechsel rot geworden waere, obwohl der Satz sich schon richtig
    umgeschrieben haette (Pruefbericht 01.11., Hinweis 2).
    """
    if hoch_set['stock'] == 'ja':
        return f'Die größte Spanne hat der {link(hoch_set)}.'
    lieferbar = [b for _a, b, r in handy if r['stock'] == 'ja']
    if not lieferbar:
        return (f'Die Obergrenze gehört zum {link(hoch_set)}, der {lage(hoch_set)} '
                f'ist; unter den lieferbaren Sets nennt keines eine Handydicke.')
    return (f'Die Obergrenze gehört allerdings zum {link(hoch_set)}, der '
            f'{lage(hoch_set)} ist; unter den lieferbaren Sets endet die Reihe bei '
            f'{max(lieferbar)} Millimetern.')


def handydicken(rows):
    """Wer nennt eine Handydicke, wer eine Tablet-Dicke, wer gar nichts.

    Die erste Fassung hiess `dickenspanne()` und gab nur (min, max) zurueck. Daraus
    wurde der Satz "die Angaben unserer sieben Sets reichen von 3 bis 13 Millimetern"
    -- und der war dreifach falsch: Nur vier Sets nennen ueberhaupt eine Handydicke,
    eines nennt eine TABLET-Dicke, und zwei nennen gar nichts, darunter ausgerechnet
    das bestbewertete. Ein Schweigen im Datenkern ist kein Beleg (§A5), und die alte
    Fassung hat es als einen gelesen.

    Dazu kam ein stiller Filter: `w <= 30` sollte Zoll-Angaben fernhalten und haette
    einen echten 33-mm-Grip beim naechsten Abgleich lautlos verschluckt. Jetzt
    entscheidet das FELD ueber die Art der Angabe, nicht die Groesse der Zahl.
    """
    handy, tablet, ohne = [], [], []
    for r in rows:
        feld = spec_of(r, 'Für') or spec_of(r, 'Kompatibel')
        if not feld:
            ohne.append(r)
            continue
        # Ein Feld, das BEIDES nennt ("Smartphone/Tablet 5-13mm"), traegt eine
        # Handy-Angabe und gehoert nicht in den Tablet-Topf -- sonst faellt die
        # Handy-Angabe stillschweigend aus der Spanne.
        if re.search(r'(?i)tablet|ipad', feld) \
                and not re.search(r'(?i)smartphone|handy|phone', feld):
            tablet.append(r)
            continue
        werte = [int(x) for x in re.findall(r'(\d+)\s*(?:–|-|bis|mm)', feld)]
        if not werte:
            raise SystemExit(f'FEHLER: "{feld}" nennt keine lesbare Millimeter-Angabe '
                             f'({r["slug"]}) -- Text und Gate muessen angepasst werden')
        handy.append((min(werte), max(werte), r))
    if not handy:
        raise SystemExit('FEHLER: kein einziges Set nennt eine Handydicke')
    return handy, tablet, ohne


def dicken_spanne(handy):
    """(kleinste Untergrenze, groesste Obergrenze, Set mit der Obergrenze)."""
    tief = min(a for a, _b, _r in handy)
    hoch = max(handy, key=lambda t: t[1])
    return tief, hoch[1], hoch[2]


def passiv(rows):
    """Sets, deren Daten eine rein passive Uebertragung nennen (Mechanik, Kapazitiv,
    Kontakte). Alles andere wird NICHT als "braucht keinen Strom" gelesen."""
    out = []
    for r in rows:
        # Zwei Schreibweisen im Datenkern: die Bauart steht entweder als WERT unter
        # "Typ" ("USB-Kontakte", "Kapazitiv", "Mechanisch/Silikon") oder als eigenes
        # FELD "Kontakte" mit dem Wert "vergoldet". Die erste Fassung las nur Werte
        # und hat die beiden Sets mit Kontakte-Feld übersehen.
        if re.search(r'(?i)mechanisch|kapazitiv|kontakt', spec_of(r, 'Typ')) \
                or any(k.startswith('Kontakte') for k, _v in r['specs']):
            out.append(r)
    return out


def ausloeser(row):
    """Die Zahl der Ausloeser aus dem specs-Feld. Zwei Kategorien fuehren sie unter
    verschiedenen Schluesseln ("Auslöser", "Buttons", "Trigger")."""
    for anfang in ('Auslöser', 'Buttons', 'Trigger'):
        v = spec_of(row, anfang)
        if v:
            m = re.search(r'(\d+)', v)
            if m:
                return int(m.group(1))
    return None


def dickenspanne(rows):
    """Kleinste und groesste Millimeter-Angabe ueber alle Kompatibilitaets-Specs."""
    werte = []
    for r in rows:
        for k, v in r['specs']:
            if k.startswith(('Für', 'Kompatibel')):
                werte += [int(x) for x in re.findall(r'(\d+)\s*(?:–|-|bis|mm|Zoll)', v)
                          if 'Zoll' not in v[v.find(x):v.find(x) + 8]]
    werte = [w for w in werte if w <= 30]        # Zoll-Angaben sind keine Millimeter
    if not werte:
        raise SystemExit('FEHLER: keine Dicken-Angabe in den Trigger-Specs gefunden')
    return min(werte), max(werte)


def hub_text(alles, L):
    """Der Hub nennt, was die drei Kategorien unterscheidet, und den Befund, der
    sich durch zwei von ihnen zieht."""
    kue, sle, tri = alles['kuehler'], alles['finger-sleeves'], alles['trigger']
    n_ges = len(kue) + len(sle) + len(tri)
    umgekehrt = [k for k, rows in alles.items() if teuerst(rows) is schlechtest(rows)]
    schw_ges = sum(len(schwache(r)) for r in alles.values())
    meist = max(sle, key=lambda r: r['count'])
    return (
        f'    <p>Wir führen {zw(n_ges)} Zubehör-Artikel in {zw(len(alles))} Kategorien: '
        f'{zw(len(sle))} Sets <a href="/zubehoer/finger-sleeves/">Finger Sleeves</a> '
        f'({eur(guenstigst(sle)["preis"])} bis {eur(teuerst(sle)["preis"])}), '
        f'{zw(len(kue))} <a href="/zubehoer/handy-kuehler/">Handy-Kühler</a> '
        f'({eur(guenstigst(kue)["preis"])} bis {eur(teuerst(kue)["preis"])}) und '
        f'{zw(len(tri))} <a href="/zubehoer/trigger/">Trigger-Sets</a> '
        f'({eur(guenstigst(tri)["preis"])} bis {eur(teuerst(tri)["preis"])}).</p>\n'
        f'    <p><strong>Ein Befund zieht sich durch '
        f'{anteil(len(umgekehrt), len(alles), "Kategorien")}:</strong> Das teuerste '
        f'Produkt ist dort das am '
        f'schlechtesten bewertete. Bei den Kühlern trifft es den '
        f'{link(teuerst(kue))} für {eur(teuerst(kue)["preis"])} mit '
        f'{pd.sterne_text(teuerst(kue)["rating"])} Sternen, bei den Triggern den '
        f'{link(teuerst(tri))} für {eur(teuerst(tri)["preis"])} mit '
        f'{pd.sterne_text(teuerst(tri)["rating"])}. Nur bei den Finger Sleeves zahlt '
        f'sich der höhere Preis aus.</p>\n'
        + (f'    <p>Zubehör ist der Teil unseres Sortiments mit den schwächsten '
           f'Bewertungen: {anteil(schw_ges, n_ges, "Artikel")} '
           f'{vb(schw_ges, "liegt", "liegen")} unter {komma(3.8, 1)} Sternen. Wir '
           f'nehmen sie trotzdem auf, weil eine Kategorie ohne die schwachen Modelle '
           f'so aussieht, als gäbe es sie nicht. In den Tabellen der Unterseiten sind '
           f'sie grau hinterlegt.</p>\n' if schw_ges else '')
        + f'    <p>Der Gegenpol dazu steht in derselben Abteilung: Das Set {link(meist)} ist '
        f'mit {pd.anzahl_text(meist["count"])} Bewertungen das meistbewertete Produkt '
        f'unseres gesamten Sortiments.</p>\n'
    )


def kategorie_tabelle(alles):
    tr = []
    for key, rows in alles.items():
        k = KATEGORIEN[key]
        tr.append(
            f'      <tr><td><a href="/{os.path.dirname(k["datei"])}/">{k["wort"]}</a></td>'
            f'<td>{len(rows)}</td>'
            f'<td>{eur(guenstigst(rows)["preis"])} bis {eur(teuerst(rows)["preis"])}</td>'
            f'<td>{pd.sterne_text(best(rows)["rating"])}</td>'
            f'<td>{len(schwache(rows))}</td></tr>')
    return (
        '    <div class="zub-wrap"><table class="zub-table">\n'
        '      <thead><tr><th scope="col">Kategorie</th><th scope="col">Artikel</th>'
        '<th scope="col">Preisspanne</th><th scope="col">Beste Bewertung</th>'
        '<th scope="col">Unter 3,8</th></tr></thead>\n'
        '      <tbody>\n' + '\n'.join(tr) + '\n      </tbody>\n'
        '    </table></div>\n'
    )


# ---------------------------------------------------------------- FAQ

def faqs_kuehler(rows, L):
    bst, teu = best(rows), teuerst(rows)
    schw = schwache(rows)
    fragen = [
        ('Bringt ein Handy-Kühler wirklich etwas?',
         'Die Temperatur senkt er messbar. Ob daraus mehr Bilder pro Sekunde werden, '
         'hängt davon ab, ob dein Handy überhaupt wegen Hitze drosselt, und bei kurzen '
         'Runden tut es das meist nicht. Wir haben das in einem eigenen Artikel '
         'auseinandergenommen: <a href="/blog/handy-kuehler-sinnvoll/">Handy-Kühler: '
         'sinnvoll oder Hype?</a>'),
        ('Welcher Handy-Kühler ist der beste?',
         f'Nach der Bewertungslage in dieser Kategorie führt der '
         f'{bst["name"]} mit {pd.sterne_text(bst["rating"])} Sternen aus '
         f'{pd.anzahl_text(bst["count"])} Bewertungen bei {eur(bst["preis"])}. Der '
         f'teuerste Kühler bei uns ist nicht der beste: Der {teu["name"]} kostet '
         f'{eur(teu["preis"])} und steht bei {pd.sterne_text(teu["rating"])}.'),
        ('Peltier oder Lüfter: Was ist der Unterschied?',
         'Ein Lüfter bewegt Luft über die Rückseite, ein Peltier-Element kühlt die '
         'Kontaktfläche aktiv unter die Umgebungstemperatur. Peltier kühlt deutlich '
         f'stärker, braucht dafür aber durchgehend Strom. '
         f'{gross(anteil(len(rows), len(rows), "Kühler"))} in unserem Sortiment '
         f'{vb(len(rows), "arbeitet", "arbeiten")} mit einem Peltier-Element.'),
        ('Braucht ein Handy-Kühler eine Steckdose?',
         f'Eine Stromquelle braucht er in jedem Fall: '
         f'{gross(anteil(len(rows), len(rows), "Kühler"))} in unserem Sortiment '
         f'{vb(len(rows), "hängt", "hängen")} während des Spielens am USB-Kabel, und '
         f'{zwn(len(ohne_akku_belegt(rows)))} von ihnen '
         f'{vb(len(ohne_akku_belegt(rows)), "nennt", "nennen")} ausdrücklich, dass kein '
         f'eigener Akku verbaut ist. Wie viel Leistung die Quelle liefern muss, steht in '
         f'den Daten des jeweiligen Modells: beim {bst["name"]} '
         f'{spec_of(bst, "Anschluss")}.'),
    ]
    if schw:
        fragen.append(
            ('Warum führt ihr Kühler mit schwachen Bewertungen?',
             f'Weil {anteil(len(schw), len(rows), "Modelle")} in dieser Kategorie unter '
             f'{komma(3.8, 1)} Sternen {vb(len(schw), "liegt", "liegen")} und eine '
             f'Liste ohne sie so aussähe, als wäre das Angebot besser als es ist. Wir '
             f'kennzeichnen sie in der Tabelle und empfehlen sie nicht.'))
    return fragen


def faqs_sleeves(rows, L, alle):
    bst, sch = best(rows), schlechtest(rows)
    pro = {r['slug']: r['preis'] / stueckzahl(r) for r in rows if stueckzahl(r)}
    gross = max(rows, key=lambda r: stueckzahl(r) or 0)
    return [
        ('Was bringen Finger Sleeves beim Handy-Gaming?',
         'Sie halten Schweiß vom Display fern, damit der Daumen nicht kleben bleibt. '
         'Das ist kein Leistungsgewinn, sondern eine Reibungsfrage, spürbar vor allem '
         'in langen Runden und im Sommer. Mehr dazu: '
         '<a href="/blog/finger-sleeves-sinnvoll/">Helfen Gaming Finger Sleeves wirklich?</a>'),
        ('Welche Finger Sleeves sind die besten?',
         f'Das Set {bst["name"]}: {pd.sterne_text(bst["rating"])} Sterne aus '
         f'{pd.anzahl_text(bst["count"])} Bewertungen, die größte Bewertungsbasis '
         f'unseres gesamten Sortiments. Es kostet {eur(bst["preis"])} für '
         f'{stueckzahl(bst)} Hülsen, also {komma(pro[bst["slug"]])} Euro je Stück, und '
         f'ist damit das teuerste Set pro Stück, das wir führen.'),
        ('Sind teure Sleeves ihr Geld wert?',
         f'In dieser Kategorie deutet die Bewertungslage darauf hin: Das teuerste Set '
         f'pro Hülse ist das am besten bewertete, das günstigste pro Hülse das am '
         f'schlechtesten. Die Spanne reicht von {komma(min(pro.values()))} bis '
         f'{komma(max(pro.values()))} Euro pro Hülse. Bei unseren Kühlern und Triggern '
         'ist es übrigens genau andersherum.'),
        ('Wie viele Hülsen brauche ich?',
         f'Zwei pro Hand, also vier für die 4-Finger-Steuerung. Die Sets reichen von '
         f'{min(stueckzahl(r) for r in rows if stueckzahl(r))} bis '
         f'{stueckzahl(gross)} Stück. Gekauft wird also Vorrat, nicht Bedarf. '
         'Sie verschleißen und sind Verbrauchsmaterial.'),
    ]


def faqs_trigger(rows, L):
    bst, teu = best(rows), teuerst(rows)
    zwei = [r for r in rows if ausloeser(r) == 2]
    handy, tablet, ohne = handydicken(rows)
    tief, hoch, hoch_set = dicken_spanne(handy)
    weg = nicht_kaufbar(rows)
    fragen = [
        ('Sind Trigger in PUBG Mobile erlaubt?',
         'Ja. PUBG Mobile sperrt Controller im normalen Matchmaking, Trigger-Aufsätze '
         'nicht: Sie drücken physisch auf das Display und sind für das Spiel ein '
         'normaler Fingertipp. Ausführlich: '
         '<a href="/blog/trigger-erlaubt-pubg/">Sind Trigger bei PUBG Mobile '
         'erlaubt?</a>'),
        ('Brauchen Trigger Bluetooth oder einen Akku?',
         f'Meist nicht. {gross(anteil(len(passiv(rows)), len(rows), "Sets"))} '
         f'{vb(len(passiv(rows)), "überträgt", "übertragen")} den Druck laut Datenblatt '
         f'rein mechanisch, kapazitiv oder über Kontakte: aufstecken, fertig, ohne '
         f'Kopplung. {gross(mz(len(rows) - len(passiv(rows)), "Set", "Sets"))} '
         f'{vb(len(rows) - len(passiv(rows)), "nennt", "nennen")} darüber hinaus eigene '
         f'Technik, nämlich der {bst["name"]} einen '
         f'Lüfter mit Akku und der {teu["name"]} ein Schnellfeuer in '
         f'{spec_of(teu, "Schnellfeuer")}.'),
        ('Passen Trigger an jedes Handy?',
         f'Nein, die Dicke entscheidet'
         + (', und unsere Daten decken das nicht lückenlos ab' if (tablet or ohne)
            else '')
         + f': {gross(anteil(len(handy), len(rows), "Sets"))} '
         f'{vb(len(handy), "nennt", "nennen")} eine Handydicke, sie reichen von {tief} '
         f'bis {hoch} Millimetern. {obergrenze(handy, hoch_set)}'
         + (f' {gross(mz(len(tablet), "Set", "Sets"))} '
            f'{vb(len(tablet), "nennt", "nennen")} eine Tablet-Angabe.' if tablet else '')
         + (f' {gross(mz(len(ohne), "Set", "Sets"))} '
            f'{vb(len(ohne), "nennt", "nennen")} gar keine.' if ohne else '')
         + ' Miss dein Handy mit Hülle, nicht ohne: Eine dicke Schutzhülle ist der '
           'häufigste Grund, warum ein Aufsatz nicht greift.'),
        ('Welcher Trigger ist der beste?',
         f'Der {bst["name"]}: {pd.sterne_text(bst["rating"])} Sterne aus '
         f'{pd.anzahl_text(bst["count"])} Bewertungen bei {eur(bst["preis"])}. Das '
         f'teuerste Trigger-Set bei uns ist nicht das beste: Der {teu["name"]} '
         f'kostet {eur(teu["preis"])} und steht bei {pd.sterne_text(teu["rating"])}.'
         + (f' Der {weg[0]["name"]} ist {lage(weg[0])}.' if weg else '')),
    ]
    # Die Frage "zwei oder vier?" ergibt nur Sinn, solange es beide Bestueckungen
    # gibt. Ohne ein Zweier-Set riete die Antwort zu etwas, das wir nicht fuehren.
    if zwei:
        fragen.insert(3, (
            'Zwei oder vier Auslöser?',
            f'Vier, wenn du die 6-Finger-Steuerung lernen willst. Zwei reichen, wenn '
            f'nur Schießen und Zielen auf die Schultern sollen. Vier Auslöser '
            f'{vb(len(rows) - len(zwei), "hat", "haben")} '
            f'{anteil(len(rows) - len(zwei), len(rows), "unserer Trigger-Sets")}.'))
    return fragen


def faqs_hub(alles, L):
    n_ges = sum(len(r) for r in alles.values())
    schw_ges = sum(len(schwache(r)) for r in alles.values())
    meist = max(alles['finger-sleeves'], key=lambda r: r['count'])
    fragen = [
        ('Welches Zubehör lohnt sich fürs Handy-Gaming wirklich?',
         'Das hängt vom Problem ab. Schwitzige Finger lösen '
         '<a href="/zubehoer/finger-sleeves/">Finger Sleeves</a> für wenige Euro. '
         'Fehlende Schultertasten lösen '
         '<a href="/zubehoer/trigger/">Trigger-Aufsätze</a>, die PUBG Mobile anders '
         'als Controller im normalen Matchmaking nicht sperrt. '
         '<a href="/zubehoer/handy-kuehler/">Kühler</a> lohnen sich nur, wenn dein '
         'Handy tatsächlich wegen Hitze drosselt.'),
        ('Was ist das meistbewertete Zubehör?',
         f'Das Set {meist["name"]} mit {pd.anzahl_text(meist["count"])} '
         f'Amazon-Bewertungen bei {pd.sterne_text(meist["rating"])} Sternen. Es ist '
         f'damit nicht nur das '
         'meistbewertete Zubehör, sondern das meistbewertete Produkt unseres gesamten '
         'Sortiments.'),
    ]
    if schw_ges:
        fragen.append(
            ('Warum stehen bei euch Produkte mit schlechten Bewertungen?',
             f'{gross(anteil(schw_ges, n_ges, "Zubehör-Artikel"))} '
             f'{vb(schw_ges, "liegt", "liegen")} unter {komma(3.8, 1)} Sternen. Wir '
             f'führen sie mit Kennzeichnung statt sie wegzulassen, weil eine Kategorie '
             f'ohne ihre schwachen Modelle vollständiger aussieht als sie ist. '
             f'Empfohlen werden sie nicht.'))
    return fragen


# ---------------------------------------------------------------- Rendering

def faq_block(paare, titel):
    items = '\n'.join(
        f'      <details class="faq-item"><summary>{q}</summary>'
        f'<div class="faq-a">{a}</div></details>'
        for q, a in paare)
    return (
        '  <section class="section"><div class="container zub-ext" style="max-width:820px">\n'
        f'    <h2>{titel}</h2>\n'
        '    <div class="faq-list">\n' + items + '\n    </div>\n'
        '  </div></section>\n')


def strip_tags(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).strip()


def karten_slugs(html):
    """Die Produktkarten der Seite in ihrer sichtbaren Reihenfolge."""
    out = []
    for m in re.finditer(r'<article class="pcard[^"]*"[^>]*>.*?</article>', html, re.S):
        s = re.search(r'data-product="([^"]+)"', m.group(0))
        if not s:
            raise SystemExit('FEHLER: Produktkarte ohne data-product — Reihenfolge nicht '
                             'bestimmbar')
        out.append(s.group(1))
    return out


def itemlist_schema(html, rows, listenname, canonical):
    """ItemList aus der SICHTBAREN Kartenreihenfolge, Namen aus products.json.

    Nicht aus der Produktliste gerendert, sondern aus der Seite: Ein Schema, das
    eine andere Reihenfolge behauptet als die Karten, ist §A4-Verstoss am Kern.
    """
    slugs = karten_slugs(html)
    nach_slug = {r['slug']: r for r in rows}
    fehlt = [s for s in slugs if s not in nach_slug]
    if fehlt:
        raise SystemExit(f'FEHLER: Karte(n) {fehlt} gehoeren nicht zu dieser Kategorie')
    fehlend = [r['slug'] for r in rows if r['slug'] not in slugs]
    if fehlend:
        raise SystemExit(f'FEHLER: {fehlend} steht in products.json, aber nicht als Karte '
                         f'auf der Seite')
    elemente = [{'@type': 'ListItem', 'position': i,
                 'name': nach_slug[s]['name'],
                 'url': 'https://smartphone-controller.com' + nach_slug[s]['detail']}
                for i, s in enumerate(slugs, 1)]
    return json.dumps({'@context': 'https://schema.org', '@type': 'ItemList',
                       'name': listenname, 'url': canonical,
                       'numberOfItems': len(elemente),
                       'itemListElement': elemente}, ensure_ascii=False)


def faqpage_schema(block):
    """FAQPage aus den sichtbaren details-Bloecken des erzeugten Blocks (§A4)."""
    items = re.findall(
        r'<details class="faq-item"><summary>(.*?)</summary>'
        r'<div class="faq-a">(.*?)</div></details>', block, re.S)
    if not items:
        raise SystemExit('FEHLER: kein FAQ-Eintrag im erzeugten Block')
    return json.dumps(
        {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': strip_tags(q),
                         'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}}
                        for q, a in items]}, ensure_ascii=False)


# ---------------------------------------------------------------- Gates

def allowed_numbers(rows, extra, gesamt):
    """Jede Zahl, die der Text dieser Seite tragen darf.

    Bewusst ENG: Es zaehlen die Preise, Bewertungen und Spec-Werte der Produkte
    DIESER Kategorie, dazu die ausdruecklich genannten Fremdprodukte und die
    abgeleiteten Stueckzahlen. Nicht die Daten aller 42 Produkte — ein Gate, das
    fast jede Zahl durchlaesst, ist keins (Lehre aus `_abgeleitet()` am 06.10.,
    das 96 bis 100 Prozent aller Zahlen von 1 bis 2000 erlaubt hat).
    """
    ok = set(FREIE_ZAHLEN)
    ok.add(str(gesamt))          # "keins der 42 Produkte" — Umfang des Sortiments
    for r in list(rows) + list(extra):
        ok.add(str(r['preis']))
        ok.add(pd.sterne_text(r['rating']))
        ok.add(pd.anzahl_text(r['count']))
        ok.add(str(r['count']))
        for _k, v in r['specs']:
            ok |= set(re.findall(r'\d+(?:[.,]\d+)?', v))
        ok |= set(re.findall(r'\d+(?:[.,]\d+)?', r['claim']))
        st = stueckzahl(r)
        if st:
            ok.add(komma(r['preis'] / st))
    # Anzahlen: wie viele Produkte die Kategorie hat, wie viele schwach sind usw.
    for n in range(0, len(rows) + 1):
        ok.add(str(n))
    return ok


# Masseinheiten, bei denen die Zahl ALLEIN nichts beweist: "40" steht als Set-Groesse
# in den Daten, "40 Stunden Akku" steht nirgends -- und genau diese Form ist in diesem
# Projekt schon live gegangen. Fuer diese Einheiten wird das PAAR geprueft.
#
# GRENZE, benannt statt verschwiegen: Das ist und bleibt eine von Hand gepflegte
# Positivliste. Eine Einheit, die hier fehlt, wird NICHT geprueft -- die Zahl muss dann
# nur fuer sich belegt sein. Der Pruefbericht vom 01.11. hat das an "18 Dezibel"
# gezeigt; die Einheit steht seitdem drin, das Prinzip bleibt. Wer eine neue Einheit in
# den Text schreibt, traegt sie hier ein.
#
# Zwei Versuche, die Liste ueberfluessig zu machen, sind gescheitert und stehen hier,
# damit sie niemand ein drittes Mal unternimmt:
#   1. Jedes Wort hinter einer Zahl als Einheit lesen. Meldete "3,3 aus", "6 weg" und
#      "77 Controller" und waere mit Ausnahmen aufgeweicht worden, bis nichts bleibt.
#   2. Die Liste aus dem Datenkern ernten. Liefert aus "Smartphone bis 11mm" und
#      "L1R1/L2R2" die Pseudo-Einheiten "bis" und "r" und machte damit den eigenen,
#      korrekten Satz "3 bis 13 Millimetern" rot.
_EINHEIT_NORM = {
    'mm': 'millimeter', 'millimeter': 'millimeter', 'millimetern': 'millimeter',
    'cm': 'zentimeter', 'zentimeter': 'zentimeter',
    'g': 'gramm', 'gramm': 'gramm', 'kg': 'kilogramm', 'kilogramm': 'kilogramm',
    'w': 'watt', 'watt': 'watt', 'v': 'volt', 'volt': 'volt',
    'mah': 'mah', 'wh': 'wattstunden',
    'std': 'stunden', 'stunde': 'stunden', 'stunden': 'stunden',
    'minute': 'minuten', 'minuten': 'minuten', 'min': 'minuten',
    'sekunde': 'sekunden', 'sekunden': 'sekunden', 'ms': 'millisekunden',
    'tag': 'tage', 'tage': 'tagen', 'tagen': 'tagen',
    'monat': 'monate', 'monate': 'monate', 'monaten': 'monate',
    'jahr': 'jahre', 'jahre': 'jahre', 'jahren': 'jahre',
    'grad': 'grad', '°c': 'grad', '°': 'grad', 'kelvin': 'kelvin',
    '%': 'prozent', 'prozent': 'prozent',
    'hz': 'hertz', 'hertz': 'hertz', 'fps': 'fps',
    'db': 'dezibel', 'dezibel': 'dezibel',
    'zoll': 'zoll',
}


def masse(text):
    """Alle (Zahl, Mass)-Paare eines Textes, Bereiche aufgeloest.

    "5-13mm" liefert (5, millimeter) UND (13, millimeter): Eine Spanne belegt beide
    Enden. Ohne diese Zeile waere die Obergrenze aus den Trigger-Specs unbelegt und
    das Gate haette den eigenen, korrekten Satz rot gemacht.
    """
    t = re.sub(r'<[^>]+>', ' ', text).lower().replace('\u2009', ' ')
    zahl = r'(\d+(?:[.,]\d+)?)'
    wort = r'([a-zäöüß°%]{1,12})'
    paare = set()
    for a_, b_, u in re.findall(zahl + r'\s*(?:–|-|bis)\s*' + zahl + r'\s*' + wort, t):
        if u in _EINHEIT_NORM:
            paare |= {(a_, _EINHEIT_NORM[u]), (b_, _EINHEIT_NORM[u])}
    for z, u in re.findall(zahl + r'\s*(?:≥|≤|<|>)?\s*' + wort, t):
        if u in _EINHEIT_NORM:
            paare.add((z, _EINHEIT_NORM[u]))
    return paare


def check_units(block, rows, extra, wo):
    """Jedes Mass im Text muss als dasselbe Mass in products.json stehen."""
    quelle = ' '.join(
        ' '.join(v for _k, v in r['specs']) + ' ' + r['claim']
        for r in list(rows) + list(extra))
    offen = sorted(masse(block) - masse(quelle))
    if offen:
        raise SystemExit(
            f'MASS-GATE ({wo}): Angabe(n) ohne Deckung in products.json: '
            + ', '.join(f'{z} {u}' for z, u in offen))


def check_numbers(block, rows, extra, wo, gesamt):
    """§A1-Drift-Gate: Jede Zahl im erzeugten Text muss aus products.json kommen."""
    check_units(block, rows, extra, wo)
    plain = re.sub(r'<[^>]+>', ' ', block)
    # Produktnamen tragen selbst Ziffern (FunCooler 6, AK77, L1R1, GXT 735G) und sind
    # keine Messwerte. Laengste zuerst, sonst frisst ein kurzer Name den langen an.
    for nm in sorted({r['name'] for r in list(rows) + list(extra)}
                     | {r['kurz'] for r in list(rows) + list(extra)},
                     key=len, reverse=True):
        plain = plain.replace(nm, ' ')
    # Spielnamen und Steuerungs-Begriffe mit Ziffer sind ebenfalls keine Messwerte.
    plain = re.sub(r'\b(PUBG|CoD)\b', ' ', plain)
    plain = plain.replace('6-Finger-Steuerung', ' ').replace('4-Finger-Steuerung', ' ')

    ok = allowed_numbers(rows, extra, gesamt)
    # Token-Regel: nie \b. "4" aus "4,4" und "157" aus einer Bewertungszahl zu lesen
    # war am 06.10. der Fehler, der das halbe Gate wertlos gemacht hat.
    gefunden = re.findall(r'(?<![\w,.-])(\d+(?:[.,]\d+)?)(?![\w,.-])', plain)
    unbelegt = sorted({g for g in gefunden if g not in ok})
    if unbelegt:
        raise SystemExit(
            f'DRIFT-GATE ({wo}): Zahl(en) ohne Deckung in products.json: '
            f'{", ".join(unbelegt)}\n'
            f'   Entweder aus den Daten ziehen oder in FREIE_ZAHLEN aufnehmen.')


def check_claims(alles, L):
    """Die Vergleichsaussagen gegen die Daten nachrechnen.

    Das Drift-Gate prueft nur, ob eine ZAHL belegt ist. Hier geht es darum, ob die
    AUSSAGE noch traegt. Am 30.09. kippte der Amazon-Abgleich zwei Saetze, obwohl
    jede Zahl darin korrekt war.
    """
    kue, sle, tri = alles['kuehler'], alles['finger-sleeves'], alles['trigger']
    alle = L.alle
    f = []

    # Kuehler-Seite
    if teuerst(kue) is not schlechtest(kue):
        f.append('Kühler: das teuerste Modell ist nicht mehr das schlechtest bewertete')
    if best(kue) is teuerst(kue) or best(kue) is guenstigst(kue):
        f.append('Kühler: der bestbewertete liegt nicht mehr preislich in der Mitte')
    if not all('Peltier' in spec_of(r, 'Typ') for r in kue):
        f.append('Kühler: nicht mehr alle arbeiten mit einem Peltier-Element')
    if not all(spec_of(r, 'Anschluss').startswith('USB') for r in kue):
        f.append('Kühler: nicht mehr alle hängen am USB-Kabel')
    # Der Satz nennt zwei Kuehler mit ausdruecklicher Akku-Verneinung und einen, bei
    # dem nur ein Netzteil in den Daten steht. Beide Haelften werden gemessen.
    ohne = ohne_akku_belegt(kue)
    if len(ohne) != 2:
        f.append(f'Kühler: nicht mehr genau zwei Modelle verneinen den Akku '
                 f'ausdrücklich, sondern {len(ohne)} — der Text sagt "zwei von ihnen"')
    rest = [r for r in kue if r not in ohne]
    if len(rest) != 1 or 'Netzteil' not in spec_of(rest[0], 'Anschluss'):
        f.append('Kühler: beim dritten Modell steht kein Netzteil mehr in den Daten, '
                 'der Satz "beim dritten nennen unsere Daten ein Netzteil" trägt nicht')
    mit_akku = [r for r in kue
                if re.search(r'(?<![\w-])Akku(?![\w-])',
                             ' '.join(v for _k, v in r['specs']) + ' ' + r['claim'])
                and r not in ohne]
    if mit_akku:
        f.append(f'Kühler: {[r["slug"] for r in mit_akku]} führt jetzt einen Akku, '
                 f'der Text schließt Akkus in dieser Kategorie aber aus')
    # "nur beim AK77" ist eine Exklusivaussage und wird gemessen, nicht geglaubt.
    luefter_akku = [r for rows in alles.values() for r in rows
                    if re.search(r'(?<![\w-])Akku(?![\w-])',
                                 ' '.join(v for _k, v in r['specs']))
                    and 'kein Akku' not in ' '.join(v for _k, v in r['specs'])
                    and 'Lüfter' in ' '.join(v for _k, v in r['specs'])]
    if [r['slug'] for r in luefter_akku] != ['ozkak-trigger-set']:
        f.append('Zubehör: "Kühlung und Akku nur beim AK77" stimmt nicht mehr, '
                 f'gefunden: {[r["slug"] for r in luefter_akku]}')

    # Sleeves-Seite
    if pd.text(teuerst(alle)['p'], 'type') != 'controller':
        f.append('Sleeves: das teuerste Produkt des Sortiments ist kein Controller '
                 'mehr, der Satz "kein Controller für X Euro" trägt dann nicht')
    meist_alle = max(alle, key=lambda r: r['count'])
    if meist_alle['slug'] != best(sle)['slug']:
        f.append('Sleeves: das meistbewertete Produkt des Sortiments ist nicht mehr '
                 f'das bestbewertete Sleeve-Set, sondern {meist_alle["slug"]}')
    if best(sle) is not max(sle, key=lambda r: r['count']):
        f.append('Sleeves: das bestbewertete Set ist nicht mehr auch das meistbewertete')
    pro = {r['slug']: r['preis'] / stueckzahl(r) for r in sle if stueckzahl(r)}
    if len(pro) != len(sle):
        f.append('Sleeves: ein Set hat keine Stückzahl mehr, der Preis pro Hülse '
                 'ist dann nicht berechenbar')
    else:
        if max(pro, key=pro.get) != best(sle)['slug']:
            f.append('Sleeves: das teuerste Set pro Hülse ist nicht mehr das '
                     'bestbewertete')
        if min(pro, key=pro.get) != schlechtest(sle)['slug']:
            f.append('Sleeves: das günstigste Set pro Hülse ist nicht mehr das '
                     'schlechtest bewertete')
    # Kein Gate mehr darauf, dass genau das Polyester-Set das schlechteste ist: Der
    # Material-Satz nennt seit Runde 5 beide Bewertungsspannen aus den Daten, statt
    # das schlechteste Set als "das Polyester-Set" auszugeben. Das Gate wuerde jetzt
    # nur noch eine korrekte Datenaenderung blockieren.
    # Kein Gate auf die Zahl der schwachen Sets: Der Satz nennt sie aus den Daten,
    # entfaellt bei null ganz und beugt Verb und Zahlwort selbst. Ein Gate haette hier
    # nur die naechste Bewertungsaenderung blockiert.

    # Trigger-Seite
    if teuerst(tri) is not schlechtest(tri):
        f.append('Trigger: das teuerste Set ist nicht mehr das schlechtest bewertete')
    if 'Lüfter' not in ' '.join(v for _k, v in best(tri)['specs']):
        f.append('Trigger: der bestbewertete bringt keinen Lüfter mehr mit')
    weg = nicht_kaufbar(tri)
    if len(weg) > 1:
        f.append(f'Trigger: {len(weg)} Sets sind nicht kaufbar, der Text nennt nur eins')
    # Die Preisspanne beginnt bei einem Set, das man nicht kaufen kann. Das steht so
    # im Satz ("das günstigste davon") und muss deshalb auch so bleiben: Sonst liest
    # die Seite "ab 9 Euro" und verschweigt, dass es diese neun Euro nicht gibt.
    if weg and weg[0] is not guenstigst(tri):
        f.append('Trigger: das nicht kaufbare Set ist nicht mehr das günstigste, der '
                 'Satz "das günstigste davon ist derzeit nicht kaufbar" trägt nicht')
    # Ebenso bei den Triggern: der Absatz steht unter Bedingung und beugt sich selbst.
    vier = [r for r in tri if ausloeser(r) == 4]
    zwei = [r for r in tri if ausloeser(r) == 2]
    if len(vier) + len(zwei) != len(tri):
        f.append('Trigger: nicht jedes Set hat zwei oder vier Auslöser in den Specs')
    if len(vier) <= len(zwei):
        f.append('Trigger: vier Auslöser sind nicht mehr die Regel im Sortiment')

    # Trigger: die Dicken-Aussage nennt drei Mengen und eine Obergrenze. Alle vier
    # Teile werden gemessen, weil der Satz vorher aus einem Schweigen eine Zusage
    # gemacht hat (Pruefbericht 01.11., Blocker 3).
    handy, tablet, ohne = handydicken(tri)
    if len(handy) + len(tablet) + len(ohne) != len(tri):
        f.append('Trigger: die Dicken-Zuordnung deckt nicht mehr alle Sets ab')
    # Keine Gates auf die drei Mengenstaerken: Substantiv und Verb kommen aus `mz()`
    # und `vb()`, der Zusatz "darunter beim bestbewerteten" steht unter Bedingung, und
    # fehlende Mengen lassen ihren Satz ganz weg. Ein Gate haette hier nur die
    # naechste korrekte Datenpflege blockiert (Pruefbericht 01.11., Blocker 1).
    # Kein Gate auf die Lieferbarkeit der Obergrenze: `obergrenze()` schreibt den
    # Nebensatz aus der Datenlage und deckt alle drei Faelle ab.

    # Trigger: "fuenf uebertragen passiv, zwei nennen eigene Technik"
    pas = passiv(tri)
    rest_tri = [r for r in tri if r not in pas]
    if {r['slug'] for r in rest_tri} != {best(tri)['slug'], teuerst(tri)['slug']}:
        f.append(f'Trigger: die beiden Sets mit eigener Technik sind nicht mehr das '
                 f'bestbewertete und das teuerste, sondern '
                 f'{[r["slug"] for r in rest_tri]}')
    if not spec_of(teuerst(tri), 'Schnellfeuer'):
        f.append('Trigger: das teuerste Set nennt kein Schnellfeuer mehr, der Satz '
                 'über seine eigene Technik trägt nicht')

    # Sleeves: der Text nennt jetzt den Zweitplatzierten mit Zahl
    rang = sorted(alle, key=lambda r: -r['count'])
    if rang[0]['slug'] != best(sle)['slug']:
        f.append('Sleeves: der Spitzenreiter nach Bewertungszahl ist nicht mehr das '
                 'bestbewertete Sleeve-Set')
    if rang[1]['count'] >= rang[0]['count']:
        f.append('Sleeves: Platz eins und zwei nach Bewertungszahl sind gleichauf')

    # Hub
    umgekehrt = [k for k, rows in alles.items() if teuerst(rows) is schlechtest(rows)]
    if set(umgekehrt) != {'kuehler', 'trigger'}:
        f.append(f'Hub: die Preis-Umkehr gilt nicht mehr für Kühler und Trigger, '
                 f'sondern für {umgekehrt}')
    if teuerst(sle) is not best(sle):
        f.append('Hub: bei den Finger Sleeves zahlt sich der höhere Preis nicht mehr aus')

    if f:
        raise SystemExit('AUSSAGEN-GATE: Der Text behauptet etwas, das die Daten nicht '
                         'mehr hergeben:\n   ' + '\n   '.join(f))


# ---------------------------------------------------------------- Anwendung

class Lookup:
    def __init__(self, products):
        self.alle = [zeile(p) for p in products]
        self._by = {r['slug']: r for r in self.alle}

    def __call__(self, slug):
        if slug not in self._by:
            raise SystemExit(f'FEHLER: Produkt "{slug}" fehlt in products.json')
        return self._by[slug]['p']


def block_fuer(key, alles, L, html, canonical):
    """Der komplette Marker-Block einer Seite."""
    if key == 'hub':
        prosa = (
            '  <section class="section"><div class="container zub-ext" style="max-width:820px">\n'
            '    <h2>Welches Zubehör lohnt sich fürs Handy-Gaming?</h2>\n'
            + hub_text(alles, L) +
            '    <h3>Die drei Kategorien im Überblick</h3>\n'
            + kategorie_tabelle(alles) +
            '  </div></section>\n')
        faq = faq_block(faqs_hub(alles, L), 'Häufige Fragen zu Gaming-Zubehör')
        itemlist = None
        # Der Hub spricht ueber alle drei Kategorien, also sind alle 14 Artikel seine
        # Datenbasis. Als `extra` gefuehrt waeren sie es auch gewesen, aber dann haette
        # das Drift-Gate die Anzahlen in der Kategorietabelle (3, 4, 7) nur zufaellig
        # durchgelassen -- ueber Ziffern aus Spec-Strings wie "4 (L1R1/L2R2)".
        rows, extra = [r for _rows in alles.values() for r in _rows], []
    else:
        rows = alles[key]
        k = KATEGORIEN[key]
        if key == 'kuehler':
            txt, faqs = kuehler_text(rows, L), faqs_kuehler(rows, L)
            h2 = 'Handy-Kühler kaufen: Darauf kommt es an'
            spalte, wert = 'Typ', lambda r: spec_of(r, 'Typ')
            # Der Text nennt den AK77 als einzige Kuehlung mit Akku: seine Zahlen
            # muessen deshalb im Drift-Gate erlaubt sein.
            extra = [L_zeile(L, 'ozkak-trigger-set')]
        elif key == 'finger-sleeves':
            txt = sleeves_text(rows, L, L.alle)
            faqs = faqs_sleeves(rows, L, L.alle)
            h2 = 'Finger Sleeves kaufen: Darauf kommt es an'
            spalte, wert = 'Material · Set', \
                lambda r: f'{spec_of(r, "Material")} · {spec_of(r, "Set")}'
            extra = [teuerst(L.alle), sorted(L.alle, key=lambda r: -r['count'])[1]]
        else:
            txt, faqs = trigger_text(rows, L), faqs_trigger(rows, L)
            h2 = 'Trigger-Aufsätze kaufen: Darauf kommt es an'
            spalte, wert = 'Auslöser', lambda r: spec_of(r, 'Auslöser') or spec_of(r, 'Buttons') \
                or spec_of(r, 'Trigger')
            extra = []
        prosa = (
            '  <section class="section"><div class="container zub-ext" style="max-width:820px">\n'
            f'    <h2>{h2}</h2>\n' + txt +
            f'    <h3>{gross(anteil(len(rows), len(rows), k["plural"]))} im Vergleich</h3>\n'
            + tabelle(rows, spalte, wert) +
            '  </div></section>\n')
        faq = faq_block(faqs, f'Häufige Fragen zu {k["dativ"]}')
        itemlist = itemlist_schema(html, rows, k['listenname'], canonical)

    inhalt = prosa + faq
    schemas = ''
    if itemlist:
        schemas += f'<script type="application/ld+json">\n{itemlist}\n</script>\n'
    schemas += f'<script type="application/ld+json">\n{faqpage_schema(inhalt)}\n</script>\n'
    return f'{START}\n{inhalt}{schemas}{END}\n', rows, extra


def L_zeile(L, slug):
    return next(r for r in L.alle if r['slug'] == slug)


def apply_to_file(path, key, alles, L):
    with open(path, encoding='utf-8') as f:
        original = f.read()
    html = original

    # 1. Alten Block entfernen (Idempotenz). Das nachgestellte \n gehoert zum
    #    Einfuegemuster und muss mit weg, sonst waechst die Datei bei jedem Lauf.
    html = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', html, flags=re.S)
    html = re.sub(re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?', '', html, flags=re.S)

    # 2. Seiten-CSS vor </head>
    if '</head>' not in html:
        raise SystemExit(f'FEHLER: kein </head> in {path}')
    html = html.replace('</head>', CSS + '\n</head>', 1)

    # 3. Block vor </main>. Die vier Seiten enden unterschiedlich eingerueckt, der
    #    Anker ist deshalb </main> selbst und nicht die Zeile davor.
    if '</main>' not in html:
        raise SystemExit(f'FEHLER: kein </main> in {path}')
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    if not canonical:
        raise SystemExit(f'FEHLER: kein canonical in {path}')
    block, rows, extra = block_fuer(key, alles, L, html, canonical.group(1))
    html = html.replace('</main>', block + '</main>', 1)

    # 4. Selbstkontrolle am ENDSTAND, nicht an den Bausteinen. Die Markup-Pruefung
    #    an der Vorstufe zu haengen hat am 06.10. zwei Fehlalarme erzeugt.
    assert html.count(START) == 1 and html.count(END) == 1, 'Block nicht genau einmal da'
    assert html.count(CSS_START) == 1 and html.count(CSS_END) == 1, 'CSS nicht genau einmal da'
    erzeugt = re.search(re.escape(START) + r'(.*?)' + re.escape(END), html, re.S).group(1)

    # Jede Klasse im erzeugten Markup braucht eine Regel — hier oder global.
    for klasse in sorted({c for attr in re.findall(r'class="([^"]+)"', erzeugt)
                          for c in attr.split()}):
        if klasse in GLOBAL_KLASSEN:
            continue
        assert f'.{klasse}' in CSS, f'CSS-Regel fehlt fuer .{klasse}'

    n_details = erzeugt.count('<details class="faq-item">')
    n_fragen = erzeugt.count('"@type": "Question"')
    assert n_details == n_fragen, f'FAQ-Drift: {n_details} sichtbar, {n_fragen} im Schema'
    assert '—' not in erzeugt, 'Em-Dash im erzeugten Text (verboten laut CLAUDE.md)'

    check_numbers(erzeugt, rows, extra, os.path.relpath(path, ROOT), len(L.alle))
    return original, html


def main():
    check = '--check' in sys.argv
    products = load_products()
    L = Lookup(products)
    alles = {k: rows_of(products, k) for k in KATEGORIEN}
    check_claims(alles, L)

    ziele = [(os.path.join(ROOT, v['datei']), k) for k, v in KATEGORIEN.items()]
    ziele.append((os.path.join(ROOT, HUB), 'hub'))

    geaendert = []
    for path, key in ziele:
        if not os.path.exists(path):
            raise SystemExit(f'FEHLER: {path} fehlt')
        original, html = apply_to_file(path, key, alles, L)
        rel = os.path.relpath(path, ROOT)
        if html != original:
            geaendert.append(rel)
            if not check:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html)
        woerter = len(strip_tags(re.search(r'<main>(.*)</main>', html, re.S).group(1)).split())
        print(f'  {rel:<34} {woerter:>4} Wörter · '
              f'{html.count(chr(60) + "details class=" + chr(34) + "faq-item")} FAQs · '
              f'{"geändert" if html != original else "unverändert"}')

    if check:
        print(f'\n[--check] {len(geaendert)} Datei(en) wären geändert worden: '
              f'{", ".join(geaendert) or "keine"}')
    else:
        print(f'\n{len(geaendert)} Zubehör-Seite(n) geschrieben: '
              f'{", ".join(geaendert) or "keine"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
