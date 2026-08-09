# Estonia — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-19.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country EE`).
**Config:** `code/data/country_config/ee.yaml`.

This document describes how the buildings-model methodology developed for Luxembourg and France is applied to Estonia — one of the three Baltic states in build group 1 (DE + EE, LV, LT).

**The headline fact:** Estonia is **not a TABULA country**. Its residential heat intensities are **Poland-derived** — extracted from the Polish TABULA typology and climate-corrected by the Estonia/Poland heating-degree-day ratio. This is the same proxy methodology Luxembourg uses with Belgium and Finland with Sweden. Every Estonia-touching number that depends on a building intensity is, at root, a Polish number scaled to Estonia's colder climate.

---

## 1. Methodology relative to Luxembourg and France

Estonia is methodologically a **proxy country**, so it follows the Luxembourg branch (proxy + climate correction), not the France/Germany branch (direct TABULA):

| Element | Luxembourg | Estonia |
|---|---|---|
| TABULA dataset | Belgium (proxy) | **Poland (proxy)** |
| Climate correction | HDD_LU/HDD_BE = 1.112 | HDD_EE/HDD_PL = **1.2625** |
| Retrofit factors source | TABULA Belgium | **TABULA Poland** |
| EUBUCCO partitions | 1 (LU00) | 1 (EE00) |
| NUTS3 regions | 1 (LU000) | 5 |
| Hotmaps reconciliation | single LU000 row | sum across all EE rows (13.27 TWh) |

Everything else — the 4-class taxonomy, the floor-height assumptions, the 0.85 useable-area fraction, `floor_source: eubucco`, the per-cohort × per-class intensity lookup with stock-weighted fallback, the multi-source reconciliation, the 8-page diagnostic PDF — is identical to Luxembourg.

---

## 2. Data sources

### 2.1 EUBUCCO
EUBUCCO v0.2 partitions buildings by NUTS2 (NUTS 2016). Estonia is a single NUTS2 region, **EE00**.

**NUTS3 vintage caveat.** Estonia's NUTS3 codes were **renumbered at the NUTS 2021 revision**. EUBUCCO v0.2 uses NUTS 2016, so `ee.yaml` lists the NUTS 2016 codes (EE001/EE004/EE006/EE007/EE008). The repo GISCO file (NUTS 2021) instead carries EE001/EE004/EE008/EE009/EE00A — those must **not** be used for the EUBUCCO join. Hotmaps reconciliation sums all rows with country == EE, so the vintage mismatch does not affect the benchmark. Flagged `NEEDS_VERIFY` — spot-check the EUBUCCO EE partition `region_id` codes before the run.

### 2.2 TABULA — Poland as proxy (the core methodological choice)

**Estonia has no national TABULA typology.** A proxy country is required.

**Poland is chosen as the proxy** because:
1. Estonia's residential stock is dominated by Soviet-era prefabricated large-panel concrete apartment blocks ("panel houses") plus rural timber houses. Poland's TABULA typology is the only published TABULA dataset that explicitly carries the Soviet/Comecon-era large-panel ("wielka płyta") apartment class — the same industrialised construction lineage as the Estonian panel stock.
2. Shared post-war central-planning construction norms and envelope practice.
3. Poland is the closest panel-bearing TABULA country to the Baltics, keeping the climate correction bounded.

**Sweden was considered and rejected as the primary proxy.** Sweden is the proxy Finland uses, is the only TABULA country colder than Estonia, and its TABULA file already exists in the repo. But Poland was chosen because (a) it gives **methodological consistency across all three Baltic states** — Latvia and Lithuania clearly need Poland for their Soviet-panel-dominated stock, and Estonia has the same profile; (b) the Polish typology carries the large-panel apartment class explicitly, which Sweden's *miljonprogram* stock only loosely approximates; (c) climate-wise the two are roughly equidistant from Estonia (Sweden ~20 % colder, Poland ~26 % milder), so Sweden offers no decisive climate advantage. Estonia is the **coldest of the three Baltics**, so it carries the largest HDD uplift in the group.

**Primary source:** Polish TABULA Scientific Report (NAPE). Extraction: `code/data/raw/tabula/pl_intensities.csv` — the file header documents the EK→net-space-heating derivation (the Polish report publishes only final/delivered energy EK, so the net space-heating values are derived) and the class/cohort mappings.

### 2.3 Climate (HDD)
`climate_multiplier = HDD_EE / HDD_PL`. Source: Eurostat `nrg_chdd_a` (base 15 °C, JRC AGRI4CAST), 5-year mean 2018–2022:
- Estonia: 4070.60 / 3890.15 / 3563.54 / 4289.96 / 4124.88 → **mean 3987.8**
- Poland: 3126.18 / 2954.00 / 3011.03 / 3497.15 / 3205.03 → **mean 3158.7**
- `climate_multiplier = 3987.8 / 3158.7 = 1.2625`.

