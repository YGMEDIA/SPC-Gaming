# 2026-09-30 · Daten · Die Quelle statt der Seite: Generator-Text und Fließtext unter Gate

## Was

Das Renderstellen-Paket hat sechs strukturierte Stellen unter das Gate gebracht. Der
Prüflauf danach war trotzdem ein NEIN, mit drei Blockern derselben Klasse. Der Grund war
kein weiteres Feld, sondern eine falsche Ebene: **Der Prosa-Text der Detailseiten gehört
gar nicht den Seiten, sondern `scripts/gen_content.py`.**

Von dort speist sich EIN Feld (`verdict`) in fünf Renderziele:

| Ziel | wie |
|---|---|
| `meta description` + og + twitter | auf 158 Zeichen gekürzt |
| Product-Schema `description` | ungekürzt |
| sichtbare Einordnungs-Box `vb-text` | ungekürzt |
| Fließtext, Stärken/Schwächen, FAQs | `desc`, `pros`, `cons`, `faqs` |

Meine Meta-Korrektur der Vorrunde hatte nur das HTML gepatcht. Ein `gen_pages.py --regen`
hätte sie restlos zurückgedreht. Der Fix war nicht durable, er sah nur so aus.

## Der Fehler hinter dem Fehler

Ich habe in der Vorrunde Renderstellen gezählt und dabei die Frage nicht gestellt, die
davor kommt: **Wer schreibt diese Stelle?** Sechs Stellen unter Kontrolle zu bringen und
die gemeinsame Quelle zu übersehen, verschiebt das Problem eine Ebene tiefer, statt es zu
lösen. Das Audit meldete grün, weil es die strukturierten Felder prüfte, die der Generator
korrekt aus products.json zieht, und blind war für den Text daneben, den er aus einem
zweiten, veralteten Datensatz zieht.

## Vorgehen

**1. `gen_content.py` korrigiert statt der 29 HTML-Dateien.** Alle veralteten Preise und
Bewertungen ersetzt, dazu vier gekippte Urteile neu geschrieben:

| Stelle | vorher | Problem |
|---|---|---|
| `razer-kishi-ultra` cons | "119 € trotz 4,0 Sternen, der günstigere Kishi V3 (88 €)" | Der Ultra kostet 63 €. Er IST der günstigere. |
| `razer-phone-cooler` cons | "Mit ca. 40 € gleichauf mit dem Black Shark" | 70 gegen 32 Euro, mehr als das Doppelte. |
| `marsgaming-mgpxpro` | "3,6 Sterne bei erst 9 Bewertungen. Keine Kaufempfehlung." | Steht bei 4,3 aus 16. Warnung in die Gegenrichtung veraltet. |
| `scuf-nomad` cons | "Für 17 € mehr bietet der G8 Plus (90 €)" | 40 gegen 76 Euro, also 36 € mehr. |

**2. Regen abgesichert statt blind ausgeführt.** Vorher Snapshot aller 39 Seiten, nachher
zeichenweiser Vergleich. Der Regen hätte zwei handgepflegte Inhalte vernichtet: den
§A6-Warnkasten auf `ozkak-6finger` und einen zusätzlichen CTA-Button auf
`razer-kishi-ultra`. Beide sind jetzt im Generator (`cta_link`, generierter Warnkasten),
statt in der Datei zu stehen, wo der nächste Regen sie wieder holt.

**3. §A6 aus den Daten statt aus dem Text.** Der Warnkasten wird aus der Bewertung
gerechnet. Das schließt vier fehlende Warnungen (`rxkfigx-sleeves`,
`ozkak-trigger-gamepad`, `razer-phone-cooler`, `magnet-peltier-cooler`) und entfernt eine
hinfällige. Steigt eine Bewertung über 3,8, verschwindet der Kasten von selbst; fällt eine
darunter, erscheint er.

**4. 51 Fließtext-Stellen in 21 Dateien korrigiert.** Darunter wieder Urteile, nicht nur
Zahlen: `marken/razer` schrieb, der Black Shark koste "dasselbe" wie der Razer-Kühler
(32 gegen 70 Euro); `marken/razer` nannte den Kishi V3 "den Einstieg", obwohl der Ultra
seit dem Abgleich 25 Euro darunter liegt; `blog/guenstige-handy-controller` riet vom
MGPXPRO ab, der inzwischen die beste Mars-Gaming-Bewertung trägt.

## Neue Gates

| Gate | prüft | bewiesen |
|---|---|---|
| **verify 6c Generator-Abgleich** | Datei == `build()` für alle 29 generierten Seiten | rot bei Handkorrektur in der Datei UND bei veraltetem Wert in `gen_content.py` |
| **verify 6c §A6-Schwelle** | unter 3,8 gibt es eine Warnung, ab 3,8 keine Nicht-Empfehlung | rot in beide Richtungen |
| **`scripts/audit_prosa.py`** | Preise und Bewertungen im Fließtext | 10 von 10 echten Altwerten erkannt |
| **verify 6b2 Karten-Kurzwertung** | `div.pro` / `div.con` innerhalb der `pcard` | rot |
| **verify 6b2 Marken-Ø** | gewichteter Schnitt und Bewertungssumme je Marke | rot |
| **verify 6a2 Tag-Bilanz** | offene `<div>` je Seite | rot |

Der Generator-Abgleich ist das stärkste davon: Er ersetzt jede denkbare Regex-Prüfung auf
diesen Text durch einen Zeichenvergleich. Fünf Renderziele sind damit mit einer einzigen
Invariante abgedeckt, und zwar dauerhaft.

## Wo der Prüfer falsch lag

Er meldete "16 von 16 Ø-Zellen falsch" in der Marken-Tabelle und lieferte Sollwerte mit.
Die Tabelle führt laut eigener Fußnote den **gewichteten** Schnitt, er hat den einfachen
gerechnet. Nachgerechnet stimmen alle 16 Zellen. Hätte ich die Befundliste abgearbeitet,
statt sie zu prüfen, hätte ich 16 korrekte Werte durch falsche ersetzt.

Ebenso unbegründet war "10 verwaiste Detailseiten, eigene Preiszeile und CTA ungeprüft":
Die zehn Seiten haben weder Preiszeile noch CTA noch Product-Schema. **Aber** der Hinweis
hat trotzdem etwas gefunden: Mein Prosa-Audit übersprang pauschal den Ordner `produkte/`
und hätte die zehn Seiten durch beide Gates fallen lassen. Nach der Umstellung auf "nur
überspringen, was der Generator besitzt" fand es dort sofort zwei falsche Preise.

## Nebenbefund

Zwei Hub-Seiten (`controller/universal/`, `controller/android/`) schlossen ihren
container-`<div>` nie. Der Browser holt das am `</section>` selbst nach, deshalb sah die
Seite richtig aus und keine Prüfung sprach an. Repariert, im Browser gegengeprüft (26
Karten, SEO-Block als Geschwister-Element, keine Konsolenfehler), Gate ergänzt.

## Verify

- `python3 scripts/verify.py` grün: 125 Seiten, 247 JSON-LD-Blöcke, 42 Produkte
- `sync_product_values.py --audit`: 0 harte Abweichungen, Sync idempotent (0 Änderungen)
- `audit_prosa.py`: 0 Abweichungen, an 10 echten Altwerten rot bewiesen
- §A6: 5 generierte Warnkästen, Schwelle in beide Richtungen rot bewiesen
- Tag-Bilanz: 0 Seiten mit offenem `<div>` (vorher 2)
- Regen-Gegenprobe: kein Zeichen redaktioneller Text verloren
- Browser-Prüfung der zwei reparierten Hubs und einer Warnkasten-Seite

## Gelernt

1. **Vor "welche Renderstellen gibt es?" kommt "wer schreibt sie?".** Sechs Stellen zu
   sichern und die gemeinsame Quelle zu übersehen, verlegt den Fehler nur. Wo ein
   Generator die Quelle ist, gehört das Gate an den Generator, nicht an die Seite.

2. **Ein Fix an generiertem Output ist kein Fix.** Meine Meta-Korrektur hätte der nächste
   Regen gelöscht, und nichts hätte es gemeldet. Deshalb prüft verify jetzt Datei gegen
   Generator: Das fängt beide Richtungen ab.

3. **Eine handgeschriebene Warnung altert in beide Richtungen.** Der MGPXPRO trug "keine
   Kaufempfehlung", als er längst bei 4,3 stand. Was sich aus Daten rechnen lässt, wird
   gerechnet, nicht getextet.

4. **Eine Befundliste ist ein Hinweis, kein Auftrag.** Zwei der Befunde waren falsch, einer
   davon mit fertigen Sollwerten, die 16 korrekte Zellen zerstört hätten. Nachrechnen kostet
   Minuten, Vertrauen kostet Korrektheit. Umgekehrt war ein sachlich falscher Befund der
   Anlass, eine echte Lücke zu finden: Der Hinweis kann daneben liegen und trotzdem auf
   etwas zeigen.

5. **Ein Audit, das einen ganzen Ordner überspringt, hat dort keine Lücke, sondern ein
   Loch.** `produkte/` pauschal auszunehmen war bequem und falsch. Ausgenommen wird, was
   nachweislich woanders geprüft wird, und zwar Datei für Datei.

---

## Nachtrag: zweite Prüfrunde (derselbe Tag)

Der Prüflauf zu diesem Paket blockierte erneut, mit acht belegbar falschen Werten. Der
entscheidende Befund war kein Wert, sondern eine Lücke in meiner eigenen Argumentation:

> **`verify.py` 6c beweist `Datei == Generator`, niemals `Generator == products.json`.**

Der Prüfer hat das belegt, indem er einen veralteten Preis in `gen_content.py` einsetzte,
regenerierte und alle drei Gates grün bleiben sah. Genau die Fehlerklasse dieser Runde,
eine Ebene tiefer. Geschlossen, indem `audit_prosa.py` jetzt auch die generierten Seiten
liest: Damit hängt die Kette durchgehend, products.json → Generator → Datei.

**Eine zweite Generator-Quelle gefunden.** `assets/data/longtail.json` speist über
`gen_longtail.py` die zehn verwaisten Datenblätter und trug noch "Ultimate 2C Wireless"
und "rund 20 Euro". Die HTML war von Hand nachgezogen, die Quelle nicht: Ein Generatorlauf
hätte beides wieder live geschrieben. Dieselbe Falle wie bei `gen_content.py`, zwei
Stunden später, in derselben Session.

**Acht Blocker behoben**, darunter drei in `llms.txt` (die GEO-Datei für KI-Crawler, von
keinem Gate gelesen) und ein kompletter Vor-Abgleich-Absatz auf
`vergleich/g8-plus-vs-kishi-v3-pro`, der 4,4 Sterne, 125 Bewertungen, 149 € und 59 €
Aufpreis nannte, während dieselbe Seite an vier anderen Stellen die richtigen Werte trug.

**Vier weitere Fehler, die der Prüfer nicht gefunden hat**, kamen beim Nachbauen der
Gates heraus: `blog/guenstige-handy-controller` nannte den 2C ein "Bluetooth-Gamepad,
läuft auch an Switch" (er ist kabelgebunden, und die eigene Review sagt "nicht Switch");
`controller/universal/gamesir-g8-plus-review` behauptete einen Aufpreis gegenüber dem
G8 Galileo, den es nicht mehr gibt (76 gegen 80 €); die FAQ "Reichen 20 Euro für ein
Geschenk?" versprach für genau diesen Betrag einen vollwertigen Controller, den es seit
dem Abgleich nicht mehr gibt; und Titel und Description desselben Budget-Artikels
verkauften "Hall-Effect ab 20 €", während der günstigste Hall-Controller 30 € kostet.

### Warum die Gates fünf von acht zunächst nicht sahen

Jede Lücke hatte eine eigene, banale Ursache. Das ist der eigentliche Ertrag:

| Ursache | Wirkung |
|---|---|
| `\b` hinter `€` | trifft nie, wenn ein Satzzeichen folgt. Ein Backslash schaltete die komplette Preisprüfung der Detailseiten stumm. |
| `[A-ZÄÖÜ]` als Markenwort | matcht "8BitDo" nicht, weil es mit einer Ziffer beginnt. |
| Punkt in der Lücke verboten | "ca. 63 €" wurde nie erreicht. Erlaubt man ihn ohne Bedingung, greift die Prüfung über Satzgrenzen: vier Fehlalarme. Richtig ist: Punkt ja, aber nicht vor Leerraum und Großbuchstabe. |
| Zahlen erst ab drei Stellen | "51 Bewertungen" fiel durch. |
| Sternform nur mit dem Wort "Sterne" | "4,5 von 5" und "4,2/5" fielen durch. |
| URL in der Lücke | jede Markdown-Zeile in llms.txt war unprüfbar. |
| Marken-Ø auf eine Stelle gerundet in die erlaubte Menge gelegt | machte "4,5" zu einem gültigen Sternwert, den kein Produkt trägt. |

### Zwei Wege, einen Wert zu prüfen

Die namensverankerte Prüfung ("X kostet 90 €") ist präzise, aber blind, sobald der Name
fehlt. Auf der eigenen Produktseite steht er fast nie dabei: "Starker Allrounder für 46 €".
Dafür gibt es jetzt die seitenbezogene Prüfung. Ein erster Entwurf verlangte, dass jeder
Wert zu einem Produkt DIESER Seite gehört, und meldete 17 Fehlalarme (Marken-Summen,
Quervergleiche in FAQs). Die weite Fassung fängt dieselbe Fehlerklasse ohne einen
einzigen: **Ein veralteter Wert gehört typischerweise zu gar keinem Produkt.** 125
Bewertungen, 2.835 Bewertungen, 4,5 Sterne, 39 € gibt es im Sortiment schlicht nicht.

### Verify (Stand nach der zweiten Runde)

- 13 von 13 Rot-Tests über `verify.py` erkannt, je einer pro Fehlerklasse, darunter drei
  Varianten der Kernlücke (veralteter Preis, veraltete Sterne, veraltete Anzahl in
  `gen_content.py` plus Regen)
- `audit_prosa.py` prüft jetzt: alle Seiten inklusive der generierten, `llms.txt`,
  `longtail.json`, Sterne auch ohne das Wort "Sterne", Bewertungszahlen (bis dahin
  berechnet, aber nie verglichen), Werte vor dem Namen, Preise auf Detailseiten,
  Werte auf Vergleichsseiten
- 0 Fehlalarme im Gesamtlauf
- Die 54 weichen Hinweise einzeln geprüft: alle Nachbarzahlen, kein echter Fund.
  Die Black-Friday-Tabelle trägt in der Normalpreis-Spalte 7 von 7 korrekte Werte.

### Zusätzlich gelernt

6. **Ein Gate, das eine Ebene beweist, beweist nicht die darunter.** `Datei == Generator`
   klingt wie Vollständigkeit und ist es nicht. Zu jedem Gate gehört der Satz, was es
   NICHT zeigt, und die Frage, wer die Quelle der Quelle prüft.

7. **Ein Generator ist eine Datenquelle und veraltet wie jede andere.** Zwei davon in
   einem Repo, beide mit demselben Muster, beide erst gefunden, nachdem ihr Output
   auffiel. Wer eine Quelle korrigiert, sucht nach der zweiten.

8. **Regex-Lücken sind keine Detailfehler, sie sind stumme Abschaltungen.** Ein `\b` an
   der falschen Stelle sah aus wie Sorgfalt und hat eine ganze Prüfung deaktiviert.
   Deshalb gilt: Jede Prüfung wird an einem echten Altwert rot bewiesen, nicht an einem
   ausgedachten, und zwar pro Fehlerklasse einzeln.

9. **Eine Prüfung, die still überspringt, ist schlimmer als keine.** Die Vergleichsseiten-
   Prüfung fand ihre Produkte über `data-product` — das steht auf Duell-Seiten nur beim
   Sieger. Sie übersprang damit genau die acht Seiten, für die sie gebaut war, und meldete
   grün. Jetzt ist "keine zwei Produkte auflösbar" selbst ein Fehler.

---

## Nachtrag: dritte Prüfrunde

Wieder blockiert, zehn falsche Stellen. Und wieder war der schwerste Befund mein eigener
Fehler aus der Runde davor.

### Ein fehlendes `\b` hat die Preisprüfung stumm abgeschaltet

```python
_SCHWELLE = re.compile(r'(?:ab|unter|über|bis|zwischen|und|…)\s*(?:€\s*)?$')
```

`und` ohne Wortgrenze trifft das Ende von **„r-und"**. Damit galt **jeder** Preis der Form
„rund 40 €" als Schwellenwert und wurde übersprungen: **101 Stellen im Repo**, davon 19 in
`gen_content.py`. Ich hatte diesen Filter in derselben Session eingebaut, um Fehlalarme zu
vermeiden, und dabei die Prüfung auf genau den Seiten deaktiviert, für die sie gebaut war.
Alle 101 Stellen waren zufällig korrekt, es war eine scharfe Ladung ohne Schuss.

### Zwei weitere Datenquellen, die dritte und vierte

