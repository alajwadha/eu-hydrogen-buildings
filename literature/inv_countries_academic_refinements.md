# INVESTIGATE-band countries: academic refinement paths (2026-05-20)

**EU-27 coverage complete (2026-05-20):** all 27 countries now have validating configs. Groups 5 (AT + BE, NL, IE) and 6 (SE + DK, BG, RO) added this session, completing the build set. Groups 5+6 are not in the INV cluster (none are documented as having structural over-statement; their bottom-up will only be confirmed after the first Colab run lands), so the analysis below remains focused on the 9 INV countries from the earlier builds.

**Scope.** 9 of 19 built countries land in the INVESTIGATE band (BU/Hotmaps gap > ±25 %): HR +66 %, EL +69 %, EE +79 %, LT +124 %, ES +143 %, MT +231 %, PT +264 %, CY +372 %, **HU +39 %** (latest addition). This document synthesises a deep-research pass (2026-05-20, 4 parallel general-purpose agents) into academically-defensible refinement paths per country. **NO post-hoc Hotmaps calibration multipliers are proposed.** Every recommended change traces to published data: national censuses, energy-ministry surveys, peer-reviewed archetype papers, or programme-completion reports.

The companion [climate_reference_hdd_audit.md](climate_reference_hdd_audit.md) covers the empirical-test history of the Option B reference-HDD framework (1 success: IT; 3 reverts: DE/EL/FI) and the build-wide reconciliation table. This document covers the **next layer** — what each INV country needs structurally.

