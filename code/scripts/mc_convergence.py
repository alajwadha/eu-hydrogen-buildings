"""Running-quantile convergence of the scenario Monte Carlo, and the SI figure for it.

The supplement states how many draws the headline 2050 CO$_2$ median needs before it
stays inside a one-per-cent tube, and it states that the deciles never get there at
N=200. Those are claims about what the sampler did, and they were typed into the prose
with no committed derivation behind them: no script produced them, no CSV carried them
and no gate compared them with anything. They happened to be right, which is the worst
version of that situation, because nothing would have caught them going wrong.

The convention matters and is easy to get backwards. A running quantile can wander back
out of the tube after entering it, so "converged after k draws" is not the first entry.
It is the LAST exit: the largest draw at which the running quantile still sits outside
the tube. Reporting first entry would flatter every series, in one case by more than a
hundred draws. The tube is centred on the N=200 value of the same series, so this is a
self-consistency diagnostic and not a claim that N=200 is the population value.

The deciles are reported as unconverged and that is a property of the estimator rather
than of this run. At N=200 the 10th percentile is the 20th order statistic, whose exact
nonparametric 95 per cent interval spans the 12th to the 29th, so it locates the
population decile only to somewhere between the 6th and the 15th percentile. That
interval is computed here too, from the binomial, rather than asserted.

Run:  cd code && PYTHONPATH=. python -m scripts.mc_convergence
Out:  results/mc_convergence.csv
      paper/figs/paper/P42_mc_convergence.{png,pdf}
"""
from __future__ import annotations
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from scripts._figstyle import set_style, PALETTE, short_scen

set_style()

RES = Path(__file__).resolve().parents[1] / "results"
FIGDIR = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"

SCENARIOS = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
VARIABLE = "co2_MtCO2"
YEAR = 2050
TUBE = 0.01          # the one-per-cent tube the supplement quotes
QUANTILES = [(50, "median"), (10, "p10"), (90, "p90")]


def draws(scenario: str) -> np.ndarray:
    """The headline 2050 CO2 metric, one value per Monte Carlo draw, in draw order."""
    d = pd.read_csv(RES / f"mc_draws_{scenario}.csv")
    s = d[(d.variable == VARIABLE) & (d.year == YEAR)].sort_values("sample")
    if s.empty:
        raise SystemExit(f"mc_draws_{scenario}.csv carries no {VARIABLE} at {YEAR}")
    return s["value"].to_numpy(dtype=float)


def running(s: np.ndarray, q: float) -> np.ndarray:
    """The quantile recomputed on the first k draws, for every k."""
    return np.array([np.percentile(s[:k], q) for k in range(1, len(s) + 1)])


def last_exit(run: np.ndarray, tube: float = TUBE) -> int:
    """Largest draw at which the running quantile is still outside the tube.

    Zero means it never left, which for a one-draw series cannot happen, so zero here
    would signal a degenerate input rather than instant convergence.
    """
    outside = np.abs(run / run[-1] - 1.0) > tube
    return int(np.max(np.nonzero(outside)[0])) + 1 if outside.any() else 0


def order_statistic_interval(n: int, q: float, conf: float = 0.95) -> tuple[int, int]:
    """Exact nonparametric interval for the population q-quantile, as order statistics.

    The number of draws below the population quantile is Binomial(n, q), so the interval
    is that distribution's tail pair. This is what makes the reported deciles indicative:
    it is a property of N, and no amount of rerunning this particular sample changes it.

    Coverage of [X_(r), X_(s)] is P(r <= B <= s-1) for B ~ Binomial(n, q), so the upper
    order statistic is the 0.975 quantile itself. Adding one to it, which looks like the
    natural off-by-one correction, widens the interval to 96.7 per cent and overstates
    how badly the decile is pinned. The realised coverage is returned so the caller can
    assert it rather than trust the construction.
    """
    p = q / 100.0
    lo = max(int(stats.binom.ppf((1 - conf) / 2, n, p)), 1)
    hi = min(int(stats.binom.ppf(1 - (1 - conf) / 2, n, p)), n)
    cov = float(stats.binom.cdf(hi - 1, n, p) - stats.binom.cdf(lo - 1, n, p))
    if cov < conf:
        raise SystemExit(f"order-statistic interval ({lo},{hi}) covers only {cov:.4f}")
    return lo, hi


