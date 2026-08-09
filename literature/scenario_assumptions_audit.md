# Scenario & Techno-Economic Assumptions — Source Audit

**Date:** 2026-05-25
**Scope:** Every numeric assumption that feeds the Monte Carlo scenario engine and the
forthcoming COST_OPT economic-optimization run, audited against published primary sources.
**Files audited:** `code/src/Config.py` (scenario shares), `code/src/Economics.py`
(techno-economic parameters, fuel prices, financials, labour multipliers).

**Method.** Three independent research passes, each cross-checking a block of the model
against named primary sources:
- **Block A — Techno-economic** (CAPEX, lifetime, FOM/VOM, efficiency/SCOP) vs
  Danish Energy Agency Technology Data, JRC, IEA *Future of Heat Pumps*, IRENA.
- **Block B — Fuel prices & financials** (residential prices, 2050 multipliers, H2
  trajectories, discount rates, labour multipliers) vs Eurostat nrg_pc_202/204,
  Eurostat lc_lci_lev, IEA WEO 2024, OIES, European Hydrogen Observatory, Ofgem, ElCom.
- **Block C — 2050 scenario shares** (HP/DH/H2/fossil/demand by scenario) vs EU
  Reference Scenario 2024 / PRIMES, REPowerEU, EHPA, IEA, EPBD recast, Gas for Climate,
  Hydrogen Council.

**Status of this document.** The **Tier-1 corrections (plus the two grounded HP refinements)
were applied to `Economics.py` on 2026-05-25** — see §5.1 for the exact diff. The Tier-2
scenario-share items (`Config.py`) remain proposals (§5.2). The academic stance holds:
corrections are applied only with a documented primary source and rationale; no post-hoc
calibration multipliers.

---

## 1. Verdict at a glance

| Block | Solidly sourced (keep as-is) | Needs a specific fix | Reframe / re-cite |
|---|---|---|---|
| A — Techno-economic | HP CAPEX (ASHP 1200, GSHP 2000), GSHP SCOP 3.8, lifetimes, DH connection cost | Combustion-boiler CAPEX (gas/oil/biomass/resistance) too high vs DEA; ASHP SCOP 3.0 low; h2_boiler CAPEX unsupported | ASHP 2050 700 aggressive |
| B — Fuel & financial | Gas + electricity country prices (exact Eurostat match); discount rates; labour multipliers; H2 CENTRAL/SLOW/STRANDED | FI elec 180→225; oil 130→~105; biomass 60→~70; UK/CH prices all off | RAPID H2; 2050 multipliers (label as scenario assumptions) |
| C — Scenario shares | All of HIGH_HP; REF HP/DH/demand; H2_HYBRID HP/DH/fossil/demand | — | **REF fossil 0.32** (relabel/lower); **H2_HYBRID H2 0.25** (misattributed citation — reframe as stress-test) |

The single most important finding is in Block C: **H2_HYBRID's 25% residential hydrogen
share is not supported as a central projection, and the Hydrogen Council 2021 citation is a
misattribution** (that figure is all-sector abatement, not building-heat share). Keep the
number only if explicitly relabelled a deliberate high-side stress-test.

---

## 2. Block A — Techno-economic parameters (`Economics.py` TECH_PARAMS)

Benchmark: Danish Energy Agency *Technology Data for Individual Heating Plants* (the same
dataset PyPSA-Eur uses), with JRC / IEA / IRENA cross-checks.

### 2.1 Heat pumps — well-sourced, keep
| Param | Current | Benchmark | Verdict |
|---|---|---|---|
| ASHP CAPEX 2025 | 1 200 | DEA ≈ 1 196 €/kW | ✓ exact |
| GSHP CAPEX 2025 | 2 000 | DEA ≈ 1 937 €/kW | ✓ |
| GSHP SCOP | 3.8 | DEA ≈ 3.85 | ✓ |
| DH connection | 500 | Standard consumer-connection framing | ✓ |

