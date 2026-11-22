<<<<<<< HEAD
# Profil Seri Pembanding Nasional (Tahap 2)
=======
﻿# Profil Seri Pembanding Nasional (Tahap 2)
>>>>>>> 6c3a75eca90542af1ad4022572bda1878c0c0262

Kelompok 14: Produktivitas tenaga kerja dan industri
Sprint 1, Tahap 2 (profil seri pembanding)

## 1. Tujuan dan cakupan

Laporan ini memprofilkan lima seri pembanding nasional: SDG_0821_NOC_RT, SDG_B821_NOC_RT, dan SDG_0922_NOC_RT dari ILOSTAT, serta SL.GDP.PCAP.EM.KD dan NV.IND.MANF.ZS dari WDI. Isinya adalah periode yang tersedia, rincian, satuan, dan tahun yang beririsan dengan seri utama. Hasilnya dipakai untuk memilih rincian yang sebanding pada tahap 6.

<<<<<<< HEAD
Data dibaca dari hasil ekstraksi tahap 1 (`src/ekstraksi`). Skrip profil: `src/profil/pembanding_tahap2.py`. Tahap ini hanya menandai dan tidak mengubah data. Tahun setelah 2026 diperlakukan sebagai proyeksi dan dikeluarkan dari irisan, sesuai panduan kelompok (angka yang melewati tahun berjalan).
=======
Data dibaca dari hasil ekstraksi tahap 1 (`src/ekstraksi`). Skrip profil: `src/silver/pembanding_tahap2.py`. Tahap ini hanya menandai dan tidak mengubah data. Tahun setelah 2026 diperlakukan sebagai proyeksi dan dikeluarkan dari irisan, sesuai panduan kelompok (angka yang melewati tahun berjalan).
>>>>>>> 6c3a75eca90542af1ad4022572bda1878c0c0262

Berkas keluaran:

1. `reports/profil/pembanding_ketersediaan.csv`: ketersediaan seri x periode x rincian.
2. `reports/profil/pembanding_dimensi_ilo.csv`: dimensi dan kode yang ada di tabel ILO.
3. `reports/profil/pembanding_kandidat.csv`: kandidat rincian sebanding, tahun irisan, dan alasan.

## 2. Ketersediaan seri x periode x rincian

| Seri | Sumber | Periode | Jumlah tahun | Tahun bolong | Proyeksi | Rincian | Satuan |
|---|---|---|---|---|---|---|---|
| SDG_0821_NOC_RT | ILOSTAT | 2000-2027 | 28 | tidak ada | 2027 | tanpa dimensi rincian (IDN, tahunan) | persen (PT, UNIT_MULT 0) |
| SDG_B821_NOC_RT | ILOSTAT | 2000-2027 | 28 | tidak ada | 2027 | tanpa dimensi rincian (IDN, tahunan) | persen (PT, UNIT_MULT 0) |
| SDG_0922_NOC_RT | ILOSTAT | 2000-2023 | 24 | tidak ada | tidak ada | tanpa dimensi rincian (IDN, tahunan) | persen (PT, UNIT_MULT 0) |
| SL.GDP.PCAP.EM.KD | WDI | 1991-2025 | 35 | tidak ada | tidak ada | hanya negara (IDN) | dolar PPP konstan 2021 (tingkat) |
| NV.IND.MANF.ZS | WDI | 1983-2025 | 43 | tidak ada | tidak ada | hanya negara (IDN) | persen PDB |

Catatan per seri:

- **SDG_0821_NOC_RT**: laju pertumbuhan tahunan output per pekerja (SDG 8.2.1), estimasi model ILO, PDB konstan 2015 dolar AS. Tidak ada observasi berstatus khusus.
- **SDG_B821_NOC_RT**: laju pertumbuhan tahunan output per pekerja (SDG 8.2.1), estimasi model ILO, PDB konstan 2021 dolar internasional PPP. Tidak ada observasi berstatus khusus.
- **SDG_0922_NOC_RT**: proporsi tenaga kerja manufaktur terhadap total tenaga kerja (SDG 9.2.2, klasifikasi ISIC). Status observasi B (patahan seri, catatan ILO: "Break in series: Methodology revised") muncul pada tiga tahun: 2008 (12,214), 2013 (13,505), dan 2021 (13,918).
- **SL.GDP.PCAP.EM.KD**: PDB per pekerja (GDP per person employed, constant 2021 PPP $). Ini berupa tingkat, bukan laju.
- **NV.IND.MANF.ZS**: nilai tambah manufaktur (Manufacturing, value added, % of GDP), mengacu ISIC Rev. 3 divisi C.

