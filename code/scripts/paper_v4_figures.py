"""
paper_v4_figures.py - new figures for Paper v4
==============================================
Adds the figures introduced in the v4 revision (COST_OPT least-cost scenario +
per-country 2025 heating mix + source-audited costs). All written to paper/figs/
as 300-dpi PDFs.

  fig22_costopt_country_map.pdf   - 2050 cost-optimal heat-pump share by country (choropleth)
  fig23_costopt_pathway.pdf       - EU least-cost tech-share pathway, -75/-90/-100% targets
  fig24_implied_carbon_price.pdf  - per-country implied carbon price (cap shadow price)
  fig25_heating_mix_2025.pdf      - 2025 residential heating mix by country (stacked)
  fig26_cost_of_ambition.pdf      - PV system cost vs target + trajectory-vs-snapshot lock-in
  fig27_costopt_eu_mix_targets.pdf- EU 2050 mix across the three ambition targets
  fig28_heatmix_crosscheck.pdf    - Eurostat vs national heating-mix divergence (validation)
  fig29_lcoh_country_tech.pdf     - LCOH heatmap by country x technology (2030, audited costs)
  fig30_abatement_supply.pdf      - abatement supply curve (countries by implied carbon price)
  fig31_hp_share_scenarios.pdf    - 2050 heat-pump share by country across all four scenarios

Run from the repo root:
  python code/scripts/paper_v4_figures.py
  python code/scripts/paper_v4_figures.py --only fig22 fig24
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
sys.path.insert(0, str(REPO_ROOT / "code"))
sys.path.insert(0, str(REPO_ROOT / "code" / "src"))
sys.path.insert(0, str(REPO_ROOT / "code" / "scripts"))

from Visualise import WONG_PALETTE, TECH_SHORT  # noqa: E402
from Config import load_heating_mix_2025  # noqa: E402
from Economics import compute_lcoh  # noqa: E402

FIGS_DIR = REPO_ROOT / "paper" / "figs"
FIGS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS = REPO_ROOT / "code" / "results"
GISCO = REPO_ROOT / "code" / "data" / "raw" / "gisco"

SERIF = ["Liberation Serif", "Times New Roman", "Times", "DejaVu Serif"]
SANS = ["Liberation Sans", "Helvetica", "Arial", "DejaVu Sans"]
matplotlib.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05, "font.family": SANS, "font.sans-serif": SANS,
    "font.serif": SERIF, "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.titlepad": 8,
    "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "legend.fontsize": 9, "legend.frameon": False, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.7, "axes.edgecolor": "#333333",
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

TECHS = ["gas_boiler", "oil_boiler", "biomass_boiler", "resistance_heater",
         "hp_air", "hp_ground", "district_heat", "h2_boiler"]
TECH_COLORS = {
    "gas_boiler": "#8c8c8c", "oil_boiler": "#4d4d4d",
    "biomass_boiler": WONG_PALETTE["green"], "resistance_heater": WONG_PALETTE["yellow"],
    "hp_air": WONG_PALETTE["blue"], "hp_ground": WONG_PALETTE["sky"],
    "district_heat": WONG_PALETTE["orange"], "h2_boiler": WONG_PALETTE["purple"],
}
C_MUTED = "#666666"
COST_OPT_BIND = WONG_PALETTE["red"]


def _title(ax, text):
    ax.set_title(text, fontfamily="serif", fontsize=12, fontweight="bold", loc="left", pad=8)


def _save(fig, name):
    out = FIGS_DIR / name
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.relative_to(REPO_ROOT)}  ({out.stat().st_size/1024:.0f} KB)")


def _country_tech_2050(scenario):
    """Return {country: {tech: share}} at 2050 from mc_country_<scenario>.csv."""
    p = RESULTS / f"mc_country_{scenario}.csv"
    if not p.exists():
        return {}
    df = pd.read_csv(p)
    df = df[(df.year == 2050) & (df.variable == "tech_share")]
    out = {}
    for c, g in df.groupby("country"):
        out[c] = dict(zip(g.tech, g.q50))
    return out


# ─────────────────────────────────────────────────────────────────────────────
def fig22_costopt_country_map():
    import geopandas as gpd
    try:
        gdf = gpd.read_file(GISCO / "NUTS_RG_01M_2021_4326_LEVL_3.geojson", engine="pyogrio")
    except Exception:
        gdf = gpd.read_file(GISCO / "NUTS_RG_01M_2021_4326_LEVL_3.geojson")
    gdf = gdf[gdf["LEVL_CODE"] == 3].copy()
    gdf["geometry"] = gdf["geometry"].simplify(0.02, preserve_topology=True)
    ctry = gdf.dissolve(by="CNTR_CODE").reset_index()

    cm = _country_tech_2050("COST_OPT_90")
    hp = {c: v.get("hp_air", 0) + v.get("hp_ground", 0) for c, v in cm.items()}
    ctry["hp"] = ctry["CNTR_CODE"].map(hp) * 100.0

    fig, ax = plt.subplots(figsize=(7.0, 7.4))
    ctry.plot(ax=ax, color="#e8e8e8", edgecolor="white", linewidth=0.2, rasterized=True)
    sub = ctry[ctry["hp"].notna()]
    sub.plot(ax=ax, column="hp", cmap="YlGnBu", vmin=0, vmax=100,
             edgecolor="white", linewidth=0.3, legend=True, rasterized=True,
             legend_kwds={"label": "Heat-pump share of 2050 useful heat (%)",
                          "shrink": 0.5, "pad": 0.01, "aspect": 24})
    ax.set_xlim(-13, 34); ax.set_ylim(34, 72); ax.set_aspect(1.6); ax.axis("off")
    _title(ax, "Cost-optimal 2050 heat-pump share by country (COST_OPT, −90%)")
    ax.text(0.0, -0.02, f"{sub['hp'].notna().sum()} countries. Least-cost LP, per-country "
            "emissions cap. Source: mc_country_COST_OPT_90.csv.",
            transform=ax.transAxes, fontsize=7.5, color=C_MUTED)
    _save(fig, "fig22_costopt_country_map.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig23_costopt_pathway():
    targets = [("75", "−75%"), ("90", "−90%"), ("100", "net-zero")]
    years = [2025, 2030, 2040, 2050]
    order = ["gas_boiler", "oil_boiler", "biomass_boiler", "resistance_heater",
             "district_heat", "h2_boiler", "hp_ground", "hp_air"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), sharey=True)
    for ax, (key, lab) in zip(axes, targets):
        df = pd.read_csv(RESULTS / f"mc_summary_COST_OPT_{key}.csv")
        ts = df[df.variable == "tech_share"]
        bottoms = np.zeros(len(years))
        for t in order:
            vals = np.array([ts[(ts.tech == t) & (ts.year == y)]["q50"].sum() for y in years]) * 100
            ax.fill_between(years, bottoms, bottoms + vals, color=TECH_COLORS[t], alpha=0.9, linewidth=0)
            bottoms = bottoms + vals
        ax.set_title(f"Cost-optimal, {lab} by 2050")
        ax.set_xlim(2025, 2050); ax.set_xticks(years); ax.set_ylim(0, 100)
        ax.set_xlabel("Year")
    axes[0].set_ylabel("Share of EU useful heat (%)")
    handles = [mpatches.Patch(color=TECH_COLORS[t], label=TECH_SHORT[t]) for t in order]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=8.5,
               bbox_to_anchor=(0.5, -0.06), frameon=True, edgecolor="#cccccc")
    fig.suptitle("EU least-cost heating-technology pathway by emissions ambition, 2025–2050",
                 fontsize=12, fontweight="bold", x=0.09, ha="left", y=1.02)
    _save(fig, "fig23_costopt_pathway.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig24_implied_carbon_price():
    sp = pd.read_csv(RESULTS / "cost_opt_shadow_prices.csv")
    d = sp[(sp.variant == "COST_OPT_90") & (sp.year == 2050)].copy()
    d = d.sort_values("shadow_eur_tco2", ascending=True)
    d = d[d.shadow_eur_tco2 >= 0]
    fig, ax = plt.subplots(figsize=(7.4, 7.2))
    y = np.arange(len(d))
    colors = [COST_OPT_BIND if v > 1 else "#b8c4cc" for v in d.shadow_eur_tco2]
    ax.barh(y, d.shadow_eur_tco2, color=colors, height=0.7, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(d.country, fontsize=8)
    ax.set_xlabel("Implied carbon price to meet −90% cap by 2050 (EUR/tCO₂)")
    for i, (_, r) in enumerate(d.iterrows()):
        if r.shadow_eur_tco2 > 1:
            ax.text(r.shadow_eur_tco2 + 2, i, f"{r.shadow_eur_tco2:.0f}", va="center",
                    fontsize=8, fontweight="bold", color="#222222")
    _title(ax, "Per-country implied carbon price (cost-optimal, −90%)")
    ax.text(0.0, -0.06, "Red = the cap binds (cost-minimisation alone misses the target); "
            "grey = non-binding (€0). Source: cost_opt_shadow_prices.csv.",
            transform=ax.transAxes, fontsize=7.5, color=C_MUTED)
    _save(fig, "fig24_implied_carbon_price.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig25_heating_mix_2025():
    hm = load_heating_mix_2025()
    rows = sorted(hm.items(), key=lambda kv: kv[1]["gas_boiler"] + kv[1]["oil_boiler"])
    countries = [c for c, _ in rows]
    fig, ax = plt.subplots(figsize=(7.6, 8.0))
    y = np.arange(len(countries))
    left = np.zeros(len(countries))
    for t in TECHS:
        vals = np.array([hm[c][t] for c in countries]) * 100
        ax.barh(y, vals, left=left, color=TECH_COLORS[t], height=0.78,
                label=TECH_SHORT[t], zorder=3)
        left += vals
    ax.set_yticks(y); ax.set_yticklabels(countries, fontsize=8)
    ax.set_xlim(0, 100); ax.set_xlabel("Share of 2025 useful heat (%)")
    ax.legend(loc="lower center", ncol=4, fontsize=7.6, bbox_to_anchor=(0.5, -0.12),
              frameon=True, edgecolor="#cccccc")
    _title(ax, "2025 residential heating mix by country (sorted by fossil share)")
    ax.text(0.0, -0.16, "Mean of Eurostat nrg_d_hhq (energy) and national/EHPA (dwelling) "
            "bases. Source: heating_mix_2025_audit.md.",
            transform=ax.transAxes, fontsize=7.3, color=C_MUTED)
    _save(fig, "fig25_heating_mix_2025.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def _costopt_pv_costs():
    """Re-solve the LP to get PV system cost per target + the -90% snapshot."""
    from Optimisation import prepare_data, solve, COST_OPT_TARGETS
    data = prepare_data(demand="bottomup")
    pv = {}
    for k, tgt in COST_OPT_TARGETS.items():
        pv[k] = solve(data, tgt, mode="trajectory")["objective"] / 1e9
    snap90 = solve(data, COST_OPT_TARGETS["90"], mode="snapshot")["objective"] / 1e9
    return data, pv, snap90


def fig26_cost_of_ambition():
    data, pv, snap90 = _costopt_pv_costs()
    keys = ["75", "90", "100"]
    labs = ["−75%", "−90%", "net-zero"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.4),
                                   gridspec_kw={"width_ratios": [1.0, 1.0]})
    # Left: PV system cost vs ambition
    x = np.arange(len(keys))
    ax1.bar(x, [pv[k] for k in keys], color=WONG_PALETTE["blue"], width=0.6, zorder=3)
    for i, k in enumerate(keys):
        ax1.text(i, pv[k] + max(pv.values()) * 0.01, f"{pv[k]:,.0f}", ha="center",
                 va="bottom", fontsize=9, fontweight="bold")
    ax1.set_xticks(x); ax1.set_xticklabels(labs)
    ax1.set_ylabel("Discounted system cost (bn EUR-yr, PV)")
    ax1.set_xlabel("2050 emissions ambition")
    _title(ax1, "Cost of ambition")
    # Right: trajectory vs snapshot (lock-in) for -90%
    ax2.bar([0, 1], [snap90, pv["90"]], color=[WONG_PALETTE["green"], WONG_PALETTE["blue"]],
            width=0.6, zorder=3)
    ax2.set_xticks([0, 1]); ax2.set_xticklabels(["Snapshot\n(no inertia)", "Trajectory\n(turnover)"])
    gap = pv["90"] - snap90
    ax2.set_ylabel("Discounted system cost (bn EUR-yr, PV)")
    ax2.annotate(f"lock-in cost\n+{gap:,.0f} bn", xy=(1, pv["90"]), xytext=(0.5, pv["90"] * 1.04),
                 ha="center", fontsize=8.5, color=COST_OPT_BIND, fontweight="bold")
    _title(ax2, "Cost of stock lock-in (−90%)")
    fig.suptitle("COST_OPT: cost of ambition and of stock-turnover lock-in",
                 fontsize=12, fontweight="bold", x=0.07, ha="left", y=1.02)
    _save(fig, "fig26_cost_of_ambition.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig27_costopt_eu_mix_targets():
    targets = [("75", "−75%"), ("90", "−90%"), ("100", "net-zero")]
    order = ["gas_boiler", "oil_boiler", "biomass_boiler", "resistance_heater",
             "district_heat", "h2_boiler", "hp_ground", "hp_air"]
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    x = np.arange(len(targets)); bottoms = np.zeros(len(targets))
    for t in order:
        vals = []
        for key, _ in targets:
            df = pd.read_csv(RESULTS / f"mc_summary_COST_OPT_{key}.csv")
            ts = df[(df.variable == "tech_share") & (df.year == 2050) & (df.tech == t)]
            vals.append(ts["q50"].sum() * 100)
        vals = np.array(vals)
        ax.bar(x, vals, bottom=bottoms, color=TECH_COLORS[t], width=0.6,
               label=TECH_SHORT[t], zorder=3)
        bottoms += vals
    ax.set_xticks(x); ax.set_xticklabels([l for _, l in targets])
    ax.set_ylim(0, 100); ax.set_ylabel("Share of EU useful heat, 2050 (%)")
    ax.set_xlabel("2050 emissions ambition")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8.5)
    _title(ax, "EU cost-optimal 2050 mix across ambition levels")
    _save(fig, "fig27_costopt_eu_mix_targets.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig28_heatmix_crosscheck():
    from build_heating_mix_2025 import D
    rows = []
    for c, (eu, nat, *_rest) in D.items():
        l1 = sum(abs(eu[t] - nat[t]) for t in TECHS)
        rows.append((c, l1))
    rows.sort(key=lambda r: r[1])
    cc = [r[0] for r in rows]; l1 = [r[1] for r in rows]
    fig, ax = plt.subplots(figsize=(7.4, 7.0))
    y = np.arange(len(cc))
    colors = [COST_OPT_BIND if v > 0.30 else WONG_PALETTE["blue"] for v in l1]
    ax.barh(y, l1, color=colors, height=0.7, zorder=3)
    ax.axvline(0.30, color=C_MUTED, linestyle=":", linewidth=1.0)
    ax.set_yticks(y); ax.set_yticklabels(cc, fontsize=8)
    ax.set_xlabel("Eurostat-vs-national mix divergence (L1 distance)")
    _title(ax, "Heating-mix cross-check: energy vs dwelling basis")
    ax.text(0.0, -0.06, "Red = >0.30 divergence (flagged); dotted line = threshold. The two "
            "bases bracket the useful-heat mix; the model uses their mean.",
            transform=ax.transAxes, fontsize=7.5, color=C_MUTED)
    _save(fig, "fig28_heatmix_crosscheck.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig29_lcoh_country_tech():
    hm = load_heating_mix_2025()
    countries = sorted(hm.keys())
    techs = ["gas_boiler", "oil_boiler", "biomass_boiler", "resistance_heater",
             "hp_air", "hp_ground", "district_heat", "h2_boiler"]
    M = np.array([[compute_lcoh(t, c, 2030, carbon_price_scenario="CENTRAL")
                   for t in techs] for c in countries])
    fig, ax = plt.subplots(figsize=(8.2, 8.4))
    im = ax.imshow(M, aspect="auto", cmap="RdYlGn_r", vmin=40, vmax=300)
    ax.set_xticks(np.arange(len(techs)))
    ax.set_xticklabels([TECH_SHORT[t] for t in techs], rotation=40, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(countries)))
    ax.set_yticklabels(countries, fontsize=7.5)
    for i in range(len(countries)):
        for j in range(len(techs)):
            ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=5.5,
                    color="#222222")
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
    cb.set_label("LCOH 2030 (EUR/MWh useful, CENTRAL carbon)")
    _title(ax, "LCOH by country and technology (2030, audited costs)")
    _save(fig, "fig29_lcoh_country_tech.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig30_abatement_supply():
    from Optimisation import prepare_data
    data = prepare_data(demand="bottomup")
    base = data["base_s1_c"]  # tCO2 per country
    sp = pd.read_csv(RESULTS / "cost_opt_shadow_prices.csv")
    d = sp[(sp.variant == "COST_OPT_90") & (sp.year == 2050)]
    sh = dict(zip(d.country, d.shadow_eur_tco2))
    rows = [(c, base.get(c, 0) / 1e6, max(sh.get(c, 0.0), 0.0)) for c in base]
    rows.sort(key=lambda r: r[2])  # by marginal (implied carbon) price
    cum = 0.0
    xs, ys = [0.0], [0.0]
    for c, mt, price in rows:
        xs += [cum, cum + mt]; ys += [price, price]
        cum += mt
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.step(xs, ys, where="post", color=WONG_PALETTE["blue"], linewidth=2.0)
    ax.fill_between(xs, ys, step="post", color=WONG_PALETTE["blue"], alpha=0.12)
    ax.set_xlabel("Cumulative 2025 scope-1 baseline emissions (MtCO₂)")
    ax.set_ylabel("Implied carbon price for −90% (EUR/tCO₂)")
    _title(ax, "Abatement supply curve: cost to reach −90% by country")
    ax.text(0.0, -0.13, "Countries ordered by the carbon price they need; most decarbonise at "
            "€0 (cost-optimal), only HR/RO/HU require a positive price.",
            transform=ax.transAxes, fontsize=7.5, color=C_MUTED)
    _save(fig, "fig30_abatement_supply.pdf")


# ─────────────────────────────────────────────────────────────────────────────
def fig31_hp_share_scenarios():
    scen = [("STATED_POLICIES", "Reference"), ("NET_ZERO", "High-elec"),
            ("H2_PUSH", "H2-hybrid"), ("COST_OPT_90", "Cost-opt −90%")]
    data = {s: _country_tech_2050(s) for s, _ in scen}
    countries = sorted(data["STATED_POLICIES"].keys()) if data["STATED_POLICIES"] else \
        sorted(load_heating_mix_2025().keys())
    M = np.array([[ (data[s].get(c, {}).get("hp_air", 0) +
                     data[s].get(c, {}).get("hp_ground", 0)) * 100
                   for s, _ in scen] for c in countries])
    fig, ax = plt.subplots(figsize=(5.6, 8.4))
    im = ax.imshow(M, aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
    ax.set_xticks(np.arange(len(scen)))
    ax.set_xticklabels([l for _, l in scen], rotation=30, ha="right", fontsize=8.5)
    ax.set_yticks(np.arange(len(countries)))
    ax.set_yticklabels(countries, fontsize=7.5)
    for i in range(len(countries)):
        for j in range(len(scen)):
            ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=6,
                    color="#222222" if M[i, j] < 60 else "white")
    cb = fig.colorbar(im, ax=ax, shrink=0.5, pad=0.03)
    cb.set_label("2050 heat-pump share (%)")
    _title(ax, "2050 heat-pump share by country and scenario")
    _save(fig, "fig31_hp_share_scenarios.pdf")


ALL = {
    "fig22": fig22_costopt_country_map, "fig23": fig23_costopt_pathway,
    "fig24": fig24_implied_carbon_price, "fig25": fig25_heating_mix_2025,
    "fig26": fig26_cost_of_ambition, "fig27": fig27_costopt_eu_mix_targets,
    "fig28": fig28_heatmix_crosscheck, "fig29": fig29_lcoh_country_tech,
    "fig30": fig30_abatement_supply, "fig31": fig31_hp_share_scenarios,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()
    names = args.only or list(ALL)
    print("Generating Paper v4 figures...")
    for n in names:
        fn = ALL.get(n)
        if fn is None:
            print(f"  [skip] unknown figure {n}")
            continue
        try:
            fn()
        except Exception as e:
            print(f"  [FAIL] {n}: {type(e).__name__}: {e}")
    print("Done.")


if __name__ == "__main__":
    main()
