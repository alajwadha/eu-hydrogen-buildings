"""Comprehensive academic figure suite (50+) for the working paper.

Generates a numbered suite (S01..) into paper/figs/suite/ from the result CSVs, applying
the repo figure house style (academic short titles, never-overlapping text via _figstyle).
Each figure is a small function; the registry at the bottom drives a try/except loop so a
single failure never aborts the suite, and a manifest (paper/figs/suite/MANIFEST.csv) lists
every figure with its title and source.

Run AFTER the model rebuild:  cd code && PYTHONPATH=. python -m scripts.figure_suite
Scenarios not yet on disk are skipped gracefully (so it can be smoke-tested mid-rebuild).
"""
from __future__ import annotations
import re
import numpy as np, pandas as pd
# numpy 2.0 removed np.trapz in favour of np.trapezoid; support both.
_trapz = getattr(np, "trapezoid", None) or np.trapz

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import compute_lcoh, LABOUR_COST_MULTIPLIER
from scripts._figstyle import set_style, short_scen, legend_below
set_style()

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "figs" / "suite"; OUT.mkdir(parents=True, exist_ok=True)
R = RESULTS_DIR

SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
SCEN_COLOR = {"CURRENT_POLICIES": "#7f7f7f", "STATED_POLICIES": "#1f77b4",
              "NET_ZERO": "#2ca02c", "H2_PUSH": "#d62728"}
TECH_ORDER = ["hp_air", "hp_ground", "district_heat", "biomass_boiler",
              "h2_boiler", "gas_boiler", "oil_boiler", "resistance_heater"]
TECH_LABEL = {"hp_air": "Heat pump (air)", "hp_ground": "Heat pump (ground)",
              "district_heat": "District heat", "biomass_boiler": "Biomass",
              "h2_boiler": "Hydrogen", "gas_boiler": "Gas", "oil_boiler": "Oil",
              "resistance_heater": "Resistance"}
TECH_COLOR = {"hp_air": "#08519c", "hp_ground": "#3182bd", "district_heat": "#e6550d",
              "biomass_boiler": "#31a354", "h2_boiler": "#6a51a3", "gas_boiler": "#969696",
              "oil_boiler": "#636363", "resistance_heater": "#fdae6b"}
CARR_COLOR = {"electricity": "#08519c", "gas": "#969696", "oil": "#636363",
              "district_heat": "#e6550d", "biomass": "#31a354", "hydrogen": "#6a51a3"}

_CACHE: dict = {}
_MANIFEST: list = []


def _csv(name):
    if name not in _CACHE:
        _CACHE[name] = pd.read_csv(R / name)
    return _CACHE[name]


def summ(sc):  return _csv(f"mc_summary_{sc}.csv")
def ctry(sc):  return _csv(f"mc_country_{sc}.csv")
def emis(sc):  return _csv(f"mc_emissions_{sc}.csv")
def have(sc):  return (R / f"mc_summary_{sc}.csv").exists()
def AV():      return [s for s in SCEN if have(s)]


def save(fig, num, title, source):
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:46].strip("_")
    name = f"S{num:02d}_{slug}"
    fig.savefig(OUT / f"{name}.png"); plt.close(fig)
    _MANIFEST.append({"fig": f"S{num:02d}", "title": title, "source": source, "file": name + ".png"})


# ── helpers ───────────────────────────────────────────────────────────────────
def barh_country(num, title, series, xlabel, source, colors=None, fmt="{:+.0f}", figsize=(7.4, 8.4)):
    s = series.dropna().sort_values()
    fig, ax = plt.subplots(figsize=figsize); y = np.arange(len(s))
    cols = colors(s.values) if callable(colors) else (colors or "#1f77b4")
    ax.barh(y, s.values, color=cols, height=0.76)
    ax.set_yticks(y); ax.set_yticklabels(s.index, fontsize=7.5)
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel(xlabel); ax.set_title(title)
    save(fig, num, title, source)


def _share_by_year(sc, var="tech_share"):
    d = summ(sc); d = d[d.variable == var]
    years = sorted(d.year.unique())
    techs = [t for t in TECH_ORDER if t in set(d.tech)]
    M = {t: [float(d[(d.year == y) & (d.tech == t)].q50.sum()) for y in years] for t in techs}
    # q50 shares are per-tech medians and need not sum to 1 (high-variance scenarios like
    # NET_ZERO over-sum ~8%); renormalise each year so the displayed mix is a proper 100% stack.
    for j in range(len(years)):
        tot = sum(M[t][j] for t in techs) or 1.0
        for t in techs:
            M[t][j] /= tot
    return years, techs, M


# ── A. demand ───────────────────────────────────────────────────────────────
def a_demand_trajectory(n):
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for sc in AV():
        d = summ(sc); t = d[(d.variable == "useful_heat_MWh") & (d.tech == "all")].sort_values("year")
        ax.plot(t.year, t.q50 / 1e6, "o-", color=SCEN_COLOR[sc], lw=2.2, label=short_scen(sc))
    ax.set_ylabel("Useful heat demand (TWh/yr)"); ax.set_xlabel("Year")
    ax.set_title("EU+UK+CH residential heat demand by scenario")
    legend_below(ax, ncol=4); save(fig, n, "Residential heat demand by scenario", "mc_summary")


