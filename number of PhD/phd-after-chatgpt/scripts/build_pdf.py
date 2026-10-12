"""Build the included one-page PDF overview. Requires reportlab."""

import sys
from pathlib import Path
from statistics import mean

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analysis import read_data, TOTAL, MATH, PRE, POST  # noqa: E402


def build():
    regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(regular)))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(bold)))
        pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold")
        font_normal, font_bold = "DejaVu", "DejaVu-Bold"
    else:
        font_normal, font_bold = "Helvetica", "Helvetica-Bold"
    d = read_data()
    target = ROOT / "report/overview.pdf"
    target.parent.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName=font_bold, fontSize=19, leading=23, textColor=colors.HexColor("#1c2638"), spaceAfter=7))
    styles.add(ParagraphStyle(name="SubCustom", parent=styles["Normal"], fontName=font_normal, fontSize=10, leading=14, textColor=colors.HexColor("#526070"), spaceAfter=13))
    styles.add(ParagraphStyle(name="BodyCustom", parent=styles["Normal"], fontName=font_normal, fontSize=9.5, leading=14, spaceAfter=9))
    styles.add(ParagraphStyle(name="SmallCustom", parent=styles["Normal"], fontName=font_normal, fontSize=8, leading=11, textColor=colors.HexColor("#526070")))
    styles.add(ParagraphStyle(name="HeadingCustom", parent=styles["Heading2"], fontName=font_bold, fontSize=11.5, leading=15, textColor=colors.HexColor("#2456a6"), spaceBefore=10, spaceAfter=5))

    story = [Paragraph("U.S. PhDs before and after ChatGPT", styles["TitleCustom"]),
             Paragraph("Research doctorate recipients at U.S. institutions | 2015-2025 | NCSES Survey of Earned Doctorates", styles["SubCustom"]),
             Paragraph("Question and scope", styles["HeadingCustom"]),
             Paragraph("How did annual research doctorate counts change around the November 30, 2022 public launch of ChatGPT? This is a descriptive timing comparison, with a mathematics and statistics focus. It does not estimate an effect caused by ChatGPT.", styles["BodyCustom"])]

    rows = [["Survey year", "All research doctorates", "Mathematics and statistics", "Math/stat share"]]
    for y in range(2015, 2026):
        rows.append([str(y), f"{d[TOTAL,y]:,}", f"{d[MATH,y]:,}", f"{100*d[MATH,y]/d[TOTAL,y]:.2f}%"])
    table = Table(rows, colWidths=[0.9*inch, 1.65*inch, 1.85*inch, 1.1*inch], repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2456a6")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), font_bold),
        ("FONTNAME", (0,1), (-1,-1), font_normal),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f8")]),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [table, Spacer(1, 10)]
    before_all = mean(d[TOTAL,y] for y in PRE)
    after_all = mean(d[TOTAL,y] for y in POST)
    before_math = mean(d[MATH,y] for y in PRE)
    after_math = mean(d[MATH,y] for y in POST)
    story += [Paragraph("Period averages", styles["HeadingCustom"]),
              Paragraph(f"Mean annual all-field count: <b>{before_all:,.0f}</b> in 2015-2022 versus <b>{after_all:,.0f}</b> in 2023-2025 ({(after_all/before_all-1)*100:+.1f}%). Mathematics and statistics: <b>{before_math:,.0f}</b> versus <b>{after_math:,.0f}</b> ({(after_math/before_math-1)*100:+.1f}%). The windows have different lengths; these are simple averages, not adjusted forecasts.", styles["BodyCustom"]),
              Paragraph("How to read this", styles["HeadingCustom"]),
              Paragraph("Survey year 2023 spans July 2022-June 2023 and straddles launch. A 2023-2025 graduation reflects admissions and research decisions made years earlier. The 2021 field taxonomy change complicates subfield trends; COVID, funding, and immigration also matter. Counts cannot show whether AI changed demand for a PhD.", styles["BodyCustom"]),
              Paragraph("Source: NCSES, Doctorate Recipients from U.S. Universities: 2025 Data Tables, NSF 26-326, Table 1-5 (Sept. 25, 2026). ncses.nsf.gov/surveys/earned-doctorates/2025. The accompanying repository contains the data, code, chart, and a fuller methodology.", styles["SmallCustom"])]
    doc = SimpleDocTemplate(str(target), pagesize=(8.5*inch, 11*inch), leftMargin=0.65*inch, rightMargin=0.65*inch, topMargin=0.55*inch, bottomMargin=0.55*inch)
    doc.build(story)
    print(target)


if __name__ == "__main__":
    build()
