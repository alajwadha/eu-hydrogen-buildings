# Step 1 — Country Policy Layer: Research Summary

**Prepared for:** Ali Alajwad & Dr. Abdurahman Alsulaiman  
**Date:** April 2026  
**Status:** Research complete. Implementation in `code/src/Policy.py`. Flags for Abdul marked ⚠️.

---

## What this layer adds to the model

The current model interpolates pre-set technology shares toward 2050 targets, treating all countries identically. The policy layer adds **country-specific constraints and cost signals** that make the model reflect reality:

| Parameter | What it changes in the model |
|---|---|
| Boiler bans | Caps fossil technology shares post-ban year per country |
| Carbon pricing | Adds a carbon cost adder to fossil fuel operating costs |
| Grid carbon intensity | Makes HP emissions country-specific (Polish HP ≠ French HP) |
| Gas grid coverage | Scales hydrogen infrastructure readiness per country |
| Switzerland parameters | Enables separate RQ2 analysis with H2 import pricing |

---

## 1. Boiler Bans — Key Findings

> **🔄 May 2026 update:** Three significant policy reversals since the initial Step 1 draft (April 2026):
> - **Netherlands** cancelled most of the 2026 hybrid HP mandate (May 2024 coalition agreement). Applies only where return on investment is within 7 years after 30% grant; apartments and listed buildings already exempt.
> - **UK** scrapped the 2035 gas boiler sale ban entirely (Labour, Jan 2025). De facto ban remains only for new builds via the Future Homes Standard.
> - **EHPA Nov 2025 boiler-ban map update:** Austria's ban extended from gas-only to all fossil; Ireland broadened ban to residential homes and gas in new builds; UK 2026 ban confirmed in new buildings only. Spain still has no commitment to any phase-out. 10 EU countries have formally committed to phase-out dates; the remaining 17 have not.
> - **From January 2025** no EU member state may subsidise standalone fossil fuel boilers (already-implemented EPBD provision).
> - **Hungary anomaly:** subsidised gas price ~€31/MWh vs ~€114/MWh market (HUF 1000bn / €2.63bn allocated to fossil fuel price compensation in 2024 budget) — distorts LCOH calculations.
>
> Country-by-country updates flow into `BOILER_BANS` and `GAS_GRID_COVERAGE` constants in `code/src/Policy.py`. See change log at bottom of this file.

### EU-wide baseline (EPBD 2024)
- **January 2025:** All member states must end subsidies for standalone fossil fuel boilers
- **2030:** Zero-emission standard for all new residential buildings
- **2040:** Complete phase-out of fossil fuel boiler installations (national roadmaps required)

### Country groupings by speed

**Fast movers (bans already in effect):**
| Country | Key action | Year |
|---|---|---|
| Denmark | Gas network banned in new buildings | 2013 |
| Netherlands | Gas network banned in new buildings | 2018 |
| France | Gas/oil banned in new SFH | 2022 |
| Germany | 65% renewable rule for all new heating | 2024 |
| Austria | All fossil heating banned (repair + new, **extended to all fossil 2025**) | 2025 |
| Netherlands | Hybrid HP mandate **partially cancelled** by new coalition May 2024 — applies only where ROI ≤ 7 years (with 30% grant); apartments and listed buildings already exempt | 2026 |
| Ireland | Ban broadened to **residential homes + gas in new builds** (EHPA Nov 2025) | 2025 |
| UK | **De facto** gas boiler ban in new homes only (Future Homes Standard 2025/26); 2035 total ban **scrapped by Labour government Jan 2025** | 2026 |

**Medium pace (bans 2028-2035):**
Germany, Ireland, Belgium, Sweden, Finland, Switzerland, UK

**Laggards (2035-2040):**
Poland, Czech Republic, Hungary, Romania, Bulgaria, Slovakia

### Critical political economy point
Germany reversed its 2024 boiler ban plan to 2028 after "strong public opposition which the far right leveraged." Poland, Czech Republic, and Slovakia formally protested EU ETS2 prices. Romania cited unaffordability. **This political heterogeneity matters for the model** — it creates genuine uncertainty in the pace of fossil phase-out that the Monte Carlo should capture.

