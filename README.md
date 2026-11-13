# Human Mobility in Yogyakarta

Group project for Rekayasa Data (UGM): analysis and visualization of human mobility in the Special Region of Yogyakarta (DIY), December 2021 to April 2022.

The project has two outputs:

| Output | Question | Where |
|---|---|---|
| 1. How the two datasets relate | Does JogjaPulse (aggregated phone-device presence) move with Google's mobility reports, and how far can it be trusted? | `notebooks/01_eda.ipynb`, `notebooks/02_cross_validation.ipynb` |
| 2. Applied analytics | What does JogjaPulse show about Ramadan, daytime visits to the city, daily rhythm and holidays? | `notebooks/03`–`07`, dashboard `dashboard/app.py` |

Headline results so far (details and caveats in [PLAN.md](PLAN.md) sections 2 and 3):

- Output 1: JogjaPulse's Gunungkidul share and Google's parks index agree weakly to moderately once both are compared with the same weekday (Spearman r = 0.37, 95% CI 0.11–0.56); there is no clear agreement for stations or malls.
- Output 2: in 3–23 Apr 2022 versus 12 Mar–1 Apr, mean daily presence share at 03:00–04:59 rises from 2.5% to 7.5% in Banguntapan and 2.6% to 6.2% in Depok. Google DIY parks and retail/recreation indices are lower by 24.9 and 8.5 points; residential is higher by 2.6 points. These are observational period differences, not a causal Ramadan effect. In the pair-level daytime analysis, Banguntapan is observed more in Umbulharjo (20.5%) than Gondokusuman (7.3%), while Depok shows the reverse (5.3% and 10.0%). These are weighted device-month proportions of each origin's home-assigned sample for December–February; the destination ordering holds in each month.

- Plan, research questions and timeline: [PLAN.md](PLAN.md)
- Table and column definitions: [docs/data_dictionary.md](docs/data_dictionary.md)
- Writing and code rules for this repo: [docs/anti_slop_guidelines.md](docs/anti_slop_guidelines.md)

## Data sources

1. JogjaPulse: aggregated mobile-device presence for DIY, 1 Dec 2021 – 30 Apr 2022.
   Widyawan, Pratama, A. R., Ariansyah, A., Farda, N. M., Pramana, S., & Miller, O. (2026). JogjaPulse: An Aggregated Spatio-Temporal Mobility Dataset for Yogyakarta, Indonesia (v1). Zenodo. https://doi.org/10.5281/zenodo.23157460. License: CC BY 4.0.
2. Google COVID-19 Community Mobility Reports: daily % change against a Jan–Feb 2020 baseline for 6 place types, Special Region of Yogyakarta. Google LLC, https://www.google.com/covid19/mobility/ (accessed Nov 2026).
3. Holiday calendar: `data/raw/external/calendar_2021_2022.csv`, compiled from SKB 3 Menteri and Kemenag announcements. Each row states its source and whether it was checked.
4. Place coordinates (transit hubs, malls, beaches): `data/raw/external/places_osm.csv`, from OpenStreetMap via Nominatim by fixed OSM id (`src/fetch_places.py`). © OpenStreetMap contributors, ODbL.

The two mobility sources are collected and processed independently (see [docs/related_datasets.md](docs/related_datasets.md)).

