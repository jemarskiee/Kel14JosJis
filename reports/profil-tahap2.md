# Profil dan Calon Anomali Seri Utama (Tahap 2)

Kelompok 14: Produktivitas tenaga kerja dan industri
Sprint 1, Tahap 2 (Profil dan anomali)

## 1. Cakupan dan metode

Seri yang diprofilkan: var1161 (SDG 8.2.1), var1344 (SDG 2.3.1), var1214 (SDG 9.2.1), dan var2755 (SDG 9.2.2). Data dibaca dari hasil ekstraksi tahap 1 (`src/ekstraksi`, fungsi `jalankan()`). Skrip profil ada di `src/profil/analisis_tahap2.py`.

Ketentuan yang dipakai:
- Tahap ini hanya menemukan dan menandai. Data mentah, hasil ekstraksi, dan Silver tidak diubah.
- Baris nasional (kode 9999 atau nama INDONESIA) dipisahkan dari baris provinsi. Statistik dan deteksi anomali hanya memakai baris provinsi.
- Bila kunci (seri, wilayah, periode, rincian) yang sama muncul di dua snapshot atau dua format (CSV dan JSON), untuk profil diambil snapshot terbaru. Ini hanya untuk analisis dan bukan keputusan Silver. Aturan resmi ditetapkan di Gold dan dicatat di log-keputusan.csv.
- Label rincian "Tidak ada" dari BPS diseragamkan menjadi "total" hanya di tabel analisis.

Cakupan data:
- Berkas BPS yang dipakai: 10 (5 CSV dan 5 JSON). Berkas WDI, ILOSTAT, dan metadata (12 tabel) dilewati karena bukan seri utama.
- Baris mentah seri target: 3.820. Baris analisis setelah penggabungan snapshot dan format: 1.623 (1.577 baris provinsi dan 46 baris nasional).
- Nilai yang bukan angka: 0.

## 2. Ringkasan profil per seri

Tabel lengkap: `reports/profil/profil_per_seri.csv`. Statistik per provinsi: `reports/profil/profil_per_provinsi.csv`. Jumlah provinsi per periode: `reports/profil/provinsi_per_periode.csv`. Semua angka di bawah hanya untuk baris provinsi.

### var1161 (laju pertumbuhan PDB per tenaga kerja, SDG 8.2.1)
- Periode: 2011 sampai 2025 (15 periode), 39 provinsi, rincian: total.
- Jumlah pengamatan: 511.
- Minimum -22,96; kuartil 1 0,115; median 2,54; rata-rata 2,728; kuartil 3 4,975; maksimum 31,79; simpangan baku 4,885.
- Satuan: kosong di hasil ekstraksi dan tercatat tidak_ada di katalog. Besaran nilai (negatif sampai belasan, median 2,54) sesuai dengan laju pertumbuhan dalam persen.

### var1344 (nilai tambah pertanian per tenaga kerja, SDG 2.3.1)
- Periode: 2015 sampai 2023 (9 periode), 34 provinsi, rincian: total.
- Jumlah pengamatan: 306.
- Minimum 17.412.788,26; kuartil 1 40.510.938,91; median 58.560.232,02; rata-rata 65.722.807,94; kuartil 3 75.574.144,91; maksimum 235.350.879,04; simpangan baku 36.958.522,23.
- Satuan: kosong di hasil ekstraksi. Katalog menyebut rupiah per tenaga kerja. Besarannya puluhan juta, jadi cocok dengan rupiah penuh, bukan ribu atau juta. Ini masih perlu dicocokkan dengan metadata.

### var1214 (proporsi nilai tambah industri manufaktur terhadap PDB, SDG 9.2.1)
- Periode: 2010 sampai 2023 (14 periode), 38 provinsi, rincian: total.
- Jumlah pengamatan: 480.
- Minimum 0,24; kuartil 1 6,578; median 12,81; rata-rata 16,037; kuartil 3 21,365; maksimum 44,51; simpangan baku 11,297.
- Satuan: kosong di hasil ekstraksi dan tercatat tidak_ada di katalog. Besaran 0,24 sampai 44,51 sesuai dengan persen.

