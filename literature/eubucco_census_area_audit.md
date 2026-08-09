# EUBUCCO vs national-census floor-area audit (2026-05-21)

## Purpose

The bottom-up model computes residential heat demand as **floor area x intensity**.
Floor area comes from EUBUCCO v0.2 (`footprint x floors x useable_fraction`).
This document audits EUBUCCO's residential floor-area total against each
country's **national-census conventional-dwelling floor area**, for all 27
EU countries, and sets the policy for when (and why) a per-country
`eubucco.area_correction` is applied.

It was written to resolve a methodological concern: the area corrections in
the INVESTIGATE-cluster work (Corrections 3-8 in
[inv_countries_academic_refinements.md](inv_countries_academic_refinements.md))
were applied **only to countries whose bottom-up disagreed with Hotmaps**,
which makes the *decision to correct* effectively Hotmaps-triggered even
though each correction *value* came from a census. That is a form of
fitting-to-the-benchmark. This audit replaces that with an explicit,
benchmark-independent rule grounded in EUBUCCO's own documented data quality.

## Three different "floor areas"

There are three distinct quantities, and they do **not** agree:

1. **Census conventional-dwelling area** (smallest). National statistics
   offices count occupied + vacant *conventional dwellings* and report their
   useful/usable floor area. Excludes: common circulation (stairwells),
   unconverted basements/attics, mixed-use commercial floors, and
   non-conventional residential structures (summer houses, dachas, sheds).
2. **EUBUCCO residential building area** (largest). All buildings tagged
   residential, `footprint x floors x 0.85`. Includes everything the census
   excludes, **plus** floor-count error wherever building height is imputed
   rather than observed.
3. **Hotmaps 2015 useful-demand area basis** (middle-to-large). Hotmaps'
   own building-stock model uses a gross, all-residential basis closer to
   EUBUCCO than to census.

**Key consequence:** anchoring the model uniformly to census would bias it
~30 % *low* against Hotmaps (the validation benchmark), because Hotmaps is
not census-based. A blanket census correction was tested and **breaks 10
otherwise-reconciled countries** (FI -58 %, SI -49 %, SK -46 %, PT -44 %,
SE -29 %, PL -28 %, EL -27 %, RO -25 %, EE, LU). It is therefore rejected as
a uniform rule. Census is used as an **independent benchmark / uncertainty
band**, and as the calibration target only where a documented mechanism
shows EUBUCCO over-states the *heated* stock.

## The 27-country audit

EUBUCCO = raw residential heated_floor_area (Mm^2, pre-correction); Census =
national-census conventional-dwelling floor area (Mm^2, central estimate);
ratio = Census / EUBUCCO; obs-h = EUBUCCO observed-height share (Table 1,
Milojevic-Dupont et al. 2023) where known; corr = applied area_correction.

