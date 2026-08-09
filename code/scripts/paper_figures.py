"""Purpose-built paper figure set for Paper v5 (second redesign, 2026-06-13).

Design brief (Ali): all figures newly conceived -- academic, modern, insightful; no
recycled presentation graphics, no arbitrary country picks, no overlapping text; the
paper's own simulation outputs everywhere (incl. a NUTS3 map of the bottom-up build);
~20 figures total covering ALL workstreams (demand build, merit order, endogenous peak
price, missing money, DH, infrastructure bill, H2 supply routes, reinforcement).

Conventions: vector PDF primary (PNG twin), serif/STIX, no in-figure titles (captions
argue), (a)/(b) panel tags, one scenario palette, representative countries only where
justified by a stated criterion (largest market / coldest / mildest), never at random.

  P01 NUTS3 map of the bottom-up demand build       (methodology)
  P02 building stock: class mix by country + TABULA vintage gradient
  P03 validation vs Hotmaps (cones + ladder)
  P04 demand fan + three-layer index                (results)
  P05 2050 technology mix across scenarios
  P06 input prices + 29-country LCOH ordering
  P07 LCOH anatomy: component stacks 2030/2050 (EU-27+UK+CH median, no country picks)
  P08 emissions fan + switching/grid waterfall
  P09 H2 gap ladder + who-pays-for-delivery
  P10 winter peak: load-duration -> endogenous price -> win matrix (3 panels)
  P11 missing money (rent as a share of annualised capital)
  P12 DH stack + DH expansion slopes (labels de-collided)
  P13 infrastructure bill
  P14 Switzerland (fresh from the engine)
  P15 Sobol + rho amplification                     (sensitivity)
  P16 H2 delivered cost by route + reinforcement robustness
  P17 cost-optimal pathway                          (cost-optimal)
  P19 grid carbon-intensity trajectories            (discussion)
  P30 graphical abstract: the three-test verdict across the bridge (introduction)

Run: cd code && PYTHONPATH=. python -m scripts.paper_figures
Out: paper/figs/paper/P##_*.pdf (+ .png twins)
"""
from __future__ import annotations
import re
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.transforms import ScaledTranslation
from pathlib import Path
from src.Config import RESULTS_DIR, PROCESSED_DIR
from src.Economics import (compute_lcoh, get_fuel_price, get_cop, get_capex, get_fom,
                           h2_distribution_adder_eur_mwh, electricity_distribution_adder_eur_mwh,
                           h2_seasonal_storage_adder_eur_mwh,
                           get_annual_hours, capital_recovery_factor, TECH_PARAMS,
                           DISCOUNT_RATE_BY_COUNTRY, DISCOUNT_RATE_REAL,
                           LABOUR_COST_MULTIPLIER)
from src.Policy import get_grid_carbon_intensity, get_carbon_cost_adder_eur_per_mwh_useful
from scripts._figstyle import (set_style, assert_printable, SCEN_COLOR, H2_HATCH,
                               ink_h2_hatch,
                               TECH_COLOR, legend_below)

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "paper"; OUT.mkdir(parents=True, exist_ok=True)
R = RESULTS_DIR
DATA = REPO / "code" / "data"

SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
SHORT = {"CURRENT_POLICIES": "Current Policies", "STATED_POLICIES": "Stated Policies",
         "NET_ZERO": "Net Zero", "H2_PUSH": "H2 Push"}
SC = dict(SCEN_COLOR)
# TECH_COLOR now lives in scripts/_figstyle.py; see the note there.
TECH_LABEL = {"hp_air": "Heat pump (air)", "hp_ground": "Heat pump (ground)",
              "district_heat": "District heat", "biomass_boiler": "Biomass",
              "h2_boiler": "Hydrogen", "gas_boiler": "Gas", "oil_boiler": "Oil",
              "resistance_heater": "Resistance"}
YEARS = [2025, 2030, 2040, 2050]
EU = list(LABOUR_COST_MULTIPLIER)

set_style()

# Every figure in this module is included at close to the full 455 pt long-paper
# column, so a native point size is very nearly the printed size. This module was the
# one major generator never retrofitted with the legibility guard, and it had drifted
# back to 5.6 pt country labels. FS_TICK_SMALL is the floor for the dense per-country
# ranking panels; assert_printable fails the build if it is ever set below it.
FS_TICK_SMALL = 6.6

# NOTE ON P01. Its colourbar label used a mathtext superscript, which matplotlib renders
# at 0.694x and which printed at 5.8 pt in the long paper. The label is Unicode here now,
# but P01 needs code/data/raw/gisco/NUTS_RG_01M_2021_4326_LEVL_3.geojson, a gitignored
# download, so it does not rebuild without running scripts.download_data first. The
# committed P01 PDF therefore still carries the old label; its inclusion was widened from
# 0.9 to the full column in methodology.tex, which lifts the printed superscript to
# 6.5 pt, so the figure is legible either way. Rerun this module after the download to
# pick up the Unicode label.
assert_printable(6.3, {"dense per-country tick label": FS_TICK_SMALL},
                 column="long", label="paper_figures (dense panels)")                                            # shared house style (sans, palette, soft spines, 200 DPI, white bg)
plt.rcParams.update({                                  # paper-embed tweaks: smaller fonts, constrained layout
    "figure.autolayout": False, "figure.constrained_layout.use": True,
    "font.size": 8.5, "axes.labelsize": 8.5, "axes.titlesize": 9.0,
    "axes.titlelocation": "center",                    # paper figures keep centred titles / panel tags
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "lines.linewidth": 1.6, "savefig.pad_inches": 0.04,
})


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf"); fig.savefig(OUT / f"{name}.png")
    plt.close(fig); print(f"  {name}")


def tag(ax, letter, dx=0.0, dy=1.03):
    """Put the panel letter above the axes, aligned with its left spine.

    Every call used to pass a hand-tuned negative dx meant to clear the y-axis labels. How far
    left that has to be depends on how wide the tick labels are, which changes with the data,
    so four panels ended up with the letter printed on top of a tick label: "(b)" on "250",
    "(a)" on "4000", "(b)" on "700". Measuring the y-axis extent and stepping left of it
    replaced one collision with another, since the rotated y-axis label reaches nearly to the
    top of the axes and the letter landed on that instead.

    The left spine is the one anchor that cannot collide with y-axis material, because
    everything the y axis draws lies to the left of x=0 and below y=1. It is also the ordinary
    journal convention. Nothing measured, nothing to drift.
    """
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes,
            fontweight="bold", fontsize=9.5, va="bottom", ha="left")


def stagger(targets, min_gap):
    """Push label y-positions apart (ascending input) so adjacent gaps >= min_gap."""
    out = list(targets)
    for i in range(1, len(out)):
        if out[i] - out[i - 1] < min_gap:
            out[i] = out[i - 1] + min_gap
    return out


def summ(sc):  return pd.read_csv(R / f"mc_summary_{sc}.csv")
def emis(sc):  return pd.read_csv(R / f"mc_emissions_{sc}.csv")


def _relative_luminance(hex_colour: str) -> float:
    """WCAG relative luminance of a #rrggbb fill."""
    def channel(v: float) -> float:
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _label_ink(fill: str) -> str:
    """Black or white, whichever carries more contrast against this fill.

    In-bar labels were uniformly white, which is right on the two dark blues and wrong on
    every light fill: white on the gas grey is 2.68:1 where small text needs 4.5:1.
    """
    # The luminance threshold was 0.36 and every fill it was written for sits below it,
    # so the fix never fired: gas 0.342, biomass 0.333, ground-source 0.305 and district
    # heat 0.303 all still printed white, at 2.68 to 2.97:1 against the 4.5:1 small-text
    # minimum. Decide on the contrast ratio itself rather than on a proxy threshold, and
    # take whichever ink actually wins.
    lum = _relative_luminance(fill)
    black = (lum + 0.05) / 0.05
    white = 1.05 / (lum + 0.05)
    return "#111111" if black >= white else "#ffffff"


