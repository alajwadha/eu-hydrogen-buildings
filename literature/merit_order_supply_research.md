# Merit-order reframe + supply: research foundation (June 2026, for Abdul direction)

Inputs for the new framing — hydrogen as a MARGINAL/peaking heat producer in a merit-order
dispatch, the 5 multi-lever scenarios, the DH source-switching workstream, and the supply
question. Four parallel research streams; key usable numbers + sources below.

---

## 1. 2050 technology capacities (merit-order stack)

**Data-availability caveat (state in methodology):** NO single source gives 2050 installed
capacity by technology for all 29 countries under a clean BAU/STEPS scenario.
- TYNDP 2024 "National Trends+" = NECP-based (~BAU), country-resolved, but STOPS AT 2040.
- TYNDP 2024 2050 has only two scenarios (Distributed Energy, Global Ambition) — both NET-ZERO.
- EU Reference Scenario 2020 (PRIMES) = per-country, current-policy, to 2050 → best BAU spine.
- IEA WEO STEPS = EU regional, not per-country, for 2050.

**Construction recommendation:** EU-Ref-2020 (PRIMES, per-country, to 2050) as the BAU spine +
TYNDP NT 2040 country files for the tech split (escalate to 2050 on each NECP trend) + national
endpoints (RTE FR, FES UK, PNIEC ES/IT, PEP2040 PL, EnergyVille BE) as the policy-target upper bound.
Downloadable per-country file (CC-BY-4.0): TYNDP 2024 NT2040 PLEXOS output
(2024-data.entsos-tyndp-scenarios.eu/files/scenarios-outputs/MMStandardOutputFile_NT2040_Plexos_CY2009_2.5_v40.xlsx.zip).

**EU27 2050 power capacity (GW, TYNDP DE / GA net-zero brackets):** wind onshore 808/804,
offshore 391/407, solar 2008/1670, hydro 180, nuclear 47/105, gas (CCGT+OCGT combined) 106,
H2 turbines 67, battery 956, coal ~4, biomass 3. (NT+ 2040: wind 533+269, solar 1134, nuclear 98,
gas 138.) Note: TYNDP lumps CCGT+OCGT into one "Methane" line; no published 2050 peaker split.

**Merit order (firing order, low→high SRMC, 2050):**
1. Zero-SRMC VRE (solar, wind, run-of-river) → set price ~EUR 0 in surplus hours.
2. Must-run/low-SRMC: nuclear (~EUR 10-15/MWh SRMC, VO&M 3.5), reservoir hydro (water value), biomass.
3. Mid-merit: gas CCGT (VO&M 4.2 + fuel/eff + CO2; ~EUR 44/MWh of carbon alone at EUR 123/tCO2).
4. Peaking / price-setting: gas OCGT (VO&M 4.5), H2 turbines, battery, DSR → EUR 80-245/MWh in tight hrs.
- By 2050 gas+H2 fleet runs ~160 full-load hours = PURE PEAKING. CO2 ~EUR 123/t dominates gas SRMC.
- HP electricity cost is BIMODAL: ~EUR 0 in RES-surplus hours, EUR 80-245 in peaker-set hours.

**DH could supply ~50% of EU heat by 2050** (Euroheat). 2050 DH fuel (TYNDP DE, EU27 TWh): methane 102,
biofuels 103, solids 72, hydrogen 76, electricity/large-HP 83, others (geothermal/excess/solar) 107.
H2-for-buildings stays niche (UK Whitby/Redcar trials cancelled 2023; H2 turbines are POWER-sector, not home boilers).

Sources: ENTSO-E TYNDP 2024 (2024.entsos-tyndp-scenarios.eu); EU Ref Scenario 2020 (PRIMES); IEA WEO 2024;
RTE Futurs 2050; NESO FES 2024; Euroheat DHC Outlook 2024; TYNDP 2022 cost-of-electricity (CO2 ~123/t).

---

## 2. Heat load-duration / seasonal profile (turn annual demand + HDD → load curve)