### var2755 (proporsi tenaga kerja manufaktur, SDG 9.2.2)
- Periode: 2018 sampai 2025 (8 periode), 38 provinsi, rincian: total.
- Jumlah pengamatan: 280.
- Minimum 0,08; kuartil 1 6,745; median 8,65; rata-rata 10,245; kuartil 3 11,49; maksimum 25,77; simpangan baku 5,577.
- Satuan: kosong di hasil ekstraksi. Katalog menyebut persen. Seluruh nilai berada dalam rentang 0 sampai 100.

### Jawaban empat pertanyaan standar tahap profil
1. Provinsi per tahun: jumlah provinsi unik per seri adalah 39 (var1161), 34 (var1344), 38 (var1214), dan 38 (var2755). Rincian per tahun ada di `provinsi_per_periode.csv`.
2. Rentang tahun: lihat daftar per seri di atas.
3. Rincian: setiap seri hanya punya satu rincian, yaitu total. Kolom turvar BPS seluruhnya "Tidak ada".
4. Kecocokan satuan dengan besaran angka: cocok untuk keempat seri (lihat catatan satuan di atas). Namun kolom satuan di hasil ekstraksi kosong untuk keempatnya.

### Kelengkapan kasar terhadap grid penuh (provinsi x periode)
- var1161: 511 dari 585 sel (87,4%).
- var1344: 306 dari 306 sel (100%).
- var1214: 480 dari 532 sel (90,2%).
- var2755: 280 dari 304 sel (92,1%).

Sebagian sel kosong kemungkinan wajar karena provinsi pemekaran baru ada sejak tahun berdirinya. Sebab pastinya belum diperiksa per provinsi dan menjadi tugas Tahap 3.

## 3. Grafik

Semua grafik ada di `reports/gambar/`, tiga per seri:
- `<seri>_total_boxplot_periode.png`: sebaran antarprovinsi pada tiap periode.
- `<seri>_total_boxplot_provinsi.png`: sebaran waktu tiap provinsi, diurutkan menurut median.
- `<seri>_total_deret_waktu.png`: deret waktu semua provinsi (abu-abu), median provinsi (biru), nilai Indonesia (merah), dan calon anomali (titik hitam).

Berkas:
1. var1161_total_boxplot_periode.png, var1161_total_boxplot_provinsi.png, var1161_total_deret_waktu.png. Temuan: Berdasarkan ketiga visualisasi data var1161, terdapat pola fluktuasi konsisten antara median provinsi dan nilai Indonesia dengan puncak pada 2013, 2015, dan 2017, serta titik terendah pada 2019–2020. Secara spasial, disparitas antarwilayah cukup mencolok: Sulawesi Tengah, Papua Selatan, dan Maluku Utara memiliki median tertinggi (>4), sedangkan Papua Tengah, Nusa Tenggara Barat, dan Riau terendah (<0). Variasi tahunan juga bervariasi, dengan sebaran terlebar pada 2017 dan tersempit pada 2024. Perlu dicatat adanya anomali ekstrem pada 2025 (nilai >30) dan 2023 (nilai < -15), serta kategori "nan" yang mengindikasikan data tidak valid. Secara keseluruhan, data menunjukkan variabilitas tinggi baik antar waktu maupun antar wilayah, dan anomali pada periode terakhir memerlukan investigasi lebih lanjut.
2. var1344_total_boxplot_periode.png, var1344_total_boxplot_provinsi.png, var1344_total_deret_waktu.png. Temuan: Berdasarkan ketiga visualisasi data var1344 (2015–2023), terlihat tren kenaikan yang konsisten pada median nasional (garis oranye) maupun nilai Indonesia (garis merah), dengan lonjakan tajam pada tahun 2023. Secara spasial, disparitas antarwilayah sangat mencolok: Kalimantan Timur, Riau, dan Kalimantan Utara mendominasi dengan median tertinggi (di atas 1,4 x 10^8), sementara Papua, Nusa Tenggara Timur, dan DI Yogyakarta berada di posisi terendah. Sebaran data antarprovinsi per periode juga semakin melebar dari tahun ke tahun, dengan banyaknya titik pencilan (outlier) ekstrem pada periode 2018–2023 yang mengindikasikan ketimpangan nilai yang semakin besar antarwilayah. 
3. var1214_total_boxplot_periode.png, var1214_total_boxplot_provinsi.png, var1214_total_deret_waktu.png. Temuan: Berdasarkan ketiga visualisasi data var1214 (2010–2023), median nasional (garis oranye) dan nilai Indonesia (garis merah) menunjukkan tren yang sangat stabil dan relatif datar di kisaran angka 12–22 sepanjang periode. Secara spasial, disparitas antarwilayah sangat mencolok: Jawa Barat, Kepulauan Riau, dan Banten mendominasi dengan median tertinggi (di atas 30), sementara Papua Tengah, Papua Pegunungan, dan Nusa Tenggara Timur berada di posisi terendah. Terdapat beberapa provinsi dengan sebaran data yang sangat lebar, seperti Sulawesi Tengah dan Maluku Utara. Selain itu, terlihat banyak titik pencilan (outlier) ekstrem yang konsisten di angka 40-an pada hampir setiap tahun, serta satu provinsi yang mengalami lonjakan drastis pada tahun 2023 (mendekati 40), mengindikasikan adanya anomali data yang perlu diverifikasi.
4. var2755_total_boxplot_periode.png, var2755_total_boxplot_provinsi.png, var2755_total_deret_waktu.png. Temuan: Berdasarkan ketiga visualisasi data var2755 (2018–2025), terlihat tren yang sangat stabil dan datar sepanjang periode, baik pada median nasional (garis oranye, kisaran 8–9) maupun nilai Indonesia (garis merah, kisaran 13–15), dengan sedikit penurunan pada tahun 2020. Secara spasial, disparitas antarwilayah sangat mencolok: Kepulauan Riau, Banten, dan Jawa Tengah mendominasi dengan median tertinggi (di atas 15), sementara Papua Pegunungan, Papua Tengah, dan Papua berada di posisi terendah (median <5). Provinsi Maluku Utara memiliki sebaran data yang sangat ekstrem dengan rentang antar-kuartil paling lebar (dari ~4 hingga ~24). Selain itu, terdapat kelompok provinsi dengan nilai konstan sangat tinggi (di kisaran 20–25) yang konsisten muncul sebagai pencilan (outlier) di setiap tahunnya, mengindikasikan adanya entitas dengan nilai yang jauh di atas rata-rata nasional.

