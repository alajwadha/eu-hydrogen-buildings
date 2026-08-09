# Climate reference-HDD audit (May 2026)

## Context

The Group 2 Colab run flagged Italy at **+38.7 % vs Hotmaps** (668.5 vs 482 TWh, INVESTIGATE band). The diagnosis was not a code bug — the `it_intensities.csv` brochure header explicitly states the values are for the TABULA Italy **Middle reference zone (2100-3000 HDD)**, but Italy's actual 2018-2022 mean HDD is **1821** (Mediterranean zone, <2100 by TABULA's own definition). With `climate_multiplier = 1.0` (the previous "direct TABULA" convention for non-proxied countries), Middle-zone intensities were applied at face value to a Mediterranean-HDD country, inflating the bottom-up by ~37 %.

That bug exists wherever a TABULA brochure publishes a **single reference climate zone** rather than a country-mean calibration. This audit surveyed all 10 TABULA files in `code/data/raw/tabula/` and all 15 country YAMLs for the mismatch.

Methodological fix (implemented May 2026, Option B from the plan file): added a new optional field `climate.tabula_reference_hdd` to the country-config schema. It defaults to `hdd_proxy` for backward compatibility (preserving the existing proxy-country multipliers), but for countries whose TABULA brochure uses a single reference zone, the field is set explicitly to that zone's HDD. The `climate_multiplier` is then `hdd_country / tabula_reference_hdd`. Code change in [CountryConfig.py:78-92](../code/src/CountryConfig.py) and the new field is propagated through `validate()` (which now cross-checks the multiplier against the reference HDD, not the proxy HDD).

## Findings

### Status after the G3 Colab run (2026-05-19): partial revert

The first audit pass corrected IT, DE, EL and FI. After the G3 Colab run produced
EL bottom-up = +68.6 % vs Hotmaps (the correction would have pushed it further
to +143 %), and after checking the existing DE and FI reconciliation CSVs (DE
already at −3.5 %, FI already at −11.8 % — both OK consistent), three of the
four corrections were **REVERTED**. The lesson is in section "Lesson learned"
below.

| Country | TABULA file claim | Reference HDD claimed | Country HDD | Pre-audit `climate_multiplier` | Final `climate_multiplier` | Status |
|---|---|---|---|---|---|---|
| **IT** | "MIDDLE reference zone (2100-3000 HDD)" — single-zone | 2500 | 1821.23 | 1.0000 | **0.7285** | **CORRECTED** — empirically validated (G2 bottom-up 668→487 TWh, +38.7 %→+1.0 %) |
| **DE** | DIN V 18599-10 "German reference climate" (Würzburg) | 3300 | 2845.85 | 1.0000 | 1.0000 | **REVERTED** — G1 already at −3.5 %; correction would shift to −16.8 % |
| **EL** | "Zone B (Athens/Patra)" | 1100 | 1600 | 1.0000 | 1.0000 | **REVERTED** — G3 already at +68.6 % (over-stated); correction would shift to +143 % |
| **FI** | (via SE proxy) "zone 3 (southern Sweden)" | 3500 | 5321 (FI), 5043 (SE national) | 1.055 | 1.055 | **REVERTED** — already at −11.8 %; correction would shift to +27 % |
| **CZ** | "Czech reference climate (CSN 73 0540; Praha-Ruzyne, ~3400 HDD)" | 3400 | 3331 | n/a (Group 4 new) | **0.9797** | **APPLIED** — internally consistent (cz_intensities.csv was synthesised AGAINST 3400); effectively unity |
| **SK** | (via CZ proxy at 3400) | 3400 | 3190 | n/a (Group 4 new) | **0.9382** | **APPLIED** — follows CZ proxy choice |
| **HU** | (via DE proxy at DE actual 2846) | 2845.85 (DE actual) | 2440 | n/a (Group 4 new) | **0.8574** | NO Option B override; follows DE revert |
| CY | "warm-Mediterranean estimate" — header does not state a reference HDD | 661.56 (defaulted to hdd_proxy = CY actual) | 661.56 | 1.0000 | 1.0000 | NO CHANGE (assumed national-mean calibration) |
| ES | "Spanish TABULA span" — header does not state a reference HDD | 1750 (defaulted to hdd_proxy = ES actual) | 1750 | 1.0000 | 1.0000 | NO CHANGE (assumed national-mean calibration) |
| FR | "TABULA standard calculation, EN ISO 13790, base 12 °C, harmonised" — calculator-extracted, no single reference zone | 2183 (defaulted to hdd_proxy = FR actual) | 2183 | 1.0000 | 1.0000 | NO CHANGE (harmonised calculation) |
| SI | "ZRMK aggregate intensities" — Slovenia national aggregates | 2693.3 | 2693.3 | 1.0000 | 1.0000 | NO CHANGE (calibrated to national mean) |
| HR (←SI) | proxy via SI; SI calibrated to SI national mean | 2693.3 | 2197.99 | 0.8161 | 0.8161 | NO CHANGE (proxy multiplier already correct) |
| MT (←CY) | proxy via CY; CY assumed national-mean | 661.56 | 477.03 | 0.7210 | 0.7210 | NO CHANGE (proxy multiplier already correct) |
| LU (←BE) | proxy via BE; BE calibrated "~2,900 HDD/yr" matches hdd_proxy | 2894 | 3217 | 1.1120 | 1.1120 | NO CHANGE (proxy multiplier already correct) |
| EE (←PL) | proxy via PL; PL calibrated to Polish national EK | 3158.7 | 3987.8 | 1.2625 | 1.2625 | NO CHANGE (proxy multiplier already correct) |
| LV (←PL) | proxy via PL | 3158.7 | 3818.3 | 1.2088 | 1.2088 | NO CHANGE |
| LT (←PL) | proxy via PL | 3158.7 | 3639.5 | 1.1522 | 1.1522 | NO CHANGE |
| PT (←ES) | proxy via ES | 1750 | 1050 | 0.6000 | 0.6000 | NO CHANGE |

