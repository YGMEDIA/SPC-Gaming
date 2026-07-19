# 2026-07-19 · system · GA4-Tracking end-to-end verifiziert (§A8 geschlossen)

## Was
Live-Test des kompletten Tracking-Pfads durch Claude Code im Browser (Auftrag Yasin): (1) Vor Consent: GTM nachweislich nicht geladen (Consent Mode Gate §C1 ✓). (2) Nach "Alle akzeptieren": GTM-PV7MKJ8P + G-Q1EK5X7PTC geladen. (3) Kaufen-Klick (G8 Galileo): dataLayer-Push {event: affiliate_click, product_name, destination} mit gtm.uniqueEventId. (4) Netzwerk-Beweis via Performance-API: /g/collect-Hits an region1.google-analytics.com mit en=page_view, en=affiliate_click + ep.product_name=gamesir-g8-galileo, en=click. §A8-Befund damit GESCHLOSSEN.

## Wie/Anmerkungen
Browser-Pane auf Live-Site; Pane-Netzwerklog griff zu kurz, deshalb performance.getEntriesByType('resource') als Beweisquelle (zeigt gesendete Fetches inkl. Query-Parameter). Button-Hydration §A3 nebenbei bestätigt (target=_blank, rel="nofollow sponsored noopener", href aus data-asin gebaut). 1 Test-Event (affiliate_click, 19.07.) ist in den echten GA4-Daten.

## Verify
en=affiliate_click + ep.product_name im gesendeten Collect-Request = maschineller Beweis. Yasin kann optional in GA4 → Echtzeit gegenprüfen.
