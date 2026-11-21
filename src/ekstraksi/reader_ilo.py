import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

def _tambahkan_asal(df, path, raw):
    path = Path(path)
    raw = Path(raw)

    berkas = path.relative_to(raw).as_posix()
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas, raw)

    return df

def baca_ilo_csv(path, raw=RAW):
    """Membaca data CSV ILOSTAT berformat SDMX."""
    df = pd.read_csv(path)
    return _tambahkan_asal(df, path, raw)

def baca_ilo_json(path, raw=RAW):
    """Membaca DSD dan metadata JSON ILOSTAT."""
    path = Path(path)

    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    bagian = data.get("data", {})
    if "dataStructures" in bagian:
        baris = bagian["dataStructures"]
    elif "dataflows" in bagian:
        baris = bagian["dataflows"]
    else:
        raise ValueError(f"Struktur JSON ILOSTAT tidak dikenali: {path}")

    df = pd.json_normalize(baris, sep=".")
    return _tambahkan_asal(df, path, raw)

def baca_semua_ilo(raw=RAW):
    """Membaca seluruh berkas CSV, DSD, dan metadata ILOSTAT."""
    raw = Path(raw)
    folder = raw / "ilostat"
    hasil = {}

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue

        nama = path.relative_to(raw).as_posix()

        if path.suffix.lower() == ".csv":
            hasil[nama] = baca_ilo_csv(path, raw)
        elif path.suffix.lower() == ".json":
            hasil[nama] = baca_ilo_json(path, raw)

    return hasil
