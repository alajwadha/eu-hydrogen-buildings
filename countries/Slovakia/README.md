# Slovakia (SK)

> **RQ relevance:** CEE country — transition pace constrained by income levels and coal/gas heating dependency. Major DH networks (Bratislava, Košice). Veolia significant operator. Geothermal potential. Russian gas dependency via Ukraine transit — pre-2022 ~85%, now diversified via LNG/Norway.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €95/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €250/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 200 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 55% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.79 | Hotmaps HDD; EHPA |
| Annual heating hours | 2500/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2038 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2038 |


**Context:** CEE country — transition pace constrained by income levels and coal/gas heating dependency.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €154 | €157 | €134 |
| Heat pump (air) | €109 | €101 | €72 |
| Heat pump (ground) | €90 | €84 | €62 |
| H₂ boiler (CENTRAL) | €274 | €194 | €107 |

> **Labour-cost adjustment applied:** Country multiplier **0.55** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 2,391,742 | 6.87 |
| MFH_HIGH | 2,072,337 | 6.32 |
| OTHER | 8,987,316 | 26.6 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~37% | District heating ~30% | Biomass ~18% | Electricity (incl HP) ~10% | Oil/coal ~5%

Strong DH in cities. Eastern Slovakia rural areas wood-dominant. Gas dominant in suburban/peri-urban.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 200 |
| 2030 | 100 |
| 2040 | 40 |
| 2050 | 8 |

---

## District heating context

**Share:** ~30% of residential heating.

Veolia (multiple cities), MH Teplárenský holding (state, Žilina, Trnava). Bratislava DH — natural gas + biomass. Košice — biomass + waste heat from US Steel.

---

## Key actors

Utilities: SPP (gas), Slovenské elektrárne. DH: Veolia, MH Teplárenský. HP brands: Daikin, Vaillant, Buderus.

---

## National programmes

Slovenská inovačná a energetická agentúra (SIEA) — Zelená domácnostiam (Green Households) HP grants. EU NRRP.

**Subsidies:** Zelená domácnostiam — €3,400 HP grant. Renovation grants for low-income.

---

## Risk flags

- DH gas dependency — Russian transit historically dominant.
- Coal phase-out in DH affects baseload — supplier diversification needed.
- HP market modest — installer training gap.
- ETS2 cost pass-through politically sensitive.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 39.8 TWh  
**NUTS coverage:** 1 NUTS1 · 4 NUTS2 · 8 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `SK0` | Slovensko | 39.80 | 100.0% | 13,451,395 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `SK02` | Západné Slovensko | 12.61 | 31.7% | 4,720,049 |
| `SK04` | Východné Slovensko | 9.74 | 24.5% | 3,512,554 |
| `SK03` | Stredné Slovensko | 9.47 | 23.8% | 3,256,892 |
| `SK01` | Bratislavský kraj | 7.98 | 20.0% | 1,961,900 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/SK.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 4 (Visegrad))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/sk.yaml`; methodology: `literature/slovakia/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 4 NUTS2 / 8 NUTS3 |
| TABULA typology | CZ (proxy) |
| Climate multiplier | 0.9382 |
| Retrofit blend factor | 0.81 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 157 Mm2 (census/EUBUCCO 0.53) |
| Hotmaps 2015 benchmark | 39.8 TWh |
| **Bottom-up result** | **40.7 TWh** (+2.2 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Slovakia has the tightest Visegrad reconciliation (+2.2 %), using the CZ typology as proxy (shared Czechoslovak 1948-93 building code / panelove domy) plus aggressive SFRB Obnova panel-retrofit shares reflecting one of the EU's highest panel-block thermal-renovation rates.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 45% · oil 2% · biomass 22% · resistance 5% · heat pump (air 4% + ground 0%) · district heat 21%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €138 | €141 | €120 |
| Heat pump (air) | €97 | €92 | €73 |
| Heat pump (ground) | €89 | €83 | €63 |
| Hydrogen boiler (CENTRAL) | €283 | €143 | €90 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 69% · district heat 31% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 20%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 29%, stock turnover 5.4%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.14**, range [0.91–1.35] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 27 (27 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 34 [31–40], new-build 49 [40–62] (central [low–high]); across the delivered-H2 supply band 27 [14–38].

<!-- /COUNTRY_MODEL_UPDATE -->
