# Switzerland (CH) — RQ2 Anchor

> **RQ2 anchor country.** Near-zero-carbon electricity grid (hydro+nuclear), HP-favourable climate, cantonal energy mandates (MuKEn), CO₂ levy of CHF 120/tCO₂ on heating fuels since 2022. The central question: can H₂ imports play any meaningful role in Swiss buildings decarbonisation by 2050, given the strength of the heat pump case?

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €120/MWh | Eurostat / Swiss Federal Office of Energy |
| Residential electricity price (H1 2025) | €220/MWh | Eurostat / BFE |
| Grid CO₂ intensity 2025 | 50 gCO₂/kWh | EMBER / IEA Switzerland 2023 |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | SFOE EP2050+ |
| Gas grid coverage | 35% of buildings | Policy.py — moderate |
| Heat pump SCOP (air-source, 2025) | 2.91 | Hotmaps; alpine climate |
| Annual heating hours | 2,286/year | Hotmaps |
| Buildings on fossil fuels (oil + gas) | ~60% | Val Index 2026 |
| HPs in operation | ~450,000 | Val Index 2026 |
| Annual HP installations (recent) | ~42,000 | Val Index 2026 |
| Swiss CO₂ levy on heating fuels | CHF 120/tCO₂ (≈€125) since 2022 | SFOE |
| Buildings share of national CO₂ | ~33% | SFOE |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 78 TWh useful heat.

