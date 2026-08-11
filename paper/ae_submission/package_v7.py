"""Refresh the V7 upload folder from the built deliverables.

This exists because the folder went stale and shipped a wrong number. The folder held copies of
V7.pdf, V7.docx and SI.pdf, its own README said "the two are refreshed together", and
nothing refreshed them. A correction to the demand-weighted derived ceiling reached the
LaTeX sources, both compiled PDFs and both papers, and the commit message said so; the
four files an editor would actually receive kept the old value for a further revision.
No gate could see it, because every gate read the .tex corpus and these are renderings.

Copying is a build step, not a check. check_submission.py asserts the copies match; this
script is what makes them match. Keeping the two apart means a gate never silently repairs
the thing it is judging.

It also prunes. Refreshing alone left the previous revision's four files sitting in the
folder beside the current ones, so the set an editor would receive held two versions of
the same manuscript and nothing said which to take. What ships is the folder, not the
subset a script happens to touch.

Run:  python3 paper/ae_submission/package_v7.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
UPLOAD = HERE / "V7"

# Everything else in the folder is packaged output and gets pruned.
KEEP = {"README.md"}

# source -> the name Editorial Manager receives
PAIRS = [
    (HERE / "V7.pdf", "Hydrogen_residential_heating_V7.pdf"),
    (HERE / "V7.docx", "Hydrogen_residential_heating_V7.docx"),
    (HERE / "SI.pdf", "Hydrogen_residential_heating_SI_V7.pdf"),
    # The graphical abstract is a separate Editorial Manager upload and was missing from
    # this folder entirely, while the gate validated it in place under paper/figs/.
    (REPO / "paper" / "figs" / "paper" / "graphical_abstract_wide.png",
     "Hydrogen_residential_heating_graphical_abstract_V7.png"),
]


def stale() -> list[tuple[Path, Path]]:
    """Pairs whose upload copy differs from the deliverable it is a copy of."""
    out = []
    for src, name in PAIRS:
        dst = UPLOAD / name
        if not src.exists():
            continue
        if not dst.exists() or src.read_bytes() != dst.read_bytes():
            out.append((src, dst))
    return out


def orphans() -> list[Path]:
    """Files in the upload folder that are not part of the current upload set."""
    expected = {name for _, name in PAIRS} | KEEP
    if not UPLOAD.is_dir():
        return []
    return sorted(p for p in UPLOAD.iterdir() if p.is_file() and p.name not in expected)


def main() -> int:
    UPLOAD.mkdir(exist_ok=True)
    missing = [s for s, _ in PAIRS if not s.exists()]
    if missing:
        print("cannot package; build these first:")
        for m in missing:
            print(f"  {m.relative_to(REPO)}")
        return 1
    todo = stale()
    for src, dst in todo:
        shutil.copy2(src, dst)
        print(f"refreshed {dst.name} from {src.relative_to(REPO)}")
    if not todo:
        print(f"upload folder already matches the built deliverables ({len(PAIRS)} files).")
    for old in orphans():
        old.unlink()
        print(f"pruned {old.name}, not part of the current upload set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
