"""Peaking-producer economics: marginal cost, clearing price, and PROFIT of the
hydrogen (vs gas) heat peaker -- the next layer of Abdul's merit-order reframe.

A peaking producer sells few hours but at the highest (clearing) price. In a merit
order the price-setting unit at the cold-snap peak is the most expensive DISPATCHED
source; a cheaper peaker (e.g. H2 where it beats gas) earns the spread = INFRAMARGINAL
RENT. The investment question is whether that rent x its few running hours recovers
the peaker's CAPEX -- the classic "missing money" problem for low-utilisation plant.

Per country x scenario (2050) we compute, for the H2 peaker boiler:
  - marginal operating cost (fuel/eff + seasonal-storage adder)        [from merit_order_heat]
  - clearing price at the peak = cost of the cheapest ALTERNATIVE the system would
    otherwise pay (min of the gas peaker and the cold-snap heat pump)  [what H2 is paid]
  - inframarginal rent = clearing - marginal (EUR/MWh; the operating margin H2 earns)
  - peaker full-load hours (the slice it serves / the slice capacity)
  - annualised H2-boiler CAPEX (EUR/kW-yr) and FOM
  - gross margin (rent x FLH) vs CAPEX -> net profit, and the "missing money" gap

Inputs: merit_order_heat.csv, heat_load_profile.csv, Economics WACC.
Run: cd code && PYTHONPATH=. python -m scripts.merit_order_profit
Out: code/results/merit_order_profit.csv + figure F12.
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import DISCOUNT_RATE_BY_COUNTRY, DISCOUNT_RATE_REAL
from scripts._figstyle import set_style, short_scen, legend_below
set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)
H2_BOILER_CAPEX_EUR_KW = 600.0     # DEA-audited H2-ready boiler CAPEX
H2_BOILER_LIFE = 20
H2_BOILER_FOM_FRAC = 0.02


def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def main():
    mo = pd.read_csv(RESULTS_DIR / "merit_order_heat.csv")
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    rows = []
    for _, r in mo.iterrows():
        c, s = r.country, r.scenario
        if c not in lp.index:
            continue
        lpc = lp.loc[c]
        # clearing price at the peak = cheapest ALTERNATIVE to H2 (what the system pays
        # if H2 is not there); H2, if cheaper, earns the spread as inframarginal rent.
        clearing = min(r.gas_peaker_eur_mwh, r.hp_peak_eur_mwh)
        rent = max(0.0, clearing - r.h2_peaker_eur_mwh)         # EUR/MWh operating margin
        # the peaker serves the peak slice; its capacity ~ peak minus the 2000-h base level
        slice_cap_gw = max(lpc.peak_GW - lpc["GW_at_2000h"], 0.1)
        peak_energy_mwh = r.peak_slice_frac * lpc.annual_TWh * 1e6
        flh = peak_energy_mwh / (slice_cap_gw * 1e3)            # peaker full-load hours
        wacc = DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL)
        ann_capex = crf(wacc, H2_BOILER_LIFE) * H2_BOILER_CAPEX_EUR_KW \
            + H2_BOILER_FOM_FRAC * H2_BOILER_CAPEX_EUR_KW       # EUR/kW-yr to recover
        # 1 kW running FLH hours = FLH/1000 MWh, so margin per kW = rent[EUR/MWh] x FLH/1000
        gross_margin = rent * flh / 1000.0                     # EUR/kW-yr earned (rent x energy)
        net_profit = gross_margin - ann_capex                  # EUR/kW-yr
        rows.append({
            "country": c, "scenario": s, "wins_peak": r.h2_wins_peak,
            "h2_marginal_eur_mwh": r.h2_peaker_eur_mwh,
            "clearing_price_eur_mwh": round(clearing, 1),
            "rent_eur_mwh": round(rent, 1),
            "peaker_flh": round(flh, 0),
            "ann_capex_eur_kw_yr": round(ann_capex, 1),
            "gross_margin_eur_kw_yr": round(gross_margin, 1),
            "net_profit_eur_kw_yr": round(net_profit, 1),
            "covers_capex": net_profit >= 0,
            "missing_money_eur_kw_yr": round(max(0.0, -net_profit), 1),
        })
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "merit_order_profit.csv", index=False)

    print("Scenario          | H2 wins peak | of those, COVER CAPEX (profitable to build) | EU rent EUR/MWh")
    for s in df.scenario.unique():
        d = df[df.scenario == s]; w = d[d.wins_peak]
        cov = w[w.covers_capex]
        print(f"  {s:<16}| {len(w):>2} | {len(cov):>2} ({', '.join(cov.country) if len(cov) else 'NONE -- missing money'}) "
              f"| {w.rent_eur_mwh.mean() if len(w) else 0:.0f}")

    # figure: H2_PUSH peaker economics -- gross margin vs CAPEX line, by country (H2 winners)
    d = df[(df.scenario == "H2_PUSH") & (df.wins_peak)].sort_values("net_profit_eur_kw_yr")
    if len(d):
        fig, ax = plt.subplots(figsize=(7.6, max(3.2, 0.46 * len(d) + 1.8)))
        y = np.arange(len(d))
        ax.barh(y, d.gross_margin_eur_kw_yr, color="#4c78a8", label="margin earned (rent × hours)")
        for yi, (_, rr) in zip(y, d.iterrows()):
            ax.plot([rr.ann_capex_eur_kw_yr]*2, [yi-0.4, yi+0.4], color="#d62728", lw=2.2)
        ax.plot([], [], color="#d62728", lw=2.2, label="CAPEX to recover")
        ax.set_yticks(y); ax.set_yticklabels(d.country)
        ax.set_xlabel("€/kW-yr  (margin short of the red line = 'missing money')")
        ax.set_title(f"H₂ peaker: margin earned vs CAPEX to recover ({short_scen('H2_PUSH')}, 2050)")
        legend_below(ax, ncol=2)
        fig.savefig(FIG / "F12_peaker_profit.png"); plt.close(fig)
    print("\nWrote results/merit_order_profit.csv + F12_peaker_profit.png (where it has H2 winners).")


if __name__ == "__main__":
    main()
