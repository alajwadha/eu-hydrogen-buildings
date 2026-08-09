# Lithuania (LT)

> **RQ relevance:** Among largest gas demand reductions in EU since 2022 (Bruegel) — rapid post-Ukraine war transition. 53% of multi-apartment buildings on DH (Lithuanian DH research). Klaipėda LNG terminal (FSRU "Independence") critical to energy security. Heat pump grants up to €14,500.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €80/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €200/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 200 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 8 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 30% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.7 | Hotmaps HDD; EHPA |
| Annual heating hours | 3000/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2028 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** Among largest gas demand reductions since 2022 (Bruegel). Rapidly decarbonising — Baltic states accelerated transition post-Ukraine war.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €131 | €136 | €120 |
| Heat pump (air) | €92 | €85 | €60 |
| Heat pump (ground) | €76 | €71 | €52 |
| H₂ boiler (CENTRAL) | €266 | €186 | €100 |

> **Labour-cost adjustment applied:** Country multiplier **0.55** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 0 | 0.0 |
| MFH_HIGH | 0 | 0.0 |
| OTHER | 0 | 17.29 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## Current heating mix (residential)

**Mix:** District heating ~57% | Biomass (mostly DH input) ~25% | Gas ~10% | Electricity (incl HP) ~5% | Oil ~3%

Heavy DH dependency in urban areas. Rural wood-heating common. Vilnius, Kaunas, Klaipėda — DH dominant.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 200 |
| 2030 | 100 |
| 2040 | 35 |
| 2050 | 8 |

---

## District heating context

**Share:** ~57% of residential heating.

Vilniaus šilumos tinklai (VŠT) — Vilnius. Kauno energija — Kaunas. Klaipėdos energija — Klaipėda. Biomass + waste + (declining) gas. Major bioenergy switch post-2014.

---

## Key actors

Utility: Ignitis (state). DH: VŠT (Vilnius), Kauno energija. HP brands: NIBE, Daikin, Stiebel Eltron.

---

## National programmes

APVA (Environmental Project Management Agency) — HP grants up to €14,500. Multi-apartment renovation programme. NRRP funds.

**Subsidies:** APVA HP grants up to €14,500 — among most generous in EU per house.

---

## Risk flags

- Klaipėda LNG dependency — single point of failure.
- Russia/Belarus border — geopolitical risk.
- Multi-apartment DH stock requires modernisation.
- Smaller installer base.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---


## EUBUCCO bottom-up heat demand build (build group 1 (DE + Baltics))

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/lt.yaml`; methodology: `literature/lithuania/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 2 NUTS2 / 10 NUTS3 |
| TABULA typology | PL (proxy) |
| Climate multiplier | 1.1522 |
| Retrofit blend factor | 0.9504 |
| comfort_regime deflator | - |
| eubucco area_correction | 0.52 (Mechanism A, imputed-floor data quality) |
| class_mix proxy | yes |
| Census floor-area benchmark | 104 Mm2 (census/EUBUCCO 0.52) |
| Hotmaps 2015 benchmark | 17.29 TWh |
| **Bottom-up result** | **18.1 TWh** (+4.8 % vs Hotmaps, OK) |

Applied corrections: class-mix proxy (per-class typology); EUBUCCO area_correction 0.52 (imputed-floor over-count).

**Insight (2026-05-25):** Lithuania reconciles at +4.8 % via a `tabula.class_mix` proxy (Swedish SFH for the wooden detached stock + Polish MFH for the Soviet panel blocks) plus an `area_correction` 0.52 (Statistics Lithuania census). Both layers are census/typology-grounded, not Hotmaps-tuned.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 12% · oil 4% · biomass 35% · resistance 3% · heat pump (air 10% + ground 0%) · district heat 36%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €117 | €122 | €107 |
| Heat pump (air) | €80 | €76 | €60 |
| Heat pump (ground) | €73 | €68 | €52 |
| Hydrogen boiler (CENTRAL) | €211 | €107 | €68 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 64% · district heat 36% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 40%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 31%, stock turnover 5.6%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.84**, range [0.63–1.08] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 16 (16 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 21 [19–26], new-build 32 [26–42] (central [low–high]); across the delivered-H2 supply band 16 [5–29].

<!-- /COUNTRY_MODEL_UPDATE -->