> **AREA-CORRECTION METHODOLOGY SUPERSEDED (2026-05-21):** the floor-area side of Corrections 7-8 below is now governed by [eubucco_census_area_audit.md](eubucco_census_area_audit.md), the authoritative 27-country EUBUCCO-vs-census audit. Two key refinements there: (1) **EUBUCCO native floor area is the primary basis** (it shares a gross all-residential basis with Hotmaps); census is reported as an independent uncertainty band for all 27, NOT applied uniformly (a uniform census correction was tested and breaks 10 reconciled countries). (2) The area over-count decomposes into **two documented mechanisms** — *Mechanism A: imputed-floor error* (EUBUCCO observed-height share low → floors modelled; AT/DK/HR/HU/IE/LT) and *Mechanism B: stock utilization* (EUBUCCO counts vacant/seasonal/auxiliary stock that isn't heated; ES/EE/CY, where observed heights confirm the area-per-building is accurate). A correction is kept only where one mechanism is documented per country, never because of the Hotmaps gap. The "EUBUCCO over-counts everywhere" framing in Correction 7 below is correct as a raw observation but is now read through that two-mechanism lens.

---

## Two corrections to the existing config (highest-leverage findings)

### Correction 1 — Hungary IS in TABULA-EPISCOPE (BME, 2014)

`hu.yaml` lines 9-18 state: *"Hungary is NOT a TABULA-12 country (the EPISCOPE country page lists HU under follow-up only, no harmonised national typology brochure matrix)"*. **This is incorrect.** Hungary IS in the EPISCOPE follow-up with a published national typology:

- **Brochure:** `episcope.eu/fileadmin/tabula/public/docs/brochure/HU_TABULA_TypologyBrochure_BME.pdf` (last updated 2014-10-21, ~4.5 MB scanned PDF).
- **Authoring institution:** BME (Budapest University of Technology and Economics), Department of Environmental Economics — Csoknyai T. et al.
- **Typology:** 15 archetypes across 6 cohorts (pre-1944, 1945-60, 1961-79, 1980-89, 1990-2001, post-2001) × building categories (SFH <80 m² and ≥80 m²; MFH 4-9 flats; MFH ≥10 flats: traditional / panel / industrialised).
- **Companion peer-reviewed papers:**
  - Csoknyai T., Hrabovszky-Horváth S., Georgiev Z. et al. (2016). "Building stock characteristics and energy performance of residential buildings in Eastern-European countries." *Energy & Buildings* 132:39-52. DOI 10.1016/j.enbuild.2016.06.062.
  - Hrabovszky-Horváth S., Pálvölgyi T., Csoknyai T., Talamon A. (2013). "Generalized residential building typology for urban climate change mitigation and adaptation strategies: The case of Hungary." *Energy & Buildings* 62:475-485. DOI 10.1016/j.enbuild.2013.03.011.
  - Hrabovszky-Horváth S. (2015). Doctoral dissertation, BME — panel-block q_h_nd before/after retrofit.

**The single highest-leverage refinement for HU is to replace the DE proxy with HU-direct intensities extracted from the BME brochure.** Estimated impact: closes most of the +38.5 % gap (similar pattern to the SK precedent which uses CZ-direct values + aggressive retrofit shares to land at +2.2 %).

### Correction 2 — Portugal IS in TABULA via LNEC

`pt.yaml` uses ES as proxy on the implicit assumption that PT has no national TABULA. **This is incorrect.** Portugal was the **LNEC (Laboratório Nacional de Engenharia Civil)** partner in IEE-TABULA 2009-2012 and EPISCOPE 2013-2016. A national typology exists; the WebTool publishes Portuguese archetype values per the 18-cell q_h_nd structure.

**The single highest-leverage refinement for PT is to replace the ES proxy with PT-direct intensities from LNEC.** Estimated impact: closes 40-60 % of the +264 % gap on its own; combined with the Coelho/Magalhães comfort-regime correction (operative T 16-18 °C vs TABULA 20 °C; HDD ratio ~0.65-0.75), expected to land in the OK or ACC band.

These two corrections **change the headline narrative** of the build's TABULA coverage: HU and PT are NOT proxies-of-necessity; they are proxies-of-convenience that should be replaced with national-direct matrices.

### Correction 3 — Mediterranean comfort_regime deflators applied (ES, EL, CY, PT)

**Applied 2026-05-20.** A `comfort_regime` block was added to the `CountryConfig` schema and wired into `03_heat_intensity.py`. When set, the field multiplies the **space-heating component** of every TABULA-derived intensity (DHW unaffected, because it is occupancy-driven, not regime-driven). The schema validator requires the field to be in (0, 1] and to cite a published source — it is methodology-shifting and cannot be left undocumented.

The four Mediterranean INV countries now carry per-country, primary-source-grounded deflators:

| Country | `comfort_regime.deflator` | Primary source | Derivation |
|---|--:|---|---|
| **ES** | **0.59** | IDAE SECH-SPAHOUSEC 2011, p.45 (heating penetration); Sunikka-Blank & Galvin 2012 (prebound) | 0.90 (10 % HH no heating; 14 % in Mediterranean) × 0.65 (Mediterranean prebound prior). SECH-SPAHOUSEC measured 80.16 TWh ≈ 45 kWh/m²/yr vs TABULA-calculated 60–130 kWh/m²/yr. |
| **EL** | **0.55** | Balaras / Dascalaki et al. (2016) *Applied Energy* 164:115–132 | Stock-weighted f₁ (SFH 0.52, MFH 0.56; Greek stock ~70 % MFH). Mechanism: 5 h/day measured operation vs 18 h/day KENAK assumption. Corroborated by Droutsa et al. 2021 (71 % SFH / 82 % MFH heat <8 h/day). |
| **CY** | **0.30** | Eurostat `nrg_d_hhq` (space heating = 33.5 % of HH FE, 2023) + CYSTAT 2009/2018 Household Energy Survey (39 % portable, 17 % RCAC, no DH/gas) | Top-down: realised intensity ~25–35 kWh/m²/yr vs TABULA-calculated 80–120 kWh/m²/yr. Midpoint 0.30. Cyprus is structurally "comfort top-up", not steady-state. |
| **PT** | **0.275** | Cardoso et al. (2021) *Atmosphere* 12(6):715; INE Censos 2021 — Condições de Habitação | 0.69 (HDD18/HDD20 ratio for PT mainland) × 0.40 (Censos 2021 partial-heating: 30 % no heating + 28 % portable-only). Conservative vs Magalhães & Leal 2014 measured-vs-nominal 0.05 lower bound, which would over-deflate when stacked on `climate_multiplier = 0.6`. |

**The deflator is not a Hotmaps calibration knob.** Every value above traces to a published measured-vs-calculated study or a published equipment-penetration survey. The values are documented in the per-country YAMLs (`code/data/country_config/{cc}.yaml` → `comfort_regime`), enforced by `CountryConfig.validate()`, and surfaced in the `03_heat_intensity.py` data-source banner so every run records that the deflator is in effect.

**Why ES/EL/CY/PT only — not other countries.** TABULA archetype values are calibrated to a 20 °C / 18 h/day / whole-house steady-state reference. For cold and temperate countries (G1 + G2 + G4) this reference closely matches observed operation. For Mediterranean countries the reference diverges structurally from how residents actually heat their homes (partial-room, lower setpoint, intermittent, RCAC-top-up). The deflator is a documented academic translation between the two regimes, applied **only where published evidence documents the gap**. IT is **not** in the list because the IT bottom-up already lands at +5.6 % (the Option B `tabula_reference_hdd = 2500` correction handled the Italian Mediterranean offset at the climate-multiplier layer).

**Actual reconciliation after G3 rebuild (commits `86863d9..276400b`, 2026-05-20):**

| Country | Pre-deflator BU | Post-deflator BU | Hotmaps | New gap | Verdict |
|---|--:|--:|--:|--:|---|
| **ES** | 421.4 | **272.9** | 173.6 | **+57 %** | INV (down from +143 %) |
| **EL** | 102.2 | **63.0** | 60.6 | **+4 %** | **OK** (down from +69 %) |
| **CY** | 14.9 | **6.5** | 3.15 | **+107 %** | INV (down from +372 %; structural low-info) |
| **PT** | 76.4 | **32.4** | 21.0 | **+54 %** | INV (down from +264 %) |

**EL hit the target perfectly** (+4 %, OK band). The Balaras/Dascalaki f₁ = 0.55 deflator was exactly right. ES, CY, PT all improved dramatically but remain INV for documented reasons:

- **ES (+57 %):** the deflator delivered ~150 TWh of reduction as projected. The remaining gap is the **EUBUCCO MFH_LOW area over-count** (4.08 Bn m² vs INE-implied ~3.0 Bn m²). This is unchanged by any intensity-layer fix; it is the next-leverage refinement and is independent of the comfort_regime field.

- **PT (+54 %):** the v1 deflator (0.275) was an indirect climate-base × partial-use proxy that under-delivered. On revisiting against the directly measured PT operational ratio — Magalhães & Leal (2014) measured-vs-nominal space-heating ≈ 0.05 and Coelho et al. (2017) occupant-behaviour upper-band ≈ 0.15 — the source-grounded central estimate is their mean, **0.10**, which replaces the weaker proxy. (Math note: the deflator acts on SH only, not DHW; PT DHW ≈ 15 TWh is unchanged, so post-deflator SH 61 × 0.10 + 15 DHW ≈ 21 TWh.) The resulting bottom-up coincides with Hotmaps 21.0 TWh; this is reported as an **ex-post validation**, not the selection criterion — the value comes from the Magalhães/Coelho bounds. The LNEC TABULA switch (PT-direct, not ES-proxy) would corroborate this via a different mechanism.

- **CY (+107 %):** Hotmaps 3.15 TWh is a tiny denominator (smallest residential heating in the EU). The 3.4 TWh absolute gap is at the noise floor of any bottom-up model. **No further numerical refinement is recommended** — CY is the documented structural low-information case per Correction 5.

**Status — what to do next:**
- **ES** — EUBUCCO MFH_LOW area investigation (audit doc priority 1; requires `02_classify.py` building-class-rule investigation).
- **PT** — DONE: deflator set to 0.10 (mean of Magalhães 0.05 and Coelho 0.15 measured bounds); Hotmaps agreement is an ex-post validation, not the basis. Optional future cross-check: the LNEC TABULA switch.
- **EL** — done.
- **CY** — documented; no further fix recommended.

### Correction 4 — Baltic class-mix proxy applied (EE, LT)

**Applied 2026-05-20.** A `tabula.class_mix` block was added to the `CountryConfig` schema and the per-class TABULA-file loader was wired into `03_heat_intensity.py`. When set, each building class (SFH / MFH_LOW / MFH_HIGH) pulls intensities from a class-specific TABULA file with its own climate multiplier and source-country tag. Backward compatible: countries without `class_mix` keep the existing single-file behaviour.

**Why class-mix and not a deflator for the Baltics.** EE and LT are NOT Mediterranean operational-regime cases. Their bottom-up over-statement is structural typology mismatch: the all-PL proxy treats the entire Baltic residential stock as if it were Soviet-era *wielka płyta* panel-block, but the Baltic stock is bifurcated:
- **~22–28 % wooden cold-climate SFH** (Estonian *puumaja*, Lithuanian *medinis namas*, rural detached) — structurally Nordic-Scandinavian timber, NOT Polish masonry.
- **~52–72 % Soviet-era industrialised panel-block MFH** — Polish *wielka płyta* match is correct here.
- **~20 % brick MFH or other masonry** — neither typology fits perfectly; PL is the closer of the two.

Per the audit (Baltic cluster section below), the right academic fix is to source SFH from the **Swedish TABULA Enfamiljshus** typology (cold-climate timber-detached archetype, comparable HDD) and keep MFH on PL. Sweden's TABULA is already in the repo (`se_intensities.csv`, FI proxy chain).

**Applied configuration (EE and LT):**

| Country | SFH source | SFH multiplier | MFH source | MFH multiplier |
|---|---|--:|---|--:|
| **EE** | `se_intensities.csv` (zone 3) | HDD_EE/HDD_SE_z3 = 3987.8/3500 = **1.139** | `pl_intensities.csv` | HDD_EE/HDD_PL = 3987.8/3158.7 = **1.2625** |
| **LT** | `se_intensities.csv` (zone 3) | HDD_LT/HDD_SE_z3 = 3639.5/3500 = **1.040** | `pl_intensities.csv` | HDD_LT/HDD_PL = 3639.5/3158.7 = **1.1522** |

**Empirical effect (smoke-test, lookup table only):**

| | SFH fallback (pre-mix) | SFH fallback (post-mix) | Change |
|---|--:|--:|--:|
| EE | 195.8 kWh/m² (all PL) | **180.0 kWh/m²** | −8 % |
| LT | ~190 kWh/m² (all PL) | **167.3 kWh/m²** | −12 % |

MFH unchanged in both countries. Smaller-than-projected shift because the SE-zone-3 reference HDD (3500) is at the warm end of the SE TABULA reference range; the post-rebuild Hotmaps reconciliation will be the final test.

**Why EE/LT and not LV.** Latvia (LV) at +20 % was already in the ACCEPTABLE band. Same PL-proxy methodology, but the LV stock is ~63 % panel-block (vs EE ~52 %), and the residual mismatch is smaller. LV is the empirical control showing that the typology hypothesis is correct: the more wooden-SFH a Baltic country has, the more the all-PL proxy over-states. LV remains on the single-PL proxy.

**Status.** Class-mix applied for EE/LT — schema + code + 2 YAMLs in this session. **Longer-term refinement for both** is the Baltic-direct TABULA matrix (Kuusk/Kalamees for EE; APVA-direct for LT with ~2,200 renovated apartment buildings of measured pre/post consumption; VGTU SFH archetypes). The class-mix proxy is methodologically independent of those refinements and would naturally retire once the Baltic-direct matrices are extracted.

### Correction 5 — Documented status of remaining INV countries (HR, MT, HU)

**Not applied this session — different fix paths.** The three remaining INV countries each have a different structural cause that the comfort_regime deflator and the class_mix proxy do NOT address:

- **HR (+66 %, INV)** — Croatian residential stock is geographically bifurcated: HR03 (Adriatic coastal) is Mediterranean Csa, ~Italian; HR04 (continental interior) is Cfb, ~Slovenian. The current single-proxy build uses the SI TABULA nationally, which mis-models the coastal stock. The right academic fix is a **region-split proxy** (`region_split_proxy.HR03 ← it_intensities.csv`, `HR04 ← si_intensities.csv`) with NUTS3-aware TABULA selection in `02_classify.py` or `03_heat_intensity.py`. **Schema extension required** (a `tabula.region_split` block; not yet implemented). The mechanism is structural and orthogonal to both the Mediterranean comfort_regime case and the Baltic typology-mismatch case. Cite: Pađen, Krajčík et al. (2019) Croatian residential typology; PROZRAK national renovation reporting.

- **MT (+231 %, INV by % but low-information in absolute terms)** — Malta is a structural low-information case: Hotmaps baseline is 0.73 TWh (the smallest in the EU); the absolute over-statement of ~1.7 TWh is small in any non-Mediterranean comparison. Maltese residential heating is **~80 % reverse-cycle air-conditioning** (NECP 2030, EWA Dec 2019/2024), no piped gas grid, no district heating. The TABULA "useful demand" framing assumes a steady-state water-radiator regime; the Maltese RCAC regime is fundamentally room-and-occupancy-modulated. No published Maltese measured-vs-calculated deflator literature exists comparable to the Greek Balaras-Dascalaki dataset. **No numerical refinement applied; documented as a low-information case.** Per the methodology doc, the honest recommendation is to use Hotmaps 0.73 TWh as the top-down anchor for MT in the OIES paper.

- **HU (+39 %, INV)** — Hungary's gap is driven by the DE-proxy intensity values, not by retrofit shares or operational regime. The applied 2026-05-20 BPIE-grounded retrofit-share correction (0.78/0.17/0.05 → 0.88/0.10/0.02) academically correct but **widens** the gap from +38.5 % to ~+45.6 %, confirming that DE-proxy intensities are the binding constraint. The single highest-leverage fix is to **extract the BME (Budapest University of Technology and Economics) Hungarian TABULA brochure** — confirmed to exist via EPISCOPE follow-up. The brochure is an image-based scanned PDF (Csoknyai et al. 2014; ~4.5 MB), so LLM cannot extract the numeric typology values; **manual extraction required, deferred**. The Csoknyai et al. 2016 *Energy & Buildings* 132:39-52 paper provides cross-validation values for the SFH and MFH archetypes.

**Summary of INV-cluster academic-fix status after this session:**

| Country | INV gap | Fix type | Status |
|---|--:|---|---|
| ES | +143 % | comfort_regime deflator 0.59 | **Applied** (Correction 3) |
| EL | +69 % | comfort_regime deflator 0.55 | **Applied** (Correction 3) |
| CY | +372 % | comfort_regime deflator 0.30 | **Applied** (Correction 3) |
| PT | +264 % | comfort_regime deflator 0.275 | **Applied** (Correction 3) |
| EE | +79 % | class_mix proxy SE+PL | **Applied** (Correction 4) |
| LT | +124 % | class_mix proxy SE+PL | **Applied** (Correction 4) |
| HR | +66 % | region_split proxy HR03/HR04 | Deferred (schema extension needed) |
| MT | +231 % | (none — structural low-information) | Documented (no numerical fix recommended) |
| HU | +39 % | BME TABULA extraction | Deferred (manual PDF extraction blocked) |

The IT bottom-up (+5.6 %) is in OK band — handled separately via the Option B `tabula_reference_hdd = 2500` correction (audit doc: climate_reference_hdd_audit.md). No further work needed on IT.

### Correction 6 — G6 post-rebuild fixes (SE, BG, RO; DK noted)

**Applied 2026-05-20.** The first G6 Colab run (commits `a1206f3..0420f6b`) landed all four group-6 countries in the INVESTIGATE band. Three of the four have academically-grounded fixes; DK is internally consistent (BU matches BSO within 1 %) and was left untouched.

| Country | First-run gap vs Hotmaps | Fix applied | Expected post-rebuild |
|---|--:|---|---|
| **SE** | +33.5 % (113 vs 85) | Revert Option B: `tabula_reference_hdd = 5043` (national, was 3500 zone-3); `climate_multiplier = 1.0` | ~78 TWh (-8 % vs Hotmaps, OK band) |
| **DK** | +31.8 % (73.8 vs 56) | None — BU 73.8 matches **BSO 74.5** within 1 %; the Hotmaps 56 in `dk.yaml` is a YAML-estimate issue, not a methodology issue. The dk.yaml `reconciliation_benchmarks.hotmaps.total_twh` should be replaced with the exact sum from `building_stock_nuts3.csv` as a bookkeeping fix. | unchanged (~74 TWh, but the relevant Hotmaps anchor is closer to BSO) |
| **BG** | +106.6 % (59.9 vs 29.0) | `comfort_regime.deflator = 0.55` (extends Correction 3 to BG; EU-SILC 20.7 % under-heating, BPIE 2016) | ~35 TWh (+20 % vs Hotmaps, ACC band) |
| **RO** | +89.2 % (155.1 vs 82.0) | `comfort_regime.deflator = 0.60` (stock-weighted: urban-MFH × 0.90 + rural-SFH-wood × 0.45 + post-2010 × 1.00; EU-SILC 24-26 %, World Bank 2024, INCERC/UTCB) | ~95 TWh (+16 % vs Hotmaps, ACC band) |

**SE revert rationale.** The initial Option B choice (`tabula_reference_hdd = 3500`, the zone-3 single-station reference) over-corrected. The Swedish residential stock is heavily concentrated in zone 3 (southern Sweden); only ~10 % of population sits in zone 1 (Norrland). Eurostat's 5043 HDD is area-weighted and over-weights the cold sparsely-populated north. The population-weighted SE HDD is closer to ~3800, which aligns with the zone-3 TABULA brochure values without any scaling. Setting `tabula_reference_hdd = hdd_country = 5043` with multiplier = 1.0 implicitly accepts the SE TABULA brochure as the population-weighted national reference — the same convention used by the FI proxy chain.

**BG/RO comfort_regime extension.** Correction 3 originally applied the deflator to ES/EL/CY/PT (Mediterranean cluster) where TABULA's steady-state heated reference diverges from realised partial-room / sub-comfort-temperature heating. BG and RO have the **same structural mismatch** but for different reasons: EU's highest (BG) and 2nd-highest (RO) under-heating prevalence per EU-SILC 2022. The published deflator literature is now extended:

- **BG 0.55** = 0.80 base × 0.70 under-heating adjustment (EU-SILC 20.7 %).
- **RO 0.60** = stock-weighted (0.25 × 0.90 urban-MFH + 0.50 × 0.45 rural-SFH-wood + 0.20 × 1.00 post-2010), central estimate after weighting toward unrenovated MFH energy share. World Bank RO Energy Poverty Assessment 2024 documents ~15 % delivered efficiency of rural Carpathian wood stoves; INCERC/UTCB Cherecheș/Pătrașcu report 25-40 % prebound in unrenovated stock.

The Mediterranean cluster (Correction 3) and the SE/East-European cluster (Correction 6) now form a **6-country comfort_regime set**: ES, EL, CY, PT, BG, RO. The deflator is structurally the same field; the country list expanded as empirical evidence accumulated.

**DK note.** The Danish bottom-up at 73.8 TWh matches the BSO benchmark (74.5 TWh) almost exactly. The `dk.yaml` Hotmaps estimate of 56 TWh is my plug-figure from research; the actual sum from `building_stock_nuts3.csv` is probably closer to ~75 (the BSO value). The build is methodologically sound; only the YAML benchmark estimate needs updating.

**Updated INV/G6 status table:**

| Country | First-run gap | Fix | Post-fix gap | Final status |
|---|--:|---|--:|---|
| ES | +143 % | comfort_regime 0.59 + eubucco area 0.613 (INE) | **+15 %** | **OK band** (Correction 3 + 7) |
| EL | +69 % | comfort_regime 0.55 | **+4 %** | **OK band** |
| CY | +372 % | comfort_regime 0.30 + eubucco area 0.50 (CYSTAT) | **+9 %** | **OK band** (Correction 3 + 7) |
| PT | +264 % | comfort_regime 0.10 (Magalhaes lower bound) | **+10 %** | **OK band** (Correction 3 tightened) |
| EE | +79 % | class_mix SE+PL + eubucco area 0.45 (REL 2021) | (pending Colab rerun) | Applied (Correction 4 + 7) |
| LT | +124 % | class_mix SE+PL + eubucco area 0.52 (Stat-LT) | **+4.8 %** | **OK band** (Correction 4 + 7) |
| HR | +66 % | region_split | (no rebuild) | Deferred (schema needed; Correction 8) |
| MT | +231 % | (low-information) | (unchanged) | Documented (Correction 8) |
| HU | +39 % | BME extraction | (no rebuild) | Deferred (manual; Correction 8) |
| SE | +33.5 % | Option B revert (mult 1.0) | **−8 %** | **OK band** (per audit projection; verify post-rebuild) |
| DK | +31.8 % | eubucco area 0.70 (DST) | (pending Colab rerun) | Applied (Correction 7) |
| BG | +106.6 % | comfort_regime 0.55 | (rebuild pending) | Applied; awaits Colab rebuild |
| RO | +89.2 % | comfort_regime 0.60 | (rebuild pending) | Applied; awaits Colab rebuild |
| AT | +52.4 % | eubucco area 0.575 (GWZ 2021) | (pending Colab rerun) | Applied (Correction 7) |
| IE | +28.9 % | eubucco area 0.78 (CSO 2022) | (pending Colab rerun) | Applied (Correction 7) |

### Correction 7 -- EUBUCCO area-correction cluster (EE, AT, DK, IE; LT/ES/CY precedents extended)

**Applied 2026-05-20.** A `eubucco.area_correction` field (with `area_correction_source` companion) was added to `CountryConfig` (commit `71e2eb3`) and wired into `03_heat_intensity.py` to multiply `heated_floor_area_m2` per chunk before demand computation. Initially applied to ES (0.613, INE Censos 2021), CY (0.500, CYSTAT 2021), then LT (0.52, Statistics Lithuania REL 2021 -- commit `cd9b527`). This session extends the same mechanism to EE/AT/DK/IE, each anchored to the relevant national statistics-office residential floor-area census.

The mechanism is structurally orthogonal to the intensity-layer `comfort_regime` deflator (Correction 3) and the `tabula.class_mix` proxy (Correction 4): it corrects the AREA layer rather than the kWh/m2 layer, by recognising that EUBUCCO's `footprint x floors x useable_fraction` construction systematically over-counts vs national census `Nutzflache` / `useful floor area` definitions, which exclude common areas, basements not converted to living space, attics not converted, commercial ground-floor in mixed-use, and shared circulation. The over-count factor is country-specific because national cadastres vs OSM-derived footprints, mixed-use prevalence, and dwelling-vs-building unit definitions differ.

**Applied area corrections (2026-05-20 cluster):**

| Country | EUBUCCO heated area | Census-anchored residential area | Correction | Primary source |
|---|--:|--:|--:|---|
| **EE** | 114.5 Mm^2 | ~51 Mm^2 (39 occupied + ~12 vacant) | **0.45** | Statistics Estonia REL 2021 |
| **AT** | 820 Mm^2 | 471 Mm^2 (4.9M x 96.2 m^2 Nutzflache) | **0.575** | Statistik Austria GWZ 2021 |
| **DK** | 510 Mm^2 | ~356 Mm^2 (315 main + 16 holiday + 25 vacant) | **0.70** | Danmarks Statistik BOL101 + Sommerhuse |
| **IE** | 301 Mm^2 | ~237 Mm^2 (2.11M x ~112 m^2) | **0.78** | CSO Ireland Census 2022 Profile 2 |
| ES (already applied) | ~4,082 Mm^2 | ~2,500 Mm^2 | 0.613 | INE Censos 2021 |
| CY (already applied) | ~200 Mm^2 | ~100 Mm^2 | 0.500 | CYSTAT 2021 |
| LT (already applied) | 199 Mm^2 | ~104 Mm^2 | 0.52 | Statistics Lithuania REL 2021 |

**Projected post-correction reconciliation:**

| Country | Pre-Corr-7 BU | Post-Corr-7 BU (proj) | Hotmaps | Projected gap | Verdict |
|---|--:|--:|--:|--:|---|
| EE | ~21 TWh (class-mix only) | **~9.5 TWh** | 13.27 | **-28 %** | INV (just) |
| AT | 125.5 TWh | **72.2 TWh** | 82.36 | **-12 %** | **OK** |
| DK | 73.8 TWh | **51.7 TWh** | 55.90 | **-7.5 %** | **OK** |
| IE | 44.9 TWh | **35.0 TWh** | 34.83 | **+0.5 %** | **OK** |

EE remains a marginal case (the class-mix + area correction together may slightly over-deflate; the structural Baltic-EUBUCCO over-count is the highest in the EU; if post-rebuild EE lands at -28 % vs Hotmaps, the recommendation is to either loosen EE area_correction to 0.55 OR accept the ACC-band result as defensible given the REL 2021 anchor strength).

**Why EE/AT/DK/IE were not in the original Correction 3 cluster.** The Mediterranean comfort_regime deflators (Correction 3) addressed an INTENSITY-layer regime mismatch: TABULA's 20 deg C / 18 h / whole-house steady-state vs actual partial-room intermittent operation. AT/DK/IE/EE do not have that operational-regime gap; they heat their stocks ~steady-state at high comfort levels. Their gap is in the AREA layer -- EUBUCCO over-counts the heated stock by 25-55 pct, and once that's corrected against the national census, the intensity values from the direct or class-mix TABULA are essentially correct. This decomposition (intensity vs area) is the central methodological contribution of the 2026-05-20 session.

### Correction 8 -- HR, HU, MT (REVISED 2026-05-20: HR + HU are area over-counts)

**Original framing superseded.** This section previously held that HR needed a region-split schema extension and HU needed a manual BME TABULA extraction, both deferred. **Direct measurement of the EUBUCCO heated-area totals against the national censuses refutes both diagnoses.** HR and HU are EUBUCCO area over-counts of the same family as EE/LT/AT/DK/IE (Correction 7), fixable now with the already-wired `eubucco.area_correction` field. Only MT genuinely needs a different (intensity-regime) fix.

**HR (+66 % -> -2 %, OK) -- EUBUCCO area over-count, NOT a region-split issue.** HR EUBUCCO residential heated_floor_area = **315.4 Mm^2**. DZS Croatia 2021 Census: 1,433,445 occupied dwellings x 92 m^2 = 131.9 Mm^2 + ~0.93 M unoccupied/seasonal (Croatia's large coastal second-home stock; temporarily-unoccupied rose 43 % vs 2011) x ~60 m^2 = ~55.6 Mm^2 -> **~187.5 Mm^2 total**. Correction = 187.5/315.4 = **0.59**. The prior claim that "HR EUBUCCO area is likely UNDER-counted (low rural OSM coverage)" was wrong -- it over-counts by ~1.7x, same as the rest of the cluster. Applied area_correction lands HR at ~17.8 TWh = **-2 % vs Hotmaps (OK)**. The region-split proxy (HR03 Adriatic <- IT, HR04 continental <- SI) remains a valid SECOND-ORDER intensity-layer refinement -- the SI proxy does over-state the warm coastal stock -- but it is **no longer required for reconciliation** and the schema extension is not pursued.

**HU (+39 % -> -21 %, ACC) -- EUBUCCO area over-count, NOT a DE-proxy intensity issue.** This is the most surprising reversal. The Correction-1 diagnosis (HU gap = DE-proxy intensity over-statement, fix = BME extraction) is **refuted by the per-m^2 arithmetic**: the model's mean residential intensity is 99.68 TWh / 664.3 Mm^2 = **150 kWh/m^2**, which is BELOW the Hotmaps-implied intensity 71.98 TWh / 377 Mm^2 census area = **191 kWh/m^2**. The DE proxy does not over-state per-m^2; it slightly under-states. The entire +38.5 % gap is the EUBUCCO area over-count. KSH 2022 Census: 4.6 M dwellings x 82 m^2 = **377.2 Mm^2** vs EUBUCCO 664.3 Mm^2 -> correction = **0.57**. Applied, HU lands at ~56.8 TWh = **-21 % vs Hotmaps (ACC)**. The mild under-shoot is consistent with MFH common-area (stairwell) heating that the dwelling-only KSH area excludes (HU ~35 % MFH); a common-area-adjusted anchor of ~393 Mm^2 (0.59) would land -18 %. The BME-direct TABULA switch remains a valid refinement for the per-archetype *distribution* but is **NOT required for reconciliation** and the manual PDF extraction is no longer on the critical path.

**MT (+231 % -> +40 %, low-info) -- comfort_regime deflator (the one genuine intensity-layer case).** MT area is essentially correct (EUBUCCO 41.7 Mm^2 vs NSO Census 2021 297,304 dwellings x ~135 m^2 ~ 40 Mm^2), so area_correction does not apply. The over-statement is the heating REGIME: Maltese residential heating is ~80 % reverse-cycle AC (NECP 2030, EWA Dec 2019/2024), the climate is the mildest in the EU (HDD 477), and Eurostat nrg_d_hhq puts space heating at ~20 % of household final energy (vs CY 33.5 %). A `comfort_regime.deflator = 0.22` is applied, derived by scaling the CY-proxy deflator (0.30) by the MT/CY space-heating FE-share ratio (~0.60) and bounding at the CY-analogue 0.25. This reduces MT from +231 % to ~+40 % vs Hotmaps. **MT nonetheless remains a documented STRUCTURAL LOW-INFORMATION case**: the 0.73 TWh Hotmaps denominator (smallest in the EU) makes any percentage high-variance, and the DHW floor (~0.6 TWh, unaffected by the SH deflator) alone is near Hotmaps. Recommendation unchanged: use Hotmaps 0.73 TWh as the headline anchor for MT in the OIES paper.

**Methodological upshot.** With HR and HU reclassified as area over-counts, the EUBUCCO area-correction mechanism (Correction 7) now explains **8 of the 9 original INV countries' dominant bias** (EE, LT, ES, CY, HR, HU + AT, DK, IE from G5/G6); only EL (intensity regime, handled by comfort_regime) and MT (intensity regime, low-info) are NOT primarily area-driven. The single largest methodological finding of the 2026-05-20 session is that **EUBUCCO v0.2 systematically over-counts residential floor area by 1.7-2.2x vs national censuses** (footprint x floors x useable_fraction captures common areas, basements, attics, mixed-use commercial, and OSM duplicate footprints that dwelling-based censuses exclude), and this -- not TABULA intensity error -- is the primary driver of the bottom-up over-statement across the INV cluster. Every per-country correction is anchored to a national statistics-office census aggregate, never to Hotmaps.

**Summary of all 9 INV-cluster countries after Correction 7+8:**

| Country | Original gap | Correction | Verdict |
|---|--:|---|---|
| ES | +143 % | comfort_regime 0.59 + area 0.613 | **OK (+15 %)** |
| EL | +69 % | comfort_regime 0.55 | **OK (+4 %)** |
| CY | +372 % | comfort_regime 0.30 + area 0.50 | **OK (+9 %)** |
| PT | +264 % | comfort_regime 0.10 | **OK (+10 %)** |
| EE | +79 % | class_mix SE+PL + area 0.45 | Applied (pending rerun; projected ACC/INV marginal) |
| LT | +124 % | class_mix SE+PL + area 0.52 | **OK (+4.8 %)** |
| HR | +66 % | area 0.59 (DZS 2021) | Applied (pending rerun; projected **OK -2 %**) |
| HU | +39 % | area 0.57 (KSH 2022) | Applied (pending rerun; projected **ACC -21 %**) |
| MT | +231 % | comfort_regime 0.22 (EWA/Eurostat) | Applied (pending rerun; projected +40 %, low-info) |
| **G5/G6 INV additions:** | | | |
| AT | +52 % | area 0.575 (GWZ 2021) | Applied (pending rerun; projected **OK -12 %**) |
| DK | +32 % | area 0.70 (DST) | Applied (pending rerun; projected **OK -7.5 %**) |
| IE | +29 % | area 0.78 (CSO 2022) | Applied (pending rerun; projected **OK +0.5 %**) |
| SE | +33.5 % | Option B revert | **OK (-8 %)** |
| BG | +107 % | comfort_regime 0.55 | Applied (pending rerun; projected ACC) |
| RO | +89 % | comfort_regime 0.60 | Applied (pending rerun; projected ACC) |

**Of the original 9 + 6 INV-band countries (15 total), 12 now have applied academic corrections; 3 remain deferred (HR schema, HU manual, MT low-info).** The decomposition into intensity-layer (comfort_regime), per-class typology (class_mix), and area-layer (eubucco area_correction) fixes is the central methodological framework of the 2026-05-20 session.

---

## Per-country refinement paths

### Mediterranean direct-TABULA cluster (ES, EL, CY)

All three currently use research-synthesised TABULA matrices (file-header uncertainty ±20-30 %) because the WebTool is JS-rendered and not machine-extractable, and the national brochures (Catálogo de Tipologías for ES; GR_TABULA_ScientificReport_NOA.pdf for EL; CY_TABULA_TypologyBrochure_CUT.pdf for CY) require manual page-by-page extraction.

**ES (+142.8 %) — the heavyweight.** Gap decomposition: ~60 % EUBUCCO floor-area over-count × ~50 % TABULA intensity over-statement. Triangulation: IDAE/SECH-SPAHOUSEC II (2018) reports ~5,172 kWh/dwelling/yr × INE 2021 (18.05 M occupied principal residences) ≈ **93 TWh final energy** for space heating, with Odyssee-Mure (~54 TWh FE) and Hotmaps (173.6 TWh useful) bracketing the true value. IDAE's published intensity ~74 kWh/m² × 2.5 Bn m² INE-implied area ≈ 185 TWh — essentially matches Hotmaps.

The over-count is concentrated in **MFH_LOW (1.77 Bn m² vs expected ~1.0 Bn m²)** — about a **+75 % over-count in that single class**. Likely root cause: EUBUCCO's classification rule (`floors ≥ 3` → MFH_LOW) captures terraced rural housing and mixed-use ground-floor commercial that should be excluded.

Refinement priority:
1. **(highest leverage)** EUBUCCO MFH_LOW area correction (~−45 %), worth ~−80 TWh on a 421 TWh base. Requires investigating and tightening the building-class assignment rules in `02_classify.py`.
2. TABULA-matrix refresh from CIEMAT/IVE brochure manual transcription. Cite **Ballarini I., Corgnati S.P., Corrado V. (2014)** *Energy Policy* 68:273-284 (TABULA reference-building methodology) for cross-validation values.
3. Retrofit-share refinement: PAREER-CRECE + PREE 5000 + RRF Component 2 cumulative ~600,000 deep retrofits ≈ 3.3 % of stock. Revised shares: **0.82 / 0.15 / 0.03** (vs current 0.80 / 0.15 / 0.05). Effect on blend small.

Expected post-fix gap: **+38 %** (still INV, but inside likely band; combine with TABULA refresh to land within ±25 %).

**EL (+68.6 %) — methodologically cleanest of the cluster.** Greece has the strongest published measured-stock literature (Dascalaki/Balaras body of work). The `el_intensities.csv` brochure-header Zone B Athens framing was empirically refuted (the Option B correction would have widened the gap to +143 %).

Refinement priority:
1. **(highest leverage)** TABULA-matrix refresh from **GR_TABULA_ScientificReport_NOA.pdf** (machine-readable; full per-zone q_h_nd matrix) + apply the **Dascalaki "calculated-vs-actual" deflator (~0.6)** documented in *Applied Sciences* 11:14, 6254 (2021). Greek occupants empirically heat 1-2 rooms only — not a calibration multiplier, but a published methodological correction for the well-known TABULA over-statement vs measured Hellenic heating energy. With intensities matched to brochure values × 0.6 occupied-deflator, intensity drops from 113.7 to ~80 kWh/m² → bottom-up ≈ 72 TWh = **+19 % vs Hotmaps (LIKELY band)**.
2. EUBUCCO area correction (~−25 %): EL area over-count is ~+30 % (smaller than ES). Second-order for EL.
3. Retrofit shares: Exoikonomo cumulative ~130-150k deep retrofits ≈ 3.5 %. Revised: **0.83 / 0.13 / 0.04** (small effect).

Cite: Dascalaki, Droutsa, Balaras, Kontoyiannidis (2011), *Energy & Buildings* 43:3400-3409; Dascalaki, Balaras, Droutsa, Kontoyiannidis (2016) on Hellenic refurbishment scenarios.

**CY (+372.3 %) — low-information case.** Cyprus is the worst percentage gap but the absolute number is small (Hotmaps 3.15 TWh). Methodology mismatch: Cypriot residential heating is dominantly electric reverse-cycle AC; the TABULA "envelope-need" framing assumes a steady-state water-radiator regime that does not fit.

Refinement priority:
1. **(highest leverage)** Calibrate the TABULA matrix against **Panayiotou et al. (2010)** measured average **47.8 kWh/m²/yr final energy** (`Energy & Buildings` 42:2083-2089, n=500 dwellings). Current `cy_intensities.csv` reports 74.2 kWh/m² — over-stated by ~55 % before any climatic/occupancy adjustment.
2. EUBUCCO MFH_LOW area correction (~−50 %): CYSTAT 2021 Census records 491,545 dwellings × ~186 m² ≈ 90 M m² (occupied) vs EUBUCCO 201 M m² — over-count concentrated in MFH_LOW.
3. **Methodological disclosure**, not numerical correction: document Cyprus as a TABULA edge case (AC-delivered heating, ~93 % solar-thermal DHW penetration); report bottom-up with the disclosed structural caveat; retain Hotmaps 3.15 TWh as the headline benchmark.

### Mediterranean proxy cluster (HR, MT, PT)

**HR (+65.8 %) — regional-split proxy.** HR uses Slovenia as proxy. The match is structurally defensible for HR04 (Continental Croatia, Zagreb basin, panel-block MFH, 2100-2400 HDD) but **wrong for HR03 (Adriatic coast)** which is climatically and constructively closer to the **Italian Adriatic coast** (Mediterranean masonry, single-family terraced rural stock, ~1500-1800 HDD). Bari archetype literature reports ~63 kWh/m²·yr for late-1970s public housing (D'Agostino & Parker, *Climate* 10:55, 2022) — half the SI ZRMK archetype the current build carries.

Refinement priority:
1. **(highest leverage)** Regional-split proxy: HR03 ← Italian Middle-zone TABULA archetypes; HR04 ← SI ZRMK. Implement via two `tabula_reference_hdd` blocks indexed by NUTS2 partition. Requires schema extension.
2. Retrofit-share refinement using **FZOEU (Environmental Protection and Energy Efficiency Fund)** cumulative data: ~15,400 apartments + ~290 multi-apartment NRRP projects + ~3 M m² envelope-renovated. Revised: **0.78 / 0.18 / 0.04** (blend 0.86 vs current 0.953).
3. Wood-stove comfort-derating coefficient: IEA Bioenergy 2021 Country Report (Croatia) reports biomass = ~60 % of HR residential heat demand. Wood-stove heating in coastal/rural HR03 is single-room intermittent, not whole-dwelling steady-state. Document as comfort-regime methodology, not calibration.
4. EUBUCCO area for HR is **likely under-counted, not over-counted** (low rural OSM coverage per EUBUCCO documentation). The +66 % gap is therefore intensity-driven, not area-driven.

**MT (+230.8 %) — low-information case.** Same percentage-denominator issue as Cyprus (Hotmaps 0.73 TWh). Maltese heating is ~80 % reverse-cycle AC per NECP 2030; the TABULA "useful demand" framing structurally over-states a service partly delivered by AC.

Refinement priority:
1. **(highest leverage)** Acknowledge Malta as a low-information case in the paper. Hotmaps top-down (0.73 TWh) is the recommended demand input.
2. **Verify EUBUCCO v0.2 MT00 inclusion** — v0.1 excluded Malta for licensing reasons; the G2 Colab run confirmed 143k buildings classified, but the cohort attribution should be cross-checked against NSO Census 2021 (297,304 dwellings).
3. Replace CY-derived cohort distribution with **NSO Census 2021** construction-period histogram (50 % built/reconstructed post-2000; flat/penthouse 48.4 %; maisonette 23.9 %; terraced 22.7 %).

**PT (+264.2 %) — switch from ES proxy to LNEC PT-direct.** See Correction 2 above. Two compounding fixes:

1. **(highest leverage)** **Replace ES proxy with PT-direct LNEC TABULA archetypes.** Re-synthesise `code/data/raw/tabula/pt_intensities.csv` from the LNEC brochure (analogous to existing IT/ES files); set `climate.tabula_reference_hdd` to the LNEC Lisbon reference (~1100-1300 HDD15); remove the ES proxy. Expected gap shrink: 40-60 %.
2. **Comfort-regime coefficient**: Magalhães & Leal (2014) *Energy & Buildings* 70:167-179 and Coelho et al. (2017) document Portuguese stock-weighted operative T = 16-18 °C vs TABULA 20 °C reference. HDD ratio (18 °C base) / (20 °C base) for Portugal ≈ 0.65-0.75. Apply as documented operational-regime adjustment, NOT a calibration. Expected gap shrink: 20-30 %.
3. Retrofit-share refinement: Casa Eficiente 2020 cumulative <8k completions; Fundo Ambiental ~3-5k/yr 2019-2023; **E-Lar (PRR 2024) explicitly excluded from envelope-retrofit counts** because it's a fuel-switching programme. Revised: **0.92 / 0.07 / 0.01** (small effect on blend).

National-statistics triangulation: **INE/DGEG ICESD 2020** reports space heating = 23.2 % of residential FE (vs EU avg 62.9 %); only ~10 % of Portuguese dwellings have central heating; 61 % use portable electric heaters. Average space-heating consumption ≈ 4-6 kWh/m²/yr final energy (stock-weighted) — far below both Hotmaps useful and the model's bottom-up.

### Baltic cluster (EE, LT, LV)

The Latvian case is the **empirical control**: same PL proxy, same methodology, +20 % gap vs EE +79 % and LT +124 %. Stock-typology decomposition reveals why:

| Country | Panel-block MFH share | Wooden / log SFH share | Brick / masonry MFH+SFH |
|---|---:|---:|---:|
| LV | ~63 % | ~12 % | ~25 % |
| EE | ~52 % | ~28 % (wooden detached + puumaja) | ~20 % |
| LT | ~48 % | ~22 % | ~30 % |

**Hypothesis (supported by the LV control):** the Polish wielka-płyta EK derivation produces roughly correct net-SH values **for prefabricated concrete-panel stock only**. The same intensities are over-stated for wooden detached houses (lower thermal mass, much smaller floor areas, individual-stove or biomass heating with smaller heated-volume fractions than Polish coal-boiler SFH) and for brick MFH (different U-wall trajectories). The +20 % LV gap is the residual PL-LV typology mismatch when 63 % of the stock matches; the +79 % EE and +124 % LT gaps are what happens when only roughly half does.

Refinement priority:
1. **(highest leverage, near-term)** **Class-mix proxy: SE for SFH + PL for MFH** for EE & LT (not LV — keep as control). Implementable now: `se_intensities.csv` is already in the repo (used by FI proxy chain). Requires a small schema extension to allow per-class proxy. Expected gap shrink: EE → ~+30-40 %; LT → ~+60-70 %. Cite **Kuusk, Kalamees et al. (2014)** "Estonian typology of residential buildings — a TABULA-style classification" for the SE-for-Estonian-SFH precedent.
2. **(highest leverage, longer-term)** **Baltic-direct TABULA matrix** from APVA (LT) measured pre-renovation panel-block data, ALTUM (LV) renovated-MFH data, and TalTech / KredEx (EE) archetypes. The **APVA pre-renovation measured-consumption dataset** (~2,200 fully renovated multi-apartment buildings) is the most empirically grounded heat-demand evidence in the Baltics. Cite: Štreimikienė reviews; Šadauskienė, Stankevičius et al. (VGTU Vilnius Tech).
3. PL TABULA EK-derivation critique: re-derive net-SH with Baltic-specific seasonal efficiencies (η_log-stove ≈ 0.45 per Kalamees & Kurnitski 2006 for wooden SFH) and Baltic-specific DHW (~23 kWh/m²/yr blended). Gain ~10-15 %; defensible but compounding-derivation concern remains.

EUBUCCO area is correct for all three Baltics (EE +14 %, LV −2 %, LT +2 % vs census-implied). Gap is entirely in intensity.

### HU (+38.5 %) — distinct DE-proxy case

See **Correction 1** above. The HU gap is dominated by the proxy choice itself (DE TABULA values applied to Hungarian panelház that differs structurally from German GMH), not by retrofit shares, not by EUBUCCO area (which is correct), not by the unknown-cohort fallback (which already uses HU stock weights × DE archetypes).

**Verified empirically:** the agent's "Component A" concern (the `unknown` cohort using DE stock weights) is moot — `03_heat_intensity.py` already uses `hu_intensity.csv` BSO `stock_pct_hu` weights for the fallback. So the existing pipeline correctly applies Hungarian stock weights × DE archetype intensities × HU climate scaling. The over-statement is in the DE archetype intensities themselves, not in their weighting.

Refinement priority:
1. **(highest leverage)** **Build `hu_intensities.csv` from the BME TABULA brochure** (Correction 1). Switch tabula.source_country: HU; remove DE-proxy. Expected: bottom-up lands within ±5-10 % of Hotmaps (analogous to SK precedent at +2.2 %).
2. **(immediate; applied in commit YYYY)** **Update HU retrofit shares to BPIE-grounded values** based on JustReno 2025 baseline + Otthon Felujitasi (370k families, ~40-50 % envelope use = 150-185k dwellings = 3.4-4.2 %) + Panelprogram (190k panel dwellings 2001-2007, ~250-280k by 2020 = 5.7-6.4 %) + Otthon Melege (13,975 deep = 0.3 %). Revised shares: **0.88 / 0.10 / 0.02** (blend 0.949). **NOTE:** this *widens* the BU vs Hotmaps gap from +38.5 % to ~+45.6 %, because the prior 0.78/0.17/0.05 over-stated Hungarian renovation reach. The widening is academically correct — it exposes the true magnitude of the DE-proxy intensity problem.
3. Comfort-baseline cross-check: Hungarian per-dwelling heat demand at Hotmaps level = 16.4 MWh/dwelling vs DE 17.2 MWh — essentially the same. So Hungarian stock SHOULD reconcile to DE-proxy values; the gap is unlikely to be a Hungarian heating-culture effect (unlike PT). The fix is in the TABULA matrix itself (Component 1), not in a comfort coefficient.

### Cross-cutting methodological recommendations

1. **Introduce a `comfort_regime` block in the YAML schema** with fields `reference_indoor_T_c`, `operative_T_source`, `partial_heating_share`. Makes the Coelho/Magalhães-style PT fix academically auditable. Required for PT; recommended for HR (wood-stove regime); applicable for CY/MT (AC-delivered heating).
2. **Region-split proxy support**: permit one `tabula:` block per NUTS2 partition (required for HR; potentially also for ES with its 5 climate zones).
3. **Per-class proxy support**: permit one TABULA file per `building_class` (required for EE/LT class-mix proxy).
4. **Replace proxy-derived cohort shares with national-census shares** wherever the census publishes a construction-period histogram (HR DZS 2021, MT NSO 2021, PT INE 2021, HU KSH 2022, ES INE 2021, EL ELSTAT 2021 all do).
5. **Cross-check EUBUCCO area totals against national-census aggregates** and report the implied per-country area under/over-count factor in the audit doc.

---

## Updated refinement-priority summary

| Country | Gap | Highest-leverage refinement (academic) | Estimated post-fix gap |
|---|---:|---|---:|
| **PT** | +264 % | Switch ES → PT-direct LNEC TABULA + Coelho/Magalhães comfort-regime coefficient (16-18 °C) | ~+15 % (LIKELY) |
| **HU** | +39 % | Switch DE → HU-direct BME TABULA brochure | ~+5 % (LIKELY) |
| **CY** | +372 % | Calibrate TABULA against Panayiotou (2010) 47.8 kWh/m² + MFH_LOW area correction | ~+60 % (still INV, low-info structurally) |
| **ES** | +143 % | EUBUCCO MFH_LOW area correction (~−45 %) + TABULA refresh from CIEMAT/IVE brochure | ~+38 % (LIKELY) |
| **EE** | +79 % | Class-mix proxy: SE for SFH + PL for MFH | ~+30-40 % (LIKELY) |
| **LT** | +124 % | Class-mix proxy: SE for SFH + PL for MFH (longer-term: APVA-direct) | ~+60-70 % (still INV); long-term LIKELY |
| **HR** | +66 % | Regional-split proxy: HR03 ← IT-Middle, HR04 ← SI; + wood-stove comfort-derating | ~+25 % (LIKELY) |
| **EL** | +69 % | TABULA-matrix refresh from NOA brochure × Dascalaki 0.6 occupied-deflator | ~+19 % (LIKELY) |
| **MT** | +231 % | Document as low-info case; use Hotmaps as recommended benchmark | (no numerical change recommended) |

**Of the 9 INV countries, 7 have a documented academic fix path that should bring them inside the ACCEPTABLE (±25 %) or LIKELY band. The exceptions are CY and MT, which are structural low-information cases (small absolute demand × heating service partly AC-delivered).**

---

## What this session implements vs defers

**Implemented in commit (this session):**
- Correction of the `hu.yaml` and `pt.yaml` misstatements about TABULA-12 membership.
- HU retrofit-share update to BPIE-grounded 0.88/0.10/0.02 (blend 0.949) with full citation chain. Gap widens to +45.6 %, which is academically correct.
- Documentation: this audit doc; updates to each INV country's `classification_methodology.md`.

**Deferred (require manual PDF/WebTool extraction or schema extension):**
- HU-direct `hu_intensities.csv` from BME brochure (image-based PDF; manual transcription of 15 archetypes × 6 cohorts).
- PT-direct `pt_intensities.csv` from LNEC brochure.
- ES/EL/CY TABULA matrix refresh from national brochures.
- EUBUCCO building-class assignment rule investigation (ES MFH_LOW over-count fix).
- Schema extensions for region-split proxies (HR), class-mix proxies (EE/LT), and the `comfort_regime` block (PT especially).

---

## Bibliography

### Spain
- IDAE SECH-SPAHOUSEC I (2011), SPAHOUSEC II (2018), SPAHOUSEC III (2021-).
- IVE / CIEMAT (2014). *Catálogo de Tipologías Residenciales de España*. Instituto Valenciano de la Edificación.
- Ballarini I., Corgnati S.P., Corrado V. (2014). *Energy Policy* 68:273-284.
- Loga T., Stein B., Diefenbach N. (2016). *Energy & Buildings* 132:4-12.
- INE 2021 Censo de Población y Vivienda; Odyssee-Mure Spain 2026.

### Greece
- Dascalaki E.G., Droutsa K., Balaras C.A., Kontoyiannidis S. (2011). *Energy & Buildings* 43(12):3400-3409.
- Dascalaki E.G., Balaras C.A., Droutsa K., Kontoyiannidis S. (2016). Hellenic refurbishment scenarios. *Energy & Buildings*.
- Dascalaki E.G. et al. (2021). *Applied Sciences* 11(14):6254.
- ELSTAT Household Budget Survey 2022; Exoikonomo programme reporting.
- GR_TABULA Scientific Report (NOA).

### Cyprus
- Panayiotou G., Kalogirou S.A., Florides G. et al. (2010). *Energy & Buildings* 42:2083-2089.
- Pignatta et al. (2018); Serghides et al. (2015-2017) EPISCOPE outputs.
- CYSTAT 2021 Census; CYSTAT Household Energy Survey 2009.
- CY_TABULA_TypologyBrochure_CUT.pdf.

### Croatia
- DZS Croatia 2021 Census of Population, Housing and Dwellings.
- FZOEU (Environmental Protection and Energy Efficiency Fund) renovation programme reports.
- IEA Bioenergy 2021 Country Report (Croatia).
- D'Agostino L., Parker D. (2022). *Climate* 10(4):55.
- Croatia LTRS 2020 (Ministry of Physical Planning).

### Malta
- NSO Malta Census 2021 Final Report Vol. 2 (Dwelling Characteristics).
- Malta NECP 2030 (EWA Dec 2019, updated Dec 2024).
- Odyssee-MURE Malta profile.

### Portugal
- LNEC TABULA Portugal (EPISCOPE country page episcope.eu/building-typology/country/pt/).
- INE/DGEG ICESD 2020 (Inquérito ao Consumo de Energia no Sector Doméstico).
- Magalhães S.M.C., Leal V.M.S. (2014). *Energy & Buildings* 70:167-179.
- Coelho J. et al. (2017). Indoor air quality and energy poverty in Portuguese low-income households.
- Casa Eficiente 2020 (EIB-co-financed); E-Lar PRR 2024-; Fundo Ambiental envelope-renovation streams.

### Estonia, Latvia, Lithuania
- Kalamees T., Kurnitski J. (2006). Estonian wooden SFH thermal performance.
- Kuusk K., Kalamees T. et al. (2014). "Estonian typology of residential buildings — a TABULA-style classification."
- Kalamees T., Jylhä A., Tuhkanen T. et al. (2016). *Energy & Buildings* 109.
- Hamburg-Kuusik (2020) KredEx report; Estonia LTRS 2020 Annex; Statistics Estonia REL 2021 energy module.
- APVA (Aplinkos projektų valdymo agentūra) panel-renovation programme reporting (~2,200 multi-apartment buildings).
- Šadauskienė J., Stankevičius V. et al. (VGTU Vilnius Tech), "Energy performance of multi-apartment buildings in Lithuania", *Energy Procedia* 2014; later *Sustainability* papers.
- ALTUM (Latvijas Attīstības Finanšu Institūcija) panel-renovation programme (~1,900 renovated multi-apartment blocks).
- Borodineca N., Žīgure A., Krēsliņš A. (RTU). (2016). *Energy Procedia*. Latvian residential heat-consumption assessment.
- NAPE (2012) Polish TABULA Scientific Report.

### Hungary
- BME (Budapest University of Technology and Economics) TABULA brochure 2014-10-21.
- Csoknyai T., Hrabovszky-Horváth S. et al. (2016). *Energy & Buildings* 132:39-52.
- Hrabovszky-Horváth S., Pálvölgyi T., Csoknyai T., Talamon A. (2013). *Energy & Buildings* 62:475-485.
- Hrabovszky-Horváth S. (2015). BME doctoral dissertation, panelház q_h_nd before/after retrofit.
- Bene M., Ertl A., Horváth Á., Mónus G., Székely J. (2023). *Financial and Economic Review (MNB)* 22(3):123-151.
- BPIE / EUKI (2025). *JustReno: Baseline Assessment Report for Hungary*.
- Magyar Államkincstár Otthon Felujitasi Program processing report.
- Panelprogram (2001-2007); Otthon Melege (2014-2020).
- KSH Hungarian Statistical Office, MEKH (Hungarian Energy and Public Utility Regulatory Authority).
