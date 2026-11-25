"""Keputusan wrangling Kasus 14 - Produktivitas dan industri."""

KASUS = 14
SLUG = "produktivitas-industri"
JUDUL = "Produktivitas dan industri"
FORMAT_BPS = "json"
LAJU = "persen_per_tahun"

SERI = {
    "var1161": dict(
        sumber="bps", tingkat="provinsi", nama="Laju pertumbuhan PDB riil per tenaga kerja (per orang bekerja) per tahun",
        satuan=LAJU, katalog_satuan="tidak_ada", bukti_satuan="judul 'Laju Pertumbuhan ... Per Tahun'; var.unit kosong; nilai bisa negatif",
        sdg="8.2.1", katalog_sdg="8.2.1", bukti_sdg="laju pertumbuhan PDB riil per orang bekerja = indikator 8.2.1",
        cakupan="BPS diolah; 2011-2025; 2024 angka sementara, 2025 sangat sementara; 2024 provinsi Papua baru dihitung pada provinsi induk (var.note)", koreksi="satuan tidak_ada -> persen_per_tahun",
    ),
    "var1344": dict(
        sumber="bps", tingkat="provinsi", nama="Nilai tambah pertanian dibagi jumlah tenaga kerja sektor pertanian",
        satuan="rupiah_per_tenaga_kerja", katalog_satuan="rupiah_per_tenaga_kerja", bukti_satuan="var.unit: 'Rupiah/Tenaga Kerja'",
        sdg="2.3.1(a)", katalog_sdg="2.3.1", bukti_sdg="nama berkas sdg2_2_3_1_a_v1344: butir nasional (a)",
        cakupan="2015-2023; 2022 angka sementara, 2023 sangat sementara", koreksi="kode SDG 2.3.1 -> 2.3.1(a)",
    ),
    "var1214": dict(
        sumber="bps", tingkat="provinsi", nama="Proporsi nilai tambah sektor industri manufaktur terhadap PDB",
        satuan="persen", katalog_satuan="tidak_ada", bukti_satuan="judul 'Proporsi ... Terhadap PDB'; var.unit kosong; nilai 0-50",
        sdg="9.2.1", katalog_sdg="9.2.1", bukti_sdg="proporsi nilai tambah manufaktur = bagian pertama indikator 9.2.1",
        cakupan="satu ukuran (proporsi terhadap PDB; bagian per kapita 9.2.1 tidak ada); dasar harga tidak disebut; 2010-2023",
        koreksi="satuan tidak_ada -> persen",
    ),
    "var2755": dict(
        sumber="bps", tingkat="provinsi", nama="Proporsi tenaga kerja pada sektor industri manufaktur",
        satuan="persen", katalog_satuan="persen", bukti_satuan="var.unit: 'Persen'",
        sdg="9.2.2", katalog_sdg="9.2.2", bukti_sdg="var.label diawali '9.2.2*'", cakupan="Sakernas; 2018-2025; ada di dua snapshot",
    ),
    "SL.GDP.PCAP.EM.KD": dict(
        sumber="wdi", tingkat="nasional", nama="GDP per person employed (constant 2021 PPP $)",
        satuan="usd_ppp_2021", katalog_satuan="-", bukti_satuan="name: '(constant 2021 PPP $)'",
        sdg="8.2.1", katalog_sdg="-", bukti_sdg="tercantum di metadata/sumber46_indikator.json; tingkat, bukan laju",
        cakupan="tingkat PDB per orang bekerja; laju dihitung di Gold", koreksi="kode SDG kosong -> 8.2.1",
    ),
    "NV.IND.MANF.ZS": dict(
        sumber="wdi", tingkat="nasional", nama="Manufacturing, value added (% of GDP)",
        satuan="persen", katalog_satuan="-", bukti_satuan="name: '(% of GDP)'",
        sdg="9.2.1", katalog_sdg="-", bukti_sdg="tercantum di metadata/sumber46_indikator.json",
        cakupan="ISIC Rev.3 C; dasar harga tidak disebut di name/sourceNote", koreksi="kode SDG kosong -> 9.2.1",
    ),
    "SDG_0821_NOC_RT": dict(
        sumber="ilostat", tingkat="nasional", nama="Annual growth rate of output per worker (GDP constant 2015 US$) (%)",
        satuan=LAJU, katalog_satuan="-", bukti_satuan="UNIT_MEASURE PT; judul DSD 'Annual growth rate'",
        sdg="8.2.1", katalog_sdg="8.2.1", bukti_sdg="nama DSD 'SDG indicator 8.2.1'",
        cakupan="ILO modelled estimates; basis USD konstan 2015; sampai 2027 (2026-2027 proyeksi)",
    ),
    "SDG_B821_NOC_RT": dict(
        sumber="ilostat", tingkat="nasional", nama="Annual growth rate of output per worker (GDP constant 2021 PPP $) (%)",
        satuan=LAJU, katalog_satuan="-", bukti_satuan="UNIT_MEASURE PT; judul DSD 'Annual growth rate'",
        sdg="8.2.1", katalog_sdg="8.2.1", bukti_sdg="nama DSD 'SDG indicator 8.2.1'",
        cakupan="ILO modelled estimates; basis PPP 2021; nilainya sama dengan SDG_0821; sampai 2027",
    ),
    "SDG_0922_NOC_RT": dict(
        sumber="ilostat", tingkat="nasional", nama="Manufacturing employment as a proportion of total employment (%)",
        satuan="persen", katalog_satuan="-", bukti_satuan="UNIT_MEASURE PT", sdg="9.2.2", katalog_sdg="9.2.2",
        bukti_sdg="nama DSD 'SDG indicator 9.2.2'", cakupan="olahan Sakernas (LFS); OBS_STATUS B = patahan",
    ),
}

