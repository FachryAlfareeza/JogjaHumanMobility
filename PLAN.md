# Project Plan: Human Mobility in Yogyakarta (Rekayasa Data)

Updated 12 Nov 2026. The project now delivers two outputs (section 0). Done: both sources downloaded and checked, EDA, cleaning pipeline, Output 1 (`notebooks/02_cross_validation.ipynb`), first pass of all four Output 2 analyses (`notebooks/03`–`06`) and the dashboard (`dashboard/app.py`). Next: group review of Output 2, T3 boundaries for maps, T16 figures, T17 script.

Deadline assumption: week 13 starts Mon 23 Nov 2026, so the video goes on eLOK by Fri 20 Nov. This still needs confirming with the lecturer (see Risks).

Writing and code in this repo follow [docs/anti_slop_guidelines.md](docs/anti_slop_guidelines.md).

## 0. Two outputs

| | Output 1: how the two datasets relate | Output 2: applied analytics |
|---|---|---|
| Question | Does JogjaPulse (device pings) move with Google's mobility reports, and how far can it be trusted? | What can a planner learn from JogjaPulse about when and where people in DIY move? |
| Notebooks | `01_eda`, `02_cross_validation` | `03_daily_rhythm`, `04_holiday_hotspots`, `05_daytime_visits`, `06_ramadan` |
| Product | Figures `eda_*`, `rq1_*` | Figures `rhythm_*`, `holiday_*`, `visits_*`, `ramadan_*`; Streamlit dashboard `dashboard/app.py` |
| Video share | about 2:00 | about 2:30 |

Output 1 sets the limits of Output 2: JogjaPulse agrees weakly to moderately with Google on one leisure proxy (Gunungkidul share vs parks); the selected station and mall cells show no clear agreement, and the day/night proxy tested shows no weekday/weekend contrast. So Output 2 leans on timing (hour-of-day shares) and on leisure, and calls OD flows "daytime visits", not commuting.

Shared rules for Output 2 (complete-day profiles, holiday baseline, city visit share, Ramadan windows) live in `src/applied.py`, which both the notebooks and the dashboard import.

## 1. Data sources

| # | Source | Role | Level | Status |
|---|---|---|---|---|
| 1 | JogjaPulse (Zenodo 10.5281/zenodo.23157460, CC BY 4.0) | Main data | 500 m grid/day, kapanewon/hour, OD/month | Downloaded, 9 files MD5-checked |
| 2 | Google Community Mobility Reports, DIY | Independent cross-check (Output 1); second view of Ramadan (Output 2) | Province/day, % vs Jan–Feb 2020 baseline | Downloaded, 151 of 151 days; 2021 also used for Ramadan 1442 |

Context layers:

| Layer | Decision | Status |
|---|---|---|
| Holiday calendar | Use | Done: 9 dated rows, 8 checked against sources, Nyepi not yet checked |
| Ramadan 1442 start (13 Apr 2021) | Use, for the Google 2021 comparison | Done: `config.RAMADAN_2021_START`, checked against the government isbat result (setkab.go.id) |
| PPKM level by date | Leave out for now | Sources disagree for Feb–Mar 2022 (reports range from level 2 to level 4); add only if a group member checks the Inmendagri texts |
| Kapanewon boundaries (HDX `cod-ab-idn`) | Use, for maps | Not started (T3) |
| Population | Use | Done: `pop_actual` from the JogjaPulse file, reference year not stated |
| Weather (Open-Meteo) | Optional | Only if on schedule by 15 Nov |
| POIs, WorldPop, Meta Movement Range | Skip | |

## 2. Output 1: JogjaPulse vs Google

| Question | Data | Method | Main figure |
|---|---|---|---|
| Does JogjaPulse's daily DIY pattern agree with Google's? | `daily_diy` (+ grid cells for transit, mall, beach) | Same-weekday deviation in both sources (2a); Spearman per pair; holiday case studies | `rq1_deviation_series`, `rq1_corr_heatmap`, `rq1_raw_vs_adjusted` |