Catatan satuan:

1. Seri ILO memiliki kolom satuan sendiri (UNIT_MEASURE PT dan UNIT_MULT 0), yaitu persen tanpa pengali.
2. Untuk WDI, kolom satuan kosong, baik di berkas data maupun di metadata (`sumber2_indikator.json`). Satuan ditetapkan dari nama indikator, bukan dari kolom unit. Karena itu kolom `satuan_sumber` untuk dua seri WDI di CSV kosong, dan satuan di atas berasal dari nama indikator.

## 3. Rincian yang tersedia

1. Ketiga seri ILO hanya memuat satu deret: Indonesia (REF_AREA IDN), tahunan (FREQ A), satu ukuran (MEASURE), satuan PT, UNIT_MULT 0. Tabelnya tidak punya dimensi jenis kelamin, umur, daerah, atau kategori ekonomi. `pembanding_dimensi_ilo.csv` menunjukkan setiap dimensi hanya punya satu nilai.
2. Kedua seri WDI hanya dibedakan menurut negara, dan hanya baris Indonesia yang dipakai.
3. Seri utama BPS juga hanya punya rincian total (kolom turvar seluruhnya "Tidak ada").

Kesimpulan: tidak ada pilihan rincian yang harus dipilih pada tahap 6. Seluruh pembanding sejajar dengan rincian total seri utama.

## 4. Tahun yang beririsan dengan seri utama

Dasar irisan untuk kelima pasangan adalah baris Indonesia di seri utama, bukan rentang provinsi.

| Seri utama | Pembanding | Periode pembanding | Irisan | Jumlah tahun |
|---|---|---|---|---|
| var1161 (2011-2025) | SDG_0821_NOC_RT | 2000-2027 | 2011-2025 | 15 |
| var1161 (2011-2025) | SDG_B821_NOC_RT | 2000-2027 | 2011-2025 | 15 |
| var1161 (2011-2025) | SL.GDP.PCAP.EM.KD | 1991-2025 | 2011-2025 | 15 |
| var1214 (2010-2023) | NV.IND.MANF.ZS | 1983-2025 | 2010-2023 | 14 |
| var2755 (2018-2025) | SDG_0922_NOC_RT | 2000-2023 | 2018-2023 | 6 |

var1344 tidak punya pembanding nasional di daftar panduan kelompok.

Keterangan:

1. Tahun 2026 dan 2027 pada ILO tidak ikut irisan var1161 karena di luar rentang var1161. Tahun 2027 juga berstatus proyeksi.
2. Untuk SL.GDP.PCAP.EM.KD, irisan 2011-2025 berlaku setelah laju dihitung. Laju tahun 2011 memerlukan nilai 2010, yang tersedia karena WDI mulai 1991.
3. var2755 hanya beririsan sampai 2023 karena SDG_0922_NOC_RT berhenti di 2023. Tahun 2024 dan 2025 di var2755 tidak punya pembanding.

## 5. Rincian kandidat sebanding dan alasannya

Tabel lengkap: `reports/profil/pembanding_kandidat.csv`.

| Pembanding | Seri utama | Irisan | Kandidat | Alasan dan catatan |
|---|---|---|---|---|
| SDG_0821_NOC_RT | var1161 | 2011-2025 | ya | Tanpa dimensi rincian, wilayah Indonesia, tahunan, ada tahun irisan. Basis PDB konstan 2015 dolar AS. |
| SDG_B821_NOC_RT | var1161 | 2011-2025 | ya | Alasan sama. Basis PDB konstan 2021 dolar internasional PPP. |
| SL.GDP.PCAP.EM.KD | var1161 | 2011-2025 | ya, setelah laju dihitung | Alasan sama. Berupa tingkat, bukan laju. Dasar PPP sama dengan SDG_B821. |
| NV.IND.MANF.ZS | var1214 | 2010-2023 | ya | Alasan sama. Persen PDB. Dasar harga belum terjelaskan. |
| SDG_0922_NOC_RT | var2755 | 2018-2023 | ya | Alasan sama. Irisan hanya sampai 2023. Ada patahan seri pada 2021. |

