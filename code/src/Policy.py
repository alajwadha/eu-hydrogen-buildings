"""
code/src/Policy.py
==================
Country-level policy parameters for the EU+CH+UK buildings heat model.

Covers all 29 modelled countries (EU27 + CH + UK) across four policy dimensions:
  1. Boiler bans / fossil fuel heating phase-out schedules
  2. Carbon pricing trajectories (EU ETS1 + ETS2 for buildings)
  3. Electricity grid carbon intensity by country (gCO2e/kWh), 2025-2050
  4. Gas grid coverage (% of households on gas network) — hydrogen infrastructure proxy
  5. Switzerland-specific hydrogen policy parameters (RQ2)

All values are research-derived with sources documented inline.
Parameters flagged ⚠️ are provisional estimates rather than sourced values.

Primary sources:
  - EHPA (2025): European Heat Pump Association boiler ban tracker
  - EPBD (2024): Energy Performance of Buildings Directive (EU) 2024/1275
  - BloombergNEF (2025): EU ETS II Market Outlook — carbon price €149/t by 2030
  - Enerdata (2025): EU ETS carbon price forecast, POLES model
  - EMBER (2024): European Electricity Review — grid carbon intensity by country
  - EEA (2024): GHG emission intensity of electricity generation, country level
  - Eurostat (2023): Energy consumption in households, nrg_d_hhq
  - Odyssee-MURE (2024): Switzerland energy efficiency and trends
  - SFOE / Prognos (2023): Swiss Energy Perspectives 2050+
  - IEA (2023): Switzerland Energy Policy Review
  - Swiss NDC Annex (2025): Switzerland 2031-2035 NDC submission to UNFCCC
"""

# =============================================================================
# 1. BOILER BANS AND HP MANDATES BY COUNTRY
# =============================================================================
# Structure per country:
#   fossil_boiler_subsidies_end: year after which subsidies for fossil boilers end
#   new_build_fossil_ban:        year after which fossil boilers banned in new buildings
#   replacement_fossil_ban:      year after which fossil boilers banned at point of replacement
#   full_fossil_ban:             year of complete fossil boiler phase-out (existing stock)
#   hp_mandate_year:             year from which HP (or hybrid) becomes mandatory at replacement
#   notes:                       key qualifications
#
# EU-wide baseline from EPBD 2024:
#   - Subsidies end:          2025 (all member states)
#   - Full phase-out target:  2040 (member state roadmaps required)
#   - New build zero-emission: 2030 (2028 for public buildings)
#
# Sources: EHPA boiler ban tracker (Nov 2025), EPBD 2024, national legislation

