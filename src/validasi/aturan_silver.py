"""Aturan validasi dasar Silver (tahap 8, dimulai sejak Sprint 1).

Dipanggil dari pipeline.py: validasi.jalankan(silver, gold)
Bisa juga berdiri sendiri:   python -m src.validasi.aturan_silver data/silver/silver.parquet
Gold belum divalidasi di Sprint 1 (menunggu panel Gold di Sprint 2).
"""
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

AKAR = Path(__file__).resolve().parents[2]
LAPORAN = AKAR / "reports" / "validasi.md"
NIM = "124450111"
TAHUN_BERJALAN = 2026  # angka ILO setelah tahun ini = proyeksi (panduan kelompok 4.2)

KOLOM_WAJIB = ["sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode", "jenis_periode",
               "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw"]
KUNCI = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]

# 38 provinsi susunan 2025: kode BPS dua digit x 100, plus 9999 = Indonesia
KODE_BPS = [11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 31, 32, 33, 34, 35, 36, 51, 52, 53,
            61, 62, 63, 64, 65, 71, 72, 73, 74, 75, 76, 81, 82, 91, 92, 93, 94, 95, 96]
WILAYAH_VALID = {9999} | {k * 100 for k in KODE_BPS}

PERIODE_RE = r"^\d{4}(-S[12]|-Q[1-4]|-(0[1-9]|1[0-2]))?$"

# Seri berupa LAJU pertumbuhan: boleh negatif, jadi tidak ikut aturan proporsi 0-100.
SERI_LAJU = {"var1161", "SDG_0821_NOC_RT", "SDG_B821_NOC_RT"}
RENTANG_LAJU = (-50, 50)           # batas kewajaran (persen); pelanggar ditinjau, bukan otomatis salah
SERI_TINGKAT_POSITIF = {"var1344", "SL.GDP.PCAP.EM.KD"}   # rupiah / dolar PPP: harus > 0
SATUAN_PERSEN = {"persen", "%", "percent"}
SATUAN_KOSONG = {"", "tidak_ada", "nan", "none"}


@dataclass
class Hasil:
    nama: str
    lolos: bool
    detail: str


