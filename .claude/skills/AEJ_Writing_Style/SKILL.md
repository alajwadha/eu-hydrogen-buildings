---
name: AEJ_Writing_Style
description: Rewrite a techno-economic energy manuscript in Applied Energy's house voice, matching how published AE authors word things, deliver findings, signpost structure and phrase captions. Built by reading 14 published AE articles end to end, with their sentences quoted throughout. Use this whenever someone is preparing, revising or restyling a paper for Applied Energy or a comparable Elsevier energy journal (Energy, Energy Conversion and Management, International Journal of Hydrogen Energy), and especially when a draft is described as reading like a working paper, a report, an economics paper or a thesis chapter rather than a journal article. Trigger it for "make this sound like Applied Energy", "the writing style is off", "this reads like a report", "our captions are too long", "match the journal's voice", and for any question about wording, phrasing, how findings are delivered, section openings, figure captions or abstract structure in an energy manuscript.
---

# Applied Energy house voice

Read from 14 published Applied Energy techno-economic articles. Every quoted line is
theirs. `references/phrasebank.md` holds the full collection organised by the job each
sentence does; open it while writing rather than reading it once.

## Before anything else: what may be copied and what may not

Every quoted sentence in this skill belongs to a published author. The purpose of quoting
them is to expose a **pattern**, and the pattern is what transfers. The sentence itself
does not.

**Copy the frame. Never the content.** A frame is the grammatical skeleton plus the
fixed connective words that make a construction recognisable in the field. `This study
presents…`, `X is expected to play an important role in…`, `However, no study has…`,
`This difference is primarily attributable to…`, `Fig. 5 shows the…`. These are field
conventions, used by hundreds of authors, and are not anyone's property.

What is theirs is everything that fills the frame: their subject matter, their adjectives,
their explanatory clause, their way of describing their own result. Lifting a clause of
theirs and swapping the nouns is paraphrase, and paraphrase without citation is
plagiarism whether or not a plagiarism checker catches it.

**The working test.** After writing a sentence built on a corpus frame, cover the frame
and read what remains. If the remainder still says something specific about the corpus
author's system rather than about yours, it came from them and must be rewritten. If a
run of more than about eight consecutive words matches a corpus sentence and those words
are not a standard field term, rewrite it.

**Where the corpus author's idea is genuinely being used**, cite them. The skill's own
guidance on this is in the discussion sections: `Comparable observations were also
reported by Huang et al. [36]`. Naming them is the house habit anyway.

This applies with most force to `references/phrasebank.md`, which is 600 lines of other
people's sentences sorted by function. It is a pattern index, not a supply of text.

## Read the paragraph before you rewrite it

Three checks, in order, before touching anything.

**1. Does it need rewriting at all?** A paragraph that already states its claim first,
carries its numbers inside its sentences, signposts its qualification and cites what it
asserts is finished. Rewriting it to demonstrate effort makes the manuscript worse and
risks the numbers. Say so and move on:

> No substantial revision needed. The paragraph already opens on its claim, carries its
> figures inline and marks its qualification.

Changing prose is not free. Every edit is an opportunity to break a pinned number, drop a
load-bearing hedge, or introduce a claim the model does not support.

**2. Is the problem the wording or the argument?** If the claim is unsupported, the
reasoning has a gap, an assumption is doing undeclared work, or the paragraph repeats one
already made, **no amount of restyling fixes it.** House voice will make a weak argument
sound more confident, which is the worst outcome available. Stop and fix the argument.

For a quantitative manuscript, that is a different job with its own tooling: recompute the
number, trace it to the artefact that produces it, and check it survives. The
`manuscript-integrity` skill does that. Use it, rather than duplicating it here.

**3. Correctness outranks voice, always.** When house style and accuracy conflict,
accuracy wins and it is not close. A hedge that makes a sentence clumsy stays if removing
it would overclaim. A long sentence stays long if splitting it would separate a result
from its condition. The corpus is a guide to how this journal sounds, not a licence to
change what a paper claims.

## The one thing underneath everything else

An Applied Energy author writes as someone **reporting**. An essayist writes as someone
**arguing**. Same facts, different sentences, and a reader places the genre inside a
paragraph.

The reporter states a fact and attaches its citation. Announces the section before
writing it. Lets the figure be the subject of its own sentence. Justifies a modelling
choice in the sentence that makes it. Says *however* where there is a qualification.
Names the misreading before correcting it.

The essayist opens on an aphorism, withholds the point for effect, carries an argument
across three sentences without signposting, uses inversion and repetition for emphasis,
and trusts the reader to see the implication.

**If a sentence's force comes from how it is built rather than what it says, it is in
the wrong genre.** That single test catches most of what needs changing.

## The opening: a funnel, and all fourteen use it

Not one opens on the author's own observation. Every one opens on the state of the
world, cited, and narrows over four or five sentences.

