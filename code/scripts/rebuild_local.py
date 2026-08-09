"""One-command local rebuild of the forward model from the per-country builds.

This codifies the "local propagation" half of the pipeline: everything that runs
on a normal machine AFTER the per-country bottom-up builds (scripts 01-04, run on
Colab per group) have produced their {CC}_heat_demand_nuts3.csv outputs and
committed them. It chains, in order:

  1. build_building_stock_bottomup()  -> building_stock_nuts3_bottomup.csv
  2. build_hp_dh_feasibility("bottomup")
  3. Monte Carlo: CURRENT_POLICIES / STATED_POLICIES / NET_ZERO / H2_PUSH (--demand bottomup)
  4. COST_OPT LP (Optimisation, --demand bottomup)
  5. grid_sensitivity, rho_sensitivity, h2_gap_analysis
  6. merit-order / supply / infrastructure chain
  7. power-arena and validation modules (capacity_payment, power_dispatch,
     power_uc, cavern_two_way_sweep, the two global sensitivities,
     swiss_integration, eurostat_anchor_invariance, electrification_bridge,
     blue_hydrogen_peaker)
  8. figures (explanatory, explanatory_2, modern) + the LMDI dashboard

Stage 7 exists because the manuscript's own claim table (paper/ae_submission/
REPRODUCE.md) sources the capital-recovery, capacity-payment, unit-commitment and
Sobol numbers from those modules. Without them a reader who runs the documented
single command reproduces the demand, LCOH and least-cost results but not the
power-sector figures the abstract leads with.

Run from the repo's code/ directory (so `src` is importable):
    cd code && PYTHONPATH=. python -m scripts.rebuild_local
Optional: --skip-figs to stop after the result CSVs.

This makes the headline results exactly reproducible from the committed
per-country outputs with a single command, instead of the manual sequence used
during development. See REPRODUCE.md for the full (Colab + local) path.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]      # .../code
# Every optional stage was wrapped in try/except and the run still exited 0, so a rebuild
# that silently skipped make_validation_table -- the paper's most-cited validation result --
# reported "LOCAL REBUILD COMPLETE". Skips are collected and the run fails on them.
SKIPPED: list[str] = []
ROOT = CODE.parent


def _run_module(mod: str, args: list[str] | None = None,
                env: dict[str, str] | None = None) -> None:
    cmd = [sys.executable, "-m", mod] + (args or [])
    shown = " ".join(f"{k}={v}" for k, v in (env or {}).items())
    print(f"\n>>> {shown + ' ' if shown else ''}python -m {mod} {' '.join(args or [])}")
    subprocess.run(cmd, cwd=str(CODE), check=True,
                   env={**os.environ, "PYTHONPATH": str(CODE), **(env or {})})


def main() -> None:
    ap = argparse.ArgumentParser(description="Local rebuild of the forward model.")
    ap.add_argument("--skip-figs", action="store_true",
                    help="Stop after the result CSVs (skip figures + dashboard).")
    ap.add_argument("--scenarios", default="CURRENT_POLICIES,STATED_POLICIES,NET_ZERO,H2_PUSH")
    args = ap.parse_args()

    print("=" * 70)
    print("LOCAL REBUILD  (forward model from committed per-country builds)")
    print("=" * 70)

    # 1-2: re-aggregate the 29-country bottom-up stock + feasibility
    print("\n[1/9] Re-aggregating bottom-up building stock + feasibility ...")
    from src.BuildingStock import (build_building_stock_bottomup,
                                   build_hp_dh_feasibility)
    build_building_stock_bottomup()
    build_hp_dh_feasibility(demand="bottomup")

    # The seasonal load profile must exist before anything that prices a hydrogen
    # boiler. compute_lcoh reads results/heat_load_profile.csv for the seasonal shift
    # fraction and falls back to a flat 0.25 if it is missing, which on a cleared
    # results/ directory would silently change every h2_boiler LCOH in the Monte Carlo
    # and in the least-cost programme by up to about 4 EUR/MWh.
    # benchmark_multi MUST precede heat_load_profile, which reads benchmark_multi.csv
    # unguarded. On a cleared results/ directory the documented top-to-bottom path therefore
    # died on its first step with FileNotFoundError, and benchmark_multi was in neither the
    # claim table nor this script.
    print("\n[2/9] Multi-benchmark validation, then the seasonal heat-load profile ...")
    _run_module("scripts.benchmark_multi")
    _run_module("scripts.heat_load_profile")

    # The backcast and naked-comparison artefacts. These were in no rebuild path, so the
    # Hungary correction that REPRODUCE.md records as fixed in reconcile_backcast.csv was
    # never applied to compare_naked.csv, lmdi_backcast.csv or lmdi_design.csv's naked
    # columns, which all still carried the pre-fix 3,818.9 TWh EU total.
    for mod in ("scripts.reconcile_backcast", "scripts.compare_naked",
                "scripts.lmdi_backcast", "scripts.lmdi_design", "scripts.cohort_forward"):
        try:
            _run_module(mod)
        except Exception as ex:
            print(f"    [skip] {mod}: {ex}")
            SKIPPED.append(mod)

    # 3: Monte Carlo per scenario
    print("\n[3/9] Monte Carlo scenarios ...")
    for sc in [s.strip() for s in args.scenarios.split(",") if s.strip()]:
        _run_module("src.Simulation", ["--scenario", sc, "--demand", "bottomup"])

    # 4: COST_OPT
    print("\n[4/9] COST_OPT least-cost LP ...")
    _run_module("src.Optimisation", ["--demand", "bottomup"])

    # 5: diagnostics / sensitivities
    print("\n[5/9] Sensitivities (grid / rho / H2-gap / climate-HDD) ...")
    for mod in ("scripts.grid_sensitivity", "scripts.rho_sensitivity",
                "scripts.h2_gap_analysis", "scripts.climate_hdd_sensitivity"):
        try:
            _run_module(mod)
        except Exception as ex:
            print(f"    [skip] {mod}: {ex}")
            SKIPPED.append(mod)

    # 6: deterministic supply / merit-order / infrastructure chain, in dependency
    # order (load profile -> endogenous peak power price -> merit order -> profit /
    # DH -> reinforcement sensitivity -> infrastructure bill -> country economics).
    # power_peak_price MUST precede merit_order_heat, which otherwise silently
    # falls back to its hard-coded peak-price constants.
    print("\n[6/9] Merit-order / supply / infrastructure chain ...")
    for mod in ("scripts.heat_load_profile", "scripts.power_peak_price",
                "scripts.merit_order_heat", "scripts.merit_order_profit",
                "scripts.merit_order_dh", "scripts.h2_delivered_cost",
                "scripts.elec_reinforcement_sensitivity",
                "scripts.infrastructure_bill", "scripts.country_econ_table",
                "scripts.h2_supply_scenario", "scripts.h2_infra_scenario",
                "scripts.heat_dispatch"):
        try:
            _run_module(mod)
        except Exception as ex:
            print(f"    [skip] {mod}: {ex}")
            SKIPPED.append(mod)

    # 7: power arena, capital recovery and the validation / robustness modules the
    # manuscript cites. power_dispatch and capacity_payment both read
    # power_peak_price.csv and merit_order_heat.csv, so they run after stage 6.
    # global_sensitivity_econ is per-scenario and takes its scenario from GSE_SCEN.
    print("\n[7/9] Power arena, capital recovery, validation and robustness ...")
    for mod in ("scripts.power_dispatch", "scripts.capacity_payment",
                "scripts.power_uc", "scripts.cavern_two_way_sweep",
                "scripts.swiss_integration", "scripts.electrification_bridge",
                "scripts.blue_hydrogen_peaker", "scripts.hp_flexibility_bound",
                "scripts.eurostat_anchor_invariance", "scripts.global_sensitivity",
                "scripts.cold_snap_duration_sweep", "scripts.dh_connection_charge",
                "scripts.make_validation_table"):
        try:
            _run_module(mod)
        except Exception as ex:
            print(f"    [skip] {mod}: {ex}")
            SKIPPED.append(mod)
    for sc in [s.strip() for s in args.scenarios.split(",") if s.strip()]:
        try:
            _run_module("scripts.global_sensitivity_econ", env={"GSE_SCEN": sc})
        except Exception as ex:
            print(f"    [skip] global_sensitivity_econ {sc}: {ex}")

    if args.skip_figs:
        print("\nDone (CSVs only; --skip-figs set).")
        return

    # 8: figures + dashboard
    print("\n[8/9] Figures ...")
    for mod in ("scripts.explanatory_figures", "scripts.explanatory_figures_2",
                "scripts.modern_figures", "scripts.results_summary",
                "scripts.figure_suite", "scripts.fig_sobol_demand",
                "scripts.fig_model_flow", "scripts.fig_uc_results",
                "scripts.graphical_abstract"):
        try:
            _run_module(mod)
        except Exception as ex:
            print(f"    [skip] {mod}: {ex}")
            SKIPPED.append(mod)
    print("\n[9/9] Dashboard data + dashboard ...")
    try:
        _run_module("scripts.generate_dashboard_data")
    except Exception as ex:
        print(f"    [skip] generate_dashboard_data: {ex}")
        SKIPPED.append("scripts.generate_dashboard_data")
    _run_module("scripts.build_lmdi_dashboard")

    # The figures the two SUBMITTED documents include. Stage 8 above runs the explanatory
    # and dashboard series, none of which emits a P-series figure, so a reader following
    # the one-command path rebuilt 4 of the 12 figures in the submission and the guide
    # claimed "all 30". These are the emitters for the other eight.
    print("\n[9/9] Figures the submission includes ...")
    for mod in ("scripts.paper_figures", "scripts.fig_nuts3_map",
                "scripts.power_merit_order", "scripts.fig_cavern_markets",
                "scripts.figs_missing_switzerland_v2", "scripts.fig_emissions_fan"):
        try:
            _run_module(mod)
        except Exception as ex:
            print(f"    [skip] {mod}: {ex}")
            SKIPPED.append(mod)

    print("\n" + "=" * 70)
    if SKIPPED:
        print(f"LOCAL REBUILD INCOMPLETE: {len(SKIPPED)} stage(s) skipped.")
        for mod in SKIPPED:
            print(f"  - {mod}")
        print("Results in code/results/ are partial. Fix the above and re-run.")
        print("=" * 70)
        raise SystemExit(1)
    print("LOCAL REBUILD COMPLETE. Results in code/results/, figures in")
    print("paper/figs/, dashboard at dashboard/lmdi_dashboard.html.")
    print("=" * 70)


if __name__ == "__main__":
    main()
