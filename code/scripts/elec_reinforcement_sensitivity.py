"""Electricity distribution-reinforcement sensitivity (closes the transmission-layer gap).

Mass heat-pump electrification adds a coincident winter peak to the LV/MV distribution
grid that the existing retail tariff does not pay for. The baseline model (like most
buildings studies) does not charge this reinforcement, while hydrogen CAN be charged its
last-mile network cost (h2_infra). This script charges the symmetric electricity-side cost
(Economics.electricity_distribution_adder_eur_mwh, ~EUR 1-38/MWh low-high) to the heat
pump and checks whether the headline conclusion -- heat pumps beat hydrogen and gas -- is
robust to it. It is the conservative-for-HP test: HP pays its network cost, H2 does not.

Run: cd code && PYTHONPATH=. python -m scripts.elec_reinforcement_sensitivity
Out: code/results/elec_reinforcement_sensitivity.csv + figure F14_elec_reinforcement.png
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import compute_lcoh, electricity_distribution_adder_eur_mwh, LABOUR_COST_MULTIPLIER
from scripts._figstyle import set_style, legend_below
set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)
Y = 2050


def best_hp(c, **kw):
    return min(compute_lcoh("hp_air", c, Y, **kw), compute_lcoh("hp_ground", c, Y, **kw))


def main():
    rows = []
    for c in LABOUR_COST_MULTIPLIER:
        # This script sweeps the electricity reinforcement adder, so its heat-pump
        # baseline must not already carry one. compute_lcoh now applies both adders by
        # default, so every row here states its own treatment explicitly rather than
        # relying on the default.
        hp = best_hp(c, elec_reinforce=False)                      # HP baseline, no reinforcement
        hp_lo = best_hp(c, elec_reinforce=True, elec_reinforce_bound="low")
        hp_ce = best_hp(c, elec_reinforce=True, elec_reinforce_bound="central")
        hp_hi = best_hp(c, elec_reinforce=True, elec_reinforce_bound="high")
        h2 = compute_lcoh("h2_boiler", c, Y, h2_infra=False)       # H2 with free gas-grid reuse
        h2_infra = compute_lcoh("h2_boiler", c, Y, h2_infra="blend")   # H2 charged its network too
        gas = compute_lcoh("gas_boiler", c, Y)
        rows.append({
            "country": c, "hp_base": hp, "hp_reinf_low": hp_lo, "hp_reinf_central": hp_ce,
            "hp_reinf_high": hp_hi, "adder_central": round(electricity_distribution_adder_eur_mwh(c), 1),
            "h2_baseline": h2, "h2_with_infra": h2_infra, "gas": gas,
            # conservative-for-HP gap: HP pays its reinforcement (high), H2 pays nothing
            "gap_hpHighReinf_vs_h2base": round(h2 - hp_hi, 1),
            "hp_still_beats_h2": hp_hi < h2, "hp_still_beats_gas": hp_hi < gas,
        })
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "elec_reinforcement_sensitivity.csv", index=False)

    n = len(df)
    print(f"Electricity distribution-reinforcement sensitivity (2050, {n} countries)")
    print(f"  reinforcement adder on HP LCOH: low {df.adder_central.min()*0.5:.1f}-{df.hp_reinf_high.sub(df.hp_base).max():.1f} EUR/MWh (band)")
    print(f"  even with the HIGH reinforcement on HP and ZERO network cost on H2:")
    print(f"     HP still beats H2 in {int(df.hp_still_beats_h2.sum())}/{n} countries")
    print(f"     HP still beats gas in {int(df.hp_still_beats_gas.sum())}/{n} countries")
    print(f"     mean HP-to-H2 headroom remaining: {df.gap_hpHighReinf_vs_h2base.mean():.0f} EUR/MWh")

    # figure: HP with reinforcement band vs H2 baseline, sorted by reinforced HP
    d = df.sort_values("hp_reinf_central")
    y = np.arange(n)
    fig, ax = plt.subplots(figsize=(7.6, 9.0))
    ax.hlines(y, d.hp_base, d.hp_reinf_high, color="#9ecae1", lw=3, label="HP + reinforcement (base→high)")
    ax.scatter(d.hp_reinf_central, y, color="#08519c", s=18, zorder=3, label="HP + reinforcement (central)")
    ax.scatter(d.h2_baseline, y, color="#6a51a3", marker="D", s=20, zorder=3, label="H₂ boiler (no network cost)")
    ax.scatter(d.gas, y, color="#969696", marker="s", s=16, zorder=3, label="gas boiler")
    ax.set_yticks(y); ax.set_yticklabels(d.country, fontsize=7.5)
    ax.set_xlabel("LCOH, 2050 (€/MWh useful)")
    ax.set_title("Heat-pump cost with grid-reinforcement vs hydrogen and gas (2050)")
    legend_below(ax, ncol=2)
    fig.savefig(FIG / "F14_elec_reinforcement.png"); plt.close(fig)
    print("\nWrote results/elec_reinforcement_sensitivity.csv + F14_elec_reinforcement.png")


if __name__ == "__main__":
    main()
