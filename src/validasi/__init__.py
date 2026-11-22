"""Tahap 8 — Validasi dan dokumentasi (pertemuan XIV–XV). Milik tim.

Tulis skema validasi Silver dan Gold (pandera atau Great Expectations): rentang nilai per satuan,
kelengkapan wilayah, keunikan kunci, konsistensi provinsi vs nasional bila relevan. Laporan
validasi ditulis ke reports/validasi.md. Data dictionary di docs/data-dictionary.md.
"""

from .aturan_silver import jalankan

__all__ = ["jalankan"]