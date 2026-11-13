# Kunjungan siang: asal berbeda, tujuan utamanya juga berbeda

Analisis Desember 2021–Februari 2022, asal di luar Kota Yogyakarta dan tujuan individual di dalam Kota. Sumber: JogjaPulse yang sudah tersedia dalam repo.

## Alur insight

1. **Dari perbandingan indikator ke rincian hubungan wilayah.** Output pertama membandingkan indikator JogjaPulse dengan Google. Untuk mengetahui asal mana yang terhubung dengan bagian Kota mana, kita memakai tabel asal–tujuan JogjaPulse. Ini perluasan pertanyaan berdasarkan rincian datanya; korelasi dengan Google tidak menjadi validasi seluruh hubungan asal–tujuan.

2. **Dua hubungan terbesar mengarah ke tujuan berbeda.** Di antara pasangan yang datanya terbit ketiga bulan, Banguntapan–Umbulharjo mempunyai rata-rata 1.092,7 perangkat per bulan, diikuti Depok–Gondokusuman 837,3. Kita memilih dua hubungan ini dari ranking jumlah perangkat, lalu membandingkan kedua asal pada kedua tujuan yang sama.

   | Asal rumah perangkat | Teramati di Umbulharjo | Teramati di Gondokusuman |
   |---|---:|---:|
   | Banguntapan | 20,5% | 7,3% |
   | Depok | 5,3% | 10,0% |

   Persentase tersebut adalah ringkasan berbobot tiga bulan terhadap sampel perangkat dengan rumah bulanan di masing-masing asal. Banguntapan lebih tinggi ke Umbulharjo; Depok lebih tinggi ke Gondokusuman. Perbedaan ini tetap terlihat setelah jumlah dibagi dengan ukuran sampel asal. Satu perangkat dapat tercatat pada kedua tujuan, sehingga tabel bukan pembagian pilihan yang saling terpisah.

3. **Urutan tujuan itu terlihat pada setiap bulan.** Umbulharjo menjadi tujuan Kota teratas yang dipublikasikan untuk Banguntapan pada Desember, Januari, dan Februari. Gondokusuman juga menjadi tujuan teratas untuk Depok pada ketiga bulan. Jadi perbedaannya tidak hanya muncul karena ketiga bulan digabungkan. Yang bertahan adalah urutannya; persentasenya berubah dan belum tentu perangkat yang sama berulang.

4. **Maknanya: hubungan siang ke Kota berbeda menurut asal.** Menggabungkan seluruh Kota menjadi satu tujuan akan menyembunyikan perbedaan tersebut. Kegunaan aplikatifnya adalah memilih Banguntapan–Umbulharjo dan Depok–Gondokusuman sebagai pasangan awal untuk observasi atau survei keterhubungan siang. Data belum menentukan kebutuhan rute atau kapasitas angkutan.

## Bukti per bulan

| Pasangan asal–tujuan | Des 2021 | Jan 2022 | Feb 2022 |
|---|---:|---:|---:|
| Banguntapan–Umbulharjo | 20,3% | 23,5% | 17,1% |
| Banguntapan–Gondokusuman | 5,4% | 8,0% | 9,6% |
| Depok–Umbulharjo | 4,9% | 5,4% | 5,6% |
| Depok–Gondokusuman | 8,2% | 10,7% | 11,7% |

Contoh perhitungan Banguntapan–Umbulharjo pada Desember: 1.394 / 6.856 = 20,3%. Ringkasan tiga bulannya: (1.394 + 1.174 + 710) / (6.856 + 4.995 + 4.150) = 20,5%. Ini proporsi berbobot perangkat-bulan, bukan perangkat unik selama tiga bulan.

## Hipotesis yang dapat dibahas

Perbedaan fungsi kawasan, akses, atau kegiatan rutin seperti bekerja dan belajar mungkin berkaitan dengan perbedaan hubungan tersebut. Ini hipotesis: tabel asal–tujuan tidak memuat alasan kunjungan, moda, rute, atau frekuensi perjalanan. Tiga bulan dengan urutan yang sama juga belum membuktikan kebiasaan jangka panjang atau perjalanan komuter.

## Definisi yang perlu disampaikan

“Kunjungan siang” berarti perangkat dengan estimasi rumah di asal teramati setidaknya sekali di tujuan pada 08.00–17.59 WIB dalam bulan tersebut. Datang sekali dan datang setiap hari sama-sama dihitung satu kali dalam satu pasangan-bulan. Rumah diperkirakan dari pengamatan malam, bukan alamat terverifikasi.

Perangkat bukan orang; persentase bukan persentase penduduk. Sampel ponsel berubah dan tidak acak. Maret–April dikeluarkan karena kualitas OD rendah. Pasangan tidak terbit tetap tidak diketahui, bukan nol. Kesimpulan difokuskan pada dua asal yang dipilih, bukan digeneralisasikan ke seluruh DIY.

## Jejak bukti

- Notebook: `notebooks/07_daytime_visit_pairs.ipynb`, bagian pemilihan fokus, hasil utama, dan lampiran.
- Grafik utama: `reports/figures/rq4_destination_pattern.png`.
- Bukti 12 pasangan-bulan, pembagi, proporsi, dan ranking tujuan per asal: `reports/tables/rq4_daytime_story_evidence.csv`.
- Konteks pemilihan hubungan: `reports/tables/rq4_top_pairs.csv`.
- Sumber asli: [JogjaPulse v1](https://zenodo.org/records/23157460), README bagian 4.6–4.7, 5–6. Notebook memeriksa ulang hitungan dan pembagi terhadap dua CSV mentah, lalu memeriksa urutan tujuan pada setiap bulan.
