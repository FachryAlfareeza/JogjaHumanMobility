# Project Plan: Human Mobility in Yogyakarta (Rekayasa Data)

_Updated 2026-11-10. Status: both data sources downloaded and verified; EDA done (`notebooks/01_eda.ipynb`); cleaning pipeline not started._

**Working assumption:** week 13 starts **Mon 23 Nov 2026**, so the **video goes on eLOK by Fri 20 Nov** (safe whether "before week 13" means before Monday or before the week ends). This gives **10 days**. Confirm the date with the lecturer (see Risks).

---

## 1. Data sources (locked)

| # | Source | Role | Level | Status |
|---|---|---|---|---|
| 1 | **JogjaPulse** (Zenodo 10.5281/zenodo.23157460, CC BY 4.0) | Main data | 500 m grid/day, kapanewon/hour, OD/month | ✅ `data/raw/jogjapulse/` (9 files, MD5 checked) |
| 2 | **Google Community Mobility Reports**, DIY | Independent cross-check + place-type context | Province/day, % vs Jan–Feb 2020 baseline | ✅ `data/raw/external/google_mobility/` (151/151 days) |

### Context layers

| Layer | Decision | Why | Effort |
|---|---|---|---|
| Holiday + PPKM calendar (hand-made CSV) | **Do** | Explains the spikes (Nataru, Imlek, Ramadan from 2 Apr); about 25 rows | 1 h |
| Kapanewon boundaries (HDX `cod-ab-idn` ADM3) | **Do** | Needed for every choropleth and the OD flow map | 2–3 h (name matching) |
| BPS population | **Already have it**: `pop_actual` in `home_maids_vs_population_kapanewon.csv` (78 kapanewon) | Per-capita rates and representativeness, with no extra download | 0 h |
| Weather (Open-Meteo, Yogyakarta point, hourly) | **Optional** | Nice "rain vs mobility" side result; only if on schedule by 15 Nov | 1–2 h |
| POIs (OSM/Overture), WorldPop, Meta Movement Range | **Skip** | Not needed for the 4 questions; Meta coverage is unverified | — |

---

## 2. Research questions (final 4)

| RQ | Question | Data | Method | Main figure |
|---|---|---|---|---|
| **RQ1: Cross-validation** | Does JogjaPulse's daily DIY trend agree with Google's independent mobility index? | JP hourly + grid → DIY daily measures; Google DIY | Same-weekday deviation method + measure matching (section 2a); Spearman per pair; holiday case studies | Overlaid deviation time series (holidays shaded) + correlation heatmap |
| **RQ2: Daily rhythm** | How does the hourly profile differ between the urban core (Kota Yogya, Depok, Mlati) and rural kapanewon, on weekdays vs weekends? | JP hourly | Share of each kapanewon's daily devices per hour; cluster the 77 profiles (k-means, k = 3–4) | Hour × kapanewon heatmap + cluster map |
| **RQ3: Holidays and tourism** | How do Nataru, Imlek and long weekends shift presence toward tourist areas (Malioboro/Gondomanan, Parangtritis, Gunungkidul beaches)? | JP grid daily + calendar | Grid share on the holiday vs the median of the same weekday in the 2 weeks before; hotspot difference map | Before/after grid map + top-10 cells table |
| **RQ4: Commuting flows** | Which kapanewon send daytime visitors into Kota Yogyakarta? | JP OD monthly (**Dec–Feb only**) | Share of each origin's homed devices seen in each destination; top flows | Flow map / chord diagram |

### 2a. RQ1 method: matching JogjaPulse to Google

**Rule:** compare *deviation from a normal day of the same weekday* in both sources, never raw counts. Raw totals give a fake r = −0.77 with Google residential, because the shrinking device count and Google's rising residential share are both trends.

| Step | JogjaPulse | Google |
|---|---|---|
| 1. Daily measure | A share or ratio that doesn't depend on the device count (table below) | The category value (% vs 2020 baseline) |
| 2. Weekday baseline | Median of the same weekday within ±2 weeks (5-point centred rolling median per weekday) | Same |
| 3. Deviation | `log(value / baseline)` | `value − baseline` |
| 4. Compare | Spearman r per pair over 151 days; repeat per panel segment (Dec / 1 Jan–15 Feb / 16 Feb–Apr); holiday case studies (25 Dec, 1 Jan, 1 Feb Imlek, 3 Mar Nyepi) | |