def a_demand_reduction(n):
    red = {}
    for sc in AV():
        d = summ(sc); t = d[(d.variable == "useful_heat_MWh") & (d.tech == "all")].sort_values("year")
        v = t.q50.values; red[short_scen(sc)] = (v[-1] / v[0] - 1) * 100
    s = pd.Series(red)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar(s.index, s.values, color=[SCEN_COLOR[k] for k in AV()])
    for i, v in enumerate(s.values): ax.text(i, v - 1.5, f"{v:.0f}%", ha="center", color="white", fontweight="bold")
    ax.set_ylabel("Demand change 2025→2050 (%)"); ax.set_title("Heat-demand reduction by scenario")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right"); save(fig, n, "Heat-demand reduction by scenario", "mc_summary")


def a_demand_by_country(n):
    sc = "STATED_POLICIES" if have("STATED_POLICIES") else AV()[0]
    d = ctry(sc); t = d[(d.variable == "useful_heat_TWh") & (d.tech == "all") & (d.year == 2050)]
    barh_country(n, f"2050 heat demand by country ({short_scen(sc)})",
                 t.set_index("country").q50, "Useful heat demand 2050 (TWh)", "mc_country",
                 colors="#1f77b4")


def a_lmdi_decomp(n):
    d = _csv("lmdi_decomposition.csv").copy()
    d = d.reindex(d.dlnQ_total.abs().sort_values().index).tail(14)
    parts = ["contrib_population", "contrib_occupancy_Dw_per_Pop", "contrib_dwelling_size", "contrib_intensity_per_m2"]
    labs = ["Population", "Occupancy", "Dwelling size", "Intensity/m²"]
    cols = ["#08519c", "#3182bd", "#e6550d", "#31a354"]
    fig, ax = plt.subplots(figsize=(7.8, 6.2)); y = np.arange(len(d))
    left_pos = np.zeros(len(d)); left_neg = np.zeros(len(d))
    for p, lab, c in zip(parts, labs, cols):
        vals = d[p].values * 100
        base = np.where(vals >= 0, left_pos, left_neg)
        ax.barh(y, vals, left=base, color=c, label=lab)
        left_pos = left_pos + np.where(vals >= 0, vals, 0); left_neg = left_neg + np.where(vals < 0, vals, 0)
    ax.set_yticks(y); ax.set_yticklabels(d.country, fontsize=8); ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel("Contribution to demand change (%)"); ax.set_title("LMDI decomposition of heat-demand change")
    legend_below(ax, ncol=4); save(fig, n, "LMDI decomposition of demand change", "lmdi_decomposition")


def a_cohort_vs_lmdi(n):
    d = _csv("cohort_forward.csv").dropna(subset=["cohort_2050_TWh", "lmdi_2050_TWh"])
    fig, ax = plt.subplots(figsize=(5.6, 5.4))
    ax.scatter(d.lmdi_2050_TWh, d.cohort_2050_TWh, color="#1f77b4", s=26)
    lim = max(d.lmdi_2050_TWh.max(), d.cohort_2050_TWh.max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="#999", lw=1)
    ax.set_xlabel("LMDI forward 2050 (TWh)"); ax.set_ylabel("Cohort-turnover 2050 (TWh)")
    ax.set_title("Forward-demand methods: cohort vs LMDI"); save(fig, n, "Cohort vs LMDI 2050 demand", "cohort_forward")


def a_climate_hdd(n):
    d = _csv("climate_hdd_sensitivity.csv")
    yrs = [2025, 2030, 2040, 2050]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    for _, r in d.iterrows():
        ax.plot(yrs, [r.twh_2025, r.twh_2030, r.twh_2040, r.twh_2050], "o-", lw=2, label=str(r.warming))
    ax.set_xlabel("Year"); ax.set_ylabel("Useful heat demand (TWh/yr)")
    ax.set_title("Heat demand under climate-warming HDD"); legend_below(ax, ncol=2)
    save(fig, n, "Climate-warming HDD demand sensitivity", "climate_hdd_sensitivity")


# ── B. technology mix ────────────────────────────────────────────────────────
def b_mix_area(n, sc):
    years, techs, M = _share_by_year(sc)
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.stackplot(years, [M[t] for t in techs], colors=[TECH_COLOR[t] for t in techs],
                 labels=[TECH_LABEL[t] for t in techs])
    ax.set_xlim(min(years), max(years)); ax.set_ylim(0, 1)
    ax.set_ylabel("Share of heat supply"); ax.set_title(f"Heating technology mix, {short_scen(sc)}")
    legend_below(ax, ncol=4); save(fig, n, f"Heating technology mix {short_scen(sc)}", "mc_summary")


def b_mix_2050_compare(n):
    av = AV(); fig, ax = plt.subplots(figsize=(7.8, 4.8))
    bottom = np.zeros(len(av))
    for t in TECH_ORDER:
        vals = []
        for sc in av:
            _, techs, M = _share_by_year(sc)
            vals.append(M[t][-1] if t in M else 0.0)
        vals = np.array(vals)
        ax.bar([short_scen(s) for s in av], vals * 100, bottom=bottom * 100, color=TECH_COLOR[t], label=TECH_LABEL[t])
        bottom = bottom + vals
    ax.set_ylabel("Share of heat supply, 2050 (%)"); ax.set_title("2050 heating mix across scenarios")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right"); legend_below(ax, ncol=4)
    save(fig, n, "2050 heating mix across scenarios", "mc_summary")


def b_share_by_country(n, tech, label):
    sc = "STATED_POLICIES" if have("STATED_POLICIES") else AV()[0]
    d = ctry(sc); t = d[(d.variable == "tech_share") & (d.tech == tech) & (d.year == 2050)]
    barh_country(n, f"2050 {label} share by country ({short_scen(sc)})",
                 t.set_index("country").q50 * 100, f"{label} share of heat, 2050 (%)", "mc_country",
                 colors=TECH_COLOR.get(tech, "#1f77b4"))


