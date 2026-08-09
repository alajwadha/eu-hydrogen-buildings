"""Reduced-form hourly POWER dispatch and the H2-vs-gas peaker investment, to 2050.

This is the explicit hourly layer that the merit-order chapter previously flagged as
future work. It does NOT replace a full unit-commitment model; it is a transparent,
calibrated 8760 dispatch that makes the cold-snap "capacity-short" hours visible and
prices the peaker that fills them. The power coupling stays reduced-form: the link to
the buildings model is the endogenous winter-peak price (power_peak_price.py); here we
add the hour-resolved DISPATCH and the cumulative peaker economics behind it.

PIPELINE per country x year x demand-basis:
  1. Build an 8760 electricity-demand series for one of three bases:
       total_elec : national baseline load (ENTSO-E) + heat-pump electricity
       hp_elec    : heat-pump electricity only (the increment heating adds to the grid)
       thermal    : useful HEAT demand (a heat-side dispatch, sources = heat techs)
     Heat-pump electricity uses a TEMPERATURE-DEPENDENT COP: in the cold snap the COP
     collapses (~0.6 x seasonal), so the ELECTRICITY peak is sharper than the heat peak
     -- the physical reason a cold, still, dark hour stresses the power system.
  2. Build calibrated hourly availability for each generator (solar diurnal+seasonal,
     wind AR(1) with a winter mean and a forced cold-snap dunkelflaute, hydro run-of-
     river seasonal, nuclear flat must-run), from the per-country capacity stack
     (data/power_capacity.csv).
  3. Dispatch by merit order: must-run VRE + nuclear + biomass, then a flexible
     peak-shaving budget (battery 4h + hydro reservoir), then the firm gas fleet; any
     residual is the PEAKER slice -- the capacity-short hours.
  4. Size the peaker to the residual peak and compute its full-load hours and energy.
  5. Price the peaker as H2-fuelled vs gas-fuelled with FULL economics -- fuel, the
     RISING carbon price (gas only), VOM, country labour, and annualised CAPEX -- and
     accumulate profit and system cost 2025->2050, with the fuel-switch crossover year.

Outputs (results/):
  power_dispatch_repday.csv     representative-day hourly stacks (avg / winter / cold-snap)
  power_dispatch_loadduration.csv  load-duration curve + peaker slice, per country-year-basis
  power_dispatch_summary.csv    peak, peaker capacity/hours/energy, short hours, per basis
  power_peaker_economics.csv    H2 vs gas peaker cashflow per country-scenario-year + cumulative
Figures (paper/figs/diagnostics/):
  F20_dispatch_coldsnap   the "6am" stacked-hour dispatch with the peaker filling the gap
  F21_load_duration       load-duration curve, peaker slice shaded
  F22_peaker_cumulative   cumulative H2-vs-gas peaker profit/cost to 2050 + crossover

Calibration sources: ENTSO-E hourly load (shape); JRC/EMHIRES & DEA capacity factors
(solar/wind/hydro); TYNDP 2024 (peaker FLH ~150-500h); DEA Technology Catalogue (OCGT/
H2 turbine CAPEX, efficiency); power_peak_price.py (endogenous clearing price).
Run: cd code && PYTHONPATH=. python -m scripts.power_dispatch
"""
from __future__ import annotations
import zlib
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from src.Config import RESULTS_DIR, DATA_DIR, TECH_DEFAULTS, YEARS
from src.Economics import get_fuel_price, LABOUR_COST_MULTIPLIER, DISCOUNT_RATE_BY_COUNTRY, DISCOUNT_RATE_REAL
from src.Policy import get_carbon_price
from scripts.power_peak_price import (ETA_OCGT, ETA_H2_TURBINE, EF_GAS, GAS_WHOLESALE_2050,
                                       VOM_PEAKER, SCARCITY_PREMIUM, power_storage_adder)
from scripts._figstyle import set_style, short_scen, legend_below, assert_printable, SCEN_COLOR


def country_seed(c: str) -> int:
    """Collision-free deterministic seed per country code.

    The weather draw was previously seeded with 42 + sum(ord(ch) for ch in c), which
    is an ASCII checksum and therefore blind to letter order and to which letters are
    used: the 29 codes collapsed onto 17 distinct seeds, so 20 countries shared a
    bit-identical 8,760-hour wind series with at least one other (FR/ES/SE, CZ/HU/IT,
    CY/PL/SI, LU/MT/RO, BG/DE, DK/FI, HR/NL, LT/UK). That imposed an implied
    cross-country wind-correlation matrix of exact ones and zeros determined by
    spelling, which matters directly for the islanded-versus-copper-plate firm-capacity
    comparison. CRC32 of the code keeps the seed deterministic and reproducible while
    separating every country.
    """
    return 42 + (zlib.crc32(c.encode("ascii")) & 0x7FFFFFFF)

set_style()

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)
FIGP = REPO / "paper" / "figs" / "paper"; FIGP.mkdir(parents=True, exist_ok=True)
CAP_CSV = DATA_DIR / "power_capacity.csv"


def _save(fig, fname: str, pname: str):
    """Save a figure for Abdul's summary (F-name) and the paper figure family (P-name)."""
    for d, n in [(FIG, fname), (FIGP, pname)]:
        fig.savefig(d / f"{n}.png"); fig.savefig(d / f"{n}.pdf")
    plt.close(fig)

# Gas wholesale (hub) price trajectory, EUR/MWh: elevated post-2022 and normalising to a
# long-run ~28 by 2050 (IEA WEO / TTF forward curve). Previously a single flat 2050 value.
GAS_WHOLESALE = {2025: 38.0, 2030: 33.0, 2040: 30.0, 2050: 28.0}
def gas_wholesale(y):
    return float(np.interp(y, list(GAS_WHOLESALE), list(GAS_WHOLESALE.values())))
# H2 seasonal-storage cost learning: salt caverns are a mature, geology-limited technology,
# so only a modest ~17% real cost decline to 2050 (EWI 2023). Multiplies the storage adder.
def storage_learning(y):
    return float(np.interp(y, [2025, 2050], [1.2, 1.0]))

# Turbine electric efficiency, TIME-VARYING (not flat). A peaker is a simple-cycle turbine
# (~40% today; PowerMag, GE Vernova H-class). Both improve modestly with R&D to 2050; the
# H2 turbine improves slightly faster because burning H2 marginally aids efficiency
# (LM6000: +0.8pp vs CH4, ScienceDirect 2024) and attracts focused H2 combustor R&D.
# Generous to H2 -- if it still loses with a turbine MORE efficient than gas, the result holds.
def eta_ocgt(y):       return float(np.interp(y, [2025, 2050], [0.40, 0.42]))
def eta_h2_turbine(y, scenario=None):
    # Hydrogen Push assumes an ADVANCED simple-cycle H2 turbine (its "big advancement"
    # premise): ceiling 48% by 2050 = H-class simple ~43% + H2 combustion bonus
    # (+0.8-3.7pp; ETN/ScienceDirect 2024) + turbine-inlet-temperature 1600->1700C. It stays
    # simple-cycle (fast-start peaker), so CAPEX is unchanged. Other scenarios keep 44%.
    hi = 0.48 if scenario == "H2_PUSH" else 0.44
    return float(np.interp(y, [2025, 2050], [0.40, hi]))

