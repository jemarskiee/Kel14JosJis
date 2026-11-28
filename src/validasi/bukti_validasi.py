import pandas as pd

def jalankan_pembuktian():
    print("Memuat data Silver dan Gold...")
    
    path_silver = 'data/silver/silver.parquet'
    path_gold = 'data/gold/panel.parquet'
    
    try:
        df_silver = pd.read_parquet(path_silver)
        df_gold = pd.read_parquet(path_gold)
    except FileNotFoundError:
        print("Error: File parquet tidak ditemukan.")
        return

    # Ambil HANYA data yang terisi
    df_gold_terisi = df_gold[df_gold['status_sel'] == 'terisi']
    
    print(f"Total baris Silver (mentah) : {len(df_silver):,}")
    print(f"Total baris Gold (terisi)   : {len(df_gold_terisi):,}")
    print("-" * 60)

    # ==========================================
    # 1. BUKTI KUNCI UNIK
    # ==========================================
    print("\n[1] PENGECEKAN KUNCI UNIK (indikator + wilayah_kode + periode)")
    kunci = ['indikator', 'wilayah_kode', 'periode']
    
    # Cek duplikat HANYA pada data terisi
    duplikat_gold = df_gold_terisi.duplicated(subset=kunci).sum()
    
    if duplikat_gold == 0:
        print("    [LULUS] AMAN: Tidak ada data duplikat. Kunci Unik terjaga.")
    else:
        print(f"    [GAGAL] Ditemukan {duplikat_gold} baris duplikat!")

    # ==========================================
    # 2. BUKTI LINEAGE (Tertelusur ke Silver)
    # ==========================================
    print("\n[2] PENGECEKAN LINEAGE (Nilai Gold == Nilai Silver)")
    # Ambil 5 sampel dari Gold yang terisi
    sampel_gold = df_gold_terisi.head(5)
    
    # Join menggunakan kolom 'seri_kode' yang ada di kedua tabel
    bukti = sampel_gold.merge(
        df_silver[['seri_kode', 'wilayah_kode', 'periode', 'rincian', 'nilai']],
        on=['seri_kode', 'wilayah_kode', 'periode', 'rincian'], 
        suffixes=('_Gold', '_Silver')
    )
    
    print("    Menampilkan 5 sampel kecocokan nilai:")
    print(bukti[['indikator', 'wilayah_kode', 'periode', 'nilai_Gold', 'nilai_Silver']].to_string(index=False))
    
    # Cek apakah nilai Gold dan Silver benar-benar sama persis
    cocok = (bukti['nilai_Gold'] == bukti['nilai_Silver']).all()
    if cocok:
        print("    [LULUS] AMAN: Nilai Gold sama persis dengan Silver (Lineage terbukti).")
    else:
        print("    [PERINGATAN] Ada nilai yang tidak cocok, cek tabel di atas.")

    print("\n" + "="*60)
    print("PEMBUKTIAN SELESAI. Silakan screenshot output ini.")

if __name__ == "__main__":
    jalankan_pembuktian()