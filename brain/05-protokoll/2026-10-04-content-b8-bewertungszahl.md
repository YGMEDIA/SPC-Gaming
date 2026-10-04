# 2026-10-04 · Content · B8: Die Bewertungszahl ist das zweite Signal

## Was

Maßnahme B8 der Bücher-Synthese (Quelle: Cialdini, Social Proof). *"4,4 Sterne aus 3.147
Bewertungen"* sind zwei Signale, nicht eins: Ein 4,8er aus 12 Bewertungen und ein 4,4er
aus 3.147 sagen etwas völlig Verschiedenes. Wer nur den Wert zeigt, zeigt die halbe
Aussage.

**Gemessen am 04.10.2026**, bevor etwas gebaut wurde:

| | Befund |
|---|---|
| Bewertungs-Badge auf **29** generierten Produktseiten | Wert in **26px, font-weight 800**; Anzahl in **11px, `--ink-dim`** — dem schwächsten Farbton des Systems. Faktor 2,4 in der Größe, blassester Ton. Formuliert als `Amazon (566 Bew.)`. |
| Vier handgepflegte Review-Seiten | Anderes Badge: **28px in `--blue`**, und in der 11px-Zeile stand `Redaktions-Score` — also **gar keine Anzahl**. Dazu ein **Score auf Zehner-Skala** (8,5 bis 9,3 von 10) mit **fünf vollen Sternen**, auf allen vier. Für den Leser heißt ★★★★★ „perfekt". |
| Schema | korrekt: `ratingValue` 4,2–4,4, `bestRating` 5, `reviewCount` gesetzt. §A4 erfüllt, auch die Sichtbarkeit (die Zahl steht als `1.953` mit Tausenderpunkt im Text) |
| Hub-Karten | tragen beide Zahlen gleich groß als Spec-Chip (`Bew. 4,1 (996)`) — hier war nichts zu tun |

Der Kern war also nicht „die Zahl fehlt", sondern **„die Zahl ist zur Fußnote gesetzt"**,
plus eine irreführende Sterne-Darstellung auf vier Seiten.

## Wie

1. **Die Anzahl bekommt eigenes Gewicht.** Eigene Klasse `.rb-count` statt Inline-Stil,
   13px statt 11px, `--ink-soft` statt `--ink-dim`, und ausgeschrieben: aus
   `Amazon (566 Bew.)` wird **`566 Bewertungen bei Amazon`**. Nachgemessen im Browser:
   Wert 26px `#10202f`, Anzahl 13px `#52617a`.
2. **Die Sterne passen zur genannten Skala.** Neue Funktion `_sterne(wert, skala)` rechnet
   das Verhältnis, statt den Rohwert als Fünfer zu lesen. Auf den vier Review-Seiten
   stehen jetzt ★★★★☆ bei 8,5 / 8,7 / 8,9 von 10 und ★★★★★ bei 9,3 — dieselbe
   Rundungsregel wie bei den Amazon-Werten.
3. **Das zweite Signal steht auch dort im Badge.** Die vier Review-Seiten zeigen neben dem
   Redaktions-Score jetzt `bei Amazon 4,2 von 5 aus 706 Bewertungen`. Der Redaktions-Score
   bleibt — er ist Yasins Inhalt, und ihn zu löschen wäre keine B8-Aufgabe.

## Warum so

Der Redaktions-Score ist **nicht** entfernt worden. Er hat keine Datenquelle im Repo und
ist damit redaktionell; was ich beheben konnte, ist die Darstellung, die ihn mit einer
Fünfer-Skala verwechselt. Dass er auf nur vier von dreizehn Review-Seiten steht und
nirgends erklärt ist, bleibt als Frage für Yasin stehen.

Die Hub-Karten sind unverändert: Dort stehen Wert und Anzahl schon im selben Chip, in
derselben Größe und Farbe. Das ist bereits gleichberechtigt; eine Umformulierung hätte
jede Karte jeder Übersichtsseite angefasst, ohne etwas zu verbessern.

## Verify

- **Elf Gates, jedes exit 0**
- **Neues Gate §B8 am ausgelieferten Stand**, über ALLE Badges jeder Seite (heute 33 auf
  33 Seiten, aber ein Gate, das beim ersten aufhört, ist ein stilles Loch):
  1. Wo ein Badge steht, steht die Anzahl — in `.rb-count`, mit einer Ziffer darin
  2. Die Anzahl darf nicht als Inline-Fußnote (`font-size:10/11px`) gesetzt sein
  3. Die Sterne-Glyphen passen zur genannten Skala (`rb-label` „von 5" / „von 10")
- **`scripts/links_batterie.py` von 20 auf 35 Fälle** (22 müssen rot werden, 13 müssen
  grün bleiben), 0 falsch, 0 nicht gegriffen
- Browser nachgemessen: `.rb-num` 26px `rgb(16,32,47)`, `.rb-count` 13px
  `rgb(82,97,122)`; Text `4,3 · von 5 · ★★★★☆ · 566 Bewertungen bei Amazon`

## Gelernt

1. **„Steht die Zahl da?" ist die falsche Frage. Die richtige ist: Wie laut?** Die
   Bewertungszahl war die ganze Zeit vorhanden — in 11px im blassesten Ton, neben einem
   26px-Wert in Schwarz. Ein Gate, das nur auf Anwesenheit prüft, hätte das nie gefunden.
   Deshalb prüft §B8 auch die FORM (eigene Klasse statt Inline-Fußnote).