def storage_per_mwh_h2(c):
    """Seasonal H2 storage, EUR per MWh-H2 (BEFORE the turbine efficiency is applied)."""
    from scripts.merit_order_heat import CAVERN, STORE_CAVERN_EUR_KG, STORE_NONCAVERN_EUR_KG, MWH_PER_KG
    eur_kg = STORE_CAVERN_EUR_KG if c in CAVERN else STORE_NONCAVERN_EUR_KG
    return eur_kg / MWH_PER_KG

# CHP cogeneration: a turbine recovering its exhaust heat reaches ~85% total efficiency (DEA
# Technology Catalogue). The waste heat (total minus electric) is credited to district heating
# where a network can absorb it, valued at a low/high band (avoided large-HP heat ~EUR50 to
# avoided peak heat ~EUR100/MWh-heat). The credit is scaled by each country's district-heating
# share -- CHP heat helps mainly where DH is significant (per Ali). Note H2-CHP heat is clean,
# whereas gas-CHP already paid carbon on the same fuel, so under high carbon H2 nets more.
CHP_TOTAL_EFF = 0.85
HEAT_VALUE = {"lo": 50.0, "hi": 100.0}   # EUR/MWh-heat, avoided DH-heat cost band

SCEN = ["CURRENT_POLICIES", "STATED_POLICIES", "NET_ZERO", "H2_PUSH"]
SCEN_LEVERS = {"CURRENT_POLICIES": dict(carbon="LOW", h2="STRANDED", grid=1.15),
               "STATED_POLICIES":  dict(carbon="CENTRAL", h2="CENTRAL", grid=1.0),
               "NET_ZERO":         dict(carbon="HIGH", h2="CENTRAL", grid=0.70),
               "H2_PUSH":          dict(carbon="HIGH", h2="RAPID", grid=1.0)}  # carbon = Net Zero (Ali 2026-06)
BASES = ["total_elec", "hp_elec", "thermal"]

# Power-peaker techno-economics (DEA Technology Catalogue 2023; power turbines, NOT boilers)
H2_TURBINE_CAPEX = 600.0   # EUR/kW, H2-ready open-cycle turbine
GAS_OCGT_CAPEX = 450.0     # EUR/kW, conventional OCGT
PEAKER_LIFE = 25
PEAKER_FOM_FRAC = 0.025

# National baseline (non-heat) electricity demand, TWh/yr ~2023 (ENTSO-E / Ember),
# and a smooth electrification growth factor to 2050 (EVs + industry; electrolysis and
# building heat are added separately so as not to double-count).
BASELINE_TWH_2023 = {
    "DE": 480, "FR": 445, "IT": 300, "ES": 245, "PL": 165, "NL": 113, "SE": 135, "BE": 82,
    "AT": 70, "CZ": 62, "RO": 52, "PT": 50, "EL": 52, "HU": 44, "FI": 82, "DK": 35, "IE": 32,
    "SK": 28, "BG": 33, "HR": 18, "LT": 12, "SI": 14, "LV": 7, "EE": 8, "LU": 6, "CY": 5,
    "MT": 3, "UK": 290, "CH": 58,
}
BASELINE_GROWTH = {2025: 1.00, 2030: 1.10, 2040: 1.25, 2050: 1.40}

# Capacity factors used to calibrate the hourly availability series (annual mean).
CF = {"solar": 0.125, "wind_on": 0.27, "wind_off": 0.45, "hydro_ror": 0.40,
      "nuclear": 0.90, "biomass": 0.60}
# Southern countries get more solar / less seasonal swing.
SOUTH = {"ES", "IT", "PT", "EL", "CY", "MT", "HR", "BG"}
HOURS = 8760
H = np.arange(HOURS)
HOD = H % 24                       # hour of day 0..23
DOY = H // 24                      # day of year 0..364
MONTH = np.clip((DOY / 30.4).astype(int), 0, 11)
# day-of-year angle for seasonality (peak winter at Jan 1)
SEAS = np.cos(2 * np.pi * DOY / 365.0)          # +1 mid-winter, -1 mid-summer
DAYLIGHT = np.clip(np.sin(np.pi * (HOD - 6) / 12.0), 0, None)   # 0 at night, bell 6-18h


# ── capacity ──────────────────────────────────────────────────────────────────
def load_capacity() -> dict:
    df = pd.read_csv(CAP_CSV)
    out: dict = {}
    for (c, y), g in df.groupby(["country", "year"]):
        out.setdefault(c, {})[int(y)] = dict(zip(g.tech, g.capacity_gw))
    return out


# ── demand profiles ─────────────────────────────────────────────────────────--
def heat_profile_row(lp: pd.DataFrame, c: str):
    return lp.loc[c] if c in lp.index else lp.loc["DE"]


def hourly_heat_shape(row) -> np.ndarray:
    """8760 useful-heat shape (GW), calibrated to annual_TWh, with a double daily peak,
    monthly seasonality from the load profile, and a sharpened cold snap."""
    m = np.array([row[f"m_{mn}"] for mn in
                  ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]])
    m = m / m.mean()
    daily = np.array([0.55, 0.5, 0.48, 0.48, 0.52, 0.7, 0.95, 1.15, 1.2, 1.1, 1.0, 0.95,
                      0.92, 0.9, 0.9, 0.95, 1.05, 1.2, 1.28, 1.22, 1.05, 0.85, 0.7, 0.6])
    daily = daily / daily.mean()
    shape = m[MONTH] * daily[HOD]
    # cold snap: coldest COLD_SNAP_DAYS in deep winter, amplified with a sharp morning
    # peak. The window is a module constant rather than a literal because its LENGTH,
    # not its depth, is what decides how much a flexible heat pump can help: intra-day
    # pre-heating cannot move load out of an event longer than the shift window. That
    # made the flexibility bound a restatement of this line until it could be swept.
    cold_days = np.zeros(365)
    cold_days[COLD_SNAP_START:COLD_SNAP_START + COLD_SNAP_DAYS] = 1.0
    snap = 1.0 + 0.6 * cold_days[DOY] * (0.6 + 0.4 * (HOD >= 6) * (HOD <= 9))
    shape = shape * snap
    gw = shape / shape.mean() * row["avg_GW"]
    return gw


def hourly_cop(c: str, heat_gw: np.ndarray, year: int) -> np.ndarray:
    """Temperature-dependent HP COP: falls toward ~0.6x seasonal in the coldest hours,
    so HP electricity peaks harder than heat. Blends air/ground seasonal COP."""
    cop_air = np.interp(year, [2025, 2050], [TECH_DEFAULTS["hp_air"]["seasonal_cop_2025"],
                                             TECH_DEFAULTS["hp_air"]["seasonal_cop_2050"]])
    cop_gnd = np.interp(year, [2025, 2050], [TECH_DEFAULTS["hp_ground"]["seasonal_cop_2025"],
                                             TECH_DEFAULTS["hp_ground"]["seasonal_cop_2050"]])
    scop = 0.75 * cop_air + 0.25 * cop_gnd
    load = heat_gw / heat_gw.max()
    return scop * (1.0 - 0.45 * load)      # coldest (load=1) -> 0.55x seasonal


