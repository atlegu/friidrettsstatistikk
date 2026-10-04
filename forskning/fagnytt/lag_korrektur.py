#!/usr/bin/env python3
"""Lager korrektur (page proof) av én artikkel fra Fagnytt_pilot.pdf: følgebrev + artikkelsidene med korrekturstempel.

    python3 lag_korrektur.py            # høydehopp-artikkelen (s. 16-20)
"""
import io
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

HERE = Path(__file__).resolve().parent
KILDE = HERE / 'Fagnytt_pilot.pdf'
UT = HERE / 'Korrektur_Hoydehopp_Fagnytt_1-2026.pdf'
FRA, TIL = 16, 20          # sidetall i bladet
TITTEL = 'Hvor forsvant alle høydehopperne?'
FORFATTER = 'Henning Hofstad'
DATO = '4. oktober 2026'
BLAA, ORANSJE, GRAA = (0.12, 0.31, 0.47), (0.85, 0.28, 0.06), (0.47, 0.47, 0.47)

# ---------- følgebrev
buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=A4)
W, H = A4
c.setFillColorRGB(*BLAA); c.rect(0, H - 22 * mm, W, 22 * mm, fill=1, stroke=0)
c.setFillColorRGB(*ORANSJE); c.rect(0, H - 24 * mm, 32 * mm, 2 * mm, fill=1, stroke=0)
c.setFillColorRGB(1, 1, 1); c.setFont('Helvetica-Bold', 10)
c.drawString(18 * mm, H - 14 * mm, 'FAGNYTT  /  NR. 1 · 2026')
c.setFillColorRGB(*ORANSJE); c.setFont('Helvetica-Bold', 10); c.drawString(18 * mm, H - 44 * mm, 'KORREKTUR')
c.setFillColorRGB(0.17, 0.17, 0.17); c.setFont('Helvetica-Bold', 26); c.drawString(18 * mm, H - 58 * mm, TITTEL)
c.setFont('Helvetica', 13); c.setFillColorRGB(*BLAA); c.drawString(18 * mm, H - 67 * mm, f'{FORFATTER}  ·  s. {FRA}–{TIL} i bladet  ·  {DATO}')
c.setStrokeColorRGB(*ORANSJE); c.setLineWidth(2.4); c.line(18 * mm, H - 74 * mm, 40 * mm, H - 74 * mm)


def avsnitt(y, overskrift, linjer):
    c.setFillColorRGB(*BLAA); c.setFont('Helvetica-Bold', 11); c.drawString(18 * mm, y, overskrift)
    y -= 6.5 * mm
    c.setFillColorRGB(0.17, 0.17, 0.17); c.setFont('Helvetica', 10.5)
    for l in linjer:
        c.drawString(21 * mm, y, l); y -= 5.4 * mm
    return y - 4 * mm


y = H - 88 * mm
y = avsnitt(y, 'Dette er', [
    f'Artikkelen slik den står i bladet, med endelige sidetall ({FRA}–{TIL}). Tekst, bilder og',
    'grafer er satt i bladets nye layout. Teksten er din, med de endringene som er listet under.'])
y = avsnitt(y, 'Vi ber deg sjekke', [
    '•  navn, årstall, høyder, rekorder og plasseringer i teksten',
    '•  at oppsettet ikke har endret meningen noen steder',
    '•  Figur 1 (se under)'])
y = avsnitt(y, 'Det redaksjonen har lagt til', [
    '•  Fire mellomtitler: «Fra dykk til flop», «Gode år – og så nedturen», «Hva er årsaken?»,',
    '    «Hva må gjøres?». To uthevede sitater er tatt ordrett fra teksten din.',
    '•  Undertittel og ingress (ingressen er presentasjonsteksten fra nr. 1-utkastet).',
    '•  Figur 1: nr. 1, 5, 10, 25 og 50 på norsk årsliste i høyde, herrer og damer, 1968–2026.',
    '•  Bildet av Falkum og Totland sist i artikkelen.'])
y = avsnitt(y, 'Slik sender du rettelser', [
    'Skriv sidetall, spalte og ordene som skal endres, for eksempel:',
    '«s. 17, venstre spalte, 2. avsnitt: ‹1 976› skal være ‹1 977›». Du kan også sende',
    'PDF-en tilbake med kommentarer. Endringer i selve layouten tar vi hos oss.'])
c.setFillColorRGB(*GRAA); c.setFont('Helvetica-Oblique', 9)
c.drawString(18 * mm, 18 * mm, 'Korrektur er ikke endelig trykkfil. Tallene i Figur 1 er hentet fra årslistene i Høydetilgraf.csv.')
c.showPage(); c.save()

# ---------- artikkelsider med stempel
stempel = io.BytesIO()
s = canvas.Canvas(stempel, pagesize=A4)
s.setFillColorRGB(*GRAA); s.setFont('Helvetica-Bold', 7)
s.drawCentredString(W / 2, 9 * mm, f'KORREKTUR  ·  FAGNYTT NR. 1 · 2026  ·  {FORFATTER.upper()}  ·  {DATO.upper()}')
s.showPage(); s.save()
stempel.seek(0)
st = PdfReader(stempel).pages[0]

w = PdfWriter()
w.add_page(PdfReader(io.BytesIO(buf.getvalue())).pages[0])
r = PdfReader(str(KILDE))
for i in range(FRA - 1, TIL):
    p = r.pages[i]
    p.merge_page(st)
    w.add_page(p)
w.add_metadata({'/Title': f'Korrektur: {TITTEL}', '/Author': 'Fagnytt'})
with open(UT, 'wb') as f:
    w.write(f)
print('Skrev', UT)
