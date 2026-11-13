import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


INDIKATOR_WDI = {
    "SL.GDP.PCAP.EM.KD",
    "NV.IND.MANF.ZS",
}


def _baca_daftar(path):
    """Membaca daftar data dari struktur JSON WDI."""
    with Path(path).open("r", encoding="utf-8-sig") as file:
        isi = json.load(file)

    if not isinstance(isi, list) or len(isi) < 2:
        raise ValueError(f"Struktur JSON WDI tidak sesuai: {path}")

    if not isinstance(isi[1], list):
        raise ValueError(f"Bagian data JSON WDI bukan daftar: {path}")

    return isi[1]


def _tambahkan_asal(df, path, raw):
    """Menambahkan informasi asal dan SHA-256 berkas."""
    path = Path(path)
    raw = Path(raw)

    berkas = path.relative_to(raw).as_posix()
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas, raw)

    return df


def baca_wdi_data(path, raw=RAW):
    """Membaca observasi WDI berdasarkan ID indikator."""
    baris = _baca_daftar(path)

    terpilih = [
        row for row in baris
        if row.get("indicator", {}).get("id") in INDIKATOR_WDI
    ]

    df = pd.json_normalize(terpilih, sep=".")
    return _tambahkan_asal(df, path, raw)


def baca_wdi_metadata(path, raw=RAW):
    """Membaca metadata sumber dan metadata indikator WDI."""
    path = Path(path)
    baris = _baca_daftar(path)

    if path.stem == "sumber":
        terpilih = baris
    else:
        terpilih = [
            row for row in baris
            if row.get("id") in INDIKATOR_WDI
        ]

    df = pd.json_normalize(terpilih, sep=".")
    return _tambahkan_asal(df, path, raw)


def baca_semua_wdi(raw=RAW):
    """Membaca seluruh berkas data dan metadata WDI."""
    raw = Path(raw)
    folder = raw / "wdi"
    hasil = {}

    for path in sorted(folder.rglob("*.json")):
        bagian = path.relative_to(folder).parts

        if path.name == "manifest_asal.json":
            continue

        nama = path.relative_to(raw).as_posix()

        if "data" in bagian:
            hasil[nama] = baca_wdi_data(path, raw)
        elif "metadata" in bagian:
            hasil[nama] = baca_wdi_metadata(path, raw)

    return hasil
