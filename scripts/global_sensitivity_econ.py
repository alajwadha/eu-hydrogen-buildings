"""Global (variance-based) sensitivity of the MC HEADLINE outputs to the full
cost / carbon-price / hydrogen-price / discount-rate / pass-through / fuel-price /
tech-share parameter space.

The demand-side Sobol (scripts/global_sensitivity.py -> global_sensitivity.csv)
covers only the four demand drivers. This adds the screen the review asks for:
the economic and policy axes that carry the emissions headline, over the real
NUTS3 Monte Carlo (src.Simulation.run_single_sample), reported as standardized
rank-regression coefficients (SRRC) -- a legitimate variance-based global screen
that works on the existing random (non-Saltelli) draw design.

Run:  cd code && PYTHONPATH=. python -m scripts.global_sensitivity_econ
Out:  code/results/global_sensitivity_economics.csv
      paper/figs/paper/P41_sensitivity_economics.{png,pdf}
"""
from __future__ import annotations
import sys, os
import numpy as np
import pandas as pd
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.Simulation import (sample_parameters, run_single_sample, compute_emissions_df,
                            aggregate_emissions, aggregate_eu, scenario_from_config, PROCESSED_DIR)

N = int(os.environ.get("GSE_N", "192"))
SCEN = os.environ.get("GSE_SCEN", "H2_PUSH")
SEED = 2026
RESULTS = Path(__file__).resolve().parents[1] / "results"
FIGDIR = Path(__file__).resolve().parents[2] / "paper" / "figs" / "paper"

SCALARS = ["fossil_share_2050", "hp_share_2050", "dh_share_2050", "h2_share_2050",
           "demand_reduction_2050", "demand_shape_p", "hp_shape_p", "dh_shape_p",
           "h2_shape_p", "hp_ground_share", "ets2_passthrough", "discount_rate",
           "hp_feas_sfh_mult", "hp_feas_mfh_mult"]
PRETTY = {"fossil_share_2050": "Fossil-phaseout ambition", "hp_share_2050": "Heat-pump target share",
          "dh_share_2050": "District-heat target share", "h2_share_2050": "Hydrogen target share",
          "demand_reduction_2050": "Demand reduction", "demand_shape_p": "Demand trajectory shape",
          "hp_shape_p": "HP uptake shape", "dh_shape_p": "DH uptake shape", "h2_shape_p": "H2 uptake shape",
          "hp_ground_share": "Ground-source HP share", "ets2_passthrough": "ETS2 pass-through",
          "discount_rate": "Discount rate (WACC)", "hp_feas_sfh_mult": "HP feasibility (SFH)",
          "hp_feas_mfh_mult": "HP feasibility (MFH)", "gas_price_mult": "Gas price",
          "elec_price_mult": "Electricity price", "h2_price_mult": "Hydrogen price"}


def _co2_2050(sdf):
    em = aggregate_emissions(sdf)
    r = em[(em["variable"] == "co2_MtCO2") & (em["year"] == 2050)]
    return float(r["value"].astype(float).sum())


def srrc(X, y):
    from scipy.stats import rankdata
    Xr = np.column_stack([rankdata(X[:, j]) for j in range(X.shape[1])])
    yr = rankdata(y)
    Xs = (Xr - Xr.mean(0)) / Xr.std(0)
    ys = (yr - yr.mean()) / yr.std()
    beta, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(y)), Xs]), ys, rcond=None)
    b = beta[1:]
    r2 = 1 - np.var(ys - Xs @ b) / np.var(ys)
    return b, float(r2)


