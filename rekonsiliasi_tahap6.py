from pathlib import Path
import pandas as pd

KATEGORI_VALID = {
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
}


def _hitung_laju_wdi_per_periode(
    df_pembanding: pd.DataFrame,
    kali_seratus: bool = True,
) -> pd.DataFrame:
    df = df_pembanding[["periode", "nilai"]].copy()
    df["periode"] = pd.to_numeric(df["periode"], errors="coerce")
    df = df.dropna(subset=["periode"]).sort_values("periode").reset_index(drop=True)
    df["periode"] = df["periode"].astype(int)

    selisih_tahun = df["periode"].diff()
    laju = df["nilai"].pct_change(fill_method=None)
    if kali_seratus:
        laju = laju * 100.0

    df["nilai_pembanding"] = laju.where(selisih_tahun == 1)
    df["catatan_transformasi"] = (
        "Laju pertumbuhan tahunan (%) dari tingkat WDI SL.GDP.PCAP.EM.KD"
    )
    return df[["periode", "nilai_pembanding", "catatan_transformasi"]]


def rekonsiliasi_satu_pasangan(
    df_gold: pd.DataFrame,
    seri_utama_kode: str,
    seri_pembanding_kode: str,
    nama_pasangan: str,
    meta_kategori: dict[int, dict[str, str]],
    konversi_laju_wdi: bool = False,
    catatan_default: str = "",
) -> pd.DataFrame:
    sub = df_gold[df_gold["wilayah"] == "Indonesia"].copy()

    utama = sub[
        (sub["jenis_seri"] == "utama") & (sub["seri_kode"] == seri_utama_kode)
    ][["periode", "nilai", "sumber", "satuan"]].copy()
    utama["periode"] = pd.to_numeric(utama["periode"], errors="coerce").astype("Int64")
    utama = utama.dropna(subset=["periode"]).sort_values("periode")
    utama["periode"] = utama["periode"].astype(int)
    utama = utama.rename(
        columns={
            "nilai": "nilai_seri_utama",
            "sumber": "sumber_utama",
            "satuan": "satuan_utama",
        }
    )

    pembanding = sub[
        (sub["jenis_seri"] == "pembanding")
        & (sub["seri_utama"] == seri_utama_kode)
        & (sub["seri_kode"] == seri_pembanding_kode)
    ][["periode", "nilai", "sumber", "satuan"]].copy()
    pembanding["periode"] = pd.to_numeric(pembanding["periode"], errors="coerce").astype("Int64")
    pembanding = pembanding.dropna(subset=["periode"]).sort_values("periode")
    pembanding["periode"] = pembanding["periode"].astype(int)

    if konversi_laju_wdi:
        laju_df = _hitung_laju_wdi_per_periode(pembanding, kali_seratus=True)
        sumber_ref = pembanding[["periode", "sumber", "satuan"]].drop_duplicates("periode")
        kanan = pd.merge(laju_df, sumber_ref, on="periode", how="left").rename(
            columns={"sumber": "sumber_pembanding", "satuan": "satuan_pembanding"}
        )
    else:
        kanan = pembanding.rename(
            columns={
                "nilai": "nilai_pembanding",
                "sumber": "sumber_pembanding",
                "satuan": "satuan_pembanding",
            }
        )
        kanan["catatan_transformasi"] = catatan_default

    gabung = (
        pd.merge(utama, kanan, on="periode", how="outer")
        .sort_values("periode")
        .reset_index(drop=True)
    )
    gabung.insert(0, "pasangan", nama_pasangan)
    gabung["selisih"] = gabung["nilai_seri_utama"] - gabung["nilai_pembanding"]

    kategori_list: list[str | None] = []
    dugaan_list: list[str | None] = []
    bukti_list: list[str | None] = []

    for row in gabung.itertuples(index=False):
        periode_val = int(row.periode)
        berpasangan = pd.notna(row.nilai_seri_utama) and pd.notna(row.nilai_pembanding)
        info = meta_kategori.get(periode_val, {})

        dugaan_val = (info.get("dugaan") or "").strip() or None
        bukti_val = (info.get("bukti_dicari") or "").strip() or None

        if not berpasangan:
            kategori_list.append(None)
            dugaan_list.append(dugaan_val)
            bukti_list.append(bukti_val)
            continue

        kat = (info.get("kategori") or "").strip()
        if kat not in KATEGORI_VALID:
            raise ValueError(
                f"[{nama_pasangan} | periode {periode_val}] Kategori tidak valid: '{kat}'. "
                f"Wajib salah satu dari: {sorted(KATEGORI_VALID)}"
            )

        if kat == "belum terjelaskan" and (not dugaan_val or not bukti_val):
            raise ValueError(
                f"[{nama_pasangan} | periode {periode_val}] Kategori 'belum terjelaskan' "
                "wajib mengisi 'dugaan' dan 'bukti_dicari'."
            )

        kategori_list.append(kat)
        dugaan_list.append(dugaan_val)
        bukti_list.append(bukti_val)

    gabung["kategori_penjelasan"] = kategori_list
    gabung["dugaan"] = dugaan_list
    gabung["bukti_dicari"] = bukti_list

    return gabung[
        [
            "pasangan",
            "periode",
            "nilai_seri_utama",
            "nilai_pembanding",
            "selisih",
            "kategori_penjelasan",
            "dugaan",
            "bukti_dicari",
            "sumber_utama",
            "sumber_pembanding",
            "satuan_utama",
            "satuan_pembanding",
            "catatan_transformasi",
        ]
    ]