## Running the pipeline

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/download_data.py          # JogjaPulse from Zenodo, MD5-checked
python src/fetch_google_mobility.py  # Google mobility, Indonesia files + DIY subset
python src/fetch_places.py           # OSM coordinates of transit hubs, malls, beaches
python src/clean.py                  # typed, validated tables -> data/interim/
python src/build_features.py         # analysis tables -> data/processed/
streamlit run dashboard/app.py       # Output 2 dashboard, opens in the browser
```

`clean.py` and `build_features.py` stop with an error if a row count, key, join or share total doesn't match what's expected.

### Daytime visits: output 2, first analysis

After the pipeline above, run:

```bash
python src/analyze_daytime_visits.py
python -m unittest discover -s tests -v
```

Open `notebooks/07_daytime_visit_pairs.ipynb` and run it top-to-bottom. Its main
question is whether the two origins with the largest pair-level connections
have different destination patterns, and whether the ordering holds each month.
The main figure is `reports/figures/rq4_destination_pattern.png`; three supporting
figures remain in the appendix. The scope is external home origins and individual
destinations inside Kota Yogyakarta for December–February, 08:00–17:59 WIB.

The short Indonesian narrative is in [docs/daytime_visit_insights.md](docs/daytime_visit_insights.md).
It separates observed results, possible explanations, and the use of the pairs
to focus later observation or surveys.

Unpublished pair-months remain unknown, never zero. Main three-month comparisons
use pairs published in all three months. Rates pool the pair counts and matching
origin-device-month denominators; they are not percentages of residents.
Devices may appear in multiple destinations, so these results are neither
unique visitors to the whole city nor trip/commuter counts.

Generated tables are in `data/processed/daytime_visits/`; input hashes and quality
checks are in `quality.json`. A compact top-pair export is saved to
`reports/tables/rq4_top_pairs.csv`. The notebook also exports the 12 focal
pair-month counts, denominators, rates and within-origin destination ranks to
`reports/tables/rq4_daytime_story_evidence.csv`, and checks their counts and
denominators directly against the raw source CSVs. This pair-level analysis complements the
origin-level city-share analysis in `notebooks/05_daytime_visits.ipynb`. The
Ramadan analysis is described below.

### Ramadan: timing and Google categories

Open `notebooks/06_ramadan.ipynb` after the pipeline and run top-to-bottom.
The main comparison includes all 21 days per period, preserving identical weekday
composition. The transition day 2 Apr is excluded. Only areas with all 24 hours
on every comparison day qualify; Banguntapan and Depok are the focal examples,
chosen from the daytime story, not from the largest Ramadan changes.

The main figure is `reports/figures/ramadan_story.png`. Supporting daily, weekly,
24-hour profile, coverage and sensitivity tables are `reports/tables/ramadan_*.csv`;
`ramadan_provenance.json` records input hashes and source reconciliation.
The Indonesian narrative is [docs/ramadan_insights.md](docs/ramadan_insights.md).
Notebook and dashboard use the same `ramadan_analysis` calculation in `src/applied.py`.

Wider hours (03:00–05:59), paired-Friday exclusion (25 Mar / 15 Apr), and a
midnight-excluded denominator preserve the focal increases. The pre-period already
trends upward; Gondomanan is sensitive to the hour block and denominator. Avoid
extending the focal conclusion to all DIY. Google covers DIY, has a different
population and baseline, and residential measures time at home. Its index changes
are not percentage changes in visit counts between the two periods. No 2021
comparison, full-Ramadan, Idul Fitri, transport-demand or business-opportunity claim
is made by this analysis.

## Structure

```
data/raw/          source files (not committed, except the holiday calendar)
data/interim/      cleaned tables (generated)
data/processed/    analysis tables (generated)
notebooks/         01-02 Output 1; 03-06 Output 2; 07 adds pair-level daytime visitation detail
src/               pipeline scripts; config.py holds shared paths and constants;
                   applied.py holds the Output 2 rules used by notebooks 03-06 and the dashboard
dashboard/         Streamlit app for Output 2
reports/figures/   exported figures
docs/              data dictionary, dataset survey, guidelines
video/, presentation/
```

## Team

| Name | NIM | Role |
|---|---|---|
| Muhammad Fachry Alfareeza | 24/540199/TK/59922 | |
| Rasyadwa Arsya Irnantyanto | 24/534714/TK/59283 | |
| Aqidatul Izzah | 24/533730/TK/59137 | |
| Yuki Shafa Maheswari | 24/545600/TK/60708 | |
| Amelia Ocha Maharani | 24/534372/TK/59229 | |
| Farand Hafiz | 24/540618/TK/60027 | |

Roles (LEAD, DE, AN, VIZ, MEDIA) are described in [PLAN.md](PLAN.md) section 3.
