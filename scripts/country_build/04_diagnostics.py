"""
04_diagnostics.py — Country-parameterised diagnostic figures (publication quality)
==================================================================================

Produces ONE publication-quality PDF from a country's processed outputs.

The eight panels:

  1. Headline reconciliation across four data sources
  2. Heat demand decomposition by class × cohort (single-hue heatmap)
  3. Intensity vs vintage curves (per class)
  4. Cohort-data coverage per class
  5. Sensitivity tornado
  6. Method comparison (top-down / fallback-dominated / per-vintage)
  7. Class-level reconciliation (grouped bars)
  8. Empirical construction-year distribution

Style
-----
Page size 7 × 5 in (178 × 127 mm) — OIES working paper full-width.
Serif headings (Liberation Serif, Times-compatible) + sans labels
(Liberation Sans, Helvetica-compatible). DejaVu fallbacks for portability.
Bar heights reduced to ~0.42 of slot for visual breathing space.
Gridlines on continuous-axis charts only, with alpha 0.20.
Two-to-three colour maximum per panel; Wong palette source of truth.

Inputs (must exist before this script runs; produced by 02 and 03)
------------------------------------------------------------------
  code/data/processed/{cc_lower}/
    {CC}_buildings_classified.parquet
    {CC}_buildings_with_heat_demand.parquet
    {CC}_heat_intensity_summary.csv
    {CC}_reconciliation_with_hotmaps.csv
  TABULA file: path from cfg.tabula_intensities_file
  code/data/raw/{cc_lower}_national/{cc_lower}_climate_retrofit.csv

Outputs
-------
  code/data/processed/{cc_lower}/{CC}_diagnostics_clean.pdf
  countries/{Country}/data/{CC}_diagnostics_clean.pdf            (mirror)

Usage
-----
  python code/scripts/country_build/04_diagnostics.py --country LU
  python code/scripts/country_build/04_diagnostics.py --country FR
"""

from __future__ import annotations

import sys
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap

# ── Repo plumbing ────────────────────────────────────────────────────────────
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[3]
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))

from Visualise import WONG_PALETTE  # noqa: E402
from CountryConfig import CountryConfig, load_country_config  # noqa: E402


def build_paths(cfg: CountryConfig) -> dict:
    """Per-country I/O paths used by the diagnostic generator."""
    cc = cfg.country_code
    cc_lower = cfg.cc_lower
    cname = cfg.country_name
    processed = REPO_ROOT / "code" / "data" / "processed" / cc_lower
    raw = REPO_ROOT / "code" / "data" / "raw"
    # Mirror dir must match the curated countries/<dir>/ name (see 02_classify).
    dir_cname = {"Czechia": "Czech-Republic"}.get(cname, cname.replace(" ", "-"))
    country = REPO_ROOT / "countries" / dir_cname / "data"
    return {
        "classified_parquet": processed / f"{cc}_buildings_classified.parquet",
        "heat_parquet":       processed / f"{cc}_buildings_with_heat_demand.parquet",
        "summary_csv":        processed / f"{cc}_heat_intensity_summary.csv",
        "reconcile_csv":      processed / f"{cc}_reconciliation_with_hotmaps.csv",
        "tabula_csv":         REPO_ROOT / cfg.tabula_intensities_file,
        "national_csv":       raw / f"{cc_lower}_national" / f"{cc_lower}_climate_retrofit.csv",
        "out_clean":          processed / f"{cc}_diagnostics_clean.pdf",
        "country_clean":      country / f"{cc}_diagnostics_clean.pdf",
    }

# ── Style: OIES working paper, full-width ────────────────────────────────────
# Use Liberation fonts (metric-compatible with Times / Helvetica) where
# available, fall back to DejaVu for cross-platform portability.
SERIF_STACK = ["Liberation Serif", "Times New Roman", "Times", "DejaVu Serif"]
SANS_STACK  = ["Liberation Sans", "Helvetica", "Arial", "DejaVu Sans"]

