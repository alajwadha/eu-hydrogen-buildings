"""Per-country, per-scenario 2050 LCOH for the best heat pump, hydrogen boiler
and gas boiler, reusing the model's own compute_lcoh (no re-derived formula).

Each policy scenario differs on two LCOH levers: the carbon price (which lifts
the gas boiler via the ETS2 adder) and the hydrogen price trajectory (which sets
the hydrogen boiler fuel cost). Best-HP is scenario-invariant because the retail
electricity price has no scenario axis and the electricity carbon adder nets to
~0 by 2050. STATED_POLICIES (CENTRAL/CENTRAL) reproduces country_econ_table.csv.

Run: cd code && PYTHONUTF8=1 PYTHONPATH=. python -m scripts.country_econ_table_by_scenario
"""
from __future__ import annotations

import pandas as pd

import src.Economics as E
from src.Config import RESULTS_DIR, SCENARIOS

POLICY_SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]


def main() -> None:
    central = pd.read_csv(RESULTS_DIR / "country_econ_table.csv")
    countries = list(central["country"])
    c0 = central.set_index("country")

    rows = []
    for c in countries:
        for name in POLICY_SCEN:
            s = SCENARIOS[name]
            cs, h2s = s["carbon_scenario"], s["h2_scenario"]
            hp = min(
                E.compute_lcoh("hp_air", c, 2050, carbon_price_scenario=cs, h2_scenario=h2s),
                E.compute_lcoh("hp_ground", c, 2050, carbon_price_scenario=cs, h2_scenario=h2s),
            )
            gas = E.compute_lcoh("gas_boiler", c, 2050, carbon_price_scenario=cs, h2_scenario=h2s)
            h2 = E.compute_lcoh("h2_boiler", c, 2050, carbon_price_scenario=cs, h2_scenario=h2s)
            rows.append({
                "country": c,
                "scenario": name,
                "lcoh_bestHP_2050": round(hp, 1),
                "lcoh_gas_2050": round(gas, 1),
                "lcoh_H2_2050": round(h2, 1),
            })

    df = pd.DataFrame(rows)
    out = RESULTS_DIR / "country_econ_table_by_scenario.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {out} ({len(df)} rows, {len(countries)} countries x {len(POLICY_SCEN)} scenarios)")

    # Validation: STATED_POLICIES must reproduce the central table.
    bad = 0
    for cc in countries:
        st = df[(df.country == cc) & (df.scenario == "STATED_POLICIES")].iloc[0]
        for col in ["lcoh_bestHP_2050", "lcoh_gas_2050", "lcoh_H2_2050"]:
            if abs(float(st[col]) - float(c0.at[cc, col])) > 0.15:
                bad += 1
                print(f"  MISMATCH {cc} {col}: scenario {st[col]} vs central {c0.at[cc, col]}")
    print(f"STATED vs central: {'exact match' if bad == 0 else str(bad) + ' mismatches'}")

    for cc in ["DE", "FR", "DK", "PL"]:
        print(f"\n{cc}:")
        for scn in POLICY_SCEN:
            r = df[(df.country == cc) & (df.scenario == scn)].iloc[0]
            print(f"  {scn:18} HP {r.lcoh_bestHP_2050:6}  gas {r.lcoh_gas_2050:6}  H2 {r.lcoh_H2_2050:6}")


if __name__ == "__main__":
    main()
