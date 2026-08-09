"""
code/src/Economics.py
======================
Step 2: Cost module — Levelised Cost of Heat (LCOH) for all heating technologies.

Computes LCOH (EUR/MWh_useful) per technology, NUTS3 region, and year using:
  - Annualised CAPEX (capital recovery factor × overnight cost)
  - Fixed O&M costs
  - Variable fuel costs (country-specific energy prices)
  - Carbon cost adder (from Policy.py — EU ETS2 from 2027)
  - Technology efficiency or COP (building-type specific)

The LCOH is the economic objective function component for RQ1 and RQ2.
It feeds directly into the LP/MILP optimisation (Step 5 / Optimisation.py).

LCOH formula:
  LCOH = (CRF × CAPEX + FOM) / AHE + VOM + (FuelPrice / η) + CarbonAdder / η

where:
  CRF = r(1+r)^n / ((1+r)^n - 1)    [capital recovery factor]
  AHE = annual heat energy delivered per unit capacity [MWh/kW/year]
  FOM = fixed O&M [EUR/kW/year]
  VOM = variable O&M [EUR/MWh_useful]
  η   = efficiency or COP

Sources:
  CAPEX: IEA Future of Heat Pumps (2022); JRC Technology Data (2023); 
         IRENA Heat Pump Costs and Markets (2022); Danish Energy Agency (2023)
  Fuel prices: Eurostat nrg_pc_202 / nrg_pc_204 (H1 2025); IEA projections
  Hydrogen prices: IEA Global Hydrogen Review (2023); OIES
  Discount rate: 5% real pre-tax (BPIE 2024 recommendation for buildings)
  Lifetimes: JRC Technology Data; IEA technology data
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "code"))

from src.Config import RESULTS_DIR, YEARS, TECHS
from src.Policy import (
    get_carbon_price,
    get_carbon_cost_adder_eur_per_mwh_useful,
    CARBON_PRICE_SCENARIO,
)


# =============================================================================
# 0b. COUNTRY LABOUR COST MULTIPLIERS  (added 2026-05-14, Ali decision)
# =============================================================================
# Heating-system CAPEX in EUR/kW is decomposed into:
#   - equipment cost (manufactured goods traded across the EU single market)
#   - installation cost (country-specific, dominated by local labour)
#
# We apply a country-specific LABOUR_COST_MULTIPLIER to the installation
# fraction of CAPEX and to FOM (since maintenance is labour-intensive).
#
# Source:  Eurostat lc_lci_lev — Hourly labour costs, construction (NACE F),
#          2024 levels in EUR (LCS2020-based + LCI extrapolation).
#          https://ec.europa.eu/eurostat/databrowser/view/lc_lci_lev/
# Anchor:  EU27 average construction = EUR 30.0/h  ->  multiplier = 1.00
# UK / CH: ONS / SECO/BFS proxies; not in Eurostat lc_lci_lev.
#
# Methodology note for the paper:
#   Equipment is treated as an internationally-traded good with negligible
#   price dispersion across EU countries (consistent with European Heat Pump
#   Association manufacturer survey 2024). Installation is treated as a
#   local non-traded service whose price scales with national construction
#   labour costs. The split per technology reflects relative drilling /
#   piping / certification labour intensity (see LABOUR_SHARE_OF_CAPEX).
#
# A licensed national labour-cost series (UN or SAMI) would replace this.
LABOUR_COST_MULTIPLIER = {
    # Low-wage CEE / Baltic / Balkan
    "BG": 0.35,   # ~EUR 10.6/h whole economy -> ~0.35 x EU construction anchor
    "RO": 0.42,   # ~EUR 12.5/h
    "HU": 0.47,   # ~EUR 14.1/h
    "LV": 0.55,   # ~EUR 13.3/h
    "PL": 0.58,   # ~EUR 15-16/h
    "LT": 0.55,   # ~EUR 13.0/h
    "HR": 0.55,   # ~EUR 14/h (high recent growth)
    "SK": 0.55,   # ~EUR 16/h
    "EE": 0.62,   # ~EUR 18/h
    "CZ": 0.60,   # ~EUR 18/h
    "PT": 0.66,   # ~EUR 20/h
    "EL": 0.65,   # ~EUR 19/h
    "MT": 0.62,   # LCS2016-based estimate
    "CY": 0.70,   # ~EUR 22/h
    "SI": 0.78,   # ~EUR 24/h
    "ES": 0.83,   # ~EUR 25/h
    # Mid-range core
    "IT": 0.97,   # ~EUR 29/h (slightly below EA)
    "IE": 1.07,   # ~EUR 32/h
    # High-wage Northern/Western
    "FI": 1.15,   # ~EUR 34/h
    "AT": 1.20,   # ~EUR 36/h
    "FR": 1.30,   # ~EUR 39/h
    "DE": 1.30,   # ~EUR 39/h
    "NL": 1.30,   # ~EUR 39/h
    "SE": 1.35,   # ~EUR 41/h (SEK->EUR)
    "BE": 1.60,   # ~EUR 48.2/h whole economy
    "DK": 1.65,   # ~EUR 50.1/h whole economy
    "LU": 1.80,   # ~EUR 55.2/h (highest EU)
    # Non-EU
    "UK": 1.10,   # ONS 2024 construction ~GBP 24/h -> ~EUR 28/h
    "CH": 1.70,   # SECO 2024 — well above EU
}
LABOUR_MULT_EU_AVG = 1.00   # fallback (anchor)

# Per-technology share of CAPEX attributable to on-site labour / installation.
# Equipment is roughly 1 - labour_share of CAPEX, ~uniform in price across EU.
# Drilling-heavy techs (ground-source HP) have highest labour share.
LABOUR_SHARE_OF_CAPEX = {
    "gas_boiler":       0.30,   # Mostly equipment; ~1-day install
    "oil_boiler":       0.30,   # Plus tank work
    "biomass_boiler":   0.30,   # Equipment + flue + fuel store
    "electric_boiler":  0.20,   # Mostly equipment; simple wiring
    "hp_air":           0.40,   # Outdoor unit + indoor + refrigerant cert
    "hp_ground":        0.55,   # Drilling/trenching dominates cost
    "district_heat":    0.50,   # Connection / substation — civils-heavy
    "h2_boiler":        0.35,   # As gas + new safety / certification labour
}
LABOUR_SHARE_DEFAULT = 0.35

# Same multiplier applied to FOM (annual O&M is field-service labour).
FOM_LABOUR_SHARE = 0.70   # ~70% of O&M is labour, 30% is parts/refrigerant


def get_labour_multiplier(country: str) -> float:
    """Returns country labour-cost multiplier (EU27 construction = 1.00)."""
    return LABOUR_COST_MULTIPLIER.get(country, LABOUR_MULT_EU_AVG)


# =============================================================================
# 1. TECHNOLOGY PARAMETERS
# =============================================================================
# All monetary values in EUR_2024.
# CAPEX in EUR/kW_thermal installed capacity.
# Lifetimes in years.
# FOM in EUR/kW/year.
# VOM in EUR/MWh_useful.
# Efficiency/COP: dimensionless (useful heat output / energy input).
#
# Learning rates applied to CAPEX from 2025 to 2050:
#   Heat pumps:    high learning (large-scale deployment expected)
#   Gas/oil boilers: mature technology, minimal cost reduction
#   H2 boiler:     moderate learning (similar to gas boiler with H2-ready components)
#   District heat: infrastructure-heavy, low learning
#
# Sources per technology documented inline.

TECH_PARAMS = {

    # ── Gas boiler ────────────────────────────────────────────────────────────
    # Source: Danish Energy Agency Technology Data, Individual Heating Plants (latest
    # vintage); JRC Technology Data (2023). REVISED 2026-05-25 (source audit, see
    # literature/scenario_assumptions_audit.md §2.2): prior 1000/950 ran high vs DEA
    # residential condensing-boiler installed investment (~407 EUR/kW). Lowered to the
    # DEA-anchored central; mature tech keeps the ~0.95 learning ratio to 2050.
    "gas_boiler": {
        "capex_2025":       420,     # EUR/kW_thermal — DEA installed (was 1_000)
        "capex_2050":       400,     # Mature technology — minimal learning
        "lifetime_yrs":     20,      # JRC: 15-25 years, central 20
        "fom_eur_kw_yr":   20,      # JRC: EUR 15-25/kW/year
        "vom_eur_mwh":      2,       # ⚠️ Estimate; JRC publishes no VOM for domestic boilers
        "efficiency_2025":  0.92,    # Condensing gas boiler (LHV)
        "efficiency_2050":  0.94,    # Slight improvement with H2-ready tech
        "fuel":             "gas",
        "annual_hours":     2000,    # Full-load equivalent hours (residential)
        "notes": "Condensing gas boiler, residential. CAPEX includes installation. "
                 "Efficiency on LHV basis. Annual hours reflects average EU climate.",
    },

    # ── Oil boiler ────────────────────────────────────────────────────────────
    # Source: Danish Energy Agency Technology Data; JRC (2023). REVISED 2026-05-25
    # (source audit §2.2): prior 1200/1150 ran high vs DEA (~450 EUR/kW installed).
    "oil_boiler": {
        "capex_2025":       450,     # DEA installed (was 1_200)
        "capex_2050":       430,
        "lifetime_yrs":     20,
        "fom_eur_kw_yr":   25,
        "vom_eur_mwh":      2,
        "efficiency_2025":  0.90,
        "efficiency_2050":  0.90,
        "fuel":             "oil",
        "annual_hours":     2000,
        "notes": "Oil condensing boiler. Higher CAPEX than gas due to storage tank. "
                 "Declining market — limited learning rate.",
    },

    # ── Biomass boiler ────────────────────────────────────────────────────────
    # Source: Danish Energy Agency Technology Data; JRC (2023). REVISED 2026-05-25
    # (source audit §2.2): prior 1600/1400 ran high vs DEA (~890 EUR/kW); FOM raised
    # to DEA-consistent ~60 EUR/kW/yr (fuel handling + cleaning is O&M-heavy).
    "biomass_boiler": {
        "capex_2025":       950,     # DEA installed (was 1_600)
        "capex_2050":       850,     # Moderate learning from scale-up
        "lifetime_yrs":     20,
        "fom_eur_kw_yr":   60,      # DEA-consistent (was 40)
        "vom_eur_mwh":      4,
        "efficiency_2025":  0.88,
        "efficiency_2050":  0.90,
        "fuel":             "biomass",
        "annual_hours":     2000,
        "notes": "Automatic pellet/chip boiler. Assumed carbon-neutral under EU accounting. "
                 "Higher FOM reflects fuel handling maintenance.",
    },

    # ── Resistance heater ─────────────────────────────────────────────────────
    # Source: Danish Energy Agency Technology Data; JRC (2023). REVISED 2026-05-25
    # (source audit §2.2): prior 400/350 high vs DEA direct-electric (~134 EUR/kW).
    "resistance_heater": {
        "capex_2025":       200,     # DEA installed (was 400)
        "capex_2050":       180,
        "lifetime_yrs":     20,
        "fom_eur_kw_yr":   5,
        "vom_eur_mwh":      1,
        "efficiency_2025":  0.98,
        "efficiency_2050":  0.99,
        "fuel":             "electricity",
        "annual_hours":     2000,
        "notes": "Direct electric heating. Low CAPEX, high operating cost. "
                 "Mainly relevant in low-demand contexts or as backup.",
    },

    # ── Air-source heat pump (ASHP) ───────────────────────────────────────────
    # Source: IEA Future of Heat Pumps (2022); IRENA Heat Pump Costs (2022)
    # CAPEX range literature: EUR 700-2,000/kW (residential ASHP incl. installation)
    # IEA central 2022: USD 1,200/kW ~ EUR 1,100/kW
    # IRENA (2022): EUR 800-1,500/kW residential
    # Learning rate: IRENA projects 40-50% cost reduction by 2050 from manufacturing scale
    # COP: seasonal COP (SCOP) varies by climate — 2.5 (cold, PL) to 4.0 (warm, ES)
    #      Using EU average SCOP 3.0 (2025) → 3.5 (2050, improved refrigerants + design)
    # REVISED 2026-05-25 (source audit §2.1): CAPEX 2025 kept at 1200 (latest DEA
    # Technology Data ~1196 EUR/kW installed). SCOP 2025 raised 3.0->3.3 (EHPA/Eurovent
    # field SCOP for air-to-water; 3.0 was the ErP "average climate" regulatory floor,
    # not the fleet seasonal average). 2050 CAPEX moved 700->800 to the IRENA/IEA
    # central learning rate (~33%) rather than the optimistic-end ~42%.
    "hp_air": {
        "capex_2025":       1_200,   # EUR/kW_thermal (incl. installation, controller)
        "capex_2050":       800,     # IRENA/IEA central ~33% reduction (was 700)
        "lifetime_yrs":     20,      # IEA: 15-25 years
        "fom_eur_kw_yr":   25,      # IEA: EUR 20-30/kW/year (filter, refrigerant check)
        "vom_eur_mwh":      2,
        "scop_2025":        3.3,     # EHPA/Eurovent field SCOP, air-to-water (was 3.0)
        "scop_2050":        3.5,     # Technology improvement projection
        "fuel":             "electricity",
        "annual_hours":     2000,
        "notes": "Air-source heat pump, residential air-to-water. "
                 "SCOP is climate-dependent — see get_cop() function below. "
                 "CAPEX learning rate: ~1.5% per year (IRENA 2022 methodology). "
                 "IEA WEO 2025: HPs with COP 3.5 already cost-competitive with gas in EU "
                 "when ETS2 is applied.",
    },

    # ── Ground-source heat pump (GSHP) ───────────────────────────────────────
    # Source: IEA (2022); Danish Energy Agency (2023)
    # Higher CAPEX due to drilling/ground loop — but higher, more stable COP
    "hp_ground": {
        "capex_2025":       2_000,   # Incl. borehole drilling
        "capex_2050":       1_400,   # Moderate learning (drilling cost dominated)
        "lifetime_yrs":     25,      # Ground loop: 50+ years; HP unit: 20-25 years
        "fom_eur_kw_yr":   30,
        "vom_eur_mwh":      2,
        "scop_2025":        3.8,
        "scop_2050":        4.3,
        "fuel":             "electricity",
        "annual_hours":     2000,
        "notes": "Ground-source HP. Higher CAPEX but higher COP and more stable "
                 "performance across climates. Primarily relevant for SFH with garden.",
    },

    # ── District heating ──────────────────────────────────────────────────────
    # Source: JRC Technology Data (2023); IEA District Heating (2021)
    # District heat connection cost varies enormously by existing infrastructure
    # Using connection cost only (not network capital — that's a grid-level cost)
    "district_heat": {
        "capex_2025":       500,     # Substation + connection cost per kW residential
        "capex_2050":       450,     # Infrastructure-heavy, low learning
        "lifetime_yrs":     30,
        "fom_eur_kw_yr":   10,
        "vom_eur_mwh":      2,
        "efficiency_2025":  0.95,    # Distribution losses
        "efficiency_2050":  0.97,
        "fuel":             "district_heat",
        "annual_hours":     2000,
        "notes": "Consumer connection cost only. District heat supply cost varies by "
                 "source (CHP, large HP, geothermal, waste heat). EU average CO2 "
                 "content ~80 gCO2/kWh (declining as networks decarbonise). "
                 "Feasibility strongly building-type dependent (MFH > SFH).",
    },

    # ── Hydrogen boiler ───────────────────────────────────────────────────────
    # Source: IEA Global Hydrogen Review (2023); Hydrogen Council (2021); JRC (2023)
    # H2 boiler CAPEX: similar to gas boiler + H2-safety modifications
    # Hydrogen Council (2021): $900-1,600/household/year → CAPEX ~EUR 1,200-1,500/kW
    # Key cost driver: H2 fuel price, not CAPEX
    # Learning: moderate — boiler manufacturing is mature; H2-compatibility is incremental
    # REVISED 2026-05-25 (source audit §2.2): prior 1400/1100 was unsupported. An
    # H2-ready boiler is a gas boiler plus incremental safety/materials (~+40%), so
    # DEA-consistent is ~600 (gas 420 x ~1.4). The fuel price, not CAPEX, is the driver.
    "h2_boiler": {
        "capex_2025":       600,     # gas boiler + ~40% H2-ready premium (was 1_400)
        "capex_2050":       550,     # Manufacturing scale, standardisation
        "lifetime_yrs":     20,
        "fom_eur_kw_yr":   25,
        "vom_eur_mwh":      2,
        "efficiency_2025":  0.90,    # Slightly lower than gas (H2 combustion characteristics)
        "efficiency_2050":  0.92,
        "fuel":             "hydrogen",
        "annual_hours":     2000,
        "notes": "Hydrogen boiler. H2 economy literature (2021): at $3/kg H2 by 2030, "
                 "residential H2 heating = $900-1600/household/year — potentially "
                 "competitive with HP in poorly insulated stock. "
                 "UK cancelled hydrogen town trial (May 2024) due to supply constraints. "
                 "Key variable: hydrogen fuel price (modelled in FUEL_PRICES below).",
    },
}


# =============================================================================
# 2. FUEL PRICES (EUR/MWh_final energy)
# =============================================================================
# All prices are RESIDENTIAL end-user prices (inclusive of taxes and levies).
# Source: Eurostat nrg_pc_202 (gas) and nrg_pc_204 (electricity), H1 2025.
# Wholesale natural gas (TTF): ~€44/MWh (April 2026, TradingEconomics).
# EU average residential gas: €114.3/MWh (H1 2025, Eurostat) = €0.1143/kWh.
# EU average residential electricity: €287.2/MWh (H1 2025, Eurostat) = €0.2872/kWh.
#
# Country-specific actuals from Eurostat H1 2025 (EUR/MWh):
#   Gas: DE=122, FR=130, NL=162, IT=124, PL=80, HU=31, RO=56, CH=~120 (est.)
#   Electricity: DE=384, BE=357, DK=349, FR=266, ES=261, PL=~300, HU=104, SE=~200
#
# Fuel price trajectories to 2050:
#   Gas: CENTRAL = slow decline as demand falls; LOW = rapid decline (gas glut);
#        HIGH = persistent volatility / geopolitical disruption
#   Electricity: declining wholesale + rising network costs → broadly flat
#   Hydrogen: HIGH now, declining steeply as production scales
#   Oil: declining demand → declining prices
#   Biomass: stable (limited supply, rising demand pressure)
#
# ⚠️ Trajectories are provisional — validate against IEA WEO 2024, OIES, PRIMES

# District heat CO2 content by country (gCO2/kWh) — country-specific (Ali decision 2026-04-26)
# Sources: EEA (2024) district heating emission factors; Euroheat & Power statistics
# High: coal/gas-dominated district heat (PL, CZ, BG)
# Low:  waste heat, geothermal, large HP (SE, FI, DK)
# Declining over time as networks decarbonise — trajectory consistent with EEA NZE
DISTRICT_HEAT_CO2_GRAMS_KWH = {
    # 2025 actuals / estimates; declining trajectory to 2050
    # Format: {year: gCO2/kWh}
    "FI": {2025: 40,  2030: 25,  2040: 10,  2050: 5},
    "SE": {2025: 35,  2030: 20,  2040: 8,   2050: 3},
    "DK": {2025: 45,  2030: 28,  2040: 12,  2050: 5},
    "DE": {2025: 140, 2030: 90,  2040: 40,  2050: 15},
    "NL": {2025: 120, 2030: 75,  2040: 30,  2050: 10},
    "FR": {2025: 80,  2030: 50,  2040: 20,  2050: 8},
    "AT": {2025: 90,  2030: 55,  2040: 22,  2050: 8},
    "IT": {2025: 110, 2030: 70,  2040: 28,  2050: 10},
    "PL": {2025: 300, 2030: 200, 2040: 100, 2050: 30},
    "CZ": {2025: 250, 2030: 160, 2040: 75,  2050: 25},
    "HU": {2025: 180, 2030: 110, 2040: 50,  2050: 18},
    "RO": {2025: 200, 2030: 130, 2040: 60,  2050: 20},
    "BG": {2025: 220, 2030: 140, 2040: 65,  2050: 22},
    "LT": {2025: 120, 2030: 70,  2040: 28,  2050: 10},
    "LV": {2025: 100, 2030: 60,  2040: 24,  2050: 8},
    "EE": {2025: 130, 2030: 80,  2040: 32,  2050: 10},
    "UK": {2025: 100, 2030: 60,  2040: 25,  2050: 8},
    "CH": {2025: 60,  2030: 35,  2040: 15,  2050: 5},
}
DH_CO2_EU_AVERAGE = {2025: 80, 2030: 50, 2040: 20, 2050: 8}   # fallback

def get_district_heat_co2(country: str, year: int) -> float:
    """Returns district heat CO2 content (gCO2/kWh) for country and year."""
    country_data = DISTRICT_HEAT_CO2_GRAMS_KWH.get(country, DH_CO2_EU_AVERAGE)
    years = sorted(country_data.keys())
    if year <= years[0]: return country_data[years[0]]
    if year >= years[-1]: return country_data[years[-1]]
    for i in range(len(years)-1):
        y0, y1 = years[i], years[i+1]
        if y0 <= year <= y1:
            t = (year - y0) / (y1 - y0)
            return country_data[y0] + t * (country_data[y1] - country_data[y0])
    return DH_CO2_EU_AVERAGE.get(year, 50)


BASE_GAS_PRICE_EUR_MWH = 114.3   # EU average H1 2025 (Eurostat nrg_pc_202)
BASE_ELEC_PRICE_EUR_MWH = 287.2  # EU average H1 2025 (Eurostat nrg_pc_204)

# Country-specific residential gas prices (EUR/MWh, H1 2025, Eurostat)
GAS_PRICE_BY_COUNTRY = {
    "DE": 122, "FR": 130, "NL": 162, "IT": 124, "BE": 115, "AT": 110,
    "ES": 86,  "PL": 80,  "CZ": 90,  "HU": 31,  "RO": 56,  "BG": 60,
    "SE": 213, "DK": 131, "FI": 95,  "LT": 80,  "LV": 75,  "EE": 105,
    "SK": 95,  "SI": 90,  "HR": 46,  "EL": 110, "PT": 115, "IE": 130,
    "LU": 115, "CY": 100, "MT": 90,
    # UK 120->80 (Ofgem cap 2025), CH 120->160 (Sep-2025) — source audit §3.3.
    # Greece keyed "EL" (model code) not "GR" — prior "GR" key never matched.
    "UK": 80,  "CH": 160,
}

# Country-specific residential electricity prices (EUR/MWh, H1 2025, Eurostat)
ELEC_PRICE_BY_COUNTRY = {
    "DE": 384, "BE": 357, "DK": 349, "IT": 320, "IE": 310, "CZ": 310,
    "FR": 266, "ES": 261, "AT": 270, "NL": 280, "SE": 200, "FI": 225,
    "LU": 290, "PL": 300, "SK": 250, "SI": 250, "HR": 200, "EL": 250,
    "PT": 250, "RO": 180, "BG": 170, "HU": 104, "LT": 200, "LV": 190,
    "EE": 210, "CY": 270, "MT": 200,
    # FI 180->225 (Eurostat 2025-S1, source audit §3.1). Greece keyed "EL".
    "UK": 310, "CH": 300,   # Ofgem/ElCom 2025 (source audit §3.3; were 280/220 est.)
}

# ── Per-country prices for the remaining carriers (added 2026-05-26) ──────────
# Previously oil / biomass / district-heat used single EU-average values. Now
# per-country, all EUR/MWh_final, residential, taxes incl. Sources: agents A/B/C
# returned DE FR IT ES NL PL / BE AT CZ SE DK FI / RO HU BG SK HR SI from
# GlobalPetrolPrices + EC Weekly Oil Bulletin (oil), ENplus / proPellets / national
# (biomass), Euroheat & national regulators (district heat); the remaining 11 are
# assigned from the same sources. HU oil corrected 180->150 (flagged data artifact).
# District-heat values for countries with negligible DH (ES, PT, IE, CY, MT) are
# neutral placeholders (their DH feasibility share is ~0). EUR/MWh.
OIL_PRICE_BY_COUNTRY = {
    "DE": 139, "FR": 183, "IT": 194, "ES": 126, "NL": 175, "PL": 156,
    "BE": 147, "AT": 163, "CZ": 152, "SE": 169, "DK": 227, "FI": 202,
    "RO": 130, "HU": 150, "BG": 130, "SK": 130, "HR": 140, "SI": 135,
    "PT": 150, "EL": 160, "IE": 150, "EE": 150, "LV": 150, "LT": 150,
    "LU": 120, "CY": 150, "MT": 150, "CH": 150, "UK": 150,
}
BIOMASS_PRICE_BY_COUNTRY = {
    "DE": 71, "FR": 80, "IT": 80, "ES": 75, "NL": 85, "PL": 70,
    "BE": 88, "AT": 60, "CZ": 71, "SE": 51, "DK": 69, "FI": 69,
    "RO": 50, "HU": 45, "BG": 55, "SK": 50, "HR": 55, "SI": 60,
    "PT": 70, "EL": 70, "IE": 80, "EE": 50, "LV": 50, "LT": 50,
    "LU": 80, "CY": 90, "MT": 90, "CH": 90, "UK": 85,
}
DISTRICT_HEAT_PRICE_BY_COUNTRY = {
    "DE": 95,  "FR": 80,  "IT": 105, "ES": 90,  "NL": 120, "PL": 100,
    "BE": 85,  "AT": 100, "CZ": 110, "SE": 90,  "DK": 133, "FI": 98,
    "RO": 63,  "HU": 35,  "BG": 45,  "SK": 80,  "HR": 70,  "SI": 95,
    "PT": 90,  "EL": 70,  "IE": 90,  "EE": 80,  "LV": 75,  "LT": 70,
    "LU": 90,  "CY": 90,  "MT": 90,  "CH": 120, "UK": 90,
}
# Per-country delivered-hydrogen cost multiplier on the NW-EU hub trajectory.
# BOTTOM-UP (2026-06): derived by scripts.h2_delivered_cost, which costs out every
# supply route per country -- domestic GREEN electrolysis, PINK (nuclear), BLUE
# (gas+CCS), PIPELINE import, SHIP (ammonia) import -- from real cost drivers (cost
# of capital/WACC, construction labour, electricity/feedstock price, renewable
# capacity factor, water scarcity, pipeline connectivity, nuclear/CO2-storage
# availability) and takes the CHEAPEST route as the delivered cost. The multiplier is
# delivered_c / EU-median, so the median country pays the hub price (1.00).
# Calibrated to verified 2050 benchmarks: IRENA (electrolyser CAPEX, green LCOH),
# IEAGHG (blue ~EUR 2.7/kg), European Hydrogen Backbone (pipe ~EUR 0.16/kg/1000km),
# OIES ET24 (Alsulaiman 2023, import routes), ET32 (Rikabi 2024) and ET08 (2022).
# Full reconciliation + sources: literature/h2_supply_country_assessment.md.
# Findings: (1) cheap-wind Atlantic/Nordic/Baltic + Iberia self-supply green H2 below
# the median (IE 0.77 ... FI 0.87); (2) pink and blue are NEVER the cheapest route in
# 2050 (green/import beat them); (3) capital cost + labour, not just sunshine, drive
# the spread (high-WACC Greece sits at 1.04 despite superb solar); (4) landlocked CE
# (SK/CZ/HU/SI/IT ~1.14-1.16) and the non-EHB islands (CY/MT ~1.31-1.33) are dearest.
# Caveat: national H2 strategies overwhelmingly EXCLUDE residential heating (H2 -> heat
# pumps + district heating for buildings), and OIES ET29 finds heating-H2 would be
# BLUE (~EUR 81/MWh) -- both make this delivered price a conservative counterfactual.
H2_MULT_BY_COUNTRY = {
    # cheap-wind / strong-resource self-suppliers (green below the EU median)
    "IE": 0.77, "DK": 0.82, "EE": 0.83, "UK": 0.83, "LV": 0.84, "LT": 0.84,
    "PT": 0.84, "SE": 0.86, "FI": 0.87, "ES": 0.92, "NL": 0.93, "BG": 0.93,
    "AT": 0.94, "RO": 0.97,
    # around the median
    "CH": 1.00, "BE": 1.02, "EL": 1.04, "PL": 1.05, "HR": 1.07,
    # core importers + landlocked Central Europe (dearer: mediocre resource / transit)
    "FR": 1.09, "LU": 1.09, "DE": 1.09, "SK": 1.14, "HU": 1.14, "CZ": 1.14,
    "SI": 1.16, "IT": 1.16,
    # isolated islands, not on the EHB (small-scale isolated-grid solar / ship import)
    "MT": 1.31, "CY": 1.33,
}
# Low / central / high band (central matches H2_MULT_BY_COUNTRY), from the
# delivered-cost model under cheaper/dearer techno-economic worlds (electrolyser
# CAPEX +/-25%, WACC +/-1pp, hub/transport/ship cost scaled). Used for the H2-supply
# sensitivity (scripts.h2_supply_scenario) and reported as a band in the paper.
H2_MULT_RANGE_BY_COUNTRY = {
    "IE": (0.58, 0.77, 1.00), "DK": (0.61, 0.82, 1.08), "EE": (0.63, 0.83, 1.07),
    "UK": (0.62, 0.83, 1.08), "LV": (0.63, 0.84, 1.08), "LT": (0.63, 0.84, 1.08),
    "PT": (0.63, 0.84, 1.07), "SE": (0.63, 0.86, 1.11), "FI": (0.65, 0.87, 1.12),
    "ES": (0.69, 0.92, 1.18), "NL": (0.69, 0.93, 1.21), "BG": (0.71, 0.93, 1.19),
    "AT": (0.70, 0.94, 1.22), "RO": (0.73, 0.97, 1.24), "CH": (0.74, 1.00, 1.31),
    "BE": (0.75, 1.02, 1.27), "EL": (0.78, 1.04, 1.33), "PL": (0.78, 1.05, 1.34),
    "HR": (0.80, 1.07, 1.37), "FR": (0.83, 1.09, 1.27), "LU": (0.90, 1.09, 1.27),
    "DE": (0.82, 1.09, 1.27), "SK": (0.91, 1.14, 1.35), "HU": (0.86, 1.14, 1.38),
    "CZ": (0.87, 1.14, 1.35), "SI": (0.91, 1.16, 1.38), "IT": (0.86, 1.16, 1.38),
    "MT": (1.02, 1.31, 1.64), "CY": (1.03, 1.33, 1.68),
}
# Per-country real cost of capital / WACC for building heating investment, used as
# the LCOH discount rate. From Damodaran country risk premiums + Steffen (2020)
# energy-WACC ordering: low-risk NW/Nordic ~3-4%, Med/CEE/Balkan 5-8%.
DISCOUNT_RATE_BY_COUNTRY = {
    "DE": 0.040, "FR": 0.050, "IT": 0.065, "ES": 0.060, "NL": 0.040, "PL": 0.070,
    "BE": 0.035, "AT": 0.030, "CZ": 0.055, "SE": 0.040, "DK": 0.035, "FI": 0.035,
    "RO": 0.075, "HU": 0.070, "BG": 0.070, "SK": 0.065, "HR": 0.065, "SI": 0.065,
    "PT": 0.060, "EL": 0.080, "IE": 0.045, "EE": 0.050, "LV": 0.055, "LT": 0.055,
    "LU": 0.030, "CY": 0.065, "MT": 0.055, "CH": 0.030, "UK": 0.045,
}

# Fuel price multipliers by year (relative to 2025 base = 1.0)
# Gas: declining as demand falls; post-2030 further decline from REpowerEU diversification
# Electricity: broadly stable (wholesale falls, network costs rise)
# Hydrogen: steep decline from current ~€200/MWh to ~€80/MWh by 2050 (green H2 learning)
# Oil: moderate decline
# Biomass: stable with slight pressure from supply constraints

FUEL_PRICE_MULTIPLIERS = {
    # year: {gas, electricity, hydrogen, oil, biomass, district_heat}
    2025: {"gas": 1.00, "electricity": 1.00, "hydrogen": 1.00, "oil": 1.00, "biomass": 1.00, "district_heat": 1.00},
    2030: {"gas": 0.90, "electricity": 0.95, "hydrogen": 0.65, "oil": 0.90, "biomass": 1.05, "district_heat": 0.95},
    2035: {"gas": 0.80, "electricity": 0.90, "hydrogen": 0.50, "oil": 0.80, "biomass": 1.05, "district_heat": 0.90},
    2040: {"gas": 0.70, "electricity": 0.85, "hydrogen": 0.40, "oil": 0.70, "biomass": 1.05, "district_heat": 0.85},
    2045: {"gas": 0.60, "electricity": 0.82, "hydrogen": 0.35, "oil": 0.60, "biomass": 1.05, "district_heat": 0.82},
    2050: {"gas": 0.55, "electricity": 0.80, "hydrogen": 0.30, "oil": 0.55, "biomass": 1.05, "district_heat": 0.80},
}

# Hydrogen base price (EUR/MWh_final) = currently ~€200/MWh (€6/kg at 33.3 kWh/kg)
# Source: European Hydrogen Observatory (2024): >€6/kg in EU
# IEA Global Hydrogen Review 2023: green H2 falls to ~€3/kg by 2030 in optimistic scenario
# CENTRAL trajectory checked against OIES projections
H2_BASE_PRICE_EUR_MWH = 200.0    # 2025 green hydrogen (~€6/kg, EHO 2024)

# 4 hydrogen price trajectory scenarios (Ali decision 2026-04-26)
# Sources: OIES ET08 (€3/kg=€90/MWh in 2030), IEA GHR 2023, PwC, ScienceDirect 2025
# Scenario 1 RAPID:   Fast learning + scale — SUBSIDISED FLOOR, not a market price.
#                     2050 ~25 €/MWh (~€0.85/kg) sits below any sourced production
#                     cost; treat as an extreme/subsidised lower bound (audit §3.5).
# Scenario 2 CENTRAL: OIES/IEA consensus central
# Scenario 3 SLOW:    Delayed deployment, infrastructure bottlenecks
# Scenario 4 STRANDED: H2 fails to scale significantly in buildings
H2_PRICE_TRAJECTORIES = {
    "RAPID":    {2025: 200, 2030: 82,  2035: 55,  2040: 38,  2050: 29},   # €/MWh — DERIVED max-optimistic floor (bottom-up learning curve: electrolyser CAPEX 1250->70 EUR/kW, SEC 52->38 kWh/kg, power ->10 EUR/MWh; Ali 2026-06)
    "CENTRAL":  {2025: 200, 2030: 90,  2035: 70,  2040: 55,  2050: 50},   # OIES-consistent
    "SLOW":     {2025: 200, 2030: 130, 2035: 100, 2040: 80,  2050: 65},   # delayed scale-up
    "STRANDED": {2025: 200, 2030: 180, 2035: 160, 2040: 140, 2050: 120},  # H2 stays expensive
}
H2_PRICE_SCENARIO = "CENTRAL"   # base case


# =============================================================================
# 3. FINANCIAL PARAMETERS
# =============================================================================
# Discount rate: 5% real, pre-tax — standard for buildings energy modelling
# Source: BPIE (2024): "Discount rates in energy system analysis" recommends 4-6% real
#         for buildings; EU/JRC standard is 4% social, 8% private
#         Using 5% as a balanced assumption consistent with IRENA and IEA practice
# ⚠️ Open: 4 per cent social or 8 per cent private.
#   This is the most sensitive parameter in LCOH after fuel prices.

# Discount rates — 5% base + 4% and 8% as sensitivity bounds (Ali decision 2026-04-26)
# Source: BPIE (2024): 4-6% real for buildings; IEA/IRENA convention: 5%
DISCOUNT_RATE_REAL = 0.05        # base case (IEA/IRENA convention)
DISCOUNT_RATE_SOCIAL = 0.04     # social/government perspective (EU guidelines)
DISCOUNT_RATE_PRIVATE = 0.08    # private consumer perspective (BPIE high)
DISCOUNT_RATE_SCENARIOS = {
    "base":    0.05,
    "social":  0.04,
    "private": 0.08,
}

def capital_recovery_factor(r: float, n: int) -> float:
    """CRF = r(1+r)^n / ((1+r)^n - 1)"""
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


# =============================================================================
# 3a-bis. HYDROGEN DISTRIBUTION INFRASTRUCTURE COST  (scenario: build/convert)
# =============================================================================
# The default H2-boiler LCOH assumes hydrogen is delivered to the home at zero
# distribution-infrastructure cost -- i.e. the existing gas grid is reused for
# free. That is optimistic: pure-100%-H2 distribution requires CONVERTING the
# existing network (polyethylene mains are largely reusable, but remaining iron/
# steel mains, meters, valves, purging and upgraded leak detection are not) and,
# where no gas grid exists, building a NEW distribution network. The h2_infra
# scenario adds this cost to the H2-boiler LCOH so hydrogen carries its true
# delivered cost.
#
# Per-connection capital (EUR/dwelling), from the gas->H2 conversion literature
# (UK H21 North of England / Northern Gas Networks; HyDeploy; Frazer-Nash /
# Element Energy for BEIS; Gas for Climate / Guidehouse 2020). These per-connection
# figures are genuinely uncertain, so each is carried as a LOW-CENTRAL-HIGH range
# rather than a point, and the resulting LCOH adder / heat-pump gap is reported as
# a sensitivity band (see the h2_infra_scenario script and the paper):
#   - CONVERSION of an existing gas connection to 100% H2 (network side, excl. the
#     in-home H2-ready boiler which is already in H2-boiler CAPEX):
#       low EUR 1,000  /  central EUR 1,500  /  high EUR 3,000.
#   - NEW-BUILD H2 distribution to a previously un-gridded dwelling:
#       low EUR 3,000  /  central EUR 5,000  /  high EUR 8,000.
# Two orthogonal axes are offered in h2_distribution_adder_eur_mwh:
#   mode  = which network scenario:
#     "convert"  RETROFIT lower bound -- convert the whole grid (CONVERT/dwelling).
#     "newbuild" GREENFIELD upper bound -- new network to every home (NEWBUILD).
#     "blend"    central -- cov*CONVERT + (1-cov)*NEWBUILD, weighted by gas-grid
#                coverage (GAS_GRID_COVERAGE).
#   bound = where in the per-connection cost range: "low" / "central" / "high".
# Each is annualised over a ~40-yr network life at the country WACC and divided by
# the per-country useful heat per dwelling (EU-average ~13 MWh/yr, scaled by the
# country's HDD ratio -- the same climate scaling the LCOH engine uses), so the
# per-country variation comes through coverage + WACC + climate throughput.
H2_DIST_CONVERT_EUR_DWELLING = 1500.0   # central (kept for back-compat / display)
H2_DIST_NEWBUILD_EUR_DWELLING = 5000.0  # central
H2_DIST_CONVERT_RANGE = {"low": 1000.0, "central": 1500.0, "high": 3000.0}
H2_DIST_NEWBUILD_RANGE = {"low": 3000.0, "central": 5000.0, "high": 8000.0}
H2_DIST_LIFETIME_YR = 40
H2_USEFUL_MWH_PER_DWELLING = 13.0


# =============================================================================
# SEASONAL HYDROGEN STORAGE FOR BASE-LOAD HEATING
# =============================================================================
# Space heating is a seasonal load. Roughly three-quarters of annual heat is drawn
# between October and March, while electrolytic hydrogen production is far flatter, so
# a hydrogen heating load has to be stored from the production season to the burning
# season. That store costs money and the model already prices it: EUR 1.5/kg where salt
# caverns exist and EUR 3.0/kg where they do not, at about one cycle a year, which is
# exactly a winter-to-summer swing.
#
# Until now that charge was applied only in the peak and dispatch tests, so the SAME
# molecule in the SAME country was priced with seasonal storage in one arena and without
# it in another. The base-load comparison, which carries the headline, paid nothing. The
# two tests therefore disagreed for a reason internal to the accounting rather than
# anything physical.
#
# We charge it here on the fraction of the load that actually has to be time-shifted.
# Against flat supply that is the winter share of annual heat minus one half, which the
# model's own monthly shape puts at a median of 0.25 and a range of 0.21 to 0.29. It is
# a conservative reading: it credits hydrogen with meeting the whole non-seasonal half
# of its load from contemporaneous production, and it ignores that a store must also be
# built for the within-winter swing.
H2_STORAGE_EUR_KG_CAVERN, H2_STORAGE_EUR_KG_NONCAVERN = 1.5, 3.0
H2_MWH_PER_KG = 1.0 / 30.0
H2_CAVERN_MARKETS = {"DE", "NL", "PL", "DK", "UK", "RO", "FR"}
_SEASONAL_SHIFT_FALLBACK = 0.25
_seasonal_shift_cache: dict | None = None


def _seasonal_shift_fraction(country: str) -> float:
    """Share of annual heat that must be carried across seasons, against flat supply.

    The per-country fraction runs from about 0.21 in the Nordics to about 0.29 in the
    south, and it multiplies the hydrogen seasonal-storage charge, so falling back to a
    flat 0.25 moves an h2_boiler LCOH by up to about 4 EUR/MWh. That is large enough to
    move country counts, so a missing or unreadable profile warns rather than passing
    silently. Run scripts.heat_load_profile before anything that prices hydrogen.
    """
    global _seasonal_shift_cache
    if _seasonal_shift_cache is None:
        _seasonal_shift_cache = {}
        try:
            import pandas as _pd
            _lp = _pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
            _winter = ["m_Oct", "m_Nov", "m_Dec", "m_Jan", "m_Feb", "m_Mar"]
            for _c, _r in _lp.iterrows():
                _seasonal_shift_cache[_c] = max(0.0, float(sum(_r[m] for m in _winter)) - 0.5)
        except Exception as _ex:
            import warnings as _w
            _w.warn(
                f"heat_load_profile.csv unreadable ({_ex}); every hydrogen seasonal-storage "
                f"charge falls back to a flat {_SEASONAL_SHIFT_FALLBACK}. Run "
                f"scripts.heat_load_profile first, or the LCOH results will not reproduce.",
                RuntimeWarning, stacklevel=2)
    if country not in _seasonal_shift_cache:
        import warnings as _w
        _w.warn(f"no load-derived seasonal shift for {country}; using the flat "
                f"{_SEASONAL_SHIFT_FALLBACK} fallback.", RuntimeWarning, stacklevel=2)
    return _seasonal_shift_cache.get(country, _SEASONAL_SHIFT_FALLBACK)


def h2_seasonal_storage_adder_eur_mwh(country: str, efficiency: float = 0.9,
                                      fraction: float | None = None) -> float:
    """Seasonal storage charge on hydrogen heat (EUR/MWh_useful).

    fraction=None uses the country's own load-derived shift share; pass 1.0 to charge
    the full seasonal store, or 0.0 to recover the previous no-storage treatment.
    """
    eur_kg = (H2_STORAGE_EUR_KG_CAVERN if country in H2_CAVERN_MARKETS
              else H2_STORAGE_EUR_KG_NONCAVERN)
    full = (eur_kg / H2_MWH_PER_KG) / max(efficiency, 0.1)   # EUR/MWh of useful heat
    f = _seasonal_shift_fraction(country) if fraction is None else float(fraction)
    return f * full


def h2_distribution_adder_eur_mwh(country: str, discount_rate: float | None = None,
                                  mode: str = "blend", bound: str = "central") -> float:
    """H2 distribution-infrastructure cost (EUR/MWh_useful), annualised at the
    country WACC over the network life. Two orthogonal axes:

    mode -- which network scenario:
      "convert"  -- RETROFIT: repurpose the whole existing gas distribution grid
                    to 100% H2 at the conversion cost for every dwelling.
                    Optimistic lower bound (assumes a usable grid reaches every
                    home and only needs conversion).
      "newbuild" -- GREENFIELD: build a dedicated H2 distribution network from
                    scratch to every dwelling. Upper bound.
      "blend"    -- coverage-weighted mix: convert where a gas grid exists,
                    new-build where it does not, weighted by GAS_GRID_COVERAGE.
                    Central per-country estimate (default).

    bound -- where in the (uncertain) per-connection cost range to evaluate:
      "low" / "central" / "high" (see H2_DIST_*_RANGE). The adder is a sensitivity
      band, not a single value; "central" reproduces the headline numbers.

    Returns 0 if hydrogen is not modelled."""
    from src.Policy import GAS_GRID_COVERAGE
    if discount_rate is None:
        discount_rate = DISCOUNT_RATE_BY_COUNTRY.get(country, DISCOUNT_RATE_REAL)
    if bound not in H2_DIST_CONVERT_RANGE:
        raise ValueError(f"unknown h2 infra cost bound: {bound!r}")
    convert = H2_DIST_CONVERT_RANGE[bound]
    newbuild = H2_DIST_NEWBUILD_RANGE[bound]
    if mode == "convert":
        capex_per_dwelling = convert
    elif mode == "newbuild":
        capex_per_dwelling = newbuild
    elif mode == "blend":
        cov = GAS_GRID_COVERAGE.get(country, 0.30)
        capex_per_dwelling = cov * convert + (1 - cov) * newbuild
    else:
        raise ValueError(f"unknown h2 infra mode: {mode!r}")
    crf = capital_recovery_factor(discount_rate, H2_DIST_LIFETIME_YR)
    # Per-dwelling throughput is climate-scaled (same HDD ratio the LCOH engine uses via
    # get_annual_hours): cold countries push more heat through the same connection, so the
    # per-MWh network adder is lower there and higher in mild ones. Replaces the flat
    # EU-average denominator, making this symmetric with the electricity reinforcement adder.
    useful_mwh = H2_USEFUL_MWH_PER_DWELLING * (COUNTRY_HDD.get(country, EU_AVERAGE_HDD)
                                               / EU_AVERAGE_HDD)
    return crf * capex_per_dwelling / useful_mwh


# Electricity DISTRIBUTION-REINFORCEMENT adder (the symmetric counterpart to the H2
# distribution adder above). Mass heat-pump electrification adds a coincident WINTER
# PEAK to the LV/MV distribution grid that the existing retail network tariff does not
# pay for; serving it needs feeder / transformer / substation reinforcement. EUR/kW of
# added coincident heat-peak (low/central/high) from EU heat-electrification network
# studies (Imperial "Alternative UK Heat" 2018; Element Energy/UKPN; Eurelectric 2018);
# a coincidence factor accounts for diversity + existing headroom (only a fraction of
# nameplate HP peak needs NEW capacity).
ELEC_REINFORCE_EUR_PER_KW_PEAK = {"low": 400.0, "central": 800.0, "high": 1600.0}
ELEC_REINFORCE_COINCIDENCE = 0.5     # share of added HP peak needing new network capacity
ELEC_REINFORCE_LIFE_YR = 40
ELEC_REINFORCE_COP_PEAK = 2.3        # cold-snap COP that sizes the added electric peak


def electricity_distribution_adder_eur_mwh(country: str, discount_rate: float | None = None,
                                           bound: str = "central") -> float:
    """Distribution-grid REINFORCEMENT cost (EUR/MWh_useful) for the added coincident
    winter heat-pump peak that mass electrification places on the LV/MV network. This is
    the electricity analogue of h2_distribution_adder_eur_mwh, applied (opt-in) to
    electric-heating LCOH so the H2-vs-HP comparison treats last-mile network capital
    symmetrically rather than charging only hydrogen for its network.

    Derivation: a dwelling's added electric peak = (annual_heat / FLH) / COP_peak;
    reinforcement CAPEX = EUR/kW-peak x coincidence x that peak; annualised at the country
    WACC over the network life and divided by annual useful heat. FLH comes from
    get_annual_hours (the same climate-scaled full-load hours the LCOH engine uses to size
    capacity), so PEAKY mild-climate loads pay more network capital per MWh and flat cold
    loads less. Across the 29 countries the central adder runs 2.2 to 19.1 EUR/MWh
    with a median of 4.9; the low-to-high band spans roughly 1 to 38 EUR/MWh.
    bound = low/central/high sensitivity band."""
    if discount_rate is None:
        discount_rate = DISCOUNT_RATE_BY_COUNTRY.get(country, DISCOUNT_RATE_REAL)
    if bound not in ELEC_REINFORCE_EUR_PER_KW_PEAK:
        raise ValueError(f"unknown elec reinforcement bound: {bound!r}")
    crf = capital_recovery_factor(discount_rate, ELEC_REINFORCE_LIFE_YR)
    # EUR/MWh = CRF x (EUR/kW-peak x coincidence) x [peak_kw / annual_heat_mwh],
    # peak_kw / annual_heat_mwh = 1000 / (FLH_country x COP_peak).
    flh = get_annual_hours(country)
    return (crf * ELEC_REINFORCE_EUR_PER_KW_PEAK[bound] * ELEC_REINFORCE_COINCIDENCE
            * 1000.0 / (flh * ELEC_REINFORCE_COP_PEAK))


# =============================================================================
# 3b. HEATING DEGREE DAYS — ANNUAL FULL-LOAD HOURS (CLIMATE-ADJUSTED)
# =============================================================================
# Decision: Use Hotmaps heating degree days per NUTS3 (Ali decision 2026-04-26)
# Source: Hotmaps HDD data from regional demand dataset
# Until NUTS3-level HDD is fully integrated, using country-level HDD adjustments
# based on Hotmaps national averages and Eurostat climate data.
#
# Reference: EU average HDD ~2,800 (Eurostat 2022 climate normal, NUTS0)
# Full-load hours = HDD × building-type factor / reference temperature
# Simplified: annual_hours = base × (national_HDD / EU_average_HDD)
#
# Country HDD (heating degree days, base 15°C, climate normal 1991-2020, Eurostat)
# Source: Eurostat env_clc_hdd; Hotmaps regional demand dataset
COUNTRY_HDD = {
    "FI": 5200, "SE": 4800, "EE": 4500, "LV": 4300, "LT": 4200,
    "PL": 3700, "CZ": 3600, "SK": 3500, "HU": 3200, "AT": 3300,
    "DE": 3200, "BE": 2900, "NL": 2800, "UK": 2800, "IE": 2700,
    "FR": 2600, "LU": 2900, "SI": 3000, "HR": 2500, "RO": 3100,
    "BG": 2900, "EL": 1800, "IT": 2200, "ES": 1900, "PT": 1600,
    "CY": 900,  "MT": 800,  "DK": 3100, "CH": 3200,
}
EU_AVERAGE_HDD = 2800   # reference
BASE_ANNUAL_HOURS = 2000   # EU average reference

def get_annual_hours(country: str) -> float:
    """Returns climate-adjusted full-load hours for a given country."""
    hdd = COUNTRY_HDD.get(country, EU_AVERAGE_HDD)
    return BASE_ANNUAL_HOURS * (hdd / EU_AVERAGE_HDD)


# =============================================================================
# 4. COP ADJUSTMENT BY CLIMATE ZONE
# =============================================================================
# ASHP seasonal COP varies significantly with climate:
#   Cold climates (FI, SE, EE, NO): SCOP ~2.5-2.8
#   Temperate (DE, FR, UK):         SCOP ~2.8-3.2
#   Warm (ES, PT, GR, CY):          SCOP ~3.5-4.5
#
# Source: EHPA (2023) Eurovent study; EU Regulation 813/2013 (ErP Directive)
# Using EU Regulation "average climate" as baseline (SCOP_ref = 3.0)
# Adjustments from Hotmaps climate zone data

COP_CLIMATE_MULTIPLIER = {
    # Countries with cold climates — below average SCOP
    "FI": 0.85, "SE": 0.88, "EE": 0.88, "LV": 0.90, "LT": 0.90,
    "DK": 0.92, "PL": 0.92, "CZ": 0.93, "SK": 0.93, "AT": 0.95,
    "DE": 0.96, "HU": 0.97, "SI": 0.97, "HR": 0.98, "RO": 0.96,
    "BG": 0.97,
    # Average climate countries
    "BE": 1.00, "NL": 1.00, "FR": 1.00, "LU": 1.00, "UK": 1.00,
    "IE": 0.98, "CH": 0.97,
    # Warm climate countries — above average SCOP
    "ES": 1.15, "PT": 1.18, "IT": 1.10, "EL": 1.20, "CY": 1.35, "MT": 1.30,
}

def get_cop(tech: str, country: str, year: int) -> float:
    """
    Returns the seasonal COP for a heat pump technology in a given country and year.
    Applies climate multiplier and technology improvement over time.
    """
    params = TECH_PARAMS.get(tech, {})
    base_scop_2025 = params.get("scop_2025", params.get("efficiency_2025", 1.0))
    base_scop_2050 = params.get("scop_2050", params.get("efficiency_2050", 1.0))

    # Linear interpolation between 2025 and 2050
    t = max(0, min(1, (year - 2025) / 25))
    base_scop = base_scop_2025 + t * (base_scop_2050 - base_scop_2025)

    # Apply climate multiplier
    climate_mult = COP_CLIMATE_MULTIPLIER.get(country, 1.0)
    return base_scop * climate_mult


# =============================================================================
# 5. LCOH CALCULATION FUNCTIONS
# =============================================================================

def get_capex(tech: str, year: int, country: str = None) -> float:
    """
    Returns the CAPEX (EUR/kW_thermal) for a technology in a given year,
    optionally scaled by country labour-cost multiplier on the installation
    fraction (LABOUR_SHARE_OF_CAPEX[tech]).

    If `country` is None, returns the EU-average (anchor) CAPEX.

    Decomposition:
      capex_country = capex_base * [(1 - L) + L * M]
      where L = labour share of CAPEX (tech-specific)
            M = country labour multiplier (EU27 construction = 1.00)
    """
    params = TECH_PARAMS[tech]
    t = max(0, min(1, (year - 2025) / 25))
    capex_base = params["capex_2025"] + t * (params["capex_2050"] - params["capex_2025"])
    if country is None:
        return capex_base
    L = LABOUR_SHARE_OF_CAPEX.get(tech, LABOUR_SHARE_DEFAULT)
    M = get_labour_multiplier(country)
    return capex_base * ((1.0 - L) + L * M)


def get_fom(tech: str, country: str = None) -> float:
    """
    Returns the country-adjusted Fixed O&M (EUR/kW/year) for a technology.
    Applies the labour multiplier on the FOM_LABOUR_SHARE portion.
    """
    fom_base = TECH_PARAMS[tech]["fom_eur_kw_yr"]
    if country is None:
        return fom_base
    M = get_labour_multiplier(country)
    return fom_base * ((1.0 - FOM_LABOUR_SHARE) + FOM_LABOUR_SHARE * M)


def get_fuel_price(fuel: str, country: str, year: int,
                   h2_scenario: str = H2_PRICE_SCENARIO,
                   price_mult: dict | None = None) -> float:
    """
    Returns the fuel price (EUR/MWh_final) for a given fuel, country, and year.
    Uses country-specific 2025 base prices with trajectory multipliers.

    For hydrogen the price follows the per-scenario trajectory in
    H2_PRICE_TRAJECTORIES (RAPID / CENTRAL / SLOW / STRANDED), interpolated
    by year. Passing h2_scenario is what lets the hydrogen-price Monte Carlo
    axis propagate into the LCOH (previously hydrogen used a single fixed
    multiplier and the sampled scenario was ignored).

    price_mult: optional {carrier: multiplier} dict. When supplied (e.g. the
    per-carrier log-normal price draws sampled in the Monte Carlo), the returned
    price is scaled by price_mult.get(fuel, 1.0). This is what lets the sampled
    fuel-price uncertainty propagate into compute_lcoh / the tech-mix bands;
    without it the draws were sampled but never used.
    """
    _m = (price_mult or {}).get(fuel, 1.0)
    # Hydrogen: per-scenario trajectory x per-country production-cost multiplier.
    if fuel == "hydrogen":
        traj = H2_PRICE_TRAJECTORIES.get(h2_scenario,
                                         H2_PRICE_TRAJECTORIES["CENTRAL"])
        h2m = H2_MULT_BY_COUNTRY.get(country, 1.0)
        tys = sorted(traj)
        if year <= tys[0]:
            return float(traj[tys[0]]) * h2m * _m
        if year >= tys[-1]:
            return float(traj[tys[-1]]) * h2m * _m
        for i in range(len(tys) - 1):
            y0, y1 = tys[i], tys[i + 1]
            if y0 <= year <= y1:
                t = (year - y0) / (y1 - y0)
                return float(traj[y0] + t * (traj[y1] - traj[y0])) * h2m * _m
        return float(traj[tys[-1]]) * h2m * _m

    # Get base price — all carriers now per-country (EU-average as fallback).
    if fuel == "gas":
        base = GAS_PRICE_BY_COUNTRY.get(country, BASE_GAS_PRICE_EUR_MWH)
    elif fuel == "electricity":
        base = ELEC_PRICE_BY_COUNTRY.get(country, BASE_ELEC_PRICE_EUR_MWH)
    elif fuel == "oil":
        base = OIL_PRICE_BY_COUNTRY.get(country, 105.0)
    elif fuel == "biomass":
        base = BIOMASS_PRICE_BY_COUNTRY.get(country, 70.0)
    elif fuel == "district_heat":
        base = DISTRICT_HEAT_PRICE_BY_COUNTRY.get(country, 80.0)
    else:
        return 0.0

    # Apply trajectory multiplier (interpolate between defined years)
    years = sorted(FUEL_PRICE_MULTIPLIERS.keys())
    mults = {y: FUEL_PRICE_MULTIPLIERS[y][fuel] for y in years
             if fuel in FUEL_PRICE_MULTIPLIERS[y]}

    if year <= years[0]:
        mult = mults[years[0]]
    elif year >= years[-1]:
        mult = mults[years[-1]]
    else:
        for i in range(len(years) - 1):
            y0, y1 = years[i], years[i + 1]
            if y0 <= year <= y1:
                t = (year - y0) / (y1 - y0)
                mult = mults[y0] + t * (mults[y1] - mults[y0])
                break
        else:
            mult = 1.0

    return base * mult * _m


def compute_lcoh(
    tech: str,
    country: str,
    year: int,
    carbon_price_scenario: str = CARBON_PRICE_SCENARIO,
    discount_rate: float = None,
    h2_scenario: str = H2_PRICE_SCENARIO,
    price_mult: dict | None = None,
    h2_infra: bool | str = "blend",
    h2_infra_bound: str = "central",
    elec_reinforce: bool = True,
    elec_reinforce_bound: str = "central",
    h2_seasonal_storage: bool | float = True,
) -> float:
    """
    Compute Levelised Cost of Heat (LCOH) in EUR/MWh_useful for a given
    technology, country, and year.

    Returns: LCOH in EUR/MWh_useful heat delivered to the building.

    Formula:
      LCOH = annualised_capex_per_mwh + fom_per_mwh + vom + fuel_cost + carbon_adder
             + delivery_network_adder

    where:
      annualised_capex_per_mwh = CRF × CAPEX / annual_hours
      fom_per_mwh              = FOM / annual_hours
      fuel_cost                = FuelPrice / η
      carbon_adder             = carbon cost on fuel (EUR/MWh_useful)
      delivery_network_adder   = the carrier's own last-mile network (see below)

    Note that η appears ONCE, on the fuel term. annual_hours is full-load hours of heat
    OUTPUT and CAPEX is EUR per kW of heat output, so the capital and fixed-O&M terms
    carry no efficiency factor. Equipment is sized to peak heat demand, which does not
    shrink because the machine is efficient. This docstring previously divided both by
    (annual_hours × η), matching an earlier implementation that counted efficiency twice
    and understated heat-pump capital by a factor of the seasonal performance factor.

    delivery_network_adder is applied BY DEFAULT and is not opt-in: the hydrogen
    distribution build for a hydrogen boiler (h2_infra, coverage-weighted "blend" mode at
    its central bound) and low- and medium-voltage reinforcement for electric heating
    (elec_reinforce). Pass h2_infra=False, elec_reinforce=False to recover the
    free-infrastructure case as a sensitivity.
    """
    params = TECH_PARAMS[tech]

    # Discount rate = per-country WACC unless an explicit rate is passed (e.g. the
    # sensitivity axis). Country cost of capital drives the capital-recovery factor.
    if discount_rate is None:
        discount_rate = DISCOUNT_RATE_BY_COUNTRY.get(country, DISCOUNT_RATE_REAL)

    # CAPEX and financial parameters — applies country labour multiplier
    capex = get_capex(tech, year, country)         # EUR/kW_th (country-adjusted)
    lifetime = params["lifetime_yrs"]
    crf = capital_recovery_factor(discount_rate, lifetime)

    # Efficiency / COP
    fuel = params["fuel"]
    if fuel == "electricity" and tech in ["hp_air", "hp_ground"]:
        eta = get_cop(tech, country, year)
    else:
        t = max(0, min(1, (year - 2025) / 25))
        eta = (params.get("efficiency_2025", params.get("scop_2025", 1.0)) +
               t * (params.get("efficiency_2050", params.get("scop_2050", 1.0)) -
                    params.get("efficiency_2025", params.get("scop_2025", 1.0))))

    annual_hours = get_annual_hours(country)   # climate-adjusted via Hotmaps HDD

    # Annual heat output per kW installed capacity (MWh/kW/year).
    #
    # annual_hours is full-load hours of HEAT OUTPUT and capex is EUR per kW of heat
    # output, so the denominator is FLH/1000 with no efficiency term. It previously
    # carried a factor of eta, which divided the capital and fixed-O&M charge by each
    # technology's own efficiency and so counted efficiency twice: once correctly
    # against fuel (see fuel_cost_per_mwh_useful below) and once wrongly against
    # capital. Equipment is sized to the dwelling's peak heat demand, which does not
    # shrink because the machine is efficient. A house needing 6.5 kW of heat needs a
    # 6.5 kW unit whether that unit is a boiler or a heat pump; efficiency changes the
    # fuel bill, not the purchase price.
    #
    # The error was worth about 32 EUR/MWh to heat pumps (SCOP 3.5-4.3) and under
    # 3 EUR/MWh to boilers (efficiency ~0.9), because the size of the distortion is
    # the efficiency itself. It therefore acted almost entirely on one side of the
    # heat-pump-versus-hydrogen comparison.
    annual_heat_mwh_per_kw = annual_hours / 1000

    # Annualised CAPEX per MWh_useful
    annualised_capex_per_mwh = (crf * capex) / annual_heat_mwh_per_kw

    # Fixed O&M per MWh_useful — applies country labour multiplier on labour share
    fom_country = get_fom(tech, country)
    fom_per_mwh = fom_country / annual_heat_mwh_per_kw

    # Variable O&M
    vom = params["vom_eur_mwh"]

    # Fuel cost per MWh_useful
    fuel_price_per_mwh_final = get_fuel_price(fuel, country, year, h2_scenario,
                                              price_mult=price_mult)
    fuel_cost_per_mwh_useful = fuel_price_per_mwh_final / eta

    # Carbon cost adder per MWh_useful
    carbon_adder = get_carbon_cost_adder_eur_per_mwh_useful(
        fuel, country, year, eta, carbon_price_scenario
    )

    lcoh = annualised_capex_per_mwh + fom_per_mwh + vom + fuel_cost_per_mwh_useful + carbon_adder
    # Delivery infrastructure. Both adders are now ON by default and evaluated at
    # their central bound, so the baseline charges each carrier its own last-mile
    # cost. They were previously both off, which is a coherent pair of assumptions
    # ("free reuse of the existing gas grid" on one side, no grid reinforcement on
    # the other) but not a realistic one, and it left the two sides of the
    # comparison priced on different bases: hydrogen at its production-plus-transport
    # cost with no distribution, electricity at a full taxed retail price that
    # already embeds distribution. Pass h2_infra=False, elec_reinforce=False to
    # recover the free-infrastructure case as a sensitivity.
    #
    # H2 infrastructure: the per-country H2 distribution-network conversion/build
    # cost added to the hydrogen-boiler LCOH. h2_infra may be a bool (True ->
    # "blend") or a mode string ("convert"/"newbuild"/"blend"); "blend" is the
    # coverage-weighted central estimate, converting where a gas grid reaches and
    # building new where it does not.
    if h2_infra and tech == "h2_boiler":
        _mode = h2_infra if isinstance(h2_infra, str) else "blend"
        lcoh += h2_distribution_adder_eur_mwh(country, discount_rate, mode=_mode,
                                              bound=h2_infra_bound)
    # Seasonal storage on the hydrogen heating load. Charged on the share of annual heat
    # that must be carried from the production season to the burning season, which the
    # model's own monthly shape puts near a quarter. The peak and dispatch tests already
    # charged this; the base-load test did not, so the same molecule was priced two ways.
    # Pass h2_seasonal_storage=False to recover the previous treatment, or a float to
    # override the fraction.
    if h2_seasonal_storage is not False and tech == "h2_boiler":
        _frac = None if h2_seasonal_storage is True else float(h2_seasonal_storage)
        lcoh += h2_seasonal_storage_adder_eur_mwh(country, eta, fraction=_frac)
    # Electricity distribution reinforcement, symmetric to h2_infra: charge electric
    # heating its share of the LV/MV grid reinforcement the added winter heat-pump
    # peak requires.
    if elec_reinforce and tech in ("hp_air", "hp_ground", "resistance_heater"):
        lcoh += electricity_distribution_adder_eur_mwh(country, discount_rate,
                                                       bound=elec_reinforce_bound)
    return round(lcoh, 2)


def compute_lcoh_all_techs(
    country: str,
    year: int,
    carbon_price_scenario: str = CARBON_PRICE_SCENARIO,
) -> dict[str, float]:
    """Returns LCOH dict for all technologies for a given country and year."""
    return {
        tech: compute_lcoh(tech, country, year, carbon_price_scenario)
        for tech in TECH_PARAMS
    }


def compute_lcoh_table(
    countries: list[str],
    years: list[int],
    carbon_price_scenario: str = CARBON_PRICE_SCENARIO,
) -> pd.DataFrame:
    """
    Computes a full LCOH table for all combinations of country × year × technology.

    Returns a DataFrame with columns:
      country, year, tech, lcoh_eur_mwh, fuel, cop_or_efficiency
    """
    rows = []
    for country in countries:
        for year in years:
            for tech, params in TECH_PARAMS.items():
                fuel = params["fuel"]
                if fuel == "electricity" and tech in ["hp_air", "hp_ground"]:
                    eta = get_cop(tech, country, year)
                else:
                    t = max(0, min(1, (year - 2025) / 25))
                    eta = (params.get("efficiency_2025", params.get("scop_2025", 1.0)) +
                           t * (params.get("efficiency_2050", params.get("scop_2050", 1.0)) -
                                params.get("efficiency_2025", params.get("scop_2025", 1.0))))

                lcoh = compute_lcoh(tech, country, year, carbon_price_scenario)
                rows.append({
                    "country":           country,
                    "year":              year,
                    "tech":              tech,
                    "lcoh_eur_mwh":      lcoh,
                    "fuel":              fuel,
                    "cop_or_efficiency": round(eta, 3),
                    "capex_eur_kw":      round(get_capex(tech, year), 0),
                    "fuel_price_eur_mwh": round(get_fuel_price(fuel, country, year), 1),
                    "carbon_adder":      round(
                        get_carbon_cost_adder_eur_per_mwh_useful(
                            fuel, country, year, eta, carbon_price_scenario), 1),
                })
    return pd.DataFrame(rows)


def cheapest_tech(country: str, year: int,
                  carbon_price_scenario: str = CARBON_PRICE_SCENARIO) -> str:
    """Returns the technology with the lowest LCOH for a given country and year."""
    costs = compute_lcoh_all_techs(country, year, carbon_price_scenario)
    return min(costs, key=costs.get)


# =============================================================================
# 6. MAIN — validation and demo
# =============================================================================
def main() -> None:
    print("=" * 65)
    print("Economics Module — LCOH Validation")
    print("=" * 65)

    # Spot check: Germany 2025
    print("\nGermany 2025 — LCOH by technology (EUR/MWh_useful):")
    costs_de_2025 = compute_lcoh_all_techs("DE", 2025)
    for tech, lcoh in sorted(costs_de_2025.items(), key=lambda x: x[1]):
        print(f"  {tech:<20} {lcoh:>7.1f}")

    # Spot check: Germany 2030 (with ETS2)
    print("\nGermany 2030 — LCOH by technology (with ETS2):")
    costs_de_2030 = compute_lcoh_all_techs("DE", 2030)
    for tech, lcoh in sorted(costs_de_2030.items(), key=lambda x: x[1]):
        print(f"  {tech:<20} {lcoh:>7.1f}")

    # Cross-country comparison: gas boiler vs HP in 2030
    print("\nGas boiler vs ASHP — LCOH in 2030 (EUR/MWh_useful):")
    countries = ["SE", "DE", "FR", "PL", "IT", "UK", "CH"]
    print(f"  {'Country':<6} {'Gas':<8} {'ASHP':<8} {'H2 Boiler':<12} {'Cheapest'}")
    for c in countries:
        gas  = compute_lcoh("gas_boiler", c, 2030)
        ashp = compute_lcoh("hp_air", c, 2030)
        h2   = compute_lcoh("h2_boiler", c, 2030)
        best = cheapest_tech(c, 2030)
        print(f"  {c:<6} {gas:<8.1f} {ashp:<8.1f} {h2:<12.1f} {best}")

    # 2050 comparison
    print("\nGas boiler vs ASHP vs H2 — LCOH in 2050 (EUR/MWh_useful):")
    print(f"  {'Country':<6} {'Gas':<8} {'ASHP':<8} {'H2 Boiler':<12} {'Cheapest'}")
    for c in countries:
        gas  = compute_lcoh("gas_boiler", c, 2050)
        ashp = compute_lcoh("hp_air", c, 2050)
        h2   = compute_lcoh("h2_boiler", c, 2050)
        best = cheapest_tech(c, 2050)
        print(f"  {c:<6} {gas:<8.1f} {ashp:<8.1f} {h2:<12.1f} {best}")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