def b_mix_heatmap(n, techs, label, cmap):
    """2050 share of a tech group by country (rows) x scenario (cols). Variation down a
    column shows country-specificity within a scenario; across columns shows the scenario
    effect -- i.e. the EU-wide lever lands differently in each country."""
    M = {}
    for sc in AV():
        c = ctry(sc); d = c[(c.variable == "tech_share") & (c.year == 2050)]
        piv = d.pivot_table(index="country", columns="tech", values="q50", aggfunc="sum")
        rowtot = piv.sum(axis=1).replace(0, 1.0)   # renormalise per country (q50 need not sum to 1)
        M[short_scen(sc)] = sum((piv[t] if t in piv else 0) for t in techs) / rowtot
    df = (pd.DataFrame(M).fillna(0) * 100).sort_values(list(M)[-1])
    fig, ax = plt.subplots(figsize=(5.6, 9.2))
    im = ax.imshow(df.values, aspect="auto", cmap=cmap, vmin=0, vmax=max(60, df.values.max()))
    ax.set_xticks(range(len(df.columns))); ax.set_xticklabels(df.columns, rotation=20, ha="right", fontsize=8)
    ax.set_yticks(range(len(df.index))); ax.set_yticklabels(df.index, fontsize=7)
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            v = df.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=6.3,
                    color="white" if v > 45 else "#222")
    fig.colorbar(im, ax=ax, label=f"{label} share 2050 (%)", fraction=0.05, pad=0.02)
    ax.set_title(f"{label} share by country and scenario, 2050")
    save(fig, n, f"{label} share heatmap country x scenario", "mc_country")


def b_hp_trajectory(n):
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for sc in AV():
        years, _, M = _share_by_year(sc)
        hp = np.array(M.get("hp_air", [0]*len(years))) + np.array(M.get("hp_ground", [0]*len(years)))
        ax.plot(years, hp * 100, "o-", color=SCEN_COLOR[sc], lw=2.2, label=short_scen(sc))
    ax.set_ylabel("Heat-pump share (%)"); ax.set_xlabel("Year")
    ax.set_title("Heat-pump electrification by scenario"); legend_below(ax, ncol=4)
    save(fig, n, "Heat-pump electrification by scenario", "mc_summary")


# ── C. emissions ─────────────────────────────────────────────────────────────
def c_co2_trajectory(n):
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for sc in AV():
        e = emis(sc); t = e[(e.variable == "co2_MtCO2") & (e.tech == "all")].sort_values("year")
        ax.plot(t.year, t.q50, "o-", color=SCEN_COLOR[sc], lw=2.2, label=short_scen(sc))
        ax.fill_between(t.year, t.q10, t.q90, color=SCEN_COLOR[sc], alpha=0.10)
    ax.set_ylabel("Buildings CO₂ (Mt/yr)"); ax.set_xlabel("Year")
    ax.set_title("Residential heating CO₂ by scenario"); legend_below(ax, ncol=4)
    save(fig, n, "Residential heating CO2 by scenario", "mc_emissions")


def c_co2_intensity(n):
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    for sc in AV():
        e = emis(sc); t = e[(e.variable == "co2_intensity_gCO2_kWh") & (e.tech == "all")].sort_values("year")
        ax.plot(t.year, t.q50, "o-", color=SCEN_COLOR[sc], lw=2.2, label=short_scen(sc))
    ax.set_ylabel("CO₂ intensity (gCO₂/kWh useful)"); ax.set_xlabel("Year")
    ax.set_title("Carbon intensity of useful heat by scenario"); legend_below(ax, ncol=4)
    save(fig, n, "Carbon intensity of useful heat", "mc_emissions")


def c_co2_by_carrier(n):
    av = AV(); fig, ax = plt.subplots(figsize=(7.6, 4.6))
    carriers = ["gas", "oil", "electricity", "district_heat", "biomass", "hydrogen"]
    bottom = np.zeros(len(av))
    for car in carriers:
        vals = []
        for sc in av:
            e = emis(sc); r = e[(e.variable == "co2_by_carrier") & (e.tech == car) & (e.year == 2050)]
            vals.append(float(r.q50.sum()))
        vals = np.array(vals)
        if vals.sum() <= 0: continue
        ax.bar([short_scen(s) for s in av], vals, bottom=bottom, color=CARR_COLOR.get(car, "#888"), label=car)
        bottom = bottom + vals
    ax.set_ylabel("2050 CO₂ (Mt/yr)"); ax.set_title("2050 CO₂ by carrier across scenarios")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right"); legend_below(ax, ncol=3)
    save(fig, n, "2050 CO2 by carrier across scenarios", "mc_emissions")


def c_co2_by_country(n):
    sc = "STATED_POLICIES" if have("STATED_POLICIES") else AV()[0]
    e = emis(sc); t = e[(e.variable == "co2_by_country") & (e.year == 2050)]
    barh_country(n, f"2050 buildings CO₂ by country ({short_scen(sc)})",
                 t.set_index("tech").q50, "CO₂ 2050 (Mt/yr)", "mc_emissions", colors="#d62728")


def c_grid_frozen(n):
    d = _csv("grid_sensitivity.csv").sort_values("year")
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(d.year, d.co2_actual_Mt, "o-", color="#2ca02c", lw=2.2, label="decarbonising grid")
    ax.plot(d.year, d.co2_frozen_grid_Mt, "s--", color="#d62728", lw=2.2, label="grid frozen at 2025")
    ax.fill_between(d.year, d.co2_actual_Mt, d.co2_frozen_grid_Mt, color="#d62728", alpha=0.08)
    ax.set_ylabel("Buildings CO₂ (Mt/yr)"); ax.set_xlabel("Year")
    ax.set_title("Grid decarbonisation contribution to CO₂ cuts"); legend_below(ax, ncol=2)
    save(fig, n, "Grid decarbonisation contribution", "grid_sensitivity")


