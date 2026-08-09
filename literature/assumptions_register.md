# Model Assumptions and Parameters Register
## eu-hydrogen-buildings | All files | Complete audit

**Purpose:** Single source of truth for every number, assumption, and parameter in the model.
Every entry has: the value, where it appears in the code, the source, whether it is validated or provisional, and any flags for Abdul.

**Maintained by:** Ali Alajwad
**Last updated:** April 2026

> **Withdrawn scenarios.** The `REF`, `HIGH_HP` and `H2_HYBRID` rows below are a
> historical record only. Those three runs were withdrawn in June 2026 and must not be
> used for any new result. The only scenarios are `CURRENT_POLICIES`, `STATED_POLICIES`,
> `NET_ZERO` and `H2_PUSH`; their shares and outputs differ materially from the
> withdrawn ones, and `src/Config.check_scenario()` raises if a withdrawn name is
> passed. Read the rows below as provenance, never as current assumptions.
**Status key:**
- ✅ Validated — sourced from peer-reviewed or authoritative institutional data
- ⚠️ Provisional — best estimate, needs literature validation or Abdul sign-off
- 🔲 Pending — not yet sourced, placeholder only
- ❌ Conflict — contradicts another value in the model (needs resolution)

---

## Part 1: Config.py — Core Model Settings

### 1.1 Geography and Time

| Parameter | Value | Source | Status | Notes |
|---|---|---|---|---|
| Countries modelled | EU27 + CH + UK = 29 | Eurostat country coverage | ✅ | "EL" used for Greece in Eurostat; "GR" used in some contexts — check consistency |
| Model years | 2025, 2030, 2040, 2050 | Standard practice | ✅ | 5-year resolution up to 2030 then 10-year steps — consistent with IEA WEO |
| Baseline heat demand year | 2015 | Hotmaps dataset reference year | ✅ | Hotmaps uses ~2015 as reference |

### 1.2 Technology CAPEX — Config.py (OLD values, superseded by Economics.py)

⚠️ **CONFLICT FLAG:** Config.py and Economics.py have different CAPEX values for the same technologies. Config.py is used by Simulation.py; Economics.py is used for LCOH. This must be resolved before the optimisation step. Economics.py values are better-sourced.

| Technology | Config.py 2025 | Economics.py 2025 | Difference | Action needed |
|---|---|---|---|---|
| gas_boiler | €1,100/kW | €1,000/kW | −€100 | ⚠️ Reconcile — use Economics.py value (JRC-sourced) |
| oil_boiler | €1,200/kW | €1,200/kW | 0 | ✅ Consistent |
| biomass_boiler | €1,600/kW | €1,600/kW | 0 | ✅ Consistent |
| resistance_heater | €400/kW | €400/kW | 0 | ✅ Consistent |
| hp_air | €1,200/kW | €1,200/kW | 0 | ✅ Consistent |
| hp_ground | €2,000/kW | €2,000/kW | 0 | ✅ Consistent |
| district_heat | €500/kW | €500/kW | 0 | ✅ Consistent |
| h2_boiler | €1,400/kW | €1,400/kW | 0 | ✅ Consistent |

**✅ RESOLVED (Apr 2026):** Config.py gas_boiler CAPEX updated to €1,000/kW (JRC). All other CAPEX values were already consistent.

### 1.3 Fuel Prices — Config.py (OLD values, superseded by Economics.py)

❌ **CONFLICT FLAG:** Config.py BASE_PRICES_2025 are completely different from Economics.py country-specific prices. Config.py uses wholesale-like prices; Economics.py uses Eurostat residential end-user prices.

| Carrier | Config.py 2025 (€/MWh) | Economics.py 2025 EU avg (€/MWh) | Source in Economics.py |
|---|---|---|---|
| gas | 55 | 114.3 | Eurostat nrg_pc_202 H1 2025 |
| oil | 80 | 130 | ⚠️ Estimate |
| biomass | 40 | 60 | ⚠️ Estimate |
| electricity | 120 | 287.2 | Eurostat nrg_pc_204 H1 2025 |
| district_heat | 80 | 80 | ⚠️ Estimate (coincidentally same) |
| hydrogen | 150 | 200 | EHO 2024 (~€6/kg) |

**✅ RESOLVED (Apr 2026):** Config.py BASE_PRICES_2025 updated to Eurostat residential end-user prices (gas: €114.3/MWh, electricity: €287.2/MWh, hydrogen: €200/MWh). PRICE_MULTIPLIERS_2050 updated to match Economics.py trajectories. Simulation.py now uses correct prices.

### 1.4 Monte Carlo Settings

| Parameter | Value | Source/Rationale | Status |
|---|---|---|---|
| N_MONTE_CARLO_SAMPLES | 200 | Convergence testing (informal) | ⚠️ Formal convergence test not done — see Appendix TODO |
| RNG_SEED | 42 | Reproducibility | ✅ Standard practice |

### 1.5 Scenario Technology Share Targets (2050)

| Scenario | HP share | DH share | H2 share | Fossil share | Demand reduction |
|---|---|---|---|---|---|
| REF | 45% | 18% | 5% | 32% | 35% |
| HIGH_HP | 65% | 20% | 5% | 10% | 50% |
| H2_HYBRID | 40% | 20% | 25% | 15% | 40% |

**Sources and status:**
| Value | Source | Status |
|---|---|---|
| REF HP 45% | IEA WEO 2025: HP share reaches 45% globally by 2050 in NZE | ✅ |
| HIGH_HP HP 65% | IEA NZE Europe-specific scenario (higher than global avg) | ⚠️ Validate exact IEA NZE Europe figure |
| H2 5% (REF/HIGH_HP) | EC Hydrogen Strategy; REpowerEU buildings sector target | ⚠️ REpowerEU is silent on buildings specifically — validate |
| H2 25% (H2_HYBRID) | Hydrogen Council 2021 scenario; REpowerEU 20Mt target | ⚠️ Provisional — flag to Abdul |
| DH 18-20% | Euroheat & Power current penetration; modest growth assumed | ⚠️ Validate against Euroheat & Power projections |
| REF demand reduction 35% | Hotmaps scenario documentation; EC Long-Term Strategy | ⚠️ Validate against IEA NZE 2050 European buildings |
| HIGH_HP demand reduction 50% | IEA NZE 2050: deep renovation + efficiency | ⚠️ Check IEA NZE Europe buildings efficiency targets |
| H2_HYBRID demand reduction 40% | Between REF and HIGH_HP | ⚠️ Interpolated — validate |

---

## Part 2: Simulation.py — Monte Carlo Sampling

### 2.1 Demand uncertainty

| Parameter | Distribution | Parameters | Source/Rationale | Status |
|---|---|---|---|---|
| demand_reduction_2050 | Normal | mean=scenario target, σ=0.05 | σ=5% = ±1 SD gives 30-40% for REF | ⚠️ σ value is heuristic — no literature source |
| demand_shape_p (power-law exponent) | Uniform | [0.8, 1.8] | Governs pace of demand reduction; 1.0=linear | ⚠️ Range is heuristic |

### 2.2 Technology share uncertainty

| Parameter | Distribution | Parameters | Status |
|---|---|---|---|
| hp_share_2050 | Normal | mean=scenario, σ=0.05 | ⚠️ σ heuristic |
| dh_share_2050 | Normal | mean=scenario, σ=0.03 | ⚠️ σ heuristic |
| h2_share_2050 | Normal | mean=scenario, σ=0.03 | ⚠️ σ heuristic |
| hp_shape_p | Uniform | [0.7, 2.0] | ⚠️ Range heuristic |
| dh_shape_p | Uniform | [0.8, 2.2] | ⚠️ Range heuristic |
| h2_shape_p | Uniform | [1.0, 2.5] | ⚠️ H2 slower rollout assumption — heuristic |
| hp_ground_share | Uniform | [0.1, 0.5] | ⚠️ GSHP is 10-50% of HP stock — heuristic, validate vs EHPA |

### 2.3 Price uncertainty

| Parameter | Distribution | Parameters | Status |
|---|---|---|---|
| price multipliers (all carriers) | Log-normal | mean=0, σ=0.15 | ⚠️ σ=15% is heuristic; literature range for gas price uncertainty is higher (30-50%) |

### 2.4 Technology share baseline (2025)

Hardcoded in `tech_shares_for_year()`:

