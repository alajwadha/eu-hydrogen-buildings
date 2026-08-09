# Project Plan — EU Hydrogen Buildings Decarbonisation Model

> **Authors:** Ali Alajwad (Cornell M.Eng) · Dr. Abdurahman Alsulaiman (EPFL)
> **Output:** OIES Working Paper
> **Coverage:** EU27 + Switzerland + United Kingdom · NUTS3 regional resolution · 2025–2050

---

## Research Questions

**RQ1 — EU.** Under what conditions does hydrogen heating become cost-competitive with heat pumps in EU buildings? At what fuel price, in which countries, and on what timeline?

**RQ2 — Switzerland.** What role can hydrogen imports play in Switzerland's net-zero buildings strategy by 2050, and how sensitive is this role to import price assumptions from OIES ET08/ET32?

---

## Overall Approach

We built a spatially-resolved techno-economic Monte Carlo model that simulates how heating technology in EU+UK+Switzerland buildings changes from 2025 to 2050. The model covers:

- **29 countries** (EU27 + CH + UK)
- **3,823 NUTS3 regions** (sub-national resolution)
- **8 heating technologies** (gas boiler, oil boiler, biomass boiler, electric resistance, air-source HP, ground-source HP, district heat, H₂ boiler)
- **26 years** (2025–2050 annual)
- **3 scenarios** (REF, HIGH_HP, H2_HYBRID) × 200 Monte Carlo draws each

The model is structured in **five sequential steps** that feed into one another. Steps 1–4 are built and integrated; Step 5 (optimisation) is specified below and scheduled in the roadmap.

---

## Next-Phase Roadmap (accepted May 2026)

The model so far runs on **top-down** Hotmaps demand with **EU-wide** technology and cost assumptions. The accepted roadmap deepens it into a fully country-resolved model and completes the 3-scenario framing. Six phases:

### Phase 1 — Per-country deep research (all 4 layers)
For each of the 26 remaining countries (LU/FR/FI done), deep-research and build a sourced parameter pack across **demand, technology, economics and policy** — replacing EU-wide defaults. Outputs per country: a `code/data/country_config/{cc}.yaml` demand config; per-country technology / economics / policy tables; TABULA intensity files; and a fully-cited documentation set (`countries/{Name}/README.md` + `sources.md`, `literature/{country}/` methodology notes, `References_v1.bib` entries) to the Luxembourg/France standard. A country is not "done" until its documentation and references are complete.

### Phase 2 — Automated 29-country bottom-up build (Colab)
The bottom-up EUBUCCO pipeline (`country_build/01–04`) is scaled to all 29 countries via **6 group notebooks** built from the `france.ipynb` template. Countries are grouped balanced by data volume (at most one heavyweight — DE, IT, ES, PL, UK — per group). Notebooks are resume-safe and commit after each country. `03_heat_intensity.py` additionally emits a small committed `{CC}_heat_demand_nuts3.csv`. Raw EUBUCCO and per-building parquets are archived on Google Drive — gitignored, because GitHub cannot hold the ~38 GB 29-country parquet total.

Indicative size-balanced groups: G1 = DE + EE, LV, LT · G2 = IT + SI, HR, MT · G3 = ES + PT, EL, CY · G4 = PL + CZ, SK, HU · G5 = UK + IE, DK, CH · G6 = NL, RO, SE, BE, AT, BG.

### Phase 3 — Bottom-up demand integration
`BuildingStock.build_building_stock_bottomup()` concatenates the 29 NUTS3 CSVs into `building_stock_nuts3_bottomup.csv` (collapsing the 4-class bottom-up scheme to the 3-type model scheme). `Simulation.py` gains a `--demand {hotmaps|bottomup}` flag.

### Phase 4 — Cost-optimal scenario (Step 5, LP)
`Optimisation.py` is implemented as a PuLP linear program (see Step 5), adding a 4th scenario, `COST_OPT`.

### Phase 5 — NUTS3 tech-deployment map
`Simulation.py` exports NUTS3 × technology shares (`mc_nuts_tech_{SCEN}.csv`); a new `fig22_tech_deployment_map()` shows where each heating technology wins across Europe.

