"""Menyusun Silver dari tabel mentah: satu skema untuk semua sumber."""
import re
import numpy as np
import pandas as pd

from src import konfigurasi as K
from src import wilayah as W
from src.laporan import ROOT, catat

KOLOM = ["sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "rincian", "nilai",
         "satuan", "sdg_kode", "batas_bawah", "batas_atas", "rujukan_tahun", "proyeksi", "_berkas_raw", "_sha256_raw"]

BULAN = {"januari": "01", "februari": "02", "maret": "03", "april": "04", "mei": "05", "juni": "06", "juli": "07",
         "agustus": "08", "september": "09", "oktober": "10", "november": "11", "desember": "12"}

def periode_bps(tahun, turtahun):
    t = str(tahun).strip()
    p = str(turtahun).strip().lower()
    if p in ("tahun", "tahunan"):
        return t, "tahun"
    if m := re.fullmatch(r"semester\s*(1|2|i|ii)(\s*\(\w+\))?", p):
        return f"{t}-S{'1' if m.group(1) in ('1', 'i') else '2'}", "semester"
    if m := re.fullmatch(r"triwulan\s*(i{1,3}|iv|[1-4])", p):
        no = {"i": 1, "ii": 2, "iii": 3, "iv": 4}.get(m.group(1)) or int(m.group(1))
        return f"{t}-Q{no}", "triwulan"
    if p in BULAN:
        return f"{t}-{BULAN[p]}", "bulan"
    return t, "tahun" # Fallback kalau format aneh

def rincian_teks(pasangan):
    bagian = sorted(f"{k}={v}" for k, v in pasangan)
    return ";".join(bagian) or "total"

def kode_rincian(teks):
    return re.sub(r"[^a-z0-9]+", "_", str(teks).strip().lower()).strip("_")

def rincian_bps(seri, turvar):
    t = str(turvar).strip()
    if t.lower() in K.RINCIAN_TOTAL_BPS:
        return "total"
    dim, kamus = getattr(K, "RINCIAN_BPS", {}).get(seri, ("rincian_bps", {}))
    return f"{dim}={kamus.get(t, kode_rincian(t))}"

def _tingkat(kode):
    return "nasional" if kode == W.INDONESIA else "provinsi"

def dari_bps(mentah):
    if K.FORMAT_BPS == "json":
        d = mentah["bps_json"].copy()
    else:
        d = mentah["bps_csv"].rename(columns={"periode": "turtahun"}).copy()
        
    # --- PATCH PENYESUAIAN NAMA KOLOM DARI EKSTRAKSI TEMANMU ---
    if "wilayah_kode" in d.columns and "wilayah_id" not in d.columns:
        d = d.rename(columns={"wilayah_kode": "wilayah_id"})
    if "rincian" in d.columns and "turvar" not in d.columns:
        d = d.rename(columns={"rincian": "turvar"})
    if "turtahun" not in d.columns:
        d["turtahun"] = "Tahunan"
    # -----------------------------------------------------------

    d["seri_kode"] = "var" + d["var_id"].astype(str)
    d = d[d["seri_kode"].isin(K.SERI)]
    d = pilih_snapshot(d)
    
    kode = d["wilayah_id"].astype(int)
    kabkota = ~(kode.isin(W.NAMA))
    catat(baris_kabkota_dibuang=int(kabkota.sum()))
    d = d[~kabkota]
    per = [periode_bps(t, p) for t, p in zip(d["tahun"], d["turtahun"])]
    kode = d["wilayah_id"].astype(int)
    out = pd.DataFrame({
        "sumber": "bps", "seri_kode": d["seri_kode"].values, "wilayah_kode": kode.values,
        "nama_wilayah": kode.map(W.NAMA).values,
        "periode": [p for p, _ in per], "jenis_periode": [j for _, j in per],
        "rincian": [rincian_bps(s, r) for s, r in zip(d["seri_kode"], d["turvar"])],
        "nilai": pd.to_numeric(d["nilai"], errors="coerce").values,
        "_berkas_raw": d["_berkas_raw"].values, "_sha256_raw": d["_sha256_raw"].values})
    out["rujukan_tahun"] = [K.RUJUKAN_TAHUN.get((s, _tingkat(w))) for s, w in zip(out["seri_kode"], out["wilayah_kode"])]
    return out

