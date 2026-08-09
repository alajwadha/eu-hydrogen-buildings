"""
figures.py — Publication figures for the EU hydrogen-buildings working paper
=============================================================================

Complements the per-country diagnostic PDF (04_diagnostics.py) with the two
figure types that 04 cannot produce:

  1. NUTS3 choropleth maps    — spatial distribution of residential heat
                                demand / intensity / building count within
                                a country.
  2. Cross-country comparison — LU / FR (/ DE / BE ...) side by side:
                                model-vs-Hotmaps validation, average heat
                                intensity, and building-stock composition.

The single-country diagnostic panels (reconciliation, class x cohort,
intensity-vs-vintage, sensitivity tornado, ...) already live in
04_diagnostics.py and are deliberately NOT duplicated here.

Usage
-----
  python code/scripts/figures.py --maps FR LU
  python code/scripts/figures.py --compare LU FR
  python code/scripts/figures.py --all          # every country with data

Outputs PNG (300 dpi) and PDF into paper/figs/.

NUTS3 boundary data
-------------------
The choropleth maps need GISCO NUTS3 polygons. If
code/data/raw/gisco/NUTS_RG_01M_2021_4326_LEVL_3.geojson is not present it is
downloaded once from the EC GISCO distribution and cached there. The boundary
file is large and gitignored; it is regenerable from this download.

Inputs (produced by scripts 02 and 03)
--------------------------------------
  code/data/processed/{cc}/{CC}_buildings_with_heat_demand.parquet   (maps)
  code/data/processed/{cc}/{CC}_reconciliation_with_hotmaps.csv      (compare)
  code/data/processed/{cc}/{CC}_heat_intensity_summary.csv           (compare)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# ── Repo plumbing ────────────────────────────────────────────────────────────
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]                # code/scripts/figures.py
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))

from Visualise import WONG_PALETTE              # noqa: E402
from CountryConfig import load_country_config   # noqa: E402

PROCESSED      = REPO_ROOT / "code" / "data" / "processed"
GISCO_DIR      = REPO_ROOT / "code" / "data" / "raw" / "gisco"
FIG_DIR        = REPO_ROOT / "paper" / "figs"
NUTS3_GEOJSON  = GISCO_DIR / "NUTS_RG_01M_2021_4326_LEVL_3.geojson"
NUTS3_URL      = ("https://gisco-services.ec.europa.eu/distribution/v2/nuts/"
                  "geojson/NUTS_RG_01M_2021_4326_LEVL_3.geojson")

# ── Style (compact version of the 04_diagnostics OIES style) ─────────────────
SANS = ["Liberation Sans", "Helvetica", "Arial", "DejaVu Sans"]

C_OURS    = WONG_PALETTE["blue"]
C_HOTMAPS = "#444444"
CLASS_ORDER  = ["SFH", "MFH_LOW", "MFH_HIGH"]
CLASS_COLORS = {
    "SFH":      WONG_PALETTE["blue"],
    "MFH_LOW":  WONG_PALETTE["orange"],
    "MFH_HIGH": WONG_PALETTE["green"],
}
# Country bar colours for the comparison panels
COUNTRY_CYCLE = [WONG_PALETTE["blue"], WONG_PALETTE["orange"],
                 WONG_PALETTE["green"], WONG_PALETTE["red"],
                 WONG_PALETTE["purple"], WONG_PALETTE["sky"]]


def _apply_style() -> None:
    mpl.rcParams.update({
        "figure.dpi":         150,
        "savefig.dpi":        300,
        "savefig.bbox":       "tight",
        "savefig.pad_inches": 0.05,
        "font.family":        SANS,
        "font.sans-serif":    SANS,
        "font.size":          10,
        "axes.titlesize":     12,
        "axes.titleweight":   "bold",
        "axes.titlelocation": "left",
        "axes.titlepad":      8,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.linewidth":     0.7,
        "axes.edgecolor":     "#333333",
        "axes.labelcolor":    "#333333",
        "xtick.color":        "#333333",
        "ytick.color":        "#333333",
        "legend.fontsize":    9,
        "legend.frameon":     False,
        "pdf.fonttype":       42,
        "ps.fonttype":        42,
    })


def _save(fig, name: str) -> None:
    """Write a figure as both PNG and PDF into paper/figs/."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG_DIR / f"{name}.{ext}")
    plt.close(fig)
    print(f"  wrote paper/figs/{name}.png  +  .pdf")


