# Reproducing the Applied Energy submission

This guide maps each headline result in the manuscript (`V5.tex`) and the
Supplementary Information (`SI.tex`) to the script that produces it, so a reader can
regenerate the numbers from the public repository. It supersedes the top-level
`README.md` where they differ: the submitted paper uses the four policy scenarios
**`CURRENT_POLICIES`, `STATED_POLICIES`, `NET_ZERO`, `H2_PUSH`** (Current Policies,
Stated Policies, Net Zero, H2 Push), not the earlier three-scenario naming.

## Setup

```bash
git clone https://github.com/alajwadha/EU-Building-Heat-Model.git
cd EU-Building-Heat-Model
pip install -r requirements.txt          # Python 3.10+; installs scipy, SALib, pulp
```

The processed inputs the analyses below need (`code/data/processed/`,
`code/results/`) are committed, so these run on a fresh clone without the raw
download. To rebuild the raw inputs from source, run `python code/scripts/download_data.py`
(Hotmaps, Eurostat, GISCO, UK ONS).

All commands are run from the `code/` directory with the package on the path:

```bash
cd code
export PYTHONPATH=.
```

## Headline numbers → scripts

**The table is in run order.** Two modules are prerequisites that fail silently rather
than loudly if their input is missing: `scripts.heat_load_profile` writes the seasonal
shift fraction that every hydrogen LCOH is priced on, and `Economics` falls back to a
flat 0.25 without it; `scripts.power_peak_price` writes the endogenous winter-peak
price, and `scripts.merit_order_heat` falls back to hard-coded constants without it.
Working the table top to bottom from a cleared `code/results/` does NOT avoid them, and an earlier version of this note said it did. Two rows are out of dependency order: `scripts.benchmark_multi` must run first because `scripts.heat_load_profile` reads `benchmark_multi.csv` unguarded, and `scripts.heat_load_profile` must precede `src.Simulation` because `compute_lcoh` reads the seasonal shift fraction it writes. Run `python -m scripts.rebuild_local`, which now chains all of this in order, or run those two rows before the Monte Carlo. Running a
single row in isolation does not, so run the two prerequisite rows first. The one-command
alternative, `python -m scripts.rebuild_local`, chains the same modules in the same order.

| Manuscript claim | Command | Output |
|---|---|---|
| Bottom-up validation against Hotmaps: EU raw deviation -0.8%, vintage-matched -8.3%. On the raw basis 19 of 29 countries sit
within +/-15% and 28 of 29 within +/-25% (Malta the sole exception); on the
vintage-matched basis those counts are 18 and 25, with the UK, Luxembourg, Estonia and
the Netherlands outside +/-25%. These are the validation figures the manuscripts quote | `python -m scripts.make_validation_table` | `results/bottomup_validation.csv` |
| Country-level validation error dispersion. Raw basis: MAPE 11.6%, demand-weighted MAPE 9.8%, RMSE 14.4 pp, median absolute error 8.5%. Vintage-matched basis: 12.4, 10.7, 15.2 and 9.6. The counts and the -0.8% aggregate above are raw-basis quantities, so a vintage-matched dispersion figure does not belong beside them | `python -m scripts.make_validation_table` | `results/bottomup_validation_metrics.csv` |
| Firm peaking fleet on each scenario's own 2050 demand path: 242, 278, 270 and 264 GW at 131 to 148 full-load hours, same supply stack and weather year. A demand-path sensitivity, not four scenario power systems. The Stated Policies row reproduces the committed 277.7 GW, which is the module's own self-check | `python -m scripts.power_demand_path_sensitivity` | `results/power_demand_path.csv` |
| Monte Carlo convergence at N = 200. The running median of the 2050 CO2 metric last leaves a +/-1% tube at draw 41, 48, 96 and 139 across the four scenarios; the running 10th percentile only at 156 to 188, so medians are read as converged and deciles as indicative. Last exit, not first entry | `python -m scripts.mc_convergence` | `results/mc_convergence.csv`, `paper/figs/paper/P42_mc_convergence.{png,pdf}` |
| 2050 heating mix and residential CO2 by scenario (≈644 Mt 2025 baseline common to all four; 352/231/10/123 Mt in 2050); LCOH ordering | `python -m src.Simulation --scenario <NAME> --demand bottomup` for each of the four scenario names | `results/mc_summary_*.csv`, `results/mc_country_*.csv` |

