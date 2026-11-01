# GSC-Lauf 8: der erste Klick, der halbierte Rest, und zum dritten Mal dieselbe dünne Seite

**Datum:** 2026-11-01 · **Loop:** gsc-loop · **Rohdaten:** `03-research/raw/gsc/2026-11-01.md`

## Was

Yasin hat vier GSC-Screenshots geliefert (28-Tage-Fenster 03.10.-30.10., Übersicht · Suchanfragen · Seiten · Länder). Daraus: Rohdaten-Notiz, Interpretation in STATUS, zwei Warteschlangen-Einträge, Checkliste für Lauf 9. Kein Code, keine Seite angefasst — dieser Lauf ist eine Auswertung, und sein Ergebnis ist die **Umkehr der geplanten Reihenfolge**.

Drei Befunde:

1. **1 Klick · 82 Impressionen · Position 52,3 · CTR 1,2 %.** Der erste Klick in einem GSC-Fenster seit Anfang August. Gegen Lauf 7 (184 Impr., Pos. 49,2) sind das 55 % weniger Impressionen bei praktisch gleicher Position.
2. **Der Verlust ist fast vollständig die Startseite.** 93 → 13 Impressionen, also 80 der 102 verlorenen. Gleichzeitig steigen die Unterseiten mit Kaufabsicht. Das ist eine Umverteilung, keine Kollaps-Kurve.
3. **Die stärkste Seite der Site hat 163 Wörter.** `/zubehoer/handy-kuehler/`, 18 Impressionen. Der Hub darüber hat 41.

## Wie

**Vergleichbarkeit zuerst hergestellt.** Die Läufe 4 bis 7 sind in STATUS teils mit 7-Tage-, teils mit 28-Tage-Zahlen notiert. Lauf 8 liefert nur 28 Tage, also wurde ausschließlich gegen die 28-Tage-Spalten von Lauf 6 und 7 gerechnet (197 → 184 → 82, Position 52,1 → 49,2 → 52,3). Die 7-Tage-Reihe (56,4 → 55,9 → 43,5 → 41,8) steht separat und wird nicht mit der 28-Tage-Reihe vermischt.

**Seiten-Deltas einzeln gebildet**, statt den Rückgang als Site-Ereignis zu behandeln. Erst dadurch fiel auf, dass die Startseite praktisch den ganzen Verlust trägt und sechs andere Seiten gleichzeitig gewinnen.

**Technische Ursache ausgeschlossen, bevor inhaltlich interpretiert wurde:** `/controller/mini-gamepad/` (minus ~21 Impr.) ist live, in der Sitemap, ohne noindex. Kein Deindexierungs-Problem.

**Dann die Lektion aus Lauf 7 angewandt und sofort die Geschwister mitgemessen**, statt nur den Treffer zu behandeln. Wortzahlen über alle 127 Seiten nach derselben Vorschrift wie bei Maßnahme 9 (`<script>`/`<style>`/`<nav>`/`<footer>`/`<head>` entfernt, Tags durch Leerzeichen, Tokens gezählt):