| Parameter | Value | Source | Status |
|---|---|---|---|
| base_hp | 0.18 (18%) | EHPA market data 2023 | ⚠️ EU average HP share ~18% per EHPA — validate exact figure |
| base_dh | 0.12 (12%) | Euroheat & Power 2023 | ⚠️ EU average DH share — validate |
| base_h2 | 0.0 (0%) | H2 boilers negligible today | ✅ |
| base_fossil | 0.60 (60%) | Complement of HP+DH+biomass | ⚠️ Derived, not independently sourced |
| base_biomass | 0.10 (10%) | Eurostat nrg_d_hhq biomass share | ⚠️ Rough estimate — validate |
| resistance_heater fixed | 0.02 (2%) | Small and stable share | ⚠️ Fixed regardless of scenario — heuristic |

### 2.5 Fossil fuel split

| Parameter | Value | Source | Status |
|---|---|---|---|
| gas share of fossil | 0.80 (80%) | Eurostat nrg_d_hhq: gas dominates fossil heating | ⚠️ EU average; country variation is large (NL near 100%, GR near 0%) |
| oil share of fossil | 0.20 (20%) | Complement of gas | ⚠️ Country variation significant |

### 2.6 HP feasibility modulation

`hp_tgt = params["hp_share_2050"] * (0.4 + 0.6 * hp_feas)`

| Parameter | Value | Meaning | Status |
|---|---|---|---|
| 0.4 (intercept) | 0.4 | Even in zero-feasibility regions, 40% of HP target is achieved | ⚠️ Heuristic — no source |
| 0.6 (slope) | 0.6 | Additional 60% of target is feasibility-weighted | ⚠️ Heuristic |

---

## Part 3: BuildingStock.py — Building Stock Construction

### 3.1 HP and District Heat Feasibility Scores

Hardcoded in `build_hp_dh_feasibility()`:

| Building type | HP feasibility | DH feasibility | Source | Status |
|---|---|---|---|---|
| SFH | 0.9 | 0.3 | Expert judgment / literature | ⚠️ High HP suitability (garden space, low heat load); low DH (dispersed) |
| MFH_HIGH | 0.5 | 0.8 | Expert judgment / literature | ⚠️ HP harder in dense multi-family; DH economical at high density |
| OTHER | 0.6 | 0.4 | Expert judgment | ⚠️ Intermediate assumption |

**Flag to Abdul:** These are the most consequential undocumented assumptions in the model. They directly determine how much HP and DH can be deployed. Need literature sources — candidate: Hotmaps HP feasibility study; EHPA technical guidelines; IEA HP for buildings report.

### 3.2 UK Building Type Mapping (TS044)

| Accommodation type | Mapped to | Rationale | Status |
|---|---|---|---|
| Detached / semi-detached / terraced | SFH | Standard housing taxonomy | ✅ |
| Purpose-built flats / maisonettes / tenements | MFH_HIGH | Multi-storey / multi-unit | ✅ |
| Converted flats / commercial conversions | MFH_HIGH | Multi-unit regardless of origin | ⚠️ Debatable — some are effectively SFH-like |
| Caravan / mobile / temporary | OTHER | Non-standard | ✅ |

### 3.3 UK data limitation

Scotland uses England and Wales building-type shares uniformly. Documented in README and limitations section. ✅

---

## Part 4: Policy.py — Country Policy Parameters

### 4.1 Carbon Prices

| Year | LOW (€/tCO2) | CENTRAL (€/tCO2) | HIGH (€/tCO2) | Sources |
|---|---|---|---|---|
| 2025 | 30 | 55 | 70 | ETS1 current trading range | ⚠️ |
| 2027 | 45 | 75 | 100 | ETS2 launch; price cap = €45 | ⚠️ BNEF: €75 central |
| 2030 | 70 | 122 | 200 | BNEF central: €122; PRIMES: €71-261 | ⚠️ Wide range — use CENTRAL |
| 2035 | 100 | 150 | 250 | Interpolated + Enerdata trend | ⚠️ Validate with Abdul |
| 2040 | 130 | 180 | 300 | Enerdata: "almost doubles by 2040 vs 2027" | ⚠️ |
| 2050 | 150 | 200 | 350 | Literature uncertain | ⚠️ Flag to Abdul |

Sources: BloombergNEF ETS2 Market Outlook (2025); Enerdata POLES model; PRIMES EC impact assessment; ICE ETS2 futures.

### 4.2 Fuel CO2 Content

| Fuel | Value (tCO2/MWh) | Source | Status |
|---|---|---|---|
| Natural gas | 0.202 | IPCC AR6 / DEFRA emission factors | ✅ |
| Oil (heating) | 0.265 | IPCC AR6 / DEFRA | ✅ |
| Biomass | 0.0 | EU Renewable Energy Directive accounting | ✅ |
| District heat | 0.080 | EU average 2025 (gCO2/kWh) | ⚠️ Now superseded by country-specific values in Economics.py — update Policy.py to use get_district_heat_co2() |
| Hydrogen (green) | 0.0 | By definition (electrolysis from renewables) | ✅ |

### 4.3 Grid Carbon Intensity (gCO2/kWh)

| Country | 2025 | 2030 | 2040 | 2050 | Source | Status |
|---|---|---|---|---|---|---|
| PL | 600 | 400 | 150 | 30 | EMBER 2024 actuals (662); EEA Fit-for-55 trajectory | ⚠️ NECP pending |
| DE | 350 | 200 | 80 | 15 | EMBER 2024 actuals (371); EEA trajectory | ⚠️ NECP pending |
| FR | 80 | 55 | 25 | 8 | EMBER 2024 actuals (~85); nuclear-dominated | ⚠️ NECP pending |
| SE | 45 | 30 | 15 | 5 | EMBER 2024; hydro + nuclear | ✅ Relatively stable |
| UK | 180 | 90 | 30 | 8 | EMBER 2024; rapid offshore wind | ⚠️ NECP pending |
| CH | 50 | 30 | 12 | 5 | IEA 2023 Switzerland; hydro + nuclear | ⚠️ Validate vs SFOE data |
| CY | 500 | 280 | 100 | 20 | Island grid, gas-heavy | ⚠️ High uncertainty — island grid |
| MT | 450 | 250 | 90 | 15 | Island grid | ⚠️ High uncertainty |
| All others | Various | Various | Various | Various | EEA Fit-for-55 trajectories | ⚠️ NECPs pending for PL, DE, FR, IT, CZ, RO, HU, BG, SK |

**NECP pull needed for:** PL, DE, FR, IT, CZ, RO, HU, BG, SK (9 countries — largest heat markets).

### 4.4 Gas Grid Coverage

| Country | Value | Source | Status |
|---|---|---|---|
| NL | 0.90 | ACER Gas Factsheet; Eurostat nrg_d_hhq | ⚠️ |
| UK | 0.85 | National Grid / OFGEM | ⚠️ |
| IT | 0.80 | ACER; Italian gas distributor data | ⚠️ |
| DE | 0.75 | BDEW (German Energy and Water Industries) | ⚠️ |
| SE | 0.05 | Energiföretagen Sverige | ⚠️ Near-zero — correct |
| FI | 0.05 | Energiavirasto (Finnish Energy Authority) | ⚠️ |
| MT | 0.02 | Essentially no gas grid | ✅ |
| All others | Various | Estimated from Eurostat nrg_d_hhq gas share in residential heating | ⚠️ All values are estimates — ACER data is the authoritative source |

**Flag to Abdul:** All gas grid coverage values are secondary estimates. The authoritative source is ACER's Gas Factsheet and national gas network operators. These values should be validated before the paper is submitted.

### 4.5 Boiler Bans

All values sourced from EHPA Boiler Ban Tracker (November 2025) and national legislation. EU-wide baseline from EPBD 2024.

Key values already well-sourced. Notable provisional values:
- Germany `replacement_fossil_ban_delayed = 2035` — scenario assumption (political backlash), not announced policy ⚠️
- Switzerland cantonal implementation varies — federal target only ⚠️
- Poland, Romania, Hungary delayed timelines — consistent with national positions but not formally legislated ⚠️

### 4.6 Switzerland H2 Import Prices (CORRECTED)

| Year | LOW (€/MWh) | CENTRAL (€/MWh) | HIGH (€/MWh) | Sources |
|---|---|---|---|---|
| 2030 | 70 | 90 | 150 | OIES ET08 (€3/kg=€90/MWh); OIES ET32 (€60-80 short pipeline) | ✅ |
| 2035 | 55 | 70 | 120 | Interpolated from OIES/IEA trajectories | ⚠️ |
| 2040 | 45 | 55 | 90 | PwC: EU ~€2/kg=€60/MWh by 2050; ScienceDirect 2025: <€85/MWh | ⚠️ |
| 2050 | 35 | 50 | 75 | PwC €60/MWh; ScienceDirect €85/MWh upper bound | ⚠️ Validate with Abdul/OIES |

