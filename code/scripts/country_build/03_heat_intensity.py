"""
03_heat_intensity.py — Per-m² heat demand calculation (country-parameterised)
================================================================================

PURPOSE
-------
Take the classified buildings produced by 02_classify.py and attach a per-m²
annual heat-demand intensity (kWh/m²/year) to each building. Aggregate by
building class and vintage cohort. Reconcile total against three external
benchmarks:
  - Hotmaps 2015 national baseline:  8.27 TWh/yr
  - EU BSO 2021 weighted average:    derived from per-cohort × stock-weight
  - Odyssee-Mure 2021 LU residential: ~7.2 TWh/yr (back-calculated)

DATA SOURCES (decided May 2026, see literature/intensity_source_methodology.md)
-------------------------------------------------------------------------------
Primary:  TABULA Belgium synthetical-average per-cohort intensities, used as
          climate-corrected proxy for Luxembourg (BE → LU multiplier 1.112)
          File: code/data/raw/tabula/be_intensities.csv

Cross-validation: EU Building Stock Observatory (Dec 2025 release), national-
          average per-cohort intensity for LU. Used only for reconciliation,
          NOT for per-building values.
          File: code/data/raw/eu_bso/lu_intensity.csv

National parameters: HDD ratio, retrofit-state distribution, DHW component.
          File: code/data/raw/lu_national/lu_climate_retrofit.csv

METHODOLOGY
-----------
For each building in LU_buildings_classified.parquet:

  1. Map `construction_year` -> vintage cohort:
        pre-1945 | 1946-1970 | 1971-1990 | 1991-2010 | 2011-2020 | post-2020
     Buildings with missing year go to 'unknown' (handled in step 5).

  2. Look up base space-heating intensity from TABULA Belgium for
     (building_class, cohort). Belgian values are calibrated to ~2,900 HDD/yr.

  3. Apply climate correction: x (HDD_LU / HDD_BE) = x 1.112
     Rationale: useful space-heating demand scales approximately linearly with
     HDD (EN ISO 13790 seasonal method). LU is ~11% colder than BE on average.

  4. Add DHW intensity (TABULA convention, ~22 kWh/m2 SFH, ~19 kWh/m2 MFH).
     DHW is roughly climate-insensitive; not multiplied by HDD ratio.

  5. Apply retrofit-state blending:
        intensity = (0.55 x intensity_original
                   + 0.35 x intensity_original x 0.65   # standard refurb
                   + 0.10 x intensity_original x 0.35)  # advanced refurb
     Weights derived from Odyssee-Mure LU 2024 + STATEC building stock 2021.

  6. Multiply by heated floor area = footprint x floors x 0.85 to get
     annual heat demand in kWh.

  7. For 'unknown' cohort buildings (no construction_year): assign the
     LU national-stock-weighted average intensity for the building class.

  8. For NON_RESIDENTIAL: use EU BSO 2025 LU non-res average (~140 kWh/m2).
     This is a rough placeholder - non-residential breakdown by sector
     (office / retail / industrial / education / health) is deferred to
     subsequent work.

OUTPUTS
-------
  - LU_heat_intensity_summary.csv   per-class + per-cohort heat demand totals
  - LU_reconciliation_with_hotmaps.csv  3-way comparison (this model / Hotmaps
                                         / EU BSO / Odyssee-Mure)
  - LU_heat_demand_nuts3.csv        per-(NUTS3, building_class) heat demand in
                                     MWh/yr. Small, git-committed; this is the
                                     model interface consumed by the Monte
                                     Carlo (BuildingStock.build_building_stock_
                                     bottomup). The per-building parquet below
                                     is archived on Drive and not committed.
  - LU_buildings_with_heat_demand.parquet  augmented parquet with intensity
                                            and heat demand columns

NO CALIBRATION TO HOTMAPS APPLIED
---------------------------------
Per decision May 2026 (Ali / Abdul), this script reports the bottom-up
TABULA-derived total AS-IS, alongside the Hotmaps / EU BSO / Odyssee-Mure
benchmarks. If the bottom-up total deviates >20% from Hotmaps, that's a
methodology finding to disclose in the paper, not a bug to silently correct.

CITATIONS
---------
  - Cyx W., Renders N., Van Holm M., Verbeke S. (2011). IEE TABULA - Belgian
    Scientific Report. VITO 2011/TEM/R/091763.
    episcope.eu/fileadmin/tabula/public/docs/scientific/BE_TABULA_ScientificReport_VITO.pdf
  - Loga T., Stein B., Diefenbach N. (2016). TABULA building typologies in 20
    European countries. Energy & Buildings 132:4-12.
    DOI 10.1016/j.enbuild.2016.06.094
  - European Commission, DG Energy. EU Building Stock Observatory database
    (Dec 2025 release). building-stock-observatory.energy.ec.europa.eu/
  - ODYSSEE-MURE. Luxembourg country profile, 2024 update.
    odyssee-mure.eu/publications/efficiency-trends-policies-profiles/luxembourg
  - Eurostat nrg_chdd_a: Cooling and heating degree days by country (annual,
    base temperature 15 C, source JRC AGRI4CAST).
"""