def _baris(df, mask, kolom=("sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "nilai", "satuan")):
    kolom = [k for k in kolom if k in df.columns]
    return df.loc[mask, kolom].head(5).to_string(index=False)


def _aturan(df):
    h = []

    def tambah(nama, pelanggar, ket_ok="", contoh=None):
        n = int(pelanggar)
        h.append(Hasil(nama, n == 0, ket_ok if n == 0 else f"{n:,} pelanggaran" + (f"; contoh:\n{contoh}" if contoh else "")))

    # A1 skema
    hilang = [k for k in KOLOM_WAJIB if k not in df.columns]
    h.append(Hasil("A1 sebelas kolom wajib ada", not hilang, "11/11 kolom" if not hilang else f"hilang: {hilang}"))
    if hilang:
        return h  # aturan lain bergantung pada kolom wajib

    # B. kunci dan kelengkapan
    kembar = df.duplicated(KUNCI, keep=False)
    tambah("B1 kunci unik (sumber+seri+wilayah+periode+rincian+berkas)", kembar.sum(),
           f"{len(df):,} baris unik", _baris(df, kembar))
    kosong = df[KOLOM_WAJIB].isna().any(axis=1)
    tambah("B2 tidak ada sel kosong di kolom wajib", kosong.sum(), contoh=_baris(df, kosong))
    nilai = pd.to_numeric(df["nilai"], errors="coerce")
    tak_hingga = nilai.isna() | ~nilai.abs().lt(float("inf"))
    tambah("B3 nilai numerik dan berhingga", tak_hingga.sum(), contoh=_baris(df, tak_hingga))

    # C. konsistensi satuan
    satuan = df["satuan"].astype(str).str.strip().str.lower()
    nuni = df.groupby(["sumber", "seri_kode", "rincian"])["satuan"].nunique()
    ganda = nuni[nuni > 1]
    h.append(Hasil("C1 satu satuan per (seri_kode, rincian)", ganda.empty,
                   f"{len(nuni)} pasangan seri-rincian" if ganda.empty else f"{len(ganda)} pasangan bersatuan ganda: {list(ganda.index[:5])}"))
    belum = satuan.isin(SATUAN_KOSONG)
    tambah("C2 satuan sudah ditetapkan (tidak kosong / tidak_ada)", belum.sum(),
           contoh=f"seri bermasalah: {sorted(df.loc[belum, 'seri_kode'].astype(str).unique())[:6]}" if belum.any() else None)

    # D. rentang nilai
    persen = satuan.isin(SATUAN_PERSEN) & ~df["seri_kode"].isin(SERI_LAJU)
    salah = persen & ~nilai.between(0, 100)
    tambah(f"D1 proporsi (satuan persen, bukan laju) di rentang 0-100 [{int(persen.sum()):,} baris diperiksa]",
           salah.sum(), contoh=_baris(df, salah))
    laju = df["seri_kode"].isin(SERI_LAJU)
    salah = laju & ~nilai.between(*RENTANG_LAJU)
    tambah(f"D2 laju pertumbuhan dalam {RENTANG_LAJU} [{int(laju.sum()):,} baris diperiksa]", salah.sum(), contoh=_baris(df, salah))
    pos = df["seri_kode"].isin(SERI_TINGKAT_POSITIF)
    salah = pos & ~(nilai > 0)
    tambah(f"D3 tingkat (rupiah/dolar PPP) > 0 [{int(pos.sum()):,} baris diperiksa]", salah.sum(), contoh=_baris(df, salah))

    # E. wilayah dan periode
    salah = ~pd.to_numeric(df["wilayah_kode"], errors="coerce").isin(WILAYAH_VALID)
    tambah("E1 wilayah_kode ada di 38 provinsi + 9999", salah.sum(),
           contoh=f"kode asing: {sorted(df.loc[salah, 'wilayah_kode'].astype(str).unique())[:8]}" if salah.any() else None)
    salah = ~df["periode"].astype(str).str.match(PERIODE_RE)
    tambah("E2 format periode (2020 / 2020-S1 / 2020-Q3 / 2020-07)", salah.sum(), contoh=_baris(df, salah))

    # F. proyeksi ILO
    ilo = df["sumber"].astype(str).str.upper().eq("ILOSTAT")
    tahun = pd.to_numeric(df["periode"].astype(str).str[:4], errors="coerce")
    if "proyeksi" not in df.columns:
        h.append(Hasil("F1 baris proyeksi ILO ditandai", False,
                       f"kolom 'proyeksi' belum ada di Silver; {int((ilo & (tahun > TAHUN_BERJALAN)).sum())} baris ILO > {TAHUN_BERJALAN} belum ditandai"))
    else:
        tanda = df["proyeksi"].fillna(False).astype(bool)
        salah = ilo & (tahun > TAHUN_BERJALAN) & ~tanda
        tambah(f"F1 baris ILO > {TAHUN_BERJALAN} ditandai proyeksi=True", salah.sum(),
               f"{int((ilo & tanda).sum())} baris proyeksi ditandai", _baris(df, salah))
        salah = tanda & ~ilo
        tambah("F2 hanya baris ILO yang bertanda proyeksi", salah.sum(), contoh=_baris(df, salah))
    return h


def _tulis_laporan(hasil, n_baris):
    lolos = sum(r.lolos for r in hasil)
    teks = ["# Validasi Silver (otomatis)\n",
            f"Baris Silver: {n_baris:,}  \nAturan: {len(hasil)}, lolos: {lolos}, gagal: {len(hasil) - lolos}\n",
            "| Aturan | Hasil | Keterangan |", "|---|---|---|"]
    for r in hasil:
        teks.append(f"| {r.nama} | {'LOLOS' if r.lolos else 'GAGAL'} | {r.detail.splitlines()[0] if r.detail else ''} |")
    LAPORAN.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN.write_text("\n".join(teks) + "\n", encoding="utf-8")


def jalankan(silver, gold=None, ketat=False):
    """silver: DataFrame atau jalur parquet. ketat=True -> keluar dengan kode 1 bila ada aturan gagal."""
    df = silver if isinstance(silver, pd.DataFrame) else pd.read_parquet(silver)
    hasil = _aturan(df)
    for r in hasil:
        print(f"  [{'LOLOS' if r.lolos else 'GAGAL'}] {r.nama}")
        if r.detail:
            print("         " + r.detail.replace("\n", "\n         "))
    lolos = sum(r.lolos for r in hasil)
    _tulis_laporan(hasil, len(df))
    print(f"validasi Silver: {lolos}/{len(hasil)} aturan lolos -> {LAPORAN.relative_to(AKAR)}")
    print(f"Metrik: python -m src.common.hasil {NIM} aturan_validasi={len(hasil)} aturan_lolos={lolos}")
    if ketat and lolos != len(hasil):
        sys.exit(1)
    return {"aturan_validasi": len(hasil), "aturan_lolos": lolos}


if __name__ == "__main__":
    jalankan(sys.argv[1] if len(sys.argv) > 1 else AKAR / "data" / "silver" / "silver.parquet")