# ── P01: NUTS3 map of the bottom-up build ─────────────────────────────────────
# SUPERSEDED by scripts/fig_nuts3_map.py. This version joins the demand build to the
# NUTS 2021 layer on the raw region code, but the build carries NUTS 2016 codes, so the
# join fails silently for 40 fully modelled regions (Croatia, Belgium, Sardinia,
# Estonia, Germany, the United Kingdom) and draws them in the "no data" grey. The
# replacement remaps through scripts/nuts_crosswalk.py first. Kept for reference only.
def p01():
    import geopandas as gpd
    geo = gpd.read_file(DATA / "raw" / "gisco" / "NUTS_RG_01M_2021_4326_LEVL_3.geojson",
                        engine="pyogrio")
    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    dem = stock.groupby("nuts_id").heat_2015_MWh.sum() / 1e6   # TWh
    geo = geo.merge(dem.rename("twh"), left_on="NUTS_ID", right_index=True, how="left")
    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    geo.plot(ax=ax, column="twh", cmap="YlOrRd",
             norm=matplotlib.colors.LogNorm(vmin=0.05, vmax=30),
             edgecolor="white", linewidth=0.08,
             missing_kwds={"color": "#e8e8e8", "edgecolor": "white", "linewidth": 0.08})
    ax.set_xlim(-12, 34); ax.set_ylim(34, 71); ax.axis("off")
    sm = plt.cm.ScalarMappable(cmap="YlOrRd",
                               norm=matplotlib.colors.LogNorm(vmin=0.05, vmax=30))
    cb = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.01)
    cb.set_label("Useful residential heat (TWh/yr, log scale)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    save(fig, "P01_nuts3_map")


# ── P02: building stock composition + vintage gradient ───────────────────────
def p02():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 4.3), layout="constrained",
                               gridspec_kw={"width_ratios": [1.15, 1]})
    rows = []
    for cc in EU:
        f = PROCESSED_DIR / cc.lower() / f"{cc}_heat_demand_nuts3.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f)
        g = d.groupby("building_class").heat_demand_MWh.sum()
        tot = g.get("SFH", 0) + g.get("MFH_LOW", 0) + g.get("MFH_HIGH", 0)
        if tot <= 0:
            continue
        rows.append({"country": cc, "SFH": g.get("SFH", 0) / tot,
                     "MFH_LOW": g.get("MFH_LOW", 0) / tot,
                     "MFH_HIGH": g.get("MFH_HIGH", 0) / tot,
                     "tot": tot / 1e6})
    df = pd.DataFrame(rows).sort_values("SFH")
    y = np.arange(len(df))
    cls = [("SFH", "#1f5fa8", "Single-family"), ("MFH_LOW", "#e07b39", "Small multi-family"),
           ("MFH_HIGH", "#7d5ba6", "Apartment blocks")]
    left = np.zeros(len(df))
    for k, c, lab in cls:
        a.barh(y, df[k] * 100, left=left, color=c, height=0.74, label=lab)
        left += df[k].values * 100
    # EU aggregate row with explicit percentages
    w = df.tot.values
    eu_sh = {k: float((df[k] * df.tot).sum() / df.tot.sum()) for k, _, _ in cls}
    ye = len(df) + 1.0
    le = 0
    for k, c, _ in cls:
        a.barh(ye, eu_sh[k] * 100, left=le, color=c, height=0.9)
        if eu_sh[k] > 0.07:
            a.text(le + eu_sh[k] * 50, ye, f"{eu_sh[k]*100:.0f}%", ha="center",
                   va="center", color="white", fontsize=7.5, fontweight="bold")
        le += eu_sh[k] * 100
    a.set_yticks(list(y) + [ye])
    a.set_yticklabels(list(df.country) + ["EU+UK+CH"], fontsize=6.6)
    a.set_ylim(-0.8, ye + 0.9)
    a.set_xlabel("Share of residential useful heat (%)")
    a.legend(loc="lower left", bbox_to_anchor=(0, 1.01), ncol=2,
             columnspacing=0.8, handletextpad=0.3)
    tag(a, "a")

    cohorts = ["pre-1945", "1946-1970", "1971-1990", "1991-2010", "2011-2020", "post-2020"]
    # The cohort keys stay as the data carries them; only the tick text is shortened, because
    # six full-length labels do not fit across a half-width panel at any rotation.
    COHORT_SHORT = ["pre-1945", "1946–70", "1971–90", "1991–2010", "2011–20", "post-2020"]
    M = {c: [] for c in cohorts}
    for f in (DATA / "raw" / "tabula").glob("*_intensities.csv"):
        try:
            d = pd.read_csv(f, comment="#")
        except Exception:
            continue
        if not {"cohort", "sh_intensity_kwh_m2_yr"} <= set(d.columns):
            continue
        g = d.groupby("cohort").sh_intensity_kwh_m2_yr.mean()
        for c in cohorts:
            if c in g.index:
                M[c].append(g[c])
    med = [np.median(M[c]) for c in cohorts]
    lo = [np.percentile(M[c], 25) for c in cohorts]
    hi = [np.percentile(M[c], 75) for c in cohorts]
    x = np.arange(len(cohorts))
    b.fill_between(x, lo, hi, color="#b03a3a", alpha=0.18, lw=0,
                   label="Interquartile range (countries)")
    b.plot(x, med, "-o", ms=4, color="#b03a3a", label="Median country")
    # 32 degrees, not 18: at 18 these six labels are long enough that each one runs about
    # 30 pt into its neighbour, so the whole row reads as one smear.
    b.set_xticks(x); b.set_xticklabels(COHORT_SHORT, rotation=90, ha="center", fontsize=7)
    b.set_ylabel("Space-heating intensity (kWh m⁻² yr⁻¹)")
    b.set_ylim(0, None)
    b.legend(loc="upper right", handlelength=1.4)
    tag(b, "b")
    save(fig, "P02_building_stock")


# ── P03: validation ───────────────────────────────────────────────────────────
def p03():
    bm = pd.read_csv(R / "benchmark_multi.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 3.1),
                               gridspec_kw={"width_ratios": [1, 1.2]})
    lo, hi = 0.8, 900
    xs = np.geomspace(lo, hi, 50)
    a.fill_between(xs, xs * 0.85, xs * 1.15, color="#2ca02c", alpha=0.12, lw=0, label="$\\pm$15%")
    a.fill_between(xs, xs * 0.75, xs * 0.85, color="#e8b54d", alpha=0.15, lw=0, label="$\\pm$25%")
    a.fill_between(xs, xs * 1.15, xs * 1.25, color="#e8b54d", alpha=0.15, lw=0)
    a.plot(xs, xs, color="#444", lw=0.8, ls="--")
    a.scatter(bm.hotmaps_TWh, bm.bottomup_TWh, s=16, color="#1f5fa8", zorder=3)
    a.set_xscale("log"); a.set_yscale("log")
    # Plain "1 / 10 / 100", not matplotlib's default 10^n. The default formatter writes the
    # exponent as a mathtext superscript at 0.70x the tick size, which printed at 5.25 pt on
    # both axes of both documents. Over three decades the plain form also reads faster.
    for axis in (a.xaxis, a.yaxis):
        axis.set_major_locator(mticker.FixedLocator([1, 10, 100]))
        axis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
        axis.set_minor_formatter(mticker.NullFormatter())
    a.set_xlim(lo, hi); a.set_ylim(lo, hi)
    a.set_xlabel("Hotmaps benchmark (TWh)"); a.set_ylabel("Bottom-up build (TWh)")
    a.legend(loc="upper left", handletextpad=0.4)
    tag(a, "a")
    d = bm.sort_values("gap_vs_hotmaps_pct")
    y = np.arange(len(d))
    cols = ["#2ca02c" if abs(v) <= 15 else ("#e8b54d" if abs(v) <= 25 else "#b03a3a")
            for v in d.gap_vs_hotmaps_pct]
    b.barh(y, d.gap_vs_hotmaps_pct, color=cols, height=0.72)
    from matplotlib.patches import Patch as _P
    b.legend(handles=[_P(facecolor="#2ca02c", label=r"$\pm$15% or better"),
                      _P(facecolor="#e8b54d", label=r"$\pm$15 to 25%"),
                      _P(facecolor="#b03a3a", label=r"beyond $\pm$25%")],
             loc="lower right", fontsize=6.5, frameon=False, handlelength=1.0,
             handleheight=0.8, borderaxespad=0.2)
    b.axvline(0, color="#333", lw=0.8)
    for v in (-15, 15):
        b.axvline(v, color="#2ca02c", lw=0.6, ls=":")
    b.set_yticks(y); b.set_yticklabels(d.country, fontsize=6.6)
    b.set_ylim(-0.8, len(d) - 0.2)
    b.set_xlabel("Deviation from Hotmaps (%)")
    tag(b, "b")
    save(fig, "P03_validation")


# ── P04: demand fan + three-layer index ───────────────────────────────────────
def p04():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7), layout="constrained",
                               gridspec_kw={"width_ratios": [1.45, 1]})
    for sc in SCEN:
        s = summ(sc); d = s[(s.variable == "useful_heat_MWh") & (s.tech == "all")]
        d = d.set_index("year")[["q10", "q50", "q90"]].reindex(YEARS) / 1e6
        a.plot(YEARS, d.q50, "-o", ms=3, color=SC[sc], label=SHORT[sc])
        a.fill_between(YEARS, d.q10, d.q90, color=SC[sc], alpha=0.12, lw=0)
    a.set_ylabel("Useful heat demand (TWh/yr)")
    a.set_xticks(YEARS); a.legend(loc="lower left", handlelength=1.4)
    tag(a, "a")
    s = summ("STATED_POLICIES")
    u = s[(s.variable == "useful_heat_MWh") & (s.tech == "all")].set_index("year").q50
    f = s[s.variable == "final_energy_MWh"].groupby("year").q50.sum()
    e = emis("STATED_POLICIES")
    c = e[(e.variable == "co2_MtCO2") & (e.tech == "all")].set_index("year").q50
    vals = [u[2050] / u[2025] * 100, f[2050] / f[2025] * 100, c[2050] / c[2025] * 100]
    labs = ["Useful\nheat", "Delivered\nenergy", "CO₂\nemissions"]
    cols = ["#1f5fa8", "#e07b39", "#b03a3a"]
    bars = b.bar(labs, vals, width=0.62, color=cols)
    b.axhline(100, color="#444", lw=0.8, ls="--")
    b.text(2.42, 101.5, "2025 = 100", fontsize=7, color="#444", ha="right")
    for r_, v in zip(bars, vals):
        b.text(r_.get_x() + r_.get_width() / 2, v + 2, f"{v:.0f}", ha="center", fontsize=8)
    b.set_ylabel("2050 level (2025 = 100)"); b.set_ylim(0, 115)
    # Panel (b) is Stated Policies alone, and read beside a four-scenario fan it was being
    # taken for a study-wide result. Say which scenario it is on the panel itself.
    # pad=3 put the title's baseline under the tag() letter at axes-fraction 1.03, and
    # the two overprinted into an unreadable blot. The overlap gate cannot see it: the tag
    # is an ax.text and the title is a set_title.
    b.set_title("Stated Policies", fontsize=8.5, pad=14)
    tag(b, "b")
    save(fig, "P04_demand_three_layer")