def annual_hp_share(mc: pd.DataFrame, c: str, year: int) -> float:
    d = mc[(mc.country == c) & (mc.year == year) & (mc.variable == "tech_share")]
    sh = d.set_index("tech")["q50"]
    return float(sh.get("hp_air", 0) + sh.get("hp_ground", 0))


def hourly_demand(c: str, year: int, scenario: str, basis: str,
                  lp: pd.DataFrame, mc: pd.DataFrame):
    """Return (demand_gw_8760, heat_gw_8760) for the chosen basis."""
    row = heat_profile_row(lp, c)
    heat_gw = hourly_heat_shape(row)
    # scale heat to the scenario/year demand level via useful_heat_TWh
    uh = mc[(mc.country == c) & (mc.year == year) & (mc.variable == "useful_heat_TWh") & (mc.tech == "all")]
    if len(uh):
        target_twh = float(uh.q50.iloc[0])
        heat_gw = heat_gw * (target_twh / (heat_gw.mean() * HOURS / 1e3))
    if basis == "thermal":
        return heat_gw, heat_gw
    # heat-pump electricity = (heat served by HP) / COP(temperature)
    hp_sh = annual_hp_share(mc, c, year)
    cop = hourly_cop(c, heat_gw, year)
    hp_elec = heat_gw * hp_sh / cop
    if basis == "hp_elec":
        return hp_elec, heat_gw
    # total_elec = national baseline load + HP electricity
    base_twh = BASELINE_TWH_2023.get(c, 30) * BASELINE_GROWTH[year]
    weekday = np.where((DOY % 7) < 5, 1.0, 0.88)
    base_daily = np.array([0.72, 0.68, 0.66, 0.66, 0.7, 0.8, 0.92, 1.0, 1.05, 1.07, 1.08, 1.08,
                           1.05, 1.03, 1.02, 1.03, 1.07, 1.12, 1.15, 1.13, 1.07, 0.98, 0.88, 0.78])
    base_daily = base_daily / base_daily.mean()
    seas_amp = 0.06 if c in SOUTH else 0.12       # mild winter peak (north) / flatter (south)
    base_shape = base_daily[HOD] * weekday * (1 + seas_amp * SEAS)
    base_gw = base_shape / base_shape.mean() * (base_twh * 1e3 / HOURS)
    return base_gw + hp_elec, heat_gw


# Robustness knobs for the peaker-need RANGE.
#  DUNKELFLAUTE_WIND: cold-snap wind availability as a fraction of normal (depth of the
#  synthetic Dunkelflaute). Central 0.25; swept 0.15 (deep) to 0.40 (mild) for sensitivity.
DUNKELFLAUTE_WIND = 0.25
DUNKEL_SWEEP = [0.15, 0.25, 0.40]

#  COLD_SNAP_DAYS / COLD_SNAP_START: the length and mid-January start of the single
#  synthetic cold-and-still event that sizes the firm fleet. Both the heat spike and the
#  wind lull run on this same window, in every country at once, which is the strongest
#  assumption in the power layer and is disclosed as such in the SI. Central 6 days;
#  swept 2 to 10 by scripts.cold_snap_duration_sweep. That sweep was written on the
#  assumption that the flexibility bound is a function of this length; it is not. The
#  bound tracks the shiftable share, which binds first. What this length does move is the
#  inflexible fleet, from 253.7 GW at two days to 302.0 at ten.
COLD_SNAP_DAYS = 6
COLD_SNAP_START = 8
COLD_SNAP_SWEEP = [2, 4, 6, 10]


# ── generator availability ──────────────────────────────────────────────────--
def vre_availability(c: str, rng, dunkel: float = DUNKELFLAUTE_WIND):
    south = c in SOUTH
    # solar: diurnal bell x seasonal (winter low); calibrated to annual CF
    sol_seas = 1 + (0.35 if south else 0.55) * SEAS * -1   # higher summer
    solar = DAYLIGHT * np.clip(sol_seas, 0.2, None)
    solar = solar / solar.mean() * (CF["solar"] * (1.25 if south else 1.0))
    solar = np.clip(solar, 0, 1)
    # wind: AR(1) around a winter-higher mean; force a cold-snap dunkelflaute
    mean_on = CF["wind_on"] * (1 + 0.25 * SEAS)
    noise = np.zeros(HOURS); a = 0.92
    e = rng.standard_normal(HOURS) * 0.18
    for t in range(1, HOURS):
        noise[t] = a * noise[t-1] + e[t]
    wind_on = np.clip(mean_on + noise, 0.01, 0.98)
    cold = (DOY >= COLD_SNAP_START) & (DOY < COLD_SNAP_START + COLD_SNAP_DAYS)
    wind_on = np.where(cold, np.clip(wind_on * dunkel, 0.02, 0.2), wind_on)   # dunkelflaute
    wind_off = np.clip(CF["wind_off"] / CF["wind_on"] * wind_on, 0.02, 0.98)
    # hydro run-of-river: spring-melt seasonal, smooth
    ror = CF["hydro_ror"] * (1 + 0.35 * np.cos(2 * np.pi * (DOY - 100) / 365.0))
    ror = np.clip(ror, 0.1, 0.95)
    return solar, wind_on, wind_off, ror


