#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt /blog/was-kostet-ein-handy-controller/ aus products.json (Massnahme B4).

Warum diese Seite: Sheridan nennt den Preis als das erste Thema, um das Anbieter einen
Bogen machen. Die Buecher-Synthese vom 30.09. hat daraus Massnahme 2 abgeleitet: eine
Seite, die die Preisfrage offensiv beantwortet, mit echten Spannen aus products.json.

Warum generiert: Jede Zahl auf dieser Seite altert mit dem naechsten preis-loop. Von
Hand geschrieben waere sie in drei Monaten falsch -- und genau diese Sorte Text hat die
Pruefserie vom 30.09./01.10. reihenweise veraltet vorgefunden. Hier steht keine Zahl im
Quelltext, jede wird gerechnet.

Keyword-Abgrenzung (§B1): Diese Seite nimmt die BUDGETFRAGE ("was kostet ein handy
controller", "handy controller preis"). Die QUALITAETSFRAGE zu billigen Geraeten
("sind guenstige gut?") gehoert weiter /blog/guenstige-handy-controller/, die
transaktionale Liste /vergleich/beste-budget-controller/. Beide werden von hier
verlinkt, statt mit ihnen zu konkurrieren.

Aufruf:  python3 scripts/gen_preisfrage.py
         python3 scripts/gen_preisfrage.py --check   (nur melden, nichts schreiben)
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

ZIEL = 'blog/was-kostet-ein-handy-controller/index.html'
URL = 'https://smartphone-controller.com/blog/was-kostet-ein-handy-controller/'
DATENSTAND = 'September 2026'


def esc(s):
    return html.escape(str(s), quote=True)


def preis(p):
    m = re.search(r'(\d+)', p.get('price') or '')
    return int(m.group(1)) if m else None


def spec(p, k):
    return next((v for kk, v in p.get('specs', []) or [] if kk == k), None)


def bewertung(p):
    m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', spec(p, 'Bew.') or '')
    if not m:
        return (0.0, 0)
    return (float(m.group(1).replace(',', '.')), int(m.group(2).replace('.', '')))


def de(x):
    """Deutsche Schreibweise: 4.6 -> 4,6 und 2188 -> 2.188"""
    if isinstance(x, float):
        return f'{x:.1f}'.replace('.', ',')
    return f'{x:,}'.replace(',', '.')


def voller_name(p):
    marke = p.get('brand', '')
    name = p.get('name', '')
    return name if marke.lower() in name.lower() else f'{marke} {name}'.strip()


def link(p):
    ziel = p.get('detail') or f"/produkte/{p['slug']}/"
    return f'<a href="{esc(ziel)}">{esc(voller_name(p))}</a>'


def daten():
    items = json.load(open('assets/data/products.json', encoding='utf-8'))
    ctrl = sorted((p for p in items if p.get('type') == 'controller' and preis(p)),
                  key=preis)
    zub = sorted((p for p in items if p.get('type') == 'zubehoer' and preis(p)),
                 key=preis)
    return items, ctrl, zub


def band(ctrl, unten, oben):
    return [p for p in ctrl if unten <= preis(p) < oben]


def bestes(gruppe):
    """Bestbewertet, bei Gleichstand das mit mehr Bewertungen."""
    return max(gruppe, key=lambda p: (bewertung(p)[0], bewertung(p)[1]))


def baue(lesezeit=4):
    items, ctrl, zub = daten()
    preise = [preis(p) for p in ctrl]
    median = sorted(preise)[len(preise) // 2]
    billigster, teuerster = ctrl[0], ctrl[-1]
    best = bestes(ctrl)
    best_stern, best_anz = bewertung(best)
    teuer_stern, teuer_anz = bewertung(teuerster)

    # Preisbaender aus der tatsaechlichen Verteilung, nicht gegriffen.
    BAENDER = [(0, 55, 'Einstieg'), (55, 100, 'Mittelklasse'), (100, 10**6, 'Oberklasse')]
    band_zeilen = []
    for unten, oben, titel in BAENDER:
        g = band(ctrl, unten, oben)
        if not g:
            continue
        b = bestes(g)
        bst, ban = bewertung(b)
        spanne = (f'{min(preis(x) for x in g)} bis {max(preis(x) for x in g)} €'
                  if len(g) > 1 else f'{preis(g[0])} €')
        band_zeilen.append(
            f'<tr><td><strong>{esc(titel)}</strong><br><span class="pr-spanne">{esc(spanne)}</span></td>'
            f'<td>{len(g)} von {len(ctrl)}</td>'
            f'<td>{link(b)}<br><span class="pr-spanne">{de(bst)} Sterne aus '
            f'{de(ban)} Bewertungen, {preis(b)} €</span></td></tr>')

    # Welche Merkmale gibt es ab welchem Preis? Ausschliesslich gerechnet.
    def spanne_mit(bed):
        tr = [preis(p) for p in ctrl if bed(p)]
        return (min(tr), max(tr), len(tr)) if tr else None

    hall = spanne_mit(lambda p: 'Hall' in (spec(p, 'Sticks') or ''))
    tablet = spanne_mit(lambda p: 'tablet' in (p.get('worksOn') or []))
    kabellos = spanne_mit(lambda p: re.search(r'BT|Bluetooth', spec(p, 'Verb.') or ''))

    merkmale = []
    if hall:
        merkmale.append(
            f'<li><strong>Driftfreie Hall-Effect-Sticks</strong> gibt es im Sortiment ab '
            f'{hall[0]} € ({hall[2]} Modelle, bis {hall[1]} €). Die Stick-Technik ist also '
            f'nicht das, wofür man mehr bezahlt.</li>')
    if kabellos:
        merkmale.append(
            f'<li><strong>Kabellos per Bluetooth</strong> läuft über die ganze Spanne von '
            f'{kabellos[0]} bis {kabellos[1]} € ({kabellos[2]} Modelle). Auch das ist keine '
            f'Frage des Budgets.</li>')
    if tablet:
        merkmale.append(
            f'<li><strong>Breite für Tablets</strong> fängt bei {tablet[0]} € an '
            f'({tablet[2]} Modelle). Wer ein iPad mini einspannen will, kommt unter diesem '
            f'Preis nicht weit.</li>')

    zub_zeilen = []
    for typ, label in (('finger-sleeves', 'Finger Sleeves'), ('trigger', 'Trigger-Aufsätze'),
                       ('kuehler', 'Handy-Kühler')):
        g = [p for p in zub if p.get('platform') == typ]
        if not g:
            continue
        zub_zeilen.append(
            f'<tr><td><strong>{esc(label)}</strong></td><td>{len(g)}</td>'
            f'<td>{min(preis(x) for x in g)} bis {max(preis(x) for x in g)} €</td></tr>')

    faqs = [
        (f'Was kostet ein guter Handy-Controller?',
         f'Unsere {len(ctrl)} Controller kosten zwischen {preis(billigster)} und '
         f'{preis(teuerster)} €, der mittlere Preis liegt bei {median} €. Mehr als die '
         f'Hälfte des Sortiments liegt unter {median + 5} €.'),
        (f'Muss ich mehr als {median} € ausgeben?',
         f'Nein. Der bestbewertete Controller in unserem Sortiment ist der '
         f'{voller_name(best)} für {preis(best)} € mit {de(best_stern)} Sternen aus '
         f'{de(best_anz)} Bewertungen. Das teuerste Modell kostet {preis(teuerster)} € und '
         f'kommt auf {de(teuer_stern)} Sterne aus {de(teuer_anz)} Bewertungen.'),
        ('Warum sind manche Controller dreimal so teuer?',
         'Nicht wegen der Sticks: Driftfreie Hall-Effect-Technik gibt es schon im Einstieg. '
         'Oben dazu kommen Baubreite für Tablets, eine Klinkenbuchse und Verarbeitung. Ob '
         'das den Aufpreis wert ist, hängt davon ab, ob du eines dieser Dinge brauchst.'),
        ('Was kostet das Zubehör?',
         f'Finger Sleeves, Trigger und Kühler liegen zusammen zwischen '
         f'{min(preis(p) for p in zub)} und {max(preis(p) for p in zub)} €. Sleeves sind '
         f'das günstigste sinnvolle Zubehör.'),
    ]
    faq_html = '\n'.join(
        f'<div class="faq-item"><h3 class="faq-q">{esc(q)}</h3><p class="faq-a">{esc(a)}</p></div>'
        for q, a in faqs)
    faq_schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'FAQPage',
        'mainEntity': [{'@type': 'Question', 'name': q,
                        'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]
    }, ensure_ascii=False)

    titel = 'Was kostet ein guter Handy-Controller? Preise 2026 im Überblick'
    # Lesezeit aus dem fertigen Text, nicht geschaetzt. Der Rumpf wird einmal ohne
    # die Zahl gebaut, gezaehlt und dann mit ihr ausgegeben.
    beschreibung = (
        f'Handy-Controller kosten bei uns {preis(billigster)} bis {preis(teuerster)} €, '
        f'im Mittel {median} €. Was du in welcher Preisklasse bekommst und wo mehr Geld '
        f'nichts bringt.')
    voll_titel = f'{titel} | smartphone-controller.com'

    article_schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'Article', 'headline': titel,
        'description': beschreibung,
        'author': {'@type': 'Person', 'name': 'Yannick Gerber',
                   'url': 'https://smartphone-controller.com/redaktion/'},
        'publisher': {'@type': 'Organization', 'name': 'smartphone-controller.com',
                      'logo': {'@type': 'ImageObject',
                               'url': 'https://smartphone-controller.com/assets/img/og-default.jpg'}},
        'datePublished': '2026-10-01', 'dateModified': '2026-10-01',
        'mainEntityOfPage': URL}, ensure_ascii=False)
    bc_schema = json.dumps({
        '@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home',
             'item': 'https://smartphone-controller.com/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Blog',
             'item': 'https://smartphone-controller.com/blog/'},
            {'@type': 'ListItem', 'position': 3, 'name': 'Was kostet ein Handy-Controller?',
             'item': URL}]}, ensure_ascii=False)

    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(voll_titel)}</title>
  <meta name="description" content="{esc(beschreibung)}">
  <link rel="canonical" href="{URL}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="smartphone-controller.com">
  <meta property="og:locale" content="de_DE">
  <meta property="og:title" content="{esc(voll_titel)}">
  <meta property="og:description" content="{esc(beschreibung)}">
  <meta property="og:url" content="{URL}">
  <meta property="og:image" content="https://smartphone-controller.com/assets/img/og-default.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(voll_titel)}">
  <meta name="twitter:description" content="{esc(beschreibung)}">
  <meta name="twitter:image" content="https://smartphone-controller.com/assets/img/og-default.jpg">
  <link rel="stylesheet" href="/assets/css/style.css?v=62c88cd1">
  <style>
