# Per-country power-capacity scenario to 2050 — provenance and method

`code/data/power_capacity.csv` (built by `code/scripts/build_power_capacity.py`) is the
installed-capacity stack the hourly dispatch model (`power_dispatch.py`) runs against:
29 countries x {2025, 2030, 2040, 2050} x 9 technologies (nuclear, hydro, onshore wind,
offshore wind, solar PV, firm gas, coal, biomass, battery power). It is a **curated,
fully-tagged capacity scenario**, not a single published dataset, because no clean
per-country 2050 BAU stack exists:

- ENTSO-E **TYNDP 2024** National Trends stops at 2040;
- the two TYNDP 2050 scenarios (Distributed Energy, Global Ambition) are both deep
  net-zero and overbuild VRE relative to current national plans;
- the **EU Reference Scenario 2020** (PRIMES) is per-country to 2050 but predates
  REPowerEU and the post-2022 acceleration.

## Method

- **2030** — each country's updated **NECP** target (well grounded; cited below).
- **2050** — the national **2050 strategy** where one exists; otherwise the 2030 NECP
  escalated on the TYNDP National-Trends growth trend.
- **2040** — linear interpolation of 2030 and 2050.
- **2025** — current actuals (ENTSO-E / Ember 2023-24) for the nine largest systems; for
  the rest, the 2030 value discounted ~15% for the VRE/battery technologies.
- Each country carries a `tag`: `anchored` (national strategy), `necp` (NECP-2030 +
  escalation), or `proxy` (small systems, structure-only).

## Anchored systems (national strategies)

| Country | Key 2050 anchors | Source |
|---|---|---|
| DE | Solar 400, onshore wind 160, offshore 70 GW (2045) | EEG 2023 targets; Agora/NEP 2045 |
| FR | Nuclear ~60, offshore 25, solar 90 GW | RTE *Futurs energetiques 2050* (N1/N2) |
| IT | Solar 150, wind 45+18 offshore GW | PNIEC 2024; MASE offshore 2050 >20 GW |
| ES | Solar 160, wind 90, nuclear 0 (out by 2035) | PNIEC 2023 update; nuclear phase-out calendar |
| PL | Solar 60, onshore 32, offshore 18, nuclear 9 GW; coal ~exit 2049 | PEP2040 / NECP |
| NL | Offshore 50, solar 80 GW | NL Klimaatakkoord / offshore roadmap 2050 |
| SE | Hydro 16, nuclear 8, onshore 38 GW | SE long-term energy scenarios (EM) |
| UK | Offshore 90, nuclear 12, solar 70 GW | NESO *Future Energy Scenarios 2025* (~270 GW total 2050) |
| CH | Hydro 17, solar 30, nuclear 0 GW | SFOE *Energy Perspectives 2050+* |

The other 17 EU members use NECP-2030 endpoints with a TYNDP-shaped escalation
(`necp`); LU, CY, MT are structure-only `proxy`.

## EU27 cross-check vs TYNDP 2024 (2050)

The builder asserts the EU27 aggregate against TYNDP anchors. Our scenario sits
**below** TYNDP's net-zero VRE totals and **above** on firm gas:

| Tech | This scenario | TYNDP 2050 | 
|---|---|---|
| Wind onshore | 559 | ~808 |
| Wind offshore | 259 | ~400 |
| Solar | 1230 | ~1700 |
| Battery (power) | 356 | ~956 |
| Firm gas | 174 | ~106 (+67 H2 turbines) |
| Nuclear | 113 | ~100 |

This gap is **deliberate and conservative for the hydrogen question.** Less VRE and less
storage mean *more* capacity-short hours and a *larger* peaking requirement — i.e. the
scenario is generous to the H2 peaker. The firm-gas figure is higher because in our model
the H2/gas turbine is the marginal investment we insert, so TYNDP's gas + H2-turbine fleet
(~173 GW) maps onto our "firm gas" line. If the peaker still fails to recover its capital
under a VRE build that is *thin* relative to TYNDP, the result is robust to a richer build.

## Caveats

- Capacity is an **input the reader can replace**; the contribution is the dispatch and
  the peaker economics, not third-decimal capacity precision.
- The stack is a single central trajectory; we do not vary it by the four policy scenarios
  (those vary carbon, H2 price, and grid carbon intensity instead). A storage- or VRE-rich
  sensitivity would shrink the peaking slice and is noted as an extension.
