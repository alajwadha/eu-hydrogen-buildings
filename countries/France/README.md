# France (FR)

> **RQ1 relevance:** Cleanest large-country grid in Europe (nuclear-dominated). Strongest case for heat pump dominance economically. Early policy mover — gas banned in new single-family homes since 2022. MaPrimeRénov' is one of Europe's most generous subsidy schemes.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €130/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €266/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 80 gCO₂/kWh | EMBER 2024 (nuclear-dominant) |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 60% of buildings | Policy.py (model) |
| Heat pump SCOP (air-source, 2025) | 3.00 | Hotmaps HDD; EHPA |
| Annual heating hours | 1,857/year | Hotmaps |
| Electricity share of residential heating | ~41% | Statista 2018 |
| Gas share of residential heating | ~33% | ADEME 2015 |
| HP sales 2024 | ~290,000 units | EHPA |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 515 TWh useful heat.

**Model trajectory (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~515 TWh | baseline |
| 2030 | ~485 TWh | −6% |
| 2040 | ~415 TWh | −19% |
| 2050 | ~360 TWh | −30% |

France has moderate heating hours (warmer than Germany) but a large dwelling stock. Heat demand reduction is gradual due to limited renovation rates historically.

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| New-build fossil ban (SFH) | 2022 | Gas/oil banned in new single-family homes (RE2020 thermal regulation) |
| New-build fossil ban (MFH) | 2025 | Extended to multi-family buildings |
| Replacement fossil ban | 2025 | Oil boilers cannot be replaced with new oil systems |
| HP mandate effective | 2025 | RE2020 requires renewable heating |
| Fossil subsidies end | 2025 | MaPrimeRénov' no longer covers new gas boilers |
| Full fossil phase-out | 2040 | National Low-Carbon Strategy (SNBC) |
| ETS2 launches | 2027 | EU-wide |

**Key policy context:** France was among the most proactive EU states on boiler phase-out. The RE2020 thermal regulation (2022) effectively banned new gas heating in single-family homes by setting strict carbon emission caps that gas cannot meet. Apartment buildings followed in 2025. The MaPrimeRénov' subsidy scheme provides up to €15,000 for low-income households installing heat pumps.

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario:

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €221/MWh | €220/MWh | €182/MWh |
| Heat pump (air) | €117/MWh | €108/MWh | €78/MWh |
| Heat pump (ground) | €102/MWh | €95/MWh | €71/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €317/MWh | €235/MWh | €142/MWh |

> **Labour-cost adjustment applied:** Country multiplier **1.30** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights:**
- France has one of the largest HP-gas gaps: HP air €114 vs gas €214 = €100/MWh advantage
- This is driven by France's clean grid (low electricity carbon adder for HP) combined with high residential gas prices
- Hydrogen boiler stays €100+/MWh above HP even in 2050 — no economic case for H₂ in French buildings

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 3.5M | 9 |
| Multi-family house (MFH) | 9.0M | 26 |
| Other / mixed | (model over-count) | 480 |

**Note:** France has approximately 37M dwellings nationally (INSEE). Single-family homes are predominant in rural and peri-urban areas; multi-family stock concentrates in Paris and other cities.

**HP/DH feasibility (provisional):** SFH HP=0.90, MFH HP=0.50, SFH DH=0.30, MFH DH=0.80

---

## EUBUCCO building-stock build (bottom-up heat demand)

Independent bottom-up estimate from the country-build pipeline (EUBUCCO v0.2 +
TABULA-FR). Method: `literature/country_build_methodology.md`.

**Stock classified — 52,610,604 EUBUCCO buildings:**

| Class | Buildings | Heated floor area | Heat demand |
|---|--:|--:|--:|
| SFH | 21.79M | 2.67 bn m² | 372.0 TWh |
| MFH_LOW | 2.43M | 1.28 bn m² | 154.1 TWh |
| MFH_HIGH | 0.17M | 0.45 bn m² | 47.7 TWh |
| NON_RESIDENTIAL | 28.23M | — (out of scope) | — |
| **Residential total** | **24.38M** | **4.40 bn m²** | **573.8 TWh** |

**Reconciliation (residential space heating + DHW):**

| Source | TWh/yr | vs bottom-up |
|---|--:|--:|
| **Bottom-up (this build)** | **573.8** | — |
| Hotmaps 2015 | 515.1 | **+11.4 %** |
| EU BSO 2020 (implied) | 744.9 | −23 % |
| Odyssee-Mure 2017 | 310.0 | +85 % |

**Insights:**
- **In-band.** +11.4 % vs Hotmaps is inside the ±25 % target *and* the tighter
  ±15 % "consistent" tier. France is research-quality.
- **Old stock dominates.** Pre-1945 buildings alone are ~236 TWh — ~41 % of
  total demand — the clear retrofit / heat-pump priority cohort.
- **Genuinely per-vintage.** 72 % of residential buildings have a EUBUCCO
  construction year, so the per-cohort TABULA intensities actually drive the
  result (contrast Luxembourg, ~0 %).
- **The floors fix mattered.** Using EUBUCCO's native roof-aware `floors`
  column instead of `round(height/3 m)` cut the estimate 651 → 574 TWh by
  removing a ~40 % floor over-count.
- **Residual gap.** Residential heated area (4.40 bn m²) still exceeds the
  national figure (~2.8–3.4 bn m²) — EUBUCCO counts outbuildings as buildings;
  mean intensity 130 kWh/m² vs Hotmaps-implied 117 (+11 %). Documented, not a
  blocker.

---

## Current heating mix (residential, ~2021)

| Energy source | Share | Notes |
|---|---|---|
| Electricity (direct + HP) | ~41% | Direct electric resistance still common in new builds |
| Natural gas | ~33% | ADEME 2015; declining |
| Heating oil (fioul) | ~14% | Falling rapidly under replacement ban |
| Wood/biomass | ~3% | Significant in rural areas, especially South-West |
| District heating | ~6% | Concentrated in Paris (CPCU) and Lyon |

France's high electricity share is partly direct resistance heating (legacy), which is much less efficient than HP. Transitioning electric resistance to heat pumps is a major efficiency opportunity.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 80 | EMBER 2024 — among the cleanest grids in Europe |
| 2030 | 50 | EEA — nuclear dominant, renewables growing |
| 2040 | 20 | Renewables expansion |
| 2050 | 8 | Near-zero |

**Implication:** French heat pumps have very low scope 2 emissions (~25 gCO₂/kWh of useful heat at COP 3). Substantially lower than gas boilers (220 gCO₂/kWh useful) from day one.

---

## Renewable potential

Solar PV (2024): ~22 GW installed (modest given the climate). Wind: ~22 GW. Nuclear: ~62 GW capacity (~70% of electricity generation). Hydro: ~26 GW.

France's grid is already very low-carbon; renewable expansion is more about resilience than CO₂ reduction.

---

## District heating context

- DH supplies ~6% of residential heating (lower than Germany; much lower than Sweden).
- Largest networks: CPCU (Paris, ~500k connections), Dalkia (Lyon, Marseille), ENGIE Solutions.
- Current fuel mix (2023): natural gas 31%, energy recovery (waste/CHP) 28%, biomass 27%, geothermal 6%, other 8%. Source: SNCU 2024.
- Renewable share of DH heat in 2023: 66.5%.
- Expansion plans: Fonds Chaleur programme funds DH expansion in mid-size cities; target +1.4 GW renewable DH capacity by 2030.

---

## Key actors

**Regulators / policy makers:**
- Ministère de la Transition écologique
- ADEME (French Environment and Energy Management Agency) — funds Fonds Chaleur
- CRE (Commission de Régulation de l'Énergie)

**Utilities:**
- EDF (electricity, nuclear-dominant)
- Engie (gas, multi-energy)
- Dalkia (DH operator, subsidiary of EDF)
- CPCU (Paris DH)

**Heat pump manufacturers (active in FR):**
- Atlantic (French, leads domestic market), De Dietrich (acquired by BDR), Daikin, Mitsubishi Electric

---

## National programmes

| Programme | Detail |
|---|---|
| **MaPrimeRénov'** | Up to €15,000 grants for HP installation; income-tiered |
| **Coup de Pouce Chauffage** | Premium for fuel-poor households switching from oil/gas |
| **CEE (Certificats d'Économies d'Énergie)** | Energy savings obligation scheme; utilities subsidise installations |
| **RE2020** | Thermal regulation banning gas in new single-family homes (2022) and multi-family (2025) |
| **Fonds Chaleur** | ADEME programme funding renewable heat (DH expansion, biomass, geothermal) |
| **Ma Prime Renov' Sérénité** | Comprehensive renovation grants for low-income households |

---

## Risk flags

- **Direct electric resistance heating legacy**: 31% of homes use direct electric heating (radiators), which is much less efficient than HP but cheaper to install. Transition resistance.
- **Apartment building heat pump challenges**: Dense Parisian stock not well-suited to air-source HP (noise, space). Most decarbonisation in MFH will need to come via DH or ground-source HP.
- **Nuclear-renewables tension**: France's grid plan relies on extending nuclear life and building new EPR2 reactors; delays could push residential electricity prices higher.
- **Gas industry lobby for biomethane**: Strong push to keep gas grid via renewable gas (biomethane); supply realistically limited to 1–2M homes.
- **MaPrimeRénov' funding cuts**: 2024 reductions in subsidy generosity hit HP sales.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 23% | 33% | 0% | 6% | 3% |
| 2030 | 40% | 0%* | 0% | 18% | 39% |
| 2050 | 49% | 0% | 7% | 16% | 26% |

*Gas drops to zero post-ban; real-world transition slower.

---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 515.1 TWh  
**NUTS coverage:** 9 NUTS1 · 27 NUTS2 · 101 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `FR1` | Ile-de-France | 104.65 | 20.3% | 37,702,089 |
| `FR2` | FR2 | 86.39 | 16.8% | 0 |
| `FR5` | FR5 | 65.31 | 12.7% | 0 |
| `FR7` | FR7 | 63.21 | 12.3% | 0 |
| `FR8` | FR8 | 61.95 | 12.0% | 0 |
| `FR6` | FR6 | 53.57 | 10.4% | 0 |
| `FR4` | FR4 | 42.80 | 8.3% | 0 |
| `FR3` | FR3 | 31.03 | 6.0% | 0 |
| `FRA` | FRA | 6.21 | 1.2% | 0 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `FR10` | Ile-de-France | 104.65 | 20.3% | 37,702,089 |
| `FR71` | Rhône-Alpes | 50.62 | 9.8% | 0 |
| `FR82` | Provence-Alpes-Côte d'Azur | 39.44 | 7.7% | 0 |
| `FR30` | FR30 | 31.03 | 6.0% | 0 |
| `FR51` | FR51 | 26.83 | 5.2% | 0 |
| `FR52` | FR52 | 24.54 | 4.8% | 0 |
| `FR61` | FR61 | 24.16 | 4.7% | 0 |
| `FR62` | FR62 | 22.83 | 4.4% | 0 |
| `FR81` | FR81 | 20.56 | 4.0% | 0 |
| `FR24` | FR24 | 20.47 | 4.0% | 0 |
| — | (Other 17 regions) | 150.00 | 29.1% | 0 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/FR.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.

---

## Sources

See [sources.md](sources.md).

## EUBUCCO bottom-up heat demand build (build group proof-of-concept)

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/fr.yaml`; methodology: `literature/france/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 22 NUTS2 / 96 NUTS3 |
| TABULA typology | FR (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.6822 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 3460 Mm2 (census/EUBUCCO 0.79) |
| Hotmaps 2015 benchmark | 515.1 TWh |
| **Bottom-up result** | **573.8 TWh** (+11.4 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** France is the proof-of-concept country and the **only matrix VERIFIED to reproduce the official `tabula-calculator.xlsx` exactly**. Its +11.4 % reconciliation therefore rests on first-principles TABULA net q_h_nd with no synthesis uncertainty -- the cleanest provenance in the build.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 33% · oil 11% · biomass 18% · resistance 15% · heat pump (air 16% + ground 1%) · district heat 4%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €191 | €191 | €155 |
| Heat pump (air) | €105 | €99 | €79 |
| Heat pump (ground) | €101 | €94 | €71 |
| Hydrogen boiler (CENTRAL) | €294 | €160 | €107 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 36% | 13% | 2% | 9% | 39% |
| Stated Policies | 43% | 14% | 6% | 9% | 27% |
| Net Zero | 54% | 22% | 4% | 10% | 9% |
| H2 Push | 46% | 18% | 9% | 10% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Stated Policies, Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **27%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €24.7bn · Stated Policies €35.0bn · Net Zero €49.4bn · H2 Push €47.8bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 66% · district heat 34% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 15%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 38%, stock turnover 6.3%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.09**, range [0.83–1.27] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 37 (37 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 44 [42–51], new-build 61 [51–76] (central [low–high]); across the delivered-H2 supply band 37 [23–47].

<!-- /COUNTRY_MODEL_UPDATE -->
