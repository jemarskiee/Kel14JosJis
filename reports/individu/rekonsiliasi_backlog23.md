# Rekonsiliasi Tabel Nasional Gold – Backlog 23

## 1. Tujuan

Rekonsiliasi dilakukan untuk memeriksa kesesuaian angka seri utama BPS dengan seri pembanding dari ILOSTAT dan World Bank (WDI) pada periode yang benar-benar beririsan. Perbandingan menggunakan keluaran `data/gold/tabel_nasional_gold.parquet` hasil pipeline.

## 2. Ringkasan periode irisan

| Seri utama | Seri pembanding | Periode irisan | Jumlah tahun |
|---|---|---:|---:|
| `var1161` | `SDG_0821_NOC_RT` | 2011–2025 | 15 |
| `var1161` | `SDG_B821_NOC_RT` | 2011–2025 | 15 |
| `var1161` | `SL.GDP.PCAP.EM.KD` | 2011–2025 | 15 |
| `var1214` | `NV.IND.MANF.ZS` | 2010–2023 | 14 |
| `var2755` | `SDG_0922_NOC_RT` | 2018–2023 | 6 |

*Catatan: Angka ditampilkan hingga tiga angka desimal. Selisih dihitung dari nilai asli sebelum pembulatan.*

## 3. Hasil perbandingan angka

### var1161 dengan SDG_0821_NOC_RT

Indikator yang diperiksa: Pertumbuhan produktivitas tenaga kerja.

| Tahun | Nilai BPS | Nilai pembanding | Selisih (BPS - pembanding) |
|---:|---:|---:|---:|
| 2011 | 6.950 | 3.513 | 3.437 |
| 2012 | 1.230 | 2.883 | -1.653 |
| 2013 | 5.320 | 4.860 | 0.460 |
| 2014 | 3.300 | 3.402 | -0.102 |
| 2015 | 4.700 | 4.018 | 0.682 |
| 2016 | 1.850 | 3.820 | -1.970 |
| 2017 | 2.800 | 2.557 | 0.243 |
| 2018 | 0.790 | 3.013 | -2.223 |
| 2019 | 3.000 | 1.959 | 1.041 |
| 2020 | -1.840 | -1.350 | -0.490 |
| 2021 | 1.650 | 4.537 | -2.887 |
| 2022 | 2.000 | 1.930 | 0.070 |
| 2023 | 1.630 | 2.189 | -0.559 |
| 2024 | 1.550 | 3.663 | -2.113 |
| 2025 | 3.750 | 3.434 | 0.316 |

### var1161 dengan SDG_B821_NOC_RT

Indikator yang diperiksa: Pertumbuhan produktivitas tenaga kerja (basis PPP 2021).

| Tahun | Nilai BPS | Nilai pembanding | Selisih (BPS - pembanding) |
|---:|---:|---:|---:|
| 2011 | 6.950 | 3.513 | 3.437 |
| 2012 | 1.230 | 2.883 | -1.653 |
| 2013 | 5.320 | 4.860 | 0.460 |
| 2014 | 3.300 | 3.402 | -0.102 |
| 2015 | 4.700 | 4.018 | 0.682 |
| 2016 | 1.850 | 3.820 | -1.970 |
| 2017 | 2.800 | 2.557 | 0.243 |
| 2018 | 0.790 | 3.013 | -2.223 |
| 2019 | 3.000 | 1.959 | 1.041 |
| 2020 | -1.840 | -1.350 | -0.490 |
| 2021 | 1.650 | 4.537 | -2.887 |
| 2022 | 2.000 | 1.930 | 0.070 |
| 2023 | 1.630 | 2.189 | -0.559 |
| 2024 | 1.550 | 3.663 | -2.113 |
| 2025 | 3.750 | 3.434 | 0.316 |

### var1161 dengan SL.GDP.PCAP.EM.KD

Indikator yang diperiksa: GDP per orang bekerja.

**Catatan: kedua indikator tidak sebanding secara langsung.** BPS `var1161` menunjukkan laju pertumbuhan GDP riil per orang bekerja, sedangkan WDI `SL.GDP.PCAP.EM.KD` menunjukkan tingkat GDP per orang bekerja dalam constant 2021 PPP dollars. Karena konsep dan satuannya berbeda, selisih numerik tidak dihitung atau ditafsirkan.

| Tahun | Nilai BPS | Nilai WDI |
|---:|---:|---:|
| 2011 | 6.950 | 20220.222 |
| 2012 | 1.230 | 20802.931 |
| 2013 | 5.320 | 21813.860 |
| 2014 | 3.300 | 22556.112 |
| 2015 | 4.700 | 23462.490 |
| 2016 | 1.850 | 24358.599 |
| 2017 | 2.800 | 24981.549 |
| 2018 | 0.790 | 25734.224 |
| 2019 | 3.000 | 26237.973 |
| 2020 | -1.840 | 25884.279 |
| 2021 | 1.650 | 27058.283 |
| 2022 | 2.000 | 27580.802 |
| 2023 | 1.630 | 28184.252 |
| 2024 | 1.550 | 29217.284 |
| 2025 | 3.750 | 30291.798 |

### var1214 dengan NV.IND.MANF.ZS

Indikator yang diperiksa: Proporsi nilai tambah manufaktur terhadap PDB.

