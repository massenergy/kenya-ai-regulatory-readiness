#!/usr/bin/env python3
"""Render a Markdown report into a formatted .docx.

    python3 md2docx.py REPORT.md OUTPUT.docx

Handles the constructs reports actually use: headings (h1-h3), tables with alignment,
fenced code blocks, blockquotes, ordered/unordered lists, horizontal rules, and inline
**bold** / *italic* / `code` (including code spans nested inside bold).

Every workaround below exists because the naive version rendered wrong. Do not simplify
without re-rendering to PDF and looking at the result.
"""
import os
import re
import sys

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor, Inches
except ImportError:
    sys.exit("python-docx is required:  pip install python-docx")

if len(sys.argv) != 3:
    sys.exit(__doc__)
SRC, OUT = sys.argv[1], sys.argv[2]

PAGE_WIDTH_IN = 6.5          # usable text width on Letter/A4 with default margins

doc = Document()

# --- base styles -----------------------------------------------------------
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for name, size, color in (("Heading 1", 20, "1F3864"),
                          ("Heading 2", 14, "2E5496"),
                          ("Heading 3", 11.5, "2E5496")):
    st = doc.styles[name]
    st.font.name = "Calibri"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = RGBColor.from_string(color)
    st.paragraph_format.space_before = Pt(14)
    st.paragraph_format.space_after = Pt(6)


def shade(element, hexcolor):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), hexcolor)
    element.append(el)


