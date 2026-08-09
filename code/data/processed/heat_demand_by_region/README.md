# Heat demand by NUTS region

Auto-generated from `code/data/processed/building_stock_nuts3.csv` (which sums Hotmaps 2015 regional heat demand baseline by NUTS3 region and building type).

## Files

### Cross-country (all 29 countries in one file)

| File | Regions | Description |
|---|---|---|
| `heat_demand_NUTS1_all.csv` | 100 | Macro-region aggregation (e.g. Bayern, Île-de-France, North West England) |
| `heat_demand_NUTS2_all.csv` | 284 | Province/Land/Comunidad level (e.g. Oberbayern, Lombardia) |
| `heat_demand_NUTS3_all.csv` | 1,369 | Finest resolution used by the model (e.g. München, Milano, Manchester) |

### Per-country (all 3 levels combined)

| File pattern | Description |
|---|---|
| `{ISO2}.csv` | One file per country (29 total). Combines NUTS1+NUTS2+NUTS3 for that country. ISO2 codes: AT, BE, BG, CH, CY, CZ, DE, DK, EE, ES, FI, FR, GR, HR, HU, IE, IT, LT, LU, LV, MT, NL, PL, PT, RO, SE, SI, SK, UK. |

Per-country files are also duplicated as `countries/{Country-Name}/data/heat_demand_regions.csv` for convenient navigation from the country profile.

## Columns

| Column | Type | Description |
|---|---|---|
| `nuts_id` | str | NUTS 2021 code (e.g. `DE21H` for München Landkreis). |
| `nuts_name` | str | Region name. Some 2024-revised French regions filled manually. |
| `nuts_level` | int | 1 (macro), 2 (province), or 3 (finest). |
| `country` | str | ISO2 country code. Note: Greece uses `EL` in NUTS codes but `GR` here for model consistency. |
| `dwellings` | float | Sum of dwellings across SFH + MFH_HIGH + OTHER from `building_stock_nuts3.csv`. **Over-counts due to OTHER bucket — see caveat.** |
| `heat_MWh` | float | Heat demand in MWh (Hotmaps 2015 baseline). |
| `heat_TWh` | float | Same value in TWh for readability. |

## Totals (sanity check)

Total across all 29 countries: **3,863 TWh/year** (Hotmaps 2015 residential heat demand). This figure is consistent across all three NUTS levels (NUTS1 sum = NUTS2 sum = NUTS3 sum).

## Caveats

1. **Dwelling counts inflated.** The `dwellings` field includes the OTHER building-type bucket from `building_stock_nuts3.csv`, which over-counts. For accurate residential dwelling counts, see national statistical offices or the EUBUCCO integration (Step 6 in `PLAN.md`).
2. **Heat demand is the reliable variable.** TWh values come directly from Hotmaps regional baseline (2015) and are the basis for all LCOH and Monte Carlo modelling.
3. **Hotmaps baseline is 2015.** Demand has changed since (efficiency improvements, mild winters, COVID); use as relative shares rather than absolute current demand for years past 2015.
4. **NUTS revisions.** The model uses NUTS 2021. Some French regions were renamed in NUTS 2024 — manual name fixes applied where the GISCO 2021 file returned blank.
5. **Extra-regio regions.** "Extra-Regio NUTS 1" entries (codes ending in `Z`, e.g. `BEZ`, `FRZ`) with zero demand were stripped during cleanup.

## How to regenerate

```bash
python3 code/scripts/aggregate_heat_demand_by_region.py    # to be added
# Or inline (one-off):
python3 -c "
import pandas as pd
bs = pd.read_csv('code/data/processed/building_stock_nuts3.csv')
gisco = pd.read_csv('code/data/raw/gisco/NUTS_RG_01M_2021_4326_clean.csv')
# ... see git log for full script
"
```

## Source

`code/data/processed/building_stock_nuts3.csv` — built by `code/src/BuildingStock.py` from:
- Hotmaps regional residential heat demand 2015 baseline (Hotmaps Project, `Hotmaps_regional_demand.csv`).
- Eurostat CENS_21DWBNO_R3 — dwellings by type by NUTS3 (2021 Census).
- GISCO NUTS_RG_01M_2021_4326 — NUTS region definitions and shapes.
- UK ONS TS044 — accommodation type by lower-tier local authority (2021 Census).

Region names from: `code/data/raw/gisco/NUTS_RG_01M_2021_4326_clean.csv`, with manual name overrides for NUTS 2024-revised codes.