from __future__ import annotations

import os
import sys
import warnings
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# Paths
REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = REPO_ROOT / "code" / "data" / "raw"

# Import country config loader
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))
from CountryConfig import CountryConfig, load_country_config  # noqa: E402


def build_paths(cfg: CountryConfig) -> dict:
    """Per-country input and output paths."""
    cc = cfg.country_code
    cc_lower = cfg.cc_lower
    cname = cfg.country_name
    processed = REPO_ROOT / "code" / "data" / "processed" / cc_lower
    country = REPO_ROOT / "countries" / cname / "data"
    # TABULA file from config; the BSO and national-params files follow a
    # naming convention `{cc_lower}_intensity.csv` and `{cc_lower}_climate_retrofit.csv`
    # under raw subfolders. Falls back to LU's names for backward compat.
    bso_file_path = RAW_DIR / "eu_bso" / f"{cc_lower}_intensity.csv"
    national_file_path = RAW_DIR / f"{cc_lower}_national" / f"{cc_lower}_climate_retrofit.csv"
    return {
        "in_parquet": processed / f"{cc}_buildings_classified.parquet",
        "tabula_file": REPO_ROOT / cfg.tabula_intensities_file,
        "bso_file": bso_file_path,
        "national_file": national_file_path,
        "out_summary":   processed / f"{cc}_heat_intensity_summary.csv",
        "out_reconcile": processed / f"{cc}_reconciliation_with_hotmaps.csv",
        "out_heat_nuts3": processed / f"{cc}_heat_demand_nuts3.csv",
        "out_parquet_augmented": processed / f"{cc}_buildings_with_heat_demand.parquet",
        "country_summary":   country / f"{cc}_heat_intensity_summary.csv",
        "country_reconcile": country / f"{cc}_reconciliation_with_hotmaps.csv",
        "country_heat_nuts3": country / f"{cc}_heat_demand_nuts3.csv",
        "processed_dir": processed,
        "country_dir": country,
    }


def section(title: str) -> None:
    print(f"\n-- {title} {'-' * max(2, 60 - len(title) - 4)}")


def assign_cohort(year) -> str:
    """Map an EUBUCCO construction_year to a TABULA-compatible cohort label."""
    if pd.isna(year):
        return "unknown"
    y = int(year)
    if y < 1945:
        return "pre-1945"
    if y < 1971:
        return "1946-1970"
    if y < 1991:
        return "1971-1990"
    if y < 2011:
        return "1991-2010"
    if y < 2021:
        return "2011-2020"
    return "post-2020"


def load_tabula(tabula_file: Path) -> pd.DataFrame:
    """Read TABULA per-class per-cohort intensities (one country's data)."""
    return pd.read_csv(tabula_file, comment="#")


def load_bso(bso_file: Path) -> pd.DataFrame:
    """Read EU BSO national-average per-cohort intensities."""
    return pd.read_csv(bso_file, comment="#")


# ── Vectorised, streaming intensity computation ──────────────────────────────
# Per-building intensity is a deterministic function of (building_class,
# cohort): only 4 classes x 7 cohorts = 28 combinations. We build that 28-row
# lookup once and vectorise the assignment with a merge. At country scale
# (FR ~53 M buildings) a per-row .apply() would take hours and a whole-file
# load would exhaust RAM; streaming batches keeps peak memory at ~one batch.
_HEAT_BATCH_SIZE = int(os.environ.get("EUHB_HEAT_BATCH", 1_000_000))

