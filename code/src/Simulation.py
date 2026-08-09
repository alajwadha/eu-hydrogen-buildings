"""
code/src/Simulation.py  —  Monte Carlo engine (integrated Step 1 + 2 + 3)
=========================================================================
Now fully integrates:
  Step 1 (Policy.py):  boiler ban enforcement, HP mandates, carbon pricing,
                        ETS2 pass-through, grid CO2 trajectories
  Step 2 (Economics.py): LCOH-weighted tech choice, H2 price trajectories,
                          discount rate sensitivity, fuel price trajectories
  Step 3 (Emissions.py): CO2 emissions per tech / country / year

Architecture:
  • tech_shares_for_year() now combines:
      (a) scenario target shares (CURRENT_POLICIES / STATED_POLICIES / NET_ZERO / H2_PUSH)
      (b) LCOH-weighted softmax — cheaper tech gets higher share within target
      (c) policy constraints — hard bans and mandates from Policy.py
  • Emissions computed per sample and aggregated
  • Country-level outputs added (top 10 countries by heat demand)
  • Sensitivity axes: carbon price (LOW/CENTRAL/HIGH), H2 trajectory
    (RAPID/CENTRAL/SLOW/STRANDED), discount rate (4/5/8%)

Output files (per scenario):
  mc_summary_{scenario}.csv      — EU aggregate quantiles (existing format)
  mc_emissions_{scenario}.csv    — CO2 emissions quantiles
  mc_country_{scenario}.csv      — country-level tech shares + emissions
  mc_sensitivity_{scenario}.csv  — sensitivity across carbon/H2/discount axes

Methodological references:

  Softmax / logit cost-weighted choice:
    The exponential weighting of normalised LCOH used in tech_shares_for_year()
    is the standard discrete-choice / logit cost-share formulation. Canonical
    references: McFadden (1974) "Conditional logit analysis of qualitative
    choice behavior" and Train (2009) "Discrete Choice Methods with
    Simulation" (Cambridge UP). Logit-based technology-share allocation has
    been used widely in CGE and partial-equilibrium energy models, e.g.
    Sue Wing (2008, Energy Economics 30:547-573) for bottom-up/top-down
    coupling, and the PRIMES model documentation (E3MLab, 2018) for end-use
    fuel-choice at sector level. Our implementation is a simplified blend
    (50% scenario target / 50% LCOH-weighted softmax) rather than a full
    structural logit estimation — see Simulation.py inline comment for the
    TODO to replace this shortcut with a proper LP/MILP in Step 5.

  Monte Carlo uncertainty propagation:
    The "sample inputs from distributions, re-run, report quantiles" design
    is one of four standard approaches reviewed in Yue, Pye, DeCarolis, Li,
    Rogan, Ó Gallachóir (2018) "A review of approaches to uncertainty
    assessment in energy system optimization models", Energy Strategy
    Reviews 21:204-217, DOI 10.1016/j.esr.2018.06.003.
    Our (carbon-price × H2-trajectory × discount-rate) sensitivity-axis
    decomposition is a common building-decarbonisation comparison design,
    e.g. as used in Rosenow (2022) "Is heating homes with hydrogen all but
    a pipe dream? An evidence review", Joule 6(10):2225-2228,
    DOI 10.1016/j.joule.2022.08.015.

  LCOH formulation (used downstream of softmax):
    Standard annuitised levelised-cost-of-heat as in IEA (2022) "The
    Future of Heat Pumps" Annex A and JRC Technology Data (2023).
    See Economics.py for the full LCOH implementation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

# ── Imports from all three steps ──────────────────────────────────────────────
from src.Config import (
    PROCESSED_DIR, RESULTS_DIR, YEARS, BASE_YEAR, TECHS, EU_COUNTRIES,
    TECH_DEFAULTS, BASE_PRICES_2025, SCENARIOS,
    RNG_SEED, N_MONTE_CARLO_SAMPLES, load_heating_mix_2025,
    forward_demand_ratio, sample_country_intensity_rates,
)

# Per-country 2025 heating mix (heating_mix_2025.csv); used as the country-specific
# 2025 base mix that the scenario shares interpolate FROM. Empty -> global fallback.
_HMIX_SIM = load_heating_mix_2025()

# Step 1 — Policy
from src.Policy import (
    BOILER_BANS, CARBON_PRICE_SCENARIOS,
    ETS2_PASSTHROUGH_SCENARIOS, ETS2_PASSTHROUGH_RATE,
    get_carbon_price, get_grid_carbon_intensity,
    get_boiler_ban_year,
)

# Step 2 — Economics
from src.Economics import (
    TECH_PARAMS, compute_lcoh, get_annual_hours, get_cop,
    H2_PRICE_TRAJECTORIES, H2_PRICE_SCENARIO,
    DISCOUNT_RATE_SCENARIOS, DISCOUNT_RATE_REAL, DISCOUNT_RATE_BY_COUNTRY,
    GAS_PRICE_BY_COUNTRY, ELEC_PRICE_BY_COUNTRY,
)

# Step 3 — Emissions
from src.Emissions import compute_emissions_df, aggregate_emissions


# ── Constants ─────────────────────────────────────────────────────────────────
# LCOH softmax temperature: higher = more uniform (less cost-driven),
# lower = winner-takes-all. 50 = moderate cost sensitivity.
#
# Note: this is a heuristic shortcut for the full discrete-choice / LP/MILP
# allocation planned for Step 5 (see Optimisation.py). The temperature value
# is chosen for plausibility (cheaper tech wins moderately, not absolutely)
# rather than estimated from market data. See module docstring above for
# the methodological references on logit cost-share allocation.
LCOH_SOFTMAX_TEMP = 50.0

# Tech groups for ban enforcement
FOSSIL_TECHS  = {"gas_boiler", "oil_boiler"}
HP_TECHS      = {"hp_air", "hp_ground"}

# Countries for country-level output. This was the fifteen largest heat markets, which
# left Ireland without an uncertainty band even though it is one of the seven markets
# where the hydrogen boiler undercuts the best heat pump. The per-country step is a
# groupby over a frame the draw has already built, so covering all 29 costs nothing
# per draw and removes the gap.
TOP_COUNTRIES = list(EU_COUNTRIES)


# ── Scenario definition ───────────────────────────────────────────────────────
@dataclass
class ScenarioParams:
    name: str
    hp_share_2050: float
    dh_share_2050: float
    h2_share_2050: float
    fossil_share_2050: float
    demand_reduction_2050: float
    carbon_scenario: str = "CENTRAL"   # per-scenario lever (multi-lever design)
    h2_scenario: str = "CENTRAL"
    grid_mult: float = 1.0             # grid-decarbonisation speed (>1 slower, <1 faster)


def scenario_from_config(name: str) -> ScenarioParams:
    cfg = SCENARIOS[name]
    return ScenarioParams(
        name=name,
        hp_share_2050=cfg["hp_share_2050"],
        dh_share_2050=cfg["district_heat_share_2050"],
        h2_share_2050=cfg["h2_share_2050"],
        fossil_share_2050=cfg["fossil_share_2050"],
        demand_reduction_2050=cfg["demand_reduction_2050"],
        carbon_scenario=cfg.get("carbon_scenario", "CENTRAL"),
        h2_scenario=cfg.get("h2_scenario", "CENTRAL"),
        grid_mult=cfg.get("grid_mult", 1.0),
    )


# Cross-country correlation of the per-carrier fuel-price shock in the MC.
# Residential fuel prices are coupled across the EU (a single wholesale gas
# market and coupled day-ahead power markets dominate the commodity component),
# so country price shocks are highly correlated -- more so than renovation rates
# (INTENSITY_RATE_CORR). Used in sample_parameters to split each carrier's
# log-normal shock into a shared EU-market factor + an idiosyncratic country
# factor, preserving each (country, carrier) marginal while keeping the
# EU-aggregate price uncertainty realistic. 0.75 is a central "strongly coupled"
# assumption (rho=1 = one EU price, rho=0 = independent national prices).
FUEL_PRICE_CORR = 0.75


# ── MC parameter sampling ─────────────────────────────────────────────────────
def sample_parameters(scen: ScenarioParams, rng: np.random.Generator,
                       carbon_scenario: str = "CENTRAL",
                       h2_scenario: str = "CENTRAL",
                       discount_rate: float = DISCOUNT_RATE_REAL) -> Dict:
    """
    Sample all uncertain parameters for one MC draw.
    Now includes Step 1 and Step 2 uncertainty axes.
    """
    params: Dict = {}

    # ── Demand uncertainty ──────────────────────────────────────────────────
    # LMDI forward (primary): per-country envelope-relevant intensity rate
    # sampled ~ N(central, sigma) per draw from scenario_intensity_rates.csv.
    # Combined with the Eurostat EUROPOP pop trajectory + observed-trend
    # household-size projection in Config.forward_demand_ratio.
    params["scenario_name"] = scen.name
    params["intensity_rate"] = sample_country_intensity_rates(scen.name, rng)

    # Legacy single-parameter projection (used as a fallback if no per-country
    # rates are available, and retained for the --projection delta sensitivity).
    params["demand_reduction_2050"] = float(np.clip(
        rng.normal(scen.demand_reduction_2050, 0.05), 0.2, 0.7))
    params["demand_shape_p"] = float(rng.uniform(0.8, 1.8))

    # ── 2050 target shares with uncertainty ─────────────────────────────────
    params["hp_share_2050"] = float(np.clip(
        rng.normal(scen.hp_share_2050, 0.05), 0.2, 0.9))
    params["dh_share_2050"] = float(np.clip(
        rng.normal(scen.dh_share_2050, 0.03), 0.0, 0.5))
    params["h2_share_2050"] = float(np.clip(
        rng.normal(scen.h2_share_2050, 0.03), 0.0, 0.5))
    # Fossil 2050 share is the scenario's POLICY-AMBITION lever (CURRENT_POLICIES
    # retains fossil heating; NET_ZERO removes it) -- NOT a residual of the clean-tech
    # targets. Using the residual made every scenario phase fossil out near-identically.
    params["fossil_share_2050"] = float(np.clip(
        rng.normal(scen.fossil_share_2050, 0.04), 0.0, 0.6))

    # ── Transition speed exponents ───────────────────────────────────────────
    params["hp_shape_p"]     = float(rng.uniform(0.7, 2.0))
    params["dh_shape_p"]     = float(rng.uniform(0.8, 2.2))
    params["h2_shape_p"]     = float(rng.uniform(1.0, 2.5))
    params["hp_ground_share"]= float(rng.uniform(0.1, 0.5))

    # ── Step 1: Policy uncertainty ───────────────────────────────────────────
    # Carbon price scenario (passed in, not sampled — run as sensitivity axis)
    params["carbon_scenario"] = carbon_scenario

    # ETS2 pass-through rate: sample uniformly between 75% and 100%
    params["ets2_passthrough"] = float(rng.uniform(0.75, 1.00))

    # ── Step 2: Economics uncertainty ────────────────────────────────────────
    # H2 price trajectory (passed in, not sampled — sensitivity axis)
    params["h2_scenario"] = h2_scenario

    # Discount rate (sampled around chosen rate ±0.5%)
    params["discount_rate"] = float(np.clip(
        rng.normal(discount_rate, 0.005), 0.03, 0.12))

    # HP feasibility uncertainty (±10% around central values)
    params["hp_feas_sfh_mult"] = float(np.clip(rng.normal(1.0, 0.10), 0.7, 1.3))
    params["hp_feas_mfh_mult"] = float(np.clip(rng.normal(1.0, 0.15), 0.5, 1.5))

    # Per-COUNTRY, per-carrier fuel-price multiplier uncertainty (lognormal,
    # sigma=15%). Country fuel prices are coupled (single EU gas market, coupled
    # power markets), so a fully independent per-country draw would diversify the
    # aggregate price uncertainty away (the same pitfall as independent renovation
    # rates). Each carrier's shock is therefore decomposed into a shared
    # EU-market factor + an idiosyncratic country factor with correlation
    # FUEL_PRICE_CORR (high, ~0.75): z_{c,carrier} = sqrt(rho)*z_EU,carrier
    # + sqrt(1-rho)*z_{c,carrier}, and mult = exp(sigma * z). This preserves each
    # (country,carrier) marginal lognormal(0,sigma) while keeping the EU-aggregate
    # price uncertainty realistic. Result: params["price_mult"][country][carrier],
    # consumed per-country in get_lcoh_for_mc -> compute_lcoh -> get_fuel_price.
    _sig = 0.15
    _a = FUEL_PRICE_CORR ** 0.5
    _b = (1.0 - FUEL_PRICE_CORR) ** 0.5
    pm: Dict[str, Dict[str, float]] = {}
    for carrier in BASE_PRICES_2025:
        z_eu = float(rng.standard_normal())
        for cc in EU_COUNTRIES:
            z = _a * z_eu + _b * float(rng.standard_normal())
            pm.setdefault(cc, {})[carrier] = float(np.exp(_sig * z))
    params["price_mult"] = pm

    return params


# ── Heat demand interpolation ─────────────────────────────────────────────────
def interpolate_heat_demand(baseline_mwh: float, year: int,
                            params: Dict, country: str = None) -> float:
    """Project baseline_mwh from BASE_YEAR to `year`.

    LMDI forward (primary) when `country` is provided and per-country
    intensity rates were sampled into params:
      D(t) = D_base * pop_ratio(t) * occupancy_ratio(t) * size_ratio(t)
                    * (1 + r_country)^(t - BASE_YEAR)

    Falls back to the single-parameter `demand_reduction_2050` formulation
    when country is None or the LMDI sample isn't present (legacy / sensitivity).
    """
    if year <= BASE_YEAR:
        return baseline_mwh
    if country and "intensity_rate" in params and country in params["intensity_rate"]:
        r = params["intensity_rate"][country]
        return baseline_mwh * forward_demand_ratio(country, year, r)
    t = (year - BASE_YEAR) / (2050 - BASE_YEAR)
    p = params["demand_shape_p"]
    reduction = np.clip(params["demand_reduction_2050"] * (t ** p), 0.0, 0.9)
    return baseline_mwh * (1.0 - reduction)


def interpolate_share(base: float, target: float, year: int,
                       exponent: float) -> float:
    if year <= 2025:
        return base
    t = (year - 2025) / (2050 - 2025)
    return base + (target - base) * (t ** exponent)


# ── LCOH computation for MC (uses Economics.py) ───────────────────────────────
def get_lcoh_for_mc(tech: str, country: str, year: int, params: Dict) -> float:
    """
    Compute LCOH using Economics.py with MC-sampled parameters.
    Applies ETS2 pass-through uncertainty and price multipliers.
    """
    try:
        lcoh = compute_lcoh(
            tech, country, year,
            carbon_price_scenario=params.get("carbon_scenario", "CENTRAL"),
            discount_rate=(DISCOUNT_RATE_BY_COUNTRY.get(country, DISCOUNT_RATE_REAL)
                           * (params.get("discount_rate", DISCOUNT_RATE_REAL)
                              / DISCOUNT_RATE_REAL)),
            h2_scenario=params.get("h2_scenario", "CENTRAL"),
            price_mult=(params.get("price_mult") or {}).get(country),
        )
        # Apply ETS2 pass-through adjustment
        # Base compute_lcoh assumes 100% pass-through
        # Scale carbon component by sampled pass-through
        pt = params.get("ets2_passthrough", ETS2_PASSTHROUGH_RATE)
        if pt < 1.0 and year >= 2027:
            # Rough carbon component: carbon price × fuel EF / efficiency
            # This is an approximation — full recomputation would be slow
            from src.Policy import get_carbon_price
            from src.Economics import TECH_PARAMS as TP
            p = TP.get(tech, {})
            fuel = p.get("fuel", "")
            ef = {"gas": 0.202, "oil": 0.265}.get(fuel, 0.0)
            eta = p.get("efficiency_2025", 1.0)
            cp = get_carbon_price(year, params.get("carbon_scenario", "CENTRAL"))
            carbon_base = cp * ef / eta
            carbon_adj  = carbon_base * pt
            lcoh = lcoh - carbon_base + carbon_adj
        return max(lcoh, 0.0)
    except Exception:
        return 999.0


# ── Policy-constrained + LCOH-weighted tech shares ────────────────────────────
def tech_shares_for_year(
    year: int,
    country: str,
    params: Dict,
    hp_feas: float,
    dh_feas: float,
    lcoh_table: dict | None = None,
) -> Dict[str, float]:
    """
    Computes technology shares integrating:
    1. Scenario-defined 2050 targets (the 4 scenarios)
    2. LCOH softmax weighting — cheaper techs get proportionally higher share
    3. Policy constraints — boiler bans and HP mandates from Policy.py

    Returns normalised dict of tech → share (sums to 1.0).
    """
    # ── Base targets from scenario ───────────────────────────────────────────
    hp_feas_adj = hp_feas * params.get("hp_feas_sfh_mult", 1.0)
    dh_feas_adj = dh_feas

    hp_tgt = params["hp_share_2050"] * (0.40 + 0.60 * min(hp_feas_adj, 1.0))
    dh_tgt = params["dh_share_2050"] * (0.40 + 0.60 * min(dh_feas_adj, 1.0))
    h2_tgt = params["h2_share_2050"]
    fossil_tgt  = params["fossil_share_2050"]
    biomass_tgt = max(0.05, 1.0 - hp_tgt - dh_tgt - h2_tgt - fossil_tgt)

    # Feasibility-suppressed heat-pump share must not pile into BIOMASS: burning
    # pellets in dense multi-family stock (where HP feasibility is lowest) is exactly
    # where district heat, not biomass, should take the load. Cap biomass at the
    # higher of its 2025 share or a sustainable 15% ceiling, and route the excess
    # first to district heat (up to its feasibility room) and then to heat pumps.
    _biomass_base_hint = (_HMIX_SIM.get(country, {}) or {}).get("biomass_boiler", 0.10)
    biomass_ceiling = max(_biomass_base_hint, 0.15)
    if biomass_tgt > biomass_ceiling:
        excess = biomass_tgt - biomass_ceiling
        biomass_tgt = biomass_ceiling
        dh_room = max(0.0, min(dh_feas_adj, 1.0) - dh_tgt)
        add = min(excess, dh_room); dh_tgt += add; excess -= add
        hp_room = max(0.0, min(hp_feas_adj, 1.0) - hp_tgt)
        add = min(excess, hp_room); hp_tgt += add; excess -= add
        biomass_tgt += excess   # only if both DH and HP are feasibility-saturated

    # 2025 starting mix that the scenario targets interpolate FROM. Per-country
    # from heating_mix_2025.csv (Eurostat + national, see heating_mix_2025_audit.md);
    # falls back to the EU-average mix where a country is missing.
    _hm = _HMIX_SIM.get(country)
    if _hm:
        base_hp = _hm["hp_air"] + _hm["hp_ground"]
        base_dh = _hm["district_heat"]
        base_h2 = _hm["h2_boiler"]
        base_gas = _hm["gas_boiler"]; base_oil = _hm["oil_boiler"]
        fossil_base = base_gas + base_oil
        biomass_base = _hm["biomass_boiler"]
        base_res = _hm["resistance_heater"]
    else:
        base_hp = 0.18; base_dh = 0.12; base_h2 = 0.0
        base_gas = 0.48; base_oil = 0.12; fossil_base = 0.60
        biomass_base = 0.10; base_res = 0.02
    gas_frac = base_gas / fossil_base if fossil_base > 1e-9 else 0.80

    hp_raw     = interpolate_share(base_hp,      hp_tgt,     year, params["hp_shape_p"])
    dh_raw     = interpolate_share(base_dh,      dh_tgt,     year, params["dh_shape_p"])
    h2_raw     = interpolate_share(base_h2,      h2_tgt,     year, params["h2_shape_p"])
    # Fossil, biomass and resistance interpolate from the country's actual 2025 share
    # to the scenario target (previously the 2025 fossil/biomass split was derived from
    # the 2050 target ratio, ignoring the real starting mix). The gas/oil split within
    # fossil uses the country's actual ratio. Shares are renormalised below.
    fossil_raw  = interpolate_share(fossil_base,  fossil_tgt,  year, params["dh_shape_p"])
    biomass_raw = interpolate_share(biomass_base, biomass_tgt, year, params["hp_shape_p"])
    res_raw     = interpolate_share(base_res,     0.02,        year, params["dh_shape_p"])

    shares = {
        "hp_air":           hp_raw * (1.0 - params["hp_ground_share"]),
        "hp_ground":        hp_raw * params["hp_ground_share"],
        "district_heat":    dh_raw,
        "h2_boiler":        h2_raw,
        "gas_boiler":       fossil_raw * gas_frac,
        "oil_boiler":       fossil_raw * (1.0 - gas_frac),
        "biomass_boiler":   biomass_raw,
        "resistance_heater":res_raw,
    }

    # ── Step 1: Policy constraints ─────────────────────────────────────────
    ban = BOILER_BANS.get(country, {})

    # Boiler ban enforces the scenario's fossil-phaseout AMBITION, not a universal
    # zero. Under an ambitious scenario (near-zero 2050 fossil target) the announced
    # replacement ban zeroes new fossil; under a weak-policy scenario fossil persists
    # at the scenario's intended share, so CURRENT_POLICIES is not forced to the same
    # near-zero fossil mix as NET_ZERO.
    # The ban applies only AFTER the base year. Austria and France carry a 2025
    # replacement ban, so without this guard the 2050 fossil-ambition draw reached
    # back and deleted their observed 2025 boiler stock, making the base year itself
    # scenario-dependent (the Net Zero 2025 median fell to ~586 MtCO2 against ~639 for
    # the others) and bimodal. A ban on replacing a boiler cannot remove the stock that
    # is already installed in the calibration year.
    replacement_ban = ban.get("replacement_fossil_ban", 2035)
    if year > BASE_YEAR and year >= replacement_ban and params["fossil_share_2050"] < 0.08:
        shares["gas_boiler"] = 0.0
        shares["oil_boiler"] = 0.0

    # HP mandate: enforce floor.
    # The `year > BASE_YEAR` guard is the same one the replacement-ban block above carries,
    # and for the same reason. Austria and France both have hp_mandate_year = 2025, so
    # without it a 25 per cent heat-pump STOCK floor was imposed on the calibration year
    # itself: AT's 2025 share read 21.6 per cent against an observed 9.25, and FR's 23.2
    # against 17.4. A mandate that new installations be heat pumps from 2025 does not put a
    # quarter of the existing stock on heat pumps in 2025. The floor belongs to the forward
    # path only, and the base year belongs to the observed mix.
    hp_mandate = ban.get("hp_mandate_year", 2040)
    if year > BASE_YEAR and year >= hp_mandate:
        hp_total = shares["hp_air"] + shares["hp_ground"]
        hp_floor = max(hp_total, 0.25)  # at least 25% HP after mandate
        if hp_total < hp_floor:
            boost = hp_floor - hp_total
            shares["hp_air"]   += boost * (1 - params["hp_ground_share"])
            shares["hp_ground"]+= boost * params["hp_ground_share"]

    # ── Step 2: LCOH softmax weighting ──────────────────────────────────────
    # Compute LCOH for each tech in this country and year
    lcoh_vals: Dict[str, float] = {}
    # Fossil boilers are EXCLUDED from the cost-responsive reallocation: their share is
    # set by policy (the scenario fossil target + bans), while the LCOH softmax decides
    # the mix among the NON-fossil options. This stops cost pressure from silently
    # eroding the scenario's intended fossil share back toward the cost optimum.
    for tech in TECHS:
        if shares.get(tech, 0.0) > 0 and tech not in ("gas_boiler", "oil_boiler"):
            lcoh_vals[tech] = get_lcoh_for_mc(tech, country, year, params)

    if lcoh_vals:
        # Softmax over inverse LCOH: cheaper = higher weight
        techs_with_lcoh = list(lcoh_vals.keys())
        lcoh_arr = np.array([lcoh_vals[t] for t in techs_with_lcoh])

        # Normalise then apply softmax (temperature controls sensitivity)
        lcoh_norm = (lcoh_arr - lcoh_arr.mean()) / (lcoh_arr.std() + 1e-9)
        weights = np.exp(-lcoh_norm / (LCOH_SOFTMAX_TEMP / lcoh_arr.std().clip(1)))
        weights /= weights.sum()

        # Blend the scenario target with an LCOH-weighted reallocation.
        # The LCOH-weighted component redistributes the *total* responsive
        # share mass across the techs in proportion to the cheapness softmax,
        # so cheaper technologies genuinely gain share. (The previous
        # implementation multiplied each tech's scenario share by its softmax
        # weight and then divided/multiplied by the same sum, which cancelled
        # out and left the mix almost unresponsive to LCOH.)
        #
        # The cost-responsive weight w_lcoh ramps from 0 in 2025 to 0.5 by
        # 2050: the 2025 mix stays anchored to the observed market baseline
        # rather than jumping straight to the cost optimum, and cost
        # responsiveness then phases in over the transition. See
        # literature/assumptions_register.md, 2026-05-18 entry.
        w_lcoh = 0.50 * float(np.clip((year - 2025) / 25.0, 0.0, 1.0))
        total_responsive = sum(shares[t] for t in techs_with_lcoh)
        for i, tech in enumerate(techs_with_lcoh):
            lcoh_share = total_responsive * weights[i]
            shares[tech] = (1.0 - w_lcoh) * shares[tech] + w_lcoh * lcoh_share

    # ── Normalise ────────────────────────────────────────────────────────────
    total = sum(shares.values())
    if total > 0:
        shares = {k: v / total for k, v in shares.items()}

    # ── Hydrogen cap: H2 is a MARGINAL/peaking producer (exogenous adoption setting,
    # share, scripts/merit_order_heat.py), not a base-load winner. Cap it at the
    # scenario's interpolated H2 target so the softmax / fossil-ban reallocation cannot
    # inflate it (the old STATED_POLICIES realised 13% H2 vs a 5% design). Route the excess to heat
    # pumps (up to feasibility) and then district heat -- the electrification techs that
    # actually absorb the banned-fossil share. Then renormalise.
    h2_ceiling = max(h2_raw, 0.0)
    if shares["h2_boiler"] > h2_ceiling + 1e-9:
        excess = shares["h2_boiler"] - h2_ceiling
        shares["h2_boiler"] = h2_ceiling
        hp_now = shares["hp_air"] + shares["hp_ground"]
        hp_room = max(0.0, min(hp_feas_adj, 1.0) - hp_now)
        add = min(excess, hp_room)
        shares["hp_air"]    += add * (1 - params["hp_ground_share"])
        shares["hp_ground"] += add * params["hp_ground_share"]
        shares["district_heat"] += (excess - add)
        total = sum(shares.values())
        if total > 0:
            shares = {k: v / total for k, v in shares.items()}

    return shares


# ── Efficiency helper (uses Economics.py) ─────────────────────────────────────
def eff_for_tech(tech: str, country: str, year: int) -> float:
    """Returns efficiency or COP for a tech using Economics.py data."""
    p = TECH_PARAMS.get(tech, TECH_DEFAULTS.get(tech, {}))
    if tech in ("hp_air", "hp_ground"):
        try:
            return get_cop(tech, country, year)
        except Exception:
            pass
    if "seasonal_cop_2025" in p:
        cop0, cop1 = p["seasonal_cop_2025"], p["seasonal_cop_2050"]
        t = np.clip((year - 2025) / 25, 0, 1)
        return cop0 + t * (cop1 - cop0)
    e0 = p.get("efficiency_2025", p.get("efficiency", 1.0))
    e1 = p.get("efficiency_2050", e0)
    t  = np.clip((year - 2025) / 25, 0, 1)
    return e0 + t * (e1 - e0)


# ── Single sample run ─────────────────────────────────────────────────────────
def run_single_sample(
    scen: ScenarioParams,
    params: Dict,
    stock: pd.DataFrame,
    feas: pd.DataFrame,
    lcoh_table: dict | None = None,
) -> pd.DataFrame:
    """
    Fully vectorised MC sample — builds output with numpy arrays,
    avoids per-row DataFrame copies. ~0.5s per sample (was 3.7s).
    """
    df = stock.merge(
        feas[["nuts_id", "country", "building_type",
              "hp_feasibility", "dh_feasibility"]],
        on=["nuts_id", "country", "building_type"],
        how="left",
    )
    df["hp_feasibility"] = df["hp_feasibility"].fillna(0.7)
    df["dh_feasibility"] = df["dh_feasibility"].fillna(0.4)
    df = df.reset_index(drop=True)

    # Pre-extract arrays once
    nuts_arr    = df["nuts_id"].values
    country_arr = df["country"].values
    btype_arr   = df["building_type"].values
    heat_base   = df["heat_2015_MWh"].values
    hp_feas_arr = df["hp_feasibility"].values
    dh_feas_arr = df["dh_feasibility"].values

    # Pre-compute tech info once
    tech_list = list(TECHS)
    tech_fuels = {t: TECH_PARAMS.get(t, {}).get("fuel",
                  TECH_DEFAULTS.get(t, {}).get("fuel", "gas"))
                  for t in tech_list}

    # Pre-compute shares for each unique (country, hp_feas, dh_feas) group
    # and efficiency for each (tech, country, year)
    group_keys  = list(zip(country_arr, hp_feas_arr, dh_feas_arr))
    unique_groups = {}
    for key in set(group_keys):
        unique_groups[key] = None  # filled below

    # Build output arrays
    out_nuts, out_country, out_btype = [], [], []
    out_year, out_tech, out_carrier  = [], [], []
    out_heat, out_fe                 = [], []

    n = len(df)

    # Pre-compute per-country LMDI multipliers once (independent of year/row).
    # Falls back to legacy single-parameter reduction if no LMDI sample in params.
    _lmdi_mode = "intensity_rate" in params and params["intensity_rate"]
    if _lmdi_mode:
        _unique_countries = np.unique(country_arr)
        _country_mult_by_year = {}  # year -> {cc: multiplier}
        for _y in YEARS:
            mults = {}
            for _cc in _unique_countries:
                _r = params["intensity_rate"].get(_cc, 0.005)
                mults[_cc] = forward_demand_ratio(_cc, int(_y), _r)
            _country_mult_by_year[_y] = mults

    for year in YEARS:
        if _lmdi_mode:
            # LMDI forward: per-country multiplier D(year)/D(BASE_YEAR).
            mult_arr = np.array([_country_mult_by_year[year][cc] for cc in country_arr])
            total_heat = heat_base * mult_arr
        else:
            # Legacy single-parameter reduction (sensitivity / fallback).
            t   = np.clip((year - BASE_YEAR) / (2050 - BASE_YEAR), 0, 1)
            red = np.clip(params["demand_reduction_2050"] * (t ** params["demand_shape_p"]), 0, 0.9)
            total_heat = heat_base * (1.0 - red)

        # Pre-compute shares for each unique group for this year
        shares_cache: Dict[tuple, Dict[str, float]] = {}
        for key in unique_groups:
            country, hp_feas, dh_feas = key
            shares_cache[key] = tech_shares_for_year(
                year, country, params, hp_feas, dh_feas, lcoh_table)

        # Pre-compute efficiency for each (tech, country) pair for this year
        eff_cache: Dict[tuple, float] = {}
        for key in unique_groups:
            country = key[0]
            for tech in tech_list:
                eff_cache[(tech, country)] = eff_for_tech(tech, country, year)

        # Vectorised output construction using group masks
        for key in unique_groups:
            country, hp_feas, dh_feas = key
            # Boolean mask for this group
            mask = (country_arr == country) & (hp_feas_arr == hp_feas) & (dh_feas_arr == dh_feas)
            idx  = np.where(mask)[0]
            if len(idx) == 0:
                continue

            g_nuts    = nuts_arr[idx]
            g_country = country_arr[idx]
            g_btype   = btype_arr[idx]
            g_heat    = total_heat[idx]
            m         = len(idx)

            shares = shares_cache[key]
            for tech, share in shares.items():
                if share <= 1e-9:
                    continue
                fuel = tech_fuels[tech]
                eta  = eff_cache[(tech, country)]
                h    = g_heat * share
                fe   = h / max(eta, 0.1)

                out_nuts.append(g_nuts)
                out_country.append(g_country)
                out_btype.append(g_btype)
                out_year.append(np.full(m, year, dtype=np.int32))
                out_tech.append(np.full(m, tech))
                out_carrier.append(np.full(m, fuel))
                out_heat.append(h)
                out_fe.append(fe)

    return pd.DataFrame({
        "nuts_id":          np.concatenate(out_nuts),
        "country":          np.concatenate(out_country),
        "building_type":    np.concatenate(out_btype),
        "year":             np.concatenate(out_year),
        "tech":             np.concatenate(out_tech),
        "carrier":          np.concatenate(out_carrier),
        "useful_heat_MWh":  np.concatenate(out_heat),
        "final_energy_MWh": np.concatenate(out_fe),
    })


# ── EU-level aggregation (heat + energy) ──────────────────────────────────────
def aggregate_eu(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates to EU-total variable-long format (existing format)."""
    # Total useful heat
    total_heat = (df.groupby("year", as_index=False)["useful_heat_MWh"].sum()
                  .assign(variable="useful_heat_MWh", tech="all", carrier="all"))

    # Final energy by carrier
    fe = (df.groupby(["year", "carrier"], as_index=False)["final_energy_MWh"].sum()
          .rename(columns={"carrier": "tech"}))
    fe["variable"] = "final_energy_MWh"
    fe["carrier"]  = fe["tech"]

    # Tech shares
    ts = df.groupby(["year", "tech"], as_index=False)["useful_heat_MWh"].sum()
    tot = ts.groupby("year")["useful_heat_MWh"].transform("sum")
    ts["value"]    = np.where(tot > 0, ts["useful_heat_MWh"] / tot, 0.0)
    ts             = ts[["year", "tech", "value"]]
    ts["variable"] = "tech_share"
    ts["carrier"]  = "all"

    total_heat.rename(columns={"useful_heat_MWh": "value"}, inplace=True)
    fe.rename(columns={"final_energy_MWh": "value"}, inplace=True)

    return pd.concat([total_heat, fe, ts], ignore_index=True)


