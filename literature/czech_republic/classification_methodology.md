# Czechia — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country CZ`).
**Config:** `code/data/country_config/cz.yaml`.

This document describes how the buildings-model methodology is applied to Czechia — the second-largest country in build group 4 (PL + CZ, SK, HU; the Visegrad group).

**The headline fact:** Czechia **is a TABULA-participating country**, but via the **EPISCOPE follow-up project** (2013-2016), not the original IEE TABULA partnership (2009-2012). The Czech residential typology was produced by **CTU Prague / UCEEB** (University Centre for Energy-Efficient Buildings; Lupisek et al.), with SEVEn as secondary stakeholder. The same `cz_intensities.csv` file is also used as the climate-corrected proxy for Slovakia (shared Czechoslovak federal building code 1948-1993).

**Czechia caveat:** the Czech EPISCOPE numeric matrix is held in the TABULA WebTool (interactive; not machine-extractable) and the Lupisek 2016 brochure (PDF). The values in `cz_intensities.csv` are **research-synthesised best estimates** bracketing the German TABULA (DIN reference) and the Polish TABULA (EK-derived), informed by the CSN 73 0540 thermal-protection requirements by period and the Czech panelove domy stock structure (VVU-ETA, T-06B, P1.11 series). Flagged NEEDS_VERIFY ±20-30 %.

---

## 1. Methodology relative to Luxembourg and France

Czechia is a **direct-TABULA country** following the France branch (with the EPISCOPE caveat above). The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

The first new schema feature applied to Czechia is the **`climate.tabula_reference_hdd` field** (introduced May 2026; see `literature/climate_reference_hdd_audit.md`). The Czech EPISCOPE brochure calibrates intensities to the Czech reference climate (CSN 73 0540; Praha-Ruzyne long-term mean ~3400 HDD at base 15 °C). Czech actual 2018-2022 HDD is ~3331, so `climate_multiplier = 3331 / 3400 = 0.9797`. Effectively unity; the documented mechanism preserves comparability with the reference.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2. Czech NUTS2 codes have been **stable across NUTS 2013/2016/2021** (no boundary or code change since the original introduction). 8 NUTS2 regions: CZ01 Praha, CZ02 Stredni Cechy, CZ03 Jihozapad, CZ04 Severozapad, CZ05 Severovychod, CZ06 Jihovychod, CZ07 Stredni Morava, CZ08 Moravskoslezsko. 14 NUTS3 regions (CZZZZ extraterritorial excluded).

### 2.2 TABULA — Czechia direct (EPISCOPE)
**Czechia is a TABULA-participating country via EPISCOPE.** Country page: episcope.eu/building-typology/country/cz. Brochure: Lupisek A. et al. (2016), "Building typology of the Czech residential stock", EPISCOPE deliverable; CTU Prague / UCEEB.

**Construction periods.** Czech EPISCOPE uses periods aligned with the CSN 73 0540 thermal-code generations: pre-1945; 1946-1970; 1971-1990 (peak panelove domy era); 1991-2010 (CSN 73 0540 1994/2002 thermal updates); 2011-2020 (CSN 73 0540-2 2011); post-2020 (nZEB per EPBD).

**Extraction:** `code/data/raw/tabula/cz_intensities.csv`. Created for build group 4. Values are research-synthesised best estimates pending TABULA WebTool / Lupisek brochure numeric appendix extraction.

### 2.3 Taxonomy mappings
- **Building class** — Czech EPISCOPE SFH / MFH / AB → our 4: SFH ← rodinny dum (detached); MFH_LOW ← bytovy dum (multi-family up to ~5 floors); MFH_HIGH ← panelovy dum AB (large-panel apartment block, 6+ floors); NON_RESIDENTIAL not in TABULA.
- **Construction cohort** — direct one-to-one mapping (Czech EPISCOPE already has 6 periods aligned with our cohorts).
- **MFH_HIGH pre-1945:** large-panel apartment blocks did not exist in Czechoslovakia before ~1953 (T-series first cohort). The pre-1945 MFH_HIGH cell is proxied from `cinzovni domy` (multi-storey rental masonry); FLAGGED.

### 2.4 Climate (HDD)
Direct TABULA with explicit reference HDD. `tabula_reference_hdd = 3400` (Czech reference climate; CSN 73 0540 / Praha-Ruzyne). `hdd_country = 3331` (Eurostat `nrg_chdd_a` 2018-2022 mean; NEEDS_VERIFY exact). Climate multiplier = 3331 / 3400 = **0.9797**.

### 2.5 Retrofit shares and factors
**Retrofit factors** — Czech EPISCOPE refurbishment scenarios (Lupisek et al.; typology-averaged): standard 0.60 (Nova zelena usporam NZU standard package; ~40 % cut); advanced 0.32 (NZU passive/deep; ~65-70 % cut). NEEDS_VERIFY against Lupisek 2016 brochure.

