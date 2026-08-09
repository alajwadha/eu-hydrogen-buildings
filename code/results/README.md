# Results index — EU+UK+CH residential heating model

All CSVs in this folder are produced by the pipeline in `code/` (one-command rebuild:
`cd code && PYTHONPATH=. python -m scripts.rebuild_local`). Scenario set (June 2026
multi-lever design): **CURRENT_POLICIES, STATED_POLICIES, NET_ZERO, H2_PUSH** plus the
**COST_OPT** least-cost LP variants (75/90/100% scope-1 caps).

Headline 2050 (q50): CO2 352 / 231 / 10 / 123 Mt (CURRENT / STATED / NET_ZERO / H2_PUSH)
from a ~644 Mt 2025 baseline. Base load: the best heat pump is cheaper than the hydrogen
boiler in **22 of 29** countries at a median gap of +15.4 EUR/MWh (medians 118.5 best HP /
122.8 H2 / 132.7 gas / 96.5 district heat); hydrogen holds the other seven (BE, DE, DK, IE,
NL, PL, UK), five of them salt-cavern markets. COST_OPT: present-value system cost
7,426.3 / 7,428.4 / 7,429.8 bn EUR-yr at the 75/90/100% caps; the scope-1 cap binds in
**4 of 29** countries in 2050 (CY, HR, PL, UK) at up to **81 EUR/tCO2**, and in 7 along
the path (adding ES, HU, RO). Power arena: a 278 GW firm peaker fleet, 31% of an 889 GW
study-area peak, supplying 0.86% of 4,513 TWh at ~139 full-load hours, recovering ~9%
of capital on a capacity-weighted basis across the cavern markets that build. A
partially flexible heat-pump load lowers the fleet by at most 10.7%
(`hp_flexibility_bound.csv`).

## Files

| Group | Files | Producer |
|---|---|---|
| Monte Carlo (per scenario) | `mc_summary_*`, `mc_emissions_*`, `mc_country_*` | `src.Simulation` |
| Least-cost LP | `mc_*_COST_OPT_*`, `cost_opt_pathway`, `cost_opt_shadow_prices`, `cost_opt_sensitivity`, `cost_opt_retrofit` | `src.Optimisation` (+ sweep script) |
| Merit order / peaking | `heat_load_profile`, `power_peak_price`, `merit_order_heat`, `merit_order_profit`, `merit_order_dh` | `scripts.heat_load_profile` → `power_peak_price` → `merit_order_*` |
| Networks / infrastructure | `infrastructure_bill`, `elec_reinforcement_sensitivity`, `h2_infra_scenario` | `scripts.infrastructure_bill` etc. |
| H2 supply | `h2_delivered_cost`, `h2_supply_scenario`, `h2_hp_gap` | `scripts.h2_*` |
| Country economics | `country_econ_table` | `scripts.country_econ_table` |
| Sensitivities | `grid_sensitivity*`, `rho_sensitivity`, `climate_hdd_sensitivity`, `global_sensitivity` | `scripts.*_sensitivity` |
| Validation / demand | `benchmark_multi`, `lmdi_*`, `cohort_forward`, `reconcile_backcast`, `compare_naked` | demand-side scripts |

MC files report q10 / q50 / q90 across 200 Monte Carlo draws. `mc_country_*` covers all
29 countries. (Runs made before June 2026 wrote only the top-15 heat markets; if a file
in this folder carries fewer than 29 country codes it predates that change and should be
regenerated before use.)

Deprecated-scenario outputs (`*_REF`, `*_HIGH_HP`, `*_H2_HYBRID`) were removed June 2026;
any reference to them is stale.