### 2a. Method

Compare each day with the median of the same weekday 1 and 2 weeks before and after, in both sources, leaving out the day itself and holidays: log ratio for JogjaPulse measures, difference for Google percentages. `build_features.py` computes these as the `dev_*` columns. Raw totals give a misleading r = −0.77 against Google residential, because the panel shrinks while residential rises.

The baseline used to include the day itself, which gave 36 days an exact-zero deviation in Gunungkidul share and hid holidays such as 25 Dec (notebook 02 section 1). Fixed in `build_features.py` on 10 Nov; 22 and 29 Apr now have no baseline. Since 13 Nov each column also needs at least 2 non-missing baseline values (before, a day could get a "median" of one value when a neighbour was suppressed); this removes one more day from the coastal measure (147 days, r 0.27 → 0.26) and changes nothing in `daily_diy`.

Results from `02_cross_validation.ipynb` (Spearman, DIY, 95% CI from a 14-day block bootstrap):

| Google category | JogjaPulse measure | r | 95% CI | Holidays same sign |
|---|---|---|---|---|
| Parks | Gunungkidul share | 0.37 | 0.11 to 0.56 | 5 of 6 |
| Parks | Coastal kapanewon share (Kretek, Tanjungsari, Tepus) | 0.26 | −0.05 to 0.52 | 5 of 6 |
| Transit stations | Share of cells within 500 m of Tugu, Lempuyangan, Jombor (OSM) | 0.19 | −0.07 to 0.41 | 3 of 6 |
| Retail & recreation | Share of cells at 5 malls (OSM) | 0.03 | −0.14 to 0.21 | 4 of 6 |
| Retail & recreation | Pings per device-hour | 0.27 | 0.12 to 0.53 | |
| Workplaces, residential | Day/night kapanewon dissimilarity | −0.16, −0.04 | | |
| Grocery & pharmacy | No proxy | | | |

Conclusion (notebook 02 section 9):

- Two matched pairs have a 95% interval that excludes zero, and they mean different things. Gunungkidul share vs parks (0.37) is a geographic proxy: where devices are. Pings per device-hour vs retail (0.27) is an intensity proxy that likely reflects app use, not shop visits.
- Gunungkidul share and Google parks moved the same way on 5 of 6 holidays. That describes the holidays; whether agreement is stronger on holidays than on other days has not been tested, so don't say "clearest on holidays".
- The selected station cells (7 cells around Tugu, Lempuyangan, Jombor) and mall cells (9 cells at 5 malls) show no clear agreement. A 500 m cell also holds the surrounding neighbourhood, so this applies to these proxies, not to transit or retail in DIY.
- The tested day/night proxy (kapanewon dissimilarity 09–17 vs 00–05) shows no clear weekday/weekend contrast (0.190–0.205 on every weekday). That doesn't prove JogjaPulse has no commuting signal, but this proxy can't validate workplaces or residential.
- Gunungkidul share correlates about equally with Google parks, retail and transit, so read it as "out-of-home activity on days off", not parks specifically. Agreement is higher in the last panel segment (r = 0.46 from 16 Feb) than in December (0.17).
- The raw −0.77 (total device-hours vs residential) is a different pair from the 0.37. To show what the adjustment does, use pairs with both values: transit cells −0.39 → 0.19, mall cells −0.34 → 0.03.

Beach grid cells are suppressed on most days (Parangtritis is published on 14 of 151), so beaches use coastal kapanewon. Giwangan, the airports and Jogja City Mall cells are partly excluded for being published on fewer than 140 days.

## 3. Output 2: applied analytics

Ordered by strength of result, which is also the order for the video.

