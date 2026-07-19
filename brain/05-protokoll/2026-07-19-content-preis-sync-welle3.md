# 2026-07-19 · preis · Welle 3: Karten-price-rows auf Hubs/Marken/Startseite (27 Stellen, 11 Dateien)

**Was:** Beim Fakten-Check für den Tablet-Artikel fiel die U2C-Karte im Tablet-Hub mit 19 € (JSON: 20 €) auf. Ursache: Die statisch gerenderten Karten-price-rows der Hubs, Marken-Seiten und Startseite stammen vom 11.07.-Rendering; Welle 2 hatte sie verfehlt, weil der Audit-Anker nur ±120 Zeichen um den Preis suchte, in Karten liegen Name und price-row aber ~300 bis 900 Zeichen auseinander. Verschärfung: Der Welle-2-Claim-Fix hatte Startseiten-Karten dadurch INKONSISTENT gemacht (Claim 94 €, Preiszeile 99 €).

**Fix:** Generischer pcard-Parser (Name → price-row, 900er-Fenster, Alias-Map Tessen→ROG Tessen / Ultimate 2C→Ultimate 2C Wireless) findet UND ersetzt: 27 price-rows in 11 Dateien (G8 79→80, X5 39→38, Kishi V3 99→94, Kishi V3 Pro 147→149, Backbone One 64→65, U2C 19→20, Tessen 89→75, ozkak-l1r1 18→9 auf produkte/+zubehoer/trigger). Nur Zahlen getauscht, UVP-Label und Format unangetastet (P-1: JS-Renderer erzeugt gleiches Markup aus JSON → Statik wieder byte-konsistent). Gegen-Audit 0 Reststellen. gaming-phones (ROG Phone, kein JSON-Produkt) bewusst ausgenommen.

**Verify:** Skript-Gegen-Audit 0 · verify.py GRÜN (101 Seiten, 227 Schemas) · Sitemap-lastmod 11 Seiten.

**Gelernt (Rückfluss preis-loop):** Der pcard-Parser MIT 900er-Fenster und Alias-Map ist ab jetzt das Standard-Audit-Werkzeug (Träger-Klasse h der Checkliste); ±120-Fenster-Greps übersehen Karten-Layouts systematisch. Und: Teil-Fixes (nur Claims) können Karten in sich inkonsistent machen — immer Claim UND price-row im selben Lauf prüfen.
