# Belgium — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country BE`).
**Config:** `code/data/country_config/be.yaml`.

Belgium is a **direct-TABULA** country in build group 5 (AT + BE, NL, IE; Northwestern temperate Europe). Note: `be_intensities.csv` already existed in the repo as the LU proxy — the same file is the direct TABULA source for BE-as-country.

## 1. Headline facts

- **TABULA source:** VITO (Flemish Institute of Technological Research, Mol) with BBRI/WTCB/CSTC. Scientific report Cyx, Renders, Van Holm, Verbeke (2011) VITO 2011/TEM/R/091763.
- **HDD:** BE 2018–2022 mean = **2520** (Eurostat estimate). **Option B applied:** `tabula_reference_hdd = 2900` (Uccle/Brussels KU Leuven Lirias long-term mean), `climate_multiplier = 2520/2900 = 0.869` to scale brochure values down to national-mean operation. The 15% gap between reference and national mean exceeds the 10% Option B trigger threshold.
- **NUTS:** 11 NUTS2 (BE10 + BE2x Flanders + BE3x Wallonia), 44+ NUTS3 (Verviers split BE336/BE337 from NUTS 2016 onward). Stable.
- **Retrofit:** Three regional vehicles — VEKA (Flanders), Wallonia Primes Habitation, Brussels RENOLUTION. LIFE BE REEL! ~8,000 deep-renovated dwellings. Climact 2024: pace needs to triple Flanders, quadruple Wallonia/Brussels for 2050 targets. Shares 0.82/0.13/0.05 reflect a low deep-renovation base.
- **Retrofit factors:** standard 0.60, advanced 0.40 (VITO case-study averages; provisional).
- **DHW:** SFH 22, MFH 19 kWh/m²/yr (VITO 2011 scientific report).
- **Hotmaps 2015 benchmark:** ~65 TWh (estimate; BPIE/Enerdata gives 69.2 TWh for 2018; sum BE NUTS3 rows exactly).
- **Comfort regime:** No deflator. BE is cold-temperate; TABULA reference matches operation; Sunikka-Blank/Galvin prebound applies marginally but no BE-specific stock-wide deflator is published.

## 2. Sources

- BE TABULA Scientific Report (VITO): episcope.eu/fileadmin/tabula/public/docs/scientific/BE_TABULA_ScientificReport_VITO.pdf
- Cyx W., Renders N., Van Holm M., Verbeke S. (2011). IEE TABULA — Belgian Scientific Report. VITO 2011/TEM/R/091763.
- Climact (2024). Upscaling the financing of Residential Renovation in Belgium.
- LIFE BE REEL! (VEKA-led, ~8,000 deep-renovated dwellings).
- Statbel housing census 2021 (cohort distribution).
- KU Leuven Lirias 571894 — Uccle / Brussels long-term HDD.
- Odyssee-Mure Belgium 2022 — residential heating ~74% of HH FE, ~17 MWh/dwelling/yr climate-corrected.

## 3. Verification status

### Verified
- 11 BE NUTS2 / 44+ NUTS3 (NUTS 2016 codes).
- TABULA source = BE direct (`be_intensities.csv` shared with LU proxy).
- `tabula_reference_hdd = 2900` (Uccle).
- `climate_multiplier = 0.8690` (2520/2900) — Option B applied.

### Needs verify
- HDD 2018-2022 mean — pull exact Eurostat `nrg_chdd_a`.
- Retrofit factors (0.60/0.40), DHW (22/19) — provisional.
- Retrofit shares (0.82/0.13/0.05) — modelling assumption; refine by region (Flanders ~0.85 unrenovated, Wallonia ~0.80, Brussels ~0.78 per Climact 2024 ranges).
- Hotmaps total (65) — sum `building_stock_nuts3.csv` exactly.
- Verviers BE336/BE337 split — verify EUBUCCO v0.2 mapping handles both subcodes.
