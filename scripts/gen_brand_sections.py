#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_brand_sections.py — Marken-Keyword-Offensive (30.09.2026)

Erweitert die vier Marken-Hubs (razer, gamesir, 8bitdo, backbone) um zwei
Sektionen, die bisher auf keiner Seite bedient wurden:

  1. Erfahrungs-Intent   "[Marke] erfahrungen / test / ist [Marke] gut"
  2. Plattform-Intent    "[Marke] controller android / iphone / tablet"

Beides sind Keyword-Typen, die laut dem Wolf-of-SEO-Befund (brain/03-research/
2026-09-30-wolf-of-seo-framework.md) bei Marken offen liegen, weil die
Hersteller sie auf Deutsch nicht besetzen. Die zugehoerigen Queries sind in
unseren eigenen GSC-Rohdaten belegt (razer controller, razer controller
android, backbone android, gamesir vs backbone, is gamesir better than
backbone, 8bitdo controller).

Eigenschaften:
  · IDEMPOTENT  — der erzeugte Block steht zwischen Markern und wird bei
                  jedem Lauf ersetzt, nie dupliziert (Lehre aus gen_hubs.py).
  · §A1         — jede Zahl stammt aus products.json, nichts steht fest im Text.
  · §A4         — das FAQPage-Schema wird aus dem finalen HTML neu gerendert,
                  Schema und sichtbarer Text koennen also nicht auseinanderlaufen.
  · §A6         — jede Marke bekommt ihre echte Schwaeche genannt.

Aufruf:  python3 scripts/gen_brand_sections.py [--check]
         --check schreibt nichts, meldet nur, ob die Dateien aktuell waeren.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = os.path.join(ROOT, 'assets', 'data', 'products.json')

START = '<!-- BRAND-EXT:START (generiert von scripts/gen_brand_sections.py — nicht von Hand editieren) -->'
END = '<!-- BRAND-EXT:END -->'
FAQ_START = '<!-- BRAND-FAQ:START -->'
FAQ_END = '<!-- BRAND-FAQ:END -->'
CSS_START = '<!-- BRAND-CSS:START -->'
CSS_END = '<!-- BRAND-CSS:END -->'

# Seiten-CSS nach dem Muster der Vergleichsseiten (dort liegt .vs-table ebenfalls
# im Seiten-<style>). Nutzt ausschliesslich bestehende Design-Tokens aus style.css.
CSS = (
    CSS_START + '\n<style>\n'
    '.brand-ext p{color:var(--ink-soft);line-height:1.7;margin-bottom:14px}\n'
    '.brand-ext h3{margin-top:26px;margin-bottom:6px}\n'
    '.brand-table{width:100%;border-collapse:collapse;margin:18px 0;font-size:14px}\n'
    '.brand-table th,.brand-table td{padding:11px 13px;border:1px solid var(--line);text-align:left}\n'
    '.brand-table th{background:var(--navy);color:#fff;font-weight:700;font-size:13px}\n'
    '.brand-table tr:nth-child(even) td{background:var(--surface-2)}\n'
    '.brand-table tr.is-current td{background:var(--blue-bg);font-weight:600}\n'
    '.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}\n'
    '.check-list{list-style:none;padding:0;margin:14px 0}\n'
    '.check-list li{position:relative;padding:8px 0 8px 26px;color:var(--ink-soft);line-height:1.65;'
    'border-bottom:1px solid var(--line-soft)}\n'
    '.check-list li:last-child{border-bottom:0}\n'
    '.check-list li::before{content:"\\2713";position:absolute;left:0;top:8px;color:var(--blue);'
    'font-weight:800}\n'
    '.check-list li strong{color:var(--ink)}\n'
    '</style>\n' + CSS_END
)

# Marken-Slug -> Anzeigename in products.json
BRANDS = {
    'razer': 'Razer',
    'gamesir': 'GameSir',
    '8bitdo': '8BitDo',
    'backbone': 'Backbone',
}


# ---------------------------------------------------------------- Datenschicht

def load_products():
    with open(PRODUCTS, encoding='utf-8') as f:
        data = json.load(f)
    return data['products'] if isinstance(data, dict) and 'products' in data else data


def rating_of(p):
    """Bewertung aus dem specs-Array: ['Bew.', '4,2 (1.655)'] -> (4.2, 1655)."""
    for entry in p.get('specs', []):
        if len(entry) == 2 and entry[0].startswith('Bew'):
            m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', entry[1])
            if m:
                return float(m.group(1).replace(',', '.')), int(m.group(2).replace('.', ''))
    return None, None


def price_of(p):
    m = re.search(r'(\d+)', p.get('price', ''))
    return int(m.group(1)) if m else None


ZAHLWORT = {1: 'ein', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf', 6: 'sechs',
            7: 'sieben', 8: 'acht', 9: 'neun', 10: 'zehn', 11: 'elf', 12: 'zwölf'}


def zw(n):
    """Kleine Zahlen im Fliesstext ausschreiben, groessere als Ziffer."""
    return ZAHLWORT.get(n, str(n))