The stages are consistent:

1. **Global stakes.** Climate, decarbonisation, energy security. Cited.
2. **A number that narrows the frame.** A share, a target, a projection. Cited.
3. **The technology enters**, usually with a "will matter" verb.
4. **The specific problem** this paper addresses.

> Energy-related carbon dioxide (CO2) emissions are responsible for the lion's share
> (73%) of global anthropogenic greenhouse gas (GHG) emissions [1]. Renewable energy
> (RE) technologies accompanied by energy efficiency are the main mitigation strategies
> to cut GHG emissions [2,3]. So far, RE has been mainly introduced in the power sector,
> where it is projected to contribute to 33% of the global electricity generation by
> 2025 [4]. **However**, the decarbonization of other hard-to-abate sectors, such as
> carbon-intensive industries and long-distance transport, still remains a key challenge
> [3]. Green hydrogen is **expected to play an important role** in complementing
> electrification to achieve net zero goals [5,6].

Five sentences, six citations, three statistics, and the paper has arrived.

The "will matter" verb is near-formulaic: *is expected to play an important role*, *is
poised to play a pivotal role*, *will most likely hold a key role*, *holds a prominent
position among*, *is expected to play a central role in*.

**Statistics are dense and always cited.** *73%*, *33% by 2025*, *69.95% and 48% in
2023, respectively*, *more than 50% of total building energy consumption*. An
introduction that argues without numbers reads as opinion here, however well grounded.

## The gap, stated outright

Applied Energy uses the word *gap*, without embarrassment, and says exactly what prior
work failed to do. An essayistic draft implies the gap through contrast and expects the
reader to infer it.

> **Nonetheless, a critical methodological limitation pervades this existing
> literature:** the ubiquitous reliance on static, historical meteorological data and
> deterministic cost models [18]. **By assuming** climate stationarity, these assessments
> **fundamentally neglect** the dynamic, multi-decadal interaction between anthropogenic
> climate change and shifting renewable energy resource availability [19].

> **However, these studies did not assess** the proximity of hydrogen production sites to
> various demand centers … which **remain a research gap**.

> **A clear gap exists in understanding whether** co-location of offshore wind, wave, and
> OFPV can systematically reduce costs on a global scale.

> **While numerous studies analyze** individual aspects of hydrogen strategies, **there
> remains a gap in** quantitative analyses addressing holistic long-term strategies.

Then the contribution, equally direct:

> **Against this background, our study fills this research gap** in the literature and
> expands the existing knowledge by developing a novel spatially explicit model.

> **Given these considerations, this study aims to bridge the critical knowledge gap in**
> the valuation of the economic feasibility of natural hydrogen production.

> **The contribution of this study, which distinguishes it from existing literature, lies
> in** its incorporation of the following elements: …

> **The main contributions are summarized as follows:** …

Several then close the introduction with a **roadmap paragraph**, which essayistic drafts
omit as clumsy:

> This paper is divided into seven sections. Section 2 briefly lists the nominated
> offshore wind locations. In Section 3, techno-economic modelling is presented …

## The paragraph

Regular enough to use as a template.

1. **First sentence names the topic**, plain subject-verb-object.
2. **Middle sentences elaborate**, each carrying a citation, chained with trailing
   participles.
3. **Last sentence qualifies**, flagged with *However* or *It is important to note that*.

> Chemically synthesised ammonia (NH3) has a long history of use as a fertiliser,
> **leading to** the development of infrastructures for its production, storage, and
> transportation at export scale [7]. MeOH is another attractive option **due to** its
> relatively high volumetric H2 density and gravimetric H2 content. Its liquid state
> under ambient conditions eliminates the need for additional transformation costs and
> reduces losses. **Moreover**, there are mature technologies for large-scale,
> long-distance transportation [6,8]. **However, it is important to note that** burning
> MeOH releases carbon, **necessitating** a carbon management process after cracking [8].

The caveat arrives **last and marked**. An essayist folds it into an earlier clause,
which reads as argument rather than report.

## The signature construction: the trailing participle

The most characteristic habit in the corpus, and the highest-leverage thing to adopt.
Where an essayist starts a new sentence for a consequence, Applied Energy hangs it off
the end with an *-ing* clause.

> …has a long history of use as a fertiliser, **leading to** the development of
> infrastructures …

> …burning MeOH releases carbon, **necessitating** a carbon management process …

> …generates economic benefits by lowering system costs, **highlighting** its value as an
> efficiency measure.

> …the resulting CSI ranges from 0 to 100, with higher values **indicating** more
> suitable locations.

> …enabling the comparison of potential sites over large coastal regions and
> **supporting** early-stage decision-making.

> Hydrogen holds a prominent position among energy carriers due to its high energy
> density [6], **making it** a strategic choice for the energy transition.

