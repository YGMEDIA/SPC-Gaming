#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gemeinsame Helfer fuer JSON-LD, benutzt von verify.py und sync_product_values.py.

Warum ein eigenes Modul: `typen_von` stand bis zum 01.10.2026 zweimal im Repo, einmal in
jedem der beiden Skripte. Der Docstring der zweiten Kopie begruendete sich ausgerechnet
damit, dass zwei Orte fuer dieselbe Regel zuverlaessig auseinanderlaufen -- und liess die
erste Kopie stehen. An einem einzigen Tag ist genau das dreimal passiert (Escaping,
Reichweite, Vergleichsregel beim Spec-Chip), jedes Mal mit demselben Ergebnis: Das eine
Werkzeug meldete gruen, das andere handelte anders.
"""


def typen_von(obj):
    """Die @type-Werte eines JSON-LD-Objekts, immer als Liste.

    @type kann ein String ODER eine Liste sein. Ein Vergleich `obj.get('@type') in MENGE`
    stuerzt bei einer Liste mit TypeError ab: Statt Befunden kaeme ein Traceback, und alle
    uebrigen Befunde des Laufs waeren weg. Ueber `"@type": ["Product"]` liessen sich am
    01.10. drei Gates abschalten, weil sie den String direkt verglichen.
    """
    t = obj.get('@type') if isinstance(obj, dict) else None
    if isinstance(t, str):
        return [t]
    if isinstance(t, (list, tuple)):
        return [x for x in t if isinstance(x, str)]
    return []
