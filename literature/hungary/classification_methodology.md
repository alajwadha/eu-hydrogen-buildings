# Hungary — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country HU`).
**Config:** `code/data/country_config/hu.yaml`.

This document describes how the buildings-model methodology is applied to Hungary — a build-group-4 country (PL + CZ, SK, HU; the Visegrad group).

**The headline fact:** Hungary **is NOT a TABULA-12 country**. The EPISCOPE country page (`episcope.eu/building-typology/country/hu`) lists Hungary only under the follow-up project with no harmonised national-typology brochure matrix. BME (Budapest University of Technology and Economics; Csoknyai 2016) and EMI (Hungarian Building Research Institute) have published Hungarian-stock archetype papers, but these are not in the TABULA-harmonised q_h_nd format. The previous memory note "HuTABULA direct" was **verified incorrect** during this build.

**Decision:** Germany (DE) is used as the **climate-corrected TABULA proxy**. DE chosen over PL because the Hungarian Pannonian-continental climate (~2440 HDD) is closer to the DE DIN-V-18599 reference climate (3300) after climate-multiplier than to the Polish national EK calibration (3159). DE TABULA has a richer 4-class taxonomy and direct net q_h_nd values (published by IWU 2015), versus PL which is itself EK-derived.

**Refinement path:** a future Hungary-direct `hu_intensities.csv` built from Csoknyai 2016 / Hrabovszky-Horvath 2013 BME archetypes would replace the DE proxy. Documented as a follow-up.

---

## 1. Methodology relative to Luxembourg and France

Hungary is a **proxy country** following the Croatia/Malta branch. The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

Hungary uses the new `climate.tabula_reference_hdd` field (introduced May 2026; see `literature/climate_reference_hdd_audit.md`). The DE TABULA values are calibrated to the DIN V 18599-10 reference climate (Wuerzburg ~3300 HDD), NOT the DE national mean (2846). The Hungarian multiplier is therefore `HDD_HU / 3300 = 2440 / 3300 = 0.7394` — NOT `HDD_HU / HDD_DE_actual`.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016 vintage). Hungary's NUTS2 set under NUTS 2016 had **7 regions** — HU10 (Kozep-Magyarorszag, Central Hungary, Budapest + Pest combined) plus HU21/HU22/HU23/HU31/HU32/HU33. The HU10 → HU11 + HU12 split took effect only from the 2018 amendment (Commission Reg. 2017/2391). The notebook assumes EUBUCCO v0.2 uses the pre-2018 7-region set. **NEEDS_VERIFY** by spot-checking the EUBUCCO HU partition `region_id` values.

20 NUTS3 regions under NUTS 2016: HU101 Budapest, HU102 Pest, plus 18 stable HU2xx / HU3xx codes. HU101 + HU102 were renumbered to HU110 / HU120 in NUTS 2021; the repo GISCO file (NUTS 2021) carries the post-amendment codes — do NOT use those for the EUBUCCO join.

### 2.2 TABULA — Germany proxy
Hungary uses `de_intensities.csv` (German TABULA / IWU 2015). The German typology is the highest-quality continental archetype set in the repo with direct net q_h_nd values.

**Limitation:** Hungary's large 1949-1989 panelhaz stock is not perfectly represented by DE archetypes. The DE TABULA AB (GMH/Hochhaus) class has different period definitions, and the panelhaz envelope construction differs from German GMH. The follow-up path (a Hungary-direct file from BME literature) addresses this.

### 2.3 Taxonomy mappings
- **Building class** — DE TABULA SFH / TH+MFH avg / AB → our 4: SFH ← EFH (Einfamilienhaus, detached); MFH_LOW ← avg(RH Reihenhaus, MFH up to ~12 dwellings); MFH_HIGH ← AB (GMH + HH, large apartment block / high-rise). NON_RESIDENTIAL not in TABULA.
- **Construction cohort** — DE TABULA periods A-L → our 6 cohorts (German aggregation already done in `de_intensities.csv`).
- **MFH_HIGH** — DE TABULA has gaps in the post-F (1969-1978) era for the GMH/AB class; flagged in `de_intensities.csv` header. The Hungarian panelhaz stock is poorly represented by the DE post-1990 cells.

### 2.4 Climate (HDD)
Source: Eurostat `nrg_chdd_a` (base 15 °C). HU 2018-2022 mean = **~2440** (best estimate; NEEDS_VERIFY exact via A.NR.HDD.HU). DE actual 2018-2022 mean = 2845.85. **`tabula_reference_hdd = 3300`** (DE DIN V 18599-10 Wuerzburg reference; inherited from de.yaml). **Climate multiplier = 2440 / 3300 = 0.7394**.