### UK note (updated Jan 2025)
**Original Conservative plan:** ban sale of new gas boilers by 2035 (would have forced HP/biomass replacement at any post-2035 boiler swap).
**Sunak weakening (Sep 2023):** softened to 80% phase-out.
**Labour government (Jan 2025):** **scrapped the 2035 sale ban entirely**. No requirement to replace existing boilers with low-carbon alternatives at any date.
**What remains:** Future Homes Standard (2025/26) imposes minimum energy efficiency on new builds that effectively excludes gas boilers in new homes; £7,500 Boiler Upgrade Scheme grant extended; Labour signals heat pump push remains a priority but without the regulatory teeth.

**Model implication:** UK's pre-2025 trajectory had a 2035 cliff edge that drove rapid HP rollout in the model. The post-Jan-2025 reality is much softer — replacement of existing boilers becomes optional/grant-driven rather than mandatory. ⚠️ Verify with Abdul that the model's UK boiler-ban parameter reflects the post-Jan-2025 reality (`replacement_fossil_ban` should be 2050 or later, not 2035).

---

## 2. Carbon Pricing — Key Findings

### Two systems now apply to buildings

**EU ETS1** (existing, covers electricity production — affects HP operating cost indirectly):
- Current price: ~€65-70/tCO2 (2025)

**EU ETS2** (NEW — directly covers buildings sector fuel costs):
- Launch: **2027**
- Initial price cap: €45/tCO2 (price stability mechanism)
- **BNEF forecast: €122/tCO2 by 2030** — highest carbon price of any market globally
- Academic range (PRIMES model): **€71-261/tCO2 by 2030** depending on complementary policies
- ETS2 futures (ICE, May 2025) already trading at ~€75/tCO2

### What this means for the model
ETS2 makes gas and oil heating significantly more expensive from 2027. At €122/tCO2 and gas's CO2 content of 0.202 tCO2/MWh:
- Gas boiler operating cost adder in 2030: ~**€25/MWh_useful**
- HP (French grid, COP=3.0) operating cost adder in 2030: ~**€0.6/MWh_useful**

This tilts the economics heavily toward HPs from 2027 onwards — **ETS2 is potentially the single most important policy variable in the model.**

### Switzerland
Switzerland has its own carbon levy: **CHF 120/tCO2 on thermal fossil fuels** (since 2022). This is ~€125/tCO2 — already above the BNEF 2030 forecast for EU ETS2. Switzerland is already at the "high policy stringency" end.

---

## 3. Electricity Grid Carbon Intensity — Key Findings

### Why this matters
The environmental benefit of heat pumps depends entirely on the electricity grid. A Polish HP running on 600 gCO2/kWh grid is worse than a gas boiler in 2025. A French HP on 80 gCO2/kWh grid is dramatically better.

### 2023 actuals (EMBER)
| Country | gCO2/kWh | Primary source |
|---|---|---|
| Poland | 662 | Coal (61%) |
| Czech Republic | 450 | Coal (40%) |
| Germany | 371 | Coal (26%) |
| EU average | 242 | Mixed |
| Belgium | ~170 | Nuclear + wind |
| France | ~85 | Nuclear |
| Sweden | ~45 | Hydro + nuclear |
| Switzerland | ~50 | Hydro + nuclear |

**EU grid fell 9% in 2024 alone** (EEA) — 40% less carbon than a decade ago. The trend is strong and accelerating.

### Model implication
HP emissions must be calculated country-by-country, not at EU average. A "hydrogen vs HP" comparison is completely different in Poland (2025) vs France (2025). The model currently ignores this — the Policy layer fixes it.

---

## 4. Gas Grid Coverage — Key Findings

### EU average
~40% of EU households connected to gas network (ACER). But conceals massive variation:
- Netherlands: ~90% (near-universal; highest EU gas dependency)
- UK: ~85%
- Italy: ~80%
- Germany: ~75%
- Sweden: ~5% (district heat + HP dominant)
- Malta, Cyprus: ~2-5% (essentially no gas grid)

### Why this matters for hydrogen
Countries with extensive gas infrastructure (NL, DE, IT, UK) have an existing pipeline network that could be partially repurposed for hydrogen. Countries with low coverage (Nordics, some Baltics) have no gas grid to repurpose — hydrogen would require entirely new infrastructure, making it even less competitive vs HP.

This creates a natural split: **high gas coverage countries = better hydrogen case; low gas coverage countries = HP clearly wins.**

---

## 5. Switzerland — RQ2 Key Findings