2. **Eine Darstellung kann falsch sein, obwohl jede Zahl stimmt.** Fünf volle Sterne neben
   „8,5 von 10": Der Score ist korrekt, das Schema ist korrekt, die Glyphen sind es nicht.
   Solche Fehler findet kein Datenabgleich, nur der Blick auf das, was der Leser sieht.
3. **Mein erster Batterie-Fall prüfte am falschen Ort.** „Formulierung der Anzahl
   geändert" editierte die generierte Seite — und wurde korrekt am Generator-Abgleich rot,
   also aus dem richtigen Grund, aber nicht an dem, was das Etikett behauptet. Eine
   Formulierungsänderung ist eine Generator-Änderung.

## Offen für Yasin

- **Der Redaktions-Score** steht auf 4 der 13 Review-Seiten, auf einer Zehner-Skala, ohne
  dass irgendwo erklärt ist, wie er zustande kommt. Entweder auf alle Reviews ausweiten
  und die Methode nennen, oder streichen — beides ist eine redaktionelle Entscheidung.
- **`Bew.` als Spec-Schlüssel** in products.json ist eine Abkürzung, die auf jeder
  Hub-Karte sichtbar wird (`Bew. 4,1 (996)`). Ausgeschrieben wäre sie lesbarer, aber der
  Schlüssel ist Datenkern und seine Änderung zieht durch alle Generatoren.

## Nachtrag: Prüflauf zu B8 (Runde 34), zwei Blocker — beide im Gate

Der Bericht hat **alle 33 Badges faktisch bestätigt** (eigener Nachrechner, Wert und
Anzahl gegen products.json, deutsche Tausenderpunkte, Glyphen verhältnisgerecht, `★+☆ = 5`)
und auch, dass sich auf den 29 generierten Seiten **kein einziger Glyph geändert** hat.
Blockiert wurde am Gate — und zwar genau bei der Eigenschaft, für die B8 gebaut wurde.

**B34-1 · Der `.rb-count`-Test las rohen Text zwischen Tags.** `([^<]*)` verträgt kein
Markup. Die Anzahl mit `<strong>` hervorzuheben — also genau das, was B8 erreichen will —
machte den Lauf **rot**. Das ist wörtlich P-13 Mechanismus 6: *das Gate verteidigt den
Fehler gegen Korrektur.* Umgekehrt genügte **irgendeine Ziffer**: `Platz 3` kam durch.
Dazu wurden Badges in HTML-Kommentaren und `<template>` mitgeprüft, obwohl sie nicht
ausgeliefert werden.

**B34-2 · Die Sterne-Prüfung schaltete sich still selbst ab.** `if _st and _lab:` ohne
`else`. **Sechs** Formen mit fünf vollen Sternen neben „8,7 von 10" blieben grün: `.stars`
als `<span>`, mit zweiter Klasse, mit einfachen Anführungszeichen, ohne `rb-label`, mit
`rb-label` „von 10 Punkten" (fehlerfreies Deutsch) und „von zehn". Und die
**Glyphen-Gesamtzahl** wurde nie geprüft — ★★★★☆☆☆ ging durch, derselbe Fehler wie der
behobene, nur im Nenner.

Das wiegt, weil die vier Seiten mit Zehner-Skala die **handgepflegten** sind: Dort gibt es
keinen Generator-Abgleich, der einspringt. Auf den 29 generierten war §B8 Redundanz, auf
den vier war es die einzige Instanz — und dort hat es nicht gegriffen.

Das Gate ist neu geschrieben: Elemente werden per **Tag-Zählung** geschnitten statt per
Regex, `.stars` tag-unabhängig und klassen-token-genau gematcht, die Skala als erste Zahl
im **tag-freien** `rb-label`-Text gelesen, `★ + ☆ == 5` geprüft, und ein fehlendes
`.stars` oder `rb-label` ist ein **Befund** statt eines Grundes zum Überspringen. Alle
sechs Löcher und alle drei Fehlalarme einzeln nachgemessen.

Übernommen: mein Batterie-Fall „Inline-Fußnote" wurde über den **falschen Zweig** rot (er
entfernte `.rb-count`, statt sie klein zu setzen) · `_RB` war toter Code · der
Code-Kommentar behauptete „dieselbe Größe wie das Skalen-Label" (13px gegen 11px) ·
`„1 Bewertungen"` ohne Singular-Regel · `aria-label="4.3 von 5 Sternen"` mit Punkt, während
sichtbar „4,3" steht — auf den vier Review-Seiten hatte B8 das korrigiert und die 29
liegen gelassen.

**Und eine Zahl in meiner eigenen Doku war zu weit:** „33 Produktseiten, Wert 26px, Anzahl
11px". Gemessen bei HEAD: **29** Seiten mit 26px/800, und **4** mit 28px in `--blue`, die
in der 11px-Zeile `Redaktions-Score` trugen — also **gar keine Anzahl**. Der Faktor 2,4
gilt für die 29; für die vier war es kein Größenverhältnis, sondern ein Fehlen.

**Nebenfix, den der Prüfer gefunden hat und ich nicht erwähnt hatte:** HEAD schrieb auf
`produkte/risoka-finger-sleeves/` `Amazon (3147 Bew.)` **ohne** Tausenderpunkt. Jetzt steht
dort `3.147 Bewertungen bei Amazon`.

**Lehre:** *Ein Gate, das eine Darstellung prüft, muss die Darstellung parsen, nicht ihren
Rohtext.* Beide Blocker kommen aus derselben Abkürzung — `[^<]*` statt Tag-Zählung — und
sie hatte in beide Richtungen Folgen: ein Loch für alles mit Markup drumherum, ein
Fehlalarm für alles mit Markup darin.
