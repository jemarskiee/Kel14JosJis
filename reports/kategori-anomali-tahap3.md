# Laporan Pemprofilan dan Kategorisasi Data (Tahap 3)

## 1. Ringkasan Eksekutif

Eksekusi modul `src.silver.kategori_tahap3` telah selesai dijalankan untuk melakukan inventarisasi sumber data, deduplikasi lintas format dan *snapshot*, deteksi patahan struktural (*structural breaks*), kategorisasi anomali, serta penyaringan data proyeksi internasional.

* **Integritas Data BPS:** Tidak ditemukan konflik nilai dalam *snapshot* yang sama maupun revisi antar *snapshot* (`0` konflik, `0` revisi). Angka yang sama persis di dua sumber dikategorikan sebagai salinan sah (`sama_bukan_duplikat_salah`).
* **Patahan Struktural:** Tidak ada periode tahun yang memenuhi kriteria aturan patahan serentak (`0` tahun).
* **Kategorisasi Anomali:** Seluruh **149** titik anomali yang teridentifikasi diklasifikasikan sebagai **`outlier_asli`** (variasi ekstrem yang valid secara substantif, bukan galat input atau perubahan metodologi).
* **Penyaringan Proyeksi:** Sebanyak **2** rekaman data proyeksi tahun 2027 dari ILOSTAT telah dikeluarkan dari proses rekonsiliasi.

---

## 2. Inventarisasi dan Seleksi Sumber Data

Dari total **22 berkas** yang dipindai di direktori sumber data, sebanyak **10 tabel BPS** digunakan sebagai seri target utama, sementara **12 tabel lainnya** (WDI, ILOSTAT, serta berkas metadata/DSD) dilewati pada tahap pemprofilan seri BPS ini.

### 2.1. Tabel Seri Target yang Dipakai (BPS)

| No. | Jalur Berkas | Format | *Snapshot* | Kode Seri | Jumlah Baris |
| :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | `bps/2026-10-17/sdg8_produktivitas.csv` | CSV | 2026-10-17 | `var1161` | 524 |
| 2 | `bps/2026-10-17/json/sdg8_produktivitas.json` | JSON | 2026-10-17 | `var1161` | 526 |
| 3 | `bps/2026-10-17/sdg9_9_2_2_v2755.csv` | CSV | 2026-10-17 | `var2755` | 288 |
| 4 | `bps/2026-10-17/json/sdg9_9_2_2_v2755.json` | JSON | 2026-10-17 | `var2755` | 288 |
| 5 | `bps/2026-10-20/sdg2_2_3_1_a_v1344.csv` | CSV | 2026-10-20 | `var1344` | 315 |
| 6 | `bps/2026-10-20/json/sdg2_2_3_1_a_v1344.json` | JSON | 2026-10-20 | `var1344` | 315 |
| 7 | `bps/2026-10-20/sdg9_9_2_1_v1214.csv` | CSV | 2026-10-20 | `var1214` | 494 |
| 8 | `bps/2026-10-20/json/sdg9_9_2_1_v1214.json` | JSON | 2026-10-20 | `var1214` | 494 |
| 9 | `bps/2026-10-20/sdg9_9_2_2_v2755.csv` | CSV | 2026-10-20 | `var2755` | 288 |
| 10 | `bps/2026-10-20/json/sdg9_9_2_2_v2755.json` | JSON | 2026-10-20 | `var2755` | 288 |

> **Catatan Teknis:** Terdapat selisih **2 baris** antara berkas `sdg8_produktivitas.csv` (524 baris) dan `sdg8_produktivitas.json` (526 baris) pada *snapshot* `2026-10-17`. Selisih ini terkonfirmasi pada tahap deduplikasi sebagai kunci unik berstatus `tunggal`.

### 2.2. Tabel yang Dilewati (12 Berkas)

