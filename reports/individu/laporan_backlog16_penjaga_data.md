# Laporan Backlog 16 – Penjaga Data

**Penanggung jawab:** Salsabila Nazwa Putri  
**NIM:** 124450002  
**Sprint:** Sprint 1

## 1. Tujuan

Memastikan data mentah pada seluruh perangkat anggota konsisten dengan `MANIFEST.csv`, pemeriksaan SHA-256 berhasil, dan nilai `data_hash` pada setiap `results/<NIM>/metrics.json` sama.

## 2. Rekap pemeriksaan anggota

Isi tabel berikut berdasarkan konfirmasi dan bukti yang dikirim masing-masing anggota.

| No. | NIM | Nama | Pemeriksaan SHA-256 | `data_hash` | Keterangan |
|---:|---|---|---|---|---|
| 1 | 124450002 | Salsabila Nazwa Putri | Lolos | a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4 | Hash pembanding |
| 2 | 124450034 | Suci Aulia | Lolos | a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4 | Sesuai |
| 3 | 124450077 | Indah Khairunnisa | Lolos | a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4 | Sesuai |
| 4 | 124450024 | Yollanda Agustina | Lolos | a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4 | Sesuai |
| 5 | 124450111 | Jeremi Marolop Partogi Situmorang | Lolos | a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4 | Sesuai |

## 3. Pemeriksaan konsistensi `data_hash`

Hash pembanding:

```text
a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4
```

Kriteria:

- Nilai `data_hash` setiap anggota harus sama persis dengan hash pembanding.
- Setiap anggota telah melaporkan pemeriksaan SHA-256 berhasil.
- Anggota yang belum mengirim bukti atau hash belum dinyatakan tervalidasi.

**Hasil akhir:** Semua sama

## 4. Pemeriksaan `data/raw/` dan Git

Pemeriksaan dilakukan pada repository dengan perintah:

```bash
git status --short data/raw/
git ls-files data/raw/
```

Catat hasil pemeriksaan:

- Perubahan pada `data/raw/`: Tidak ada
- File `data/raw/` yang terlacak Git: Tidak ada

Berdasarkan hasil pemeriksaan, tidak ditemukan perubahan pada file `data/raw/` yang terdeteksi Git dan tidak ada file dalam direktori tersebut yang terlacak oleh Git. Dengan demikian, ketentuan pengelolaan `data/raw/` telah terpenuhi.

## 5. Kesimpulan

Backlog 16 – Penjaga Data telah diselesaikan. Seluruh 5 anggota kelompok telah melaporkan pemeriksaan SHA-256 dengan status lolos dan memiliki nilai `data_hash` yang sama. Pemeriksaan Git juga menunjukkan tidak ada perubahan yang terdeteksi pada `data/raw/` dan tidak ada file dalam direktori tersebut yang terlacak oleh Git.
