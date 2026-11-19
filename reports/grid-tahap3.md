# Grid Lengkap dan Kelengkapan Panel (Tahap 3)

Kelompok 14: Produktivitas tenaga kerja dan industri
Sprint 1, Tahap 3 (grid dan kelengkapan panel)

## 1. Metode

Grid provinsi x tahun dibentuk per seri (var1161, var1344, var1214, var2755) dari hasil ekstraksi tahap 1. Skrip: `src/silver/grid_tahap3.py`. Data mentah, hasil ekstraksi, dan Silver tidak diubah.

Aturan:
1. Baris Indonesia (9999) dipisah dari baris provinsi: 46 baris nasional (`reports/profil/baris_nasional.csv`) dan 1.577 baris provinsi.
2. Susunan 38 provinsi diambil dari kode wilayah di var2755 (38 kode, tidak ada kode dengan dua nama). Nama ke-38 provinsi diperiksa satu per satu, termasuk Kalimantan Utara dan empat provinsi baru Papua.
3. Kunci yang sama pada dua snapshot atau dua format (CSV dan JSON) diambil dari snapshot terbaru, hanya untuk analisis. Aturan pemilihan resmi ditetapkan di Gold dan dicatat di log.
4. Sel provinsi baru sebelum tahun berdiri ditandai `belum_berdiri` dan tidak dihitung missing (Kalimantan Utara 2012; Papua Barat Daya, Papua Selatan, Papua Tengah, dan Papua Pegunungan 2022). Tahun berdiri adalah asumsi awal. Sel yang terisi tetap dihitung terisi walaupun sebelum tahun itu.
5. Sel kosong dibiarkan kosong dan dilaporkan. Tidak ada imputasi.
6. Keputusan dicatat di `log-keputusan.csv` (K-002 sampai K-007).

## 2. Kode di luar 38 provinsi

var1161 memuat satu kode di luar susunan 38, yaitu kode `1`, sebanyak 2 baris: 2015 (nilai 4,62) dan 2016 (nilai 1,83). Kode ini tidak punya nama wilayah.

Bukti dari berkas mentah (`bps/2026-10-17/json/sdg8_produktivitas.json`):
- Kunci datacontent-nya 1116101150 dan 1116101160. Menurut aturan kunci (vervar, var, turvar, tahun, turtahun) keduanya terbaca vervar 1, var 1161, turvar 0, tahun 115 dan 116 (2015 dan 2016), turtahun 0. Jadi kode 1 ada di data mentah dan bukan hasil salah pecah di pembaca.
- Daftar vervar pada halaman JSON itu hanya memuat 9999 (INDONESIA). Kode 1 tidak punya label.
- Kedua baris hanya ada di JSON. CSV tidak memuatnya, sehingga berkas ini berisi 524 baris (CSV) dan 526 baris (JSON).

Nilainya dekat dengan angka nasional tahun yang sama (4,70 dan 1,85) tetapi tidak sama, sehingga tidak cukup untuk menyimpulkan bahwa kode ini adalah baris nasional. Arti kode 1 belum terbukti. Kedua baris tidak masuk grid, tidak dihapus, tidak dipetakan ke wilayah lain, dan tetap tercatat di `reports/profil/kode_wilayah_di_luar_38.csv` (log K-006). Keduanya adalah 2 dari 511 pengamatan var1161 pada profil Tahap 2, dan nilainya berada di dalam rentang provinsi. var1214 dan var2755 memuat 38 kode provinsi dan var1344 memuat 34 kode.

## 3. Kelengkapan per seri

| Seri | Periode | Sel grid | Belum berdiri | Diharapkan | Terisi | Kosong | Persen terisi |
|---|---|---|---|---|---|---|---|
| var1161 | 2011-2025 | 570 | 45 | 525 | 509 | 16 | 97,0 |
| var1214 | 2010-2023 | 532 | 48 | 484 | 480 | 4 | 99,2 |
| var1344 | 2015-2023 | 342 | 28 | 314 | 306 | 8 | 97,5 |
| var2755 | 2018-2025 | 304 | 16 | 288 | 280 | 8 | 97,2 |
| Total | | 1.748 | 137 | 1.611 | 1.575 | 36 | 97,8 |

Persen terisi = terisi dibagi sel diharapkan (sel belum berdiri tidak dihitung). Baris provinsi hasil ekstraksi 1.577 = 1.575 sel terisi + 2 baris kode 1 yang di luar grid.

