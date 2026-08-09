# Cyprus (CY)

> **RQ relevance:** Mediterranean climate — heating hours only 642/year (lowest among 22). 60.3% residential space heating from oil (highest dependency in EU). Near-100% solar water heater penetration — unique building profile. Very small absolute heat demand.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €100/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €270/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 500 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 20 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 5% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 4.05 | Hotmaps HDD; EHPA |
| Annual heating hours | 642/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 60.3% residential space heating from oil (2023). Near-100% solar water heater penetration — unique building profile.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €273 | €274 | €244 |
| Heat pump (air) | €116 | €108 | €71 |
| Heat pump (ground) | €103 | €97 | €68 |
| H₂ boiler (CENTRAL) | €432 | €345 | €234 |

> **Labour-cost adjustment applied:** Country multiplier **0.70** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 572,307 | 0.69 |
| MFH_HIGH | 295,857 | 0.36 |
| OTHER | 1,745,165 | 2.1 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Oil ~60% | Electricity (direct + HP) ~30% | Solar thermal (DHW) ~8% | Wood ~2%

Eurostat 2023: 60.3% oil for space heating. Near-universal solar water heating (Mediterranean climate, building code mandates).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 500 |
| 2030 | 280 |
| 2040 | 100 |
| 2050 | 20 |

---

## District heating context

**Share:** ~<1% of residential heating.

No meaningful district heating — climate does not favour it.

---

## Key actors

Utility: EAC (Electricity Authority of Cyprus). HP brands: Daikin, Mitsubishi, LG.

---

## National programmes

EU NRRP funds. Cyprus Government "Save - Renovate" scheme. Small EHPA-tracked market (3,000 HPs sold 2024).

**Subsidies:** Small/suspended HP subsidies. EU NRRP grants for building renovation.

---

## Risk flags

- 60% oil dependency in space heating — biggest oil-boiler stock by share in EU.
- Off-grid for gas: no national gas distribution network.
- LNG terminal under construction at Vassilikos — geopolitical dimension.
- Higher LCOH due to cooling priority (A/C dominant).
- Grid CO₂ 500 g/kWh (highest in 22) — HP carbon benefit limited.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 3 (Iberian + Aegean))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/cy.yaml`; methodology: `literature/cyprus/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 1 NUTS2 / 1 NUTS3 |
| TABULA typology | CY (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.945 |
| comfort_regime deflator | 0.3 |
| eubucco area_correction | 0.5 (Mechanism B, occupancy/stock-utilization) |
| class_mix proxy | no |
| Census floor-area benchmark | 100 Mm2 (census/EUBUCCO 0.5) |
| Hotmaps 2015 benchmark | 3.15 TWh |
| **Bottom-up result** | **3.3 TWh** (+3.3 % vs Hotmaps, OK) |

Applied corrections: comfort_regime deflator 0.3 (intensity layer); occupancy correction 0.5 (heated-base; vacant/seasonal stock excluded).

**Insight (2026-05-25):** Cyprus reconciles at +3.3 % via a `comfort_regime` deflator 0.30 (reverse-cycle-AC top-up regime) x an occupancy area_correction 0.50 (~30 % vacancy + tourism/unfinished stock, unheated in mild winters). Structurally low-information (3.15 TWh denominator), but lands in the OK band.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 0% · oil 54% · biomass 6% · resistance 9% · heat pump (air 31% + ground 0%) · district heat 0%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €208 | €211 | €184 |
| Heat pump (air) | €103 | €98 | €75 |
| Heat pump (ground) | €103 | €97 | €71 |
| Hydrogen boiler (CENTRAL) | €416 | €251 | €183 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 50% · district heat 50% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 3%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.33**, range [1.03–1.68] — isolated island, ship-import only (not on the EHB).

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 112 (112 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 137 [129–163], new-build 197 [163–247] (central [low–high]); across the delivered-H2 supply band 112 [96–131].

<!-- /COUNTRY_MODEL_UPDATE -->