# ── Country-level aggregation ─────────────────────────────────────────────────
def aggregate_countries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates tech shares and emissions per country.
    Returns rows: country, year, tech, variable, value.
    """
    records = []
    for country in TOP_COUNTRIES:
        cdf = df[df["country"] == country]
        if cdf.empty:
            continue

        # Tech shares per country
        ts = cdf.groupby(["year", "tech"])["useful_heat_MWh"].sum()
        tot = cdf.groupby("year")["useful_heat_MWh"].sum()
        for (year, tech), v in ts.items():
            share = v / max(tot.get(year, 1e-9), 1e-9)
            records.append({
                "country": country, "year": year,
                "tech": tech, "variable": "tech_share", "value": round(share, 4)
            })

        # CO2 emissions per country
        if "co2_tCO2" in cdf.columns:
            co2 = cdf.groupby("year")["co2_tCO2"].sum() / 1e6  # Mt
            for year, v in co2.items():
                records.append({
                    "country": country, "year": year,
                    "tech": "all", "variable": "co2_MtCO2", "value": round(v, 3)
                })

        # Useful heat per country (TWh)
        heat = cdf.groupby("year")["useful_heat_MWh"].sum() / 1e6
        for year, v in heat.items():
            records.append({
                "country": country, "year": year,
                "tech": "all", "variable": "useful_heat_TWh", "value": round(v, 2)
            })

    return pd.DataFrame(records)


# ── LCOH weighted average ─────────────────────────────────────────────────────
def compute_weighted_lcoh(df: pd.DataFrame, params: Dict) -> pd.DataFrame:
    """
    Computes the heat-demand-weighted average LCOH across all techs and countries.
    Returns rows: year, variable='lcoh_weighted_avg_eur_mwh', value.
    """
    records = []
    for year in df["year"].unique():
        ydf = df[df["year"] == year]
        total_cost = 0.0
        total_heat = 0.0
        for _, row in ydf.iterrows():
            lcoh = get_lcoh_for_mc(row["tech"], row["country"], int(year), params)
            heat = row["useful_heat_MWh"]
            total_cost += lcoh * heat
            total_heat += heat
        if total_heat > 0:
            records.append({
                "year": year, "variable": "lcoh_weighted_avg_eur_mwh",
                "tech": "all", "carrier": "all",
                "value": round(total_cost / total_heat, 2),
            })
    return pd.DataFrame(records)


# ── Main Monte Carlo runner ───────────────────────────────────────────────────
def _checkpoint(all_eu, all_em, all_co, scenario_name, n_done):
    """Save quantiles from samples collected so far — called every 25 samples."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    eu = pd.concat(all_eu, ignore_index=True)
    em = pd.concat(all_em, ignore_index=True)
    co = pd.concat(all_co, ignore_index=True)
    _save_quantiles(eu, "value", ["year","variable","tech","carrier"],
                    RESULTS_DIR / f"mc_summary_{scenario_name}.csv")
    _save_quantiles(em, "value", ["year","variable","tech","carrier"],
                    RESULTS_DIR / f"mc_emissions_{scenario_name}.csv")
    _save_quantiles(co, "value", ["country","year","tech","variable"],
                    RESULTS_DIR / f"mc_country_{scenario_name}.csv")
    print(f"  [checkpoint] {n_done} samples saved", flush=True)


