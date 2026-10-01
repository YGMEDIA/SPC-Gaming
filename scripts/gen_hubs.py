# -*- coding: utf-8 -*-
"""Hub-Seiten (iOS/Android/Universal) + /produkte/:
   1) Produktkarten statisch pre-rendern (GEO: KI-Crawler sehen Inhalte ohne JS)
   2) SEO-Editorial + FAQ ergänzen
   3) ItemList/BreadcrumbList/FAQPage-Schema
"""
import json, re, html

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://smartphone-controller.com'
items = json.load(open(f'{ROOT}/assets/data/products.json'))

def esc(s): return html.escape(str(s), quote=True)

def marker(name, inhalt):
    """Generierten Block zwischen Marker setzen, damit der naechste Lauf ihn findet."""
    return f'<!-- {name}:START -->\n{inhalt}\n<!-- {name}:END -->'


def _div_ende(s, start):
    """Index hinter dem </div>, das das bei `start` geoeffnete <div> schliesst.
    Regex kann das nicht: die Karten enthalten selbst </div>, ein nicht-gieriges
    Muster bricht beim ersten ab, ein gieriges frisst den Rest der Seite."""
    i, tiefe = start, 0
    for m in re.finditer(r'<(/?)div\b[^>]*?(/?)>', s[start:]):
        if m.group(2) == '/':
            continue
        tiefe += -1 if m.group(1) else 1
        if tiefe == 0:
            return start + m.end()
    raise ValueError('kein schliessendes </div> gefunden')


def setze_karten(s, grid_id, cards):
    """Karten in ein Grid schreiben, egal ob es leer oder schon gefuellt ist.
    Vorher verlangte das Muster ein LEERES Grid (`>\\s*</div>`): ein zweiter Lauf war
    damit zwar folgenlos, aber der Generator hat seine Hauptaufgabe stumm uebersprungen.
    Eine Aenderung an products.json waere auf diesen vier Seiten nie angekommen."""
    m = re.search(rf'<div[^>]*id="{grid_id}"[^>]*>', s)
    if not m:
        raise ValueError(f'Grid #{grid_id} nicht gefunden')
    ende = _div_ende(s, m.start())
    return s[:m.end()] + cards + '\n</div>' + s[ende:]

# Der Altbestand traegt noch keine Marker. Damit der erste Lauf nach dieser Aenderung
# aufraeumt statt ein drittes Exemplar danebenzusetzen, kennt jeder Blockname zusaetzlich
# die Form, in der er frueher geschrieben wurde.
_ALTFORM = {
    # seo_text() + faq_html() stehen immer zusammen; das <style> am Ende von faq_html()
    # ist der eindeutige Abschluss.
    'HUB-SEO': re.compile(r'\s*<div class="hub-seo".*?<style>\.hub-faq .*?</style>', re.S),
}
# Die drei Schema-Typen, die dieser Generator erzeugt. Auf den Hub-Seiten stammt jeder
# Block dieser Typen von hier; handgepflegte gibt es dort nicht (Stand HEAD 781ef1c: genau
# drei Bloecke je Hub, alle aus diesem Script).
_SCHEMA_TYPEN = {'ItemList', 'BreadcrumbList', 'FAQPage'}


def entferne_block(s, name):
    """Block aus frueheren Laeufen entfernen, inklusive nachgestelltem Zeilenumbruch.
    Ohne das Entfernen haengt jeder Lauf an: am 30.09. standen SEO-Text und alle drei
    Schemas doppelt auf allen drei Haupt-Hubs, FAQPage inklusive."""
    s = re.sub(rf'\n?<!-- {name}:START -->.*?<!-- {name}:END -->\n?', '', s, flags=re.S)
    if name in _ALTFORM:
        s = _ALTFORM[name].sub('', s)
    if name == 'HUB-SCHEMA':
        def weg(m):
            try:
                d = json.loads(m.group(1))
            except Exception:
                return m.group(0)
            return '' if isinstance(d, dict) and d.get('@type') in _SCHEMA_TYPEN else m.group(0)
        s = re.sub(r'\n?<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
                   weg, s, flags=re.S)
    return s

