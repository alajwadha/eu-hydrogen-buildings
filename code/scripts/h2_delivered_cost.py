"""Bottom-up per-country DELIVERED hydrogen cost (2050), replacing the judgment
H2_MULT_BY_COUNTRY buckets with a transparent multi-route, multi-driver calc.

For each country we cost out every supply route it can realistically use and take
the CHEAPEST one as the delivered cost:

  GREEN  electrolysis from dedicated renewables  (every country)
  PINK   electrolysis from firm nuclear power     (nuclear countries)
  BLUE   gas reforming + CCS                       (gas+CO2-storage countries)
  PIPE   pipeline import of hub hydrogen + transport (grid-connected countries)
  SHIP   seaborne ammonia import + reconversion    (coastal / islands)

Each route is driven by MORE than the renewable resource. The cost drivers are:
  - cost of capital (WACC)         -> via the capital-recovery factor on CAPEX
  - construction LABOUR cost        -> scales the install share of RES/electrolyser CAPEX
  - electricity / feedstock price   -> dominant operating cost (green/pink/blue)
  - resource quality (capacity factor) -> sets full-load hours (green)
  - water scarcity                  -> desalination adder for electrolysis feedwater
  - pipeline connectivity / distance -> import transport premium
  - nuclear / CO2-storage availability -> unlocks the pink / blue routes

WACC and labour are taken from the model (Economics); the gas price is the model's
2050 per-country price; the rest are documented parametric inputs below (estimates
from IEA GHR, IRENA, OIES ET32, Global Wind/Solar Atlas, IAEA PRIS - treat as
order-of-magnitude, which is why the result is reported as a band).

The per-country multiplier on the NW-EU hub trajectory is delivered_c / median_c,
so a country at the EU median pays the hub price (multiplier 1.0).

Run:  cd code && PYTHONPATH=. python -m scripts.h2_delivered_cost
Out:  code/results/h2_delivered_cost.csv + console
"""
from __future__ import annotations

import statistics as st

import pandas as pd

from src.Config import RESULTS_DIR
from src.Economics import (DISCOUNT_RATE_BY_COUNTRY, DISCOUNT_RATE_REAL,
                          LABOUR_COST_MULTIPLIER, H2_MULT_BY_COUNTRY)

# --- global techno-economic constants (2050 central) --------------------------
# CALIBRATED to verified 2050 benchmarks (IRENA Global Hydrogen Trade Costs 2022;
# IEA Global Hydrogen Review 2024 / NZE; IEAGHG 2022-07 for blue; European Hydrogen
# Backbone 2022 for pipeline transport; OIES ET24 Alsulaiman 2023, ET32 Rikabi 2024
# and ET08 2022 for delivered/import costs; OECD WP227 2023 for WACC sensitivity).
# See literature/h2_supply_country_assessment.md for the full reconciliation.
ELZ_CAPEX = 300.0      # EUR/kW electrolyser, 2050 (IRENA EUR 120-300/kW; IEA ~USD 269/kW)
ELZ_LIFE = 20
ELZ_FOM_FRAC = 0.03    # /yr of CAPEX
RES_CAPEX = 750.0      # EUR/kW blended dedicated solar+wind, 2050
RES_LIFE = 25
RES_FOM = 18.0         # EUR/kW/yr
SPEC_MWH_PER_KG = 0.047   # electrolyser electricity use ~47 kWh/kg by 2050 (IRENA 45-48)
LABOUR_SHARE_RES = 0.40   # install share of RES CAPEX scaled by labour
LABOUR_SHARE_ELZ = 0.30
NUCLEAR_LCOE = 78.0    # EUR/MWh firm new-build nuclear power (pink stays > green/import)
NUCLEAR_CF = 0.90
BLUE_GAS_MWH_PER_KG = 0.050   # gas feedstock+fuel per kg H2 (SMR ~76% eff)
BLUE_GAS_WHOLESALE_EUR_MWH = 30.0  # WHOLESALE/industrial gas for SMR feedstock, 2050
                              # (NOT the taxed residential retail price; IEAGHG uses ~EUR 30/MWh)