| Quelle | Zustand | warum kein Gate sie sah |
|---|---|---|
| `scripts/gen_hubs.py` | „abxylute S8 (ca. 39 €, 4,4 Sterne)" statt 46 € / 4,3 | Produktwerte als Literal im `HUBS`-Dict. Die Datei ist laut eigenem Kommentar NICHT idempotent, ein Regen deckt den Fehler also nie auf. |
| `data-price`-Attribute | 4 von 8 veraltet | Steuert die Sortierung „Preis aufsteigend" auf dem Controller-Hub. Die sichtbaren Preise daneben stimmten alle: ein **funktionaler** Fehler, den keine Textprüfung sehen kann. |

Damit sind es vier Generator- und Datenquellen neben products.json: `gen_content.py`,
`longtail.json`, `gen_hubs.py`, `llms.txt`. Alle vier stehen jetzt im Fließtext-Audit.

### Die Bindung an eine Datei

`verify.py` band jede widerlegte Aussage an **eine** Datei. Genau das hat vier Befunde
überleben lassen: Der Ultimate 2C stand auf **sechs weiteren Seiten** als
Bluetooth-Gamepad fürs iPhone, zwei davon in FAQPage-Schemas — er ist kabelgebunden, und
unsere eigene Review sagt „(nicht Switch)" und „Kein iOS-Support". Dieselbe Bindung hatte
die Hall-Invariante: Sie prüfte eine Seite auf **Anwesenheit** des richtigen Werts, während
„Hall-Effect ab 20 €" auf vier anderen Seiten stand. Beide jetzt repoweit und auf
**Abwesenheit des falschen** Werts. Die umgestellte Hall-Invariante fand sofort zwei
weitere Stellen in `llms.txt`, die keine der drei Prüfrunden gefunden hatte.

### `@graph` war ein blinder Fleck im Schema-Gate

```python
if obj.get('@type') != 'Product':
    continue
```

Ein `@graph`-Block hat oben kein `@type`. Die Prüfung stieg aus, ohne zu rekursieren:
**38 von 42 Product-Schemas wurden geprüft, genau die vier in `@graph` nicht** — und das
sind die vier kommerziell wichtigsten Reviews. `ratingValue`, `reviewCount` und
`offers/price` liefen dort frei manipulierbar durch alle Gates.

### Fehlalarme messen, bevor man schärft

Der Prüfer hat sieben korrekte Formulierungen gefunden, bei denen das Audit rot wurde:
Skalenaussagen („5,0 Sterne"), Anzahl-Schwellen („weniger als 100 Bewertungen"),
Näherungen auf Vergleichsseiten, Marken-Summen, Fremdprodukte, Versandkosten. Alle sieben
entschärft und als Proben festgehalten. **Ein Gate, das bei richtigem Text anschlägt, wird
abgeschaltet** — Fehlalarmfreiheit ist keine Kosmetik, sie ist die Bedingung dafür, dass
ein Gate überlebt.

### Verify (Stand nach der dritten Runde)

- **19 von 19 Rot-Tests** über `verify.py`, je einer pro Fehlerklasse
- **8 von 8 Fehlalarm-Proben** bleiben grün
- falsche Differenzen werden erkannt, richtige nicht gemeldet
- Prozentaussagen bleiben strukturell blind; die einzige im Repo (V3 → V3 Pro, 73 Prozent)
  hat jetzt eine eigene Invariante
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen

### Zusätzlich gelernt

10. **Ein Filter gegen Fehlalarme ist ein Loch mit guter Absicht.** Mein `_SCHWELLE`-Filter
    sollte „unter 50 €" ausnehmen und hat „r-und" mitgenommen. Wer eine Ausnahme einbaut,
    testet sie gegen die Fälle, die sie NICHT treffen soll, und zählt, wie viele Stellen
    sie im Repo stumm schaltet.

11. **Eine widerlegte Aussage ist überall widerlegt.** Die Bindung an die Datei, in der sie
    zuerst auffiel, ist bequem und falsch. Und eine Invariante prüft die Abwesenheit des
    falschen Werts, nicht die Anwesenheit des richtigen an einer Stelle.

12. **Maschinenlesbare Werte driften unsichtbar.** `data-price` steuert eine Sortierung.
    Vier Werte waren falsch, während die sichtbaren Preise daneben alle stimmten. Wo Daten
    doppelt stehen, einmal für Menschen und einmal für Code, gehört die Maschinenfassung
    genauso ins Gate.

---

## Nachtrag: vierte Prüfrunde

Zehn Stellen, eine fünfte Datenquelle, und zwei Gate-Lücken, die ich selbst eingebaut hatte.

### Die Freigabeliste war zu weit, um zu greifen

`pruefe_seitenwerte` prüfte Sternwerte gegen die Menge **aller im Sortiment vorkommenden**
Werte. Das Sortiment kennt 3,3 · 3,5 · 3,6 · 3,7 · 3,8 · 3,9 · 4,0 · 4,1 · 4,2 · 4,3 ·
4,4 · 4,6 — nur 3,4 und 4,5 wären aufgefallen. Ein veralteter Sternwert in
`gen_content.py` stand nach dem Regen **sechsmal** auf der erzeugten Seite, während die
Technik-Tabelle derselben Seite den richtigen Wert zeigte, und alle drei Gates blieben
grün. Die Prüfung ist jetzt seitenbezogen: Auf der eigenen Produktseite gilt nur der Wert
dieses Produkts.

### Ein `<strong>` hat die Preisprüfung ausgehebelt

Die Lückenregel verbot `<` und `>`, weil ein Tag den Bezug brechen sollte. Das tut es
nicht: „Der G8 Galileo kostet `<strong>`92 €`</strong>`" ist ein Satz, und die Fettung ist
die naheliegendste Redaktionsform für einen Preis. Tags werden jetzt positionserhaltend
durch Leerzeichen ersetzt. Dieselbe Änderung schließt vier weitere Klassen auf einen
Schlag: Wert in einer Liste unter der Überschrift, Wert in der Nachbarzelle, `<em>`
zwischen Name und Wert, durchgekoppelter Name.

### Die fünfte Datenquelle

`data-platform` steuert den Live-Filter (iPhone/Android/Universal) auf dem Controller-Hub.
**Fünf von acht Werten** wichen von `worksOn` ab, darunter der kabelgebundene Ultimate 2C
mit `ios` — **genau die Aussage, die eine Runde zuvor per VERBOTEN-Liste aus dem Text
entfernt worden war.** Im Attribut hat sie überlebt und dort funktional gewirkt: Der 2C
erschien im iPhone-Filter. `data-price` hatte in Runde 3 ein Gate bekommen, sein Zwilling
nicht.

### Fünf von acht Vergleichsseiten wurden stumm übersprungen

`vergleich_produkte()` verlangte `<tr><th>`. Zwei Seiten schreiben ihren Kopf mit `<td>`,
drei haben gar keine Vergleichstabelle. Ein vertauschtes Preispaar wäre dort unentdeckt
geblieben. Dieselbe Klasse wie der Kartenscan ab `data-product` und der pauschal
übersprungene Ordner: **eine `continue`-Zeile, die eine Annahme über das Markup trifft.**

### Ein Generator, der eine Fallunterscheidung nicht kennt

`gen_brand_sections.py` verdrahtete das Wort „unter": „Der Einstieg liegt mit 63 Euro aber
**unter** dem günstigsten Razer-Controller, der **63 Euro** kostet." Nach dem Abgleich
kosten beide dasselbe, und die Seite widerlegte sich im selben Satz. Behoben im Generator,
nicht in der Datei: `vergleichswort()` liefert jetzt unter, über oder gleichauf.

### Verify (Stand nach der vierten Runde)

- **13 von 13 Fehlerklassen** rot, je eine pro Quelle: `gen_content.py` (Preis, Sterne,
  Anzahl), `longtail.json`, `llms.txt` (Preis, Anzahl), `gen_hubs.py`, `data-price`,
  `data-platform`, `@graph`-Schema, VERBOTEN repoweit, Hall-Invariante, Prozentaussage
- **17 von 17 Fehlalarm-Proben** grün
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen

### Zusätzlich gelernt

13. **Eine Freigabeliste ist so gut wie ihre Enge.** „Der Wert muss zu irgendeinem Produkt
    gehören" klingt nach einer Prüfung und ist bei zwölf belegten Sternwerten fast keine.
    Der Bezugsrahmen gehört so eng gefasst, wie die Seite ihn hergibt: eigene Produktseite
    → eigenes Produkt, Vergleichsseite → die zwei verglichenen, Blogseite → das
    nächstgenannte.

14. **Eine widerlegte Aussage wandert in die Attribute.** Der 2C als iPhone-Gerät war aus
    jedem Satz entfernt und stand weiter in `data-platform`, wo er den Filter steuerte.
    Wer eine Aussage aus dem Text tilgt, sucht sie in der Maschinenfassung.

15. **Jede Ausnahme in einem Gate braucht eine Gegenprobe, und zwar in beide Richtungen.**
    Die Lücke von 85 auf 130 Zeichen zu weiten, fing einen echten Fehler und erzeugte im
    selben Lauf einen Fehlalarm auf einer Markensumme. Erst die Gegenprobe zeigt, ob eine
    Schärfung netto etwas bringt.

---

## Nachtrag: fünfte Prüfrunde

Drei belegbar falsche Stellen, eine sechste Datenquelle, und eine Ausnahme, die ich selbst
eingebaut hatte und die einen Fehler **vier Prüfrunden lang** gedeckt hat.

### Der Freibrief, der den X2s-Fehler vier Runden versteckt hat

`pruefe_detailpreise` erlaubte jeden Wert, der zu **irgendeinem** Produkt im Sortiment
gehört (`w in ALLE_PREISE`). Auf `controller/universal/gamesir-x2s-review` stand seit dem
21.07. „✓ Günstiger Preis (ca. **46 €**)", während dieselbe Seite an vier anderen Stellen
und im Schema korrekt 53 € zeigt. 46 € ist der Preis der abxylute S8 — deshalb war der
Wert gedeckt. Der Freibrief ist gestrichen; die fünf dadurch entstehenden Fehlalarme sind
weg, seit Geschwisterprodukte derselben Marke zum Seitenkontext zählen.

Direkt daneben, Zeile 80: „✗ Nur mittelmäßige Bewertung (**3,8**)" statt 3,9. Diese Form
war für **jedes** Muster unsichtbar, weil alle das Wort „Stern", „von 5" oder „/5"
verlangten. Ein nackter Wert in Klammern kam in keiner Regel vor.

### Die sechste Quelle ist `worksOn` selbst

Runde 4 hat `data-platform` aus `worksOn` gesetzt und ein Gleichheits-Gate gebaut. Damit
war der Zwilling synchron — und ein falscher Wert sauber ins Attribut **propagiert**.
`worksOn` ist handgepflegt und wurde gegen nichts geprüft:

> `viture-8bitdo`, `worksOn: [android, **ios**, universal]`
> `claim` desselben Eintrags: „Für Android und XR-Brillen gebaut … **Kein iOS, kein Bluetooth.**"

Das Produkt stand als Karte im iPhone-Hub, mit genau diesem Satz sichtbar darauf. Exakt
die Fehlerklasse, die Runde 4 beim Ultimate 2C geschlossen hat, eine Ebene tiefer.
`worksOn` wird jetzt gegen `claim` und `specs.Verb.` geprüft, die Karte ist aus dem
iPhone-Hub entfernt (24 statt 25 Modelle).

### Zwei weitere stille Abschaltungen

- **`fremdbezug` akzeptierte fremde Marken.** „Razer", „GameSir", „Backbone" und „8BitDo"
  stehen auf fast jeder Seite — die Ausnahme war praktisch immer erfüllt und die
  seitenbezogene Prüfung damit faktisch aus. Jetzt nur noch Produktnamen.
- **Der Universal-Hub fehlte in der Hub-Prüfung.** Vier von fünf Hubs wurden gegen
  `worksOn` gehalten, der fünfte gegen nichts. Beim Aufnehmen fiel auf, dass die Prüfung
  zusätzlich einen Typfilter braucht: Zubehör trägt ebenfalls „universal", gehört aber
  nicht auf einen Controller-Hub.

### Was dieses Gate NICHT abdeckt, steht jetzt drin

`verify.py` 6c vergleicht 29 Detailseiten zeichengleich mit dem Generator. **13 weitere
Produkte** haben handgepflegte Review-Seiten unter `/controller/…-review/` und sind davon
nicht erfasst — genau dort saß der X2s-Fehler. Die Zahl wird jetzt geprüft und gemeldet,
sobald sie sich ändert, statt eine Abdeckung zu suggerieren, die für ein Drittel der
Detailseiten nicht existiert.

### Verify (Stand nach der fünften Runde)

- **17 von 17 Fehlerklassen rot**, je eine pro Quelle und Fehlerform
- **22 von 22 korrekte Sätze grün**
- Hinweis zur Messmethodik: Sieben Proben schlugen zunächst an, weil ich sie in eine
  *generierte* Seite geschrieben hatte. Das war kein Fehlalarm, sondern das Drift-Gate,
  das eine Handkorrektur an generiertem Output korrekt meldet. Auf nicht generierten
  Seiten wiederholt: alle grün. **Eine Messung, die das Prüfobjekt verändert, misst das
  falsche.**

### Zusätzlich gelernt

16. **Jede Ausnahme ist ein Verfallsdatum.** `w in ALLE_PREISE` sollte Fehlalarme
    verhindern und hat einen echten Fehler vier Prüfrunden lang gedeckt. Wer eine Ausnahme
    einbaut, schreibt dazu, welchen Fehler sie durchlässt — und prüft, ob dieser Fehler
    im Bestand vorkommt.

17. **Synchronisieren heißt nicht prüfen.** `data-platform` aus `worksOn` zu setzen hat
    zwei Felder in Übereinstimmung gebracht, von denen eines falsch war. Ein Abgleich
    zwischen zwei Kopien ersetzt keine Prüfung gegen eine Quelle.

18. **Ein Gate soll sagen, was es nicht kann.** 6c deckt 29 von 42 Detailseiten. Diese
    Zahl gehört ins Gate selbst, sonst liest sich Grün als Vollständigkeit.

---

## Nachtrag: sechste Prüfrunde

Zwei Blocker, eine siebte Datenquelle, und drei Gate-Stellen, an denen meine Reparaturen
aus Runde 5 nur halb saßen.

### Die siebte Quelle ist JavaScript

`assets/js/*.js`, vier Dateien, 777 Zeilen, **von keinem Gate gelesen**: `verify.py` und
`audit_prosa.py` globben `**/index.html`, `sync_product_values` läuft nur über `*.html`.
Zwei Dinge lagen dort:

- **`main.js:135` behauptete: „Wir empfehlen nur Controller mit 4★+ auf Amazon."** Der
  Footer wird per JS in **109 Seiten** injiziert. 11 von 42 Produkten liegen unter 4,0,
  fünf davon Controller, und alle werden empfohlen. Der Satz widersprach zusätzlich der
  **eigenen** Schwelle: §A6 und `verify.py` arbeiten mit 3,8. Dazu zeichnete der Footer
  4,5 Sterne ohne jede Datengrundlage. Beides ersetzt durch das, was wir tatsächlich tun:
  „Unsere Empfehlungsschwelle liegt bei 3,8 Sternen. Modelle darunter listen wir trotzdem,
  aber mit ausdrücklicher Warnung statt Kaufempfehlung."
- **Der Affiliate-Tag `ygmedia-21` steht nur in `main.js:9`.** Der Prüfer hat ihn gegen
  `fremdtag-21` getauscht: alle Gates grün. Das ist die Geldleitung der gesamten Site.
  Jetzt eine Invariante.

### Mein eigener Fix war unvollständig

Die Entfernung des VITURE aus dem iPhone-Hub hatte ich für erledigt gehalten: Karte,
ItemList-Eintrag, sichtbarer Zähler und Filter-Attribute stimmten, das Wort „viture" kam
nicht mehr vor. **`"numberOfItems": 25` blieb stehen**, während die Liste 24 Einträge hat.
Ein Zähler im Schema, den niemand nachrechnet. Jetzt prüft verify `numberOfItems` gegen
die Listenlänge — bewusst nicht gegen die Kartenzahl, weil mehrere Seiten absichtlich eine
Top-Auswahl im Schema führen und mehr Karten zeigen.

### Drei halbe Reparaturen aus Runde 5

| Was ich behauptet hatte | Was tatsächlich war |
|---|---|
| „`ALLE_PREISE`-Freibrief gestrichen" | Nur in `pruefe_detailpreise`. In `pruefe_vergleiche` lebte er weiter. |
| „Markengeschwister im Seitenkontext" | Gab **368** zusätzliche Werte frei, genutzt von genau einem Satz. Verengt auf Marke + Typ: nachgemessen 62 zusätzliche Preiswerte statt 368. Die im ersten Nachtrag genannten "66" waren eine Schätzung, kein Messwert. |
| „6c deckt 29 von 42, 13 sind handgepflegt" | Zu optimistisch. Dazu kommen 10 Longtail-Seiten ohne products.json-Eintrag, die aus `pruefe_detailpreise` herausfielen, weil die Funktion über products.json iterierte. Ein erfundener Preis dort blieb grün. |

Alle drei behoben. Die Longtail-Seiten laufen jetzt mit, und die Offenlegung nennt beide
ungedeckten Gruppen einzeln.

### Eine bewusst offene Stelle

