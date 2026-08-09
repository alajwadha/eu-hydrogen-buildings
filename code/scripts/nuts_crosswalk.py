"""Derive a NUTS 2016 -> NUTS 2021 correspondence for the demand build.

Why this exists. The bottom-up building-stock build carries NUTS 2016 region codes,
while the NUTS3 map is drawn on the NUTS 2021 layer. Between the two vintages Eurostat
re-coded and in places redrew regions: Croatia's counties moved from HR04x to
HR02x/HR05x/HR06x, Belgium's Hainaut and Limburg arrondissements were renumbered and
partly merged, Sardinia's provinces were reorganised, Estonia and one German district
were renumbered, and the United Kingdom was re-coded. Joining the build to the 2021
layer on the raw code therefore fails silently for those regions, and they render as
"no data" grey on a map that is in fact fully modelled.

How the correspondence is derived. Not by hand and not from a lookup table typed out
here, but from the geometries themselves: for every build code absent from the 2021
layer, we intersect its 2016 polygon with every 2021 polygon in the same country and
keep the overlaps above one per cent of the old area, normalised to sum to one. The
result is an area weight, so a pure re-code gets weight 1.0, a merger sends several old
regions to one new region, and a genuine boundary change splits the old region's value
across its successors in proportion to overlapping area.

The derived weights are corroborated by the region names carried in both geometry
files: for the pure re-codes the old and new names are identical (HR041 "Grad Zagreb"
-> HR050 "Grad Zagreb"), and the mergers are named as such (BE324 "Arr. Mouscron" and
BE327 "Arr. Tournai" -> BE328 "Arr. Tournai-Mouscron").

Caveat worth stating: area weighting assumes demand is spread evenly within an old
region, which it is not. It is exact for the pure re-codes and the mergers, and
approximate only for the handful of genuinely redrawn regions.

Run:  cd code && PYTHONPATH=. python -m scripts.nuts_crosswalk
Out:  code/data/processed/nuts2016_to_2021_crosswalk.csv
"""
from __future__ import annotations
import json
from pathlib import Path

import pandas as pd
from shapely.geometry import shape
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "raw" / "nuts2json"
PROC = ROOT / "data" / "processed"
MIN_SHARE = 0.01          # ignore slivers below one per cent of the old region


def load(year: int) -> dict[str, tuple[str, object]]:
    src = GEO / f"nutsrg_3_{year}_4326_20M.json"
    feats = json.load(open(src, encoding="utf-8"))["features"]
    return {f["properties"]["id"]: (f["properties"].get("na"),
                                    make_valid(shape(f["geometry"])))
            for f in feats}


def build_crosswalk() -> pd.DataFrame:
    g16, g21 = load(2016), load(2021)
    stock = pd.read_csv(PROC / "building_stock_nuts3_bottomup.csv")
    codes = set(stock.nuts_id.unique())
    orphans = sorted(c for c in codes if c not in g21 and c in g16)
    unresolvable = sorted(c for c in codes if c not in g21 and c not in g16)

    rows = []
    for old in orphans:
        old_name, geo = g16[old]
        area = geo.area
        for new, (new_name, geo2) in g21.items():
            if new[:2] != old[:2]:
                continue
            try:
                inter = geo.intersection(geo2).area
            except Exception:
                continue
            if area and inter / area > MIN_SHARE:
                rows.append({"old": old, "old_name": old_name, "new": new,
                             "new_name": new_name, "weight": inter / area})
    xw = pd.DataFrame(rows)
    xw["weight"] = xw.weight / xw.groupby("old").weight.transform("sum")
    xw = xw.sort_values(["old", "weight"], ascending=[True, False]).reset_index(drop=True)

    print(f"build codes                     : {len(codes)}")
    print(f"absent from the 2021 layer      : {len(orphans) + len(unresolvable)}")
    print(f"  resolved via 2016 geometry    : {len(orphans)} -> {xw.new.nunique()} regions")
    print(f"  unresolvable (absent from both): {unresolvable or 'none'}")
    exact = xw.groupby("old").weight.max()
    print(f"pure re-codes / mergers (w >= 0.95): {(exact >= 0.95).sum()}")
    print(f"genuinely split regions            : {(exact < 0.95).sum()}")
    return xw


def main() -> None:
    xw = build_crosswalk()
    PROC.mkdir(parents=True, exist_ok=True)
    out = PROC / "nuts2016_to_2021_crosswalk.csv"
    xw.to_csv(out, index=False)
    print(f"\nwrote {out} ({len(xw)} rows)")


if __name__ == "__main__":
    main()
