# Finland (FI)

> **RQ relevance:** Highest HP penetration per household after Norway (524/1000 households). 45% residential DH share. Coldest climate of EU (3,714 heating hours). Oil boiler phase-out by 2030 in all buildings. Strong domestic HP industry. Helsinki cogen-DH historic model.

---

## Snapshot

| Metric | Value | Source |
|---|---|---|
| Residential gas price (H1 2025) | €95/MWh | Eurostat nrg_pc_202 |
| Residential electricity price (H1 2025) | €180/MWh | Eurostat nrg_pc_204 |
| Grid CO₂ intensity 2025 | 80 gCO₂/kWh | EMBER 2024 |
| Grid CO₂ intensity 2050 | 5 gCO₂/kWh | EEA Fit-for-55 |
| Gas grid coverage | 5% of buildings | Policy.py (model) |
| Heat pump SCOP (air, 2025) | 2.55 | Hotmaps HDD; EHPA |
| Annual heating hours | 3714/year | Hotmaps |

---

## Policy

| Measure | Year |
|---|---|
| Fossil Boiler Subsidies End | 2025 |
| New Build Fossil Ban | 2025 |
| Replacement Fossil Ban | 2035 |
| Full Fossil Ban | 2040 |
| Hp Mandate Year | 2035 |


**Context:** High district heating penetration. Oil boiler ban in new builds. Gas grid coverage very low outside Helsinki metro.

---

## Economics (LCOH at CENTRAL carbon scenario)

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €148 | €152 | €130 |
| Heat pump (air) | €88 | €82 | €59 |
| Heat pump (ground) | €75 | €70 | €52 |
| H₂ boiler (CENTRAL) | €268 | €188 | €102 |

> **Labour-cost adjustment applied:** Country multiplier **1.15** (EU27 construction = 1.00, Eurostat lc_lci_lev 2024) scales the installation portion of CAPEX (tech-specific labour share: HP_air 40%, HP_ground 55%, gas boiler 30%, DH 50%, H₂ boiler 35%) and 70% of FOM.


---

## Building stock (model data)

| Building type | Dwellings (model) | Heat (TWh) |
|---|---|---|
| SFH | 2,226,821 | 9.55 |
| MFH_HIGH | 3,334,397 | 13.93 |
| OTHER | 11,315,323 | 54.66 |


> Caveat: model OTHER category over-counts; cross-reference national statistical offices.

---

## EUBUCCO building-stock build (bottom-up heat demand)

Independent bottom-up estimate from the country-build pipeline (EUBUCCO v0.2 +
Sweden-proxy TABULA). Method: `literature/country_build_methodology.md` and
`literature/finland/classification_methodology.md`. Colab run 2026-05-17.

> **Sweden-proxied intensities.** Finland is **not a TABULA country**. Its
> residential heat intensities are taken from the **Sweden** TABULA national
> typology brochure and climate-corrected by the Finland/Sweden heating-
> degree-day ratio (1.055). This is the same proxy pattern Luxembourg uses
> with Belgium. Every per-m² heat intensity in this build is, at root, a
> Swedish value scaled to Finland's climate — see the methodology doc.

**Stock classified — 6,633,364 EUBUCCO buildings:**

| Class | Buildings | Heated floor area | Heat demand |
|---|--:|--:|--:|
| SFH | 2.08M | 0.31 bn m² | 45.3 TWh |
| MFH_LOW | 0.27M | 0.19 bn m² | 19.9 TWh |
| MFH_HIGH | 9,312 | 0.03 bn m² | 3.7 TWh |
| NON_RESIDENTIAL | 4.27M | — (out of scope) | — |
| **Residential total** | **2.36M** | **0.53 bn m²** | **68.9 TWh** |

**Reconciliation (residential space heating + DHW):**

| Source | TWh/yr | vs bottom-up |
|---|--:|--:|
| **Bottom-up (this build)** | **68.9** | — |
| Hotmaps 2015 | 78.1 | **−11.8 %** |
| EU BSO (implied) | 65.8 | +4.7 % |
| Statistics Finland 2023 | 42.0 | +64 % |

> The 42.0 TWh is the verified national residential space-heating figure
> (Statistics Finland, *Energy consumption in households 2023*); it occupies
> the Odyssee-Mure benchmark slot. The 2026-05-17 run's CSV still shows the
> pre-verification 40 TWh estimate — it refreshes to 42 on the next Colab run.

