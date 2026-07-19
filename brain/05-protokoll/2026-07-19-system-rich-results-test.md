# 2026-07-19 · system · Rich-Results-Test autonom gefahren (offen seit 11.07., erledigt)

**Was:** Den seit 11.07. offenen Handgriff "Rich-Results-Test" selbst erledigt statt auf Yasin zu warten — das Google-Tool (search.google.com/test/rich-results) braucht keinen Login und läuft in der internen Browser-Pane. 4 Live-URLs getestet, Crawl-Zeitpunkt 18:34-18:37 Uhr = bereits der Video-Deploy-Stand vom Abend.

**Ergebnisse (0 kritische Fehler auf allen 4):**
| URL | Gültige Elemente |
|---|---|
| /controller/universal/gamesir-g8-galileo-review/ | 4: Produkt-Snippets, Händlereinträge, Navigationspfade, **Rezensions-Snippets** |
| /produkte/marsgaming-mgpxpro/ | 4: Produkt, Händler, Breadcrumb, Rezension |
| /produkte/risoka-trigger/ | 3: Produkt, Händler, Breadcrumb |
| /controller-finder/ | 1: Breadcrumb |

Sterne-Snippets sind damit für Reviews UND generierte Produktseiten technisch freigegeben. "Nicht kritische Probleme" bei Händlereinträgen (3 Stück, z. B. beim G8) sind die optionalen Offer-Felder (priceValidUntil, Versand-/Rückgabedetails) — bewusst offen, dafür bräuchten wir belegbare Daten, die wir nicht erfinden (§A5-Geist).

**Wichtig fürs Verständnis:** FAQPage erscheint NICHT mehr als eigener Rich-Result-Typ — Google zeigt FAQ-Rich-Results seit 2023 nur noch für Behörden-/Gesundheitsseiten. Unser FAQPage-Schema bleibt trotzdem korrekt und nützlich (Inhaltsverständnis/GEO), es fehlt nichts.

**Wie (Werkzeug-Lehre):** Der Test lässt sich per URL-Parameter direkt starten: `search.google.com/test/rich-results?url=<encoded-URL>` — das umgeht das fummelige Formular (Enter im Feld startet nichts, der Submit-Button muss geklickt werden). Interne Browser-Pane vorher per resize auf Desktop-Preset bringen, sonst rendert das Tool in einer Mini-Ecke.

**Verify:** Testergebnis-Screens gesichtet + Detailansicht Händlereinträge geöffnet. Kein Site-Change, kein Commit nötig (nur Brain-Doku).

**Gelernt:** Google-Tools ohne Login-Zwang gehören in die Autonomie-Klasse (wie P-9/P-10-Beschaffung) — nicht in "Braucht Yasin". Der Test sollte nach größeren Schema-Änderungen wiederholt werden (nächster Anlass: nach dem Autoren-Paket/Person-Schema, dann /redaktion/ mittesten).
