# Malta — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country MT`).
**Config:** `code/data/country_config/mt.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Malta — a build-group-2 country (IT + SI, HR, MT).

**Two headline facts.** (1) Malta is **not a TABULA country**; its residential heat intensities are **Cyprus-derived** — extracted from the Cyprus TABULA typology and climate-corrected by the Malta/Cyprus heating-degree-day ratio. (2) Malta has **the lowest residential heat demand of any country in this study** (Hotmaps 2015 baseline 0.73 TWh). Space heating is a marginal end-use: the Malta heat market is ~80% electric (reverse-cycle air-conditioning), there is no piped gas grid and no district heating.

---

## 1. Methodology relative to Luxembourg and France

Malta is a **proxy country**, following the Luxembourg branch (proxy + climate correction). The taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO — a data-availability risk
EUBUCCO v0.2 partitions by NUTS2. Malta is a single NUTS2 region (MT00), with 2 NUTS3 regions (MT001 Malta island, MT002 Gozo & Comino).

**Critical caveat.** EUBUCCO v0.1 did **not** redistribute Malta building data — the source licence did not permit redistribution; EUBUCCO instead published code to reproduce the workflow. If this persists in v0.2, the bottom-up build **cannot run** for Malta. In that case the model **falls back to the top-down Hotmaps demand** (0.73 TWh) for Malta. The Group 2 Colab notebook is fault-tolerant: a failed Malta download is logged and the loop continues. Flagged `NEEDS_VERIFY`.

### 2.2 TABULA — Cyprus as proxy
**Malta has no national TABULA typology.** Cyprus is chosen as the proxy: it is the only other small, warm-Mediterranean island state (Köppen Csa) with a TABULA typology, with comparable masonry construction and a heating-marginal, reverse-cycle-AC-dominated heat market. Greece is a secondary cross-check.

**Extraction:** `code/data/raw/tabula/cy_intensities.csv`. **Important caveat:** the Cyprus TABULA per-type values are held in the TABULA WebTool (interactive) and not machine-extractable. The `cy_intensities.csv` values are **research-synthesised best estimates** for a warm-Mediterranean country with low heating demand — flagged `NEEDS_VERIFY`, ±30% uncertainty. Because Malta's heating demand is negligible and EUBUCCO may not even hold Malta data, the precision of this file has minimal effect on study results. The Cyprus typology has only 3 construction periods, so several of the model's 6 cohorts carry identical values (a documented limitation).

### 2.3 Climate (HDD)
`climate_multiplier = HDD_MT / HDD_CY`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022:
- Malta: 386.91 / 540.06 / 418.24 / 482.13 / 557.81 → **mean 477.03** — effectively the lowest HDD in the EU.
- Cyprus: → **mean 661.56**.
- `climate_multiplier = 477.03 / 661.56 = 0.7210`.

### 2.4 Retrofit shares and factors
**Retrofit factors** — the Cyprus TABULA refurbishment ratios (standard 0.70, advanced 0.50), used as the proxy. **PROVISIONAL**. Warm-climate refurbishment yields smaller absolute savings.

**Retrofit shares** (0.92 original / 0.06 standard / 0.02 advanced) are a **modelling assumption** — Malta has no national heating-retrofit programme and the limestone-masonry stock is essentially unrefurbished for heating purposes. Immaterial to the result given the negligible heat demand.

**Resulting blend factor:** 0.92 × 1.00 + 0.06 × 0.70 + 0.02 × 0.50 = **0.972**.

### 2.5 DHW intensity
DHW added per building from the `cy_intensities.csv` DHW column (warm-climate values, ~16 SFH / ~14 MFH).

### 2.6 Non-residential intensity
Estimate, 120 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.7 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **0.73** | 2015 | verified | Sum across all MT NUTS3 rows — the smallest in the study. |
| Odyssee-Mure | 0.5 | 2023 | estimate | Malta residential space heating is marginal and AC-delivered. |
| EU BSO | 0.6 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

Malta's heating demand is negligible; percentage reconciliation against the 0.73 TWh baseline is low-information and should be interpreted with that caveat.

---

## 3. NUTS3 spatial join
Malta has 2 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. MT00 single NUTS2 partition; 2 NUTS3 codes (stable NUTS 2016/2021).
2. HDD MT = 477.03, HDD CY = 661.56 (Eurostat `nrg_chdd_a` 2018–2022); `climate_multiplier = 0.7210`.
3. Hotmaps MT total = 0.73 TWh — the smallest in the study.
4. Config validates; the full input chain loads cleanly (unknown-cohort fallback SFH ≈ 72 kWh/m²/yr).

### Still needs verification
1. **EUBUCCO Malta data availability** — v0.1 excluded Malta for licensing reasons; if v0.2 also lacks Malta, the bottom-up build cannot run and the model falls back to top-down Hotmaps demand.
2. **TABULA intensities** (`cy_intensities.csv`) — research-synthesised estimates for a warm-Mediterranean country; verify against the TABULA WebTool (country CY).
3. **Cyprus 3-period typology** — several of the model's 6 cohorts carry identical values.
4. **Retrofit factors** (0.70/0.50) and **DHW** — provisional; immaterial given negligible heat demand.
5. **Non-residential intensity** (120) — estimate; contributes 0 TWh.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Malta built as a build-group-2 country, a TABULA **proxy** country using Cyprus as the proxy. Created `mt.yaml`, `cy_intensities.csv` (research-synthesised pending WebTool verification), `eu_bso/mt_intensity.csv`, `mt_national/mt_climate_retrofit.csv`. climate_multiplier 0.7210 from Eurostat HDD. Flagged the EUBUCCO Malta data-availability risk and the negligible-heat-demand caveat. | Ali / Claude |
| 2026-05-19 | First G2 Colab run unexpectedly succeeded at script 01 — EUBUCCO v0.2 DOES carry Malta building data (143k buildings in the MT00 partition), contrary to the v0.1 licensing-exclusion that the YAML had documented as a risk. Script 02 also succeeded. Script 03 then failed: `pd.read_csv` raised on `mt_climate_retrofit.csv` lines 19-20, which had unquoted commas inside `(Cyprus TABULA standard refurbishment (proxy, provisional))`. Same CSV-quoting bug as HR/CY/PT. Fixed in commit 07c90e4 by wrapping the source field in double quotes. | Ali / Claude |
| 2026-05-20 | Second G2 Colab run completed: bottom-up 2.42 TWh vs Hotmaps 0.73 TWh = **+230.8 % (INVESTIGATE band by percentage, low-information case in absolute terms)**. Malta is the second-smallest residential heat demand in the EU (after Cyprus); the percentage gap is inflated by Hotmaps being a small denominator. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **2.42** | **57.9** |
| Hotmaps 2015 baseline | 0.73 | 17.5 |
| EU BSO 2022 weighted-avg implied total | 2.60 | 62.4 |
| Odyssee-Mure 2023 (final energy, definitional gap vs Hotmaps useful demand) | 0.50 | 12.0 |

**Verdict:** Bottom-up vs Hotmaps = **+230.8 %** (INVESTIGATE — but a **low-information case** in absolute terms).

Malta's percentage verdict is **structurally misleading**:

1. **Hotmaps itself is tiny (0.73 TWh).** A bottom-up over-statement of ~1.7 TWh is large in percentage terms but small in absolute terms. The Maltese residential heat demand is the lowest in the EU; the percentage gap is fundamentally a denominator issue.
2. **Malta's residential heating is dominated by reverse-cycle air-conditioning electricity use, not heat-as-energy-service.** ~80 % of Maltese households use AC for both cooling and the limited winter heating they need; there is no piped gas grid and no district heating. The TABULA/EUBUCCO bottom-up methodology assumes a heated reference-condition framing that doesn't match Maltese household practice.
3. **EUBUCCO Malta data is now confirmed available** (143k buildings in the MT00 partition), contradicting the v0.1 licensing-exclusion concern that the YAML had originally flagged.

Malta uses the Cyprus TABULA as proxy (climate_multiplier 0.7210, scaling CY values down to Malta's even milder HDD 477 vs CY 661). The `cy_intensities.csv` file itself is research-synthesised at ±20-30 % per the file header.

**For any Malta-specific analysis, Hotmaps 2015 (0.73 TWh) remains the recommended top-down benchmark.** The model output (2.42 TWh) is reportable as a methodology-finding bottom-up, but the absolute residential heat demand of Malta is sufficiently small that the percentage discrepancy is not a load-bearing issue for the overall EU model. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).

---

## 7. Academic refinement path (research 2026-05-20)

**Malta is a structural low-information case; no numerical refinement is recommended.** The percentage gap is inflated by the small Hotmaps denominator (0.73 TWh); the absolute over-statement of ~1.7 TWh would look small in any country with a non-negligible heating market. Maltese residential heating is **~80 % reverse-cycle AC** per the NECP 2030 (EWA Dec 2019, updated Dec 2024) — no piped gas grid, no district heating. The TABULA "useful demand" framing assumes a steady-state water-radiator regime; the Maltese RCAC regime is fundamentally room-and-occupancy-modulated. Switching the proxy to IT Middle-zone with a low-comfort coefficient is no improvement; the honest fix is a Malta-direct comfort-regime model parameterized from NECP RCAC penetration data.

Three documentation refinements (not numerical fixes):
1. Acknowledge Malta as a low-information case in the OIES paper. Hotmaps top-down (0.73 TWh) is the recommended demand input.
2. Replace the CY-derived cohort distribution with **NSO Malta Census 2021** construction-period histogram (297,304 dwellings; 50 % built/reconstructed post-2000; flat/penthouse 48.4 %, maisonette 23.9 %, terraced 22.7 %).
3. Verify EUBUCCO v0.2 MT00 inclusion — the G2 Colab run confirmed 143k Maltese buildings classified, contradicting the v0.1 licensing-exclusion that the YAML originally flagged as a risk; the NSO 297k-dwellings figure suggests MT00 may be missing ~50 % of stock.

Full per-country ranked refinement priorities are in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Mediterranean proxy cluster section.

## Applied (2026-05-21): comfort_regime deflator — `comfort_regime.deflator = 0.22`

The "honest fix is a Malta-direct comfort-regime model" noted above **was applied this session**. A `comfort_regime` deflator of **0.22** was added to `mt.yaml` (multiplies the space-heating component only; DHW unchanged), derived by scaling the CY-proxy deflator (0.30) by the MT/CY space-heating-share ratio of household final energy (Eurostat `nrg_d_hhq`: MT ~20 % vs CY 33.5 %) ≈ 0.60 → ~0.18, bounded at the CY-analogue 0.25; applied value **0.22**. Grounds: Malta NECP 2030 / EWA (~80 % reverse-cycle AC heating); the mildest EU climate (HDD 477).

**Result:** bottom-up drops from +231 % to **+36 % vs Hotmaps** — still INV, but the absolute gap is ~0.27 TWh on a 0.73 TWh denominator (noise floor). MT is **NOT corrected on the area side**: EUBUCCO MT area (~42 Mm²) ≈ NSO 2021 (~40 Mm²), so no occupancy/area correction applies — the over-statement is purely the heating regime. MT remains a documented **structural low-information case**; the recommended headline demand input for the OIES paper stays the Hotmaps top-down 0.73 TWh.
