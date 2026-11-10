"""Clean the raw inputs into typed tables in data/interim/.

Reads data/raw/jogjapulse/*.csv, the Google DIY subset and the holiday calendar.
Each table is checked against the row counts in the JogjaPulse README, its key
uniqueness and the study window before it is written.

Run: python src/clean.py
"""
import numpy as np
import pandas as pd

from config import (CALENDAR_CSV, GOOGLE_CATEGORIES, HALF_CELL_DEG, INTERIM, LATTICE_STEPS_DEG,
                    N_DAYS, N_KAPANEWON, RAW_EXT, RAW_JP, STUDY_END, STUDY_START)

CODE_COLS = {"kab_code": str, "kapanewon_code": str,
             "origin_kab_code": str, "origin_code": str, "dest_kab_code": str, "dest_code": str}

# Row counts stated in the JogjaPulse README, section 4.
EXPECTED_ROWS = {"presence_kapanewon_hourly": 230_418, "presence_cell500m_daily": 183_548,
                 "od_home_visits_kapanewon_monthly": 9_894, "od_origin_homes_monthly": 390,
                 "home_maids_vs_population_kapanewon": 78,
                 "validation_night_presence_kapanewon": 156}


def read_jp(name: str) -> pd.DataFrame:
    df = pd.read_csv(RAW_JP / f"{name}.csv", dtype=CODE_COLS)
    if len(df) != EXPECTED_ROWS[name]:
        raise ValueError(f"{name}: {len(df)} rows, README says {EXPECTED_ROWS[name]}")
    return df


def norm_name(s: pd.Series) -> pd.Series:
    return s.str.strip().str.upper().str.replace(r"\s+", " ", regex=True)


def assert_unique(df: pd.DataFrame, keys: list[str], name: str) -> None:
    dup = df.duplicated(keys).sum()
    if dup:
        raise ValueError(f"{name}: {dup} duplicate rows on {keys}")


def assert_window(dates: pd.Series, name: str) -> None:
    if dates.min() < STUDY_START or dates.max() > STUDY_END or dates.nunique() != N_DAYS:
        raise ValueError(f"{name}: dates {dates.min()}..{dates.max()}, {dates.nunique()} days")


def clean_hourly() -> pd.DataFrame:
    df = read_jp("presence_kapanewon_hourly")
    df["kab_kota"] = norm_name(df.kab_kota)
    df["kapanewon"] = norm_name(df.kapanewon)
    df["date"] = pd.to_datetime(df.date)
    df["hour"] = df.hour.astype("int8")
    df["timestamp_wib"] = df.date + pd.to_timedelta(df.hour, unit="h")
    df = df.astype({"n_maids": "int32", "n_pings": "int32"})
    assert_unique(df, ["kapanewon_code", "date", "hour"], "hourly")
    assert_window(df.date, "hourly")
    if df.kapanewon_code.nunique() != N_KAPANEWON:
        raise ValueError(f"hourly: {df.kapanewon_code.nunique()} kapanewon codes")
    if (df.n_maids < 5).any():
        raise ValueError("hourly: rows below the k = 5 threshold")
    return df


def build_crosswalk(hourly: pd.DataFrame, pop: pd.DataFrame, night: pd.DataFrame,
                    od: pd.DataFrame) -> pd.DataFrame:
    """One row per kapanewon code, with a check that every other file matches it."""
    xw = (hourly[["kab_code", "kab_kota", "kapanewon_code", "kapanewon"]]
          .drop_duplicates().sort_values("kapanewon_code").reset_index(drop=True))
    if xw.kapanewon_code.duplicated().any():
        raise ValueError("crosswalk: one code maps to two names")

    key = set(zip(xw.kab_kota, xw.kapanewon))
    for name, df, kab, kap in [("population", pop, "KAB_KOTA", "KEC_KAPN"),
                               ("night validation", night, "kab_kota", "kapanewon")]:
        missing = set(zip(norm_name(df[kab]), norm_name(df[kap]))) - key
        if missing:
            raise ValueError(f"{name}: names not in hourly file: {sorted(missing)}")

    od_codes = set(od.origin_code) | set(od.dest_code)
    if not od_codes <= set(xw.kapanewon_code):
        raise ValueError(f"OD: unknown codes {sorted(od_codes - set(xw.kapanewon_code))}")

    xw["name_is_unique"] = ~xw.kapanewon.duplicated(keep=False)
    return xw


