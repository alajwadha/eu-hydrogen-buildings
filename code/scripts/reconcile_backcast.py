"""Vintage-matched reconciliation of the bottom-up model against Hotmaps 2015.

The bottom-up demand is a BASE_YEAR (2025) snapshot (EUBUCCO ~2020-2023 stock x
TABULA design intensity). Comparing it directly to the Hotmaps 2015 benchmark
mixes two vintages roughly a decade apart. This script backcasts the 2025
snapshot to 2015 along each country's historical net demand trend
(Config.backcast_factor, sourced in demand_trajectory.csv) so the comparison is
vintage-matched, then reports both the raw (snapshot-vs-Hotmaps) and the
vintage-matched (backcast-2015-vs-Hotmaps) gaps side by side.

Bands (on the vintage-matched gap): OK +/-15%, ACC +/-25%, INV >+/-25%.

Run:  python code/scripts/reconcile_backcast.py
Out:  code/results/reconcile_backcast.csv  (+ printed table)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))

import Config as C  # noqa: E402


def _national_twh(csv_path: Path) -> pd.Series:
    df = pd.read_csv(csv_path)
    return df.groupby("country")["heat_2015_MWh"].sum() / 1e6


def _verdict(gap_pct: float) -> str:
    a = abs(gap_pct)
    if a <= 15.0:
        return "OK"
    if a <= 25.0:
        return "ACC"
    return "INV"


def main() -> None:
    hotmaps_path = C.PROCESSED_DIR / "building_stock_nuts3.csv"
    bottom_path = C.PROCESSED_DIR / "building_stock_nuts3_bottomup.csv"
    if not hotmaps_path.exists() or not bottom_path.exists():
        raise FileNotFoundError(
            "Need both building_stock_nuts3.csv (Hotmaps 2015) and "
            "building_stock_nuts3_bottomup.csv (bottom-up). Run the builds first."
        )

    hotmaps = _national_twh(hotmaps_path)          # 2015 benchmark
    snapshot = _national_twh(bottom_path)          # model BASE_YEAR (2025)

    rows = []
    for cc in sorted(snapshot.index):
        hm = float(hotmaps.get(cc, float("nan")))
        snap = float(snapshot[cc])
        f15 = C.backcast_factor(cc, 2015)
        back15 = snap * f15
        traj = C._STOCK_GROWTH.get(cc, {})
        conf = traj.get("confidence", "DEFAULT")
        raw_gap = (snap - hm) / hm * 100.0 if hm == hm and hm > 0 else float("nan")
        vm_gap = (back15 - hm) / hm * 100.0 if hm == hm and hm > 0 else float("nan")
        rows.append({
            "country": cc,
            "hotmaps_2015_TWh": round(hm, 2),
            "model_2025_snapshot_TWh": round(snap, 2),
            "backcast_factor_2015": round(f15, 4),
            "model_2015_backcast_TWh": round(back15, 2),
            "raw_gap_pct": round(raw_gap, 1),
            "vintage_matched_gap_pct": round(vm_gap, 1),
            "verdict_vm": _verdict(vm_gap) if vm_gap == vm_gap else "n/a",
            "trend_conf": conf,
        })

    out = pd.DataFrame(rows)

    # EU total row (countries with a Hotmaps value)
    valid = out["hotmaps_2015_TWh"].notna() & (out["hotmaps_2015_TWh"] > 0)
    hm_tot = out.loc[valid, "hotmaps_2015_TWh"].sum()
    snap_tot = out.loc[valid, "model_2025_snapshot_TWh"].sum()
    back_tot = out.loc[valid, "model_2015_backcast_TWh"].sum()
    eu = {
        "country": "EU(sum)",
        "hotmaps_2015_TWh": round(hm_tot, 1),
        "model_2025_snapshot_TWh": round(snap_tot, 1),
        "backcast_factor_2015": round(back_tot / snap_tot, 4) if snap_tot else float("nan"),
        "model_2015_backcast_TWh": round(back_tot, 1),
        "raw_gap_pct": round((snap_tot - hm_tot) / hm_tot * 100.0, 1) if hm_tot else float("nan"),
        "vintage_matched_gap_pct": round((back_tot - hm_tot) / hm_tot * 100.0, 1) if hm_tot else float("nan"),
        "verdict_vm": "",
        "trend_conf": "",
    }
    out = pd.concat([out, pd.DataFrame([eu])], ignore_index=True)

    res_dir = ROOT / "code" / "results"
    res_dir.mkdir(parents=True, exist_ok=True)
    out_path = res_dir / "reconcile_backcast.csv"
    out.to_csv(out_path, index=False)

    print(f"BASE_YEAR = {C.BASE_YEAR}; backcast target = 2015")
    print(out.to_string(index=False))
    n = out.iloc[:-1]
    counts = n["verdict_vm"].value_counts().to_dict()
    print(f"\nVintage-matched verdicts: {counts}")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
