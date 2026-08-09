# Italy — Sources

## From model
- `code/src/Policy.py`, `code/src/Economics.py`, `data/processed/building_stock_nuts3.csv`, `code/results/mc_country_STATED_POLICIES.csv`

## External

**Eurostat (H1 2025):** Gas nrg_pc_202; Electricity nrg_pc_204
**Eurostat (2023):** 53.5% residential space heating from gas in Italy
**Hotmaps:** Residential heat demand baseline
**EMBER 2024 / EEA Fit-for-55:** Grid CO₂

**ENEA (Italian National Agency for New Technologies, Energy and Sustainable Economic Development):**
- Conto Termico 3.0 Annual Report 2025: €320M disbursed, 58% to heat pumps
- Ecobonus / Bonus Ristrutturazioni programme details
- bonusfiscali.enea.it

**GSE (Gestore dei Servizi Energetici):**
- Conto Termico administration
- www.gse.it

**IEA Bioenergy Italy Country Report 2024:**
- Italy 90–100% fossil fuel import-reliant; bioenergy 15% net import dependent
- https://www.ieabioenergy.com/wp-content/uploads/2024/12/CountryReport2024_Italy_final.pdf

**Italian Budget Law 2025:**
- Ecobonus 50%/36% rates; exclusion of single fossil-fuel boilers 2025–2027

**Mordor Intelligence — Italy Heat Pump Market 2024:**
- Air-to-water 82% market share
- Sub-10 kW 61% of installations
- North-West 34% of national revenue
- https://www.mordorintelligence.com/industry-reports/italy-heat-pump-market

**Mordor Intelligence — Italy HVAC Market:**
- A/W heat pumps 68% of sales
- Daikin Altherma 3 H HT delivers 70°C — radiator compatibility key for retrofits
- 4.2M installed R-410A units need refrigerant transition

**ISTAT (Italian National Statistics):**
- ~25M residential dwellings
- Building age distribution

**Italia Domani (National Recovery and Resilience Plan):**
- Strengthening Ecobonus, Superbonus details
- https://www.italiadomani.gov.it

**ECOS / EHPA position papers:**
- Italy boiler ban policy direction

---

## Citations

```bibtex
@misc{Eurostat2023ITgas,
  author = {Eurostat},
  title = {Disaggregated final energy consumption in households},
  year = {2023}
}

@misc{ENEAContoTermico2025,
  author = {{ENEA}},
  title = {Conto Termico 3.0 Annual Report 2025},
  year = {2025}
}

@misc{MordorIntelligence2024ItalyHP,
  title = {Italy Heat Pump Market: Size, Share \& 2030 Growth Trends},
  publisher = {Mordor Intelligence},
  year = {2024}
}
```

---

## EUBUCCO bottom-up build sources (build group 2)

Sources for the bottom-up heat-demand build (`it.yaml`, methodology in
`literature/italy/classification_methodology.md`):

- **EUBUCCO v0.2** — Milojevic-Dupont N. et al. (2023), *Scientific Data* 10:147, DOI 10.1038/s41597-023-02040-2. https://eubucco.com/files/v0.2 (ODbL v1.0).
- **Italian TABULA typology (Politecnico di Torino)** — per-class × per-cohort space-heating energy need. https://episcope.eu/building-typology/country/it/ ; Ballarini I., Corgnati S.P., Corrado V. (2014), *Energy Policy* 68:273-284. See `code/data/raw/tabula/it_intensities.csv` (research-synthesised pending TABULA WebTool verification).
- **Eurostat `nrg_chdd_a`** — heating degree days (base 15 °C, JRC AGRI4CAST), 2018–2022 mean 1821.23. https://ec.europa.eu/eurostat/databrowser/view/nrg_chdd_a
- **ENEA Superbonus 110% reporting** — retrofit-state assumptions.
- **ISTAT census** — residential stock age structure.