## 4. Calon anomali

Daftar lengkap (provinsi, periode, nilai, metode, alasan): `reports/profil/calon_anomali.csv`. Semua baris berstatus "calon, ditandai saja, belum diubah".

Metode:
1. IQR lintas provinsi: nilai di luar Q1 - 1,5 x IQR atau Q3 + 1,5 x IQR, dihitung per periode (minimal 8 provinsi).
2. Z-score deret provinsi: nilai dengan |z| di atas 2,5 terhadap rata-rata deret provinsi itu (minimal 6 periode).
3. Lonjakan antarperiode: selisih tahun ke tahun di luar batas IQR dengan faktor 3.
4. Calon patahan seri: median perubahan seluruh provinsi pada satu periode menyimpang dengan robust z di atas 3,5.
5. Di luar rentang wajar: var2755 di luar 0 sampai 100, var1344 di bawah 0.

Jumlah calon anomali:
- var1161: 43 (IQR lintas provinsi 34, z-score deret provinsi 9).
- var1214: 33 (IQR lintas provinsi 11, lonjakan antarperiode 17, z-score deret provinsi 5).
- var1344: 36 (IQR lintas provinsi 29, lonjakan antarperiode 7).
- var2755: 37 (IQR lintas provinsi 33, lonjakan antarperiode 4).
- Total: 149. Calon patahan seri: 0. Di luar rentang wajar: 0.

Contoh var1161 (dari daftar):
- 2011: Sumatera Utara (18,09), Lampung (18,22), dan Sulawesi Tenggara (15,58) berada di atas batas atas antarprovinsi (14,96).
- 2013: Kalimantan Timur (-6,41) dan Sulawesi Barat (12,15) di luar batas [1,45; 10,68].
- 2015: Nusa Tenggara Barat (19,85), Kalimantan Timur (16,39), Sulawesi Tengah (12,52), dan Maluku (-3,12) di luar batas [-2,63; 11,46].
- 2018: Nusa Tenggara Timur (-7,31), Sulawesi Tengah (11,98), dan Maluku (-8,59) di luar batas [-5,94; 5,82].
- 2019: Papua (-15,34) dan Nusa Tenggara Barat (-6,51) di luar batas [-3,03; 10,61].
- 2020: Maluku Utara (5,25) dan Papua (8,47) di atas batas atas 4,16.
- Sulawesi Tengah muncul berulang (2015, 2018, 2021, nilai 11,09 pada 2021), yang menunjukkan pola khas provinsi dan bukan galat acak.

