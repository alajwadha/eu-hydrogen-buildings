# Ireland (IE)

> **RQ relevance:** Highest petroleum products share in residential energy in EU (41.7%, Eurostat 2023). Boiler bans broadened to residential homes/gas in new buildings (EHPA 2025). HP sales grew 19% in 2024 — strong policy momentum. Long-term subsidy stability. New Warm Homes Plan from 2025.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €130/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €310/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 220 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 40% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.94 | Hotmaps HDD; EHPA |
| Annual heating hours | 1928/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2025 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2030 |


**Context:** Boiler ban broadened to residential homes and gas in new buildings (EHPA 2025). 41.7% of residential energy from petroleum products (highest EU share). Target: 600,000 HP installations 2021-2030.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €213 | €213 | €176 |
| Heat pump (air) | €134 | €124 | €88 |
| Heat pump (ground) | €113 | €106 | €78 |
| H₂ boiler (CENTRAL) | €306 | €224 | €133 |

> **Labour-cost adjustment applied:** Country multiplier **1.07** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 0 | 0.0 |
| MFH_HIGH | 0 | 0.0 |
| OTHER | 0 | 34.83 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Oil ~42% | Gas ~35% | Peat ~5% | Electricity (incl HP) ~10% | Biomass/coal ~8%

High oil dependency reflects rural off-gas-grid population. Gas concentrated in Dublin + east coast. Peat use being phased out by Bord na Móna.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 220 |
| 2030 | 120 |
| 2040 | 45 |
| 2050 | 8 |

---

## District heating context

**Share:** ~<2% of residential heating.

Very limited — Tallaght DH (waste heat from Amazon data centre), small university networks. CHP not widely deployed.

---

## Key actors

Utility: ESB, Bord Gáis. SEAI (state agency). HP brands: Daikin, Mitsubishi, NIBE, Joule.

---

## National programmes

SEAI (Sustainable Energy Authority of Ireland) Better Energy Homes scheme — €6,500 for ASHP, €4,500 for hybrid. Carbon tax escalator (€7.50/t increase annually).

**Subsidies:** SEAI: ASHP €6,500, A2A €3,500, hybrid HP €4,500. Strong long-term consistency.

---

## Risk flags

- High oil dependency in rural areas — off-grid customers face highest transition costs.
- HP installer shortage — government targeting trade training.
- New build market dominant for HP; retrofit market slower.
- Ranks 5th in Europe HP/1000 households — but still small base.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 34.8 TWh  
**NUTS coverage:** 1 NUTS1 · 2 NUTS2 · 8 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `IE0` | Ireland | 34.83 | 100.0% | 0 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `IE02` | IE02 | 25.93 | 74.5% | 0 |
| `IE01` | IE01 | 8.89 | 25.5% | 0 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/IE.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 5 (NW temperate))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/ie.yaml`; methodology: `literature/ireland/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 3 NUTS2 / 8 NUTS3 |
| TABULA typology | IE (direct) |
| Climate multiplier | 0.9846 (Option B; tabula_reference_hdd = 2600.0) |
| Retrofit blend factor | 0.85 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.78 (Mechanism A, imputed-floor data quality) |
| class_mix proxy | no |
| Census floor-area benchmark | 237 Mm2 (census/EUBUCCO 0.79) |
| Hotmaps 2015 benchmark | 34.83 TWh |
| **Bottom-up result** | **35.1 TWh** (+0.6 % vs Hotmaps, OK) |

Applied corrections: Option B reference-HDD correction; EUBUCCO area_correction 0.78 (imputed-floor over-count).

**Insight (2026-05-25):** Ireland has the tightest NW-temperate reconciliation (+0.6 %) via an `eubucco.area_correction` 0.78 (CSO Census 2022; OSM-sourced footprints with <15 % observed heights -> imputed-floor over-count). Direct Energy Action typology.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 28% · oil 56% · biomass 3% · resistance 6% · heat pump (air 7% + ground 0%) · district heat 0%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €186 | €185 | €150 |
| Heat pump (air) | €117 | €111 | €88 |
| Heat pump (ground) | €109 | €102 | €77 |
| Hydrogen boiler (CENTRAL) | €215 | €120 | €83 |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Net Zero (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **10%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 73% · district heat 27% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 10%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 28%, stock turnover 5.2%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.77**, range [0.58–1.00] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 6 (6 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 13 [11–19], new-build 28 [19–41] (central [low–high]); across the delivered-H2 supply band 6 [-4–19].

<!-- /COUNTRY_MODEL_UPDATE -->
