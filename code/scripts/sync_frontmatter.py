"""Copy the AE abstract, highlights and title from V5.tex into frontmatter_body.tex.

The Word twin is built by pandoc from `frontmatter_body.tex` plus the section files, not
from `V5.tex`, so the abstract and highlights existed twice. They diverged: the Word
file shipped for four days with an abstract V5.tex no longer carried. This script makes
V5.tex the single source and the gate checks the two still agree afterwards.

Run:  cd code && PYTHONPATH=. python -m scripts.sync_frontmatter
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AE = REPO / "paper" / "ae_submission"
MAIN = AE / "V5.tex"
FM = AE / "frontmatter_body.tex"
BUILD = AE / "build.py"


def _block(tex: str, env: str) -> str:
    m = re.search(r"\\begin\{" + env + r"\}\n(.*?)\\end\{" + env + r"\}", tex, re.S)
    if not m:
        raise SystemExit(f"V5.tex has no {env} environment")
    return m.group(1).strip()


def main() -> None:
    main_tex = MAIN.read_text(encoding="utf-8")
    abstract = _block(main_tex, "abstract")
    highlights = _block(main_tex, "highlights")
    title = re.search(r"\\title\{(.*?)\}\n", main_tex, re.S).group(1).strip()

    fm = FM.read_text(encoding="utf-8")
    fm = re.sub(r"(\\section\*\{Abstract\}\n\n).*?(\n\n%% HIGHLIGHTS)",
                lambda m: m.group(1) + abstract + m.group(2), fm, flags=re.S)
    fm = re.sub(r"(\\section\*\{Highlights\}\n\n\\begin\{itemize\}\n).*?(\n\\end\{itemize\})",
                lambda m: m.group(1) + highlights + m.group(2), fm, flags=re.S)
    FM.write_text(fm, encoding="utf-8")

    build = BUILD.read_text(encoding="utf-8")
    build = re.sub(r"DEFAULT_TITLE = .*?\n(?=\n\n)", "DEFAULT_TITLE = " + repr(title) + "\n",
                   build, count=1, flags=re.S)
    BUILD.write_text(build, encoding="utf-8")

    print(f"synced abstract ({len(abstract.split())} tokens), "
          f"{len(highlights.splitlines())} highlights and the title into "
          f"{FM.relative_to(REPO)} and {BUILD.relative_to(REPO)}")


if __name__ == "__main__":
    main()