The verb pool: *leading to, resulting in, yielding, allowing, enabling, supporting,
highlighting, emphasizing, indicating, suggesting, reflecting, representing,
necessitating, providing, thereby reducing, contributing to, driven by, attributed to*.

It reads flat, and the flatness is the point: it subordinates the consequence to the
fact, which is what reporting does.

## How a numeric result is worded

The shape is consistent: **claim, number in parentheses or apposition, driver introduced
by *driven by* or *attributed to*, consequence in a trailing participle.**

> Under S1 and base case assumptions, the landed LCOH would be 11.3 AUD/kg, **with** 34%
> **attributed to** PV CAPEX, followed by 16.7% and 13.6% from LNH3 storage units and
> PEM, **respectively**.

> Baseline analysis reveals a 2-fold LCOA differential ($601–$1203/ton) **driven by**
> solar-wind resource quality and temporal complementarity.

> Internal heat exchange between coaxial pipes **is found to account for** up to 25% of
> radial heat loss in shallow sections, **emphasizing** the need for careful borehole
> configuration.

> The results indicate that rLPG could substitute between 9.09 and 12.73 Mton of
> conventional fossil fuels by 2050, **depending on** the stringency of the transition
> pathway.

The verbs that carry numbers: *account for, range from, reach, amount to, correspond to,
drop to, rise to, is estimated to, is found to, yields*.

**`respectively`** lets one sentence carry parallel results where a draft would spend
three. It is everywhere in this corpus and typically absent from working papers.

## The figure is the subject

> **Fig. 6 presents** the simulated temperature fields for a 2500 m-deep, solar-charged
> borehole at four depths.

> To ascertain the contribution of each component to the landed cost, **Fig. 11 depicts**
> a breakdown of final LCOH sorted in descending order.

> **As can be seen from** the CAPEX data, subsurface engineering costs predominantly
> influence capital expenditures.

> **Table 3 summarises** the assumptions involved in levelized costing.

A draft that states the finding and drops `(Fig. 6)` in parentheses is doing the same
job in the wrong voice.

## Justifying a choice where the choice is made

Applied Energy explains itself inline rather than deferring to a methods appendix.

> The "Unconstrained" scenario **serves as a benchmark, representing** a strategy where
> decisions are made without policy-imposed constraints. **This allows us to assess** the
> alignment between the cost-optimal strategy and current political objectives.

> Technology learning curves **are disabled to isolate** climate-induced effects.

> A project lifetime of 25 years and a real discount rate of 8% are used **which lies
> within the range commonly adopted** in offshore renewable energy assessments, typically
> 5–10%.

> **While** other scenarios were tested to analyze supply dynamics, **the results are not
> further included in the discussion.**

## Framing the status of a claim

Careful writers strip these as filler. Here they are genre markers.

> **It is clear that** the most cost-effective modality will depend on local
> circumstances.

> **It can thus be inferred that** subsurface engineering costs predominantly influence
> capital expenditures.

> **From these findings we can conclude that according to our model**, the optimal
> strategy consists of …

And the **deny-then-supply** move, which is worth having in hand:

> **However, these results should not be interpreted as** policy-driven viability.
> **Rather, they indicate that** policy support can accelerate deployment for projects
> that are already near-commercial.

An essayist writes only the correct reading and trusts the reader. Naming the misreading
first is both plainer and safer with referees.

## Engaging prior work by name

The discussion names authors and states agreement.

> **Comparable observations were also reported by Huang et al. [36]**, who analyzed the
> contribution of multiple parameters to threshold inlet temperatures. **While their**
> optimization target **differed from ours, both studies highlight** the dominant role of
> borehole depth and flow rate.

> **This aligns closely with the findings by Lux et al. [32]** and our own model results.

Discussing the literature as an undifferentiated body reads as evasive here.

When a cited number disagrees with yours, the corpus has exactly one form. The difference is
the subject, and a named modelling choice is the cause.

> **Musa et al. report a lower LCOH of USD$1.99/kg, a difference primarily attributable to
> the substantial economies of scale in their larger model.**

No adjective on their work, no defence of yours. `we attribute`, `at odds with` and
`disagree` appear zero times in fourteen papers. Full treatment in `references/stance.md` §6.

## Delivering a result the reader will not like

Across all fourteen papers there are eight sentences that state a result in negative
grammar. `not viable` 0, `least promising` 0, `economically unattractive` 0. This literature
almost never says a technology fails; it says one option costs more than another, and names
why.

> S4 achieves an energy efficiency of 52.70 %, **which is lower than** the 88–89 % efficiency
> of ABS [79] **but addresses the limitation of** ABS in storage duration.

> The heat storage proportion of the MS system **is only** 5.6 %, **which is much lower than
> that of** the 63.7 % of the MS-SA system.

> **Neither pathway** of H2P nor A2P **achieves lifecycle profitability.**