BLUE_FIXED_EUR_KG = 1.20      # SMR/ATR CAPEX + CCS; gives ~EUR 2.7/kg at gas EUR 30/MWh
                              # (matches IEAGHG 2050 SMR/ATR+CCS EUR 2.67-2.72/kg)
WATER_ADDER_STRESS = 0.05     # EUR/kg desalinated feedwater (IRENA <4% of LCOH)
WATER_ADDER_BASE = 0.02
HUB_EUR_MWH = 50.0     # model NW-EU 2050 hub trajectory (reference level)
# Seaborne import = cheap-sunbelt PRODUCTION + an additive ammonia conversion/
# shipping/cracking block (OIES ET32: ~EUR 1.5/kg large-terminal; cracking alone
# ~EUR 2/kg; small island terminals lose the scale economies -> add a penalty).
SHIP_EXPORT_EUR_KG = 1.10        # 2050 sunbelt green-H2 production (OIES ET32 ~1.0-1.25)
SHIP_CHAIN_LARGE_EUR_KG = 1.50   # synth + ship + crack, large terminal (OIES ET32)
SHIP_CHAIN_ISLAND_EXTRA_EUR_KG = 1.00   # small-scale cracking/terminal penalty (islands)
ISLAND_GREEN_PENALTY_EUR_KG = 0.20   # isolated-grid + small-scale electrolysis penalty
                                     # for islands self-supplying (no grid balancing)
EUR_KG_TO_MWH = 30.0          # 1 kg H2 = 0.03333 MWh  ->  EUR/kg * 30 = EUR/MWh

# --- per-country drivers (documented estimates) -------------------------------
# cf      : blended dedicated-RES capacity factor (best wind/solar/hydro hybrid)
# nuclear : pink route available (operating or firmly planned nuclear)
# blue    : gas-reforming + CO2-storage route credible
# water   : water-stressed -> desalination feedwater adder
# transp  : pipeline-import transport premium over hub (None = not pipeline-connected)
# ship    : seaborne import feasible (coastal / island)
DRIVERS = {
    # NW-EU core (well connected, moderate-good wind)
    "DE": dict(cf=0.32, nuclear=False, blue=True,  water=False, transp=0.05, ship=True),
    "FR": dict(cf=0.34, nuclear=True,  blue=False, water=False, transp=0.05, ship=True),
    "BE": dict(cf=0.36, nuclear=True,  blue=False, water=False, transp=0.05, ship=True),
    "NL": dict(cf=0.38, nuclear=False, blue=True,  water=False, transp=0.05, ship=True),
    "LU": dict(cf=0.30, nuclear=False, blue=False, water=False, transp=0.05, ship=False),
    "UK": dict(cf=0.42, nuclear=True,  blue=True,  water=False, transp=0.08, ship=True),
    # Nordics / Baltics (strong wind, low WACC)
    "DK": dict(cf=0.45, nuclear=False, blue=True,  water=False, transp=0.10, ship=True),
    "SE": dict(cf=0.42, nuclear=True,  blue=False, water=False, transp=0.12, ship=True),
    "FI": dict(cf=0.38, nuclear=True,  blue=False, water=False, transp=0.12, ship=True),
    "EE": dict(cf=0.38, nuclear=False, blue=False, water=False, transp=0.12, ship=True),
    "LV": dict(cf=0.38, nuclear=False, blue=False, water=False, transp=0.12, ship=True),
    "LT": dict(cf=0.38, nuclear=False, blue=False, water=False, transp=0.12, ship=True),
    "IE": dict(cf=0.45, nuclear=False, blue=False, water=False, transp=0.13, ship=True),
    # Landlocked / Central Europe (pipeline-dependent, weaker resource)
    "CZ": dict(cf=0.28, nuclear=True,  blue=False, water=False, transp=0.10, ship=False),
    "SK": dict(cf=0.28, nuclear=True,  blue=False, water=False, transp=0.10, ship=False),
    "HU": dict(cf=0.30, nuclear=True,  blue=False, water=False, transp=0.12, ship=False),
    "AT": dict(cf=0.34, nuclear=False, blue=False, water=False, transp=0.10, ship=False),
    "CH": dict(cf=0.36, nuclear=True,  blue=False, water=False, transp=0.12, ship=False),
    "SI": dict(cf=0.30, nuclear=True,  blue=False, water=False, transp=0.12, ship=True),
    "PL": dict(cf=0.34, nuclear=False, blue=False, water=False, transp=0.10, ship=True),
    # South / SE Europe (strong solar, some water stress)
    "ES": dict(cf=0.40, nuclear=False, blue=False, water=True,  transp=0.13, ship=True),
    "PT": dict(cf=0.42, nuclear=False, blue=False, water=True,  transp=0.13, ship=True),
    "IT": dict(cf=0.34, nuclear=False, blue=True,  water=True,  transp=0.12, ship=True),
    "EL": dict(cf=0.38, nuclear=False, blue=False, water=True,  transp=0.13, ship=True),
    "HR": dict(cf=0.32, nuclear=False, blue=False, water=False, transp=0.13, ship=True),
    "BG": dict(cf=0.36, nuclear=True,  blue=True,  water=True,  transp=0.13, ship=True),
    "RO": dict(cf=0.36, nuclear=True,  blue=True,  water=False, transp=0.13, ship=True),
    # Isolated islands (NOT pipeline-connected: transp=None)
    "CY": dict(cf=0.30, nuclear=False, blue=False, water=True,  transp=None, ship=True),
    "MT": dict(cf=0.28, nuclear=False, blue=False, water=True,  transp=None, ship=True),
}


