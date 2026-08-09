# Czech Republic (CZ)

> **RQ relevance:** 40% coal in electricity mix (2023). High grid CO₂ — HP environmental benefit limited until grid decarbonises. Prague DH largest in country. Replacement ban delayed to 2038. HP market collapsed in 2024 (-64% — largest fall in Europe).

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €90/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €310/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 420 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 20 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 55% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.79 | Hotmaps HDD; EHPA |
| Annual heating hours | 2571/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2038 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2038 |


**Context:** 40% coal in electricity mix (2023, EMBER). High grid carbon intensity. HP environmental benefit depends critically on grid decarbonisation.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €148 | €152 | €131 |
| Heat pump (air) | €135 | €127 | €87 |
| Heat pump (ground) | €111 | €105 | €75 |
| H₂ boiler (CENTRAL) | €274 | €193 | €107 |

> **Labour-cost adjustment applied:** Country multiplier **0.60** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 4,628,092 | 12.02 |
| MFH_HIGH | 5,786,384 | 15.91 |
| OTHER | 21,155,876 | 56.72 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~36% | District heating ~31% | Coal/solid ~12% | Biomass ~11% | HP+electric ~10%

DH widely used in cities. Coal still significant in rural single-family homes. Gas dominant in newer urban/suburban housing.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 420 |
| 2030 | 250 |
| 2040 | 100 |
| 2050 | 20 |

---

## District heating context

**Share:** ~31% of residential heating.

Largest DH: Prague (Pražská teplárenská — 265,000 households, 13 PJ/year). Waste heat from Mělník TPS (30km distant). Many city/town networks.

---

## Key actors

Utilities: ČEZ, EPH, Pražská teplárenská. HP brands: Bosch, Daikin, Mitsubishi, NIBE, Stiebel Eltron.

---

## National programmes

Modernisation Fund (EU ETS auction revenue) — boiler replacement scheme "Nová zelená úsporám" (New Green Savings). Heat pump grants up to CZK 180,000.

**Subsidies:** Nová zelená úsporám — up to CZK 180,000 per HP. Modernisation Fund building renovation.

---

## Risk flags

- HP sales -64% in 2024 — largest market collapse in Europe.
- Coal-dependent grid — HP near-term CO₂ benefit weak.
- Czech industrial cluster (ŠKODA, automotive) — high electricity demand competes with residential HP.
- DH affordability politically sensitive in current high-inflation environment.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 18% | 38% | 0% | 13% | 29% |
| 2030 | 20% | 36% | 0% | 13% | 28% |
| 2050 | 48% | 0% | 7% | 17% | 26% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 84.6 TWh  
**NUTS coverage:** 1 NUTS1 · 8 NUTS2 · 14 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `CZ0` | Česko | 84.64 | 100.0% | 31,570,352 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `CZ01` | Praha | 14.50 | 17.1% | 4,277,307 |
| `CZ06` | Jihovýchod | 12.69 | 15.0% | 4,913,481 |
| `CZ05` | Severovýchod | 11.57 | 13.7% | 4,414,042 |
| `CZ02` | Střední Čechy | 9.85 | 11.6% | 4,049,815 |
| `CZ03` | Jihozápad | 9.40 | 11.1% | 3,610,834 |
| `CZ08` | Moravskoslezsko | 9.39 | 11.1% | 3,529,131 |
| `CZ07` | Střední Morava | 8.95 | 10.6% | 3,466,187 |
| `CZ04` | Severozápad | 8.29 | 9.8% | 3,309,555 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/CZ.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 4 (Visegrad))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/cz.yaml`; methodology: `literature/czech_republic/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 8 NUTS2 / 14 NUTS3 |
| TABULA typology | CZ (direct) |
| Climate multiplier | 0.9797 (Option B; tabula_reference_hdd = 3400) |
| Retrofit blend factor | 0.898 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 450 Mm2 (census/EUBUCCO 0.82) |
| Hotmaps 2015 benchmark | 84.64 TWh |
| **Bottom-up result** | **77.9 TWh** (-8.0 % vs Hotmaps, OK) |

Applied corrections: Option B reference-HDD correction.

**Insight (2026-05-25):** Czechia reconciles at -8.0 % on the direct EPISCOPE typology. Verification corrected the source attribution: the primary EPISCOPE scientific report is **STU-K**, not Lupisek/UCEEB (a companion deliverable). CZ is the proxy source for Slovakia.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 35% · oil 6% · biomass 16% · resistance 5% · heat pump (air 3% + ground 1%) · district heat 33%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €131 | €135 | €116 |
| Heat pump (air) | €116 | €111 | €87 |
| Heat pump (ground) | €105 | €99 | €74 |
| Hydrogen boiler (CENTRAL) | €282 | €142 | €88 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 35% | 12% | 2% | 11% | 39% |
| Stated Policies | 42% | 13% | 6% | 10% | 27% |
| Net Zero | 51% | 23% | 4% | 12% | 9% |
| H2 Push | 45% | 19% | 9% | 11% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €2.0bn · Stated Policies €3.1bn · Net Zero €3.2bn · H2 Push €3.6bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 61% · district heat 39% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 18%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 38%, stock turnover 6.3%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.14**, range [0.87–1.35] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 14 (14 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 20 [18–26], new-build 33 [26–44] (central [low–high]); across the delivered-H2 supply band 14 [-0–26].

<!-- /COUNTRY_MODEL_UPDATE -->
