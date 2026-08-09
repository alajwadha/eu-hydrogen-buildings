# Luxembourg — EUBUCCO building-stock integration

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alajwadha/eu-hydrogen-buildings/blob/main/notebooks/luxembourg.ipynb)

EUBUCCO v0.2 building-stock integration for Luxembourg — our smallest test country (~186k buildings). The build serves as a template for the other 28 country folders.

**Result:** 7.84 TWh residential heat demand vs Hotmaps 8.27 TWh (-5.2%, well within ±15%). Four-source reconciliation clusters tightly (BSO 6.75 / Odyssee 7.20 / ours 7.84 / Hotmaps 8.27 TWh).

## Why Luxembourg

- Smallest building stock in the EU-27 (~186k buildings vs Germany's ~30M).
- Single NUTS2 region (LU00) and single NUTS3 region (LU000) — no aggregation complexity.
- High-quality national data available for cross-validation (STATEC, Klima-Agence, Odyssee-Mure).
- Heating-dominant climate (~3,217 HDD/yr vs Belgium 2,894), warranting a 1.112 climate multiplier for TABULA Belgium intensities.

## Pipeline split (4 scripts, 2 environments)

```
                    Google Colab (runs the heavy pipeline)
                    --------------------------------------
01_download.py      EUBUCCO LU00.parquet (~30 MB) from s3.eubucco.com
        v
02_classify.py      Per-building classification (SFH/MFH/non-res)
        v
        |       LU_buildings_classified.parquet
        v
03_heat_intensity   Per-vintage TABULA intensities + climate correction
        v
        |       LU_buildings_with_heat_demand.parquet
        |       LU_heat_intensity_summary.csv             Pushed to GitHub
        |       LU_reconciliation_with_hotmaps.csv        (committed in repo)
        |       (and other CSVs + provenance)
        v
                    Local VS Code (regenerates figures)
                    -----------------------------------
04_diagnostics.py   <- pulls all the above from GitHub
        v
                    LU_diagnostics_clean.pdf  (8-page paper-quality)
```

**Why the split?** Script 04 only consumes already-computed CSVs and parquets — fast, deterministic, and best run locally where the matplotlib version is pinned. This means:

- Reviewers can clone the repo and re-render the diagnostic PDF locally without any cloud setup.
- You don't need a Colab session just to tweak a chart.

**Why Colab still runs 01-03 (and not just locally)?** Historical reason: when GBA cross-check was part of the pipeline, script 02 streamed a 10 GB tile that needed gigabit + Drive caching. With GBA removed, the bottleneck is gone and 01-03 actually run fine on a laptop (~10 seconds end-to-end). Colab is now optional, not required.

## How to run

### Option 1 (recommended) — Colab notebook + push to GitHub

1. Click the [Open In Colab badge](https://colab.research.google.com/github/alajwadha/eu-hydrogen-buildings/blob/main/notebooks/luxembourg.ipynb) above.
2. Add a fine-grained GitHub PAT to Colab Secrets as `GITHUB_PAT` (Contents: read+write on this repo only — instructions inside the notebook).
3. `Runtime -> Run all`.

The notebook clones the repo, runs scripts 01-03 on Colab's VM, stores raw data on your Drive (`MyDrive/eu-hydrogen-raw/`), commits the processed outputs (CSVs + parquets), and pushes to `main`. Total time **~30 seconds** end-to-end.

After the push, run script 04 locally to regenerate the diagnostic PDF (see Step B below).

### Option 2 — Run everything locally

If you want to skip Colab entirely (any modern laptop works now that GBA streaming is gone):

```powershell
cd path/to/eu-hydrogen-buildings
git pull
pip install -r requirements.txt
python code/scripts/country_build/01_download.py
python code/scripts/country_build/02_classify.py
python code/scripts/country_build/03_heat_intensity.py
python code/scripts/country_build/04_diagnostics.py
```

Total time ~30-60 seconds end-to-end on a modern laptop. Or use VS Code tasks (`Ctrl+Shift+P -> Tasks: Run Task -> 🇱🇺 LU: ▶ RUN ALL 4 SCRIPTS`).

### Step B — Local diagnostic PDF (after Colab path)

After Option 1 pushes successfully:

```powershell
cd path/to/eu-hydrogen-buildings
git pull
python code/scripts/country_build/04_diagnostics.py
git add code/data/processed/lu/LU_diagnostics_clean.pdf countries/Luxembourg/data/LU_diagnostics_clean.pdf
git commit -m "Regenerate LU diagnostic PDF"
git push
```

Or via task: `Ctrl+Shift+P -> Tasks: Run Task -> 🇱🇺 LU: 4 — Diagnostic PDF (local, fast)`.

## Datasets used

| Dataset | Role | Coverage | License | Size (LU) |
|---|---|---|---|---|
| EUBUCCO v0.2 (LU00) | Primary: footprints + height + type + age | 186,171 buildings | ODbL | ~28 MB |
| TABULA Belgium (VITO 2011) | Per-vintage residential intensity, climate-corrected | 18 cohort x class rows | research-use | <1 KB |
| EU BSO 2021 LU | Independent intensity benchmark | 6 cohort rows | open | <1 KB |
| Luxembourg national parameters | HDD, retrofit blend, DHW | 11 parameters | open | <1 KB |

**Note on GBA (Zhu et al. 2025):** earlier iterations of this build also pulled the GBA.ODbLPolygon tile (~10 GB) for a residential-area cross-check. That cross-check found GBA's residential area to be ~1.4× EUBUCCO's, consistent with GBA's looser polygon definition that includes sheds, extensions, and garages. This is preserved in the paper's methodology section as a one-time published finding citing Zhu et al. 2025. GBA is no longer pulled at pipeline runtime because (a) the 10 GB tile took ~22 minutes to bbox-filter through Drive FUSE, dominating total Colab time, and (b) the TUM-hosted WFS endpoint has a server-side response-size cap (~1 MB before truncation gets common, fully reliable only up to ~200 features per request) that would require thousands of paged requests with no net speed gain. The pre-removal `load_gba()` function is preserved in git history (commit `d248600`) if a fresh cross-check is ever needed.

## Outputs

**Committed to git** (the summary tables and the diagnostic PDF, so a reviewer can check
the build without rerunning the pipeline):

```
code/data/processed/lu/
  LU_aggregated_NUTS3.csv                    (per-class counts + areas)
  LU_heat_demand_nuts3.csv                   (per-NUTS3 demand, the model input)
  LU_heat_intensity_summary.csv              (per-class x per-cohort heat demand)
  LU_reconciliation_with_hotmaps.csv         (4-way source comparison)
  LU_model_comparison.csv                    (new vs existing building_stock_nuts3 row)
  LU_diagnostics_clean.pdf                   (8-page paper-quality PDF — see below)
  raw_data_provenance.txt                    (URL, MD5, citation for the EUBUCCO input)
```

Summary outputs are mirrored to `countries/Luxembourg/data/` for the country-folder reader.

**Not committed:**

```
code/data/processed/lu/
  LU_buildings_classified.parquet            (~22 MB — 186k rows x 8 cols)
  LU_buildings_with_heat_demand.parquet      (~23 MB — adds intensity + demand)
code/data/raw/
  the 28 MB EUBUCCO source file
```

The per-building parquets are gitignored (`.gitignore`: `code/data/processed/**/*.parquet`)
and no parquet has ever been committed to this repository. Regenerate them by running
scripts 01-03; script 04 and everything downstream then work from the local copies. The
EUBUCCO source is likewise gitignored: Colab keeps it cached on Drive, and locally script 01
refetches it on first run (one HTTP fetch from `s3.eubucco.com`, takes seconds).

**Data policy (revised June 2026):** an earlier note here said the derived parquets were
committed. They were not, and at 29-country scale they would add roughly 38 GB, so the
policy is now explicit: parquets stay out of git and are regenerated from the pipeline.

## The 8-page diagnostic PDF (script 04)

| Page | Content |
|---|---|
| 1 | Headline reconciliation: ours/Hotmaps/BSO/Odyssee with +/-15% Hotmaps band |
| 2 | Heat demand by class x cohort — reveals 99.8% sits in "unknown" cohort |
| 3 | Intensity-vs-vintage curves (TABULA BE x LU/BE climate x retrofit + DHW) |
| 4 | Cohort & residential-area coverage transparency (0.04% have construction_year) |
| 5 | Sensitivity tornado — which assumption moves 7.84 TWh the most |
| 6 | Method comparison: (A) top-down vs (B) fallback-dominated vs (C) per-vintage |
| 7 | Class-level reconciliation — reveals SFH/OTHER disagreement between ours and Hotmaps |
| 8 | Empirical construction-year distribution for the 74 buildings that have it |

Palette: Wong (Okabe-Ito), colourblind-safe. Defined in `code/src/Visualise.py` as `WONG_PALETTE` so the same palette is available for paper figures (use `from Visualise import WONG_PALETTE, get_palette`).

## Classification rules (script 02)

```
if EUBUCCO_type starts with "non-"     ->  NON_RESIDENTIAL
if floors_est >= 6 AND footprint >= 800 ->  MFH_HIGH
if floors_est <= 2 AND footprint < 250  ->  SFH
if 2 < floors_est <= 5                  ->  MFH_LOW
otherwise                               ->  MFH_HIGH (ambiguous mid-density)
```

Floor estimation: `floors = round(height_m / 3.0)` for residential, `/ 3.5` otherwise. Heated area: `footprint_area_m2 * floors * 0.85` (0.85 = usable area fraction after internal walls + corridors).

## Heat intensity methodology (script 03)

For each residential building:

```
intensity_kwh_m2_yr =
    TABULA_BE[class, cohort].sh_intensity            # base space-heating
    * climate_multiplier_LU_BE  (1.112 = 3217/2894)  # Eurostat HDD ratio
    * retrofit_blend            (0.813)              # 55% orig + 35% std*0.65 + 10% adv*0.35
    + DHW_intensity              (22 SFH, 19 MFH)    # TABULA convention

For buildings with no construction_year (~99.96% in LU):
    fallback intensity = weighted average across cohorts using national age structure
```

Non-residential gets a flat 140 kWh/m2/yr placeholder (EU BSO LU non-res average, **flagged as approximate** — see methodology page 4 of the diagnostic PDF).

## Reproducibility

Each download writes URL + MD5 + citation into `raw_data_provenance.txt` (committed). Source versions:

- EUBUCCO v0.2 DOI 10.5281/zenodo.7225259 (Milojevic-Dupont et al. 2023)
- TABULA BE: VITO report 2011/TEM/R/091763 (Cyx et al. 2011)
- Eurostat HDD: dataset `nrg_chdd_a`, 5-yr average 2018-2022
- GBA (referenced in methods, not pulled at runtime): mediaTUM ID 1782307 (Zhu et al. 2025)

Full bib entries in `paper/References_v1.bib`.

## Open questions (pending Abdul review)

- Heat intensity methodology: 6 specific decisions documented in `literature/intensity_source_methodology.md` section 5.
- Whether the per-vintage TABULA approach is the right framing for the paper, given LU's 0.04% cohort coverage (see diagnostic PDF page 6).
- Class-split disagreement with Hotmaps (page 7 of the diagnostic): genuine finding or artifact of our classification rule?
- Once LU is signed off: which 1-2 countries to build next (recommend one high-coverage like FR/DE, one low like BG/HR) before full 29-country scale-out.