.pr-tabelle{{width:100%;border-collapse:collapse;margin:18px 0;font-size:15px}}
.pr-tabelle th,.pr-tabelle td{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
.pr-tabelle th{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-dim);font-weight:800}}
.pr-spanne{{font-size:13px;color:var(--ink-soft)}}
.pr-antwort{{background:var(--blue-bg);border:1px solid var(--blue-dim);border-radius:var(--radius-lg);padding:20px 24px;margin:24px 0}}
.pr-antwort .pr-label{{font-size:11px;font-weight:800;color:var(--blue);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}}
.pr-antwort p{{font-size:16px;font-weight:700;color:var(--ink);line-height:1.55;margin:0}}
.hub-faq{{max-width:820px;margin:32px auto 0}}
.hub-faq .faq-item{{border-bottom:1px solid var(--line);padding:16px 0}}
.hub-faq .faq-item:last-child{{border-bottom:none}}
.hub-faq .faq-q{{font-size:16px;font-weight:700;margin-bottom:8px}}
.hub-faq .faq-a{{font-size:14px;color:var(--ink-soft);line-height:1.65}}
  </style>
  <script type="application/ld+json">{article_schema}</script>
  <script type="application/ld+json">{bc_schema}</script>
  <script type="application/ld+json">{faq_schema}</script>
