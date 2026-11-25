import pandas as pd

def terapkan_aturan_gold(df_silver):
    print("[GOLD] Menerapkan aturan pemilihan (snapshot, rincian, tahun)...")
    df = df_silver.copy()
    
    # 1. Filter hanya periode tahunan (4 digit) tanpa membuat kolom baru
    if 'periode' in df.columns:
        df['periode'] = df['periode'].astype(str)
        df = df[df['periode'].str.match(r'^\d{4}$')]
    
    # 2. Filter Rincian (menggunakan kolom bantuan sementara)
    if 'rincian' in df.columns:
        df['rincian_str'] = df['rincian'].astype(str).str.lower()
        df = df[df['rincian_str'].isin(['total', 'tidak ada', 'nan', ''])]

    # 3. Pilih Snapshot Terbaru
    if 'snapshot' in df.columns:
        df = df.sort_values('snapshot', ascending=False)
    
    # Drop duplikat
    kunci_unik = ['seri_kode', 'wilayah_kode', 'periode']
    if 'rincian' in df.columns:
        kunci_unik.append('rincian')
        
    df_gold = df.drop_duplicates(subset=kunci_unik, keep='first')
    
    # 4. Standarisasi Z-Score per Seri
    if 'nilai_num' in df_gold.columns:
        df_gold['nilai_zscore'] = df_gold.groupby('seri_kode')['nilai_num'].transform(
            lambda x: (x - x.mean()) / x.std()
        )

    # 5. Bawa Penanda Outlier (Samakan tipe data periode)
    try:
        df_anomali = pd.read_csv("reports/profil/anomali_berkategori.csv")
        kunci_anomali = ['seri_kode', 'wilayah_kode', 'periode']
        
        df_anomali['periode'] = df_anomali['periode'].astype(str)
        df_anomali['is_outlier'] = True
        
        # Buang duplikat di data anomali agar tidak menggandakan baris Gold
        df_anomali = df_anomali.drop_duplicates(subset=kunci_anomali)
        
        df_gold = df_gold.merge(
            df_anomali[kunci_anomali + ['is_outlier']], 
            on=kunci_anomali, how='left'
        )
        df_gold['is_outlier'] = df_gold['is_outlier'].fillna(False)
    except Exception as e:
        print(f"[GOLD] Peringatan: Gagal membawa penanda outlier ({e})")

    # PERBAIKAN: Hapus kolom bantuan agar tidak error di DuckDB
    df_gold = df_gold.drop(columns=['rincian_str'], errors='ignore')

    print(f"[GOLD] Baris awal Silver: {len(df_silver)} | Baris terpilih ke Gold: {len(df_gold)}")
    print(f"[GOLD] Baris yang dibuang (duplikat/rincian non-total): {len(df_silver) - len(df_gold)}")
    
    return df_gold