def c_cumulative_co2(n):
    av = AV(); yrs = [2025, 2030, 2040, 2050]; cum = {}
    for sc in av:
        e = emis(sc); t = e[(e.variable == "co2_MtCO2") & (e.tech == "all")].set_index("year").q50
        ser = [float(t.get(y, np.nan)) for y in yrs]
        cum[short_scen(sc)] = _trapz(ser, yrs)
    s = pd.Series(cum)
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar(s.index, s.values, color=[SCEN_COLOR[k] for k in av])
    ax.set_ylabel("Cumulative CO₂ 2025–2050 (Mt)"); ax.set_title("Cumulative heating CO₂ by scenario")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right"); save(fig, n, "Cumulative heating CO2 by scenario", "mc_emissions")


# ── D. costs / LCOH ──────────────────────────────────────────────────────────
def d_lcoh_by_tech(n):
    C = list(LABOUR_COST_MULTIPLIER)
    techs = [("gas_boiler", "Gas boiler"), ("oil_boiler", "Oil boiler"), ("h2_boiler", "Hydrogen boiler"),
             ("biomass_boiler", "Biomass"), ("hp_air", "HP air"), ("hp_ground", "HP ground")]
    def med(t, y): return float(np.median([compute_lcoh(t, c, y) for c in C]))
    v25 = [med(t, 2025) for t, _ in techs]; v50 = [med(t, 2050) for t, _ in techs]
    x = np.arange(len(techs)); w = 0.38
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.bar(x - w/2, v25, w, label="2025", color="#9ecae1"); ax.bar(x + w/2, v50, w, label="2050", color="#08519c")
    ax.set_xticks(x); ax.set_xticklabels([nm for _, nm in techs], rotation=15, ha="right")
    ax.set_ylabel("LCOH (€/MWh useful)"); ax.set_title("Levelised cost of heat by technology, EU median")
    legend_below(ax, ncol=2); save(fig, n, "LCOH by technology EU median", "Economics")


def d_lcoh_by_country(n):
    e = _csv("country_econ_table.csv").dropna(subset=["lcoh_bestHP_2050"]).sort_values("lcoh_bestHP_2050")
    y = np.arange(len(e)); h = 0.26
    fig, ax = plt.subplots(figsize=(8.0, 9.4))
    ax.barh(y + h, e.lcoh_H2_2050, h, color="#6a51a3", label="Hydrogen boiler")
    ax.barh(y, e.lcoh_gas_2050, h, color="#969696", label="Gas boiler")
    ax.barh(y - h, e.lcoh_bestHP_2050, h, color="#08519c", label="Best heat pump")
    ax.set_yticks(y); ax.set_yticklabels(e.country, fontsize=7.5); ax.invert_yaxis()
    ax.set_xlabel("LCOH, 2050 (€/MWh useful)"); ax.set_title("Levelised cost of heat by country, 2050")
    legend_below(ax, ncol=3); save(fig, n, "LCOH by country 2050", "country_econ_table")


def d_gap_by_country(n):
    e = _csv("country_econ_table.csv").dropna(subset=["h2_minus_hp_gap_2050"])
    barh_country(n, "Hydrogen-boiler minus heat-pump cost by country (2050)",
                 e.set_index("country").h2_minus_hp_gap_2050, "H₂ − HP LCOH, 2050 (€/MWh)",
                 "country_econ_table",
                 colors=lambda v: ["#2ca02c" if x <= 0 else ("#d62728" if x > 60 else "#ff7f0e") for x in v])


def d_wacc(n):
    e = _csv("country_econ_table.csv")
    barh_country(n, "Cost of capital (WACC) by country", e.set_index("country").wacc_pct,
                 "Real WACC (%)", "country_econ_table", colors="#7b3294")


def d_labour(n):
    e = _csv("country_econ_table.csv")
    barh_country(n, "Installation-labour cost multiplier by country", e.set_index("country").labour_mult,
                 "Labour cost multiplier (EU=1)", "country_econ_table", colors="#1b9e77")


def d_h2_price_kg(n):
    e = _csv("country_econ_table.csv").sort_values("h2_2050_eur_kg")
    y = np.arange(len(e)); h = 0.38
    fig, ax = plt.subplots(figsize=(7.6, 9.0))
    ax.barh(y + h/2, e.h2_2025_eur_kg, h, color="#fdae6b", label="2025")
    ax.barh(y - h/2, e.h2_2050_eur_kg, h, color="#d94701", label="2050")
    ax.set_yticks(y); ax.set_yticklabels(e.country, fontsize=7.5); ax.invert_yaxis()
    ax.set_xlabel("Delivered hydrogen price (€/kg)"); ax.set_title("Delivered hydrogen price by country")
    legend_below(ax, ncol=2); save(fig, n, "Delivered hydrogen price by country", "country_econ_table")