**Model trajectory (historical pre-June-2026 run; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~78 TWh | baseline |
| 2030 | ~73 TWh | −6% |
| 2040 | ~63 TWh | −19% |
| 2050 | ~55 TWh | −30% |

Smallest absolute demand of the 7 (small country, ~9M population, smaller stock). Alpine climate with cold winters but well-insulated building standard (Minergie certification widespread).

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| Fossil subsidies end | 2025 | Phased out via Gebäudeprogramm reform |
| New-build fossil ban | 2023 | Effective via MuKEn-aligned cantonal laws |
| Replacement fossil ban | 2030 | Cantonal — varies by canton, no national ban |
| HP mandate effective | 2030 | Effective via "renewable share" cantonal requirements |
| Full fossil phase-out | 2040 | Energy Strategy 2050 target |
| Swiss CO₂ levy | CHF 120/t since 2022 | National policy |
| ETS2 (does not directly apply) | n/a | Switzerland not in EU ETS but maintains parallel scheme |

**Key policy context — federalism matters:**

Switzerland does not have a national boiler ban. Instead, building energy regulation is cantonal (state-level), harmonised via **MuKEn** (Mustervorschriften der Kantone im Energiebereich — Cantonal Model Regulations on Energy). MuKEn 2014 is in force; MuKEn 2025 is being finalised with stricter requirements.

**Cantonal variation:**
- **Quasi-ban cantons** (Fribourg, Jura, Lucerne, Basel-Stadt, Neuchâtel, Glarus): ≥90% of new heating systems are renewable. These cantons effectively prohibit fossil heating in renovations.
- **Soft enforcement cantons** (Valais, Aargau): fossil heating still permitted at replacement.
- **MuKEn principle**: when replacing a fossil boiler 1:1 with another fossil boiler, owner must offset by either (a) renewable energy share ≥10% or (b) efficiency upgrade. In practice this often forces a HP switch.

**Climate and Innovation Act 2023:**
- Approved by Swiss electorate June 2023
- Target: CO₂-neutral Switzerland by 2050
- CHF 200M/year through 2030 for replacing old oil, gas, electric heating

**MuKEn 2025 (in development):**
- Stricter renewable energy share requirements
- New mandates for existing-building insulation, windows, ventilation
- "Grey energy" embodied-emissions limits
- Implementation target: 2030

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario:

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €205/MWh | €205/MWh | €172/MWh |
| Heat pump (air) | €103/MWh | €95/MWh | €68/MWh |
| Heat pump (ground) | €91/MWh | €85/MWh | €64/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €310/MWh | €229/MWh | €137/MWh |

> **Labour-cost adjustment applied:** Country multiplier **1.70** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights for RQ2:**
- Ground-source HP is the **cheapest** option in Switzerland in 2025 (€83/MWh) — well below gas (€192) and H₂ boiler (€291)
- Even under the LOW H₂ import scenario (OIES ET32), H₂ boiler LCOH (€85/MWh in 2050) only approaches but does not beat ground-source HP (€58/MWh)
- **No economic case for H₂ in Swiss residential heating before 2050** in any scenario
- Possible H₂ niches: hard-to-electrify historic buildings, industrial process heat, seasonal storage with hydropower

**Important caveat:** Swiss HP installation costs are unusually high compared to peers (€20–50k vs €15k in Sweden). Reasons include labour costs, fragmented installer market, and equipment markup. This is reflected in the model via the discount rate but not via country-specific CAPEX — limitation flagged.

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 3.0M | 9 |
| Multi-family house (MFH) | 5.8M | 17 |
| Other / mixed | (model over-count) | 52 |

Switzerland has ~4.7M dwellings nationally (Federal Statistical Office BFS). Multi-family dominates (~70% of dwellings) — apartment-building heat pumps and DH are the main retrofit pathways.

**HP/DH feasibility:** SFH HP=0.90, MFH HP=0.50, DH varies sharply by canton/city.

---

## Current heating mix (residential, ~2023)

| Energy source | Share | Notes |
|---|---|---|
| Oil heating | ~30% | Falling; quasi-banned in several cantons |
| Natural gas | ~30% | Concentrated in urban areas |
| Heat pumps | ~25% | Air-source dominant; ground-source significant |
| District heating | ~10% | Expanding under cantonal plans |
| Wood/biomass | ~5% | Some rural, Alpine areas |
| Direct electric resistance | ~1% (declining) | MuKEn mandates replacement |

In 2024, Swiss HP installations declined by 47% in H1 vs 2023 — installer capacity and electricity-vs-gas price ratio cited. Concurrently, gas and oil heating installations rose 12%. This is a near-term setback driven by political uncertainty and energy price stabilisation; long-term trajectory unchanged.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 50 | Hydro 56%, nuclear 33%, solar/wind 7%, other 4% |
| 2030 | 30 | Renewables expansion under Energy Strategy 2050 |
| 2040 | 15 | |
| 2050 | 5 | Near-zero |

Swiss grid is among Europe's cleanest. HPs are highly effective for CO₂ reduction immediately.

---

## Renewable potential

Hydro: ~17 GW (max practical), nearly fully exploited. Solar: ~6 GW installed (rapid growth 2022–24). Wind: ~0.2 GW (very limited, NIMBY). Geothermal: emerging, supports ground-source HPs.

Switzerland's challenge: post-nuclear, after Mühleberg shutdown and lifecycle extensions for remaining plants, the country will need 25–30 TWh of additional renewable generation by 2050. Solar PV is the main growth path.

---

## District heating context

- DH supplies ~10% of residential heat — growing.
- Major networks: Zurich (ERZ), Geneva (SIG), Basel (IWB), Lausanne (SiL).
- Many cantons mandating DH expansion under MuKEn 2025.
- Fuel mix: ~50% waste-to-energy, 30% biomass, 15% gas (transitioning), 5% large HPs.
- Federal Building Programme (Gebäudeprogramm) distributed CHF 360M+ in 2024 for renovations + DH expansion.

---

## Key actors

**Federal:**
- BFE / SFOE (Swiss Federal Office of Energy)
- BAFU (Federal Office for the Environment)
- ElCom (electricity regulator)

**Cantonal:**
- EnDK (Conference of Cantonal Energy Directors) — coordinates MuKEn
- Cantonal energy offices (26 in total)

**Utilities (largest):**
- Axpo (mostly hydro), Alpiq, BKW
- IWB (Basel), SIG (Geneva), EWZ (Zurich), SiL (Lausanne) — municipal multi-utilities, often DH operators
- Swissgrid (TSO)

**Heat pump market:**
- ~3,200 HVAC firms (Val Index 2026 — heavily SME)
- Major foreign brands: Daikin, Mitsubishi, NIBE, Viessmann, Hoval (CH-based)
- 40% of firms have owner over 55 — significant succession transition

---

## National programmes

| Programme | Detail |
|---|---|
| **Gebäudeprogramm (Federal Building Programme)** | CHF 360M+ in 2024; co-funded by CO₂ levy revenue + cantonal contributions |
| **CO₂ levy on heating fuels** | CHF 120/tCO₂ since 2022; revenue redistributed to households (per-capita) and Gebäudeprogramm |
| **MuKEn 2014 / MuKEn 2025** | Cantonal regulations on building energy |
| **Climate and Innovation Act 2023** | CHF 200M/year until 2030 for replacing fossil heating |
| **GEAK (Gebäudeenergieausweis der Kantone)** | Energy performance certification |
| **Pronovo CO₂ levy redistribution** | Reduces household electricity bills |

---

## Risk flags

- **Cantonal fragmentation**: 26 different regulatory regimes. National policy aspirations slowed by federalist constraints.
- **HP cost outlier**: Swiss HP installations cost 2–3× peer-country prices. Investigative reports (lenews.ch 2024) attribute to labour, supplier markup, lack of installer competition.
- **2024 HP sales collapse**: −47% in H1 2024, +12% in fossil installations. Risk that political uncertainty stalls transition.
- **Hydropower seasonal constraint**: Winter electricity import dependency (peak heat demand coincides with low hydro). Affects HP economics in cold spells.
- **Nuclear policy**: Phaseout law (2017) being challenged; 2025 referendum on lifecycle extensions possible. Affects long-term electricity supply security.
- **No EU ETS2**: Switzerland outside ETS — its CHF 120/t levy is higher than current ETS, but pass-through and political durability uncertain.
- **H₂ infrastructure absent**: Switzerland has no major H₂ pipelines. Imports would require building new infrastructure or upgrading existing gas grid — costly and slow.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 25% | 30% | 0% | 10% | 5% |
| 2030 | 41% | 0%* | 0% | 18% | 38% |
| 2050 | 50% | 0% | 7% | 16% | 25% |

*Model accelerates gas exit due to cantonal mandates; real-world trajectory will be slower in soft-enforcement cantons.

---

## RQ2 implications

The central RQ2 finding from the model is unambiguous: **H₂ imports cannot economically displace heat pumps in Swiss buildings before 2050 under any OIES import price scenario.** Even under the LOW import trajectory (CHF 60–70/MWh by 2050), H₂ boiler LCOH remains above ground-source HP LCOH.

Possible H₂ niches in Switzerland (not quantified in this model):
1. **Historic city-centre buildings** (Bern Old Town, Geneva Vieille-Ville) where HP installation is constrained by listed-building rules and acoustic limits.
2. **Industrial process heat** beyond the model's residential scope (Swiss chemicals/pharma sectors).
3. **Seasonal storage integrated with hydropower** — converting summer hydro surplus to H₂ for winter peak. This is more a power-sector question than a heating one.
4. **Backup/peak generation** in winter when import dependency tightens.

For Swiss buildings policy, the implication is that hydrogen infrastructure investment should be deprioritised in favour of accelerating HP deployment, grid reinforcement, and DH expansion in dense urban areas.

---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 77.9 TWh  
**NUTS coverage:** 1 NUTS1 · 7 NUTS2 · 26 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `CH0` | Schweiz/Suisse/Svizzera | 77.88 | 100.0% | 26,974,051 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `CH02` | Espace Mittelland | 17.61 | 22.6% | 5,925,303 |
| `CH01` | Région lémanique | 15.02 | 19.3% | 5,092,434 |
| `CH04` | Zürich | 13.07 | 16.8% | 4,879,521 |
| `CH05` | Ostschweiz | 11.22 | 14.4% | 3,694,254 |
| `CH03` | Nordwestschweiz | 10.09 | 13.0% | 3,706,737 |
| `CH06` | Zentralschweiz | 7.03 | 9.0% | 2,532,303 |
| `CH07` | Ticino | 3.83 | 4.9% | 1,143,499 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/CH.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.

---

## Sources

See [sources.md](sources.md).

## EUBUCCO bottom-up heat demand build (build group 7 (UK + CH; non-EU))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/ch.yaml`; methodology: `literature/switzerland/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 7 NUTS2 / 26 NUTS3 |
| TABULA typology | AT (proxy) |
| Climate multiplier | 1.0328 |
| Retrofit blend factor | 0.828 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 480 Mm2 (EUBUCCO comparison pending first build) |
| Hotmaps 2015 benchmark | 77.9 TWh |
| **Bottom-up result** | **86.8 TWh** (+11.4 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Switzerland reconciles at +11.4 % (OK) on the AT typology as proxy -- a notable result because EUBUCCO's swisstopo footprints carry ~0 % construction-year, so the build is **99.8 % unknown-cohort** and runs almost entirely on the RegBL-grounded BSO stock weights. Landing in the OK band from a zero-attribute partition validates the stock-weighted fallback approach.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 18% · oil 39% · biomass 12% · resistance 6% · heat pump (air 16% + ground 6%) · district heat 4%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €218 | €215 | €168 |
| Heat pump (air) | €115 | €108 | €86 |
| Heat pump (ground) | €108 | €100 | €76 |
| Hydrogen boiler (CENTRAL) | €267 | €143 | €96 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 37% | 12% | 2% | 8% | 39% |
| Stated Policies | 43% | 15% | 6% | 8% | 27% |
| Net Zero | 52% | 25% | 4% | 9% | 9% |
| H2 Push | 44% | 22% | 8% | 9% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 4 of 5 sources by marginal cost and undercuts the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €3.1bn · Stated Policies €4.6bn · Net Zero €7.0bn · H2 Push €6.6bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 53% · district heat 47% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 12%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.00**, range [0.74–1.31] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 20 (20 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 24 [23–29], new-build 35 [29–43] (central [low–high]); across the delivered-H2 supply band 20 [6–37].

<!-- /COUNTRY_MODEL_UPDATE -->