# ── P05: 2050 mix across scenarios ────────────────────────────────────────────
# How far a segment label has to drop for its ink, rather than its layout box, to sit on
# the middle of the band. See the note at the call site. Measured off the rendered
# figure; no gate asserts it, so re-measure if the font or the label size changes.
LABEL_NUDGE_PT = 0.80


def p05():
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    bottom = np.zeros(4)
    order = ["hp_air", "hp_ground", "district_heat", "biomass_boiler",
             "h2_boiler", "gas_boiler", "oil_boiler", "resistance_heater"]
    for t in order:
        vals = []
        for sc in SCEN:
            s = summ(sc); d = s[(s.year == 2050) & (s.variable == "tech_share")]
            sh = dict(zip(d.tech, d.q50)); tot = sum(sh.values()) or 1.0
            vals.append(sh.get(t, 0.0) / tot * 100)
        vals = np.array(vals)
        # Hydrogen carries a hatch as well as a colour. Under deuteranopia its purple
        # is the closest pair in this palette to the heat-pump blue (simulated
        # separation 27.1 of 441), and hydrogen is what this figure is read for.
        seg = ax.bar([SHORT[s].replace(" ", "\n") for s in SCEN], vals, bottom=bottom,
                     width=0.62, color=TECH_COLOR[t], label=TECH_LABEL[t],
                     hatch=(H2_HATCH if t == "h2_boiler" else None),
                     edgecolor="none", linewidth=0.0)
        if t == "h2_boiler":
            ink_h2_hatch(seg)
        for i, v in enumerate(vals):
            # Two defects here. Every label was white, and white on the four light fills
            # runs 2.68 to 2.97:1 against the 4.5:1 small-text minimum, so the gas, biomass,
            # ground-source and district-heat numbers were barely readable. And the >= 7
            # threshold left hydrogen unlabelled in three of the four bars (0.5, 5.5 and
            # 3.6 per cent), which is the one category this paper is read for. Label colour
            # now follows the fill's luminance, and the threshold is low enough to carry
            # hydrogen everywhere it is non-trivial.
            if v >= 2:
                # Every segment label is white, outline included, on the author's call.
                # One ink for the whole series rather than one chosen per fill: mixed
                # black and white digits read as two kinds of number. Black was tried and
                # rejected on the look of it, and so was a dark outline behind the white.
                #
                # Nothing sits behind the digit any more. Hydrogen's hatch used to be
                # white, so a white label on it was white glyphs over white stripes, and
                # the fix was a solid patch of the segment's own fill behind each number.
                # That patch cut the stripes into stubs around every hydrogen label and
                # read as a rendering fault. The hatch is now drawn in H2_HATCH_INK, a
                # dark shade of hydrogen's own purple, so a white digit cannot collide
                # with it and the patch, its tight padding and its clip path all go.
                #
                # What white costs, recorded rather than argued. Seven fills carry a
                # label. The worst is the gas grey at 2.68:1 and four of the seven fall
                # under the 3:1 large-text floor, let alone the 4.5:1 small-text minimum;
                # black would have been 3.26:1 and three of seven, so neither ink clears
                # 4.5:1 across a palette this wide. Darkening the fills themselves was
                # tried in an earlier round and rejected for a different reason: it
                # collapsed biomass against oil under simulated deuteranopia, 55.9 to 17.7
                # of 441, trading a contrast problem for a worse colour-vision one.
                # Hydrogen, the one category this figure is read for, is the best of them
                # at 5.36:1.
                #
                # So the labels are a convenience and nothing rests on reading them. Every
                # share that matters is stated in the Results prose, and the whole series
                # ships in the summary artefact behind this figure.
                # One weight as well as one colour. Hydrogen's digits were bold and the
                # other seven were not, which made them read as a different kind of
                # number rather than as the same series emphasised.
                #
                # va="center" does not put a digit in the middle of its band. It centres
                # the text layout box, which runs from the font's descent to its ascent,
                # and a digit has no descender and stops short of the ascent, so the ink
                # sits above the middle of that box. On the thick bands nobody sees it. On
                # hydrogen's Net Zero band, 3.6 per cent of the axis and 6.5 pt on the
                # printed page against a 4.8 pt digit, the 4 rode against the boundary
                # with the resistance band above it.
                #
                # LABEL_NUDGE_PT corrects it for every label, since the bias is the font's
                # and applies to all eight series. Measured off the rendered figure at 600
                # dpi rather than derived from font internals: at a 2 pt offset the ink
                # centre sat 1.20 pt below the band centre, so 0.80 pt is what puts it on
                # the band centre. Checked afterwards across every labelled band in the
                # four bars: worst deviation 0.06 pt, one pixel at 600 dpi, and the Net
                # Zero hydrogen band exactly on centre. Applied in points through the
                # transform, so it holds whatever the axis limits or the figure size
                # become.
                ink = "#ffffff"
                tr = ax.transData + ScaledTranslation(0, -LABEL_NUDGE_PT / 72,
                                                      fig.dpi_scale_trans)
                ax.text(i, bottom[i] + v / 2, f"{v:.0f}", ha="center", va="center",
                        fontsize=6.8, color=ink, zorder=5, transform=tr)
        bottom += vals
    ax.set_ylabel("Share of useful heat, 2050 (%)"); ax.set_ylim(0, 100)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), handlelength=1.2)
    save(fig, "P05_mix_2050")


# ── P06: input prices + LCOH ordering ─────────────────────────────────────────
def p06():
    yrs = [2025, 2030, 2035, 2040, 2045, 2050]
    fig = plt.figure(figsize=(6.3, 4.6), layout="constrained")
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.85])
    axs = [fig.add_subplot(gs[0, i]) for i in range(3)]
    for ax, fuel, lab in zip(axs, ["gas", "electricity", "hydrogen"],
                             ["Gas", "Electricity", "Hydrogen (CENTRAL)"]):
        M = np.array([[get_fuel_price(fuel, c, y) for c in EU] for y in yrs])
        med = np.median(M, axis=1); lo = np.percentile(M, 25, axis=1); hi = np.percentile(M, 75, axis=1)
        ax.plot(yrs, med, color="#1f5fa8")
        ax.fill_between(yrs, lo, hi, color="#1f5fa8", alpha=0.18, lw=0)
        ax.set_title(("(a) " if fuel == "gas" else "") + lab, fontsize=8, pad=3)
        ax.set_xticks([2025, 2050]); ax.set_ylim(0, None)
    axs[0].set_ylabel("Residential price (€/MWh)")   # letter is in the title above
    e = pd.read_csv(R / "country_econ_table.csv").dropna(subset=["lcoh_bestHP_2050"])
    e = e.sort_values("lcoh_bestHP_2050")
    ax = fig.add_subplot(gs[1, :])
    y = np.arange(len(e))
    for yi, (_, r_) in zip(y, e.iterrows()):
        ax.plot([min(r_.lcoh_bestHP_2050, r_.lcoh_gas_2050, r_.lcoh_H2_2050),
                 max(r_.lcoh_bestHP_2050, r_.lcoh_gas_2050, r_.lcoh_H2_2050)],
                [yi, yi], color="#d9d9d9", lw=1.1, zorder=1)
    ax.scatter(e.lcoh_bestHP_2050, y, s=15, color="#1f5fa8", zorder=3, label="Best heat pump")
    ax.scatter(e.lcoh_H2_2050, y, s=15, marker="D", color="#7d5ba6", zorder=3, label="Hydrogen boiler")
    ax.scatter(e.lcoh_gas_2050, y, s=15, marker="s", color="#9e9e9e", zorder=3, label="Gas boiler")
    ax.set_yticks(y); ax.set_yticklabels(e.country, fontsize=6.6)
    ax.set_ylim(-0.8, len(e) - 0.2)
    ax.set_xlabel("Levelised cost of heat, 2050 (€/MWh useful)")
    ax.legend(loc="lower right", handletextpad=0.2, borderaxespad=0.2)
    tag(ax, "b")
    save(fig, "P06_prices_lcoh")


