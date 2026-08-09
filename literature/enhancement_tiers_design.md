# Enhancement tiers — implementation designs (T3-retrofit, T4-cohorts, T5, T6)

The model is validated and accuracy-complete (19/29 countries within +/-15% of Hotmaps, 28/29 within +/-25%; MT the
lone documented exception; EU LMDI design backcast -1.0% vs Hotmaps). The four items below
are *enhancements* (rigour/realism), not fixes. Each is specified here to a
shovel-ready level -- formulation, sourced data, files to touch, validation,
effort/risk -- so it can be built cleanly as a focused unit rather than rushed
into the core. None is required for the modelling to be sound.

---

## T3 - Endogenous renovation depth in COST_OPT

**Why.** COST_OPT currently fixes demand at the REF LMDI trajectory; it optimises
the *supply* mix only. Endogenising retrofit lets the LP trade renovation CAPEX
against supply-side switching (the standard cost-optimal-buildings question).

**Formulation (linear; avoid the bilinear share x retrofit trap).** Re-cast
COST_OPT in ABSOLUTE MWh rather than shares, OR add retrofit as a separate
demand-reduction variable:
- `retro[c,y] in [0, RETRO_MAX * demand[c,y]]`  (MWh of useful heat avoided)
- served demand `D'[c,y] = demand[c,y] - retro[c,y]`
- supply variables `q[c,t,y] >= 0`, balance `sum_t q[c,t,y] = D'[c,y]`
- objective adds `c_retro[c,y] * retro[c,y]`; cap uses `sum_t ef*q` (retro EF=0)
Keep it as a NEW function `solve_with_retrofit(...)` (do not modify the validated
`solve()`); compare fixed-demand vs endogenous-retrofit as a variant.

**Sourced cost curve (Ipsos/Navigant 2019, Table 11 / p.80).** EUR/m2 by depth
with the achieved primary-energy saving. Converted to EUR/MWh_useful saved at a
~150 kWh/m2.yr baseline intensity, CRF 5%/30yr (~0.065):

| Depth | EUR/m2 | saving | heat saved (kWh/m2.yr) | EUR/MWh_saved |
|---|--:|--:|--:|--:|
| Light | 104 | ~13% | ~20 | ~349 |
| Medium | 154 | ~41% | ~62 | ~163 |
| Deep | 219 | ~66% | ~99 | ~144 |

Retrofit is generally pricier per MWh than heat pumps (~70-100), so the LP will
pick little retrofit at -90% and more only at -100% / where supply abatement is
exhausted -- the expected, defensible result. Use a per-country baseline
intensity (from the bottom-up build) to make c_retro country-specific.

**Files:** `Optimisation.py` (new `solve_with_retrofit`, RETRO_MAX + cost curve
constants), `scripts/cost_opt_retrofit.py` (run + compare), paper paragraph.
**Validation:** LP solves Optimal; retrofit share ~0 at -90%, rising at -100%;
PV-cost delta vs fixed-demand reported. **Effort:** ~1 day. **Risk:** medium
(new LP; isolate from `solve()`).

---

## T4 - Vintage-cohort turnover forward

**Why.** The forward uses a single aggregate envelope-decline rate
`(1-r)^(t-2025)`. A cohort model tracks the stock by vintage with explicit
demolition / new-build / retrofit flows, so the intensity path is an emergent
weighted average rather than an assumed exponential.

**Formulation.** Carry the per-(class,cohort) floor area `A[c,k,t]` forward:
- demolition: `A[c,k,t+1] = A[c,k,t] * (1 - demo_rate)`
- new build: add `A_new[c,t]` at the prevailing new-build standard intensity
  (EPBD nZEB from 2030)
- retrofit: move a fraction `renov_rate[c]` of each cohort from its existing
  intensity to the retrofitted intensity (TABULA standard/deep states already in
  the *_intensities.csv files)
- demand `D[c,t] = sum_{k} A[c,k,t] * intensity[c,k,state]`