def dispatch(c: str, year: int, scenario: str, basis: str, cap: dict,
             lp: pd.DataFrame, mc: pd.DataFrame, rng, dunkel: float = DUNKELFLAUTE_WIND):
    """One full 8760 dispatch. Returns a dict of arrays + scalars."""
    demand, heat_gw = hourly_demand(c, year, scenario, basis, lp, mc)
    k = cap.get(c, {}).get(year, {})
    g = lambda t: float(k.get(t, 0.0))
    solar_a, won_a, woff_a, ror_a = vre_availability(c, rng, dunkel)

    if basis == "thermal":
        # heat-side stack: HP+DH+biomass+gas boiler base, peaker = H2 boiler
        gen = {}
        # treat the firm "non-peaker" heat capacity as the load-duration base at ~500h
        row = heat_profile_row(lp, c)
        firm = row["GW_at_500h"] if "GW_at_500h" in row else demand.mean() * 2
        residual = np.clip(demand - firm, 0, None)
        gen["base_heat"] = np.minimum(demand, firm)
        peaker = residual
        peaker_cap = float(peaker.max())
    else:
        nuclear = g("nuclear") * CF["nuclear"]
        biomass = g("biomass") * CF["biomass"] * 0.8
        solar = g("solar") * solar_a
        wind = g("wind_on") * won_a + g("wind_off") * woff_a
        ror = g("hydro") * 0.4 * ror_a            # ~40% of hydro is run-of-river
        mustrun = nuclear + biomass + solar + wind + ror
        residual = demand - mustrun               # may be negative (surplus)
        gen = dict(nuclear=np.full(HOURS, nuclear), biomass=np.full(HOURS, biomass),
                   solar=solar, wind=wind, hydro_ror=ror)
        gas_cap = g("gas")                         # FIXED firm gas nameplate
        batt_p = g("battery_gw"); batt_e = batt_p * 4.0   # 4-hour battery (power, energy)
        res_p = g("hydro") * 0.6                    # reservoir discharge power (energy-rich)
        # Causal storage dispatch with a tracked STATE OF CHARGE over the whole year. The
        # battery discharges to shave load above the firm gas ceiling and recharges only from
        # genuine spare capacity (when net load after must-run VRE is below that ceiling).
        # The SoC CARRIES across hours, so a multi-day Dunkelflaute DEPLETES the battery and
        # the firm peaker must cover the sustained deficit -- batteries handle the daily peak,
        # not a sustained cold snap (that is what firm capacity is for). Reservoir hydro is
        # energy-rich and contributes up to its power rating. (Earlier versions let the
        # battery fully recharge every day, which wrongly erased the peaker need.)
        net = demand - mustrun                     # load the firm + storage fleet must serve
        flex_dis = np.zeros(HOURS); soc = batt_e; eff = 0.92
        for t in range(HOURS):
            if net[t] > gas_cap:                   # deficit above firm gas -> discharge storage
                want = net[t] - gas_cap
                give = min(want, res_p)            # reservoir first (energy-rich, seasonal)
                b = min(want - give, batt_p, soc)  # then battery, limited by state of charge
                soc -= b
                flex_dis[t] = give + b
            else:                                  # spare capacity -> recharge the battery
                soc = min(batt_e, soc + min(gas_cap - net[t], batt_p) * eff)
        gen["flex"] = flex_dis
        residual = net - flex_dis
        gas = np.clip(residual, 0, gas_cap)
        gen["gas"] = gas
        resid_after_gas = np.clip(residual - gas_cap, 0, None)   # load left for the peaker
        # The peaker (OCGT / H2 turbine) is a FIXED fleet too, not an unbounded residual.
        # Size it to a ~3-hour loss-of-load planning standard (the 4th-highest hour of the
        # year): firm peaking capacity is built for adequacy in normal conditions, and the
        # extreme tail is met as a few hours of LOSS OF LOAD. Output is capped at nameplate;
        # demand above the entire fixed fleet is unserved.
        s = np.sort(resid_after_gas)[::-1]
        # Under a three-hour loss-of-load standard the top three shortfall hours are
        # allowed to go unserved, so the requirement is the 4th-highest. If fewer than
        # four hours exceed the firm ceiling then every shortfall hour already sits
        # inside that allowance and the requirement is zero. The earlier fallback sized
        # to s[0] instead, the single worst hour, which is the most conservative answer
        # where the standard asks for the least. It does not bite the headline run (only
        # Slovakia reaches it, at 0.0 GW) but it made the flexibility sweep
        # non-monotonic: shifting enough load to drop a country below four shortfall
        # hours flipped it from the 4th-highest hour to the highest, and Italy alone
        # swung 17 GW on it.
        peaker_cap_fixed = float(s[3]) if len(s) > 3 and s[3] > 0 else 0.0
        peaker = np.clip(resid_after_gas, 0.0, peaker_cap_fixed)
        gen["unserved"] = np.clip(resid_after_gas - peaker_cap_fixed, 0.0, None)
        peaker_cap = peaker_cap_fixed

    gen["peaker"] = peaker
    short_mask = peaker > 1e-6
    unserved_arr = gen.get("unserved")
    unserved_gwh = float(unserved_arr.sum()) if unserved_arr is not None else 0.0
    lol_hours = int((unserved_arr > 1e-6).sum()) if unserved_arr is not None else 0
    peaker_energy = float(peaker.sum())                      # GWh (GW x 1h)
    return dict(demand=demand, heat_gw=heat_gw, gen=gen, peaker=peaker,
                short_hours=int(short_mask.sum()), peaker_cap_gw=float(peaker_cap),
                peaker_energy_gwh=peaker_energy,
                peaker_flh=(peaker_energy / peaker_cap if peaker_cap > 0 else 0.0),
                unserved_gwh=unserved_gwh, lol_hours=lol_hours,
                peak_gw=float(demand.max()))


# ── peaker economics (H2 vs gas), cumulative to 2050 ─────────────────────────--
def crf(r, n):
    return r * (1 + r) ** n / ((1 + r) ** n - 1)


def peaker_economics(c: str, scenario: str, energy_by_year: dict, cap_by_year: dict,
                     dh_avail: float = 0.0) -> pd.DataFrame:
    """Full-economics cashflow for an H2 vs gas peaker, serving the capacity-short
    energy each year and sized to THAT year's peaker capacity (the fleet builds out
    over time). All inputs are year-varying. In CHP mode the turbine's recovered heat
    is credited to district heating (low/high band), scaled by dh_avail (the country's
    DH share)."""
    lv = SCEN_LEVERS[scenario]
    wacc = DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL)
    labour = LABOUR_COST_MULTIPLIER.get(c, 1.0)
    crf_fom = crf(wacc, PEAKER_LIFE) + PEAKER_FOM_FRAC
    rows = []
    for y in YEARS:
        e_mwh = energy_by_year.get(y, 0.0) * 1e3            # GWh -> MWh
        cap_gw = cap_by_year.get(y, 0.0)
        ann_h2 = crf_fom * H2_TURBINE_CAPEX * cap_gw * 1e6  # EUR/yr at this year's capacity
        ann_gas = crf_fom * GAS_OCGT_CAPEX * cap_gw * 1e6
        cp = get_carbon_price(y, lv["carbon"])               # rises over time
        gas_w = gas_wholesale(y)                             # declines over time
        h2_w = get_fuel_price("hydrogen", c, y, lv["h2"]) * 0.85   # H2 delivered, year-varying
        vom = VOM_PEAKER * (0.5 + 0.5 * labour)
        eo = eta_ocgt(y); eh = eta_h2_turbine(y, scenario)   # H2 turbine eff scenario-aware (H2 Push advanced)
        storage = storage_per_mwh_h2(c) * storage_learning(y) / eh   # EUR/MWh-e at this year's eff
        gas_var = gas_w / eo + cp * EF_GAS / eo + vom
        h2_var = h2_w / eh + storage + vom
        # year-aware endogenous scarcity price: cheaper firm SRMC + scarcity premium
        # (matches power_peak_price.py at 2050; lower in earlier, lower-carbon years)
        clr = min(gas_var, h2_var) + SCARCITY_PREMIUM["central"]
        rev = clr * e_mwh
        gp = rev - (gas_var * e_mwh + ann_gas)               # electricity-only profit, EUR/yr
        hp = rev - (h2_var * e_mwh + ann_h2)
        # CHP heat credit: recovered heat (MWh-heat per MWh-e) x heat value x DH absorption
        heat_gas = max(0.0, (CHP_TOTAL_EFF - eo) / eo)
        heat_h2 = max(0.0, (CHP_TOTAL_EFF - eh) / eh)
        cr_g = lambda v: v * heat_gas * dh_avail * e_mwh
        cr_h = lambda v: v * heat_h2 * dh_avail * e_mwh
        rows.append(dict(country=c, scenario=scenario, year=y,
                         energy_gwh=round(e_mwh / 1e3, 1), clearing_eur_mwh=round(clr, 1),
                         carbon_eur_t=cp, dh_avail=round(dh_avail, 3),
                         gas_var_eur_mwh=round(gas_var, 1), h2_var_eur_mwh=round(h2_var, 1),
                         revenue_meur=round(rev / 1e6, 2),
                         gas_profit_meur=round(gp / 1e6, 2),
                         h2_profit_meur=round(hp / 1e6, 2),
                         gas_profit_chp_lo_meur=round((gp + cr_g(HEAT_VALUE["lo"])) / 1e6, 2),
                         gas_profit_chp_hi_meur=round((gp + cr_g(HEAT_VALUE["hi"])) / 1e6, 2),
                         h2_profit_chp_lo_meur=round((hp + cr_h(HEAT_VALUE["lo"])) / 1e6, 2),
                         h2_profit_chp_hi_meur=round((hp + cr_h(HEAT_VALUE["hi"])) / 1e6, 2),
                         gas_syscost_meur=round((gas_var * e_mwh + ann_gas) / 1e6, 2),
                         h2_syscost_meur=round((h2_var * e_mwh + ann_h2) / 1e6, 2)))
    df = pd.DataFrame(rows)
    # Cumulative, undiscounted: trapezoidal across the 4 milestone years over the
    # 5/10/10-yr steps, so the weights are half-intervals and sum to the 25 years from
    # 2025 to 2050. The terminal year carries a half-step (5), not a full one; an earlier
    # version gave 2050 a weight of 10, which integrated 30 years under a "to 2050" label
    # and inflated every cumulative figure by about a fifth.
    w = {2025: 2.5, 2030: 7.5, 2040: 10, 2050: 5}         # year-weights to integrate
    for col in ["gas_profit_meur", "h2_profit_meur", "gas_profit_chp_lo_meur",
                "gas_profit_chp_hi_meur", "h2_profit_chp_lo_meur", "h2_profit_chp_hi_meur",
                "gas_syscost_meur", "h2_syscost_meur"]:
        df[f"cum_{col}"] = np.cumsum([df.loc[df.year == y, col].iloc[0] * w[y] for y in YEARS])
    return df