def add_runs(par, text):
    """Inline **bold**, *italic*, `code`."""
    for tok in re.split(r"(\*\*.+?\*\*|`[^`]+`|(?<!\*)\*(?!\*)[^*]+\*(?!\*))", text):
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            # A code span can sit inside bold (**… `[billing]` …**). Render it bold and
            # drop the backticks instead of printing them literally.
            for part in re.split(r"(`[^`]+`)", tok[2:-2]):
                if not part:
                    continue
                r = par.add_run(part[1:-1] if part.startswith("`") else part)
                r.bold = True
                if part.startswith("`"):
                    r.font.name = "Consolas"
                    r.font.size = Pt(9.5)
        elif tok.startswith("`") and tok.endswith("`"):
            r = par.add_run(tok[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor.from_string("A03030")
        elif tok.startswith("*") and tok.endswith("*"):
            par.add_run(tok[1:-1]).italic = True
        else:
            par.add_run(tok)


def strip_md(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"\1", text)


BLOCK_START = r"^(#{1,6}\s|\||>|```|---$|\d+\.\s|[-*]\s)"

lines = open(SRC, encoding="utf-8").read().split("\n")
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()

    # --- fenced code block -------------------------------------------------
    if stripped.startswith("```"):
        i += 1
        body = []
        while i < len(lines) and not lines[i].strip().startswith("```"):
            body.append(lines[i])
            i += 1
        i += 1
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(4)
        r = p.add_run("\n".join(body))
        r.font.name = "Consolas"
        r.font.size = Pt(9.5)
        shade(p._p.get_or_add_pPr(), "F2F2F2")
        continue

    # --- table -------------------------------------------------------------
    if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:*-]+\|", lines[i + 1].strip()):
        header = [c.strip() for c in stripped.strip("|").split("|")]
        align_row = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
        aligns = [WD_ALIGN_PARAGRAPH.RIGHT if a.endswith(":") and not a.startswith(":")
                  else WD_ALIGN_PARAGRAPH.CENTER if a.startswith(":") and a.endswith(":")
                  else WD_ALIGN_PARAGRAPH.LEFT for a in align_row]
        i += 2
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1

        t = doc.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Repeat the header on every page a long table spans.
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        t.rows[0]._tr.get_or_add_trPr().append(th)

        for j, h in enumerate(header):
            cell = t.rows[0].cells[j]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = aligns[j]
            r = p.add_run(strip_md(h))
            r.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor.from_string("FFFFFF")
            shade(cell._tc.get_or_add_tcPr(), "1F3864")

        for row in rows:
            new_row = t.add_row()
            cs = OxmlElement("w:cantSplit")
            new_row._tr.get_or_add_trPr().append(cs)
            for j, val in enumerate(row[:len(header)]):
                new_row.cells[j].text = ""
                p = new_row.cells[j].paragraphs[0]
                p.alignment = aligns[j]
                p.paragraph_format.space_after = Pt(2)
                add_runs(p, val)
                for r in p.runs:
                    r.font.size = Pt(9.5)

        # Column widths: share the text width in proportion to content, but never below
        # the longest unbreakable token or values like "+16,740" split mid-number.
        widths = []
        for j in range(len(header)):
            cells_j = [strip_md(header[j])] + [strip_md(r[j]) for r in rows if j < len(r)]
            longest_cell = max(len(c) for c in cells_j)
            longest_word = max((len(w) for c in cells_j for w in c.split()), default=4)
            widths.append(min(max(longest_cell, longest_word + 2, 8), 34))
        total = sum(widths)
        t.autofit = False
        # Both of these are required: the renderer takes widths from w:tblGrid, and
        # without a fixed layout it re-autofits and ignores them entirely.
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(layout)
        grid = t._tbl.find(qn("w:tblGrid"))
        gridcols = grid.findall(qn("w:gridCol")) if grid is not None else []
        for j, w in enumerate(widths):
            if j < len(gridcols):
                gridcols[j].set(qn("w:w"), str(int(PAGE_WIDTH_IN * 1440 * w / total)))
            inches = Inches(PAGE_WIDTH_IN * w / total)
            for row in t.rows:
                row.cells[j].width = inches
        doc.add_paragraph()
        continue

    # --- blockquote --------------------------------------------------------
    if stripped.startswith(">"):
        body = []
        while i < len(lines) and lines[i].strip().startswith(">"):
            body.append(lines[i].strip().lstrip(">").strip())
            i += 1
        for chunk in [c for c in "\n".join(body).strip().split("\n\n") if c.strip()]:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(4)
            add_runs(p, chunk.replace("\n", " "))
            for r in p.runs:
                r.italic = True
                r.font.color.rgb = RGBColor.from_string("404040")
            shade(p._p.get_or_add_pPr(), "FAF6EC")
        continue

    if stripped in ("---", "***", "___"):
        i += 1
        continue

    # --- headings ----------------------------------------------------------
    m = re.match(r"^(#{1,6})\s+(.*)", stripped)
    if m:
        doc.add_heading(strip_md(m.group(2)), level=min(len(m.group(1)), 3))
        i += 1
        continue

    # --- lists -------------------------------------------------------------
    m = re.match(r"^(\d+)\.\s+(.*)", stripped)
    if m:
        p = doc.add_paragraph(style="List Number")
        add_runs(p, m.group(2))
        i += 1
        while i < len(lines) and lines[i].startswith("   ") and lines[i].strip():
            add_runs(p, " " + lines[i].strip())
            i += 1
        continue
    if re.match(r"^[-*]\s", stripped):
        p = doc.add_paragraph(style="List Bullet")
        add_runs(p, stripped[2:])
        i += 1
        while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
            add_runs(p, " " + lines[i].strip())
            i += 1
        continue

    if not stripped:
        i += 1
        continue

    # --- paragraph ---------------------------------------------------------
    # Soft-wrapped prose is rejoined, but a line opening with a bold label
    # (**Date:** …) is an intentional new line, not wrap — keep those breaks.
    segments = [[stripped]]
    i += 1
    while i < len(lines) and lines[i].strip() and not re.match(BLOCK_START, lines[i].strip()):
        nxt = lines[i].strip()
        (segments.append([nxt]) if nxt.startswith("**") else segments[-1].append(nxt))
        i += 1
    par = doc.add_paragraph()
    for n, seg in enumerate(segments):
        if n:
            par.add_run().add_break()
        add_runs(par, " ".join(seg))

out_dir = os.path.dirname(os.path.abspath(OUT))
os.makedirs(out_dir, exist_ok=True)   # the reports/ folder may not exist yet
doc.save(OUT)
print(f"wrote {OUT}")
