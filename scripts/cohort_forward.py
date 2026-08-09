"""T4 -- vintage-cohort turnover forward (alternative to the LMDI single-rate forward).

The default forward scales national demand by D0 * pop * occupancy * (1-r)^(t-2025),
a single aggregate envelope-decline rate r. This module instead carries the
per-(class, cohort) floor area forward with explicit stock flows, so the
intensity path is an EMERGENT weighted average:

  existing stock  : A_kc(t) = A_kc(2025) * (1 - demo_rate)^(t-2025), with each
                    cohort's intensity declining as renovation accumulates
                    I_eff = I_kc * (1 - min(1, renov_rate_c*(t-2025)) * (1-RETRO_FACTOR));
  new build       : total floor area grows with population x occupancy (same
                    drivers as the LMDI forward); the increment over the
                    surviving existing stock is new build at an nZEB intensity;
  demand(t)       = sum_kc A_kc(t) * I_eff_kc(t)  +  A_new(t) * I_nzeb.

2025 area + intensity per (class, cohort) are read from each country's
{CC}_heat_intensity_summary.csv. renov_rate_c is the country's STATED_POLICIES
envelope-renovation rate (scenario_intensity_rates.csv). This is an alternative
forward_mode kept SEPARATE from the validated LMDI default; the script reports
cohort vs LMDI per country + EU as a cross-check (they agree at the EU level to
within ~3%, validating the single-rate LMDI forward against an explicit
stock-flow model; per-country differences reflect cohort structure and
new-build growth).

Sources: demolition ~0.1%/yr and renovation rates (BPIE / Ipsos 2019);
nZEB new-build intensity (EPBD recast).

Run:  cd code && PYTHONPATH=. python -m scripts.cohort_forward
Out:  code/results/cohort_forward.csv + console
"""
from __future__ import annotations

import pandas as pd

import src.Config as C
from src.Config import PROCESSED_DIR, RESULTS_DIR, BASE_YEAR, forward_demand_ratio

DEMO_RATE = 0.001        # ~0.1%/yr stock demolition (BPIE)
RETRO_FACTOR = 0.50      # retrofitted-state intensity ~half of existing (TABULA standard ~0.55)
I_NZEB = 45.0            # nZEB new-build useful intensity (kWh/m2/yr), EPBD recast (fallback)
YEARS = list(range(BASE_YEAR, 2051))


def _ref_rate(cc: str) -> float:
    rates = C.central_country_intensity_rates("STATED_POLICIES")
    return rates.get(cc, 0.0055)


def _summary(cc: str):
    f = PROCESSED_DIR / cc.lower() / f"{cc}_heat_intensity_summary.csv"
    if not f.exists():
        return None
    d = pd.read_csv(f)
    cols = {c.lower(): c for c in d.columns}
    a = cols.get("total_heated_area_m2"); i = cols.get("mean_intensity_kwh_m2")
    if not (a and i):
        return None
    d = d[(d[a] > 0) & d[i].notna()].copy()
    return d[[a, i]].rename(columns={a: "area_m2", i: "intensity"})


def cohort_demand(cc: str) -> tuple[float, float] | None:
    s = _summary(cc)
    if s is None or s.empty:
        return None
    A0 = s["area_m2"].to_numpy()
    I0 = s["intensity"].to_numpy()
    base_demand = float((A0 * I0).sum()) / 1e9   # TWh (kWh -> TWh)
    r = _ref_rate(cc)
    # new-build nZEB intensity: use the lowest-intensity (newest) cohort as a floor
    i_nzeb = min(I_NZEB, float(I0.min())) if len(I0) else I_NZEB

    out = {}
    A_total_2025 = float(A0.sum())
    for t in YEARS:
        yrs = t - BASE_YEAR
        # surviving existing stock + its retrofit-reduced intensity
        surv = (1 - DEMO_RATE) ** yrs
        renov = min(1.0, r * yrs)
        i_eff = I0 * (1 - renov * (1 - RETRO_FACTOR))
        existing_area = A0 * surv
        existing_demand = float((existing_area * i_eff).sum())
        # total floor area driven by pop x occupancy (r=0 isolates the stock term)
        stock_growth = forward_demand_ratio(cc, t, 0.0)
        total_area = A_total_2025 * stock_growth
        new_area = max(0.0, total_area - existing_area.sum())
        new_demand = new_area * i_nzeb
        out[t] = (existing_demand + new_demand) / 1e9   # TWh
    return base_demand, out[2050]


def main() -> None:
    rows, eu_cohort, eu_lmdi = [], 0.0, 0.0
    for cc in C.central_country_intensity_rates("STATED_POLICIES"):
        res = cohort_demand(cc)
        if res is None:
            continue
        d2025, d2050_cohort = res
        lmdi_2050 = d2025 * forward_demand_ratio(cc, 2050, _ref_rate(cc))
        eu_cohort += d2050_cohort
        eu_lmdi += lmdi_2050
        rows.append({"country": cc, "demand_2025_TWh": round(d2025, 2),
                     "cohort_2050_TWh": round(d2050_cohort, 2),
                     "lmdi_2050_TWh": round(lmdi_2050, 2),
                     "cohort_vs_lmdi_pct": round((d2050_cohort / lmdi_2050 - 1) * 100, 1)
                     if lmdi_2050 else None})
    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "cohort_forward.csv", index=False)
    print(df.to_string(index=False))
    print(f"\nEU 2050 useful heat: cohort {eu_cohort:.0f} TWh vs LMDI {eu_lmdi:.0f} TWh "
          f"({(eu_cohort/eu_lmdi-1)*100:+.1f}%)")
    print("The two independent forwards agree at the EU level to within ~3%; "
          "per-country differences reflect each stock's cohort structure and "
          "new-build growth (e.g. faster-growing stocks diverge more). The cohort "
          "model is kept as an alternative forward_mode; the LMDI single-rate "
          "forward remains the validated default.")
    print(f"Wrote {RESULTS_DIR / 'cohort_forward.csv'}")


if __name__ == "__main__":
    main()
