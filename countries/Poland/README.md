# Poland (PL)

> **RQ1 relevance:** Coal-dominated grid (600 gCO₂/kWh in 2025 — highest of the 7 countries). Largest air-pollution crisis in EU. Czyste Powietrze (Clean Air) is Europe's largest residential heating replacement scheme (€22.5bn budget). HP economic case weakened by coal-heavy grid in near term.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €80/MWh | Eurostat nrg_pc_202 (lowest of 7) |
| Residential electricity price (H1 2025) | €300/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 600 gCO₂/kWh | EMBER 2024 — highest of 7 |
| Grid CO₂ intensity 2050 | 30 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 50% of buildings | Policy.py |
| Heat pump SCOP (air-source, 2025) | 2.76 | Hotmaps (cold, continental climate) |
| Annual heating hours | 2,643/year | Hotmaps (2nd coldest after SE) |
| Residential energy from coal/solid fuels | ~20.6% | World Bank |
| Buildings using solid fuel boilers | ~2M+ "high-emission" units | Clean Air Fund |
| HP installations in 2024 | Market collapsed in 2023 after subsidy uncertainty | Notes |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 258 TWh useful heat.

**Model trajectory (historical pre-June-2026 run; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~258 TWh | baseline |
| 2030 | ~245 TWh | −5% |
| 2040 | ~210 TWh | −19% |
| 2050 | ~180 TWh | −30% |

Cold winters, large stock, high heat demand per dwelling. Poor building envelope insulation in pre-1990 housing increases demand.

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| Fossil subsidies end | 2025 | Czyste Powietrze excludes new coal boilers from 2022 |
| New-build fossil ban | 2030 | Slow timeline — protests against rapid phase-out |
| Replacement fossil ban | 2040 | Slowest of the 7 countries |
| HP mandate effective | 2040 | Tied to replacement ban |
| Full fossil phase-out | 2040 | Aligned with replacement ban |
| ETS2 launches | 2027 | EU-wide; Poland challenged €149/t projections |

**Key policy context:** Poland is constrained by coal dependency (still ~60% of electricity generation in 2024) and lower household incomes. Political resistance to rapid ETS2 — Poland protested EU price projections of €149/tCO₂ by 2030 as unaffordable. The Czyste Powietrze scheme is the primary policy lever: subsidies of up to 100% for low-income households replacing high-emission boilers.

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario:

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €136/MWh | €141/MWh | €124/MWh |
| Heat pump (air) | €136/MWh | €131/MWh | €86/MWh |
| Heat pump (ground) | €111/MWh | €108/MWh | €74/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €272/MWh | €192/MWh | €105/MWh |

> **Labour-cost adjustment applied:** Country multiplier **0.58** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights:**
- Poland is the **only country** in the 7 where HP and gas are nearly tied in 2025: HP air €139 vs gas €142 (€3/MWh advantage)
- Lower gas prices (€80/MWh) reflect domestic gas + subsidies; lower than EU average
- Cold climate gives lower COP (2.76) which raises HP LCOH
- Coal-heavy grid means HP carbon performance is actually *worse* than gas boiler in 2025 (600 g/kWh × 0.33 = 200 vs 220 for gas). Crossover after grid decarbonisation in early 2030s.

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 8.9M | 24 |
| Multi-family house (MFH) | 11.1M | 28 |
| Other / mixed | (model over-count) | 206 |

Poland has ~14.5M dwellings nationally (GUS — Polish Statistical Office). Half are single-family homes. About 2M+ households still use polluting solid-fuel boilers (coal, wet wood, refuse).

**HP/DH feasibility:** SFH HP=0.90, MFH HP=0.50, SFH DH=0.30, MFH DH=0.80

---

## Current heating mix (residential, ~2023)

| Energy source | Share | Notes |
|---|---|---|
| Coal/lignite (incl. polluting boilers) | ~30% | World Bank: ~20% energy from solid fossil |
| District heating | ~24% | High share in apartment blocks — Soviet-era infrastructure |
| Natural gas | ~25% | Concentrated in urban areas |
| Biomass (wood) | ~15% | Often "polluting" mixed with refuse |
| Heat pumps + electric | ~5% | Growing but coal-dominant grid limits CO₂ benefit |

Polish residential heating is structurally distinct: dominated by either Soviet-era apartment-block DH (in cities) or single-family solid-fuel boilers (in countryside).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 600 | Coal ~60% of generation |
| 2030 | 350 | Coal exit accelerating; gas + renewables filling gap |
| 2040 | 100 | |
| 2050 | 30 | Late but reached |

**Implication:** Polish heat pumps are NOT carbon-effective in 2025. At grid intensity 600 g/kWh and COP 2.76, scope 2 emissions ~217 gCO₂/MWh useful — virtually identical to a gas boiler. Crossover only after grid decarbonises substantially (~2032 based on trajectory).

---

## Renewable potential

Solar PV: ~17 GW installed (rapid growth from 2020). Wind: ~9 GW onshore, ~6 GW offshore Baltic planned. Coal exit timeline: 2049 government, 2030 NGO target.

Poland's offshore wind in the Baltic is the most strategic resource. As wind comes online (10+ GW by 2030), grid intensity will fall.

---

## District heating context

- DH supplies ~24% of residential heating — second highest among the 7 (after Sweden).
- ~3,000 DH systems, concentrated in major cities. Total piping: ~22,000 km.
- Fuel mix: hard coal ~70%, biomass ~10%, gas ~10%, waste/other ~10%.
- Many systems are old (1960s–80s) with high losses (15–25%). Need major investment to align with EU Energy Efficiency Directive (efficient DH criteria).
- Government targets: convert DH to renewable/efficient via Modernizing Infrastructure programme.

---

## Key actors

**Regulators / policy makers:**
- Ministry of Climate and Environment (oversees Czyste Powietrze)
- National Fund for Environmental Protection and Water Management (NFOŚiGW) — administers Czyste Powietrze
- URE (energy regulator)

**Utilities:**
- PGE (state-owned, largest electricity producer)
- PGNiG (gas, merged into Orlen in 2022)
- Tauron, Enea (regional utilities)

**District heating operators (largest):**
- Veolia (Warsaw, multiple cities)
- PGE Energia Ciepła
- Fortum (Częstochowa)

**Heat pump market:**
- Mostly imported (Daikin, Mitsubishi, NIBE, Viessmann, Panasonic)
- 2025 Czyste Powietrze update requires EU/EFTA-manufactured equipment — major change

---

## National programmes

| Programme | Detail |
|---|---|
| **Czyste Powietrze (Clean Air)** | Largest: €22.5bn budget 2018–2029. Subsidies up to PLN 135,000 (€31k) for highest-need households. Now requires equipment from EU/EFTA. |
| **Moje Ciepło (My Heat)** | Up to PLN 21,000 (€4,800) for HP in new energy-efficient homes |
| **Mój Prąd 6.0 (My Electricity)** | PV + battery only (HP removed from coverage 2024) |
| **Stop Smog** | Commune-level programme for energy-poor households; subsidies up to PLN 53,000 |
| **STOP COAL** | Phase-out plan for solid-fuel boilers; smog-control resolutions in major cities |

---

## Risk flags

- **Grid carbon intensity in 2020s**: HPs in Poland actually have similar carbon to gas boilers until ~2032. Premature electrification may not yield CO₂ benefits initially.
- **Energy poverty**: 20%+ of Polish households at risk of energy poverty. ETS2 cost pass-through politically difficult.
- **Just Transition Fund dependency**: Coal regions (Silesia) need transition support. EU funds central to feasibility.
- **EU manufacturer requirement (2025 Czyste Powietrze rule)**: Excludes Asian HP brands from subsidy eligibility — could shrink supply / raise prices.
- **HP market collapse 2023–24**: Sales dropped sharply after subsidy reform; consumer trust damaged.
- **Coal lobby influence**: Strong political coal constituency in Silesia.
- **DH infrastructure renewal**: Most networks need major capex; risk of stranded assets if customers exit faster than upgrades.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 5% | 25% | 0% | 24% | 15% |
| 2030 | 20% | 36% | 0% | 13% | 28% |
| 2050 | 48% | 0% | 7% | 16% | 26% |

Poland's 2030 retains significant gas share (36%) reflecting delayed replacement ban (2040). Coal/solid fuel share assumed to fall faster than gas.

---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 257.9 TWh  
**NUTS coverage:** 6 NUTS1 · 16 NUTS2 · 72 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `PL1` | PL1 | 56.26 | 21.8% | 0 |
| `PL2` | Makroregion południowy | 53.28 | 20.7% | 19,799,856 |
| `PL3` | PL3 | 45.74 | 17.7% | 0 |
| `PL4` | Makroregion północno-zachodni | 40.37 | 15.7% | 15,579,717 |
| `PL6` | Makroregion północny | 35.84 | 13.9% | 14,487,551 |
| `PL5` | Makroregion południowo-zachodni | 26.44 | 10.3% | 10,149,367 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `PL12` | PL12 | 38.95 | 15.1% | 0 |
| `PL22` | Śląskie | 30.70 | 11.9% | 11,605,885 |
| `PL41` | Wielkopolskie | 23.16 | 9.0% | 8,685,894 |
| `PL21` | Małopolskie | 22.57 | 8.8% | 8,193,971 |
| `PL51` | Dolnośląskie | 19.31 | 7.5% | 7,765,237 |
| `PL11` | PL11 | 17.31 | 6.7% | 0 |
| `PL31` | PL31 | 15.06 | 5.8% | 0 |
| `PL63` | Pomorskie | 14.23 | 5.5% | 5,940,648 |
| `PL32` | PL32 | 13.88 | 5.4% | 0 |
| `PL61` | Kujawsko-pomorskie | 12.88 | 5.0% | 5,084,813 |
| — | (Other 6 regions) | 49.88 | 19.3% | 12,740,043 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/PL.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.

---

## Sources

See [sources.md](sources.md).

## EUBUCCO bottom-up heat demand build (build group 4 (Visegrad))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/pl.yaml`; methodology: `literature/poland/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 17 NUTS2 / 73 NUTS3 |
| TABULA typology | PL (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.912 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 1139 Mm2 (census/EUBUCCO 0.66) |
| Hotmaps 2015 benchmark | 257.93 TWh |
| **Bottom-up result** | **279.9 TWh** (+8.5 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Poland reconciles at +8.5 % on the NAPE EK-derived typology (internally consistent per verification). PL is also the proxy source for the three Baltic states; the EK->net derivation carries the documented Polish ~15-20 % uncertainty, an upstream-source property flagged in the matrix header.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 16% · oil 26% · biomass 22% · resistance 1% · heat pump (air 3% + ground 0%) · district heat 32%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €121 | €126 | €111 |
| Heat pump (air) | €115 | €113 | €86 |
| Heat pump (ground) | €104 | €101 | €74 |
| Hydrogen boiler (CENTRAL) | €263 | €134 | €85 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 35% | 12% | 2% | 11% | 39% |
| Stated Policies | 43% | 13% | 6% | 10% | 27% |
| Net Zero | 52% | 19% | 4% | 14% | 9% |
| H2 Push | 46% | 15% | 8% | 14% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **12%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €7.6bn · Stated Policies €10.9bn · Net Zero €11.9bn · H2 Push €12.6bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 68% · district heat 32% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 15%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 34%, stock turnover 5.9%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.05**, range [0.78–1.34] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 11 (11 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 18 [15–24], new-build 33 [24–46] (central [low–high]); across the delivered-H2 supply band 11 [-4–27].

<!-- /COUNTRY_MODEL_UPDATE -->
