# United Kingdom — building classification & heat-intensity methodology

Build group 7 (UK + CH; non-EU additions, Phase 1F). Companion to `code/data/country_config/uk.yaml`.

## 1. Status and how the UK differs from the EU-27 builds

The UK is the first non-EU country in the set. It is **not a TABULA-12 participant**, but it has the richest national residential stock-energy evidence base in Europe (English Housing Survey + Cambridge Housing Model + RdSAP). The UK is therefore built as a **direct national typology** (`uk_intensities.csv`), not a proxy, with `climate_multiplier = 1.0`.

Two structural differences from the EU-27 pipeline:
- **Statistical geography:** EUBUCCO v0.2 added the UK on the **NUTS 2016 `UK`-prefixed vintage** (40 NUTS2, 173 NUTS3), the last EU vintage before Brexit. The post-2021 ITL (`TLxxx`) codes are not used. Any join to current ONS data needs a NUTS-2016 → ITL-2021 crosswalk.
- **EUBUCCO source:** the UK has no open national building register, so its EUBUCCO footprints are **OpenStreetMap + Microsoft-ML**. Footprint coverage is good but `construction_year` / `type` attributes are sparse — expect a **fallback-dominated** (unknown-cohort) result driven by the `uk_intensity.csv` BSO stock weights. Northern Ireland (`UKN0`) is the highest-risk partition.

## 2. Data sources

- **EUBUCCO v0.2** (UK NUTS2 partitions; OSM + Microsoft footprints). Coverage confirmed via docs.eubucco.com/v0.2 (v0.1/Sci.Data paper covered EU-27 + CH only and is NOT a UK source).
- **Heat intensities (`uk_intensities.csv`, direct):** Cambridge Housing Model (DECC/BRE; RdSAP physics over the EHS); English Housing Survey 2022-23 Energy Report (DESNZ/MHCLG); UK Housing Energy Fact File 2013 (Palmer & Cooper). SH intensity by 6 cohorts × 3 classes; flats most efficient per EHS. RESEARCH-SYNTHESISED, ±20-30 % (SAP-modelled vs metered "performance gap", especially pre-1919 solid wall).
- **Climate:** Eurostat `nrg_chdd_a` (UK historically reported); 2018-2022 mean ≈ 2500 HDD base 15 °C (NEEDS_VERIFY — base 15.5 gives ~2400-2700; Met Office HadUK as fallback).
- **Retrofit shares (0.35 / 0.45 / 0.20):** EHS 2022 EPC distribution (A-C 48 %, D 43 %, E-G 9 %) + ECO / Great British Insulation Scheme / Boiler Upgrade Scheme history; ~8 M solid-wall homes remain the un-insulated "original" tail.
- **Reconciliation:** Hotmaps 2015 (EU28-era) — **467.70 TWh**, sum of `heat_2015_MWh` across all 174 UK NUTS3 rows in `building_stock_nuts3.csv` (verified 2026-05-21). Cross-check vs DESNZ ECUK residential space heating ~330 TWh (final-energy basis).

## 3. Occupancy / heated-base note

UK Census 2021: occupied ~93.5 %; vacant + second homes ~6.5 %, **largely unheated** in the mild UK climate (frost protection only). Per the area-methodology policy (`literature/eubucco_census_area_audit.md`), the UK is a candidate for **both** a Mechanism-A correction (OSM/Microsoft imputed floors) and a Mechanism-B occupancy correction — but **no `area_correction` is applied in this initial build**. It will be sized only after the first Colab run reveals the EUBUCCO UK area and the native Hotmaps gap (not pre-fitted to the benchmark).

## 4. Verification status

Verified 2026-05-21: NUTS2/NUTS3 code lists (NUTS 2016 UK vintage), Hotmaps benchmark (467.70 TWh), EUBUCCO v0.2 UK coverage, input-chain load + `build_intensity_lookup` (blend 0.7225; class fallbacks SFH 130 / MFH_LOW 118 / MFH_HIGH 110 kWh/m²).

NEEDS_VERIFY: exact UK HDD 2018-2022 mean; `uk_intensities.csv` vs EHS 2022-23 energy tables; EUBUCCO UK `construction_year` completeness + NI partition; `census_floor_area.eubucco_mm2` + ratio (pending first build).

## 5. Change log

- 2026-05-21: UK package created (group 7). Direct CHM/EHS typology; Hotmaps 467.70 TWh; area/occupancy correction deferred to post-first-build assessment.
- 2026-05-24: download fix -- `nuts2_partitions` corrected to EUBUCCO's NUTS 2016 UK keys (42; Scotland UKM5-9 + NI UKN0/UKN1; the older UKM2/UKM3 from the Hotmaps file 404'd).
- 2026-05-24: **first Colab build -- 368.9 TWh = -21.1 % vs Hotmaps (ACC).** UK is NOT an area case: EUBUCCO area 2933 Mm2 vs census 2750 Mm2 = ratio 0.94 (within 6 %), so NO `area_correction` applied. The -21 % is an intensity-layer under-shoot (build is 99.9 % unknown-cohort -> stock-weighted CHM/EHS x 0.7225 blend ~126 kWh/m2 vs Hotmaps-implied ~159). Likely driver: the retrofit blend over-discounts the un-retrofitted solid-wall stock. Within ACC band -> left native; a retrofit-share revisit (raise the "original" share) is the candidate refinement. All 29 countries now have first-run results.
