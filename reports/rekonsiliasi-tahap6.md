# Rekonsiliasi Data – Tahap 6

## 1. Daftar Pasangan Rekonsiliasi

| No | Seri utama | Seri pembanding | Metode |
|---|---|---|---|
| 1 | var1161 | ILO SDG_0821_NOC_RT dan SDG_B821_NOC_RT | Membandingkan nilai dan memahami perbedaan basis melalui metadata indikator |
| 2 | var1161 | WDI SL.GDP.PCAP.EM.KD | Mengubah data level WDI menjadi pertumbuhan tahunan sebelum dibandingkan |
| 3 | var1214 | WDI NV.IND.MANF.ZS | Membandingkan persentase manufaktur terhadap PDB dan memeriksa basis harga |
| 4 | var2755 | ILO SDG_0922_NOC_RT | Membandingkan nilai pada periode yang beririsan |

## 2. Catatan Keterbandingan

### var1161 dengan ILO SDG_0821_NOC_RT dan SDG_B821_NOC_RT
Kedua seri ILO memiliki nilai yang identik pada data yang digunakan. Perbandingan dilakukan pada 8 periode yang beririsan (2018–2025). Perbedaan basis atau definisi indikator perlu mengacu pada metadata masing-masing seri.

### var1161 dengan WDI SL.GDP.PCAP.EM.KD
Data WDI berbentuk nilai level produktivitas, sehingga diubah menjadi pertumbuhan tahunan dengan rumus:

`((nilai_t / nilai_t-1) - 1) * 100`

Perbandingan mencakup 15 periode (2011–2025). Tren pada beberapa tahun terlihat searah, tetapi terdapat selisih pada sejumlah periode. Kedua seri tidak dianggap identik karena perbedaan sumber dan definisi.

### var1214 dengan WDI NV.IND.MANF.ZS
Perbandingan mencakup 14 periode (2010–2023). Kedua seri menunjukkan tren penurunan, tetapi nilai var1214 cenderung lebih tinggi dibanding WDI. Basis harga (konstan atau berlaku) belum dapat dipastikan dari metadata yang tersedia.

### var2755 dengan ILO SDG_0922_NOC_RT
Perbandingan mencakup 6 periode (2018–2023). Nilainya relatif berdekatan dengan selisih terbesar 0,527 pada 2019. Perbedaan tetap dimungkinkan karena sumber dan metode penghitungan indikator.

## 3. Ringkasan Periode Beririsan

| Pasangan | Periode beririsan |
|---|---:|
| var1161 – ILO (satu pasangan logis) | 8 |
| var1161 – WDI (pertumbuhan) | 15 |
| var1214 – WDI | 14 |
| var2755 – ILO | 6 |
| **Total** | **43** |

Catatan: Dua seri ILO pada pasangan pertama memiliki nilai identik dalam snapshot, sehingga dihitung sebagai satu pasangan logis.

## 4. Sumber Data
Data pembanding berasal dari ekstraksi ILOSTAT dan World Development Indicators (WDI), snapshot 20 Oktober 2026.
