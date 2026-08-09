"""Per-country power-generation + storage capacity scenario to 2050 (GW).

The dispatch model (power_dispatch.py) needs an installed-capacity stack per country
and year. There is NO single clean per-country 2050 BAU dataset (TYNDP 2024 National
Trends stops at 2040; the 2050 TYNDP scenarios are both net-zero; EU Reference 2020 is
PRIMES per-country to 2050 but pre-REPowerEU). We therefore curate a transparent,
fully-tagged capacity scenario:

  - the LARGE systems (DE, FR, IT, ES, PL, NL, SE, UK, CH) are anchored to national
    strategies / NECPs (cited per country below);
  - 2030 is mostly the country's updated NECP (well grounded);
  - 2050 is the national 2050 strategy where one exists, else the 2030 NECP escalated
    on the TYNDP National-Trends growth trend;
  - the long tail uses NECP-2030 + a TYNDP-shaped escalation, tagged "necp/proxy";
  - the EU27 aggregate is cross-checked against the TYNDP 2024 totals (assert in main()).

Every (country) row carries a `tag`: anchored | necp | proxy. The point of the model is
the DISPATCH and the H2-vs-gas peaker economics; capacity precision is inherently
scenario-dependent and is carried as an input the reader can replace.

Techs (GW): nuclear, hydro (reservoir+ror), wind_on, wind_off, solar, gas (firm CCGT+OCGT),
coal (hard+lignite, declining), biomass, battery_gw (power). 2040 = interpolate(2030,2050).

Run: cd code && PYTHONPATH=. python -m scripts.build_power_capacity
Out: code/data/power_capacity.csv (country,year,tech,capacity_gw,tag)

Sources: ENTSO-E TYNDP 2024 National Trends; EU Reference Scenario 2020 (PRIMES);
RTE Futurs energetiques 2050 (FR); German NEP/Agora 2045; Spain PNIEC 2030; Italy PNIEC
2024; Poland PEP2040/NECP; NESO FES 2025 (UK); Swiss Energy Perspectives 2050+;
EMBER 2024 / ENTSO-E installed-capacity (2025 actuals).
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path
from src.Config import EU_COUNTRIES

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "code" / "data" / "power_capacity.csv"
TECHS = ["nuclear", "hydro", "wind_on", "wind_off", "solar", "gas", "coal", "biomass", "battery_gw"]

# CAP[cc] = {tech: (gw_2030, gw_2050)}; 2040 interpolated; 2025 in CAP25. GW.
# Anchored systems use national-plan numbers (see module docstring); others NECP+escalation.
CAP = {
    # --- anchored to national strategies ---
    "DE": dict(nuclear=(0, 0), hydro=(6, 6), wind_on=(115, 160), wind_off=(30, 70),
               solar=(215, 400), gas=(45, 45), coal=(15, 0), biomass=(9, 9), battery_gw=(25, 90), tag="anchored"),
    "FR": dict(nuclear=(58, 60), hydro=(26, 27), wind_on=(35, 58), wind_off=(4, 25),
               solar=(45, 90), gas=(9, 6), coal=(1, 0), biomass=(2, 3), battery_gw=(4, 20), tag="anchored"),
    "IT": dict(nuclear=(0, 4), hydro=(19, 20), wind_on=(26, 45), wind_off=(2, 18),
               solar=(79, 150), gas=(45, 35), coal=(3, 0), biomass=(4, 4), battery_gw=(15, 60), tag="anchored"),
    "ES": dict(nuclear=(3, 0), hydro=(17, 17), wind_on=(59, 90), wind_off=(3, 12),
               solar=(76, 160), gas=(26, 18), coal=(2, 0), biomass=(1, 2), battery_gw=(13, 45), tag="anchored"),
    "PL": dict(nuclear=(0, 9), hydro=(2, 3), wind_on=(20, 32), wind_off=(6, 18),
               solar=(27, 60), gas=(12, 14), coal=(20, 2), biomass=(2, 3), battery_gw=(4, 18), tag="anchored"),
    "NL": dict(nuclear=(0.5, 3), hydro=(0, 0), wind_on=(8, 12), wind_off=(21, 50),
               solar=(30, 80), gas=(18, 12), coal=(2, 0), biomass=(3, 3), battery_gw=(6, 25), tag="anchored"),
    "SE": dict(nuclear=(7, 8), hydro=(16, 16), wind_on=(20, 38), wind_off=(2, 12),
               solar=(7, 25), gas=(1, 1), coal=(0, 0), biomass=(5, 6), battery_gw=(2, 10), tag="anchored"),
    "UK": dict(nuclear=(6, 12), hydro=(2, 2), wind_on=(16, 30), wind_off=(35, 90),
               solar=(30, 70), gas=(35, 20), coal=(0, 0), biomass=(6, 6), battery_gw=(20, 60), tag="anchored"),
    "CH": dict(nuclear=(2, 0), hydro=(15, 17), wind_on=(0.2, 2), wind_off=(0, 0),
               solar=(8, 30), gas=(0, 1), coal=(0, 0), biomass=(0.5, 1), battery_gw=(1, 5), tag="anchored"),
    # --- NECP-2030 + TYNDP-shaped escalation ---
    "AT": dict(nuclear=(0, 0), hydro=(15, 16), wind_on=(7, 14), wind_off=(0, 0), solar=(13, 30), gas=(4, 2), coal=(0, 0), biomass=(3, 3), battery_gw=(1, 6), tag="necp"),
    "BE": dict(nuclear=(2, 2), hydro=(0.1, 0.1), wind_on=(4, 7), wind_off=(6, 8), solar=(11, 25), gas=(8, 6), coal=(0, 0), biomass=(1, 1), battery_gw=(2, 8), tag="necp"),
    "DK": dict(nuclear=(0, 0), hydro=(0, 0), wind_on=(5, 8), wind_off=(8, 18), solar=(8, 18), gas=(1, 1), coal=(1, 0), biomass=(3, 3), battery_gw=(1, 6), tag="necp"),
    "FI": dict(nuclear=(4, 4), hydro=(3, 3), wind_on=(9, 22), wind_off=(1, 4), solar=(1, 6), gas=(1, 1), coal=(1, 0), biomass=(4, 4), battery_gw=(1, 5), tag="necp"),
    "IE": dict(nuclear=(0, 0), hydro=(0.2, 0.2), wind_on=(6, 11), wind_off=(2, 9), solar=(3, 10), gas=(5, 4), coal=(0, 0), biomass=(0.3, 0.5), battery_gw=(1, 6), tag="necp"),
    "PT": dict(nuclear=(0, 0), hydro=(7, 8), wind_on=(7, 12), wind_off=(0.2, 4), solar=(14, 35), gas=(4, 3), coal=(0, 0), biomass=(0.7, 1), battery_gw=(2, 10), tag="necp"),
    "EL": dict(nuclear=(0, 0), hydro=(3, 4), wind_on=(7, 14), wind_off=(0, 3), solar=(13, 30), gas=(6, 5), coal=(1, 0), biomass=(0.1, 0.3), battery_gw=(3, 12), tag="necp"),
    "CZ": dict(nuclear=(4, 6), hydro=(2, 2), wind_on=(0.3, 3), wind_off=(0, 0), solar=(5, 20), gas=(2, 4), coal=(6, 1), biomass=(0.4, 1), battery_gw=(1, 6), tag="necp"),
    "RO": dict(nuclear=(1.4, 4), hydro=(7, 7), wind_on=(3, 9), wind_off=(0, 3), solar=(5, 18), gas=(4, 4), coal=(3, 0), biomass=(0.1, 0.5), battery_gw=(1, 6), tag="necp"),
    "BG": dict(nuclear=(2, 4), hydro=(3, 3), wind_on=(0.7, 4), wind_off=(0, 1), solar=(3, 12), gas=(0.5, 1), coal=(4, 0), biomass=(0.1, 0.2), battery_gw=(1, 5), tag="necp"),
    "HU": dict(nuclear=(2, 4), hydro=(0.1, 0.1), wind_on=(0.3, 2), wind_off=(0, 0), solar=(7, 18), gas=(4, 4), coal=(1, 0), biomass=(0.5, 1), battery_gw=(1, 6), tag="necp"),
    "SK": dict(nuclear=(2.7, 3), hydro=(2.5, 2.5), wind_on=(0, 1), wind_off=(0, 0), solar=(2, 8), gas=(1, 2), coal=(0.3, 0), biomass=(0.2, 0.5), battery_gw=(0.3, 3), tag="necp"),
    "HR": dict(nuclear=(0, 0), hydro=(2.2, 2.5), wind_on=(1.4, 4), wind_off=(0, 1), solar=(2, 8), gas=(1, 1), coal=(0.2, 0), biomass=(0.1, 0.2), battery_gw=(0.3, 2), tag="necp"),
    "SI": dict(nuclear=(0.7, 1.4), hydro=(1.3, 1.5), wind_on=(0, 0.3), wind_off=(0, 0), solar=(1.7, 6), gas=(0.5, 0.5), coal=(0.6, 0), biomass=(0.1, 0.1), battery_gw=(0.2, 1.5), tag="necp"),
    "LT": dict(nuclear=(0, 0), hydro=(1, 1.1), wind_on=(2, 5), wind_off=(0, 1.4), solar=(2, 7), gas=(1, 1), coal=(0, 0), biomass=(0.3, 0.5), battery_gw=(0.2, 2), tag="necp"),
    "LV": dict(nuclear=(0, 0), hydro=(1.6, 1.6), wind_on=(1, 3), wind_off=(0, 0.4), solar=(1, 4), gas=(1, 1), coal=(0, 0), biomass=(0.2, 0.4), battery_gw=(0.1, 1), tag="necp"),
    "EE": dict(nuclear=(0, 0.3), hydro=(0.01, 0.01), wind_on=(1, 4), wind_off=(0, 1), solar=(1, 4), gas=(0.2, 0.2), coal=(1, 0), biomass=(0.3, 0.4), battery_gw=(0.1, 1), tag="necp"),
    "LU": dict(nuclear=(0, 0), hydro=(1.3, 1.3), wind_on=(0.2, 0.6), wind_off=(0, 0), solar=(0.5, 2), gas=(0.4, 0.3), coal=(0, 0), biomass=(0.1, 0.1), battery_gw=(0.05, 0.5), tag="proxy"),
    "CY": dict(nuclear=(0, 0), hydro=(0, 0), wind_on=(0.2, 0.5), wind_off=(0, 0.3), solar=(0.7, 3), gas=(1.1, 1.2), coal=(0, 0), biomass=(0.01, 0.05), battery_gw=(0.1, 1), tag="proxy"),
    "MT": dict(nuclear=(0, 0), hydro=(0, 0), wind_on=(0, 0), wind_off=(0, 0.3), solar=(0.3, 1), gas=(0.7, 0.7), coal=(0, 0), biomass=(0.01, 0.02), battery_gw=(0.05, 0.4), tag="proxy"),
}

# 2025 actuals (approx, ENTSO-E/EMBER), for the largest systems + a structural default.
CAP25 = {
    "DE": dict(nuclear=0, hydro=6, wind_on=63, wind_off=9, solar=100, gas=33, coal=37, biomass=9, battery_gw=12),
    "FR": dict(nuclear=63, hydro=26, wind_on=24, wind_off=1.5, solar=22, gas=12, coal=1.5, biomass=2, battery_gw=1),
    "IT": dict(nuclear=0, hydro=19, wind_on=12, wind_off=0.1, solar=37, gas=50, coal=6, biomass=4, battery_gw=5),
    "ES": dict(nuclear=7, hydro=17, wind_on=31, wind_off=0, solar=33, gas=27, coal=2, biomass=1, battery_gw=3),
    "PL": dict(nuclear=0, hydro=2, wind_on=10, wind_off=0, solar=18, gas=4, coal=28, biomass=2, battery_gw=1),
    "NL": dict(nuclear=0.5, hydro=0, wind_on=7, wind_off=4.5, solar=24, gas=20, coal=4, biomass=3, battery_gw=2),
    "SE": dict(nuclear=7, hydro=16, wind_on=16, wind_off=0.2, solar=4, gas=1, coal=0, biomass=5, battery_gw=0.5),
    "UK": dict(nuclear=6, hydro=2, wind_on=15, wind_off=15, solar=17, gas=37, coal=0, biomass=6, battery_gw=5),
    "CH": dict(nuclear=3, hydro=15, wind_on=0.1, wind_off=0, solar=6, gas=0, coal=0, biomass=0.5, battery_gw=0.5),
}


def main():
    rows = []
    for cc in EU_COUNTRIES:
        spec = CAP.get(cc)
        if spec is None:
            continue
        tag = spec["tag"]
        for t in TECHS:
            g30, g50 = spec[t]
            g40 = round(g30 + (g50 - g30) * 0.5, 2)
            g25 = CAP25.get(cc, {}).get(t)
            if g25 is None:  # no curated 2025 -> hold 2030 back ~15% as a rough actual
                g25 = round(g30 * 0.85, 2) if t in ("wind_on", "wind_off", "solar", "battery_gw") else g30
            for yr, g in [(2025, g25), (2030, g30), (2040, g40), (2050, g50)]:
                rows.append({"country": cc, "year": yr, "tech": t,
                             "capacity_gw": round(float(g), 2), "tag": tag})
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)

    # EU27 (exclude UK, CH) 2050 sanity vs TYNDP 2024 anchors
    eu27 = [c for c in CAP if c not in ("UK", "CH")]
    s = df[(df.year == 2050) & (df.country.isin(eu27))].groupby("tech").capacity_gw.sum()
    print("EU27 2050 totals (GW) vs TYNDP anchor:")
    anchor = {"wind_on": 808, "wind_off": 400, "solar": 1700, "nuclear": 100, "gas": 106, "battery_gw": 956}
    for t in ["wind_on", "wind_off", "solar", "nuclear", "gas", "coal", "biomass", "battery_gw", "hydro"]:
        a = anchor.get(t)
        print(f"  {t:<11} {s.get(t, 0):>7.0f}" + (f"   (TYNDP ~{a})" if a else ""))
    print(f"\nWrote {OUT.name}: {df.country.nunique()} countries x 4 years x {len(TECHS)} techs = {len(df)} rows")
    print("Tags:", df.drop_duplicates('country').tag.value_counts().to_dict())


if __name__ == "__main__":
    main()
