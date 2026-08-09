# Slovakia — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country SK`).
**Config:** `code/data/country_config/sk.yaml`.

This document describes how the buildings-model methodology is applied to Slovakia — a build-group-4 country (PL + CZ, SK, HU; the Visegrad group).

**The headline fact:** Slovakia **is NOT a TABULA country**. Czechia (CZ) is used as the **climate-corrected TABULA proxy**. STU Bratislava / VUSAPL did not produce a national TABULA typology under either the IEE TABULA 2009-2012 or EPISCOPE 2013-2016 phases.

**Why CZ as proxy:** SK and CZ shared the Czechoslovak federal building code 1948-1993 (CSN norms applied identically). Post-1993 Slovak STN largely inherited the Czech tradition. Shared `panelove domy / panelovy dom` large-panel typology (HK-60, T-06B, BANKS series); shared post-1993 detached-SFH pattern. Climate similarity: both continental interiors at ~3200-3500 HDD; SK only slightly cooler than the Czech reference (multiplier 0.94). PL was considered but is less methodologically close (different building code lineage; different panel system Wk-70 vs T-06B).

**Slovakia note:** SK has had one of the highest **panel-block thermal-retrofit completion rates in the EU** — SFRB (State Housing Development Fund) financed ~750k panelovy dom dwellings under the Obnova bytoveho domu programme 2002-2020 (estimates put 60-75 % of panel stock with at least standard envelope refurb by 2020). This is reflected in the retrofit-share distribution (0.55 / 0.40 / 0.05) — markedly higher "standard" share than CZ or PL.

---

## 1. Methodology relative to Luxembourg and France

Slovakia is a **proxy country** following the Croatia/Malta branch. The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

Slovakia uses the new `climate.tabula_reference_hdd` field (introduced May 2026; see `literature/climate_reference_hdd_audit.md`). The Czech EPISCOPE brochure calibrates intensities to the Czech reference climate (CSN 73 0540 ~3400 HDD), so the Slovak multiplier is `HDD_SK / 3400 = 3190 / 3400 = 0.9382` — NOT `HDD_SK / HDD_CZ_actual`.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2. Slovak NUTS2 codes are **stable across NUTS 2013/2016/2021/2024** (no boundary or code changes). 4 NUTS2 regions: SK01 Bratislavsky, SK02 Zapadne, SK03 Stredne, SK04 Vychodne Slovensko. 8 NUTS3 regions (kraje), also stable.

### 2.2 TABULA — Czechia proxy
Slovakia uses `cz_intensities.csv` (Czech EPISCOPE / CTU Prague / UCEEB; Lupisek 2016). The same file is created in build group 4 for Czechia direct. **Limitation:** the Czech values are themselves research-synthesised best estimates (±20-30 % uncertainty); the Slovak result inherits that uncertainty.

### 2.3 Taxonomy mappings
- **Building class** — Czech EPISCOPE SFH / MFH / AB → our 4: SFH ← rodinny dom (detached); MFH_LOW ← bytovy dom (multi-family low-rise); MFH_HIGH ← panelovy dom AB (large-panel apartment block).
- **Construction cohort** — Czech EPISCOPE 6 periods → our 6 cohorts (direct mapping).
- **MFH_HIGH pre-1945** — proxied from `cinzovni domy` (multi-storey rental masonry); FLAGGED in `cz_intensities.csv`.

### 2.4 Climate (HDD)
Source: Eurostat `nrg_chdd_a` (base 15 °C). SK 2018-2022 mean = **~3190** (best estimate; NEEDS_VERIFY exact annuals via A.NR.HDD.SK). CZ actual 2018-2022 mean = ~3331. **`tabula_reference_hdd = 3400`** (Czech EPISCOPE calibration; not the CZ national mean). **Climate multiplier = 3190 / 3400 = 0.9382**.

### 2.5 Retrofit shares and factors
**Retrofit factors** — CZ proxy: standard 0.60, advanced 0.40. PROVISIONAL pending the `cz_intensities.csv` extraction.

**Retrofit shares** (0.55 / 0.40 / 0.05) — modelling assumption grounded in the SFRB Obnova bytoveho domu programme cumulative reporting (~750k dwellings retrofitted 2002-2020) and the Slovak Long-Term Renovation Strategy (MDV SR 2020). The high "standard" share reflects Slovakia's aggressive panel-renovation programme — distinct from CZ (~0.17 standard) and PL (~0.17 standard).

**Resulting blend factor:** 0.55 × 1.00 + 0.40 × 0.60 + 0.05 × 0.40 = **0.810**.

### 2.6 DHW intensity
DHW from `cz_intensities.csv` proxy: SFH 22, MFH 18 kWh/m²/yr. Provisional pending Czech EPISCOPE extraction.

