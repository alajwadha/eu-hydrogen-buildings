"""
run.py  —  Single entry point for the EU Hydrogen Buildings model pipeline.

Usage:
  python run.py [--scenario CURRENT_POLICIES|STATED_POLICIES|NET_ZERO|H2_PUSH|COST_OPT|ALL|ALL+COST_OPT]
                [--skip-download] [--carbon LOW|CENTRAL|HIGH]
                [--h2 RAPID|CENTRAL|SLOW|STRANDED] [--demand hotmaps|bottomup]
                [--figures-only] [--sensitivity]

  COST_OPT runs the least-cost LP (code/src/Optimisation.py): the -75/-90/-100%
  emissions-cap variants of the cost-optimal decarbonisation pathway.

Steps:
  1. Download raw data (Hotmaps, Eurostat, GISCO)
  2. Build building stock (NUTS3 × building type × heat demand)
  3. Run Monte Carlo simulation (Steps 1+2+3 integrated)
  4. Generate paper figures and tables
  5. Regenerate dashboard data.js
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
CODE_DIR  = REPO_ROOT / "code"
sys.path.insert(0, str(CODE_DIR))

import warnings
# A blanket ignore silenced src.Economics' RuntimeWarning guard for a missing
# heat_load_profile.csv, so every hydrogen LCOH on this path could fall back to a flat 0.25
# seasonal shift fraction -- worth about 4 EUR/MWh -- with nothing printed. Keep the noise
# suppression for third-party deprecations and let our own guards through.
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.simplefilter("always", RuntimeWarning)


def step(n: int, label: str) -> None:
    print(f"\n{'='*60}")
    print(f"  STEP {n}: {label}")
    print(f"{'='*60}")


def run_pipeline(
    scenarios: list,
    skip_download: bool = False,
    carbon: str = "CENTRAL",
    h2: str = "CENTRAL",
    figures_only: bool = False,
    sensitivity: bool = False,
    n_samples: int = 200,
    demand: str = "hotmaps",
) -> None:

    import src.Config as cfg
    cfg.N_MONTE_CARLO_SAMPLES = n_samples

    # ── Step 1: Download data ─────────────────────────────────────────────
    if not skip_download and not figures_only:
        step(1, "Download raw data")
        try:
            subprocess.run(
                [sys.executable, str(CODE_DIR / "scripts" / "download_data.py")],
                check=True,
            )
        except Exception as e:
            print(f"  [warn] Download failed: {e} — continuing with cached data")
    else:
        print("\nStep 1: skipped (--skip-download or --figures-only)")

    # ── Step 2: Build building stock ──────────────────────────────────────
    if not figures_only:
        # compute_lcoh reads results/heat_load_profile.csv for the seasonal shift fraction
        # and falls back to a flat 0.25 without it, which moves every hydrogen LCOH in the
        # Monte Carlo by up to about 4 EUR/MWh. run.py never produced it, so a clean-results
        # run silently priced the seasonal store wrong. Produce it before anything prices a
        # hydrogen boiler.
        import subprocess as _sp, sys as _sys
        print("\nStep 2a: Seasonal heat-load profile (prerequisite for every H2 LCOH)")
        _sp.run([_sys.executable, "-m", "scripts.heat_load_profile"],
                cwd=str(Path(__file__).resolve().parent / "code"), check=False,
                env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent / "code")})
        step(2, f"Build NUTS3 building stock (demand={demand})")
        from src.BuildingStock import (
            build_building_stock, build_building_stock_bottomup,
            build_hp_dh_feasibility, stock_path as _stock_path,
            feas_path as _feas_path,
        )
        sp = _stock_path(demand)
        fp = _feas_path(demand)
        if demand == "bottomup":
            # Reassemble from the per-country builds every run (cheap) so it
            # always reflects the latest committed country results.
            build_building_stock_bottomup()
            build_hp_dh_feasibility(demand="bottomup")
            print("  Bottom-up building stock + feasibility built.")
        elif not sp.exists():
            build_building_stock()
            build_hp_dh_feasibility()
            print("  Building stock built.")
        else:
            if not fp.exists():
                build_hp_dh_feasibility()
            print(f"  Building stock exists ({sp.stat().st_size/1024:.0f} KB) — skipped rebuild.")

    # ── Step 3: Monte Carlo simulation ────────────────────────────────────
    if not figures_only:
        step(3, "Monte Carlo simulation (Steps 1+2+3 integrated)")
        from src.Simulation import run_monte_carlo, run_sensitivity
        from src.Economics import DISCOUNT_RATE_REAL

        if sensitivity:
            print("  Running sensitivity analysis across all axes...")
            run_sensitivity(scenarios[0], demand=demand)
        else:
            for scenario in scenarios:
                t0 = time.time()
                if scenario == "COST_OPT":
                    # Least-cost LP (Step 5 / Optimisation.py): solves the
                    # -75/-90/-100% emissions-cap variants in one pass; not a
                    # Monte-Carlo run, so it ignores carbon/h2/discount axes.
                    from src.Optimisation import run_cost_opt
                    run_cost_opt(demand=demand)
                else:
                    run_monte_carlo(
                        scenario,
                        carbon_scenario=carbon,
                        h2_scenario=h2,
                        discount_rate=DISCOUNT_RATE_REAL,
                        demand=demand,
                    )
                print(f"  {scenario} completed in {(time.time()-t0)/60:.1f} min")

    # ── Step 4: Generate figures and tables ───────────────────────────────
    step(4, "Generate paper figures and tables")
    from src.Visualise import make_all_figures
    # Visualise is not COST_OPT-aware yet; it reads the mc_*_COST_OPT_* tables
    # directly. Only pass the MC scenarios so figure generation never breaks.
    _fig_scenarios = [s for s in scenarios if s != "COST_OPT"]
    if _fig_scenarios:
        make_all_figures(_fig_scenarios)

    # ── Step 5: Regenerate dashboard data ─────────────────────────────────
    step(5, "Regenerate dashboard data.js")
    try:
        subprocess.run(
            [sys.executable,
             str(CODE_DIR / "scripts" / "generate_dashboard_data.py")],
            check=True,
        )
    except Exception as e:
        print(f"  [warn] Dashboard data generation failed: {e}")

    print("\n" + "="*60)
    print("  PIPELINE COMPLETE")
    print(f"  Figures:   paper/figs/")
    print(f"  Tables:    paper/tables/")
    print(f"  Results:   code/results/")
    print(f"  Dashboard: https://alajwadha.github.io/eu-hydrogen-buildings/")
    print("="*60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="EU Hydrogen Buildings model pipeline")
    parser.add_argument("--scenario", default="ALL",
        help="CURRENT_POLICIES | STATED_POLICIES | NET_ZERO | H2_PUSH | COST_OPT | "
             "ALL | ALL+COST_OPT (default: ALL). COST_OPT runs the least-cost LP.")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--carbon", default="CENTRAL",
        help="Carbon price: LOW | CENTRAL | HIGH")
    parser.add_argument("--h2", default="CENTRAL",
        help="H2 trajectory: RAPID | CENTRAL | SLOW | STRANDED")
    parser.add_argument("--figures-only", action="store_true",
        help="Skip simulation, just regenerate figures from existing results")
    parser.add_argument("--sensitivity", action="store_true",
        help="Run full sensitivity analysis (slower)")
    parser.add_argument("--samples", type=int, default=200,
        help="Number of Monte Carlo samples (default: 200)")
    # Defaulted to "hotmaps" while every published number is on "bottomup", and both bases
    # write the SAME filenames with no basis marker, so an unflagged run silently replaced
    # the published results with indistinguishable files. Default flipped to the published
    # basis; src.Optimisation already defaulted this way.
    parser.add_argument("--demand", default="bottomup",
        choices=["hotmaps", "bottomup"],
        help="Demand basis: bottomup (29-country EUBUCCO+TABULA build; the basis every "
             "published number in the manuscripts sits on, and the default) | hotmaps "
             "(the 2015 regional benchmark, a DIFFERENT demand level, for reconciliation only)")
    args = parser.parse_args()

    if args.scenario == "ALL":
        scenarios = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
    elif args.scenario == "ALL+COST_OPT":
        scenarios = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH", "COST_OPT"]
    else:
        scenarios = [args.scenario]

    run_pipeline(
        scenarios=scenarios,
        skip_download=args.skip_download,
        carbon=args.carbon,
        h2=args.h2,
        figures_only=args.figures_only,
        sensitivity=args.sensitivity,
        n_samples=args.samples,
        demand=args.demand,
    )


if __name__ == "__main__":
    main()