Contoh var1214 (33 calon):
- Jawa Barat muncul 10 kali pada metode IQR lintas provinsi (2012 sampai 2018, 2020, 2021, dan 2023), dengan nilai 42,16 sampai 43,72. Nilainya stabil di atas batas atas antarprovinsi (misalnya 41,81 pada 2012 dan 42,53 pada 2023). Ini pola khas provinsi (basis industri besar), bukan galat acak.
- Kepulauan Riau: 41,96 pada 2021 (di atas batas 41,06). Pada 2020 nilainya 40,77 dan perubahannya +2,79 terhadap tahun sebelumnya, di luar batas lonjakan [-1,48; 1,39].
- Sulawesi Tengah: lonjakan berturut-turut pada 2015, 2016, dan 2018 sampai 2023. Perubahan terbesar +8,88 pada 2018 (menjadi 21,38), dan nilainya naik terus sampai 36,82 pada 2023. Ini tren naik yang panjang, bukan lonjakan satu kali.
- Maluku Utara: lonjakan 2020 sampai 2023, dengan perubahan +3,96, +6,39, +7,81, dan +4,43 (menjadi 30,09 pada 2023).
- Papua Barat 2023: 39,36, perubahan +8,49 dan z-score 3,19 (ditandai dua metode). Maluku 2023 (6,65; z = 3,00) dan Papua 2023 (2,86; z = 2,98) juga ditandai z-score. Tahun 2023 berstatus angka sangat sementara menurut catatan BPS, jadi revisi mungkin menjelaskan sebagian.

Contoh var1344 (36 calon):
- Riau, Kalimantan Timur, dan Kalimantan Utara berulang kali di atas batas atas antarprovinsi pada 2015 sampai 2023. Riau mencapai nilai maksimum seri, 235.350.879,04 pada 2023 (batas atas 181.437.260,42), dan pada tahun yang sama ditandai lonjakan +35.480.818,54.
- DKI Jakarta: 120.232.473,70 pada 2016 dengan perubahan +85.486.173,88, lonjakan terbesar di seri ini. Pada 2018 turun -36.419.932,40 (menjadi 93.703.148,43).
- Kepulauan Riau: lonjakan +29.252.528,93 pada 2016 dan -21.349.460,37 pada 2020.
- Sulawesi Utara 2016: lonjakan +32.787.994,25 (menjadi 82.469.708,59).
- Catatan: batas bawah IQR bernilai negatif pada 2016 sampai 2023 (misalnya -31.318.120,09 pada 2023) karena sebaran antarprovinsi sangat miring ke kanan. Batas bawah ini tidak berarti apa-apa untuk nilai yang selalu positif. Calon anomali di seri ini praktis semuanya sisi atas, yaitu provinsi berbasis tambang atau perkebunan dan DKI Jakarta.

Contoh var2755 (37 calon):
- Kepulauan Riau, Banten, dan Jawa Tengah muncul hampir setiap tahun 2018 sampai 2025 di atas batas atas. Kepulauan Riau tertinggi, 25,77 pada 2022 (batas atas 17,28). Jawa Barat juga di atas batas pada 2018 sampai 2020, 2022, dan 2024 (18,74 sampai 21,07).
- Maluku Utara: 19,84 pada 2022, 25,48 pada 2023, 24,66 pada 2024, dan 24,90 pada 2025. Pada 2021 nilainya 16,66 dengan lonjakan +10,96, perubahan terbesar di seri ini, dan +5,64 pada 2023.
- DI Yogyakarta 2023: 13,74, perubahan -3,54 (di luar [-3,36; 3,38]). Papua 2024: 5,32, perubahan +3,79.
- Semua nilai tetap dalam rentang 0 sampai 100, jadi tidak ada yang melanggar rentang wajar. Pola berulang pada provinsi industri menunjukkan outlier asli (struktur ekonomi), bukan galat.