The last is the strongest negative statement in the corpus, and note what it does not have:
no *unfortunately*, no *fails to*, no *cannot*, no verdict adjective. It names a concrete
financial criterion and stops.

So a draft saying *hydrogen is not viable for building heat* should say that hydrogen
delivers heat at a higher cost in *N* of *M* regions, and give the mechanism. Same claim,
and the reader issues the verdict. `references/stance.md` §1.

## Policy implications: the corpus never recommends

`we recommend` appears **zero times** in fourteen papers written to inform decisions.
Instead the paper grants a capability and the reader is the agent.

> By disaggregating energy consumption at the sectoral, end-use, and regional levels,
> **policymakers can identify** critical areas for intervention.

> ... **enabling policymakers to evaluate** the trade-offs between ...

> The results **will assist policymakers in** formulating ...

The verbs are *enable*, *assist*, *support*, *provide*, *inform*. `should be` does appear, 53
times, but it instructs the reader how to read the paper or tells the next researcher what to
do, not a government what to fund. `references/stance.md` §2.

## Acknowledging a limitation

Acknowledge and recover in the same breath. Never leave the concession hanging.

> The primary barrier arises from the limited knowledge, confidentiality, and scarcity of
> publicly available data … **However, despite this constraint, the study effectively
> utilises existing data to generate robust, albeit approximate, models** to achieve its
> objectives.

> **While grounded in** a specific geological setting, **the methodology and insights
> extend more broadly to** natural hydrogen projects worldwide.

## The conclusion

Eleven of the fourteen open with the study as grammatical subject. It is a formula, and
using it costs nothing.

> **This study presents** a spatially and temporally-explicit techno-economic analysis of
> green hydrogen and synthetic methane plants throughout the energy transition. **First,
> we develop** a detailed GIS assessment method …

> **This study establishes** a life-cycle cost model for UHS based on key cost drivers …

> **The present study proposes** a new heat-power decoupling system featuring a molten
> salt coupled steam accumulator …

Then the findings, usually numbered or bulleted:

> **The main conclusions are as follows:** (1) Thermal losses primarily occur between the
> inner and outer coaxial pipes … (2) A thermal accumulation effect emerges over
> long-term operation, with the system reaching dynamic thermal equilibrium after about 5
> years.

Then future work, often in the section title itself: *Conclusions and outlook*,
*Conclusion and future work*.

Conclusions run **470 to 620 words**, and thirteen of the fourteen contain **no first person
at all**. Bodies do use *we*, sparingly; at the conclusion it disappears. Each numbered item
is self-contained and carries its own figures, because a reader who reads only the conclusion
is meant to leave with every headline number.

## Restating a number without rewording it

That last point has a consequence people get backwards. A headline figure appears in the
highlights, the abstract, the results, the discussion and the conclusion, and **the digits,
the unit, the case labels and the qualifying condition are held constant word for word.**

> *Abstract.* For a storage capacity of 10⁷ kg and one injection–withdrawal cycle per year,
> the LCOHS is $0.70/kg for SC, $0.76/kg for DGR, and $0.92/kg for LRC.
> *Results.* The final LCOHS for different scenarios **are shown with** the lowest cost for SC
> at $0.70/kg, DGR at $0.76/kg, and the highest for LRC at $0.92/kg.
> *Conclusion.* At a 10⁷ kg storage scale with one injection–withdrawal cycle per year, the
> LCOHS **is significantly lower for geological storage**: $0.70/kg in SC, $0.76/kg in DGR,
> and $0.92/kg in LRC.

Only the frame moves. The abstract states, the results locate and rank, the discussion sets
the number against an external benchmark, the conclusion judges. Rewording the quantity to
avoid looking repetitive is how a correct number turns into a wrong claim, usually by losing
its condition. `references/restatement.md`.

## Acronyms and adjectives

**Define once, then use relentlessly.** The prose becomes acronym-dense and that is
normal: *GH2, LH2, LNH3, MeOH, MCH, LOHC, LCOH, LCOA, PEM, WACC, vRES, CSI, CCF*.
Spelling a term out repeatedly reads as writing for a lay audience.

**Evaluative adjectives are permitted.** *Attractive*, *promising*, *significant*,
*crucial*, *well-established*, *highly suitable*. Technical writing guides ban these;
here their absence reads as oddly withholding. Use them where the paper genuinely
evaluates, not for emphasis.

## Section headings name content, never a claim

A quiet but pervasive difference. Applied Energy headings are noun phrases:

> Introduction · Study regions and meteorological data · UHS cost calculation model ·
> Economic calculations · Techno-economic modelling · Offshore wind · Results · Capacity
> factors · Optimization results · Statistical analysis of driving factors · Economic
> analysis under basic operating conditions · Sensitivity analysis · Discussion and policy
> comparison · Conclusions and outlook