Die Geschwisterregel erlaubt auf einer Produktseite die Preise der Varianten desselben
Modells. Ein Preis, der zufällig zu einer Schwestervariante passt (45 € statt 40 € beim
ShanWan), fällt damit nicht auf. Das ist der Preis dafür, dass der legitime Satz „die
schwarze und weiße Variante, je ca. 40 €" nicht rot wird. 66 zusätzlich erlaubte Werte
über 42 Produkte, und die Alternative wäre ein Fehlalarm auf korrektem Text.

### Verify (Stand nach der sechsten Runde)

- **21 von 21 Fehlerklassen rot**, jetzt über sieben Quellen: products.json, gen_content.py,
  longtail.json, gen_hubs.py, llms.txt, die `data-*`-Attribute und `assets/js/`
- **25 von 25 korrekte Sätze grün**
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen

### Zusätzlich gelernt

19. **„Erledigt" ist eine Behauptung, die man prüft wie jede andere.** Drei meiner
    Reparaturen aus Runde 5 saßen nur zur Hälfte, und ich hatte sie im Protokoll als
    geschlossen geführt. Was ein Gate schließen soll, wird nach dem Einbau gemessen,
    nicht angenommen: Wie viele Werte gibt eine Ausnahme frei? An wie vielen Stellen
    greift der Fix?

20. **Ein Zähler ist eine Aussage.** `numberOfItems` sah aus wie Metadaten und war eine
    Behauptung über die Seite, die nach meiner eigenen Änderung nicht mehr stimmte.
    Alles, was eine Zahl nennt, gehört nachgerechnet, auch wenn es niemand liest — Google
    liest es.

21. **Code ist Content.** Sieben Runden lang habe ich HTML, JSON und Generatoren geprüft
    und das JavaScript übersehen, das den Footer in 109 Seiten schreibt und den
    Affiliate-Tag hält. Die Frage „wer schreibt diese Stelle?" endet nicht bei den
    Dateien, die nach Inhalt aussehen.

---

## Nachtrag: siebte Prüfrunde

Zwei live falsche Preisaussagen, die Geldleitung an zwei weiteren Stellen ungesichert,
und eine Attribut-Ebene, die sechs Runden lang niemand gelesen hat.

### Die Geldleitung war nur zu einem Drittel gesichert

Runde 6 hatte den Affiliate-Tag geprüft — auf **Anwesenheit** des richtigen Tags in
**einer** Datei. Er steht aber an drei Stellen: `main.js:9`, `gen_pages.py:134` (von dort
in die `offers.url` aller 42 Produktseiten) und einmal direkt in einem Product-Schema.
Zwei davon ließen sich auf einen fremden Tag umbiegen, ohne dass ein Gate ansprang.

Das ist wörtlich die Lehre Nummer 11 aus diesem Protokoll — repoweit prüfen, auf
Abwesenheit des falschen statt Anwesenheit des richtigen — die ich bei der Hall-Invariante
gezogen und beim Affiliate-Tag nicht angewendet habe. Jetzt sucht verify jedes `tag=` in
HTML, Python und JavaScript und meldet alles, was nicht `ygmedia-21` ist.

### Attribute: die achte Ebene

`maskiere_tags()` ersetzt Tags positionserhaltend durch Leerzeichen — **samt
Attributinhalt**. Damit war der Text in `meta description`, `og:description`, `alt` und
`title` für jede Prüfung unsichtbar, auf allen 13 handgepflegten Review-Seiten und allen
Hubs, Blogs und Vergleichsseiten. Der Docstring desselben Skripts nennt Meta-Descriptions
ausdrücklich als Prüfziel.

Attributwerte werden jetzt zusätzlich als eigener Textblock angehängt. Funde daraus tragen
statt einer Zeilennummer die Kennzeichnung „Attributwert", weil die Zeile im angehängten
Block irreführend wäre.

### Zwei Synonyme, zwei stille Abschaltungen

- Die Hall-Invariante kannte „Hall-Effect", „Hall-Sticks" und „Drift-Schutz", nicht
  **„driftfrei"**. Ein Synonym, und „ab 20 € mit driftfreien Sticks" stand live.
- `fremdbezug` übersprang jede Wertstelle, in deren Umgebung irgendein fremder
  Produktname stand: **42 von 286 (14 Prozent)**. Genau die Bauform, die `pros`/`cons`
  benutzen. Jetzt wird nur übersprungen, wenn der Wert dem genannten Fremdprodukt
  **wirklich gehört**.

### Die Geschwisterregel war dreifach falsch beschrieben

Ich hatte sie dokumentiert als „Preise der Varianten desselben Modells", gemessen mit
„66 zusätzlichen Werten". Nachgemessen: Der Filter war `brand == brand and type == type`,
und für GameSir hieß das, dass X2s, G8 Plus, G8 Galileo, X5 Lite und X3 Pro wechselseitig
als Varianten galten — vier Produktlinien, keine Farbvarianten. Damit blieb auf der
53-Euro-Seite der Satz „Mit 80 Euro ist er der teuerste GameSir" grün.

Jetzt gilt die Freigabe nur, wenn der Satz ausdrücklich von einer Variante spricht. Und
Preise ohne Produktnamen in der Nähe gehören dem Produkt der Seite, nicht der Menge aller
dort irgendwo genannten Produkte.

### Unbelegte Zahlen auf der meistbesuchten Seite

Die Startseite warb an vier Stellen mit **„100+ Controller getestet"**, direkt neben
„40+ Modelle im Sortiment". Wir führen 42 Produkte und haben 13 ausführlich getestet. Die
Kategorie-Kacheln nannten „7 / 9 / 6 Modelle getestet" — das passte weder zu den Reviews
(3 / 3 / 7) noch zum Hub-Bestand (24 / 26 / 26). Alles auf gerechnete Werte gesetzt, mit
Invariante.

### Verify (Stand nach der siebten Runde)

- **27 von 27 Fehlerklassen rot**, über sieben Quellen und die Attribut-Ebene
- **26 von 27 korrekte Sätze grün**; der eine Treffer war erneut das Drift-Gate auf einer
  generierten Seite, also ein Messartefakt
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen

### Zusätzlich gelernt

22. **Eine gezogene Lehre wirkt nicht rückwirkend.** „Repoweit, auf Abwesenheit prüfen"
    stand seit Runde 3 in diesem Protokoll und war bei der Hall-Invariante umgesetzt.
    Beim Affiliate-Tag habe ich zwei Runden später wieder auf Anwesenheit in einer Datei
    geprüft. Eine Lehre gehört bei jedem neuen Gate durchgegangen, nicht nur dort, wo sie
    entstanden ist.

23. **Was ein Werkzeug wegwirft, prüft es nie.** `maskiere_tags()` war als Verbesserung
    gebaut und hat dabei eine ganze Ebene entsorgt, die der eigene Docstring als Prüfziel
    nennt. Bei jeder Normalisierung gehört die Frage dazu: Was fällt hier heraus, und
    prüft es jemand anders?

24. **Eine Zahl im Protokoll ist eine Behauptung.** Ich hatte „66 zusätzliche Werte"
    geschrieben, ohne zu messen; nachgerechnet sind es 62, und die Beschreibung der Regel
    war ebenfalls falsch. Der Prüfer hat meine eigene Lehre 19 auf meine eigene Zahl
    angewendet. Wer eine Messung nennt, hat sie gemacht.

---

## Nachtrag: achte Prüfrunde

Zwei Blocker, ein unbelegter Mess-Claim und ein Einrückungsfehler in meinem eigenen Gate.

### Ein Gate, das genau dann ausfällt, wenn die bewachte Datei verschwindet

Die §A6-Schwellenprüfung aus Runde 6 stand versehentlich **innerhalb** der Tag-Schleife.
Folge: Ein einziger echter Fehler erzeugte **141 identische Meldungen**, eine pro geprüfter
Datei. Und fehlte `main.js`, lief verify in einen `NameError` und starb mit Traceback,
statt zu melden, dass die Schwelle fehlt — das Gate hätte genau dann geschwiegen, wenn die
Datei weg ist, die es bewacht.

### Lehre 11, zum dritten Mal nicht angewendet

`llms.txt:10` nannte **„28 Controller für iPhone"**. Es sind 24, und das sagen fünf andere
Stellen im eigenen Repo: products.json, der Hub, sein ItemList-Zähler, sein sichtbarer
Zähler und die Startseiten-Kachel. Die Bestandszahl-Invariante aus Runde 7 war auf
`index.html` und `main.js` festgenagelt — dieselbe Bindung an eine Datei, die vorher schon
die Hall-Aussagen und den Affiliate-Tag durchgelassen hat. Jetzt repoweit.

Der Affiliate-Check hatte dieselbe Grenze anders herum: `**/*.html`, `scripts/*.py`,
`assets/js/*.js`, `llms.txt`. Ein fremder Tag in `products.json`, `sitemap.xml` oder
`style.css` blieb grün. Jetzt alle Textdateien.

### Eine Invariante ist so gut wie ihre Wortliste

Die Hall-Invariante kannte drei Schreibweisen. Im Bestand stehen dreizehn:
`Hall-Effect` (435×), `Driftfreie` (48×, großgeschrieben, die Regex war case-sensitiv),
`Hall-Effekt` mit k (19×), `Hall-Sensorik` (17×), `Hall-Sensor/-en` (14×),
`Drift-Schutz` (5×). Dazu prüfte sie nur Beträge, die Vielfache von fünf sind — „ab 22
Euro" wäre durchgelaufen. Die Schreibweisen habe ich jetzt per grep aus dem Bestand
gesammelt, statt sie zu erfinden.

### Der unbelegte Mess-Claim

Runde 7 hat „100+ Controller getestet" korrigiert und zwei Sätze danebenstehen lassen:
**„Echte Messwerte — Latenz & Input-Lag getestet"** und **„wir messen die Latenz für jeden
Controller."** Im ganzen Repo stehen vier Millisekunden-Werte, alle als allgemeine
Technik-Erklärung im Blog, keiner auf einer Produktseite. Für eine deutsche
Affiliate-Seite ist das die heikelste Stelle des Berichts. Ersetzt durch das, was wir
belegen: Amazon-Daten mit Beleg, und die Verbindungsart steht bei jedem Produkt.

Dazu: „Alle 13 getesteten Controller ansehen" verlinkte auf eine Seite mit 10 Karten, die
sich selbst „Top 10" nennt, und zwei Kacheln standen nebeneinander mit „13 ausführliche
Tests" und „13 ausführliche Reviews" — Rest meiner eigenen Runde-7-Bearbeitung.

### Drei Generatoren las kein Gate

`TEXTQUELLEN` kannte `gen_content.py` und `gen_hubs.py`. `gen_longtail.py`,
`gen_brand_sections.py` und `gen_pages.py` nicht. Der schwerste Fall war `gen_longtail.py`:
Sein Lauf stand auf Modulebene **ohne `__main__`-Guard**, ein Import schrieb also Dateien.
Deshalb konnte es für die zehn Longtail-Datenblätter kein `Datei == Generator` geben.
`gen_pages.py` begründet seinen Guard ausdrücklich im Kommentar — die Lehre war nicht auf
das Schwestermodul übertragen. Jetzt hat `gen_longtail.py` denselben Guard und dieselbe
`generierte_seiten()`, und die zehn Seiten stehen unter dem Zeichenvergleich.

### Attributprüfung: eine von vier

Runde 7 hatte `attribut_text()` gebaut und nur in `pruefe()` eingehängt. Die drei anderen
Prüffunktionen strippen Tags und sahen Attributinhalte weiter nie. Dazu verwarf die
Funktion Werte unter acht Zeichen (`alt="92 €"` hat fünf) und las nur doppelt gequotete
Attribute. Alles behoben.

### Verify (Stand nach der achten Runde)

- **32 von 32 Fehlerklassen rot**, über acht Quellen und die Attribut-Ebene
- **30 von 30 korrekte Sätze grün**
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen

### Zusätzlich gelernt

25. **Ein Gate mit Einrückungsfehler meldet laut und schützt nicht.** 141 Meldungen für
    einen Fehler sahen nach Gründlichkeit aus; dahinter stand eine Schleife, die eine
    dateiunabhängige Prüfung 141 Mal ausführte und bei fehlender Datei abstürzte. Nach dem
    Einbau gehört ein Blick darauf, wie oft eine Meldung erscheint und was passiert, wenn
    die geprüfte Datei fehlt.

26. **Eine Invariante an Begriffen ist so gut wie ihre Wortliste, und die gehört gegrept.**
    Drei Schreibweisen gegen dreizehn im Bestand. Wer eine Begriffsliste aus dem Kopf
    schreibt, deckt die Fälle ab, an die er denkt, nicht die, die im Repo stehen.

27. **Eine korrigierte Zahl macht den Satz daneben nicht wahr.** „100+ Controller
    getestet" war der Anlass, „wir messen die Latenz für jeden Controller" stand zwei
    Zeilen weiter und blieb stehen. Wer eine unbelegte Behauptung findet, liest den
    Absatz zu Ende.

---

## Nachtrag: neunte Prüfrunde

Die Runde hat eine Ebene geöffnet, die acht Runden lang niemand betrachtet hat: nicht die
Produktwerte, sondern **die Aussagen darüber, wie und wann sie entstehen**.

### Prozess-, Methodik- und Datumsaussagen

Acht Runden haben Preise, Sterne und Bewertungszahlen geprüft. Kein Gate las je einen Satz
darüber, wie diese Zahlen zustande kommen. Dort lagen jetzt die schwersten Befunde:

| Aussage | Wirklichkeit |
|---|---|
| „Preise wöchentlich geprüft" (Startseite) | letzte Pflege 21.07., nächste 30.09. — zehn Wochen |
| „Preise & Specs laufend geprüft" (Footer, 109 Seiten) | dieselbe Lücke |
| „Stand Juli 2026" auf 19 Seiten | in neun Fällen mit Preisen, die erst am 30.09. entstanden |
| fünf verschiedene Datenstände gleichzeitig live | Juni, Juli, August, September, 30.09. |
| „Über 100 Geräte getestet" (Bestenliste) | 42 Produkte, 13 ausführliche Tests |
| „42 getesteten Produkten" (3 Stellen) | dieselbe Verwechslung von Sortiment und Test |

