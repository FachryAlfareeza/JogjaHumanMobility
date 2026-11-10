# Project Plan: Human Mobility in Yogyakarta (Rekayasa Data)

Updated 10 Nov 2026. Done: both sources downloaded and checked, EDA (`notebooks/01_eda.ipynb`), cleaning pipeline (`src/clean.py`, `src/build_features.py`). Next: analysis notebooks 02–05.

Deadline assumption: week 13 starts Mon 23 Nov 2026, so the video goes on eLOK by Fri 20 Nov. This still needs confirming with the lecturer (see Risks).

Writing and code in this repo follow [docs/anti_slop_guidelines.md](docs/anti_slop_guidelines.md).

## 1. Data sources

| # | Source | Role | Level | Status |
|---|---|---|---|---|
| 1 | JogjaPulse (Zenodo 10.5281/zenodo.23157460, CC BY 4.0) | Main data | 500 m grid/day, kapanewon/hour, OD/month | Downloaded, 9 files MD5-checked |
| 2 | Google Community Mobility Reports, DIY | Independent cross-check | Province/day, % vs Jan–Feb 2020 baseline | Downloaded, 151 of 151 days |

Context layers:

| Layer | Decision | Status |
|---|---|---|
| Holiday calendar | Use | Done: 9 dated rows, 8 checked against sources, Nyepi not yet checked |
| PPKM level by date | Leave out for now | Sources disagree for Feb–Mar 2022 (reports range from level 2 to level 4); add only if a group member checks the Inmendagri texts |
| Kapanewon boundaries (HDX `cod-ab-idn`) | Use, for maps | Not started (T3) |
| Population | Use | Done: `pop_actual` from the JogjaPulse file, reference year not stated |
| Weather (Open-Meteo) | Optional | Only if on schedule by 15 Nov |
| POIs, WorldPop, Meta Movement Range | Skip | |

## 2. Research questions

| RQ | Question | Data | Method | Main figure |
|---|---|---|---|---|
| RQ1 Cross-validation | Does JogjaPulse's daily DIY pattern agree with Google's? | `daily_diy` (+ grid cells for transit, mall, beach) | Same-weekday deviation in both sources (2a); Spearman per pair; holiday case studies | Deviation time series with holidays marked; correlation heatmap |
| RQ2 Daily rhythm | How do hourly profiles differ between urban and rural kapanewon, and weekdays vs weekends? | `hourly_kapanewon` (`share_of_own_day`) | Cluster the 78 profiles (k-means, k = 3–4) | Hour × kapanewon heatmap; cluster map |
| RQ3 Holidays and tourism | Where does presence shift on holidays and long weekends? | `grid_daily` (artifact cells excluded) | Holiday share minus the mean of the same weekday 1 and 2 weeks before | Difference map; top-10 cells |
| RQ4 Commuting | Which kapanewon send daytime visitors to Kota Yogyakarta? | `od_dec_feb` | `visit_rate` by origin; top flows | Flow map or bar chart |

### 2a. RQ1 method

Compare each day with the median of the same weekday within ±2 weeks, in both sources: log ratio for JogjaPulse measures, difference for Google percentages. `build_features.py` computes these as the `dev_*` columns. Raw totals give a misleading r = −0.77 against Google residential, because the panel shrinks while residential rises.

| Google category | JogjaPulse measure | Spearman r so far |
|---|---|---|
| Parks | `jp_share_gunungkidul`; to try: coastal kapanewon or beach cells | 0.31 |
| Retail & recreation | Gondomanan + Gedongtengen daytime share; mall cells | 0.26 (using Gunungkidul share) |
| Transit stations | Cells at Tugu, Lempuyangan, Giwangan, YIA | Not tested |
| Workplaces | Weekday 08–17 vs 00–05 ratio | −0.01, not usable yet |
| Residential | Inverse day/night ratio | 0.18 with the wrong sign, not usable yet |
| General activity | `jp_pings_per_device_hour` | 0.31 retail, 0.31 transit, −0.32 residential |
| Grocery & pharmacy | No proxy | Skipped |

The 0.31 value is reproduced by `daily_diy.parquet`. The other values come from a quick check on 10 Nov and need confirming in `02_cross_validation.ipynb`. Current evidence supports "weak to moderate agreement, clearest on holidays".

Open items: build cell lists for stations, malls and beaches (artifact cells excluded); find a workplaces/residential measure; check why 25 Dec shows near-zero deviation.

### 2b. Normalisation rules

| Problem | Rule |
|---|---|
| Panel size changes (night presence peaks in Feb, April is 5.8× lower) | Don't compare raw `n_maids` across time |
| Panel geography drifts (Kota Yogyakarta share 11% in Dec, 25% in Apr) | Shares only for comparing places on the same day; across time, use `dev_*` columns or compare within one `panel_segment` |
| Suppression (k = 5) | Missing row means fewer than 5 devices, not zero |
| Lattice artifact (70 cells, 8.6% of presence) | Exclude `lattice_artifact` cells; `share_of_diy_day` already does |
| Duplicate kapanewon name (JETIS) | Join on `kapanewon_code` |
| Google is a % vs a 2020 weekday baseline | Compare deviations, not levels |
| Google is province-level | RQ1 at DIY/day level only |
| OD Mar–Apr flagged `reduced_quality` | `od_dec_feb` keeps Dec–Feb only |

## 3. Tasks

Roles: LEAD (repo, integration), DE (data), AN (analysis), VIZ, MEDIA (video, slides). Six members (names and NIMs in the README); with six people, DE and AN can each take two.