**Method (when2heat / Hotmaps / PyPSA-Eur-Sec standard):**
- Split annual useful heat: SH = (1 - f_DHW) x total, DHW = f_DHW x total, f_DHW ~ 0.18 (0.15 cold, 0.20 mild).
- DHW = FLAT across the year (= DHW_annual / 8760); sits as base load under the SH peak.
- SH shaped by HDD: SH_h = SH_annual x HDD_h / sum(HDD). Threshold 15 C. Inertia-weighted T_ref
  = (T_d + 0.5 T_{d-1} + 0.25 T_{d-2} + 0.125 T_{d-3})/1.875. Smoother: BDEW sigmoid h(T)=A/(1+(B/(T-40))^C)+D.
- Without hourly T: distribute SH by MONTHLY HDD shares (table below) + set peak via FLH: SH_peak = SH_annual/FLH.

**Monthly HDD shares (% of annual, Eurostat nrg_chdd_m 2018-22), space-heating:**
| | Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec | DJF | Oct-Mar | peak mo |
| EU27 | 17 15 14 9 5 1 1 1 3 7 12 16 | ~48% | ~80% | 17% |
| Cold (FI/SE) | 15 13 12 9 6 2 1 2 5 8 11 14 | 42-43% | 73-75% | 15% |
| Mild (ES/IT/PT) | 20-23 15-16 14-15 9-10 2-4 1 0 0 0-1 3-5 13 17-18 | 53-57% | 85-87% | 20-23% |
- Counter-intuitive: MILD Med countries are PEAKIER (shorter sharper season) than cold Nordics (long full season).

**Peak ratios / load-duration shape (space heating):**
- peak-hour/avg ~5-7 (SH only), ~3-4.5 (total incl DHW). peak-day/avg ~2.5-3.5.
- FLH ~1000-1800 h (old stock 1800, passive 1000); default current EU avg ~2000-2200 h.
- Hours above threshold (SH): >80% peak ~50-150 h/yr; >50% ~700-1200 h; >20% ~3500-4500 h.
- Cold = flatter/longer; mild = steeper/shorter. DHW raises the floor (curve never hits 0 in summer).

**Per-country anchors (Eurostat annual HDD):** FI 5656, SE 5316, EE 4338 (cold); EU ~3000;
ES ~1700, PT 1233, CY 778, MT 534 (mild).

Sources: Ruhnau/Hirth/Praktiknjo 2019 (when2heat, Sci Data 6:189); Zeyen/Brown 2021 (PyPSA-Eur-Sec, Energy);
Hotmaps heat-load-profiles wiki; Heat Roadmap Europe STRATEGO WP2; Watson/Lomas/Buswell 2019 (Energy Policy 126:533);
Eurostat nrg_chdd_m + energy-consumption-in-households; BDEW SLP / demandlib.

---

## 3. District-heating / CHP fuel (workstream C — source switching)

**Today (EU-27):** renewables+waste-heat 44% (Euroheat 2023): biomass ~35%, waste-heat ~4%; by raw fuel input
~gas 40 / coal 29 / biomass 16 / renewable-waste 5 / non-ren-waste 4 / oil 3 / elec 1 (EC). Country highlights:
SE biomass 46 + waste 22 + waste-heat 8 + HP 7 (fossil-free); DK biomass 49 + waste 23 + gas 10;
PL coal 61-75; HU/SK/RO gas-heavy; LT renewables ~81; Vienna gas-CHP 52 + waste 21 + waste-heat 18.

**2050 outlook:** combustion (coal/gas, partly biomass) → large electric HEAT PUMPS + RECOVERED/EXCESS HEAT
(industrial waste heat, MSW incineration, sewage/wastewater, data centres) + geothermal + solar thermal.
DK/SE/FI/AT target fully decarbonised DH by 2030-2040. **"Largely waste/recovered heat by 2050" reference =
HEAT ROADMAP EUROPE (Connolly/Lund/Mathiesen, Aalborg)**: DH share 13% → ~50-55%; waste incineration 105 → 1198 TWh/yr;
excess heat 53 → 219 TWh/yr. Caveat: frame as "recovered/excess heat broadly" — EU circular-economy + ETS-on-incinerators
(~2028) CAP MSW volume and raise its carbon cost. Schmidt et al. Energy 2025: HP + recovered heat + geothermal dominant, H2 marginal.

**Marginal cost of DH heat by source (EUR/MWh-heat):**
| waste incineration ~0 to NEGATIVE (-20..+10) | biomass 25-35 | industrial waste heat 10-30 |
| large heat pump ~35-40 | geothermal 55-65 | H2 boiler/CHP 80-150+ |
Plus DH distribution ~28-35 EUR/MWh (source-independent).

