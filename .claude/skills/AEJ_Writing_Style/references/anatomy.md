# Section-by-section anatomy

How an Applied Energy paper is actually put together, from reading all 14 in the corpus.
Use this when deciding what a section should contain and in what order. For sentence
frames, use `phrasebank.md`.

## Contents

1. Title
2. Highlights
3. Abstract
4. Introduction
5. Literature review
6. Methods
7. Equations
8. Results
9. Sensitivity analysis
10. Discussion
11. Conclusion
12. Section headings, throughout
13. Numbers and units, throughout

---

## 1. Title

The dominant form is **[what was done] of [what], for [where or which case]**, with the
method named. Titles are informative rather than clever, and several state the case study
explicitly after a colon.

Corpus titles:

> Techno-economics of renewable hydrogen export: A case study for Australia-Japan
> Comparative techno-economic analysis of large-scale underground hydrogen storage
> Smart power-to-gas deployment strategies informed by spatially explicit cost and value models
> Modeling Germany's hydrogen future: Insights into spatial distribution
> A spatially explicit techno-economic framework for assessing co-located [systems]
> Long-term climate vulnerability of green ammonia economics
> Global techno-economic assessment of hybrid offshore wind, wave, and [solar]

Recurring openers: *Techno-economic(s) of*, *Comparative techno-economic analysis of*,
*A spatially explicit framework for*, *Global assessment of*, *Modeling X's Y future*.

None poses a question. None uses a rhetorical contrast.

## 2. Highlights

Telegraphic, verb-first, articles dropped, numbers in parentheses. Typically one or two
on what was built, three or four on what was found.

> Proposed a solar-assisted medium–deep geothermal seasonal storage framework.
> Revealed long-term thermal accumulation and stabilization after 5 years.
> Developed a regression-based model (R2 = 0.98) for rapid performance prediction.
> Identified optimal drilling depth (1375–1560 m) and flow rate (6.7–9.5 kg/s).
> Confirmed solar charging cuts heating cost by 26% and shortens payback period.

> Propose new heat-power decoupling method of molten salt coupled steam accumulator.
> New method can realize the full storage of sensible and latent heat of steam.
> Investigate operational state of the heat-power decoupling system on a typical day.

> Two-fold LCOA differential ($601–$1203/ton) driven by solar–wind complementarity.
> Subpolar zones gain 5.5% production via westerly wind intensification.
> Water stress surges +145% in Australia but improves 92% in Chile under RCP 8.5.

Leading verbs seen: *Proposed, Developed, Revealed, Identified, Confirmed, Investigated,
Incorporated, Established, Analyzed, Compared*.

A full grammatical sentence with a prepositional opener reads as the wrong register here.

## 3. Abstract

Five moves, in order, roughly 230 to 330 words.

1. **Context**, one or two sentences, plain.
2. **Gap**, hinged on *yet*, *however*, *owing to*, or *neglect*.
3. **What this study does**, study or authors as subject, aims often enumerated (i),
   (ii), (iii).
4. **Findings**, each with its number in parentheses, in reporting order.
5. **Qualifier or implication**, usually opening *However*.

Worked example, with the moves marked:

> [1] Green hydrogen allows coupling renewable electricity to hard-to-decarbonize
> sectors, such as long-distance transport and carbon-intensive industries, in order to
> achieve net zero emissions. [2] Evaluating the cost and value of power-to-gas is a
> major challenge, owing to the spatial distribution and temporal variability of
> renewable electricity, CO2 and energy demand. [3] Here, we propose a method, based on
> geographic information system (GIS) and techno-economic modeling, to: (i) compare the
> levelized cost and levelized value of power-to-gas across locations; (ii) identify
> potential hotspots for their future implementation in Switzerland; and (iii) set cost
> improvement targets as well as smart deployment strategies. Our method accounts for the
> spatial and temporal availability of renewable electricity and CO2 sources, as well as
> the presence of gas infrastructure, heating networks, oxygen and gas demand centers.
> [4] We find that only green hydrogen plants connected directly to run-of-river
> hydropower plants are currently profitable in Switzerland (with NPV per CAPEX ranging
> between 2.3-5.6). [5] However, considering technological progress by 2050, a few green
> hydrogen plants deployed in the demand centers and powered by rooftop PV electricity
> will also become economically attractive.

## 4. Introduction

A funnel, four to eight paragraphs, ending in a contribution statement and often a
roadmap.

