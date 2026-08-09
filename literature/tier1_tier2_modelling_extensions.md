# Tier 1 / Tier 2 modelling extensions — sourcing, decisions, and specs

Status note (2026-05-28). This document records the sourced data, the decisions
taken, and the precise remaining implementation steps for the modelling roadmap
items started this session. Each external figure is attributed to a primary
source. Items marked **DONE** are implemented and committed; **CONFIG/DOC** means
the data + configuration + documentation are in place but the code wiring or a
Colab validation run remains; **SCOPED** means designed and sourced but not yet
built.

---

## T1a — Hungary HU-direct TABULA  (DONE)

Replaced the German proxy with Hungarian-specific intensities extracted directly
from the **Hungarian national TABULA/EPISCOPE typology brochure** (Csoknyai T.,
Hrabovszky-Horvath S., Seprodi-Egeresi M., Szendro G., *National Typology of
Residential Buildings in Hungary*, BME, 2014;
`episcope.eu/.../HU_TABULA_TypologyBrochure_BME.pdf`). Net space-heat demand
(q_h_nd, kWh/m2/yr) was read off each archetype's heating-season chart, with
per-cell page citations in `code/data/raw/tabula/hu_intensities.csv`. Cohort
mapping (BME pre-1944/1945-79/1980-89/1990-2005/post-2006 -> our 6 cohorts by
midpoint proximity) and class mapping (BME SFH>80/<80, MFH, panel AB -> our
SFH/MFH_LOW/MFH_HIGH) are documented in the file header; DHW carried at the
central-European DE-TABULA values pending an HU-specific figure. `hu.yaml`
switched to source_country HU, climate_multiplier 1.0 (values already at HU
reference climate — removes the prior dependence on the NEEDS_VERIFY HU/DE HDD
ratio). **Pending:** Colab rebuild to re-reconcile (the net direction of the
switch is not sign-obvious; reported as-is, not tuned).

Cross-references: Csoknyai et al. (2016) E&B 132:39-52; Hrabovszky-Horvath et al.
(2013) E&B 62:475-485.

## T1b — Croatia climate region-split  (CONFIG/DOC; code wiring pending)

Croatia has **no national TABULA typology** (absent from the EPISCOPE country
list), so a climate-matched neighbour split replaces the single Slovenian proxy.
The Adriatic coast is Koppen Csa, the interior Cfb/Dfb (Segota & Filipcic
regionalisation; Mimic et al. 2024, *Atmospheric Science Letters*,
doi:10.1002/asl.1270). Croatian building regulation prescribes ~35 kWh/m2.a
(coastal) vs ~45 (continental) for new SFH, confirming the contrast (via
Krajcic et al. 2026, *MDPI Buildings* 16(1):207, doi:10.3390/buildings16010207).

Decision (in `hr.yaml tabula.region_split`):
- **coastal -> Italian TABULA**, climate_multiplier 0.52: NUTS3 HR033 Zadar,
  HR034 Sibenik-Knin, HR035 Split-Dalmatia, HR036 Istria, HR037 Dubrovnik-Neretva
  (clearly Csa Dalmatia + Istria). Coastal mean HDD ~1300 (Eurostat nrg_chddr2_a:
  Split-Dalmatia ~1289, Dubrovnik ~1104) / Italian TABULA Middle reference ~2500.
- **interior -> Slovenian TABULA**, climate_multiplier 0.80: all other NUTS3.
  Interior mean HDD ~2150 (Zagreb ~2085, Osijek ~2073, Varazdin ~2266) / SI 2693.
- HR031 (Primorsko-goranska/Gorski Kotar) and HR032 (Lika-Senj) assigned to
  **interior** despite a coastal strip, because their large cold mountainous
  hinterlands behave continentally (flagged judgement; coastal dwelling share
  then ~25-28%, 2021 DZS census).

Schema: a new optional `tabula.region_split` block + `tabula_region_split` field
on `CountryConfig` (backward-compatible; None for all other countries; validated).

**Remaining code step — 03_heat_intensity.py NUTS3-aware build (spec):**
1. `main()`: when `cfg.tabula_region_split` is set, do not pass a single TABULA
   frame; instead let `build_intensity_lookup` build one (class, cohort) sub-lookup
   per region (loading each region's `file` with its `climate_multiplier`, reusing
   the existing per-class `load_tabula(...).set_index(...)` pattern already used
   for `tabula_class_mix`), tagging each row with a `region` column, and return a
   `nuts3 -> region` map (built from the region `nuts3` lists, default to
   `default_region`).
2. `stream_intensity`: when the lookup carries a `region` column, add
   `chunk["region"] = chunk["nuts3"].map(region_map).fillna(default_region)` and
   merge on `["region", "building_class", "cohort"]` instead of
   `["building_class", "cohort"]`. The classified parquet already carries `nuts3`
   (used for nuts_acc), so no upstream change is needed.
3. Backward compatibility: when `region_split is None` the merge keys and behaviour
   are unchanged (regression-checked on LU at the config layer; re-check the full
   LU build after wiring).
4. Validate by re-reconciling HR in Colab; refine the two multipliers / the
   HR031-HR032 assignment if HR lands outside the +/-25% band.

