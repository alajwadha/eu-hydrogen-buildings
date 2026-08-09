# Slovenia (SI)

> **RQ relevance:** 40% residential energy from renewables (Eurostat 2023). DH significant in Ljubljana, Maribor, Velenje. Strong wood-burning culture in rural Alpine areas. Ljubljana DH coal-to-gas transition under way; biomass + WTE growing.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €90/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €250/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 200 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 10 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 50% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.91 | Hotmaps HDD; EHPA |
| Annual heating hours | 2142/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2028 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 40% residential energy from renewables (2023). District heating significant in urban areas.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €158 | €162 | €141 |
| Heat pump (air) | €109 | €101 | €72 |
| Heat pump (ground) | €92 | €86 | €63 |
| H₂ boiler (CENTRAL) | €289 | €208 | €119 |

> **Labour-cost adjustment applied:** Country multiplier **0.78** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 1,141,137 | 2.97 |
| MFH_HIGH | 620,300 | 1.61 |
| OTHER | 3,616,484 | 9.41 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Biomass (wood) ~33% | Gas ~22% | District heating ~16% | Oil ~14% | Electricity (incl HP) ~13% | Coal ~2%

Strong biomass culture especially Alpine north. Gas dominant in central Slovenia. DH widespread urban.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 200 |
| 2030 | 110 |
| 2040 | 45 |
| 2050 | 10 |

---

## District heating context

**Share:** ~16% of residential heating.

Energetika Ljubljana (capital, ~57k connections, transitioning from coal Šoštanj power plant). Maribor DH. Velenje DH.

---

## Key actors

Utilities: HSE, GEN, Petrol. DH: Energetika Ljubljana. HP brands: NIBE, Daikin, Vaillant, Buderus.

---

## National programmes

Eko Sklad (Eco Fund) — HP grants up to €4,000. New green deal subsidies. NRRP funds. Building Energy Renovation grants.

**Subsidies:** Eko Sklad — up to €4,000 per HP grant. Tax deductions for energy efficiency.

---

## Risk flags

- Coal phase-out (Šoštanj plant — sole large coal asset) affects DH supply Ljubljana.
- Alpine air quality issues from wood-burning.
- Small market (13,000 HPs sold 2024).
- Renewable share constrained by terrain (limited wind potential).

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 2 (IT + Adriatic))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/si.yaml`; methodology: `literature/slovenia/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 2 NUTS2 / 12 NUTS3 |
| TABULA typology | SI (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.81 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 72 Mm2 (census/EUBUCCO 0.41) |
| Hotmaps 2015 benchmark | 13.99 TWh |
| **Bottom-up result** | **17.4 TWh** (+24.5 % vs Hotmaps, ACC) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Slovenia lands at +24.5 % (ACC, edge of band) on the direct ZRMK typology -- which verification rated the **cleanest-mapped matrix** in the build (values reproduce the ZRMK national aggregates; Hotmaps independently corroborated by the ZRMK energy balance). The single ZRMK multi-unit class (MFH_LOW = MFH_HIGH) is a source limitation, not a pipeline choice.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 14% · oil 15% · biomass 45% · resistance 6% · heat pump (air 9% + ground 0%) · district heat 11%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €139 | €143 | €123 |
| Heat pump (air) | €98 | €92 | €73 |
| Heat pump (ground) | €91 | €85 | €64 |
| Hydrogen boiler (CENTRAL) | €297 | €154 | €99 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 63% · district heat 37% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 30%, stock turnover 5.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.16**, range [0.91–1.38] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 35 (35 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 43 [40–50], new-build 60 [50–76] (central [low–high]); across the delivered-H2 supply band 35 [22–47].

<!-- /COUNTRY_MODEL_UPDATE -->