**Paragraph 1: global stakes.** Climate, energy security or resource depletion. Every
sentence cited. Ends by naming the sector or technology.

**Paragraph 2: the technology's expected role, with market numbers.** Installed capacity
today, projections, targets. Every figure cited.

> The current global installed capacity of offshore wind is approximately 83 GW, with an
> additional 48 GW under construction. … Under high-ambition scenarios, the installed
> capacity of offshore wind is projected to increase to 500–1,600 GW by 2030, and 2000
> GW by 2050 [1]. Reaching these targets would imply yearly installations of
> approximately 100 GW, which raises concerns about whether global supply chains can meet
> the requirements [9].

Note the last sentence: a **derived implication** from the cited numbers, which is how
the paper earns the right to its question.

**Paragraph 3: definitions.** New or contested terms are defined explicitly and
contrasted with what they are not.

> Co-located or hybrid offshore energy parks refer to integrated systems where two or
> more renewable technologies are deployed within a shared offshore area and connected to
> common infrastructure, such as export cables, substations, and shared maintenance
> logistics. This contrasts with traditional single-source parks that operate
> independently.

**Paragraph 4 onward: what is known, claim by cited claim.** See §5.

**Final paragraphs: the gap, the contribution, the roadmap.**

## 5. Literature review

Whether it is its own section or the back half of the introduction, the texture is the
same and it is the part most unlike a working paper: **every claim about prior work
carries a number.**

> A recent detailed case study investigated the effects of installing OFPV between the
> unused marine space in between existing wind turbines, and found that the coefficient
> of variation (CoV) decreased by 20.8%, in addition to the increased energy density.

> A study of the Dutch part of the North Sea showed that the energy density could be
> increased by roughly 22% [15] when co-locating wave power, wind power and OFPV.

> At the system level, co-locating offshore wind and floating PV can reduce the power
> variability by 63% [19].

> [16] focused specifically on hydrogen demand in the German industrial sector estimating
> a range from 197 TWh to 298 TWh, primarily for methanol, steel, and ammonia production.

> Their results show that the technical and economic benefits increase with the nominal
> capacity of the PtG plant and that higher capacity factors (by ≈11%) are needed for PEM
> electrolyzers due to its higher CAPEX compared to AEL electrolyzers.

Characterising the literature qualitatively, without numbers, reads as evasive here. If a
prior study's headline figure is known, quote it.

The review closes on the gap, marked with *Despite*, *However*, or *Nonetheless*.

## 6. Methods

**Sections are named for their contents, not "Methodology".** The corpus has *Study
regions and meteorological data*, *Nominated offshore wind locations*, *UHS cost
calculation model*, *Economic calculations*, *System modeling*, *Assumptions and cost
estimation*.

**Data sources are named with their acronym and citation**, then described with counts.

> The Photovoltaic Geographical Information System (PVGIS) database was used to access
> the hourly time-series data which combines satellite-based estimates of the irradiance
> with reanalysis data to produce validated renewable resource estimates [30]. … All the
> datasets have 166,536 hourly time series spanning over 19 years (2005–2023) and offer
> statistically sound characterization of interannual variability.

**Tables are narrated in prose, not merely pointed at.** This is a substantial habit. The
paper says "Table 1 is a summary of …" and then walks through the values in sentences:

> The solar resource data shows the expected latitudinal and climatic gradients. The Al
> Wusta, Oman has the highest GHI of 2345 kWh/m2/year, the typical feature of BWh hot
> desert climate with low cloud cover. Pilbara, Australia has shown similar solar
> resources (2244 kWh/m2/year) even though it is located at the southern hemisphere. …
> The Magallanes, Chile has much lower solar availability (1100 kWh/m2/year) because it
> is located at high latitudes (53.2°S) and there is continuous cloud cover.

**Every modelling choice is justified where it is made**, including choices not to do
something:

> Technology learning curves are disabled to isolate climate-induced effects.
> A project lifetime of 25 years and a real discount rate of 8% are used which lies
> within the range commonly adopted in offshore renewable energy techno-economic
> assessments, typically 5–10%.
> To make the results relevant immediately, it is assumed that electricity generated
> offshore is brought onshore to an electrolyser station.
> While other scenarios were tested to analyze the change in supply dynamics, the results
> are not further included in the discussion.
> During the development of this study, the WKN had not yet been published, which is the
> reason it is not included in the scenario assumptions.

