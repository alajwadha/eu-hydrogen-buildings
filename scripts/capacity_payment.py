"""Standing capacity payment for the hydrogen peaker, derived from persisted model
outputs and the model's own cost constants (no new run, no fabrication).

Each cavern market recovers a different share of its annualised capital from market
rent by 2050, because the scarcity margin is common (60 EUR/MWh) but the run window is
not. The residual standing payment that would make the plant whole follows by
arithmetic, computed per country so it stays consistent with the 25-year dispatch
model that produces the recovery:

  annualised capex (EUR/kW-yr) = (CRF(wacc, 25 yr) + FOM) x H2_TURBINE_CAPEX
  standing payment             = annualised capex x (1 - recovery_share_c)

recovery_share_c is rebuilt here from the same margin and capacity terms the dispatch
model uses, country by country. An earlier version applied a single EU-aggregate
recovery scalar to every country, which made the implied per-country recovery
round-trip back to that constant; the spread it appeared to show was rounding, not
signal. Countries that win on operating cost but build no peaker in 2050 (the Netherlands)
have no capital to recover and are reported separately rather than averaged in.

The break-even utilisation is NOT computed here from the peak-hour margin (which is
the scarcity premium, ~60 EUR/MWh); over the running hours the effective inframarginal
rent is lower, and the text quotes the multiple from the published single-year
recovery rather than re-deriving it here, to avoid conflating the peak-hour margin
with the effective rent.

Run:  cd code && PYTHONPATH=. python -m scripts.capacity_payment
Out:  code/results/capacity_payment.csv
"""
from __future__ import annotations
import os

import numpy as np
from pathlib import Path

import pandas as pd
from src.Config import RESULTS_DIR
from src.Economics import DISCOUNT_RATE_BY_COUNTRY, DISCOUNT_RATE_REAL
from scripts.power_dispatch import (
    crf, PEAKER_LIFE, PEAKER_FOM_FRAC, H2_TURBINE_CAPEX, GAS_OCGT_CAPEX,
    YEARS, SCEN_LEVERS, eta_ocgt, eta_h2_turbine, gas_wholesale, get_carbon_price,
    get_fuel_price, storage_per_mwh_h2, storage_learning, EF_GAS, SCARCITY_PREMIUM,
    VOM_PEAKER, LABOUR_COST_MULTIPLIER,
)
from scripts.merit_order_heat import CAVERN

SCEN, YEAR = "H2_PUSH", 2050


def _per_country_recovery():
    """Rebuild the 2050 capital-recovery share country by country, on the same terms
    the dispatch model uses. Returns {country: (rec_h2, rec_gas, cap_gw, flh)}."""
    s = pd.read_csv(RESULTS_DIR / "power_dispatch_summary.csv")
    s = s[s.basis == "total_elec"]
    energy = {c: dict(zip(g.year, g.peaker_energy_gwh)) for c, g in s.groupby("country")}
    cap = {c: dict(zip(g.year, g.peaker_cap_gw)) for c, g in s.groupby("country")}
    flh = {c: dict(zip(g.year, g.peaker_flh)) for c, g in s.groupby("country")}

    lv = SCEN_LEVERS[SCEN]
    eo, gw = eta_ocgt(YEAR), gas_wholesale(YEAR)
    eh, cp = eta_h2_turbine(YEAR, SCEN), get_carbon_price(YEAR, lv["carbon"])

    out = {}
    for c in sorted(CAVERN):
        if c not in energy:
            continue
        e_mwh = float(np.interp(YEAR, YEARS, [energy[c][m] for m in YEARS])) * 1e3
        cap_kw = float(np.interp(YEAR, YEARS, [cap[c][m] for m in YEARS])) * 1e6
        wacc = DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL)
        af = crf(wacc, PEAKER_LIFE) + PEAKER_FOM_FRAC
        vom = VOM_PEAKER * (0.5 + 0.5 * LABOUR_COST_MULTIPLIER.get(c, 1.0))
        h2d = get_fuel_price("hydrogen", c, YEAR, lv["h2"])
        sto = storage_per_mwh_h2(c) * storage_learning(YEAR) / eh
        gvar = gw / eo + cp * EF_GAS / eo + vom
        hvar = h2d * 0.85 / eh + sto + vom
        clr = min(gvar, hvar) + SCARCITY_PREMIUM["central"]
        hk, gk = af * H2_TURBINE_CAPEX * cap_kw, af * GAS_OCGT_CAPEX * cap_kw
        out[c] = (
            (clr - hvar) * e_mwh / hk if hk else float("nan"),
            (clr - gvar) * e_mwh / gk if gk else float("nan"),
            cap_kw / 1e6,
            flh[c][YEAR],
        )
    return out