| Seite | Wörter | Impr. 28T |
|---|---|---|
| /zubehoer/ (Hub) | 41 | 0 |
| **/zubehoer/handy-kuehler/** | **163** | **18** |
| /zubehoer/finger-sleeves/ | 168 | 0 |
| /zubehoer/trigger/ | 294 | 0 |
| /controller/tablet/ | 131 | 0 |

Zum Vergleich die bereits ausgebauten Hubs: controller/android 1138 · controller/ios 1109 · controller/universal 1002 · marken/razer 1006.

**Gegenprobe gegen einen Fehlalarm:** 41 Wörter könnten heißen, dass der Inhalt per JS kommt — das wäre ein §A2-Bruch und ein ganz anderer Befund. Nachgesehen: `/zubehoer/` enthält statisch vier Karten und 20 Links. Kein §A2-Bruch, die Seite ist schlicht kurz. Ebenso geprüft und als **kein Befund** eingestuft: die 14 `/ratgeber/*` mit 7 Wörtern und `marken/mocute` (11) / `marken/ipega` (14) sind die gewollten Redirect-Stubs.

## Warum so

**Warum Maßnahme 5 nicht gebaut wird, obwohl sie als Nächstes dran war.** „Titles auf Klickrate" setzt voraus, dass die Seite gesehen wird. Position 52,3 ist Ergebnisseite 5 bis 6. Eine Title-Änderung dort erzeugt über Monate kein vom Rauschen unterscheidbares Signal — der einzige Klick dieses Fensters kam von einer Seite mit genau einer Impression. Die Maßnahme ist nicht falsch, sie hat nur keinen Messpunkt. Sie bleibt geparkt, bis eine Seite in den Positionen 5-20 steht.

**Warum stattdessen der Zubehör-Ast.** Das Muster hat zweimal funktioniert: Lauf 6 fand die stärkste Nachfrage auf einem 118-Wörter-Hub, Lauf 7 dasselbe auf vier Marken-Seiten mit 59 bis 138 Wörtern. Beide Male hielt oder wuchs die Nachfrage nach dem Ausbau. Hier liegt derselbe Fall zum dritten Mal vor, diesmal auf der Seite mit den meisten Impressionen der ganzen Site.

**Warum der Impressions-Rückgang nicht als Alarm behandelt wird.** Impressionen auf Position 50 entstehen nur, wenn jemand bis Ergebnisseite 5 blättert. Sie sind das volatilste Signal, das GSC hat, und ihre Zahl sagt wenig über den Zustand der Site. Die Zusammensetzung sagt mehr — und die hat sich zugunsten der Geld-Seiten verschoben.

**Was offen bleibt und nicht wegerklärt wird.** Zwischen Lauf 7 und diesem Fenster liegen 20+ Commits, die fast jede Seite angefasst haben. Ob die Umverteilung von unserer Arbeit kommt oder von Google, entscheiden diese Daten nicht. Das steht so in den Rohdaten und in STATUS, ohne Hypothese, die ich nicht belegen kann.

## Verify

- `python3 scripts/verify.py` grün (reine Brain-Änderung, keine Seite angefasst).
- Jede Zahl in der Rohdaten-Notiz stammt aus einem der vier Screenshots oder ist eine Differenz aus zwei davon. Die Wortzahlen und die Sitemap-/noindex-Prüfung sind am Repo gemessen, die Messvorschrift steht dabei.
- **Rechen-Vorbehalt festgehalten statt geglättet:** Die zehn sichtbaren Seiten-Zeilen summieren auf 81 Impressionen, die Übersicht nennt 82 bei 20 Seiten — das geht nicht auf. Die Länder summieren dagegen exakt (68+7+4+2+1 = 82). Ursache unbekannt, vermutlich Anonymisierung oder unterschiedliche Datenschnitte. Steht als Vorbehalt in der Notiz, weil eine erfundene Erklärung schlimmer wäre als eine offene Lücke.

## Gelernt

**1. Eine Zahl aus der Projekt-Kurzfassung ist keine Messung.** Ich habe am 18.10. geschrieben, Maßnahme 5 ziele auf „deine Positionen um 18". Die 18,3 stammt aus der CLAUDE.md-Kurzfassung vom 18.07., also aus der New-Site-Boost-Phase vor dem Einbruch am 25.07. Die tatsächlichen Positionen seit Lauf 4 liegen zwischen 41,8 und 56,4 — die Rohdaten lagen die ganze Zeit im selben Vault. Der Unterschied ist nicht kosmetisch: Bei Position 18 wäre Maßnahme 5 der richtige nächste Hebel gewesen, bei Position 52 ist sie Arbeit ohne Messpunkt. **Regel: Bevor eine Maßnahme mit einer Kennzahl begründet wird, kommt die Zahl aus dem jüngsten Lauf in `raw/gsc/`, nicht aus einer Zusammenfassung.**

**2. Die Lektion aus Lauf 7 hat diesmal gehalten.** Dort war der Fund auf einer Marken-Seite in Wahrheit ein Fund auf allen vieren. Deshalb hier nicht die eine Seite gemessen, sondern alle 127 — und aus einem Ein-Seiten-Befund wurde ein Ast aus vier Seiten plus einem zweiten Treffer (`/controller/tablet/`). Eine Einzelmessung hätte drei davon übersehen.

**3. Ein Durchschnitt beantwortet die Frage nicht, die er zu beantworten scheint.** Position 52,3 ist der Mittelwert über 41 Queries. Ob darunter eine auf Position 8 steht, entscheidet über den nächsten Bauschritt — und genau diese Spalte fehlt im Paket. Für Lauf 9 steht sie als Punkt 1 der Checkliste, mit der Begründung dabei, damit sie nicht wieder als Formalie durchrutscht.
