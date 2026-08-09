# TABULA intensity-matrix verification (2026-05-22)

## Purpose

Every `code/data/raw/tabula/*_intensities.csv` was research-synthesised and
flagged `NEEDS_VERIFY`. This document records a verification pass (four parallel
research agents, 2026-05-22) that cross-checked each matrix against the primary
TABULA brochures / scientific reports and, where obtainable, the **machine-
readable `tabula-calculator.xlsx`** (the official EPISCOPE source). It downgrades
the flag per file and — critically — documents a **coupling problem** that
governs whether the value corrections can actually be applied.

All "expected" values are TABULA **calculated net `q_h_nd`** (net useful space
heating, EN ISO 13790 quasi-steady), the correct reference target. Realisation
(measured-vs-calculated) is handled separately by the `comfort_regime` deflator.

## Per-file verdict

| File | Verdict | Key finding | Propagates to |
|---|---|---|---|
| `fr_intensities.csv` | **VERIFIED** | Reproduces `tabula-calculator.xlsx` exactly under its documented class/cohort mapping. | — |
| `si_intensities.csv` | PARTIALLY-VERIFIED | Maps cleanly onto ZRMK aggregates; Hotmaps independently corroborated by the ZRMK national balance. Source limitation: MFH_LOW = MFH_HIGH (ZRMK has one multi-unit class). | HR (proxy) |
| `pl_intensities.csv` | PARTIALLY-VERIFIED | EK→net derivation internally consistent; clean PL reconciliation (+8.5 %). 2011-2020 cells slightly low. | EE/LV/LT (proxy) |
| `cz_intensities.csv` | PARTIALLY-VERIFIED | Reconciles well (CZ −8 %, SK +2 %). **Source is STU-K** (`CZ_TABULA_ScientificReport_STU-K.pdf`), not Lupišek/UCEEB — citation fix. SFH pre-1945 (245) ~10 % high. | SK (proxy) |
| `uk_intensities.csv` | PARTIALLY-VERIFIED | All 18 cells within ~15 % of Cambridge Housing Model / EHS. Values are SAP-**modelled** (above metered for pre-1919 solid wall — performance gap). | — |
| `be_intensities.csv` | PARTIALLY-VERIFIED | pre-1945 + 1971-90 sound; **1946-70, 1991-2010, 2011-20, post-2020 too LOW** (file applied an NZEB decay not in TABULA; calculator post-2020 ≈ 64-89, file ≈ 26-30). | **LU (proxy ×1.112)** |
| `it_intensities.csv` | matrix TOO LOW | pre-1990 SFH/TH/MFH **15-30 % below** the POLITO zona-E archetypes (SFH pre-1945 260 vs ~335). DHW 18 vs brochure 15. Would be VERIFIED if raised. | — |
| `el_intensities.csv` | PARTIALLY-VERIFIED | pre-1990 SFH/MFH **~20-30 % high** vs NOA Zone-B calculated demand. Single MFH class. | — |
| `de_intensities.csv` | NEEDS_VERIFY | **Unphysical SFH age-inversion** (1946-70 = 308 > pre-1945 = 294); post-2010 new-build cells 30-50 % high (ignore EnEV2009/GEG). Mid cohorts OK. | HU (proxy) |
| `at_intensities.csv` | NEEDS_VERIFY | Same SFH inversion (275 > 265) + post-2010 cells high (OIB 2014/2023 deliver lower). Old/mid OK. | CH (proxy) |
| `se_intensities.csv` | NEEDS_VERIFY | Older SFH (209, 197) ~15-25 % high; net-vs-"energianvändning" ambiguity unresolved; zone-3 (3500) vs national (5043) reference inconsistency. Highest-risk. | **FI (proxy) + EE/LT (class-mix SFH)** |
| `es_intensities.csv` | NEEDS_VERIFY | IVE brochure publishes only *final* energy (efficiency-confounded), not net `q_h_nd`. Net values plausible but unverifiable from the brochure; needs the WebTool. | — |
| `cy_intensities.csv` | NEEDS_VERIFY | Brochure exposes SFH-coastal only: period-2 (65) should be ~50; MFH unverifiable. Low impact (MT proxy only). | MT (proxy) |

**Tally:** 1 VERIFIED (FR), 6 PARTIALLY-VERIFIED (SI, PL, CZ, UK, BE, EL), 5
NEEDS_VERIFY (DE, AT, SE, ES, CY), 1 too-low-but-reconciles (IT).

## The coupling problem (critical — read before applying any correction)

The matrices do **not** stand alone. Each country's bottom-up is
`intensity × climate_multiplier × retrofit_blend × (Option-B / comfort_regime /
area_correction)`, and the synthesised matrices were implicitly sized so the
product reconciles with Hotmaps. Verification shows several matrices diverge
from primary TABULA — but **the divergence is partly offset by the other
layers**, so the bottom-up still reconciles. Concretely:

- **IT** matrix is ~25 % *too low*, yet IT reconciles at **+5.6 %** — because the
  Option B `tabula_reference_hdd = 2500` multiplier (0.73) was compensating.
  Raising the matrix to true POLITO values **without** re-deriving Option B
  would push IT to ~**+28 % (INV)**.
- **SE** matrix older-SFH is *too high*, yet SE reconciles at **−4 %**. Lowering
  it pushes SE more negative **and** worsens FI (−12 %, SE proxy) and the EE/LT
  class-mix.
- **BE** recent cohorts are *too low*; raising them worsens BE (+19 %) but
  **improves LU** (−20 %, BE proxy).
- **DE/AT** the new-build over-statement is on tiny cohorts (small effect), but
  the SFH age-inversion is a genuine unphysical bug.

**Implication:** correcting individual matrix values is **not** a safe
find-replace. It cascades through proxy children and breaks currently-OK
reconciliations, because some of the reconciliation was achieved by offsetting
errors. This is the honest characterisation for the OIES paper: the model's
Hotmaps agreement is partly a *calibrated* outcome of a coupled input system,
not an independent prediction from first-principles TABULA values.

## The authoritative fix path

The FR/BE agent obtained the **machine-readable `tabula-calculator.xlsx`**, from
which net `q_h_nd` can be extracted exactly for every TABULA-12 country (FR was
verified this way). The rigorous fix is a **coordinated re-build of the
intensity layer**:
1. Re-extract every TABULA-12 matrix (DE, AT, IT, ES, EL, CY, PL, CZ, SI, SE, BE,
   FR) from `tabula-calculator.xlsx` at true net `q_h_nd`.
2. Re-derive each country's `climate_multiplier` / Option-B `tabula_reference_hdd`
   against the corrected matrices.
3. Re-fit the `comfort_regime` deflators (which are *measured/calculated* ratios)
   against the corrected calculated values.
4. Re-run all countries; the area/occupancy corrections (census-grounded) are
   unaffected and carry through.

This is a scoped future work-package, not a piecemeal edit. Until then the
matrices stay as-is (they reconcile), with this verification on record.

## Applied now (zero-risk, no rerun)

- **CZ source attribution corrected** to STU-K (`CZ_TABULA_ScientificReport_STU-K.pdf`)
  in `cz_intensities.csv` header + `sk.yaml` / Czech + Slovak methodology docs —
  a citation fix with no value change.

## Sources

- `tabula-calculator.xlsx` (EPISCOPE official, sheet `Calc.Set.Building`).
- POLITO Italian TABULA brochure (zona E `Q_H_nd`); NOA Greek Scientific Report
  (Table 4.6); IVE Spanish brochure; CUT Cyprus brochure; NAPE Polish report;
  STU-K Czech report; ZRMK Slovenian typology; Swedish TABULA brochure (MdH);
  VITO Belgian Scientific Report 2011; IWU German brochure + Loga/Stein/
  Diefenbach (2016) E&B 132:4-12; AEA Austrian report; Cambridge Housing Model /
  EHS 2022-23 (UK).

## Proposed corrections: current -> recommended (NOT yet applied)

Per the coupling caveat above, these are **documented but not applied** (applying them in isolation breaks reconciliation; they belong to the coordinated re-extraction). "Current" = the live value in the CSV today; "Rec." = the verification-recommended net q_h_nd; rows where the two match are omitted. Values kWh/m2/yr.


### FR France (`fr_intensities.csv`)

VERIFIED -- reproduces tabula-calculator.xlsx exactly; no value change.


### UK United Kingdom (`uk_intensities.csv`)

PARTIALLY-VERIFIED -- all 18 cells within ~15% of Cambridge Housing Model / EHS; no value change. Caveat: SAP-MODELLED, above metered for pre-1919 solid wall (performance gap).


### SI Slovenia (`si_intensities.csv`)

PARTIALLY-VERIFIED -- values map onto ZRMK aggregates; no value change (MFH_LOW = MFH_HIGH is a real ZRMK single-class limitation).


### ES Spain (`es_intensities.csv`)

NEEDS_VERIFY -- the IVE brochure publishes only FINAL energy (efficiency-confounded), not net q_h_nd; current values are plausible but not verifiable from the brochure. Net q_h_nd must come from the TABULA WebTool. No change made.


### PL Poland (`pl_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | 2011-2020 | 95 | **110** | EK 141 x gas eta ~0.92 -> ~110-115; current slightly low |

### CZ Czechia (`cz_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | pre-1945 | 245 | **225** | Czech uninsulated SFH net-SH typically ~200-230; current 245 high edge |