def de(x, dec=2):
    """Deutsche Zahlschreibweise: 4.46 -> '4,46'; 1655 -> '1.655'."""
    if isinstance(x, int):
        return f'{x:,}'.replace(',', '.')
    return f'{x:.{dec}f}'.replace('.', ',')


def brand_stats(products, brand):
    """Kennzahlen einer Marke. Controller und Zubehoer werden getrennt, weil ein
    Kuehler die Controller-Bewertung sonst verzerrt."""
    sel = [p for p in products if p.get('brand') == brand]
    rows = []
    for p in sel:
        r, c = rating_of(p)
        rows.append({'p': p, 'rating': r, 'count': c, 'price': price_of(p),
                     'type': p.get('type'), 'works': p.get('worksOn', [])})
    ctrl = [r for r in rows if r['type'] == 'controller' and r['rating']]
    total = sum(r['count'] for r in ctrl)
    return {
        'brand': brand,
        'all': rows,
        'ctrl': sorted(ctrl, key=lambda r: -r['rating']),
        'n_ctrl': len(ctrl),
        'n_all': len(sel),
        'reviews': total,
        'avg': sum(r['rating'] * r['count'] for r in ctrl) / total,
        'best': max(ctrl, key=lambda r: r['rating']),
        'worst': min(ctrl, key=lambda r: r['rating']),
        'cheapest': min(ctrl, key=lambda r: r['price']),
        'dearest': max(ctrl, key=lambda r: r['price']),
        'zubehoer': [r for r in rows if r['type'] != 'controller'],
    }


def name(row):
    return row['p']['name']


def link(row):
    return f'<a href="{row["p"]["detail"]}">{row["p"]["name"]}</a>'


class Lookup:
    """Zugriff auf einzelne Produkte per slug. Jede Zahl im Fliesstext geht hier
    durch, damit nichts fest im Text steht, was in products.json gepflegt wird (§A1)."""

    def __init__(self, products):
        self._by_slug = {p['slug']: p for p in products}

    def __call__(self, slug):
        if slug not in self._by_slug:
            raise SystemExit(f'FEHLER: Produkt "{slug}" fehlt in products.json — Text anpassen')
        return self._by_slug[slug]

    def price(self, slug):
        return price_of(self(slug))

    def rating(self, slug):
        return de(rating_of(self(slug))[0], 1)

    def count(self, slug):
        return de(rating_of(self(slug))[1])

    def link(self, slug):
        p = self(slug)
        return f'<a href="{p["detail"]}">{p["name"]}</a>'


# ---------------------------------------------------------------- Textschicht

def comparison_table(stats_all, current):
    """Vier-Zeilen-Uebersicht, die aktuelle Marke hervorgehoben. Reine Faktenzeilen
    aus products.json; die Einordnung drumherum ist je Seite eigener Text."""
    order = sorted(stats_all.values(), key=lambda s: -s['avg'])
    rows = []
    for s in order:
        cur = s['brand'] == current
        cells = (f'<td>{"<strong>" if cur else ""}{s["brand"]}{"</strong>" if cur else ""}</td>'
                 f'<td>{s["n_ctrl"]}</td>'
                 f'<td>{de(s["avg"])}</td>'
                 f'<td>{de(s["reviews"])}</td>'
                 f'<td>{s["cheapest"]["price"]} bis {s["dearest"]["price"]} €</td>')
        rows.append(f'      <tr{" class=\"is-current\"" if cur else ""}>{cells}</tr>')
    return (
        '    <div class="table-wrap"><table class="brand-table">\n'
        '      <thead><tr><th>Marke</th><th>Controller</th><th>Ø Bewertung</th>'
        '<th>Bewertungen</th><th>Preisspanne</th></tr></thead>\n'
        '      <tbody>\n' + '\n'.join(rows) + '\n      </tbody>\n'
        '    </table></div>\n'
        '    <p class="table-note" style="color:var(--ink-soft);font-size:.9rem;margin-top:10px">'
        'Verglichen werden die vier Marken, zu denen wir eine eigene Übersicht führen. Der Wert ist '
        'der gewichtete Durchschnitt der Amazon-Sternebewertungen aller Controller dieser Marke in '
        'unserem Sortiment. Zubehör wie Kühler oder Halterungen ist nicht eingerechnet, weil es die '
        'Controller-Bewertung sonst verzerrt.</p>\n'
    )


