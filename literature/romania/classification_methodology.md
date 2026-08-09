# Romania — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country RO`).
**Config:** `code/data/country_config/ro.yaml`.

Romania is a **proxy-TABULA** country in build group 6 (SE + DK, BG, RO; Nordic + South-East Europe).

## 1. Headline facts

- **TABULA source:** **Czechia (CZ proxy)**. RO is not a TABULA-12 country (URBAN-INCERC publishes Romanian residential typology research but not a TABULA-format archetype database). Romanian *blocuri* (Soviet-era industrialised MFH) share Comecon construction lineage with Czech *paneláks*; thermal envelope U-values, slab geometries and DHW riser configurations are highly comparable. CZ HDD (~3260) is the closer continental analogue than PL (too cold, ~3160) or HU (HU itself is DE-proxy, chaining adds noise).
- **Pannonian overlay (deferred):** RO11 (Nord-Vest, Cluj/Oradea) + RO42 (Vest, Timișoara/Arad) sit in Habsburg-influenced lowlands where HU brick MFH typology may fit better. A future `region_split_proxy` schema (same extension HR needs) would carry an HU overlay weight ~0.20 for these two NUTS2.
- **HDD:** RO 2018–2022 mean = **2805** (Eurostat). `tabula_reference_hdd = 3400` (CZ CSN 73 0540 reference). `climate_multiplier = 2805/3400 = 0.8250`.
- **NUTS:** 8 NUTS2 (RO11–RO42) / 42 NUTS3 (41 județe + Municipiul București). Stable.
- **Retrofit:** PNRT (Programul Național de Reabilitare Termică, since 2002; OUG 18/2009 expansion): ~3,500-4,500 apartment blocks by 2020. PNRR Component C5: €1.39B for 2021-2026, target 4.3 Mm² residential. Renovation rate ~0.3%/yr (Renovate Europe, among EU's lowest deep-renovation rates). Cumulative ~18-22% retrofit penetration by 2024, mostly partial.
- **Retrofit shares:** 0.80/0.15/0.05.
- **Retrofit factors:** standard 0.60, advanced 0.32 (CZ TABULA via proxy).
- **DHW:** SFH 12, MFH 15 kWh/m²/yr (CZ proxy; RO household sizes slightly larger but climate-insensitive).
- **Hotmaps 2015 benchmark:** ~82 TWh (Hotmaps + STRATEGO WP2 RO; residential SH+DHW useful 78-85 TWh).
- **Fuel mix (2022):** biomass 46-50% (rural; 80% of rural HH wood-heated), gas 22-25% (urban Bucharest/Cluj/Timișoara), DH 12-14% (collapsing from 30% in 2000), electricity 10-13%, residual oil/LPG/coal ~3-5%.
- **Comfort regime:** **APPLIED 2026-05-20 — `comfort_regime.deflator = 0.60`.** The first G6 Colab run landed RO at +89.2 % over Hotmaps (BU 155.1 vs Hotmaps 82.0), confirming the CZ-proxy TABULA values applied without an operational-regime correction substantially over-state realised Romanian heating demand. Coefficient derivation: 0.25 urban-MFH (DH/gas) × 0.90 + 0.50 rural-SFH wood-heated × 0.45 + 0.20 post-2010 stock × 1.00 = 0.65; central estimate **0.60** after weighting toward unrenovated MFH energy share. Cites EU-SILC 2022 (24–26 % under-heating, EU's 2nd-highest), World Bank Romania Energy Poverty Assessment 2024 (rural wood stoves ~15 % delivered efficiency; 21.1 % HH below energy-poverty line), INCERC/UTCB Cherecheș/Pătrașcu 25–40 % prebound, OECD WP 1812 (2024). Expected post-rebuild: ~95 TWh vs Hotmaps 82 (~+16 %, ACC band).

## 2. Sources

- TABULA building typologies overview (Loga et al. 2016) *Energy & Buildings* 132:4-12.
- CZ TABULA Scientific Report (proxy source): episcope.eu/fileadmin/tabula/public/docs/scientific/CZ_TABULA_ScientificReport_STU-K.pdf
- STRATEGO WP2 Romania country report (Heat Roadmap Europe).
- Hotmaps D2.3 EU28 open dataset.
- Type Projects as Tools: Housing Type Design in Communist Romania (RO archetypes).
- Romania PNRR Component C5 (energy renovation).
- Casa Verde Plus heat-pump programme (AFM).
- World Bank Romania Energy Poverty Assessment 2024.
- OECD Decarbonising Romania's Economy WP 1812 (2024).
- Renovate Europe — Romania factsheet (0.3%/yr rate).
- INCERC / UTCB Bucharest measured-vs-calculated research (Cherecheș, Pătrașcu).
- Odyssee-Mure Romania profile.

## 3. Verification status

### Verified
- 8 RO NUTS2 / 42 NUTS3 (stable).
- TABULA source = CZ proxy.
- `tabula_reference_hdd = 3400` (CZ CSN 73 0540 reference).
- `climate_multiplier = 0.8250` (2805/3400).

### Needs verify
- HDD 2018-2022 mean ~2805 — pull exact Eurostat.
- HU overlay for Pannonian RO11+RO42 — deferred to NUTS3 `region_split_proxy` schema extension (also needed for HR).
- Retrofit shares (0.80/0.15/0.05) — modelling assumption from PNRT + PNRR.
- Comfort regime deflator — **applied 2026-05-20** (0.60, stock-weighted; see section 1); follow-up: per-NUTS3 differentiation of the rural-SFH-wood vs urban-MFH stock weights once `region_split_proxy` schema lands (also benefits HR).
- Hotmaps total (82) — sum `building_stock_nuts3.csv` exactly.
- Ilfov (RO322) vs București (RO321) — verify EUBUCCO doesn't double-count Bucharest suburban communes assigned to Ilfov county shapes.
