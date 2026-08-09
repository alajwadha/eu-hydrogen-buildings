# Switzerland — building classification & heat-intensity methodology

Build group 7 (UK + CH; non-EU additions). Companion to `code/data/country_config/ch.yaml`.

## 1. Status and how CH differs from the EU-27 builds

Switzerland is a non-EU country and **not a TABULA-12 participant**. **Austria (AT)** is used as the climate-corrected TABULA proxy — the closest TABULA country by construction tradition (shared SIA/OIB-aligned Alpine-continental building code, same construction-period bands, similar cold climate). Swiss heat intensities are AT-derived, scaled by `HDD_CH / HDD_AT = 3150 / 3050 = 1.0328`.

**The critical structural difference:** per Milojević-Dupont et al. (2023) Table 1, the Swiss EUBUCCO source (swisstopo government footprints) has **~100 % height coverage but ~0 % `construction_year` and ~0 % building `type`**. Footprint geometry is excellent, but cohorts and the SFH/MFH split **cannot be read from EUBUCCO** — essentially every Swiss building falls in the `unknown` cohort. The Swiss bottom-up is therefore **entirely fallback-dominated**: it is driven by the stock-weighted intensity computed from `ch_intensity.csv`. The `stock_pct_ch` weights in that file are the most load-bearing numbers in the CH build.

## 2. Data sources

- **EUBUCCO v0.2** (CH NUTS2 partitions CH01-CH07; swisstopo government footprints; 26 NUTS3). Geometry good; age/type absent.
- **Heat intensities (AT proxy, `at_intensities.csv`):** Austria TABULA (AEA / Lechner et al. 2011) for the per-cohort SH **shape**, scaled by the CH/AT HDD ratio. Swiss-direct evidence anchors the national **total** as a cross-check: Streicher et al. (2019, EPFL) "SwissRes" archetype model (54 archetypes from >25,000 GEAK/CECB+ certificates; SFH ~41 % above MFH; pre-1980 ~70 % of SH energy); SIA 380/1 norm; Prognos/TEP BFE Gebäudeparkmodell. AT-proxy band shape is PROVISIONAL — verify against SwissRes.
- **Climate:** Eurostat `nrg_chdd_a` reports CH; 2018-2022 mean ≈ 3150 HDD base 15 °C (NEEDS_VERIFY; ~3000-3300, strong altitude gradient — mid-plateau ~2800-3200, alpine cantons far higher).
- **Retrofit shares (0.58 / 0.32 / 0.10):** Das Gebäudeprogramm (CO2-levy funded) + cantonal funding + GEAK Plus; ~1 %/yr renovation rate; pre-1980-dominated stock (~70 %); ~64 % still oil/gas heated. Factors PROVISIONAL (AT proxy).
- **Reconciliation:** **77.90 TWh**, sum of `heat_2015_MWh` across all 26 CH NUTS3 rows in `building_stock_nuts3.csv` (verified 2026-05-21). NOTE: the public Hotmaps Toolbox covered EU28 only, but the repo `building_stock_nuts3.csv` carries CH rows — used as the reconciliation anchor for consistency with the other countries. Cross-check vs BFE Gesamtenergiestatistik 2022 residential Raumwärme ~200 PJ (~56 TWh, final-energy basis).

## 3. Occupancy / heated-base note

CH vacancy is very low (Leerwohnungsziffer ~1 %), so occupancy is a minor factor. The larger consideration is the large alpine **Zweitwohnungen** stock (~10 % of dwellings, concentrated in Valais/Graubünden/Ticino under the Lex Weber 20 % cap). These are **partially heated** (frost protection year-round + ski-season use), so they are NOT excluded — but a partial heating derate in high-second-home NUTS3 regions is a candidate refinement. Per the area policy, **no `area_correction` is applied in this initial build**; sized only after the first Colab run.

## 4. Verification status

Verified 2026-05-21: NUTS2/NUTS3 code lists (CH01-CH07; 26 CH0xx), Hotmaps benchmark (77.90 TWh), EUBUCCO CH government source, input-chain load + `build_intensity_lookup` (mult 1.0328, blend 0.828; class fallbacks SFH 180 / MFH_LOW 141 / MFH_HIGH 129 kWh/m²).

NEEDS_VERIFY: exact CH HDD 2018-2022 mean; AT-proxy band shape vs Streicher 2019 SwissRes; retrofit shares/factors; **EUBUCCO CH `construction_year` ~0 % → bind RegBL/GWR age + type distribution** (the single most important refinement; the result is otherwise pure fallback); `census_floor_area.eubucco_mm2` + ratio (pending first build).

## 5. Change log

- 2026-05-21: CH package created (group 7). AT proxy (mult 1.0328); Hotmaps 77.90 TWh; flagged as fallback-dominated due to absent EUBUCCO construction-year; area/occupancy correction deferred.