PARAM_LABEL = {
    "fossil_share_2050":     "Fossil-phaseout ambition (2050 fossil target share)",
    "elec_price_mult":       "Electricity-price multiplier",
    "hp_feas_mfh_mult":      "Heat-pump feasibility, multi-family",
    "demand_reduction_2050": "2050 demand reduction",
    "dh_share_2050":         "District-heat 2050 target share",
    "dh_shape_p":            "District-heat uptake exponent",
    "demand_shape_p":        "Demand-reduction path exponent",
    "ets2_passthrough":      "ETS2 pass-through",
    "h2_price_mult":         "Hydrogen-price multiplier",
    "hp_shape_p":            "Heat-pump uptake exponent",
    "h2_shape_p":            "Hydrogen uptake exponent",
    "gas_price_mult":        "Gas-price multiplier",
    "hp_feas_sfh_mult":      "Heat-pump feasibility, single-family",
    "hp_share_2050":         "Heat-pump 2050 target share",
    "h2_share_2050":         "Hydrogen 2050 target share",
    "hp_ground_share":       "Ground-source share of heat pumps",
    "discount_rate":         "Discount rate / WACC",
}


def _emit_si_table(out: pd.DataFrame, r2: float, n: int) -> None:
    """Write the SI screen table from the artefact rather than by hand.

    The hand-written version showed 6 of the 17 sampled parameters while its caption
    claimed to cover "economic, policy and technology-share uncertainty", so every
    technology-share axis it named was missing from the table a reader was pointed at.
    Generating it means the table is the artefact, and adding a sampled parameter cannot
    silently leave the table behind.
    """
    d = out.sort_values("srrc", key=lambda s: -s.abs())
    lead = d.iloc[0]
    rest = d.iloc[1:]
    # Three sampled parameters reach no live code path in the production configuration, so
    # their coefficients are noise on a variable the model never reads. One of them,
    # hp_feas_mfh_mult, was ranking THIRD of seventeen. Daggered in the table and named in
    # the caption, because a ranking that presents an inert parameter above fourteen live
    # ones invites a reader to draw a conclusion from it.
    INERT = {"hp_feas_mfh_mult": "read by no code path in src/",
             "demand_reduction_2050": "read only on the legacy non-LMDI branch",
             "demand_shape_p": "read only on the legacy non-LMDI branch"}
    def mark(name: str) -> str:
        return PARAM_LABEL.get(name, name) + (r"$^{\dagger}$" if name in INERT else "")
    rows = [r"% Generated by scripts.global_sensitivity_econ -- do not edit by hand.",
            r"\begin{table}[htbp]", r"\centering",
            r"\caption{\textbf{Global variance-based sensitivity of 2050 buildings-sector",
            r"\ce{CO2} emissions.} Every parameter the Monte Carlo samples, as standardised",
            rf"rank-regression coefficients (SRRC) over the NUTS3 Monte Carlo ($N={n}$ draws,",
            rf"H2~Push scenario; rank-$R^2 = {r2:.2f}$). One policy lever governs the 2050",
            r"emissions headline and every other axis, economic, technology-share and",
            rf"discount alike, carries $|\mathrm{{SRRC}}| < {abs(rest.srrc).max():.2f}$.}}",
            r"\label{tab:sens_econ}", r"\begin{tabular}{lc}", r"\toprule",
            r"Sampled parameter & SRRC \\", r"\midrule",
            f"{mark(lead.parameter)} & ${lead.srrc:+.3f}$ \\\\",
            r"\midrule"]
    rows += [f"{mark(r.parameter)} & ${r.srrc:+.3f}$ \\\\"
             for r in rest.itertuples()]
    _flagged = [PARAM_LABEL.get(k, k) for k in INERT if k in set(d.parameter)]
    rows += [r"\bottomrule", r"\end{tabular}",
             (r"\\[2pt]{\footnotesize$^{\dagger}$Sampled but inert in the production "
              r"configuration (" + "; ".join(_flagged) + r"), so the coefficient is noise on "
              r"a variable the model does not read. Listed for completeness of the sampled "
              r"set, and its rank should not be read as influence.}" if _flagged else ""),
             r"\\[2pt]{\footnotesize\textit{Source: Authors' contribution.}}",
             r"\end{table}", ""]
    (RESULTS.parents[1] / "paper" / "ae_submission" / "si_body"
     / "_tab_sens_econ.tex").write_text("\n".join(rows), encoding="utf8")


