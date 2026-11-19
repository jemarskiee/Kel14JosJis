
from pathlib import Path
from io import StringIO

import pandas as pd

from src.common.manifest import RAW, sha256_raw


def baca_csv(path, raw=RAW):
    path = Path(path)
    raw = Path(raw)

    berkas = path.relative_to(raw).as_posix()

    # Membaca file dengan beberapa kemungkinan encoding
    isi = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            isi = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if isi is None:
        raise ValueError(f"Gagal membaca encoding file: {path}")

    # Mendeteksi pemisah kolom
    baris_awal = isi.splitlines()[0]
    pemisah = ";" if baris_awal.count(";") > baris_awal.count(",") else ","
    desimal = "," if pemisah == ";" else "."

    df = pd.read_csv(
        StringIO(isi),
        sep=pemisah,
        decimal=desimal
    )

    # Menambahkan informasi asal data
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas, raw)

    return df
