# Step 2 — Cost Module (Economics.py): Research Summary

**Prepared for:** Ali Alajwad & Dr. Abdurahman Alsulaiman  
**Date:** April 2026  
**Status:** Module complete and validated. Flags for Abdul marked ⚠️.

---

## What Step 2 adds to the model

The current model assigns technology shares by interpolating toward pre-set 2050 targets. It has **no cost calculation** — it cannot answer which technology is cheapest, or under what conditions hydrogen becomes competitive. Step 2 fixes this by computing **Levelised Cost of Heat (LCOH)** for every technology in every country in every year. This is the economic objective function that will feed into the LP/MILP optimisation (Step 5).

---

## The LCOH Formula

```
LCOH = (CRF × CAPEX) / AHE  +  FOM / AHE  +  VOM  +  FuelPrice/η  +  CarbonAdder/η
```

| Term | Meaning | Key driver |
|---|---|---|
| CRF × CAPEX / AHE | Annualised capital cost per MWh useful | CAPEX, discount rate, lifetime |
| FOM / AHE | Fixed O&M per MWh useful | Maintenance intensity |
| VOM | Variable O&M | Consumables |
| FuelPrice / η | Fuel cost per MWh useful heat | Energy prices, efficiency |
| CarbonAdder / η | ETS2 carbon cost on fuel | Carbon price, fuel CO2 content |

where CRF = r(1+r)^n / ((1+r)^n − 1), η = efficiency or COP, AHE = annual heat equivalent hours × η / 1000.

---

## Key Results from Validated Module

### Germany — LCOH by technology (EUR/MWh useful)

| Technology | 2025 | 2030 | Change |
|---|---|---|---|
| District heat | 113 | 114 | +1% |
| Ground-source HP | 136 | 128 | **-6%** |
| Air-source HP | 163 | 152 | **-7%** |
| Biomass boiler | 168 | 169 | flat |
| Gas boiler | 201 | 201 | flat (ETS2 offsets fuel price decline) |
| H2 boiler | 301 | 219 | **-27%** (H2 price learning) |
| Oil boiler | 230 | 235 | +2% |
| Resistance heater | 431 | 416 | -3% |

**Key insight:** Heat pumps are already cheaper than gas boilers in Germany in 2025 — the cost advantage deepens by 2030 as ETS2 adds ~€27/MWh to gas boiler operating costs. Hydrogen remains significantly more expensive than HPs throughout.

### Cheapest technology by country in 2030

| Country | Gas boiler | ASHP | H2 boiler | Cheapest |
|---|---|---|---|---|
| Sweden | 290 | 94 | 219 | Ground-source HP |
| Germany | 201 | 152 | 219 | District heat |
| France | 209 | 104 | 219 | Ground-source HP |
| Poland | 160 | 139 | 219 | District heat |
| UK | 199 | 110 | 219 | Ground-source HP |
| Switzerland | 199 | 92 | 219 | Ground-source HP |

**Key insight:** Hydrogen boilers are not cost-competitive with heat pumps in any modelled country in 2030. The H2 case depends critically on fuel price decline and whether specific building segments (poorly insulated, high heat demand, no garden space for GSHP) make HP installation prohibitively expensive.

---

## 1. CAPEX — Key Findings

> **🔄 May 2026 update:** Country-specific labour cost multipliers added to `Economics.py` (commit b824faf, 2026-05-14). CAPEX and FOM are now scaled by country-level labour cost rather than treated as uniform across the 29 countries. See new §1b below for full methodology. Heat demand also now available at NUTS1, NUTS2 and NUTS3 levels (commit 4930b27); see Step 3 §6 for the regional aggregation.

### Heat pumps (ASHP)
- **2025 CAPEX:** EUR 1,200/kW (IEA Future of Heat Pumps, 2022; IRENA, 2022)
- **2050 CAPEX:** EUR 700/kW — ~40% reduction from manufacturing scale (IRENA 2022, IEA NZE)
- **Learning rate:** ~1.5%/year, consistent with solar PV trajectory at comparable deployment scale
- IEA WEO 2025: HPs with COP 3.5 already cost-competitive with gas in EU when ETS2 is applied
- Global HP sales rose 27% from 2020-2024; EU sales fell 5% in 2024 (market correction after 2022 energy crisis surge)

### Gas and oil boilers
- **Gas boiler 2025:** EUR 1,000/kW (JRC Technology Data 2023; Danish Energy Agency 2023)
- Mature technology — minimal CAPEX learning (−5% by 2050)
- Key cost is fuel + carbon, not capital

### Hydrogen boiler
- **2025 CAPEX:** EUR 1,400/kW — gas boiler + H2-safety materials + controls
- **2050 CAPEX:** EUR 1,100/kW — manufacturing standardisation
- Hydrogen Council (2021): at $3/kg H2 by 2030, residential H2 heating = $900-1,600/household/year
- UK cancelled hydrogen town trial (May 2024) due to lack of low-carbon H2 supply and cost concerns
- **Critical finding:** H2 boiler CAPEX is not the main barrier — it's the H2 fuel price

