"""Markdown -> PDF (reportlab), styled for a research-paper read: Times New Roman
body, justified text, a centred title/author block, numbered-section headings, and
GitHub tables. Handles headings, paragraphs, bullet lists, images, blockquotes, a
`::center::` line marker, and inline **bold**/*italic*/`code`.

    python scripts/md2pdf.py docs/paper/longitudinal_report.md docs/paper/longitudinal_report.pdf
"""
import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, ListFlowable, ListItem, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

# --- Fonts: Times New Roman gives a serif paper look and full Unicode coverage
# (>=, <=, ~=, x, sub/superscripts) that reportlab's builtin Helvetica lacks.
FONTS = {"n": "times.ttf", "b": "timesbd.ttf", "i": "timesi.ttf", "bi": "timesbi.ttf"}
FDIR = Path("C:/Windows/Fonts")
BASE, BOLD, ITAL, BITAL = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique"
try:
    pdfmetrics.registerFont(TTFont("Serif", str(FDIR / FONTS["n"])))
    pdfmetrics.registerFont(TTFont("Serif-Bold", str(FDIR / FONTS["b"])))
    pdfmetrics.registerFont(TTFont("Serif-Italic", str(FDIR / FONTS["i"])))
    pdfmetrics.registerFont(TTFont("Serif-BoldItalic", str(FDIR / FONTS["bi"])))
    pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                                  italic="Serif-Italic", boldItalic="Serif-BoldItalic")
    BASE, BOLD, ITAL, BITAL = "Serif", "Serif-Bold", "Serif-Italic", "Serif-BoldItalic"
except Exception:
    pass

ss = getSampleStyleSheet()
TITLE = ParagraphStyle("title", parent=ss["Title"], fontName=BOLD, fontSize=17,
                       leading=21, alignment=TA_CENTER, spaceBefore=4, spaceAfter=6)
CENTER = ParagraphStyle("center", parent=ss["BodyText"], fontName=BASE, fontSize=10.5,
                        leading=14, alignment=TA_CENTER, spaceAfter=3)
BODY = ParagraphStyle("body", parent=ss["BodyText"], fontName=BASE, fontSize=10,
                      leading=14, alignment=TA_JUSTIFY, spaceAfter=6, firstLineIndent=0)
CELL = ParagraphStyle("cell", parent=BODY, fontSize=9, leading=11, alignment=TA_LEFT, spaceAfter=0)
CAP = ParagraphStyle("cap", parent=BODY, fontName=ITAL, fontSize=8.5, leading=11,
                     alignment=TA_LEFT, spaceAfter=8, textColor=colors.HexColor("#333333"))
H = {1: ParagraphStyle("h1", parent=ss["Heading1"], fontName=BOLD, fontSize=13, spaceBefore=12, spaceAfter=5),
     2: ParagraphStyle("h2", parent=ss["Heading2"], fontName=BOLD, fontSize=11.5, spaceBefore=9, spaceAfter=4),
     3: ParagraphStyle("h3", parent=ss["Heading3"], fontName=BITAL, fontSize=10.5, spaceBefore=7, spaceAfter=3)}


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", t)  # drop link targets, keep text
    return t


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    base = src.parent
    lines = src.read_text(encoding="utf-8").splitlines()
    flow, i, seen_title = [], 0, False
    bullets = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            flow.append(ListFlowable(
                [ListItem(Paragraph(inline(b), BODY), leftIndent=10) for b in bullets],
                bulletType="bullet", start="\u2022"))
            flow.append(Spacer(1, 3)); bullets = []

    while i < len(lines):
        s = lines[i].strip()
        if not s:
            flush_bullets(); i += 1; continue
        if s.startswith("::center::"):
            flush_bullets()
            flow.append(Paragraph(inline(s[len("::center::"):].strip()), CENTER)); i += 1; continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            flush_bullets()
            lvl = len(m.group(1))
            if lvl == 1 and not seen_title:
                seen_title = True
                flow.append(Paragraph(inline(m.group(2)), TITLE))
            else:
                flow.append(Paragraph(inline(m.group(2)), H[lvl]))
            i += 1; continue
        if s.startswith("!["):
            flush_bullets()
            mm = re.match(r"!\[(.*?)\]\((.+?)\)", s)
            if mm:
                p = (base / mm.group(2)).resolve()
                if p.exists():
                    try:
                        flow.append(Image(str(p), width=12 * cm, height=9 * cm, kind="proportional"))
                        flow.append(Spacer(1, 2))
                        if mm.group(1).strip():
                            flow.append(Paragraph(inline(mm.group(1).strip()), CAP))
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
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
            flow.append(t); flow.append(Spacer(1, 7)); continue
        if re.match(r"^[-*]\s+", s):
            bullets.append(re.sub(r"^[-*]\s+", "", s)); i += 1; continue
        if s.startswith("> "):
            flow.append(Paragraph("<i>" + inline(s[2:]) + "</i>", BODY)); i += 1; continue
        if re.match(r"^-{3,}$", s):
            i += 1; continue
        flush_bullets()
        flow.append(Paragraph(inline(s), BODY)); i += 1

    flush_bullets()
    doc = SimpleDocTemplate(str(dst), pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title=src.stem.replace("_", " "))
    doc.build(flow)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
