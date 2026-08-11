# V7 text-only revision log

Every passage changed relative to V6, with original and revised wording, in the order of
the specification. No numerical result, table cell, equation, parameter value, assumption,
citation, scenario definition or model output was altered. No model was run.

---

## 1. Graphical abstract: spatial description

`code/scripts/graphical_abstract.py`, both canvases.

**Original**
> 29 European markets (EU-27, UK, Switzerland) · 1,369 NUTS3 regions · 2025 to 2050

**Revised**
> 29 European markets (EU-27, UK, Switzerland)
> 1,369-region NUTS3 demand surface · 2025 to 2050

Wrapped to two lines on the tall canvas because the longer string reached the right edge
and the file's own clip gate rejected it. The wide upload variant was already two lines.

## 2. Graphical abstract: capital-recovery claim and the two sets of seven

**Original**
> Counts charge both carriers symmetrically, hydrogen paying its own last-mile network. No market recovers the peaker's capital from market rent. On the high carbon path hydrogen wins the power peak only in the 7 salt-cavern markets, a different seven; the 5 that build would need €31 to 63/kW-yr to be financeable.

**Revised**
> Counts charge both carriers symmetrically, including hydrogen's own last-mile network. No tested market reaches full peaker-capital recovery across the assumed scarcity margins. On the high-carbon path, hydrogen wins the power peak in seven salt-cavern markets, a different set from its base-load wins; the five that build require €31–63/kW-yr to be financeable.

Two deviations from the supplied text, both to avoid hard-coding a model output as a
literal. "seven" and "five" remain the artefact-derived counts rendered as words, and
"a different set from its base-load wins" replaces "a different set from the seven
base-load wins" because the base-load count is not among the values this panel reads and
deriving it would have meant computing a new number.

## 3. Abstract

Replaced in full with the supplied version, verbatim. Rendered word count **250** (the
specification labelled it 249; a whitespace split of the supplied text gives 250 either
way). Within Applied Energy's 250-word limit.

## 4. Nomenclature

**$K^{\mathrm{T}}$**
> *orig:* Eq. (2) turns it into an annual charge by applying CRF_c+f; this is the €600/kW of the abstract and of Section 3.4
> *rev:* Eq. (2) annualises this cost by applying CRF_c+f

**Country index**
> *orig:* c — Country (region) index
> *rev:* c — Country index

**Turbine efficiencies**
> *orig:* The winter-peak merit order that sets the win counts holds both at 0.40, so that comparison is even-handed. The capital-recovery layer instead lets them evolve, the gas turbine to 0.42 by 2050 and the hydrogen turbine to 0.44, or 0.48 under H2 Push, which assumes an advanced simple-cycle machine; there the hydrogen unit is deliberately given the better turbine
> *rev:* The headline winter-peak merit order holds both turbines at an efficiency of 0.40. The capital-recovery layer uses evolving efficiencies: 0.42 for gas and 0.44 for hydrogen by 2050, rising to 0.48 for hydrogen under H2 Push, which assumes an advanced simple-cycle machine