# ── representative days + load-duration ──────────────────────────────────────--
def rep_days(disp: dict) -> dict:
    gen = disp["gen"]
    keys = [k for k in gen if k != "peaker"] + ["peaker"]
    def day_mean(mask):
        out = {k: gen[k][mask].reshape(-1, 24).mean(0) for k in keys}
        out["demand"] = disp["demand"][mask].reshape(-1, 24).mean(0)
        return out
    winter = np.isin(MONTH, [0, 1, 11])
    # the capacity-critical day is the one the PEAKER works hardest (deep in a multi-day
    # Dunkelflaute, when the battery is depleted) -- not merely the highest-demand day.
    peaker_by_day = disp["peaker"].reshape(365, 24).sum(1)
    cold_day = int(peaker_by_day.argmax()) if peaker_by_day.max() > 0 \
        else int(disp["demand"].reshape(365, 24).sum(1).argmax())
    cold1 = (DOY == cold_day)
    return {"average": day_mean(np.ones(HOURS, bool)),
            "winter": day_mean(winter),
            "coldsnap": day_mean(cold1)}


def eu_peaker_bounds(cap, lp, mc, dunkel):
    """EU-aggregate 2050 peaker need under a given Dunkelflaute depth, as two bounds:
    ISLANDED (sum of 29 national peakers, no cross-border trade) and COPPER-PLATE (one
    pooled fleet sized to the EU-aggregate residual peak, i.e. perfect interconnection).
    Reality lies between -- nearer the islanded end during a correlated continent-wide
    event, nearer copper-plate when the cold snap is regional."""
    eu_demand = np.zeros(HOURS); eu_mr = np.zeros(HOURS); islanded = 0.0; eu_gas = 0.0
    for c in lp.index:
        if c not in cap:
            continue
        # Advance the generator exactly as main() does, BASES outer and YEARS inner, and
        # read the same cell. A fresh generator here would draw a different weather path
        # and put the central sweep point about 4 per cent above the headline fleet the
        # paper reports beside it (287 against 275 GW), which is weather noise presented
        # as a modelling difference.
        rng = np.random.default_rng(country_seed(c))
        d = None
        for basis in BASES:
            for year in YEARS:
                r = dispatch(c, year, "STATED_POLICIES", basis, cap, lp, mc, rng,
                             dunkel=dunkel)
                if basis == "total_elec" and year == 2050:
                    d = r
        islanded += d["peaker_cap_gw"]
        eu_demand += d["demand"]
        gg = d["gen"]
        eu_mr += gg["nuclear"] + gg["biomass"] + gg["wind"] + gg["solar"] + gg["hydro_ror"] + gg["flex"]
        eu_gas += cap.get(c, {}).get(2050, {}).get("gas", 0.0)
    resid = np.sort(np.clip(eu_demand - eu_mr - eu_gas, 0, None))[::-1]
    copper = float(resid[3]) if len(resid) > 3 and resid[3] > 0 else (float(resid[0]) if len(resid) else 0.0)
    return islanded, copper


def _recovery_projection(energy_store, cap_store, countries):
    """Year-by-year projection (annual 2025-2050) of the share of the peaker's annualised
    CAPEX recovered from market revenue, H2 vs gas, all four scenarios. EU+UK+CH AGGREGATE,
    weighted by each country's peaker energy and capacity (NOT one country). All inputs
    evolve over time; per-country energy/capacity interpolate from the milestone dispatch.
    Answers 'when does it recover?' -- it never reaches 100%."""
    col = dict(SCEN_COLOR)
    cc = [c for c in countries if c in energy_store and c in cap_store]
    rows = []
    for y in range(2025, 2051):
        eo = eta_ocgt(y); gw = gas_wholesale(y)
        for sc, lv in SCEN_LEVERS.items():
            eh = eta_h2_turbine(y, sc)               # scenario-aware (H2 Push advanced turbine)
            cp = get_carbon_price(y, lv["carbon"])
            ge = he = gk = hk = 0.0                      # EU earns / capex sums, gas & H2
            for c in cc:
                e_mwh = float(np.interp(y, YEARS, [energy_store[c][m] for m in YEARS])) * 1e3
                cap_kw = float(np.interp(y, YEARS, [cap_store[c][m] for m in YEARS])) * 1e6
                af = crf(DISCOUNT_RATE_BY_COUNTRY.get(c, DISCOUNT_RATE_REAL), PEAKER_LIFE) + PEAKER_FOM_FRAC
                vom = VOM_PEAKER * (0.5 + 0.5 * LABOUR_COST_MULTIPLIER.get(c, 1.0))
                h2d = get_fuel_price("hydrogen", c, y, lv["h2"])
                sto = storage_per_mwh_h2(c) * storage_learning(y) / eh
                gvar = gw / eo + cp * EF_GAS / eo + vom
                hvar = h2d * 0.85 / eh + sto + vom
                clr = min(gvar, hvar) + SCARCITY_PREMIUM["central"]
                ge += (clr - gvar) * e_mwh; he += (clr - hvar) * e_mwh
                gk += af * GAS_OCGT_CAPEX * cap_kw; hk += af * H2_TURBINE_CAPEX * cap_kw
            rows.append(dict(year=y, scenario=sc,
                             gas_recovery_pct=round(ge / gk * 100, 1) if gk else 0.0,
                             h2_recovery_pct=round(he / hk * 100, 1) if hk else 0.0))
    df = pd.DataFrame(rows); df.to_csv(RESULTS_DIR / "power_peaker_recovery_projection.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for sc in SCEN:
        d = df[df.scenario == sc]
        ax.plot(d.year, d.h2_recovery_pct, "-", color=col[sc], lw=2.0, label=f"{short_scen(sc)} (H₂)")
        ax.plot(d.year, d.gas_recovery_pct, "--", color=col[sc], lw=1.3)
    ax.plot([], [], "--", color="#555", lw=1.3, label="gas peaker (dashed, any scenario)")
    ax.axhline(100, color="k", lw=1.1); ax.text(2025.3, 103, "break-even (100%)", fontsize=9)
    ax.axhline(0, color="#999", lw=0.6)
    ax.set_ylabel("Capital recovered from market revenue (%)"); ax.set_xlabel("Year")
    ax.set_xlim(2025, 2050); ax.set_ylim(-80, 170)
    ax.set_title("Peaker capital recovery to 2050 (EU+UK+CH): gas slips below break-even as the grid\ndecarbonises; H₂ (solid) never reaches it", fontsize=11)
    legend_below(ax, ncol=4)
    _save(fig, "F25_recovery_projection", "P25_recovery_projection")
    print("\n=== Capital-recovery projection (EU+UK+CH aggregate, % of CAPEX recovered) ===")
    print(f"{'scenario':<16}{'fuel':>5}" + "".join(f"{y:>8}" for y in [2025, 2030, 2040, 2050]))
    for sc in SCEN:
        d = df[df.scenario == sc].set_index("year")
        for fuel, c2 in [("gas", "gas_recovery_pct"), ("H2", "h2_recovery_pct")]:
            print(f"{sc:<16}{fuel:>5}" + "".join(f"{d.loc[y, c2]:>7.0f}%" for y in [2025, 2030, 2040, 2050]))


def _robustness(cap, lp, mc):
    """Peaker-need range across interconnection (islanded vs copper-plate) and
    Dunkelflaute depth -- the two assumptions the headline 270 GW is most sensitive to."""
    rows = []
    for dk in DUNKEL_SWEEP:
        isl, cop = eu_peaker_bounds(cap, lp, mc, dk)
        rows.append(dict(dunkelflaute_wind=dk, islanded_gw=round(isl), copperplate_gw=round(cop)))
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "power_dispatch_robustness.csv", index=False)
    print("\n=== Peaker-need ROBUSTNESS: interconnection x Dunkelflaute depth (EU+UK+CH, 2050) ===")
    print(f"{'wind x':>8}{'islanded GW':>14}{'copper-plate GW':>17}")
    for _, r in df.iterrows():
        print(f"{r.dunkelflaute_wind:>8.2f}{r.islanded_gw:>14.0f}{r.copperplate_gw:>17.0f}")
    print("(reality sits between the two columns; nearer islanded in a correlated event)")
    return df


