# Luxembourg (LU)

> **RQ relevance:** 45.3% residential energy from gas (Eurostat 2023). High-income country — transition financing less of a barrier. Cross-border worker market — many residents commute to BE/FR/DE. Small absolute market (1,000 HPs sold 2024 per EHPA). Highest gas-savings-per-HP installation (EHPA 2024).

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €115/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €290/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 150 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 70% of buildings | Policy.py (model) |
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
| Hp Mandate Year | 2030 |


**Context:** 45.3% residential energy from gas (2023, Eurostat). High income country — transition financing less of a barrier.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €208 | €208 | €177 |
| Heat pump (air) | €128 | €118 | €84 |
| Heat pump (ground) | €112 | €105 | €78 |
| H₂ boiler (CENTRAL) | €322 | €240 | €147 |

> **Labour-cost adjustment applied:** Country multiplier **1.80** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 336,889 | 1.53 |
| MFH_HIGH | 271,190 | 1.23 |
| OTHER | 1,216,158 | 5.52 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## EUBUCCO building-stock build (bottom-up heat demand)

Independent bottom-up estimate from the country-build pipeline (EUBUCCO v0.2 +
TABULA Belgium proxy). Method: `literature/country_build_methodology.md`.

**Stock classified — 186,171 EUBUCCO buildings:**

| Class | Buildings | Heated floor area | Heat demand |
|---|--:|--:|--:|
| SFH | 71,411 | 13.7 Mm² | 2.69 TWh |
| MFH_LOW | 27,394 | 23.8 Mm² | 3.77 TWh |
| MFH_HIGH | 119 | 1.0 Mm² | 0.15 TWh |
| NON_RESIDENTIAL | 87,247 | — (out of scope) | — |
| **Residential total** | **98,924** | **0.04 bn m²** | **6.60 TWh** |

**Reconciliation (residential space heating + DHW):**

| Source | TWh/yr | vs bottom-up |
|---|--:|--:|
| **Bottom-up (this build)** | **6.60** | — |
| Hotmaps 2015 | 8.27 | **−20.2 %** |
| EU BSO 2021 (implied) | 5.70 | +16 % |
| Odyssee-Mure 2021 | 7.20 | −8 % |

**Insights:**
- **In-band, at the lower edge.** −20.2 % vs Hotmaps is inside the ±25 %
  target ("acceptable") but not the tighter ±15 % tier.
- **Fallback-driven, not per-vintage.** EUBUCCO has a construction year for
  only ~0 % of LU buildings, so the result is effectively the EU BSO
  stock-weighted class-average intensity × floor area — *not* a true
  per-vintage bottom-up. This must be stated in any write-up.
- **TABULA Belgium proxy.** No national TABULA data for Luxembourg; Belgian
  intensities are used with a 1.112 climate multiplier (LU is ~11 % colder).
- **Consistent with France.** Uses EUBUCCO's native `floors` column
  (`floor_source: eubucco`), the same method as the France build, so the two
  countries are directly comparable.

---

## Current heating mix (residential)

**Mix:** Gas ~45% | Oil ~30% | District heating ~12% | Electricity (incl HP) ~10% | Biomass ~3%

Gas dominant in urban Luxembourg City + suburbs. Oil persists rural. DH growing in new districts (Cloche d'Or, Esch-Belval).

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 150 |
| 2030 | 80 |
| 2040 | 30 |
| 2050 | 8 |

---

## District heating context

**Share:** ~12% of residential heating.

Sudgaz/Enovos networks. Esch-sur-Alzette redevelopment includes DH. Small national scale but growing in new builds.

---

## Key actors

Utility: Enovos, Sudgaz. HP brands: Vaillant, Bosch, Daikin, Stiebel Eltron.

---

## National programmes

Klimabonus (climate bonus) — up to €17,500 for HP installation. Highest per-household subsidy in EU. Free energy audit.

**Subsidies:** Klimabonus: ASHP up to €11,400, GSHP up to €17,500. EnPrime renovation premium.

---

## Risk flags

- Very small national market — limited installer scaling.
- Strong subsidies → high HP/€ effectiveness but limited scale.
- Cross-border heating culture (workers from FR/BE/DE).
- Cost of living + property prices very high — renovation capacity not the bottleneck.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 8.3 TWh  
**NUTS coverage:** 1 NUTS1 · 1 NUTS2 · 1 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `LU0` | Luxembourg | 8.27 | 100.0% | 1,824,237 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `LU00` | Luxembourg | 8.27 | 100.0% | 1,824,237 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/LU.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group proof-of-concept)

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/lu.yaml`; methodology: `literature/luxembourg/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 1 NUTS2 / 1 NUTS3 |
| TABULA typology | BE (proxy) |
| Climate multiplier | 1.112 |
| Retrofit blend factor | 0.813 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 33 Mm2 (census/EUBUCCO 0.86) |
| Hotmaps 2015 benchmark | 8.27 TWh |
| **Bottom-up result** | **6.6 TWh** (-20.2 % vs Hotmaps, ACC) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Luxembourg lands at -20.2 % (ACC) using the BE typology as proxy (x1.112). The under-shoot is partly inherited: the BE matrix's recent cohorts are too low vs the official calculator (see Belgium), which propagates into Luxembourg's modern-stock demand. Traceable to the upstream BE TABULA extraction and disclosed.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 56% · oil 23% · biomass 6% · resistance 2% · heat pump (air 6% + ground 1%) · district heat 6%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €174 | €175 | €145 |
| Heat pump (air) | €111 | €105 | €83 |
| Heat pump (ground) | €105 | €98 | €74 |
| Hydrogen boiler (CENTRAL) | €293 | €158 | €107 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 52% · district heat 48% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 10%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **1.09**, range [0.90–1.27] — European Hydrogen Backbone import-connected.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 32 (32 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 37 [36–42], new-build 48 [42–58] (central [low–high]); across the delivered-H2 supply band 32 [22–42].

<!-- /COUNTRY_MODEL_UPDATE -->