mpl.rcParams.update({
    # Geometry
    "figure.figsize":    (7.0, 5.0),    # 7 x 5 inches, OIES full-page width
    "figure.dpi":        150,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "savefig.pad_inches": 0.05,
    # Typography
    "font.family":       SANS_STACK,
    "font.sans-serif":   SANS_STACK,
    "font.serif":        SERIF_STACK,
    "font.size":         10,
    "axes.titlesize":    12,
    "axes.titleweight":  "bold",
    "axes.titlelocation":"left",
    "axes.titlepad":     8,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "legend.frameon":    False,
    "legend.handlelength": 1.5,
    # Axes
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.linewidth":     0.7,
    "axes.edgecolor":     "#333333",
    "axes.labelcolor":    "#333333",
    "xtick.color":        "#333333",
    "ytick.color":        "#333333",
    "xtick.major.size":   3,
    "ytick.major.size":   3,
    "xtick.major.width":  0.7,
    "ytick.major.width":  0.7,
    # Grid (off by default; turn on per-panel)
    "axes.grid":          False,
    "grid.linewidth":     0.4,
    "grid.color":         "#cccccc",
    "grid.alpha":         0.55,
    # Default colour cycle if used
    "axes.prop_cycle":    mpl.cycler(color=[
        WONG_PALETTE["blue"], WONG_PALETTE["orange"],
        WONG_PALETTE["green"], WONG_PALETTE["red"],
        WONG_PALETTE["purple"], WONG_PALETTE["sky"],
    ]),
    # PDF output: embed fonts (Type 42 == TrueType embedding)
    "pdf.fonttype":       42,
    "ps.fonttype":        42,
})

# Colour scheme — keep tight, only 3 source colours and 4 class colours
C_OURS      = WONG_PALETTE["blue"]
C_HOTMAPS   = "#444444"
C_BSO       = WONG_PALETTE["green"]
C_ODYSSEE   = WONG_PALETTE["orange"]

C_SFH       = WONG_PALETTE["blue"]
C_MFH_LOW   = WONG_PALETTE["orange"]
C_MFH_HIGH  = WONG_PALETTE["green"]
C_NONRES    = "#888888"

C_SUBTLE_GRID = "#dddddd"
C_TEXT_MUTED  = "#666666"

CLASS_COLORS = {
    "SFH":             C_SFH,
    "MFH_LOW":         C_MFH_LOW,
    "MFH_HIGH":        C_MFH_HIGH,
    "NON_RESIDENTIAL": C_NONRES,
}
CLASS_ORDER  = ["SFH", "MFH_LOW", "MFH_HIGH", "NON_RESIDENTIAL"]
COHORT_ORDER = ["pre-1945", "1946-1970", "1971-1990",
                "1991-2010", "2011-2020", "post-2020", "unknown"]

# Single-hue gradient for class*cohort heatmap (page 2)
HEATMAP_CMAP = LinearSegmentedColormap.from_list(
    "wong_blue", ["#f4f9fc", WONG_PALETTE["blue"]], N=256)


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────

def _read_columns(path, columns: list) -> pd.DataFrame:
    """Read selected columns from a parquet, dictionary-encoding the text
    columns so pandas receives compact 'category' dtype.

    At country scale (FR ~53 M rows) loading every column as object dtype
    would exhaust a standard runtime -- the same OOM that scripts 02 and 03
    were rewritten to avoid. The panels only need a handful of columns, so
    we read exactly those. Columns absent from the file are skipped.
    """
    import pyarrow.parquet as pq
    available = set(pq.ParquetFile(path).schema_arrow.names)
    cols = [c for c in columns if c in available]
    table = pq.read_table(path, columns=cols)
    for name in ("building_class", "cohort"):
        if name in table.column_names:
            idx = table.schema.get_field_index(name)
            table = table.set_column(
                idx, name, table.column(name).dictionary_encode())
    return table.to_pandas()


def load_all_data(paths: dict) -> dict:
    classified = paths["classified_parquet"]
    heat       = paths["heat_parquet"]
    summary    = paths["summary_csv"]
    reconcile  = paths["reconcile_csv"]
    tabula     = paths["tabula_csv"]
    national   = paths["national_csv"]
    missing = [p for p in (classified, heat, summary, reconcile, tabula, national)
               if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Required inputs missing — run scripts 02 and 03 first:\n  "
            + "\n  ".join(str(p) for p in missing)
        )

    # Read only the columns the panels actually use, memory-efficiently.
    # heat: panels 3/5/6.  classified: panels 4/8.
    heat_df = _read_columns(heat, ["building_class", "cohort",
                                   "intensity_kwh_m2_yr",
                                   "heated_floor_area_m2",
                                   "construction_year"])
    classified_df = _read_columns(classified, ["building_class",
                                               "construction_year"])

    return {
        "summary":    pd.read_csv(summary),
        "reconcile":  pd.read_csv(reconcile),
        "tabula":     pd.read_csv(tabula, comment="#"),
        "national":   pd.read_csv(national, comment="#"),
        "heat":       heat_df,
        "classified": classified_df,
    }


