"""Reprice the hydrogen peaker at blue hydrogen and report what survives.

The paper prices hydrogen green, at about EUR50/MWh delivered in 2050, inclusive of
transport and exclusive of the last-mile distribution the levelised cost charges
separately. The
one dedicated assessment of hydrogen for the German heating sector concludes that any
hydrogen actually supplied to heating would be blue, at about EUR81/MWh (Dickel, OIES
ET29). The Supplementary Information already reverses that assumption for the base-load
levelised-cost test, where it closes hydrogen's remaining seven wins.

It used to claim the capacity-side findings were "unaffected" by the same point, on the
grounds that the peaking comparison prices both turbines at wholesale. That reasoning
answers the *tax* objection, since neither turbine pays a household tariff, but it does
not answer the *provenance* objection: a dearer molecule raises the hydrogen turbine's
short-run cost against an unchanged gas turbine. This script computes what actually
happens, using the model's own peak-price formula with only the hydrogen price
substituted. The identifiers below still read `gate` for historical reasons; the
quantity they hold is the delivered price defined above.

Two substitutions bracket the reasonable readings of a single-country estimate:

  flat        every market pays EUR81/MWh, i.e. the German figure is read as
              a European price. This is the harsher reading and it removes the win.
  proportional  each market's own price is scaled by 81/50, i.e. the German figure
              is read as a green-to-blue ratio and each country keeps its relative
              position. The win set holds and the margin roughly halves.

The capital-recovery verdict itself is untouched either way, because a winner's
inframarginal rent is the scarcity premium times its run hours and carries no fuel-price
term. What is exposed is the win set that feeds it.

Run:  cd code && PYTHONPATH=. python -m scripts.blue_hydrogen_peaker
Out:  results/blue_hydrogen_peaker.csv
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

from scripts.power_peak_price import (power_storage_adder, ETA_H2_TURBINE, VOM_PEAKER,
                                      H2_BACKBONE_FACTOR)
from src.Economics import get_fuel_price, compute_lcoh
from src.Config import RESULTS_DIR
import src.Config as C

SCEN = "H2_PUSH"
YEAR = 2050
H2_LEVEL = "RAPID"                 # the hydrogen path H2 Push runs on
CAVERN = ["DE", "DK", "FR", "NL", "PL", "RO", "UK"]
BLUE_GATE_EUR_MWH = 81.0           # Dickel (OIES ET29), German heating sector
GREEN_REFERENCE_EUR_MWH = 50.0     # the north-west-Europe green hub the model prices on


def srmc(country: str, gate_eur_mwh: float) -> float:
    """Hydrogen-turbine short-run marginal cost, EUR/MWh-e, at a given gate price."""
    return (gate_eur_mwh * H2_BACKBONE_FACTOR / ETA_H2_TURBINE
            + power_storage_adder(country) + VOM_PEAKER)


def main() -> None:
    peak = pd.read_csv(RESULTS_DIR / "power_peak_price.csv")
    peak = peak[peak.scenario == SCEN].set_index("country")

    rows = []
    for c in CAVERN:
        green_gate = get_fuel_price("hydrogen", c, YEAR, H2_LEVEL)
        gas = float(peak.loc[c, "ocgt_srmc"])
        cases = {
            "green": green_gate,
            "blue_flat": BLUE_GATE_EUR_MWH,
            "blue_proportional": green_gate * BLUE_GATE_EUR_MWH / GREEN_REFERENCE_EUR_MWH,
        }
        for case, gate in cases.items():
            h2 = srmc(c, gate)
            rows.append(dict(country=c, scenario=SCEN, year=YEAR, case=case,
                             h2_gate_eur_mwh=round(gate, 2),
                             h2_turbine_srmc=round(h2, 1),
                             ocgt_srmc=round(gas, 1),
                             advantage_eur_mwh_e=round(gas - h2, 1),
                             hydrogen_wins=bool(gas > h2)))

    # The base-load count under the same two substitutions. Two passages declined to give
    # this count, on the grounds that the figure quoted in earlier drafts predated the
    # seasonal-storage charge and had not been recomputed on the storage-inclusive basis.
    # It is recomputed here, so those refusals were stale and the assertion elsewhere in
    # both manuscripts that blue pricing closes all seven leads is derived rather than
    # remembered. Both substitutions are reported because they do not agree on the count.
    base = []
    for c in sorted(C.EU_COUNTRIES):
        hp = min(compute_lcoh("hp_air", c, YEAR), compute_lcoh("hp_ground", c, YEAR))
        gate = get_fuel_price("hydrogen", c, YEAR, H2_LEVEL)
        green = compute_lcoh("h2_boiler", c, YEAR)
        flat = compute_lcoh("h2_boiler", c, YEAR,
                            price_mult={"hydrogen": BLUE_GATE_EUR_MWH / gate})
        prop = compute_lcoh("h2_boiler", c, YEAR,
                            price_mult={"hydrogen": BLUE_GATE_EUR_MWH
                                        / GREEN_REFERENCE_EUR_MWH})
        base.append(dict(country=c, hp_lcoh=round(hp, 2), h2_green=round(green, 2),
                         h2_blue_flat=round(flat, 2), h2_blue_proportional=round(prop, 2),
                         green_lead=bool(green < hp), flat_lead=bool(flat < hp),
                         proportional_lead=bool(prop < hp)))
    bdf = pd.DataFrame(base)
    bdf.to_csv(RESULTS_DIR / "blue_hydrogen_baseload.csv", index=False)

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "blue_hydrogen_peaker.csv", index=False)

    print(f"\n=== Hydrogen peaker repriced at blue hydrogen "
          f"({SCEN} {YEAR}, the seven salt-cavern markets) ===")
    print(f"{'case':20s}{'H2 SRMC EUR/MWh-e':>20s}{'advantage':>22s}{'wins':>8s}")
    for case in ["green", "blue_flat", "blue_proportional"]:
        x = df[df.case == case]
        print(f"{case:20s}{x.h2_turbine_srmc.min():9.1f} to {x.h2_turbine_srmc.max():<8.1f}"
              f"{x.advantage_eur_mwh_e.min():+11.1f} to {x.advantage_eur_mwh_e.max():+8.1f}"
              f"{int(x.hydrogen_wins.sum()):5d}/7")
    print("\nThe capital-recovery verdict is unchanged in every case: a winner's rent is "
          "the scarcity\npremium times its run hours and carries no fuel-price term. What "
          "moves is the win set.")
    n = len(bdf)
    print(f"\n=== Base-load levelised cost repriced at blue hydrogen ({YEAR}) ===")
    print(f"  green            heat pump cheaper in {int((~bdf.green_lead).sum())}/{n}, "
          f"hydrogen leads in {int(bdf.green_lead.sum())} "
          f"({', '.join(sorted(bdf[bdf.green_lead].country))})")
    for col, lbl in [("flat_lead", "blue, flat gate"),
                     ("proportional_lead", "blue, proportional")]:
        held = sorted(bdf[bdf[col]].country)
        print(f"  {lbl:16s} heat pump cheaper in {int((~bdf[col]).sum())}/{n}, "
              f"hydrogen leads in {len(held)} ({', '.join(held) if held else 'none'})")
    print(f"Wrote {RESULTS_DIR / 'blue_hydrogen_peaker.csv'}")
    print(f"Wrote {RESULTS_DIR / 'blue_hydrogen_baseload.csv'}")


if __name__ == "__main__":
    main()
