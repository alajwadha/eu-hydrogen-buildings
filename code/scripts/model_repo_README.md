# EU hydrogen buildings model

The techno-economic model behind *Hydrogen in residential heating and the power system: a
merit-order and capital-recovery assessment for 29 European markets*.

It reconstructs residential useful heat demand for the EU-27, the United Kingdom and
Switzerland at NUTS3 resolution, prices eight heating technologies on a levelised basis,
and then runs three tests in order: a levelised-cost comparison, an operating-cost merit
order across three arenas, and a standalone capital-recovery test for a hydrogen peaker.

## What is here, and what is not

This repository holds the **model and the code needed to run it**. It does not carry the
manuscript, the figures, the results, or any third-party dataset.

    src/                model
    scripts/            data retrieval and the hourly heat-load profile
    data/country_config/ our own per-country assumptions, 29 YAML files
    run.py              single entry point
    requirements.txt    Python dependencies

Input data is **fetched, not bundled**. `scripts/download_data.py` retrieves it from the
original providers, so nobody redistributes Eurostat, Hotmaps, EUBUCCO, GISCO or EMBER
data under a licence that is not theirs to grant, and every run is traceable to the
provider's own copy.

Results are not committed either. They reproduce from the code and the fetched inputs.

## Running it

    python3 -m pip install -r requirements.txt
    python3 run.py --scenario ALL

The first run downloads the source datasets, which takes a while and needs network access.
Afterwards, `--skip-download` reuses what is on disk.

Useful switches:

| Switch | Effect |
|---|---|
| `--scenario` | `CURRENT_POLICIES`, `STATED_POLICIES`, `NET_ZERO`, `H2_PUSH`, `COST_OPT`, `ALL` |
| `--carbon` | `LOW`, `CENTRAL`, `HIGH` carbon-price path |
| `--h2` | `RAPID`, `CENTRAL`, `SLOW`, `STRANDED` hydrogen-price path |
| `--demand` | `hotmaps` or `bottomup` demand reconstruction |
| `--sensitivity` | run the sensitivity sweeps |

## Two things worth knowing before you read the output

**The power layer runs on one synthetic weather year.** Hourly heat demand is a seasonal
profile times a fixed daily shape, amplified over a single six-day cold snap; wind is an
AR(1) process forced to a lull over those same days in all 29 countries at once. Every
firm-capacity and capital-recovery number descends from that construction. It is a screen,
not an adequacy assessment.

**Two input trajectories do a lot of work and are assumptions rather than projections.**
The carbon-price paths in `src/Policy.py` and the real-terms retail fuel-price multipliers
in `src/Economics.py` set, respectively, which markets hydrogen wins on the power peak and
how wide the base-load margins are. Both are documented in the paper's Supplementary
Information and both are worth changing before trusting a number.

## Licence

MIT. See `LICENSE`.

## Authors

Abdurahman Alsulaiman, Laboratory of Environmental and Urban Economics (LEURE), EPFL, Switzerland
Ali Alajwad, RENEW Lab, Johns Hopkins University, and Cornell University

Access to anything not in this repository is available from the authors on request.
