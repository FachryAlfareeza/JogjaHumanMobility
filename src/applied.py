"""Shared calculations for the applied analyses (Output 2): notebooks 03-06 and the dashboard.

Each function holds one rule, so the notebooks and dashboard/app.py give the same numbers.
"""
import numpy as np
import pandas as pd

from config import CITY_KAB_CODE, RAMADAN_WINDOW_DAYS

MIN_COMPLETE_DAYS = 20     # complete 24-hour days a kapanewon needs for a stable profile
MIN_HOMED = 100            # home devices an OD origin needs in every month to be ranked
BASELINE_WEEKS = (-2, -1, 1, 2)


def complete_days(hourly: pd.DataFrame) -> pd.DataFrame:
    """Rows of kapanewon-days with all 24 hours published.

    A suppressed hour (< 5 devices) is missing, and in small kapanewon that happens mostly
    at night, so a profile averaged over incomplete days looks emptier at night than it is.
    """
    n = hourly.groupby(["kapanewon_code", "date"]).hour.transform("size")
    return hourly[n == 24]


def kapanewon_profiles(hourly: pd.DataFrame, by: list[str] | None = None) -> pd.DataFrame:
    """Mean share of the day per hour (%) for each kapanewon, from complete days only.

    `by` adds grouping columns (e.g. ["is_day_off"]). Each day counts once, whatever the
    panel size that day. Kapanewon with fewer than MIN_COMPLETE_DAYS complete days are dropped.
    """
    full = complete_days(hourly)
    n_full = full.groupby("kapanewon_code").date.nunique()
    full = full[full.kapanewon_code.isin(n_full.index[n_full >= MIN_COMPLETE_DAYS])]
    keys = ["kapanewon_code"] + (by or [])
    return full.groupby(keys + ["hour"]).share_of_own_day.mean().unstack("hour") * 100


def pooled_profile(hourly: pd.DataFrame, group: str | None = None) -> pd.DataFrame:
    """Share of the day per hour (%) for all kapanewon pooled (or per `group`), mean over days.

    Pooling many kapanewon keeps suppression small, so all days are used. Rows: dates
    (and group); columns: hours.
    """
    keys = ["date"] + ([group] if group else [])
    dh = hourly.groupby(keys + ["hour"]).n_maids.sum().unstack("hour", fill_value=0)
    return dh.div(dh.sum(axis=1), axis=0) * 100


def baseline_days(day: pd.Timestamp, daily: pd.DataFrame) -> list[pd.Timestamp]:
    """Same weekday 1 and 2 weeks either side, no holidays, same panel segment.

    Used for holiday shifts. Unlike build_features.weekday_deviation, the panel segment
    must match, so 1 Jan is not compared with December across a panel break.
    """
    cand = [day + pd.Timedelta(weeks=w) for w in BASELINE_WEEKS]
    return [c for c in cand if c in daily.index and not daily.is_holiday[c]
            and daily.panel_segment[c] == daily.panel_segment[day]]


def shifts(share: pd.DataFrame, daily: pd.DataFrame, relative: bool = False,
           min_days: int = 2) -> pd.DataFrame:
    """Shift of each day's shares from its baseline_days mean.

    `share` has dates as rows. relative=False gives percentage-point differences;
    relative=True gives log(day / baseline), with zero shares (fully suppressed) left out.
    """
    out = {}
    for day in share.index:
        b = baseline_days(day, daily)
        if len(b) < min_days:
            continue
        base = share.loc[b].mean()
        if relative:
            out[day] = np.log(share.loc[day].where(share.loc[day] > 0) / base)
        else:
            out[day] = share.loc[day] - base
    return pd.DataFrame(out).T


def city_visits(od: pd.DataFrame) -> pd.DataFrame:
    """Per origin and month: home devices, city visits, all away visits, city share and rate.

    city_rate  = sum of visit_rate over the city kapanewon (city kapanewon visited per home device)
    city_share = city visits / all visits outside the origin (%), which removes differences in how
                 much an origin's devices move at all, and the month-to-month rise in visit rates.
    """
    away = od[~od.is_intra]
    homed = od.drop_duplicates(["month", "origin_code"]).set_index(["origin_code", "month"]).n_homed_maids
    all_away = away.groupby(["origin_code", "month"]).n_maids.sum()
    city = (away[away.dest_kab_code == CITY_KAB_CODE].groupby(["origin_code", "month"]).n_maids.sum()
            .reindex(all_away.index, fill_value=0))
    out = pd.DataFrame({"home_devices": homed.reindex(all_away.index), "city_visits": city,
                        "away_visits": all_away})
    out["city_rate"] = out.city_visits / out.home_devices
    out["city_share"] = out.city_visits / out.away_visits * 100
    return out


def ranked_origins(od: pd.DataFrame) -> pd.Index:
    """Origins with at least MIN_HOMED home devices in every month."""
    homed = od.drop_duplicates(["month", "origin_code"]).pivot(index="origin_code", columns="month",
                                                               values="n_homed_maids")
    return homed.index[(homed >= MIN_HOMED).all(axis=1)]


def ramadan_windows(start: pd.Timestamp, days: int = RAMADAN_WINDOW_DAYS):
    """(before, during): the `days` days ending 2 days before `start`, and the first `days` days.

    The day before the government start is left out because Muhammadiyah started one day
    earlier in 2022 (2 Apr), so that day is a mix of both.
    """
    before = pd.date_range(end=start - pd.Timedelta(days=2), periods=days)
    during = pd.date_range(start=start, periods=days)
    return before, during