Two HP refinements proposed:
- **ASHP SCOP 2025: 3.0 → 3.3.** EHPA/Eurovent field SCOP for air-to-water sits ~3.2–3.5;
  3.0 is the regulatory "average climate" floor, not the fleet seasonal average.
- **ASHP CAPEX 2050: 700 → 800.** A 42% reduction is at the optimistic end of IRENA/IEA
  learning curves; 800 (~33% reduction) is the more defensible central.

### 2.2 Combustion boilers — CAPEX runs high vs DEA
DEA residential boiler *investment* (€/kW, incl. installation) is materially below the
model's values. These are the clearest Block-A corrections.

| Tech | Current CAPEX 2025 | DEA-anchored recommended | FOM note |
|---|---|---|---|
| gas_boiler | 1 000 | ~420 | keep 20 |
| oil_boiler | 1 200 | ~450 | keep 25 |
| biomass_boiler | 1 600 | ~950 | FOM 40→60 (DEA higher) |
| resistance_heater | 400 | ~200 | keep 5 |
| h2_boiler | 1 400 | ~600 | keep 25 |

`h2_boiler` at 1 400 is **unsupported** — H2-ready boilers are gas-boiler + incremental
safety/materials, so DEA-consistent is ~600 (gas + ~40%). The model's inline note already
flags H2 *fuel* price (not CAPEX) as the real driver, which this correction reinforces.

### 2.3 Important caveat — CAPEX basis
DEA Technology Data is the March-2018 dataset rescaled to recent euros. If the paper cites a
**2023/2025** DEA or JRC vintage instead, ASHP installed cost sits closer to ~1 000 €/kW and
the current 1 200 is already reasonable. **Decision needed: which vintage does the paper
cite?** The combustion-boiler corrections hold across vintages; the HP numbers are
vintage-sensitive.

---

## 3. Block B — Fuel prices & financial parameters

### 3.1 Residential gas & electricity (Eurostat nrg_pc_202/204, H1 2025) — keep
Country and EU values match Eurostat 2025-S1 **exactly** (gas band D2, elec band DC, all
taxes incl.). Spot checks: EU gas 114.3 ✓, EU elec 287.2 ✓, DE gas 122 ✓, NL gas 162 ✓,
HU gas 31 ✓, SE gas 213 ✓, DE elec 384 ✓, HU elec 104 ✓.

**Two exceptions:**
- **FI electricity 180 → 225.** Eurostat 2025-S1 Finland = 22.5 c/kWh; current understates by ~45.
- **PL gas 80 — verify.** The EUR-denominated band-D2 series returned NA on the mirror;
  80 is plausible but should be confirmed against the native-PLN series at the H1-2025 rate.

### 3.2 Estimated prices (no primary source on file)
| Fuel | Current | Recommended | Source |
|---|---|---|---|
| Oil (`get_fuel_price` line 612) | 130 | ~100–110 | EC Weekly Oil Bulletin; DE heating oil ~96 €/MWh |
| Biomass (line 614) | 60 | ~70 | ENplus/German pellet market (~68–80 €/MWh) |
| District heat (line 616) | 80 | keep 80, **cite** Euroheat & Power DH Price Series | weakly sourced, value OK |

### 3.3 UK / CH prices — all four off (flagged estimates)
| | Current | Authoritative 2025 | Recommended |
|---|---|---|---|
| UK gas | 120 | Ofgem cap 6.3–7.0 p/kWh → ~74–82 | ~80 |
| UK elec | 280 | Ofgem cap 25.7–27.0 p/kWh → ~300–320 | ~310 |
| CH gas | 120 | ~0.188 USD/kWh → ~170 | ~150–170 |
| CH elec | 220 | ElCom 2025 median 29.0 Rp/kWh → ~310 | ~300 |

These are already `⚠️`-flagged in code as estimates; re-derive from Ofgem (UK) and ElCom (CH).

