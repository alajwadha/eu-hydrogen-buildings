"""Base-load win counts under each of the four hydrogen price paths.

The manuscript reports that the heat pump is cheapest on base load in 13 of the 29
markets on the rapid path, 22 on the central, 26 on the slow and 29 on the stranded,
and it uses that spread as the hedge on its own headline. Every one of those counts
reproduces from the model, but no committed artefact carried them: h2_gap_analysis.py
fixes h2_scenario="CENTRAL", so it can only ever print the 22, and h2_supply_scenario.csv
sweeps a different axis (the supply-route multiplier) and returns 15 / 22 / 26. A
referee looking for the price-path counts therefore found the supply-route counts
instead, which share two of their four values. This file writes them out so the
comparison is unambiguous and the gate can pin it.

The count is the number of markets where the best available heat pump undercuts the
hydrogen boiler on 2050 levelised cost, the same comparison the headline 22 rests on.

Run:  cd code && PYTHONPATH=. python -m scripts.h2_price_path_counts
Out:  code/results/h2_price_path_counts.csv + console
"""
from __future__ import annotations

import pandas as pd

from src.Config import EU_COUNTRIES, RESULTS_DIR
from src.Economics import compute_lcoh

PATHS = ("RAPID", "CENTRAL", "SLOW", "STRANDED")


def main() -> None:
    rows = []
    for path in PATHS:
        gaps = {}
        for c in EU_COUNTRIES:
            hp = min(compute_lcoh(t, c, 2050, h2_scenario=path)
                     for t in ("hp_air", "hp_ground"))
            gaps[c] = compute_lcoh("h2_boiler", c, 2050, h2_scenario=path) - hp
        wins = sorted(k for k, v in gaps.items() if v > 0)
        rows.append({
            "h2_price_path":   path,
            "hp_cheaper_count": len(wins),
            "h2_cheaper_count": len(EU_COUNTRIES) - len(wins),
            "median_gap_eur_mwh": round(pd.Series(gaps).median(), 1),
            "h2_cheaper_markets": ",".join(sorted(set(EU_COUNTRIES) - set(wins))),
        })

    df = pd.DataFrame(rows)
    out = RESULTS_DIR / "h2_price_path_counts.csv"
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
