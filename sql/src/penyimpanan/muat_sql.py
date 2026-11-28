from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Mapping, Any


def _ambil_nilai(baris: Any, kunci: str, fallback: Any = None) -> Any:
    if isinstance(baris, Mapping):
        return baris.get(kunci, fallback)
    return getattr(baris, kunci, fallback)


def muat_ke_sqlite(
    db_path: str | Path,
    schema_path: str | Path,
    baris_silver: Iterable[Mapping[str, Any] | Any] = (),
    baris_gold_provinsi: Iterable[Mapping[str, Any] | Any] = (),
    baris_gold_nasional: Iterable[Mapping[str, Any] | Any] = (),
    baris_gold_rekonsiliasi: Iterable[Mapping[str, Any] | Any] = (),
) -> dict[str, int]:
    """Membuat skema SQLite (jika belum ada), memuat data, dan mengembalikan jumlah baris per tabel."""
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    ddl_sql = Path(schema_path).read_text(encoding="utf-8")

    with sqlite3.connect(db_file) as conn:
        conn.executescript(ddl_sql)

        silver_list = list(baris_silver)
        if silver_list:
            conn.executemany(
                """
                INSERT OR IGNORE INTO silver_indikator (
                    seri_kode, wilayah_kode, nama_wilayah, periode, jenis_periode,
                    rincian, satuan, nilai, sumber, proyeksi, _berkas_raw, _sha256_raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        _ambil_nilai(b, "seri_kode"),
                        _ambil_nilai(b, "wilayah_kode"),
                        _ambil_nilai(b, "nama_wilayah"),
                        _ambil_nilai(b, "periode"),
                        _ambil_nilai(b, "jenis_periode"),
                        _ambil_nilai(b, "rincian"),
                        _ambil_nilai(b, "satuan"),
                        _ambil_nilai(b, "nilai"),
                        _ambil_nilai(b, "sumber"),
                        _ambil_nilai(b, "proyeksi"),
                        _ambil_nilai(b, "_berkas_raw"),
                        _ambil_nilai(b, "_sha256_raw"),
                    )
                    for b in silver_list
                ],
            )

        prov_list = list(baris_gold_provinsi)
        if prov_list:
            conn.executemany(
                """
                INSERT INTO gold_panel_provinsi (
                    sumber, indikator, seri_kode, rincian, wilayah_kode, nama_wilayah,
                    periode, jenis_periode, nilai, satuan, sdg_kode, batas_bawah,
                    batas_atas, status_sel, penanda, rujukan_tahun, proyeksi,
                    _berkas_raw, _sha256_raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        _ambil_nilai(b, "sumber"),
                        _ambil_nilai(b, "indikator"),
                        _ambil_nilai(b, "seri_kode"),
                        _ambil_nilai(b, "rincian"),
                        _ambil_nilai(b, "wilayah_kode"),
                        _ambil_nilai(b, "nama_wilayah"),
                        _ambil_nilai(b, "periode"),
                        _ambil_nilai(b, "jenis_periode"),
                        _ambil_nilai(b, "nilai"),
                        _ambil_nilai(b, "satuan"),
                        _ambil_nilai(b, "sdg_kode"),
                        _ambil_nilai(b, "batas_bawah"),
                        _ambil_nilai(b, "batas_atas"),
                        _ambil_nilai(b, "status_sel"),
                        _ambil_nilai(b, "penanda"),
                        _ambil_nilai(b, "rujukan_tahun"),
                        _ambil_nilai(b, "proyeksi"),
                        _ambil_nilai(b, "_berkas_raw"),
                        _ambil_nilai(b, "_sha256_raw"),
                    )
                    for b in prov_list
                ],
            )

        nas_list = list(baris_gold_nasional)
        if nas_list:
            conn.executemany(
                """
                INSERT INTO gold_tabel_nasional (
                    periode, seri_kode, jenis_seri, seri_utama, wilayah,
                    nilai, sumber, satuan, _berkas_raw, _sha256_raw
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        _ambil_nilai(b, "periode"),
                        _ambil_nilai(b, "seri_kode"),
                        _ambil_nilai(b, "jenis_seri"),
                        _ambil_nilai(b, "seri_utama"),
                        _ambil_nilai(b, "wilayah"),
                        _ambil_nilai(b, "nilai"),
                        _ambil_nilai(b, "sumber"),
                        _ambil_nilai(b, "satuan"),
                        _ambil_nilai(b, "_berkas_raw"),
                        _ambil_nilai(b, "_sha256_raw"),
                    )
                    for b in nas_list
                ],
            )

        rek_list = list(baris_gold_rekonsiliasi)
        if rek_list:
            conn.executemany(
                """
                INSERT INTO gold_rekonsiliasi (
                    periode, seri_utama, seri_pembanding, wilayah,
                    nilai_utama, nilai_pembanding, selisih, kategori_selisih
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        _ambil_nilai(b, "periode"),
                        _ambil_nilai(b, "seri_utama"),
                        _ambil_nilai(b, "seri_pembanding"),
                        _ambil_nilai(b, "wilayah"),
                        _ambil_nilai(b, "nilai_utama"),
                        _ambil_nilai(b, "nilai_pembanding"),
                        _ambil_nilai(b, "selisih"),
                        _ambil_nilai(b, "kategori_selisih"),
                    )
                    for b in rek_list
                ],
            )

        jumlah_baris: dict[str, int] = {}
        for nama_tabel in (
            "silver_indikator",
            "gold_panel_provinsi",
            "gold_tabel_nasional",
            "gold_rekonsiliasi",
        ):
            cur = conn.execute(f"SELECT COUNT(*) FROM {nama_tabel}")
            jumlah_baris[nama_tabel] = int(cur.fetchone()[0])

        conn.commit()

    return jumlah_baris