| ID | Task | Output | Owner | Depends on | Status |
|---|---|---|---|---|---|
| T1 | GitHub repo, add members | github.com/FachryAlfareeza/JogjaHumanMobility | LEAD | | Repo exists; add members |
| T2 | Holiday calendar | `data/raw/external/calendar_2021_2022.csv` | DE | | Done |
| T3 | Kapanewon boundaries (HDX), match to `kapanewon_code` | `data/raw/external/diy_kapanewon.geojson`, crosswalk column | DE | | Not started |
| T4 | Weather (optional) | `data/raw/external/weather_yogya_hourly.csv` | DE | | Optional |
| T5 | `src/clean.py` | `data/interim/*.parquet` | DE | | Done |
| T6 | Kapanewon crosswalk | `data/interim/kapanewon_crosswalk.csv` | DE | T5 | Done for JogjaPulse files; HDX column waits for T3 |
| T7–T10 | `src/build_features.py` | `data/processed/{daily_diy, hourly_kapanewon, grid_daily, od_dec_feb}.parquet` | DE | T2, T5 | Done |
| T11 | `01_eda.ipynb` | 16 figures `reports/figures/eda_*.png` | AN | | Done |
| T12 | `02_cross_validation.ipynb` (RQ1) | F4–F6, correlation table | AN | T7 | Next |
| T13 | `03_daily_rhythm.ipynb` (RQ2) | F7–F9 | AN | T8 | |
| T14 | `04_holiday_hotspots.ipynb` (RQ3) | F10–F12 | AN, VIZ | T9 | |
| T15 | `05_od_flows.ipynb` (RQ4) | F13–F14 | VIZ | T10, T3 for the map | |
| T16 | Final figures at 1920×1080 | `reports/figures/` | VIZ | T12–T15 | |
| T17 | Video script, about 700 words | `video/script.md` | MEDIA | T12–T15 | |
| T18 | Record and edit, 5:00 max | `video/final.mp4` (not committed) | MEDIA | T16, T17 | |
| T19 | Upload to eLOK | | LEAD | T18 | |
| T20 | Slides | `presentation/` | MEDIA | T16 | |
| T21 | Final README with results and video link | `README.md` | LEAD | T16 | |

## 4. Timeline

Critical path: T12 (RQ1), then T16, T17, T18, T19.

| Date | Milestone |
|---|---|
| Tue 10 Nov | Plan, EDA and pipeline done; roles assigned |
| Wed 11 Nov | T12 first pass; T3 boundaries |
| Thu 12 Nov | T13, T14 drafts |
| Fri 13 Nov | T12 result fixed (decides the video headline); T15 draft |
| Sat 14 – Sun 15 Nov | Finish T13–T15; optional T4 |
| Mon 16 Nov | All results frozen; T17 script draft |
| Tue 17 Nov | T16 final figures; script final |
| Wed 18 Nov | T18 record and edit |
| Thu 19 Nov | Group review of the cut |
| Fri 20 Nov | T19 upload (buffer 21–22 Nov) |
| 23 Nov – 4 Dec | T20 slides, T21 README, rehearsal, presentation |

## 5. Notebooks

All notebooks after 01 read `data/processed/` and import constants from `src/config.py`.

| Notebook | Figures | Video segment |
|---|---|---|
| `01_eda.ipynb` (done) | `eda_panel_decay`, `eda_raw_vs_share`, `eda_representativeness`, `eda_grid_lattice_artifacts`, `eda_heatmap_hour_weekday`, `eda_od_kabupaten_matrix`, `eda_jp_vs_google_parks` | 0:30–1:15 data and caveats |
| `02_cross_validation.ipynb` | F4 deviation series (Gunungkidul share vs parks); F5 correlation heatmap; F6 raw vs adjusted correlation | 1:15–2:15 |
| `03_daily_rhythm.ipynb` | F7 hour × kapanewon heatmap; F8 cluster map; F9 weekday vs weekend by cluster | 2:15–3:00 |
| `04_holiday_hotspots.ipynb` | F10 share series with holidays; F11 difference map; F12 top cells | 3:00–3:45 |
| `05_od_flows.ipynb` | F13 flows into Kota Yogyakarta; F14 top origins | 3:45–4:20 |
| Video only | Pipeline diagram; limitations slide | 0:30–1:15; 4:20–4:45 |

## 6. Risks and open questions

| Risk | Impact | Mitigation |
|---|---|---|
| eLOK deadline not confirmed | Whole schedule | LEAD confirms this week; plan targets 20 Nov |
| RQ1 agreement stays weak | Headline changes | Report it as found, with reasons (panel drift, opt-in differences); test per panel segment |
| Lattice artifact | Fake hotspots | Excluded in `grid_daily`; shown as a limitation |
| Panel size and geography drift | Fake trends | Rules in 2b |
| HDX names vs JogjaPulse names | Map joins fail | T3 matches on code where possible, then names, with an assertion of 0 unmatched |
| `pop_actual` reference year unknown | Weaker per-capita claims | Label as "BPS, year not stated in JogjaPulse" |
| PPKM levels unverified | Can't explain policy effects | Left out; mention as a limitation if needed |
| Nyepi date not checked against SKB text | Minor | Check before using Nyepi in a figure |
| Video longer than 5:00 | Penalty | Script capped at about 700 words; timed at the 19 Nov review |
| Uneven contribution | Grading | Each task has an owner who commits their own work |

## Next 3 actions

1. LEAD: confirm the eLOK deadline, assign the roles in the README team table (6 members), add members to the GitHub repo.
2. AN: start `02_cross_validation.ipynb` from `data/processed/daily_diy.parquet` and test the transit, mall and beach cell measures.
3. DE: T3, fetch HDX kapanewon boundaries and add their code to the crosswalk.
