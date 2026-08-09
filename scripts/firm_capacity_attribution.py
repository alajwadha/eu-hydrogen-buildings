"""Attribute the firm peaking fleet's annual cost to heat, two ways.

The base-load comparison charges the heat pump for distribution reinforcement but not for
the firm generating capacity the same winter evenings call on. That asymmetry runs against
our own accounting, so the limitations quantify it, and until now the quantification was
hand arithmetic: no script produced the two adders or the counts that follow from them, and
a referee who tried to reproduce them found nothing in the repository that did. This script
closes that gap. It writes one row per attribution basis, and one row per country for the
counts, so every figure the limitations quote is checkable.

Two bases bracket the value. Pro rata charges heating its share of total electricity demand,
which is the defensible reading, since the fleet serves the whole load and heating is a
minority of it. Charging the fleet in full to the heat-pump load treats every megawatt of
firm capacity as built for electrified heat, which no one would argue, and is carried only
as an upper bound.

Run:  cd code && PYTHONPATH=. python -m scripts.firm_capacity_attribution
Out:  results/firm_capacity_attribution.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path(__file__).resolve().parents[1] / "results"


def _incremental_share():
    """Share of the firm peaking fleet that exists because heat is electrified.

    Runs the committed dispatch twice, once as published and once with the heat-pump
    share forced to zero, and differences the fleets. The rng is seeded once per country
    and consumed across every basis and year, exactly as power_dispatch.main() does; a
    fresh rng per call draws a different VRE sequence and does NOT reproduce the
    committed 277.7 GW, which is the trap this helper exists to avoid.
    """
    import numpy as np
    from scripts import power_dispatch as pdisp

    cap = pdisp.load_capacity()
    lp = pd.read_csv(RESULTS / "heat_load_profile.csv").set_index("country")
    mc = pd.read_csv(RESULTS / "mc_country_STATED_POLICIES.csv")
    countries = [c for c in cap if c in lp.index]

    def run(zero_hp):
        original = pdisp.annual_hp_share
        if zero_hp:
            pdisp.annual_hp_share = lambda *a, **k: 0.0
        total = 0.0
        try:
            for c in countries:
                rng = np.random.default_rng(pdisp.country_seed(c))
                for basis in pdisp.BASES:
                    for year in pdisp.YEARS:
                        d = pdisp.dispatch(c, year, "STATED_POLICIES", basis,
                                           cap, lp, mc, rng)
                        if basis == "total_elec" and year == 2050:
                            total += d["peaker_cap_gw"]
        finally:
            pdisp.annual_hp_share = original
        return total

    with_hp, without_hp = run(False), run(True)
    return (with_hp - without_hp) / with_hp, with_hp, without_hp


def main() -> int:
    cap = pd.read_csv(RESULTS / "capacity_payment.csv")
    disp = pd.read_csv(RESULTS / "power_dispatch_summary.csv")
    disp = disp[(disp.basis == "total_elec") & (disp.year == 2050)]
    den = pd.read_csv(RESULTS / "power_demand_denominator.csv")
    den = den[(den.scenario == "STATED_POLICIES") & (den.year == 2050)].iloc[0]
    gap = pd.read_csv(RESULTS / "h2_hp_gap.csv")

    fleet_gw = float(disp.peaker_cap_gw.sum())

    # The annualised charge is the turbine's, over the markets that actually build one.
    # Taking it over all seven cavern rows would include two that build nothing, and
    # taking it over all 29 would apply a range computed on a different population.
    built = cap[cap.peaker_cap_gw > 0]
    lo, hi = float(built.ann_capex_h2.min()), float(built.ann_capex_h2.max())

    bill_lo_bn = fleet_gw * lo / 1000.0
    bill_hi_bn = fleet_gw * hi / 1000.0

    # Heat-pump heat in 2050 is the Stated Policies heat-pump share of useful demand. The
    # denominator for the pro-rata share is the same 4,513 TWh the power block uses
    # throughout, so numerator and denominator come from one series.
    hp_elec_twh = float(den.hp_elec_twh)
    total_elec_twh = float(den.total_elec_twh)
    heat_share = hp_elec_twh / total_elec_twh

    mc = pd.read_csv(RESULTS / "mc_summary_STATED_POLICIES.csv")
    m = mc[(mc.year == 2050) & (mc.variable == "tech_share")]
    hp_share = float(m[m.tech.isin(["hp_air", "hp_ground"])].q50.sum() / m.q50.sum())
    # The variable is useful_heat_MWh, not useful_heat_twh. An earlier draft of this
    # script filtered on the latter, matched zero rows every run and fell through to a
    # hard-coded 3483.0 that happened to be right, so the very defect the script was
    # written to remove survived inside it. No fallback now: a missing input raises.
    dem = mc[(mc.year == 2050) & (mc.variable == "useful_heat_MWh")]
    if dem.empty:
        raise SystemExit("mc_summary_STATED_POLICIES.csv carries no useful_heat_MWh rows")
    heat_twh = float(dem.q50.sum()) / 1e6
    hp_heat_twh = hp_share * heat_twh

    full_lo = bill_lo_bn * 1e9 / (hp_heat_twh * 1e6)
    full_hi = bill_hi_bn * 1e9 / (hp_heat_twh * 1e6)
    pro_lo, pro_hi = heat_share * full_lo, heat_share * full_hi

    # Between the two sits the basis cost causation asks for. A peaking asset is built for
    # a peak, so the question is how much of the fleet exists BECAUSE heat is electrified,
    # which the dispatch answers directly: re-run it with the heat-pump load removed and
    # difference the fleets. Charging a capacity asset on a share of ANNUAL ENERGY is what
    # the pro-rata basis does, and it is why that basis returns 9.2% where the physical
    # driver is nearer 80% -- the cold snap collapses the COP exactly when demand peaks.
    #
    # The share is an ordering choice: it charges electrified heat as the LAST load added.
    # Adding it first would attribute far less. That ambiguity is intrinsic to marginal
    # cost allocation and the manuscript says so rather than pretending otherwise.
    inc_share, fleet_with, fleet_without = _incremental_share()
    inc_lo, inc_hi = inc_share * full_lo, inc_share * full_hi

    # The base-load count is the number of markets in which the best heat pump is cheaper
    # than the hydrogen boiler. Adding an adder to the heat pump's cost moves the gap by
    # that adder, so a country flips when its 2050 gap falls below it.
    def count(adder):
        return int((gap.gap_2050 > adder).sum())

    def flips(adder):
        f = gap[(gap.gap_2050 > 0) & (gap.gap_2050 <= adder)]
        return ",".join(sorted(f.country))

    rows = [
        dict(basis="fleet", fleet_gw=round(fleet_gw, 1),
             ann_charge_lo_eur_kw_yr=round(lo, 1), ann_charge_hi_eur_kw_yr=round(hi, 1),
             annual_bill_lo_bn=round(bill_lo_bn, 1), annual_bill_hi_bn=round(bill_hi_bn, 1),
             hp_heat_twh=round(hp_heat_twh, 0), heat_share_of_elec=round(heat_share, 4),
             adder_lo_eur_mwh="", adder_hi_eur_mwh="", count_lo="", count_hi="",
             flips_lo="", flips_hi=""),
        dict(basis="pro_rata", fleet_gw=round(fleet_gw, 1),
             ann_charge_lo_eur_kw_yr=round(lo, 1), ann_charge_hi_eur_kw_yr=round(hi, 1),
             annual_bill_lo_bn=round(bill_lo_bn, 1), annual_bill_hi_bn=round(bill_hi_bn, 1),
             hp_heat_twh=round(hp_heat_twh, 0), heat_share_of_elec=round(heat_share, 4),
             adder_lo_eur_mwh=round(pro_lo, 1), adder_hi_eur_mwh=round(pro_hi, 1),
             count_lo=count(pro_lo), count_hi=count(pro_hi),
             flips_lo=flips(pro_lo), flips_hi=flips(pro_hi)),
        dict(basis="incremental", fleet_gw=round(fleet_gw, 1),
             ann_charge_lo_eur_kw_yr=round(lo, 1), ann_charge_hi_eur_kw_yr=round(hi, 1),
             annual_bill_lo_bn=round(bill_lo_bn, 1), annual_bill_hi_bn=round(bill_hi_bn, 1),
             hp_heat_twh=round(hp_heat_twh, 0), heat_share_of_elec=round(inc_share, 4),
             adder_lo_eur_mwh=round(inc_lo, 1), adder_hi_eur_mwh=round(inc_hi, 1),
             count_lo=count(inc_lo), count_hi=count(inc_hi),
             flips_lo=flips(inc_lo), flips_hi=flips(inc_hi)),
        dict(basis="full", fleet_gw=round(fleet_gw, 1),
             ann_charge_lo_eur_kw_yr=round(lo, 1), ann_charge_hi_eur_kw_yr=round(hi, 1),
             annual_bill_lo_bn=round(bill_lo_bn, 1), annual_bill_hi_bn=round(bill_hi_bn, 1),
             hp_heat_twh=round(hp_heat_twh, 0), heat_share_of_elec=round(heat_share, 4),
             adder_lo_eur_mwh=round(full_lo, 1), adder_hi_eur_mwh=round(full_hi, 1),
             count_lo=count(full_lo), count_hi=count(full_hi),
             flips_lo=flips(full_lo), flips_hi=flips(full_hi)),
    ]
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "firm_capacity_attribution.csv", index=False)

    print("Firm-capacity attribution to heat")
    print(f"  fleet                {fleet_gw:.1f} GW at "
          f"EUR{lo:.1f} to {hi:.1f}/kW-yr = EUR{bill_lo_bn:.1f} to {bill_hi_bn:.1f} bn/yr")
    print(f"  heat-pump heat 2050  {hp_heat_twh:.0f} TWh "
          f"({100*hp_share:.1f}% of {heat_twh:.0f} TWh)")
    print(f"  heating share of elec {100*heat_share:.1f}% "
          f"({hp_elec_twh:.0f} of {total_elec_twh:.0f} TWh)")
    print(f"  pro rata             EUR{pro_lo:.1f} to {pro_hi:.1f}/MWh, "
          f"count {count(pro_lo)} then {count(pro_hi)} of 29")
    print(f"  incremental          {100*inc_share:.1f}% of the fleet "
          f"({fleet_with:.1f} GW with heat pumps, {fleet_without:.1f} without), "
          f"EUR{inc_lo:.1f} to {inc_hi:.1f}/MWh, "
          f"count {count(inc_lo)} then {count(inc_hi)} of 29")
    print(f"    flips at the low bound  {flips(inc_lo)}")
    print(f"  charged in full      EUR{full_lo:.1f} to {full_hi:.1f}/MWh, "
          f"count {count(full_lo)} then {count(full_hi)} of 29")
    print(f"    flips at the low bound  {flips(full_lo)}")
    print(f"    and in addition at high {flips(full_hi)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
