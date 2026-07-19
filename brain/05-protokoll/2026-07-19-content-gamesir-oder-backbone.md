# 2026-07-19 · content · Neuer Marken-Vergleich "GameSir oder Backbone?" (P-5)

**Was:** Neuer Blog-Artikel `/blog/gamesir-oder-backbone/` für das GSC-Query-Cluster aus Lauf 1 (5+ Varianten, de+en: "gamesir oder/vs backbone", "backbone vs gamesir", "is gamesir better than backbone?"). Bislang gab es dafür keine passende Seite, nur das Modell-Duell. Sitemap 97 → 98 URLs.

**Wie (P-5 komplett):** verdict-box mit Direktantwort → 7 H2-Sektionen (1.034 Wörter netto) → 4 FAQs → Related-Box (4 Links) → Finder-CTA. Article + BreadcrumbList + FAQPage-Schema, OG komplett. Blog-Index: Karte an Position 1 + ItemList-Schema auf 14 Einträge neu nummeriert. llms.txt +1. Key-Visual als eigene SVG-Illustration im Corporate-Look (zwei Grip-Silhouetten hell/blau, Energie-Impuls, kein Text im Bild), Browser-verifiziert; og:image bleibt og-default.jpg bis Yasins fotoreales Bild kommt (SVG für Social ungeeignet, Muster 19.07.).

**Inhaltliche Linie:** Marken-Frage, nicht Modell-Frage (Abgrenzung zum Duell dokumentiert in keyword-strategie.md). Kernthese aus belegten Sortiments-Daten: GameSir = Technik pro Euro (Hall-Effect ab 38 €, Pass-Through, Klinke, kein Abo), Backbone = Gesamterlebnis (138 g, Verarbeitung, App, PS-Anbindung, aber Backbone+-Abo für Vollumfang). §A6: je Marke 3 ehrliche Schwächen benannt (GameSir: funktionales Design, 230 g, X2s nur 3,8 Sterne · Backbone: keine Hall-Sticks, kein Pass-Through, Abo + Pro-Preis 189 €). Eine FAQ spiegelt wörtlich die englische GSC-Query ("Ist GameSir besser als Backbone?").

**Warum so:** Blog-first ist GSC-bewiesen (alle bisherigen Klicks über Blog); die Marken-Frage ist BOFU-nah und füttert beide Marken-Hubs + das Duell + 5 Reviews mit interner Verlinkung. Der zuvor erledigte Preis-Sync (Welle 2) war Voraussetzung: Der Artikel nennt 8 Preise, alle == products.json.

**Verify (maschinell):** Title-Kern 57 ≤ 62 · 1.034 Wörter ≥ 700 · 10 unique Geld-Link-Ziele ≥ 3 · FAQ-Schema == sichtbarer Text (4/4 stringgleich) · 8 Preis-Nennungen gegen products.json geprüft · Bewertungs-Claims (4,4/1.200+ · 4,4/900+ · 3,8) JSON-gedeckt · kein Em-Dash · `scripts/verify.py` GRÜN (99 Seiten, 221 Schemas, Sitemap 98).

**Braucht Yasin (in STATUS eingetragen):** Fotoreales Key-Visual generieren. Prompt: "Zwei Smartphone-Gaming-Controller liegen einander gegenüber auf dunkler navy-blauer Fläche, der linke in hellem Weiß-Silber, der rechte in kräftigem Blau, zwischen ihnen ein feiner blauer Energie-Funke, dramatisches seitliches Licht, Produktfotografie, 16:9". Danach: JPG-Optimierung + Einbau + og:image-Umstellung durch Claude Code (bewiesener Workflow).

**Gelernt:** Ein Query-Cluster mit deutschen UND englischen Varianten braucht keine englische Seite: deutsche Antwort + wörtlich gespiegelte Frage-FAQ deckt beide; Erfolgskontrolle im gsc-loop (auch die en-Queries beobachten).
