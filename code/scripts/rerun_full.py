"""Full from-scratch rerun after a scenario-input change (e.g. Hydrogen Push -> High
carbon + derived Rapid H2). Chains the Monte Carlo rebuild and then the merit-order /
dispatch chain in the order they depend on each other. Each step is a subprocess so one
failure stops the run with a clear marker.

Run (detached, logged):  cd code && PYTHONPATH=. PYTHONUTF8=1 python -m scripts.rerun_full
"""
from __future__ import annotations
import subprocess, sys, os, time
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(CODE), "PYTHONUTF8": "1"}

# Only Hydrogen Push changed (carbon CENTRAL->HIGH, Rapid H2 price); the other three
# scenarios and the building stock are unchanged, so rerun ONLY the H2_PUSH Monte Carlo,
# then the full merit-order / dispatch chain (which reads all four scenarios' MC outputs --
# three from the existing cache, H2_PUSH freshly rerun).
STEPS = [
    ("src.Simulation", ["--scenario", "H2_PUSH", "--demand", "bottomup"]),
    ("scripts.power_peak_price", []),       # endogenous scarcity price (MUST precede merit_order_heat)
    ("scripts.merit_order_heat", []),       # building peaking merit order
    ("scripts.merit_order_dh", []),         # district-heating merit order
    ("scripts.merit_order_profit", []),     # missing-money / peaker investment
    ("scripts.infrastructure_bill", []),    # network-infrastructure bill per scenario
    ("scripts.power_dispatch", []),         # hourly power dispatch + peaker economics + robustness + recovery
    ("scripts.heat_dispatch", []),          # hourly heat-side dispatch (DH + whole-building)
]
OPTIONAL = [                                # figures: refresh, but don't fail the run on a plotting hiccup
    ("scripts.paper_figures", []),
    ("scripts.diagnostic_figures", []),
]


def main():
    t0 = time.time()
    for i, (mod, args) in enumerate(STEPS, 1):
        print(f"\n========== [{i}/{len(STEPS)}] python -m {mod} {' '.join(args)} ==========", flush=True)
        r = subprocess.run([sys.executable, "-m", mod] + args, cwd=str(CODE), env=ENV)
        if r.returncode != 0:
            print(f"\n!!! FAILED at {mod} (exit {r.returncode}) after {time.time()-t0:.0f}s", flush=True)
            sys.exit(1)
    for mod, args in OPTIONAL:
        print(f"\n========== (figures) python -m {mod} ==========", flush=True)
        r = subprocess.run([sys.executable, "-m", mod] + args, cwd=str(CODE), env=ENV)
        if r.returncode != 0:
            print(f"  (figure step {mod} returned {r.returncode}; continuing)", flush=True)
    print(f"\n=== RERUN COMPLETE in {time.time()-t0:.0f}s ===", flush=True)


if __name__ == "__main__":
    main()