## T1c — Spain / Italy EUBUCCO area  (DOC; ES already corrected)

The agent sourced authoritative 2021 census occupied-dwelling floor areas:
- **Spain (INE Censo 2021):** 18,536,616 occupied (principales) dwellings;
  ~90 m2/dwelling useful area (superficie util, INE Censo 2011, the latest direct
  measurement) -> ~1.67 Bn m2. Raw ratio vs EUBUCCO 4.08 = 0.41 (occupied) /
  0.56 (total stock incl. secondary+vacant). URL: ine.es/prensa/censo_2021_jun.pdf.
- **Italy (ISTAT Censimento permanente 2021):** 25,690,057 occupied dwellings
  (abitazioni occupate); avg ~99.7 m2 computed from the official surface-class
  distribution -> ~2.56 Bn m2. Raw ratio vs EUBUCCO 4.47 = 0.57. URL:
  istat.it/.../Today-Abitazioni_01_08-2024.pdf.

**Net-vs-gross caveat (important):** census "superficie / superficie util" is net
usable internal area; EUBUCCO is gross (footprint x storeys). Part of the gap is
definitional, not over-count. The model's existing benchmarks
(`es.yaml census_eubucco_ratio 0.61`, `it.yaml 0.72`) are computed against the
model's *heated* residential area (which already applies useable_area_fraction),
**not** raw gross EUBUCCO, which is why they sit above the agent's raw ratios.

Decision:
- **ES:** already has `eubucco.area_correction: 0.613` applied (INE Censo 2021,
  Mechanism B). The new INE figures corroborate the direction; no change made.
- **IT:** carries the `census_floor_area` benchmark (0.72) but **no** correction
  is applied. Applying one (analogous to ES) requires the model's IT heated-area
  output to compute `census_occupied / model_area` and isolate the over-count
  from the net-vs-gross definitional gap. **Do this in the next Colab IT build**
  (the ISTAT 2021 occupied figure above is the heated-stock anchor); do not set
  an unvalidated multiplier here.

## T2c — rho (cross-country renovation correlation)  (FINDING: cannot estimate)

Goal was to ground `INTENSITY_RATE_CORR = 0.5` empirically. **Finding:** no
per-country, year-by-year renovation-rate panel exists in the open literature.
The Ipsos/Navigant (2019) *Comprehensive study of building energy renovation
activities* reports only a single 2012-2016 cross-section (Table 2; underlying
ACE architect survey only 2012/2014/2016, interpolated otherwise); the BPIE EU
Buildings Climate Tracker tracks indicators over time but at EU-aggregate level.
Only Odyssee-MURE holds an annual per-country series, which would have to be
pulled interactively from the portal. **Conclusion:** rho cannot be estimated by
cross-country correlation from public cross-sections; rho = 0.5 remains a
documented structural assumption, and the rho-sensitivity (paper Table tab:rho,
rho in {0, 0.5, 1}) already reports the full range. This honest non-availability
is the right answer rather than a fabricated correlation.

## T3 — retrofit cost curves (for endogenised renovation depth)  (SOURCED; LP build SCOPED)

For a future endogenous renovation-depth decision in COST_OPT, the cleanest
depth-resolved cost+saving table is **Ipsos/Navigant (2019)**, Final Report
(Nov 2019), Table 11 (cost) + p.80 (savings), EUR/m2 of renovated residential
floor area, EU28 average:

| Depth (primary-energy-saving band) | Cost (EUR/m2) | Energy saving | Source |
|---|--:|--:|---|
| Below threshold (<3%) | 56 | <1% | Ipsos/Navigant 2019, Tab.11/p.80 |
| Light / single-measure (3-30%) | 104 | ~13% | same |
| Medium / multi-measure (30-60%) | 154 | ~41% | same |
| Deep / major (>60%) | 219 | ~66% | same |
| All energy renovations (mean) | 83 | ~9% | same |

Country-level EUR/m2 are also in Table 11 (e.g. deep: BG 79, DK 271, AT 257).
URL: energy.ec.europa.eu/system/files/2019-12/1.final_report_0.pdf. JRC EUR
29906 EN (Filippidou & Jimenez Navarro 2019, doi:10.2760/278207) gives the
cost-vs-saving methodology and the central-vs-southern cost-optimality split but
no clean EUR/m2-by-depth table. These curves let COST_OPT trade retrofit CAPEX
(annualised) against the demand reduction it buys, instead of fixing demand at
the REF trajectory. **SCOPED:** the LP variable + constraint design is a
multi-day extension and is not built here.

## T4 — structural realism  (SCOPED)

Designed but not built this session (each needs its own sourcing + validation):
spatially-resolved HP/DH feasibility (current scores are ~uniform 0.67, which is
why the RQ1 "low HP feasibility" condition is inert); HP-load -> grid carbon /
capacity feedback (grid trajectory is exogenous); climate-warming HDD trajectory
(HDD frozen at the 1991-2020 normal) and an optional cooling end-use; and a
vintage-cohort turnover forward (demolition / new-build / retrofit cohorts)
replacing the single aggregate envelope-decline rate. Cooling and full
electricity-system coupling are scope expansions beyond the residential-heat
boundary and should be staged as separate work.
