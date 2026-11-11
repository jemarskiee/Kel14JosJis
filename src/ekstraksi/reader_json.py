
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


URUTAN_DIMENSI = ["vervar", "var", "turvar", "tahun", "turtahun"]


def _lebar_dimensi(data, nama):
    nilai = [str(item["val"]) for item in data.get(nama, [])]
    return max((len(x) for x in nilai), default=0)


def _peta_dimensi(data, nama):
    return {
        str(item["val"]): item.get("label")
        for item in data.get(nama, [])
    }



def _uraikan_key(key, data):
    key = str(key)
    hasil = {}
    posisi = len(key)

    # Baca dimensi dari belakang, kecuali vervar
    for nama in reversed(URUTAN_DIMENSI[1:]):
        lebar = _lebar_dimensi(data, nama)

        kode = key[posisi - lebar:posisi]
        posisi -= lebar

        peta = _peta_dimensi(data, nama)

        hasil[f"{nama}_id"] = kode
        hasil[nama] = peta.get(kode)

    # Sisa karakter merupakan kode wilayah
    kode_wilayah = key[:posisi]
    peta_wilayah = _peta_dimensi(data, "vervar")

    hasil["vervar_id"] = kode_wilayah
    hasil["vervar"] = peta_wilayah.get(kode_wilayah)

    return hasil



def baca_json(path, raw=RAW):
    path = Path(path)
    raw = Path(raw)

    berkas = path.relative_to(raw).as_posix()

    with path.open("r", encoding="utf-8-sig") as file:
        isi = json.load(file)

    baris = []

    for bagian in isi:
        datacontent = bagian.get("datacontent", {})

        for key, nilai in datacontent.items():
            row = _uraikan_key(key, bagian)

            row["datacontent_key"] = key
            row["nilai"] = nilai

            row["status"] = bagian.get("status")
            row["data_availability"] = bagian.get("data-availability")
            row["last_update"] = bagian.get("last_update")
            row["subject"] = bagian.get("subject")

            baris.append(row)

    df = pd.DataFrame(baris)
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas, raw)

    return df