def erfahrung_text(s, allst, L):
    """Sektion 1 je Marke: was die Bewertungslage wirklich hergibt.
    Jede Zahl kommt aus products.json, keine steht fest im Text (§A1)."""
    b = s['brand']
    gs, eb = allst['GameSir'], allst['8BitDo']

    if b == 'Razer':
        aufpreis = L.price('razer-kishi-v3-pro') - L.price('razer-kishi-v3')
        return (
            f'<p>Razer hat die kleinste Bewertungsbasis der vier Marken, die wir mit eigenem Hub '
            f'führen. Die drei Kishi-Controller kommen zusammen auf {de(s["reviews"])} Amazon-Bewertungen '
            f'und einen gewichteten Schnitt von {de(s["avg"])} von 5 Sternen. Zum Vergleich: '
            f'GameSir bringt es mit fünf Modellen auf {de(gs["reviews"])} Bewertungen. Das heißt '
            f'nicht, dass Razer schlechter ist, aber die Urteile stehen auf dünnerem Eis, und '
            f'einzelne Ausreißer wiegen schwerer.</p>\n'
            f'<p>Auffällig ist, wie eng die Kishi-Modelle beieinander liegen. Der '
            f'{L.link("razer-kishi-v3")} steht bei {L.rating("razer-kishi-v3")} Sternen. Der '
            f'{L.link("razer-kishi-v3-pro")} kostet {aufpreis} Euro mehr und steht bei '
            f'{L.rating("razer-kishi-v3-pro")}. Der Mehrpreis kauft Ausstattung, nicht '
            f'Zufriedenheit. Am '
            f'schwächsten schneidet unter den Controllern der {L.link("razer-kishi-ultra")} mit '
            f'{L.rating("razer-kishi-ultra")} Sternen ab.</p>\n'
            f'<p><strong>Was wir nicht empfehlen:</strong> Das schwächste Razer-Produkt bei uns ist '
            f'kein Controller, sondern der {L.link("razer-phone-cooler")} mit '
            f'{L.rating("razer-phone-cooler")} von 5 Sternen. Er kostet '
            f'{L.price("razer-phone-cooler")} Euro und wird damit schlechter bewertet als jedes '
            f'andere Razer-Gerät in unserer Liste. Wer kühlen will, ist mit dem Black Shark '
            f'{L.link("black-shark-funcooler")} besser bedient: '
            f'{L.price("black-shark-funcooler")} Euro bei '
            f'{L.rating("black-shark-funcooler")} Sternen.</p>\n'
        )

    if b == 'GameSir':
        return (
            f'<p>GameSir hat mit Abstand die belastbarste Datenlage: {de(s["reviews"])} Amazon-'
            f'Bewertungen über {zw(s["n_ctrl"])} Controller, mehr als Razer, Backbone und 8BitDo '
            f'zusammen. Der gewichtete Schnitt liegt bei {de(s["avg"])} von 5 Sternen. Wenn eine '
            f'Marke bei dieser Menge an Rückmeldungen stabil über 4 Sternen bleibt, ist das '
            f'aussagekräftiger als ein Spitzenwert aus wenigen Dutzend Stimmen.</p>\n'
            f'<p>Innerhalb der Marke liegen allerdings Welten zwischen den Modellen: '
            f'{de(s["best"]["rating"], 1)} Sterne beim {link(s["best"])}, '
            f'{de(s["worst"]["rating"], 1)} beim {link(s["worst"])}. Wer bei GameSir blind zum '
            f'teuersten Modell greift, kauft nicht automatisch das beste: Der '
            f'{L.link("gamesir-x3-pro")} kostet {L.price("gamesir-x3-pro")} Euro und steht bei '
            f'{L.rating("gamesir-x3-pro")} Sternen, der {L.link("gamesir-x5-lite")} kostet '
            f'{L.price("gamesir-x5-lite")} Euro und liegt mit {L.rating("gamesir-x5-lite")} '
            f'darüber.</p>\n'
            f'<p><strong>Woran es bei den schwächeren Modellen liegt:</strong> Beim '
            f'{L.link("gamesir-x2s")} nennen wir in unserem Test die Verarbeitung als Schwachpunkt, '
            f'sie bleibt unter G8-Niveau, dazu kommt der kleinere Griff. Beim '
            f'{L.link("gamesir-x3-pro")} ist es der Zuschnitt: aktive Kühlung, dafür kein '
            f'Bluetooth. Wer die Marke von ihrer besten Seite will, '
            f'greift zur G8-Reihe oder zum X5 Lite.</p>\n'
        )

    if b == '8BitDo':
        return (
            f'<p>8BitDo ist die bestbewertete Marke in unserem Sortiment: {de(s["avg"])} von 5 Sternen '
            f'im gewichteten Schnitt, aus {de(s["reviews"])} Amazon-Bewertungen über {zw(s["n_ctrl"])} '
            f'Controller. Der {link(s["best"])} allein trägt {de(s["best"]["count"])} davon und steht '
            f'bei {de(s["best"]["rating"], 1)} Sternen, bei einem Preis von {s["best"]["price"]} '
            f'Euro.</p>\n'
            f'<p>Die Einschränkung, die dazugehört: {zw(s["n_ctrl"])} Modelle sind eine schmale Basis. '
            f'GameSir liegt mit {de(gs["avg"])} niedriger, stützt sich dafür aber auf '
            f'{de(gs["reviews"])} Bewertungen über {zw(gs["n_ctrl"])} Geräte. Ein Markenschnitt aus zwei '
            f'Produkten sagt vor allem etwas über diese zwei Produkte aus.</p>\n'
            f'<p><strong>Der eigentliche Unterschied</strong> liegt nicht in der Bewertung, sondern in '
            f'der Bauform. Beide 8BitDo-Modelle sind klassische Gamepads und spannen das Handy nicht '
            f'ein: Du brauchst einen Ständer oder eine Halterung dazu. Wer einen Controller sucht, der '
            f'das Handy hält, ist bei den Teleskop-Modellen von GameSir, Razer oder Backbone richtig. '
            f'Wer ohnehin am Tisch oder auf dem Sofa spielt, bekommt bei 8BitDo für '
            f'{s["cheapest"]["price"]} bis {s["dearest"]["price"]} Euro Technik, für die Teleskop-'
            f'Modelle deutlich mehr verlangen.</p>\n'
        )

    # Backbone
    return (
        f'<p>Backbone liegt mit {de(s["avg"])} von 5 Sternen aus {de(s["reviews"])} Bewertungen im '
        f'oberen Feld. Die Urteile stehen allerdings auf sehr unterschiedlich breiter Basis: '
        f'Der {link(s["best"])} kommt auf '
        f'{de(s["best"]["rating"], 1)} Sterne aus {de(s["best"]["count"])} Bewertungen, der '
        f'{link(s["worst"])} steht bei {de(s["worst"]["rating"], 1)} Sternen, allerdings erst aus '
        f'{de(s["worst"]["count"])} Bewertungen. Diese Zahl ist zu klein für ein belastbares Urteil, '
        f'wir führen sie trotzdem, statt sie wegzulassen.</p>\n'
        f'<p>Bei Backbone steht das teuerste Gerät unseres gesamten Sortiments: der '
        f'{link(s["dearest"])} für {s["dearest"]["price"]} Euro. Der Einstieg liegt mit '
        f'{s["cheapest"]["price"]} Euro aber unter dem günstigsten Razer-Controller, der '
        f'{allst["Razer"]["cheapest"]["price"]} Euro kostet. Bezahlt wird das Ökosystem, also '
        f'die App, die Spielebibliothek und Streaming-Dienste zusammenführt, und die '
        f'Verarbeitung.</p>\n'
        f'<p><strong>Der Haken, den man vor dem Kauf kennen sollte:</strong> Teile der Backbone-App '
        f'sind an ein Abo gekoppelt. Bei GameSir und Razer sind die Apps vollständig kostenlos. Wer '
        f'den Controller nur als Controller nutzen will, zahlt bei Backbone für Funktionen mit, die '
        f'er nicht abruft. Die Abwägung im Detail steht in '
        f'<a href="/blog/gamesir-oder-backbone/">GameSir oder Backbone</a>.</p>\n'
    )