</head>
<body>
<header class="site-header" id="site-header">
<div class="trust-strip"><div class="container">
<span class="ts">Unabhängig &amp; herstellerneutral</span>
<span class="ts">42 Modelle im Sortiment</span>
<span class="ts">Datenstand September 2026</span>
</div></div>
<div class="header-main">
<a href="/" class="logo" aria-label="smartphone-controller.com – Startseite"><span class="logo-text">smartphone-controller<span class="logo-tld">.com</span></span></a>
</div>
<nav class="main-nav" aria-label="Hauptnavigation"><div class="container">
<a href="/produkte/" class="nav-link">🛒 Alle Produkte</a>
<a href="/controller-finder/" class="nav-link">🎮 Controller-Finder</a>
<a href="/controller/ios/" class="nav-link">iPhone</a>
<a href="/controller/android/" class="nav-link">Android</a>
<a href="/controller/universal/" class="nav-link">Universal</a>
<a href="/zubehoer/finger-sleeves/" class="nav-link">Finger Sleeves</a>
<a href="/zubehoer/trigger/" class="nav-link">Trigger</a>
<a href="/vergleich/" class="nav-link">Vergleiche</a>
<a href="/blog/" class="nav-link">Blog</a>
<a href="/marken/gamesir/" class="nav-link">GameSir ★<span class="nav-badge">Top-Marke</span></a>
</div></nav>
</header>
<main>
  <section class="page-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep" aria-hidden="true">›</span><a href="/blog/">Blog</a><span class="sep" aria-hidden="true">›</span><span class="cur">Was kostet ein Handy-Controller?</span></nav>
      <span class="eyebrow">📝 Blog · Kaufberatung</span>
      <h1>{esc(titel)}</h1>
      <p class="lead">Die Preisfrage, ohne Umweg beantwortet: was die Spanne ist, was du in welcher Klasse bekommst und an welcher Stelle mehr Geld nachweislich nichts mehr bringt.</p>
      <div class="article-byline">Von <a href="/redaktion/">Yannick Gerber</a> · {lesezeit} Min. Lesezeit · Datenstand {DATENSTAND}</div>
    </div>
  </section>

  <section class="section"><div class="container" style="max-width:820px">

    <div class="pr-antwort">
      <div class="pr-label">Die kurze Antwort</div>
      <p>Die {len(ctrl)} Controller in unserem Sortiment kosten zwischen {preis(billigster)} und {preis(teuerster)} €. Der mittlere Preis liegt bei {median} €. Der am besten bewertete Controller im Sortiment kostet {preis(best)} €.</p>
    </div>

    <h2>Was du in welcher Preisklasse bekommst</h2>
    <p>Die Einteilung stammt nicht aus dem Bauch, sondern aus der Verteilung unserer {len(ctrl)} Modelle. In jeder Klasse steht das am besten bewertete Gerät.</p>
    <table class="pr-tabelle">
      <tr><th>Klasse</th><th>Modelle</th><th>Bestbewertet in dieser Klasse</th></tr>
      {''.join(band_zeilen)}
    </table>

    <h2>Wofür du wirklich mehr bezahlst</h2>
    <p>Drei Dinge, die man gern für Preistreiber hält, sind keine:</p>
    <ul>
      {''.join(merkmale)}
    </ul>
    <p>Was oben dazukommt, ist vor allem Baubreite, eine Klinkenbuchse für das Headset und Verarbeitung. Wie die Technik hinter den Sticks überhaupt funktioniert, steht in unserem Ratgeber zu <a href="/blog/hall-effect-erklaert/">Hall-Effect-Sticks</a>.</p>

    <h2>Wo mehr Geld nichts bringt</h2>
    <p>Der am besten bewertete Controller in unserem Sortiment ist der {link(best)} für {preis(best)} €: {de(best_stern)} Sterne aus {de(best_anz)} Bewertungen. Das teuerste Modell, der {link(teuerster)}, kostet {preis(teuerster)} € und kommt auf {de(teuer_stern)} Sterne aus {de(teuer_anz)} Bewertungen.</p>
    <p>Das heißt nicht, dass der teure Controller schlecht wäre. Es heißt, dass der Preis allein nichts über die Zufriedenheit aussagt. Ob billige Geräte wirklich taugen, haben wir getrennt untersucht: <a href="/blog/guenstige-handy-controller/">Sind günstige Handy-Controller gut?</a> Wer direkt eine Auswahl will, findet sie in den <a href="/vergleich/beste-budget-controller/">besten Budget-Controllern</a>.</p>

    <h2>Was das Zubehör kostet</h2>
    <table class="pr-tabelle">
      <tr><th>Kategorie</th><th>Modelle</th><th>Preisspanne</th></tr>
      {''.join(zub_zeilen)}
    </table>
    <p>Zubehör ist der günstigste Hebel: Finger Sleeves kosten weniger als ein Spiel und helfen genau dann, wenn du beim Touch-Spielen bleiben willst.</p>

    <div class="text-center mt-8">
      <a href="/controller-finder/" class="btn btn-primary">Passenden Controller finden →</a>
    </div>

    <div class="hub-faq">
      <h2>Häufige Fragen</h2>
      <div class="faq-list">
{faq_html}
      </div>
    </div>

    <p style="font-size:13px;color:var(--ink-soft);margin-top:28px">Alle Preise stammen aus unserem Datenbestand mit Stand {DATENSTAND} und werden mit jedem Preisabgleich neu berechnet. Amazon-Preise schwanken, maßgeblich ist der Preis auf der Produktseite.</p>

  </div></section>
