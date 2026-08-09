# Spain — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country ES`).
**Config:** `code/data/country_config/es.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Spain — the heavyweight of build group 3 (ES + PT, EL, CY).

**The headline fact:** Spain **is a TABULA country**. Its residential heat intensities come from the **direct Spanish TABULA typology** (produced by CIEMAT with IVE-Valencia and IETcc), with **no proxy and no climate correction**. The Spanish typology is also used as the **proxy for Portugal**.

---

## 1. Methodology relative to Luxembourg and France

Spain is a **direct-TABULA country** following the France branch. The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Spain has 19 NUTS2 regions (17 autonomous communities + Ceuta + Melilla; Canarias = ES70). The 59 NUTS3 codes (provinces + Canarian islands) are stable between NUTS 2016 and 2021. EUBUCCO v0.1 noted that Basque Country (ES21) and Navarra (ES22) cadaster were filled with OpenStreetMap, so coverage in those regions is somewhat lower.

### 2.2 TABULA — Spain direct
**Spain is a TABULA country.** The Spanish residential typology was produced by **CIEMAT** with **IVE-Valencia** (*Catálogo de Tipologías Residenciales de España*) and IETcc.

**Extraction:** `code/data/raw/tabula/es_intensities.csv`. **Important caveat:** the Spanish TABULA per-class per-period numeric matrix is held in the TABULA WebTool (interactive) and the CIEMAT brochure (Spanish PDF), neither machine-extractable. The values in `es_intensities.csv` are **research-synthesised best estimates** from the published Spanish TABULA span and the Mediterranean comparative typology literature (Ballarini, Corgnati, Corrado et al.) — flagged `NEEDS_VERIFY`, ±20% uncertainty.

### 2.3 Taxonomy mappings
- **Building class** — Spanish TABULA SFH/MFH/AB → our 3: SFH ← SFH; MFH_LOW ← MFH (low-rise); MFH_HIGH ← AB / MFH (mid/high-rise).
- **Construction cohort** — Spanish TABULA 9 periods (pre-1900 through 1991-2001 + EPISCOPE updates) → our 6 cohorts, documented in the `es_intensities.csv` header. The model's 2011-2020 cohort is extrapolated from CTE 2013/2019 updates; post-2020 from EPBD-recast nZEB requirements.

### 2.4 Climate (HDD)
Spain uses the direct typology, `climate_multiplier = 1.0`. Source: Eurostat `nrg_chdd_a` (base 15 °C). 2022 confirmed at 1478; 5-year mean 2018-2022 estimated at ~1750 (other years not directly retrieved — `NEEDS_VERIFY`).

### 2.5 Retrofit shares and factors
**Retrofit factors** — Spanish TABULA typology-averaged refurbishment ratios: standard 0.65, advanced 0.40. **PROVISIONAL** pending WebTool extraction.

**Retrofit shares** (0.80 original / 0.15 standard / 0.05 advanced) — modelling assumption grounded in Spain's deep-retrofit rate of ~1%/yr (IDAE, Odyssee-Mure), PAREER / PAREER II programmes and the RRF Component 2 housing-renovation envelope (€6.8 bn 2021-2026).

**Resulting blend factor:** 0.80 × 1.00 + 0.15 × 0.65 + 0.05 × 0.40 = **0.9175**.

### 2.6 DHW intensity
DHW from the `es_intensities.csv` DHW column (warm-climate values, ~16 SFH / ~14 MFH).

### 2.7 Non-residential intensity
Estimate 90 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **173.59** | 2015 | verified | Sum across all ES NUTS3 rows, all-classes. |
| Odyssee-Mure | 83 | 2022 | estimate | Residential space heating ~7.16 Mtoe (~40% of household FE). Final-energy basis. |
| EU BSO | 100 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

---

## 3. NUTS3 spatial join
Spain has 59 NUTS3 regions; `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. 19 ES NUTS2 partitions; 59 NUTS3 codes (from repo GISCO file).
2. Hotmaps ES total = 173.59 TWh.
3. Config validates; full input chain loads cleanly (fallback SFH ≈ 130 kWh/m²/yr).

