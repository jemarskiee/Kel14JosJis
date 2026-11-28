

CREATE TABLE IF NOT EXISTS silver_indikator (
    id_baris INTEGER PRIMARY KEY AUTOINCREMENT,
    seri_kode TEXT NOT NULL,
    wilayah_kode TEXT NOT NULL,
    nama_wilayah TEXT NOT NULL,
    periode INTEGER NOT NULL,
    jenis_periode TEXT NOT NULL,
    rincian TEXT NOT NULL,
    satuan TEXT,
    nilai REAL,
    sumber TEXT NOT NULL,
    proyeksi TEXT,
    _berkas_raw TEXT,
    _sha256_raw TEXT,
    UNIQUE (sumber, seri_kode, wilayah_kode, periode, jenis_periode, rincian)
);

CREATE TABLE IF NOT EXISTS gold_panel_provinsi (
    id_baris INTEGER PRIMARY KEY AUTOINCREMENT,
    sumber TEXT NOT NULL,
    indikator TEXT NOT NULL,
    seri_kode TEXT NOT NULL,
    rincian TEXT NOT NULL,
    wilayah_kode TEXT NOT NULL,
    nama_wilayah TEXT NOT NULL,
    periode INTEGER NOT NULL,
    jenis_periode TEXT NOT NULL,
    nilai REAL,
    satuan TEXT,
    sdg_kode TEXT,
    batas_bawah REAL,
    batas_atas REAL,
    status_sel TEXT,
    penanda TEXT,
    rujukan_tahun TEXT,
    proyeksi TEXT,
    _berkas_raw TEXT,
    _sha256_raw TEXT
);

CREATE TABLE IF NOT EXISTS gold_tabel_nasional (
    id_baris INTEGER PRIMARY KEY AUTOINCREMENT,
    periode INTEGER NOT NULL,
    seri_kode TEXT NOT NULL,
    jenis_seri TEXT NOT NULL,
    seri_utama TEXT,
    wilayah TEXT NOT NULL,
    nilai REAL,
    sumber TEXT NOT NULL,
    satuan TEXT,
    _berkas_raw TEXT,
    _sha256_raw TEXT
);

CREATE TABLE IF NOT EXISTS gold_rekonsiliasi (
    id_baris INTEGER PRIMARY KEY AUTOINCREMENT,
    periode INTEGER NOT NULL,
    seri_utama TEXT NOT NULL,
    seri_pembanding TEXT NOT NULL,
    wilayah TEXT NOT NULL,
    nilai_utama REAL,
    nilai_pembanding REAL,
    selisih REAL,
    kategori_selisih TEXT
);
