"""
code/scripts/generate_dashboard_data.py — Full data generator
"""
import json, sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "code"))

import numpy as np
import pandas as pd

from src.Config import EU_COUNTRIES, PROCESSED_DIR
from src.Policy import (
    BOILER_BANS, CARBON_PRICE_SCENARIOS, GRID_CARBON_INTENSITY,
    GAS_GRID_COVERAGE, SWITZERLAND_POLICY,
    get_carbon_price, get_grid_carbon_intensity, ETS2_PASSTHROUGH_RATE,
)
from src.Economics import (
    TECH_PARAMS, compute_lcoh, get_fuel_price, get_annual_hours,
    capital_recovery_factor, DISCOUNT_RATE_REAL, DISCOUNT_RATE_SCENARIOS,
    GAS_PRICE_BY_COUNTRY, ELEC_PRICE_BY_COUNTRY, H2_PRICE_TRAJECTORIES,
    H2_PRICE_SCENARIO, get_cop, get_capex, get_fom,
)
from src.Policy import get_carbon_cost_adder_eur_per_mwh_useful, CARBON_PRICE_SCENARIO

RESULTS_DIR   = REPO_ROOT / "code" / "results"
DASHBOARD_DIR = REPO_ROOT / "dashboard"
DOCS_DIR      = REPO_ROOT / "docs"
for d in [DASHBOARD_DIR, DOCS_DIR]: d.mkdir(exist_ok=True)

ALL_YEARS      = list(range(2025, 2051))
SNAPSHOT_YEARS = [2025, 2030, 2035, 2040, 2045, 2050]

COUNTRY_META = {
    "AT":{"name":"Austria","flag":"🇦🇹","lat":47,"lon":14,"eu":True},
    "BE":{"name":"Belgium","flag":"🇧🇪","lat":50,"lon":4,"eu":True},
    "BG":{"name":"Bulgaria","flag":"🇧🇬","lat":43,"lon":25,"eu":True},
    "CY":{"name":"Cyprus","flag":"🇨🇾","lat":35,"lon":33,"eu":True},
    "CZ":{"name":"Czech Republic","flag":"🇨🇿","lat":50,"lon":15,"eu":True},
    "DE":{"name":"Germany","flag":"🇩🇪","lat":51,"lon":10,"eu":True},
    "DK":{"name":"Denmark","flag":"🇩🇰","lat":56,"lon":10,"eu":True},
    "EE":{"name":"Estonia","flag":"🇪🇪","lat":59,"lon":25,"eu":True},
    "ES":{"name":"Spain","flag":"🇪🇸","lat":40,"lon":-3,"eu":True},
    "FI":{"name":"Finland","flag":"🇫🇮","lat":64,"lon":26,"eu":True},
    "FR":{"name":"France","flag":"🇫🇷","lat":46,"lon":2,"eu":True},
    # Greece is keyed "EL" throughout the model, following Eurostat rather than
    # ISO-3166. Keying it "GR" here made every price, policy, climate and
    # building-stock lookup below miss, so the dashboard showed Greece the EU-average
    # fallbacks instead of its own figures.
    "EL":{"name":"Greece","flag":"🇬🇷","lat":39,"lon":22,"eu":True},
    "HR":{"name":"Croatia","flag":"🇭🇷","lat":45,"lon":16,"eu":True},
    "HU":{"name":"Hungary","flag":"🇭🇺","lat":47,"lon":19,"eu":True},
    "IE":{"name":"Ireland","flag":"🇮🇪","lat":53,"lon":-8,"eu":True},
    "IT":{"name":"Italy","flag":"🇮🇹","lat":42,"lon":12,"eu":True},
    "LT":{"name":"Lithuania","flag":"🇱🇹","lat":56,"lon":24,"eu":True},
    "LU":{"name":"Luxembourg","flag":"🇱🇺","lat":50,"lon":6,"eu":True},
    "LV":{"name":"Latvia","flag":"🇱🇻","lat":57,"lon":25,"eu":True},
    "MT":{"name":"Malta","flag":"🇲🇹","lat":36,"lon":14,"eu":True},
    "NL":{"name":"Netherlands","flag":"🇳🇱","lat":52,"lon":5,"eu":True},
    "PL":{"name":"Poland","flag":"🇵🇱","lat":52,"lon":20,"eu":True},
    "PT":{"name":"Portugal","flag":"🇵🇹","lat":39,"lon":-8,"eu":True},
    "RO":{"name":"Romania","flag":"🇷🇴","lat":46,"lon":25,"eu":True},
    "SE":{"name":"Sweden","flag":"🇸🇪","lat":60,"lon":18,"eu":True},
    "SI":{"name":"Slovenia","flag":"🇸🇮","lat":46,"lon":15,"eu":True},
    "SK":{"name":"Slovakia","flag":"🇸🇰","lat":48,"lon":19,"eu":True},
    "CH":{"name":"Switzerland","flag":"🇨🇭","lat":47,"lon":8,"eu":False},
    "UK":{"name":"United Kingdom","flag":"🇬🇧","lat":54,"lon":-2,"eu":False},
}