### 2.5 Retrofit shares and factors
**Retrofit factors** — best-estimate continental values: standard 0.62, advanced 0.35. The pure DE-proxy factors (0.55 / 0.18 from IWU 2015) are too aggressive for Hungary because the dominant Hungarian renovation programmes — Otthon Felujitasi Program (2021-2022) and Panel Plus / Otthon Melege (2014-2020) — deliver mostly partial envelope work, not full IWU "zukunftsweisend" deep retrofit.

**Retrofit shares** (0.78 / 0.17 / 0.05) — modelling assumption. The Otthon Felujitasi 2021-2022 subsidy reached ~250-300k dwellings (~6-7 % of stock); the Hungarian LTRS 2020 acknowledges ~70 % of pre-1992 stock is not deep-renovated.

**Resulting blend factor:** 0.78 × 1.00 + 0.17 × 0.62 + 0.05 × 0.35 = **0.9029**.

### 2.6 DHW intensity
DHW from `de_intensities.csv` proxy at the HU level: SFH 14, MFH 15 kWh/m²/yr (between DE 11/16 and PL 28/23). NEEDS_VERIFY against Csoknyai 2016 archetypes.

### 2.7 Non-residential intensity
Estimate 110 kWh/m²/yr (Hungarian non-residential continental tertiary stock). `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **71.98** | 2015 | verified | Sum across 20 HU NUTS3 rows in `building_stock_nuts3.csv`. |
| EU BSO | 55 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |
| Odyssee-Mure | 45 | 2022 | estimate | Hungarian households final energy ~80 TWh; space heating ~56 %. |

---

## 3. NUTS3 spatial join
Hungary has 20 NUTS3 regions. HU101 / HU102 (Budapest / Pest) were renumbered to HU110 / HU120 at the 2018 amendment. The YAML uses NUTS 2016 codes to align with EUBUCCO v0.2.

---

## 4. Verification status (2026-05-19)

### Verified
1. 7 NUTS2 partitions (NUTS 2016 pre-2018 vintage; HU10 single Central Hungary).
2. 20 NUTS3 regions extracted from Hotmaps HU rows (NUTS 2016).
3. Hotmaps HU total = 71.98 TWh.
4. Config validates; full input chain loads cleanly (fallback SFH ≈ 144 kWh/m²/yr).
5. HU is NOT in TABULA-12 — confirmed (memory note corrected).

### Still needs verification
1. **EUBUCCO HU NUTS2 vintage** — assumed 7-region pre-2018 (HU10 single); if EUBUCCO uses 8-region post-2018 (HU11 + HU12), the `nuts2_partitions` list needs updating. Spot-check EUBUCCO HU partition `region_id` values.
2. **HDD 2018-2022 mean (2440)** — best estimate; direct Eurostat `nrg_chdd_a` extraction via A.NR.HDD.HU not yet done.
3. **`tabula_reference_hdd = 3300`** — inherited from de.yaml (DIN V 18599-10 Wuerzburg).
4. **Retrofit factors (0.62 / 0.35)** — provisional; cross-check against Csoknyai 2016 panel-block retrofit studies.
5. **Retrofit shares (0.78 / 0.17 / 0.05)** — modelling assumption from Otthon Felujitasi completion figures and LTRS-HU 2020.
6. **DHW (14 / 15)** — provisional continental defaults; verify against Csoknyai 2016.
7. **Non-residential intensity** (110) — rough placeholder.
8. **EU BSO total** (55) — anchored estimate.
9. **Odyssee-Mure total** (45) — Eurostat households disaggregation.
10. **REFINEMENT PATH** — a Hungary-direct `hu_intensities.csv` from BME archetype literature (Csoknyai 2016; Hrabovszky-Horvath 2013) would replace the DE proxy. Documented as a follow-up.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Hungary built as build-group-4 country with Germany as the climate-corrected TABULA proxy. Previous memory note "HuTABULA direct" verified incorrect — HU is NOT in TABULA-12 (EPISCOPE country page confirmed). Created `hu.yaml`, `eu_bso/hu_intensity.csv`, `hu_national/hu_climate_retrofit.csv`. Reuses `de_intensities.csv`. climate_multiplier = 0.7394; tabula_reference_hdd = 3300 (DE DIN V 18599-10 Wuerzburg reference inherited from de.yaml). | Ali / Claude |
| 2026-05-20 | Option B reference-HDD correction for HU **REVERTED** after the parallel DE revert: DE was found to reconcile cleanly at climate_multiplier = 1.0 (its DIN-Wuerzburg Option B correction would have broken its OK reconciliation). HU therefore recomputed against DE actual HDD (2846) instead of DE reference HDD (3300): new `climate_multiplier = 2440 / 2845.85 = 0.8574`. The HU YAML no longer carries an explicit `tabula_reference_hdd` (defaults to hdd_proxy = 2845.85). | Ali / Claude |
| 2026-05-20 | First G4 Colab run failed at script 01: EUBUCCO bucket HTTP 404 for the HU NUTS2 partitions. The YAML used 7 NUTS 2016 codes (HU10 + HU2x + HU3x), but direct `curl` probes showed EUBUCCO v0.2 uses 8 **NUTS 2021** codes for Hungary (HU10 → 404; HU11 → 200; HU12 → 200). HU10 was split into HU11 (Budapest) + HU12 (Pest) in the 2018 NUTS amendment, and EUBUCCO honoured it. | Ali / Claude |
| 2026-05-20 | Fixed in commit `bc70d66`: replaced `eubucco.nuts2_partitions` with the 8 NUTS 2021 codes (HU11/HU12/HU21/HU22/HU23/HU31/HU32/HU33) and the `nuts3_regions` list (HU110/HU120 replacing the NUTS 2016 HU101/HU102). Updated `hotmaps_nuts3_id` HU101 → HU110 (Budapest). | Ali / Claude |
| 2026-05-20 | G4 Colab re-run completed: bottom-up 99.68 TWh vs Hotmaps 71.98 TWh = **+38.5 % (INVESTIGATE band)**. EUBUCCO HU classified 5.93 M buildings across 8 NUTS2 partitions; the NUTS 2021 fix worked first try. The gap exceeds the prediction in the pre-build placeholder (expected OK to ACC); HU joins ES, PT, EL, CY, HR, MT, EE, LT in the INVESTIGATE band. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **99.68** | **150.0** |
| Hotmaps 2015 baseline | 71.98 | 108.3 |
| EU BSO 2022 weighted-avg implied total | 86.17 | 129.7 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 45.00 | 67.7 |

**Verdict:** Bottom-up vs Hotmaps = **+38.5 %** (INVESTIGATE — outside ±25 % band).

Hungary is the **9th country in the INVESTIGATE cluster** — but a structurally distinct case from the Mediterranean (ES/PT/EL/CY/HR/MT) and Baltic (EE/LT) over-counts. The decomposition is:

- **EUBUCCO floor area is reasonable.** Our 0.665 Bn m² for HU vs population × census m²/dwelling (9.6 M × ~70) ≈ 0.67 Bn m² is essentially a match. No area issue.
- **Intensity is the entire driver.** Bottom-up 150.0 kWh/m² vs Hotmaps-implied 108.3 kWh/m² = ~38 % over. The DE-proxy TABULA values, climate-scaled by 0.8574 (HU/DE actual HDD), still over-state Hungarian residential heating intensity by ~40 %.

**This is the first INV result for a DE-proxy country**, and it suggests two compatible interpretations:

1. **Hungarian heating culture differs from German.** Hungarian homes have lower thermal comfort baselines historically (KSH energy-poverty data show ~15-20 % of households consistently report inability to keep adequately warm). The German TABULA's archetypes assume a steady heated reference condition that Hungarian residents do not match — analogous to the Portuguese vs Spanish gap (PT +264 % with ES proxy).
2. **The HU retrofit-share assumption may be too conservative.** I used 0.78/0.17/0.05 (original/standard/advanced); Hungary's panelház renovation programmes (Panel Plus 2014-2020, Otthon Felujitasi 2021-2022, Otthon Melege) may have delivered more "standard" retrofit than 17 % of stock. The Slovak comparison is instructive: SK uses retrofit shares 0.55/0.40/0.05 reflecting the SFRB Obnova programme and lands at +2.2 %; if Hungary's actual standard share were closer to 0.30-0.40, the BU would drop substantially.

**Hotmaps remains the recommended residential heat-demand benchmark for Hungary.** Two refinement paths:

- **Re-derive HU retrofit shares** from Otthon Felujitasi / Panel Plus completion data (Magyar Falu Program reports; ÉMI evaluations). This is the most actionable next step — it could close half the gap.
- **Build a Hungary-direct `hu_intensities.csv`** from BME archetype literature (Csoknyai 2016; Hrabovszky-Horvath 2013) instead of the DE proxy. This is the longer-term refinement.

See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) for the broader build-wide audit and the cross-country over-count patterns.

---

## 7. Academic refinement path (research 2026-05-20) — Correction 1 of the build

**SESSION FINDINGS (high-importance, applied 2026-05-20):**

1. **`hu.yaml` header CORRECTED.** The earlier YAML asserted "Hungary is NOT a TABULA-12 country" — VERIFIED INCORRECT by direct inspection of `episcope.eu/building-typology/country/hu/`. Hungary IS in TABULA-EPISCOPE via **BME (Budapest University of Technology and Economics)**; the published brochure `HU_TABULA_TypologyBrochure_BME.pdf` (2014-10-21) carries 15 archetypes × 6 cohorts (pre-1944; 1945-60; 1961-79; 1980-89; 1990-2001; post-2001) × building categories (SFH <80 / ≥80 m²; MFH 4-9 flats; MFH ≥10 flats traditional / panel / industrialised). The brochure is image-based; manual table extraction is required.

2. **HU retrofit shares UPDATED to BPIE-grounded values.** Prior shares 0.78/0.17/0.05 (blend 0.9029) over-stated Hungarian renovation reach. BPIE/EUKI (2025) *JustReno: Baseline Assessment Report for Hungary* reports HU annual renovation rate **0.3-0.5 %/yr — lowest in the EU**. Compounded with programme-specific cumulative counts (Otthon Felujitasi 2021-2022: ~370k families, ~40-50 % envelope use = 150-185k dwellings = 3.4-4.2 %; Panelprogram 2001-2007 + Otthon Melege continuation to ~250-280k panel dwellings by 2020 = 5.7-6.4 %; Otthon Melege deep-retrofit subset 13,975 dwellings = 0.3 %), the de-duplicated cumulative is ~10 % standard + ~2 % advanced. **New shares 0.88/0.10/0.02 (blend 0.949)** — academically correct; widens the BU vs Hotmaps gap from +38.5 % to **~+45.6 %**, which exposes that the DE-proxy archetype intensities are the binding constraint (the gap was previously masked by over-stated retrofit reach).

**Highest-leverage academic fix (deferred — requires manual extraction):** **Build `code/data/raw/tabula/hu_intensities.csv` from the BME brochure** and switch `tabula.source_country: HU`. Expected outcome: bottom-up lands within ±5-10 % of Hotmaps (SK precedent at +2.2 % suggests this is realistic — SK uses CZ-direct TABULA + aggressive panel-retrofit shares for analogous panelové domy / panelház stock). Companion peer-reviewed sources for the same matrix: **Csoknyai T. et al. (2016)** *Energy & Buildings* 132:39-52 (DOI 10.1016/j.enbuild.2016.06.062); **Hrabovszky-Horváth S. et al. (2013)** *Energy & Buildings* 62:475-485 (DOI 10.1016/j.enbuild.2013.03.011); **Hrabovszky-Horváth S. (2015)** BME doctoral dissertation on panelház q_h_nd before/after retrofit.

**Important verified finding (Component A from the research dossier is moot):** the `unknown`-cohort fallback in `03_heat_intensity.py` already uses the Hungarian BSO file `stock_pct_hu` weights × DE archetype intensities × HU climate scaling. So the existing pipeline correctly applies Hungarian stock weights, not DE weights, even when EUBUCCO has no construction-year tag for a building. The over-statement is in the DE archetype intensities themselves, not in their weighting. This rules out one hypothesis and confirms the BME extraction is the binding refinement.

> **[SUPERSEDED 2026-05-21 — "DE archetype intensities are the binding constraint" is WRONG.]** The per-m² arithmetic refutes it: the model's mean residential intensity is 99.68 TWh / 664.3 Mm² = **150 kWh/m²**, BELOW the Hotmaps-implied 71.98 TWh / 377 Mm² census area = **191 kWh/m²**. The DE proxy does not over-state per-m² — the entire +38.5 % gap is an EUBUCCO **area** over-count. See "Applied" below.

## Applied (2026-05-21): EUBUCCO area correction (Mechanism A) — `eubucco.area_correction = 0.57`

Applied an area correction; HU now lands at **59.5 TWh = −17 % (ACC)** — without the BME extraction.

**Mechanism — imputed floors (data quality).** EUBUCCO HU is on the low-coverage list AND has ~3 % observed heights → floor counts are largely ML-imputed. EUBUCCO HU residential area = **664 Mm²** vs KSH 2022 (4.6 M dwellings × 82 m²) = **377 Mm²** → factor 377/664 = **0.57** (**Mechanism A** family, [eubucco_census_area_audit.md](../eubucco_census_area_audit.md)). The −17 % residual under-shoot is consistent with MFH common-area heating excluded from the dwelling-only census (HU ~35 % MFH). The BME-direct `hu_intensities.csv` switch remains a valid refinement for the per-archetype *distribution* but is **NOT required for reconciliation** — the binding constraint was area, not intensity. Census-grounded, not Hotmaps-tuned.

Full per-country research, retrofit-share programme citations, and the cross-country over-count patterns are in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — "Correction 1" section and the HU detailed entry.
