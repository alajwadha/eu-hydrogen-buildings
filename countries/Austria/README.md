# Austria (AT)

> **RQ relevance:** EWG (Renewable Heat Act) entered force 29 Feb 2024 — comprehensive ban on gas/oil in new buildings. 95% renewable electricity (2024) — strong HP case. Gas grid moderately developed; 80% of gas historically from Russia → strong post-2022 transition pressure.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €110/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €270/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 120 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 55% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.85 | Hotmaps HDD; EHPA |
| Annual heating hours | 2357/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2020 |
| Replacement Fossil Ban | 2025 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2025 |


**Context:** Austria banned repair of old fossil heating and new installs from 2025. Extended ban from gas only to all fossil fuels as of 2025 (EHPA).

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €183 | €185 | €156 |
| Heat pump (air) | €119 | €110 | €79 |
| Heat pump (ground) | €101 | €94 | €70 |
| H₂ boiler (CENTRAL) | €294 | €213 | €124 |

> **Labour-cost adjustment applied:** Country multiplier **1.20** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 4,132,700 | 12.64 |
| MFH_HIGH | 4,875,516 | 14.09 |
| OTHER | 18,739,652 | 55.64 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~37% | Oil ~17% | District heating ~27% | HP+electric ~12% | Biomass ~7%

Heat output sold via DH represents ~17% of heat provided (IEA Bioenergy 2024). Gas grid dense in urban areas. Direct biomass use ~27% — significant in rural areas.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 120 |
| 2030 | 70 |
| 2040 | 25 |
| 2050 | 5 |

---

## District heating context

**Share:** ~27% of residential heating.

Strong CHP-based district heating (Vienna largest). 80% of DH was fossil-based (2012) — transitioning. Biomass + geothermal growth.

---

## Key actors

Major utilities: Verbund (electricity), Wien Energie (DH), OMV (gas). HP brands: ait-deutschland, Heliotherm, IDM, Vaillant.

---

## National programmes

"Raus aus Öl und Gas" (Out of Oil and Gas) household scheme — up to €7,500 per household. Bundesförderung (federal grant) for HP up to €22,500. Extended via NextGenerationEU funding (€159M additional).

**Subsidies:** AT subsidy: up to 20% grant for new buildings (max €7,500), 35% for retrofit (max €5,000) for ASHP/GSHP, Jan 2023–Dec 2024.

---

## Risk flags

- Heating accounts for 25% of Austrian gas consumption — 80% historically from Russia.
- EWG hydrogen exemption: H2-ready gas boilers still permitted under conditions.
- Renewable Gas Act (EGG) rejected Sep 2024 — biomethane targets uncertain.
- Cantonal/Länder variation in subsidy generosity.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 39% | 0% | 0% | 19% | 40% |
| 2030 | 40% | 0% | 0% | 18% | 39% |
| 2050 | 50% | 0% | 7% | 16% | 25% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 82.4 TWh  
**NUTS coverage:** 3 NUTS1 · 9 NUTS2 · 35 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `AT1` | Ostösterreich | 35.43 | 43.0% | 12,367,722 |
| `AT3` | Westösterreich | 29.71 | 36.1% | 9,751,147 |
| `AT2` | Südösterreich | 17.23 | 20.9% | 5,628,999 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `AT13` | Wien | 16.82 | 20.4% | 6,284,606 |
| `AT12` | Niederösterreich | 15.91 | 19.3% | 5,178,704 |
| `AT31` | Oberösterreich | 13.67 | 16.6% | 4,548,959 |
| `AT22` | Steiermark | 11.74 | 14.3% | 3,864,772 |
| `AT33` | Tirol | 7.13 | 8.7% | 2,301,825 |
| `AT21` | Kärnten | 5.49 | 6.7% | 1,764,227 |
| `AT32` | Salzburg | 5.38 | 6.5% | 1,693,726 |
| `AT34` | Vorarlberg | 3.52 | 4.3% | 1,206,637 |
| `AT11` | Burgenland | 2.71 | 3.3% | 904,412 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/AT.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 5 (NW temperate))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/at.yaml`; methodology: `literature/austria/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 9 NUTS2 / 35 NUTS3 |
| TABULA typology | AT (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.8575 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.575 (Mechanism A, imputed-floor data quality) |
| class_mix proxy | no |
| Census floor-area benchmark | 471 Mm2 (census/EUBUCCO 0.57) |
| Hotmaps 2015 benchmark | 82.36 TWh |
| **Bottom-up result** | **72.1 TWh** (-12.4 % vs Hotmaps, OK) |

Applied corrections: EUBUCCO area_correction 0.575 (imputed-floor over-count).

**Insight (2026-05-25):** Austria reconciles at -12.4 % via an `eubucco.area_correction` 0.575 (Mechanism A: ~7 % observed heights -> imputed-floor over-count; Statistik Austria GWZ 2021). Verification: the **published AEA matrix** has the same SFH age-inversion + post-2010 over-statement as DE -- upstream TABULA data, disclosed; the reconciliation is robust because old/mid cohorts dominate.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 27% · oil 12% · biomass 26% · resistance 4% · heat pump (air 7% + ground 2%) · district heat 21%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €158 | €160 | €132 |
| Heat pump (air) | €104 | €98 | €78 |
| Heat pump (ground) | €96 | €89 | €68 |
| Hydrogen boiler (CENTRAL) | €245 | €129 | €84 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 35% | 12% | 2% | 11% | 39% |
| Stated Policies | 41% | 14% | 6% | 11% | 27% |
| Net Zero | 50% | 20% | 4% | 16% | 9% |
| H2 Push | 43% | 17% | 8% | 15% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €1.1bn · Stated Policies €2.1bn · Net Zero €2.1bn · H2 Push €2.7bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 54% · district heat 46% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 41%, stock turnover 6.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.94**, range [0.70–1.22] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 17 (17 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 21 [20–25], new-build 31 [25–39] (central [low–high]); across the delivered-H2 supply band 17 [4–32].

<!-- /COUNTRY_MODEL_UPDATE -->