def breakdown(tech, code, year):
    p = TECH_PARAMS[tech]
    t = max(0, min(1, (year-2025)/25))
    if "scop_2025" in p:
        eta = get_cop(tech, code, year)
    else:
        e0 = p.get("efficiency_2025", 0.92)
        e1 = p.get("efficiency_2050", e0)
        eta = e0 + t*(e1-e0)
    eta = max(eta, 0.1)
    # Capital is charged on HEAT OUTPUT, with no efficiency term: annual_hours is
    # full-load hours of heat and capex is EUR per kW of heat. This file carried its own
    # copy of the doubled-efficiency error that was removed from Economics.compute_lcoh,
    # and its output is published, so the public dashboard was understating heat-pump
    # capital by a factor of the seasonal performance factor.
    from src.Economics import (DISCOUNT_RATE_BY_COUNTRY,
                               h2_distribution_adder_eur_mwh,
                               electricity_distribution_adder_eur_mwh,
                               h2_seasonal_storage_adder_eur_mwh)
    capex = get_capex(tech, year, code)             # country-adjusted
    r = DISCOUNT_RATE_BY_COUNTRY.get(code, DISCOUNT_RATE_REAL)
    crf = capital_recovery_factor(r, p["lifetime_yrs"])
    ah = get_annual_hours(code)
    aheat = ah / 1000
    capex_c = round(crf*capex/aheat, 1)
    fom_country = get_fom(tech, code)               # country-adjusted
    fom_c   = round(fom_country/aheat, 1)
    storage_c = 0.0
    if tech == "h2_boiler":
        infra_c = round(h2_distribution_adder_eur_mwh(code, r, mode="blend", bound="central"), 1)
        storage_c = round(h2_seasonal_storage_adder_eur_mwh(code, eta), 1)
    elif tech in ("hp_air", "hp_ground", "resistance_heater"):
        infra_c = round(electricity_distribution_adder_eur_mwh(code, r, bound="central"), 1)
    else:
        infra_c = 0.0
    vom_c   = p["vom_eur_mwh"]
    fuel_c  = round(get_fuel_price(p["fuel"], code, year)/eta, 1)
    carbon_c= round(get_carbon_cost_adder_eur_per_mwh_useful(p["fuel"],code,year,eta,CARBON_PRICE_SCENARIO),1)
    return {"capex":capex_c,"fom":fom_c,"vom":vom_c,"fuel":fuel_c,"carbon":carbon_c,
            "network":infra_c,"storage":storage_c,
            "total":round(capex_c+fom_c+vom_c+fuel_c+carbon_c+infra_c+storage_c,1)}