def attach_code(df: pd.DataFrame, xw: pd.DataFrame, kab: str, kap: str) -> pd.DataFrame:
    out = df.assign(kab_kota=norm_name(df[kab]), kapanewon=norm_name(df[kap]))
    out = out.drop(columns=[c for c in (kab, kap) if c not in ("kab_kota", "kapanewon")])
    out = out.merge(xw[["kab_kota", "kapanewon", "kab_code", "kapanewon_code"]],
                    on=["kab_kota", "kapanewon"], how="left", validate="many_to_one")
    if out.kapanewon_code.isna().any():
        raise ValueError("attach_code: unmatched kapanewon")
    return out


def clean_grid() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = read_jp("presence_cell500m_daily")
    df["date"] = pd.to_datetime(df.date)
    df["n_maids"] = df.n_maids.astype("int32")
    assert_unique(df, ["cell_id", "date"], "grid")
    assert_window(df.date, "grid")

    cells = (df[["cell_id", "x_min_utm", "y_min_utm", "centroid_lon", "centroid_lat"]]
             .drop_duplicates().reset_index(drop=True))
    if cells.cell_id.duplicated().any():
        raise ValueError("grid: a cell_id has two sets of coordinates")
    on_lattice = np.zeros(len(cells), dtype=bool)
    for step in LATTICE_STEPS_DEG:
        dist = lambda v: np.abs(v / step - np.round(v / step)) * step  # noqa: E731
        on_lattice |= (dist(cells.centroid_lat) < HALF_CELL_DEG) & (dist(cells.centroid_lon) < HALF_CELL_DEG)
    cells["lattice_artifact"] = on_lattice
    return df[["cell_id", "date", "n_maids"]], cells


def clean_od() -> tuple[pd.DataFrame, pd.DataFrame]:
    visits = read_jp("od_home_visits_kapanewon_monthly")
    homes = read_jp("od_origin_homes_monthly")
    for df in (visits, homes):
        df["month"] = pd.PeriodIndex(df.month, freq="M")
        df["reduced_quality"] = df.reduced_quality.astype(bool)
        for c in [c for c in df.columns if c.endswith("kab_kota") or c.endswith("kapanewon")]:
            df[c] = norm_name(df[c])
    visits["n_maids"] = visits.n_maids.astype("int32")
    homes["n_homed_maids_daytime"] = homes.n_homed_maids_daytime.astype("Int32")  # blank when < 5
    assert_unique(visits, ["month", "origin_code", "dest_code"], "OD visits")
    assert_unique(homes, ["month", "origin_code"], "OD homes")
    return visits, homes


def clean_google() -> pd.DataFrame:
    g = pd.read_csv(RAW_EXT / "google_mobility" / "google_mobility_diy.csv", parse_dates=["date"])
    g = g.rename(columns=lambda c: c.replace("_percent_change_from_baseline", ""))
    g = g.loc[g.date.between(STUDY_START, STUDY_END), ["date"] + GOOGLE_CATEGORIES]
    assert_unique(g, ["date"], "google")
    assert_window(g.date, "google")
    if g[GOOGLE_CATEGORIES].isna().any().any():
        raise ValueError("google: missing values in the study window")
    return g.reset_index(drop=True)


def clean_calendar() -> pd.DataFrame:
    cal = pd.read_csv(CALENDAR_CSV, parse_dates=["date"])
    cal["verified"] = cal.verified.eq("yes")
    return cal


def main() -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)

    hourly = clean_hourly()
    pop = read_jp("home_maids_vs_population_kapanewon")
    night = read_jp("validation_night_presence_kapanewon")
    od_visits, od_homes = clean_od()
    xw = build_crosswalk(hourly, pop, night, od_visits)

    pop = attach_code(pop, xw, "KAB_KOTA", "KEC_KAPN").rename(
        columns={"n_users": "n_home_devices", "ratio": "devices_per_resident"})
    night = attach_code(night, xw, "kab_kota", "kapanewon")
    grid, cells = clean_grid()

    outputs = {"hourly_kapanewon": hourly, "grid_daily": grid, "grid_cells": cells,
               "od_visits": od_visits, "od_homes": od_homes, "population": pop,
               "night_validation": night, "google_diy": clean_google(),
               "calendar": clean_calendar()}
    for name, df in outputs.items():
        df.to_parquet(INTERIM / f"{name}.parquet", index=False)
        print(f"{name:18} {len(df):>8,} rows")
    xw.to_csv(INTERIM / "kapanewon_crosswalk.csv", index=False)
    print(f"{'kapanewon_crosswalk':18} {len(xw):>8,} rows "
          f"(names shared by two kabupaten: {sorted(xw.loc[~xw.name_is_unique, 'kapanewon'].unique())})")


if __name__ == "__main__":
    main()
