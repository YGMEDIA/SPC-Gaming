#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B7: Der Rueckweg von der Produktseite zu den Uebersichten, die sie fuehren.

WAS GEMESSEN WURDE (04.10.2026, ueber den Inhaltslink-Graph: Links innerhalb von <main>,
ohne Breadcrumb, ohne Navigation und Footer, weil die auf jeder Seite gleich sind und
deshalb kein thematisches Signal tragen):

  777 Inhaltslinks ueber 109 Inhaltsseiten. Gezaehlt wird je QUELLE-ZIEL-PAAR einmal,
  Selbstlinks aus, Stub-Seiten als Quelle aus. Die Verlinkung ist nicht duenn -- sie ist
  EINSEITIG:
  · Alle vier Marken-Hubs verlinken LUECKENLOS ihre Produkte (0 fehlen).
    Alle 14 Produkte dieser vier Marken verlinken NICHT zurueck. 14 von 14.
  · Die fuenf Plattform-Hubs verlinken alle ihre Controller (0 fehlen).
    13 der 28 Controller verlinken auf keinen einzigen Plattform-Hub.
    (Hier stand "29 von 42" -- das mischte zwei Mengen: alle Produkte gegen nur drei
    Hubs. Zubehoer kann per Konstruktion keinen Plattform-Hub haben, und PLATTFORM_HUBS
    unten fuehrt fuenf. Eine Zahl, deren Population man raten muss, ist keine.)
  · Blog-Artikel sind der am schwaechsten verlinkte Seitentyp (Median 3 eingehende
    Inhaltslinks, Minimum 1) -- ausgerechnet die Seiten, ueber die laut STATUS der
    GSC-Traffic kommt. Reviews kommen auf Median 18.

Das ist genau das, was B7 meint ("systematisch statt punktuell"): Es gibt eine Richtung,
und es gibt sie ueberall, aber die Rueckrichtung gibt es nirgends.

DIE REGEL, UND WARUM SIE NICHTS NEUES ERKLAERT
"Jede Produktseite verlinkt zurueck auf jede TAXONOMIE-Seite, die sie listet."

Die Zuordnung wird NICHT gepflegt, sie wird aus dem bestehenden Linkgraph gelesen: Wer ein
Produkt in seinen Karten fuehrt, ist fuer dieses Produkt eine Uebersicht, und das Produkt
verlinkt dorthin zurueck. Damit gibt es keine zweite Wahrheit ueber die Zuordnung, die
veralten koennte -- eine neue Marke, ein neuer Plattform-Hub oder ein umsortiertes Produkt
wirken beim naechsten Lauf von allein.

Taxonomie heisst: die drei Pfad-Familien, die die Informationsarchitektur der Site
ausmachen. NICHT dazu gehoeren Bestenlisten, die Geschenke-Seite und die Startseite --
die sind redaktionelle Auswahl, nicht die Kategorie, in der ein Produkt lebt. Wuerde man
sie mitnehmen, haette jede Produktseite acht Rueckverweise und keiner saegte mehr etwas.

Gemessen mit dieser Regel: jedes der 42 Produkte haengt an mindestens einer Taxonomie-
Seite, Median 3, Maximum 6.

