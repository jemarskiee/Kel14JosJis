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
| 1 | 124450002 | Salsabila Nazwa Putri | Lolos* | `a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4` | Hash pembanding |
| 2 | [NIM] | [Nama] | [Lolos/Belum] | [Tempel hash lengkap] | [Sesuai/Belum diperiksa] |
| 3 | [NIM] | [Nama] | [Lolos/Belum] | [Tempel hash lengkap] | [Sesuai/Belum diperiksa] |
| 4 | [NIM] | [Nama] | [Lolos/Belum] | [Tempel hash lengkap] | [Sesuai/Belum diperiksa] |

\*Status SHA-256 pada baris penanggung jawab diisi berdasarkan hasil pemeriksaan yang benar-benar dijalankan.

## 3. Pemeriksaan konsistensi `data_hash`

Hash pembanding:

```text
a3e02f7dc596e0eb3eb31def465255c7452c62689cab0f05fac7baf1c86859d4
```

Kriteria:
- Nilai `data_hash` setiap anggota harus sama persis dengan hash pembanding.
- Setiap anggota telah melaporkan pemeriksaan SHA-256 berhasil.
- Anggota yang belum mengirim bukti atau hash belum dinyatakan tervalidasi.

**Hasil akhir:** [Isi setelah seluruh anggota diperiksa: Semua sama / Masih terdapat perbedaan]

## 4. Pemeriksaan `data/raw/` dan Git

Pemeriksaan dilakukan pada repository dengan perintah:

```bash
git status --short data/raw/
git ls-files data/raw/
```

Catat hasil pemeriksaan:
- Perubahan pada `data/raw/`: [Tidak ada / Ada, jelaskan]
- File `data/raw/` yang terlacak Git: [Tidak ada / Ada, jelaskan]

Data pada `data/raw/` tidak boleh diubah secara manual maupun dimasukkan ke commit.

## 5. Kesimpulan

[Isi setelah seluruh bukti terkumpul. Nyatakan Backlog 16 selesai hanya jika seluruh anggota melaporkan SHA-256 lolos, semua `data_hash` sama, dan ketentuan `data/raw/` terpenuhi.]
