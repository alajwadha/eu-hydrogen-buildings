# Step 3 — Building Stock Layer: Research Summary

**Prepared for:** Ali Alajwad & Dr. Abdurahman Alsulaiman
**Date:** May 2026
**Status:** Module implemented in `code/src/BuildingStock.py` (Hotmaps + Eurostat + UK ONS). EUBUCCO Luxembourg build complete (commit `055ec1f`), pending Abdul sign-off before scale-out to all 29 countries. Flags for Abdul marked ⚠️.

> **2026-05-15 update.** Section 4 (below) was originally written when the build pulled both EUBUCCO and the GBA (Global Building Atlas) ODbLPolygon tile. After running the build end-to-end, GBA was retired from the runtime pipeline (commit `b06998c`). The GBA cross-check yielded one stable finding — residential floor area in GBA is ~1.4× EUBUCCO's, consistent with GBA's looser polygon definition — which is preserved in the paper methodology citing Zhu et al. (2025). The text below retains the dual-source narrative for historical accuracy; the runtime pipeline is now EUBUCCO-only. See `literature/assumptions_register.md` entry 2026-05-15 for full rationale.

---

## What this layer adds to the model

Step 3 produces per-NUTS3 building-stock characteristics that drive:

- **Total heat demand by region** (input to LCOH-weighted Monte Carlo)
- **Building-class mix** (SFH vs MFH) — determines heat-pump retrofit feasibility, district-heat suitability, and the relative cost of envelope refurbishment
- **Per-class heated floor area** — used to convert per-m² intensity values from TABULA/EU BSO into absolute demand
- **HP and DH feasibility scores** — heuristic 0–1 multipliers that scale technology share in the softmax blending step

Implementation lives in `code/src/BuildingStock.py` with five functions:
`load_hotmaps_regional`, `load_eurostat_census`, `load_uk_ts044_shares`, `build_building_stock`, `build_hp_dh_feasibility`. The processed output is `code/data/processed/building_stock_nuts3.csv` (3,823 rows, 1,397 NUTS3 regions).

A finer-grained replacement pipeline using EUBUCCO + Global Building Atlas is documented in §4 of this file and being first applied on Luxembourg in `code/scripts/luxembourg/`.

---

## 1. Current data sources

### 1.1 Hotmaps regional heat demand (2015 baseline)

Hotmaps is the primary source of regional **heat demand** in the current model. The dataset provides residential and service-sector space heating + DHW demand at hectare resolution (100 × 100 m) across EU28 + Norway + Iceland + Switzerland, aggregated to NUTS3 for our model.

**Methodology** (Hotmaps Project, IEE 2016-2020): top-down approach combining

- Population grid at hectare level
- Building construction age distribution
- Heating Degree Days (HDD)
- National statistics of energy demand per floor area

Two parallel estimation strategies are blended:
1. **Population-based**: hectare population × NUTS3 average gross floor area per person (from European Census Hub)
2. **Building-area-based**: independent dataset for non-residential coverage

The population-based approach is more accurate for residential stock; the area-based one corrects for non-residential.

**Validation against UK community-led feasibility studies** (10 sites, Community Heat UK 2023): Hotmaps consistently **underestimates** annual thermal demand by ~25% on average. This is a known limitation of top-down methods that miss localised high-demand buildings (older churches, schools, industrial-adjacent residential).

⚠️ **Implication for our model:** national totals from Hotmaps are conservative. The 3,863 TWh/year EU + CH + UK total (across our 29 countries) is likely 10-25% lower than reality. Cross-check against Eurostat ENER/NRG_BAL recommended.

### 1.2 Eurostat 2021 Census (`cens_21dwob_r3`)

Provides **dwelling counts by building type** at NUTS3 resolution. Building types follow the Conference of European Statisticians Recommendations for the 2020 Censuses of Population and Housing:

- Detached house
- Semi-detached house
- Row / terraced house
- Apartment in a building with 5+ storeys
- Apartment in a building with fewer than 5 storeys
- Other types of accommodation

