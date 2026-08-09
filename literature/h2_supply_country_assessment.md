# Per-country hydrogen supply-route assessment

> **Authoritative method = the bottom-up delivered-cost model (see the
> "Bottom-up delivered-cost model" section at the end of this file, 2026-06).**
> It supersedes the judgment-bucket multipliers in the qualitative assessment
> below, which remain as the per-country evidence base (EHB connectivity, national
> strategies, project pipeline) that informs the model's per-country drivers.

**Purpose.** Ground the per-country delivered-hydrogen cost multiplier
(`Economics.H2_MULT_BY_COUNTRY`) with real evidence, instead of the earlier crude
"+/-10%, landlocked = dearer" heuristic which was flagged in-code as the
least-grounded parameter. The multiplier is expressed relative to a NW-EU hub
trajectory (~EUR 200/MWh in 2025 -> ~EUR 50/MWh in 2050, central).

**Method.** Eight parallel web-research passes (one per country, CY+MT together),
each covering: (1) domestic green/pink-H2 potential and cost, (2) European Hydrogen
Backbone (EHB) pipeline-import connectivity, (3) blue-H2 / other, (4) whether the
national hydrogen strategy foresees a residential-HEATING role, and (5) a net 2050
delivered-cost multiplier vs the NW-EU hub with a low-central-high band. Conducted
2026-05.

## Headline findings

1. **The "landlocked = dearer" heuristic is largely wrong.** CZ, SK, HU, AT and LU
   are well-connected EHB TRANSIT nodes fed by cheap *repurposed* pipe (~EUR
   0.1-0.2/kg per 1,000 km) from Ukrainian, SE-European and North-African supply.
   Their delivered H2 sits at or only slightly above the hub, not +10%. Several were
   revised DOWN (SK 1.10->1.00, LU 1.10->1.03, CZ/AT 1.10->1.05).

2. **The true high-price outliers are the islands.** Neither Cyprus nor Malta is on
   the EHB. Supply is small-scale domestic solar-H2 (no scale economies, isolated
   grid, desalinated feedwater) or ship-imported ammonia with a steep small-scale
   cracking penalty (~$14/kg at island scale vs ~$3.7/kg at 400 kt/yr). Corrected UP
   from 1.00 to ~1.25 (MT, with the H2-ready Melita pipeline as upside) and ~1.30 (CY).

3. **National strategies almost universally exclude residential heating.** Every
   assessed country reserves H2 for industry/transport and steers buildings to heat
   pumps + district heating (Austria and Switzerland are the most explicit). The
   "delivered residential-H2 price" is therefore a modelling counterfactual in most
   of these countries -- itself a finding that reinforces RQ1.

## Per-country multipliers (vs NW-EU hub; central [low-high])

| Country | Old | New central | Range | One-line basis |
|---|---|---|---|---|
| CZ Czechia | 1.10 | 1.05 | 0.95-1.20 | CEHC + Czech-German interconnector transit hub; nuclear/pink-H2 optionality; thin domestic RES |
| SK Slovakia | 1.10 | 1.00 | 0.92-1.08 | Core EHB node on UA-DE corridor; cheap repurposed pipe; ~60% nuclear; depleted-field storage |
| HU Hungary | 1.10 | 1.08 | 1.00-1.15 | Strong solar + SEEHyC PCI corridor (RO-HU-SK); Paks pink-H2 option; inland transit premium |
| AT Austria | 1.10 | 1.05 | 0.98-1.15 | Three-corridor EHB hub (SoutH2 from N. Africa); largest CE gas/H2 storage; but no coast |
| CH Switzerland | 1.10 | 1.08 | 1.00-1.18 | Alpine HyWay corridor (PMI Dec-2025); but non-EU, winter power deficit, mid-line transit cost |
| LU Luxembourg | 1.10 | 1.03 | 1.00-1.08 | Embedded in dense BE/FR/DE backbone core (HY4Link PCI); near-hub importer despite "landlocked" |
| SI Slovenia | 1.10 | 1.10 | 1.05-1.18 | N. Adriatic valley + 4-way pipe; but constrained RES, ~50% import-dependent, spur-not-trunk |
| CY Cyprus | 1.00 | 1.30 | 1.15-1.70 | NOT on EHB; isolated solar-H2 + desalination; ship-import ammonia is ceiling not floor |
| MT Malta | 1.00 | 1.25 | 1.10-1.65 | NOT on EHB; H2-ready Melita pipe to Sicily is upside; else floating-offshore or ship-import |