**Previous values (€180/€80) were wrong and have been corrected.**

### 4.7 ETS2 Pass-Through

| Scenario | Rate | Source | Status |
|---|---|---|---|
| Base | 100% | Conservative assumption (full pass-through) | ⚠️ |
| Sensitivity | 75% | EC impact assessment ETS2 (2023); regulated tariffs | ⚠️ The 75% figure is an estimate — validate with EC impact assessment document |

---

## Part 5: Economics.py — LCOH Module

### 5.1 Technology CAPEX (EUR/kW thermal, EUR2024)

| Technology | 2025 | 2050 | Sources | Status |
|---|---|---|---|---|
| gas_boiler | 1,000 | 950 | JRC Technology Data (2023) central; Danish Energy Agency (2023) | ✅ |
| oil_boiler | 1,200 | 1,150 | JRC Technology Data (2023) | ✅ |
| biomass_boiler | 1,600 | 1,400 | Danish Energy Agency (2023); JRC (2023) | ✅ |
| resistance_heater | 400 | 350 | JRC Technology Data (2023) | ✅ |
| hp_air | 1,200 | 700 | IEA Future of Heat Pumps (2022): USD 1,200/kW; IRENA (2022): EUR 800-1,500/kW; 40% reduction by 2050 | ✅ |
| hp_ground | 2,000 | 1,400 | IEA (2022); Danish Energy Agency (2023) | ✅ |
| district_heat | 500 | 450 | JRC Technology Data (2023); IEA District Heating (2021) | ✅ |
| h2_boiler | 1,400 | 1,100 | IEA Global Hydrogen Review (2023); Hydrogen Council (2021) | ✅ |

### 5.2 Technology Lifetimes (years)

| Technology | Value | Source | Status |
|---|---|---|---|
| gas_boiler | 20 | JRC: 15-25 years, central 20 | ✅ |
| oil_boiler | 20 | JRC | ✅ |
| biomass_boiler | 20 | JRC | ✅ |
| resistance_heater | 20 | JRC | ✅ |
| hp_air | 20 | IEA: 15-25 years | ✅ |
| hp_ground | 25 | Ground loop: 50+ years; HP unit: 20-25 years | ✅ |
| district_heat | 30 | Infrastructure-heavy | ✅ |
| h2_boiler | 20 | Similar to gas boiler | ✅ |

### 5.3 Fixed O&M (EUR/kW/year)

| Technology | Value | Source | Status |
|---|---|---|---|
| gas_boiler | 20 | JRC: EUR 15-25/kW/year | ✅ |
| oil_boiler | 25 | JRC | ✅ |
| biomass_boiler | 40 | Higher due to fuel handling | ✅ |
| resistance_heater | 5 | Minimal maintenance | ✅ |
| hp_air | 25 | IEA: EUR 20-30/kW/year | ✅ |
| hp_ground | 30 | IEA | ✅ |
| district_heat | 10 | Consumer-side only | ✅ |
| h2_boiler | 25 | Analogous to gas boiler | ⚠️ No specific H2 boiler O&M data found — gas boiler analogy |

### 5.4 Variable O&M (EUR/MWh_useful)

| All technologies | 1-4 | ⚠️ All provisional estimates — no specific source | ⚠️ |

### 5.5 Efficiency / COP

| Technology | 2025 | 2050 | Source | Status |
|---|---|---|---|---|
| gas_boiler | 0.92 | 0.94 | JRC / EHPA; condensing boiler LHV | ✅ |
| oil_boiler | 0.90 | 0.90 | JRC | ✅ |
| biomass_boiler | 0.88 | 0.90 | JRC | ✅ |
| resistance_heater | 0.98 | 0.99 | Electrical efficiency ~1.0 | ✅ |
| hp_air SCOP | 3.0 | 3.5 | IEA/EHPA EU average SCOP; EU Regulation 813/2013 | ✅ |
| hp_ground SCOP | 3.8 | 4.3 | IEA; Danish Energy Agency | ✅ |
| district_heat | 0.95 | 0.97 | Distribution losses | ✅ |
| h2_boiler | 0.90 | 0.92 | Slightly lower than gas (H2 combustion) | ⚠️ Limited specific data — flag to Abdul |

### 5.6 Discount Rate

| Scenario | Value | Source | Status |
|---|---|---|---|
| Base | 5.0% real pre-tax | BPIE (2024): 4-6% real; IEA/IRENA convention | ✅ |
| Social | 4.0% real | EU guidelines; JRC social rate | ✅ |
| Private | 8.0% real | BPIE (2024) private consumer perspective | ✅ |

### 5.7 Fuel Prices (EUR/MWh, residential end-user, H1 2025)

| Carrier | EU average | Country range | Source | Status |
|---|---|---|---|---|
| Natural gas | 114.3 | €31 (HU) to €213 (SE) | Eurostat nrg_pc_202 H1 2025 | ✅ |
| Electricity | 287.2 | €104 (HU) to €384 (DE) | Eurostat nrg_pc_204 H1 2025 | ✅ |
| Heating oil | 130 | Estimated | ⚠️ No Eurostat residential oil price table used — estimate only |
| Biomass | 60 | Estimated | ⚠️ EU wood pellet average — estimate only |
| District heat | 80 | Estimated | ⚠️ Euroheat & Power average — estimate only |
| Hydrogen | 200 | ~€6/kg in EU | European Hydrogen Observatory (2024) | ✅ |

**UK and Switzerland gas/electricity prices:** Estimated (not in Eurostat nrg_pc_202/204) ⚠️

### 5.8 Hydrogen Price Trajectories (EUR/MWh)

| Scenario | 2025 | 2030 | 2035 | 2040 | 2050 | Sources | Status |
|---|---|---|---|---|---|---|---|
| RAPID | 200 | 70 | 50 | 35 | 25 | Optimistic IEA/BNEF scenario | ⚠️ |
| CENTRAL | 200 | 90 | 70 | 55 | 50 | OIES ET08 (€3/kg=€90/MWh in 2030); ScienceDirect 2025 | ✅ |
| SLOW | 200 | 130 | 100 | 80 | 65 | Delayed scale-up scenario | ⚠️ |
| STRANDED | 200 | 180 | 160 | 140 | 120 | H2 fails to scale in buildings | ⚠️ |

### 5.9 Climate-Adjusted Annual Full-Load Hours

`annual_hours = 2000 × (country_HDD / 2800)`

| Parameter | Value | Source | Status |
|---|---|---|---|
| Base annual hours | 2,000 | EU reference assumption | ⚠️ Standard but not explicitly sourced |
| EU average HDD | 2,800 | Eurostat env_clc_hdd; climate normal 1991-2020 | ✅ |
| Country HDD values | Various | Eurostat env_clc_hdd; Hotmaps regional demand dataset | ⚠️ Values are estimates pending formal Hotmaps HDD extraction |
| Finland | 5,200 HDD → 3,714 hours | | ⚠️ |
| Cyprus | 900 HDD → 643 hours | | ⚠️ |
| Germany | 3,200 HDD → 2,286 hours | | ⚠️ |

### 5.10 COP Climate Multipliers

| Country group | Multiplier | Basis | Status |
|---|---|---|---|
| Cold (FI, SE, EE) | 0.85-0.88 | EU Regulation 813/2013 climate zones | ⚠️ |
| Temperate (DE, FR, UK) | 0.96-1.00 | Reference climate | ✅ |
| Warm (ES, PT) | 1.15-1.18 | Mediterranean climate | ⚠️ |
| Hot (CY, MT) | 1.30-1.35 | Sub-tropical | ⚠️ |
| Source | EHPA (2023) Eurovent study; EU Regulation 813/2013 (ErP Directive) | | ⚠️ Exact values are estimates — validate against EHPA Eurovent study |

### 5.11 District Heat CO2 Content (gCO2/kWh, country-specific)

| Country | 2025 | 2050 | Source | Status |
|---|---|---|---|---|
| Poland | 300 | 30 | EEA (2024); coal-dominated DH | ⚠️ |
| Sweden | 35 | 3 | EEA (2024); largely decarbonised | ⚠️ |
| Germany | 140 | 15 | EEA (2024) | ⚠️ |
| EU fallback | 80 | 8 | EEA EU average | ⚠️ |
| Source for all | EEA (2024) district heating emission factors; Euroheat & Power statistics | | ⚠️ Exact values are secondary estimates — Euroheat & Power is the primary source |

### 5.12 Fuel Price Trajectories (multipliers on 2025 base)

