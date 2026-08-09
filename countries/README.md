# Country Profiles

Per-country profiles for all 29 countries in the EU Hydrogen Buildings model. Each folder contains a structured `README.md` (Style B), `sources.md` with citations, and `data/profile.yaml` (machine-readable).

## Coverage — 29 countries

### Tier 1 — Deep profiles (high RQ relevance, 7 countries)
| Country | RQ relevance | Key feature |
|---|---|---|
| [Germany (DE)](Germany/) | RQ1 | Largest EU heating market; GEG 2024 backlash; OIES paper ET29 exists |
| [France (FR)](France/) | RQ1 | Cleanest large-country grid (nuclear); MaPrimeRénov'; early gas ban |
| [Italy (IT)](Italy/) | RQ1 | Superbonus → Ecobonus transition; high gas dependency |
| [Netherlands (NL)](Netherlands/) | RQ1 | Highest gas dependency in EU; 2026 mandate dropped |
| [Poland (PL)](Poland/) | RQ1 | Coal-dominated grid; Czyste Powietrze programme |
| [Sweden (SE)](Sweden/) | RQ1 | District heating leader (50%); near-zero residential gas |
| [Switzerland (CH)](Switzerland/) | **RQ2 anchor** | MuKEn cantonal mandates; clean grid; no national ban |

### Tier 2 — Standard profiles (22 countries)

**Northern/Western Europe:**
- [Austria (AT)](Austria/) — EWG Renewable Heat Act 2024
- [Belgium (BE)](Belgium/) — Three-region federal structure (Flanders/Wallonia/Brussels)
- [Denmark (DK)](Denmark/) — DH leader, 65% of households; cross-party consensus
- [Finland (FI)](Finland/) — 524 HPs/1000 households; coldest climate
- [Ireland (IE)](Ireland/) — 42% oil dependency; SEAI Better Energy scheme
- [Luxembourg (LU)](Luxembourg/) — Most generous HP subsidy (€17,500); small market
- [United Kingdom (UK)](United-Kingdom/) — **Total gas boiler ban scrapped Jan 2025**

**Southern Europe:**
- [Cyprus (CY)](Cyprus/) — 60% oil heating; Mediterranean climate (642 heating hours)
- [Greece (GR)](Greece/) — 41% oil; lignite DH transitioning
- [Malta (MT)](Malta/) — 75% electricity heating; mildest climate
- [Portugal (PT)](Portugal/) — 88% renewables (biomass); growing HP sales
- [Spain (ES)](Spain/) — PNIEC 35% electrification target; AFEC grants

**Central/Eastern Europe:**
- [Bulgaria (BG)](Bulgaria/) — Sofia DH; high energy poverty
- [Croatia (HR)](Croatia/) — Subsidised gas €46/MWh; biomass culture
- [Czech Republic (CZ)](Czech-Republic/) — Coal grid; Prague DH; HP sales -64% in 2024
- [Hungary (HU)](Hungary/) — **Subsidised gas €31/MWh**; Russian energy dependence
- [Romania (RO)](Romania/) — 5.5M wood+gas homes; Bucharest DH issues
- [Slovakia (SK)](Slovakia/) — DH dominant in cities; geothermal potential
- [Slovenia (SI)](Slovenia/) — Eko Sklad grants; Šoštanj coal phase-out

**Baltics:**
- [Estonia (EE)](Estonia/) — Oil shale legacy; Estonia-Latvia DH cross-border link (Oct 2025)
- [Latvia (LV)](Latvia/) — Major wood pellet exporter; biomass DH
- [Lithuania (LT)](Lithuania/) — 57% DH; Klaipėda LNG; €14,500 HP grants

---

## Format (Style B)

Each profile has 11 structured sections:
- **Snapshot** — key metrics table
- **Policy** — boiler bans, ETS2, national laws (model data + context)
- **Economics** — LCOH for each tech across 2025/2030/2050
- **Building stock** — dwellings, types, heat demand (from Hotmaps + Eurostat Census 2021)
- **Current heating mix** — what % gas/HP/biomass/DH today (web-researched)
- **Grid CO₂ trajectory** — 2025 → 2050 (EMBER + EEA)
- **District heating context** — share, networks, fuel mix
- **Key actors** — utilities, regulators, HP manufacturers
- **National programmes** — subsidies, mandates, schemes
- **Risk flags** — political/infrastructural/social risks
- **Model results** — REF scenario MC median tech shares

Plus `sources.md` with citation pointers, and `data/profile.yaml` (machine-readable LCOH/policy/MC data extracted from the model).

---

## Data provenance

- **Model parameters** (LCOH, MC results, grid CO₂, fuel prices, building stock): extracted from `code/src/` and `code/results/` of this repo
- **Current heating mix, programmes, market data**: web-researched May 2026, with sources noted per country
- **Building stock counts**: Eurostat Census 2021 (CENS_21DWBNO_R3), Hotmaps heat demand baseline; UK from ONS Census 2021 (TS044)

> **Known limitations to discuss with Abdul:**
> 1. The model's building stock file aggregates by NUTS3 with three categories (SFH / MFH_HIGH / OTHER). The "OTHER" bucket over-counts dwellings.
> 2. HP/DH feasibility scores (SFH HP=0.9, MFH HP=0.5, SFH DH=0.3, MFH DH=0.8) are expert judgement — flagged for validation.
> 3. Some Tier 2 countries (small absolute heat demand) are not in the top-15 reported in `mc_country_{SCENARIO}.csv`. For those, see `code/results/mc_summary_{SCENARIO}.csv` for EU aggregate.
> 4. **Several policy timetables changed since model parameters last refreshed** — notable cases flagged in country READMEs:
>    - NL hybrid HP mandate cancelled (2024)
>    - UK 2035 gas boiler ban scrapped (Jan 2025)
>    - Wallonia oil-boiler ban postponed (2024)
>    - Hungary subsidised gas price €31/MWh — anomaly
>    - Czech Republic HP sales -64% in 2024

---

## Country folder structure

```
{ISO2}/
├── README.md         ← Structured Style B profile
├── sources.md        ← Citations and references
└── data/
    └── profile.yaml  ← Machine-readable model data
```