# ─────────────────────────────────────────────────────────────────────────────
# Data access
# ─────────────────────────────────────────────────────────────────────────────

def _has_country_data(cc: str) -> bool:
    """True if scripts 02+03 outputs exist for this country code."""
    cc_lower = cc.lower()
    return (PROCESSED / cc_lower /
            f"{cc}_buildings_with_heat_demand.parquet").exists()


def _available_countries() -> list[str]:
    """Country codes (upper-case) that have a heat-demand parquet on disk."""
    found = []
    if PROCESSED.is_dir():
        for sub in sorted(PROCESSED.iterdir()):
            if not sub.is_dir():
                continue
            cc = sub.name.upper()
            if _has_country_data(cc):
                found.append(cc)
    return found


def heat_by_nuts3(cc: str) -> pd.DataFrame:
    """Aggregate the heat-demand parquet to one row per NUTS3 region.

    Returns columns: nuts3, heat_twh, heated_area_m2, n_buildings,
    intensity_kwh_m2. Residential classes only (NON_RESIDENTIAL is excluded
    because the model carries zero heated area for it).
    """
    aug = PROCESSED / cc.lower() / f"{cc}_buildings_with_heat_demand.parquet"
    if not aug.exists():
        raise FileNotFoundError(
            f"{aug} not found — run scripts 02 and 03 for {cc} first.")
    df = pd.read_parquet(aug, columns=["nuts3", "building_class",
                                       "heat_demand_kwh_yr",
                                       "heated_floor_area_m2"])
    res = df[df["building_class"] != "NON_RESIDENTIAL"]
    g = res.groupby("nuts3", observed=True).agg(
        heat_kwh=("heat_demand_kwh_yr", "sum"),
        heated_area_m2=("heated_floor_area_m2", "sum"),
        n_buildings=("heat_demand_kwh_yr", "size"),
    ).reset_index()
    g["heat_twh"] = g["heat_kwh"] / 1e9
    g["intensity_kwh_m2"] = np.where(
        g["heated_area_m2"] > 0, g["heat_kwh"] / g["heated_area_m2"], np.nan)
    return g[["nuts3", "heat_twh", "heated_area_m2",
              "n_buildings", "intensity_kwh_m2"]]


def country_summary(cc: str) -> dict:
    """Headline numbers for one country, from its reconciliation + summary CSVs."""
    cc_lower = cc.lower()
    rec_path = PROCESSED / cc_lower / f"{cc}_reconciliation_with_hotmaps.csv"
    sum_path = PROCESSED / cc_lower / f"{cc}_heat_intensity_summary.csv"
    if not rec_path.exists() or not sum_path.exists():
        raise FileNotFoundError(
            f"Reconciliation/summary CSV missing for {cc} — run script 03.")
    rec = pd.read_csv(rec_path)
    summ = pd.read_csv(sum_path)

    def _rec(query: str) -> float:
        m = rec[rec["source"].str.contains(query, regex=False)]
        return float(m["twh_yr"].iloc[0]) if not m.empty else np.nan

    res = summ[summ["building_class"] != "NON_RESIDENTIAL"]
    area_by_class = res.groupby("building_class")["total_heated_area_m2"].sum()
    total_area = float(area_by_class.sum())
    total_demand_twh = float(res["total_demand_twh_yr"].sum())
    avg_intensity = (total_demand_twh * 1e9 / total_area
                     if total_area > 0 else np.nan)

    cfg = load_country_config(cc)
    return {
        "cc":            cc,
        "name":          cfg.country_name,
        "bottom_up":     _rec("Bottom-up: residential only"),
        "hotmaps":       _rec("Hotmaps"),
        "bso":           _rec("EU BSO"),
        "odyssee":       _rec("Odyssee-Mure"),
        "avg_intensity": avg_intensity,
        "class_share":   {c: float(area_by_class.get(c, 0.0)) / total_area
                          if total_area > 0 else 0.0
                          for c in CLASS_ORDER},
    }