# ── P07: LCOH anatomy (the median market's component stack) ───────────────────
def _lcoh_components(tech, year):
    """The component stack of the market sitting at the study median for this cell.

    This used to take the median of each component independently and stack those. A sum
    of independent medians is not the median of the sums, and the totals came out at
    112/125/129 against the paper's own 132.7/118.5/122.8, which inverted both gaps: the
    drawn heat-pump-to-hydrogen distance read 13.3 where the text says 4.3, and the
    hydrogen-to-gas distance read 4.5 where the text says 9.9. The figure said the
    opposite of the abstract on the one channel a reader trusts without checking, which
    is bar height.

    Round 24 answered that by deleting the printed totals and disclaiming additivity in
    the axis label and the note. That was the wrong answer. A stacked bar whose total is
    declared meaningless has already failed as a stacked bar, and a caption that tells a
    reader not to believe the artwork is a confession rather than a fix.

    With 29 markets the median is an actual market, not an interpolation, so this returns
    that market's own six components. They sum to the study median exactly, the gaps read
    the right way round, and every band is one real place's real cost. The price is that
    the six bars are not all the same market, so a composition difference between two bars
    carries a country difference inside it. That is disclosed by printing the market on
    the bar, and it is a smaller price than a figure that contradicts its own paper.
    """
    caps, foms, voms, fuels, carbons, infras = [], [], [], [], [], []
    p = TECH_PARAMS[tech]
    for c in EU:
        r = DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL)
        crf = capital_recovery_factor(r, p["lifetime_yrs"])
        if tech in ("hp_air", "hp_ground"):
            eta = get_cop(tech, c, year)
        else:
            t = max(0, min(1, (year - 2025) / 25))
            eta = (p.get("efficiency_2025", 1.0)
                   + t * (p.get("efficiency_2050", 1.0) - p.get("efficiency_2025", 1.0)))
        # Capital is charged on HEAT OUTPUT: annual_hours is full-load hours of heat and
        # capex is EUR per kW of heat, so there is no efficiency term here. This function
        # is a component-wise reimplementation of compute_lcoh (the stack has to be broken
        # out for the figure) and it previously carried its own copy of the eta factor that
        # was removed from Economics.compute_lcoh, which would have silently reproduced the
        # old figure from corrected code. It also has to apply the same delivery adders the
        # engine now applies by default, or the stack will not sum to the quoted LCOH.
        ahe = get_annual_hours(c) / 1000
        caps.append(crf * get_capex(tech, year, c) / ahe)
        foms.append(get_fom(tech, c) / ahe)
        voms.append(p["vom_eur_mwh"])
        fuels.append(get_fuel_price(p["fuel"], c, year) / eta)
        carbons.append(get_carbon_cost_adder_eur_per_mwh_useful(p["fuel"], c, year, eta, "CENTRAL"))
        if tech == "h2_boiler":
            # Distribution network plus the seasonal store the heating load requires.
            # The engine charges both by default, so the stack must carry both or it
            # will not sum to the levelised cost quoted in the text.
            infras.append(h2_distribution_adder_eur_mwh(c, mode="blend", bound="central")
                          + h2_seasonal_storage_adder_eur_mwh(c, eta))
        elif tech in ("hp_air", "hp_ground", "resistance_heater"):
            infras.append(electricity_distribution_adder_eur_mwh(c, bound="central"))
        else:
            infras.append(0.0)
    # Fixed and variable O&M ride together. Variable O&M is a flat EUR2/MWh for all three
    # technologies in both years, so its own band printed an identical 1.6 pt hairline in
    # every bar while holding a legend entry that invited the reader to look for it. A
    # band that is the same everywhere separates nothing.
    oms = [f + v for f, v in zip(foms, voms)]
    stacks = list(zip(caps, oms, fuels, carbons, infras))
    order = sorted(range(len(EU)), key=lambda i: sum(stacks[i]))
    m = order[len(order) // 2]
    return [float(x) for x in stacks[m]], EU[m], float(sum(stacks[m]))


def p07():
    techs = [("gas_boiler", "Gas boiler"), ("hp_air", "Heat pump (air)"),
             ("h2_boiler", "Hydrogen boiler")]
    comp_lab = ["Capital", "O\\&M", "Fuel", "Carbon (ETS2)",
                "Last-mile network + seasonal store"]
    # The last band was #7d6fb0, which sits 30 of 441 from the hydrogen purple this paper
    # uses everywhere else, so a reader who learned "purple is hydrogen" in Fig. 3 read
    # this band as hydrogen when it means network plus storage. The teal breaks the hue
    # association and separates from all five other bands by at least 85 of 441 under
    # simulated deuteranopia and 93 under protanopia.
    comp_col = ["#1f5fa8", "#5b9bd5", "#e07b39", "#b03a3a", "#17706b"]
    fig, ax = plt.subplots(figsize=(5.8, 3.5))
    X, ticks, tick_lab = 0, [], []
    for tech, lab in techs:
        for year in (2030, 2050):
            comps, market, total = _lcoh_components(tech, year)
            bottom = 0
            for v, c in zip(comps, comp_col):
                ax.bar(X, v, bottom=bottom, width=0.7, color=c)
                # Label any segment tall enough to hold the text. Below about 11 the
                # digits would overprint the band boundaries either side.
                if v >= 11:
                    # 7.6 pt, not 6.6: at this figure's print scale a 6.6 pt
                    # label prints at 5.6 pt, under the project's 6 pt floor.
                    ax.text(X, bottom + v / 2, f"{v:.0f}", ha="center", va="center",
                            fontsize=7.6, color="white", fontweight="bold")
                bottom += v
            # The total is now printable because it means something: it is the study
            # median for this cell, and the bar is one market's stack that sums to it.
            ax.text(X, total + 3.5, f"{total:.0f}", ha="center", va="bottom",
                    fontsize=7.6, fontweight="bold")
            # Which market that is. A composition difference between two bars carries a
            # country difference inside it, so the country has to be on the page.
            # 7.5, not 6.6, and the same size as the tick labels: at this figure's 0.83
            # print scale a 6.6 pt label sets 5.46 pt on the page, under the 6 pt floor.
            ax.text(X, total + 12.5, market, ha="center", va="bottom", fontsize=7.5,
                    color="#555555")
            ticks.append(X); tick_lab.append(f"{year}")
            X += 1
        ax.text(X - 1.5, -30, lab, ha="center", fontsize=8)
        X += 0.6
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in comp_col]
    # Outside the axes: every in-axes corner collides with a bar. The gas stacks reach
    # 152 and the hydrogen 2030 stack 172 against a 190 ceiling, so an upper-left or
    # upper-right legend prints over the stacks and over their value labels.
    ax.legend(handles, [l.replace("\\&", "&") for l in comp_lab],
              loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=3,
              handlelength=1.1, handletextpad=0.4, columnspacing=1.2,
              frameon=False, fontsize=7.5)
    ax.set_xticks(ticks); ax.set_xticklabels(tick_lab, fontsize=7.5)
    ax.set_ylabel("Levelised cost of heat\n(€/MWh useful)")
    # Headroom for the printed total and the market code above the tallest stack, which
    # is hydrogen at 2030 (175.1).
    ax.set_ylim(0, 205)
    ax.tick_params(axis="x", length=0)
    save(fig, "P07_lcoh_anatomy")


# ── P08: emissions fan + waterfall ────────────────────────────────────────────
def p08():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7), layout="constrained",
                               gridspec_kw={"width_ratios": [1.45, 1]})
    for sc in SCEN:
        e = emis(sc); d = e[(e.variable == "co2_MtCO2") & (e.tech == "all")]
        d = d.set_index("year").reindex(YEARS)
        a.plot(YEARS, d.q50, "-o", ms=3, color=SC[sc], label=SHORT[sc])
        a.fill_between(YEARS, d.q10, d.q90, color=SC[sc], alpha=0.12, lw=0)
        a.annotate(f"{d.q50[2050]:.0f}", (2050, d.q50[2050]), xytext=(5, 0),
                   textcoords="offset points", color=SC[sc], fontsize=7.5,
                   fontweight="bold", va="center")
    a.set_ylabel("Buildings CO₂ (Mt/yr)")
    a.set_xticks(YEARS); a.set_xlim(2024, 2056); a.legend(loc="lower left", handlelength=1.4)
    tag(a, "a")
    # All three levels come from the SAME file. Taking the 2050 endpoint from the Monte
    # Carlo median instead (230.9 against this file's 264.2) closed the waterfall only by
    # letting the grid/DH bar absorb the 33 Mt difference between two bases, which
    # overstated it by 23 per cent and contradicted the 62/38 split the appendix reports.
    g = pd.read_csv(R / "grid_sensitivity.csv").set_index("year")
    e25 = g.loc[2025, "co2_actual_Mt"]; frozen50 = g.loc[2050, "co2_frozen_grid_Mt"]
    act50 = g.loc[2050, "co2_actual_Mt"]
    d_sw, d_gr = e25 - frozen50, frozen50 - act50
    b.bar(0, e25, color="#8c8c8c", width=0.62)
    b.bar(1, d_sw, bottom=frozen50, color="#1f5fa8", width=0.62)
    b.bar(2, d_gr, bottom=act50, color="#2ca02c", width=0.62)
    b.bar(3, act50, color="#b03a3a", width=0.62)
    for x0, y0 in [(0, e25), (1, frozen50), (2, act50)]:
        b.plot([x0 + 0.31, x0 + 0.69], [y0, y0], color="#666", lw=0.7, ls=":")
    b.set_xticks(range(4))
    b.set_xticklabels(["2025", "Technology\nswitch", "Grid + DH\nclean-up", "2050"], fontsize=6.8)
    b.text(0, e25 + 9, f"{e25:.0f}", ha="center", fontsize=8)
    b.text(3, act50 + 9, f"{act50:.0f}", ha="center", fontsize=8)
    b.text(1, frozen50 + d_sw / 2, f"$-${d_sw:.0f}", ha="center", va="center",
           fontsize=7.5, color="white")
    b.text(2, act50 + d_gr / 2, f"$-${d_gr:.0f}", ha="center", va="center",
           fontsize=7.5, color="white", fontweight="bold")
    b.set_ylabel("CO₂ (Mt yr⁻¹)")
    tag(b, "b")
    save(fig, "P08_emissions_attribution")