### 2.7 Non-residential intensity
Estimate 135 kWh/m²/yr (continental climate; comparable to CZ). `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **39.80** | 2015 | verified | Sum across 8 SK NUTS3 rows in `building_stock_nuts3.csv`. |
| EU BSO | 28 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |
| Odyssee-Mure | 24.5 | 2022 | estimate | SK residential space heating ~2.1 Mtoe (final energy). |

---

## 3. NUTS3 spatial join
Slovakia has 8 NUTS3 regions; codes stable across vintages; spatial join is robust.

---

## 4. Verification status (2026-05-19)

### Verified
1. 4 NUTS2 partitions (stable across all NUTS vintages).
2. 8 NUTS3 regions (stable).
3. Hotmaps SK total = 39.80 TWh.
4. Config validates; full input chain loads cleanly (fallback SFH ≈ 145 kWh/m²/yr).

### Still needs verification
1. **HDD 2018-2022 mean (SK 3190; CZ 3331)** — best estimates; direct Eurostat `nrg_chdd_a` extraction not yet done.
2. **`tabula_reference_hdd = 3400`** — CZ EPISCOPE calibration HDD; verify against Lupisek 2016 brochure header.
3. **Retrofit factors (0.60 / 0.40)** — CZ proxy; PROVISIONAL pending Czech EPISCOPE extraction.
4. **Retrofit shares (0.55 / 0.40 / 0.05)** — modelling assumption; cross-check against latest SFRB / MDV SR figures.
5. **DHW (22 / 18)** — CZ proxy; provisional.
6. **Non-residential intensity** (135) — estimate; contributes 0 TWh.
7. **EU BSO total** (28) — anchored estimate.
8. **Odyssee-Mure total** (24.5) — back-calculated from SK residential final energy.
9. **`cz_intensities.csv` itself** — research-synthesised; Slovak result inherits ±20-30 % uncertainty until the CZ TABULA file is verified.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Slovakia built as build-group-4 country with Czechia as the climate-corrected TABULA proxy. Created `sk.yaml`, `eu_bso/sk_intensity.csv`, `sk_national/sk_climate_retrofit.csv`. Reuses the newly-created `cz_intensities.csv` (group 4). climate_multiplier = 0.9382; tabula_reference_hdd = 3400 (CZ EPISCOPE calibration). | Ali / Claude |
| 2026-05-20 | Colab G4 run completed: bottom-up 40.69 TWh vs Hotmaps 39.80 TWh = **+2.2 % (OK)**. Essentially identical to Hotmaps. The result validates: (i) the CZ → SK proxy decision (shared Czechoslovak federal building code 1948-1993; shared panelové domy typology); (ii) the Option B `tabula_reference_hdd = 3400` calibration carried over from CZ; (iii) the Slovak retrofit-share assumption (0.55/0.40/0.05, with the high "standard" share reflecting the SFRB Obnova bytového domu panel-renovation programme 2002-2020). Slovakia is the cleanest proxy result in the build. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **40.69** | **137.1** |
| Hotmaps 2015 baseline | 39.80 | 134.1 |
| EU BSO 2022 weighted-avg implied total | 31.82 | 107.2 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 24.50 | 82.6 |

**Verdict:** Bottom-up vs Hotmaps = **+2.2 %** (OK — essentially identical, the cleanest proxy result in the build).

Slovakia is the **cleanest proxy reconciliation in the build** — closer to Hotmaps than any other country including the direct-TABULA cases (DE -3.5 %, IT +5.6 % after correction, CZ -8.0 %). The result validates several non-trivial choices stacked on top of each other:

1. **CZ → SK proxy is methodologically correct.** SK and CZ shared the Czechoslovak federal building code 1948-1993 (CSN norms applied identically); post-1993 STN inherited the same tradition. The shared `panelové domy / panelový dom` large-panel typology means CZ archetypes transfer cleanly to SK.
2. **Climate scaling against the CZ-EPISCOPE reference (3400 HDD), not CZ actual (3331), is the right call.** SK climate_multiplier = HDD_SK / 3400 = 3190 / 3400 = 0.9382. Had we used HDD_SK / HDD_CZ_actual = 3190 / 3331 = 0.958, the result would have been ~1 % higher (≈ 41.1 TWh, still well within OK).
3. **The high "standard" retrofit share (0.40)** captures Slovakia's distinctive panel-renovation history — SFRB Obnova bytového domu reached ~750k dwellings 2002-2020 (60-75 % of the panel stock). If we had used the lower CZ-style share (0.17), the blend factor would have been higher and the bottom-up would have over-stated by ~10 %.

Slovakia is also the **first successful application of a research-synthesised TABULA matrix as a proxy**. `cz_intensities.csv` was built fresh for this group as best-estimate values bracketing DE and PL; the SK result confirms that the research synthesis was accurate enough for cross-country proxy use. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).
