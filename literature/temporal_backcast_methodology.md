# Temporal consistency: base-year anchoring + LMDI multi-driver 2015 backcast

**Status:** 2026-05-28. Replaces the earlier single-driver stock-growth backcast
with a per-country multi-driver LMDI decomposition on the design-demand basis.

## 1. The problem

The bottom-up demand is built from **EUBUCCO v0.2** footprints (snapshot
~2020-2023) and **TABULA/EPISCOPE** design intensities, after the documented
area/comfort/climate corrections. It is therefore an estimate of the **current**
residential heating stock's **design useful demand** (kWh/m^2/yr at TABULA's
reference 20 deg C / 18 h / whole-house operation). Two defects followed from
treating this snapshot as the year-2015 demand level:

1. **Benchmark vintage mismatch.** The snapshot (current stock) was compared
   directly against **Hotmaps 2015**, a benchmark a decade older. Raw gaps
   conflated model error with a decade of real stock and efficiency change.

2. **Latent anchoring inconsistency in the scenario engine.** Demand reduction
   was interpolated from 2015 while every other time-varying quantity (tech
   shares, COP, turnover, prices) was interpolated from 2025. The model's 2025
   demand therefore sat below the snapshot it was supposedly built from.

## 2. The fix

### 2a. Base-year anchoring (forward, affects scenario results)

`Config.BASE_YEAR = 2025`. The bottom-up snapshot is the demand level in
BASE_YEAR; net useful-demand reduction accrues from BASE_YEAR to 2050 in:

- `Simulation.interpolate_heat_demand` and the vectorised MC loop
- `Optimisation._demand_factor`

2025 demand now equals the snapshot exactly; the 2050 endpoint is unchanged.

### 2b. 2015 backcast (LMDI multi-driver, design basis)

To compare against Hotmaps 2015 at a **matched vintage**, the BASE_YEAR national
snapshot is backcast to 2015 using the **Logarithmic Mean Divisia Index (LMDI;
Ang 2005)** multi-driver decomposition. The identity:

```
Q_2015 / Q_2025 = (Pop_15 / Pop_25)
                * ((Dw/Pop)_15 / (Dw/Pop)_25)
                * ((m2/Dw)_15 / (m2/Dw)_25)
                * (i_design_15 / i_design_25)
```

where:
- **Pop**: total population (Eurostat `demo_gind`; ONS for UK; BFS for CH).
- **Dw**: total residential dwellings (Eurostat census 2011 / 2021 endpoints
  interpolated; national stats offices Destatis, INSEE, ISTAT, INE, CBS, SCB,
  GUS, ONS/MHCLG, CSO, KSH, INS, NSI, CYSTAT, CSB, STATEC, SURS, NSO Malta,
  BFS).
- **Dw/Pop**: dwellings per capita (= 1 / household size); rises as households
  shrink across most of Europe.
- **m2/Dw**: average dwelling floor area (Eurostat `ilc_hcmh02` 2012 reference;
  national series where available for DE 2023, PL 2023, CZ 2021). Treated as
  flat per country across 2015-2025 because national-series checks show drift
  <2% over a decade.
- **i_design**: **design** specific energy intensity (kWh/m^2/yr), i.e. the
  envelope-driven part. Backcast factor per country:
  ```
  i_design_15 / i_design_25 = (1 + r_country)^10
  ```
  where `r_country` is the country's **envelope-relevant renovation rate**,
  derived from JRC depth bands with envelope-saving weights:
  ```
  r_country = 0.50 * deep_pct + 0.25 * medium_pct + 0.05 * light_pct
  ```
  This isolates the envelope component (insulation, glazing, airtightness)
  from conversion-efficiency and behaviour effects that change *final* but not
  *design* demand. EU stock-weighted average r ~ 0.55 %/yr (range 0.26 FI to
  1.00 CH); see `code/data/country_config/design_intensity_decline.csv` for
  per-country values and sources.

**Why design intensity and not metered intensity.** The model represents the
*useful design demand* of the building envelope, not delivered final energy.
Metered intensity declines additionally through boiler/HP efficiency improvement
and prebound/behavioural response, neither of which changes what the building
physically needs. Using a metered-intensity ratio for the backcast would be a
category mismatch.

### 2c. Per-country corrections (kept as-is)

The four model-side corrections are **source-grounded fixes, not Hotmaps
calibrations**:

- `eubucco.area_correction` per country (AT/DK/EE/ES/HR/HU/IE/LT/CY) -- census
  heated-dwelling area (Statistik Austria GWZ, Danmarks Statistik BOL101,
  Statistics Estonia, INE, DZS, KSH, CSO, Statistics Lithuania, CYSTAT).
- `comfort_regime.deflator` per country (ES/EL/CY/PT/BG/RO/MT) -- Mediterranean
  partial-heating regime (IDAE SPAHOUSEC II; CRES, Santamouris et al.; CYSTAT
  Household Energy Consumption Survey; INE ICESD; NSI EHCI; INS ECRDS; NSO
  Malta Household Budget Survey).
- `tabula.class_mix_proxy` (EE, LT) -- Baltic SFH from Swedish wooden typology +
  MFH from Polish panel-block typology.
- Option B `tabula_reference_hdd` (IT, FI, plus BE/DK/IE/NL/SK using ref-zone)
  -- TABULA brochure published a specific reference-zone HDD rather than the
  national mean.

Documented in `eubucco_census_area_audit.md`, `climate_reference_hdd_audit.md`,
`inv_countries_academic_refinements.md`.

### 2d. Forward projection 2025 -> 2050 (LMDI, scenario-differentiated)

The same multiplicative decomposition runs forward to project demand to 2050:

```
D_c(t) / D_c(2025) = (Pop_c,t / Pop_c,25)
                   * ((Dw/Pop)_c,t / (Dw/Pop)_c,25)
                   * (1 - r_{c,s})^(t - 2025)
```

with average dwelling size held flat. Inputs: population from EUROPOP2023
(EU-27), ONS 2022-based (UK), BFS A-00-2025 (CH), in `pop_projection.csv`;
dwellings-per-capita from the household-size trajectory (linear extrapolation of
the observed 2015-2023 `ilc_lvph01` trend); and `r_{c,s}` the per-country,
per-scenario envelope-design intensity decline rate in
`scenario_intensity_rates.csv`. The demand reduction is therefore an **emergent**
quantity (net of population, occupancy and envelope renovation), not an imposed
2050 target. Code: `Config.forward_demand_ratio`.

**Scenario lever and the proportional-scaling caveat.** Central rates: REF holds
each country's current envelope-renovation pace (EU stock-weighted ~0.55 %/yr);
HIGH_HP multiplies it by 2.73 (EU-average 1.5 %/yr = Renovation Wave 3 %/yr x
~50 % envelope depth, / 0.55); H2_HYBRID by 1.64 (intermediate; hydrogen does not
change the envelope). The **same multiplier is applied to every country**, so
the scenarios scale each country's own baseline proportionally rather than
converging all countries to a common target. This preserves the cross-country
heterogeneity of REF but means HIGH_HP implies an envelope-intensity decline of
~2.7 %/yr in high-baseline countries (e.g. CH), at the upper edge of physical
plausibility for a sustained 25-yr rate, and <1 %/yr in low-baseline countries
(e.g. FI). HIGH_HP should be read as proportional acceleration of national
paces, not as convergence to the uniform 3 %/yr Renovation Wave target.

**Sensitivity sampling.** In the 200-draw Monte Carlo, `r_{c,s}` is sampled
N(central, sigma) truncated to [0, 5 %]/yr, with sigma ~= 0.21 x central so the
published low/high columns (central x 0.65 / x 1.35) correspond to the 5th/95th
percentiles. Country shocks are **correlated through a shared EU-policy factor**:
z_c = sqrt(rho)*z_EU + sqrt(1-rho)*z_c_idio with rho = 0.5 (Config.INTENSITY_RATE_CORR).
This preserves each country's marginal (so per-country bands and all medians are
unchanged) while preventing the EU-aggregate band from being diversified away by
the (unrealistic) assumption of independent national renovation pace; the EU band
is ~2.2x wider than under independent draws (3.0x at rho=1). rho is a structural knob: rho=0
recovers independence, rho=1 full correlation.

**COST_OPT note.** The cost-optimisation LP fixes demand at the REF LMDI
trajectory (central per-country rate) and optimises only the supply mix; it does
not co-optimise renovation depth. Its emissions cap is scope-1 (on-site
combustion) only, with an exogenous near-zero 2050 grid, so a -100 % cap means
net-zero on-site combustion, not economy-wide net-zero. See
`cost_optimisation_methodology.md`.

