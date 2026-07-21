# -*- coding: utf-8 -*-
"""Rüstet neu aufgenommene Produkte in die bereits statisch gerenderten Seiten nach.

Warum ein eigenes Script: gen_hubs.py ist NICHT idempotent (SEO-Text und Schemas
würden bei erneutem Lauf doppelt eingefügt). Dieses Script fasst ausschließlich
Karten, Zähler und ItemList-Schemas an und ist idempotent: Produkte, deren Karte
schon im HTML steht, werden übersprungen.

Karten-Markup und ItemList kommen aus gen_hubs.py (Import ohne Nebenwirkung),
damit kein Drift zwischen Generator und Nachrüstung entsteht.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_hubs as G

REFRESH = '--refresh' in sys.argv  # bestehende Karten neu rendern (nach Preis-/Rating-Änderungen)
items = json.load(open(f'{ROOT}/assets/data/products.json'))
G.items = items  # Generator-Funktionen auf den frischen Stand heben

HUB_NAMES = {
    'controller/ios/index.html': ('ios', 'Die besten iPhone-Controller 2026', '/controller/ios/'),
    'controller/android/index.html': ('android', 'Die besten Android-Controller 2026', '/controller/android/'),
    'controller/universal/index.html': ('universal', 'Die besten Universal-Controller 2026', '/controller/universal/'),
}

def insert_card(html, card, after_slug):
    """Karte direkt hinter die Karte von after_slug setzen (Reihenfolge = products.json)."""
    i = html.index(f'data-product="{after_slug}"')
    j = html.index('</article>', i) + len('</article>')
    return html[:j] + card + html[j:]

def replace_card(html, p, featured):
    """Bestehende Karte komplett durch frisch generierte ersetzen (Preise/Ratings/Specs aktuell)."""
    i = html.index(f'<article class="pcard')
    while True:
        j = html.index('</article>', i) + len('</article>')
        if f'data-product="{p["slug"]}"' in html[i:j]:
            break
        i = html.index('<article class="pcard', j)
    return html[:i] + G.card_html(p, featured).lstrip('\n') + html[j:]

def sync_grid(path, produkte, count_pattern=None, count_text=None, schema_cfg=None, refresh=False):
    f = f'{ROOT}/{path}'
    s = open(f, encoding='utf-8').read()
    added, refreshed = [], 0
    for n, p in enumerate(produkte):
        if f'data-product="{p["slug"]}"' in s:
            if refresh:
                vorher = s
                s = replace_card(s, p, featured=(n == 0 and 'pcard featured' in vorher))
                if s != vorher: refreshed += 1
            continue
        assert n > 0, f'{path}: neues Produkt an Position 0, Anker fehlt'
        s = insert_card(s, G.card_html(p), produkte[n - 1]['slug'])
        added.append(p['slug'])
    if count_pattern:
        s, n_cnt = re.subn(count_pattern, count_text.format(n=len(produkte)), s)
        assert n_cnt == 1, f'{path}: Zähler nicht eindeutig ({n_cnt})'
    if schema_cfg:
        name, url = schema_cfg
        neu = json.dumps(G.itemlist_schema(name, G.DOMAIN + url, produkte), ensure_ascii=False)
        s, n_s = re.subn(r'\{"@context": "https://schema\.org", "@type": "ItemList".*?\}\]\}', neu.replace('\\', '\\\\'), s, count=1)
        assert n_s == 1, f'{path}: ItemList-Schema nicht ersetzt'
    open(f, 'w', encoding='utf-8').write(s)
    # Gegenprobe
    check = open(f, encoding='utf-8').read()
    have = len(re.findall(r'<article class="pcard', check))
    assert have == len(produkte), f'{path}: {have} Karten statt {len(produkte)}'
    info = []
    if added: info.append(f'+{len(added)}: {", ".join(added)}')
    if refreshed: info.append(f'{refreshed} aktualisiert')
    print(f'✓ {path}: {have} Karten' + (f' ({" · ".join(info)})' if info else ' (unverändert)'))

for path, (platform, list_name, url) in HUB_NAMES.items():
    lst = G.hub_list(platform)
    sync_grid(path, lst,
              count_pattern=r'<span class="hub-count" id="hubCount">[^<]*</span>',
              count_text='<span class="hub-count" id="hubCount">{n} Modelle</span>',
              schema_cfg=(list_name, url), refresh=REFRESH)

sync_grid('produkte/index.html', items,
          count_pattern=r'(<div class="pf-count" id="resultCount" aria-live="polite">)[^<]*(</div>)',
          count_text=r'\g<1>{n} Produkte\g<2>', refresh=REFRESH)
