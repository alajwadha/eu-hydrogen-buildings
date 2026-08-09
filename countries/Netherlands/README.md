# Netherlands (NL)

> **RQ1 relevance:** Highest gas dependency in the EU (72.9% residential space heating from gas, Eurostat 2023). Most challenging transition. **Important update:** The 2026 hybrid heat pump mandate was abandoned by the new coalition government in 2024 — significant policy reversal that this model does not yet reflect.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €162/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €280/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 280 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 10 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 90% of buildings | Policy.py — highest in modelled set |
| Heat pump SCOP (air-source, 2025) | 3.00 | Hotmaps |
| Annual heating hours | 2,000/year | Hotmaps |
| Gas share of residential space heating | 72.9% | Eurostat 2023 |
| Individual heat pumps installed (2024) | ~700,000 (1 in 12 homes) | HPT Magazine 2025 |
| HP share in new builds | ~75% | HPT 2025 |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 161 TWh useful heat.

**Model trajectory (historical pre-June-2026 run; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~160 TWh | baseline |
| 2030 | ~150 TWh | −6% |
| 2040 | ~130 TWh | −19% |
| 2050 | ~110 TWh | −31% |

Smallest absolute demand of the 7 (small country, smaller stock), but per-capita is high due to gas-heated stock and cold-damp winters.

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| New gas connections ban | 2018 | All new buildings must be gas-free (Wet Voortgang Energietransitie) |
| Hybrid HP mandate | **CANCELLED** | Was scheduled 2026; abandoned by 2024 coalition |
| Replacement fossil ban | 2026 (in model) | **Model overstates actual policy** — only voluntary now |
| HP mandate effective | 2026 (model) | **Cancelled in reality** |
| Fossil subsidies end | 2025 | |
| Full fossil phase-out | 2040 | Climate Agreement 2019 |
| ETS2 launches | 2027 | EU-wide |

**Important policy update:** In May 2022, the Dutch government announced hybrid heat pumps would become mandatory for boiler replacements from January 2026. In May 2023, multi-story apartment blocks and listed buildings were exempted. **In 2024, the new coalition government (PVV-VVD-NSC-BBB) abandoned the mandate entirely**, leaving only voluntary uptake supported by subsidies. The model still encodes the 2026 mandate; this is a known limitation that overstates the speed of NL transition.

**Subsidies remain in place:** ISDE programme provides ~30% grant for HP installation; €150M/yr through 2030. Hybrid HP saves ~60% of gas use vs full gas boiler.

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario:

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €251/MWh | €246/MWh | €197/MWh |
| Heat pump (air) | €124/MWh | €114/MWh | €80/MWh |
| Heat pump (ground) | €106/MWh | €100/MWh | €72/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €310/MWh | €228/MWh | €137/MWh |

> **Labour-cost adjustment applied:** Country multiplier **1.30** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights:**
- Largest HP-gas gap in modelled set: HP air €121 vs gas €245 = €124/MWh in 2025
- Despite this clear economics, switching rate has dropped 30% in 2024 due to political uncertainty and stable gas prices
- The hybrid HP option (HP + gas boiler in parallel) has been preferred for retrofits because it requires no radiator/insulation upgrade

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 10.2M | 30 |
| Multi-family house (MFH) | 3.2M | 10 |
| Other / mixed | (model over-count) | 121 |

NL has ~8.2M dwellings nationally (HPT Magazine 2025). About 75% SFH/terraced houses, 25% apartments.

**HP/DH feasibility:** SFH HP=0.90, MFH HP=0.50, SFH DH=0.30, MFH DH=0.80

---

## Current heating mix (residential, 2023)

| Energy source | Share | Notes |
|---|---|---|
| Natural gas | 72.9% | Eurostat — highest in EU |
| Electricity (direct + HP) | ~13% | HPs in ~8% of homes |
| District heating | ~6% | Concentrated in Rotterdam, Amsterdam, Utrecht |
| Other (biomass, oil) | ~8% | Marginal |

The Netherlands sits on top of the Groningen gas field — historical gas abundance shaped infrastructure. Production has now been wound down due to earthquake damage, but gas grid remains.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 280 | Gas-CCGT heavy; growing offshore wind |
| 2030 | 110 | EEA — offshore wind expansion |
| 2040 | 35 | |
| 2050 | 10 | |

NL has the most ambitious offshore wind plan: 21 GW by 2030, 70 GW by 2050.

---

## Renewable potential

NL has Europe's strongest offshore wind resource. Onshore wind constrained. Solar PV ~25 GW installed (high per-capita despite cloudy climate).

Critical issue: **grid congestion**. The Dutch electricity grid is increasingly congested — TenneT (TSO) has declared parts of the country "congestion zones" where new connections are paused. This impacts HP deployment because mass electrification requires grid reinforcement.

---

## District heating context

- DH supplies ~6% of residential heating.
- Largest networks: Eneco (Rotterdam ~50k connections, growing), Vattenfall (Amsterdam), Ennatuurlijk (multiple cities).
- Fuel mix: mostly gas + waste-to-energy + industrial waste heat (Rotterdam port refineries).
- Government targets to expand DH to 750k connections by 2030 from current ~410k.
- Major political controversy: pricing regulation (Warmtewet) under reform.

---

## Key actors

**Regulators / policy makers:**
- Ministerie van Klimaat en Groene Groei (Climate Ministry)
- ACM (consumer/markets authority)
- TenneT (transmission system operator)
- Netbeheer Nederland (DSO association — drove hybrid HP plan)

**Utilities:**
- Eneco, Vattenfall, Essent (RWE), Nuon
- Gasunie (gas TSO; potential H₂ network operator)

**Heat pump manufacturers active in NL:**
- NIBE (Swedish, acquired Itho Daalderop 2023, market leader)
- Daikin, Mitsubishi Electric
- Remeha, Intergas, ATAG (gas boiler incumbents, increasingly hybrid)

---

## National programmes

| Programme | Detail |
|---|---|
| **ISDE (Investeringssubsidie duurzame energie)** | ~30% grant on HP installation cost; €150M/year through 2030 |
| **Nationaal Warmtefonds** | Interest-free loans for low-income households (<€60k) |
| **Energiebespaarlening** | Energy-saving loans for renovations |
| **Hybrid HP voluntary uptake** | Industry plan: 100k+ hybrid HP installs per year (target now harder to meet) |

---

## Risk flags

- **Coalition government U-turn (2024)**: Hybrid HP mandate abandoned. Significant slowdown risk vs model assumption.
- **Grid congestion**: TenneT capacity bottleneck delays new HP connections in some regions.
- **High gas-grid sunk costs**: 90% of buildings connected — strongest argument for hydrogen retrofit pathway.
- **Apartment building heat pump unsuitability**: Dense urban stock not well-suited to individual air-source HP.
- **Gas grid operator lobby**: Gasunie and DSOs advocate hydrogen retrofit of existing gas grids.
- **Cold-climate apartment heating constraints**: Listed buildings in historic Amsterdam difficult to retrofit.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 8% | 73% | 0% | 6% | 2% |
| 2030 | 40% | 0%* | 0% | 19% | 38% |
| 2050 | 51% | 0% | 7% | 16% | 25% |

*Model shows gas at 0% from 2030 due to encoded replacement ban; real-world path now slower after 2024 policy U-turn. **This is the country where the model and reality diverge most.** Worth flagging as a sensitivity in the paper.

---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 160.6 TWh  
**NUTS coverage:** 4 NUTS1 · 12 NUTS2 · 40 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `NL3` | West-Nederland | 79.34 | 49.4% | 14,766,341 |
| `NL4` | Zuid-Nederland | 33.89 | 21.1% | 11,143,963 |
| `NL2` | Oost-Nederland | 31.74 | 19.8% | 10,806,496 |
| `NL1` | Noord-Nederland | 15.67 | 9.8% | 3,300,883 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `NL33` | Zuid-Holland | 33.81 | 21.0% | 5,827,673 |
| `NL32` | Noord-Holland | 29.39 | 18.3% | 3,762,671 |
| `NL41` | Noord-Brabant | 23.16 | 14.4% | 7,688,781 |
| `NL22` | Gelderland | 18.34 | 11.4% | 6,152,938 |
| `NL31` | Utrecht | 12.87 | 8.0% | 3,992,258 |
| `NL42` | Limburg (NL) | 10.73 | 6.7% | 3,455,182 |
| `NL21` | Overijssel | 10.22 | 6.4% | 3,429,762 |
| `NL12` | Friesland (NL) | 5.83 | 3.6% | 0 |
| `NL11` | Groningen | 5.45 | 3.4% | 1,826,338 |
| `NL13` | Drenthe | 4.40 | 2.7% | 1,474,545 |
| — | (Other 2 regions) | 6.45 | 4.0% | 2,407,535 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/NL.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.

---

## Sources

See [sources.md](sources.md).

## EUBUCCO bottom-up heat demand build (build group 5 (NW temperate))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/nl.yaml`; methodology: `literature/netherlands/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 12 NUTS2 / 47 NUTS3 |
| TABULA typology | NL (direct) |
| Climate multiplier | 0.8534 (Option B; tabula_reference_hdd = 2900.0) |
| Retrofit blend factor | 0.8075 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 1000 Mm2 (census/EUBUCCO 1.02) |
| Hotmaps 2015 benchmark | 160.65 TWh |
| **Bottom-up result** | **130.7 TWh** (-18.6 % vs Hotmaps, ACC) |

Applied corrections: Option B reference-HDD correction.

**Insight (2026-05-25):** The Netherlands lands at -18.6 % (ACC) on the direct typology. The Dutch stock is well-insulated with highly efficient gas heating, so a moderate under-shoot vs the Hotmaps 2015 baseline is expected. Left native within the ACC band.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 80% · oil 0% · biomass 4% · resistance 2% · heat pump (air 7% + ground 0%) · district heat 5%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €222 | €218 | €170 |
| Heat pump (air) | €106 | €101 | €80 |
| Heat pump (ground) | €100 | €94 | €70 |
| Hydrogen boiler (CENTRAL) | €253 | €138 | €93 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 39% | 11% | 2% | 8% | 39% |
| Stated Policies | 46% | 12% | 6% | 8% | 27% |
| Net Zero | 57% | 21% | 4% | 9% | 9% |
| H2 Push | 49% | 17% | 8% | 9% | 15% |

**Merit-order winter peak:** hydrogen is the cheapest peaking source here under Stated Policies, Net Zero, H2 Push (endogenous cold-snap power price ~€240/MWh). Even there, the inframarginal rent recovers at most **30%** of the H2 boiler's annualised CAPEX -- the peaker runs too few hours to pay for itself ('missing money').

**District-heating supply stack (Net Zero, 2050):** H2 ranks 3 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €6.1bn · Stated Policies €8.1bn · Net Zero €12.9bn · H2 Push €11.5bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 67% · district heat 30% · H2 3% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 5%, H2-for-buildings ceiling 2050 3%, demand reduction by 2050 38%, stock turnover 6.3%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.93**, range [0.69–1.21] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 23 (23 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 29 [27–34], new-build 42 [34–54] (central [low–high]); across the delivered-H2 supply band 23 [10–38].

<!-- /COUNTRY_MODEL_UPDATE -->