| Google category | JogjaPulse measure | File | Quick-check r* |
|---|---|---|---|
| Parks (incl. beaches/tourism) | Gunungkidul share of daily devices; refine to coastal kapanewon (Tepus, Tanjungsari, Kretek) or beach grid cells | hourly / grid | 0.28 |
| Retail & recreation | Share of daytime presence in Gondomanan + Gedongtengen (Malioboro); refine with mall grid cells | hourly / grid | 0.26 (Gunungkidul share) |
| Transit stations | Share of presence in cells at Tugu, Lempuyangan, Giwangan, YIA (Temon) | grid | 0.28 (Gunungkidul share), cells not tested yet |
| Workplaces | Weekday 08–17 vs 00–05 presence ratio | hourly | −0.01 ❌ needs a better measure |
| Residential | Inverse of the day/night ratio | hourly | 0.18 (wrong sign) ❌ |
| General activity | Pings per device (`n_pings / n_maids`) | hourly | 0.31 retail, 0.31 transit, −0.32 residential |
| Grocery & pharmacy | No good proxy, so skip it | — | — |

\*Quick exploratory check on 10 Nov (Spearman, 151 days, weekday-deviation method); `02_cross_validation.ipynb` must reproduce it properly. **Expected result: weak-to-moderate agreement (r ≈ 0.3), strongest for leisure/tourism.** On 1 Jan 2022 both point the same way: Gunungkidul share +14% vs a normal Saturday, Google parks +40.

**Open items for RQ1:** build the grid-cell lists for transit, mall and beach areas (needs coordinates); find a working workplaces/residential measure (try the share of devices in the same kapanewon by day and night, using `validation_night_presence_kapanewon.csv` as the night anchor); check whether 25 Dec gives 0 deviation because of the weekday-median window.

### Normalisation rules (apply everywhere)

| Problem | Rule |
|---|---|
| JP panel decay (~87k → ~9k devices/day; drops on 1 Jan and 16 Feb 2022) | Never use raw `n_maids` across time. Use **shares**: `n_maids / DIY total that day (or hour)`. For RQ1, use the same-weekday deviation method in section 2a. A plain 7-day median isn't enough: it leaves JogjaPulse's weekly cycle in, which Google's baseline has already removed, and that gave r ≈ 0. |
| JP suppression (k = 5) | A missing row means < 5 devices, not 0. Leave it as NaN, report % suppressed, and don't sum across suppressed cells for small areas. |
| **Panel geography drifts** (EDA): Kota Yogyakarta's share goes 11% → 25% from Dec to Apr | Shares are only safe for comparing places **within the same day**. Across time, use the same-weekday local baseline (section 2a) or stay within one panel segment. Never plot a raw share trend over the whole period as a finding. |
| **Coordinate-lattice artifact** (EDA): 70 grid cells on 0.1°/0.05° lattice points hold 8.6% of presence (7–20× a normal cell) | Flag them as `lattice_artifact` (rule in `01_eda.ipynb` §5.1) and **exclude them from all grid analyses** (hotspots, holiday shifts, transit/mall/beach cells for RQ1). Kapanewon-level files are only mildly affected. |
| **Kapanewon names not unique** (EDA): "JETIS" exists in Bantul (34.02.09) and Kota Yogyakarta (34.71.02) | Join on `kapanewon_code` or `(kab_kota, kapanewon)`, never on the name alone. |
| Google is % vs a weekday-specific 2020 baseline | Compare **deviations**, not levels (section 2a); never read Google's 0 as "normal 2021". |
| Google is province-level only | RQ1 is at DIY/day level only. |
| OD `reduced_quality` in Mar–Apr 2022 | RQ4 uses Dec 2021 – Feb 2022 only; mention it as a limitation. |

---

## 3. Task list

Roles: **LEAD** (integrator/repo), **DE** (data engineer), **AN** (analyst), **VIZ**, **MEDIA** (video/slides). Put names in the README team table.

