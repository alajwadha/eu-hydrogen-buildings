"""
code/src/Optimisation.py  —  Step 5: COST_OPT least-cost decarbonisation pathway
=================================================================================
A cost-optimisation scenario that *replaces* the exogenous fixed-share scenarios
(STATED_POLICIES / NET_ZERO / H2_PUSH) with a linear program: it picks the least-cost mix of
heating technologies, per country and milestone year, that satisfies an emissions
glide path and a set of physical/policy constraints.

It reuses the audited techno-economics from Economics.py (compute_lcoh, which already
bundles annualised CAPEX + FOM + VOM + fuel + the ETS2 carbon adder) and the
country/year emission factors from Emissions.py. Nothing here re-derives costs; the LP
only *allocates* demand across technologies given those costs and constraints.

Design (see literature/scenario_assumptions_audit.md):

  Decision variable
    x[c, t, y] in [0, 1]  — share of country c's useful heat met by technology t in
    milestone year y. Country-level (not NUTS3): the LP is small and the cost-optimal
    EU pathway is naturally framed at country/EU level. Per-NUTS3 feasibility enters as
    demand-weighted country ceilings.

  Objective  (minimise discounted system cost of the heating pathway)
    min  sum_{c,t,y}  w[y] * pv[y] * LCOH[c,t,y] * demand[c,y] * x[c,t,y]
    where LCOH is EUR/MWh_useful (Economics.compute_lcoh, ETS2 inside), demand[c,y] is
    country useful heat (MWh), w[y] is the representative-period length of milestone y,
    and pv[y] = 1/(1+r)^(y-2025) discounts to 2025.

  Constraints
    1. Balance:        sum_t x[c,t,y] = 1                       for all c, y
    2. 2025 anchor:    x[c,t,2025] = START_MIX[t]               (transition, not a jump)
    3. Feasibility:    x[c,'district_heat',y] <= dh_cap[c]
                       x[c,'hp_ground',y]    <= gshp_cap[c]
                       x[c,'hp_air']+x[c,'hp_ground'] <= hp_cap[c]
                       x[c,'h2_boiler',y]    <= H2_CAP[y]
                       x[c,'biomass_boiler',y] <= BIOMASS_CAP   (sustainable-supply limit)
    4. Boiler ban:     x[c,'gas']+x[c,'oil'] <= fossil_ceiling(c,y)  (Policy.BOILER_BANS)
    5. Turnover:       |x[c,t,y] - x[c,t,y_prev]| <= TURNOVER_RATE * (y - y_prev)
                       (trajectory mode only; ~5%/yr stock replacement, 20-yr lifetime)
    6. Emissions cap:  sum_t x[c,t,y]*scope1_ef[c,t,y]*demand[c,y] <= cap[c,y]
                       PER COUNTRY, on SCOPE-1 (on-site gas/oil combustion) only.

  Why per-country. Each country must meet the target from its OWN 2025 scope-1 baseline,
  so every country gets a real cost-optimal decarbonisation pathway (consistent with the
  project's country-by-country design). This differs from an EU-aggregate cap, where
  cheap-abatement countries over-deliver and others free-ride. With a per-country cap the
  cap's shadow price varies by country: it is the implied carbon price *that country* needs
  to hit the target (written to cost_opt_shadow_prices.csv).

  Why scope-1. The cap follows the EPBD "zero-emission building" definition (no on-site
  fossil). Electricity-grid and district-heat decarbonisation are exogenous (Policy.py /
  Economics.py), so capping them here would double-count grid policy and make a -100%
  (net-zero on-site) target artificially infeasible. The *reported* emissions output
  still includes scope-2 grid/DH emissions via Emissions.get_emission_factor.

  Targets. Three ambition variants by 2050: -75% / -90% / -100% vs each country's 2025
  scope-1 baseline.

  Modes.
    trajectory — perfect-foresight over 2025..2050 with the turnover constraint (primary).
    snapshot   — each year optimised independently (no anchor, no turnover); a diagnostic
                 benchmark showing the cost of stock lock-in / value of foresight.

Outputs (per variant tag, e.g. COST_OPT_90):
  mc_summary_{tag}.csv    — EU tech_share + final_energy + useful_heat (q10/q50/q90)
  mc_emissions_{tag}.csv  — total (scope1+2) CO2 Mt + intensity (q10/q50/q90)
  mc_country_{tag}.csv    — per-country tech_share + co2 + useful_heat (q10/q50/q90)
  cost_opt_pathway.csv    — tidy x[c,t,y] + emissions for every variant (incl. snapshot)

Solved deterministically at central inputs, so q10 = q50 = q90 = the central optimum.
(The MC-band sampler is a documented extension point in prepare_data via fuel_mult /
discount_rate; not run by default.)

Methodological lineage: least-cost LP technology allocation under an emissions cap is the
standard bottom-up energy-system design (cf. oemof.solph, Krien et al. 2020; TIMES/MARKAL).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pulp

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "code"))

from src.Config import (PROCESSED_DIR, RESULTS_DIR, YEARS, BASE_YEAR, TECHS,
                        load_heating_mix_2025)
from src.Economics import (
    TECH_PARAMS, compute_lcoh, get_cop, DISCOUNT_RATE_REAL,
    DISCOUNT_RATE_BY_COUNTRY,
)
from src.Emissions import get_emission_factor, FUEL_EF_TCO2_PER_MWH
from src.Policy import BOILER_BANS


# =============================================================================
# Model assumptions (documented; central case)
# =============================================================================
# 2025 starting mix — anchors the trajectory so COST_OPT is a transition, not an
# instant jump to the cost optimum. Mirrors the Simulation.py base mix (fossil-heavy
# EU residential stock today). Sums to 1.0.
START_MIX: Dict[str, float] = {
    "gas_boiler":        0.42,
    "oil_boiler":        0.12,
    "biomass_boiler":    0.10,
    "resistance_heater": 0.04,
    "hp_air":            0.13,
    "hp_ground":         0.05,
    "district_heat":     0.12,
    "h2_boiler":         0.02,
}

# Demand trajectory (exogenous, held common across the three emissions targets so the
# *technology* mix is what responds to the cap). STATED_POLICIES-central renovation path.
DEMAND_REDUCTION_2050 = 0.35     # vs base useful heat (audit: EU Ref / Renovation Wave)
DEMAND_SHAPE_P        = 1.3      # transition shape (mid of Simulation's 0.8-1.8 range)

# Sustainable-biomass ceiling for buildings (EU biomass is supply-limited; flooding the
# mix with biomass is not credible). Documented assumption.
BIOMASS_CAP = 0.20

# Hydrogen-for-buildings availability ceiling, ramping (audit: building H2 is a niche;
# keep it bounded unless costs make it attractive within the cap).
H2_CAP = {2025: 0.00, 2030: 0.02, 2040: 0.06, 2050: 0.10}

# Stock turnover: ~5%/yr replaceable at a 20-yr boiler/HP lifetime. Caps how fast any
# technology share can grow or shrink between milestone years (trajectory mode).
TURNOVER_RATE = 0.05             # per year

# Ground-source HP needs a borehole or a large ground loop, so it is realistically
# confined to detached single-family homes with suitable plot/geology. The ceiling is
# the deployable fraction of single-family heat demand. Empirically GSHP is <2% of EU
# dwellings today; even Sweden, the global leader, reaches ~20% of single-family homes.
# We therefore cap the 2050 GSHP-deployable share at 0.15 of single-family demand
# (sweep 0.10-0.25 in scripts.cost_opt_sensitivity) -- a defensible upper bound, not a
# forecast. The previous 0.60 let GSHP supply 33-47% of all EU heat, an implausible
# constraint artefact; 0.15 yields a realistic single-digit-to-~10% GSHP share and
# shifts the cost-optimal mix toward air-source heat pumps and district heat.
GSHP_SFH_FRACTION = 0.15

# Representative-period weights (years each milestone stands in for) for the discounted
# pathway cost, across the 2025..2030..2040..2050 milestones. Trapezoidal, so the
# weights are half-intervals and sum to the 25 years the pathway actually spans. An
# earlier version used {5, 10, 10, 10}, which sums to 35: it gave the terminal year a
# full forward step and so integrated ten years beyond 2050 under a "to 2050" label,
# overweighting the endpoint by a factor of two against the trapezoidal weight. The
# same mistake was found and fixed in scripts.power_dispatch, whose weights these match.
PERIOD_WEIGHT = {2025: 2.5, 2030: 7.5, 2040: 10.0, 2050: 5.0}

COST_OPT_TARGETS = {"75": 0.75, "90": 0.90, "100": 1.00}

FOSSIL_TECHS = ("gas_boiler", "oil_boiler")

# Per-country inputs (heating_mix_2025.csv via Config). The globals above are the
# fallback when a country is missing from the file. See literature/
# heating_mix_2025_audit.md for sourcing (Eurostat nrg_d_hhq + national/EHPA).
_HMIX = load_heating_mix_2025()

def _start_mix(country: str) -> Dict[str, float]:
    """Country 2025 heating mix (8 techs), renormalised to sum exactly 1.0."""
    row = _HMIX.get(country)
    if not row:
        return dict(START_MIX)
    mix = {t: row.get(t, 0.0) for t in TECHS}
    s = sum(mix.values()) or 1.0
    return {t: v / s for t, v in mix.items()}

def _biomass_cap(country: str) -> float:
    row = _HMIX.get(country)
    return row["biomass_ceiling_2050"] if row else BIOMASS_CAP

def _h2_cap(country: str, year: int) -> float:
    """Per-country H2-for-buildings ceiling, ramping 0 (2025) -> ceiling (2050)."""
    row = _HMIX.get(country)
    ceil = row["h2_ceiling_2050"] if row else H2_CAP.get(2050, 0.10)
    t = float(np.clip((year - 2025) / 25.0, 0.0, 1.0))
    return ceil * t

def _demand_reduction(country: str) -> float:
    row = _HMIX.get(country)
    return row["demand_reduction_2050"] if row else DEMAND_REDUCTION_2050

def _turnover(country: str) -> float:
    row = _HMIX.get(country)
    return row["turnover_rate"] if row else TURNOVER_RATE

def _decay_floor(start_share: float, turnover: float, year: int,
                 anchor_year: int = 2025) -> float:
    """Lowest share a tech can reach by `year` given turnover from its anchor.

    anchor_year defaults to 2025 (the START_MIX baseline used by perfect
    foresight). The myopic roll passes the *realised* milestone the window is
    anchored to, so the feasibility floor decays from the stock actually
    standing in that year rather than always from 2025.
    """
    return start_share - turnover * (year - anchor_year)


# =============================================================================
# Data preparation
# =============================================================================
def _stock_feas_paths(demand: str) -> Tuple[Path, Path]:
    if demand == "bottomup":
        return (PROCESSED_DIR / "building_stock_nuts3_bottomup.csv",
                PROCESSED_DIR / "hp_dh_feasibility_bottomup.csv")
    return (PROCESSED_DIR / "building_stock_nuts3.csv",
            PROCESSED_DIR / "hp_dh_feasibility.csv")


def _eta(tech: str, country: str, year: int) -> float:
    """Efficiency or seasonal COP — mirrors Simulation.eff_for_tech via Economics.py."""
    if tech in ("hp_air", "hp_ground"):
        try:
            return get_cop(tech, country, year)
        except Exception:
            pass
    p = TECH_PARAMS.get(tech, {})
    e0 = p.get("efficiency_2025", p.get("scop_2025", 1.0))
    e1 = p.get("efficiency_2050", p.get("scop_2050", e0))
    t = float(np.clip((year - 2025) / 25.0, 0.0, 1.0))
    return e0 + t * (e1 - e0)


_OPT_INT_RATES = {}
try:
    import src.Config as _C
    _OPT_INT_RATES = _C.central_country_intensity_rates("STATED_POLICIES")
except Exception:
    pass


def _demand_factor(country: str, year: int) -> float:
    """Demand multiplier D(year)/D(BASE_YEAR) for COST_OPT LP (deterministic).

    Uses the LMDI multi-driver forward projection with the per-country STATED_POLICIES
    central intensity rate (same envelope-retrofit pace assumed by the LP's
    cost-minimisation under the country-specific emissions cap). Falls back
    to the legacy single-parameter `demand_reduction` if LMDI rates absent.
    """
    if _OPT_INT_RATES and country in _OPT_INT_RATES:
        import src.Config as _C
        return _C.forward_demand_ratio(country, year, _OPT_INT_RATES[country])
    t = (year - BASE_YEAR) / (2050 - BASE_YEAR)
    red = float(np.clip(_demand_reduction(country) * (t ** DEMAND_SHAPE_P), 0.0, 0.9))
    return 1.0 - red


def prepare_data(demand: str = "bottomup",
                 discount_rate: float = DISCOUNT_RATE_REAL,
                 carbon_scenario: str = "CENTRAL",
                 h2_scenario: str = "CENTRAL",
                 fuel_mult: float = 1.0) -> Dict:
    """
    Assemble all LP inputs. Returns a dict of countries, demand[c,y], lcoh[c,t,y],
    scope1_ef_useful[c,t,y], total_ef_useful[c,t,y], and feasibility caps.

    fuel_mult scales LCOH (used only by the optional MC-band sampler); central = 1.0.
    """
    stock_p, feas_p = _stock_feas_paths(demand)
    stock = pd.read_csv(stock_p)
    feas = pd.read_csv(feas_p)

    countries = sorted(stock["country"].unique().tolist())

    # Base demand per country, and demand[c,y]
    base = stock.groupby("country")["heat_2015_MWh"].sum().to_dict()
    demand_cy: Dict[Tuple[str, int], float] = {}
    for c in countries:
        for y in YEARS:
            demand_cy[(c, y)] = base.get(c, 0.0) * _demand_factor(c, y)

    # Feasibility caps (demand-weighted to country level). The feasibility file already
    # carries heat_2015_MWh per (nuts, country, building_type), so use it directly.
    fm = feas.copy()
    if "heat_2015_MWh" not in fm.columns:
        fm = fm.merge(stock[["nuts_id", "country", "building_type", "heat_2015_MWh"]],
                      on=["nuts_id", "country", "building_type"], how="left")
    fm["heat_2015_MWh"] = fm["heat_2015_MWh"].fillna(0.0)
    hp_cap, dh_cap, gshp_cap = {}, {}, {}
    for c in countries:
        cdf = fm[fm["country"] == c]
        w = cdf["heat_2015_MWh"].to_numpy()
        wsum = w.sum() if w.sum() > 0 else 1.0
        hp_cap[c] = float(np.clip((cdf["hp_feasibility"].to_numpy() * w).sum() / wsum, 0.3, 1.0))
        dh_cap[c] = float(np.clip((cdf["dh_feasibility"].to_numpy() * w).sum() / wsum, 0.0, 0.7))
        sfh = cdf[cdf["building_type"] == "SFH"]["heat_2015_MWh"].sum()
        gshp_cap[c] = float(np.clip(sfh / wsum * GSHP_SFH_FRACTION, 0.0, 0.25))

    # LCOH and emission intensities per (c, t, y)
    lcoh, s1_ef, tot_ef = {}, {}, {}
    for c in countries:
        for t in TECHS:
            fuel = TECH_PARAMS[t]["fuel"]
            wacc_c = DISCOUNT_RATE_BY_COUNTRY.get(c, discount_rate)
            for y in YEARS:
                lc = compute_lcoh(t, c, y, carbon_price_scenario=carbon_scenario,
                                  discount_rate=wacc_c, h2_scenario=h2_scenario)
                if fuel_mult != 1.0:
                    lc *= fuel_mult       # band sampler: scale overall cost level
                lcoh[(c, t, y)] = lc
                eta = max(_eta(t, c, y), 0.1)
                # scope-1: only direct combustion of gas/oil
                s1 = FUEL_EF_TCO2_PER_MWH.get(fuel, 0.0) if fuel in ("gas", "oil") else 0.0
                s1_ef[(c, t, y)] = s1 / eta
                tot_ef[(c, t, y)] = get_emission_factor(fuel, c, y) / eta

    # 2025 scope-1 baseline emissions PER COUNTRY for the cap glide path. Each
    # country's emissions cap is anchored to its own 2025 baseline, so every
    # country must hit the target from where it starts (a per-country pathway).
    base_s1_c, base_tot_c = {}, {}
    for c in countries:
        sm = _start_mix(c)
        base_s1_c[c] = sum(sm[t] * s1_ef[(c, t, 2025)] * demand_cy[(c, 2025)]
                           for t in TECHS)
        # Total (scope-1 + scope-2 grid/DH) 2025 baseline, for the scope-2 cap
        # sensitivity variant (solve(cap_basis="total")).
        base_tot_c[c] = sum(sm[t] * tot_ef[(c, t, 2025)] * demand_cy[(c, 2025)]
                            for t in TECHS)
    base_s1 = sum(base_s1_c.values())   # EU total, for reporting only

    return dict(countries=countries, demand=demand_cy, lcoh=lcoh,
                s1_ef=s1_ef, tot_ef=tot_ef, hp_cap=hp_cap, dh_cap=dh_cap,
                gshp_cap=gshp_cap, base_s1=base_s1, base_s1_c=base_s1_c,
                base_tot_c=base_tot_c, discount_rate=discount_rate)


# =============================================================================
# LP construction and solve
# =============================================================================
def _fossil_ceiling(country: str, year: int) -> float:
    """Boiler-ban phase-out: existing on-site fossil declines over ~20 yr after the ban."""
    ban = BOILER_BANS.get(country, {}).get("replacement_fossil_ban", 2035)
    if year < ban:
        return 1.0
    return float(np.clip(1.0 - (year - ban) / 20.0, 0.0, 1.0))


def _emissions_cap(base_s1: float, target: float, year: int) -> float:
    """Linear scope-1 glide from baseline (2025) to (1-target) of baseline by 2050."""
    t = float(np.clip((year - 2025) / 25.0, 0.0, 1.0))
    factor = 1.0 - target * t
    return base_s1 * factor


def solve(data: Dict, target: float, mode: str = "trajectory",
          cap_basis: str = "scope1",
          years_subset: List[int] | None = None,
          anchor: Dict[Tuple[str, str], float] | None = None) -> Dict:
    """
    Build and solve the LP for one emissions target and mode.
    Returns dict with shares[(c,t,y)], status, objective, and the emissions shadow price.

    cap_basis: 'scope1' (default; on-site gas/oil combustion only, the headline
    EPBD definition) or 'total' (scope-1 + exogenous grid/district-heat, the
    scope-2 sensitivity variant). 'total' caps each country against its 2025
    total-emissions baseline using the total emission factor.

    years_subset / anchor are the rolling-horizon hooks used by solve_myopic and
    leave the public perfect/snapshot behaviour untouched when both are None:

      years_subset : the milestone years to optimise jointly (the look-ahead
                     window). Defaults to all of YEARS. Variables, balance,
                     feasibility, turnover and the cap are built only over these
                     years, so a window {2030,2040} optimises just those two.
      anchor       : {(country, tech): realised share} fixing the FIRST year of
                     the window to the stock actually standing then. In
                     trajectory mode it replaces the START_MIX 2025 anchor; the
                     same realised mix and the window's first year then become
                     the reference point for the turnover bound and the
                     feasibility decay-floor (so the window decays from where the
                     stock really is, not always from 2025).
    """
    countries = data["countries"]
    demand, lcoh = data["demand"], data["lcoh"]
    s1_ef = data["s1_ef"]
    hp_cap, dh_cap, gshp_cap = data["hp_cap"], data["dh_cap"], data["gshp_cap"]
    r = data["discount_rate"]

    years = list(years_subset) if years_subset is not None else list(YEARS)
    y_anchor = years[0]                    # window's anchored first year

    prob = pulp.LpProblem(f"COST_OPT_{int(target*100)}_{mode}", pulp.LpMinimize)

    x = {(c, t, y): pulp.LpVariable(f"x_{c}_{t}_{y}", lowBound=0, upBound=1)
         for c in countries for t in TECHS for y in years}

    # Objective: discounted, period-weighted system heating cost (over the window).
    prob += pulp.lpSum(
        PERIOD_WEIGHT[y] * (1.0 / (1.0 + r) ** (y - 2025))
        * lcoh[(c, t, y)] * demand[(c, y)] * x[(c, t, y)]
        for c in countries for t in TECHS for y in years
    )

    cap_cons = {}
    for c in countries:
        sm = _start_mix(c)                 # per-country 2025 mix (sums to 1.0)
        turn = _turnover(c)                # per-country stock turnover rate
        # Reference stock the window decays/turns over from: the injected realised
        # anchor if given, else the 2025 START_MIX (unchanged default behaviour).
        ref = ({t: anchor[(c, t)] for t in TECHS} if anchor is not None else sm)
        start_hp = ref["hp_air"] + ref["hp_ground"]
        # The anchored first year is fixed and never feasibility-/turnover-clipped,
        # exactly as 2025 is exempt in the default path (y > 2025 guard below).
        for y in years:
            # 1. balance
            prob += pulp.lpSum(x[(c, t, y)] for t in TECHS) == 1.0, f"bal_{c}_{y}"
            # 3. feasibility ceilings — constrain *future* deployment (y>anchor), not the
            #    anchored stock. A country that already exceeds a feasibility cap
            #    (e.g. DK 66% district heat, BG 50% biomass) is allowed to keep that
            #    stock and decay it toward the cap no faster than turnover allows, so a
            #    high starting share never makes the LP infeasible.
            if y > y_anchor:
                def _ceil(cap, start):
                    return float(np.clip(
                        max(cap, _decay_floor(start, turn, y, y_anchor)), 0.0, 1.0))
                prob += x[(c, "district_heat", y)] <= _ceil(dh_cap[c], ref["district_heat"])
                prob += x[(c, "hp_ground", y)] <= _ceil(gshp_cap[c], ref["hp_ground"])
                prob += (x[(c, "hp_air", y)] + x[(c, "hp_ground", y)]
                         <= _ceil(hp_cap[c], start_hp))
                prob += x[(c, "h2_boiler", y)] <= _ceil(_h2_cap(c, y), ref["h2_boiler"])
                prob += x[(c, "biomass_boiler", y)] <= _ceil(_biomass_cap(c), ref["biomass_boiler"])
                # 4. boiler-ban fossil ceiling
                prob += (x[(c, "gas_boiler", y)] + x[(c, "oil_boiler", y)]
                         <= _fossil_ceiling(c, y)), f"fossilban_{c}_{y}"

        # 2. anchor (trajectory mode only) — fix the window's first year to the
        #    observed/realised mix; snapshot mode leaves every year free.
        if mode == "trajectory":
            for t in TECHS:
                prob += x[(c, t, y_anchor)] == ref[t], f"anchor_{c}_{t}"
            # 5. turnover bounds between consecutive milestones in the window
            #    (per-country rate)
            for t in TECHS:
                for i in range(1, len(years)):
                    y0, y1 = years[i - 1], years[i]
                    lim = turn * (y1 - y0)
                    prob += x[(c, t, y1)] - x[(c, t, y0)] <= lim
                    prob += x[(c, t, y0)] - x[(c, t, y1)] <= lim

    # 6. PER-COUNTRY scope-1 emissions cap per year — each country must hit the
    #    target from its own 2025 baseline (no cross-country averaging).
    _use_total = (cap_basis == "total")
    base_c = data["base_tot_c"] if _use_total else data["base_s1_c"]
    ef_cap = data["tot_ef"] if _use_total else s1_ef
    for c in countries:
        for y in years:
            cap = _emissions_cap(base_c[c], target, y)
            con = pulp.lpSum(ef_cap[(c, t, y)] * demand[(c, y)] * x[(c, t, y)]
                             for t in TECHS) <= cap
            name = f"emcap_{c}_{y}"
            prob += con, name
            cap_cons[(c, y)] = name

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    shares = {k: float(v.value() or 0.0) for k, v in x.items()}

    # Shadow price of each (country, year) cap = the implied carbon price
    # (EUR/tCO2) that country needs in that year to hit its target.
    #
    # The raw dual is in units of the OBJECTIVE, which is period-weighted and
    # discounted to 2025, while the cap constraint is in plain tonnes of that year.
    # Dividing by w[y]*pv[y] returns it to euros per tonne in year-y money, which is
    # what "implied carbon price" means and what the manuscript quotes. Reporting the
    # raw dual instead inflates it by that factor, about 3x at 2050, and makes the
    # number move whenever the period weights change even though the real price cannot.
    shadow = {}
    for (c, y), nm in cap_cons.items():
        con = prob.constraints.get(nm)
        pi = getattr(con, "pi", None)
        norm = PERIOD_WEIGHT[y] * (1.0 / (1.0 + r) ** (y - 2025))
        shadow[(c, y)] = abs(pi) / norm if pi is not None else float("nan")

    return dict(shares=shares, status=pulp.LpStatus[status],
                objective=float(pulp.value(prob.objective) or 0.0),
                shadow_price=shadow)


# =============================================================================
# Foresight relaxation: realised-cost scoring + myopic rolling horizon
# =============================================================================
def realised_cost(data: Dict, shares: Dict[Tuple[str, str, int], float],
                  retro: Dict[Tuple[str, int], float] | None = None) -> float:
    """Discounted, period-weighted system cost of a GIVEN share trajectory.

    Identical objective expression to solve()/solve_with_retrofit(), evaluated on
    an arbitrary realised mix instead of LP variables. This is what makes the
    three foresight modes commensurable: perfect, myopic and snapshot each
    produce a full {(c,t,y)} trajectory, and we score every one of them on the
    SAME realised-cost metric. (The raw LP objective of snapshot is NOT
    comparable to perfect's because snapshot is a relaxation that drops the 2025
    anchor and so re-allocates the existing stock for free in every year,
    including 2025; scoring its realised mix here removes that free lunch.)

    If retro is given, the retrofit (negawatt) cost is added at each country's
    Ipsos retrofit LCOH so retrofit and non-retrofit runs stay comparable.
    """
    demand, lcoh = data["demand"], data["lcoh"]
    r = data["discount_rate"]
    cost = 0.0
    for c in data["countries"]:
        for y in YEARS:
            disc = PERIOD_WEIGHT[y] * (1.0 / (1.0 + r) ** (y - 2025))
            for t in TECHS:
                cost += disc * lcoh[(c, t, y)] * demand[(c, y)] * shares.get((c, t, y), 0.0)
    return float(cost)


def solve_myopic(data: Dict, target: float, lookahead: int = 1,
                 cap_basis: str = "scope1",
                 retrofit: bool = False,
                 country_intensity: Dict | None = None) -> Dict:
    """Rolling-horizon (myopic) relaxation of perfect foresight.

    Perfect foresight solves 2025..2050 jointly with one objective, so the cap
    that only bites in 2050 already shapes the 2030 stock it commits. Myopia
    relaxes exactly that — and ONLY that: the cost data, carbon data, caps,
    feasibility ceilings and the turnover rule are all untouched; only the set
    of years seen jointly changes.

    Algorithm (per the task's rolling horizon):
      * Anchor the realised 2025 stock to the observed START_MIX.
      * For each decision milestone y in {2025, 2030, 2040}, solve the
        trajectory LP over the window [y, ... up to `lookahead` further
        milestones], anchored to the realised stock standing at y.
      * COMMIT the window's first post-anchor year as realised stock (the stock
        decays/turns over from the realised anchor via the existing turnover
        rule, carried forward as the next window's anchor).
      * Roll forward to 2030, 2040, 2050.

    lookahead = number of FUTURE milestones the planner sees beyond the year it
    is committing (1 = sees only the next milestone; large = full horizon). With
    lookahead >= len(YEARS) the first window already spans 2025..2050 and the
    roll reproduces perfect foresight exactly (validated).

    Returns the same dict shape as solve()/solve_with_retrofit (a full realised
    {(c,t,y)} trajectory, status, the realised-cost objective, 2050 shadow
    prices), plus retro_share when retrofit=True.
    """
    countries = data["countries"]
    c_retro = None
    if retrofit:
        ci = country_intensity or {}
        c_retro = {c: retrofit_cost_per_mwh(ci.get(c, 150.0)) for c in countries}

    def _solve_window(years_win, anch, anch_retro):
        if retrofit:
            return _solve_retrofit_window(data, target, c_retro, years_win,
                                          anch, anch_retro, cap_basis)
        return solve(data, target, mode="trajectory", cap_basis=cap_basis,
                     years_subset=years_win, anchor=anch)

    # Realised trajectory, seeded with the observed 2025 mix (the true anchor).
    realised: Dict[Tuple[str, str, int], float] = {}
    realised_retro: Dict[Tuple[str, int], float] = {}
    for c in countries:
        sm = _start_mix(c)
        for t in TECHS:
            realised[(c, t, 2025)] = sm[t]
        realised_retro[(c, 2025)] = 0.0

    statuses = []
    last_shadow: Dict[Tuple[str, int], float] = {}
    # Decision milestones we still need to COMMIT: 2030, 2040, 2050 (2025 fixed).
    for di in range(1, len(YEARS)):
        commit_year = YEARS[di]
        anchor_year = YEARS[di - 1]
        # Window: the anchor + commit_year + up to `lookahead-1` further milestones.
        win_end = min(di + (lookahead - 1), len(YEARS) - 1)
        years_win = YEARS[di - 1: win_end + 1]
        anch = {(c, t): realised[(c, t, anchor_year)] for c in countries for t in TECHS}
        anch_retro = ({c: realised_retro[(c, anchor_year)] for c in countries}
                      if retrofit else None)
        res = _solve_window(years_win, anch, anch_retro)
        statuses.append(res["status"])
        # Commit only the first post-anchor year; the rest of the window is
        # look-ahead and discarded (re-decided when its own window arrives).
        for c in countries:
            for t in TECHS:
                realised[(c, t, commit_year)] = res["shares"].get((c, t, commit_year), 0.0)
            if retrofit:
                realised_retro[(c, commit_year)] = \
                    res.get("retro_share", {}).get((c, commit_year), 0.0)
        # Keep the most recent window's shadow prices for the committed year.
        for c in countries:
            sp = res["shadow_price"].get((c, commit_year))
            if sp is not None:
                last_shadow[(c, commit_year)] = sp

    status = "Optimal" if all(s == "Optimal" for s in statuses) else ";".join(statuses)
    out = dict(shares=realised, status=status,
               objective=realised_cost(data, realised,
                                        realised_retro if retrofit else None),
               shadow_price=last_shadow)
    if retrofit:
        out["retro_share"] = realised_retro
    return out


# ── T3: endogenous renovation depth ──────────────────────────────────────────
# Retrofit is added as a linear "negawatt" share that competes with the supply
# technologies on cost: x_retro[c,y] is the fraction of a country's useful heat
# AVOIDED by envelope renovation. Demand balance becomes
# sum_t x[c,t,y] + x_retro[c,y] = 1, so retrofit shrinks the supply shares (and
# hence both system cost and emissions). This keeps the LP linear (no bilinear
# share x demand-reduction term). The retrofit "LCOH" is the annualised envelope
# cost per MWh of useful heat avoided.
#
# Cost basis: Ipsos/Navigant (2019) "Comprehensive study of building energy
# renovation activities", Table 11 / p.80 -- medium-depth (multi-measure)
# renovation 154 EUR/m2 achieving ~41% primary-energy saving (the representative
# marginal depth). Annualised at a 5% real rate over a 30-yr envelope life
# (CRF 0.0651) and divided by the heat actually saved per m2
# (country useful-heat intensity x saving fraction), so the retrofit cost per
# MWh is COUNTRY-SPECIFIC: cheaper per MWh in cold, high-intensity stock (more
# kWh saved per m2), dearer in warm low-intensity stock.
RETROFIT_MAX_2050 = 0.40        # max useful-heat share avoidable by 2050 retrofit
RETROFIT_CRF = 0.0651           # 5% real, 30-yr envelope life
RETROFIT_COST_EUR_M2 = 154.0    # Ipsos/Navigant 2019 medium-depth
RETROFIT_SAVING_FRAC = 0.41     # Ipsos/Navigant 2019 medium-depth PE saving
RETROFIT_RAMP_PER_YR = 0.02     # retrofit share can grow <= 2 pp/yr


def retrofit_cost_per_mwh(intensity_kwh_m2: float) -> float:
    """Country retrofit LCOH (EUR/MWh_useful avoided) from the Ipsos curve."""
    heat_saved_mwh_m2 = max(intensity_kwh_m2, 1.0) / 1000.0 * RETROFIT_SAVING_FRAC
    return RETROFIT_CRF * RETROFIT_COST_EUR_M2 / heat_saved_mwh_m2


def _solve_retrofit_window(data: Dict, target: float, c_retro: Dict,
                           years_subset: List[int] | None = None,
                           anchor: Dict[Tuple[str, str], float] | None = None,
                           anchor_retro: Dict[str, float] | None = None,
                           cap_basis: str = "scope1",
                           mode: str = "trajectory") -> Dict:
    """Windowed retrofit LP core (shared by solve_with_retrofit and solve_myopic).

    With years_subset/anchor/anchor_retro all None this is the original
    full-horizon retrofit LP anchored to 2025 (unchanged behaviour). The myopic
    roll passes a window, the realised supply anchor and the realised retrofit
    anchor for the window's first year.
    """
    countries = data["countries"]
    demand, lcoh = data["demand"], data["lcoh"]
    s1_ef = data["s1_ef"]
    hp_cap, dh_cap, gshp_cap = data["hp_cap"], data["dh_cap"], data["gshp_cap"]
    r = data["discount_rate"]

    years = list(years_subset) if years_subset is not None else list(YEARS)
    y_anchor = years[0]

    prob = pulp.LpProblem(f"COST_OPT_RETRO_{int(target*100)}_{mode}", pulp.LpMinimize)
    x = {(c, t, y): pulp.LpVariable(f"x_{c}_{t}_{y}", lowBound=0, upBound=1)
         for c in countries for t in TECHS for y in years}
    xr = {(c, y): pulp.LpVariable(f"xr_{c}_{y}", lowBound=0, upBound=RETROFIT_MAX_2050)
          for c in countries for y in years}

    # Objective: supply cost + retrofit (negawatt) cost
    prob += (pulp.lpSum(PERIOD_WEIGHT[y] * (1.0 / (1.0 + r) ** (y - 2025))
                        * lcoh[(c, t, y)] * demand[(c, y)] * x[(c, t, y)]
                        for c in countries for t in TECHS for y in years)
             + pulp.lpSum(PERIOD_WEIGHT[y] * (1.0 / (1.0 + r) ** (y - 2025))
                          * c_retro[c] * demand[(c, y)] * xr[(c, y)]
                          for c in countries for y in years))

    cap_cons = {}
    for c in countries:
        sm = _start_mix(c)
        turn = _turnover(c)
        ref = ({t: anchor[(c, t)] for t in TECHS} if anchor is not None else sm)
        ref_retro = (anchor_retro[c] if anchor_retro is not None else 0.0)
        start_hp = ref["hp_air"] + ref["hp_ground"]
        for y in years:
            # 1. balance: supply shares + retrofit (avoided) = 1
            prob += (pulp.lpSum(x[(c, t, y)] for t in TECHS) + xr[(c, y)] == 1.0,
                     f"bal_{c}_{y}")
            if y > y_anchor:
                def _ceil(cap, start):
                    return float(np.clip(
                        max(cap, _decay_floor(start, turn, y, y_anchor)), 0.0, 1.0))
                prob += x[(c, "district_heat", y)] <= _ceil(dh_cap[c], ref["district_heat"])
                prob += x[(c, "hp_ground", y)] <= _ceil(gshp_cap[c], ref["hp_ground"])
                prob += (x[(c, "hp_air", y)] + x[(c, "hp_ground", y)]
                         <= _ceil(hp_cap[c], start_hp))
                prob += x[(c, "h2_boiler", y)] <= _ceil(_h2_cap(c, y), ref["h2_boiler"])
                prob += x[(c, "biomass_boiler", y)] <= _ceil(_biomass_cap(c), ref["biomass_boiler"])
                prob += (x[(c, "gas_boiler", y)] + x[(c, "oil_boiler", y)]
                         <= _fossil_ceiling(c, y)), f"fossilban_{c}_{y}"
        # 2. anchors: window's first year supply = ref mix, retrofit = ref retrofit
        if mode == "trajectory":
            for t in TECHS:
                prob += x[(c, t, y_anchor)] == ref[t], f"anchor_{c}_{t}"
            prob += xr[(c, y_anchor)] == ref_retro, f"anchor_retro_{c}"
            for t in TECHS:
                for i in range(1, len(years)):
                    y0, y1 = years[i - 1], years[i]
                    lim = turn * (y1 - y0)
                    prob += x[(c, t, y1)] - x[(c, t, y0)] <= lim
                    prob += x[(c, t, y0)] - x[(c, t, y1)] <= lim
            # 5b. retrofit ramps gradually
            for i in range(1, len(years)):
                y0, y1 = years[i - 1], years[i]
                prob += xr[(c, y1)] - xr[(c, y0)] <= RETROFIT_RAMP_PER_YR * (y1 - y0)

    # 6. emissions cap (supply techs only; retrofit avoids emissions by avoiding demand)
    _use_total = (cap_basis == "total")
    base_c = data["base_tot_c"] if _use_total else data["base_s1_c"]
    ef_cap = data["tot_ef"] if _use_total else s1_ef
    for c in countries:
        for y in years:
            cap = _emissions_cap(base_c[c], target, y)
            prob += (pulp.lpSum(ef_cap[(c, t, y)] * demand[(c, y)] * x[(c, t, y)]
                                for t in TECHS) <= cap, f"emcap_{c}_{y}")
            cap_cons[(c, y)] = f"emcap_{c}_{y}"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    shares = {k: float(v.value() or 0.0) for k, v in x.items()}
    retro = {k: float(v.value() or 0.0) for k, v in xr.items()}
    shadow = {}                              # normalised as in solve(), see the note there
    for (c, y), nm in cap_cons.items():
        con = prob.constraints.get(nm)
        pi = getattr(con, "pi", None)
        norm = PERIOD_WEIGHT[y] * (1.0 / (1.0 + r) ** (y - 2025))
        shadow[(c, y)] = abs(pi) / norm if pi is not None else float("nan")
    return dict(shares=shares, retro_share=retro, status=pulp.LpStatus[status],
                objective=float(pulp.value(prob.objective) or 0.0),
                shadow_price=shadow)


def solve_with_retrofit(data: Dict, target: float, country_intensity: Dict,
                        mode: str = "trajectory", cap_basis: str = "scope1") -> Dict:
    """Cost-optimal LP that co-optimises envelope retrofit with the supply mix.

    Identical to solve() but adds a per-country, per-year retrofit "negawatt"
    share x_retro that avoids demand at the country-specific retrofit LCOH.
    country_intensity: {country: useful-heat kWh/m2/yr} (EU-average 150 fallback).
    Returns the same dict shape as solve(), plus retro_share[(c,y)].

    Thin full-horizon wrapper over _solve_retrofit_window (the retrofit core that
    solve_myopic also reuses on rolling windows); behaviour is unchanged.
    """
    countries = data["countries"]
    c_retro = {c: retrofit_cost_per_mwh(country_intensity.get(c, 150.0))
               for c in countries}
    return _solve_retrofit_window(data, target, c_retro, years_subset=None,
                                  anchor=None, anchor_retro=None,
                                  cap_basis=cap_basis, mode=mode)


# =============================================================================
# Output assembly (matches mc_*_{scenario}.csv shape)
# =============================================================================
def _build_long(data: Dict, shares: Dict) -> Dict[str, pd.DataFrame]:
    """Turn an optimal share dict into the three mc_* long tables (q10=q50=q90)."""
    countries, demand = data["countries"], data["demand"]
    tot_ef = data["tot_ef"]

    rows = []
    for c in countries:
        for y in YEARS:
            d = demand[(c, y)]
            for t in TECHS:
                sh = shares.get((c, t, y), 0.0)
                heat = sh * d
                eta = max(_eta(t, c, y), 0.1)
                fe = heat / eta
                co2 = heat * tot_ef[(c, t, y)]   # tot_ef is per useful-MWh
                rows.append((c, y, t, TECH_PARAMS[t]["fuel"], sh, heat, fe, co2))
    df = pd.DataFrame(rows, columns=["country", "year", "tech", "carrier",
                                     "share", "useful_heat_MWh", "final_energy_MWh",
                                     "co2_tCO2"])

    # --- EU summary: useful_heat, final_energy by carrier, tech_share ---
    eu_heat = df.groupby("year", as_index=False)["useful_heat_MWh"].sum()
    eu_heat["variable"] = "useful_heat_MWh"; eu_heat["tech"] = "all"; eu_heat["carrier"] = "all"
    eu_heat = eu_heat.rename(columns={"useful_heat_MWh": "q50"})

    ts = df.groupby(["year", "tech"], as_index=False)["useful_heat_MWh"].sum()
    tot = ts.groupby("year")["useful_heat_MWh"].transform("sum")
    ts["q50"] = np.where(tot > 0, ts["useful_heat_MWh"] / tot, 0.0)
    ts["variable"] = "tech_share"; ts["carrier"] = "all"
    ts = ts[["year", "tech", "carrier", "variable", "q50"]]

    fe = df.groupby(["year", "carrier"], as_index=False)["final_energy_MWh"].sum()
    fe = fe.rename(columns={"carrier": "tech", "final_energy_MWh": "q50"})
    fe["variable"] = "final_energy_MWh"; fe["carrier"] = fe["tech"]

    summary = pd.concat([
        eu_heat[["year", "variable", "tech", "carrier", "q50"]],
        fe[["year", "variable", "tech", "carrier", "q50"]],
        ts[["year", "variable", "tech", "carrier", "q50"]],
    ], ignore_index=True)
    summary["q10"] = summary["q50"]; summary["q90"] = summary["q50"]
    summary = summary[["year", "variable", "tech", "carrier", "q10", "q50", "q90"]]

    # --- Emissions: total Mt + intensity ---
    co2_y = df.groupby("year", as_index=False)["co2_tCO2"].sum()
    co2_y["q50"] = co2_y["co2_tCO2"] / 1e6
    co2_y["variable"] = "co2_MtCO2"; co2_y["tech"] = "all"; co2_y["carrier"] = "all"
    heat_y = df.groupby("year")["useful_heat_MWh"].sum()
    inten = (df.groupby("year")["co2_tCO2"].sum() / heat_y.replace(0, np.nan) * 1e6).fillna(0)
    inten_df = inten.reset_index()
    inten_df.columns = ["year", "q50"]
    inten_df["variable"] = "co2_intensity_gCO2_kWh"; inten_df["tech"] = "all"; inten_df["carrier"] = "all"
    emissions = pd.concat([
        co2_y[["year", "variable", "tech", "carrier", "q50"]],
        inten_df[["year", "variable", "tech", "carrier", "q50"]],
    ], ignore_index=True)
    emissions["q10"] = emissions["q50"]; emissions["q90"] = emissions["q50"]
    emissions = emissions[["year", "variable", "tech", "carrier", "q10", "q50", "q90"]]

    # --- Country level: tech_share, co2_MtCO2, useful_heat_TWh ---
    crows = []
    for c in countries:
        cdf = df[df["country"] == c]
        tot_c = cdf.groupby("year")["useful_heat_MWh"].sum()
        for (y, t), v in cdf.groupby(["year", "tech"])["useful_heat_MWh"].sum().items():
            crows.append((c, y, t, "tech_share", v / max(tot_c.get(y, 1e-9), 1e-9)))
        for y, v in cdf.groupby("year")["co2_tCO2"].sum().items():
            crows.append((c, y, "all", "co2_MtCO2", v / 1e6))
        for y, v in tot_c.items():
            crows.append((c, y, "all", "useful_heat_TWh", v / 1e6))
    country = pd.DataFrame(crows, columns=["country", "year", "tech", "variable", "q50"])
    country["q10"] = country["q50"]; country["q90"] = country["q50"]
    country = country[["country", "year", "tech", "variable", "q10", "q50", "q90"]]

    return dict(summary=summary, emissions=emissions, country=country, pathway=df)


# =============================================================================
# Driver
# =============================================================================
def run_cost_opt(targets: List[str] | None = None,
                 mode: str = "trajectory",
                 demand: str = "bottomup",
                 also_snapshot: bool = True) -> None:
    """Solve every target variant and write the mc_*_{tag} outputs + a tidy pathway CSV."""
    targets = targets or list(COST_OPT_TARGETS.keys())
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nCOST_OPT  (demand={demand}, mode={mode})")
    data = prepare_data(demand=demand)
    print(f"  countries={len(data['countries'])}  2025 scope-1 baseline="
          f"{data['base_s1']/1e6:.0f} MtCO2")

    countries = data["countries"]
    pathway_frames = []
    shadow_rows = []
    # The present-value system cost per target is a headline number in the paper
    # (the "cost of ambition" spread across the three caps). It used to be printed
    # to the console only, which left the -75% figure unverifiable from the
    # committed CSVs, so it is persisted here alongside the pathway.
    objective_rows = []
    for key in targets:
        target = COST_OPT_TARGETS[key]
        res = solve(data, target, mode=mode)
        tag = f"COST_OPT_{key}"
        # Degeneracy guard: a country whose 2025 scope-1 (on-site fossil) baseline
        # is negligible (e.g. Malta -- no gas grid, near-all-electric heating) has
        # almost no tonnage under the cap, so the LP's per-tonne dual is a
        # numerically degenerate artefact (a tiny denominator inflates EUR/tCO2 to
        # implausible values like ~1,967). Such countries are flagged degenerate:
        # their implied carbon price is meaningless (there is effectively no
        # on-site fossil to abate) and is written as NaN + excluded from the
        # binding-country count, rather than reported as a real price.
        base_s1_c = data["base_s1_c"]
        MIN_S1_BASELINE_TCO2 = 0.5e6   # 0.5 MtCO2 scope-1; below this the dual is degenerate
        degenerate = {c for c in countries
                      if base_s1_c.get(c, 0.0) < MIN_S1_BASELINE_TCO2}
        # Per-country 2050 implied carbon price (cap shadow price)
        sh2050 = {c: (float("nan") if c in degenerate
                      else res["shadow_price"].get((c, 2050), float("nan")))
                  for c in countries}
        binding = [c for c, v in sh2050.items() if v == v and v > 1.0]
        mx = max([v for v in sh2050.values() if v == v], default=float("nan"))
        print(f"  [{tag}] status={res['status']}  "
              f"PV cost={res['objective']/1e9:.1f} bn EUR-yr  "
              f"2050 cap binds in {len(binding)}/{len(countries)} countries "
              f"(max implied price {mx:.0f} EUR/tCO2)")
        if res["status"] != "Optimal":
            print(f"    [warn] {tag} not optimal — skipping outputs")
            continue
        objective_rows.append({"variant": tag, "mode": mode,
                               "target_cut_frac": target,
                               "pv_system_cost_bn_eur_yr": round(res["objective"] / 1e9, 4),
                               "n_countries": len(countries),
                               "n_binding_2050": len(binding),
                               "max_shadow_2050_eur_tco2": (round(mx, 2) if mx == mx
                                                            else float("nan"))})
        tables = _build_long(data, res["shares"])
        tables["summary"].to_csv(RESULTS_DIR / f"mc_summary_{tag}.csv", index=False)
        tables["emissions"].to_csv(RESULTS_DIR / f"mc_emissions_{tag}.csv", index=False)
        tables["country"].to_csv(RESULTS_DIR / f"mc_country_{tag}.csv", index=False)
        pw = tables["pathway"].copy()
        pw["variant"] = tag
        pw["mode"] = mode
        pathway_frames.append(pw)
        for c in countries:
            for y in YEARS:
                deg = c in degenerate
                sv = (float("nan") if deg
                      else round(res["shadow_price"].get((c, y), float("nan")), 2))
                shadow_rows.append({"variant": tag, "country": c, "year": y,
                                    "shadow_eur_tco2": sv,
                                    "degenerate_low_baseline": deg})

        # snapshot diagnostic (no anchor/turnover) for the -90% case
        if also_snapshot and key == "90" and mode == "trajectory":
            snap = solve(data, target, mode="snapshot")
            if snap["status"] == "Optimal":
                snap_pw = _build_long(data, snap["shares"])["pathway"]
                snap_pw["variant"] = f"{tag}_SNAP"; snap_pw["mode"] = "snapshot"
                pathway_frames.append(snap_pw)
                objective_rows.append({"variant": f"{tag}_SNAP", "mode": "snapshot",
                                       "target_cut_frac": target,
                                       "pv_system_cost_bn_eur_yr": round(snap["objective"] / 1e9, 4),
                                       "n_countries": len(countries),
                                       "n_binding_2050": float("nan"),
                                       "max_shadow_2050_eur_tco2": float("nan")})
                print(f"  [{tag}_SNAP] snapshot diagnostic  "
                      f"PV cost={snap['objective']/1e9:.1f} bn EUR-yr "
                      f"(gap vs trajectory shows lock-in cost)")

    if pathway_frames:
        allpw = pd.concat(pathway_frames, ignore_index=True)
        allpw.to_csv(RESULTS_DIR / "cost_opt_pathway.csv", index=False)
        pd.DataFrame(shadow_rows).to_csv(
            RESULTS_DIR / "cost_opt_shadow_prices.csv", index=False)
        pd.DataFrame(objective_rows).to_csv(
            RESULTS_DIR / "cost_opt_objective.csv", index=False)
        print(f"  Saved: cost_opt_pathway.csv ({len(allpw)} rows), "
              f"cost_opt_shadow_prices.csv, cost_opt_objective.csv "
              f"+ mc_*_COST_OPT_* tables")


def main() -> None:
    ap = argparse.ArgumentParser(description="COST_OPT least-cost decarbonisation LP")
    ap.add_argument("--demand", default="bottomup", choices=["hotmaps", "bottomup"])
    ap.add_argument("--mode", default="trajectory", choices=["trajectory", "snapshot"])
    ap.add_argument("--targets", default="75,90,100",
                    help="Comma list of emission-cut targets: 75,90,100")
    ap.add_argument("--no-snapshot", action="store_true",
                    help="Skip the -90%% snapshot diagnostic")
    args = ap.parse_args()
    run_cost_opt(targets=[t.strip() for t in args.targets.split(",") if t.strip()],
                 mode=args.mode, demand=args.demand,
                 also_snapshot=not args.no_snapshot)


if __name__ == "__main__":
    main()
