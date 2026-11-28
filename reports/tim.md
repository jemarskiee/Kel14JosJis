# Laporan tim — <Nama tim>, kasus <NN> <judul kasus>

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.
* **Perbandingan SQL dengan JSON mentah:** JSON mentah di `data/raw/` menyimpan respons/struktur asli sesuai `MANIFEST.csv`, tetapi belum memiliki skema kolom seragam, tipe data tegas, atau jaminan keunikan baris. Tabel SQL (`silver_indikator`, `gold_panel_provinsi`, `gold_tabel_nasional`, dan `gold_rekonsiliasi` di `sql/schema_kasus14.sql` yang dimuat dari `pipeline.py` ke SQLite) menata kolom dengan tipe data dan kunci/keunikan yang jelas sehingga mudah dikueri dan diverifikasi jumlah barisnya.
* **Alasan pilihan basis data dan kecocokan per lapisan:** SQLite dipilih karena berjalan sebagai berkas basis data lokal tanpa server terpisah dan terintegrasi langsung dengan modul `sqlite3` bawaan Python. Pendekatan SQL ini cocok untuk lapisan **Silver** (kunci unik per entitas/periode/rincian agar pemuatan aman), **Gold** (tabel panel provinsi, tabel nasional, dan rekonsiliasi yang siap dianalisis dan dicek jumlah barisnya), sementara berkas basis data besar tetap tidak di-commit ke repositori.

## Masalah data dan penanganannya
Tabel masalah yang ditemukan (missing, outlier, patahan seri, duplikat, format, wilayah) dengan
jumlah baris terdampak, keputusan, dan alternatif yang ditolak. Rujuk id di `log-keputusan.csv`.

## Integrasi dan rekonsiliasi
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
