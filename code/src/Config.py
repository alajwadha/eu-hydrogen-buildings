"""
code/src/Config.py  —  Central configuration: paths, geography, parameters
==========================================================================
Single source of truth for paths, country lists, technology defaults,
baseline fuel prices, and scenario settings consumed by every other module.

All numeric values cite their sources inline. Where a value is an estimate
without a primary source it is marked with a warning emoji and a TODO.

Primary sources used in this file:

  Techno-economic (TECH_DEFAULTS):
    - JRC Technology Data — Energy Technology Reference Indicator (ETRI)
      projections (2023 update). publications.jrc.ec.europa.eu
    - IEA (2022) "The Future of Heat Pumps" — heat-pump CAPEX, COP, lifetime
    - IRENA (2022) "Heat Pumps: Costs, Performance, Outlook"
    - Danish Energy Agency (2023) "Technology Data for Heating Installations"

  Fuel prices (BASE_PRICES_2025):
    - Eurostat nrg_pc_202 (residential gas prices, H1 2025)
    - Eurostat nrg_pc_204 (residential electricity prices, H1 2025)
    - Eurostat nrg_d_hhq (residential energy consumption by fuel)
    - European Hydrogen Observatory (2024) hydrogen cost calculator

  Long-term price multipliers (PRICE_MULTIPLIERS_2050):
    - IEA World Energy Outlook 2024 (STEPS scenario) for gas/electricity
    - Oxford Institute for Energy Studies (OIES) hydrogen price trajectories

  Scenarios (STATED_POLICIES / NET_ZERO / H2_PUSH) — see literature/scenario_assumptions_audit.md sec 4:
    - STATED_POLICIES: a frozen / current-measures trend. NOT the post-Fit-for-55 EU
      Reference Scenario 2024 (which projects a faster gas decline); the ~32%
      residual fossil share is consistent with a current-measures freeze.
    - NET_ZERO: aligned with REPowerEU (60M heat pumps by 2030) + EHPA
      "half of EU buildings" + IEA "The Future of Heat Pumps" (2022).
    - H2_PUSH: a DELIBERATE high-side hydrogen STRESS-TEST, not a central
      projection. The 25% residential-H2 share exceeds the mainstream consensus
      (IEA / IRENA / Hydrogen Science Coalition / Deloitte put building H2 below
      ~1-2%); it is anchored to the gas-industry upper bound (Gas for Climate
      "Optimised Gas") and pre-2024 UK/DE hydrogen-heating strategies. The
      earlier "Hydrogen Council 2021" citation was a misattribution: that ~20%
      figure is total cross-sector abatement, not a residential-heat share.

  Country list (EU_COUNTRIES):
    - EU27 + Switzerland (CH, in Eurostat census via free-movement
      agreement) + UK (handled separately via ONS Census 2021 TS044)
"""
import csv
from pathlib import Path

# ---------------------------------------------------------------------
# Core paths
# ---------------------------------------------------------------------

ROOT_DIR      = Path(__file__).resolve().parents[2]
CODE_DIR      = ROOT_DIR / "code"
DATA_DIR      = CODE_DIR / "data"
RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR   = CODE_DIR / "results"
FIGS_DIR      = ROOT_DIR / "paper" / "figs"

# ---------------------------------------------------------------------
# Geography / time
# ---------------------------------------------------------------------

# EU27 + Switzerland + UK (for modelling purposes)
EU_COUNTRIES = [
    "AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES",
    "FI","FR","HR","HU","IE","IT","LT","LU","LV","MT",
    "NL","PL","PT","RO","SE","SI","SK",
    "CH",  # Switzerland (in Eurostat census)
    "UK",  # United Kingdom (not in Eurostat census, handled via TS044)
]

# BASE_YEAR is the model's present-day anchor. The bottom-up demand snapshot
# (EUBUCCO ~2020-2023 stock x TABULA design intensity) is treated as the demand
# level in BASE_YEAR, NOT in 2015 -- so the scenario demand trajectory and the
# 2015 Hotmaps backcast are both referenced to a single, real present-day year.
# See literature/temporal_backcast_methodology.md.
BASE_YEAR = 2025

