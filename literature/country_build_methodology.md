# Country-build pipeline — methodology

**Status:** Implemented and run for Luxembourg (country #1), France
(country #2) and Finland (country #3, a Sweden-proxy build).
**Code:** `code/scripts/country_build/` (`01_download.py` → `04_diagnostics.py`),
`code/src/CountryConfig.py`, `code/data/country_config/{cc}.yaml`.
**Per-country numbers and their sources:** Section 7 below, plus
`literature/{country}/classification_methodology.md`,
`literature/intensity_source_methodology.md` and `literature/assumptions_register.md`.

This document explains the *generic* method. It is country-agnostic: one set of
scripts, one YAML config per country. A country is selected with `--country`.

---

## 1. Overview

The pipeline turns the EUBUCCO v0.2 open building-stock dataset into a
bottom-up estimate of residential space-heating + hot-water demand for a
country, broken down by building class and construction vintage, and reconciles
it against three independent published benchmarks.

```
01_download.py     EUBUCCO NUTS2 parquet partitions  (S3, ODbL, anonymous)
        |
02_classify.py     per-building class + floors + heated floor area
        |          -> {CC}_buildings_classified.parquet
        |             {CC}_aggregated_NUTS3.csv
        v
03_heat_intensity  per-building heat intensity + annual demand
        |          -> {CC}_buildings_with_heat_demand.parquet
        |             {CC}_heat_intensity_summary.csv
        |             {CC}_reconciliation_with_hotmaps.csv
        v
04_diagnostics.py  8-page diagnostic / visualisation PDF
                   (run in VS Code, not in the Colab notebook)
```

Scripts 01–03 run on Google Colab (the heavy steps); script 04 (visualisation)
runs locally in VS Code. Heavy countries are processed with `--per-partition`
streaming so they fit a standard ~12 GB runtime — France is ~53 M buildings.

Every country-specific value lives in `code/data/country_config/{cc}.yaml`,
loaded and validated by `CountryConfig.py`. The scripts contain **no** country
constants.

---

## 2. Script 01 — Download

Downloads the EUBUCCO v0.2 building parquet for each NUTS2 partition of the
country (1 for Luxembourg, 22 for metropolitan France) from `s3.eubucco.com`.
Anonymous, ODbL-licensed, resumable (re-running skips files already present).
Raw parquets are routed to `EUHB_RAW_DIR` (a Google Drive folder, outside the
repo) and are gitignored — they are regenerable.

---

## 3. Script 02 — Classify

For every building EUBUCCO supplies a footprint polygon, a height, a native
floor count, a type string and (often) a construction year. Script 02 derives:

**Footprint area** — polygon area in EPSG:3035 (ETRS89-LAEA, equal-area).

**Floors** — controlled by `classification.floor_source` in the YAML:
- `eubucco` — use EUBUCCO's own `floors` column (roof-aware, modelled by
  EUBUCCO with confidence bounds). This is the recommended setting.
- `estimate` — legacy `round(height / floor_height)`, ~3.0 m residential /
  3.5 m other. It over-counts floors by ~40 % because EUBUCCO `height` is
  roof-inclusive (a 1-storey pitched-roof house reads as 2 storeys), which
  inflated heated area and heat demand. Kept only as a per-building fallback
  where the native value is missing.

**Building class** — four classes, assigned by sequential first-match rules:

| Rule | Condition | Class |
|---|---|---|
| 1 | EUBUCCO `type` starts with "non-" | NON_RESIDENTIAL |
| 2 | floors ≥ 6 and footprint ≥ 800 m² | MFH_HIGH |
| 3 | floors ≤ 2 and footprint < 250 m² | SFH |
| 4 | 3 ≤ floors ≤ 5 | MFH_LOW |
| 5 | otherwise (ambiguous large building) | MFH_HIGH |

SFH = single-family house; MFH_LOW = low-rise apartment block (3–5 floors);
MFH_HIGH = mid/high-rise (≥6 floors); NON_RESIDENTIAL = commercial / industrial
/ public. The thresholds follow TABULA / EU Building Stock Observatory / Hotmaps
typologies; full justification is in the `02_classify.py` docstring and
`literature/{country}/classification_methodology.md`.

**Heated floor area** = footprint × floors × `useable_area_fraction` (0.85).
NON_RESIDENTIAL is carried with zero heated area — non-residential demand is
out of scope for this build (a flagged limitation).

Results are aggregated to NUTS3. For large countries `--per-partition` streams
one NUTS2 region at a time so peak memory stays at ~one partition.

---

## 4. Script 03 — Heat intensity

Attaches a per-m² annual heat intensity (kWh/m²/yr) to every building and
multiplies by heated floor area to get annual demand.

1. **Vintage cohort** from `construction_year`:
   `pre-1945 | 1946-1970 | 1971-1990 | 1991-2010 | 2011-2020 | post-2020`,
   else `unknown`.
2. **Base intensity** from the TABULA per-class × per-cohort space-heating
   value for that (class, cohort).
3. **Climate correction** — multiply by `climate_multiplier` = HDD(country) /
   HDD(TABULA source). 1.0 when TABULA data is for the country itself.
4. **Retrofit blend** — multiply by
   `blend = share_original·1 + share_standard·factor_standard
   + share_advanced·factor_advanced`,
   the stock-share-weighted average insulation state.
5. **Domestic hot water** — add a class-specific DHW intensity (climate-
   insensitive, so not scaled by HDD).
6. **Unknown-cohort fallback** — buildings with no construction year get a
   class-level intensity that is the EU BSO stock-weighted average across
   cohorts. Where cohort coverage is low (e.g. Luxembourg, ~0 %) the result is
   effectively this fallback rather than a true per-vintage calculation — this
   must be disclosed.
7. **NON_RESIDENTIAL** — a flat intensity is configured but contributes 0 TWh
   because heated area is 0 (see §3).

Intensity = `base · climate_multiplier · blend + DHW`. The computation is
vectorised and streamed in batches, so it is memory-safe at country scale.

---

## 5. Script 04 — Visualisations

Builds the 8-page diagnostic PDF (headline reconciliation, class × cohort heat
map, intensity-vs-vintage curves, cohort-coverage transparency, sensitivity
tornado, method comparison, class-level reconciliation, vintage histogram).
It consumes only the CSV/parquet outputs of 02–03 and is run locally in VS Code
(the "Visualizations (country build)" task), not inside the Colab notebook.

---

## 6. Reconciliation

The bottom-up residential total is reported **as-is**, never calibrated, beside
three independent benchmarks:

- **Hotmaps** — national residential space-heating baseline.
- **EU BSO** — per-cohort intensities × national stock weights × our
  residential floor area (an implied total).
- **Odyssee-Mure** — back-calculated national residential figure.

Acceptance target: bottom-up "residential only" within **±25 %** of Hotmaps
(±15 % is the tighter "consistent" tier). A gap outside ±25 % is treated as a
methodology finding to investigate, not a number to silently correct.

---

## 7. Country-specific parameters and their sources

All values below are in `code/data/country_config/{cc}.yaml`; the YAML carries
inline source citations and mirrors `code/data/raw/{cc}_national/`.

| Parameter | Luxembourg (LU) | France (FR) | Finland (FI) | Source |
|---|---|---|---|---|
| EUBUCCO partitions | 1 (LU00) | 22 (metropolitan) | 5 (FI19/FI1B/FI1C/FI1D/FI20) | EUBUCCO v0.2, Milojevic-Dupont et al. 2023 |
| TABULA source | Belgium (proxy) | France (direct) | Sweden (proxy) | VITO 2011 (BE); TABULA-FR / Rochard 2015 (FR); Sweden TABULA brochure (SE) |
| HDD (degree-days/yr) | 3217 | 2183 | 5321 | Eurostat `nrg_chdd_a`, 2018–2022 avg |
| Climate multiplier | 1.112 (3217/2894 vs BE) | 1.000 (direct) | 1.055 (5321/5043 vs SE) | HDD ratio |
| Retrofit shares (orig/std/adv) | 0.55 / 0.35 / 0.10 | 0.305 / 0.609 / 0.086 | 0.55 / 0.35 / 0.10 (placeholder) | LU: Odyssee-Mure 2024 + STATEC 2021; FR: SDES 2025 DPE distribution; FI: placeholder, no Finnish source |
| Retrofit factors (std/adv) | 0.65 / 0.35 | 0.57 / 0.35 | 0.74 / 0.49 | LU: TABULA Belgium refurb scenarios; FR: TABULA-FR Rochard 2015 Tableau 4; FI: Sweden TABULA brochure refurb scenarios |
| Retrofit blend | 0.813 | 0.6822 | 0.858 | Computed from shares × factors |
| DHW intensity (SFH/MFH) | 22 / 19 | 10 / 15 | 16 / 17 | LU: TABULA Belgium; FR: TABULA harmonised `q_w_nd`; FI: Sweden TABULA brochure |
| Non-residential intensity | 140 | 120 | 130 (placeholder) | LU: EU BSO non-res avg; FR: CEREN tertiary 240 × ~50 % heating share; FI: placeholder |
| Floor source | eubucco | eubucco | eubucco | EUBUCCO v0.2 native `floors` column |
| Hotmaps benchmark (TWh) | 8.27 | 515.1 | 78.14 | Hotmaps Toolbox via `building_stock_nuts3.csv` |
| Odyssee-Mure benchmark (TWh) | 7.2 | 310 | 42 | Odyssee-Mure country profiles; FI uses Statistics Finland 2023 (the national source behind the Odyssee-Mure FI series) |

Finland is a TABULA **proxy** country: it has no national TABULA typology, so
its residential heat intensities are taken from the Sweden TABULA brochure and
climate-corrected by the FI/SE HDD ratio — the same proxy pattern Luxembourg
uses with Belgium. Several Finnish parameters (retrofit shares, non-residential
intensity, the EU BSO and Odyssee-Mure benchmarks) could not be sourced and
are placeholders; they are tracked in `fi.yaml._meta.needs_verify_summary` and
`literature/finland/classification_methodology.md`.

Detailed provenance: `literature/luxembourg/classification_methodology.md`,
`literature/france/classification_methodology.md`,
`literature/finland/classification_methodology.md`,
`literature/intensity_source_methodology.md`, `literature/assumptions_register.md`.

---

## 8. Known limitations

1. **Non-residential demand is out of scope** — NON_RESIDENTIAL buildings carry
   zero heated area, so the bottom-up total is residential-only.
2. **Construction-year coverage varies** — France ~72 %, Luxembourg ~0 %,
   Finland ~2 %. Where it is low the result is fallback-driven, not
   per-vintage.
3. **EUBUCCO counts building polygons, not dwellings** — garages, sheds and
   outbuildings can be classified SFH, which somewhat inflates residential
   floor area even with the EUBUCCO-floors fix.
4. **Single retrofit blend per country** — one stock-weighted blend is applied
   to all vintages; a per-cohort retrofit-factor scheme is a possible refinement.
5. **TABULA proxying** — countries without national TABULA data use a
   climate-corrected neighbour (Luxembourg uses Belgium; Finland uses Sweden).
   For Finland this also means MFH_LOW and MFH_HIGH carry identical intensities,
   because the Sweden TABULA typology has only one multi-family class.

---

## 9. Results so far

| Country | EUBUCCO buildings | Residential heated area | Bottom-up demand | vs Hotmaps |
|---|--:|--:|--:|--:|
| Luxembourg | 186,171 | 0.04 bn m² | 6.60 TWh | −20.2 % |
| France | 52,610,604 | 4.40 bn m² | 573.8 TWh | +11.4 % |
| Finland | 6,633,364 | 0.53 bn m² | 68.9 TWh | −11.8 % |

All three within the ±25 % target band, all using `floor_source: eubucco`;
Finland and France are also inside the tighter ±15 % "consistent" tier.
Per-country detail is in `countries/Luxembourg/README.md`,
`countries/France/README.md` and `countries/Finland/README.md`. Note that
Finland's EUBUCCO construction-year coverage is near-zero, so its result is
fallback-driven rather than per-vintage (see §8 limitation 2).

---

## 10. Adding the next country

1. Create `code/data/country_config/{cc}.yaml` (copy `fr.yaml`, fill in the
   Section 7 parameters with cited sources).
2. Add `code/data/raw/tabula/{cc}_intensities.csv` and
   `code/data/raw/eu_bso/{cc}_intensity.csv`.
3. Copy `notebooks/france.ipynb`, set the `COUNTRY` variable.
4. Run 01–03 on Colab, 04 in VS Code, reconcile.
5. Document the country in `literature/{country}/` and
   `countries/{Country}/README.md`.