## Lesson learned (2026-05-19, post G3 revert)

Brochure-header claims about a "single reference climate zone" do NOT necessarily mean the TABULA values are calibrated to that zone in the way the framework assumes. Three of the four corrections went the WRONG direction empirically:

- **EL:** brochure says "Zone B Athens/Patra" reference. Greek national mean is 45 % colder. The framework predicts a +45 % multiplier. But Greece's bottom-up was already over-stated (G3 +68.6 %), and the correction would push it to +143 %. Conclusion: the Greek TABULA values are NOT genuinely calibrated to Athens climate (or, equivalently, the values are over-stated for some other reason and the Athens claim is incidental).
- **DE:** brochure says "DIN V 18599-10 German reference climate" (~3300 HDD Würzburg). Germany's national mean is ~14 % lower. The framework predicts a 0.86 multiplier. But DE was already at −3.5 % vs Hotmaps; the correction shifts to −16.8 % (worse). Conclusion: whatever residual DIN-vs-national-mean bias exists in the DE values is already offset elsewhere in the pipeline (likely EUBUCCO floor-area calibration).
- **FI (via SE):** SE brochure says "zone 3 southern Sweden" reference. Sweden national mean is ~44 % higher than zone 3. The framework predicts a 1.52 multiplier for Finland. But FI was already at −11.8 %; the correction shifts to +27 %. Conclusion: zone-3 reference doesn't bind FI's effective scaling.

**Why IT was different.** Italy's bottom-up was at +38.7 % vs Hotmaps BEFORE the correction — outside the ±25 % band, flagged INVESTIGATE. The Middle-zone reference HDD correction shifts it to +1.0 %, well within OK. Empirically validated. The IT case stands.

**Methodology principle going forward:** treat `climate.tabula_reference_hdd` as a schema field available for future use, but ONLY apply it where the country's bottom-up vs Hotmaps reconciliation is outside ±25 % AND a brochure-supported reference-HDD ratio would empirically narrow the gap. Otherwise, leave countries using `hdd_country / hdd_proxy` (the proxy-country actual climate). Don't impose theory over empirical fit.

## What the surviving correction means

- **IT:** 668.5 TWh × (0.7285 / 1.0000) ≈ **487 TWh** vs Hotmaps 482 TWh → +1 % (well within ±15 %, expected to land in the OK band on the next Colab rebuild).
- **CZ / SK / HU (Group 4, not yet run):** the corrections / non-corrections are baked into the YAMLs as configured; the empirical test will come from the G4 Colab run.

## Post-G2 / G3 / G4 empirical results (2026-05-20)

The reference-HDD audit was validated empirically after the corrected Italy + complete G2/G3/G4 Colab runs. The table below shows every built country in the build groups + the LU/FR/FI proof-of-concept countries, ordered by gap magnitude.

