"""Aturan validasi tabel nasional (N) dan berkas rekonsiliasi (R0), Sprint 2."""
import pandas as pd

from .aturan_silver import AKAR, RENTANG_LAJU, Hasil

NASIONAL = AKAR / "data" / "gold" / "tabel_nasional_gold.csv"
REKON = AKAR / "data" / "gold" / "rekonsiliasi.csv"  # nama usulan, belum disepakati
KOLOM_REKON = ["seri_utama", "pembanding", "periode", "nilai_utama", "nilai_pembanding", "selisih", "kategori"]
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


def _aturan_r0():
    nama = "R0 berkas rekonsiliasi ada dengan kolom wajib (periode, nilai utama, nilai pembanding, selisih, kategori)"
    if not REKON.exists():
        return Hasil(nama, False, "data/gold/rekonsiliasi.csv belum ada; aturan R1 dan seterusnya belum bisa diperiksa")
    r = pd.read_csv(REKON)
    hilang = [k for k in KOLOM_REKON if k not in r.columns]
    return Hasil(nama, not hilang, f"{len(r):,} baris" if not hilang else f"kolom hilang: {hilang}")


def aturan_nasional():
    h = []
    if NASIONAL.exists():
        h.extend(_aturan_n(pd.read_csv(NASIONAL)))
    else:
        h.append(Hasil("N0 tabel nasional ada di data/gold/tabel_nasional_gold.csv", False, "berkas tidak ditemukan"))
    h.append(_aturan_r0())
    return h