| Carrier | 2030 | 2040 | 2050 | Rationale | Status |
|---|---|---|---|---|---|
| Gas | 0.90 | 0.70 | 0.55 | Declining demand → lower prices | ⚠️ IEA WEO reference |
| Electricity | 0.95 | 0.85 | 0.80 | Wholesale falls, network costs rise | ⚠️ Estimated |
| Oil | 0.90 | 0.70 | 0.55 | Demand decline | ⚠️ Estimated |
| Biomass | 1.05 | 1.05 | 1.05 | Supply pressure | ⚠️ Estimated |
| District heat | 0.95 | 0.85 | 0.80 | Decarbonising → lower fuel cost | ⚠️ Estimated |

**All trajectory multipliers are provisional estimates. Flag to Abdul for IEA WEO 2024/PRIMES validation.**

---

## Part 6: Outstanding Conflicts and Priority Actions

### Priority 1 — Must fix before optimisation (Step 5)

1. ✅ **RESOLVED** — Config.py updated to Eurostat residential prices. (Apr 2026)

2. ✅ **RESOLVED** — gas_boiler CAPEX updated to €1,000/kW (JRC). (Apr 2026)

3. **HP/DH feasibility scores** — the most consequential undocumented assumptions. Must source from literature before publication.

### Priority 2 — Fix before paper submission

4. **Variable O&M** — all technologies use provisional €1-4/MWh. Find JRC or IEA Technology Perspectives data.

5. **H2 boiler O&M** — no specific source. Use gas boiler analogy until better data found.

6. **Oil, biomass, district heat consumer prices** — not from Eurostat (unlike gas and electricity). Source Eurostat nrg_d_hhq or Eurostat energy price statistics.

7. **UK and Switzerland energy prices** — not in Eurostat price statistics. Source from OFGEM (UK) and SFOE/Elcom (Switzerland).

8. **Gas price multiplier trajectories** — provisional. Validate against IEA WEO 2024 STEPS or PRIMES.

9. **Monte Carlo uncertainty ranges** — all σ and range parameters are heuristic. Consider calibrating against published scenario fan charts (e.g. IEA WEO demand scenarios).

10. **NECP grid intensity** — 9 priority countries need NECP data pulled.

### Priority 3 — Before final submission

11. **COP climate multipliers** — validate exact values against EHPA Eurovent study.

12. **Scenario shares (HP, H2, DH)** — validate each against specific IEA NZE, EC LTS, Hydrogen Council scenario documents with page references.

13. **N_MONTE_CARLO_SAMPLES = 200** — add formal convergence test (Appendix figure).

14. **Gas/fossil split (80/20)** — validate against Eurostat country-level data.

---

## Part 7: What Is Well-Documented vs What Needs Work

### Well-documented ✅
- Technology CAPEX (Economics.py) — IEA, IRENA, JRC
- Technology lifetimes — JRC
- Technology efficiencies/COP — IEA, EHPA, EU Regulation
- Fuel prices: gas and electricity — Eurostat H1 2025
- Green hydrogen price — EHO 2024
- Switzerland H2 import prices — OIES ET08/ET32 (corrected)
- Carbon prices — BNEF, Enerdata, PRIMES
- Boiler bans — EHPA Boiler Ban Tracker, national legislation
- Grid carbon intensity (2025 actuals) — EMBER 2024
- Discount rates — BPIE 2024, IEA convention
- Building type mapping — Eurostat, ONS

### Needs work ⚠️
- HP/DH feasibility scores — most critical gap
- Variable O&M — all technologies
- Oil, biomass, DH consumer prices — not from Eurostat
- UK and Switzerland energy prices — not in Eurostat
- Fuel price trajectories 2030-2050 — provisional multipliers
- Grid carbon intensity 2030-2050 — NECPs needed
- Monte Carlo uncertainty ranges — all heuristic
- Scenario technology share targets — need specific IEA/EC page references
- Gas grid coverage — secondary estimates
- COP climate multipliers — validate against EHPA Eurovent

### Placeholder / not sourced 🔲
- V&OM for H2 boiler — no specific data exists yet
- District heat consumer prices (oil, biomass) — needs Eurostat nrg_d_hhq pull

---

## 2026-05-14 update — Country labour cost multipliers

Added to `code/src/Economics.py`. CAPEX and FOM now scale by national labour cost.

**Source:** Eurostat `lc_lci_lev` — Hourly labour costs, construction (NACE F), 2024 levels in EUR (LCS2020-based + LCI extrapolation). EU27 mean construction = €30.0/h, range €10.6 (BG) → €55.2 (LU). https://ec.europa.eu/eurostat/databrowser/view/lc_lci_lev/

**Formula:**
- `CAPEX_country = CAPEX_anchor × [(1 − L) + L × M]`
- `FOM_country   = FOM_anchor   × [(1 − FOM_LABOUR_SHARE) + FOM_LABOUR_SHARE × M]`

where:
- L = `LABOUR_SHARE_OF_CAPEX[tech]`: gas_boiler 0.30, oil_boiler 0.30, biomass 0.30, electric 0.20, hp_air 0.40, hp_ground 0.55, district_heat 0.50, h2_boiler 0.35
- M = `LABOUR_COST_MULTIPLIER[country]`: range 0.35 (BG) → 1.80 (LU); EU27 anchor = 1.00
- FOM_LABOUR_SHARE = 0.70 (70% of O&M is field-service labour)

**Effect on 2025 LCOH** (relative to old uniform-CAPEX assumption):
- CEE/Baltics/Balkans: HP_air ~2–7% lower, HP_ground ~3–11% lower, gas boiler ~3–10% lower
- Mid-range (IE, IT, ES): ±2% on most techs
- Nordic/Benelux/CH: HP_air ~+1–6%, HP_ground ~+2–10%, gas boiler ~+1–8%

**Status:** ✅ Validated against Eurostat 2024. Validate with Abdul UN/SAMI labour data if preferred.

---

## 2026-05-14 update — Heat demand by NUTS region (all three levels)

Added per-NUTS-level heat demand aggregation tables to enable regional analysis and reporting in country profiles.

**Source primary:** `code/data/processed/building_stock_nuts3.csv` (Hotmaps 2015 regional residential heat demand baseline, aggregated by NUTS3 region and building type by `code/src/BuildingStock.py`).

**Source for names:** `code/data/raw/gisco/NUTS_RG_01M_2021_4326_clean.csv` (Eurostat GISCO NUTS 2021 regional definitions). Manual name overrides applied for ~30 French NUTS 2024-revised codes (e.g. `FRK1`→`Auvergne`, `FRL0`→`Provence-Alpes-Côte d'Azur`).

**Files generated:**

| Path | Contents |
|---|---|
| `code/data/processed/heat_demand_by_region/heat_demand_NUTS1_all.csv` | All 100 NUTS1 regions across 29 countries |
| `code/data/processed/heat_demand_by_region/heat_demand_NUTS2_all.csv` | All 284 NUTS2 regions |
| `code/data/processed/heat_demand_by_region/heat_demand_NUTS3_all.csv` | All 1,369 NUTS3 regions |
| `code/data/processed/heat_demand_by_region/{ISO2}.csv` | Per-country combined file (all 3 levels), 29 files |
| `countries/{Country-Name}/data/heat_demand_regions.csv` | Same as above, mirrored next to country profile |
| `code/scripts/aggregate_heat_demand_by_region.py` | Reproducible build script |

**Schema:** `nuts_id`, `nuts_name`, `nuts_level` (1/2/3), `country` (ISO2), `dwellings`, `heat_MWh`, `heat_TWh`.

**Sanity check:** Total = 3,863 TWh/year across all 29 countries — consistent across all three aggregation levels (NUTS1 sum = NUTS2 sum = NUTS3 sum).

**Top-10 NUTS2 regions added to each country README** under `## Regional heat demand (NUTS)` section, alongside a full NUTS1 breakdown. Dwelling-count caveat appended (OTHER bucket over-counts; see EUBUCCO integration plan for fix).

**Greece encoding:** Eurostat uses `EL` for Greek NUTS codes; our model uses `GR` for the country code. Files use `EL` for NUTS prefixes but `GR` in the `country` column for model consistency.

**Status:** ✅ Internally consistent and reproducible from primary sources. Hotmaps baseline is 2015 — flag in paper as a known limitation; full refresh planned via EUBUCCO integration (Step 6).

---

## 2026-05-14 update — Luxembourg: building stock integration (EUBUCCO + GBA)

Integration of two open European building stock datasets for Luxembourg, our smallest test country (~150k buildings). Implements Step 6 of `PLAN.md` (EUBUCCO/GBA scoping) on a single-country basis. Scripts in `code/scripts/luxembourg/`.

