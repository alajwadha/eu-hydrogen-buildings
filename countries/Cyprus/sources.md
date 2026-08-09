# Cyprus — Sources

## From model
- `code/src/Policy.py`, `code/src/Economics.py`, `data/processed/building_stock_nuts3.csv`, `code/results/mc_country_STATED_POLICIES.csv`

## External

**Eurostat (H1 2025):** Gas nrg_pc_202; Electricity nrg_pc_204
**Eurostat 2023:** Disaggregated final energy consumption in households (heating mix shares)
**Hotmaps:** Residential heat demand baseline; HDD per country
**EMBER 2024:** Electricity grid carbon intensity actuals
**EEA Fit-for-55:** Grid CO₂ projections 2030–2050

**EHPA (European Heat Pump Association):**
- Market Report 2025 — country HP sales/stock data
- Boiler Ban Tracker Nov 2025 — phase-out timetables
- Subsidies for Residential Heat Pumps in Europe 2023
- https://www.ehpa.org/market-data/

**IEA Bioenergy Country Reports 2024:**
- Cyprus-specific bioenergy and heating data
- https://www.ieabioenergy.com/

**JRC Country Fiche on Heat Pumps (where applicable):**
- https://publications.jrc.ec.europa.eu

**National policy documents:**
- See README.md programmes section for specific national schemes and laws.

**OIES (Oxford Institute for Energy Studies):**
- ET08 (2022), ET32 (2024) — hydrogen import pricing

**Additional country-specific sources** — see relevant news/web citations in README context.

---

## Notes for paper bibliography

Citations to be added to main `paper/References_v1.bib` upon paper revision. Each programme/policy specifically cited in the README has a primary source web-search-validated as of May 2026.

---

## EUBUCCO bottom-up build sources (build group 3)

Sources for the bottom-up heat-demand build (`cy.yaml`, methodology in
`literature/cyprus/classification_methodology.md`):

- **EUBUCCO v0.2** — Milojevic-Dupont N. et al. (2023), *Scientific Data* 10:147, DOI 10.1038/s41597-023-02040-2. https://eubucco.com/files/v0.2 (ODbL v1.0).
- **Cyprus TABULA typology (Cyprus University of Technology — Panayiotou, Kalogirou, Florides)** — per-class × per-period space-heating energy need. https://episcope.eu/building-typology/country/cy/ ; CY_TABULA_TypologyBrochure_CUT.pdf. See `code/data/raw/tabula/cy_intensities.csv` (research-synthesised pending WebTool verification; shared with Malta which uses it as a climate-corrected proxy).
- **Eurostat `nrg_chdd_a`** — heating degree days (base 15 °C, JRC AGRI4CAST); 2018-2022 mean 661.56. https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a
- **EPISCOPE Cyprus refurbishment-state survey** — retrofit-state assumptions (54% no insulation).
