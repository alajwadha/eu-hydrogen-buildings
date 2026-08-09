# Italy (IT)

> **RQ1 relevance:** High residential gas dependency (53.5% of space heating from gas, Eurostat 2023). Superbonus 110% (2020–2023) accelerated renovations dramatically; replaced by Ecobonus 50% and Conto Termico 3.0 in 2025. Replacement boiler ban delayed until 2035 — slower transition path than France or Netherlands.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €124/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €320/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 250 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 10 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 80% of buildings | Policy.py (model) |
| Heat pump SCOP (air-source, 2025) | 3.30 | Hotmaps; Mediterranean climate |
| Annual heating hours | 1,571/year | Hotmaps (warmest of the 7) |
| Gas share of space heating | 53.5% | Eurostat 2023 |
| HP sales 2024 | ~700k–800k units (includes A/A) | EHPA / Mordor Intelligence |

---

## Heat demand

**Current baseline (Hotmaps, 2015):** 482 TWh useful heat.

**Model trajectory (historical pre-June-2026 run; superseded by the model update below):**

| Year | Useful heat (TWh) | Reduction vs 2025 |
|------|--------------------|--------------------|
| 2025 | ~480 TWh | baseline |
| 2030 | ~455 TWh | −5% |
| 2040 | ~395 TWh | −18% |
| 2050 | ~340 TWh | −29% |

Italy has the warmest climate of the 7 countries — heating hours below 1,600/year — so heat demand per dwelling is moderate, but the stock is large (~25M households).

---

## Policy

| Measure | Year | Detail |
|---|---|---|
| Fossil subsidies end | 2025 | Ecobonus excludes single fossil-fuel boilers from 2025–2027 |
| New-build fossil ban | 2025 | Following EPBD; gas boilers excluded from Ecobonus |
| Replacement fossil ban | 2035 | Substantially delayed compared to France/NL |
| HP mandate effective | 2035 | Tied to replacement ban |
| Full fossil phase-out | 2040 | National Energy and Climate Plan |
| ETS2 launches | 2027 | EU-wide |

**Key policy context:** Italy is taking the slowest path among large EU economies. Steps toward replacement ban are being taken (ECOS/EHPA), but implementation is delayed to 2035. The Superbonus 110% scheme (2020–2023) drove ~500,000 energy renovations but was politically toxic due to ballooning fiscal cost (over €100bn). Replaced by the more targeted Ecobonus (50% for primary residences) and Conto Termico 3.0 (direct cash grants up to 40% of HP cost) in 2025.

---

## Economics (LCOH)

LCOH at CENTRAL carbon scenario:

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €217/MWh | €217/MWh | €182/MWh |
| Heat pump (air) | €126/MWh | €117/MWh | €82/MWh |
| Heat pump (ground) | €108/MWh | €101/MWh | €74/MWh |
| Hydrogen boiler (CENTRAL trajectory) | €320/MWh | €238/MWh | €145/MWh |

> **Labour-cost adjustment applied:** Country multiplier **0.97** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, H₂ boiler 35%) and 70% of FOM.

**Key cost insights:**
- HP air €91/MWh cheaper than gas in 2025 — strong economic case
- Warm climate gives Italian HPs the highest COP (3.30) of the 7 countries
- Cooling demand is rising — A/W heat pumps with reversible function are attractive
- A typical air-to-water HP retrofit costs €12,000–18,000 vs €4,000–6,000 for a condensing boiler

---

## Building stock

| Building type | Dwelling count (model) | Heat demand (TWh) |
|---|---|---|
| Single-family house (SFH) | 18.2M | 49 |
| Multi-family house (MFH) | 40.8M | 108 |
| Other / mixed | (model over-count) | 325 |

Italy has ~25M residential dwellings (ISTAT). Multi-family housing dominates urban areas (Milan, Rome, Naples); detached homes more common in rural North.

**HP/DH feasibility:** SFH HP=0.90, MFH HP=0.50 (apartment retrofit constrained)

---

## Current heating mix (residential, ~2023)

| Energy source | Share | Notes |
|---|---|---|
| Natural gas | 53.5% | Eurostat 2023 — highest share among modelled countries |
| Heating oil | ~7% | Declining, rural/older buildings |
| Biomass (wood/pellets) | ~15% | High in Apennines, Alpine regions |
| Heat pumps + electric | ~10% | Air-to-air (split AC) dominant, hydronic HP growing |
| District heating | ~4% | Concentrated in North (Milan, Turin, Brescia) |

Italy has a unique pattern: high gas in urban North, high biomass in mountainous regions, growing reversible air-to-air HPs driven by cooling demand.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh | Notes |
|---|---|---|
| 2025 | 250 | Gas-heavy (~30% of generation); growing solar |
| 2030 | 100 | National plan: 70% renewable electricity by 2030 |
| 2040 | 30 | |
| 2050 | 10 | |

Italy's grid is decarbonising rapidly via solar PV expansion (~25 GW installed; target 80 GW by 2030).

---

## Renewable potential

Italy has the best solar resource of the 7 countries (1,800–2,000 kWh/m²/year in the South vs 900–1,100 in Germany). Wind: limited onshore potential, growing offshore. Hydro: stable, ~50 GWh/year.

Solar+HP combo is the most attractive economic pathway for SFH retrofits — Ecobonus + Conto Termico can cover 50–90% of combined cost.

---

## District heating context

