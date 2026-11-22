"""Tahap 2: profil dan calon anomali var1161, var1344, var1214, var2755.
Tujuan: menemukan, bukan memperbaiki. Skrip hanya membaca hasil ekstraksi
dan menulis tabel serta grafik di reports/. Data tidak diubah."""
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.ekstraksi import jalankan

SERI = ["var1161", "var1344", "var1214", "var2755"]
GAMBAR = Path("reports/gambar")
PROFIL = Path("reports/profil")
GAMBAR.mkdir(parents=True, exist_ok=True)
PROFIL.mkdir(parents=True, exist_ok=True)

# Nama kolom baku (kiri) dan kemungkinan nama di tabel ekstraksi (kanan).
KANDIDAT = {
    "seri_kode": ["seri_kode", "var_id", "kode_seri", "seri"],
    "wilayah_kode": ["wilayah_kode", "wilayah_id", "vervar_id", "kode_wilayah"],
    "nama_wilayah": ["nama_wilayah", "wilayah", "vervar", "provinsi"],
    "periode": ["tahun", "label_tahun", "periode"],
    "rincian": ["rincian", "turvar", "label_turvar"],
    "nilai": ["nilai", "value"],
    "satuan": ["satuan", "unit"],
    "berkas": ["_berkas_raw", "berkas_raw"],
    "ukuran": ["label_var", "var_label"],
}

# Rentang wajar sementara (hanya untuk menandai). var1214 sengaja kosong
# karena memuat dua ukuran; isi setelah rinciannya jelas.
RENTANG = {"var2755": (0, 100), "var1344": (0, None)}