Geographic coverage: NUTS2 in 23 tables and NUTS3 in 12 tables.

**Note on dataset code:** the current implementation in `BuildingStock.py` loads `cens_21dwbno_r3` — this appears to be a typo. The Eurostat code is `cens_21dwob_r3` ("DWelling, Occupancy status, type of Building, region"). Verify in next run.

⚠️ The 6-category Census taxonomy is aggregated in our model into 3 classes (SFH / MFH_HIGH / OTHER). The "OTHER" bucket over-counts non-residential dwellings — confirmed for Germany where OTHER is 67% of the dwelling count vs the realistic ~10-15%. This is fixed by the EUBUCCO build (§4).

### 1.3 UK ONS TS044 (Accommodation Type)

The UK is not in the Eurostat census so we substitute the ONS 2021 Census Table TS044, which uses an England/Wales accommodation taxonomy:

- Detached
- Semi-detached
- Terraced
- Purpose-built block of flats / tenement
- Converted / shared house
- Other converted building (school, church, warehouse)
- Commercial building

National shares are applied uniformly across all UK NUTS3 regions (174 regions). This is a strong simplification — Greater London has very different mix than rural Wales.

⚠️ For Scotland and Northern Ireland we use the national England/Wales shares; this should be replaced with NRS (Scotland) and NISRA (Northern Ireland) when time permits.

---

## 2. Building typology — what the literature says

### 2.1 TABULA / EPISCOPE harmonised typologies

The **TABULA** (IEE 2009-2012) and follow-up **EPISCOPE** projects developed harmonised residential building typologies across 20 European countries. Each national typology classifies buildings by:

- **Size class**: SFH, terraced, MFH, apartment block
- **Age cohort**: 5–7 construction-period bands, country-specific
- **Refurbishment level**: original / standard refurbishment / advanced refurbishment

For each archetype, TABULA provides U-values, building element shares, and standardised energy performance via ISO 13790 (seasonal method).

**Useful values for cross-validation:**
- Single family / terraced: ~10 kWh/m²·a useful heating for hot water (TABULA WebTool)
- Multi-family / apartment block: ~15 kWh/m²·a useful heating for hot water
- Pre-1970 Swiss SFH: 170–200 kWh/m²·a final energy for space heating
- 525% range in final energy demand from newest to oldest cohort within same archetype (Streicher et al. 2019, Swiss CECB-Plus 25,000-building analysis)

⚠️ **Decision pending for script 03_heat_intensity.py:** TABULA is the academic standard but only covers ~13-20 countries; Luxembourg specifically is not in TABULA. For LU we would use Belgium or Germany as proxy archetype. Alternative is EU Building Stock Observatory (§2.2).

### 2.2 EU Building Stock Observatory (BSO)

The EU BSO was relaunched December 2025 (DG Energy) with a streamlined three-domain structure:
1. **Building stock** (counts, floor areas)
2. **Renovation rates**
3. **Energy consumption**

Key 2025 facts:
- **111 million buildings** in EU27 (101M residential, 10M services)
- 300+ MtCO2e direct fossil fuel emissions from residential sector (2021)
- 130+ MtCO2e from service sector
- 9.3% of EU population unable to keep home adequately warm (energy poverty 2022)
- 14.8% live in homes with structural issues

⚠️ The 2025 BSO is much more usable than earlier versions (the previous BSO had many "empty bottles"). Worth reviewing whether it should replace Hotmaps as our primary stock source for 2030+ scenarios, or be used as cross-validation.

### 2.3 Country-level building stock variance

Per-country dwelling type distributions vary dramatically (OECD HM1.5 housing stock database):

- **Detached/SFH-dominant** (>50%): Ireland, UK rural, Belgium, Netherlands urban
- **Apartment-dominant** (>60%): Spain, Italy urban, all CEE (Plattenbau legacy), Korea
- **Mixed**: France, Germany (regional split between Bundesländer)

⚠️ This is captured in our model only at the country level via Eurostat — finer regional variation is being added via the EUBUCCO build.

---

## 3. HP and DH feasibility — what the literature says

