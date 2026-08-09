# Sweden (SE)

> **RQ1 relevance:** District heating dominates (>50% of residential heat). Near-zero residential gas use (<5% grid coverage). Cleanest grid combined with HP-friendly culture — the "completed transition" benchmark for the model. Useful contrast country in the paper to show what success looks like.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €213/MWh | Eurostat nrg_pc_202 — **outlier** (tiny gas market) |
| Residential electricity price (H1 2025) | €200/MWh | Eurostat nrg_pc_204 (lowest of 7) |
| Grid CO₂ intensity 2025 | 45 gCO₂/kWh | EMBER 2024 (hydro+nuclear+wind) |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 5% of buildings | Policy.py — very low |
| Heat pump SCOP (air-source, 2025) | 2.64 | Hotmaps (coldest of 7) |
| Annual heating hours | 3,429/year | Hotmaps — highest |
| District heating share of residential heat | ~50% | EHPA / SEI |
| Electricity share (incl. HP) | ~48% | Eurostat 2023 |
| Fossil fuel share of residential heating | <5% | SEI Policy Brief |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 99 TWh useful heat.

**Model trajectory (historical pre-June-2026 run; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~100 TWh | baseline |
| 2030 | ~95 TWh | −5% |
| 2040 | ~80 TWh | −19% |
| 2050 | ~70 TWh | −30% |

Despite the cold climate, Sweden's heat demand is moderate because the building envelope is well-insulated (highest standards in EU since the 1970s).

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| Fossil subsidies end | 2025 | Long phased out for boilers |
| New-build fossil ban | 2022 | Boverket regulations effectively rule out fossil heating |
| Replacement fossil ban | 2030 | Existing buildings |
| HP mandate effective | 2030 | |
| Full fossil phase-out | 2040 | National 2045 net-zero |
| ETS2 launches | 2027 | EU-wide (limited buildings impact in SE due to electrification) |

**Key policy context:** Sweden completed most of the heating transition between 1970 and 2010 — oil and gas largely replaced by DH and HPs. The current policy focus is on grid stability, optimising existing DH networks, and renewable electricity expansion. Sweden's carbon tax (since 1991) on fossil heating fuels — currently ~SEK 1,400/tCO₂ (≈€125) — pre-dates and substantially exceeds EU ETS2 levels.

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario:

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €282/MWh | €272/MWh | €204/MWh |
| Heat pump (air) | €94/MWh | €87/MWh | €63/MWh |
| Heat pump (ground) | €81/MWh | €75/MWh | €57/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €275/MWh | €195/MWh | €108/MWh |

> **Labour-cost adjustment applied:** Country multiplier **1.35** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights:**
- HP-gas gap is huge (€185/MWh) — but gas is essentially absent so the comparison is academic
- Real cost competition is HP vs DH: both at ~€80–100/MWh in Sweden, very competitive
- Cold climate gives lower COP (2.64) but cheap electricity (€200/MWh — cheapest of the 7) compensates
- Hydrogen has no economic foothold; Sweden's energy strategy uses H₂ for industry (steel) not buildings

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 5.1M | 16 |
| Multi-family house (MFH) | 5.3M | 17 |
| Other / mixed | (model over-count) | 67 |

Sweden has ~4.9M dwellings nationally (SCB — Swedish Statistics Bureau). Roughly equal split single-family / multi-family. Multi-family buildings predominantly DH-connected (85% market share); single-family more HP-oriented (16% DH).

**HP/DH feasibility:** Both very high in Sweden — assume SFH HP=0.95, MFH DH=0.85 (above default)

---

## Current heating mix (residential, ~2023)

| Energy source | Share | Notes |
|---|---|---|
| District heating | ~50% | SEI, EHPA — highest in modelled countries |
| Heat pumps + electric | ~25% | HP dominant in SFH; resistance heating in older homes |
| Direct electricity | ~20% | Falling as HPs replace resistance heating |
| Biomass (wood, pellets) | ~3% | Some rural use |
| Oil + gas | <5% | Effectively phased out |

Sweden's transition is largely complete. The 2025 challenge is fine-tuning: replacing remaining direct electric resistance with HPs (efficiency gain), and decarbonising the marginal DH inputs (mostly biomass/waste already).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 45 | Mix: 45% hydro, 30% nuclear, 17% wind, 7% biomass, 1% gas |
| 2030 | 25 | |
| 2040 | 10 | |
| 2050 | 5 | Near-zero |

Sweden has one of the world's cleanest grids. HP carbon performance excellent across all scenarios.

---

## Renewable potential

Hydro: ~16 GW installed (largely tapped). Wind: ~14 GW onshore + ~1 GW offshore (rapid offshore expansion planned). Solar: ~3 GW (modest, climate-limited). Nuclear: ~7 GW (debate on lifecycle extensions / new build).

Industrial electrification (Hybrit green steel, Northvolt batteries) is increasing electricity demand and creating tension with consumer prices.

---

## District heating context

- DH supplies >50% of total Swedish heat demand — uniquely high in Europe.
- ~500 DH systems across 283 municipalities; 23,000 km of pipes.
- 85% market share in multi-family residential; 16% in single-family.
- DH fuel mix 2024: 46% biomass, 22% waste-to-energy, 11% flue-gas condensation, 8% industrial waste heat, 7% large HPs, 3% grid electricity, 2% fossil, 0.3% peat. Source: Energiföretagen / Wikipedia.
- Major operators: Stockholm Exergi, Göteborg Energi, Eon, Vattenfall, Tekniska Verken (Linköping).
- Renewable share: ~95% of DH input.
- DH integration with large HPs is a key R&D direction (Lygnerud / Lund University).

---

## Key actors

**Regulators / policy makers:**
- Energimyndigheten (Swedish Energy Agency)
- Boverket (National Board of Housing, Building and Planning)
- Naturvårdsverket (Environmental Protection Agency)
- Skatteverket (administers carbon tax)

**Utilities:**
- Vattenfall (state-owned, electricity dominant)
- E.ON Sweden
- Stockholm Exergi (DH, Stockholm — biomass + waste)
- Göteborg Energi (DH, Gothenburg)
- Fortum Värme (DH minority interest)

**Heat pump manufacturers:**
- NIBE (Swedish, largest European HP manufacturer)
- Thermia (also Swedish)
- Bosch, Daikin, Mitsubishi Electric

---

## National programmes

| Programme | Detail |
|---|---|
| **Carbon tax** | SEK 1,400/tCO₂ (~€125), in force since 1991, full rate from 2018 for non-ETS |
| **Klimatklivet** | Climate investment grants for businesses/municipalities |
| **ROT-avdrag** | 50% labour tax deduction on home renovation, can be used for HP installation |
| **HP installation grant** | Up to SEK 30,000 direct grant |
| **Energieffektiviseringsstöd** | Energy efficiency support for buildings |

---

## Risk flags

- **Direct electric resistance heating legacy**: ~20% of homes use resistance heaters. Replacement with HP is the main efficiency frontier.
- **DH market saturation**: Falling DH demand (renovations, mild winters) creates revenue pressure for utilities; competition with HPs in renovations.
- **Industrial electricity demand**: Hybrit, Northvolt may push prices up, hurting HP economics.
- **Eurostat gas price outlier**: €213/MWh reflects very small residential gas market (few customers, high fixed costs). LCOH calculations for gas in SE are nominally large but irrelevant — no installed gas stock to convert.
- **Nuclear policy uncertainty**: Mixed signals on extending vs phasing out — affects grid carbon trajectory.
- **Biomass sustainability**: 46% of DH from biomass; questions on forest carbon accounting per EU RED III.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 25% | 5% | 0% | 50% | 5% |
| 2030 | 40% | 0% | 0% | 18% | 39% |
| 2050 | 50% | 0% | 7% | 16% | 25% |

**Note:** Model's 2030 share substantially shifts shares (DH 50% → 18%) which appears inconsistent with real-world DH inertia. Worth investigating: model may be over-rotating Sweden's stock toward biomass/HP rather than preserving DH dominance. Flagged for Abdul.

---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 99.4 TWh  
**NUTS coverage:** 4 NUTS1 · 9 NUTS2 · 22 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `SE2` | Södra Sverige | 40.87 | 41.1% | 13,558,675 |
| `SE1` | Östra Sverige | 38.38 | 38.6% | 12,376,877 |
| `SE3` | Norra Sverige | 20.16 | 20.3% | 5,490,098 |
| `SEZ` | SEZ | 0.01 | 0.0% | 0 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `SE11` | Stockholm | 22.63 | 22.8% | 7,116,056 |
| `SE23` | Västsverige | 18.94 | 19.0% | 6,258,832 |
| `SE12` | Östra Mellansverige | 15.75 | 15.8% | 5,260,821 |
| `SE22` | Sydsverige | 13.49 | 13.6% | 4,668,786 |
| `SE31` | Norra Mellansverige | 9.42 | 9.5% | 2,698,479 |
| `SE21` | Småland med öarna | 8.44 | 8.5% | 2,631,057 |
| `SE33` | Övre Norrland | 6.24 | 6.3% | 1,609,727 |
| `SE32` | Mellersta Norrland | 4.51 | 4.5% | 1,181,892 |
| `SEZZ` | SEZZ | 0.01 | 0.0% | 0 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/SE.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.

---

## Sources

See [sources.md](sources.md).

## EUBUCCO bottom-up heat demand build (build group 6 (Nordic + Balkan))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/se.yaml`; methodology: `literature/sweden/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 8 NUTS2 / 21 NUTS3 |
| TABULA typology | SE (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.858 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 452 Mm2 (census/EUBUCCO 0.74) |
| Hotmaps 2015 benchmark | 85.0 TWh |
| **Bottom-up result** | **81.8 TWh** (-3.7 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Sweden reconciles at -3.7 % after reverting the Option B over-correction (`tabula_reference_hdd = 5043` national, multiplier 1.0). Verification: the **published Swedish (MdH) brochure** older-SFH rows are ~15-25 % high, with an unresolved net-vs-energianvandning definitional ambiguity -- an upstream-source issue. SE feeds FI and the EE/LT class-mix, so it is the highest-propagation file; the reconciliation nonetheless holds.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 1% · oil 1% · biomass 11% · resistance 9% · heat pump (air 17% + ground 13%) · district heat 48%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €264 | €255 | €187 |
| Heat pump (air) | €84 | €79 | €63 |
| Heat pump (ground) | €78 | €73 | €55 |
| Hydrogen boiler (CENTRAL) | €219 | €113 | €73 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 35% | 12% | 2% | 10% | 39% |
| Stated Policies | 43% | 12% | 6% | 10% | 27% |
| Net Zero | 52% | 21% | 4% | 11% | 9% |
| H2 Push | 45% | 18% | 8% | 11% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **21%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €0.7bn · Stated Policies €1.8bn · Net Zero €2.0bn · H2 Push €2.5bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 66% · district heat 34% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 42%, stock turnover 6.5%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.86**, range [0.63–1.11] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 18 (18 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 21 [20–24], new-build 29 [24–36] (central [low–high]); across the delivered-H2 supply band 18 [5–31].

<!-- /COUNTRY_MODEL_UPDATE -->
