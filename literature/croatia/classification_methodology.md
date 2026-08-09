# Croatia — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country HR`).
**Config:** `code/data/country_config/hr.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Croatia — a build-group-2 country (IT + SI, HR, MT).

**The headline fact:** Croatia is **not a TABULA country**. Its residential heat intensities are **Slovenia-derived** — extracted from the Slovenian TABULA typology and climate-corrected by the Croatia/Slovenia heating-degree-day ratio. This is the proxy methodology used for Luxembourg (Belgium), Finland (Sweden) and the Baltic states (Poland).

---

## 1. Methodology relative to Luxembourg and France

Croatia is a **proxy country**, following the Luxembourg branch (proxy + climate correction). All other elements — taxonomy, floor-height assumptions, `floor_source: eubucco`, the per-cohort intensity lookup with stock-weighted fallback, the multi-source reconciliation, the 8-page diagnostic PDF — are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Under NUTS 2016 Croatia had 2 NUTS2 regions: **HR03 Jadranska** (Adriatic/coastal) and **HR04 Kontinentalna** (continental, incl. Zagreb). The 4-region split (HR02/HR03/HR05/HR06) only came with NUTS 2021 and post-dates EUBUCCO's geometry base.

**NUTS3 vintage caveat.** Croatia has 21 NUTS3 counties. `hr.yaml` lists the NUTS 2021 codes (from the repo GISCO file); EUBUCCO v0.2 uses NUTS 2016, where the counties were coded under HR03x/HR04x. `02_classify.py` assigns buildings to NUTS3 by spatial join / EUBUCCO `region_id`, so the join is robust to the code-vintage difference. EUBUCCO documentation also flags Croatia as a **low-coverage country** (sparse construction-year attribute) — expect the result to be fallback-dominated. Both flagged `NEEDS_VERIFY`.

### 2.2 TABULA — Slovenia as proxy

**Croatia has no national TABULA typology.** Slovenia is chosen as the proxy because:
1. Croatia and Slovenia were both Yugoslav republics until 1991 and share the same socialist-era multi-family apartment-block construction system (1960s–1980s estates), comparable post-war detached masonry SFH, and the same building-code lineage of the period.
2. Of the TABULA countries, Slovenia is the closest single-country analogue to Croatia's continental, multi-family-heavy stock. Italy is too warm (HDD ratio 1.23), Austria too cold/alpine (0.65). Serbia is a defensible secondary cross-check (shared Yugoslav tradition) but is not in Eurostat HDD data.
3. Croatia is **warmer** than Slovenia, so the climate correction is **below 1.0**.

**Extraction:** `code/data/raw/tabula/si_intensities.csv` (shared with Slovenia). The Slovenian TABULA values are themselves derived from the ZRMK aggregate report — see `literature/slovenia/classification_methodology.md`. Note the inherited limitation that MFH_LOW and MFH_HIGH carry identical intensities (the ZRMK 2-class scheme).

### 2.3 Climate (HDD)
`climate_multiplier = HDD_HR / HDD_SI`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022:
- Croatia: 2166.74 / 2106.64 / 2170.86 / 2399.07 / 2146.64 → **mean 2197.99**
- Slovenia: → **mean 2693.30**
- `climate_multiplier = 2197.99 / 2693.30 = 0.8161`. Croatia is ~18% milder than Slovenia (the national HDD is intermediate between the warm Adriatic coast and the colder continental interior).

### 2.4 Retrofit shares and factors
**Retrofit factors** — the Slovenian TABULA refurbishment ratios (standard 0.65, advanced 0.40), used as the proxy. **PROVISIONAL** pending the Slovenian WebTool extraction.

**Retrofit shares** (0.88 original / 0.10 standard / 0.02 advanced) are a **modelling assumption** grounded in the Croatian Long-Term Renovation Strategy and EC renovation-rate data (~1%/yr, only ~1.5% of renovations "medium depth" and ~0.1% "deep" over 2012–2016) — Croatia's stock is overwhelmingly original.

**Resulting blend factor:** 0.88 × 1.00 + 0.10 × 0.65 + 0.02 × 0.40 = **0.953**.

### 2.5 DHW intensity
DHW added per building from the `si_intensities.csv` DHW column (Slovenian-proxy values).

### 2.6 Non-residential intensity
Estimate, 130 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.7 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **18.23** | 2015 | verified | Sum across all HR NUTS3 rows, all-classes. |
| Odyssee-Mure | 17.2 | 2023 | estimate | HR residential space heating ~1.48 Mtoe; final-energy basis — broadly consistent with Hotmaps. |
| EU BSO | 15.0 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

---

## 3. NUTS3 spatial join
Croatia has 21 NUTS3 counties, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. HR03 + HR04 NUTS2 partitions (NUTS 2016).
2. HDD HR = 2197.99, HDD SI = 2693.30 (Eurostat `nrg_chdd_a` 2018–2022); `climate_multiplier = 0.8161`.
3. Hotmaps HR total = 18.23 TWh — broadly consistent with the Odyssee-Mure residential figure.
4. Config validates; the full input chain loads cleanly (unknown-cohort fallback SFH ≈ 95 kWh/m²/yr).

### Still needs verification
1. **NUTS3 codes** — NUTS 2021 used; EUBUCCO v0.2 uses NUTS 2016 (HR03x/HR04x); the spatial join handles assignment.
2. **EUBUCCO low coverage** — Croatia's construction-year attribute is sparse; the result will be fallback-dominated.
3. **TABULA intensities** — Slovenian-proxy values, themselves derived from the ZRMK aggregate; MFH_LOW = MFH_HIGH limitation inherited.
4. **Retrofit factors** (0.65/0.40) and **DHW** — provisional.
5. **Retrofit shares** (0.88/0.10/0.02) — modelling assumption.
6. **Non-residential intensity** (130) — estimate; contributes 0 TWh.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Croatia built as a build-group-2 country, a TABULA **proxy** country using Slovenia as the proxy (shared Yugoslav-era construction tradition). Created `hr.yaml`, `eu_bso/hr_intensity.csv`, `hr_national/hr_climate_retrofit.csv`; shares `si_intensities.csv` with Slovenia. climate_multiplier 0.8161 from Eurostat HDD. Retrofit factors provisional. | Ali / Claude |
| 2026-05-19 | First G2 Colab run failed at script 03: `pd.read_csv` raised on `hr_climate_retrofit.csv` lines 19-20, which had unquoted commas inside `(Slovenian TABULA standard refurbishment (proxy, provisional))`. The unquoted comma split the row into 5 fields where the header declared 4. Same CSV-quoting bug pattern that bit MT/CY/PT. Fixed in commit 07c90e4 by wrapping the source field in double quotes. | Ali / Claude |
| 2026-05-20 | Second G2 Colab run completed: bottom-up 30.23 TWh vs Hotmaps 18.23 TWh = **+65.8 % (INVESTIGATE band)**. HR sits in the Mediterranean / warm-climate over-count cluster, at the lower end (CY +372 %, MT +231 %, PT +264 %, ES +143 %, EL +69 %, HR +66 %, IT +5.6 % after correction). | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **30.23** | **95.9** |
| Hotmaps 2015 baseline | 18.23 | 57.8 |
| EU BSO 2022 weighted-avg implied total | 30.64 | 97.2 |
| Odyssee-Mure 2023 (final energy, definitional gap vs Hotmaps useful demand) | 17.20 | 54.5 |

**Verdict:** Bottom-up vs Hotmaps = **+65.8 %** (INVESTIGATE — outside ±25 % band).

Croatia is at the **lower end of the Mediterranean over-count cluster** — much smaller than ES (+143 %) or PT (+264 %), comparable to EL (+69 %). HR uses Slovenia as the TABULA proxy (climate_multiplier 0.8161, scaling Slovenian values down to Croatia's milder HDD 2197 vs SI 2693). The +66 % gap is consistent with the pattern across warm-climate countries that we get from research-synthesised TABULA matrices applied to EUBUCCO areas.

The Slovenian proxy is the **closest TABULA match by construction tradition** (shared Yugoslav-era panelové domy / large-panel multi-family stock, comparable single-family detached typology, similar coastal vs continental climate split). The proxy framework itself is methodologically defensible; the +66 % residual reflects:

- **EUBUCCO floor-area over-count for HR** — probably modest (HR was flagged as a low-coverage EUBUCCO country in the v0.2 documentation; rural OSM data is sparser than for Italy or Germany).
- **Research-synthesised SI TABULA values** — `si_intensities.csv` is derived from the ZRMK aggregate report (not the full per-class per-period numerical matrix), with ±20 % uncertainty per the file header.

**Hotmaps remains the recommended residential heat-demand benchmark for Croatia.** The refinement path is a HR-direct TABULA extraction (Faculty of Civil Engineering, University of Zagreb; or HEP Toplinarstvo data) — Croatia is not currently in TABULA-12 but published Croatian residential archetype studies exist. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).

---

## 7. Academic refinement path (research 2026-05-20)

**Highest-leverage academic fix: regional-split proxy.** Croatia's two NUTS2 partitions are climatically and constructively distinct. **HR04 (Continental, Zagreb basin, 2100-2400 HDD, panel-block MFH)** is well-matched by the SI ZRMK proxy. **HR03 (Adriatic coast)** is Mediterranean masonry (tufa stone / perforated brick with air cavity, single-family terraced rural stock, ~1500-1800 HDD) — closer to the **Italian Adriatic coast** (Friuli/Marche/Puglia archetypes). Bari case literature (D'Agostino & Parker, *Climate* 10:55, 2022) reports ~63 kWh/m²/yr for late-1970s public housing — about half the SI ZRMK archetype the current build carries. **Implement two `tabula:` blocks per NUTS2 partition**: HR03 ← Italian Middle-zone TABULA; HR04 ← SI ZRMK. Requires schema extension. Second-priority fix: wood-stove comfort-derating coefficient (IEA Bioenergy 2021 Country Report: biomass = ~60 % of HR residential heat demand; coastal/rural HR03 wood-stove heating is single-room intermittent, not whole-dwelling steady-state). Third-priority: retrofit shares from FZOEU cumulative data (~15,400 apartments + ~290 NRRP multi-apartment + ~3 M m² envelope-renovated) → revised 0.78/0.18/0.04.

Important methodological point: EUBUCCO documentation flags Croatia as a **low-coverage** country (rural OSM sparsity), which **under-counts** floor area rather than over-counting it — so the +66 % gap is entirely intensity-driven. Expected post-fix gap: **+25 %** (LIKELY band, edge of ACC). Full citations and ranked priorities in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Mediterranean proxy cluster section.

> **[SUPERSEDED 2026-05-21 — the "area is under-counted / gap is entirely intensity-driven" claim above is WRONG.]** Direct measurement: EUBUCCO HR residential area = **315 Mm²**, but DZS 2021 records 1,433,445 occupied (×92 m²) + ~0.93 M unoccupied/seasonal ≈ **188 Mm²** — HR **over-counts** by ~1.7×. The mechanism is imputed floors: EUBUCCO HR has only ~1 % observed heights (Milojević-Dupont 2023, Table 1). See "Applied" below.

## Applied (2026-05-21): EUBUCCO area correction (Mechanism A) — `eubucco.area_correction = 0.59`

Applied an area correction; HR now lands at **17.8 TWh = −2.2 % (OK)** — without the region-split schema work.

**Mechanism — imputed floors (data quality).** EUBUCCO HR is on the low-coverage list AND has ~1 % observed heights → floor counts are almost entirely ML-imputed, over-stating area. EUBUCCO 315 Mm² vs DZS 2021 ~188 Mm² → factor **0.59** (the **Mechanism A** family, [eubucco_census_area_audit.md](../eubucco_census_area_audit.md)). The region-split proxy (HR03←IT-Middle, HR04←SI) remains a valid **second-order intensity refinement** for the warm Adriatic coastal stock, but is **no longer required for reconciliation** and the schema extension is not pursued. Census-grounded, not Hotmaps-tuned.
