# Human Mobility in Yogyakarta

Group project for Rekayasa Data (UGM), on human mobility analytics and visualization for the Special Region of Yogyakarta (DIY).

See [PLAN.md](PLAN.md) for the full plan, research questions and timeline.

## Data sources

1. **JogjaPulse**: aggregated spatio-temporal mobility dataset for Yogyakarta (Dec 2021 – Apr 2022).
   Widyawan, Pratama, A. R., Ariansyah, A., Farda, N. M., Pramana, S., & Miller, O. (2026). Zenodo. https://doi.org/10.5281/zenodo.23157460. License: CC BY 4.0.
2. **Google COVID-19 Community Mobility Reports**: daily % change vs baseline for 6 place types, Special Region of Yogyakarta, 2021–2022. Google LLC, https://www.google.com/covid19/mobility/ (accessed Nov 2026). Fetch it with `python src/fetch_google_mobility.py`.

More candidate sources are listed in [docs/related_datasets.md](docs/related_datasets.md).

## Structure

```
data/
  raw/jogjapulse/   original CSVs from Zenodo (not committed)
  raw/external/     second data source(s)
  interim/          cleaned parquet
  processed/        joined, analysis-ready tables
notebooks/          01_eda, 02_..., one per research question
src/                pipeline scripts
reports/figures/    exported charts and maps
dashboard/          optional Streamlit app
video/              script + final video
presentation/       slides for weeks 13-14
docs/               notes, data dictionary
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python src/download_data.py          # downloads + verifies JogjaPulse files
python src/fetch_google_mobility.py  # Google mobility, Indonesia + DIY subset
```

## Team

| Name | NIM | Role |
|---|---|---|
| | | |
