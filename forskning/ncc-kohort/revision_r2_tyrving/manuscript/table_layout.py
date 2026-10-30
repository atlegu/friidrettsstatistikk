"""
table_layout.py — column widths and line-break control for the Word tables (used by
analysis/r1_06_tables.py, which writes the pipe tables, and build_r1.py, which converts them).

pandoc takes a pipe table's relative column widths from the dash counts of its separator line, and Word
lays the table out at those fixed widths: a word or number wider than its column is split inside the word.
The widths are therefore computed from the printed width of the text:

1. every column gets room for its widest unbreakable piece (Word may break at a space, after a hyphen and
   on either side of an en dash) plus the cell margins and a little slack; a bracketed interval such as "[0.60, 0.95]"
   counts as one piece (the build then joins it with a no-break space), except in the columns where giving
   that up saves most, if the table cannot otherwise fit;
2. any set of columns whose cells are all short may be widened to hold each cell on one line, and the rest
   of the line is shared in proportion to how much each column still lacks for its longest cell (the
   automatic table layout of web browsers);
3. of these layouts the one with the fewest printed lines is chosen, by filling every cell line by line;
   a line break inside a bracketed interval or at the dash of a range ("13 [6–" / "20]") counts as two
   lines.

Widths are in points for the table text, Times New Roman 10 pt (style "Table Text", set by build_r1.py and
tabletext.lua; Adobe Times-Roman metrics, bold counted 6% wider), on a 450-pt text line (A4 with 1-inch
margins) with the cell margins of pandoc's table style (5.4 pt on each side).
"""

import re

LINE_PT = 450                      # text line
FONT_PT = 10                       # table text
MARGIN_PT = 10.8                   # cell margins, left and right
SLACK_PT, MIN_SLACK_PT = 5.2, 1.5  # room beyond the text: preferred, and at least
SHORT_PT = 130                     # longest cell of a column that may be kept on one line
UGLY = 2                           # cost of a break inside an interval or at a range dash, in lines
DASHES = 400                       # dash count of a separator line (resolution of the widths)
ROUND_PT = LINE_PT / DASHES / 2    # largest rounding of a column width to whole dashes
NBSP = "\N{NO-BREAK SPACE}"
DASH = "\N{EN DASH}"

_W = {**dict.fromkeys("0123456789", 500), " ": 250, NBSP: 250, ".": 250, ",": 250, ":": 278, ";": 278,
      "(": 333, ")": 333, "[": 333, "]": 333, "-": 333, DASH: 500, "\N{EM DASH}": 1000, "\N{MINUS SIGN}": 564,
      "+": 564, "=": 564, "<": 564, ">": 564, "\N{GREATER-THAN OR EQUAL TO}": 549, "\N{LESS-THAN OR EQUAL TO}": 549,
      "\N{MULTIPLICATION SIGN}": 564, "%": 833, "/": 278, "'": 180, "\N{RIGHT SINGLE QUOTATION MARK}": 333,
      "\N{LEFT DOUBLE QUOTATION MARK}": 444, "\N{RIGHT DOUBLE QUOTATION MARK}": 444, "\N{SUPERSCRIPT TWO}": 300,
      "\N{GREEK SMALL LETTER CHI}": 549, "\N{ALMOST EQUAL TO}": 549, "\N{RIGHTWARDS ARROW}": 1000,
      "\N{MIDDLE DOT}": 250, "\N{SQUARE ROOT}": 549, "&": 778, "?": 444, "!": 333}
_W.update(zip("abcdefghijklmnopqrstuvwxyz", [444, 500, 444, 500, 444, 333, 500, 500, 278, 278, 500, 278, 778,
                                             500, 500, 500, 500, 333, 389, 278, 500, 500, 722, 500, 500, 444]))
_W.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [722, 667, 667, 722, 611, 556, 722, 722, 333, 389, 722, 611, 889,
                                             722, 722, 556, 722, 667, 556, 611, 722, 722, 944, 722, 722, 611]))

NUM = r"[\N{MINUS SIGN}-]?\d[\d.,]*%?"
CI = re.compile(r"(\\?\[" + NUM + r"),[ \N{NO-BREAK SPACE}](" + NUM + r"\\?\])")   # [0.60, 0.95], escaped \[ \]


def text_pt(s, bold=False):
    """Printed width in points of plain text."""
    return sum(_W.get(ch, 556) for ch in s) * FONT_PT / 1000 * (1.06 if bold else 1)


def plain(cell):
    """(text without markdown and highlight markup, bold?)"""
    c = str(cell)
    return re.sub(r"\{\+|\+\}|\*|\\|~|\^", "", c), "**" in c


def _join(text):
    return CI.sub(lambda m: f"{m.group(1)},{NBSP}{m.group(2)}", text)