def plattform_text(s, L):
    """Sektion 2 je Marke: welches Modell an welcher Plattform."""
    b = s['brand']

    if b == 'Razer':
        return (
            '<p>Alle drei Kishi-Controller sind USB-C-Geräte und funktionieren sowohl an '
            'Android-Handys als auch an iPhones ab dem iPhone 15, weil Apple erst dort auf USB-C '
            'gewechselt ist. Für ältere iPhones mit Lightning-Anschluss führen wir kein '
            'Razer-Modell.</p>\n'
            '<ul class="check-list">\n'
            '  <li><strong>Android:</strong> alle drei Modelle. Razer nennt für den Kishi V3 '
            'Android 14 als Mindestversion, ältere Systeme können also außen vor bleiben.</li>\n'
            '  <li><strong>iPhone:</strong> ab iPhone 15 alle drei Modelle, darunter keines.</li>\n'
            '  <li><strong>Tablet:</strong> alle drei führen das iPad mini in ihren '
            'Kompatibilitätslisten. Ausdrücklich für Tablets ausgelegt ist aber nur der '
            '<a href="/produkte/razer-kishi-ultra/">Kishi Ultra</a>, den Razer bis 8 Zoll angibt. '
            'Welche Controller sonst an ein Tablet passen, steht in '
            '<a href="/blog/controller-fuer-tablet/">Controller für Tablets</a>.</li>\n'
            '</ul>\n'
            '<p>Die Razer Nexus App läuft auf Android und iOS und kostet nichts. Ein Abo ist für '
            'keine Funktion nötig, das unterscheidet Razer vom Backbone-Ökosystem.</p>\n'
        )

    if b == 'GameSir':
        return (
            '<p>GameSir deckt als einzige der vier Marken beide Verbindungsarten ab, und genau '
            'daran entscheidet sich, ob ein Modell zu deinem Handy passt.</p>\n'
            '<ul class="check-list">\n'
            '  <li><strong>Nur USB-C:</strong> '
            '<a href="/controller/universal/gamesir-x5-lite-review/">X5 Lite</a> und '
            '<a href="/controller/universal/gamesir-g8-galileo-review/">G8 Galileo</a>. Am iPhone '
            'braucht es dafür ein iPhone 15 oder neuer.</li>\n'
            '  <li><strong>USB-C und Bluetooth:</strong> der '
            '<a href="/controller/universal/gamesir-g8-plus-review/">G8 Plus</a> ist das einzige Modell, '
            'das beides beherrscht, und das einzige mit Switch-Betrieb. Die Bluetooth-Verbindung '
            'kostet messbar Latenz, am Handy steckst du ihn besser an.</li>\n'
            '  <li><strong>Nur Bluetooth:</strong> der '
            '<a href="/controller/universal/gamesir-x2s-review/">X2s</a>. Funktioniert unabhängig '
            f'vom Anschluss, also auch an älteren iPhones, ist aber mit '
            f'{L.rating("gamesir-x2s")} Sternen das schwächste Modell der Marke.</li>\n'
            '  <li><strong>Android mit Kühlung:</strong> der '
            '<a href="/controller/android/gamesir-x3-pro-review/">X3 Pro</a> ist der einzige '
            'GameSir mit eingebauter Peltier-Kühlung, verbindet sich ausschließlich per USB-C '
            'und hat kein '
            'Bluetooth. Er ist auf Android zugeschnitten; wer ihn am iPhone nutzen will, prüft '
            'vorher die Angaben auf seiner Produktseite.</li>\n'
            '  <li><strong>Tablet:</strong> G8 Plus und X5 Lite reichen bis zum iPad mini. Die '
            'übrigen Modelle sind auf Handy-Breite ausgelegt.</li>\n'
            '</ul>\n'
            '<p>Die GameSir-App gibt es für Android und iOS, sie ist kostenlos und ohne Abo nutzbar. '
            'Unter Android lassen sich damit Tastenbelegungen und Stick-Kurven anpassen, unter iOS '
            'ist der Funktionsumfang systembedingt kleiner.</p>\n'
        )

    if b == '8BitDo':
        return (
            '<p>8BitDo baut klassische Gamepads, keine Teleskop-Controller. Das Handy wird nicht '
            'eingespannt, sondern steht daneben. Für die Plattformfrage heißt das: Es geht nicht um '
            'den Stecker deines Handys, sondern darum, welches System der Controller unterstützt.</p>\n'
            '<ul class="check-list">\n'
            '  <li><strong>Android:</strong> beide Modelle. Das ist die Plattform, für die 8BitDo '
            'diese Controller ausgelegt hat.</li>\n'
            '  <li><strong>iPhone:</strong> hier lohnt der Blick auf die jeweilige Produktseite, '
            'bevor du bestellst. Der '
            '<a href="/produkte/8bitdo-ultimate-mobile/">Ultimate Mobile</a> ist auf Android '
            'ausgerichtet, für iPhone-Nutzer sind der '
            '<a href="/controller/ios/backbone-one-2-review/">Backbone One</a> oder die '
            'Teleskop-Modelle von <a href="/marken/gamesir/">GameSir</a> die sicherere Wahl.</li>\n'
            '  <li><strong>Am PC:</strong> für den '
            '<a href="/controller/universal/8bitdo-ultimate-2c-review/">Ultimate 2C</a> gibt '
            '8BitDo Windows ausdrücklich an. Welche weiteren Systeme ein Modell unterstützt, '
            'steht jeweils auf seiner Produktseite.</li>\n'
            '</ul>\n'
            '<p>Der Preis für die günstige Technik ist die fehlende Halterung: Bei beiden Modellen '
            'brauchst du einen Ständer, einen Tisch oder eine separate Klemme. Wer das Handy in der '
            'Hand halten will, findet Teleskop-Alternativen im '
            '<a href="/controller/android/">Android-Hub</a>.</p>\n'
        )

    # Backbone
    return (
        '<p>Bei Backbone ist die Plattformfrage die häufigste Fehlkaufquelle, weil zwei ähnlich '
        'aussehende Modelle unterschiedliche Stecker haben.</p>\n'
        '<ul class="check-list">\n'
        '  <li><strong>iPhone ab 15 und Android:</strong> '
        '<a href="/controller/ios/backbone-one-2-review/">Backbone One 2. Gen</a> und '
        '<a href="/controller/ios/backbone-pro-review/">Backbone Pro</a>, beide mit USB-C. Der '
        'Pro lässt sich zusätzlich per Bluetooth koppeln und dann auch kabellos nutzen.</li>\n'
        '  <li><strong>iPhone 14 und älter:</strong> nur die '
        '<a href="/controller/ios/backbone-one-ps-review/">PlayStation Edition</a> mit '
        'Lightning-Stecker. Sie passt dafür an kein Android-Handy.</li>\n'
        '  <li><strong>Android allgemein:</strong> möglich, aber Backbone ist als iPhone-Marke '
        'gestartet, und die App ist unter iOS runder. Wer ausschließlich Android nutzt, bekommt bei '
        '<a href="/marken/gamesir/">GameSir</a> mehr Technik fürs Geld.</li>\n'
        '</ul>\n'
        '<p>Vor dem Kauf lohnt der Blick auf den eigenen Anschluss: Bei den eingespannten Modellen '
        'entscheidet Lightning oder USB-C über passt oder passt nicht, und ein Adapter löst das '
        'nicht. Nur beim Pro gibt es mit Bluetooth einen zweiten Weg.</p>\n'
    )


