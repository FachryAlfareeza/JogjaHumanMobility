# Slide plan and script (5 minutes)

_Draft 2026-11-10; restructured 2026-11-12 into the two outputs (PLAN.md section 0), with numbers from the first pass of notebooks 03–06. Every number comes from a notebook (see the source column) or the JogjaPulse README._

The same slides serve two uses: the eLOK video (narration over slides) and the week 13–14 live presentation.

## 1. Visual system

| Element | Rule |
|---|---|
| Format | 16:9, 1920×1080. Figures exported at that size from `reports/figures/` (T16) |
| Layout | Title = the finding as one sentence. Figure takes the left ~2/3; right column holds at most 2 key numbers with a one-line label each. No bullet walls |
| Fonts | One sans family (e.g. Inter or Source Sans 3). Title 36 pt, key number 60 pt bold, labels 18 pt, source line 12 pt |
| Colours | JogjaPulse = one colour (e.g. teal `#0F766E`), Google = one contrasting colour (e.g. orange `#C2410C`), holidays = light grey bands. Keep these identical in every figure and slide |
| Source line | Bottom-left on every data slide: data source + method, e.g. "JogjaPulse + Google CMR, 151 hari, deviasi hari yang sama" |
| Caveat chip | Small grey box on the slide where the limitation applies (devices ≠ people, panel shrinks, OD Mar–Apr excluded) |
| Animation | Only "appear" for the second figure or the key number, timed to the narration. No transitions |
| Language | Slide text in Bahasa Indonesia; keep technical terms as used in the repo (kapanewon, device, share) |

## 2. Storyboard

Two parts: Output 1 (slides 2–5, how far JogjaPulse can be trusted, checked against Google) and Output 2 (slides 6–9, what it can be used for). Slide 5 ends with the bridge: JogjaPulse agrees weakly to moderately with Google on one leisure proxy, while the selected station and mall cells and the tested day/night proxy show no clear agreement, so Output 2 uses timing and leisure.

