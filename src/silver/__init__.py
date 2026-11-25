"""Tahap 4 - Profil, pembersihan, dan penyeragaman ke Silver."""
import pandas as pd
import numpy as np
from pathlib import Path
from src import konfigurasi as K

from src.silver.analisis_tahap2 import siapkan, terbaru
from src.silver.kategori_tahap3 import dedup, MUSTAHIL, KUNCI

def jalankan(mentah):
    print("=== MEMULAI PROSES SILVER (TAHAP 4) ===")
    
    # 1. Standarisasi
    print("1. Menstandarisasi dan meratakan data...")
    df = siapkan(mentah)
    
    # 2. Deduplikasi
    print("2. Melakukan deduplikasi...")
    kunci_cek, ringkasan_dedup = dedup(df)
    df_bersih = terbaru(df)
    
    # --- PERBAIKAN E1: Buang kode wilayah asing '1' ---
    if "wilayah_kode" in df_bersih.columns:
        df_bersih = df_bersih[df_bersih["wilayah_kode"].astype(str) != '1']
    
    # 3. Buang nilai mustahil
    print("3. Membuang nilai di luar batas mustahil...")
    mask_mustahil = pd.Series(False, index=df_bersih.index)
    for seri, (batas_bawah, batas_atas) in MUSTAHIL.items():
        if batas_bawah is not None:
            mask_mustahil |= (df_bersih["seri_kode"] == seri) & (df_bersih["nilai_num"] < batas_bawah)
        if batas_atas is not None:
            mask_mustahil |= (df_bersih["seri_kode"] == seri) & (df_bersih["nilai_num"] > batas_atas)
    df_bersih = df_bersih[~mask_mustahil].copy()
    
    # 4. Validasi Akhir Kunci
    print("4. Validasi akhir kunci unik...")
    if df_bersih.duplicated(subset=KUNCI).any():
        raise ValueError("GAGAL: Masih ada duplikat pada Kunci Silver!")
    
    # 5. Standarisasi Format Kolom
    print("5. Menyeragamkan format kolom...")
    if "berkas" in df_bersih.columns:
        df_bersih["berkas"] = df_bersih["berkas"].astype(str).str.lstrip("/")
    else:
        df_bersih["berkas"] = "unknown"
        
    if "sumber" not in df_bersih.columns:
        df_bersih["sumber"] = df_bersih["berkas"].str.split("/").str[0]
    df_bersih["_berkas_raw"] = df_bersih["berkas"]
    
    if "_sha256_raw" not in df_bersih.columns:
        try:
            from src.common.manifest import baca
            manifest = baca()
            df_bersih["_sha256_raw"] = df_bersih["_berkas_raw"].map(manifest)
        except Exception:
            df_bersih["_sha256_raw"] = "unknown"

    if "jenis_periode" not in df_bersih.columns:
        df_bersih["jenis_periode"] = "tahun"
    if "satuan" not in df_bersih.columns:
        df_bersih["satuan"] = np.nan
    if "nama_wilayah" not in df_bersih.columns:
        df_bersih["nama_wilayah"] = np.nan

    df_bersih["periode"] = df_bersih["periode"].astype(str)
    df_bersih["wilayah_kode"] = pd.to_numeric(df_bersih["wilayah_kode"], errors="raise").astype("int64")
    df_bersih["seri_kode"] = df_bersih["seri_kode"].astype(str)
    df_bersih["rincian"] = df_bersih["rincian"].astype(str)
    df_bersih["jenis_periode"] = df_bersih["jenis_periode"].astype(str).str.strip().str.lower().replace({"tahunan": "tahun"})

    kamus_satuan = {"var1161": "Persen", "var1214": "Persen", "var1344": "Rupiah/Tenaga Kerja", "var2755": "Persen"}
    df_bersih["satuan"] = df_bersih["satuan"].fillna(df_bersih["seri_kode"].map(kamus_satuan))
    
    kamus_wilayah = {9999: "INDONESIA", 1100: "ACEH", 1200: "SUMATERA UTARA", 1300: "SUMATERA BARAT", 1400: "RIAU", 1500: "JAMBI", 1600: "SUMATERA SELATAN", 1700: "BENGKULU", 1800: "LAMPUNG", 1900: "KEP. BANGKA BELITUNG", 2100: "KEP. RIAU", 3100: "DKI JAKARTA", 3200: "JAWA BARAT", 3300: "JAWA TENGAH", 3400: "DI YOGYAKARTA", 3500: "JAWA TIMUR", 3600: "BANTEN", 5100: "BALI", 5200: "NUSA TENGGARA BARAT", 5300: "NUSA TENGGARA TIMUR", 6100: "KALIMANTAN BARAT", 6200: "KALIMANTAN TENGAH", 6300: "KALIMANTAN SELATAN", 6400: "KALIMANTAN TIMUR", 6500: "KALIMANTAN UTARA", 7100: "SULAWESI UTARA", 7200: "SULAWESI TENGAH", 7300: "SULAWESI SELATAN", 7400: "SULAWESI TENGGARA", 7500: "GORONTALO", 7600: "SULAWESI BARAT", 8100: "MALUKU", 8200: "MALUKU UTARA", 9100: "PAPUA BARAT", 9400: "PAPUA"}
    df_bersih["nama_wilayah"] = df_bersih["nama_wilayah"].fillna(df_bersih["wilayah_kode"].map(kamus_wilayah))
    df_bersih["nama_wilayah"] = df_bersih["nama_wilayah"].fillna("Wilayah " + df_bersih["wilayah_kode"].astype(str))

    kolom_dibuang = ["bukan_angka", "snapshot", "berkas", "nasional"] 
    df_silver = df_bersih.drop(columns=[c for c in kolom_dibuang if c in df_bersih.columns])
    
    if "nilai_num" in df_silver.columns:
        df_silver = df_silver.drop(columns=["nilai"], errors="ignore")
        df_silver = df_silver.rename(columns={"nilai_num": "nilai"})
    df_silver = df_silver.loc[:, ~df_silver.columns.duplicated()]

    # --- PERBAIKAN F1: Tambahkan kolom proyeksi ---
    df_silver["proyeksi"] = False
    for seri, tahun_list in K.PROYEKSI.items():
        mask = (df_silver['seri_kode'] == seri) & (df_silver['periode'].astype(str).isin(tahun_list))
        df_silver.loc[mask, 'proyeksi'] = True

    out_path = Path("data/silver/silver.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(out_path, index=False)
    print(f"Berhasil disimpan ke {out_path} ({len(df_silver)} baris)")

    return df_silver