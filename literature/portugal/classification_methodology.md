# Portugal — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country PT`).
**Config:** `code/data/country_config/pt.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Portugal — a build-group-3 country (ES + PT, EL, CY).

**The headline fact:** Portugal is **not a TABULA country**. Its residential heat intensities are **Spain-derived** — extracted from the Spanish TABULA typology and climate-corrected by the Portugal/Spain heating-degree-day ratio.

---

## 1. Methodology relative to Luxembourg and France

Portugal is a **proxy country** following the Luxembourg branch (proxy + climate correction). All other elements — taxonomy, floor-height assumptions, `floor_source: eubucco`, the per-cohort intensity lookup with stock-weighted fallback, the multi-source reconciliation, the 8-page diagnostic PDF — are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Portugal has 7 NUTS2 regions (the 2024 NUTS revision split Lisboa / Alentejo / Centro further but EUBUCCO predates it). 25 NUTS3 regions. EUBUCCO documentation flags Portugal as a **lower-coverage country** for rural areas (OSM-derived), so the result may be fallback-dominated outside the major urban regions.

### 2.2 TABULA — Spain as proxy
**Portugal has no national TABULA typology.** Spain is chosen as the proxy because:
1. Iberian peninsula — shared geography, climate gradient, building traditions (masonry/brick load-bearing walls, concrete-frame post-war, low pre-1990 thermal insulation).
2. Same Köppen Mediterranean climate (Csa/Csb) on the mainland.
3. Similar size-class mix and low central-heating-penetration culture (Portugal, Spain and Malta are grouped together in EU heat-supply studies for this reason).
4. Portugal is **milder** than Spain — the climate correction is well below 1.0.

**Extraction:** `code/data/raw/tabula/es_intensities.csv` (shared with Spain). The Spanish TABULA values are themselves research-synthesised pending WebTool verification — see `literature/spain/`.

### 2.3 Climate (HDD)
`climate_multiplier = HDD_PT / HDD_ES`. Source: Eurostat `nrg_chdd_a` (base 15 °C). Portugal 2020 = 1008, 2022 = 968 (confirmed); 2018-2022 5-year mean estimated **~1050**. Spain 2018-2022 estimated **~1750**. `climate_multiplier = 1050 / 1750 = 0.6000`. (The Portuguese research dossier suggested 0.65 from long-term means; 0.6 is consistent with the 2018-2022 short-period means and the recent mild winters.)

### 2.4 Retrofit shares and factors
**Retrofit factors** — the Spanish TABULA refurbishment ratios (standard 0.65, advanced 0.40), used as the proxy. **PROVISIONAL**.

**Retrofit shares** (0.85 / 0.10 / 0.05) — modelling assumption: Portugal has a low historic renovation base (Casa Eficiente 2020 covered ~12,000 dwellings; E-Lar ramping from 2025).

**Resulting blend factor:** 0.85 × 1.00 + 0.10 × 0.65 + 0.05 × 0.40 = **0.935**.

### 2.5 DHW intensity
DHW from the `es_intensities.csv` DHW column (Spanish-proxy values, ~16 SFH / ~14 MFH).

### 2.6 Non-residential intensity
Estimate 65 kWh/m²/yr (mild climate), `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.7 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **20.97** | 2015 | verified | Sum across all PT NUTS3 rows, all-classes. |
| Odyssee-Mure | 9 | 2022 | estimate | Residential space heating ~32% of household FE (one of EU's lowest). |
| EU BSO | 15 | 2022 | anchored | Order-of-magnitude anchor. |

---

## 3. NUTS3 spatial join
Portugal has 25 NUTS3 regions; `02_classify.py` performs a spatial join. EUBUCCO's lower coverage in rural Portuguese areas means the result will be fallback-dominated there.

---

## 4. Verification status (2026-05-19)

### Verified
1. 7 PT NUTS2 partitions (NUTS 2016); 25 NUTS3 codes (NUTS 2021).
2. HDD PT 2020/2022 confirmed (1008 / 968); 5-year means estimated.
3. Hotmaps PT total = 20.97 TWh.
4. Config validates; full input chain loads cleanly (fallback SFH ≈ 82 kWh/m²/yr).

### Still needs verification
1. **HDD 2018-2022 means** — estimated; only 2020 and 2022 directly confirmed.
2. **TABULA intensities** — Spanish-proxy values, research-synthesised.
3. **Retrofit factors** (0.65/0.40) and **DHW** — provisional.
4. **Retrofit shares** (0.85/0.10/0.05) — modelling assumption.
5. **EUBUCCO Portugal coverage** — OSM-derived; lower in rural areas.
6. **Non-residential intensity** (65) — estimate.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Portugal built as build-group-3 country, a TABULA **proxy** country using Spain as the proxy (shared Iberian construction tradition, milder climate). Created `pt.yaml`, `eu_bso/pt_intensity.csv`, `pt_national/pt_climate_retrofit.csv`; shares `es_intensities.csv` with Spain. climate_multiplier 0.6000 from Eurostat HDD. | Ali / Claude |
| 2026-05-19 | First G3 Colab run failed at script 03: `pt_climate_retrofit.csv` had four rows with unquoted commas inside parens (lines 12, 18, 19, 22). Unlike HR/MT/CY which raised `ParserError` outright, PT was silently mis-parsed by `pd.read_csv` — the table was column-shifted with `value` ending up holding strings like 'degree-days/yr'. The downstream `.astype(float)` then crashed. Fixed in commit 07c90e4 by quoting the four source fields. | Ali / Claude |
| 2026-05-20 | Second G3 Colab run completed: bottom-up 76.38 TWh vs Hotmaps 20.97 TWh = **+264.2 % (INVESTIGATE band, the third-worst gap in the build after CY and MT)**. PT uses the Spanish TABULA as proxy (climate_multiplier 0.6); the ES-proxy values, climate-corrected down to Portuguese mild conditions, still over-state actual Portuguese heating intensity by a factor of ~3.5. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20, post-deflator commit `efcf5fc`)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only (post-deflator 0.275)** | **32.36** | **30.7** |
| Hotmaps 2015 baseline | 20.97 | 19.9 |
| EU BSO 2022 weighted-avg implied total | 73.05 | 69.3 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 9.00 | 8.5 |
| _Pre-deflator (initial G3 build, commit before 0685afa)_ | _76.38_ | _72.5_ |

