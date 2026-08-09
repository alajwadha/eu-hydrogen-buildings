#!/usr/bin/env python
"""Consolidate per-country, per-scenario model outputs into a single countries.json
for the interactive globe site. Reads code/results/*.csv, writes ~/countries_site_data.json.

Run:  cd code && PYTHONUTF8=1 python scripts/build_site_data.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

CODE = Path(__file__).resolve().parents[1]      # .../code
RES = CODE / "results"
OUT = Path.home() / "countries_site_data.json"

SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
SCEN_LABEL = {
    "CURRENT_POLICIES": "Current Policies",
    "STATED_POLICIES": "Stated Policies",
    "NET_ZERO": "Net Zero",
    "H2_PUSH": "H2 Push",
}
YEARS = [2025, 2030, 2040, 2050]
CAVERN = {"DE", "NL", "PL", "DK", "UK", "RO", "FR"}

NAME = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
    "EL": "Greece", "ES": "Spain", "FI": "Finland", "FR": "France",
    "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IT": "Italy",
    "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MT": "Malta",
    "NL": "Netherlands", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "CH": "Switzerland",
    "UK": "United Kingdom",
}
ISO3 = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "CY": "CYP", "CZ": "CZE", "DE": "DEU",
    "DK": "DNK", "EE": "EST", "EL": "GRC", "ES": "ESP", "FI": "FIN", "FR": "FRA",
    "HR": "HRV", "HU": "HUN", "IE": "IRL", "IT": "ITA", "LT": "LTU", "LU": "LUX",
    "LV": "LVA", "MT": "MLT", "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU",
    "SE": "SWE", "SI": "SVN", "SK": "SVK", "CH": "CHE", "UK": "GBR",
}
CANON = list(NAME.keys())

TECH_GROUP = {
    "hp_air": "heatPump", "hp_ground": "heatPump",
    "district_heat": "districtHeat",
    "h2_boiler": "hydrogen",
    "gas_boiler": "fossil", "oil_boiler": "fossil",
    "biomass_boiler": "biomass", "resistance_heater": "resistance",
}


def num(x, nd=1):
    try:
        if pd.isna(x):
            return None
        return round(float(x), nd)
    except Exception:
        return None


econ = pd.read_csv(RES / "country_econ_table.csv").set_index("country")
lcoh_scn = pd.read_csv(RES / "country_econ_table_by_scenario.csv")
LCOH_SCN = {(str(r["country"]), str(r["scenario"])): r for _, r in lcoh_scn.iterrows()}
heat = pd.read_csv(RES / "merit_order_heat.csv")
dh = pd.read_csv(RES / "merit_order_dh.csv")
pk = pd.read_csv(RES / "power_peaker_economics.csv")
pk = pk[pk["year"] == 2050]
infra = pd.read_csv(RES / "infrastructure_bill.csv")
infra_idx = {(str(r["country"]), str(r["scenario"])): r for _, r in infra.iterrows()}
mc = {scn: pd.read_csv(RES / f"mc_country_{scn}.csv") for scn in SCEN}
DETAILED = set(mc["H2_PUSH"]["country"].unique())   # 15 countries with a full tech-share mix

# Emissions for all 29 countries live in mc_emissions_<scn>.csv, where co2_by_country
# rows encode the country in the `tech` column. Also grab the EU-29 total per year.
EM = {}       # scenario -> {(country, year): MtCO2}
EU_EM = {}    # scenario -> {year: EU-29 total MtCO2}
for scn in SCEN:
    e = pd.read_csv(RES / f"mc_emissions_{scn}.csv")
    cbc = e[(e["variable"] == "co2_by_country") & (e["carrier"] == "all")]
    EM[scn] = {(str(r["tech"]), int(r["year"])): num(r["q50"]) for _, r in cbc.iterrows()}
    tot = e[(e["variable"] == "co2_MtCO2") & (e["tech"] == "all") & (e["carrier"] == "all")]
    EU_EM[scn] = {str(int(r["year"])): num(r["q50"]) for _, r in tot.iterrows()}


def flag_lookup(df, col):
    d = {}
    for _, r in df.iterrows():
        try:
            d[(str(r["country"]), str(r["scenario"]))] = bool(int(r[col])) if not pd.isna(r[col]) else False
        except (ValueError, TypeError):
            d[(str(r["country"]), str(r["scenario"]))] = bool(r[col])
    return d


heat_win = flag_lookup(heat, "h2_wins_peak")
dh_win = flag_lookup(dh, "h2_beats_gas_chp")
power_win = {}
for _, r in pk.iterrows():
    try:
        power_win[(str(r["country"]), str(r["scenario"]))] = (
            float(r["h2_var_eur_mwh"]) < float(r["gas_var_eur_mwh"])
        )
    except Exception:
        power_win[(str(r["country"]), str(r["scenario"]))] = False


def arena_state(country, scen, win_dict):
    if not win_dict.get((country, scen), False):
        return "loss"
    return "decisive" if country in CAVERN else "marginal"


def shares_for(df_c, year):
    rows = df_c[(df_c["variable"] == "tech_share") & (df_c["year"] == year)]
    if len(rows) == 0:
        return None
    g = {"heatPump": 0.0, "districtHeat": 0.0, "hydrogen": 0.0,
         "fossil": 0.0, "biomass": 0.0, "resistance": 0.0}
    for _, r in rows.iterrows():
        grp = TECH_GROUP.get(str(r["tech"]))
        if grp:
            g[grp] += float(r["q50"] or 0)
    return {k: round(v, 4) for k, v in g.items()}


def emissions_for(country, scen):
    return {str(y): EM[scen].get((country, y)) for y in YEARS}


countries = []
for c in CANON:
    lcoh = {
        "hp": num(econ.at[c, "lcoh_bestHP_2050"]) if c in econ.index else None,
        "h2": num(econ.at[c, "lcoh_H2_2050"]) if c in econ.index else None,
        "gas": num(econ.at[c, "lcoh_gas_2050"]) if c in econ.index else None,
    }
    grid = {
        "elecPrice": num(econ.at[c, "elec_2025_eur_mwh"], 0) if c in econ.index else None,
        "co2_2025": num(econ.at[c, "grid_co2_2025"], 0) if c in econ.index else None,
        "co2_2050": num(econ.at[c, "grid_co2_2050"], 0) if c in econ.index else None,
    }
    entry = {"iso2": c, "iso3": ISO3[c], "name": NAME[c],
             "cavern": c in CAVERN, "detailed": c in DETAILED,
             "lcoh": lcoh, "grid": grid, "scenarios": {}}
    for scn in SCEN:
        df_c = mc[scn][mc[scn]["country"] == c]
        inf = infra_idx.get((c, scn))
        infra_out = None
        if inf is not None:
            infra_out = {
                "elec": num(inf.get("elec_bn_central")),
                "dh": num(inf.get("dh_bn_central")),
                "h2": num(inf.get("h2_bn_central")),
                "total": num(inf.get("total_bn_central")),
            }
        lr = LCOH_SCN.get((c, scn))
        entry["scenarios"][scn] = {
            "lcoh": {
                "hp": num(lr["lcoh_bestHP_2050"]),
                "h2": num(lr["lcoh_H2_2050"]),
                "gas": num(lr["lcoh_gas_2050"]),
            }
            if lr is not None
            else None,
            "emissions": emissions_for(c, scn),
            "shares": shares_for(df_c, 2050),
            "sharesByYear": {str(y): shares_for(df_c, y) for y in YEARS},
            "arenas": {
                "buildingPeak": arena_state(c, scn, heat_win),
                "districtHeat": arena_state(c, scn, dh_win),
                "power": arena_state(c, scn, power_win),
            },
            "infra": infra_out,
        }
    countries.append(entry)

doc = {
    "meta": {
        "scenarios": SCEN,
        "scenarioLabels": SCEN_LABEL,
        "years": YEARS,
        "cavern": sorted(CAVERN),
        "detailedCountries": sorted(DETAILED),
        "euEmissions": EU_EM,
        "source": "Alajwad (2026), OIES working paper; model outputs.",
    },
    "countries": countries,
}
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"Wrote {OUT} ({len(countries)} countries)")
print("Missing LCOH:", [c["iso2"] for c in countries if c["lcoh"]["hp"] is None])
for scn in SCEN:
    n = sum(1 for c in countries if c["scenarios"][scn]["emissions"]["2050"] is not None)
    print(f"  {scn}: {n}/29 have 2050 emissions")
for arena in ["buildingPeak", "districtHeat", "power"]:
    n = sum(1 for c in countries
            if c["scenarios"]["H2_PUSH"]["arenas"][arena] in ("decisive", "marginal"))
    print(f"  H2_PUSH {arena} wins: {n}/29 (expect 16/20/15)")
