"""Electricity merit-order placement of hydrogen (the 2026-06-15 reframe, Abdul).

Per the meeting: electricity is priced on OPERATING (short-run marginal) cost, NOT capex -- a
sunk capital cost does not set the spot price. So we order every generator by its short-run
marginal cost (SRMC, EUR/MWh-e) and ask WHERE the H2 turbine sits. Under a high carbon price the
gas peaker is dear; if hydrogen's SRMC undercuts it, hydrogen CAN take that dispatchable-backup
role. Capex re-enters only as a caveat (a capacity payment), quantified in scripts/capacity_payment.py.

Two figures (split out of the old two-panel P26 and restructured for publication):
  P26_merit_order.png   EU merit-order COST LADDER: SRMC by technology, 2050 (Hydrogen Push),
                        hydrogen highlighted just below the gas peaker.
  P27_h2_crossover.png  per-country H2-vs-gas operating-cost MARGIN (diverging bars), 2050:
                        hydrogen undercuts the gas peaker in N of 29 countries.

Short-run marginal costs (EUR/MWh-e, 2050), fuel + VOM (+ carbon on fossil) ONLY, no capex:
  Solar / wind       ~1-2   negligible variable O&M           (IRENA 2023; NREL ATB 2024)
  Hydro (run-of-river) ~3   O&M only                          (IEA Hydropower 2021)
  Nuclear            ~12    fuel ~7 + O&M ~5                   (IEA WEO 2023; World Nuclear Assoc. 2023)
  Biomass            ~55    feedstock / electrical efficiency  (IRENA Renewable Power Gen. Costs 2023)
  Gas peaker (OCGT)  ~256   gas wholesale/eta + carbon x EF/eta  (this model; DEA Tech. Catalogue 2023)
  H2 turbine         ~168   delivered H2/eta + seasonal storage  (this model; OIES H2 price + Caglayan 2020)
  Coal               ~330   coal/eta + high carbon (residual; ~0 GW by 2050)
Carbon, gas and hydrogen prices are the scenario's own time-varying paths (src/Policy, src/Economics);
gas and H2 SRMC are read straight from the dispatch's per-country economics so the figure and the
dispatch never disagree.

Reads: data/power_capacity.csv, results/power_peaker_economics.csv, results/power_dispatch_summary.csv
Out:   paper/figs/paper/{P26_merit_order,P27_h2_crossover}.png (+ pdf, + diagnostics mirror)
Run:   cd code && PYTHONPATH=. python -m scripts.power_merit_order
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from scripts._figstyle import (set_style, assert_printable, short_scen, H2_HATCH,
                               ink_h2_hatch)
set_style()

REPO = Path(__file__).resolve().parents[2]
FIGP = REPO / "paper" / "figs" / "paper"; FIGP.mkdir(parents=True, exist_ok=True)
FIGA = REPO / "paper" / "figs" / "diagnostics"; FIGA.mkdir(parents=True, exist_ok=True)
SCEN, YEAR = "H2_PUSH", 2050

# SRMC of the low-/zero-carbon fleet (EUR/MWh-e), fuel + VOM only. Sources in the module docstring.
SRMC_LOWC = {"solar": 1.0, "wind_on": 1.5, "wind_off": 2.0, "hydro": 3.0,
             "nuclear": 12.0, "biomass": 55.0}
COAL_SRMC = 330.0
LBL = {"solar": "Solar PV", "wind_on": "Onshore wind", "wind_off": "Offshore wind",
       # The SRMC on this rung is the run-of-river value, and the only capacity series we
       # hold is the whole 2050 hydro fleet with reservoir plant in it. Naming the rung
       # for the cost and printing no capacity beside it is the only pairing of the two
       # that is true; the previous row put a run-of-river price against a 162 GW fleet
       # and said so in a note instead of on the page.
       "hydro": "Hydro (run-of-river)", "nuclear": "Nuclear", "biomass": "Biomass",
       "gas": "Gas peaker (OCGT)", "h2": "H₂ turbine", "coal": "Coal"}
COL = {"solar": "#e3c34a", "wind_on": "#4f9d69", "wind_off": "#2f7d52", "hydro": "#3fa7b5",
       # Nuclear was #7d6fb0, one step from hydrogen's #7d5ba6, so the two purple rungs
       # read as one technology in the figure whose whole job is to separate them.
       "nuclear": "#6b7f96", "biomass": "#9bbb6b", "gas": "#9a9a9a", "h2": "#7d5ba6",
       "coal": "#444444"}
H2_GREEN, H2_PALE, GAS_GREY = "#2e8b57", "#a8d5ba", "#9a9a9a"


def save(fig, name):
    for d in (FIGP, FIGA):
        fig.savefig(d / f"{name}.png"); fig.savefig(d / f"{name}.pdf")
    plt.close(fig)


CAVERN_MARKET = "DK"          # named salt-cavern market for the merit-order ladder


def _load():
    cap = pd.read_csv(REPO / "code" / "data" / "power_capacity.csv")
    cap = cap[cap.year == YEAR].groupby("tech").capacity_gw.sum()
    econ = pd.read_csv(RESULTS_DIR / "power_peaker_economics.csv")
    econ = econ[(econ.scenario == SCEN) & (econ.year == YEAR)].set_index("country")
    summ = pd.read_csv(RESULTS_DIR / "power_dispatch_summary.csv")
    summ = summ[(summ.basis == "total_elec") & (summ.year == YEAR)].set_index("country")
    return cap, econ, summ


def fig_merit_ladder(cap, econ, summ):
    """Figure A -- the merit-order cost ladder (SRMC by technology, hydrogen highlighted)."""
    # Price the dispatchable tip for a NAMED salt-cavern market, from the same
    # short-run cost series the manuscript quotes (power_peak_price.csv). Previously
    # this used the 29-country mean of power_peaker_economics.csv, which is a different
    # series and showed hydrogen below gas on average -- contradicting both this
    # figure's caption ("in a salt-cavern market") and the text, which states that at
    # the cross-country median hydrogen sits ABOVE gas.
    pp = pd.read_csv(RESULTS_DIR / "power_peak_price.csv")
    pp = pp[(pp.scenario == SCEN) & (pp.country == CAVERN_MARKET)].iloc[0]
    gas, h2 = float(pp.ocgt_srmc), float(pp.h2_turbine_srmc)
    pk = float(summ.peaker_cap_gw.sum())               # the firm dispatchable (peaker) fleet, GW
    # None means "print no capacity for this rung". Hydro takes it because the rung's cost
    # is run-of-river and the only capacity series is the whole fleet.
    rows = [(LBL[t], s, (None if t == "hydro" else float(cap.get(t, 0.0))), COL[t])
            for t, s in SRMC_LOWC.items()]
    # Both dispatchable rows carry the SAME firm fleet: they are alternative fuels for one
    # peaker fleet, not two fleets that add. Only these two rungs are model output; the
    # low-carbon rungs above are literature SRMC constants (SRMC_LOWC).
    rows += [(LBL["h2"], h2, pk, COL["h2"]), (LBL["gas"], gas, pk, COL["gas"])]
    # Coal is a ~3 GW residual by 2050. Including it pushed the axis maximum to ~400,
    # squeezed five bars into slivers, and at the current canvas its value label
    # overprinted the capacity annotation. Excluded below 5 GW.
    if float(cap.get("coal", 0.0)) > 5.0:
        rows.append((LBL["coal"], COAL_SRMC, float(cap["coal"]), COL["coal"]))
    rows.sort(key=lambda r: r[1])                       # ascending SRMC = merit order
    labels, vals, caps, cols = zip(*rows)
    y = np.arange(len(rows))
    # Leave room on the right for the capacity column: the longest bar's value label
    # must clear it, or the two overprint.
    xmax = max(vals) * 1.42

    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    bars = ax.barh(y, vals, color=cols, edgecolor="white", linewidth=0.6, height=0.70,
                   zorder=3)
    # Hydrogen is hatched purple in Figs 3, 6, 7 and in both graphical abstracts, and was
    # solid here alone, so the reader who learned the key elsewhere had to relearn it.
    for b, lab in zip(bars, labels):
        if lab == LBL["h2"]:
            b.set_hatch(H2_HATCH)
            ink_h2_hatch(b)
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.invert_yaxis()   # cheapest at top
    # The two dispatchable rungs are one fleet burning either fuel. Printing the same
    # 278 GW on both rows made the column read as a 556 GW peaking fleet, and the note
    # underneath had to say it was not. A brace spanning the two rows with the figure
    # printed once says it on the page instead.
    i_h2, i_gas = labels.index(LBL["h2"]), labels.index(LBL["gas"])
    shared = abs(i_h2 - i_gas) == 1
    for yi, v, cgw in zip(y, vals, caps):
        ax.text(v + xmax * 0.012, yi, f"€{v:.0f}", va="center", ha="left",
                fontsize=9.5, color="#1a1a1a")
        if cgw is None or (shared and yi == max(i_h2, i_gas)):
            continue
        # White bbox: the capacity column sits inside the axes, so the vertical grid line
        # at 350 ran straight through these labels. The overlap checker missed it because
        # it compares text against text and callouts against data, never against the axis
        # furniture drawn behind them.
        lab = f"{cgw:,.0f} GW"
        ax.text(xmax * 0.995, yi + (0.5 if shared and yi == min(i_h2, i_gas) else 0.0),
                lab, va="center", ha="right",
                fontsize=8, color="#999999", zorder=4,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    if shared:
        # The brace itself, plus what the shared number means.
        xb = xmax * 0.999
        ax.plot([xb, xb], [min(i_h2, i_gas) - 0.30, max(i_h2, i_gas) + 0.30],
                color="#bbbbbb", lw=0.8, zorder=3, clip_on=False)
        # 7.4 at this figure's 0.85 print scale sets 6.3 pt; 6.6 would set 5.6 pt.
        ax.text(xmax * 0.995, max(i_h2, i_gas) + 0.60, "one fleet, either fuel",
                va="center", ha="right", fontsize=7.4, color="#999999", style="italic",
                zorder=4, bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    # The grey right-hand column carried no header, so the figure alone did not say what
    # those numbers are; only the caption did.
    ax.text(xmax * 0.995, -0.72, "2050 fleet", va="bottom", ha="right",
            fontsize=8.0, color="#999999", style="italic", zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))   # >= 6 pt at this figure's 0.78 scale
    # dashed guide at H2's SRMC: it sits below gas and coal (the bars crossing it to the right)
    ax.axvline(h2, color=COL["h2"], ls="--", lw=1.3, alpha=0.85, zorder=2)
    # The bar tip already prints this value. Labelling the guide with it too printed the
    # same number twice about a centimetre apart; the guide only needs to say what it is.
    ax.text(h2 - xmax * 0.012, -0.55, "H₂", color=COL["h2"], fontweight="bold",
            fontsize=9, ha="right", va="bottom")
    ax.set_xlim(0, xmax); ax.set_ylim(len(rows) - 0.4, -0.9)
    # Stop the x ticks before the capacity column, so the grid does not run into it
    # and leave orphaned stubs between the rows.
    ax.set_xticks([t for t in ax.get_xticks() if t <= max(vals) * 1.08])
    ax.set_xlabel("Short-run marginal cost, 2050 (€/MWh-e), fuel and carbon only")
    ax.grid(axis="x", color="#ececec", lw=0.8, zorder=0)
    # The house style sets axes.grid=True on the y axis, and asking for an x grid does not
    # turn that off. On a horizontal bar chart the y axis is categorical, so those lines
    # measure nothing; they were drawn straight through the capacity column, which is why
    # the earlier fix to trim the x ticks did not clear it. This is the axis that was wrong.
    ax.grid(axis="y", visible=False)
    # The axes run to xmax to make room for that column, so the bottom spine ran on past
    # the last tick and under numbers it does not scale. Clip it to the plotted range.
    ax.spines["bottom"].set_bounds(0, max(ax.get_xticks()))
    ax.set_axisbelow(True)
    save(fig, "P26_merit_order")
    return gas, h2, pk


def fig_crossover(econ):
    """Figure B -- per-country operating-cost margin (gas minus H2); diverging, sorted."""
    d = econ.copy()
    d["margin"] = d.gas_var_eur_mwh - d.h2_var_eur_mwh         # >0 => hydrogen cheaper
    d = d.sort_values("margin", ascending=False)
    y = np.arange(len(d))
    # A single green over every positive margin conflated two very different cases. The
    # manuscript's result rests on seven markets whose margin runs 85 to 99 EUR/MWh-e --
    # exactly the salt-cavern set power_peak_price.csv selects -- while eight more clear
    # zero by 0.2 to 8, inside any reasonable read of model noise. The threshold is set
    # from the data's own order-of-magnitude break, not chosen: sorted margins step from
    # 85.3 straight down to 8.0, so anything in [10, 80] separates the two groups
    # identically. Pale green marks the marginal wins so the eye cannot read them as
    # equivalent to the seven.
    DECISIVE_EUR_MWH = 40.0
    cols = [H2_GREEN if m >= DECISIVE_EUR_MWH else (H2_PALE if m > 0 else GAS_GREY)
            for m in d.margin]
    nwin = int((d.margin > 0).sum())
    ndecisive = int((d.margin >= DECISIVE_EUR_MWH).sum())
    _narrow = d.margin[(d.margin > 0) & (d.margin < DECISIVE_EUR_MWH)]
    narrow_max = float(_narrow.max()) if len(_narrow) else 0.0

    # This was a 7.8 in canvas placed at 0.62\textwidth in the long paper, a factor of
    # 0.50, which printed the tip labels at 3.8 pt and the country codes at 4.1 pt. Drawn
    # at the column width instead, so the scale is about 1 and the fonts print as set.
    FIGW_IN, FS_TIP, FS_CODE, FS_SIDE = 6.2, 8.0, 8.5, 9.5
    assert_printable(FIGW_IN, {"tip label": FS_TIP, "country code": FS_CODE,
                               "side annotation": FS_SIDE, "axis label": 10.0},
                     column="long", label="P27_h2_crossover")
    fig, ax = plt.subplots(figsize=(FIGW_IN, 7.4))
    ax.barh(y, d.margin.values, color=cols, edgecolor="white", linewidth=0.5, height=0.74, zorder=3)
    ax.axvline(0, color="#333333", lw=1.0, zorder=4)
    ax.set_yticks(y); ax.set_yticklabels(d.index, fontsize=FS_CODE); ax.invert_yaxis()
    ax.set_xlabel("Hydrogen's operating-cost advantage over the gas peaker, 2050 (€/MWh-e)")
    # value label at each bar tip (€/MWh-e), so the near-zero cluster (e.g. ES +0, BG -0) is legible
    span = float(d.margin.max() - d.margin.min())
    pad = span * 0.012
    for yi, m, col in zip(y, d.margin.values, cols):
        ha = "left" if m >= 0 else "right"
        ax.text(m + (pad if m >= 0 else -pad), yi, f"{m:+.0f}", va="center", ha=ha,
                fontsize=FS_TIP, color=col, zorder=5)
    ax.margins(x=0.10)               # headroom so the tip labels are never clipped
    ax.text(0.985, 0.015, "hydrogen cheaper  →", transform=ax.transAxes, ha="right", va="bottom",
            color=H2_GREEN, fontweight="bold", fontsize=FS_SIDE)
    ax.text(0.015, 0.015, "←  gas cheaper", transform=ax.transAxes, ha="left", va="bottom",
            color="#777777", fontweight="bold", fontsize=FS_SIDE)
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor=H2_GREEN, edgecolor="white",
              label=f"hydrogen wins decisively ({ndecisive} markets, all salt-cavern)"),
        Patch(facecolor=H2_PALE, edgecolor="white",
              label=f"hydrogen wins narrowly ({nwin - ndecisive} markets, by at most "
                    f"\u20ac{narrow_max:.0f}/MWh-e)"),
        Patch(facecolor=GAS_GREY, edgecolor="white",
              label=f"gas wins ({len(d) - nwin} markets)")],
        loc="lower center", bbox_to_anchor=(0.5, 1.005), ncol=1, frameon=False,
        fontsize=FS_TIP, handlelength=1.4, handleheight=0.9, borderaxespad=0.0)
    ax.grid(axis="x", color="#ececec", lw=0.8, zorder=0); ax.set_axisbelow(True)
    ax.grid(axis="y", visible=False)     # categorical axis, as above
    save(fig, "P27_h2_crossover")
    return nwin, ndecisive


def main():
    cap, econ, summ = _load()
    gas, h2, pk = fig_merit_ladder(cap, econ, summ)
    nwin, ndecisive = fig_crossover(econ)
    peak = float(summ.peak_gw.sum())
    # The manuscript's win set is the seven salt-cavern markets from
    # power_peak_price.csv. The looser power_peaker_economics series wins in 15
    # markets and previously drove this headline to 263 GW / 29%; report the
    # manuscript's definition so the console cannot contradict the paper.
    ppw = pd.read_csv(RESULTS_DIR / "power_peak_price.csv")
    ppw = ppw[ppw.scenario == SCEN]
    win7 = sorted(ppw.loc[ppw.h2_turbine_srmc < ppw.ocgt_srmc, "country"])
    wincap = float(summ.loc[[c for c in win7 if c in summ.index]].peaker_cap_gw.sum())
    print(f"P26 merit ladder: H2 €{h2:.0f} < gas €{gas:.0f}/MWh-e (by €{gas-h2:.0f}); peaker fleet {pk:.0f} GW")
    print(f"P27 crossover:    H2 undercuts gas in {nwin}/29 countries, {ndecisive} of them "
          f"decisively (the manuscript's {len(win7)}); the other "
          f"{nwin - ndecisive} clear zero by under EUR 10/MWh-e")
    print(f"Headline: H2 can take ~{100*wincap/peak:.0f}% of EU peak capacity (~{wincap:.0f} of {peak:.0f} GW)")
    print("Wrote P26_merit_order + P27_h2_crossover (png+pdf) -> paper/figs/paper + diagnostics")


if __name__ == "__main__":
    main()
