# Bulgaria — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country BG`).
**Config:** `code/data/country_config/bg.yaml`.

Bulgaria is a **proxy-TABULA** country in build group 6 (SE + DK, BG, RO; Nordic + South-East Europe). BG has a thin SOFENA TABULA brochure (2013, Bulgarian-only) but lacks the full per-cohort matrix integration — CZ is used as the structural proxy.

## 1. Headline facts

- **TABULA source:** **Czechia (CZ proxy)**. Bulgaria's *panelki* (industrialised concrete-panel MFH, ~60% of population) share Comecon construction lineage with Czech *paneláks*. Continental winter regime (CZ HDD ~3260) is closer to BG (~2600) than EL (~1600) or PL (~3160 but heavier panel-block bias). PL is the backup proxy.
- **HDD:** BG 2018–2022 mean = **2600** (Eurostat estimate). `tabula_reference_hdd = 3400` (CZ CSN 73 0540 Praha-Ruzyne, same as `cz.yaml`). `climate_multiplier = 2600/3400 = 0.7647`. Note: BG is scaled to the CZ TABULA REFERENCE HDD (3400), not the CZ actual HDD (3260) — methodology consistent with the Option B framework.
- **NUTS:** 6 NUTS2 (BG31–BG42) / 28 NUTS3 (oblasti, 1:1 with administrative provinces). Stable.
- **Retrofit:** National Programme for EE in Multifamily Residential Buildings (NPEEMRB, since 2015, 100% grant): ~1,923 buildings renovated by Jan 2021. NRRP (Recovery & Resilience Facility) "Sustainable energy renovation" pillar: €627M for residential MFH, target ~5 Mm² by 2026. Pre-2015 deep-renovation rate ~0.1%/yr (BPIE 2016). Cumulative renovated share ~3-4% of dwellings as of 2023; mostly partial (facade + windows).
- **Retrofit shares:** 0.85/0.12/0.03 reflect LTRS 2020 ("91% of dwellings in classes E/F/G") + NPEEMRB + NRRP.
- **Retrofit factors:** standard 0.60, advanced 0.32 (CZ TABULA via proxy).
- **DHW:** SFH 12, MFH 15 kWh/m²/yr (CZ proxy values).
- **Hotmaps 2015 benchmark:** ~29 TWh (BG residential SH+DHW useful, consistent with NECP 2021-2030 household FEC ~2.4 Mtoe).
- **Fuel mix:** Electricity 41% (HP + resistance), biomass/wood 33-34% (rural fuel-of-choice, 63% in rural HH), DH 15% (Sofia + 11 other cities), coal 7%, gas 3% (very low penetration vs CZ/PL).
- **Comfort regime:** **APPLIED 2026-05-20 — `comfort_regime.deflator = 0.55`.** The first G6 Colab run landed BG at +106.6 % over Hotmaps (BU 59.9 vs Hotmaps 29.0), confirming the CZ-proxy TABULA values applied without an operational-regime correction substantially over-state realised Bulgarian heating demand. Coefficient derivation: 0.80 base operational coefficient × 0.70 under-heating prevalence adjustment (EU-SILC 2022: 20.7 % of BG HH cannot afford adequate warmth — EU's highest; ~25 % of pre-1990 stock operates at sub-reference T) = 0.56 ≈ 0.55. Cites Eurostat EU-SILC 2022, BPIE 2016 BG renovation report, BG LTRS 2020, EEA 2025 energy-poverty profile. Expected post-rebuild: ~35 TWh vs Hotmaps 29 (~+20 %, ACC band).

## 2. Sources

- BG TABULA country page (SOFENA): episcope.eu/building-typology/country/bg/
- BG LTRS 2020: energy.ec.europa.eu/system/files/2021-08/bg_ltrs_2020_en_version_0.pdf
- BG Integrated NECP 2021-2030.
- MRRB — National Programme for EE in Multifamily Residential Buildings.
- BPIE (2016). Accelerating the renovation of the Bulgarian building stock.
- Odyssee-Mure Bulgaria profile.
- EU-SILC 2022 (Eurostat) — energy poverty.
- Renovate2Recover — BG NRRP assessment.

## 3. Verification status

### Verified
- 6 BG NUTS2 / 28 NUTS3 (stable).
- TABULA source = CZ proxy (panelák ~ panelki MFH lineage match).
- `tabula_reference_hdd = 3400` (CZ CSN 73 0540 reference).
- `climate_multiplier = 0.7647` (2600/3400).

### Needs verify
- HDD 2018-2022 mean ~2600 — pull exact Eurostat.
- BG SOFENA TABULA brochure — verify for any usable per-cohort values that could supplement the CZ proxy.
- Retrofit shares (0.85/0.12/0.03) — modelling assumption from LTRS + BPIE.
- Comfort regime deflator — **applied 2026-05-20** (0.55, see section 1); follow-up: triangulate against a dedicated Bulgarian measured-vs-calculated study (BAS / BPIE numerical extraction) if one becomes available.
- Hotmaps total (29) — sum `building_stock_nuts3.csv` exactly.
- HU overlay for far-south Blagoevgrad/Burgas coastal stock — not implemented; the BG cluster is small enough that the single-CZ proxy is acceptable.