**Datasets and licensing:**
- **EUBUCCO v0.2** (LU00 NUTS2 partition, ~10-50 MB parquet) — ODbL — used for height, type, age attributes. Coverage in v0.1: 73% have height, 46% have type, 24% have age. Source: Milojevic-Dupont et al. (2023), DOI 10.1038/s41597-023-02040-2.
- **GBA.ODbLPolygon** (tile e005_n50_e010_n45, ~200 MB GeoJSON, clipped to LU bbox in 02_classify.py) — ODbL — used as polygon-completeness check. Source: Zhu et al. (2025), DOI 10.14459/2025mp1782307.
- GBA.Polygon (with heights), GBA.LoD1, and GBA.Height deliberately excluded due to CC BY-NC license — incompatible with downstream commercial reuse.

**Classification rules** (`02_classify.py`, function `classify_row`):
Four classes: SFH, MFH_LOW (3-5 floors), MFH_HIGH (≥6 floors), NON_RESIDENTIAL. Sequential rules:
1. EUBUCCO.type starts with "non-" → NON_RESIDENTIAL
2. floors ≥ 6 AND footprint ≥ 800 m² → MFH_HIGH
3. floors ≤ 2 AND footprint < 250 m² → SFH
4. 3 ≤ floors ≤ 5 → MFH_LOW
5. default → MFH_HIGH (policy-conservative — over-counts hard-to-electrify stock)

**Derived attributes:**
- `footprint_area_m2`: polygon area in EPSG:3035 (ETRS89/LAEA equal-area)
- `floors_estimated`: round(height_m / floor_height); floor_height = 3.0 m residential, 3.5 m other; min 1
- `heated_floor_area_m2`: footprint × floors × 0.85 (useable area fraction, TABULA/ISO 52000)

**Parameter sources:**
- 3.0 m residential floor-to-floor: European typical (2.5 m clear ceiling + structure + services)
- 3.5 m non-residential floor-to-floor: commercial ceilings + raised access floor allowance
- 0.85 useable area fraction: TABULA, ISO 52000
- 250 m² SFH footprint cap: EU SFH typology midpoint (Hotmaps, TABULA)
- 800 m² high-rise floor footprint: ~10-15 apartments per floor lower bound
- 6-floor MFH_HIGH threshold: EU lift-mandate cutoff; concrete-frame construction boundary; standard TABULA / EU Building Stock Observatory / Hotmaps cut

**Heat demand intensity** (`03_heat_intensity.py`): currently STUB with placeholder kWh/m²/yr values. Real source pending Abdul decision between TABULA / EU Building Stock Observatory / Hotmaps / STATEC. See script 03 docstring for full decision list.

**Status:** Luxembourg pipeline live, scripts documented and runnable. Real intensity calibration deferred. Validation against STATEC pending. Scale-up to other countries pending Abdul approval.

**Files:**
- `code/scripts/luxembourg/01_download.py` — anonymous fetches from S3 + HuggingFace
- `code/scripts/luxembourg/02_classify.py` — classification + diagnostics
- `code/scripts/luxembourg/03_heat_intensity.py` — STUB intensity assignment
- `code/scripts/luxembourg/README.md` — pipeline doc + license notes
- Outputs to `code/data/processed/luxembourg/` (per-building) and `countries/Luxembourg/data/` (summary mirror)

---

## 2026-05-14 update — Building classification (EUBUCCO build)

**Scope:** Luxembourg for the EUBUCCO + Global Building Atlas integration. Sets the template for the 28-country rollout planned as Step 6 of the project plan.

**Implementation:**
- Code: `code/scripts/luxembourg/02_classify.py`
- Methodology doc: `literature/luxembourg/classification_methodology.md` (paper-ready)
- In-code docstring: 139-line module-level methodology block in `02_classify.py`

**Classes (4):**
- `SFH` — single-family house (detached, semi-detached, terraced)
- `MFH_LOW` — multi-family house low-rise (3-5 floors)
- `MFH_HIGH` — multi-family house mid/high-rise (≥6 floors)
- `NON_RESIDENTIAL` — commercial, industrial, office, retail, public

**Decision rules (sequential, first match):**
1. EUBUCCO `type` starts with "non-" → NON_RESIDENTIAL
2. floors ≥ 6 AND footprint ≥ 800 m² → MFH_HIGH
3. floors ≤ 2 AND footprint < 250 m² → SFH
4. 3 ≤ floors ≤ 5 → MFH_LOW
5. else → MFH_HIGH (conservative default)

**Floor estimate:** `floors = round(height_m / floor_height)`, minimum 1, NaN if height missing. Floor height = 3.0 m residential, 3.5 m non-residential.

**Heated floor area:** `footprint × floors × 0.85` (TABULA/ISO 52000 useable-area fraction).

**Sources:**
- EUBUCCO v0.2 (Milojevic-Dupont et al., 2023; DOI 10.5281/zenodo.7225259) — ODbL
- GBA ODbLPolygon (Zhu et al., 2025; DOI 10.14459/2025mp1782307) — ODbL only (CC BY-NC components deliberately excluded for commercial-compatibility)
- TABULA (IEE 2009-2012) for useable area fraction and SFH typology bounds
- ISO 52000-1, EN 17037, EN 378 for floor heights and HP retrofit constraints
- Hotmaps building stock distribution for footprint thresholds

**Status:** ✅ Implemented for Luxembourg, awaiting first run. ⏳ Pending Abdul review of:
- 250/800 m² footprint thresholds (calibration against STATEC)
- "Conservative default → MFH_HIGH" rule (has opposite sign for DH scenarios)
- Mixed-use buildings handling
- Use of EUBUCCO `building-type-harmonization.csv` for finer taxonomy

**Validation planned subsequent:** STATEC dwelling count (~241k), Eurostat ENER/NRG_BAL, Luxembourg Cadastre 2020 — all must reconcile within ±25% before scaling to 29 countries.

---

## 2026-05-14 update — Colab + EUHB_RAW_DIR override

Added support for running the Luxembourg in Google Colab with raw data stored on Google Drive, to allow execution on laptops with limited disk/RAM.

**New file:** `notebooks/luxembourg.ipynb` (Colab notebook with 8 executable cells: install, mount, clone, configure path, download, classify, heat intensity, auto-commit).

**Script changes:**
- `01_download.py` and `02_classify.py` now respect environment variable `EUHB_RAW_DIR`.
- If set, raw downloads and reads happen there instead of `code/data/raw/`.
- Default behaviour (laptop / Codespaces) unchanged: falls back to in-repo `code/data/raw/`.
- Banner comment added at the top of each affected script.

**Authentication for auto-commit from Colab:**
- Reads `GITHUB_PAT` from Colab Secret manager (fine-grained PAT scoped to this repo only, with `Contents: Read and write`).
- PAT never appears in the notebook; never committed; never sent through chat.
- Replaces the GitHub Actions workflow approach we previously planned (the workflow file was never committed because the Claude-side token lacked `workflow` scope; Colab path is simpler anyway).

**Raw data location on Drive:** `MyDrive/eu-hydrogen-raw/`. Chosen to be outside the synced repo path so Google Drive desktop doesn't try to mirror ~200 MB of raw building footprints to the user's laptop.

**Status:** ✅ Notebook + script changes committed. ⏳ Awaiting first Colab run by Ali.

---

## 2026-05-14 update — GBA tile size correction + streaming read

**Discovery:** the GBA.ODbLPolygon tile `europe/e005_n50_e010_n45.geojson` is **10.4 GB**, not the ~200 MB initially estimated. The tile covers a full 5°×5° box spanning lon 5–10°E, lat 45–50°N — most of France, parts of Germany, Switzerland, northern Italy, the Benelux. Several million buildings, of which only ~150k are in Luxembourg.

**Symptom:** loading the full GeoJSON with `geopandas.read_file(GBA_SRC)` in `02_classify.py` exhausted Colab's RAM and was killed by the runtime.

**Fix (commit pending):** `02_classify.py::load_gba()` now uses pyogrio's bbox-filtered read via GDAL, which streams the file from disk and only materialises features whose envelope intersects the Luxembourg bbox. Memory footprint stays in the 50–200 MB range instead of 30+ GB.

```python
gdf = gpd.read_file(GBA_SRC, bbox=bbox_in_file_crs, engine="pyogrio")
```

**Side-effects:**
- Adds `pyogrio` as a hard dependency (was already in requirements.txt as recommended)
- CRS detection is now done via `pyogrio.read_info(path)` (header-only read) before the data load, so we know the file's CRS before computing the bbox to project into
- The bbox is computed in the file's CRS (EPSG:3857 Web Mercator) by reprojecting LU's WGS84 bbox