**Insights:**
- **In-band.** −11.8 % vs Hotmaps is inside the ±25 % target *and* the tighter
  ±15 % "consistent" tier — research-quality, the same band as France.
- **Cohort coverage is near-zero.** ~98 % of residential buildings have no
  EUBUCCO construction year, so the result is driven by the unknown-cohort
  stock-weighted fallback intensity, not a genuine per-vintage calculation.
  This is the Luxembourg situation (also ~0 %), not the France one (72 %
  coverage). Disclosed as a limitation: the headline total is robust but the
  cohort breakdown above is fallback-dominated.
- **Sweden-proxied.** Every intensity is a Swedish TABULA value × the FI/SE
  HDD ratio (1.055) × the retrofit blend (0.858) + DHW. MFH_LOW and MFH_HIGH
  share intensities because the Sweden TABULA typology has one MFH class.
- **Non-residential dominates the building count.** 4.27M of 6.63M buildings
  (64 %) classify as NON_RESIDENTIAL — Finland's stock is full of summer
  cottages, saunas and outbuildings — but they carry zero heated area and are
  out of scope for the residential total.

**Key build parameters:** TABULA source Sweden (proxy); climate multiplier
1.055; retrofit blend 0.858 (factors 0.74 / 0.49 from the Sweden brochure;
shares a placeholder pending Finnish data); DHW 16 / 17 kWh/m²·a (SFH / MFH);
`floor_source: eubucco`. Several parameters are `NEEDS_VERIFY` placeholders —
see `fi.yaml._meta.needs_verify_summary`.

---

## Current heating mix (residential)

**Mix:** District heating ~45% | HP+electric ~38% | Biomass ~9% | Oil ~5% | Gas ~3%

Finland: 45% residential DH (IEA Bioenergy 2024). Three-quarters of distributed heat from biomass. Direct electric resistance + HP common in single-family homes.

---

## Grid CO₂ trajectory

| Year | gCO₂/kWh |
|---|---|
| 2025 | 80 |
| 2030 | 50 |
| 2040 | 20 |
| 2050 | 5 |

---

## District heating context

**Share:** ~45% of residential heating.

Major operators: Helen (Helsinki — combined w/ data center heat recovery 2025), Vantaan Energia, Tampereen Sähkölaitos. CHP plants core. Biomass + waste + heat pumps + (small) gas.

---

## Key actors

Utilities: Fortum, Helen, Gasum. HP brands: NIBE (Swedish), Suomen Lämpöpumput (Finnish), Bosch.

---

## National programmes

ARA (Housing Finance and Development Centre) grants. Oil boiler replacement grant — €4,000. NRRP-funded HP grants. Low-VAT on HP installations.

**Subsidies:** ARA oil boiler replacement grant €4,000. ETS revenue building improvement fund.

---

## Risk flags

- Coldest climate — air-source HPs less efficient at -20°C. Ground-source or hybrid often needed.
- Biomass sustainability — Finnish forests under EU LULUCF scrutiny.
- Helsinki DH still partly coal — Hanasaari closed 2023, Salmisaari to follow.
- Industrial competition for biomass (paper, pulp).
- Very limited gas market — pipeline only to Helsinki area.

---

## Model results (historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)

_Country not among the top-15 reported per-country emitters (small absolute heat demand). Approximate tech shares follow the regional/EU pattern — see `code/results/mc_summary_STATED_POLICIES.csv` for the EU aggregate._


---

---

## Regional heat demand (NUTS)

**National total (model baseline, 2015):** 78.1 TWh  
**NUTS coverage:** 2 NUTS1 · 5 NUTS2 · 19 NUTS3 regions

### By NUTS1 (macro-region)

| NUTS1 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `FI1` | Manner-Suomi | 77.71 | 99.5% | 16,780,335 |
| `FI2` | Åland | 0.43 | 0.5% | 96,206 |

### By NUTS2 (top 10 + Other)

| NUTS2 code | Region | Heat demand (TWh) | Share | Dwellings |
|---|---|---|---|---|
| `FI1B` | Helsinki-Uusimaa | 22.65 | 29.0% | 5,619,145 |
| `FI1D` | Pohjois- ja Itä-Suomi | 19.44 | 24.9% | 2,658,266 |
| `FI19` | Länsi-Suomi | 19.05 | 24.4% | 4,584,390 |
| `FI1C` | Etelä-Suomi | 16.57 | 21.2% | 3,918,534 |
| `FI20` | Åland | 0.43 | 0.5% | 96,206 |