**Out-of-scope work is acknowledged and pointed at**, rather than ignored:

> It is worth noting that pinpointing the optimal offshore location, although not the
> focus of this study, necessitates a thorough evaluation of weather patterns, water
> depth and wave heights, given their critical impact [69]. It is suggested that the
> methodology proposed by Eriksson et al. [70] provides a way to incorporate risk factors
> owing to extreme weather into an optimisation study.

## 7. Equations

Introduced by a purpose clause, then the equation, then every symbol defined in a
`where` sentence closed with *respectively*.

> To incorporate the impact of height and surface roughness on wind speed at the
> turbine's hub height, Eq. (1) is applied [72]:
>
> where, v_cut−in, v_rated and v_cut−out are the cut-in speed (below which the turbine
> generates no power), rated speed (at which generated power reaches its rated value),
> and cut-out speed (above which the turbine's blades stop rotating), respectively.

Note that each symbol's gloss carries a parenthetical explanation of its physical
meaning, not just its name.

Also standard: *This aggregation is mathematically expressed in Eq. (1), where the result
reflects …*, and *the following equations are proposed by [80]*.

## 8. Results

**Subsection titles are noun phrases naming content**: *Capacity factors*, *Optimization
results*, *Statistical analysis of driving factors*, *Economic analysis under basic
operating conditions*. Never a claim.

**Each subsection opens on its figure.**

> Fig. 5 presents the average capacity factors for all locations globally.

**Validation against external sources comes immediately**, before interpretation.

> The wind power capacity factors show good agreement with overlapping reported locations
> in the Global Wind Atlas [75].

**Anomalies are stated, attributed, and defended.** This is a signature move and it
inoculates against a referee finding it first.

> The PV capacity factors are lower than commonly reported global values [76]. This
> discrepancy is primarily due to the assumption of horizontal panel orientation without
> tilt-angle optimization, which is expected to underestimate PV capacity factors relative
> to optimally tilted systems but avoids overestimating performance given the uncertain
> impact of wave-induced motions on OFPV systems [34].

**Operational definitions are given where the analysis needs them**, not left to methods.

> In the following analysis, "all locations" refers to the full set of feasible offshore
> sites (n = 22,713), while "co-located" or "mixed" refers to the subset of locations
> where the cost-optimal solution includes two or more technologies with nonzero capacity
> shares.

**Findings inside a paragraph are enumerated.**

> The distributions of LCOE, shown in Fig. 8(a), reveal two main findings. First, as
> expected, LCOE values based on near-future assumptions are generally lower than those
> based on present-day assumptions. … Second, the LCOE distributions across all locations
> are consistently lower than those for locations where a mixed technology portfolio is
> preferred.

**Statistical claims are backed with the test and the p-value.**

> This difference is statistically significant. Mann-Whitney U-tests indicate that for
> both present-day and near-future assumptions, the LCOE distributions for all locations
> are lower than those for mixed locations for the corresponding scenario (p<0.005).

**Paragraphs close on interpretation**, marked: *These results indicate that…*, *This
indicates that…*, *as evidenced by…*

## 9. Sensitivity analysis

Method stated first in full, then what was varied and by how much, then what moved most
and why.

> Fig. 9 shows a sensitivity analysis for several parameters. The sensitivity analysis has
> been performed by both increasing and decreasing the CapEx for one technology (wind
> power, wave power, OFPV, grid connection costs) by 25% and running the optimization
> again while maintaining the CapEx of the other variables constant. These variations can
> be interpreted as representing uncertainty in future cost development, including
> conservative and optimistic learning pathways for emerging technologies. This results in
> eight sensitivity cases for both the present-day and the near-future scenario.

Then the mechanism behind the largest mover is explained, not just reported:

> For the present-day scenario, the largest change is seen in the capacity factor of OFPV
> in locations where a mix is preferred, when increasing wind power CapEx by 25%. The
> explanation for this change lies in the fact that with the CapEx increase, the number of
> locations where a mix is preferred decreases. With the CapEx increase, locations
> initially cost-optimal for PV–wind installations are now cost-optimal for PV-only
> installations, and therefore fewer locations with high solar resources are included in
> the subset of mixed locations.

## 10. Discussion

The commonest architecture: **restate what the study did, announce N drivers, then take
them First / Second / Third.**

> This study provides a foundational techno-economic framework for natural hydrogen, using
> the Bourakébougou field as an illustrative best-case scenario to evaluate its commercial
> potential. The analysis highlights three primary drivers that shape its viability:
> production scale, policy support, and transportation logistics.
>
> **First**, the study confirms that economies of scale are the most powerful lever for
> cost reduction. The base scenario presents a small-scale production from field test
> results, which led to 15,000 m3/day (approximately 56 kg/hour or 1.3 tons/day) across
> ten vertical wells, resulting in an LCOH of $6.82 per kilogram. **Importantly**, scaling
> production capacity by a factor of six to 336 kg/hour (8 tons/day) reduces the LCOH by
> more than 60%. This result emphasizes the nonlinear nature of hydrogen cost formation,
> where capital-intensive components are rapidly diluted as throughput increases. **Hence
> achieving commercial scale is critical for competitiveness.**

Each driver paragraph runs: topic claim → base numbers → the key comparison flagged with
*Importantly* → interpretation → a one-line takeaway.

The discussion also carries the **deny-then-supply** correction:

> **However, these results should not be interpreted as** policy-driven viability.
> **Rather, they indicate that** policy support can accelerate deployment for projects
> that are already near-commercial, while long-term competitiveness remains fundamentally
> governed by production scale, reservoir performance, and infrastructure access.

And explicit comparison with named prior work:

> Comparable observations were also reported by Huang et al. [36], who analyzed the
> contribution of multiple parameters to threshold inlet temperatures. While their
> optimization target, which is threshold temperature, differed from ours, both studies
> highlight the dominant role of borehole depth and flow rate.

## 11. Conclusion

Three parts, in order.

**Restate what the study did**, with the study as grammatical subject. Eleven of fourteen
do this.

> This study presents a spatially and temporally-explicit techno-economic analysis of
> green hydrogen and synthetic methane plants throughout the energy transition. First, we
> develop a detailed GIS assessment method to map various electricity and CO2 supply
> sources, as well as demand centers across the country. This data is then used as an
> input to the techno-economic model.

**List the findings**, numbered or bulleted, each carrying its number.

> The main conclusions are as follows: (1) Thermal losses primarily occur between the
> inner and outer coaxial pipes, especially at shallow depths. … (2) A thermal
> accumulation effect emerges over long-term operation, with the system reaching dynamic
> thermal equilibrium after about 5 years.

**Point at future work**, often in the section title itself (*Conclusions and outlook*,
*Conclusion and future work*).

> Future research should extend the present fixed benchmark configuration toward spatially
> optimized hybrid designs. In particular, the wave component could be optimized regionally
> by adjusting the size.

## 12. Section headings, throughout

**Noun phrases naming content. Never a claim.**

Corpus headings: *Introduction · Study regions and meteorological data · UHS cost
calculation model · Economic calculations · Techno-economic modelling · Offshore wind ·
Results · Capacity factors · Optimization results · Statistical analysis of driving
factors · Economic analysis under basic operating conditions · Sensitivity analysis ·
Discussion and policy comparison · Further enhancement · Conclusions and outlook*

A heading like *On levelised cost, hydrogen holds base load in seven markets* states a
finding, which belongs in the text. The Applied Energy equivalent is *Levelised cost of
heat*.

## 13. Numbers and units, throughout

**The same quantity is often given in more than one unit**, so no reader has to convert.

> 15,000 m3/day (approximately 56 kg/hour or 1.3 tons/day)
> less than 6 tons/day (250 kg/hour)
> £60/kW-yr, roughly €70/kW-yr at 2024 rates

**Ranges are given rather than point values** wherever the model produced one, with the
driver attached.

> a 2-fold LCOA differential ($601–$1203/ton) driven by solar-wind resource quality
> optimal drilling depth (1375–1560 m) and flow rate (6.7–9.5 kg/s)
> between 9.09 and 12.73 Mton … depending on the stringency of the transition pathway

**Percentages carry their base.**

> 95.7 % (15.5 % for drilling, 65.8 % for mining, and 14.4 % for lining)
> 34% attributed to PV CAPEX, followed by 16.7% and 13.6% from LNH3 storage units and PEM,
> respectively

**Uncertainty in projections is flagged in its own sentence** rather than hedged into the
claim.

> It is worth noting that projections of future levels of installed capacities are highly
> uncertain and depend on factors such as market development and policy incentives.