### 3.1 Heat pump retrofit feasibility

The current model assigns heuristic feasibility scores:

| Building class | HP score | Rationale |
|---|---|---|
| SFH | 0.9 | Outdoor unit placement trivial; low-temp retrofit feasible |
| MFH_HIGH | 0.5 | Shaft space + electrical capacity constraints |
| OTHER | 0.6 | Mixed (industrial easier, retail harder) |

**JRC EUR 31699 EN (2023) findings:**
- REPowerEU target: 30 million heat pumps installed by 2030
- JRC sees manufacturing capacity reaching ~47 GW/year by 2030 in conservative scenario
- Highest projected increases in NECPs: Spain, Hungary, Belgium, Poland
- Largest projected ambient heat from HP: Italy (5.7 Mtoe), France (4.5 Mtoe) by 2030

**Multi-family barriers** (EHPA position 2025, EHPA Nov 2023 facts):
- **Technical:** providing required heating capacity at supplied temperature; many pre-1970 MFH buildings need envelope refurb or >60°C supply temp (which crashes COP); access to heat source (no roof/yard for ASHP)
- **Non-technical:** complex ownership structure; high investment cost; refrigerant volume limits (EN 378); requires resident coordination

**MFH HP case studies** (NRDC 2019 + EHPA case studies 2023-2024):
- Central air-to-water HP works for buildings with existing hot-water distribution (can reuse piping)
- Steam heating systems require ripping out distribution piping — adds 30-50% to cost
- Plant-room space requirement: ~1.5x larger than the gas boiler it replaces
- Best retrofits target ground-source HP using existing courtyards or geothermal fields

