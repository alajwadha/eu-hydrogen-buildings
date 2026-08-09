"""Firm peaking fleet under each scenario's own 2050 electricity demand path.

power_dispatch builds one physical fleet, on the Stated Policies demand path, and then
reprices that same fleet under all four economic scenarios. That is a defensible design,
since the supply stack and the weather year are held fixed and only fuel and carbon move,
but it leaves a reader unable to tell how much of the 278 GW is the demand path rather
than the dispatch logic. This module answers exactly that question and nothing more.

It re-runs the committed dispatch with each scenario's own mc_country file in place of the
Stated Policies one, holding the supply stack, the constructed weather year, the sizing
rule and every cost assumption fixed. So this is a demand-path sensitivity, not four
scenario power systems: a genuine scenario-specific supply transformation would need new
capacity assumptions this repository does not carry.

Two things about the arithmetic are easy to get wrong and were.

The RNG is created once per country in power_dispatch.main and then consumed across the
whole basis-by-year loop, so the VRE availability draw at total_elec/2050 depends on every
call before it. Calling dispatch once per country in isolation gives a different and wrong
answer: 296.8 GW for Stated Policies against the committed 277.7. This module therefore
walks BASES and YEARS in the same order and reads off the same cell, which reproduces the
committed fleet exactly and is the check that the sensitivity is measuring what it claims.

The fleet is a sum over countries and the full-load hours are the fleet-weighted ratio of
summed energy to summed capacity, not a mean of per-country ratios.

Run:  cd code && PYTHONPATH=. python -m scripts.power_demand_path_sensitivity
Out:  results/power_demand_path.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts import power_dispatch as pdz

YEAR = 2050
BASIS = "total_elec"


def fleet_on(scenario: str, cap: dict, lp: pd.DataFrame, countries: list) -> dict:
    """Summed peaking fleet and fleet full-load hours on one scenario's demand path."""
    mc = pd.read_csv(pdz.RESULTS_DIR / f"mc_country_{scenario}.csv")
    tot_cap = tot_energy = 0.0
    for c in countries:
        # Same construction and same consumption order as power_dispatch.main, or the
        # weather draw lands elsewhere in the stream and the fleet comes out wrong.
        rng = np.random.default_rng(pdz.country_seed(c))
        for basis in pdz.BASES:
            for year in pdz.YEARS:
                d = pdz.dispatch(c, year, scenario, basis, cap, lp, mc, rng)
                if basis == BASIS and year == YEAR:
                    tot_cap += d["peaker_cap_gw"]
                    tot_energy += d["peaker_energy_gwh"]
    return {"scenario": scenario,
            "peaker_fleet_gw": round(tot_cap, 1),
            "peaker_energy_gwh": round(tot_energy, 1),
            "peaker_flh": round(tot_energy / tot_cap)}


def main() -> int:
    cap = pdz.load_capacity()
    lp = pd.read_csv(pdz.RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    countries = [c for c in cap if c in lp.index]

    rows = [fleet_on(s, cap, lp, countries) for s in pdz.SCEN]
    df = pd.DataFrame(rows)
    df.to_csv(pdz.RESULTS_DIR / "power_demand_path.csv", index=False)

    print(f"Firm peaking fleet at {YEAR} on each scenario's own demand path")
    print(df.to_string(index=False))

    sp = df[df.scenario == "STATED_POLICIES"].iloc[0]
    lo, hi = df.peaker_fleet_gw.min(), df.peaker_fleet_gw.max()
    print(f"\nRange {lo:.0f} to {hi:.0f} GW; Stated Policies {sp.peaker_fleet_gw:.0f} GW "
          f"at {sp.peaker_flh:.0f} full-load hours")
    # The published fleet is the Stated Policies row. If this stops reproducing it, the
    # sensitivity is no longer anchored on the same dispatch and must not be reported.
    committed = pd.read_csv(pdz.RESULTS_DIR / "power_dispatch_summary.csv")
    ref = committed[(committed.basis == BASIS) & (committed.year == YEAR)].peaker_cap_gw.sum()
    if abs(ref - sp.peaker_fleet_gw) > 0.5:
        raise SystemExit(f"Stated Policies row {sp.peaker_fleet_gw} GW does not reproduce "
                         f"the committed {ref:.1f} GW; the RNG order has probably drifted")
    print(f"reproduces the committed Stated Policies fleet ({ref:.1f} GW)")
    print(f"\nWrote {pdz.RESULTS_DIR / 'power_demand_path.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