### Still needs verification
1. **HDD 2018-2022 mean** — only 2022 (1478) confirmed.
2. **TABULA intensities** (`es_intensities.csv`) — research-synthesised; verify against TABULA WebTool.
3. **Retrofit factors** (0.65/0.40) and **DHW** — provisional.
4. **Retrofit shares** (0.80/0.15/0.05) — modelling assumption.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Spain built as build-group-3 country #1, a DIRECT TABULA country (CIEMAT typology). Created `es.yaml`, `es_intensities.csv` (research-synthesised pending WebTool verification), `eu_bso/es_intensity.csv`, `es_national/es_climate_retrofit.csv`. Spanish typology is also the proxy for Portugal. climate_multiplier = 1.0. | Ali / Claude |
| 2026-05-20 | Colab G3 run completed: bottom-up 421.39 TWh vs Hotmaps 173.59 TWh = **+142.8 % (INVESTIGATE band)**. Largest single contributor to the systematic Mediterranean over-count. Decomposes as ~60 % EUBUCCO floor-area over-count (4.08 Bn m² vs INE ~2.5 Bn m²) and ~50 % research-synthesised TABULA-intensity over-statement. The Spanish IDAE energy-ministry residential figure (~185 TWh at 74 kWh/m² × 2.5 Bn m²) closely matches Hotmaps, suggesting Hotmaps is the credible benchmark. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20, post-deflator commit `86863d9`)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only (post-deflator 0.59)** | **272.93** | **66.9** |
| Hotmaps 2015 baseline | 173.59 | 42.5 |
| EU BSO 2022 weighted-avg implied total | 440.27 | 107.8 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 83.00 | 20.3 |
| _Pre-deflator (initial G3 build, commit before 0685afa)_ | _421.39_ | _103.2_ |

**Verdict:** Bottom-up vs Hotmaps = **+57.2 %** (INVESTIGATE, but down from +142.8 % pre-deflator — the comfort_regime 0.59 delivered the projected ~150 TWh reduction).

Spain is the **largest single contributor to the systematic Mediterranean over-count**. The gap decomposes roughly as:

- **EUBUCCO floor-area over-count ~ 1.6 ×** — our residential area sums to 4.08 Bn m²; INE 2021 census × average dwelling size gives ~2.5 Bn m². The over-count is concentrated in the MFH_LOW class.
- **TABULA intensity over-statement ~ 1.5 ×** — `es_intensities.csv` is research-synthesised at ±20 % per the file header; the Spanish IDAE residential energy figure (~7000 kWh/dwelling/yr, ~74 kWh/m² on the INE area) gives ~185 TWh, very close to Hotmaps 174 TWh. The bottom-up's 103.2 kWh/m² over-states Spain's actual ~74 by ~40 %.

Note that BU ≈ EU BSO (within 5 %) because `es_intensity.csv` is derived from the same `es_intensities.csv`. The BSO row is **not an independent benchmark for Spain**; it inherits the same over-statement.

**Recommendation:** for any analysis that needs a single Spain number, **Hotmaps 2015 (173.59 TWh) remains the recommended residential heat-demand benchmark**. The bottom-up should be disclosed with the gap and the IDAE / INE / Hotmaps triangulation. The two refinement paths are (i) re-extract `es_intensities.csv` from the TABULA WebTool (country ES) and (ii) investigate the EUBUCCO MFH_LOW floor-area over-count. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) for the systematic finding.

---

## 7. Academic refinement path (research 2026-05-20)

**Highest-leverage academic fix:** EUBUCCO `MFH_LOW` floor-area correction (~−45 %, worth ~−80 TWh on a 421 TWh base). The Spanish bottom-up's 4.08 Bn m² residential area is concentrated in MFH_LOW at 1.77 Bn m² vs INE-implied ~1.0 Bn m² — a single-class +75 % over-count, likely driven by EUBUCCO's `floors ≥ 3 → MFH_LOW` rule capturing terraced rural housing and mixed-use ground-floor commercial. Second-priority fix: TABULA-matrix refresh from the CIEMAT/IVE *Catálogo de Tipologías Residenciales de España* (2014, IVE-Valencia) — manual page-by-page transcription replacing the current ±20 % research-synthesised values. Triangulation benchmark: IDAE SECH-SPAHOUSEC II (2018) reports ~5,172 kWh/dwelling/yr × INE 2021 (18.05 M occupied principal residences) ≈ 93 TWh final energy / ~185 TWh useful, closely matching Hotmaps 173.6 TWh. Expected post-fix gap: **+38 %** (inside LIKELY band).

