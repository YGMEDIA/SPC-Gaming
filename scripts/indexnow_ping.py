# -*- coding: utf-8 -*-
"""IndexNow-Ping an Bing & Co. (Block C). Meldet URLs sofort zur Indexierung.

Nutzung:
  python3 scripts/indexnow_ping.py --all            # alle Sitemap-URLs melden
  python3 scripts/indexnow_ping.py URL [URL ...]    # einzelne URLs melden
Nach jedem inhaltlichen Deploy laufen lassen (deploy-loop Schritt 5).
"""
import json, re, sys, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "smartphone-controller.com"
KEY = "c3e41f387a9193f67de7196c7ae7bb50"

def sitemap_urls():
    sm = open(os.path.join(ROOT, "sitemap.xml")).read()
    return re.findall(r"<loc>(https://[^<]+)</loc>", sm)

def ping(urls):
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls[:10000],
    }).encode()
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow", data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status

if __name__ == "__main__":
    args = sys.argv[1:]
    urls = sitemap_urls() if (not args or args[0] == "--all") else args
    status = ping(urls)
    # 200/202 = angenommen
    print(f"IndexNow: {len(urls)} URLs gemeldet, HTTP {status}")
    sys.exit(0 if status in (200, 202) else 1)
