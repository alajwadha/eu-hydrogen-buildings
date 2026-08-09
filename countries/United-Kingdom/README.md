# United Kingdom (UK)

> **RQ relevance:** Future Homes Standard (2025) bans gas boilers in new builds only. **Critical update Jan 2025: Labour govt SCRAPPED total gas boiler ban for existing homes** (was 2035 target). HP sales +56% in 2024 due to Boiler Upgrade Scheme; further +27% in 2025. ETS2 NOT directly applicable (post-Brexit UK ETS separate). 85% gas grid coverage — highest in 22.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €120/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €280/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 180 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 85% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 3.0 | Hotmaps HDD; EHPA |
| Annual heating hours | 2000/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2025 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2035 |
| Hp Mandate Year | 2030 |


**Context:** Future Homes Standard (2025): fossil fuel heating banned in new builds. Gas boiler ban in new builds pushed to 2035 (from 2025 under Sunak). Boiler Upgrade Scheme: £7,500 grant for ASHP/GSHP. EHPA (Nov 2025): UK likely to end fossil fuel boilers in new buildings from 2026.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €201 | €201 | €168 |
| Heat pump (air) | €120 | €110 | €79 |
| Heat pump (ground) | €102 | €95 | €70 |
| H₂ boiler (CENTRAL) | €304 | €222 | €131 |

> **Labour-cost adjustment applied:** Country multiplier **1.10** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 135 | 364.31 |
| MFH_HIGH | 37 | 101.46 |
| OTHER | 0 | 1.97 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** Gas ~75% | Oil ~5% | Electricity (incl HP) ~10% | District heating ~3% | Biomass/solid fuel ~7%

~24M homes on gas (vast majority). ~865k oil-heated (mostly rural England/NI/Scotland). DH limited. Strong gas grid coverage and culture.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 180 |
| 2030 | 90 |
| 2040 | 30 |
| 2050 | 8 |

---

## District heating context

**Share:** ~3% of residential heating.

Limited compared to peers. Major networks: Sheffield, Birmingham, London (Bunhill, Olympic Park). Heat Networks Investment Project (~£320M). Growing in new urban developments.

---

## Key actors

Utilities: British Gas (Centrica), EDF Energy, Octopus, SSE. Heat pump market: Daikin, Mitsubishi, Vaillant, Worcester Bosch. Octopus Energy — major installer (Octopus Heat Pumps).

---

## National programmes

Boiler Upgrade Scheme — £7,500 per HP. Warm Homes Plan (from 2025). Great British Insulation Scheme. Future Homes Standard 2025.

**Subsidies:** Boiler Upgrade Scheme (BUS): £7,500 per HP. ECO4 obligation scheme. Warm Homes Plan launching 2025.

---

## Risk flags