def _pieces(text, bold, join):
    """A cell's pieces between line-break opportunities: (width, space before, break before is ugly)."""
    text = (_join(text) if join else text).replace("< .", "<" + NBSP + ".").strip()
    out, depth, prev = [], 0, ""
    for k, word in enumerate(re.split(r"[ \t]+", text)):
        for i, p in enumerate(re.split(r"(?<=-)(?=[A-Za-z])|(?<=\w" + DASH + r")(?=\w)|(?<=\w)(?=" + DASH + r"\w)", word)):
            out.append((text_pt(p, bold), text_pt(" ", bold) if k and not i else 0,
                        depth > 0 or (i > 0 and (prev.endswith(DASH) or p.startswith(DASH)))))
            depth, prev = depth + p.count("[") - p.count("]"), p
    return out


def _lines(pieces, avail):
    """(lines, ugly breaks) when the pieces are set line by line into `avail` points."""
    n, ugly, cur = 1, 0, None
    for w, gap, bad in pieces:
        if cur is not None and cur + gap + w > avail:
            n, ugly, cur = n + 1, ugly + bad, w
        else:
            cur = w if cur is None else cur + gap + w
    return n, ugly


def _ci_need(text, bold):
    """Column width that holds the cell's widest interval on one line (keep_together's rule)."""
    return max([text_pt(_join(m.group()), bold) + MARGIN_PT + MIN_SLACK_PT - ROUND_PT for m in CI.finditer(text)] or [0])


def col_widths(header, rows):
    """(dash counts, columns whose intervals may wrap) for a pipe table. Raises if even the widest pieces do
    not fit on the line, so a table that Word would have to split inside a word is never written."""
    ncol = len(header)
    table = [header] + [list(r) + [""] * (ncol - len(r)) for r in rows]
    cell = [[plain(r[j]) for j in range(ncol)] for r in table]
    text = [max(text_pt(*cell[i][j]) for i in range(len(table))) for j in range(ncol)]
    pieces = {join: [[_pieces(*cell[i][j], join) for j in range(ncol)] for i in range(len(table))] for join in (True, False)}
    need = [[_ci_need(*cell[i][j]) for j in range(ncol)] for i in range(len(table))]
    widest = {join: [max(w for i in range(len(table)) for w, _, _ in pieces[join][i][j]) for j in range(ncol)]
              for join in (True, False)}
    # 1. widest piece; intervals unjoined first in the columns where that saves most
    joined = set(range(ncol))
    lo = lambda: [widest[j in joined][j] + MARGIN_PT + MIN_SLACK_PT for j in range(ncol)]  # noqa: E731
    while sum(lo()) > LINE_PT:
        save = {j: widest[True][j] - widest[False][j] for j in joined if widest[True][j] > widest[False][j]}
        if not save:
            raise ValueError(f"table too wide for the line: {header}")
        joined.discard(max(save, key=save.get))
    base = lo()

    def spread(width):
        want = [max(w, t + MARGIN_PT + SLACK_PT) for w, t in zip(width, text)]
        room, extra = LINE_PT - sum(width), sum(a - w for a, w in zip(want, width))
        return [w + (room * (a - w) / extra if extra > 0 else room / ncol) for w, a in zip(width, want)]

    def cost(width):
        total = 0
        for i in range(len(table)):
            height = 1
            for j in range(ncol):
                n, ugly = _lines(pieces[need[i][j] <= width[j]][i][j], width[j] - MARGIN_PT - MIN_SLACK_PT + ROUND_PT)
                height, total = max(height, n), total + UGLY * ugly
            total += height
        return total

    # 2-3. every set of short columns held on one line; the layout with the fewest lines
    short = [j for j in range(ncol) if text[j] + MARGIN_PT <= SHORT_PT and text[j] + MARGIN_PT + MIN_SLACK_PT > base[j]]
    best = None
    for mask in range(1 << len(short)):
        width = [text[j] + MARGIN_PT + MIN_SLACK_PT if j in short and mask >> short.index(j) & 1 else base[j]
                 for j in range(ncol)]
        if sum(width) <= LINE_PT:
            width = spread(width)
            c = cost(width)
            if best is None or c < best[0] - 1e-9:
                best = (c, width)
    width = best[1]
    return [max(3, round(DASHES * w / sum(width))) for w in width], sorted(set(range(ncol)) - joined)


def keep_together(md):
    """Line-break control in the pipe tables of a markdown text: '< .001' is never broken, and a bracketed
    interval is joined with a no-break space when its column is wide enough to hold it (column widths from
    the table's dash counts)."""
    out, frac = [], None
    for line in md.split("\n"):
        if not line.startswith("|"):
            frac = None
        elif re.fullmatch(r"\|(?::?-+:?\|)+", line.strip()):
            d = [len(x.strip(":")) for x in line.strip()[1:-1].split("|")]
            frac = [k / sum(d) for k in d]
        else:
            line = line.replace("< .", "<" + NBSP + ".")
            if frac:
                cells = line.strip()[1:-1].split("|")

                def join(m, j):
                    fits = _ci_need(plain(m.group())[0], "**" in cells[j]) <= frac[j] * LINE_PT
                    return f"{m.group(1)},{NBSP if fits else ' '}{m.group(2)}"
                cells = [CI.sub(lambda m, j=j: join(m, j), c) if j < len(frac) else c for j, c in enumerate(cells)]
                line = "|" + "|".join(cells) + "|"
        out.append(line)
    return "\n".join(out)