Auch die BESCHRIFTUNG ist abgeleitet: Sie kommt aus der `<h1>` der Zielseite. Eine
getippte Liste von Labels waere die naechste Zahl, die veraltet -- davon hat dieses Repo
genug gesehen.
"""
import glob
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKER = 'HUBLINKS'
# Die Plattform-Hubs stehen als Menge da und nicht als Pfadmuster `controller/*/`, weil
# unter /controller/ auch die Bestenliste liegt -- die ist eine Rangfolge, keine
# Kategorie. Marken- und Zubehoer-Hubs sind dagegen vollstaendig ueber die Pfadtiefe
# bestimmt (genau ein Segment unter der Familie).
PLATTFORM_HUBS = {
    '/controller/ios/', '/controller/android/', '/controller/universal/',
    '/controller/tablet/', '/controller/mini-gamepad/',
}


def ist_taxonomie(url):
    """Ist diese URL eine Uebersicht, in der ein Produkt lebt?"""
    if url in PLATTFORM_HUBS:
        return True
    return (url.startswith(('/marken/', '/zubehoer/'))
            and url.endswith('/') and url.count('/') == 3)


def _rumpf(text):
    """Nur der Inhaltsbereich: <main> ohne Breadcrumb-nav, ohne script/style.

    Navigation und Footer stehen auf jeder Seite und tragen deshalb kein thematisches
    Signal -- wer sie mitzaehlt, misst, dass jede Seite mit jeder verbunden ist.
    """
    m = re.search(r'<main\b.*?</main>', text, re.S)
    s = m.group(0) if m else ''
    s = re.sub(r'<nav\b.*?</nav>', ' ', s, flags=re.S)
    return re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S)


_ROBOTS = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*content="[^"]*noindex', re.I)
_REFRESH = re.compile(r'<meta[^>]+http-equiv=["\']refresh["\']', re.I)


def ist_stub(text):
    """Noindex oder Weiterleitung. Ein Link von hier traegt kein Crawl-Signal.

    Geprueft wird das META-TAG, nicht das WORT. Die erste Fassung war
    `'noindex' in text` ueber die ganze Datei -- ein Hub, dessen Prosa das Wort erwaehnt
    ("Altmodelle stehen auf noindex"), galt damit als Weiterleitung, und alle Produkte
    dieses Hubs verloren ihre Uebersicht. Schlimmer: Der vom Gate vorgeschlagene Fix haette
    den Rueckweg-Block auf sieben Produktseiten GELOESCHT und den Lauf rot gelassen. Ein
    Gate, aus dem es keinen Ausweg gibt ausser dem Zuruecknehmen eines korrekten Satzes,
    hat die falsche Regel.

    Gemessen: Drei Longtail-Datenblaetter (ipega-pg-9023, ipega-pg-9083s, mocute-050)
    hatten GENAU EINE eingehende Quelle, und die war in beiden Faellen eine
    noindex-Weiterleitung (`/marken/ipega/`, `/marken/mocute/`). Fuer einen Crawler sind
    diese Seiten damit verwaist -- das Waisen-Gate in verify.py hat sie trotzdem
    durchgewunken, weil es Links von Stub-Seiten mitzaehlte.
    """
    kopf = text[:text.index('</head>') + 7] if '</head>' in text else text[:4000]
    return bool(_ROBOTS.search(kopf) or _REFRESH.search(kopf))


# Eine Produktkarte. NUR solche Links begruenden eine Zuordnung -- ein redaktioneller
# Vergleichssatz im Fliesstext begruendet keine. Die erste Fassung las JEDEN Link in
# <main>, und damit standen vier falsche Saetze live: Der Black-Shark-KUEHLER sagte
# "steht auch in dieser Uebersicht: Razer Controller 2026" (einziger Hub-Link der Seite,
# Quelle war ein Satz auf dem Razer-Hub, der ihn als Alternative empfiehlt), ein
# Backbone-Produkt nannte den 8BitDo-Hub, ein GameSir-Produkt den Razer-Hub, und ein
# Teleskop-Controller den Mini-Gamepad-Hub. Das ist das GEGENTEIL des B7-Ziels: ein
# falsches thematisches Signal mit falschem Ankertext.
_KARTE_RE = re.compile(r'<article[^>]*class="[^"]*\bpcard\b[^"]*"[^>]*>.*?</article>', re.S)
# Query und Anker gehoeren nicht zum Ziel, schliessen den Link aber auch nicht aus. Die
# erste Fassung verlangte `[^"#?]*` bis zum Anfuehrungszeichen und sah `/x/?from=hub`
# ueberhaupt nicht -- das Produkt verlor dadurch seine Uebersicht.
_HREF_RE = re.compile(r'href="(/[^"]*)"')


def _kartenziele(rumpf):
    """Die internen Ziele aller Produktkarten eines Seitenrumpfs, ohne Query und Anker."""
    aus = set()
    for k in _KARTE_RE.finditer(rumpf):
        for m in _HREF_RE.finditer(k.group(0)):
            z = m.group(1).split('?')[0].split('#')[0].rstrip('/')
            if z:
                aus.add(z)
    return aus


def _seiten():
    return sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True))


def _url(pfad):
    rel = os.path.relpath(pfad, ROOT).replace(os.sep, '/')
    return '/' if rel == 'index.html' else '/' + rel.rsplit('/', 1)[0] + '/'


def taxonomie_karte():
    """{produkt-detail-url ohne Schraegstrich: [(hub-url, beschriftung), ...]}.

    EIN Durchgang ueber alle Seiten, das Ergebnis wird vom Aufrufer wiederverwendet.
    Generator und Sync rufen dieselbe Funktion -- eine Quelle fuer die Zuordnung.
    """
    karte, labels, ohne_h1 = {}, {}, []
    for f in _seiten():
        t = open(f, encoding='utf-8').read()
        if ist_stub(t):
            continue
        u = _url(f)
        if not ist_taxonomie(u):
            continue
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
        if not h1:
            # Ohne h1 gibt es keine Beschriftung. Die erste Fassung wich still auf die URL
            # aus, und dann stand "<a href=...>/zubehoer/trigger/</a>" als Satzbaustein auf
            # sieben Produktseiten -- bei gruenem Lauf. Lieber ein Befund als ein Satz, den
            # niemand so schreiben wuerde.
            ohne_h1.append(u)
            continue
        # html.unescape VOR esc(): Sonst wird aus "&amp;" im h1 ein sichtbares "&amp;amp;".
        # verify.py macht das an der entsprechenden Stelle richtig; hier fehlte es.
        labels[u] = re.sub(r'\s+', ' ',
                           html.unescape(re.sub(r'<[^>]+>', '', h1.group(1)))).strip()
        for ziel in _kartenziele(_rumpf(t)):
            karte.setdefault(ziel, set()).add(u)
    return ({z: sorted((u, labels[u]) for u in hubs if u in labels)
             for z, hubs in karte.items()}, sorted(ohne_h1))


def hublinks_html(detail, karte, esc):
    """Der Block fuer EINE Produktseite, oder '' wenn keine Uebersicht sie fuehrt.

    Bewusst knapp und ohne Ueberschrift mit Rangfolge-Anspruch: Das ist Navigation, kein
    Inhalt, und soll den Leser nicht ein zweites Mal durch die Kaufentscheidung schicken.
    """
    hubs = karte.get((detail or '').rstrip('/'), [])
    if not hubs:
        return ''
    teile = ' · '.join(f'<a href="{esc(u)}">{esc(t)}</a>' for u, t in hubs)
    wort = 'dieser Übersicht' if len(hubs) == 1 else 'diesen Übersichten'
    return (f'<p class="hublinks">Dieses Modell steht auch in {wort}: {teile}</p>')


def block(inhalt):
    """Leerer Inhalt ergibt KEINEN Block.

    Die erste Fassung umhuellte auch den leeren String und schrieb damit auf jede Seite
    ohne Hinweis ein leeres Markerpaar. Fuer den Leser unsichtbar, fuer das Gate aber ein
    Hinweis, der da nicht sein soll -- und genau daran ist der erste Lauf des
    B10-Gates rot geworden, mit 27 Meldungen.
    """
    if not inhalt:
        return ''
    return f'<!-- {MARKER}:START -->\n{inhalt}\n<!-- {MARKER}:END -->'


def entferne(s):
    return re.sub(rf'<!-- {MARKER}:START -->.*?<!-- {MARKER}:END -->\n?', '', s, flags=re.S)