# ── P09: H2 gap + delivery ────────────────────────────────────────────────────
def p09():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 4.4),
                               gridspec_kw={"width_ratios": [1.25, 1]})
    g = pd.read_csv(R / "h2_hp_gap.csv").sort_values("gap_2050", ascending=True)
    y = np.arange(len(g))
    # Colour by which side of the line a country sits on, and how far. The old
    # thresholds assumed a single near-zero case; the gap now spans both signs widely.
    cols = ["#2ca02c" if v <= -15 else ("#8fbf6a" if v <= 0 else
            ("#e8b54d" if v <= 15 else "#7d5ba6")) for v in g.gap_2050]
    a.barh(y, g.gap_2050, color=cols, height=0.72)
    a.axvline(0, color="#333", lw=0.8)
    # The four shades encode the size of the gap and had no key anywhere, in the figure or
    # the caption, so the reader saw an encoding with no way to read it.
    # The bar is h2_lcoh MINUS best_hp_lcoh, so a NEGATIVE bar means hydrogen is the
    # cheaper carrier. The first version of this key read the sign the other way round and
    # labelled Denmark, hydrogen's widest win at -29.7, as "heat pump ahead" -- the legend
    # contradicted the paper's own headline. Keep the labels tied to the sign, not to the
    # order the colours happen to appear in.
    _key = [(("#2ca02c", "hydrogen ahead by over 15"), ("#8fbf6a", "hydrogen ahead by up to 15")),
            (("#e8b54d", "heat pump ahead by up to 15"), ("#7d5ba6", "heat pump ahead by over 15"))]
    a.legend([plt.Rectangle((0, 0), 1, 1, color=c) for row in _key for c, _ in row],
             [lab + " \u20ac/MWh" for row in _key for _, lab in row],
             loc="lower center", bbox_to_anchor=(0.5, -0.30), ncol=2, frameon=False,
             fontsize=6.2, handlelength=1.0, handletextpad=0.4, columnspacing=1.0)
    a.set_yticks(y); a.set_yticklabels(g.country, fontsize=6.6)
    a.set_ylim(-0.8, len(g) - 0.2)
    a.set_xlabel("H₂ boiler $-$ best heat pump, 2050 (€/MWh)")
    # No leader-line callout naming the widest win and the count. It was pinned inside the
    # axes over a 29-row bar chart, so it crossed bars, and the reader can already see which
    # bar is longest. The count is stated in the caption, where it cannot collide with data.
    tag(a, "a")
    hi = pd.read_csv(R / "h2_infra_scenario.csv").set_index("country")
    cases = ["baseline", "convert", "blend", "newbuild"]
    labels = ["Free gas-grid\nreuse", "Retrofit", "Blend", "New-build"]
    eu_c = [hi.gap_baseline.mean()] + [hi[f"gap_{c}_central"].mean() for c in cases[1:]]
    eu_l = [hi.gap_baseline.mean()] + [hi[f"gap_{c}_low"].mean() for c in cases[1:]]
    eu_h = [hi.gap_baseline.mean()] + [hi[f"gap_{c}_high"].mean() for c in cases[1:]]
    dk_c = [hi.loc["DK", "gap_baseline"]] + [hi.loc["DK", f"gap_{c}_central"] for c in cases[1:]]
    dk_l = [hi.loc["DK", "gap_baseline"]] + [hi.loc["DK", f"gap_{c}_low"] for c in cases[1:]]
    dk_h = [hi.loc["DK", "gap_baseline"]] + [hi.loc["DK", f"gap_{c}_high"] for c in cases[1:]]
    x = np.arange(4)
    b.fill_between(x, eu_l, eu_h, color="#7d5ba6", alpha=0.15, lw=0)
    b.plot(x, eu_c, "-o", ms=3.5, color="#7d5ba6", label="EU-27+UK+CH mean")
    b.fill_between(x, dk_l, dk_h, color="#2ca02c", alpha=0.15, lw=0)
    b.plot(x, dk_c, "-s", ms=3.5, color="#2ca02c", label="Denmark")
    b.axhline(0, color="#333", lw=0.8)
    b.set_xticks(x); b.set_xticklabels(labels, fontsize=7)
    b.set_ylabel("Gap (€/MWh); $\\leq$0 = H₂ at parity")
    b.legend(loc="upper left")
    tag(b, "b")
    save(fig, "P09_h2_gap_delivery")


# ── P10: winter peak (load-duration -> endogenous price -> dispatch) ─────────
def p10():
    fig = plt.figure(figsize=(6.3, 4.1), layout="constrained")
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 0.95, 1.0])
    a = fig.add_subplot(gs[0, 0]); b = fig.add_subplot(gs[0, 1]); c = fig.add_subplot(gs[0, 2])

    lp = pd.read_csv(R / "heat_load_profile.csv").set_index("country")
    CUM = [100, 500, 1000, 2000, 4000, 8760]
    reps = [("DE", "largest market", "#1f5fa8", "o", "-"),
            ("SE", "coldest tier", "#2ca02c", "s", "--"),
            ("ES", "mildest tier", "#e07b39", "^", ":")]
    for cc, why, col, mk, ls in reps:
        r_ = lp.loc[cc]
        ys = np.array([r_[f"GW_at_{h}h"] for h in CUM]) / r_["avg_GW"]
        a.plot(CUM, ys, marker=mk, ls=ls, ms=2.8, color=col, label=f"{cc} ({why})")
    a.axvspan(0, 2000, color="#b03a3a", alpha=0.07, lw=0)
    a.text(950, a.get_ylim()[1] * 0.97, "peak slice", fontsize=6.8, color="#b03a3a",
           ha="center", va="top")
    a.set_xscale("log"); a.set_xticks([100, 1000, 8760])
    a.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    a.set_xlabel("Hours per year exceeded")
    a.set_ylabel("Heat demand (multiple of annual mean)")
    a.legend(loc="lower left", fontsize=6.6, handlelength=1.3)
    tag(a, "a")

    p = pd.read_csv(R / "power_peak_price.csv")
    # These four were typed here as literals, and a reviewer who searched Economics, Policy,
    # Config and every results CSV for them found nothing, so a journal figure appeared to
    # carry numbers with no artefact behind them. They are the reduced form's own fallback
    for i, sc in enumerate(SCEN):
        d = p[p.scenario == sc].peak_elec
        b.vlines(i, d.min(), d.max(), color=SC[sc], lw=5, alpha=0.35)
        b.scatter([i], [d.mean()], s=24, color=SC[sc], zorder=3)
        # The "former constant" dashes were the hard-coded peak price this layer replaced.
        # They are a note to ourselves about a superseded version, not a result, and they
        # were the third mark type in a panel whose legend already sat over the data.
    # H2 Push: the cold-snap price across only the units hydrogen sets (mean
    # peak_elec where the H2 turbine is marginal), the value the text cites.
    hp = p[p.scenario == "H2_PUSH"]
    h2set = hp[hp.marginal_unit == "h2_turbine"].peak_elec
    j = SCEN.index("H2_PUSH")
    b.scatter([j], [h2set.mean()], s=30, marker="D", facecolor="white",
              edgecolor=SC["H2_PUSH"], linewidths=1.2, zorder=5)
    b.annotate(f"€{h2set.mean():.0f}", (j, h2set.mean()), xytext=(-9, -1),
               textcoords="offset points", fontsize=6.6, color=SC["H2_PUSH"],
               va="center", ha="right")
    b.scatter([], [], s=24, color="#666", label="scenario mean")
    b.scatter([], [], s=30, marker="D", facecolor="white", edgecolor="#666",
              linewidths=1.2, label="countries hydrogen sets")
    b.set_xticks(range(4))
    b.set_xticklabels(["Curr.", "Stated", "Net\nZero", "H2\nPush"], fontsize=7)
    b.set_ylabel("Winter-peak electricity price (€/MWh-e)")
    # Below the axes. Inside, at upper left, it covered the top of the Net Zero band,
    # which is the widest band in the panel and the one the text discusses.
    b.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=6.6,
             frameon=False, handletextpad=0.3, columnspacing=1.0)
    tag(b, "b")

    # The symmetric accounting basis, which is what both papers now headline. This panel
    # used to read h2_wins_peak from merit_order_heat.csv, which is the basis that charges
    # hydrogen no last-mile network, so after the text moved to the symmetric counts the
    # grid and its own printed totals would have contradicted the paragraph beside them.
    wn = pd.read_csv(R / "building_peak_winners.csv")
    wn = wn[wn.basis == "symmetric"]
    won = {r.scenario: set(str(r.countries).split()) for r in wn.itertuples()}
    mo = pd.read_csv(R / "merit_order_heat.csv")
    piv = pd.DataFrame(
        {s: [c in won.get(s, set()) for c in sorted(mo.country.unique())] for s in SCEN},
        index=sorted(mo.country.unique()))
    piv = piv.loc[piv.sum(axis=1).sort_values(ascending=False).index]
    c.imshow(piv.values.astype(float), aspect="auto",
             cmap=matplotlib.colors.ListedColormap(["#f0f0f0", "#2ca02c"]), vmin=0, vmax=1)
    counts = piv.sum(axis=0).astype(int)
    c.set_xticks(range(4))
    c.set_xticklabels(["Curr.", "Stated", "Net\nZero", "H2\nPush"], fontsize=7)
    c.tick_params(axis="x", pad=13)     # room for the count row drawn just below the grid
    # The counts used to be a third line of the tick label, under an already two-line
    # label, which put them a centimetre below the column they count.
    for i, sc in enumerate(SCEN):
        c.text(i, len(piv) - 0.25, f"{counts[sc]}/29", ha="center", va="top", fontsize=7,
               fontweight="bold", color="#1a1a1a")
    c.set_yticks(range(len(piv))); c.set_yticklabels(piv.index, fontsize=6.6)
    c.set_xticks(np.arange(-0.5, 4), minor=True)
    c.set_yticks(np.arange(-0.5, len(piv)), minor=True)
    c.grid(which="minor", color="white", lw=0.8)
    c.tick_params(which="minor", length=0)
    for spine in c.spines.values():
        spine.set_visible(False)
    tag(c, "c")
    save(fig, "P10_winter_peak")


