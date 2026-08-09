"""
code/src/BuildingStock.py  —  Step 3a: Building stock & heat demand assembly
============================================================================
Builds the NUTS3-resolution building stock + useful heat demand table used
by every downstream module. Combines two anchor datasets with country
augmentation for the UK (not in Eurostat census).

Primary data sources:

  Hotmaps regional useful heat demand (2015 baseline):
    JRC Hotmaps Toolbox — heat & cold demand maps at NUTS3.
    Source: gitlab.com/hotmaps/heat — released under CC BY 4.0.
    Used here: total space-heating + hot-water useful energy per NUTS3
    region, in GWh/year (column HOTMAPS_HEAT_COLUMN).
    Citation: Pezzutto S. et al. (2018) "Hotmaps Project, D2.3: WP2 Report
    — Open Data Set for the EU28". European Commission H2020.

  Eurostat residential census 2021 (CENS_21DWBNO_R3):
    Number of dwellings by NUTS3 region, classified by number of dwellings
    per building (RES1, RES2, RES_GE3) — basis for our SFH vs MFH split.
    Source: Eurostat data browser, dataset CENS_21DWBNO_R3.
    URL: ec.europa.eu/eurostat/databrowser/view/CENS_21DWBNO_R3

  UK Census 2021 TS044 (Accommodation type):
    ONS table TS044 at lower-tier local authority (LTLA) resolution.
    Used because the UK is not in Eurostat's census release.
    Mapped to nearest NUTS3 equivalent by ONS LTLA -> NUTS3 lookup.
    Source: ons.gov.uk/datasets/TS044

  Eurostat GISCO NUTS 2024:
    Geometry and NUTS code list for joining the three sources above.
    Source: ec.europa.eu/eurostat/web/gisco/geodata/reference-data/
            administrative-units-statistical-units/nuts

The SFH / MFH_HIGH / OTHER classification scheme is documented in
literature/luxembourg/classification_methodology.md.

Output: code/data/processed/building_stock_nuts3.csv
        — 3,823 rows (one per NUTS3 region × building type)
"""
import numpy as np
import pandas as pd

from src.Config import (
    RAW_DIR,
    PROCESSED_DIR,
    EU_COUNTRIES,
    HOTMAPS_HEAT_COLUMN,
    MODEL_BUILDING_TYPES,
    BUILDING_TYPE_MAPPING,
    UK_TS044_PATH,
)


def load_hotmaps_regional() -> pd.DataFrame:
    """Load Hotmaps NUTS3 useful heat (GWh) for SH+HW."""
    path = RAW_DIR / "hotmaps" / "Hotmaps_regional_demand.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Hotmaps regional file not found: {path}. Run download_data.py first."
        )

    df = pd.read_csv(path, sep=";")
    print("Hotmaps_regional_demand columns:")
    print(list(df.columns))

    col_candidates = {c.lower(): c for c in df.columns}
    nuts_id_col = None
    for key in ["nuts_code", "nuts_id", "nuts code", "nuts3", "nuts"]:
        if key in col_candidates:
            nuts_id_col = col_candidates[key]
            break
    if nuts_id_col is None:
        raise RuntimeError(
            "Could not find a NUTS ID column in Hotmaps_regional_demand.csv. "
            f"Columns: {list(df.columns)}"
        )

    nuts_level_col = None
    for key in ["nuts_level", "nuts_lvl", "level"]:
        if key in col_candidates:
            nuts_level_col = col_candidates[key]
            break

    if HOTMAPS_HEAT_COLUMN not in df.columns:
        raise RuntimeError(
            f"Configured HOTMAPS_HEAT_COLUMN='{HOTMAPS_HEAT_COLUMN}' not found in Hotmaps file."
        )

    if nuts_level_col is not None:
        df = df.loc[df[nuts_level_col] == 3].copy()

    df["nuts_id"] = df[nuts_id_col].astype(str)
    if "COUNTRY_CODE" in df.columns:
        df["country"] = df["COUNTRY_CODE"].astype(str)
    else:
        df["country"] = df["nuts_id"].str[:2]

    df = df[df["country"].isin(EU_COUNTRIES)].copy()

    out = df[["nuts_id", "country", HOTMAPS_HEAT_COLUMN]].copy()
    out.rename(columns={HOTMAPS_HEAT_COLUMN: "heat_2015_GWh"}, inplace=True)
    return out