def main():
    scen = scenario_from_config(SCEN)
    # Read the BOTTOMUP stock, which is the basis every published number sits on. This read
    # the Hotmaps 2015 benchmark files instead, so the SI's economic sensitivity table and
    # the rank-R2 values the manuscripts quote were computed on a different demand basis from
    # the results they qualify.
    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    feas = pd.read_csv(PROCESSED_DIR / "hp_dh_feasibility_bottomup.csv")
    rng = np.random.default_rng(SEED)
    names = SCALARS + ["gas_price_mult", "elec_price_mult", "h2_price_mult"]
    X, Yco2 = [], []
    print(f"Global economic sensitivity: {SCEN}, N={N}")
    for i in range(N):
        p = sample_parameters(scen, rng, scen.carbon_scenario, scen.h2_scenario)
        sdf = run_single_sample(scen, p, stock, feas)
        sdf = compute_emissions_df(sdf, grid_mult=scen.grid_mult)
        pm = p["price_mult"]

        def _m(c):
            return float(np.mean([pm[k].get(c, 1.0) for k in pm]))
        X.append([float(p[k]) for k in SCALARS] + [_m("gas"), _m("electricity"), _m("hydrogen")])
        Yco2.append(_co2_2050(sdf))
        if (i + 1) % 48 == 0:
            print(f"  {i+1}/{N}")
    X = np.array(X)
    b, r2 = srrc(X, np.array(Yco2))
    out = pd.DataFrame({"scenario": SCEN, "output": "co2_2050_MtCO2",
                        "parameter": names, "srrc": np.round(b, 4)}).sort_values(
        "srrc", key=lambda s: -s.abs())
    # The rank-R2 used to live only in out.attrs, which to_csv silently discards, so the
    # figure quoted a number no committed artefact contained and no gate could check. It is
    # a property of the whole fit rather than of one parameter, so it goes in its own column,
    # repeated down the rows, which is the cheapest shape a CSV can carry it in.
    out.attrs["r2"] = r2
    out["rank_r2"] = round(r2, 4)
    RESULTS.mkdir(exist_ok=True)
    out.to_csv(RESULTS / "global_sensitivity_economics.csv", index=False)

    # Accumulate one row per scenario so all four rank-R2 values are readable at once,
    # which is how the papers quote them.
    summary_path = RESULTS / "global_sensitivity_econ_r2.csv"
    prior = (pd.read_csv(summary_path) if summary_path.exists()
             else pd.DataFrame(columns=["scenario", "rank_r2", "n_draws"]))
    prior = prior[prior.scenario != SCEN]
    pd.concat([prior, pd.DataFrame([{"scenario": SCEN, "rank_r2": round(r2, 4),
                                     "n_draws": N}])]).sort_values("scenario").to_csv(
        summary_path, index=False)
    if SCEN == "H2_PUSH":
        _emit_si_table(out, r2, N)
    print(out.to_string(index=False))
    print(f"rank-R2 = {r2:.3f}")

    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    o = out.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#c0392b" if abs(v) >= 0.1 else "#95a5a6" for v in o["srrc"]]
    ax.barh([PRETTY.get(p, p) for p in o["parameter"]], o["srrc"], color=colors)
    ax.axvline(0, color="k", lw=0.7)
    ax.set_xlabel("Standardized rank-regression coefficient (SRRC)")
    ax.set_title(f"Global sensitivity of 2050 buildings CO₂ ({SCEN.replace('_',' ').title()})\n"
                 f"rank-$R^2$ = {r2:.2f}, N = {N} draws")
    fig.tight_layout()
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / "P41_sensitivity_economics.png", dpi=200)
    fig.savefig(FIGDIR / "P41_sensitivity_economics.pdf")
    print("wrote P41_sensitivity_economics.{png,pdf}")


if __name__ == "__main__":
    main()