### Phase 6 — Full run and outputs
All 4 scenarios on bottom-up demand, with regenerated figures, tables and dashboard.

**Cadence:** Claude completes one group's research + documentation and commits it; Ali runs that group's Colab notebook; repeat for all 6 groups. **Scenario mapping:** business-as-usual = `REF`, cost-optimal clean pathway = `COST_OPT`, hydrogen pathway = `H2_HYBRID` (`HIGH_HP` kept as a sensitivity).

> **STATUS (June 2026): the May-2026 roadmap (Phases 1–6) is COMPLETE.** All 29 countries built bottom-up, integrated, COST_OPT added, full 200-sample run, figures, twice adversarially audited. The model is consistent end-to-end. The next phase below comes from Abdul's review meeting (June 2026).

---

## Next direction — Abdul review (June 2026)

Abdul's central steer: **stop framing the hydrogen result as "H₂ boiler vs heat pump LCOH"** (everyone does that). Reframe it as a **system merit-order (dispatch) question**, with hydrogen as a *marginal/peaking* heat producer. Three workstreams (A–C) are the priority, plus the supply extension (D) and the delivery-scenario / presentation / process items (E–H).

### AGREED SCENARIO FRAMEWORK (Ali, June 2026) — supersedes the old REF/HIGH_HP/H2_HYBRID
The old 3 scenarios were **wrong**: differentiated essentially by renovation rate only (carbon + H₂ price were CENTRAL for all), with bad names, and the imposed tech-share targets let banned fossil leak into H₂ (REF realised 13% H₂ vs 5% design). Replaced by **5 multi-lever scenarios**, with the technology mix **DERIVED from the merit-order economics** (NOT imposed shares):

| Scenario | Renovation | Carbon (ETS2) | H₂ price | Grid decarb. | Narrative |
|---|---|---|---|---|---|
| **CURRENT_POLICIES** | low (current as-built) | LOW | STRANDED/SLOW | slow | Only already-implemented measures; bans as enacted, not announced |
| **STATED_POLICIES** | current pace | CENTRAL | CENTRAL | central | Announced/legislated targets included (EPBD bans, ETS2 as stated) |
| **NET_ZERO** | Renovation-Wave | HIGH | CENTRAL | fast | Net-zero-aligned: deep renovation + high carbon + fast clean grid; HP+DH led |
| **H2_PUSH** | moderate | CENTRAL | RAPID (cheap H₂) | central | Hydrogen-favourable: cheap H₂ + gas-grid repurposing + policy support |
| **COST_OPTIMIZED** | (LP-chosen demand path) | — (shadow-priced) | CENTRAL | central | Least-cost LP (existing COST_OPT) |

Each scenario is a **bundle of 4 levers** (renovation rate, carbon trajectory, H₂-price trajectory, grid-decarbonisation speed) — NOT renovation alone. The heating-technology mix is then the **emergent output of the merit-order dispatch** (workstream B), so H₂'s share is derived from where it sits in the firing order under that scenario's levers, never imposed. This requires: (i) per-scenario lever wiring in Config + Simulation; (ii) the merit-order dispatch model (B); (iii) a full rename across code/results/figures/paper.

