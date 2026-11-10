# Datasets Related to JogjaPulse

This is a web search (Nov 2026) for datasets that match or complement JogjaPulse, which covers DIY, 1 Dec 2021 – 30 Apr 2022, with kapanewon-hourly, 500 m grid-daily and monthly OD counts.

**Fit:** ✅ covers DIY *and* Dec 2021 – Apr 2022 · 🟡 covers DIY but a different period, or needs extra work · ❌ only a methodological comparison

## A. Mobility datasets (same kind of data)

| # | Dataset | Coverage | Granularity | Fit | Join to JogjaPulse | Access |
|---|---|---|---|---|---|---|
| 1 | **Google COVID-19 Community Mobility Reports** | Global, Feb 2020 – 15 Oct 2022 | Province only (`sub_region_1` = "Special Region of Yogyakarta"; Indonesia has no kabupaten level), daily, % change vs baseline for 6 place types (retail & recreation, grocery & pharmacy, parks, transit, workplaces, residential) | ✅ **verified**: 151/151 days in the window, no missing values | `date` → daily DIY totals from `presence_kapanewon_hourly` | Downloaded by `src/fetch_google_mobility.py` → `data/raw/external/google_mobility/` |
| 2 | **Meta Data for Good, Movement Range Maps** | ~Mar 2020 – May 2022 | Admin region (GADM; probably kabupaten for Indonesia), daily `change_in_movement`, `stay_put` | ✅ (to verify) | `date` + kabupaten (`kab_kota`) | Free, HDX "movement-range-maps" (one big TSV) |
| 3 | Meta Movement Distribution Maps (successor) | Dec 2022 onward | Admin region, daily distance distribution | 🟡 starts after the JogjaPulse window | — | HDX |
| 4 | **Grab-Posisi** GPS trajectories | Jakarta + Singapore, 2019 | Raw GPS pings from Grab driver phones (car + motorcycle) | ❌ different city, for method comparison | Not joinable | Free for non-commercial use: engineering.grab.com/grab-posisi |
| 5 | Mendeley "Tourism Dataset" (TripAdvisor) | Bali, Malang, **Yogyakarta**; Oct 2022 – Jan 2023 | Tourist visit transactions at attractions | 🟡 different period | Attraction location → kapanewon | Free: doi 10.17632/h58s544674.1 |
| 6 | BPS Statistik Wisatawan Nusantara (built from mobile positioning data) | Indonesia, yearly | Province-level domestic trips | 🟡 yearly only | DIY yearly totals | Free PDF/tables, bps.go.id |
| 7 | Trans Jogja ridership (Bapperida "Dataku" portal) | DIY | Yearly/monthly passengers | 🟡 coarse, check monthly 2021–22 | Month | bappeda.jogjaprov.go.id/dataku |
| 8 | Helsinki dynamic population (Scientific Data 2021), Changchun phone network (Sci Data 2018), Barcelona Vodafone grid, Milan TIM presence | Other cities | 250 m grid hourly / base stations | ❌ comparison only | — | Open |

**No open DIY traffic-volume data was found.** Dishub ATCS counts exist only as press figures, and the GPS data in UGM theses is not public.

## B. Context datasets (to explain *why* mobility changes)

| # | Dataset | Use | Join key | Access |
|---|---|---|---|---|
| 9 | **HDX COD-AB Indonesia (`cod-ab-idn`)**, admin boundaries levels 0–3, BPS P-codes | Kapanewon polygons for choropleth maps | kapanewon name/code (check name matching) | Free, data.humdata.org/dataset/cod-ab-idn |
| 10 | **BPS DIY "Dalam Angka" 2022** (province + each kabupaten) | Population, area, density per kapanewon | kapanewon | Free PDF/Excel, yogyakarta.bps.go.id (+ slemankab / bantulkab / gunungkidulkab / kulonprogokab .bps.go.id) |
| 11 | dataset.jogjakota.go.id | Kota Yogyakarta population per kemantren 2022 | kemantren (= kapanewon in the city) | Free CSV |
| 12 | **WorldPop 100 m (R2025A)** / **Meta High-Res Population Density 30 m** | Residential population per 500 m cell, to normalise the grid | Aggregate raster into JogjaPulse cells (UTM 49S) | Free (CC BY 4.0), HDX / worldpop.org |
| 13 | **Open-Meteo Historical Weather (ERA5)** | Hourly rain and temperature for Yogyakarta | `date` + `hour` | Free, no key: archive-api.open-meteo.com/v1/archive |
| 14 | **Overture Maps Places** / Foursquare OS Places / OpenStreetMap | POIs (campuses, malls, beaches, terminals) per grid cell | Spatial join to 500 m cells | Free (CDLA / ODbL) |
| 15 | Holidays + PPKM level calendar (manual table) | Christmas/New Year, Imlek, Ramadan (2 Apr 2022), PPKM levels | `date` | Build from government announcements |

## Recommendation

For the "at least 2 data sources" requirement, the strongest story is:

1. **JogjaPulse** (main data)
2. **Google Community Mobility Reports, DIY rows**: a second, *independent* mobility source for the same place and period. We can validate JogjaPulse against it (does the daily trend match Google's?). This is a good analytics angle.
3. Optionally **Meta Movement Range Maps** at kabupaten level, as a third source to cross-check.
4. Context layers: **HDX boundaries** (maps), **BPS population** (per-capita), and **Open-Meteo + holiday calendar** (drivers).

Google's DIY rows are confirmed: all 151 days from 1 Dec 2021 to 30 Apr 2022, with all 6 categories complete. Google's figures are % changes against a pre-COVID baseline (the median for each weekday, 3 Jan – 6 Feb 2020), not counts. Compare **trends** (for example, correlate daily changes or z-scores), not levels. Google only has province-level data for Indonesia, so the comparison happens at DIY level.

**Are the two sources independent? Yes, they come from separate pipelines.**

| | JogjaPulse | Google CMR |
|---|---|---|
| Collected by | A commercial location-data aggregator (under a UGM research agreement) | Google |
| Collected through | Ad/analytics SDKs inside third-party apps where the user granted location permission | Google account **Location History** (opt-in, off by default) |
| Device ID | Mobile advertising ID (MAID) | Google account |
| Privacy method | k-anonymity (k = 5), suppression | Differential privacy |
| Output | Device counts (grid / kapanewon / OD) | % change vs Jan–Feb 2020 baseline by place type |

The *people* can overlap: the same smartphone owner may appear in both. But the data collection, sampling, and processing are separate. A match between the two is therefore real external validation, not one dataset checked against itself. Both are smartphone-based convenience samples, so they share a bias toward smartphone users.

Still to verify: whether Meta Movement Range has Indonesia kabupaten rows.
