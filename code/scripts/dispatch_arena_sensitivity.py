"""The five choices that can move a dispatch-arena count, swept in one place.

Round 13's referees made the same criticism from three directions: the sensitivity
analysis is extensive, but the parameters it sweeps are not the ones that can flip a
headline. The storage-adder sweep scales cavern and non-cavern in lockstep at a fixed
2.0 ratio, so it cannot test the split that produces the result. The scarcity-premium
sweep was reported only where it is an algebraic identity. Meanwhile the choices that
DO move the counts had never been swept at all.

This script sweeps them. Each block answers one question and writes one CSV block:

  pi_s          The scarcity premium. It cancels from the POWER arena, where the premium
                is added to whichever firm unit is marginal, so the seven is invariant
                across the whole EUR30 to 120/MWh-e band. It does NOT cancel from the
                BUILDING peak, because that is precisely the price the cold-snap heat
                pump is charged, at pi_peak / COP_cold. An earlier draft of the SI
                asserted that no reported count depends on it, which is false for that
                arena and is the error this block exists to prevent recurring.

  cop_derate    COP_cold = max(f * SCOP, floor). The published f = 0.60 with a 1.8 floor
                is calibrated to low-temperature field measurements, and the field
                evidence supports roughly 0.5 to 0.75. Never swept before this. It is the
                single largest lever on the building-peak count.

  cavern_set    CAVERN is a hard-coded seven-country set read off Caglayan et al. The
                power-arena win set is that list VERBATIM across the whole central band,
                so "seven" is an input reported as a result. Alternative readings of the
                same source (Iberia included; northern France only) give 9 and 6.

  h2_last_mile  The building-peak arena charges gas the Eurostat residential retail
                tariff, which carries network and taxes inside it, and charges hydrogen
                fuel plus seasonal storage with NO last-mile term -- while the paper's
                stated rule is that each carrier pays its own last mile. That rule holds
                in the base-load LCOH (Economics.compute_lcoh adds the adder) and is
                silently dropped here. Charging the model's own adder is the test.

  dh_gas_basis  The district-heat stack prices gas at the same residential retail tariff,
                where a district-heat operator buys wholesale. The count is a hydrogen-
                versus-gas comparison alone, so the electricity price the large heat pump
                pays cannot move it and the repricing is one-sided by construction.

Run:  cd code && PYTHONPATH=. python -m scripts.dispatch_arena_sensitivity
Out:  results/dispatch_arena_sensitivity.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RESULTS = Path(__file__).resolve().parents[1] / "results"


def _ctx():
    import scripts.merit_order_heat as moh
    import scripts.power_peak_price as ppp
    from src.Economics import (get_fuel_price, get_carbon_price, get_cop,
                               h2_distribution_adder_eur_mwh)
    lp = pd.read_csv(RESULTS / "heat_load_profile.csv").set_index("country")
    peak = pd.read_csv(RESULTS / "power_peak_price.csv")
    pt = {(r.country, r.scenario): r.peak_elec for _, r in peak.iterrows()}
    return moh, ppp, get_fuel_price, get_carbon_price, get_cop, \
        h2_distribution_adder_eur_mwh, lp, pt


def building_peak(premium=None, derate=(0.60, 1.8), h2_net=False, winners=None):
    """Counts and the demand-weighted derived ceiling, per scenario.

    premium=None uses the committed power_peak_price.csv; a number rebuilds the peak
    price at that scarcity premium so the sweep is on one lever at a time.

    Pass a dict as `winners` to receive the winning country codes per scenario. Both
    papers name the Stated Policies winners, and until this existed the names traced to
    nothing: the counts were persisted and the identities were not, so changing the
    headline accounting basis would silently have left a country list belonging to the
    other basis beside a count belonging to this one.
    """
    moh, ppp, fuel, carbon, cop_of, h2net, lp, pt = _ctx()
    frac, floor = derate
    add = {c: (h2net(c) if h2_net else 0.0) for c in lp.index}
    out = {}
    for s, lv in moh.SCEN.items():
        n, wt = 0, 0.0
        if winners is not None:
            winners[s] = []
        for c in lp.index:
            cp = carbon(2050, lv["carbon"])
            gasp = fuel("gas", c, 2050) / moh.ETA_GAS + cp * moh.EF_GAS / moh.ETA_GAS
            h2p = (fuel("hydrogen", c, 2050, lv["h2"]) / moh.ETA_H2
                   + moh.storage_adder(c) + add[c])
            if premium is None:
                pk = pt[(c, s)]
            else:
                lvp = ppp.SCEN_LEVERS[s]
                cpp = carbon(2050, lvp["carbon"])
                ocgt = (ppp.GAS_WHOLESALE_2050 / ppp.ETA_OCGT
                        + cpp * ppp.EF_GAS / ppp.ETA_OCGT + ppp.VOM_PEAKER)
                h2d = fuel("hydrogen", c, 2050, lvp["h2"]) * ppp.H2_BACKBONE_FACTOR
                h2t = (h2d / ppp.ETA_H2_TURBINE + ppp.power_storage_adder(c)
                       + ppp.VOM_PEAKER)
                pk = min(ocgt, h2t) + premium
            hpp = pk / max(max(cop_of("hp_air", c, 2050) * frac, floor), 1.0)
            if h2p <= gasp and h2p <= hpp:
                n += 1
                wt += moh.peak_slice_fraction(lp.loc[c]) * lp.loc[c, "annual_TWh"]
                if winners is not None:
                    winners[s].append(c)
        out[s] = (n, 100 * wt / lp["annual_TWh"].sum())
    return out


def power_arena(cavern_set=None):
    """H2 Push power-arena win list. Invariant to pi_s by construction, so no premium arg."""
    moh, ppp, fuel, carbon, *_ = _ctx()
    original = moh.CAVERN
    if cavern_set is not None:
        moh.CAVERN = cavern_set
    try:
        lp = pd.read_csv(RESULTS / "heat_load_profile.csv").set_index("country")
        lv = ppp.SCEN_LEVERS["H2_PUSH"]
        cp = carbon(2050, lv["carbon"])
        ocgt = (ppp.GAS_WHOLESALE_2050 / ppp.ETA_OCGT
                + cp * ppp.EF_GAS / ppp.ETA_OCGT + ppp.VOM_PEAKER)
        wins = []
        for c in lp.index:
            h2d = fuel("hydrogen", c, 2050, lv["h2"]) * ppp.H2_BACKBONE_FACTOR
            h2t = (h2d / ppp.ETA_H2_TURBINE + ppp.power_storage_adder(c) + ppp.VOM_PEAKER)
            if h2t <= ocgt:
                wins.append(c)
        return wins
    finally:
        moh.CAVERN = original


def dh_arena(gas_price=None):
    """District-heat counts. gas_price=None uses the residential retail tariff."""
    from scripts.merit_order_dh import (SCEN, ETA_GAS_CHP, ETA_H2_CHP, COP_LARGE_HP,
                                        EF_GAS, ETA_BIOMASS_CHP, WASTE_HEAT_EUR_MWH)
    moh, _, fuel, carbon, *_rest = _ctx()
    lp = pd.read_csv(RESULTS / "heat_load_profile.csv").set_index("country")
    out = {}
    for s, lv in SCEN.items():
        n = 0
        for c in lp.index:
            cp = carbon(2050, lv["carbon"])
            gas = gas_price if gas_price is not None else fuel("gas", c, 2050)
            h2 = fuel("hydrogen", c, 2050, lv["h2"])
            gas_chp = gas / ETA_GAS_CHP + cp * EF_GAS / ETA_GAS_CHP
            h2_chp = h2 / ETA_H2_CHP + moh.storage_adder(c)
            if h2_chp <= gas_chp:
                n += 1
        out[s] = n
    return out


def main() -> int:
    moh, ppp, *_ = _ctx()
    rows = []
    SC = list(moh.SCEN)

    def add(axis, setting, counts, note=""):
        r = dict(axis=axis, setting=setting, note=note)
        for s in SC:
            v = counts[s]
            if isinstance(v, tuple):
                r[f"count_{s}"], r[f"bound_pct_{s}"] = v[0], round(v[1], 1)
            else:
                r[f"count_{s}"] = v
        rows.append(r)

    print("Dispatch-arena sensitivity: the five choices that can move a count\n")

    print("1. scarcity premium, BUILDING winter peak (it cancels from the power arena)")
    for p in (30.0, 60.0, 120.0):
        c = building_peak(premium=p)
        add("pi_s_building_peak", f"{p:.0f} EUR/MWh-e", c,
            "published" if p == 60 else "")
        print(f"   pi_s={p:5.0f}  " + "  ".join(
            f"{s.split('_')[0][:7]}={c[s][0]:2d} [{c[s][1]:4.1f}%]" for s in SC))

    print("\n2. cold-snap COP derate, COP_cold = max(f*SCOP, floor)")
    for frac, floor in [(0.50, 1.6), (0.55, 1.7), (0.60, 1.8), (0.70, 2.0), (0.75, 2.2)]:
        c = building_peak(derate=(frac, floor))
        add("cop_derate", f"{frac:.2f} floor {floor:.1f}", c,
            "published" if (frac, floor) == (0.60, 1.8) else "")
        print(f"   f={frac:.2f}/{floor:.1f}  " + "  ".join(
            f"{s.split('_')[0][:7]}={c[s][0]:2d} [{c[s][1]:4.1f}%]" for s in SC))

    print("\n3. hydrogen last mile in the BUILDING peak arena")
    win_rows = []
    for on in (False, True):
        w = {}
        c = building_peak(h2_net=on, winners=w)
        basis = "symmetric" if on else "asymmetric"
        for s in SC:
            win_rows.append({"basis": basis, "scenario": s,
                             "n": len(w[s]), "countries": " ".join(w[s])})
        # "published" pointed at the asymmetric row, which stopped being what the
        # manuscript publishes when it moved to symmetric accounting. Label the basis,
        # not the vintage, so the CSV cannot drift out of step with the paper again.
        add("h2_last_mile", "charged" if on else "not charged", c,
            "headline" if on else "earlier_draft")
        print(f"   {'charged    ' if on else 'not charged'}  " + "  ".join(
            f"{s.split('_')[0][:7]}={c[s][0]:2d} [{c[s][1]:4.1f}%]" for s in SC))

    print("\n4. cavern set membership, H2 Push POWER arena")
    base = set(moh.CAVERN)
    for lbl, S in [("published", base), ("plus Iberia", base | {"ES", "PT"}),
                   ("minus France", base - {"FR"})]:
        w = power_arena(S)
        rows.append(dict(axis="cavern_set", setting=lbl,
                         note="; ".join(sorted(w)),
                         **{f"count_{s}": (len(w) if s == "H2_PUSH" else "") for s in SC}))
        print(f"   {lbl:13s} {len(w)} wins: {', '.join(sorted(w))}")

    print("\n5. district-heat gas price basis")
    for lbl, g in [("residential retail", None), ("wholesale hub 30", 30.0)]:
        c = dh_arena(g)
        add("dh_gas_basis", lbl, c,
            "earlier_draft" if g is None else "headline")
        print(f"   {lbl:19s} " + "  ".join(
            f"{s.split('_')[0][:7]}={c[s]:2d}" for s in SC))

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "dispatch_arena_sensitivity.csv", index=False)

    wdf = pd.DataFrame(win_rows)
    wdf.to_csv(RESULTS / "building_peak_winners.csv", index=False)
    print("\nBuilding-peak winners by accounting basis")
    print(wdf.to_string(index=False))

    print(f"\nWrote {RESULTS / 'dispatch_arena_sensitivity.csv'}")
    print(f"Wrote {RESULTS / 'building_peak_winners.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
