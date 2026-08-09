"""Climate-warming HDD sensitivity (T4, robustness).

The model holds heating-degree-days at the 1991-2020 climate normal, so the
central demand trajectory excludes the demand-reducing effect of a warming
climate. This script applies a warming-HDD overlay to the STATED_POLICIES useful-heat
trajectory as a one-sided sensitivity (it can only lower heating demand).

Method. Space-heating demand scales ~linearly with HDD; domestic hot water does
not. We therefore apply the warming factor only to the space-heating share
(SH_SHARE) of useful heat:
    D_warm(t) = D(t) * [ (1-SH_SHARE) + SH_SHARE * (1 - r_hdd)^(t-2025) ]
for a per-decade HDD decline expressed as an annual rate r_hdd.

Sourced warming rates (EU population-weighted HDD decline, base 15-18 C):
- central r_hdd = 0.35%/yr  (~ -8.5% by 2050 vs 2025), RCP4.5-consistent;
- low     0.20%/yr  (~ -5%,  our own conservative bound; Spinoni runs only RCP4.5 and
            RCP8.5, so this rate is NOT that study's RCP2.6 result and must not be labelled one);
- high    0.55%/yr  (~ -13%, RCP8.5 / high warming).
Basis: Spinoni et al. (2018) "Changes of heating and cooling degree-days in
Europe 1981-2100", Int. J. Climatology 38:e191-e208 (doi:10.1002/joc.5362), which
projects EU HDD declining roughly 5-15% by mid-century across RCPs; corroborated
by the EEA "Heating and cooling degree days" indicator. These are robustness
bounds, NOT the central case.

Run:  cd code && PYTHONPATH=. python -m scripts.climate_hdd_sensitivity
Out:  code/results/climate_hdd_sensitivity.csv + console
"""
from __future__ import annotations

import pandas as pd

from src.Config import RESULTS_DIR

SH_SHARE = 0.85          # space heating as a share of residential useful heat (DHW ~15%)
RATES = {"low (own bound)": 0.0020, "central (RCP4.5)": 0.0035, "high (RCP8.5)": 0.0055}
YEARS = [2025, 2030, 2040, 2050]


def main() -> None:
    d = pd.read_csv(RESULTS_DIR / "mc_summary_STATED_POLICIES.csv")
    u = (d[d.variable == "useful_heat_MWh"].groupby("year")["q50"].sum() / 1e6)  # TWh
    base2025 = u.loc[2025]

    rows = []
    print(f"STATED_POLICIES useful heat with climate-warming HDD overlay (SH share {SH_SHARE:.0%}):")
    print(f"{'scenario':18s} " + " ".join(f"{y:>8d}" for y in YEARS) + "   2050 vs no-warming")
    # no-warming baseline row
    base_row = {y: round(float(u.loc[y]), 0) for y in YEARS}
    rows.append({"warming": "none (central model)", **{f"twh_{y}": base_row[y] for y in YEARS},
                 "delta_2050_vs_nowarm_pct": 0.0})
    print(f"{'none (model)':18s} " + " ".join(f"{base_row[y]:8.0f}" for y in YEARS) + "        0.0%")
    for label, r in RATES.items():
        vals = {}
        for y in YEARS:
            f = (1 - SH_SHARE) + SH_SHARE * (1 - r) ** (y - 2025)
            vals[y] = float(u.loc[y]) * f
        dpct = (vals[2050] / float(u.loc[2050]) - 1) * 100
        rows.append({"warming": label, **{f"twh_{y}": round(vals[y], 0) for y in YEARS},
                     "delta_2050_vs_nowarm_pct": round(dpct, 1)})
        print(f"{label:18s} " + " ".join(f"{vals[y]:8.0f}" for y in YEARS) + f"     {dpct:6.1f}%")

    # Overall STATED_POLICIES 2050 reduction vs 2025 including warming
    print("\nREF 2050 demand change vs 2025:")
    for row in rows:
        chg = (row["twh_2050"] / base2025 - 1) * 100
        print(f"  {row['warming']:22s}: {chg:+.1f}%")
    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "climate_hdd_sensitivity.csv", index=False)
    print(f"\nWrote {RESULTS_DIR / 'climate_hdd_sensitivity.csv'}")


if __name__ == "__main__":
    main()