## 4. Persen terisi per tahun

Tabel lengkap: `reports/profil/kelengkapan_per_tahun.csv`.

- var1161: 100% pada 2011, 2016-2021, dan 2025. 97,1% pada 2012-2015 (33 dari 34 provinsi). 89,5% pada 2022-2024 (34 dari 38).
- var1214: 100% pada 2010-2021 dan 2023. 89,5% pada 2022 (34 dari 38).
- var1344: 100% pada 2015-2021. 89,5% pada 2022 dan 2023.
- var2755: 100% pada 2018-2021, 2024, dan 2025. 89,5% pada 2022 dan 2023.

Persen terendah 89,5% berarti 34 dari 38 provinsi terisi.

## 5. Sel kosong

Detail: `reports/profil/sel_kosong_detail.csv`. Seluruh 36 sel kosong ada pada lima provinsi. Tidak ada celah di tengah deret dan tidak ada provinsi lama yang kosong.

| Provinsi | Seri dan tahun kosong | Sel |
|---|---|---|
| Kalimantan Utara | var1161 2012-2015 | 4 |
| Papua Barat Daya, Papua Selatan, Papua Tengah, Papua Pegunungan | var1161 2022-2024 (3 sel per provinsi), var1214 2022 (1), var2755 2022-2023 (2), var1344 2022-2023 (2) | 32 |

Penyebab:
1. var1161: catatan BPS (var.note) menyatakan laju 2024 dihitung pada provinsi induk (Papua dan Papua Barat) karena data tenaga kerja provinsi baru baru tersedia 2024, sehingga laju provinsi baru baru tersedia 2025.
2. var1344 dan var2755: catatan BPS tidak memberi penjelasan. Penyebab belum terjelaskan. Pada var1344 keempat provinsi baru Papua tidak ada di seri (34 provinsi).
3. Kalimantan Utara var1161 2012-2015: belum terjelaskan. Menurut `grid_panel.csv`, var1214 sudah memuat nilai Kalimantan Utara sejak 2010, jadi cakupan provinsi baru berbeda antarseri dan tidak diseragamkan.

## 6. Laju var1161: provinsi vs nasional

Tabel: `reports/profil/laju_provinsi_vs_nasional.csv`.
- Korelasi angka nasional dan median provinsi: 0,865.
- Angka nasional berada di dalam rentang provinsi pada seluruh 15 tahun (2011-2025).
- Arah berlawanan hanya pada 2018: nasional 0,79 dan median provinsi -0,22, keduanya dekat nol.
- Median provinsi tidak dibobot menurut ukuran ekonomi provinsi, sehingga tidak diharapkan sama dengan angka nasional. Paket tidak memuat bobot.

Kesimpulan: laju provinsi konsisten dengan angka nasional dalam hal rentang, arah, dan korelasi.

## 7. var1214

Satu ukuran. Kolom turvar seluruhnya "Tidak ada" (494 baris), daftar turvar di JSON mentah satu entri, judul dan metadata `var` tunggal, `related` kosong, dan tidak ada entri katalog kembar. Panduan menyebut dua ukuran, tetapi pembedanya tidak ditemukan pada snapshot 2026-10-20. Seri diperlakukan sebagai satu seri dan dikonfirmasi ke pembimbing (log K-005). Dasar harga tidak disebut di metadata. Catatan BPS: 2022 angka sementara dan 2023 angka sangat sementara.

## 8. Keterbatasan

1. Tahun berdiri provinsi baru adalah asumsi awal.
2. Median provinsi tidak dibobot.
3. Penyebab sel kosong var1344, var2755, dan Kalimantan Utara var1161 belum terjelaskan.
4. Arti kode wilayah 1 pada var1161 belum terbukti.
5. Silver resmi belum ada (`src/silver` masih template), sehingga metrik `baris_silver` belum bisa diisi. Angka yang dipakai adalah `baris_analisis` (1.623 baris setelah penggabungan snapshot dan format).

## 9. Rujukan

- `reports/profil/grid_panel.csv`, `kelengkapan_per_seri.csv`, `kelengkapan_per_tahun.csv`, `sel_kosong_detail.csv`, `kode_wilayah_di_luar_38.csv`, `baris_nasional.csv`, `laju_provinsi_vs_nasional.csv`
- Gambar: `reports/gambar/grid_var1161.png`, `grid_var1214.png`, `grid_var1344.png`, `grid_var2755.png`
- Log: `log-keputusan.csv` K-002 sampai K-007