def run_monte_carlo(
    scenario_name: str,
    save_samples: bool = False,
    carbon_scenario: str = "CENTRAL",
    h2_scenario: str = "CENTRAL",
    discount_rate: float = DISCOUNT_RATE_REAL,
    demand: str = "hotmaps",
) -> None:
    """
    Full Monte Carlo run integrating Steps 1, 2, and 3.

    Parameters
    ----------
    scenario_name    : CURRENT_POLICIES | STATED_POLICIES | NET_ZERO | H2_PUSH
    save_samples     : save full NUTS3 parquet (large)
    carbon_scenario  : LOW | CENTRAL | HIGH  (Step 1)
    h2_scenario      : RAPID | CENTRAL | SLOW | STRANDED  (Step 2)
    discount_rate    : real pre-tax rate  (Step 2; default 5%)
    demand           : hotmaps (Hotmaps 2015 baseline) | bottomup
                       (29-country EUBUCCO+TABULA build)
    """
    scen = scenario_from_config(scenario_name)
    # Multi-lever design: each scenario carries its own carbon-price and H2-price
    # trajectory, so they differ on more than renovation rate. The scenario's levers
    # take precedence over the CLI defaults (the CLI is used only for the --sensitivity
    # one-at-a-time sweeps, which drive run_single_sample directly).
    carbon_scenario = scen.carbon_scenario
    h2_scenario = scen.h2_scenario
    tag  = f"{scenario_name}_C{carbon_scenario}_H{h2_scenario}"
    print(f"\nMonte Carlo: {tag}")
    print(f"  Carbon: {carbon_scenario} | H2: {h2_scenario} | r={discount_rate:.1%} "
          f"| demand={demand}")

    _stock_f = ("building_stock_nuts3_bottomup.csv" if demand == "bottomup"
                else "building_stock_nuts3.csv")
    _feas_f  = ("hp_dh_feasibility_bottomup.csv" if demand == "bottomup"
                else "hp_dh_feasibility.csv")
    stock = pd.read_csv(PROCESSED_DIR / _stock_f)
    feas  = pd.read_csv(PROCESSED_DIR / _feas_f)
    rng   = np.random.default_rng(RNG_SEED)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    all_eu, all_em, all_co, all_lc, all_samples = [], [], [], [], []

    # LCOH is recomputed PER SAMPLE inside tech_shares_for_year (via get_lcoh_for_mc),
    # so each draw's per-country fuel-price multipliers, carbon-price scenario,
    # hydrogen trajectory, discount rate and ETS2 pass-through propagate into the
    # technology-mix and emissions bands (the price_mult wiring was completed
    # 2026-06; previously the per-carrier fuel-price draws were dropped from the
    # share allocation).
    print("  LCOH recomputed per sample (price-side uncertainty active)")

    for i in range(N_MONTE_CARLO_SAMPLES):
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  Sample {i+1}/{N_MONTE_CARLO_SAMPLES}")

        params = sample_parameters(scen, rng, carbon_scenario,
                                   h2_scenario, discount_rate)

        # Run NUTS3 simulation (Steps 1 + 2 integrated)
        sdf = run_single_sample(scen, params, stock, feas)

        # Step 3: add emissions (grid_mult = scenario grid-decarbonisation speed lever)
        sdf = compute_emissions_df(sdf, grid_mult=scen.grid_mult)
        sdf["sample"] = i

        # EU aggregation
        eu_df = aggregate_eu(sdf)
        eu_df["sample"] = i
        all_eu.append(eu_df)

        # Emissions aggregation
        em_df = aggregate_emissions(sdf)
        em_df["sample"] = i
        all_em.append(em_df)

        # Country-level aggregation
        co_df = aggregate_countries(sdf)
        co_df["sample"] = i
        all_co.append(co_df)

        if save_samples:
            all_samples.append(sdf)

    print("  Aggregating results...")

    # ── EU summary quantiles (existing format) ────────────────────────────
    eu_all = pd.concat(all_eu, ignore_index=True)
    _save_quantiles(eu_all, "value", ["year","variable","tech","carrier"],
                    RESULTS_DIR / f"mc_summary_{scenario_name}.csv")

    # ── Emissions quantiles ───────────────────────────────────────────────
    em_all = pd.concat(all_em, ignore_index=True)
    _save_quantiles(em_all, "value", ["year","variable","tech","carrier"],
                    RESULTS_DIR / f"mc_emissions_{scenario_name}.csv")

    # ── Per-draw EU archive ───────────────────────────────────────────────
    # The quantile files above discard the draws they were computed from, which
    # makes any statistic other than q10/q50/q90 unrecoverable from the archive:
    # no bootstrap interval, no check of whether a band is unimodal, no way to see
    # that a technology was absent rather than small. It is also how the two
    # defects fixed alongside this stayed invisible. Roughly 1 MB per scenario.
    _save_draws(eu_all, em_all, scenario_name)

    # ── Country-level quantiles ───────────────────────────────────────────
    co_all = pd.concat(all_co, ignore_index=True)
    _save_quantiles(co_all, "value", ["country","year","tech","variable"],
                    RESULTS_DIR / f"mc_country_{scenario_name}.csv")

    if save_samples:
        _save_samples(all_samples, scenario_name)

    print(f"  Done. Results in code/results/")
    _print_summary(eu_all, em_all, scenario_name)


