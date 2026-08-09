#!/usr/bin/env python3
"""Assemble the standalone model repository, ready to push.

The published repository carries the model and nothing else: no manuscript, no figures, no
results, and no third-party dataset. Input data is fetched by `scripts/download_data.py`
from the original providers, so nobody redistributes Eurostat, Hotmaps, EUBUCCO, GISCO or
EMBER data under a licence that is not theirs to grant.

This script does not touch GitHub. It writes a directory you then push, because repository
creation needs a credential this environment does not hold.

Run:
    cd code && python3 -m scripts.make_model_repo --out ~/eu-h2-buildings-model

Then:
    cd ~/eu-h2-buildings-model
    git init -b main && git add -A
    git commit -m "Model for the European hydrogen buildings assessment"
    gh repo create eu-h2-buildings-model --private --source=. --push
    gh api -X PUT repos/<owner>/eu-h2-buildings-model/collaborators/<co-author> \\
        -f permission=push
"""
from __future__ import annotations
import argparse
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# What ships. Everything else is deliberately left behind.
SRC_MODULES = ["BuildingStock.py", "Config.py", "CountryConfig.py", "Economics.py",
               "Emissions.py", "Optimisation.py", "Policy.py", "PowerUC.py",
               "Simulation.py", "Visualise.py", "__init__.py"]
SCRIPTS = ["__init__.py", "download_data.py", "heat_load_profile.py"]
ROOT_FILES = ["run.py", "requirements.txt", "LICENSE"]

GITIGNORE = """\
__pycache__/
*.pyc
.DS_Store

# Fetched from the providers, never committed.
data/raw/
data/processed/

# Reproduce from the code and the fetched inputs.
results/
figures/
"""


def copy(src: Path, dst: Path) -> bool:
    if not src.exists():
        print("  missing, skipped:", src.relative_to(REPO))
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="directory to assemble into")
    ap.add_argument("--force", action="store_true", help="overwrite an existing directory")
    a = ap.parse_args()

    out = Path(a.out).expanduser().resolve()
    if out.exists():
        if not a.force:
            return int(bool(sys.stderr.write(
                f"{out} exists. Pass --force to overwrite.\n")) ) or 1
        shutil.rmtree(out)
    out.mkdir(parents=True)

    n = 0
    for m in SRC_MODULES:
        n += copy(REPO / "code" / "src" / m, out / "src" / m)
    for s in SCRIPTS:
        n += copy(REPO / "code" / "scripts" / s, out / "scripts" / s)
    for f in ROOT_FILES:
        n += copy(REPO / f, out / f)
    n += copy(REPO / "code" / "Include.py", out / "Include.py")

    # Our own per-country assumptions. Not third-party, so they ship.
    cfg = REPO / "code" / "data" / "country_config"
    for y in sorted(cfg.glob("*.yaml")):
        n += copy(y, out / "data" / "country_config" / y.name)

    readme = REPO / "code" / "scripts" / "model_repo_README.md"
    if readme.exists():
        shutil.copy2(readme, out / "README.md")
        n += 1
    (out / ".gitignore").write_text(GITIGNORE)
    n += 1

    print(f"\n{n} files assembled in {out}")
    print("\nCheck before pushing:")
    print("  - no data/raw or data/processed  ->", not (out / "data" / "raw").exists()
          and not (out / "data" / "processed").exists())
    print("  - no results                     ->", not (out / "results").exists())
    print("  - no manuscript                  ->", not (out / "paper").exists())
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"  - total size                     -> {size / 1024:.0f} kB")
    print("\nThen: git init -b main && git add -A && git commit && gh repo create")
    return 0


if __name__ == "__main__":
    sys.exit(main())
