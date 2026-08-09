"""Charge district heat the last-mile connection the other two carriers already pay.

WHY THIS EXISTS. The paper's methodological claim is symmetric network charging: each
carrier is charged its own last-mile network, so the heat-pump-versus-hydrogen comparison
does not quietly hand one of them a free grid. That symmetry covers the two carriers the
paper leads with. It does not cover district heat, which pays no connection charge at all
while both of the others do, and district heat is nonetheless reported as the cheapest
option in the levelised-cost section and as the largest component of the least-cost mix.

The asymmetry was described in the SI and quantified in the body, but the numbers behind
it lived in neither a script nor a CSV. A referee pointed out that this is the same
defect the paper had just corrected elsewhere: a load-bearing figure that a reader cannot
regenerate. This script commits them.

WHAT IT COMPUTES. For each of the 29 countries, at 2050:
  - the district-heat levelised cost as the model currently charges it (no connection),
  - the annualised connection charge, taking the same EUR 5,000 per connection that this
    paper's own infrastructure bill already assigns district heat, over a 40-year asset
    life at the country's own cost of capital, spread over that country's per-dwelling
    annual useful-heat demand,
  - the district-heat cost with the charge applied,
  - and whether district heat still undercuts the best heat pump, before and after.

The charge is deliberately computed on the paper's own committed inputs rather than a new
assumption: the connection cost is the central value from the infrastructure bill, the
lifetime matches the network asset life used there, and the discount rate is the same
per-country WACC the levelised-cost layer uses everywhere else.

WHAT IT DOES NOT DO. It does not re-solve the least-cost program with the charge applied,
so it bounds the direction and size of the effect on that program without quantifying the
resulting mix. The body says so where the least-cost mix is reported.

Run:  cd code && PYTHONPATH=. python -m scripts.dh_connection_charge
Out:  code/results/dh_connection_charge.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.Config import RESULTS_DIR, PROCESSED_DIR
from src.Economics import (compute_lcoh, DISCOUNT_RATE_BY_COUNTRY, DISCOUNT_RATE_REAL)
from scripts.infrastructure_bill import DH_CONNECTION_EUR

YEAR = 2050
LIFE = 40                      # network asset life, as the infrastructure bill assumes
HP_TECHS = ("hp_air", "hp_ground")


def crf(r: float, n: int) -> float:
    return r / (1.0 - (1.0 + r) ** -n) if r > 0 else 1.0 / n


def main() -> None:
    # Annual useful heat per country, and the dwelling count the infrastructure bill uses,
    # so the charge is spread on exactly the stock that bill assigns connections to.
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    dwellings = (stock[stock.building_type.isin(["SFH", "MFH_HIGH"])]
                 .groupby("country").dwellings_2021.sum())
    demand = lp["annual_TWh"]

    rows = []
    for c in sorted(set(demand.index) & set(dwellings.index)):
        dh = compute_lcoh("district_heat", c, YEAR)
        hp = min(compute_lcoh(t, c, YEAR) for t in HP_TECHS)
        wacc = DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL)
        ann = DH_CONNECTION_EUR["central"] * crf(wacc, LIFE)      # EUR per dwelling-year
        # Useful heat per dwelling per year (MWh), from the same demand the model carries.
        if c in dwellings.index and dwellings[c] > 0 and c in demand.index:
            mwh_per_dwelling = demand[c] * 1e6 / dwellings[c]     # TWh -> MWh, per dwelling
        else:
            mwh_per_dwelling = np.nan
        charge = ann / mwh_per_dwelling if mwh_per_dwelling and mwh_per_dwelling > 0 else np.nan
        rows.append(dict(country=c, dh_lcoh=round(dh, 2), best_hp_lcoh=round(hp, 2),
                         connection_charge_eur_mwh=round(charge, 2),
                         dh_lcoh_with_charge=round(dh + charge, 2),
                         dh_cheaper_before=bool(dh < hp),
                         dh_cheaper_after=bool(dh + charge < hp)))

    df = pd.DataFrame(rows)
    out = RESULTS_DIR / "dh_connection_charge.csv"
    df.to_csv(out, index=False)

    ch = df.connection_charge_eur_mwh.dropna()
    print(f"District-heat connection charge, {YEAR}\n")
    print(f"  district-heat LCOH median      : {df.dh_lcoh.median():.2f} EUR/MWh")
    print(f"  connection charge median       : {ch.median():.1f} EUR/MWh "
          f"(range {ch.min():.1f} to {ch.max():.1f})")
    print(f"  DH cheaper than best HP before : {int(df.dh_cheaper_before.sum())} of {len(df)}")
    print(f"  DH cheaper than best HP after  : {int(df.dh_cheaper_after.sum())} of {len(df)}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