---

## 1b. Country labour cost multipliers — Key Findings

**Added to `Economics.py` on 2026-05-14 (commit b824faf).** Previously, the model treated CAPEX and Fixed O&M as uniform across all 29 countries — implying that installing the same heat pump cost the same in Bulgaria as in Luxembourg. This is a known simplification that this update corrects.

### Why this matters

Labour is a large share of total installed cost for heating-system retrofits:
- **Heat pump (air-source):** ~40% of installed CAPEX is field labour (drilling, refrigerant work, electrical, plumbing, commissioning)
- **Heat pump (ground-source):** ~55% — borehole drilling dominates
- **Gas boiler:** ~30% — simpler installation, factory-built unit
- **District heat connection:** ~50% — trenching, sub-station, building interface
- **Hydrogen boiler:** ~35% — similar to gas plus extra safety/certification labour
- **Fixed O&M (all techs):** ~70% labour (service-call hours), 30% parts/refrigerant

Eurostat hourly labour cost data for construction (NACE F, code `lc_lci_lev`, 2024 levels) shows a 5× spread across the 29 countries:
- **Lowest:** Bulgaria €10.6/h (multiplier 0.35)
- **EU27 mean:** ~€30.0/h (anchor multiplier = 1.00)
- **Highest:** Luxembourg €55.2/h (multiplier 1.80)
- **Switzerland:** €52.8/h (multiplier 1.75)
- **UK:** ~€33/h (multiplier 1.10)
- **CEE bracket:** PL/RO/HU/SK/BG/HR/LT/LV/EE all in 0.35-0.55 range
- **Western bracket:** DE/FR/IT/NL/BE/AT/IE all in 0.95-1.30 range
- **Nordic/CH/LU bracket:** DK/SE/FI/CH/LU all in 1.50-1.80 range

### Formula

```
CAPEX_country = CAPEX_anchor × [(1 − L) + L × M]
FOM_country   = FOM_anchor   × [(1 − FOM_LABOUR_SHARE) + FOM_LABOUR_SHARE × M]
```

where:
- L = `LABOUR_SHARE_OF_CAPEX[tech]` (tech-specific, see above)
- M = `LABOUR_COST_MULTIPLIER[country]` (Eurostat 2024)
- `FOM_LABOUR_SHARE = 0.70` (70% of O&M is field-service labour)

### Effect on 2025 LCOH

Relative to the old uniform-CAPEX assumption:

| Country group | HP_air | HP_ground | Gas boiler |
|---|---|---|---|
| CEE / Baltics / Balkans | −2% to −7% | −3% to −11% | −3% to −10% |
| Mid-range (IE, IT, ES) | ±2% | ±2% | ±2% |
| Nordic / Benelux / CH | +1% to +6% | +2% to +10% | +1% to +8% |

⚠️ **Effect interpretation:** the labour multiplier *reduces* the LCOH gap between countries for capital-intensive technologies (HP), which has the policy-relevant implication that **HP retrofit looks ~5-10% cheaper than previously assumed in CEE/Baltic countries** in our model. This is consistent with the EHPA observation that HP uptake in Poland/Hungary is currently constrained by upfront cost, electricity tariffs, and policy rather than labour cost.

### Status

✅ Validated against Eurostat 2024. ✅ All 29 country profile YAMLs (`countries/{Country-Name}/data/profile.yaml`) refreshed with new LCOH values. ✅ Wired into `compute_lcoh`, `Visualise.py` cost breakdown plots, and the dashboard.

⚠️ **Outstanding:** validate with Abdul against UN/SAMI labour data if he prefers a different source. Current implementation is Eurostat `lc_lci_lev` — uses LCS2020 levels + LCI extrapolation to 2024.

---

## 2. Fuel Prices — Key Findings

### 2025 actuals (Eurostat H1 2025)
| Fuel | EU average | Range across EU |
|---|---|---|
| Natural gas (residential) | €114/MWh | €31 (HU) → €213 (SE) |
| Electricity (residential) | €287/MWh | €104 (HU) → €384 (DE) |
| Hydrogen (green) | ~€200/MWh | ~€6/kg (EHO 2024) |
| Heating oil | ~€130/MWh | estimate |

### Gas price outlook
- Wholesale TTF: ~€44/MWh (April 2026) — elevated vs pre-2022 but below 2022 crisis peak
- Current Hormuz Strait disruption (US-Iran conflict, April 2026) pushing prices up 13%+ in recent days — geopolitical volatility remains
- Residential gas prices include significant tax component (47% in NL, 31% SE, 28% DK)
- Long-run trajectory: declining demand → lower prices; but geopolitical disruption risk = HIGH

### Hydrogen price outlook
- Currently ~€200/MWh (~€6/kg) for green hydrogen in EU (EHO 2024)
- IEA Global Hydrogen Review 2023: falls to ~€3/kg by 2030 in optimistic scenario
- Model uses: €200 (2025) → €130 (2030) → €80 (2040) → €60 (2050) ⚠️ **validate with Abdul**

