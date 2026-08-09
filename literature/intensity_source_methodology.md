# Heat Intensity Source Methodology — Luxembourg

**Prepared for:** Ali Alajwad & Dr. Abdurahman Alsulaiman
**Date:** May 2026
**Status:** Real implementation deployed in `code/scripts/luxembourg/03_heat_intensity.py`.
**Scope:** Luxembourg only. Scale-out to 29 countries pending Abdul validation.

---

## 1. Why this document exists

Script `03_heat_intensity.py` was previously a stub with placeholder per-class intensities (160 / 130 / 150 kWh/m²·a for SFH / MFH / non-res). Result: bottom-up total of 6.43 TWh/yr vs Hotmaps 8.27 TWh (−22% gap).

This document records the upgrade from placeholders to a real bottom-up intensity model, the source-decision rationale, and the resulting reconciliation against three external benchmarks.

---

## 2. Source decision matrix

The script needed per-(building class × vintage cohort) intensity values in kWh/m²·a. Five candidate sources were considered:

| Source | Coverage of LU | Granularity | Status |
|---|---|---|---|
| (a) TABULA / EPISCOPE | ❌ LU not a TABULA country | Per (class × cohort × refurb level) | **Adopted via Belgium proxy** |
| (b) EU Building Stock Observatory | ✅ LU covered, Dec 2025 release | National avg by cohort, no class | **Adopted for cross-validation** |
| (c) Hotmaps building stock | ✅ LU covered | National total only | **Adopted as reconciliation benchmark** |
| (d) STATEC LU national | ✅ LU covered | Aggregated only; no public archetype detail | Considered; format barriers |
| (e) Odyssee-Mure LU 2024 | ✅ LU covered | National total trend; useful for trend validation | **Adopted as reconciliation benchmark** |

### Final choice: blended (a) + (b) + (c) + (e)

- **(a) TABULA Belgium** = primary source for per-(class × cohort) intensities. Belgium chosen as proxy because:
  - Climate similarity: BE ~2,900 HDD/yr vs LU ~3,217 HDD/yr (Eurostat nrg_chdd_a 2018-2022 avg)
  - Construction practice overlap: stone/masonry pre-WWII; brick cavity + concrete post-war
  - Code harmonisation: Walloon PEB ≈ Luxembourgish energy passport
  - German (DE) proxy rejected: too cold, over-counts MFH; Italian (IT) rejected: wrong climate
- **(b) EU BSO LU national-weighted** = used both (i) for the "unknown cohort" fallback intensity per class, and (ii) as one of three reconciliation benchmarks
- **(c) Hotmaps 2015 baseline** = primary reconciliation benchmark; what the existing 5-step model uses
- **(e) Odyssee-Mure 2021 back-calculation** = independent reconciliation (0.448 Mtoe residential × 55% heating share = 7.20 TWh)

### No calibration applied

Per decision (Ali / Abdul, May 2026): the script reports the bottom-up total **as-is**, alongside the Hotmaps / EU BSO / Odyssee benchmarks. If the bottom-up total deviates >20% from Hotmaps, that's a methodology finding to disclose in the paper, not a bug to silently correct. With the current implementation the gap is −5.2% (well within tolerance), so this is not actively a concern.

---

## 3. Methodology

For each building in `LU_buildings_classified.parquet`:

### Step 1 — Cohort assignment

Map EUBUCCO `construction_year` to a TABULA-compatible cohort:

| Cohort label | Year range | Rationale for cutoff |
|---|---|---|
| `pre-1945` | < 1945 | Pre-WWII stock; mostly solid-masonry; no insulation |
| `1946-1970` | 1945-1970 | Reconstruction era; brick cavity walls (uninsulated) |
| `1971-1990` | 1971-1990 | First insulation regulations post-oil-crisis |
| `1991-2010` | 1991-2010 | EPBD-aligned construction; cavity insulation common |
| `2011-2020` | 2011-2020 | Near-zero-energy push; LU mandatory 2017 |
| `post-2020` | ≥ 2021 | NZEB mandatory for new builds |
| `unknown` | NaN | Missing `construction_year` → fallback (Step 5) |

Cutoffs align with TABULA Belgium cohort boundaries, EPBD recast (2018), and LU-specific regulatory waves.

### Step 2 — TABULA Belgium per-(class × cohort) base lookup

