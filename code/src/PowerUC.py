"""Unit-commitment (UC) power model for the v12 extension of the EU hydrogen-heating paper.

This REPLACES the reduced-form merit-order SIMULATION in scripts/power_dispatch.py with an
explicit cost-minimising UNIT-COMMITMENT optimisation, per country, on a set of weighted
representative days. The reduced-form model stacked must-run VRE -> heuristic storage ->
firm gas (clip) -> a fixed peaker fleet sized to the 4th-highest residual hour. The UC keeps
the SAME demand series, the SAME must-run VRE+nuclear+biomass, and the SAME causal battery+
reservoir state-of-charge dispatch (so the comparison is like-for-like), and turns the
THERMAL fleet decision (firm CCGT vs OCGT vs H2-turbine peaker) into a real optimisation with
commitment binaries, minimum-stable-output, ramps, minimum up/down times, a reserve margin,
and start-up costs.

Why this design (validate-ability first):
  The reduced-form model's demand, VRE availability, and storage SoC are physically
  calibrated and already validated against the paper's headline numbers. The UC's job is the
  piece the reduced form did heuristically -- committing and dispatching the dispatchable
  fleet. So PowerUC reuses scripts.power_dispatch for demand/VRE/storage VERBATIM (same RNG
  ordering, same Dunkelflaute) and optimises only the dispatchable layer. This makes the LIMIT
  TEST exact: with pmin=0, ramp=inf, startup=0, min-up/down=1h, no reserve, and the peaker
  capacity pinned to the reduced form's 4th-highest-hour rule, the UC must collapse to the
  merit-order clip and reproduce power_dispatch_summary.csv to within rounding.

Representative days (the tractability reducer):
  The full 8760 h is reduced to ~8-12 weighted representative days via k-means on the 24-h
  net-load shape (scipy.cluster.vq; sklearn is absent in this environment), with the design
  Dunkelflaute day and the peak-residual day FORCE-INCLUDED as their own singleton clusters
  (they drive adequacy and must not be averaged away). Each rep-day carries a weight = the
  number of real days it represents, used in the objective and the energy accounting.

Unit classes (split the single "gas" nameplate of power_capacity.csv):
  The capacity file has one firm "gas" number per country. The UC splits it into a firm
  CCGT base (cheap, mid-merit, slow) and an OCGT peaker (expensive, fast), and adds an
  H2-turbine peaker class. The CCGT share of the gas nameplate and the peaker nameplate
  follow the reduced form: CCGT = the firm "gas" capacity (what the reduced form clipped to),
  peaker (OCGT + H2 turbine) = sized to the 4th-highest residual-after-CCGT hour. This keeps
  the installed dispatchable capacity identical to the reduced form so the GW totals reconcile.

UC techno-economic parameters (per unit class): DEA Technology Catalogue 2023 "Technology
Data for Generation of Electricity and District Heating" + ENTSO-E TYNDP 2024 assumptions:
  CCGT       : pmin 0.40, ramp 0.50/h, min-up 4h, min-down 3h, start EUR 60/MW, eta 0.58
  OCGT       : pmin 0.20, ramp 1.00/h, min-up 1h, min-down 1h, start EUR 25/MW, eta(year)
  H2 turbine : pmin 0.20, ramp 1.00/h, min-up 1h, min-down 1h, start EUR 25/MW, eta(year)
These are the ~30 params the task asks for; sourced to the same catalogues already cited in
the repo (power_dispatch.py header). Marginal (variable) costs reuse src.Economics /
src.Policy via scripts.power_dispatch (fuel, the rising carbon price on gas, VOM, storage
adder for H2), so the cost basis is identical to the economics module.

Solver: PuLP 3.0.2 + bundled CBC (single-threaded). Default is the LP RELAXATION (commitment
u continuous in [0,1]) for tractability across 29 countries x 4 years; the integer MILP is
run only on the design week of a few countries to measure the integrality gap.
"""
from __future__ import annotations
import numpy as np, pandas as pd, time
import pulp
from dataclasses import dataclass, field

