# Laporan Persiapan Tahap 5: Rancangan Tabel SQL & Pemuatan Silver

## 1. Alasan Memilih DuckDB
Kami memilih **DuckDB** sebagai basis data untuk lapisan Silver ini karena beberapa alasan:
*   **Performa Analitik (OLAP):** DuckDB dioptimalkan untuk pemrosesan analitik berbasis kolom (columnar), sehingga sangat cepat dalam melakukan query agregasi pada data berukuran besar.
*   **Integrasi Mudah (In-Process):** DuckDB dapat berjalan langsung di dalam lingkungan Python (tanpa perlu setup server database terpisah) dan terintegrasi mulus dengan Pandas DataFrame (seperti pada skrip `muat_sql.py`).
*   **Validasi Ketat:** DuckDB mendukung penuh standar SQL untuk *Primary Key*, *Foreign Key*, dan *Check Constraints*. Ini sangat penting sebagai "lapis validasi terakhir" agar data yang masuk benar-benar bersih dan konsisten.

## 2. Perbandingan dengan Menyimpan JSON Mentah
Menyimpan respons JSON mentah sebagai dokumen mungkin lebih mudah di awal, tetapi sangat tidak efisien untuk kebutuhan analitik:
*   **Skema:** JSON tidak memiliki skema yang kaku (rawan inkonsistensi tipe data), sedangkan tabel SQL memaksa tipe data yang konsisten.
*   **Performa:** JSON membutuhkan proses *parsing* berulang setiap kali data ingin dianalisis, dan tidak mendukung *indexing* atau *constraints*.
*   **Kesimpulan:** Dengan mentransformasikannya ke tabel relasional di DuckDB, kita mendapatkan struktur data yang rapi, tipe data yang seragam, dan kecepatan query yang jauh lebih baik untuk kebutuhan pelaporan (Gold layer).