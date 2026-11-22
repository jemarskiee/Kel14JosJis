# Data dictionary — Kelompok 14

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## data/silver/silver.parquet

Dibuat oleh `python pipeline.py` (tahap ekstraksi lalu silver). Angka di bawah dihitung dari
`silver.parquet` Silver pertama (22 Nov 2026) dengan `profil_kamus.py`.

- Bentuk: 1.623 baris x 11 kolom. Seluruhnya kolom wajib; tidak ada kolom tambahan.
- Cakupan: hanya sumber BPS, empat seri (var1161, var1214, var1344, var2755). WDI dan ILO belum masuk.
- Jumlah kosong: 0 di semua kolom.
- Kunci unik (README): sumber + seri_kode + wilayah_kode + periode + rincian + berkas.
- Urutan kolom fisik: seri_kode, wilayah_kode, nama_wilayah, periode, rincian, satuan, nilai, sumber,
  _berkas_raw, _sha256_raw, jenis_periode.
- Validasi: `src/validasi/aturan_silver.py`, laporan `reports/validasi.md`.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak (0 kosong) | sah: bps, bnpb, wdi, who_gho, ilostat; di Silver sekarang hanya bps (1.623 baris) | nama folder data/raw | Aturan A1, B1, B2 |
| seri_kode | string | BPS: varNNNN | tidak (0 kosong) | var1161 (526 baris), var1214 (494), var1344 (315), var2755 (288) | tahap ekstraksi | Aturan A1, B1, B2. Seri ILO dan WDI akan memakai nama seri/kode indikator (K-003, K-004) |
| wilayah_kode | int64 | kode BPS x 100 | tidak (0 kosong) | 40 nilai: 9999 (Indonesia), 38 kode provinsi 1100–9700 (daftar di bawah), dan 1 (tidak sah, 2 baris var1161) | pemetaan wilayah (K-028), dipaksa int64 (K-019) | Aturan B1, E1. E1 gagal hanya karena kode 1 (temuan 1). Batas atas di template (9600) menjadi 9700 |
| nama_wilayah | string | huruf kapital seperti BPS | tidak (0 kosong) | pasangan kode–nama di daftar bawah; kode 1 bernama "Wilayah 1" | kamus kode BPS; yang kosong diisi (K-019) | Pencocokan memakai kode, bukan nama (K-028) |
| periode | string | YYYY (tahun) | tidak (0 kosong) | 2010–2025 (16 tahun berbeda); per seri di tabel pemetaan | tahap ekstraksi | Aturan E2 |
| jenis_periode | string | tahun | tidak (0 kosong) | hanya "tahun" (1.623 baris) | dibuat di Silver (K-021) | Semua seri BPS di Silver bersifat tahunan |
| rincian | string | total | tidak (0 kosong) | hanya "total" (1.623 baris) | tahap ekstraksi | var1214 diperlakukan satu seri (K-018; temuan 5). Aturan B1, C1 |
| nilai | float64 | menurut kolom satuan | tidak (0 kosong) | per seri di tabel pemetaan | `nilai_num` di-rename menjadi `nilai` (K-023) | Aturan B3, D1, D2, D3. Langkah 3 Silver membuang nilai di luar batas mustahil sebelum validasi (temuan 4) |
| satuan | string | Persen; Rupiah/Tenaga Kerja | tidak (0 kosong) | dua nilai: Persen (1.308 baris), Rupiah/Tenaga Kerja (315 baris) | kamus pemetaan, karena BPS tidak menyertakan satuan (K-020) | Aturan C1, C2. Satu satuan per seri (lihat pemetaan). Penulisan belum seragam antar-log (temuan 5) |
| _berkas_raw | string | jalur relatif terhadap data/raw/ | tidak (0 kosong) | 4 jalur, semuanya JSON (tabel pemetaan) | direkonstruksi dari kolom bantu `berkas` (K-022) | Lineage |
| _sha256_raw | string | sha256 heksadesimal, 64 karakter | tidak (0 kosong) | 4 nilai unik, satu per berkas; panjang 64 di semua baris | lookup dari data/raw/MANIFEST.csv (K-022) | Lineage |

