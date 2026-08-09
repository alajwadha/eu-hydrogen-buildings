"""Idempotent updater: inject a dated, data-driven 'country-specific model update'
section into every countries/<Name>/README.md, between HTML markers so re-runs replace
rather than duplicate. Sources: corrected Economics.compute_lcoh, the per-country
heating_mix_2025.csv, and the per-country COST_OPT_90 results. Temporary; delete after."""
import sys, re, glob, os
sys.path.insert(0, "code")
import pandas as pd
from src.Economics import (compute_lcoh, H2_MULT_BY_COUNTRY,
                          H2_MULT_RANGE_BY_COUNTRY)
from src.Config import load_heating_mix_2025

START = "<!-- COUNTRY_MODEL_UPDATE -->"
END = "<!-- /COUNTRY_MODEL_UPDATE -->"
DATE = "2026-06-12"
SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
SCEN_SHORT = {"CURRENT_POLICIES": "Current Policies", "STATED_POLICIES": "Stated Policies",
              "NET_ZERO": "Net Zero", "H2_PUSH": "H2 Push"}
HMIX = load_heating_mix_2025()
co = pd.read_csv("code/results/mc_country_COST_OPT_90.csv")
sp = pd.read_csv("code/results/cost_opt_shadow_prices.csv")
MC = {s: pd.read_csv(f"code/results/mc_country_{s}.csv") for s in SCEN}
MO = _mo = pd.read_csv("code/results/merit_order_heat.csv")
MP = pd.read_csv("code/results/merit_order_profit.csv")
MD = pd.read_csv("code/results/merit_order_dh.csv")
IB = pd.read_csv("code/results/infrastructure_bill.csv")


def _read_indexed(path):
    try:
        return pd.read_csv(path).set_index("country")
    except Exception:
        return None


H2SUP = _read_indexed("code/results/h2_supply_scenario.csv")
H2INF = _read_indexed("code/results/h2_infra_scenario.csv")


def h2_regime(m):
    if m <= 0.95:
        return "renewable-rich domestic production"
    if m >= 1.20:
        return "isolated island, ship-import only (not on the EHB)"
    return "European Hydrogen Backbone import-connected"


def h2_supply_block(cc):
    """Lines describing the grounded delivered-H2 multiplier and the 2050
    H2-vs-heat-pump gap under the supply band and the distribution-infra scenarios."""
    lo, ce, hi = H2_MULT_RANGE_BY_COUNTRY.get(cc, (None, H2_MULT_BY_COUNTRY.get(cc, 1.0), None))
    out = []
    band = f" range [{lo:.2f}–{hi:.2f}]" if lo is not None else ""
    out.append(f"**Hydrogen supply** (delivered-cost multiplier vs the NW-EU hub, "
               f"grounded {DATE} from the per-country supply-route assessment, "
               f"[h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)): "
               f"central **{ce:.2f}**,{band} — {h2_regime(ce)}.")
    out.append("")
    if H2INF is not None and cc in H2INF.index:
        r = H2INF.loc[cc]
        gb = r["gap_baseline"]
        rc = f"{r['gap_convert_central']:.0f} [{r['gap_convert_low']:.0f}–{r['gap_convert_high']:.0f}]"
        nb = f"{r['gap_newbuild_central']:.0f} [{r['gap_newbuild_low']:.0f}–{r['gap_newbuild_high']:.0f}]"
        sup = ""
        if H2SUP is not None and cc in H2SUP.index:
            s = H2SUP.loc[cc]
            sup = (f"; across the delivered-H2 supply band "
                   f"{s['gap_central']:.0f} [{s['gap_low']:.0f}–{s['gap_high']:.0f}]")
        parity = "at heat-pump parity" if gb <= 0 else f"{gb:.0f} EUR/MWh above the best heat pump"
        out.append(f"**Hydrogen-boiler vs best heat-pump LCOH gap, 2050 (EUR/MWh useful):** "
                   f"baseline {gb:.0f} ({parity}, free gas-grid reuse). With hydrogen paying "
                   f"its distribution network: retrofit {rc}, new-build {nb} (central [low–high])"
                   f"{sup}.")
        out.append("")
    return out

def data_cc(readme_cc):
    return "EL" if readme_cc == "GR" else readme_cc

def scenario_mix_2050(cc):
    """4-scenario 2050 mix table rows (renormalised q50) from mc_country_{SCEN}.csv."""
    rows = []
    for s in SCEN:
        d = MC[s]
        d = d[(d.country == cc) & (d.year == 2050) & (d.variable == "tech_share")]
        if d.empty:
            return None
        sh = dict(zip(d.tech, d.q50))
        tot = sum(sh.values()) or 1.0
        g = lambda k: sh.get(k, 0.0) / tot
        rows.append((SCEN_SHORT[s], g("hp_air") + g("hp_ground"), g("district_heat"),
                     g("h2_boiler"), g("biomass_boiler"),
                     g("gas_boiler") + g("oil_boiler")))
    return rows


