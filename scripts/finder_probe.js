/* Fuehrt assets/js/finder.js gegen die WIRKLICHE Struktur von controller-finder/index.html
 * aus und berichtet, was dabei herauskommt.
 *
 * Vorgeschichte, weil sie die Bauform erklaert: Der Vertrag zwischen Seite und Skript war
 * drei Pruefrunden lang eine Sammlung von Mustern ueber Markup, und jede Runde fand eine
 * Nachbarform, die durchlief, waehrend der Finder auf der Seite tot war -- Element
 * umbenannt, Script-Tag auskommentiert, in <noscript> gewickelt, `data-step` am falschen
 * Element, `data-step` gedoppelt, Klasse mit Suffix umbenannt, Script-Tag in den <head>
 * ohne `defer`, Startzustand `is-active` entfernt. Ein Vertrag zwischen zwei Dateien laesst
 * sich nicht durch Suchen nach Schreibweisen pruefen.
 *
 * Die erste Fassung dieses Harness baute ihr DOM SELBST, aus Zahlen, die verify.py aus der
 * Seite gelesen hatte. Sie bewies damit etwas ueber finder.js im Leerlauf und nichts ueber
 * die Seite: mit entferntem `id="finder"` meldete sie weiter 36 Kombinationen und 16 Slugs.
 * Jetzt kommt der Baum aus scripts/dom_baum.py, geparst aus der echten Datei.
 *
 * Eingabe (stdin, JSON): { dom, produkte? }
 *   dom       der Baum der Seite (scripts/dom_baum.py)
 *   produkte  ersetzt products.json fuer diesen Lauf; verify.py nutzt das fuer die
 *             Gegenprobe (nur Modelle unter der Schwelle -> der Finder darf nichts
 *             empfehlen). Ohne diese Probe beweist der Filter nichts, weil die Rangfolge
 *             das schwache Modell ohnehin aus den Top 3 haelt.
 * Ausgabe (stdout, JSON): siehe `bericht` unten, oder { fehler }
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.dirname(path.dirname(path.resolve(__filename)));
// Nicht verdrahtet: R22 hat `is-active` in JS, CSS und Markup sauber umbenannt, verify
// leitet den Namen aus `classList.toggle(...)` ab -- der Harness hatte ihn fest, also vier
// Fehler mit erfundener Ursache ("der Leser sieht keine Frage"). Halb abgeleitet, halb
// verdrahtet ist die schlechteste Mischung.
let AKTIV = 'is-active';

/* ---------- Minimal-DOM ueber dem geparsten Baum ---------- */