Renewable-rich domestic producers (ES, PT, EL, SE, FI, DK, IE) keep ~0.90;
NW-EU / core-backbone countries stay hub-priced at 1.00.

## Sources by country

### CZ — Czechia (1.05 [0.95-1.20])
- EU Clean Hydrogen Observatory, Czech national strategy (2024) — https://observatory.clean-hydrogen.europa.eu/hydrogen-landscape/policies-and-standards/national-strategies/czech-republic
- Central European Hydrogen Corridor, UA-SK-CZ-DE, ~92% repurposed, ~2029 — https://www.cehc.eu/cehc-project/
- Czech-German Hydrogen Interconnector, ~1,068 km, 2030 — https://www.cghi.eu/
- Green Hydrogen Organisation, Czechia (no residential-heating role) — https://gh2.org/countries/czechia
- IEA, Czechia 2025 (heat pumps + district heating for buildings) — https://www.iea.org/reports/czechia-2025/executive-summary

### SK — Slovakia (1.00 [0.92-1.08])
- Eustream, Slovak Hydrogen Backbone / H2I-TR (9.1 GW, PCI 10.5, post-2032) — https://www.eustream.sk/en/transparency/network-development/energy-transformation-projects/
- CEHC, UA-SK-CZ-AT-DE — https://www.cehc.eu/cehc-project/
- EU Clean Hydrogen Observatory, Slovakia (heating "requires further analysis") — https://observatory.clean-hydrogen.europa.eu/hydrogen-landscape/policies-and-standards/national-strategies/slovakia
- CSIRO HyResource, Slovakia (200 kt 2030 -> 400-600 kt 2050, 90% low-carbon, nuclear) — https://research.csiro.au/hyresource/policy/international/slovakia/
- NaturalGasWorld, EPIF/Eustream/Nafta/RWE blue-H2 + CO2 storage — https://www.naturalgasworld.com/eustream-rwe-eye-blue-hydrogen-in-slovakia-92393

### HU — Hungary (1.08 [1.00-1.15])
- EU Clean Hydrogen Observatory, Hungary (240 MW 2030, 2% blend; industry/transport) — https://observatory.clean-hydrogen.europa.eu/hydrogen-landscape/policies-and-standards/national-strategies/hungary
- SEEHyC, South-East European Hydrogen Corridor (HU 399 km, ~2032) — https://www.seehyc.eu/project-description/
- MOL Group, 10 MW green-H2 at Danube refinery (2024) — https://molgroup.info/en/media-centre/press-releases/
- Szabó (RIFS), "Hungary's Hydrogen Strategy: Ambition within Political Confines" (2023) — https://real.mtak.hu/168481/1/RIFS_Discussion_Paper_6002966.pdf

### AT — Austria (1.05 [0.98-1.15])
- eceee, "Austria's new hydrogen strategy slams use in heating, transport" (2022) — https://www.eceee.org/all-news/news/austrias-new-hydrogen-strategy-slams-use-in-heating-transport/
- EU Clean Hydrogen Observatory, Austria — https://observatory.clean-hydrogen.europa.eu/hydrogen-landscape/policies-and-standards/national-strategies/austria
- SoutH2 Corridor (3,300 km, >4 Mtpa, >65% repurposed, early 2030s) — https://www.south2corridor.net/initiative/
- Gas Connect Austria, H2 Backbone WAG + Penta-West (PCI, 2030) — https://h2backbone-wag-pw.at/en/project-description/
- OIES ET32, Green Hydrogen Imports into Europe (2024) — https://www.oxfordenergy.org/wpcms/wp-content/uploads/2024/04/ET32-Green-Hydrogen-Imports-into-Europe-An-Assessment-of-Potential-Sources.pdf