### Build sequence (June 2026, research in hand — see literature/merit_order_supply_research.md)
The four research streams are done; concrete steps to implement workstreams A–E:
1. **[DONE] Heat load-duration profile** (`scripts/heat_load_profile.py` → `heat_load_profile.csv`): per-country monthly profile + load-duration curve from annual demand + HDD (80/20 SH/DHW, peak/avg 3.5 cold → 5.2 mild). This is the demand input the merit-order dispatches against.
2. **[SUPERSEDED by a documented shortcut -- TYNDP has no clean per-country 2050 BAU; the endogenous peak price (power_peak_price.py) prices the marginal OCGT-vs-H2-turbine unit + scarcity premium band instead of a full capacity dispatch; disclosed in methodology + limitations] Capacity stack per country to 2050**: build `merit_order_capacity.csv` from TYNDP 2024 NT-2040 (per-country) + EU Ref Scenario 2020 (PRIMES, per-country to 2050) + national endpoints; tag found vs proxy. Power generation by source + DH/CHP capacity.
3. **[DONE]** **Marginal operating cost per technology** (EU-uniform): nuclear ~10–15, CCGT (fuel/eff + CO2 ~123/t → ~44/MWh carbon), OCGT/H2 peakers; waste-to-energy NEGATIVE (gate fee); large HP (bimodal on power price); biomass 25–35; geothermal 55–65. From research sec 1 + 3.
4. **[DONE -- merit_order_heat.py + power_peak_price.py; H2 wins the peak 0/4/9/8 of 29, EU-weighted share <=8%; missing money 0/29 (merit_order_profit.py); full hourly power coupling = stated future work] Merit-order dispatch (workstream B)**: stack capacities by marginal cost against the load-duration curve; the price-setting (marginal) unit on the peak slice is the focus. Insert H₂ as a quick-start storable peaker and find (a) the price it needs to enter and (b) the % of peak/marginal heat it captures. Couple to power (heat ≈ 25% of final electricity; HP electricity cost = time-weighted avg of ~€0 RES hours and €80–245 peaker hours).
5. **[DONE -- cavern EUR50 / non-cavern EUR100 per MWh-heat, Caglayan 2020] H₂ seasonal-storage adder (workstream D carve-out)**: add ~€1–2/kg (salt-cavern, 1 cycle/yr) to the H₂ peaking cost, €3+/kg for countries WITHOUT salt caverns (Caglayan 2020: DE/NL/PL/DK/UK have them; most of S/CE/Alpine EU do not). Keep the rest of supply as the delivered-cost input.
6. **[DONE -- merit_order_dh.py; H2 ranks 4.3-5.0 of 5; the carbon price, not cheap H2, opens the door (0/5/11/10 of 29)] DH source-switching (workstream C)**: DH dispatch with waste-to-energy at negative SRMC (must-run baseload, capacity-capped + declining), then recovered heat → large HP → biomass → H₂ at the margin. "Largely recovered/waste heat by 2050" anchored on Heat Roadmap Europe.
7. **[DONE -- June 12-13: levers wired, renamed, rebuilt 3x with double-check fixes, purpose-built P01-P19 figure set, Paper v5 with 4 new equations + Limitations + Assumptions]** **5-scenario lever wiring + rename + rebuild + paper** (workstream E/G): once the dispatch produces the mix, wire the 4-lever bundles, rename everywhere, rebuild, regenerate figures, update paper with Limitations + Assumptions sections.

### A. Renovation-rate correlation
Find and **apply the empirical correlation** between the envelope-renovation rate and the model's other drivers (population, electrification/income, the shared EU-policy factor). Today the cross-country renovation correlation is the structural assumption ρ = 0.5 and the per-country rates are anchored to observed pace + EU targets. Ground the correlation empirically and wire it in, so the renovation-rate sampling reflects a real co-movement rather than a flat ρ.

### B. Merit-order / marginal-producer economics — THE REFRAME (priority)
Replace the static LCOH comparison with a **dispatch / firing-order model of heat supply**, where technologies are stacked by **marginal operating cost** and the most expensive (last-on) unit is the *marginal producer* that sets the price and meets the peak slice of demand. Hydrogen — quick to start/stop, storable like gas, and paying **no carbon cost** — is modelled as a candidate **marginal (peaking) producer**, not a base-load replacement. Steps:

1. **Heat-demand profile per country** — build a load-duration / daily heat-demand curve over the year (from heating-degree-days × the number of days). The coldest days set peak demand; apply the demand ratio across the year.
2. **Technology capacity to 2050 per country** — do NOT derive ourselves; take projected capacities from **IEA business-as-usual scenarios** (use country-level if available, else regional proxy applied per country, respecting structure e.g. FR nuclear-heavy, DE no nuclear). Deep-research the capacities per country.
3. **Marginal operating cost per technology** — fuel + processing + carbon, the dispatch price (assume EU-uniform cost per technology for tractability: a gas peaker in IT ≈ a gas peaker in FR).
4. **Build the firing order (merit-order step curve)** for heat: cheap base-load first (nuclear, renewables, waste/CHP) → mid (CCGT) → marginal/peaking (fossil peakers, hydrogen) last. Where each technology's capacity runs out, the next-dearest takes over until peak demand is met.
5. **Insert hydrogen as a marginal producer** with its own delivered price + carbon-free benefit. Find (a) the price hydrogen must reach to enter the merit order, and (b) the **% of (marginal/peak) heat demand hydrogen can capture**. That share — not "H₂ replaces heat pumps" — is the headline hydrogen result.
6. **Power-sector link:** heat is ~25% of final electricity consumption; trace that electricity's source mix 2025→2050 and apply the power-sector firing order (hydrogen can also be an electricity source/store feeding heat pumps). Use the SAME scenario set for power as for demand.
- *Caveat (Abdul):* merit-order/marginal-cost dispatch data is standard for **electricity**; it may not exist directly for **heat** — derive carefully, likely off the electricity system, and flag the approximation.

