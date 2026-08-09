# Latvia — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country LV`).
**Config:** `code/data/country_config/lv.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Latvia — one of the three Baltic states in build group 1 (DE + EE, LV, LT).

**The headline fact:** Latvia is **not a TABULA country**. Its residential heat intensities are **Poland-derived** — extracted from the Polish TABULA typology and climate-corrected by the Latvia/Poland heating-degree-day ratio. This is the same proxy methodology Luxembourg uses with Belgium and Finland with Sweden.

---

## 1. Methodology relative to Luxembourg and France

Latvia is a **proxy country**, following the Luxembourg branch (proxy + climate correction):

| Element | Luxembourg | Latvia |
|---|---|---|
| TABULA dataset | Belgium (proxy) | **Poland (proxy)** |
| Climate correction | HDD_LU/HDD_BE = 1.112 | HDD_LV/HDD_PL = **1.2088** |
| Retrofit factors source | TABULA Belgium | **TABULA Poland** |
| EUBUCCO partitions | 1 (LU00) | 1 (LV00) |
| NUTS3 regions | 1 (LU000) | 6 |
| Hotmaps reconciliation | single LU000 row | sum across all LV rows (18.22 TWh) |

The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to Luxembourg.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Latvia is a single NUTS2 region, **LV00**. Latvia has 6 NUTS3 regions (planning regions, LV003/LV005/LV006/LV007/LV008/LV009); the codes are unchanged between NUTS 2016 and 2021 (the 2021 revision adjusted boundaries under Latvia's administrative-territorial reform but kept the codes).

### 2.2 TABULA — Poland as proxy

**Latvia has no national TABULA typology.** Poland is chosen as the proxy because:
1. Latvia's residential stock is dominated by Soviet-era prefabricated large-panel concrete apartment blocks (serial types 103, 104, 119, 467, 602) plus older Riga masonry and rural timber houses. Poland's TABULA typology explicitly carries the Soviet/Comecon-era large-panel ("wielka płyta") apartment class — the same industrialised construction lineage as the Latvian serial panel blocks.
2. Shared post-war central-planning construction norms.
3. Poland is the closest panel-bearing TABULA country; using it for all three Baltic states keeps the methodology consistent across the group.

**Primary source:** Polish TABULA Scientific Report (NAPE). Extraction: `code/data/raw/tabula/pl_intensities.csv` — the header documents the EK→net-space-heating derivation and the class/cohort mappings.

### 2.3 Climate (HDD)
`climate_multiplier = HDD_LV / HDD_PL`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022:
- Latvia: 3870.56 / 3633.98 / 3413.39 / 4151.13 / 4022.19 → **mean 3818.3**
- Poland: → **mean 3158.7**
- `climate_multiplier = 3818.3 / 3158.7 = 1.2088`.

### 2.4 Retrofit shares and factors
**Retrofit factors** are the Poland TABULA typology-averaged refurbishment ratios: **standard 0.63**, **advanced 0.50**.

**Retrofit shares** (0.90 original / 0.07 standard / 0.03 advanced) are a **modelling assumption**. Latvia's renovation pace is the lowest of the Baltics: only ~4 % of residential buildings have been deeply renovated (~1,900 of ~39,000 multi-apartment buildings); the Latvian State Audit Office has flagged the renovation rate as "critically low". The standard/advanced sub-split is an assumption — flagged.

**Resulting blend factor:** 0.90 × 1.00 + 0.07 × 0.63 + 0.03 × 0.50 = **0.9591**.

### 2.5 DHW intensity
DHW is added per building from the `pl_intensities.csv` DHW column (Poland-proxy values).

### 2.6 Non-residential intensity
Estimate, 160 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh (NON_RESIDENTIAL carries zero heated area).

### 2.7 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **18.22** | 2015 | verified | Sum across all LV NUTS3 rows in `building_stock_nuts3.csv`, all-classes. |
| Odyssee-Mure | 13.0 | 2023 | estimate | LV residential space heating; intensity ~141 kWh/m²/yr (2023). Final-energy basis. |
| EU BSO | 14.0 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

---

## 3. NUTS3 spatial join
Latvia has 6 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. LV00 single NUTS2 partition; 6 NUTS3 codes (stable NUTS 2016/2021).
2. HDD LV = 3818.3, HDD PL = 3158.7 (Eurostat `nrg_chdd_a` 2018–2022); `climate_multiplier = 1.2088`.
3. Poland TABULA intensities — `code/data/raw/tabula/pl_intensities.csv`.
4. Retrofit factors 0.63 / 0.50 — Polish TABULA typology-averaged refurbishment ratios.
5. Hotmaps LV total = 18.22 TWh — computed from `building_stock_nuts3.csv`.
6. Config validates; full input chain loads cleanly (unknown-cohort fallback SFH ≈ 217 kWh/m²/yr).

### Still needs verification
1. **Retrofit shares** (0.90/0.07/0.03) — modelling assumption; no published three-state envelope distribution for Latvia.
2. **Non-residential intensity** (160) — estimate; contributes 0 TWh.
3. **EU BSO benchmark** — anchored estimate, BSO portal not retrievable.
4. **Poland TABULA net-SH values** — derived from the Polish report's EK figures, ±15–20 % uncertainty.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Latvia built as a build-group-1 country, a TABULA **proxy** country using Poland as the proxy. Created `lv.yaml`, `eu_bso/lv_intensity.csv`, `lv_national/lv_climate_retrofit.csv`; shares `pl_intensities.csv` with Estonia and Lithuania. climate_multiplier 1.2088 from Eurostat HDD. Retrofit factors 0.63/0.50 from the Polish TABULA; retrofit shares a modelling assumption from ALTUM renovation reporting. | Ali / Claude |
| 2026-05-19 | Colab G1 run completed: bottom-up 21.92 TWh vs Hotmaps 18.22 TWh = **+20.0 % (ACCEPTABLE band)**. Latvia is the only Baltic country to land inside ±25 %, despite using the same PL proxy methodology as EE (+78 %) and LT (+124 %). The smaller gap may reflect Latvia's heavy reliance on district heating (concrete-panel apartment blocks in Riga / Daugavpils) which closely matches the Polish wielka płyta archetype that drives the proxy. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-19)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **21.92** | **208.9** |
| Hotmaps 2015 baseline | 18.22 | 173.7 |
| EU BSO 2022 weighted-avg implied total | 21.69 | 206.8 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 13.00 | 123.9 |

**Verdict:** Bottom-up vs Hotmaps = **+20.0 %** (ACCEPTABLE — within ±25 % band; document the gap).

Latvia is **the only Baltic country to land inside the ±25 % acceptance band** — quietly, the most successful PL-proxy outcome in the build. The +20 % gap is moderate compared to Estonia (+78 %) and Lithuania (+124 %), despite all three using the same `pl_intensities.csv` and similar climate multipliers (LV 1.2088 vs EE 1.2625 vs LT 1.1522).

The difference is likely structural: Latvia's residential stock is heavily concentrated in concrete-panel apartment blocks (Soviet-era serii 119, 467, 318 buildings), heated mostly via district heating in Riga and Daugavpils. This closely matches the Polish wielka płyta archetype that drives the proxy, more than Estonia's mixed detached-wooden + panel stock or Lithuania's heterogeneous mix. The proxy methodology is most accurate where the proxy country and the target country share dominant building archetypes.

**Latvia's result is the strongest evidence that the PL-Baltic proxy framework can work** when the building stock matches. It also implies that EE and LT could be improved by replacing the all-classes PL proxy with a class-mix-weighted approach (EE wooden SFH replaced by a Finnish SFH proxy, retaining PL for panel blocks). See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).
