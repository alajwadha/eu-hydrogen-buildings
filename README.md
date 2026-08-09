# EU hydrogen buildings model

A bottom-up techno-economic model of residential heat decarbonisation across the EU-27,
the United Kingdom and Switzerland, 2025 to 2050.

Useful heat demand is reconstructed from NUTS3 building stock and aggregated to the
country before any cost test, then carried through eight heating technologies and four
scenarios in a Monte Carlo. Hydrogen is tested against heat-pump electrification three
ways: on levelised cost of delivered heat, on winter-peak merit order across the
building, district-heat and power arenas, and on whether a hydrogen peaker recovers its
capital from market rent.

This repository holds the model and its inputs. It does not hold the manuscripts, the
figures or the committed model outputs; every result in the papers is reproducible from
what is here.

## Layout

| Path | What it is |
|---|---|
| `src/` | the model: building stock, economics, emissions, policy, dispatch, the least-cost programme |
| `scripts/` | the analysis steps and sensitivity sweeps that run on top of the model |
| `scripts/country_build/` | the per-country bottom-up build, from building footprints to heat intensity |
| `data/raw/` | third-party inputs as downloaded |
| `data/processed/` | the intermediate tables the forward model runs from |
| `data/country_config/` | per-country archetype typology, climate and stock settings |
| `run.py` | one entry point for the whole pipeline |

## Running it

```
pip install -r requirements.txt
python run.py --scenario ALL
```

Useful switches: `--scenario CURRENT_POLICIES|STATED_POLICIES|NET_ZERO|H2_PUSH|COST_OPT|ALL`,
`--demand hotmaps|bottomup`, `--carbon LOW|CENTRAL|HIGH`, `--h2 RAPID|CENTRAL|SLOW|STRANDED`,
`--skip-download` to run from the cached inputs, `--sensitivity` for the sweeps.

Individual analysis steps run as modules from this directory, for example:

```
PYTHONPATH=. python -m scripts.power_dispatch
PYTHONPATH=. python -m scripts.capacity_payment
```

## Inputs

Most third-party data is retrieved by `scripts/download_data.py` (Hotmaps, Eurostat,
GISCO). Two are not automatic. The UK ONS TS044 accommodation-type table is a one-time
manual download and is committed here. The EUBUCCO v0.2 building footprints that drive
the bottom-up demand basis are fetched from the EUBUCCO object store by the per-country
build scripts; the forward model runs from the committed intermediate tables without
them, and only reproducing the bottom-up build from raw footprints needs that step.

## Authors

Abdurahman Alsulaiman and Ali Alajwad.

## Licence

MIT. See `LICENSE`.