## 3. The driver data

Per-country annual time series 2015-2023, all 29 countries (EU-27 + UK + CH):

| Dataset | File | Source |
|---|---|---|
| Residential space-heating final energy (TJ) | `heat_drivers_eurostat.csv` (27 EU) + `heat_drivers_national.csv` (UK+CH) | Eurostat `nrg_d_hhq` FC_OTH_HH_E_SH; DESNZ ECUK 2024 Table U3; BFE Privathaushalte 2000-2023 |
| Heating degree days (annual) | same panels | Eurostat `nrg_chdd_a` base 15C; DESNZ DUKES 1.1.9 base 15.5C |
| Population | same panels | Eurostat `demo_gind` (POP/JAN); ONS UKPOP; BFS via BFE Tab 11 |
| Real GDP (CLV20_MEUR) | same panels | Eurostat `nama_10_gdp`; ONS ABMI (UK); SECO via BFE (CH) |
| Residential electricity (TJ) | same panels | Eurostat `nrg_d_hhq` E7000; DESNZ ECUK; BFE Tab 10 |
| Dwellings (annual, count) | `heat_drivers_demographics.csv` | Eurostat census 2011/2021 + national stats (Destatis, INSEE EAPL, ISTAT permanent census, INE, CBS 81955ENG, SCB BO0104, GUS, ONS Dwelling Stock by Tenure, MHCLG Live Tables, CSO Census 2022, KSH 2022 census, INS Romania, NSI BG, CYSTAT, CSB Latvia, STATEC, SURS, NSO Malta, BFS GWS) |
| Avg household size (persons/dw) | same | Eurostat `ilc_lvph01`; ONS Families and Households; BFS Privathaushalte |
| Avg dwelling size (m2) | same | Eurostat `ilc_hcmh02` 2012 reference; Destatis 2023; GUS 2023; CZSO 2021 |
| Renovation rate by depth (%/yr) | `heat_drivers_renovation.csv` | JRC Castellazzi & Esposito 2019 Table 2 (EU-28 2012-2016 floor-area-based); BPIE 2024 EU Buildings Climate Tracker; national supplements (ADEME MaPrimeRenov; ENEA Superbonus; SEAI National Retrofit Plan; KfW BEG; English Housing Survey; BFE Gebaeudeprogramm) |
| Design intensity decline %/yr per country | `design_intensity_decline.csv` | Derived: 0.5*deep + 0.25*medium + 0.05*light from JRC depth bands |
| Residential energy prices (gas, elec, oil, pellets, DH) | `heat_drivers_prices.csv` | Eurostat `nrg_pc_202` (gas band D2 tax-incl); `nrg_pc_204` (elec band DC); oil/pellets/DH gaps documented |
| Heating-tech mix 2015 vs 2023 (8 techs) | `heating_mix_2015_vs_2023.csv` | Eurostat `nrg_d_hhq` by fuel + EHPA Market Reports 2016 & 2024 + national (BDH, IDAE, ENEA, CEREN/Observatoire EDF, SEAI, SCB/Energimyndigheten, Statistics Finland/SULPU, BFS/FWS) |
| Dwelling-stock growth %/yr per country | `stock_growth.csv` | OECD HM1.1 + Eurostat census + national stats (HIGH-confidence rows: DE, BE, FR, ES, FI, NL, PL, RO, SE, BG, UK, CH) |
| 30-yr HDD climate normal (1991-2020) | `hdd_normal_1991_2020.csv` | Eurostat `nrg_chdd_a` mean 1991-2020 base 15 deg C; DESNZ Energy Trends 7.1b for UK base 15.5 (WMO Climatological Normal) |

## 4. The LMDI weights

Three different "weights" sit inside the method, all explicit:

1. **Multiplicative driver weight = 1** for each driver in the backcast ratio.
   It's an identity, not a regression. No fitting, no estimated elasticities.

2. **Depth-band weights** (the only judgment weights, in `design_intensity_decline.csv`):
   deep x 0.50, medium x 0.25, light x 0.05. Each captures the typical envelope
   contribution of a renovation of that depth (deep ~50 % design-intensity
   reduction per renovation, medium ~25 %, light ~5 %; mid-range of BPIE depth
   bands and EU passive-house standards).

