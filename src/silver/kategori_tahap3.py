"""Tahap 3: kategori calon anomali, patahan serentak, deduplikasi, proyeksi ILO.
Hanya membaca. Tidak mengubah data mentah, ekstraksi, atau Silver."""
from pathlib import Path
import numpy as np
import pandas as pd

from src.ekstraksi import jalankan
from src.silver.analisis_tahap2 import siapkan
from src.silver.pembanding_tahap2 import baca_ilo, TAHUN_BERJALAN

PROFIL = Path("reports/profil")
PROFIL.mkdir(parents=True, exist_ok=True)
EPS = 1e-9
KUNCI = ["seri_kode", "wilayah_kode", "periode", "rincian"]

# Dari var.note BPS di metadata JSON mentah.
SEMENTARA = {
    "var1161": {"2024": "angka sementara", "2025": "angka sangat sementara"},
    "var1344": {"2022": "angka sementara", "2023": "angka sangat sementara"},
    "var1214": {"2022": "angka sementara", "2023": "angka sangat sementara"},
}
# Rentang mustahil (bukan rentang wajar): di luar ini dianggap bukti galat.
MUSTAHIL = {"var1161": (-100, 100), "var1214": (0, 100),
            "var2755": (0, 100), "var1344": (0, None)}
PROV_BARU = {"6500", "9200", "9500", "9600", "9700"}


def dedup(d):
    x = d.dropna(subset=["nilai_num"]).copy()
    x["format"] = np.where(x["berkas"].str.contains(".json", regex=False), "json", "csv")
    ps = (x.groupby(KUNCI + ["snapshot"])["nilai_num"].agg(["min", "max"]).reset_index())
    ps["beda_format"] = (ps["max"] - ps["min"]) > EPS
    k = (ps.groupby(KUNCI).agg(n_snapshot=("snapshot", "nunique"),
                               konflik_format=("beda_format", "max"),
                               lo=("min", "min"), hi=("max", "max")).reset_index())
    k["revisi"] = ((k["hi"] - k["lo"]) > EPS) & (k["n_snapshot"] > 1) & ~k["konflik_format"]
    n = x.groupby(KUNCI).size().rename("n_salinan").reset_index()
    k = k.merge(n, on=KUNCI)
    k["status"] = np.select(
        [k["konflik_format"], k["revisi"], k["n_salinan"] > 1],
        ["konflik_dalam_snapshot", "revisi_antar_snapshot", "sama_bukan_duplikat_salah"],
        default="tunggal")
    ring = k.groupby(["seri_kode", "status"]).size().rename("n_kunci").reset_index()
    return k, ring


def patahan(prov):
    out = []
    for (s, r), g in prov.groupby(["seri_kode", "rincian"]):
        g = g.sort_values(["wilayah_kode", "periode"]).copy()
        g["selisih"] = g.groupby("wilayah_kode")["nilai_num"].diff()
        m = g.groupby("periode")["selisih"].median().dropna()
        if len(m) < 4:
            continue
        med = m.median()
        mad = (m - med).abs().median() * 1.4826
        for t, v in m.items():
            h = g.loc[g["periode"] == t, "selisih"].dropna()
            if len(h) < 8:
                continue
            arah = float((np.sign(h) == np.sign(v)).mean()) if v != 0 else 0.0
            z = (v - med) / mad if mad > 0 else np.nan
            out.append(dict(seri_kode=s, periode=str(t), median_perubahan=round(v, 3),
                            robust_z=round(z, 2) if pd.notna(z) else np.nan,
                            persen_searah=round(100 * arah, 1), n_provinsi=len(h)))
    p = pd.DataFrame(out)
    if p.empty:
        p["calon_patahan"] = []
        return p
    p["calon_patahan"] = (p["persen_searah"] >= 70) & (p["robust_z"].abs() > 3)
    return p


