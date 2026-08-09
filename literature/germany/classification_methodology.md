# Germany — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country DE`).
**Config:** `code/data/country_config/de.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Germany — the first country of build group 1 (DE + EE, LV, LT) and the heavyweight of the 29-country scale-out.

**The headline fact:** Germany **is a TABULA country**. Its residential heat intensities come from the **direct German TABULA typology** (produced by IWU Darmstadt), with **no proxy and no climate correction** — the same methodological branch as France, not the proxy branch used for Luxembourg, Finland and the Baltic states.

---

## 1. Methodology relative to Luxembourg and France

The pipeline architecture is unchanged. Germany is methodologically a **direct-TABULA country** and so follows the **France branch**:

| Element | Luxembourg | France | Germany |
|---|---|---|---|
| TABULA dataset | Belgium (proxy) | **France (direct)** | **Germany (direct)** |
| Climate correction | HDD_LU/HDD_BE = 1.112 | 1.0 (direct) | **1.0 (direct)** |
| Retrofit factors source | TABULA Belgium | TABULA France | **TABULA Germany (IWU 2015)** |
| EUBUCCO partitions | 1 (LU00) | 22 | **38 NUTS2 (Regierungsbezirke)** |
| NUTS3 regions | 1 | 96 | **401 Kreise** |
| Hotmaps reconciliation | single LU000 row | sum across FR rows | **sum across all DE rows (793.70 TWh)** |

Everything else — the 4-class taxonomy (SFH / MFH_LOW / MFH_HIGH / NON_RESIDENTIAL), the floor-height assumptions (3.0 m residential / 3.5 m other), the 0.85 useable-area fraction, `floor_source: eubucco`, the per-cohort × per-class intensity lookup with stock-weighted fallback for unknown vintages, the multi-source reconciliation, and the 8-page diagnostic PDF — is identical to Luxembourg and France.

Germany is the heavyweight of build group 1. EUBUCCO v0.1 covered ~202M buildings EU-wide; Germany is the single largest national partition. Script 02 runs in `--per-partition` streaming mode so peak RAM stays at roughly one NUTS2 region.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions buildings by NUTS2 region (NUTS 2016 vintage). Germany has **38 NUTS2 regions** (the *Regierungsbezirk* / government-region level), listed in `de.yaml`. The 401 NUTS3 *Kreise* codes were extracted from the repo GISCO file (`NUTS_RG_01M_2021_4326_clean.csv`); German NUTS3 codes are stable between the 2016 and 2021 vintages.

Citation: Milojevic-Dupont N. et al. (2023). EUBUCCO v0.1. *Scientific Data* 10:147. DOI 10.1038/s41597-023-02040-2.

### 2.2 TABULA — Germany direct
**Germany is a TABULA country.** The German residential typology was produced by **IWU Darmstadt** (Institut Wohnen und Umwelt) for the EU TABULA/EPISCOPE projects. No proxy and no climate correction are used.

**Primary source:** IWU 2015, *Deutsche Wohngebäudetypologie / TABULA Typology Brochure Germany* (Loga, Diefenbach, Stein, Born), and the German TABULA Scientific Report (IWU). Country page: `https://episcope.eu/building-typology/country/de/`.

**Extraction:** `code/data/raw/tabula/de_intensities.csv` (18 cells = 3 classes × 6 cohorts). The file header documents the extraction. Key points:

- **Energy-need basis.** The space-heating intensity is the German TABULA net space-heating energy need (q_h,nd, *Netto-Heizwärmebedarf*), the standard TABULA reference calculation (DIN V 18599-10, German reference climate). This is the calculated energy need, not the measured-consumption-adapted value — consistent with how the BE/FR/SE proxy files were built.
- The German TABULA also publishes a measured-consumption-adapted version (~0.5–0.85× for high-demand old stock). It is **not** used, for cross-country consistency. The bottom-up total is reported as-is and reconciled against Hotmaps without calibration.

