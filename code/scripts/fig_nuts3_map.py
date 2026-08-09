"""NUTS3 map of the bottom-up useful residential heat demand.

Supersedes the p01() panel in scripts/paper_figures.py, which joined the demand build
to the NUTS 2021 layer on the raw region code. The build carries NUTS 2016 codes, so
that join failed silently for 40 regions across Croatia, Belgium, Sardinia, Estonia,
Germany and the United Kingdom, and they were drawn in the "no data" grey even though
they are fully modelled. Here the build is first remapped through the area-weighted
2016 -> 2021 correspondence derived in scripts/nuts_crosswalk.py.

The remaining grey is genuine and is now stated on the figure: regions outside the
29-country study area (Norway, Iceland, the western Balkans, Türkiye and
Liechtenstein), which the NUTS layer carries but the model does not cover.

The five French overseas departments are modelled nowhere in the build and lie outside
the map frame in any case; the Canary Islands, Azores and Madeira are modelled but sit
outside the frame, so the map covers continental Europe only.

Run:  cd code && PYTHONPATH=. python -m scripts.fig_nuts3_map
Out:  paper/figs/paper/P01_nuts3_map.{png,pdf}
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Patch
from matplotlib.collections import PatchCollection
from matplotlib.colors import LogNorm
from scripts._figstyle import set_style

set_style()
plt.rcParams.update({"figure.autolayout": False, "savefig.bbox": "tight",
                     "axes.grid": False})

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "raw" / "nuts2json" / "nutsrg_3_2021_4326_20M.json"
PROC = ROOT / "data" / "processed"
OUT = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"

STUDY = set("AT BE BG HR CY CZ DK EE FI FR DE EL HU IE IT LV LT LU MT NL PL PT "
            "RO SK SI ES SE UK CH".split())
MISSING = "#e8e8e8"
# 0.05 to 30 spanned nearly three decades while the middle 80 per cent of regions sit
# between 0.76 and 5.5 TWh, so almost every region rendered in the same saturated red and
# the map carried no information. The scale is now the 2nd-to-98th percentile of the data
# it draws, rounded outward to decade-friendly bounds, with the colourbar extended at both
# ends so the 2.4 per cent of regions outside the range are still visibly outside it.
VMIN, VMAX = 0.3, 12.0


def demand_2021() -> pd.Series:
    """Per-region useful heat demand (TWh) on NUTS 2021 codes.

    Two regions (Landau in der Pfalz and Sefton) are absent from the bottom-up build
    but are estimated in the model's regional demand table. We fall back to that
    estimate, rescaled by the country's median ratio between the two builds so the
    filled regions sit on the same basis as the rest of the map.
    """
    stock = pd.read_csv(PROC / "building_stock_nuts3_bottomup.csv")
    # heat_2015_MWh is a legacy column name from the first build and NOT a 2015 vintage:
    # it sums to 3,827.4 TWh, which is the model's 2025 base year to the decimal, against
    # the Hotmaps 2015 regional benchmark of 3,863.3. A referee read the name and concluded the caption's
    # year was wrong. It is not; the name is.
    dem = stock.groupby("nuts_id").heat_2015_MWh.sum() / 1e6
    xw = pd.read_csv(PROC / "nuts2016_to_2021_crosswalk.csv")
    moved = dem.index.intersection(xw.old.unique())
    remapped = (xw[xw.old.isin(moved)]
                .assign(twh=lambda d: d.old.map(dem) * d.weight)
                .groupby("new").twh.sum())
    dem = dem.drop(index=moved)                       # drop the stale 2016 codes
    dem = dem.add(remapped, fill_value=0.0)           # add (EE008 already holds data)

    reg = pd.read_csv(PROC / "heat_demand_by_region" / "heat_demand_NUTS3_all.csv")
    reg = reg[reg.nuts_level == 3].set_index("nuts_id").heat_TWh
    # Only regions that genuinely exist in the 2021 layer and still carry no demand.
    valid = {f["properties"]["id"]
             for f in json.load(open(GEO, encoding="utf-8"))["features"]}
    have = set(dem[dem > 0].index)
    gap = pd.Index(sorted(i for i in reg.index
                          if i in valid and i[:2] in STUDY and i not in have))
    if len(gap):
        both = dem.index.intersection(reg.index)
        ratio = (dem[both] / reg[both]).groupby(
            [i[:2] for i in both]).median()            # bottom-up / regional, per country
        fill = pd.Series({g: reg[g] * ratio.get(g[:2], 1.0) for g in gap})
        print(f"filled from the regional table: "
              + ", ".join(f"{g} {v:.2f} TWh" for g, v in fill.items()))
        dem = dem.add(fill, fill_value=0.0)
    return dem


def poly_paths(geom):
    """GeoJSON Polygon / MultiPolygon -> matplotlib Paths (holes preserved)."""
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poly in polys:
        verts, codes = [], []
        for ring in poly:
            if len(ring) < 3:
                continue
            verts.extend(ring)
            codes.extend([MplPath.MOVETO] + [MplPath.LINETO] * (len(ring) - 2)
                         + [MplPath.CLOSEPOLY])
        if verts:
            out.append(MplPath(np.asarray(verts), codes))
    return out


def nuts3_map():
    feats = json.load(open(GEO, encoding="utf-8"))["features"]
    dem = demand_2021()

    cmap = matplotlib.colormaps["YlOrRd"]
    norm = LogNorm(vmin=VMIN, vmax=VMAX)
    fig, ax = plt.subplots(figsize=(5.6, 5.6))

    patches, colours = [], []
    drawn = grey = 0
    for f in feats:
        nid = f["properties"]["id"]
        v = dem.get(nid)
        col = cmap(norm(v)) if v and v > 0 else MISSING
        if v and v > 0:
            drawn += 1
        elif nid[:2] in STUDY:
            grey += 1
        for p in poly_paths(f["geometry"]):
            patches.append(PathPatch(p))
            colours.append(col)
    ax.add_collection(PatchCollection(patches, facecolor=colours, edgecolor="white",
                                      linewidth=0.08, match_original=False))

    # National borders, drawn over the NUTS3 fill. Without them every internal boundary is
    # the same thin white line, so a reader cannot see where one country ends, and the
    # caption's whole claim is that the gradient INSIDE a country is what a country average
    # suppresses. Built by unioning each country's NUTS3 outlines rather than loading a
    # second layer, so the borders can never disagree with the regions they enclose.
    for cc in sorted(STUDY):
        outline = [p for f in feats if f["properties"]["id"][:2] == cc
                   for p in poly_paths(f["geometry"])]
        if outline:
            ax.add_collection(PatchCollection(
                [PathPatch(p) for p in outline], facecolor="none",
                edgecolor="#4a4a4a", linewidth=0.32, match_original=False, zorder=4))

    ax.set_xlim(-12, 34); ax.set_ylim(34, 71)
    ax.set_aspect(1 / np.cos(np.radians(52.5)))       # equirectangular, mid-latitude
    ax.axis("off")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cb = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.01, extend="both")
    cb.set_label("Useful residential heat (TWh/yr, log scale)", fontsize=7.5)
    # A log colourbar labels its MINOR ticks too, and matplotlib draws those at 0.7x the
    # major size. At 7 pt that is 4.9 pt declared, which printed at 4.65 pt once the figure
    # was included in the narrower Applied Energy column and put the map under the 6 pt
    # floor on its own. Label the decades explicitly and leave the minor ticks unlabelled.
    import matplotlib.ticker as mticker
    cb.ax.yaxis.set_major_locator(mticker.FixedLocator([0.3, 1, 3, 10]))
    cb.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
    cb.ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    cb.ax.tick_params(labelsize=7, which="major")
    cb.ax.tick_params(which="minor", labelleft=False, labelright=False)
    ax.legend(handles=[Patch(facecolor=MISSING, edgecolor="white",
                             label="Outside the study area")],
              loc="lower left", fontsize=7, frameon=False,
              bbox_to_anchor=(-0.02, -0.045))

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"P01_nuts3_map.{ext}")
    plt.close(fig)
    print(f"regions drawn with data      : {drawn}")
    print(f"study-area regions still grey: {grey}")
    print("wrote P01_nuts3_map.{png,pdf}")


if __name__ == "__main__":
    nuts3_map()
