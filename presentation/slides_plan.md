# Slide plan and script (5 minutes)

_Draft 2026-11-10. Numbers marked `[isi: ...]` come from notebooks 02–05, which aren't written yet. Fill them in from the notebook cell, or cut the sentence. All other numbers come from `notebooks/01_eda.ipynb` or the JogjaPulse README (see the source column)._

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

| # | Time | Slide title (finding) | Visual | Key numbers on slide | Source |
|---|---|---|---|---|---|
| 1 | 0:00–0:15 | Mobilitas Penduduk di DIY: Apa Kata Data Ponsel? | Map of DIY with 5 kabupaten outlined, team names + NIM, course name | — | — |
| 2 | 0:15–0:45 | Dua sumber data, empat pertanyaan | Left: two source cards (JogjaPulse: 500 m grid/day, kapanewon/hour, OD/month; Google CMR: province/day). Right: 4 RQ as short lines | 151 hari (1 Des 2021 – 30 Apr 2022); 78 kapanewon | EDA §2.2 |
| 3 | 0:45–1:05 | Dari data mentah ke tabel analisis | Pipeline diagram: raw (Zenodo, Google) to `clean.py` to `build_features.py` to 4 processed tables to notebooks. GitHub URL in corner | 4 tabel processed | repo |
| 4 | 1:05–1:40 | Jumlah device menyusut dan bergeser, jadi angka mentah tidak bisa dibandingkan antarwaktu | `eda_panel_decay.png` (break lines 1 Jan, 16 Feb), then appear `eda_raw_vs_share.png` | Night presence 3.634 → 644 per jam (Des → Apr); share Kota Yogyakarta 10,5% → 24,5% | EDA §3 |
| 5 | 1:40–2:30 | RQ1: JogjaPulse dan Google bergerak searah, tapi lemah | F4: deviation series JP Gunungkidul share vs Google parks, holidays shaded. Appear F6: raw vs adjusted correlation side by side | r = 0,31 (Spearman, 151 hari); korelasi semu mentah −0,77 | EDA §9 / `02_cross_validation` |
| 6 | 2:30–3:10 | RQ2: Pusat kota dan desa punya ritme harian berbeda | F7 hour × kapanewon heatmap (start from `eda_heatmap_hour_weekday.png` if F7 isn't ready); appear F8 cluster map | Puncak 18–20, terendah 02–05; `[isi: jumlah cluster, contoh beda]` | EDA §4.1 / `03_daily_rhythm` |
| 7 | 3:10–3:50 | RQ3: Libur panjang menggeser kehadiran ke `[isi: wilayah dari F11]` | F11 grid map holiday-minus-baseline (lattice cells removed), F12 top-10 table as small inset | 1 Jan 2022: share Gunungkidul +14% vs Sabtu normal; `[isi: sel teratas]` | PLAN §2a / `04_holiday_hotspots` |
| 8 | 3:50–4:25 | RQ4: `[isi: asal utama]` mengirim pengunjung siang terbanyak ke Kota Yogyakarta | F13 flow map into Kota Yogyakarta, F14 top origins bar chart | `[isi: 3 asal teratas + share]`; data Des–Feb saja | `05_od_flows` |
| 9 | 4:25–4:45 | Batasan: device bukan orang | Left: `eda_grid_lattice_artifacts.png`. Right: 3 short lines (lattice, representativeness, OD quality) | 1,2% sel memuat 8,6% presence; Gondomanan 2,2 device/penduduk | EDA §5.1, §6 |
| 10 | 4:45–5:00 | Kesimpulan | 3 one-line findings + GitHub URL + QR code + data citation | — | — |

Slide 4 is deliberately early: every later finding depends on the normalisation it explains, so the audience needs it before RQ1.

## 3. Script (Bahasa Indonesia)

About 610 words. At a normal Indonesian speaking pace (120–130 words per minute) that is 4:45–5:05, so time a read-through and cut slide 3 first if it runs over.

**Slide 1 (0:00–0:15)**
Halo, kami kelompok [nama] dari mata kuliah Rekayasa Data. Kami meneliti bagaimana penduduk Daerah Istimewa Yogyakarta bergerak, menggunakan data lokasi ponsel.

**Slide 2 (0:15–0:45)**
Kami memakai dua sumber data. Sumber utama adalah JogjaPulse, data kehadiran device ponsel yang sudah dianonimkan, untuk 151 hari dari Desember 2021 sampai April 2022. Datanya tersedia per sel 500 meter per hari, per kapanewon per jam, dan per pasangan asal–tujuan per bulan. Sumber kedua adalah Google Community Mobility Reports untuk DIY, yang kami pakai sebagai pembanding independen. Kami menjawab empat pertanyaan: apakah kedua sumber sepakat, bagaimana ritme harian tiap wilayah, apa efek hari libur, dan dari mana komuter yang masuk ke Kota Yogyakarta.

**Slide 3 (0:45–1:05)**
Pipeline kami ditulis dalam Python. Data mentah dibersihkan, lalu digabung menjadi empat tabel analisis: harian provinsi, per jam per kapanewon, grid harian, dan asal–tujuan. Semua kode ada di GitHub.

**Slide 4 (1:05–1:40)**
Temuan pertama justru soal datanya sendiri. Jumlah device yang terekam tidak stabil. Rata-rata kehadiran malam turun dari sekitar 3.600 per jam di Desember menjadi sekitar 640 di April. Komposisinya juga bergeser: porsi Kota Yogyakarta naik dari 10,5 persen menjadi 24,5 persen. Perubahan sebesar itu kemungkinan besar berasal dari panel, bukan perilaku warga. Karena itu kami tidak pernah membandingkan angka mentah antarwaktu. Kami memakai share, dan untuk tren kami bandingkan setiap hari dengan hari yang sama dalam dua minggu di sekitarnya.

**Slide 5 (1:40–2:30)**
Pertanyaan pertama: apakah JogjaPulse sejalan dengan Google? Kalau memakai angka mentah, korelasinya minus 0,77, tetapi itu semu, karena kedua data sama-sama punya tren. Setelah disesuaikan dengan metode hari yang sama, porsi device di Gunungkidul berkorelasi dengan indeks taman dan wisata Google sebesar 0,31. Itu korelasi lemah sampai sedang. Kesepakatan paling jelas terlihat saat libur: pada 1 Januari 2022, porsi Gunungkidul naik 14 persen dibanding Sabtu biasa, dan indeks taman Google juga naik.

**Slide 6 (2:30–3:10)**
Pertanyaan kedua: ritme harian. Di seluruh DIY, aktivitas paling rendah pukul dua sampai lima pagi, datar dari siang sampai sore, dan memuncak pukul enam sampai delapan malam. Kami mengelompokkan profil per jam dari 78 kapanewon menjadi [isi] kelompok. [isi: satu kalimat beda pusat kota vs desa, dan hari kerja vs akhir pekan.]

**Slide 7 (3:10–3:50)**
Pertanyaan ketiga: hari libur. Kami membandingkan share setiap sel grid saat libur dengan median hari yang sama dua minggu sebelumnya. Sel yang koordinatnya kemungkinan dibulatkan sudah kami buang. [isi: sel atau wilayah yang paling naik saat Nataru dan Imlek, dengan angkanya.]

**Slide 8 (3:50–4:25)**
Pertanyaan keempat: komuter. Dari data asal–tujuan Desember sampai Februari, kami menghitung porsi device dari tiap kapanewon asal yang terlihat di Kota Yogyakarta. [isi: tiga asal teratas dan porsinya.] Data Maret dan April tidak kami pakai karena kualitasnya ditandai menurun.

**Slide 9 (4:25–4:45)**
Ada beberapa batasan. Device bukan orang, dan sampelnya lebih banyak di kota. Di Gondomanan ada 2,2 device "rumah" per penduduk. Selain itu, 1,2 persen sel grid memuat 8,6 persen kehadiran, kemungkinan karena koordinat yang dibulatkan, jadi sel itu kami keluarkan.

**Slide 10 (4:45–5:00)**
Kesimpulannya: data ponsel bisa menunjukkan ritme harian, efek libur, dan arus komuter di DIY, asalkan perubahan panel dikoreksi dulu. Kode dan data ada di GitHub kami. Terima kasih.

## 4. Before recording

- Replace every `[isi: ...]` with a number from notebooks 02–05, or cut the sentence.
- Check the 1 Jan Google parks value in `02_cross_validation.ipynb` before saying it out loud (PLAN gives +40 from the quick check only).
- Time one full read-through; target 4:50 to leave room for pauses.
- Run the anti-slop checklist (`docs/anti_slop_guidelines.md` §6) on the slide text.