YEARS = [2025, 2030, 2040, 2050]

# ---------------------------------------------------------------------
# Technologies and techno-economic assumptions
# (simple, meant as a starting point)
# ---------------------------------------------------------------------

TECHS = [
    "gas_boiler",
    "oil_boiler",
    "biomass_boiler",
    "resistance_heater",
    "hp_air",
    "hp_ground",
    "district_heat",
    "h2_boiler",
]

# All monetary units in EUR, per kW or per MWh as noted.
# NOTE: Economics.py TECH_PARAMS is the AUTHORITATIVE techno-economic source for the
# LCOH used by the Monte Carlo and COST_OPT. The values here are a lightweight
# fallback/reference; they were synced to the 2026-05-25 source-audit corrections
# (see literature/scenario_assumptions_audit.md §5.1) to avoid stale numbers.
TECH_DEFAULTS = {
    "gas_boiler": {
        "capex_2025": 420.0,     # DEA installed (was 1000); audit §2.2
        "capex_2050": 400.0,
        "efficiency": 0.92,      # Condensing boiler LHV (JRC)
        "fixed_om_frac": 0.015,
        "fuel": "gas",
    },
    "oil_boiler": {
        "capex_2025": 450.0,     # DEA installed (was 1200)
        "capex_2050": 430.0,
        "efficiency": 0.90,
        "fixed_om_frac": 0.015,
        "fuel": "oil",
    },
    "biomass_boiler": {
        "capex_2025": 950.0,     # DEA installed (was 1600)
        "capex_2050": 850.0,
        "efficiency": 0.88,
        "fixed_om_frac": 0.020,
        "fuel": "biomass",
    },
    "resistance_heater": {
        "capex_2025": 200.0,     # DEA direct-electric (was 400)
        "capex_2050": 180.0,
        "efficiency": 0.98,
        "fixed_om_frac": 0.010,
        "fuel": "electricity",
    },
    "hp_air": {
        "capex_2025": 1200.0,    # latest DEA (~1196) — kept
        "capex_2050": 800.0,
        "seasonal_cop_2025": 3.3,   # EHPA/Eurovent field SCOP (was 3.0)
        "seasonal_cop_2050": 3.5,
        "fixed_om_frac": 0.020,
        "fuel": "electricity",
    },
    "hp_ground": {
        "capex_2025": 2000.0,
        "capex_2050": 1400.0,
        "seasonal_cop_2025": 3.8,
        "seasonal_cop_2050": 4.3,
        "fixed_om_frac": 0.020,
        "fuel": "electricity",
    },
    "district_heat": {
        "capex_2025": 500.0,  # connection cost per kW
        "capex_2050": 500.0,
        "efficiency": 0.95,
        "fixed_om_frac": 0.015,
        "fuel": "district_heat",
    },
    "h2_boiler": {
        "capex_2025": 600.0,     # gas + ~40% H2-ready premium (was 1400); audit §2.2
        "capex_2050": 550.0,
        "efficiency": 0.90,
        "fixed_om_frac": 0.020,
        "fuel": "hydrogen",
    },
}

# Baseline final-energy prices in EUR/MWh_final — EU average residential end-user
# Source: Eurostat nrg_pc_202 (gas) and nrg_pc_204 (electricity), H1 2025
# Oil, biomass, DH: estimates (Eurostat nrg_d_hhq secondary estimates)
# Hydrogen: European Hydrogen Observatory (2024) ~€6/kg = €200/MWh
# NOTE: These are EU averages used in the Monte Carlo.
# Country-specific prices are used in Economics.py for precise LCOH calculations.
BASE_PRICES_2025 = {
    "gas":          114.3,   # Eurostat nrg_pc_202 H1 2025 EU avg (€0.1143/kWh)
    "oil":          105.0,   # EC Weekly Oil Bulletin (audit §3.2; was 130)
    "biomass":       70.0,   # ENplus/German pellet market (audit §3.2; was 60)
    "electricity":  287.2,   # Eurostat nrg_pc_204 H1 2025 EU avg (€0.2872/kWh)
    "district_heat": 80.0,   # Euroheat & Power DH Price Series
    "hydrogen":     200.0,   # EHO 2024: ~€6/kg at 33.3 kWh/kg
}

