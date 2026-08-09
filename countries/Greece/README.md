# Greece (GR)

> **RQ relevance:** 40.9% residential space heating from oil (Eurostat 2023). Oil boiler ban announced 2025 in all buildings (EHPA Nov 2025 map). Significant biomass + electric heating. DH limited to Western Macedonia/Peloponnese (lignite-fed historically). Mediterranean — moderate heating demand.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €110/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €250/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 300 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 10 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 35% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 3.6 | Hotmaps HDD; EHPA |
| Annual heating hours | 1285/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 40.9% residential space heating from oil products (2023, Eurostat). Significant oil boiler stock — transition requires active policy.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €207 | €208 | €178 |
| Heat pump (air) | €98 | €91 | €62 |
| Heat pump (ground) | €84 | €79 | €57 |
| H₂ boiler (CENTRAL) | €326 | €243 | €149 |

> **Labour-cost adjustment applied:** Country multiplier **0.65** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)



> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Oil ~41% | Biomass (wood/pellets) ~22% | Electricity (incl HP) ~21% | Gas ~13% | DH ~3%

Eurostat 2023: 40.9% oil products. Strong biomass use in rural/mountain areas (Epirus, Macedonia). Gas growing in urban Athens/Thessaloniki.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 300 |
| 2030 | 160 |
| 2040 | 60 |
| 2050 | 10 |

---

## District heating context

**Share:** ~3% of residential heating.

Western Macedonia (Ptolemaida, Kozani, Amyntaio) — historically lignite-fed, now transitioning. Serres (gas CHP). Small networks. Total ~3% nationally.

---

## Key actors

Utility: PPC (Public Power Corporation). HP brands: Daikin, Mitsubishi, LG.

---

## National programmes

"Exoikonomo" (Save Energy) home renovation grants. NRRP funds. Recently launched HP-specific grant scheme.

**Subsidies:** Exoikonomo and Photovoltaika sto Sxoleio programmes; HP under building renovation grants.

---

## Risk flags

- 41% oil dependency — second-highest in EU after Cyprus.
- Lignite phase-out — DH systems lose primary fuel; need alternative.
- Heatwave-driven cooling > heating demand in summer.
- 18,000 HPs sold 2024 (EHPA) — modest scale.
- Energy poverty significant — political sensitivity on fuel tax.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 3 (Iberian + Aegean))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/el.yaml`; methodology: `literature/greece/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 13 NUTS2 / 52 NUTS3 |
| TABULA typology | EL (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.9325 |
| comfort_regime deflator | 0.55 |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 630 Mm2 (census/EUBUCCO 0.7) |
| Hotmaps 2015 benchmark | 60.6 TWh |
| **Bottom-up result** | **63.0 TWh** (+4.0 % vs Hotmaps, OK) |

Applied corrections: comfort_regime deflator 0.55 (intensity layer).

**Insight (2026-05-25):** Greece lands at +4.0 % via a `comfort_regime` deflator 0.55 (Balaras/Dascalaki measured ~5 h/day operation vs the 18 h KENAK reference). Verification: the **published NOA matrix** pre-1990 rows run ~20-30 % high vs Zone-B calculated demand -- an upstream-source nuance, partly offset by the deflator and disclosed.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 18% · oil 37% · biomass 27% · resistance 5% · heat pump (air 11% + ground 0%) · district heat 1%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €179 | €180 | €152 |
| Heat pump (air) | €89 | €85 | €66 |
| Heat pump (ground) | €86 | €81 | €60 |
| Hydrogen boiler (CENTRAL) | €296 | €167 | €116 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 59% · district heat 41% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 20%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 30%, stock turnover 5.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.04**, range [0.78–1.33] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 56 (56 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 71 [66–86], new-build 106 [86–136] (central [low–high]); across the delivered-H2 supply band 56 [42–72].

<!-- /COUNTRY_MODEL_UPDATE -->
