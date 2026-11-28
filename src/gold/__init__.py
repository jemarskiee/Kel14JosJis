
"""Tahap 6 — Tabel nasional Gold: seri utama dan pembanding per periode."""

from pathlib import Path
import re

import pandas as pd


PASANGAN = {
    "SDG_0821_NOC_RT": "var1161",
    "SDG_B821_NOC_RT": "var1161",
    "SL.GDP.PCAP.EM.KD": "var1161",
    "NV.IND.MANF.ZS": "var1214",
    "SDG_0922_NOC_RT": "var2755",
}

SERI_UTAMA = ["var1161", "var1344", "var1214", "var2755"]


def _baris(periode, seri, nilai, sumber, satuan, berkas, sha256,
           jenis_seri, seri_utama, metode_asal):
    return {
        "periode": str(periode),
        "seri_kode": seri,
        "jenis_seri": jenis_seri,
        "seri_utama": seri_utama,
        "wilayah": "Indonesia",
        "nilai": pd.to_numeric(nilai, errors="coerce"),
        "sumber": sumber,
        "satuan": satuan,
        "_berkas_raw": berkas,
        "_sha256_raw": sha256,
        "metode_asal": metode_asal,
    }


def jalankan(silver, mentah):
    """Membuat tabel nasional Gold dari Silver dan hasil ekstraksi."""

    hasil = []

    # 1. Mengambil seri utama BPS tingkat nasional.
    bps = silver[
        (silver["wilayah_kode"] == 9999)
        & (silver["seri_kode"].isin(SERI_UTAMA))
    ].copy()

    for _, r in bps.iterrows():
        hasil.append(_baris(
            r["periode"], r["seri_kode"], r["nilai"],
            "BPS", r["satuan"], r["_berkas_raw"],
            r.get("_sha256_raw", None), "utama", r["seri_kode"],
            "BPS: wilayah_kode=9999"
        ))

    # 2. Mengambil seri pembanding ILOSTAT.
    for nama, df in mentah.items():
        nama = str(nama)
        cocok = re.search(
            r"DF_(SDG_[A-Z0-9]+_NOC_RT)",
            nama.upper()
        )

        if cocok:
            seri = cocok.group(1)
            if seri not in PASANGAN:
                continue

            indonesia = df[
                df["REF_AREA"].astype(str).str.upper() == "IDN"
            ]

            for _, r in indonesia.iterrows():
                hasil.append(_baris(
                    r["TIME_PERIOD"], seri, r["OBS_VALUE"],
                    "ILOSTAT",
                    r.get("UNIT_MEASURE", None),
                    r["_berkas_raw"],
                    r.get("_sha256_raw", None),
                    "pembanding", PASANGAN[seri],
                    "ILOSTAT: REF_AREA=IDN"
                ))

    # 3. Mengambil seri pembanding World Development Indicators.
    for nama, df in mentah.items():
        if "indicator.id" not in df.columns:
            continue

        for seri, seri_utama in PASANGAN.items():
            if seri not in ["SL.GDP.PCAP.EM.KD", "NV.IND.MANF.ZS"]:
                continue

            indonesia = df[
                (df["countryiso3code"].astype(str).str.upper() == "IDN")
                & (df["indicator.id"].astype(str) == seri)
                & (df["value"].notna())
            ]

            for _, r in indonesia.iterrows():
                hasil.append(_baris(
                    r["date"], seri, r["value"],
                    "WDI", r.get("unit", None),
                    r["_berkas_raw"],
                    r.get("_sha256_raw", None),
                    "pembanding", seri_utama,
                    "WDI: countryiso3code=IDN"
                ))

    # 4. Menyusun dan memeriksa tabel.
    if not hasil:
        raise ValueError("Tidak ada data nasional yang berhasil dikumpulkan.")

    gold = pd.DataFrame(hasil)
    gold["periode"] = gold["periode"].astype(str).str.extract(r"(\d{4})")[0]

    if gold["periode"].isna().any():
        raise ValueError("Ada periode yang tidak dapat dibaca sebagai tahun.")

    gold["periode"] = gold["periode"].astype(int)

    if gold.duplicated(["periode", "seri_kode"]).any():
        duplikat = gold.loc[
            gold.duplicated(["periode", "seri_kode"], keep=False),
            ["periode", "seri_kode", "_berkas_raw"]
        ]
        raise ValueError(
            "Ada data ganda untuk kombinasi periode dan seri:\n"
            + duplikat.to_string(index=False)
        )

    if gold[["_berkas_raw", "nilai"]].isna().any().any():
        raise ValueError("Asal berkas atau nilai Gold ditemukan kosong.")

    gold = gold.sort_values(
        ["periode", "jenis_seri", "seri_kode"]
    ).reset_index(drop=True)

    # 5. Menyimpan keluaran Gold.
    folder = Path("data/gold")
    folder.mkdir(parents=True, exist_ok=True)

    jalur = folder / "tabel_nasional_gold.parquet"
    gold.to_parquet(jalur, index=False)
    jalur_csv = folder / "tabel_nasional_gold.csv"
    gold.to_csv(jalur_csv, index=False, encoding="utf-8-sig")

    print(f"Tabel nasional Gold disimpan: {jalur}")
    print(f"CSV nasional Gold disimpan: {jalur_csv}")
    print(f"Jumlah baris: {len(gold)}")
    print(f"Jumlah seri: {gold['seri_kode'].nunique()}")
    print(f"Jumlah berkas sumber: {gold['_berkas_raw'].nunique()}")

    return {"tabel_nasional": gold}