| # | Time | Slide title (finding) | Visual | Key numbers on slide | Source |
|---|---|---|---|---|---|
| 1 | 0:00–0:15 | Mobilitas Penduduk di DIY: Apa Kata Data Ponsel? | Map of DIY with 5 kabupaten outlined, the 6 team names + NIMs (README team table), course name | — | README |
| 2 | 0:15–0:40 | Dua sumber data, dua output | Left: two source cards (JogjaPulse: 500 m grid/day, kapanewon/hour, OD/month; Google CMR: province/day). Right: "Output 1: seberapa bisa dipercaya?" and "Output 2: untuk apa?" Pipeline strip and GitHub URL along the bottom | 151 hari (1 Des 2021 – 30 Apr 2022); 78 kapanewon | EDA §2.2 |
| 3 | 0:40–1:05 | Jumlah device menyusut dan bergeser, jadi angka mentah tidak bisa dibandingkan antarwaktu | `eda_panel_decay.png` (break lines 1 Jan, 16 Feb), then appear `eda_raw_vs_share.png` | Night presence 3.634 → 644 per jam (Des → Apr); share Kota Yogyakarta 10,5% → 24,5% | EDA §3 |
| 4 | 1:05–1:45 | Output 1: porsi Gunungkidul dan indeks taman Google searah, tapi lemah | `rq1_raw_vs_adjusted.png`, then appear `rq1_deviation_series.png` | Sel mal: mentah −0,34 → disesuaikan 0,03; Gunungkidul vs taman r = 0,37 (Spearman, 149 hari, 95% CI 0,11–0,56); searah di 5 dari 6 hari libur | `02_cross_validation` §3b, §4, §7 |
| 5 | 1:45–2:00 | Proxy stasiun, mal, dan komuter yang kami uji tidak sejalan | `rq1_corr_heatmap.png` with the parks row highlighted; caveat chip: "7 sel stasiun, 9 sel mal, termasuk lingkungan sekitarnya" | Stasiun r = 0,19, mal r = 0,03 (CI memuat 0); ping per device-jam vs ritel r = 0,27 (intensitas, bukan kunjungan) | `02_cross_validation` §3b, §8 |
| 6 | 2:00–2:45 | Output 2 · Ramadan: porsi aktivitas jam sahur naik dua kali lipat | `ramadan_hourly_profile.png`, then appear `ramadan_google_categories.png` | Jam 03–04: 3,7% → 8,1% dari aktivitas sehari; Google taman −25,8 poin (2021: −19,3) | `06_ramadan` §1, §2, §4 |
| 7 | 2:45–3:20 | Output 2 · Pengunjung siang Kota Yogyakarta datang dari kapanewon tetangga | `visits_top_origins.png`, then appear `visits_origin_destination_heatmap.png` (flow map if T3 is done) | Banguntapan 38,2%, Sewon 38,1%, Kasihan 35,5%; data Des–Feb saja | `05_daytime_visits` §2, §3 |
| 8 | 3:20–3:55 | Output 2 · Hari libur menggeser aktivitas ke malam, tapi tidak ke satu titik | Left: `rhythm_weekday_vs_dayoff.png`. Right: `holiday_kapanewon_top.png` | Hari libur di Kota: siang −2,7 poin, malam +2,2 poin; tidak ada sel 500 m yang menonjol; Kokap +46% | `03_daily_rhythm` §4, `04_holiday_hotspots` §2–§4 |
| 9 | 3:55–4:25 | Dashboard: semua hasil bisa dijelajahi | Screen recording of `dashboard/app.py`: Ramadan tab, then pick an origin in the daytime-visits tab | — | `dashboard/app.py` |
| 10 | 4:25–4:45 | Batasan: device bukan orang | Left: `eda_grid_lattice_artifacts.png`. Right: 3 short lines (lattice, representativeness, one Ramadan only) | 1,2% sel memuat 8,6% presence; Gondomanan 2,2 device/penduduk | EDA §5.1, §6 |
| 11 | 4:45–5:00 | Kesimpulan | 2 one-line findings (one per output) + GitHub URL + QR code + data citation | — | — |

Slide 3 comes before Output 1 because every later number depends on the normalisation it explains.

## 3. Script (Bahasa Indonesia)

About 520 words of narration. At a normal Indonesian speaking pace (120–130 words per minute) that is 3:59–4:19 of speech; the rest of the 5:00 is pauses and the dashboard recording on slide 9. Time a read-through with the slides, and shorten slide 9 first if it runs over.

**Slide 1 (0:00–0:15)**
Halo, kami kelompok [nama] dari mata kuliah Rekayasa Data. Kami meneliti bagaimana penduduk Daerah Istimewa Yogyakarta bergerak, menggunakan data lokasi ponsel.

**Slide 2 (0:15–0:40)**
Sumber utama kami adalah JogjaPulse, data kehadiran device ponsel yang sudah dianonimkan, untuk 151 hari dari Desember 2021 sampai April 2022. Sumber kedua adalah Google Community Mobility Reports untuk DIY. Proyek kami punya dua output. Pertama, seberapa jauh JogjaPulse sejalan dengan Google. Kedua, bagaimana hasilnya dipakai untuk analisis yang lebih aplikatif.

**Slide 3 (0:40–1:05)**
Jumlah device yang terekam tidak stabil. Kehadiran malam turun dari sekitar 3.600 per jam di Desember menjadi sekitar 640 di April, dan porsi Kota Yogyakarta naik dari 10,5 menjadi 24,5 persen. Itu kemungkinan besar perubahan panel, bukan perilaku warga, jadi kami hanya memakai porsi, bukan angka mentah.