| ID | Stage | Task | Output | Owner | Depends on |
|---|---|---|---|---|---|
| T1 | Setup | Create GitHub repo, push scaffold, add everyone, set branch rule (PR per notebook) | GitHub URL in README | LEAD | — |
| T2 | Ingest | Build holiday + PPKM calendar | `data/raw/external/calendar_2021_2022.csv` (date, name, type, ppkm_level) | DE | — |
| T3 | Ingest | Fetch kapanewon boundaries (DIY subset) in `src/fetch_external.py` | `data/raw/external/diy_kapanewon.geojson` | DE | — |
| T4 | Ingest | (Optional) Fetch Open-Meteo hourly weather | `data/raw/external/weather_yogya_hourly.csv` | DE | — |
| T5 | Clean | `src/clean.py`: types, datetimes (WIB), name standardisation (upper-case, strip "KAPANEWON/KEMANTREN"), Google column renames | `data/interim/*.parquet` | DE | — |
| T6 | Clean | Kapanewon crosswalk keyed on `kapanewon_code` (JP files) ↔ (kab, name) (pop file) ↔ HDX names | `data/interim/kapanewon_crosswalk.csv` (78 rows, 0 unmatched) | DE | T3, T5 |
| T7 | Integrate | `src/build_features.py`: daily DIY table (JP totals, shares, de-trended index) + Google + calendar | `data/processed/daily_diy.parquet` | DE | T2, T5 |
| T8 | Integrate | Hourly kapanewon shares + weekday/holiday flags + population | `data/processed/hourly_kapanewon.parquet` | DE | T5, T6 |
| T9 | Integrate | Grid daily shares + holiday flags + `lattice_artifact` flag (copy the rule from `01_eda.ipynb` §5.1) | `data/processed/grid_daily.parquet` | DE | T5, T2 |
| T10 | Integrate | OD shares Dec–Feb, joined to boundaries | `data/processed/od_dec_feb.parquet` | DE | T6 |
| T11 | Analyse | ✅ **Done 10 Nov**: `01_eda.ipynb` (reads raw data directly; 16 figures `reports/figures/eda_*.png`) | figures F1–F3 + extras | AN | — |
| T12 | Analyse | `02_cross_validation.ipynb` (RQ1) | F4–F6 + correlation table | AN | T7 |
| T13 | Analyse | `03_daily_rhythm.ipynb` (RQ2) | F7–F9 | AN | T8 |
| T14 | Analyse | `04_holiday_hotspots.ipynb` (RQ3) | F10–F12 | AN + VIZ | T9 |
| T15 | Analyse | `05_od_flows.ipynb` (RQ4) | F13–F14 | VIZ | T10 |
| T16 | Visualise | Final styling pass; export PNG (1920×1080) to `reports/figures/` | 8–10 video-ready figures | VIZ | T11–T15 |
| T17 | Video | Script (~700 words), storyboard mapping each figure to a segment | `video/script.md` | MEDIA | T12–T15 drafts |
| T18 | Video | Record narration + screen/figure edit, 5:00 max | `video/final.mp4` (not committed) | MEDIA | T16, T17 |
| T19 | Video | **Upload to eLOK** | eLOK submission | LEAD | T18 |
| T20 | Slides | Slides from the same figures + methods + limitations | `presentation/slides.pptx` | MEDIA | T16 |
| T21 | Repo | README final: sources, how to run, results summary, video link | README.md | LEAD | T16 |

---

## 4. Timeline (critical path in **bold**)

Critical path: **T5 → T7 → T12 (RQ1) → T16 → T17 → T18 → T19**. RQ1 is the headline result, so it gates the script.

| Date | Day | Milestone |
|---|---|---|
| 10 Nov | Tue | Plan agreed, roles assigned, **T1** repo up |
| 11 Nov | Wed | T2, T3 done; **T5 clean.py** done |
| 12 Nov | Thu | T6 crosswalk; **T7 daily_diy**; T8–T10 |
| 13 Nov | Fri | T11 EDA; **T12 RQ1 first result** (go/no-go: do the trends agree?) |
| 14–15 Nov | Sat–Sun | T13, T14, T15 drafts; optional T4 weather |
| 16 Nov | Mon | **All RQ results frozen**; T17 script draft |
| 17 Nov | Tue | **T16 final figures**; script final |
| 18 Nov | Wed | **T18 record + edit** |
| 19 Nov | Thu | Review cut with the whole group, fixes |
| **20 Nov** | **Fri** | **T19 upload to eLOK** (buffer: 21–22 Nov) |
| 23 Nov – 4 Dec | Weeks 13–14 | T20 slides, T21 README, rehearse, present |

