"""The heating -> electricity bridge (Abdul's 2026-06-15 reframe, step 2 of the new section).

Heating is electrifying (heat pumps + resistance), so a growing share of HEAT demand becomes
ELECTRICITY demand. Two figures motivate why the power-sector peaker question matters for a
heating paper:

  P28_electrified_heat.png        per-country share of HEATING met DIRECTLY by electricity
                                  (heat pumps + resistance), 2050 vs 2030 -- heat is heavily
                                  electrified (district heat, ~half of it electric large-HP, adds more).
  P29_heat_electricity_share.png  per-country heating ELECTRICITY as a share of total power demand,
                                  2050 -- electrified heat is a material slice of the grid, so the
                                  grid's firm/peaking needs (where hydrogen competes) bear on heating.

Heating electricity = useful heat x (hp_air_share/COP_air + hp_ground_share/COP_ground + resistance).
Total power demand    = national baseline load (ENTSO-E 2023) x growth (x1.40 by 2050) + heating elec.
Tech shares + useful heat: the Monte Carlo (results/mc_country_<scen>.csv, q50). COPs: src.Economics
(temperature/country specific). Scenario = H2 Push, to match the merit-order figures P26/P27;
the printout also reports Net Zero (deeper electrification) for the text.

Reads: results/mc_country_{H2_PUSH,NET_ZERO}.csv; src.Economics.get_cop; power_dispatch baselines.
Out:   paper/figs/paper/{P28_electrified_heat,P29_heat_electricity_share}.png (+pdf, +abdul mirror)
       results/electrification_bridge.csv
Run:   cd code && PYTHONPATH=. python -m scripts.electrification_bridge
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from scripts._figstyle import set_style, short_scen
from scripts.power_dispatch import BASELINE_TWH_2023, BASELINE_GROWTH
set_style()
try:
    from src.Economics import get_cop
except Exception:
    get_cop = None

REPO = Path(__file__).resolve().parents[2]
FIGP = REPO / "paper" / "figs" / "paper"; FIGP.mkdir(parents=True, exist_ok=True)
FIGA = REPO / "paper" / "figs" / "diagnostics"; FIGA.mkdir(parents=True, exist_ok=True)
SCEN = "H2_PUSH"
BLUE, TEAL, RED, DK = "#2c6fb3", "#3fa7b5", "#c0392b", "#1a1a1a"


def save(fig, name):
    for d in (FIGP, FIGA):
        fig.savefig(d / f"{name}.png"); fig.savefig(d / f"{name}.pdf")
    plt.close(fig)


def _cop(tech, c, year, default):
    if get_cop is None:
        return default
    try:
        v = float(get_cop(tech, c, year)); return max(v, 1.5) if v else default
    except Exception:
        return default


def _row(m, c, year):
    d = m[(m.country == c) & (m.year == year)]
    sh = {t: float(d[(d.variable == "tech_share") & (d.tech == t)].q50.iloc[0])
          if len(d[(d.variable == "tech_share") & (d.tech == t)]) else 0.0
          for t in ["hp_air", "hp_ground", "resistance_heater", "district_heat"]}
    uh = d[(d.variable == "useful_heat_TWh") & (d.tech == "all")]
    sh["useful_heat"] = float(uh.q50.iloc[0]) if len(uh) else 0.0
    return sh


def build(scen):
    m = pd.read_csv(RESULTS_DIR / f"mc_country_{scen}.csv")
    rows = []
    for c in sorted(m.country.unique()):
        s50, s40, s30 = _row(m, c, 2050), _row(m, c, 2040), _row(m, c, 2030)
        elec50 = s50["hp_air"] + s50["hp_ground"] + s50["resistance_heater"]
        elec40 = s40["hp_air"] + s40["hp_ground"] + s40["resistance_heater"]
        elec30 = s30["hp_air"] + s30["hp_ground"] + s30["resistance_heater"]
        ca, cg = _cop("hp_air", c, 2050, 3.2), _cop("hp_ground", c, 2050, 4.0)
        heat_elec = s50["useful_heat"] * (s50["hp_air"] / ca + s50["hp_ground"] / cg
                                          + s50["resistance_heater"] / 1.0)
        base = BASELINE_TWH_2023.get(c, 30) * BASELINE_GROWTH[2050]
        rows.append({"country": c, "elec50": elec50, "elec40": elec40, "elec30": elec30, "dh50": s50["district_heat"],
                     "useful_heat": s50["useful_heat"], "heat_elec_twh": heat_elec,
                     "total_elec_twh": base + heat_elec,
                     "share_of_elec": heat_elec / (base + heat_elec) if base + heat_elec else 0.0})
    return pd.DataFrame(rows).set_index("country")


def _emit_country_table(df):
    """Per-country share of heat met directly by electricity, 2030/2040/2050 (meeting ask B)."""
    t = (df[["elec30", "elec40", "elec50"]] * 100).round(0).astype(int)
    t.columns = ["y30", "y40", "y50"]
    t = t.sort_values("y50", ascending=False)
    t.to_csv(RESULTS_DIR / "electrified_share_by_country.csv")
    eu = (df[["elec30", "elec40", "elec50"]].mul(df.useful_heat, axis=0).sum()
          / df.useful_heat.sum() * 100).round(0).astype(int)
    rows = [r"\begin{table}[htbp]", r"\centering", r"\small",
            r"\caption{Share of residential heat met directly by electricity (heat pumps and "
            r"resistance heating), per country, 2030/2040/2050, under H2 Push, with the "
            r"heat-weighted EU-27+UK+CH average in the final row.}",
            r"\label{tab:electrified}", r"\begin{tabular}{lrrr}", r"\toprule",
            r"Country & 2030 & 2040 & 2050 \\", r"\midrule"]
    for c, r in t.iterrows():
        rows.append(f"{c} & {r.y30} & {r.y40} & {r.y50} \\\\")
    rows += [r"\midrule",
             f"EU-27+UK+CH (heat-weighted) & {eu['elec30']} & {eu['elec40']} & {eu['elec50']} \\\\",
             r"\bottomrule", r"\end{tabular}",
             r"\\[2pt]{\footnotesize\textit{Source: Authors' contribution, scenario Monte Carlo medians.}}",
             r"\end{table}", ""]
    (REPO / "paper" / "sections" / "_tab_electrified.tex").write_text("\n".join(rows), encoding="utf8")


def main():
    df = build(SCEN)
    df.to_csv(RESULTS_DIR / "electrification_bridge.csv")
    _emit_country_table(df)
    w = df.useful_heat / df.useful_heat.sum()                          # heat-weighted EU averages
    eu_elec = float((df.elec50 * w).sum() * 100)
    eu_dh_elec = float(((df.elec50 + 0.45 * df.dh50) * w).sum() * 100)  # + electric large-HP in DH (~45%)
    eu_share = float(df.heat_elec_twh.sum() / df.total_elec_twh.sum() * 100)
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")["annual_TWh"]
    cov = 100 * lp[lp.index.isin(df.index)].sum() / lp.sum()       # heat-demand coverage of the 15
    note = f"{len(df)} largest countries · {cov:.0f}% of EU-27+UK+CH heat demand"

    # ---- B (P28): electrified-heat share, 2050 stacked (direct electric + electric DH) + 2030 marker ----
    d = df.sort_values("elec50")
    y = np.arange(len(d)); dh_e = d.dh50 * 0.45        # ~45% of district heat is electric (large HP)
    fig, ax = plt.subplots(figsize=(3.7, 4.7))
    ax.barh(y, d.elec50 * 100, color=BLUE, height=0.68, zorder=3, label="heat pumps + resistance")
    ax.barh(y, dh_e * 100, left=d.elec50 * 100, color="#a9cce8", height=0.68, zorder=3,
            label="electric district heat (~45% of DH)")
    ax.scatter(d.elec30 * 100, y, color=DK, s=18, zorder=6, label="2030 (direct electric)")
    ax.axvline(eu_dh_elec, color=RED, ls="--", lw=1.2, zorder=5)
    ax.text(eu_dh_elec + 1, 0.4, f"EU-27+UK+CH avg {eu_dh_elec:.0f}%", color=RED, fontsize=7.2, va="top")
    ax.set_yticks(y); ax.set_yticklabels(d.index, fontsize=8)
    ax.set_xlabel("Share of heating met by electricity, 2050 (%)", fontsize=8)
    ax.set_title("(a)", loc="left", y=1.24)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.05), ncol=1,
              frameon=False, fontsize=7.2)   # 6.6 printed at 5.77 pt at 0.49\textwidth
    ax.grid(axis="x", color="#ececec", lw=0.8); ax.set_axisbelow(True)
    save(fig, "P28_electrified_heat")

    # ---- C (P29): heating electricity as a share of total power demand, 2050 ----
    d = df.sort_values("share_of_elec")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(3.7, 4.7))
    ax.barh(y, d.share_of_elec * 100, color=TEAL, height=0.7, zorder=3)
    ax.axvline(eu_share, color=RED, ls="--", lw=1.2, zorder=4)
    ax.text(eu_share + 0.3, 0.4, f"EU-27+UK+CH {eu_share:.0f}%", color=RED, fontsize=7.2, va="top")
    ax.set_yticks(y); ax.set_yticklabels(d.index, fontsize=8)
    ax.set_xlabel("Heating electricity, share of total\npower demand, 2050 (%)", fontsize=8)
    ax.set_title("(b)", loc="left")
    ax.grid(axis="x", color="#ececec", lw=0.8); ax.set_axisbelow(True)
    save(fig, "P29_heat_electricity_share")

    nz = build("NET_ZERO"); wz = nz.useful_heat / nz.useful_heat.sum()
    nz_elec = float((nz.elec50 * wz).sum() * 100)
    print(f"{SCEN}: EU direct-electric heat {eu_elec:.0f}% (+electric DH -> {eu_dh_elec:.0f}%); "
          f"heating = {eu_share:.0f}% of power demand. NET_ZERO direct-electric heat {nz_elec:.0f}%.")
    print("Wrote P28_electrified_heat + P29_heat_electricity_share (png+pdf) -> paper + abdul")


if __name__ == "__main__":
    main()
