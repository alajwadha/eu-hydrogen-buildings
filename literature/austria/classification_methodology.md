# Austria — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country AT`).
**Config:** `code/data/country_config/at.yaml`.

Austria is a **direct-TABULA** country in build group 5 (AT + BE, NL, IE; Northwestern temperate Europe).

## 1. Headline facts

- **TABULA source:** AEA (Austrian Energy Agency). National brochure + scientific report; underlying ZEUS EPC database (~40,000 certificates). The brochure does NOT publish an explicit single-station reference HDD — it is built on a national-mean calibration, so `tabula_reference_hdd = hdd_country = 3050` and `climate_multiplier = 1.0`. No Option B correction.
- **HDD:** AT 2018–2022 mean = **3050** (Eurostat `nrg_chdd_a`, JRC AGRI4CAST). NEEDS_VERIFY exact.
- **NUTS:** 9 NUTS2 (AT11–AT34), 35 NUTS3. Stable across NUTS 2013/2016/2021.
- **Retrofit:** Sanierungsoffensive (federal, ~360M EUR/yr 2026–2030), Sanierungsbonus, Raus-aus-Oel-Bonus (52,652 applications by Dec 2024), Wohnbauforderung. IIBW + Umweltbundesamt: ~1.5%/yr renovation rate. Shares 0.65/0.27/0.08 reflect Austria's higher renovated share than DE/CZ.
- **Retrofit factors:** standard 0.65, advanced 0.40 (AT TABULA typology-averaged; provisional).
- **DHW:** SFH 10, MFH 15 kWh/m²/yr (AT TABULA / OIB Richtlinie 6 convention).
- **Hotmaps 2015 benchmark:** ~72 TWh (estimate from D2.3 + HRE4; needs exact sum from `building_stock_nuts3.csv`).
- **Comfort regime:** No deflator (cold-temperate Alpine; TABULA reference matches operation; AEA ZEUS calibration is itself anchored to measured EPC data).

## 2. Pipeline

Identical to the cross-country pipeline: EUBUCCO v0.2 partitions × per-building classification × TABULA-derived intensity × climate multiplier × retrofit blend × (no comfort_regime deflator). 4-class taxonomy (SFH / MFH_LOW / MFH_HIGH / NON_RESIDENTIAL); 6 cohorts (pre-1945 / 1946-1970 / 1971-1990 / 1991-2010 / 2011-2020 / post-2020).

## 3. Sources

- AT TABULA Scientific Report (AEA): episcope.eu/fileadmin/tabula/public/docs/scientific/AT_TABULA_ScientificReport_AEA.pdf
- AT TABULA Brochure (AEA, 2014 update): episcope.eu/fileadmin/tabula/public/docs/brochure/AT_TABULA_TypologyBrochure_AEA.pdf
- Lechner R., Tappeiner G., Lang G. (2011). IEE TABULA — Austria Scientific Report.
- OIB Richtlinie 6 (2023). Energieeinsparung und Waermeschutz.
- Statistik Austria — Mikrozensus Wohnen 2021 / Gebäude- und Wohnungszählung 2011.
- IIBW + Umweltbundesamt renovation monitoring.

## 4. Verification status

### Verified
- 9 AT NUTS2 / 35 NUTS3 (stable).
- TABULA source = AT direct (AEA).
- `tabula_reference_hdd = 3050` (AEA ZEUS national-mean calibration).

### Needs verify
- HDD 2018-2022 mean — pull exact from Eurostat `nrg_chdd_a`.
- `at_intensities.csv` — research-synthesised, ±20–30 % uncertainty; verify against AEA brochure numeric appendix.
- Retrofit factors (0.65/0.40), DHW (10/15) — provisional.
- Retrofit shares (0.65/0.27/0.08) — modelling assumption from IIBW + UBA.
- Hotmaps total (72) — sum `building_stock_nuts3.csv` exactly across AT NUTS3.

## Applied (2026-05-20): EUBUCCO area correction (Mechanism A) — `eubucco.area_correction = 0.575`

The first G5 Colab build landed AT at 125.5 TWh vs Hotmaps 82.36 = **+52 % (INVESTIGATE)**. Applied an area correction; AT now lands at **72.1 TWh = −12.4 % (OK)**.

**Mechanism — imputed floors (data quality), NOT occupancy.** EUBUCCO's Austrian footprints are cadastre-sourced (BEV), but only **~7 % of building heights are observed** (Milojević-Dupont 2023, Table 1); the other ~93 % of floor counts are ML-imputed, which over-states floor area even on good footprints. EUBUCCO AT residential area = **820 Mm²** vs Statistik Austria GWZ 2021 (4.9 M dwellings × 96.2 m² Nutzfläche) = **471 Mm²** → factor 471/820 = **0.575**. This is the **Mechanism A** family (AT/DK/HR/HU/IE/LT) documented in [eubucco_census_area_audit.md](../eubucco_census_area_audit.md) — distinct from the occupancy (Mechanism B) corrections for ES/EE/CY. The value is census-grounded, not Hotmaps-tuned.