**Data:** demolition ~0.1-0.2%/yr (BPIE), new-build rate from dwelling-stock
growth (already have population/occupancy), renovation rate per country (BPIE /
Ipsos cross-section, already sourced), new-build intensity = TABULA post-2020 /
nZEB rows. **Files:** `Config.forward_demand_ratio` -> a cohort-stock module;
`Simulation` forward loop. **Validation:** reproduce the current -9% REF as a
limiting case (single-rate ~ aggregate of cohort flows); per-cohort area sums
conserved. **Effort:** ~2-3 days. **Risk:** high (replaces the validated forward;
keep the LMDI forward as the default, cohort as an alternative `forward_mode`).

---

## T5 - Global sensitivity + second independent benchmark

**(a) Global sensitivity.** Replace the one-at-a-time tornado with a Morris
elementary-effects screen (cheaper than Sobol) over the axes: carbon-price
scenario, H2 trajectory, discount rate, ETS2 pass-through, INTENSITY_RATE_CORR,
FUEL_PRICE_CORR, per-scenario envelope rate. Use SALib (`morris.sample` /
`morris.analyze`). The full NUTS3 MC is ~2 min/run, so a Morris screen
(~10 trajectories x (k+1) runs) is ~hours -- run on a reduced sample (e.g.
N_MONTE_CARLO_SAMPLES=20 inside each evaluation) or a country-aggregated
surrogate. Output: ranked mu*/sigma per axis on 2030 CO2 and 2050 demand.
**Files:** `scripts/global_sensitivity.py` (additive; no core change).
**Effort:** ~1-2 days (compute-bound). **Risk:** low (standalone).

**(b) Second benchmark.** Compare the bottom-up per-country residential useful
heat to **JRC-IDEES** (residential space-heat + water-heat useful energy;
the JRC Integrated Database of the European Energy System) -- an orthogonal
benchmark to Hotmaps. IDEES is USEFUL energy (matches the model), unlike Eurostat
nrg_d_hhq (final). **Data:** JRC-IDEES residential module (publications.jrc.ec).
**Files:** `scripts/benchmark_idees.py` + a comparison table. **Effort:** ~0.5
day once IDEES is downloaded. **Risk:** low.

---

## T6 - Per-NUTS3 feasibility (and the region-split limit)

**Region-split does NOT generalise.** HR worked because Croatia has *no* national
TABULA (an IT/SI neighbour split was the proxy). All 29 countries now have a
TABULA source, and ES/FR/IT use their *own* national typology -- a single file
that carries no sub-national climate-zone intensity variation. "Region-splitting"
them would need sub-national TABULA intensities that do not exist in the source,
so it is not a clean transfer. (If desired, the right move is per-NUTS3 HDD
scaling of the national intensities -- a climate multiplier that varies by NUTS3
rather than one national value -- which is a smaller, separate change.)

**The real T6 item: per-NUTS3 HP/DH feasibility.** Feasibility scores are
currently ~uniform (~0.67), which is why the RQ1 "low heat-pump feasibility"
condition is inert and why COST_OPT's HP/DH caps are country-mean. Make them
NUTS3-resolved from observable proxies:
- HP feasibility: dwelling type mix (SFH vs MFH share, already in the stock) +
  urban density (EUBUCCO footprint density) -- MFH-dense urban NUTS3 score lower.
- DH feasibility: heat-density (MWh/km2 from the bottom-up demand + area) -- the
  standard Hotmaps district-heating-potential criterion (>~ 50-120 TJ/km2).
**Data:** already in the build (per-NUTS3 demand, area, class mix); the Hotmaps
DH-density thresholds are published. **Files:** `BuildingStock.build_hp_dh_
feasibility` (NUTS3 scoring), then it flows into the MC + COST_OPT caps.
**Validation:** re-reconcile; the RQ1 conditions analysis gains a real feasibility
axis. **Effort:** ~1-2 days. **Risk:** medium (changes feasibility inputs to MC +
COST_OPT; re-runs needed).

---

## Recommended execution order

1. **T5(b)** second benchmark -- fastest, pure validation, no model change.
2. **T6** per-NUTS3 feasibility -- unlocks an inert RQ1 axis; data already present.
3. **T3** endogenous-retrofit LP -- isolated variant; sourced; high paper value.
4. **T5(a)** global sensitivity -- compute-bound; run when the above are stable.
5. **T4** vintage cohorts -- largest; do last, as an alternative forward mode.

Each needs its own verification (and T6 needs a Colab re-reconciliation). None
should be merged into the validated default paths until individually validated.
