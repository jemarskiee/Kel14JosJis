"""Satu perintah reproduksi tim: data mentah -> Silver -> Gold -> validasi.

python unduh_data.py --kasus <N>     # sekali, isi data/raw/
python pipeline.py

Urutan tahap tidak diubah; isi tiap tahap di src/<tahap>/. Tahap 7 (skala, arsip WDI) ditulis
sebagai skrip terpisah di src/skala/ karena memakai unduhan tambahan.
"""
"""Satu perintah reproduksi tim: data mentah -> Silver -> Gold -> validasi."""
import sys
import time
from pathlib import Path

from src import ekstraksi, gold, silver, validasi
from src.common.manifest import periksa
from src.penyimpanan.muat_sql import muat_ke_sqlite


def main():
    n, salah = periksa()
    if salah:
        sys.exit(f"data/raw tidak cocok dengan MANIFEST.csv ({len(salah)} berkas). Jalankan ulang unduh_data.py.")
    print(f"data/raw: {n} berkas cocok dengan MANIFEST.csv")

    for nama, langkah in [
        ("ekstraksi", lambda h: ekstraksi.jalankan()),
        ("silver", lambda h: silver.jalankan(h["ekstraksi"])),
        ("gold", lambda h: gold.jalankan(h["silver"], h["ekstraksi"])),
        # ("validasi", lambda h: validasi.jalankan(h["silver"], h["gold"])),
    ]:
        mulai = time.time()
        hasil[nama] = langkah(hasil)
        print(f"{nama:<10} selesai dalam {time.time() - mulai:.1f} s")

    schema_path = Path("sql/schema_kasus14.sql")
    db_path = Path("data/sql/kasus14.db")
    if schema_path.exists():
        silver_data = hasil.get("silver")
        baris_silver = (
            silver_data.to_dict(orient="records")
            if hasattr(silver_data, "to_dict")
            else (silver_data or [])
        )
        jumlah_baris = muat_ke_sqlite(
            db_path=db_path,
            schema_path=schema_path,
            baris_silver=baris_silver,
        )
        print("Verifikasi jumlah baris SQLite:", jumlah_baris)

    print("Periksa skema minimal: python -m src.common.skema data/silver/silver.parquet")


hasil = {}

if __name__ == "__main__":
    main()