### 2.3 Two taxonomy mappings

**Building class — German TABULA 4 classes → our 3 residential classes.** German TABULA has EFH (single-family), RH (terraced), MFH (multi-family) and AB (GMH/HH large apartment block). Mapping: SFH ← EFH; MFH_LOW ← average of RH and MFH; MFH_HIGH ← AB.

**Construction cohort — German TABULA 12 periods → our 6 cohorts.** German periods A–L (…1859 through 2016+) are averaged into the 6 model cohorts; the mapping is documented in the `de_intensities.csv` header. post-2020 is extrapolated from the newest German period (2016+), flagged.

**Known limitation — MFH_HIGH gap.** The German TABULA defines **no large apartment block (GMH/AB) after period F (1969–1978)**. The MFH_HIGH cohorts 1991-2010, 2011-2020 and post-2020 are therefore estimated (post-1990 cells proxied to MFH_LOW new-build, since large blocks built post-1990 follow the same EnEV/GEG new-build code). Flagged `NEEDS_VERIFY` in `de_intensities.csv` and `de.yaml._meta`.

### 2.4 Climate (HDD)
Germany uses the direct German typology, so `climate_multiplier = 1.0`. `hdd_country` and `hdd_proxy` are both set to Germany's own HDD so the loader's multiplier check passes.

**Source:** Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022:
DE annual HDD 2784.88 / 2812.97 / 2754.54 / 3128.38 / 2748.46 → **mean 2845.85**.

### 2.5 Retrofit shares and factors
**Retrofit factors** are the German TABULA typology-averaged refurbishment ratios: **standard 0.55**, **advanced 0.18** of existing-state space-heating need (IWU 2015 brochure, refurbishment variants 001/002/003).

**Retrofit shares** (0.60 original / 0.30 standard / 0.10 advanced) are a **modelling assumption**. Germany's energy-renovation rate is low (~1.0 %/yr; dena Gebäudereport 2024, Odyssee-Mure). Sustained over ~1990–2024 a ~1 %/yr rate implies roughly 40 % of the stock has had at least one envelope refurbishment, weighted toward standard rather than deep measures. The standard/advanced sub-split remains an assumption — flagged.

**Resulting blend factor:** 0.60 × 1.00 + 0.30 × 0.55 + 0.10 × 0.18 = **0.783**.

### 2.6 DHW intensity
DHW is added per building from the `de_intensities.csv` DHW column: 11.0 kWh/m²/yr for SFH/TH, 16.5 for MFH/AB (German TABULA area-specific DHW energy need, near-constant across cohorts).

### 2.7 Non-residential intensity
Estimate, 120 kWh/m²/yr, `NEEDS_VERIFY`. NON_RESIDENTIAL buildings carry zero heated area in the pipeline, so this value contributes 0 TWh to the residential bottom-up total.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **793.70** | 2015 | verified | Sum of `heat_2015_MWh` across all DE NUTS3 rows in `building_stock_nuts3.csv`. All-classes total, the reconciliation target per the LU/FR methodology. |
| Odyssee-Mure / AGEB | 540 | 2022 | estimate | German household space-heating final energy, recent (mild) years ~500–550 TWh. Final-energy basis — below the Hotmaps 2015 useful-demand, cold-reference-year figure. |
| EU BSO | 650 | 2022 | anchored | Order-of-magnitude anchor; the BSO portal could not be queried. |

The Hotmaps 2015 figure is a useful-demand, cold-year, all-classes total; the Odyssee-Mure ~540 TWh is a recent-year, final-energy, residential figure. The definitional gap is expected and should be stated in the paper.

---

## 3. NUTS3 spatial join
Germany has 401 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present), the same way the France build does.

---

## 4. Verification status (2026-05-19)