def d_price_scatter(n):
    e = _csv("country_econ_table.csv")
    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    ax.scatter(e.gas_2025_eur_mwh, e.elec_2025_eur_mwh, color="#1f77b4", s=26)
    for _, r in e.iterrows():
        ax.annotate(r.country, (r.gas_2025_eur_mwh, r.elec_2025_eur_mwh), fontsize=7, xytext=(3, 3),
                    textcoords="offset points", path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    ax.set_xlabel("Gas price 2025 (€/MWh)"); ax.set_ylabel("Electricity price 2025 (€/MWh)")
    ax.set_title("Residential gas vs electricity prices, 2025"); save(fig, n, "Gas vs electricity prices 2025", "country_econ_table")


# ── E. merit order / H2 peaking ──────────────────────────────────────────────
def e_winscount(n):
    mo = _csv("merit_order_heat.csv")
    s = mo.groupby("scenario").h2_wins_peak.sum().reindex(SCEN).dropna()
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar([short_scen(i) for i in s.index], s.values, color=[SCEN_COLOR[i] for i in s.index])
    for i, v in enumerate(s.values): ax.text(i, v + 0.1, f"{int(v)}/29", ha="center", fontweight="bold")
    ax.set_ylabel("Countries where H₂ wins the peak"); ax.set_title("Where hydrogen wins the heat peak, by scenario")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right"); save(fig, n, "Where hydrogen wins the peak", "merit_order_heat")


def e_peak_cost(n, sc):
    mo = _csv("merit_order_heat.csv"); d = mo[mo.scenario == sc].set_index("country")
    order = d.sort_values("h2_peaker_eur_mwh").index
    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(7.2, 9.0))
    ax.barh(y - 0.2, d.loc[order, "gas_peaker_eur_mwh"], 0.4, color="#969696", label="gas peaker")
    ax.barh(y + 0.2, d.loc[order, "h2_peaker_eur_mwh"], 0.4,
            color=["#2ca02c" if d.loc[c, "h2_wins_peak"] else "#6a51a3" for c in order],
            label="H₂ peaker (green = wins)")
    ax.set_yticks(y); ax.set_yticklabels(order, fontsize=7.5); ax.invert_yaxis()
    ax.set_xlabel("Marginal cost of peaking heat, 2050 (€/MWh)")
    ax.set_title(f"Marginal cost of peaking heat ({short_scen(sc)})")
    legend_below(ax, ncol=2); save(fig, n, f"Peaking heat marginal cost {short_scen(sc)}", "merit_order_heat")


def e_profit_recovery(n):
    p = _csv("merit_order_profit.csv"); w = p[p.wins_peak].copy()
    w["recovery"] = 100 * w.gross_margin_eur_kw_yr / w.ann_capex_eur_kw_yr
    g = w.groupby("scenario").recovery.mean().reindex([s for s in SCEN if s in set(w.scenario)])
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.bar([short_scen(i) for i in g.index], g.values, color=[SCEN_COLOR[i] for i in g.index])
    ax.axhline(100, color="#333", ls="--", lw=1, label="full CAPEX recovery")
    for i, v in enumerate(g.values): ax.text(i, v + 1, f"{v:.0f}%", ha="center", fontweight="bold")
    ax.set_ylabel("CAPEX recovered by rent (%)"); ax.set_title("H₂ peaker capital recovery (the 'missing money')")
    plt.setp(ax.get_xticklabels(), rotation=12, ha="right"); legend_below(ax, ncol=1)
    save(fig, n, "H2 peaker capital recovery", "merit_order_profit")


def e_storage_adder(n):
    mo = _csv("merit_order_heat.csv"); d = mo[mo.scenario == mo.scenario.iloc[0]].drop_duplicates("country")
    barh_country(n, "Seasonal hydrogen-storage cost adder by country",
                 d.set_index("country").h2_storage_adder, "Storage adder (€/MWh-heat)", "merit_order_heat",
                 colors=lambda v: ["#2ca02c" if x < 70 else "#d62728" for x in v])


def e_peak_ratio(n):
    lp = _csv("heat_load_profile.csv")
    barh_country(n, "Peak-to-average heat demand ratio by country",
                 lp.set_index("country").peak_over_avg, "Peak / average demand", "heat_load_profile",
                 colors="#e6550d")


def e_dh_stack(n, sc):
    d = _csv("merit_order_dh.csv"); d = d[d.scenario == sc].set_index("country")
    panel = [c for c in ["DE", "DK", "NL", "FR", "PL", "SE", "ES", "IT"] if c in d.index]
    order = ["waste", "large_hp", "biomass", "gas_chp", "h2"]
    lab = {"waste": "waste/excess", "large_hp": "large HP", "biomass": "biomass CHP", "gas_chp": "gas CHP", "h2": "H₂"}
    col = {"waste": "#8c8c8c", "large_hp": "#1f77b4", "biomass": "#2ca02c", "gas_chp": "#d62728", "h2": "#9467bd"}
    x = np.arange(len(panel)); w = 0.16
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    for i, k in enumerate(order):
        ax.bar(x + (i - 2) * w, [d.loc[c, f"mc_{k}"] for c in panel], w, color=col[k], label=lab[k])
    ax.set_xticks(x); ax.set_xticklabels(panel); ax.set_ylabel("Marginal cost (€/MWh-heat)")
    ax.set_title(f"District-heating supply merit order ({short_scen(sc)})")
    legend_below(ax, ncol=5, y=-0.16); save(fig, n, f"DH supply merit order {short_scen(sc)}", "merit_order_dh")


