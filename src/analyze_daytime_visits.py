"""Daytime home-to-destination links, Dec–Feb; external origins into Kota Yogyakarta.

Run after clean.py and build_features.py: python src/analyze_daytime_visits.py
Missing published pairs stay unknown. Counts are not unique city visitors or trips.
"""
import hashlib
import json
from pathlib import Path

import pandas as pd

from config import INTERIM, OD_GOOD_MONTHS, PROCESSED, ROOT

KEY = ["month", "origin_code", "dest_code"]
PAIR = ["origin_code", "origin_kapanewon", "origin_kab_kota",
        "dest_code", "dest_kapanewon", "dest_kab_kota"]


def require_unique(frame: pd.DataFrame, keys: list[str], label: str) -> None:
    if frame[keys].isna().any().any() or frame.duplicated(keys).any():
        raise ValueError(f"{label}: missing or duplicate key {keys}")


def build_pair_month(od: pd.DataFrame, homes: pd.DataFrame, areas: pd.DataFrame,
                     months: list[str] | None = None) -> pd.DataFrame:
    """Explicit origin×destination×month grid; no zero imputation or name-only joins."""
    months = list(OD_GOOD_MONTHS if months is None else months)
    od, homes, areas = od.copy(), homes.copy(), areas.copy()
    od["month"], homes["month"] = od.month.astype(str), homes.month.astype(str)
    require_unique(areas, ["kapanewon_code"], "areas")
    require_unique(od, KEY, "OD")
    require_unique(homes, ["month", "origin_code"], "homes")
    if not set(od.month).issubset(months):
        raise ValueError("OD contains months outside the quality-approved window")
    known = set(areas.kapanewon_code)
    if not (set(od.origin_code) | set(od.dest_code)).issubset(known):
        raise ValueError("OD contains unknown area codes")
    if od.n_maids.isna().any() or (od.n_maids < 5).any() or (od.n_maids % 1 != 0).any():
        raise ValueError("Published OD counts must be integers >= 5")
    homes = homes[homes.month.isin(months)]
    if homes.n_homed_maids.isna().any() or (homes.n_homed_maids <= 0).any():
        raise ValueError("Home denominators must be positive")

    origin = areas.loc[areas.kab_kota.ne("YOGYAKARTA"), ["kapanewon_code", "kapanewon", "kab_kota"]]
    origin = origin.rename(columns={"kapanewon_code": "origin_code", "kapanewon": "origin_kapanewon", "kab_kota": "origin_kab_kota"})
    dest = areas.loc[areas.kab_kota.eq("YOGYAKARTA"), ["kapanewon_code", "kapanewon", "kab_kota"]]
    dest = dest.rename(columns={"kapanewon_code": "dest_code", "kapanewon": "dest_kapanewon", "kab_kota": "dest_kab_kota"})
    if origin.empty or dest.empty:
        raise ValueError("Need both external origins and Kota destinations")
    grid = pd.DataFrame({"month": months}).merge(origin, how="cross").merge(dest, how="cross")
    observed = od[[*KEY, "n_maids", "n_homed_maids"]].rename(columns={"n_homed_maids": "processed_home_count"})
    result = (grid.merge(observed, on=KEY, how="left", validate="one_to_one")
              .merge(homes[["month", "origin_code", "n_homed_maids"]],
                     on=["month", "origin_code"], how="left", validate="many_to_one"))
    if result.n_homed_maids.isna().any():
        raise ValueError("Missing origin-month home denominator")
    result["published"] = result.n_maids.notna()
    used = result.loc[result.published]
    if not used.processed_home_count.eq(used.n_homed_maids).all():
        raise ValueError("Processed OD and home denominator disagree")
    if (used.n_maids > used.n_homed_maids).any():
        raise ValueError("Pair count exceeds origin homes")
    result["n_maids"] = result.n_maids.astype("Int64")
    result["visit_rate"] = result.n_maids / result.n_homed_maids
    result["rank_count_month"] = result.groupby("month").n_maids.rank(method="min", ascending=False)
    result["rank_count_within_dest_month"] = result.groupby(["month", "dest_code"]).n_maids.rank(method="min", ascending=False)
    result["top3_month"] = result.rank_count_month.le(3).fillna(False)
    result = result.drop(columns="processed_home_count").sort_values(KEY).reset_index(drop=True)
    require_unique(result, KEY, "pair-month output")
    if len(result) != len(origin) * len(dest) * len(months):
        raise ValueError("Origin–destination grid lost or duplicated rows")
    return result