### 3.4 2050 fuel-price multipliers — defensible scenario assumptions
Gas 0.55, elec 0.80, oil 0.55, biomass 1.05, DH 0.80 are **directionally consistent** with
IEA WEO 2024 STEPS/APS and PRIMES. Caveat: IEA declines are wholesale/import-led; retail
(fixed network + tax components) is stickier, so **gas 0.55 and elec 0.80 are the optimistic
end**. No public source gives a clean retail index — label these as scenario assumptions, not
citations.

### 3.5 Hydrogen trajectories — CENTRAL/SLOW/STRANDED sound; RAPID is a floor
Base €200/MWh (~€6/kg) matches European Hydrogen Observatory 2024. CENTRAL→50 €/MWh
(~€1.7/kg) by 2050 is within OIES/IEA ranges. **RAPID 25 €/MWh (~€0.85/kg) is below any
sourced production cost** — relabel as a subsidised/floor bound, not a market price.

### 3.6 Discount rates — keep
5% base / 4% social / 8% private: conventional, JRC/BPIE-consistent. The 8% private rate is
on the low side of household retrofit hurdle rates (often 8–15%+) but defensible.

### 3.7 Labour-cost multipliers — keep
Calibrated against Eurostat lc_lci_lev 2024 (EU construction €30.0/h = 1.00). Spot checks:
BG 0.35→€10.5 (Eurostat 10.6) ✓; DK 1.65→€49.5 (50.1) ✓; LU 1.80→€54.0 (55.2) ✓. DE/FR at
1.30 may be marginally low (construction runs low-40s €/hr ≈ 1.35–1.45×); minor.

---

## 4. Block C — 2050 scenario shares (`Config.py` SCENARIOS)

### 4.1 REF "current-policy trend"
HP 0.45 ✓, DH 0.18 ✓ (mild high), H2 0.05 (loosely high; truer ~0–2%), demand −0.35 ✓.
**Weak point: fossil 0.32.** EU Ref 2024 (post-Fit-for-55) projects faster gas decline
(~20–25% residual). Either **relabel REF as a "frozen / current-measures" trend** (which a
32% fossil residual does fit) or **lower fossil toward ~0.25**.

### 4.2 HIGH_HP "high electrification" — best anchored, keep
HP 0.65 ✓ (REPowerEU 60M HPs/2030 + EHPA half-of-buildings + IEA *Future of Heat Pumps*),
DH 0.20 ✓, H2 0.05 (immaterial over-count), fossil 0.10 ✓, demand −0.50 ✓ (ambitious EPBD
deep-renovation bookend). Cite REPowerEU + EHPA + IEA + EPBD recast.

### 4.3 H2_HYBRID — reframe (most important finding)
HP 0.40 ✓, DH 0.20 ✓, fossil 0.15 ✓, demand −0.40 ✓. **But H2 0.25 is unsupported as a
projection:**
- Deloitte/Hydrogen Council 2023: buildings < **1%** of 2050 global H2 demand.
- 54-study meta-review + IPCC: H2 a niche (~2%) of heating energy.
- UK shelved hydrogen-town trials (2023); German H2-ready-boiler framing contested.
- The cited **Hydrogen Council 2021 "20%" figure is total cross-sector abatement, not a
  residential-heat share** — a misattribution.

**Recommendation:** keep 0.25 only if explicitly relabelled a **deliberate high-side
stress-test / sensitivity**, re-anchored to **Gas for Climate "Optimised Gas"** and
**pre-2024 UK/DE hydrogen-heating strategies**, with an explicit caveat that
IEA/IRENA/Hydrogen Science Coalition/Deloitte place real-world building H2 below ~1–2%.

---

## 5. Corrections

### 5.1 Applied to `Economics.py` on 2026-05-25 (signed off)

Vintage decision: cite the **latest DEA Technology Data** (most academically defensible).
Under that vintage ASHP installed cost (~1196) supports keeping CAPEX 2025 = 1200; the two
HP refinements below are separately grounded (EHPA field SCOP; IRENA/IEA central learning).

