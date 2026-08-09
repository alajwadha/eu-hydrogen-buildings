"""LMDI design-basis backcast: per-country multi-driver decomposition using

- Population (Eurostat, ONS, BFS)
- Dwellings (national stats offices)
- Avg dwelling size (constant: very slow drift, Eurostat ilc_hcmh02)
- DESIGN intensity decline (envelope-relevant renovation, deep*0.5 + medium*0.25 + light*0.05)
- 30-yr HDD climate normal (1991-2020 WMO standard) for sanity-check, NOT for intensity

LMDI identity (multiplicative):
  Q_15 / Q_25 = (Pop_15 / Pop_25)
              * ((Dw/Pop)_15 / (Dw/Pop)_25)
              * ((m2/Dw)_15 / (m2/Dw)_25)
              * (i_design_15 / i_design_25)

where i_design_15 / i_design_25 = (1 + r)^10 with r = design_intensity_decline_pct_yr/100.
This is the DESIGN intensity ratio (envelope only), not metered. So:
  - Boiler/HP efficiency improvements (which cut final but not useful) do NOT enter.
  - Behavior / prebound effect does NOT enter.
  - Climate is irrelevant for design demand (TABULA already references normal climate).

Inputs:
  code/data/country_config/heat_drivers_eurostat.csv  (Eurostat panel)
  code/data/country_config/heat_drivers_national.csv  (UK+CH)
  code/data/country_config/heat_drivers_demographics.csv (dw, hh, size)
  code/data/country_config/design_intensity_decline.csv (per-country r)
  code/data/country_config/hdd_normal_1991_2020.csv     (30-yr HDD normals, sanity check)
  code/data/processed/building_stock_nuts3.csv          (Hotmaps 2015 benchmark)
  code/data/processed/building_stock_nuts3_bottomup.csv (model corrected snapshot)
  code/results/compare_naked.csv                         (model naked snapshot)

Outputs:
  code/results/lmdi_design.csv          headline per-country table
  code/results/lmdi_design_drivers.csv  per-country driver values + log contributions

Methodology references:
  - Ang, B.W. (2005). "The LMDI approach to decomposition analysis: a practical
    guide." Energy Policy 33(7): 867-871. doi:10.1016/j.enpol.2003.10.010
    (The canonical Logarithmic Mean Divisia Index multiplicative + additive
    forms; log-mean weight L(a,b) = (b-a)/ln(b/a).)
  - Ang, B.W. (2015). "LMDI decomposition approach: A guide for implementation."
    Energy Policy 86: 233-238.

Driver references:
  - Castellazzi, L. & Esposito, S. (2019). "Comprehensive study of building
    energy renovation activities and the uptake of nearly zero-energy
    buildings in the EU." JRC EUR 29906 EN. (Per-country renovation depth
    bands deep / medium / light, residential, floor-area-based, 2012-2016
    average. The envelope-relevant rate is derived here as
    r = 0.50*deep + 0.25*medium + 0.05*light, isolating envelope contribution
    from boiler/HVAC swaps that change *final* but not *design* demand.)
  - BPIE (2024). "EU Buildings Climate Tracker." Brussels. (Confirms EU
    weighted renovation rate has remained close to 1%/yr through 2023, well
    below the Renovation Wave 3%/yr target.)
  - WMO (2017). "Guidelines on the Calculation of Climate Normals."
    WMO-No. 1203. (The 1991-2020 climate normal in
    hdd_normal_1991_2020.csv is reported as context only; the LMDI itself
    does not use HDD because design demand is climate-normal by construction.)

Data sources:
  - Eurostat: demo_gind (population), ilc_lvph01 (avg household size),
    ilc_hcmh02 (avg dwelling size, 2012 reference), cens_11dwob / cens_21dwst
    (census dwelling stock), nrg_d_hhq (residential space heating), nrg_chdd_a
    (HDD), nama_10_gdp (real GDP).
  - National statistical offices for annual dwelling stock and energy:
    Destatis (DE), INSEE EAPL (FR), ISTAT permanent census (IT), INE (ES, PT),
    CBS 81955ENG (NL), SCB BO0104 (SE), GUS (PL), ONS Dwelling Stock by Tenure
    + MHCLG Live Tables (UK), CSO Census 2022 (IE), CZSO 2021 (CZ), KSH 2022
    (HU), INS Romania, NSI Bulgaria, CYSTAT, CSB Latvia, STATEC (LU), SURS (SI),
    NSO Malta, BFS Gebaeude- und Wohnungsstatistik (CH).
  - UK national: DESNZ Energy Consumption in the UK (ECUK) 2024 Table U3;
    DESNZ Energy Trends 7.1b for 30-yr HDD normal at base 15.5C.
  - CH national: BFE Der Energieverbrauch der Privaten Haushalte 2000-2023
    (Prognos 2024); SECO real GDP series via BFE Tab 11.
  - Renovation supplements: ADEME MaPrimeRenov (FR), ENEA Superbonus bulletins
    (IT), SEAI National Retrofit Plan (IE), KfW BEG statistics (DE), English
    Housing Survey + ECO (UK), BFE Gebaeudeprogramm (CH).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))
import Config as C  # noqa: E402


def _load_panel() -> pd.DataFrame:
    parts = [pd.read_csv(C.DATA_DIR / "country_config" / fn) for fn in
             ["heat_drivers_eurostat.csv", "heat_drivers_national.csv",
              "heat_drivers_demographics.csv"]]
    return pd.concat(parts, ignore_index=True)


def _series(panel, cc, metric):
    return panel[(panel.country == cc) & (panel.metric == metric)] \
        .set_index("year")["value"].dropna().sort_index()


def _national_twh(p):
    df = pd.read_csv(p)
    return df.groupby("country")["heat_2015_MWh"].sum() / 1e6


def main() -> None:
    panel = _load_panel()
    designs = pd.read_csv(C.DATA_DIR / "country_config" / "design_intensity_decline.csv") \
        .set_index("country")["design_intensity_decline_pct_yr"]
    hdd30 = pd.read_csv(C.DATA_DIR / "country_config" / "hdd_normal_1991_2020.csv") \
        .set_index("country")
    hot = _national_twh(C.PROCESSED_DIR / "building_stock_nuts3.csv")
    snap = _national_twh(C.PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    naked = pd.read_csv(ROOT / "code" / "results" / "compare_naked.csv") \
        .set_index("country")["snapshot_naked_TWh"]
    # Observed 2015 climate-corrected against the WMO 30-yr normal (1991-2020).
    # Use this in place of the 9-yr panel mean (the 9-yr mean was depressed by
    # the unusually warm 2019-2023 period).
    TJ_TO_TWH = 1 / 3600.0
    obs_2015_cc_30yr = {}
    for cc in snap.index:
        heat = _series(panel, cc, "heat_residential_TJ")
        hdd  = _series(panel, cc, "hdd")
        if 2015 not in heat.index or 2015 not in hdd.index or cc not in hdd30.index:
            obs_2015_cc_30yr[cc] = float("nan")
            continue
        hdd_normal = float(hdd30.loc[cc, "hdd_1991_2020"])
        obs_2015_cc_30yr[cc] = heat[2015] * (hdd_normal / hdd[2015]) * TJ_TO_TWH

    NYRS = 10  # 2015 -> 2025

    rows, drivers = [], []
    for cc in sorted(snap.index):
        pop = _series(panel, cc, "population")
        dw  = _series(panel, cc, "dwellings_total")
        # Use earliest available year >= 2015 and latest available; for pop/dw both exist 2015 and 2023.
        if pop.empty or dw.empty:
            continue
        y15 = 2015
        ylt = max(int(pop.index.max()), int(dw.index.max()))
        # Use 2023 if available for both, else latest common.
        common = sorted(set(pop.index) & set(dw.index))
        if 2015 not in common:
            continue
        ylt = max([y for y in common if y >= 2015]) if common else ylt
        if ylt <= y15:
            continue

        pop_15, pop_lt = float(pop[y15]), float(pop[ylt])
        dw_15, dw_lt   = float(dw[y15]),  float(dw[ylt])

        pop_ratio = pop_15 / pop_lt
        dw_ratio  = dw_15  / dw_lt
        occ_ratio = (dw_15 / pop_15) / (dw_lt / pop_lt)
        size_ratio = 1.0  # constant (Eurostat ilc_hcmh02 reference only)

        # Design intensity decline (envelope-relevant)
        r = float(designs.get(cc, 0.55)) / 100.0
        # i_15 / i_25 -- 2015 intensity HIGHER (less retrofit done)
        # Use NYRS = 2025 - 2015 (always 10 yrs for the backcast horizon),
        # not (ylt - 2015) since we apply to model_2025 snapshot.
        design_intensity_ratio = (1 + r) ** NYRS

        # Multi-driver LMDI ratio: Q_2015 / Q_2025
        # For backcast we want model_2015 = model_2025 * ratio, where ratio = Q_15/Q_25.
        # Note pop and dwellings use ylt (latest observed) as proxy for 2025; that's an
        # approximation (population grows slightly more, dwellings ditto). For most
        # countries 2023->2025 effect is tiny (<1%); we accept it.
        lmdi_ratio = pop_ratio * occ_ratio * size_ratio * design_intensity_ratio

        snapshot_corr = float(snap[cc])
        snapshot_nak  = float(naked.get(cc, float("nan")))
        m15_corr = snapshot_corr * lmdi_ratio
        m15_nak  = snapshot_nak  * lmdi_ratio

        hot_v = float(hot.get(cc, float("nan")))

        # Climate normal sanity check (informational only)
        hdd_normal = float(hdd30.loc[cc, "hdd_1991_2020"]) if cc in hdd30.index else float("nan")
        hdd_recent = float(hdd30.loc[cc, "hdd_2015_2023"]) if cc in hdd30.index else float("nan")

        obs15 = obs_2015_cc_30yr.get(cc, float("nan"))
        rows.append({
            "country": cc,
            "hotmaps_2015_TWh": round(hot_v, 1),
            "observed_2015_TWh_30yr_normal": round(obs15, 1) if obs15 == obs15 else None,
            "model_2015_corrected": round(m15_corr, 1),
            "model_2025_corrected": round(snapshot_corr, 1),
            "model_2015_naked": round(m15_nak, 1) if m15_nak == m15_nak else None,
            "model_2025_naked": round(snapshot_nak, 1) if snapshot_nak == snapshot_nak else None,
            "gap_2015_vs_hotmaps_pct": round((m15_corr - hot_v) / hot_v * 100, 1) if hot_v > 0 else None,
            "change_2015_to_2025_pct": round((snapshot_corr - m15_corr) / m15_corr * 100, 1),
            "lmdi_ratio_15_to_25": round(lmdi_ratio, 4),
        })

        drivers.append({
            "country": cc,
            "pop_ratio_15_lt": round(pop_ratio, 4),
            "occupancy_ratio_15_lt": round(occ_ratio, 4),
            "dw_ratio_15_lt": round(dw_ratio, 4),
            "size_ratio_15_lt": size_ratio,
            "design_intensity_decline_pct_yr": round(r * 100, 2),
            "design_intensity_ratio_15_25": round(design_intensity_ratio, 4),
            "lmdi_ratio_15_25": round(lmdi_ratio, 4),
            "hdd_1991_2020": hdd_normal,
            "hdd_2015_2023": hdd_recent,
            "warm_decade_factor": round(hdd_recent / hdd_normal, 4) if hdd_normal else None,
            "ylt_used": ylt,
            "dlnQ_pop": round(np.log(pop_ratio), 4),
            "dlnQ_occupancy": round(np.log(occ_ratio), 4),
            "dlnQ_size": 0.0,
            "dlnQ_intensity": round(np.log(design_intensity_ratio), 4),
            "dlnQ_total": round(np.log(lmdi_ratio), 4),
        })

    out = pd.DataFrame(rows)
    drv = pd.DataFrame(drivers)

    valid = out["hotmaps_2015_TWh"].notna()
    eu = {
        "country": "EU",
        "hotmaps_2015_TWh": round(out.loc[valid, "hotmaps_2015_TWh"].sum(), 1),
        "observed_2015_TWh_30yr_normal": round(out.loc[valid, "observed_2015_TWh_30yr_normal"].dropna().sum(), 1),
        "model_2015_corrected": round(out.loc[valid, "model_2015_corrected"].sum(), 1),
        "model_2025_corrected": round(out.loc[valid, "model_2025_corrected"].sum(), 1),
        "model_2015_naked": round(out.loc[valid, "model_2015_naked"].dropna().sum(), 1),
        "model_2025_naked": round(out.loc[valid, "model_2025_naked"].dropna().sum(), 1),
    }
    h = eu["hotmaps_2015_TWh"]; m15 = eu["model_2015_corrected"]; m25 = eu["model_2025_corrected"]
    eu["gap_2015_vs_hotmaps_pct"] = round((m15 - h) / h * 100, 1)
    eu["change_2015_to_2025_pct"] = round((m25 - m15) / m15 * 100, 1)
    eu["lmdi_ratio_15_to_25"] = round(m15 / m25, 4)
    out = pd.concat([out, pd.DataFrame([eu])], ignore_index=True)

    out.to_csv(ROOT / "code" / "results" / "lmdi_design.csv", index=False)
    drv.to_csv(ROOT / "code" / "results" / "lmdi_design_drivers.csv", index=False)

    cols = ["country", "hotmaps_2015_TWh", "observed_2015_TWh_30yr_normal",
            "model_2015_corrected", "model_2025_corrected",
            "gap_2015_vs_hotmaps_pct", "change_2015_to_2025_pct", "lmdi_ratio_15_to_25"]
    print(out[cols].to_string(index=False))
    print("\n=== Driver decomposition (per country) ===")
    print(drv[["country", "pop_ratio_15_lt", "occupancy_ratio_15_lt", "size_ratio_15_lt",
               "design_intensity_decline_pct_yr", "design_intensity_ratio_15_25",
               "lmdi_ratio_15_25", "ylt_used"]].to_string(index=False))
    print(f"\nSaved code/results/lmdi_design.csv\nSaved code/results/lmdi_design_drivers.csv")


if __name__ == "__main__":
    main()
