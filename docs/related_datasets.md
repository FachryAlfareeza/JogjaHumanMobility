# Datasets Related to JogjaPulse

Web search done 10 Nov 2026. JogjaPulse covers DIY from 1 Dec 2021 to 30 Apr 2022, with kapanewon-hourly, 500 m grid-daily and monthly OD counts.

Fit column: "same place and period" means it covers DIY and Dec 2021 – Apr 2022.

## Mobility datasets

| # | Dataset | Coverage | Granularity | Fit | Status |
|---|---|---|---|---|---|
| 1 | Google COVID-19 Community Mobility Reports | Global, Feb 2020 – 15 Oct 2022 | Province only for Indonesia (`sub_region_1` = "Special Region of Yogyakarta"); daily % change vs baseline for 6 place types | Same place and period | In use. Checked: 151 of 151 days, no missing values. Fetched by `src/fetch_google_mobility.py`. |
| 2 | Meta Data for Good, Movement Range Maps | About Mar 2020 – May 2022 | Admin regions (GADM), daily `change_in_movement`, `stay_put` | Possibly same period | Not checked whether Indonesia has kabupaten rows. Not used. |
| 3 | Meta Movement Distribution Maps | From Dec 2022 | Admin regions, daily | Starts after the study period | Not usable |
| 4 | Grab-Posisi GPS trajectories | Jakarta and Singapore, 2019 | Raw GPS from Grab driver phones | Different city | Method comparison only |
| 5 | Mendeley "Tourism Dataset" (TripAdvisor, doi 10.17632/h58s544674.1) | Bali, Malang, Yogyakarta; Oct 2022 – Jan 2023 | Visits to attractions | Different period | Not used |
| 6 | BPS Statistik Wisatawan Nusantara (from mobile positioning data) | Indonesia, yearly | Province, yearly | Too coarse | Not used |
| 7 | Trans Jogja ridership (Bapperida "Dataku" portal) | DIY | Yearly or monthly | Not checked for 2021–22 monthly | Not used |
| 8 | Helsinki dynamic population (Sci Data 2021), Changchun network (Sci Data 2018), Barcelona and Milan operator data | Other cities | Grid or base station | Different city | Method comparison only |

No open traffic-count data for DIY was found. Dishub ATCS figures appear only in press releases, and the GPS data used in UGM theses is not public.

## Context datasets

| # | Dataset | Use | Join key | Status |
|---|---|---|---|---|
| 9 | HDX COD-AB Indonesia (`cod-ab-idn`), admin levels 0–3 | Kapanewon polygons for maps | Kapanewon name or code | Planned (PLAN task T3) |
| 10 | BPS DIY "Dalam Angka" 2022 | Population and area per kapanewon | Kapanewon | Not needed: JogjaPulse already includes `pop_actual` |
| 11 | dataset.jogjakota.go.id | Kota Yogyakarta population per kemantren, 2022 | Kemantren | Optional cross-check of `pop_actual` |
| 12 | WorldPop 100 m (R2025A), Meta 30 m population density | Residents per 500 m cell | Raster aggregated to cells | Not used |
| 13 | Open-Meteo historical weather (ERA5) | Hourly rain and temperature | Date and hour | Optional (PLAN task T4) |
| 14 | Overture Maps / Foursquare OS Places / OpenStreetMap | Points of interest per cell | Spatial join | Not used yet; may help label RQ1 cells |
| 15 | Holiday calendar | Holiday flags | Date | In use: `data/raw/external/calendar_2021_2022.csv` |

## Are JogjaPulse and Google independent?

They come from separate collection and processing pipelines.

| | JogjaPulse | Google CMR |
|---|---|---|
| Collected by | A commercial location-data aggregator, shared with UGM under a research agreement | Google |
| Collected through | Location features in third-party apps where the user granted location permission | Google account Location History (opt-in, off by default) |
| Device identifier | Mobile advertising ID | Google account |
| Privacy method | k-anonymity (k = 5), suppression | Differential privacy |
| Output | Device counts (grid, kapanewon, OD) | % change vs a Jan–Feb 2020 weekday baseline |

The same person can appear in both, but sampling and processing are separate. Agreement between the two therefore counts as external validation. Both are samples of smartphone users who allow location tracking, so they share that bias.

Google's values are % changes against the median for each weekday from 3 Jan to 6 Feb 2020, not counts. Compare deviations, not levels (PLAN section 2a).

## Sources

- Google: [documentation](https://www.google.com/covid19/mobility/data_documentation.html), [anonymization paper](https://arxiv.org/abs/2004.04145)
- Meta: [Movement Distribution Maps](https://ai.meta.com/ai-for-good/datasets/movement-distribution-maps/)
- [Grab-Posisi](https://engineering.grab.com/grab-posisi), [Mendeley Tourism Dataset](https://data.mendeley.com/datasets/h58s544674/1)
- [BPS Statistik Wisatawan Nusantara 2025](https://www.bps.go.id/en/publication/2026/04/30/06948320ebe75b7678b09c56/statistik-wisatawan-nusantara-2025.html)
- [Helsinki dynamic population](https://link.springer.com/10.1038/s41597-021-01113-4), [Changchun network](https://www.nature.com/articles/sdata2018228)
- [HDX COD-AB Indonesia](https://geo.btaa.org/catalog/84a1d98a-790b-4d66-9d14-bbfa48500802), [WorldPop R2025A](https://data.worldpop.org/repo/prj/Global_2015_2030/R2025A/doc/Global2_Release_Statement_R2025A_v1.pdf)
- [Open-Meteo historical API](https://open-meteo.com/en/docs/historical-weather-api), [Overture Places](https://docs.overturemaps.org/guides/places)
- Holidays: [SKB 3 Menteri 2022 (Setkab)](https://setkab.go.id/inilah-skb-3-menteri-perubahan-hari-libur-nasional-dan-cuti-bersama-tahun-2022/), [Ramadan 1443 start (Bisnis)](https://kabar24.bisnis.com/read/20220401/15/1517953/pemerintah-tetapkan-awal-ramadan-pada-3-april-2022-ini-alasannya)