BOILER_BANS = {
    # ── NORDICS — most aggressive ───────────────────────────────────────────
    "DK": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2013,   # gas network ban for new builds (2013)
        "replacement_fossil_ban": 2030,  # target via district heat + HP
        "full_fossil_ban": 2035,
        "hp_mandate_year": 2030,
        "notes": "Gas network connection banned in new buildings since 2013. "
                 "Target: 50% connected to district heating by 2028. "
                 "70% CO2 reduction by 2030 vs 1990.",
    },
    "SE": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2022,
        "replacement_fossil_ban": 2030,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2030,
        "notes": "Strong district heating + HP market. Very low gas grid coverage. "
                 "48% of residential energy from electricity (2023, Eurostat).",
    },
    "FI": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2025,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "High district heating penetration. Oil boiler ban in new builds. "
                 "Gas grid coverage very low outside Helsinki metro.",
    },
    # ── WESTERN EUROPE — fast movers ───────────────────────────────────────
    "NL": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2018,   # gas network ban in new builds since 2018
        "replacement_fossil_ban": 2026,  # hybrid HP mandatory at replacement from 2026
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2026,
        "notes": "Gas network banned for new buildings since 2018. "
                 "Hybrid HP mandatory at replacement from 2026. "
                 "72.9% of residential space heating still from gas (2023, Eurostat). "
                 "Highest gas dependency in EU — transition particularly challenging.",
    },
    "DE": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2024,   # 65% renewable energy rule from 2024
        "replacement_fossil_ban": 2028,  # delayed from 2024 after political backlash
        "replacement_fossil_ban_delayed": 2035,  # German backlash scenario (far-right leverage)
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2028,
        "hp_mandate_year_delayed": 2035,  # German backlash scenario
        "notes": "GEG (Building Energy Act) 2024: all new heating systems must use "
                 "≥65% renewable energy. Implementation delayed from 2024 to 2028 "
                 "for replacements after strong public opposition. Target: 6M HPs by 2030.",
    },
    "AT": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2020,   # oil boilers banned in new builds
        "replacement_fossil_ban": 2025,  # ban on repair of old systems + new installs
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2025,
        "notes": "Austria banned repair of old fossil heating and new installs from 2025. "
                 "Extended ban from gas only to all fossil fuels as of 2025 (EHPA).",
    },
    "FR": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2022,   # gas/oil banned in new SFH from 2022
        "replacement_fossil_ban": 2025,  # extended to MFH after 2025
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2025,
        "notes": "Gas/oil boilers banned in new single-family homes from 2022. "
                 "Extended to multi-family homes after 2025. MaPrimeRénov' subsidy scheme. "
                 "France among the most proactive EU states on boiler phase-out.",
    },
    "BE": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2025,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "Fossil fuel heating systems banned in new buildings from 2025. "
                 "Flanders has separate regional policy.",
    },
    "IE": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2025,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2030,
        "notes": "Boiler ban broadened to residential homes and gas in new buildings (EHPA 2025). "
                 "41.7% of residential energy from petroleum products (highest EU share). "
                 "Target: 600,000 HP installations 2021-2030.",
    },
    "LU": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2025,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2030,
        "notes": "45.3% residential energy from gas (2023, Eurostat). "
                 "High income country — transition financing less of a barrier.",
    },
    # ── SOUTHERN EUROPE ────────────────────────────────────────────────────
    "IT": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2025,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "Steps being taken toward ban (ECOS/EHPA). 53.5% residential space "
                 "heating from gas (2023, Eurostat). Superbonus scheme previously "
                 "accelerated renovations but was scaled back in 2023.",
    },
    "ES": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "Relatively low heating demand per dwelling (warm climate). "
                 "National NECP targets HP deployment but no formal boiler ban yet.",
    },
    "PT": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "88.2% residential space heating from renewables (mainly biomass, 2023). "
                 "Low gas dependency — transition pathway is biomass → HP.",
    },
    "EL": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "40.9% residential space heating from oil products (2023, Eurostat). "
                 "Significant oil boiler stock — transition requires active policy.",
    },
    "CY": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "60.3% residential space heating from oil (2023). "
                 "Near-100% solar water heater penetration — unique building profile.",
    },
    "MT": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "75.4% residential energy from electricity (highest EU share, 2023). "
                 "Mild climate — low absolute heating demand.",
    },
    # ── CENTRAL/EASTERN EUROPE — laggards ─────────────────────────────────
    "PL": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2040,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2040,
        "notes": "20.6% residential energy from solid fossil fuels (coal). "
                 "Poland protested EU ETS2 price projections (€149/t by 2030). "
                 "Transition constrained by coal dependency and lower incomes. "
                 "Government previously hostile to rapid phase-out.",
    },
    "CZ": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2038,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2038,
        "notes": "40% coal in electricity mix (2023, EMBER). High grid carbon intensity. "
                 "HP environmental benefit depends critically on grid decarbonisation.",
    },
    "HU": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2038,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2038,
        "notes": "46.4% residential energy from gas (2023). "
                 "Strong district heating infrastructure in urban areas.",
    },
    "SK": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2038,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2038,
        "notes": "CEE country — transition pace constrained by income levels and "
                 "coal/gas heating dependency.",
    },
    "RO": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2040,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2040,
        "notes": "2.5M dwellings heated directly by gas; 3.5M by solid fuel (wood/coal). "
                 "Romanian authorities cited unaffordability of rapid transition. "
                 "54.3% residential energy from renewables (mostly biomass). "
                 "Gradual approach: new collective housing first.",
    },
    "BG": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2040,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2040,
        "notes": "51.7% residential energy from electricity (2023). "
                 "High electricity carbon intensity — HP benefit limited until grid decarbonises.",
    },
    "HR": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2030,
        "replacement_fossil_ban": 2038,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2038,
        "notes": "44.9% residential energy from renewables (biomass). "
                 "Highest energy consumption per dwelling in EU after climate adjustment.",
    },
    "SI": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2028,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "40% residential energy from renewables (2023). "
                 "District heating significant in urban areas.",
    },
    # ── BALTICS ────────────────────────────────────────────────────────────
    "EE": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2028,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "39.5% residential energy from renewables. "
                 "Largest gas demand reduction since 2022 (Bruegel tracker) — "
                 "strong response to Russia's invasion of Ukraine.",
    },
    "LV": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2028,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "40.6% residential energy from renewables (2023). "
                 "Significant district heating penetration.",
    },
    "LT": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2028,
        "replacement_fossil_ban": 2035,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2035,
        "notes": "Among largest gas demand reductions since 2022 (Bruegel). "
                 "Rapidly decarbonising — Baltic states accelerated transition post-Ukraine war.",
    },
    # ── NON-EU ─────────────────────────────────────────────────────────────
    "CH": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2023,   # cantons implementing renewable-only new builds
        "replacement_fossil_ban": 2030,
        "full_fossil_ban": 2040,
        "hp_mandate_year": 2030,
        "notes": "CO2 levy on thermal fossil fuels: CHF 120/tCO2 since 2022. "
                 "Conference of Cantonal Energy Directors 2050+ policy: mandating "
                 "renewable heating for new buildings and systems, expanding district "
                 "heating, dismantling gas grids or transitioning to green hydrogen. "
                 "Energy Strategy 2050: target 1.5M HPs (from 0.3M today). "
                 "Buildings account for ~1/3 of Swiss CO2 emissions.",
    },
    "UK": {
        "fossil_boiler_subsidies_end": 2025,
        "new_build_fossil_ban": 2025,   # Future Homes Standard 2025
        "replacement_fossil_ban": 2035,  # delayed from 2026 by Sunak (oil/LPG)
        "full_fossil_ban": 2035,
        "hp_mandate_year": 2030,
        "notes": "Future Homes Standard (2025): fossil fuel heating banned in new builds. "
                 "Gas boiler ban in new builds pushed to 2035 (from 2025 under Sunak). "
                 "Boiler Upgrade Scheme: £7,500 grant for ASHP/GSHP. "
                 "EHPA (Nov 2025): UK likely to end fossil fuel boilers in new buildings from 2026.",
    },
}


