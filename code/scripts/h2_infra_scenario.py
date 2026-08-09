"""H2 distribution-infrastructure scenarios: what the H2-boiler LCOH and the
H2-vs-heat-pump gap become when hydrogen must pay for its distribution network,
instead of reusing the existing gas grid for free.

The default model (BASELINE) assumes free reuse of the gas grid: the H2-boiler
LCOH carries no distribution-infrastructure cost. We add two network scenarios,
each annualised at the country WACC over a 40-yr network life and divided by
~13 MWh useful/dwelling (Economics.h2_distribution_adder_eur_mwh):

  RETROFIT  (mode="convert")  -- repurpose the WHOLE existing gas grid to 100% H2
                                 at the conversion cost for every dwelling.
                                 Optimistic lower bound.
  NEW-BUILD (mode="newbuild") -- build a dedicated H2 distribution network from
                                 scratch to every dwelling. Upper bound.
  (BLEND    (mode="blend")    -- coverage-weighted mix, reported as the central
                                 per-country case for reference.)

Crucially, the per-connection capital cost is UNCERTAIN, so each scenario is a
SENSITIVITY BAND, not a point: per-dwelling conversion = EUR 1,000 / 1,500 / 3,000
(low/central/high) and new-build = EUR 3,000 / 5,000 / 8,000. We therefore report
the gap as central [low-high] for each scenario.

Sources for the per-connection figures are documented in Economics.py (UK H21 /
Northern Gas Networks; HyDeploy; Frazer-Nash / Element Energy for BEIS; Gas for
Climate / Guidehouse 2020 European Hydrogen Backbone).

Run:  cd code && PYTHONPATH=. python -m scripts.h2_infra_scenario
Out:  code/results/h2_infra_scenario.csv + console
"""
from __future__ import annotations

import pandas as pd

import src.Policy as P
from src.Config import RESULTS_DIR
from src.Economics import compute_lcoh, h2_distribution_adder_eur_mwh

COUNTRIES = ["AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EE", "EL", "ES",
             "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL",
             "PL", "PT", "RO", "SE", "SI", "SK", "UK"]

MODES = ["convert", "blend", "newbuild"]
BOUNDS = ["low", "central", "high"]


def main() -> None:
    rows = []
    for c in COUNTRIES:
        try:
            # This script sweeps the H2 distribution adder itself, so it must start
            # from an LCOH that does NOT already carry one. compute_lcoh now applies
            # the blend adder by default; pass h2_infra=False here or every row would
            # count the network twice. The heat-pump side keeps the reinforcement
            # adder, which is the symmetric charge and is not what this sweep varies.
            hp = min(compute_lcoh("hp_air", c, 2050),
                     compute_lcoh("hp_ground", c, 2050))
            h2_base = compute_lcoh("h2_boiler", c, 2050, h2_infra=False)
        except Exception as e:
            print(f"  [skip] {c}: {e}")
            continue
        row = {
            "country": c,
            "gas_grid_cov": round(P.GAS_GRID_COVERAGE.get(c, 0.30), 2),
            "best_hp_2050": round(hp, 1),
            "h2_2050_baseline": round(h2_base, 1),
            "gap_baseline": round(h2_base - hp, 1),
        }
        # adder + gap for each (mode, bound): the sensitivity band per scenario
        for m in MODES:
            for b in BOUNDS:
                add = h2_distribution_adder_eur_mwh(c, mode=m, bound=b)
                row[f"adder_{m}_{b}"] = round(add, 1)
                row[f"gap_{m}_{b}"] = round(h2_base + add - hp, 1)
        rows.append(row)

    df = pd.DataFrame(rows).sort_values("gap_newbuild_central")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "h2_infra_scenario.csv", index=False)

    # Console: per-country gap as central [low-high] for the two end-member scenarios
    def band(r, m):
        return f"{r[f'gap_{m}_central']:.0f} [{r[f'gap_{m}_low']:.0f}-{r[f'gap_{m}_high']:.0f}]"
    print(f"{'ctry':<5}{'cov':>5}{'baseline':>10}   {'RETROFIT gap':>18}   {'NEW-BUILD gap':>18}")
    print(f"{'':5}{'':5}{'(free)':>10}   {'central [low-high]':>18}   {'central [low-high]':>18}")
    for _, r in df.iterrows():
        print(f"{r.country:<5}{r.gas_grid_cov:>5.2f}{r.gap_baseline:>10.0f}   "
              f"{band(r,'convert'):>18}   {band(r,'newbuild'):>18}")

    def parity(col):
        return int((df[col] <= 0).sum())
    print("\nPer-connection cost band -> adder band (EUR/MWh_useful), EU range:")
    print(f"  RETROFIT/convert  central {df.adder_convert_central.min():.0f}-"
          f"{df.adder_convert_central.max():.0f}  "
          f"(low {df.adder_convert_low.min():.0f}-{df.adder_convert_low.max():.0f}, "
          f"high {df.adder_convert_high.min():.0f}-{df.adder_convert_high.max():.0f})")
    print(f"  NEW-BUILD         central {df.adder_newbuild_central.min():.0f}-"
          f"{df.adder_newbuild_central.max():.0f}  "
          f"(low {df.adder_newbuild_low.min():.0f}-{df.adder_newbuild_low.max():.0f}, "
          f"high {df.adder_newbuild_high.min():.0f}-{df.adder_newbuild_high.max():.0f})")
    print("\nCountries at heat-pump parity (gap<=0) in 2050, central / low / high:")
    print(f"  BASELINE (free grid)  : {parity('gap_baseline')}")
    for m in ["convert", "blend", "newbuild"]:
        print(f"  {m:<20}: {parity(f'gap_{m}_central')} / "
              f"{parity(f'gap_{m}_low')} / {parity(f'gap_{m}_high')}")
    print("\nEU-mean H2-HP gap (EUR/MWh), central [low-high]:")
    print(f"  baseline {df.gap_baseline.mean():.0f}")
    for m in ["convert", "blend", "newbuild"]:
        print(f"  {m:<10}: {df[f'gap_{m}_central'].mean():.0f} "
              f"[{df[f'gap_{m}_low'].mean():.0f}-{df[f'gap_{m}_high'].mean():.0f}]")
    print(f"\nWrote {RESULTS_DIR / 'h2_infra_scenario.csv'}")


if __name__ == "__main__":
    main()