| Parameter | Before | After | Basis |
|---|---|---|---|
| gas_boiler capex_2025 / 2050 | 1000 / 950 | **420 / 400** | DEA residential condensing, installed |
| oil_boiler capex_2025 / 2050 | 1200 / 1150 | **450 / 430** | DEA |
| biomass_boiler capex_2025 / 2050 | 1600 / 1400 | **950 / 850** | DEA |
| biomass_boiler fom | 40 | **60** | DEA (fuel-handling O&M) |
| resistance_heater capex_2025 / 2050 | 400 / 350 | **200 / 180** | DEA direct-electric |
| h2_boiler capex_2025 / 2050 | 1400 / 1100 | **600 / 550** | gas + ~40% H2-ready premium |
| hp_air scop_2025 | 3.0 | **3.3** | EHPA/Eurovent field SCOP (3.0 = ErP floor) |
| hp_air capex_2050 | 700 | **800** | IRENA/IEA central learning (~33%, not 42%) |
| hp_air capex_2025 | 1200 | 1200 (kept) | latest DEA ~1196 |
| ELEC FI | 180 | **225** | Eurostat nrg_pc_204 2025-S1 |
| GAS UK / CH | 120 / 120 | **80 / 160** | Ofgem cap 2025 / Sep-2025 |
| ELEC UK / CH | 280 / 220 | **310 / 300** | Ofgem cap 2025 / ElCom 2025 |
| oil price base | 130 | **105** | EC Weekly Oil Bulletin |
| biomass price base | 60 | **70** | ENplus/German pellet market |
| DH price base | 80 | 80 (kept) | now cited: Euroheat & Power DH Price Series |
| RAPID H2 trajectory | (unlabelled) | relabelled | documented as a subsidised floor |

Validated: `python code/src/Economics.py` runs clean; heat pumps and district heat now lead
the merit order across DE/SE/FR/PL/IT/UK/CH in 2030 and 2050 (the expected result with
DEA-correct boiler CAPEX + ETS2). No code-logic changes, only data values + comments.

### 5.2 Tier-2 — `Config.py` scenario shares (still proposals, need paper-level call)
- REF fossil 0.32: relabel REF as "frozen/current-measures" **or** lower to ~0.25.
- H2_HYBRID H2 0.25: relabel as a deliberate stress-test + re-cite (§4.3).
- PL gas 80: verify against the native-PLN Eurostat series (the EUR mirror returned NA).

These are scenario *narrative/labelling* decisions rather than data errors, so they are held
for an explicit call rather than auto-applied.

---

## 6. Primary sources

- Danish Energy Agency — *Technology Data for Individual Heating Plants* (boilers, HPs).
- JRC — *Technology Data* (2023); *Towards net-zero emissions in the EU energy system by 2050*.
- IEA — *The Future of Heat Pumps* (2022); *World Energy Outlook 2024*; *Global Hydrogen Review 2024*.
- IRENA — *Heat Pump Costs and Markets* (2022).
- Eurostat — nrg_pc_202 (gas), nrg_pc_204 (electricity), 2025-S1; lc_lci_lev (labour, 2024); env_clc_hdd.
- EC Weekly Oil Bulletin; Ofgem price cap 2025; ElCom tariff data 2025; Euroheat & Power DH Price Series.
- European Hydrogen Observatory (2024); OIES ET32 green-hydrogen-imports (2024).
- EU Reference Scenario 2024 / PRIMES; REPowerEU; EHPA REPowerEU & Heat Pump Action Plan; EPBD recast.
- Gas for Climate 2050 ("Optimised Gas"); Hydrogen Council (2021, 2023); Hydrogen Science Coalition;
  Deloitte hydrogen-demand outlook; 54-study hydrogen-heating meta-review (ScienceDirect 2023).