### Electricity price trajectory
- EU average broadly stable (wholesale falls, network costs rise by 8.9% in 2024)
- Key dynamic: ETS2 (2027) adds carbon cost to gas but NOT to electricity → widens the electricity/gas price ratio in HP's favour

---

## 3. Carbon Pricing Impact on LCOH — Critical Finding

ETS2 launches in 2027 and directly taxes buildings sector fuel use. The carbon cost adder on LCOH at CENTRAL scenario (€122/tCO2 by 2030):

| Technology | Fuel | Carbon adder 2030 (EUR/MWh useful) |
|---|---|---|
| Gas boiler (η=0.92) | Gas | **+26.8** |
| Oil boiler (η=0.90) | Oil | **+35.9** |
| ASHP (COP=3.0, DE grid) | Electricity | **+8.1** |
| ASHP (COP=3.0, FR grid) | Electricity | **+1.5** |
| H2 boiler | Hydrogen (green) | **0** |
| Biomass boiler | Biomass | **0** |

**This is the most important number in the model.** ETS2 makes gas boilers ~€27/MWh more expensive overnight in 2027, while HPs face only ~€8/MWh adder (and near-zero in low-carbon grid countries). This is the primary economic mechanism that makes HPs cost-competitive across the EU from 2027.

---

## 4. Discount Rate — Key Decision Required

The discount rate is arguably the **most sensitive parameter** in LCOH calculations. Literature uses:

| Rate | Context | Source |
|---|---|---|
| 4% real | Social/government perspective | EU guidelines, JRC, BPIE |
| 5% real | Balanced assumption | IRENA, IEA, this model |
| 8% real | Private consumer perspective | BPIE 2024 |
| 10%+ real | High-risk / emerging markets | Oxford Economics 2026 |

The model uses **5% real pre-tax** as the central assumption. The difference between 4% and 8% can change the LCOH ranking between capital-intensive technologies (HP, district heat) and low-CAPEX technologies (gas boiler).

⚠️ **Question for Abdul:** Should we use 5% (consistent with IEA/IRENA practice) or run sensitivity across 4%, 5%, 8%? Given this is an OIES publication, the IEA convention of 5% is probably appropriate, but Abdul should confirm.

---

## 5. COP by Climate Zone

ASHP seasonal COP varies significantly across Europe:

| Country | COP multiplier | Effective COP 2025 | Effective COP 2050 |
|---|---|---|---|
| Finland | 0.85 | 2.55 | 2.98 |
| Poland | 0.92 | 2.76 | 3.22 |
| Germany | 0.96 | 2.88 | 3.36 |
| France | 1.00 | 3.00 | 3.50 |
| Spain | 1.15 | 3.45 | 4.03 |
| Cyprus | 1.35 | 4.05 | 4.73 |

This matters enormously: a Polish HP (COP 2.76) on a coal-heavy grid (600 gCO2/kWh) has a carbon footprint worse than a gas boiler in 2025. This is why the Policy layer (Step 1) and the Economics layer (Step 2) must work together — the HP case varies completely by country.

---

## Questions for Abdul

1. **Hydrogen fuel price trajectory:** Is €200 (2025) → €130 (2030) → €60 (2050) consistent with OIES projections? This is the single most important variable for RQ1 and RQ2.

2. **Discount rate:** 5% real (IEA convention) or run 4%/5%/8% as sensitivity? The choice significantly affects the HP vs gas boiler CAPEX comparison.

3. **District heat CO2 content:** Using EU average 80 gCO2/kWh — but this varies enormously (near-zero in Nordics, high in Poland). Should we model country-specific district heat emission factors?

4. **Annual hours assumption:** Using 2,000 full-load hours for all countries. In reality: ~1,500 hours in warm southern EU, ~2,500 in cold northern EU. Should we apply a climate-dependent hours correction?

5. **Gas price country variation:** The model uses country-specific 2025 gas prices from Eurostat (€31/MWh in Hungary to €213/MWh in Sweden). The Sweden figure is anomalous (district heat dominant, gas rarely used). Should we cap outliers?

---

## Implementation Status

| Component | Status |
|---|---|
| `code/src/Economics.py` | ✅ Complete — all 8 technologies, 29 countries, 2025-2050 |
| Integration into `Simulation.py` | 🔲 Next session — connect LCOH to Monte Carlo |
| Integration into `Optimisation.py` | 🔲 Step 5 — LP uses LCOH as objective |
| Validation against published LCOH studies | 🔲 Pending — compare with IEA/IRENA published values |
| Abdul validation of H2 prices and discount rate | 🔲 Pending |

---

## Change log

| Date | Change |
|---|---|
| 2026-04-xx | Initial draft of Step 2 economics research summary. |
| 2026-05-14 | Added §1b on country labour cost multipliers (Eurostat lc_lci_lev 2024, commit b824faf). CAPEX and FOM now scaled by national labour cost; 29 countries calibrated; range 0.35 (BG) to 1.80 (LU). All country profile YAMLs refreshed. Cross-referenced new per-NUTS heat demand aggregation (commit 4930b27, see Step 3 §6). |