def summarize_pairs(pair_month: pd.DataFrame) -> pd.DataFrame:
    """Three-month rate = sum pair counts / sum corresponding origin-device-months.

    Primary mean/rate are null unless every study month is published for the pair.
    Ranking is by pair; denominators must never be summed across destinations.
    """
    expected = pair_month.month.nunique()
    summary = pair_month.groupby(PAIR, as_index=False).agg(
        months_expected=("month", "nunique"), months_published=("published", "sum"),
        observed_device_months=("n_maids", lambda s: s.sum(min_count=1)),
        origin_device_months=("n_homed_maids", "sum"),
        min_monthly_rate=("visit_rate", "min"), max_monthly_rate=("visit_rate", "max"),
        top3_months=("top3_month", "sum"))
    summary["complete_months"] = summary.months_published.eq(expected)
    summary["mean_devices_per_month"] = (summary.observed_device_months / expected).where(summary.complete_months)
    summary["pooled_visit_rate"] = (summary.observed_device_months / summary.origin_device_months).where(summary.complete_months)
    summary["pair_label"] = (summary.origin_kapanewon.str.title() + " (" + summary.origin_kab_kota.str.title()
                             + ") → " + summary.dest_kapanewon.str.title())
    return summary.sort_values(["mean_devices_per_month", "origin_code", "dest_code"],
                               ascending=[False, True, True], na_position="last").reset_index(drop=True)


def run_analysis() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    paths = {"od": PROCESSED / "od_dec_feb.parquet", "homes": INTERIM / "od_homes.parquet",
             "areas": INTERIM / "kapanewon_crosswalk.csv"}
    for path in paths.values():
        if not path.exists():
            raise FileNotFoundError(f"{path.name} missing; run clean.py and build_features.py first")
    od = pd.read_parquet(paths["od"])
    homes = pd.read_parquet(paths["homes"])
    areas = pd.read_csv(paths["areas"], dtype={"kapanewon_code": str})
    pairs = build_pair_month(od, homes, areas)
    summary = summarize_pairs(pairs)
    qa = {
        "months": OD_GOOD_MONTHS, "scope": "External home origins → individual Kota Yogyakarta daytime destinations",
        "unit": "MAIDs observed within each home-origin/destination/month; not trips or unique city visitors",
        "possible_pair_months": len(pairs), "published_pair_months": int(pairs.published.sum()),
        "unpublished_pair_months": int((~pairs.published).sum()), "possible_pairs": len(summary),
        "complete_three_month_pairs": int(summary.complete_months.sum()),
        "unpublished_counts_stay_null": bool(pairs.loc[~pairs.published, "n_maids"].isna().all()),
        "name_collision_pairs_retained": int((pairs.published & pairs.origin_kapanewon.eq(pairs.dest_kapanewon)).sum()),
        "rank_ties": "minimum rank; all pairs tied at rank 3 qualify for top3",
        "input_sha256": {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()},
    }
    target = PROCESSED / "daytime_visits"
    target.mkdir(exist_ok=True)
    pairs.to_parquet(target / "pair_month.parquet", index=False)
    summary.to_parquet(target / "pair_summary.parquet", index=False)
    (target / "quality.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    tables = ROOT / "reports" / "tables"
    tables.mkdir(exist_ok=True)
    summary.head(15).to_csv(tables / "rq4_top_pairs.csv", index=False)
    return pairs, summary, qa


if __name__ == "__main__":
    _, _, quality = run_analysis()
    print(json.dumps(quality, indent=2))
