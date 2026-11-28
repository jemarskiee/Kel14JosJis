# Validasi Silver dan Gold (otomatis)

Baris Silver: 1,621  
Aturan: 32, lolos: 30, gagal: 2

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
| G0 kolom panel yang diperlukan ada | LOLOS | 1,748 sel, 19 kolom |
| G1 kunci panel unik (indikator+wilayah+periode+rincian) | LOLOS | 1,748 sel unik |
| G2 satu satuan per indikator | LOLOS | 4 indikator |
| G3 setiap sel terisi berpasangan satu-satu di Silver [1,575 sel diperiksa] | LOLOS | 1,575 sel berpasangan |
| G4 nilai dan sidik berkas Gold sama dengan Silver | LOLOS | 1,575 sel cocok |
| G5 status_sel sah dan nilai ada hanya pada sel terisi | LOLOS | {'terisi': 1575, 'belum_berdiri': 137, 'kosong': 24, 'belum_terbit': 12} |
| G6 nilai terisi dalam rentang wajar per satuan | LOLOS | 1,575 sel diperiksa |
| G7 wilayah panel = 38 provinsi (tanpa 9999) | LOLOS | 38 wilayah unik |
| N1 kunci tabel nasional unik (seri_kode+wilayah+periode) | LOLOS | 204 baris unik |
| N2 satuan terisi dan satu per seri_kode | GAGAL | 78 baris satuan kosong pada seri ['NV.IND.MANF.ZS', 'SL.GDP.PCAP.EM.KD']; satuan ganda pada [] |
| N3 nilai tabel nasional dalam rentang wajar per seri_kode | LOLOS | 204 baris diperiksa |
| N4 baris ILO setelah 2026 ditandai proyeksi, dan hanya ILO | GAGAL | kolom proyeksi tidak ada di tabel nasional; 2 baris ILO setelah 2026 belum ditandai |
| N5 baris BPS tabel nasional sama dengan Silver (kode 9999: nilai dan berkas asal) | LOLOS | 46 baris BPS cocok dengan Silver |
| R0 berkas rekonsiliasi ada dengan kolom wajib (periode, nilai utama, nilai pembanding, selisih, kategori) | LOLOS | 160 baris, 5 pasangan |
| R1 setiap baris berselisih punya kategori sah (lima kategori panduan 5.7) | LOLOS | 65 baris berselisih berkategori sah |
| R2 selisih sama dengan nilai utama dikurangi nilai pembanding (toleransi 0,01) | LOLOS | 65 selisih cocok |
| R3 baris ILO setelah 2026 tidak ikut rekonsiliasi (tanpa selisih) | LOLOS | 2 baris ILO setelah 2026, tanpa selisih |
| R4 kelima pasangan bagian 3 panduan ada dan berselisih | LOLOS | 5 pasangan lengkap |
| R5 pembanding WDI untuk var1161 berupa laju (-50 sampai 50), bukan tingkat | LOLOS | 15 baris berselisih diperiksa |