| CC | EUBUCCO | Census | ratio | obs-h | corr | status |
|----|--------:|-------:|------:|------:|-----:|--------|
| AT | 820  | 471  | 0.57 | 7%   | 0.575 | **corrected** -- imputed floors |
| BE | 840  | 660  | 0.79 | -    | 1.0  | native (reconciles) |
| BG | 455  | 347  | 0.76 | low-cov | 1.0 | native (comfort_regime only) |
| CY | 200  | 100  | 0.50 | 100% | 0.50 | **corrected** -- occupancy/unheated stock |
| CZ | 548  | 450  | 0.82 | -    | 1.0  | native (reconciles) |
| DE | 4502 | 4070 | 0.90 | -    | 1.0  | native (reconciles) |
| DK | 510  | 356  | 0.70 | 0%   | 0.70 | **corrected** -- imputed floors |
| EE | 114  | 51   | 0.45 | 100% | 0.50 | **corrected** -- occupancy/unheated stock |
| EL | 898  | 630  | 0.70 | low-cov | 1.0 | native (comfort_regime only) |
| ES | 4082 | 2500-3300 | 0.61-0.81 | 95% | 0.613 | **corrected** -- occupancy/unheated stock |
| FI | 526  | 248  | 0.47 | -    | 1.0  | native (census excludes heated cottages) |
| FR | 4397 | 3460 | 0.79 | -    | 1.0  | native (reconciles) |
| HR | 315  | 188  | 0.60 | 1% / low-cov | 0.59 | **corrected** -- imputed floors |
| HU | 664  | 377  | 0.57 | 3% / low-cov | 0.57 | **corrected** -- imputed floors |
| IE | 301  | 237  | 0.79 | 13% / OSM | 0.78 | **corrected** -- imputed floors |
| IT | 4471 | 3234 | 0.72 | -    | 1.0  | native (reconciles) |
| LT | 200  | 104  | 0.52 | 0%   | 0.52 | **corrected** -- imputed floors |
| LU | 38   | 33   | 0.86 | -    | 1.0  | native (reconciles) |
| LV | 105  | 68   | 0.65 | -    | 1.0  | native (ACC; control) |
| MT | 42   | 42   | 1.00 | 100% | 1.0  | native (area OK; comfort_regime only) |
| NL | 982  | 1000 | 1.02 | -    | 1.0  | native (reconciles) |
| PL | 1716 | 1139 | 0.66 | -    | 1.0  | native (reconciles) |
| PT | 1054 | 575  | 0.55 | low-cov | 1.0 | native (comfort_regime only) |
| RO | 1179 | 730  | 0.62 | low-cov | 1.0 | native (comfort_regime only) |
| SE | 614  | 452  | 0.74 | -    | 1.0  | native (census excludes heated cottages) |
| SI | 174  | 72   | 0.41 | -    | 1.0  | native (reconciles) |
| SK | 297  | 157  | 0.53 | -    | 1.0  | native (reconciles) |

**Headline finding:** EUBUCCO's residential floor area exceeds the census
conventional-dwelling area in **every** EU country (ratio 0.41-1.02). The
over-count is universal -- but its *cause* and *whether it matters* differ.

## Two over-count mechanisms

The EUBUCCO/census gap decomposes into two physically distinct, independently
documented mechanisms. A correction is applied only where one of them is
established for that country.

### Mechanism A -- imputed-floor area error (EUBUCCO data quality)

EUBUCCO floor area = footprint x **floors**, and floors are derived from
building height. Per the v0.2 documentation, only **16.6 %** of floors and
**43.2 %** of heights are observed; **56.7 %** of heights are ML-estimated.
Where a country's observed-height share is low, its floor counts -- hence
floor area -- are modelled and can be systematically over-stated, **even
when the footprints come from a high-quality national cadastre.**

