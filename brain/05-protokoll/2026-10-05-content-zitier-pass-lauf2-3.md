# 2026-10-05 · Content · S1 Zitier-Pass, Läufe 2 und 3

## Was

Fortsetzung der am 20.07. von Yasin freigegebenen Serie: je Lauf die Sektions-Einstiege
**einer** Seite zu eigenständigen Direktantworten mit belegten Zahlen formen. Reihenfolge
GSC-getrieben.

**Die Seite nach Daten gewählt, nicht nach Gefühl.** Jüngstes Paket im Repo ist Lauf 7
(29.09., Fenster 31.08. bis 27.09.). Seiten nach Impressionen:

| Seite | Impr. 28T | Entscheidung |
|---|---|---|
| / | 93 | Startseite, keine Sektions-Einstiege dieser Art |
| **blog/hall-effect-erklaert** | **28** | **gewählt** |
| controller/mini-gamepad | 23 | Hub, Prosa gehört `gen_hubs.py` — eigener Lauf |
| marken/razer | 11 | Einstiege antworten bereits eigenständig (gemessen) |

Dazu passen die Queries: „hall effect controller", „hall effect joystick", „hall joystick"
bringen zusammen 9 der 31 Impressionen der 7-Tage-Sicht.

`controller-verbindet-nicht` bleibt gesperrt (Titel-Experiment, gsc-loop).

## Der Befund

Alle sechs H2-Einstiege der Seite gemessen. **Fünf antworten bereits eigenständig**
(„Stick-Drift bedeutet, dass …", „Drei Gründe: Kosten, Abstimmung und Lieferketten").

**Einer antwortet gar nicht:** Unter „Welche Smartphone-Controller haben
Hall-Effect-Sticks?" stand **kein einziger Satz**, sondern direkt drei Karten. Die Frage
im H2 ist genau die, die Google uns stellt, und die Antwort war ein Bild aus drei
Kacheln: nicht zitierbar, nicht vorlesbar, für ein Snippet unbrauchbar.

## Wie

Ein Absatz, der die Frage vollständig beantwortet und für sich allein steht:

> **Fünf der 28 Controller in unserem Sortiment führen Hall-Effect-Sticks in den
> technischen Daten:** der GameSir G8 Galileo, der G8 Plus und der X5 Lite, dazu der
> 8BitDo Ultimate 2C und der Scuf Nomad. Der Razer Kishi V3 nutzt TMR, die neuere
> Variante desselben Prinzips. Drei davon stehen hier mit Preis und Einordnung.

