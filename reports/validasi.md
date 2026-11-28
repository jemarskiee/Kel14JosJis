# Validasi Silver (otomatis)

Baris Silver: 1,621  
Aturan: 13, lolos: 13, gagal: 0

| Aturan | Hasil | Keterangan |
|---|---|---|
| A1 sebelas kolom wajib ada | LOLOS | 11/11 kolom |
| B1 kunci unik (sumber+seri+wilayah+periode+rincian+berkas) | LOLOS | 1,621 baris unik |
| B2 tidak ada sel kosong di kolom wajib | LOLOS |  |
| B3 nilai numerik dan berhingga | LOLOS |  |
| C1 satu satuan per (seri_kode, rincian) | LOLOS | 4 pasangan seri-rincian |
| C2 satuan sudah ditetapkan (tidak kosong / tidak_ada) | LOLOS |  |
| D1 proporsi (satuan persen, bukan laju) di rentang 0-100 [782 baris diperiksa] | LOLOS |  |
| D2 laju pertumbuhan dalam (-50, 50) [524 baris diperiksa] | LOLOS |  |
| D3 tingkat (rupiah/dolar PPP) > 0 [315 baris diperiksa] | LOLOS |  |
| E1 wilayah_kode ada di 38 provinsi + 9999 | LOLOS |  |
| E2 format periode (2020 / 2020-S1 / 2020-Q3 / 2020-07) | LOLOS |  |
| F1 baris ILO > 2026 ditandai proyeksi=True | LOLOS | 0 baris proyeksi ditandai |
| F2 hanya baris ILO yang bertanda proyeksi | LOLOS |  |