A heading like *On levelised cost, hydrogen holds base load in seven markets* states a
finding. The journal's equivalent is *Levelised cost of heat*, with the finding in the
text where a reader can weigh it. Argumentative headings are one of the strongest signals
that a draft came from a report.

## The literature review is numeric

The part least like a working paper. Every claim about prior work carries that work's
number.

> A recent detailed case study investigated the effects of installing OFPV between the
> unused marine space in between existing wind turbines, and **found that the coefficient
> of variation (CoV) decreased by 20.8%**.

> A study of the Dutch part of the North Sea showed that the energy density could be
> **increased by roughly 22%** [15].

> At the system level, co-locating offshore wind and floating PV can **reduce the power
> variability by 63%** [19].

> [16] focused specifically on hydrogen demand in the German industrial sector estimating
> **a range from 197 TWh to 298 TWh**, primarily for methanol, steel, and ammonia
> production.

Characterising the literature qualitatively, as a body with a tendency, reads as evasive
here. If a prior study's headline figure is known, quote it.

## Methods: narrate the table, justify every choice

**Tables are walked through in prose, not merely pointed at.** A draft that writes "Table
1 gives the inputs" and stops is leaving out something the journal always does:

> The solar resource data shows the expected latitudinal and climatic gradients. The Al
> Wusta, Oman has the highest GHI of 2345 kWh/m2/year, the typical feature of BWh hot
> desert climate with low cloud cover. Pilbara, Australia has shown similar solar
> resources (2244 kWh/m2/year) even though it is located at the southern hemisphere. …
> The Magallanes, Chile has much lower solar availability (1100 kWh/m2/year) because it is
> located at high latitudes (53.2°S).

**Every modelling choice is justified in the sentence that makes it**, including the
choice not to do something:

> Technology learning curves **are disabled to isolate** climate-induced effects.
> A project lifetime of 25 years and a real discount rate of 8% are used **which lies
> within the range commonly adopted** in offshore renewable energy assessments, typically
> 5–10%.
> **While** other scenarios were tested to analyze supply dynamics, **the results are not
> further included in the discussion.**
> During the development of this study, the WKN had not yet been published, **which is the
> reason it is not included** in the scenario assumptions.

**Out-of-scope work is named and pointed at**, not ignored:

> It is worth noting that pinpointing the optimal offshore location, **although not the
> focus of this study**, necessitates a thorough evaluation of weather patterns … **It is
> suggested that the methodology proposed by Eriksson et al. [70] provides a way to**
> incorporate risk factors.

## Results: validate, then explain the anomaly yourself

Each subsection opens on its figure, validates against an external source, and only then
interprets.

> **Fig. 5 presents** the average capacity factors for all locations globally. The wind
> power capacity factors **show good agreement with** overlapping reported locations in
> the Global Wind Atlas [75].

The signature move is confessing the anomaly before a referee finds it, with the reason
and the defence in the same breath:

> The PV capacity factors **are lower than commonly reported global values** [76]. **This
> discrepancy is primarily due to** the assumption of horizontal panel orientation without
> tilt-angle optimization, **which is expected to underestimate** PV capacity factors
> relative to optimally tilted systems **but avoids overestimating** performance given the
> uncertain impact of wave-induced motions on OFPV systems [34].

Findings inside a paragraph are enumerated, and statistical claims carry their test:

> The distributions of LCOE, shown in Fig. 8(a), **reveal two main findings. First**, as
> expected, … **Second**, the LCOE distributions across all locations are consistently
> lower …

> This difference is statistically significant. **Mann-Whitney U-tests indicate that** …
> for the corresponding scenario (**p<0.005**).

## The discussion: N drivers, taken in order

The commonest architecture in the corpus. Restate what the study did, announce how many
drivers there are, then take them one per paragraph.

> This study provides a foundational techno-economic framework for natural hydrogen …
> **The analysis highlights three primary drivers that shape its viability: production
> scale, policy support, and transportation logistics.**
>
> **First**, the study confirms that economies of scale are the most powerful lever for
> cost reduction. The base scenario presents … 15,000 m3/day (approximately 56 kg/hour or
> 1.3 tons/day) across ten vertical wells, resulting in an LCOH of $6.82 per kilogram.
> **Importantly**, scaling production capacity by a factor of six … reduces the LCOH by
> more than 60%. This result emphasizes the nonlinear nature of hydrogen cost formation …
> **Hence achieving commercial scale is critical for competitiveness.**

Each driver paragraph: topic claim → base numbers → key comparison flagged *Importantly*
→ interpretation → a one-line takeaway.

## Numbers and units

**The same quantity is given in more than one unit**, so no reader converts:

> 15,000 m3/day (approximately 56 kg/hour or 1.3 tons/day)
> less than 6 tons/day (250 kg/hour)