def buat_meta_otomatis_dari_pasangan(
    df_gold: pd.DataFrame,
    seri_utama_kode: str,
    seri_pembanding_kode: str,
    kategori_default: str,
    dugaan_default: str = "",
    bukti_default: str = "",
    konversi_laju_wdi: bool = False,
) -> dict[int, dict[str, str]]:
    sub = df_gold[df_gold["wilayah"] == "Indonesia"]
    th_utama = set(
        pd.to_numeric(
            sub[(sub["jenis_seri"] == "utama") & (sub["seri_kode"] == seri_utama_kode)]["periode"],
            errors="coerce",
        )
        .dropna()
        .astype(int)
    )
    kanan_df = sub[
        (sub["jenis_seri"] == "pembanding")
        & (sub["seri_utama"] == seri_utama_kode)
        & (sub["seri_kode"] == seri_pembanding_kode)
    ][["periode", "nilai"]].copy()
    kanan_df["periode"] = pd.to_numeric(kanan_df["periode"], errors="coerce")
    kanan_df = kanan_df.dropna(subset=["periode"]).sort_values("periode")
    kanan_df["periode"] = kanan_df["periode"].astype(int)

    if konversi_laju_wdi:
        laju = kanan_df["nilai"].pct_change(fill_method=None) * 100.0
        selisih_th = kanan_df["periode"].diff()
        th_pembanding = set(kanan_df.loc[selisih_th == 1, "periode"])
    else:
        th_pembanding = set(kanan_df["periode"])

    irisan_tahun = sorted(th_utama & th_pembanding)
    meta: dict[int, dict[str, str]] = {}
    for th in irisan_tahun:
        entri = {"kategori": kategori_default}
        if kategori_default == "belum terjelaskan":
            entri["dugaan"] = dugaan_default or (
                f"Perbedaan nilai antara {seri_utama_kode} dan {seri_pembanding_kode} pada tahun {th}."
            )
            entri["bukti_dicari"] = bukti_default or (
                f"Sudah memeriksa kolom tabel_nasional_gold untuk {seri_utama_kode} vs {seri_pembanding_kode}."
            )
        meta[th] = entri
    return meta


def jalankan_rekonsiliasi_tahap6(
    gold_path: str | Path = "data/gold/tabel_nasional_gold.parquet",
    out_dir: str | Path = "data/gold",
) -> pd.DataFrame:
    df_gold = pd.read_parquet(gold_path)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    daftar_pasangan = [
        (
            "var1161",
            "SDG_0821_NOC_RT",
            "var1161_vs_ILO_SDG_0821_NOC_RT",
            "metode berbeda",
            False,
            "Bandingkan basis indikator ILO SDG_0821_NOC_RT dengan seri utama var1161.",
        ),
        (
            "var1161",
            "SDG_B821_NOC_RT",
            "var1161_vs_ILO_SDG_B821_NOC_RT",
            "metode berbeda",
            False,
            "Bandingkan basis indikator ILO SDG_B821_NOC_RT dengan seri utama var1161.",
        ),
        (
            "var1161",
            "SL.GDP.PCAP.EM.KD",
            "var1161_vs_WDI_SL_GDP_PCAP_EM_KD",
            "metode berbeda",
            True,
            "",
        ),
        (
            "var1214",
            "NV.IND.MANF.ZS",
            "var1214_vs_WDI_NV_IND_MANF_ZS",
            "belum terjelaskan",
            False,
            "Periksa dasar harga (konstan vs berlaku) antara var1214 dan WDI NV.IND.MANF.ZS.",
        ),
        (
            "var2755",
            "SDG_0922_NOC_RT",
            "var2755_vs_ILO_SDG_0922_NOC_RT",
            "belum terjelaskan",
            False,
            "Bandingkan definisi dan cakupan var2755 dengan ILOSTAT SDG_0922_NOC_RT.",
        ),
    ]

    hasil_list: list[pd.DataFrame] = []
    for utama_kode, pembanding_kode, nama, kat_def, is_wdi_laju, catatan in daftar_pasangan:
        meta = buat_meta_otomatis_dari_pasangan(
            df_gold=df_gold,
            seri_utama_kode=utama_kode,
            seri_pembanding_kode=pembanding_kode,
            kategori_default=kat_def,
            konversi_laju_wdi=is_wdi_laju,
        )
        df_p = rekonsiliasi_satu_pasangan(
            df_gold=df_gold,
            seri_utama_kode=utama_kode,
            seri_pembanding_kode=pembanding_kode,
            nama_pasangan=nama,
            meta_kategori=meta,
            konversi_laju_wdi=is_wdi_laju,
            catatan_default=catatan,
        )
        hasil_list.append(df_p)

    tabel_rekonsiliasi = pd.concat(hasil_list, ignore_index=True)

    parquet_out = out_path / "rekonsiliasi_nasional.parquet"
    csv_out = out_path / "rekonsiliasi_nasional.csv"
    tabel_rekonsiliasi.to_parquet(parquet_out, index=False)
    tabel_rekonsiliasi.to_csv(csv_out, index=False)

    berpasangan = tabel_rekonsiliasi.dropna(
        subset=["nilai_seri_utama", "nilai_pembanding", "selisih"]
    )
    jumlah_pasangan = int(len(berpasangan))
    median_selisih = round(float(berpasangan["selisih"].median()), 6) if jumlah_pasangan > 0 else 0.0

    print(f"Tersimpan di: {parquet_out} dan {csv_out}")
    print(f"Total baris rekonsiliasi (termasuk periode tanpa pasangan): {len(tabel_rekonsiliasi)}")
    print(f"pasangan_rekonsiliasi={jumlah_pasangan}")
    print(f"selisih_median={median_selisih}")
    return tabel_rekonsiliasi


if __name__ == "__main__":
    jalankan_rekonsiliasi_tahap6()