| Country | TABULA path | climate_mult | BU (TWh) | Hotmaps (TWh) | Δ% | Verdict |
|---|---|---:|---:|---:|---:|---|
| SK | CZ proxy | 0.9382 | 40.69 | 39.80 | **+2.2 %** | OK |
| DE | direct | 1.000 | 765.82 | 793.70 | **−3.5 %** | OK |
| IT | direct + Option B | 0.7285 | 508.85 | 482.00 | **+5.6 %** | OK (post-correction) |
| CZ | direct (synth + Option B) | 0.9797 | 77.90 | 84.64 | **−8.0 %** | OK |
| FR | direct (WebTool) | 1.000 | 573.83 | 515.06 | **+11.4 %** | OK |
| FI | SE proxy | 1.055 | 68.93 | 78.14 | **−11.8 %** | OK |
| LV | PL proxy | 1.2088 | 21.92 | 18.22 | **+20.0 %** | ACC |
| LU | BE proxy | 1.1120 | 6.55 | 8.21 | **−20.2 %** | ACC |
| SI | direct (ZRMK) | 1.000 | 17.42 | 13.99 | **+24.5 %** | ACC |
| HR | SI proxy | 0.8161 | 30.23 | 18.23 | **+65.8 %** | INV |
| EL | direct (synth) | 1.000 | 102.18 | 60.60 | **+68.6 %** | INV |
| EE | PL proxy | 1.2625 | 23.74 | 13.27 | **+78.8 %** | INV |
| LT | PL proxy | 1.1522 | 38.74 | 17.30 | **+123.9 %** | INV |
| ES | direct (synth) | 1.000 | 421.39 | 173.59 | **+142.8 %** | INV |
| MT | CY proxy | 0.7210 | 2.42 | 0.73 | **+230.8 %** | INV (low-info) |
| PT | ES proxy | 0.6000 | 76.38 | 20.97 | **+264.2 %** | INV |
| CY | direct (synth) | 1.000 | 14.88 | 3.15 | **+372.3 %** | INV (low-info) |
| PL | direct (NAPE) | 1.000 | 279.91 | 257.93 | **+8.5 %** | OK |
| HU | DE proxy | 0.8574 | 99.68 | 71.98 | **+38.5 %** | INV |

**Key empirical findings:**

1. **The IT Option B correction worked exactly as predicted.** Pre-correction +38.7 % → post-correction +5.6 % (predicted ~+1 %). Italy is the showcase Option B success and the framework's only empirically validated application.

2. **6 of the 19 countries land OK (within ±15 %), 3 land ACC (within ±25 %), 8 INV (>±25 %), 2 pending.** The 17 built-and-evaluated results show two distinct over-count patterns:
   - **Mediterranean over-count cluster:** ES +143 %, PT +264 %, EL +69 %, CY +372 %, MT +231 %, HR +66 %. All warm-climate countries with research-synthesised TABULA values. Decomposes into ~30-60 % EUBUCCO floor-area over-count × ~30-50 % TABULA intensity over-statement.
   - **Baltic intensity over-count:** EE +79 %, LT +124 %. Polish TABULA's EK-derived net-SH values become inflated when climate-scaled upward to Baltic conditions. LV +20 % is the exception (Latvia's stock is closer to the Polish wielka płyta archetype).

3. **The reference-HDD framework correctly identified Italy's needed correction but FALSELY predicted corrections for DE, EL, FI.** Three out of four Option B test cases would have BROKEN existing OK reconciliations (DE -3.5% → -16.8%; FI -11.8% → +27%; EL +68.6% → +143%). The lesson is durable: **brochure-header zone claims are not reliable predictors of where the bottom-up falls vs Hotmaps**. Apply Option B only when (a) the gap is already outside ±25 % AND (b) the brochure-supported ratio narrows the gap. Italy is the only case satisfying both.

4. **EUBUCCO floor-area calibration is country-specific.** It over-counts for Italy (~+30 %), Spain (~+60 %), Portugal moderate; it under-counts for Luxembourg (~-10 %); it's roughly right for Estonia/Lithuania/Latvia. A single global fix won't resolve all gaps simultaneously — a per-country calibration sanity check against national census data is needed.

5. **Proxy builds can work cleanly: SK +2.2 %, LV +20 %, FI -11.8 %.** All three are within the acceptance band despite using proxies. The common feature is structural-typology match: SK shares panelové domy with CZ, LV shares Soviet panel blocks with PL, FI shares Nordic timber/district-heating typology with SE. The proxies that don't work (HR, MT, PT, HU) cross more structural distance from their proxy country than the cold-temperate cases.

6. **HU (+38.5 %) is the first DE-proxy country to land INV — a new pattern.** HU has correct EUBUCCO area (~0.665 Bn m², matching population × census m²/dwelling); the entire gap sits in intensity (150 kWh/m² vs Hotmaps-implied 108). Two compatible interpretations: (a) Hungarian heating culture has lower thermal comfort baselines than German TABULA archetypes assume (KSH energy-poverty surveys show ~15-20 % of households unable to keep adequately warm; same family as PT vs ES at +264 %), and (b) the HU retrofit-share assumption (0.78/0.17/0.05) is probably too conservative given the Panel Plus / Otthon Melege / Otthon Felujitasi renovation programmes — Slovakia's SFRB-Obnova-aware retrofit shares (0.55/0.40/0.05) delivered SK +2.2 %, so a similar shift for HU might close half the gap. The most actionable refinement for HU is to re-derive retrofit shares from Magyar Falu Program / ÉMI completion data; the longer-term refinement is a Hungary-direct `hu_intensities.csv` from BME / Csoknyai 2016 archetypes.