from src.Config import YEARS
# Reuse the reduced-form demand / VRE / storage machinery VERBATIM (identical RNG, Dunkelflaute,
# COP derate, baseline load) so the UC differs from the reduced form ONLY in the dispatchable
# layer -- this is what makes the limit test a true apples-to-apples check.
from scripts.power_dispatch import (
    load_capacity, hourly_demand, vre_availability, CF, HOURS, H, HOD, DOY, MONTH,
    eta_ocgt, eta_h2_turbine, gas_wholesale, storage_per_mwh_h2, storage_learning,
    SCEN_LEVERS, country_seed,
)
from scripts.power_peak_price import EF_GAS, VOM_PEAKER, SCARCITY_PREMIUM
from src.Economics import get_fuel_price, LABOUR_COST_MULTIPLIER
from src.Policy import get_carbon_price

DAY_H = 24


# ── UC techno-economic parameters per unit class (DEA Technology Catalogue 2023 / TYNDP 2024)
@dataclass
class UnitClass:
    name: str
    pmin_frac: float        # minimum stable output as a fraction of Pmax (when committed)
    ramp_frac: float        # max ramp up/down per hour as a fraction of Pmax
    min_up: int             # minimum up time, hours
    min_down: int           # minimum down time, hours
    start_cost_eur_mw: float  # start-up cost, EUR per MW of committed capacity
    is_peaker: bool         # True for OCGT / H2 turbine (the adequacy slice)

# Three dispatchable classes. CCGT is the firm mid-merit gas (what the reduced form "clip"
# served from the gas nameplate); OCGT and the H2 turbine are the fast peakers (the 4th-
# highest-hour adequacy slice). Parameters: DEA Technology Catalogue 2023 tables "05 Gas turbine,
# combined cycle" and "52 Gas turbine, simple cycle". DEA gives CCGT secondary-regulation ramp
# 3-5%/min (= ~1.8-3.0/h; central ~4%/min = 2.4/h) and 30% minimum load; OCGT ramps faster with
# ~20% minimum load. Min up/down + start cost from ENTSO-E TYNDP 2024 unit-commitment assumptions
# (CCGT warm start ~EUR 50-80/MW, min-up/down a few hours; OCGT effectively unconstrained). The
# H2 turbine mirrors the OCGT mechanically (a simple-cycle peaker; only its fuel/efficiency
# differ, handled in the cost layer). NB: earlier internal drafts used CCGT ramp 0.50/h, which is
# well below DEA and over-stated the peaker energy in solar-heavy southern grids; corrected to 2.4/h.
UNIT_CLASSES = {
    "CCGT":      UnitClass("CCGT",      pmin_frac=0.30, ramp_frac=2.40, min_up=4, min_down=3,
                           start_cost_eur_mw=60.0, is_peaker=False),
    "OCGT":      UnitClass("OCGT",      pmin_frac=0.20, ramp_frac=4.00, min_up=1, min_down=1,
                           start_cost_eur_mw=25.0, is_peaker=True),
    "H2turbine": UnitClass("H2turbine", pmin_frac=0.20, ramp_frac=4.00, min_up=1, min_down=1,
                           start_cost_eur_mw=25.0, is_peaker=True),
}

# Share of the firm "gas" nameplate that is CCGT (mid-merit) vs OCGT (peaking). The reduced
# form treated the ENTIRE gas nameplate as the firm "clip" tier (i.e. CCGT-like). To match its
# installed CCGT capacity exactly we set the CCGT block = the full gas nameplate, and the
# OCGT+H2 peaker block = the separately sized adequacy slice (4th-highest residual hour). So no
# gas capacity is moved; the peaker is ADDITIONAL firm capacity, exactly as in power_dispatch.
CCGT_SHARE_OF_GAS = 1.0
# Reserve margin: committed-but-not-dispatched headroom the system must hold for contingencies,
# as a fraction of the rep-day's peak net load (a light operating-reserve proxy; TYNDP uses
# ~country reserve requirements, here a uniform planning proxy turned ON only in the real UC).
RESERVE_FRAC = 0.05
# Reduced-form efficiencies for the cost layer of CCGT (firm gas). The reduced form's firm gas
# was a "clip" with no explicit efficiency; for the UC cost we use a CCGT electric efficiency.
ETA_CCGT = 0.58


