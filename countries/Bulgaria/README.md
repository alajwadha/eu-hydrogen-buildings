# Bulgaria (BG)

> **RQ relevance:** High electricity share (51.7%) in residential energy due to widespread direct electric heating. High grid carbon intensity (350 gCO₂/kWh) limits HP carbon benefit in near term. Sofia largest DH system. Lower-income — transition financing key constraint.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €60/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €170/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 350 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 20 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 40% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.91 | Hotmaps HDD; EHPA |
| Annual heating hours | 2071/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2030 |
| Replacement Fossil Ban | 2040 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2040 |


**Context:** 51.7% residential energy from electricity (2023). High electricity carbon intensity — HP benefit limited until grid decarbonises.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €119 | €126 | €117 |
| Heat pump (air) | €81 | €76 | €51 |
| Heat pump (ground) | €67 | €64 | €45 |
| H₂ boiler (CENTRAL) | €278 | €197 | €110 |

> **Labour-cost adjustment applied:** Country multiplier **0.35** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 2,783,860 | 3.96 |
| MFH_HIGH | 3,500,649 | 4.98 |
| OTHER | 12,578,216 | 17.9 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Electricity (direct + HP) ~51% | Biomass ~25% | District heating ~17% | Gas ~5% | Oil <2%

Eurostat 2023: 51.7% electricity in residential energy. Wood heating common in rural areas. Gas use limited to urban centres (Sofia, Plovdiv).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 350 |
| 2030 | 200 |
| 2040 | 80 |
| 2050 | 20 |

---

## District heating context

**Share:** ~17% of residential heating.

Sofia DH (Toplofikatsiya Sofia) — largest in country, ~12 towns/cities with DH. Coal + gas + biomass mix. Soviet-era infrastructure.

---

## Key actors

Utilities: BEH (state holding), CEZ. DH: Toplofikatsiya Sofia, EVN. HP brands: Daikin, Bosch, Mitsubishi.

---

## National programmes

Operational Programme Environment 2021–2027 (EU funds) — building renovation grants. Energy efficiency obligation on electricity suppliers. National Recovery and Resilience Plan funds HP installations.

**Subsidies:** Small market — limited dedicated HP subsidy. 8,000 HPs sold 2024 (EHPA).

---

## Risk flags

- High grid CO₂ (350 g/kWh 2025) — HPs less carbon-effective near term.
- Coal phase-out resistance — Maritsa basin coal complex.
- Energy poverty rate ~33% (highest in EU).
- DH affordability issues — districts losing customers to electric/biomass.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 26.8 TWh  
**NUTS coverage:** 2 NUTS1 · 6 NUTS2 · 28 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `BG4` | Югозападна и Южна централна България | 13.43 | 50.0% | 9,551,488 |
| `BG3` | Северна и Югоизточна България | 13.41 | 50.0% | 9,311,237 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `BG41` | Югозападен | 8.67 | 32.3% | 5,841,385 |
| `BG42` | Южен централен | 4.76 | 17.7% | 3,710,103 |
| `BG34` | Югоизточен | 3.84 | 14.3% | 2,726,851 |
| `BG33` | Североизточен | 3.38 | 12.6% | 2,426,692 |
| `BG31` | Северозападен | 3.18 | 11.8% | 2,055,902 |
| `BG32` | Северен централен | 3.01 | 11.2% | 2,101,792 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/BG.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 6 (Nordic + Balkan))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/bg.yaml`; methodology: `literature/bulgaria/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 6 NUTS2 / 28 NUTS3 |
| TABULA typology | CZ (proxy) |
| Climate multiplier | 0.7647 |
| Retrofit blend factor | 0.9316 |
| comfort_regime deflator | 0.55 |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 347 Mm2 (census/EUBUCCO 0.76) |
| Hotmaps 2015 benchmark | 29.0 TWh |
| **Bottom-up result** | **35.6 TWh** (+22.7 % vs Hotmaps, ACC) |

Applied corrections: comfort_regime deflator 0.55 (intensity layer).

**Insight (2026-05-25):** Bulgaria lands at +22.7 % (ACC) via a `comfort_regime` deflator 0.55 (EU-SILC records the EU's highest under-heating prevalence; BPIE 2016). The deflator is the same intensity-layer mechanism as the Mediterranean cluster, extended on documented under-heating evidence.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 5% · oil 5% · biomass 52% · resistance 18% · heat pump (air 1% + ground 0%) · district heat 19%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €102 | €109 | €101 |
| Heat pump (air) | €70 | €67 | €52 |
| Heat pump (ground) | €65 | €61 | €45 |
| Hydrogen boiler (CENTRAL) | €239 | €125 | €81 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 66% · district heat 34% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 25%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 26%, stock turnover 5.1%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.93**, range [0.71–1.19] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 35 (35 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 44 [41–52], new-build 63 [52–80] (central [low–high]); across the delivered-H2 supply band 35 [23–49].

<!-- /COUNTRY_MODEL_UPDATE -->
