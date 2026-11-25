"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim.

Keluaran: data/gold/*.parquet (panel provinsi x tahun x indikator siap analisis, plus tabel
rekonsiliasi dengan pembanding nasional) dan basis data SQL (mis. data/gold/gold.sqlite).
"""
import pandas as pd
from .pemilihan import terapkan_aturan_gold

def jalankan(silver):
    """
    Fungsi utama untuk menjalankan seluruh proses Gold Layer.
    Ini akan dipanggil oleh pipeline.py
    """
    print("=== MEMULAI PROSES GOLD (TAHAP 4, 5, & 6) ===")
    
    # --- TAHAP 4: ATURAN PEMILIHAN (SNAPSHOT, RINCIAN, TAHUN) ---
    print("-> Menerapkan aturan pemilihan panel (Tahap 4)...")
    
    # Cek apakah 'silver' berupa dataframe atau path file
    if isinstance(silver, pd.DataFrame):
        df_silver = silver
    elif isinstance(silver, dict) and 'data' in silver:
        df_silver = silver['data']
    else:
        df_silver = pd.read_parquet(silver)
        
    # Panggil fungsi dari pemilihan.py
    df_gold = terapkan_aturan_gold(df_silver)
    
    # --- TAHAP 5: SIMPAN KE DATABASE DUCKDB ---
    print("-> Memuat data ke DuckDB (Tahap 5)...")
    # PENTING: Import dilakukan di dalam fungsi untuk menghindari circular import
    from . import muat_sql
    
    # PERBAIKAN: Buang kolom baru (is_outlier & nilai_zscore) agar tidak bentrok dengan skema SQL
    df_untuk_sql = df_gold.drop(columns=['is_outlier', 'nilai_zscore'], errors='ignore')
    muat_sql.jalankan(df_untuk_sql)
    
    # --- TAHAP 6: BUAT TABEL NASIONAL ---
    print("-> Membuat Tabel Nasional (Tahap 6)...")
    try:
        # PENTING: Import juga dilakukan di dalam fungsi
        from . import nasional
        nasional.jalankan(df_gold)
    except Exception as e:
        print(f"   [Peringatan] Tahap 6 gagal dilewati: {e}")

    print("=== PROSES GOLD SELESAI ===")
    
    # Kembalikan dataframe Gold untuk dilempar ke validasi
    return df_gold