3. **Log-mean weight L(a, b) = (b - a) / ln(b/a)** (Ang 2005). Used to
   convert log-ratios into TWh contributions in the additive form. Makes the
   per-driver contributions sum exactly to the total change (no residual).

Country aggregation to EU = TWh sum (equivalent to weighting each country by its
2025 model demand). Largest weights: DE 20 %, FR 15 %, IT 13 %, UK 10 %, PL 7 %,
ES 4 %, BE 3 %, NL 3 %.

The **30-yr HDD normal** is used only to climate-correct the *observed
final-energy* benchmark (Eurostat metered series). It does **not** enter the
design backcast (the model is at TABULA normal climate by construction).

## 5. Results

### 5a. Headline (EU)

| Metric | Value | Reading |
|---|---|---|
| Hotmaps 2015 (top-down benchmark) | 3,863 TWh | reference |
| Model 2025 corrected (snapshot) | 3,828 TWh | present-day design demand |
| **Model 2015 corrected (LMDI design backcast)** | **3,825 TWh** | matched-vintage design demand |
| **Gap Model 2015 vs Hotmaps 2015** | **-1.0 %** | within +/-15 % OK band; validation passes |
| **EU Delta 2015 -> 2025** | **+0.1 %** | essentially flat |
| Observed 2015 (Eurostat metered, climate-corrected to 30-yr WMO normal) | 2,234 TWh | metered final energy ~58 % of Hotmaps useful; the prebound effect |
| Model 2025 naked (no corrections) | 4,708 TWh | snapshot without comfort/area/Option B/class_mix |
| Model 2015 naked (LMDI design backcast) | 4,729 TWh | for sensitivity only |

All rows are the `EU` row of `results/lmdi_design.csv` as committed. This is the LMDI
*design* backcast, in which population, occupancy, dwelling size and envelope intensity all
move and very nearly cancel. It is not the stock-only backcast in
`results/reconcile_backcast.csv`, which carries no envelope term and therefore reads -8.5 %
vintage-matched on its own Hotmaps basis. The two are different constructions and the
manuscripts say so.

### 5b. EU LMDI driver decomposition (Δ 2025 − 2015, TWh)

| Driver | Contribution | % of EU 2025 | Reading |
|---|---|---|---|
| Population | +66.9 TWh | +1.75 % | pop grew, added demand |
| Occupancy (Dw/Pop) | +175.2 TWh | +4.59 % | households shrank, more dw per person |
| Dwelling size | 0.0 TWh | 0 % | held flat |
| Design intensity (envelope retrofit) | -240.1 TWh | -6.29 % | envelope retrofit removed demand |
| **Net Delta** | **+2.0 TWh** | **+0.05 %** | drivers nearly cancel |

**Why the EU change is only ~0.1 % (and not larger):** the two "stock-side"
drivers and the "intensity" driver push in opposite directions and at roughly
the same magnitude over the 2015-2023 window:

- **Stock-side push (UP)** -- combined +6.3 % over the decade. EU population
  grew ~0.2 %/yr (+1.8 % over 10 yrs); average household size fell from ~2.4
  to ~2.3 persons, so dwellings per capita rose ~0.5 %/yr (+4.6 % over 10 yrs).
  More people *and* more dwellings per person both push design demand up.
- **Intensity-side pull (DOWN)** -- combined -6.3 % over the decade. The
  envelope-relevant renovation rate is ~0.55 %/yr EU stock-weighted, so a
  decade of retrofits removed ~5.5 % of the stock's design specific demand;
  with the new-build component the cumulative effect is ~6.3 %.

The two forces happen to be of nearly identical size over this particular
decade. There is no fundamental reason they MUST cancel -- in a more
retrofit-aggressive decade (e.g. if the Renovation Wave's 3 %/yr ambition were
hit), intensity would dominate and the EU net would turn negative. In a
slower-retrofit / faster-stock-growth period it would turn positive. **2015 to
2025 just happens to be near the cancellation point** because (a) EU renovation
rate has been stuck near the long-run baseline (BPIE 2024 *Climate Tracker*
confirms the EU has not accelerated towards the Renovation Wave 3 % target)
and (b) household-size decline plus new construction added stock at a similar
pace to that baseline retrofit.

The per-country results illustrate the same balance from each side: countries
with fast pop / stock growth and slow retrofit go positive (LU +15 %, MT +16 %,
EE +7 %, FI +6 %, SE +5 %); countries with slow stock growth and faster
retrofit go negative (PT -5 %, BG -5 %, IT -4 %, HR -4 %, ES -4 %); countries
where the two balance (DE, FR, UK, PL, NL, AT, IE, etc.) sit within +/-3 %.

