"""Tahap 1 — Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ (CSV, JSON WebAPI BPS, XLSX BNPB, SDMX ILO, JSON WDI) menjadi
DataFrame mentah yang setia pada sumbernya: jangan membersihkan di sini, cukup ratakan struktur
dan catat asal tiap baris (`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).
"""



from pathlib import Path

from src.common.manifest import RAW
from .reader_csv import baca_csv
from .reader_json import baca_json


def jalankan():
    folder = Path(RAW) / "bps"
    hasil = {}

    # Membaca seluruh file CSV
    for path in sorted(folder.rglob("*.csv")):
        if path.name == "manifest_asal.json":
            continue

        nama = path.relative_to(RAW).as_posix()
        hasil[nama] = baca_csv(path)

    # Membaca seluruh file JSON data
    for path in sorted(folder.rglob("*.json")):
        if path.name == "manifest_asal.json":
            continue

        nama = path.relative_to(RAW).as_posix()
        hasil[nama] = baca_json(path)

    # Menampilkan jumlah baris setiap file
    for nama, df in hasil.items():
        print(f"{nama}: {len(df)} baris")

    return hasil