def crf(r: float, n: int) -> float:
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def _green_like(power_eur_mwh, cf, wacc, labour, water_stress,
                capex_mult=1.0, wacc_delta=0.0):
    """LCOH (EUR/kg) of electrolysis given a power price + full-load hours."""
    w = wacc + wacc_delta
    flh = cf * 8760.0
    elz_capex = ELZ_CAPEX * capex_mult * (1 - LABOUR_SHARE_ELZ + LABOUR_SHARE_ELZ * labour)
    elz_kg = (elz_capex * crf(w, ELZ_LIFE) + ELZ_CAPEX * capex_mult * ELZ_FOM_FRAC) \
             * SPEC_MWH_PER_KG * 1000.0 / flh
    elec_kg = power_eur_mwh * SPEC_MWH_PER_KG
    water = WATER_ADDER_STRESS if water_stress else WATER_ADDER_BASE
    return elec_kg + elz_kg + water


def _res_lcoe(cf, wacc, labour, capex_mult=1.0, wacc_delta=0.0):
    """Dedicated renewable LCOE (EUR/MWh)."""
    w = wacc + wacc_delta
    capex = RES_CAPEX * capex_mult * (1 - LABOUR_SHARE_RES + LABOUR_SHARE_RES * labour)
    ann = capex * crf(w, RES_LIFE) + RES_FOM
    return ann / (cf * 8.76)


def routes_eur_mwh(cc, capex_mult=1.0, wacc_delta=0.0,
                   hub_mult=1.0, transp_mult=1.0, ship_mult=1.0):
    d = DRIVERS[cc]
    wacc = DISCOUNT_RATE_BY_COUNTRY.get(cc, DISCOUNT_RATE_REAL)
    labour = LABOUR_COST_MULTIPLIER.get(cc, 1.0)
    out = {}
    # GREEN
    power = _res_lcoe(d["cf"], wacc, labour, capex_mult, wacc_delta)
    green_kg = _green_like(power, d["cf"], wacc, labour, d["water"],
                           capex_mult, wacc_delta)
    if d["transp"] is None:               # isolated island: no grid balancing, small scale
        green_kg += ISLAND_GREEN_PENALTY_EUR_KG
    out["green"] = green_kg * EUR_KG_TO_MWH
    # PINK
    if d["nuclear"]:
        out["pink"] = _green_like(NUCLEAR_LCOE, NUCLEAR_CF, wacc, labour, d["water"],
                                  capex_mult, wacc_delta) * EUR_KG_TO_MWH
    # BLUE (wholesale gas feedstock, not taxed residential retail)
    if d["blue"]:
        out["blue"] = (BLUE_GAS_WHOLESALE_EUR_MWH * BLUE_GAS_MWH_PER_KG
                       + BLUE_FIXED_EUR_KG * capex_mult) * EUR_KG_TO_MWH
    # PIPE import
    if d["transp"] is not None:
        out["pipe"] = HUB_EUR_MWH * hub_mult * (1 + d["transp"] * transp_mult)
    # SHIP import: sunbelt production + ammonia conversion/shipping/cracking block,
    # with a small-scale penalty for islands (no pipeline) lacking terminal scale.
    if d["ship"]:
        chain = SHIP_CHAIN_LARGE_EUR_KG
        if d["transp"] is None:           # island: small-terminal penalty
            chain += SHIP_CHAIN_ISLAND_EXTRA_EUR_KG
        out["ship"] = (SHIP_EXPORT_EUR_KG * hub_mult
                       + chain * ship_mult) * EUR_KG_TO_MWH
    return out


