# Croatia (HR)

> **RQ relevance:** 44.9% residential energy from renewables (mainly biomass). Highest energy consumption per dwelling in EU after climate adjustment. Gas price unusually low (€46/MWh) — distorted prior to ETS2. Coastal/inland climate split. Small market.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €46/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €200/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 180 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 45% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.94 | Hotmaps HDD; EHPA |
| Annual heating hours | 1785/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2038 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2038 |


**Context:** 44.9% residential energy from renewables (biomass). Highest energy consumption per dwelling in EU after climate adjustment.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €115 | €123 | €119 |
| Heat pump (air) | €92 | €85 | €59 |
| Heat pump (ground) | €78 | €73 | €53 |
| H₂ boiler (CENTRAL) | €294 | €212 | €123 |

> **Labour-cost adjustment applied:** Country multiplier **0.55** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 628,687 | 1.14 |
| MFH_HIGH | 581,689 | 1.02 |
| OTHER | 2,455,633 | 16.07 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Biomass (wood) ~45% | Gas ~30% | Electricity (incl HP) ~15% | DH ~7% | Oil ~3%

Heavy wood-burning culture (rural, mountain areas). Gas dominant in Zagreb + coastal cities. Eurostat 2023: 44.9% renewables (mostly biomass).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 180 |
| 2030 | 100 |
| 2040 | 40 |
| 2050 | 8 |

---

## District heating context

**Share:** ~7% of residential heating.

Zagreb DH (HEP-Toplinarstvo) — largest. Some smaller networks. Mostly gas + some biomass.

---

## Key actors

Utility: HEP. DH: HEP-Toplinarstvo. HP brands: Daikin, Mitsubishi, Bosch.

---

## National programmes

NRRP-funded HP grants. Environmental Protection and Energy Efficiency Fund (EPEEF). Building Energy Renovation Programme.

**Subsidies:** EPEEF grants — up to 60% for HP in renovation projects. NRRP allocations.

---

## Risk flags

- Subsidised gas price €46/MWh — exposed when ETS2 hits 2027.
- 8,000 HPs sold 2024 — small market.
- Wood-burning air quality issues — PM2.5 problems in inland cities.
- Tourism economy seasonal — heating mostly off-season.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 2 (IT + Adriatic))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/hr.yaml`; methodology: `literature/croatia/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 2 NUTS2 / 21 NUTS3 |
| TABULA typology | SI (proxy) |
| Climate multiplier | 0.8161 |
| Retrofit blend factor | 0.953 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.59 (Mechanism A, imputed-floor data quality) |
| class_mix proxy | no |
| Census floor-area benchmark | 188 Mm2 (census/EUBUCCO 0.6) |
| Hotmaps 2015 benchmark | 18.23 TWh |
| **Bottom-up result** | **17.8 TWh** (-2.2 % vs Hotmaps, OK) |

Applied corrections: EUBUCCO area_correction 0.59 (imputed-floor over-count).

**Insight (2026-05-25):** Croatia reconciles at -2.2 % via an `eubucco.area_correction` 0.59 (Mechanism A: imputed floors + DZS-2021 census). Uses the SI typology as proxy. The region-split refinement (HR03 Adriatic coast <- Italian Middle-zone) remains a documented future intensity refinement but is no longer required for reconciliation.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 25% · oil 4% · biomass 59% · resistance 2% · heat pump (air 1% + ground 0%) · district heat 8%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €92 | €102 | €99 |
| Heat pump (air) | €82 | €78 | €61 |
| Heat pump (ground) | €77 | €72 | €54 |
| Hydrogen boiler (CENTRAL) | €279 | €147 | €96 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 66% · district heat 34% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 30%, stock turnover 5.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.07**, range [0.80–1.37] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 42 (42 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 51 [48–60], new-build 72 [60–91] (central [low–high]); across the delivered-H2 supply band 42 [27–58].

<!-- /COUNTRY_MODEL_UPDATE -->