def pilih_snapshot(d):
    d = d.assign(_snapshot=d["_berkas_raw"].str.split("/").str[1])
    laporan = []
    pakai = []
    for seri, g in d.groupby("seri_kode"):
        snap = sorted(g["_snapshot"].unique())
        baru = g[g["_snapshot"] == snap[-1]]
        pakai.append(baru)
        kunci = ["wilayah_id", "turvar", "tahun", "turtahun"]
        for lama in snap[:-1]:
            a = g[g["_snapshot"] == lama].set_index(kunci)["nilai"].astype(float)
            b = baru.set_index(kunci)["nilai"].astype(float)
            sama = a.index.intersection(b.index)
            laporan.append({"seri_kode": seri, "snapshot_dipakai": snap[-1], "snapshot_lain": lama,
                            "baris_lain": len(a), "baris_dipakai": len(b), "sel_sama": len(sama),
                            "nilai_berbeda": int(((a[sama] - b[sama]).abs() > 1e-9).sum())})
    if laporan:
        (ROOT / "reports").mkdir(exist_ok=True)
        pd.DataFrame(laporan).to_csv(ROOT / "reports" / "snapshot-bps.csv", index=False)
    catat(bps_snapshot_ganda=len(laporan), bps_snapshot_beda=int(sum(r["nilai_berbeda"] for r in laporan)))
    return pd.concat(pakai).drop(columns="_snapshot") if pakai else d.drop(columns="_snapshot")

def _label_statis(c, level, teks):
    t = re.sub(r"\s+\d+\)?$", "", str(teks).strip())
    k = kode_rincian(t)
    return c.get("kamus_header", {}).get(level, {}).get(k, k)

def _rincian_statis(c, nilai_level):
    pas = []
    for level, (dim, kamus) in c["dimensi"].items():
        v = nilai_level[level]
        if v in c.get("total", ()):
            continue
        pas.append((dim, kamus.get(v, v)))
    return rincian_teks(pas)

def dari_statis(mentah):
    bagian, kosong, uji = [], 0, []
    h_all = mentah["bps_statis_html"]
    c_all = mentah.get("bps_statis", pd.DataFrame(columns=["_berkas_raw"]))
    for seri, c in K.TABEL_STATIS.items():
        d = h_all[h_all["_berkas_raw"].str.endswith(c["berkas"] + ".json")].copy()
        for n, level in enumerate(c["header"], start=1):
            d[level] = [_label_statis(c, level, x) for x in d[f"h{n}"]]
        if "pisah" in c:
            d = d[d[c["pisah"][0]] == c["pisah"][1]]
        d = d[d["tahun"].astype(str).str.fullmatch(r"\d{4}")]
        kosong += int(d["nilai"].isna().sum())
        d = d[d["nilai"].notna()]
        d["rincian"] = [_rincian_statis(c, r) for r in d[list(c["header"])].to_dict("records")]
        d["periode"] = d["tahun"].astype(str)
        bagian.append(pd.DataFrame({
            "sumber": "bps", "seri_kode": seri, "wilayah_kode": d["wilayah_kode"].astype(int).values,
            "nama_wilayah": d["wilayah_kode"].map(W.NAMA).values, "periode": d["periode"].values,
            "jenis_periode": "tahun", "rincian": d["rincian"].values, "nilai": d["nilai"].astype(float).values,
            "_berkas_raw": d["_berkas_raw"].values, "_sha256_raw": d["_sha256_raw"].values}))
    if uji:
        pd.DataFrame(uji).to_csv(ROOT / "reports" / "uji-silang-statis.csv", index=False)
    catat(statis_kosong_dibuang=kosong, statis_uji_beda=int(sum(u["nilai_berbeda"] + u["hanya_html"] + u["hanya_csv"] for u in uji)))
    return pd.concat(bagian, ignore_index=True) if bagian else pd.DataFrame(columns=KOLOM)

def dari_wdi(mentah):
    d = mentah["wdi_data"]
    kosong = int(d["value"].isna().sum())
    d = d[d["value"].notna()]
    out = pd.DataFrame({
        "sumber": "wdi", "seri_kode": d["indicator_id"].values,
        "wilayah_kode": [W.dari_negara("wdi", c) for c in d["country_id"]],
        "periode": d["date"].astype(str).values, "jenis_periode": "tahun", "rincian": "total",
        "nilai": d["value"].astype(float).values,
        "_berkas_raw": d["_berkas_raw"].values, "_sha256_raw": d["_sha256_raw"].values})
    out["nama_wilayah"] = out["wilayah_kode"].map(W.NAMA)
    return out, kosong

def dari_ilostat(mentah):
    from src import kamus_ilo
    from src.ekstraksi.ilostat import dimensi
    d = mentah["ilo_csv"].copy()
    d = d[d["seri_kode"].isin(K.SERI)]
    kosong = int((d["OBS_VALUE"] == "").sum())
    d = d[d["OBS_VALUE"] != ""]
    dims = dimensi(d)
    d[dims] = d[dims].fillna("")
    dims = [k for k in dims if d[k].ne("").any()]
    rinci = []
    for r in d[dims].to_dict("records"):
        pas = [kamus_ilo.kode(k, r[k]) for k in dims if r[k]]
        rinci.append(rincian_teks([p for p in pas if p]))
    jenis = d["FREQ"].map({"A": "tahun", "Q": "triwulan", "M": "bulan"})
    out = pd.DataFrame({
        "sumber": "ilostat", "seri_kode": d["seri_kode"].values,
        "wilayah_kode": [W.dari_negara("ilostat", c) for c in d["REF_AREA"]],
        "periode": d["TIME_PERIOD"].values, "jenis_periode": jenis.values, "rincian": rinci,
        "nilai": pd.to_numeric(d["OBS_VALUE"]).values,
        "batas_bawah": pd.to_numeric(d["LOWER_BOUND"].replace("", np.nan)).values,
        "batas_atas": pd.to_numeric(d["UPPER_BOUND"].replace("", np.nan)).values,
        "status_obs": d["OBS_STATUS"].replace("", None).values,
        "_berkas_raw": d["_berkas_raw"].values, "_sha256_raw": d["_sha256_raw"].values})
    out["nama_wilayah"] = out["wilayah_kode"].map(W.NAMA)
    return out, d

