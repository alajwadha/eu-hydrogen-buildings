# France — Sources

## From model (this repo)
- `code/src/Policy.py`, `code/src/Economics.py`, `data/processed/building_stock_nuts3.csv`, `code/results/mc_country_STATED_POLICIES.csv`

## External sources

**Eurostat (H1 2025):** Gas nrg_pc_202; Electricity nrg_pc_204

**Hotmaps:** Residential heat demand baseline, NUTS3

**EMBER 2024 / EEA Fit-for-55:** Electricity grid CO₂

**RE2020 thermal regulation (2022):**
- Effective ban on gas in new single-family homes
- French Ministry of Ecological Transition

**ADEME (Agence de l'environnement et de la maîtrise de l'énergie):**
- Heating mix data (2015 baseline): 33% gas, 14% oil, 41% electricity, 3% wood, 6% DH
- Fonds Chaleur programme

**SDES (Service des données et études statistiques):**
- Distribution of energy sources for heating, 2021 (via Statista)

**SNCU (Syndicat National du Chauffage Urbain):**
- DH energy mix 2023: 66.5% renewable
- 31% gas / 28% energy recovery / 27% biomass / 6% geothermal / 8% other

**JRC Country Fiche on Heat Pumps — France (JRC137131_010):**
- Electricity-gas price ratio 2.22 (2023 S1)
- MaPrimeRénov' subsidy: up to €15,000 for ground-source HP
- HP replaces gas → 92% CO₂ reduction in single-family home
- https://publications.jrc.ec.europa.eu/repository/bitstream/JRC137131/JRC137131_010.pdf

**IEA Bioenergy France Country Report 2024:**
- French power generation: ~70% nuclear, 8–12% fossil, growing renewables
- https://www.ieabioenergy.com/wp-content/uploads/2024/12/CountryReport2024_France_final.pdf

**INSEE (French national statistics office):**
- Dwelling stock counts; ~37M dwellings nationally

**Planète Énergies:**
- 67% of home energy in France goes to heating; 10% to hot water; electric heating 31% of homes

**Other:**
- ScienceDirect article on Lyon DH (2018): 44% gas, 33% electricity, 14% oil, 6% DH, 3% wood

---

## Citations for paper

```bibtex
@techreport{JRC2024HPFrance,
  author = {{Joint Research Centre}},
  title = {Country fiche on heat pumps: France},
  number = {JRC137131-010},
  institution = {European Commission},
  year = {2024}
}

@misc{SNCU2024,
  author = {{Syndicat National du Chauffage Urbain}},
  title = {Energy mix of district heating networks in France 2023},
  year = {2024}
}

@misc{ADEME2015heating,
  author = {ADEME},
  title = {Residential heating mix in France},
  year = {2015}
}
```