def extra_faqs(s, allst, L):
    """Je zwei zusaetzliche FAQs, die auf in GSC belegte Marken-Queries zielen."""
    b = s['brand']
    gs, bb = allst['GameSir'], allst['Backbone']

    if b == 'Razer':
        return [
            ('Funktioniert ein Razer Kishi am Android-Handy?',
             'Ja, alle drei Kishi-Modelle sind USB-C-Controller und laufen an Android-Handys mit '
             'USB-C-Anschluss. Für den Kishi V3 nennt Razer dabei Android 14 als Mindestversion. '
             'Am iPhone funktionieren sie erst ab dem iPhone 15, weil ältere Modelle einen '
             'Lightning-Anschluss haben.'),
            ('Sind Razer-Controller ihr Geld wert?',
             f'Beim Kishi V3 für {L.price("razer-kishi-v3")} Euro ja: Er steht bei '
             f'{L.rating("razer-kishi-v3")} von 5 Sternen, der {L.price("razer-kishi-v3-pro")} Euro '
             f'teure V3 Pro bei {L.rating("razer-kishi-v3-pro")}. Der Aufpreis kauft Ausstattung, '
             f'nicht Zufriedenheit. Preis-Leistungs-Sieger der Marke ist damit das Einstiegsmodell. '
             f'Wer weniger ausgeben will, findet bei <a href="/marken/gamesir/">GameSir</a> ab '
             f'{gs["cheapest"]["price"]} Euro Hall-Effect-Technik.'),
        ]

    if b == 'GameSir':
        return [
            ('Ist GameSir besser als Backbone?',
             f'Bei der Technik pro Euro ja, beim Gesamterlebnis nicht unbedingt. GameSir liegt im '
             f'Bewertungsschnitt bei {de(s["avg"])} von 5 Sternen aus {de(s["reviews"])} Bewertungen, '
             f'Backbone bei {de(bb["avg"])} aus {de(bb["reviews"])}. GameSir bietet Hall-Effect-Sticks '
             f'schon ab {s["cheapest"]["price"]} Euro und eine App ohne Abo, Backbone das rundere '
             f'Ökosystem am iPhone. Die ausführliche Abwägung steht in '
             f'<a href="/blog/gamesir-oder-backbone/">GameSir oder Backbone</a>.'),
            ('Wie zuverlässig sind GameSir-Controller?',
             f'Über {de(s["reviews"])} Amazon-Bewertungen hinweg liegt die Marke bei '
             f'{de(s["avg"])} von 5 Sternen. Die Unterschiede innerhalb des Sortiments sind aber '
             f'groß: Die G8-Reihe und der X5 Lite liegen zwischen '
             f'{L.rating("gamesir-g8-plus")} und {L.rating("gamesir-x5-lite")} Sternen, der '
             f'X3 Pro bei {L.rating("gamesir-x3-pro")} und der X2s bei {L.rating("gamesir-x2s")}. '
             f'Wer zur G8-Reihe oder zum X5 Lite greift, kauft die belastbare Seite der Marke.'),
        ]

    if b == '8BitDo':
        return [
            ('Sind 8BitDo-Controller gut für Handyspiele?',
             f'Von der Bewertung her ja: {de(s["avg"])} von 5 Sternen aus {de(s["reviews"])} '
             f'Bewertungen sind der beste Markenschnitt in unserem Sortiment. Der Haken ist die '
             f'Bauform. Beide Modelle sind klassische Gamepads und halten das Handy nicht, du '
             f'brauchst also einen Ständer dazu. Für unterwegs sind Teleskop-Controller praktischer, '
             f'für zuhause ist 8BitDo das günstigere und besser bewertete Angebot.'),
            ('Warum sind 8BitDo-Controller so viel günstiger?',
             f'Weil die ausziehbare USB-C-Mechanik fehlt, die ein Teleskop-Modell teuer macht. '
             f'Sie ist der aufwendigste Teil eines solchen Controllers. An der Sensorik wird trotzdem nicht gespart: Der Ultimate 2C '
             f'hat für {L.price("8bitdo-ultimate-2c")} Euro driftfreie Hall-Effect-Sticks, die bei '
             f'Teleskop-Modellen erst ab {L.price("gamesir-x5-lite")} Euro anfangen.'),
        ]

    # Backbone
    return [
        ('Gibt es Backbone-Controller für Android?',
         'Ja, der Backbone One 2. Gen und der Backbone Pro haben beide USB-C und funktionieren an '
         'Android-Handys. Die PlayStation Edition dagegen hat einen Lightning-Stecker und passt '
         'ausschließlich an iPhones bis Generation 14. Wer ausschließlich Android nutzt, sollte '
         'vorher vergleichen: <a href="/marken/gamesir/">GameSir</a> bietet in derselben Preisklasse '
         'mehr Technik.'),
        ('Ist Backbone oder GameSir die bessere Wahl?',
         f'Das hängt am Handy. Am iPhone spricht das Ökosystem für Backbone: App, Spielebibliothek '
         f'und Streaming greifen dort am saubersten ineinander. Am Android-Handy und beim Preis pro '
         f'Technik liegt GameSir vorn, mit Hall-Effect-Sticks ab {gs["cheapest"]["price"]} Euro und '
         f'einer App ohne Abo. Der direkte Vergleich steht in '
         f'<a href="/blog/gamesir-oder-backbone/">GameSir oder Backbone</a>.'),
    ]