def load_eurostat_census() -> pd.DataFrame:
    """Load CENS_21DWBNO_R3 clean CSV (dwellings by building type and NUTS3)."""
    # Use the pre-cleaned CSV already in the repo
    path_clean = RAW_DIR / "eurostat" / "cens_21dwbno_r3_clean.csv"
    path_tsv   = RAW_DIR / "eurostat" / "cens_21dwbno_r3.tsv"

    if path_clean.exists():
        df = pd.read_csv(path_clean)
        df["OBS_VALUE"] = pd.to_numeric(df["2021"], errors="coerce")
    elif path_tsv.exists():
        # Fallback: parse raw TSV downloaded by download_data.py
        df_raw = pd.read_csv(path_tsv, sep="\t", comment="#")
        dim_col   = df_raw.columns[0]
        year_cols = [c for c in df_raw.columns if "2021" in str(c)]
        if len(year_cols) != 1:
            raise RuntimeError(f"Expected one 2021 column, found: {year_cols}")
        dims = df_raw[dim_col].str.split(",", expand=True)
        dims.columns = ["freq", "n_person", "building", "unit", "geo"]
        dims["OBS_VALUE"] = pd.to_numeric(df_raw[year_cols[0]], errors="coerce")
        df = dims
    else:
        raise FileNotFoundError(
            f"Eurostat census file not found. Expected:\n"
            f"  {path_clean}\n"
            f"Run download_data.py or ensure cens_21dwbno_r3_clean.csv is present."
        )

    print("Eurostat building codes found:")
    print(sorted(df["building"].dropna().unique().tolist()))

    def _map_type(b: str) -> str:
        return BUILDING_TYPE_MAPPING.get(b, "OTHER")

    df["building_type"] = df["building"].astype(str).map(_map_type)
    df["nuts_id"]  = df["geo"].astype(str)
    df["country"]  = df["nuts_id"].str[:2]
    df = df[df["country"].isin(EU_COUNTRIES)].copy()
    df = df[df["building_type"].isin(MODEL_BUILDING_TYPES)].copy()

    agg = (
        df.groupby(["nuts_id", "country", "building_type"], as_index=False)["OBS_VALUE"]
        .sum()
        .rename(columns={"OBS_VALUE": "dwellings_2021"})
    )
    print("Example aggregated Eurostat census rows:")
    print(agg.head())
    return agg


def load_uk_ts044_shares() -> dict:
    """
    Load UK-wide building-type shares from ONS TS044 (Accommodation type).

    Expected file: UK_TS044_PATH (see config), which should be the
    'csv format (Machine readable dataset)' for TS044 with:
    - area type: Lower tier local authorities
    - coverage: England and Wales

    We ignore the geography dimension and aggregate over all LTLAs to
    get national totals by accommodation type, then map those to
    SFH / MFH_HIGH / OTHER.

    Returns a dict {building_type: share} or an empty dict if the UK
    file is missing.
    """
    path = UK_TS044_PATH
    if not path.exists():
        print(
            f"[warn] UK TS044 file not found at {path}.\n"
            "       UK NUTS3 regions will fall back to building_type = 'OTHER' only."
        )
        return {}

    df = pd.read_csv(path)
    print("UK TS044 raw columns:")
    print(list(df.columns))

    # Identify accommodation-type column by looking for known labels
    obj_cols = df.select_dtypes(include="object").columns
    accom_col = None
    keywords = ["detached", "semi-detached", "terraced", "purpose-built", "tenement",
                "caravan", "mobile", "temporary", "converted", "commercial", "maisonette"]
    for col in obj_cols:
        vals = df[col].astype(str).str.lower()
        score = 0.0
        for kw in keywords:
            score += vals.str.contains(kw).mean()
        if score > 0.05:
            accom_col = col
            break

    if accom_col is None:
        raise RuntimeError(
            "Could not identify an 'accommodation type' column in UK TS044 file.\n"
            "Please ensure you exported the machine-readable CSV with an "
            "Accommodation type column, or adjust load_uk_ts044_shares()."
        )

    # Identify numeric value column as the one with the largest total
    num_cols = df.select_dtypes(include=[np.number]).columns
    if len(num_cols) == 0:
        raise RuntimeError("No numeric columns found in UK TS044 file; check format.")
    sums = df[num_cols].sum()
    value_col = sums.idxmax()

    # Aggregate by accommodation type over all geographies
    agg = (
        df.groupby(accom_col, as_index=False)[value_col]
        .sum()
        .rename(columns={accom_col: "accommodation_type", value_col: "households"})
    )

    def map_accom_to_bt(name: str) -> str:
        s = str(name).lower()
        if "detached" in s or "semi-detached" in s or "semi detached" in s or "terraced" in s:
            return "SFH"
        if ("purpose-built" in s or "purpose built" in s or "flat" in s or
                "maisonette" in s or "tenement" in s):
            return "MFH_HIGH"
        if "caravan" in s or "mobile" in s or "temporary" in s:
            return "OTHER"
        if "converted" in s or "commercial" in s or "shop" in s or "warehouse" in s or "office" in s:
            return "MFH_HIGH"
        return "OTHER"

    agg["building_type"] = agg["accommodation_type"].map(map_accom_to_bt)
    bt_agg = agg.groupby("building_type", as_index=False)["households"].sum()

    total = bt_agg["households"].sum()
    if total <= 0:
        raise RuntimeError("UK TS044 data seems to have zero households; check file.")

    bt_agg["share"] = bt_agg["households"] / total
    print("Inferred UK building-type shares from TS044:")
    print(bt_agg[["building_type", "share"]])

    shares = {}
    for bt in MODEL_BUILDING_TYPES:
        row = bt_agg[bt_agg["building_type"] == bt]
        if not row.empty:
            shares[bt] = float(row["share"].iloc[0])
        else:
            shares[bt] = 0.0
    return shares


