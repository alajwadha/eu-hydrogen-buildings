# Denmark (DK)

> **RQ relevance:** World leader in district heating — ~64.5% of households on DH, >95% coverage in 4 largest cities. Plan to convert ~50% of remaining gas-heated homes (400k) to DH by 2028. Coal already phased out of DH. Cross-party political consensus enables fast transition.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €131/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €349/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 130 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 15% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.76 | Hotmaps HDD; EHPA |
| Annual heating hours | 2214/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2013 |
| Replacement Fossil Ban | 2030 |
| Full Fossil Ban | 2035 |
| Hp Mandate Year | 2030 |


**Context:** Gas network connection banned in new buildings since 2013. Target: 50% connected to district heating by 2028. 70% CO2 reduction by 2030 vs 1990.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €218 | €217 | €179 |
| Heat pump (air) | €157 | €145 | €104 |
| Heat pump (ground) | €134 | €125 | €93 |
| H₂ boiler (CENTRAL) | €312 | €230 | €138 |

> **Labour-cost adjustment applied:** Country multiplier **1.65** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 3,531,582 | 10.88 |
| MFH_HIGH | 2,519,075 | 7.62 |
| OTHER | 12,230,422 | 37.4 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** District heating ~65% | HP+electric ~18% | Gas ~10% | Oil ~5% | Biomass ~2%

IEA 2023: DH 50%+ of buildings sector heat. 64.5% of households connected. Gas being phased out by 2028.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 130 |
| 2030 | 70 |
| 2040 | 25 |
| 2050 | 5 |

---

## District heating context

**Share:** ~65% of residential heating.

60,000 km of DH network. 60% renewable input (biomass, waste, geothermal, solar). 95%+ coverage in Copenhagen, Aarhus, Odense, Aalborg. CHP plants (e.g. Vestforbrænding waste-to-energy) are core providers. Heat plan 2030 expanding by 39,000 customers.

---

## Key actors

DH operators: Vestforbrænding, HOFOR (Copenhagen), Fjernvarme Fyn. HP brands: Danfoss, NIBE, Bosch, Vaillant. Climate Ministry, Danish Energy Agency.

---

## National programmes

Building Pool grant scheme — €80M annually for HPs. Tilskudspuljen (Climate Pool) for fossil heating replacement. Special schemes for low-income households.

**Subsidies:** Building Pool — DKK 8,750 per home for fossil heating replacement; additional grants for low-income.

---

## Risk flags

- Biomass sustainability questions: 70% of DH biomass imported (mainly from Baltic states). Approx 75% of biomass imported overall.
- North Sea oil/gas phase-out by 2050 — affects state revenue planning.
- Successful early adoption — model for other countries but not directly replicable in countries lacking DH.
- DH expansion to remaining gas-heated homes by 2028 is ambitious — feasibility uncertain.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 19% | 36% | 0% | 14% | 29% |
| 2030 | 38% | 0% | 0% | 20% | 40% |
| 2050 | 49% | 0% | 7% | 17% | 25% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 55.9 TWh  
**NUTS coverage:** 1 NUTS1 · 5 NUTS2 · 11 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `DK0` | Danmark | 55.90 | 100.0% | 18,281,079 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `DK01` | Hovedstaden | 17.35 | 31.0% | 5,770,646 |
| `DK04` | Midtjylland | 12.53 | 22.4% | 4,128,063 |
| `DK03` | Syddanmark | 12.19 | 21.8% | 3,868,486 |
| `DK02` | Sjælland | 7.83 | 14.0% | 2,620,217 |
| `DK05` | Nordjylland | 6.00 | 10.7% | 1,893,667 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/DK.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 6 (Nordic + Balkan))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/dk.yaml`; methodology: `literature/denmark/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 5 NUTS2 / 11 NUTS3 |
| TABULA typology | DK (direct) |
| Climate multiplier | 0.9548 (Option B; tabula_reference_hdd = 2900.0) |
| Retrofit blend factor | 0.805 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.7 (Mechanism A, imputed-floor data quality) |
| class_mix proxy | no |
| Census floor-area benchmark | 356 Mm2 (census/EUBUCCO 0.7) |
| Hotmaps 2015 benchmark | 55.9 TWh |
| **Bottom-up result** | **51.7 TWh** (-7.6 % vs Hotmaps, OK) |

Applied corrections: Option B reference-HDD correction; EUBUCCO area_correction 0.7 (imputed-floor over-count).

**Insight (2026-05-25):** Denmark reconciles at -7.6 % via an `eubucco.area_correction` 0.70 (Danmarks Statistik + Sommerhuse). Direct SBi TABULA. Note ~63 % of Danish residential heat is delivered by district heating -- the bottom-up reports useful demand at the meter; downstream DH allocation is separate.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 13% · oil 4% · biomass 6% · resistance 2% · heat pump (air 7% + ground 1%) · district heat 66%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €188 | €188 | €152 |
| Heat pump (air) | €138 | €130 | €104 |
| Heat pump (ground) | €129 | €120 | €91 |
| Hydrogen boiler (CENTRAL) | €228 | €127 | €88 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 37% | 11% | 2% | 9% | 39% |
| Stated Policies | 45% | 12% | 6% | 9% | 27% |
| Net Zero | 54% | 22% | 4% | 10% | 9% |
| H2 Push | 48% | 17% | 8% | 10% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Stated Policies, Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **40%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €1.4bn · Stated Policies €2.4bn · Net Zero €2.4bn · H2 Push €3.0bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 67% · district heat 33% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 10%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.82**, range [0.61–1.08] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline -3 (at heat-pump parity, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 2 [0–7], new-build 13 [7–23] (central [low–high]); across the delivered-H2 supply band -3 [-14–11].

<!-- /COUNTRY_MODEL_UPDATE -->