**Ranges rather than point values**, with the driver attached:

> a 2-fold LCOA differential ($601–$1203/ton) **driven by** solar-wind resource quality
> optimal drilling depth (1375–1560 m) and flow rate (6.7–9.5 kg/s)
> between 9.09 and 12.73 Mton … **depending on** the stringency of the transition pathway

**Percentages carry their base:**

> 95.7 % (15.5 % for drilling, 65.8 % for mining, and 14.4 % for lining)

**Uncertainty gets its own sentence** rather than being hedged into the claim:

> It is worth noting that projections of future levels of installed capacities are highly
> uncertain and depend on factors such as market development and policy incentives.

## Highlights and title

**Highlights are telegraphic**: verb first, articles dropped, numbers in parentheses.
Usually one or two on what was built, three or four on what was found.

> Proposed a solar-assisted medium–deep geothermal seasonal storage framework.
> Developed a regression-based model (R2 = 0.98) for rapid performance prediction.
> Identified optimal drilling depth (1375–1560 m) and flow rate (6.7–9.5 kg/s).
> Confirmed solar charging cuts heating cost by 26% and shortens payback period.

Leading verbs: *Proposed, Developed, Revealed, Identified, Confirmed, Investigated,
Incorporated, Established, Analyzed, Compared*.

**Titles** name what was done, to what, for which case. None poses a question or uses a
rhetorical contrast.

> Techno-economics of renewable hydrogen export: A case study for Australia-Japan
> Comparative techno-economic analysis of large-scale underground hydrogen storage
> A spatially explicit techno-economic framework for assessing co-located systems

## Captions

An Applied Energy caption **identifies**; a working-paper caption **argues**. Corpus
figures run about 20 words, tables about 11.

Relocate rather than delete. A long caption is doing three jobs: naming what is plotted
(keep), stating a method or convention (move to methods), telling the reader what to
conclude (move to results, where an argument can be developed).

> **Fig. 5.** 2050 power merit order in Denmark, a salt-cavern market, under H2 Push.
> Both turbines held at the same efficiency.

## Converting an essayistic draft

| The draft writes | Applied Energy would write |
|---|---|
| *On the levelised-cost test the outcome settles, and it settles on the cost of holding the molecule between seasons.* | *The levelised-cost comparison is governed by the cost of seasonal storage.* |
| *Hydrogen was priced as a system operator prices it, on short-run marginal cost, which bounds the heating share it could hold by where it wins the winter-peak merit order.* | *Hydrogen is priced on short-run marginal cost, as a system operator would dispatch it, thereby bounding its heating share to the markets in which it wins the winter-peak merit order.* |
| *Neither gives a hydrogen peaker's standalone capital-recovery position market by market.* | *However, neither provides a standalone capital-recovery position for a hydrogen peaker at the market level, which remains a research gap.* |
| *The count turns on the hydrogen price path and not the policy scenario.* | *The count is determined by the hydrogen price path rather than by the policy scenario.* |
| *That is the same condition that decides the peaking arena.* | *This condition also determines the outcome in the peaking arena, indicating that both tests rest on the same physical quantity.* |
| *Space heating draws about three-quarters of its energy between October and March while electrolytic production is far flatter, so the mismatch must be stored.* | *Space heating draws approximately three-quarters of its energy between October and March, whereas electrolytic production is considerably flatter, necessitating seasonal storage of the resulting mismatch.* |
| *No hydrogen peaker recovers its capital from market rent in any country or scenario we run.* | *No hydrogen peaker recovers its capital from market rent in any country or scenario, with capacity-weighted recovery reaching only 9% across the markets that build.* |

The moves in the right-hand column are the whole conversion: name an explicit subject,
push the consequence into a trailing participle, mark the concession with *whereas* or
*however*, drag the number into the sentence, and prefer the plain verb to the vivid one.

## Where this collides with a project's own prose rules

Many careful authors ban em-dashes, colon splices, stock intensifiers and phrases like
*it is important to note*, because they are the register of machine-generated prose.
Applied Energy uses several freely, and the counts matter because they decide which of
two arguments you are actually having.

| Phrase | Corpus uses |
|---|---|
| `It is worth noting` | 14 |
| `It is important to` | 10 |
| `It should be noted` | 6 |
| `In recent years` | 5 |
| `Nowadays` | 1 |
| `It is well known` | 0 |
| `Obviously` | 0 |
| `Needless to say` | 0 |

So the general writing advice to strip all eight is half right. Three of them are common
in this journal and function as genre markers, and three genuinely never appear.

**The project's rules win.** Do not import a banned construction because the corpus has
it, and say so rather than breaking a rule quietly. But be clear which kind of rule is
being applied. Removing `It is worth noting` because a project bans it is a house
preference and is fine. Removing it because it is *bad journal writing* is a claim about
Applied Energy that the corpus does not support.

