# Spain (ES)

> **RQ relevance:** PNIEC 2023-2030 (Royal Decree 986/2024) targets 35% electrification by 2030. 97% renewable electricity by 2050 plan. ~14% HP+electricity in residential heating. Warm climate gives high HP COP (3.45). Air-to-air HPs dominant due to cooling demand.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €86/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €261/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 160 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 35% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 3.45 | Hotmaps HDD; EHPA |
| Annual heating hours | 1357/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** Relatively low heating demand per dwelling (warm climate). National NECP targets HP deployment but no formal boiler ban yet.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €183 | €187 | €166 |
| Heat pump (air) | €104 | €96 | €68 |
| Heat pump (ground) | €90 | €84 | €62 |
| H₂ boiler (CENTRAL) | €329 | €246 | €151 |

> **Labour-cost adjustment applied:** Country multiplier **0.83** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 13,560,820 | 16.89 |
| MFH_HIGH | 31,708,693 | 40.47 |
| OTHER | 91,723,920 | 116.22 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~42% | Oil ~14% | Coal ~3% | Electricity (incl HP) ~14% | Biomass ~13% | LPG/butane ~12% | DH ~2%

Idealista/IDEA: 42% gas, 14% oil, 3% coal in homes. North vs South split — Mediterranean South minimal heating. PNIEC targets ~50% renewable in heating by 2030.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 160 |
| 2030 | 90 |
| 2040 | 35 |
| 2050 | 8 |

---

## District heating context

**Share:** ~2% of residential heating.

Very low — limited to a few networks (Sant Cugat, Móstoles). Solar thermal more common.

---

## Key actors

Utilities: Iberdrola, Endesa, Naturgy. HP brands: Daikin, Mitsubishi, LG, Atlantic.

---

## National programmes

AFEC subsidies: €500/kW for ASHP up to €3,000. PNIEC programmes. Plan MOVES (decarbonisation in mobility + heating). Junta de Andalucía, regional schemes.

**Subsidies:** AFEC HP grant: €500/kW up to €3,000 (€2,000-3,000 typical). Plan MOVES IV operational.

---

## Risk flags

- HP grant scheme expired end-2024 — uncertainty on next programme.
- Reversible air-to-air HPs (split A/C) dominant — counts statistically as "HP" but inefficient for heating.
- High poverty in rural Spain — affordability constraints on retrofit.
- Heatwave-driven cooling demand growing fast — grid pressure summer peak.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 21% | 37% | 0% | 13% | 28% |
| 2030 | 23% | 35% | 0% | 13% | 26% |
| 2050 | 51% | 0% | 6% | 16% | 24% |


---

---


## EUBUCCO bottom-up heat demand build (build group 3 (Iberian + Aegean))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/es.yaml`; methodology: `literature/spain/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 19 NUTS2 / 59 NUTS3 |
| TABULA typology | ES (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.9175 |
| comfort_regime deflator | 0.59 |
| eubucco area_correction | 0.613 (Mechanism B, occupancy/stock-utilization) |
| class_mix proxy | no |
| Census floor-area benchmark | 2500 Mm2 (census/EUBUCCO 0.61) |
| Hotmaps 2015 benchmark | 173.59 TWh |
| **Bottom-up result** | **167.3 TWh** (-3.6 % vs Hotmaps, OK) |

Applied corrections: comfort_regime deflator 0.59 (intensity layer); occupancy correction 0.613 (heated-base; vacant/seasonal stock excluded).

**Insight (2026-05-25):** Spain lands at -3.6 % via two independent layers: a `comfort_regime` deflator 0.59 (IDAE SECH-SPAHOUSEC partial-heating regime, intensity) x an occupancy area_correction 0.613 (INE principal residences; vacant/secondary stock unheated). The Spanish IVE brochure publishes only *final* energy, not net q_h_nd, so the matrix cannot be brochure-verified -- an **upstream TABULA-source limitation**, not ours.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 31% · oil 22% · biomass 24% · resistance 12% · heat pump (air 11% + ground 0%) · district heat 0%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €150 | €154 | €135 |
| Heat pump (air) | €94 | €89 | €70 |
| Heat pump (ground) | €90 | €84 | €63 |
| Hydrogen boiler (CENTRAL) | €265 | €151 | €106 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 37% | 12% | 2% | 9% | 39% |
| Stated Policies | 42% | 14% | 6% | 9% | 27% |
| Net Zero | 52% | 21% | 4% | 12% | 9% |
| H2 Push | 43% | 18% | 9% | 13% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €26.5bn · Stated Policies €37.0bn · Net Zero €48.5bn · H2 Push €48.4bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 49% · district heat 51% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 8%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 32%, stock turnover 5.7%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.92**, range [0.69–1.18] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 43 (43 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 54 [50–65], new-build 80 [65–103] (central [low–high]); across the delivered-H2 supply band 43 [30–57].

<!-- /COUNTRY_MODEL_UPDATE -->
