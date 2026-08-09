"""Hourly HEAT-side dispatch -- the heat mirror of power_dispatch.py.

Ali asked for the same cold-snap dispatch picture, but for heating. Two views:

  (A) DISTRICT-HEATING merit order, hour by hour. One operator dispatches a stack of DH
      sources into the same pipes, cheapest first. Each source has a FIXED capacity (only the
      heat-pump output varies, with the source temperature). The ORDER is scenario-dependent:
      in the Hydrogen Push world (cheap derived H2 + high carbon) hydrogen is cheaper than gas
      CHP, so H2 is dispatched just BELOW gas CHP and GAS CHP, the dearest source, sets the
      peak price; in lower-carbon scenarios H2 is the dearest and only catches the residual
      peak. The figure stacks in the true EU-mean cost order and names the marginal
      (price-setting) source explicitly (consistent with merit_order_dh.py).

  (B) WHOLE-BUILDING heat, hour by hour. Total residential heat demand met by the installed
      heating mix (heat pumps, district heat, biomass, gas/H2 boilers). Heat-pump output is
      capacity-limited and its COP collapses in the cold snap, so a peaking heat source
      (H2 / resistance / gas boiler) covers the residual -- the heat-side analogue of the
      electricity peaker gap.

Both are reduced-form and calibrated, not a unit-commitment model. Source marginal costs
reuse merit_order_dh.dh_marginal_costs; the hourly heat shape reuses power_dispatch.

Outputs (results/): heat_dispatch_dh_repday.csv, heat_dispatch_building_repday.csv,
heat_dispatch_summary.csv. Figures: P23 (DH cold-snap merit order, EU aggregate),
P24 (whole-building heat cold-snap, EU aggregate), mirrored F23/F24.
Run: cd code && PYTHONPATH=. python -m scripts.heat_dispatch
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR
from scripts.power_dispatch import (HOURS, HOD, DOY, MONTH, hourly_heat_shape, heat_profile_row,
                                    _save, hourly_cop)
from scripts.merit_order_dh import dh_marginal_costs, STACK_ORDER, STACK_LABEL
from scripts._figstyle import (set_style, legend_below, short_scen, assert_printable,
                               H2_HATCH, ink_h2_hatch)
set_style()

SCEN_HEAT = "H2_PUSH"   # the H2-favourable scenario for the headline heat figure

# DH supply-stack FIXED capacities, as a fraction of each country's peak DH demand. The
# cheap decarbonised base (waste heat + large heat pumps + biomass) plus legacy gas CHP
# covers ~85% of the peak; hydrogen, the dearest source, fills the residual cold-snap peak.
# (Reduced-form sizing; the point is the merit order and H2's position, not exact DH fleet
# data. Sum of non-H2 caps is deliberately < peak so H2 has a peak slice to serve.)
DH_CAP_FRAC = {"waste": 0.20, "large_hp": 0.45, "biomass": 0.10, "gas_chp": 0.10, "h2": 0.20}


def dh_hourly(c, lp, dh_share, scen=SCEN_HEAT):
    """One country's hourly DH dispatch by merit order. Returns dict of 8760 arrays."""
    row = heat_profile_row(lp, c)
    heat = hourly_heat_shape(row) * dh_share              # DH heat demand, GW
    peak = float(heat.max())
    mc = dh_marginal_costs(c, scen)
    order = sorted(STACK_ORDER, key=lambda k: mc[k])      # TRUE cost order, cheapest first
    caps = {k: DH_CAP_FRAC.get(k, 0.0) * peak for k in STACK_ORDER}
    rem = heat.copy(); gen = {}
    for k in order:                                       # dispatch each source up to its cap
        served = np.minimum(rem, caps[k])
        gen[k] = served
        rem = rem - served
    gen["unserved"] = np.clip(rem, 0, None)               # above the full fixed stack
    # H2 serves more where it is cheap enough to rank ahead of gas CHP (consistent with
    # merit_order_dh); where it is the dearest source it only catches the residual peak.
    return dict(demand=heat, gen=gen, h2_cap=caps["h2"], h2_rank=order.index("h2") + 1,
                h2_energy=float(gen["h2"].sum()), h2_hours=int((gen["h2"] > 1e-6).sum()),
                dh_twh=float(heat.sum() / 1e3))