| Tahun | Nilai BPS | Nilai pembanding | Selisih (BPS - pembanding) |
|---:|---:|---:|---:|
| 2010 | 22.040 | 22.039 | 0.001 |
| 2011 | 22.060 | 21.761 | 0.299 |
| 2012 | 21.970 | 21.451 | 0.519 |
| 2013 | 21.720 | 21.029 | 0.691 |
| 2014 | 21.650 | 21.075 | 0.575 |
| 2015 | 21.540 | 20.986 | 0.554 |
| 2016 | 21.380 | 20.523 | 0.857 |
| 2017 | 21.220 | 20.160 | 1.060 |
| 2018 | 21.040 | 19.863 | 1.177 |
| 2019 | 20.790 | 19.704 | 1.086 |
| 2020 | 20.610 | 19.866 | 0.744 |
| 2021 | 20.550 | 19.243 | 1.307 |
| 2022 | 20.470 | 18.336 | 2.134 |
| 2023 | 20.390 | 18.667 | 1.723 |

### var2755 dengan SDG_0922_NOC_RT

Indikator yang diperiksa: Proporsi tenaga kerja sektor manufaktur.

| Tahun | Nilai BPS | Nilai pembanding | Selisih (BPS - pembanding) |
|---:|---:|---:|---:|
| 2018 | 14.680 | 14.391 | 0.289 |
| 2019 | 14.910 | 14.383 | 0.527 |
| 2020 | 13.610 | 13.779 | -0.169 |
| 2021 | 14.270 | 13.918 | 0.352 |
| 2022 | 14.170 | 13.966 | 0.204 |
| 2023 | 13.830 | 13.698 | 0.132 |

## 4. Analisis penyebab perbedaan

1. **`var1161` dengan `SDG_0821_NOC_RT`:** BPS menyajikan laju pertumbuhan produktivitas tenaga kerja nasional, sedangkan ILO menggunakan modelled estimates yang diharmonisasi untuk memperhitungkan perbedaan data nasional, cakupan, dan metode pengumpulan maupun tabulasi. Perbedaan angka dapat berkaitan dengan proses harmonisasi tersebut.

2. **`var1161` dengan `SDG_B821_NOC_RT`:** indikator sama-sama mengukur pertumbuhan output per pekerja, tetapi metadata ILO menunjukkan basis GDP yang berbeda. `SDG_0821_NOC_RT` menggunakan GDP konstan 2015 USD, sedangkan `SDG_B821_NOC_RT` menggunakan GDP konstan 2021 international dollars berdasarkan PPP. Pada keluaran yang diperiksa, nilai kedua seri ILO tercatat sama untuk seluruh 15 tahun irisan. Kesamaan angka pada snapshot ini tidak berarti definisi basisnya identik.

3. **`var1161` dengan `SL.GDP.PCAP.EM.KD`:** tidak dapat direkonsiliasi sebagai selisih nilai karena satu seri merupakan laju pertumbuhan, sedangkan seri WDI merupakan tingkat GDP per orang bekerja. Seri WDI hanya dapat digunakan sebagai informasi kontekstual, bukan pembanding numerik langsung.

4. **`var1214` dengan `NV.IND.MANF.ZS`:** keduanya menggambarkan kontribusi nilai tambah manufaktur terhadap PDB dalam persentase. Namun, sumber data, cakupan, klasifikasi industri, metode penyusunan, dan pembaruan data dapat menyebabkan perbedaan. Catatan BPS juga menyebutkan angka 2022 bersifat sementara dan 2023 sangat sementara. Metadata yang tersedia belum cukup untuk menetapkan satu penyebab spesifik bagi setiap selisih.

5. **`var2755` dengan `SDG_0922_NOC_RT`:** keduanya mengukur proporsi tenaga kerja sektor manufaktur. BPS menggunakan data Sakernas, sedangkan metadata ILO menjelaskan bahwa indikatornya dihitung dari data ketenagakerjaan menurut jenis kelamin dan aktivitas ekonomi. ILO juga menyatakan angka dapat berbeda dari data nasional karena perbedaan sumber atau tahun referensi. Perbedaan cakupan dan klasifikasi industri juga perlu diperhatikan.

## 5. Kesimpulan

Seluruh pasangan yang diperiksa memiliki periode irisan, tetapi tidak seluruhnya dapat dibandingkan secara langsung. Pasangan `var1161` dengan WDI `SL.GDP.PCAP.EM.KD` merupakan indikator berbeda konsep dan satuan. Pasangan lainnya dapat diperiksa berdasarkan tahun yang sama, dengan mempertimbangkan perbedaan sumber, basis penghitungan, harmonisasi, serta status revisi data. Selisih angka tidak otomatis menunjukkan kesalahan salah satu sumber.

## 6. Sumber dan batasan

- Data angka: `data/gold/tabel_nasional_gold.parquet`.
- Metadata ILO: `data/raw/ilostat/2026-10-20/dsd/`.
- Metadata indikator WDI: `data/raw/wdi/2026-10-20/metadata/`.
- Metadata dan catatan BPS: berkas JSON pada direktori `data/raw/bps/`.
- Rekonsiliasi ini menggunakan periode yang tersedia pada keluaran Gold. Penyebab selisih dijelaskan berdasarkan metadata yang tersedia; penyebab spesifik yang tidak didukung metadata tidak diasumsikan.
