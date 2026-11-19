"""Tahap 2 (pembanding): profil SDG_0821_NOC_RT, SDG_B821_NOC_RT, SDG_0922_NOC_RT,
SL.GDP.PCAP.EM.KD, NV.IND.MANF.ZS. Hanya membaca hasil ekstraksi dan menulis
tabel di reports/profil/. Data tidak diubah."""
import re
from pathlib import Path
import pandas as pd

from src.ekstraksi import jalankan
from src.silver.analisis_tahap2 import kumpulkan

PROFIL = Path("reports/profil")
PROFIL.mkdir(parents=True, exist_ok=True)
TAHUN_BERJALAN = 2026   # angka ILO setelah tahun ini dianggap proyeksi

ILO = ["SDG_0821_NOC_RT", "SDG_B821_NOC_RT", "SDG_0922_NOC_RT"]
WDI = ["SL.GDP.PCAP.EM.KD", "NV.IND.MANF.ZS"]

PASANGAN = {
    "SDG_0821_NOC_RT": ["var1161"],
    "SDG_B821_NOC_RT": ["var1161"],
    "SL.GDP.PCAP.EM.KD": ["var1161"],
    "NV.IND.MANF.ZS": ["var1214"],
    "SDG_0922_NOC_RT": ["var2755"],
}
CATATAN = {
    "SDG_0821_NOC_RT": "laju output per pekerja, estimasi model ILO, PDB konstan 2015 dolar AS; beda basis dengan SDG_B821_NOC_RT",
    "SDG_B821_NOC_RT": "laju output per pekerja, estimasi model ILO, PDB konstan 2021 dolar internasional PPP; beda basis dengan SDG_0821_NOC_RT",
    "SL.GDP.PCAP.EM.KD": "WDI berupa tingkat (konstan 2021 PPP), bukan laju; hitung laju dulu sebelum dibandingkan dengan var1161; dasar PPP sama dengan SDG_B821_NOC_RT",
    "NV.IND.MANF.ZS": "persen PDB; dasar harga tidak dinyatakan di metadata WDI; dasar harga var1214 juga belum diketahui, periksa di tahap 6",
    "SDG_0922_NOC_RT": "proporsi tenaga kerja manufaktur (ISIC); sumber dan tahun referensi dapat berbeda dari angka nasional BPS; irisan hanya sampai 2023",
}
SATUAN_PANDUAN = {
    "SDG_0821_NOC_RT": "laju pertumbuhan (konfirmasi dari metadata)",
    "SDG_B821_NOC_RT": "laju pertumbuhan (konfirmasi dari metadata)",
    "SDG_0922_NOC_RT": "proporsi (konfirmasi dari metadata)",
    "SL.GDP.PCAP.EM.KD": "dolar PPP konstan, tingkat (panduan kelompok bagian 3)",
    "NV.IND.MANF.ZS": "persen PDB (konfirmasi dari metadata)",
}
INFO = {"REF_AREA", "FREQ", "MEASURE", "UNIT_MEASURE", "UNIT_MULT", "SOURCE",
        "INDICATOR", "COLLECTION", "REPORTING_TYPE", "DECIMALS", "DATAFLOW"}


def kol(df, kandidat):
    peta = {c.upper(): c for c in df.columns}
    for k in kandidat:
        if k in peta:
            return peta[k]
    return None


def seri_ilo(teks):
    m = re.search(r"DF_(SDG_[A-Z0-9]+_NOC_RT)", str(teks).upper())
    return m.group(1) if m else None


def total_like(v):
    u = str(v).upper()
    return (u in {"T", "_T", "Z", "_Z", "-", "NAN", "ALL"} or u.endswith("_T")
            or "TOTAL" in u or u.endswith("NAT"))


def mampat(tahun):
    th = sorted(tahun)
    if not th:
        return "tidak ada"
    if th == list(range(th[0], th[-1] + 1)):
        return f"{th[0]}-{th[-1]} ({len(th)} tahun)"
    return " ".join(map(str, th))


def ringkas(g):
    ok = g.loc[g["nilai_num"].notna(), "tahun"].dropna().astype(int)
    th = sorted(set(ok))
    if not th:
        return dict(n_obs=0, tahun_awal="", tahun_akhir="", n_tahun=0,
                    tahun_hilang="", tahun_proyeksi="", _tahun=set())
    hilang = sorted(set(range(th[0], th[-1] + 1)) - set(th))
    proy = [t for t in th if t > TAHUN_BERJALAN]
    return dict(n_obs=len(ok), tahun_awal=th[0], tahun_akhir=th[-1], n_tahun=len(th),
                tahun_hilang=" ".join(map(str, hilang)),
                tahun_proyeksi=" ".join(map(str, proy)), _tahun=set(th))


def profil_ilo():
    pass


