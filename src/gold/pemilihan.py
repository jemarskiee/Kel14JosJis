import pandas as pd

def terapkan_aturan_gold(df_silver):
    print("[GOLD] Menerapkan aturan pemilihan (snapshot, rincian, resolusi periode)...")
    df_awal = df_silver.copy()
    df = df_silver.copy()
    
    # --- ATURAN 1: RESOLUSI PERIODE ---
    # Kita memilih mempertahankan resolusi tahunan (4 digit). 
    # Jika ada semester/bulanan, kita tandai sebagai "dibuang".
    if 'periode' in df.columns:
        df['periode'] = df['periode'].astype(str)
        df_tahunan = df[df['periode'].str.match(r'^\d{4}$')]
        baris_buang_periode = len(df) - len(df_tahunan)
        df = df_tahunan
    
    # --- ATURAN 2: RINCIAN ---
    if 'rincian' in df.columns:
        df['rincian_str'] = df['rincian'].astype(str).str.lower()
        df_total = df[df['rincian_str'].isin(['total', 'tidak ada', 'nan', ''])]
        baris_buang_rincian = len(df) - len(df_total)
        df = df_total

    # --- ATURAN 3: DUPLIKASI SNAPSHOT ---
    if 'snapshot' in df.columns:
        df = df.sort_values('snapshot', ascending=False)
    
    kunci_unik = ['seri_kode', 'wilayah_kode', 'periode']
    if 'rincian' in df.columns:
        kunci_unik.append('rincian')
        
    df_gold = df.drop_duplicates(subset=kunci_unik, keep='first')
    baris_buang_snapshot = len(df) - len(df_gold)

    # --- STANDARISASI & OUTLIER ---
    if 'nilai_num' in df_gold.columns:
        df_gold['nilai_zscore'] = df_gold.groupby('seri_kode')['nilai_num'].transform(
            lambda x: (x - x.mean()) / x.std()
        )

    try:
        df_anomali = pd.read_csv("reports/profil/anomali_berkategori.csv")
        kunci_anomali = ['seri_kode', 'wilayah_kode', 'periode']
        df_anomali['periode'] = df_anomali['periode'].astype(str)
        df_anomali['is_outlier'] = True
        df_anomali = df_anomali.drop_duplicates(subset=kunci_anomali)
        
        df_gold = df_gold.merge(df_anomali[kunci_anomali + ['is_outlier']], on=kunci_anomali, how='left')
        df_gold['is_outlier'] = df_gold['is_outlier'].fillna(False)
    except Exception as e:
        print(f"[GOLD] Peringatan: Gagal membawa penanda outlier ({e})")

    df_gold = df_gold.drop(columns=['rincian_str'], errors='ignore')

    # --- LAPORAN BARIS TERBUANG ---
    print(f"[GOLD] Baris awal Silver: {len(df_awal)}")
    print(f"[GOLD] Dibuang karena resolusi bukan tahunan: {baris_buang_periode}")
    print(f"[GOLD] Dibuang karena rincian bukan 'total': {baris_buang_rincian}")
    print(f"[GOLD] Dibuang karena duplikasi snapshot: {baris_buang_snapshot}")
    print(f"[GOLD] Baris akhir terpilih ke Gold: {len(df_gold)}")
    
    return df_gold