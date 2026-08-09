"""T3 -- endogenous renovation depth in COST_OPT (run + compare).

Compares the validated fixed-demand cost-optimal LP (solve) with the
retrofit-endogenous variant (solve_with_retrofit), at the -90% and -100% caps.
Reports, per variant: present-value system cost, EU 2050 retrofit (avoided-demand)
share, and the binding-country count -- so the paper can state how much envelope
renovation the cost-optimum actually chooses, and at what cost.

Per-country retrofit cost is built from each country's useful-heat intensity
(kWh/m2/yr, read from {CC}_reconciliation_with_hotmaps.csv) via the Ipsos/Navigant
2019 medium-depth curve (Optimisation.retrofit_cost_per_mwh).

Run:  cd code && PYTHONPATH=. python -m scripts.cost_opt_retrofit
Out:  code/results/cost_opt_retrofit.csv + console
"""
from __future__ import annotations

import glob
import os

import pandas as pd

import src.Optimisation as O
from src.Config import RESULTS_DIR, PROCESSED_DIR


def _country_intensity() -> dict:
    """Useful-heat intensity (kWh/m2/yr) per country from the reconciliation files."""
    out = {}
    for f in glob.glob(str(PROCESSED_DIR / "*" / "??_reconciliation_with_hotmaps.csv")):
        cc = os.path.basename(f)[:2].upper()
        d = pd.read_csv(f)
        m = d[d["source"].str.contains("residential only", case=False, na=False)]
        if len(m) and "kwh_m2_yr_avg" in d.columns:
            v = float(m["kwh_m2_yr_avg"].iloc[0])
            if v > 0:
                out[cc] = v
    return out


def _eu_share(data, res, year):
    """Demand-weighted EU retrofit share in `year`.

    Reporting 2050 alone hid the result: the ramp constraint is one-sided, so the program
    builds retrofit for the interim caps and lets it lapse by 2050, and a 2050-only reader
    concluded the option was never selected.
    """
    dem = data["demand"]
    tot = sum(dem[(c, year)] for c in data["countries"])
    s = sum(res["retro_share"].get((c, year), 0.0) * dem[(c, year)]
            for c in data["countries"])
    return s / tot if tot else 0.0


def _positive(res, year):
    return sorted(f"{c} {100 * v:.1f}" for (c, y), v in res["retro_share"].items()
                  if y == year and v > 1e-6)


def _eu_2050(data, res, key="retro_share"):
    dem = data["demand"]
    tot = sum(dem[(c, 2050)] for c in data["countries"])
    if key == "retro_share":
        s = sum(res["retro_share"].get((c, 2050), 0.0) * dem[(c, 2050)]
                for c in data["countries"])
        return s / tot if tot else 0.0
    return None


def _binders(data, res):
    base = data["base_s1_c"]
    sh = {c: res["shadow_price"].get((c, 2050), float("nan"))
          for c in data["countries"] if base.get(c, 0.0) >= 0.5e6}
    return sum(1 for v in sh.values() if v == v and v > 1.0)


def main() -> None:
    ci = _country_intensity()
    print(f"per-country intensities: {len(ci)} countries; "
          f"retrofit LCOH range {O.retrofit_cost_per_mwh(max(ci.values())):.0f}"
          f"-{O.retrofit_cost_per_mwh(min(ci.values())):.0f} EUR/MWh "
          f"(cold/high-intensity cheapest)")
    data = O.prepare_data(demand="bottomup")

    rows = []
    for key in ("90", "100"):
        tgt = O.COST_OPT_TARGETS[key]
        fixed = O.solve(data, tgt)
        retro = O.solve_with_retrofit(data, tgt, ci)
        rs = _eu_2050(data, retro)
        per_year = {y: _eu_share(data, retro, y) for y in (2025, 2030, 2040, 2050)}
        for y, v in per_year.items():
            print(f"    retrofit {y}: EU {100 * v:.2f}%  "
                  f"[{', '.join(_positive(retro, y)) or 'none'}]")
        rows.append({"cap": f"-{key}%",
                     "retro_share_2030_pct": round(100 * per_year[2030], 2),
                     "retro_share_2040_pct": round(100 * per_year[2040], 2),
                     "pv_fixed_bn": round(fixed["objective"] / 1e9, 1),
                     "pv_retrofit_bn": round(retro["objective"] / 1e9, 1),
                     "retro_share_2050_pct": round(rs * 100, 1),
                     "binders_fixed": _binders(data, fixed),
                     "binders_retrofit": _binders(data, retro),
                     "status": retro["status"]})
        print(f"  -{key}%: PV fixed {rows[-1]['pv_fixed_bn']} bn | "
              f"PV+retrofit {rows[-1]['pv_retrofit_bn']} bn | "
              f"retrofit avoids {rows[-1]['retro_share_2050_pct']}% of 2050 demand | "
              f"binders {rows[-1]['binders_fixed']}->{rows[-1]['binders_retrofit']}")
    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "cost_opt_retrofit.csv", index=False)
    print(f"\nInterpretation: medium-depth retrofit (~{O.retrofit_cost_per_mwh(150):.0f} "
          f"EUR/MWh at 150 kWh/m2) is pricier per MWh than heat pumps (~70-100), so the "
          f"cost-optimum picks retrofit only where clean-supply abatement is exhausted or "
          f"in cold high-intensity stock. Reported as-is, not forced.")
    print(f"Wrote {RESULTS_DIR / 'cost_opt_retrofit.csv'}")


if __name__ == "__main__":
    main()
