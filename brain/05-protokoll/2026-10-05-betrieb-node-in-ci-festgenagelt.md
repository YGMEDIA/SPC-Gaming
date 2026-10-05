# 2026-10-05 · Betrieb · Die vier Workflow-Punkte (Stopp-Punkt, von Yasin freigegeben)

> Dieser Eintrag beschreibt Punkt 2 (node). Die drei übrigen kamen am selben Tag dazu und
> stehen am Ende: vier Gates, die nirgends in CI liefen · fünf Actions auf Node-20-Pfad ·
> ein falscher Kommentar über die Python-Version.

## Was

`.github/workflows/` ist einer der drei Stopp-Punkte aus CLAUDE.md: melden statt ändern.
Punkt 2 der drei gemeldeten Befunde hat Yasin am 05.10. freigegeben, die anderen zwei
bleiben gemeldet.

**Der Befund:** `node` kam im Workflow nirgends vor. Es war einfach im
`ubuntu-latest`-Image vorhanden, und `verify.py` benutzt es für den stärksten §A6-Test:
Es führt `assets/js/finder.js` tatsächlich aus und prüft, ob der Finder Produkte unter der
3,8-Schwelle wirklich herausfiltert.

**Warum das dringend war:** GitHub warnt im Lauf selbst, dass `ubuntu-latest` **ab dem
19.10.2026 auf Ubuntu 26 wechselt**. Fällt node dabei aus dem Image, passiert nichts
Lautes.

## Die Messung

Lokal mit einem PATH ohne node, aber mit demselben Python:

```
$ env PATH="$NUR_PYTHON:/usr/bin:/bin" python3 scripts/verify.py
  WARN  §A6: node fehlt — der Finder wurde NICHT ausgefuehrt. …
✅ GRÜN — 0 Fehler, 1 Warnungen
EXIT=0
```

**Exit 0.** Der Deploy wäre also grün durchgelaufen, während der §A6-Finder-Test
übersprungen wird. Die Warnung steht im Log, aber ein Log liest niemand, wenn der Haken
grün ist.

*(Nebenbei beim Messen: Ein erster Versuch mit `PATH="/usr/bin:/bin"` machte verify ROT —
aber aus einem anderen Grund, weil damit auch das Homebrew-Python verschwand und das
System-Python 3.9 `gen_brand_sections.py` nicht parsen kann. Das ist Punkt 3 der
Workflow-Befunde, nicht dieser hier. Eine Messung, die zwei Dinge gleichzeitig ändert,
misst keines von beiden.)*

## Wie

Zwei Zeilen Absicherung, nicht eine:

1. **`actions/setup-node@v4` mit `node-version: '22'`.** Node ist damit angefordert und
   auf eine Hauptversion festgelegt, statt aus dem Image zu fallen.
2. **Der verify-Schritt fällt, wenn die Warnung im Lauf steht.** Ohne das könnte ein
   späterer Umbau den node-Schritt entfernen, ohne dass irgendetwas rot wird — dieselbe
   Klasse wie ein gelöschtes Gate, das stumm grün bleibt (das ist in diesem Repo zuletzt
   bei B12 passiert, und davor zweimal beim Finder-§A6-Gate).

```yaml
      - name: verify.py
        run: |
          set -o pipefail
          python3 scripts/verify.py 2>&1 | tee "$RUNNER_TEMP/verify.log"
          if grep -q 'node fehlt' "$RUNNER_TEMP/verify.log"; then
            echo "::error::verify.py lief ohne node — der §A6-Finder-Test wurde uebersprungen …"
            exit 1
          fi
```

`set -o pipefail` steht da, weil hinter einer Pipe sonst der Exit-Code von `tee` zählt.
Genau diese Falle hat mich in dieser Session schon einmal einen Batterie-Lauf mit
17 falschen Fällen als „exit 0" lesen lassen.

## Verify

- Die Shell-Logik lokal nachgespielt: `grep` trifft bei vorhandener Warnung und trifft
  nicht ohne sie; `set -o pipefail` reicht Exit 3 durch `tee` durch
- Workflow-Struktur ausgezählt: 6 Schritte im verify-Job, drei Actions
  (checkout@v4, setup-python@v5, setup-node@v4), keine Tabs, kein CRLF
- **Vierzehn Gates lokal exit 0** vor dem Push
- **Der CI-Lauf 37357463288 belegt es:** `actions/setup-node@v4` lief mit
  `node-version: 22`, node kam aus dem Cache (`/opt/hostedtoolcache/node/22.23.3/x64`),
  und `verify.py` meldet **„0 Fehler, 0 Warnungen"** — die Warnung „node fehlt" steht
  also nicht im Lauf, der §A6-Finder-Test ist wirklich gelaufen. Lauf grün.
- **Nicht bewiesen, und das gehört dazu:** Dass der neue `grep`-Riegel in CI *greift*,
  ist lokal nachgespielt, aber nicht im echten Lauf ausgelöst worden — dafür müsste man
  node im Runner entfernen. Die Shell-Logik ist dieselbe, der Beweis ist einer aus zweiter
  Hand.

**Neuer Befund aus demselben Lauf (gemeldet, nicht geändert):** GitHub warnt am Ende des
Jobs: *„Node.js 20 is deprecated. The following actions target Node.js 20 but are being
forced to run on Node.js 24: actions/checkout@v4, actions/setup-node@v4,
actions/setup-python@v5."* Das betrifft die Laufzeit der Actions selbst, nicht unser
node 22. Es läuft heute, aber die drei Actions stehen auf einem Auslaufpfad. Das ist ein
vierter Workflow-Punkt für Yasin.

