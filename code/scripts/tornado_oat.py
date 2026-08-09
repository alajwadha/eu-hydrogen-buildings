"""The 2030 emissions tornado, computed rather than asserted.

The working paper carries a tornado table on 2030 buildings CO2 with three axes and six
bounds. Until now nothing in the repository produced it: no script ran the screen and no
CSV held the numbers, so a referee who tried to reproduce the table found nothing. That
is the exact defect class the numbers gate exists to catch, and a whole table had slipped
past it because the gate can only check values it has been told about.

This script runs the screen. It is a genuine one-at-a-time perturbation, not a rescaling
of the scenario ledger: each axis moves ALONE from the Stated Policies central setting,
every other lever is held, and the model is re-run end to end for that draw. The three
axes are the ones the table names.

  hydrogen price   H2_PRICE_TRAJECTORIES, RAPID (low) against STRANDED (high)
  ETS2 carbon      carbon-price scenario, HIGH (low emissions) against LOW (high)
  discount rate    the real WACC on annualised equipment capital, 0.03 against 0.09

Emissions FALL when hydrogen is cheap, when carbon is dear, and (weakly) when capital is
cheap, because each moves the levelised-cost ordering toward the low-carbon options and
the share allocation is cost-responsive. The sign convention in the table is therefore
"emissions-lowering bound" and "emissions-raising bound", not "low lever" and "high lever".

One draw, not a distribution. The tornado is a deterministic screen around the central
draw and is reported as such; the sampled bands are the Monte Carlo's job and are
reported separately. Using the median draw keeps the screen comparable with the
scenario ledger, which is also quoted at the median.

Run:  cd code && PYTHONPATH=. python -m scripts.tornado_oat
Out:  results/tornado_oat.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RESULTS = Path(__file__).resolve().parents[1] / "results"
YEAR = 2030
BASE_SCEN = "STATED_POLICIES"


def _run(carbon: str, h2: str, rate: float, stock, feas) -> float:
    """2030 EU buildings CO2 (MtCO2) for one deterministic central draw."""
    from src.Simulation import (scenario_from_config, sample_parameters,
                                run_single_sample, compute_emissions_df,
                                aggregate_emissions)
    scen = scenario_from_config(BASE_SCEN)
    # One fixed seed for every arm, so the only thing that differs between arms is the
    # axis under test. A fresh seed per arm would mix sampling noise into the screen and
    # the tornado would be measuring the rng as much as the lever.
    rng = np.random.default_rng(20260601)
    params = sample_parameters(scen, rng, carbon, h2, rate)
    sdf = run_single_sample(scen, params, stock, feas)
    sdf = compute_emissions_df(sdf, grid_mult=scen.grid_mult)
    em = aggregate_emissions(sdf)
    row = em[(em.year == YEAR) & (em.variable == "co2_MtCO2")]
    if row.empty:
        row = em[em.year == YEAR]
    return float(row["value"].sum())


def main() -> int:
    from src.Config import PROCESSED_DIR
    from src.Economics import DISCOUNT_RATE_REAL
    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    feas = pd.read_csv(PROCESSED_DIR / "hp_dh_feasibility_bottomup.csv")

    r0 = DISCOUNT_RATE_REAL
    base = _run("CENTRAL", "CENTRAL", r0, stock, feas)
    print(f"Tornado on {YEAR} buildings CO2, {BASE_SCEN}, central draw")
    print(f"  baseline = {base:.1f} MtCO2 (carbon CENTRAL, H2 CENTRAL, r={r0:.1%})\n")

    axes = [
        ("Hydrogen price", ("CENTRAL", "RAPID", r0, "rapid"),
                           ("CENTRAL", "STRANDED", r0, "stranded")),
        ("ETS2 carbon price", ("HIGH", "CENTRAL", r0, "high price"),
                              ("LOW", "CENTRAL", r0, "low price")),
        ("Discount rate", ("CENTRAL", "CENTRAL", 0.03, "low"),
                          ("CENTRAL", "CENTRAL", 0.09, "high")),
    ]
    rows = []
    for label, lo, hi in axes:
        vlo = _run(lo[0], lo[1], lo[2], stock, feas)
        vhi = _run(hi[0], hi[1], hi[2], stock, feas)
        dlo, dhi = vlo - base, vhi - base
        rows.append(dict(axis=label,
                         lowering_setting=lo[3], lowering_delta_mtco2=round(dlo, 1),
                         raising_setting=hi[3], raising_delta_mtco2=round(dhi, 1),
                         baseline_mtco2=round(base, 1), year=YEAR, scenario=BASE_SCEN))
        print(f"  {label:20s} {dlo:+6.1f} ({lo[3]})   {dhi:+6.1f} ({hi[3]})")

    df = pd.DataFrame(rows)
    df["span_mtco2"] = (df.raising_delta_mtco2 - df.lowering_delta_mtco2).round(1)
    df = df.sort_values("span_mtco2", ascending=False)
    df.to_csv(RESULTS / "tornado_oat.csv", index=False)
    print(f"\nranked by span: {', '.join(df.axis)}")
    print(f"Wrote {RESULTS / 'tornado_oat.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