def kategori(an, p, konflik, awal):
    pat = set(zip(p.loc[p["calon_patahan"], "seri_kode"], p.loc[p["calon_patahan"], "periode"]))
    kon = set(zip(konflik["seri_kode"], konflik["wilayah_kode"], konflik["periode"]))
    n_tanda = an.groupby(["seri_kode", "wilayah_kode"])["periode"].nunique()
    rows = []
    for _, b in an.iterrows():
        s, t, w, v = b["seri_kode"], str(b["periode"]), str(b["wilayah_kode"]), b["nilai"]
        galat = []
        if (s, w, t) in kon:
            galat.append("nilai CSV dan JSON berbeda pada snapshot yang sama")
        lo, hi = MUSTAHIL.get(s, (None, None))
        if lo is not None and v < lo:
            galat.append(f"nilai di bawah batas mustahil {lo}")
        if hi is not None and v > hi:
            galat.append(f"nilai di atas batas mustahil {hi}")
        if galat:
            kat, tindakan, bukti = "galat_input", "perlu_perbaikan_lewat_kode_dan_log", galat
        elif (s, t) in pat:
            kat, tindakan = "patahan_seri", "ditandai_tidak_diubah"
            bukti = ["perubahan serentak searah di hampir semua provinsi pada periode ini"]
        else:
            kat, tindakan = "outlier_asli", "ditandai_tidak_diubah"
            bukti = ["tidak ada bukti galat dan tidak serentak antarprovinsi"]
        n = int(n_tanda.get((s, w), 0))
        if n >= 3:
            bukti.append(f"provinsi ini ditandai pada {n} periode (pola struktural)")
        if t in SEMENTARA.get(s, {}):
            bukti.append(f"{SEMENTARA[s][t]} menurut catatan BPS, kemungkinan direvisi")
        if w in PROV_BARU and awal.get((s, w)) == t:
            bukti.append("tahun pertama data provinsi baru di seri ini")
        rows.append(dict(b, kategori=kat, bukti="; ".join(bukti), tindakan=tindakan))
    return pd.DataFrame(rows)


def main():
    hasil = jalankan()
    d = siapkan(hasil)
    d["periode"] = d["periode"].astype(str)

    k, ring = dedup(d)
    k.drop(columns=["lo", "hi"]).to_csv(PROFIL / "dedup_kunci.csv", index=False)
    ring.to_csv(PROFIL / "dedup_ringkasan.csv", index=False)
    konflik = k[k["status"] == "konflik_dalam_snapshot"]
    print("\n=== DEDUPLIKASI (jumlah kunci per status) ===")
    print(ring.to_string())
    print("konflik dalam snapshot yang sama (calon galat):", len(konflik))
    print("revisi antar snapshot:", int((k["status"] == "revisi_antar_snapshot").sum()))

    prov = d[(~d["nasional"]) & d["nilai_num"].notna()].copy()
    prov = prov.sort_values("snapshot", kind="stable").drop_duplicates(KUNCI, keep="last")
    awal = prov.groupby(["seri_kode", "wilayah_kode"])["periode"].min().to_dict()

    p = patahan(prov)
    p.to_csv(PROFIL / "patahan_serentak.csv", index=False)
    lolos = p[p["calon_patahan"]] if len(p) else p
    print("\n=== TAHUN YANG LOLOS ATURAN PATAHAN ===")
    print(lolos.to_string() if len(lolos) else "tidak ada")
    print("\n=== 5 PERIODE PALING SERENTAK PER SERI (robust z mutlak terbesar) ===")
    for s, g in p.groupby("seri_kode"):
        print(s)
        print(g.reindex(g["robust_z"].abs().sort_values(ascending=False).index).head(5).to_string())

    an = pd.read_csv(PROFIL / "calon_anomali.csv", dtype={"wilayah_kode": str, "periode": str})
    an = an[an["metode"] != "calon patahan seri"]
    kat = kategori(an, p, konflik, awal)
    kat.to_csv(PROFIL / "anomali_berkategori.csv", index=False)
    print("\n=== KATEGORI ANOMALI ===")
    print(kat.groupby(["seri_kode", "kategori"]).size().to_string())
    print("total:", len(kat))
    print(kat["kategori"].value_counts().to_string())

    rows, _ = baca_ilo(hasil)
    pr = [dict(seri_kode=r["seri_kode"], tahun=th, status="proyeksi",
               tindakan="dikeluarkan_dari_rekonsiliasi")
          for r in rows for th in sorted(r["_tahun"]) if th > TAHUN_BERJALAN]
    pd.DataFrame(pr, columns=["seri_kode", "tahun", "status", "tindakan"]).to_csv(
        PROFIL / "proyeksi_ilo.csv", index=False)
    print("\n=== PROYEKSI ILO (setelah tahun", TAHUN_BERJALAN, ") ===")
    print(pd.DataFrame(pr).to_string() if pr else "tidak ada")
    print("\nselesai. Lihat reports/profil/")


if __name__ == "__main__":
    main()
