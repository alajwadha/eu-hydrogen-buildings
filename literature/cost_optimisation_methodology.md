# COST_OPT — Least-Cost Decarbonisation Pathway (methodology)

**Module:** `code/src/Optimisation.py`  ·  **Added:** 2026-05-25  ·  **Solver:** PuLP + CBC

> **Withdrawn scenarios.** `REF`, `HIGH_HP` and `H2_HYBRID` were withdrawn in June 2026
> and must not be used for any new result. They are named below only to describe how
> COST_OPT differs from an exogenous-share scenario. The current four are
> `CURRENT_POLICIES`, `STATED_POLICIES`, `NET_ZERO` and `H2_PUSH`.

COST_OPT is the fourth scenario. Where REF / HIGH_HP / H2_HYBRID impose *exogenous* 2050
technology shares, COST_OPT *solves* for the least-cost mix of heating technologies, per
country and milestone year, subject to an emissions glide path and physical/policy limits.
It reuses the audited techno-economics (Economics.py `compute_lcoh`, which already bundles
annualised CAPEX + FOM + VOM + fuel + the ETS2 carbon adder) and the country/year emission
factors (Emissions.py). The LP only *allocates* demand; it does not re-derive any cost.

## 1. Formulation

**Decision variable** `x[c,t,y] ∈ [0,1]` — share of country *c*'s useful heat met by
technology *t* in milestone year *y* (y ∈ {2025, 2030, 2040, 2050}). The model is solved at
country level (not NUTS3): the cost-optimal EU pathway is naturally a country/EU-level
object, the LP stays small, and NUTS3 detail enters as demand-weighted country ceilings.

**Objective** — minimise the discounted, period-weighted system cost of the pathway:

```
min  Σ_{c,t,y}  w[y] · (1+r)^-(y-2025) · LCOH[c,t,y] · demand[c,y] · x[c,t,y]
```

`LCOH` is EUR/MWh_useful; `demand[c,y]` is country useful heat (MWh); `w[y]` is the
representative-period length of each milestone {2025:5, 2030:10, 2040:10, 2050:10 yr};
`r` = 5% real (Economics.DISCOUNT_RATE_REAL). This is the discounted stream of annual
heating cost along the milestone path.

**Constraints**

| # | Constraint | Form |
|---|---|---|
| 1 | Demand balance | Σ_t x[c,t,y] = 1 |
| 2 | 2025 anchor (trajectory mode) | x[c,t,2025] = START_MIX[t] |
| 3 | Feasibility (y>2025) | DH ≤ dh_cap[c]; GSHP ≤ gshp_cap[c]; HP_air+HP_ground ≤ hp_cap[c]; H2 ≤ H2_CAP[y]; biomass ≤ 0.20 |
| 4 | Boiler ban | gas+oil ≤ fossil_ceiling(c,y) from Policy.BOILER_BANS (20-yr phase-out after ban year) |
| 5 | Stock turnover (trajectory) | \|x[c,t,y] − x[c,t,y−1]\| ≤ 0.05·Δyears |
| 6 | Emissions cap | Σ_t x·scope1_ef·demand ≤ cap[c,y], **per country** |

**Why a per-country, scope-1 cap.** Each country must meet the target from its **own** 2025
scope-1 baseline, so every country gets a real cost-optimal decarbonisation pathway,
consistent with the project's country-by-country design. (An EU-aggregate cap would let
cheap-abatement countries over-deliver while others free-ride, hiding which countries
actually need a policy push.) With a per-country cap the cap's shadow price varies by
country: it is the implied carbon price *that country* needs to hit the target, written to
`cost_opt_shadow_prices.csv`. The cap is on **scope-1 (on-site gas/oil combustion)** following
the EPBD "zero-emission building" definition: electricity-grid and district-heat
decarbonisation are *exogenous* (Policy.py / Economics.py), so capping them here would
double-count grid policy and make a −100% (net-zero on-site) target artificially infeasible.
The **reported** emissions output still includes scope-2 grid/DH emissions.

## 2. Central assumptions (documented in `Optimisation.py`)

| Assumption | Value | Basis |
|---|---|---|
| 2025 starting mix | **per country** (heating_mix_2025.csv) | Eurostat nrg_d_hhq + national/EHPA, mean of bases; each country anchored to its actual mix. See heating_mix_2025_audit.md |
| Demand reduction by 2050 | **per country** ~25–43% | clip(0.20 + 0.15·renovation_rate); higher-renovation countries cut more |
| Biomass ceiling | **per country** ~0.02–0.40 | sustainable domestic biomass (forest-rich Nordic/Baltic high; islands ~0) |
| H2-for-buildings ceiling 2050 | **per country** (mostly 0; NL 0.03, UK 0.02) | building H2 is a niche; only NL/UK have/had pilots |
| Stock turnover | **per country** ~4.5–6.5%/yr | clip(0.045 + 0.015·renovation_rate); ~20-yr lifetime |
| GSHP ceiling | 60% of single-family demand | GSHP needs outdoor space for ground loops |
| Feasibility (HP/DH) caps | demand-weighted country averages | from the hp_dh_feasibility layer |

