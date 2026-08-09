"""COST_OPT robustness sweep (T3): feasibility-ceiling sensitivity + scope-2 cap.

The cost-optimal 2050 mix is partly ceiling-driven (ground-source HP and biomass
run up against feasibility caps), and the headline cap is scope-1 (on-site
combustion) only. This script quantifies both:

  1. GSHP ceiling sweep   -- GSHP_SFH_FRACTION in {0.30, 0.45, 0.60}
  2. Biomass ceiling sweep -- BIOMASS_CAP in {0.10, 0.20, 0.30}
  3. Scope-2 cap variant   -- cap on total (scope-1 + grid/DH) emissions

All at the -90% target, trajectory mode. Reports the EU 2050 technology mix
(demand-weighted), the present-value system cost, and the binding-country count
for each setting, so the paper can state how sensitive the cost-optimal result
is to these structural assumptions.

Run:  cd code && PYTHONPATH=. python -m scripts.cost_opt_sensitivity
Out:  code/results/cost_opt_sensitivity.csv + console
"""
from __future__ import annotations

import pandas as pd

import src.Optimisation as O
from src.Config import RESULTS_DIR, TECHS, YEARS

TARGET = O.COST_OPT_TARGETS["90"]
TECHS_REP = ["hp_air", "hp_ground", "district_heat", "biomass_boiler",
             "h2_boiler", "gas_boiler"]


def _eu_shares_2050(data, res) -> dict:
    dem = data["demand"]
    tot = sum(dem[(c, 2050)] for c in data["countries"])
    out = {}
    for t in TECHS:
        s = sum(res["shares"].get((c, t, 2050), 0.0) * dem[(c, 2050)]
                for c in data["countries"])
        out[t] = s / tot if tot else 0.0
    return out


def _binders(data, res) -> tuple[int, float]:
    base = data["base_s1_c"]
    sh = {c: res["shadow_price"].get((c, 2050), float("nan"))
          for c in data["countries"] if base.get(c, 0.0) >= 0.5e6}
    binding = [c for c, v in sh.items() if v == v and v > 1.0]
    mx = max([v for v in sh.values() if v == v], default=float("nan"))
    return len(binding), mx


def _row(label, gshp, biomass, cap_basis, data, res):
    sh = _eu_shares_2050(data, res)
    nb, mx = _binders(data, res)
    return {"setting": label, "gshp_frac": gshp, "biomass_cap": biomass,
            "cap_basis": cap_basis, "status": res["status"],
            "pv_bn_eur_yr": round(res["objective"] / 1e9, 1),
            "hp_air_2050": round(sh["hp_air"] * 100, 1),
            "hp_ground_2050": round(sh["hp_ground"] * 100, 1),
            "district_heat_2050": round(sh["district_heat"] * 100, 1),
            "biomass_2050": round(sh["biomass_boiler"] * 100, 1),
            "h2_2050": round(sh["h2_boiler"] * 100, 1),
            "binders_2050": nb, "max_price_eur_tco2": round(mx, 0)}


def main() -> None:
    rows = []
    g0 = O.GSHP_SFH_FRACTION
    b0 = O.BIOMASS_CAP

    # Baseline (central ceilings, scope-1)
    data = O.prepare_data(demand="bottomup")
    res = O.solve(data, TARGET)
    rows.append(_row("baseline (central, scope-1)", g0, b0, "scope1", data, res))

    # 1. GSHP ceiling sweep (prepare_data reads GSHP_SFH_FRACTION); centred on the
    #    realistic 0.15 deployable-SFH ceiling, bracketing 0.10-0.25.
    for g in (0.10, 0.15, 0.25):
        O.GSHP_SFH_FRACTION = g
        d = O.prepare_data(demand="bottomup")
        r = O.solve(d, TARGET)
        rows.append(_row(f"GSHP_frac={g:.2f}", g, b0, "scope1", d, r))
    O.GSHP_SFH_FRACTION = g0

    # 2. Biomass ceiling sweep (solve reads BIOMASS_CAP)
    data = O.prepare_data(demand="bottomup")
    for b in (0.10, 0.20, 0.30):
        O.BIOMASS_CAP = b
        r = O.solve(data, TARGET)
        rows.append(_row(f"biomass_cap={b:.2f}", g0, b, "scope1", data, r))
    O.BIOMASS_CAP = b0

    # 3. Scope-2 cap variant (cap on total emissions)
    data = O.prepare_data(demand="bottomup")
    r = O.solve(data, TARGET, cap_basis="total")
    rows.append(_row("scope-2 cap (total emissions)", g0, b0, "total", data, r))

    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "cost_opt_sensitivity.csv", index=False)
    cols = ["setting", "pv_bn_eur_yr", "hp_ground_2050", "biomass_2050",
            "h2_2050", "binders_2050", "max_price_eur_tco2"]
    print(df[cols].to_string(index=False))
    print(f"\nWrote {RESULTS_DIR / 'cost_opt_sensitivity.csv'}")


if __name__ == "__main__":
    main()
