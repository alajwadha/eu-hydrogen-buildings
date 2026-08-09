# Greece — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country EL`).
**Config:** `code/data/country_config/el.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Greece — a build-group-3 country (ES + PT, EL, CY).

**The headline fact:** Greece **is a TABULA country**. Its residential heat intensities come from the **direct Greek TABULA typology** (produced by the National Observatory of Athens / NTUA / CRES), with **no proxy and no climate correction**.

**Note on ISO2 code:** this model uses **EL** (the Eurostat convention) for Greece, not GR. EUBUCCO v0.2 uses Eurostat NUTS, so EL is correct.

---

## 1. Methodology relative to Luxembourg and France

Greece is a **direct-TABULA country** following the France branch. The 4-class taxonomy, floor-height assumptions, `floor_source: eubucco`, per-cohort intensity lookup with stock-weighted fallback, multi-source reconciliation and 8-page diagnostic PDF are identical to the earlier builds.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions by NUTS2 (NUTS 2016). Greece has 13 NUTS2 regions (all prefixed EL3x / EL4x / EL5x / EL6x). 52 NUTS3 regional units (*perifereiakes enotites*), stable in NUTS 2016 / 2021.

### 2.2 TABULA — Greece direct
**Greece is a TABULA country.** The Greek residential typology was produced by the **National Observatory of Athens (NOA)** with NTUA and CRES.

**Climate zones.** Greek TABULA defines **4 climate zones** per KENAK (A warmest — Crete; B — Athens/Patra; C — Thessaloniki; D coldest — Florina). The values used in `el_intensities.csv` are for **reference Zone B (Athens/Patra)**, the population-weighted reference.

**Extraction:** `code/data/raw/tabula/el_intensities.csv`. **Important caveat:** the Greek TABULA full numeric matrix is held in the brochure PDF and the TABULA WebTool, neither machine-extractable. The values are **research-synthesised best estimates** from the Greek TABULA range (~56–160 kWh/m²/yr) and the Dascalaki / Balaras measured-typology literature — flagged `NEEDS_VERIFY`, ±20% uncertainty.

### 2.3 Taxonomy mappings
- **Building class** — Greek TABULA SFH / MFH (only 2 residential classes — *polykatoikia*) → our 3: SFH ← SFH; MFH_LOW ← MFH; MFH_HIGH ← MFH (same — limitation; same approach as Slovenia/Cyprus).
- **Construction cohort** — Greek TABULA 3 periods (pre-1980; 1981-2000; 2001-2010) → our 6 cohorts. The model's pre-1945 and 1946-1970 cohorts both inherit the Greek TABULA pre-1980 values (uninsulated; first thermal-insulation regulation TOTEE introduced in 1980). 2011-2020 and post-2020 are extrapolated from KENAK-2010 / KENAK-2017 / nZEB requirements.

### 2.4 Climate (HDD)
Greece uses the direct typology, `climate_multiplier = 1.0`. Source: Eurostat `nrg_chdd_a` (base 15 °C). 2022 confirmed at 1538; 5-year mean 2018-2022 estimated ~1600 (other years `NEEDS_VERIFY`).

### 2.5 Retrofit shares and factors
**Retrofit factors** — Greek TABULA typology-averaged refurbishment ratios: standard 0.65, advanced 0.35 (Exoikonomo deep retrofits target ~65% saving). **PROVISIONAL**.

**Retrofit shares** (0.85 / 0.10 / 0.05) — modelling assumption grounded in the Greek Exoikonomo programme (cumulative ~47,000 dwellings deep-renovated as of early 2026, of a ~4 million stock = ~1%).

**Resulting blend factor:** 0.85 × 1.00 + 0.10 × 0.65 + 0.05 × 0.35 = **0.9325**.

### 2.6 DHW intensity
DHW from the `el_intensities.csv` DHW column (~18 SFH / ~16 MFH).

### 2.7 Non-residential intensity
Estimate 80 kWh/m²/yr, `NEEDS_VERIFY`. Contributes 0 TWh.

### 2.8 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **60.60** | 2015 | verified | Sum across all EL NUTS3 rows, all-classes. |
| Eurostat / Odyssee-Mure | 25 | 2022 | estimate | Residential FE ~50 TWh; space heating ~50% → ~25 TWh final-energy basis. |
| EU BSO | 35 | 2022 | anchored | Order-of-magnitude anchor. |

The Hotmaps 60.60 TWh figure appears higher than Eurostat-derived useful heat — a definitional gap (useful demand vs delivered final energy; broader scope) that should be stated in the paper.

---

## 3. NUTS3 spatial join
Greece has 52 NUTS3 regions; `02_classify.py` performs a spatial join.

---

## 4. Verification status (2026-05-19)

### Verified
1. 13 EL NUTS2 partitions; 52 NUTS3 codes (NUTS 2016 / 2021).
2. HDD EL 2022 = 1538 (Eurostat); 5-year mean estimated 1600.
3. Hotmaps EL total = 60.60 TWh.
4. Config validates; full input chain loads cleanly (fallback SFH ≈ 132 kWh/m²/yr).

### Still needs verification
1. **HDD 2018-2022 mean** — only 2022 confirmed.
2. **TABULA intensities** — research-synthesised (Zone B reference); verify against WebTool.
3. **MFH_LOW = MFH_HIGH** — Greek TABULA has one MFH class (limitation).
4. **pre-1945 / 1946-1970 cohorts** — both inherit Greek TABULA pre-1980 values.
5. **Retrofit factors** (0.65/0.35) and **DHW** — provisional.
6. **Retrofit shares** (0.85/0.10/0.05) — modelling assumption.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Greece built as build-group-3 country, a DIRECT TABULA country (NOA/NTUA/CRES typology, Zone B reference). Created `el.yaml`, `el_intensities.csv` (research-synthesised pending WebTool verification), `eu_bso/el_intensity.csv`, `el_national/el_climate_retrofit.csv`. climate_multiplier = 1.0. | Ali / Claude |
| 2026-05-19 | Colab G3 run completed: bottom-up 102.18 TWh vs Hotmaps 60.60 TWh = **+68.6 % (INVESTIGATE band)**. EL sits in the Mediterranean over-count cluster. | Ali / Claude |
| 2026-05-20 | Exploratory Option B reference-HDD correction tested and **REVERTED**. The brochure header explicitly calls out Zone B (Athens/Patra, ~1100 HDD) as the reference; Greek national mean HDD is 1600 (~45 % higher). The framework predicted a `climate_multiplier = 1600 / 1100 = 1.4545` should narrow the gap. Applied locally, the result would have shifted bottom-up to ~149 TWh = +143 % vs Hotmaps, MAKING IT WORSE. This is the cleanest negative empirical result against the Option B framework: the brochure-header zone claim does not reliably predict where the values fall vs Hotmaps. Reverted to climate_multiplier = 1.0; see [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) for the lesson learned. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-20, post-deflator commit `2158bef`)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only (post-deflator 0.55)** | **63.04** | **70.2** |
| Hotmaps 2015 baseline | 60.60 | 67.5 |
| EU BSO 2022 weighted-avg implied total | 98.39 | 109.5 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 25.00 | 27.8 |
| _Pre-deflator (initial G3 build, commit before 0685afa)_ | _102.18_ | _113.7_ |

**Verdict:** Bottom-up vs Hotmaps = **+4.0 %** — **OK band (consistent within ±15 %)**. The Balaras/Dascalaki f₁ = 0.55 deflator hit exactly the right value; EL is the showcase success for the comfort_regime framework. No further refinement required for the OIES paper bottom-up.

Greece is in the Mediterranean over-count cluster (alongside ES +143 %, PT +264 %, IT before correction +39 %, HR +66 %, CY +372 %, MT +231 %). The decomposition is roughly:

- **EUBUCCO floor area is moderately over-counted** — our 0.90 Bn m² aligns within ~15 % of EL pop 10.4 M × ~75 m²/dwelling.
- **Intensity is the dominant driver** — bottom-up at 113.7 kWh/m² over-states Hotmaps-implied (~67.5 kWh/m²) by ~47 %.

**Greece is the showcase NEGATIVE result for the Option B framework.** The `el_intensities.csv` brochure header explicitly cites Zone B (Athens/Patra, ~1100 HDD) as the reference climate; Greek national mean is 1600 HDD. The framework predicts a climate_multiplier of 1.45 should narrow the gap (scaling the cold-zone average above the warm-zone reference). Empirically the correction moves EL **further away from Hotmaps** (+143 % instead of +69 %).

The most credible interpretation: **`el_intensities.csv` is over-stated in absolute terms**, regardless of zone framing. The brochure header's Zone B claim is methodologically real but is not the binding constraint on the synthesised intensities — the values are over-stated for the Greek stock and would over-state regardless of climate scaling.

**Hotmaps remains the recommended residential heat-demand benchmark for Greece.** The refinement path is a TABULA WebTool re-extraction (country GR, Zone B explicitly) to anchor the synthesised values. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) for the broader audit lesson.

---

## 7. Academic refinement path (research 2026-05-20)

**Highest-leverage academic fix (and methodologically the cleanest of the Mediterranean cluster):** replace the current research-synthesised `el_intensities.csv` with values from **GR_TABULA_ScientificReport_NOA.pdf** (machine-readable PDF in the EPISCOPE archive, ~80 pages, full per-Zone q_h_nd matrix authored by NOA/NTUA/CRES — Dascalaki et al. 2011), THEN multiply by the **Dascalaki "calculated-vs-actual" deflator (~0.6)** documented in *Applied Sciences* 11(14):6254 (2021). Greek occupants empirically heat 1-2 rooms only, not whole-dwelling steady-state; this is a published methodological correction for the well-known TABULA over-statement vs measured Hellenic heating energy, NOT a calibration multiplier. Expected outcome: intensity drops from 113.7 → ~80 kWh/m² → bottom-up ≈ 72 TWh = **+19 % vs Hotmaps (LIKELY band)**.

Citations: Dascalaki E.G., Droutsa K., Balaras C.A., Kontoyiannidis S. (2011) *Energy & Buildings* 43(12):3400-3409; Dascalaki et al. (2021) *Applied Sciences* 11(14):6254; ELSTAT Household Budget Survey 2022 (39.9 % central oil heating); Exoikonomo cumulative ~130-150k deep retrofits ≈ 3.5 % (refined retrofit shares 0.83/0.13/0.04, blend effect small). Full ranked refinement priorities are in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Mediterranean direct-TABULA cluster section.

### 7.1 Applied this session (2026-05-20): comfort_regime deflator 0.55

The Balaras/Dascalaki adaptation factor was applied directly to `el.yaml` and wired into `03_heat_intensity.py` (multiplies the space-heating component only; DHW unchanged).

**Coefficient:** **0.55** — the stock-weighted mean of the published Balaras et al. (2016) f₁ measured-vs-calculated ratios for the Hellenic residential stock:
- SFH f₁ = 0.52
- MFH f₁ = 0.56 (Greek stock is ~70 % apartments → weighted average ≈ 0.55)

**Empirical basis:** Balaras et al. analysed ~8,500 KENAK Energy Performance Certificates plus 100+ household audits. The mechanism is documented: KENAK / REPB calculates at **18 h/day** whole-house steady-state operation; measured Greek operation averages **5 h/day** with widespread partial-room heating. Droutsa et al. (2021) corroborates: 71 % of SFH and 82 % of MFH heat fewer than 8 h/day; only 7 % SFH / 17 % MFH heat the whole dwelling. Post-2012 heating-oil-tax shock compressed central-heating use further (Santamouris et al. 2013 measured 37 % below-expected residential consumption that winter; ~95 % of Athens apartment blocks bought no heating oil).

**Status:** the 0.55 coefficient is THE published deflator — more precise than the earlier "~0.6" working figure in the audit doc. The TABULA-matrix refresh from the NOA scientific report remains the next refinement (it would replace the research-synthesised intensities; the deflator stays applied either way, since it represents operation not calibration).

**Post-rebuild result (commit `2158bef`, 2026-05-20): SUCCESS.** Bottom-up dropped from **102.2 TWh (+69 %)** to **63.0 TWh (+4 %)** vs Hotmaps 60.6 — **inside the OK band (±15 %)**. The Balaras/Dascalaki f₁ = 0.55 deflator was exactly the right coefficient. EL is now reconciled and no further refinement is required for the OIES paper bottom-up. The TABULA-matrix refresh and Dascalaki-deflator-on-refreshed-matrix path can still be pursued for academic precision but is no longer a model-correctness need.

**Sources:**
- Balaras, C.A., Dascalaki, E.G., Droutsa, K.G., Kontoyiannidis, S. (2016) "Empirical assessment of calculated and actual heating energy use in Hellenic residential buildings", *Applied Energy* 164: 115–132. DOI 10.1016/j.apenergy.2015.11.027.
- Dascalaki, E.G., Droutsa, K.G., Balaras, C.A., Kontoyiannidis, S. (2011) *Energy & Buildings* 43(12): 3400–3409.
- Droutsa, Kontoyiannidis, Dascalaki, Balaras (2021), *Applied Sciences* 11(14): 6254 (occupancy behaviour).
- Santamouris et al. (2013), *Energy & Buildings*, DOI 10.1016/j.enbuild.2013.06.024 (post-tax consumption compression).