**Waste economics = REVENUE not fuel cost:** WtE charges a GATE FEE (~EUR 80-150/t today, +75-225/t with ETS) to
accept waste → SRMC near zero/negative → must-run BASELOAD at bottom of merit order. Model with negative/near-zero
variable cost + availability cap (declining with circular economy) + rising CO2 on the fossil ~50% of MSW carbon.
If waste capped, next-cheapest baseload = recovered industrial heat → large HP (cheap power) → biomass → H2 at margin.

Sources: Euroheat DHC 2023; Heat Roadmap Europe (heatroadmap.eu, HRE4/5); Schmidt et al. Energy 2025;
REKK V4 2023; PGE 2023; DBDH Austria; AGFW DE; Nordic Energy Baltic HP 2021; Carbon Brief / ETH 2022 (HP 3x cheaper than H2);
gate-fee: Wikipedia/IEA; CE Delft "Waste Incineration under EU ETS" 2025.

---

## 4. Supply chain — delivered H2 + the seasonal-storage carve-out (workstream D)

**Production 2050 (EUR/kg; 1 EUR/kg ~ 30 EUR/MWh):** green best sunbelt/wind 0.7-1.4; green Europe ~1.3-2.2;
blue (gas+CCS) 1.15-2.0 (gas-price-sensitive); pink (nuclear) 4.7-6.6 (uncompetitive).
**Conversion+ship+crack (imports):** ammonia chain ~1.5/kg (shipping only ~0.1); LH2 liquefaction +0.8/kg (loses 30-36% energy) → LH2 uncompetitive vs pipeline.
**Pipeline (EHB):** EUR 0.08/kg/1000km repurposed, 0.16 new (~3-6 EUR/MWh/1000km) — beats shipping for all EU distances.
**Delivered 2050:** domestic EU green ~EUR 65/MWh (~2.2/kg); N-Africa pipeline import ~36-60/MWh; LH2 ship ~86 (uncompetitive).
EC + EWI + autarky study (arXiv 2510.04669, 2025): domestic EU ~10% cheaper than cheapest import; pipeline-from-N-Africa,
NOT ships, is the competing import. The model's ~EUR 50/MWh 2050 hub sits mid-band → defensible.

**THE CARVE-OUT (critical for the peaking framing): SEASONAL STORAGE.** If H2 is a winter-peaking heat producer it must be
stored seasonally (fill summer, draw winter = ~1 cycle/yr = the EXPENSIVE end of the cavern cost curve):
- Salt cavern: EUR 0.66-1.75/kg normal; ~0.45/kg large @3 cycles/yr; up to ~3.50/kg small @1 cycle/yr (EWI 2023).
- Porous (depleted field) ~USD 1.5/kg vs salt ~0.8/kg.
- Salt-cavern capacity (Caglayan et al. 2020, IJHE): ~84.8 PWh EU; concentrated GERMANY (highest ~9.4 PWh), NL, PL, DK, UK,
  N-France, RO; MUCH of Southern/Central-Eastern/Alpine Europe LACKS it → costlier depleted-field or pipeline dependence.

**Recommendation:** keep delivered H2 as a per-country INPUT (hub EUR 50/MWh x pipeline-distance multiplier, anchored on
Alsulaiman ET24 / Rikabi ET32 + EHB) -- do NOT re-model production/conversion/shipping. BUT for the peaking framing, ADD ONE
explicit term: a SEASONAL-STORAGE ADDER (~EUR 1-2/kg central @1 cycle/yr salt cavern; EUR 3+/kg for countries WITHOUT
caverns), differentiated by domestic salt-cavern access (Caglayan 2020). That single term makes the peaking framing internally
consistent and spatially honest, without dragging the upstream supply chain into a buildings paper.

Sources: Alsulaiman OIES ET24 2023; Rikabi OIES ET32 2024; IRENA Global H2 Trade Part III 2022; EHB roadmap 2022-23;
EWI underground-storage 2023; Caglayan et al. IJHE 2020; arXiv 2510.04669 (2025); EC via Hydrogen Insight 2024.

---

## 5. Implemented merit-order model (what the scripts actually compute)

