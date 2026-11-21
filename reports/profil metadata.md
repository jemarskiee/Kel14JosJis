# Laporan Tahap 4: Validasi Metadata dan Ketertelusuran Koreksi Katalog

**NIM:** 124450077
**Tahap:** 4 (Persiapan)
**Tanggal:** 19 November 2026

## 1. Latar Belakang
Berdasarkan arahan pada Tahap 4, kode SDG dan satuan pada katalog awal masih terdapat kekosongan (`tidak_ada`). Oleh karena itu, dilakukan pengecekan ulang terhadap berkas mentah (raw) dan metadata. Seluruh koreksi yang diambil telah didokumentasikan di `log-keputusan.csv` agar dapat ditelusuri (*traceable*), dan tabel lengkapnya dapat dilihat pada `docs/seri.csv`.

## 2. Sumber Metadata dan Penelusuran Koreksi (Traceability)
Semua koreksi satuan dan kode SDG dapat ditelusuri langsung ke berkas sumber (JSON/CSV) beserta spesifikasi/baris datanya. Berikut adalah ringkasan penelusurannya:

| Seri / Indikator | Katalog Awal | Keputusan Akhir | Sumber Asal & Bukti Spesifik (Traceability) |
| :--- | :--- | :--- | :--- |
| `var1161` | Satuan: `tidak_ada` | Satuan: `persen_per_tahun` | `bps/2026-10-17/json/sdg8_produktivitas.json` (var.label). Bukti: Judul "Laju Pertumbuhan... Per Tahun" & nilai bisa negatif. |
| `var1344` | SDG: `2.3.1` | SDG: `2.3.1(a)` | `bps/2026-10-20/json/sdg2_2_3_1_a_v1344.json`. Bukti: Nama berkas secara eksplisit mencantumkan butir (a). |
| `var1214` | Satuan: `tidak_ada` | Satuan: `persen` | `bps/2026-10-20/json/sdg9_9_2_1_v1214.json`. Bukti: Judul "Proporsi... Terhadap PDB" & nilai berkisar 0–50. |
| `var2755` | Satuan: `persen` | Satuan: `persen` | `bps/2026-10-17/json/sdg9_9_2_2_v2755.json` (var.label). |
| `SL.GDP.PCAP.EM.KD` | SDG: kosong | SDG: `8.2.1` | `wdi/2026-10-20/metadata/sumber2_indikator.json`. Bukti: Tercantum di metadata `sumber46_indikator.json`. |
| `NV.IND.MANF.ZS` | SDG: kosong | SDG: `9.2.1` | `wdi/2026-10-20/metadata/sumber2_indikator.json`. Bukti: Tercantum di metadata `sumber46_indikator.json`. |
| `SDG_0821_NOC_RT` | - | Satuan: `persen_per_tahun` | `ilostat/2026-10-20/metadata/dataflow.json`. Bukti: `UNIT_MEASURE PT` & judul DSD 'Annual growth rate'. |
| `SDG_B821_NOC_RT` | - | Satuan: `persen_per_tahun` | `ilostat/2026-10-20/metadata/dataflow.json`. Bukti: Nama fisik file menggunakan huruf B, dan `UNIT_MEASURE PT`. |
| `SDG_0922_NOC_RT` | - | Satuan: `persen` | `ilostat/2026-10-20/metadata/dataflow.json`. Bukti: `UNIT_MEASURE PT`. |

*(Tabel lengkap beserta kolom `cakupan` dan `bukti_sdg` untuk seluruh seri dapat dilihat pada file `docs/seri.csv`)*

## 3. Perbedaan Nilai Awal di Laporan Profil vs Keputusan Akhir
Pada laporan profil awal, kolom satuan tercatat kosong (`tidak_ada`) karena proses ekstraksi otomatis (Tahap 1) tidak menarik metadata dari *header* atau DSD (Data Structure Definition). 
*   **Contoh `var1161`:** Laporan awal hanya menampilkan angka. Setelah ditelusuri ke `var.label`, terbukti itu adalah data laju (bisa negatif), sehingga keputusan akhirnya menjadi `persen_per_tahun`.
*   **Contoh WDI:** Kode SDG awalnya kosong, setelah dicek ke `sumber46_indikator.json`, baru ditemukan kode aslinya (`8.2.1` dan `9.2.1`).
*   **Contoh `var1344`:** Katalog awal hanya menulis `2.3.1`, namun berdasarkan nama berkas fisik (`sdg2_2_3_1_a_...`), indikator ini merujuk pada sub-indikator (a), sehingga dikoreksi menjadi `2.3.1(a)`.

Semua koreksi ini bersifat *traceable* (dapat dilacak) dan telah dicatat di `log-keputusan.csv` (K-001 s.d K-009).

## 4. Catatan Penting Terkait Kualitas Data (Cakupan)
Berdasarkan hasil validasi metadata pada berkas mentah, ditemukan catatan penting terkait status data yang menjelaskan anomali pada laporan profil:
*   Data `var1161` (2024-2025), `var1344` (2022-2023), dan `var1214` (2022-2023) berstatus sebagai **angka sementara / sangat sementara**. Hal ini memvalidasi keputusan untuk tidak melakukan intervensi/permulusan data secara sembarangan di tahap Silver.
*   Data `var2755` berasal dari Sakernas dan ada di dua snapshot. Dipilih snapshot `2026-10-20` agar tidak terjadi duplikasi data.