def card_html(p, featured=False):
    """Identisches Markup wie hub-render.js/produkte.js — JS überschreibt später 1:1."""
    specs = ''.join(f'<span class="spec-tag"><span class="k">{esc(s[0])}</span> {esc(s[1])}</span>'
                    for s in (p.get('specs') or [])[:3])
    detail = f'<a href="{esc(p["detail"])}" class="btn-detail">Mehr erfahren</a>' if p['detail'] else ''
    img = f' data-img="{esc(p["img"])}"' if p.get('img') else ''
    icon = ('❄️' if p['platform'] == 'kuehler' else '🧤' if p['platform'] == 'finger-sleeves' else '🎯') \
        if p['type'] == 'zubehoer' else '🎮'
    return f'''
      <article class="pcard{' featured' if featured else ''}" data-product="{esc(p['slug'])}">
        <div class="pcard-img"><div class="product-icon">{icon}</div></div>
        <div class="pcard-body">
          <div class="pcard-brand">{esc(p.get('brand') or '—')}</div>
          <h2 class="pcard-name">{esc(p['name'])}</h2>
          {f'<p class="pcard-claim">{esc(p["claim"])}</p>' if p.get('claim') else ''}
          <div class="pcard-specs">{specs}</div>
          <div class="pcard-foot">
            <div class="price-row"><span class="price">{esc(p.get('price') or '—')}</span><span class="in-stock">Verfügbar</span></div>
            <div class="pcard-actions">{detail}<a class="btn-amazon" data-asin="{esc(p['asin'])}" data-product="{esc(p['slug'])}" href="#"{img}>Kaufen →</a></div>
          </div>
        </div>
      </article>'''

def hub_list(platform):
    return [p for p in items if p['type'] == 'controller' and
            platform in (p.get('worksOn') or [p['platform']])]

def itemlist_schema(name, url, lst):
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "url": url,
            "numberOfItems": len(lst),
            "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                 "name": f"{p['brand']} {p['name']}" if p['brand'].lower() not in p['name'].lower() else p['name'],
                                 "url": DOMAIN + (p['detail'] or '/produkte/')} for i, p in enumerate(lst)]}

def bc_schema(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u}
                                for i, (n, u) in enumerate(crumbs)]}

def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def faq_html(faqs):
    inner = ''.join(f'<div class="faq-item"><h3 class="faq-q">{esc(q)}</h3><p class="faq-a">{esc(a)}</p></div>' for q, a in faqs)
    return f'''
      <div class="hub-faq" style="max-width:820px;margin:48px auto 0">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:8px;letter-spacing:-.01em">Häufige Fragen</h2>
        <div class="faq-list" style="margin-top:8px">{inner}</div>
      </div>
      <style>.hub-faq .faq-item{{border-bottom:1px solid var(--line);padding:16px 0}}.hub-faq .faq-item:last-child{{border-bottom:none}}.hub-faq .faq-q{{font-size:16px;font-weight:700;margin-bottom:8px}}.hub-faq .faq-a{{font-size:14px;color:var(--ink-soft);line-height:1.65}}</style>'''

def seo_text(paras, h2):
    inner = ''.join(f'<p style="font-size:15px;line-height:1.7;color:var(--ink-soft);margin-bottom:14px">{p}</p>' for p in paras)
    return f'''
      <div class="hub-seo" style="max-width:820px;margin:48px auto 0">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:14px;letter-spacing:-.01em">{h2}</h2>
        {inner}
      </div>'''