# =============================================================================
# 2. CARBON PRICING TRAJECTORIES
# =============================================================================
# Two systems apply to the buildings sector:
#
# A) EU ETS1 (existing, covers large industry + power — affects electricity prices)
#    Current price: ~€65-70/tCO2 (2025)
#    Trajectories: BNEF: €149/t by 2030; Enerdata/POLES: €70-100/t by 2030
#
# B) EU ETS2 (NEW — covers buildings + road transport + small industry)
#    Launch: 2027
#    Price cap: €45/t initially (price stability reserve mechanism)
#    BNEF forecast: €122/t by 2030 (high scenario); €99/t average 2027-2030
#    Academic range (PRIMES model): €71-261/tCO2 by 2030 depending on complementary policies
#    ETS2 futures (ICE, May 2025): ~€75/tCO2
#
# C) National carbon taxes (supplement or replace ETS2 for non-covered sectors)
#    Switzerland: CHF 120/tCO2 on thermal fossil fuels (since 2022)
#    Sweden, Finland, Netherlands: among highest national carbon taxes in world
#
# For the model we use three carbon price scenarios applied to fuel costs:
#   LOW:    Conservative — ETS2 price cap holds, complementary policies effective
#   CENTRAL: BNEF central forecast — most likely
#   HIGH:   PRIMES high scenario — limited complementary policies, high price

CARBON_PRICE_EUR_PER_TCO2 = {
    # Year: {LOW, CENTRAL, HIGH}
    2025: {"LOW": 30,  "CENTRAL": 55,  "HIGH": 70},    # ETS1 only, buildings not yet covered
    2027: {"LOW": 45,  "CENTRAL": 75,  "HIGH": 100},   # ETS2 launch (price cap = €45 initially)
    2030: {"LOW": 70,  "CENTRAL": 122, "HIGH": 200},   # BNEF central = €122; PRIMES high = €261
    2035: {"LOW": 100, "CENTRAL": 150, "HIGH": 250},   # ⚠️ Interpolated between the 2030 and 2040 anchors; no published 2035 figure
    2040: {"LOW": 130, "CENTRAL": 180, "HIGH": 300},   # ⚠️ Enerdata: "almost doubles by 2040 vs 2027"
    2050: {"LOW": 150, "CENTRAL": 200, "HIGH": 350},   # ⚠️ Literature uncertain — Enerdata POLES model
}

# Default scenario for model runs (can be overridden in Config.py)
# Carbon price scenario — run all three as sensitivity axis (Ali decision 2026-04-26)
# Use CARBON_PRICE_SCENARIOS list to iterate; CARBON_PRICE_SCENARIO is the base
CARBON_PRICE_SCENARIO = "CENTRAL"   # base case
CARBON_PRICE_SCENARIOS = ["LOW", "CENTRAL", "HIGH"]   # all three for sensitivity