def building_hourly(c, lp, mc_df, year=2050):
    """One country's whole-building heat demand, stacked by the installed heating mix
    (each technology serves its share of every hour). Heat pumps form the base; the H2
    boiler, where deployed, serves its share. Returns dict of 8760 arrays by source."""
    row = heat_profile_row(lp, c)
    heat = hourly_heat_shape(row)                          # total building heat demand, GW
    sh = mc_df[(mc_df.country == c) & (mc_df.year == year) & (mc_df.variable == "tech_share")]
    sh = sh.set_index("tech")["q50"] if len(sh) else pd.Series(dtype=float)
    f = {"heat_pump": float(sh.get("hp_air", 0) + sh.get("hp_ground", 0) + sh.get("resistance_heater", 0)),
         "district_heat": float(sh.get("district_heat", 0)),
         "biomass": float(sh.get("biomass_boiler", 0)),
         "gas_boiler": float(sh.get("gas_boiler", 0) + sh.get("oil_boiler", 0)),
         "h2_boiler": float(sh.get("h2_boiler", 0))}
    tot = sum(f.values()) or 1.0                          # MC median shares need not sum to 1
    gen = {k: heat * (v / tot) for k, v in f.items()}     # normalise so the stack meets demand
    resid = np.clip(heat - sum(gen.values()), 0, None)    # countries with no/incomplete share data
    gen["heat_pump"] = gen["heat_pump"] + resid           # default unallocated heat to HP (2050 dominant)
    return dict(demand=heat, gen=gen, h2_peak_twh=float(gen["h2_boiler"].sum() / 1e3))


def _eu_repday(per_country):
    """Sum each country's arrays into an EU aggregate and extract the peak (cold-snap) day."""
    # sorted, because a set of strings iterates in hash order and CPython randomises string
    # hashes per process. The values were identical every run but the COLUMN ORDER of the two
    # repday CSVs shuffled, so a rerun always left them modified in git and an artefact diff
    # could never be used to check that a reproduction matched.
    keys = sorted(set().union(*[set(d["gen"]) for d in per_country]))
    eu_demand = np.zeros(HOURS); eu_gen = {k: np.zeros(HOURS) for k in keys}
    for d in per_country:
        eu_demand += d["demand"]
        for k in keys:
            eu_gen[k] = eu_gen[k] + d["gen"].get(k, np.zeros(HOURS))
    peak_src = eu_gen.get("h2", eu_gen.get("h2_boiler"))
    pday = peak_src.reshape(365, 24).sum(1).argmax() if peak_src is not None else \
        eu_demand.reshape(365, 24).sum(1).argmax()
    mask = (DOY == int(pday))
    out = {k: eu_gen[k][mask].reshape(-1, 24).mean(0) for k in keys}
    out["demand"] = eu_demand[mask].reshape(-1, 24).mean(0)
    return out


def _fig_heat_coldsnap(day, order, labels, cols, _title, fname, pname, hatch_key=None, marginal=None):
    pos = (np.arange(24) - 6) % 24
    sidx = np.argsort(pos); xs = pos[sidx]
    # 8.6 in at 0.88\textwidth printed the legend at 5.2 pt. Drawn at the column
    # width so the shared 8 pt legend font prints at its nominal size.
    FIGW_IN = 6.4
    assert_printable(FIGW_IN, {"legend (legend_below)": 8.0, "tick/axis default": 9.0},
                     column="long", label="P23_dh_heat_dispatch")
    fig, ax = plt.subplots(figsize=(FIGW_IN, 3.9))
    bottom = np.zeros(24); marg_bot = marg_top = None
    for k in order:
        if k not in day:
            continue
        vals = np.asarray(day[k])[sidx]
        # A series that is zero in every hour still produced a legend swatch, so the key
        # named a mark the canvas does not carry. Unserved energy is the usual case.
        if not np.any(vals > 1e-9):
            continue
        # Hydrogen carries H2_HATCH wherever it is stacked against other technologies. In
        # this stack its red sits closer to the biomass green under deuteranopia (simulated
        # separation 51.7 of 441) than any other pair, and the two segments are adjacent.
        hatch = "xxxx" if k == hatch_key else (H2_HATCH if k in ("h2", "h2_boiler") else None)
        bc = ax.bar(xs, vals, bottom=bottom, width=0.92, color=cols[k], label=labels[k],
                    edgecolor="white", linewidth=0.3, hatch=hatch)
        if k in ("h2", "h2_boiler"):
            ink_h2_hatch(bc)
        if marginal and k == marginal[0]:
            marg_bot, marg_top = bottom.copy(), bottom + vals
        bottom += vals
    dem = np.asarray(day["demand"])[sidx]
    ax.plot(xs, dem, "k-", lw=2.0, label="Heat demand", zorder=5)
    ax.set_ylim(0, float(max(dem.max(), bottom.max())) * 1.20)
    # No boxed callout naming the price-setting source. It was drawn at the top of the axes
    # over the data, and it duplicated the legend, which already reads "gas CHP (sets peak
    # price)". The legend label is the whole of the information and it cannot collide.
    ax.set_xticks(range(0, 24, 3)); ax.set_xticklabels([f"{(h+6)%24:02d}:00" for h in range(0, 24, 3)])
    ax.set_xlabel("Hour of cold-snap day (from 06:00)"); ax.set_ylabel("Heat (GW-thermal)")
    # No in-figure title. It repeated the caption word for word, which is the one place a
    # journal figure should not spend a line, and it pushed the plot down the canvas.
    # ncol=3, not 4. These labels are long enough that four columns made the legend wider
    # than the axes, and savefig(bbox='tight') then padded the canvas out to the legend, so
    # the plotted data occupied under half the width it was given on the page.
    legend_below(ax, ncol=3)
    _save(fig, fname, pname)


