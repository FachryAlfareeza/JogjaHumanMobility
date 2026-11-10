"""Build analysis-ready tables in data/processed/ from data/interim/.

Outputs (columns documented in docs/data_dictionary.md):
  daily_diy.parquet          one row per day: JogjaPulse DIY measures, Google categories,
                             calendar flags, and same-weekday deviations for RQ1
  hourly_kapanewon.parquet   kapanewon x hour presence with shares, calendar, population
  grid_daily.parquet         500 m cell x day presence with shares and the lattice flag
  od_dec_feb.parquet         home -> daytime-visit flows for the months not flagged reduced_quality

Run: python src/build_features.py   (after src/clean.py)
"""
import numpy as np
import pandas as pd

from config import (GOOGLE_CATEGORIES, INTERIM, KAB_ORDER, N_DAYS, N_KAPANEWON,
                    OD_GOOD_MONTHS, PROCESSED, panel_segment)

NIGHT_HOURS = range(0, 6)
DAY_HOURS = range(9, 18)
HOLIDAY_TYPES = {"public_holiday", "collective_leave"}


def weekday_deviation(df: pd.DataFrame, log_ratio: bool, window: int = 5) -> pd.DataFrame:
    """Deviation of each day from the median of the same weekday in the surrounding weeks.

    window=5 means the day itself plus two of the same weekday on each side (+-2 weeks).
    JogjaPulse measures use log(value / baseline); Google's % values use value - baseline,
    because Google is already a % change against a weekday-specific 2020 baseline.
    """
    df = df.astype(float)
    out = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
    for wd in range(7):
        idx = df.index[df.index.day_of_week == wd]
        base = df.loc[idx].rolling(window, center=True, min_periods=3).median()
        out.loc[idx] = np.log(df.loc[idx] / base) if log_ratio else df.loc[idx] - base
    return out