# ── P11: missing money (CAPEX-recovery lollipop) ─────────────────────────────
def p11():
    mp = pd.read_csv(R / "merit_order_profit.csv")
    w = mp[mp.wins_peak].copy()
    w["rec"] = 100 * w.gross_margin_eur_kw_yr / w.ann_capex_eur_kw_yr
    w = w.sort_values("rec")
    w["lab"] = w.country + " (" + w.scenario.map(
        {"STATED_POLICIES": "Stated", "NET_ZERO": "Net Zero", "H2_PUSH": "H2 Push"}) + ")"
    fig, ax = plt.subplots(figsize=(5.0, 4.6))
    y = np.arange(len(w))
    ax.hlines(y, 0, w.rec, color=[SC[sc] for sc in w.scenario], lw=1.6, alpha=0.85)
    ax.scatter(w.rec, y, s=22, color=[SC[sc] for sc in w.scenario], zorder=3)
    # The x-axis used to run to 112 so the break-even line at 100 could be drawn, which
    # spent nearly two-thirds of the panel on empty space to the right of a maximum of
    # about 40. Break-even is now stated on the axis rather than drawn at it, and the
    # scale is set by the data.
    top = float(w.rec.max())
    ax.set_xlim(0, top * 1.30)
    ax.set_yticks(y); ax.set_yticklabels(w.lab, fontsize=6.6)
    ax.set_ylim(-0.8, len(w) - 0.2)
    ax.set_xlabel("Share of annualised peaker capital recovered by the rent (%)\n"
                  "Break-even is 100%; no country-scenario pair reaches half of it")
    for yi, (v, sc) in enumerate(zip(w.rec, w.scenario)):
        # One decimal, not zero. Portugal recovers 0.47 per cent and printed as "0"
        # beside a visibly non-zero lollipop, and Sweden's 39.93 and Denmark's 39.67 both
        # printed "40" while Denmark's 39.30 printed "39".
        ax.text(v + top * 0.02, yi, f"{v:.1f}", va="center", ha="left", fontsize=6.5,
                color=SC[sc])
    handles = [plt.Line2D([], [], color=SC[sc], marker="o", ls="-", ms=5,
                          label=SHORT[sc]) for sc in SCEN[1:]]
    # Below the axes. Inside, at lower right, it covered the four lowest-recovery rows,
    # which are the rows the figure exists to show.
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3,
              frameon=False, handletextpad=0.4, handlelength=1.4, fontsize=7.5)
    save(fig, "P11_missing_money")


# ── P12: DH stack + expansion (labels de-collided) ────────────────────────────
def p12():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 3.2), layout="constrained",
                               gridspec_kw={"width_ratios": [1.4, 1]})
    md = pd.read_csv(R / "merit_order_dh.csv")
    d = md[md.scenario == "H2_PUSH"].set_index("country")
    panel = [c for c in ["DE", "DK", "NL", "FR", "PL", "SE"] if c in d.index]
    order = ["waste", "large_hp", "biomass", "gas_chp", "h2"]
    lab = {"waste": "Waste heat", "large_hp": "Large HP", "biomass": "Biomass CHP",
           "gas_chp": "Gas CHP", "h2": "Hydrogen"}
    col = {"waste": "#9e9e9e", "large_hp": "#1f5fa8", "biomass": "#4daf6a",
           "gas_chp": "#b03a3a", "h2": "#7d5ba6"}
    x = np.arange(len(panel)); wdt = 0.15
    hatch = {"h2": H2_HATCH, "gas_chp": "xx"}
    for i, k in enumerate(order):
        bs = a.bar(x + (i - 2) * wdt, [d.loc[c, f"mc_{k}"] for c in panel], wdt,
                   color=col[k], label=lab[k], hatch=hatch.get(k),
                   edgecolor="white" if k == "gas_chp" else "none", linewidth=0.0)
        if k == "h2":
            ink_h2_hatch(bs)
    a.set_xticks(x); a.set_xticklabels(panel)
    a.set_ylabel("Marginal cost (€/MWh heat)")
    a.legend(ncol=2, loc="upper left", columnspacing=0.8, handletextpad=0.3, fontsize=6.8)
    tag(a, "a")

    mc = pd.read_csv(R / "mc_country_NET_ZERO.csv")
    sh = mc[(mc.variable == "tech_share") & (mc.tech == "district_heat")]
    piv = sh.pivot_table(index="country", values="q50", columns="year")
    tot = mc[(mc.variable == "tech_share")].pivot_table(index="country", columns="year",
                                                        values="q50", aggfunc="sum")
    piv = (piv / tot).dropna() * 100
    piv = piv.sort_values(2050)
    yy = np.arange(len(piv))
    for yi, (c_, row) in zip(yy, piv.iterrows()):
        up = row[2050] >= row[2025]
        col = "#e07b39" if up else "#9e9e9e"
        b.plot([row[2025], row[2050]], [yi, yi], "-", color=col, lw=1.4, zorder=2)
        b.scatter([row[2025]], [yi], s=14, facecolor="white", edgecolor=col, lw=1.1, zorder=3)
        b.scatter([row[2050]], [yi], s=16, color=col, zorder=3)
    b.set_yticks(yy); b.set_yticklabels(piv.index, fontsize=6.8)
    b.set_ylim(-0.8, len(piv) - 0.2)
    b.scatter([], [], s=14, facecolor="white", edgecolor="#555", lw=1.1, label="2025")
    b.scatter([], [], s=16, color="#555", label="2050")
    b.legend(loc="lower right", handletextpad=0.3)
    b.set_xlabel("District-heat share of useful heat (%)")
    tag(b, "b")
    save(fig, "P12_dh_stack_expansion")


# ── P13: infrastructure bill ──────────────────────────────────────────────────
def p13():
    ib = pd.read_csv(R / "infrastructure_bill.csv")
    eu = ib.groupby("scenario")[["elec_bn_central", "dh_bn_central", "h2_bn_central",
                                 "total_bn_central", "total_bn_low", "total_bn_high"]].sum().reindex(SCEN)
    fig, ax = plt.subplots(figsize=(4.6, 3.1))
    x = np.arange(4)
    parts = [("elec_bn_central", "Electricity reinforcement", "#1f5fa8"),
             ("dh_bn_central", "District-heat expansion", "#e07b39"),
             ("h2_bn_central", "Hydrogen network", "#7d5ba6")]
    bottom = np.zeros(4)
    for colname, lab, c in parts:
        v = eu[colname].values
        ax.bar(x, v, bottom=bottom, color=c, width=0.62, label=lab)
        bottom += v
    ax.errorbar(x, eu.total_bn_central, fmt="none",
                yerr=[eu.total_bn_central - eu.total_bn_low,
                      eu.total_bn_high - eu.total_bn_central],
                ecolor="#333", capsize=3, lw=0.9)
    for xi, v in zip(x, eu.total_bn_central):
        ax.text(xi + 0.36, v, f"{v:.0f}", fontsize=7.5, va="center")
    ax.set_xticks(x); ax.set_xticklabels([SHORT[s].replace(" ", "\n") for s in SCEN], fontsize=7.5)
    ax.set_ylabel("Cumulative network investment,\n2025–2050 (bn €)")
    ax.legend(loc="upper left")
    save(fig, "P13_infrastructure_bill")


# ── P14: Switzerland ──────────────────────────────────────────────────────────
def p14():
    yrs = [2025, 2030, 2035, 2040, 2045, 2050]
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    hp_lo = [min(compute_lcoh("hp_air", "CH", y), compute_lcoh("hp_ground", "CH", y)) for y in yrs]
    hp_hi = [max(compute_lcoh("hp_air", "CH", y), compute_lcoh("hp_ground", "CH", y)) for y in yrs]
    ax.fill_between(yrs, hp_lo, hp_hi, color="#1f5fa8", alpha=0.22, lw=0)
    ax.plot(yrs, [compute_lcoh("gas_boiler", "CH", y) for y in yrs], color="#9e9e9e", ls=":")
    for h2s, col in [("STRANDED", "#b03a3a"), ("CENTRAL", "#7d5ba6"), ("RAPID", "#e07b39")]:
        v = [compute_lcoh("h2_boiler", "CH", y, h2_scenario=h2s) for y in yrs]
        ax.plot(yrs, v, color=col, lw=1.7)
        ax.annotate("H₂ " + h2s, (2050, v[-1]), xytext=(4, 0),
                    textcoords="offset points", color=col, fontsize=7, va="center")
    ax.annotate("Gas boiler", (2050, compute_lcoh("gas_boiler", "CH", 2050)),
                xytext=(4, -9), textcoords="offset points", color="#9e9e9e",
                fontsize=7, va="center")
    # The label used to sit inside the band at 2030, where the H2 CENTRAL line crosses it,
    # so blue text lay over a purple line over a blue band. It goes to the right margin
    # with the other three series labels, and says what the band is rather than naming it.
    # The right margin already carries three series labels, so the band is named inside
    # the axes at its left end, in the empty quadrant under it, where nothing else runs.
    ax.annotate("Heat pumps\n(air to ground source)", (2025.4, 122), fontsize=7,
                color="#1f5fa8", va="center", ha="left")
    ax.set_ylabel("LCOH (€/MWh useful)")
    ax.set_xlabel("Year")
    ax.set_xticks([2025, 2030, 2040, 2050]); ax.set_xlim(2024.5, 2062)
    ax.set_ylim(0, 315)
    save(fig, "P14_switzerland")