# Long-term price multipliers vs 2025 — applied in Monte Carlo simulation
# Sources: IEA WEO 2024 reference scenario (gas, electricity);
#          EHO/OIES H2 price trajectories (hydrogen);
#          Estimated for oil, biomass, district heat ⚠️
# NOTE: Full 4-trajectory H2 price model is in Economics.py FUEL_PRICE_MULTIPLIERS.
# These multipliers are simplified for the Monte Carlo sampling layer.
PRICE_MULTIPLIERS_2050 = {
    "gas":           0.55,   # Declining demand — IEA WEO STEPS
    "oil":           0.55,   # Declining demand
    "biomass":       1.05,   # Supply pressure — stable to slight increase
    "electricity":   0.80,   # Wholesale falls, network costs rise (Eurostat trend)
    "district_heat": 0.80,   # Decarbonising networks — lower fuel cost
    "hydrogen":      0.30,   # OIES CENTRAL: €200 → €60/MWh by 2050
}

# ---------------------------------------------------------------------
# Monte Carlo settings and scenario-level 2050 targets
# ---------------------------------------------------------------------

RNG_SEED = 42
N_MONTE_CARLO_SAMPLES = 200

# ── The four multi-lever scenarios (June 2026 redesign) ──
# These four are the ONLY scenarios. The earlier REF, HIGH_HP and H2_HYBRID runs are
# withdrawn: their outputs differ materially from these (the old H2_HYBRID put hydrogen
# at 25 per cent of the 2050 mix against H2 Push's 8), so they must never be quoted,
# plotted or mapped onto a current scenario name. Their result files have been deleted
# and RETIRED_SCENARIOS below guards against reintroduction. COST_OPTIMIZED is a
# separate least-cost LP cross-check (Optimisation.py), not one of the four.
# Each scenario is a BUNDLE of levers -- renovation rate (via scenario_intensity_rates.csv),
# carbon-price trajectory, H2-price trajectory, and grid-decarbonisation speed (grid_mult) --
# NOT renovation alone. h2_share_2050 is an EXOGENOUS ADOPTION SETTING, one lever of the
# scenario bundle, and it is NOT derived from the merit order. An earlier version of this
# comment said it was, which was wrong and reached the supplement: the merit order's own
# demand-weighted peak-slice potential is 0, 0.6, 7.5 and 9.0 per cent on the symmetric
# accounting (scripts/dispatch_arena_sensitivity.py), against the 0, 5, 3 and 8 set here.
# Stated Policies is the case where the two disagree most, and that disagreement is a
# result the paper reports rather than something to reconcile by editing either number.
# The dispatch screen is an INDEPENDENT test of these pathways, not their source.
# Simulation.py samples this lever at a 3 pp standard deviation and caps realised hydrogen
# at the drawn target, so realised shares track the setting, not the screen.
# Heat pumps + district heat absorb the rest as fossil is banned out.
# COST_OPTIMIZED is the 5th scenario (the LP in Optimisation.py), not listed here.
# grid_mult scales the grid carbon-intensity trajectory (>1 slower decarb, <1 faster).
SCENARIOS = {
    "CURRENT_POLICIES": {
        "description": "Current-measures freeze: only already-implemented policies. Slow "
                       "renovation, LOW carbon, slow grid, STRANDED (expensive) H2 -> more "
                       "residual fossil, no economic role for hydrogen heating.",
        "hp_share_2050": 0.40, "district_heat_share_2050": 0.16,
        "h2_share_2050": 0.00, "fossil_share_2050": 0.40,
        "demand_reduction_2050": 0.25,
        "carbon_scenario": "LOW", "h2_scenario": "STRANDED", "grid_mult": 1.15,
    },
    "STATED_POLICIES": {
        "description": "Announced/legislated targets (EPBD boiler bans, ETS2 as stated). Current "
                       "renovation pace, CENTRAL carbon + H2, central grid. Merit-order H2 ~5% "
                       "(peaking, cavern countries).",
        "hp_share_2050": 0.50, "district_heat_share_2050": 0.18,
        "h2_share_2050": 0.05, "fossil_share_2050": 0.27,
        "demand_reduction_2050": 0.35,
        "carbon_scenario": "CENTRAL", "h2_scenario": "CENTRAL", "grid_mult": 1.0,
    },
    "NET_ZERO": {
        "description": "Net-zero-aligned: Renovation-Wave pace, HIGH carbon, FAST clean grid; "
                       "heat-pump + district-heat led. Merit-order H2 ~3% (a cheap high-RES grid "
                       "lets heat pumps win even the cold-snap peak).",
        "hp_share_2050": 0.62, "district_heat_share_2050": 0.22,
        "h2_share_2050": 0.03, "fossil_share_2050": 0.05,
        "demand_reduction_2050": 0.50,
        "carbon_scenario": "HIGH", "h2_scenario": "CENTRAL", "grid_mult": 0.70,
    },
    "H2_PUSH": {
        "description": "Maximally hydrogen-favourable: moderate renovation, HIGH carbon (same as "
                       "Net Zero, so the gas competitor is penalised everywhere), RAPID (cheap) "
                       "H2 + gas-grid repurposing + policy support. Gives hydrogen its strongest "
                       "shot on BOTH levers; merit-order H2 share is its highest plausible "
                       "peaking share, in salt-cavern countries.",
        "hp_share_2050": 0.46, "district_heat_share_2050": 0.20,
        "h2_share_2050": 0.08, "fossil_share_2050": 0.15,
        "demand_reduction_2050": 0.40,
        "carbon_scenario": "HIGH", "h2_scenario": "RAPID", "grid_mult": 1.0,
    },
}

