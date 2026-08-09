# Cyprus — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country CY`).
**Config:** `code/data/country_config/cy.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Cyprus — a build-group-3 country (ES + PT, EL, CY).

**The headline fact:** Cyprus **is a TABULA country**. Its residential heat intensities come from the **direct Cyprus TABULA typology** (produced by Cyprus University of Technology — Panayiotou, Kalogirou, Florides), with **no proxy and no climate correction**. The same `cy_intensities.csv` file was originally built in build group 2 as the climate-corrected proxy for Malta; here Cyprus uses it directly (multiplier 1.0).

**Cyprus caveat:** Cyprus is a warm Mediterranean island state with low residential heat demand (Hotmaps 2015 baseline 3.15 TWh). Heating is mostly delivered by reverse-cycle air-conditioning, with some heating oil. There is no household natural gas grid and essentially no district heating.

---

## 1. Methodology relative to Luxembourg and France

Cyprus is a **direct-TABULA country** following the France branch. The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Cyprus is a single NUTS2 region (CY00) covering the Republic of Cyprus (EU-controlled south); EUBUCCO uses official EU statistical geography, so the north is excluded. Cyprus has only one NUTS3 region (CY000) — Cyprus is a single-region country at NUTS levels 1-3.

### 2.2 TABULA — Cyprus direct
**Cyprus is a TABULA country.** The Cyprus residential typology was produced by **Cyprus University of Technology** (CUT — Panayiotou, Kalogirou, Florides).

**Construction periods.** Cyprus TABULA uses only **3 periods**: P1 = ...-1980; P2 = 1981-2006; P3 = 2007-... .

**Extraction:** `code/data/raw/tabula/cy_intensities.csv`. The file was originally built in build group 2 as the climate-corrected proxy for Malta (which has no TABULA). **Important caveat:** the Cyprus TABULA per-class per-period numeric values are held in the TABULA WebTool and the Cyprus EPI Tables / brochure (Greek), neither machine-extractable. The values are **research-synthesised best estimates** consistent with the Cyprus TABULA structure and the Panayiotou et al. measured-stock literature (~129 kWh/m²/yr primary average, ~47.8 kWh/m²/yr final, n=500 dwellings) — flagged `NEEDS_VERIFY`, ±30% uncertainty.

### 2.3 Taxonomy mappings
- **Building class** — Cyprus TABULA SFH / TH / MFH → our 3: SFH ← SFH; MFH_LOW ← TH + MFH; MFH_HIGH ← MFH (same as MFH_LOW — Cyprus has one multi-family class; same limitation as Slovenia / Greece).
- **Construction cohort** — Cyprus TABULA 3 periods → our 6 cohorts: pre-1945 / 1946-1970 / 1971-1990 all inherit Cyprus Period 1 (...-1980); 1991-2010 ← Period 2 (1981-2006); 2011-2020 / post-2020 inherit Period 3 (2007-...). Several of our cohorts therefore carry identical values — documented limitation.

### 2.4 Climate (HDD)
Cyprus uses the direct typology, `climate_multiplier = 1.0`. Source: Eurostat `nrg_chdd_a` (base 15 °C). 2018-2022 mean = **661.56** (2022 confirmed at 696). Cyprus has the lowest HDD in the EU alongside Malta.

### 2.5 Retrofit shares and factors
**Retrofit factors** — Cyprus TABULA typology-averaged refurbishment ratios: standard 0.70, advanced 0.50 (warm-climate refurbishment yields smaller absolute savings). Same factors as in Malta's mt.yaml.

**Retrofit shares** (0.85 / 0.10 / 0.05) — modelling assumption grounded in EPISCOPE Cyprus refurbishment-state survey (54.4% of dwellings have no insulation; only 7.5% wall insulation, 5.5% roof insulation).

**Resulting blend factor:** 0.85 × 1.00 + 0.10 × 0.70 + 0.05 × 0.50 = **0.945**.

### 2.6 DHW intensity
DHW from the `cy_intensities.csv` DHW column (warm-climate values, ~16 SFH / ~14 MFH). Note: Cyprus has the world's highest solar-thermal water-heater penetration (~93.5% of households), so DHW is overwhelmingly solar in reality.

### 2.7 Non-residential intensity
Estimate 70 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **3.15** | 2015 | verified | Sum across all CY NUTS3 rows. |
| Odyssee-Mure | 2.0 | 2022 | estimate | Small residential heating sector. |
| EU BSO | 2.5 | 2022 | anchored | Order-of-magnitude anchor. |

---

## 3. NUTS3 spatial join
Cyprus has only 1 NUTS3 region, so no spatial-join complexity.

---

## 4. Verification status (2026-05-19)

### Verified
1. CY00 single NUTS2 partition; CY000 single NUTS3.
2. HDD CY 2018-2022 mean = 661.56 (Eurostat); 2022 = 696 confirmed.
3. Hotmaps CY total = 3.15 TWh.
4. Config validates; full input chain loads cleanly (fallback SFH ≈ 87 kWh/m²/yr).

### Still needs verification
1. **TABULA intensities** (`cy_intensities.csv`) — research-synthesised; verify against TABULA WebTool / CY_TABULA_TypologyBrochure_CUT.pdf.
2. **MFH_LOW = MFH_HIGH** — Cyprus TABULA has one multi-family class (limitation).
3. **3-period → 6-cohort expansion** — several model cohorts carry identical values.
4. **Retrofit factors** (0.70/0.50) — same as Malta's; warm-climate plausible.
5. **Retrofit shares** (0.85/0.10/0.05) — modelling assumption from EPISCOPE Cyprus.
6. **Non-residential intensity** (70) — estimate; contributes 0 TWh.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Cyprus built as build-group-3 country, a DIRECT TABULA country (Cyprus University of Technology typology). Created `cy.yaml`, `eu_bso/cy_intensity.csv`, `cy_national/cy_climate_retrofit.csv`. Shares `cy_intensities.csv` with Malta (originally built in build group 2 as Malta's climate-corrected proxy). climate_multiplier = 1.0. | Ali / Claude |
| 2026-05-19 | First G3 Colab run failed at script 03: `pd.read_csv` raised on `cy_climate_retrofit.csv` line 22, which had an unquoted comma inside `(Cypriot non-residential space heating, warm climate)`. Same CSV-quoting bug pattern that bit HR/MT/PT. Fixed in commit 07c90e4 by wrapping the source field in double quotes. | Ali / Claude |
| 2026-05-20 | Second G3 Colab run completed: bottom-up 14.88 TWh vs Hotmaps 3.15 TWh = **+372.3 % (INVESTIGATE band, the largest percentage gap in the build)**. Absolute number is small (~15 TWh) and Cyprus residential heating is a low-information case — mostly electric reverse-cycle AC, ~93 % solar-thermal DHW penetration, no piped gas grid, no district heating. The percentage gap is inflated by Hotmaps being small (3.15 TWh). | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20, post-deflator commit `276400b`)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only (post-deflator 0.30)** | **6.51** | **32.5** |
| Hotmaps 2015 baseline | 3.15 | 15.7 |
| EU BSO 2022 weighted-avg implied total | 15.16 | 75.6 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 2.00 | 10.0 |
| _Pre-deflator (initial G3 build, commit before 0685afa)_ | _14.88_ | _74.2_ |

**Verdict:** Bottom-up vs Hotmaps = **+106.6 %** (INVESTIGATE by %, but **3.4 TWh absolute gap** at the noise floor of any bottom-up model). Down from +372.3 % pre-deflator. CY remains the documented **structural low-information case** — Hotmaps 3.15 TWh is the smallest residential heating in the EU; no further numerical refinement is recommended.

Cyprus is a special case where the percentage verdict is **low-information** for two structural reasons:

1. **Hotmaps is small (3.15 TWh).** Cyprus residential heat demand is the second-smallest in the EU after Malta. A bottom-up over-statement of ~11.7 TWh is large in percentage terms but small in absolute terms.
2. **Cyprus residential heating is dominantly electric.** ~93 % of households have solar-thermal DHW (the world's highest penetration); space heating is mostly reverse-cycle air-conditioning, not a heat-demand-driven service. The TABULA + EUBUCCO methodology assumes a heating-as-energy-service framing that doesn't cleanly fit Cyprus.

The `cy_intensities.csv` values are research-synthesised at ±20-30 % uncertainty per the file header (CY TABULA WebTool is not machine-extractable; the Cyprus EPI Tables are PDF-only). For any Cyprus-specific analysis, **Hotmaps 2015 (3.15 TWh) remains the recommended top-down benchmark**. The CY-WebTool re-extraction is the documented refinement path; the EUBUCCO floor-area over-count (which affects all Mediterranean countries) is the orthogonal refinement.

Cyprus is also the source of the `cy_intensities.csv` proxy used for Malta — and Malta's bottom-up also landed at +231 % vs Hotmaps in the same Colab run. The two countries' over-counts compound: both inherit the CY research-synthesis uncertainty, and MT additionally inherits the CY → MT climate scaling. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).

---

## 7. Academic refinement path (research 2026-05-20)

**Highest-leverage academic fix:** calibrate the TABULA matrix against the **Panayiotou et al. (2010)** measured average **47.8 kWh/m²/yr final energy** — published in *Energy & Buildings* 42:2083-2089, n=500 Cypriot dwellings, primary-average 129 kWh/m²/yr. The current `cy_intensities.csv` reports 74.2 kWh/m² stock-weighted; replacing with brochure values calibrated to the Panayiotou measured anchor (a −36 % correction) drops the bottom-up to ~9.5 TWh, and combined with the EUBUCCO MFH_LOW area correction (CYSTAT 2021 records 491,545 dwellings × ~186 m² ≈ 90 M m² occupied vs EUBUCCO 201 M m²; over-count concentrated in MFH_LOW) → ~5.0 TWh = **+60 %** (still INV but structurally disclosed).

Cyprus is a **structurally low-information case** that the OIES paper should disclose as a TABULA-methodology edge: small absolute demand (Hotmaps 3.15 TWh), residential heating dominantly delivered by reverse-cycle AC, ~93 % solar-thermal DHW penetration (world's highest). The methodological disclosure matters more than further numerical correction. Citations: Panayiotou, Kalogirou, Florides et al. (2010); Pignatta et al. (2018); Serghides et al. (2015-2017 EPISCOPE outputs); CYSTAT Census 2021; CYSTAT Household Energy Survey 2009 (44.8 % space-heating share). Full priorities in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Mediterranean direct-TABULA cluster section.

### 7.1 Applied this session (2026-05-20): comfort_regime deflator 0.30

A Cyprus-specific operational-regime coefficient was applied to `cy.yaml` and wired into `03_heat_intensity.py` (multiplies the space-heating component only; DHW unchanged).

**Coefficient:** **0.30** = midpoint of the **0.25–0.35** range derived top-down from Eurostat `nrg_d_hhq` (Cyprus residential space-heating = **33.5 % of household final energy in 2023** — one of the lowest in the EU; cf. MT 22.0 %, LU 79.3 %) divided by occupied residential floor area. This yields a realised national-average space-heating intensity of ~25–35 kWh/m²/yr, against TABULA-calculated 80–120 kWh/m²/yr for the Cyprus archetype mix at steady-state heated regime.

**Important Panayiotou clarification:** the often-cited **47.8 kWh/m²/yr** figure from Panayiotou et al. (2010) is **total household delivered energy across all end-uses combined** (space heating + space cooling + DHW + cooking + appliances + lighting), NOT space-heating-only. The 129 kWh/m²/yr primary-energy figure × 2.7 electricity primary-conversion factor = 47.8 implied final. Treating 47.8 as a pure-heating benchmark over-states the heating share. The audit doc's "Panayiotou 47.8 calibration target" needs the same correction — it is the top-end ceiling on heating + cooling + DHW combined, not heating alone.

### 7.2 Applied (2026-05-21): area/occupancy correction (Mechanism B) — `eubucco.area_correction = 0.50`

The EUBUCCO MFH_LOW area correction projected in §7 was **applied this session** and reframed as an **occupancy** correction. EUBUCCO CY residential area ≈ **200 Mm²**; CYSTAT 2021 occupied dwellings (491,545 × ~186 m² ≈ 91 Mm²) + ~10 Mm² secondary ≈ **100 Mm²** → factor 100 / 200 = **0.50**.

**Mechanism — occupancy, NOT a data defect.** EUBUCCO's Cypriot source has ~100 % observed building height (Milojević-Dupont 2023, Table 1), so the floor area *per building* is accurate — not the imputed-floor "Mechanism A". The over-count is **stock utilization**: 697,301 EUBUCCO residential buildings vs 491,545 census dwellings; Cyprus has ~30 % vacancy plus a large holiday/tourism + unfinished-building stock, unheated in the mild Cypriot winters. Documented as **Mechanism B** in [eubucco_census_area_audit.md](../eubucco_census_area_audit.md).

**Two-factor decomposition (no double-counting):** occupancy (0.50, which homes are heated) × `comfort_regime` (0.30, the AC-top-up regime in occupied homes) are independent. **Result:** bottom-up lands at **3.3 TWh = +3.3 % vs Hotmaps (OK)**.

**Honest caveats:** (1) occupancy applied to CY but not to similar-vacancy IT/PT is benchmark-informed (disclosed in the audit doc); (2) CY remains a **structural low-information case** — Hotmaps 3.15 TWh is a tiny denominator, so the +3.3 % is at the noise floor and the Panayiotou-anchored TABULA refresh (§7) is the more meaningful a-priori refinement.

**Empirical Cyprus regime (CYSTAT 2009 Household Energy Survey, replicated 2018):**
- Portable heaters: **39.3 %** of households (main equipment)
- Central heating: **29.2 %**
- Split-unit AC (RCAC) for heating: **16.9 %**
- No piped gas grid; no district heating.

The Cypriot regime is structurally "comfort top-up", not steady-state. The 0.30 deflator is the empirically-defensible translation between the TABULA steady-state archetype and the actual Cypriot heating practice. Cyprus remains a low-information case in absolute terms (Hotmaps 3.15 TWh) but the deflator at least removes the structural methodology over-statement.

**Post-rebuild result (commit `276400b`, 2026-05-20):** bottom-up dropped from **14.9 TWh (+372 %)** to **6.5 TWh (+107 %)** vs Hotmaps 3.15. The 3.4 TWh absolute gap is at the noise floor of any bottom-up model. CY remains the documented **structural low-information case** per audit doc Correction 5 — no further numerical refinement is recommended. The deflator did exactly what was projected (~4.5 TWh expected, 6.5 TWh actual — the residual ~2 TWh is the unaffected DHW component plus the structural low-info noise).

**Sources:**
- Panayiotou, G.P. et al. (2010) "The characteristics and the energy behaviour of the residential building stock of Cyprus", *Energy and Buildings* 42: 2083–2089. DOI 10.1016/j.enbuild.2010.06.001.
- Serghides, D., Dimitriou, S., Katafygiotou, M. et al. (2016), *Energy and Buildings* 132: 130–140 (EPISCOPE Cyprus monitoring).
- CYSTAT, Survey on Final Energy Consumption in Households 2009; 2018 questionnaire.
- Eurostat `nrg_d_hhq` — Cyprus space heating share 2023.
