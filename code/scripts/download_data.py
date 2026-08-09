import requests
from pathlib import Path

from src.Config import RAW_DIR

HOTMAPS_DIR = RAW_DIR / "hotmaps"
EUROSTAT_DIR = RAW_DIR / "eurostat"
GISCO_DIR = RAW_DIR / "gisco"
UK_DIR = RAW_DIR / "uk"

for d in (HOTMAPS_DIR, EUROSTAT_DIR, GISCO_DIR, UK_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Hotmaps regional useful energy demand for SH+HW
HOTMAPS_REGIONAL_URL = (
    "https://gitlab.com/hotmaps/regional_demand/-/raw/master/data/Hotmaps_regional_demand.csv"
)

# Hotmaps building stock (not strictly needed, but provided for completeness)
HOTMAPS_BUILDING_STOCK_URL = (
    "https://gitlab.com/hotmaps/building-stock/-/raw/master/data/building_stock.csv"
)

# Eurostat CENS_21DWBNO_R3 – TSV via SDMX 2.1
EUROSTAT_CENS_CANDIDATES = [
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
    "CENS_21DWBNO_R3?time=2021&format=tsv&compressed=false",
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
    "cens_21dwbno_r3?time=2021&format=tsv&compressed=false",
]

# GISCO NUTS3 shapefile zip (1:1M, 4326)
GISCO_NUTS3_ZIP_URL = (
    "https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/"
    "NUTS_RG_01M_2021_4326.shp.zip"
)


def _download(url: str, dest: Path, binary: bool = False, timeout: int = 300) -> None:
    if dest.exists():
        print(f"[skip] {dest} already exists")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[download] {url}")
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    if binary:
        dest.write_bytes(resp.content)
    else:
        dest.write_text(resp.text, encoding="utf-8")
    size_mb = dest.stat().st_size / 1e6
    print(f"[ok] saved to {dest} ({size_mb:.2f} MB)")


def download_hotmaps_regional() -> Path:
    dest = HOTMAPS_DIR / "Hotmaps_regional_demand.csv"
    _download(HOTMAPS_REGIONAL_URL, dest, binary=False)
    return dest


def download_hotmaps_building_stock() -> Path:
    dest = HOTMAPS_DIR / "building_stock.csv"
    _download(HOTMAPS_BUILDING_STOCK_URL, dest, binary=False)
    return dest


def download_eurostat_census() -> Path:
    dest = EUROSTAT_DIR / "cens_21dwbno_r3.tsv"
    if dest.exists():
        print(f"[skip] {dest} already exists")
        return dest

    last_error = None
    for url in EUROSTAT_CENS_CANDIDATES:
        try:
            _download(url, dest, binary=False)
            return dest
        except requests.HTTPError as e:
            last_error = e
            print(f"[warn] Eurostat API failed for {url}: {e}")

    print("\n[ERROR] Could not download CENS_21DWBNO_R3 TSV automatically.")
    print("        Eurostat sometimes changes or throttles the API.")
    print("Manual one-time fallback:")
    print("  1. Open: https://ec.europa.eu/eurostat/databrowser/view/CENS_21DWBNO_R3/default/table?lang=en")
    print("  2. Click 'Download' → 'TSV'.")
    print(f"  3. Save the file as: {dest}")
    if last_error is not None:
        raise last_error
    else:
        raise RuntimeError("Eurostat TSV download failed.")


def download_gisco_nuts3() -> Path:
    dest = GISCO_DIR / "NUTS_RG_01M_2021_4326.shp.zip"
    _download(GISCO_NUTS3_ZIP_URL, dest, binary=True)
    return dest


def main() -> None:
    print("=== Downloading Hotmaps regional heat demand ===")
    download_hotmaps_regional()

    print("\n=== Downloading Hotmaps building stock CSV ===")
    download_hotmaps_building_stock()

    print("\n=== Downloading Eurostat census (CENS_21DWBNO_R3 TSV) ===")
    try:
        download_eurostat_census()
    except Exception as e:
        print(f"Eurostat download failed: {e}")

    print("\n=== Downloading GISCO NUTS3 shapefile (zip) ===")
    download_gisco_nuts3()

    print("\nAll downloads attempted. If Eurostat failed, follow the printed TSV instructions.")
    print("UK TS044 (accommodation type) is a manual one-time download; see README.")


if __name__ == "__main__":
    main()