def merit_block(cc):
    """Merit-order outcome for this country: where H2 wins the winter peak (endogenous
    peak power price), the peaker's capital recovery, and the DH-stack position."""
    out = []
    mo = MO[MO.country == cc]
    if mo.empty:
        return out
    wins = [SCEN_SHORT[s] for s in SCEN
            if not mo[(mo.scenario == s) & (mo.h2_wins_peak)].empty]
    pe = mo[mo.scenario == "STATED_POLICIES"]
    pe_txt = f" (endogenous cold-snap power price ~€{pe.peak_elec_eur_mwh.iloc[0]:.0f}/MWh)" \
        if "peak_elec_eur_mwh" in mo.columns and not pe.empty else ""
    if wins:
        rec = MP[(MP.country == cc) & (MP.wins_peak)]
        rec_txt = ""
        if not rec.empty:
            best = 100 * (rec.gross_margin_eur_kw_yr / rec.ann_capex_eur_kw_yr).max()
            rec_txt = (f" Even there, the inframarginal rent recovers at most "
                       f"**{best:.0f}%** of the H2 boiler's annualised CAPEX -- the "
                       f"peaker runs too few hours to pay for itself ('missing money').")
        out.append(f"**Merit-order winter peak:** hydrogen is the cheapest peaking source "
                   f"here under {', '.join(wins)}{pe_txt}.{rec_txt}")
    else:
        out.append(f"**Merit-order winter peak:** hydrogen never beats the gas peaker or "
                   f"the cold-snap heat pump here in any scenario{pe_txt}.")
    out.append("")
    md = MD[(MD.country == cc) & (MD.scenario == "NET_ZERO")]
    if not md.empty:
        r = md.iloc[0]
        beats = "undercuts" if r.h2_beats_gas_chp else "does not undercut"
        out.append(f"**District-heating supply stack (Net Zero, 2050):** H2 ranks "
                   f"{int(r.h2_rank_in_stack)} of 5 sources by marginal cost and {beats} "
                   f"the gas CHP at the peak.")
        out.append("")
    ib = IB[IB.country == cc].set_index("scenario")
    if not ib.empty and "total_bn_central" in ib.columns:
        cells = " · ".join(f"{SCEN_SHORT[s]} €{ib.loc[s, 'total_bn_central']:.1f}bn"
                           for s in SCEN if s in ib.index)
        out.append(f"**Network-infrastructure bill (cumulative 2025-2050, central):** {cells} "
                   f"(electricity reinforcement + district-heat expansion + H2 network).")
        out.append("")
    return out


def cost_opt_2050(cc):
    d = co[(co.country == cc) & (co.year == 2050) & (co.variable == "tech_share")]
    if d.empty:
        return None
    s = dict(zip(d.tech, d.q50))
    g = lambda k: s.get(k, 0.0)
    return dict(hp=g("hp_air") + g("hp_ground"), dh=g("district_heat"),
                h2=g("h2_boiler"), fossil=g("gas_boiler") + g("oil_boiler"),
                biomass=g("biomass_boiler"), resistance=g("resistance_heater"))

def shadow_2050(cc):
    d = sp[(sp.variant == "COST_OPT_90") & (sp.year == 2050) & (sp.country == cc)]
    return float(d.shadow_eur_tco2.iloc[0]) if not d.empty else float("nan")

