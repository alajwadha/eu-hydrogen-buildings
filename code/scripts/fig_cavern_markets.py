"""Focused merit-order comparison for the seven salt-cavern markets where hydrogen is much
cheaper than the gas peaker (2050, H2 Push): grouped bars of the operating (short-run marginal)
cost, gas peaker versus hydrogen turbine. White background, no in-figure title (caption above).

Run: cd code && PYTHONPATH=. python -m scripts.fig_cavern_markets
"""
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from scripts._figstyle import set_style, TECH_COLOR, H2_HATCH, ink_h2_hatch
set_style()

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "paper"; OUT.mkdir(parents=True, exist_ok=True)
OUTA = REPO / "paper" / "figs" / "diagnostics"; OUTA.mkdir(parents=True, exist_ok=True)
# The win set is DERIVED from the data below, not listed here. A hard-coded list would
# keep plotting the same seven markets, and contradicting its own caption, if the model
# moved. Ordered by hydrogen's advantage so the bars read monotonically.

# Source the SAME short-run cost series the manuscript quotes: power_peak_price.csv
# (the endogenous winter-peak merit order, which yields the seven-market win set).
# power_peaker_economics.csv carries a different SRMC series that wins in 15 markets;
# plotting from it made the bars disagree with the caption and the text.
e = pd.read_csv(REPO / "code" / "results" / "power_peak_price.csv")
d = e[e.scenario == "H2_PUSH"].set_index("country").rename(
    columns={"ocgt_srmc": "gas_var_eur_mwh", "h2_turbine_srmc": "h2_var_eur_mwh"})
d = d[d.h2_var_eur_mwh < d.gas_var_eur_mwh]                      # the win set, from the data
d = d.assign(_adv=d.gas_var_eur_mwh - d.h2_var_eur_mwh).sort_values("_adv", ascending=False)
x = np.arange(len(d)); w = 0.38

fig, ax = plt.subplots(figsize=(5.4, 3.4))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
b1 = ax.bar(x - w / 2, d.gas_var_eur_mwh, w, color="#969696", label="Gas peaker")
# Hydrogen was drawn #d62728 here, a third colour for it across the submission after the
# purple of Fig. 3 and the orange the graphical abstract used. It is the house purple now,
# and it carries the house hatch, which is what keeps it separable from the gas grey.
b2 = ax.bar(x + w / 2, d.h2_var_eur_mwh, w, color=TECH_COLOR["h2_boiler"],
            label="H₂ turbine", hatch=H2_HATCH, edgecolor="white", linewidth=0.0)
ink_h2_hatch(b2)
for bars in (b1, b2):
    for r in bars:
        ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 3, f"{r.get_height():.0f}",
                ha="center", va="bottom", fontsize=8.5)
# This row printed f"-{margin:.0f}" over a margin computed as gas minus hydrogen, which
# is positive: the minus sign was inserted by hand and contradicted the caption, which
# calls the same quantity an advantage of about EUR 72 to 89/MWh-e. The row also sat
# inside the data rectangle at 1.10x the tallest bar, so a reader read "-89" against the
# y-axis at about 280 EUR/MWh-e. It is keyed, signed correctly and lifted clear of the
# frame here.
for i, c in enumerate(d.index):
    margin = d.gas_var_eur_mwh[c] - d.h2_var_eur_mwh[c]
    ax.annotate(f"{margin:.1f}", xy=(i, 1.0), xycoords=("data", "axes fraction"),
                xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                fontsize=8.5, color="#2e8b57", annotation_clip=False)
ax.annotate("H₂ advantage (€/MWh-e)", xy=(0.0, 1.0), xycoords="axes fraction",
            xytext=(0, 16), textcoords="offset points", ha="left", va="bottom",
            fontsize=7.5, color="#2e8b57", style="italic", annotation_clip=False)
ax.set_xticks(x); ax.set_xticklabels(d.index)
ax.set_ylabel("Operating cost, 2050 (€/MWh-e)")
ax.set_ylim(0, max(d.gas_var_eur_mwh) * 1.18)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2,
          frameon=False, fontsize=8)
fig.tight_layout()
for base, name in [(OUT, "P33_cavern_markets"), (OUTA, "F33_cavern_markets")]:
    fig.savefig(base / f"{name}.pdf")
    # No local dpi override: the house 400 is what keeps the Word twin above
    # Elsevier's 300 dpi floor, and 200 here put this one figure at 167.
    fig.savefig(base / f"{name}.png")
plt.close(fig)
print("wrote P33_cavern_markets: gas vs H2 operating cost for", list(d.index))