def _save_quantiles(df: pd.DataFrame, val_col: str,
                    group_cols: list, path) -> None:
    """Quantiles across draws, counting absent technologies as zero.

    A technology with a zero share contributes no row to the long-format output
    (see the share filter in run_single_sample), so a naive groupby-quantile takes
    the quantile over only the draws in which the technology exists. That makes
    every reported median conditional on the technology being present: under an
    ambitious scenario where fossil heat survives in a minority of draws, the
    reported median is the median of that minority rather than of the run. Absence
    means zero heat, zero final energy and zero share, so we complete the panel
    over (group, sample) before quantiling.
    """
    if "sample" in df.columns:
        keys = df[group_cols].drop_duplicates()
        keys["_j"] = 1
        samples = pd.DataFrame({"sample": df["sample"].unique(), "_j": 1})
        full = keys.merge(samples, on="_j").drop(columns="_j")
        df = (full.merge(df[group_cols + ["sample", val_col]],
                         on=group_cols + ["sample"], how="left")
                  .fillna({val_col: 0.0}))
    q = (df.groupby(group_cols)[val_col]
         .quantile([0.10, 0.50, 0.90])
         .unstack(-1).reset_index())
    q.columns = group_cols + ["q10", "q50", "q90"]
    q.to_csv(path, index=False)
    print(f"  Saved: {path.name}")