def main():
    cap = load_capacity()
    lp = pd.read_csv(RESULTS_DIR / "heat_load_profile.csv").set_index("country")
    mc = pd.read_csv(RESULTS_DIR / "mc_country_STATED_POLICIES.csv")
    countries = [c for c in cap if c in lp.index]
    # district-heating share per country (2050) -> how much CHP waste heat a DH network can
    # absorb; drives the CHP heat credit (helps mainly where DH is significant, per Ali).
    dhc = mc[(mc.year == 2050) & (mc.tech == "district_heat") & (mc.variable == "tech_share")]
    dh_share = dict(zip(dhc.country, dhc.q50)) if len(dhc) else {}

    summ, reprows, ldrows = [], [], []
    energy_store = {}     # c -> {year: peaker_energy_gwh @ total_elec}
    cap_store = {}        # c -> {year: peaker_cap_gw   @ total_elec}
    eu_demand = np.zeros(HOURS); eu_peaker = np.zeros(HOURS); eu_gen = {}   # EU-27+UK+CH aggregate, 2050
    for c in countries:
        rng = np.random.default_rng(country_seed(c))  # deterministic per country
        for basis in BASES:
            for year in YEARS:
                d = dispatch(c, year, "STATED_POLICIES", basis, cap, lp, mc, rng)
                summ.append(dict(country=c, basis=basis, year=year, peak_gw=round(d["peak_gw"], 2),
                                 peaker_cap_gw=round(d["peaker_cap_gw"], 2),
                                 short_hours=d["short_hours"],
                                 peaker_energy_gwh=round(d["peaker_energy_gwh"], 1),
                                 peaker_flh=round(d["peaker_flh"], 0),
                                 unserved_gwh=round(d.get("unserved_gwh", 0.0), 1),
                                 lol_hours=d.get("lol_hours", 0)))
                if basis == "total_elec":
                    energy_store.setdefault(c, {})[year] = d["peaker_energy_gwh"]
                    cap_store.setdefault(c, {})[year] = d["peaker_cap_gw"]
                    if year == 2050:
                        eu_demand += d["demand"]; eu_peaker += d["peaker"]
                        for k, arr in d["gen"].items():
                            eu_gen[k] = eu_gen.get(k, np.zeros(HOURS)) + arr
                        rd = rep_days(d)
                        for dt, dd in rd.items():
                            for h in range(24):
                                reprows.append(dict(country=c, daytype=dt, hour=h,
                                    **{k: round(float(v[h]), 3) for k, v in dd.items()}))
                        # net-load-duration of the load the THERMAL fleet serves (gas +
                        # peaker = demand - VRE - must-run - flex); the slice above firm
                        # gas capacity is the peaker's energy.
                        thermal = d["gen"]["gas"] + d["peaker"]
                        ld = np.sort(thermal)[::-1]
                        gas_cap = cap.get(c, {}).get(2050, {}).get("gas", 0.0)
                        for i in range(0, HOURS, 60):
                            ldrows.append(dict(country=c, rank_h=i, load_gw=round(float(ld[i]), 2),
                                               gas_cap=round(gas_cap, 2)))
    # EU-27+UK+CH aggregate cold-snap day (sum of all countries' 2050 dispatch)
    eu_disp = dict(demand=eu_demand, gen=eu_gen, peaker=eu_peaker)
    for dt, dd in rep_days(eu_disp).items():
        for h in range(24):
            reprows.append(dict(country="EU", daytype=dt, hour=h,
                                **{k: round(float(v[h]), 3) for k, v in dd.items()}))
    # 365-day seasonality: daily means of the EU-27+UK+CH 2050 hourly dispatch (the marquee figure)
    nday = HOURS // 24
    daily = {k: v[:nday * 24].reshape(nday, 24).mean(1) for k, v in eu_gen.items()}
    daily["peaker"] = eu_peaker[:nday * 24].reshape(nday, 24).mean(1)
    daily["demand"] = eu_demand[:nday * 24].reshape(nday, 24).mean(1)
    pd.DataFrame(daily).to_csv(RESULTS_DIR / "power_dispatch_daily.csv", index=False)

    # The annual electricity total and its heat-pump increment were the DENOMINATOR of the
    # peaker's energy share and lived only in this function's runtime, in no committed
    # column. Both manuscripts consequently quoted the H2 Push pair (4,497 / 401 TWh)
    # against a fleet computed on STATED_POLICIES, whose own pair is 4,513 / 417 TWh: the
    # numerator and the denominator came from different scenarios and no gate could see it.
    # Written out here so the claim is checkable.
    _nonheat = sum(BASELINE_TWH_2023.get(c, 30) for c in countries) * BASELINE_GROWTH[2050]
    _hp = sum(hourly_demand(c, 2050, "STATED_POLICIES", "hp_elec", lp, mc)[0].mean()
              for c in countries) * HOURS / 1e3
    pd.DataFrame([dict(scenario="STATED_POLICIES", year=2050,
                       nonheat_twh=round(_nonheat, 1), hp_elec_twh=round(_hp, 1),
                       total_elec_twh=round(_nonheat + _hp, 1))]).to_csv(
        RESULTS_DIR / "power_demand_denominator.csv", index=False)
    pd.DataFrame(summ).to_csv(RESULTS_DIR / "power_dispatch_summary.csv", index=False)
    pd.DataFrame(reprows).to_csv(RESULTS_DIR / "power_dispatch_repday.csv", index=False)
    pd.DataFrame(ldrows).to_csv(RESULTS_DIR / "power_dispatch_loadduration.csv", index=False)

    econ = []
    for c in countries:
        for s in SCEN:
            econ.append(peaker_economics(c, s, energy_store.get(c, {}), cap_store.get(c, {}),
                                         dh_avail=float(dh_share.get(c, 0.0))))
    econ_df = pd.concat(econ, ignore_index=True)
    econ_df.to_csv(RESULTS_DIR / "power_peaker_economics.csv", index=False)

    _print_and_plot(pd.DataFrame(summ), pd.DataFrame(reprows), econ_df)
    _recovery_projection(energy_store, cap_store, countries)
    _robustness(cap, lp, mc)