* **World Development Indicators (WDI) — 5 berkas:** `kelompok-02-hal-01.json` (66 baris), `kelompok-06-hal-01.json` (66 baris), `sumber.json` (71 baris), `sumber2_indikator.json` (2 baris), dan `sumber46_indikator.json` (2 baris).
* **ILOSTAT — 7 berkas:** `DF_SDG_0821_NOC_RT.csv` (28 baris), `DF_SDG_0922_NOC_RT.csv` (24 baris), `DF_SDG_B821_NOC_RT.csv` (28 baris), 3 berkas DSD JSON (masing-masing 1 baris), dan `dataflow.json` (1.215 baris).

---

## 3. Hasil Deduplikasi dan Konsistensi *Snapshot*

Evaluasi kunci dilakukan untuk memeriksa duplikasi antar format (CSV vs. JSON) serta konsistensi nilai antar tanggal pengambilan data (*snapshot* `2026-10-17` dan `2026-10-20`). Sesuai panduan, angka yang sama persis di dua sumber bukanlah duplikat yang salah, melainkan salinan sah.

| Kode Seri | Status Kunci | Jumlah Kunci ($n$) | Keterangan |
| :--- | :--- | :---: | :--- |
| `var1161` | `sama_bukan_duplikat_salah` | 524 | Konsisten antara format CSV dan JSON |
| `var1161` | `tunggal` | 2 | Hanya terdapat pada sumber JSON `2026-10-17` |
| `var1214` | `sama_bukan_duplikat_salah` | 494 | Konsisten antara format CSV dan JSON |
| `var1344` | `sama_bukan_duplikat_salah` | 315 | Konsisten antara format CSV dan JSON |
| `var2755` | `sama_bukan_duplikat_salah` | 288 | Konsisten lintas format dan *snapshot* |
| **Total** | | **1.623** | **Konflik: 0 \| Revisi antar *snapshot*: 0** |

**Temuan Utama:**
* Tidak ditemukan konflik nilai dalam *snapshot* yang sama (`calon galat = 0`).
* Tidak ditemukan perubahan atau revisi angka antara *snapshot* `2026-10-17` dan `2026-10-20` untuk seri yang tumpang tindih (`var2755`). Bukti rincian tersimpan di `reports/profil/dedup_kunci.csv`.

---

## 4. Analisis Patahan Struktural dan Pergerakan Serentak

Pemeriksaan aturan patahan bertujuan mendeteksi pergeseran tingkat (*level shift*) yang terjadi secara serentak di mayoritas provinsi pada tahun tertentu. Berdasarkan evaluasi terhadap nilai $|z_{\text{robust}}|$ dan proporsi arah perubahan (`persen_searah`), **tidak ada tahun yang lolos aturan patahan** (`calon_patahan = False` di seluruh seri).

Berikut adalah ringkasan **5 periode paling serentak** (diurutkan berdasarkan nilai mutlak $z_{\text{robust}}$ terbesar) untuk masing-masing seri:

### 4.1. Seri `var1161` (SDG 8 — Produktivitas Tenaga Kerja)

| Periode | Median Perubahan | $z_{\text{robust}}$ | Persen Searah (%) | Jumlah Provinsi ($n$) | Calon Patahan |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2017** | $6,775$ | $1,42$ | $79,4\%$ | 34 | `False` |
| **2020** | $-6,015$ | $-1,19$ | $94,1\%$ | 34 | `False` |
| **2018** | $-5,015$ | $-0,98$ | $85,3\%$ | 34 | `False` |
| **2021** | $4,130$ | $0,88$ | $91,2\%$ | 34 | `False` |
| **2013** | $3,890$ | $0,84$ | $81,8\%$ | 33 | `False` |

* **Interpretasi:** Tahun 2020 menunjukkan kontraksi paling serentak secara nasional ($94,1\%$ provinsi mengalami penurunan dengan median $-6,015$), diikuti pemulihan serentak pada 2021 ($91,2\%$ provinsi naik). Namun, karena besarnya $z_{\text{robust}}$ masih berada dalam batas wajar ($|z_{\text{robust}}| \le 1,42$), fluktuasi ini mencerminkan guncangan ekonomi makro (pandemi COVID-19), bukan patahan definisi statistik.