# ---------------------------------------------------------------------
# Dataset-specific settings
# ---------------------------------------------------------------------

# Hotmaps column with total SH + HW useful energy (GWh)
HOTMAPS_HEAT_COLUMN = "Total_SH_HW"

# Model-level building types
MODEL_BUILDING_TYPES = ["SFH", "MFH_HIGH", "OTHER"]

# Eurostat CENS_21DWBNO_R3 building codes -> model types
# RES1 / RES2: 1–2 dwellings → SFH
# RES_GE3:     3+ dwellings   → MFH_HIGH
BUILDING_TYPE_MAPPING = {
    "RES1": "SFH",
    "RES2": "SFH",
    "RES_GE3": "MFH_HIGH",
    "RES": "OTHER",
    "NRES": "OTHER",
    "TOTAL": "OTHER",
    "UNK": "OTHER",
}

# UK TS044 (Accommodation type, Census 2021) manual CSV path
UK_TS044_PATH = RAW_DIR / "uk" / "ts044_accommodation_ltla.csv"


# ---------------------------------------------------------------------

# Withdrawn scenarios. Guard so a stale name cannot silently re-enter the pipeline.
RETIRED_SCENARIOS = ("REF", "HIGH_HP", "H2_HYBRID")


def check_scenario(name: str) -> str:
    """Raise on a withdrawn scenario name; return it unchanged if current."""
    if name in RETIRED_SCENARIOS:
        raise ValueError(
            f"{name} is a withdrawn scenario and must not be used. The four current "
            f"scenarios are {', '.join(SCENARIOS)}."
        )
    return name