def interp_h2(traj, year):
    ys = sorted(traj.keys())
    if year <= ys[0]: return traj[ys[0]]
    if year >= ys[-1]: return traj[ys[-1]]
    for i in range(len(ys)-1):
        y0,y1=ys[i],ys[i+1]
        if y0<=year<=y1:
            t=(year-y0)/(y1-y0)
            return round(traj[y0]+t*(traj[y1]-traj[y0]),1)
    return traj[ys[-1]]

def main():
    print(f"Generating full dashboard data...")
    scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]

    # Building stock
    stock_path = PROCESSED_DIR/"building_stock_nuts3.csv"
    stock_df = pd.read_csv(stock_path) if stock_path.exists() else pd.DataFrame()
    print(f"  Building stock: {len(stock_df)} rows")

    # Country stats from stock
    country_stats = {}
    if not stock_df.empty:
        for code, grp in stock_df.groupby("country"):
            twh = round(grp["heat_2015_MWh"].sum()/1e6, 1)
            total_dw = grp["dwellings_2021"].sum()
            shares = {}
            for bt, bg in grp.groupby("building_type"):
                shares[bt] = round(bg["dwellings_2021"].sum()/total_dw*100 if total_dw>0 else 0, 1)
            nuts3 = grp.groupby("nuts_id")["heat_2015_MWh"].sum().nlargest(20)
            country_stats[code] = {
                "heat_demand_twh": twh,
                "building_shares": shares,
                "top_nuts3": {k: round(v/1e6,3) for k,v in nuts3.items()},
            }

    # Build per-country data
    countries = {}
    for code, meta in COUNTRY_META.items():
        print(f"  {code}", end=" ", flush=True)
        ban = BOILER_BANS.get(code, {})

        # Full LCOH trajectory
        lcoh_full = {}
        lcoh_bd   = {}
        for tech in TECH_PARAMS:
            lcoh_full[tech] = {}
            lcoh_bd[tech]   = {}
            for year in ALL_YEARS:
                try: lcoh_full[tech][year] = round(compute_lcoh(tech,code,year),1)
                except: lcoh_full[tech][year] = None
            for year in SNAPSHOT_YEARS:
                try: lcoh_bd[tech][year] = breakdown(tech,code,year)
                except: lcoh_bd[tech][year] = None

        # Grid CO2 full
        grid_co2_full = {y: round(get_grid_carbon_intensity(code,y),0) for y in ALL_YEARS}

        # Carbon prices snapshots
        carbon = {s: {y: round(get_carbon_price(y,s),1) for y in SNAPSHOT_YEARS}
                  for s in ["LOW","CENTRAL","HIGH"]}

        # H2 prices all trajectories all years
        h2_prices = {
            sn: {y: interp_h2(traj,y) for y in ALL_YEARS}
            for sn,traj in H2_PRICE_TRAJECTORIES.items()
        }

        # CH H2 import
        h2_import = None
        if code=="CH":
            raw = SWITZERLAND_POLICY.get("h2_import_price_eur_per_mwh",{})
            h2_import = {str(yr):{s:v for s,v in sc.items()} for yr,sc in raw.items()}

        # Cheapest tech per snapshot year
        cheapest = {}
        for year in SNAPSHOT_YEARS:
            best_t, best_v = None, float("inf")
            for tech in TECH_PARAMS:
                v = lcoh_full.get(tech,{}).get(year)
                if v and v < best_v: best_t,best_v = tech,v
            cheapest[year] = {"tech":best_t,"lcoh":round(best_v,1) if best_v<float("inf") else None}

        stats = country_stats.get(code,{})
        countries[code] = {
            "meta": {**meta},
            "policy":{
                "subsidies_end":           ban.get("fossil_boiler_subsidies_end",2025),
                "new_build_ban":           ban.get("new_build_fossil_ban",2030),
                "replacement_ban":         ban.get("replacement_fossil_ban",2035),
                "replacement_ban_delayed": ban.get("replacement_fossil_ban_delayed"),
                "full_ban":                ban.get("full_fossil_ban",2040),
                "hp_mandate":              ban.get("hp_mandate_year",2035),
                "hp_mandate_delayed":      ban.get("hp_mandate_year_delayed"),
                "notes":                   ban.get("notes",""),
            },
            "energy":{
                "gas_price_2025":  GAS_PRICE_BY_COUNTRY.get(code,114),
                "elec_price_2025": ELEC_PRICE_BY_COUNTRY.get(code,287),
                "gas_grid_pct":    round(GAS_GRID_COVERAGE.get(code,0.3)*100),
                "h2_import_prices":h2_import,
            },
            "grid_co2":       grid_co2_full,
            "carbon_prices":  carbon,
            "lcoh":           lcoh_full,
            "lcoh_breakdown": lcoh_bd,
            "h2_prices":      h2_prices,
            "annual_hours":   round(get_annual_hours(code)),
            "cheapest_by_year":cheapest,
            "heat_demand_twh":stats.get("heat_demand_twh"),
            "building_shares":stats.get("building_shares",{}),
            "top_nuts3":      stats.get("top_nuts3",{}),
        }
    print()

    # EU aggregate from MC results
    eu_agg = {}
    for scen in scenarios:
        path = RESULTS_DIR/f"mc_summary_{scen}.csv"
        if not path.exists(): print(f"  [skip] {scen}"); continue
        df = pd.read_csv(path)
        hd = df[df["variable"]=="useful_heat_MWh"][["year","q10","q50","q90"]].copy()
        hd[["q10","q50","q90"]] = (hd[["q10","q50","q90"]]/1e6).round(1)
        ts = df[df["variable"]=="tech_share"][["year","tech","q10","q50","q90"]].copy()
        ts[["q10","q50","q90"]] = ts[["q10","q50","q90"]].round(4)
        fe = df[df["variable"]=="final_energy_MWh"][["year","tech","q10","q50","q90"]].copy()
        fe[["q10","q50","q90"]] = (fe[["q10","q50","q90"]]/1e6).round(1)
        eu_agg[scen] = {
            "heat_demand":hd.to_dict(orient="records"),
            "tech_shares": ts.to_dict(orient="records"),
            "final_energy":fe.to_dict(orient="records"),
        }

    output = {
        "generated_at":          datetime.now().isoformat(),
        "scenarios_available":   [s for s in scenarios if s in eu_agg],
        "all_years":             ALL_YEARS,
        "snapshot_years":        SNAPSHOT_YEARS,
        "countries":             countries,
        "eu_aggregate":          eu_agg,
        "tech_meta":             {t:{"fuel":p["fuel"],"capex_2025":p["capex_2025"],"capex_2050":p["capex_2050"],"lifetime":p["lifetime_yrs"]} for t,p in TECH_PARAMS.items()},
        "h2_price_trajectories": H2_PRICE_TRAJECTORIES,
        "discount_rate_scenarios":DISCOUNT_RATE_SCENARIOS,
        "ets2_passthrough":      ETS2_PASSTHROUGH_RATE,
    }

    js = f"// Auto-generated — do not edit\n// {output['generated_at']}\nconst DASHBOARD_DATA = {json.dumps(output,separators=(',',':'),default=str)};\n"

    for dest in [DASHBOARD_DIR/"data.js", DOCS_DIR/"data.js", REPO_ROOT/"data.js"]:
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(js, encoding="utf-8")

    size_kb = round((REPO_ROOT/"data.js").stat().st_size/1024,1)
    avail = output["scenarios_available"]
    print(f"  Written: data.js ({size_kb} KB)")
    print(f"  Countries: {len(countries)} | Scenarios: {avail}")
    print(f"  LCOH points per tech per country: {len(ALL_YEARS)}")
    if size_kb > 1500:
        print(f"\n  ⚠ {size_kb} KB is large — consider upload-on-demand approach if loading is slow")

if __name__ == "__main__":
    main()