### C. CHP / district-heating source switching
When a CHP/district-heat network exists, the **source can be switched**. Per country: (1) identify the current and 2050 DH/CHP fuel — often **waste / wastewater** (find a reference that confirms "by 2050 it is largely waste"); (2) put an **economic value on waste**; (3) if waste is phased out, cost the alternatives per kWh — large heat pump vs hydrogen — to see what replaces it in the DH plant.

### D. Supply side (optional — Ali's interest; scope decision)
Possible upstream extension: production → midstream → transport → delivered cost. **Abdul's warning:** this is a huge effort (his ammonia paper ran ~200 pages, mostly appendix) and every layer adds contestable assumptions. **Default: treat delivered H₂ as an INPUT** — already done via the bottom-up delivered-cost model calibrated to Alsulaiman OIES ET24 / ET32. Decide explicitly where to stop; if extending, be ruthless about documenting assumptions.

### E. Hydrogen delivery scenarios (refine)
- The **fair like-for-like comparison is H₂ boiler vs GAS boiler** (same technology class), not H₂ vs heat pump.
- Three H₂ delivery routes: (1) **blend** H₂ into the existing gas grid (~2–5%, with leakage); (2) **retrofit** the existing gas grid to 100% H₂ (retrofit cost — already in the infra scenario); (3) **new dedicated H₂ pipelines** / hydrogen backbone.

### F. Carbon pricing
ETS2 covers buildings from 2027; project to 2050 using **one standardized BAU source**. UK/CH: assume comparable pricing (own systems but similar). Present the COST_OPT "implied carbon price" as **indicative**.

### G. Presentation / figure polish (Abdul's paper feedback)
- Figure titles: **"EU + UK + Switzerland"** (not just EU).
- LCOH-comparison figure: add **2050** (currently 2025).
- Remove internal gridlines, keep a clean black frame.
- Fix legend positioning.
- Add a dedicated **Limitations** section and an **Assumptions** section.

### H. Writing process, timeline, submission
- **Abdul's writing order:** results → discussion → literature review → research questions → introduction → conclusion → abstract. Methodology/data written alongside results; the *detailed* methodology goes in the **appendix** (no black box — every value supported).
- **Timeline:** freeze results by ~mid-July; the report is ~2–3 weeks after results are frozen (AI-assisted drafting, then wording polish).
- **Submission:** OIES working paper (internal → external review) first, then a journal (hydrogen / energy-systems). Affiliation: Columbia (Ali), possibly Johns Hopkins.

---

## Step 1 — Policy

### What it does
Defines the regulatory environment each country operates under: when fossil-fuel boilers must be phased out, when carbon pricing takes effect, and how clean the electricity grid is expected to become.

### Inputs we collected
- **Boiler ban dates** for all 29 countries — four dates per country: subsidies end, new-build ban, replacement ban, full phase-out
  - Sources: EHPA Boiler Ban Tracker (Nov 2025); Germany GEG 2024; EU EPBD 2024; Swiss EnDK 2050+; UK Future Homes Standard
- **Carbon price trajectories** — three scenarios (LOW €70/t, CENTRAL €122/t, HIGH €200/t by 2030)
  - Sources: BNEF ETS2 Outlook; Enerdata POLES
  - ETS2 launches 2027 → buildings pay zero carbon cost before that year
