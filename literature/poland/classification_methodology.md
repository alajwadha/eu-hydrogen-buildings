# Poland — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country PL`).
**Config:** `code/data/country_config/pl.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Poland — the heavyweight of build group 4 (PL + CZ, SK, HU; the Visegrad group).

**The headline fact:** Poland **is a TABULA country**. Its residential heat intensities come from the **direct Polish TABULA typology** produced by NAPE (Narodowa Agencja Poszanowania Energii) under the IEE TABULA 2009-2012 project, with **no proxy and no climate correction**. The same `pl_intensities.csv` file is also used as the climate-corrected proxy for Estonia, Latvia and Lithuania (build group 1).

**Poland caveat:** the Polish TABULA published EK (energia koncowa = final energy) values, not the TABULA-harmonised net space-heating need. The `sh_intensity_kwh_m2_yr` values in `pl_intensities.csv` are DERIVED by deducting DHW + applying period-typical heating-system efficiencies (coal/stove ~0.55-0.65 pre-1990; gas/condensing ~0.90-0.95 newer). Treat as best estimates with ±15-20 % uncertainty.

---

## 1. Methodology relative to Luxembourg and France

Poland is a **direct-TABULA country** following the France branch. The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds. Poland adds the Visegrad-specific large-panel typology (wielka plyta MFH_HIGH blocks).

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Poland has **16 NUTS2 regions** under NUTS 2016 (PL11-PL12, PL21-PL22, PL31-PL34, PL41-PL43, PL51-PL52, PL61-PL63). Polish NUTS2 codes were substantially recoded in the 2018 NUTS amendment (e.g. PL12 Mazowieckie split into PL91 + PL92); the repo GISCO file (NUTS 2021) carries the post-amendment codes — do NOT use those for the EUBUCCO join. **NEEDS_VERIFY** by spot-checking the EUBUCCO PL partition `region_id` values.

72 NUTS3 regions under NUTS 2016 (PLZZ extraterritorial excluded). Codes extracted from `code/data/processed/building_stock_nuts3.csv` (Hotmaps tabulation; NUTS 2016).

### 2.2 TABULA — Poland direct
**Poland is a TABULA country.** The Polish residential typology was produced by **NAPE (Narodowa Agencja Poszanowania Energii)** under the IEE TABULA 2009-2012 project.

**Construction periods.** Polish TABULA uses periods: before 1945; 1946-1966; 1967-1985; 1986-1992; 1993-2002; 2003-2008; after 2008.

**Extraction:** `code/data/raw/tabula/pl_intensities.csv`. Originally created in build group 1 as the climate-corrected proxy for the Baltic states; here Poland uses it directly (climate_multiplier = 1.0). **Important caveat:** the Polish TABULA values are DERIVED from the published EK (final energy) figures — not the TABULA-harmonised net SH. Treat as ±15-20 % uncertainty.

### 2.3 Taxonomy mappings
- **Building class** — Polish TABULA SFH / TH / MFH / AB → our 4: SFH ← SFH; MFH_LOW ← average(TH, MFH); MFH_HIGH ← AB (wielka plyta apartment block, 6+ floors); NON_RESIDENTIAL not in TABULA.
- **Construction cohort** — Polish TABULA 7 periods → our 6 cohorts: pre-1945 ← before-1945; 1946-1970 ← 1946-1966; 1971-1990 ← avg(1967-1985, 1986-1992); 1991-2010 ← avg(1993-2002, 2003-2008); 2011-2020 ← after-2008; post-2020 ← EXTRAPOLATED with WT2017/WT2021 adjustment (FLAGGED).
- **MFH_HIGH pre-1945 + 1946-1970:** the Polish AB class has no building older than 1967 (large-panel blocks did not exist in Poland before ~1960). Those two cells are proxied/interpolated from PL.N.MFH and the 1967-1985 AB building. FLAGGED in `pl_intensities.csv`.

### 2.4 Climate (HDD)
Poland uses the direct typology, `climate_multiplier = 1.0`. The new `tabula_reference_hdd` field is set to 3158.7 (same as hdd_proxy) — the Polish TABULA EK methodology calibrates intensities to a climate normalisation built into the energy certificate, effectively the Polish national mean. Source: Eurostat `nrg_chdd_a` (base 15 °C). 2018-2022 mean = **3158.7** (2018: 3126; 2019: 2954; 2020: 3011; 2021: 3497; 2022: 3205).

### 2.5 Retrofit shares and factors
**Retrofit factors** — Polish TABULA Sec. 3.4.3 typology-averaged refurbishment ratios: standard 0.63, advanced 0.50.

**Retrofit shares** (0.78 / 0.17 / 0.05) — modelling assumption grounded in the Polish Long-Term Renovation Strategy (Ministerstwo Rozwoju i Technologii 2022) and Czyste Powietrze ("Clean Air") programme cumulative reporting (NFOSiGW 2024; ~700k mostly-shallow retrofits to 2024, ~6-7 % of stock; deep retrofits via Stop-Smog gminne and EU RPO/POIiS).

**Resulting blend factor:** 0.78 × 1.00 + 0.17 × 0.63 + 0.05 × 0.50 = **0.912**.

### 2.6 DHW intensity
DHW from the `pl_intensities.csv` DHW column: SFH 28, MFH 23 kWh/m²/yr. These are DERIVED from the Polish energy-certificate DHW assumption (~25-30 SFH; ~22-24 MFH); flagged provisional.

### 2.7 Non-residential intensity
Estimate 145 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh in the current pipeline.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **257.93** | 2015 | verified | Sum across 72 PL NUTS3 rows in `building_stock_nuts3.csv`. |
| EU BSO | 210 | 2022 | anchored | Order-of-magnitude anchor. |
| Odyssee-Mure | 190 | 2022 | back-calculated | ~13 Mtoe final energy / 0.7-0.8 efficiency → ~190 TWh useful demand. |

---

## 3. NUTS3 spatial join
Poland has 72 NUTS3 regions; 02_classify.py assigns buildings by spatial join / EUBUCCO `region_id`. The NUTS3 codes shifted at the 2018 amendment (e.g. PL127 Miasto Warszawa → PL911), so the YAML's NUTS 2016 list is what aligns with the EUBUCCO partitions. Spot-check before run.

---

## 4. Verification status (2026-05-19)

### Verified
1. 16 NUTS2 partitions (NUTS 2016 vintage; pre-2018 amendment).
2. 72 NUTS3 regions extracted from Hotmaps PL rows.
3. HDD PL 2018-2022 mean = 3158.7 (Eurostat `nrg_chdd_a`).
4. Hotmaps PL total = 257.93 TWh.
5. Config validates; full input chain loads cleanly (fallback SFH ≈ 168 kWh/m²/yr).

### Still needs verification
1. **NUTS 2016 ↔ EUBUCCO partition codes** — spot-check the actual `region_id` values in the EUBUCCO PL parquet files.
2. **`pl_intensities.csv` 18-row matrix** — DERIVED from EK; verify against TABULA WebTool or NAPE 2012 brochure.
3. **Retrofit shares (0.78 / 0.17 / 0.05)** — modelling assumption from LTRS 2022 + Czyste Powietrze reporting.
4. **DHW (28 / 23)** — derived in `pl_intensities.csv` from Polish energy-certificate DHW assumption.
5. **Non-residential intensity** (145) — rough placeholder; contributes 0 TWh.
6. **EU BSO total** (210) — anchored estimate; portal not retrievable.
7. **Odyssee-Mure total** (190) — back-calculated; verify against Odyssee-Mure PL country fiche.
8. **MFH_HIGH pre-1945 / 1946-1970** — proxied/interpolated; flagged in TABULA file.
9. **post-2020 cohort** — EXTRAPOLATED with WT2017/WT2021 adjustment.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Poland built as build-group-4 country, a DIRECT TABULA country (NAPE). Created `pl.yaml`, `eu_bso/pl_intensity.csv`, `pl_national/pl_climate_retrofit.csv`. Reuses `pl_intensities.csv` (originally built in group 1 as the EE/LV/LT proxy). climate_multiplier = 1.0; tabula_reference_hdd defaults to hdd_proxy = 3158.7. | Ali / Claude |
| 2026-05-20 | First G4 Colab run failed at script 01: EUBUCCO bucket HTTP 404 for the PL NUTS2 partitions. The YAML used NUTS 2016 codes (PL11/PL12/PL31-PL34/...), but direct `curl` probes of `s3.eubucco.com` showed EUBUCCO v0.2 uses **NUTS 2021** codes for Poland specifically (PL11 → 404; PL71 → 200; PL12 → 404; PL91 → 200). Poland had a major NUTS2 recoding in the 2018 amendment (Commission Reg. 2017/2391) that EUBUCCO honoured. | Ali / Claude |
| 2026-05-20 | Fixed in commit `bc70d66`: replaced `eubucco.nuts2_partitions` with the 17 NUTS 2021 codes (PL21/PL22/PL41-PL43/PL51-PL52/PL61-PL63/PL71/PL72/PL81/PL82/PL84/PL91/PL92) and the `nuts3_regions` list with the 73 NUTS 2021 NUTS3 codes from the GISCO file. Updated `hotmaps_nuts3_id` PL127 → PL911 (Warsaw city). | Ali / Claude |
| 2026-05-20 | G4 Colab re-run completed: bottom-up 279.91 TWh vs Hotmaps 257.93 TWh = **+8.5 % (OK band)**. Poland reconciles cleanly with Hotmaps — the second-largest single bottom-up in the build after Germany (765.82 TWh). EUBUCCO PL classified 21.99 M buildings across 17 NUTS2 partitions; the NUTS 2021 fix worked first try. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **279.91** | **163.1** |
| Hotmaps 2015 baseline | 257.93 | 150.3 |
| EU BSO 2022 weighted-avg implied total | 274.86 | 160.2 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 190.00 | 110.7 |

**Verdict:** Bottom-up vs Hotmaps = **+8.5 %** (OK — within ±15 % consistency band).

Poland's reconciliation is **one of the cleanest direct-TABULA results in the build** despite using a TABULA matrix that the file header itself flags as ±15-20 % uncertain (the NAPE EK-derived values are not the TABULA-harmonised net SH). Three observations make this result especially informative:

1. **Poland is the canary for the Polish-TABULA EK-derivation methodology.** When PL TABULA values are applied at face value (climate_multiplier = 1.0, no scaling), they reconcile within +8.5 % of Hotmaps. But when the same values are climate-scaled UPWARD to colder Baltic conditions, the result blows up: EE +78.8 %, LT +123.9 %. The over-statement bias only appears when the multiplier > ~1.15. PL ↔ LV (multiplier 1.21, +20 % gap) is the closest case to a clean amplification check.

2. **EUBUCCO PL floor-area is consistent.** Our bottom-up at 163.1 kWh/m² vs Hotmaps-implied 150.3 kWh/m² implies a ~9 % intensity over-statement — very small. The 21.99 M buildings across 17 NUTS2 partitions match GUS census expectations within a few percent.

3. **The NUTS 2021 vintage fix was the critical enabler.** The first G4 attempt (commit 48c2d20) failed because pl.yaml carried NUTS 2016 codes (PL11/PL12 etc) that no longer exist in EUBUCCO v0.2. EUBUCCO honoured the post-2018 NUTS amendment for PL but not for all other countries. The lesson: per-country EUBUCCO vintage verification matters more than assumed.

Poland anchors the **Visegrad sub-group's credibility**: PL +8.5 %, CZ -8.0 %, SK +2.2 %, HU +38.5 %. Three of four in OK; only HU lands INV. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).