The two flags matter. `--demand bottomup` selects the 29-country EUBUCCO/TABULA
reconstruction the manuscript reports; the default (`hotmaps`, the 2015 top-down
regional surface) is the reconciliation benchmark described in the Methods and anchors
2025 demand about 1 % higher, so it returns a different set of figures. `--scenario`
runs one scenario at a time and defaults to `STATED_POLICIES`; the carbon and hydrogen
paths come from each scenario's own configuration, so `--carbon` and `--h2` do not need
setting. To regenerate all four:

```bash
for s in CURRENT_POLICIES STATED_POLICIES NET_ZERO H2_PUSH; do
    python -m src.Simulation --scenario "$s" --demand bottomup
done
```
| Manuscript claim | Command | Output |
|---|---|---|
| Country heat-load profiles and the seasonal shift fraction (median 0.248, range 0.210 to 0.290). Run this before anything that prices the seasonal store, or `Economics` silently falls back to a flat 0.25 | `python -m scripts.heat_load_profile` | `results/heat_load_profile.csv` |
| Endogenous winter-peak electricity price; the seven salt-cavern power-arena wins | `python -m scripts.power_peak_price` | `results/power_peak_price.csv` |
| Delivered hydrogen cost by country and route | `python -m scripts.h2_delivered_cost` | `results/h2_delivered_cost.csv` |
| Base-load LCOH, heat pumps win 22 of 29 (2050); medians 118.5 best HP / 122.8 H2 / 132.7 gas EUR/MWh | `python -m scripts.h2_gap_analysis` | `results/h2_hp_gap.csv` |
| Three cost terms are ON in the baseline and set the base-load result: `compute_lcoh` defaults are `h2_infra="blend"`, `h2_infra_bound="central"` (hydrogen last-mile network), `elec_reinforce=True`, `elec_reinforce_bound="central"` (LV/MV reinforcement for the heat-pump winter peak), and `h2_seasonal_storage=True` (the store the seasonal heating load requires, charged on each country's own load-derived shift fraction). Every base-load count above assumes all three, so a reader who omits any of them reproduces a different number set. Turning off the storage term alone gives 12 of 29 for heat pumps; the load-derived fraction gives 22; charging the full seasonal adder gives 29. Turning off all three together (`h2_infra=False, elec_reinforce=False, h2_seasonal_storage=False`) is a different case again and gives 5 of 29 at a median gap of -16.5 EUR/MWh | `python -m scripts.h2_infra_scenario`, `python -m scripts.elec_reinforcement_sensitivity` | `results/h2_infra_scenario.csv`, `results/elec_reinforcement_sensitivity.csv` |
| Building-level peak win counts. The module prints 0/4/9/16, which charges hydrogen no last-mile network; the manuscripts headline the symmetric 0/2/7/14, which charges it the same blended adder the base-load comparison uses. Both bases, and their demand-weighted ceilings, are in `results/dispatch_arena_sensitivity.csv` under the `h2_last_mile` axis. Merit-order bound on the hydrogen ceiling. Run `scripts.power_peak_price` first, or this module silently falls back to hard-coded peak-price constants | `python -m scripts.merit_order_heat` | `results/merit_order_heat.csv` |
| District-heat peak win counts. The module prints 0/5/11/20, which prices the competing gas unit at the residential retail tariff; the manuscripts headline the symmetric 0/0/7/7, which prices it at the EUR 30/MWh wholesale hub an operator actually pays (`dispatch_arena_sensitivity.csv`, `dh_gas_basis` axis) | `python -m scripts.merit_order_dh` | `results/merit_order_dh.csv` |
| Peaker capital recovery for the 278 GW firm fleet (Stated Policies dispatch, 2050, priced under each scenario's fuel and carbon paths), 31% of an 889 GW study-area peak while supplying 0.86% of 4,513 TWh at ~139 full-load hours; €357 bn vs €142 bn cumulative shortfall, an undiscounted 25-year sum | `python -m scripts.power_dispatch` | Fleet, peak, share and full-load hours: `results/power_dispatch_summary.csv`, summing `peaker_cap_gw`, `peak_gw` and `peaker_energy_gwh` over the `basis=total_elec`, `year=2050` rows (277.66 GW, 888.84 GW, 31.24%, 139.33 h; 38.69 TWh against the 4,513 TWh denominator, now written to `results/power_demand_denominator.csv` so it is checkable; both the fleet and that denominator are on the Stated Policies dispatch). Recovery path: `results/power_peaker_recovery_projection.csv`. Cumulative shortfall: `results/power_peaker_economics.csv`, summing `cum_h2_profit_meur` and `cum_gas_profit_meur` at 2050 |
| Peaker capital recovery ≈9% capacity-weighted across the cavern markets (H2 Push 2050), spanning 5 to 40% as run windows range from 48 to 343 h; per-market standing capacity payment ≈31 to 63 €/kW-yr (gas 41 to 52 in the same markets); technology neutrality, gas 45 vs H2 51 €/kW-yr capacity-weighted across the 5 of 7 markets that build (the Netherlands and Romania win on operating cost but need no peaker under the three-hour standard), gas cheaper in 4 of those 5 and across 96% of winning capacity, so a neutral auction procures gas; emissions-conditioning premium ≈172 €/tCO2 (≈239 with the gas rent floored at zero), the neutrality sign reversing only below ≈520 to 540 €/kW, about an 18% premium | `python -m scripts.capacity_payment` | Ranges and per-market payments: `results/capacity_payment.csv` (`recovery_h2_pct`, `peaker_flh`, `standing_payment_h2`, `standing_payment_gas`; the capacity-weighted figures weight by `peaker_cap_gw` over the 5 rows with `peaker_cap_gw > 0`). The conditioning premium, the ≈520 to 540 €/kW reversal and the 96% capacity share are printed by the run and carried in no column; `scripts.check_manuscript_numbers` re-runs the module and reads them off its console output so a stale figure fails the gate |
| Unit-commitment cross-check: agrees with the reduced-form merit order to within 0.33% on dispatched energy and 0.40% on peak capacity, at an LP-vs-MILP integrality gap of 0.038 to 0.110% on the five countries spot-checked | `python -m scripts.power_uc` | `results/power_uc_summary.csv`, `results/power_uc_limit_validation.csv` |
| Joint storage-adder × scarcity-premium sweep; the count holds at seven across storage
adders of €50 to 75/MWh-heat and at every scarcity premium, and not outside that window
(SI Table S14) | `python -m scripts.cavern_two_way_sweep` | `results/cavern_two_way_sweep.csv` |
| Firm-capacity requirement under a partially flexible heat-pump load, across three energy-conserving smoothing operators (symmetric, one-sided pre-heat, capped finite store). Shifting 10 to 30% of the heat-pump load across a 3 to 13 hour window takes the 277.7 GW fleet to between 277.1 and 248.0 GW, a reduction of at most 10.7% (SI Table S9) | `python -m scripts.hp_flexibility_bound` | `results/hp_flexibility_bound.csv` |
| Sensitivity of the firm-capacity requirement to the assumed length of the synthetic cold-and-still event. Sweeping it from 2 to 10 days moves the inflexible fleet from 253.7 to 302.0 GW, so the 277.7 GW headline carries about ±9% from this one assumption, while the flexibility reduction stays nearly flat at 8.9 to 11.6% (SI Table S10) | `python -m scripts.cold_snap_duration_sweep` | `results/cold_snap_duration_sweep.csv` |
| Hydrogen peaker repriced at blue hydrogen (Dickel OIES, €81/MWh at the gate). Read as a European price the cavern win reverses in all seven, the turbine going to €289/MWh-e against the gas peaker's €256; read as a green-to-blue ratio the seven hold with the advantage falling from €72 to 89 to €30 to 57/MWh-e. The capital-recovery arithmetic is invariant either way, since a winner's rent is the scarcity premium times its run hours | `python -m scripts.blue_hydrogen_peaker` | `results/blue_hydrogen_peaker.csv` |
| Least-cost linear program: 2050 mix 53% district heat / 45% heat pumps / 0.34% hydrogen; present-value system cost 7,426.3 / 7,428.4 / 7,429.8 bn €-yr at the −75/−90/−100% scope-1 caps, a 0.05% cost of ambition; the cap binds in 4 of 29 countries in 2050 (CY, HR, PL, UK) at up to €81/tCO2 and in 7 along the path | `python -m src.Optimisation` | `results/cost_opt_pathway.csv`, `results/cost_opt_shadow_prices.csv`, `results/cost_opt_objective.csv` (one row per cap, carrying the present-value cost) |
| Cumulative 2025 to 2050 network-infrastructure bill, €249 / 325 / 506 / 412 bn across Current Policies, Stated Policies, Net Zero and H2 Push, over all 29 markets; the H2 Push split is €89 bn of electricity reinforcement against €74 bn of hydrogen network | `python -m scripts.infrastructure_bill` | `results/infrastructure_bill.csv` |
| District-heat last-mile connection charge, the largest unpriced network asymmetry left in the cost layer. District heat is the cheapest option in 26 of 29 countries as the model charges it (median 96.5 EUR/MWh); charging it the same EUR 5,000 per connection the infrastructure bill already assigns it, over 40 years at the country cost of capital, adds a median 21.0 EUR/MWh and leaves it cheapest in 7 of 29 | `python -m scripts.dh_connection_charge` | `results/dh_connection_charge.csv` |
| District-heat dispatch. Supporting analysis, not quoted in the manuscript: the hydrogen share of district heat runs to 66.6 TWh, 9.3% of EU district-heat energy in aggregate and 14.3% on the EU representative day | `python -m scripts.heat_dispatch` | `results/heat_dispatch_summary.csv` |
| Electrified-heat bridge. Supporting analysis, not quoted in the manuscript: 41% of H2 Push heat is direct-electric, 51% including electric district heat, and heating is 8.5% of power demand on this run's own denominator. The manuscript's 9.2% heating share is a different quantity, written by `scripts.power_dispatch` and read by `scripts.firm_capacity_attribution` (row below) | `python -m scripts.electrification_bridge` | `results/electrification_bridge.csv` |
| Per-country economic tables | `python -m scripts.country_econ_table` | `results/country_econ_table.csv` |
| Base-load count under each of the four hydrogen price paths: 13 rapid, 22 central, 26 slow, 29 stranded. Distinct from the supply-route sweep in the row below, which returns 15 / 22 / 26 on a different axis and shares two of its four values with this one | `python -m scripts.h2_price_path_counts` | `results/h2_price_path_counts.csv` |
| Firm-capacity attribution on three bases. Pro rata charges heating its 9.2% share of power demand at €1.0 to 1.3/MWh and leaves the count at 22; incremental charges the 79.6% of the fleet that exists because heat is electrified, at €8.9 to 11.5/MWh, taking it to 19 then 17; charging the whole fleet is €11.2 to 14.5/MWh and gives 17 then 15 | `python -m scripts.firm_capacity_attribution` | `results/firm_capacity_attribution.csv` |
| Dispatch-arena sensitivities: symmetric building-peak counts 0/2/7/14 with the hydrogen last mile charged, and symmetric district-heat counts 0/0/7/7 with gas at the wholesale hub; the Stated Policies ceiling of 0.6%; the cavern set widened to nine on Iberian storage and narrowed to six on French northern basins (SI Table S7) ; and the winning countries by name on each basis, so a country list in the prose can be checked and not only its count (Stated Policies is NL and DK on the symmetric basis, DE, FR, NL and DK on the asymmetric) | `python -m scripts.dispatch_arena_sensitivity` | `results/dispatch_arena_sensitivity.csv`, `results/building_peak_winners.csv` |
| Peak-arena wins and gross margins on the evolving-efficiency series, where the heat-side recovery aggregates to 20.3% over the winning country-scenario pairs. This file's own H2 Push win count is 16, the same as the merit order. The 15-market count is a different series, produced by the `scripts.power_dispatch` row above: it is where the hydrogen turbine undercuts gas on the 2050 operating cost in `power_peaker_economics.csv`, which lets both machines' efficiencies evolve, whereas the published merit order holds them equal | `python -m scripts.merit_order_profit` | `results/merit_order_profit.csv` |
| Blue hydrogen on **base load**, distinct from the peaker row above. A flat €81/MWh gate closes the lead in all seven; a green-to-blue ratio leaves Denmark holding | `python -m scripts.blue_hydrogen_peaker` | `results/blue_hydrogen_baseload.csv` |
| Islanded-versus-pooled firm requirement, 291/278/251 GW islanded against 267/239/205 GW on an EU copper plate across the wind-lull sweep | `python -m scripts.power_dispatch` | `results/power_dispatch_robustness.csv` |
| Seasonal-storage classification and the per-country storage adder (SI Table S8): €12.1/MWh in Germany on the cavern rate against €28.4 in Spain without | `python -m scripts.storage_geology` | `results/storage_geology.csv` |
| LMDI decomposition of the 2015→2025 demand change (+1.8% population, +4.6% occupancy, 0.0% dwelling size, −6.3% envelope intensity, net +0.1%) and the 26-country envelope term of −11.8%. The design backcast this produces lands −1.0% against the Hotmaps 2015 surface, which is a different basis from the −8.3% vintage-matched validation gap and from the −8.5% raw-Hotmaps reconciliation | `python -m scripts.lmdi_backcast && python -m scripts.lmdi_design` | `results/lmdi_decomposition.csv`, `results/lmdi_backcast.csv`, `results/lmdi_design.csv`, `results/lmdi_design_drivers.csv` |
| Frozen-grid counterfactual behind the emissions attribution: the Stated Policies 2025→2050 fall of 644.1 to 264.2 MtCO2 splits 62% technology switching and 38% grid and district-heat cleanness, against 407.3 Mt on a frozen grid. The 264.2 is this run's deterministic central trajectory, not the 231 MtCO2 Monte Carlo median the manuscript reports for the same scenario and year. Supporting analysis, not quoted in the manuscript | `python -m scripts.grid_sensitivity` | `results/grid_sensitivity.csv`, `results/grid_sensitivity_summary.csv` |
| Heating-degree-day overlay on 2050 demand: 3,483 TWh at the frozen 1991 to 2020 normal against 3,338 / 3,235 / 3,102 TWh under low, RCP4.5 and RCP8.5 warming. The manuscript quotes the RCP4.5 case as an approximately 15% deepening of the Stated Policies fall | `python -m scripts.climate_hdd_sensitivity` | `results/climate_hdd_sensitivity.csv` |
| Least-cost program variants: GSHP-fraction and biomass-cap sweeps, and a scope-2 cap that charges electrified heat for its power-sector emissions. The scope-2 run barely moves the mix (52.9% district heat, 45.6% heat pumps, 0.3% hydrogen, against 52.9 / 45.4 / 0.3 on the scope-1 baseline) at a present value of 7,429.0 bn against 7,428.4 bn, and a shadow price of €83/tCO2 against €81 | `python -m scripts.cost_opt_sensitivity` | `results/cost_opt_sensitivity.csv` |
| Least-cost program with envelope retrofit as a decision (SI Section S1.7): retrofit takes 2.79% of the stock at 2030 and 5.81% at 2040, falls to zero at 2050, and lowers the present value from 7,428.4 to 7,403.6 bn at the −90% cap | `python -m scripts.cost_opt_retrofit` | `results/cost_opt_retrofit.csv` |
| Correlation-structure sweep behind the EU demand band: band widths at ρ = 0, 0.5 and 1.0. Supporting analysis; the 1.7× and 2.7× widths the SI quotes at ρ = 0.25 and 0.75 are closed-form, not from this file | `python -m scripts.rho_sensitivity` | `results/rho_sensitivity.csv` |
| One-at-a-time tornado on the 2030 Stated Policies demand drivers, the deterministic companion to the Sobol screen. Supporting analysis, not quoted in the manuscript | `python -m scripts.tornado_oat` | `results/tornado_oat.csv` |
| Hydrogen supply-route scenarios | `python -m scripts.h2_supply_scenario` | `results/h2_supply_scenario.csv` |
| Switzerland, validation-limit arm (2050 HP 122.4 to 131.1 €/MWh, H2 boiler 128.0) and endogenous arm (HP 120.9 to 129.9, H2 boiler 130.6) | `python -m scripts.swiss_integration` | `results/swiss_integration.csv` |
| Base-year demand anchor rank-invariance (Eurostat vs Hotmaps; the 7 caverns unchanged) | `python -m scripts.eurostat_anchor_invariance` | `results/eurostat_anchor_invariance.csv` |
| Global economic sensitivity, fossil-phaseout ambition SRRC 0.98, every other axis <0.02 (SI Table S13, which the H2 Push run writes from the artefact as `si_body/_tab_sens_econ.tex`; all 17 sampled parameters appear, not a selection). Set `GSE_SCEN` to run each scenario; rank-R² is 0.930/0.942/0.432/0.949 across Current Policies, Stated Policies, Net Zero and H2 Push | `for s in CURRENT_POLICIES STATED_POLICIES NET_ZERO H2_PUSH; do GSE_SCEN=$s python -m scripts.global_sensitivity_econ; done` | `results/global_sensitivity_economics.csv`, `paper/ae_submission/si_body/_tab_sens_econ.tex` |
| Rank-R² of the economic sensitivity fit, by scenario (0.930 / 0.942 / 0.432 / 0.949). This used to survive only in prose and a figure title, because pandas discards `DataFrame.attrs` on write; it is now a committed column and its own summary CSV | `for s in CURRENT_POLICIES STATED_POLICIES NET_ZERO H2_PUSH; do GSE_SCEN=$s python -m scripts.global_sensitivity_econ; done` | `results/global_sensitivity_econ_r2.csv` |
| Demand-driver Sobol indices behind SI Fig. S3 | `python -m scripts.global_sensitivity` | `results/global_sensitivity.csv` |
| Demand-driver Sobol figure (SI Fig. S3) | `python -m scripts.fig_sobol_demand` | `paper/figs/paper/P40_sobol_demand.{png,pdf}` |
| Model architecture figure (Fig. 1) | `python -m scripts.fig_model_flow` | `paper/figs/paper/P00_model_flow.{png,pdf}` |

Each script prints its headline figures and writes a CSV under `code/results/`. The
cost-optimal least-cost program and the unit-commitment MILP cross-check
(`src.Optimisation`, `src.PowerUC`) both need the CBC solver bundled with `pulp`,
which `requirements.txt` installs; the reduced-form results above do not require it.

## Building the documents

```bash
cd paper/ae_submission
pdflatex V5.tex && bibtex V5 && pdflatex V5.tex && pdflatex V5.tex   # -> V5.pdf
pdflatex SI.tex   && bibtex SI   && pdflatex SI.tex   && pdflatex SI.tex     # -> SI.pdf
```

A no-LaTeX path (`python build.py`) renders Word and PDF twins via pandoc and
weasyprint; the canonical typeset PDFs come from the LaTeX build above.