def _print_and_plot(summ, rep, econ):
    tot = summ[summ.basis == "total_elec"]
    print("=== Capacity-short hours (total electricity incl. heat), by year (EU+UK+CH) ===")
    for y in YEARS:
        d = tot[tot.year == y]
        print(f"  {y}: mean {d.short_hours.mean():.0f} short h/yr, "
              f"peaker FLH {d[d.peaker_flh>0].peaker_flh.mean():.0f}, "
              f"peaker cap {d.peaker_cap_gw.sum():.0f} GW EU, "
              f"peaker energy {d.peaker_energy_gwh.sum()/1e3:.1f} TWh EU, "
              f"loss-of-load {d.unserved_gwh.sum()/1e3:.2f} TWh / {d.lol_hours.mean():.0f} h")
    e50 = econ[econ.year == 2050]
    print("\n=== Peaker 2050 variable cost: H2 vs gas (EUR/MWh) + who is cheaper ===")
    for s in SCEN:
        d = e50[e50.scenario == s]
        n_h2 = int((d.h2_var_eur_mwh < d.gas_var_eur_mwh).sum())
        print(f"  {s:<16} gas {d.gas_var_eur_mwh.mean():.0f}  h2 {d.h2_var_eur_mwh.mean():.0f}  "
              f"-> H2 cheaper in {n_h2}/29")
    print("\n=== Cumulative peaker PROFIT to 2050 (EU sum, bn EUR): power-only vs +CHP heat ===")
    print(f"{'scenario':<16}{'GAS elec':>9}{'+CHP lo':>9}{'+CHP hi':>9} | {'H2 elec':>9}{'+CHP lo':>9}{'+CHP hi':>9}")
    cum = econ[econ.year == 2050]
    for s in SCEN:
        d = cum[cum.scenario == s]
        g = [d.cum_gas_profit_meur.sum()/1e3, d.cum_gas_profit_chp_lo_meur.sum()/1e3, d.cum_gas_profit_chp_hi_meur.sum()/1e3]
        h = [d.cum_h2_profit_meur.sum()/1e3, d.cum_h2_profit_chp_lo_meur.sum()/1e3, d.cum_h2_profit_chp_hi_meur.sum()/1e3]
        print(f"  {s:<14}{g[0]:>9.0f}{g[1]:>9.0f}{g[2]:>9.0f} | {h[0]:>9.0f}{h[1]:>9.0f}{h[2]:>9.0f}")
    # split the cold-snap peaker into its H2-won share (H2 Push) and the gas remainder
    pk = summ[(summ.basis == "total_elec") & (summ.year == 2050)].set_index("country").peaker_cap_gw
    hp = e50[e50.scenario == "H2_PUSH"].set_index("country")
    win = hp.h2_var_eur_mwh < hp.gas_var_eur_mwh
    common = [c for c in pk.index if c in win.index]
    h2_frac = sum(pk[c] for c in common if bool(win[c])) / max(sum(pk[c] for c in common), 1e-9)
    de_frac = 1.0 if "DE" in win.index and bool(win["DE"]) else 0.0
    _fig_coldsnap(rep, "EU", h2_frac=h2_frac); _fig_coldsnap(rep, "DE", suffix="_DE", h2_frac=de_frac)
    _fig_seasonality(h2_frac=h2_frac)
    _fig_loadduration(summ); _fig_cumulative(econ)
    print(f"\nWrote 3 dispatch CSVs + F20/F21/F22 -> {RESULTS_DIR.name}/, {FIG.name}/")


def _fig_coldsnap(rep, country="EU", suffix="", h2_frac=0.77):
    d = rep[(rep.country == country) & (rep.daytype == "coldsnap")].sort_values("hour")
    if not len(d):
        return
    d = d.copy()
    d["peaker_h2"] = d["peaker"] * h2_frac             # peaker capacity hydrogen wins (H2 Push)
    d["peaker_gas"] = d["peaker"] * (1.0 - h2_frac)    # the gas-peaker remainder
    order = ["nuclear", "biomass", "hydro_ror", "wind", "solar", "flex", "gas",
             "peaker_h2", "peaker_gas", "unserved"]
    labels = {"nuclear": "Nuclear", "biomass": "Biomass", "hydro_ror": "Hydro (RoR)",
              "wind": "Wind", "solar": "Solar", "flex": "Battery + reservoir",
              "gas": "Gas (firm, CCGT)", "peaker_h2": "H₂ peaker (H2 Push)",
              "peaker_gas": "Gas peaker", "unserved": "Unserved (loss of load)"}
    cols = {"nuclear": "#7b6888", "biomass": "#8c6d31", "hydro_ror": "#6baed6",
            "wind": "#74c476", "solar": "#fdd835", "flex": "#bdbdbd",
            "gas": "#969696", "peaker_h2": "#d62728", "peaker_gas": "#4d4d4d",
            "unserved": "#3b0a0a"}
    pos = (d.hour.values - 6) % 24              # x-position 0 = 06:00, 23 = 05:00
    sidx = np.argsort(pos); xs = pos[sidx]
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    bottom = np.zeros(24)
    present = [k for k in order if k in d.columns]
    for k in present:
        vals = d[k].values[sidx]
        ax.bar(xs, vals, bottom=bottom, width=0.92, color=cols[k],
               label=labels[k], edgecolor="white", linewidth=0.3,
               hatch=("xxxx" if k == "unserved" else None))
        bottom += vals
    ax.plot(xs, d["demand"].values[sidx], "k-", lw=2.0, label="Electricity demand")
    ax.set_xticks(range(0, 24, 3))
    ax.set_xticklabels([f"{(h+6)%24:02d}:00" for h in range(0, 24, 3)])
    ax.set_xlabel("Hour of cold-snap day (from 06:00)")
    ax.set_ylabel("Power (GW)")
    legend_below(ax, ncol=5)
    _save(fig, f"F20_dispatch_coldsnap{suffix}", f"P20_dispatch_coldsnap{suffix}")


