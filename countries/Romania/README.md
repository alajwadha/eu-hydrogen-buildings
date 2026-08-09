# Romania (RO)

> **RQ relevance:** 2.5M dwellings heated directly by gas; 3.5M by solid fuel (wood/coal). Romania protested ETS2 — affordability. 54.3% residential energy from natural gas (Eurostat 2023). DH in major cities (Bucharest) but networks deteriorating. Lowest gas price in EU after BG (€56/MWh).

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €56/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €180/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 250 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 10 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 45% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.88 | Hotmaps HDD; EHPA |
| Annual heating hours | 2214/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2040 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2040 |


**Context:** 2.5M dwellings heated directly by gas; 3.5M by solid fuel (wood/coal). Romanian authorities cited unaffordability of rapid transition. 54.3% residential energy from renewables (mostly biomass). Gradual approach: new collective housing first.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €113 | €121 | €114 |
| Heat pump (air) | €83 | €77 | €53 |
| Heat pump (ground) | €69 | €65 | €47 |
| H₂ boiler (CENTRAL) | €277 | €196 | €109 |

> **Labour-cost adjustment applied:** Country multiplier **0.42** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 11,422,501 | 15.3 |
| MFH_HIGH | 6,796,324 | 9.44 |
| OTHER | 36,455,432 | 49.51 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~54% | Biomass/wood ~25% | District heating ~12% | Electricity (incl HP) ~6% | Oil/coal ~3%

Eurostat 2023: 54.3% gas. Wood-burning dominant in rural Carpathians. DH Bucharest serves ~600k apartments (RADET — bankruptcies issues).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 250 |
| 2030 | 130 |
| 2040 | 50 |
| 2050 | 10 |

---

## District heating context

**Share:** ~12% of residential heating.

Bucharest (Termoenergetica, ex-RADET) — major network, financial difficulties. Smaller networks in Constanța, Timișoara, Iași. Mostly gas + (some) cogeneration.

---

## Key actors

Utilities: Hidroelectrica (electricity), Romgaz, OMV Petrom. DH: Termoenergetica (Bucharest). HP brands: Daikin, Bosch, Mitsubishi.

---

## National programmes

Casa Verde (Green House) — solar PV + HP grants. NRRP. ANRE renewable heating support.

**Subsidies:** Casa Verde Plus — ~€4,000 for HP. National building renovation grants under NRRP.

---

## Risk flags

- 3.5M wood/coal homes — major rural transition challenge.
- Bucharest DH financial collapse (RADET 2018-19 — restructured as Termoenergetica) — service reliability issues.
- ETS2 protest — Romania challenged €149/t projections.
- High energy poverty (>30%).
- Limited HP market (10,000 sold 2024).

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 20% | 38% | 0% | 12% | 28% |
| 2030 | 22% | 36% | 0% | 12% | 26% |
| 2050 | 52% | 0% | 6% | 15% | 24% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 74.3 TWh  
**NUTS coverage:** 4 NUTS1 · 8 NUTS2 · 42 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `RO3` | Macroregiunea Trei | 20.75 | 27.9% | 15,158,748 |
| `RO2` | Macroregiunea Doi | 20.42 | 27.5% | 15,728,018 |
| `RO1` | Macroregiunea Unu | 18.97 | 25.5% | 13,645,374 |
| `RO4` | Macroregiunea Patru | 14.11 | 19.0% | 10,142,117 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `RO21` | Nord-Est | 11.69 | 15.7% | 8,925,721 |
| `RO32` | Bucureşti-Ilfov | 10.40 | 14.0% | 7,198,274 |
| `RO31` | Sud-Muntenia | 10.35 | 13.9% | 7,960,474 |
| `RO11` | Nord-Vest | 9.71 | 13.1% | 7,191,021 |
| `RO12` | Centru | 9.26 | 12.5% | 6,454,353 |
| `RO22` | Sud-Est | 8.72 | 11.8% | 6,802,297 |
| `RO41` | Sud-Vest Oltenia | 7.07 | 9.5% | 5,317,293 |
| `RO42` | Vest | 7.04 | 9.5% | 4,824,824 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/RO.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 6 (Nordic + Balkan))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/ro.yaml`; methodology: `literature/romania/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 8 NUTS2 / 42 NUTS3 |
| TABULA typology | CZ (proxy) |
| Climate multiplier | 0.825 |
| Retrofit blend factor | 0.906 |
| comfort_regime deflator | 0.6 |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 730 Mm2 (census/EUBUCCO 0.62) |
| Hotmaps 2015 benchmark | 82.0 TWh |
| **Bottom-up result** | **99.1 TWh** (+20.9 % vs Hotmaps, ACC) |

Applied corrections: comfort_regime deflator 0.6 (intensity layer).

**Insight (2026-05-25):** Romania lands at +20.9 % (ACC) via a stock-weighted `comfort_regime` deflator 0.60 (urban-MFH x rural-wood-stove x post-2010; World Bank 2024 + EU-SILC). Rural Carpathian wood-stove heating at ~15 % delivered efficiency is the dominant driver.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 34% · oil 1% · biomass 48% · resistance 3% · heat pump (air 0% + ground 0%) · district heat 13%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €97 | €106 | €99 |
| Heat pump (air) | €74 | €70 | €55 |
| Heat pump (ground) | €69 | €64 | €48 |
| Hydrogen boiler (CENTRAL) | €249 | €129 | €83 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 35% | 12% | 2% | 10% | 39% |
| Stated Policies | 42% | 13% | 6% | 10% | 27% |
| Net Zero | 51% | 17% | 4% | 16% | 9% |
| H2 Push | 44% | 15% | 8% | 15% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **5%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €3.1bn · Stated Policies €5.0bn · Net Zero €7.0bn · H2 Push €6.7bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 66% · district heat 34% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 28%, stock turnover 5.2%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.97**, range [0.73–1.24] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 35 (35 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 43 [40–52], new-build 62 [52–79] (central [low–high]); across the delivered-H2 supply band 35 [22–50].

<!-- /COUNTRY_MODEL_UPDATE -->
