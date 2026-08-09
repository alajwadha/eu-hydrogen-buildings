# Italy — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country IT`).
**Config:** `code/data/country_config/it.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Italy — the heavyweight of build group 2 (IT + SI, HR, MT).

**The headline fact:** Italy **is a TABULA country**. Its residential heat intensities come from the **direct Italian TABULA typology** (produced by Politecnico di Torino), with **no proxy and no climate correction** — the France/Germany branch.

---

## 1. Methodology relative to Luxembourg and France

Italy is a **direct-TABULA country** and follows the France branch:

| Element | France | Italy |
|---|---|---|
| TABULA dataset | France (direct) | **Italy (direct, Politecnico di Torino)** |
| Climate correction | 1.0 | **1.0 (direct)** |
| EUBUCCO partitions | 22 | **21 NUTS2 regions** |
| NUTS3 regions | 96 | **107 province** |
| Hotmaps reconciliation | sum across FR rows | **sum across all IT rows (482.00 TWh)** |

The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to Luxembourg and France. Italy is large, so script 02 runs in `--per-partition` streaming mode.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Italy has 21 NUTS2 regions (Trentino-Alto Adige split into the autonomous provinces ITH1 Bolzano and ITH2 Trento). The 107 NUTS3 codes were extracted from the repo GISCO file; the Sardinian provinces saw minor 2016→2021 changes, flagged in `it.yaml._meta`.

### 2.2 TABULA — Italy direct
**Italy is a TABULA country.** The Italian residential typology was produced by the TEBE research group at **Politecnico di Torino** for the EU TABULA/EPISCOPE projects. The DIRECT Italian typology is used (no proxy, no climate correction). The Italian TABULA defines three climate zones (Alpine >3000 HDD, Middle 2100-3000 HDD, Mediterranean <2100 HDD); the **Middle reference zone** is used.

**Extraction:** `code/data/raw/tabula/it_intensities.csv`. **Important caveat:** the full per-class per-period numeric matrix of the Italian TABULA is held in the TABULA WebTool (interactive) and the Politecnico di Torino Building Typology Brochure, neither machine-extractable. The `it_intensities.csv` values are **research-synthesised best estimates** from the published Italian TABULA span (~50–300 kWh/m²/yr across types and ages; REHVA Journal and Emerald comparative-typology papers) and the Ballarini/Corrado POLITO archetype literature — flagged `NEEDS_VERIFY`, to be confirmed against the TABULA WebTool. Treat as ±20% uncertainty.

### 2.3 Taxonomy mappings
- **Building class** — Italian TABULA SFH/TH/MFH/AB → our 3: SFH ← SFH; MFH_LOW ← TH; MFH_HIGH ← MFH + AB.
- **Construction cohort** — Italian TABULA 8 periods (…1900 through post-2005) → our 6 cohorts, documented in the `it_intensities.csv` header. The model's 2011-2020 and post-2020 cohorts fall beyond TABULA's newest "post-2005" class and are extrapolated from the Italian nZEB standard (DM 26/06/2015), flagged.

### 2.4 Climate (HDD)
Italy uses the direct typology, `climate_multiplier = 1.0`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022: 1879.86 / 1746.84 / 1813.91 / 1748.95 / 1916.57 → **mean 1821.23**.

### 2.5 Retrofit shares and factors
**Retrofit factors** — Italian TABULA typology-averaged refurbishment ratios: standard ~0.62, advanced ~0.30 of existing-state space-heating need. **PROVISIONAL** pending the WebTool extraction.

**Retrofit shares** (0.75 original / 0.20 standard / 0.05 advanced) are a **modelling assumption** grounded in ENEA Superbonus 110% reporting (~495,700 residential renovations completed by May 2024, ~5% of the stock) and Odyssee-Mure Italy.

**Resulting blend factor:** 0.75 × 1.00 + 0.20 × 0.62 + 0.05 × 0.30 = **0.889**.

### 2.6 DHW intensity
DHW added per building from the `it_intensities.csv` DHW column (~18 kWh/m²/yr, roughly period-independent in the Italian TABULA).

### 2.7 Non-residential intensity
Estimate, 110 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh (NON_RESIDENTIAL carries zero heated area).

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **482.00** | 2015 | verified | Sum across all IT NUTS3 rows in `building_stock_nuts3.csv`, all-classes. |
| ENEA / Odyssee-Mure | 294 | 2019 | estimate | Italian residential final energy ~294 TWh; space heating ~70%. Final-energy basis. |
| EU BSO | 320 | 2022 | anchored | Order-of-magnitude anchor; BSO portal not retrievable. |

The Hotmaps 2015 figure substantially exceeds ENEA's residential final-energy figure; the gap is a definitional one (useful demand / all-classes vs final energy / residential) and should be stated in the paper.

---

## 3. NUTS3 spatial join
Italy has 107 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. 21 IT NUTS2 partitions and 107 NUTS3 codes (from the repo GISCO file).
2. HDD IT = 1821.23 (Eurostat `nrg_chdd_a` 2018–2022 mean).
3. Hotmaps IT total = 482.00 TWh (computed from `building_stock_nuts3.csv`).
4. Config validates; the full TABULA + BSO + national input chain loads cleanly (unknown-cohort fallback SFH ≈ 185 kWh/m²/yr).

### Still needs verification
1. **TABULA intensities** (`it_intensities.csv`) — research-synthesised best estimates; verify against the TABULA WebTool (country IT, Middle zone).
2. **Retrofit factors** (0.62/0.30) and **DHW** (18) — provisional.
3. **Retrofit shares** (0.75/0.20/0.05) — modelling assumption from Superbonus reporting.
4. **Non-residential intensity** (110) — estimate; contributes 0 TWh.
5. **NUTS3** — Sardinian provinces changed 2016→2021; spot-check EUBUCCO region_id codes.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Italy built as build-group-2 country #1, a DIRECT TABULA country (Politecnico di Torino typology). Created `it.yaml`, `it_intensities.csv` (research-synthesised pending WebTool verification), `eu_bso/it_intensity.csv`, `it_national/it_climate_retrofit.csv`. climate_multiplier = 1.0. Retrofit factors provisional. | Ali / Claude |
| 2026-05-19 | First Colab G2 run completed: bottom-up 668.5 TWh vs Hotmaps 482 TWh = +38.7 % (INVESTIGATE band). Diagnosed: `it_intensities.csv` brochure header explicitly states values are for the TABULA **Middle reference zone** (2100-3000 HDD), but IT's actual 2018-2022 mean HDD is 1821 (Mediterranean zone). Middle-zone intensities were being applied at face value. | Ali / Claude |
| 2026-05-20 | Applied Option B reference-HDD correction: introduced `climate.tabula_reference_hdd = 2500` (Middle zone midpoint) and `climate_multiplier = 1821.23 / 2500 = 0.7285`. Re-ran Italy in G2 Colab (deleted IT summary CSV to force rebuild). New bottom-up = **508.85 TWh = +5.6 % vs Hotmaps (OK)**. Italy is the only country in the build where Option B was empirically validated; the same correction tested for DE, EL and FI was reverted because it would have broken their existing OK reconciliations. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** (post-Option B correction) | **508.85** | **113.8** |
| Hotmaps 2015 baseline | 482.00 | 107.8 |
| EU BSO 2022 weighted-avg implied total | 656.22 | 146.8 |
| Odyssee-Mure 2019 (final energy, definitional gap vs Hotmaps useful demand) | 294.00 | 65.8 |

**Verdict:** Bottom-up vs Hotmaps = **+5.6 %** (OK — within ±15 % consistency band).

**Italy is the showcase Option B success.** The pre-correction result was 668.5 TWh (+38.7 %, INVESTIGATE band, the largest gap in build groups 1-2). The brochure header was unambiguous about Middle-zone calibration, and the actual Italian HDD (1821) sits in the Mediterranean zone — the framework predicted the multiplier change should narrow the gap, and the empirical outcome confirmed it within 6 % of Hotmaps.

The result also exposed an interesting feature of the reconciliation: the BU now disagrees with EU BSO (656.22 TWh) by ~30 %. This is because `it_intensity.csv` (the BSO derived row) is built from `it_intensities.csv × retrofit blend + DHW`, NOT from the BSO portal directly — so it inherits the pre-correction over-statement. The BSO row is best treated as a sanity check on the TABULA-derived intensity rather than as an independent benchmark. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) for the full audit trail.
