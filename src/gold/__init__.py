"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim.

Keluaran: data/gold/*.parquet (panel provinsi x tahun x indikator siap analisis, plus tabel
rekonsiliasi dengan pembanding nasional) dan basis data SQL (mis. data/gold/gold.sqlite).
"""


def jalankan(silver):
    """
    Fungsi utama untuk menjalankan seluruh proses Gold Layer.
    Ini akan dipanggil oleh pipeline.py
    """
    print("=== MEMULAI PROSES GOLD (TAHAP 5 & 6) ===")
    
    # 1. Jalankan Tahap 5: Simpan ke Database DuckDB (SQL)
    print("-> Memuat Silver ke DuckDB (Tahap 5)...")
    # PENTING: Import dilakukan di dalam fungsi untuk menghindari circular import
    from . import muat_sql
    muat_sql.jalankan(silver)
    
    # 2. Jalankan Tahap 6: Buat Tabel Nasional & Laporan
    print("-> Membuat Tabel Nasional (Tahap 6)...")
    try:
        # PENTING: Import juga dilakukan di dalam fungsi
        from . import nasional
        nasional.jalankan(silver)
    except Exception as e:
        print(f"   [Peringatan] Tahap 6 gagal dilewati: {e}")

    print("=== PROSES GOLD SELESAI ===")