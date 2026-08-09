"""
Include.py — Environment setup (varnerlab pattern)
====================================================
Called at the top of every script in code/scripts/.
Sets up the Python path, imports core modules, and confirms the environment.

Usage (in any script):
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from Include import *

Or from Spyder / Jupyter:
    exec(open('code/Include.py').read())
"""

import sys
import os
from pathlib import Path

# ── Repo root ─────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent  # eu-hydrogen-buildings/
CODE_DIR  = REPO_ROOT / "code"
SRC_DIR   = CODE_DIR  / "src"
DATA_DIR  = CODE_DIR  / "data"
RAW_DIR   = DATA_DIR  / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RESULTS_DIR   = CODE_DIR  / "results"
FIGS_DIR      = REPO_ROOT / "paper" / "figs"

# Add src to path so modules are importable
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(CODE_DIR))

# ── Core imports ──────────────────────────────────────────────────────────────
from src.Config import *

print(f"✓ eu-hydrogen-buildings environment loaded")
print(f"  REPO_ROOT : {REPO_ROOT}")
print(f"  DATA_DIR  : {DATA_DIR}")
print(f"  RESULTS   : {RESULTS_DIR}")
print(f"  PAPER FIGS: {FIGS_DIR}")