Most of what matters here survives any de-AI rule set: the funnel opening, the trailing
participle, the figure-as-subject sentence, *respectively*, cited statistics, inline
justification, naming prior authors, the roadmap paragraph and the conclusion formula.

## Working order

Sweeping the manuscript once per move is faster and more even than working sentence by
sentence. `rewriting.md` gives the twelve moves and the order; the short version:

1. Rewrite the abstract to the five moves (`phrasebank.md` §1 to §5). Most-read text.
2. Rewrite the opening paragraph as a funnel: global stakes, cited statistic, technology,
   problem.
3. State the gap in the journal's own words, then the contribution, then a roadmap
   sentence.
4. Work paragraph by paragraph: topic first, caveat last and flagged, consequences into
   trailing participles.
5. Convert the constructions in the table above.
6. Rewrite the results so figures are subjects and numbers ride inside sentences.
7. Convert every unfavourable finding to a comparison in positive grammar, and every direct
   recommendation to an enabling clause with the policymaker as agent (`stance.md` §1 and §2).
8. Set the hedging: one modal per claim, no epistemic adverbs (`stance.md` §3).
9. Reopen the conclusion with *This study presents…*, drop the first person, and list the
   findings as numbered items each carrying its own figures.
10. Cut table captions, then figure captions, relocating rather than deleting. Provenance
    goes into lettered footnotes under the table (`mechanics.md` §2).
11. Trace each headline number through highlights, abstract, results, discussion and
    conclusion. Digits, unit, labels and qualifying condition identical everywhere
    (`restatement.md`).
12. Re-run whatever numerical gate the project has. Caption text is where pinned phrases
    live, and restyling is how they break.
13. Rebuild the PDF, render it, and look at the pages. Nothing before this step can see
    a figure floating at 70 per cent width, an axis label under 6 pt, a five-line caption
    or an orphaned float (`visual_review.md`).

## Do not break these while restyling

**Any number, or any claim about one.** A caption can be shortened; what it asserts
cannot change.

**Load-bearing hedges.** *On the even-handed series*, *conditional on one weather year*.
These look like padding and are not. Stripping them turns a careful claim into an
overclaim, which is worse than sounding like a report.

**The argument's order.** House voice governs how sentences sound, not what the paper
says or the sequence in which it says it.

**The author's reasoning and their contribution.** House voice is a register, not a
personality. Two authors writing in it still write differently, because what they choose
to emphasise, which comparison they think decisive and how they frame their own
contribution are theirs. Convert the constructions, and leave the judgement alone. If a
restyled paragraph makes a different point from the original, the restyling failed
regardless of how well it matches the corpus.

The line is easy to locate in practice: changing *the count turns on the hydrogen price
path* to *the count is determined by the hydrogen price path* is house voice. Changing it
to *the hydrogen price path is the principal determinant* adds a ranking the author did
not claim.

## Look at the pages before you call it finished

Every other check here reads the source. A referee and an editor look at pages, and their
first impression is formed before a sentence is read. Render the PDF and go through it
with your eye.

    python scripts/render_pages.py main.pdf              # whole document, structure
    python scripts/render_pages.py main.pdf --detail 22  # one figure, readable

Then open the images. Three passes, in order.

**Flick through the low-resolution pages.** Where does the eye stop? Which pages are half
empty? Are the figures spread through the results, or clumped where the floats drifted? A
run of four text-only pages is where a reader disengages, and it is visible in two seconds
at this zoom and invisible in the source.

**On each figure.** Does it fill its column or the full text width, or is it floating at
70 per cent with margins either side? Is the smallest text readable? Is the legend boxed
and inside the axes? Does every bar carry its value? How many lines is the caption when
rendered, as opposed to how many words when counted?

**On each table.** Three horizontal rules and no verticals. Units in the header.
Provenance in lettered footnotes below rather than in the caption.

**What this is not for.** Do not reformat the submission to look like the published
article. Elsevier's *Your Paper Your Way* policy accepts any reasonable layout at first
submission, formatting is requested only at revision, and the two-column article is
typeset by Elsevier's production team. A single-column, double-spaced `[review]` build is
the right thing to submit.

**What transfers anyway.** Production re-typesets the text. It does not redraw your
figures, rewrite your captions, or shorten a table caption carrying 130 words of
provenance. An axis label set at 5 pt is 5 pt in print and nobody will fix it. So judge
figure content, caption length and table structure from the submission PDF.

The one question it cannot answer is whether the smallest text survives a two-column
width. Do not rebuild the manuscript to find out. `width=f\textwidth` scales by width
alone, so a label set at *p* points prints at `p × f × 3.4 / (native width in inches)`,
with Applied Energy's column at about 3.4 inches. Compute it, hold a 6 pt floor, and
assert the floor inside the figure generator. If you want to look rather than compute,
render the one figure at 3.4 inches, not the whole document.
`references/visual_review.md` carries the full checklist, the split between what is yours
and what is production's, and what the published corpus's pages actually look like.