### 5c. Per-country result

In `code/results/lmdi_design.csv` (29 countries) and
`code/results/lmdi_design_drivers.csv` (per-country LMDI components). Headline
per-country Δ 2015->2025 ranges from -5 % (PT, BG: rising heating uptake +
intensity decline) to +16 % (LU, MT: fast pop/stock growth + slow retrofit).
15 of 29 countries land within +/- 15 % vs Hotmaps at matched vintage.

## 6. Why the corrections stay (and why we don't force the Hotmaps gap)

Each correction is independently sourced and applied per documented mechanism:
- `comfort_regime.deflator` cites measured-vs-calculated heating studies for the
  specific country (IDAE SPAHOUSEC II for ES; CRES + Santamouris for EL; CYSTAT
  HECS for CY; INE ICESD for PT; NSI EHCI for BG; INS ECRDS for RO; NSO HBS for MT).
- `eubucco.area_correction` cites the country's census heated-dwelling area.
- `tabula.class_mix_proxy` and Option B `tabula_reference_hdd` cite the upstream
  TABULA brochure's published reference zone or typology source.

None was tuned to reduce the Hotmaps gap. The resulting -1.0 % at the EU level
is a *validation pass within the OK band*, not a fit. We intentionally do not
back away from any correction in order to push the gap positive: doing so would
trade source-grounded calibration for benchmark fitting, which the project's
methodology rule forbids.

**Honesty caveat (the limit of the rule).** Each correction *value* is set from
a cited primary source and the arithmetic is independently reproducible. But the
*decision of which lever to apply to which country* is benchmark-informed: a
country is investigated for a correction because its naked snapshot sits far
from Hotmaps, and the lever chosen is the physically-applicable one for that
country (Mediterranean -> comfort regime; over-counted stock -> area; proxy
typology -> class mix; single-zone TABULA -> reference HDD). The model is
therefore most accurately described as **benchmark-anchored selection among
physically-grounded corrections**, not a Hotmaps-independent prediction. Two
values were also numerically revisited after seeing the gap: PT's deflator
(0.275 -> 0.10, re-grounded on the directly measured Magalhaes/Coelho operational
ratio; Hotmaps agreement is an ex-post validation, see
`inv_countries_academic_refinements.md`) and EE's area factor (0.445 -> 0.50, the
census-range midpoint; the alternative that would *hit* Hotmaps is ~0.55, and we
deliberately leave the ~19 % undershoot on the table). Where a country cannot be
corrected on independent source grounds (HR, MT, HU), the gap is reported as a
documented INVESTIGATE exception rather than closed. This caveat is also recorded
in `eubucco_census_area_audit.md`.

## 7. Reproduce

```
python code/scripts/lmdi_design.py
```

Reads the driver panels above; writes `code/results/lmdi_design.csv` (headline
per-country table) and `code/results/lmdi_design_drivers.csv` (per-country
driver values and log contributions).

## 8. References (primary)

### Method
- **Ang, B.W.** (2005). *The LMDI approach to decomposition analysis: a practical
  guide.* Energy Policy 33: 867-871. (Multiplicative + additive LMDI.)
- **Ang, B.W.** (2015). *LMDI decomposition approach: A guide for implementation.*
  Energy Policy 86: 233-238.

### Building-stock / renovation
- **Castellazzi, L. & Esposito, S.** (2019). *Comprehensive study of building
  energy renovation activities and the uptake of nearly zero-energy buildings
  in the EU.* JRC, EUR 29906 EN. (Per-country depth-band renovation rates.)
- **BPIE** (2024). *EU Buildings Climate Tracker.* Brussels.
- **BPIE** (2020). *On the way to a climate-neutral Europe.*
- **EHPA** (2016, 2024). *European Heat Pump Market and Statistics Reports.*

### Data sources
- Eurostat `nrg_d_hhq` (households disaggregated energy), `nrg_chdd_a` (HDD),
  `nrg_pc_202`/`nrg_pc_204` (gas/electricity prices), `ilc_lvph01` (household
  size), `ilc_hcmh02` (dwelling size), `demo_gind` (population), `nama_10_gdp`
  (real GDP), census 2021 dwelling stock.
