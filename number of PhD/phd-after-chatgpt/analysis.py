"""Descriptive analysis of U.S. research doctorates from NCSES SED 2025."""

import csv
from pathlib import Path
from statistics import mean
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
START_YEAR, END_YEAR = 2015, 2025
PRE = range(2015, 2023)
POST = range(2023, 2026)
TOTAL = "All research doctorates"
MATH = "Mathematics and statistics"
SUBFIELDS = (
    "Applied mathematics", "Mathematics", "Statistics",
    "Mathematics and statistics, other",
)
FIELDS = (TOTAL, MATH, *SUBFIELDS, "Computer and information sciences")


def read_data():
    data = {}
    with (ROOT / "data/sed_2025_table_1_5.csv").open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["field"], int(row["year"]))
            if key in data:
                raise ValueError(f"Duplicate row: {key}")
            count = int(row["count"])
            if count < 0 or row["source_table"] != "SED 2025 Table 1-5":
                raise ValueError(f"Invalid count or provenance: {key}")
            data[key] = count
    expected = {(f, y) for f in FIELDS for y in range(START_YEAR, END_YEAR + 1)}
    if set(data) != expected:
        raise ValueError(f"Missing: {sorted(expected - set(data))}; extra: {sorted(set(data) - expected)}")
    for year in range(START_YEAR, END_YEAR + 1):
        if sum(data[f, year] for f in SUBFIELDS) != data[MATH, year]:
            raise ValueError(f"Mathematics subfields do not sum to total in {year}")
        if data[MATH, year] > data[TOTAL, year]:
            raise ValueError(f"Mathematics exceeds all doctorates in {year}")
    return data


def period_line(data, field):
    before = mean(data[field, y] for y in PRE)
    after = mean(data[field, y] for y in POST)
    return f"| {field} | {before:,.1f} | {after:,.1f} | {(after / before - 1) * 100:+.1f}% |"


def summary(data):
    lines = [
        "# U.S. research doctorates: descriptive comparison",
        "",
        "Source: NCSES Survey of Earned Doctorates 2025, Table 1-5 (fixed release).",
        "ChatGPT public launch: November 30, 2022. Survey year 2023 overlaps that date.",
        "",
        "## Annual recipients",
        "",
        "| Survey year | All research doctorates | Mathematics and statistics | Math/stat share | Computer and information sciences |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for year in range(START_YEAR, END_YEAR + 1):
        share = 100 * data[MATH, year] / data[TOTAL, year]
        lines.append(f"| {year} | {data[TOTAL, year]:,} | {data[MATH, year]:,} | {share:.2f}% | {data['Computer and information sciences', year]:,} |")
    lines += [
        "", "## Mean annual recipients", "",
        "Pre: 2015-2022 (8 survey years); later: 2023-2025 (3 survey years).",
        "Unequal windows, secular trends, and cohort lags limit interpretation.", "",
        "| Field | 2015-22 mean | 2023-25 mean | Relative difference |",
        "| --- | ---: | ---: | ---: |",
    ]
    for field in (TOTAL, MATH, "Computer and information sciences"):
        lines.append(period_line(data, field))
    lines += [
        "", "## Mathematics detail (exploratory)", "",
        "NCSES changed its field taxonomy in 2021. Do not infer a change in pure mathematics doctoral production from the 'Mathematics' label alone: its reported count moved substantially into other classifications before ChatGPT launched.",
        "", "| Field | 2015-22 mean | 2023-25 mean | Relative difference |",
        "| --- | ---: | ---: | ---: |",
    ]
    for field in SUBFIELDS:
        lines.append(period_line(data, field))
    lines += [
        "", "## Interpretation", "",
        "This is a timing comparison, not a causal estimate of ChatGPT's effect. Degrees awarded shortly after launch reflect years of prior study. COVID disruption, field recoding, enrollment, funding, and immigration could alter the counts. The aggregate mathematics and statistics series is more suitable for trend reading than the individual subfield labels.",
        "", "Original table: https://www.ncses.nsf.gov/pubs/nsf26326/assets/data-tables/tables/nsf26326-tab001-005.pdf",
        "Survey methods: https://www.ncses.nsf.gov/surveys/earned-doctorates/2025",
        "",
    ]
    return "\n".join(lines)


def svg_chart(data):
    width, height = 1000, 610
    panels = [(TOTAL, 75, 95, 420, 360, 50000, 60000, "#2456a6"),
              (MATH, 565, 95, 420, 360, 1700, 2400, "#bb5a32")]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Annual U.S. research doctorates, 2015 through 2025">',
           '<rect width="100%" height="100%" fill="#fbfaf7"/>',
           '<text x="60" y="42" font-size="26" font-family="sans-serif" fill="#1c2638">U.S. research doctorates, 2015-2025</text>',
           '<text x="60" y="65" font-size="14" font-family="sans-serif" fill="#526070">NCSES SED 2025 Table 1-5 | launch marker: November 2022</text>']
    for name, left, top, w, h, lo, hi, color in panels:
        xx = lambda y: left + (y - START_YEAR) * w / (END_YEAR - START_YEAR)
        yy = lambda n: top + h - (n - lo) * h / (hi - lo)
        for tick in range(lo, hi + 1, 2000 if name == TOTAL else 100):
            y = yy(tick)
            out += [f'<line x1="{left}" y1="{y:.1f}" x2="{left+w}" y2="{y:.1f}" stroke="#dfe3e8"/>',
                    f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-size="11" font-family="sans-serif" fill="#58616c">{tick:,}</text>']
        for yr in (2015, 2017, 2019, 2021, 2023, 2025):
            out.append(f'<text x="{xx(yr):.1f}" y="{top+h+25}" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#58616c">{yr}</text>')
        marker = xx(2022.5)
        out.append(f'<line x1="{marker:.1f}" y1="{top}" x2="{marker:.1f}" y2="{top+h}" stroke="#596e7d" stroke-dasharray="5 5"/>')
        points = " ".join(f"{xx(y):.1f},{yy(data[name, y]):.1f}" for y in range(START_YEAR, END_YEAR+1))
        out.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>')
        for y in range(START_YEAR, END_YEAR+1):
            out.append(f'<circle cx="{xx(y):.1f}" cy="{yy(data[name,y]):.1f}" r="4" fill="{color}"/>')
        out.append(f'<text x="{left}" y="{top-17}" font-size="18" font-family="sans-serif" font-weight="bold" fill="#1c2638">{escape(name)}</text>')
        out.append(f'<text x="{left+w}" y="{yy(data[name,2025])-10:.1f}" text-anchor="end" font-size="13" font-family="sans-serif" fill="{color}">{data[name,2025]:,}</text>')
    out += ['<line x1="60" y1="525" x2="940" y2="525" stroke="#dfe3e8"/>',
            '<text x="60" y="550" font-size="13" font-family="sans-serif" fill="#526070">Dashed line falls between survey years 2022 and 2023. The 2023 academic year overlaps the launch.</text>',
            '<text x="60" y="572" font-size="13" font-family="sans-serif" fill="#526070">Graduations reflect prior cohorts; these trends do not identify an AI effect.</text>', '</svg>']
    return "\n".join(out)


def main():
    data = read_data()
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    (output / "summary.md").write_text(summary(data), encoding="utf-8")
    (output / "trends.svg").write_text(svg_chart(data), encoding="utf-8")
    print("Wrote output/summary.md and output/trends.svg")


if __name__ == "__main__":
    main()