- **Electricity grid CO₂ intensity** — per country per year
  - Sources: EMBER 2024 (current actuals); EEA Fit-for-55 (2030–2050 projections)
  - Example trajectories: Poland 600 → 30 gCO₂/kWh · Germany 350 → 15 · France 80 → 8 · Sweden 45 → 5

### How it feeds the Monte Carlo
- Boiler ban year → **hard constraint**: gas/oil share forced to zero after ban
- HP mandate year → minimum HP share floor
- Carbon price → passed into LCOH calculation per scenario
- **ETS2 pass-through rate** (75–100%, sampled per draw) → scales the carbon component of LCOH

### Module
`code/src/Policy.py`

### Open issue
Carbon price path is treated as a scenario axis, not a probabilistic parameter. The MC uncertainty bands do **not** include carbon price risk.

---

## Step 2 — Economics (Levelised Cost of Heat)

### What it does
Calculates the all-in cost of heat for every technology in every country in every year. This is the **Levelised Cost of Heat (LCOH)** in €/MWh useful heat delivered.

### Formula
```
LCOH = (annualised CAPEX) + (fixed O&M) + (variable O&M) + (fuel cost ÷ efficiency) + (carbon adder)
```
Where:
- annualised CAPEX = Capital Recovery Factor × CAPEX/kW ÷ (annual hours × efficiency)
- fixed O&M = FOM €/kW/yr ÷ (annual hours × efficiency)
- carbon adder = carbon price × fuel emission factor ÷ efficiency

### Parameter sources

| Component | Country-specific? | Source |
|---|---|---|
| CAPEX (€/kW upfront) | No — same for all countries | JRC Technology Data 2023; IEA Future of Heat Pumps 2022; IRENA Heat Pump Costs 2022; Danish Energy Agency 2023 |
| FOM (€/kW/yr fixed maintenance) | No — same for all countries | JRC Technology Data 2023 |
| VOM (€/MWh variable cost) | No — same for all countries | JRC Technology Data 2023 |
| Gas price (€/MWh residential) | **Yes — per country** | Eurostat nrg_pc_202, H1 2025 (residential end-user including all taxes) |
| Electricity price (€/MWh residential) | **Yes — per country** | Eurostat nrg_pc_204, H1 2025 (residential end-user including all taxes) |
| Heat pump efficiency (SCOP) | **Yes — per country** | Hotmaps HDD data; EHPA performance database |
| Heating hours per year | **Yes — per country** | Hotmaps heating degree days |
| H₂ fuel price | No — four global trajectories | OIES ET08 (2022); OIES ET32 (2024). RAPID/CENTRAL/SLOW/STRANDED |
| Discount rate | No — 5% real pre-tax | BPIE 2024 (consistent with IEA) |

### Key parameter values
- Gas boiler: CAPEX €1,000/kW · efficiency 92%
- Air-source HP: CAPEX €1,200/kW (2025) → €700/kW (2050) · SCOP 2.8–4.1 by climate
- Ground-source HP: CAPEX €2,000/kW → €1,400/kW · SCOP 3.5–4.5
- H₂ boiler: CAPEX €1,400/kW → €1,100/kW · efficiency 90%
- District heat connection: CAPEX €1,200/kW network connection

### Headline finding from this step
**Heat pumps are already cheaper than gas boilers in all 29 countries in 2025.** EU median: HP €124/MWh vs gas €197/MWh. Driven by post-2022 residential gas price escalation combined with HP COP advantage.

### How it feeds the Monte Carlo
LCOH table pre-computed once per run. Inside the simulation, cheaper technologies get proportionally higher market share via softmax weighting, blended 50/50 with scenario target.

### Module
`code/src/Economics.py`

### Open issues
- CAPEX/FOM/VOM are the same across all 29 countries — no labour cost differential
- Fuel price multipliers are sampled (±15% lognormal) but **never actually used** in the LCOH calculation — the table is built once per run
- Softmax blending (50/50) is a shortcut for the full LP/MILP

---

## Step 3 — Building Stock

### What it does
Provides the spatial foundation of the model. Defines how much heat each NUTS3 region needs, in which building types, and what fraction of those buildings are physically suitable for each technology.

