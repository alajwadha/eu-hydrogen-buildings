# The buildings and heat domain, and where this corpus stops

## Read this section before trusting anything below it

The fourteen-paper corpus contains **no paper about heating the building stock**. That is
the single most important limit on this skill when it is applied to a dwelling-heat
manuscript.

Measured over the whole corpus body text:

| Term | Uses |
|---|---|
| `dwelling` | 0 |
| `building stock` | 0 |
| `heating degree` | 0 |
| `thermal envelope` | 0 |
| `radiator` | 0 |
| `space heating` | 1 |
| `residential` | 5 |
| `household` | 7 |
| `heat pump` | 54, but almost all in reference titles or as a component of an industrial system |
| `district heating` | 26 |
| `boiler` | 35 |
| `COP` | 35 |
| `retrofit` | 17 |

Terms specific to a NUTS3-resolution European buildings study fare worse still: `NUTS` 0,
`peaker` 0, `capacity payment` 0.

Attempts to widen the corpus with published buildings-heat articles were blocked. The egress
proxy denied `discovery.ucl.ac.uk` (an Applied Energy accepted manuscript on Dutch
residential building stock, *Applied Energy* 306 (2022) 118060), `arxiv.org`, and
`sciencedirect.com`, so no additional full text could be read. This section therefore rests
on the heat-side prose that is genuinely inside the corpus, which is real and useful but
narrower than a buildings paper needs.

**Where the evidence is second-hand it is marked as such.** Treat marked items as leads to
verify, not as corpus findings.

## What the corpus does support

Two of the fourteen are heat papers in the thermal-system sense, and they carry the
journal's heat vocabulary directly.

**AE8**, solar-assisted seasonal thermal energy storage in medium-deep boreholes for
district heating. **AE9**, molten salt coupled steam accumulator for heat-power decoupling.
**AE3** maps power-to-gas across Switzerland and touches district heat networks; **AE6**
models German hydrogen and touches low-temperature heat in buildings.

### The opening funnel, in the heat register

AE8's introduction is the closest thing in the corpus to the opening a buildings-heat paper
needs, and it can be used as a direct model:

> In the context of increasingly severe global climate change, deep decarbonization of
> energy systems has become a core strategy for countries committed to cutting greenhouse-gas
> emissions. The Paris Agreement sets the target of limiting global temperature rise to well
> below 2 °C above pre-industrial levels [1], which has prompted numerous countries and
> regions, including the European Union, the United States, and China, to establish visions
> for achieving net-zero carbon emissions by around 2050 [2–4]. In this global push, **space
> heating and cooling in buildings has been widely recognized as a key sector for carbon
> mitigation, particularly in cold and temperate regions in which heating accounts for more
> than 50% of total building energy consumption in these areas** [5,6], **with the majority of
> heat still supplied by fossil fuels such as coal and natural gas** [7].

Note the shape: global, treaty, then the sector arrives with a cited share and the incumbent
fuel named. Three sentences, seven citations. A European buildings paper substitutes the EU
share of final energy for the 50 % figure and substitutes natural gas for coal, and the
paragraph works unchanged.

### The one-sentence gap statement, fused to sentence one

AE8's abstract opens with capability and gap in a single sentence:

> Solar-assisted seasonal thermal energy storage (SSTES) in medium-deep boreholes **can
> decarbonize district heating, yet its long-term techno-economics remain unclear.**

`X can do Y, yet its Z remains unclear` is the tightest gap frame in the corpus and it is
already in the heat register.

### Heat quantities, as the journal words them

| Quantity | Corpus wording |
|---|---|
| Cost of delivered heat | **`levelized cost of heat (LCOH)`**, defined as *the average cost per unit of useful energy delivered over the system's lifecycle* |
| Payback | `simple pay-back period (PBP)`, reported in years to 1 dp |
| Seasonal split | `heating season` and `non-heating season`, both used as bare nouns |
| Demand | `heating demand`, `annual heating demand`, `thermal demand`, `heat demand` all attested |
| Delivery | `heat supply`, `heat supply potential` |
| Performance | `heat extraction capacity`, `heat storage proportion`, `utilization efficiency` |
| Temperature | `outlet temperature`, `supply temperature`, `subsurface temperature` |

Attested sentences worth copying wholesale:

> To gauge the economic performance of the solar-assisted medium-deep geothermal STES, two
> indicators are used: the levelized cost of heat (LCOH) and the simple pay-back period (PBP).