def table() -> pd.DataFrame:
    rows = []
    for sc in SCENARIOS:
        s = draws(sc)
        for q, name in QUANTILES:
            run = running(s, q)
            rows.append({
                "scenario": sc,
                "quantile": name,
                "n_draws": len(s),
                "final_value_MtCO2": round(float(run[-1]), 2),
                "last_exit_draw": last_exit(run),
                "max_dev_after_half_pct": round(
                    float(np.max(np.abs(run[len(s) // 2:] / run[-1] - 1)) * 100), 2),
            })
    return pd.DataFrame(rows)


def figure(tab: pd.DataFrame) -> None:
    # Canvas width is set by the print-scale floor, not by taste. Both documents include
    # this at \textwidth, the wider of the two text blocks is 469.8 pt and the long paper's
    # is 455.2 pt, so a 9.2 in canvas is scaled to 0.70 on the page and an 8 pt legend
    # lands at 5.6 pt. At 7.6 in the scale is about 0.85 and the smallest run clears 6 pt.
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 2.95), sharey=True)
    for ax, (q, name), title in zip(
            axes, [(50, "median"), (10, "p10")],
            ["(a) running median", "(b) running 10th percentile"]):
        ax.axhspan(-TUBE * 100, TUBE * 100, color="#d9d9d9", alpha=0.55, zorder=0)
        for sc, col in zip(SCENARIOS, PALETTE):
            s = draws(sc)
            run = running(s, q)
            k = np.arange(1, len(s) + 1)
            ax.plot(k, (run / run[-1] - 1) * 100, color=col, lw=1.3,
                    label=short_scen(sc), zorder=3)
            x = last_exit(run)
            ax.plot([x], [(run[x - 1] / run[-1] - 1) * 100], "o", color=col,
                    ms=4.5, zorder=4)
        ax.set_title(title, fontsize=9.5)
        ax.set_xlabel("Draws")
        ax.set_xlim(5, len(s))
        # The first few dozen draws overshoot to +27 per cent in panel (b). Scaling to
        # that would flatten the whole tail, which is the part the claim is about, so
        # the early spikes clip at the top and the axis is set from the settled range.
        ax.set_ylim(-3.5, 9)
        ax.grid(alpha=0.35)
    axes[0].set_ylabel("Deviation from the value at\n200 draws (%)")
    axes[1].legend(loc="upper right", frameon=False, fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGDIR / f"P42_mc_convergence.{ext}")
    plt.close(fig)


def main() -> None:
    tab = table()
    tab.to_csv(RES / "mc_convergence.csv", index=False)
    figure(tab)

    n = int(tab.n_draws.iloc[0])
    lo, hi = order_statistic_interval(n, 10)
    med = tab[tab["quantile"] == "median"]
    dec = tab[tab["quantile"] == "p10"]

    print(f"Running-quantile convergence of {VARIABLE} at {YEAR}, tube +/-{TUBE:.0%}")
    print(tab.to_string(index=False))
    print(f"\nMedian last leaves the tube at draw "
          f"{', '.join(f'{r.scenario} {r.last_exit_draw}' for r in med.itertuples())}")
    print(f"10th percentile last leaves at draw {dec.last_exit_draw.min()} to "
          f"{dec.last_exit_draw.max()} across the four scenarios")
    print(f"At N={n} the 10th percentile is order statistic "
          f"{int(round(0.10 * n))}; exact 95% interval spans order statistics "
          f"{lo} to {hi}, i.e. the {100 * lo / n:.1f}th to the {100 * hi / n:.1f}th "
          f"percentile of the population (the supplement rounds the upper bound up)")
    print(f"\nWrote {RES / 'mc_convergence.csv'}")
    print(f"Wrote {FIGDIR / 'P42_mc_convergence.pdf'}")


if __name__ == "__main__":
    main()