> Full NUTS3 detail is in `data/heat_demand_regions.csv`. Central copy: `code/data/processed/heat_demand_by_region/FI.csv`. Source: Hotmaps regional heat demand baseline (2015), aggregated from `code/data/processed/building_stock_nuts3.csv`.
> ⚠️ **Caveat on dwelling counts:** the "Dwellings" column aggregates SFH + MFH_HIGH + OTHER building types from the model's `building_stock_nuts3.csv`. The OTHER bucket over-counts non-residential records; cross-reference national statistical offices for accurate residential dwelling counts. Heat demand (TWh) is the reliable column — sourced from Hotmaps 2015 baseline.


---

## Sources

See [sources.md](sources.md).


## EUBUCCO bottom-up heat demand build (build group proof-of-concept)

Spatially-resolved residential heat demand from EUBUCCO v0.2 building footprints x TABULA-style heat intensities (pipeline `code/scripts/country_build/01-04`). Config: `code/data/country_config/fi.yaml`; methodology: `literature/finland/classification_methodology.md`.

| Parameter | Value |
|---|---|
| EUBUCCO partitions | 5 NUTS2 / 19 NUTS3 |
| TABULA typology | SE (proxy) |
| Climate multiplier | 1.055 |
| Retrofit blend factor | 0.858 |
| comfort_regime deflator | - |
| eubucco area_correction | - |
| class_mix proxy | no |
| Census floor-area benchmark | 248 Mm2 (census/EUBUCCO 0.47) |
| Hotmaps 2015 benchmark | 78.14 TWh |
| **Bottom-up result** | **68.9 TWh** (-11.8 % vs Hotmaps, OK) |

Direct/proxy TABULA with no post-hoc correction (native bottom-up reconciles with Hotmaps).

**Insight (2026-05-25):** Finland reconciles at -11.8 % using the Swedish typology as proxy (Sweden is the only TABULA country colder than Finland). Inherits the SE matrix's older-SFH definitional ambiguity (upstream, disclosed); within the OK band.

References: [`literature/eubucco_census_area_audit.md`](../../literature/eubucco_census_area_audit.md) (area / occupancy methodology); [`literature/inv_countries_academic_refinements.md`](../../literature/inv_countries_academic_refinements.md) (INV-cluster corrections); [`literature/climate_reference_hdd_audit.md`](../../literature/climate_reference_hdd_audit.md) (Option B reference-HDD).

---

<!-- COUNTRY_MODEL_UPDATE -->

## Country-specific model update (2026-06-12)

*Reflects the source-audited techno-economics (DEA-corrected CAPEX; [scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), the per-country 2025 heating mix ([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the per-country least-cost pathway ([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), and the grounded hydrogen supply + distribution-infrastructure assessment ([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). Supersedes any LCOH / mix figures earlier in this file that predate 2026-06-12.*

**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + national/EHPA, mean of bases): gas 1% · oil 10% · biomass 18% · resistance 24% · heat pump (air 10% + ground 9%) · district heat 28%.

**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**

| Technology | 2025 | 2030 | 2050 |
|---|---|---|---|
| Gas boiler | €133 | €137 | €115 |
| Heat pump (air) | €93 | €88 | €70 |
| Heat pump (ground) | €85 | €80 | €60 |
| Hydrogen boiler (CENTRAL) | €217 | €110 | €69 |

**Merit-order winter peak:** hydrogen never beats the gas peaker or the cold-snap heat pump here in any scenario (endogenous cold-snap power price ~€240/MWh).

**District-heating supply stack (Net Zero, 2050):** H2 ranks 5 of 5 sources by marginal cost and does not undercut the gas CHP at the peak.

**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix heat pump 66% · district heat 34% · H2 0% · biomass 0% · fossil 0%. Under a per-country cap, the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target).

**Per-country COST_OPT parameters:** sustainable-biomass ceiling 30%, H2-for-buildings ceiling 2050 0%, demand reduction by 2050 38%, stock turnover 6.3%/yr.

**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, grounded 2026-06-12 from the per-country supply-route assessment, [h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): central **0.87**, range [0.65–1.12] — renewable-rich domestic production.

**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** baseline 9 (9 EUR/MWh above the best heat pump, free gas-grid reuse). With hydrogen paying its distribution network: retrofit 12 [11–15], new-build 18 [15–24] (central [low–high]); across the delivered-H2 supply band 9 [-3–22].

<!-- /COUNTRY_MODEL_UPDATE -->
