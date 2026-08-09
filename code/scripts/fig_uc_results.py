"""Unit-commitment upgrade of the power dispatch: what the explicit commitment of the firm
fleet changes relative to the reduced-form merit-order clip (2050, EU-27+UK+CH). Three panels:
(a) fleet peaker energy, limits off versus unit commitment; (b) fleet-mean peaker full-load
hours, limits off versus unit commitment; (c) the per-country operating-reserve shortfall the
5 per cent margin implies, summing to the EU-wide firm-capacity adder. White background, no
in-figure title (caption above), house style.

Reads code/results/power_uc_summary.csv (constraints active) and power_uc_limit_summary.csv
(constraints disabled, reproduces the reduced-form clip). Output PNG+PDF to paper/figs/paper/.

Run: cd code && PYTHONPATH=. python -m scripts.fig_uc_results
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from scripts._figstyle import set_style, assert_printable
set_style()

# The earlier layout was one row of three panels on a 12.6 in canvas placed into the
# 455 pt long-paper column, a factor of 0.51, which printed panel (c)'s country codes
# at 3.6 pt. Restacked as two rows on a 7.4 in canvas so the same content prints above
# the 6 pt floor, and the arithmetic is checked on every build.
# explicit gridspec margins below, so disable the global auto-layout
# savefig.bbox=None left the canvas at its declared size, and with right=0.975 plus the
# house style's left-aligned titles, panel (b)'s title ran to x=537.4 pt on a 532.8 pt media
# box: the last character of "2050" was cut off, and the figure shipped that way. "tight"
# extends the canvas to whatever the artists need, which is what every other figure here uses.
plt.rcParams.update({"figure.autolayout": False, "savefig.bbox": "tight"})
FIGW_IN = 7.4
FS_VALUE, FS_TICK_C, FS_BADGE = 10.0, 8.2, 9.5
assert_printable(FIGW_IN, {"value label": FS_VALUE, "panel (c) country code": FS_TICK_C,
                           "total badge": FS_BADGE, "axis/tick default": 9.0},
                 column="long", label="P34_uc_results")

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "paper"; OUT.mkdir(parents=True, exist_ok=True)
OUTA = REPO / "paper" / "figs" / "diagnostics"; OUTA.mkdir(parents=True, exist_ok=True)

YEAR = 2050
uc = pd.read_csv(REPO / "code" / "results" / "power_uc_summary.csv")
lim = pd.read_csv(REPO / "code" / "results" / "power_uc_limit_summary.csv")
uc = uc[uc.year == YEAR].copy()
lim = lim[lim.year == YEAR].copy()

# fleet aggregates
uc_energy = uc.peaker_energy_gwh.sum() / 1000.0          # TWh
lim_energy = lim.peaker_energy_gwh.sum() / 1000.0        # TWh
uc_flh = uc.peaker_energy_gwh.sum() / uc.peaker_cap_gw.sum()
lim_flh = lim.peaker_energy_gwh.sum() / lim.peaker_cap_gw.sum()
res_total = uc.reserve_short_gw.sum()                    # GW

GAS, H2GREY, NAVY, AMBER = "#969696", "#bdbdbd", "#2c6fb3", "#e07b39"

# (a) and (b) share the top row; (c) takes the full width below, where 29 horizontal
# bars need the vertical room their labels do not get in a one-row layout.
fig = plt.figure(figsize=(FIGW_IN, 7.7))
# hspace 0.34 on a row of two 2-bar charts left a blank band of about 17 per cent of the
# canvas, which is roughly an inch of empty page inside a full-width float and is why
# everything else in the figure prints as small as it does.
gs = fig.add_gridspec(2, 2, height_ratios=[0.90, 2.05], hspace=0.30, wspace=0.32,
                      left=0.115, right=0.965, top=0.950, bottom=0.055)
axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])]
fig.patch.set_facecolor("white")

# Panel (a): peaker energy, limits off vs unit commitment
ax = axes[0]; ax.set_facecolor("white")
vals = [lim_energy, uc_energy]
bars = ax.bar([0, 1], vals, width=0.6, color=[H2GREY, NAVY])
for r, v in zip(bars, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + 0.8, f"{v:.1f}", ha="center", va="bottom",
            fontweight="bold", fontsize=FS_VALUE)
pct = 100.0 * (uc_energy - lim_energy) / lim_energy
ax.annotate(f"+{pct:.0f}%", xy=(1, uc_energy), xytext=(0.5, max(vals) * 1.08),
            ha="center", color=AMBER, fontweight="bold", fontsize=FS_VALUE)
ax.set_xticks([0, 1]); ax.set_xticklabels(["Limits\noff", "Unit\ncommitment"])
ax.set_ylabel("Fleet peaker energy (TWh)")
ax.set_ylim(0, max(vals) * 1.22)
ax.set_title("(a) Peaker energy, 2050")

# Panel (b): mean peaker full-load hours, limits off vs unit commitment
ax = axes[1]; ax.set_facecolor("white")
vals = [lim_flh, uc_flh]
bars = ax.bar([0, 1], vals, width=0.6, color=[H2GREY, NAVY])
for r, v in zip(bars, vals):
    ax.text(r.get_x() + r.get_width() / 2, v + 2, f"{v:.0f}", ha="center", va="bottom",
            fontweight="bold", fontsize=FS_VALUE)
ax.set_xticks([0, 1]); ax.set_xticklabels(["Limits\noff", "Unit\ncommitment"])
ax.set_ylabel("Fleet-mean peaker full-load hours")
ax.set_ylim(0, max(vals) * 1.22)
ax.set_title("(b) Peaker utilisation, 2050")

# Panel (c): per-country reserve shortfall, summing to the EU-wide firm-capacity adder
ax = axes[2]; ax.set_facecolor("white")
rs = uc[uc.reserve_short_gw > 0].sort_values("reserve_short_gw", ascending=True)
ax.barh(rs.country, rs.reserve_short_gw, color=NAVY, height=0.72)
ax.set_xlabel("Operating-reserve shortfall (GW)")
ax.tick_params(axis="y", labelsize=FS_TICK_C)
# The EU total goes in the panel title, not in a boxed badge inside the axes. The badge sat
# at the bottom-right corner, which on a sorted bar chart is exactly where the shortest bars
# and their value labels are.
ax.set_title(f"(c) Reserve-margin shortfall, 2050 "
             f"(EU-27+UK+CH total {res_total:.0f} GW)")

for base, name in [(OUT, "P34_uc_results"), (OUTA, "F34_uc_results")]:
    fig.savefig(base / f"{name}.pdf"); fig.savefig(base / f"{name}.png", dpi=200)
plt.close(fig)
print(f"wrote P34_uc_results: energy {lim_energy:.1f}->{uc_energy:.1f} TWh "
      f"(+{pct:.0f}%), FLH {lim_flh:.0f}->{uc_flh:.0f}, reserve total {res_total:.0f} GW")