### DE Germany (`de_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | pre-1945 | 294.2 | **245** | IWU EFH A/B/C avg; current reads like a worst-archetype / non-q_h_nd figure |
| SFH | 1946-1970 | 307.9 | **230** | fixes unphysical inversion (current 1946-70 > pre-1945); IWU EFH D/E |
| SFH | 1971-1990 | 182.2 | **165** | high edge; IWU EFH F/G/H |
| SFH | 2011-2020 | 91.9 | **65** | EnEV 2009/2016 cut SFH below ~70 |
| SFH | post-2020 | 84.2 | **50** | GEG 2020 |
| MFH_LOW | pre-1945 | 236 | **185** | IWU RH+MFH A/B/C |
| MFH_LOW | 1971-1990 | 146.2 | **125** | IWU |
| MFH_LOW | 2011-2020 | 71.2 | **52** | IWU K/L |
| MFH_LOW | post-2020 | 59.9 | **42** | GEG |
| MFH_HIGH | pre-1945 | 172.2 | **150** | IWU GMH B/C |
| MFH_HIGH | 1991-2010 | 87.9 | **75** | estimate (no GMH post-1978) |
| MFH_HIGH | 2011-2020 | 72.1 | **52** | proxy MFH new-build |
| MFH_HIGH | post-2020 | 59.9 | **42** | proxy |

### AT Austria (`at_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | 1946-1970 | 275 | **205** | fixes unphysical inversion (current 275 > pre-1945 265); AEA EZFH Wiederaufbau |
| SFH | 2011-2020 | 85 | **55** | OIB 2014 NZEB delivers ~45-65 |
| SFH | post-2020 | 70 | **45** | OIB 2023 |
| MFH_LOW | 1971-1990 | 140 | **120** | OIB Wv 1979 |
| MFH_LOW | 2011-2020 | 70 | **48** | OIB 2014 |
| MFH_LOW | post-2020 | 58 | **40** | OIB 2023 |
| MFH_HIGH | 1946-1970 | 165 | **140** | AEA (high edge) |
| MFH_HIGH | 1971-1990 | 135 | **115** | Plattenbau |
| MFH_HIGH | 1991-2010 | 85 | **72** | OIB |
| MFH_HIGH | 2011-2020 | 70 | **45** | OIB 2014 |
| MFH_HIGH | post-2020 | 58 | **38** | OIB 2023 |

### IT Italy (`it_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | pre-1945 | 260 | **330** | POLITO zona-E Q_H,nd ~335 (current 15-30% too low) |
| SFH | 1946-1970 | 220 | **300** | POLITO 275-344 |
| SFH | 1971-1990 | 170 | **140** | POLITO 1976-90 = 136 (slightly high now) |
| SFH | 1991-2010 | 115 | **90** | POLITO 1991-2005 = 92 |
| MFH_LOW | pre-1945 | 180 | **220** | POLITO TH 200-250 |
| MFH_LOW | 1946-1970 | 155 | **190** | POLITO TH 173-241 |
| MFH_HIGH | pre-1945 | 150 | **180** | POLITO MFH 200-250 / AB 133-194 |
| MFH_HIGH | 1946-1970 | 125 | **150** | POLITO MFH 153-170 |
| (DHW) | all | 18 | **15** | POLITO brochure Q_W,nd ~= 15 |

### EL Greece (`el_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | pre-1945 | 170 | **115** | NOA Zone-B calc demand (124.7) minus DHW |
| SFH | 1946-1970 | 170 | **115** | NOA Zone-B |
| SFH | 1971-1990 | 140 | **95** | NOA transitional |
| MFH_LOW | pre-1945 | 115 | **90** | NOA Zone-B (100.7) minus DHW |
| MFH_LOW | 1946-1970 | 115 | **90** | NOA Zone-B |
| MFH_LOW | 1971-1990 | 100 | **80** | NOA |
| MFH_HIGH | pre-1945 | 115 | **90** | NOA Zone-B (single MFH class) |
| MFH_HIGH | 1946-1970 | 115 | **90** | NOA Zone-B |
| MFH_HIGH | 1971-1990 | 100 | **80** | NOA |

### BE Belgium (`be_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | 1946-1970 | 225 | **270** | tabula-calculator.xlsx BE.N (current 17% low) |
| SFH | 1991-2010 | 115 | **150** | calculator (current 25% low) |
| SFH | 2011-2020 | 65 | **113** | calculator BE.06 (current 43% low) |
| SFH | post-2020 | 30 | **89** | calculator (current applied an NZEB decay not in TABULA) |
| MFH_LOW | 1946-1970 | 180 | **210** | calculator mean(TH, MFH-Small) |
| MFH_LOW | 1991-2010 | 95 | **125** | calculator |
| MFH_LOW | 2011-2020 | 55 | **82** | calculator |
| MFH_LOW | post-2020 | 28 | **65** | calculator |
| MFH_HIGH | 1971-1990 | 130 | **154** | calculator |
| MFH_HIGH | 2011-2020 | 52 | **77** | calculator |
| MFH_HIGH | post-2020 | 26 | **64** | calculator |

### SE Sweden (`se_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | pre-1945 | 209 | **185** | BETSI net range; current 209 at/above top (net-vs-energianvandning ambiguity -> re-extract) |
| SFH | 1946-1970 | 196.8 | **170** | current 197 likely high |

### CY Cyprus (`cy_intensities.csv`)

| class | cohort | current | rec. | why |
|---|---|--:|--:|---|
| SFH | 1991-2010 | 65 | **50** | CUT brochure SFH class-3 = 47.6 |
