# Ireland — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country IE`).
**Config:** `code/data/country_config/ie.yaml`.

Ireland is a **direct-TABULA** country in build group 5 (AT + BE, NL, IE; Northwestern temperate Europe).

## 1. Headline facts

- **TABULA source:** Energy Action Ltd (Badurek, Hanratty, Sheldrick 2012) — NOT UCD or SEAI as sometimes assumed. 34 dwelling types across 10 age bands. Only ONE apartment archetype (pre-1977) — MFH_LOW and MFH_HIGH values in our build are based on that one archetype with cohort scaling, flagged.
- **HDD:** IE 2018–2022 mean = **2560** (Eurostat estimate). `tabula_reference_hdd = 2600` (Dublin Airport / DEAP convention). `climate_multiplier = 2560/2600 = 0.985` — near-identity, no Option B trigger.
- **NUTS:** 3 NUTS2 (IE04 Northern & Western, IE05 Southern, IE06 Eastern & Midland — post-2018 NUTS 2016 revision from previous 2 regions). 8 NUTS3. EUBUCCO v0.2 uses NUTS 2021 boundaries.
- **CONSTRUCTION-YEAR coverage in EUBUCCO IE: <15%** (BER database not ingested into EUBUCCO; BAG-equivalent absent). Significant unknown-cohort fallback expected. Consider supplementing with SEAI BER public research download in follow-up work.
- **Retrofit:** SEAI Better Energy Homes, One Stop Shop, Warmer Homes (free for low-income). 2023 alone: 47,953 upgrades incl. 13,850 to B2 standard. Cumulative 2019-2023 ~125k upgrades. Target: 500k homes to B2 + 400k heat pumps by 2030. Shares 0.72/0.20/0.08 reflect this acceleration.
- **Retrofit factors:** standard 0.55, advanced 0.25 (IE TABULA "usual" ~45% reduction, "advanced" NZEB-equivalent ~75% reduction).
- **DHW:** 15 kWh/m²/yr (IE TABULA / DEAP convention).
- **Hotmaps 2015 benchmark:** ~26 TWh (SEAI Heating & Cooling in Ireland Today: 26.3 TWh useful 2015).
- **Comfort regime:** Documented under-heating in IE (ESRI WP749 fuel-poverty; 14% of households 2024 cannot afford adequate warmth, ESRI). But no stock-wide published deflator (Goodman/UCD/SEAI ratio not published). TABULA-reference operation kept as central case; the under-heated low-income decile is a candidate follow-up refinement.

## 2. Sources

- IE TABULA Scientific Report (Energy Action): episcope.eu/fileadmin/tabula/public/docs/scientific/IE_TABULA_ScientificReport_EnergyAction.pdf
- IE TABULA Brochure (2012): episcope.eu/fileadmin/tabula/public/docs/brochure/IE_TABULA_TypologyBrochure_EnergyAction.pdf
- Badurek M., Hanratty M., Sheldrick W. (2012). Irish building typology.
- SEAI (2023). Retrofit Full Year Report.
- SEAI (2023). Heating and Cooling in Ireland Today.
- SEAI (2023). Energy in Ireland 2023.
- Goodman et al. ESRI WP749 — fuel-poverty / thermostat setpoints.
- CSO Census 2022 — dwelling-period histogram for NUTS3 cohort imputation.
- CSO (2018). Information Note for Data Users — Revision to the Irish NUTS2 and NUTS3 Regions.
- Odyssee-Mure Ireland country profile.

## 3. Verification status

### Verified
- 3 IE NUTS2 / 8 NUTS3 (NUTS 2016 revision active in EUBUCCO v0.2).
- TABULA source = IE direct (Energy Action Ltd).
- `tabula_reference_hdd = 2600` (Dublin DEAP convention).
- `climate_multiplier = 0.9846` (near-identity).

### Needs verify
- HDD 2018-2022 mean — pull exact Eurostat.
- `ie_intensities.csv` — research-synthesised; verify Energy Action brochure.
- Retrofit factors (0.55/0.25), DHW (15) — provisional.
- Retrofit shares (0.72/0.20/0.08) — modelling assumption from SEAI annual reports.
- EUBUCCO IE construction-year <15% coverage; substantial unknown-cohort fallback share expected. Supplement with SEAI BER public research download.
- Hotmaps total (26) — sum `building_stock_nuts3.csv` exactly.
- IE MFH_HIGH cohort gap: high-rise pre-1990 stock essentially absent (Ballymun towers demolished); current placeholder values flagged.

## Applied (2026-05-20): EUBUCCO area correction (Mechanism A) — `eubucco.area_correction = 0.78`

The first G5 Colab build landed IE at 44.9 TWh vs Hotmaps 34.83 = **+29 % (INVESTIGATE)**. Applied an area correction; IE now lands at **35.1 TWh = +0.6 % (OK)**.

**Mechanism — imputed floors + OSM sourcing (data quality).** Ireland has no open national building register, so EUBUCCO IE footprints are **OSM-derived** with only ~13 % observed heights (Milojević-Dupont 2023, Table 1) — floor counts are largely imputed. EUBUCCO IE residential area = **301 Mm²** vs CSO Census 2022 (2.112 M habitable dwellings × ~112 m²) = **237 Mm²** → factor 237/301 = **0.78** (the mildest of the Mechanism-A corrections). This is the **Mechanism A** family documented in [eubucco_census_area_audit.md](../eubucco_census_area_audit.md). Census-grounded, not Hotmaps-tuned. The IE TABULA intensity vintage (Energy Action 2012, pre-SEAI-Retrofit-Plan) is a possible secondary contributor, deferred.