### 4.2. Seri `var1214` (SDG 9.2.1 — Proporsi Nilai Tambah Manufaktur)

| Periode | Median Perubahan | $z_{\text{robust}}$ | Persen Searah (%) | Jumlah Provinsi ($n$) | Calon Patahan |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2021** | $0,060$ | $2,81$ | $52,9\%$ | 34 | `False` |
| **2019** | $-0,145$ | $-1,80$ | $61,8\%$ | 34 | `False` |
| **2023** | $-0,135$ | $-1,57$ | $64,7\%$ | 34 | `False` |
| **2013** | $0,005$ | $1,57$ | $50,0\%$ | 34 | `False` |
| **2017** | $-0,010$ | $1,24$ | $50,0\%$ | 34 | `False` |

* **Interpretasi:** Meskipun tahun 2021 memiliki skor $z_{\text{robust}} = 2,81$, tingkat keserentakan antar provinsi hanya $52,9\%$ (hampir berimbang antara provinsi yang naik dan turun), sehingga tidak dikategorikan sebagai patahan struktural.

### 4.3. Seri `var1344` (SDG 2.3.1.a — Produktivitas Pertanian Skala Kecil)

| Periode | Median Perubahan | $z_{\text{robust}}$ | Persen Searah (%) | Jumlah Provinsi ($n$) | Calon Patahan |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2020** | $-2.155.103,765$ | $-2,29$ | $58,8\%$ | 34 | `False` |
| **2023** | $6.495.614,205$ | $1,21$ | $88,2\%$ | 34 | `False` |
| **2019** | $1.210.625,140$ | $-0,93$ | $76,5\%$ | 34 | `False` |
| **2016** | $5.512.842,170$ | $0,82$ | $91,2\%$ | 34 | `False` |
| **2021** | $4.815.109,610$ | $0,53$ | $88,2\%$ | 34 | `False` |

* **Interpretasi:** Penurunan median terbesar terjadi pada 2020 ($-2,16 \times 10^6$ dengan $z_{\text{robust}} = -2,29$), sementara ekspansi serentak terjadi pada 2016 ($91,2\%$), 2021 ($88,2\%$), dan 2023 ($88,2\%$).

### 4.4. Seri `var2755` (SDG 9.2.2 — Proporsi Tenaga Kerja Manufaktur)

| Periode | Median Perubahan | $z_{\text{robust}}$ | Persen Searah (%) | Jumlah Provinsi ($n$) | Calon Patahan |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2020** | $-0,365$ | $-0,87$ | $79,4\%$ | 34 | `False` |
| **2021** | $0,375$ | $0,80$ | $76,5\%$ | 34 | `False` |
| **2019** | $0,330$ | $0,70$ | $67,6\%$ | 34 | `False` |
| **2022** | $-0,280$ | $-0,67$ | $64,7\%$ | 34 | `False` |
| **2023** | $0,090$ | $0,16$ | $52,9\%$ | 34 | `False` |

* **Interpretasi:** Seri `var2755` menunjukkan stabilitas paling tinggi dibandingkan seri lainnya, dengan nilai $|z_{\text{robust}}| < 1$ di seluruh periode pengamatan.

---

## 5. Kategorisasi Anomali

Karena tidak ditemukan konflik data maupun patahan struktural akibat perubahan metodologi, seluruh titik ekstrem yang terdeteksi pada observasi tingkat provinsi diklasifikasikan ke dalam kategori **`outlier_asli`**. Tabel lengkap dengan alasan per baris dapat dilihat di `reports/profil/anomali_berkategori.csv`.

| Kode Seri | Kategori Anomali | Jumlah Titik | Proporsi (%) |
| :--- | :--- | :---: | :---: |
| `var1161` | `outlier_asli` | 43 | $28,86\%$ |
| `var2755` | `outlier_asli` | 37 | $24,83\%$ |
| `var1344` | `outlier_asli` | 36 | $24,16\%$ |
| `var1214` | `outlier_asli` | 33 | $22,15\%$ |
| **Total** | **`outlier_asli`** | **149** | **$100,00\%$** |