The four research streams above are operationalised in three deterministic scripts (2050,
per country x scenario; same fuel-price / ETS-carbon / seasonal-storage basis throughout).
These outputs are independent of the Monte Carlo technology-mix rebuild.

### 5a. Building-level peak dispatch — `scripts/merit_order_heat.py` (-> F11)
For the cold-snap peak slice (energy above the 2000-h demand level, trapezoidal from the load-
duration curve), three quick-start sources compete on MARGINAL operating cost (EUR/MWh-heat):
- gas peaker   = gas_price/0.92 + carbon_price x 0.202/0.92
- H2 peaker    = H2_price/0.90 + seasonal_storage_adder  (EUR 50/MWh cavern, EUR 100 non-cavern)
- cold-snap HP = peak_scarcity_elec / max(0.60 x seasonal_COP, 1.8)   (air-source COP collapses at -7 C)
H2's heating share is DERIVED, not imposed: it equals the peak slice only where the H2 peaker
undercuts BOTH the gas peaker and the cold-snap HP. Result (countries where H2 wins the peak):
CURRENT 0/29, STATED 4/29, NET_ZERO 9/29, H2_PUSH 8/29 (ENDOGENOUS peak power price,
scripts/power_peak_price.py -- supersedes the constant-price 4/29 and 9/29 figures);
EU-weighted derived H2 share <=8%.

### 5b. Peaking-producer PROFIT / "missing money" — `scripts/merit_order_profit.py` (-> F12)
The dispatch question (can H2 win the peak?) is separate from the INVESTMENT question (would a
producer build the H2 peaker?). For each H2-winning country x scenario, per kW of H2-ready boiler:
- clearing price at the peak = cost of the cheapest ALTERNATIVE the system would otherwise pay
  = min(gas peaker, cold-snap HP). The price-setting unit is paid this.
- inframarginal rent = clearing - H2 marginal cost (EUR/MWh) = the operating margin H2 captures.
- gross margin (EUR/kW-yr) = rent x peaker_FLH / 1000  [1 kW over FLH hours = FLH/1000 MWh].
  peaker FLH ~520 h (the peak slice / the slice capacity = peak_GW - the 2000-h base level).
- annualised CAPEX (EUR/kW-yr) = CRF(WACC, 20yr) x 600 EUR/kW + 2% FOM, recovered or not.
RESULT: in 0 of 29 countries, in EVERY scenario, does the rent recover the CAPEX. Best case
(Denmark, H2_PUSH): EUR 25.6/kW-yr earned vs EUR 54.2/kW-yr needed (47% recovery); most winners
recover <20%. The marginal H2 heat producer earns a positive rent but operates at a full-cost
LOSS everywhere -- the classic missing-money problem for low-utilisation plant. So H2 peaking
heat is not a spontaneous market outcome even in its best niches; it needs a capacity payment or
subsidy. Robust to FLH: even at double the running hours, only Denmark would approach break-even.
(Inframarginal-rent / missing-money theory: standard merit-order market economics, e.g. Joskow 2008.)

### 5c. District-heating source-switching merit order — `scripts/merit_order_dh.py` (-> F13)
A DH operator dispatches one stack into the same pipes, cheapest source first. Marginal costs
(EUR/MWh-heat, 2050): waste/excess heat 10 (must-run floor); large DH heat pump = elec/COP 3.0;
biomass CHP = biomass/0.85; gas CHP = gas/0.90 + carbon x 0.202/0.90; H2 = H2/0.90 + storage adder.
H2 sits at/near the TOP of the stack everywhere (mean rank 4.3-5.0 of 5) -> dispatched only for the
residual peak, and only where it undercuts the gas peaker. Countries where H2 < gas CHP / EU-wt H2
DH share: CURRENT 0/29 (0.0%), STATED 5/29 (5.3%), NET_ZERO 11/29 (8.4%), H2_PUSH 10/29 (8.3%).
KEY FINDING: NET_ZERO (high carbon, central H2) beats gas CHP in MORE countries than H2_PUSH
(central carbon, cheap H2). In district heating it is the CARBON PRICE on the gas alternative,
not cheap hydrogen, that opens the door for H2 -- and even then only for the peak sliver above the
waste/HP/biomass baseload. Consistent with 5a/5b: H2's role in heat is a small carbon-priced
peaking residual, never a baseload fuel.