def build_building_stock() -> None:
    hotmaps = load_hotmaps_regional()
    census_eu = load_eurostat_census()

    # Start with Eurostat census for EU27 + CH
    census_list = [census_eu]

    # Optionally add UK using TS044 national shares
    uk_shares = load_uk_ts044_shares()
    if uk_shares:
        uk_regions = hotmaps.loc[hotmaps["country"] == "UK", ["nuts_id", "country"]].drop_duplicates()
        if uk_regions.empty:
            print("No UK NUTS3 regions found in Hotmaps; skipping UK augmentation.")
        else:
            rows = []
            for _, r in uk_regions.iterrows():
                for bt in MODEL_BUILDING_TYPES:
                    share = float(uk_shares.get(bt, 0.0))
                    if share <= 0.0:
                        continue
                    rows.append(
                        {
                            "nuts_id": r["nuts_id"],
                            "country": r["country"],
                            # dwellings_2021 is arbitrary here; we just need
                            # correct *shares* per NUTS3.
                            "building_type": bt,
                            "dwellings_2021": share,
                        }
                    )
            census_uk = pd.DataFrame.from_records(rows)
            census_list.append(census_uk)

    census = pd.concat(census_list, ignore_index=True)

    # Merge with Hotmaps to get heat_2015_GWh per NUTS3
    stock = census.merge(
        hotmaps, on=["nuts_id", "country"], how="right", validate="many_to_one"
    )

    # For NUTS3 with no building-type info (e.g. missing in census), fall back to OTHER
    stock["building_type"] = stock["building_type"].fillna("OTHER")
    stock["dwellings_2021"] = stock["dwellings_2021"].fillna(0.0)

    # dwellings_2021 is a NORMALISATION BASE, not a dwelling count, and only its ratio
    # within a region is ever used. The bases differ by country: most carry a Eurostat
    # census cell, the UK branch above writes shares directly, and regions missing from
    # the census carry zero. Summing the column across Europe gives about 1,095 million,
    # roughly four times the real stock, and per country it runs from correct (France)
    # to six times high (Germany) to zero (the United Kingdom). The README quoted a
    # total from it once. Nothing downstream reads the level: heat_2015_MWh below
    # multiplies regional heat by dwellings_share alone.
    total_dwellings = stock.groupby("nuts_id")["dwellings_2021"].transform("sum")
    with np.errstate(divide="ignore", invalid="ignore"):
        stock["dwellings_share"] = np.where(
            total_dwellings > 0,
            stock["dwellings_2021"] / total_dwellings,
            1.0 / stock.groupby("nuts_id")["building_type"].transform("count"),
        )

    stock["heat_2015_MWh"] = stock["heat_2015_GWh"] * 1000.0 * stock["dwellings_share"]

    out_cols = [
        "nuts_id",
        "country",
        "building_type",
        "dwellings_2021",
        "dwellings_share",
        "heat_2015_MWh",
    ]
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "building_stock_nuts3.csv"
    stock[out_cols].to_csv(out_path, index=False)
    print(f"Saved building stock to {out_path}")