Die fünf sind **die mit `Sticks: Hall-Effect` in products.json**, nicht die, die irgendwo
im Text Hall behaupten. Das ist der Unterschied, der zählt: Die 14 unbelegten Spec-Chips
aus B6 (darunter zweimal „Sticks Hall-Effect") stehen auf Seiten, nicht im Datenkern, und
sie gehen in diese Zahl **nicht** ein. Käme der Beleg per Screenshot, stiege die Zahl —
und das Gate unten würde es verlangen.

Die Antwort nennt bewusst alle fünf und sagt dann, dass drei davon unten stehen. Eine
Direktantwort, die nur die drei empfohlenen nennt, wäre eine Auswahl, keine Antwort.

## Verify

- **Neue §A5-Invariante:** Die Form „N der M Controller … Hall-Effect" wird repoweit
  gegen den Datenkern gerechnet (N = Controller mit `Hall` im `Sticks`-Spec, M = alle
  Controller). Dazu die TMR-Aussage: „Der X nutzt TMR" verlangt, dass X **der einzige**
  Controller mit TMR ist.
- **Sechs Defektformen gemessen, 0 falsch:** Hall-Zahl verfälscht · Sortimentszahl
  verfälscht · unbekanntes Zahlwort („Etliche") · ein Hall-Controller verliert seinen
  Sticks-Spec · ein zweiter Controller bekommt TMR · legitimer Zusatz daneben bleibt grün
- **`scripts/links_batterie.py` von 102 auf 106 Fälle**, 0 falsch
- **Vierzehn Gates exit 0**, Lesezeit der Seite bleibt bei 4 Minuten (800 Wörter)
- Die Zählung selbst gegengerechnet: 28 Controller, 6 mit `Sticks`-Spec, davon 5 Hall und
  1 TMR

## Gelernt

1. **Eine Überschrift, die eine Frage stellt, schuldet einen Satz.** Drei Karten sind
   eine Antwort für ein Auge, das schon auf der Seite ist. Für ein Snippet, eine
   Sprachausgabe oder ein Sprachmodell existiert sie nicht. Und es war ausgerechnet die
   Sektion zur stärksten Query der Seite.
2. **Die Zahl in der Direktantwort muss aus dem Datenkern kommen, nicht aus dem Text.**
   Sonst hätte ich hier „acht" geschrieben: So viele Seiten behaupten Hall-Effect, wenn
   man die unbelegten Chips mitzählt. Die Antwort wäre zitierfähig gewesen und falsch.
3. **Vor dem Pass messen, welcher Einstieg ihn braucht.** Fünf von sechs brauchten ihn
   nicht. Dieselbe Lehre wie in Lauf 1, und sie hat wieder gehalten: zwei Seiten der
   Kandidatenliste schieden aus, bevor eine Zeile geschrieben war.

---

# Lauf 3 · controller/mini-gamepad (23 Impr./28T)

## Der Befund

Die stärkste **Query** der Site zeigt hierher: „mini gamepad android" mit 20 von 184
Impressionen in 28 Tagen. Die Seite ist seit dem Ausbau in gsc-Lauf 6 inhaltlich gut
(499 Wörter, FAQ mit vier echten Antworten), und drei der vier FAQ-Antworten sind bereits
eigenständig zitierbar mit Zahlen.

**Der Sektions-Einstieg war es nicht:** „Mini-Gamepads sind die Antwort auf ein
praktisches Problem: Teleskop-Controller spannen das Handy fest ein und sind unterwegs
sperrig." Das ist eine Problembeschreibung, keine Antwort. Wer fragt „mini gamepad
android", bekommt hier zuerst erklärt, was Teleskop-Controller falsch machen.

**Nebenbefund zur Loop-Notiz:** Dort stand „Hubs nur mit gen_hubs-Sync (Generator nicht
idempotent)". Beides trifft auf diese Seite nicht zu: Der Mini-Gamepad-Hub ist
handgepflegt (`gen_hubs.py` kennt ihn nicht, nur `sync_product_values` hält seine Karten
nach), und `gen_hubs.py` ist seit der Idempotenzprobe nachweislich idempotent und
baumstabil. Die Notiz war vom 20.07. und seitdem überholt.

## Wie

Der Einstieg beantwortet jetzt zuerst die Frage und erzählt danach weiter:

> **Zwei Mini-Gamepads führen wir im Sortiment, beide per Bluetooth und beide an Android
> wie am iPhone nutzbar:** den 8BitDo Ultimate Mobile für 45 Euro und den abxylute M4
> Snap-On für 50 Euro. Mini-Gamepads sind die Antwort auf ein praktisches Problem: …

Jede Angabe ist abgeleitet: die Zwei aus `worksOn` (Flag `mini`), „Android wie am iPhone"
ebenfalls aus `worksOn`, die Preise aus products.json. Was **nicht** dasteht, obwohl es
naheläge: „auch an Tablet und PC". Das steht als allgemeine Aussage über Bluetooth weiter
unten im Text, ist aber für diese zwei Modelle in `worksOn` nicht hinterlegt.

## Verify

- **Neue §A5-Invariante:** „N Mini-Gamepads führen wir" wird gegen `worksOn` gerechnet,
  mit Zahlwort-Auflösung wie bei der Hall-Prüfung; ein unbekanntes Zahlwort ist selbst
  ein Befund
- **Fünf Defektformen gemessen, 0 falsch:** Zahl verfälscht · unbekanntes Zahlwort · ein
  Produkt verliert das `mini`-Flag · Preis im Einstieg verfälscht (fängt `audit_prosa`) ·
  legitimer Zusatz bleibt grün
- Vorher geprüft, dass die Prosa-Werte dieser Seite überhaupt gegatet sind: Preis,
  Sternzahl und Bewertungszahl einzeln verfälscht, alle drei machen `audit_prosa.py` und
  `verify.py` rot
- **`scripts/links_batterie.py` von 106 auf 109 Fälle**, 0 falsch
- **Vierzehn Gates exit 0**, Browser: Einstieg fett, kein Horizontal-Scroll

## Gelernt (Lauf 3)

4. **Eine Loop-Notiz altert wie jede andere Aussage über den Stand.** „Generator nicht
   idempotent" stimmte am 20.07. und war seit der Idempotenzprobe widerlegt; die Notiz
   hätte den Lauf fast teurer gemacht, als er war. Vor dem Bauen gilt die Messung, nicht
   die Notiz.
5. **Die stärkste Query der Site zeigte auf einen Einstieg, der mit dem Nachteil der
   Konkurrenzbauform begann.** Inhaltlich richtig, als Antwort unbrauchbar. Die Frage
   zuerst beantworten, dann einordnen.
