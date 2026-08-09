# Power merit-order & electrification bridge, method and sources

*Companion to the 2026-06-15 reframe (Abdul): assess hydrogen's role in the electricity
sector on an **operating-cost / merit-order** basis, then bridge back to heating. Figures
P26-P29; scripts `power_merit_order.py`, `electrification_bridge.py`, `power_dispatch.py`.*

---

## 1. The reframe, why operating cost, not capex

Wholesale electricity is priced at the **short-run marginal cost (SRMC)** of the marginal
generator: fuel + variable O&M (+ a carbon cost on fossil plant). Capital cost is **sunk** and
does **not** set the spot price; it is recovered (if at all) through inframarginal rent and
capacity mechanisms. We therefore place hydrogen in the power **merit order** by SRMC and ask
where it sits relative to the carbon-priced gas peaker. Capital recovery ("missing money") is a
**separate investment question**, reported as a caveat (see `power_dispatch.py`,
`power_peaker_recovery_projection.csv`).

Standard references for marginal-cost pricing of electricity: Stoft, *Power System Economics*
(2002); Joskow, "Capacity payments in imperfect electricity markets" (*Utilities Policy*, 2008).

## 2. Short-run marginal cost by technology (EUR/MWh-e, 2050)

| Technology | SRMC | Basis | Source |
|---|--:|---|---|
| Solar PV | ~1 | variable O&M only | IRENA, *Renewable Power Generation Costs 2023*; NREL ATB 2024 |
| Onshore wind | ~1-2 | variable O&M only | IRENA 2023; NREL ATB 2024 |
| Offshore wind | ~2 | variable O&M only | IRENA 2023; NREL ATB 2024 |
| Hydro (run-of-river) | ~3 | O&M only | IEA, *Hydropower Special Market Report* (2021) |
| Nuclear | ~12 | fuel ~7 + O&M ~5 | IEA *WEO 2023*; World Nuclear Association cost data (2023) |
| Biomass | ~55 | feedstock / electrical efficiency (~35%) | IRENA 2023; IEA Bioenergy |
| **H₂ turbine** | **~221** | delivered H₂ / η + seasonal storage adder | this model (OIES H₂ price; Caglayan et al. 2020 storage); DEA *Technology Catalogue* 2023 (η) |
| **Gas peaker (OCGT)** | **~239** | gas wholesale / η + carbon × EF / η | this model; DEA *Technology Catalogue* 2023 |
| Coal | ~330 | coal / η + high carbon (residual; ≈0 GW by 2050) | this model |

Carbon, gas and hydrogen price paths are the scenario's own time-varying trajectories
(`src/Policy.py`, `src/Economics.py`): carbon (High path) 70 / 200 / 350 €/tCO₂ for 2025 /
2030 / 2050 (EU ETS design; BloombergNEF ETS2; PRIMES; Enerdata POLES); H₂ "Rapid" derived
bottom-up to 29 €/MWh by 2050 (electrolyser learning curve, floor validated vs Energy
Transitions Commission and Hydrogen Council ~€1-1.4/kg). The gas and H₂ SRMC in the figure are
read directly from the dispatch's per-country economics so figure and model never disagree.

**H₂-turbine efficiency (Hydrogen Push):** advanced simple-cycle, 40% (2025) rising to **48% (2050)**:
H-class simple-cycle ~43% + H₂ combustion bonus (+0.8 to +3.7 pp) + turbine-inlet-temperature
1600 → 1700 °C. Sources: ETN Global, *Hydrogen Gas Turbines* report (Oct 2024); ScienceDirect,
hydrogen-fired gas-turbine performance (2024). A combined-cycle unit reaches ~58-64% but needs
~€800-900/kW and is not a fast-start peaker, so we keep simple-cycle (CAPEX unchanged).

## 3. Capacity credit at the winter peak

For the "share of peak capacity hydrogen can take" we use the firm dispatchable (peaker) fleet
sized in `power_dispatch.py` to a ~3-hour loss-of-load standard. Firm-capacity (capacity-credit)
treatment of variable renewables at the cold-snap/Dunkelflaute peak follows the ENTSO-E
*European Resource Adequacy Assessment* (ERAA 2023) method and NREL capacity-value literature:
solar ≈ 0 at the winter evening peak, wind low in a Dunkelflaute, hydro/nuclear/biomass and
gas/H₂ firm.

## 4. The heating → electricity bridge (P28-P29)

- **Electrified-heat share** = (heat-pump + resistance) share of useful heat, per country, from
  the Monte Carlo tech mix (`mc_country_<scen>.csv`, q50). District heat is ~45% electric
  (large heat pumps) and shown as a separate stacked segment.
- **Heating electricity** = useful heat × (hp_air_share/COP_air + hp_ground_share/COP_ground +
  resistance_share). COPs from `src/Economics` (temperature- and country-specific).
- **Total power demand** = national baseline load (ENTSO-E Transparency, 2023) × growth (×1.40
  by 2050, consistent with TYNDP/ENTSO-E demand scenarios) + heating electricity.
- **Coverage:** the detailed bottom-up mix is modelled for the **15 largest countries = 91% of
  EU heat demand**; the small 14 lack full bottom-up inputs. The 29-country power merit order
  (P26/P27) uses price data that exist for all 29. Coverage is stated on every affected figure.

## 5. Headline results (2050, Hydrogen Push)

- Merit order: H₂ turbine **€221/MWh-e** sits just **below** the gas peaker **€239** (and far
  below coal €330), above the cheap low-carbon base (VRE ≈ 0, nuclear €12, biomass €55).
- Hydrogen undercuts the gas peaker on operating cost in **15 of 29 countries**.
- Hydrogen can therefore take up to **~29% of EU peak capacity** (~263 of 906 GW; ~77% of the
  firm peaker fleet) in those countries, but only **~1% of generated electricity** (~44 TWh of
  ~4,500), because the peaker runs ~130 h/yr. **A capacity role, not an energy role.**
- Heating is **~46% directly electric** (≈55% incl. electric district heat; Net Zero ~58%) and
  is **~9% of total power demand** in 2050, material enough that the grid's firm/peaking needs
  bear on the heating transition.
- **Caveat (capex):** the H₂ peaker still recovers only ~13% of its capital at these run-hours,
  so a deliberate build implies a standing capacity payment (`power_dispatch.py`).