function Knoten(roh, eltern) {
  const el = {
    tag: roh.tag,
    attrs: Object.assign({}, roh.attrs),
    eltern: eltern || null,
    kinder: [],
    eigenerText: roh.text || '',
    _html: null,
    _handler: {},
  };
  el.kinder = (roh.children || []).map(k => Knoten(k, el));

  Object.defineProperty(el, 'classList', {
    value: {
      _liste: () => (el.attrs.class || '').split(/\s+/).filter(Boolean),
      _setze(l) { el.attrs.class = l.join(' '); },
      contains(n) { return this._liste().includes(n); },
      add(n) { const l = this._liste(); if (!l.includes(n)) { l.push(n); this._setze(l); } },
      remove(n) { this._setze(this._liste().filter(x => x !== n)); },
      toggle(n, an) {
        const soll = an === undefined ? !this.contains(n) : !!an;
        if (soll) this.add(n); else this.remove(n);
      },
    },
  });

  Object.defineProperty(el, 'dataset', {
    get() {
      // data-foo-bar -> fooBar, genau wie im Browser. Fehlt das Attribut, ist der Wert
      // undefined -- und genau das ist der Schaden, den Runde 20 gezeigt hat:
      // `+undefined === n` ist fuer jeden Schritt falsch.
      const d = {};
      for (const k of Object.keys(el.attrs)) {
        if (k.startsWith('data-')) {
          d[k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = el.attrs[k];
        }
      }
      return d;
    },
  });

  Object.defineProperty(el, 'textContent', {
    get() {
      if (el._html !== null) return el._html.replace(/<[^>]*>/g, '');
      return el.eigenerText + el.kinder.map(k => k.textContent).join('');
    },
    set(v) { el._html = String(v); el.kinder = []; el.eigenerText = String(v); },
  });

  Object.defineProperty(el, 'innerHTML', {
    get() { return el._html === null ? '' : el._html; },
    set(v) { el._html = String(v); },
  });

  // ABWEICHUNG VOM BROWSER, benannt statt verschwiegen: Der Browser registriert mehrere
  // Handler je Ereignis, hier gewinnt der letzte. finder.js legt nie zwei auf dasselbe
  // Element, also heute ohne Unterschied -- aber es ist eine Abweichung.
  el.addEventListener = (ev, fn) => { el._handler[ev] = fn; };

  // Ein Klick erreicht ein deaktiviertes Element NICHT. Die erste Fassung rief den
  // Handler direkt auf: `disabled` an den Antwort-Knoepfen liess die Probe 36
  // Kombinationen und 3 Karten melden, waehrend der Leser den Finder nicht starten
  // konnte (R21, im Browser gegengemessen). Gilt auch fuer <fieldset disabled>.
  el.istDeaktiviert = () => {
    for (let k = el; k; k = k.eltern) {
      if (Object.prototype.hasOwnProperty.call(k.attrs, 'disabled')
          && (k === el || k.tag === 'fieldset')) return true;
    }
    return false;
  };
  // Unsichtbar ohne Stylesheet: diese drei stehen im Baum und brauchen keinen
  // CSS-Interpreter. `hidden`, inline `display:none`/`visibility:hidden`, `aria-hidden`.
  el.istVersteckt = () => {
    for (let k = el; k; k = k.eltern) {
      if (Object.prototype.hasOwnProperty.call(k.attrs, 'hidden')) return 'hidden-Attribut';
      if (/(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)/i.test(k.attrs.style || '')) {
        return 'style="' + (k.attrs.style || '').slice(0, 40) + '"';
      }
      if ((k.attrs['aria-hidden'] || '').toLowerCase() === 'true') return 'aria-hidden';
    }
    return null;
  };
  el.scrollIntoView = () => {};
  el.querySelectorAll = (sel) => alleTreffer(el, sel);
  el.querySelector = (sel) => alleTreffer(el, sel)[0] || null;
  return el;
}

function* nachkommen(el) {
  for (const k of el.kinder) { yield k; yield* nachkommen(k); }
}

function passt(el, sel) {
  let m;
  if ((m = /^\.([\w-]+)$/.exec(sel))) {
    // Als TOKEN, nicht als Teilstring: `finder-step-alt` ist nicht `finder-step`.
    return (el.attrs.class || '').split(/\s+/).includes(m[1]);
  }
  if ((m = /^#([\w-]+)$/.exec(sel))) return el.attrs.id === m[1];
  if ((m = /^\[([\w-]+)\]$/.exec(sel))) return Object.prototype.hasOwnProperty.call(el.attrs, m[1]);
  if ((m = /^([a-zA-Z][\w-]*)$/.exec(sel))) return el.tag === m[1].toLowerCase();
  return false;
}

function alleTreffer(el, sel) {
  const aus = [];
  for (const k of nachkommen(el)) if (passt(k, sel)) aus.push(k);
  return aus;
}

/* ---------- Lauf ---------- */

async function main(eingabe) {
  if (!eingabe.dom) return { fehler: 'kein DOM uebergeben' };
  // Der Pfad kommt aus finder.js, nicht aus diesem Skript: Ein Zeiger auf eine ANDERE
  // vorhandene JSON-Datei lief vorher durch, weil verify nur os.path.exists prueft und der
  // Stub die URL ignorierte. Der Finder zeigte dann fuer jede Kombination dauerhaft
  // "Keine perfekte Uebereinstimmung" (R21, im Browser gegengemessen).
  const quelle_roh = fs.readFileSync(path.join(ROOT, 'assets/js/finder.js'), 'utf8');
  const am = /classList\.toggle\(\s*['"]([\w-]+)['"]/.exec(quelle_roh);
  if (am) AKTIV = am[1];
  const fm = /fetch\(\s*['"](\/[^'"]+)['"]/.exec(quelle_roh);
  const datenpfad = fm ? fm[1].replace(/^\//, '') : 'assets/data/products.json';
  let produkte;
  if (eingabe.produkte) {
    produkte = eingabe.produkte;
  } else {
    try {
      produkte = JSON.parse(fs.readFileSync(path.join(ROOT, datenpfad), 'utf8'));
    } catch (e) {
      produkte = [];
    }
  }

  const wurzel = Knoten(eingabe.dom, null);
  const nachId = new Map();
  for (const k of nachkommen(wurzel)) if (k.attrs.id) {
    if (!nachId.has(k.attrs.id)) nachId.set(k.attrs.id, k);
  }
  const document = { getElementById: (id) => nachId.get(id) || null };
  const window = { dataLayer: [] };
  const fetch = () => Promise.resolve({ json: () => Promise.resolve(produkte) });

  let startfehler = null;
  try {
    new Function('document', 'window', 'fetch', quelle_roh)(document, window, fetch);
  } catch (e) {
    // Ein Absturz beim Start IST ein Befund und kein Grund, die Probe zu beenden.
    startfehler = String((e && e.message) || e);
  }
  await new Promise(r => setImmediate(r));

  const finder = nachId.get('finder');
  if (!finder) {
    return { startfehler, kein_finder: true, schritte: 0, kombis: 0, slugs: [],
             max_karten: 0, aktiv_start: [], aktiv_nach_klicks: [], titel: [],
             step_werte: [], antworten: [] };
  }
  const schritte = alleTreffer(finder, '.finder-step');
  const ergebnis = alleTreffer(finder, '.finder-result')[0] || null;
  const knoepfe = alleTreffer(finder, '.finder-opt');
  const fortschritt = alleTreffer(finder, '.fp-step');
  const zurueck = alleTreffer(finder, '[data-back]');
  const grid = nachId.get('finderMatches');
  const titelEl = nachId.get('finderResultTitle');
  const neustart = nachId.get('finderRestart');

  const aktive = () => schritte.map((s, i) => (s.classList.contains(AKTIV) ? i : -1))
    .filter(i => i >= 0);
  const aktiv_start = aktive();
  const step_werte = schritte.map(s => (s.dataset.step === undefined ? null : s.dataset.step));

  // Die Gruppen entstehen JE SCHRITT, nicht aus der Dokumentreihenfolge der Schluessel.
  // R21: Vertauscht man die beiden Antwortgruppen von Schritt 2 und 3, steht die
  // Budget-Ueberschrift ueber den Prioritaets-Antworten -- alle Zustaende blieben korrekt,
  // weil die Gruppen nur nach Schluessel gebildet wurden und der Schritt keine Rolle
  // spielte. Jetzt berichtet die Probe, welcher Schluessel in welchem Schritt liegt.
  const fragen = schritte.map(s => alleTreffer(s, '.finder-opt'));
  const keys_je_schritt = fragen.map(g => [...new Set(g.map(b => b.dataset.key))]);

  // Die Klassenketten vom jeweiligen Element bis zu #finder. verify prueft damit die
  // CSS-Kaskade fuer JEDE Klasse auf dem Weg, nicht nur fuer zwei verdrahtete Namen:
  // R22 hat `.finder-options{display:none}` und `.finder{display:none}` ans Ende von
  // style.css gehaengt -- gleiche Schadensform, Nachbarelement, Lauf gruen.
  // Welche Elemente finder.js UMSCHALTET, gemessen statt geraten: die Sammlungen, auf
  // denen show() die aktive Klasse setzt. Ein Vorfahr aus dieser Menge darf im
  // Ruhezustand `display:none` tragen -- das ist der korrekte Zustand, kein Defekt. Ohne
  // diese Unterscheidung meldete das Gate die Antwort-Knoepfe von Schritt 2 und 3 als
  // "per CSS versteckt", und das waere ein Fehlalarm auf dem richtigen Markup gewesen.
  const umgeschaltet = new Set([...schritte, ...fortschritt, ...(ergebnis ? [ergebnis] : [])]);
  const kette = (el) => {
    const aus = [];
    for (let k = el; k; k = k.eltern) {
      // Attribute kommen mit: Ohne sie konnte die CSS-Pruefung Verbundgruppen mit
      // Attribut-Selektor nicht bewerten und uebersprang sie. R24 hat gezeigt, dass
      // `.finder-step[data-step]{display:none}` den Finder toetet (gleiche Spezifitaet
      // wie `.finder-step.is-active`, spaeter in der Quelle) -- und dass diese
      // Schreibweise in style.css Hausbrauch ist (9 Vorkommen).
      aus.push({ c: (k.attrs.class || '').split(/\s+/).filter(Boolean),
                 id: k.attrs.id || null, tag: k.tag, a: Object.assign({}, k.attrs),
                 u: umgeschaltet.has(k) });
      if (k === finder) break;
    }
    return aus;   // [0] ist das Element selbst, danach die Vorfahren bis #finder
  };
  const bericht = {
    startfehler,
    aktiv_klasse: AKTIV,
    ketten: {
      finder: kette(finder),
      schritte: schritte.map(kette),
      ergebnis: ergebnis ? kette(ergebnis) : null,
      knoepfe: knoepfe.map(kette),
    },
    // Beschriftung je Antwort-Knopf, fuer den Abgleich mit data-value: R22 hat
    // data-value ios/android vertauscht, Beschriftungen unveraendert -- ein Leser mit
    // iPhone drueckte "iPhone" und bekam die Android-Auswahl, Lauf gruen.
    optionen: knoepfe.map(b => ({ key: b.dataset.key, value: b.dataset.value,
                                  text: b.textContent.replace(/\s+/g, ' ').trim() })),
    schritte: schritte.length,
    hat_ergebnis: !!ergebnis,
    hat_grid: !!grid,
    hat_titel: !!titelEl,
    hat_neustart: !!neustart,
    knoepfe: knoepfe.length,
    knoepfe_in_schritten: fragen.reduce((n, g) => n + g.length, 0),
    zurueck: zurueck.length,
    zurueck_mit_handler: 0,
    zurueck_wirkt: null,
    knoepfe_ohne_key: knoepfe.filter(b => b.dataset.key === undefined
                                       || b.dataset.value === undefined).length,
    fragen: fragen.length,
    keys_je_schritt,
    knoepfe_deaktiviert: knoepfe.filter(b => b.istDeaktiviert()).length,
    finder_versteckt: finder.istVersteckt(),
    schritte_versteckt: schritte.map(s => s.istVersteckt()).filter(Boolean),
    karten_ohne_asin: 0,
    karten_ohne_text: 0,
    step_werte,
    aktiv_start,
    aktiv_nach_klicks: [],
    aktiv_je_position: [],      // je Klickposition ALLE beobachteten Werte (BL-4)
    ergebnis_aktiv_am_ende: [],
    paare: [],                  // [karten, titel] je Kombination, entdoppelt (BL-3)
    je_kombi: [],               // {antworten, slugs} je Kombination (R23 B-5)
    doppelte_karten: 0,         // Kombinationen mit doppeltem Slug (BL-5)
    min_karten: null,
    antworten: [],
    slugs: [],
    titel: [],
    max_karten: 0,
    kombis: 0,
  };
  bericht.zurueck_mit_handler = zurueck.filter(b => !!b._handler.click).length;
  if (!fragen.length || fragen.some(f => !f.length)) return bericht;

  // Wirkt Zurueck? Zwei Antworten vorwaerts, dann zurueck: es muss genau der
  // vorhergehende Schritt aktiv sein. Runde 19 hat `data-back` von den Knoepfen entfernt
  // und das Wort nur in einem CSS-Kommentar gelassen -- die Mustersuche war erfuellt, die
  // Knoepfe waren tot. Ein Zustand laesst sich nicht so taeuschen.
  if (neustart && neustart._handler.click) neustart._handler.click();
  if (fragen[0][0]._handler.click) {
    fragen[0][0]._handler.click();
    const vorher = aktive();
    const zb = zurueck.find(b => !!b._handler.click);
    if (zb) {
      zb._handler.click();
      const nachher = aktive();
      bericht.zurueck_wirkt = (vorher.length === 1 && nachher.length === 1
                               && nachher[0] === vorher[0] - 1);
    } else {
      bericht.zurueck_wirkt = false;
    }
  }

  const slugs = new Set();
  const titel = new Set();
  const wege = fragen.reduce((acc, opts, i) =>
    acc.flatMap(weg => opts.map((_, j) => weg.concat([[i, j]]))), [[]]);

  for (const weg of wege) {
    if (neustart && neustart._handler.click) neustart._handler.click();
    const aktivFolge = [];
    for (const [i, j] of weg) {
      const btn = fragen[i][j];
      if (!btn._handler.click) return Object.assign(bericht, { fehler: `Option ${i}/${j} ohne Klick-Handler` });
      if (btn.istDeaktiviert()) continue;   // wie im Browser: kein Event
      btn._handler.click();
      aktivFolge.push(aktive().length);
    }
    bericht.kombis++;
    // ALLE beobachteten Werte je Position. Die erste Fassung behauptete im Kommentar
    // "schlechtester Zustand gewinnt" und uebernahm einen spaeteren Wert nur, wenn er
    // !== 1 war -- an der LETZTEN Position ist der Defektwert aber 1 (die Frage bleibt
    // neben dem Ergebnis stehen), also war dort jede Kombination ausser der ersten blind.
    for (let i = 0; i < aktivFolge.length; i++) {
      if (!bericht.aktiv_je_position[i]) bericht.aktiv_je_position[i] = [];
      if (!bericht.aktiv_je_position[i].includes(aktivFolge[i])) {
        bericht.aktiv_je_position[i].push(aktivFolge[i]);
      }
    }
    if (bericht.aktiv_nach_klicks.length < 1) bericht.aktiv_nach_klicks = aktivFolge;
    // Antworten UND Empfehlungen zusammen. Ohne diese Zuordnung liess sich die
    // Plattform-Zusage nicht pruefen: R23 hat den Plattform-Filter aus score() entfernt,
    // der Finder empfahl iPhone-Nutzern ein Android-only-Modell, und der Lauf blieb gruen.
    const antwortenHier = {};
    for (const [i, j] of weg) {
      const b2 = fragen[i][j];
      if (b2.dataset.key !== undefined) antwortenHier[b2.dataset.key] = b2.dataset.value;
    }
    bericht.je_kombi.push({ antworten: antwortenHier,
                            slugs: [...new Set([...(grid ? grid.innerHTML : '')
                              .matchAll(/data-product="([^"]+)"/g)].map(m => m[1]))] });
    bericht.ergebnis_aktiv_am_ende.push(ergebnis ? ergebnis.classList.contains(AKTIV) : false);
    if (titelEl) titel.add(titelEl.textContent);
    const html = grid ? grid.innerHTML : '';
    // VERSCHIEDENE Slugs, nicht Attribut-Vorkommen: `data-product` steht zweimal pro
    // Karte (am <article> und am Kauf-Link), die erste Fassung meldete deshalb 6 Karten
    // bei "Deine Top 3 Empfehlungen" -- ein Messfehler, der das Top-N-Gate sofort
    // falsch gemacht haette.
    // Karten als KARTEN zaehlen, nicht als Attribut-Vorkommen, und ihren Inhalt pruefen.
    // R21: Die Kartenvorlage ausgehoehlt und nur `data-product` stehen gelassen liess die
    // Probe weiter "3 Karten" melden -- im Browser drei leere <article>, null data-asin,
    // also die Geldleitung aus dem Finder weg (§A3).
    const karten = html.split(/<article\b/).slice(1);
    for (const k of karten) {
      const sm = /data-product="([^"]+)"/.exec(k);
      if (sm) slugs.add(sm[1]);
      if (!/data-asin="[^"]+"/.test(k)) bericht.karten_ohne_asin++;
      if (k.replace(/<[^>]*>/g, '').replace(/\s+/g, '').length < 10) bericht.karten_ohne_text++;
    }
    bericht.max_karten = Math.max(bericht.max_karten, karten.length);
    bericht.min_karten = bericht.min_karten === null
      ? karten.length : Math.min(bericht.min_karten, karten.length);
    // Titel UND Kartenzahl zusammen: Ein Zweig mit "Deine Top 3 Empfehlungen" und leerem
    // Gitter blieb gruen, weil nur das Maximum gemessen wurde (R22, 9 der 36 Faelle).
    const paar = karten.length + '|' + (titelEl ? titelEl.textContent.trim() : '');
    if (!bericht.paare.includes(paar)) bericht.paare.push(paar);
    // Dreimal dasselbe Modell als "Top 3" ist eine sichtbar falsche Seite. Die Slugs
    // wurden vorher entdoppelt, BEVOR etwas geprueft wurde.
    const slugsHier = karten.map(k => (/data-product="([^"]+)"/.exec(k) || [])[1])
      .filter(Boolean);
    if (new Set(slugsHier).size !== karten.length) bericht.doppelte_karten++;
  }
  bericht.slugs = [...slugs].sort();
  bericht.titel = [...titel].sort();
  bericht.ergebnis_aktiv_am_ende = [...new Set(bericht.ergebnis_aktiv_am_ende)];
  return bericht;
}

let roh = '';
process.stdin.on('data', (c) => { roh += c; });
process.stdin.on('end', () => {
  main(JSON.parse(roh || '{}'))
    .catch(e => ({ fehler: String((e && e.stack) || e) }))
    .then(aus => {
      process.stdout.write(JSON.stringify(aus));
      // Der Finder laedt products.json per Promise; ohne harten Ausstieg haengt der
      // Prozess an offenen Microtasks und verify.py wartet auf ein Ende, das nie kommt.
      process.exit(0);
    });
});