def _load_nuts3_boundaries():
    """Return a GeoDataFrame of GISCO NUTS3 polygons, downloading once if needed."""
    import geopandas as gpd
    if not NUTS3_GEOJSON.exists():
        import requests
        print(f"  NUTS3 boundaries not cached — downloading from GISCO ...")
        GISCO_DIR.mkdir(parents=True, exist_ok=True)
        resp = requests.get(NUTS3_URL, timeout=180)
        resp.raise_for_status()
        NUTS3_GEOJSON.write_bytes(resp.content)
        print(f"  cached -> {NUTS3_GEOJSON.relative_to(REPO_ROOT)} "
              f"({len(resp.content)/1024:.0f} KB)")
    # Prefer the pyogrio engine (a project dependency): it avoids a known
    # fiona-version incompatibility and is faster on large GeoJSON.
    try:
        return gpd.read_file(NUTS3_GEOJSON, engine="pyogrio")
    except Exception:                                  # noqa: BLE001
        return gpd.read_file(NUTS3_GEOJSON)


# ─────────────────────────────────────────────────────────────────────────────
# Figure: NUTS3 choropleth map
# ─────────────────────────────────────────────────────────────────────────────

_METRICS = {
    "heat_twh": ("Residential heat demand (TWh/yr)", "YlOrRd"),
    "intensity_kwh_m2": ("Mean residential heat intensity "
                         "(kWh m⁻² yr⁻¹)", "YlOrRd"),
    "n_buildings": ("Residential building count", "viridis"),
}


def make_nuts3_map(cc: str, metric: str = "heat_twh") -> None:
    """Choropleth of one metric across a country's NUTS3 regions."""
    if metric not in _METRICS:
        raise ValueError(f"metric must be one of {list(_METRICS)}")
    cfg = load_country_config(cc)
    data = heat_by_nuts3(cc)
    bnd = _load_nuts3_boundaries().rename(columns={"NUTS_ID": "nuts3"})

    merged = bnd.merge(data, on="nuts3", how="inner")
    if merged.empty:
        print(f"  [{cc}] no NUTS3 polygons matched the data — skipping map "
              f"(are the nuts3 codes GISCO NUTS3 IDs?)")
        return
    if len(merged) < 2:
        print(f"  [{cc}] only {len(merged)} NUTS3 region(s) — a choropleth "
              f"is not meaningful; skipping map.")
        return

    merged = merged.to_crs("EPSG:3035")          # equal-area for Europe
    label, cmap = _METRICS[metric]

    fig, ax = plt.subplots(figsize=(6.6, 6.8))
    merged.plot(column=metric, ax=ax, cmap=cmap, legend=True,
                edgecolor="white", linewidth=0.25,
                legend_kwds={"label": label, "shrink": 0.55,
                             "pad": 0.01})
    ax.set_axis_off()
    short = label.split("(")[0].strip()
    ax.set_title(f"{cfg.country_name}: {short.lower()} by NUTS3 region",
                 loc="left", fontweight="bold", fontsize=12, pad=10)
    ax.text(0.0, -0.02,
            f"{len(merged)} NUTS3 regions  |  EUBUCCO v0.2 + TABULA "
            f"bottom-up  |  EPSG:3035",
            transform=ax.transAxes, fontsize=7.5, color="#666666",
            va="top", ha="left")
    _save(fig, f"map_{cc}_{metric}")


# ─────────────────────────────────────────────────────────────────────────────
# Figure: cross-country comparison (3 panels, one file each)
# ─────────────────────────────────────────────────────────────────────────────