# ── F. H2 supply ─────────────────────────────────────────────────────────────
def f_delivered_cost(n):
    d = _csv("h2_delivered_cost.csv")
    routecol = {"green": "#2ca02c", "blue": "#1f77b4", "pink": "#e377c2", "pipe": "#ff7f0e", "ship": "#8c564b"}
    s = d.set_index("country").delivered_eur_mwh.sort_values()
    cols = [routecol.get(d.set_index("country").loc[c, "cheapest_route"], "#888") for c in s.index]
    fig, ax = plt.subplots(figsize=(7.4, 8.4)); y = np.arange(len(s))
    ax.barh(y, s.values, color=cols, height=0.76)
    ax.set_yticks(y); ax.set_yticklabels(s.index, fontsize=7.5)
    ax.set_xlabel("Delivered hydrogen cost, 2050 (€/MWh)"); ax.set_title("Delivered hydrogen cost by country and route")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in routecol.values()]
    ax.legend(handles, routecol.keys(), loc="lower right", frameon=False, fontsize=8, title="cheapest route")
    save(fig, n, "Delivered hydrogen cost by route", "h2_delivered_cost")


def f_routes(n):
    d = _csv("h2_delivered_cost.csv")
    routes = [("green", "Green (EU)"), ("blue", "Blue (CCS)"), ("pink", "Pink (nuclear)"),
              ("pipe", "Pipeline import"), ("ship", "Ship import")]
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    data = [d[r].dropna().values for r, _ in routes]
    bp = ax.boxplot(data, labels=[lab for _, lab in routes], patch_artist=True)
    for patch, c in zip(bp["boxes"], ["#2ca02c", "#1f77b4", "#e377c2", "#ff7f0e", "#8c564b"]): patch.set_facecolor(c)
    ax.set_ylabel("Hydrogen cost (€/kg)"); ax.set_title("Hydrogen supply cost by production/import route")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right"); save(fig, n, "Hydrogen cost by route", "h2_delivered_cost")


def f_infra_ladder(n):
    inf = _csv("h2_infra_scenario.csv")
    means = [("Free gas-grid\nreuse", inf.gap_baseline.mean(), "#9ecae1"),
             ("Retrofit grid", inf.gap_convert_central.mean(), "#fdae6b"),
             ("Blend", inf.gap_blend_central.mean(), "#fd8d3c"),
             ("New grid", inf.gap_newbuild_central.mean(), "#de2d26")]
    fig, ax = plt.subplots(figsize=(6.8, 4.4)); xs = np.arange(len(means))
    ax.bar(xs, [m[1] for m in means], color=[m[2] for m in means], width=0.62)
    for xi, m in zip(xs, means): ax.text(xi, m[1] + 0.6, f"€{m[1]:.0f}", ha="center", fontweight="bold", fontsize=9)
    ax.set_xticks(xs); ax.set_xticklabels([m[0] for m in means])
    ax.set_ylabel("EU-mean H₂ − HP gap, 2050 (€/MWh)"); ax.set_title("Hydrogen cost gap by delivery-infrastructure scenario")
    save(fig, n, "H2 cost gap by infrastructure scenario", "h2_infra_scenario")


def f_supply_range(n):
    d = _csv("h2_supply_scenario.csv").sort_values("gap_central")
    fig, ax = plt.subplots(figsize=(7.4, 8.4)); y = np.arange(len(d))
    ax.hlines(y, d.gap_low, d.gap_high, color="#bbb", lw=2)
    ax.scatter(d.gap_central, y, color="#d62728", s=20, zorder=3)
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(d.country, fontsize=7.5)
    ax.set_xlabel("H₂ − HP gap, 2050 (€/MWh): low–high range, central dot")
    ax.set_title("Hydrogen cost-gap uncertainty by country"); save(fig, n, "Hydrogen cost-gap range by country", "h2_supply_scenario")


def f_grid_readiness(n):
    e = _csv("country_econ_table.csv")
    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    ax.scatter(e.gas_grid_cov, e.h2_infra_readiness, color="#6a51a3", s=26)
    for _, r in e.iterrows():
        ax.annotate(r.country, (r.gas_grid_cov, r.h2_infra_readiness), fontsize=7, xytext=(3, 3),
                    textcoords="offset points", path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])
    ax.set_xlabel("Gas-grid household coverage"); ax.set_ylabel("H₂ infrastructure readiness")
    ax.set_title("Gas-grid coverage vs hydrogen-infrastructure readiness")
    save(fig, n, "Gas grid vs H2 infra readiness", "country_econ_table")


# ── G. validation ────────────────────────────────────────────────────────────
def g_hotmaps_bar(n):
    b = _csv("benchmark_multi.csv")
    barh_country(n, "Heat-demand validation: model vs Hotmaps by country",
                 b.set_index("country").gap_vs_hotmaps_pct, "Model − Hotmaps (% of Hotmaps)", "benchmark_multi",
                 colors=lambda v: ["#2ca02c" if abs(x) <= 15 else ("#ff7f0e" if abs(x) <= 25 else "#d62728") for x in v],
                 fmt="{:+.0f}%")


def g_scatter_11(n):
    b = _csv("benchmark_multi.csv")
    fig, ax = plt.subplots(figsize=(5.8, 5.6))
    ax.scatter(b.hotmaps_TWh, b.bottomup_TWh, color="#1f77b4", s=26)
    lim = max(b.hotmaps_TWh.max(), b.bottomup_TWh.max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="#999", lw=1)
    ax.set_xlabel("Hotmaps demand (TWh)"); ax.set_ylabel("Bottom-up model demand (TWh)")
    ax.set_title("Bottom-up model vs Hotmaps, 1:1"); save(fig, n, "Bottom-up vs Hotmaps scatter", "benchmark_multi")