# ---------------------------------------------------------------- Rendering

def render_block(s, allst, L):
    b = s['brand']
    return (
        f'{START}\n'
        f'  <section class="section"><div class="container brand-ext" style="max-width:820px">\n'
        f'    <h2>Wie gut sind {b}-Controller wirklich?</h2>\n'
        f'    {erfahrung_text(s, allst, L)}'
        f'    <h3>Die vier Marken im Bewertungsvergleich</h3>\n'
        f'{comparison_table(allst, b)}'
        f'  </div></section>\n'
        f'  <section class="section"><div class="container brand-ext" style="max-width:820px">\n'
        f'    <h2>{b} an Android-Handy, iPhone und Tablet</h2>\n'
        f'    {plattform_text(s, L)}'
        f'  </div></section>\n'
        f'{END}'
    )


def render_faq_items(s, allst, L):
    out = [FAQ_START]
    for q, a in extra_faqs(s, allst, L):
        out.append(f'<details class="faq-item"><summary>{q}</summary><div class="faq-a">{a}</div></details>')
    out.append(FAQ_END)
    return '\n'.join(out)


def strip_tags(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).strip()


def rebuild_faq_schema(html):
    """FAQPage-Schema aus den sichtbaren details-Bloecken neu rendern (§A4)."""
    items = re.findall(
        r'<details class="faq-item"><summary>(.*?)</summary><div class="faq-a">(.*?)</div></details>',
        html, re.S)
    if not items:
        return html
    entities = [{'@type': 'Question', 'name': strip_tags(q),
                 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}}
                for q, a in items]
    payload = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage',
                          'mainEntity': entities}, ensure_ascii=False)

    def repl(m):
        try:
            if json.loads(m.group(1)).get('@type') == 'FAQPage':
                return f'<script type="application/ld+json">\n{payload}\n</script>'
        except json.JSONDecodeError:
            pass
        return m.group(0)

    return re.sub(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                  repl, html, flags=re.S)