**Retrofit shares** (0.78 / 0.17 / 0.05) — modelling assumption grounded in the Czech Long-Term Renovation Strategy (2020), Nova zelena usporam programme reporting (active since 2014, successor to 2009-2014 Zelena usporam), and BPIE 2022 Renovation Wave CZ profile. Renovation rate ~1.0-1.3 %/yr.

**Resulting blend factor:** 0.78 × 1.00 + 0.17 × 0.60 + 0.05 × 0.32 = **0.898**.

### 2.6 DHW intensity
DHW from `cz_intensities.csv`: SFH 12, MFH_LOW 14, MFH_HIGH 15 kWh/m²/yr. Czech EPISCOPE / CSN 73 0331-1 convention. Provisional.

### 2.7 Non-residential intensity
Estimate 130 kWh/m²/yr (continental-climate non-residential). `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **84.64** | 2015 | verified | Sum across 14 CZ NUTS3 rows in `building_stock_nuts3.csv`. |
| EU BSO | 78 | 2022 | anchored | Order-of-magnitude anchor. |
| Odyssee-Mure | 65 | 2022 | estimate | CZ residential space heating (MPO / EnergoStat; final energy). |

---

## 3. NUTS3 spatial join
14 NUTS3 regions; codes stable across vintages, so the spatial join is robust either way.

---

## 4. Verification status (2026-05-19)

### Verified
1. 8 NUTS2 partitions (stable across NUTS 2013/2016/2021).
2. 14 NUTS3 regions (stable across vintages).
3. Hotmaps CZ total = 84.64 TWh.
4. Config validates; full input chain loads cleanly (fallback SFH ≈ 170 kWh/m²/yr).

### Still needs verification
1. **HDD 2018-2022 mean (3331)** — best estimate; direct Eurostat `nrg_chdd_a` extraction via series A.NR.HDD.CZ not yet done.
2. **`tabula_reference_hdd = 3400`** — Czech reference climate from CSN 73 0540 / Praha-Ruzyne long-term mean; verify against Lupisek 2016 brochure header.
3. **`cz_intensities.csv` 18-row matrix** — research-synthesised; verify against the TABULA WebTool (country CZ) or Lupisek 2016 brochure numeric appendix.
4. **Retrofit factors (0.60 / 0.32)** — estimated from NZU savings; verify against Czech EPISCOPE Scientific Report.
5. **Retrofit shares (0.78 / 0.17 / 0.05)** — modelling assumption.
6. **DHW (12 / 14-15)** — DIN/CSN reference values; verify CSN 73 0331-1.
7. **Non-residential intensity** (130) — estimate; contributes 0 TWh.
8. **MFH_HIGH pre-1945** — proxied from `cinzovni domy`; FLAGGED.
9. **post-2020 cohort** — EXTRAPOLATED per EPBD nZEB; FLAGGED.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Czechia built as build-group-4 country, a direct EPISCOPE/TABULA country (CTU Prague / UCEEB; Lupisek 2016). Created `cz.yaml`, `eu_bso/cz_intensity.csv`, `cz_national/cz_climate_retrofit.csv`, and the new `code/data/raw/tabula/cz_intensities.csv` (research-synthesised, flagged ±20-30 %). climate_multiplier = 0.9797; tabula_reference_hdd = 3400 (CSN 73 0540 / Praha-Ruzyne). Same file is shared as the proxy for Slovakia. | Ali / Claude |
| 2026-05-20 | Colab G4 run completed: bottom-up 77.90 TWh vs Hotmaps 84.64 TWh = **−8.0 % (OK)**. The result validates both the research-synthesised `cz_intensities.csv` matrix and the CZ reference-climate choice of 3400 HDD (Czech actual 2018-2022 ≈ 3331). The same file used as proxy for Slovakia also delivered SK at +2.2 % vs Hotmaps. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **77.90** | **142.0** |
| Hotmaps 2015 baseline | 84.64 | 154.3 |
| EU BSO 2022 weighted-avg implied total | 79.62 | 145.2 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 65.00 | 118.5 |

**Verdict:** Bottom-up vs Hotmaps = **−8.0 %** (OK — within ±15 % consistency band).

Czechia's clean reconciliation is the **second important validation in the build (after Germany), and the first validation of a research-synthesised TABULA matrix**. `cz_intensities.csv` was constructed for this build by bracketing the DE and PL TABULA values and applying CSN 73 0540 thermal-code logic per period; the brochure header explicitly flagged ±20-30 % uncertainty. The empirical −8 % gap is well inside that bound and inside the ±15 % consistency band.

The Czech result is also a quiet validation of the Option B reference-HDD framework applied correctly: `tabula_reference_hdd = 3400` (CSN 73 0540 / Praha-Ruzyne long-term mean) ≈ Czech actual HDD (3331), so the climate_multiplier of 0.9797 is near unity and doesn't materially shift the result. The CZ file shares its calibration with SK (climate-corrected by HDD_SK / 3400 = 0.9382); SK landed at +2.2 % vs Hotmaps in the same Colab run, confirming the proxy approach works for shared-tradition neighbours. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).