### CH — Switzerland (1.08 [1.00-1.18])
- Enerdata, "Switzerland adopts its national hydrogen strategy" (2024) — https://www.enerdata.net/publications/daily-energy-news/switzerland-adopts-its-national-hydrogen-strategy.html
- Hydrogen Europe, "Hydrogen imports to drive Swiss demand surge from 2035" (2024) — https://hydrogeneurope.eu/hydrogen-imports-to-drive-swiss-demand-surge-from-2035-under-new-strategy/
- Fluxys, Alpine Hydrogen Corridor / Alpine HyWay (PMI+PCI Dec 2025) — https://www.fluxys.com/en/projects/alpine-hydrogen-corridor-alpine-hyway-linking-germany-switzerland-to-hydrogen-supply-from-italy
- ETH Zurich, "Hydrogen for ground transportation and heating is a bad idea" (2021) — https://ethz.ch/en/news-and-events/eth-news/news/2021/11/hydrogen-for-ground-transportation-and-heating-is-a-bad-idea.html

### LU — Luxembourg (1.03 [1.00-1.08])
- EU Clean Hydrogen Observatory, Luxembourg (buildings as fallback; import reliance) — https://observatory.clean-hydrogen.europa.eu/index.php/hydrogen-landscape/policies-and-standards/national-strategies/luxembourg
- Creos Luxembourg, Hydrogen grid / HY4Link (PCI, ~120 km BE/FR/DE, 2032-34) — https://www.creos-net.lu/en/individuals/creos-luxembourg/hydrogen-grid
- EHB country-specific developments (full connection via BE & DE by 2040, MosaHyc) — https://ehb.eu/page/country-specific-developments
- Green Hydrogen Organisation, Luxembourg (no residential-heating use) — https://gh2.org/countries/luxembourg

### SI — Slovenia (1.10 [1.05-1.18])
- EHB country narratives, Slovenia as import corridor (4-way interconnections) — https://ehb.eu/page/country-specific-developments
- Plinovodi, European Integration / SoutH2, Murfeld, Krk (interconnections by 2035) — https://www.plinovodi.si/en/hydrogen/european-integration/
- North Adriatic Hydrogen Valley (EUR 700m, >5,000 t/yr) — https://www.nahv.eu/about-nahv/
- Balkan Green Energy News, Slovenia updated NECP (100 MW; buildings 55% RES) — https://balkangreenenergynews.com/slovenia-adopts-updated-integrated-national-energy-and-climate-plan/

### CY — Cyprus (1.30 [1.15-1.70]) and MT — Malta (1.25 [1.10-1.65])
- EU Clean Hydrogen Observatory, Cyprus strategy (domestic solar-H2 only, water scarcity) — https://observatory.clean-hydrogen.europa.eu/index.php/hydrogen-landscape/policies-and-standards/national-strategies/cyprus
- EHB country narratives (neither CY nor MT appears) — https://ehb.eu/page/country-specific-developments
- Melita TransGas Pipeline, PCI 5.19 (H2-ready Malta-Italy) — https://energywateragency.gov.mt/pci-5-19-melita-transgas-pipeline/
- IRENA, Global Hydrogen Trade to Meet the 1.5C Goal (shipping ~$0.10/kg per 1,000 km) (2022) — https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2022/Jul/IRENA_Global_hydrogen_trade_part_1_2022_.pdf
- "Technoeconomic Evaluation of Ammonia Cracking: A Question of Colors and Scale" (small-scale ~$14.3/kg vs large ~$3.7/kg) — https://www.researchgate.net/publication/384841070
- ODYSSEE-MURE, household energy (Malta lowest space-heating share; CY/MT highest AC) — https://www.odyssee-mure.eu/publications/efficiency-by-sector/households/household-eu.pdf

## Implication for the model

The grounded multipliers move the EHB-connected CE countries CLOSER to the hub
(narrowing their H2-vs-heat-pump gap slightly) and the islands FURTHER from it. The
headline RQ1 conclusion is unaffected: none of the narrowed-gap CE countries reaches
heat-pump parity even at the low end of its multiplier band (the narrowest baseline
gaps -- DK +1, PL +7, FI +10, CZ +11 -- do not close), and the islands have near-zero
residential heating demand so their upward correction is immaterial to the heating
result. The most policy-relevant finding is qualitative: in nearly every above-average
country, the national hydrogen strategy explicitly excludes residential heating, so
hydrogen-for-buildings is a counterfactual the model prices rather than a planned
supply chain.

