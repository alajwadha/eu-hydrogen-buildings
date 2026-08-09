# Belgium (BE)

> **RQ relevance:** Three-region federal structure — Flanders, Wallonia, Brussels — each with different boiler ban timetables. Brussels banned gas in new builds 2025; Wallonia postponed in 2024; Flanders banned new gas connections 2025. Highest gas-grid coverage in EU after NL. HP sales +7% in 2025 — restored growth after EU-wide slump.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €115/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €357/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 160 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 65% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 3.0 | Hotmaps HDD; EHPA |
| Annual heating hours | 2071/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2025 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** Fossil fuel heating systems banned in new buildings from 2025. Flanders has separate regional policy.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €204 | €204 | €173 |
| Heat pump (air) | €149 | €138 | €99 |
| Heat pump (ground) | €128 | €119 | €88 |
| H₂ boiler (CENTRAL) | €316 | €234 | €142 |

> **Labour-cost adjustment applied:** Country multiplier **1.60** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 6,972,684 | 22.05 |
| MFH_HIGH | 2,838,995 | 9.6 |
| OTHER | 19,799,534 | 80.2 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~37% | Oil ~37% | HP+electric ~12% | DH ~5% | Biomass ~9%

Wallonia: ~50% homes still on oil. Flanders: 24% on oil. Brussels: 79% on gas (very high). Belgium overall gas + oil dominates.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 160 |
| 2030 | 100 |
| 2040 | 40 |
| 2050 | 8 |

---

## District heating context

**Share:** ~5% of residential heating.

Very limited DH — only some networks in Antwerp, Brussels, university campuses. Below EU average.

---

## Key actors

Utilities: Engie, Eneco. DSO: Fluvius (Flanders). HP brands: Daikin, Mitsubishi, Vaillant, NIBE.

---

## National programmes

Flanders: "Mijn VerbouwPremie" — up to €6,400 for HP. Wallonia: "Primes Habitation". Brussels: subsidies via "Renolution". VAT reduced on HP in new builds.

**Subsidies:** See above — regional schemes.

---

## Risk flags

- Regional fragmentation: 3 different ban regimes complicates national policy assessment.
- Wallonia oil-boiler ban postponed by Energy Minister Cécile Neven in 2024 — "dates not realistic".
- High oil dependency in Wallonia rural areas (off gas grid) — alternatives needed.
- Apartment heat-pump retrofits difficult in dense Brussels stock.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 19% | 37% | 0% | 14% | 29% |
| 2030 | 21% | 35% | 0% | 13% | 27% |
| 2050 | 50% | 0% | 7% | 16% | 25% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 111.8 TWh  
**NUTS coverage:** 3 NUTS1 · 11 NUTS2 · 44 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `BE2` | Vlaams Gewest | 62.35 | 55.7% | 18,013,988 |
| `BE3` | Région wallonne | 35.30 | 31.6% | 7,845,677 |
| `BE1` | Région de Bruxelles-Capitale/Brussels Hoofdstedelijk Gewest | 14.20 | 12.7% | 3,751,548 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `BE21` | Prov. Antwerpen | 17.74 | 15.9% | 5,617,348 |
| `BE10` | Région de Bruxelles-Capitale/ Brussels Hoofdstedelijk Gewest | 14.20 | 12.7% | 3,751,548 |
| `BE23` | Prov. Oost-Vlaanderen | 13.89 | 12.4% | 4,639,177 |
| `BE32` | Prov. Hainaut | 13.01 | 11.6% | 817,210 |
| `BE25` | Prov. West-Vlaanderen | 11.79 | 10.5% | 3,723,211 |
| `BE24` | Prov. Vlaams-Brabant | 11.23 | 10.0% | 3,420,052 |
| `BE33` | Prov. Liège | 10.95 | 9.8% | 3,440,298 |
| `BE22` | Prov. Limburg (BE) | 7.70 | 6.9% | 614,200 |
| `BE35` | Prov. Namur | 4.82 | 4.3% | 1,515,277 |
| `BE31` | Prov. Brabant Wallon | 3.73 | 3.3% | 1,201,987 |
| `BE34` | Prov. Luxembourg (BE) | 2.78 | 2.5% | 870,905 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/BE.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 5 (NW temperate))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/be.yaml`; methodology: `literature/belgium/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 11 NUTS2 / 48 NUTS3 |
| TABULA typology | BE (direct) |
| Climate multiplier | 0.869 (Option B; tabula_reference_hdd = 2900.0) |
| Retrofit blend factor | 0.918 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 660 Mm2 (census/EUBUCCO 0.79) |
| Hotmaps 2015 benchmark | 111.84 TWh |
| **Bottom-up result** | **132.8 TWh** (+18.7 % vs Hotmaps, ACC) |

Applied corrections: Option B reference-HDD correction.

**Insight (2026-05-25):** Belgium lands at +18.7 % (ACC) on the direct VITO typology. Verification against the official `tabula-calculator.xlsx` found the recent cohorts (1991+) **too low** -- our synthesis applied an NZEB decay not present in the published Belgian TABULA. This is an upstream-extraction issue in our BE matrix (documented, current -> recommended values recorded); correcting it would worsen BE slightly but improve LU. Left native pending the coordinated re-extraction.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 60% · oil 23% · biomass 6% · resistance 5% · heat pump (air 3% + ground 0%) · district heat 3%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €172 | €174 | €144 |
| Heat pump (air) | €131 | €124 | €98 |
| Heat pump (ground) | €122 | €114 | €86 |
| Hydrogen boiler (CENTRAL) | €275 | €149 | €101 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 35% | 15% | 2% | 8% | 39% |
| Stated Policies | 42% | 16% | 6% | 8% | 27% |
| Net Zero | 51% | 26% | 4% | 9% | 9% |
| H2 Push | 45% | 22% | 8% | 9% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €9.4bn · Stated Policies €11.4bn · Net Zero €16.4bn · H2 Push €14.9bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 49% · district heat 51% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 10%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.02**, range [0.75–1.27] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 15 (15 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 20 [18–25], new-build 32 [25–43] (central [low–high]); across the delivered-H2 supply band 15 [0–28].

<!-- /COUNTRY_MODEL_UPDATE -->
