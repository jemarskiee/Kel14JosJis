"""Aturan validasi tabel nasional (N) dan berkas rekonsiliasi (R0), Sprint 2."""
import pandas as pd

from .aturan_silver import AKAR, RENTANG_LAJU, Hasil

NASIONAL = AKAR / "data" / "gold" / "tabel_nasional_gold.csv"
REKON = AKAR / "data" / "gold" / "rekonsiliasi_nasional.csv"
KOLOM_REKON = ["pasangan", "periode", "nilai_seri_utama", "nilai_pembanding", "selisih", "kategori_penjelasan"]
KATEGORI_SAH = {"definisi berbeda", "metode berbeda", "vintage berbeda", "cakupan berbeda", "belum terjelaskan"}
PASANGAN_WAJIB = ["var1161_vs_ILO_SDG_0821_NOC_RT", "var1161_vs_ILO_SDG_B821_NOC_RT", "var1161_vs_WDI_SL_GDP_PCAP_EM_KD", "var1214_vs_WDI_NV_IND_MANF_ZS", "var2755_vs_ILO_SDG_0922_NOC_RT"]
KUNCI = ["seri_kode", "wilayah", "periode"]
LAJU = ["var1161", "SDG_0821_NOC_RT", "SDG_B821_NOC_RT"]
TINGKAT = ["var1344", "SL.GDP.PCAP.EM.KD"]
PROPORSI = ["var1214", "var2755", "NV.IND.MANF.ZS", "SDG_0922_NOC_RT"]
CUTOFF_PROYEKSI = 2026


def _contoh(d, mask, kolom):
    return d.loc[mask, kolom].head(5).to_string(index=False)


def _aturan_n(d):
    h = []

    kembar = d.duplicated(KUNCI, keep=False)
    n = int(kembar.sum())
    h.append(Hasil("N1 kunci tabel nasional unik (seri_kode+wilayah+periode)", n == 0,
                   f"{len(d):,} baris unik" if n == 0 else f"{n:,} pelanggaran; contoh:\n" + _contoh(d, kembar, KUNCI)))

    kosong = d["satuan"].isna() | d["satuan"].astype(str).str.strip().eq("")
    seri_kosong = sorted(d.loc[kosong, "seri_kode"].unique())
    n_sat = d.loc[~kosong].groupby("seri_kode")["satuan"].nunique()
    ganda = list(n_sat[n_sat.gt(1)].index)
    ok = (not seri_kosong) and (not ganda)
    n_seri = d["seri_kode"].nunique()
    ket = f"{n_seri} seri, satu satuan terisi masing-masing"
    if not ok:
        ket = f"{int(kosong.sum())} baris satuan kosong pada seri {seri_kosong}; satuan ganda pada {ganda}"
    h.append(Hasil("N2 satuan terisi dan satu per seri_kode", ok, ket))

    v = pd.to_numeric(d["nilai"], errors="coerce")
    dikenal = d["seri_kode"].isin(LAJU + TINGKAT + PROPORSI)
    salah = (~dikenal
             | v.isna()
             | (d["seri_kode"].isin(LAJU) & ~v.between(*RENTANG_LAJU))
             | (d["seri_kode"].isin(TINGKAT) & ~v.gt(0))
             | (d["seri_kode"].isin(PROPORSI) & ~v.between(0, 100)))
    n = int(salah.sum())
    h.append(Hasil("N3 nilai tabel nasional dalam rentang wajar per seri_kode", n == 0,
                   f"{len(d):,} baris diperiksa" if n == 0 else f"{n:,} pelanggaran; contoh:\n" + _contoh(d, salah, KUNCI + ["nilai"])))

    nama4 = f"N4 baris ILO setelah {CUTOFF_PROYEKSI} ditandai proyeksi, dan hanya ILO"
    ilo = d["sumber"].eq("ILOSTAT") & d["periode"].gt(CUTOFF_PROYEKSI)
    if "proyeksi" not in d.columns:
        h.append(Hasil(nama4, False, f"kolom proyeksi tidak ada di tabel nasional; {int(ilo.sum())} baris ILO setelah {CUTOFF_PROYEKSI} belum ditandai"))
    else:
        tanda = d["proyeksi"].fillna(False).astype(bool)
        salah = ilo.ne(tanda)
        n = int(salah.sum())
        h.append(Hasil(nama4, n == 0, f"{int(ilo.sum())} baris proyeksi ditandai benar" if n == 0 else f"{n:,} pelanggaran"))
    return h


