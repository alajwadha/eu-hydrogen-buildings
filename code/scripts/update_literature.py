"""
code/scripts/update_literature.py
===================================
Continuously monitors academic literature relevant to this paper and
auto-updates paper/References_v1.bib with new, vetted references.

What it does:
  1. Searches Semantic Scholar + OpenAlex APIs for new papers
  2. Scores each paper for relevance to this study's topics
  3. Deduplicates against the existing .bib file
  4. Appends new entries to References_v1.bib
  5. Writes literature/new_papers.md — a human-readable report of
     what was found and which paper sections it is likely relevant to
  6. Tracks reference count toward the 100-reference minimum

What it does NOT do:
  ⚠️  It does NOT insert \\cite{} keys into the .tex files automatically.
  Citation placement is a judgment call for Ali and Abdul.
  Use new_papers.md to decide where each paper belongs.

Usage:
  python code/scripts/update_literature.py           # run once
  python code/scripts/update_literature.py --dry-run # preview only, no file changes

Schedule (optional, run weekly):
  On Mac/Linux add to crontab:
    0 9 * * 1 cd /path/to/eu-hydrogen-buildings && python code/scripts/update_literature.py

APIs used (all free, no API key required):
  - Semantic Scholar: https://api.semanticscholar.org
  - OpenAlex:         https://api.openalex.org
  - CrossRef:         https://api.crossref.org
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import urllib.parse
import urllib.request
import urllib.error

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parents[2]
BIB_FILE    = REPO_ROOT / "paper" / "References_v1.bib"
LIT_DIR     = REPO_ROOT / "literature"
REPORT_FILE = LIT_DIR / "new_papers.md"
SEEN_FILE   = LIT_DIR / "seen_dois.txt"          # tracks already-processed DOIs
LOG_FILE    = LIT_DIR / "search_log.jsonl"        # full search history

LIT_DIR.mkdir(parents=True, exist_ok=True)

# ── Search topics ─────────────────────────────────────────────────────────────
# Each entry: (query_string, [section_tags])
# Section tags tell Ali/Abdul which paper section a result is likely relevant to.
SEARCH_QUERIES = [
    # Core topic — hydrogen in buildings
    ("hydrogen heating buildings decarbonisation",
     ["literature_review:h2", "methodology", "discussion"]),
    ("hydrogen boiler residential net zero",
     ["literature_review:h2", "results"]),
    ("green hydrogen buildings sector EU",
     ["introduction", "literature_review:h2"]),

    # Heat pumps — competing technology
    ("heat pump electrification buildings Europe",
     ["literature_review:hp", "methodology"]),
    ("air source heat pump decarbonisation residential",
     ["literature_review:hp"]),
    ("heat pump cost learning rate 2050",
     ["methodology", "sensitivity"]),

    # EU energy policy context
    ("REpowerEU hydrogen strategy buildings",
     ["introduction", "literature_review:policy"]),
    ("EU buildings energy performance directive decarbonisation",
     ["introduction", "literature_review:buildings"]),
    ("net zero buildings Europe 2050 pathway",
     ["introduction", "literature_review:buildings"]),

    # Spatial / NUTS3 modelling
    ("NUTS3 regional heat demand Europe Hotmaps",
     ["methodology", "literature_review:spatial"]),
    ("spatially resolved building heating model Europe",
     ["methodology", "literature_review:spatial"]),

    # Switzerland specific
    ("Switzerland hydrogen energy buildings net zero",
     ["literature_review:switzerland", "results:rq2"]),
    ("Swiss energy strategy 2050 heating",
     ["literature_review:switzerland"]),

    # Techno-economic modelling
    ("techno-economic heating decarbonisation MILP optimisation",
     ["methodology"]),
    ("LP MILP optimisation energy buildings",
     ["methodology"]),
    ("carbon price heat decarbonisation residential",
     ["methodology", "sensitivity"]),

    # District heat + biomass (technologies in scope)
    ("district heating expansion Europe low carbon",
     ["literature_review:buildings", "methodology"]),

    # Hydrogen infrastructure + costs
    ("green hydrogen production cost 2030 2050",
     ["methodology", "literature_review:h2"]),
    ("hydrogen import Europe price trajectory",
     ["literature_review:h2", "results:rq2"]),
]

# ── Relevance scoring keywords ────────────────────────────────────────────────
HIGH_RELEVANCE = [
    "hydrogen", "heat pump", "building", "residential", "heating",
    "decarboni", "net zero", "NUTS", "Hotmaps", "district heat",
    "EU", "European", "Switzerland", "Swiss", "2050", "electrification",
    "boiler", "energy efficiency", "renovation", "building stock",
]
MEDIUM_RELEVANCE = [
    "energy system", "carbon", "climate", "renewable", "scenario",
    "optimisation", "optimization", "techno-economic", "pathway",
    "transition", "low carbon", "emission", "fossil fuel",
]
# Papers from these journals get a relevance bonus
PREFERRED_JOURNALS = [
    "energy", "applied energy", "energy policy", "energy conversion",
    "nature energy", "joule", "international journal of hydrogen",
    "renewable and sustainable energy", "energy and buildings",
    "oxford energy", "oies",
]
# Minimum year — exclude old papers unless highly cited
MIN_YEAR = 2018


# ── Utility: HTTP GET with retry ──────────────────────────────────────────────
def _get(url: str, retries: int = 3, pause: float = 1.5) -> Optional[dict]:
    headers = {"User-Agent": "eu-hydrogen-buildings-research/1.0 (academic)"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(pause * (attempt + 1))
            else:
                print(f"  [warn] GET failed: {url[:80]}... — {e}")
                return None


# ── Search APIs ───────────────────────────────────────────────────────────────
def search_semantic_scholar(query: str, limit: int = 15) -> list[dict]:
    """Search Semantic Scholar for papers matching query."""
    q = urllib.parse.quote(query)
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={q}&limit={limit}"
        f"&fields=title,authors,year,abstract,externalIds,venue,citationCount,openAccessPdf"
    )
    data = _get(url)
    if not data or "data" not in data:
        return []
    results = []
    for p in data["data"]:
        doi = (p.get("externalIds") or {}).get("DOI", "")
        results.append({
            "title":    p.get("title", ""),
            "authors":  [a.get("name", "") for a in (p.get("authors") or [])],
            "year":     p.get("year") or 0,
            "abstract": p.get("abstract") or "",
            "doi":      doi.lower() if doi else "",
            "venue":    p.get("venue") or "",
            "citations": p.get("citationCount") or 0,
            "pdf_url":  (p.get("openAccessPdf") or {}).get("url", ""),
            "source":   "semantic_scholar",
        })
    time.sleep(1.0)  # respect rate limit
    return results


def search_openalex(query: str, limit: int = 15) -> list[dict]:
    """Search OpenAlex for papers matching query."""
    q = urllib.parse.quote(query)
    url = (
        f"https://api.openalex.org/works"
        f"?search={q}&per-page={limit}"
        f"&filter=publication_year:>{MIN_YEAR - 1}"
        f"&sort=relevance_score:desc"
        f"&select=title,authorships,publication_year,abstract_inverted_index,"
        f"doi,primary_location,cited_by_count,open_access"
        f"&mailto=research@eu-hydrogen-buildings.org"
    )
    data = _get(url)
    if not data or "results" not in data:
        return []
    results = []
    for p in data["results"]:
        doi = (p.get("doi") or "").replace("https://doi.org/", "").lower()
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in (p.get("authorships") or [])
        ]
        venue = ""
        loc = p.get("primary_location") or {}
        src = loc.get("source") or {}
        venue = src.get("display_name") or ""

        # Reconstruct abstract from inverted index
        abstract = ""
        inv = p.get("abstract_inverted_index") or {}
        if inv:
            words = {pos: word for word, positions in inv.items()
                     for pos in positions}
            abstract = " ".join(words[i] for i in sorted(words))

        results.append({
            "title":    p.get("title") or "",
            "authors":  authors,
            "year":     p.get("publication_year") or 0,
            "abstract": abstract,
            "doi":      doi,
            "venue":    venue,
            "citations": p.get("cited_by_count") or 0,
            "pdf_url":  (p.get("open_access") or {}).get("oa_url") or "",
            "source":   "openalex",
        })
    time.sleep(0.5)
    return results


# ── Relevance scoring ─────────────────────────────────────────────────────────
def score_relevance(paper: dict) -> float:
    text = (
        (paper.get("title") or "") + " " +
        (paper.get("abstract") or "") + " " +
        (paper.get("venue") or "")
    ).lower()

    score = 0.0
    for kw in HIGH_RELEVANCE:
        if kw.lower() in text:
            score += 2.0
    for kw in MEDIUM_RELEVANCE:
        if kw.lower() in text:
            score += 1.0
    for j in PREFERRED_JOURNALS:
        if j.lower() in (paper.get("venue") or "").lower():
            score += 3.0
            break

    # Penalise old or uncited papers
    year = paper.get("year") or 0
    if year < MIN_YEAR:
        score *= 0.3
    elif year >= 2022:
        score += 2.0

    # Bonus for highly cited
    cites = paper.get("citations") or 0
    if cites > 100:
        score += 2.0
    elif cites > 30:
        score += 1.0

    return round(score, 1)


# ── BibTeX key generation ─────────────────────────────────────────────────────
def make_bib_key(paper: dict) -> str:
    """Generate a BibTeX key: FirstAuthorLastNameYEAR_FirstKeyword"""
    authors = paper.get("authors") or []
    if authors:
        last = authors[0].split()[-1]
        last = re.sub(r"[^a-zA-Z]", "", last)
    else:
        last = "Unknown"

    year = paper.get("year") or "XXXX"

    # First significant word from title
    title = paper.get("title") or ""
    stop = {"a", "an", "the", "of", "in", "on", "and", "for",
            "to", "with", "from", "role", "study"}
    words = [w for w in re.sub(r"[^a-zA-Z ]", "", title).split()
             if w.lower() not in stop]
    keyword = words[0].capitalize() if words else "Paper"

    return f"{last}{year}{keyword}"


# ── BibTeX entry generation ───────────────────────────────────────────────────
def make_bibtex_entry(paper: dict, key: str) -> str:
    authors = paper.get("authors") or ["Unknown"]
    author_str = " and ".join(authors[:6])
    if len(authors) > 6:
        author_str += " and others"

    title   = (paper.get("title") or "").replace("{", "").replace("}", "")
    year    = paper.get("year") or "XXXX"
    venue   = paper.get("venue") or ""
    doi     = paper.get("doi") or ""
    source  = paper.get("source") or ""
    score   = paper.get("relevance_score") or 0.0
    tags    = ", ".join(paper.get("section_tags") or [])

    doi_line  = f"  doi       = {{{doi}}},\n" if doi else ""
    url_line  = f"  url       = {{https://doi.org/{doi}}},\n" if doi else ""

    return (
        f"% [AUTO] Source: {source} | Relevance: {score} | Sections: {tags}\n"
        f"% Added: {date.today().isoformat()}\n"
        f"@article{{{key},\n"
        f"  author  = {{{author_str}}},\n"
        f"  title   = {{{{{title}}}}},\n"
        f"  journal = {{{venue}}},\n"
        f"  year    = {{{year}}},\n"
        f"{doi_line}"
        f"{url_line}"
        f"}}\n"
    )


# ── Load existing .bib DOIs and keys ─────────────────────────────────────────
def load_existing_bib(bib_file: Path) -> tuple[set, set]:
    """Returns (existing_dois, existing_keys)"""
    if not bib_file.exists():
        return set(), set()
    content = bib_file.read_text(encoding="utf-8")
    dois = set(re.findall(r"doi\s*=\s*\{([^}]+)\}", content, re.IGNORECASE))
    dois = {d.lower().strip() for d in dois}
    keys = set(re.findall(r"@\w+\{(\w+),", content))
    return dois, keys


def load_seen_dois(seen_file: Path) -> set:
    if not seen_file.exists():
        return set()
    return set(seen_file.read_text().splitlines())


def save_seen_doi(seen_file: Path, doi: str) -> None:
    with open(seen_file, "a") as f:
        f.write(doi + "\n")


def count_bib_entries(bib_file: Path) -> int:
    if not bib_file.exists():
        return 0
    return len(re.findall(r"^@\w+\{", bib_file.read_text(), re.MULTILINE))


# ── Main pipeline ─────────────────────────────────────────────────────────────
def run(dry_run: bool = False) -> None:
    print(f"\n{'='*60}")
    print(f"Literature Update — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    if dry_run:
        print("DRY RUN — no files will be modified\n")

    existing_dois, existing_keys = load_existing_bib(BIB_FILE)
    seen_dois = load_seen_dois(SEEN_FILE)
    skip_dois = existing_dois | seen_dois

    print(f"Existing .bib entries : {count_bib_entries(BIB_FILE)}")
    print(f"Already seen DOIs     : {len(skip_dois)}")
    print(f"Target                : 100 references minimum\n")

    all_candidates = []

    for query, section_tags in SEARCH_QUERIES:
        print(f"Searching: '{query[:55]}...'")

        for fetch_fn in [search_semantic_scholar, search_openalex]:
            papers = fetch_fn(query, limit=12)
            for p in papers:
                p["section_tags"] = section_tags
                p["relevance_score"] = score_relevance(p)
            all_candidates.extend(papers)

    print(f"\nTotal raw results     : {len(all_candidates)}")

    # Deduplicate by DOI within this batch
    seen_in_batch: set[str] = set()
    unique = []
    for p in all_candidates:
        doi = p.get("doi") or ""
        key = doi if doi else p.get("title", "").lower()[:60]
        if key and key not in seen_in_batch:
            seen_in_batch.add(key)
            unique.append(p)

    print(f"After deduplication   : {len(unique)}")

    # Filter out already-known papers
    new_papers = []
    for p in unique:
        doi = p.get("doi") or ""
        if doi and doi in skip_dois:
            continue
        if p.get("year") and p["year"] < MIN_YEAR and p.get("citations", 0) < 50:
            continue
        if p["relevance_score"] < 4.0:
            continue
        new_papers.append(p)

    # Sort by relevance score descending
    new_papers.sort(key=lambda x: x["relevance_score"], reverse=True)
    print(f"New relevant papers   : {len(new_papers)}")

    if not new_papers:
        print("\nNo new papers to add — literature is up to date.")
        _write_report([], existing_dois, dry_run)
        return

    # Generate BibTeX entries
    added = []
    bib_block = "\n\n% ── AUTO-ADDED by update_literature.py ─────────────────────────\n"
    bib_block += f"% Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    bib_block += f"% {len(new_papers)} new papers found\n\n"

    for p in new_papers:
        key = make_bib_key(p)
        # Ensure key uniqueness
        if key in existing_keys:
            key = key + "a"
        existing_keys.add(key)

        entry = make_bibtex_entry(p, key)
        bib_block += entry + "\n"

        doi = p.get("doi") or ""
        p["_bib_key"] = key
        added.append(p)

        if not dry_run:
            if doi:
                save_seen_doi(SEEN_FILE, doi)

    # Append to .bib file
    if not dry_run and added:
        with open(BIB_FILE, "a", encoding="utf-8") as f:
            f.write(bib_block)
        print(f"\n✓ Added {len(added)} entries to {BIB_FILE.name}")
    elif dry_run:
        print(f"\n[DRY RUN] Would add {len(added)} entries to {BIB_FILE.name}")
        print("\nSample entries:")
        print(bib_block[:1500] + "...")

    # Write report
    _write_report(added, existing_dois, dry_run)

    # Log run
    if not dry_run:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "queries": len(SEARCH_QUERIES),
                "raw_results": len(all_candidates),
                "new_added": len(added),
                "bib_total": count_bib_entries(BIB_FILE),
            }) + "\n")


def _write_report(added: list, existing_dois: set, dry_run: bool) -> None:
    """Write literature/new_papers.md — human-readable report for Ali/Abdul."""
    total_bib = count_bib_entries(BIB_FILE)
    remaining = max(0, 100 - total_bib)

    lines = [
        f"# Literature Update Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"{'> DRY RUN — no files modified' if dry_run else ''}",
        f"",
        f"## Reference Count",
        f"| Metric | Count |",
        f"|---|---|",
        f"| Current `.bib` entries | {total_bib} |",
        f"| New papers added this run | {len(added)} |",
        f"| Still needed (min 100) | {remaining} |",
        f"",
    ]

    if added:
        lines += [
            f"## New Papers Added",
            f"> ⚠️ These have been added to `References_v1.bib` automatically.",
            f"> **Citation placement** (`\\cite{{key}}` in the `.tex` files) requires Ali/Abdul judgment.",
            f"> Use the section tags below to identify where each paper likely belongs.",
            f"",
        ]

        # Group by section tags
        by_section: dict[str, list] = {}
        for p in added:
            for tag in (p.get("section_tags") or ["untagged"]):
                by_section.setdefault(tag, []).append(p)

        section_labels = {
            "introduction":              "Introduction",
            "literature_review:h2":      "Literature Review — Hydrogen in Buildings",
            "literature_review:hp":      "Literature Review — Heat Pumps",
            "literature_review:buildings": "Literature Review — Buildings Decarbonisation",
            "literature_review:spatial": "Literature Review — Spatial Modelling",
            "literature_review:switzerland": "Literature Review — Switzerland",
            "literature_review:policy":  "Literature Review — EU Policy",
            "methodology":               "Methodology",
            "results":                   "Results",
            "results:rq2":               "Results — Switzerland (RQ2)",
            "discussion":                "Discussion",
            "sensitivity":               "Sensitivity Analysis",
        }

        for tag, papers in sorted(by_section.items()):
            label = section_labels.get(tag, tag)
            lines.append(f"### {label}")
            for p in papers:
                key    = p.get("_bib_key", "?")
                title  = p.get("title") or "Untitled"
                year   = p.get("year") or "?"
                auth   = (p.get("authors") or ["?"])[0].split()[-1]
                venue  = p.get("venue") or ""
                score  = p.get("relevance_score") or 0
                cites  = p.get("citations") or 0
                doi    = p.get("doi") or ""
                doi_link = f" | [DOI](https://doi.org/{doi})" if doi else ""

                lines += [
                    f"**`\\cite{{{key}}}`** — {auth} ({year})",
                    f"*{title}*  ",
                    f"_{venue}_ | Relevance: {score} | Citations: {cites}{doi_link}",
                    f"",
                ]
            lines.append("")
    else:
        lines.append("## No new papers found this run — literature is up to date.\n")

    lines += [
        "---",
        "## How to Cite in the Paper",
        "1. Find a paper above in the relevant section",
        "2. Open `paper/sections/<section>.tex`",
        "3. Add `\\cite{KEY}` at the appropriate point",
        "4. Run `make` in `paper/` to rebuild the PDF",
        "",
        "## Search Queries Used This Run",
    ]
    for q, tags in SEARCH_QUERIES:
        lines.append(f"- `{q}` → {', '.join(tags)}")

    report_path = REPORT_FILE if not dry_run else LIT_DIR / "new_papers_dryrun.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{'[DRY RUN] ' if dry_run else ''}Report written to {report_path.name}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search academic APIs and update References_v1.bib."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview results without modifying any files."
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run)