---

## 6. Penyaringan Data Proyeksi ILOSTAT (Pasca-2026)

Pada dataset pembanding internasional dari ILOSTAT, teridentifikasi entri yang merupakan angka proyeksi untuk tahun setelah 2026. Untuk menjaga validitas perbandingan terhadap data realisasi/historis BPS, rekaman tersebut dikeluarkan secara otomatis dari tahap rekonsiliasi. Rincian ada di `reports/profil/proyeksi_ilo.csv`.

| No. | Kode Seri ILOSTAT | Tahun | Status | Tindakan |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `SDG_0821_NOC_RT` | 2027 | `proyeksi` | `dikeluarkan_dari_rekonsiliasi` |
| 2 | `SDG_B821_NOC_RT` | 2027 | `proyeksi` | `dikeluarkan_dari_rekonsiliasi` |

---

## 7. Kesimpulan dan Rekomendasi Tindak Lanjut

1. **Pertahankan Nilai `outlier_asli`:** Sebanyak **149** titik anomali yang teridentifikasi merupakan karakteristik asli variasi antarprovinsi (misalnya provinsi dengan konsentrasi industri pengolahan atau pertambangan yang tinggi). Nilai-nilai ini **tidak boleh dihapus atau diimputasi** pada tahap pembersihan data, melainkan cukup diberi penanda (*flag*) untuk keperluan pemodelan atau analisis sensitivitas.
2. **Verifikasi 2 Kunci Tunggal pada `var1161`:** Lakukan pemeriksaan singkat terhadap 2 baris tambahan yang hanya ada di `sdg8_produktivitas.json` (kemungkinan agregat tingkat nasional/"INDONESIA" atau wilayah administratif tambahan) agar skema penyatuan CSV dan JSON tetap konsisten.
3. **Kesiapan Tahap Rekonsiliasi:** Dengan `0` konflik *snapshot* dan telah tersaringnya data proyeksi tahun 2027 dari ILOSTAT, dataset seri target BPS telah bersih dan siap dilanjutkan ke tahap rekonsiliasi lintas sumber (BPS vs. WDI/ILOSTAT).
4. **Rujukan Log Keputusan:** Seluruh aturan dan hasil keputusan deduplikasi, deteksi patahan, kategorisasi anomali, serta penyaringan proyeksi telah dicatat secara eksplisit di dalam `log-keputusan.csv` pada baris **K-024 sampai K-027**.


### Keterkaitan Log Keputusan dan Kategori Anomali
Untuk menjaga transparansi, alur keputusan ini dirujuk secara eksplisit:
1. **Deduplikasi:** Kunci yang sama persis di dua snapshot diberi status `sama_bukan_duplikat_salah`, sedangkan angka yang berbeda (delta > 1e-9) diberi status `revisi_antar_snapshot` (Rujukan Log: **K-029**). 
2. **Konflik Nilai:** Konflik antar format (CSV vs JSON di hari yang sama) dicek secara otomatis. Jika ada, baris tersebut akan masuk sebagai `galat_input`. Karena hasil pengecekan adalah 0, maka 0 baris yang terdampak konflik (Rujukan Log: **K-030**).
3. **Patahan Seri:** Pengecekan lonjakan serentak antarprovinsi menunjukkan 0 tahun yang memenuhi kriteria. Oleh karena itu, tidak ada anomali yang dikategorikan sebagai patahan seri (Rujukan Log: **K-031**).
4. **Kategori Anomali:** Karena bersih dari konflik dan patahan, seluruh 149 anomali divalidasi sebagai karakteristik asli data (outlier asli) dan hanya ditandai tanpa diubah nilainya (Rujukan Log: **K-028**). Data per baris dapat dilihat pada `reports/profil/anomali_berkategori.csv`.