def make_comparison(country_codes: list[str]) -> None:
    """Cross-country comparison figures from each country's CSVs."""
    summaries = []
    for cc in country_codes:
        try:
            summaries.append(country_summary(cc))
        except FileNotFoundError as exc:
            print(f"  skipping {cc}: {exc}")
    if not summaries:
        print("  no countries with data — nothing to compare.")
        return
    if len(summaries) == 1:
        print(f"  only {summaries[0]['cc']} has data — comparison figures "
              f"need >=2 countries; rendering single-country versions anyway.")

    names  = [s["name"] for s in summaries]
    x      = np.arange(len(summaries))

    # Panel A — model validation: bottom-up vs Hotmaps, per country
    fig, ax = plt.subplots(figsize=(7, 4.2))
    bw = 0.36
    ax.bar(x - bw / 2, [s["bottom_up"] for s in summaries], bw,
           color=C_OURS, label="Bottom-up (this study)")
    ax.bar(x + bw / 2, [s["hotmaps"] for s in summaries], bw,
           color=C_HOTMAPS, label="Hotmaps baseline")
    for i, s in enumerate(summaries):
        if s["hotmaps"] and not np.isnan(s["hotmaps"]):
            dev = (s["bottom_up"] - s["hotmaps"]) / s["hotmaps"] * 100
            top = max(s["bottom_up"], s["hotmaps"])
            ax.text(i, top * 1.04, f"{dev:+.0f}%", ha="center", va="bottom",
                    fontsize=9, color="#444444")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Residential heat demand (TWh/yr)")
    ax.grid(axis="y", linewidth=0.4, color="#dddddd", alpha=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left")
    ax.set_title("Model validation: bottom-up estimate vs Hotmaps, by country",
                 loc="left")
    _save(fig, "compare_validation")

    # Panel B — average residential heat intensity, per country
    fig, ax = plt.subplots(figsize=(7, 4.0))
    colors = [COUNTRY_CYCLE[i % len(COUNTRY_CYCLE)]
              for i in range(len(summaries))]
    ax.bar(x, [s["avg_intensity"] for s in summaries], 0.55, color=colors)
    for i, s in enumerate(summaries):
        ax.text(i, s["avg_intensity"] * 1.02, f"{s['avg_intensity']:.0f}",
                ha="center", va="bottom", fontsize=9.5, fontweight="bold",
                color="#222222")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Mean intensity (kWh m⁻² yr⁻¹)")
    ax.grid(axis="y", linewidth=0.4, color="#dddddd", alpha=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Average residential heat intensity, by country", loc="left")
    _save(fig, "compare_intensity")

    # Panel C — building-stock composition (share of heated floor area)
    fig, ax = plt.subplots(figsize=(7, 4.0))
    bottom = np.zeros(len(summaries))
    for cls in CLASS_ORDER:
        vals = np.array([s["class_share"].get(cls, 0.0) * 100
                         for s in summaries])
        ax.bar(x, vals, 0.55, bottom=bottom, color=CLASS_COLORS[cls],
               label=cls)
        for i, v in enumerate(vals):
            if v > 4:
                ax.text(i, bottom[i] + v / 2, f"{v:.0f}%", ha="center",
                        va="center", fontsize=8.5, color="white")
        bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Share of residential heated floor area (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=3)
    ax.set_title("Residential building-stock composition, by country",
                 loc="left")
    _save(fig, "compare_stock_composition")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--maps", nargs="*", metavar="CC",
                        help="country codes to render NUTS3 choropleth maps for")
    parser.add_argument("--compare", nargs="*", metavar="CC",
                        help="country codes to put in the comparison figures")
    parser.add_argument("--metric", default="heat_twh",
                        choices=list(_METRICS),
                        help="metric for the choropleth maps (default heat_twh)")
    parser.add_argument("--all", action="store_true",
                        help="maps for every country with data + a comparison "
                             "across all of them")
    args = parser.parse_args()

    if not (args.maps or args.compare or args.all):
        parser.error("nothing to do — pass --maps, --compare, or --all")

    _apply_style()
    print("=" * 64)
    print("figures.py — publication figures")
    print("=" * 64)

    available = _available_countries()
    print(f"Countries with processed data: "
          f"{', '.join(available) if available else '(none)'}")

    maps    = args.maps if args.maps is not None else []
    compare = args.compare if args.compare is not None else []
    if args.all:
        maps = available
        compare = available

    for cc in maps:
        cc = cc.upper()
        print(f"\nNUTS3 map — {cc} ({args.metric})")
        if not _has_country_data(cc):
            print(f"  no processed data for {cc}; skipping.")
            continue
        try:
            make_nuts3_map(cc, metric=args.metric)
        except Exception as exc:                      # noqa: BLE001
            print(f"  ERROR rendering {cc} map: {exc}")

    if compare:
        print(f"\nCross-country comparison — "
              f"{', '.join(c.upper() for c in compare)}")
        make_comparison([c.upper() for c in compare])

    print("\n" + "=" * 64)
    print(f"Done. Figures in {FIG_DIR.relative_to(REPO_ROOT)}/")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