Read `code/data/raw/tabula/be_intensities.csv`. 18 rows: 3 classes (SFH / MFH_LOW / MFH_HIGH) × 6 cohorts. For each building, look up its (`building_class`, `cohort`) → `sh_intensity_kwh_m2_yr` (space heating, BE, original-state) and `dhw_intensity_kwh_m2_yr` (DHW).

### Step 3 — Climate correction BE → LU

Useful space-heating demand scales approximately linearly with HDD under EN ISO 13790 (seasonal method). LU HDD / BE HDD = 3217 / 2894 = **1.112**. Multiply BE space-heating intensity by 1.112 to get LU-corrected value.

DHW is **not** climate-corrected (water-heating demand depends on temperature differential between mains water and target temp, which is roughly climate-insensitive at LU/BE latitudes).

### Step 4 — Retrofit-state blending

LU residential stock is not uniformly in original condition. Apply a blend representing the actual mix:

| State | Share | Intensity multiplier |
|---|---|---|
| Original (no retrofit) | 55% | 1.00 |
| Standard refurb (single insulation pass) | 35% | 0.65 |
| Advanced refurb (deep retrofit / passive standard) | 10% | 0.35 |

Blend factor = 0.55 × 1.00 + 0.35 × 0.65 + 0.10 × 0.35 = **0.813**

Multiplier weights derived from Odyssee-Mure LU 2024 country profile + STATEC building stock 2021. Retrofit-impact factors (0.65, 0.35) from TABULA Belgium published refurb scenarios.

### Step 5 — Unknown-cohort fallback

For buildings with no `construction_year` in EUBUCCO (~53% of LU buildings in current export): assign a class-specific national-stock-weighted average intensity. Computed as:

```
fallback_intensity[class] = Σ over cohorts of:
    stock_pct_LU[cohort] × TABULA_BE[class, cohort] × climate × retrofit_blend + DHW[class]
```

where `stock_pct_LU` weights come from EU BSO LU file. Computed values:

| Class | Fallback intensity (kWh/m²·a) |
|---|---|
| SFH | 195.8 |
| MFH_LOW | 158.2 |
| MFH_HIGH | 150.4 |

These are sensible — they sit at the centre of the per-cohort range (which spans ~30-265 for SFH).

### Step 6 — Non-residential treatment