def _save_draws(eu_all: pd.DataFrame, em_all: pd.DataFrame,
                scenario_name: str) -> None:
    """Persist the per-draw EU aggregates the quantile files summarise away.

    Absent technologies are written as explicit zeros, so the archive supports the
    same statistics the quantile files report and does not reproduce the
    conditional-median trap it exists to make visible.
    """
    keep = ["sample", "year", "variable", "tech", "carrier", "value"]
    df = pd.concat([eu_all[keep], em_all[keep]], ignore_index=True)
    keys = df[["year", "variable", "tech", "carrier"]].drop_duplicates()
    keys["_j"] = 1
    samples = pd.DataFrame({"sample": sorted(df["sample"].unique()), "_j": 1})
    full = keys.merge(samples, on="_j").drop(columns="_j")
    df = (full.merge(df, on=["sample", "year", "variable", "tech", "carrier"],
                     how="left")
              .fillna({"value": 0.0})
              .sort_values(["variable", "year", "tech", "carrier", "sample"]))
    p = RESULTS_DIR / f"mc_draws_{scenario_name}.csv"
    df.to_csv(p, index=False, float_format="%.6g")
    print(f"  Saved: {p.name} ({len(df):,} rows)")


def _save_samples(all_samples: list, scenario_name: str) -> None:
    sdf = pd.concat(all_samples, ignore_index=True)
    try:
        p = RESULTS_DIR / f"mc_samples_{scenario_name}.parquet"
        sdf.to_parquet(p, index=False)
        print(f"  Saved samples: {p.name}")
    except Exception:
        p = RESULTS_DIR / f"mc_samples_{scenario_name}.csv"
        sdf.to_csv(p, index=False)
        print(f"  Saved samples: {p.name}")


