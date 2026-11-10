"""Paths and constants shared by the pipeline scripts and notebooks."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_JP = ROOT / "data" / "raw" / "jogjapulse"
RAW_EXT = ROOT / "data" / "raw" / "external"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"

CALENDAR_CSV = RAW_EXT / "calendar_2021_2022.csv"
PLACES_CSV = RAW_EXT / "places_osm.csv"

STUDY_START = pd.Timestamp("2021-12-01")
STUDY_END = pd.Timestamp("2022-04-30")
N_DAYS = 151

# Breaks in the device panel reported in the JogjaPulse README (section 6).
PANEL_BREAKS = pd.to_datetime(["2022-01-01", "2022-02-16"])
PANEL_SEGMENTS = ["S1 Dec", "S2 1 Jan-15 Feb", "S3 16 Feb-Apr"]

KAB_ORDER = ["YOGYAKARTA", "SLEMAN", "BANTUL", "KULON PROGO", "GUNUNGKIDUL"]
N_KAPANEWON = 78

GOOGLE_CATEGORIES = ["retail_and_recreation", "grocery_and_pharmacy", "parks",
                     "transit_stations", "workplaces", "residential"]

# Grid cells containing a point on a 0.1 or 0.05 degree lattice hold 7-20x the presence
# of other cells (see notebooks/01_eda.ipynb section 5.1); likely rounded coordinates.
LATTICE_STEPS_DEG = (0.1, 0.05)
HALF_CELL_DEG = 0.00226  # about 250 m at this latitude

# OD months flagged reduced_quality in the source; analyses use the other months.
OD_GOOD_MONTHS = ["2021-12", "2022-01", "2022-02"]


def panel_segment(dates: pd.Series) -> pd.Series:
    """Label each date with its panel segment (S1, S2, S3)."""
    bins = [STUDY_START - pd.Timedelta(days=1), PANEL_BREAKS[0] - pd.Timedelta(days=1),
            PANEL_BREAKS[1] - pd.Timedelta(days=1), STUDY_END]
    return pd.cut(dates, bins=bins, labels=PANEL_SEGMENTS)