def _fig_seasonality(h2_frac=0.77):
    """365-day seasonality of the EU dispatch. TWO STACKED PANELS sharing the x-axis:
      (top)    the full generation stack, daily means across the year;
      (bottom) a DEDICATED peaker-only panel, zoomed to the few-GW peaker band so the
               H₂-won contribution (red) -- invisible atop the full stack -- is legible,
               with the winter window (DJF) shaded to mark where the peaker earns its keep.
    White background, no in-figure title (caption above)."""
    d = pd.read_csv(RESULTS_DIR / "power_dispatch_daily.csv")
    days = np.arange(len(d))
    ph2 = d["peaker"].values * h2_frac
    pgas = d["peaker"].values * (1.0 - h2_frac)
    base = ["nuclear", "biomass", "hydro_ror", "wind", "solar", "flex", "gas"]
    blab = {"nuclear": "Nuclear", "biomass": "Biomass", "hydro_ror": "Hydro (RoR)", "wind": "Wind",
            "solar": "Solar", "flex": "Battery + reservoir", "gas": "Gas (firm, CCGT)"}
    bcol = {"nuclear": "#7b6888", "biomass": "#8c6d31", "hydro_ror": "#6baed6", "wind": "#74c476",
            "solar": "#fdd835", "flex": "#bdbdbd", "gas": "#969696"}
    keys = [k for k in base if k in d.columns]
    series = [d[k].values for k in keys] + [ph2, pgas]
    labels = [blab[k] for k in keys] + ["H₂ peaker (H2 Push)", "Gas peaker"]
    colors = [bcol[k] for k in keys] + ["#d62728", "#4d4d4d"]
    starts = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    FIGW_IN = 9.6
    assert_printable(FIGW_IN, {"legend": 9.5, "annotation": 9.5, "tick": 10.0,
                               "axis label": 11.0}, column="long",
                     label="P25_dispatch_seasonality")
    # Height raised from 6.6 to 7.2 to make room for the top panel's legend ABOVE the
    # axes. It used to sit below them at bbox y=-0.04, inside an hspace of 0.18; with ten
    # entries at ncol=5 it wrapped to two rows and the second row was drawn into the gap
    # and then painted over by the lower panel's opaque axes. Five entries were invisible
    # in the published figure, among them Wind, the largest band in the panel, and the
    # hydrogen peaker, which is the figure's subject.
    fig, (ax, axp) = plt.subplots(2, 1, figsize=(FIGW_IN, 7.2), sharex=True,
                                  gridspec_kw=dict(height_ratios=[2.4, 1.0], hspace=0.18))
    fig.patch.set_facecolor("white")
    # ── top: full generation stack ──
    ax.set_facecolor("white")
    ax.stackplot(days, *series, labels=labels, colors=colors, edgecolor="none")
    ax.plot(days, d["demand"].values, color="#111111", lw=1.3, label="Electricity demand")
    ax.set_xlim(0, len(d) - 1); ax.set_ylim(0, None)
    ax.set_ylabel("Power (GW, daily mean)", fontsize=11)
    ax.tick_params(labelsize=10)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=5, frameon=False,
              fontsize=9.5)
    # ── bottom: peaker-only zoom (the result the figure exists to show) ──
    axp.set_facecolor("white")
    # shade the winter window where the peaker runs
    axp.axvspan(0, 59, color="#f2d9d9", alpha=0.55, lw=0)
    axp.axvspan(334, len(d) - 1, color="#f2d9d9", alpha=0.55, lw=0)
    axp.stackplot(days, pgas, ph2, labels=["Gas peaker", "H₂ peaker (H2 Push)"],
                  colors=["#4d4d4d", "#d62728"], edgecolor="none")
    axp.plot(days, d["peaker"].values, color="#7a0d0d", lw=1.6, label="Total peaker")
    axp.set_xticks(starts); axp.set_xticklabels(months, fontsize=10)
    axp.set_xlim(0, len(d) - 1); axp.set_ylim(0, max(1.0, float(d["peaker"].max()) * 1.25))
    axp.set_ylabel("Peaker (GW)", fontsize=11)
    axp.tick_params(labelsize=10)
    axp.text(0.012, 0.90, "Peaker only (zoom): the H₂-won winter contribution",
             transform=axp.transAxes, fontsize=9.5, color="#7a0d0d", fontweight="bold")
    axp.legend(loc="upper right", ncol=1, frameon=False, fontsize=9.5)
    pk = d["peaker"].values
    win = float(np.concatenate([pk[:59], pk[334:]]).mean()); summ_ = float(pk[151:243].mean())
    print(f"Seasonality: peaker daily-mean winter (DJF) {win:.0f} GW vs summer (JJA) {summ_:.0f} GW "
          f"({win/max(summ_,1e-6):.1f}x); H2 share of the peaker {100*h2_frac:.0f}%")
    _save(fig, "F25_dispatch_seasonality", "P25_dispatch_seasonality")


def _fig_loadduration(summ, country="DE"):
    ld = pd.read_csv(RESULTS_DIR / "power_dispatch_loadduration.csv")
    d = ld[ld.country == country].sort_values("rank_h")
    if not len(d):
        return
    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(d.rank_h, d.load_gw, "-", color="#1f77b4", lw=1.8,
            label="Net load served by gas + peaker")
    firm = float(d.gas_cap.iloc[0])
    ax.axhline(firm, color="#969696", ls="--", lw=1.2)
    top = d[d.load_gw >= firm]
    ax.fill_between(top.rank_h, firm, top.load_gw, color="#d62728", alpha=0.40,
                    label="Peaker slice (capacity-short)")
    q = summ.query("country==@country and basis=='total_elec' and year==2050")
    short_h = int(q.short_hours.iloc[0]) if len(q) else int((d.load_gw >= firm).sum() * 60)
    ax.annotate(f"firm gas capacity ({firm:.0f} GW)", (HOURS*0.42, firm), xytext=(0, 8),
                textcoords="offset points", fontsize=9, color="#555")
    ax.annotate(f"peaker needed {short_h} h/yr", (300, firm),
                xytext=(40, 30), textcoords="offset points", fontsize=9, color="#b03a3a")
    ax.set_xlabel("Hours per year (sorted, highest net load first)")
    ax.set_ylabel("Net load to dispatchable fleet (GW)")
    ax.set_xlim(0, HOURS); ax.set_ylim(0, None); legend_below(ax, ncol=2)
    _save(fig, "F21_load_duration", "P21_load_duration")


def _fig_cumulative(econ):
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    col = dict(SCEN_COLOR)
    for s in SCEN:
        d = econ[econ.scenario == s].groupby("year")[["cum_gas_profit_meur", "cum_h2_profit_meur"]].sum().reindex(YEARS)
        ax.plot(YEARS, d.cum_gas_profit_meur / 1e3, "-o", ms=4, color=col[s], label=f"{short_scen(s)} (gas)")
        ax.plot(YEARS, d.cum_h2_profit_meur / 1e3, "--s", ms=4, color=col[s], label=f"{short_scen(s)} (H₂)")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(YEARS); ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative peaker profit, EU+UK+CH (bn€)")
    legend_below(ax, ncol=4)
    _save(fig, "F22_peaker_cumulative", "P22_peaker_cumulative")


if __name__ == "__main__":
    main()
