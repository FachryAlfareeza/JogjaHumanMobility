# Data Dictionary

Pipeline: `src/clean.py` writes `data/interim/`, then `src/build_features.py` writes `data/processed/`. Notebooks should read `data/processed/`. All times are WIB (UTC+7). "Device" means a mobile advertising ID; it is not a person.

## Shared calendar columns

These appear in all processed tables except `od_dec_feb`.

| Column | Type | Meaning |
|---|---|---|
| `holiday_name` | str or null | Public holiday or collective leave on that date (from `data/raw/external/calendar_2021_2022.csv`) |
| `is_holiday` | bool | `holiday_name` is not null |
| `day_of_week` | int | 0 = Monday … 6 = Sunday |
| `is_weekend` | bool | Saturday or Sunday |
| `is_day_off` | bool | Weekend or holiday |
| `is_ramadan` | bool | On or after 3 Apr 2022 (government start of Ramadan 1443) |
| `panel_segment` | category | `S1 Dec`, `S2 1 Jan-15 Feb`, `S3 16 Feb-Apr`; splits at the two panel breaks in the JogjaPulse README |

## `daily_diy.parquet` (151 rows, one per day)

| Column | Meaning |
|---|---|
| `jp_presence_total` | Sum of `n_maids` over all kapanewon and hours (device-hours). Depends on panel size: don't compare across time. |
| `jp_night_presence` | Mean over 00–05 of summed `n_maids`. Tracks panel size. |
| `jp_pings_per_device_hour` | Total pings / total device-hours |
| `jp_city_daytime_share` | Kota Yogyakarta's share of DIY device-hours, 09–17 |
| `jp_share_<kabupaten>` | Kabupaten's share of DIY device-hours that day (5 columns, sum to 1) |
| `g_<category>` | Google % change vs the Jan–Feb 2020 weekday baseline (6 categories) |
| `dev_jp_<measure>` | log(value / baseline). Baseline = median of the same weekday 1 and 2 weeks before and after, leaving out the day itself and holidays; null if fewer than 2 such days (22 and 29 Apr 2022). Only for measures that don't depend on panel size. |
| `dev_g_<category>` | value − the same baseline |

## `hourly_kapanewon.parquet` (230,418 rows, one per kapanewon × date × hour with ≥ 5 devices)

| Column | Meaning |
|---|---|
| `kapanewon_code` | BPS-style code, e.g. `34.71.02`. Use this to join; names are not unique ("JETIS"). |
| `kab_kota`, `kapanewon` | Upper-case names |
| `date`, `hour`, `timestamp_wib` | Day, hour 0–23, and both combined |
| `n_maids`, `n_pings` | Distinct devices and pings in that hour (from source) |
| `share_of_diy_hour` | `n_maids` / sum over all kapanewon in that hour |
| `share_of_own_day` | `n_maids` / the kapanewon's total over that day (hourly profile) |
| `pop_actual` | Population from the JogjaPulse population file (BPS; reference year not stated in the source) |
| `devices_per_resident` | Devices with home in the kapanewon / `pop_actual` |

## `grid_daily.parquet` (183,548 rows, one per 500 m cell × day with ≥ 5 devices)

| Column | Meaning |
|---|---|
| `cell_id` | `E{i}_N{j}`, UTM 49S (EPSG:32749) |
| `x_min_utm`, `y_min_utm` | Lower-left corner in metres |
| `centroid_lon`, `centroid_lat` | WGS84 centroid |
| `n_maids` | Distinct devices that day |
| `lattice_artifact` | Cell contains a 0.1° or 0.05° lattice point (70 cells, about 8.6% of presence). Likely rounded coordinates. Exclude from hotspot analyses. |
| `share_of_diy_day` | `n_maids` / total over non-artifact cells that day. Null for artifact cells. |

## `od_dec_feb.parquet` (7,872 rows; Dec 2021 – Feb 2022 only)

| Column | Meaning |
|---|---|
| `month` | Period (YYYY-MM) |
| `origin_*`, `dest_*` | Home kapanewon and daytime-visit kapanewon (codes and names) |
| `n_maids` | Devices whose monthly home is the origin and that were seen in the destination 08:00–17:59 |
| `n_homed_maids` | Devices whose home is the origin that month |
| `visit_rate` | `n_maids / n_homed_maids` |
| `is_intra` | Origin equals destination |

March and April are excluded because the source flags them `reduced_quality`.

## Interim tables (`data/interim/`)

These are typed copies of the raw files, with names normalised and checked: `hourly_kapanewon`, `grid_daily`, `grid_cells`, `od_visits`, `od_homes`, `population`, `night_validation`, `google_diy`, `calendar`, plus `kapanewon_crosswalk.csv` (78 codes; `name_is_unique` is false for the two JETIS rows).