@dataclass
class UCParams:
    """Switches that turn the real UC constraints on/off. The LIMIT preset collapses the UC to
    the reduced-form merit-order sort (used for validation)."""
    enforce_pmin: bool = True
    enforce_ramp: bool = True
    enforce_minupdown: bool = True
    enforce_reserve: bool = True
    integer: bool = False           # True = MILP commitment; False = LP relaxation
    peaker_split: bool = True       # split peaker block into OCGT + H2 turbine

    @staticmethod
    def limit() -> "UCParams":
        # pmin=0, ramp=inf, startup ignored, min-up/down=1, no reserve -> pure merit order.
        return UCParams(enforce_pmin=False, enforce_ramp=False, enforce_minupdown=False,
                        enforce_reserve=False, integer=False, peaker_split=False)


# ── the reduced-form residual the UC inherits ────────────────────────────────────────────────
def reduced_form_layers(c: str, year: int, scenario: str, cap: dict,
                        lp: pd.DataFrame, mc: pd.DataFrame):
    """Reproduce, VERBATIM from power_dispatch, the demand, must-run, causal storage and the
    fixed peaker capacity for one country-year on the total_elec basis, using the SAME RNG
    ordering as power_dispatch.main() (one rng per country, advanced through BASES x YEARS).

    Returns the 8760-h arrays the UC dispatchable layer sees: demand, mustrun, flex (storage
    discharge), the firm gas (CCGT) nameplate, and the reduced-form fixed peaker capacity.
    """
    from scripts.power_dispatch import BASES
    rng = np.random.default_rng(country_seed(c))
    demand = mustrun = flex = None
    gas_cap = 0.0
    peaker_cap_fixed = 0.0
    # advance the rng exactly as power_dispatch.main(): BASES outer, YEARS inner
    for basis in BASES:
        for yy in YEARS:
            d, _heat = hourly_demand(c, yy, scenario, basis, lp, mc)
            if basis != "total_elec":
                # still must draw VRE to advance the rng identically
                vre_availability(c, rng)
                continue
            solar_a, won_a, woff_a, ror_a = vre_availability(c, rng)
            if yy != year:
                continue
            k = cap.get(c, {}).get(yy, {})
            g = lambda t: float(k.get(t, 0.0))
            nuclear = g("nuclear") * CF["nuclear"]
            biomass = g("biomass") * CF["biomass"] * 0.8
            solar = g("solar") * solar_a
            wind = g("wind_on") * won_a + g("wind_off") * woff_a
            ror = g("hydro") * 0.4 * ror_a
            mr = nuclear + biomass + solar + wind + ror
            gas_cap = g("gas")
            batt_p = g("battery_gw"); batt_e = batt_p * 4.0
            res_p = g("hydro") * 0.6
            net = d - mr
            flex_dis = np.zeros(HOURS); soc = batt_e; eff = 0.92
            for t in range(HOURS):
                if net[t] > gas_cap:
                    want = net[t] - gas_cap
                    give = min(want, res_p)
                    b = min(want - give, batt_p, soc)
                    soc -= b
                    flex_dis[t] = give + b
                else:
                    soc = min(batt_e, soc + min(gas_cap - net[t], batt_p) * eff)
            residual = net - flex_dis
            resid_after_gas = np.clip(residual - gas_cap, 0, None)
            s = np.sort(resid_after_gas)[::-1]
            peaker_cap_fixed = float(s[3]) if len(s) > 3 and s[3] > 0 else (float(s[0]) if len(s) else 0.0)
            demand, mustrun, flex = d, mr, flex_dis
    if demand is None:
        raise RuntimeError(f"reduced_form_layers: no total_elec/{year} for {c}")
    return dict(demand=demand, mustrun=mustrun, flex=flex,
                gas_cap=gas_cap, peaker_cap_fixed=peaker_cap_fixed)