### Pemetaan seri, rincian, dan satuan

Rincian: semua baris Silver bernilai `total` (kamus rincian hanya satu entri). Kode SDG dan satuan katalog
berasal dari panduan kelompok, yang menyatakan bahwa itu belum tentu benar; kolom "Satuan di Silver"
adalah isi Silver sebenarnya.

| seri_kode | _berkas_raw | Butir SDG | Satuan katalog | Satuan di Silver | n | periode | nilai min | nilai maks | n wilayah |
|---|---|---|---|---|---|---|---|---|---|
| var1161 | bps/2026-10-17/json/sdg8_produktivitas.json | 8.2.1 | tidak_ada | Persen | 526 | 2011–2025 | -22,96 | 31,79 | 40 |
| var1214 | bps/2026-10-20/json/sdg9_9_2_1_v1214.json | 9.2.1 | tidak_ada | Persen | 494 | 2010–2023 | 0,24 | 44,51 | 39 |
| var1344 | bps/2026-10-20/json/sdg2_2_3_1_a_v1344.json | 2.3.1 (K-002: 2.3.1(a)) | rupiah_per_tenaga_kerja | Rupiah/Tenaga Kerja | 315 | 2015–2023 | 17.412.788,26 | sekitar 2,35 x 10^8 (2,353509e+08) | 35 |
| var2755 | bps/2026-10-20/json/sdg9_9_2_2_v2755.json | 9.2.2 | persen | Persen | 288 | 2018–2025 | 0,08 | 25,77 | 39 |

Catatan: "n wilayah" var1161 sudah termasuk 9999 dan kode 1. Rentang periode keempat seri sama dengan periode di katalog.
Hanya empat berkas JSON yang masuk Silver. Berkas CSV dan snapshot 2026-10-17 var2755 tidak ada di Silver
(K-024, K-025; temuan 6).

Seri sumber lain (belum ada di Silver; dicatat dari log supaya siap saat masuk):

| seri_kode | Sumber | Butir SDG | Satuan menurut log |
|---|---|---|---|
| SL.GDP.PCAP.EM.KD | wdi | 8.2.1 (K-004) | usd_ppp_2021 |
| NV.IND.MANF.ZS | wdi | 9.2.1 (K-005) | persen |
| SDG_0821_NOC_RT | ilostat | 8.2.1 (katalog) | persen_per_tahun (K-003) |
| SDG_B821_NOC_RT | ilostat | 8.2.1 (katalog) | persen_per_tahun (K-003) |
| SDG_0922_NOC_RT | ilostat | 9.2.2 (katalog) | diambil dari DSD (K-008); nilai belum dicatat di sini |

### Daftar kode wilayah di Silver

Indonesia: 9999 INDONESIA. Kode tidak sah: 1 (Wilayah 1; 2 baris var1161, 2015 dan 2016).
Provinsi (38): 1100 ACEH; 1200 SUMATERA UTARA; 1300 SUMATERA BARAT; 1400 RIAU; 1500 JAMBI;
1600 SUMATERA SELATAN; 1700 BENGKULU; 1800 LAMPUNG; 1900 KEP. BANGKA BELITUNG; 2100 KEP. RIAU;
3100 DKI JAKARTA; 3200 JAWA BARAT; 3300 JAWA TENGAH; 3400 DI YOGYAKARTA; 3500 JAWA TIMUR; 3600 BANTEN;
5100 BALI; 5200 NUSA TENGGARA BARAT; 5300 NUSA TENGGARA TIMUR; 6100 KALIMANTAN BARAT;
6200 KALIMANTAN TENGAH; 6300 KALIMANTAN SELATAN; 6400 KALIMANTAN TIMUR; 6500 KALIMANTAN UTARA;
7100 SULAWESI UTARA; 7200 SULAWESI TENGAH; 7300 SULAWESI SELATAN; 7400 SULAWESI TENGGARA;
7500 GORONTALO; 7600 SULAWESI BARAT; 8100 MALUKU; 8200 MALUKU UTARA; 9100 PAPUA BARAT;
9200 PAPUA BARAT DAYA; 9400 PAPUA; 9500 PAPUA SELATAN; 9600 PAPUA TENGAH; 9700 PAPUA PEGUNUNGAN.
(9300 tidak ada.)