RINCIAN_TOTAL_BPS = {"tidak ada"}
RINCIAN_TOTAL_WHO = {"TOTAL", ""}
RINCIAN_DIMENSI = {}
RINCIAN_NILAI = {}
KODE_RINCIAN = {}
RUJUKAN_TAHUN = {}
TIDAK_TERBIT = {}
TAHUN_TERBIT = {}

PROYEKSI = {s: {"2026", "2027"} for s in ("SDG_0821_NOC_RT", "SDG_B821_NOC_RT")}
TAHUN_UNDUH = 2026
STATUS_ILO = {"B"}
RENTANG = {"persen": (0, 100), LAJU: (-100, 100), "rupiah_per_tenaga_kerja": (0, 1e10), "usd_ppp_2021": (0, 1e6)}
ANOMALI = {"k_iqr": 1.5, "min_titik_samping": 6, "lompat_relatif": 0.20, "porsi_patahan": 0.70}

PASANGAN = [
    dict(id="P1", judul="Laju produktivitas: BPS vs ILO (dua basis harga)",
         utama="var1161", rincian_utama="total", pembanding=[("SDG_0821_NOC_RT", "total"), ("SDG_B821_NOC_RT", "total")],
         jenis="selisih", kategori="metode (PDB riil BPS vs estimasi model ILO); proyeksi ILO dikeluarkan",
         alasan_rincian="tanpa rincian",
         pertanyaan=[("Beda 0821 dan B821?", "Basis harga USD konstan 2015 vs PPP 2021 (nama DSD); lajunya sama di semua tahun."),
                     ("Tahun mana yang sah?", "2026-2027 proyeksi (PROYEKSI); 2024-2025 BPS angka sementara.")]),
    dict(id="P2", judul="Laju produktivitas BPS vs WDI tingkat PDB per pekerja",
         utama="var1161", rincian_utama="total", pembanding=[("SL.GDP.PCAP.EM.KD", "total")],
         jenis="selisih", kategori="WDI tingkat (USD PPP 2021), bukan laju; laju WDI dihitung di Gold sebelum dibandingkan",
         alasan_rincian="tanpa rincian", pertanyaan=[("Bisa langsung dibandingkan?", "Tidak: hitung (t / t-1 - 1) x 100 dari WDI dulu.")]),
    dict(id="P3", judul="Nilai tambah manufaktur terhadap PDB: BPS vs WDI",
         utama="var1214", rincian_utama="total", pembanding=[("NV.IND.MANF.ZS", "total")],
         jenis="selisih", kategori="dasar harga belum diketahui di kedua sumber; dicek di Sprint 2", alasan_rincian="tanpa rincian",
         pertanyaan=[("Harga konstan atau berlaku?", "Tidak disebut di judul BPS maupun name/sourceNote WDI.")]),
    dict(id="P4", judul="Tenaga kerja manufaktur: BPS vs ILO",
         utama="var2755", rincian_utama="total", pembanding=[("SDG_0922_NOC_RT", "total")],
         jenis="selisih", kategori="metode (olahan Sakernas yang sama)", alasan_rincian="tanpa rincian",
         pertanyaan=[("Sumber sama?", "Keduanya Sakernas (var.note; SOURCE LFS).")]),
]