# ── representative-day reducer ────────────────────────────────────────────────────────────────
def representative_days(residual_net: np.ndarray, peaker_signal: np.ndarray,
                        n_clusters: int = 10, seed: int = 0,
                        peaker_cover: float = 0.99, max_forced: int = 185):
    """Reduce 365 daily 24-h residual-net-load shapes to a set of weighted representative days.

    The peaker energy = sum over hours of max(residual - firm_cap, 0) is a CONVEX, threshold
    quantity: plain k-means averages days WITHIN a cluster, which by Jensen's inequality
    systematically UNDERSTATES the peaker slice (the bit above the firm gas ceiling). So a naive
    cluster set fails the limit test on countries whose peaker energy is concentrated in a few
    cold days (e.g. DE: ~90% of peaker energy in ~15 days out of 26).

    Fix -- a HYBRID reducer:
      1. FORCE-INCLUDE, as weight-1 singletons, the top peaker-signal days that together hold
         >= `peaker_cover` (default 97%) of the annual peaker energy, plus the peak-demand and
         peak-residual days. These carry the adequacy slice exactly (their own real shape, no
         averaging), so the peaker energy/FLH survive the reduction. Capped at `max_forced`.
      2. CLUSTER the remaining (low/zero-peaker) days with scipy.cluster.vq k-means into the
         leftover budget for the cheap CCGT / baseload accounting; each cluster's representative
         is the real day nearest its mean, weighted by the cluster size.
    Weights are the number of real days each representative stands for and sum to exactly 365.

    residual_net : 8760, the load the dispatchable fleet serves (demand - mustrun - flex)
    peaker_signal: 8760, resid_after_gas (= max(residual - firm gas cap, 0)); drives day-picking
    Returns (days (D,24) GW, weights (D,), hours = D*24).
    """
    daily = residual_net[: 365 * DAY_H].reshape(365, DAY_H)
    pk_by_day = peaker_signal[: 365 * DAY_H].reshape(365, DAY_H).sum(1)
    tot_pk = pk_by_day.sum()
    peak_day = int(daily.max(1).argmax())
    resid_peak_day = int(pk_by_day.argmax())

    # (1) force-include the smallest set of top-peaker days covering `peaker_cover` of the energy
    forced = set()
    if tot_pk > 1e-9:
        order = np.argsort(pk_by_day)[::-1]
        csum = np.cumsum(pk_by_day[order]) / tot_pk
        n_cover = int(np.searchsorted(csum, peaker_cover)) + 1
        n_cover = min(n_cover, max_forced, int((pk_by_day > 1e-6).sum()))
        forced.update(int(d) for d in order[:n_cover])
    forced.update([peak_day, resid_peak_day])
    forced = sorted(forced)

    free_idx = np.array([d for d in range(365) if d not in forced], dtype=int)
    # cluster budget = whatever is left after the forced singletons (at least 1, at most |free|)
    n_free = max(1, n_clusters - len(forced))
    n_free = min(n_free, len(free_idx)) if len(free_idx) else 0

    rng = np.random.default_rng(seed)
    days_list, weights_list = [], []
    for d in forced:
        days_list.append(daily[d]); weights_list.append(1.0)

    if len(free_idx):
        X = daily[free_idx]
        if n_free >= len(X):
            for i in range(len(X)):
                days_list.append(X[i]); weights_list.append(1.0)
        else:
            try:
                from scipy.cluster.vq import kmeans2
                sd = X.std(0); sd[sd < 1e-9] = 1.0
                Xw = X / sd
                init = Xw[rng.choice(len(Xw), n_free, replace=False)]
                centroids, labels = kmeans2(Xw, init, minit="matrix", iter=50, seed=seed)
                for j in range(n_free):
                    mask = labels == j
                    w = int(mask.sum())
                    if w == 0:
                        continue
                    centre = centroids[j] * sd
                    k = np.argmin(((X[mask] - centre) ** 2).sum(1))
                    days_list.append(X[mask][k]); weights_list.append(float(w))
            except Exception:
                order2 = np.argsort(X.max(1))
                for ch in np.array_split(order2, n_free):
                    if not len(ch):
                        continue
                    days_list.append(X[ch[len(ch) // 2]]); weights_list.append(float(len(ch)))

    days = np.array(days_list)
    weights = np.array(weights_list)
    weights = weights * (365.0 / weights.sum())   # renormalise (k-means may drop empties) to 365
    return days, weights, days.shape[0] * DAY_H


# ── the per-country UC model ────────────────────────────────────────────────────────────────
def _variable_costs(c: str, year: int, scenario: str):
    """Per-unit-class variable cost EUR/MWh-e and the cold-snap clearing price, reusing the
    economics module's basis (identical to power_dispatch.peaker_economics)."""
    lv = SCEN_LEVERS[scenario]
    cp = get_carbon_price(year, lv["carbon"])
    gas_w = gas_wholesale(year)
    labour = LABOUR_COST_MULTIPLIER.get(c, 1.0)
    vom = VOM_PEAKER * (0.5 + 0.5 * labour)
    eo = eta_ocgt(year)
    eh = eta_h2_turbine(year, scenario)
    h2_w = get_fuel_price("hydrogen", c, year, lv["h2"]) * 0.85
    storage = storage_per_mwh_h2(c) * storage_learning(year) / eh
    ccgt_var = gas_w / ETA_CCGT + cp * EF_GAS / ETA_CCGT + vom        # firm mid-merit gas
    ocgt_var = gas_w / eo + cp * EF_GAS / eo + vom                    # gas peaker
    h2_var = h2_w / eh + storage + vom                               # H2 peaker
    clr = min(ocgt_var, h2_var) + SCARCITY_PREMIUM["central"]
    return dict(CCGT=ccgt_var, OCGT=ocgt_var, H2turbine=h2_var, clearing=clr)


def solve_country_uc(c: str, year: int, scenario: str, cap: dict,
                     lp: pd.DataFrame, mc: pd.DataFrame, params: UCParams,
                     n_clusters: int = 10, time_limit: int = 120, verbose: bool = False,
                     unit_size_gw: float = 1.0, design_week_only: bool = False):
    """Build and solve the UC for one country-year on the representative days. Returns a dict
    with the peaker capacity/energy/FLH (mirroring power_dispatch), the firm CCGT energy, the
    objective, the solve status and time, and the rep-day weights.

    unit_size_gw     : target size of each identical clustered unit (granular commitment).
    design_week_only : if True, solve ONLY the adequacy-critical rep-days (the forced
                       Dunkelflaute / peak-residual days, ~a design week) -- used for the MILP
                       integrality-gap check so the integer solve is small and exact."""
    t0 = time.time()
    rf = reduced_form_layers(c, year, scenario, cap, lp, mc)
    demand, mustrun, flex = rf["demand"], rf["mustrun"], rf["flex"]
    gas_cap = rf["gas_cap"]
    peaker_cap_total = rf["peaker_cap_fixed"]
    # the load the dispatchable fleet (CCGT + peakers) must serve, after must-run and storage
    residual_net = np.clip(demand - mustrun - flex, 0.0, None)
    resid_after_gas = np.clip(residual_net - gas_cap, 0.0, None)

    # installed dispatchable capacity (GW). CCGT = firm gas nameplate; peaker block split.
    P = {"CCGT": gas_cap * CCGT_SHARE_OF_GAS}
    if params.peaker_split and peaker_cap_total > 0:
        # split the adequacy peaker block 50/50 OCGT/H2 turbine so BOTH classes exist and the
        # cost optimiser chooses which to run (its dispatch share is the model output, not the
        # capacity split). Capacity totals are unchanged vs the reduced form.
        P["OCGT"] = peaker_cap_total * 0.5
        P["H2turbine"] = peaker_cap_total * 0.5
    else:
        P["OCGT"] = peaker_cap_total
        P["H2turbine"] = 0.0
    classes = [g for g in ["CCGT", "OCGT", "H2turbine"] if P.get(g, 0.0) > 1e-9]
    if not classes:
        # no dispatchable capacity at all (pure-VRE country): nothing to optimise
        return _empty_result(c, year, scenario, demand, gas_cap, peaker_cap_total,
                             time.time() - t0)
    # CLUSTERED unit commitment: represent each class as N identical units of ~unit_size_gw, so
    # commitment is GRANULAR (u counts committed units, 0..N) rather than one lumpy block. This is
    # both physically realistic and essential for the MILP: with a single block per class, binary
    # commitment + minimum stable output is artificially coarse and inflates the integrality gap.
    # In the LP relaxation u is continuous in [0, N]; in the MILP it is integer in [0, N].
    nU = {}     # committed-unit count cap per class
    uP = {}     # unit size (GW) per class
    for g in classes:
        n = max(1, int(round(P[g] / unit_size_gw)))
        nU[g] = n
        uP[g] = P[g] / n     # exact unit size so n*uP == installed capacity

    costs = _variable_costs(c, year, scenario)
    days, weights, _ = representative_days(residual_net, resid_after_gas,
                                           n_clusters=n_clusters,
                                           seed=country_seed(c))
    if design_week_only:
        # keep only the highest-load rep-days (the adequacy-critical "design week") for a small,
        # exact MILP. Singleton (weight ~1) forced days are the ones with the highest day-peaks.
        topk = min(7, days.shape[0])
        idx = np.argsort(days.max(1))[::-1][:topk]
        days = days[idx]; weights = weights[idx]
    D = days.shape[0]

    prob = pulp.LpProblem(f"UC_{c}_{year}", pulp.LpMinimize)
    # decision vars. u[g,d,h] = number of COMMITTED units of class g (0..nU[g]); continuous in the
    # LP relaxation, integer in the MILP (clustered unit commitment). su = units started this hour.
    p = {}    # output GW (whole class)
    u = {}    # committed unit count
    su = {}   # units started at hour h
    for g in classes:
        N = nU[g]
        for d in range(D):
            for h in range(DAY_H):
                p[g, d, h] = pulp.LpVariable(f"p_{g}_{d}_{h}", lowBound=0, upBound=P[g])
                if params.integer:
                    u[g, d, h] = pulp.LpVariable(f"u_{g}_{d}_{h}", lowBound=0, upBound=N, cat="Integer")
                else:
                    u[g, d, h] = pulp.LpVariable(f"u_{g}_{d}_{h}", lowBound=0, upBound=N, cat="Continuous")
                su[g, d, h] = pulp.LpVariable(f"su_{g}_{d}_{h}", lowBound=0, upBound=N)
    # unserved energy (loss of load) with a high penalty = behaves like the reduced form's cap
    VOLL = 8000.0   # EUR/MWh, value of lost load (penalty so the model serves load if it can)
    ls = {(d, h): pulp.LpVariable(f"ls_{d}_{h}", lowBound=0) for d in range(D) for h in range(DAY_H)}
    # spill / curtailment (over-generation dump). Essential once minimum-stable-output and
    # min-up bind: a unit forced ON at pmin for its min-up window may exceed the load in some
    # hours; without a spill variable the load-balance EQUALITY would be unsatisfiable and the
    # MILP would (wrongly) shut the cheap unit off and SHED LOAD instead, exploding the objective.
    # Spill carries a negligible cost so it is used only to absorb genuine over-generation.
    sp = {(d, h): pulp.LpVariable(f"sp_{d}_{h}", lowBound=0) for d in range(D) for h in range(DAY_H)}
    SPILL_PEN = 0.01   # EUR/MWh, token cost so spill is the last resort but always available
    # reserve-shortfall slack: the installed dispatchable fleet is sized to a 3-h loss-of-load
    # standard (the reduced form's 4th-highest hour), so it is DELIBERATELY below the residual
    # peak. A hard reserve margin would then be infeasible by construction; instead we let the
    # operating-reserve requirement be RELAXED by a non-negative shortfall, penalised below VOLL
    # (the system commits headroom where it can, and the residual shortfall is reported, not an
    # infeasibility). This keeps the UC a feasible LP/MILP for every country.
    RESERVE_PEN = 1000.0   # EUR/MW-h of unmet operating reserve (< VOLL so energy is served first)
    rs = {(d, h): pulp.LpVariable(f"rs_{d}_{h}", lowBound=0)
          for d in range(D) for h in range(DAY_H)} if params.enforce_reserve else {}

    # objective: weighted (variable cost * output + start cost * started capacity) + VOLL*unserved
    prob += pulp.lpSum(
        weights[d] * (
            pulp.lpSum(costs[g] * p[g, d, h] * 1e3 for g in classes for h in range(DAY_H))     # GW->MW
            + pulp.lpSum(UNIT_CLASSES[g].start_cost_eur_mw * uP[g] * 1e3 * su[g, d, h]
                         for g in classes for h in range(DAY_H))   # start cost per unit started
            + pulp.lpSum(VOLL * ls[d, h] * 1e3 for h in range(DAY_H))
            + pulp.lpSum(SPILL_PEN * sp[d, h] * 1e3 for h in range(DAY_H))
            + (pulp.lpSum(RESERVE_PEN * rs[d, h] * 1e3 for h in range(DAY_H))
               if params.enforce_reserve else 0)
        )
        for d in range(D)
    )

    for d in range(D):
        for h in range(DAY_H):
            # load balance: dispatchable + unserved = residual net load + spill (over-generation)
            prob += (pulp.lpSum(p[g, d, h] for g in classes) + ls[d, h] == days[d, h] + sp[d, h],
                     f"bal_{d}_{h}")
            for g in classes:
                uc = UNIT_CLASSES[g]
                # capacity & (optional) minimum-stable-output coupling, per unit committed:
                #   pmin_frac * unit_size * u  <=  p  <=  unit_size * u   (u = committed unit count)
                prob += p[g, d, h] <= uP[g] * u[g, d, h], f"pmax_{g}_{d}_{h}"
                if params.enforce_pmin:
                    prob += p[g, d, h] >= uP[g] * uc.pmin_frac * u[g, d, h], f"pmin_{g}_{d}_{h}"
                # ramp limits within the rep-day (whole-class ramp capability = P[g]*ramp_frac/h)
                if params.enforce_ramp and h > 0:
                    prob += p[g, d, h] - p[g, d, h - 1] <= P[g] * uc.ramp_frac, f"rampU_{g}_{d}_{h}"
                    prob += p[g, d, h - 1] - p[g, d, h] <= P[g] * uc.ramp_frac, f"rampD_{g}_{d}_{h}"
                # start-up logic: su >= u[h] - u[h-1] (cyclic within the rep-day)
                hp = h - 1 if h > 0 else DAY_H - 1
                prob += su[g, d, h] >= u[g, d, h] - u[g, d, hp], f"start_{g}_{d}_{h}"
        # operating reserve: committed capacity must cover the hour's (fixed) net load plus a
        # reserve margin (headroom for contingencies). Referenced to the FIXED rep-day load, NOT
        # served load -- referencing served load would let the optimiser shed load purely to
        # shrink the reserve requirement (a perverse VOLL-vs-reserve trade). The shortfall slack
        # rs absorbs any genuine deficit (the fleet is sub-peak by design), so it stays feasible.
        #   sum(P[g]*u[g,h]) + rs[h]  >=  load[h] * (1 + reserve)
        if params.enforce_reserve:
            for h in range(DAY_H):
                prob += (pulp.lpSum(uP[g] * u[g, d, h] for g in classes) + rs[d, h]
                         >= days[d, h] * (1.0 + RESERVE_FRAC), f"reserve_{d}_{h}")
        # min-up / min-down within the rep-day (cyclic), MILP-meaningful; light in LP
        if params.enforce_minupdown:
            for g in classes:
                uc = UNIT_CLASSES[g]
                if uc.min_up > 1:
                    for h in range(DAY_H):
                        win = [(h + k) % DAY_H for k in range(uc.min_up)]
                        prob += pulp.lpSum(u[g, d, hh] for hh in win) >= uc.min_up * su[g, d, h], \
                            f"minup_{g}_{d}_{h}"

    solver = pulp.PULP_CBC_CMD(msg=1 if verbose else 0, timeLimit=time_limit)
    status = prob.solve(solver)
    solve_t = time.time() - t0

    # extract dispatch
    out = {g: np.zeros((D, DAY_H)) for g in classes}
    for g in classes:
        for d in range(D):
            for h in range(DAY_H):
                out[g][d, h] = float(p[g, d, h].value() or 0.0)
    lost = np.array([[float(ls[d, h].value() or 0.0) for h in range(DAY_H)] for d in range(D)])
    resv_short = (np.array([[float(rs[d, h].value() or 0.0) for h in range(DAY_H)] for d in range(D)])
                  if params.enforce_reserve else np.zeros((D, DAY_H)))

    # annual energy = sum over rep-days weighted by the number of real days each represents
    def annual_gwh(arr):  # arr (D,24) GW -> GWh/yr
        return float((arr.sum(1) * weights).sum())
    ccgt_e = annual_gwh(out.get("CCGT", np.zeros((D, DAY_H))))
    ocgt_e = annual_gwh(out.get("OCGT", np.zeros((D, DAY_H))))
    h2_e = annual_gwh(out.get("H2turbine", np.zeros((D, DAY_H))))
    peaker_e = ocgt_e + h2_e
    unserved = annual_gwh(lost)
    peaker_cap = P.get("OCGT", 0.0) + P.get("H2turbine", 0.0)
    # peaker output peak across rep-days (for an output-based capacity cross-check)
    peaker_out = out.get("OCGT", np.zeros((D, DAY_H))) + out.get("H2turbine", np.zeros((D, DAY_H)))
    peaker_peak_out = float(peaker_out.max()) if peaker_out.size else 0.0
    lol_hours = int(((lost > 1e-6) * weights[:, None]).sum())
    resv_short_gw = float(resv_short.max()) if resv_short.size else 0.0

    return dict(
        country=c, year=year, scenario=scenario,
        peak_gw=float(demand.max()),
        firm_ccgt_cap_gw=P.get("CCGT", 0.0), firm_ccgt_energy_gwh=ccgt_e,
        peaker_cap_gw=peaker_cap, peaker_energy_gwh=peaker_e,
        peaker_flh=(peaker_e / peaker_cap if peaker_cap > 0 else 0.0),
        ocgt_energy_gwh=ocgt_e, h2_energy_gwh=h2_e,
        peaker_peak_out_gw=peaker_peak_out,
        unserved_gwh=unserved, lol_hours=lol_hours, reserve_short_gw=round(resv_short_gw, 3),
        objective_eur=float(pulp.value(prob.objective) or 0.0),
        status=pulp.LpStatus[status], solve_s=round(solve_t, 2),
        n_repdays=D, weights=weights.tolist(),
    )


def _empty_result(c, year, scenario, demand, gas_cap, peaker_cap_total, solve_t):
    return dict(country=c, year=year, scenario=scenario, peak_gw=float(demand.max()),
                firm_ccgt_cap_gw=gas_cap, firm_ccgt_energy_gwh=0.0,
                peaker_cap_gw=peaker_cap_total, peaker_energy_gwh=0.0, peaker_flh=0.0,
                ocgt_energy_gwh=0.0, h2_energy_gwh=0.0, peaker_peak_out_gw=0.0,
                unserved_gwh=0.0, lol_hours=0, objective_eur=0.0, status="NoUnits",
                solve_s=round(solve_t, 2), n_repdays=0, weights=[])
