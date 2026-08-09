# Hungary (HU)

> **RQ relevance:** 46.4% residential energy from gas (Eurostat 2023). Subsidised gas price €31/MWh — political price cap, anomaly in LCOH (HP LCOH €61 vs gas €95). Strong DH in urban areas. Geothermal potential. CEE transition pace constrained by income.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €31/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €104/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 250 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 10 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 70% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.91 | Hotmaps HDD; EHPA |
| Annual heating hours | 2285/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2038 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2038 |


**Context:** 46.4% residential energy from gas (2023). Strong district heating infrastructure in urban areas.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €86 | €96 | €99 |
| Heat pump (air) | €56 | €52 | €35 |
| Heat pump (ground) | €48 | €45 | €32 |
| H₂ boiler (CENTRAL) | €276 | €196 | €109 |

> **Labour-cost adjustment applied:** Country multiplier **0.47** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 4,726,297 | 11.31 |
| MFH_HIGH | 1,791,810 | 4.24 |
| OTHER | 13,045,512 | 56.43 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~46% | Biomass ~28% | District heating ~16% | Electricity (incl HP) ~8% | Oil ~2%

Eurostat 2023: 46.4% gas residential. Gas-heavy Hungary heavily exposed pre-2022; price cap from 2013 ("rezsicsökkentés" — utility price reduction).

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

**Share:** ~16% of residential heating.

15.5% of dwellings on DH (2011 census). Veolia, FŐTÁV (Budapest, ~250k households). Pécs DH biomass-fired. Geothermal in several towns (Mosonmagyaróvár, Hódmezővásárhely).

---

## Key actors

Utility: MVM (state). DH: FŐTÁV (Budapest), Veolia. HP brands: Daikin, Vaillant, Mitsubishi, Bosch.

---

## National programmes

"Otthonfelújítási támogatás" (Home renovation grant) — up to €7,500 for HP. Geothermal expansion programme.

**Subsidies:** Otthonfelújítási támogatás — 50% or up to HUF 3M (~€7,500) for renovations including HPs.

---

## Risk flags

- Hungary government gas price cap = €31/MWh, hugely subsidised vs market.
- Russian gas/oil dependency — 85% crude oil import from Russia. EU exemption preserves flow.
- ETS2 pass-through politically explosive given cap.
- HP subsidy capped — limits uptake.
- District heating losing customers — affordability + competition.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 20% | 39% | 0% | 12% | 28% |
| 2030 | 23% | 36% | 0% | 12% | 26% |
| 2050 | 52% | 0% | 6% | 15% | 24% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 72.0 TWh  
**NUTS coverage:** 3 NUTS1 · 7 NUTS2 · 20 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `HU3` | Alföld és Észak | 26.61 | 37.0% | 10,980,767 |
| `HU1` | Közép-Magyarország | 25.30 | 35.1% | 0 |
| `HU2` | Dunántúl | 20.07 | 27.9% | 8,582,852 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `HU10` | HU10 | 25.30 | 35.1% | 0 |
| `HU32` | Észak-Alföld | 9.62 | 13.4% | 4,083,730 |
| `HU33` | Dél-Alföld | 9.09 | 12.6% | 3,687,500 |
| `HU31` | Észak-Magyarország | 7.90 | 11.0% | 3,209,537 |
| `HU21` | Közép-Dunántúl | 7.00 | 9.7% | 3,111,662 |
| `HU22` | Nyugat-Dunántúl | 6.79 | 9.4% | 2,883,037 |
| `HU23` | Dél-Dunántúl | 6.28 | 8.7% | 2,588,153 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/HU.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 4 (Visegrad))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/hu.yaml`; methodology: `literature/hungary/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 8 NUTS2 / 20 NUTS3 |
| TABULA typology | DE (proxy) |
| Climate multiplier | 0.8574 |
| Retrofit blend factor | 0.949 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.57 (Mechanism A, imputed-floor data quality) |
| class_mix proxy | no |
| Census floor-area benchmark | 377 Mm2 (census/EUBUCCO 0.57) |
| Hotmaps 2015 benchmark | 71.98 TWh |
| **Bottom-up result** | **59.5 TWh** (-17.4 % vs Hotmaps, ACC) |

Applied corrections: EUBUCCO area_correction 0.57 (imputed-floor over-count).

**Insight (2026-05-25):** Hungary lands at -17.4 % (ACC) via an `eubucco.area_correction` 0.57 (KSH 2022 census). The original +38.5 % gap was shown by per-m2 arithmetic to be an **area** over-count, not a DE-proxy intensity problem (the model's 150 kWh/m2 is below the Hotmaps-implied 191). The BME-direct typology switch remains an optional per-archetype refinement, not required for reconciliation.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 56% · oil 1% · biomass 30% · resistance 3% · heat pump (air 1% + ground 0%) · district heat 9%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €70 | €80 | €84 |
| Heat pump (air) | €49 | €47 | €36 |
| Heat pump (ground) | €47 | €44 | €33 |
| Hydrogen boiler (CENTRAL) | €285 | €145 | €92 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 34% | 12% | 1% | 10% | 39% |
| Stated Policies | 40% | 14% | 5% | 9% | 27% |
| Net Zero | 49% | 18% | 4% | 15% | 9% |
| H2 Push | 42% | 16% | 8% | 15% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €2.7bn · Stated Policies €4.0bn · Net Zero €5.4bn · H2 Push €5.0bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 68% · district heat 32% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 20%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 28%, stock turnover 5.2%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.14**, range [0.86–1.38] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 59 (59 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 66 [64–74], new-build 84 [74–99] (central [low–high]); across the delivered-H2 supply band 59 [44–72].

<!-- /COUNTRY_MODEL_UPDATE -->
