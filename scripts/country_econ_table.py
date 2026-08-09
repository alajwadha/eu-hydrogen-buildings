"""Per-country techno-economic table: LCOH, fuel + H2 prices (2025 & 2050),
labour multiplier, WACC, H2 infrastructure proxy, grid intensity, H2-HP gap.

Pulls REAL values from Economics.py / Policy.py (no invented numbers). Two
fields the user asked for are NOT model parameters and are reported as the
honest proxy:
  - "H2 infrastructure cost per kg per country": the model has no per-kg infra
    cost; it uses GAS_GRID_COVERAGE as the hydrogen-infrastructure-readiness
    proxy (high gas-grid coverage -> existing pipeline -> lower H2 retrofit cost).
    Reported as gas_grid_coverage + h2_readiness (0-1).
  - "transmission costs": not broken out; retail fuel prices already INCLUDE
    network/transmission charges, so the gas/elec prices shown are end-user
    (transmission-inclusive).
H2 EUR/MWh is converted to EUR/kg at the LHV (1 kg H2 = 33.33 kWh = 0.03333 MWh).

Run:  cd code && PYTHONPATH=. python -m scripts.country_econ_table
Out:  code/results/country_econ_table.csv + console
"""
from __future__ import annotations

import pandas as pd

import src.Economics as E
import src.Policy as P
from src.Config import RESULTS_DIR, PROCESSED_DIR
from src.Economics import compute_lcoh, get_fuel_price, DISCOUNT_RATE_REAL

MWH_PER_KG_H2 = 0.03333   # LHV: 1 kg H2 ~ 33.33 kWh


def main() -> None:
    countries = sorted(E.LABOUR_COST_MULTIPLIER.keys()
                       | E.DISCOUNT_RATE_BY_COUNTRY.keys()
                       | P.GRID_CARBON_INTENSITY.keys())
    # restrict to the 29 model countries (those with a grid-intensity entry)
    countries = [c for c in countries if c in P.GRID_CARBON_INTENSITY]

    try:
        gap = pd.read_csv(RESULTS_DIR / "h2_hp_gap.csv").set_index("country")
    except Exception:
        gap = None

    rows = []
    for c in countries:
        h2_25 = get_fuel_price("hydrogen", c, 2025, "CENTRAL")
        h2_50 = get_fuel_price("hydrogen", c, 2050, "CENTRAL")
        try:
            hp = min(compute_lcoh("hp_air", c, 2050), compute_lcoh("hp_ground", c, 2050))
            gasb = compute_lcoh("gas_boiler", c, 2050)
            h2b = compute_lcoh("h2_boiler", c, 2050)
        except Exception:
            hp = gasb = h2b = None
        gG = P.GRID_CARBON_INTENSITY.get(c, {})
        rows.append({
            "country": c,
            "labour_mult": E.LABOUR_COST_MULTIPLIER.get(c, 1.0),
            "wacc_pct": round(E.DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL) * 100, 1),
            "elec_2025_eur_mwh": round(get_fuel_price("electricity", c, 2025), 1),
            "gas_2025_eur_mwh": round(get_fuel_price("gas", c, 2025), 1),
            "h2_mult": E.H2_MULT_BY_COUNTRY.get(c, 1.0),
            "h2_2025_eur_mwh": round(h2_25, 1),
            "h2_2050_eur_mwh": round(h2_50, 1),
            "h2_2025_eur_kg": round(h2_25 * MWH_PER_KG_H2, 2),
            "h2_2050_eur_kg": round(h2_50 * MWH_PER_KG_H2, 2),
            "gas_grid_cov": round(P.GAS_GRID_COVERAGE.get(c, 0.30), 2),
            "h2_infra_readiness": round(P.h2_infrastructure_readiness(c), 2),
            "grid_co2_2025": gG.get(2025), "grid_co2_2050": gG.get(2050),
            "lcoh_bestHP_2050": round(hp, 1) if hp else None,
            "lcoh_gas_2050": round(gasb, 1) if gasb else None,
            "lcoh_H2_2050": round(h2b, 1) if h2b else None,
            "h2_minus_hp_gap_2050": (round(float(gap.loc[c, "gap_2050"]), 1)
                                     if gap is not None and c in gap.index else None),
        })
    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "country_econ_table.csv", index=False)
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(df.to_string(index=False))
    print(f"\nWrote {RESULTS_DIR / 'country_econ_table.csv'} ({len(df)} countries, {len(df.columns)} cols)")


if __name__ == "__main__":
    main()
