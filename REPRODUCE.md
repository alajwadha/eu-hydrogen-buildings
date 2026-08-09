# Reproducing the results

This document gives the exact, end-to-end path to reproduce every headline
number, figure and the dashboard from a clean checkout. The pipeline has two
halves: the **per-country bottom-up build** (heavy; EUBUCCO download +
classification; run on Google Colab, once per country group) and the **forward
model** (light; runs locally in one command from the committed per-country
outputs).

## 0. Environment

- Python 3.10+ (matching `requirements.txt` and the README); `pip install -r requirements.txt` (pandas, numpy, pyyaml,
  pyarrow, matplotlib, pulp). CBC ships with PuLP.
- Repo: `github.com/alajwadha/eu-hydrogen-buildings`, branch `main`.

## 1. Per-country bottom-up build (Colab, only when inputs change)

Scripts `code/scripts/country_build/{01_download,02_classify,03_heat_intensity,
04_diagnostics}.py`, driven by one YAML per country
(`code/data/country_config/{cc}.yaml`). They are resume-safe: a country whose
`code/data/processed/{cc}/{CC}_heat_intensity_summary.csv` already exists in the
repo is skipped. To force a rebuild after changing a country's inputs, delete
that country's `code/data/processed/{cc}/` outputs, then run its group notebook:

| Group | Countries | Colab notebook |
|---|---|---|
| G1 | DE + Baltics (EE, LV, LT) | notebooks/group1_de_baltics.ipynb |
| G2 | IT, SI, HR, MT | notebooks/group2_it_adriatic.ipynb |
| G3 | ES, PT, EL, CY | notebooks/group3_iberian_aegean.ipynb |
| G4 | PL, CZ, SK, HU | notebooks/group4_visegrad.ipynb |
| G5 | AT, BE, NL, IE | notebooks/group5_northwest.ipynb |
| G6 | SE, DK, BG, RO | notebooks/group6_nordic_se.ipynb |
| G7 | UK, CH | notebooks/group7_uk_ch.ipynb |
| -- | FR, FI, LU | france / finland / luxembourg .ipynb |

Colab URL pattern:
`https://colab.research.google.com/github/alajwadha/eu-hydrogen-buildings/blob/main/notebooks/<name>.ipynb`

Each notebook commits the rebuilt `{CC}_heat_demand_nuts3.csv` (+ summary,
reconciliation, diagnostics) back to `main`. A normal Colab runtime suffices
(Italy is the heaviest, a few hours).

A single per-country run can also be reproduced locally **if** that country's
classified parquet is present. No parquet is committed to this repository, so the
parquet has to come from a prior local run of scripts 01-02 (or from the Drive
archive); the LU summary CSVs and diagnostic PDF are committed, the LU parquets are not:
`python code/scripts/country_build/03_heat_intensity.py --country LU`
Add `--no-corrections` to write the uncorrected (`*_naked`) outputs for the
correction-attribution diagnostic.

## 2. Forward model (local, one command)

After the per-country outputs are in the repo, regenerate everything downstream:

```
cd code && PYTHONPATH=. python -m scripts.rebuild_local
```

This runs, in order: re-aggregate `building_stock_nuts3_bottomup.csv` +
feasibility -> Monte Carlo over the four policy scenarios (`src.Simulation`) -> COST_OPT
LP (`src.Optimisation`) -> grid / rho / H2-gap sensitivities -> all 30 figures ->
the LMDI dashboard. Use `--skip-figs` to stop after the result CSVs.

Determinism: the Monte Carlo seed is `Config.RNG_SEED = 42` and
`N_MONTE_CARLO_SAMPLES = 200`. Medians are MC-noise-stable to ~+/-0.3 pp; bands
depend on the documented structural knobs `INTENSITY_RATE_CORR = 0.5`
(renovation correlation) and `FUEL_PRICE_CORR = 0.75` (fuel-price correlation).

```
cd code && PYTHONPATH=. python -m scripts.mc_convergence   # is N = 200 enough?
```

This reads the persisted per-draw values in `results/mc_draws_*.csv` and writes
`results/mc_convergence.csv` plus the SI convergence figure. It reports, for each
scenario, the last draw at which a running quantile still sits outside a +/-1% tube
around its value at N = 200. The running median last leaves at draw 41, 48, 96 and 139
across the four scenarios, and the running 10th percentile only at 156 to 188, which is
why the supplements read the medians as converged and the deciles as indicative. Note the
convention: a running quantile can re-enter the tube and leave again, so this is the last
exit and not the first entry, and reporting first entry would flatter every series.

## 3. Validation / backcast

```
cd code && PYTHONPATH=. python -m scripts.make_validation_table  # the figures the papers quote
cd code && PYTHONPATH=. python -m scripts.lmdi_design        # 2015 vintage-matched reconciliation
cd code && PYTHONPATH=. python -m scripts.reconcile_backcast
```

`make_validation_table` writes `results/bottomup_validation.csv`, and it is the source of
the validation numbers the manuscripts actually state: an EU raw deviation of -0.8% and a
vintage-matched -8.3%, with 19 of 29 countries inside +/-15% and 28 of 29 inside +/-25%.
It also writes `results/bottomup_validation_metrics.csv`, the country-level error
dispersion on both bases: on the raw basis a MAPE of 11.6%, a demand-weighted MAPE of
9.8%, an RMSE of 14.4 percentage points and a median absolute error of 8.5%, and on the
vintage-matched basis 12.4, 10.7, 15.2 and 9.6. The counts and the -0.8% aggregate are
raw-basis quantities, so do not read a vintage-matched dispersion figure against them.
It was missing from this guide entirely, so the paper's most-cited validation result had no
documented reproduction path while two adjacent tables that compute different things did.
These two commands produce two different 2015 comparisons, and a number from one does not
transfer to the other.