_COHORTS = ["pre-1945", "1946-1970", "1971-1990", "1991-2010",
            "2011-2020", "post-2020", "unknown"]


def _cohort_vectorized(construction_year: pd.Series) -> np.ndarray:
    """Array form of assign_cohort(): construction_year -> cohort label.

    Identical boundaries to assign_cohort(); construction_year values are
    whole years so the float comparisons here match its int() truncation.
    """
    yr = pd.to_numeric(construction_year, errors="coerce").to_numpy("float64")
    return np.select(
        [np.isnan(yr), yr < 1945, yr < 1971, yr < 1991, yr < 2011, yr < 2021],
        ["unknown", "pre-1945", "1946-1970", "1971-1990",
         "1991-2010", "2011-2020"],
        default="post-2020",
    )


def build_intensity_lookup(tabula: pd.DataFrame, bso: pd.DataFrame,
                            cfg: CountryConfig):
    """Build the (building_class, cohort) -> (intensity, source) lookup.

    Reproduces the original per-row lookup_intensity() plus the unknown-cohort
    fallback exactly, as a 28-row table that can be merged onto the building
    set. Verified byte-identical to the row form on Luxembourg.

    Returns (lookup_df, retrofit_blend, class_fallbacks).
    """
    blend = (cfg.retrofit_share_original * 1.0
             + cfg.retrofit_share_standard * cfg.retrofit_factor_standard
             + cfg.retrofit_share_advanced * cfg.retrofit_factor_advanced)
    # Optional operational-regime deflator (Mediterranean cluster). When
    # set in the YAML it multiplies the SPACE-HEATING component only;
    # DHW is occupancy-driven and not affected by partial-room / lower-T
    # heating behaviour. Defaults to 1.0 (no change) for countries where
    # the TABULA reference regime matches actual operation (G1 cold +
    # temperate countries).
    deflator = (cfg.comfort_regime_deflator
                if cfg.comfort_regime_deflator is not None else 1.0)
    nonres = cfg.non_residential_intensity

    # Per-class TABULA selection. When cfg.tabula_class_mix is set,
    # different building classes can be sourced from different TABULA
    # files with different climate multipliers (e.g. EE/LT pull SFH from
    # the Swedish wooden-house typology and MFH from the Polish panel-
    # block typology). Each class_specs entry carries an indexed TABULA
    # frame, a climate multiplier, and a source-tag string for traceability.
    default_src_tag = f"tabula_{cfg.tabula_source_country.lower()}_proxy"
    default_tab_indexed = tabula.set_index(["building_class", "cohort"])

    repo_root = Path(__file__).resolve().parents[3]

    class_specs: dict[str, tuple] = {}
    for cls in ("SFH", "MFH_LOW", "MFH_HIGH"):
        mix_entry = (cfg.tabula_class_mix or {}).get(cls)
        if mix_entry:
            f = Path(mix_entry["file"])
            if not f.is_absolute():
                f = repo_root / f
            tab_cls = load_tabula(f).set_index(["building_class", "cohort"])
            clim_cls = float(mix_entry["climate_multiplier"])
            src_cls = str(mix_entry["source_country"]).lower()
            tag_cls = f"tabula_{src_cls}_class_mix"
            class_specs[cls] = (tab_cls, clim_cls, tag_cls)
        else:
            class_specs[cls] = (default_tab_indexed,
                                cfg.climate_multiplier, default_src_tag)

    def _direct(cls, cohort):
        tab_cls, clim_cls, _ = class_specs[cls]
        tr = tab_cls.loc[(cls, cohort)]
        sh = float(tr["sh_intensity_kwh_m2_yr"]) * clim_cls * blend * deflator
        dhw = float(tr["dhw_intensity_kwh_m2_yr"])
        return sh + dhw

    # Unknown-cohort fallback: BSO stock-weighted average over known cohorts.
    weight_col = next((c for c in bso.columns
                       if c.startswith("stock_pct_")), None)
    if weight_col is None:
        raise ValueError(
            f"EU BSO file has no 'stock_pct_*' column; columns: "
            f"{list(bso.columns)}")
    bso_weights = bso.set_index("cohort")[weight_col] / 100.0

    class_fallbacks = {}
    for cls in ("SFH", "MFH_LOW", "MFH_HIGH"):
        tab_cls, _, _ = class_specs[cls]
        wsum = 0.0
        for cohort, weight in bso_weights.items():
            if (cls, cohort) in tab_cls.index:
                wsum += weight * _direct(cls, cohort)
        class_fallbacks[cls] = wsum

    rows = []
    for cls in ("SFH", "MFH_LOW", "MFH_HIGH", "NON_RESIDENTIAL"):
        for cohort in _COHORTS:
            if cls == "NON_RESIDENTIAL":
                rows.append((cls, cohort, nonres, "non_res_flat_rate"))
            else:
                tab_cls, _, src_tag_cls = class_specs[cls]
                if cohort != "unknown" and (cls, cohort) in tab_cls.index:
                    rows.append((cls, cohort, _direct(cls, cohort),
                                 src_tag_cls))
                else:
                    rows.append((cls, cohort, class_fallbacks[cls],
                                 "tabula_stock_weighted_unknown_cohort"))
    lookup = pd.DataFrame(rows, columns=["building_class", "cohort",
                                         "intensity_kwh_m2_yr",
                                         "intensity_source"])
    return lookup, blend, class_fallbacks


