# Human Mobility in Yogyakarta

Group project for Rekayasa Data (UGM): analysis and visualization of human mobility in the Special Region of Yogyakarta (DIY), December 2021 to April 2022.

- Plan, research questions and timeline: [PLAN.md](PLAN.md)
- Table and column definitions: [docs/data_dictionary.md](docs/data_dictionary.md)
- Writing and code rules for this repo: [docs/anti_slop_guidelines.md](docs/anti_slop_guidelines.md)

## Data sources

1. JogjaPulse: aggregated mobile-device presence for DIY, 1 Dec 2021 – 30 Apr 2022.
   Widyawan, Pratama, A. R., Ariansyah, A., Farda, N. M., Pramana, S., & Miller, O. (2026). JogjaPulse: An Aggregated Spatio-Temporal Mobility Dataset for Yogyakarta, Indonesia (v1). Zenodo. https://doi.org/10.5281/zenodo.23157460. License: CC BY 4.0.
2. Google COVID-19 Community Mobility Reports: daily % change against a Jan–Feb 2020 baseline for 6 place types, Special Region of Yogyakarta. Google LLC, https://www.google.com/covid19/mobility/ (accessed Nov 2026).
3. Holiday calendar: `data/raw/external/calendar_2021_2022.csv`, compiled from SKB 3 Menteri and Kemenag announcements. Each row states its source and whether it was checked.

The two mobility sources are collected and processed independently (see [docs/related_datasets.md](docs/related_datasets.md)).

## Running the pipeline

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/download_data.py          # JogjaPulse from Zenodo, MD5-checked
python src/fetch_google_mobility.py  # Google mobility, Indonesia files + DIY subset
python src/clean.py                  # typed, validated tables -> data/interim/
python src/build_features.py         # analysis tables -> data/processed/
```

`clean.py` and `build_features.py` stop with an error if a row count, key, join or share total doesn't match what's expected.

## Structure

```
data/raw/          source files (not committed, except the holiday calendar)
data/interim/      cleaned tables (generated)
data/processed/    analysis tables (generated)
notebooks/         01_eda.ipynb, then one notebook per research question
src/               pipeline scripts; config.py holds shared paths and constants
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
