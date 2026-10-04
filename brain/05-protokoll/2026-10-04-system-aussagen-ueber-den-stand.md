# 2026-10-04 · System · Sechs falsche Aussagen über einen grünen Stand

## Was

Abschluss von B5. Der dreißigste Prüflauf hat sechs Blocker und sieben Hinweise gebracht,
und zum ersten Mal in dieser Serie saß **kein einziger im ausgelieferten Inhalt und keiner
in der Gate-Logik**. Alle sechs waren falsche Aussagen über einen Stand, der gemessen
richtig war: in Docstrings, in einer Überschrift, in der Constitution, im Protokoll.

Behoben:

| Befund | Wo | Falsch | Gemessen |
|---|---|---|---|
| Handgezählte Namensliste | `scripts/idempotenzprobe.py` Docstring | fünf Skripte außerhalb der Vorschrift, darunter `verify.py` | **neun**; `verify.py` hat gar keinen `__main__`-Guard und gehört nicht dazu; fünf fehlten |
| Beruhigender Nachsatz | dieselbe Stelle | "alle sind Prüfer oder Proben und schreiben nur in Kopien" | gilt für sieben von neun; `indexnow_ping.py` meldet an Bing, `md_to_pdf.py` schreibt ins Repo |
| Zwei Kopien divergent | `brain/CLAUDE.md`, `brain/INDEX.md` | P-1…P-8 | P-1…P-13 (Divergenz in diesem Paket selbst erzeugt, im HEAD waren beide `CLAUDE.md` bit-identisch) |
| Unmögliche Spanne | P-13 Überschrift | "Runden 17 bis 29, Nummern 10 bis 23" | 13 Runden gegen 14 Nummern; richtig 16 bis 30 / 10 bis 24 |
| Veraltete Spannen | `2026-10-02-…md` | "Prüfrunden 18 bis 28", "21 bis 28" | beide Falltabellen tragen R29-Fälle (4 Marker in `css_kaskade.py`, 2 in `finder_batterie.py`) |
| Produktzahl | `SPC-CONSTITUTION.md` §A1 | 40 Produkte | **42** (§A6 derselben Datei nannte schon 42) |
| Aufzählung statt Eigenschaft | `produktdaten.preis_zahl()` GRENZE | "die einzigen Punkte stehen in 'ca. 40 €'" | 7 der 42 Preise tragen einen Punkt, in 6 Schreibweisen; keiner ist ein Tausenderpunkt |
| Rest-Fragment | P-13 Mechanismus 19 | Zahlen-Nachsatz zweimal im Punkt, sich widersprechend | entfernt |
| Startzahl | `robustheitsprobe.py` Docstring | "startet verify.py 117 Mal" | 118 (117 Defektformen plus Schlusslauf); gibt jetzt der Lauf aus |

Als benannte Grenze stehen geblieben, nicht weggebaut: `_argument()` in `css_kaskade.py`
überspringt keine Anführungszeichen und keine `[…]`, also schließt das `)` in
`:not([data-x=")"])` das Argument zu früh. Gemessen in den ausgelieferten CSS-Quellen: 72
Quellen, 2989 Selektoren, 9 mit Funktions-Pseudoklasse (alle `:nth-child(even)`), **0** mit
Anführungszeichen oder `[` im Argument. Steht mit der Null in der GRENZEN-Liste.

## Wie

Zwei neue Gates in `verify.py`, beide in beide Richtungen nachgemessen:

- **Die zwei `CLAUDE.md`-Kopien müssen identisch bleiben.** Rot mit dem Diff in der
  Meldung. Die Antwort auf diese Klasse stand schon im Repo (`sync_footer.py --check`,
  "bevor die fünfte Kopie entsteht"), vier Commits vorher, für den Pflicht-Footer.
- **Kein Preis darf einen Tausenderpunkt tragen.** Sonst rechnen zwei Leser desselben
  Feldes still verschieden: `produktdaten.preis_zahl()` liest "1.299 €" als 1299,
  `gen_preisfrage.preis()` als 1. Der Kommentar beschrieb diesen Unterschied als "heute
  kein Problem"; jetzt macht der erste vierstellige Preis den Lauf rot und nennt den Fix
  (beide Stellen auf `preis_zahl()` ziehen, §A1).

Statt der Namensliste gibt `idempotenzprobe.py` die Menge jetzt aus: `ausserhalb()` leitet
sie ab (ausführbar heißt `__main__`-Guard, außerhalb heißt `_schreiber()` ist falsch) und
nennt je Name den Weg nach außen. `robustheitsprobe.py` gibt die Zahl der verify.py-Starts
aus statt sie im Docstring zu führen.

## Warum so

Die Lehre dieser ganzen Serie war "keine Zahl ohne Messvorschrift". Runde 30 zeigt, dass
eine **Namensliste** derselbe Fehler ist, nur schwerer zu bemerken: Eine Zahl merkt man an,
eine Liste liest sich wie ein Beweis. Und sie zeigt, dass ein **beruhigender Nachsatz** eine
Behauptung ist. "Alle sind harmlose Prüfer" galt für sieben von neun, und die zwei
Ausnahmen waren genau die, die nach außen wirken -- eine davon der Grund, aus dem die
Sperre in dieser Datei überhaupt existiert.

Die `CLAUDE.md`-Divergenz habe ich selbst erzeugt, vier Commits nach derselben Klasse beim
Footer. Deshalb ein Gate statt eines Vorsatzes: Wer eine zweite Kopie duldet, baut im
selben Schritt den Vergleich.

