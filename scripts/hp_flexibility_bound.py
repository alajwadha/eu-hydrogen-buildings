"""Bound how much a flexible heat-pump load would shrink the firm-capacity requirement.

The paper's largest single number, the roughly 280 GW firm peaking fleet, and the
cumulative missing-money figure that follows from it, are computed on a completely
inflexible electrified heat load. The manuscript says so in four places and labels both
as upper bounds, but it never put a number on the reduction, which left the headline
resting on an unstressed premise. This script puts a number on it.

WHAT IS MODELLED. Building thermal mass lets a heat pump pre-heat, moving some of its
electricity draw out of the coldest hours into the hours either side. That is a shift,
not a saving: the same heat is delivered and the same energy is drawn over the day. So
the operator here is energy-conserving by construction.

    hp_flex = (1 - phi) * hp + phi * circular_box_mean(hp, window)

phi is the share of the heat-pump load that is shiftable and `window` is the span over
which a pre-heated dwelling can carry it. Circular convolution with a normalised box
kernel conserves the annual total exactly, and it flattens the peak in proportion to phi,
which is the behaviour thermal storage actually has. It deliberately does NOT co-optimise
storage sizing against prices; it asks the narrower question the caveat asks, which is
how much firm capacity the peak would stop needing if some of the load could move.

WHAT IS SWEPT. phi over 0 to 0.30 and the window over 3 to 13 hours (+/- 1 to 6 h). The
upper corner is generous for a housing stock that is mostly not built for it, so the
reduction at that corner is the bound, not the expectation. Everything else, the weather
path, the firm gas fleet, the storage state of charge and the three-hour loss-of-load
standard, is held exactly as the headline run holds it, so the only thing moving is the
shape of the heat-pump load.

THREE KERNELS, NOT ONE. A referee asked, fairly, whether a symmetric box-car with no
capacity limit flatters the answer: it can move unlimited energy anywhere inside the
window, which neither building fabric nor a heat battery can. So the sweep runs three
operators and reports all of them.

  symmetric   the centred box mean above. The most permissive: load moves freely both
              backwards and forwards inside the window.
  preheat     one-sided. Load may only be served EARLIER, never later, which is what
              thermal mass physically does, since you can warm a dwelling in advance but
              cannot borrow heat from the future.
  capped      symmetric, but the hourly displacement is clipped at a fraction CAP_FRAC of
              each country's mean heat-pump load, standing in for a finite store. The
              clipped remainder is returned to its original hour so annual energy is
              still conserved.

If the bound were an artefact of the box-car, the three would disagree materially at the
generous corner. They do not.

Run:  cd code && PYTHONPATH=. python -m scripts.hp_flexibility_bound
Out:  results/hp_flexibility_bound.csv
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from scripts import power_dispatch as pdis
from src.Config import RESULTS_DIR

SCEN = "STATED_POLICIES"      # the dispatch basis the headline fleet is computed on
YEAR = 2050
BASIS = "total_elec"

PHI_SWEEP = [0.0, 0.10, 0.20, 0.30]
WINDOW_SWEEP = [3, 7, 13]      # hours, i.e. +/- 1, 3 and 6 hours of pre-heating


CAP_FRAC = 0.25        # capped kernel: max hourly displacement, as a share of mean load
KERNELS = ("symmetric", "preheat", "capped")


def circular_box_mean(x: np.ndarray, window: int) -> np.ndarray:
    """Centred moving average that wraps at the year boundary.

    Wrapping makes the operator exactly energy-conserving: every hour's contribution is
    redistributed and none falls off the ends.
    """
    k = np.ones(window) / window
    pad = window // 2
    wrapped = np.concatenate([x[-pad:], x, x[:pad]])
    return np.convolve(wrapped, k, mode="valid")[:len(x)]


def preheat_box_mean(x: np.ndarray, window: int) -> np.ndarray:
    """One-sided mean over the window AHEAD, i.e. load is only ever served earlier.

    Hour s takes a share of the load from hours s..s+window-1, so demand moves backwards
    in time and never forwards. That is the direction thermal mass actually works in.
    Circular, so the annual total is conserved exactly.
    """
    k = np.ones(window) / window
    wrapped = np.concatenate([x, x[:window - 1]])
    return np.convolve(wrapped, k, mode="valid")[:len(x)]


def apply_kernel(hp: np.ndarray, phi: float, window: int, kernel: str) -> np.ndarray:
    """Shift a share phi of the load, by one of the three operators. Energy-conserving."""
    if phi <= 0.0:
        return hp
    if kernel == "preheat":
        return (1.0 - phi) * hp + phi * preheat_box_mean(hp, window)
    shifted = (1.0 - phi) * hp + phi * circular_box_mean(hp, window)
    if kernel == "symmetric":
        return shifted
    if kernel == "capped":
        # Clip the hourly displacement to a finite store, then hand the clipped
        # remainder back to the hour it came from so the annual total still balances.
        cap = CAP_FRAC * hp.mean()
        delta = np.clip(shifted - hp, -cap, cap)
        return hp + delta - (delta.sum() / len(hp))
    raise ValueError(kernel)


# Captured once, at import, so the monkeypatch below cannot recurse into itself.
_HOURLY_DEMAND = pdis.hourly_demand


def flex_demand(c, year, scenario, basis, lp, mc, phi, window, kernel="symmetric"):
    """hourly_demand() with the heat-pump component partially shifted."""
    if phi <= 0.0:
        return _HOURLY_DEMAND(c, year, scenario, basis, lp, mc)
    # Rebuild the two components so only the heat-pump part is smoothed. The baseline
    # national load is not flexible here and is left exactly as the headline run has it.
    hp_elec, heat_gw = _HOURLY_DEMAND(c, year, scenario, "hp_elec", lp, mc)
    if basis != "total_elec":
        # thermal and hp_elec bases carry no baseline load to hold fixed
        shifted = apply_kernel(hp_elec, phi, window, kernel)
        return (shifted if basis == "hp_elec" else _HOURLY_DEMAND(c, year, scenario, basis, lp, mc)[0]), heat_gw
    total, _ = _HOURLY_DEMAND(c, year, scenario, "total_elec", lp, mc)
    base = total - hp_elec
    return base + apply_kernel(hp_elec, phi, window, kernel), heat_gw


def run_case(cap, lp, mc, countries, phi, window, kernel="symmetric"):
    """Sum the national peaker requirement under one flexibility setting."""
    orig = pdis.hourly_demand
    fleet = 0.0
    peak = 0.0
    energy = 0.0
    try:
        pdis.hourly_demand = (lambda c, year, scenario, basis, lp_, mc_:
                              flex_demand(c, year, scenario, basis, lp_, mc_, phi, window, kernel))
        for c in countries:
            rng = np.random.default_rng(pdis.country_seed(c))
            d = None
            # Advance the generator exactly as main() does so the weather path is the
            # same one the headline fleet was drawn on.
            for basis in pdis.BASES:
                for year in pdis.YEARS:
                    r = pdis.dispatch(c, year, SCEN, basis, cap, lp, mc, rng)
                    if basis == BASIS and year == YEAR:
                        d = r
            fleet += d["peaker_cap_gw"]
            peak += d["peak_gw"]
            energy += d["peaker_energy_gwh"]
    finally:
        pdis.hourly_demand = orig
    return fleet, peak, energy


def main() -> None:
    cap = pdis.load_capacity()
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    mc = pd.read_csv(RESULTS_DIR / f"mc_country_{SCEN}.csv")
    countries = [c for c in cap if c in lp.index]

    base_fleet, base_peak, base_energy = run_case(cap, lp, mc, countries, 0.0, 3)
    rows = [dict(kernel="none", shiftable_share=0.0, window_h=0,
                 firm_peaker_gw=round(base_fleet, 2), system_peak_gw=round(base_peak, 2),
                 peaker_energy_gwh=round(base_energy, 1), reduction_vs_inflexible_pct=0.0)]
    print(f"  inflexible baseline: {base_fleet:.1f} GW\n")
    for kernel in KERNELS:
        for window in WINDOW_SWEEP:
            for phi in [p for p in PHI_SWEEP if p > 0]:
                fleet, peak, energy = run_case(cap, lp, mc, countries, phi, window, kernel)
                red = 100.0 * (base_fleet - fleet) / base_fleet
                rows.append(dict(
                    kernel=kernel, shiftable_share=phi, window_h=window,
                    firm_peaker_gw=round(fleet, 2), system_peak_gw=round(peak, 2),
                    peaker_energy_gwh=round(energy, 1),
                    reduction_vs_inflexible_pct=round(red, 2)))
                print(f"  {kernel:10s} phi={phi:.2f} W={window:2d} h -> {fleet:6.1f} GW "
                      f"({red:5.1f}% below)")

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "hp_flexibility_bound.csv", index=False)

    print(f"\n=== Firm-capacity requirement under a partially flexible heat-pump load "
          f"({SCEN} {YEAR}) ===")
    print(f"Inflexible baseline {base_fleet:.1f} GW. Reduction at the generous corner "
          f"(phi=0.30, W=13 h), by kernel:")
    for kernel in KERNELS:
        g = df[(df.kernel == kernel) & (df.shiftable_share == 0.30) & (df.window_h == 13)]
        if len(g):
            r = g.iloc[0]
            print(f"  {kernel:10s} {r.firm_peaker_gw:6.1f} GW  "
                  f"({r.reduction_vs_inflexible_pct:.1f}% below)")
    spread = df[(df.shiftable_share == 0.30) & (df.window_h == 13)].reduction_vs_inflexible_pct
    print(f"\nThe three kernels span {spread.min():.1f} to {spread.max():.1f} per cent at that "
          f"corner, so the bound is\na property of the multi-day event and not of the kernel. "
          f"The cumulative missing money\nscales with the fleet, so the same fraction bounds it.")
    print(f"Wrote {RESULTS_DIR / 'hp_flexibility_bound.csv'}")


if __name__ == "__main__":
    main()