def _aturan_rekon():
    nama0 = "R0 berkas rekonsiliasi ada dengan kolom wajib (periode, nilai utama, nilai pembanding, selisih, kategori)"
    if not REKON.exists():
        return [Hasil(nama0, False, "data/gold/rekonsiliasi_nasional.csv tidak ditemukan; R1 sampai R5 tidak bisa diperiksa")]
    r = pd.read_csv(REKON)
    hilang = [k for k in KOLOM_REKON if k not in r.columns]
    h = [Hasil(nama0, not hilang, f"{len(r):,} baris, {r['pasangan'].nunique()} pasangan" if not hilang else f"kolom hilang: {hilang}")]
    if hilang:
        return h
    ada = r["selisih"].notna()

    sah = r["kategori_penjelasan"].isin(KATEGORI_SAH)
    salah = ada & ~sah
    n = int(salah.sum())
    h.append(Hasil("R1 setiap baris berselisih punya kategori sah (lima kategori panduan 5.7)", n == 0,
                   f"{int(ada.sum()):,} baris berselisih berkategori sah" if n == 0
                   else f"{n:,} pelanggaran; contoh:\n" + r.loc[salah, ["pasangan", "periode", "selisih", "kategori_penjelasan"]].head(5).to_string(index=False)))

    lengkap = r["nilai_seri_utama"].notna() & r["nilai_pembanding"].notna()
    hitung = r["nilai_seri_utama"] - r["nilai_pembanding"]
    salah = ada & (~lengkap | (r["selisih"] - hitung).abs().gt(0.01))
    n = int(salah.sum())
    h.append(Hasil("R2 selisih sama dengan nilai utama dikurangi nilai pembanding (toleransi 0,01)", n == 0,
                   f"{int(ada.sum()):,} selisih cocok" if n == 0
                   else f"{n:,} pelanggaran; contoh:\n" + r.loc[salah, ["pasangan", "periode", "nilai_seri_utama", "nilai_pembanding", "selisih"]].head(5).to_string(index=False)))

    ilo = r["pasangan"].str.contains("ILO") & r["periode"].gt(CUTOFF_PROYEKSI)
    salah = ilo & ada
    n = int(salah.sum())
    h.append(Hasil(f"R3 baris ILO setelah {CUTOFF_PROYEKSI} tidak ikut rekonsiliasi (tanpa selisih)", n == 0,
                   f"{int(ilo.sum())} baris ILO setelah {CUTOFF_PROYEKSI}, tanpa selisih" if n == 0 else f"{n:,} pelanggaran"))

    ada_pasangan = set(r["pasangan"])
    tanpa_baris = [p for p in PASANGAN_WAJIB if p not in ada_pasangan]
    tanpa_selisih = [p for p in PASANGAN_WAJIB if p in ada_pasangan and not r.loc[r["pasangan"].eq(p), "selisih"].notna().any()]
    ok = (not tanpa_baris) and (not tanpa_selisih)
    h.append(Hasil("R4 kelima pasangan bagian 3 panduan ada dan berselisih", ok,
                   f"{len(PASANGAN_WAJIB)} pasangan lengkap" if ok else f"tanpa baris: {tanpa_baris}; tanpa selisih: {tanpa_selisih}"))

    w = r["pasangan"].eq("var1161_vs_WDI_SL_GDP_PCAP_EM_KD") & ada
    salah = w & ~r["nilai_pembanding"].between(*RENTANG_LAJU)
    n = int(salah.sum())
    h.append(Hasil("R5 pembanding WDI untuk var1161 berupa laju (-50 sampai 50), bukan tingkat", n == 0,
                   f"{int(w.sum())} baris berselisih diperiksa" if n == 0
                   else f"{n:,} pelanggaran; contoh:\n" + r.loc[salah, ["pasangan", "periode", "nilai_pembanding"]].head(5).to_string(index=False)))
    return h


def _aturan_n5(d):
    nama = "N5 baris BPS tabel nasional sama dengan Silver (kode 9999: nilai dan berkas asal)"
    sp = AKAR / "data" / "silver" / "silver.parquet"
    if not sp.exists():
        return Hasil(nama, False, "data/silver/silver.parquet tidak ditemukan")
    s = pd.read_parquet(sp)
    s = s[pd.to_numeric(s["wilayah_kode"], errors="coerce").eq(9999)][["seri_kode", "periode", "_berkas_raw", "nilai"]].copy()
    s["periode"] = pd.to_numeric(s["periode"], errors="coerce")
    b = d[d["sumber"].eq("BPS")].copy()
    m = b.merge(s, on=["seri_kode", "periode", "_berkas_raw"], how="left", suffixes=("", "_silver"), indicator=True)
    tanpa = m["_merge"].ne("both")
    beda = (m["nilai"] - m["nilai_silver"]).abs().gt(1e-9)
    salah = tanpa | beda
    n = int(salah.sum())
    if n == 0:
        return Hasil(nama, True, f"{len(b):,} baris BPS cocok dengan Silver")
    kolom = ["seri_kode", "periode", "_berkas_raw", "nilai", "nilai_silver"]
    return Hasil(nama, False, f"{n:,} pelanggaran; contoh:\n" + m.loc[salah, kolom].head(5).to_string(index=False))


def aturan_nasional():
    h = []
    if NASIONAL.exists():
        d = pd.read_csv(NASIONAL)
        h.extend(_aturan_n(d))
        h.append(_aturan_n5(d))
    else:
        h.append(Hasil("N0 tabel nasional ada di data/gold/tabel_nasional_gold.csv", False, "berkas tidak ditemukan"))
    h.extend(_aturan_rekon())
    return h
