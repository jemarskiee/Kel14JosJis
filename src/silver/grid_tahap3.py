"""Tahap 3: grid lengkap provinsi x periode, kelengkapan panel, pemisahan
baris Indonesia, dan pemeriksaan laju provinsi vs nasional (var1161).
Hanya membaca hasil ekstraksi. Tidak mengubah data mentah, ekstraksi, atau Silver."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.ekstraksi import jalankan
from src.silver.analisis_tahap2 import siapkan, terbaru, SERI

PROFIL = Path("reports/profil")
GAMBAR = Path("reports/gambar")
PROFIL.mkdir(parents=True, exist_ok=True)
GAMBAR.mkdir(parents=True, exist_ok=True)

# Provinsi baru: tahun pertama berdiri. Sebelum tahun itu sel bukan missing.
# Tahun ini asumsi awal; cocokkan dengan data (kolom sebab di sel_kosong_detail.csv).
BERDIRI = {
    "KALIMANTAN UTARA": 2012,
    "PAPUA SELATAN": 2022,
    "PAPUA TENGAH": 2022,
    "PAPUA PEGUNUNGAN": 2022,
    "PAPUA BARAT DAYA": 2022,
}

# REVISI: Tambahan untuk klasifikasi sel belum terbit (data belum dirilis BPS)
BUKTI_1161 = ("var.note BPS: laju provinsi baru (DOB) baru tersedia 2025; "
              "2024 dihitung pada provinsi induk")
BELUM_TERBIT = {("var1161", n, t): BUKTI_1161
                for n in ("PAPUA BARAT DAYA", "PAPUA SELATAN", "PAPUA TENGAH", "PAPUA PEGUNUNGAN")
                for t in (2022, 2023, 2024)}


def sebab_kosong(t, f, l):
    if f is None:
        return "provinsi_tidak_ada_di_seri"
    if t < f:
        return "sebelum_data_pertama"
    if t > l:
        return "setelah_data_terakhir"
    return "celah_tengah"


def peta_sel(g, s):
    w = g.pivot(index="nama", columns="tahun", values="kode_status").sort_index()
    fig, ax = plt.subplots(figsize=(9, 10))
    # REVISI: vmax diubah jadi 3 karena ada status baru (belum_terbit = 3)
    ax.imshow(w.values, aspect="auto", cmap="RdYlGn", vmin=0, vmax=3)
    ax.set_xticks(range(len(w.columns)))
    ax.set_xticklabels(w.columns, rotation=60, fontsize=7)
    ax.set_yticks(range(len(w.index)))
    ax.set_yticklabels(w.index, fontsize=6)
    # REVISI: Judul keterangan warna disesuaikan
    ax.set_title(f"{s}: hijau terisi, oranye belum terbit, kuning belum berdiri, merah kosong", fontsize=9)
    fig.tight_layout()
    fig.savefig(GAMBAR / f"grid_{s}.png", dpi=130)
    plt.close(fig)


def main():
    d = siapkan(jalankan())
    a = terbaru(d)
    a["tahun"] = pd.to_numeric(a["periode"], errors="coerce")
    print("\nperiode bukan tahun:", int(a["tahun"].isna().sum()))
    a = a.dropna(subset=["tahun"]).copy()
    a["tahun"] = a["tahun"].astype(int)

    # 1. pisahkan baris Indonesia dari baris provinsi
    nas = a[a["nasional"]].copy()
    prov = a[~a["nasional"]].copy()
    nas[["seri_kode", "wilayah_kode", "nama_wilayah", "tahun", "nilai_num"]].sort_values(
        ["seri_kode", "tahun"]).to_csv(PROFIL / "baris_nasional.csv", index=False)
    print("baris nasional:", len(nas), "| baris provinsi:", len(prov))

    # 2. susunan 38 provinsi: kode di var2755, nama diperiksa manual
    ref = prov[prov["seri_kode"] == "var2755"]
    nama = ref.groupby("wilayah_kode")["nama_wilayah"].agg(lambda x: x.value_counts().index[0])
    print("\nJumlah kode provinsi di var2755:", len(nama))
    print(nama.to_string())
    if len(nama) != 38:
        raise SystemExit("Kode di var2755 bukan 38. Kirim daftar di atas ke saya.")
    prov38 = sorted(nama.index)

    ganda = prov.groupby("wilayah_kode")["nama_wilayah"].nunique()
    print("\nkode dengan lebih dari satu nama:", ganda[ganda > 1].index.tolist())

    luar = prov[~prov["wilayah_kode"].isin(prov38)]
    lt = (luar.groupby(["seri_kode", "wilayah_kode", "nama_wilayah"], dropna=False)
          .agg(n=("nilai_num", "count"), tahun_awal=("tahun", "min"),
               tahun_akhir=("tahun", "max")).reset_index())
    lt.to_csv(PROFIL / "kode_wilayah_di_luar_38.csv", index=False)
    print("\nkode di luar 38 provinsi:")
    print(lt.to_string() if len(lt) else "tidak ada")

    # 3. grid lengkap
    baris = []
    for s in SERI:
        p = prov[(prov["seri_kode"] == s) & (prov["wilayah_kode"].isin(prov38))]
        if p.empty:
            continue
        tahun = range(int(p["tahun"].min()), int(p["tahun"].max()) + 1)
        nilai = p.set_index(["wilayah_kode", "tahun"])["nilai_num"]
        awal = p.groupby("wilayah_kode")["tahun"].min()
        akhir = p.groupby("wilayah_kode")["tahun"].max()
        for w in prov38:
            lahir = BERDIRI.get(str(nama[w]).upper().strip())
            f = int(awal[w]) if w in awal.index else None
            l = int(akhir[w]) if w in akhir.index else None
            for t in tahun:
                v = nilai.get((w, t), np.nan)
                if pd.notna(v):
                    st, sb, ks = "terisi", "", 3
                elif lahir and t < lahir:
                    st, sb, ks = "belum_berdiri", "", 1
                elif (s, str(nama[w]).upper().strip(), t) in BELUM_TERBIT:
                    # REVISI: Tambahan kondisi untuk menangkap status belum terbit
                    st, ks = "belum_terbit", 2
                    sb = BELUM_TERBIT[(s, str(nama[w]).upper().strip(), t)]
                else:
                    st, sb, ks = "kosong", sebab_kosong(t, f, l), 0
                baris.append(dict(seri_kode=s, wilayah_kode=w, nama=nama[w], tahun=t,
                                  status=st, sebab=sb, nilai=v, kode_status=ks))
    g = pd.DataFrame(baris)
    g.drop(columns="kode_status").to_csv(PROFIL / "grid_panel.csv", index=False)

    # 4. kelengkapan per tahun dan per seri (belum_berdiri & belum_terbit tidak dihitung missing)
    # REVISI: buang status belum_terbit juga dari sel yang diharapkan
    ada = g[~g["status"].isin(["belum_berdiri", "belum_terbit"])]
    kt = (ada.groupby(["seri_kode", "tahun"])
          .agg(sel_diharapkan=("status", "size"),
               sel_terisi=("status", lambda x: int((x == "terisi").sum()))).reset_index())
    kt["persen_terisi"] = (100 * kt["sel_terisi"] / kt["sel_diharapkan"]).round(1)
    kt.to_csv(PROFIL / "kelengkapan_per_tahun.csv", index=False)

    ks = (g.groupby("seri_kode")
          .agg(tahun_awal=("tahun", "min"), tahun_akhir=("tahun", "max"),
               sel_grid=("status", "size"),
               belum_berdiri=("status", lambda x: int((x == "belum_berdiri").sum())),
               belum_terbit=("status", lambda x: int((x == "belum_terbit").sum())),
               terisi=("status", lambda x: int((x == "terisi").sum())),
               kosong=("status", lambda x: int((x == "kosong").sum()))).reset_index())
    
    # REVISI: Masukkan belum_terbit ke dalam pengurangan sel_diharapkan
    ks["sel_diharapkan"] = ks["sel_grid"] - ks["belum_berdiri"] - ks["belum_terbit"]
    ks["persen_terisi"] = (100 * ks["terisi"] / ks["sel_diharapkan"]).round(1)
    
    sb = g[g["status"] == "kosong"].pivot_table(index="seri_kode", columns="sebab",
                                                values="tahun", aggfunc="count", fill_value=0)
    ks = ks.merge(sb.reset_index(), on="seri_kode", how="left").fillna(0)
    ks.to_csv(PROFIL / "kelengkapan_per_seri.csv", index=False)

    # Hanya detail untuk sel yang benar-benar missing (kosong)
    kd = (g[g["status"] == "kosong"].groupby(["seri_kode", "wilayah_kode", "nama", "sebab"])
          .agg(n_sel=("tahun", "size"),
               tahun=("tahun", lambda x: " ".join(map(str, sorted(x))))).reset_index())
    kd.to_csv(PROFIL / "sel_kosong_detail.csv", index=False)

    for s, gg in g.groupby("seri_kode"):
        peta_sel(gg, s)

    # 5. laju provinsi vs nasional (var1161)
    pv = prov[(prov["seri_kode"] == "var1161") & prov["wilayah_kode"].isin(prov38)]
    r = pv.groupby("tahun")["nilai_num"].agg(
        median_prov="median", min_prov="min", max_prov="max", n_prov="count")
    n = nas[nas["seri_kode"] == "var1161"].groupby("tahun")["nilai_num"].first().rename("nasional")
    c = r.join(n, how="left")
    c["selisih_nasional_median"] = c["nasional"] - c["median_prov"]
    c["nasional_dalam_rentang"] = (c["nasional"] >= c["min_prov"]) & (c["nasional"] <= c["max_prov"])
    c["arah_sama"] = np.sign(c["nasional"]) == np.sign(c["median_prov"])
    c.reset_index().round(3).to_csv(PROFIL / "laju_provinsi_vs_nasional.csv", index=False)

    pd.set_option("display.width", 200)
    print("\n=== KELENGKAPAN PER SERI ===")
    print(ks.to_string())
    print("\n=== KELENGKAPAN PER TAHUN ===")
    print(kt.to_string())
    print("\n=== LAJU var1161: PROVINSI VS NASIONAL ===")
    print(c.round(2).to_string())
    ok = c.dropna(subset=["nasional"])
    if len(ok):
        print("korelasi nasional vs median provinsi:", round(ok["nasional"].corr(ok["median_prov"]), 3))
        print("tahun nasional di luar rentang provinsi:", ok.index[~ok["nasional_dalam_rentang"]].tolist())
        print("tahun arah berlawanan:", ok.index[~ok["arah_sama"]].tolist())
    else:
        print("tidak ada baris nasional var1161")
        
    # REVISI: Output terminal dipisah menjadi 4 baris
    print("\nsel_missing (kosong):", int((g["status"] == "kosong").sum()))
    print("sel_belum_terbit:", int((g["status"] == "belum_terbit").sum()))
    print("sel_belum_berdiri:", int((g["status"] == "belum_berdiri").sum()))
    print("sel_kosong_grid (missing + belum_terbit):", int(g["status"].isin(["kosong", "belum_terbit"]).sum()))
    print("selesai. Lihat reports/profil/ dan reports/gambar/grid_*.png")


if __name__ == "__main__":
    main()