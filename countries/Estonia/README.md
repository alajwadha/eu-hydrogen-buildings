# Estonia (EE)

> **RQ relevance:** Among largest gas demand reductions in EU since 2022 (Bruegel) — accelerated transition post-Ukraine war. Soviet-era DH infrastructure prevalent (Tartu, Tallinn). Strong renewable share via biomass + waste-to-energy in DH. October 2025: Estonia-Latvia DH cross-border link opened (Utilitas).

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €105/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €210/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 300 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 15 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 30% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.64 | Hotmaps HDD; EHPA |
| Annual heating hours | 3214/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2028 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 39.5% residential energy from renewables. Largest gas demand reduction since 2022 (Bruegel tracker) — strong response to Russia's invasion of Ukraine.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €157 | €160 | €134 |
| Heat pump (air) | €100 | €92 | €64 |
| Heat pump (ground) | €82 | €77 | €56 |
| H₂ boiler (CENTRAL) | €264 | €184 | €99 |

> **Labour-cost adjustment applied:** Country multiplier **0.62** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 325,754 | 1.12 |
| MFH_HIGH | 729,582 | 2.43 |
| OTHER | 2,131,150 | 9.72 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** District heating ~50% | HP+electric ~20% | Biomass ~22% | Gas ~6% | Oil shale-derived heat (residual) ~2%

Tartu DH (Gren) ~92% biomass — one of cleanest in CEE. Tallinn DH (Utilitas) — major operator. Direct biomass + electric resistance common in rural areas.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 300 |
| 2030 | 150 |
| 2040 | 60 |
| 2050 | 15 |

---

## District heating context

**Share:** ~50% of residential heating.

Gren (Tartu, Pärnu, Viljandi, Kohtla-Järve), Utilitas (Tallinn). Major TES system inaugurated 2025 (1.1 GWh accumulator). Cross-border link Valga-Valka with Latvia (Oct 2025, 1.6 km pipeline).

---

## Key actors

Utilities: Eesti Energia (state). DH: Gren, Utilitas. HP brands: NIBE, Mitsubishi.

---

## National programmes

KredEx — energy efficiency grants for residential buildings. EU NRRP. Apartment block renovation grants (Soviet-era blocks dominant).

**Subsidies:** KredEx HP grants under apartment renovation; small market overall.

---

## Risk flags

- Oil shale legacy — Narva power plants account for major grid CO₂. Decommissioning timeline uncertain.
- BRELL grid uncoupling from Russia/Belarus 2025 — grid stability transitional issues.
- Smaller HP market — limited installer base.
- District heating monopolies — competition concerns.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 1 (DE + Baltics))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/ee.yaml`; methodology: `literature/estonia/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 1 NUTS2 / 5 NUTS3 |
| TABULA typology | PL (proxy) |
| Climate multiplier | 1.2625 |
| Retrofit blend factor | 0.938 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.5 (Mechanism B, occupancy/stock-utilization) |
| class_mix proxy | yes |
| Census floor-area benchmark | 51 Mm2 (census/EUBUCCO 0.45) |
| Hotmaps 2015 benchmark | 13.27 TWh |
| **Bottom-up result** | **10.8 TWh** (-18.7 % vs Hotmaps, ACC) |

Applied corrections: class-mix proxy (per-class typology); occupancy correction 0.5 (heated-base; vacant/seasonal stock excluded).

**Insight (2026-05-25):** Estonia lands at -18.7 % (ACC) via a `tabula.class_mix` proxy (Swedish wooden SFH + Polish panel MFH) plus an occupancy `area_correction` 0.50. The suvila (summer-house) stock that EUBUCCO counts but is unheated in winter is the area driver; the honest census-grounded under-shoot is carried rather than tuned up to the benchmark.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 6% · oil 0% · biomass 41% · resistance 6% · heat pump (air 6% + ground 1%) · district heat 39%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €143 | €146 | €121 |
| Heat pump (air) | €85 | €80 | €64 |
| Heat pump (ground) | €77 | €72 | €55 |
| Hydrogen boiler (CENTRAL) | €207 | €105 | €66 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 61% · district heat 39% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 40%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 35%, stock turnover 6.0%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.83**, range [0.63–1.07] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 12 (12 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 16 [14–20], new-build 26 [20–34] (central [low–high]); across the delivered-H2 supply band 12 [1–25].

<!-- /COUNTRY_MODEL_UPDATE -->
