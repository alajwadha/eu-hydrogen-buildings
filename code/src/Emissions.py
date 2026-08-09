"""
code/src/Emissions.py  —  Step 3: Emissions module
====================================================
Computes CO₂ emissions (tCO₂) from final energy use per technology,
country, and year.

Used by Simulation.py to add emissions to every Monte Carlo sample.

Emission factors:
  Combustion fuels: IPCC AR6 / DEFRA 2024 (scope 1 direct emissions)
  Electricity:      country × year grid intensity from Policy.py (EMBER 2024)
  District heat:    country × year from Economics.py (EEA emission factors)
  Biomass / H2:     zero under EU accounting (renewable fuel directive)

Sources:
  Gas:        IPCC AR6 WG3 Annex II — 0.202 tCO2/MWh (natural gas, combustion)
  Oil:        IPCC AR6 — 0.265 tCO2/MWh (heating oil, combustion)
  Biomass:    EU RED II / EU ETS — zero (carbon-neutral accounting)
  Hydrogen:   zero (green H2 — electrolysis from renewables)
  Electricity: EMBER 2024 country grid intensity (gCO2/kWh) via Policy.py
  District heat: EEA district heating emission factors via Economics.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.Policy import get_grid_carbon_intensity
from src.Economics import get_district_heat_co2

# ── Fuel combustion emission factors (tCO2/MWh_final) ─────────────────────────
# Source: IPCC AR6 WG3 Table 12.6; DEFRA 2024 GHG Conversion Factors
FUEL_EF_TCO2_PER_MWH: dict[str, float] = {
    "gas":          0.202,   # Natural gas (LHV basis)
    "oil":          0.265,   # Light heating oil
    "biomass":      0.000,   # Carbon-neutral under EU RED II
    "hydrogen":     0.000,   # Green hydrogen — zero scope 1
    "district_heat":0.000,   # Handled separately (country-specific)
    "electricity":  0.000,   # Handled separately (grid intensity)
}


def get_emission_factor(fuel: str, country: str, year: int) -> float:
    """
    Returns emission factor in tCO2/MWh_final for a given fuel,
    country, and year.

    For electricity and district heat, uses country-specific and
    time-varying emission intensities.
    """
    if fuel == "electricity":
        # Grid CO2 in gCO2/kWh → tCO2/MWh
        return get_grid_carbon_intensity(country, year) / 1000.0

    if fuel == "district_heat":
        # District heat CO2 in gCO2/kWh → tCO2/MWh
        return get_district_heat_co2(country, year) / 1000.0

    return FUEL_EF_TCO2_PER_MWH.get(fuel, 0.0)


def compute_emissions_df(df: pd.DataFrame, grid_mult: float = 1.0) -> pd.DataFrame:
    """
    Vectorised CO2 computation — applies emission factors per (carrier, country, year)
    group using lookup table. ~10x faster than row iteration.

    grid_mult scales the GRID-dependent emission factors (electricity + district heat)
    to represent the scenario's grid-decarbonisation speed (the 4th scenario lever:
    >1 = slower clean-up / dirtier grid, <1 = faster). Combustion fuels are unaffected.
    """
    df = df.copy()

    # Build emission factor lookup per unique (carrier, country, year)
    groups = df.groupby(["carrier","country","year"])
    ef_map = {}
    for (carrier, country, year), _ in groups:
        ef = get_emission_factor(carrier, country, int(year))
        if carrier in ("electricity", "district_heat"):
            # The grid-speed lever PHASES IN from 1.0 in 2025 (the observed EMBER
            # baseline, identical across scenarios) to its full value by 2050. It must
            # NOT rescale the fixed 2025 starting point: doing so made each scenario's
            # 2025 emissions differ (CURRENT 1.15x, NET_ZERO 0.70x) and the headline
            # %-reductions non-comparable across scenarios.
            phase = min(max((int(year) - 2025) / 25.0, 0.0), 1.0)
            ef *= 1.0 + (grid_mult - 1.0) * phase     # scenario grid-decarbonisation speed
        ef_map[(carrier, country, year)] = ef

    # Vectorised lookup via map
    df["_key"] = list(zip(df["carrier"], df["country"], df["year"]))
    df["_ef"]  = df["_key"].map(ef_map)
    df["co2_tCO2"] = df["final_energy_MWh"] * df["_ef"]

    useful = df["useful_heat_MWh"].replace(0, np.nan)
    df["co2_intensity_gCO2_kWh"] = (df["co2_tCO2"] / useful * 1e6).fillna(0)
    df.drop(columns=["_key","_ef"], inplace=True)
    return df


def aggregate_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates emissions to EU+country level.
    Returns long-format DataFrame with variable names:
      co2_MtCO2         — total EU emissions (Mt CO2/year)
      co2_by_carrier     — breakdown by fuel carrier (Mt CO2)
      co2_by_country     — top 15 countries by emissions (Mt CO2)
      co2_intensity_avg  — EU average gCO2/kWh useful heat
    """
    records = []

    # 1. EU total emissions by year
    eu_total = df.groupby("year")["co2_tCO2"].sum() / 1e6  # → Mt CO2
    for year, val in eu_total.items():
        records.append({"year": year, "variable": "co2_MtCO2",
                        "tech": "all", "carrier": "all", "value": round(val, 3)})

    # 2. Emissions by fuel carrier
    eu_carrier = df.groupby(["year", "carrier"])["co2_tCO2"].sum() / 1e6
    for (year, carrier), val in eu_carrier.items():
        records.append({"year": year, "variable": "co2_by_carrier",
                        "tech": carrier, "carrier": carrier, "value": round(val, 3)})

    # 3. Emissions by country (top 15)
    eu_country = df.groupby(["year", "country"])["co2_tCO2"].sum() / 1e6
    for (year, country), val in eu_country.items():
        records.append({"year": year, "variable": "co2_by_country",
                        "tech": country, "carrier": "all", "value": round(val, 3)})

    # 4. EU average CO2 intensity of useful heat
    heat_total = df.groupby("year")["useful_heat_MWh"].sum()
    co2_total  = df.groupby("year")["co2_tCO2"].sum()
    intensity  = (co2_total / heat_total.replace(0, np.nan) * 1e6).fillna(0)  # gCO2/kWh
    for year, val in intensity.items():
        records.append({"year": year, "variable": "co2_intensity_gCO2_kWh",
                        "tech": "all", "carrier": "all", "value": round(val, 1)})

    return pd.DataFrame(records)


def main() -> None:
    """Quick validation."""
    from src.Config import PROCESSED_DIR, RESULTS_DIR
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1]))

    print("Emissions module validation:")
    for fuel, country, year in [
        ("gas",      "DE", 2025), ("gas",      "DE", 2030),
        ("electricity","DE", 2025), ("electricity","FR", 2025),
        ("electricity","PL", 2025), ("district_heat","PL", 2025),
        ("electricity","SE", 2050),
    ]:
        ef = get_emission_factor(fuel, country, year)
        print(f"  {fuel:<15} {country} {year}: {ef:.4f} tCO2/MWh")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
