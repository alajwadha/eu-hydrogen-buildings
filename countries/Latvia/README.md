# Latvia (LV)

> **RQ relevance:** 40.6% residential energy from renewables (mostly biomass + DH bioenergy). Significant DH penetration. Major biomass DH transformations 2010-2020. October 2025: Estonia-Latvia DH cross-border link inaugurated (Valga-Valka).

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €75/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €190/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 120 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 30% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.7 | Hotmaps HDD; EHPA |
| Annual heating hours | 3071/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2028 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** 40.6% residential energy from renewables (2023). Significant district heating penetration.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €125 | €131 | €116 |
| Heat pump (air) | €86 | €80 | €57 |
| Heat pump (ground) | €72 | €67 | €50 |
| H₂ boiler (CENTRAL) | €265 | €185 | €100 |

> **Labour-cost adjustment applied:** Country multiplier **0.55** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 546,812 | 1.8 |
| MFH_HIGH | 1,369,832 | 4.26 |
| OTHER | 3,842,956 | 12.16 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** District heating ~39% | Biomass (direct + DH input) ~32% | Gas ~12% | Electricity (incl HP) ~14% | Oil ~3%

High biomass share — Latvia is major wood pellet exporter (to Denmark, UK). DH widely used in Riga, Daugavpils.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 120 |
| 2030 | 65 |
| 2040 | 25 |
| 2050 | 5 |

---

## District heating context

**Share:** ~39% of residential heating.

Rīgas siltums — Riga (largest network). Gren (Daugavpils). Biomass + (legacy) gas. Cross-border DH link Valka-Valga with Estonia from 2025.

---

## Key actors

Utility: Latvenergo. DH: Rīgas siltums. HP brands: NIBE, Daikin.

---

## National programmes

Altum (state development bank) — HP and renovation grants. Apartment building renovation grants. NRRP.

**Subsidies:** Altum loans + grants for HP and energy renovation.

---

## Risk flags

- Biomass export economy — domestic supply faces competition.
- Russian border — historic gas dependency, now diversified.
- Smaller HP market (4,000 sold 2024).
- DH affordability issues for low-income.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 1 (DE + Baltics))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/lv.yaml`; methodology: `literature/latvia/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 1 NUTS2 / 6 NUTS3 |
| TABULA typology | PL (proxy) |
| Climate multiplier | 1.2088 |
| Retrofit blend factor | 0.9591 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 68 Mm2 (census/EUBUCCO 0.65) |
| Hotmaps 2015 benchmark | 18.22 TWh |
| **Bottom-up result** | **21.9 TWh** (+20.0 % vs Hotmaps, ACC) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Latvia is the Baltic **control**: same single Polish proxy as EE/LT, but with **no area or class-mix correction applied**, it lands at +20.0 % (ACC). This residual is exactly the proxy-mismatch signal -- it shows how much the all-PL typology over-states a partly-wooden Baltic stock, and validates why EE/LT (more wooden + bigger EUBUCCO area gap) needed their corrections while LV did not.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 7% · oil 3% · biomass 49% · resistance 1% · heat pump (air 2% + ground 0%) · district heat 38%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €111 | €117 | €104 |
| Heat pump (air) | €77 | €73 | €58 |
| Heat pump (ground) | €70 | €65 | €50 |
| Hydrogen boiler (CENTRAL) | €210 | €107 | €67 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 61% · district heat 39% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 40%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 31%, stock turnover 5.6%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.84**, range [0.63–1.08] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 18 (18 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 22 [21–27], new-build 33 [27–43] (central [low–high]); across the delivered-H2 supply band 18 [6–31].

<!-- /COUNTRY_MODEL_UPDATE -->