def national_param(national_df: pd.DataFrame, key: str) -> float:
    return float(national_df.loc[national_df["parameter"] == key, "value"].iloc[0])


# ─────────────────────────────────────────────────────────────────────────────
# Common figure helpers
# ─────────────────────────────────────────────────────────────────────────────

def _setup_axes(ax, ygrid: bool = False, xgrid: bool = False) -> None:
    """Apply consistent axis style: spine colour, tick direction, optional grid."""
    if ygrid:
        ax.grid(axis="y", which="major", linewidth=0.4,
                color=C_SUBTLE_GRID, alpha=0.8, zorder=0)
    if xgrid:
        ax.grid(axis="x", which="major", linewidth=0.4,
                color=C_SUBTLE_GRID, alpha=0.8, zorder=0)
    ax.set_axisbelow(True)


def _title(ax, text: str, pre: str = "") -> None:
    """Serif title, left-aligned, with optional 'Figure N — ' prefix."""
    if pre:
        ax.set_title(pre + text, fontfamily="serif",
                     fontsize=12, fontweight="bold", loc="left", pad=8)
    else:
        ax.set_title(text, fontfamily="serif",
                     fontsize=12, fontweight="bold", loc="left", pad=8)


# ─────────────────────────────────────────────────────────────────────────────
# Panel 1 — Headline reconciliation
# ─────────────────────────────────────────────────────────────────────────────