# ============================================================
# Inhalte pro Hub
# ============================================================
HUBS = {
 'controller/ios/index.html': dict(
   platform='ios',
   crumbs=[('Home','/'),('Controller','/controller/'),('iPhone','/controller/ios/')],
   list_name='Die besten iPhone-Controller 2026',
   new_desc='Die besten Controller für iPhone 15, 16 & 17 im Vergleich: USB-C-Clips wie Backbone One & GameSir G8 sowie Bluetooth-Gamepads — mit Preisen, Bewertungen und ehrlichen Schwächen.',
   seo_h2='iPhone-Controller kaufen: Darauf kommt es an',
   seo=[ 'Seit dem iPhone 15 setzt Apple auf USB-C — und das hat den Controller-Markt verändert: Clip-Controller wie der <a href="/controller/universal/gamesir-g8-galileo-review/">GameSir G8 Galileo</a> oder der <a href="/controller/ios/backbone-one-2-review/">Backbone One (2. Gen)</a> stecken direkt am Port und spielen praktisch ohne Input-Lag. Für ältere iPhones mit Lightning-Anschluss ist die Auswahl stark eingeschränkt — dort führt der Weg fast nur über Bluetooth-Gamepads oder die Lightning-Version des Backbone One.',
        'Grundsätzlich hast du am iPhone zwei Wege: <strong>USB-C-Clip-Controller</strong> (Handy wird eingespannt, minimale Latenz, ideal für Shooter und kompetitives Spielen) oder <strong>Bluetooth-Gamepads</strong> (flexibler, funktionieren auch am iPad und Apple TV, aber mit spürbar mehr Latenz). Für Apple Arcade, Cloud Gaming über Xbox GamePass oder GeForce NOW und native Titel wie Genshin Impact sind beide Wege gut — für PUBG Mobile und CoD Mobile gelten Sonderregeln, die wir in den FAQ erklären.',
        'Unsere Testsieger fürs iPhone: Der <a href="/controller/universal/gamesir-g8-galileo-review/">GameSir G8 Galileo</a> (ca. 80 €) mit Hall-Effect-Sticks als Gesamtsieger, der <a href="/controller/ios/backbone-one-2-review/">Backbone One</a> (ca. 63 €) für das beste App-Ökosystem und der <a href="/controller/universal/gamesir-x5-lite-review/">GameSir X5 Lite</a> (ca. 45 €) als Preistipp.'],
   faqs=[('Welcher Controller passt zum iPhone 15, 16 und 17?','Alle USB-C-Clip-Controller — z. B. GameSir G8 Galileo, Backbone One (2. Gen) oder Razer Kishi V3 — passen an iPhone 15 und neuer. Dazu funktionieren alle Bluetooth-Controller mit MFi- oder iOS-Unterstützung.'),
         ('Funktionieren Controller mit älteren iPhones (Lightning)?','Nur eingeschränkt: USB-C-Clips passen nicht. Für iPhone 14 und älter brauchst du entweder die Lightning-Version des Backbone One oder ein Bluetooth-Gamepad wie den abxylute S8.'),
         ('Kann ich mit Controller PUBG Mobile oder CoD Mobile auf dem iPhone spielen?','CoD Mobile ja: Controller werden offiziell unterstützt, Controller-Spieler bekommen eigenes Matchmaking. PUBG Mobile nein: Im normalen Matchmaking sind Controller nicht erlaubt. Die legale Alternative dort sind Trigger-Aufsätze, die physisch aufs Display drücken.'),
         ('Welche iPhone-Spiele unterstützen Controller nativ?','Hunderte — darunter Genshin Impact, Call of Duty: Warzone Mobile, Minecraft, Stardew Valley, alle Apple-Arcade-Titel sowie sämtliche Cloud-Gaming-Dienste (Xbox GamePass, GeForce NOW, PS Remote Play).')]),
 'controller/android/index.html': dict(
   platform='android',
   crumbs=[('Home','/'),('Controller','/controller/'),('Android','/controller/android/')],
   list_name='Die besten Android-Controller 2026',
   new_desc='Android-Controller im Vergleich 2026: USB-C-Clips, Bluetooth-Gamepads & Teleskop-Controller für Samsung, Pixel & Xiaomi — mit Preisen, Bewertungen und ehrlichen Schwächen.',
   seo_h2='Android-Controller kaufen: Darauf kommt es an',
   seo=[ 'Android ist die offenste Plattform fürs Controller-Gaming: Praktisch jedes Bluetooth-Gamepad koppelt sich ohne Umwege, USB-C-Clip-Controller wie der <a href="/controller/universal/gamesir-g8-galileo-review/">GameSir G8 Galileo</a> laufen per Plug-and-Play, und mit Apps wie Mantis lassen sich sogar Spiele ohne native Controller-Unterstützung per Key-Mapping steuern — eine Freiheit, die es auf dem iPhone so nicht gibt.',
        'Die Wahl hängt von deinem Spielstil ab: <strong>USB-C-Clips</strong> (GameSir, Razer Kishi) für minimale Latenz und kompetitives Spielen, <strong>Teleskop-Bluetooth-Controller</strong> (ShanWan, Trust) als günstiger Einstieg ab 30 €, oder <strong>klassische Gamepads</strong> (8BitDo, Mars Gaming) mit Handy-Halterung, wenn du denselben Controller auch am PC oder an der Switch nutzen willst.',
        'Wichtig für Samsung-Nutzer: In Kombination mit Samsung DeX oder dem integrierten Game Booster laufen Controller besonders rund. Und wer Wert auf Langlebigkeit legt, achtet auf Hall-Effect-Sticks (GameSir G8, EasySMX M15, 8BitDo Ultimate Mobile) — sie verhindern den gefürchteten Stick-Drift dauerhaft.'],
   faqs=[('Welcher Controller ist der beste für Android?','Unser Gesamtsieger ist der GameSir G8 Galileo (ca. 80 €, USB-C, Hall-Effect). Preistipp unter den Clip-Controllern ist der GameSir X5 Lite (ca. 45 €). Wer ein klassisches Gamepad will, greift zum 8BitDo Ultimate Mobile (ca. 45 €).'),
         ('USB-C oder Bluetooth — was ist besser am Android-Handy?','USB-C hat praktisch keinen Input-Lag und lädt teilweise das Handy durch (Pass-Through). Bluetooth ist flexibler und funktioniert auch am Tablet oder TV — hat aber je nach Modell 20–60 ms mehr Latenz.'),
         ('Warum wird mein Bluetooth-Controller in PUBG Mobile gesperrt?','PUBG Mobile blockiert Controller im normalen Matchmaking aktiv, um Fairness zu wahren — erlaubt sind Trigger-Aufsätze, die physisch aufs Display drücken (siehe unsere Trigger-Kategorie). Anders CoD Mobile: Dort ist der Controller-Support offiziell, mit eigenem Controller-Matchmaking.'),
         ('Funktionieren Android-Controller auch am Smart-TV?','Die meisten Bluetooth-Modelle ja — praktisch für Cloud Gaming am Fernseher über GeForce NOW oder Xbox GamePass. USB-C-Clip-Controller sind dagegen fest ans Handy gebunden.')]),
 'controller/universal/index.html': dict(
   platform='universal',
   crumbs=[('Home','/'),('Controller','/controller/'),('Universal','/controller/universal/')],
   list_name='Die besten Universal-Controller 2026',
   new_desc='Universal-Controller 2026 im Vergleich: Ein Controller für iPhone, Android, PC und Switch — Multi-Plattform-Modelle mit Preisen, Bewertungen und ehrlichen Schwächen.',
   seo_h2='Universal-Controller: Ein Gerät für alles',
   seo=[ 'Universal-Controller lösen ein Alltagsproblem: Wer iPhone und Android-Tablet besitzt, am PC spielt oder eine Switch im Haus hat, will nicht für jedes Gerät einen eigenen Controller kaufen. Multi-Plattform-Modelle wie der <a href="/produkte/abxylute-s8/">abxylute S8</a> (iPhone/iPad/Android/Switch 1 & 2) oder der <a href="/produkte/marsgaming-mgp-bt2/">Mars Gaming MGP-BT2</a> wechseln per Tastenkombination zwischen den Plattform-Modi.',
        'Technisch gibt es zwei Bauformen: <strong>Teleskop-Controller</strong> (GameSir X2s, HELLCOOL) spannen das Handy direkt ein und sind die kompakteste Lösung unterwegs. <strong>Klassische Gamepads</strong> (abxylute S8, Mars Gaming) brauchen einen Handy-Ständer, funktionieren dafür aber an jedem Bildschirm — vom Tablet bis zum Smart-TV.',
        'Achte beim Kauf auf zwei Dinge: Hall-Effect-Sticks für Langlebigkeit (GameSir G8, Kishi V3 Pro, EasySMX M15) und die Verbindungsart — USB-C-Modelle wie der <a href="/produkte/viture-8bitdo/">VITURE × 8BitDo</a> haben keinen Input-Lag, Bluetooth-Modelle sind flexibler einsetzbar.'],
   faqs=[('Was ist ein Universal-Controller?','Ein Controller, der mehrere Plattformen unterstützt — typischerweise iOS, Android, PC und oft Nintendo Switch. Der Plattform-Modus wird meist per Tastenkombination beim Einschalten gewählt.'),
         ('Funktioniert ein Controller wirklich an iPhone UND Android?','Ja — alle Bluetooth-Controller in dieser Kategorie koppeln sich mit beiden Systemen. Bei USB-C-Clips gilt: iPhone ab Modell 15 (USB-C-Port), Android sowieso.'),
         ('Welcher Universal-Controller ist der beste?','Als Clip-Controller: der GameSir G8 Galileo (Testsieger, ca. 80 €). Als klassisches Multi-Plattform-Gamepad: der abxylute S8 (ca. 46 €, inkl. Switch-2-Support, 4,3 Sterne).')]),
}

