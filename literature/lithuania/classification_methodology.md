# Lithuania — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country LT`).
**Config:** `code/data/country_config/lt.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Lithuania — one of the three Baltic states in build group 1 (DE + EE, LV, LT).

**The headline fact:** Lithuania is **not a TABULA country**. Its residential heat intensities are **Poland-derived** — extracted from the Polish TABULA typology and climate-corrected by the Lithuania/Poland heating-degree-day ratio. Lithuania is the mildest of the three Baltic states, so it carries the smallest HDD correction in the group.

---

## 1. Methodology relative to Luxembourg and France

Lithuania is a **proxy country**, following the Luxembourg branch (proxy + climate correction):

| Element | Luxembourg | Lithuania |
|---|---|---|
| TABULA dataset | Belgium (proxy) | **Poland (proxy)** |
| Climate correction | HDD_LU/HDD_BE = 1.112 | HDD_LT/HDD_PL = **1.1522** |
| Retrofit factors source | TABULA Belgium | **TABULA Poland** |
| EUBUCCO partitions | 1 (LU00) | 2 (LT01, LT02) |
| NUTS3 regions | 1 (LU000) | 10 |
| Hotmaps reconciliation | single LU000 row | sum across all LT rows (17.29 TWh) |

The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to Luxembourg.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Lithuania's NUTS2 structure changed at the 2016 revision from a single region (LT00) to **two** — LT01 Sostinės regionas (Capital region) and LT02 Vidurio ir vakarų Lietuvos regionas (Central & Western Lithuania). EUBUCCO v0.2 therefore provides two Lithuanian partitions. Lithuania has 10 NUTS3 regions (counties), codes identical in NUTS 2016 and 2021.

### 2.2 TABULA — Poland as proxy

**Lithuania has no national TABULA typology.** Poland is chosen as the proxy because:
1. Lithuania's residential stock is dominated by Soviet-era prefabricated large-panel concrete apartment blocks (~35,000 Soviet-era apartment buildings, ~72 % of multi-dwelling floor area) plus older masonry and rural timber houses. Poland's TABULA typology explicitly carries the Soviet/Comecon-era large-panel ("wielka płyta") apartment class.
2. Shared post-war central-planning construction norms (SNiP-derived).
3. Poland is the closest panel-bearing TABULA country; using it for all three Baltic states keeps the methodology consistent across the group.

**Primary source:** Polish TABULA Scientific Report (NAPE). Extraction: `code/data/raw/tabula/pl_intensities.csv` — the header documents the EK→net-space-heating derivation and the class/cohort mappings.

### 2.3 Climate (HDD)
`climate_multiplier = HDD_LT / HDD_PL`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022:
- Lithuania: 3692.16 / 3394.26 / 3310.44 / 4022.50 / 3778.37 → **mean 3639.5**
- Poland: → **mean 3158.7**
- `climate_multiplier = 3639.5 / 3158.7 = 1.1522`.

Lithuania is the mildest of the three Baltic states (Estonia 3988, Latvia 3818, Lithuania 3640 HDD), so it carries the smallest Poland-proxy climate correction.

### 2.4 Retrofit shares and factors
**Retrofit factors** are the Poland TABULA typology-averaged refurbishment ratios: **standard 0.63**, **advanced 0.50**.

**Retrofit shares** (0.88 original / 0.08 standard / 0.04 advanced) are a **modelling assumption**. Lithuania runs one of Europe's most prominent multi-apartment renovation programmes (APVA), but as of the early-2020s baseline only ~2,200 of ~38,000 pre-1993 multi-apartment buildings were fully renovated (<15 % of eligible blocks, ~5 % of total stock). The standard/advanced sub-split is an assumption — flagged.

**Resulting blend factor:** 0.88 × 1.00 + 0.08 × 0.63 + 0.04 × 0.50 = **0.9504**.

### 2.5 DHW intensity
DHW is added per building from the `pl_intensities.csv` DHW column (Poland-proxy values).

### 2.6 Non-residential intensity
Estimate, 150 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh (NON_RESIDENTIAL carries zero heated area).

### 2.7 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **17.29** | 2015 | verified | Sum across all LT NUTS3 rows in `building_stock_nuts3.csv`, all-classes. |
| Odyssee-Mure | 11.0 | 2022 | estimate | LT residential space heating; final-energy basis estimate. |
| EU BSO | 13.0 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

A Lithuania-specific consideration: decarbonisation competes against an already heavily biomass-fired district-heating system (~50 % of households, DH fuel >75 % biomass) rather than against fossil gas — gas heats only ~11 % of dwellings. This shapes the technology layer but not the bottom-up heat-demand build documented here.

---

## 3. NUTS3 spatial join
Lithuania has 10 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. LT01 + LT02 NUTS2 partitions (NUTS 2016); 10 NUTS3 codes (stable NUTS 2016/2021).
2. HDD LT = 3639.5, HDD PL = 3158.7 (Eurostat `nrg_chdd_a` 2018–2022); `climate_multiplier = 1.1522`.
3. Poland TABULA intensities — `code/data/raw/tabula/pl_intensities.csv`.
4. Retrofit factors 0.63 / 0.50 — Polish TABULA typology-averaged refurbishment ratios.
5. Hotmaps LT total = 17.29 TWh — computed from `building_stock_nuts3.csv`.
6. Config validates; full input chain loads cleanly (unknown-cohort fallback SFH ≈ 201 kWh/m²/yr).

### Still needs verification
1. **Retrofit shares** (0.88/0.08/0.04) — modelling assumption; no published three-state envelope distribution for Lithuania.
2. **Non-residential intensity** (150) — estimate; contributes 0 TWh.
3. **EU BSO benchmark** — anchored estimate, BSO portal not retrievable.
4. **Poland TABULA net-SH values** — derived from the Polish report's EK figures, ±15–20 % uncertainty.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Lithuania built as a build-group-1 country, a TABULA **proxy** country using Poland as the proxy. Created `lt.yaml`, `eu_bso/lt_intensity.csv`, `lt_national/lt_climate_retrofit.csv`; shares `pl_intensities.csv` with Estonia and Lithuania. climate_multiplier 1.1522 from Eurostat HDD. Retrofit factors 0.63/0.50 from the Polish TABULA; retrofit shares a modelling assumption from APVA renovation reporting. | Ali / Claude |
| 2026-05-19 | Colab G1 run completed: bottom-up 38.74 TWh vs Hotmaps 17.30 TWh = **+123.9 % (INVESTIGATE band, the largest gap among non-Mediterranean countries in the build)**. The gap is almost entirely intensity-driven (LT floor-area aligns within ~2 % of population × census m²/dwelling). LT inherits the same PL-proxy bias as EE but the LT/PL climate scaling (1.1522) is smaller, making the residual gap surprisingly larger — the relationship between Polish national EK values and Lithuanian actual heat consumption is non-linear in HDD. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-19)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **38.74** | **194.0** |
| Hotmaps 2015 baseline | 17.30 | 86.6 |
| EU BSO 2022 weighted-avg implied total | 38.21 | 191.4 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 11.00 | 55.1 |

**Verdict:** Bottom-up vs Hotmaps = **+123.9 %** (INVESTIGATE — the largest non-Mediterranean gap in the build).

Lithuania is the **most extreme manifestation of the Baltic-PL-proxy over-count pattern**. The pure-intensity decomposition is striking:

- ~~**EUBUCCO floor area is essentially right** — our 199 Mm² aligns within ~2 % of LT pop 2.8 M × ~70 m²/dwelling. No area issue to investigate.~~ **CORRECTED 2026-05-20:** the original claim was a math error (multiplied total POPULATION by per-DWELLING area). Correct comparison: 1.31 M households × ~72 m² mean useful area = ~94 Mm² main residences + ~10 Mm² secondary = ~104 Mm² total per Statistics Lithuania 2021 Census. **EUBUCCO LT (199 Mm²) over-counts by ~1.91×.** An `eubucco.area_correction = 0.52` is now applied in lt.yaml (commit pending) to land the BU at the Statistics Lithuania anchor. Same structural mechanism as ES (0.613) and CY (0.500); LT was originally diagnosed correctly as "intensity-driven" but it was actually intensity AND area, both contributing roughly equally to the +124% gap.
- **Intensity over-states by ~2.2 ×** — bottom-up at 194 kWh/m² is more than double Hotmaps-implied (~87 kWh/m²).

The over-count cannot be explained by EUBUCCO floor-area mistakes — it sits entirely in the TABULA layer. Specifically, the Polish TABULA's EK-derived net-SH values, when climate-scaled by 1.1522 to Lithuanian conditions, produce per-m² intensities that exceed actual Lithuanian residential heat demand by a factor of ~2.2. This is unlikely to be resolved by EUBUCCO area work; it requires a national-data Lithuanian re-derivation (Vilnius Tech / Lithuanian Building Institute archetypes; APVA renovation programme data).

**Hotmaps remains the recommended residential heat-demand benchmark for Lithuania** for any analysis requiring a single national number. The Lithuanian gap is also the clearest empirical case in the build that **the bottom-up TABULA + EUBUCCO + climate-scaling pipeline can produce a 2× over-count even when the floor-area input is correct** — TABULA values, not EUBUCCO areas, drive the LT residual. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).

---

## 7. Academic refinement path (research 2026-05-20)

**Highest-leverage academic fix (near-term):** same as EE — **class-mix proxy: SE for SFH + PL for MFH**. Lithuania's ~22 % wooden / log SFH (mainly rural *medinis namas*) is the structural mismatch that the all-classes PL proxy doesn't capture. Implementing the class-mix proxy is expected to bring LT down to **~+60-70 %** (still INV but much improved). For LT specifically the gain is smaller than EE because LT has a smaller wooden SFH share — the residual will need the longer-term fix below.

**Longer-term refinement (most precise option, deferred):** **Baltic-direct TABULA matrix from APVA measured-consumption data**. The Aplinkos projektų valdymo agentūra has ~2,200 fully renovated multi-apartment buildings documented with measured pre/post heat consumption — **this is the most empirically grounded heat-demand evidence in the Baltics** (gold standard: measured post-meter consumption, not modelled archetype values). Pair with VGTU Vilnius Tech archetypes for SFH (Šadauskienė, Stankevičius et al., *Energy Procedia* 2014; subsequent *Sustainability* papers) and the Lithuanian LTRS 2020 four-serial-type panel-block reference (1A, 1.1.7, 1-318, 467-A). With an APVA-grounded matrix, LT is expected to land within ±10 % of Hotmaps.

Full citations and the LV-control / typology-hypothesis decomposition are in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Baltic cluster section.

### 7.1 Applied this session (2026-05-20): class_mix proxy — SE for SFH, PL for MFH

The schema extension is no longer deferred — `CountryConfig` now supports a `tabula.class_mix` field (added this session for the EE/LT pair). LT applies it on the same template as EE.

**Configuration:**
- **SFH:** Swedish TABULA Enfamiljshus typology (`se_intensities.csv`), climate-scaled by HDD_LT / HDD_SE_zone3 = 3639.5 / 3500 = **1.040**. Lithuania is the mildest of the three Baltic states, so the SE-zone-3 climate correction is small (close to 1.0).
- **MFH_LOW + MFH_HIGH:** Polish TABULA (`pl_intensities.csv`) retained, climate-scaled by HDD_LT / HDD_PL = 3639.5 / 3158.7 = **1.1522** (unchanged from pre-class-mix).

**Empirical effect:** local smoke-test (`build_intensity_lookup` on LT config) shows the SFH fallback intensity drops from the all-PL-derived ~190 kWh/m² to the SE-derived **167.3 kWh/m²** (~−12 %), with MFH unchanged. Smaller absolute shift than the EE case because LT has a smaller wooden-SFH share and a milder climate correction; the residual LT gap will need the longer-term APVA-direct fix below.

**Status:** the **APVA-direct TABULA matrix** (measured pre/post heat consumption from ~2,200 renovated multi-apartment buildings) remains the highest-precision refinement and is the planned next-step beyond the class-mix proxy. Pair with VGTU Vilnius Tech wooden-SFH archetypes (Šadauskienė et al. 2014). The class-mix proxy is methodologically independent and would naturally retire once the LT-direct matrix is extracted.

**Sources:**
- APVA (Aplinkos Projektų Valdymo Agentūra) renovation programme reporting — ~2,200 renovated multi-apartment buildings with measured consumption.
- Šadauskienė, J., Stankevičius, V. et al. (2014) — VGTU Vilnius Tech residential archetypes, *Energy Procedia*.
- LTRS 2020 — four-serial-type panel-block reference (1A, 1.1.7, 1-318, 467-A).
- Polish TABULA Scientific Report (NAPE) — large-panel MFH archetype.
- Swedish TABULA National Typology Brochure — Enfamiljshus zone-3 archetypes.