def kumpulkan(obj, jalur=""):
    """Telusuri hasil jalankan() (dict/list/DataFrame) dan keluarkan semua DataFrame."""
    if isinstance(obj, pd.DataFrame):
        yield jalur, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from kumpulkan(v, f"{jalur}/{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from kumpulkan(v, f"{jalur}[{i}]")


def seri_dari_nama(s):
    s = str(s).lower()
    m = re.search(r"var(\d{3,5})", s)
    if m:
        return "var" + m.group(1)
    m = re.search(r"v(\d{4})", s)
    if m:
        return "var" + m.group(1)
    if "sdg8_produktivitas" in s:
        return "var1161"
    return np.nan


def petakan(df):
    peta = {}
    for k, cands in KANDIDAT.items():
        for c in cands:
            if c in df.columns:
                peta[k] = c
                break
    return peta


def siapkan_satu(jalur, df):
    peta = petakan(df)
    if "nilai" not in peta or "periode" not in peta:
        return None
    if "wilayah_kode" not in peta and "nama_wilayah" not in peta:
        return None
    d = pd.DataFrame(index=df.index)
    for k, v in peta.items():
        d[k] = df[v]
    for k in ["nama_wilayah", "rincian", "satuan", "berkas"]:
        if k not in d.columns:
            d[k] = np.nan
    if "wilayah_kode" not in d.columns:
        d["wilayah_kode"] = d["nama_wilayah"]
    # berkas: bila tidak ada kolomnya, pakai jalur dictionary
    d["berkas"] = d["berkas"].fillna(jalur).astype(str)
    # seri: dari kolom bila ada, jika gagal ambil dari nama berkas
    if "seri_kode" in d.columns:
        s = d["seri_kode"].astype(str).str.extract(r"(var\d+)")[0]
    else:
        s = pd.Series(np.nan, index=d.index)
    dari_nama = d["berkas"].map(seri_dari_nama)
    d["seri_kode"] = s.fillna(dari_nama)
    d = d[d["seri_kode"].isin(SERI)].copy()
    if d.empty:
        return None
    return d


def siapkan(hasil):
    tabel, dipakai, dilewati = [], [], []
    for jalur, df in kumpulkan(hasil):
        d = siapkan_satu(jalur, df)
        if d is None:
            dilewati.append((jalur, list(df.columns)[:8]))
        else:
            tabel.append(d)
            dipakai.append((jalur, len(d)))
    if not tabel:
        print("Tipe hasil jalankan():", type(hasil))
        print("Tabel yang ditemukan dan kolomnya:")
        for jalur, kol in dilewati[:15]:
            print(" ", jalur, kol)
        raise SystemExit("Tidak ada tabel dengan var1161/var1344/var1214/var2755. "
                         "Kirim daftar di atas ke saya.")
    print("Tabel yang dipakai:")
    for jalur, n in dipakai:
        print(f"  {jalur}: {n} baris seri target")
    print(f"Tabel dilewati (WDI, ILO, metadata, dll): {len(dilewati)}")

    d = pd.concat(tabel, ignore_index=True)
    d["wilayah_kode"] = d["wilayah_kode"].astype(str).str.replace(r"\.0$", "", regex=True)
    d["nilai_num"] = pd.to_numeric(d["nilai"], errors="coerce")
    d["bukan_angka"] = d["nilai_num"].isna() & d["nilai"].notna()
    d["periode"] = d["periode"].astype(str).str.replace(r"\.0$", "", regex=True)
    d["rincian"] = d["rincian"].fillna("total").astype(str).str.strip()
    d.loc[d["rincian"].str.lower().isin(["tidak ada", "tidak_ada", "-", ""]), "rincian"] = "total"
    d["snapshot"] = d["berkas"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0]
    nama = d["nama_wilayah"].astype(str).str.upper().str.strip()
    d["nasional"] = (d["wilayah_kode"] == "9999") | (nama == "INDONESIA")
    return d


def terbaru(d):
    """Khusus untuk profil: bila kunci sama muncul di dua snapshot atau
    dua format, ambil snapshot terbaru. Ini BUKAN keputusan Silver."""
    kunci = ["seri_kode", "wilayah_kode", "periode", "rincian"]
    a = d.dropna(subset=["nilai_num"]).sort_values("snapshot", kind="stable")
    return a.drop_duplicates(kunci, keep="last").reset_index(drop=True)


def iqr_batas(x, k=1.5):
    q1, q3 = x.quantile(0.25), x.quantile(0.75)
    i = q3 - q1
    return q1 - k * i, q3 + k * i


def baris(s, r, w, nama, t, nilai, metode, alasan):
    return dict(seri_kode=s, rincian=r, wilayah_kode=w, nama_wilayah=nama,
                periode=t, nilai=nilai, metode=metode, alasan=alasan,
                status="calon, ditandai saja, belum diubah")


def cari_anomali(a):
    out = []
    p = a[~a["nasional"]]
    for (s, r), g in p.groupby(["seri_kode", "rincian"]):
        g = g.sort_values(["wilayah_kode", "periode"]).copy()
        # A. IQR lintas provinsi pada periode yang sama
        for t, h in g.groupby("periode"):
            if h["nilai_num"].count() < 8:
                continue
            lo, hi = iqr_batas(h["nilai_num"])
            for _, b in h[(h["nilai_num"] < lo) | (h["nilai_num"] > hi)].iterrows():
                out.append(baris(s, r, b["wilayah_kode"], b["nama_wilayah"], t,
                    b["nilai_num"], "IQR lintas provinsi",
                    f"di luar batas [{lo:.2f}; {hi:.2f}] antarprovinsi pada {t}"))
        # B. z-score pada deret waktu tiap provinsi
        for w, h in g.groupby("wilayah_kode"):
            sd = h["nilai_num"].std()
            if h["nilai_num"].count() < 6 or pd.isna(sd) or sd == 0:
                continue
            z = (h["nilai_num"] - h["nilai_num"].mean()) / sd
            for i in z[z.abs() > 2.5].index:
                b = h.loc[i]
                out.append(baris(s, r, w, b["nama_wilayah"], b["periode"],
                    b["nilai_num"], "z-score deret provinsi",
                    f"z = {z[i]:.2f} terhadap rata-rata deret provinsi itu"))
        # C. lonjakan perubahan antarperiode (IQR dengan faktor 3)
        g["selisih"] = g.groupby("wilayah_kode")["nilai_num"].diff()
        sel = g["selisih"].dropna()
        if len(sel) >= 20:
            lo, hi = iqr_batas(sel, k=3)
            for _, b in g[(g["selisih"] < lo) | (g["selisih"] > hi)].iterrows():
                out.append(baris(s, r, b["wilayah_kode"], b["nama_wilayah"],
                    b["periode"], b["nilai_num"], "lonjakan antarperiode",
                    f"perubahan {b['selisih']:.2f} di luar [{lo:.2f}; {hi:.2f}]"))
        # D. calon patahan seri: perubahan serentak di banyak provinsi
        m = g.groupby("periode")["selisih"].median().dropna()
        if len(m) >= 5:
            med = m.median()
            mad = (m - med).abs().median() * 1.4826
            if mad > 0:
                z = (m - med) / mad
                for t in z[z.abs() > 3.5].index:
                    h = g.loc[g["periode"] == t, "selisih"].dropna()
                    arah = (np.sign(h) == np.sign(m[t])).mean()
                    out.append(baris(s, r, "SEMUA", "serentak", t, m[t],
                        "calon patahan seri",
                        f"median perubahan {m[t]:.2f} menyimpang (robust z {z[t]:.1f}); "
                        f"{arah:.0%} provinsi searah"))
        # E. di luar rentang wajar
        if s in RENTANG:
            lo, hi = RENTANG[s]
            mask = g["nilai_num"] < lo
            if hi is not None:
                mask |= g["nilai_num"] > hi
            for _, b in g[mask].iterrows():
                out.append(baris(s, r, b["wilayah_kode"], b["nama_wilayah"],
                    b["periode"], b["nilai_num"], "di luar rentang wajar",
                    f"nilai di luar rentang {lo} sampai {hi}"))
    an = pd.DataFrame(out)
    if len(an):
        an["wilayah_kode"] = an["wilayah_kode"].astype(str)
    return an


def aman(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", str(s)).strip("-")


def buat_gambar(a, an):
    for (s, r), g in a.groupby(["seri_kode", "rincian"]):
        p, n = g[~g["nasional"]], g[g["nasional"]]
        if p.empty:
            continue
        satuan = "|".join(sorted(map(str, g["satuan"].dropna().unique())))
        nama = f"{s}_{aman(r)}"
        judul = f"{s} - {r} (satuan katalog: {satuan})"
        per = sorted(p["periode"].unique())
        # 1. boxplot per periode
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.boxplot([p.loc[p["periode"] == t, "nilai_num"] for t in per])
        ax.set_xticks(range(1, len(per) + 1))
        ax.set_xticklabels(per, rotation=60, fontsize=8)
        ax.set_title("Boxplot antarprovinsi per periode: " + judul, fontsize=9)
        fig.tight_layout(); fig.savefig(GAMBAR / f"{nama}_boxplot_periode.png", dpi=130)
        plt.close(fig)
        # 2. boxplot per provinsi
        nm = p.groupby("wilayah_kode")["nama_wilayah"].first()
        med = p.groupby("wilayah_kode")["nilai_num"].median().sort_values()
        fig, ax = plt.subplots(figsize=(8, 10))
        ax.boxplot([p.loc[p["wilayah_kode"] == k, "nilai_num"] for k in med.index],
                   vert=False)
        ax.set_yticks(range(1, len(med) + 1))
        ax.set_yticklabels([str(nm[k]) for k in med.index], fontsize=7)
        ax.set_title("Boxplot per provinsi: " + judul, fontsize=9)
        fig.tight_layout(); fig.savefig(GAMBAR / f"{nama}_boxplot_provinsi.png", dpi=130)
        plt.close(fig)
        # 3. deret waktu
        w = p.pivot_table(index="periode", columns="wilayah_kode", values="nilai_num")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(w.index, w.values, color="lightgray", lw=0.8)
        ax.plot(w.index, w.median(axis=1), color="tab:blue", lw=2, label="median provinsi")
        if len(n):
            nn = n.groupby("periode")["nilai_num"].first()
            ax.plot(nn.index, nn.values, color="tab:red", lw=2, label="Indonesia")
        if len(an):
            x = an[(an["seri_kode"] == s) & (an["rincian"] == r) & (an["wilayah_kode"] != "SEMUA")]
            x = x[x["periode"].isin(w.index)]
            if len(x):
                ax.scatter(x["periode"], x["nilai"], color="black", s=14, zorder=5,
                           label="calon anomali")
        ax.tick_params(axis="x", rotation=60, labelsize=8)
        ax.legend(fontsize=8)
        ax.set_title("Deret waktu: " + judul, fontsize=9)
        fig.tight_layout(); fig.savefig(GAMBAR / f"{nama}_deret_waktu.png", dpi=130)
        plt.close(fig)


def main():
    d = siapkan(jalankan())
    a = terbaru(d)
    print("baris mentah seri ini:", len(d), "| baris analisis:", len(a))
    print("nilai bukan angka:", int(d["bukan_angka"].sum()))
    print("kode wilayah unik per seri:")
    print(a.groupby("seri_kode")["wilayah_kode"].nunique())
    p = a[~a["nasional"]]

    g = p.groupby(["seri_kode", "rincian"])
    t1 = g["nilai_num"].agg(n="count", min="min", q1=lambda x: x.quantile(0.25),
            median="median", mean="mean", q3=lambda x: x.quantile(0.75),
            max="max", std="std")
    t2 = g.agg(periode_awal=("periode", "min"), periode_akhir=("periode", "max"),
            n_periode=("periode", "nunique"), n_provinsi=("wilayah_kode", "nunique"),
            satuan=("satuan", lambda x: "|".join(sorted(map(str, x.dropna().unique())))))
    t1.join(t2).reset_index().round(3).to_csv(PROFIL / "profil_per_seri.csv", index=False)

    pv = p.groupby(["seri_kode", "rincian", "wilayah_kode"]).agg(
        nama_wilayah=("nama_wilayah", "first"), n=("nilai_num", "count"),
        min=("nilai_num", "min"), median=("nilai_num", "median"),
        mean=("nilai_num", "mean"), std=("nilai_num", "std"),
        max=("nilai_num", "max"), periode_awal=("periode", "min"),
        periode_akhir=("periode", "max")).reset_index()
    pv.round(3).to_csv(PROFIL / "profil_per_provinsi.csv", index=False)

    pp = (p.groupby(["seri_kode", "rincian", "periode"])["wilayah_kode"]
            .nunique().rename("n_provinsi").reset_index())
    pp.to_csv(PROFIL / "provinsi_per_periode.csv", index=False)

    nas = a[a["nasional"]].groupby(["seri_kode", "rincian", "periode"])["nilai_num"].first().rename("nasional")
    pr = p.groupby(["seri_kode", "rincian", "periode"])["nilai_num"].agg(
        median_prov="median", min_prov="min", max_prov="max")
    bd = pr.join(nas).reset_index()
    bd["nasional_di_luar_rentang_provinsi"] = (bd["nasional"] < bd["min_prov"]) | (bd["nasional"] > bd["max_prov"])
    bd.round(3).to_csv(PROFIL / "nasional_vs_provinsi.csv", index=False)

    an = cari_anomali(a)
    an.round(3).to_csv(PROFIL / "calon_anomali.csv", index=False)
    buat_gambar(a, an)

    if len(an):
        print(an.groupby(["seri_kode", "metode"]).size())
    print("selesai. Lihat reports/profil/ dan reports/gambar/")


if __name__ == "__main__":
    main()