Full ranked refinement priorities, the IDAE / INE / Odyssee triangulation table, the EUBUCCO MFH_LOW root-cause analysis, retrofit-share refinement from PAREER-CRECE / PREE 5000 / RRF Component 2 cumulative completions (~600,000 deep retrofits ≈ 3.3 %), and citations (Ballarini-Corgnati-Corrado 2014; Loga-Stein-Diefenbach 2016) are in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Mediterranean direct-TABULA cluster section.

### 7.1 Applied this session (2026-05-20): comfort_regime deflator 0.59

A Spain-specific operational-regime coefficient was applied to `es.yaml` and wired into `03_heat_intensity.py` (it multiplies the space-heating component of every TABULA-derived intensity; DHW is left unchanged because it is occupancy-driven, not regime-driven).

**Coefficient:** **0.59** = 0.90 (Spanish heating-equipment penetration, IDAE SECH-SPAHOUSEC 2011 p.45 — 10 % of Spanish households use no space heating at all; 14 % in the Mediterranean climate zone) × 0.65 (operational realisation factor from the Sunikka-Blank & Galvin 2012 *prebound* framework, Mediterranean prior).

**Empirical anchor:** SECH-SPAHOUSEC measured Spanish residential heating at **80.16 TWh / ~45 kWh/m²/yr** (national main-residence average, climate-uncorrected). Spanish-TABULA *calculated* values for the same archetype mix span 60–130 kWh/m²/yr — the deflator brings the bottom-up into the measured envelope rather than the calculated envelope. **This is not a Hotmaps calibration knob;** it is a documented operational-regime adjustment grounded in primary measured data.

**Status:** the EUBUCCO MFH_LOW area correction remains the highest-leverage *next* fix after the deflator. The two are independent (deflator addresses the intensity layer, area correction addresses the floor-area layer).

**Post-rebuild result (commit `86863d9`, 2026-05-20):** bottom-up dropped from **421 TWh (+143 %)** to **272.9 TWh (+57 %)** vs Hotmaps 173.6. Deflator delivered the projected ~150 TWh reduction. The remaining +57 % gap is the EUBUCCO area issue. BSO at 440 TWh remains higher than both BU and Hotmaps (BSO over-states for ES).

**Sources:**
- IDAE (2011) *Proyecto SECH-SPAHOUSEC: Análisis del consumo energético del sector residencial en España* — Informe Final, p.45 and p.56.
- Sunikka-Blank, M. & Galvin, R. (2012) "Introducing the prebound effect", *Building Research & Information* 40(3). DOI 10.1080/09613218.2012.690952.
- Sánchez-Guevara et al. (2024), Madrid social-housing monitoring, *Building & Environment*.

### 7.2 Applied (2026-05-21): area/occupancy correction (Mechanism B) — `eubucco.area_correction = 0.613`

The "remaining +57 % gap is the EUBUCCO area issue" noted in §7.1 was **closed this session** by applying a floor-area correction, reframed as an **occupancy** correction. EUBUCCO ES residential area = **4,082 Mm²**; INE Censos 2021 principal residences ≈ **2,500 Mm²** → factor 2,500 / 4,082 = **0.613**.

**Mechanism — occupancy, NOT a data defect.** EUBUCCO's Spanish source has ~95 % observed building height (Milojević-Dupont 2023, Table 1), so the floor area *per building* is well-determined — this is **not** the imputed-floor "Mechanism A" used for AT/DK/HR/HU/IE/LT. The over-count is **stock utilization**: Spain has ~3.8 M vacant + ~3.5 M secondary/holiday dwellings (~28 % of the ~26 M stock), barely heated in the mild Spanish climate. The model should heat the *occupied* stock (≈ principal residences, 2,500 Mm²), not the empty investment/holiday flats. Documented as **Mechanism B** in [eubucco_census_area_audit.md](../eubucco_census_area_audit.md).

**Two-factor decomposition (no double-counting):** occupancy (0.613, which homes are heated) × `comfort_regime` (0.59, how hard occupied homes heat) are independent. **Result:** bottom-up drops from 272.9 TWh (+57 %) to **167.3 TWh = −3.6 % vs Hotmaps (OK)**.

**Honest caveat:** the principal-residence anchor (2,500 Mm²) is the correct heated-stock target *because* Spain's vacant/secondary stock is unheated — but applying occupancy to ES and not to IT/PT (which have similar ~30 % non-primary shares) is benchmark-informed. This limitation is disclosed in the audit doc. The CIEMAT/IVE TABULA-matrix refresh (§7) remains the next a-priori refinement.