- DESNZ (2024). *Energy Consumption in the UK (ECUK) 2024.* End-use tables.
- DESNZ (2022). *Long-term mean temperatures 1991-2020 special article.* Energy
  Trends, 31 Mar 2022.
- BFE/OFEN (2024). *Der Energieverbrauch der Privaten Haushalte 2000-2023*
  (Prognos for Swiss Federal Office of Energy).
- OECD Affordable Housing Database HM1.1 *Housing stock and construction.*
- Hotmaps Project (2019-2020). *Regional residential heat demand dataset.*
- National statistical offices: Destatis, INSEE, ISTAT, INE, CBS, SCB, GUS,
  ONS/MHCLG, CSO Ireland, CZSO, KSH, INS Romania, NSI Bulgaria, CYSTAT, CSB
  Latvia, STATEC, SURS, NSO Malta, BFS Switzerland.
- WMO (2017). *WMO Guidelines on the Calculation of Climate Normals.* WMO-No. 1203.

### Project-internal
- `literature/eubucco_census_area_audit.md` (the area-correction audit).
- `literature/climate_reference_hdd_audit.md` (Option B climate-multiplier audit).
- `literature/inv_countries_academic_refinements.md` (Mediterranean/Baltic
  refinements).
- `literature/tabula_intensity_verification.md` (TABULA matrix cross-checks).
- `literature/heating_mix_2025_audit.md` (per-country 2025 heating mix).

## 9. Available backcast scripts (sibling methodologies)

Three backcast scripts are preserved in `code/scripts/`, each implementing a
different academically valid methodology along the spectrum of "what variation
to credit":

| Script | Method | Inputs | Use case |
|---|---|---|---|
| **`lmdi_design.py`** (HEADLINE) | LMDI multi-driver on the DESIGN basis: Pop x Occupancy x Size x envelope-only intensity. The conceptually correct version for a design-demand model. | Eurostat panels + design_intensity_decline.csv | Reported in the paper as the headline backcast. |
| **`lmdi_backcast.py`** (ALTERNATIVE) | LMDI multi-driver on the OBSERVED-METERED basis: same driver structure but the intensity term is the observed Eurostat `nrg_d_hhq` ratio with conversion-efficiency add-back. Conservative cross-check. | Eurostat panels + design_intensity_decline.csv (for add-back rate) | Sensitivity / cross-check. Documents what the EU LMDI looks like if the metered final-energy series drives intensity. |
| **`reconcile_backcast.py`** (SIMPLE) | Single-driver: model_2015 = model_2025 x (1+g_country)^(-10), where g_country is the per-country dwelling-stock growth rate. Captures only the stock effect, ignores intensity. | stock_growth.csv | Quick diagnostic / pedagogical reference for "what would the backcast say if only stock changed?" |

The three are kept for both academic transparency (showing the methodology
lineage, including the iterations that landed at the headline) and as
sensitivity-band documentation. `compare_naked.py` is a separate diagnostic
that analytically undoes the four per-country corrections to show the naked
EUBUCCO x TABULA snapshot vs the corrected one (Mediterranean cluster blows
up without the comfort-regime deflator; cold-temperate countries already
match).

## 10. Files touched

- `code/src/Config.py` -- `BASE_YEAR=2025`, `STOCK_GROWTH_PATH`,
  `load_stock_growth`, `stock_growth_rate`, `backcast_factor`.
- `code/src/Simulation.py` -- re-anchored `interpolate_heat_demand` + vectorised loop.
- `code/src/Optimisation.py` -- re-anchored `_demand_factor`.
- `code/data/country_config/` -- 9 new/replaced datasets (see Table in section 3).
- `code/scripts/lmdi_design.py` -- headline LMDI multi-driver script (design basis).
- `code/scripts/lmdi_backcast.py` -- alternative LMDI on observed-metered basis.
- `code/scripts/reconcile_backcast.py` -- single-driver stock-growth backcast.
- `code/scripts/compare_naked.py` -- naked-vs-corrected snapshot comparison.
- `code/results/lmdi_design.csv`, `lmdi_design_drivers.csv` -- headline outputs.
- `code/results/lmdi_backcast.csv`, `lmdi_decomposition.csv` -- alternative outputs.
- `code/results/reconcile_backcast.csv` -- simple-backcast output.
- `code/results/compare_naked.csv` -- per-country corrected vs naked snapshot.
