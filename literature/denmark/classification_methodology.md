# Denmark — building classification and heat-intensity methodology

**Status:** draft, awaiting Abdul review and the Colab build run.
**Last updated:** 2026-05-20.
**Authors:** Ali Alajwad with Claude.
**Implemented in:** `code/scripts/country_build/02_classify.py`, `03_heat_intensity.py`, `04_diagnostics.py` (all with `--country DK`).
**Config:** `code/data/country_config/dk.yaml`.

Denmark is a **direct-TABULA** country in build group 6 (SE + DK, BG, RO; Nordic + South-East Europe).

## 1. Headline facts

- **TABULA source:** SBi (Statens Byggeforskningsinstitut, now Aalborg University BUILD). Wittchen K.B., Kragh J. (2012). SBi 2012:01 — "Danish building typologies — Participation in the TABULA project". 27 building types, 9 age bands, Real-Example + Synthetic-Average models.
- **HDD:** DK 2018–2022 mean = **2769** (Eurostat). `tabula_reference_hdd = 2900` (DRY 2010 København), `climate_multiplier = 2769/2900 = 0.955`. Near-identity, no Option B trigger.
- **NUTS:** 5 NUTS2 / 11 NUTS3. Stable since 2007.
- **Retrofit:** Bygningsfornyelse (municipal), Boligjobordningen (green craftsman tax deduction, re-introduced 2025), Bygningspuljen / Klimatilskud (HP + envelope subsidy, Energistyrelsen). BR18 / BR23 new-build standards. Energistyrelsen + Bolius: ~25-30% of pre-1980 SFH have had at least one major envelope measure. Deep-renovation rate ~1%/yr.
- **Retrofit factors:** standard 0.50 (DK TABULA halves SH), advanced 0.30 (BR18-equivalent ~30-50 kWh/m²/yr).
- **DHW:** stock-uniform ~15 kWh/m²/yr (DK TABULA convention; occupancy-driven not envelope-driven).
- **Hotmaps 2015 benchmark:** ~56 TWh (DK residential SH+DHW useful). Energistatistik 2022 households ≈ 53 TWh useful — close cross-check.
- **DH penetration:** DK residential ~63% district heating, ~15-16% gas, ~12-13% HP, ~5% oil legacy, ~4-5% biomass. The TABULA-derived bottom-up reports useful heat demand at meter; downstream DH-vs-other delivery allocation is separate.
- **Comfort regime:** No deflator (Nordic, indoor 20 °C setpoints match TABULA, TABULA reference HDD within 5% of operational mean).

## 2. Sources

- DK TABULA Scientific Report (SBi): episcope.eu/fileadmin/tabula/public/docs/scientific/DK_TABULA_ScientificReport_SBi.pdf
- DK TABULA country page: episcope.eu/building-typology/country/dk/
- Wittchen K.B., Kragh J. (2012). SBi 2012:01.
- BR18 / BR23 — Bygningsreglementet.
- Energistyrelsen — Bygningspuljen.
- DBDH (Danish Board of District Heating).
- DMI (2018). DRY 2010 climate reference update.
- Odyssee-Mure Denmark country profile.

## 3. Verification status

### Verified
- 5 DK NUTS2 / 11 NUTS3 (stable since 2007).
- TABULA source = DK direct (SBi 2012:01).
- `tabula_reference_hdd = 2900` (DRY 2010 København).
- `climate_multiplier = 0.9548` (2769/2900).

### Needs verify
- `dk_intensities.csv` — research-synthesised; verify SBi 2012:01 brochure numeric values.
- Retrofit factors (0.50/0.30), DHW (15/15) — provisional.
- Hotmaps total (56) — sum `building_stock_nuts3.csv` exactly.