# ETS2 pass-through rate to residential consumers
# Decision: flag as sensitivity — run both 100% and 75%
# 100% = full policy signal passes to end consumers
# 75%  = realistic (regulated tariffs, supplier absorption of some cost)
# Sources: PRIMES model documentation; EC impact assessment ETS2 (2023)
ETS2_PASSTHROUGH_RATE = 1.00          # base case (100%)
ETS2_PASSTHROUGH_SCENARIOS = [0.75, 1.00]   # sensitivity: 75% and 100%

# CO2 content of fuels (tCO2/MWh_final) — for converting carbon price to fuel cost adder
FUEL_CO2_CONTENT = {
    "gas":          0.202,   # tCO2/MWh (natural gas)
    "oil":          0.265,   # tCO2/MWh (heating oil)
    "biomass":      0.0,     # assumed carbon-neutral under EU accounting rules
    "electricity":  None,    # varies by country and year — see GRID_CARBON_INTENSITY
    "district_heat": 0.080,  # ⚠️ EU average; varies widely with the network's fuel mix
    "hydrogen":     0.0,     # green hydrogen — zero emissions by assumption
}


# =============================================================================
# 3. ELECTRICITY GRID CARBON INTENSITY BY COUNTRY (gCO2e/kWh)
# =============================================================================
# Source: EMBER European Electricity Review 2024; EEA indicator ENER 038 (2024)
# 2023 actuals from EMBER; 2030-2050 consistent with EEA Fit-for-55 trajectories
# and country-level national energy and climate plans (NECPs)
#
# Key 2023 actuals (EMBER):
#   Poland:  662 gCO2/kWh (highest — 61% coal)
#   Czechia: 450 gCO2/kWh (40% coal)
#   Germany: 371 gCO2/kWh (26% coal)
#   EU avg:  242 gCO2/kWh (-17% from 2022, -40% from decade ago)
#   Belgium: ~170 gCO2/kWh
#   France:  ~85 gCO2/kWh (nuclear-dominated)
#   Sweden:  ~45 gCO2/kWh (hydro + nuclear)
#   Norway:  ~30 gCO2/kWh (hydro-dominated — not in model but reference)
#   CH:      ~50 gCO2/kWh (hydro + nuclear)
#
# 2050 target: EU electricity sector near-zero (EEA: 80-90% RES by 2050)
# Note: Enerdata projects <50 gCO2/kWh for most EU countries by 2050 (EnerBlue scenario)
#
# NECP flag: Pull NECPs per country for more precision (Ali decision 2026-04-26)
# TODO: Download national NECPs from EC website and extract grid intensity trajectories
# Until then, values below are scenario-consistent estimates from EEA Fit-for-55
# Priority countries for NECP pull: PL, DE, FR, IT, CZ, RO (largest heat markets)
#
# Opt-out mechanism: set EXCLUDE_GRID_INTENSITY_COUNTRIES = [] to use all countries,
# or add country codes to exclude from carbon intensity calculations (use EU average)
NECP_GRID_INTENSITY_PENDING = ["PL","DE","FR","IT","CZ","RO","HU","PL","BG","SK"]
EXCLUDE_GRID_INTENSITY_COUNTRIES = []   # empty = use all; add codes to use EU avg

# ⚠️ 2030 and beyond values are scenario-consistent estimates. 
# For precise modelling, use EMBER API or EEA country data.
# Structure: country -> {year: gCO2e/kWh}