def build_hp_dh_feasibility(demand: str = "hotmaps") -> None:
    """Build the per-(NUTS3, building-type) heat-pump and district-heat
    feasibility scores.

    T6: the scores are now NUTS3-RESOLVED, not flat-by-type. Each technology's
    base score by building type is modulated by the NUTS3's urbanisation /
    heat-density, proxied by the share of dwellings in multi-family blocks
    (MFH_HIGH) -- the only density-relevant signal available in the committed
    stock (the alternative, MWh/km^2, needs NUTS3 land area, which is not carried
    forward; see literature/enhancement_tiers_design.md T6). Logic, grounded in
    the Hotmaps district-heating-potential criterion and heat-pump siting
    constraints:
      - HP feasibility DECREASES with MFH density (less outdoor space for units /
        ground loops, tighter electrical-connection constraints in dense stock);
      - DH feasibility INCREASES with MFH density (district heating is viable only
        above a linear heat-density threshold, which dense urban areas meet).
    This gives genuine cross-NUTS3 variation (dense urban vs rural) and activates
    the RQ1 'low heat-pump feasibility' condition that the flat-score version left
    inert. Demand is unaffected (feasibility enters only the technology-share
    layer), so the bottom-up reconciliation is unchanged.
    """
    stock = pd.read_csv(stock_path(demand))

    def hp_base(bt: str) -> float:
        return {"SFH": 0.9, "MFH_HIGH": 0.5}.get(bt, 0.6)

    def dh_base(bt: str) -> float:
        return {"SFH": 0.3, "MFH_HIGH": 0.8}.get(bt, 0.4)

    # Per-NUTS3 MFH dwelling share as the density/urbanisation proxy.
    dcol = "dwellings_2021" if "dwellings_2021" in stock.columns else None
    if dcol:
        piv = stock.pivot_table(index="nuts_id", columns="building_type",
                                values=dcol, aggfunc="sum").fillna(0.0)
        tot = piv.sum(axis=1).replace(0, np.nan)
        mfh_share = (piv.get("MFH_HIGH", 0.0) / tot).fillna(0.0).clip(0.0, 1.0)
    else:
        mfh_share = pd.Series(dtype=float)

    feas = (
        stock.groupby(["nuts_id", "country", "building_type"], as_index=False)
        .agg({"heat_2015_MWh": "sum"})
    )
    ms = feas["nuts_id"].map(mfh_share).fillna(0.0)
    # HP: up to -30% in fully-MFH (dense) NUTS3; DH: scales up with density,
    # capped at 0.9 (a feasibility ceiling, not a guarantee).
    feas["hp_feasibility"] = (feas["building_type"].map(hp_base)
                              * (1.0 - 0.30 * ms)).clip(0.20, 0.95).round(3)
    feas["dh_feasibility"] = (feas["building_type"].map(dh_base)
                              * (0.70 + 0.80 * ms)).clip(0.0, 0.90).round(3)

    out_path = feas_path(demand)
    feas.to_csv(out_path, index=False)
    nun = feas["nuts_id"].nunique()
    print(f"Saved NUTS3-resolved HP/DH feasibility to {out_path} "
          f"({nun} NUTS3; HP {feas.hp_feasibility.min():.2f}-{feas.hp_feasibility.max():.2f}, "
          f"DH {feas.dh_feasibility.min():.2f}-{feas.dh_feasibility.max():.2f})")