From Table 1 of Milojevic-Dupont et al. (2023), the observed-height share for
the corrected countries is: **DK 0 %, LT 0 %, HR 1 %, HU 3 %, AT 7 %, IE
13 %** -- all heavily imputed. HR and HU additionally sit on the paper's
explicit low-coverage list ("Bulgaria, Croatia, Greece, Hungary, Romania and
Portugal"); IE is OSM-sourced (no national footprint dataset). For these six,
the area over-count is a **documented EUBUCCO data-quality artefact**, and the
`area_correction` calibrates the imputed area back to the census.

### Mechanism B -- stock utilization / occupancy (unheated standing stock)

For **ES, EE, CY** the EUBUCCO observed-height share is high (ES 95 %, EE
100 %, CY 100 %), so the floor area *per building* is accurate -- Mechanism A
does not apply. Yet EUBUCCO still counts far more residential floor area than
the census, because it counts the **entire standing stock**, a large share of
which is **vacant, seasonal, or auxiliary and is not continuously heated**:

- **EE:** 440,113 buildings classified SFH vs ~220,000 single-family houses
  in the census. The ~220k excess is Estonia's *suvila* (summer-house/dacha)
  stock -- closed and unheated through the heating season.
- **CY:** 697,301 residential buildings vs 491,545 census dwellings; Cyprus
  has ~30 % vacancy plus a large holiday/tourism + unfinished-building stock.
  Mild winters mean the empty units are not heated.
- **ES:** ~3.8 M vacant + ~3.5 M secondary dwellings (~28 % of the ~26 M
  stock), barely heated in a mild climate.

The `area_correction` here calibrates EUBUCCO's *total* stock to the *heated*
(occupied conventional-dwelling) stock. This is **not** the heating-regime
correction: `comfort_regime` reduces the intensity of *occupied* homes
(partial-room, lower setpoint), while occupancy reduces the *count* of heated
homes. For ES and CY the two factors are independent and multiplicative
(occupancy x intensity-regime) -- not double-counting.

**Mechanism B is a deliberate MODELING CHOICE about the heated base, not an
EUBUCCO data defect -- and it is benchmark-independent.** EUBUCCO represents
these countries' stock correctly; the buildings exist and their areas are
right. The choice is that a *residential heat-demand* model should heat the
*occupied* dwelling stock, not vacant investment flats, closed summer houses,
or unfinished tourism stock. Both inputs to the correction are independent of
Hotmaps: the **value** is census floor area / EUBUCCO floor area (e.g. ES
2,500 principal-residence Mm^2 / 4,082 = 0.613), and the **decision to apply
it** rests on national-census vacancy rates plus documented heating culture
(Mediterranean empty flats and Estonian *suvila* are unheated; Finnish/Swedish
cottages are winterised and heated, so they are NOT excluded). Neither input
is the Hotmaps gap. This is the same standard the data-quality corrections
(Mechanism A) are held to: a correction is legitimate only if both its value
and the decision to apply it are independent of the benchmark being validated
against.

**Honest limitation.** The Mechanism-B decision rule ("is the vacant/seasonal
stock heated?") is grounded in census + heating-culture evidence but carries a
genuine judgment element, and it does **not** by itself separate the corrected
countries from the uncorrected ones: several *native* (uncorrected) countries
also have high vacancy/secondary shares (Italy ~30 %, Portugal ~30 %, France
~18 % with second homes) yet reconcile with Hotmaps without an occupancy
correction, because their full-stock-times-intensity product already matches
the benchmark. In other words, occupancy is a *real and legitimate* effect but
is **not a sufficient stand-alone classifier**; the corrections rest on the
*combination* of (documented mechanism A or B) and (benchmark divergence), and
that combination is disclosed per country in the all-27 occupancy audit below.
This is the central honesty caveat of the area methodology and is reported as
such rather than hidden.

### Why the gap is NOT corrected in the "native" countries

- **Reconciling countries (BE, CZ, DE, FR, IT, LU, NL, PL, SI, SK, LV):**
  the EUBUCCO-native bottom-up already agrees with the independent Hotmaps
  demand benchmark. EUBUCCO's gross basis matches Hotmaps' gross basis here;
  the census is simply the third (smaller, net-dwelling) quantity. Forcing a
  census correction would bias these below their own demand benchmark with no
  physical justification.
- **Nordic cottage countries (FI, SE):** the census conventional-dwelling
  area *under*-states the heated stock, because Finnish/Swedish secondary and
  cottage stock (mokki, fritidshus) is winterised and heated -- the opposite
  of the Estonian/Cypriot/Spanish case. EUBUCCO's larger area is the better
  heated-stock proxy here, so census is the wrong anchor.
- **comfort_regime countries (BG, EL, PT, RO):** these over-state via the
  *intensity* layer (partial/sub-comfort heating), already handled by
  `comfort_regime`. Their EUBUCCO areas are not separately corrected; the
  census gap is reported in the band but is partly the Hotmaps/EUBUCCO-vs-
  census definitional offset, not a heated-stock defect.

## Policy

1. **EUBUCCO native is the primary floor-area basis** for the bottom-up. It
   shares a gross, all-residential basis with the Hotmaps validation benchmark.
2. **National census floor area is reported for all 27 countries as an
   independent benchmark / uncertainty band** (this document + the
   `reconciliation_benchmarks.census_floor_area` field in each country YAML).
3. **A per-country `eubucco.area_correction` is applied only where a
   documented mechanism (A or B above) establishes that EUBUCCO over-states
   the *heated* residential stock** -- never because the bottom-up disagreed
   with Hotmaps. Each correction's YAML cites its mechanism + observed-height
   share or occupancy evidence.
4. The correction value is the census/EUBUCCO ratio (Mechanism A) or the
   heated-fraction implied by census occupancy + auxiliary-stock analysis
   (Mechanism B), with the definitional caveats below.

## Caveats on the census numbers

The census anchors carry ~+/-20-30 % definitional uncertainty and are NOT
mutually consistent in definition across countries -- this is exactly why
census is a band, not a hard correction target:

- **Useful vs livable vs gross.** RO census reports *livable* area (rooms
  only); useful area (incl. kitchen/bath/hall) is ~50 % larger. IT/EL publish
  useful area for *occupied* dwellings only. Definitions differ by office.
- **Principal vs total stock.** PT's 112.5 m^2 mean is habitual-residence
  only; ES 2,500 Mm^2 is principal residences (total stock ~3,300 Mm^2 with
  the ~28 % vacant/secondary share). Using total vs principal swings the
  ratio materially (ES 0.61 -> 0.81).
- **Auxiliary/non-conventional stock.** Summer houses, dachas and saunas are
  excluded from "conventional dwellings" but counted by EUBUCCO; whether they
  are heated is country-specific (unheated in EE/ES/CY; heated in FI/SE).

## All-27 occupancy / heated-base audit (2026-05-21)

Extends the Mechanism-B lens to every country, from the latest national
censuses (Eurostat `cens_21` where the office figure was not retrievable).
"Non-primary %" = vacant + secondary/seasonal share of the total dwelling
stock. "Heated?" = whether that non-primary stock is realistically heated in
winter (climate + heating culture). "Corr." = the area/occupancy correction
status in the model.

| CC | occupied % | non-primary % | non-primary heated? | model treatment |
|----|-----------:|--------------:|---------------------|-----------------|
| BE | ~98 | ~2  | heated | native |
| NL | 97.5 | 2.5 | heated | native |
| DE | 95.7 | 4.3 | heated | native |
| SE | ~95 | (cottages separate) | heated | native |
| LU | ~90 | ~10 | heated | native |
| FI | 88.5 | 11.5 (+free-time sep) | mixed/heated | native |
| PL | 88.3 | 11.7 | mixed (cold) | native |
| HU | ~87 | ~13 | mixed (cold) | **corrected (Mech A)** |
| IE | 86.7 | 10.8 | mixed | **corrected (Mech A)** |
| LT | ~85 | ~15 | mixed (cold) | **corrected (Mech A)** |
| CZ | 83.9 | 16.1 (incl chaty) | mixed (cold) | native |
| AT | 81.8 | ~18 | mixed (Alpine) | **corrected (Mech A)** |
| FR | 81.8 | 18.2 | mixed | native |
| SI | 80.8 | 19.2 | mixed (cold) | native |
| SK | ~77 | ~23 | mixed (cold) | native |
| LV | 76.2 | 23.8 | mixed (cold) | native |
| EE | 76.0 | 24.0 | **unheated** (suvila) | **corrected (Mech B)** |
| RO | ~75 | ~25 | mixed (cold) | native (comfort_regime) |
| CY | 75.3 | 24.7 | **unheated** (mild) | **corrected (Mech B)** |
| MT | 74.5 | 25.5 | **unheated** (mild) | native (comfort_regime) |
| IT | ~73 | ~27 | **unheated** (mild) | **native** -- see finding |
| ES | 69.6 | 30.4 | **unheated** (mild) | **corrected (Mech B)** |
| PT | 69.5 | 30.5 | **unheated** (mild) | native (comfort_regime) |
| EL | ~65 | ~35 (2011) | **unheated** (mild) | native (comfort_regime) |
| HR | 59.9 | ~35 | **unheated** (mild coast) | **corrected (Mech A)** |
| BG | ~61 | ~39 | **unheated** (depop. rural) | native (comfort_regime) |
| DK | ~96 | ~4 (+cottages sep) | mixed | **corrected (Mech A)** |

(Flags: EL is 2011 census, ELSTAT 2021 dwelling table only released Jul 2024;
LV/PL/RO/SI/SK/MT report a single occupied-vs-unoccupied figure so vacant and
secondary cannot be cleanly split; LU/LT splits are approximate.)

### The central finding (and limitation)

**Occupancy does not separate the corrected countries from the uncorrected
ones.** The clearest evidence is the Mediterranean trio with near-identical
profiles:

| | non-primary % | climate | model treatment | gap vs Hotmaps |
|---|--:|---|---|--:|
| ES | 30.4 | mild | occupancy correction 0.613 | -3.6 % |
| IT | ~27 | mild | **none** (Option B ref-HDD) | +5.6 % |
| PT | 30.5 | mild | **none** (comfort_regime) | +3.6 % |

All three have ~30 % largely-unheated non-primary stock. Yet ES is given an
explicit occupancy/area correction, while IT reconciles through the
`tabula_reference_hdd = 2500` intensity correction and PT through the
`comfort_regime = 0.10` intensity deflator. Applying an occupancy correction
to IT or PT *on top of* their existing intensity corrections would push them
to roughly -23 % and -27 % (double-counting the same physical over-statement
through two layers).

**What this means, stated honestly:**

1. The physical over-statement in the mild-climate, high-vacancy countries is
   real and the same in kind (unheated non-primary stock + partial-room
   heating regime). The model corrects it through *whichever single
   documented lever* (area/occupancy, `tabula_reference_hdd`, or
   `comfort_regime`) brings that country in line with the independent Hotmaps
   benchmark. The levers are all primary-source-grounded, but **the choice of
   which lever to use per country is informed by the benchmark** -- that is
   where Hotmaps information legitimately enters.
2. Therefore the per-country corrections are **not derivable from occupancy
   (or any single attribute) a priori**, and the model's Hotmaps
   reconciliation should be read as *benchmark-anchored selection among
   physically-grounded corrections*, not as an independent prediction. This is
   the honest characterisation for the OIES paper.
3. The cold-climate countries with substantial non-primary shares (LV 24 %,
   SK 23 %, RO 25 %, SI 19 %, PL 12 %, CZ 16 %) are left native because (a)
   their vacant stock is partly heated (frost protection in cold winters, so
   the heated fraction exceeds the occupied fraction) and (b) their
   EUBUCCO-native bottom-up already reconciles. Both are defensible, but (b)
   is again a benchmark-informed choice.

**No mechanical change is made to IT/PT/EL/BG/MT here** -- applying occupancy
on top of their intensity corrections would double-count. The audit is
reported so the reader can see the full occupancy picture and judge each
country's correction. This transparency is the deliverable; pretending a clean
a-priori rule exists would be the dishonest alternative.

## Sources

- Milojevic-Dupont N., Wagner F., Nachtigall F. et al. (2023). "EUBUCCO v0.1:
  a global building stock database." *Scientific Data* 10:147. DOI
  10.1038/s41597-023-02040-2 (Table 1 attribute coverage; Technical
  Validation low-coverage list; ES Basque/Navarra OSM-infill note).
- EUBUCCO v0.2 documentation: docs.eubucco.com/v0.2 (height 43.2 % observed /
  56.7 % ML-estimated; floors 16.6 % observed; conflation hierarchy).
- National census floor-area sources, per country: Statistik Austria GWZ 2021;
  Statbel (BE); NSI Bulgaria Housing Fund 2022; CYSTAT 2021; CSU (CZ); Zensus
  2022 (DE); Danmarks Statistik BOL101 (DK); Statistics Estonia REL 2021;
  ELSTAT 2021; INE Censos 2021 (ES); Tilastokeskus (FI); INSEE (FR); DZS 2021
  (HR); KSH 2022 (HU); CSO Census 2022 (IE); ISTAT Censimento 2021 (IT);
  Statistics Lithuania REL 2021; STATEC RP2021 (LU); CSB 2021 (LV); NSO Census
  2021 (MT); CBS (NL); GUS NSP 2021 (PL); INE Censos 2021 (PT); INS RPL 2021
  (RO); SCB (SE); SURS 2021 (SI); SU SR 2021 (SK).
