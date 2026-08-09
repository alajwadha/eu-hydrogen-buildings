"""
02_classify.py — Classify buildings into SFH / MFH_LOW / MFH_HIGH / NON_RESIDENTIAL
================================================================================================

PURPOSE
-------
Take the raw EUBUCCO v0.2 building polygons for Luxembourg (NUTS2 = LU00),
compute per-building derived attributes, assign each building to one of four
classes used by the buildings model, aggregate to NUTS3 (LU000), and compare
against the existing simplified model row.

INPUTS  (produced by 01_download.py)
------------------------------------
  code/data/raw/eubucco/LU00.parquet

OUTPUTS
-------
  code/data/processed/{cc_lower}/    (e.g. lu/, fr/)
      LU_buildings_classified.parquet     per-building results (EUBUCCO subset)
      LU_aggregated_NUTS3.csv             counts + heated area by class
      LU_diagnostics_clean.pdf            1-page placeholder (overwritten by 04)
      LU_model_comparison.csv             new vs existing building_stock_nuts3.csv
  countries/Luxembourg/data/              (summary outputs mirrored)
      LU_buildings_aggregated_NUTS3.csv
      LU_model_comparison.csv
      LU_diagnostics_clean.pdf

USAGE
-----
    python code/scripts/country_build/02_classify.py --country LU
    python code/scripts/country_build/02_classify.py --country FR --per-partition

    --per-partition is a low-memory mode for large multi-partition countries
    (FR has 22 NUTS2 partitions, DE has 16, ...). Each partition is classified
    and streamed to the output parquet one at a time, so peak RAM stays at
    ~one partition instead of the whole country. It is required on a standard
    ~12 GB Colab runtime: without it, France (~29 M buildings) exhausts memory
    and the process is killed by the Linux OOM killer (exit code -9). See the
    run_per_partition() docstring for the two deliberate differences from the
    default all-at-once path (geometry not retained; aggregates concatenated).

NOTE: earlier versions also loaded the GBA.ODbLPolygon tile for a residential-
area cross-check. That was removed because the 10 GB tile took ~22 minutes to
bbox-filter through Drive FUSE, dominating total Colab time, while the
TUM-hosted WFS endpoint has a server-side response-size cap that makes paged
fetches no faster. The cross-check ratio (~1.4× GBA/EUBUCCO residential area)
remains documented in the paper methodology as a one-time published finding
attributed to Zhu et al. 2025. See commit history for the load_gba()
implementation if a fresh cross-check is ever needed.

================================================================================
CLASSIFICATION METHODOLOGY (paper-ready)
================================================================================

The model uses four classes that map to distinct heating-system feasibility,
insulation strategy, and energy-performance profiles:

  SFH              — Single-family house (detached, semi-detached, terraced)
  MFH_LOW          — Multi-family house, low-rise (3–5 floors)
  MFH_HIGH         — Multi-family house, mid/high-rise (≥6 floors)
  NON_RESIDENTIAL  — Commercial, industrial, office, retail, public

DECISION RULES (sequential, first match wins)
---------------------------------------------
  Rule 1.  EUBUCCO.type starts with "non-"            → NON_RESIDENTIAL
  Rule 2.  floors ≥ 6  AND  footprint ≥ 800 m²        → MFH_HIGH
  Rule 3.  floors ≤ 2  AND  footprint < 250 m²        → SFH
  Rule 4.  3 ≤ floors ≤ 5                              → MFH_LOW
  Rule 5.  default (ambiguous large building)          → MFH_HIGH

DERIVED ATTRIBUTES
------------------
  footprint_area_m2  = polygon area in EPSG:3035 (ETRS89 / LAEA, equal-area
                       projection standard for European spatial analysis)
  floors_estimated   = round(height_m / floor_height), min 1
                       floor_height = 3.0 m residential, 3.5 m non-residential
                       returns NaN if height missing
  heated_floor_area_m2 = footprint × floors × 0.85

JUSTIFICATIONS
--------------
- Rule 1 (EUBUCCO.type first):
    EUBUCCO's `type` attribute (where present, ~46% coverage in v0.1, higher in
    v0.2) is the most authoritative non-residential signal. Trusting it first
    short-circuits false-positive residential classification of commercial
    stock — critical because non-residential demand profiles differ
    fundamentally from residential and would distort our HP feasibility scoring.

- Rule 2 (≥6 floors AND ≥800 m² → MFH_HIGH):
    6 floors is the standard high-rise threshold in European building-stock
    typologies (TABULA, EU Building Stock Observatory, Hotmaps). At 6+ floors
    a lift becomes mandatory in most EU codes, structural construction shifts
    to concrete frame (vs masonry/timber), and HP retrofit becomes
    significantly harder (refrigerant volume limits, shaft space, electrical
    capacity, balcony unit placement). The 800 m² footprint co-requirement
    filters out narrow 6-floor row houses that wouldn't be towers.

- Rule 3 (≤2 floors AND <250 m² → SFH):
    Detached and small terraced homes. Most EU SFHs have footprints in the
    80-200 m² range; 250 m² caps row-house outliers. The 2-floor cap excludes
    3-floor townhouses, which energy-economically behave more like MFH_LOW
    (party-wall heat sharing, shared roof line, harder HP unit placement).

- Rule 4 (3-5 floors → MFH_LOW):
    Dominant European apartment-block typology — Plattenbau, HLM, IRA,
    Blocchi popolari etc. — same insulation strategy, same heating-system
    options (HP retrofit feasible with shaft work; gas/DH boiler centralised
    is dominant today; some scope for floor-by-floor unit replacement).

- Rule 5 (default MFH_HIGH):
    When height is missing AND footprint large, more likely a large building
    than a single-family home. Defaulting to MFH_HIGH is policy-conservative:
    high-rises are the hardest class to electrify, so over-counting MFH_HIGH
    *understates* achievable HP uptake. Erring in the policy-safe direction.

PARAMETER VALUES AND THEIR SOURCES
----------------------------------
  3.0 m floor-to-floor residential   = European typical (2.5 m clear ceiling
                                       + 0.5 m structure + services)
  3.5 m floor-to-floor other         = commercial ceiling height + raised
                                       access floor allowance
  0.85 useable area fraction         = TABULA, ISO 52000 (after internal
                                       walls, lobbies, stairwells)
  250 m² SFH footprint cap           = EU SFH typology midpoint + row-house
                                       upper bound (Hotmaps, TABULA)
  800 m² high-rise minimum footprint = corresponds to roughly an apartment
                                       floor with ~10-15 units

KNOWN LIMITATIONS (to disclose in paper methods section)
--------------------------------------------------------
  1. Height attribute coverage in EUBUCCO LU ~73% (Milojevic-Dupont et al. 2023);
     for the ~27% without height we fall back to area-only rules, which are
     biased toward classifying as SFH or MFH_LOW.
  2. EUBUCCO type attribute coverage in v0.1 was 46% (LU v0.2 may differ);
     when missing, residential is the working assumption.
  3. The 6-floor / 800 m² thresholds are heuristic and unvalidated against
     national Luxembourg building stock data (STATEC). A future calibration
     step should sample EUBUCCO buildings against STATEC ground truth.
  4. We classify by physical attributes only; no use is made of EUBUCCO's
     `building-type-harmonization.csv` taxonomy table. Adding this is a
     subsequent improvement.
  5. The 0.85 useable-area fraction is a single TABULA-default value applied
     uniformly. Real values vary 0.75–0.92 across building types and ages.

VALIDATION DESIGN (subsequent)
------------------------------
  - Cross-check total dwelling count against STATEC 2021 census (LU has
    ~241k dwellings in residential buildings).
  - Cross-check total heated floor area against Eurostat ENER/NRG_BAL series.
  - Compare per-class share against Luxembourg Cadastre 2020 register.

OUTPUTS — FOR PAPER
-------------------
  Use `LU_aggregated_NUTS3.csv` directly in the methods section. The diagnostics
  PDF can be reproduced as a paper appendix figure. The per-building parquet
  is too large for the paper but supports reviewer reproducibility on request.
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths ───────────────────────────────────────────────────────────────────
# Banner: set the environment variable `EUHB_RAW_DIR` to override the default
# raw-data location. Used by the Colab notebook to read raw data from Google
# Drive (MyDrive/eu-hydrogen-raw/). Default (laptop/Codespaces) is unchanged.
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = Path(
    os.environ.get("EUHB_RAW_DIR", REPO_ROOT / "code" / "data" / "raw")
)
EXISTING_BS = REPO_ROOT / "code" / "data" / "processed" / "building_stock_nuts3.csv"

# Import country config loader
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))
from CountryConfig import CountryConfig, load_country_config  # noqa: E402


def build_paths(cfg: CountryConfig) -> dict:
    """Compute all per-country paths in one place.

    Returns a dict with both filesystem paths to write outputs to and the
    raw-data parquet path(s) that 01_download.py will have produced.
    """
    cc = cfg.country_code           # e.g. "LU"
    cc_lower = cfg.cc_lower          # e.g. "lu"
    cname = cfg.country_name         # e.g. "Luxembourg"
    out_dir = REPO_ROOT / "code" / "data" / "processed" / cc_lower
    out_dir.mkdir(parents=True, exist_ok=True)
    # Mirror dir must match the curated countries/<dir>/ names (hyphenated; a couple
    # differ from the display country_name, e.g. Czechia -> Czech-Republic).
    _DIR_OVERRIDE = {"Czechia": "Czech-Republic"}
    dir_cname = _DIR_OVERRIDE.get(cname, cname.replace(" ", "-"))
    country_dir = REPO_ROOT / "countries" / dir_cname / "data"
    country_dir.mkdir(parents=True, exist_ok=True)
    return {
        # Raw sources: one parquet per NUTS2 partition
        "eubucco_sources": [RAW_DIR / "eubucco" / cfg.eubucco_filename(p)
                            for p in cfg.nuts2_partitions],
        "out_dir":         out_dir,
        "out_parquet":     out_dir / f"{cc}_buildings_classified.parquet",
        "out_nuts3":       out_dir / f"{cc}_aggregated_NUTS3.csv",
        "out_pdf":         out_dir / f"{cc}_diagnostics_clean.pdf",
        "out_comparison":  out_dir / f"{cc}_model_comparison.csv",
        "country_dir":         country_dir,
        "country_out_nuts3":   country_dir / f"{cc}_buildings_aggregated_NUTS3.csv",
        "country_out_comparison": country_dir / f"{cc}_model_comparison.csv",
        "country_out_pdf":     country_dir / f"{cc}_diagnostics_clean.pdf",
    }


# ── Logging helpers ─────────────────────────────────────────────────────────
def header(s: str) -> None:
    print()
    print("=" * 60)
    print(s)
    print("=" * 60)


def section(s: str) -> None:
    print(f"\n── {s} " + "─" * (55 - len(s)))


# ── Load data ───────────────────────────────────────────────────────────────
def load_eubucco(sources: list[Path]):
    """Load EUBUCCO parquet(s) for one country.

    Multi-partition countries (FR has 22, DE has 16, etc.) get their
    NUTS2 parquets concatenated into a single GeoDataFrame here.
    Single-partition countries (LU has 1) get a single load.
    """
    try:
        import geopandas as gpd
    except ImportError:
        print("ERROR: geopandas not installed. Run: pip install geopandas pyarrow")
        sys.exit(1)

    missing = [p for p in sources if not p.exists()]
    if missing:
        print(f"ERROR: EUBUCCO source(s) not found:")
        for p in missing:
            print(f"   {p}")
        print("Run 01_download.py --country <CC> first.")
        sys.exit(1)

    if len(sources) == 1:
        section(f"Loading EUBUCCO {sources[0].name}")
        gdf = gpd.read_parquet(sources[0])
    else:
        section(f"Loading {len(sources)} EUBUCCO partitions and concatenating")
        parts = []
        for i, src in enumerate(sources, 1):
            print(f"  [{i}/{len(sources)}] {src.name}", end=" ... ", flush=True)
            part = gpd.read_parquet(src)
            print(f"{len(part):,} rows")
            parts.append(part)
        gdf = pd.concat(parts, ignore_index=True)
        # Restore GeoDataFrame type after concat (pandas concat loses it)
        if not isinstance(gdf, gpd.GeoDataFrame):
            gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=parts[0].crs)
    print(f"  rows:    {len(gdf):,}")
    print(f"  columns: {list(gdf.columns)}")
    print(f"  CRS:     {gdf.crs}")
    if len(gdf) > 0:
        print("  sample rows (first 3):")
        sample_cols = [c for c in gdf.columns if c != "geometry"][:6]
        print(gdf[sample_cols].head(3).to_string(index=False))
    return gdf


# ── Classification ──────────────────────────────────────────────────────────
def estimate_floors(height_m: float, is_residential: bool,
                    floor_h_residential: float,
                    floor_h_other: float) -> float:
    """Floors estimated from building height. Returns NaN if height invalid.

    Floor-height assumption (see module docstring §PARAMETER VALUES):
      - Residential:     ~3.0 m (clear ceiling 2.5 m + structure + services)
      - Non-residential: ~3.5 m (commercial ceiling + raised access floor)
    Min 1 floor enforced. Round to nearest integer. Country-configurable.
    """
    if pd.isna(height_m) or height_m <= 0:
        return np.nan
    floor_h = floor_h_residential if is_residential else floor_h_other
    n = max(1.0, np.round(height_m / floor_h))
    return n


def classify_row(area_m2: float, floors: float, type_str: str | None) -> str:
    """
    Classify one building into SFH / MFH_LOW / MFH_HIGH / NON_RESIDENTIAL.

    Sequential rules (see module docstring §DECISION RULES for full justification):
      Rule 1.  EUBUCCO.type starts with "non-"        → NON_RESIDENTIAL
      Rule 2.  floors ≥ 6  AND  footprint ≥ 800       → MFH_HIGH
      Rule 3.  floors ≤ 2  AND  footprint < 250       → SFH
      Rule 4.  3 ≤ floors ≤ 5                          → MFH_LOW
      Rule 5.  default                                  → MFH_HIGH

    Parameters
    ----------
    area_m2 : float
        Footprint area in EPSG:3035 square metres.
    floors : float
        Estimated number of storeys. NaN if height missing.
    type_str : str | None
        EUBUCCO `type` attribute. None if missing.

    Returns
    -------
    str  one of {"SFH", "MFH_LOW", "MFH_HIGH", "NON_RESIDENTIAL"}
    """
    # Rule 1: explicit non-residential overrides everything
    if type_str is not None and isinstance(type_str, str):
        t = type_str.strip().lower()
        if t in ("non-residential", "non_residential", "nonres",
                 "commercial", "industrial", "office", "retail"):
            return "NON_RESIDENTIAL"

    # Without a usable height we fall back to area-only heuristic.
    # Bias is toward SFH/MFH_LOW; flagged as a limitation in module docstring.
    if pd.isna(floors):
        if pd.isna(area_m2) or area_m2 < 250:
            return "SFH"
        return "MFH_LOW"

    # Rule 2: high-rise — needs both floor and footprint thresholds
    if floors >= 6 and (pd.isna(area_m2) or area_m2 >= 800):
        return "MFH_HIGH"
    # Rule 3: single-family — small footprint + low floor count
    if floors <= 2 and (pd.isna(area_m2) or area_m2 < 250):
        return "SFH"
    # Rule 4: low-rise apartment block — dominant European mid-density typology
    if floors <= 5:
        return "MFH_LOW"
    # Rule 5: ambiguous — default to MFH_HIGH (policy-conservative for HP uptake)
    return "MFH_HIGH"


def add_derived_attrs(gdf, source_label: str, height_col: str | None,
                      type_col: str | None, cfg: CountryConfig):
    """
    Add footprint_area_m2, floors_estimated, building_class, heated_floor_area_m2.
    Assumes gdf is already in a sensible CRS; reprojects to EPSG:3035 for area.
    Uses country-config-supplied floor heights and useable area fraction.
    """
    section(f"Computing derived attributes [{source_label}]")
    if gdf.crs is None:
        print("  WARN: no CRS — assuming EPSG:4326")
        gdf = gdf.set_crs("EPSG:4326")

    # Project to ETRS89-LAEA for accurate European area
    gdf_proj = gdf.to_crs("EPSG:3035")
    gdf["footprint_area_m2"] = gdf_proj.geometry.area
    print(f"  footprint area: median {gdf.footprint_area_m2.median():.0f} m², "
          f"max {gdf.footprint_area_m2.max():.0f} m²")

    # Height
    if height_col and height_col in gdf.columns:
        gdf["height_m"] = pd.to_numeric(gdf[height_col], errors="coerce")
        n_with_h = gdf.height_m.notna().sum()
        print(f"  height available: {n_with_h:,} / {len(gdf):,} "
              f"({n_with_h*100/len(gdf):.1f}%)")
    else:
        gdf["height_m"] = np.nan
        print(f"  height column not present in this source — all NaN")

    # Type (residential / non-residential)
    if type_col and type_col in gdf.columns:
        gdf["building_type_raw"] = gdf[type_col].astype(str).where(
            gdf[type_col].notna(), None)
        n_with_t = gdf.building_type_raw.notna().sum()
        print(f"  type available:   {n_with_t:,} / {len(gdf):,} "
              f"({n_with_t*100/len(gdf):.1f}%)")
    else:
        gdf["building_type_raw"] = None
        print("  type column not present")

    # Floors
    is_residential = ~gdf["building_type_raw"].fillna("").str.lower().str.startswith("non")
    gdf["floors_estimated"] = gdf.apply(
        lambda r: estimate_floors(r["height_m"], is_residential.loc[r.name],
                                  cfg.floor_height_residential_m,
                                  cfg.floor_height_other_m),
        axis=1
    )
    # Prefer EUBUCCO's native `floors` column when configured
    # (classification.floor_source: eubucco) -- roof-aware, avoids the
    # round(height / 3 m) over-count. Height estimate stays the fallback.
    if cfg.floor_source == "eubucco" and "floors" in gdf.columns:
        native = pd.to_numeric(gdf["floors"], errors="coerce")
        gdf["floors_estimated"] = native.where(
            native.notna() & (native > 0.0), gdf["floors_estimated"])

    # Building class
    gdf["building_class"] = gdf.apply(
        lambda r: classify_row(r["footprint_area_m2"],
                               r["floors_estimated"],
                               r["building_type_raw"]),
        axis=1
    )

    # Heated floor area (residential only, set 0 for non-residential)
    floors_for_area = gdf["floors_estimated"].fillna(1.0)
    raw_floor_area = (gdf["footprint_area_m2"] * floors_for_area
                      * cfg.useable_area_fraction)
    gdf["heated_floor_area_m2"] = np.where(
        gdf["building_class"] == "NON_RESIDENTIAL", 0.0, raw_floor_area
    )

    print(f"  classification breakdown:")
    print(gdf.building_class.value_counts().to_string())
    print(f"  total heated floor area: "
          f"{gdf.heated_floor_area_m2.sum()/1e6:.2f} million m²")

    return gdf


# ── Aggregation + model comparison ─────────────────────────────────────────
def assign_nuts3(gdf, cfg: CountryConfig):
    """Attach a NUTS3 region code to every building as column 'nuts3'.

    Strategy (in order of preference):
      1. If EUBUCCO already has 'region_id' (NUTS3) — use it directly.
         This is the v0.2 schema documented at
         https://docs.eubucco.com/v0.2/data-format/schema/. EUBUCCO uses
         "modified NUTS 2016 boundaries" with two regional merges
         (DEB33 -> DEB3H, UKD73 -> UKD47).
      2. If single-NUTS3 country in cfg (e.g. LU, MT) — use the only code.
      3. Otherwise — fall back to a GISCO NUTS3 boundary spatial join
         (used if a future EUBUCCO version drops region_id, or for
         other building datasets that lack it).
    """
    # Strategy 1: trust the column if EUBUCCO provides it
    if "region_id" in gdf.columns:
        section("Using EUBUCCO 'region_id' column for NUTS3 attribution")
        n_with = gdf["region_id"].notna().sum()
        print(f"  region_id available: {n_with:,}/{len(gdf):,} "
              f"({n_with*100/len(gdf):.1f}%)")
        gdf = gdf.copy()
        gdf["nuts3"] = gdf["region_id"].fillna(f"{cfg.country_code}_UNKNOWN")
        # Sanity: verify the codes look like NUTS3 (length 5)
        sample = gdf["nuts3"].dropna().astype(str).head(5).tolist()
        print(f"  sample NUTS3 codes: {sample}")
        # Check coverage vs config
        unique = gdf["nuts3"].nunique()
        print(f"  unique NUTS3 codes in data: {unique} "
              f"(config lists {len(cfg.nuts3_regions)})")
        return gdf

    # Strategy 2: trivial single-region country (LU, MT, ...)
    if len(cfg.nuts3_regions) == 1:
        gdf = gdf.copy()
        gdf["nuts3"] = cfg.nuts3_regions[0]
        return gdf

    # Strategy 3: GISCO spatial join (multi-region country, no region_id col)
    import geopandas as gpd
    gisco_dir = REPO_ROOT / "code" / "data" / "raw" / "gisco"
    candidates = list(gisco_dir.glob("NUTS_RG_*_4326.shp")) \
               + list(gisco_dir.glob("NUTS_RG_*_4326.gpkg")) \
               + list(gisco_dir.glob("NUTS_RG_*_4326.geojson"))
    if not candidates:
        raise FileNotFoundError(
            f"Multi-NUTS3 country {cfg.country_code} needs a GISCO NUTS3 "
            f"boundary file (the parquet has no 'region_id' column). "
            f"Expected one of:\n"
            f"  {gisco_dir}/NUTS_RG_01M_2021_4326.{{shp,gpkg,geojson}}\n"
            f"Download from "
            f"https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/"
            f"administrative-units-statistical-units/nuts (scale 1:1M, year 2021, "
            f"EPSG:4326 (Geographic/WGS84), Polygons)."
        )
    nuts_file = candidates[0]
    section(f"NUTS3 spatial join fallback "
            f"(multi-region country, {len(cfg.nuts3_regions)} regions expected)")
    print(f"  using boundary file: {nuts_file.name}")
    bnd = gpd.read_file(nuts_file)
    bnd_n3 = bnd[(bnd["LEVL_CODE"] == 3)
                 & (bnd["CNTR_CODE"] == cfg.country_code)][
                     ["NUTS_ID", "geometry"]].rename(columns={"NUTS_ID": "nuts3"})
    print(f"  GISCO has {len(bnd_n3)} NUTS3 polygons for {cfg.country_code}")
    if len(bnd_n3) != len(cfg.nuts3_regions):
        print(f"  WARN: config lists {len(cfg.nuts3_regions)} NUTS3 regions "
              f"but GISCO returns {len(bnd_n3)}. Check {cfg.cc_lower}.yaml.")
    gdf_proj = gdf.to_crs("EPSG:3035")
    bnd_proj = bnd_n3.to_crs("EPSG:3035")
    points = gdf_proj.copy()
    points["geometry"] = gdf_proj.geometry.representative_point()
    joined = gpd.sjoin(points, bnd_proj, how="left", predicate="within")
    n_unmatched = joined["nuts3"].isna().sum()
    if n_unmatched:
        print(f"  WARN: {n_unmatched:,} buildings could not be matched to a NUTS3 "
              f"region (~{n_unmatched*100/len(joined):.2f}%). These will be "
              f"labelled as '{cfg.country_code}_UNMATCHED'.")
    joined["nuts3"] = joined["nuts3"].fillna(f"{cfg.country_code}_UNMATCHED")
    gdf = gdf.copy()
    gdf["nuts3"] = joined["nuts3"].values
    return gdf


def aggregate_to_nuts3(gdf, label: str) -> pd.DataFrame:
    """Aggregate building-level counts and heated areas, grouped by
    (nuts3, building_class). `gdf` must have a 'nuts3' column attached
    by `assign_nuts3` first.
    """
    if "nuts3" not in gdf.columns:
        raise ValueError(
            "aggregate_to_nuts3: gdf has no 'nuts3' column. "
            "Call assign_nuts3(gdf, cfg) first."
        )
    # observed=True so category-dtype keys (per-partition pass 2) produce the
    # same rows as object-dtype keys (all-at-once path) — present combos only.
    agg = gdf.groupby(["nuts3", "building_class"], observed=True).agg(
        building_count=("building_class", "size"),
        total_footprint_m2=("footprint_area_m2", "sum"),
        total_heated_area_m2=("heated_floor_area_m2", "sum"),
        mean_floors=("floors_estimated", "mean"),
        median_height_m=("height_m", "median"),
    ).reset_index()
    agg["source"] = label
    return agg


def compare_to_existing_model(agg_eubucco: pd.DataFrame,
                              cfg: CountryConfig) -> pd.DataFrame:
    """Compare aggregated counts to the existing building_stock_nuts3.csv row(s).

    For single-NUTS3 countries this is a per-class comparison.
    For multi-NUTS3 countries this aggregates to country total first
    (Hotmaps NUTS3 rows are joined separately by 03_heat_intensity.py).
    """
    nuts3_for_compare = cfg.hotmaps_nuts3_id
    section(f"Comparison with current model ({nuts3_for_compare} row)")
    if not EXISTING_BS.exists():
        print(f"  WARN: {EXISTING_BS} not found, skipping comparison")
        return pd.DataFrame()

    bs = pd.read_csv(EXISTING_BS)
    if len(cfg.nuts3_regions) == 1:
        model_rows = bs[bs.nuts_id == nuts3_for_compare].copy()
    else:
        # Multi-region: compare against any of this country's rows in the
        # existing model (these are stored at NUTS3 in building_stock_nuts3.csv)
        model_rows = bs[bs.nuts_id.str.startswith(cfg.country_code)].copy()

    if model_rows.empty:
        print(f"  WARN: no rows for {cfg.country_code} found in model")
        return pd.DataFrame()

    print(f"\n  CURRENT model (building_stock_nuts3.csv) — "
          f"{len(model_rows)} rows for {cfg.country_code}:")
    print(model_rows[["nuts_id", "building_type", "dwellings_2021",
                      "heat_2015_MWh"]].head(10).to_string(index=False))

    # Aggregate EUBUCCO results to country total for the compare table
    # (NUTS3-level comparison stays in 03's reconciliation CSV).
    eu_country = agg_eubucco.groupby("building_class").agg(
        building_count=("building_count", "sum"),
        total_heated_area_m2=("total_heated_area_m2", "sum"),
    ).reset_index()
    print("\n  EUBUCCO classification (country total):")
    print(eu_country.to_string(index=False))

    # Build a side-by-side comparison at country level
    eubucco_pivot = eu_country.set_index("building_class")[
        ["building_count", "total_heated_area_m2"]
    ].rename(columns=lambda c: f"eubucco_{c}")
    model_map = {"SFH": "SFH", "MFH_LOW": "MFH_HIGH", "MFH_HIGH": "MFH_HIGH",
                 "NON_RESIDENTIAL": "OTHER"}
    model_pivot = model_rows.groupby("building_type").agg(
        model_dwellings=("dwellings_2021", "sum"),
        model_heat_MWh=("heat_2015_MWh", "sum"),
    )
    combined = eubucco_pivot.reset_index()
    combined["model_building_type"] = combined["building_class"].map(model_map)
    combined = combined.merge(
        model_pivot.reset_index().rename(columns={"building_type": "model_building_type"}),
        on="model_building_type", how="left"
    )
    return combined


# ── Diagnostic plots ────────────────────────────────────────────────────────
def make_diagnostics(eubucco, out_pdf: Path) -> None:
    """Placeholder — the real 8-page diagnostic PDF is generated by
    code/scripts/country_build/04_diagnostics.py after script 03 has
    produced the heat-demand outputs. We keep this function as a no-op
    so the existing call site in main() works; it just writes a short
    interim placeholder PDF that 04 then overwrites.

    Rationale for the split: the old in-script plots (footprint histograms,
    height distributions, etc.) added little analytical value. The new PDF
    requires reconciliation + heat-intensity outputs from script 03, which
    is why diagnostic generation moved to 04.
    """
    section("Skipping in-script diagnostics (handled by 04_diagnostics.py)")
    print(f"  Interim placeholder will be at {out_pdf}")
    print("  Run 04_diagnostics.py after 03_heat_intensity.py for the full 8-page PDF.")
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
    except ImportError:
        return

    # Minimal placeholder so out_pdf exists if 04 isn't run
    with PdfPages(out_pdf) as pp:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        ax.text(0.5, 0.65,
                "Diagnostic PDF — placeholder\n\n"
                "The full 8-page diagnostic is generated by\n"
                "04_diagnostics.py after 03_heat_intensity.py.\n\n"
                "If you are seeing this page in the committed PDF, the\n"
                "pipeline did not complete past script 02.",
                ha="center", va="center", fontsize=11,
                family="DejaVu Sans")
        pp.savefig(fig)
        plt.close(fig)


# ── Per-partition (low-memory) classification ───────────────────────────────
# Buildings per streamed batch. A whole French NUTS2 region (e.g. Ile-de-France
# / FR10) is itself too large to hold in a standard ~12 GB runtime, so even
# per-partition we must sub-divide. Overridable via the EUHB_PARTITION_BATCH
# environment variable if a batch still proves too big (or to go faster on a
# High-RAM runtime).
_PARTITION_BATCH_SIZE = int(os.environ.get("EUHB_PARTITION_BATCH", 250_000))


def _estimate_floors_vectorized(height, is_residential, fh_res, fh_other):
    """Array form of estimate_floors().

    floors = max(1, round(height / floor_height)); NaN where height is
    missing or non-positive. floor_height is the residential value where
    is_residential is True, else the non-residential value. Uses np.round
    (round-half-to-even), exactly as estimate_floors() does.
    """
    h = pd.to_numeric(height, errors="coerce").to_numpy(dtype="float64")
    fh = np.where(np.asarray(is_residential, dtype=bool), fh_res, fh_other)
    with np.errstate(invalid="ignore", divide="ignore"):
        n = np.maximum(1.0, np.round(h / fh))
    return np.where(np.isnan(h) | (h <= 0), np.nan, n)


def _classify_vectorized(area, floors, building_type_raw):
    """Array form of classify_row().

    Reproduces classify_row()'s sequential first-match rules with np.select
    (np.select returns the choice of the first true condition, so condition
    order == rule order). Verified byte-identical to looping classify_row()
    over the rows -- see the Luxembourg smoke test referenced in
    run_per_partition().
    """
    area = np.asarray(area, dtype="float64")
    floors = np.asarray(floors, dtype="float64")
    area_na = np.isnan(area)
    floors_na = np.isnan(floors)

    t = pd.Series(building_type_raw, dtype="object").astype("string")
    t = t.str.strip().str.lower()
    nonres = t.isin(["non-residential", "non_residential", "nonres",
                     "commercial", "industrial", "office", "retail"])
    nonres = nonres.fillna(False).to_numpy(dtype=bool)

    small_area = area_na | (area < 250.0)   # area missing OR < 250 m^2
    big_area = area_na | (area >= 800.0)    # area missing OR >= 800 m^2

    conds = [
        nonres,                                          # Rule 1
        floors_na & small_area,                          # floors NaN -> SFH
        floors_na & ~small_area,                         # floors NaN -> MFH_LOW
        (~floors_na) & (floors >= 6.0) & big_area,       # Rule 2
        (~floors_na) & (floors <= 2.0) & small_area,     # Rule 3
        (~floors_na) & (floors <= 5.0),                  # Rule 4
    ]
    choices = ["NON_RESIDENTIAL", "SFH", "MFH_LOW",
               "MFH_HIGH", "SFH", "MFH_LOW"]
    return np.select(conds, choices, default="MFH_HIGH")  # Rule 5


def _derive_and_classify(gdf, height_col, type_col, cfg):
    """Vectorised port of add_derived_attrs() for the per-partition path.

    Computes footprint_area_m2, height_m, building_type_raw,
    floors_estimated, building_class and heated_floor_area_m2 with array
    operations instead of per-row .apply(axis=1) -- the row form is both a
    speed and a memory problem at country scale. Returns a plain
    (geometry-free) DataFrame; construction_year and region_id are passed
    through if present. Verified to match add_derived_attrs() exactly via
    the Luxembourg smoke test.
    """
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    footprint = gdf.geometry.to_crs("EPSG:3035").area.to_numpy(dtype="float64")

    if height_col and height_col in gdf.columns:
        height = pd.to_numeric(gdf[height_col], errors="coerce")
    else:
        height = pd.Series(np.nan, index=gdf.index)

    if type_col and type_col in gdf.columns:
        raw = gdf[type_col]
        building_type_raw = raw.astype(str).where(raw.notna(), None)
    else:
        building_type_raw = pd.Series([None] * len(gdf), index=gdf.index,
                                      dtype="object")

    is_residential = ~(building_type_raw.fillna("").astype(str)
                       .str.lower().str.startswith("non"))
    floors = _estimate_floors_vectorized(
        height, is_residential.to_numpy(dtype=bool),
        cfg.floor_height_residential_m, cfg.floor_height_other_m)
    # Prefer EUBUCCO's native `floors` column when configured
    # (classification.floor_source: eubucco). It is roof-aware and avoids the
    # systematic over-count of round(height / 3 m); the height estimate above
    # stays the fallback for any building whose native value is missing or
    # non-positive.
    if cfg.floor_source == "eubucco" and "floors" in gdf.columns:
        native = pd.to_numeric(gdf["floors"],
                               errors="coerce").to_numpy(dtype="float64")
        floors = np.where(np.isnan(native) | (native <= 0.0), floors, native)

    building_class = _classify_vectorized(footprint, floors,
                                          building_type_raw)

    floors_for_area = np.where(np.isnan(floors), 1.0, floors)
    raw_area = footprint * floors_for_area * cfg.useable_area_fraction
    heated = np.where(building_class == "NON_RESIDENTIAL", 0.0, raw_area)

    out = pd.DataFrame({
        "footprint_area_m2": footprint,
        "height_m": height.to_numpy(dtype="float64"),
        "floors_estimated": floors,
        "building_type_raw": building_type_raw.to_numpy(),
        "building_class": building_class,
        "heated_floor_area_m2": heated,
    })
    for passthrough in ("construction_year", "region_id"):
        if passthrough in gdf.columns:
            out[passthrough] = gdf[passthrough].to_numpy()
    return out


def run_per_partition(cfg: CountryConfig, paths: dict) -> int:
    """Memory-bounded classification for large multi-partition countries.

    The default path in main() loads every NUTS2 partition into a single
    in-memory GeoDataFrame. For France (~53 million buildings across 22
    partitions) that peaks far above a standard Colab runtime's ~12 GB and
    the process is killed by the OOM killer (observed: exit code -9). A
    single dense NUTS2 region (Ile-de-France) is itself too large, so this
    mode streams in two ways:

      * each NUTS2 parquet is read in row batches of _PARTITION_BATCH_SIZE
        buildings (env var EUHB_PARTITION_BATCH);
      * each batch is classified with vectorised array operations and
        appended to the output parquet, then freed before the next batch.

    Peak memory is therefore ~one batch, regardless of how large a partition
    or the whole country is.

    Three differences from the all-at-once path, all deliberate:

      1. The classified parquet does NOT retain polygon `geometry`. Geometry
         is used only to derive `footprint_area_m2` (which IS kept). No
         downstream script reads geometry: 03_heat_intensity.py needs only
         scalar attribute columns, and 04_diagnostics.py reads CSVs.

      2. Classification is vectorised (_derive_and_classify) rather than a
         per-row .apply(). The rules are unchanged; results are verified
         byte-identical to the all-at-once path on Luxembourg.

      3. NUTS3 aggregation is done per partition, inside the streaming loop,
         on one partition's scalar (geometry-free) data at a time. Because
         each NUTS3 region belongs to exactly one NUTS2 partition, the
         per-partition aggregates concatenate exactly -- this avoids a
         full-table readback that, at ~53 M rows, itself exhausted RAM.

    All computed values are identical to the all-at-once path.
    """
    import gc
    import json

    try:
        import geopandas as gpd
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("ERROR: per-partition mode needs geopandas + pyarrow.")
        print("Run: pip install geopandas pyarrow")
        return 1

    sources = paths["eubucco_sources"]
    missing = [p for p in sources if not p.exists()]
    if missing:
        print("ERROR: EUBUCCO source(s) not found:")
        for p in missing:
            print(f"   {p}")
        print(f"Run 01_download.py --country {cfg.country_code} first.")
        return 1

    header(f"{cfg.country_name} ({cfg.country_code}) — building "
           f"classification [per-partition / low-memory mode]")
    section(f"Streaming {len(sources)} NUTS2 partitions in batches of "
            f"{_PARTITION_BATCH_SIZE:,} buildings")
    print(f"  output parquet: {paths['out_parquet']}")
    print("  geometry is not retained (footprint_area_m2 is kept) — "
          "see run_per_partition docstring.")

    # Columns persisted per building. `geometry` is intentionally excluded.
    desired_cols = ["footprint_area_m2", "height_m", "floors_estimated",
                    "building_type_raw", "building_class",
                    "heated_floor_area_m2", "construction_year", "nuts3"]
    str_cols = {"building_type_raw", "building_class", "nuts3"}

    writer = None
    final_cols = None
    total_rows = 0
    agg_parts = []   # one small NUTS3 aggregate per partition

    for i, src in enumerate(sources, 1):
        pf = pq.ParquetFile(src)
        n_src = pf.metadata.num_rows
        section(f"Partition [{i}/{len(sources)}] — {src.name} "
                f"({n_src:,} buildings)")

        # GeoParquet metadata: geometry column name + CRS.
        geom_col, crs = "geometry", "EPSG:4326"
        md = pf.schema_arrow.metadata
        if md and b"geo" in md:
            geo = json.loads(md[b"geo"])
            geom_col = geo.get("primary_column", "geometry")
            crs = geo.get("columns", {}).get(geom_col, {}).get("crs") or crs

        part_rows = 0
        partition_frames = []   # this partition's geometry-free scalar batches
        for batch in pf.iter_batches(batch_size=_PARTITION_BATCH_SIZE):
            df = pa.Table.from_batches([batch]).to_pandas()
            geom = gpd.GeoSeries.from_wkb(df[geom_col], crs=crs)
            gdf = gpd.GeoDataFrame(df.drop(columns=[geom_col]),
                                   geometry=geom, crs=crs)
            del df

            height_col = type_col = None
            for c in gdf.columns:
                lc = c.lower()
                if "height" in lc and height_col is None:
                    height_col = c
                if "type" in lc and type_col is None:
                    type_col = c

            rec = _derive_and_classify(gdf, height_col, type_col, cfg)
            del gdf

            # NUTS3 from EUBUCCO's region_id (v0.2 schema). Per-partition
            # mode needs region_id, or a single-NUTS3 country; it does not
            # do the geometry-based GISCO spatial-join fallback.
            if "region_id" in rec.columns:
                rec["nuts3"] = rec["region_id"].fillna(
                    f"{cfg.country_code}_UNKNOWN")
            elif len(cfg.nuts3_regions) == 1:
                rec["nuts3"] = cfg.nuts3_regions[0]
            else:
                if writer is not None:
                    writer.close()
                print(f"ERROR: per-partition mode needs an EUBUCCO "
                      f"'region_id' column for multi-region countries; none "
                      f"found in {src.name}.")
                return 1

            # Fix the persisted column set from the first batch so every
            # written row group shares one Arrow schema.
            if final_cols is None:
                final_cols = [c for c in desired_cols if c in rec.columns]
                if "construction_year" not in final_cols:
                    print("  WARN: 'construction_year' not in EUBUCCO data — "
                          "script 03 will use unknown-cohort intensities.")

            # Plain (non-geo) frame, explicit dtypes -> stable schema.
            # 'string' dtype (not object) so an all-null batch still yields
            # an Arrow `string` field rather than `null`.
            out = pd.DataFrame()
            for c in final_cols:
                s = rec[c].reset_index(drop=True)
                if c in str_cols:
                    out[c] = s.astype("string")
                else:
                    out[c] = pd.to_numeric(s, errors="coerce").astype("float64")
            del rec

            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(paths["out_parquet"], table.schema)
            writer.write_table(table)
            part_rows += len(out)
            total_rows += len(out)
            partition_frames.append(out)   # kept for this partition's aggregate
            del table
            gc.collect()

        # Aggregate this partition to NUTS3 now, while only one partition's
        # worth of (geometry-free, scalar) data is in memory. EUBUCCO
        # partitions are per-NUTS2 and every NUTS3 region belongs to exactly
        # one NUTS2, so each partition's NUTS3 keys are disjoint from every
        # other partition's: the per-partition aggregates concatenate exactly,
        # no (nuts3, building_class) key appears twice. This replaces a
        # full-table readback that, at ~53 M rows, exhausted a standard
        # runtime's RAM (the observed exit -9 in the aggregation step).
        part_df = pd.concat(partition_frames, ignore_index=True)
        del partition_frames
        agg_parts.append(aggregate_to_nuts3(part_df, "EUBUCCO"))
        del part_df
        gc.collect()
        print(f"  classified {part_rows:,} buildings "
              f"(running total {total_rows:,})")

    if writer is not None:
        writer.close()
    section("Per-building parquet written")
    print(f"  {total_rows:,} buildings -> {paths['out_parquet']}")
    print(f"  columns: {final_cols} (geometry not retained)")

    # Concatenate the per-partition NUTS3 aggregates (disjoint keys -- see
    # the comment in the loop). Sort so row order matches the all-at-once
    # path's globally-sorted groupby output.
    section("Aggregating to NUTS3")
    agg_eu = pd.concat(agg_parts, ignore_index=True)
    agg_eu = agg_eu.sort_values(
        ["nuts3", "building_class"]).reset_index(drop=True)
    agg_eu["nuts3"] = agg_eu["nuts3"].astype(str)
    agg_eu["building_class"] = agg_eu["building_class"].astype(str)
    del agg_parts
    gc.collect()

    agg_eu.to_csv(paths["out_nuts3"], index=False)
    agg_eu.to_csv(paths["country_out_nuts3"], index=False)
    print(f"  NUTS3 aggregation saved: {paths['out_nuts3']}")
    print(f"  mirrored to:             {paths['country_out_nuts3']}")

    comparison = compare_to_existing_model(agg_eu, cfg)
    if not comparison.empty:
        comparison.to_csv(paths["out_comparison"], index=False)
        comparison.to_csv(paths["country_out_comparison"], index=False)
        print(f"  Model comparison saved:  {paths['out_comparison']}")
        print(f"  mirrored to:             {paths['country_out_comparison']}")

    # make_diagnostics ignores its first argument (placeholder PDF only).
    make_diagnostics(None, paths["out_pdf"])
    try:
        import shutil
        shutil.copy(paths["out_pdf"], paths["country_out_pdf"])
        print(f"  mirrored diagnostics PDF to: {paths['country_out_pdf']}")
    except Exception as e:
        print(f"  WARN: could not mirror PDF: {e}")

    header("Done.")
    print("Next step:")
    print(f"    python code/scripts/country_build/03_heat_intensity.py "
          f"--country {cfg.country_code}")
    return 0


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--country", required=True,
                        help="2-letter ISO country code (e.g. LU, FR, DE)")
    parser.add_argument("--per-partition", action="store_true",
                        help="Low-memory mode: classify one NUTS2 partition at "
                             "a time and stream the output parquet, instead of "
                             "loading the whole country into RAM. Required for "
                             "large countries (FR, DE) on a standard-RAM "
                             "runtime. Does not retain polygon geometry in the "
                             "output parquet (see run_per_partition docstring).")
    args = parser.parse_args()

    cfg = load_country_config(args.country)
    paths = build_paths(cfg)

    if args.per_partition:
        return run_per_partition(cfg, paths)

    header(f"{cfg.country_name} ({cfg.country_code}) — building classification")

    # Load EUBUCCO from one or more NUTS2 partitions
    eubucco = load_eubucco(paths["eubucco_sources"])

    # Inspect EUBUCCO columns to pick the right ones
    height_col_eu = None
    type_col_eu = None
    for c in eubucco.columns:
        lc = c.lower()
        if "height" in lc and height_col_eu is None:
            height_col_eu = c
        if lc in ("type", "building_type") or "type" in lc:
            type_col_eu = c if type_col_eu is None else type_col_eu
    print(f"\nEUBUCCO height column detected: {height_col_eu}")
    print(f"EUBUCCO type column detected:   {type_col_eu}")

    eubucco = add_derived_attrs(eubucco, "EUBUCCO",
                                height_col=height_col_eu,
                                type_col=type_col_eu, cfg=cfg)

    # Attach NUTS3 region to each building (trivial for single-region
    # countries; spatial join against GISCO for multi-region countries)
    eubucco = assign_nuts3(eubucco, cfg)

    # Aggregate + compare
    agg_eu = aggregate_to_nuts3(eubucco, "EUBUCCO")
    agg_eu.to_csv(paths["out_nuts3"], index=False)
    agg_eu.to_csv(paths["country_out_nuts3"], index=False)
    print(f"\nNUTS3 aggregation saved: {paths['out_nuts3']}")
    print(f"  mirrored to:            {paths['country_out_nuts3']}")

    comparison = compare_to_existing_model(agg_eu, cfg)
    if not comparison.empty:
        comparison.to_csv(paths["out_comparison"], index=False)
        comparison.to_csv(paths["country_out_comparison"], index=False)
        print(f"Model comparison saved:  {paths['out_comparison']}")
        print(f"  mirrored to:           {paths['country_out_comparison']}")

    # Save building-level outputs
    section(f"Saving classified buildings (EUBUCCO) — {cfg.country_code}")
    save_cols = ["geometry", "footprint_area_m2", "height_m",
                 "floors_estimated", "building_type_raw",
                 "building_class", "heated_floor_area_m2",
                 "construction_year", "nuts3"]
    missing = [c for c in save_cols if c not in eubucco.columns]
    if "construction_year" in missing:
        print("  WARN ====================================================")
        print("  WARN: 'construction_year' is NOT in the EUBUCCO dataframe.")
        print("  WARN: Script 03 will fall back to unknown-cohort intensities")
        print("  WARN: for every building. Per-vintage TABULA lookups disabled.")
        print("  WARN: Check that the EUBUCCO parquet schema still exposes a")
        print("  WARN: 'construction_year' column (column name may have changed).")
        print("  WARN ====================================================")
    save_cols = [c for c in save_cols if c in eubucco.columns]
    eubucco[save_cols].to_parquet(paths["out_parquet"], index=False)
    print(f"  saved {len(eubucco):,} buildings to {paths['out_parquet']}")
    print(f"  columns written: {list(save_cols)}")

    make_diagnostics(eubucco, paths["out_pdf"])
    # Mirror the diagnostics PDF to the country folder
    try:
        import shutil
        shutil.copy(paths["out_pdf"], paths["country_out_pdf"])
        print(f"  mirrored diagnostics PDF to: {paths['country_out_pdf']}")
    except Exception as e:
        print(f"  WARN: could not mirror PDF: {e}")

    header("Done.")
    print("Next step:")
    print(f"    python code/scripts/country_build/03_heat_intensity.py "
          f"--country {cfg.country_code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