## Gelernt

1. **Eine Abhängigkeit, die niemand angefordert hat, ist keine Zusage, sondern ein
   Zufall.** Node lief seit dem ersten CI-Tag mit, weil es zufällig im Image lag. Das
   fällt erst auf, wenn das Image wechselt, und dann fällt es leise aus.
2. **Eine Warnung bei Exit 0 ist in CI dasselbe wie Schweigen.** Der Mensch sieht einen
   grünen Haken. Wenn eine Warnung etwas bedeutet, das den Lauf wertlos macht, muss sie
   den Lauf anhalten — an der Stelle, an der sie gemeint ist, nicht in verify.py selbst:
   Dort bleibt sie richtig, weil node lokal fehlen darf.
3. **Ein Stopp-Punkt ist keine Sperre, sondern eine Frage.** Der Befund lag seit dem
   01.10. gemessen und begründet in STATUS; die Freigabe kam in einem Satz, und die
   Umsetzung hat zwanzig Minuten gedauert. Was es gebraucht hat, war die Messung, nicht
   die Erlaubnis.

---

# Nachtrag: die drei übrigen Workflow-Punkte (05.10., ebenfalls freigegeben)

## Punkt 1 · Vier Gates liefen nirgends in CI

Von den vierzehn Gates fuhren drei als eigener Schritt und sieben als Unter-Gate über
`verify.py` mit. **Vier liefen nur auf Yasins Rechner:** `sync_footer.py --check`,
`sync_lesezeit.py --check`, `sync_kompat.py --check`, `css_kaskade.py`. Ein Push, der
eines davon bricht, deployte grün — zum Beispiel ein Footer, der auf 16 Seiten
auseinanderläuft, oder eine Lesezeit, die nach einem Textausbau nicht mehr stimmt.

Gemessen kosten die vier zusammen **1,6 Sekunden** (1,4 davon `sync_footer`). Es war nie
die Laufzeit, es war schlicht nie eingetragen.

**Beleg aus Lauf 37358684541:** alle vier Schritte im Log, jeder mit seiner eigenen
Ausgabe (`0 Datei(en) waeren geaendert` · `0 Abweichung(en)` · `0 Datei(en)` ·
`39 Selektor-Faelle + 42 Kaskaden-Faelle, 0 falsch`).

## Punkt 3 · Fünf Actions auf dem Node-20-Pfad

GitHub warnte in **beiden** Jobs: „Node.js 20 is deprecated … forced to run on Node.js
24" — im Gate-Job `checkout@v4`, `setup-node@v4`, `setup-python@v5`, im Deploy-Job
`checkout@v4`, `deploy-pages@v4` und das intern benutzte `upload-artifact@v4`.

Jede Action um **eine** Hauptversion, nicht auf die neueste: checkout v4→v5,
setup-python v5→v6, setup-node v4→v5, upload-pages-artifact v3→**v5**, deploy-pages
v4→v5. Das räumt die Warnung weg und hält die Menge der Verhaltensänderungen klein.

**Geprüft am Verhalten, nicht am Namen:** `runs.using` in der jeweiligen `action.yml` am
gewählten Tag abgefragt. Vier laufen auf `node24`. `upload-pages-artifact` ist ein
Composite — und dessen **v4 pinnt intern `upload-artifact@v4.6.2`**, hätte die Warnung
also stehen lassen; erst v5 zieht auf v7.0.0. Ohne diese Abfrage wäre der Punkt mit einer
Versionsnummer „erledigt" gewesen, die nichts ändert.

**Beleg aus Lauf 37359174321: null Deprecation-Warnungen**, beide Jobs grün, Site live
(HTTP 200, Stichprobe auf einer Produktseite).

## Punkt 4 · Der Kommentar über die Python-Version war falsch

Er sagte: „Geprueft: die Skripte nutzen keine Konstrukte oberhalb von 3.9, die Festlegung
dient nur der Reproduzierbarkeit."

Gemessen mit 3.9.6: **37 der 38 Skripte parsen, `gen_brand_sections.py` nicht.** Zeile 200
hat einen Backslash im Ausdrucksteil eines f-Strings, und das erlaubt erst PEP 701 ab
3.12. `verify.py` startet diese Datei als Unter-Gate. Die 3.12 ist also **tragend**, nicht
kosmetisch — der Kommentar sagt das jetzt samt Begründung.

## Gelernt (aus allen vieren)

4. **Eine Versionsnummer ist kein Verhalten.** Der Sprung auf `upload-pages-artifact@v4`
   hätte den Punkt abgehakt und die Warnung dagelassen, weil die Abhängigkeit eine Ebene
   tiefer steckt. Gefragt werden muss die `action.yml`, nicht der Tag.
5. **Vier Gates fehlten nicht aus einem Grund, sondern aus keinem.** Sie sind nach dem
   CI-Aufbau entstanden und wurden nie nachgetragen. Die Liste der Gates und die Liste
   der CI-Schritte waren zwei Listen, und zwei Listen laufen auseinander — deshalb nennt
   der Kommentar im Workflow jetzt die Gesamtzahl und sagt, wo die übrigen laufen.
6. **Ein falscher Kommentar ist eine Falle mit Verfallsdatum.** „Nutzt nichts oberhalb von
   3.9" hätte beim nächsten Aufräumen jemanden dazu gebracht, die Version zu senken, und
   das Marken-Gate wäre mit einem Parse-Fehler gestorben — in CI, nach dem Merge.