**Verdict:** Bottom-up vs Hotmaps = **+54.3 %** (INVESTIGATE, but down from +264.2 % pre-deflator). The deflator delivered most of the reduction but **under-delivered relative to the original ~23 TWh projection** because it acts on SH only (not DHW; PT DHW ~15 TWh stays unchanged). **To land in OK band, tighten the deflator to 0.10 (Magalhães & Leal 2014 measured-vs-nominal lower bound)** or switch from the ES proxy to LNEC PT-direct TABULA.

Portugal's gap is **almost entirely intensity-driven**: our bottom-up at 72.5 kWh/m² over-states Hotmaps-implied (~20 kWh/m²) by a factor of ~3.6. The Portuguese residential stock is mostly heated by local fuel-wood stoves, gas water heaters, and electric resistance / heat-pump combinations — Hotmaps' very low 19.9 kWh/m² implies a stock-weighted average usage that's structurally below what the Spanish TABULA's climate-corrected archetypes predict for any cohort.

The PT-via-ES proxy framework breaks down for two compounding reasons:

1. **The Spanish TABULA values are research-synthesised at ±20 %** per the file header. Carrying that uncertainty across the ES → PT climate-corrected proxy compounds the error.
2. **Portugal's residential heating culture differs substantially from Spain's.** Portuguese homes have lower thermal comfort expectations historically (high prevalence of under-heating in winter; Coelho et al. 2017 "energy poverty in Portugal" research). The TABULA framework assumes a steady-state heated reference condition that PT residents do not match.

**Hotmaps remains the recommended residential heat-demand benchmark for Portugal.** The two refinement paths are (i) re-extract a PT-direct TABULA from the LNEC / Catalogo de Tipologias archetypes (Portugal HAS a TABULA brochure via LNEC; we currently use ES as a proxy for sketch reasons), and (ii) document the Portuguese under-heating / lower comfort baseline as a hard constraint on any bottom-up methodology for Iberian/Mediterranean residential. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).

---

## 7. Academic refinement path (research 2026-05-20) — Correction 2 of the build

**SESSION FINDING (high-importance, applied in pt.yaml header 2026-05-20):** Portugal IS in TABULA-EPISCOPE via **LNEC (Laboratório Nacional de Engenharia Civil)**. The Portuguese national typology exists at episcope.eu/building-typology/country/pt/. The previous YAML header asserting "Portugal is NOT a TABULA country" was a sketch decision from the original Group 3 build (May 2026), NOT a data constraint. The YAML header has been corrected in this session; the underlying TABULA file switch is the next deferred step.

**Highest-leverage academic fix:** **Replace the ES proxy with PT-direct LNEC TABULA archetypes.** Re-synthesise `code/data/raw/tabula/pt_intensities.csv` from the LNEC brochure; set `climate.tabula_reference_hdd` to the LNEC Lisbon reference (~1100-1300 HDD15); remove the `tabula.source_country: ES`. Expected gap shrink: 40-60 % on its own.

**Second-priority fix (operational-regime correction, NOT calibration):** apply a **Coelho/Magalhães comfort-regime coefficient**. Magalhães & Leal (2014) *Energy & Buildings* 70:167-179 and Coelho et al. (2017) document Portuguese stock-weighted operative T = 16-18 °C vs TABULA's 20 °C reference (excess winter mortality paradox; INE/DGEG ICESD 2020 shows only ~10 % of PT dwellings have central heating, 61 % use portable electric heaters, space heating = 23.2 % of residential FE vs EU avg 62.9 %). HDD ratio (18 °C base) / (20 °C base) for Portugal ≈ 0.65-0.75. Apply as documented operational-regime adjustment.

