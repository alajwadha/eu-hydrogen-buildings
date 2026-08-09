# 2025 Residential Heating-Technology Mix — per-country audit (29 countries)

**Date:** 2026-05-26
**Output:** `code/data/country_config/heating_mix_2025.csv` (the values the model reads)
**Generator:** `code/scripts/build_heating_mix_2025.py` (carries the two raw source mixes per country)
**Consumed by:** `Optimisation.py` (per-country `START_MIX`, biomass/H2 ceilings, demand
reduction, turnover) and `Simulation.py` (per-country 2025 base mix for REF/HIGH_HP/H2_HYBRID).

## Why this exists

COST_OPT and the Monte-Carlo scenarios previously used a single EU-average 2025 starting mix
(gas 0.42 / oil 0.12 / …) for all 29 countries. That is wrong (Sweden is ~0% gas, the
Netherlands ~80% gas) and it distorts each country's emissions baseline. This file gives a
per-country 2025 mix over the 8 model technologies, plus per-country biomass/H2 ceilings,
demand-reduction and turnover.

## Method — two independent sources, cross-checked

Each country's mix was estimated **two ways** and the two were compared (the user's
"both, see if they match"):

1. **Eurostat-based (energy)** — Eurostat `nrg_d_hhq` (Disaggregated final energy consumption
   in households), space-heating end-use `FC_OTH_HH_E_SH`, latest year (2022/2023). Fuel→tech
   mapping: natural gas→`gas_boiler`; oil/petroleum **+ solid fossil (coal/peat, flagged)**
   →`oil_boiler`; derived heat→`district_heat`; primary solid biofuels→`biomass_boiler`;
   ambient heat (RA600, = heat-pump renewable output)→`hp_air`; remaining electricity
   →`resistance_heater` (split toward `hp_air` where EHPA penetration is known). UK and CH are
   not in `nrg_d_hhq`: UK from DESNZ ECUK + ONS Census 2021, CH from Swiss FSO/SFOE.
2. **National / industry (dwelling-equipment)** — national statistics, Odyssee-Mure country
   profiles, EHPA / JRC heat-pump data, BPIE, Heat Roadmap Europe.

**Final mix = the mean of the two, renormalised to 1.0.** Rationale: the model allocates
*useful heat* (energy), but the Eurostat *final-energy* basis over-weights inefficient techs
(wood stoves, oil, coal burn at low efficiency → high energy share) while the national
*dwelling-count* basis over-weights low-energy-per-unit techs (heat pumps, district heat). The
two bracket the useful-heat truth, so their mean is the central estimate. Where they diverge
materially (L1 distance > 0.30) the country is flagged below.

## Cross-cutting caveats

- **Energy-vs-dwelling basis** is the dominant source of divergence (not data error): biomass
  and oil look larger in the Eurostat energy basis; HP and DH look larger in the dwelling basis.
