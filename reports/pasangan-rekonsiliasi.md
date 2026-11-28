# Tabel nasional dan pasangan rekonsiliasi

Dihasilkan `python pipeline.py` (`src/gold/nasional.py`) dari Silver dan `src/konfigurasi.py`. Selisih dihitung di Sprint 2; Sprint 1 memastikan setiap pasangan memang sebanding dan mencatat tahun yang beririsan.

Tabel nasional (periode x seri, rincian total, tampilan lebar): `reports/tabel-nasional.csv`. Kolom BPS hanya terisi pada tahun survei; itu bentuk datanya, tidak diisi.

## Ringkasan pasangan

| id | seri_utama | pembanding | jenis | periode_beririsan | tahun | dugaan_kategori |
|---|---|---|---|---|---|---|
| P1 | var1161 | SDG_0821_NOC_RT [total], SDG_B821_NOC_RT [total] | selisih | 0 | - | metode (PDB riil BPS vs estimasi model ILO); proyeksi ILO dikeluarkan |
| P2 | var1161 | SL.GDP.PCAP.EM.KD [total] | selisih | 0 | - | WDI tingkat (USD PPP 2021), bukan laju; laju WDI dihitung di Gold sebelum dibandingkan |
| P3 | var1214 | NV.IND.MANF.ZS [total] | selisih | 0 | - | dasar harga belum diketahui di kedua sumber; dicek di Sprint 2 |
| P4 | var2755 | SDG_0922_NOC_RT [total] | selisih | 0 | - | metode (olahan Sakernas yang sama) |

## Rincian per pasangan

### P1: Laju produktivitas: BPS vs ILO (dua basis harga)
- Seri utama: `var1161` (rincian `total`)
- Pembanding: `SDG_0821_NOC_RT` (rincian `total`), `SDG_B821_NOC_RT` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: -
- Dugaan kategori selisih (diuji di Sprint 2): metode (PDB riil BPS vs estimasi model ILO); proyeksi ILO dikeluarkan

Pertanyaan keterbandingan dan jawabannya:

1. **Beda 0821 dan B821?** Basis harga USD konstan 2015 vs PPP 2021 (nama DSD); lajunya sama di semua tahun.
2. **Tahun mana yang sah?** 2026-2027 proyeksi (PROYEKSI); 2024-2025 BPS angka sementara.

### P2: Laju produktivitas BPS vs WDI tingkat PDB per pekerja
- Seri utama: `var1161` (rincian `total`)
- Pembanding: `SL.GDP.PCAP.EM.KD` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: -
- Dugaan kategori selisih (diuji di Sprint 2): WDI tingkat (USD PPP 2021), bukan laju; laju WDI dihitung di Gold sebelum dibandingkan

Pertanyaan keterbandingan dan jawabannya:

1. **Bisa langsung dibandingkan?** Tidak: hitung (t / t-1 - 1) x 100 dari WDI dulu.

### P3: Nilai tambah manufaktur terhadap PDB: BPS vs WDI
- Seri utama: `var1214` (rincian `total`)
- Pembanding: `NV.IND.MANF.ZS` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: -
- Dugaan kategori selisih (diuji di Sprint 2): dasar harga belum diketahui di kedua sumber; dicek di Sprint 2

Pertanyaan keterbandingan dan jawabannya:

1. **Harga konstan atau berlaku?** Tidak disebut di judul BPS maupun name/sourceNote WDI.

### P4: Tenaga kerja manufaktur: BPS vs ILO
- Seri utama: `var2755` (rincian `total`)
- Pembanding: `SDG_0922_NOC_RT` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: -
- Dugaan kategori selisih (diuji di Sprint 2): metode (olahan Sakernas yang sama)

Pertanyaan keterbandingan dan jawabannya:

1. **Sumber sama?** Keduanya Sakernas (var.note; SOURCE LFS).
