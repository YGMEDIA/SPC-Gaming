# 2026-10-05 · Content · S1 Zitier-Pass, Lauf 2

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
