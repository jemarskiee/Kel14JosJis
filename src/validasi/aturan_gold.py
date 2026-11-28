"""Aturan validasi Gold (Sprint 2) dan penggabung dengan aturan Silver.

Dipanggil dari pipeline.py: validasi.jalankan(silver, gold)
Panel Gold dibaca dari data/gold/panel.parquet, karena panel belum dibuat oleh pipeline.py.
Aturan rekonsiliasi (R) menyusul setelah struktur tabelnya jelas.
"""
import sys

import numpy as np
import pandas as pd

from src.wilayah import PROVINSI

from .aturan_silver import AKAR, NIM, RENTANG_LAJU, Hasil, _aturan

PANEL = AKAR / "data" / "gold" / "panel.parquet"
LAPORAN = AKAR / "reports" / "validasi.md"
KOLOM_TERDOKUMENTASI = 11  # dari metrics.json Sprint 1; sesuaikan bila kamus data berubah

KUNCI_PANEL = ["indikator", "wilayah_kode", "periode", "rincian"]
KUNCI_SILVER = ["seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
STATUS_SAH = {"terisi", "belum_berdiri", "belum_terbit", "kosong"}
KOLOM_PERLU = KUNCI_PANEL + ["seri_kode", "satuan", "nilai", "status_sel", "_berkas_raw", "_sha256_raw"]


def _baca(x):
    return x if isinstance(x, pd.DataFrame) else pd.read_parquet(x)


def _contoh(df, mask, kolom):
    kolom = [k for k in kolom if k in df.columns]
    return df.loc[mask, kolom].head(5).to_string(index=False)


def aturan_gold(silver):
    h = []

    def tambah(nama, pelanggar, ok="", contoh=""):
        n = int(pelanggar)
        ket = ok if n == 0 else f"{n:,} pelanggaran" + (f"; contoh:\n{contoh}" if contoh else "")
        h.append(Hasil(nama, n == 0, ket))

    if not PANEL.exists():
        h.append(Hasil("G0 panel Gold ada di data/gold/panel.parquet", False, "berkas tidak ditemukan"))
        return h
    p = pd.read_parquet(PANEL)
    hilang = [k for k in KOLOM_PERLU if k not in p.columns]
    h.append(Hasil("G0 kolom panel yang diperlukan ada", not hilang,
                   f"{len(p):,} sel, {p.shape[1]} kolom" if not hilang else f"hilang: {hilang}"))
    if hilang:
        return h

    kembar = p.duplicated(KUNCI_PANEL, keep=False)
    tambah("G1 kunci panel unik (indikator+wilayah+periode+rincian)", kembar.sum(),
           f"{len(p):,} sel unik", _contoh(p, kembar, KUNCI_PANEL + ["status_sel"]))

    n_sat = p.groupby("indikator")["satuan"].nunique(dropna=False)
    ganda = n_sat[n_sat.ne(1)]
    h.append(Hasil("G2 satu satuan per indikator", ganda.empty,
                   f"{len(n_sat)} indikator" if ganda.empty else f"bersatuan ganda atau kosong: {list(ganda.index)}"))

    terisi = p[p["status_sel"].eq("terisi")].copy()
    s = _baca(silver)[KUNCI_SILVER + ["nilai", "_sha256_raw"]].copy()
    for d in (terisi, s):
        d["wilayah_kode"] = pd.to_numeric(d["wilayah_kode"], errors="coerce")
        d["periode"] = d["periode"].astype(str)
    m = terisi.merge(s, on=KUNCI_SILVER, how="left", suffixes=("_gold", "_silver"), indicator=True)
    tanpa = m["_merge"].ne("both")
    selisih_baris = abs(len(m) - len(terisi))
    tambah(f"G3 setiap sel terisi berpasangan satu-satu di Silver [{len(terisi):,} sel diperiksa]",
           int(tanpa.sum()) + selisih_baris, f"{len(terisi):,} sel berpasangan",
           _contoh(m, tanpa, KUNCI_SILVER))

    ada = m[~tanpa]
    beda_nilai = pd.Series(~np.isclose(ada["nilai_gold"].astype(float), ada["nilai_silver"].astype(float),
                                       rtol=0, atol=1e-9), index=ada.index)
    beda_sha = ada["_sha256_raw_gold"].ne(ada["_sha256_raw_silver"])
    beda = beda_nilai | beda_sha
    tambah("G4 nilai dan sidik berkas Gold sama dengan Silver", beda.sum(), f"{len(ada):,} sel cocok",
           _contoh(ada, beda, KUNCI_SILVER + ["nilai_gold", "nilai_silver"]))

    nilai = pd.to_numeric(p["nilai"], errors="coerce")
    isi = p["status_sel"].eq("terisi")
    tak = ~p["status_sel"].isin(STATUS_SAH) | (isi != nilai.notna())
    tambah("G5 status_sel sah dan nilai ada hanya pada sel terisi", tak.sum(),
           str(p["status_sel"].value_counts().to_dict()), _contoh(p, tak, KUNCI_PANEL + ["status_sel", "nilai"]))

    persen = isi & p["satuan"].eq("persen")
    laju = isi & p["satuan"].eq("persen_per_tahun")
    tingkat = isi & p["satuan"].eq("rupiah_per_tenaga_kerja")
    salah = (persen & ~nilai.between(0, 100)) | (laju & ~nilai.between(*RENTANG_LAJU)) | (tingkat & ~nilai.gt(0))
    tambah("G6 nilai terisi dalam rentang wajar per satuan", salah.sum(),
           f"{int(isi.sum()):,} sel diperiksa", _contoh(p, salah, KUNCI_PANEL + ["satuan", "nilai"]))

    wk = pd.to_numeric(p["wilayah_kode"], errors="coerce")
    salah = ~wk.isin(list(PROVINSI.keys()))
    tambah("G7 wilayah panel = 38 provinsi (tanpa 9999)", salah.sum(), f"{wk.nunique()} wilayah unik",
           _contoh(p, salah, KUNCI_PANEL))
    return h


def _laporan(hasil, n_silver):
    lolos = sum(r.lolos for r in hasil)
    teks = ["# Validasi Silver dan Gold (otomatis)\n",
            f"Baris Silver: {n_silver:,}  \nAturan: {len(hasil)}, lolos: {lolos}, gagal: {len(hasil) - lolos}\n",
            "| Aturan | Hasil | Keterangan |", "|---|---|---|"]
    for r in hasil:
        ket = r.detail.splitlines()[0] if r.detail else ""
        teks.append(f"| {r.nama} | {'LOLOS' if r.lolos else 'GAGAL'} | {ket} |")
    LAPORAN.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN.write_text("\n".join(teks) + "\n", encoding="utf-8")


def jalankan(silver, gold=None, ketat=False):
    s = _baca(silver)
    hasil = _aturan(s) + aturan_gold(s)
    for r in hasil:
        print(f"  [{'LOLOS' if r.lolos else 'GAGAL'}] {r.nama}")
        if r.detail:
            print("         " + r.detail.replace("\n", "\n         "))
    lolos = sum(r.lolos for r in hasil)
    _laporan(hasil, len(s))
    print(f"validasi: {lolos}/{len(hasil)} aturan lolos -> {LAPORAN.relative_to(AKAR)}")
    print(f"Metrik: python -m src.common.hasil {NIM} aturan_validasi={len(hasil)} "
          f"aturan_lolos={lolos} kolom_terdokumentasi={KOLOM_TERDOKUMENTASI}")
    if ketat and lolos != len(hasil):
        sys.exit(1)
    return {"aturan_validasi": len(hasil), "aturan_lolos": lolos}


if __name__ == "__main__":
    jalankan(AKAR / "data" / "silver" / "silver.parquet")
