"""Per-country heat load-duration profile -- the demand input for the merit-order
(dispatch) reframe. Turns annual residential useful-heat demand + heating-degree-days
into (a) a monthly seasonal profile and (b) a load-duration curve, separating a flat
domestic-hot-water (DHW) base load from the weather-driven space-heating (SH) peak.

Method (when2heat / Hotmaps / PyPSA-Eur-Sec standard; see
literature/merit_order_supply_research.md sec 2):
  - split annual heat: SH = (1 - f_DHW) x total, DHW = f_DHW x total; DHW flat over the year.
  - SH distributed across months by HDD-tier monthly shares (cold / EU / mild by annual HDD).
  - load-duration: SH peak = SH_annual / FLH (full-load hours, by tier); a normalised SH
    load-duration shape (calibrated to hours-above-threshold anchors) scaled by peak; DHW adds a
    flat floor so the curve never hits zero in summer.

Output: code/results/heat_load_profile.csv (per country) + a figure. The merit-order model
(next step) stacks 2050 capacities by marginal cost against this load-duration curve to find
where hydrogen sits as a marginal/peaking producer.

Run: cd code && PYTHONPATH=. python -m scripts.heat_load_profile
"""
from __future__ import annotations
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scripts._figstyle import set_style
set_style()
from pathlib import Path
from src.Config import RESULTS_DIR
from src.Economics import COUNTRY_HDD

REPO = Path(__file__).resolve().parents[2]
FIG = REPO / "paper" / "figs" / "diagnostics"; FIG.mkdir(parents=True, exist_ok=True)

# Monthly space-heating shares (% of annual SH), Eurostat nrg_chdd_m tiers (research sec 2)
MONTHLY = {
    "cold": [.15,.135,.125,.09,.06,.02,.01,.02,.05,.08,.11,.14],
    "eu":   [.17,.15,.14,.09,.05,.01,.01,.01,.03,.07,.12,.16],
    "mild": [.215,.155,.145,.095,.03,.01,.00,.00,.005,.04,.13,.175],
}
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
# normalised SH load-duration anchors: (cumulative-hour fraction, level as fraction of peak)
LDC_X = [0.0, 0.011, 0.11, 0.46, 1.0]
LDC_Y = [1.0, 0.80, 0.50, 0.20, 0.0]
CUM_HOURS = [100, 500, 1000, 2000, 4000, 8760]


def tier(hdd):
    return "cold" if hdd > 4000 else ("mild" if hdd < 2000 else "eu")


def params(hdd):
    t = tier(hdd)
    f_dhw = {"cold": 0.15, "eu": 0.18, "mild": 0.20}[t]
    flh = {"cold": 2200, "eu": 2000, "mild": 1400}[t]   # SH full-load hours
    return t, f_dhw, flh


def main():
    bm = pd.read_csv(RESULTS_DIR / "benchmark_multi.csv").set_index("country")
    rows = []
    for c, hdd in COUNTRY_HDD.items():
        if c not in bm.index:
            continue
        D = float(bm.loc[c, "bottomup_TWh"])          # annual useful heat, TWh
        t, f_dhw, flh = params(hdd)
        sh, dhw = (1 - f_dhw) * D, f_dhw * D
        msh = np.array(MONTHLY[t]); msh = msh / msh.sum()
        sh_month = sh * msh
        dhw_month = np.full(12, dhw / 12.0)
        tot_month = sh_month + dhw_month
        avg_gw = D * 1e3 / 8760.0                       # TWh -> GW average
        sh_peak_gw = sh * 1e3 / flh                     # SH peak power
        dhw_base_gw = dhw * 1e3 / 8760.0
        peak_gw = sh_peak_gw + dhw_base_gw
        # load-duration: demand (GW) exceeded for N hours
        ldc = {}
        for h in CUM_HOURS:
            x = h / 8760.0
            sh_frac = float(np.interp(x, LDC_X, LDC_Y))
            ldc[f"GW_at_{h}h"] = round(sh_peak_gw * sh_frac + dhw_base_gw, 2)
        row = {"country": c, "hdd": hdd, "tier": t, "annual_TWh": round(D, 1),
               "f_dhw": f_dhw, "sh_flh": flh, "avg_GW": round(avg_gw, 2),
               "peak_GW": round(peak_gw, 2), "peak_over_avg": round(peak_gw / avg_gw, 2),
               "dhw_base_GW": round(dhw_base_gw, 2)}
        row.update(ldc)
        row.update({f"m_{MONTHS[i]}": round(tot_month[i] / D, 3) for i in range(12)})
        rows.append(row)
    df = pd.DataFrame(rows).sort_values("annual_TWh", ascending=False)
    df.to_csv(RESULTS_DIR / "heat_load_profile.csv", index=False)

    # figure: EU-aggregate monthly profile + representative load-duration curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    eu_m = df[[f"m_{m}" for m in MONTHS]].mul(df.annual_TWh, axis=0).sum() / df.annual_TWh.sum()
    ax1.bar(MONTHS, eu_m.values * 100, color="#08519c")
    ax1.set_ylabel("% of annual heat demand"); ax1.set_title("EU monthly heat demand")
    ax1.axhline(100/12, color="#d62728", ls="--", lw=1, label="flat (8.3%)"); ax1.legend(frameon=False)
    for c, col in [("DE", "#08519c"), ("ES", "#e6550d"), ("FI", "#2ca02c")]:
        if c in df.country.values:
            r = df[df.country == c].iloc[0]
            ys = [r[f"GW_at_{h}h"] for h in CUM_HOURS]
            ax2.plot(CUM_HOURS, ys, "o-", label=f"{c} ({r.tier})", lw=2)
    ax2.set_xlabel("hours/year demand is exceeded"); ax2.set_ylabel("heat demand (GW)")
    ax2.set_title("Heat load-duration curve")
    ax2.axvspan(0, 500, color="#d62728", alpha=0.08, label="peak slice")
    ax2.legend(frameon=False)
    fig.savefig(FIG / "F10_heat_load_profile.png"); plt.close(fig)

    print(df[["country", "tier", "annual_TWh", "peak_GW", "peak_over_avg", "sh_flh"]].head(12).to_string(index=False))
    print(f"\nWrote results/heat_load_profile.csv ({len(df)} countries) + F10_heat_load_profile.png")
    print(f"EU peak/avg range: {df.peak_over_avg.min():.1f}-{df.peak_over_avg.max():.1f} "
          f"(mild countries peakier, as expected)")


if __name__ == "__main__":
    main()