def build_building_stock_bottomup() -> None:
    """Assemble the NUTS3 building stock from the 29-country EUBUCCO + TABULA
    bottom-up build, as the alternative to the Hotmaps-derived
    build_building_stock(). Concatenates the per-country
    {CC}_heat_demand_nuts3.csv files emitted by 03_heat_intensity.py, maps the
    build's four classes onto the model's three building types, and writes
    building_stock_nuts3_bottomup.csv with the SAME schema as the Hotmaps
    version so the Monte Carlo can switch via --demand bottomup.

    Build class -> model type:
      SFH               -> SFH
      MFH_LOW + MFH_HIGH -> MFH_HIGH   (the model's single multi-family class)
      NON_RESIDENTIAL    -> OTHER      (carries ~0 heat in the residential build)

    heat_2015_MWh here holds the BOTTOM-UP baseline useful demand (EUBUCCO
    footprints x TABULA intensity x retrofit blend + DHW, after all applied
    area/comfort corrections), NOT the Hotmaps 2015 figure -- the column name is
    kept only for schema parity with the Hotmaps stock file.

    dwellings_2021 holds an estimated DWELLING count: EUBUCCO gives building
    counts, and one apartment block must not weigh the same as one detached
    house in the density proxy that drives the NUTS3 HP/DH feasibility split
    (build_hp_dh_feasibility). Building counts are converted with per-class
    dwellings-per-building factors (TABULA residential typology / Eurostat
    census averages): SFH 1, small multi-family ~6, apartment blocks ~20,
    non-residential 0 (offices are not dwellings and must not dilute the
    density denominator).

    NOTE: the Hotmaps building_stock_nuts3.csv is the reconciliation benchmark
    the country builds were validated against, so it is never overwritten; this
    writes a separate file.
    """
    CLASS_TO_TYPE = {
        "SFH": "SFH", "MFH_LOW": "MFH_HIGH", "MFH_HIGH": "MFH_HIGH",
        "NON_RESIDENTIAL": "OTHER",
    }
    # Dwellings per building by build class (TABULA typology: SFH/TH = 1 dwelling;
    # MFH typically 4-10 apartments -> 6; AB/high-rise typically 15-30 -> 20;
    # non-residential contributes no dwellings).
    DWELLINGS_PER_BUILDING = {
        "SFH": 1.0, "MFH_LOW": 6.0, "MFH_HIGH": 20.0, "NON_RESIDENTIAL": 0.0,
    }
    frames, missing = [], []
    for cc in EU_COUNTRIES:
        f = PROCESSED_DIR / cc.lower() / f"{cc}_heat_demand_nuts3.csv"
        if not f.exists():
            missing.append(cc)
            continue
        d = pd.read_csv(f)
        d["country"] = cc
        frames.append(d)
    if not frames:
        raise FileNotFoundError(
            "No {CC}_heat_demand_nuts3.csv files found; run the country builds first."
        )
    if missing:
        print(f"[warn] bottom-up demand missing for {missing} "
              f"(FR/FI/LU predate the per-NUTS3 emission -- re-run their "
              f"notebooks). Building from {len(frames)} countries.")

    raw = pd.concat(frames, ignore_index=True)
    raw["building_type"] = raw["building_class"].map(CLASS_TO_TYPE).fillna("OTHER")
    # Convert building counts to estimated dwellings at CLASS level (before the
    # MFH_LOW/MFH_HIGH merge), so the density proxy weights an apartment block
    # ~20x a detached house instead of 1x (the bug this replaces).
    raw["dwellings_est"] = raw["n_buildings"] * raw["building_class"].map(
        DWELLINGS_PER_BUILDING).fillna(0.0)
    agg = (
        raw.groupby(["nuts_id", "country", "building_type"], as_index=False)
        .agg(n_buildings=("n_buildings", "sum"),
             dwellings_2021=("dwellings_est", "sum"),
             heat_2015_MWh=("heat_demand_MWh", "sum"))
    )
    total = agg.groupby("nuts_id")["dwellings_2021"].transform("sum")
    with np.errstate(divide="ignore", invalid="ignore"):
        agg["dwellings_share"] = np.where(
            total > 0,
            agg["dwellings_2021"] / total,
            1.0 / agg.groupby("nuts_id")["building_type"].transform("count"),
        )
    out_cols = ["nuts_id", "country", "building_type", "n_buildings",
                "dwellings_2021", "dwellings_share", "heat_2015_MWh"]
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "building_stock_nuts3_bottomup.csv"
    agg[out_cols].to_csv(out_path, index=False)

    nat = (agg.groupby("country")["heat_2015_MWh"].sum() / 1e6).round(1)
    print(f"Saved bottom-up building stock to {out_path.name} "
          f"({len(agg)} rows, {agg['country'].nunique()} countries, "
          f"{agg['dwellings_2021'].sum()/1e6:.0f}M est. dwellings).")
    print("National bottom-up useful-heat totals (TWh):")
    print(nat.to_string())


def stock_path(demand: str = "hotmaps"):
    """Return the building-stock CSV path for the chosen demand basis.
    demand='hotmaps' -> building_stock_nuts3.csv (Hotmaps 2015 baseline);
    demand='bottomup' -> building_stock_nuts3_bottomup.csv (29-country build).
    """
    fname = ("building_stock_nuts3_bottomup.csv" if demand == "bottomup"
             else "building_stock_nuts3.csv")
    return PROCESSED_DIR / fname


def feas_path(demand: str = "hotmaps"):
    """Return the HP/DH feasibility CSV path matching the demand basis, so the
    stock <-> feasibility merge in the Monte Carlo stays self-consistent."""
    fname = ("hp_dh_feasibility_bottomup.csv" if demand == "bottomup"
             else "hp_dh_feasibility.csv")
    return PROCESSED_DIR / fname


def main() -> None:
    build_building_stock()
    build_hp_dh_feasibility()


# ── Entry point ───────────────────────────────────────────────────────────────
# Allows: python code/src/BuildingStock.py
if __name__ == "__main__":
    main()