def _print_summary(eu_all: pd.DataFrame, em_all: pd.DataFrame,
                   scenario_name: str) -> None:
    """Print key results to console."""
    print(f"\n  === {scenario_name} Key Results ===")
    for year in YEARS:
        hs  = eu_all[(eu_all["variable"]=="useful_heat_MWh")&(eu_all["year"]==year)]["value"]
        co  = em_all[(em_all["variable"]=="co2_MtCO2")&(em_all["year"]==year)]["value"]
        hp  = eu_all[(eu_all["variable"]=="tech_share")&
                     (eu_all["tech"].isin(["hp_air","hp_ground"]))&
                     (eu_all["year"]==year)].groupby("sample")["value"].sum()
        if not hs.empty and not co.empty:
            print(f"  {year}: Heat={hs.median()/1e6:.0f} TWh | "
                  f"CO2={co.median():.0f} MtCO2 | "
                  f"HP share={hp.median()*100:.0f}%")


# ── Sensitivity runner ────────────────────────────────────────────────────────
def run_sensitivity(scenario_name: str = "STATED_POLICIES", demand: str = "hotmaps") -> None:
    """
    Run MC across all sensitivity axes:
      Carbon price:   LOW × CENTRAL × HIGH
      H2 trajectory:  RAPID × CENTRAL × SLOW × STRANDED
      Discount rate:  4% × 5% × 8%

    Saves mc_sensitivity_{scenario}.csv with axis labels.
    demand: hotmaps | bottomup (selects the building-stock basis).
    """
    scen = scenario_from_config(scenario_name)
    _stock_f = ("building_stock_nuts3_bottomup.csv" if demand == "bottomup"
                else "building_stock_nuts3.csv")
    _feas_f  = ("hp_dh_feasibility_bottomup.csv" if demand == "bottomup"
                else "hp_dh_feasibility.csv")
    stock = pd.read_csv(PROCESSED_DIR / _stock_f)
    feas  = pd.read_csv(PROCESSED_DIR / _feas_f)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Use fewer samples for sensitivity (speed)
    N_SENS = max(50, N_MONTE_CARLO_SAMPLES // 4)

    all_rows = []
    # One-at-a-time axes only: the base case plus each axis varied to its
    # bounds with the other two held at base. The sensitivity tornado (fig9)
    # needs exactly these cells; the full 3x4x3 = 36-cell grid was ~5x slower
    # and produced no extra figure.
    _base_r = DISCOUNT_RATE_SCENARIOS["base"]
    axes = [("CENTRAL", "CENTRAL", "base", _base_r)]
    for c in CARBON_PRICE_SCENARIOS:
        if c != "CENTRAL":
            axes.append((c, "CENTRAL", "base", _base_r))
    for h in H2_PRICE_TRAJECTORIES:
        if h != "CENTRAL":
            axes.append(("CENTRAL", h, "base", _base_r))
    for r_name, r_val in DISCOUNT_RATE_SCENARIOS.items():
        if r_name != "base":
            axes.append(("CENTRAL", "CENTRAL", r_name, r_val))

    for c_scen, h_scen, r_name, r_val in axes:
        tag = f"C={c_scen} H={h_scen} r={r_name}"
        print(f"  Sensitivity: {tag}")
        rng = np.random.default_rng(RNG_SEED)

        sample_eu = []
        for i in range(N_SENS):
            params = sample_parameters(scen, rng, c_scen, h_scen, r_val)
            sdf = run_single_sample(scen, params, stock, feas)
            sdf = compute_emissions_df(sdf, grid_mult=scen.grid_mult)
            eu_df = aggregate_eu(sdf)
            em_df = aggregate_emissions(sdf)

            for _, row in eu_df.iterrows():
                all_rows.append({
                    "carbon_scenario": c_scen,
                    "h2_scenario":     h_scen,
                    "discount_rate":   r_name,
                    "sample":          i,
                    **row.to_dict(),
                })
            for _, row in em_df.iterrows():
                all_rows.append({
                    "carbon_scenario": c_scen,
                    "h2_scenario":     h_scen,
                    "discount_rate":   r_name,
                    "sample":          i,
                    **row.to_dict(),
                })

    sens_df = pd.DataFrame(all_rows)
    out = RESULTS_DIR / f"mc_sensitivity_{scenario_name}.csv"
    sens_df.to_csv(out, index=False)
    print(f"  Sensitivity saved: {out.name} ({len(sens_df)} rows)")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Monte Carlo EU+CH+UK buildings heat model (Steps 1+2+3 integrated).")
    parser.add_argument("--scenario",  default="STATED_POLICIES",
                        help="Scenario: CURRENT_POLICIES | STATED_POLICIES | NET_ZERO | H2_PUSH")
    parser.add_argument("--carbon",    default="CENTRAL",
                        help="Carbon price: LOW | CENTRAL | HIGH")
    parser.add_argument("--h2",        default="CENTRAL",
                        help="H2 trajectory: RAPID | CENTRAL | SLOW | STRANDED")
    parser.add_argument("--discount",  default="base",
                        help="Discount rate: base (5%%) | social (4%%) | private (8%%)")
    parser.add_argument("--sensitivity", action="store_true",
                        help="Run full sensitivity analysis across all axes")
    parser.add_argument("--save-samples", action="store_true",
                        help="Save full NUTS3 sample outputs")
    parser.add_argument("--demand", default="hotmaps",
                        choices=["hotmaps", "bottomup"],
                        help="Demand basis: hotmaps (2015 baseline) | bottomup "
                             "(29-country EUBUCCO+TABULA build)")
    args = parser.parse_args()

    r = DISCOUNT_RATE_SCENARIOS.get(args.discount, DISCOUNT_RATE_REAL)

    if args.sensitivity:
        run_sensitivity(args.scenario, demand=args.demand)
    else:
        run_monte_carlo(
            args.scenario,
            save_samples=args.save_samples,
            carbon_scenario=args.carbon,
            h2_scenario=args.h2,
            discount_rate=r,
            demand=args.demand,
        )


if __name__ == "__main__":
    main()