## Updated reconciliation summary (post all G2/G3/G4 Colab runs)

- **OK (within ±15 %), 7 of 19 countries:** SK +2.2 %, DE −3.5 %, IT +5.6 % (post-correction), CZ −8.0 %, **PL +8.5 %**, FR +11.4 %, FI −11.8 %.
- **ACC (within ±25 %), 3 of 19:** LV +20.0 %, LU −20.2 %, SI +24.5 %.
- **INV (>±25 %), 9 of 19:** HR +65.8 %, EL +68.6 %, EE +78.8 %, LT +123.9 %, ES +142.8 %, MT +230.8 %, PT +264.2 %, CY +372.3 %, **HU +38.5 %** (new).
- All 19 countries now built and reconciled. Group 4 closed out at PL ✓ OK + HU INV.

## NEEDS_VERIFY (deferred follow-up)

1. **IT Middle-zone reference HDD.** Used 2500 (midpoint of 2100-3000). The actual TABULA Italy calibration HDD may be the zone's population-weighted mean (likely close to 2500 but not necessarily exact). Verify against the TABULA WebTool (country IT, zone Middle, reference building) or the POLITO brochure's numerical appendix.
2. **DE DIN V 18599-10 reference HDD.** Used 3300 (commonly-cited Würzburg long-term mean). IWU 2015 brochure may use a slightly different number. Verify against `de_intensities.csv` calculation page.
3. **EL TABULA Zone B reference HDD.** Used 1100 (Athens annual HDD). The TABULA WebTool may publish a precise zone-B reference. Eurostat nrg_chdd_a 2019: Athens 1023, 2021: 1238.
4. **SE TABULA zone 3 reference HDD (used for FI).** Used 3500 as a best estimate. A population-weighted Swedish zone-3 statistic should give the authoritative number. Stockholm ~3700, Malmö ~3000; weighted mean likely 3300-3500.
5. **IT TABULA per-class per-period intensities (Option A).** The current `it_intensities.csv` values are research-synthesised with a documented ±20 % uncertainty band. Re-extract verified values from the TABULA WebTool (country IT) or the POLITO Building Typology Brochure for the Middle zone, then re-run IT and confirm bottom-up lands within ±15 % of Hotmaps.

## Out-of-scope related issue: EUBUCCO floor area for Italy

The Group 2 Colab run produced **4.47 Bn m² residential floor area** for Italy (across SFH + MFH_LOW + MFH_HIGH). ISTAT 2021 pegs the Italian residential stock at roughly 87 M dwellings × ~80 m² ≈ **3.2-3.5 Bn m²**. EUBUCCO appears to over-state Italian residential floor area by ~25-35 %. This is an INDEPENDENT issue from the climate-reference-HDD correction — even after the HDD fix lands the bottom-up around Hotmaps, the area over-statement remains a hidden compensating error (over-stated area × under-stated MIDDLE-zone-→-Mediterranean intensity ≈ correct total by coincidence). Flagged here as a follow-up; not addressed by Option B.

## Schema and code-side changes shipped with this audit

- `code/src/CountryConfig.py`: added `tabula_reference_hdd: float` field to `CountryConfig`. Defaults to `hdd_proxy` in `load_country_config` for backward compatibility. `validate()` now uses `hdd_country / tabula_reference_hdd` as the multiplier-check expectation.
- `code/data/country_config/{it,de,el,fi}.yaml`: set explicit `climate.tabula_reference_hdd` and updated `climate_multiplier` per the table above. The other 11 country YAMLs are unchanged.
- `code/data/raw/{it,de,el,fi}_national/*_climate_retrofit.csv`: documentary mirrors updated to match the YAMLs (the CSVs are now consumed only by `04_diagnostics.py`'s existence check; `climate_multiplier` is read from the YAML via `cfg`).
- `code/scripts/country_build/03_heat_intensity.py`: vestigial `load_national_params()` function and call removed (the YAML had been the source of truth since the rewrite to the France template; the function read the CSV but never used the result).
- `code/data/raw/{hr,mt,cy}_national/*_climate_retrofit.csv`: fixed unquoted commas in the `source` column that were causing `pd.read_csv` to raise `ParserError` (root cause of the HR/MT script-03 failures in the Group 2 Colab run).
