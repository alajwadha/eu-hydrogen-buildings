# Netherlands — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country NL`).
**Config:** `code/data/country_config/nl.yaml`.

Netherlands is a **direct-TABULA** country in build group 5 (AT + BE, NL, IE; Northwestern temperate Europe).

## 1. Headline facts

- **TABULA source:** TNO / Agentschap NL (now RVO). Voorbeeldwoningen 2011 (30 reference dwellings) + Voorbeeldwoningen 2022 update (51 reference dwellings, stock to 2018). NTA 8800 = current Dutch EPC method.
- **HDD:** NL 2018–2022 mean = **2475** (Eurostat estimate, low end of expected range). **Option B applied:** `tabula_reference_hdd = 2900` (KNMI De Bilt 1971-2000 normal), `climate_multiplier = 2475/2900 = 0.853`.
- **NUTS:** 12 NUTS2 (NL11–NL42), ~40 NUTS3 (COROP regions). Stable across NUTS 2013/2016/2021.
- **CONSTRUCTION-YEAR coverage in EUBUCCO NL: 100%** (BAG `bouwjaar` is a primary attribute on every verblijfsobject). EUBUCCO v0.1 paper Table 1 (Milojevic-Dupont et al. 2023) confirms. The OPPOSITE problem applies: NL has NO `type` field in BAG (`gebruiksdoel` not ingested) — residential filter may need post-hoc re-join.
- **Retrofit:** NL is the most-retrofitted EU residential stock. CBS Feb 2026: ~40% of dwellings with energy label carry A+. Roof insulation 86%, glass 85%, façade 73%, floor 63%. Programmes: Nationaal Isolatieprogramma (post-Klimaatakkoord 2019), ISDE (HP + insulation subsidy), aardgasvrije wijken pilots. Shares 0.55/0.35/0.10 reflect aggressive penetration.
- **Retrofit factors:** standard 0.65, advanced 0.30 (NL TABULA "usual" ~35% reduction, "advanced" ~70% reduction; provisional).
- **DHW:** SFH 17, MFH 20 kWh/m²/yr (Voorbeeldwoningen 2022).
- **Hotmaps 2015 benchmark:** ~115 TWh (~95 TWh SH + ~20 TWh DHW).
- **Comfort regime:** No deflator. Majcen/Itard/Visscher (TU Delft 2013) documented NL prebound (measured ~20-30% below TABULA in old poorly-insulated dwellings) and rebound (+10-20% in well-insulated) — these net out at stock level. Per-cohort prebound is a candidate follow-up refinement but not a flat deflator.

## 2. Sources

- NL TABULA country page: episcope.eu/building-typology/country/nl/
- Voorbeeldwoningen 2022 (RVO): rvo.nl/sites/default/files/2023-01/brochure-voorbeeldwoningen-bestaande-bouw-2022.pdf
- Agentschap NL (2011). Voorbeeldwoningen 2011 — bestaande bouw.
- Milojevic-Dupont N. et al. (2023). EUBUCCO v0.1. *Scientific Data* 10:147.
- CBS (Feb 2026). "Vier op de tien Nederlandse huizen hebben nu top energielabels".
- Klimaatakkoord (2019); ISDE (RVO); Nationaal Isolatieprogramma.
- Majcen D., Itard L., Visscher H. (2013). Actual vs theoretical gas consumption in Dutch dwellings. TU Delft / *Building & Environment*.
- KNMI climate normals via CBS 80370eng.

## 3. Verification status

### Verified
- 12 NL NUTS2 / ~40 NUTS3 (stable across NUTS vintages).
- TABULA source = NL direct (Voorbeeldwoningen 2011/2022).
- `tabula_reference_hdd = 2900` (KNMI De Bilt 1971-2000).
- `climate_multiplier = 0.8534` (2475/2900) — Option B applied.
- EUBUCCO construction-year coverage: 100% (BAG bouwjaar).

### Needs verify
- HDD 2018-2022 mean — pull exact Eurostat.
- `nl_intensities.csv` — research-synthesised; verify Voorbeeldwoningen.
- Retrofit factors (0.65/0.30), DHW (17/20) — provisional.
- Retrofit shares (0.55/0.35/0.10) — aggressive per CBS; verify against CBS Statline 82900NED.
- Hotmaps total (115) — sum `building_stock_nuts3.csv` exactly.
- EUBUCCO `type` field missing (BAG `gebruiksdoel` not ingested); residential filter may need post-hoc re-join against raw BAG.