GRID_CARBON_INTENSITY = {
    # High coal — fastest reduction needed
    "PL": {2025: 600, 2030: 400, 2040: 150, 2050: 30},
    "CZ": {2025: 420, 2030: 250, 2040: 100, 2050: 20},
    "BG": {2025: 350, 2030: 200, 2040: 80,  2050: 20},
    "EE": {2025: 300, 2030: 150, 2040: 60,  2050: 15},

    # High fossil but decarbonising fast
    "DE": {2025: 350, 2030: 200, 2040: 80,  2050: 15},
    "NL": {2025: 280, 2030: 150, 2040: 60,  2050: 10},
    "BE": {2025: 160, 2030: 100, 2040: 40,  2050: 8},
    "IT": {2025: 250, 2030: 140, 2040: 55,  2050: 10},
    "EL": {2025: 300, 2030: 160, 2040: 60,  2050: 10},
    "HU": {2025: 250, 2030: 130, 2040: 50,  2050: 10},
    "SK": {2025: 200, 2030: 100, 2040: 40,  2050: 8},
    "RO": {2025: 250, 2030: 130, 2040: 50,  2050: 10},
    "HR": {2025: 180, 2030: 100, 2040: 40,  2050: 8},
    "SI": {2025: 200, 2030: 110, 2040: 45,  2050: 10},

    # Low carbon already — nuclear/hydro/wind dominated
    "FR": {2025: 80,  2030: 55,  2040: 25,  2050: 8},
    "SE": {2025: 45,  2030: 30,  2040: 15,  2050: 5},
    "FI": {2025: 80,  2030: 50,  2040: 20,  2050: 5},
    "DK": {2025: 130, 2030: 70,  2040: 25,  2050: 5},
    "AT": {2025: 120, 2030: 70,  2040: 25,  2050: 5},

    # Medium
    "ES": {2025: 160, 2030: 90,  2040: 35,  2050: 8},
    "PT": {2025: 120, 2030: 65,  2040: 25,  2050: 5},
    "IE": {2025: 220, 2030: 120, 2040: 45,  2050: 8},
    "LU": {2025: 150, 2030: 80,  2040: 30,  2050: 8},
    "CY": {2025: 500, 2030: 280, 2040: 100, 2050: 20},   # island grid, gas-heavy
    "MT": {2025: 450, 2030: 250, 2040: 90,  2050: 15},   # island grid

    # Baltics
    "LT": {2025: 200, 2030: 100, 2040: 35,  2050: 8},
    "LV": {2025: 120, 2030: 65,  2040: 25,  2050: 5},

    # Non-EU
    "CH": {2025: 50,  2030: 30,  2040: 12,  2050: 5},    # hydro + nuclear dominant
    "UK": {2025: 180, 2030: 90,  2040: 30,  2050: 8},    # rapid offshore wind deployment
}


# =============================================================================
# 4. GAS GRID COVERAGE (% of households connected to gas network)
# =============================================================================
# Used as a proxy for hydrogen infrastructure readiness:
#   - High gas coverage → existing pipeline infrastructure → lower H2 retro-fit cost
#   - Low gas coverage  → no existing infrastructure → H2 deployment more costly
#
# Sources:
#   - ACER Gas Factsheet: EU average ~40% of households on gas network
#   - Eurostat nrg_d_hhq (2023): residential energy by fuel by country
#   - National gas companies / ENTSOG data
#
# Note: Gas coverage ≠ gas for heating. Some countries have gas grid but use it
# primarily for cooking (e.g. Southern Europe). Coverage here refers to any
# household gas connection, as this is the relevant infrastructure indicator
# for potential hydrogen repurposing.
# ⚠️ Values below are estimates from secondary sources — validate before publication.

GAS_GRID_COVERAGE = {
    # Very high — large gas-dependent populations
    "NL": 0.90,   # historically near-universal; actively reducing
    "IT": 0.80,   # gas dominant for heating + cooking
    "DE": 0.75,   # 38% of space heating from gas; widespread grid
    "HU": 0.70,   # 53.6% residential space heating from gas
    "LU": 0.70,
    "BE": 0.65,
    "FR": 0.60,   # widespread but reducing under new-build ban
    "AT": 0.55,
    "CZ": 0.55,
    "SK": 0.55,
    "PL": 0.50,
    "SI": 0.50,
    "HR": 0.45,
    "RO": 0.45,
    "BG": 0.40,
    "EL": 0.35,
    "ES": 0.35,
    "IE": 0.40,
    "PT": 0.25,   # low; mainly renewables/biomass
    "EE": 0.30,
    "LV": 0.30,
    "LT": 0.30,
    "UK": 0.85,   # one of highest in Europe; near-universal urban coverage
    "CH": 0.35,   # canton-level gas grids; being actively dismantled per EnDK 2050+

    # Very low — limited gas infrastructure
    "SE": 0.05,   # district heat + HP dominant; minimal gas grid
    "FI": 0.05,
    "DK": 0.15,   # gas network ban for new buildings since 2013
    "CY": 0.05,   # oil + solar dominated
    "MT": 0.02,   # essentially no gas grid
}