def calendar_by_date(cal: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DataFrame({"date": pd.date_range("2021-12-01", "2022-04-30")})
    hol = cal[cal.type.isin(HOLIDAY_TYPES)]
    out = dates.merge(hol[["date", "name"]].rename(columns={"name": "holiday_name"}),
                      on="date", how="left", validate="one_to_one")
    out["is_holiday"] = out.holiday_name.notna()
    out["day_of_week"] = out.date.dt.day_of_week.astype("int8")
    out["is_weekend"] = out.day_of_week >= 5
    out["is_day_off"] = out.is_weekend | out.is_holiday
    ramadan_start = cal.loc[cal.name.str.contains("government"), "date"].iloc[0]
    out["is_ramadan"] = out.date >= ramadan_start
    out["panel_segment"] = panel_segment(out.date)
    return out


def build_daily(hourly: pd.DataFrame, google: pd.DataFrame, cal: pd.DataFrame) -> pd.DataFrame:
    by_dh = hourly.groupby(["date", "hour"]).n_maids.sum().unstack()
    day_hours = hourly[hourly.hour.isin(DAY_HOURS)]
    kab = hourly.groupby(["date", "kab_kota"]).n_maids.sum().unstack()[KAB_ORDER]

    jp = pd.DataFrame({
        "jp_presence_total": by_dh.sum(axis=1),
        "jp_night_presence": by_dh[list(NIGHT_HOURS)].mean(axis=1),
        "jp_pings_per_device_hour": hourly.groupby("date").n_pings.sum() / hourly.groupby("date").n_maids.sum(),
        "jp_city_daytime_share": (day_hours[day_hours.kab_kota == "YOGYAKARTA"].groupby("date").n_maids.sum()
                                  / day_hours.groupby("date").n_maids.sum()),
    })
    for k in KAB_ORDER:
        jp[f"jp_share_{k.lower().replace(' ', '_')}"] = kab[k] / kab.sum(axis=1)

    g = google.set_index("date")[GOOGLE_CATEGORIES].add_prefix("g_")

    # Deviations only for measures that don't depend on panel size (not the raw totals).
    jp_rel = jp.drop(columns=["jp_presence_total", "jp_night_presence"])
    dev = pd.concat([weekday_deviation(jp_rel, log_ratio=True).add_prefix("dev_"),
                     weekday_deviation(g, log_ratio=False).add_prefix("dev_")], axis=1)

    daily = calendar_by_date(cal).set_index("date").join(jp).join(g).join(dev).reset_index()
    if len(daily) != N_DAYS or daily[jp.columns.tolist() + g.columns.tolist()].isna().any().any():
        raise ValueError("daily: missing days or values")
    share_cols = [c for c in daily.columns if c.startswith("jp_share_")]
    if not np.allclose(daily[share_cols].sum(axis=1), 1):
        raise ValueError("daily: kabupaten shares don't sum to 1")
    return daily


def build_hourly(hourly: pd.DataFrame, pop: pd.DataFrame, cal_d: pd.DataFrame) -> pd.DataFrame:
    h = hourly.drop(columns=["kab_code"]).copy()
    h["share_of_diy_hour"] = h.n_maids / h.groupby(["date", "hour"]).n_maids.transform("sum")
    h["share_of_own_day"] = h.n_maids / h.groupby(["kapanewon_code", "date"]).n_maids.transform("sum")
    h = h.merge(pop[["kapanewon_code", "pop_actual", "devices_per_resident"]],
                on="kapanewon_code", how="left", validate="many_to_one")
    h = h.merge(cal_d, on="date", how="left", validate="many_to_one")
    if not np.allclose(h.groupby(["date", "hour"]).share_of_diy_hour.sum(), 1):
        raise ValueError("hourly: DIY shares don't sum to 1")
    if h.pop_actual.isna().any():
        raise ValueError("hourly: kapanewon without population")
    return h


def build_grid(grid: pd.DataFrame, cells: pd.DataFrame, cal_d: pd.DataFrame) -> pd.DataFrame:
    g = grid.merge(cells, on="cell_id", how="left", validate="many_to_one")
    clean = ~g.lattice_artifact
    # Share among non-artifact cells only, so artifact cells don't shrink everyone else's share.
    g["share_of_diy_day"] = np.where(
        clean, g.n_maids / g[clean].groupby("date").n_maids.sum().reindex(g.date).to_numpy(), np.nan)
    g = g.merge(cal_d, on="date", how="left", validate="many_to_one")
    if not np.allclose(g.groupby("date").share_of_diy_day.sum(), 1):
        raise ValueError("grid: shares don't sum to 1")
    return g


def build_od(visits: pd.DataFrame, homes: pd.DataFrame) -> pd.DataFrame:
    keep = visits.month.astype(str).isin(OD_GOOD_MONTHS)
    od = visits[keep].merge(homes[["month", "origin_code", "n_homed_maids"]],
                            on=["month", "origin_code"], how="left", validate="many_to_one")
    if od.n_homed_maids.isna().any():
        raise ValueError("OD: origins without a homed-device count")
    od["visit_rate"] = od.n_maids / od.n_homed_maids
    od["is_intra"] = od.origin_code == od.dest_code
    if (od.visit_rate > 1).any():
        raise ValueError("OD: more visitors than homed devices")
    return od.drop(columns=["reduced_quality"])


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    read = lambda name: pd.read_parquet(INTERIM / f"{name}.parquet")  # noqa: E731
    hourly, cal = read("hourly_kapanewon"), read("calendar")
    cal_d = calendar_by_date(cal)

    outputs = {
        "daily_diy": build_daily(hourly, read("google_diy"), cal),
        "hourly_kapanewon": build_hourly(hourly, read("population"), cal_d),
        "grid_daily": build_grid(read("grid_daily"), read("grid_cells"), cal_d),
        "od_dec_feb": build_od(read("od_visits"), read("od_homes")),
    }
    if outputs["hourly_kapanewon"].kapanewon_code.nunique() != N_KAPANEWON:
        raise ValueError("hourly: kapanewon lost in the join")
    for name, df in outputs.items():
        df.to_parquet(PROCESSED / f"{name}.parquet", index=False)
        print(f"{name:17} {len(df):>8,} rows x {df.shape[1]} cols")


if __name__ == "__main__":
    main()