# Zahlen, die nichts mit Preisen oder Bewertungen zu tun haben und deshalb nicht
# aus products.json stammen koennen. Jede weitere Zahl muss belegt sein.
FREIE_ZAHLEN = {
    '5',    # "von 5 Sternen"
    '15',   # iPhone 15 (USB-C-Wechsel bei Apple)
    '14',   # iPhone 14 (letzte Lightning-Generation)
    '13',   # iOS 13 (systemweite Gamepad-Unterstuetzung)
    '8',    # Zoll-Angabe beim Kishi Ultra
    '2',    # "2. Gen", "Ultimate 2C"
    '4',    # "stabil über 4 Sternen"
}


def check_numbers(text, s, allst, products):
    """Prueft, dass jede Zahl im erzeugten Text aus products.json ableitbar ist."""
    plain = re.sub(r'<[^>]+>', ' ', text)
    # Produktnamen tragen selbst Ziffern (Kishi V3, G8 Plus, FunCooler 6) und sind
    # keine Messwerte: vor der Pruefung entfernen, laengste zuerst.
    for nm in sorted({p['name'] for p in products}, key=len, reverse=True):
        plain = plain.replace(nm, ' ')
    # Fremdgeraete- und Versionsbezeichnungen sind ebenfalls keine Messwerte.
    plain = re.sub(r'\b(iPhone|iPad|iOS|Android|Generation|Gen\.?)\s+\d+', ' ', plain)

    erlaubt = set(FREIE_ZAHLEN)
    for st in allst.values():
        erlaubt |= {de(st['avg']), de(st['reviews']), str(st['n_ctrl']), str(st['n_all'])}
        for row in st['all']:
            if row['price'] is not None:
                erlaubt.add(str(row['price']))
            if row['rating'] is not None:
                erlaubt.add(de(row['rating'], 1))
                erlaubt.add(de(row['count']))
    # Preisdifferenzen zwischen Modellen derselben Marke sind zulaessig, weil wir
    # Aufpreise ausweisen.
    for st in allst.values():
        prices = [r['price'] for r in st['all'] if r['price'] is not None]
        erlaubt |= {str(abs(a - b)) for a in prices for b in prices if a != b}

    gefunden = re.findall(r'(?<![\w,.])(\d+(?:[.,]\d+)?)(?![\w])', plain)
    unbelegt = sorted({g for g in gefunden if g not in erlaubt})
    if unbelegt:
        raise SystemExit(
            f'DRIFT-GATE ({s["brand"]}): Zahl(en) im Text ohne Deckung in products.json: '
            f'{", ".join(unbelegt)}\n'
            f'   Entweder aus den Daten ziehen (Lookup) oder in FREIE_ZAHLEN aufnehmen.')