### Buildings sector profile
- Buildings account for ~1/3 of Swiss CO2 emissions
- Energy Strategy 2050 target: reduce buildings energy to 65 TWh (from ~100 TWh)
- Net-zero buildings by 2050 (Federal Council)
- Heat pumps: target 1.5M units by 2050 (from 0.3M today)
- CO2 levy: CHF 120/tCO2 on thermal fossil fuels (since 2022)

### Hydrogen role in Swiss buildings: **Limited**
The Swiss Energy Perspectives 2050+ (the authoritative national scenario study) is clear:
- **Heat pumps are the primary decarbonisation technology for Swiss buildings**
- **District heating expansion in urban areas** is the second pathway
- Hydrogen's role in Swiss buildings is **minimal** in the ZERO scenario
- H2 is primarily for heavy transport, industrial process heat, and seasonal energy storage
- Gas grids in Swiss cities to be "dismantled or transitioned to green hydrogen" per Cantonal Energy Directors — but this primarily affects remaining commercial users, not residential heating

### Hydrogen import prices (RQ2 sensitivity)
This is the key uncertainty for RQ2. Switzerland imports all fossil fuels — green H2 would come from:
- Domestic production: hydro-electrolysis (7 PJ potential identified in EP2050+)
- Imports from EU neighbours: Germany (ambitious H2 strategy), France, Italy, Austria

The model uses three import price scenarios (EUR/MWh):

| Year | LOW (domestic) | CENTRAL (EU import) | HIGH (scarce) |
|---|---|---|---|
| 2030 | €120 | €180 | €250 |
| 2040 | €70 | €110 | €160 |
| 2050 | €50 | €80 | €120 |

⚠️ **These need Abdul's validation against OIES hydrogen price projections.**

---

## Questions for Abdul before implementation

1. **Carbon price scenario choice:** Should we run the model with CENTRAL (€122/t by 2030) as the base case, with LOW and HIGH as sensitivity bounds? Or should we treat carbon pricing as a separate sensitivity axis?

2. **Switzerland H2 import prices:** Are the CENTRAL values (€180/MWh in 2030, €80/MWh in 2050) consistent with OIES internal projections? This is the pivotal number for RQ2.

3. **ETS2 pass-through:** ETS2 is levied on fuel suppliers, not consumers directly. The pass-through rate to end consumers is uncertain (possibly 60-80%, not 100%). Should we model full pass-through or a discounted rate? This significantly affects the economics.

4. **German political economy:** Germany's reversal on the 2024 boiler ban is important. Should we model a scenario where political backlash slows the boiler ban timeline across Eastern Europe? This is essentially a fourth scenario.

5. **Grid decarbonisation assumption:** The 2030 and beyond grid carbon intensity values are scenario-consistent estimates based on EEA Fit-for-55 trajectories. Should we source country-level NECP projections for more precision? This would require downloading national energy plans for all 29 countries.

---

## What the Policy layer enables

Once integrated into the Simulation, the model will be able to:

- **Compare identical technologies across countries** accounting for different carbon costs, grid intensities, and regulatory timelines
- **Show when HP becomes economically optimal in each country** (incorporating ETS2 from 2027)
- **Identify which countries are most suitable for H2 deployment** based on gas infrastructure readiness and policy trajectory
- **Model Switzerland's RQ2** with the specific Swiss policy framework and H2 import price sensitivity
- **Run policy sensitivity analyses** (e.g. "what if Germany's boiler ban stays at 2028 vs reverts to 2040?")

---

## Implementation status

| Component | Status |
|---|---|
| `code/src/Policy.py` | ✅ Complete — all 29 countries, all 4 policy dimensions |
| Integration into `Simulation.py` | 🔲 Next session — connect Policy module to Monte Carlo |
| Integration into `Economics.py` | 🔲 Step 2 — cost module needed first |
| Abdul validation of key parameters | 🔲 Pending — see questions above |
| Switzerland RQ2 analytical layer | 🔲 Step 6 — after LP/MILP |

---

## Change log

| Date | Change |
|---|---|
| 2026-04-xx | Initial draft of Step 1 policy research summary. |
| 2026-05-14 | Updates from EHPA Nov 2025 boiler-ban map: Austria extended to all fossil, Ireland broadened to residential + gas in new builds, UK 2026 confirmed for new buildings only. NL hybrid HP mandate partially cancelled (May 2024 coalition). UK 2035 ban scrapped by Labour government (Jan 2025). Hungary subsidised gas anomaly noted (€31/MWh vs €114/MWh market). EU-wide subsidy ban for standalone fossil boilers in force from January 2025. |