**Note on a corrected research error.** The first Estonia research dossier reported an Estonia/Poland HDD ratio of 1.04; that was traced to a mislabelled column (Latvia's HDD series printed under a "Poland" header). The correct ratio, 1.2625, is used here.

### 2.4 Retrofit shares and factors
**Retrofit factors** are the Poland TABULA typology-averaged refurbishment ratios: **standard 0.63**, **advanced 0.50** of existing-state space-heating need.

**Retrofit shares** (0.85 original / 0.10 standard / 0.05 advanced) are a **modelling assumption**. Estonia's residential stock is overwhelmingly unrenovated: of ~22,600 apartment buildings only ~1,000 have been deeply renovated under the KredEx programme (~4–5 %), and energy-performance class A/B/C has been awarded to only ~9 % of certified apartment buildings. The standard/advanced sub-split is an assumption — flagged.

**Resulting blend factor:** 0.85 × 1.00 + 0.10 × 0.63 + 0.05 × 0.50 = **0.938**.

### 2.5 DHW intensity
DHW is added per building from the `pl_intensities.csv` DHW column (Poland-proxy values, ~22–30 kWh/m²/yr).

### 2.6 Non-residential intensity
Estimate, 130 kWh/m²/yr (Estonian LTRS 2020 office space heating), `NEEDS_VERIFY`. Contributes 0 TWh — NON_RESIDENTIAL carries zero heated area.

### 2.7 Reconciliation benchmarks
| Source | Value (TWh/yr) | Year | Status | Notes |
|---|--:|---|---|---|
| Hotmaps | **13.27** | 2015 | verified | Sum across all EE NUTS3 rows in `building_stock_nuts3.csv`, all-classes. |
| Odyssee-Mure | 7.7 | 2023 | estimate | EE residential space-heating final energy ~0.665 Mtoe; final-energy basis, recent warm year. |
| EU BSO | 9.0 | 2020 | anchored | Anchored to the Estonian LTRS pre-2000-stock heating estimate; BSO portal not retrievable. |

The Hotmaps useful-demand, cold-year figure sitting above the Odyssee-Mure recent-year final-energy figure is expected; the definitional gap should be stated in the paper.

---

## 3. NUTS3 spatial join
Estonia has 5 NUTS3 regions, so `02_classify.py` performs a spatial join (or uses the EUBUCCO `region_id` column where present).

---

## 4. Verification status (2026-05-19)

### Verified
1. EE00 single NUTS2 partition; 5 NUTS3 codes (NUTS 2016 vintage for EUBUCCO).
2. HDD EE = 3987.8, HDD PL = 3158.7 (Eurostat `nrg_chdd_a` 2018–2022 means); `climate_multiplier = 1.2625`.
3. Poland TABULA intensities — `code/data/raw/tabula/pl_intensities.csv`.
4. Retrofit factors 0.63 / 0.50 — Polish TABULA typology-averaged refurbishment ratios.
5. Hotmaps EE total = 13.27 TWh — computed from `building_stock_nuts3.csv`.
6. Config validates; full TABULA + BSO + national input chain loads cleanly (unknown-cohort fallback SFH ≈ 215 kWh/m²/yr).

### Still needs verification
1. **Retrofit shares** (0.85/0.10/0.05) — modelling assumption; no published three-state envelope distribution for Estonia.
2. **NUTS3 vintage** — EUBUCCO v0.2 uses NUTS 2016 (EE001/004/006/007/008); spot-check the EUBUCCO EE partition `region_id` codes.
3. **Non-residential intensity** (130) — estimate; contributes 0 TWh.
4. **EU BSO benchmark** — anchored estimate, BSO portal not retrievable.
5. **Poland TABULA net-SH values** — derived from the Polish report's EK (final-energy) figures, ±15–20 % uncertainty; see the `pl_intensities.csv` header.

---

## 5. Change log

| Date | Change | By |
|---|---|---|
| 2026-05-19 | Initial draft: Estonia built as a build-group-1 country, a TABULA **proxy** country using Poland as the proxy. Created `ee.yaml`, `eu_bso/ee_intensity.csv`, `ee_national/ee_climate_retrofit.csv`; shares `code/data/raw/tabula/pl_intensities.csv` with Latvia and Lithuania. climate_multiplier 1.2625 from Eurostat HDD. Sweden documented as the considered-but-rejected alternative proxy. Retrofit factors 0.63/0.50 from the Polish TABULA; retrofit shares a modelling assumption from KredEx renovation reporting. | Ali / Claude |
| 2026-05-19 | Colab G1 run completed: bottom-up 23.74 TWh vs Hotmaps 13.27 TWh = **+78.8 % (INVESTIGATE band)**. The gap is almost entirely intensity-driven (EE floor-area aligns within ~15 % of population × census m²/dwelling). This is the second-worst Baltic over-count after Lithuania (+124 %); both inherit the Polish TABULA's EK-derivation bias amplified by upward climate scaling to cold Baltic conditions. | Ali / Claude |

---

## 6. Reconciliation result (Colab build 2026-05-19)

| Source | Value (TWh/yr) | kWh/m²/yr |
|---|--:|--:|
| **Bottom-up: residential only** | **23.74** | **207.2** |
| Hotmaps 2015 baseline | 13.27 | 116.0 |
| EU BSO 2022 weighted-avg implied total | 23.61 | 206.0 |
| Odyssee-Mure 2022 (final energy, definitional gap vs Hotmaps useful demand) | 7.70 | 67.2 |

**Verdict:** Bottom-up vs Hotmaps = **+78.8 %** (INVESTIGATE — outside ±25 % band).

Estonia is the **second-worst Baltic over-count** in the build (after Lithuania at +124 %). The decomposition is unusual relative to the Mediterranean cases:

- **EUBUCCO floor area is roughly right** — our area divided by population × ~75 m²/dwelling census gives an over-count of only ~15 %. **[SUPERSEDED 2026-05-21 — THIS CLAIM IS WRONG.** It used population × m²/dwelling (a unit error, the same one corrected for Lithuania). The correct comparison is *households/dwellings* × m²/dwelling: Statistics Estonia REL 2021 records 557,146 occupied + 175,690 vacant dwellings ≈ 51 Mm² vs EUBUCCO 114.5 Mm² — a ~2.2× over-count. See §7.2 and [eubucco_census_area_audit.md](../eubucco_census_area_audit.md).]
- **Intensity is the main driver** — bottom-up at 207.2 kWh/m² over-states Hotmaps-implied (~116 kWh/m² on our area) by ~80 %. **[SUPERSEDED — the over-count is split between intensity (class-mix, §7.1) AND area/occupancy (§7.2); it is NOT intensity-only.]**

The root cause is the **Polish TABULA's EK (final-energy) derivation methodology**, which over-states net space-heating need when transposed to Baltic climates (HDD 3988 for EE) via climate_multiplier 1.2625. The Polish report does not publish TABULA-harmonised net SH; the `pl_intensities.csv` values are derived by deducting DHW from EK figures and applying period-typical heating-system efficiencies (header notes ±15-20 % uncertainty). Compounding factors include the Polish wielka płyta typology being structurally different from Estonia's predominantly wooden detached and Soviet-era panel stock.

**Hotmaps remains the recommended residential heat-demand benchmark for Estonia** for any analysis requiring a single national number. The refinement path is a national EE-typology re-derivation from KredEx / Statistics Estonia / Tallinn University of Technology archetype work. See [climate_reference_hdd_audit.md](../climate_reference_hdd_audit.md).

---

## 7. Academic refinement path (research 2026-05-20)

**Highest-leverage academic fix (near-term, implementable now):** **class-mix proxy — SE for SFH + PL for MFH.** Estonia's stock is ~28 % wooden detached (puumaja), ~52 % panel-block MFH (Soviet serii), ~20 % brick MFH. The Polish wielka-płyta TABULA matches panel-block well but over-states wooden-SFH and brick-MFH intensities when climate-scaled upward to Baltic conditions. Sweden's TABULA carries cold-climate wooden-detached archetypes at comparable HDD (HDD_EE/HDD_SE ≈ 1.06) — already in the repo as `se_intensities.csv` (used by the FI proxy chain). Methodological precedent: Kuusk, Kalamees et al. (2014) — "Estonian typology of residential buildings — a TABULA-style classification" explicitly establishes the SE-for-Estonian-SFH match. **Expected gap shrink:** EE +79 % → ~+30-40 % (LIKELY band).

**Why LV works and EE doesn't:** Latvia at +20 % (ACC) is the empirical control. Same PL proxy methodology, but LV stock is ~63 % panel-block (vs EE 52 %), and the residual mismatch is smaller. This confirms the typology hypothesis.

**Longer-term refinement:** Baltic-direct TABULA matrix from TalTech / KredEx publications (Kalamees, Kurnitski, Jylhä, Tuhkanen; Kalamees & Kurnitski 2006 wooden SFH; KredEx renovation reporting for ~1,000+ apartment buildings with measured pre/post EK). Implementation requires a small `CountryConfig.py` schema extension for per-class proxy. Full citations and the Baltic-cluster decomposition table are in [`inv_countries_academic_refinements.md`](../inv_countries_academic_refinements.md) — Baltic cluster section.

### 7.1 Applied this session (2026-05-20): class_mix proxy — SE for SFH, PL for MFH

The schema extension above is no longer deferred — it was added to `CountryConfig` this session as the optional `tabula.class_mix` field, validated, and wired into `03_heat_intensity.py`. EE is the first country to use it. LT uses it too.

**Configuration:**
- **SFH:** Swedish TABULA Enfamiljshus typology (`se_intensities.csv`), climate-scaled by HDD_EE / HDD_SE_zone3 = 3987.8 / 3500 = **1.139**. Swedish southern (zone-3) typology covers timber-framed cold-climate detached houses, structurally close to Estonian *puumaja*.
- **MFH_LOW + MFH_HIGH:** Polish TABULA (`pl_intensities.csv`) retained, climate-scaled by HDD_EE / HDD_PL = 3987.8 / 3158.7 = **1.2625** (unchanged from the pre-class-mix configuration). Polish *wielka płyta* typology matches the Soviet-era industrialised panel-block MFH that dominates the Baltic apartment-block stock.

**Empirical effect on the lookup:** local smoke-test (`build_intensity_lookup` on EE config) shows the SFH fallback intensity drops from the all-PL-derived 195.8 kWh/m² to the SE-derived **180.0 kWh/m²** (~−8 %), with MFH unchanged. Smaller absolute shift than the audit projection had suggested — the SE-zone-3 reference HDD chosen (3500) is at the warm end of the SE TABULA reference range; the FI proxy chain uses the much higher SE national HDD (5043) and gets correspondingly different multipliers. If the EE result post-rebuild is still over Hotmaps, the next test would be sensitivity to the SE reference HDD assumption.

**This is not a Hotmaps calibration knob.** The class-mix decision is grounded in the published Kuusk-Kalamees Estonian typology paper and the Polish TABULA's explicit large-panel MFH match. The climate multipliers trace to Eurostat `nrg_chdd_a`.

**Status:** the Baltic-direct TABULA matrix from TalTech / KredEx (Kalamees & Kurnitski 2006 wooden SFH; KredEx renovation pre/post measured EK data) remains the longer-term refinement and would replace both proxy files entirely. The class-mix proxy is methodologically independent of that refinement and would naturally retire once the EE-direct matrix is extracted.

**Sources:**
- Kuusk, K., Kalamees, T. (2014) "Estonian typology of residential buildings — a TABULA-style classification", *Procedia Engineering* / IBPSA-Nordic.
- Kalamees, T., Kurnitski, J. (2006), Estonian wooden detached houses thermal-performance baseline.
- KredEx (2020+) renovation programme reporting (~1,000 apartment buildings with measured pre/post heat consumption).
- Polish TABULA Scientific Report (NAPE) — *wielka płyta* MFH archetype.
- Swedish TABULA National Typology Brochure — Enfamiljshus zone-3 (southern Sweden) archetypes.

### 7.2 Applied (2026-05-21): area/occupancy correction (Mechanism B) — `eubucco.area_correction = 0.50`

The §6 claim that "EUBUCCO floor area is roughly right" is **wrong** (a population × m²/dwelling unit error). Direct measurement: EUBUCCO EE residential heated area = **114.5 Mm²**, but Statistics Estonia REL 2021 records 557,146 occupied + 175,690 vacant dwellings ≈ **51 Mm²** — a ~2.2× over-count. So EE has **both** an intensity issue (class-mix, §7.1) **and** a large area issue.

**Mechanism — occupancy, NOT a data defect.** EUBUCCO's CH-style Estonian source has ~100 % observed building height (Milojević-Dupont 2023, Table 1), so the floor area *per building* is accurate. The over-count is **stock utilization**: EUBUCCO classifies 440,113 buildings as SFH vs ~220,000 single-family houses in the census — the ~220k excess is Estonia's *suvila* (summer-house/dacha) stock, closed and unheated through the heating season, plus vacant dwellings. This is the same family as ES/CY (occupied stock heated; vacant/seasonal not) and is documented as **Mechanism B** in [eubucco_census_area_audit.md](../eubucco_census_area_audit.md).

**Value 0.50** = midpoint of the census range 0.45 (strict occupied+vacant 51/114.5) to 0.54 (adding MFH common-area circulation + suvila stock that EUBUCCO captures). It is **not** tuned to Hotmaps (which would need ~0.55). **Result:** combined with the §7.1 class-mix, EE lands at **10.8 TWh = −18.7 % vs Hotmaps (ACC)** — an honest census-grounded under-shoot, not corrected upward to hit the benchmark.

**Honest caveat:** occupancy is a real, census-grounded effect, but applying it to EE (and ES/CY) and not to e.g. IT/PT — which have similar vacancy — is benchmark-informed (the lever that reconciles each country is chosen with knowledge of the Hotmaps gap). This limitation is disclosed in the audit doc, not hidden.
