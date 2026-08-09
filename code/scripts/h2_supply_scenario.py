"""H2-supply sensitivity: how the 2050 H2-boiler-vs-heat-pump gap moves when each
country's DELIVERED-hydrogen cost is varied over its supply-grounded low-central-
high band (Economics.H2_MULT_RANGE_BY_COUNTRY).

The multiplier is relative to the NW-EU hub trajectory (~EUR 50/MWh in 2050,
central). It captures how hydrogen is OBTAINED per country: cheap domestic
production (renewable-rich ~0.90), EHB pipeline imports via repurposed corridors
(landlocked Central Europe ~1.00-1.10, NOT the old flat +10%), or ship-only import
to the isolated islands (CY/MT ~1.25-1.30). Grounding + sources:
literature/h2_supply_country_assessment.md.

Implemented without touching the LCOH engine: get_fuel_price already applies the
central H2_MULT_BY_COUNTRY[c] and an optional per-carrier price_mult, so evaluating
bound b just means passing price_mult={"hydrogen": mult_b / mult_central}.

Run:  cd code && PYTHONPATH=. python -m scripts.h2_supply_scenario
Out:  code/results/h2_supply_scenario.csv + console
"""
from __future__ import annotations

import pandas as pd

from src.Config import RESULTS_DIR
from src.Economics import (compute_lcoh, H2_MULT_BY_COUNTRY,
                          H2_MULT_RANGE_BY_COUNTRY)

COUNTRIES = ["AT", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EE", "EL", "ES",
             "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL",
             "PL", "PT", "RO", "SE", "SI", "SK", "UK"]


def main() -> None:
    rows = []
    for c in COUNTRIES:
        lo, ce, hi = H2_MULT_RANGE_BY_COUNTRY.get(c, (None, H2_MULT_BY_COUNTRY.get(c, 1.0), None))
        central = H2_MULT_BY_COUNTRY.get(c, 1.0)
        try:
            hp = min(compute_lcoh("hp_air", c, 2050), compute_lcoh("hp_ground", c, 2050))
            # central uses the model's own H2_MULT; low/high scale relative to it
            h2_lo = compute_lcoh("h2_boiler", c, 2050, price_mult={"hydrogen": lo / central})
            h2_ce = compute_lcoh("h2_boiler", c, 2050)
            h2_hi = compute_lcoh("h2_boiler", c, 2050, price_mult={"hydrogen": hi / central})
        except Exception as e:
            print(f"  [skip] {c}: {e}")
            continue
        rows.append({
            "country": c,
            "h2_mult_low": lo, "h2_mult_central": ce, "h2_mult_high": hi,
            "best_hp_2050": round(hp, 1),
            "h2_2050_low": round(h2_lo, 1),
            "h2_2050_central": round(h2_ce, 1),
            "h2_2050_high": round(h2_hi, 1),
            "gap_low": round(h2_lo - hp, 1),
            "gap_central": round(h2_ce - hp, 1),
            "gap_high": round(h2_hi - hp, 1),
        })
    df = pd.DataFrame(rows).sort_values("gap_central")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "h2_supply_scenario.csv", index=False)

    print(f"{'ctry':<5}{'mult (lo/ce/hi)':>20}{'best_HP':>9}   {'H2-HP gap central [lo-hi]':>26}")
    for _, r in df.iterrows():
        mult = f"{r.h2_mult_low:.2f}/{r.h2_mult_central:.2f}/{r.h2_mult_high:.2f}"
        gap = f"{r.gap_central:.0f} [{r.gap_low:.0f}-{r.gap_high:.0f}]"
        print(f"{r.country:<5}{mult:>20}{r.best_hp_2050:>9.0f}   {gap:>26}")

    def parity(col):
        return int((df[col] <= 0).sum())
    print(f"\nCountries at heat-pump parity (gap<=0) in 2050:")
    print(f"  central {parity('gap_central')}  /  H2-cheap (low) {parity('gap_low')}"
          f"  /  H2-dear (high) {parity('gap_high')}")
    print(f"EU-mean H2-HP gap: central {df.gap_central.mean():.0f} "
          f"[low {df.gap_low.mean():.0f} - high {df.gap_high.mean():.0f}]")
    print(f"\nWrote {RESULTS_DIR / 'h2_supply_scenario.csv'}")


if __name__ == "__main__":
    main()