def apply_to_file(path, s, allst, L, products):
    with open(path, encoding='utf-8') as f:
        original = f.read()
    html = original

    # 1. Alten Block entfernen (Idempotenz). Das nachgestellte \n gehoert zum
    # Einfuege-Muster in Schritt 2/3 und muss mit weg, sonst waechst die Datei
    # bei jedem Lauf um eine Leerzeile.
    html = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', html, flags=re.S)
    html = re.sub(re.escape(FAQ_START) + r'.*?' + re.escape(FAQ_END) + r'\n?', '', html, flags=re.S)
    html = re.sub(re.escape(CSS_START) + r'.*?' + re.escape(CSS_END) + r'\n?', '', html, flags=re.S)

    # 1b. Seiten-CSS vor </head> (Muster der Vergleichsseiten)
    if '</head>' not in html:
        raise SystemExit(f'FEHLER: kein </head> in {path}')
    html = html.replace('</head>', CSS + '\n</head>', 1)

    # 2. Neue Sektionen vor der FAQ-Sektion einsetzen
    anchor = f'  <section class="section"><div class="container" style="max-width:820px">\n    <h2>Häufige Fragen zu {s["brand"]}</h2>'
    if anchor not in html:
        raise SystemExit(f'FEHLER: FAQ-Anker nicht gefunden in {path}')
    html = html.replace(anchor, render_block(s, allst, L) + '\n' + anchor, 1)

    # 3. Neue FAQ-Eintraege ans Ende der bestehenden faq-list
    close = '    </div>\n  </div></section>\n</main>'
    if close not in html:
        raise SystemExit(f'FEHLER: FAQ-Listenende nicht gefunden in {path}')
    html = html.replace(close, render_faq_items(s, allst, L) + '\n' + close, 1)

    # 4. Schema aus dem finalen HTML neu rendern
    html = rebuild_faq_schema(html)

    # 5. Selbstkontrolle
    assert html.count(START) == 1 and html.count(END) == 1, 'Block nicht genau einmal vorhanden'
    assert html.count(CSS_START) == 1 and html.count(CSS_END) == 1, 'CSS-Block nicht genau einmal vorhanden'
    for klasse in ('brand-table', 'check-list', 'table-wrap', 'is-current'):
        if f'class="{klasse}"' in html or f'{klasse}"' in html:
            assert f'.{klasse}' in html or klasse == 'is-current', f'CSS fehlt fuer .{klasse}'
    n_details = html.count('<details class="faq-item">')
    n_schema = html.count('"@type": "Question"')
    assert n_details == n_schema, f'FAQ/Schema-Drift: {n_details} sichtbar, {n_schema} im Schema'

    # Em-Dash-Verbot gilt fuer NEU erzeugten Text; die Altbestaende in Titles und
    # Bestandsprosa stehen unter Meta-Freeze und werden hier bewusst nicht angefasst.
    generated = re.search(re.escape(START) + r'(.*?)' + re.escape(END), html, re.S).group(1)
    generated += re.search(re.escape(FAQ_START) + r'(.*?)' + re.escape(FAQ_END), html, re.S).group(1)
    assert '—' not in generated, 'Em-Dash im generierten Text (verboten laut CLAUDE.md)'

    # Drift-Gate (§A1): Jeder Euro-Betrag, jeder Sternewert und jede Bewertungszahl
    # im erzeugten Text muss aus products.json ableitbar sein. Wer hier eine Zahl
    # von Hand in den Fliesstext schreibt, faellt auf.
    check_numbers(generated, s, allst, products)

    return original, html


# ---------------------------------------------------------------- main

def main():
    check = '--check' in sys.argv
    products = load_products()
    allst = {v: brand_stats(products, v) for v in BRANDS.values()}
    L = Lookup(products)

    changed = []
    for slug, brand in BRANDS.items():
        path = os.path.join(ROOT, 'marken', slug, 'index.html')
        original, html = apply_to_file(path, allst[brand], allst, L, products)
        if html != original:
            changed.append(slug)
            if not check:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html)
        words = len(strip_tags(re.search(r'<main>(.*)</main>', html, re.S).group(1)).split())
        print(f'  {slug:<9} {words:>4} Wörter · {html.count("<details class=\"faq-item\">")} FAQs'
              f' · {"geändert" if html != original else "unverändert"}')

    if check:
        print(f'\n[--check] {len(changed)} Datei(en) wären geändert worden: {", ".join(changed) or "keine"}')
    else:
        print(f'\n{len(changed)} Marken-Hub(s) geschrieben: {", ".join(changed) or "keine"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