def terapkan_galat(s):
    from fnmatch import fnmatch
    aturan = getattr(K, "GALAT_INPUT", {})
    catatan, buang = [], pd.Series(False, index=s.index)
    for (seri, wil, per, rinci), a in aturan.items():
        cocok = (s["seri_kode"] == seri) & (s["wilayah_kode"] == wil) & (s["periode"] == per) & (s["rincian"] == rinci)
        cocok &= s["_berkas_raw"].map(lambda b: fnmatch(b, a.get("berkas", "*")))
        if not cocok.any():
            raise ValueError(f"GALAT_INPUT {(seri, wil, per, rinci)} tidak cocok dengan baris Silver mana pun")
        for i in s.index[cocok]:
            catatan.append({"seri_kode": seri, "wilayah_kode": wil, "periode": per, "rincian": rinci,
                            "nilai_asli": s.at[i, "nilai"], "tindakan": str(a["tindakan"]), "bukti": a["bukti"],
                            "_berkas_raw": s.at[i, "_berkas_raw"]})
        if a["tindakan"] == "buang":
            buang |= cocok
        else:
            s.loc[cocok, "nilai"] = float(a["tindakan"])
    hasil = pd.DataFrame(catatan, columns=["seri_kode", "wilayah_kode", "periode", "rincian", "nilai_asli", "tindakan",
                                           "bukti", "_berkas_raw"])
    if len(hasil):
        (ROOT / "reports").mkdir(exist_ok=True)
        hasil.to_csv(ROOT / "reports" / "galat-input.csv", index=False)
    catat(galat_ditangani=len(hasil))
    return s[~buang].reset_index(drop=True), hasil

def susun(mentah):
    bagian, info = [], {"cakupan_who": {}}
    if "bps_json" in mentah or "bps_csv" in mentah:
        bagian.append(dari_bps(mentah))
    if getattr(K, "TABEL_STATIS", None) and "bps_statis_html" in mentah:
        bagian.append(dari_statis(mentah))
    if "wdi_data" in mentah:
        wdi, info["wdi_null"] = dari_wdi(mentah)
        bagian.append(wdi)
    if "ilo_csv" in mentah:
        ilo, info["ilo_patah"] = dari_ilostat(mentah)
        bagian.append(ilo)
        
    if not bagian:
        raise ValueError("Tidak ada data valid yang bisa diproses dari hasil ekstraksi.")

    s = pd.concat(bagian, ignore_index=True)
    s, info["galat"] = terapkan_galat(s)
    s["satuan"] = s["seri_kode"].map(lambda k: K.SERI[k]["satuan"])
    s["sdg_kode"] = s["seri_kode"].map(lambda k: K.SERI[k]["sdg"])
    for k in ("batas_bawah", "batas_atas"):
        if k not in s:
            s[k] = np.nan
    s["rujukan_tahun"] = pd.array(s.get("rujukan_tahun", pd.Series([None] * len(s))), dtype="Int64")
    s["wilayah_kode"] = s["wilayah_kode"].astype("int64")
    s["nilai"] = s["nilai"].astype("float64")
    
    # TAMBAHAN F1: Menandai proyeksi ILO
    s["proyeksi"] = False
    for seri, tahun_list in K.PROYEKSI.items():
        mask = (s['seri_kode'] == seri) & (s['periode'].astype(str).isin(tahun_list))
        s.loc[mask, 'proyeksi'] = True

    kolom = KOLOM[:-2] + ["status_obs"] + KOLOM[-2:] if "status_obs" in s else KOLOM
    if "status_obs" in s:
        s["status_obs"] = s["status_obs"].astype("string")
    if "proyeksi" not in kolom:
        kolom.insert(kolom.index("_berkas_raw"), "proyeksi")
        
    s = s[kolom].sort_values(["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]).reset_index(drop=True)
    catat(baris_silver=len(s), seri_silver=int(s["seri_kode"].nunique()),
          rincian_dienkode=int(s["rincian"].nunique()), wdi_null_dibuang=info.get("wdi_null", 0),
          who_kosong_dibuang=info.get("who_kosong", 0), who_kembar_setara=info.get("who_kembar", (0, 0))[0],
          who_kembar_bertentangan=info.get("who_kembar", (0, 0))[1])
    return s, info