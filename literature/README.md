# literature/

Project literature, methodology documents, and assumption tracking.

## Files

| File / Folder | Description |
|---|---|
| `assumptions_register.md` | **All modelling assumptions** with provenance and status tags. Authoritative source for paper methods section. |
| `step1_policy_research_summary.md` | Research underlying the policy module (boiler bans, ETS2, grid CO2). |
| `step2_economics_research_summary.md` | Research underlying the economics module (LCOH, fuel prices, labour multipliers). |
| `step3_buildingstock_research_summary.md` | Research underlying the building-stock module (Hotmaps, Eurostat, EUBUCCO build, HP/DH feasibility). |
| `intensity_source_methodology.md` | Heat-intensity (kWh/m²/yr) source decision matrix and methodology for the LU script 03. |
| `luxembourg/` | Methodology + data dictionaries for the EUBUCCO building-stock build. |
| `new_papers.md` | Latest report from the literature scanner — papers found, relevance scores, suggested sections. |
| `seen_dois.txt` | DOIs already processed — prevents duplicates across literature-scan runs. |
| `search_log.jsonl` | Log of every literature scan (timestamp, queries, papers added). |

## How to update the literature

```bash
# Run from repo root
python code/scripts/update_literature.py

# Preview without changing files
python code/scripts/update_literature.py --dry-run
```

## How to cite a paper in the manuscript

1. Open `literature/new_papers.md`
2. Find a paper in the relevant section
3. Copy its `\cite{KEY}` 
4. Paste into the appropriate `paper/sections/*.tex` file
5. Run `make` in `paper/` to rebuild the PDF

## ⚠️ Important

- Papers are added to `References_v1.bib` **automatically**
- `\cite{}` placement in `.tex` files is **manual** — Ali and Abdul decide where each citation goes
- Run weekly to catch new publications
- All entries tagged `[AUTO]` in the `.bib` should be verified before final submission
