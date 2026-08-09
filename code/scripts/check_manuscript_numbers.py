"""Check the manuscripts' headline numbers against the artefacts that produce them.

check_submission.py verifies that the documents build and that the front matter fits
Elsevier's limits. It says nothing about whether the numbers in the prose still match the
CSVs the reproduction guide points a reader at, and that is where this project has
repeatedly gone wrong: a model fix regenerates the results, most of the prose is updated,
and a handful of instances survive in the least-read or the most-read places. The last
round left a stale firm-fleet share in the abstract itself and a stale emissions-
conditioning premium in seven locations, including the reproduction guide, which told a
reader that running a named script would print a number it no longer prints.

Every check below states the claim, derives the value from `code/results/`, and lists the
files the claim must appear in with the right value. Add a row whenever a number becomes
load-bearing enough to appear in more than one place.

Run:  cd code && PYTHONPATH=. python -m scripts.check_manuscript_numbers
Exit: non-zero if any manuscript figure disagrees with its artefact.
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "code" / "results"

SUBMISSION = sorted((REPO / "paper" / "ae_submission" / "sections").glob("*.tex")) + \
             sorted((REPO / "paper" / "ae_submission" / "si_body").glob("*.tex")) + \
             [REPO / "paper" / "ae_submission" / "V5.tex",
              REPO / "paper" / "ae_submission" / "frontmatter_body.tex",
              REPO / "paper" / "ae_submission" / "REPRODUCE.md",
              REPO / "paper" / "ae_submission" / "cover_letter.md"]
LONG = sorted((REPO / "paper" / "sections").glob("*.tex"))
# Repo-level prose that quotes model numbers. It was outside this gate, and a stale EU
# validation gap (-1.2% where the artefact now says -1.0%) sat in the root REPRODUCE.md and
# two literature notes through every pass this file made. Anything that states a model
# result to a reader belongs in the corpus, manuscript or not.
DOCS = [REPO / "REPRODUCE.md", REPO / "README.md"] + \
       sorted((REPO / "literature").glob("*.md"))
ALL = SUBMISSION + LONG + DOCS


def dispatch50():
    d = pd.read_csv(RESULTS / "power_dispatch_summary.csv")
    return d[(d.basis == "total_elec") & (d.year == 2050)]


def uc50():
    d = pd.read_csv(RESULTS / "power_uc_summary.csv")
    return d[(d.basis == "total_elec") & (d.year == 2050)]


def capacity_built():
    c = pd.read_csv(RESULTS / "capacity_payment.csv")
    return c[c.peaker_cap_gw > 0]


def conditioning_premium() -> tuple[int, int]:
    """Re-run capacity_payment and read the premium off its own console output.

    Reading the printed value rather than recomputing it here means this check fails if
    the script's own arithmetic changes, which is the point: the manuscript quotes what
    the script prints.
    """
    r = subprocess.run([sys.executable, "-m", "scripts.capacity_payment"],
                       cwd=REPO / "code", capture_output=True, text=True,
                       env={**__import__("os").environ, "PYTHONPATH": str(REPO / "code"),
                            # Read the console output without letting the gate rewrite the
                            # SI table this module also emits. A checker must not edit what
                            # it judges, or a moved artefact gets silently written into the
                            # manuscript and then passes.
                            "CAPACITY_PAYMENT_NO_EMIT": "1"})
    out = r.stdout
    m1 = re.search(r"emissions-conditioning premium: (\d+) EUR/tCO2", out)
    m2 = re.search(r"floored at zero: gas [\d.]+ EUR/kW-yr, premium (\d+) EUR/tCO2", out)
    # Fail loudly. Returning -1 on a failed subprocess printed "artefact = -1" as though
    # it were a derived value, and the check that reads it carries only stale patterns, so
    # the gate reported a pass while the module behind the paper's policy headline had not
    # compiled for a full revision. A checker that cannot reach its artefact has not
    # verified anything and must say so.
    if r.returncode != 0 or not (m1 and m2):
        raise SystemExit(
            "scripts.capacity_payment did not yield the conditioning premium "
            f"(exit {r.returncode}). The gate cannot verify EUR172/EUR239 without it.\n"
            + (r.stderr or out)[-800:])
    return int(m1.group(1)), int(m2.group(1))


def num(v: float, dp: int = 1) -> str:
    """Regex matching exactly this number and no other, sign included.

    Two traps, both of which have shipped in this file. An unescaped decimal point makes
    "-1.0" match the literal "-100", so the pattern hit unrelated prose and the check
    reported ok on stale text. And without digit fences "51" matches inside "512" and "1.0"
    inside "31.05".
    """
    body = re.escape(f"{abs(v):.{dp}f}")
    sign = "-" if v < 0 else r"\+?"
    return rf"(?<![\d.]){sign}{body}(?![\d])"


def peaker_ledgers():
    """The three cumulative-2050 shortfall series, recomputed rather than read.

    They are different numbers, they are quoted in different places, and conflating them
    is what put 358/143 in the working paper against 357/142 in the submission while both
    quoted the reduced form's 278 GW and 139 hours beside it.

      reduced form   power_peaker_economics.csv                          -357.3 / -142.4
      UC, off        power_uc_limit_summary.csv -> peaker_economics      -358.4 / -143.2
      UC, on         power_uc_summary.csv       -> peaker_economics      -356.0 / -142.3
    """
    from scripts.power_dispatch import peaker_economics, SCEN
    mc = pd.read_csv(RESULTS / "mc_country_STATED_POLICIES.csv")
    dhc = mc[(mc.year == 2050) & (mc.tech == "district_heat")
             & (mc.variable == "tech_share")]
    dh = dict(zip(dhc.country, dhc.q50))

    def run(path):
        d = pd.read_csv(RESULTS / path)
        if "basis" in d.columns:
            d = d[d.basis == "total_elec"]
        ys, cs = sorted(d.year.unique()), sorted(d.country.unique())

        def pick(c, y, col):
            return float(d[(d.country == c) & (d.year == y)][col].iloc[0])

        E = {c: {y: pick(c, y, "peaker_energy_gwh") for y in ys} for c in cs}
        C = {c: {y: pick(c, y, "peaker_cap_gw") for y in ys} for c in cs}
        e = pd.concat([peaker_economics(c, s, E.get(c, {}), C.get(c, {}),
                                        dh_avail=float(dh.get(c, 0.0)))
                       for c in cs for s in SCEN], ignore_index=True)
        e = e[(e.year == 2050) & (e.scenario == "H2_PUSH")]
        return e.cum_h2_profit_meur.sum() / 1e3, e.cum_gas_profit_meur.sum() / 1e3

    red = pd.read_csv(RESULTS / "power_peaker_economics.csv")
    red = red[(red.year == 2050) & (red.scenario == "H2_PUSH")]
    reduced = (red.cum_h2_profit_meur.sum() / 1e3,
               red.cum_gas_profit_meur.sum() / 1e3)
    return reduced, run("power_uc_limit_summary.csv"), run("power_uc_summary.csv")


def build_checks():
    x, u, b = dispatch50(), uc50(), capacity_built()
    fleet = x.peaker_cap_gw.sum()
    peak = x.peak_gw.sum()
    flh = x.peaker_energy_gwh.sum() / fleet
    w = b.peaker_cap_gw
    rec_cw = (b.recovery_h2_pct * w).sum() / w.sum()
    gas_cheaper = int((b.standing_payment_gas < b.standing_payment_h2).sum())
    prem, prem_floor = conditioning_premium()
    # The two per-MWh-e storage rungs, derived rather than typed. power_storage_adder
    # divides the heat-side rate by the turbine efficiency, so the cavern and non-cavern
    # markets each return a single value.
    from scripts.power_peak_price import power_storage_adder as _psa
    from scripts.merit_order_heat import CAVERN as _CAV
    from src.Config import EU_COUNTRIES as _EUC
    storage_mwh_e = (min(_psa(c) for c in _EUC if c in _CAV),
                     min(_psa(c) for c in _EUC if c not in _CAV))
    rob = pd.read_csv(RESULTS / "power_dispatch_robustness.csv").sort_values("dunkelflaute_wind")

    traj = pd.read_csv(RESULTS / "power_peaker_recovery_projection.csv")
    rec_traj = traj[traj.scenario == "H2_PUSH"].sort_values("year")

    gap = pd.read_csv(RESULTS / "h2_hp_gap.csv").sort_values("gap_2050")
    near10 = list(gap[gap.gap_2050.abs() <= 10].country)

    fca = pd.read_csv(RESULTS / "firm_capacity_attribution.csv").set_index("basis")

    # Monte Carlo convergence, derived by scripts/mc_convergence.py. The four median
    # draw counts and the decile range were stated in both supplements with nothing
    # behind them: no script computed them and no CSV carried them. They were right,
    # which is the worst case, since nothing would have caught them going wrong.
    _mcc = pd.read_csv(RESULTS / "mc_convergence.csv")
    _mcm = _mcc[_mcc["quantile"] == "median"].set_index("scenario")
    mc_med = ", ".join(str(int(_mcm.loc[s, "last_exit_draw"])) for s in
                       ("CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"))
    _mcd = _mcc[_mcc["quantile"] == "p10"]
    mc_dec_lo = int(_mcd.last_exit_draw.min())
    mc_dec_hi = int(_mcd.last_exit_draw.max())

    # Country-level validation error, derived by make_validation_table.error_metrics.
    # Quoted to one decimal in both manuscripts, so the patterns are built at that width.
    _vm = pd.read_csv(RESULTS / "bottomup_validation_metrics.csv").set_index("basis")
    _raw, _vint = _vm.loc["raw"], _vm.loc["vintage_matched"]
    val_mape = f"{_raw.mape_pct:.1f}"
    val_wmape = f"{_raw.weighted_mape_pct:.1f}"
    val_rmse = f"{_raw.rmse_pct:.1f}"
    val_medae = f"{_raw.median_abs_err_pct:.1f}"
    val_vm = (f"{_vint.mape_pct:.1f}, {_vint.weighted_mape_pct:.1f}, "
              f"{_vint.rmse_pct:.1f} and {_vint.median_abs_err_pct:.1f}")

    (led_h2, led_gas), (lim_h2, lim_gas), (uc_h2, uc_gas) = peaker_ledgers()
    uc_ease_h2 = abs(lim_h2) - abs(uc_h2)

    # The dispatch-arena sensitivities, read off the artefact that computes them rather
    # than restated here. If the sweep moves, the gate moves with it and the prose fails.
    _ars = pd.read_csv(RESULTS / "dispatch_arena_sensitivity.csv")

    def _ars_row(axis, setting):
        r = _ars[(_ars.axis == axis) & (_ars.setting == setting)]
        if r.empty:
            raise SystemExit(f"dispatch_arena_sensitivity.csv has no {axis}/{setting} row")
        return r.iloc[0]

    _lm = _ars_row("h2_last_mile", "charged")
    # The demand-weighted ceiling quartet, on both accounting bases. These two lists look
    # interchangeable and are not: 0, 5.1, 7.9, 9.3 belongs to the basis that charges
    # hydrogen no last-mile network, and 0, 0.6, 7.5, 9.0 to the symmetric one. The AE body
    # switched its headline to symmetric and kept quoting the asymmetric quartet, which no
    # gate could see because only the Stated-Policies value was pinned, and only inside one
    # sensitivity sentence.
    _lm_open = _ars_row("h2_last_mile", "not charged")
    _S4 = ("CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH")

    def _pct(v: float) -> str:
        """Both manuscripts write the zero as `0` and every other value to one decimal."""
        return "0" if abs(v) < 1e-9 else f"{v:.1f}"

    arena_bound_sym = ", ".join(_pct(float(_lm[f"bound_pct_{s}"])) for s in _S4)
    arena_bound_open = ", ".join(_pct(float(_lm_open[f"bound_pct_{s}"])) for s in _S4)
    # Both papers write the quartet as "a, b, c and d", so each pattern needs the list
    # split at the final comma.
    _sym_lo, _sym_hi = arena_bound_sym.rsplit(", ", 1)
    _opn_lo, _opn_hi = arena_bound_open.rsplit(", ", 1)

    # The building-peak winners by name, on both bases. Both papers name the Stated
    # Policies set, and until dispatch_arena_sensitivity persisted it the names traced to
    # nothing while the counts beside them traced to a CSV.
    _bpw = pd.read_csv(RESULTS / "building_peak_winners.csv")
    _bpw_sym = _bpw[(_bpw.basis == "symmetric") & (_bpw.scenario == "STATED_POLICIES")]
    arena_win_sp = " and ".join(str(_bpw_sym.countries.iloc[0]).split())
    arena_lastmile = ", ".join(str(int(_lm[f"count_{s}"])) for s in
                               ("CURRENT_POLICIES", "STATED_POLICIES",
                                "NET_ZERO", "H2_PUSH"))
    arena_lastmile_bound = f"{float(_lm['bound_pct_STATED_POLICIES']):.1f}"
    cop_deep_h2p = str(int(_ars_row("cop_derate", "0.75 floor 2.2")["count_H2_PUSH"]))

    mop = pd.read_csv(RESULTS / "merit_order_profit.csv")
    mw = mop[mop.wins_peak]
    heat_rec = 100 * mw.gross_margin_eur_kw_yr.sum() / mw.ann_capex_eur_kw_yr.sum()
    agg_2050 = float(rec_traj.h2_recovery_pct.iloc[-1])

    n3 = int((x.lol_hours == 3).sum())
    n0 = int((x.lol_hours == 0).sum())
    _mh = pd.read_csv(RESULTS / "merit_order_heat.csv")
    _lp = pd.read_csv(RESULTS / "heat_load_profile.csv").set_index("country")["annual_TWh"]
    _mh["w"] = _mh.country.map(_lp)
    # Two artefacts compute this same ceiling and they disagreed in print: the manuscript
    # said 8.0 for Net Zero and the sensitivity sweep said 7.9. Neither was stale. The
    # merit-order file rounds h2_derived_share to three decimals for display, and summing
    # that display column over 29 countries accumulated 0.02 pp, enough to tip 7.94 to
    # 7.96 and round the other way. This gate was making the same mistake, so it would
    # have certified the wrong value. Take the published bound from the sweep, which sums
    # unrounded slice fractions, and assert the two paths still describe one model.
    _sw = pd.read_csv(RESULTS / "dispatch_arena_sensitivity.csv")
    # The sweep's note column now names the accounting basis rather than the vintage, so
    # this selects the asymmetric row by its setting. It used note == "published", which
    # silently became an empty selection and crashed the moment the labels were corrected.
    _pub = _sw[(_sw.axis == "h2_last_mile") & (_sw.setting == "not charged")].iloc[0]
    _order = list(dict.fromkeys(_mh.scenario))
    dshares = ", ".join(f"{float(_pub[f'bound_pct_{s}']):.1f}" for s in _order)
    for _s in _order:
        _rounded = (_mh[_mh.scenario == _s].eval("h2_derived_share * w").sum()
                    / _mh[_mh.scenario == _s].w.sum() * 100)
        # Compare at the precision the paper prints, not within a tolerance looser than
        # it. A 0.10 pp band tolerated exactly the 0.065 pp disagreement that produced the
        # published 8.0 against the artefact's 7.9, so the guard would have passed the
        # defect it was written for. Two artefacts computing one quantity have to agree on
        # the digit that reaches the page.
        if round(_rounded, 1) != round(float(_pub[f"bound_pct_{_s}"]), 1):
            raise SystemExit(
                f"derived ceiling for {_s} disagrees between artefacts: "
                f"merit_order_heat {_rounded:.2f} vs sweep {_pub[f'bound_pct_{_s}']}. "
                "These are two computations of one quantity; reconcile them at source.")

    # Two 2015 validation gaps that look interchangeable and are not. lmdi_design backcasts
    # the whole design decomposition, whose drivers nearly cancel; reconcile_backcast applies
    # stock growth alone with no envelope term to offset it. Pinning both stops either from
    # being quoted as the other, which is how -1.2% survived after the run moved to -1.0%.
    _ld = pd.read_csv(RESULTS / "lmdi_design.csv")
    lmdi_gap = float(_ld.loc[_ld.country == "EU", "gap_2015_vs_hotmaps_pct"].iloc[0])
    _rb = pd.read_csv(RESULTS / "reconcile_backcast.csv")
    _eu = _rb[_rb.country == "EU(sum)"].iloc[0]
    vm_gap = float(_eu.vintage_matched_gap_pct)

    _r2 = pd.read_csv(RESULTS / "global_sensitivity_econ_r2.csv").set_index("scenario")
    r2s = ", ".join(f"{_r2.loc[s, 'rank_r2']:.3f}" for s in
                    ("CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH")
                    if s in _r2.index)

    dhc = pd.read_csv(RESULTS / "dh_connection_charge.csv")

    # Germany and Spain are the worked pair for the base-load seasonal-storage charge, and
    # the quantity has two efficiency conventions that produce near-identical numbers: the
    # base-load levelised cost divides by the year-specific boiler efficiency (0.92 at
    # 2050) giving 12.1 and 28.4, and the peaking layer divides by 0.90 giving 12.4 and
    # 29.0. The SI table published the peaking pair under a base-load heading while all the
    # prose carried the base-load pair, and nothing distinguished them to a reader. Assert
    # the base-load pair wherever the base-load charge is named.
    # The NUTS3 region count was 1,367 in both manuscripts, the architecture figure's
    # header band and the graphical abstract, and it traced to nothing: the demand surface
    # carries 1,369 level-3 regions. The same sentence's 3,863 TWh was exact, which is what
    # made the wrong count look checked. Derive both from the file.
    _n3 = pd.read_csv(REPO / "code" / "data" / "processed" / "heat_demand_by_region" /
                      "heat_demand_NUTS3_all.csv")
    _n3 = _n3[_n3.nuts_level == 3]
    n3_regions = int(_n3.nuts_id.nunique())
    n3_twh = float(_n3.heat_TWh.sum())

    _sg = pd.read_csv(RESULTS / "storage_geology.csv").set_index("country")
    sg_de = float(_sg.loc["DE", "adder_baseload_eur_mwh_heat"])
    sg_es = float(_sg.loc["ES", "adder_baseload_eur_mwh_heat"])

    # The Swiss verdict rests on two arms that differ by 4 EUR/MWh and are easy to swap.
    # The uncoupled ("limit") arm takes EU prices without feeding Swiss load back; the
    # endogenous arm closes the fixed point and credits the reservoir fleet. Both papers
    # quote the uncoupled gap as the conservative one and the endogenous gap beside it, so
    # a swap would silently make the conservative claim on the wider number.
    # Switzerland wins the H2 Push building peak on the uncoupled 29-country series and
    # loses it on the reservoir-credited endogenous arm. Both manuscripts state a Swiss
    # peaking verdict; the working paper stated the endogenous one four times without
    # naming the arm, which reads as a denial of the uncoupled win that puts CH inside the
    # count of 16 the same paper reports. Any unqualified denial fails here.
    # The blue-hydrogen base-load count has two readings of one German estimate and they
    # disagree: a flat EUR 81 gate closes all seven leads, a green-to-blue ratio leaves
    # Denmark. Two passages used to decline the count entirely while the conclusion and
    # the submission asserted the flat one, so the assertion is now derived and both
    # readings are pinned. Quoting either count without its construction is the failure.
    _bb = pd.read_csv(RESULTS / "blue_hydrogen_baseload.csv")
    blue_flat_hp = int((~_bb.flat_lead).sum())
    blue_prop_hp = int((~_bb.proportional_lead).sum())

    _mo = pd.read_csv(RESULTS / "merit_order_heat.csv")
    _ch = _mo[(_mo.country == "CH") & (_mo.scenario == "H2_PUSH")]
    ch_wins_uncoupled = bool(_ch.h2_wins_peak.iloc[0])

    _si = pd.read_csv(RESULTS / "swiss_integration.csv")
    _si = _si[(_si.year == 2050) & (_si.scenario == "STATED_POLICIES")]
    def _ch_gap(mode):
        r = _si[_si["mode"] == mode].iloc[0]
        return float(r.h2_boiler_lcoh) - float(r.hp_air_lcoh)
    ch_limit, ch_endo = _ch_gap("limit"), _ch_gap("endogenous")

    # The carbon charge the heat pump pays. Electricity is netted against its 2025 level,
    # so the adder is small, and the quantity had two values in circulation: a median of
    # 0.7 EUR/MWh in four places and 4.7 in two others, both describing the same thing.
    # 4.7 traces to no year, no carbon path and no efficiency convention in the model.
    # No CSV carries it, so derive it from the same functions the LCOH pass calls.
    from src.Economics import get_cop
    from src.Policy import get_carbon_cost_adder_eur_per_mwh_useful as _adder
    from src.Config import EU_COUNTRIES as _CS
    import statistics as _st
    _hp30 = [_adder("electricity", c, 2030, get_cop("hp_air", c, 2030), "CENTRAL")
             for c in _CS]
    hp_carbon_2030 = _st.median(_hp30)
    hp_carbon_2030_max = max(_hp30)
    # And the year it actually reaches zero everywhere. It is zero at the median from
    # 2040 but two grids still pay a fraction then, so "exactly zero by 2040" was wrong.
    # Swept over all three carbon paths, because the claim this pins is the one that
    # makes the 2050 hydrogen counts path-independent, and that has to hold on each.
    hp_carbon_zero_yr = next(
        y for y in (2030, 2035, 2040, 2045, 2050)
        if max(_adder("electricity", c, y, get_cop("hp_air", c, y), p)
               for c in _CS for p in ("LOW", "CENTRAL", "HIGH")) < 0.005)

    # The base-load count across the four hydrogen price paths. A referee reported this
    # as tracing to nothing, because no CSV carried it and the nearest file sweeps the
    # supply-route multiplier instead, returning 15 / 22 / 26 against the prose's
    # 13 / 22 / 26 / 29. The counts do reproduce; two of the four values coincide, which
    # is what made the substitution look plausible. Both axes are pinned so neither can
    # be quoted as the other.
    _pp = pd.read_csv(RESULTS / "h2_price_path_counts.csv").set_index("h2_price_path")
    h2_path_counts = ", ".join(str(int(_pp.loc[p, "hp_cheaper_count"]))
                               for p in ("RAPID", "CENTRAL", "SLOW", "STRANDED"))
    _hs = pd.read_csv(RESULTS / "h2_supply_scenario.csv")
    h2_supply_counts = ", ".join(str(int((_hs[c] > 0).sum()))
                                 for c in ("gap_low", "gap_central", "gap_high"))

    econ = pd.read_csv(RESULTS / "power_peaker_economics.csv")
    econ = econ[econ.year == 2050]
    ratios = [econ[econ.scenario == s].cum_h2_profit_meur.sum()
              / econ[econ.scenario == s].cum_gas_profit_meur.sum()
              for s in ("CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH")]

    return [
        # (claim, value the prose must carry, patterns that must NOT appear, files)
        # The unit commitment's own fleet is legitimately 280 GW, because its sizing pass
        # builds a 2.8 GW peaker in Romania that the reduced form's duration test does not.
        # Note the cause is the sizing pass and NOT the reserve and ramp constraints: the
        # limit arm runs with those constraints disabled and still builds Romania
        # (power_uc_limit_validation.csv, rf_cap 0.0 against uc_cap 2.8). Three documents
        # carried the wrong explanation, including this comment.
        # Only a 280 that is NOT attributed to the unit commitment is stale.
        # Both numbers come from one file and one of them was wrong for months while the
        # other was exact. Any count that is not the file's fails, in each manuscript.
        # Three region counts coexist and each is right for its own artefact: 1,369 in the
        # demand surface, 1,397 in the building-stock table, 1,359 drawn by the map. This
        # check is the demand-surface one, so it runs on the files that make that claim.
        # Pattern the slot, not the stale string: any span attached to the price paths
        # that is not the file's endpoints fails, including the supply-route 15.
        ("base-load count across the four hydrogen price paths", h2_path_counts,
         [r"(?<![\d.])(?!13\b)\d+ (?:of (?:the )?29 (?:markets|countries) )?"
          r"on (?:a|the) rapid",
          r"from (?!13\b)\d+ to \d+ (?:markets )?across the hydrogen price paths",
          r"from 13 to (?!29\b)\d+ (?:markets )?across the hydrogen price paths"],
         SUBMISSION + LONG,
         r"13 of (?:the )?29 (?:markets|countries)[^.]{0,60}?22[^.]{0,45}?26[^.]{0,60}?29"),
        # This check had an empty stale list and no presence assertion, so it printed
        # [ok] on every run while testing nothing. Pattern the slot the claim occupies
        # (the low-to-high span across the supply-route fractions) and require the right
        # span to appear, so a silent disappearance fails too.
        ("base-load count across the hydrogen supply routes", h2_supply_counts,
         [rf"across the fractions we\s+\w+,? (?!{h2_supply_counts.split(', ')[0]} to "
          rf"{h2_supply_counts.split(', ')[2]}\b)\d+ to \d+",
          rf"22 markets on the adopted basis and (?!{h2_supply_counts.split(', ')[0]} to "
          rf"{h2_supply_counts.split(', ')[2]}\b)\d+ to \d+"],
         SUBMISSION + LONG,
         {"AE submission": rf"{h2_supply_counts.split(', ')[0]} to "
                           rf"{h2_supply_counts.split(', ')[2]} across the fractions"}),
        # Pattern the slot, not the stale string: any per-MWh figure attached to the
        # 2025-level netting that is not the median fails, so a future wrong value fails
        # too. The Polish maximum is excluded by name because it is the same artefact.
        ("heat-pump carbon adder at 2030, median EUR/MWh", f"{hp_carbon_2030:.1f}",
         [rf"2025 (?:carbon cost|level)[^.]{{0,160}}?"
          rf"(?<![\d.])(?!{hp_carbon_2030:.1f}\b|{hp_carbon_2030_max:.1f}\b)"
          rf"\d+\.\d/MWh"],
         SUBMISSION + LONG, rf"{hp_carbon_2030:.1f}/MWh"),
        # The increment is zero at the median from 2040 and zero in every market only at
        # 2050. Any claim that it is exactly zero from 2040 contradicts France and Sweden.
        ("year the electricity carbon increment reaches zero everywhere",
         hp_carbon_zero_yr,
         [r"(?:exactly zero|falls to zero|is zero|reaches zero)(?: from| by)? 2040",
          r"(?:zero|nothing) by 2040(?! at the median)",
          r"increment is zero by 2040"],
         SUBMISSION + LONG, rf"zero (?:in every market )?by {hp_carbon_zero_yr}"),
        ("NUTS3 regions in the demand surface", n3_regions,
         # The map caption legitimately says "1,359 regions the map draws", a different
         # and correct count, so that phrasing is excluded rather than the check narrowed
         # to a wording only one of the three sites uses.
         [rf"1\{{,\}}(?!{n3_regions % 1000}\b)\d{{3}} (?:NUTS3 )?regions(?! the map draws)"],
         SUBMISSION + LONG,
         rf"1\{{,\}}{n3_regions % 1000}"),
        ("NUTS3 demand surface total, TWh", round(n3_twh),
         # normalise() turns `~` into a space, so the old pattern, written with a
         # literal `~TWh`, could never match and reported [ok] on every run while
         # testing nothing. Repaired naively it matched every 3,xxx TWh in the
         # corpus, including the 2025 base year and the 2050 band, which are
         # different quantities. Pattern the slot: this total is the Hotmaps
         # regional surface, always named as such or set against the Eurostat
         # figure it is compared with.
         [rf"regional total is 3\{{,\}}(?!{round(n3_twh) % 1000}\b)\d{{3}}",
          rf"2\{{,\}}075\$? vs \$?3\{{,\}}(?!{round(n3_twh) % 1000}\b)\d{{3}}",
          rf"3\{{,\}}(?!{round(n3_twh) % 1000}\b)\d{{3}} TWh\\,yr"],
         SUBMISSION + LONG, rf"3\{{,\}}{round(n3_twh) % 1000}"),
        # Presence assertions on the headline quantities. Without them these were pure
        # blacklists on a value that was wrong once: a referee replaced all 31 occurrences
        # of the 278 GW fleet with 999 across the submission and the gate printed
        # "[ok ] firm peaker fleet, GW artefact = 278" and exited 0. A check that only
        # knows the last wrong answer certifies every new one. Each pattern below is the
        # paper's own phrasing for the quantity, so a value that silently changes or
        # disappears fails in the manuscript that carries it.
        ("firm peaker fleet, GW", round(fleet),
         [r"(?<!commitment puts a )\b280 GW\b", r"\b281 GW\b"], ALL,
         # normalise() has already turned every ~ into a space, so these match the
         # normalised text and not the LaTeX source.
         {"AE submission": rf"(?<![\d.]){round(fleet)} GW",
          "working paper": rf"(?<![\d.]){round(fleet)} GW"}),
        ("fleet share of system peak, %", round(100 * fleet / peak),
         [r"32\\?% of study-area peak",
          r"\b32 per cent of (?:the 889|peak|the study-area)",
          r"roughly 32 per cent"], ALL,
         {"AE submission": rf"(?<![\d.]){round(100 * fleet / peak)} per cent of the study area's",
          "working paper": rf"(?<![\d.]){round(100 * fleet / peak)} per cent of peak capacity"}),
        # Two 138s hid from the literal patterns because the SI writes the number in math
        # mode with an approximation sign: "$\approx$138~h" and "$\sim$138-full-load-hour".
        # normalise() strips the $ but the words "about"/"hours" were never there to match.
        # Pattern the NUMBER in its unit context instead of a remembered phrase.
        # No presence assertion left this one blacklist-only: rewriting 139 at a single
        # site was silent even after the count contract went in, because a count needs a
        # pattern to count. It is quoted in the conclusion and in the working paper's
        # abstract, so it gets one in each.
        ("fleet full-load hours", round(flh),
         [r"\b138[- ]?(?:full-load|h\b|hours\b)"
          r"(?!(?:[^.]|\.\d){0,120}?(?:limits-off|limits off|constraints switched off|"
          r"is not the 139|280\.5))",
          r"about 138\b"], ALL,
         {"AE submission": rf"(?<![\d.]){round(flh)} (?:full-load )?hours?",
          "working paper": rf"(?<![\d.]){round(flh)} full-load"}),
        ("countries building a peaker", int((x.peaker_cap_gw > 0).sum()),
         [r"Twenty of the 29\s*\n?build peaking"], ALL),
        ("cavern markets that build", len(b),
         [r"[Ss]ix of the seven cavern markets build", r"six markets that actually build",
          r"of the six markets that build", r"across the six that build"], ALL),
        # The capacity-weighted recovery is quoted to one decimal in three documents and
        # moved by 0.1 when the sizing fix dropped Romania out of the weighting. A tenth
        # of a per cent reads as a typo rather than a stale number, which is exactly why
        # it survived the last sweep in the long paper while the submission was corrected.
        ("capacity-weighted H2 recovery, %", round(rec_cw, 1),
         [r"from 8\.6 to about 51", r"recovery of 8\.6"], ALL,
         {"AE submission": rf"recovery runs 4\.4, {rec_cw:.1f}"}),
        ("markets where gas needs the smaller payment", gas_cheaper,
         [r"in five of the six markets that build", r"gas is cheaper in five of those six"], ALL),
        # Blacklist only, so substituting a brand-new wrong premium passed the whole
        # gate. Pattern the slot and require the live value: the emissions condition is
        # the paper's answer to its own policy question and appears in six documents.
        # Two slots covered two of the seven sites. The other five phrase the premium
        # without "of" ("costs about", "it displaces, about", "premium is about"), so
        # substituting a wrong number in any of them passed, and the per-manuscript
        # presence assertion was then satisfied by the abstract's own duplicate. A bare
        # \euro{}\d+/tCO slot cannot be used: nine other values legitimately take that
        # shape in these two papers. So one anchored slot per phrasing in use.
        ("conditioning premium, EUR/tCO2", prem,
         [r"178/tCO", r"178 EUR/tCO2", r"178 €/tCO2",
          rf"condition worth at least \\euro\{{\}}(?!{prem}\b)\d+",
          rf"(?:premium|condition) (?:of|is) (?:about |roughly )?"
          rf"\\euro\{{\}}(?!{prem}\b|{prem_floor}\b)\d+/tCO",
          rf"\\euro\{{\}}(?!{prem}\b|{prem_floor}\b)\d+/tCO[^.]{{0,30}}of displaced gas",
          rf"gas generation it displaces, (?:about |roughly )?"
          rf"\\euro\{{\}}(?!{prem}\b)\d+/tCO"],
         ALL,
         {"AE submission": rf"\\euro\{{\}}{prem}/tCO",
          "working paper": rf"\\euro\{{\}}{prem}/tCO"}),
        # Round 26 gave `prem` one anchored slot per phrasing and left its floored twin
        # with one, so 239 was guarded at a single site of five and the working paper's
        # own abstract could state a value the model does not produce with the suite
        # green. The two values are the same claim at two settings and get the same
        # treatment. A bare 239 slot is unusable: power_bridge.tex:137 carries an
        # unrelated \euro{}239/MWh-e gas clearing price, so every anchor is tCO2-bound.
        ("conditioning premium floored, EUR/tCO2", prem_floor,
         [r"245/tCO", r"245 EUR/tCO2",
          # Anchor on the premium itself. "floored at zero" also appears about the
          # carbon increment, and matching that fired on a correct sentence.
          rf"conditioning premium to (?:roughly |about )?\\euro\{{\}}(?!{prem_floor}\b)\d+",
          # One slot per phrasing, each anchored so the number sits immediately beside
          # the words that identify it. A looser slot spanning 60 characters matched
          # starting at the legitimate 172 and reached forward to "rent floored",
          # reporting two correct sentences as stale.
          rf"or \\euro\{{\}}(?!{prem_floor}\b)\d+ if the gas rent is floored",
          rf"rising to (?:roughly |about )?\\euro\{{\}}(?!{prem_floor}\b)\d+/tCO",
          rf"or about €(?!{prem_floor}\b)\d+/tCO2 with the gas plant's rent floored",
          rf"\(≈(?!{prem_floor}\b)\d+ with the gas rent floored"],
         ALL,
         {"AE submission": rf"\\euro\{{\}}{prem_floor}/tCO",
          "working paper": rf"\\euro\{{\}}{prem_floor}\b"}),
        ("islanded requirement sweep, GW",
         ", ".join(str(int(v)) for v in rob.islanded_gw[::-1]),
         [r"291, 280 and 252"], ALL,
         # The prose states the sweep in the opposite order to the artefact column,
         # so build the assertion from the same values rather than reusing the string.
         {"AE submission": "islanded requirement runs "
          + ", ".join(str(int(v)) for v in list(rob.islanded_gw)[:2])
          + rf" and {int(list(rob.islanded_gw)[2])} GW"}),
        # The standing payment is the paper's own answer to its own policy question, and
        # it was quoted as "31 to 69" against a script that prints "31 to 63". The 69 is
        # Romania's annualised capex, and Romania builds nothing. Both ends of both ranges
        # are pinned here, to the builders, because a non-builder has no capital to recover.
        ("standing payment H2, EUR/kW-yr",
         f"{b.standing_payment_h2.min():.0f} to {b.standing_payment_h2.max():.0f}",
         [rf"(?<![\d.]){b.standing_payment_h2.min():.0f} to "
          rf"(?!{b.standing_payment_h2.max():.0f}\b)\d+(?=.{{0,45}}?(?:kW-yr|hydrogen))"], ALL,
         rf"{b.standing_payment_h2.min():.0f} to {b.standing_payment_h2.max():.0f}"),
        ("annualised H2 capex, EUR/kW-yr",
         f"{b.ann_capex_h2.min():.0f} to {b.ann_capex_h2.max():.0f}",
         [rf"\b{b.ann_capex_h2.min():.0f} to (?!{b.ann_capex_h2.max():.0f}\b)\d+/kW-yr",
          r"13\.9 to 18\.6"], ALL),
        # The only committed recovery trajectory rises monotonically to 2050. Any claim
        # that it peaks or plateaus earlier contradicts it.
        ("recovery trajectory shape",
         f"monotone to {int(rec_traj.year.iloc[-1])}, peak {rec_traj.h2_recovery_pct.max():.1f}%",
         [r"plateau[s]? (?:there |from )", r"peak in the late 1930s|peak in the late 2030s"], ALL),
        ("near-boundary countries within EUR10/MWh", ", ".join(near10),
         [r"Austria at \$\+\$8\.0 and\s*Romania", r"Romania a little beyond"], ALL),
        # The district-heat connection charge was quantified in the prose before it was
        # committed to a script, which is the same defect ("a number with no artefact")
        # this file exists to catch. It has a script now, and these are its outputs.
        ("district heat cheapest, before / after the connection charge",
         f"{int(dhc.dh_cheaper_before.sum())} of {len(dhc)} / {int(dhc.dh_cheaper_after.sum())} of {len(dhc)}",
         [r"in 26 of 29 countries to (?!7\b)\d+", r"median \\euro\{\}21\.7/MWh"], ALL,
         r"26 of 29 (?:countries )?to 7"),
        # The heat-side peaker is a different asset from the power peaker: 20-year life,
        # 2 per cent FOM, and it runs ~519 h against the power fleet's 139, so it recovers
        # more. The prose claimed 13 per cent "on the 29-country cumulative path"; no
        # aggregation yields 13, and the 29 is 29 winning country-SCENARIO pairs spanning
        # only 16 countries, not 29 countries. Both errors were the same misreading.
        ("heat-side peaker recovery, %", round(heat_rec, 1),
         [r"about 13 per cent on the 29-country",
          r"29-country cumulative\s*path"], ALL,
         {"working paper": r"about 20 per cent, aggregated across the 29"}),
        # The long paper rounded the study-area aggregate to 14 while the AE carried 14.6.
        # Same quantity, two documents, two values.
        ("aggregate recovery at 2050, %", round(agg_2050, 1),
         [r"reaches 14 per cent by 2050", r"aggregate, which reaches 14 per"], ALL,
         {"AE submission": rf"{agg_2050:.1f} per cent in 2050",
          "working paper": rf"reaches {agg_2050:.1f} per cent by 2050"}),
        # The long paper quoted the storage adder's per-MWh-heat values under an MWh-e
        # label. power_peak_price.power_storage_adder divides by the turbine efficiency, so
        # per MWh-e it is 112.5 and 225.0, not 50 and 100.
        # The audit reported this check as governing no text anywhere. Half right: the
        # AE submission does not state it, and the working paper does, at
        # power_bridge.tex, rounded to whole euros. So the fix is a presence assertion
        # scoped to the paper that carries it and keyed to the form it prints, not
        # deletion. The check was a pure blacklist on two historical phrasings and would
        # have run green forever whatever the artefact said.
        ("storage adder per MWh-e",
         f"{storage_mwh_e[0]:.0f} / {storage_mwh_e[1]:.0f}",
         [r"\\euro\{\}50/MWh-e where caverns", r"expressed per\s+MWh-e dispatched",
          rf"about \\euro\{{\}}(?!{storage_mwh_e[0]:.0f}\b)\d+ and "
          rf"\\euro\{{\}}\d+/MWh-e at \$"],
         ALL,
         {"working paper": rf"about \\euro\{{\}}{storage_mwh_e[0]:.0f} and "
                           rf"\\euro\{{\}}{storage_mwh_e[1]:.0f}/MWh-e"}),
        # The lost-load distribution is 19 countries at three hours, nine at none, and
        # Romania at two. "The remaining 10 carry none" folded Romania in with the zeros.
        ("lost-load distribution", f"{n3} at 3 h, {n0} at none, RO at 2",
         [r"the remaining 10 carry none"], ALL),
        # The demand-weighted derived shares, which the scenario ceilings are bounded by.
        # The prose previously gave "0 to 8 per cent" and called it the basis for a ceiling
        # the same sentence set at 8, which was circular.
        ("demand-weighted derived shares, %", dshares,
         [r"of 0 to 8 per cent of useful heat, the basis"], ALL),
        # These four survived only in prose and a figure title, because to_csv discards
        # DataFrame.attrs. They are now written to their own CSV, so they are checkable.
        ("rank-R2 by scenario", r2s,
         [r"rank-\$?R\^?2\$? (?:is |= )?0\.9[0-2]"], ALL),
        # The firm-capacity attribution was hand arithmetic on the paper's own inputs
        # until scripts/firm_capacity_attribution.py was written for it; a referee looked
        # for the artefact and found none. Both adders and both counts now come from it.
        ("firm-capacity adder charged in full, EUR/MWh",
         f"{fca.loc['full','adder_lo_eur_mwh']} to {fca.loc['full','adder_hi_eur_mwh']}",
         [r"12\.1 to 16\.2/MWh", r"11\.1 to 14\.4/MWh"], ALL),
        ("base-load count charged in full",
         f"{int(fca.loc['full','count_lo'])} then {int(fca.loc['full','count_hi'])}",
         [r"falls to 17 and then 14 of 29", r"to 17 and then 14\b"], ALL),
        ("cumulative H2-to-gas shortfall ratio",
         f"{min(ratios):.1f} to {max(ratios):.1f}",
         [r"roughly three to four times the loss"], ALL),
        # The commitment layer's easing read 1.3/0.2 bn in both documents against an
        # artefact that says 2.4/0.9. It had been carried forward from an earlier run:
        # nothing recomputed it, because the base it is subtracted from moved instead.
        # normalise() leaves \euro{} in place, so a pattern written as a natural phrase
        # misses "hydrogen by about \euro{}1.3 bn" entirely. This one shipped that way and
        # passed on text I had deliberately broken to test it. Slot the number instead:
        # any easing near the commitment layer that is not the artefact's value fails.
        # Assert the value, not the absence of a remembered wrong one: any Swiss base-load
        # gap that is neither arm fails, and a document that discusses the Swiss base-load
        # comparison without stating the uncoupled gap fails too.
        ("Swiss base-load gap, uncoupled arm, EUR/MWh", round(ch_limit, 1),
         [rf"\\euro\{{\}}(?!{re.escape(f'{ch_limit:.1f}')})\d\.\d/MWh below the\s+hydrogen boiler"], ALL,
         rf"{re.escape(f'{ch_limit:.1f}')}/MWh"),
        ("Swiss base-load gap, endogenous arm, EUR/MWh", round(ch_endo, 1),
         [], LONG, rf"{re.escape(f'{ch_endo:.1f}')}/MWh"),
        ("base-load storage charge, cavern worked example, EUR/MWh", sg_de,
         [r"\\euro\{\}12\.4/MWh"], ALL, r"12\.1/MWh"),
        ("base-load storage charge, non-cavern worked example, EUR/MWh", sg_es,
         [r"\\euro\{\}29\.0/MWh"], ALL, r"28\.4/MWh"),
        # Assert the qualifier, not the number. The claim is only true of one arm, so a
        # sentence that denies a Swiss peak win without naming the arm is the failure.
        ("Swiss peak denial names its arm",
         "CH wins the uncoupled H2 Push peak" if ch_wins_uncoupled else "CH wins none",
         # \b after the optional plural. Without it `scenarios?` matches the singular
         # INSIDE "scenarios", so the lookahead then inspects "s once ..." instead of
         # " once ...", the negative lookahead succeeds, and two correctly qualified
         # sentences were reported stale.
         [r"wins no Swiss (?:winter )?peak in any (?:of the four )?scenarios?\b"
          r"(?!\s+(?:once|on the|when|under the))",
          r"at the winter peak hydrogen loses everywhere"], ALL),
        # Slot form, not presence. A presence assertion on "cheaper in all 29" stayed
        # satisfied by the sensitivity appendix while the results section was broken to
        # 26, which is the same corpus-wide hole the peaker-ledger and network-bill
        # checks had, here inside a single manuscript. Match the SHAPE of the claim and
        # exclude only the right number, so every occurrence is checked.
        ("blue base-load count, flat gate", blue_flat_hp,
         [rf"cheaper in all (?!{blue_flat_hp}\b)\d+", ], ALL,
         {"working paper": rf"cheaper in all {blue_flat_hp}",
          "AE submission": r"removes hydrogen's advantage in all seven"}),
        ("blue base-load count, proportional", blue_prop_hp,
         [rf"(?:and )?in (?!{blue_prop_hp}\b)\d+ with Denmark",
          rf"in (?!{blue_prop_hp}\b)\d+ if the German figure"], ALL,
         {"working paper": rf"in {blue_prop_hp} with Denmark",
          "AE submission": r"Denmark alone holds"}),
        ("unit-commitment easing, hydrogen, bn", f"{uc_ease_h2:.1f}",
         [rf"(?:hydrogen by about|by about) (?:\\euro\{{\}}|EUR ?)?"
          rf"(?!{uc_ease_h2:.1f}(?![\d]))\d\.\d bn(?=(?:[^.]|\.\d){{0,60}}?"
          rf"(?:for hydrogen|and gas by))"], ALL),
        # The five dispatch-arena sensitivities were added after round 13's referees showed
        # that the sweeps in the paper were not the ones that can flip a count. Each is
        # recomputed by scripts.dispatch_arena_sensitivity and pinned here, because the
        # whole point of adding them is that a reader can check them.
        ("dispatch-arena last mile, charged counts", arena_lastmile,
         [r"of 29 to 0, (?!2, 7 and 14)\d+, \d+ and \d+, and the demand-weighted"], ALL,
         {"working paper": r"to 0, 2,\s*7 and 14",
          "AE submission": r"to 0, 2, 7 and 14"}),
        # normalise() turns `~` into a plain space, so every pattern here is written with
        # plain spaces. Writing `per~cent` matches nothing, which is how the first draft
        # of these two checks reported "asserted nowhere" against correct prose.
        ("dispatch-arena last mile, Stated ceiling", arena_lastmile_bound,
         # Anchor on "derived ceiling under Stated Policies", because the SCARCITY-PREMIUM
         # sensitivity legitimately moves the same 5.1 to 0.2 a few paragraphs away. An
         # unanchored "from 5.1 to ..." fired on that correct sentence.
         [rf"derived ceiling under Stated Policies from 5\.1 to "
          rf"(?!{arena_lastmile_bound})\d\.\d per cent"], ALL,
         {"working paper": r"derived ceiling under Stated Policies from 5\.1 to 0\.6 per cent",
          "AE submission": r"derived ceiling under Stated Policies from 5\.1 to 0\.6 per cent"}),
        # The stale pattern must be anchored tightly. An earlier version used
        # `Adding Iberia[^.]*gives (?!nine)\w+`, and the greedy run skipped over the
        # correct "gives nine" to match "gives six" later in the SAME sentence, so the
        # gate failed on prose that was right.
        ("cavern-set range, alternative readings", "nine",
         [r"including Iberia gives (?!nine\b)\w+",
          r"the source also maps, gives (?!nine\b)\w+"], ALL,
         {"working paper": r"the source also maps, gives nine",
          "AE submission": r"including Iberia gives nine"}),
        ("COP derate sweep, deep end H2 Push", cop_deep_h2p,
         [rf"and 0, 1, 7 and (?!{cop_deep_h2p}\b)\d+ at 0\.75"], ALL,
         {"working paper": rf"0, 1, 7 and {cop_deep_h2p} at 0\.75",
          "AE submission": rf"0, 1, 7 and {cop_deep_h2p} at 0\.75"}),
        # Both manuscripts now headline the symmetric quartet and print the asymmetric one
        # beside it, so each quartet needs its own anchor phrase. When they briefly shared
        # the anchor "hydrogen share of", this pair failed, correctly: one slot cannot hold
        # two values and be checkable.
        ("demand-weighted arena ceiling, symmetric basis", arena_bound_sym,
         [rf"puts the symmetric counts at (?!{_sym_lo} and {_sym_hi}\b)[\d., and]+per cent",
          rf"hydrogen share of (?!{_sym_lo} and {_sym_hi}\b)"
          rf"[\d., and]+per cent of useful heat"],
         SUBMISSION + LONG,
         {"AE submission": rf"puts the symmetric counts at {_sym_lo} and {_sym_hi} per cent",
          "working paper": rf"hydrogen share of {_sym_lo} and {_sym_hi} per cent of useful heat"}),
        # The sentence that opens the arena section. It survived the switch to symmetric
        # accounting still reading "to 16 of 29 countries at the building winter peak, 20
        # in district heating", while citing the very table that says 14 and seven, and
        # while its own next-but-one sentence said "the rise to 14 and seven". Every check
        # above passed, because each was anchored on a phrase this sentence does not use.
        # A slot is only covered if some pattern names it.
        ("arena section opening counts, symmetric basis", arena_lastmile,
         [r"win count rises with\s+carbon-pricing ambition in every arena, to "
          r"(?!14 of 29\b)\d+"],
         SUBMISSION,
         {"AE submission": r"in every arena, to 14 of 29\s+countries at the building "
                           r"winter peak, seven in district heating and seven"}),
        # The named winners, not only how many. A count and a country list can disagree
        # silently, and they did: the long paper carried the asymmetric pair (DE, FR, NL
        # and DK) while its count moved to the symmetric 2.
        ("building-peak winners under Stated Policies, symmetric basis", arena_win_sp,
         [rf"under Stated Policies \((?!{arena_win_sp}\))[A-Z, and]+\)"],
         LONG, {"working paper": rf"under Stated Policies \({arena_win_sp}\)"}),
        ("demand-weighted arena ceiling, earlier draft's basis", arena_bound_open,
         [rf"earlier draft's accounting gives (?!{_opn_lo} and {_opn_hi}\b)[\d., and]+\.",
          rf"against (?!{_opn_lo} and {_opn_hi}\b)[\d., and]+on the earlier draft's basis"],
         SUBMISSION + LONG,
         {"AE submission": rf"earlier draft's accounting gives {_opn_lo} and {_opn_hi}",
          "working paper": rf"against {_opn_lo} and {_opn_hi} on the earlier draft's basis"}),
        # Both manuscripts phrase the H2 Push count identically, so one pattern covers it.
        ("MC median convergence, H2 Push draws", mc_med.split(", ")[3],
         [rf"only after (?!{mc_med.split(', ')[3]}\b)\d+ under H2"], SUBMISSION + LONG,
         rf"only after {mc_med.split(', ')[3]} under H2 Push"),
        # The other three are worded differently in the two manuscripts, so the presence
        # half is per-manuscript while the stale half patterns each slot in both.
        ("MC median convergence, other three scenarios", mc_med.rsplit(", ", 1)[0],
         [rf"after (?!{mc_med.split(', ')[0]}\b)\d+, \d+ and \d+ draws under Current",
          rf"after \d+, (?!{mc_med.split(', ')[1]}\b)\d+ and \d+ draws under Current",
          rf"after \d+, \d+ and (?!{mc_med.split(', ')[2]}\b)\d+ draws under Current",
          rf"final value after (?!{mc_med.split(', ')[0]}\b)\d+ draws under Current",
          rf"Current Policies and (?!{mc_med.split(', ')[1]}\b)\d+ under Stated",
          rf"Stated Policies, after (?!{mc_med.split(', ')[2]}\b)\d+ under Net Zero"],
         SUBMISSION + LONG,
         {"AE submission": rf"after {mc_med.split(', ')[0]}, {mc_med.split(', ')[1]} and "
                           rf"{mc_med.split(', ')[2]} draws under Current",
          "working paper": rf"after {mc_med.split(', ')[0]} draws under Current Policies "
                           rf"and {mc_med.split(', ')[1]} under Stated Policies, after "
                           rf"{mc_med.split(', ')[2]} under Net Zero"}),
        ("MC decile convergence, last exit draw range", f"{mc_dec_lo} to {mc_dec_hi}",
         [rf"last leaves that tube at draw (?!{mc_dec_lo} to {mc_dec_hi}\b)\d+ to \d+",
          rf"last leaves that tube between draws (?!{mc_dec_lo} and {mc_dec_hi}\b)"
          rf"\d+ and \d+"],
         SUBMISSION + LONG,
         {"AE submission": rf"at draw {mc_dec_lo} to {mc_dec_hi} in all four scenarios",
          "working paper": rf"between draws {mc_dec_lo} and {mc_dec_hi} in all four "
                           rf"scenarios"}),
        # The four validation dispersion statistics. A referee supplied them from the CSV
        # and they were correct, but on the vintage-matched basis, while the counts and the
        # -0.8 per cent aggregate the same passage quotes are on the raw one. Typing them in
        # would have put two bases in one sentence with nothing to say so. Both bases are
        # derived in make_validation_table.error_metrics and both are quoted here, and each
        # slot below is patterned so a value that changes basis, drifts or disappears fails.
        ("validation MAPE, raw basis", val_mape,
         [rf"mean absolute deviation across the 29 countries is (?!{val_mape}\b)\d+\.\d"],
         SUBMISSION + LONG, rf"across the 29 countries is {val_mape}"),
        ("validation weighted MAPE, raw basis", val_wmape,
         [rf"demand-weighted mean (?!{val_wmape}\b)\d+\.\d"],
         SUBMISSION + LONG, rf"demand-weighted mean {val_wmape}"),
        ("validation RMSE, raw basis", val_rmse,
         [rf"root-mean-square deviation (?!{val_rmse}\b)\d+\.\d"],
         SUBMISSION + LONG, rf"root-mean-square deviation {val_rmse} percentage points"),
        ("validation median absolute error, raw basis", val_medae,
         [rf"median absolute deviation (?!{val_medae}\b)\d+\.\d"],
         SUBMISSION + LONG, rf"median absolute deviation {val_medae}"),
        # The vintage-matched quartet is quoted as a bare list, so it is checked as one slot.
        ("validation dispersion, vintage-matched basis", val_vm,
         [rf"the same four read (?!{val_vm.replace('.', chr(92) + '.')}\b)"
          rf"\d+\.\d, \d+\.\d, \d+\.\d and \d+\.\d"],
         SUBMISSION + LONG, rf"the same four read {val_vm.replace('.', chr(92) + '.')}"),
        # The two 2015 backcast gaps are checked per file by backcast_gaps_per_file() rather
        # than here. A corpus-wide tuple cannot express them: these documents legitimately
        # quote BOTH gaps in one passage in order to explain that they are different
        # constructions, so a stale-pattern half fires on correct prose, and a presence half
        # passes as soon as any one file is right.
    ]


def architecture_claims() -> list[str]:
    """No document may call the hydrogen share dispatch-derived, because it is not.

    Config sets h2_share_2050 to 0, 5, 3 and 8 per cent and Simulation samples around
    those settings; the merit-order screen supports 0, 0.6, 7.5 and 9.0. The two are
    different quantities and one does not produce the other. A code comment and a
    supplement paragraph both said it did, which is a claim about the architecture that
    the architecture does not support, and no numeric check could see it because no
    number was wrong. This one reads for the phrasing instead.
    """
    bad = re.compile(r"merit-order-derived|dispatch-derived (?:bound|share|ceiling)|"
                     r"derive(?:s|d)? (?:each )?scenario'?s? (?:hydrogen )?(?:share|ceiling)",
                     re.I)
    hits = []
    for f in ALL + [REPO / "code" / "src" / "Config.py",
                    REPO / "code" / "src" / "Simulation.py"]:
        if not f.exists():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if bad.search(line):
                hits.append(f"{f.relative_to(REPO)}:{i}: {line.strip()[:90]}")
    return hits


def figure_text_hardcodes() -> list[str]:
    """Figure text must not hard-code a number band. It is manuscript text and it drifts.

    This file's corpus was .tex plus a few .md, so text rendered INTO a figure by a Python
    generator was never checked against anything. The graphical abstract, which is page 1 of
    the submission, carried "EUR 31 to 69/kW-yr capacity payment" against the artefact's 31
    to 63, and against five agreeing instances elsewhere in the same paper. The 69 was not
    even the same quantity: it is the upper bound of the annualised capital over all seven
    cavern markets, two of which build nothing. Every check in this file passed throughout,
    because none of them could see it.

    Rather than try to match each band to the right artefact from outside the script, the rule
    is structural: a generator that states a range in its figure text has to compute it. A
    literal range in a string is the defect, whatever its value, because nothing keeps it
    honest. Ranges in comments are fine, and so are axis limits and other numeric arguments.
    """
    import ast
    out = []
    band = re.compile(r"(?:€|EUR\s?)\d[\d,.]*\s+to\s+(?:€|EUR\s?)?\d")
    # rglob, both trees. One level of code/scripts left country_build/ and every
    # module in the submission directory outside a scanner written because a
    # generator drew a wrong range onto page one of the submission.
    srcs = [f for d in (REPO / "code", REPO / "paper" / "ae_submission")
            for f in sorted(d.rglob("*.py")) if "__pycache__" not in f.parts]
    for py in srcs:
        if py.name.startswith("check_"):
            continue
        src = py.read_text()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        # Exclude docstrings by identity. A line-based filter that only strips "#" comments
        # flagged this very function's docstring, which quotes the bad band in order to
        # explain it, so the check reported a defect on the text describing the defect.
        docs = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)) and node.body:
                first = node.body[0]
                if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)):
                    docs.add(id(first.value))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and id(node) not in docs and band.search(node.value)):
                out.append(f"{py.relative_to(REPO)}:{node.lineno} hard-codes a currency "
                           f"range in figure text; derive it from the artefact: "
                           f"{node.value.strip()[:70]!r}")
    return out


def price_table() -> list[str]:
    """Check the fuel-price table against the prices the model actually charges.

    Three of its six rows had been left at the single EU-average values that per-country
    series replaced in May 2026 (oil 130, biomass 60, district heat 80, against means of
    154, 69 and 88), so a reader recomputing an average from the appendix could not
    reproduce the table. The other two rows are the Eurostat consumption-weighted
    aggregates, which are correct but differ from the unweighted mean, and that is now
    stated rather than left to be discovered.
    """
    import numpy as np
    from src.Economics import get_fuel_price
    import src.Config as C
    tex = REPO / "paper" / "sections" / "appendix_detail.tex"
    if not tex.exists():
        return []
    txt, _ = normalise(tex.read_text())
    # Scope to the table, not the file. "District heat" also heads a row of the technology
    # CAPEX table earlier in this appendix, and an unscoped search read 500 EUR/kW off that
    # one and reported the price table wrong.
    block = re.search(r"label\{tab:prices\}(.*?)\\bottomrule", txt)
    if not block:
        return ["tab:prices not found in appendix_detail.tex"]
    txt = block.group(1)
    rows = [("Natural gas", "gas"), ("Electricity", "electricity"),
            ("Heating oil", "oil"), ("Biomass", "biomass"),
            ("District heat", "district_heat"), ("Hydrogen", "hydrogen")]
    out = []
    for label, fuel in rows:
        mean = float(np.mean([get_fuel_price(fuel, c, 2025) for c in C.EU_COUNTRIES]))
        m = re.search(rf"{label}\s*&\s*(\d+)\s*&", txt)
        if not m:
            out.append(f"tab:prices has no {label} row")
        elif int(m.group(1)) != round(mean):
            out.append(f"tab:prices says {label} is {m.group(1)} EUR/MWh in 2025; the mean "
                       f"of the 29 per-country prices is {mean:.1f}")
    return out


def network_bill_splits() -> list[str]:
    """The bill's per-carrier split, which the totals check does not see.

    The totals were corrected and two split values in the same paragraph were left:
    Current Policies reinforcement at 59 against 61.6, and the Stated Policies low band at
    188 against 187.5. Assert the four electricity-reinforcement values and the four low
    bands directly.
    """
    ib = pd.read_csv(RESULTS / "infrastructure_bill.csv").groupby("scenario")[
        ["elec_bn_central", "total_bn_low"]].sum()
    out = []
    for f in ALL:
        if not f.exists():
            continue
        txt, lines = normalise(f.read_text())
        for s_, lbl in [("CURRENT_POLICIES", "Current Policies"),
                        ("STATED_POLICIES", "Stated Policies"),
                        ("NET_ZERO", "Net Zero"), ("H2_PUSH", "H2 Push")]:
            want = round(ib.loc[s_, "total_bn_low"])
            for m in re.finditer(rf"\[(\d{{3}}) to \d{{3}}\] under {lbl}", txt):
                if int(m.group(1)) != want:
                    out.append(f"{f.relative_to(REPO)}:{lines[m.start()]}  {lbl} low band "
                               f"reads {m.group(1)}, artefact is {want}")
    return out


def co2_table_reductions() -> list[str]:
    """Every reduction cell in the emissions table, against its own baseline.

    Three of twelve were truncated where the other nine rounded, which made the table
    inconsistent with itself and understated the pathway a reader is most likely to quote.
    """
    base = float(pd.read_csv(RESULTS / "mc_emissions_STATED_POLICIES.csv")
                 .query("variable == 'co2_MtCO2' and year == 2025").q50.iloc[0])
    want = {}
    for s_, lbl in [("CURRENT_POLICIES", "Current Policies"),
                    ("STATED_POLICIES", "Stated Policies"),
                    ("NET_ZERO", "Net Zero"), ("H2_PUSH", "H2 Push")]:
        d = pd.read_csv(RESULTS / f"mc_emissions_{s_}.csv")
        d = d[d.variable == "co2_MtCO2"]
        want[lbl] = [round(100 * (float(d[d.year == y].q50.iloc[0]) - base) / base)
                     for y in (2030, 2040, 2050)]
    out = []
    for f in ALL:
        if not f.exists():
            continue
        txt, lines = normalise(f.read_text())
        for lbl, w in want.items():
            m = re.search(rf"{lbl} *& *[\d~]+ *& *\$?-(\d+)\\?% *\$? *& *[\d~]+ *& *"
                          rf"\$?-(\d+)\\?% *\$? *& *[\d~]+ *& *\$?-(\d+)", txt)
            if not m:
                continue
            got = [-int(m.group(i)) for i in (1, 2, 3)]
            if got != w:
                out.append(f"{f.relative_to(REPO)}:{lines[m.start()]}  {lbl} reductions "
                           f"read {got}, artefact gives {w}")
    return out


def network_bill_values() -> list[str]:
    """Every 'EUR NNN bn under <scenario>' that is a network bill must be right.

    The whole series went stale in the working paper while the submission was propagated,
    across four files and fifteen values, with the figure beside the prose already
    regenerated on the new CSV.

    Four slot designs failed here before this one, each by matching correct text. Keyed on
    the scenario name it hit the peaker-shortfall ledger, which quotes three-digit bn
    figures under the same four scenario names. Keyed on a network word with a forward
    window it skipped the correct value and matched the next scenario's. Keyed on the label
    that follows the value it still hit "563 bn under Current Policies", which is the
    shortfall. Keyed on the enclosing sentence, and then on a 900-character window after a
    bill phrase, it read the working paper and skipped the submission, whose SI states the
    totals a full paragraph after the subsection names the bill.

    So invert the scope. Match every "NNN bn under <scenario>" in the corpus and exclude
    only those whose neighbourhood names the peaker, the shortfall or capital. What
    remains is a network bill wherever it is stated and however the sentence is built,
    which is what makes this survive a rewrite of the prose around it.

    The presence assertion counts per manuscript. A corpus-wide counter stays satisfied
    while one manuscript keeps a matching sentence, so an edit that reshapes the other
    manuscript's copy out of the pattern drops it from coverage in silence.
    """
    ib = pd.read_csv(RESULTS / "infrastructure_bill.csv").groupby("scenario")[
        "total_bn_central"].sum()
    want = {"Current Policies": ib["CURRENT_POLICIES"],
            "Stated Policies": ib["STATED_POLICIES"],
            "Net Zero": ib["NET_ZERO"], "H2 Push": ib["H2_PUSH"]}
    val = re.compile(r"(?<![\d.])(\d{3})(?:\.\d+)? bn(?: \[[^\]]*\])? under "
                     r"(Current Policies|Stated Policies|Net Zero|H2 Push)")
    # The peaker ledger, its scenario sweep and the capital-recovery passages are the only
    # other places that write a three-digit bn figure under these four names.
    peaker_ctx = re.compile(r"peaker|shortfall|loses|missing.money|capital", re.I)
    groups = {"AE submission": SUBMISSION, "working paper": LONG,
              "reproduction docs": DOCS}
    fails, seen = [], dict.fromkeys(groups, 0)
    for label, files in groups.items():
        for f in files:
            if not f.exists():
                continue
            txt, lines = normalise(f.read_text())
            for m in val.finditer(txt):
                if peaker_ctx.search(txt[max(0, m.start() - 320):m.end() + 120]):
                    continue
                seen[label] += 1
                got, lbl = int(m.group(1)), m.group(2)
                if got != round(want[lbl]):
                    fails.append(f"{f.relative_to(REPO)}:{lines[m.start()]}  network bill "
                                 f"under {lbl} reads {got} bn, artefact is "
                                 f"{round(want[lbl])} bn")
    # The reproduction docs are not required to restate the totals, so they are checked
    # when present and never asserted absent.
    for label in ("AE submission", "working paper"):
        if not seen[label]:
            fails.append(f"the {label} states no network-bill scenario total in a shape "
                         f"this reads; the four totals are asserted nowhere in it")
    return fails


def peaker_ledger_sentences() -> list[str]:
    """The headline shortfall sentence must carry the reduced-form pair.

    A corpus-wide value check cannot express this. Three shortfall series legitimately
    appear in these documents (reduced form, unit commitment with constraints off, and
    with them on), and so do a scenario sweep and a district-heat-credited band, so any
    bare "EUR NNN bn near the word peaker" pattern fires on correct prose: it flagged the
    CHP-credited 343 to 350 bn and the 125 to 134 bn gas band on its first run.

    Match the headline SENTENCE instead, the one that pairs the two fleets, and assert
    both numbers in it. The reduced form is the right pair there because it is the
    dispatch that also gives the 278 GW and the 139 hours the same passages quote. The
    working paper had the unit-commitment limit case in this slot and so read 358/143
    where the submission read 357/142.

    The presence assertion is per manuscript, not corpus-wide. A single corpus-wide
    counter stays satisfied as soon as one document still carries the sentence, and a
    redundancy edit to the working paper duly reshaped its copy out of the pattern while
    the submission kept the gate quiet. Each manuscript must carry the sentence somewhere.

    Scoping the presence test on the topic instead ("a cumulative 2050 loss") was tried
    and is wrong: the network-infrastructure bill is also cumulative to 2050, so it fires
    on three files that never discuss the peaker.
    """
    (h2, gas), _, _ = peaker_ledgers()
    want_h2, want_gas = abs(h2), abs(gas)
    # normalise() strips $ and turns ~ into a space, but \euro{} survives it. The two
    # documents differ over whether either figure carries "about", over whether the loss
    # is written as a bare magnitude or with an explicit minus, and over whether it is
    # rounded (357) or carried to one decimal (357.3), so the comparison is numeric.
    eur = r"(?:\\euro\{\}|EUR ?)?"
    sign = r"(?:[-\u2212] ?)?"
    pat = re.compile(
        rf"peaker loses (?:about )?{sign}{eur}([\d.]+) bn against "
        rf"(?:about )?{sign}{eur}([\d.]+) bn", re.I)
    # 0.5 bn separates the reduced form from both unit-commitment series on the hydrogen
    # figure (357.3 against 358.4 and 356.0). It does not separate them on the gas figure
    # (142.4 against 142.3), which is why both members of the pair must match.
    tol = 0.5
    out = []
    groups = {"AE submission": SUBMISSION, "working paper": LONG}
    for label, files in groups.items():
        found = 0
        for f in files:
            if not f.exists():
                continue
            txt, lines = normalise(f.read_text())
            for m in pat.finditer(txt):
                found += 1
                got_h2, got_gas = float(m.group(1)), float(m.group(2))
                if abs(got_h2 - want_h2) > tol or abs(got_gas - want_gas) > tol:
                    out.append(f"{f.relative_to(REPO)}:{lines[m.start()]}  headline "
                               f"shortfall reads {got_h2}/{got_gas} bn, reduced form is "
                               f"{want_h2:.1f}/{want_gas:.1f} bn")
        if not found:
            out.append(f"the {label} carries no headline sentence pairing the two peaker "
                       f"fleets; the reduced-form pair {want_h2:.1f}/{want_gas:.1f} bn is "
                       f"asserted nowhere in it")
    return out


def backcast_gaps_per_file() -> list[str]:
    """Every document that discusses a 2015 backcast gap must carry the live figure.

    A corpus-wide presence assertion passes as soon as ONE file states the right value, so it
    misses the mixed case: the artefact moves, one document is updated and another keeps the
    old number. That is close to what happened here. Reading it per file catches it, and it
    stays quiet on files that never raise the subject.
    """
    _ld = pd.read_csv(RESULTS / "lmdi_design.csv")
    lmdi = float(_ld.loc[_ld.country == "EU", "gap_2015_vs_hotmaps_pct"].iloc[0])
    _rb = pd.read_csv(RESULTS / "reconcile_backcast.csv")
    vm = float(_rb[_rb.country == "EU(sum)"].iloc[0].vintage_matched_gap_pct)
    # Anchored on the artefact name as well as the prose phrasing. Keyed on the phrase alone,
    # this missed the root REPRODUCE.md, which writes "`lmdi_design.csv` backcasts the whole
    # design decomposition" and never the words "LMDI backcast".
    # The trigger has to name the BASIS, not the subject. Widening this check from the
    # reproduction docs to every document made it fire on both manuscripts, which discuss
    # the vintage-matched backcast on the all-class validation basis and correctly carry
    # -8.3, against this check's -8.5 from the raw-Hotmaps reconciliation basis. Two
    # bases, two figures, one phrase: the check was demanding the wrong one of the two.
    topics = [("LMDI design backcast", r"lmdi_design|LMDI (?:design )?backcast|design backcast",
               lmdi),
              ("stock-only vintage-matched backcast",
               r"reconcile_backcast|reconciliation backcast", vm)]
    out = []
    for f in ALL:
        if not f.exists():
            continue
        txt, _ = normalise(f.read_text())
        for name, topic, val in topics:
            if re.search(topic, txt, re.I) and not re.search(num(val), txt):
                out.append(f"{f.relative_to(REPO)} discusses the {name} but never states "
                           f"its current value, {val:.1f}%")
    return out


def si_figure_pointers() -> list[str]:
    """Cross-check the SI's "Figure n of the main text" pointers against V5.aux.

    The SI cites main-text figures by NUMBER, because the two documents compile
    separately and LaTeX cannot resolve a label across them. Inserting one figure in the
    body therefore silently redirects every SI pointer after it. That happened when the
    NUTS3 map went in as Fig. 2: four pointers began naming the figure before the one
    they describe, which sends a reader to a real figure about the wrong thing. V5.aux
    is the authority. Each pointer is keyed to the label its surrounding sentence is
    about, so the check fails on a wrong number and not merely on a changed one.
    """
    aux = REPO / "paper" / "ae_submission" / "V5.aux"
    si = [REPO / "paper" / "ae_submission" / "si_body" / n
          for n in ("methods.tex", "results.tex")]
    if not aux.exists():
        # Not a skip. paper/ae_submission/*.aux is gitignored, so on a fresh clone
        # this returned [] and the gate printed a pass with every pointer
        # assertion in this function silently disabled. A check that cannot reach
        # its inputs has not verified anything, and must say so.
        return [f"{aux.relative_to(REPO)} is absent, so no pointer in this check "
                f"was evaluated. Build the documents first (the .aux is a build "
                f"product and is not committed)."]
    label_to_num = dict(re.findall(r"newlabel\{(fig:[a-z0-9_]+)\}\{\{(\d+)\}",
                                  aux.read_text()))
    # the sentence phrase that identifies which body figure each SI pointer means
    # "feeding the pipeline of Fig" was a second key on fig:arch. The two SI sentences it
    # and the key above guarded were merged into one, so it matched nothing and, because
    # the presence test was keyed by label rather than by phrase, its live sibling kept it
    # disarmed and the gate reported a pass on a check that had stopped running.
    expect = {"The architecture is demand-first": "fig:arch",
              "falls from 40~per~cent to zero at the median under Net": "fig:mix",
              "with district heat cheaper than either": "fig:lcoh",
              # The sentence carrying this pointer reports the EUR167 to 184/MWh-e spread
              # across the seven cavern markets and the EUR72 to 89 margins, which is the
              # cavern-market figure. It was keyed to fig:merit, the single-country Denmark
              # ladder, so the gate actively defended a pointer that sent the reader to a
              # figure showing one market when the sentence is about seven.
              "The dispatchable-tip ordering therefore flips sign": "fig:cavern",
              "The seven winning markets are precisely the salt-cavern countries": "fig:cavern",
              "reaches \\euro{}165.9/MWh in 2050": "fig:swiss"}
    # Keyed by PHRASE, not by label. Four of the seven keys share a label, so a
    # label-keyed set let a dead key be disarmed by a live sibling: the key
    # "feeding the pipeline of Fig" matched nothing in the SI, fig:arch was in
    # `seen` because its other key matched, and the check reported a pass on a key
    # that had silently stopped running. That is the exact failure the comment
    # below claims was closed, still open one level up.
    bad, seen, matched = [], set(), set()
    for f in si:
        if not f.exists():
            continue
        raw = f.read_text()
        # Scan a WHITESPACE-NORMALISED copy, because "Figure~5 of the main\ntext" wraps
        # across a line break and a line-by-line scan cannot see it. The first version of
        # this check was line-based and missed exactly one of the five stale pointers for
        # that reason, which is how the defect survived a pass that reported itself clean.
        flat = " ".join(raw.split())
        offsets = []              # flat-index -> source line, for a usable message
        line = 1
        for ch in raw:
            if ch.isspace():
                if ch == "\n":
                    line += 1
                if offsets and offsets[-1][1] == " ":
                    continue
                offsets.append((line, " "))
            else:
                offsets.append((line, ch))
        for phrase, label in expect.items():
            fphrase = " ".join(phrase.split())
            start = flat.find(fphrase)
            if start < 0:
                # A key that no longer matches disarms its own check. That happened:
                # rewording a caption silently switched off the very pointer this gate
                # was written to protect, and the gate went on reporting a pass. An
                # unmatched key is now a failure, so the prose and the gate cannot drift
                # apart quietly.
                continue
            seen.add(label)
            matched.add(phrase)
            want = label_to_num.get(label)
            # the pointer sits in the same sentence, so look a little either side
            window = flat[max(0, start - 200):start + 400]
            m = re.search(r"Fig(?:ure)?\.?~?(\d+) of the main text", window)
            src = offsets[start][0] if start < len(offsets) else 0
            if want and m and m.group(1) != want:
                bad.append(f"{f.relative_to(REPO)}:{src} says Figure {m.group(1)} "
                           f"for {label}, V5.aux says {want}")
    for phrase, label in expect.items():
        if phrase not in matched:
            bad.append(f"key for {label} matched nothing: {phrase!r}. Reword the key to "
                       f"the sentence's current wording, or this check does not run.")
    return bad


def main_to_si_table_pointers() -> list[str]:
    """Cross-check the main text's "Supplementary Table Sn" pointers against SI.aux.

    The sibling of si_figure_pointers, in the other direction and for tables. Reordering
    one SI float renumbers every table after it, and the body hard-codes the numbers
    because the two documents compile separately. That happened while the SI tables were
    being put into citation order: a caption that had just been given "Table S6" was
    pointing at the arenas table, which the reorder had made S5. Each pointer is keyed to
    the label its sentence is about, so this fails on a wrong number and not on a changed
    one.
    """
    aux = REPO / "paper" / "ae_submission" / "SI.aux"
    body = [REPO / "paper" / "ae_submission" / "sections" / n
            for n in ("methods.tex", "results.tex", "intro.tex", "concl.tex")]
    if not aux.exists():
        # Not a skip. paper/ae_submission/*.aux is gitignored, so on a fresh clone
        # this returned [] and the gate printed a pass with every pointer
        # assertion in this function silently disabled. A check that cannot reach
        # its inputs has not verified anything, and must say so.
        return [f"{aux.relative_to(REPO)} is absent, so no pointer in this check "
                f"was evaluated. Build the documents first (the .aux is a build "
                f"product and is not committed)."]
    label_to_num = dict(re.findall(r"newlabel\{(tab:[a-z0-9_]+)\}\{\{S(\d+)\}",
                                   aux.read_text()))
    # Two keys guarded two of the five pointers the body actually makes. The other three
    # were correct and unguarded, which is the state the two guarded ones were in when
    # one of them went wrong. Every pointer now has a key.
    expect = {"per-arena detail is in": "tab:arenas",
              "repeats the levers": "tab:scenarios",
              "since hydrogen still competes in the large north-western markets":
                  "tab:lcoh_by_country",
              "does not displace the electricity reinforcement it still requires":
                  "tab:infra_bill",
              "the assumed event length alone carries": "tab:hp_flex",
              "closes the gap for the winning peakers": "tab:capacity_payment"}
    # The plural form, which the single-table pattern cannot see: "Tables~S9 and~S10"
    # is one pointer naming two labels, and the second was invisible to the check.
    expect_second = {"the assumed event length alone carries": "tab:snap_duration"}
    # Phrase-keyed, matching its sibling. Two keys sharing a label let a dead
    # key be disarmed by a live one; safe here today only because the two keys
    # carry two labels, which is a coincidence and not a guarantee.
    bad, seen, matched = [], set(), set()
    for f in body:
        if not f.exists():
            continue
        flat = " ".join(f.read_text().split())
        for phrase, label in expect.items():
            start = flat.find(" ".join(phrase.split()))
            if start < 0:
                continue
            seen.add(label)
            matched.add(phrase)
            want = label_to_num.get(label)
            # Both directions. The window used to run forward from the key phrase only,
            # and one of the two original pointers reads "Table~S4 repeats the levers
            # with the derived bounds", so its number sits BEFORE its key. The forward
            # window found no pointer, the match came back None, and the check silently
            # did nothing. Its key matched, so it never reported "matched nothing"
            # either: it had been half dead since it was written, and a break test that
            # walked the five forward pointers did not touch it.
            window = flat[max(0, start - 260):start + 260]
            m = re.search(r"Tables?~?S(\d+)(?:\s+and~?S(\d+))?", window)
            if want and not m:
                # A key that matches prose containing no pointer at all is a dead key,
                # not a pass. This is the half that made the defect invisible.
                bad.append(f"{f.relative_to(REPO)}: key for {label} matched prose that "
                           f"names no Supplementary Table. Re-key it to the sentence "
                           f"that carries the pointer.")
            if want and m and m.group(1) != want:
                bad.append(f"{f.relative_to(REPO)} says Supplementary Table S{m.group(1)} "
                           f"for {label}, SI.aux says S{want}")
            second = expect_second.get(phrase)
            if second:
                want2 = label_to_num.get(second)
                seen.add(second)
                if want2 and m and m.group(2) != want2:
                    bad.append(f"{f.relative_to(REPO)} says Supplementary Table "
                               f"S{m.group(2)} for {second}, SI.aux says S{want2}")
    for phrase, label in expect.items():
        if phrase not in matched:
            bad.append(f"key for {label} matched nothing: {phrase!r}. Reword the key to "
                       f"the sentence's current wording, or this check does not run.")
    return bad


def si_table_numbers() -> list[str]:
    """Cross-check REPRODUCE.md's "SI Table Sn" pointers against SI.aux.

    Inserting one table renumbers every table after it, and the reproduction guide
    hard-codes the numbers. That happened the first time a table was added: three
    pointers silently began naming the wrong table, which is worse than a stale value
    because it sends a reader somewhere plausible. LaTeX resolves the labels, so the
    .aux file is the authority; this reads it and reports any pointer that no longer
    matches the label the surrounding text is about.
    """
    aux = REPO / "paper" / "ae_submission" / "SI.aux"
    repro = REPO / "paper" / "ae_submission" / "REPRODUCE.md"
    if not aux.exists() or not repro.exists():
        missing = [str(x.relative_to(REPO)) for x in (aux, repro) if not x.exists()]
        return [f"{', '.join(missing)} absent, so no reproduction-guide pointer "
                f"was evaluated. Build the documents first."]
    # [a-z0-9_], matching both siblings. Without the digits tab:co2 could never resolve.
    label_to_num = dict(re.findall(r"newlabel\{(tab:[a-z0-9_]+)\}\{\{(S\d+)\}",
                                   aux.read_text()))
    # which label each REPRODUCE row's pointer is about, keyed by a phrase in that row
    # Four keys guarded four of the six pointers the guide makes. The other two were
    # correct and unguarded, which is the state main_to_si_table_pointers was in when
    # one of its two went wrong.
    expect = {"count holds at seven": "tab:cavern_sweep",
              "partially flexible heat-pump load": "tab:hp_flex",
              "cold-and-still event": "tab:snap_duration",
              "fossil-phaseout ambition": "tab:sens_econ",
              "Dispatch-arena sensitivities": "tab:arenas",
              "Seasonal-storage classification": "tab:storage_geology"}
    # Scan the whole file whitespace-flattened, as si_figure_pointers does. A line-based
    # scan could not see the cavern-sweep row, whose key phrase sits on one source line
    # and whose "(SI Table S14)" pointer sits two lines below, so that key had never once
    # been evaluated and breaking the pointer left the gate green.
    flat = " ".join(repro.read_text().split())
    bad, matched = [], set()
    for phrase, label in expect.items():
        start = flat.find(" ".join(phrase.split()))
        if start < 0:
            continue
        matched.add(phrase)
        want = label_to_num.get(label)
        m = re.search(r"SI Table (S\d+)", flat[start:start + 400])
        if want and m and m.group(1) != want:
            bad.append(f"REPRODUCE.md says {m.group(1)} for {label}, SI.aux says {want}")
    # An unmatched key disarms its own check, which is what happened to the sibling.
    for phrase, label in expect.items():
        if phrase not in matched:
            bad.append(f"REPRODUCE.md key for {label} matched nothing: {phrase!r}. "
                       "Reword it to the row's current wording, or it does not run.")
    return bad


def normalise(txt: str) -> tuple[str, list[int]]:
    """Flatten LaTeX source so a pattern written as one phrase matches the wrapped text.

    This guard shipped with a hole that a referee found before we did. Every pattern here
    is a literal phrase, but LaTeX source wraps at column ~80, so "from 8.6 to about 51"
    sits in the file as "from 8.6 to about\n51" and the regex misses it. The same class of
    miss hides `$280$~GW` from a pattern written `280~GW`, because the prose puts the
    number in math mode. Three stale figures survived a full sweep that way.

    A third variant defeated it again after the first repair: `~` is a non-breaking space
    in LaTeX but not whitespace to Python, so a document writing `32~per cent` and one
    writing `32~per~cent` are the same sentence to a reader and different strings to a
    regex. Four stale instances hid in that gap. So `~` is normalised to a space too, and
    patterns should be written with plain spaces.

    A fourth: Markdown prose uses the typographic minus U+2212 where a pattern built by
    num() writes an ASCII hyphen, so a correctly stated negative value read as absent.
    Fold it to the hyphen.

    So: treat `~` as a space, fold the typographic minus to a hyphen, collapse every
    whitespace run to a single space, and drop the `$` delimiters that only mark math. Return the flattened text alongside a
    map from each flattened offset back to its source line, so a hit still reports the
    line a human can open.
    """
    out, lines, line = [], [], 1
    prev_space = False
    for ch in txt:
        if ch == "\n":
            line += 1
        if ch == "$":                      # math delimiter, never part of a phrase
            continue
        if ch.isspace() or ch == "~":      # `~` is a LaTeX space, not a character
            if prev_space:
                continue
            out.append(" "); lines.append(line); prev_space = True
        else:
            # U+2212 in prose against an ASCII hyphen in every num() pattern: a correctly
            # stated negative read as absent, which is the same normalisation class as the
            # `~` hole above.
            out.append("-" if ch == "\u2212" else ch)
            lines.append(line); prev_space = False
    return "".join(out), lines


MANUSCRIPTS = (
    ("working paper", REPO / "paper"),
    ("AE submission", REPO / "paper" / "ae_submission"),
)


def _by_manuscript(files):
    """Group a check's files by the manuscript they belong to.

    A presence assertion evaluated with any() over the whole corpus is satisfied by a
    single correct occurrence anywhere, which is how a value can go wrong in five of six
    places and still pass. Grouping makes each manuscript answer for its own text.

    Three buckets, not two. Bucketing on "ae_submission in parts" alone filed the
    reproduction guide, the README and the 22 literature notes as the working paper, so a
    correct string in one literature note satisfied a presence assertion that every
    working-paper section failed. network_bill_values() already groups three ways with
    these labels; this makes the tuple path agree with it.
    """
    # The reproduction guide and the cover letter live under ae_submission/ and were
    # therefore filed as the manuscript. They are not the manuscript. Breaking both of
    # the supplement's statements of the cavern storage charge escaped, because
    # REPRODUCE.md held the AE bucket's presence assertion up on its own. That is the
    # same defect as the literature-note one this function was written to close, one
    # boundary further in. A reproduction document describes the manuscript; it cannot
    # stand in for it.
    ae = [f for f in files if "ae_submission" in f.parts and f.suffix == ".tex"]
    docs = [f for f in files if f not in ae and (f in DOCS or f.suffix == ".md")]
    long = [f for f in files if f not in ae and f not in docs]
    return [(label, group) for label, group in
            (("working paper", long), ("AE submission", ae), ("reproduction docs", docs))
            if group]


SITES_FILE = REPO / "code" / "results" / "presence_sites.json"


def _load_sites() -> dict:
    """Recorded occurrence counts, keyed (claim, manuscript).

    Recorded rather than declared, so the contract costs nothing to maintain and cannot
    drift from the corpus by neglect. Regenerate deliberately with --record-sites after
    a change that legitimately moves a count, and the diff shows what moved.
    """
    if not SITES_FILE.exists():
        return {}
    return {tuple(k.split("\u0000")): v for k, v in
            json.loads(SITES_FILE.read_text()).items()}


def main() -> int:
    fails = []
    SITES = _load_sites()
    observed = {}
    print("Manuscript numbers against their artefacts\n")
    checks = build_checks()
    corpus = {f: normalise(f.read_text()) for f in ALL if f.exists()}
    for check in checks:
        claim, value, stale_patterns, files = check[:4]
        present = check[4] if len(check) > 4 else None
        hits = []
        for f in files:
            txt, linemap = corpus.get(f, ("", []))
            for pat in stale_patterns:
                for m in re.finditer(pat, txt):
                    line = linemap[m.start()] if m.start() < len(linemap) else 0
                    hits.append(f"{f.relative_to(REPO)}:{line}  {m.group(0)!r}")
        missing, miscount = [], []
        if present:
            # Per-manuscript, not corpus-wide. A referee showed that with `any()` over the
            # whole corpus, five of six occurrences of a value could be wrong and the check
            # still passed on the sixth. Each manuscript that carries files for this claim
            # must assert the right value in its own text.
            #
            # `present` may be a dict keyed by manuscript label where the two documents
            # word the same claim differently, or where only one of them makes it. A label
            # absent from the dict carries no assertion, which is how a claim that lives in
            # one manuscript alone is expressed.
            for label, group in _by_manuscript(files):
                pat = present.get(label) if isinstance(present, dict) else present
                if pat is None:
                    continue
                # A bare string means "each MANUSCRIPT must carry this". The reproduction
                # docs are a separate bucket so that a value in a literature note cannot
                # satisfy a manuscript's assertion; they are not themselves required to
                # restate every manuscript number. Assert against them only when a dict
                # names them.
                if label == "reproduction docs" and not isinstance(present, dict):
                    continue
                # Count, do not any(). A value stated in six places inside one manuscript
                # was protected by an assertion one correct occurrence satisfied, so
                # corrupting the other five passed: rewriting 278 to 279 at a single SI
                # site shipped green while the same edit at every site failed. Presence
                # was detecting disappearance, not corruption, and the skill's own wording
                # ("require the correct value to appear somewhere") is what specified the
                # weaker contract.
                #
                # The count is recorded on first run rather than declared by hand, in
                # SITES below, so a check gains the contract without anyone maintaining a
                # number. A drop means a site went stale or vanished. A rise means the
                # value was typed into a slot that should have referred back to it, which
                # is how a headline number acquires a second, unmaintained home.
                n = sum(len(re.findall(pat, corpus.get(f, ("", []))[0])) for f in group)
                want_n = SITES.get((claim, label))
                if n == 0:
                    missing.append((label, pat, 0, want_n))
                elif want_n is not None and n != want_n:
                    miscount.append((label, pat, n, want_n))
                observed[(claim, label)] = n
        ok = not hits and not missing and not miscount
        print(f"  [{'ok ' if ok else 'FAIL'}] {claim:38s} artefact = {value}")
        for h in hits:
            print(f"          stale: {h}")
        for label, pat, _n, _w in missing:
            print(f"          absent: nothing in the {label} matches {pat!r}; "
                  f"the right value is asserted nowhere in it")
        for label, pat, n, want_n in miscount:
            print(f"          count: the {label} states {pat!r} {n} time(s), "
                  f"against {want_n} recorded. A drop means a site went stale; "
                  f"a rise means the value acquired a second home.")
        if hits or missing or miscount:
            fails.append(claim)

    for msg in network_bill_splits() + co2_table_reductions():
        fails.append(msg)
        print(f"  [FAIL] {msg}")

    for msg in network_bill_values():
        fails.append(msg)
        print(f"  [FAIL] {msg}")

    for msg in peaker_ledger_sentences():
        fails.append(msg)
        print(f"  [FAIL] {msg}")

    for msg in architecture_claims():
        print(f"  [FAIL] hydrogen share called dispatch-derived: {msg}")
        fails.append("architecture claim")
    for msg in backcast_gaps_per_file():
        print(f"  [FAIL] backcast gap: {msg}")
        fails.append("backcast gap")

    for msg in price_table():
        print(f"  [FAIL] price table: {msg}")
        fails.append("price table")

    for msg in figure_text_hardcodes():
        print(f"  [FAIL] figure text: {msg}")
        fails.append("figure text")

    for msg in si_table_numbers():
        print(f"  [FAIL] SI table pointer: {msg}")
        fails.append("SI table pointer")

    for msg in si_figure_pointers():
        print(f"  [FAIL] SI figure pointer: {msg}")
        fails.append("SI figure pointer")

    for msg in main_to_si_table_pointers():
        print(f"  [FAIL] main-text SI table pointer: {msg}")
        fails.append("main-text SI table pointer")

    if "--record-sites" in sys.argv:
        SITES_FILE.parent.mkdir(parents=True, exist_ok=True)
        SITES_FILE.write_text(json.dumps(
            {"\u0000".join(k): v for k, v in sorted(observed.items())},
            indent=1) + "\n", encoding="utf-8")
        print(f"\nrecorded {len(observed)} presence site-count(s) -> "
              f"{SITES_FILE.relative_to(REPO)}")
        return 0

    print()
    if fails:
        print(f"{len(fails)} claim(s) carry a value the artefacts no longer produce:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("Every checked claim matches the artefact that produces it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
