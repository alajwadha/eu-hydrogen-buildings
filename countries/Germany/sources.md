# Germany — Sources

## Data sources

### From model (this repo)
- `code/src/Policy.py` — boiler bans, carbon prices, grid CO₂ trajectory
- `code/src/Economics.py` — fuel prices, COP, LCOH parameters
- `data/processed/building_stock_nuts3.csv` — dwellings and heat demand by NUTS3 and building type
- `code/results/mc_country_STATED_POLICIES.csv` — MC scenario outputs

### External sources

**Eurostat (residential fuel prices, H1 2025):**
- Gas: nrg_pc_202 — https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_202/default/table
- Electricity: nrg_pc_204 — https://ec.europa.eu/eurostat/databrowser/view/nrg_pc_204/default/table

**Eurostat Census 2021:**
- CENS_21DWBNO_R3 — dwellings by NUTS3 and building type

**Hotmaps:**
- Residential heat demand baseline (~2015), per NUTS3 — https://www.hotmaps-project.eu

**EMBER 2024:**
- Electricity grid carbon intensity actuals — https://ember-energy.org

**EEA Fit-for-55:**
- Grid CO₂ projections 2030–2050

**OIES (Oxford Institute for Energy Studies):**
- ET29 (Feb 2024): *Decarbonising Germany's heating sector* — https://www.oxfordenergy.org/wpcms/wp-content/uploads/2024/02/ET29-Decarbonising-Germanys-heating-sector.pdf
- Key data points: 9.5M gas-heated buildings, 6M oil, 1.5M DH, 1M electric/HP

**EHPA Market Data 2025:**
- 2025 HP sales: 299,000 units in Germany (48% market share)
- https://ehpa.org/market-data/

**JRC Technology Data 2023:**
- CAPEX/FOM/VOM for heat pumps, gas boilers, hydrogen boilers (same parameters used across all model countries)

**IRENA Heat Pump Costs 2022; IEA Future of Heat Pumps 2022:**
- Learning rate assumptions for HP CAPEX decline 2025–2050

**Danish Energy Agency 2023:**
- Technology data catalogue for heating technologies

**JRC Country Fiche on Heat Pumps — Germany (JRC137131):**
- HP subsidy structure (up to 70%, EUR 21,000 cap)
- Residential electricity-gas price ratio
- https://publications.jrc.ec.europa.eu/repository/bitstream/JRC137131/JRC137131_011.pdf

**Agora Energiewende (Oct 2024):**
- *Analysis of the EU heating market* — German HP/gas boiler sales ratio 2.2:1 in 2023
- https://www.agora-energiewende.org/fileadmin/Projekte/2024/2024-10_EU_Clean_Heat/EU_heating_market_analysis.pdf

**Federal regulations:**
- GEG (Gebäudeenergiegesetz / Building Energy Act 2024)
- BAFA / KfW heat pump subsidy programme guidelines
- Wärmeplanung mandate (Wärmeplanungsgesetz 2024)

**DVGW (German gas industry association):**
- Study on hydrogen-compatibility of gas pipelines (95.9% H₂-compatible)
- Cited in OIES ET29

---

## Citations for the paper

```bibtex
@techreport{OIES2024Germany,
  author = {{Oxford Institute for Energy Studies}},
  title = {ET29: Decarbonising Germany's heating sector},
  year = {2024},
  month = {February},
  url = {https://www.oxfordenergy.org/wpcms/wp-content/uploads/2024/02/ET29-Decarbonising-Germanys-heating-sector.pdf}
}

@techreport{JRC2024HPGermany,
  author = {{Joint Research Centre}},
  title = {Country fiche on heat pumps: Germany},
  number = {JRC137131},
  institution = {European Commission},
  year = {2024}
}

@misc{EHPA2025Market,
  author = {{European Heat Pump Association}},
  title = {Market Data 2025},
  year = {2025},
  url = {https://ehpa.org/market-data/}
}
```

---

## EUBUCCO bottom-up build sources (build group 1)

Sources specific to the bottom-up heat-demand build (`de.yaml`,
`de_intensities.csv`, methodology in `literature/germany/`):

**EUBUCCO v0.2** — building footprints, height, type, age.
- Milojevic-Dupont N. et al. (2023). EUBUCCO v0.1. *Scientific Data* 10:147. DOI 10.1038/s41597-023-02040-2.
- Data: https://eubucco.com/files/v0.2 — ODbL v1.0.

**German TABULA typology (IWU Darmstadt)** — per-class × per-cohort space-heating energy need and refurbishment factors.
- Loga T., Diefenbach N., Stein B., Born R. (2015). *Deutsche Wohngebäudetypologie / TABULA Typology Brochure Germany*, 2nd ed. IWU, Darmstadt. https://episcope.eu/building-typology/country/de/
- Loga T., Stein B., Diefenbach N. (2016). TABULA building typologies in 20 European countries. *Energy & Buildings* 132:4-12. DOI 10.1016/j.enbuild.2016.06.094

**Eurostat `nrg_chdd_a`** — heating degree days (base 15 °C, JRC AGRI4CAST), 2018–2022 mean. https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a

**dena Gebäudereport 2024** — German residential stock age structure and ~1 %/yr renovation rate.

```bibtex
@techreport{EUBUCCO2023,
  author = {Milojevic-Dupont, Nikola and others},
  title = {EUBUCCO v0.1: a database of 200 million European buildings},
  journal = {Scientific Data},
  volume = {10}, pages = {147}, year = {2023},
  doi = {10.1038/s41597-023-02040-2}
}

@techreport{IWU2015TABULA_DE,
  author = {Loga, Tobias and Diefenbach, Nikolaus and Stein, Britta and Born, Rolf},
  title = {Deutsche Wohngeb\"audetypologie / TABULA Typology Brochure Germany},
  institution = {Institut Wohnen und Umwelt (IWU)},
  year = {2015}, address = {Darmstadt}
}
```