# ============================================================
# Ausführung nur bei direktem Aufruf — die Funktionen oben sind
# importierbar (sync_new_products.py nutzt card_html/hub_list/
# itemlist_schema für driftfreies Nachrüsten neuer Produkte).
# ACHTUNG: Dieses Skript ist NICHT idempotent (SEO-Text + Schemas
# würden bei erneutem Lauf doppelt eingefügt) — nie zweimal laufen lassen.
# ============================================================
if __name__ == '__main__':
    for path, cfg in HUBS.items():
        f = f'{ROOT}/{path}'
        s = open(f, encoding='utf-8').read()
        lst = hub_list(cfg['platform'])
        cards = ''.join(card_html(p, i == 0) for i, p in enumerate(lst))
        count_label = f'{len(lst)} Modelle'

        # 1) Statisches Pre-Rendering in den hubGrid
        s = setze_karten(s, 'hubGrid', cards)
        # 2) Zähler statisch
        s = s.replace('<span class="hub-count" id="hubCount">Lädt …</span>',
                      f'<span class="hub-count" id="hubCount">{count_label}</span>')
        # 3) Meta-Description ersetzen
        s = re.sub(r'(<meta name="description" content=")[^"]*(")',
                   r'\g<1>' + cfg['new_desc'] + r'\g<2>', s)
        # 4) SEO-Text + FAQ vor dem "Alle Controller"-Backlink einfügen.
        # Marker-Idempotenz (P-11): erst den Block der Vorlaeufe entfernen, dann neu setzen.
        # Ohne das haengte jeder Lauf an — am 30.09. standen nach einem zweiten Lauf SEO-Text
        # und alle drei Schemas doppelt auf allen drei Haupt-Hubs, inklusive FAQPage. Das ist
        # ein §A4-Verstoss und ein Rich-Results-Risiko, und verify zaehlte die Bloecke nur.
        s = entferne_block(s, 'HUB-SEO')
        insert = marker('HUB-SEO', seo_text(cfg['seo'], cfg['seo_h2']) + faq_html(cfg['faqs']))
        anchor = '<div class="text-center mt-8">'
        if anchor in s:
            s = s.replace(anchor, insert + '\n' + anchor, 1)
        else:
            s = s.replace('</main>', insert + '\n</main>', 1)
        # 5) Schema in <head>
        s = entferne_block(s, 'HUB-SCHEMA')
        schemas = [itemlist_schema(cfg['list_name'], DOMAIN + '/' + path.replace('index.html',''), lst),
                   bc_schema(cfg['crumbs']), faq_schema(cfg['faqs'])]
        block = '\n'.join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False)}\n</script>' for x in schemas)
        s = s.replace('</head>', marker('HUB-SCHEMA', block) + '\n</head>', 1)
        open(f, 'w', encoding='utf-8').write(s)
        print(f'✓ {path}: {len(lst)} Karten statisch, SEO-Text, {len(cfg["faqs"])} FAQs, 3 Schemas')

    # ============================================================
    # /produkte/ — alle 40 statisch pre-rendern
    # ============================================================
    f = f'{ROOT}/produkte/index.html'
    s = open(f, encoding='utf-8').read()
    cards = ''.join(card_html(p) for p in items)
    s = setze_karten(s, 'productGrid', cards)
    s = s.replace('id="resultCount">Lädt …<', f'id="resultCount">{len(items)} Produkte<')
    s = s.replace('id="resultCount"><', f'id="resultCount">{len(items)} Produkte<')
    open(f, 'w', encoding='utf-8').write(s)
    # Karten zaehlen, nicht Zeilen mit dem Praefix: grep -c 'class="pcard' traf auch
    # pcard-img, pcard-body und pcard-title und meldete 378 Karten fuer 42 Produkte.
    n = len(re.findall(r'<article class="pcard', s))
    print(f'✓ produkte/index.html: {n} Karten statisch pre-rendert')