`lmdi_design.csv` backcasts the whole design decomposition, so population, occupancy,
dwelling size and envelope intensity all move and very nearly cancel: its EU row reads
3,825.3 TWh for 2015 against Hotmaps 3,863.1, a gap of **-1.0%**, and only +0.1% of change
between 2015 and 2025. `reconcile_backcast.csv` applies stock growth alone with no envelope
term to offset it, so its `EU(sum)` row reads -8.5% vintage-matched against -0.9% raw (the
raw column compares the 2025 snapshot to Hotmaps 2015 and is not vintage-matched at all).
Both sit inside the +/-15% band and neither is Hotmaps-fitted.

This paragraph previously said -8.7% and -1.2%. Those came from a committed
`reconcile_backcast.csv` that was stale against its own script: its EU snapshot read
3,818.9 TWh, where a rerun gives 3,827.4, which is what `benchmark_multi.csv` (3,827.5) and
the manuscripts (3,827 TWh) both carry. Hungary moved most, from 59.5 to 68.1 TWh, which
also moved its verdict from ACC to OK. Re-run this table whenever the per-country build
outputs change; the numbers gate reads the live file and will flag the documentation.

The two tables also take their Hotmaps column from different places: `reconcile_backcast`
sums the NUTS3 surface, `benchmark_multi` uses the per-country configured residential
baseline. Sweden reads 99.4 against 85.0 TWh between them, Romania 74.2 against 82.0 and
Bulgaria 26.8 against 29.0. The manuscripts quote the harmonised all-class basis, -0.8% raw
and -8.3% vintage-matched, and the SI says in as many words that the committed backcast
table reads a slightly different figure on its own basis, now -8.5%. Match the benchmark basis before comparing any two of
these figures.

## 4. Input manifest (key data + provenance)

| Input | File / source | Version / vintage |
|---|---|---|
| Building footprints | EUBUCCO v0.2 (Milojevic-Dupont et al. 2023) | v0.2, ~2020-2023 snapshot |
| Building typology intensities | TABULA/EPISCOPE national brochures, `code/data/raw/tabula/*.csv` | 17 typology files for 29 countries. **12 countries use another country's typology** (BG←CZ, CH←AT, EE←PL, FI←SE, HR←SI, LT←PL, LU←BE, LV←PL, MT←CY, PT←ES, RO←CZ, SK←CZ), each recorded in `tabula.source_country` in that country's `code/data/country_config/*.yaml`. HU = BME 2014. |
| HDD climate | Eurostat `nrg_chdd_a` / `nrg_chddr2_a`; WMO normal 1991-2020 | 2018-2022 mean (corrections); 30-yr normal (LMDI) |
| Validation benchmark | Hotmaps regional heat demand | 2015 |
| Census floor area | national stats offices (INE, ISTAT, Destatis, ...) | per-country, 2011/2021 |
| Population projection | EUROPOP2023 (`proj_19np`), ONS 2022-based, BFS A-00-2025 | `pop_projection.csv` |
| Household size | Eurostat `ilc_lvph01` | 2015-2023 trend |
| Scenario envelope rates | `code/data/country_config/scenario_intensity_rates.csv` | per-country x per-scenario |
| Techno-economics (CAPEX/COP) | DEA Technology Data 2023; EHPA 2024; JRC | `code/src/Economics.py` |
| Fuel prices | Eurostat `nrg_pc_202/204` H1 2025; OIES ET32 H2 trajectory | 2025 base + multipliers |
| Grid carbon intensity | EMBER 2024 actuals; EEA Fit-for-55 projections | `code/src/Policy.py` |
| Installed power capacity (the whole power arena rests on this) | NECP/TYNDP-anchored, assembled by `code/scripts/build_power_capacity.py`, which tags every row `anchored`/`necp`/`proxy` | `code/data/power_capacity.csv`; a curated scenario, not a published dataset |
| EU Building Stock Observatory intensities | BSO 2022, one file per country, used as a reconciliation benchmark | `code/data/raw/eu_bso/{cc}_intensity.csv` |
| Salt-cavern storage classification | Mapped potential of Caglayan et al. 2020, applied as a binary with no working-volume threshold of our own; the two storage rates (EUR 1.5/3.0 per kg) are this study's assumption | `CAVERN` in `code/scripts/merit_order_heat.py`; tabulated per country by `code/scripts/storage_geology.py` |
| Retrofit cost | Ipsos/Navigant 2019 medium depth (EUR 154/m2, 41% saving); JRC EUR 29906 EN | wired into the least-cost LP as one depth: `Optimisation.retrofit_cost_per_mwh`. A depth *curve*, so the LP could choose depth endogenously, is not implemented |

Methodology detail: `literature/temporal_backcast_methodology.md`,
`cost_optimisation_methodology.md`, `eubucco_census_area_audit.md`,
`climate_reference_hdd_audit.md`, `inv_countries_academic_refinements.md`,
`tier1_tier2_modelling_extensions.md`.

## 5. Known reproduction caveats

- A few legacy outputs (FR/FI/LU) predate the per-NUTS3 emission column; their
  notebooks should be re-run if `building_stock_nuts3_bottomup.csv` warns about
  missing countries.
- The classified parquets (`{CC}_buildings_classified.parquet`) are large and
  archived on Drive. None is committed, for any country, and `.gitignore` excludes
  them repo-wide. Full per-country reproduction therefore requires the Colab step
  (Section 1) or a local run of scripts 01-02.
- COST_OPT requires PuLP/CBC; the Monte Carlo does not.