- DH supplies only ~4% of residential heating — much lower than Germany or Sweden.
- Geographic concentration: Northern Italy (Brescia, Turin, Milan, Bologna).
- Brescia and Turin have the most developed networks; smaller cities expanding.
- Fuel mix: gas-dominant historically; biomass + waste growing.
- Italy's Ministry of Ecological Transition supports DH expansion under Fit-for-55, but the market is fragmented.

---

## Key actors

**Regulators / policy makers:**
- Ministero dell'Ambiente e della Sicurezza Energetica (MASE) — energy ministry
- ENEA (national agency for new technologies, energy, sustainable economic development) — administers Ecobonus/Conto Termico
- GSE (Gestore dei Servizi Energetici) — energy services manager
- ARERA — regulator

**Utilities:**
- Enel (electricity, multi-energy, largest in Europe by market cap)
- Eni (gas, multi-energy)
- A2A (Brescia, multi-utility, DH operator)
- Iren (Turin/Reggio Emilia DH)

**Heat pump manufacturers:**
- Ariston (Italian, leads water heaters), Daikin (strong presence), Mitsubishi Electric, Vaillant
- Daikin reported 31% Italian HP revenue growth in 2025

---

## National programmes

| Programme | Detail |
|---|---|
| **Ecobonus 2025** | 50% tax deduction for main homes, 36% for others; spread over 10 years |
| **Bonus Ristrutturazioni** | 50% tax deduction on renovation costs up to €96k/property |
| **Conto Termico 3.0** | Direct grant (not tax credit) up to 40% of HP cost; faster cash flow than Ecobonus |
| **VAT exemption on HP** | Through 2027 |
| **Superbonus 110%** | Discontinued; legacy renovations still being processed |

---

## Risk flags

- **Slow replacement ban (2035)**: Italy lags France/Netherlands on phase-out timeline. ETS2 will pressure faster transition.
- **Fiscal hangover from Superbonus**: €100bn+ cost has soured political appetite for generous subsidies. Conto Termico more constrained.
- **Apartment retrofit complexity**: Condominium consent rules make multi-family HP retrofits slow and expensive.
- **Installer shortage in South**: Less developed installer base outside Lombardy/Piedmont.
- **Heritage building constraints**: Italy has the highest share of pre-1960 buildings in Europe; HP retrofit constrained by listed-building rules in city centres.
- **F-Gas regulation transition**: 4.2M installed R-410A units need retrofit to R-32/R-454B refrigerants by 2030.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

| Year | HP share | Gas share | H₂ share | DH share | Biomass |
|---|---|---|---|---|---|
| 2025 | 10% | 54% | 0% | 4% | 15% |
| 2030 | 22% | 34% | 0% | 13% | 27% |
| 2050 | 50% | 0% | 6% | 17% | 25% |

Italy's 2030 still has gas at 34% — reflecting the delayed 2035 replacement ban. By 2050, all scenarios converge on near-zero gas.

---

---

## EUBUCCO bottom-up heat demand build (build group 2 (IT + Adriatic))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/it.yaml`; methodology: `literature/italy/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 21 NUTS2 / 107 NUTS3 |
| TABULA typology | IT (direct) |
| Climate multiplier | 0.7285 (Option B; tabula_reference_hdd = 2500) |
| Retrofit blend factor | 0.889 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 3234 Mm2 (census/EUBUCCO 0.72) |
| Hotmaps 2015 benchmark | 482.0 TWh |
| **Bottom-up result** | **508.9 TWh** (+5.6 % vs Hotmaps, OK) |

Applied corrections: Option B reference-HDD correction.

**Insight (2026-05-25):** Italy reconciles at +5.6 % via the Option B `tabula_reference_hdd = 2500` (TABULA Middle-zone) correction. Verification shows the synthesised matrix sits ~15-30 % below the **published POLITO archetypes** -- an upstream TABULA-extraction gap, disclosed, not a pipeline error. Because the Option-B multiplier was sized against the current matrix, the two are coupled and the reconciliation holds; re-extracting POLITO values would require re-deriving Option B together (see verification doc).

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 62% · oil 5% · biomass 22% · resistance 2% · heat pump (air 6% + ground 0%) · district heat 2%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €189 | €189 | €155 |
| Heat pump (air) | €113 | €107 | €84 |
| Heat pump (ground) | €108 | €100 | €75 |
| Hydrogen boiler (CENTRAL) | €315 | €172 | €116 |

**2050 heating mix by scenario** (Monte Carlo median, renormalised; the four June-2026 multi-lever scenarios):

| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |
|---|---|---|---|---|---|
| Current Policies | 37% | 12% | 2% | 9% | 39% |
| Stated Policies | 43% | 14% | 6% | 9% | 27% |
| Net Zero | 53% | 22% | 4% | 12% | 9% |
| H2 Push | 44% | 19% | 8% | 12% | 15% |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**Network-infrastructure bill (cumulative 2025-2050, central):** Current Policies €31.4bn · Stated Policies €41.4bn · Net Zero €58.1bn · H2 Push €53.6bn (electricity reinforcement + district-heat expansion + H2 network).

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 54% · district heat 46% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 12%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.16**, range [0.86–1.38] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 41 (41 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 51 [48–62], new-build 76 [62–96] (central [low–high]); across the delivered-H2 supply band 41 [25–53].

<!-- /COUNTRY_MODEL_UPDATE -->