Der Datenstand hat jetzt **eine** Quelle in `verify.py` und eine Invariante, die alle 27
Stellen dagegen hält. Frequenz-Zusagen („wöchentlich", „täglich", „laufend geprüft")
lassen das Gate rot werden, solange der Verlauf sie nicht hergibt.

### Der zweite Einrückungsfehler, spiegelbildlich

Runde 8 hat einen Block ausgerückt, der in einer Schleife stand. Diese Runde fand den
umgekehrten Fall: Die Hall-Schleife lief **außerhalb** ihres `if _hall:`-Guards, während
ihr Muster darin definiert wird. Mit umbenanntem `Sticks`-Spec starb verify mit
`NameError`, und **alles danach lief nie**. Zwei Einrückungsfehler in zwei Runden, beide
in Blöcken, die ich selbst eingefügt habe.

### Die Wortliste, zum zweiten Mal unvollständig

Runde 8 hatte die Hall-Schreibweisen „per grep aus dem Bestand gesammelt". Gegrept hatte
ich nach `Hall-Effect`, `Hall-Effekt`, `Hall-Sensor`, `driftfrei`, `Drift-Schutz` —
**`Hall-Sticks` mit 98 Vorkommen war nicht dabei**, ebensowenig `Hall-Trigger` (10×),
`Hall-Technik` (4×) und `Drift-frei`. Diesmal habe ich das Muster offen gegrept
(`Hall[- ]?\w+|[Dd]rift[- ]?\w+`) statt gegen eine Liste, die ich schon im Kopf hatte.

### Zwei Produkte unter einem Namen, sieben Monate später

Runde 4 hatte `ozkak-trigger-l1r1` und `toaluea-trigger-joystick` in products.json
auseinandergehalten. Die **vorgerenderten** Seiten trugen weiter den alten, identischen
Namen: acht Stellen in drei Dateien, darunter ein ItemList-Schema. Auf `/produkte/`
hydratisiert JS die Namen, ohne JS bleibt der alte stehen — ein §A2-Widerspruch zwischen
der statischen und der hydratisierten Fassung. Beim Korrigieren fiel auf, dass eine
Zuordnung über den umgebenden Text falsch griff: In einem JSON-Block stehen beide Slugs
nebeneinander. Die Zuordnung läuft jetzt über die URL **desselben** ListItem-Objekts.

### Was ich nicht entscheiden kann

`/redaktion/` und `/ueber-uns/` beschreiben ein Testverfahren: „Jeder Controller wird über
mindestens 2 bis 3 Wochen im echten Gaming-Alltag getestet", „Wir messen Input-Latenz,
Stick-Präzision und Hüllen-Kompatibilität mit echten Geräten (iPhone 15 Pro, Samsung
Galaxy S25)", „Die meisten Produkte kaufen wir selbst."

Ob das stattfindet, weiß nur Yasin. Ich habe die Seiten **nicht** angefasst: Sie
beschreiben sein Arbeitsverfahren, und eine Löschung wäre genauso falsch wie eine
unbelegte Behauptung, falls die Tests stattfinden. Der Punkt steht in STATUS unter
„Braucht Yasin". Zu beachten: Runde 8 hat den schwächeren Satz auf der Startseite
entschärft, die Methodikseiten tragen die stärkere Fassung weiter. Bestätigt Yasin das
Verfahren, kann die Startseite zurück.

### Verify (Stand nach der neunten Runde)

- Alle neuen Gates rot bewiesen: Datenstand, Frequenz-Zusage, Hall-Sticks, ItemList-Zähler,
  Bestandszahl repoweit, Generator-Literal
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen

### Zusätzlich gelernt

28. **Die Aussagen über die Daten sind selbst Daten.** Acht Runden Wertprüfung, und
    daneben stand „Preise wöchentlich geprüft" bei zehn Wochen Abstand und fünf
    verschiedene Datenstände gleichzeitig. Was eine Zahl über den Prozess behauptet,
    gehört genauso ins Gate wie die Zahl selbst.

29. **Ein Datum ist eine Zahl mit einer Quelle.** 27 Stellen, fünf Werte. Jetzt eine
    Konstante und eine Invariante: Beim nächsten Preis-Sync ändert sich eine Zeile.

30. **„Per grep gesammelt" ist erst wahr, wenn das Muster offen war.** Ich hatte nach den
    Begriffen gegrept, die ich schon kannte, und das Ergebnis als Vollständigkeit notiert.
    `Hall-Sticks` mit 98 Vorkommen war nicht dabei. Ein Suchmuster, das die Antwort
    vorwegnimmt, bestätigt nur die eigene Liste.

---

## Nachtrag: zehnte Prüfrunde

Die schwersten Befunde dieser Runde stehen nicht im Text, sondern **im Bild** und **im
Footer** — und sie wirken nach außen, gegenüber Amazon und gegenüber ASUS.

### Das Testsieger-Bild zeigte das Konkurrenzprodukt

`assets/img/products-real/gamesir-g8.jpg` und `gamesir-g8-2.jpg` sind ASUS-ROG-Werbebilder:
ROG-Logo auf dem Display, Slogan „FOR THOSE WHO DARE", ROG-Mauspad, ROG-Tastatur,
Studio-Gel-Licht. Ich habe die Dateien selbst angesehen. Sie liefen an drei Stellen als
GameSir G8 Galileo, darunter als **Hero-Bild des Testsieger-Reviews** und auf der
Startseite unter der Bildunterschrift „Testsieger · GameSir G8 Galileo".

Darüber stand die Sektionsüberschrift: **„Echte Fotos statt Pressebilder — so testen
wir."** Alle drei dort gezeigten Bilder waren Hersteller-Werbematerial, eine Lizenz ist
nirgends dokumentiert. §C3 verbietet Pressebilder ausdrücklich.

Behoben: Alle sechs Verweise auf lokale Pressebilder zeigen jetzt auf die
Amazon-Produktbilder, die die Site ohnehin durchgängig nutzt. Die Claims „Echte Fotos
statt Pressebilder" und „Echte Fotos, echte Schwächen" sind ersetzt durch das, was
zutrifft.

### Zwei Footer-Claims auf 109 Seiten

- **„Bestpreis-Links / Direkt zum günstigsten Händler"** — es gibt genau einen Händler.
- **„Offizieller Amazon-Partner"** — die PartnerNet-Teilnahmebedingungen untersagen diese
  Bezeichnung. Jetzt „Teilnehmer am Amazon-PartnerNet".

### Pflichtangaben existierten ohne JavaScript nicht

Alle 109 Seiten trugen `<footer class="site-footer" id="site-footer"></footer>` — **leer**.
Affiliate-Hinweis, Impressum und Datenschutz wurden ausschließlich von `main.js`
injiziert. Statisch fand sich ein Impressum-Link auf **vier** Seiten, ein
Datenschutz-Link auf **einer**. Das kollidiert mit §A2 („Jede Seite zeigt ihren vollen
Inhalt ohne JavaScript") und §C2 (Kennzeichnung sitewide), und der No-JS-Check prüfte
bisher nur Produktkartenzahlen auf vier Hub-Seiten.

Jetzt steht der Pflicht-Footer statisch in allen 109 Seiten und in beiden Generatoren; JS
ersetzt ihn wie bisher. Ein Gate prüft alle drei Angaben pro Seite.

### Ein Fund aus der eigenen Browser-Prüfung

Beim Gegenprüfen im Browser zeigte der Header weiter die alten Werte, obwohl der Server
die neue Datei auslieferte: `main.js` wurde **ohne Versionsparameter** eingebunden. Für
wiederkehrende Besucher hätte das bedeutet, die korrigierten Footer-Claims und den
Affiliate-Hinweis erst nach Cache-Ablauf zu sehen. Bei rechtlich relevanten Texten ist das
nicht hinnehmbar. Der Parameter ist jetzt der Inhalts-Hash, `scripts/bump_asset_version.py`
zieht ihn nach, und verify prüft ihn.

### Menschen- und maschinenlesbares Datum

Runde 9 hatte die sichtbaren Datenstände vereinheitlicht. Die maschinenlesbaren Zwillinge
blieben stehen: **18 Blogseiten** mit `dateModified` auf Juli/August und **88 von 108**
Sitemap-Einträgen mit veraltetem `lastmod` — auf genau den Seiten, deren Inhalt in diesem
Stand geändert wurde. Google liest diese Felder. Beide nachgezogen, beide mit Invariante.

### Weitere Korrekturen

„laufend gepflegt" (5 Stellen) war dieselbe Frequenz-Zusage wie das in Runde 9 entfernte
„laufend geprüft" — das Muster ist jetzt offen gefasst statt aufgezählt. Die
Tablet-Schwelle „driftfreie Sticks ab 45 €" widersprach `worksOn` doppelt. „Backbone
Backbone Pro" stand auf acht Seiten im sichtbaren Text, Ursache war die bedingungslose
Verkettung `brand + name` in zwei Generatoren. Und „Testsieger" bezeichnete drei
verschiedene Produkte: auf Duell-Seiten heißt der Gewinner jetzt „Sieger dieses
Vergleichs".

### Verify (Stand nach der zehnten Runde)

- 7 von 7 neuen Gates rot bewiesen
- `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0 harte Abweichungen
- Browser-Gegenprobe: Footer korrekt, Header korrekt, alle Amazon-Bilder laden, keine
  Konsolenfehler

### Zusätzlich gelernt

31. **Ein Bild ist eine Behauptung, und kein Skript kann sie lesen.** Ein `alt`-Attribut
    und eine Bildunterschrift sagen, was zu sehen ist. Neun Runden Textprüfung haben
    nicht bemerkt, dass unser Testsieger-Foto ein Konkurrenzprodukt zeigt. Bilder prüft
    man, indem man sie ansieht — das gehört in jede Runde, in der Bilder dazukommen.

32. **Die gefährlichsten Aussagen stehen dort, wo sie niemand für Inhalt hält.** Footer,
    Badge, Bildunterschrift, `numberOfItems`, `lastmod`. „Offizieller Amazon-Partner"
    stand in einer JavaScript-Zeile und auf 109 Seiten.

33. **Pflichtangaben gehören ins HTML, nicht in ein Skript.** Impressum und Datenschutz
    per JS zu injizieren heißt: Ohne JS existieren sie nicht. Das ist kein Stilfehler,
    das ist eine fehlende Pflichtangabe.

34. **Eine Korrektur wirkt erst, wenn sie ankommt.** Eine geänderte Datei ohne
    Versionsparameter erreicht wiederkehrende Besucher nicht. Bei rechtlich relevanten
    Texten gehört das Cache-Verhalten zur Korrektur dazu.

---

## Nachtrag: elfte Prüfrunde (Bildebene) und zwölfte Bauwelle

### Was die elfte Runde fand

Sechs Blocker, vier davon auf der Bildebene. Die drei, die erst durch Ansehen des Bildes
auffielen:

1. **`81G-d2mMISL` ist ein Razer-Werbebanner.** 1500x1500, zeigt eine Person auf einem
   Sofa mit der eingebrannten Werbezeile „CONTROLLER IM FULLSIZE-FORMAT". Lief auf
   `index.html` unter dem Alt „Razer Kishi V3 TMR-Thumbsticks im Detail" mit dem Label
   „Stick-Check" und als Hero der Review mit „mit Full-Size-TMR-Thumbsticks". Dasselbe
   Bild trug in der Galerie derselben Seite einen zutreffenden Alt — der Beweis, dass die
   beiden anderen falsch waren.
   Beim Suchen des Ersatzes stellte sich heraus: `61qFvyXZH+L`, das zweite Galeriebild,
   ist **ebenfalls** ein Werbebanner („FULLSIZE-TMR-ANALOGSTICKS / Modernste Präzision").
   Die Kishi-V3-Galerie besteht überwiegend aus A+-Marketingbannern. Nur das Hauptbild
   `618HoYQQUrL` ist ein echtes Produktfoto — was kein Zufall ist: Amazon verlangt für
   das Hauptbild weißen Hintergrund ohne Text. Genutzt wird jetzt dieses.
2. **Tessen-Hero:** Alt „in den Händen beim Spielen" an einem freigestellten Produktfoto
   auf Weiß, ohne Hände und ohne Handy.
3. **`usb-c-vs-bluetooth.jpg`:** Der Alt behauptete zwei Geräte („USB-C-Controller am
   Handy angeschlossen vs. kabelloser Bluetooth-Controller"), das Bild zeigt genau ein
   Gespann auf einem Schreibtisch.

Dazu zwei Textbefunde:

4. **„Bessere Sticks" widerspricht drei eigenen Quellen.** Die Vergleichstabelle auf
   derselben Seite führt beide Sticks als „magnetisch, driftfrei". Der eigene Artikel
   `blog/hall-effect-vs-tmr/` sagt wörtlich „Auf dem Datenblatt gewinnt TMR" — also das
   Gegenteil. Die Aussage stand an fünf Stellen, zwei davon in einem FAQPage-Schema.
5. **„wer gewinnt den direkten Duell?"** Duell ist sächlich. Stand in Lead und
   twitter:description.

### Was daraufhin gebaut wurde

**Bildmaß-Gate** (`scripts/mess_bilder.py`, `assets/data/bildmasse.json`, verify 6b4).
Beim Ersetzen der Bilder fiel auf: an allen vier Amazon-Bildern mit Maßangabe standen noch
die Maße der früher dort liegenden lokalen Pressebilder. `1920x700` an einem 1500x1500
großen Banner, `1366x910` an einem quadratischen Produktfoto. Getippte Maße veralten
still, wenn die Bildquelle wechselt, und kosten sichtbaren Layout-Sprung.
Das Gate prüft das **Verhältnis**, nicht die absolute Größe: `/assets/img/autor-yg.svg`
liegt in 112x112 vor und steht bewusst mit 56x56 im Markup. Die erste Fassung des Gates
meldete genau das als Fehler — 14 Treffer, alle korrekt im Markup. Regel nachgeschärft
statt Ausnahme eingebaut.

**Statische Hauptnavigation** (`scripts/sync_header.py`, verify §A2).
`<header id="site-header">` war auf allen 109 Seiten leer, gefüllt erst von main.js. Ohne
JavaScript hatte damit keine Seite eine Navigation: die zehn wichtigsten internen Links
der Domain existierten für jeden nicht-JS-Crawler nicht. Gleiche Bauart wie die
Footer-Lücke aus Runde 10, eine Ebene höher und mit mehr SEO-Gewicht.
Einzige Quelle bleibt das `nav`-Array in main.js; das Script liest es aus und leitet das
Markup ab. Zwei Pflegeorte wären genau der Fehler, gegen den diese ganze Session läuft.

**Cache-Busting für alle Assets.** Bisher nur main.js. style.css entscheidet, ob die
Pflichtangaben lesbar sind; finder.js, hub-render.js und produkte.js rendern Preise. Die
Regel war richtig, ihr Geltungsbereich zu eng — dieselbe Bauart wie ein halbes Dutzend
Befunde davor.

**Nebenwirkung, die auffiel:** Seit der Trust-Strip statisch ausgeliefert wird, steht
„Datenstand September 2026" auf jeder Seite. Das Sitemap-`lastmod`-Gate las das als
Seitenaussage und meldete 16 Fehler. Header und Footer werden dort jetzt vor der Prüfung
entfernt: eine Aussage, die auf allen 109 Seiten identisch steht, trägt keine Information
über die einzelne Seite — das Gate hätte für alle oder für keine gefeuert und damit nichts
mehr geprüft.

### Verify (Stand nach der zwölften Bauwelle)

- 4 von 4 neuen Gates rot bewiesen (Seitenverhältnis, unbekanntes Bild, leerer Header,
  Navigation gegen main.js), danach wieder grün
- Cache-Gate rot bewiesen: eine Änderung an style.css ohne Bump meldet 109 Fehler
- Generatorlauf (`gen_pages`, `gen_longtail`, `gen_hubs`) danach: verify bleibt grün,
  Navigation überlebt, Assetversionen bleiben stehen
- Browser-Gegenprobe mit und ohne JS, Desktop und 375px: Navigation vollständig, kein
  horizontaler Überlauf

### Zusätzlich gelernt

35. **Ein Werbebanner ist kein Produktfoto, auch wenn es aus der Produktgalerie kommt.**
    Amazon-A+-Bilder tragen eingebrannte Herstellerwerbung. Sie liegen in derselben
    Galerie wie echte Produktfotos und sind über die URL nicht unterscheidbar. Nur das
    Hauptbild ist verlässlich werbefrei, weil Amazon das vorschreibt. Wer ein
    Galeriebild redaktionell einsetzt, muss es ansehen.

36. **Eine Zahl im Markup ist eine Behauptung über eine Datei.** `width` und `height`
    sagen: so ist dieses Bild geformt. Wechselt die Quelle, bleibt die Behauptung stehen
    und wird falsch — genau wie ein Preis, der im Text stehen bleibt. Maße gehören
    gemessen und belegt, nicht getippt.

37. **Wenn ein neues Gate sofort vierzehn Treffer meldet, ist erst die Regel verdächtig.**
    Der Reflex ist, eine Ausnahme einzubauen. Richtig war: nachsehen, was die Treffer
    gemeinsam haben, und die Regel auf das schärfen, was sie eigentlich meint. Hier war
    das Verhältnis gemeint, nicht die Pixelzahl.

38. **Eine Aussage, die auf jeder Seite steht, prüft nichts mehr.** Sobald der Datenstand
    statisch im Header stand, konnte das lastmod-Gate nur noch für alle oder für keine
    Seite feuern. Ein Gate, das immer oder nie anschlägt, ist keins. Chrome gehört vor
    einer seitenbezogenen Prüfung entfernt.

39. **Ein Widerspruch zur eigenen Quelle ist schwerer zu sehen als ein falscher Wert.**
    „Bessere Sticks" verletzt keinen Wert in products.json, sondern die eigene
    Vergleichstabelle zwei Absätze tiefer und den eigenen Ratgeberartikel. Kein
    Datenabgleich findet so etwas. Gefunden hat es ein Prüfer, der beide Texte gelesen
    hat — das bleibt Handarbeit.

---

## Nachtrag: zwölfte Prüfrunde

Keine Freigabe, sieben Blocker. Der schwerste stammte aus meiner eigenen Arbeit in der
Runde davor.

### Der Befund, den ich selbst gesehen und weggeredet habe

Beim Drift-Check nach dem Header-Umbau lief ich `gen_hubs.py`. Danach meldete verify
**256 JSON-LD-Blöcke statt 247**. Ich habe die Zahl gelesen, als Generator-Output
verbucht und weitergearbeitet. Tatsächlich standen ab diesem Moment **ItemList,
BreadcrumbList und FAQPage doppelt auf allen drei Haupt-Hubs**, dazu der SEO-Text.
Ursache: `gen_hubs.py` hängte bei jedem Lauf an, statt zu ersetzen. `verify.py` zählte
Schema-Blöcke, prüfte aber nie auf Dubletten, und blieb grün. Ein zweiter Lauf hätte
neun Blöcke erzeugt, ein dritter zwölf.

Die Lehre ist nicht "Generator war kaputt", sondern: **eine Kennzahl, die sich ohne
erklärbaren Grund ändert, ist ein Befund.** Ich hatte die Erklärung nicht, habe mir aber
eine gebaut.

### Was die Reparatur nebenbei ans Licht brachte

`gen_hubs.py` bekam Marker-Idempotenz (P-11) plus eine Aufräumregel für den markerlosen
Altbestand. Beim Umbau fiel auf: Das Karten-Muster verlangte ein **leeres** Grid
(`>\s*</div>`). Ein zweiter Lauf war dadurch zwar folgenlos, aber der Generator hat seine
Hauptaufgabe stumm übersprungen: Eine Änderung an products.json wäre auf diesen vier
Seiten mit 118 Karten **nie angekommen**. Nicht-Idempotenz und stilles Nichtstun sahen
von außen gleich aus.

Sobald das Grid tatsächlich neu rendert, meldete das §A1-Audit sofort einen Fehler, der
seit Langem eingefroren war: `products.json` hielt `"Tablet/iPad &lt;10mm"` als
HTML-Entity. Der Generator escapte sie ein zweites Mal zu `&amp;lt;`. Der Datenkern hält
jetzt Klartext (`<10mm`), die Renderer escapen. Im selben Zug stand das Audit selbst
falsch da: Es verglich den escapten Seitenwert gegen den rohen JSON-Wert, während die
Zeile darüber beim Claim längst korrekt gegen `esc()` prüfte.

### Die übrigen sechs

**Werbebanner umetikettiert statt entfernt.** Ich hatte den falschen Alt-Text ersetzt und
das Bild stehen lassen. Es lief weiter in der Galerie unter "Produktbilder" und im
`image`-Array des Product-Schemas, das Google als Produktbild liest. Beim Nachprüfen:
**alle drei Galeriebilder des Kishi V3 sind A+-Werbebanner** mit eingebrannten Razer-
Werbezeilen. Galerie geleert, Schema auf das werbefreie Hauptbild reduziert, alle drei
Bild-IDs in VERBOTEN. Symptom behandeln heißt hier: das Bild bleibt.

**Preise, die per Link an ein Produkt gebunden sind, prüfte niemand.** Beide Audits
binden Preise über Namen und Aliase. Ein Preis, der über `href="/produkte/<slug>/"` an
ein Produkt gebunden ist, war für beide unsichtbar, obwohl der Slug maschinenlesbar
danebensteht. Auf `blog/mobile-gaming-setup/` standen deshalb ein Kühler mit 18 statt
16 Euro (dreimal), ein Trigger-Link auf ein 20-Euro-Produkt neben "ab 9 Euro" (9 Euro
stimmt, der Link zeigte auf das falsche Produkt) und eine Setup-Summe von 90 statt 87
Euro, die zwei Absätze höher korrekt gerechnet war. Alle drei Gates grün.

**Ein FEHLENDER Header fiel nicht auf, nur ein leerer.** `if not _m: continue`. Die
Unterscheidung lag 28 Zeilen höher bereit: Das Footer-Gate trennt Stubs über
`http-equiv="refresh"`.

**Die Navigation wurde nur an den hrefs geprüft.** Ein Nav-Label ließ sich durch
beliebigen Text ersetzen, und der Trust-Strip mit drei Aussagen auf 109 Seiten war
vollständig ungeprüft. Jetzt Zeichenvergleich gegen `sync_header.header_html()`.

**"42 Modelle im Sortiment" war auf 109 Seiten ungeprüft.** Das Zähler-Gate nutzte
`re.search`, also genau ein Vorkommen je Datei, und kannte nur zwei fest benannte
Dateien. `index.html` trägt die Zahl viermal. Vor dem statischen Header stand sie an
einer Laufzeitstelle, danach an 112 — das Gate wurde nicht mitgezogen.

**`_SCHWELLE` stellte jede "ab N €"-Behauptung prüffrei.** Mein `re.I` aus derselben
Session hat die Ausnahme verbreitert, nicht verengt, und `und` exemptierte eine sehr
große Klasse normaler Prosa. `und` gilt jetzt nur noch als zweite Hälfte einer Spanne
("zwischen 30 und 100 Euro", 6 Stellen im Repo, alle in dieser Form). Für "ab N €" gibt
es ein eigenes Gate, das ausdrücklich benennt, was es NICHT kann: Es kennt die gemeinte
Menge nicht und prüft deshalb nur, dass N überhaupt ein Preis ist, den wir führen.

### Verify

Neun Rot-Proben, alle bestanden, danach grün: Schema-Dublette · fehlender Header ·
gefälschtes Nav-Label · gefälschter Trust-Strip · gefälschte Bestandszahl am zweiten und
am vierten Vorkommen · Preis hinter Produktlink · unbelegte Untergrenze · zweite
veraltete Asset-Referenz hinter einer korrekten. `gen_hubs.py` über drei Läufe
hash-identisch. `verify.py` grün, `audit_prosa.py` 0, `sync_product_values.py --audit` 0.

### Zusätzlich gelernt

40. **Eine Kennzahl, die sich ohne erklärbaren Grund ändert, ist ein Befund.** 247 auf
    256 JSON-LD-Blöcke war die Meldung, dass gerade eine Regression entstanden ist. Ich
    habe sie gelesen und mir eine Erklärung gebaut, statt nachzusehen. Wer eine Zahl
    erklärt, ohne sie geprüft zu haben, hat sie nicht erklärt.

41. **Nicht-Idempotenz und stilles Nichtstun sehen von außen gleich aus.** Beide Muster
    in `gen_hubs.py` führten dazu, dass ein zweiter Lauf "nichts kaputt machte". Beim
    einen wuchs die Datei, beim anderen wurde die Hauptaufgabe übersprungen. Idempotenz
    beweist man mit identischen Hashes UND mit einem Test, dass eine Quelländerung
    ankommt.

42. **Ein Gate, das etwas zählt, prüft es nicht.** verify zählte Schema-Blöcke in jeder
    Ausgabe und blieb bei sechs statt drei grün. Eine Zahl im Report ist keine
    Invariante.

43. **Umetikettieren ist keine Reparatur.** Der falsche Alt-Text war das Symptom, das
    Werbebanner die Ursache. Wer den Text korrigiert und das Bild stehen lässt, hat die
    Behauptung verschoben, nicht entfernt. In die VERBOTEN-Liste gehört die Ursache, hier
    die Bild-ID, nicht nur der Wortlaut.

44. **Eine Bindung kann auch ein Link sein.** Beide Audits ordneten Preise über Namen zu.
    Dass ein `href="/produkte/<slug>/"` daneben steht und maschinenlesbar genau sagt,
    worum es geht, hat niemand genutzt. Die verlässlichste Zuordnung im Markup blieb
    ungenutzt, während über Namensähnlichkeit gematcht wurde.

45. **Wer eine Aussage ins Chrome verschiebt, muss ihr Gate mitverschieben.** "42 Modelle
    im Sortiment" stand vor dem statischen Header an einer Laufzeitstelle und danach an
    112. Das Gate prüfte weiter genau eine. Jede Änderung am Geltungsbereich einer
    Aussage ist auch eine Änderung am Geltungsbereich ihrer Prüfung.

46. **Ein Gate soll sagen, was es nicht kann.** Das neue "ab N €"-Gate kennt die gemeinte
    Menge nicht und schreibt das in den Kommentar. Sonst liest der nächste Durchgang
    Grün als "Untergrenzen sind geprüft" und hört dort auf zu suchen.

---

## Nachtrag: dreizehnte Prüfrunde

Sechs Blocker. **Vier davon sind beim Schließen der Runde-12-Blocker neu entstanden.**
Das ist die Kernbeobachtung dieser Runde und kein Zufall: Jede Korrektur verschiebt etwas,
und wer nur das Ergebnis prüft und nicht die Nachbarschaft, baut den nächsten Fehler ein.

### Die vier selbstgemachten

**Schreiber und Prüfer auseinandergelaufen.** In Runde 12 hatte ich das §A1-Audit auf
`esc(v)` umgestellt, weil products.json jetzt Klartext hält. Den SCHREIBER derselben
Datei habe ich nicht mitgezogen. Folge: Ein Lauf von `sync_product_values.py` schrieb
`<10mm` roh ins Markup, das eigene Audit erwartete `&lt;10mm` und wurde rot. Schlimmer:
Das Muster `[^<]*` endete am eingeschleusten `<`, der Rest blieb stehen, und jeder
weitere Lauf hängte den Wert erneut davor: `&lt;10mm&lt;10mm&lt;10mm`. Das ist exakt die
Anhäng-Klasse, die ich eine Runde vorher in `gen_hubs.py` repariert hatte, in einer
anderen Datei wieder eingebaut.

**Escaping nur für das Label.** `gen_pages.py` escapte das Tabellen-Label, nicht den Wert.
Gegen HEAD war das ein Rückschritt: Dieselbe Angabe stand auf den Karten korrekt als
`&lt;10mm` und in der Technik-Tabelle roh. `verify.py` 6c vergleicht zeichengleich gegen
den Generator — ein Defekt IM Generator ist dadurch grundsätzlich unsichtbar.

**Das Link-Preis-Gate übersprang Links.** Der Schwanz `.{0,200}` war Teil des Treffers,
also konsumierte jeder Match bis zu 200 Zeichen, und `finditer` setzte dahinter auf. Auf
`blog/mobile-gaming-setup/` fehlte dadurch ausgerechnet der Link, dessen falscher Preis
das Gate überhaupt ausgelöst hatte: von drei Produktlinks sah das Gate zwei. Mit
Lookahead sind es repoweit 232 statt vorher gezählter 22. Dazu zwei weitere Löcher, die
der Prüfer belegt hat: Ein `<strong>` um den Preis machte ihn unsichtbar (der Schwanz
endete am ersten `<`), und die Regex verlangte `<a href="` wörtlich, womit zwei Links mit
`class=` davor nie geprüft wurden.

**Der Fensterrand war zu weit.** Nach dem Öffnen des Fensters meldete das Gate einen
Preis, der stimmte: Hinter dem Link auf den Black Shark begann auf
`produkte/razer-phone-cooler/` der nächste Abschnitt mit der EIGENEN Preistabelle.
"Direkt hinter dem Link" endet jetzt am Block, nicht nach 200 Zeichen.

### Die zwei übrigen

**`platformLabel` blieb beim worksOn-Fix stehen.** Als der VITURE-Eintrag in Runde 6 sein
falsches `ios` verlor, behielt er `platformLabel: "Universal"`. Über `ALT_PLATFORM` in
`gen_pages.py` wird daraus "für Android & iPhone" — auf derselben Seite, deren Lead
"Kein iOS, kein Bluetooth" sagt. `platformLabel` kam in keinem der drei Prüfskripte vor.

**Die Werbebanner sind eine Klasse, keine drei IDs.** Ich hatte drei Razer-Bild-IDs in
VERBOTEN gesetzt. Der Prüfer fand dieselbe Sorte beim ROG Tessen (alle drei Galeriebilder,
selbst nachgeprüft: "Compatible with Any Phone Cases / Equipped with 7–14.5 mm rubber
pads" über losen Gummi-Abstandshaltern), bei GameSir und bei Backbone. Von sechs
stichprobenartig angesehenen Nicht-Razer-Bildern waren vier Banner. Bei 116 Galeriebildern
kann eine Sperrliste nach ID das nicht schließen.
Die Grenze, die ich ziehen konnte: **Das Amazon-HAUPTBILD ist die einzige Klasse, die
garantiert werbefrei ist**, weil Amazon dafür weißen Hintergrund ohne Text vorschreibt.
`Product.image` führt jetzt nur noch dieses eine Bild, in allen 59 Schemas, mit Gate.
Die sichtbaren Galerien bleiben stehen und sind als Katalogbilder ausgewiesen; ob dort
Herstellerwerbung stehen darf, ist eine Lizenz- und Kennzeichnungsfrage für Yasin. Das
Gate schreibt ausdrücklich hin, dass es dazu nichts sagt.

### Ein eigener Fehler beim Prüfen

Beim Rücksetzen einer Rot-Probe habe ich `git checkout` auf eine Datei mit
ungecommittetem Sessionstand ausgeführt und damit die komplette Überarbeitung von
`vergleich/kishi-ultra-vs-g8-plus/` vernichtet (119 € statt 63 €, falscher Preis-Sieger,
26 verify-Fehler). Genau dieser Vorfall steht seit dem 30.09. schon einmal in diesem
Protokoll. Gerettet hat der Snapshot, den der Prüfer als `git stash create` angelegt
hatte. **Rot-Proben werden ab sofort über eine Scratchpad-Kopie zurückgesetzt, nie über
`git checkout`.**

### Verify

Acht Rot-Proben, alle bestanden, danach grün: Spec-Wert roh eingeschleust (Sync heilt
selbst) · Galeriebild zurück ins Product-Schema · Untergrenze im Rest einer
Bandüberschrift · platformLabel gegen worksOn · Preis in `<strong>` hinter einem
Produktlink · Preis hinter einem Link mit `class=` davor · blanker Preis als Kontrolle ·
Schema-Dublette. Drei Läufe `sync_product_values.py` sind No-ops. Alle sieben Generatoren
über zwei volle Durchläufe hash-identisch, UND eine Teständerung an products.json
(16 → 17 €) kommt in allen erzeugten Seiten an, ohne Altwert-Rest. products.json exakt
zurückgesetzt, jede verbleibende Abweichung gegen HEAD einzeln begründet.

### Zusätzlich gelernt

47. **Wer den Prüfer ändert, muss den Schreiber mitändern.** Audit und Sync sind zwei
    Seiten derselben Regel. Ich habe die Vergleichsseite auf `esc()` umgestellt und die
    Schreibseite vergessen — das Ergebnis war nicht nur rot, es vervielfachte den Wert
    bei jedem Lauf.

48. **Ein Gate, das den Kontext mitkonsumiert, überspringt Treffer.** `finditer` setzt
    hinter dem Match auf. Steht der geprüfte Kontext IM Match, verschluckt jeder Treffer
    den nächsten. Kontext gehört in einen Lookahead. Der Unterschied waren hier 22 gegen
    232 geprüfte Stellen — und das Gate meldete beide Male grün.

49. **Ein Fenster in Zeichen ist kein Kontext.** 200 Zeichen reichten über den Absatz
    hinaus in die nächste Tabelle. Kontext endet an Blockgrenzen, nicht nach einer
    Zeichenzahl.

50. **Eine Sperrliste schließt keine Klasse.** Drei verbotene Bild-IDs, während 116
    Galeriebilder derselben Sorte weiterliefen. Wo man die einzelnen Fälle nicht prüfen
    kann, braucht es eine strukturelle Grenze — hier: nur das Amazon-Hauptbild, weil
    dessen Werbefreiheit von Amazon erzwungen wird.

51. **Ein Datenfeld, das nirgends geprüft wird, ist eine Datenquelle.** `platformLabel`
    kam in keinem der drei Prüfskripte vor und steuerte trotzdem den Alt-Text jedes
    Produktbildes. Die Frage "welche Felder liest der Generator?" ist eine andere als
    "welche Felder prüfen wir?" — und die zweite Liste war kürzer.

52. **`git checkout` ist bei ungecommittetem Stand ein Löschbefehl.** Zum zweiten Mal in
    derselben Session verloren. Rot-Proben werden über Scratchpad-Kopien zurückgesetzt.

---

## Entscheidung Yasin (30.09.): Galerien bleiben

Auf die Frage, ob Herstellerwerbung mit eingebrannter Werbezeile in den sichtbaren
Galerien stehen darf: **so lassen, Banner nicht einzeln prüfen.**

Daraus folgt:

- Die Galerie der Kishi-V3-Review ist **wiederhergestellt**. Ich hatte sie in Runde 13
  entfernt, weil alle drei Bilder A+-Banner sind. Nach dieser Entscheidung wäre sonst
  ausgerechnet ein Produkt ohne Galerie, während 39 andere ihre behalten. Die drei
  Alt-Texte sind die ursprünglichen und beschreiben zutreffend, was zu sehen ist.
- Die drei Razer-Bild-IDs sind **aus der VERBOTEN-Liste raus**. Eine Sperre gegen Bilder,
  die laut Entscheidung stehen bleiben sollen, wäre eine Invariante gegen den eigenen
  Beschluss.
- **Was bleibt:** Falsche Alt-Texte sind weiter gesperrt (das war nie die Bilderfrage,
  sondern eine Beschreibungsfrage). Und `Product.image` führt weiter nur das
  Amazon-Hauptbild. Das ist bewusst NICHT von der Entscheidung berührt: In den
  strukturierten Daten liest Google DAS Produktbild und kann es als solches ausspielen.
  Ein Werbebanner an dieser Stelle ist eine Aussage an die Suchmaschine, nicht eine
  Illustration für Leser. Falls Yasin das anders will, ist es eine Zeile in
  `gen_pages.py`.

**Gelernt (53):** Eine Entscheidung des Eigentümers gilt für die ganze Klasse, nicht nur
für den Fall, der die Frage ausgelöst hat. Die Galerie, die ich vorab entfernt hatte,
gehörte zurück — sonst hätte meine eigene Vorwegnahme eine Inkonsistenz hinterlassen, die
niemand beschlossen hat.

---

## Nachtrag: vierzehnte Prüfrunde

Zwei Blocker. Fünf der sechs Runde-13-Fixes halten, und beide Blocker sind dieselbe
Fehlerfamilie in zwei Ausprägungen: **Ein Gate, das Mitgliedschaft in einer Liste prüft
statt Bindung an das konkrete Objekt.**

### Blocker 1: Das Schema-Bild-Gate war eine Freigabeliste

Ich hatte geschrieben `if _b not in _HAUPTBILDER` — also "ist das irgendein Hauptbild aus
dem Sortiment", nicht "ist das DAS Hauptbild dieses Produkts". Der Prüfer hat das
ASUS-ROG-Bild ins Schema des GameSir G8 Galileo getauscht: **alle drei Gates grün.**

Das ist exakt der Fehler, der die gesamte Bildarbeit ausgelöst hat ("ASUS-ROG-Werbebild
als GameSir-Testsieger"), und derselbe Bauplan wie der `ALLE_PREISE`-Freibrief, der in
Runde 5 gestrichen wurde, **weil er vier Prüfrunden lang einen Fehler gedeckt hatte.**
Dritter Auftritt derselben Konstruktion, diesmal von mir gebaut, während der Grund für
ihre Streichung zwei Bildschirme weiter oben im selben Protokoll steht.

Die Fehlermeldung war dabei ehrlicher als der Code: Sie sagte "dort gehört nur das
Amazon-Hauptbild hin", geprüft wurde etwas Schwächeres. Reichweite: 12 der 41
Product-Schemas stehen auf handgepflegten Review-Seiten, für die es kein anderes Gate
gibt. Gebunden wird jetzt über den Schema-`name`, abgesichert über die `data-asin`
derselben Seite; lässt sich das Produkt nicht eindeutig bestimmen, ist **das** der
Fehler, statt still auf die Liste zurückzufallen.

### Blocker 2: Audit und Schreiber mit verschiedener Reichweite

Runde 13 hatte den Schreiber der Spec-Chips erweitert, damit er über Fremdtags
hinweggreift. Das Audit endete weiter am ersten `<`. Folge: sichtbarer Zusatztext in
einer Karte (`… &lt;10mm<strong> und PC und Konsole</strong>`) war für alle drei Gates
unsichtbar **und wurde vom nächsten Sync-Lauf spurlos gelöscht.**

Dieselbe Familie wie Runde-13-Blocker 1, nur eine Dimension weiter: dort waren Audit und
Schreiber sich über das Escaping uneins, hier über die Reichweite. Zweimal derselbe
Riss zwischen zwei Regexen, die dasselbe beschreiben sollen. Konsequenz: Beide benutzen
jetzt **eine gemeinsame Konstante** `CHIP_REST`. Ein Riss ist damit nicht mehr möglich,
ohne beide Seiten zugleich zu ändern.

### Was der Prüfer außerdem bestätigt hat

Die Prämisse hinter der Schema-Reduktion ("das Amazon-Hauptbild ist werbefrei") hat er an
den neun stark nicht-quadratischen Hauptbildern nachgesehen: alle saubere Freisteller auf
Weiß. Das Link-Preis-Gate erfasst nachgezählt **232 Stellen** und damit exakt alle
Produktlinks im Repo. Eine Teständerung an products.json (63 → 77 €) löst 44 Befunde über
zehn verschiedene Prüfwege aus.

### Drei Grenzen, die jetzt im Code stehen

- Das Link-Preis-Gate schaut nur **hinter** den Link. Ein Preis davor, dessen Produktbezug
  allein im Linktext steht, fällt durch. Eine Prüfung davor hätte Fehlalarme auf legitime
  Differenzsätze erzeugt ("kostet 64 Euro mehr"); alle 232 Stellen wurden von Hand
  abgesucht, ohne echten Fund.
- Das Bildmaß-Gate beweist "HTML passt zum Belegstand", nicht "Belegstand passt zur
  Wirklichkeit". Dafür gibt es jetzt `mess_bilder.py --check`, das jedes Bild live
  nachmisst (22/22 identisch).
- `sync_detail_felder` schrieb den Preis roh in dieselbe Zelle, die `gen_pages.py` escapt
  schreibt. Kein Live-Risiko, aber der dritte Schreiber-Riss an einem Tag; jetzt escapt.

### Verify

Vier Rot-Proben mit den exakten Belegen des Prüfers, danach grün: fremdes Hauptbild im
Product-Schema · sichtbarer Zusatztext im Spec-Chip · gefälschter Bildmaß-Belegstand ·
drei Sync-Schreibläufe als No-op. Alle sieben Generatoren über zwei volle Durchläufe
byte-identisch. Vier Gates grün: `verify.py`, `audit_prosa.py`,
`sync_product_values.py --audit`, `mess_bilder.py --check`.

### Zusätzlich gelernt

54. **Eine Freigabeliste ist kein Gate.** "Ist der Wert in der Menge aller erlaubten
    Werte?" beantwortet nie die Frage "gehört dieser Wert HIERHIN?". Dreimal an einem Tag
    gebaut: `ALLE_PREISE`, die Sternwert-Freigabe, jetzt die Hauptbild-Liste. Das Muster
    ist erkennbar an seiner Formulierung — `x in ALLE_…` statt `x == das_erwartete`.
    Wenn sich das Objekt nicht auflösen lässt, ist DAS der Fehler.

55. **Wer eine Fehlermeldung schreibt, die mehr verspricht als der Code prüft, hat den
    Befund schon formuliert.** "Dort gehört nur das Amazon-Hauptbild hin" beschrieb die
    richtige Regel, während daneben die falsche stand. Meldungstext und Bedingung gehören
    beim Schreiben gegeneinander gelesen.

56. **Zwei Regexe, die dasselbe beschreiben, laufen auseinander.** Nicht vielleicht,
    sondern zuverlässig, und zwar bei der nächsten Änderung an genau einer von beiden.
    Zweimal an einem Tag passiert (Escaping, dann Reichweite). Gemeinsames Muster in eine
    Konstante, die beide benutzen.

---

## Nachtrag: fünfzehnte Prüfrunde

Vier Blocker. Dazu ein Zwischenfall, der nichts mit dem Code zu tun hatte: **Die externe
Platte hat sich mitten im Prüflauf abgemeldet**, mit einem Teststand auf der Platte
(G8-Galileo auf 77 € plus ein kompletter Generator-Durchlauf). Gerettet hat die
Backup-Disziplin des Prüflaufs: Dateikopien plus SHA-256-Manifest vor der ersten
Änderung, kein `git`-Eingriff. Nach dem Wiedereinhängen byte-genau zurückgesetzt, 238
Dateien, 0 Abweichungen, `git diff --shortstat` identisch mit dem Sessionbeginn. Ich habe
das unabhängig nachgeprüft, bevor ich weitergebaut habe.

### B1: Das Gate band an die Behauptung, nicht an die Identität

Meine Runde-14-Korrektur löste das Produkt über den **Schema-Namen** auf und sicherte das
angeblich mit `data-asin` ab. Tatsächlich kehrte die Funktion bei eindeutigem
Namenstreffer sofort zurück — der ASIN-Zweig war toter Code, bei allen 41 Schemas. Wer
`name` UND `image` gemeinsam auf ein fremdes Produkt stellte, kam durch: Die Seite lieferte
ein Product-Schema mit fremdem Namen und fremdem Foto, aber eigenem Preis und eigener
Bewertung.

Das ist die Runde-14-Lehre in ihrer nächsten Verkleidung. Dort war es eine Freigabeliste,
hier eine Bindung an das Objekt, das der Prüfgegenstand selbst *behauptet* zu sein. Beides
läuft darauf hinaus, die Behauptung gegen sich selbst zu prüfen. Die Identität einer Seite
steht im Pfad und in ihren `data-asin`, nicht in dem Feld, das manipuliert werden könnte.
Und wieder versprach der Kommentar ("abgesichert mit den data-asin derselben Seite") etwas,
das der Code nicht tat.

### B2: Mein Reparaturwerkzeug machte denselben Fehler wie der HTML-Parser

`CHIP_REST` übersprang Tags mit `<(?!/|span|div|p\b)[^>]*>`. Bei einem rohen `<` im Wert
las das Muster `<10mm</span>` als **ein** Tag und verschluckte das schließende `</span>`.
Der Schreiber löschte es, alle vier Gates blieben grün, der zweite Lauf war idempotent —
der kaputte Zustand war damit dauerhaft. Erreichbar über den vorgeschriebenen
Reparaturweg: Audit rot, Sync laufen lassen, grün, Markup kaputt.

Die erste Korrektur (Buchstabe nach `<` verlangen) machte es sichtbar, reparierte aber nur
halb: Der Wert wurde richtig geschrieben, der rohe Rest blieb stehen. Die richtige Lösung
war, den Chip an seinem **eigenen** schließenden `</span>` zu begrenzen statt Tags zu
überspringen. Damit ist der erfasste Bereich exakt der Chipinhalt, egal was darin steht.
Drei Defektformen durchgespielt (rohes `<`, fremdes Element, leerer Wert): alle drei
werden rot, der Sync stellt byte-identisch wieder her, verify endet grün.
Dazu ein neues Gate: Ein rohes `<`, das kein Tag eröffnet, ist ein Fehler. Die Tag-Bilanz
zählte bisher nur `<div>`.

### B3: Einen Befund teilweise zu schließen heißt, ihn offen zu lassen

Der ursprüngliche Bildbefund nannte ausdrücklich `og:image` und `twitter:image`. Ein Gate
bekam nur der Schema-Zweig. Beide Felder und das sichtbare Produktfoto ließen sich auf ein
fremdes Produkt umstellen, ohne dass eins der vier Gates etwas sagte. Jetzt gegen das
Produkt der Seite gebunden, auf Seiten mit Product-Schema — die Vergleichsseiten tragen
bewusst das Standard-OG-Bild und hätten sonst drei Fehlalarme erzeugt.
Den `<title>` prüfe ich bewusst nicht: "Backbone One – PlayStation Edition" steht dort als
"Backbone One PlayStation Edition", eine Normalisierung bräuchte mehr Regeln als der Fall
wert ist. Das steht als Begründung im Code.

### B4: Eine Reparaturanweisung, die ins Leere zeigt

Für alle 39 generierten Seiten nannte die Meldung `gen_pages.py --regen <slug>` und
`gen_content.py`. Für die 10 Longtail-Seiten gibt dieser Befehl "0 Seiten regeneriert" aus
und der Fehler bleibt stehen; richtig wären `gen_longtail.py` und `longtail.json`. Das ist
schlimmer als keine Anweisung: Man führt sie aus und glaubt, es sei erledigt.

### Verify

Elf Rot-Proben, alle bestanden, danach grün: Schema-Name fremd · Schema-Bild fremd · beide
zugleich · rohes `<` im Chip · fremdes Element im Chip · leerer Chipwert · og:image ·
twitter:image · cta-photo · falscher canonical · fremdes Video-Poster. Dazu die
Gegenprobe, dass eine gen_pages-Seite weiterhin ihren eigenen Befehl genannt bekommt.
Der gelieferte Stand ist ein Generator-Fixpunkt: Ein voller Durchlauf ändert nichts, zwei
weitere ebenfalls nicht. Vier Gates grün.

### Zusätzlich gelernt

57. **Ein Gate darf nie an das binden, was der Prüfgegenstand über sich behauptet.** Der
    Schema-Name ist Teil dessen, was geprüft werden soll — ihn als Schlüssel zu benutzen,
    heißt die Behauptung gegen sich selbst zu halten. Identität kommt von außen: aus dem
    Pfad, aus `data-asin`, aus dem Dateinamen.

58. **Wenn der Kommentar eine Absicherung verspricht, prüf nach, ob der Code sie
    erreicht.** Zweimal hintereinander beschrieb mein Kommentar die richtige Regel,
    während daneben eine schwächere stand. Beim zweiten Mal war der versprochene Zweig
    nachweislich unerreichbar.

59. **Ein Reparaturwerkzeug, das Markup per Regex überspringt, macht die Fehler des
    Parsers nach.** Wer Tags überspringen will, muss wissen, was ein Tag ist. Sicherer ist,
    den Bereich an seiner eigenen Grenze festzumachen statt an dem, was darin stehen
    könnte.

60. **Einen Befund teilweise zu schließen heißt, ihn offen zu lassen.** Der Bildbefund
    nannte og:image und twitter:image beim Namen; gebaut wurde ein Gate für den
    Schema-Zweig. Wer eine Befundbeschreibung liest, hakt jede darin genannte Stelle
    einzeln ab.

61. **Eine Reparaturanweisung ist Teil des Gates und wird mitgeprüft.** Sie zeigte für 10
    von 39 Seiten auf einen Befehl, der nichts tut.

62. **Teststände gehören in Dateikopien mit Manifest, nicht in den Kopf.** Als die Platte
    mitten im Lauf verschwand, war der einzige Grund, warum nichts verloren ging, ein
    Backup, das vor der ersten Änderung angelegt worden war.

---

## Nachtrag: sechzehnte Prüfrunde

Fünf Blocker, vier davon Regressionen aus Runde 15. Dazu ein eigener Fehler beim Bauen,
der zeigt, wie die Reparatur selbst zur Gefahr wird.

### Ein Gate, das sich mit einem Leerzeichen abschalten ließ

Das og:image-Gate aus Runde 15 begann mit `if '"@type": "Product"' not in _h: continue`.
Ein Leerzeichen mehr (`"@type" : "Product"`) schaltete es lautlos ab. Der Prüfer hat
genau das getan, dazu og:image, twitter:image und das sichtbare Foto auf ein fremdes
Produkt gesetzt: **alle vier Gates grün** — der Ursprungsbefund dieser ganzen Arbeit,
wieder offen. Fünfzehn Zeilen darüber parst das Schwestergate korrekt; ich habe daneben
gegreppt.

### Eine Identitätsprüfung, die 41 von 42 Seiten abdeckte

`_name_passt()` stand hinter einem `if not _bilder: continue`. Ein Product-Schema **ohne**
`image`-Feld konnte deshalb beliebig behaupten, ein anderes Produkt zu sein. Genau eine
Seite im Repo hat so ein Schema (`backbone-one-2-review`) — und genau deshalb fiel es
niemandem auf. Eine Prüfung, die 97 Prozent abdeckt, fühlt sich an wie eine, die wirkt.

### Zwei Fälle, die das alte Muster meldete und das neue nicht mehr

Mein `CHIP_REST`-Fix aus Runde 15 hatte kein DOTALL. Ein Chip, dessen Inhalt auf einer
eigenen Zeile steht, wurde ab da **gar nicht mehr gefunden**: Audit still, Schreiber
repariert nicht. Dasselbe bei fehlendem `</span>`, wo der Schreiber zusätzlich den
nachfolgenden Chip mitfraß, ohne dass ein else-Zweig das gemeldet hätte. Der Kommentar
darüber behauptete, der erfasste Bereich sei "exakt der Chipinhalt, egal was darin steht"
— für diese beiden Fälle griff er gar nicht.
Behoben mit `[\s\S]` statt DOTALL-Flag (ein `(?s)` mitten im konkatenierten Muster ist ein
`PatternError`), einem Abbruch am öffnenden `<span` und einem else-Zweig "Label da, Chip
nicht abgrenzbar".

### Ein Gate, das gegenüber seiner eigenen Begründung invertiert war

Mein Rohes-`<`-Gate meldete `<(?![a-zA-Z!/?])`, also `<10mm`. Der Kommentar daneben sagte,
so ein `<` breche den Parser. Mit `html.parser` nachgemessen:

```
'<p>Dicke <ab 20 Millimeter.</p>'  -> sichtbar: 'Dicke '
'<p>Dicke <10mm hier.</p>'         -> sichtbar: 'Dicke <10mm hier.'
```

Das Gate fing genau die harmlose Klasse und ließ genau die schädliche durch. `<ab` hält
der Parser für ein Element und frisst alles bis zum nächsten `>`. Geprüft wird jetzt
gegen die tatsächlich verwendeten Elementnamen: Was wie ein Tag aussieht, aber keins ist,
ist der gefährliche Fall. Die harmlose Variante bleibt gemeldet, sie ist trotzdem falsch.

### `offers.url` trug eine ungeprüfte ASIN

Der Affiliate-Tag darin ist seit Runde 6 repoweit gegated, die ASIN daneben nicht —
während für `data-asin` genau das seit Langem geprüft wird. Derselbe Fehler, eine Stelle
weiter.

### Mein eigener Fehler beim Bauen

Beim Einbau habe ich mit einer Textsuche auf `"for _f in pages:\n    _h = open(...)"`
gearbeitet und damit **das ItemList-Zähler-Gate überschrieben** — ein Block, der mit meiner
Änderung nichts zu tun hatte. Aufgefallen ist es sofort (NameError), repariert aus dem
Backup des Prüflaufs. Lehre: In einer 1246-Zeilen-Datei ist ein mehrzeiliges Textfragment
kein eindeutiger Anker. Entweder man liest die Stelle vorher und editiert gezielt, oder
man prüft, wie oft das Fragment vorkommt.

### Außerdem

Die Review-Seiten hingen für ihre Identität allein an `data-asin`, also an einer
Behauptung der Seite. Ein zweiter, völlig legitimer Kauf-Button ("Alternative ansehen")
machte verify rot **und** ließ gleichzeitig das og:image-Gate still durchlaufen.
`products.json[].detail` zeigt auf genau diese Seiten und ist eine externe Identität;
verify und sync lösen jetzt in derselben Reihenfolge auf: Pfad, detail, dann ASIN.
Dazu listenfest gemacht: `"@type": ["Product"]` ließ verify mit `TypeError` abstürzen —
statt Befunden kam ein Traceback, und alle übrigen Befunde des Laufs waren weg.

### Verify

Zehn Rot-Proben, alle bestanden: Leerzeichen-`@type` mit fremden Bildern · Schema ohne
Bild mit fremdem Namen · fremde ASIN in `offers.url` · mehrzeiliger Chip mit falschem Wert
(repariert byte-identisch) · Chip ohne schließendes `</span>` · `<ab` · `<Typ` · `<10mm` ·
zweiter Kauf-Button als Fehlalarm-Gegenprobe (jetzt grün) · og-Gate greift trotz zweitem
Button. Vier Gates grün, alle sieben Generatoren idempotent, der Stand ist ein Fixpunkt.

### Zusätzlich gelernt

63. **Wer JSON greppt statt zu parsen, baut eine Abschaltung ein.** Ein Leerzeichen hat
    gereicht. Daneben lag ein Gate, das es richtig machte — die Versuchung ist, für den
    "schnellen Vorfilter" zu greppen, und genau der Vorfilter entscheidet dann alles.

64. **Eine Prüfung, die 41 von 42 Fällen abdeckt, fühlt sich an wie eine, die wirkt.**
    Die Lücke lag hinter einem `continue`, das für einen anderen Zweck da war.
    Reihenfolge von Bedingungen ist Geltungsbereich: Was hinter einem `continue` steht,
    gilt nur für den Rest.

65. **Ein Fix kann eine Prüfung verengen, ohne dass es auffällt.** Mein neues
    `CHIP_REST` fand zwei Fälle nicht mehr, die das alte meldete. Beim Ersetzen eines
    Musters gehört der Vergleich dazu: Was fand das alte, was findet das neue?

66. **Wenn Kommentar und Code sich widersprechen, miss nach, welcher recht hat.** Ich
    hatte die Begründung richtig aufgeschrieben und das Gegenteil implementiert. Zwei
    Zeilen `html.parser` hätten das beim Schreiben gezeigt.

67. **Ein mehrzeiliges Textfragment ist kein eindeutiger Anker.** Eine Textsuche hat in
    einer 1246-Zeilen-Datei einen fremden Block getroffen und überschrieben. Vor jedem
    skriptgesteuerten Ersetzen: zählen, wie oft das Fragment vorkommt.

---

## Nachtrag: siebzehnte Prüfrunde

Fünf Blocker, vier davon Regressionen aus Runde 16. Der erste ist der ärgerlichste der
ganzen Session.

### Ich habe die Freigabeliste gebaut, vor der mein eigener Katalog warnt

Runde 16 hat das Rohes-`<`-Gate auf eine Liste gültiger Elementnamen umgestellt. Das ist
wörtlich `x in ALLE_…` statt `x == das_erwartete` — die Bauart, die in Runde 14 dreimal
als Fehler erkannt und am selben Tag als Pattern aufgeschrieben wurde
(`SPC-PATTERNS.md`: "Eine Freigabeliste ist kein Gate").

Sie versagte in beide Richtungen zugleich:

- **Durchgelassen:** `Gewicht <b 200 Gramm ist leicht, Dicke <a 20 Millimeter …` — `b`
  und `a` stehen auf der Liste. Der Parser frisst rund 140 Zeichen sichtbaren Text, alle
  vier Gates grün. Ebenso `<span class="hinweis"Datenstand September 2026</span>`, ein
  Tag ohne schließendes `>`.
- **Falsch gemeldet:** 21 gültige Elemente (`<abbr>`, `<mark>`, `<clipPath>`, `<address>`,
  …) mit der Anweisung, sie als `&lt;` zu schreiben — befolgt hätte das das Markup
  zerstört. Dazu war der Kommentar falsch: Er behauptete, gegen "die tatsächlich im Repo
  verwendeten Elementnamen" zu prüfen, während 34 der 83 Namen nirgends vorkamen und 21
  gültige fehlten.

Die Lösung brauchte gar keine Liste. Die Regel ist **strukturell**: Zwischen einem
tag-eröffnenden `<` und dem nächsten `<` muss ein `>` stehen. Das kennt auch Elemente,
die wir noch nie benutzt haben. Gemessen: 0 Befunde auf den 125 Bestandsseiten, 10/10 in
der Gegenprobe, 6/6 gegen die Proben des Prüfers.

### Audit und Schreiber, dritter Riss

Runde 16 hat beide auf dasselbe Muster gebracht. Die **Vergleichsregel** blieb
verschieden: Das Audit strich Tags vor dem Vergleich weg (`re.sub(r'<[^>]*>','',…)`), der
Schreiber ersetzt den ganzen Bereich. Ein `<strong>` in einem Spec-Chip war damit für
alle vier Gates unsichtbar und wurde vom nächsten Sync ersatzlos gelöscht — wörtlich die
Klasse, die der Kommentar darüber als behoben beschreibt. Jetzt wird roh verglichen.

### "Listenfest" erreichte 3 von 6 Stellen

`_typen_von()` deckte drei `@type`-Vergleiche ab, drei Stringvergleiche blieben stehen.
Über `"@type": ["Product"]` ließen sich damit die GSC-Invariante, der ItemList-Zähler und
die Schema-Preis-/Bewertungsprüfung abschalten. Der Helfer stand außerdem erst ab Zeile
660 und war für die Stellen davor gar nicht erreichbar.

### Eine Vorbedingung, die der Prüfling selbst stellt, ist keine

Das og:image-Gate begann mit `if not _hat_produktschema(_h): continue`. Wer das
Product-Schema entfernte oder sein `@type` auf `"Thing"` änderte, schaltete die komplette
Bildprüfung ab: alle vier Bilder auf ein fremdes Produkt, verify grün. Und nichts
verlangte, dass eine Produktseite überhaupt ein Product-Schema trägt.
Die Vorbedingung hängt jetzt an der **externen** Identität (Pfad bzw.
`products.json[].detail`), und eine Produktseite ohne Product-Schema ist selbst ein
Befund. Der Angriff des Prüfers ergibt statt Grün vier Fehler.

### Noch ein eigener Fehlalarm, sofort beim Testen

Das neu eingebaute Verwaisten-Gate meldete beim ersten Lauf **alle zehn Longtail-Seiten**
als verwaist. Sie werden von `gen_longtail.py` aus `longtail.json` gebaut; meine
Bekannt-Menge kannte nur `products.json`. Ein Gate, das beim ersten Lauf zehn Fehlalarme
erzeugt, hat die Quellenlage nicht verstanden.

### Verify

Vierzehn Rot-Proben, alle bestanden: Tag ohne `>` · `<b 200 Gramm` · `<ab` · `<10mm` ·
`<abbr>` und `<address>` als Gegenprobe grün · `<strong>` im Spec-Chip (repariert
byte-identisch) · ItemList-Zähler mit Listen-`@type` · Schema-Preis mit Listen-`@type` ·
`@type: Thing` plus drei fremde Bilder · fehlendes Product-Schema · echte verwaiste Seite
· die zehn Longtail-Seiten als Fehlalarm-Gegenprobe. Vier Gates grün, alle sieben
Generatoren idempotent, der Stand ist ein Fixpunkt.

### Zusätzlich gelernt

68. **Eine Regel, die eine Liste braucht, ist meist die falsche Regel.** Die
    Elementnamen-Liste war in beide Richtungen falsch und hätte nie vollständig werden
    können. Die strukturelle Formulierung ("zwischen `<` und dem nächsten `<` muss ein
    `>` stehen") ist kürzer, braucht keine Pflege und kennt auch, was wir noch nie
    benutzt haben. Wenn ein Gate eine Aufzählung erfordert, lohnt die Frage, welche
    Eigenschaft man eigentlich meint.

69. **Ein aufgeschriebenes Pattern schützt nicht vor dem Fehler, den es beschreibt.** Ich
    habe die Freigabeliste am selben Tag gebaut, an dem ich die Warnung davor formuliert
    habe. Die Patterns helfen beim Prüfen, nicht beim Schreiben — was heißt, dass das
    Prüfen gegen den eigenen Katalog ein eigener Arbeitsschritt ist.

70. **Ein gemeinsames Muster reicht nicht, wenn die Vergleichsregel auseinanderläuft.**
    Dritter Riss zwischen Audit und Schreiber an einem Tag, diesmal in der
    Normalisierung. Gemeinsam gehört alles, was beide über denselben Wert annehmen.

71. **Eine Vorbedingung, die der Prüfling selbst stellt, ist keine.** `if not
    hat_schema(): continue` heißt: Wer das Schema entfernt, schaltet die Prüfung ab.
    Vorbedingungen gehören an externe Identitäten, und das Fehlen des Geprüften ist
    selbst ein Befund.

72. **Ein neues Gate wird gegen den Bestand gemessen, bevor es als fertig gilt.** Zehn
    Fehlalarme beim ersten Lauf waren die Antwort auf eine Frage, die ich vorher nicht
    gestellt hatte: Wer baut diese Seiten eigentlich alles?

---

## Nachtrag: Landkarte der ungegateten Flächen

Ein paralleler Rechercheauftrag hat systematisch durchgezählt, welche Dateien, Felder und
Dateitypen von keinem der vier Gates angefasst werden. Ergebnis: **Keine HTML-Datei ist
ungelesen** (alle 125 heißen `index.html`, alle vier Gates traversieren sie), aber in den
gelesenen Dateien liegen Flächen ohne Prüfung. Zwei davon waren so schwer, dass sie sofort
geschlossen wurden.

### §A6, erster Satz, hatte nie ein Gate

CLAUDE.md sagt: "Jedes Review nennt mindestens zwei echte Schwächen. Schwache Produkte
(Rating unter 3,8) bekommen explizite Warnung statt Kaufempfehlung." Der **zweite** Satz
war seit Langem gegated. Der **erste** kam in allen vier Gates nur in Kommentaren vor.

Faktisch erfüllen ihn alle Seiten (13 handgepflegte Reviews und 29 Produktseiten, jeweils
mindestens zwei). Aber ein neuer Eintrag in gen_content mit einer oder null Schwächen wäre
durch jedes Gate gelaufen. Jetzt zweifach gesichert: ein Gate in verify.py und ein Abbruch
im Generator selbst, bevor die Datei geschrieben wird.

**Beinahe-Fehler dabei:** Meine erste Messung zählte con-item mit doppelten
Anführungszeichen und meldete 19 angeblich leere Seiten. Die handgepflegten Reviews
schreiben es mit einfachen. Ich hätte ein Gate auf eine falsche Zählung gebaut und 19
korrekte Seiten "repariert". Gezählt wird jetzt zitatunabhängig.

### Der Controller-Finder konnte ein schwaches Produkt als Empfehlung ausspielen

finder.js filtert auf type gleich controller, bewertet und zeigt die Top 3 unter der
Überschrift "Deine Top 3 Empfehlungen" mit dem Badge "Bester Match" — ohne Bewertung und
ohne die §A6-Warnung, die jede andere Fläche trägt. Unter den 28 Controllern liegt einer
unter 3,8 (Turtle Beach Atom, 3,5). Er konnte dort landen.

Der Rechercheauftrag hatte das als "zweite Bewertungsschwelle, nie gegen A6_SCHWELLE
gehalten" gemeldet. Das stimmte so nicht: Die Zahlen in score() sind **Ranking-Gewichte**,
kein Empfehlungs-Schwellwert, und sie auf 3,8 zu zwingen wäre falsch gewesen. Der
eigentliche Befund lag daneben und war schwerer: Die Ergebnisliste selbst kannte gar keine
Schwelle. Nachgesehen statt übernommen — und der richtige Fix war ein Filter vor der
Ausgabe, nicht eine Änderung am Scoring.

finder.js trägt die Schwelle jetzt als benannte Konstante, verify.py hält sie gegen
A6_SCHWELLE und prüft, dass sie auch angewandt wird. Im Browser durchgeklickt: sechs
Schritte, drei Empfehlungen, der schwache Controller ist raus, keine Konsolenfehler.

### Was offen bleibt und zu Yasin gehört

**Keines der vier Gates läuft in CI.** `.github/workflows/deploy.yml` ruft rsync und
deploy-pages auf, aber kein Gate. Die gesamte Absicherung dieser Session hängt daran, dass
jemand die Skripte von Hand startet. Änderungen an `.github/workflows/` sind laut CLAUDE.md
ein Stopp-Punkt, deshalb nicht angefasst — gehört gefragt.

Dazu kleinere Flächen als Merkposten: robots.txt-Inhalt (nur Existenz geprüft, ein
Disallow-Slash wäre grün), kein 404.html, das products.json-Feld platform nur auf
Nicht-Leer geprüft, video.duration in keinem Gate, platformLabel deckt 25 von 42 Produkten,
longtail.json nur als Rohtext statt als Struktur, Sitemap-Rückrichtung ist warn statt err.

### Zusätzlich gelernt

73. **Eine Regel aus zwei Sätzen braucht zwei Gates.** §A6 war zur Hälfte gesichert, und
    die gesicherte Hälfte hat die ungesicherte verdeckt: In jeder Prüfrunde stand "§A6 ist
    gegated" im Kopf, obwohl nur der zweite Satz gemeint war.

74. **Eine Befundmeldung kann auf das Richtige zeigen und das Falsche benennen.** Die
    "zweite Bewertungsschwelle" in finder.js war keine; der echte Fehler lag zwanzig Zeilen
    weiter und war schwerer. Wer den Befund wörtlich umgesetzt hätte, hätte das Scoring
    kaputtgemacht und den Fehler stehen lassen.

75. **Eine Messung, die 19 Treffer meldet, prüft man, bevor man sie zur Grundlage macht.**
    Doppelte statt einfache Anführungszeichen — und fast hätte ich 19 korrekte Seiten
    "repariert". Dieselbe Lehre wie bei den vierzehn Avatar-Treffern, nur in die andere
    Richtung.

---

## Nachtrag: achtzehnte Prüfrunde

Vier Blocker, alle in den Gates der Vorrunde. Der schwerste ist der lehrreichste:

### Ein Gate, das in genau seinem eigenen Anlassfall abstürzt

Das Verwaisten-Gate aus Runde 17 ist für den Fall gebaut, dass ein Produkt aus
`products.json` entfernt wird. Genau dann fiel es aus: `gen_longtail.py` löst
`alternatives` über `by_slug[s]` auf, das Entfernen erzeugt einen `KeyError`, und ein
breites `except` um den gesamten Abschnitt 6c ersetzte **vierzig Prüfungen** durch eine
einzige Zeile — Zeichenvergleich aller 39 Generator-Seiten, Verwaisten-Gate und die
Zählung der handgepflegten Seiten, alles weg. **13 der 42 Produkte** sind als
Longtail-Alternative verdrahtet, es trifft also jedes dritte.

Drei Konsequenzen:
1. Der Generator stirbt nicht mehr an einem Datenfehler, er lässt die unbekannte
   Alternative weg. Ein Generator, der abbricht, nimmt jede Prüfung mit, die hinter ihm
   steht.
2. Der hängende Verweis wird von einem eigenen Gate gemeldet, wo er hingehört.
3. Das `except` sagt jetzt, **was** ausgefallen ist. Eine Meldung, die einen Abbruch
   zugibt, aber nicht benennt, welche vierzig Prüfungen damit entfielen, lädt dazu ein,
   den Rest des Laufs für aussagekräftig zu halten.

Der Test belegt beides: Statt eines Absturzes nennt der Lauf jetzt den hängenden Verweis
UND die verwaiste Seite.

### Wieder ein Proxy statt der Messung

`_gebaut` bildete die gen_pages-Hälfte aus dem Feld `detail` — einer Behauptung von
products.json. Der Generator verlangt zusätzlich einen `CONTENT`-Eintrag. Fehlt der,
baut **kein** Generator die Seite, sie fällt stumm aus dem Zeichenvergleich (39 → 28 in
der Probe), und das Gate schwieg, während seine Meldung wörtlich behauptete, genau das zu
prüfen. Jetzt aus `generierte_seiten()` beider Generatoren, also aus dem, was sie
liefern.

Das ist dieselbe Klasse wie in Runde 14 (Freigabeliste), 15 (Bindung an den Schema-Namen)
und 16 (String-Grep auf `@type`): **ein Stellvertreter, der leichter zu greifen ist als
die Sache selbst.**

### Mein `<`-Gate meldete korrektes Markup mit einer falschen Begründung

Drei Fehlalarme, alle auf `<` in Attributwerten (`alt="Gewicht < 200 g"`,
`onclick="if(a<b)go()"`). Mit `html.parser` nachgemessen: Alle drei bleiben vollständig
intakt. Die Meldung behauptete trotzdem "der Parser frisst alles bis zum nächsten >".
Dazu meldete der Zweig für das rohe `<` dieselbe Begründung, obwohl der eigene Kommentar
des Gates diese Klasse als harmlos bezeichnet.
Jetzt werden Attributwerte mit derselben Technik maskiert wie script und style, und die
beiden Klassen haben getrennte, zutreffende Begründungen. **16 von 16 Proben korrekt**,
gegen den echten Gate-Code ausgeführt, nicht gegen einen Nachbau.

### `detail` war nicht eindeutig

`slug` und `asin` werden seit Langem auf Doppelung geprüft, `detail` nicht — dabei ist es
seit Runde 16 die externe Identität, über die eine Seite ihrem Produkt zugeordnet wird.
Ein doppelter `detail` machte die Zuordnung mehrdeutig, und damit fielen die komplette
Bildprüfung und die Schema-Pflicht still aus. Der Lauf wurde zwar rot, aber über
Kollateralschaden an Preisen: **keine der 21 Meldungen nannte die Ursache.**

### Verify

Vier Blocker mit den exakten Szenarien des Prüfers rot bewiesen, dazu 16/16 Markup-Proben
und zwei Fehlalarm-Gegenproben. Acht Generatoren je zweimal, hash-identisch. Vier Gates
grün.

### Zusätzlich gelernt

76. **Ein Gate muss in seinem eigenen Anlassfall funktionieren.** Das Verwaisten-Gate
    stürzte genau dann ab, wenn ein Produkt entfernt wird — dem einzigen Fall, für den es
    existiert. Beim Bauen gehört der Anlassfall durchgespielt, nicht nur ein künstlicher
    Ersatz.

77. **Ein breites `except` um viele Prüfungen ist eine Abschaltung mit Alibi.** Es meldet
    etwas, verschweigt aber, was dadurch nicht gelaufen ist. Entweder der Geltungsbereich
    wird klein genug, dass der Ausfall offensichtlich ist, oder die Meldung zählt auf,
    was sie mitgerissen hat.

78. **Ein Generator, der an einem Datenfehler abbricht, nimmt jede Prüfung mit, die
    hinter ihm steht.** Datenfehler gehören gemeldet, nicht geworfen — das Melden ist
    Aufgabe des Gates, das Weiterlaufen Aufgabe des Generators.

79. **Eindeutigkeit prüft man für jedes Feld, das als Schlüssel benutzt wird.** `detail`
    wurde in Runde 16 zur Identität befördert, ohne die Prüfung mitzunehmen, die `slug`
    und `asin` längst hatten. Wer ein Feld zum Schlüssel macht, erbt dessen Pflichten.

---

## Nachtrag: die restlichen ungegateten Flächen (01.10.)

Nach der Freigabe die Liste aus der Landkarte abgearbeitet. Acht Flächen, zwei echte
Befunde darin, beide von mir selbst verursacht.

### Was gebaut wurde

**robots.txt inhaltlich.** Bis dahin wurde nur geprüft, DASS die Datei existiert. Ein
versehentliches `Disallow: /` hätte die komplette Domain aus dem Index genommen, und alle
vier Gates wären grün geblieben: der teuerste denkbare Fehler mit der billigsten
denkbaren Ursache. Geprüft werden jetzt: kein `Disallow: /` im Block für `User-agent: *`,
die `Sitemap:`-Zeile zeigt auf unsere Sitemap, und keine URL der Sitemap ist durch eine
Disallow-Regel gesperrt.

**Sitemap-Rückrichtung von `warn()` auf `err()`.** Eine indexierbare Seite, die nicht in
der Sitemap steht, wird schlechter gefunden. Vor der Verschärfung gemessen: 0 Seiten
betroffen.

**longtail.json als Struktur.** Zwei Gates lasen die Datei, aber nur als Zeichenkette.
Dass ein Pflichtfeld leer ist, zwei Einträge denselben Slug oder dasselbe Keyword tragen
oder ein Slug zugleich in products.json steht, hätte keins gemerkt — products.json hat
diese Prüfungen seit Langem.

**products.json gegen das Vokabular in produkte.js.** `platform` und `type` waren nur auf
Nicht-Leer geprüft, steuern im Browser aber Filterleiste und Label. Ein Wert, den
`PLAT_ORDER` nicht kennt, erzeugt gar keinen Filter-Chip. Und `platformLabel` ist nicht
frei wählbar, sondern genau das Label zu `platform`.

**Verwaiste Seiten im SEO-Sinn.** Die Rückrichtung war nur für `/produkte/` gegen die
Generatoren geprüft, nicht gegen die Verlinkung — und die ist es, die zählt.

**video gegen products.json.** `url` und `poster` waren auf Herkunft geprüft, aber nie
gegen den Datenkern; `duration` kam in keinem der vier Gates vor, wird aber sichtbar als
"Länge N Min." ausgespielt.

**Eine eigene 404-Seite**, die es vorher nicht gab (GitHub lieferte seine generische).

### Die zwei Befunde

**`viture-8bitdo` trug `platform: "universal"` und `platformLabel: "Android"`** — meine
eigene halbe Korrektur aus Runde 16. Damals habe ich das Label geändert, weil
`ALT_PLATFORM["Universal"]` zu "für Android & iPhone" wird und das dem Claim "Kein iOS"
widersprach. Den Schlüssel daneben habe ich stehen lassen.
Beim Nachsehen stellte sich auch meine damalige Annahme als falsch heraus: `worksOn:
universal` heißt nicht "läuft auf iPhone", sondern ist eine Kategoriezugehörigkeit — alle
18 Zubehörteile tragen sie. Richtig ist `platform: "android"`, weil die zwei Geschwister
mit identischem `worksOn` (8BitDo Ultimate 2C, GameSir X3 Pro) genau das tragen. Jetzt
angeglichen, und das neue Gate hält die Regel fest.

**`produkte/gamesir-g4s/` war verwaist.** Indexierbar, in der Sitemap, von keiner
einzigen Seite verlinkt. Die neun anderen Longtail-Datenblätter werden alle von einem
Marken-Hub verlinkt; im GameSir-Hub listet ein handgeschriebener Satz X2, X3 und T4 Pro,
der G4s fehlte. Ergänzt.

### Zwei Beinahe-Fehler beim Bauen

**Die erste Verlinkungsmessung meldete 19 Waisen.** Sie las nur das `nav`-Array aus
main.js, nicht die Links im Footer, der ebenfalls dort entsteht. Mit allen JS-Dateien
blieb genau eine übrig. Hätte ich die 19 übernommen, hätte ich 18 korrekt unverlinkte
Redirect-Stubs "repariert".

**Die 404-Seite rendete unformatiert.** Ich hatte `related-card` benutzt — eine Klasse,
die nur in einem Seiten-`<style>` von `gen_longtail.py` existiert, nicht in style.css.
Der Pattern-Katalog warnt davor seit Juli, und verify fängt ungestyltes Markup
ausdrücklich nicht. Gesehen habe ich es erst im Browser. Jetzt `cat-card`/`cat-grid` aus
style.css, plus eine Prüfung, dass keine Klasse der Seite ohne Stil dasteht.

Dazu: Die 404 erbte aus dem Kontakt-Gerüst einen BreadcrumbList, der einen Pfad
"Home > Rechtliches > Kontakt" behauptete, den es auf einer Fehlerseite nicht gibt.
Entfernt.

### Werkzeuge mitgezogen

`404.html` wäre die einzige ausgelieferte HTML-Datei ohne Gate gewesen: Alle drei
Werkzeuge globben `**/index.html`. `verify.py`, `sync_header.py` und
`bump_asset_version.py` nehmen sie jetzt mit — sonst hätte das Schließen einer
ungegateten Fläche eine neue geöffnet.
Das canonical-Gate gilt jetzt für **indexierbare** Seiten statt für alle: Eine 404 hat
keine eigene URL, sie antwortet unter jeder, ein Selbst-canonical wäre dort falsch. Das
ist eine Regel, keine Ausnahme für einen Einzelfall.

### Verify

Siebzehn Rot-Proben, alle bestanden: `Disallow: /` · fehlende Sitemap-Zeile · falsche
Sitemap-Zeile · robots sperrt eine Sitemap-URL · Seite fehlt in der Sitemap · leeres
Longtail-Feld · Slug doppelt · Keyword doppelt · Slug-Kollision mit products.json ·
platformLabel passt nicht zu platform · unbekanntes platform · unbekannter type ·
geschrumpftes JS-Vokabular · unverlinkte Seite · fremdes Video-Poster · fehlende
Videolänge · 404 im Browser gegengeprüft. Acht Generatoren über drei Durchläufe
hash-identisch, vier Gates grün.

### Zusätzlich gelernt

80. **Eine Datei, die nur auf Existenz geprüft wird, ist nicht geprüft.** `robots.txt`
    stand seit Juli in der Invariantenliste — als Dateiname. Ein `Disallow: /` darin wäre
    durch alle vier Gates gegangen.

81. **Wer eine ungegatete Fläche schließt, prüft zuerst, ob er dabei eine neue öffnet.**
    Die 404-Seite wäre die einzige ausgelieferte HTML ohne Gate gewesen, weil alle
    Werkzeuge `**/index.html` globben.

82. **Eine Messung, die 19 Treffer meldet, ist verdächtig, nicht alarmierend.** Zum
    zweiten Mal an zwei Tagen: Erst 19 angeblich leere Schwächen-Listen (falsche
    Anführungszeichen), jetzt 19 angebliche Waisen (nur das nav-Array gelesen, nicht den
    Footer). Beide Male hätte die ungeprüfte Übernahme korrekten Bestand zerstört.

---

## B1 umgesetzt: Kompatibilitäts-Antwort auf jeder Produktseite (01.10.)

Maßnahme 1 der Bücher-Synthese, Grundlage Jäckel und Sheridan: *"Kompatibilitäts-Antwort
auf jeder Produktseite ganz nach oben. Passt an: iPhone 15 und neuer, Android mit USB-C.
Passt nicht an: iPhone 14 und älter. Das ist die Frage, die Amazon offenlässt, und wir
beantworten sie derzeit weiter unten oder gar nicht."*

### Die Entscheidung, die alles andere bestimmt hat

42 handgepflegte Kompatibilitätsblöcke wären exakt die Sorte Text, die diese Session
reihenweise veraltet vorgefunden hat. Der Block wird deshalb **abgeleitet**, aus genau
zwei Feldern von products.json: `worksOn` und dem Spec-Feld `Verb.`.

Die einzige Schlussfolgerung, die der Code zieht, ist Gerätegeschichte und keine
Produktbehauptung: Das iPhone 15 ist das erste mit USB-C. Ein kabelgebundener
USB-C-Controller passt daher nicht an iPhone 14 und älter, ein Lightning-Controller nicht
an iPhone 15 und neuer. Dieselbe Herleitung steht seit Juli in den FAQ mehrerer
Review-Seiten.

### Was die Datenlage erzwungen hat

Sechs Controller hatten **kein** `Verb.`-Feld. Ohne Anschlussart lässt sich die
iPhone-Generation nicht ableiten. Alle sechs nennen die Verbindung auf ihrer **eigenen
Review-Seite** — die Information war da, nur nicht im Datenkern. Übernommen, wörtlich,
ohne etwas zu erfinden (§A5). Damit haben jetzt alle 28 Controller ein `Verb.`.

Dabei kam ein Fall heraus, den nichts prominent zeigte: **Der Backbone One PlayStation
Edition ist ein Lightning-Gerät.** Er passt an iPhone bis 14 und **nicht** an iPhone 15
und neuer — die Umkehrung des Normalfalls. Die Seite sagte das im Fließtext ("Passt nur
an iPhones bis Generation 14"), aber nicht dort, wo jemand es sucht.

Neun Zubehörteile bekommen **keinen** Block: Sie führen keine Maßangabe, und "passt an
alle Smartphones" wäre eine Behauptung ohne Beleg. Lieber kein Block als ein beliebiger.
Die fünf Trigger mit Maßangabe zeigen die Gehäusedicke, denn bei ihnen ist genau das die
Kompatibilitätsfrage.

### Zwei Wege, eine Quelle

Die 29 generierten `/produkte/`-Seiten bekommen den Block von `gen_pages.py`, die 13
handgepflegten Review-Seiten von `scripts/sync_kompat.py`. Beide ziehen Inhalt und
Escaping aus derselben Funktion (`scripts/kompat.py`) — nach drei Rissen zwischen zwei
Kopien derselben Regel an zwei Tagen war das keine Stilfrage mehr.

Für die generierten Seiten deckt der Zeichenvergleich alles ab. Für die handgepflegten
gibt es ein eigenes Gate: fehlender Block, abweichender Block und ein Block, den die
Daten nicht mehr hergeben, werden alle drei rot.

### Verify

Drei Rot-Proben bestanden (Block von Hand verfälscht · Block entfernt · `worksOn`
geändert ohne Nachziehen), `sync_kompat.py` über drei Läufe idempotent, neun Werkzeuge
hash-identisch, vier Gates grün. Im Browser auf beiden Seitentypen und auf 375 px
gegengeprüft, kein horizontaler Überlauf.

Abdeckung: 33 von 42 Produktseiten.

### Gelernt

83. **Eine Maßnahme aus einem Buch wird erst brauchbar, wenn man fragt, woher der Text
    kommt.** "Kompatibilitäts-Antwort nach oben" klingt nach Schreibarbeit. Als
    Datenableitung gebaut, kostet sie einmal Nachdenken und altert nie — als Handtext
    wäre sie in drei Monaten so falsch gewesen wie alles andere, was diese Session
    gefunden hat.

84. **Wo die Daten nichts hergeben, gehört kein Block hin.** Neun Zubehörteile bleiben
    ohne. Die Versuchung, die Lücke mit "passt an alle Smartphones" zu füllen, ist genau
    der Mechanismus, über den unbelegte Behauptungen entstehen.

85. **Eine fehlende Angabe im Datenkern kann auf der eigenen Seite längst stehen.** Sechs
    Controller hatten kein `Verb.`, alle sechs nannten die Verbindung in ihrer eigenen
    Spec-Tabelle. Bevor man eine Angabe als "nicht vorhanden" behandelt, sucht man sie
    dort, wo sie schon einmal veröffentlicht wurde.

---

## B4 umgesetzt: die Preisfrage offensiv beantwortet (01.10.)

Maßnahme 2 der Bücher-Synthese, Grundlage Sheridan: Der Preis ist das erste Thema, um
das Anbieter einen Bogen machen. Neue Seite `/blog/was-kostet-ein-handy-controller/`,
erzeugt von `scripts/gen_preisfrage.py`.

### Keine Zahl im Quelltext

Jede Zahl auf dieser Seite altert mit dem nächsten preis-loop. Von Hand geschrieben wäre
sie in drei Monaten falsch. Der Generator rechnet alles: Spanne, Median, Preisbänder,
Anzahl je Band, bestbewertetes Gerät je Band, Merkmalsgrenzen, Zubehörspannen, sogar die
Lesezeit aus der fertigen Wortzahl. Gegenprobe: Preis des 8BitDo auf 27 € gesetzt, einmal
generiert, die Zahl steht überall neu; zurückgesetzt, alles wieder bei 30 €.

### Was die Daten hergaben, und warum es unbequem ist

Der am besten bewertete Controller im Sortiment ist der **günstigste**: 8BitDo Ultimate 2C
für 30 €, 4,6 Sterne aus 2.188 Bewertungen, zugleich das meistbewertete Gerät. Das
teuerste Modell kostet 190 € und kommt auf 4,4 aus 459.

Das ist für eine Affiliate-Seite die unangenehmste Auskunft, die man geben kann, weil an
teuren Geräten mehr verdient wird. Es ist genau Sheridans Punkt: Wer die Preisfrage ehrlich
beantwortet, gewinnt das Vertrauen, das die Kaufentscheidung trägt.

Dazu die Merkmalsgrenzen, gerechnet statt behauptet:
- **Hall-Effect-Sticks** ab 30 € (5 Modelle, bis 80 €) — die Stick-Technik ist nicht das,
  wofür man mehr zahlt.
- **Kabellos** über die ganze Spanne von 30 bis 190 € (17 Modelle).
- **Tablet-Breite** erst ab 63 € (3 Modelle) — das ist eine echte Preisgrenze.

### Drei Dinge, die die Gates sofort verlangt haben

Die neue Seite war beim ersten Lauf dreifach rot, und jeder Fehler war berechtigt:
fehlender Sitemap-Eintrag, fehlende Pflichtangaben im Footer, kein einziger interner Link.
Genau die drei Dinge, die man bei einer neuen Seite vergisst. Das Waisen-Gate von heute
früh hat sich damit beim ersten echten Einsatz bewährt.

Dazu: Der Generator schrieb zunächst einen leeren Header und unversionierte Assets, weil
er nicht in den Nachzieh-Listen von `sync_header.py` und `bump_asset_version.py` stand.
Aufgenommen, jetzt erzeugt ein Alleinlauf einen grünen Stand.

### Abgrenzung statt Kannibalisierung

§B1 verlangt ein Keyword-Ziel pro Seite. Die Qualitätsfrage ("sind günstige gut?") bleibt
bei `/blog/guenstige-handy-controller/`, die transaktionale Liste bei
`/vergleich/beste-budget-controller/`. Die neue Seite nimmt nur die Budgetfrage und
verlinkt beide anderen als Antwort. In `keyword-strategie.md` dokumentiert.

### Kein erfundenes Bild

Für die Karte im Blog-Index gab es kein passendes Foto. Das Standard-OG-Bild ist ein
Marken-Banner mit eigener Headline und wäre in einer Liste von Artikelfotos ein
Fremdkörper gewesen; ein Produktfoto hätte eine Aussage gemacht, die der Artikel nicht
trifft. Die Karte trägt deshalb ein Icon auf Markenfläche. Ein echtes Key-Visual kann
nachgereicht werden.

### Verify

Zehn Werkzeuge über drei Durchläufe hash-identisch, vier Gates grün, im Browser
gegengeprüft. Selbstaktualisierung an einer Preisänderung bewiesen.

### Gelernt

86. **Die unbequeme Antwort ist die, die niemand sonst gibt.** Dass der bestbewertete
    Controller der günstigste ist, steht in unseren Daten seit dem Amazon-Abgleich. Keine
    Seite hat es ausgesprochen, weil die Rechnung niemand gemacht hat. Eine generierte
    Seite macht sie bei jedem Lauf neu.

87. **Eine neue Seite ist der ehrlichste Test für die Gates.** Sitemap, Pflichtangaben,
    interner Link, statischer Header, Assetversionen: fünf Dinge, die bei neuem Content
    typischerweise vergessen werden, und alle fünf wurden gemeldet statt übersehen.

88. **Wer einen Generator baut, trägt ihn in die Nachzieh-Listen ein.** Sonst erzeugt sein
    Alleinlauf einen roten Stand, und der nächste Durchgang sucht den Fehler in der Seite
    statt in der Kette.