- **Coal-as-oil proxy.** The 8 techs have no coal boiler, so residential solid fossil (coal/peat)
  is folded into `oil_boiler`. Material only for **PL** (its `oil_boiler` is ~96% coal), **CZ**
  (~10pp coal), **IE** (~14pp peat/coal); negligible elsewhere. The scope-1 EF understates coal
  (uses oil's 0.265 vs ~0.34 tCO2/MWh) — a documented approximation.
- **Resistance-vs-heat-pump split** of the electricity bucket is the single most uncertain
  parameter everywhere (Eurostat does not separate HP-driving electricity from resistance).
  Most load-bearing for FR, ES, PT, and the warm islands.
- **Estonia** reports ambient heat = 0 in Eurostat 2023 (HP output misclassified); the national
  estimate corrects this (HP ~0.13). The mean reflects the correction.
- **Warm islands (CY, MT)** have no gas grid and no district heating; much "heating" is
  reversible air-to-air units counted as `hp_air`. MT space heating is ~21% of residential
  energy (lowest in EU).

## Per-country final mix (share of 2025 useful heat) + parameters

gas / oil / bio = biomass / res = resistance / hpa = hp_air / hpg = hp_ground / dh = district_heat.
h2_boiler ≈ 0 everywhere in 2025 (omitted). bio_cap = sustainable-biomass ceiling 2050.
**!** marks the 11 countries with high (>0.30) Eurostat-vs-national divergence.

| cc | gas | oil | bio | res | hpa | hpg | dh | bio_cap | h2_2050 | dem_red | notes |
|----|-----|-----|-----|-----|-----|-----|-----|---------|---------|---------|-------|
| DE! | .51 | .21 | .11 | .03 | .05 | .01 | .10 | .12 | 0 | .35 | gas-dominant; oil energy-overweighted |
| FR! | .33 | .11 | .18 | .15 | .16 | .01 | .04 | .15 | 0 | .38 | large electric (resistance vs HP uncertain) |
| IT! | .62 | .05 | .22 | .03 | .06 | .00 | .03 | .12 | 0 | .35 | gas-dominant; wood-stove energy overweight |
| ES! | .31 | .22 | .24 | .12 | .11 | .00 | .01 | .08 | 0 | .32 | weak agreement; reversible-AC heating |
| NL  | .80 | .01 | .05 | .02 | .07 | .01 | .05 | .05 | .03 | .38 | ~80% gas; only NL has a residential-H2 pilot |
| PL! | .16 | .26 | .23 | .01 | .03 | .00 | .32 | .15 | 0 | .335 | oil bucket ~96% COAL; DH large by dwellings |
| BE  | .60 | .23 | .06 | .05 | .03 | .00 | .03 | .10 | 0 | .35 | gas+oil ~83% |
| AT  | .27 | .12 | .27 | .04 | .07 | .02 | .21 | .30 | 0 | .41 | biomass + DH heavy, forest-rich |
| CZ  | .35 | .06 | .16 | .05 | .03 | .01 | .33 | .18 | 0 | .38 | very large DH (coal/gas-fired); some coal |
| SE  | .01 | .01 | .11 | .09 | .17 | .13 | .48 | .30 | 0 | .425 | DH + HP; fossil ~0 |
| DK  | .13 | .04 | .07 | .03 | .07 | .01 | .66 | .10 | 0 | .35 | DH-dominant (~66%) |
| FI  | .01 | .10 | .17 | .24 | .10 | .09 | .28 | .30 | 0 | .38 | large direct-electric + DH + wood |
| RO  | .34 | .01 | .48 | .03 | .01 | .00 | .13 | .30 | 0 | .275 | wood-dominant + gas |
| HU  | .56 | .01 | .30 | .03 | .01 | .00 | .09 | .20 | 0 | .275 | gas-dominant; binds in COST_OPT |
| BG! | .05 | .05 | .52 | .18 | .01 | .00 | .19 | .25 | 0 | .26 | wood-dominant; resistance vs biomass uncertain |
| SK  | .45 | .02 | .22 | .05 | .04 | .01 | .21 | .20 | 0 | .29 | gas + DH; DH larger by dwellings |
| HR  | .25 | .04 | .59 | .02 | .01 | .00 | .08 | .30 | 0 | .305 | wood-dominant; binds in COST_OPT |
| SI! | .14 | .15 | .45 | .06 | .09 | .01 | .11 | .30 | 0 | .305 | wood + real oil use; well-validated (SURS) |
| PT! | .03 | .04 | .52 | .18 | .23 | .00 | .00 | .30 | 0 | .305 | wood (energy) vs electric (dwelling); no DH |
| EL! | .18 | .37 | .27 | .05 | .11 | .00 | .01 | .20 | 0 | .305 | oil + wood; reversible-AC heating |
| IE! | .28 | .56 | .03 | .06 | .07 | .01 | .00 | .10 | 0 | .275 | oil-heavy (incl. ~14pp peat/coal) |
| EE! | .06 | .00 | .41 | .06 | .06 | .01 | .39 | .40 | 0 | .35 | DH + wood; Eurostat HP=0 (corrected) |
| LV  | .07 | .03 | .49 | .01 | .02 | .00 | .38 | .40 | 0 | .3125 | DH + wood (~90% combined) |
| LT  | .12 | .04 | .35 | .03 | .10 | .00 | .36 | .40 | 0 | .3125 | DH + wood + gas |
| LU  | .57 | .23 | .07 | .02 | .06 | .01 | .06 | .10 | 0 | .35 | gas + oil dominated |
| CY  | .00 | .54 | .06 | .09 | .31 | .00 | .00 | .03 | 0 | .35 | no gas/DH; oil + reversible-AC HP |
| MT  | .00 | .09 | .00 | .23 | .69 | .00 | .00 | .02 | 0 | .305 | electricity-only island; reversible-AC HP |
| CH  | .18 | .39 | .12 | .06 | .16 | .06 | .04 | .12 | 0 | .35 | oil #1 (declining); HP rising |
| UK  | .80 | .05 | .02 | .09 | .02 | .00 | .02 | .05 | .02 | .35 | ~85% gas+oil; H2-village trials cancelled |

`demand_reduction_2050` = clip(0.20 + 0.15·renovation_rate, 0.25, 0.50) from the per-country
renovation rate; `turnover_rate` = clip(0.045 + 0.015·renovation_rate, 0.045, 0.065). Both are
transparent monotonic heuristics on the (weak, ~0.3–1.5%/yr) renovation rates, not precise
per-country measurements.

## Sources

Eurostat `nrg_d_hhq` (2022/2023, via Eurostat/DBnomics API); Odyssee-Mure country profiles;
EHPA European Heat Pump Market & Statistics 2023/2024 and JRC heat-pump status fiches 2024;
national statistics (Destatis/BDEW, SDES, ISTAT, IDAE SPAHOUSEC III, CBS, GUS, Statistik
Austria, ČSÚ, Swedish/Danish/Finnish energy agencies, SURS, INE/DGEG, SEAI National Heat Study,
Estonian Competition Authority, SPRK, LSTA, STATEC, Swiss FSO/SFOE, DESNZ ECUK, ONS Census 2021);
IEA Bioenergy country reports; BPIE; Heat Roadmap Europe. H2-for-buildings: ICCT (2050 households)
and national hydrogen strategies (all assign buildings ~0; only NL and UK have/had pilots).
Full per-country two-source pairs are in `code/scripts/build_heating_mix_2025.py`.