Penafsiran: semua baris di atas masih calon outlier asli. Tidak ada yang dikoreksi dan tidak ada yang dinyatakan galat input. Penyebab tiap kasus belum diteliti.

## 5. Temuan untuk Tahap 3

1. var1214 dan dua ukuran. Panduan menyebut var1214 memuat dua ukuran dalam satu judul. Pembedanya tidak ditemukan pada snapshot 2026-10-20:
   - Judul di manifest_asal.json dan label di bagian var JSON hanya satu: "Proporsi Nilai Tambah Sektor Industri Manufaktur Terhadap PDB".
   - Kolom turvar seluruhnya "Tidak ada" (494 baris per berkas, CSV dan JSON identik).
   - Unit dan definisi kosong di metadata. Nilai berada dalam satu sebaran (0,24 sampai 44,51).
   Seri ini diprofilkan sebagai satu seri. Perlu dikonfirmasi ke pembimbing sebelum Tahap 3. Bila ada pembeda, pemisahan dicatat di log-keputusan.csv beserta alternatif yang ditolak.
2. Catatan BPS untuk var1214: 2022 angka sementara dan 2023 angka sangat sementara. Ini kemungkinan penjelasan bila ada nilai janggal di dua tahun tersebut.
3. Satuan. Kolom satuan di hasil ekstraksi kosong untuk keempat seri. Satuan baku ditetapkan dari metadata dan dicatat di log: var1161 persen (laju), var1214 persen, var2755 persen, var1344 rupiah per tenaga kerja.
4. var2755 dua snapshot. Dari 280 pasangan provinsi-periode yang ada di snapshot 2026-10-17 dan 2026-10-20, 0 bernilai berbeda, jadi tidak ada revisi. Rincian: `reports/profil/var2755_dua_snapshot.csv`. Aturan pemilihan snapshot tetap harus ditetapkan di Gold.
5. var1161 dan jumlah baris. Berkas sdg8_produktivitas tanggal 17 Oktober berisi 524 baris (CSV) dan 526 baris (JSON), selisih 2 baris. Analisis memakai 511 baris provinsi hasil penggabungan. Perlu diperiksa baris mana yang hanya ada di JSON.
6. Jumlah provinsi. var1161 memuat 39 kode provinsi di luar 9999, sedangkan susunan baku adalah 38. Perlu dicek kode tambahan itu dan pemetaannya ke susunan 38 provinsi. var1344 hanya memuat 34 provinsi, perlu dicek apakah provinsi pemekaran Papua 2022 memang tidak ada.
7. Kelengkapan panel. Sel kosong terhadap grid penuh: var1161 12,6%, var1214 9,8%, var2755 7,9%, var1344 0%. Pemisahan antara provinsi yang belum berdiri dan data yang benar-benar hilang dilakukan di Tahap 3.
8. Patahan seri. Metode serentak tidak menandai periode mana pun (0). Ini tidak membuktikan tidak ada patahan, karena deretnya pendek (8 sampai 15 periode). Periksa deret waktu secara visual, terutama 2020 pada var1161. Pada 2020 batas IQR antarprovinsi melebar menjadi [-8,34; 4,16].
9. Rentang wajar var1214 sengaja belum diisi. Rentang 0 sampai 100 dapat dipakai setelah satuan ditetapkan.

## 6. Berkas keluaran

- `src/profil/analisis_tahap2.py`
- `reports/profil/profil_per_seri.csv`
- `reports/profil/profil_per_provinsi.csv`
- `reports/profil/provinsi_per_periode.csv`
- `reports/profil/nasional_vs_provinsi.csv`
- `reports/profil/calon_anomali.csv`
- `reports/profil/var2755_dua_snapshot.csv`
- `reports/gambar/*.png` (12 gambar)
- `results/<nim>/metrics.json` (outlier_ditandai, patahan_ditandai)

## 7. Keterbatasan

- Ambang (IQR 1,5, z-score 2,5, IQR 3 untuk lonjakan, robust z 3,5) dipilih sebagai titik awal dan bisa diubah. Jumlah calon anomali bergantung pada ambang ini.
- IQR lintas provinsi menandai banyak titik karena sebaran antarprovinsi memang lebar, terutama pada var1161. Daftarnya adalah calon, bukan kesimpulan.
- Profil memakai snapshot terbaru bila kunci kembar. Ini bukan aturan Silver.