**Implication for scale-out:** for the 29-country rollout, GBA tiles must be enumerated by country (lon/lat boxes), and the same bbox-filter approach used per country. Tile size estimates per country:
- Luxembourg: 10.4 GB tile, ~150k buildings after filter
- Germany: 4-6 tiles × ~5-15 GB each, ~30M buildings after filter
- Total raw GBA download for all 29 countries: likely 100–200 GB

**Recommendation for scale-out:** either (a) use GBA only for spot-check countries, not all 29; (b) skip GBA polygon-completeness check entirely and rely on EUBUCCO + national source cross-validation; or (c) move to GBA's per-country WFS endpoint which fetches only LU bbox without downloading the full tile. Decision deferred until after Luxembourg validates.

---

## 2026-05-14 update — Script 03 real implementation (heat intensity)

`code/scripts/luxembourg/03_heat_intensity.py` upgraded from placeholder stub to real bottom-up implementation. Replaces the placeholder per-class intensities (160/130/120/150 kWh/m²/yr for SFH/MFH_LOW/MFH_HIGH/non-res) that gave −22% gap vs Hotmaps with a TABULA Belgium proxy + climate-corrected + retrofit-blended approach.

**Data sources added:**
- `code/data/raw/tabula/be_intensities.csv` — 18 rows (3 classes × 6 cohorts)
- `code/data/raw/eu_bso/lu_intensity.csv` — 6 rows (one per cohort)
- `code/data/raw/lu_national/lu_climate_retrofit.csv` — 11 LU parameters

**Result:** bottom-up total of 7.84 TWh/yr (vs Hotmaps 8.27 TWh = −5.2%, within ±15% tolerance). Four sources cluster tightly: Hotmaps 8.27 / This 7.84 / Odyssee 7.20 / BSO 6.75 TWh.

**Methodology:** TABULA Belgium synthetical-average per (class × cohort) intensity × HDD-ratio LU/BE (1.112) × retrofit blend factor (0.813) + DHW component (22 kWh/m² SFH, 19 kWh/m² MFH). Unknown-cohort buildings get class-specific stock-weighted fallback (SFH 195.8, MFH_LOW 158.2, MFH_HIGH 150.4 kWh/m²/yr).

**No calibration applied** per Ali/Abdul decision: bottom-up reported as-is alongside benchmarks.

**Script 02 also updated:** `construction_year` added to the saved-column list in `02_classify.py`, so script 03 can use vintage data on re-run. Backward-compatible — script 03 detects missing column and falls back to "unknown" cohort treatment.

**Documentation:** new `literature/intensity_source_methodology.md` with full source decision matrix, methodology walk-through, results table, and 6 open questions for Abdul. Step 3 doc §5 refreshed to reflect real implementation.

**Status:** ✅ Implementation tested locally; produces sensible results. ⏳ Awaiting Ali to re-run Colab cells 3, 6, 7, 8 to refresh outputs with the new vintage data.

---

## 2026-05-15 — Repo-wide citation audit (Step 4 of methodology audit)

Comprehensive sweep of citations across `code/src/`, `paper/References_v1.bib`, and the data files used by the Luxembourg. Triggered by the discovery in the prior turn that three citations in `intensity_source_methodology.md` were stale or incorrect (VITO report number, Eurostat HDD dataset code, Odyssee-Mure trend year-range).

**Bib additions (21 new entries, all web-verified before commit):**
- `MilojevicDupont2023Eubucco` — Sci. Data 10:147, DOI 10.1038/s41597-023-02040-2
- `Zhu2025GlobalBuildingAtlas` — ESSD 17:6647-6668, DOI 10.5194/essd-17-6647-2025
- `Pezzutto2018Hotmaps` — Hotmaps D2.3 WP2 Open Data Set, H2020 GA 723677
- `Loga2016Tabula` — Energy & Buildings 132:4-12, DOI 10.1016/j.enbuild.2016.06.094
- `Cyx2011TabulaBelgium` — VITO scientific report 2011/TEM/R/091763 (NOT 2011/SET/R/0190)
- `EurostatHDD2025` — Cooling and heating degree days, `nrg_chdd_a` (NOT `tps00130`)
- `Yue2018Uncertainty` — Energy Strategy Reviews 21:204-217, DOI 10.1016/j.esr.2018.06.003
- `SueWing2008Synthesis` — Energy Economics 30(2):547-573, DOI 10.1016/j.eneco.2006.06.004
- `McFadden1974ConditionalLogit` — Frontiers in Econometrics, ed. Zarembka, Academic Press
- `Train2009DiscreteChoice` — Cambridge UP, 2nd ed., ISBN 978-0521766555
- `Yu1973GroupDecision` — Management Science 19(8):936-946, DOI 10.1287/mnsc.19.8.936
- `Zeleny1973CompromiseProgramming` — In Cochrane & Zeleny, UofSC Press, pp.262-301
- `Bistline2020ValueOfTechnology` — Energy Economics 86:104694, DOI 10.1016/j.eneco.2020.104694
- `ISO52000-1` — ISO 52000-1:2017, Geneva
- `EN16798-1` — CEN EN 16798-1:2019, Brussels
- `OdysseeMURE2024Luxembourg` — LU country profile, 2024 release
- `BSO2025` — EU Building Stock Observatory database, Dec 2025 release
- `JRC137131Luxembourg` — JRC report 137131 (LU heat pump market)
- `LuxembourgRGD1995` — RGD 27.12.1995, first LU thermal regulation
- `LuxembourgEPBD2020` — Worré, Winandy, Sijaric, EPBD Concerted Action
- `Rosenow2022PipeDream` — Joule 6(10):2225-2228, DOI 10.1016/j.joule.2022.08.015

**Pre-existing bib entries verified correct (no changes needed):**
- `Krien2020Oemofsolpha`, `Kountouris2024Unified`, `Prina2020Classification` (referenced by Optimisation.py)
- All Eurostat dataset codes referenced in Config.py docstring: `nrg_pc_202`, `nrg_pc_204`, `nrg_d_hhq` — all confirmed against Eurostat databrowser

**Src module docstrings — comprehensive source attribution added:**
- `code/src/BuildingStock.py` — Hotmaps, Eurostat census `CENS_21DWBNO_R3`, UK Census `TS044`, GISCO NUTS 2024
- `code/src/Config.py` — JRC ETRI, IEA, IRENA, Danish Energy Agency, Eurostat fuel prices, IEA WEO STEPS, OIES
- `code/src/Simulation.py` — McFadden logit, Train discrete-choice, Sue Wing CGE coupling, Yue uncertainty review, Rosenow pipe-dream
- `code/src/Optimisation.py` — Yu group-decision, Zeleny compromise programming, oemof.solph, existing model design references

**Issues found and corrected before commit:**
- Zhu2025: removed invented dataset DOI; kept mediaTUM URL only
- EN 16798-1: expanded title to full official version (was truncated)
- BuildingStock.py: removed unverified TS044 version number from URL
- Simulation.py: removed "Sens et al. 2022 Energy & Buildings" (could not verify; appears to be a hallucinated citation); replaced with verified Rosenow 2022 Joule

**What was NOT changed:**
- No model logic changes — pure documentation/attribution
- Country profile READMEs not touched (separate audit pass needed)
- `literature/` markdown files use prose citations; not converted to BibTeX keys (would require a separate consolidation pass)
- `paper/Paper_v2.tex` not modified

**Status:** complete. All 21 new bib entries web-verified against authoritative sources. Sanity-checked by reading full URLs / DOIs / publisher metadata, not just first-search-result-looks-plausible.

---

## 2026-05-15 update — GBA removed from the LU runtime pipeline

**Background.** Earlier entries (above) describe the EUBUCCO + GBA dual-source design where GBA contributed a polygon-completeness cross-check. After the LU ran successfully end-to-end, the GBA cross-check was retired from the runtime pipeline because:

1. **Cost.** The 10.4 GB GBA tile took ~22 minutes to bbox-filter through Drive FUSE in Colab, dominating total pipeline time (~25 minutes overall vs ~30 seconds for EUBUCCO alone).
2. **WFS workaround failed.** Investigated the TUM-hosted WFS endpoint `https://tubvsig-so2sat-vm1.srv.mwn.de/geoserver/ows` as a bbox-only alternative. The endpoint is live and serves valid GeoJSON, but has a hard server-side response cap: reliable up to `count≈200` per request, truncated for larger requests via "IncompleteRead" connection drops. Paged retrieval for LU's ~447k features would require ~2,235 requests at ~0.4 s each = ~15-25 minutes — no net speed gain.
3. **Information value.** The cross-check yielded a single, stable validation number: GBA's residential floor area for LU is ~1.4× EUBUCCO's, attributable to GBA's looser polygon definition (includes sheds, extensions, garages). Re-deriving this on every pipeline run is wasteful; it's now a static, published finding.