**Slide 4 (1:05–1:45)**
Output pertama. Angka mentah menyesatkan karena kedua data punya tren: sel di sekitar mal dan indeks ritel Google berkorelasi minus 0,34, tetapi setelah setiap hari dibandingkan dengan hari yang sama satu dan dua minggu di sekitarnya, korelasinya tinggal 0,03. Dengan metode yang sama, porsi device di Gunungkidul berkorelasi dengan indeks taman Google sebesar 0,37: lemah sampai sedang. Pada 5 dari 6 hari libur keduanya bergerak searah; contohnya 1 Januari, porsi Gunungkidul naik sekitar 20 persen dan indeks taman Google naik 41 poin.

**Slide 5 (1:45–2:00)**
Untuk sel di sekitar stasiun dan mal yang kami pilih, tidak ada kesepakatan yang jelas. Ukuran siang–malam yang kami uji juga tidak menunjukkan beda hari kerja dan akhir pekan. Jadi kami memakai JogjaPulse untuk waktu aktivitas dan wisata, bukan untuk mengukur komuter.

**Slide 6 (2:00–2:45)**
Output kedua, dimulai dari Ramadan. Kami membandingkan tiga minggu pertama Ramadan dengan tiga minggu sebelumnya. Porsi aktivitas pukul tiga sampai lima pagi naik dari 3,7 menjadi 8,1 persen, mulai tepat 2 dan 3 April. Ini kemungkinan waktu sahur, dan terlihat di semua kabupaten. Google menunjukkan kunjungan ke taman turun 26 poin, dan pola yang sama muncul pada Ramadan 2021. JogjaPulse sejalan: porsi Gunungkidul turun 30 persen.

**Slide 7 (2:45–3:20)**
Kedua, pengunjung siang ke Kota Yogyakarta. Dari data asal–tujuan Desember sampai Februari, kami menghitung porsi kunjungan siang ke luar kapanewon asal yang menuju Kota. Tertinggi adalah tetangga langsung Kota: Banguntapan 38 persen, Sewon 38 persen, dan Kasihan 36 persen. Tujuan terbanyak adalah Umbulharjo dan Gondokusuman. Data ini tidak membedakan kerja dan rekreasi.

**Slide 8 (3:20–3:55)**
Ketiga, ritme harian dan hari libur. Pada hari libur, porsi aktivitas bergeser dari siang ke malam, paling besar di Kota: siang turun 2,7 poin, malam naik 2,2 poin. Kami juga mencari sel 500 meter yang ramai saat libur, tetapi tidak ada yang melebihi akhir pekan biasa. Di tingkat kapanewon, Kokap di Kulon Progo naik di keenam hari libur.

**Slide 9 (3:55–4:25)**
Semua hasil ini kami kemas dalam dashboard. Pengguna bisa memilih wilayah dan melihat ritme hariannya, perubahan saat Ramadan, atau dari mana pengunjung sebuah kapanewon datang.

**Slide 10 (4:25–4:45)**
Ada beberapa batasan. Device bukan orang, dan sampelnya lebih banyak di kota. Di Gondomanan ada 2,2 device "rumah" per penduduk. Sebagian kecil sel grid kemungkinan berisi koordinat yang dibulatkan, jadi kami keluarkan. Dan JogjaPulse hanya mencakup satu Ramadan.

**Slide 11 (4:45–5:00)**
Kesimpulannya: JogjaPulse sejalan secara lemah sampai sedang dengan Google untuk aktivitas wisata, dan dengan koreksi panel bisa menunjukkan pergeseran jam saat Ramadan serta asal pengunjung Kota. Kode dan dashboard ada di GitHub kami. Terima kasih.

## 4. Before recording

- Recheck the Output 2 numbers against notebooks 03–06 if anything in the pipeline is rerun.
- Record the dashboard segment (slide 9) from a fresh `streamlit run dashboard/app.py`.
- Time one full read-through; target 4:50 to leave room for pauses.
- Run the anti-slop checklist (`docs/anti_slop_guidelines.md` §6) on the slide text.
