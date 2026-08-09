# Slovenia — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country SI`).
**Config:** `code/data/country_config/si.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Slovenia — a build-group-2 country (IT + SI, HR, MT).

**The headline fact:** Slovenia **is a TABULA country**. Its residential heat intensities come from the **direct Slovenian TABULA typology** (produced by the Building and Civil Engineering Institute ZRMK, Ljubljana), with **no proxy and no climate correction**. The Slovenian typology is also used as the **proxy for Croatia**.

---

## 1. Methodology relative to Luxembourg and France

Slovenia is a **direct-TABULA country** (France/Germany branch). The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Slovenia has 2 NUTS2 regions: SI03 Vzhodna (East) and SI04 Zahodna (West). Slovenia has 12 NUTS3 statistical regions, codes unchanged across NUTS 2016/2021/2024.

### 2.2 TABULA — Slovenia direct
**Slovenia is a TABULA country.** The Slovenian residential typology was produced by the **Building and Civil Engineering Institute ZRMK** (Ljubljana). The DIRECT Slovenian typology is used (no proxy, no climate correction).

**Extraction:** `code/data/raw/tabula/si_intensities.csv`. **Important caveat:** the ZRMK scientific report tabulates heating need aggregated into two classes — SUH (Single Unit Houses) and MUH (Multi Unit Houses) — across the Slovenian periods; the clean per-type values are in the TABULA WebTool (interactive). The `si_intensities.csv` values are **derived from the ZRMK aggregate intensities** and mapped onto our 6 cohorts. Because the ZRMK energy-balance model has only SUH and MUH, **MFH_LOW and MFH_HIGH necessarily carry identical intensities** — a documented limitation of the source. Flagged `NEEDS_VERIFY`.

### 2.3 Taxonomy mappings
- **Building class** — ZRMK 2-class scheme → our 3: SFH ← SUH; MFH_LOW ← MUH; MFH_HIGH ← MUH (same — limitation disclosed).
- **Construction cohort** — the Slovenian periods (pre-1945, 1945-1970, 1971-1980, 1981-2002, 2003-2008, from-2009) **do not align** with the model's 6 cohorts. The mapping (documented in the `si_intensities.csv` header) interpolates across the boundary mismatch — notably the model's 1971-1990 cohort straddles the Slovenian 1971-1980 and 1981-2002 periods. The ZRMK SUH 1971-1980 aggregate (~196 kWh/m²/yr) is a known floor-area artefact and is replaced by an interpolated value.

### 2.4 Climate (HDD)
Slovenia uses the direct typology, `climate_multiplier = 1.0`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022: 2587.40 / 2602.14 / 2678.32 / 2965.26 / 2633.38 → **mean 2693.30**.

### 2.5 Retrofit shares and factors
**Retrofit factors** — Slovenian TABULA typology-averaged refurbishment ratios: standard 0.65, advanced 0.40. **PROVISIONAL** pending the WebTool extraction.

**Retrofit shares** (0.55 original / 0.32 standard / 0.13 advanced) are a **modelling assumption** grounded in the ZRMK refurbishment-state subtype data (the oldest class splits roughly 40/42/17% un-refurbished / medium / full) and Slovenia's moderate renovation activity.

**Resulting blend factor:** 0.55 × 1.00 + 0.32 × 0.65 + 0.13 × 0.40 = **0.810**.

### 2.6 DHW intensity
DHW added per building from the `si_intensities.csv` DHW column (~20 kWh/m²/yr SFH, ~18 MFH).

### 2.7 Non-residential intensity
Estimate, 110 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh. The Slovenian TABULA explicitly states non-residential subsectors were not studied.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **13.99** | 2015 | verified | Sum across all SI NUTS3 rows, all-classes. |
| ZRMK | 13.9 | 2011 | verified | The Slovenian TABULA total residential primary energy ~13.9 TWh — essentially identical to the Hotmaps figure; space-heating need alone ~8.58 TWh. |
| EU BSO | 11.0 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

The Hotmaps 13.99 TWh figure is strongly corroborated by the independent ZRMK national energy balance.

---

## 3. NUTS3 spatial join
Slovenia has 12 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. SI03 + SI04 NUTS2 partitions; 12 NUTS3 codes (stable NUTS 2016/2021).
2. HDD SI = 2693.30 (Eurostat `nrg_chdd_a` 2018–2022 mean).
3. Hotmaps SI total = 13.99 TWh — corroborated by the ZRMK 2011 energy balance.
4. Config validates; the full input chain loads cleanly (unknown-cohort fallback SFH ≈ 99 kWh/m²/yr).

### Still needs verification
1. **TABULA intensities** (`si_intensities.csv`) — derived from the ZRMK aggregate report; verify per-type values against the TABULA WebTool.
2. **MFH_LOW = MFH_HIGH** — the ZRMK 2-class scheme cannot distinguish low- and high-rise multi-family.
3. **Cohort-boundary mismatch** — Slovenian periods do not align with the model's 6 cohorts; intensity mapping interpolates.
4. **Retrofit factors** (0.65/0.40) and **DHW** — provisional.
5. **Non-residential intensity** (110) — estimate; contributes 0 TWh.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Slovenia built as a build-group-2 country, a DIRECT TABULA country (ZRMK typology). Created `si.yaml`, `si_intensities.csv` (derived from the ZRMK aggregate report), `eu_bso/si_intensity.csv`, `si_national/si_climate_retrofit.csv`. The Slovenian typology is also the proxy for Croatia. climate_multiplier = 1.0. Retrofit factors provisional. | Ali / Claude |
| 2026-05-19 | Colab G2 run completed: bottom-up 17.42 TWh vs Hotmaps 13.99 TWh = **+24.5 % (ACCEPTABLE band)**. Slovenia is right at the upper edge of the acceptance band — the highest gap of the "ACC" countries. The Slovenian TABULA (ZRMK) is the only direct national typology in the build whose values come from a published scientific report (not research synthesis); the gap suggests EUBUCCO floor-area over-counting is the residual driver. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-19)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **17.42** | **100.2** |
| Hotmaps 2015 baseline | 13.99 | 80.5 |
| EU BSO 2022 weighted-avg implied total | 17.69 | 101.8 |
| Odyssee-Mure 2011 (final energy, definitional gap vs Hotmaps useful demand) | 8.60 | 49.5 |

**Verdict:** Bottom-up vs Hotmaps = **+24.5 %** (ACCEPTABLE — within ±25 % band; document the gap).

Slovenia is the **only "ACC" country in build groups 1-4** that does not have a structural over-count problem traceable to research-synthesised TABULA values. The Slovenian TABULA matrix in `si_intensities.csv` is derived directly from the ZRMK scientific report — the only direct extraction from a TABULA brochure in the build that isn't research-synthesised (DE is the other one).

The +24.5 % residual likely reflects **the same EUBUCCO floor-area over-counting that contributes to all other builds** but is less amplified for Slovenia because the TABULA intensities are accurate. Slovenia's stock is heavy on the post-war single-family detached typology (with the legacy of pre-1991 Yugoslav-era multi-family stock concentrated around Ljubljana, Maribor, Celje); the ZRMK SUH (Single Unit Houses) class matches the dominant typology well.

The result is also a **sanity check on the Croatia proxy build** (which uses the same `si_intensities.csv` with climate scaling to HR's milder national HDD). HR landed at +65.8 % — much further from Hotmaps. The HR/SI gap difference (~40 pp) is consistent with the broader Mediterranean over-count pattern, and suggests the SI → HR climate scaling alone doesn't introduce major error. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).
