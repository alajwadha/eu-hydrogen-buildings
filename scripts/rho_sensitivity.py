"""Sensitivity of the EU-aggregate 2050 demand band to the cross-country
renovation-rate correlation rho.

Useful heat demand depends only on the per-country pop x occupancy x envelope-rate
product (not on tech shares or prices), so the EU demand band is generated
entirely by the intensity-rate sampling. We therefore reproduce it analytically
and cheaply: take per-country 2025 base demand, sample correlated rates at
rho in {0, 0.5, 1}, and form the EU 2050 sum over many draws.

rho=0  -> independent draws (diversified, narrow EU band)
rho=0.5 -> central (the shipped Config.INTENSITY_RATE_CORR)
rho=1  -> fully correlated (widest)

Run:  cd code && PYTHONPATH=. python -m scripts.rho_sensitivity
Out:  code/results/rho_sensitivity.csv  + console
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.Config import (PROCESSED_DIR, RESULTS_DIR, forward_demand_ratio,
                        sample_country_intensity_rates)

N_DRAWS = 4000
RHOS = [0.0, 0.5, 1.0]
SCENARIOS = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]


def _base_demand_by_country() -> dict:
    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    return (stock.groupby("country")["heat_2015_MWh"].sum() / 1e6).to_dict()  # TWh


def main() -> None:
    base = _base_demand_by_country()
    countries = list(base.keys())
    # Pre-compute the pop x occupancy multiplier (rate-independent) per country
    # by reading it off forward_demand_ratio at r=0.
    popocc = {c: forward_demand_ratio(c, 2050, 0.0) for c in countries}

    rows = []
    print("EU 2050 useful demand (TWh) band by correlation rho:")
    for sc in SCENARIOS:
        for rho in RHOS:
            rng = np.random.default_rng(20260528)
            eu = np.empty(N_DRAWS)
            for i in range(N_DRAWS):
                rates = sample_country_intensity_rates(sc, rng, rho=rho)
                tot = 0.0
                for c in countries:
                    r = rates.get(c, 0.0055)
                    intens = (1.0 - r) ** 25
                    tot += base[c] * popocc[c] * intens
                eu[i] = tot
            q10, q50, q90 = np.percentile(eu, [10, 50, 90])
            width = q90 - q10
            rows.append({"scenario": sc, "rho": rho,
                         "q10": round(q10, 1), "q50": round(q50, 1),
                         "q90": round(q90, 1), "width": round(width, 1)})
            print(f"  {sc:10s} rho={rho:.1f}: {q50:6.0f} [{q10:.0f}-{q90:.0f}]  width={width:.0f}")
    out = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(RESULTS_DIR / "rho_sensitivity.csv", index=False)
    # Width amplification rho=0.5 and rho=1 vs rho=0
    print("\nBand-width amplification vs independent (rho=0):")
    for sc in SCENARIOS:
        w0 = out[(out.scenario == sc) & (out.rho == 0.0)]["width"].iloc[0]
        w5 = out[(out.scenario == sc) & (out.rho == 0.5)]["width"].iloc[0]
        w1 = out[(out.scenario == sc) & (out.rho == 1.0)]["width"].iloc[0]
        print(f"  {sc:10s}: rho0.5={w5/w0:.1f}x  rho1.0={w1/w0:.1f}x")
    print(f"\nWrote {RESULTS_DIR / 'rho_sensitivity.csv'}")


if __name__ == "__main__":
    main()