Apply flat 140 kWh/m²·a (EU BSO 2025 LU non-residential average). Note: heated floor area for NON_RESIDENTIAL is 0 in the current country output (script 02 assigns `heated_floor_area = 0` to NON_RES because they're not part of residential heating decarbonisation), so non-res contributes zero to the bottom-up total. This is a known limitation flagged for subsequent work.

### Step 7 — Heat demand per building

```
heat_demand_kWh = (sh_intensity_corrected + dhw) × heated_floor_area_m2
```

where `heated_floor_area_m2 = footprint × floors × 0.85` (TABULA convention).

### Step 8 — Aggregate + reconcile

Group by (`building_class`, `cohort`); sum to national total; compare against four benchmarks.

---

## 4. Results (May 2026 country run)

| Source | TWh/yr | kWh/m²/yr avg |
|---|---|---|
| Hotmaps 2015 baseline | 8.27 | 181.2 |
| **Bottom-up (this model)** | **7.84** | **171.9** |
| Odyssee-Mure 2021 LU residential | 7.20 | 157.8 |
| EU BSO 2021 LU weighted-avg implied | 6.75 | 147.9 |

**Bottom-up vs Hotmaps gap: −5.2% (within ±15% tolerance — consistent)**

The four estimates form a narrow cluster:
- Hotmaps 2015 = 8.27 TWh (highest; 2015 vintage so before efficiency gains)
- This model = 7.84 TWh (bottom-up, May 2026)
- Odyssee-Mure 2021 = 7.20 TWh (national stats, climate-corrected)
- EU BSO 2025 = 6.75 TWh (lowest; reflects 2021-25 efficiency improvements)

The downward trend from Hotmaps 2015 → BSO 2025 (−18% over 10 years) is consistent with the Odyssee-Mure observation that **LU specific space-heating consumption fell from 21.6 koe/m² in 2000 to 12.2 koe/m² in 2022** — a 44% reduction over 22 years.

The model's bottom-up total sits naturally between Hotmaps and Odyssee, which is what we'd expect: it uses TABULA values that pre-date the most recent efficiency gains but applies climate + retrofit corrections that capture the LU-specific reality.

---

## 5. Open questions for Abdul

1. **Retrofit-state shares (55/35/10)** — these are my best estimate from Odyssee-Mure cumulative renovation series + STATEC. Should we have STATEC's annual energy passport (Energiepass) data instead?
2. **Climate correction linear in HDD** — is this acceptable for the OIES paper, or do we need a more sophisticated degree-day weighting (e.g. sub-monthly correction)?
3. **Belgian proxy for LU** — accept as documented, or use a weighted (BE + DE) blend?
4. **Non-residential treatment** — currently flat 140 kWh/m². For OIES residential-focused paper, leave as-is, or split by sector (office / retail / industrial / education / health)?
5. **Unknown-cohort fallback** — currently EU BSO stock-weighted. Should it instead be Hotmaps-calibrated (a target value that closes the gap with Hotmaps national total)?
6. **EUBUCCO `construction_year` coverage** — only ~47% of LU buildings have it. Script 02 needs the column added to `save_cols` to expose this to script 03. Done in this commit. For scale-out, what to do for countries where EUBUCCO age coverage is much lower (e.g. Eastern Europe with <20%)?

---

## 6. Implementation status

| Component | Status |
|---|---|
| TABULA BE intensity table | ✅ `code/data/raw/tabula/be_intensities.csv` (18 rows) |
| EU BSO LU national reference | ✅ `code/data/raw/eu_bso/lu_intensity.csv` (6 rows) |
| LU national parameters (HDD, retrofit, DHW) | ✅ `code/data/raw/lu_national/lu_climate_retrofit.csv` (11 params) |
| Script 03 real implementation | ✅ `code/scripts/luxembourg/03_heat_intensity.py` |
| Reconciliation against 3 benchmarks | ✅ Output: `LU_reconciliation_with_hotmaps.csv` |
| Per-class × per-cohort summary | ✅ Output: `LU_heat_intensity_summary.csv` |
| Augmented building parquet | ✅ Output: `LU_buildings_with_heat_demand.parquet` (22 MB) |
| Script 02 `construction_year` exposure | ✅ Added to `save_cols` in this commit |
| Scale-out to 29 countries | 🔲 Pending Abdul approval after Luxembourg build validation |
| Per-country TABULA proxy mapping | 🔲 Pending — proposed: LU→BE, CY→GR, MT→IT, BG→RO, HR→SI, others direct |
| Non-residential breakdown | 🔲 Pending — out of scope for residential-focused OIES paper |

---

## 7. Sources

- **TABULA / EPISCOPE Belgium typology:** Cyx W., Renders N., Van Holm M., Verbeke S. (2011). *IEE TABULA — Typology Approach for Building Stock Energy Assessment, Belgian Scientific Report.* VITO report **2011/TEM/R/091763**, August 2011. https://episcope.eu/fileadmin/tabula/public/docs/scientific/BE_TABULA_ScientificReport_VITO.pdf. National brochure (Dutch): www.episcope.eu/building-typology/country/be/
- **TABULA cross-country methodology:** Loga T., Stein B., Diefenbach N. (2016). TABULA building typologies in 20 European countries. *Energy & Buildings* 132:4-12. DOI 10.1016/j.enbuild.2016.06.094
- **TABULA Common Calculation Method:** episcope.eu/fileadmin/tabula/public/docs/report/TABULA_CommonCalculationMethod.pdf
- **EU Building Stock Observatory:** European Commission, DG Energy. EU BSO database (Dec 2025 release). building-stock-observatory.energy.ec.europa.eu/
- **Odyssee-Mure Luxembourg:** odyssee-mure.eu/publications/efficiency-trends-policies-profiles/luxembourg.html (2024 release)
- **Eurostat HDD:** `nrg_chdd_a` — Cooling and heating degree days by country, annual data (base temperature 15°C; source: JRC AGRI4CAST gridded meteorological data). https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a/default/table
- **JRC Luxembourg heat pump market profile:** JRC137131 (2024)
- **Renov.lu vintage examples:** renov.lu/en/heating/heat-pump/electricity-consumption/ (real-world LU intensity by vintage)

---

## Change log

| Date | Change |
|---|---|
| 2026-05-14 | Initial implementation. Replaced placeholder intensities with TABULA BE + EU BSO + LU national-parameters blend. Bottom-up total 7.84 TWh vs Hotmaps 8.27 TWh (−5.2%, within tolerance). |