# ── P15: Sobol + rho ──────────────────────────────────────────────────────────
def p15():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.9), layout="constrained")
    gs_ = pd.read_csv(R / "global_sensitivity.csv").sort_values("ST")
    labmap = {"envelope_rate_mult": "Envelope renovation rate",
              "occupancy_mult": "Occupancy (household size)",
              "dwelling_size_mult": "Dwelling size", "population_mult": "Population"}
    y = np.arange(len(gs_))
    # Words, not $S_T$/$S_1$: a mathtext subscript renders at 0.70x the declared size, so
    # these two labels printed at 5.25 pt. The symbols live in the caption and the text.
    a.barh(y, gs_.ST, height=0.55, color="#1f5fa8", label="Total order")
    a.scatter(gs_.S1, y, s=22, color="#e07b39", zorder=3, label="First order")
    a.set_yticks(y); a.set_yticklabels([labmap.get(d, d) for d in gs_.driver], fontsize=7.5)
    a.xaxis.set_major_locator(mticker.MaxNLocator(nbins=4, prune="upper"))
    a.set_xlabel("Sobol index, 2050 useful heat")
    # Inside at lower right it covered the Population bar, which is the smallest bar and
    # the one a reader checks against the first-order dot.
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=2, frameon=False,
             handletextpad=0.3, fontsize=7.5)
    tag(a, "a")
    rho = pd.read_csv(R / "rho_sensitivity.csv")
    for sc in SCEN:
        d = rho[rho.scenario == sc].sort_values("rho")
        if len(d):
            b.plot(d.rho, d.width, "-o", ms=3.5, color=SC[sc], label=SHORT[sc])
            b.annotate(f"{d.width.iloc[-1]:.0f}", (1.0, d.width.iloc[-1]), xytext=(4, 0),
                       textcoords="offset points", fontsize=6.6, color=SC[sc], va="center")
    b.set_xlabel("Renovation correlation " + chr(36) + chr(92) + "rho" + chr(36))
    b.set_ylabel("2050 demand band width (TWh)")
    b.set_xticks([0, 0.5, 1]); b.set_xlim(-0.10, 1.30)
    b.legend(loc="upper left", handlelength=1.4)
    tag(b, "b")
    save(fig, "P15_sensitivity")


# ── P16: H2 supply routes + reinforcement robustness ──────────────────────────
def p16():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 4.4), layout="constrained")
    dc = pd.read_csv(R / "h2_delivered_cost.csv").sort_values("delivered_eur_mwh")
    y = np.arange(len(dc))
    ROUTE_COL = {"green": "#2ca02c", "blue": "#1f5fa8", "pipe": "#e07b39", "ship": "#9e9e9e"}
    ROUTE_LAB = {"green": "Domestic green", "blue": "Blue (gas+CCS)",
                 "pipe": "Pipeline import", "ship": "Ship (ammonia)"}
    cols = [ROUTE_COL.get(r_, "#555") for r_ in dc.cheapest_route]
    a.barh(y, dc.delivered_eur_mwh, color=cols, height=0.72)
    dcr = dc.reset_index(drop=True)
    alts = []
    for i_, row in dcr.iterrows():
        vals = [row[k] for k in ("green", "blue", "pipe", "ship")
                if k != row.cheapest_route and pd.notna(row[k])]
        alts.append(min(vals) if vals else np.nan)
    a.scatter(alts, y, s=14, marker="|", color="#333", lw=1.2, zorder=3)
    a.set_yticks(y); a.set_yticklabels(dcr.country, fontsize=6.6)
    a.set_ylim(-0.8, len(dcr) - 0.2)
    a.set_xlim(0, 118)
    a.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune="upper"))
    a.set_xlabel("Delivered hydrogen cost\n2050 (€/MWh)")
    # Only the routes that actually win somewhere. Blue and ship are cheapest in no
    # country, so their swatches named nothing, and blue reuses panel (b)'s colour for a
    # different quantity.
    _won = [k for k in ROUTE_COL if (dc.cheapest_route == k).any()]
    handles = [plt.Rectangle((0, 0), 1, 1, color=ROUTE_COL[k]) for k in _won]
    handles.append(plt.Line2D([], [], color="#333", marker="|", ls="", ms=8, mew=1.4))
    a.legend(handles, [ROUTE_LAB[k] for k in _won] + ["Next-best route"],
             loc="lower right", fontsize=6.6, handletextpad=0.4, handlelength=1.0)
    tag(a, "a")

    er = pd.read_csv(R / "elec_reinforcement_sensitivity.csv")
    # h2_baseline is the free-gas-grid arm of the sensitivity script (h2_infra=False),
    # kept explicitly so this panel still asks the conservative-for-heat-pump question:
    # charge the heat pump its HIGH reinforcement and hydrogen no network at all.
    er["headroom"] = er.h2_baseline - er.hp_reinf_high
    er = er.sort_values("headroom")
    y = np.arange(len(er))
    cols = ["#b03a3a" if v < 0 else "#1f5fa8" for v in er.headroom]
    b.barh(y, er.headroom, color=cols, height=0.72)
    b.axvline(0, color="#333", lw=0.8)
    b.set_yticks(y); b.set_yticklabels(er.country, fontsize=6.6)
    b.set_ylim(-0.8, len(er) - 0.2)
    b.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune="lower"))
    b.set_xlabel("H₂ without network cost minus\nHP at high reinforcement\n2050 (€/MWh); $>$0 = HP cheaper")
    tag(b, "b")
    save(fig, "P16_supply_robustness")


# ── P17: cost-optimal pathway ─────────────────────────────────────────────────
def p17():
    p = pd.read_csv(R / "cost_opt_pathway.csv")
    p = p[(p.variant == "COST_OPT_90") & (p["mode"] == "trajectory")]
    g = p.groupby(["year", "tech"]).useful_heat_MWh.sum().reset_index()
    tot = g.groupby("year").useful_heat_MWh.transform("sum")
    g["share"] = g.useful_heat_MWh / tot
    years = sorted(g.year.unique())
    techs = [t for t in TECH_COLOR if t in set(g.tech)]
    M = [[float(g[(g.year == y) & (g.tech == t)].share.sum()) for y in years] for t in techs]
    fig, ax = plt.subplots(figsize=(5.4, 2.9))
    ax.stackplot(years, M, colors=[TECH_COLOR[t] for t in techs],
                 labels=[TECH_LABEL[t] for t in techs])
    ax.set_xlim(min(years), max(years)); ax.set_ylim(0, 1)
    ax.set_ylabel("Share of useful heat"); ax.set_xticks(YEARS)
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), handlelength=1.2)
    save(fig, "P17_costopt_pathway")