⚠️ Our 0.9 / 0.5 / 0.6 scores are placeholders. Need Abdul's validation. Suggested range from literature:
- SFH: 0.85-0.95 (consistent with current)
- MFH_LOW (3-5 floors): 0.55-0.70 (we don't have this class yet — comes with EUBUCCO build)
- MFH_HIGH (≥6 floors): 0.30-0.50 (current 0.5 sits at upper edge)
- NON_RESIDENTIAL: 0.40-0.60 depending on subtype

### 3.2 District heating feasibility

The current model heuristic:

| Building class | DH score | Rationale |
|---|---|---|
| SFH | 0.3 | Long pipe-per-house ratio kills economics |
| MFH_HIGH | 0.8 | High linear heat density |
| OTHER | 0.4 | Mixed |

**Heat Roadmap Europe (HRE) thresholds** for "economic DH feasibility":
- **Linear heat density**: 1.4-1.5 MWh per metre of pipe per year (Gudmundsson 2013; Persson et al. 2014)
- **Spatial heat density**: 150 MWh/ha/year (Persson et al. 2014)
- **EU28 threshold**: 50 MJ/m² per year for dense urban areas (Persson et al. 2019)

**Pan-European Thermal Atlas methodology** (HRE Persson et al. 2018): high-resolution disaggregation of national demand to hectare grid; identifies coherent supply zones via spatial clustering.

**EU-27 DH potential trajectory** (Fallahnejad et al. 2024, *Applied Energy*):
- Current DH share: ~15% of EU residential heat demand
- 2050 economic potential: **31%** under decarbonisation scenario
- 39% of DH potential sits in areas with distribution costs above €35/MWh
- Most Member States have average DH distribution costs €28-32/MWh

**EHPA position (October 2025)** introduces a new dimension: low-temperature ambient-loop networks ("mini thermal grids") connecting handfuls of buildings — blurs the line between HP and DH technology categories. Worth tracking but currently not in our model.

⚠️ Our DH scores don't reflect linear-heat-density-based feasibility. A better implementation would compute per-NUTS3 linear heat density and threshold against 1.5 MWh/m. This requires GIS data we don't currently have processed. Defer to subsequent.

---

## 4. EUBUCCO + GBA — the replacement pipeline

After running EUBUCCO + GBA for Luxembourg and confirming the pipeline works, we plan to **replace the Hotmaps + Eurostat building stock layer for all 29 countries**. The build is documented separately in `literature/luxembourg/classification_methodology.md`; key facts summarised here for the Step 3 narrative.

### 4.1 EUBUCCO v0.2

European Building Stock Characteristics in a Common and Open database (Milojevic-Dupont et al. 2023; v0.2 release 2024-2025).

- **322+ million buildings** across EU27 + Norway + Switzerland + UK
- Composed of 55 open datasets: 62% government registries, 17% OpenStreetMap, 20% Microsoft footprints
- Per-building attributes: footprint geometry, **type** (residential / non-residential), **height**, **construction year**
- Coverage in v0.1: 73% have height, 46% have type, 24% have age. v0.2 expected to be higher.
- License: ODbL v1.0 (commercial OK)
- Distribution: per-NUTS2 partitioned GeoParquet, accessible anonymously via S3 (no auth/registration)
- DOI: 10.5281/zenodo.7225259

### 4.2 Global Building Atlas (GBA)

Zhu et al. (2025), ESSD. Three components, three licenses:

- **GBA.Polygon** — 2.75 billion buildings worldwide, footprints with predicted height (CC BY-NC)
- **GBA.LoD1** — 2.68 billion LoD1 3D models (CC BY-NC)
- **GBA.Height** — 3 × 3 m global height raster, RMSE 1.5-8.9 m (CC BY-NC)
- **GBA.ODbLPolygon** — footprints only, ODbL (commercial-OK subset of GBA.Polygon)
- DOI: 10.14459/2025mp1782307

For this project we **deliberately use only `GBA.ODbLPolygon`** to preserve commercial-compatible licensing of the downstream model output. Height attributes come from EUBUCCO; GBA is used for polygon-completeness cross-validation.

### 4.3 Classification scheme (replaces current 3-class with 4-class)

The build classifies every building into one of four classes:

- **SFH** — Single-family house (detached, semi-detached, terraced)
- **MFH_LOW** — Multi-family house, low-rise (3-5 floors)
- **MFH_HIGH** — Multi-family house, mid/high-rise (≥6 floors)
- **NON_RESIDENTIAL** — Commercial, industrial, office, retail, public

Decision rules (sequential, first match wins):
1. EUBUCCO `type` starts with "non-" → NON_RESIDENTIAL
2. floors ≥ 6 AND footprint ≥ 800 m² → MFH_HIGH
3. floors ≤ 2 AND footprint < 250 m² → SFH
4. 3 ≤ floors ≤ 5 → MFH_LOW
5. else → MFH_HIGH (conservative default)

where `floors = round(height_m / 3.0)` for residential, `/ 3.5` for non-residential, NaN if height missing.

**Heated floor area** = footprint × floors × 0.85 (TABULA / ISO 52000-1 useable-area fraction).

**Why six floors is the high-rise threshold:** EU lift mandate kicks in at 5-6 floors; construction shifts from masonry/timber to concrete frame; EN 378 refrigerant volume limits create a discontinuous HP-retrofit barrier. The 800 m² footprint co-requirement filters narrow 6-floor row houses (which behave like MFH_LOW, not towers).

**Why 250 m² for SFH:** matches EU SFH typology midpoint + row-house upper bound from TABULA + Hotmaps building stock distributions.

⚠️ The "ambiguous-default-to-MFH_HIGH" rule is conservative for HP feasibility (over-counts the hardest-to-electrify class, understates achievable uptake) but anti-conservative for DH feasibility (overstates connectability). Decision: keep as-is for OIES paper (HP-feasibility focus); revisit if/when we expand to DH-specific scenarios.

### 4.4 Validation plan

Before scaling from Luxembourg to all 29 countries, the country output is checked against:

1. **STATEC 2021 census**: ~241,000 dwellings in residential buildings in Luxembourg. Sum of SFH + MFH_LOW + MFH_HIGH heated_floor_area / typical Luxembourgish dwelling size (~120 m²) must be within ±15%.
2. **Eurostat ENER/NRG_BAL**: total residential heated floor area × per-m² intensity should reconcile with Luxembourg residential final energy consumption.
3. **Luxembourg Cadastre 2020**: per-class share must align with official cadastre typology within ±25%.

⚠️ **Decision gate:** if all three validations pass within tolerances, scale to all 29 countries. If any fails by more than ±25%, revisit the classification thresholds (the 6-floor / 800 m² / 250 m² cuts) before scale-out.

### 4.5 Scale-out plan (post-validation)

Once Luxembourg validates:

1. Refactor `01_download.py` to loop over all 29 EUBUCCO NUTS2 partitions (some countries have many; e.g. Germany has 38)
2. Refactor `02_classify.py` to be parallelised over NUTS2 partitions
3. Country-specific footprint thresholds: Eastern European prefab MFH_LOW has larger per-building footprints than Western European MFH_LOW; the current uniform thresholds may need country-specific tuning
4. Output: replace `code/data/processed/building_stock_nuts3.csv` with a refreshed file that has the four-class breakdown
5. Update Visualise.py and the dashboard to render the new four-class structure

Expected processing time: ~30-60 minutes per country on a modern laptop; 12-24 hours sequential for all 29; parallelisable to 2-4 hours.

---

## 5. Heat intensity (kWh/m²·a) — Luxembourg implementation

> **🔄 May 2026 update:** Real implementation now deployed for Luxembourg. Source decision: **(a) TABULA Belgium proxy + (b) EU BSO LU cross-validation + (c) Hotmaps reconciliation + (e) Odyssee-Mure benchmark**. Detailed methodology and source decision rationale documented in `literature/intensity_source_methodology.md`.

Every classified building gets a per-m² heat demand intensity from a per (class × cohort) lookup, climate-corrected from BE to LU, blended across retrofit states, plus a DHW component.

### Method (deployed in `code/scripts/luxembourg/03_heat_intensity.py`)

For each building:

1. **Cohort assignment** based on EUBUCCO `construction_year`: pre-1945, 1946-1970, 1971-1990, 1991-2010, 2011-2020, post-2020, or "unknown"
2. **TABULA Belgium lookup** for `(building_class, cohort)` → space-heating + DHW intensity (BE original-state)
3. **Climate correction** × (HDD_LU / HDD_BE) = × 1.112 (LU is ~11% colder than BE)
4. **Retrofit blending** × 0.813 = 0.55 × 1.00 + 0.35 × 0.65 + 0.10 × 0.35 (LU stock weights × TABULA refurb factors)
5. **DHW add-on** (climate-insensitive): 22 kWh/m²·a SFH, 19 kWh/m²·a MFH
6. **Heat demand** = intensity × footprint × floors × 0.85

### Data files

- `code/data/raw/tabula/be_intensities.csv` — 18 rows (3 classes × 6 cohorts)
- `code/data/raw/eu_bso/lu_intensity.csv` — 6 rows for cross-validation
- `code/data/raw/lu_national/lu_climate_retrofit.csv` — 11 LU parameters (HDD, retrofit shares, DHW)

### Luxembourg result (May 2026)

| Source | TWh/yr | kWh/m²/yr |
|---|---|---|
| Hotmaps 2015 baseline | 8.27 | 181.2 |
| **Bottom-up (this model)** | **7.84** | **171.9** |
| Odyssee-Mure 2021 LU residential | 7.20 | 157.8 |
| EU BSO 2021 LU weighted-avg | 6.75 | 147.9 |

Bottom-up vs Hotmaps gap: **−5.2%**. Within ±15% tolerance.

The four estimates form a narrow cluster, with the downward trend Hotmaps 2015 → BSO 2025 (−18%) matching Odyssee-Mure's observation of −44% LU specific space-heating consumption between 2000 and 2022.

### Scale-out plan for the other 28 countries

When LU validation completes and Abdul approves scale-out:
- **Direct TABULA**: AT, BE, CZ, DK, DE, FR, GR, IE, IT, NL, NO, PL, ES, SE, UK (15 countries)
- **Proxies needed**: LU→BE, CY→GR, MT→IT, BG→RO (where RO is direct), HR→SI, EE/LV/LT→shared Baltic proxy from FI/SE, SK→CZ, RO→CZ, HU→AT, PT→ES, FI→SE, IS→NO, LI→CH, CH→DE (or own data), SI→IT
- Document each proxy choice in the per-country methodology section

### Open questions for Abdul (heat intensity specifically)

⚠️ See `literature/intensity_source_methodology.md` §5 for the 6 open questions:
1. Retrofit-state shares (55/35/10) — STATEC Energiepass data preferred if available?
2. Climate correction linear in HDD — sufficient or need sub-monthly?
3. BE-only proxy for LU vs blended BE+DE?
4. Non-residential treatment — flat 140 kWh/m² OK for residential-focused OIES paper?
5. Unknown-cohort fallback — EU BSO stock-weighted vs Hotmaps-calibrated?
6. Scale-out: per-country TABULA proxy mapping confirmed?

---

## 6. Per-NUTS3 vs per-NUTS2 vs per-NUTS1 aggregation

The model operates at NUTS3 but produces aggregates at NUTS1 (16-state DE level) and NUTS2 (Bundesländer / régions / autonomous communities level) for visualisation and validation. These have been built into `code/data/processed/heat_demand_by_region/` (added 2026-05-14):

- `heat_demand_NUTS1_all.csv` — 100 macro-regions
- `heat_demand_NUTS2_all.csv` — 284 provinces / Länder
- `heat_demand_NUTS3_all.csv` — 1,369 finest regions
- `{ISO2}.csv` × 29 countries — per-country combined file

Each country profile (`countries/{Country-Name}/README.md`) shows the full NUTS1 breakdown and top-10 NUTS2 regions for that country.

Total across all 29 countries: **3,863 TWh/year** (consistent across all three NUTS levels — sanity check).

---

## Questions for Abdul before further implementation

1. ⚠️ **HP / DH feasibility scores:** keep current heuristic (0.9 / 0.5 / 0.6 for HP; 0.3 / 0.8 / 0.4 for DH), or move to literature-based ranges?
2. ⚠️ **Hotmaps 2015 baseline 10-25% underestimate:** disclose as paper limitation (current plan) or apply a national-level uplift correction?
3. ⚠️ **Heat-intensity source for script 03:** TABULA + EU BSO blend, pure TABULA with country proxies, or different?
4. ⚠️ **Vintage cohort cutoffs:** standard TABULA bands (5-7 per country), or simplified 5-band common across all 29?
5. ⚠️ **EUBUCCO `type` taxonomy:** apply EUBUCCO's `building-type-harmonization.csv` (auxiliary taxonomy file) for finer non-residential subcategories?
6. ⚠️ **Country-specific footprint thresholds:** uniform 250/800 m² across all countries, or country-specific calibration (especially for CEE prefab buildings)?
7. ⚠️ **DH spatial-feasibility refinement:** move from class-based heuristic to linear-heat-density threshold (1.5 MWh/m, Persson et al.)? Requires GIS post-processing — defer to v2?

---

## What the Building Stock layer enables

Once Step 3 is complete and validated:

- **LCOH × dwelling-count weighting** in Monte Carlo (Step 4) becomes accurate at NUTS3 level
- **HP and DH technology shares** computed per region rather than per country
- **Heat-demand sensitivity** to demolition / new-build scenarios becomes representable
- **Renovation-wave modelling** (per-vintage retrofit rate) becomes possible — needs script 03's vintage cohort assignment first
- **Spatial dashboard layer** for the D3 GitHub Pages dashboard — overlay HP/DH suitability on a NUTS3 map

---

## Implementation status

| Component | Status |
|---|---|
| Current 3-class building stock (Hotmaps + Eurostat + UK ONS) | ✅ Implemented (`BuildingStock.py`) |
| HP/DH feasibility heuristic | ✅ Implemented (`build_hp_dh_feasibility`) |
| Per-NUTS3 heat demand from Hotmaps | ✅ Loaded into `building_stock_nuts3.csv` |
| Per-NUTS{1,2,3} aggregation | ✅ Implemented (`aggregate_heat_demand_by_region.py`, 2026-05-14) |
| Per-country regional tables in country READMEs | ✅ All 29 countries (NUTS1 full + top-10 NUTS2 + Other) |
| EUBUCCO build (Luxembourg) | ✅ Scripts written + documented; ⏳ awaiting first run |
| EUBUCCO + GBA scale-out to 29 countries | 🔲 Pending build verification |
| 4-class replacement (SFH / MFH_LOW / MFH_HIGH / NON_RESIDENTIAL) | ⏳ In place for build; pending model integration |
| Heat-intensity per m² (script 03) | ✅ Real implementation deployed: TABULA BE proxy + EU BSO + Hotmaps reconciliation. Bottom-up 7.84 TWh vs Hotmaps 8.27 TWh (−5.2%). See `literature/intensity_source_methodology.md` |
| Vintage-cohort assignment | 🔲 Pending Abdul decision on cohort cutoffs |
| Validation against STATEC / ENER / Cadastre | 🔲 Pending first country run |
| Abdul validation of feasibility scores | 🔲 Pending |
| Disclosure of Hotmaps 25% underestimate in paper | 🔲 Pending Abdul decision (paragraph drafted) |

---

## Sources

- Milojevic-Dupont N. et al. (2023). EUBUCCO v0.1: European building stock characteristics. *Scientific Data* 10:147. https://doi.org/10.5281/zenodo.7225259
- Zhu X.X. et al. (2025). GlobalBuildingAtlas: An Open Global and Complete Dataset of Building Polygons, Heights and LoD1 3D Models. *ESSD*. https://doi.org/10.14459/2025mp1782307
- Loga T., Stein B., Diefenbach N. (2016). TABULA building typologies in 20 European countries. *Energy and Buildings* 132:4-12.
- Streicher K.N. et al. (2019). Analysis of space heating demand in the Swiss residential building stock. *Energy and Buildings* 184:300-322.
- Persson U., Möller B., Werner S. (2014). Heat Roadmap Europe: Identifying strategic heat synergy regions. *Energy Policy* 74:663-681.
- Persson U., Wiechers E., Möller B., Werner S. (2019). Heat Roadmap Europe: Heat distribution costs. *Energy* 176:604-622.
- Fallahnejad M. et al. (2024). District heating potential in the EU-27. *Applied Energy* 353(PB):122206.
- Gudmundsson O., Thorsen J.E., Zhang L. (2013). Cost analysis of district heating compared to its competing technologies. *WIT Trans. Ecology and the Environment* 176:107-118.
- JRC EUR 31699 EN (2023). Heat Pumps in the European Union. JRC134991.
- EHPA (Nov 2023). Heat Pumps in Europe Key Facts & Figures.
- EHPA (Oct 2025). Position on the Heating and Cooling strategy.
- EU Building Stock Observatory (December 2025 release). https://building-stock-observatory.energy.ec.europa.eu/
- Hotmaps Project (IEE 2016-2020). https://www.hotmaps-project.eu/
- Eurostat Census 2021. CENS_21DWOB_R3: Dwellings by occupancy status, type of building, NUTS3.
- ONS England & Wales 2021 Census, TS044 Accommodation Type.
- Community Heat UK (2023). Demand Density assessment — Hotmaps vs UK feasibility studies.

---

## Change log

| Date | Change |
|---|---|
| 2026-05-14 | Initial draft. Documents current Hotmaps + Eurostat + UK ONS implementation. Adds EUBUCCO build methodology and scale-out plan. Includes heat-intensity decision matrix for script 03. |
| 2026-05-14 (PM) | §5 refreshed with real implementation. Replaced placeholder intensities with TABULA BE proxy + EU BSO + Hotmaps reconciliation. Bottom-up total 7.84 TWh vs Hotmaps 8.27 TWh (−5.2% gap, within ±15% tolerance). Detailed methodology in `literature/intensity_source_methodology.md`. Script 02 also updated to expose `construction_year` to script 03. |