def baca_ilo(hasil):
    out = []
    for jalur, df in kumpulkan(hasil):
        kb = kol(df, ["_BERKAS_RAW", "BERKAS_RAW"])
        d = df.copy()
        d["_seri"] = d[kb].map(seri_ilo) if kb else seri_ilo(jalur)
        d = d[d["_seri"].isin(ILO)]
        if len(d):
            out.append(d)
    if not out:
        print("Tabel ILO (DF_SDG_...) tidak ditemukan di hasil jalankan().")
        return [], pd.DataFrame()
    d = pd.concat(out, ignore_index=True)
    cT = kol(d, ["TIME_PERIOD", "TIME", "PERIODE", "TAHUN"])
    cV = kol(d, ["OBS_VALUE", "NILAI", "VALUE"])
    kb = kol(d, ["_BERKAS_RAW", "BERKAS_RAW"])
    if cT is None or cV is None:
        print("Kolom ILO belum dikenali. Kolom yang ada:", d.columns.tolist())
        return [], pd.DataFrame()
    d["tahun"] = pd.to_numeric(d[cT].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
    d["nilai_num"] = pd.to_numeric(d[cV], errors="coerce")
    sistem = {x for x in [cT, cV, kb, "_seri", "tahun", "nilai_num"] if x}
    NONDIM = {"DATAFLOW", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "UNIT_MEASURE_TYPE",
           "SOURCE", "DECIMALS", "UPPER_BOUND", "LOWER_BOUND",
           "STRUCTURE", "STRUCTURE_ID", "ACTION"}
    dims = [c for c in d.columns
         if c.upper() not in NONDIM
         and not c.upper().startswith(("NOTE", "OBS_", "_"))
         and c not in ("tahun", "nilai_num")
         and d[c].notna().any()]
    for c in dims:
        d[c] = d[c].fillna("-").astype(str)
    kstat = kol(d, ["OBS_STATUS"])

    dim_rows, rows = [], []
    for s, g in d.groupby("_seri"):
        for c in dims:
            v = g[c].value_counts()
            dim_rows.append(dict(sumber="ILOSTAT", seri_kode=s, dimensi=c,
                                 n_nilai_unik=len(v),
                                 nilai="; ".join(f"{k} ({n})" for k, n in v.head(15).items())))
    for key, g in d.groupby(["_seri"] + dims):
        key = key if isinstance(key, tuple) else (key,)
        s, vals = key[0], dict(zip(dims, key[1:]))
        rinc = {c: v for c, v in vals.items() if c.upper() not in INFO}
        sat = " ".join(vals[c] for c in dims if c.upper() in {"UNIT_MEASURE", "UNIT_MULT"})
        area = next((v for c, v in vals.items() if c.upper() == "REF_AREA"), "")
        frek = next((v for c, v in vals.items() if c.upper() == "FREQ"), "")
        r = dict(sumber="ILOSTAT", seri_kode=s,
                 rincian="; ".join(f"{c}={v}" for c, v in rinc.items()) or "tanpa dimensi rincian",
                 wilayah=area, frekuensi=frek)
        r.update(ringkas(g))
        r["satuan_sumber"] = sat or "tidak ada kolom satuan"
        r["satuan_panduan"] = SATUAN_PANDUAN[s]
        r["status_obs"] = "; ".join(sorted(g[kstat].dropna().astype(str).unique())) if kstat else ""
        r["_nontotal"] = [f"{c}={v}" for c, v in rinc.items() if not total_like(v)]
        r["_area_ok"] = (area == "") or ("IDN" in area.upper())
        r["_freq_ok"] = frek in ("", "A")
        rows.append(r)
    return rows, pd.DataFrame(dim_rows)


def baca_wdi(hasil):
    out = []
    for jalur, df in kumpulkan(hasil):
        j = jalur.lower().replace("\\", "/")
        if "wdi" not in j or "/data/" not in j:
            continue
        for kode in WDI:
            for c in df.columns:
                m = df[c].astype(str).str.contains(kode, regex=False)
                if m.any():
                    sub = df[m].copy()
                    sub["_seri"] = kode
                    out.append(sub)
                    break
    if not out:
        print("Baris WDI untuk", WDI, "tidak ditemukan di tabel data WDI.")
        return []
    d = pd.concat(out, ignore_index=True)
    cN = kol(d, ["COUNTRYISO3CODE", "COUNTRY", "NEGARA", "WILAYAH", "REF_AREA", "COUNTRY_ID"])
    cY = kol(d, ["DATE", "TAHUN", "PERIODE", "TIME_PERIOD", "YEAR", "TIME"])
    cV = kol(d, ["VALUE", "NILAI", "OBS_VALUE"])
    cU = kol(d, ["UNIT", "SATUAN"])
    if cY is None or cV is None:
        print("Kolom WDI belum dikenali. Kolom yang ada:", d.columns.tolist())
        return []
    d["tahun"] = pd.to_numeric(d[cY].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
    d["nilai_num"] = pd.to_numeric(d[cV], errors="coerce")
    d["_neg"] = d[cN].astype(str) if cN else "tidak diketahui"
    rows = []
    for (s, neg), g in d.groupby(["_seri", "_neg"]):
        r = dict(sumber="WDI", seri_kode=s, rincian="tanpa dimensi rincian (hanya negara)",
                 wilayah=neg[:60], frekuensi="A")
        r.update(ringkas(g))
        r["satuan_sumber"] = ("; ".join(sorted(g[cU].dropna().astype(str).unique()))
                              if cU else "tidak ada kolom satuan")
        r["satuan_panduan"] = SATUAN_PANDUAN[s]
        r["status_obs"] = ""
        r["_nontotal"] = []
        r["_area_ok"] = bool(re.search(r"\bIDN?\b|INDONESIA", neg.upper()))
        r["_freq_ok"] = True
        rows.append(r)
    return rows


def tahun_utama():
    ps = pd.read_csv(PROFIL / "profil_per_seri.csv")
    nas = pd.read_csv(PROFIL / "nasional_vs_provinsi.csv")
    hasil = {}
    for s, a in ps.groupby("seri_kode"):
        awal = int(pd.to_numeric(a["periode_awal"]).min())
        akhir = int(pd.to_numeric(a["periode_akhir"]).max())
        n = nas[(nas["seri_kode"] == s) & nas["nasional"].notna()]
        hasil[s] = dict(prov=set(range(awal, akhir + 1)),
                        nas=set(pd.to_numeric(n["periode"], errors="coerce").dropna().astype(int)))
    return hasil


def susun_kandidat(rows, utama):
    out = []
    for r in rows:
        for su in PASANGAN[r["seri_kode"]]:
            u = utama.get(su, dict(prov=set(), nas=set()))
            th = {t for t in r["_tahun"] if t <= TAHUN_BERJALAN}
            dasar = "baris Indonesia" if u["nas"] else "rentang provinsi"
            ref = u["nas"] or u["prov"]
            irisan = th & ref
            masalah = []
            if r["_nontotal"]:
                masalah.append("rincian bukan total (" + ", ".join(r["_nontotal"])
                               + "), sedangkan seri utama hanya total")
            if not r["_area_ok"]:
                masalah.append("wilayah bukan Indonesia")
            if not r["_freq_ok"]:
                masalah.append("frekuensi bukan tahunan")
            if not irisan:
                masalah.append("tidak ada tahun beririsan dengan seri utama")
            ya = not masalah
            alasan = ("tanpa rincian atau semua rincian berkode total, wilayah Indonesia, tahunan, "
                      f"beririsan dengan {su} ({dasar}). " if ya else "; ".join(masalah) + ". ")
            alasan += CATATAN[r["seri_kode"]]
            if r["tahun_proyeksi"]:
                alasan += f". Tahun proyeksi ({r['tahun_proyeksi']}) dikeluarkan dari irisan"
            out.append(dict(sumber=r["sumber"], seri_pembanding=r["seri_kode"], rincian=r["rincian"],
                            seri_utama=su, dasar_irisan=dasar,
                            tahun_pembanding=mampat(r["_tahun"]),
                            tahun_irisan=mampat(irisan), n_irisan=len(irisan),
                            kandidat_sebanding="ya" if ya else "tidak", alasan=alasan))
    return pd.DataFrame(out)


def main():
    hasil = jalankan()
    rows_ilo, dim = baca_ilo(hasil)
    rows_wdi = baca_wdi(hasil)
    rows = rows_ilo + rows_wdi
    if not rows:
        raise SystemExit("Tidak ada baris pembanding terbaca. Kirim pesan di atas ke saya.")
    tabel = pd.DataFrame(rows)
    publik = [c for c in tabel.columns if not c.startswith("_")]
    tabel[publik].to_csv(PROFIL / "pembanding_ketersediaan.csv", index=False)
    if len(dim):
        dim.to_csv(PROFIL / "pembanding_dimensi_ilo.csv", index=False)
    kand = susun_kandidat(rows, tahun_utama())
    kand.to_csv(PROFIL / "pembanding_kandidat.csv", index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print("\n=== KETERSEDIAAN ===")
    print(tabel[["sumber", "seri_kode", "rincian", "n_obs", "tahun_awal", "tahun_akhir",
                 "n_tahun", "tahun_hilang", "tahun_proyeksi"]].to_string())
    if len(dim):
        print("\n=== DIMENSI ILO ===")
        print(dim[["seri_kode", "dimensi", "n_nilai_unik", "nilai"]].to_string())
    print("\n=== KANDIDAT SEBANDING ===")
    print(kand[["seri_pembanding", "seri_utama", "tahun_irisan", "kandidat_sebanding"]].to_string())
    print("\nselesai. Lihat reports/profil/pembanding_*.csv")


if __name__ == "__main__":
    main()