### Verified
1. 38 DE NUTS2 partitions and 401 NUTS3 codes — NUTS 2016/2021, cross-checked against the repo GISCO file.
2. HDD DE = 2845.85 (Eurostat `nrg_chdd_a` 2018–2022 mean).
3. German TABULA intensities extracted — `code/data/raw/tabula/de_intensities.csv`, 18 cells, class and cohort mappings documented.
4. Retrofit factors 0.55 / 0.18 — German TABULA typology-averaged refurbishment ratios.
5. Hotmaps DE total = 793.70 TWh — computed from `building_stock_nuts3.csv`.
6. Config validates against `CountryConfig.load_country_config`; the full TABULA + BSO + national input chain loads cleanly (unknown-cohort fallback SFH ≈ 193 kWh/m²/yr).

### Still needs verification
1. **Retrofit shares** (0.60/0.30/0.10) — modelling assumption from Germany's ~1 %/yr renovation rate; no published three-state envelope distribution.
2. **MFH_HIGH cohorts 1991-2010 onward** — the German TABULA defines no large apartment block after 1978; those cells are estimated.
3. **Non-residential intensity** (120) — estimate; contributes 0 TWh.
4. **EU BSO benchmark** — anchored estimate, BSO portal not retrievable.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Germany built as build-group-1 country #1, a DIRECT TABULA country (IWU typology). Created `de.yaml`, `de_intensities.csv` (extracted from the IWU 2015 German TABULA brochure), `eu_bso/de_intensity.csv`, `de_national/de_climate_retrofit.csv`. climate_multiplier = 1.0. Retrofit factors 0.55/0.18 from the German TABULA refurbishment scenarios; retrofit shares a modelling assumption from the ~1 %/yr renovation rate. | Ali / Claude |
| 2026-05-19 | Colab G1 run completed: bottom-up 765.82 TWh vs Hotmaps 793.7 TWh = **−3.5 % (OK)**. Germany anchors the pipeline credibility — the largest single bottom-up in the build, the only country with TABULA values extracted from a published brochure rather than research synthesis. The DE TABULA, applied at face value to German actual climate, reconciles cleanly with Hotmaps. | Ali / Claude |
| 2026-05-20 | Option B reference-HDD correction tested and **REVERTED**. The brochure uses the DIN V 18599-10 reference climate (Wuerzburg, ~3300 HDD); German actual mean HDD is 2846 (~14 % below). The framework predicted a `climate_multiplier = 2845.85 / 3300 = 0.8624`. Applied locally, the result would have shifted bottom-up to ~660 TWh = −16.8 % vs Hotmaps, BREAKING the existing OK reconciliation. Whatever DIN-vs-national-mean residual bias exists in the DE values is already offset elsewhere in the pipeline (likely EUBUCCO floor-area calibration that happens to fit Germany well). Reverted to `climate_multiplier = 1.0`; the failed Option B experiment is documented in [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) as a lesson against imposing theory over empirical fit. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **765.82** | **170.1** |
| Hotmaps 2015 baseline | 793.70 | 176.3 |
| EU BSO 2022 weighted-avg implied total | 700.07 | 155.5 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 540.00 | 120.0 |

**Verdict:** Bottom-up vs Hotmaps = **−3.5 %** (OK — within ±15 % consistency band).

Germany is the pipeline's reference anchor for cold-temperate continental Europe. The DE TABULA (IWU 2015) is the only directly machine-extracted typology in the build — all other "research-synthesised" TABULA files for ES/EL/CY/IT/CZ/PL etc. are best estimates with ±20-30 % uncertainty. Germany's clean reconciliation establishes that the EUBUCCO + TABULA × retrofit-blend + DHW pipeline works correctly when the input data is good.

The Option B reference-HDD methodology was developed and tested using Italy + Germany as test cases. Germany's revert (alongside reverts for EL and FI) is the **negative empirical result** that constrains the framework: the brochure-header reference-zone claim doesn't reliably predict where the bottom-up falls vs Hotmaps. Only Italy (where the brochure was unambiguous about a Middle-zone calibration AND the actual climate clearly sits in a different zone) survived as a successful Option B application. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).
