# Laporan tim — Kelompok 14, kasus 14 (Produktivitas tenaga kerja dan industri)

Satu dokumen bersama, enam bagian. Angka dapat ditarik ulang dari `data/silver`, `data/gold`, dan `log-keputusan.csv` yang sudah di-*commit*.

## 1. Ringkasan
**Kasus:** 14 (Produktivitas tenaga kerja dan industri).
**Seri yang ditangani:** `var1161` (SDG 8.2.1), `var1344` (SDG 2.3.1a), `var1214` (SDG 9.2.1), `var2755` (SDG 9.2.2), serta pembanding dari ILOSTAT dan WDI.
**Temuan utama:** Kualitas data BPS sangat baik dari sisi konsistensi (0 revisi antar-snapshot, 0 konflik format CSV/JSON). Namun, terdapat tantangan pada kelengkapan panel di mana 36 sel kosong (dominan karena provinsi pemekaran baru) serta 149 nilai ekstrem yang terkonfirmasi sebagai *outlier asli* (bukan galat input) akibat karakteristik ekonomi daerah.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.
* **Perbandingan SQL dengan JSON mentah:** JSON mentah di `data/raw/` menyimpan respons/struktur asli sesuai `MANIFEST.csv`, tetapi belum memiliki skema kolom seragam, tipe data tegas, atau jaminan keunikan baris. Tabel SQL (`silver_indikator`, `gold_panel_provinsi`, `gold_tabel_nasional`, dan `gold_rekonsiliasi` di `sql/schema_kasus14.sql` yang dimuat dari `pipeline.py` ke SQLite) menata kolom dengan tipe data dan kunci/keunikan yang jelas sehingga mudah dikueri dan diverifikasi jumlah barisnya.
* **Alasan pilihan basis data dan kecocokan per lapisan:** SQLite dipilih karena berjalan sebagai berkas basis data lokal tanpa server terpisah dan terintegrasi langsung dengan modul `sqlite3` bawaan Python. Pendekatan SQL ini cocok untuk lapisan **Silver** (kunci unik per entitas/periode/rincian agar pemuatan aman), **Gold** (tabel panel provinsi, tabel nasional, dan rekonsiliasi yang siap dianalisis dan dicek jumlah barisnya), sementara berkas basis data besar tetap tidak di-commit ke repositori.
## 2. Data dan lineage
- **Sumber dan format:** Data BPS diekstraksi dari 10 berkas (5 CSV dan 5 JSON) dari dua snapshot (17 dan 20 Oktober 2026). Data pembanding berasal dari 12 berkas WDI, ILOSTAT, dan metadata.
- **Lineage:** Setiap baris dipetakan dengan `_berkas_raw` (jalur file) dan `_sha256_raw` (hash validasi integritas) untuk memastikan data yang masuk ke Silver adalah data yang sah dari sumber.
- **Hasil tarik ulang API (Snapshot):** Perbandingan snapshot 17 dan 20 Oktober pada seri `var2755` (280 pasangan provinsi-periode) menunjukkan **0 perubahan** (identik). Tidak ada revisi data BPS dalam rentang waktu tersebut.

## 3. Masalah data dan penanganannya
| Masalah | Jumlah Terdampak | Keputusan | Alternatif Ditolak | Log ID |
| :--- | :--- | :--- | :--- | :--- |
| **Celah Panel (Missing)** | 36 sel | Memisahkan sel `belum_berdiri` (137), `belum_terbit` (12), dan `kosong` (24). Sel kosong dibiarkan, tidak diimputasi. | Imputasi dari provinsi induk, interpolasi. | K-011 s/d K-015 |
| **Anomali / Outlier** | 149 baris | Dikategorikan 100% sebagai `outlier_asli` (kondisi ekonomi), ditandai tanpa diubah nilainya. | Menghapus data ekstrem, menganggapnya galat. | K-026 / K-030 |
| **Patahan Seri** | 0 baris | Tidak ada lonjakan serentak antarprovinsi yang memenuhi kriteria *robust z-score* (MAD). | Menganggap guncangan COVID-19 (2020) sebagai patahan. | K-031 / K-033 |
| **Duplikasi Snapshot/Format** | 1.623 baris | Angka sama persis dianggap salinan sah (`sama_bukan_duplikat_salah`). | Menghapus salah satu snapshot tanpa pengecekan. | K-024 / K-029 |
| **Konflik Nilai** | 0 baris | Tidak ditemukan beda nilai antara CSV dan JSON pada hari yang sama. | Memilih salah satu format secara buta. | K-025 / K-032 |
| **Format & Katalog** | 1.623 baris | Melengkapi satuan yang kosong di BPS (Persen/Rupiah). Memperbaiki nama SDG B821. | Membiarkan satuan kosong (NaN). | K-002, K-020 |

## 4. Integrasi dan rekonsiliasi
- **Selisih & Penjelasan:** Seri BPS dibandingkan dengan seri pembanding (seperti ILOSTAT `SDG_0821` dan WDI `SL.GDP.PCAP.EM.KD`). WDI berupa *tingkat* (dolar PPP) harus dihitung lajunya terlebih dahulu untuk dibandingkan dengan `var1161` (yang sudah berupa laju persen). Perbedaan granularitas (BPS per provinsi, WDI/ILO per nasional) serta *vintage* data menjadi penjelas utama selisih nilai.
- **Analisis Revisi:** Arsip WDI dan ILO dari dua snapshot tidak menunjukkan revisi signifikan. Angka ILO tahun 2027 dikategorikan sebagai *proyeksi* dan dikeluarkan dari rekonsiliasi Tahap 6 (Log: K-027).

## 5. Validasi dan reproduksibilitas
- **Skema Validasi:** Data yang dimuat ke Silver telah lolos uji skema (`python -m src.common.skema`) dengan memastikan tipe data (integer untuk wilayah, float untuk nilai) dan tidak ada kolom yang hilang.
- **Waktu Pipeline & Reproduksi:** *Tertunda.* Uji coba *clone* dari repositori bersih dan pengukuran waktu `python pipeline.py` belum dapat diselesaikan karena anggota penanggung jawab (Reproduksi & Demo) sedang sakit.
- **Keterbatasan:** 
  1. Perbedaan metode pemilihan snapshot belum ditetapkan secara resmi di Gold.
  2. Angka `var1161` untuk provinsi baru di tahun 2022-2023 masih menunggu konfirmasi BPS terkait status "belum terbit".
  3. Perhitungan patahan seri menggunakan deret pendek (8-15 periode) sehingga sensitivitasnya terbatas.

## 6. Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
| :--- | :--- | :--- | :--- | :--- |
| **Salsabila Nazwa Putri** | 124450002 | Penjaga Data & Evaluasi (Ekstraksi) | - | Data dan lineage |
| **Yollanda Agustina** | 124450024 | Reproduksi & Demo (Integrasi) | Uji clone dari nol dan rekam video demo (sedang sakit) | Integrasi dan rekonsiliasi |
| **Suci Aulia ** | 124450034 | Analis Utama (Profil & Pembersihan) | Resolusi konflik log & metrik | Masalah data dan penanganannya, Validasi |
| **Indah Khairunnisa** | 124450077 | Integrator (Transformasi & panel) | - | - |
| **Jeremi Marolop Partogi Situmorang** | 124450111 | Koordinator (Validasi & dokumentasi) | - | Ringkasan & Pembagian kerja |