A safeguard lets a country that already exceeds a cap (e.g. DK 66% district heat, BG 52%
biomass) keep that existing stock and decay it toward the cap no faster than turnover allows,
so a high 2025 share never makes the LP infeasible.

## 3. Variants

Three emissions-ambition variants by 2050 vs **each country's** 2025 scope-1 baseline
(~522 MtCO2 EU total on the full 29-country EU27+CH+UK bottom-up build, with the per-country
2025 mix): **COST_OPT_75**
(−75%), **COST_OPT_90** (−90%), **COST_OPT_100** (−100%, net-zero on-site fossil). Two modes:
**trajectory** (perfect foresight + turnover, primary) and **snapshot** (each year
independent — a diagnostic for the cost of stock lock-in). Outputs use the standard
`mc_*_{tag}.csv` shape so they slot into the dashboard/figures, plus a tidy
`cost_opt_pathway.csv` and the per-country implied carbon prices in
`cost_opt_shadow_prices.csv`.

## 4. Headline results (29-country build, central inputs)

- **Most countries decarbonise on their own; a few need a carbon-price push.** With the
  DEA-correct techno-economics and ETS2 inside LCOH, heat pumps are the cheapest option in
  most countries. SUPERSEDED (June 2026, post GSHP-ceiling fix 0.60->0.15): the caps now bind in 0/29 countries at EUR 0 implied carbon price in every variant; the historical 2/29 text below is retained for provenance. Originally: all three caps bind in only **2/29 countries — CZ (~€86/tCO2 in 2050,
  plus ~€8 in 2040) and PL (~€57)** — where high starting fossil shares and a slower turnover
  path keep the **intermediate-year** scope-1 trajectory above the cap even though the 2050
  endpoint mix resembles the unconstrained optimum. (A transient ~€1,967 spike appears for MT
  in 2030: a degenerate artefact of MT's tiny absolute scope-1 baseline, excluded from the
  binding count.) Those per-country implied carbon prices are the headline policy result
  (full table in `cost_opt_shadow_prices.csv`).
- **2050 EU mix (≈ across variants):** heat pumps ~73% (air ~38% + ground ~35%), district
  heat ~26%, hydrogen and residual fossil each <1% (hydrogen is priced out by the cheaper
  HP/DH, NOT at its availability ceiling), biomass/resistance ~0. Per-country mixes differ
  markedly with feasibility (e.g. DE: DH ~49% + GSHP ~37%; PL: HP ~76% + DH ~14%).
- **Total CO2 (scope 1+2), COST_OPT_90:** ≈ 644 → 316 → 75 → 22 MtCO2 (2025→2050).
- **Lock-in cost:** the snapshot optimum (PV ≈ 8,013 bn EUR-yr) is ~€1,545 bn cheaper than the
  realistic trajectory (PV ≈ 9,558 bn EUR-yr), quantifying the cost of the stock-turnover
  constraint. The cap adds little: PV is ≈9,558 bn at −75/−90/−100% alike, because with a
  near-zero exogenous 2050 grid the cap is met mainly by removing on-site fossil.

## 5. Caveats and sensitivities (flagged for the paper)

- **GSHP share is feasibility-bound.** Cost-minimisation favours ground-source HPs (higher
  COP → lower LCOH), so they run up to `gshp_cap` (~34% of EU heat). Real GSHP deployment is
  a minority of HP sales (~10%); the `GSHP_SFH_FRACTION = 0.60` ceiling is the binding
  assumption here and is a first-order sensitivity to report.
- **Hydrogen is priced out, not capped.** With the DEA-audited costs and CENTRAL H2 prices
  the LP picks essentially no hydrogen (<1%); it does not reach its 10% availability ceiling,
  consistent with the audit's counter-consensus on building hydrogen.
- **Demand is fixed at the REF LMDI trajectory** (central per-country envelope rate; EU −9.3%
  by 2050) and identical across targets — the LP optimises the supply mix at a given demand
  path and does not co-optimise renovation depth against supply-side switching. Its 2050 EU
  demand (~3,480 TWh) therefore tracks REF rather than the deeper-renovation scenarios.
- **Emissions cap is scope-1 (on-site) only**, with an exogenous near-zero 2050 grid, so the
  −100% target means net-zero on-site combustion rather than economy-wide net-zero; this is
  why the cap binds in only two countries and costs little.
- **Run covers the full 29 countries** (EU27 + CH + UK) as of 2026-05-26, after the FR/FI/LU
  Colab builds landed (FR commit 8189f02).
- Cost inputs reflect the 2026-05-25 source audit (see
  [scenario_assumptions_audit.md](scenario_assumptions_audit.md) §5.1).

## 6. How to run

```
python run.py --scenario COST_OPT --demand bottomup --skip-download
# or all four scenarios:  --scenario ALL+COST_OPT
# or the module directly: python code/src/Optimisation.py --demand bottomup
#   options: --mode trajectory|snapshot   --targets 75,90,100   --no-snapshot
```
VS Code task: **"🎯 Run COST_OPT (least-cost LP, BOTTOM-UP demand)"**.