def g_multi_benchmark(n):
    b = _csv("benchmark_multi.csv")
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    for col, lab, c in [("gap_vs_hotmaps_pct", "Hotmaps", "#1f77b4"),
                        ("gap_vs_bso_pct", "BSO", "#ff7f0e"), ("gap_vs_odyssee_pct", "Odyssée", "#2ca02c")]:
        ax.hist(b[col].dropna(), bins=np.arange(-40, 41, 8), alpha=0.5, color=c, label=lab)
    ax.axvline(0, color="#333", lw=1); ax.set_xlabel("Model − benchmark (%)"); ax.set_ylabel("Countries")
    ax.set_title("Demand-validation deviation across benchmarks"); legend_below(ax, ncol=3)
    save(fig, n, "Validation deviation across benchmarks", "benchmark_multi")


def g_backcast(n):
    d = _csv("lmdi_backcast.csv").dropna(subset=["hotmaps_2015_TWh", "model_2015_lmdi_corrected"])
    fig, ax = plt.subplots(figsize=(5.8, 5.6))
    ax.scatter(d.hotmaps_2015_TWh, d.model_2015_lmdi_corrected, color="#6a51a3", s=26)
    lim = max(d.hotmaps_2015_TWh.max(), d.model_2015_lmdi_corrected.max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="#999", lw=1)
    ax.set_xlabel("Hotmaps 2015 (TWh)"); ax.set_ylabel("Model LMDI back-cast 2015 (TWh)")
    ax.set_title("LMDI back-cast vs Hotmaps 2015"); save(fig, n, "LMDI backcast vs Hotmaps 2015", "lmdi_backcast")


# ── H. COST_OPT / sensitivity ────────────────────────────────────────────────
def h_costopt_mix(n):
    co = _csv("mc_summary_COST_OPT_90.csv")
    sh = {r.tech: r.q50 for _, r in co[(co.year == 2050) & (co.variable == "tech_share")].iterrows()}
    seg = [("Heat pump", sh.get("hp_air", 0) + sh.get("hp_ground", 0), "#08519c"),
           ("District heat", sh.get("district_heat", 0), "#e6550d"),
           ("Biomass", sh.get("biomass_boiler", 0), "#31a354"),
           ("Hydrogen", sh.get("h2_boiler", 0), "#6a51a3"),
           ("Fossil", sh.get("gas_boiler", 0) + sh.get("oil_boiler", 0), "#969696")]
    fig, ax = plt.subplots(figsize=(9.0, 2.6)); left = 0
    for lbl, val, c in seg:
        ax.barh(0, val * 100, left=left * 100, color=c, edgecolor="white")
        if val > 0.03: ax.text((left + val/2) * 100, 0, f"{lbl}\n{val*100:.0f}%", ha="center", va="center",
                               color="white", fontweight="bold", fontsize=9)
        left += val
    ax.set_xlim(0, 100); ax.set_ylim(-0.6, 0.5); ax.axis("off")
    ax.set_title("Cost-optimal 2050 heating mix (−90% scope-1 cap)")
    save(fig, n, "Cost-optimal 2050 heating mix", "mc_summary_COST_OPT_90")


def h_costopt_pathway(n):
    p = _csv("cost_opt_pathway.csv")
    p = p[(p.variant == "COST_OPT_90") & (p["mode"] == "trajectory")]
    g = p.groupby(["year", "tech"]).useful_heat_MWh.sum().reset_index()
    tot = g.groupby("year").useful_heat_MWh.transform("sum")
    g["share"] = g.useful_heat_MWh / tot
    years = sorted(g.year.unique()); techs = [t for t in TECH_ORDER if t in set(g.tech)]
    M = {t: [float(g[(g.year == y) & (g.tech == t)].share.sum()) for y in years] for t in techs}
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.stackplot(years, [M[t] for t in techs], colors=[TECH_COLOR[t] for t in techs],
                 labels=[TECH_LABEL[t] for t in techs])
    ax.set_xlim(min(years), max(years)); ax.set_ylim(0, 1)
    ax.set_ylabel("Share of heat supply"); ax.set_title("Cost-optimal heating-mix pathway (−90% scope-1)")
    legend_below(ax, ncol=4); save(fig, n, "Cost-optimal heating pathway", "cost_opt_pathway")


def h_shadow_price(n):
    sp = _csv("cost_opt_shadow_prices.csv")
    v = sp[(sp.year == 2050)]
    v = v[(v.variant == 90) | (v.variant == "90")] if len(v[(v.variant == 90) | (v.variant == "90")]) else v
    s = v.groupby("country").shadow_eur_tco2.mean()
    if s.abs().sum() == 0:
        fig, ax = plt.subplots(figsize=(6.4, 2.2)); ax.axis("off")
        ax.text(0.5, 0.5, "Cost-optimal implied carbon price ≈ €0/tCO₂\n(no binding caps under least cost)",
                ha="center", va="center", fontsize=12, fontweight="bold")
        ax.set_title("Cost-optimal implied carbon price"); save(fig, n, "Cost-optimal implied carbon price", "cost_opt_shadow_prices")
        return
    barh_country(n, "Cost-optimal implied carbon price by country (2050)", s, "Shadow price (€/tCO₂)",
                 "cost_opt_shadow_prices", colors="#7b3294")


