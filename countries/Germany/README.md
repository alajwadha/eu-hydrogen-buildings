# Germany (DE)

> **RQ1 relevance:** Largest EU heating market and largest single source of building-sector CO₂. Reference case for hydrogen-vs-heat-pump debate given OIES paper ET29 and the politically contested GEG (Building Energy Act).

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €122/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €384/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 350 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 15 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 75% of buildings | Policy.py (model) |
| Heat pump SCOP (air-source, 2025) | 2.88 | Hotmaps HDD; EHPA |
| Annual heating hours | 2,286/year | Hotmaps |
| Buildings on natural gas | ~50% (9.5M of 19M) | OIES ET29 (2024) |
| Buildings on heating oil | ~32% (6M of 19M) | OIES ET29 (2024) |
| HP sales 2025 (preliminary) | 299,000 units, 48% market share | EHPA Market Data 2025 |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 794 TWh useful heat (residential, all building types).

**Model trajectory (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~790 TWh | baseline |
| 2030 | ~745 TWh | −6% |
| 2040 | ~640 TWh | −19% |
| 2050 | ~535 TWh | −33% |

Germany has the highest absolute heat demand in Europe due to its large building stock and cold winters (2,286 annual heating hours, highest among the seven countries except Sweden).

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| Fossil boiler subsidies end | 2025 | Federal subsidies for new gas/oil boilers ended |
| New-build fossil ban | 2024 | GEG: all new heating systems must use ≥65% renewable energy |
| Replacement fossil ban | 2028 (delayed from 2024) | After GEG public backlash, replacement bans delayed |
| Replacement fossil ban (worst case) | 2035 | Slippage scenario if Wärmeplanung delays |
| Heat pump mandate | 2028 | All new heating systems must meet 65% renewable share |
| Full fossil phase-out | 2040 | National Climate Action Plan target |
| Carbon price (national CO₂ levy on heating fuels) | 2021– | National scheme pending merger with ETS2; €55/t (2025) rising to €65/t (2026) |
| ETS2 launches | 2027 | EU-wide carbon pricing on buildings and road transport |

**Key policy context:** The Gebäudeenergiegesetz (GEG, Building Energy Act) 2024 mandates that all new heating systems use ≥65% renewable energy. Originally to apply from 2024, the law was substantially weakened after public opposition: replacement bans now linked to municipal Wärmeplanung (municipal heating plans), which most municipalities will not complete until 2026–2028. The Wärmeplanung process is the binding mechanism — a building is only required to switch when its municipality completes its plan and designates a heating zone (district heat / hydrogen / heat pump).

**National target:** 6 million heat pumps installed by 2030 (current pace: ~0.3M/yr; on track to miss target by ~1.5M units).

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario (€122/tCO₂ by 2030):

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €200/MWh | €200/MWh | €166/MWh |
| Heat pump (air) | €163/MWh | €152/MWh | €106/MWh |
| Heat pump (ground) | €137/MWh | €128/MWh | €93/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €299/MWh | €218/MWh | €128/MWh |

> **Labour-cost adjustment applied:** Country multiplier **1.30** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights:**
- Air-source heat pump already 18% cheaper than gas boiler at 2025 prices
- ETS2 adds approximately €11/MWh to gas boiler LCOH by 2030 (CENTRAL minus LOW), versus only €3.5/MWh to heat pump LCOH (via grid carbon)
- Hydrogen boiler LCOH stays €60–80/MWh above best heat pump LCOH through 2050 under CENTRAL trajectory
- Only the RAPID hydrogen trajectory (€25/MWh fuel by 2050) brings hydrogen close to parity

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 41.1M | 123 |
| Multi-family house (MFH) | 47.1M | 136 |
| Other / mixed | (over-counted in model) | 534 |

**Note:** The model's `building_stock_nuts3.csv` over-counts dwellings in the OTHER category (commercial + other building types are inflated). Cross-reference with Eurostat Census 2021: Germany has approximately 43M dwellings total. The OIES ET29 paper cites 19M residential buildings with ~9.5M on gas and ~6M on oil.

**HP/DH feasibility scores (provisional, expert judgment — flagged for Abdul):**
- SFH: HP = 0.90, DH = 0.30
- MFH: HP = 0.50, DH = 0.80

---

## Current heating mix (residential, ~2023)

| Energy source | Share | Notes |
|---|---|---|
| Natural gas | ~50% | OIES ET29: 9.5M of 19M buildings |
| Heating oil | ~32% | OIES ET29: 6M buildings |
| District heating | ~8% | OIES ET29: 1.5M buildings |
| Heat pumps + electric | ~5% | Growing rapidly; 299k units sold 2025 |
| Biomass (wood, pellets) | ~5% | Mostly rural |

Heat pumps overtook gas boilers in new sales in 2025: 48% market share vs gas 44%. This is the inflection point — but does not yet translate to stock turnover (gas still dominates installed base).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 350 | EMBER 2024 actuals; gas + remaining coal |
| 2030 | 150 | EEA Fit-for-55 projection; aggressive coal phase-out |
| 2040 | 50 | Renewables-dominant grid |
| 2050 | 15 | Near-zero carbon |

Germany's grid intensity is roughly the EU average and declines steeply. By 2030, heat pump CO₂ performance improves substantially even without further behavioural change.

---

## Renewable potential

Solar PV capacity (2024): ~88 GW installed. Wind: ~70 GW. Renewable share of generation in 2024: ~52%. Plan: 80% renewable electricity by 2030.

**Implication for HP economics:** Increasing wholesale renewable share lowers daytime electricity prices but residential tariffs (which include high grid/levy components) decline more slowly. The "spark spread" (electricity-to-gas price ratio) is currently ~3.1× — at the edge of HP economic viability with COP ~3.

---

## District heating context

- DH supplies ~14% of all heat demand (residential + commercial); 8% of residential buildings.
- Major networks in Berlin, Hamburg, Munich, Leipzig, Cologne.
- Current DH fuel mix: ~40% gas, ~25% CHP biomass/waste, ~20% industrial waste heat, ~15% coal (declining).
- Expansion plans under Wärmeplanung: aim to double DH connections by 2030, prioritising dense urban cores.
- Decarbonisation pathway: large heat pumps + waste heat recovery + biomass + (potentially) hydrogen for peak.

---

## Key actors

**Regulators / policy makers:**
- BMWK (Federal Ministry for Economic Affairs and Climate Action)
- KfW (state development bank, runs heat pump subsidy programmes)
- BAFA (federal office for economic affairs and export control — administers GEG subsidies)
- BNetzA (Federal Network Agency — grid regulation)

**Utilities (largest):**
- E.ON, RWE, EnBW, Vattenfall (multi-energy)
- Stadtwerke (municipal utilities — operate most DH networks)

**Heat pump manufacturers (HQ in DE):**
- Viessmann (acquired by Carrier 2024), Bosch (Buderus), Vaillant, Stiebel Eltron

---

## National programmes

| Programme | Detail |
|---|---|
| **BAFA / KfW heat pump subsidy** | Up to 70% of cost, capped €21,000. Standard rate 30%, +20% bonus for rapid fossil replacement, +5% for natural refrigerants or low-T water sources |
| **BEG (Bundesförderung effiziente Gebäude)** | Renovation grants for energy efficiency upgrades |
| **GEG (Gebäudeenergiegesetz)** | 65% renewable requirement for new heating systems |
| **Wärmeplanung (municipal heat planning)** | Mandatory by 2026 (large cities) / 2028 (small towns); defines DH/HP/H₂ zones |
| **National CO₂ levy** | €55/t in 2025, €65/t in 2026; merges into ETS2 from 2027 |

---

## Risk flags

- **Political backlash on GEG**: The 2024 GEG was so politically toxic it contributed to the collapse of the Scholz coalition. Implementation has been substantially weakened. The current CDU/SPD coalition (from 2025) has signalled further softening.
- **Wärmeplanung delays**: Many municipalities will miss the 2026/2028 deadlines. This delays the binding replacement-ban trigger and slows the transition.
- **Hydrogen industry lobby**: German gas distributors (DVGW) actively promote hydrogen as gas-grid replacement. OIES ET29 notes 95.9% of gas pipelines are H₂-compatible — strong infrastructure lobby for hydrogen pathway.
- **Installer capacity shortage**: ~30k HP installers needed by 2030 vs ~10k available today.
- **Grid bottleneck**: Mass HP deployment increases peak electricity demand by an estimated 30 GW; grid reinforcement underfunded.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 23% | 50% | 0% | 8% | 5% |
| 2030 | 37% | 0%* | 0% | 20% | 40% |
| 2050 | 48% | 0% | 7% | 17% | 26% |

*Gas share drops to zero in the model after replacement ban takes effect — but real-world stock turnover will be slower.

---

---

## EUBUCCO bottom-up heat demand build (build group 1 (DE + Baltics))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/de.yaml`; methodology: `literature/germany/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 38 NUTS2 / 401 NUTS3 |
| TABULA typology | DE (direct) |
| Climate multiplier | 1.0 |
| Retrofit blend factor | 0.783 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 4070 Mm2 (census/EUBUCCO 0.9) |
| Hotmaps 2015 benchmark | 793.7 TWh |
| **Bottom-up result** | **765.8 TWh** (-3.5 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Germany reconciles cleanly (-3.5 %) on the direct IWU typology. Verification (tabula_intensity_verification.md) found the **published IWU TABULA matrix** carries an unphysical SFH age-inversion (1946-70 > pre-1945) and over-stated post-2010 cells. These are **upstream TABULA/IWU data issues, not pipeline errors** -- the model applies the published German typology as-is and discloses the divergence. The reconciliation is robust to them because the mid-cohorts that dominate the German stock are sound.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 51% · oil 21% · biomass 11% · resistance 3% · heat pump (air 5% + ground 0%) · district heat 10%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €174 | €175 | €143 |
| Heat pump (air) | €141 | €134 | €106 |
| Heat pump (ground) | €130 | €121 | €91 |
| Hydrogen boiler (CENTRAL) | €283 | €148 | €97 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 34% | 15% | 2% | 9% | 39% |
| Stated Policies | 42% | 16% | 6% | 9% | 27% |
| Net Zero | 50% | 26% | 4% | 10% | 9% |
| H2 Push | 44% | 21% | 8% | 10% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Stated Policies, Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **34%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €33.0bn · Stated Policies €44.6bn · Net Zero €72.8bn · H2 Push €62.9bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 48% · district heat 52% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 12%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.09**, range [0.82–1.27] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 6 (6 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 11 [9–16], new-build 23 [16–33] (central [low–high]); across the delivered-H2 supply band 6 [-9–15].

<!-- /COUNTRY_MODEL_UPDATE -->