### Aturan validasi (ringkas)

A1 kolom wajib ada; B1 kunci unik; B2 tidak ada sel kosong; B3 nilai numerik; C1 satu satuan per seri+rincian;
C2 satuan tidak kosong/tidak_ada; D1 persen 0-100 kecuali seri laju; D2 laju dalam -50..50 (batas kewajaran
buatan sendiri, bukan standar sumber; K-029); D3 tingkat lebih dari 0; E1 wilayah_kode valid; E2 format
periode; F1 baris ILO setelah 2026 wajib bertanda kolom boolean `proyeksi`.
Hasil Silver pertama: 10 dari 12 lolos (E1 dan F1 gagal).

### Catatan dan temuan terbuka

1. **Kode wilayah `1`** (2 baris var1161: 2015 nilai 4,62 dan 2016 nilai 1,83; hanya JSON 17 Okt, tanpa
   label). K-017 mengeluarkannya dari grid tetapi tidak menghapus baris, jadi masih ada di Silver dan E1
   gagal. Pemilik: 124450034.
2. **WDI dan ILO belum masuk Silver** (12 tabel dilewati). Aturan F1 belum teruji; butuh kolom boolean
   `proyeksi`.
3. **Reproduksi**: `silver.parquet` hasil pipeline di laptop terdeteksi berbeda dari yang di-commit; isinya
   belum dibandingkan.
4. **Pembuangan nilai di luar batas mustahil** di langkah 3 Silver: jumlah baris dan log pencatatnya belum
   diketahui.
5. **var1214 dan satuan.** K-018 memperlakukan var1214 sebagai satu seri. Bukti di berkas mentah: judul tabel di
   `manifest_asal.json` (snapshot 2026-10-20) adalah "Proporsi Nilai Tambah Sektor Industri Manufaktur Terhadap
   PDB" (satu ukuran); `turvar_id` seluruhnya 0 dan `turvar` "Tidak ada" pada 494 baris; jumlah baris di manifest
   sama dengan Silver (494); nilainya 0,24–44,51, satu per wilayah-tahun. Panduan kelompok (bagian 4.2 dan 6)
   menyebut var1214 memuat dua ukuran dalam satu judul yang harus dipisah; hal itu tidak terlihat pada judul
   maupun data. Menunggu konfirmasi pembimbing (Ardika Satria).
   Satuan di manifest kosong; "Persen" di Silver berasal dari K-002 (alasan di log hanya mencatat verifikasi nama
   berkas), jadi belum bersumber dari metadata eksplisit.
   Satuan: Silver memakai "Persen" untuk var1161, padahal K-007 menetapkan `persen_per_tahun` (laju).
   Penulisan satuan juga berbeda antar-log: K-020 "Persen", K-002/K-005 "persen", K-003/K-007 "persen_per_tahun".
6. **Snapshot dan format.** Silver hanya memuat empat berkas JSON (var1161 dari snapshot 17 Okt; tiga seri
   lain dari 20 Okt). Snapshot 17 Okt var2755 dan semua berkas CSV tidak masuk Silver (K-024, K-025),
   sedangkan Langkah Kerja umum bagian 2 menyebut kedua snapshot disimpan di Silver lalu dipilih di Gold.
   Menunggu konfirmasi pemilik K-024 (124450034) dan pembimbing.

## data/gold/<tabel>.parquet

Belum ada; Gold dikerjakan di Sprint 2.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|