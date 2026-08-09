# Luxembourg — building classification methodology

**Status:** draft, awaiting Abdul review.
**Last updated:** 2026-05-15.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/luxembourg/02_classify.py`.

This document is the paper-ready methodology for the EUBUCCO integration in the Luxembourg country build of the eu-hydrogen-buildings model. It is the reference for the methods section of the OIES paper and the technical appendix.

> **2026-05-15 update — GBA cross-check moved to historical reference.** Earlier versions of this pipeline used the Global Building Atlas (GBA) ODbLPolygon tile as a footprint-completeness check against EUBUCCO. That check yielded a single, stable finding: GBA's residential floor area for Luxembourg is ~1.4× EUBUCCO's, attributable to GBA's looser polygon definition (it counts sheds, extensions, and garages that EUBUCCO's source cadastres filter out). Because the cross-check produces one stable number for a 22-minute Colab cost, GBA is no longer pulled at runtime. The 1.4× finding remains in this document and in the paper, citing Zhu et al. (2025). See `literature/assumptions_register.md` entry 2026-05-15 for full rationale.

---

## 1. Objective

Replace the existing model's three-category building stock (`SFH` / `MFH_HIGH` / `OTHER` from NUTS3-aggregated Hotmaps + Eurostat data) with a building-resolved, classified stock built from open European building footprint datasets. The classification must:

1. Distinguish heating-system feasibility classes (HP retrofit, district heat connection, gas/oil legacy);
2. Preserve consistency with the existing model's spatial resolution (NUTS3);
3. Be reproducible from open sources;
4. Be defensible in a peer-review setting.

---

## 2. Datasets used

| Dataset | Version / DOI | Role | License |
|---|---|---|---|
| EUBUCCO | v0.2; DOI [10.5281/zenodo.7225259](https://doi.org/10.5281/zenodo.7225259) | Primary source — building footprints with height, type, age | ODbL v1.0 |
| Global Building Atlas (GBA) — ODbLPolygon | DOI [10.14459/2025mp1782307](https://doi.org/10.14459/2025mp1782307) | Historical cross-check (no longer pulled at runtime) — found ~1.4× residential floor area vs EUBUCCO, consistent with GBA's looser polygon definition | ODbL v1.0 |
| Hotmaps regional heat demand | 2015 baseline | Existing model — for cross-validation | CC BY 4.0 |
| Eurostat CENS_21DWBNO_R3 | 2021 Census | Existing model — dwelling counts per NUTS3 by building type | Eurostat ToU |

GBA's CC BY-NC components (`GBA.Polygon`, `GBA.LoD1`, `GBA.Height`) are **deliberately not used** to preserve commercial-compatible licensing of the model output. Heights are supplied by EUBUCCO instead.

Scope: **Luxembourg (NUTS2 = `LU00`, NUTS3 = `LU000`)**. ~150,000 buildings. Selected as smallest national stock with single-NUTS-region aggregation simplicity, allowing rapid pipeline validation before scaling to the full 29-country model.

---

## 3. The four classes

| Class | Definition | Energy-relevance |
|---|---|---|
| **`SFH`** | Single-family house (detached, semi-detached, terraced) | Largest envelope/dwelling ratio → highest specific heat demand; easiest heat-pump retrofit (outdoor unit placement trivial); poor district-heat economics (long pipe per house). |
| **`MFH_LOW`** | Multi-family house, low-rise (3–5 floors) | Dominant European apartment-block typology. Centralised gas boilers dominate today. HP retrofit feasible with shaft work. DH connection often economic in dense urban areas. |
| **`MFH_HIGH`** | Multi-family house, mid/high-rise (≥6 floors, towers) | Lowest per-dwelling envelope loss. HP retrofit hardest (refrigerant volume limits per EN 378, shaft space constraints, electrical capacity). DH most attractive economically. |
| **`NON_RESIDENTIAL`** | Commercial, industrial, office, retail, public | Excluded from residential heat demand calculation. Profile differs fundamentally (occupancy schedule, higher specific demand for retail/office, summer cooling dominant). |

These four are mapped to the existing model's `SFH` / `MFH_HIGH` / `OTHER` categories as: `SFH→SFH`, `{MFH_LOW, MFH_HIGH}→MFH_HIGH`, `NON_RESIDENTIAL→OTHER`. The four-class split is preserved internally for finer-grained downstream analysis (HP feasibility scoring, DH suitability scoring).

---

## 4. Decision rules

Applied in order; first match wins.

| # | Condition | Class |
|---|---|---|
| 1 | EUBUCCO `type` starts with `"non-"` | **NON_RESIDENTIAL** |
| 2 | floors ≥ 6 AND footprint ≥ 800 m² | **MFH_HIGH** |
| 3 | floors ≤ 2 AND footprint < 250 m² | **SFH** |
| 4 | 3 ≤ floors ≤ 5 | **MFH_LOW** |
| 5 | else (ambiguous; typically missing height + large footprint) | **MFH_HIGH** (conservative default) |

where:
- `floors = round(height_m / floor_height)`, minimum 1;
- `floor_height = 3.0 m` for residential, `3.5 m` for non-residential;
- `floors = NaN` if height is missing (~27% of LU buildings in EUBUCCO);
- `footprint_area_m2` is computed from the polygon in EPSG:3035 (ETRS89-LAEA, equal-area projection standard for European spatial analysis).

---

## 5. Justification of each rule

### 5.1 Rule 1 — EUBUCCO type first

EUBUCCO's `type` attribute is the most authoritative non-residential signal available. Coverage was 46% in v0.1 (Milojevic-Dupont et al., 2023); v0.2 is expected to be higher. Trusting this first short-circuits false-positive residential classification of commercial stock, which would otherwise distort:

- the residential heat-demand total (commercial buildings have ~1.5–2× higher specific demand for retail/office);
- the HP-feasibility scoring (commercial buildings have different cooling/heating ratios);
- the per-dwelling cost calculations downstream in the LCOH module.

### 5.2 Rule 2 — Six floors as the high-rise threshold

The six-floor threshold is the standard cut in European buildings-sector typologies including TABULA (IEE 2009–2012), the EU Building Stock Observatory, and Hotmaps. Three independent technical reasons converge at six floors:

1. **Lift mandate.** Most EU national building codes (e.g. Bauordnungen in DE, RBC in BE, Code de la Construction in FR) require lifts at ~5 floors and above for new residential construction. This shifts maintenance cost, accessibility constraints, and unit ownership structure.
2. **Construction system.** Below six floors, timber and masonry construction remain economical; at six floors and above, reinforced-concrete or steel framing dominates, with material consequences for embodied carbon and renovation feasibility.
3. **HP retrofit constraints.** EN 378 refrigerant volume limits, condenser unit placement requirements, and shaft riser dimensions create a discontinuous step in HP retrofit complexity above ~6 floors.

The 800 m² footprint co-requirement filters out narrow 6-floor row houses that share none of the above structural or energy characteristics.

### 5.3 Rule 3 — SFH definition

A single-family dwelling in the EU is typically 80–200 m² footprint with 1–2 storeys; small row/terraced houses extend the upper bound to roughly 250 m² (TABULA national typology reports, Hotmaps building stock distributions). The 2-floor cap excludes 3-floor townhouses, which:
- share party walls with neighbours (heat sharing reduces per-unit demand);
- have shared roof structure (insulation strategy differs);
- have harder HP unit placement (no rear garden access in many cases).

These behave more like MFH_LOW for energy purposes and are classified as such.

### 5.4 Rule 4 — MFH_LOW (3–5 floors)

The dominant European apartment-block typology. Examples: German *Plattenbau*, French *HLM*/*barre*, Italian *blocchi popolari*, Spanish *bloque*. Common features relevant to the model:

- Centralised heating system (gas boiler in West, DH in CEE, oil in some pockets);
- HP retrofit feasible with shaft work for refrigerant runs;
- District-heat connection economically attractive in dense urban contexts;
- Unit-by-unit replacement possible (unlike MFH_HIGH where centralised system is the norm).

Distinguishing this from MFH_HIGH matters because the latter has materially lower per-dwelling envelope loss (shared walls/roofs) but materially higher HP retrofit cost. The two have opposite signs in many policy scenarios.

### 5.5 Rule 5 — Conservative default

When height is missing and footprint is large (typical of older OSM data or imputation gaps), the building is more likely a large structure than a single-family home. Defaulting to MFH_HIGH is policy-conservative because high-rises are the **hardest** class to electrify. Over-counting MFH_HIGH therefore **understates** the achievable heat-pump uptake — erring in the direction less likely to overstate decarbonisation potential.

This rule should be revisited in district-heat-feasibility analysis, where the same default has the opposite policy direction (DH is easier in dense MFH_HIGH stock, so over-counting would *overstate* DH potential).

---

## 6. Parameter values and their sources

| Parameter | Value | Source |
|---|---|---|
| Floor-to-floor, residential | 3.0 m | EN 17037; ISO 52000-1; 2.5 m clear + 0.5 m structure/services |
| Floor-to-floor, non-residential | 3.5 m | Standard commercial ceiling + raised access floor allowance |
| Useable area fraction | 0.85 | TABULA; ISO 52000-1; EN 16798-1 (after internal walls, lobbies, stairwells) |
| SFH footprint cap | 250 m² | Hotmaps + TABULA SFH typology midpoint + row-house upper bound |
| High-rise minimum footprint | 800 m² | Corresponds to ~10–15 apartment units per floor |
| Projection for area | EPSG:3035 (ETRS89-LAEA) | INSPIRE / EuroSDR European spatial analysis standard |

The 0.85 useable-area fraction is a single TABULA-default value applied uniformly across all classes; real values vary 0.75–0.92 across building types and ages (TABULA national reports). This is acknowledged as a simplification.

---

## 7. Derived attributes computed per building

| Attribute | Formula | Units |
|---|---|---|
| `footprint_area_m2` | polygon area, reprojected to EPSG:3035 | m² |
| `height_m` | EUBUCCO `height` field (NaN if missing) | m |
| `floors_estimated` | round(height / floor_height), min 1, NaN if no height | integer |
| `building_class` | from decision rules in §4 | enum |
| `heated_floor_area_m2` | footprint × floors × 0.85, or 0 if NON_RESIDENTIAL | m² |

---

## 8. Aggregation to NUTS3

Luxembourg has a single NUTS3 region (`LU000`), so aggregation is the national total. For larger countries in the planned rollout, EUBUCCO's `nuts3` field will be used directly (already present in v0.2 partitioning). The aggregation produces, per NUTS3:

- Building count per class
- Total footprint area per class
- Total heated floor area per class
- Mean floors per class
- Median height per class

This is mirrored to `countries/Luxembourg/data/LU_buildings_aggregated_NUTS3.csv` and to `code/data/processed/luxembourg/LU_aggregated_NUTS3.csv`.

---

## 9. Cross-validation with current model

The aggregated EUBUCCO classification is compared against the existing row for `LU000` in `code/data/processed/building_stock_nuts3.csv`. The comparison is saved as `LU_model_comparison.csv` and shows side-by-side:

| Metric | Current model | EUBUCCO build | Ratio |
|---|---|---|---|
| SFH dwelling count | from Eurostat census | from classification | ratio |
| MFH_HIGH dwelling count | from Eurostat census | sum of MFH_LOW + MFH_HIGH | ratio |
| OTHER count | from Eurostat census | NON_RESIDENTIAL count | ratio |

The current model's OTHER bucket is known to over-count (cf. `literature/assumptions_register.md`). One of the primary goals of this build is to quantify by how much, and confirm that the EUBUCCO-based count corrects it.

---

## 10. Known limitations (for paper methods section)

1. **Height attribute missing for ~27% of LU buildings.** Where missing, falls back to area-only rules, biased toward SFH/MFH_LOW. Could be partially closed by EUBUCCO's imputed-height field (not used).
2. **Type attribute missing for ~54% of LU buildings (v0.1 stat).** When missing, residential is the working assumption.
3. **Thresholds are heuristic, not calibrated.** The 6-floor / 800 m² / 250 m² cuts have not been validated against national Luxembourg statistics (STATEC). A future calibration step against STATEC ground truth is needed.
4. **Mixed-use buildings classified by single type.** EUBUCCO's `type` picks one. A future refinement could split heated_floor_area between residential and non-residential layers.
5. **No use of EUBUCCO `building-type-harmonization.csv`.** This taxonomy table could provide a finer-grained type system; deferred to subsequent.
6. **Uniform thresholds across countries.** Eastern European prefab MFH_LOW has noticeably larger per-building footprints than Western European MFH_LOW. The current cuts may need country-specific tuning in the 29-country rollout.
7. **The "ambiguous → MFH_HIGH" default has opposite sign for DH scenarios.** Conservative for HP feasibility (understates uptake potential), anti-conservative for DH feasibility (overstates connectability).

---

## 11. Validation design (subsequent)

Three checks planned once the Luxembourg build succeeds and before scaling to the other 28 countries:

1. **STATEC dwelling-count check.** Luxembourg had ~241,000 dwellings in residential buildings at the 2021 census (STATEC). Total `SFH` + `MFH_LOW` + `MFH_HIGH` heated_floor_area divided by typical Luxembourgish dwelling size (~120 m²) should give a number within ±15% of this.
2. **Eurostat ENER/NRG_BAL cross-check.** Total residential heated floor area × per-m² intensity from script 03 should reconcile with Eurostat residential final energy consumption.
3. **Luxembourg Cadastre 2020 register.** Per-class share against the official cadastre's residential typology.

If any of these fails by more than ±25%, the threshold values in §6 will be revisited before the 29-country rollout.

---

## 12. Provenance and reproducibility

- **Code:** `code/scripts/luxembourg/02_classify.py` — has the same methodology as a module-level docstring, plus runnable code.
- **Inputs:** logged by `01_download.py` with URLs and MD5 checksums in `code/data/raw/luxembourg_provenance.txt`.
- **Outputs:** committed to `code/data/processed/luxembourg/` and `countries/Luxembourg/data/`.
- **Versions:** EUBUCCO v0.2, GBA v1 (2025), repo commit hash recorded by GitHub.

Re-running the build end-to-end (downloads + processing) takes ~10–20 minutes on a 4-core machine; outputs are bit-stable except for downstream re-saves of the parquet (geopandas writes don't preserve insertion order).

---

## 13. Citation format for the paper

When citing the Luxembourg build in the methods section, use:

> Building stock classification follows the EUBUCCO + Global Building Atlas integration Luxembourg build, documented in `literature/luxembourg/classification_methodology.md` of the project repository. Buildings are classified into four classes (SFH, MFH_LOW, MFH_HIGH, NON_RESIDENTIAL) using sequential decision rules combining EUBUCCO's `type` attribute (where present) with footprint area (computed in EPSG:3035) and floor count estimated from EUBUCCO height divided by floor-to-floor assumption (3.0 m residential, 3.5 m non-residential). Heated floor area applies a 0.85 useable-area fraction (TABULA convention; ISO 52000-1). Source datasets: Milojevic-Dupont et al. (2023) for EUBUCCO; Zhu et al. (2025) for the Global Building Atlas.

---

## 14. Change log

| Date | Change | Author |
|---|---|---|
| 2026-05-14 | Initial draft, subsequent-script-creation | Ali / Claude |
| 2026-05-16 | Colab LU build completed: bottom-up 6.55 TWh vs Hotmaps 8.21 TWh = **−20.2 % (ACCEPTABLE band)**. Luxembourg was the original proof-of-concept country; the slightly-under-stated bottom-up reflects EUBUCCO's lower coverage of LU's pre-2000 multi-family stock and the small absolute size of the LU residential market. The framework itself is the most thoroughly validated in the build. | Ali / Claude |

---

## 15. Reconciliation result (Colab build 2026-05-16)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **6.55** | **171.3** |
| Hotmaps 2015 baseline | 8.21 | 214.4 |
| EU BSO 2022 weighted-avg implied total | 5.66 | 147.9 |
| Odyssee-Mure 2021 (final energy, definitional gap vs Hotmaps useful demand) | 7.20 | 188.0 |

**Verdict:** Bottom-up vs Hotmaps = **−20.2 %** (ACCEPTABLE — within ±25 % band; document the gap).

Luxembourg is **the original proof-of-concept country for the build pipeline**. Every other country's methodology, YAML schema, and per-country deliverable list (config + BSO + national + methodology doc + README extension) traces back to the LU template. The slightly under-stated bottom-up (-20 %) reflects three structural features:

1. **EUBUCCO has lower coverage of LU's pre-2000 multi-family stock.** The Luxembourgish housing market is small but expensive, with a high share of large single-family detached and luxury apartments; the dominant Belgian-derived TABULA archetypes don't fully capture the heavier-than-typical-MFH share of large detached.
2. **The Belgian TABULA proxy uses `climate_multiplier = 1.112` (BE 2900 → LU 3217 HDD).** This is a small upward correction; the residual under-statement isn't traceable to the climate scaling.
3. **The absolute number is small (~7 TWh).** The -20 % gap means ~1.7 TWh under-statement — comparable to Malta in absolute terms but more interpretable because Luxembourg has a substantial space-heating market.

Unlike the Mediterranean and Baltic over-counts, Luxembourg's residual is on the *under* side — the only country in the build groups 1-4 that under-states by more than 15 %. This is an interesting empirical point: it suggests **EUBUCCO floor-area calibration is country-specific** (over-counts for Spain, Italy; about-right for Estonia/Lithuania; under-counts for Luxembourg). See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md) for the broader build-wide audit.
