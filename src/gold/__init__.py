
"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim.

Keluaran: data/gold/*.parquet (panel provinsi x tahun x indikator siap analisis, plus tabel
rekonsiliasi dengan pembanding nasional) dan basis data SQL (mis. data/gold/gold.sqlite).
"""

import pandas as pd
from src.gold import panel


def jalankan(silver):
    """
    Fungsi utama untuk menjalankan seluruh proses Gold Layer.
    Ini akan dipanggil oleh pipeline.py.
    """

    print("=== MEMULAI PROSES GOLD (TAHAP 4, 5, & 6) ===")

    # --- TAHAP 4: ATURAN PEMILIHAN PANEL GOLD ---
    print("-> Menerapkan aturan pemilihan panel (Tahap 4)...")

    # Cek apakah silver berupa dataframe atau path file
    if isinstance(silver, pd.DataFrame):
        df_silver = silver
    elif isinstance(silver, dict) and 'data' in silver:
        df_silver = silver['data']
    else:
        df_silver = pd.read_parquet(silver)

    # Jalankan proses pembentukan panel Gold
    df_gold = panel.jalankan(df_silver)

    # --- TAHAP 5: SIMPAN KE DATABASE DUCKDB ---
    print("-> Memuat data ke DuckDB (Tahap 5)...")

    # Import di dalam fungsi untuk menghindari circular import
    from . import muat_sql

    # Buang kolom yang tidak sesuai dengan skema SQL
    kolom_dibuang = [
        'indikator',
        'status_sel',
        'penanda',
        'is_outlier',
        'nilai_zscore'
    ]

    df_untuk_sql = df_gold.drop(
        columns=kolom_dibuang,
        errors='ignore'
    )

    df_untuk_sql = df_untuk_sql.dropna(subset=['nilai'])

    muat_sql.jalankan(df_untuk_sql)

    # --- TAHAP 6: BUAT TABEL NASIONAL ---
    print("-> Membuat Tabel Nasional (Tahap 6)...")

    try:
        from . import nasional
        nasional.jalankan(silver)

    except Exception as e:
        print(f"   [Peringatan] Tahap 6 gagal dilewati: {e}")

    print("=== PROSES GOLD SELESAI ===")