NAME = {"DK": "Denmark", "UK": "United Kingdom", "FR": "France", "DE": "Germany",
        "PL": "Poland", "RO": "Romania", "NL": "Netherlands"}
SI_TAB = (Path(__file__).resolve().parents[2] / "paper" / "ae_submission" / "si_body"
          / "_tab_capacity_payment.tex")


def emit_si_table(df: "pd.DataFrame", built: "pd.DataFrame") -> None:
    """Write the per-market capacity-payment table from the artefact.

    This table was hand-maintained while the README told a reader that
    scripts.capacity_payment emitted it. Its numbers happened to match, but nothing kept
    them in sync, and the same file also carried the capacity-weighted row and the "four of
    five" and "96 per cent" claims as typed text. All of it is derived here.
    """
    # Print what the artefact says. capacity_payment.csv is rounded with numpy and this
    # table used to format the unrounded frame with Python's f-string, and the two
    # disagree on an exact half: Poland's peaker is 22.05 GW, which went to the file as
    # 22.0 and onto the page as 22.1. A referee who downloads the CSV to check the table
    # should read the same digits. Round once, here, on the same basis as the file.
    d = df.sort_values("recovery_h2_pct", ascending=False).copy()
    for _c in d.columns:
        if _c not in ("country", "wacc"):
            d[_c] = d[_c].round(1)
    # The weighted rows below stay on the unrounded frame: those are computed quantities,
    # not display values, and rounding their inputs first would change the answer.
    w = built.peaker_cap_gw
    cw_rec = (built.recovery_h2_pct * w).sum() / w.sum()
    cw_h2 = (built.standing_payment_h2 * w).sum() / w.sum()
    cw_gas = (built.standing_payment_gas * w).sum() / w.sum()
    cw_rec_gas = (built.recovery_gas_pct * w).sum() / w.sum()
    n_gas_cheaper = int((built.standing_payment_gas < built.standing_payment_h2).sum())
    share = 100 * built.loc[built.standing_payment_gas < built.standing_payment_h2,
                            "peaker_cap_gw"].sum() / w.sum()
    idle = [NAME.get(c, c) for c in df.loc[df.peaker_cap_gw <= 0, "country"]]
    rows = []
    for _, r in d.iterrows():
        nm = NAME.get(r.country, r.country)
        if r.peaker_cap_gw <= 0:
            # "n/a", not \textemdash. The house rule bans em-dashes and these were the
            # only ones reaching the compiled SI, ten of them, in a document otherwise
            # free of the glyph.
            rows.append(f" {nm:<14} & {100*r.wacc:.1f} &  0.0 &   0 & n/a & "
                        f"n/a & n/a & n/a \\\\")
        else:
            rows.append(f" {nm:<14} & {100*r.wacc:.1f} & {r.peaker_cap_gw:4.1f} & "
                        f"{r.peaker_flh:3.0f} & {r.recovery_h2_pct:4.1f} & "
                        f"{r.standing_payment_h2:4.1f} & $-${abs(r.recovery_gas_pct):.1f} & "
                        f"{r.standing_payment_gas:4.1f} \\\\")
    tex = rf"""% Generated by scripts.capacity_payment -- do not edit by hand.
\begin{{table}}[htbp]
 \centering
  \caption{{\textbf{{The standing capacity payment a winning hydrogen peaker would
 need, 2050.}} The seven salt-cavern markets in which the hydrogen turbine wins the
 winter peak on operating cost (H2~Push).}}
 \label{{tab:capacity_payment}}
 \small
 \begin{{tabular}}{{lrrrrrrr}}
 \toprule
 Country & & Peaker & Run & \multicolumn{{2}}{{c}}{{Hydrogen}} & \multicolumn{{2}}{{c}}{{Gas}} \\
 \cmidrule(lr){{5-6}}\cmidrule(lr){{7-8}}
 & WACC & fleet & window & Recovery & Payment & Recovery & Payment \\
 & (\%) & (GW) & (h/yr) & (\%) & (\euro{{}}/kW-yr) & (\%) & (\euro{{}}/kW-yr) \\
 \midrule
{chr(10).join(rows)}
 \midrule
 Capacity-weighted & n/a & {w.sum():.1f} & n/a & {cw_rec:.1f} & {cw_h2:.1f} & $-${abs(cw_rec_gas):.1f} & {cw_gas:.1f} \\
 \bottomrule
 \end{{tabular}}
 \par\vspace{{3pt}}{{\footnotesize\raggedright
 \textit{{Note:}} recovery is the single-year ratio of inframarginal rent to that year's
 annualised capital charge, and the payment is the shortfall the rent leaves. The gas
 column prices the same plant at \euro{{}}450/kW against \euro{{}}600/kW for a
 hydrogen-ready turbine, and its recovery is negative because hydrogen sets the clearing
 price here. The Netherlands and Romania build no peaker, so their recovery and payment
 are undefined. Cells round independently, so the capacity rows sum to
 {d.loc[d.peaker_cap_gw > 0, 'peaker_cap_gw'].sum():.1f} against a printed
 {w.sum():.1f}.\par}}
 \vspace{{2pt}}{{\footnotesize\raggedright \textit{{Source: Authors' contribution.}}\par}}
\end{{table}}
"""
    # Emitting is opt-in. The number gate subprocess-runs this module to read the
    # conditioning premium off its console output, and while the write was
    # unconditional that gate rewrote a manuscript source file every time it ran. It
    # happened to be byte-identical, so git stayed clean; had the artefact moved, the
    # gate would have silently repaired the SI table and then reported a pass on it.
    # A checker must not edit the thing it is judging.
    if os.environ.get("CAPACITY_PAYMENT_NO_EMIT"):
        if SI_TAB.exists() and SI_TAB.read_text() != tex:
            print(f"WARNING: {SI_TAB.name} differs from what this run would write; "
                  "re-run without CAPACITY_PAYMENT_NO_EMIT to refresh it.")
        return
    SI_TAB.write_text(tex)
    print(f"Wrote {SI_TAB}")


