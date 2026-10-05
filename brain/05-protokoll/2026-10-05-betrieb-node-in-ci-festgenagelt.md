# 2026-10-05 · Betrieb · node in CI festgenagelt (Stopp-Punkt, von Yasin freigegeben)

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
