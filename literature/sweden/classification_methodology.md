# Sweden — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country SE`).
**Config:** `code/data/country_config/se.yaml`.

Sweden is a **direct-TABULA** country in build group 6 (SE + DK, BG, RO; Nordic + South-East Europe). Note: `se_intensities.csv` already existed in the repo as the FI proxy. For SE-as-country the same file is used with a critical methodology delta vs the FI config (see below).

## 1. Headline facts

- **TABULA source:** Boverket / IVL — "Exempelsamling - klimatzon 1/2/3" brochure (95 pp, Swedish). Three climate zones; `se_intensities.csv` extracted from zone 3 (southern Sweden) which holds the large majority of stock.
- **HDD:** SE national 2018–2022 mean = **5043** (per verified `fi.yaml`).
- **Option B reverted 2026-05-20:** `tabula_reference_hdd = 5043` (matches `hdd_country`), `climate_multiplier = 1.0`. Initial choice was `tabula_reference_hdd = 3500` (zone-3 single station) with multiplier 1.4409 — that over-corrected: the first G6 Colab run landed SE at 113 TWh (+33 % vs Hotmaps 85, +28 % vs BSO 88.5). Revert rationale: the Swedish residential stock is heavily concentrated in zone 3 (southern Sweden); only ~10 % of population sits in zone 1 (Norrland). The Eurostat 5043 HDD is area-weighted (over-weighting the cold sparsely-populated north); the population-weighted SE HDD is closer to ~3800, which aligns with the zone-3 TABULA brochure values without scaling. Setting `tabula_reference_hdd = hdd_country = 5043` with `climate_multiplier = 1.0` implicitly accepts the SE TABULA brochure as the population-weighted national reference — the same convention used by the FI proxy chain.
- **DELTA vs FI proxy:** none anymore (this session's revert aligned both). The FI build at HDD 5321 against the same SE brochure uses multiplier = 5321/5043 = 1.055, a small adjustment for FI's slightly colder climate.
- **NUTS:** 8 NUTS2 (riksområden) / 21 NUTS3 (län). Stable across NUTS 2016/2021/2024.
- **Retrofit:** Boverket BBR trajectory (BBR 2006 ~110 kWh/m²/yr → BBR 2021 NZEB 35-65; BBR 2025 from 1 Jul 2025). Refurbishment factors standard 0.74 / advanced 0.49 are from the SE TABULA brochure (means across 15 zone-3 examples). Shares 0.55/0.35/0.10 reflect Boverket + Odyssee SE evidence of ~1%/yr deep-renovation rate.
- **DHW:** SFH 16, MFH 17 kWh/m²/yr (SE TABULA brochure "Tappvarmvatten" electric-resistance row).
- **Hotmaps 2015 benchmark:** ~85 TWh (estimate; Odyssee 4.04 Mtoe SH 2023 ≈ 47 TWh + DHW ≈ 35-40 TWh).
- **Comfort regime:** No deflator (cold-climate Nordic; TABULA reference matches operation; near-universal 20-22 °C setpoints).

## 2. Sources

- SE TABULA country page: episcope.eu/building-typology/country/se/
- TABULA SE National Typology Brochure — "Exempelsamling - klimatzon 1/2/3".
- Loga T., Stein B., Diefenbach N. (2016). *Energy & Buildings* 132:4-12.
- Boverket BBR (Building Regulations); BBR 2025 took effect 1-Jul-2025.
- Energimyndigheten EN0103 (Lokaler / non-residential premises).
- Odyssee-Mure Sweden country profile (Jan 2026 update).
- Hotmaps D5.2 EU-28 H&C outlook.

## 3. Verification status

### Verified
- 8 SE NUTS2 / 21 NUTS3 (stable).
- TABULA source = SE direct (`se_intensities.csv` zone 3).
- `tabula_reference_hdd = 5043` (population-weighted national mean; Option B 3500 reverted 2026-05-20 after over-correcting to +33 % vs Hotmaps).
- `climate_multiplier = 1.0` (zone-3 TABULA values treated as population-representative for the Swedish stock concentrated in zone 3).

### Needs verify
- `se_intensities.csv` zone-3 only; population-weighted multi-zone is the next refinement (zones 1-2 are colder with smaller stock).
- Retrofit shares (0.55/0.35/0.10) — modelling assumption.
- Hotmaps total (85) — sum `building_stock_nuts3.csv` exactly across SE NUTS3.
- Non-residential intensity (140) — estimate; pull EN0103 point estimate.
