#!/usr/bin/env python3
"""Lager en Word-utgave (.docx) av en Fagnytt-artikkel i blad/artikler/ til gjennomgang og endringer.

    python3 word/lag_word.py blad/artikler/02_tallene.md Tallene_finnes_Fagnytt.docx
"""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
kilde, ut = Path(sys.argv[1]), Path(sys.argv[2])
s = kilde.read_text(encoding='utf-8')


def args(txt, start, n):
    """Les n klammeargumenter {..} fra posisjon start; returnerer (liste, sluttpos)."""
    out, i = [], start
    for _ in range(n):
        while txt[i] in ' \n': i += 1
        assert txt[i] == '{'
        d, j = 0, i
        while True:
            if txt[j] == '{': d += 1
            elif txt[j] == '}':
                d -= 1
                if d == 0: break
            j += 1
        out.append(txt[i + 1:j]); i = j + 1
    return out, i


m = re.search(r'\\artikkelopener', s)
if m:
    (tittel, under, forf, dato, kicker, ingress), e = args(s, m.end(), 6)
    flat = lambda t: re.sub(r'\s+', ' ', t).strip()
    head = f"# {flat(tittel)}\n\n**{flat(under)}**\n\n*{flat(kicker)}* · Av {flat(forf)} · {flat(dato)}\n\n*{flat(ingress)}*\n\n"
    s = s[:m.start()] + head + s[e:]
s = re.sub(r'\\lettrine\[[^\]]*\]\{(.)\}\{([^}]*)\}', r'\1\2', s)
s = s.replace('\\sluttmerke', '')


def tabell(mt):
    blokk = mt.group(0)
    rader = re.findall(r'^(?!\\)(.+?) \\\\$', blokk, flags=re.M)
    hode = re.search(r'\\textbf.*?\\\\', blokk).group(0)
    celler = lambda r: [re.sub(r'\\textbf\{(.*?)\}', r'\1', c).replace('\\%', '%').replace('\\\\', '').strip() for c in r.split('&')]
    hrad = celler(hode)
    body = [celler(r) for r in rader if not r.startswith('\\textbf')]
    cap = re.search(r'\\caption\{\\figlabel\{(.*?)\}(.*)\}\s*\\end', blokk, flags=re.S)
    tekst = f"**{cap.group(1).capitalize()}.** {cap.group(2).strip()}" if cap else ''
    linje = lambda c: '| ' + ' | '.join(c) + ' |'
    return '\n' + tekst + '\n\n' + linje(hrad) + '\n|' + '---|' * len(hrad) + '\n' + '\n'.join(linje(b) for b in body) + '\n'


s = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', tabell, s, flags=re.S)
tmp = HERE / '_word_tmp.md'
tmp.write_text(s, encoding='utf-8')
subprocess.run(['pandoc', str(tmp), '-o', str(ut), '--from', 'markdown+smart', '--lua-filter', str(HERE / 'word.lua'),
                '--resource-path', str(ROOT), '--shift-heading-level-by=0', '--wrap=none'], check=True, cwd=ROOT)
tmp.unlink()
print('Skrev', ut)