**$\pi^{\mathrm{s}}$** (consistency with the body's new terminology)
> *orig:* Scarcity premium (low/central/high {30,60,120} €/MWh; the sensitivity grid adds 90)
> *rev:* Scarcity margin (low/central/high {30,60,120} €/MWh; the sensitivity grid adds 90)

All four propagated to `frontmatter_body.tex`, the Word path.

## 5. Methods: NUTS3 sentence and Figure 1

**Methods**
> *orig:* Coverage spans the EU-27, the United Kingdom and Switzerland, and demand resolves to the third level of the Nomenclature of Territorial Units for Statistics (NUTS3), 1,369 regions, aggregating to the country before the economic tests apply.
> *rev:* Coverage spans the EU-27, the United Kingdom and Switzerland. Demand is resolved at the third level of the Nomenclature of Territorial Units for Statistics as a 1,369-region NUTS3 demand surface, then aggregated to country level before the economic tests.

**Figure 1** (`code/scripts/fig_model_flow.py`)
> *orig:* Residential useful heat reconstructed bottom-up for 1,369 NUTS3 regions across 29 markets, validated against national statistics
> *rev:* A 1,369-region NUTS3 residential useful-heat demand surface reconstructed bottom-up across 29 markets and validated against national statistics

## 6. Methods: aggregate validation wording

> *orig:* The two agree to −0.8 per cent across the aggregate and to within ±25 per cent in 28 of the 29 countries.
> *rev:* The bottom-up reconstruction is 0.8 per cent below the benchmark in aggregate, and 28 of the 29 country estimates lie within ±25 per cent.

## 7. Weather description

> *orig:* The weather series is the strongest assumption in the paper and every power-sector number descends from it, so we state it here rather than leaving it to the Supplementary Information. The power layer runs on synthetic hourly series, not reanalysis or metered data, and on one realisation of a single year.
> *rev:* The weather construction is the dominant limitation on the power-sector results. The power layer uses one synthetic hourly year rather than reanalysis or metered data.

> *orig:* The firm-fleet requirement carries a band of about ±9 per cent from the assumed event length alone, and a reader should treat it, the full-load hours and the cumulative shortfall as conditional on this constructed year, and not as an adequacy assessment.
> *rev:* The firm-fleet requirement varies by about ±9 per cent with the assumed event length. The resulting capacity requirement, full-load hours and cumulative shortfall are conditional on the constructed weather year and should not be interpreted as adequacy estimates.

## 8. Monte Carlo punctuation

> *orig:* …correlated country-carrier fuel-price multipliers, Cross-country shock correlation is 0.5…
> *rev:* …correlated country-carrier fuel-price multipliers. Cross-country shock correlation is 0.5…

The sampled-parameter list and the correlation values are unchanged.

## 9. Opening of Results

> *orig:* Section 3.1 sets the demand, technology-mix and emissions spine those tests run on, and the last two sections are cross-checks, a heat-pump and district-heat cost program and the standalone Switzerland case. The 200-sample Monte Carlo carries the demand, technology-mix and emissions spine as medians with percentile bands. The cost, dispatch and capital-recovery tests are evaluated at central parameters, with their governing prices and charges swept as deterministic axes. Running medians settle inside a ±1 per cent tube by draw 139 and the deciles only by 188, so we read medians as converged and deciles as indicative.
> *rev:* Section 3.1 reports the demand, technology-mix and emissions results used by the subsequent tests. Sections 3.5 and 3.6 provide the least-cost and Switzerland cross-checks. Monte Carlo results for demand, technology mix and emissions are reported as medians with percentile bands. The cost, dispatch and capital-recovery tests use central parameters with their governing prices and charges evaluated in deterministic sweeps. Running medians enter and remain within ±1 per cent by draw 139, whereas the deciles do so only by draw 188. Medians are therefore treated as converged and deciles as indicative.

Section numbers are LaTeX cross-references, so they renumber with the document.

## 10. Demand-validation metrics

> *orig:* However, across the 29 countries the mean absolute deviation is 11.6 per cent, demand-weighted 9.8 per cent, root-mean-square 14.4 per cent and median 8.5 per cent. In addition, backcasting to the benchmark's 2015 vintage widens the aggregate to −8.3 per cent. That layer sets the demand field and the weights every later statistic carries, and everything after it runs on country parameters, so no cost ordering is resolved beneath it.
> *rev:* Across the 29 countries, the mean absolute percentage error is 11.6 per cent, the demand-weighted mean absolute percentage error is 9.8 per cent, the root-mean-square error of the percentage deviations is 14.4 percentage points, and the median absolute percentage error is 8.5 per cent. Backcasting to the benchmark's 2015 vintage produces an aggregate deviation of −8.3 per cent. That layer sets the demand field and the weights every later statistic carries, and subsequent economic parameters are applied at country level, so the model does not resolve subnational cost rankings.

## 11. Heat-pump CAPEX explanation removed from Results

> *orig:* Fuel is the largest component of all three, the heat pump carries the largest capital charge at about 28 per cent because its equipment is sized to peak heat demand, and the hydrogen boiler's network-and-storage charge at about 27 per cent matches its capital and fixed operating charges combined.
> *rev:* Fuel is the largest cost component for all three technologies. Capital accounts for about 28 per cent of median heat-pump LCOH, while the hydrogen boiler's network-and-storage component, at about 27 per cent, is comparable to its combined capital and fixed O&M.

## 12. Weighted mean

> *orig:* Across all 29 the median country gap is +€15.4/MWh, whereas the 2025 demand-weighted mean is only +€1.4/MWh, since hydrogen still competes in the large north-western markets
> *rev:* Across all 29 markets, the median 2050 country gap is +€15.4/MWh, whereas the mean weighted by 2025 country heat demand is +€1.4/MWh, since hydrogen still competes in the large north-western markets

## 13. Figure 4 note

> *orig:* each 2050 stack sums to the median quoted in the text
> *rev:* each 2050 stack sums to the median reported in the main text

## 14. "Asymmetric accounting" removed at all three substantive sites

**Table 1 footnote d**
> *orig:* Stated Policies sets adoption above it, which Section 3.3 reports as a finding. The asymmetric accounting gives 0, 5.1, 7.9 and 9.3 per cent.
> *rev:* Stated Policies sets adoption above it (Section 3.3). The sensitivity excluding hydrogen last-mile distribution and using the residential rather than wholesale gas tariff gives 0, 5.1, 7.9 and 9.3 per cent.

Footnote c was shortened by eight words in the same edit, to hold the float within the
125-word caption-plus-notes limit that the longer phrase would otherwise have breached:
"and the realised medians sit a little above them for the reason given in the text" →
"so realised medians sit slightly above them".

**Section 3.4**
> *orig:* The same molecule wins operating-cost dispatch in up to 7 of 29 district-heat markets, and 20 on the asymmetric accounting.
> *rev:* Hydrogen wins operating-cost dispatch in up to 7 of 29 district-heat markets under the symmetric treatment and in 20 under the sensitivity excluding hydrogen last-mile distribution and using the residential rather than wholesale gas tariff.

**Switzerland**
> *orig:* (16 against 15 on the asymmetric accounting)
> *rev:* the sensitivity excluding hydrogen last-mile distribution and using the residential rather than wholesale gas tariff gives 16 rather than 15

**Table 2 note** (already carried the long form in V6; unchanged)

## 15. "The first two counts" identified

> *orig:* Under the sensitivity excluding hydrogen last-mile distribution and using the residential rather than wholesale gas tariff, the first two counts read 16 and 20.
> *rev:* Under the sensitivity excluding hydrogen last-mile distribution and using the residential rather than wholesale gas tariff, the building-winter-peak count becomes 16 and the district-heat-peak count becomes 20.

## 16. Figure 5 introduction

> *orig:* Fig. 5 presents the 2050 power merit order in Denmark under H2 Push, and Fig. 6 the markets in which hydrogen undercuts the gas peaker. Hydrogen's advocates cast it as a peaker serving only the cold-snap tip, when the air-source COP collapses, so we reprice it on SRMC across the building, district-heat and power-sector peaks.
> *rev:* Fig. 5 presents H2 Push merit-order prices for Denmark against the study-area peaking fleet sized on the Stated Policies demand path; Fig. 6 identifies the markets in which hydrogen undercuts the gas peaker. To test hydrogen as a cold-snap peaker when air-source heat-pump COP declines, we compare its SRMC with the competing unit in the building, district-heat and power-sector peak calculations.

## 17. Equal- and evolving-efficiency paragraph

> *orig:* The model prices the dispatchable tip and holds the rungs below it at literature short-run costs. The figures are H2 Push, and Net Zero holds the same ordering with a narrower cavern advantage. On the equal-efficiency series that sets the win counts the hydrogen turbine's cross-country median is about €286/MWh-e, some €30/MWh-e above the carbon-priced gas peaker at €256/MWh-e, so gas remains the cheaper firm unit in the typical market (Eq. (1); Fig. 5). Both run the high carbon path, which lifts the gas peaker to that €256/MWh-e; on the central path it sits near €181 and the cavern advantage narrows to a few euros, so this count is conditional on the carbon path, whereas the base-load ordering is not (Supplementary Section S1.3). By contrast, on the evolving-efficiency series the medians close to €238 against €239/MWh-e and the undercut count rises to 15, or 8 without the backbone discount, no longer confined to cavern geology. The headline winner count uses equal turbine efficiencies. The evolving-efficiency sensitivity gives the hydrogen turbine the more efficient machine and yields 15 winners, or eight without the backbone discount. Capital recovery is evaluated separately under the evolving-efficiency assumptions for the five of the seven headline cavern markets that build peaking capacity. The seven-market dispatch count and the recovery ratios therefore answer different questions. In the seven the turbine falls to €168 to 184/MWh-e, €72 to 89 below the gas peaker, and across the 22 non-cavern markets sits about €36 above.

> *rev:* The model prices the marginal dispatchable units using literature-based short-run costs for the technologies below them in the merit order. The medians quoted here are H2 Push, and Net Zero holds the same ordering with a narrower cavern advantage. Under the equal-efficiency series used for the headline winner count, the hydrogen turbine's cross-country median is about €286/MWh-e, approximately €30/MWh-e above the carbon-priced gas peaker at €256/MWh-e (Eq. (1); Fig. 5). Gas is therefore the cheaper firm unit in the typical market. Both turbines are evaluated on the high-carbon path. On the central carbon path, the gas peaker is about €181/MWh-e and the cavern advantage narrows to a few euros, so the headline winner count is conditional on the carbon path, whereas the base-load ordering is not (Supplementary Section S1.3). Under the evolving-efficiency sensitivity, hydrogen receives the higher assumed turbine efficiency; the hydrogen and gas medians converge to approximately €238 and €239/MWh-e, respectively, and the hydrogen winner count rises to 15, or eight without the backbone discount, and is no longer confined to cavern geology. Capital recovery is evaluated separately under the evolving-efficiency assumptions for the five of the seven headline cavern markets that build peaking capacity. The seven-market headline dispatch count and the capital-recovery ratios therefore address different questions. In the seven headline cavern markets, the hydrogen turbine costs €168–184/MWh-e, €72–89/MWh-e below the gas peaker; across the 22 non-cavern markets it is approximately €36/MWh-e more expensive.

The 15 and eight results now appear once. Three items were kept from the original that the
supplied replacement omitted: the scenario attribution of the medians, the equation and
figure cross-references, and the Supplementary Section S1.3 pointer. Dropping them would
have removed content the specification did not ask to remove.

## 18. Ranking of the seven markets

> *orig:* in descending advantage Denmark, the United Kingdom, the Netherlands, Romania, Poland, and France and Germany tied (Fig. 6), and are not the seven hydrogen holds on base load.
> *rev:* in descending advantage Denmark, the United Kingdom, the Netherlands, Romania and Poland, followed by France and Germany, which are tied (Fig. 6). They are not the seven markets in which hydrogen wins the base-load comparison.

## 19. Power-sector blue-hydrogen wording

> *orig:* Alternative readings move it, since including Iberia gives nine and restricting France to its northern basins six. Provenance moves it further. At the €81/MWh blue figure read flat across Europe the turbine reaches €289/MWh-e and all seven reverse, while on a green-to-blue ratio they hold at €30 to 57/MWh-e.
> *rev:* Alternative cavern classifications move it, since including Iberia gives nine and restricting France to its northern basins six. Provenance moves it further. With a uniform blue-hydrogen price of €81/MWh across Europe, the turbine reaches €289/MWh-e and all seven headline power-sector wins reverse. Scaling each country's green-hydrogen price by the 81/50 ratio instead preserves hydrogen advantages of €30–57/MWh-e in those seven markets.

## 20. Capital-recovery screen

> *orig:* Wherever hydrogen is the cheaper firm unit it sets the clearing price at its own short-run cost plus the scarcity premium π^s, so its rent is that premium and recovery is
> *rev:* Under the fixed scarcity-margin screen, a hydrogen unit that is the cheaper firm technology is assigned a price equal to its SRMC plus the assumed scarcity margin π^s. Its modelled scarcity rent is therefore π^s, and recovery is

## 21. Private-finance sentence

> *orig:* No tested market reaches the 100 per cent private finance requires over the €30 to 120/MWh scarcity-margin range
> *rev:* No tested market reaches the 100 per cent recovery threshold required for private finance over the €30–120/MWh scarcity-margin range

## 22. Capacity separated from utilisation

> *orig:* The role the missing money implies divides in two.
> *rev:* The peaking fleet is large in capacity but small in annual energy.

> *orig:* On each scenario's own demand path, same stack and weather year, it runs 242 to 278 GW at 131 to 148 full-load hours.
> *rev:* Using each scenario's own demand path with the same technology stack and weather year, required peaking capacity ranges from 242 to 278 GW and utilisation from 131 to 148 full-load hours.

## 23. Value-of-lost-load sensitivity

> *orig:* lifts the central 8.7 to about 51 per cent, so the direction survives and the magnitude does not.
> *rev:* raises capacity-weighted recovery from 8.7 per cent to about 51 per cent. Recovery remains below 100 per cent, but its estimated magnitude is therefore sensitive to the treatment of shortage hours.

## 24. Energy-only caveat and legal wording

> *orig:* The third is that our energy-only baseline describes no real market, since three of the seven already run a mechanism. European law already carries an emissions condition of the kind selection would require, and on our own figures it does not bite. […] A 2050 build therefore faces the rate limb alone, and an unabated open-cycle turbine clears it at about 505 gCO2/kWh-e on our own emission factor, so the Article offers no selection lever here.
> *rev:* Third, the modelled energy-only scarcity-margin screen does not represent any single real market, and three of the seven markets already operate a capacity mechanism. European law already includes an emissions condition, but it does not bind for a 2050 build under the model assumptions. […] A 2050 build therefore faces the rate limb alone. Using the model's emission factor, an unabated open-cycle turbine emits about 505 gCO2/kWh-e, below the 550 gCO2/kWh-e threshold. Article 22(4) therefore does not distinguish between the technologies in this case.

The 350 kgCO2/kWe-yr annual limb and its pre-July-2019 commissioning condition are
retained verbatim.

## 25. Least-cost cross-check

> *orig:* The mix speaks to district heat and heat pumps, not to a technology the program was never free to choose.
> *rev:* The resulting mix informs the comparison between district heat and heat pumps, but not hydrogen, because hydrogen is fixed at zero in 27 countries and at its ceiling in the other two.

> *orig:* Supplementary Section S2.8 gives three bounds on reading it, the largest district heat's unpriced connection charge.
> *rev:* Supplementary Section S2.8 reports three interpretive bounds. The largest limitation is the omitted district-heat connection charge.

> *orig:* The discounted present-value system cost varies by only 0.05 per cent between the −75 and −100 per cent caps, so ambition is cheap in this program.
> *rev:* The discounted present-value system cost differs by only 0.05 per cent between the −75 and −100 per cent caps under this formulation.

"scope-1 emissions cap" already carried its space in V6; verified, no change needed.

## 26. Switzerland

> *orig:* The clean grid removes the carbon argument and the geology the storage argument, so what remains of the gap is the retail levy on electricity, a few euros per megawatt-hour.
> *rev:* Switzerland's clean grid limits hydrogen's carbon advantage, while the absence of salt caverns removes its low-cost-storage advantage.

> *orig:* On the endogenous arm the peaking arena runs the same way, unaffected by the levy question because both turbines buy fuel at wholesale. There the hydrogen peaker loses the Swiss winter peak in all four scenarios, priced out by storage cost alone at €135 to 236/MWh-heat against a heat-pump peak of €62 to 90/MWh-heat. The uncoupled 29-country comparison prices that peak at €155/MWh-heat without crediting the reservoir fleet, so hydrogen does win under H2 Push, and crediting the fleet drops the peak to €90/MWh-heat and removes the win. We read the Swiss peaking verdict off the endogenous arm, the better-specified for that test; the base-load figures above are the uncoupled arm, whose €5.6/MWh gap is the narrower of the pair, against €9.6/MWh on the endogenous one. The arena counts stay on the uncoupled series, whose symmetric H2 Push building-peak count is 14 against the endogenous 13 (16 against 15 on the asymmetric accounting), because the coupling exists for Switzerland alone and the uncoupled series is the more hydrogen-favourable of the pair.
> *rev:* On the endogenous arm, both turbines purchase fuel at wholesale prices, so retail levy treatment does not affect the peaking comparison. Hydrogen loses the Swiss winter peak in all four scenarios, at €135–236/MWh-heat compared with €62–90/MWh-heat for the heat pump. The uncoupled 29-country comparison prices the H2 Push peak at €155/MWh-heat without crediting the Swiss reservoir fleet, producing a hydrogen win; crediting the reservoir fleet lowers the peak price to €90/MWh-heat and removes that win. The endogenous arm is therefore used for the Swiss peaking verdict, while the uncoupled arm supplies the reported base-load results. The base-load gap is €5.6/MWh on the uncoupled arm and €9.6/MWh on the endogenous arm. For cross-market comparability, the arena counts remain on the uncoupled series: the symmetric H2 Push building-peak count is 14 rather than the endogenous count of 13, and the sensitivity excluding hydrogen last-mile distribution and using the residential rather than wholesale gas tariff gives 16 rather than 15. Coupling is modelled only for Switzerland, and the uncoupled series is the more hydrogen-favourable comparison.

## 27. Synthesis paragraph

> *orig:* The base-load market count is the least robust of the three, ranging from 13 to 29 markets across the hydrogen-price paths tested.
> *rev:* The base-load comparison is the least robust of the three: the number of markets in which the heat pump beats hydrogen ranges from 13 to 29 across the hydrogen-price paths tested.

## 28. Opening of the Conclusion

> *orig:* This study screens Europe's building-heat choice across 29 markets to 2050, pricing hydrogen as a system operator does. The three tests address different operating roles and are not statistically independent.
> *rev:* This study screens European residential heat across 29 markets to 2050 in three operating roles. The tests address distinct questions but share some input assumptions.

The two sentences on seasonal storage and the capital-recovery ratio are retained verbatim.

## 29. Conclusion finding 1

> *orig:* (1) On base-load levelised cost the best 2050 heat pump delivers €118.5/MWh against €122.8 for the hydrogen boiler and €132.7 for gas, beating gas in 24 of the 29 markets, 19 to 29 across the carbon paths, and hydrogen in 22 when firm-generation cost is allocated pro rata to heating's share of annual electricity demand, falling to 19 at the low bound and 17 at the high one when it is allocated by the change in peaking capacity. The all-29 median gap is €15.4/MWh and the demand-weighted mean €1.4/MWh, because the markets hydrogen holds are the large ones.
> *rev:* (1) On central 2050 levelised cost, the best heat pump delivers at €118.5/MWh, compared with €122.8/MWh for the hydrogen boiler and €132.7/MWh for gas. Heat pumps beat gas in 24 of the 29 markets under the central carbon path; the count ranges from 19 to 29 across the carbon paths tested. Against hydrogen, heat pumps win in 22 markets when firm-generation cost is allocated pro rata to heating's annual electricity-demand share. Allocation by the change in peaking capacity gives 19 heat-pump wins at the low bound and 17 at the high bound. The median 2050 country gap is €15.4/MWh, while the mean weighted by 2025 country heat demand is €1.4/MWh because the hydrogen-favouring markets are relatively large.

## 30. Conclusion finding 2

> *orig:* (2) The seven markets hydrogen holds on base load are the paper's least robust count. The count behind them runs from 13 to 29 across the hydrogen-price paths tested, and Dickel concludes that the hydrogen realistically supplied to heat would be blue, at about €81/MWh on the route priced here, which closes all seven. Levelling the carriers' fiscal treatment would move the comparison the same way, by an amount beyond the scope of this study.
> *rev:* (2) Under the central symmetric accounting, hydrogen wins the base-load comparison in seven markets and heat pumps in 22. Across the hydrogen-price paths tested, the number of heat-pump wins ranges from 13 to 29. Dickel concludes that the hydrogen realistically supplied to heat would be blue, at about €81/MWh on the route priced here. A uniform blue-hydrogen price of €81/MWh removes hydrogen's advantage in all seven central green-hydrogen base-load markets. Scaling each country's green-hydrogen price by the 81/50 ratio instead leaves Denmark as the sole hydrogen win. Levelling the carriers' fiscal treatment moves the comparison in the same direction, by an amount outside this study's scope.

The Dickel and IEAGHG citations are retained; the specification's replacement omitted them,
and dropping them would have deleted attribution the specification forbids changing.

## 31. Conclusion finding 3

> *orig:* At a turbine capital cost of €600/kW no tested market reaches full peaker-capital recovery across the assumed scarcity margins, about 9 per cent capacity-weighted in 2050 at the central margin and 4.4 to 17.4 per cent across the range, so a standing payment of €31 to 63/kW-yr closes the gap.
> *rev:* At a hydrogen-ready turbine capital cost of €600/kW, no tested market reaches full peaker-capital recovery across the assumed scarcity margins. Capacity-weighted recovery is about 9 per cent at the central 2050 margin and ranges from 4.4 to 17.4 per cent across the tested margins. A standing payment of €31–63/kW-yr closes the modelled gap.

## 32. Conclusion finding 4

> *orig:* (4) Policy ambition sets the emissions outcome, the four scenarios reaching 352, 231, 10 and 123 MtCO2 by 2050 from a 2025 baseline of about 644 MtCO2, a spread the fossil-phaseout lever leads.
> *rev:* (4) Policy ambition sets the emissions outcome. From a 2025 baseline of about 644 MtCO2, 2050 operational emissions reach 352 MtCO2 under Current Policies, 231 under Stated Policies, 10 under Net Zero and 123 under H2 Push. The differences are driven principally by the fossil-phaseout lever.

## 33. Policy implications

> *orig:* Article 22(4) of the Electricity Regulation supplies no vehicle, so selection rests on that premium.
> *rev:* At the assumed gas-turbine emissions intensity, the Article 22(4) threshold does not distinguish the two technologies; selection therefore requires a more restrictive emissions condition or an equivalent premium.

> *orig:* (4) A national scope-1 target is not reachable on price alone everywhere, so the four markets where the cap binds at 2050, and three more that bind earlier, need a complementary instrument.
> *rev:* (4) Within the model, the national scope-1 target is not reached through the price signal alone in every country, so the four markets where the cap binds at 2050, and three more that bind earlier, need a complementary instrument.

## 34. Limitations

> *orig:* Seven limitations bound these results, each with its direction in Supplementary Section S2.9. The largest is the weather construction of Section 2, which bounds the power-sector half. The 278 GW fleet, the 139 full-load hours, the €357 bn shortfall and the zero row of Table 2 rest on it
> *rev:* Seven limitations and their expected directions are detailed in Supplementary Section S2.9. The largest is the weather construction described in Section 2, which conditions the power-sector results. The 278 GW fleet, the 139 full-load hours, the €357 bn shortfall and the finding that no power-sector peaker reaches full capital recovery in Table 2 rest on it

## 35. Data availability, grammar only

> *orig:* Large third-party inputs are retrieved by the included download scripts for Hotmaps, Eurostat and GISCO. Two are not. The UK ONS TS044 accommodation-type table is a manual one-time download, and it is committed to the repository, and the EUBUCCO v0.2 building footprints that drive the bottom-up demand basis are fetched from the EUBUCCO object store by the per-country build scripts.
> *rev:* Large third-party inputs for Hotmaps, Eurostat and GISCO are retrieved by the included download scripts. Two inputs require separate handling: the UK ONS TS044 accommodation-type table is a one-time manual download committed to the repository, whereas the EUBUCCO v0.2 building footprints are fetched from the EUBUCCO object store by the per-country build scripts.

No repository claim was inspected or verified; only the sentence structure changed.

---

# Final prose pass

## Banned metaphors removed

| Phrase | Where | Replacement |
|---|---|---|
| "spine" (×2) | Results opening | "the demand, technology-mix and emissions results used by the subsequent tests" |
| "the dispatchable tip" / "the rungs below it" | §3.3 | "the marginal dispatchable units … the technologies below them in the merit order" |
| "the same molecule" | §3.4 | "Hydrogen" |
| "does not bite" | §3.4 | "does not bind for a 2050 build under the model assumptions" |
| "the direction survives" | §3.4 | "Recovery remains below 100 per cent" |
| "ambition is cheap" | §3.5 | "under this formulation" |
| "closes the seven" | §3.2 | "and the second is the most consequential" |
| "what remains of the gap" | §3.6 | removed with item 26 |
| "which closes all seven" | Conclusion | split into the two blue-hydrogen constructions (item 30) |

## Additional sentence splits and label additions

> *orig:* Three caveats bear on the base-load case, the second of which closes the seven on its own.
> *rev:* Three caveats bear on the base-load case, and the second is the most consequential.

This also removes an over-claim: only the uniform-price blue-hydrogen construction removes
all seven, and the ratio construction leaves Denmark, which is the distinction item 30
exists to protect.

## Typography

**En dashes for bare numeric ranges** (23 sites). The specification's own supplied text
draws the distinction — "€31–63/kW-yr" for a bare range, "ranges from 4.4% to 17.4%" after
"from" — and V6 used "to" throughout. Every bare range now takes an en dash; every
"from X to Y", "rises from X to Y" and "the count ranges from X to Y" construction keeps
"to", where it is correct English. Converted: €50–100/MWh-heat, €31–63/kW-yr (×2),
€51–66/kW-yr (×2), €1.0–1.3/MWh, €11.2–14.5/MWh, €8.9–11.5/MWh, €249–506 bn,
€215–307/MWh, €41–52/kW-yr, €520–540/kW, €122.4–131.1/MWh, €30–120/MWh (×2),
€168–184/MWh-e, €72–89/MWh-e, €30–57/MWh-e, €135–236/MWh-heat, €62–90/MWh-heat,
10–352 MtCO2, 0.3–12 TWh/yr, 1.80–2.84, 3,367–3,589 TWh, 30–55 per cent, 1991–2020,
97.5–100.1, 2.8–4.1, 12–18 per cent, 4.4–17.4 per cent, 248.0–265.6 GW. The graphical
abstract's capacity-payment band was changed to the same convention so the figure and the
sentence quoting it are punctuated alike.

**H2 Push** given a non-breaking tie at the two sites that lacked one (Methods scenario
definitions, Table 2 header), so all 20 occurrences now match.

**Percent convention** left as V6 had it and verified internally consistent: the symbol in
the abstract, the nomenclature and table cells; "per cent" spelled out in running prose.
The specification's supplied replacements used "%"; rendering them that way would have
made the body the only mixed part of the document, so the existing convention was kept.
Say the word and it can be swept to "%" throughout, body and SI together.

**H2 and CO2** verified consistent: the molecule is always subscripted (H$_2$, CO$_2$,
tCO$_2$, MtCO$_2$, gCO$_2$, kgCO$_2$); "H2 Push" is a scenario name and takes no
subscript, as in V6.

**Unit distinctions preserved**: €/MWh (62), €/MWh-e (15), €/MWh-heat (8), €/kW (9),
€/kW-yr (8), €/kg (3), €/tCO2 (7). No conversion between them.