Die Spannen-Befunde sind die billigsten überhaupt -- "14 Nummern aus 13 Runden" braucht
keine Projektkenntnis -- und deshalb die, die nicht stehen bleiben dürfen.

## Verify

- Neun Gates, jedes Exit 0: `verify.py` · `audit_prosa.py` ·
  `sync_product_values.py --audit` · `sync_footer.py --check` · `sync_lesezeit.py --check` ·
  `sync_kompat.py --check` · `css_kaskade.py` · `gen_preisfrage.py --check` ·
  `gen_brand_sections.py --check`
- Rot/grün je neues Gate: Preis auf "ca. 1.299 €" → rot mit Nennung beider Leser;
  `brain/CLAUDE.md` auf P-1…P-8 zurückgedreht → rot mit Diff; unverändert → grün
- Reinraum (305 Dateien, frisch aus `git ls-files`, ohne `.git`): **GRÜN, 0 Fehler, 0
  Warnungen**, 127 Seiten · 250 JSON-LD-Blöcke · 42 Produkte
- Ohne `node` im PATH (eigenes `bin` mit Symlink auf python3, damit NUR node fehlt):
  **Exit 0 mit sichtbarer Warnung**
- Nicht-Objekt-Eintrag in products.json: Lauf endet rot (283 Fehler), **kein Abbruch**;
  der einzige Traceback in der Ausgabe ist der bekannte, absichtlich GEMELDETE Abbruch von
  `gen_brand_sections.py`
- `robustheitsprobe.py`, `finder_batterie.py`, `idempotenzprobe.py`: siehe Lauf dieses
  Datums, je 0 Befunde
- Runden-Zählung nach eigener Vorschrift:
  `grep -cE '^#+.*(Prüfung zu B5|Nachprüfung zu B5|Prüflauf zu B5)'` → **30**
- P-13: 24 numerierte Mechanismen, Überschrift "Vierundzwanzig", Spanne 16 bis 30 /
  10 bis 24 (fünfzehn gegen fünfzehn), Katalog v4.5, Marker in `INDEX.md` mitgezogen

## Gelernt

Lehren 233 bis 238 stehen in `2026-09-30-prosa-und-generatorquelle.md`, P-13 Mechanismus 24
fasst sie als Bau-Regel. Kurz:

1. Eine Namensliste ohne Messvorschrift ist derselbe Fehler wie eine Zahl ohne.
2. Ein beruhigender Nachsatz ist eine Behauptung und wird mitgeprüft.
3. Zwei Kopien derselben Datei brauchen ein Gate, nicht Disziplin.
4. Was sich ohne Projektkenntnis nachrechnen lässt, rechnet der Prüfer nach.
5. Eine Aufzählung behauptet Vollständigkeit, eine Eigenschaft nicht -- ist die
   Eigenschaft gemeint, gehört sie ins Gate.
6. Ein Test, der die Umgebung beschneidet, beschneidet mehr als gedacht: Mein erster
   node-loser Lauf tauschte über `PATH=/usr/bin:/bin` auch Python 3.14 gegen 3.9 und wurde
   an einem SyntaxError rot, nicht am fehlenden `node`.

## Offen für Yasin · Stopp-Punkt `.github/workflows/`

Gemessen und berichtet, nicht geändert:

1. Der Workflow fährt **drei** Gates, das Repo hat **neun** mit Exit 0/1. Nicht in CI:
   `sync_footer.py --check`, `sync_lesezeit.py --check`, `sync_kompat.py --check`,
   `css_kaskade.py`, `gen_preisfrage.py --check`, `gen_brand_sections.py --check`. Ein
   Push, der eines davon bricht, deployt grün.
2. `node` kommt im Workflow nicht vor. Die `ubuntu-latest`-Images bringen Node mit, das
   §A6-Gate läuft dort also voraussichtlich -- aber nichts fixiert und nichts prüft das.
   Fällt Node aus dem Image, wird aus dem stärksten §A6-Gate eine Warnung bei Exit 0.
3. Der Kommentar über `python-version: '3.12'` sagt "Geprueft: die Skripte nutzen keine
   Konstrukte oberhalb von 3.9, die Festlegung dient nur der Reproduzierbarkeit". Falsch:
   `gen_brand_sections.py:200` hat einen Backslash im Ausdrucksteil eines f-Strings und ist
   unter Python 3.9 nicht parsebar (gemessen mit 3.9.6; die anderen 26 Skripte parsen). Die
   3.12 ist tragend, nicht kosmetisch. Dieselbe Zeile sagt "Alle drei Gates brauchen nur
   die Standardbibliothek" -- für Python stimmt das, aber das stärkste §A6-Gate braucht die
   `node`-Binärdatei.

## Beobachtung ohne Befundcharakter

Ein einziger Nicht-Objekt-Eintrag in products.json lässt den `try`-Block um die
Produkt-Invarianten fliegen, und `items` wird auf `[]` gesetzt. Alle nachgelagerten
Produkt-Gates laufen dann gegen eine leere Liste. Der Lauf wird trotzdem rot (gemessen: 283
Fehler), aber über Kollateralschaden statt über die Ursache -- dieselbe Form wie der
`detail`-Doppler vom 30.09. Kein Risiko für Live, weil rot rot bleibt; die Meldung nennt
nur die Ursache nicht.
