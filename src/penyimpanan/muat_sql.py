from pathlib import Path
import sqlite3
import pandas as pd


def _siapkan_df_untuk_tabel(conn: sqlite3.Connection, nama_tabel: str, df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None
    info = conn.execute(f"PRAGMA table_info({nama_tabel})").fetchall()
    kolom_tabel = [row[1] for row in info]
    kolom_tersedia = [k for k in kolom_tabel if k in df.columns]
    df_bersih = df[kolom_tersedia].copy()

    # Pastikan kolom NOT NULL yang bertipe teks tidak berisi None/NaN agar insert SQL tidak gagal
    for row in info:
        _, nama_kol, tipe_kol, not_null, _, _ = row
        if nama_kol in df_bersih.columns and not_null:
            if "INT" in tipe_kol.upper():
                df_bersih[nama_kol] = pd.to_numeric(df_bersih[nama_kol], errors="coerce").fillna(0).astype(int)
            else:
                df_bersih[nama_kol] = df_bersih[nama_kol].fillna("").astype(str)

    return df_bersih


def muat_ke_sqlite(
    db_path: str = "data/sql/kasus14.db",
    ddl_path: str = "sql/schema_kasus14.sql",
    silver_df: pd.DataFrame | None = None,
    gold_panel_df: pd.DataFrame | None = None,
    gold_nasional_df: pd.DataFrame | None = None,
    rekonsiliasi_df: pd.DataFrame | None = None,
    silver_parquet: str = "data/silver/silver.parquet",
    gold_panel_parquet: str = "data/gold/panel.parquet",
    gold_nasional_parquet: str = "data/gold/tabel_nasional_gold.parquet",
) -> dict[str, tuple[int, int]]:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    if silver_df is None and Path(silver_parquet).exists():
        silver_df = pd.read_parquet(silver_parquet)
    if gold_panel_df is None and Path(gold_panel_parquet).exists():
        gold_panel_df = pd.read_parquet(gold_panel_parquet)
    if gold_nasional_df is None and Path(gold_nasional_parquet).exists():
        gold_nasional_df = pd.read_parquet(gold_nasional_parquet)

    conn = sqlite3.connect(db_path)
    try:
        ddl_sql = Path(ddl_path).read_text(encoding="utf-8")
        conn.executescript(ddl_sql)

        tabel_map = [
            ("silver_indikator", silver_df),
            ("gold_panel_provinsi", gold_panel_df),
            ("gold_tabel_nasional", gold_nasional_df),
            ("gold_rekonsiliasi", rekonsiliasi_df),
        ]

        for nama_tabel, df in tabel_map:
            df_siap = _siapkan_df_untuk_tabel(conn, nama_tabel, df)
            if df_siap is not None and not df_siap.empty:
                conn.execute(f"DELETE FROM {nama_tabel}")
                df_siap.to_sql(nama_tabel, conn, if_exists="append", index=False)

        conn.commit()

        ringkasan: dict[str, tuple[int, int]] = {}
        if silver_df is not None:
            cnt_sql = conn.execute("SELECT COUNT(*) FROM silver_indikator").fetchone()[0]
            ringkasan["silver_indikator"] = (cnt_sql, len(silver_df))
        if gold_panel_df is not None:
            cnt_sql = conn.execute("SELECT COUNT(*) FROM gold_panel_provinsi").fetchone()[0]
            ringkasan["gold_panel_provinsi"] = (cnt_sql, len(gold_panel_df))
        if gold_nasional_df is not None:
            cnt_sql = conn.execute("SELECT COUNT(*) FROM gold_tabel_nasional").fetchone()[0]
            ringkasan["gold_tabel_nasional"] = (cnt_sql, len(gold_nasional_df))

        return ringkasan
    finally:
        conn.close()


if __name__ == "__main__":
    hasil = muat_ke_sqlite()
    for tabel, (cnt_sql, cnt_pq) in hasil.items():
        print(f"{tabel}: SQL={cnt_sql}, Parquet={cnt_pq}, sama={cnt_sql == cnt_pq}")
