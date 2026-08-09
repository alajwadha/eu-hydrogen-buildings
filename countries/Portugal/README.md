# Portugal (PT)

> **RQ relevance:** 88.2% residential space heating from renewables (mainly biomass — Eurostat 2023). Lowest gas dependency among modelled countries. Transition pathway is biomass → HP, not gas → HP. HP sales grew (one of three EU countries with growth in 2024). 71% renewable electricity 2024.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €115/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €250/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 120 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 25% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 3.54 | Hotmaps HDD; EHPA |
| Annual heating hours | 1142/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 88.2% residential space heating from renewables (mainly biomass, 2023). Low gas dependency — transition pathway is biomass → HP.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €222 | €223 | €190 |
| Heat pump (air) | €100 | €92 | €65 |
| Heat pump (ground) | €86 | €80 | €60 |
| H₂ boiler (CENTRAL) | €339 | €256 | €159 |

> **Labour-cost adjustment applied:** Country multiplier **0.66** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 5,473,716 | 3.74 |
| MFH_HIGH | 4,609,495 | 3.24 |
| OTHER | 20,182,824 | 13.99 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Biomass (wood, fireplace) ~50% | Electricity (incl HP) ~30% | Gas ~10% | LPG ~7% | Oil ~3%

Eurostat 2023: 88.2% renewables in space heating (mostly biomass burning in stoves/fireplaces). Mild climate — many homes have no central heating at all.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 120 |
| 2030 | 65 |
| 2040 | 25 |
| 2050 | 5 |

---

## District heating context

**Share:** ~<1% of residential heating.

Very limited — Lisbon Climaespaço (CHP-based). Not a significant national share.

---

## Key actors

Utilities: EDP, Galp. HP brands: Daikin, Mitsubishi, Vaillant, Bosch.

---

## National programmes

Programa de Apoio Edifícios + Sustentáveis (Sustainable Buildings Support). ADENE energy efficiency grants. NRRP funds.

**Subsidies:** Programa Edifícios Sustentáveis — HP grants. ADENE schemes.

---

## Risk flags

- 50%+ biomass burning in fireplaces — major PM2.5 air quality issue.
- Renewable electricity grid (71%) — HP carbon performance excellent.
- Limited central heating culture — installation density low.
- 95% renewable electricity in April 2024 — strong HP case.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 3 (Iberian + Aegean))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/pt.yaml`; methodology: `literature/portugal/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 7 NUTS2 / 25 NUTS3 |
| TABULA typology | ES (proxy) |
| Climate multiplier | 0.6 |
| Retrofit blend factor | 0.935 |
| comfort_regime deflator | 0.1 |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 575 Mm2 (census/EUBUCCO 0.55) |
| Hotmaps 2015 benchmark | 20.97 TWh |
| **Bottom-up result** | **21.7 TWh** (+3.6 % vs Hotmaps, OK) |

Applied corrections: comfort_regime deflator 0.1 (intensity layer).

**Insight (2026-05-25):** Portugal lands at +3.6 % via a `comfort_regime` deflator 0.10 -- the Magalhaes & Leal (2014) measured-vs-nominal lower bound, the strongest published TABULA-vs-actual gap in the EU. Uses the ES typology as proxy.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 3% · oil 4% · biomass 52% · resistance 18% · heat pump (air 23% + ground 0%) · district heat 0%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €185 | €186 | €156 |
| Heat pump (air) | €91 | €86 | €67 |
| Heat pump (ground) | €87 | €81 | €61 |
| Hydrogen boiler (CENTRAL) | €252 | €148 | €106 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 56% · district heat 44% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 30%, stock turnover 5.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.84**, range [0.63–1.07] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 45 (45 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 59 [54–72], new-build 90 [72–117] (central [low–high]); across the delivered-H2 supply band 45 [34–58].

<!-- /COUNTRY_MODEL_UPDATE -->