### Data structure
`data/processed/building_stock_nuts3.csv` — **3,823 rows**, one per NUTS3 × building type combination.

Each row contains:
- `nuts_id` — region code (e.g., BE100 = Brussels)
- `country` — ISO2 code
- `building_type` — SFH (single-family house), MFH (multi-family house, apartment blocks), OTHER
- `dwellings_2021` — count of dwellings of that type in that region
- `heat_2015_MWh` — baseline annual heat demand for that building type in that region

### Sources

| Data | Source |
|---|---|
| Dwellings by type and NUTS3 (EU27 + CH) | Eurostat Census 2021 (table CENS_21DWBNO_R3) |
| UK dwellings | ONS Census 2021 (table TS044) |
| Heat demand per region | Hotmaps project (residential space heating + DHW, baseline ~2015) |

### Feasibility scores

Stored in `data/processed/hp_dh_feasibility.csv`. These reflect how technically feasible it is to install each technology in each building type:

| Building type | HP feasibility | DH feasibility |
|---|---|---|
| Single-family house (SFH) | 0.90 | 0.30 |
| Multi-family house (MFH) | 0.50 | 0.80 |
| Other (commercial, public) | 0.70 | 0.50 |

These are **expert judgment** with no published source — flagged for Abdul's validation before submission.

### How it feeds the Monte Carlo
Every MC draw starts from this file. For each of the 3,823 rows, the simulation asks: given the heat demand in this region and building type, how is that heat supplied in each year? Feasibility scores cap the maximum penetration of HP/DH in each row.

### Module
`code/src/BuildingStock.py`

---

## Step 4 — Monte Carlo Simulation

### What it does
Ties Steps 1, 2, and 3 together. Runs the full model 200 times per scenario. Each run varies key uncertain parameters to produce uncertainty bands rather than single-point estimates.

### What varies between the 200 draws
- Demand reduction rate (σ = 5% around scenario target)
- Transition speed (power-law exponent; how fast technology shares shift)
- HP / DH feasibility multipliers (±10–15%)
- ETS2 pass-through rate (75–100% uniform)
- Discount rate (±0.5% around 5%)

### What does NOT vary (current limitation)
- Fuel prices (sampled but disconnected from LCOH)
- Carbon price path (treated as scenario axis)
- CAPEX learning rates
- Technology efficiencies

### Emissions calculation (within Step 4)
After each MC draw computes technology shares and final energy use, emissions are calculated using:
- Gas/oil combustion: IPCC AR6 WG3 (gas 0.202 tCO₂/MWh; oil 0.265 tCO₂/MWh)
- Electricity (heat pumps): country × year grid intensity from EMBER + EEA
- District heat: EEA district heating database, 23 countries
- Biomass: zero (EU RED II accounting; contested scientifically)
- Green hydrogen: zero scope 1

### Speed
0.58 seconds per sample (after vectorisation). 200 samples ≈ 2 minutes per scenario. All three scenarios in ~6 minutes on a standard laptop.

### Outputs
For each scenario, three CSV files in `code/results/`:
- `mc_summary_{SCEN}.csv` — EU-wide heat demand and tech shares, q10/q50/q90 quantiles
- `mc_emissions_{SCEN}.csv` — CO₂ totals by carrier, country, intensity
- `mc_country_{SCEN}.csv` — country-level breakdown (top 15)

### Modules
`code/src/Simulation.py` (main engine) · `code/src/Emissions.py` (CO₂ module)

### Scenarios

| Scenario | Description | HP 2050 | H₂ 2050 | Demand 2050 |
|---|---|---|---|---|
| **REF** | Reference — moderate ambition, current policy trajectory | 50% | 7% | −30% |
| **HIGH_HP** | High electrification — deep renovation + max HP rollout | 56% | 5% | −46% |
| **H2_HYBRID** | Hydrogen hybrid — meaningful H₂ role, gas grid repurposed | 37% | 26% | −36% |

---

## Step 5 — Optimisation (LP/MILP)

### What it should do
Replace the softmax blending shortcut with a proper optimisation. Find the cost-minimising technology deployment pathway subject to:
- Policy constraints (boiler bans, HP mandate floors)
- Feasibility constraints (HP/DH penetration caps per NUTS3 building type)
- Carbon budget constraints
- Annual capacity constraints (installer capacity, manufacturing supply)