def delivered(cc, **kw):
    r = routes_eur_mwh(cc, **kw)
    route = min(r, key=r.get)
    return r[route], route, r


# techno-economic uncertainty toggles: cheaper (low) and dearer (high) H2 worlds.
# Production AND import move together (a cheaper-H2 world lowers the hub too); the
# reference median is held at the central value so each country's band is its own
# delivered-cost uncertainty, not a moving-yardstick artefact.
LOW_KW = dict(capex_mult=0.75, wacc_delta=-0.01, hub_mult=0.85, transp_mult=0.7, ship_mult=0.8)
HIGH_KW = dict(capex_mult=1.25, wacc_delta=+0.01, hub_mult=1.15, transp_mult=1.3, ship_mult=1.2)


def main() -> None:
    countries = list(DRIVERS)
    cen = {c: delivered(c)[0] for c in countries}
    lo = {c: delivered(c, **LOW_KW)[0] for c in countries}
    hi = {c: delivered(c, **HIGH_KW)[0] for c in countries}
    med_cen = st.median(cen.values())
    med_lo = med_hi = med_cen   # fixed reference -> clean, monotonic per-country bands

    rows = []
    for c in countries:
        dcen, route, allr = delivered(c)
        rows.append({
            "country": c,
            "delivered_eur_mwh": round(dcen, 1),
            "delivered_eur_kg": round(dcen / EUR_KG_TO_MWH, 2),
            "cheapest_route": route,
            "green": round(allr.get("green", float("nan")), 1),
            "pink": round(allr["pink"], 1) if "pink" in allr else None,
            "blue": round(allr["blue"], 1) if "blue" in allr else None,
            "pipe": round(allr["pipe"], 1) if "pipe" in allr else None,
            "ship": round(allr["ship"], 1) if "ship" in allr else None,
            "mult_central": round(dcen / med_cen, 2),
            "mult_low": round(lo[c] / med_lo, 2),
            "mult_high": round(hi[c] / med_hi, 2),
            "mult_old_judgment": H2_MULT_BY_COUNTRY.get(c, 1.0),
        })
    df = pd.DataFrame(rows).sort_values("mult_central")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "h2_delivered_cost.csv", index=False)

    show = ["country", "cheapest_route", "green", "pink", "blue", "pipe", "ship",
            "delivered_eur_mwh", "delivered_eur_kg", "mult_central", "mult_old_judgment"]
    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(df[show].to_string(index=False))
    print(f"\nEU median delivered: {med_cen:.0f} EUR/MWh ({med_cen/EUR_KG_TO_MWH:.2f} EUR/kg) "
          f"= multiplier 1.00 (the hub).")
    print("Cheapest-route counts:", df.cheapest_route.value_counts().to_dict())
    print(f"Multiplier range across band: low median {df.mult_low.min():.2f}-{df.mult_low.max():.2f}, "
          f"high {df.mult_high.min():.2f}-{df.mult_high.max():.2f}")
    print(f"\nWrote {RESULTS_DIR / 'h2_delivered_cost.csv'}")


if __name__ == "__main__":
    main()
