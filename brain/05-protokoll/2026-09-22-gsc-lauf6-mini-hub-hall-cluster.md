# 2026-09-22 · gsc-loop · Lauf 6: Erste Erholung + Thin-Page-Fund im stärksten Cluster

**Was:** Lauf 6 ausgewertet (7T 13.-19.09. + 28T 23.08.-19.09.) und zwei datenbelegte Maßnahmen umgesetzt. Rohdaten: `03-research/raw/gsc/2026-09-22.md`.

**Die gute Nachricht: Position 55,9 → 43,5.** Erstmals seit dem 25.07.-Einbruch ein klares Erholungssignal, minus 12,4 Plätze in einer Woche. Die Impressionen sinken zwar weiter (25 → 19), aber das ist das erwartete Bild einer Konsolidierung: weniger, dafür deutlich besser platzierte Rankings.

**Der entscheidende Fund (nur durch die 28-Tage-Sicht sichtbar):** Die stärkste Query der letzten vier Wochen ist **"mini gamepad android" mit 15 Impressionen**, nicht Hall-Effect. Die 7-Tage-Sicht allein hätte das verschleiert (dort nur 2). Und diese Nachfrage landete auf einer **Thin Page**: /controller/mini-gamepad/ hatte 118 Wörter, 3 Karten, keinen SEO-Text und keine FAQs, während der iOS-Hub 1181 Wörter trägt.

**Maßnahme 1 — Mini-Gamepad-Hub auf Standard gebracht (118 → 499 Wörter):**
SEO-Sektion mit drei Absätzen (Abgrenzung Mini-Gamepad vs. Teleskop, Bluetooth-Latenz ehrlich benannt, der fehlende Handy-Halter als echte Einschränkung), 4 FAQs mit FAQPage-Schema, ItemList-Schema, interne Verlinkung zu Android-/iOS-Hub, Budget-Vergleich und dem Hall-Artikel. **Alle Karten neu über `gen_hubs.card_html` gerendert** (driftfrei), damit künftige Preis-Wellen die Seite erfassen.
**Kuratierung bewusst NICHT aufgebläht:** Es blieb bei den 3 wirklich passenden Produkten. Kandidaten wie ShanWan-Modelle oder der abxylute S8 wurden geprüft und verworfen, weil "kompakt genug für die Tasche" aus den Belegdaten nicht sauber ableitbar war (§A5-Geist). Lieber 3 richtige Karten mit Substanz als 6 mit wackliger Begründung.
**Meta-Freeze eingehalten:** Title und Description blieben unangetastet (der Hub ist Impressions-Träger); geändert wurde ausschließlich der Seiteninhalt.

**Befund dabei: eine Geister-Karte.** Eine Karte trug `data-product="abxylute-retro"` im article-Attribut, ein Slug, den products.json nicht kennt. Inhalt und Affiliate-Link gehörten korrekt zum abxylute M4 Snap-On, der Link funktionierte also. Das Problem lag tiefer: Der pcard-Parser des preis-loops und die Sync-Skripte arbeiten über `data-product`, fanden den Slug nicht und hätten die Karte bei **jeder künftigen Preis-Welle stillschweigend übersprungen**. Mit dem Neurendern ist sie weg.

**Maßnahme 2 — Hall-Cluster gestärkt (Warteschlange seit Lauf 4):** Der Träger `blog/hall-effect-erklaert` holt 9 von 19 Impressionen (47 %). Von 6 Produkten mit belegter Hall-Technik in den Specs verlinkte **keines** auf den Erklär-Artikel. Gezielter Pass statt Flächen-Verlinkung: 4 Hand-Reviews (G8 Galileo, X5 Lite, Ultimate 2C, G8 Plus) haben jetzt genau einen kontextuellen Prosa-Link, jeweils an der Stelle, wo die Technik als Vorteil genannt wird. Die 48 Seiten, die "Hall" irgendwo erwähnen, wurden bewusst NICHT alle verlinkt.

**Technische Grenze dokumentiert:** Die zwei GEN-Seiten (scuf-nomad, razer-kishi-ultra) können keinen Link bekommen. `gen_pages.py` jagt alle Texte durch `esc()`, HTML in `desc`/`faqs` ist damit unmöglich. Von Hand nachzurüsten wäre der Generator-Drift-Fehler vom 21.07. — bewusst unterlassen. Falls kontextuelle Links auf GEN-Seiten je gebraucht werden, ist das eine Generator-Änderung als eigenes Paket.

**Verify:** verify.py GRÜN nach jedem Schritt (123 Seiten) · Faktenkontrolle des neuen Hub-Texts maschinell gegen products.json (jede Zahl belegt: 20 €, 4,5/854, 50 €, 56 g) · keine erfundenen Slugs · DOM-Prüfung im Browser (3 Karten mit korrekten ASINs, 3 Schemas, 4 FAQs; Hall-Link sichtbar im Pros-Element) · Schemas enthalten kein HTML · git diff bestätigt: keine Title/Description-Zeile angefasst.

**Offene Beobachtung:** Die Indexierung ist erstmals rückläufig (71 → 66), nicht indexiert 121 → 129, Gründe 6 → 8. Plausibel sind die 16 noindex-Stubs, die in eigene Kategorien wandern. Die Gründe-Tabelle fehlt zum vierten Mal im Paket, deshalb bleibt es eine Hypothese → Lauf-7-Checkliste Punkt 1.

**Neuer Merkposten:** Em-Dash-Altlast aus der Zeit vor der Regel: 17 von 42 products.json-Claims und 101 von 123 HTML-Seiten enthalten Em-Dashes, überwiegend in Titles und Descriptions. Wegen des Meta-Freeze jetzt nicht angefasst; nach Freeze-Ende als eigener kleiner Pass (Claims zuerst, weil sie über die Karten sitewide durchschlagen).

**Gelernt:** (1) **Die 7-Tage-Sicht allein führt in die Irre.** Erst das 28-Tage-Fenster zeigte, dass das stärkste Cluster ein anderes ist als gedacht. Beide Fenster gehören ab jetzt ins Standard-Paket. (2) Nachfrage trifft Thin Page ist der wertvollste Befund überhaupt: Google schickt Nutzer auf eine Seite, die die Frage kaum beantwortet. Solche Paarungen aktiv suchen, statt nur Rankings zu beobachten. (3) Ein falscher Slug in einem Karten-Attribut ist unsichtbar für Menschen und für jedes Sync-Skript. Kartenbestände deshalb gegen products.json rückwärts prüfen, nicht nur vorwärts.