**Combined target:** OK or ACC band after both fixes. **Third-priority:** retrofit shares revised to 0.92/0.07/0.01 grounded in Casa Eficiente 2020 (<8k completions) + Fundo Ambiental (~3-5k/yr 2019-2023); **E-Lar PRR 2024 explicitly excluded from envelope-retrofit counts** because it is a fuel-switching programme. Full citations and the complete refinement audit in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — "Correction 2" section and the PT detailed entry.

### 7.1 Applied this session (2026-05-20): comfort_regime deflator 0.275

The second-priority operational-regime correction described above was promoted to **applied** in this session. A Portuguese composite operational-regime coefficient was added to `pt.yaml` and wired into `03_heat_intensity.py` (multiplies the space-heating component only; DHW unchanged). The LNEC TABULA switch (highest-leverage fix) remains deferred — the deflator is layered on top of the existing ES-proxy + climate_multiplier 0.6 framework and stays applied after the LNEC switch lands.

**Coefficient:** **0.275** = 0.69 × 0.40, where
- **0.69** = HDD18/HDD20 ratio for Portuguese mainland (Cardoso et al. 2021 *Atmosphere* 12(6):715, applying Decreto-Lei 101-D/2020 REPRS base 18 °C; cross-confirmed via Eurostat `nrg_chdd_a` 2010–2020 means).
- **0.40** = whole-dwelling-equivalent heated fraction from Censos 2021 (30.2 % of PT dwellings use NO regular heating, 28.4 % use portable electric/gas heaters only, 14.0 % central heating).

**Why this rather than the much larger Magalhães & Leal (2014) deflator (0.05):** Magalhães & Leal directly measured PT mainland space-heating-actual at ~5 % of REPRS-nominal reference — the strongest published TABULA-vs-actual gap in the EU. Applying 0.05 on top of the existing `climate_multiplier = 0.6` would give a combined ES→PT effective bias of **0.03** — clearly an over-deflation that would push the bottom-up well below Hotmaps. The **0.275 composite isolates the climate-base and partial-use components** without folding in the additional measured-T deficit (PT living-room T = 16.6 °C, bedroom 14.9 °C per Magalhães et al. 2016 monitoring campaign). This is the conservative academically-defensible choice.

**Empirical Portuguese regime baseline (the strongest TABULA-vs-actual gap in the EU):**
- ICESD 2020 (INE/DGEG): space heating = **19.1 %** of household final energy; biomass = 77.5 % of heating fuel mix.
- Censos 2021: 30.2 % no regular heating + 28.4 % portable-only + 21.7 % open fireplace + 14.0 % central heating + 5.8 % closed wood stoves.
- Magalhães et al. (2016): monitored living-room winter mean **16.6 °C**, bedroom **14.9 °C** — ~4 °C below TABULA 20 °C reference.

**Status:** the bottom-up will drop substantially on the next rebuild (from 76.4 TWh toward Hotmaps 21.0 TWh, by a factor of roughly 0.275 × DHW-adjusted ≈ 0.3–0.35 on the SH portion of the existing 72.5 kWh/m² intensity, plus the small unaffected DHW component). The LNEC TABULA switch remains the cleanest next refinement, but the deflator is methodologically independent and stays applied either way.

**Post-rebuild result (commit `efcf5fc`, 2026-05-20):** bottom-up dropped from **76.4 TWh (+264 %)** to **32.4 TWh (+54 %)** vs Hotmaps 21.0. The 0.275 deflator **under-delivered relative to the original projection** (~23 TWh expected). Math: the deflator acts on SH only; PT DHW ≈ 1.05 Bn m² × 14 kWh/m² ≈ 15 TWh, so SH-after-deflator was 76.4 × ~0.27 ≈ 17 TWh, plus 15 TWh DHW = 32 TWh. The original projection implicitly treated the full 76.4 TWh as deflatable, which was wrong.

**Two paths to OK band:**
1. **Tighten the deflator to 0.10** — the Magalhães & Leal (2014) measured-vs-nominal lower bound (PT mainland space-heating-actual at ~5 % of REPRS-nominal; the strongest published TABULA-vs-actual gap in the EU). This would land PT at ~21 TWh, OK band. Academically defensible from the same Magalhães citation already in `pt.yaml`.
2. **Switch from ES proxy to LNEC PT-direct TABULA** (highest-leverage refinement per audit doc). Same outcome via a cleaner methodology path; requires manual LNEC brochure extraction.

Until one of these is applied, PT remains INV at +54 %.

**Sources:**
- Magalhães, S.M.C. & Leal, V.M.S. (2014) "Characterization of thermal performance and nominal heating gap... Portugal mainland", *Energy and Buildings* 70: 167–179. DOI 10.1016/j.enbuild.2013.11.054.
- Magalhães, S.M.C., Leal, V.M.S., Horta, I.M. (2016), *Energy and Buildings* 119: 293–299 (winter T monitoring).
- INE, Censos 2021 — Condições de Habitação (8-Feb-2023 destaque).
- INE / DGEG, ICESD 2020 destaque (19-Jul-2021).
- Cardoso et al. (2021), *Atmosphere* 12(6): 715 (Portuguese REPRS HDD base 18 °C).