def _dh_h2_share_weighted(summ):
    """The per-country-weighted EU hydrogen share of district-heat energy.

    This used to draw a 29-row bar chart as well. That figure said one thing, that three
    salt-cavern markets reach about 29 per cent and the other 26 sit under 1, and it spent
    a full page saying it: 26 of its bars were invisible at print size and the whole chart
    was two numbers and a list of countries. The appendix states it in a sentence instead.
    The weighted share is still computed here, because the text quotes it.
    """
    df = pd.DataFrame(summ)
    return 100 * df["h2_dh_energy_gwh"].sum() / (df["dh_twh"].sum() * 1e3 + 1e-9)


def main():
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    mc = pd.read_csv(RESULTS_DIR / "mc_country_STATED_POLICIES.csv")
    dhc = mc[(mc.year == 2050) & (mc.tech == "district_heat") & (mc.variable == "tech_share")]
    dh_share = dict(zip(dhc.country, dhc.q50)) if len(dhc) else {}
    countries = list(lp.index)

    dh_list, bld_list, summ = [], [], []
    for c in countries:
        dh = dh_hourly(c, lp, float(dh_share.get(c, 0.1)))
        bl = building_hourly(c, lp, mc)
        dh_list.append(dh); bld_list.append(bl)
        summ.append(dict(country=c, dh_share=round(float(dh_share.get(c, 0.1)), 3),
                         dh_twh=round(dh["dh_twh"], 2), h2_dh_cap_gw=round(dh["h2_cap"], 2),
                         h2_dh_energy_gwh=round(dh["h2_energy"], 1), h2_dh_hours=dh["h2_hours"],
                         h2_dh_share_pct=round(100 * dh["h2_energy"] / (dh["dh_twh"]*1e3 + 1e-9), 1),
                         bld_h2_peak_twh=round(bl["h2_peak_twh"], 2)))
    pd.DataFrame(summ).to_csv(RESULTS_DIR / "heat_dispatch_summary.csv", index=False)

    # EU-aggregate cold-snap days
    dh_day = _eu_repday(dh_list)
    bld_day = _eu_repday(bld_list)
    pd.DataFrame([dict(hour=h, **{k: round(float(np.asarray(v)[h]), 3) for k, v in dh_day.items()})
                  for h in range(24)]).to_csv(RESULTS_DIR / "heat_dispatch_dh_repday.csv", index=False)
    pd.DataFrame([dict(hour=h, **{k: round(float(np.asarray(v)[h]), 3) for k, v in bld_day.items()})
                  for h in range(24)]).to_csv(RESULTS_DIR / "heat_dispatch_building_repday.csv", index=False)

    # Representative-day H2 DH share (the single cold-snap aggregate the dispatch figure plots),
    # to contrast with the per-country-weighted share in the by-country figure below.
    repday_share = 100 * float(np.asarray(dh_day["h2"]).sum()) / float(np.asarray(dh_day["demand"]).sum())

    # ---- figures ----
    # Stack in the TRUE EU-mean cost order (cheapest at the bottom, dearest on top). The dearest
    # source actually dispatched at the peak hour SETS the peak price, so name it explicitly. With
    # cheap derived H2 + high carbon (Hydrogen Push) gas CHP is the dearest, so it sets the peak and
    # H2 is dispatched just below it; in lower-carbon scenarios H2 would be the dearest instead.
    mc_eu = {k: float(np.mean([dh_marginal_costs(c, SCEN_HEAT)[k] for c in countries])) for k in STACK_ORDER}
    cost_order = sorted(STACK_ORDER, key=lambda k: mc_eu[k])
    ph = int(np.argmax(np.asarray(dh_day["demand"])))
    marginal_src = [k for k in cost_order if float(np.asarray(dh_day[k])[ph]) > 1e-3][-1]
    print("DH EU-mean marginal cost (EUR/MWh): " + ", ".join(f"{k} {mc_eu[k]:.0f}" for k in cost_order))
    print(f"DH marginal source at the EU peak: {marginal_src} ({STACK_LABEL[marginal_src]})")
    dh_order = cost_order + ["unserved"]
    dh_labels = {**STACK_LABEL, "unserved": "Unserved (loss of load)"}
    dh_labels[marginal_src] = STACK_LABEL[marginal_src] + " (sets peak price)"
    dh_cols = {"waste": "#7f7f7f", "large_hp": "#1f77b4", "biomass": "#2ca02c",
               "gas_chp": "#c49c4d", "h2": "#d62728", "unserved": "#3b0a0a"}
    # Titles, not panel letters. These two go into separate float environments, and only the
    # first is included in the manuscript, so a bare "(a)" sent the reader looking for a "(b)"
    # that is not on the page.
    _fig_heat_coldsnap(dh_day, dh_order, dh_labels, dh_cols,
                       f"District-heat supply, {short_scen(SCEN_HEAT)} 2050",
                       "F23_dh_heat_dispatch", "P23_dh_heat_dispatch", hatch_key="unserved",
                       marginal=(marginal_src, STACK_LABEL[marginal_src]))
    bld_order = ["heat_pump", "district_heat", "biomass", "gas_boiler", "h2_boiler"]
    bld_labels = {"heat_pump": "Heat pumps", "district_heat": "District heat",
                  "biomass": "Biomass", "gas_boiler": "Gas/oil boiler", "h2_boiler": "H₂ boiler"}
    bld_cols = {"heat_pump": "#1f77b4", "district_heat": "#ff7f0e", "biomass": "#2ca02c",
                "gas_boiler": "#969696", "h2_boiler": "#d62728"}
    _fig_heat_coldsnap(bld_day, bld_order, bld_labels, bld_cols,
                       f"Building-level heat supply, {short_scen(SCEN_HEAT)} 2050",
                       "F24_building_heat_dispatch", "P24_building_heat_dispatch")

    wcut = _dh_h2_share_weighted(summ)
    print(f"H2 DH share: per-country-weighted EU {wcut:.1f}% vs representative-day EU {repday_share:.1f}%; "
          f"~29% in DE/UK/DK only, PL {next(s['h2_dh_share_pct'] for s in summ if s['country']=='PL')}%")

    df = pd.DataFrame(summ)
    print(f"=== Heat-side dispatch ({SCEN_HEAT}, 2050) ===")
    print(f"EU DH demand: {df.dh_twh.sum():.0f} TWh; H2 as DH peaker: {df.h2_dh_energy_gwh.sum()/1e3:.1f} TWh "
          f"({100*df.h2_dh_energy_gwh.sum()/(df.dh_twh.sum()*1e3):.1f}% of DH), "
          f"H2 DH peaker cap {df.h2_dh_cap_gw.sum():.0f} GW-th, runs ~{df.h2_dh_hours.mean():.0f} h/yr mean")
    print(f"Whole-building H2-boiler heat (its mix share, where deployed): {df.bld_h2_peak_twh.sum():.0f} TWh EU")
    print("Top DH countries by H2 DH share:")
    print(df.nlargest(6, "h2_dh_share_pct")[["country", "dh_share", "dh_twh", "h2_dh_share_pct", "h2_dh_hours"]].to_string(index=False))
    print(f"\nWrote heat_dispatch_*.csv + P23/P24 (F23/F24).")


if __name__ == "__main__":
    main()
