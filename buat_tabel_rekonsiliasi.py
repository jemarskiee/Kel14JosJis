import csv, json, glob, os

base = "data/raw"
out = "reports/profil/tabel-rekonsiliasi.csv"
os.makedirs(os.path.dirname(out), exist_ok=True)

data = {}

def put(series, year, value):
    if value not in (None, ""):
        try:
            data.setdefault(str(year), {})[series] = float(value)
        except (ValueError, TypeError):
            pass

# Seri nasional
with open("reports/profil/tabel_nasional.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        for s in ["var1161", "var1214", "var2755"]:
            put(s, r["periode"], r.get(s))

# Seri ILO
ilo_files = {
    "DF_SDG_0821_NOC_RT.csv": "ILO_0821",
    "DF_SDG_B821_NOC_RT.csv": "ILO_B821",
    "DF_SDG_0922_NOC_RT.csv": "ILO_0922",
}
for filename, series in ilo_files.items():
    path = os.path.join(base, "ilostat", "2026-10-20", "data", filename)
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("REF_AREA") == "IDN":
                put(series, r.get("TIME_PERIOD"), r.get("OBS_VALUE"))

# Seri WDI
wdi = {}
for path in glob.glob(os.path.join(base, "wdi", "2026-10-20", "data", "*.json")):
    with open(path, encoding="utf-8-sig") as f:
        j = json.load(f)
    for r in j[1]:
        if r.get("countryiso3code") != "IDN":
            continue
        code = r.get("indicator", {}).get("id")
        year = r.get("date")
        value = r.get("value")
        if code in ["SL.GDP.PCAP.EM.KD", "NV.IND.MANF.ZS"] and value is not None:
            wdi.setdefault(code, {})[int(year)] = float(value)

# WDI produktivitas: level dan pertumbuhan tahunan
levels = wdi.get("SL.GDP.PCAP.EM.KD", {})
for year, value in levels.items():
    put("WDI_productivity_level", year, value)
    prev = levels.get(year - 1)
    if prev not in (None, 0):
        put("WDI_productivity_growth_pct", year, (value / prev - 1) * 100)

for year, value in wdi.get("NV.IND.MANF.ZS", {}).items():
    put("WDI_manufacturing_pct", year, value)

columns = [
    "var1161", "ILO_0821", "ILO_B821",
    "WDI_productivity_level", "WDI_productivity_growth_pct",
    "var1214", "WDI_manufacturing_pct",
    "var2755", "ILO_0922"
]
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["periode"] + columns)
    writer.writeheader()
    for year in sorted(data, key=int):
        row = {"periode": year}
        row.update(data[year])
        writer.writerow(row)

print("Tabel berhasil dibuat:", out)

