"""Minimal, robust Markdown -> PDF (reportlab). Handles headings, paragraphs,
bullet lists, GitHub tables, images, and inline **bold**/*italic*/`code`.

    python scripts/md2pdf.py docs/paper/optionB_report.md docs/paper/optionB_report.pdf
"""
import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, ListFlowable, ListItem, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ss = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=ss["BodyText"], fontSize=9.5, leading=13, alignment=TA_LEFT, spaceAfter=4)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=8, leading=10, spaceAfter=0)
H = {1: ParagraphStyle("h1", parent=ss["Heading1"], fontSize=16, spaceBefore=10, spaceAfter=6),
     2: ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, spaceBefore=8, spaceAfter=4),
     3: ParagraphStyle("h3", parent=ss["Heading3"], fontSize=11, spaceBefore=6, spaceAfter=3)}


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", t)  # drop link targets, keep text
    return t


def cells(line):
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    return parts


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    base = src.parent
    lines = src.read_text(encoding="utf-8").splitlines()
    flow, i = [], 0
    bullets = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            flow.append(ListFlowable([ListItem(Paragraph(inline(b), BODY), leftIndent=10) for b in bullets],
                                     bulletType="bullet", start="•"))
            flow.append(Spacer(1, 3)); bullets = []

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush_bullets(); i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            flush_bullets()
            lvl = len(m.group(1))
            flow.append(Paragraph(inline(m.group(2)), H[lvl])); i += 1; continue
        if s.startswith("!["):
            flush_bullets()
            mm = re.match(r"!\[.*?\]\((.+?)\)", s)
            if mm:
                p = (base / mm.group(1)).resolve()
                if p.exists():
                    try:
                        flow.append(Image(str(p), width=12 * cm, height=9 * cm, kind="proportional"))
                        flow.append(Spacer(1, 4))
                    except Exception:
                        pass
            i += 1; continue
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?[\s:\-|]+\|?$", lines[i + 1].strip()):
            flush_bullets()
            header = cells(s); i += 2; rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i].strip())); i += 1
            data = [[Paragraph(inline(c), CELL) for c in header]] + \
                   [[Paragraph(inline(c), CELL) for c in r] for r in rows]
            t = Table(data, repeatRows=1, hAlign="LEFT")
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
            flow.append(t); flow.append(Spacer(1, 5)); continue
        if re.match(r"^[-*]\s+", s):
            bullets.append(re.sub(r"^[-*]\s+", "", s)); i += 1; continue
        if s.startswith("> "):
            flow.append(Paragraph("<i>" + inline(s[2:]) + "</i>", BODY)); i += 1; continue
        if re.match(r"^-{3,}$", s):
            i += 1; continue
        flush_bullets()
        flow.append(Paragraph(inline(s), BODY)); i += 1

    flush_bullets()
    doc = SimpleDocTemplate(str(dst), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.6 * cm, bottomMargin=1.6 * cm)
    doc.build(flow)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