---

## Bottom-up delivered-cost model (2026-06) — authoritative

The judgment buckets above were replaced by a transparent bottom-up model
(`code/scripts/h2_delivered_cost.py`) in response to the critique that the
multiplier should reflect MORE than renewable resource (it must also capture cost
of capital, labour, electricity/feedstock price, and supply routes other than
imports). For each country the model levelises EVERY supply route and takes the
cheapest:

- **GREEN** dedicated-renewable electrolysis — LCOE(capacity factor, WACC, labour)
  + electrolyser CAPEX(WACC, labour) + water; isolated islands carry a small-scale
  grid penalty.
- **PINK** nuclear electrolysis (nuclear countries) — firm power at ~EUR 78/MWh,
  90% load factor.
- **BLUE** gas reforming + CCS (gas+CO2-storage countries) — gas feedstock + CAPEX
  + CCS.
- **PIPE** pipeline import — hub price + transport (connectivity premium).
- **SHIP** seaborne ammonia import — sunbelt production + synthesis/shipping/
  cracking block (+ small-scale penalty for island terminals).

**Cost drivers** (the user's point — not just sun/wind): WACC (`DISCOUNT_RATE_BY_
COUNTRY`), construction labour (`LABOUR_COST_MULTIPLIER`), per-country electricity
and gas price, renewable capacity factor, water scarcity, pipeline connectivity,
and nuclear / CO2-storage availability.

**Calibration to verified 2050 benchmarks** (cross-checked, see below): electrolyser
CAPEX ~EUR 300/kW and green LCOH (IRENA Global Hydrogen Trade Costs 2022); blue
~EUR 2.7/kg = matches IEAGHG 2022-07 SMR/ATR+CCS (EUR 2.67-2.72/kg); pipeline
transport EUR 0.16/kg per 1000 km (European Hydrogen Backbone 2022); delivered/import
costs (OIES ET24 Alsulaiman 2023; ET32 Rikabi 2024; ET08 2022). EU-median delivered
cost = EUR 48/MWh (EUR 1.61/kg), set as the hub (multiplier 1.0) — consistent with
published domestic-EU green (~EUR 1.4/kg) and import (~EUR 2.0/kg) figures.

### Key findings

1. **Pink and blue are NEVER the cheapest route in 2050.** Nuclear electrolysis
   (~EUR 127/MWh, set by firm nuclear power cost) and gas+CCS (~EUR 81/MWh) are both
   beaten by cheap green or imported hydrogen. The "nuclear/CCS optionality" the
   qualitative research flagged for Central Europe does not lower delivered cost.
2. **Capital and labour, not sunshine, drive the ranking.** High-WACC Greece (8%)
   sits at 1.04 despite superb solar; cheap-capital strong-wind Ireland/Denmark/
   Baltics self-supply green H2 well below the median (0.77-0.87).
3. **Pipeline import caps connected countries** at hub +5-15%; the dearest are the
   landlocked CE states (SK/CZ/HU/SI/IT ~1.14-1.16) and the non-backbone islands
   (CY/MT ~1.31-1.33).
4. **Heating implication.** At central values only Denmark reaches heat-pump parity
   in 2050; any distribution-infrastructure cost removes it. Even at the cheapest
   end of every country's supply band (free-grid), only a cluster of ~9 cold
   cheap-wind northern countries reach parity, and pricing distribution closes all
   but the coldest. OIES ET29 (Dickel 2024) concludes any heating hydrogen would be
   BLUE (~EUR 81/MWh), dearer than the green/import cost modelled — so the gap is
   conservative.

### Final per-country multipliers (delivered cost / EU-median; central [low-high])

| Country | Cheapest route | Delivered EUR/kg | Multiplier | Range |
|---|---|---|---|---|
| IE | green | 1.24 | 0.77 | 0.58-1.00 |
| DK | green | 1.33 | 0.82 | 0.61-1.08 |
| EE | green | 1.34 | 0.83 | 0.63-1.07 |
| UK | green | 1.34 | 0.83 | 0.62-1.08 |
| LV | green | 1.36 | 0.84 | 0.63-1.08 |
| LT | green | 1.36 | 0.84 | 0.63-1.08 |
| PT | green | 1.34 | 0.84 | 0.63-1.07 |
| SE | green | 1.38 | 0.86 | 0.63-1.11 |
| FI | green | 1.39 | 0.87 | 0.65-1.12 |
| ES | green | 1.48 | 0.92 | 0.69-1.18 |
| NL | green | 1.50 | 0.93 | 0.69-1.21 |
| BG | green | 1.50 | 0.93 | 0.71-1.19 |
| AT | green | 1.52 | 0.94 | 0.70-1.22 |
| RO | green | 1.55 | 0.97 | 0.73-1.24 |
| CH | green | 1.61 | 1.00 | 0.74-1.31 |
| BE | green | 1.63 | 1.02 | 0.75-1.27 |
| EL | green | 1.67 | 1.04 | 0.78-1.33 |
| PL | green | 1.68 | 1.05 | 0.78-1.34 |
| HR | green | 1.71 | 1.07 | 0.80-1.37 |
| FR | pipe | 1.75 | 1.09 | 0.83-1.27 |
| LU | pipe | 1.75 | 1.09 | 0.90-1.27 |
| DE | pipe | 1.75 | 1.09 | 0.82-1.27 |
| SK | pipe | 1.83 | 1.14 | 0.91-1.35 |
| HU | green | 1.84 | 1.14 | 0.86-1.38 |
| CZ | pipe | 1.83 | 1.14 | 0.87-1.35 |
| SI | pipe | 1.87 | 1.16 | 0.91-1.38 |
| IT | green | 1.86 | 1.16 | 0.86-1.38 |
| MT | green | 2.10 | 1.31 | 1.02-1.64 |
| CY | green | 2.14 | 1.33 | 1.03-1.68 |

### Verified calibration sources

- **OIES ET24** — Alsulaiman (2023), *Renewable Hydrogen Import Routes into the EU*: 2030 landed green-ammonia LCOH to Rotterdam ~USD 2.1-2.7/kg; production-only ~USD 1.6-2.1/kg; electrolyser EUR 500/kW, electricity EUR 30/MWh. https://www.oxfordenergy.org/publications/renewable-hydrogen-import-routes-into-the-eu/
- **OIES ET32** — Rikabi (2024), *Green Hydrogen Imports into Europe*: 2050 production ~EUR 1.0-1.25/kg (Morocco/Chile/Australia); ammonia transport+cracking ~EUR 1.5/kg, cracking alone ~EUR 2/kg. https://www.oxfordenergy.org/wpcms/wp-content/uploads/2024/04/ET32-Green-Hydrogen-Imports-into-Europe-An-Assessment-of-Potential-Sources.pdf
- **OIES ET08** — Lenivova & Hove (2022): 2030 supply ~EUR 3/kg; blue ~EUR 2.6/kg; pipeline transport USD/1000km/kg retrofitted 0.13 / new 0.24-0.64; green needs electricity <= EUR 50/MWh for EUR 3/kg.
- **OIES ET29** — Dickel (2024), *Decarbonising Germany's Heating Sector*: heating H2 would be BLUE (ATR+CCS); gas-grid conversion ~EUR 30bn; argues a mixed HP/DH/H2 portfolio (no per-kWh H2-vs-HP comparison). https://www.oxfordenergy.org/publications/decarbonising-germanys-heating-sector/
- **IRENA** (2022) *Global Hydrogen Trade Costs*: electrolyser 2050 EUR 120-300/kW; 45-48 kWh/kg; best-case green USD 0.65-0.76/kg; poor-resource/high-WACC up to USD 2/kg; WACC 4%->6% raises RE-LCOE +37%; desalination <4% of LCOH.
- **IEAGHG** (2022-07) blue SMR/ATR+CCS 2050 EUR 2.4-2.9/kg (central ~2.7); gas-price sensitivity ~±EUR 0.12/kg per ±10% gas.
- **European Hydrogen Backbone** (2022): pipeline transport EUR 0.11-0.21/kg per 1000 km (central 0.16); 60% of the 2040 network repurposed.
- **OECD WP227** (2023): cost-of-capital 10%->20% raises green H2 LCOH up to +73%; project WACCs span 6.4-24%.