- 2035 gas boiler ban for existing homes SCRAPPED (Jan 2025) — model overstates UK ambition.
- Hydrogen-blend ready boilers (20% H2) now standard — supports H2 lobby narrative.
- Outside EU ETS2 — separate UK ETS, different price trajectory.
- BUS uptake limited by upfront cost — only ~30k claims/year.
- Heat pump installer shortage acute.
- Hydrogen village trial (Whitby) was cancelled 2023 — public opposition; signal that H2 in buildings face headwinds.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP | Gas/Oil | H₂ | DH | Biomass |
|---|---|---|---|---|---|
| 2025 | 20% | 40% | 0% | 13% | 25% |
| 2030 | 27% | 36% | 0% | 12% | 22% |
| 2050 | 56% | 0% | 6% | 16% | 19% |


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 467.7 TWh  
**NUTS coverage:** 12 NUTS1 · 42 NUTS2 · 173 NUTS3 regions (NUTS 2016)

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `UKJ` | South East (England) | 61.66 | 13.2% | 21 |
| `UKI` | London | 53.33 | 11.4% | 21 |
| `UKD` | North West (England) | 52.59 | 11.2% | 20 |
| `UKM` | Scotland | 46.95 | 10.0% | 23 |
| `UKH` | East of England | 41.99 | 9.0% | 15 |
| `UKG` | West Midlands (England) | 41.26 | 8.8% | 13 |
| `UKE` | Yorkshire and the Humber | 39.85 | 8.5% | 10 |
| `UKK` | South West (England) | 39.07 | 8.4% | 11 |
| `UKF` | East Midlands (England) | 33.65 | 7.2% | 10 |
| `UKL` | Wales | 24.49 | 5.2% | 11 |
| `UKC` | North East (England) | 20.53 | 4.4% | 6 |
| `UKN` | Northern Ireland | 12.37 | 2.6% | 4 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `UKM3` | UKM3 | 19.77 | 4.2% | 7 |
| `UKG3` | West Midlands | 19.57 | 4.2% | 6 |
| `UKD3` | Greater Manchester | 19.06 | 4.1% | 4 |
| `UKJ1` | Berkshire, Buckinghamshire and Oxfordshire | 18.81 | 4.0% | 4 |
| `UKJ2` | Surrey, East and West Sussex | 18.66 | 4.0% | 5 |
| `UKM2` | UKM2 | 18.20 | 3.9% | 7 |
| `UKK1` | Gloucestershire, Wiltshire and Bristol/Bath area | 17.88 | 3.8% | 4 |
| `UKH1` | East Anglia | 17.64 | 3.8% | 5 |
| `UKE4` | West Yorkshire | 16.93 | 3.6% | 4 |
| `UKF1` | Derbyshire and Nottinghamshire | 15.93 | 3.4% | 5 |
| — | (Other 30 regions) | 285.30 | 61.0% | 114 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/UK.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group 7 (UK + CH; non-EU))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/uk.yaml`; methodology: `literature/united_kingdom/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 42 NUTS2 / 173 NUTS3 |
| TABULA typology | UK (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.7225 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 2750 Mm2 (EUBUCCO 2933 Mm2; ratio 0.94 -- close, no over-count) |
| Hotmaps 2015 benchmark | 467.7 TWh |
| **Bottom-up result** | **368.9 TWh** (-21.1 % vs Hotmaps, ACC) |

Native result, no post-hoc correction applied. UK is NOT an area case: EUBUCCO area (2933 Mm2) is within 6 % of the census (2750 Mm2), so no `area_correction` is warranted (one would push it further below Hotmaps). The -21 % is an intensity-layer under-shoot: the UK build is 99.9 % unknown-cohort, so the result is the stock-weighted CHM/EHS intensity x the 0.7225 retrofit blend (~126 kWh/m2) vs the Hotmaps-implied ~159 kWh/m2. The likely driver is the retrofit blend (0.35/0.45/0.20) over-discounting the UK's large un-retrofitted solid-wall stock; within the +/-25 % ACC band, so left native. A retrofit-share revisit (raising the "original" share) is the candidate refinement.

**Insight (2026-05-25):** The United Kingdom lands at -21.1 % (ACC) on the direct Cambridge Housing Model / EHS typology. It is **NOT an area case** -- EUBUCCO area (2933 Mm2) matches the census (2750 Mm2) within 6 %, so no area_correction is applied. The under-shoot is intensity-layer: the build is 99.9 % unknown-cohort, so it runs on the stock-weighted CHM/EHS x 0.7225 retrofit blend (~126 kWh/m2) vs the Hotmaps-implied ~159; the retrofit blend likely over-discounts the un-retrofitted solid-wall stock. Within ACC band -> left native; a retrofit-share revisit is the candidate refinement.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 80% · oil 5% · biomass 2% · resistance 9% · heat pump (air 2% + ground 0%) · district heat 2%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €131 | €136 | €120 |
| Heat pump (air) | €115 | €108 | €86 |
| Heat pump (ground) | €107 | €99 | €75 |
| Hydrogen boiler (CENTRAL) | €228 | €125 | €85 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 36% | 13% | 2% | 8% | 39% |
| Stated Policies | 44% | 14% | 6% | 8% | 27% |
| Net Zero | 53% | 24% | 4% | 9% | 9% |
| H2 Push | 47% | 20% | 8% | 9% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **25%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 3 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €26.9bn · Stated Policies €32.6bn · Net Zero €47.6bn · H2 Push €42.4bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 67% · district heat 31% · H2 2% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 5%, H2-for-buildings ceiling 2050 2%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.83**, range [0.62–1.08] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 10 (10 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 17 [15–23], new-build 31 [23–44] (central [low–high]); across the delivered-H2 supply band 10 [-1–24].

<!-- /COUNTRY_MODEL_UPDATE -->