# Hydrogen infrastructure readiness proxy (0-1 scale)
# Based on gas grid coverage: high coverage → easier H2 network repurposing
def h2_infrastructure_readiness(country: str) -> float:
    """
    Returns a 0-1 score for hydrogen infrastructure readiness.
    Based on gas grid coverage as a proxy for pipeline infrastructure.
    Countries with high gas penetration have existing pipeline networks
    that could potentially be repurposed for hydrogen distribution.

    Note: This is a first-order proxy. Full assessment would also consider:
    - Pipeline material compatibility (PE vs steel)
    - Gas pressure levels and compressor stations
    - National hydrogen strategy commitments
    - Import terminal capacity (for green H2)
    """
    coverage = GAS_GRID_COVERAGE.get(country, 0.30)  # default EU average
    return min(1.0, coverage)


# =============================================================================
# 5. SWITZERLAND-SPECIFIC PARAMETERS (RQ2)
# =============================================================================
# Switzerland is modelled separately for RQ2 with specific policy parameters.
# Sources:
#   - SFOE / Prognos (2023): Energy Perspectives 2050+ (EP2050+)
#   - IEA (2023): Switzerland Energy Policy Review
#   - Swiss NDC Annex (2025): NDC 2031-2035 submission to UNFCCC
#   - Odyssee-MURE (2024): Switzerland energy efficiency profile
#   - Green Hydrogen Organisation (2024): Switzerland hydrogen strategy
#   - Swiss CO2 Act 2024; Climate and Innovation Act 2023

SWITZERLAND_POLICY = {
    # Buildings sector targets
    "buildings_energy_target_2050_twh": 65,  # SFOE Energy Strategy 2050: reduce to 65 TWh
    "buildings_co2_target_2050": "net_zero",  # Federal Council: net CO2 emissions to zero by 2050
    "buildings_share_of_national_co2": 0.33,  # ~1/3 of Swiss CO2 emissions

    # Carbon pricing
    "co2_levy_chf_per_tco2_2022": 120,       # CO2 levy on thermal fossil fuels since 2022
    "co2_levy_trajectory": "⚠️ Pending — Swiss CO2 Act 2024 sets targets through 2030; "
                            "2030-2050 trajectory under Climate and Innovation Act 2023",

    # Heat pump targets
    "hp_target_2050": 1_500_000,    # Target: 1.5M HPs from 0.3M today (EP2050+)
    "hp_current_2023": 300_000,     # Approximate current stock

    # Hydrogen strategy (Switzerland 2024 National Hydrogen Strategy)
    "hydrogen_strategy_published": 2024,
    "hydrogen_role_buildings": "limited",  # EP2050+: H2 primarily for heavy transport + industry
    "hydrogen_role_buildings_notes": (
        "Swiss Energy Perspectives 2050+ (EP2050+) sees heat pumps as the primary "
        "decarbonisation technology for buildings, with district heat expansion. "
        "Gas grids in Swiss cities to be dismantled or transitioned to green hydrogen "
        "(Cantonal Energy Directors 2050+ policy). Hydrogen production potential: "
        "7 PJ from run-of-river sites. Main role of H2 in CH is heavy transport + industry, "
        "NOT residential heating. Buildings H2 share in ZERO scenario: minimal (<5%)."
    ),

    # Hydrogen import price sensitivity (key for RQ2)
    # Switzerland does not produce oil/gas domestically → imports all fossil fuels.
    # Green hydrogen would be imported from EU neighbours (DE, FR, IT, AT)
    # or produced domestically (hydro-electrolysis).
    # Source: IEA Global Hydrogen Review 2023; Agora Energiewende; OIES estimates
    "h2_import_price_eur_per_mwh": {
        # Year: {LOW (domestic CH hydro-electrolysis), CENTRAL (EU pipeline import), HIGH (supply constrained)}
        # Sources: OIES ET08 (2022): ~€3/kg = €90/MWh from EU sources in 2030
        #          OIES ET32 (2024): short pipeline (100-500km) €60-80/MWh in 2030
        #          ScienceDirect (2025): EU domestic H2 marginal cost below €85/MWh by 2050
        #          PwC (2022): Europe production ~€2/kg = €60/MWh by 2050
        # Corrected from original estimates — validated against OIES literature
        2030: {"LOW": 70,  "CENTRAL": 90,  "HIGH": 150},
        2035: {"LOW": 55,  "CENTRAL": 70,  "HIGH": 120},
        2040: {"LOW": 45,  "CENTRAL": 55,  "HIGH": 90},
        2050: {"LOW": 35,  "CENTRAL": 50,  "HIGH": 75},
    },

    # District heating expansion
    "district_heat_expansion_target": "Urban areas per Cantonal Energy Directors 2050+ policy",
    "district_heat_current_share_space_heating": 0.10,  # ⚠️ Estimate; validate

    # Renovation rate
    "renovation_rate_pct_per_year": 1.5,  # Swiss average building renovation rate (⚠️ estimate)
    "renovation_rate_target_2030": 2.0,   # SFOE target to accelerate renovation

    # Key policy instruments
    "buildings_programme": (
        "Federal-cantonal Buildings Programme: supports emission reductions in buildings. "
        "CHF 200M/year maximum federal contribution. "
        "SWEETER programme: 2025-2036 follow-on to existing programme."
    ),
    "cantonal_energy_directors_2050_plus": (
        "EnDK 2050+ (2022): Ten energy-strategic guidelines. "
        "Key measures: mandate renewable heating for new buildings and systems; "
        "expand district heating; dismantle gas grids or transition to green hydrogen. "
        "Cantons are primarily responsible for building energy regulation (Article 89, "
        "paragraph 4 of Swiss Federal Constitution)."
    ),
}