def panel1(data: dict):
    rec = data["reconcile"]
    bench = data["cfg"].reconciliation_benchmarks

    def _yr(key):
        y = bench.get(key, {}).get("year", "")
        return f" {y}" if y else ""

    # Benchmark years come from the country config, and the source-string
    # match is year-agnostic, so this panel is country-generic.
    rows = []
    for key, label, query, color in [
        ("ours",    "Bottom-up (this study)",             "Bottom-up: residential only", C_OURS),
        ("hotmaps", f"Hotmaps{_yr('hotmaps')}",           "Hotmaps",      C_HOTMAPS),
        ("bso",     f"EU BSO{_yr('eu_bso')}",             "EU BSO",       C_BSO),
        ("odyssee", f"Odyssee-Mure{_yr('odyssee_mure')}", "Odyssee-Mure", C_ODYSSEE),
    ]:
        m = rec[rec["source"].str.contains(query, regex=False)]
        if not m.empty:
            rows.append({"key":   key, "label": label,
                         "twh":   m["twh_yr"].iloc[0],
                         "kwh":   m["kwh_m2_yr_avg"].iloc[0],
                         "color": color})
    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(7, 4.2))

    hotmaps_twh = df.loc[df["key"] == "hotmaps", "twh"].iloc[0]
    ax.axvspan(hotmaps_twh * 0.85, hotmaps_twh * 1.15,
               color="#000000", alpha=0.06, zorder=1, linewidth=0)
    ax.axvline(hotmaps_twh, color=C_HOTMAPS, linestyle=":",
               linewidth=0.9, alpha=0.7, zorder=2)

    y = np.arange(len(df))
    ax.barh(y, df["twh"], color=df["color"], edgecolor="none",
            height=0.45, zorder=3)
    for i, row in df.iterrows():
        ax.text(row["twh"] + 0.12, i, f"{row['twh']:.2f} TWh",
                va="center", ha="left", fontsize=9.5, fontweight="bold",
                color="#222222")
        ax.text(row["twh"] + 0.12, i - 0.32,
                f"{row['kwh']:.0f} kWh m$^{{-2}}$",
                va="center", ha="left", fontsize=8.5,
                color=C_TEXT_MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels(df["label"])
    ax.invert_yaxis()
    ax.set_xlabel("Residential heat demand (TWh yr$^{-1}$)")
    ax.set_xlim(0, df["twh"].max() * 1.30)
    _setup_axes(ax, xgrid=True)
    _title(ax, f"Residential heat demand for {data['cfg'].country_name}, four data sources")

    # Subtle band annotation
    ax.text(hotmaps_twh, len(df) - 0.4,
            "  ±15 % of Hotmaps",
            fontsize=8, color=C_TEXT_MUTED, va="center", ha="left",
            zorder=4)

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 2 — Heat demand by class × cohort (heatmap)
# ─────────────────────────────────────────────────────────────────────────────

def panel2(data: dict):
    sm = data["summary"]
    pivot = sm.pivot_table(index="building_class", columns="cohort",
                           values="total_demand_twh_yr",
                           aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(index=[c for c in CLASS_ORDER if c in pivot.index],
                          fill_value=0)
    cols = [c for c in COHORT_ORDER if c in pivot.columns]
    pivot = pivot[cols]

    fig, ax = plt.subplots(figsize=(7, 3.6))

    # Asymmetric: use log for colour to handle the huge unknown/known ratio,
    # but linear text labels for readability.
    arr = pivot.values
    arr_for_color = np.log10(arr + 1e-3)  # +epsilon to avoid log(0)
    im = ax.imshow(arr_for_color, aspect="auto", cmap=HEATMAP_CMAP,
                   vmin=arr_for_color.min(),
                   vmax=arr_for_color.max())

    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, rotation=20, ha="right")
    ax.set_yticks(np.arange(len(pivot)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Construction cohort")
    ax.tick_params(top=False, right=False, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Cell labels in TWh
    for i in range(len(pivot)):
        for j in range(len(cols)):
            v = arr[i, j]
            if v < 0.01:
                s = "—"
                color = "#bbbbbb"
            elif v < 0.1:
                s = f"{v:.2f}"
                color = "#333333" if arr_for_color[i, j] < arr_for_color.max() * 0.5 else "white"
            else:
                s = f"{v:.2f}"
                color = "#333333" if arr_for_color[i, j] < arr_for_color.max() * 0.5 else "white"
            ax.text(j, i, s, ha="center", va="center", fontsize=8.5,
                    color=color)

    # Colour bar
    cbar = fig.colorbar(im, ax=ax, shrink=0.65, pad=0.02, aspect=18)
    cbar.set_label("Heat demand (TWh yr$^{-1}$, log scale)",
                   fontsize=9, labelpad=8)
    # Show actual TWh values on colour bar, not log values
    tick_vals_twh = [0.01, 0.1, 1.0, 5.0]
    cbar.set_ticks(np.log10([v + 1e-3 for v in tick_vals_twh]))
    cbar.set_ticklabels([str(v) for v in tick_vals_twh])
    cbar.outline.set_linewidth(0.5)

    _title(ax, "Heat demand by building class × construction cohort")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 3 — Intensity vs vintage curves
# ─────────────────────────────────────────────────────────────────────────────

def panel3(data: dict):
    tabula = data["tabula"].copy()
    heat = data["heat"]
    cfg = data["cfg"]

    # Read model parameters from CountryConfig (the YAML), not the national
    # CSV. The CSV's parameter names are country-specific (e.g.
    # 'climate_multiplier_lu_vs_be' vs 'climate_multiplier_fr_vs_proxy'),
    # which made this panel Luxembourg-only; cfg exposes them uniformly.
    climate_mult = cfg.climate_multiplier
    rs_orig = cfg.retrofit_share_original
    rs_std  = cfg.retrofit_share_standard
    rs_adv  = cfg.retrofit_share_advanced
    rf_std  = cfg.retrofit_factor_standard
    rf_adv  = cfg.retrofit_factor_advanced
    blend = rs_orig + rs_std * rf_std + rs_adv * rf_adv

    tabula["display_intensity"] = (tabula["sh_intensity_kwh_m2_yr"]
                                   * climate_mult * blend
                                   + tabula["dhw_intensity_kwh_m2_yr"])

    fig, ax = plt.subplots(figsize=(7, 4.2))

    cohort_to_x = {c: i for i, c in enumerate(
        [c for c in COHORT_ORDER if c != "unknown"])}

    for cls, color in [("SFH", C_SFH), ("MFH_LOW", C_MFH_LOW),
                       ("MFH_HIGH", C_MFH_HIGH)]:
        sub = tabula[(tabula["building_class"] == cls)
                     & (tabula["cohort"] != "unknown")].copy()
        sub["x"] = sub["cohort"].map(cohort_to_x)
        sub = sub.sort_values("x")
        ax.plot(sub["x"], sub["display_intensity"],
                marker="o", markersize=5, linewidth=1.8,
                color=color, label=cls, zorder=3)

    # Fallback dashed lines
    fb = heat[heat["cohort"] == "unknown"].groupby("building_class")[
        "intensity_kwh_m2_yr"].mean()
    for cls, color in [("SFH", C_SFH), ("MFH_LOW", C_MFH_LOW),
                       ("MFH_HIGH", C_MFH_HIGH)]:
        if cls in fb.index:
            ax.axhline(fb[cls], linestyle="--", linewidth=1.0,
                       color=color, alpha=0.55, zorder=2)
            ax.text(len(cohort_to_x) - 0.55, fb[cls] + 4,
                    f"{cls} fallback",
                    color=color, fontsize=7.5, alpha=0.95,
                    va="bottom", ha="right")

    ax.set_xticks(list(cohort_to_x.values()))
    ax.set_xticklabels(list(cohort_to_x.keys()), rotation=20, ha="right")
    ax.set_xlabel("Construction cohort")
    ax.set_ylabel("Heat intensity (kWh m$^{-2}$ yr$^{-1}$)")
    ax.set_xlim(-0.4, len(cohort_to_x) + 0.6)
    _setup_axes(ax, ygrid=True)
    ax.legend(loc="upper right", title=None)
    _title(ax, "Heat intensity vs construction vintage, by building class")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 4 — Cohort coverage per class
# ─────────────────────────────────────────────────────────────────────────────

def panel4(data: dict):
    cls_df = data["classified"]
    if "construction_year" not in cls_df.columns:
        cls_df = cls_df.copy()
        cls_df["construction_year"] = np.nan

    grouped = cls_df.groupby("building_class").agg(
        total=("construction_year", "size"),
        known=("construction_year", lambda s: s.notna().sum()),
    )
    grouped["unknown"] = grouped["total"] - grouped["known"]
    grouped = grouped.reindex(CLASS_ORDER, fill_value=0)

    fig, ax = plt.subplots(figsize=(7, 4.2))

    x = np.arange(len(grouped))
    ax.bar(x, grouped["unknown"], color=C_SUBTLE_GRID, edgecolor="none",
           label="Unknown cohort", width=0.55, zorder=3)
    ax.bar(x, grouped["known"], bottom=grouped["unknown"],
           color=C_OURS, edgecolor="none",
           label="Has construction year", width=0.55, zorder=4)

    # Pct annotations
    ymax = grouped["total"].max()
    for i, (_, row) in enumerate(grouped.iterrows()):
        if row["total"] > 0:
            pct = row["known"] / row["total"] * 100
            ax.text(i, row["total"] + ymax * 0.025,
                    f"{pct:.2f}%",
                    ha="center", va="bottom",
                    fontsize=9, color=C_TEXT_MUTED)

    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index, rotation=15, ha="right")
    ax.set_ylabel("Building count")
    ax.set_ylim(0, ymax * 1.15)
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(
        lambda v, _: f"{int(v):,}"))
    _setup_axes(ax, ygrid=True)
    ax.legend(loc="upper left")
    _title(ax, "Cohort data availability per building class (EUBUCCO v0.2)")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 5 — Sensitivity tornado
# ─────────────────────────────────────────────────────────────────────────────

def panel5(data: dict):
    rec = data["reconcile"]
    base = rec.loc[rec["source"].str.contains(
        "Bottom-up: residential only", regex=False), "twh_yr"].iloc[0]
    hotmaps = rec.loc[rec["source"].str.contains(
        "Hotmaps", regex=False), "twh_yr"].iloc[0]

    heat = data["heat"]
    res = heat[heat["building_class"] != "NON_RESIDENTIAL"]
    sfh_area = res[res["building_class"] == "SFH"]["heated_floor_area_m2"].sum()
    mfh_area = res[res["building_class"].isin(["MFH_LOW", "MFH_HIGH"])][
        "heated_floor_area_m2"].sum()

    cfg = data["cfg"]
    dhw_sfh = cfg.dhw_sfh
    dhw_mfh = cfg.dhw_mfh
    dhw_contrib = (sfh_area * dhw_sfh + mfh_area * dhw_mfh) / 1e9
    sh_contrib = base - dhw_contrib
    sens = [
        ("Unknown-cohort fallback intensity (±15 %)",
         -0.15 * sh_contrib * 0.96, +0.15 * sh_contrib * 0.96),
        (f"{cfg.country_code}/{cfg.tabula_source_country} heating-degree-day ratio (±10 %)",
         -0.10 * sh_contrib, +0.10 * sh_contrib),
        ("Retrofit blend share (±10 pp)",
         +0.10 * sh_contrib, -0.10 * sh_contrib),
        ("Heated-floor-area conversion (±5 %)",
         -0.05 * base, +0.05 * base),
        ("Domestic hot water intensity (±20 %)",
         -0.20 * dhw_contrib, +0.20 * dhw_contrib),
    ]
    sens.sort(key=lambda r: abs(r[1]) + abs(r[2]), reverse=True)

    fig, ax = plt.subplots(figsize=(7, 4.4))

    for i, (label, lo, hi) in enumerate(sens):
        ax.barh(i, lo, left=base, color=WONG_PALETTE["red"], alpha=0.75,
                edgecolor="none", zorder=3, height=0.5)
        ax.barh(i, hi, left=base, color=WONG_PALETTE["green"], alpha=0.75,
                edgecolor="none", zorder=3, height=0.5)
        ax.text(base + lo - 0.07, i, f"{base+lo:.2f}",
                ha="right", va="center", fontsize=8.5, color="#222222")
        ax.text(base + hi + 0.07, i, f"{base+hi:.2f}",
                ha="left",  va="center", fontsize=8.5, color="#222222")

    ax.axvline(base, color="#111111", linewidth=1.3, zorder=4)
    ax.axvline(hotmaps, color=C_HOTMAPS, linewidth=0.9, linestyle=":",
               alpha=0.7, zorder=2)

    ax.set_yticks(np.arange(len(sens)))
    ax.set_yticklabels([s[0] for s in sens])
    ax.invert_yaxis()
    ax.set_xlabel("Residential heat demand (TWh yr$^{-1}$)")
    xmin = base + min(s[1] for s in sens) - 0.6
    xmax = base + max(s[2] for s in sens) + 0.6
    ax.set_xlim(xmin, xmax)
    _setup_axes(ax, xgrid=True)

    # Inline mini-legend BELOW the x-axis label
    fig.subplots_adjust(bottom=0.20)
    fig.text(0.99, 0.02,
             f"Base case  {base:.2f} TWh   |   Hotmaps  {hotmaps:.2f} TWh",
             fontsize=8.5, color=C_TEXT_MUTED,
             ha="right", va="bottom")

    _title(ax, "Sensitivity of the bottom-up estimate to model assumptions")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 6 — Method comparison
# ─────────────────────────────────────────────────────────────────────────────

def panel6(data: dict):
    rec = data["reconcile"]
    heat = data["heat"]
    res = heat[heat["building_class"] != "NON_RESIDENTIAL"]
    total_area_m2 = res["heated_floor_area_m2"].sum()

    hotmaps = rec.loc[rec["source"].str.contains(
        "Hotmaps", regex=False), "twh_yr"].iloc[0]
    fallback = rec.loc[rec["source"].str.contains(
        "Bottom-up: residential only", regex=False), "twh_yr"].iloc[0]

    known = res[res["construction_year"].notna()]
    if len(known) > 0 and known["heated_floor_area_m2"].sum() > 0:
        per_vintage_mean = (
            (known["intensity_kwh_m2_yr"] * known["heated_floor_area_m2"]).sum()
            / known["heated_floor_area_m2"].sum()
        )
        per_vintage_twh = per_vintage_mean * total_area_m2 / 1e9
    else:
        per_vintage_twh = float("nan")

    n_known = int(len(known))
    methods = [
        ("A. Hotmaps top-down\n(national fuel × heating share)",
         hotmaps, C_HOTMAPS),
        ("B. Bottom-up, this study\n(per-class fallback × area)",
         fallback, C_OURS),
        (f"C. Pure per-vintage TABULA\n(known-cohort subset, {n_known:,} buildings)",
         per_vintage_twh, C_BSO),
    ]

    fig, ax = plt.subplots(figsize=(7, 3.9))

    y = np.arange(len(methods))
    for i, (label, twh, color) in enumerate(methods):
        if not np.isnan(twh):
            ax.barh(i, twh, color=color, height=0.45,
                    edgecolor="none", zorder=3)
            ax.text(twh + 0.12, i, f"{twh:.2f} TWh",
                    va="center", ha="left", fontsize=10,
                    fontweight="bold", color="#222222")

    ax.set_yticks(y)
    ax.set_yticklabels([m[0] for m in methods])
    ax.invert_yaxis()
    ax.set_xlabel("Residential heat demand (TWh yr$^{-1}$)")
    ax.set_xlim(0, hotmaps * 1.30)
    _setup_axes(ax, xgrid=True)
    _title(ax, f"Three computational approaches to {data['cfg'].country_name} residential heat")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 7 — Class-level reconciliation
# ─────────────────────────────────────────────────────────────────────────────

def panel7(data: dict):
    summary = data["summary"]
    ours = summary.groupby("building_class")["total_demand_twh_yr"].sum()
    ours_sfh = ours.get("SFH", 0)
    ours_mfh_high = ours.get("MFH_HIGH", 0)
    ours_mfh_low = ours.get("MFH_LOW", 0)
    ours_resid = ours_sfh + ours_mfh_high + ours_mfh_low

    bsn_path = REPO_ROOT / "code" / "data" / "processed" / "building_stock_nuts3.csv"
    hotmaps_sfh = hotmaps_mfh_high = hotmaps_other = float("nan")
    cfg = data["cfg"]
    if bsn_path.exists():
        bsn = pd.read_csv(bsn_path)
        id_col = next((c for c in ("nuts_id", "nuts3_id", "region_id")
                       if c in bsn.columns), None)
        if id_col is not None:
            country_rows = bsn[bsn[id_col] == cfg.hotmaps_nuts3_id]
            for _, row in country_rows.iterrows():
                bt = row.get("building_type", "")
                mwh = row.get("heat_2015_MWh", 0)
                if bt == "SFH":
                    hotmaps_sfh = mwh / 1e6
                elif bt == "MFH_HIGH":
                    hotmaps_mfh_high = mwh / 1e6
                elif bt == "OTHER":
                    hotmaps_other = mwh / 1e6

    bso_total = cfg.reconciliation_benchmarks.get("eu_bso", {}).get("total_twh", 0)
    if ours_resid > 0:
        bso_sfh      = bso_total * (ours_sfh      / ours_resid)
        bso_mfh_high = bso_total * (ours_mfh_high / ours_resid)
        bso_other    = bso_total * (ours_mfh_low  / ours_resid)
    else:
        bso_sfh = bso_mfh_high = bso_other = float("nan")

    classes = ["SFH", "MFH_HIGH", "MFH_LOW / OTHER"]
    sources = [
        ("Bottom-up (this study)",
         [ours_sfh, ours_mfh_high, ours_mfh_low], C_OURS),
        ("Hotmaps 2015",
         [hotmaps_sfh, hotmaps_mfh_high, hotmaps_other], C_HOTMAPS),
        ("EU BSO 2021 (apportioned)",
         [bso_sfh, bso_mfh_high, bso_other], C_BSO),
    ]

    fig, ax = plt.subplots(figsize=(7, 4.0))

    bar_w = 0.26
    x = np.arange(len(classes))
    seen = set()
    for i, (label, vals, color) in enumerate(sources):
        offset = (i - 1) * bar_w
        for xpos, val in zip(x + offset, vals):
            if np.isnan(val):
                continue
            show = label not in seen
            ax.bar(xpos, val, width=bar_w * 0.92, color=color,
                   edgecolor="none",
                   label=label if show else None, zorder=3)
            seen.add(label)
            if val > 0.15:
                ax.text(xpos, val + 0.06, f"{val:.2f}",
                        ha="center", va="bottom", fontsize=8,
                        color="#222222")

    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.set_ylabel("Heat demand (TWh yr$^{-1}$)")
    ymax = max([v for src in sources for v in src[1] if not np.isnan(v)])
    ax.set_ylim(0, ymax * 1.20)
    _setup_axes(ax, ygrid=True)
    ax.legend(loc="upper left", ncol=1)
    _title(ax, "Class-level reconciliation, three sources")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Panel 8 — Empirical construction-year distribution
# ─────────────────────────────────────────────────────────────────────────────

def panel8(data: dict):
    cls_df = data["classified"]
    if "construction_year" not in cls_df.columns:
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.text(0.5, 0.5, "construction_year column not present",
                ha="center", va="center", color=C_TEXT_MUTED, fontsize=11,
                transform=ax.transAxes)
        ax.axis("off")
        return fig

    known = cls_df[cls_df["construction_year"].notna()].copy()
    known["construction_year"] = known["construction_year"].astype(int)

    fig, ax = plt.subplots(figsize=(7, 3.8))

    if len(known) > 0:
        bins = np.arange(int(known["construction_year"].min()) // 10 * 10,
                         int(known["construction_year"].max()) // 10 * 10 + 11,
                         10)
        bottoms = np.zeros(len(bins) - 1)
        for cls, color in [("SFH", C_SFH), ("MFH_LOW", C_MFH_LOW),
                           ("MFH_HIGH", C_MFH_HIGH),
                           ("NON_RESIDENTIAL", C_NONRES)]:
            sub = known[known["building_class"] == cls]["construction_year"]
            if len(sub) > 0:
                counts, _ = np.histogram(sub, bins=bins)
                ax.bar(bins[:-1], counts, width=8, align="edge",
                       bottom=bottoms,
                       color=color, edgecolor="none",
                       label=f"{cls} (n={len(sub)})", zorder=3)
                bottoms += counts

    ax.set_xlabel("Construction year (10-year bins)")
    ax.set_ylabel("Building count")
    _setup_axes(ax, ygrid=True)
    ax.legend(loc="upper left")
    _title(ax,
           f"Construction-year distribution of the {len(known)} buildings "
           f"with year metadata")

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Build pipeline
# ─────────────────────────────────────────────────────────────────────────────

PANELS = [
    ("Reconciliation",         panel1),
    ("Class * cohort",         panel2),
    ("Intensity vs vintage",   panel3),
    ("Cohort coverage",        panel4),
    ("Sensitivity tornado",    panel5),
    ("Method comparison",      panel6),
    ("Class-level reconcile",  panel7),
    ("Vintage histogram",      panel8),
]


def build_pdf(out_path: Path, data: dict) -> None:
    with PdfPages(out_path) as pdf:
        for i, (name, panel_func) in enumerate(PANELS, start=1):
            fig = panel_func(data=data)
            pdf.savefig(fig)
            plt.close(fig)
            print(f"    page {i} — {name}")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", required=True,
                        help="2-letter ISO country code (e.g. LU, FR, DE)")
    args = parser.parse_args()

    cfg = load_country_config(args.country)
    paths = build_paths(cfg)

    print("=" * 64)
    print(f"04_diagnostics.py — {cfg.country_name} ({cfg.country_code}) "
          f"diagnostic figures")
    print("=" * 64)

    data = load_all_data(paths)
    data["cfg"] = cfg  # let panels access country metadata for titles etc.
    print(f"  Loaded {len(data['classified']):,} classified buildings")
    print(f"  Loaded {len(data['heat']):,} buildings with heat demand")

    out_clean = paths["out_clean"]
    country_clean = paths["country_clean"]
    out_clean.parent.mkdir(parents=True, exist_ok=True)
    country_clean.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n  Building CLEAN PDF (paper-ready) → {out_clean.name}")
    build_pdf(out_clean, data=data)

    shutil.copy(out_clean, country_clean)

    print("\n  Output files:")
    for p in (out_clean, country_clean):
        print(f"    {p.relative_to(REPO_ROOT)}  ({p.stat().st_size/1024:.1f} KB)")

    print("\n" + "=" * 64)
    print("Done.")
    print("=" * 64)


if __name__ == "__main__":
    main()