## Reporting what was done

After a substantial pass, say what changed and what did not. Two things are worth
reporting and one is not.

**Report the counts that exist.** `check_stance.py` and `check_manuscript.py` produce
them: markers per thousand words, captions over the corpus p90, sentences over 60 words,
verdict vocabulary found, first person in the conclusion. These are countable before and
after, so a claim of improvement is checkable.

**Report the three highest-priority remaining improvements**, ranked by how much they
would change a referee's read. Usually one is structural, one is a defensible-claim
problem and one is prose. Naming three forces a judgement about what matters; naming
fifteen does not.

**Do not score the manuscript out of ten.** *Scientific clarity: 7/10* is a number with
no derivation, and a paper that bans unsourced figures in its own prose should not carry
them in its review notes either. Where a score is genuinely wanted, build it from the
counts the scripts produce and show the arithmetic.

## Supporting material

Eleven documents. The references are where the substance is; keep them open while writing
rather than reading them once.

| File | What it answers | When to open it |
|---|---|---|
| **`references/wording.md`** | How the sentences are built: subject slot, demonstrative chaining, the reporting-verb ladder, causation and comparison vocabulary, the word *only*, nominalisation, where the number goes, tense, how one finding becomes a paragraph, sentence openers, what the corpus never does, sentence-length distribution, and the discourse-marker budget | Writing or rewriting any sentence |
| **`references/stance.md`** | What the author is allowed to claim and how firmly: delivering an unfavourable result, policy implications without recommending, the modal hedging ladder, register at the conclusion, the limitations block, and disagreeing with a published number | Writing results, discussion, conclusion or limitations, and any time the finding is unwelcome |
| **`references/restatement.md`** | One headline number traced through highlights, abstract, results, discussion and conclusion in six papers: what is held constant and what may change | Before drafting the abstract or conclusion, and in the final consistency sweep |
| **`references/rewriting.md`** | Twelve mechanical moves that convert essayistic prose, each with a trigger, an operation and worked before-and-after pairs, plus the order to apply them in | Working through a draft |
| **`references/phrasebank.md`** | 31 sentence functions with corpus frames: opening, gap, contribution, roadmap, method, figure, numeric result, prior work, limitation, conclusion, equation, dataset, anomaly, statistical test, sensitivity, discourse markers | Stuck on how to phrase a particular job |
| **`references/anatomy.md`** | What each section contains and in what order: title, highlights, abstract, introduction, literature review, methods, equations, results, sensitivity, discussion, conclusion, headings, numbers and units | Before restructuring anything |
| **`references/mechanics.md`** | Everything below the sentence: figure design, table design and the lettered-footnote habit that keeps captions short, caption length by panel count, cross-reference style, numbers and units, spelling, paragraph length, citation density, body length, scenario naming, appendices, nomenclature, keywords, declarations | Building a figure or table, or setting anything that has a house convention |
| **`references/visual_review.md`** | How to render the pages and what to look for: why the review PDF misleads, what fourteen published pages look like when examined, a figure-table-page checklist, and the ten defects that survive every text-level check | Before calling a manuscript finished, and whenever a figure or table is built |
| `references/domain_heat.md` | What this corpus does and does not support for a buildings-and-heat manuscript, the heat vocabulary that is attested, and how to handle the terms that are not | Writing a paper about heating, dwellings or the building stock |
| `references/revision.md` | The response to reviewers: four reply moves built from the corpus's concession and attribution grammar, plus process conventions marked as unverified | After a revise-and-resubmit decision |
| `references/corpus_signals.md` | Measured lengths, with extraction caveats | A length question |

**One limit worth knowing before you rely on any of this.** The fourteen papers are
techno-economic energy-systems articles: hydrogen, ammonia, offshore wind, biomass, storage,
district heat. None of them is about heating the building stock. `dwelling`, `building
stock`, `heating degree` and `thermal envelope` appear zero times. For a buildings paper the
sentence-level guidance transfers, and the domain lexicon does not. Read
`references/domain_heat.md` first.

Scripts: `check_stance.py` flags verdict vocabulary, direct recommendations, epistemic
adverbs, off-register intensifiers, first person in the conclusion, marker density and
sentence rhythm, each against its corpus count; `style_signature.py` reports which journal
constructions a draft never uses; `check_manuscript.py` names the longest captions and
sentences; `render_pages.py` turns the PDF into images so the layout can be looked at;
`measure_corpus.py` re-derives everything for a different journal. All are checks after
rewriting, not guides to it, and the last one of them is your eye.

    python scripts/check_stance.py main.tex sections/*.tex
    python scripts/render_pages.py main.pdf
