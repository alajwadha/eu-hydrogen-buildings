"""T5(b) -- multi-benchmark validation of the bottom-up residential heat demand.

Compares the model's bottom-up residential useful heat, per country, against the
THREE independent benchmarks already carried in each
{CC}_reconciliation_with_hotmaps.csv:
  - Hotmaps 2015 (the primary reconciliation benchmark; modelled useful heat);
  - EU BSO weighted-average implied total (per-cohort BSO intensities x stock);
  - Odyssee-MURE national residential (back-calculated; FINAL-energy basis, so a
    definitional gap vs useful demand is expected and flagged).
These come from independent data lineages, so agreement across them is a stronger
validation than against Hotmaps alone. (A fourth benchmark, JRC-IDEES residential
useful heat, is a planned addition once the IDEES residential module is pulled --
see literature/enhancement_tiers_design.md T5(b).)

Run:  cd code && PYTHONPATH=. python -m scripts.benchmark_multi
Out:  code/results/benchmark_multi.csv + console
"""
from __future__ import annotations

import glob
import os

import pandas as pd

from src.Config import RESULTS_DIR, PROCESSED_DIR


def _val(df: pd.DataFrame, key: str) -> float | None:
    m = df[df["source"].str.contains(key, case=False, na=False)]
    return float(m["twh_yr"].iloc[0]) if len(m) else None


def main() -> None:
    rows = []
    for f in sorted(glob.glob(str(PROCESSED_DIR / "*" / "??_reconciliation_with_hotmaps.csv"))):
        cc = os.path.basename(f)[:2].upper()
        d = pd.read_csv(f)
        bu = _val(d, "residential only")
        hm = _val(d, "Hotmaps")
        bso = _val(d, "BSO")
        ody = _val(d, "Odyssee")
        if bu is None:
            continue

        def gap(x):
            return round((bu - x) / x * 100, 1) if x else None
        rows.append({"country": cc, "bottomup_TWh": round(bu, 1),
                     "hotmaps_TWh": hm, "bso_TWh": bso, "odyssee_TWh": ody,
                     "gap_vs_hotmaps_pct": gap(hm), "gap_vs_bso_pct": gap(bso),
                     "gap_vs_odyssee_pct": gap(ody)})
    df = pd.DataFrame(rows)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_DIR / "benchmark_multi.csv", index=False)

    # EU aggregates + agreement summary
    eu = {c: df[c].sum() for c in ("bottomup_TWh", "hotmaps_TWh", "bso_TWh")}
    print("Per-country bottom-up vs three independent benchmarks (TWh, gap %):")
    print(df.to_string(index=False))
    print("\nEU totals (TWh):")
    print(f"  bottom-up {eu['bottomup_TWh']:.0f} | Hotmaps {eu['hotmaps_TWh']:.0f} "
          f"({(eu['bottomup_TWh']/eu['hotmaps_TWh']-1)*100:+.1f}%) | "
          f"EU BSO {eu['bso_TWh']:.0f} ({(eu['bottomup_TWh']/eu['bso_TWh']-1)*100:+.1f}%)")
    for col, lab in [("gap_vs_hotmaps_pct", "Hotmaps"), ("gap_vs_bso_pct", "EU BSO"),
                     ("gap_vs_odyssee_pct", "Odyssee")]:
        s = df[col].dropna()
        within15 = (s.abs() <= 15).sum()
        within25 = (s.abs() <= 25).sum()
        print(f"  vs {lab:8s}: median |gap| {s.abs().median():.1f}%, "
              f"{within15}/{len(s)} within +/-15%, {within25}/{len(s)} within +/-25%")
    print("\nNote: Odyssee is a FINAL-energy series; its gap vs useful demand is "
          "definitional (efficiency of conversion), not a model error.")
    print(f"Wrote {RESULTS_DIR / 'benchmark_multi.csv'}")


if __name__ == "__main__":
    main()
