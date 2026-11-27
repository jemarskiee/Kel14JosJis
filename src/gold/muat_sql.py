from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path.cwd()
def catat(**kwargs): 
    print(f"Log Pemuatan: {kwargs}")

DB = ROOT / "data" / "gold" / "gudang.duckdb"
DDL = Path(__file__).with_name("silver.sql")

def jalankan(silver):
    silver = silver.drop(columns=['proyeksi'], errors='ignore') 
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)
    
    seri = pd.read_csv(ROOT / "docs" / "seri.csv")[["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "sdg_kode"]]
    seri["sdg_kode"] = seri["sdg_kode"].astype(str)
    
    s = silver.copy()
    
    # Paksa wilayah_kode jadi integer agar cocok dengan skema SQL
    s["wilayah_kode"] = pd.to_numeric(s["wilayah_kode"], errors='coerce').fillna(0).astype(int)
    
    # --- TAMBAHAN BARU: Isi nama_wilayah yang kosong agar tidak melanggar NOT NULL ---
    if "nama_wilayah" in s.columns:
        s["nama_wilayah"] = s["nama_wilayah"].fillna("Tidak Diketahui")
    # --------------------------------------------------------------------------------

    # Cek apakah kolom rujukan_tahun ada
    if "rujukan_tahun" in s.columns:
        s["rujukan_tahun"] = s["rujukan_tahun"].astype("float64")
    else:
        s["rujukan_tahun"] = None
    
    with duckdb.connect(str(DB)) as con:
        con.execute(DDL.read_text(encoding="utf-8"))
        
        con.register("seri_df", seri)
        con.execute("INSERT INTO seri SELECT * FROM seri_df")
        
        con.register("silver_df", s)
        
        # Ambil daftar kolom yang benar-benar ada di tabel DuckDB
        cols_db = [c[0] for c in con.execute("DESCRIBE silver").fetchall()]
        
        # Filter: hanya masukkan kolom yang ada di dataframe DAN ada di tabel DuckDB
        kolom_valid = [c for c in s.columns if c in cols_db]
        
        if not kolom_valid:
            raise ValueError("Error: Tidak ada kolom yang cocok antara dataframe dan tabel DuckDB!")
            
        kolom_str = ", ".join(kolom_valid)
        con.execute(f"INSERT INTO silver ({kolom_str}) SELECT {kolom_str} FROM silver_df")
        
        n = con.execute("SELECT count(*) FROM silver").fetchone()[0]
        
    if n != len(silver):
        raise AssertionError(f"DuckDB memuat {n} baris, Silver {len(silver)} baris")
        
    catat(baris_sql=n)
    return n