def h_costopt_sweep(n):
    s = _csv("cost_opt_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(7.4, 4.2)); x = np.arange(len(s))
    ax.bar(x, s.pv_bn_eur_yr, color="#1f77b4")
    ax.set_xticks(x); ax.set_xticklabels(s.setting, rotation=20, ha="right", fontsize=7.5)
    ax.set_ylabel("System cost (bn €/yr)"); ax.set_title("Cost-optimal system cost across assumption settings")
    save(fig, n, "Cost-optimal system cost sweep", "cost_opt_sensitivity")


def h_rho(n):
    d = _csv("rho_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    for sc in d.scenario.unique():
        g = d[d.scenario == sc].sort_values("rho")
        ax.plot(g.rho, g.width, "o-", lw=2, label=short_scen(str(sc)))
    ax.set_xlabel("Price-correlation ρ"); ax.set_ylabel("CO₂ 10–90% band width (Mt)")
    ax.set_title("Output uncertainty vs price-correlation assumption"); legend_below(ax, ncol=3)
    save(fig, n, "Uncertainty vs price correlation", "rho_sensitivity")


def h_sobol(n):
    d = _csv("global_sensitivity.csv").sort_values("ST")
    y = np.arange(len(d)); h = 0.38
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.barh(y + h/2, d.ST, h, color="#08519c", label="total effect Sₜ")
    ax.barh(y - h/2, d.S1, h, color="#9ecae1", label="first order S₁")
    ax.set_yticks(y); ax.set_yticklabels(d.driver); ax.set_xlabel("Sobol sensitivity index")
    ax.set_title("Global sensitivity of CO₂ to input drivers"); legend_below(ax, ncol=2)
    save(fig, n, "Global Sobol sensitivity", "global_sensitivity")


def h_climate_bar(n):
    d = _csv("climate_hdd_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(6.6, 4.2)); x = np.arange(len(d))
    ax.bar(x, d.delta_2050_vs_nowarm_pct, color="#e6550d")
    ax.set_xticks(x); ax.set_xticklabels(d.warming.astype(str), rotation=18, ha="right", fontsize=8)
    ax.set_ylabel("2050 demand vs no-warming (%)"); ax.set_title("Climate-warming effect on 2050 heat demand")
    save(fig, n, "Climate warming effect on 2050 demand", "climate_hdd_sensitivity")


# ── registry ─────────────────────────────────────────────────────────────────
def build():
    for old in OUT.glob("*.png"):   # clean slate so disk always matches the manifest
        old.unlink()
    n = [13]  # suite numbering continues after F1-F13
    def nxt():
        n[0] += 1; return n[0]

    jobs = [
        lambda: a_demand_trajectory(nxt()), lambda: a_demand_reduction(nxt()),
        lambda: a_demand_by_country(nxt()), lambda: a_lmdi_decomp(nxt()),
        lambda: a_cohort_vs_lmdi(nxt()), lambda: a_climate_hdd(nxt()),
    ]
    for sc in SCEN:
        if have(sc): jobs.append(lambda sc=sc: b_mix_area(nxt(), sc))
    jobs += [
        lambda: b_mix_2050_compare(nxt()),
        lambda: b_share_by_country(nxt(), "hp_air", "Air heat-pump"),
        lambda: b_share_by_country(nxt(), "district_heat", "District-heat"),
        lambda: b_share_by_country(nxt(), "h2_boiler", "Hydrogen"),
        lambda: b_hp_trajectory(nxt()),
        lambda: b_mix_heatmap(nxt(), ["hp_air", "hp_ground"], "Heat-pump", "Blues"),
        lambda: b_mix_heatmap(nxt(), ["gas_boiler", "oil_boiler"], "Fossil", "Reds"),
        lambda: c_co2_trajectory(nxt()), lambda: c_co2_intensity(nxt()),
        lambda: c_co2_by_carrier(nxt()), lambda: c_co2_by_country(nxt()),
        lambda: c_grid_frozen(nxt()), lambda: c_cumulative_co2(nxt()),
        lambda: d_lcoh_by_tech(nxt()), lambda: d_lcoh_by_country(nxt()),
        lambda: d_gap_by_country(nxt()), lambda: d_wacc(nxt()), lambda: d_labour(nxt()),
        lambda: d_h2_price_kg(nxt()), lambda: d_price_scatter(nxt()),
        lambda: e_winscount(nxt()),
    ]
    for sc in ["STATED_POLICIES", "NET_ZERO", "H2_PUSH"]:
        if have(sc) or True: jobs.append(lambda sc=sc: e_peak_cost(nxt(), sc))
    jobs += [
        lambda: e_profit_recovery(nxt()), lambda: e_storage_adder(nxt()), lambda: e_peak_ratio(nxt()),
        lambda: e_dh_stack(nxt(), "NET_ZERO"), lambda: e_dh_stack(nxt(), "H2_PUSH"),
        lambda: f_delivered_cost(nxt()), lambda: f_routes(nxt()), lambda: f_infra_ladder(nxt()),
        lambda: f_supply_range(nxt()), lambda: f_grid_readiness(nxt()),
        lambda: g_hotmaps_bar(nxt()), lambda: g_scatter_11(nxt()), lambda: g_multi_benchmark(nxt()),
        lambda: g_backcast(nxt()),
        lambda: h_costopt_mix(nxt()), lambda: h_costopt_pathway(nxt()), lambda: h_shadow_price(nxt()),
        lambda: h_costopt_sweep(nxt()), lambda: h_rho(nxt()), lambda: h_sobol(nxt()),
        lambda: h_climate_bar(nxt()),
    ]

    ok = fail = 0
    for j in jobs:
        try:
            j(); ok += 1
        except Exception as ex:
            fail += 1; print(f"  [FAIL] {ex}")
    pd.DataFrame(_MANIFEST).to_csv(OUT / "MANIFEST.csv", index=False)
    print(f"\nfigure_suite: {ok} figures written to paper/figs/suite/ ({fail} failed). "
          f"Scenarios on disk: {', '.join(AV())}")
    print("Manifest: paper/figs/suite/MANIFEST.csv")


if __name__ == "__main__":
    build()