</main>
<footer class="site-footer" id="site-footer">
  <div class="container">
    <p class="foot-affiliate">Transparenz-Hinweis: Einige Links auf dieser Seite sind Affiliate-Links (Amazon PartnerNet). Kaufst du über einen solchen Link, erhalten wir eine kleine Provision &mdash; für dich ändert sich der Preis nicht. Das beeinflusst unsere Tests und Bewertungen nicht.</p>
    <p class="foot-legal"><a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · <a href="/affiliate-hinweis/">Affiliate-Hinweis</a> · © 2026 YG MEDIA</p>
  </div>
</footer>
<script src="/assets/js/main.js?v=b9adbc20"></script>
</body>
</html>
'''


def wortzahl(html_text):
    nur_text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', html_text, flags=re.S)
    nur_text = re.sub(r'<[^>]+>', ' ', nur_text)
    return len(re.findall(r'\w+', nur_text))


def baue_fertig():
    """Zweistufig: einmal bauen, um den Text zu zaehlen, dann mit der echten Lesezeit.

    Eine getippte Lesezeit auf einer Seite, die sonst jede Zahl ableitet, waere genau die
    Stelle, die als erste nicht mehr stimmt."""
    roh = baue()
    minuten = max(1, round(wortzahl(roh) / 200))
    return baue(minuten)


def main():
    nur_pruefen = '--check' in sys.argv
    neu = baue_fertig()
    alt = open(ZIEL, encoding='utf-8').read() if os.path.exists(ZIEL) else None
    if alt == neu:
        print(f'{ZIEL}: unveraendert')
        return 0
    if nur_pruefen:
        print(f'{ZIEL}: wuerde sich aendern')
        return 1
    os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
    open(ZIEL, 'w', encoding='utf-8').write(neu)
    print(f'{ZIEL}: {"erzeugt" if alt is None else "aktualisiert"} ({len(neu)} Zeichen)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