| # | Topic | Notebook | Question | Result (first pass, 12 Nov) | Caveat |
|---|---|---|---|---|---|
| A1 | Ramadan | `06_ramadan` | How do daily timing and place visits change in Ramadan 1443? | The 03:00–04:59 share of the day rises from 3.7% to 8.1% (first 3 weeks vs 3 weeks before), stepping up on 2–3 Apr; it rose in all 16 kapanewon with enough data and in every kabupaten. Google: parks −25.8, transit −11.4, retail −8.8 pp, residential +2.2; Ramadan 2021 has the same signs, and a placebo 3 weeks earlier moves the other way. JogjaPulse Gunungkidul share −29.5% (placebo +3.2%), the same direction as Google parks. | One Ramadan in JogjaPulse. The 00–02 drop (11.3% to 5.9%) is local: Gondomanan held 44.6% of DIY 00–02 device-hours before Ramadan. Data ends before Idul Fitri. |
| A2 | Daytime visits to the city | `05_daytime_visits` | Where do Kota Yogyakarta's daytime visitors live, and which city kapanewon do they visit? | Neighbouring kapanewon send the largest share of their daytime visits to the city: Banguntapan 38.2%, Sewon 38.1%, Kasihan 35.5%, Depok 28.8%, Gamping 27.2%. Kabupaten medians: Sleman 15.2%, Bantul 13.9%, Kulon Progo 10.6%, Gunungkidul 9.3%. Most visited: Umbulharjo, Gondokusuman. | Dec–Feb only. A "daytime visit" (08–17, once a month) is not commuting; Output 1's day/night proxy showed no weekday contrast. Visit rates double Dec–Feb (panel), so the city share is the quoted measure. |
| A3 | Daily rhythm | `03_daily_rhythm` | At what hours is each kapanewon busy, and what changes on days off? | Profiles are very similar across kapanewon (k-means k = 2, silhouette 0.67, separates only 4 kapanewon with a 01:00–02:00 peak). Median night share 13.2% in Kota Yogyakarta vs 10.5% in Gunungkidul. On days off, share moves from daytime to night, most in the city (daytime −2.68 pp, night +2.24 pp). | Complete 24-hour days only; 13 kapanewon (10 in Gunungkidul) have too few. Night share correlates with devices per day (Spearman 0.36). |
| A4 | Holidays | `04_holiday_hotspots` | Which places gain on public holidays? | No hotspot at 500 m: redistribution 26.1% on holidays vs 24.2% on ordinary weekends; the top cell (1.16 pp) is below the placebo 95th percentile (2.42 pp). Kokap (+46%, up on 6 of 6 holidays) and Gedongtengen (+20%) beat the placebo; 2 of 78 is about what chance gives. Gunungkidul kapanewon gain 11.8% on average. | Baseline is ±1, ±2 weeks within the same panel segment. 29 Apr has no baseline. Mostly a negative result. |

The dashboard (`streamlit run dashboard/app.py`) has one tab per topic plus a tab that summarises Output 1. Each tab says which notebook its numbers come from.

### 3b. Normalisation rules (both outputs)

| Problem | Rule |
|---|---|
| Panel size changes (night presence peaks in Feb, April is 5.8× lower) | Don't compare raw `n_maids` across time |
| Panel geography drifts (Kota Yogyakarta share 11% in Dec, 25% in Apr) | Shares only for comparing places on the same day; across time, use `dev_*` columns, compare within one `panel_segment`, or use a placebo window |
| Suppression (k = 5) | Missing row means fewer than 5 devices, not zero; kapanewon profiles use complete 24-hour days |
| Lattice artifact (70 cells, 8.6% of presence) | Exclude `lattice_artifact` cells; `share_of_diy_day` already does |
| Duplicate kapanewon name (JETIS) | Join on `kapanewon_code` |
| Google is a % vs a 2020 weekday baseline | Compare deviations or same-length windows with the same weekday mix, not levels |
| Google is province-level | Google comparisons at DIY/day level only |
| OD Mar–Apr flagged `reduced_quality` | `od_dec_feb` keeps Dec–Feb only |