def section(cc):
    hm = HMIX.get(cc)
    if not hm:
        return None
    pct = lambda k: f"{hm[k] * 100:.0f}%"
    lc = {t: {y: compute_lcoh(t, cc, y, carbon_price_scenario="CENTRAL")
              for y in (2025, 2030, 2050)}
          for t in ("gas_boiler", "hp_air", "hp_ground", "h2_boiler")}
    L = []
    L.append(START)
    L.append("")
    L.append(f"## Country-specific model update ({DATE})")
    L.append("")
    L.append("*Reflects the source-audited techno-economics (DEA-corrected CAPEX; "
             "[scenario_assumptions_audit.md](../../literature/scenario_assumptions_audit.md)), "
             "the per-country 2025 heating mix "
             "([heating_mix_2025_audit.md](../../literature/heating_mix_2025_audit.md)), the "
             "per-country least-cost pathway "
             "([cost_optimisation_methodology.md](../../literature/cost_optimisation_methodology.md)), "
             "and the grounded hydrogen supply + distribution-infrastructure assessment "
             "([h2_supply_country_assessment.md](../../literature/h2_supply_country_assessment.md)). "
             f"Supersedes any LCOH / mix figures earlier in this file that predate {DATE}.*")
    L.append("")
    L.append("**2025 residential heating mix** (share of useful heat; Eurostat nrg_d_hhq + "
             "national/EHPA, mean of bases): "
             f"gas {pct('gas_boiler')} · oil {pct('oil_boiler')} · biomass {pct('biomass_boiler')} · "
             f"resistance {pct('resistance_heater')} · heat pump (air {pct('hp_air')} + "
             f"ground {pct('hp_ground')}) · district heat {pct('district_heat')}.")
    L.append("")
    L.append("**LCOH (EUR/MWh useful, CENTRAL carbon, audited costs):**")
    L.append("")
    L.append("| Technology | 2025 | 2030 | 2050 |")
    L.append("|---|---|---|---|")
    names = [("gas_boiler", "Gas boiler"), ("hp_air", "Heat pump (air)"),
             ("hp_ground", "Heat pump (ground)"), ("h2_boiler", "Hydrogen boiler (CENTRAL)")]
    for key, nm in names:
        L.append(f"| {nm} | €{lc[key][2025]:.0f} | €{lc[key][2030]:.0f} | €{lc[key][2050]:.0f} |")
    L.append("")
    mix = scenario_mix_2050(cc)
    if mix:
        L.append("**2050 heating mix by scenario** (Monte Carlo median, renormalised; "
                 "the four June-2026 multi-lever scenarios):")
        L.append("")
        L.append("| Scenario | Heat pump | District heat | Hydrogen | Biomass | Fossil |")
        L.append("|---|---|---|---|---|---|")
        for nm, hp, dh, h2, bio, fo in mix:
            L.append(f"| {nm} | {hp*100:.0f}% | {dh*100:.0f}% | {h2*100:.0f}% | "
                     f"{bio*100:.0f}% | {fo*100:.0f}% |")
        L.append("")
    L.extend(merit_block(cc))
    copt = cost_opt_2050(cc)
    sh = shadow_2050(cc)
    if copt:
        binds = (sh == sh and sh > 1.0)
        cap_txt = (f"the 2050 emissions cap **binds at ~€{sh:.0f}/tCO2** (cost-minimisation alone "
                   "does not reach the target here)" if binds else
                   "the 2050 emissions cap is **non-binding** (cost-minimisation already beats the target)")
        L.append("**COST_OPT least-cost pathway (−90% scope-1 by 2050):** 2050 mix "
                 f"heat pump {copt['hp']*100:.0f}% · district heat {copt['dh']*100:.0f}% · "
                 f"H2 {copt['h2']*100:.0f}% · biomass {copt['biomass']*100:.0f}% · "
                 f"fossil {copt['fossil']*100:.0f}%. Under a per-country cap, {cap_txt}.")
        L.append("")
    L.append(f"**Per-country COST_OPT parameters:** sustainable-biomass ceiling "
             f"{hm['biomass_ceiling_2050']*100:.0f}%, H2-for-buildings ceiling 2050 "
             f"{hm['h2_ceiling_2050']*100:.0f}%, demand reduction by 2050 "
             f"{hm['demand_reduction_2050']*100:.0f}%, stock turnover "
             f"{hm['turnover_rate']*100:.1f}%/yr.")
    L.append("")
    L.extend(h2_supply_block(cc))
    L.append(END)
    return "\n".join(L)

updated, skipped = [], []
for path in sorted(glob.glob("countries/*/README.md")):
    if os.path.basename(os.path.dirname(path)) == "_template":
        continue
    txt = open(path, encoding="utf-8").read()
    head = txt.splitlines()[0]
    mobj = re.search(r"\(([A-Z]{2})\)", head)
    if not mobj:
        skipped.append((path, "no CC in header"))
        continue
    cc = data_cc(mobj.group(1))
    sec = section(cc)
    if sec is None:
        skipped.append((path, f"no heating-mix row for {cc}"))
        continue
    if START in txt and END in txt:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), sec, txt, flags=re.DOTALL)
    else:
        new = txt.rstrip() + "\n\n---\n\n" + sec + "\n"
    # Historical-tagging pass OUTSIDE the marker block: the Gen-1 profile body still
    # carries pre-June-2026 scenario names and numbers. Tag, don't falsify -- the old
    # tables stay as the historical run they were, explicitly superseded by the block.
    blk_s = new.find(START)
    head_part, block_part = new[:blk_s], new[blk_s:]
    head_part = head_part.replace(
        "(REF scenario, Monte Carlo median)",
        "(historical pre-June-2026 run, Monte Carlo median; superseded by the model update below)")
    head_part = head_part.replace(
        "(REF scenario)", "(historical pre-June-2026 run; superseded by the model update below)")
    # The superseded REF / HIGH_HP / H2_HYBRID runs are not used anywhere. Their numbers
    # differ materially from the four current scenarios (the old H2_HYBRID showed 25 per
    # cent hydrogen against H2 Push's 8), so relabelling them "now Net Zero / now H2 Push"
    # invited them to be read as current. Strip any that survive in an old README instead.
    head_part = "\n".join(l for l in head_part.split("\n")
                          if not re.search(r"HIGH_HP|H2_HYBRID", l))
    new = head_part + block_part
    open(path, "w", encoding="utf-8", newline="\n").write(new)
    updated.append(os.path.basename(os.path.dirname(path)) + f" ({cc})")

print(f"Updated {len(updated)} READMEs:")
for u in updated:
    print("  ", u)
if skipped:
    print("SKIPPED:")
    for s in skipped:
        print("  ", s)