Penanda "ya" hanya berlaku untuk empat kriteria: rincian (tanpa dimensi atau berkode total), wilayah (Indonesia), frekuensi (tahunan), dan adanya tahun irisan. Kesamaan definisi belum diperiksa pada tahap ini dan ditentukan di tahap 6 berdasarkan catatan di bagian 6.

## 6. Catatan untuk tahap 6

1. **var1161 dengan SDG_0821 dan SDG_B821.** Keduanya laju pertumbuhan tahunan output per pekerja dan merupakan estimasi model ILO, sedangkan var1161 berasal dari BPS. Bedanya, SDG_0821 memakai PDB konstan 2015 dolar AS dan SDG_B821 memakai PDB konstan 2021 dolar internasional PPP. Selisih terhadap var1161 kemungkinan masuk kategori definisi atau metode, dan harus dibuktikan dari angka, bukan diasumsikan.
2. **var1161 dengan SL.GDP.PCAP.EM.KD.** Seri WDI ini berupa tingkat (konstan 2021 PPP). Laju harus dihitung dulu dan caranya dicatat sebelum dibandingkan. Dasar PPP-nya sama dengan SDG_B821, sehingga pasangan ini paling dekat dengan SDG_B821.
3. **var1214 dengan NV.IND.MANF.ZS.** NV.IND.MANF.ZS adalah persen PDB (ISIC Rev. 3 divisi C). Dasar harga tidak dinyatakan di metadata WDI yang tersedia. Dasar harga var1214 juga belum diketahui karena unit dan definisi di metadata BPS kosong. Keduanya perlu ditelusuri sebelum membandingkan. Catatan BPS: var1214 tahun 2022 berstatus angka sementara dan 2023 angka sangat sementara.
4. **var2755 dengan SDG_0922.** Sesuai catatan ILO, angkanya dapat berbeda dari angka nasional karena perbedaan sumber dan tahun referensi. Irisan hanya 2018 sampai 2023 (6 tahun). Seri ILO memiliki patahan seri (metodologi direvisi) pada 2008, 2013, dan 2021. Tahun 2021 berada di dalam irisan, jadi perubahan selisih terhadap var2755 sekitar 2021 perlu diperiksa sebagai kemungkinan perbedaan metode sebelum dinyatakan belum terjelaskan.
5. **Proyeksi.** Tahun 2027 pada SDG_0821 dan SDG_B821 dikeluarkan dari rekonsiliasi.
6. **Satuan.** Satuan ILO diambil dari kolom UNIT_MEASURE dan UNIT_MULT. Satuan WDI ditetapkan dari nama indikator karena kolom unit kosong. Bila ada keputusan yang mengubah atau menafsirkan data (misalnya cara menghitung laju WDI), catat satu baris di `log-keputusan.csv` saat keputusan dibuat.

## 7. Keterbatasan

1. Penanda kandidat sebanding adalah heuristik sederhana (rincian, wilayah, frekuensi, tahun) dan belum menilai kesamaan definisi.
2. Batas proyeksi (setelah 2026) mengikuti panduan kelompok, yaitu angka yang melewati tahun berjalan.
3. Dasar harga NV.IND.MANF.ZS dan var1214 belum terjelaskan.
4. Kecocokan basis PDB ILO dengan BPS belum diuji secara numerik. Pengujian dilakukan di tahap 6.
<<<<<<< HEAD
5. Patahan seri ILO pada 2021 dalam irisan SDG_0922 dengan var2755 belum diuji pengaruhnya terhadap selisih. Pengujian dilakukan di tahap 6.
=======
5. Patahan seri ILO pada 2021 dalam irisan SDG_0922 dengan var2755 belum diuji pengaruhnya terhadap selisih. Pengujian dilakukan di tahap 6.
>>>>>>> 6c3a75eca90542af1ad4022572bda1878c0c0262