**What was removed (commit `b06998c`):**
- `01_download.py` — GBA URL constants, `GBA_DIR`, `--skip-gba` flag, GBA download block, GBA mkdir
- `02_classify.py` — entire `load_gba()` function (~80 lines), `GBA_SRC`, `LU_BBOX`, `agg_gba` parameter from `compare_to_existing_model()`, `gba` parameter from `make_diagnostics()`, `--sample` CLI flag (only applied to GBA sampling)
- Notebook cell 6 references to "clipping GBA to Luxembourg bbox"
- Notebook cell 0 reference to "EUBUCCO + GBA building stock"

**What was kept:**
- The `Zhu2025GlobalBuildingAtlas` bib entry in `paper/References_v1.bib` is preserved.
- The paper methodology section will continue to cite Zhu et al. (2025) when reporting the 1.4× GBA/EUBUCCO ratio as a one-time published finding.
- Historical notes added to `01_download.py` and `02_classify.py` top docstrings explaining the removal.
- One-time Drive cleanup cell added to the Colab notebook to delete the obsolete `MyDrive/eu-hydrogen-raw/gba/` folder (was 10.86 GB on Ali's Drive; freed by the first run after commit `ec7d8fc`).

**If a fresh cross-check is needed (e.g. new EUBUCCO version):** the `load_gba()` implementation is preserved in git history at commit `d248600`, file `code/scripts/luxembourg/02_classify.py`. Restoration is a single `git show d248600:code/scripts/luxembourg/02_classify.py` and reapply.

**Impact on the 29-country scale-out:** simpler. Removes the per-country GBA tile enumeration problem flagged in the 2026-05-14 entry above. Total raw GBA download for 29 countries (previously estimated at 100–200 GB) drops to zero.

**Status:** complete. Last verified Colab run (commit `055ec1f`) completed end-to-end in ~30 seconds with EUBUCCO-only pipeline.

---

## 2026-05-17 update — Finland (country #3): Sweden-proxy building-stock build

Finland added to the country-build pipeline as country #3, following the same generic scripts as Luxembourg and France with a new per-country config. Finland is methodologically a **TABULA proxy country**: it has no national TABULA typology, so its residential heat intensities are taken from the **Sweden** TABULA national typology brochure and climate-corrected by the FI/SE heating-degree-day ratio. This is the Luxembourg-via-Belgium pattern, not the France direct-TABULA pattern.

**Files created:**
- `code/data/country_config/fi.yaml` — Finland config (loads and validates via `CountryConfig.load_country_config('FI')`).
- `code/data/raw/tabula/se_intensities.csv` — Sweden-proxy per-class × per-cohort space-heating + DHW intensities (18 cells), extracted from the Sweden TABULA brochure.
- `code/data/raw/eu_bso/fi_intensity.csv` — Finnish stock weights by cohort + Sweden-proxy national-average intensities.
- `notebooks/finland.ipynb` — Colab build notebook (`COUNTRY = 'FI'`).
- `literature/finland/classification_methodology.md` — full Finland methodology, including the Sweden-proxy rationale and the two taxonomy mappings.

**Key parameters and status:**

| Parameter | Value | Source | Status |
|---|---|---|---|
| EUBUCCO partitions | 5 (FI19, FI1B, FI1C, FI1D, FI20) | NUTS 2016/2021 | ✅ |
| NUTS3 regions | 19 (maakunnat) | Statistics Finland / Eurostat NUTS 2021 | ✅ |
| TABULA source | Sweden (proxy) | Sweden TABULA National Typology Brochure | ✅ |
| HDD Finland | 5,321 degree-days/yr | Eurostat `nrg_chdd_a` 2018–2022 mean (DBnomics `A.NR.HDD.FI`) | ✅ |
| HDD Sweden (proxy) | 5,043 degree-days/yr | Eurostat `nrg_chdd_a` 2018–2022 mean (DBnomics `A.NR.HDD.SE`) | ✅ |
| Climate multiplier | 1.055 | HDD_FI / HDD_SE | ✅ |
| Retrofit factors (std/adv) | 0.74 / 0.49 | Sweden TABULA brochure refurbishment scenarios (mean of *Förbättrad/Lågenergi* ÷ *Nuvarande* over 15 building examples) | ✅ |
| Retrofit shares (orig/std/adv) | 0.55 / 0.35 / 0.10 | Modelling assumption consistent with the Finland LTRS ~1.8 %/yr renovation rate (Ministry of the Environment 2020, EPBD Art. 2a) | ⚠️ Original-vs-renovated share grounded; standard/advanced sub-split unverified |
| Retrofit factors (std/adv) | 0.74 / 0.49 | Sweden TABULA brochure refurbishment scenarios | ✅ |
| Cohort-extrapolation factors (2011-2020, post-2020) | 0.80 / 0.65 | Corroborated vs Swedish BBR new-build requirement history (Boverket: ~110→90→~75 kWh/m²·a, 2006→2015→2021) | ⚠️ Order-of-magnitude support |
| Retrofit blend | 0.858 | Computed | ✅ |
| DHW intensity (SFH/MFH) | 16 / 17 kWh/m²·a | Sweden TABULA brochure existing-state DHW | ✅ |
| Non-residential intensity | 130 kWh/m²·a | Estimate | 🔲 No Finnish service-sector heating intensity sourced; contributes 0 TWh (zero heated area) |
| Hotmaps benchmark | 78.14 TWh | Sum of FI rows in `building_stock_nuts3.csv` | ✅ |
| Residential heating benchmark | 42.0 TWh (2023) | Statistics Finland, *Energy consumption in households 2023* (released 5 Dec 2024) — occupies the Odyssee-Mure slot | ✅ |
| EU BSO benchmark | 42.0 TWh | Anchored to the Statistics Finland 2023 figure; EU BSO portal not retrievable | ⚠️ Not a true BSO value |

**Two taxonomy mappings (documented in the Finland methodology doc):**
- *Class:* Sweden TABULA has only SFH and MFH; our model has SFH / MFH_LOW / MFH_HIGH. MFH_LOW and MFH_HIGH both take Sweden's single MFH value, so they are necessarily identical for Finland.
- *Cohort:* Sweden's 5 construction periods (≤1960 … 1996-2005) are mapped onto our 6 cohorts. The two newest cohorts (2011-2020, post-2020) are **extrapolated** from SE 1996-2005 with new-build improvement factors (0.80, 0.65) — flagged for verification.

**`needs_verify` summary (full list in `fi.yaml._meta.needs_verify_summary`):** after the 2026-05-17 verification pass the remaining open items are the retrofit standard/advanced sub-split, the (0-TWh) non-residential intensity, the BSO-specific benchmark, and the Sweden climate-zone choice.

**Status:** ✅ Config + inputs + notebook + docs in place; `fi.yaml` validates; Colab pipeline run complete (bottom-up 68.9 TWh, −11.8 % vs Hotmaps, in the ±15 % consistent tier). ✅ Verification pass done — the residential-heating benchmark is now the Statistics Finland 2023 figure (42 TWh), and the cohort-extrapolation factors and retrofit-share grounding are sourced. The retrofit standard/advanced sub-split remains the largest open item (Finland publishes no envelope-state stock distribution).

---

## 2026-05-17 update — Finland verification pass + script-04 diagnostics in Colab

Follow-up to the Finland build. Two strands of work.

**(1) Verification of Finland placeholders.** Web research against primary sources (Statistics Finland, Finland's Long-Term Renovation Strategy, Boverket BBR):
- **Residential heating benchmark:** Statistics Finland, *Energy consumption in households 2023* (released 5 Dec 2024) reports ~42 TWh used on heating residential spaces in 2023. This replaces the earlier 40 TWh Odyssee-Mure estimate (`odyssee_mure` slot) and also anchors the `eu_bso` slot (the BSO portal could not be queried).
- **Cohort-extrapolation factors (0.80/0.65)** for the two newest cohorts: corroborated against the Swedish BBR new-build energy-requirement history (Boverket ~110 kWh/m²·a in 2006, ~90 in 2015, ~75 or lower from 2021).
- **Retrofit shares (0.55/0.35/0.10):** relabelled from placeholder to a modelling assumption grounded in the Finland LTRS ~1.8 %/yr renovation rate. The standard/advanced sub-split is still an assumption.
- **Non-residential intensity (130 kWh/m²·a):** could not be sourced (no clean Finnish service-sector heating-only kWh/m² figure); retained as an estimate. Contributes 0 TWh.
- The bottom-up result is unchanged (68.9 TWh) — only benchmark/provenance fields moved.

**(2) Script-04 diagnostics restored to the Colab notebooks.** `04_diagnostics.py` (the 8-page diagnostic PDF) was smoke-tested across all 8 panels and found sound; one stale hard-coded string in panel 6 ("23 buildings") was made dynamic, and the misleading `lu_intensity` variable name in the country-generic script was renamed. A new non-fatal "## 8b" cell was added to both `notebooks/france.ipynb` and `notebooks/finland.ipynb` so the diagnostic PDF is produced in Colab and committed alongside the CSVs; a 04 failure is logged but does not block the auto-commit of the 02/03 outputs.

**Status:** ✅ Complete. fi.yaml + the three FI input CSVs + both notebooks + the Finland docs updated. ⏳ Next Colab run regenerates the FI reconciliation CSV with the 42 TWh benchmark and produces the diagnostic PDF.

---

## 2026-05-18 update — Paper v3: model fix, methodology, bibliography, figures

A consolidated revision pass for Paper v3 (`paper/Paper_v3.tex`).

### Model fix — LCOH-responsive technology mix (Simulation.py)

`tech_shares_for_year()` blends a scenario-prescribed technology mix with an
LCOH softmax ("cheaper technologies get higher share"). The LCOH-blend code
contained a cancelling bug: the per-tech reallocation was computed as
`scenario_share * weight / SUM * SUM`, in which the `/SUM * SUM` cancels, so
the LCOH term collapsed to `scenario_share * weight` and the mix was almost
unresponsive to cost. This is why the earlier sensitivity tornado showed the
emissions pathway as insensitive to every economic axis.

**Fix:** the LCOH-weighted component now redistributes the *total* responsive
share mass across technologies in proportion to the cheapness softmax
(`lcoh_share = total_responsive * weight`), blended 50/50 with the scenario
shares. The technology mix is now genuinely cost-responsive (to carbon price,
CAPEX learning and the central fuel-price trajectories). The Monte Carlo for
all three scenarios and the sensitivity run were regenerated.

**Known limitation (still open):** `Economics.compute_lcoh()` takes only the
carbon-price scenario; the sampled hydrogen-price scenario and discount rate
are NOT threaded into it (they read module-level defaults). So the hydrogen
price and discount rate still do not propagate to the Monte Carlo LCOH or
emissions. The central hydrogen-price *trajectory* is in the model
(`FUEL_PRICES`), but the hydrogen-price and discount-rate *uncertainty* axes
are inert. Threading both through `compute_lcoh` and its callers is the next
model fix. Flagged in `paper/sections/sensitivity.tex`.

### Methodology section filled (paper/sections/methodology.tex)

Every red `[TODO]` stub was filled from sourced values in this register:
the techno-economic parameter table (CAPEX/SCOP, EUR2024, JRC / Danish
Energy Agency / IEA / IRENA), the technology-mix interpolation text with the
HP-feasibility equation, a fuel-price table (Eurostat `nrg_pc_202/204` +
2050 multipliers), and per-scenario narrative justification. Repo URL fixed.

### Bibliography (paper/References_v1.bib)

10 missing citation keys added and web-verified: `SFOE2023hydrogen`,
`REpowerEU2022`, `Fabra2009etspassthrough` (note: published as Fabra &
Reguant, AER 2014 — the key's "2009" is an author artefact),
`Competition2021`, `EMBER2024electricity`, `EEA2023fit55`, `IEA2023pumps`,
`Hotmaps2019`, `IEA2023NZE`, `EuropeanCommission2018LTS`. The paper now
compiles with 0 undefined citations and 0 undefined references; 275 bib
entries, no duplicate keys.

### Figures — full rebuild and audit (code/src/Visualise.py, fig3-21)

- fig3-14 restyled to the Wong colourblind-safe palette to match the v3
  methodology figures (fig15-21); baked-in "Figure N:" title prefixes and
  the bottom-of-figure source note removed (source attribution now lives in
  the LaTeX caption).
- Overlap fixes: fig7 (legend over bars -> single shared legend below the
  panels), fig10 (legends over the lines -> moved to a clear corner with
  headroom), fig12 (6-entry legend over the breakeven line -> moved below
  the axes), fig13 (panel titles colliding with the suptitle -> top margin
  added).
- fig6 heatmap: diverging RdYlGn colormap (wrong for sequential share data)
  replaced with the sequential YlGnBu.
- fig9: the sensitivity tornado, previously a placeholder box, is a real
  one-at-a-time tornado on 2030 emissions.
- fig11: previously a degenerate flat bar chart (every country "crosses
  over" in 2025, so all bars were identical). Replaced with a horizontal bar
  chart of the 2025 air-source-HP cost advantage over a gas boiler per
  country, sorted -- an informative quantity from the same data.
- fig11 was also missing from the `make_all_figures()` driver; added.
- `run_sensitivity()` now precomputes the LCOH table once per axis
  (~1.5-2 h -> ~15 min).

**Status:** ✅ Model fix applied and Monte Carlo regenerated; methodology and
bibliography complete; all 19 figures rebuilt and audited. Paper_v3.pdf
recompiled clean. ⏳ Open: thread hydrogen-price and discount-rate into
`compute_lcoh` so those uncertainty axes propagate.

---

## 2026-05-18 update (2) — H2/discount propagation, 2025 anchoring, results re-audit

Follow-up to the earlier 2026-05-18 entry, completing the model fixes.

### compute_lcoh now receives the hydrogen-price scenario and discount rate

Previously `Economics.compute_lcoh()` took only the carbon-price scenario;
the sampled hydrogen-price scenario and discount rate were ignored (they read
module-level defaults), so those two Monte Carlo axes were inert. Now:
- `get_fuel_price()` takes an `h2_scenario` argument and, for hydrogen, uses
  the per-scenario `H2_PRICE_TRAJECTORIES` (RAPID/CENTRAL/SLOW/STRANDED)
  interpolated by year, instead of a single fixed multiplier. This also
  removes a pre-existing inconsistency: the hydrogen price in `compute_lcoh`
  no longer disagrees with the trajectories used in figs 10/14.
- `compute_lcoh()` takes `discount_rate` and `h2_scenario` arguments;
  `get_lcoh_for_mc()` and `precompute_lcoh_table()` pass the sampled values.
- Result: the hydrogen-price and discount-rate axes now propagate. In the
  sensitivity tornado (fig9) H2 price becomes the largest single driver of
  2030 emissions (~+/-5 MtCO2); discount rate has a small effect.

### 2025 mix anchored to the observed baseline

After the LCOH-blend bug fix, the cost-responsive softmax was applied at full
weight in every year, which pulled the 2025 heat-pump share to ~37% --- well
above the observed ~18-23%. Fixed: the cost-responsive weight `w_lcoh` now
ramps linearly from 0 in 2025 to 0.5 by 2050, so 2025 stays anchored to the
observed market baseline and cost-responsiveness phases in over the
transition. 2025 HP share is now 19-21% across scenarios.

### run_sensitivity slimmed

`run_sensitivity()` now evaluates only the 8 one-at-a-time cells the
sensitivity tornado needs (base + each axis at its bounds), not the full
3x4x3 = 36-cell grid. Runtime ~36 min -> ~8 min, no figure lost.

### Results / discussion prose re-audited against the regenerated figures

The model fixes changed the outputs, so every quoted number in
`results.tex`, `discussion.tex` and Table~\ref{tab:co2} was re-checked
against the regenerated `mc_summary`/`mc_emissions` data and updated:
technology shares, H2-boiler LCOH (now 301/176/119 EUR/MWh for 2025/30/50),
the ETS2 adders (gas +11, HP +1.6 EUR/MWh), the CO2 table, the Germany
LCOH gap, and the Switzerland LCOH figures. Heat-demand numbers were
unchanged (demand is independent of the technology mix).

### Known limitation still open

The 2025 technology mix differs modestly between scenarios (the fossil vs
biomass split of the residual is derived from each scenario's 2050 targets
rather than a single observed split), so model 2025 emissions are
404/206/290 MtCO2 for REF/HIGH_HP/H2_HYBRID. Table~\ref{tab:co2} reductions
are reported against the single REF 2025 reference baseline (404 MtCO2).
Anchoring the 2025 fossil/biomass split to a common observed value is the
next refinement.

**Status:** Both flagged limitations from the previous entry are now fixed
(H2/discount propagation; 2025 anchoring). Paper_v3.pdf recompiled clean:
45 pages, 0 undefined citations/references.
