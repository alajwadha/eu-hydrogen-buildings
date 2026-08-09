"""Grid-decarbonisation sensitivity / attribution for the 2050 emissions result.

Referee concern: the STATED_POLICIES -98% buildings-CO2 reduction by 2050 partly reflects an
EXOGENOUS near-zero 2050 electricity grid (Policy.GRID_CARBON_INTENSITY). This
script decomposes the 2025->2050 emissions fall into (a) fuel switching + demand
(moving off on-site gas/oil to electricity / H2 / DH / biomass) and (b) grid +
district-heat cleanness (the exogenous carbon-intensity decline), by recomputing
the SAME 2050 technology mix under a counterfactual grid frozen at its 2025
intensity.

Method: build one central STATED_POLICIES sample (central per-country envelope rate, CENTRAL
carbon/H2), take its per-(country, carrier, year) final energy, and compute
emissions twice: once with the actual time-varying grid/DH intensity, once with
both held at their 2025 level for all years. The gap at 2050 is the cleanness
contribution; the remainder of the 2025->2050 fall is switching + demand.

Run:  cd code && PYTHONPATH=. python -m scripts.grid_sensitivity   (or via repo root with PYTHONPATH=code)
Out:  code/results/grid_sensitivity.csv  + console summary
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import src.Policy as Policy
from src.Config import (PROCESSED_DIR, RESULTS_DIR, RNG_SEED,
                        central_country_intensity_rates)
from src.Simulation import (scenario_from_config, sample_parameters,
                           run_single_sample)
from src.Emissions import compute_emissions_df

YEARS = [2025, 2030, 2040, 2050]


def _central_sample(scenario: str = "STATED_POLICIES") -> pd.DataFrame:
    """One central-rate sample: per-(nuts, country, tech, carrier, year) energy."""
    scen = scenario_from_config(scenario)
    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    feas = pd.read_csv(PROCESSED_DIR / "hp_dh_feasibility_bottomup.csv")
    rng = np.random.default_rng(RNG_SEED)
    params = sample_parameters(scen, rng, "CENTRAL", "CENTRAL", 0.05)
    # Force the deterministic central envelope rate (not a draw)
    params["intensity_rate"] = central_country_intensity_rates(scenario)
    return run_single_sample(scen, params, stock, feas)


def main() -> None:
    df = _central_sample("STATED_POLICIES")

    # (a) actual time-varying grid/DH intensity
    em_actual = compute_emissions_df(df)
    eu_actual = em_actual.groupby("year")["co2_tCO2"].sum() / 1e6  # MtCO2

    # (b) grid + district-heat intensity frozen at each country's 2025 level
    real_grid = Policy.get_grid_carbon_intensity
    try:
        import src.Economics as Economics
        real_dh = Economics.get_district_heat_co2
    except Exception:
        Economics = None
        real_dh = None
    Policy.get_grid_carbon_intensity = lambda c, y: real_grid(c, 2025)
    if Economics is not None:
        Economics.get_district_heat_co2 = lambda c, y: real_dh(c, 2025)
    # Emissions.py imported the names at module load -> patch there too
    import src.Emissions as Emissions
    Emissions.get_grid_carbon_intensity = lambda c, y: real_grid(c, 2025)
    if real_dh is not None:
        Emissions.get_district_heat_co2 = lambda c, y: real_dh(c, 2025)
    try:
        em_frozen = compute_emissions_df(df)
        eu_frozen = em_frozen.groupby("year")["co2_tCO2"].sum() / 1e6
    finally:
        Policy.get_grid_carbon_intensity = real_grid
        Emissions.get_grid_carbon_intensity = real_grid
        if real_dh is not None:
            Economics.get_district_heat_co2 = real_dh
            Emissions.get_district_heat_co2 = real_dh

    e25 = eu_actual[2025]
    e50a = eu_actual[2050]
    e50f = eu_frozen[2050]
    cleanness = e50f - e50a              # grid + DH carbon-intensity decline
    switching = e25 - e50f               # fuel switch + demand (even on 2025 grid)
    total = e25 - e50a

    rows = []
    print("Grid-decarbonisation attribution (STATED_POLICIES, central, EU buildings CO2):")
    print(f"  2025 emissions                         : {e25:7.1f} MtCO2")
    print(f"  2050 emissions (actual clean grid)     : {e50a:7.1f} MtCO2  ({(e50a/e25-1)*100:+.1f}%)")
    print(f"  2050 emissions (grid+DH frozen at 2025): {e50f:7.1f} MtCO2  ({(e50f/e25-1)*100:+.1f}%)")
    print(f"  -- attribution of the {total:.0f} Mt fall --")
    print(f"  fuel switching + demand : {switching:7.1f} Mt  ({switching/total*100:4.0f}% of fall)")
    print(f"  grid + DH cleanness     : {cleanness:7.1f} Mt  ({cleanness/total*100:4.0f}% of fall)")
    for y in YEARS:
        rows.append({"year": y, "co2_actual_Mt": round(float(eu_actual[y]), 1),
                     "co2_frozen_grid_Mt": round(float(eu_frozen[y]), 1)})
    out = pd.DataFrame(rows)
    out.attrs = {}
    summary = pd.DataFrame([{
        "metric": "STATED_POLICIES_2050_attribution",
        "co2_2025_Mt": round(float(e25), 1),
        "co2_2050_actual_Mt": round(float(e50a), 1),
        "co2_2050_frozen_grid_Mt": round(float(e50f), 1),
        "switching_demand_Mt": round(float(switching), 1),
        "grid_dh_cleanness_Mt": round(float(cleanness), 1),
        "switching_pct_of_fall": round(float(switching / total * 100), 0),
        "cleanness_pct_of_fall": round(float(cleanness / total * 100), 0),
    }])
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(RESULTS_DIR / "grid_sensitivity.csv", index=False)
    summary.to_csv(RESULTS_DIR / "grid_sensitivity_summary.csv", index=False)
    print(f"\nWrote {RESULTS_DIR / 'grid_sensitivity.csv'} and _summary.csv")


if __name__ == "__main__":
    main()