> As shown in Table 8, **under the same annual heating demand**, the optimized system adopts a
> shallow geothermal source combined with a seasonal thermal storage strategy.

> Compared to a system without solar assistance, the optimized design achieves a **26.3%
> reduction in Levelized Cost of Heat (LCOH)** and shortens the payback period from 9.9 to 7.4
> years.

> Oversized flow rates may enhance heat extraction capacity but significantly increase pumping
> energy consumption, while undersized flow rates **may fail to meet heating demand**, leading
> to suboptimal performance.

The last one is the sanctioned way to say a heating system does not deliver: *may fail to
meet heating demand*, with the mechanism on both sides of the trade-off in the same sentence.

### One useful attested sentence on the electrification-versus-hydrogen boundary

AE6, explaining why a modelled outcome differs:

> This difference can be explained by **the inability to utilize electrolyzer waste heat for
> low-temperature heating in industry and buildings**.

That is the corpus's own phrasing for the low-temperature heat end use, and `low-temperature
heating in industry and buildings` is worth adopting verbatim.

### Captions in the heat register

AE8's fifteen figure captions are all short noun phrases, mostly under twelve words, and
they name the physical quantity rather than the finding:

> Fig. 5. Comparison between simulated and measured outlet temperature.
> Fig. 8. Soil temperature evolution after seasonal charging cycles (Year 1–10).
> Fig. 12. Evolution of annual thermal storage and extraction performance over 11 operational years.
> Fig. 14. Pareto front of LCOH and PBP for the optimized STES system.
> Table 4 Validation results of outlet temperature and heat extraction rate.
> Table 5 Economic parameters used in LCOH and PBP analysis.

AE3, which is the closest analogue to a spatially explicit European study, captions its maps
the same way, naming the selection rule rather than the result:

> Fig. 6. Top 20 hotspots (located at RoR hydropower plants) for deployment of green hydrogen
> plants across Switzerland on the basis of highest NPV per unit of CAPEX.
> Fig. 10. Roadmap for green hydrogen (PtH) and synthetic methane (PtM) plants deployment
> across different locations in Switzerland based on our results.

A choropleth of regional heat costs takes a caption of the same shape: what is mapped, over
what geography, on what basis.

## What the corpus does not support, and what to do about it

**No attested wording exists here for**: dwellings and the dwelling stock, archetypes,
occupancy, retrofit depth or retrofit rate, building age bands, heating degree days, the
thermal envelope, gas grid conversion or decommissioning, the boiler replacement cycle, or
consumer bills. The skill cannot tell you how this journal words those, because in these
fourteen papers it never does.

**Practical rule.** For every term in that list, either

1. use the term as the technical literature already uses it and define it on first use, which
   is the corpus's own habit for anything unfamiliar, or
2. reduce it to a quantity the corpus does word, since most of them can be. Retrofit depth
   becomes a stated change in specific heat demand in kWh/m²/yr. Archetypes become
   *representative building types*, close to AE8's *a single building type*. Heating degree
   days become *annual heating demand*, which is attested.

Option 2 is safer, because a quantity with a unit is always in this journal's register and a
sector term of art may not be.

**Second-hand leads, to verify before use.** These came from search result snippets rather
than from read full text, so they are provenance-marked and not corpus findings:

- *Applied Energy* 306 (2022) 118060, on Dutch residential building stock, reportedly
  contains *natural gas boilers are almost phased out by 2050 and the heat supply for space
  heating is dominated by heat networks and electric heat pumps*. Blocked host, unverified.
- A figure of roughly *31 % of total European energy demand* for residential space heating and
  hot water is attributed to a climate-impact study of decentralised heat pump and gas boiler
  mixes. Blocked host, unverified, and the base of the percentage is not established.

Neither should be cited from here. They are listed so that a later session with network
access knows exactly which two documents would close this gap.

## How to close this gap properly

Three or four full texts would do it: an *Applied Energy* paper on national or European
building-heat decarbonisation, one on heat pump versus hydrogen or gas comparison, one
spatially explicit heat demand mapping paper, and one dwelling-stock model. Extract them with
plain `pdftotext` into `paper/style_corpus/flow/`, not `pdftotext -layout`, since layout mode
interleaves the two columns and destroys reading order. Then re-run the same extractions used
here and replace this section's caveats with counts.