def stream_intensity(in_parquet: Path, out_aug: Path,
                     lookup: pd.DataFrame,
                     area_correction: float = 1.0,
                     region_map: dict | None = None,
                     default_region: str | None = None) -> tuple[dict, dict]:
    """Stream the classified parquet in batches: attach intensity + heat
    demand to each building, write the augmented parquet, and accumulate
    aggregates. Peak memory is ~one batch.

    Returns (acc, nuts_acc):
      acc      -> (building_class, cohort) -> [n, sum_heated_m2,
                  sum_intensity, sum_demand_kwh]
      nuts_acc -> (nuts3, building_class)  -> [n, sum_demand_kwh]

    nuts_acc feeds the small, git-committed {CC}_heat_demand_nuts3.csv that
    the Monte Carlo consumes (the per-building parquet is archived on Drive,
    not committed). Empty if the classified parquet has no 'nuts3' column.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(in_parquet)
    writer = None
    acc = {}
    nuts_acc = {}
    total = 0
    for batch in pf.iter_batches(batch_size=_HEAT_BATCH_SIZE):
        chunk = batch.to_pandas()
        if "construction_year" not in chunk.columns:
            chunk["construction_year"] = np.nan
        chunk["cohort"] = _cohort_vectorized(chunk["construction_year"])
        # Vectorised intensity assignment. A left merge keeps row order and,
        # since the lookup covers every (class, cohort), matches every building
        # exactly once. When the lookup is region-split (carries a 'region'
        # column), each building is first tagged with a region from its NUTS3
        # code (default_region otherwise) and the merge keys on region too.
        if "region" in lookup.columns:
            nuts_col = ("nuts3" if "nuts3" in chunk.columns
                        else ("nuts_id" if "nuts_id" in chunk.columns else None))
            if nuts_col is not None and region_map:
                chunk["region"] = (chunk[nuts_col].map(region_map)
                                   .fillna(default_region))
            else:
                chunk["region"] = default_region
            chunk = chunk.merge(lookup, on=["region", "building_class", "cohort"],
                                how="left")
        else:
            chunk = chunk.merge(lookup, on=["building_class", "cohort"],
                                how="left")
        # Optional EUBUCCO area correction: shrinks per-building heated area
        # by a documented national-census-grounded factor. Both the area
        # column and the demand column scale by the same factor, so per-m^2
        # intensity reporting stays accurate. Defaults to 1.0 (no change).
        if area_correction != 1.0:
            chunk["heated_floor_area_m2"] = (
                chunk["heated_floor_area_m2"] * area_correction)
        chunk["heat_demand_kwh_yr"] = (
            chunk["intensity_kwh_m2_yr"] * chunk["heated_floor_area_m2"])

        g = chunk.groupby(["building_class", "cohort"], observed=True).agg(
            n=("intensity_kwh_m2_yr", "size"),
            sh=("heated_floor_area_m2", "sum"),
            si=("intensity_kwh_m2_yr", "sum"),
            sd=("heat_demand_kwh_yr", "sum"))
        for key, r in g.iterrows():
            a = acc.setdefault(key, [0, 0.0, 0.0, 0.0])
            a[0] += int(r["n"])
            a[1] += float(r["sh"])
            a[2] += float(r["si"])
            a[3] += float(r["sd"])

        # Per-(NUTS3, class) heat-demand accumulation for the committed CSV.
        if "nuts3" in chunk.columns:
            gn = chunk.groupby(["nuts3", "building_class"],
                               observed=True).agg(
                n=("heat_demand_kwh_yr", "size"),
                sd=("heat_demand_kwh_yr", "sum"))
            for key, r in gn.iterrows():
                a = nuts_acc.setdefault(key, [0, 0.0])
                a[0] += int(r["n"])
                a[1] += float(r["sd"])

        # Stable Arrow schema across batches: text columns as 'string'.
        for c in ("building_class", "cohort", "intensity_source",
                  "nuts3", "building_type_raw"):
            if c in chunk.columns:
                chunk[c] = chunk[c].astype("string")
        out_table = pa.Table.from_pandas(chunk, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(out_aug, out_table.schema)
        writer.write_table(out_table)
        total += len(chunk)
        print(f"  processed {total:,} buildings")

    if writer is not None:
        writer.close()
    print(f"  augmented parquet written: {total:,} buildings -> {out_aug.name}")
    return acc, nuts_acc


def aggregate_results(acc: dict, bso: pd.DataFrame, cfg: CountryConfig):
    """Build the per-(class,cohort) summary and the reconciliation table from
    the streamed accumulators (see stream_intensity). Output columns and row
    order match the previous groupby-based implementation.
    """
    rows = []
    for (cls, cohort), (n, sh, si, sd) in acc.items():
        rows.append({
            "building_class": cls,
            "cohort": cohort,
            "n_buildings": n,
            "total_heated_area_m2": sh,
            "mean_intensity_kwh_m2": (si / n) if n else float("nan"),
            "total_demand_kwh_yr": sd,
        })
    summary = pd.DataFrame(rows).sort_values(
        ["building_class", "cohort"]).reset_index(drop=True)
    summary["total_demand_twh_yr"] = summary["total_demand_kwh_yr"] / 1e9

    bottom_up_twh = summary["total_demand_twh_yr"].sum()
    res = summary[summary["building_class"] != "NON_RESIDENTIAL"]
    bottom_up_res_twh = res["total_demand_twh_yr"].sum()
    total_heated_all = summary["total_heated_area_m2"].sum()
    total_res_area_m2 = res["total_heated_area_m2"].sum()

    weight_col = next((c for c in bso.columns
                       if c.startswith("stock_pct_")), None)
    bso = bso.copy()
    bso["weighted_kwh_m2"] = (bso[weight_col] / 100.0
                              * bso["bso_intensity_kwh_m2_yr"])
    bso_avg_intensity = bso["weighted_kwh_m2"].sum()
    bso_implied_total_twh = bso_avg_intensity * total_res_area_m2 / 1e9

    bench = cfg.reconciliation_benchmarks
    hotmaps_twh = bench.get("hotmaps", {}).get("total_twh")
    odyssee_twh = bench.get("odyssee_mure", {}).get("total_twh")

    def safe_kwh_m2(twh, area):
        return (round(twh * 1e9 / area, 1)
                if (twh is not None and area > 0) else None)

    proxy_label = (cfg.tabula_source_country
                   if cfg.tabula_source_country != cfg.country_code
                   else "direct")

    rows = [
        {"source": f"Bottom-up: EUBUCCO + TABULA {proxy_label} "
                   f"(this model, all classes)",
         "twh_yr": round(bottom_up_twh, 3),
         "kwh_m2_yr_avg": safe_kwh_m2(bottom_up_twh, total_heated_all),
         "note": "TABULA \u00d7 HDD ratio \u00d7 retrofit blend + DHW; "
                 "non-res flat"},
        {"source": "Bottom-up: residential only (excludes NON_RESIDENTIAL)",
         "twh_yr": round(bottom_up_res_twh, 3),
         "kwh_m2_yr_avg": safe_kwh_m2(bottom_up_res_twh, total_res_area_m2),
         "note": "Comparable to Hotmaps + EU BSO + Odyssee residential "
                 "figures"},
    ]
    if hotmaps_twh is not None:
        rows.append({
            "source": f"Hotmaps {bench['hotmaps'].get('year', '?')} "
                      f"baseline (existing model)",
            "twh_yr": hotmaps_twh,
            "kwh_m2_yr_avg": safe_kwh_m2(hotmaps_twh, total_res_area_m2),
            "note": "Residential baseline (see "
                    "cfg.reconciliation_benchmarks.hotmaps)"})
    rows.append({
        "source": f"EU BSO {bench.get('eu_bso', {}).get('year', '?')} "
                  f"weighted-avg implied total",
        "twh_yr": round(bso_implied_total_twh, 3),
        "kwh_m2_yr_avg": round(bso_avg_intensity, 1),
        "note": f"BSO per-cohort intensities \u00d7 {cfg.country_code} stock "
                f"weights \u00d7 our residential area"})
    if odyssee_twh is not None:
        rows.append({
            "source": f"Odyssee-Mure {bench['odyssee_mure'].get('year', '?')} "
                      f"{cfg.country_code} residential (back-calculated)",
            "twh_yr": odyssee_twh,
            "kwh_m2_yr_avg": safe_kwh_m2(odyssee_twh, total_res_area_m2),
            "note": bench["odyssee_mure"].get("note", "")})
    reconcile = pd.DataFrame(rows)
    return summary, reconcile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", required=True,
                        help="2-letter ISO country code (e.g. LU, FR, DE)")
    parser.add_argument("--no-corrections", action="store_true",
                        help="Run the NAKED bottom-up: disable all four documented "
                             "source-grounded corrections (comfort_regime deflator, "
                             "eubucco area_correction, tabula class_mix_proxy, and the "
                             "tabula_reference_hdd / Option-B climate adjustment). "
                             "Diagnostic only: quantifies how much each correction moves "
                             "the bottom-up vs the uncorrected snapshot. Writes outputs "
                             "with a _naked suffix so corrected results are not overwritten.")
    args = parser.parse_args()

    cfg = load_country_config(args.country)

    if args.no_corrections:
        # Revert every documented correction to its pre-correction value so the
        # build reproduces the uncorrected ("naked") snapshot. Each lever is
        # neutralised at its identity:
        #   comfort_regime.deflator        -> 1.0 (no operational deflation)
        #   eubucco.area_correction        -> None (no area rescale)
        #   tabula.class_mix               -> None (single-proxy TABULA)
        #   climate_multiplier             -> hdd_country / hdd_proxy
        #       (removes the Option-B tabula_reference_hdd adjustment; reverts to
        #        the plain proxy-HDD ratio, = 1.0 for direct-TABULA countries)
        naked_clim = cfg.hdd_country / cfg.hdd_proxy
        print("\n[--no-corrections] NAKED build: disabling the 4 documented corrections")
        print(f"    comfort_regime.deflator : {cfg.comfort_regime_deflator} -> 1.0")
        print(f"    eubucco.area_correction : {cfg.eubucco_area_correction} -> None")
        print(f"    tabula.class_mix        : "
              f"{'set' if cfg.tabula_class_mix else None} -> None")
        print(f"    climate_multiplier      : {cfg.climate_multiplier:.3f} -> "
              f"{naked_clim:.3f} (hdd_country/hdd_proxy)")
        cfg.comfort_regime_deflator = None
        cfg.eubucco_area_correction = None
        cfg.tabula_class_mix = None
        cfg.climate_multiplier = naked_clim

    paths = build_paths(cfg)
    if args.no_corrections:
        # Redirect every output to a *_naked.* sibling so the corrected files
        # produced by a normal run are preserved for side-by-side comparison.
        for k in ("out_summary", "out_reconcile", "out_heat_nuts3",
                  "out_parquet_augmented", "country_summary",
                  "country_reconcile", "country_heat_nuts3"):
            p = paths.get(k)
            if p is not None:
                paths[k] = p.with_name(p.stem + "_naked" + p.suffix)

    print("=" * 60)
    print(f"03_heat_intensity.py — {cfg.country_name} ({cfg.country_code}) "
          f"per-m² heat demand")
    print("=" * 60)
    print("\nData sources:")
    print(f"  TABULA {cfg.tabula_source_country}: {paths['tabula_file']}")
    print(f"  EU BSO {cfg.country_code}:    {paths['bso_file']}")
    print(f"  national:           {paths['national_file']}")

    if not paths["in_parquet"].exists():
        print(f"\nERROR: input not found at {paths['in_parquet']}")
        print(f"Run 02_classify.py --country {cfg.country_code} first.")
        return 1

    for f in (paths["tabula_file"], paths["bso_file"], paths["national_file"]):
        if not f.exists():
            print(f"\nERROR: source data not found: {f}")
            return 1

    section("Loading source data")
    tabula = load_tabula(paths["tabula_file"])
    bso = load_bso(paths["bso_file"])
    print(f"  TABULA {cfg.tabula_source_country} rows: {len(tabula)}")
    print(f"  BSO {cfg.country_code} rows:             {len(bso)}")

    section("Computing per-building intensities (vectorised, streaming)")
    nuts3_to_region = None
    default_region = None
    if cfg.tabula_region_split and not args.no_corrections:
        # Climate region-split: build one (class, cohort) sub-lookup per region
        # from that region's TABULA file + per-region climate multiplier, tag
        # each with a 'region' column, and concatenate. Buildings are mapped to
        # a region by NUTS3 in stream_intensity (default_region otherwise).
        import dataclasses
        rs = cfg.tabula_region_split
        default_region = rs["default_region"]
        sub_lookups, nuts3_to_region, fallbacks = [], {}, {}
        blend = None
        for rname, entry in rs["regions"].items():
            rtab = load_tabula(REPO_ROOT / entry["file"])
            rcfg = dataclasses.replace(
                cfg, climate_multiplier=float(entry["climate_multiplier"]),
                tabula_class_mix=None, tabula_region_split=None)
            rlook, blend, rfb = build_intensity_lookup(rtab, bso, rcfg)
            rlook = rlook.copy()
            rlook["region"] = rname
            sub_lookups.append(rlook)
            fallbacks.update({f"{rname}:{k}": v for k, v in rfb.items()})
            for code in entry["nuts3"]:
                nuts3_to_region[code] = rname
            print(f"  region {rname:9s} <- {entry['source_country']} TABULA "
                  f"(clim {float(entry['climate_multiplier']):.3f}, "
                  f"{len(entry['nuts3'])} NUTS3)")
        lookup = pd.concat(sub_lookups, ignore_index=True)
        print(f"  region-split: default '{default_region}', "
              f"{len(nuts3_to_region)} NUTS3 mapped to a region")
    else:
        lookup, blend, fallbacks = build_intensity_lookup(tabula, bso, cfg)
        print(f"  climate multiplier ({cfg.country_code}/"
              f"{cfg.tabula_source_country}): {cfg.climate_multiplier:.3f}")
    print(f"  retrofit blend factor:     {blend:.3f}")
    if cfg.comfort_regime_deflator is not None:
        print(f"  comfort-regime deflator:   {cfg.comfort_regime_deflator:.3f} "
              f"(SH only; DHW unchanged)")
        print(f"    source: {cfg.comfort_regime_source}")
    area_correction = (cfg.eubucco_area_correction
                       if cfg.eubucco_area_correction is not None else 1.0)
    if area_correction != 1.0:
        print(f"  EUBUCCO area correction:   {area_correction:.3f} "
              f"(scales heated area + demand; per-m2 intensity unchanged)")
        print(f"    source: {cfg.eubucco_area_correction_source}")
    print(f"  non-residential flat rate: {cfg.non_residential_intensity} "
          f"kWh/m2/yr")
    for _cls, _val in fallbacks.items():
        print(f"  unknown-cohort fallback {_cls}: {_val:.1f} kWh/m2/yr")

    paths["processed_dir"].mkdir(parents=True, exist_ok=True)
    paths["country_dir"].mkdir(parents=True, exist_ok=True)
    acc, nuts_acc = stream_intensity(paths["in_parquet"],
                                     paths["out_parquet_augmented"], lookup,
                                     area_correction=area_correction,
                                     region_map=nuts3_to_region,
                                     default_region=default_region)

    section("Aggregating results")
    summary, reconcile = aggregate_results(acc, bso, cfg)

    total_n = int(summary["n_buildings"].sum())
    known_n = int(summary.loc[summary["cohort"] != "unknown",
                              "n_buildings"].sum())
    pct_year = known_n / total_n * 100 if total_n else 0.0
    print(f"\n  buildings with a known construction cohort: "
          f"{known_n:,} / {total_n:,} ({pct_year:.2f}%)")
    if 0 < pct_year < 5:
        print("  WARN: construction_year coverage is very low; the result is")
        print("  WARN: dominated by the stock-weighted unknown-cohort")
        print("  WARN: fallback intensities, not a per-vintage calculation.")
        print("  WARN: Reviewers should be told this in the paper.")

    print("\nPer-class \u00d7 per-cohort heat demand:")
    print(summary.to_string(index=False))
    print("\nReconciliation:")
    print(reconcile.to_string(index=False))

    bottom_up_res_rows = reconcile.loc[
        reconcile["source"].str.contains("residential only"), "twh_yr"]
    if not bottom_up_res_rows.empty:
        bottom_up_res = bottom_up_res_rows.iloc[0]
        hotmaps_twh = cfg.reconciliation_benchmarks.get(
            "hotmaps", {}).get("total_twh")
        if hotmaps_twh is not None:
            delta_pct = (bottom_up_res - hotmaps_twh) / hotmaps_twh * 100
            print(f"\nResidential bottom-up vs Hotmaps: "
                  f"{bottom_up_res:.2f} vs {hotmaps_twh:.2f} TWh "
                  f"({delta_pct:+.1f}%)")
            if abs(delta_pct) <= 15:
                print("  [OK] within \u00b115% of Hotmaps \u2014 consistent")
            elif abs(delta_pct) <= 25:
                print("  [acceptable] within \u00b125% of Hotmaps \u2014 "
                      "document the gap")
            else:
                print("  [investigate] >25% off Hotmaps \u2014 check before "
                      "scale-out")

    section("Saving outputs")
    summary.to_csv(paths["out_summary"], index=False)
    print(f"  summary:        {paths['out_summary']}")
    summary.to_csv(paths["country_summary"], index=False)
    print(f"  mirrored to:    {paths['country_summary']}")
    reconcile.to_csv(paths["out_reconcile"], index=False)
    print(f"  reconciliation: {paths['out_reconcile']}")
    reconcile.to_csv(paths["country_reconcile"], index=False)
    print(f"  mirrored to:    {paths['country_reconcile']}")

    # Per-(NUTS3, class) heat demand -- the small, git-committed CSV that the
    # Monte Carlo reads as its bottom-up demand input. heat_demand_MWh = the
    # streamed kWh sum / 1e3.
    nuts_rows = [
        {"nuts_id": nuts3, "building_class": cls,
         "n_buildings": n, "heat_demand_MWh": sd / 1e3}
        for (nuts3, cls), (n, sd) in nuts_acc.items()
    ]
    if nuts_rows:
        heat_nuts3 = (pd.DataFrame(nuts_rows)
                      .sort_values(["nuts_id", "building_class"])
                      .reset_index(drop=True))
        heat_nuts3.to_csv(paths["out_heat_nuts3"], index=False)
        print(f"  NUTS3 heat:     {paths['out_heat_nuts3']}")
        heat_nuts3.to_csv(paths["country_heat_nuts3"], index=False)
        print(f"  mirrored to:    {paths['country_heat_nuts3']}")
    else:
        print(f"  WARN: classified parquet has no 'nuts3' column; "
              f"{cfg.country_code}_heat_demand_nuts3.csv not written")

    aug_mb = paths["out_parquet_augmented"].stat().st_size / 1024 / 1024
    print(f"  augmented:      {paths['out_parquet_augmented']} ({aug_mb:.1f} MB)")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)
    print(f"\nNext: python code/scripts/country_build/04_diagnostics.py "
          f"--country {cfg.country_code}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