# ── P30: the three-test verdict ─────────────────────────────────────────────────────────
def p30():
    """One-view overview figure for the end of the introduction (doubles as the
    abstract graphic): the merit-order reframe carried left to right across the
    three linked arenas -- building winter peak -> district-heat stack -> power
    sector -- with the monotonic country-count tuples rising with policy ambition,
    the recurring 'carbon price on the competitor opens the niche' mechanism, and
    the missing-money caveat. All counts and prices are read live from the engine
    outputs so the schematic cannot drift from the numbers in the text."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    # --- numbers, straight from results (verified against the section text) ------
    mo = pd.read_csv(R / "merit_order_heat.csv")
    md = pd.read_csv(R / "merit_order_dh.csv")
    pe = pd.read_csv(R / "power_peaker_economics.csv")
    pe50 = pe[pe.year == 2050]
    rec = pd.read_csv(R / "power_peaker_recovery_projection.csv")

    build_counts = [int(mo[mo.scenario == s].h2_wins_peak.sum()) for s in SCEN]
    dh_counts    = [int(md[md.scenario == s].h2_beats_gas_chp.sum()) for s in SCEN]
    pow_counts   = [int((pe50[pe50.scenario == s].h2_var_eur_mwh
                         < pe50[pe50.scenario == s].gas_var_eur_mwh).sum()) for s in SCEN]

    d = pe50[pe50.scenario == "H2_PUSH"]
    h2_var  = float(d.h2_var_eur_mwh.mean())                  # ~221
    gas_var = float(d.gas_var_eur_mwh.mean())                 # ~239
    h2_rec  = float(rec[(rec.year == 2050) &
                        (rec.scenario == "H2_PUSH")].h2_recovery_pct.iloc[0])  # ~13

    SCEN_SHORT = ["Curr.", "Stated", "Net Zero", "H2 Push"]
    SCOL = [SC[s] for s in SCEN]                              # grey / blue / green / red

    fig = plt.figure(figsize=(7.2, 4.6))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    INK, MUTE = "#1a1a1a", "#6b6b6b"

    # --- header ------------------------------------------------------------------
    ax.text(2.6, 96.5, "Where hydrogen can win the dispatch", fontsize=13.5,
            fontweight="bold", color=INK, va="top")
    ax.text(2.6, 90.6,
            "On the full annual cost of heat the heat pump is cheapest in 22 of 29 countries, so "
            "heat electrifies. Hydrogen enters only\n"
            "as a peaker, priced on short-run marginal cost against the carbon-taxed competitor, "
            "and is tested in three linked\n"
            "arenas. The count is the number of the 29 countries in which it would be dispatched.",
            fontsize=8.0, color=MUTE, va="top", linespacing=1.45)

    # --- three arena cards -------------------------------------------------------
    cards = [
        dict(x=3.5,  title="Building winter peak",
             sub="vs the carbon-taxed gas boiler\nat the peak hour", counts=build_counts),
        dict(x=36.5, title="District-heat stack",
             sub="vs gas CHP on the marginal\nheat unit", counts=dh_counts),
        dict(x=69.5, title="Power sector",
             sub="H2 turbine vs gas peaker,\n€/MWh-e", counts=pow_counts),
    ]
    CW, CH, CY = 27.0, 47.0, 23.0          # card width, height, bottom y
    cell_w = (CW - 4.0) / 4.0

    for k, c in enumerate(cards):
        x0 = c["x"]
        ax.add_patch(FancyBboxPatch((x0, CY), CW, CH, boxstyle="round,pad=0.0,rounding_size=1.6",
                                    fc="#fbfbfb", ec="#d9d9d9", lw=1.0, zorder=1))
        # arena name + what it is tested against
        ax.text(x0 + 1.8, CY + CH - 3.0, f"{k+1}.  {c['title']}", fontsize=10.0,
                fontweight="bold", color=INK, va="top")
        ax.text(x0 + 1.8, CY + CH - 8.6, c["sub"], fontsize=7.4, color=MUTE, va="top",
                linespacing=1.35)

        # the monotonic count strip: one cell per scenario, rising with ambition
        cy = CY + 9.5
        for j in range(4):
            cx = x0 + 2.0 + j * cell_w
            won = c["counts"][j]
            shade = SCOL[j] if won > 0 else "#eaeaea"
            txtc  = "white" if won > 0 else "#9a9a9a"
            ax.add_patch(FancyBboxPatch((cx, cy), cell_w - 0.9, 9.2,
                                        boxstyle="round,pad=0.0,rounding_size=0.8",
                                        fc=shade, ec="none", zorder=3))
            ax.text(cx + (cell_w - 0.9) / 2, cy + 5.9, f"{won}", ha="center", va="center",
                    fontsize=12.5, fontweight="bold", color=txtc, zorder=4)
            ax.text(cx + (cell_w - 0.9) / 2, cy + 1.9, "/29", ha="center", va="center",
                    fontsize=6.6, color=txtc, zorder=4)
            ax.text(cx + (cell_w - 0.9) / 2, cy - 2.2, SCEN_SHORT[j], ha="center", va="top",
                    fontsize=6.6, color=MUTE, rotation=0)
        # ambition arrow under the strip
        ax.annotate("", xy=(x0 + CW - 2.2, CY + 1.4), xytext=(x0 + 2.2, CY + 1.4),
                    arrowprops=dict(arrowstyle="-|>", color="#9a9a9a", lw=1.0,
                                    shrinkA=0, shrinkB=0))
        ax.text(x0 + CW / 2, CY + 2.7, "rising policy ambition", ha="center", va="bottom",
                fontsize=6.6, color=MUTE, style="italic")

    # bridge arrows linking the arenas (the heating-to-power bridge)
    for x0 in (cards[0]["x"] + CW, cards[1]["x"] + CW):
        ax.add_patch(FancyArrowPatch((x0 + 0.7, CY + CH / 2), (x0 + 5.3, CY + CH / 2),
                                     arrowstyle="-|>", mutation_scale=12,
                                     color="#b03a3a", lw=1.8, zorder=5))
    ax.text(cards[0]["x"] + CW + 3.0, CY + CH / 2 + 2.6, "electrify", ha="center",
            fontsize=6.2, color="#b03a3a", style="italic")
    ax.text(cards[1]["x"] + CW + 3.0, CY + CH / 2 + 2.6, "winter\npeak", ha="center",
            fontsize=6.2, color="#b03a3a", style="italic", linespacing=1.0)

    # --- mechanism + caveat ribbon ----------------------------------------------
    ry = 1.2
    ax.add_patch(FancyBboxPatch((3.5, ry), 93.0, 19.6,
                                boxstyle="round,pad=0.0,rounding_size=1.6",
                                fc="#f4f1ec", ec="#e3ddd3", lw=1.0, zorder=1))
    # mechanism (left half)
    ax.text(5.4, ry + 17.0, "Mechanism", fontsize=8.6, fontweight="bold",
            color="#7a5b1e", va="top")
    ax.text(5.4, ry + 13.6,
            "The carbon price on the competitor, not cheap hydrogen,\n"
            "opens the niche, and the counts scale with ambition\n"
            f"because carbon pricing does. At the power peak the H2\n"
            f"turbine (about {h2_var:.0f}) sits just below gas (about {gas_var:.0f} €/MWh-e).",
            fontsize=7.2, color="#5d5546", va="top", linespacing=1.45)
    # divider rule
    ax.plot([50.0, 50.0], [ry + 1.8, ry + 17.8], color="#d8cdb8", lw=1.0, zorder=2)
    # caveat (right half)
    ax.text(52.2, ry + 17.0, "Caveat", fontsize=8.6, fontweight="bold",
            color="#9c4a36", va="top")
    ax.text(52.2, ry + 13.6,
            "Even where it wins, the peaker runs too few hours to\n"
            f"recover its capital, about {h2_rec:.0f}% under H2 Push. That is\n"
            "the classic missing-money problem, so the role is a\n"
            "dispatched one, not one a market would build unaided.",
            fontsize=7.2, color="#7a4a3b", va="top", linespacing=1.45)

    save(fig, "P30_three_test_verdict")


# ── P19: grid carbon-intensity trajectories ───────────────────────────────────
def p19():
    yrs = list(range(2025, 2051, 5))
    M = np.array([[get_grid_carbon_intensity(c, y) for c in EU] for y in yrs])
    med = np.median(M, axis=1); lo = np.percentile(M, 10, axis=1); hi = np.percentile(M, 90, axis=1)
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.fill_between(yrs, lo, hi, color="#1f5fa8", alpha=0.15, lw=0,
                    label="10th–90th percentile (countries)")
    ax.plot(yrs, med, color="#1f5fa8", label="Median country")
    # The three country lines were drawn without a label, so the legend keyed only the band
    # and the median and a reader saw three dashed series it did not explain. The left-edge
    # annotation names them but the legend has to as well, since that is where a reader looks.
    for cc, col, what in [("PL", "#b03a3a", "most carbon-intensive"),
                          ("DE", "#e07b39", "largest"), ("SE", "#2ca02c", "cleanest")]:
        ax.plot(yrs, [get_grid_carbon_intensity(cc, y) for y in yrs], lw=1.0, ls="--",
                color=col, label=f"{cc}, {what}")
        # The left-edge annotation that used to name each line is redundant now the legend
        # does, and at 7 pt it was the smallest type in the figure: moving the legend below
        # the axes cut the print scale to 0.81 and took that 7 pt under the 6 pt floor.
    ax.set_ylabel("Grid carbon intensity (gCO₂ kWh⁻¹)")
    ax.set_xlabel("Year")
    ax.set_xticks(YEARS)
    # The legend sits inside the axes, upper right, where every series has already fallen
    # away and nothing is drawn. Below the axes at ncol=3 it was wider than the plot, and
    # savefig crops to the widest artist, so the saved page was mostly legend: included at
    # 0.95\textwidth the axes themselves printed about 40 per cent of the text width and
    # the figure read as a small picture in a wide white box.
    ax.legend(loc="upper right", frameon=False, fontsize=7.4, handlelength=1.6,
              labelspacing=0.35, borderaxespad=0.2)
    save(fig, "P19_grid_trajectories")


if __name__ == "__main__":
    # A figure that fails here keeps whatever version is already on disk, which is how
    # P01 came to be older than the data it reads: its NUTS3 geometry is not in the
    # repository, so it threw on every rebuild and the batch moved on quietly. The
    # failures are still non-fatal, since one missing input should not cost the other
    # nineteen figures, but they are now counted and listed at the end and the exit
    # status is non-zero, so a rebuild cannot report success while a figure is stale.
    # p01 is NOT in this list. It is the superseded map (see its own comment): it reads a
    # gitignored GISCO geojson that no script in the repository writes, so the documented
    # command "python -m scripts.paper_figures" exited 1 on every fresh clone, for a figure
    # the submission includes as Fig. 2. The live map is scripts.fig_nuts3_map, which reads
    # a committed cache and writes the same P01_nuts3_map output. Run that instead.
    failed = []
    for f in (p02, p03, p04, p05, p06, p07, p08, p09, p10,
              p11, p12, p13, p14, p15, p16, p17, p19, p30):
        try:
            f()
        except Exception as ex:
            failed.append(f"{f.__name__}: {type(ex).__name__}: {ex}")
            print(f"  [FAIL] {failed[-1]}")
    print(f"Done -> {OUT}")
    if failed:
        print(f"\n{len(failed)} of 19 figures did NOT rebuild and are stale on disk:")
        for x in failed:
            print(f"  - {x}")
        raise SystemExit(1)
