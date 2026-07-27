# 2026-07-27 · gsc-loop · Lauf 2 (Fenster 18.-26.07.) + Maßnahme Direktvergleich G8 Plus vs. Kishi V3 Pro

**Was:** Yasins Paket 2 ausgewertet — das erste Fenster NACH den großen 18./19.07.-Deploys. Rohdaten: `03-research/raw/gsc/2026-07-27.md`.

**Kernbefund: Die Deploys wirken.** Ø Position 16,8 → **13,6** (minus 3,2 in einer Woche), CTR 1,6 → 2,3 %, 7 Klicks. Wichtigste Struktur-Änderung: Die Klick-Träger drehen vom Blog (Lauf 1: alle Klicks) auf **Startseite (4) und Zubehör-Hubs** (Trigger 1 Klick/23 Impr., Finger-Sleeves 1/13) — die Geld-Seiten greifen. "controller für handy" konvertierte bei einer einzigen Impression.

**Diagnose statt Panik bei zwei Auffälligkeiten:** (1) www-URLs in den Top-Seiten (ios-Hub 16 Impr.) — live geprüft: 301 + Canonical korrekt, Google konsolidiert nur noch, kein Fix nötig. (2) verbindet-nicht nach der Title-Schärfung aus den Top-Seiten verschwunden — Ranking-Neubewertung nach Title-Änderung ist normales Verhalten, Lauf 3 entscheidet. Ebenso beobachten: welche-spiele-controller 75 Impr./0 Klicks (Lauf 1: 2 Klicks).

**Indexierung:** Bericht hinkt nach (Stand ~10.07., 53/65 wie Baseline) — Punkt-3-Fragen aus Lauf 1 bleiben offen. NEU aus der Aufschlüsselung: eingereichte Seiten nur 10/60 indexiert (alter Sitemap-Stand), "Gefunden, nicht indexiert" 47 bleibt der Engpass. Gegenmaßnahme: Yasin beantragt Indexierung für 6 Prio-URLs (siehe Braucht Yasin).

**Maßnahme aus den Daten (Warteschlangen-Kandidat bestätigt):** Das Razer-Cluster formiert sich (razer-Queries, marken/razer 10 Impr., kishi-v3-review 9) → Direktvergleich **/vergleich/g8-plus-vs-kishi-v3-pro/** gebaut (Muster g8-galileo-vs-kishi-v3, BreadcrumbList only). Ehrliches Duell auf Belegstand der Rating-Welle: G8 Plus = Preis-Leistungs-Sieger (90 €, Hall-Sticks+Trigger, BT+Kabel, Switch/Tablet), V3 Pro = besser bewertet (4,4/125 vs. 4,1/457) mit 4 Zusatztasten/TMR/HD-Haptik — die Winner-Box nennt die bessere V3-Pro-Bewertung ausdrücklich. Vor Publish eine unbelegte Tabellenzeile entfernt (G8-Plus-Haptik "Standard-Vibration" stand in keinem Beleg, §A5). Einbau: Vergleichs-Index-Karte, Duell-Links aus beiden Reviews (interne Stärkung = Indexierungs-Engpass), Sitemap 104 URLs, 3 lastmods.

**§A1-Fix nebenbei:** G8-Plus-Review nannte als Verbindung nur "USB-C, kabelgebunden (MFi)" — products.json und der Amazon-Titel (Beleg 21.07.) sagen Bluetooth + USB-C. Zeile korrigiert, bevor das Duell die Divergenz sichtbar gemacht hätte.

**Verify:** verify.py GRÜN (105 Seiten, 231 Schemas, 42 Produkte) · Browser-Sichtung der Duell-Seite (Hero, Kurz-Urteil, Tabelle rendern im Muster-Look) · Sitemap 104 · Commit + Deploy + IndexNow 200.

**Gelernt:** (1) Nach Title-Änderungen Sichtbarkeits-Dellen einpreisen und erst nach 2 Fenstern urteilen. (2) Der GSC-Indexierungsbericht kann Wochen nachhinken — Interpretation immer ans "Letzte Aktualisierung"-Datum binden, sonst zieht man falsche Schlüsse aus alten Zahlen. (3) Query-Cluster in den Daten (Razer) sind der beste Priorisierer für die Content-Warteschlange — der Kandidat lag seit 6 Tagen bereit, die Daten gaben den Startschuss.