## 4. Tasks

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
| T11 | `01_eda.ipynb` (Output 1) | 16 figures `eda_*` | AN | | Done |
| T12 | `02_cross_validation.ipynb` (Output 1) | `rq1_*` | AN | T7 | Done |
| T13 | `03_daily_rhythm.ipynb` (A3) | `rhythm_*` | AN | T8 | First pass done; cluster map waits for T3 |
| T14 | `04_holiday_hotspots.ipynb` (A4) | `holiday_*` | AN, VIZ | T9 | First pass done |
| T15 | `05_daytime_visits.ipynb` (A2) | `visits_*` | VIZ | T10, T3 for the map | First pass done; flow map waits for T3 |
| T22 | `06_ramadan.ipynb` (A1) | `ramadan_*` | AN | T8 | First pass done |
| T23 | Dashboard | `dashboard/app.py` | VIZ, LEAD | T13–T15, T22 | First version runs; needs group review |
| T16 | Final figures at 1920×1080 | `reports/figures/` | VIZ | T12–T15, T22 | |
| T17 | Video script, about 650 words | `presentation/slides_plan.md` section 3 | MEDIA | T12–T15, T22 | Draft follows the two-output structure |
| T18 | Record and edit, 5:00 max (include a 20 s dashboard screen recording) | `video/final.mp4` (not committed) | MEDIA | T16, T17, T23 | |
| T19 | Upload to eLOK | | LEAD | T18 | |
| T20 | Slides | `presentation/` | MEDIA | T16 | |
| T21 | Final README with results and video link | `README.md` | LEAD | T16 | |

## 5. Timeline

Critical path: Output 2 review, then T16, T17, T18, T19.

| Date | Milestone |
|---|---|
| Tue 10 Nov | Plan, EDA and pipeline done; roles assigned |
| Thu 12 Nov | Output 1 done; Output 2 first pass (A1–A4) and dashboard |
| Fri 13 Nov | Group reviews Output 2; T3 boundaries |
| Sat 14 – Sun 15 Nov | Maps (if T3 is done); optional T4 |
| Mon 16 Nov | All results frozen; T17 script final draft |
| Tue 17 Nov | T16 final figures; script final |
| Wed 18 Nov | T18 record and edit |
| Thu 19 Nov | Group review of the cut |
| Fri 20 Nov | T19 upload (buffer 21–22 Nov) |
| 23 Nov – 4 Dec | T20 slides, T21 README, rehearsal, presentation (live dashboard demo) |

## 6. Risks and open questions

| Risk | Impact | Mitigation |
|---|---|---|
| eLOK deadline not confirmed | Whole schedule | LEAD confirms this week; plan targets 20 Nov |
| Output 1 agreement is weak | Output 2 claims could overreach | Output 2 leans on timing and leisure, where Output 1 found agreement, and checks each result against a placebo window |
| Ramadan result rests on one Ramadan in JogjaPulse | Could be season or panel | Google 2021 comparison and placebo windows (notebook 06 §4b); state it as one Ramadan |
| Lattice artifact | Fake hotspots | Excluded in `grid_daily`; shown as a limitation |
| Panel size and geography drift | Fake trends | Rules in 3b |
| HDX names vs JogjaPulse names | Map joins fail | T3 matches on code where possible, then names, with an assertion of 0 unmatched |
| `pop_actual` reference year unknown | Weaker per-capita claims | Label as "BPS, year not stated in JogjaPulse" |
| PPKM levels unverified | Can't explain policy effects | Left out; mention as a limitation if needed |
| Nyepi date not checked against SKB text | Minor | Check before using Nyepi in a figure |
| Video longer than 5:00 | Penalty | Script capped at about 650 words; timed at the 19 Nov review |
| Uneven contribution | Grading | Each task has an owner who commits their own work |

## Next 3 actions

1. LEAD: confirm the eLOK deadline, assign the roles in the README team table (6 members), add members to the GitHub repo.
2. All: review notebooks 03–06 and the dashboard (each member must be able to explain the topic they present). Decide whether A4 (holidays, mostly negative) stays in the video or moves to the dashboard only.
3. DE: T3, kapanewon boundaries. HDX `cod-ab-idn` is only offered as whole-country files (218 MB geodatabase, 456 MB GeoJSON), so download once, cut DIY (code `34`) in a script, and commit only the small DIY file.