---

## 5. Notebook plan

| Notebook | Figures | Video segment |
|---|---|---|
| `01_eda.ipynb` ✅ | F1 `eda_panel_decay`; F2 `eda_raw_vs_share` (shows the drift); F3 `eda_representativeness`; plus `eda_grid_lattice_artifacts`, `eda_heatmap_hour_weekday`, `eda_od_kabupaten_matrix`, `eda_jp_vs_google_parks` | 0:30–1:15 Data + caveats (F1, F2, lattice map as limitations) |
| `02_cross_validation.ipynb` | F4 deviation time series, JP Gunungkidul share vs Google parks (holidays shaded); F5 correlation heatmap (JP measures × Google categories); F6 raw-count vs adjusted correlation side by side (shows why normalising matters) | 1:15–2:15 **Finding 1: independent sources agree** |
| `03_daily_rhythm.ipynb` | F7 hour × kapanewon share heatmap; F8 cluster map of rhythm types; F9 weekday vs weekend profile by cluster | 2:15–3:00 Finding 2 |
| `04_holiday_hotspots.ipynb` | F10 DIY share time series with holidays shaded; F11 grid map holiday-minus-baseline share; F12 top-10 gaining cells | 3:00–3:45 Finding 3 |
| `05_od_flows.ipynb` | F13 flow map into Kota Yogyakarta (Dec–Feb); F14 top-15 origin bar chart | 3:45–4:20 Finding 4 |
| — | Pipeline diagram (raw → interim → processed → notebooks) | 0:30–1:15 |
| — | Limitations slide (devices ≠ people, panel decay, smartphone bias, OD quality) | 4:20–4:45, then conclusion + GitHub link to 5:00 |

---

## 6. Risks and open questions

| Risk / question | Impact | Mitigation |
|---|---|---|
| **Actual eLOK deadline** (which date counts as "before week 13"?) | Whole schedule | LEAD asks the lecturer/eLOK page **today**; the plan targets 20 Nov regardless |
| Kapanewon name mismatches (JP upper-case vs HDX names; "Kemantren" in the city). ✅ The 77-vs-78 puzzle is solved: duplicate name "JETIS" | Broken joins and maps | T6 crosswalk keyed on code, assert 0 unmatched |
| Coordinate-lattice artifact inflates 70 grid cells (8.6% of presence) | Fake hotspots in RQ3 and RQ1 cell lists | Exclude flagged cells; show the before/after map as a limitation in the video |
| Panel geography drifts (city share 11% → 25%) | Fake "trend" findings | Same-weekday local baseline only; no full-period share trends as findings |
| RQ1 shows weak agreement | Headline finding changes | Still a valid result: report it, explain why (panel shifts, opt-in differences); test per segment |
| Panel decay distorts every trend | Wrong conclusions | Normalisation rules in section 2 are mandatory; F1 shows the drops in the video |
| OD Mar–Apr `reduced_quality` | Biased flows | Use Dec–Feb only |
| `pop_actual` source year unknown (README placeholder) | Per-capita figures less defensible | Label as "BPS (year not stated in JogjaPulse)"; optionally cross-check 3–4 kapanewon against BPS Dalam Angka 2022 |
| Meta Movement Range coverage unverified | None (dropped) | Mention only as future work |
| Video over 5:00 | Penalty | Script capped at about 700 words; time it at the T19 review |
| Uneven member contribution | Grading | Each task has an owner; each owner commits their own work |

---

## Next 3 actions

1. **LEAD:** confirm the exact eLOK deadline, fill in the team/role table in the README, and create and push the GitHub repo (T1).
2. **DE:** write `src/clean.py` (T5) and the kapanewon crosswalk (T6), joining on `kapanewon_code`. Move the `lattice_artifact` flag from `01_eda.ipynb` into the grid pipeline (T9).
3. **DE/AN:** build `data/processed/daily_diy.parquet` (T7) and run `02_cross_validation.ipynb` (T12) by **Fri 13 Nov**. The EDA preview already gives r = 0.31 (Gunungkidul share vs Google parks); the notebook must confirm it properly and test the transit, mall and beach cell measures (artifact cells excluded).
