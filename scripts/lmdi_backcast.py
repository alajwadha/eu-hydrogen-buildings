"""LMDI multi-driver backcast: country-specific decomposition of residential heat
demand using Population, Dwellings, Dwelling Size, and climate-corrected Intensity.

LMDI identity (each factor multiplies; weights are implicit at 1):

  Q = Pop * (Dw/Pop) * (Area/Dw) * (Q/Area)

For the backcast ratio 2015/latest:

  Q_15/Q_lt = (Pop_15/Pop_lt) * ((Dw/Pop)_15/(Dw/Pop)_lt) *
              ((Area/Dw)_15/(Area/Dw)_lt) * ((Q/Area)_15/(Q/Area)_lt)

Intensity Q/Area is climate-corrected (heat * mean_HDD / HDD), per country.

Inputs (all in code/data/country_config/):
  heat_drivers_eurostat.csv     (27 EU: heat, HDD, electricity, pop, GDP)
  heat_drivers_national.csv     (UK + CH: same metrics from DESNZ/ONS/BFE/BFS)
  heat_drivers_demographics.csv (dwellings, household size, dwelling size)
  heat_drivers_renovation.csv   (renovation rates, mostly JRC 2012-2016)
  heat_drivers_prices.csv       (gas + electricity prices; oil/pellets/DH missing)
  heating_mix_2015_vs_2023.csv  (technology mix 2015 + 2023)
  stock_growth.csv              (per-country dwelling growth rate)

Outputs:
  code/results/lmdi_backcast.csv          per-country table
  code/results/lmdi_decomposition.csv     additive log-change contributions per driver

Backcast of the model snapshot:
  model_2015_lmdi = model_2025 * stock_ratio * size_ratio * design_intensity_ratio
where stock_ratio uses dwelling growth, size_ratio defaults 1 where no data,
and design_intensity_ratio uses observed metered ratio adjusted UP by the
conversion-efficiency improvement (~+0.5%/yr) so it reflects DESIGN (model)
intensity rather than FINAL energy.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))
import Config as C  # noqa: E402

TJ_TO_TWH = 1 / 3600.0
CONV_EFF_CORRECTION_PCT_YR = 0.5  # final energy fell ~0.5%/yr faster than useful demand


def _load_long() -> pd.DataFrame:
    """Concat the three time-series long panels into one wide-ready table."""
    parts = []
    for fn in ["heat_drivers_eurostat.csv", "heat_drivers_national.csv",
               "heat_drivers_demographics.csv"]:
        p = C.DATA_DIR / "country_config" / fn
        parts.append(pd.read_csv(p))
    return pd.concat(parts, ignore_index=True)


def _series(panel: pd.DataFrame, cc: str, metric: str) -> pd.Series:
    s = panel[(panel.country == cc) & (panel.metric == metric)] \
        .set_index("year")["value"].dropna().sort_index()
    return s


def _national_twh(csv_path: Path) -> pd.Series:
    df = pd.read_csv(csv_path)
    return df.groupby("country")["heat_2015_MWh"].sum() / 1e6


def _ratio_15_to_latest(s: pd.Series) -> tuple[float, int]:
    """Return (value_2015 / value_latest, latest_year). NaN if 2015 missing."""
    if 2015 not in s.index or len(s) < 2:
        return float("nan"), 0
    lt = int(s.index.max())
    if lt == 2015:
        return 1.0, 2015
    return float(s[2015] / s[lt]), lt


def main() -> None:
    panel = _load_long()
    hot = _national_twh(C.PROCESSED_DIR / "building_stock_nuts3.csv")
    snap = _national_twh(C.PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    # naked snapshot from previous step
    naked = pd.read_csv(ROOT / "code" / "results" / "compare_naked.csv") \
        .set_index("country")["snapshot_naked_TWh"]

    rows = []
    decomp_rows = []

    for cc in sorted(snap.index):
        heat = _series(panel, cc, "heat_residential_TJ")
        hdd  = _series(panel, cc, "hdd")
        pop  = _series(panel, cc, "population")
        dw   = _series(panel, cc, "dwellings_total")
        hh   = _series(panel, cc, "avg_household_size")
        sz   = _series(panel, cc, "avg_dwelling_size_m2")

        if heat.empty or hdd.empty or pop.empty or dw.empty:
            continue

        # Climate-correct heat to country's mean HDD over the panel.
        common = sorted(set(heat.index) & set(hdd.index))
        mean_hdd = hdd.loc[common].mean()
        heat_cc = pd.Series({y: heat[y] * (mean_hdd / hdd[y]) for y in common})

        # Latest available year for each metric
        h_15, lt_h = _ratio_15_to_latest(heat_cc)
        p_15, lt_p = _ratio_15_to_latest(pop)
        d_15, lt_d = _ratio_15_to_latest(dw)
        hh_r, _ = _ratio_15_to_latest(hh)  # household size

        # Dwelling size: only 2012 reference for most. Assume slow drift -> ratio 1.
        # If multiple years present, use real 2015 vs latest.
        if 2015 in sz.index and len(sz) > 1 and sz.index.max() > 2015:
            sz_15 = sz[2015]
            sz_lt = sz[sz.index.max()]
            size_ratio = sz_15 / sz_lt
        else:
            size_ratio = 1.0

        # Decomposition components: pop, occupancy (=Dw/Pop), size, intensity
        # Identity check: Q = Pop * (Dw/Pop) * (Area/Dw) * (Q/Area)
        # ratio Q_15/Q_lt = pop_ratio * occ_ratio * size_ratio * intensity_ratio
        # occ_ratio = (Dw/Pop)_15 / (Dw/Pop)_lt
        # We have dw_ratio = Dw_15/Dw_lt and pop_ratio = Pop_15/Pop_lt
        # so occ_ratio = dw_ratio / pop_ratio
        occ_ratio = d_15 / p_15 if (p_15 == p_15 and p_15 != 0) else float("nan")

        # Intensity ratio (Q/Area). Q observed = heat_cc.
        # Area_lt = Dw_lt * size_lt; Area_15 = Dw_15 * size_15. Ratio area_15/lt = d_15 * size_ratio.
        # intensity_ratio = (Q_15/Area_15)/(Q_lt/Area_lt) = h_15 / (d_15 * size_ratio)
        if d_15 and size_ratio:
            intensity_ratio = h_15 / (d_15 * size_ratio)
        else:
            intensity_ratio = float("nan")

        # Sanity check: pop_ratio * occ_ratio * size_ratio * intensity_ratio ~ h_15
        # = p_15 * (d_15/p_15) * size_ratio * h_15 / (d_15 * size_ratio) = h_15. OK.

        # DESIGN intensity ratio = metered + conversion-efficiency adjustment
        # Each year, final fell ~0.5%/yr more than useful; over (lt_h - 2015) yrs:
        nyr = lt_h - 2015 if lt_h > 2015 else 0
        design_intensity_ratio = intensity_ratio * (1 + CONV_EFF_CORRECTION_PCT_YR / 100) ** nyr

        # MODEL BACKCAST (stock-only, the user's preferred direction since 2015<2025):
        g = C.stock_growth_rate(cc)
        stock_only_ratio = (1 + g) ** (2015 - C.BASE_YEAR)
        snapshot_twh = float(snap[cc])
        naked_twh = float(naked.get(cc, float("nan")))
        model_2015_stock_corrected = snapshot_twh * stock_only_ratio
        model_2015_stock_naked = naked_twh * stock_only_ratio

        # MODEL BACKCAST (LMDI multi-driver, design-intensity):
        # = snapshot * (pop_ratio * occ_ratio * size_ratio * design_intensity_ratio)
        # equivalently = snapshot * d_15 * size_ratio * design_intensity_ratio
        # = snapshot * (Q_15_design / Q_lt_design)
        lmdi_ratio = d_15 * size_ratio * design_intensity_ratio if (d_15 == d_15) else float("nan")
        model_2015_lmdi_corrected = snapshot_twh * lmdi_ratio
        model_2015_lmdi_naked = naked_twh * lmdi_ratio

        # Observed Eurostat 2015 (TWh, final energy, CC) -- independent benchmark
        obs_2015_twh = heat_cc.get(2015, float("nan")) * TJ_TO_TWH if 2015 in heat_cc.index else float("nan")

        hotmaps = float(hot.get(cc, float("nan")))

        rows.append({
            "country": cc,
            "hotmaps_2015_TWh": round(hotmaps, 1),
            "observed_2015_final_CC_TWh": round(obs_2015_twh, 1),
            "snapshot_corrected_2025_TWh": round(snapshot_twh, 1),
            "snapshot_naked_2025_TWh": round(naked_twh, 1),
            "model_2015_stock_corrected": round(model_2015_stock_corrected, 1),
            "model_2015_stock_naked": round(model_2015_stock_naked, 1),
            "model_2015_lmdi_corrected": round(model_2015_lmdi_corrected, 1),
            "model_2015_lmdi_naked": round(model_2015_lmdi_naked, 1),
            "pop_ratio_15_lt": round(p_15, 4),
            "dw_ratio_15_lt": round(d_15, 4),
            "size_ratio_15_lt": round(size_ratio, 4),
            "intensity_ratio_observed": round(intensity_ratio, 4) if intensity_ratio == intensity_ratio else "",
            "intensity_ratio_design": round(design_intensity_ratio, 4) if design_intensity_ratio == design_intensity_ratio else "",
            "latest_year": lt_h,
        })

        # LMDI additive (log) decomposition: contribution of each driver to ΔlnQ
        if all(x and x == x for x in [p_15, occ_ratio, size_ratio, intensity_ratio]) and p_15 > 0:
            dln_pop  = np.log(p_15)
            dln_occ  = np.log(occ_ratio)
            dln_size = np.log(size_ratio) if size_ratio > 0 else 0
            dln_int  = np.log(intensity_ratio) if intensity_ratio > 0 else 0
            dln_tot  = dln_pop + dln_occ + dln_size + dln_int
            decomp_rows.append({
                "country": cc,
                "dlnQ_total": round(dln_tot, 4),
                "contrib_population": round(dln_pop, 4),
                "contrib_occupancy_Dw_per_Pop": round(dln_occ, 4),
                "contrib_dwelling_size": round(dln_size, 4),
                "contrib_intensity_per_m2": round(dln_int, 4),
                "pct_population": round(100 * dln_pop / dln_tot, 1) if dln_tot else 0,
                "pct_occupancy": round(100 * dln_occ / dln_tot, 1) if dln_tot else 0,
                "pct_size": round(100 * dln_size / dln_tot, 1) if dln_tot else 0,
                "pct_intensity": round(100 * dln_int / dln_tot, 1) if dln_tot else 0,
            })

    out = pd.DataFrame(rows)
    # EU aggregate
    valid = out["hotmaps_2015_TWh"].notna()
    eu = {
        "country": "EU",
        "hotmaps_2015_TWh": round(out.loc[valid, "hotmaps_2015_TWh"].sum(), 1),
        "observed_2015_final_CC_TWh": round(out.loc[valid, "observed_2015_final_CC_TWh"].sum(), 1),
        "snapshot_corrected_2025_TWh": round(out.loc[valid, "snapshot_corrected_2025_TWh"].sum(), 1),
        "snapshot_naked_2025_TWh": round(out.loc[valid, "snapshot_naked_2025_TWh"].sum(), 1),
        "model_2015_stock_corrected": round(out.loc[valid, "model_2015_stock_corrected"].sum(), 1),
        "model_2015_stock_naked": round(out.loc[valid, "model_2015_stock_naked"].sum(), 1),
        "model_2015_lmdi_corrected": round(out.loc[valid, "model_2015_lmdi_corrected"].sum(), 1),
        "model_2015_lmdi_naked": round(out.loc[valid, "model_2015_lmdi_naked"].sum(), 1),
        "pop_ratio_15_lt": "", "dw_ratio_15_lt": "", "size_ratio_15_lt": "",
        "intensity_ratio_observed": "", "intensity_ratio_design": "", "latest_year": "",
    }
    out = pd.concat([out, pd.DataFrame([eu])], ignore_index=True)

    decomp = pd.DataFrame(decomp_rows)

    out_path = ROOT / "code" / "results" / "lmdi_backcast.csv"
    out.to_csv(out_path, index=False)
    decomp_path = ROOT / "code" / "results" / "lmdi_decomposition.csv"
    decomp.to_csv(decomp_path, index=False)

    # Print compact summary
    cols = ["country", "hotmaps_2015_TWh", "observed_2015_final_CC_TWh",
            "snapshot_corrected_2025_TWh", "snapshot_naked_2025_TWh",
            "model_2015_lmdi_corrected", "model_2015_lmdi_naked"]
    print("=== Headline table (TWh) ===")
    print(out[cols].to_string(index=False))
    print(f"\n=== LMDI decomposition (log contributions to dlnQ_observed 2015->latest) ===")
    if not decomp.empty:
        print(decomp.to_string(index=False))
    print(f"\nSaved {out_path}\nSaved {decomp_path}")


if __name__ == "__main__":
    main()
