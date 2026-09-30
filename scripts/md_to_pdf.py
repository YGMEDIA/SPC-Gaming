#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_to_pdf.py — macht aus einer Brain-Markdown-Datei ein lesbares PDF im Shop-Look.

Gedacht fuer `brain/07-wissen/`: aufbereitetes Fremdwissen, das Yasin auch ausserhalb
des Repos lesen oder weitergeben koennen soll.

Braucht reportlab. Das System-Python ist per PEP 668 gesperrt, deshalb ein venv:
    python3 -m venv .venv-tools && .venv-tools/bin/pip install reportlab
    .venv-tools/bin/python scripts/md_to_pdf.py <quelle.md> <ziel.pdf> "<Titel>" "<Untertitel>"

Unterstuetzt: H2/H3, Absaetze, Listen, Tabellen, Trennlinien, **fett**, *kursiv*, `code`.
"""

import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

NAVY = colors.HexColor('#12233f')
BLUE = colors.HexColor('#1f6feb')
SOFT = colors.HexColor('#44546a')
LINE = colors.HexColor('#d6dbe3')

ss = getSampleStyleSheet()
S = {
    'h1': ParagraphStyle('h1', parent=ss['Title'], fontName='Helvetica-Bold', fontSize=19,
                         leading=24, textColor=NAVY, spaceAfter=4, alignment=0),
    'sub': ParagraphStyle('sub', parent=ss['Normal'], fontSize=9.5, leading=13.5,
                          textColor=SOFT, spaceAfter=14),
    'h1b': ParagraphStyle('h1b', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=16,
                          leading=20, textColor=NAVY, spaceBefore=20, spaceAfter=9),
    'h2': ParagraphStyle('h2', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=13.5,
                         leading=17.5, textColor=NAVY, spaceBefore=15, spaceAfter=6),
    'h3': ParagraphStyle('h3', parent=ss['Heading2'], fontName='Helvetica-Bold', fontSize=10.8,
                         leading=14.5, textColor=BLUE, spaceBefore=11, spaceAfter=4),
    'p': ParagraphStyle('p', parent=ss['Normal'], fontSize=9.5, leading=14,
                        spaceAfter=6.5, textColor=colors.HexColor('#1a2230')),
    'it': ParagraphStyle('it', parent=ss['Normal'], fontName='Helvetica-Oblique', fontSize=8.6,
                         leading=12, textColor=SOFT, spaceAfter=6.5),
    'cell': ParagraphStyle('cell', parent=ss['Normal'], fontSize=8.2, leading=11.4),
    'cellh': ParagraphStyle('cellh', parent=ss['Normal'], fontName='Helvetica-Bold',
                            fontSize=8.2, leading=11.4, textColor=colors.white),
}


def inline(t):
    t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', t)
    t = re.sub(r'`([^`]+?)`', r'<font face="Courier" size="8.4">\1</font>', t)
    return t


def spalten_breiten(n, verfuegbar):
    if n == 2:
        return [verfuegbar * 0.34, verfuegbar * 0.66]
    if n == 3:
        return [verfuegbar * 0.46, verfuegbar * 0.30, verfuegbar * 0.24]
    if n == 4:
        return [verfuegbar * 0.05, verfuegbar * 0.43, verfuegbar * 0.31, verfuegbar * 0.21]
    if n == 5:
        return [verfuegbar * 0.05, verfuegbar * 0.41, verfuegbar * 0.20, verfuegbar * 0.13,
                verfuegbar * 0.21]
    return [verfuegbar / n] * n


def build(md_path, pdf_path, titel, untertitel):
    zeilen = open(md_path, encoding='utf-8').read().splitlines()
    flow = [Paragraph(titel, S['h1']), Paragraph(untertitel, S['sub']),
            HRFlowable(width='100%', color=LINE, spaceAfter=10)]
    puffer = []

    def tabelle_leeren():
        if not puffer:
            return
        rows = [r for r in puffer if not all(set(c) <= set('-: ') for c in r)]
        if rows:
            daten = [[Paragraph(inline(c), S['cellh'] if n == 0 else S['cell']) for c in r]
                     for n, r in enumerate(rows)]
            t = Table(daten, colWidths=spalten_breiten(len(rows[0]), A4[0] - 40 * mm),
                      repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), NAVY),
                ('GRID', (0, 0), (-1, -1), 0.4, LINE),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                 [colors.white, colors.HexColor('#f4f6f9')]),
                ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            flow.extend([Spacer(1, 4), t, Spacer(1, 10)])
        puffer.clear()

    for roh in zeilen:
        z = roh.rstrip()
        if z.startswith('|'):
            puffer.append([c.strip() for c in z.strip('|').split('|')])
            continue
        tabelle_leeren()
        if not z:
            continue
        if z.startswith('---') and len(set(z)) <= 2:
            flow.append(HRFlowable(width='100%', color=LINE, spaceBefore=8, spaceAfter=8))
        elif z.startswith('### '):
            flow.append(Paragraph(inline(z[4:]), S['h3']))
        elif z.startswith('## '):
            flow.append(Paragraph(inline(z[3:]), S['h2']))
        elif z.startswith('# '):
            flow.append(Paragraph(inline(z[2:]), S['h1b']))
        elif z.startswith('*') and z.endswith('*') and not z.startswith('**'):
            flow.append(Paragraph(inline(z.strip('*')), S['it']))
        elif z.startswith('- '):
            flow.append(Paragraph('&bull;&nbsp;&nbsp;' + inline(z[2:]), S['p']))
        else:
            flow.append(Paragraph(inline(z), S['p']))
    tabelle_leeren()

    def deko(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(SOFT)
        canvas.setFont('Helvetica', 7.5)
        canvas.drawString(20 * mm, 12 * mm,
                          'smartphone-controller.com · YG MEDIA · Stand 30.09.2026')
        canvas.drawRightString(A4[0] - 20 * mm, 12 * mm, f'Seite {doc.page}')
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, 16 * mm, A4[0] - 20 * mm, 16 * mm)
        canvas.restoreState()

    SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=20 * mm, bottomMargin=22 * mm,
                      leftMargin=20 * mm, rightMargin=20 * mm,
                      title=titel, author='YG MEDIA').build(
        flow, onFirstPage=deko, onLaterPages=deko)
    print(f'PDF geschrieben: {pdf_path}')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    build(*sys.argv[1:5])