### Status
**Scheduled — Phase 4 of the roadmap.** Module is currently a placeholder (`code/src/Optimisation.py`) raising `NotImplementedError`.

### Decided approach
Implemented as a **linear program** — shares of a building stock are genuinely fractional, so no MILP — using **PuLP** with the bundled CBC solver (no external solver install). Objective: minimise total discounted system cost over `share[nuts_id, building_type, year, tech]`. Constraints: shares sum to 1 per region/type/year; fossil shares forced to 0 after each country's boiler-ban year; HP/district-heat shares capped by `hp_dh_feasibility.csv`; HP-mandate floor; an annual replacement-rate ramp (~5–7%/yr) for realistic pathways; and an optional EU carbon-budget constraint. It becomes the 4th scenario, `COST_OPT`, alongside REF / HIGH_HP / H2_HYBRID.

---

## Outputs Generated

### Figures (13 total, `paper/figs/`)
1. Heat demand decomposition by scenario
2. Tech shares timeline
3. **Transition pathways** — stacked area chart, all four scenarios with MC bands
4. **CO₂ trajectory** — emissions over time with uncertainty
5. **LCOH comparison** — horizontal bars by tech, with country range
6. **Country heatmap** — tech shares 2030 vs 2050
7. **ETS2 impact** — gas vs HP, by country
8. **H₂ threshold** — competitiveness gap under 4 price trajectories
9. Sensitivity tornado (pending `--sensitivity` run)
10. **Fuel price trajectories** — gas, electricity, hydrogen
11. ~~HP crossover year~~ (removed — uninformative)
12. **Grid CO₂ trajectories** — by country group with breakeven line
13. **LCOH waterfall** — cost breakdown for DE/PL/FR
14. **Switzerland H₂** — RQ2-specific (import price vs HP LCOH)

### Tables (`paper/tables/`)
- LCOH summary (90 rows)
- CO₂ reduction by scenario
- Country tech shares
- ETS2 adder by country

### Paper
- `paper/Paper_v2.tex` — current working draft
- Sections: Abstract ✅ · Results (~1,600w, real numbers) ✅ · Discussion (~1,200w) ✅ · Conclusion (~1,100w, 5 policy implications) ✅
- Pending: Introduction (3 TODOs), Methodology (7), Literature review (8), Limitations (2)

### Interactive Dashboard
- `docs/index.html` — D3 choropleth map, country comparison, H₂ threshold finder
- Live at: https://alajwadha.github.io/eu-hydrogen-buildings/

---

## Open Items for Abdul

### Model design
1. CAPEX/FOM same across countries — acceptable for OIES, or add country multiplier?
2. Softmax blending in place of LP/MILP — keep as shortcut or build Step 5 before submission?
3. MC bands don't include fuel price or carbon price uncertainty — acceptable for working paper?

### Data
4. HP/DH feasibility scores (SFH=0.90, MFH=0.50, SFH DH=0.30, MFH DH=0.80) — Abdul's sign-off or published source?
5. H₂ price reference — is OIES ET08 correct, has ET32 superseded it?
6. Hungary residential gas €31/MWh (subsidised) — use subsidised or market price?
7. Biomass zero-emission (EU RED II) — run sensitivity with upstream emissions?

### Framing
8. Headline finding "HP already cheaper than gas everywhere in 2025" — right framing for OIES, or lead with policy/infrastructure?
9. Conclusion definitiveness on H₂ in buildings — appropriate, or soften for hydrogen industry readers?
10. Target outlet — OIES Working Paper only, or journal submission after (Energy Policy / Applied Energy / Energy Research & Social Science)?

---

## How to Run

```bash
# Clone
git clone https://github.com/alajwadha/eu-hydrogen-buildings
cd eu-hydrogen-buildings

# Setup (one-time)
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Full pipeline — all four scenarios, 200 MC samples, all figures, dashboard
python run.py --skip-download --samples 200

# Or from VS Code: Ctrl+Shift+B → "🔬 Run ALL scenarios (200 samples)"
```

Runtime: ~6 minutes on a standard laptop.
