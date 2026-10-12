# U.S. research doctorates before and after ChatGPT

An exploratory, reproducible look at annual U.S. research doctorate counts, with a focus on mathematics and statistics. The public release of ChatGPT on November 30, 2022 is the time marker, **not** an identified cause of any change.

## Quick start

```bash
python3 analysis.py
```

This uses only the Python standard library and writes `output/summary.md` and `output/trends.svg`. Open the SVG in a browser or GitHub. A short PDF overview is in [`report/overview.pdf`](report/overview.pdf); its source is `scripts/build_pdf.py` (requires `reportlab`).

## Questions

1. How many research doctorates did U.S. universities award each year from 2015 through 2025?
2. Did the trajectory in mathematics and statistics differ from the overall trajectory?
3. What can and cannot be learned by placing a November 2022 marker on these series?

## Data

`data/sed_2025_table_1_5.csv` transcribes selected rows from the **total recipients** block of NCSES, *Survey of Earned Doctorates 2025*, [Table 1-5 (PDF)](https://www.ncses.nsf.gov/pubs/nsf26326/assets/data-tables/tables/nsf26326-tab001-005.pdf). The [survey page](https://www.ncses.nsf.gov/surveys/earned-doctorates/2025) offers the original Excel download. The CSV records all research doctorates, mathematics and statistics, four reported mathematics/statistics subfields, and computer and information sciences for context. It is a fixed 2025 release snapshot; later revisions can differ from earlier publications.

The unit is **research doctorate recipients at U.S. institutions**, not all people with a PhD living in the U.S. and not professional doctorates such as MD or JD. The survey's 2025 academic year is July 1, 2024–June 30, 2025. The 2021 field classification change can affect detailed field comparisons. NCSES explicitly cautions about comparing field data across the change; the subfield series are exploratory.

## Study design

`analysis.py` compares the mean annual count in 2015–2022 with 2023–2025, and reports year-by-year counts and mathematics/statistics' share of the overall total. The 2023 survey year overlaps the launch date, and doctoral degrees generally reflect years of admission, training, funding, immigration, and labor-market decisions. COVID-era disruption and changing field codes are additional confounders. Three years after the launch are too few to measure a mature pipeline effect. The project makes **descriptive comparisons only**; no statistical causal claim is warranted.

## Mathematics-focused next steps

- Look separately at research doctorate admissions and first-year enrollments, which may respond before graduation counts. NCSES's [Graduate Students and Postdoctorates in Science and Engineering](https://ncses.nsf.gov/surveys/graduate-students-postdoctorates-s-e) is a candidate source, but its coverage is limited to science and engineering.
- Study mathematics and statistics postgraduation plans using SED Table 9-9, keeping academic employment and industry destinations distinct.
- Study dissertations' subject matter with a documented corpus and a stable classification protocol. Do not treat a keyword match for “AI” as evidence that ChatGPT caused a dissertation topic.
- Revisit the series as later SED years appear, ideally modeling admission cohorts and degree completion lags.

## Reproduce and extend

The CSV has `year`, `field`, `count`, and `source_table`. To extend it, add complete years for each field from a newer **single** SED table version, then update `END_YEAR` in `analysis.py`. Run `python3 analysis.py`; inspect the validation errors if a row is absent or duplicated. If adapting to the official workbook, record its table number, release date, taxonomy, and transformations.

## License and citation

Analysis code and prose: MIT (`LICENSE`). Public source data are attributed to NCSES; check the agency's terms for redistribution and cite the original source. Suggested citation: National Center for Science and Engineering Statistics, *Doctorate Recipients from U.S. Universities: 2025 Data Tables*, NSF 26-326, Table 1-5, September 25, 2026.