# =============================================================================
# 6. UTILITY FUNCTIONS
# =============================================================================

def get_boiler_ban_year(country: str, ban_type: str = "replacement_fossil_ban") -> int:
    """
    Returns the year for a specific type of boiler ban for a given country.
    ban_type options: 'fossil_boiler_subsidies_end', 'new_build_fossil_ban',
                      'replacement_fossil_ban', 'full_fossil_ban', 'hp_mandate_year'
    """
    country_data = BOILER_BANS.get(country, {})
    return country_data.get(ban_type, 2040)  # default to EU 2040 phase-out


def get_carbon_price(year: int, scenario: str = CARBON_PRICE_SCENARIO) -> float:
    """
    Returns carbon price (EUR/tCO2) for a given year and scenario.
    Interpolates linearly between defined years.
    """
    years = sorted(CARBON_PRICE_EUR_PER_TCO2.keys())
    prices = {y: CARBON_PRICE_EUR_PER_TCO2[y][scenario] for y in years}

    if year <= years[0]:
        return prices[years[0]]
    if year >= years[-1]:
        return prices[years[-1]]

    for i in range(len(years) - 1):
        y0, y1 = years[i], years[i + 1]
        if y0 <= year <= y1:
            t = (year - y0) / (y1 - y0)
            return prices[y0] + t * (prices[y1] - prices[y0])

    return prices[years[-1]]


def get_grid_carbon_intensity(country: str, year: int) -> float:
    """
    Returns electricity grid carbon intensity (gCO2e/kWh) for a country and year.
    Interpolates linearly between defined years.
    """
    country_data = GRID_CARBON_INTENSITY.get(country, GRID_CARBON_INTENSITY["DE"])
    years = sorted(country_data.keys())

    if year <= years[0]:
        return country_data[years[0]]
    if year >= years[-1]:
        return country_data[years[-1]]

    for i in range(len(years) - 1):
        y0, y1 = years[i], years[i + 1]
        if y0 <= year <= y1:
            t = (year - y0) / (y1 - y0)
            return country_data[y0] + t * (country_data[y1] - country_data[y0])

    return country_data[years[-1]]


def get_carbon_cost_adder_eur_per_mwh_useful(
    fuel: str, country: str, year: int, efficiency: float,
    carbon_price_scenario: str = CARBON_PRICE_SCENARIO
) -> float:
    """
    Returns the carbon cost adder (EUR/MWh_useful) for a given fuel, country, and year.
    This is the additional cost imposed by carbon pricing on a technology's operating cost.

    Parameters:
        fuel:     Energy carrier ('gas', 'oil', 'electricity', etc.)
        country:  Country code
        year:     Modelling year
        efficiency: Technology efficiency or COP (to convert final to useful energy)
        carbon_price_scenario: 'LOW', 'CENTRAL', or 'HIGH'

    Returns:
        EUR/MWh_useful energy delivered
    """
    carbon_price = get_carbon_price(year, carbon_price_scenario)

    if fuel in ("electricity", "district_heat"):
        # Grid electricity and district-heat generation are under ETS1, whose carbon
        # cost is ALREADY embedded in the 2025 Eurostat retail price (the carbon-price
        # table is "ETS1 only, buildings not yet covered" in 2025). Charging the full
        # carbon_price x intensity on top would double-count the carbon already in the
        # price. We therefore charge only the INCREMENTAL carbon cost above the 2025
        # level: cp(y)*I(y) - cp(2025)*I(2025), floored at zero. As the grid
        # decarbonises (I falls faster than cp rises) this is ~0 for most countries,
        # leaving a small positive adder only for slow-decarbonising high-carbon grids
        # early in the horizon. Gas/oil heating (below) is NOT netted: ETS2 is genuinely
        # new from 2027 and is not embedded in the 2025 heating-fuel price.
        cp_2025 = get_carbon_price(2025, carbon_price_scenario)
        if fuel == "electricity":
            i_y = get_grid_carbon_intensity(country, year) / 1000      # tCO2/MWh_final
            i_25 = get_grid_carbon_intensity(country, 2025) / 1000
        else:
            from src.Economics import get_district_heat_co2
            i_y = get_district_heat_co2(country, year) / 1000
            i_25 = get_district_heat_co2(country, 2025) / 1000
        co2_cost_final = max(0.0, carbon_price * i_y - cp_2025 * i_25)  # EUR/MWh_final
        return co2_cost_final / max(efficiency, 0.1)                    # EUR/MWh_useful
    elif fuel in FUEL_CO2_CONTENT and FUEL_CO2_CONTENT[fuel] is not None:
        # Gas/oil: full carbon price (ETS2 is new from 2027, not in the 2025 price).
        co2_per_mwh_final = FUEL_CO2_CONTENT[fuel]
        return carbon_price * co2_per_mwh_final / max(efficiency, 0.1)
    else:
        return 0.0  # hydrogen, biomass — zero carbon cost