# Per-country 2025 heating-technology mix + COST_OPT country parameters
# ---------------------------------------------------------------------
# Source: code/data/country_config/heating_mix_2025.csv, built by
# code/scripts/build_heating_mix_2025.py as the mean of two independent bases
# (Eurostat nrg_d_hhq energy shares + national/Odyssee/EHPA dwelling shares).
# See literature/heating_mix_2025_audit.md for the per-country comparison,
# sources, and the fuel->tech mapping. Used by Optimisation.py (per-country
# START_MIX, biomass/H2 ceilings, demand reduction, turnover) and Simulation.py
# (per-country 2025 base mix for STATED_POLICIES/NET_ZERO/H2_PUSH).
HEATING_MIX_PATH = DATA_DIR / "country_config" / "heating_mix_2025.csv"

def load_heating_mix_2025() -> dict:
    """Returns {country: {tech_share..., biomass_ceiling_2050, h2_ceiling_2050,
    demand_reduction_2050, turnover_rate}} from heating_mix_2025.csv. Empty if
    the file is absent (callers fall back to global defaults)."""
    out: dict = {}
    if not HEATING_MIX_PATH.exists():
        return out
    with open(HEATING_MIX_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cc = row.pop("country")
            out[cc] = {k: float(v) for k, v in row.items()}
    return out


# ---------------------------------------------------------------------
# Per-country residential stock-growth rate (for the 2015 Hotmaps backcast)
# ---------------------------------------------------------------------
# The bottom-up snapshot is the BASE_YEAR (2025) demand level for the CURRENT
# building stock. To compare it against the Hotmaps 2015 benchmark at a MATCHED
# vintage, we backcast the snapshot to 2015 by removing the dwellings added
# since 2015: demand scales with floor area, so the 2015 stock -- smaller by the
# net dwelling-stock growth rate -- carries proportionally less demand (2015
# below the 2025 snapshot). The second-order intensity change (the 2015 stock
# was less retrofitted, i.e. slightly higher kWh/m2) partly offsets this and is
# deliberately NOT credited, leaving a conservative stock-only adjustment.
# Source per country in stock_growth.csv (Eurostat/OECD census dwelling counts +
# national statistical offices). See literature/temporal_backcast_methodology.md.
STOCK_GROWTH_PATH = DATA_DIR / "country_config" / "stock_growth.csv"

# EU-mean fallback dwelling-stock growth (%/yr) when a country row is absent.
DEFAULT_STOCK_GROWTH_PCT_YR = 0.88

def load_stock_growth() -> dict:
    """Returns {country: {stock_growth_pct_yr, metric, basis_year_range, source,
    confidence}} from stock_growth.csv. Empty if the file is absent (callers
    fall back to DEFAULT_STOCK_GROWTH_PCT_YR)."""
    out: dict = {}
    if not STOCK_GROWTH_PATH.exists():
        return out
    with open(STOCK_GROWTH_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cc = row.pop("country")
            out[cc] = row
    return out

_STOCK_GROWTH = load_stock_growth()

def stock_growth_rate(country: str) -> float:
    """Per-country net annual dwelling-stock growth as a fraction (e.g. 0.009 = +0.9%/yr)."""
    row = _STOCK_GROWTH.get(country)
    pct = float(row["stock_growth_pct_yr"]) if row else DEFAULT_STOCK_GROWTH_PCT_YR
    return pct / 100.0

def backcast_factor(country: str, target_year: int = 2015) -> float:
    """Multiplier converting the BASE_YEAR (2025) snapshot to `target_year`
    demand by scaling with the building stock. With positive stock growth g, an
    earlier year had a SMALLER stock and thus LESS demand, so factor < 1 for
    2015 (the 2015 backcast sits below the 2025 snapshot)."""
    g = stock_growth_rate(country)
    return (1.0 + g) ** (target_year - BASE_YEAR)


# ---------------------------------------------------------------------
# LMDI multi-driver FORWARD projection (2025 -> 2050)
# ---------------------------------------------------------------------
# Same Logarithmic Mean Divisia Index (Ang 2005) decomposition used for the
# 2015 backcast, applied forward to project demand 2025 -> 2050:
#   D(t) = D(BASE_YEAR) * (Pop(t)/Pop_25) * ((Dw/Pop)(t)/(Dw/Pop)_25)
#          * ((m2/Dw)(t)/(m2/Dw)_25) * (1-r)^(t-2025)
# where r is the per-country, per-scenario envelope-relevant intensity decline
# rate (positive r => demand falls forward in time) sampled per MC draw from
# N(central, sigma). Pop trajectory from
# Eurostat EUROPOP2023 + ONS UK + BFS CH; household-size trajectory linearly
# extrapolated from the observed 2015-2023 trend in heat_drivers_demographics.csv;
# dwelling-size held flat. See literature/temporal_backcast_methodology.md
# section 5 (LMDI), scenario_intensity_rates.csv for the per-country rates.
POP_PROJECTION_PATH = DATA_DIR / "country_config" / "pop_projection.csv"
SCENARIO_INTENSITY_RATES_PATH = DATA_DIR / "country_config" / "scenario_intensity_rates.csv"
HEAT_DRIVERS_DEMOGRAPHICS_PATH = DATA_DIR / "country_config" / "heat_drivers_demographics.csv"


def load_pop_projection() -> dict:
    """Returns {country: {year: population}} from pop_projection.csv. Empty if
    the file is absent (callers fall back to flat population = 1.0 ratio)."""
    out: dict = {}
    if not POP_PROJECTION_PATH.exists():
        return out
    with open(POP_PROJECTION_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cc = row["country"]
            try:
                yr = int(row["year"])
                pop = float(row["population"])
            except (KeyError, ValueError):
                continue
            out.setdefault(cc, {})[yr] = pop
    return out


def load_intensity_rates() -> dict:
    """Returns {scenario: {country: {central, low, high, sigma}}} from
    scenario_intensity_rates.csv (rates as fractions: 0.0055 = 0.55%/yr)."""
    out: dict = {}
    if not SCENARIO_INTENSITY_RATES_PATH.exists():
        return out
    with open(SCENARIO_INTENSITY_RATES_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sc = row["scenario"]
            cc = row["country"]
            out.setdefault(sc, {})[cc] = {
                "central": float(row["central_pct_yr"]) / 100.0,
                "low":     float(row["low_pct_yr"]) / 100.0,
                "high":    float(row["high_pct_yr"]) / 100.0,
                "sigma":   float(row["sigma_pct_yr"]) / 100.0,
            }
    return out


def _linear_extrapolate(years_obs: list, values_obs: list, target_years: range) -> dict:
    """Simple OLS linear extrapolation, bounded to physical range."""
    n = len(years_obs)
    if n < 2:
        v = values_obs[0] if values_obs else 0.0
        return {y: v for y in target_years}
    mx = sum(years_obs) / n
    my = sum(values_obs) / n
    ssxy = sum((years_obs[i] - mx) * (values_obs[i] - my) for i in range(n))
    ssx  = sum((years_obs[i] - mx) ** 2 for i in range(n))
    slope = ssxy / ssx if ssx else 0.0
    intercept = my - slope * mx
    out = {}
    for y in target_years:
        v = intercept + slope * y
        out[y] = max(1.5, min(3.5, v))  # physical bounds on household size
    return out


def load_hh_projection() -> dict:
    """Per-country avg household size trajectory 2025-2050, linearly
    extrapolated from the observed 2015-2023 trend in
    heat_drivers_demographics.csv. Bounded to [1.5, 3.5] persons/dwelling."""
    out: dict = {}
    if not HEAT_DRIVERS_DEMOGRAPHICS_PATH.exists():
        return out
    rows: dict = {}
    with open(HEAT_DRIVERS_DEMOGRAPHICS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("metric") != "avg_household_size":
                continue
            cc = row["country"]
            try:
                yr = int(row["year"])
                v = float(row["value"])
            except (KeyError, ValueError):
                continue
            rows.setdefault(cc, {})[yr] = v
    for cc, yrhh in rows.items():
        years = sorted(yrhh.keys())
        values = [yrhh[y] for y in years]
        out[cc] = _linear_extrapolate(years, values, range(2015, 2051))
    return out


_POP_PROJ = load_pop_projection()
_HH_PROJ  = load_hh_projection()
_INT_RATES = load_intensity_rates()


def forward_demand_ratio(country: str, year: int, r_intensity: float) -> float:
    """LMDI multi-driver multiplier D(year)/D(BASE_YEAR) for given intensity
    decline rate `r_intensity` (fraction per year, e.g. 0.0055 = 0.55%/yr).

    D(t)/D(25) = pop_ratio * occupancy_ratio * size_ratio * intensity_ratio
              = pop(t)/pop(25) * hh(25)/hh(t) * 1.0 * (1+r)^(t-25)

    Falls back to 1.0 for missing-data drivers (acts as a no-op for that
    component). Returns 1.0 for year <= BASE_YEAR (the snapshot is the
    BASE_YEAR demand by construction).
    """
    if year <= BASE_YEAR:
        return 1.0
    pop = _POP_PROJ.get(country, {})
    pop_r = (pop[year] / pop[BASE_YEAR]) if (pop and BASE_YEAR in pop and year in pop) else 1.0
    hh = _HH_PROJ.get(country, {})
    occ_r = (hh[BASE_YEAR] / hh[year]) if (hh and BASE_YEAR in hh and year in hh and hh[year] > 0) else 1.0
    # r_intensity is a positive DECLINE rate. Intensity in year T relative to
    # the BASE_YEAR is (1 - r)^(T - BASE_YEAR): for T > BASE_YEAR it falls
    # (retrofit progresses), for T < BASE_YEAR it was higher (less retrofit done).
    int_r = (1.0 - r_intensity) ** (year - BASE_YEAR)
    return pop_r * occ_r * int_r


# Cross-country correlation of the envelope-renovation-rate shock in the MC.
# Renovation pace is driven partly by common EU policy (EPBD, Renovation Wave)
# and partly by national factors, so country rates are positively but not
# perfectly correlated. Each country's shock is decomposed as
#   z_c = sqrt(rho) * z_common + sqrt(1-rho) * z_country
# which preserves the marginal N(central, sigma) for every country (so the
# per-country bands and all medians are unchanged) while inducing pairwise
# correlation rho across countries. rho=0 reproduces fully independent draws,
# which diversify away the EU-aggregate uncertainty and understate the true
# band; rho=1 is fully correlated (widest EU band). 0.5 is a central
# "moderately policy-correlated" assumption; treat it as a structural knob.
INTENSITY_RATE_CORR = 0.5


def sample_country_intensity_rates(scenario: str, rng, rho: float = None) -> dict:
    """Sample per-country intensity rate ~ N(central, sigma) for given scenario,
    with cross-country correlation rho (default INTENSITY_RATE_CORR) via a shared
    EU-policy factor plus idiosyncratic country noise. Marginals (hence per-country
    bands and all medians) are preserved; only the EU-aggregate band reflects rho.
    Truncated to [0, 5%/yr] physical range. Returns {country: r_fraction}."""
    if rho is None:
        rho = INTENSITY_RATE_CORR
    a = rho ** 0.5
    b = (1.0 - rho) ** 0.5
    z_common = float(rng.standard_normal())
    rates = {}
    for cc, params in _INT_RATES.get(scenario, {}).items():
        z = a * z_common + b * float(rng.standard_normal())
        v = params["central"] + params["sigma"] * z
        v = max(0.0, min(0.05, v))
        rates[cc] = v
    return rates


def central_country_intensity_rates(scenario: str) -> dict:
    """Per-country central (no-sample) intensity rate for given scenario.
    Used by COST_OPT (deterministic LP)."""
    return {cc: p["central"] for cc, p in _INT_RATES.get(scenario, {}).items()}
