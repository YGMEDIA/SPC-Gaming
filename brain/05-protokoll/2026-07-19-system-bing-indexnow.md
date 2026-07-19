# 2026-07-19 · system · Block C: Bing + IndexNow live

## Was
Yasin hat Bing Webmaster Tools per GSC-Import verifiziert (Property aktiv, Screenshot 19.07.). Claude Code: IndexNow eingerichtet — Key-Datei im Root (deployt automatisch), `scripts/indexnow_ping.py` (stdlib, meldet Sitemap- oder Einzel-URLs an api.indexnow.org), deploy-loop um Schritt 6 ergänzt. Erst-Ping nach Deploy: 97 URLs, HTTP 202 (angenommen), Key-Datei live verifiziert (HTTP 200).

## Wie/Warum
Script-Variante statt Workflow-Integration: kein .github/workflows-Touch (Menschen-Gate), Ping läuft künftig als Deploy-Loop-Schritt durch Claude Code. IndexNow beschleunigt Bing/Copilot-Indexierung von Tagen auf Stunden — zahlt auf die GEO-Schiene ein (Copilot speist aus dem Bing-Index).

## Verify
Key-Datei live HTTP 200 · Ping HTTP 202 mit 97 URLs · verify.py GRÜN.

## Offen (Yasin)
Bing → Sitemaps-Tab prüfen; falls leer, sitemap.xml einmal manuell einreichen. Erste Performance-Daten in 2-7 Tagen.