def get_hp_feasibility_policy_multiplier(country: str, year: int) -> float:
    """
    Returns a policy multiplier (0-1) that scales HP feasibility based on
    whether an HP mandate is in effect for the given country and year.
    
    Pre-mandate: HP feasibility reflects economic competition only (multiplier = 1.0)
    Post-mandate: HP feasibility boosted (multiplier > 1.0, capped at 1.5)
    
    This captures the effect of regulations forcing HP adoption at replacement.
    """
    mandate_year = get_boiler_ban_year(country, "hp_mandate_year")
    if year < mandate_year:
        return 1.0
    elif year >= mandate_year + 10:
        return 1.5   # full mandate effect after 10 years
    else:
        # Ramp up from 1.0 to 1.5 over 10 years post-mandate
        t = (year - mandate_year) / 10
        return 1.0 + 0.5 * t


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Quick validation / demo
    print("=== Policy Module Validation ===\n")

    print("Boiler ban years (replacement_fossil_ban):")
    for c in ["DE", "NL", "FR", "PL", "UK", "CH"]:
        ban = get_boiler_ban_year(c, "replacement_fossil_ban")
        hp  = get_boiler_ban_year(c, "hp_mandate_year")
        print(f"  {c}: fossil ban {ban}, HP mandate {hp}")

    print("\nCarbon prices (CENTRAL scenario):")
    for y in [2025, 2027, 2030, 2035, 2040, 2050]:
        print(f"  {y}: €{get_carbon_price(y, 'CENTRAL'):.0f}/tCO2")

    print("\nGrid carbon intensity (gCO2/kWh):")
    for c in ["PL", "DE", "FR", "CH", "UK"]:
        vals = {y: f"{get_grid_carbon_intensity(c, y):.0f}" for y in [2025, 2030, 2040, 2050]}
        print(f"  {c}: {vals}")

    print("\nGas grid coverage (H2 infrastructure proxy):")
    for c in ["NL", "DE", "FR", "PL", "SE", "CH", "UK"]:
        print(f"  {c}: {GAS_GRID_COVERAGE.get(c, 0.3):.0%} → H2 readiness: {h2_infrastructure_readiness(c):.2f}")

    print("\nCarbon cost adder — gas boiler (η=0.92) vs HP (COP=3.0) in Germany, 2030:")
    gas_adder = get_carbon_cost_adder_eur_per_mwh_useful("gas", "DE", 2030, 0.92)
    hp_adder  = get_carbon_cost_adder_eur_per_mwh_useful("electricity", "DE", 2030, 3.0)
    print(f"  Gas boiler:  €{gas_adder:.1f}/MWh_useful")
    print(f"  HP (air):    €{hp_adder:.1f}/MWh_useful")

    print("\n=== Switzerland RQ2 ===")
    print(f"  H2 import price 2030 (CENTRAL): €{SWITZERLAND_POLICY['h2_import_price_eur_per_mwh'][2030]['CENTRAL']}/MWh")
    print(f"  H2 import price 2050 (CENTRAL): €{SWITZERLAND_POLICY['h2_import_price_eur_per_mwh'][2050]['CENTRAL']}/MWh")
    print(f"  Buildings energy target 2050:   {SWITZERLAND_POLICY['buildings_energy_target_2050_twh']} TWh")
