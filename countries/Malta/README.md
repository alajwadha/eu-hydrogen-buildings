# Malta (MT)

> **RQ relevance:** 75.4% residential energy from electricity (highest EU share, Eurostat 2023). Mild Mediterranean climate — heating hours just 571/year (lowest in 22). Very small market. Reverse-cycle A/C dominant. Gas grid effectively absent.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €90/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €200/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 450 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 15 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 2% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 3.9 | Hotmaps HDD; EHPA |
| Annual heating hours | 571/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 75.4% residential energy from electricity (highest EU share, 2023). Mild climate — low absolute heating demand.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €275 | €277 | €251 |
| Heat pump (air) | €104 | €97 | €63 |
| Heat pump (ground) | €95 | €90 | €63 |
| H₂ boiler (CENTRAL) | €449 | €362 | €248 |

> **Labour-cost adjustment applied:** Country multiplier **0.62** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 283,665 | 0.13 |
| MFH_HIGH | 235,365 | 0.11 |
| OTHER | 1,038,048 | 0.49 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Electricity (direct + reversible HP) ~75% | LPG (bottled) ~15% | Solar thermal ~7% | Biomass <2%

Mild climate + electricity-dependent + universal A/C → unique profile. Heating tied to brief winter periods only.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 450 |
| 2030 | 250 |
| 2040 | 90 |
| 2050 | 15 |

---

## District heating context

**Share:** ~<1% of residential heating.

No district heating — climate does not support it.

---

## Key actors

Utility: Enemalta. HP brands: Daikin, Mitsubishi, LG (mostly imported).

---

## National programmes

Malta Enterprise / Regulator for Energy and Water Services schemes — small HP grants. Energy efficiency support for elderly/vulnerable.

**Subsidies:** Small national HP grant programmes; EU NRRP allocations.

---

## Risk flags

- Cooling-dominated climate — model focused on heating may overestimate transformation needs.
- Grid CO₂ 450 g/kWh — among worst in EU (LNG-fired plus interconnector imports).
- Small market (6,000 HPs sold 2024 — mostly A/A).
- Limited installer/maintenance base.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 2 (IT + Adriatic))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/mt.yaml`; methodology: `literature/malta/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 1 NUTS2 / 2 NUTS3 |
| TABULA typology | CY (proxy) |
| Climate multiplier | 0.721 |
| Retrofit blend factor | 0.972 |
| comfort_regime deflator | 0.22 |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 42 Mm2 (census/EUBUCCO 1.0) |
| Hotmaps 2015 benchmark | 0.73 TWh |
| **Bottom-up result** | **1.0 TWh** (+35.7 % vs Hotmaps, INV) |

Applied corrections: comfort_regime deflator 0.22 (intensity layer).

**Insight (2026-05-25):** Malta is the **only INV result (+35.7 %)** and a documented structural low-information case: the Hotmaps denominator is 0.73 TWh (smallest in the EU), so the ~0.27 TWh absolute gap is at the noise floor. A `comfort_regime` deflator 0.22 (NECP/EWA ~80 % reverse-cycle AC) brings it down from +231 %, but the recommended headline demand input for the paper stays the Hotmaps top-down 0.73 TWh.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 0% · oil 9% · biomass 0% · resistance 22% · heat pump (air 68% + ground 0%) · district heat 0%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €199 | €203 | €180 |
| Heat pump (air) | €91 | €87 | €66 |
| Heat pump (ground) | €92 | €86 | €63 |
| Hydrogen boiler (CENTRAL) | €413 | €251 | €184 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 40% · district heat 60% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 2%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 30%, stock turnover 5.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.31**, range [1.02–1.64] — isolated island, ship-import only (not on the EHB).

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 121 (121 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 146 [137–171], new-build 204 [171–255] (central [low–high]); across the delivered-H2 supply band 121 [105–139].

<!-- /COUNTRY_MODEL_UPDATE -->
