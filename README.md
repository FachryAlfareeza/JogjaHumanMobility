# Human Mobility in Yogyakarta

Group project for Rekayasa Data (UGM): analysis and visualization of human mobility in the Special Region of Yogyakarta (DIY), December 2021 to April 2022.

The project has two outputs:

| Output | Question | Where |
|---|---|---|
| 1. How the two datasets relate | Does JogjaPulse (aggregated phone-device presence) move with Google's mobility reports, and how far can it be trusted? | `notebooks/01_eda.ipynb`, `notebooks/02_cross_validation.ipynb` |
| 2. Applied analytics | What does JogjaPulse show about Ramadan, daytime visits to the city, daily rhythm and holidays? | `notebooks/03`–`07`, dashboard `dashboard/app.py` |

Headline results so far (details and caveats in [PLAN.md](PLAN.md) sections 2 and 3):

- Output 1: JogjaPulse's Gunungkidul share and Google's parks index agree weakly to moderately once both are compared with the same weekday (Spearman r = 0.37, 95% CI 0.11–0.56); there is no clear agreement for stations or malls.
- Output 2: in the first three weeks of Ramadan 1443, the share of the day's device-hours at 03:00–04:59 rises from 3.7% to 8.1%. Kapanewon bordering Kota Yogyakarta send the largest share of their daytime visits into the city (Banguntapan 38.2%, Sewon 38.1%, Kasihan 35.5%).

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

Open `notebooks/07_daytime_visit_pairs.ipynb` and run it top-to-bottom to produce three
`reports/figures/rq4_*.png` figures. The notebook compares external home origins
with individual destinations inside Kota Yogyakarta for December–February.
It shows volume, origin-based visit rates, and stability across months.

Unpublished pair-months remain unknown, never zero. Main three-month comparisons
use pairs published in all three months. Rates pool the pair counts and matching
origin-device-month denominators; they are not percentages of residents.
Devices may appear in multiple destinations, so these results are neither
unique visitors to the whole city nor trip/commuter counts.

Generated tables are in `data/processed/daytime_visits/`; input hashes and quality
checks are in `quality.json`. A compact top-pair export is saved to
`reports/tables/rq4_top_pairs.csv`. This pair-level analysis complements the
origin-level city-share analysis in `notebooks/05_daytime_visits.ipynb`. The
existing Ramadan notebook (`06_ramadan.ipynb`) and dashboard are unchanged.

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