def main():
    rec = _per_country_recovery()
    rows = []
    for c, (r_h2, r_gas, cap_gw, hours) in rec.items():
        wacc = DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL)
        crf_fom = crf(wacc, PEAKER_LIFE) + PEAKER_FOM_FRAC      # 25-yr life, matches recovery basis
        ann_h2, ann_gas = crf_fom * H2_TURBINE_CAPEX, crf_fom * GAS_OCGT_CAPEX
        rows.append(dict(country=c, wacc=round(wacc, 3), peaker_cap_gw=round(cap_gw, 2),
                         peaker_flh=int(hours), recovery_h2_pct=100 * r_h2,
                         ann_capex_h2=ann_h2, standing_payment_h2=ann_h2 * (1 - r_h2),
                         recovery_gas_pct=100 * r_gas,
                         ann_capex_gas=ann_gas, standing_payment_gas=ann_gas * (1 - r_gas)))
    df = pd.DataFrame(rows)
    # Round the money and percentage columns only. Rounding the whole frame to 1 dp
    # collapsed the wacc column (0.035 -> 0.0), which is a column a referee reads.
    out = df.copy()
    for c in out.columns:
        if c not in ("country", "wacc"):
            out[c] = out[c].round(1)
    out.to_csv(RESULTS_DIR / "capacity_payment.csv", index=False)

    built = df[df.peaker_cap_gw > 0]
    nobuild = sorted(df.loc[df.peaker_cap_gw == 0, "country"])

    def rng(col, d=built):
        return f"{d[col].min():.0f} to {d[col].max():.0f}"

    print(f"{SCEN} {YEAR}, per-country capital recovery across the cavern markets that build:")
    for _, r in built.iterrows():
        print(f"  {r.country}  {r.peaker_cap_gw:6.2f} GW  {r.peaker_flh:4d} h  "
              f"recovery {r.recovery_h2_pct:5.1f}%  standing payment "
              f"{r.standing_payment_h2:5.1f} EUR/kW-yr")
    if nobuild:
        print(f"  no 2050 peaker built (recovery undefined): {', '.join(nobuild)}")
    print("\nAcross the cavern markets that build (EUR/kW-yr):")
    print(f"  annualised H2 capex   : {rng('ann_capex_h2')}")
    print(f"  standing payment (H2) : {rng('standing_payment_h2')}")
    print(f"  annualised gas capex  : {rng('ann_capex_gas')}")
    print(f"  standing payment (gas): {rng('standing_payment_gas')}")
    print(f"  H2 recovery span      : {built.recovery_h2_pct.min():.1f} to "
          f"{built.recovery_h2_pct.max():.1f}%")

    # Technology neutrality. A capacity auction clears on EUR/kW-yr required, not on the
    # recovery fraction. Gas recovers less of its capital here (its rent is negative,
    # because hydrogen sets the clearing price) yet asks for less money, because an OCGT
    # costs less to build than a hydrogen-ready turbine. So a technology-neutral payment
    # in these markets buys unabated gas; selecting hydrogen needs an emissions condition,
    # whose cost is the payment difference over the gas generation it displaces.
    w = built.peaker_cap_gw
    wp_h2 = (built.standing_payment_h2 * w).sum() / w.sum()
    wp_gas = (built.standing_payment_gas * w).sum() / w.sum()
    cheaper = built[built.standing_payment_gas < built.standing_payment_h2]
    e_mwh_e = built.peaker_flh.mul(built.peaker_cap_gw).sum() * 1e3      # GW x h -> GWh -> MWh
    co2 = e_mwh_e / eta_ocgt(YEAR) * EF_GAS                              # tCO2/yr if gas ran instead
    premium = (wp_h2 - wp_gas) * w.sum() * 1e6 / co2
    print("\nTechnology neutrality (capacity-weighted across the markets that build):")
    print(f"  payment required      : gas {wp_gas:.1f} vs H2 {wp_h2:.1f} EUR/kW-yr")
    print(f"  gas turbine capex     : {GAS_OCGT_CAPEX:.0f} vs {H2_TURBINE_CAPEX:.0f} EUR/kW for H2")
    print(f"  gas is cheaper in     : {len(cheaper)} of {len(built)} markets "
          f"({100 * cheaper.peaker_cap_gw.sum() / w.sum():.0f}% of winning capacity)")
    # A gas peaker will not dispatch below its own SRMC, so floor its rent at zero and
    # report the resulting upper bound alongside the headline figure.
    wp_gas_floor = (built.ann_capex_gas * w).sum() / w.sum()
    premium_floor = (wp_h2 - wp_gas_floor) * w.sum() * 1e6 / co2
    print(f"  with gas rent floored at zero: gas {wp_gas_floor:.1f} EUR/kW-yr, "
          f"premium {premium_floor:.0f} EUR/tCO2")
    print(f"  emissions-conditioning premium: {premium:.0f} EUR/tCO2 of displaced gas "
          f"generation, on top of the carbon price already in the gas plant's SRMC")
    # The corollary above turns entirely on the capex gap, so sweep it. Below roughly
    # 520-540 EUR/kW the sign reverses and a technology-neutral payment procures hydrogen.
    print("\nSensitivity of the corollary to the hydrogen turbine capex:")
    print(f"  {'H2 capex':>9} {'premium':>8} {'gas cheaper in':>15} {'conditioning EUR/tCO2':>22}")
    sweep = []
    for K in (450, 495, 520, 540, 550, 553, 560, 600, 700):
        rows = []
        for _, r in built.iterrows():
            wacc = DISCOUNT_RATE_BY_COUNTRY.get(r.country, DISCOUNT_RATE_REAL)
            af = crf(wacc, PEAKER_LIFE) + PEAKER_FOM_FRAC
            rent_h2 = r.recovery_h2_pct / 100 * (af * H2_TURBINE_CAPEX)   # rent is capex-independent
            rent_gas = r.recovery_gas_pct / 100 * (af * GAS_OCGT_CAPEX)
            rows.append((r.peaker_cap_gw, af * K - rent_h2, af * GAS_OCGT_CAPEX - rent_gas))
        tw = sum(x[0] for x in rows)
        ph = sum(x[0] * x[1] for x in rows) / tw
        pg = sum(x[0] * x[2] for x in rows) / tw
        n = sum(1 for x in rows if x[2] < x[1])
        prem = (ph - pg) * tw * 1e6 / co2
        sweep.append((K, prem))
        print(f"  {K:>9.0f} {100*(K/GAS_OCGT_CAPEX-1):>7.0f}% {n:>10} of {len(rows)} {prem:>22.0f}")
    lo = max(k for k, p in sweep if p < 0); hi = min(k for k, p in sweep if p > 0)
    print(f"  sign reverses between {lo:.0f} and {hi:.0f} EUR/kW "
          f"(about {100*(0.5*(lo+hi)/GAS_OCGT_CAPEX-1):.0f}% premium over gas)")
    emit_si_table(df, built)
    print("\nwrote results/capacity_payment.csv")


if __name__ == "__main__":
    main()
