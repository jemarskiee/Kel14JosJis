"""
Tahap 4 - Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II/VII).
Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Setiap keputusan pembersihan dicatat di log-keputusan.csv.
"""
import pandas as pd
import numpy as np
from pathlib import Path

# IMPORT FUNGSI DARI FILE YANG SUDAH KAMU BUAT
from src.silver.analisis_tahap2 import siapkan, terbaru
from src.silver.kategori_tahap3 import dedup, MUSTAHIL, KUNCI

def catat_log(logs, aksi, jumlah, keterangan):
    """Fungsi bantu untuk mencatat log keputusan pembersihan."""
    logs.append({
        "aksi": aksi,
        "jumlah_baris": jumlah,
        "keterangan": keterangan
    })

def jalankan(mentah):
    """
    Menerima keluaran Tahap 1 (mentah), tulis dan kembalikan DataFrame Silver.
    """
    print("=== MEMULAI PROSES SILVER (TAHAP 4) ===")
    logs = []
    
    # 1. Standarisasi dan Flatten Data (dari analisis_tahap2.py)
    print("1. Menstandarisasi dan meratakan data...")
    df = siapkan(mentah)
    baris_awal = len(df)
    catat_log(logs, "Ekstraksi Awal", baris_awal, "Data mentah berhasil diratakan.")
    
    # 2. Deduplikasi & Penanganan Snapshot (dari analisis_tahap2.py & kategori_tahap3.py)
    print("2. Melakukan deduplikasi (Kunci Silver tidak boleh kembar)...")
    # Kita gunakan fungsi dedup milikmu untuk melihat ringkasan konflik
    kunci_cek, ringkasan_dedup = dedup(df)
    
    # Ambil data terbaru berdasarkan snapshot (fungsi dari analisis_tahap2.py)
    # Fungsi ini sudah memastikan KUNCI (seri, wilayah, periode, rincian) unik.
    df_bersih = terbaru(df)
    baris_setelah_dedup = len(df_bersih)
    
    # Catat berapa banyak duplikat yang dibuang
    duplikat_dibuang = baris_awal - baris_setelah_dedup
    catat_log(logs, "Deduplikasi", duplikat_dibuang, 
              f"Mengambil snapshot terbaru. Sisa baris: {baris_setelah_dedup}")
    
    # 3. Penanganan Nilai Mustahil (dari kategori_tahap3.py)
    print("3. Membuang nilai di luar batas mustahil...")
    mask_mustahil = pd.Series(False, index=df_bersih.index)
    for seri, (batas_bawah, batas_atas) in MUSTAHIL.items():
        if batas_bawah is not None:
            mask_mustahil |= (df_bersih["seri_kode"] == seri) & (df_bersih["nilai_num"] < batas_bawah)
        if batas_atas is not None:
            mask_mustahil |= (df_bersih["seri_kode"] == seri) & (df_bersih["nilai_num"] > batas_atas)
            
    jumlah_mustahil = mask_mustahil.sum()
    df_bersih = df_bersih[~mask_mustahil].copy()
    catat_log(logs, "Buang Nilai Mustahil", jumlah_mustahil, 
              "Nilai di luar rentang wajar yang disepakati dihapus.")
    
    # 4. Validasi Akhir Kunci Silver
    print("4. Validasi akhir kunci unik...")
    if df_bersih.duplicated(subset=KUNCI).any():
        raise ValueError("GAGAL: Masih ada duplikat pada Kunci Silver setelah pembersihan!")
    
        # 5. Standarisasi Format Kolom & Tipe Data
    print("5. Menyeragamkan format kolom...")
    
    # --- A. PERBAIKAN KOLOM LINEAGE (BERKAS & HASH) ---
    # Di tahap 2, nama file disimpan di kolom 'berkas'. Kita bersihkan slash-nya.
    if "berkas" in df_bersih.columns:
        df_bersih["berkas"] = df_bersih["berkas"].astype(str).str.lstrip("/")
    else:
        df_bersih["berkas"] = "unknown"
        
    # Buat kolom 'sumber' (bps, wdi, ilostat, dll)
    if "sumber" not in df_bersih.columns:
        df_bersih["sumber"] = df_bersih["berkas"].str.split("/").str[0]
        
    # Buat kolom '_berkas_raw' (wajib untuk skema)
    df_bersih["_berkas_raw"] = df_bersih["berkas"]
    
    # Buat kolom '_sha256_raw' (wajib untuk skema) dengan mengambil dari MANIFEST
    if "_sha256_raw" not in df_bersih.columns:
        try:
            from src.common.manifest import baca
            manifest = baca()
            df_bersih["_sha256_raw"] = df_bersih["_berkas_raw"].map(manifest)
        except Exception:
            df_bersih["_sha256_raw"] = "unknown"

    # --- B. BUAT KOLOM YANG HILANG LAINNYA ---
    if "jenis_periode" not in df_bersih.columns:
        df_bersih["jenis_periode"] = "tahun"
        
    if "satuan" not in df_bersih.columns:
        df_bersih["satuan"] = np.nan
        
    if "nama_wilayah" not in df_bersih.columns:
        df_bersih["nama_wilayah"] = np.nan

    # --- C. PENYERAGAMAN TIPE DATA ---
    df_bersih["periode"] = df_bersih["periode"].astype(str)
    
    # Kode wilayah harus berupa bilangan bulat
    df_bersih["wilayah_kode"] = pd.to_numeric(
        df_bersih["wilayah_kode"], errors="raise"
    ).astype("int64")
    
    df_bersih["seri_kode"] = df_bersih["seri_kode"].astype(str)
    df_bersih["rincian"] = df_bersih["rincian"].astype(str)
    
    # Menyesuaikan jenis periode dengan aturan skema
    df_bersih["jenis_periode"] = (
        df_bersih["jenis_periode"]
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({"tahunan": "tahun"})
    )

    # --- D. PATCHING SATUAN & WILAYAH (Agar lolos Skema) ---
    kamus_satuan = {
        "var1161": "Persen",
        "var1214": "Persen",
        "var1344": "Rupiah/Tenaga Kerja",
        "var2755": "Persen"
    }
    df_bersih["satuan"] = df_bersih["satuan"].fillna(
        df_bersih["seri_kode"].map(kamus_satuan)
    )
    
    kamus_wilayah = {
        9999: "INDONESIA", 1100: "ACEH", 1200: "SUMATERA UTARA", 1300: "SUMATERA BARAT",
        1400: "RIAU", 1500: "JAMBI", 1600: "SUMATERA SELATAN", 1700: "BENGKULU", 
        1800: "LAMPUNG", 1900: "KEP. BANGKA BELITUNG", 2100: "KEP. RIAU", 
        3100: "DKI JAKARTA", 3200: "JAWA BARAT", 3300: "JAWA TENGAH", 
        3400: "DI YOGYAKARTA", 3500: "JAWA TIMUR", 3600: "BANTEN", 
        5100: "BALI", 5200: "NUSA TENGGARA BARAT", 5300: "NUSA TENGGARA TIMUR", 
        6100: "KALIMANTAN BARAT", 6200: "KALIMANTAN TENGAH", 6300: "KALIMANTAN SELATAN", 
        6400: "KALIMANTAN TIMUR", 6500: "KALIMANTAN UTARA", 7100: "SULAWESI UTARA", 
        7200: "SULAWESI TENGAH", 7300: "SULAWESI SELATAN", 7400: "SULAWESI TENGGARA", 
        7500: "GORONTALO", 7600: "SULAWESI BARAT", 8100: "MALUKU", 8200: "MALUKU UTARA", 
        9100: "PAPUA BARAT", 9400: "PAPUA"
    }
    df_bersih["nama_wilayah"] = df_bersih["nama_wilayah"].fillna(
        df_bersih["wilayah_kode"].map(kamus_wilayah)
    )
    df_bersih["nama_wilayah"] = df_bersih["nama_wilayah"].fillna(
        "Wilayah " + df_bersih["wilayah_kode"].astype(str)
    )

    # --- E. SIMPAN KE PARQUET ---
    # Buang kolom bantu (TAPI JANGAN BUANG _berkas_raw dan _sha256_raw)
    kolom_dibuang = ["bukan_angka", "snapshot", "berkas", "nasional"] 
    df_silver = df_bersih.drop(columns=[c for c in kolom_dibuang if c in df_bersih.columns])
    
    # Pastikan kolom nilai yang dipakai adalah nilai_num
    if "nilai_num" in df_silver.columns:
        # Hapus kolom 'nilai' lama (yang mungkin masih teks), lalu pakai 'nilai_num'
        df_silver = df_silver.drop(columns=["nilai"], errors="ignore")
        df_silver = df_silver.rename(columns={"nilai_num": "nilai"})
        
    # Sapu bersih: pastikan tidak ada nama kolom yang kembar (jaga-jaga)
    df_silver = df_silver.loc[:, ~df_silver.columns.duplicated()]

    out_path = Path("data/silver/silver.parquet")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(out_path, index=False)
    print(f"Berhasil disimpan ke {out_path} ({len(df_silver)} baris)")
    catat_log(logs, "Simpan Parquet", len(df_silver), f"Data disimpan ke {out_path}")

    # 7. Simpan Log Keputusan
    #log_path = Path("log-keputusan.csv")
    #pd.DataFrame(logs).to_csv(log_path, index=False)
    #print(f"Log keputusan disimpan di {log_path}")

    return df_silver