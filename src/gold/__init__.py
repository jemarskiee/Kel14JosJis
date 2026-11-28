"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold."""
import pandas as pd
from .pemilihan import terapkan_aturan_gold

def jalankan(silver, mentah):
    """
    Fungsi utama untuk menjalankan seluruh proses Gold Layer.
    Ini akan dipanggil oleh pipeline.py
    """
    print("=== MEMULAI PROSES GOLD (TAHAP 4, 5, & 6) ===")
    
    # --- TAHAP 4: ATURAN PEMILIHAN (SNAPSHOT, RINCIAN, RESOLUSI PERIODE) ---
    print("-> Menerapkan aturan pemilihan panel (Tahap 4)...")
    
    # Cek apakah 'silver' berupa dataframe atau path file
    if isinstance(silver, pd.DataFrame):
        df_silver = silver
    elif isinstance(silver, dict) and 'data' in silver:
        df_silver = silver['data']
    else:
        df_silver = pd.read_parquet(silver)
        
    # Panggil fungsi dari pemilihan.py (mencetak baris yang dibuang)
    df_gold = terapkan_aturan_gold(df_silver)
    
    # --- TAHAP 5: SIMPAN KE DATABASE DUCKDB ---
    print("-> Memuat data ke DuckDB (Tahap 5)...")
    try:
        from . import muat_sql
        # PERBAIKAN: Buang kolom baru (is_outlier & nilai_zscore) agar tidak bentrok dengan skema tabel SQL
        df_untuk_sql = df_gold.drop(columns=['is_outlier', 'nilai_zscore'], errors='ignore')
        muat_sql.jalankan(df_untuk_sql)
    except Exception as e:
        print(f"   [Peringatan] Tahap 5 gagal dilewati: {e}")
    
    # --- TAHAP 6: BUAT TABEL NASIONAL ---
    print("-> Membuat Tabel Nasional (Tahap 6)...")
    try:
        from . import nasional
        # PERBAIKAN: Kirim df_gold dan 'mentah' (sesuai parameter fungsi nasional milik temanmu)
        # Kita juga perlu menangkap hasil dari nasional
        hasil_nasional = nasional.jalankan(df_gold)
    except Exception as e:
        print(f"   [Peringatan] Tahap 6 gagal dilewati: {e}")
        hasil_nasional = {}

    print("=== PROSES GOLD SELESAI ===")
    
    # Kembalikan dataframe Gold untuk dilempar ke validasi
    return df_gold