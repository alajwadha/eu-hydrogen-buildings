"""Build an interactive Claude-generated HTML dashboard for the LMDI forward
results. Self-contained: single HTML file with embedded JSON + Plotly via CDN.

Open dashboard/lmdi_dashboard.html in any browser to explore:
  - Headline tiles (EU 2025, STATED_POLICIES/NET_ZERO/H2_PUSH 2050, Hotmaps gap)
  - EU aggregate trajectory 2025-2050 (3 scenarios + COST_OPT + Monte Carlo bands)
  - Per-country trajectory picker (dropdown)
  - 2050 demand bar chart per country / per scenario
  - LMDI backcast driver decomposition (population x occupancy x size x intensity)
  - COST_OPT binding-country shadow prices

Run:  python code/scripts/build_lmdi_dashboard.py
Out:  dashboard/lmdi_dashboard.html
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))
import Config as C  # noqa: E402


def _safe_read(p: Path) -> pd.DataFrame:
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def build_data() -> dict:
    """Collect all LMDI / scenario / backcast results into a single dict."""
    res = ROOT / "code" / "results"
    data: dict = {"scenarios": [], "countries": [], "eu_trajectory": {},
                  "country_trajectories": {}, "bar_2050": {},
                  "lmdi_drivers_eu": {}, "shadow_prices": [], "headline": {}}

    # Scenarios + per-year EU summary (mc_summary_*.csv uses 'variable',
    # 'useful_heat_MWh' is the total across tech/carrier=all when summed).
    scenarios = ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]
    for sc in scenarios:
        f = res / f"mc_summary_{sc}.csv"
        df = _safe_read(f)
        if df.empty:
            continue
        sub = df[df["variable"] == "useful_heat_MWh"].copy()
        sub = sub.groupby("year", as_index=False).agg({"q10": "sum", "q50": "sum", "q90": "sum"})
        sub = sub.sort_values("year")
        traj = {"year": sub.year.tolist(),
                "q10": (sub.q10 / 1e6).round(1).tolist(),
                "q50": (sub.q50 / 1e6).round(1).tolist(),
                "q90": (sub.q90 / 1e6).round(1).tolist()}
        data["eu_trajectory"][sc] = traj
        data["scenarios"].append(sc)

    # COST_OPT pathway -> EU aggregate per year (90% variant as headline)
    co_path = res / "cost_opt_pathway.csv"
    if co_path.exists():
        co = pd.read_csv(co_path)
        if "variant" in co.columns:
            for variant in ["COST_OPT_75", "COST_OPT_90", "COST_OPT_100"]:
                sub = co[co.variant == variant]
                if sub.empty:
                    continue
                eu = sub.groupby("year")["useful_heat_MWh"].sum() / 1e6
                data["eu_trajectory"][variant] = {
                    "year": eu.index.tolist(),
                    "q10": eu.round(1).tolist(),
                    "q50": eu.round(1).tolist(),
                    "q90": eu.round(1).tolist(),
                }

    # Per-country trajectories. mc_country_*.csv has 'variable',
    # 'useful_heat_TWh' (already TWh), tech='all'.
    for sc in scenarios:
        f = res / f"mc_country_{sc}.csv"
        df = _safe_read(f)
        if df.empty:
            continue
        sub = df[(df["variable"] == "useful_heat_TWh") & (df["tech"] == "all")].copy()
        for cc, gp in sub.groupby("country"):
            gpy = gp.sort_values("year")
            tr = {"year": gpy.year.tolist(),
                  "q10": gpy.q10.round(2).tolist(),
                  "q50": gpy.q50.round(2).tolist(),
                  "q90": gpy.q90.round(2).tolist()}
            data["country_trajectories"].setdefault(cc, {})[sc] = tr

    # COST_OPT per-country pathway (90% variant)
    if co_path.exists() and not co.empty and "variant" in co.columns:
        co90 = co[co.variant == "COST_OPT_90"]
        for cc, gp in co90.groupby("country"):
            agg = gp.groupby("year")["useful_heat_MWh"].sum() / 1e6
            data["country_trajectories"].setdefault(cc, {})["COST_OPT_90"] = {
                "year": agg.index.tolist(),
                "q10": agg.round(2).tolist(),
                "q50": agg.round(2).tolist(),
                "q90": agg.round(2).tolist(),
            }

    data["countries"] = sorted(data["country_trajectories"].keys())

    # 2050 bar chart per country per scenario (q50; useful_heat_TWh, tech=all)
    for sc in scenarios:
        f = res / f"mc_country_{sc}.csv"
        df = _safe_read(f)
        if df.empty:
            continue
        sub = df[(df["variable"] == "useful_heat_TWh") & (df["tech"] == "all") & (df["year"] == 2050)]
        bar = sub.groupby("country")["q50"].first()
        data["bar_2050"][sc] = {"countries": bar.index.tolist(),
                                "values": bar.round(2).tolist()}

    # LMDI backcast EU driver decomposition (from earlier lmdi_design results)
    lmdi_drv = res / "lmdi_design_drivers.csv"
    if lmdi_drv.exists():
        drv = pd.read_csv(lmdi_drv)
        # Per-country contributions; compute EU sums using lmdi_design.csv for
        # absolute TWh weights.
        des = pd.read_csv(res / "lmdi_design.csv")
        des_c = des[des.country != "EU"].set_index("country")
        drv_c = drv.set_index("country")
        import numpy as np
        m25 = des_c["model_2025_corrected"].values
        m15 = des_c["model_2015_corrected"].values
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where((m15 > 0) & (m25 > 0) & (np.abs(m25 - m15) > 1e-9),
                             m15 / m25, np.nan)
            L = np.where(np.isnan(ratio), m25, (m15 - m25) / np.log(ratio))
        labels = ["Population", "Occupancy (Dw/Pop)", "Dwelling size", "Design intensity"]
        cols = ["dlnQ_pop", "dlnQ_occupancy", "dlnQ_size", "dlnQ_intensity"]
        contribs = []
        for col in cols:
            v = (L * drv_c.loc[des_c.index, col].values).sum()
            # Convert to ΔQ from 2025->2015 sense -> flip sign so positive = pushes demand up over time
            contribs.append(round(-v, 1))
        data["lmdi_drivers_eu"] = {"labels": labels, "values": contribs,
                                    "totalTWh": round(des_c["model_2025_corrected"].sum() - des_c["model_2015_corrected"].sum(), 1)}

    # COST_OPT shadow prices (2050, all variants)
    sp_path = res / "cost_opt_shadow_prices.csv"
    if sp_path.exists():
        sp = pd.read_csv(sp_path)
        sp50 = sp[(sp.year == 2050) & (sp.shadow_eur_tco2 > 0.01)].copy()
        sp50 = sp50.sort_values(["variant", "shadow_eur_tco2"], ascending=[True, False])
        data["shadow_prices"] = sp50.to_dict(orient="records")

    # Headline tiles
    if "STATED_POLICIES" in data["eu_trajectory"]:
        eu_ref = data["eu_trajectory"]["STATED_POLICIES"]
        i25 = eu_ref["year"].index(2025) if 2025 in eu_ref["year"] else 0
        i50 = eu_ref["year"].index(2050) if 2050 in eu_ref["year"] else -1
        data["headline"]["eu_2025"] = eu_ref["q50"][i25]
        data["headline"]["ref_2050"] = eu_ref["q50"][i50]
        for sc in ["CURRENT_POLICIES", "NET_ZERO", "H2_PUSH"]:
            if sc in data["eu_trajectory"]:
                t = data["eu_trajectory"][sc]
                idx50 = t["year"].index(2050) if 2050 in t["year"] else -1
                data["headline"][f"{sc.lower()}_2050"] = t["q50"][idx50]
        if "COST_OPT_90" in data["eu_trajectory"]:
            t = data["eu_trajectory"]["COST_OPT_90"]
            idx50 = t["year"].index(2050) if 2050 in t["year"] else -1
            data["headline"]["costopt90_2050"] = t["q50"][idx50]

    # LMDI backcast gap (Model 2015 vs Hotmaps 2015 EU)
    if (res / "lmdi_design.csv").exists():
        des = pd.read_csv(res / "lmdi_design.csv")
        eu = des[des.country == "EU"]
        if not eu.empty:
            data["headline"]["backcast_gap_pct"] = float(eu.iloc[0]["gap_2015_vs_hotmaps_pct"])
            data["headline"]["hotmaps_2015"] = float(eu.iloc[0]["hotmaps_2015_TWh"])

    return data


def render_html(data: dict) -> str:
    """Render the dashboard HTML with embedded data + Plotly."""
    data_json = json.dumps(data)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LMDI Forward Dashboard - EU Hydrogen Buildings</title>
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
         max-width: 1280px; margin: 20px auto; padding: 0 20px; color: #222; }
  .header { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white; padding: 20px 25px; border-radius: 8px; margin-bottom: 20px; }
  .header h1 { margin: 0 0 8px 0; font-size: 24px; }
  .header p { margin: 0; opacity: 0.92; font-size: 14px; line-height: 1.5; }
  .tile-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
              gap: 12px; margin: 20px 0; }
  .tile { padding: 16px; background: #fafafa; border: 1px solid #e0e0e0;
          border-radius: 6px; }
  .tile .num { font-size: 26px; font-weight: 700; color: #2c3e50; }
  .tile .lbl { color: #666; font-size: 12px; text-transform: uppercase;
               letter-spacing: 0.5px; margin-top: 4px; }
  .section { margin: 30px 0; padding: 18px 22px; background: white;
             border: 1px solid #e8e8e8; border-radius: 6px;
             box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
  .section h2 { margin: 0 0 14px 0; font-size: 18px; color: #2c3e50;
                border-bottom: 2px solid #f0f0f0; padding-bottom: 8px; }
  .section .note { color: #666; font-size: 13px; margin: 0 0 10px 0; }
  select { font-size: 15px; padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; }
  .chart { width: 100%; height: 460px; }
  .footer { color: #888; font-size: 12px; text-align: center; margin: 30px 0; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; }
  th, td { padding: 6px 10px; border-bottom: 1px solid #eee; text-align: left; }
  th { background: #f5f5f5; font-size: 12px; text-transform: uppercase; letter-spacing: 0.3px; }
</style>
</head>
<body>

<div class="header">
  <h1>EU Hydrogen Buildings - LMDI Forward Dashboard</h1>
  <p>Per-country, multi-driver Logarithmic Mean Divisia Index projection of residential heat demand 2025 to 2050.
  Drivers: Population (Eurostat EUROPOP2023 + ONS + BFS) x Occupancy (Eurostat ilc_lvph01) x Dwelling size (held flat)
  x Design intensity (envelope renovation from JRC depth bands). Scenarios: STATED_POLICIES (frozen policy), NET_ZERO (Renovation Wave realised),
  H2_PUSH (intermediate), COST_OPT (LP).</p>
</div>

<div class="tile-row" id="tiles"></div>

<div class="section">
  <h2>EU aggregate trajectory 2025 to 2050</h2>
  <p class="note">Useful heat demand, TWh per year, EU 29-country sum. Shaded bands = 10th to 90th Monte Carlo percentile.</p>
  <div id="eu-traj" class="chart"></div>
</div>

<div class="section">
  <h2>Per-country trajectory</h2>
  <p class="note">Select a country to view its scenario trajectories.
  <label>Country: <select id="country-picker"></select></label></p>
  <div id="country-traj" class="chart"></div>
</div>

<div class="section">
  <h2>2050 useful demand by country and scenario</h2>
  <p class="note">Median Monte Carlo demand in 2050 per country (TWh). Sort by descending STATED_POLICIES demand.</p>
  <div id="bar-2050" class="chart"></div>
</div>

<div class="section">
  <h2>LMDI backcast driver decomposition (EU sum 2025 to 2015)</h2>
  <p class="note">Each bar = contribution of that driver to the (2025 - 2015) change in EU demand, TWh.
  Positive = driver pushed demand up over the decade.</p>
  <div id="lmdi-drivers" class="chart"></div>
</div>

<div class="section">
  <h2>COST_OPT 2050 shadow prices (binding countries)</h2>
  <p class="note">Implied carbon price per country at the -75 / -90 / -100 percent emissions cap (the only countries where the LP cap binds).</p>
  <div id="shadow-prices"></div>
</div>

<div class="footer">
  Generated by build_lmdi_dashboard.py. Repository:
  <a href="https://github.com/alajwadha/eu-hydrogen-buildings">github.com/alajwadha/eu-hydrogen-buildings</a>.
  Methodology: literature/temporal_backcast_methodology.md.
</div>

<script>
const DATA = __DATA_JSON__;

const COLORS = {
  CURRENT_POLICIES: "#7f7f7f",
  STATED_POLICIES: "#1f77b4",
  NET_ZERO: "#2ca02c",
  H2_PUSH: "#ff7f0e",
  COST_OPT_75: "#9467bd",
  COST_OPT_90: "#d62728",
  COST_OPT_100: "#8c564b",
};

// Headline tiles
function renderTiles() {
  const h = DATA.headline || {};
  const tiles = [
    ["EU 2025 demand", h.eu_2025, "TWh"],
    ["STATED_POLICIES 2050", h.ref_2050, "TWh"],
    ["CURRENT_POLICIES 2050", h.current_policies_2050, "TWh"],
    ["NET_ZERO 2050", h.net_zero_2050, "TWh"],
    ["H2_PUSH 2050", h.h2_push_2050, "TWh"],
    ["COST_OPT -90% 2050", h.costopt90_2050, "TWh"],
    ["Backcast 2015 gap vs Hotmaps", h.backcast_gap_pct, "%"],
  ];
  const el = document.getElementById("tiles");
  el.innerHTML = tiles.filter(t => t[1] !== undefined).map(t => {
    const v = (typeof t[1] === "number") ?
      (t[2] === "%" ? t[1].toFixed(1) : Math.round(t[1]).toLocaleString()) : "-";
    return `<div class="tile"><div class="num">${v} ${t[2]}</div><div class="lbl">${t[0]}</div></div>`;
  }).join("");
}

// EU aggregate trajectory chart
function renderEuTraj() {
  const traces = [];
  for (const [sc, t] of Object.entries(DATA.eu_trajectory || {})) {
    const color = COLORS[sc] || "#666";
    // Upper-lower fill for MC band
    if (t.q10.some((v, i) => v !== t.q90[i])) {
      traces.push({
        x: t.year.concat([...t.year].reverse()),
        y: t.q90.concat([...t.q10].reverse()),
        fill: "toself", fillcolor: color + "33", line: { color: "transparent" },
        name: sc + " range", legendgroup: sc, showlegend: false, hoverinfo: "skip",
      });
    }
    traces.push({
      x: t.year, y: t.q50, mode: "lines+markers", name: sc, legendgroup: sc,
      line: { color: color, width: 2 }, marker: { size: 6 },
    });
  }
  Plotly.newPlot("eu-traj", traces, {
    yaxis: { title: "Useful heat demand (TWh/yr)", rangemode: "tozero" },
    xaxis: { title: "Year" },
    hovermode: "x unified", margin: { t: 20 },
  }, { responsive: true });
}

// Per-country trajectory
function renderCountryTraj(cc) {
  const ct = DATA.country_trajectories[cc] || {};
  const traces = [];
  for (const [sc, t] of Object.entries(ct)) {
    const color = COLORS[sc] || "#666";
    if (t.q10.some((v, i) => v !== t.q90[i])) {
      traces.push({
        x: t.year.concat([...t.year].reverse()),
        y: t.q90.concat([...t.q10].reverse()),
        fill: "toself", fillcolor: color + "33", line: { color: "transparent" },
        name: sc + " range", legendgroup: sc, showlegend: false, hoverinfo: "skip",
      });
    }
    traces.push({
      x: t.year, y: t.q50, mode: "lines+markers", name: sc, legendgroup: sc,
      line: { color: color, width: 2 }, marker: { size: 6 },
    });
  }
  Plotly.newPlot("country-traj", traces, {
    yaxis: { title: cc + " useful heat demand (TWh/yr)", rangemode: "tozero" },
    xaxis: { title: "Year" },
    hovermode: "x unified", margin: { t: 20 },
  }, { responsive: true });
}

function setupCountryPicker() {
  const sel = document.getElementById("country-picker");
  for (const cc of DATA.countries || []) {
    const o = document.createElement("option"); o.value = cc; o.text = cc;
    sel.appendChild(o);
  }
  if (DATA.countries && DATA.countries.length) {
    const def = ["DE","FR","UK","IT","PL","ES"].find(c => DATA.countries.includes(c)) || DATA.countries[0];
    sel.value = def;
    renderCountryTraj(def);
    sel.addEventListener("change", () => renderCountryTraj(sel.value));
  }
}

// 2050 bar by country
function renderBar2050() {
  const bar = DATA.bar_2050 || {};
  const refCountries = bar.STATED_POLICIES ? bar.STATED_POLICIES.countries : [];
  const refValues = bar.STATED_POLICIES ? bar.STATED_POLICIES.values : [];
  const order = refCountries.map((c, i) => [c, refValues[i]]).sort((a,b) => b[1]-a[1]).map(x => x[0]);
  const traces = [];
  for (const sc of ["CURRENT_POLICIES","STATED_POLICIES","NET_ZERO","H2_PUSH"]) {
    if (!bar[sc]) continue;
    const lookup = Object.fromEntries(bar[sc].countries.map((c, i) => [c, bar[sc].values[i]]));
    traces.push({ x: order, y: order.map(c => lookup[c] || 0), type: "bar",
                  name: sc, marker: { color: COLORS[sc] } });
  }
  Plotly.newPlot("bar-2050", traces, {
    yaxis: { title: "2050 useful heat demand (TWh)" },
    xaxis: { title: "Country (sorted by STATED_POLICIES demand)" },
    barmode: "group", margin: { t: 20 },
  }, { responsive: true });
}

// LMDI driver decomposition
function renderLmdiDrivers() {
  const d = DATA.lmdi_drivers_eu || {};
  if (!d.labels) return;
  const colors = d.values.map(v => v >= 0 ? "#2ca02c" : "#d62728");
  Plotly.newPlot("lmdi-drivers", [{
    x: d.labels, y: d.values, type: "bar", marker: { color: colors },
    text: d.values.map(v => (v>=0?"+":"") + v.toFixed(1) + " TWh"), textposition: "outside",
  }], {
    yaxis: { title: "Contribution to (Q_2025 - Q_2015), TWh" },
    margin: { t: 20 }, annotations: [{
      x: 0.5, y: 1.05, xref: "paper", yref: "paper", showarrow: false,
      text: "Total Q_2025 - Q_2015 = " + (d.totalTWh >= 0 ? "+" : "") + d.totalTWh + " TWh",
      font: { size: 12, color: "#555" },
    }],
  }, { responsive: true });
}

// Shadow prices table
function renderShadowPrices() {
  const sp = DATA.shadow_prices || [];
  if (!sp.length) {
    document.getElementById("shadow-prices").innerHTML = "<p>No binding shadow prices.</p>";
    return;
  }
  let html = "<table><thead><tr><th>Variant</th><th>Country</th><th>Year</th><th>Implied EUR/tCO2</th></tr></thead><tbody>";
  for (const r of sp) {
    html += `<tr><td>${r.variant}</td><td>${r.country}</td><td>${r.year}</td><td>${r.shadow_eur_tco2.toFixed(2)}</td></tr>`;
  }
  html += "</tbody></table>";
  document.getElementById("shadow-prices").innerHTML = html;
}

renderTiles();
renderEuTraj();
setupCountryPicker();
renderBar2050();
renderLmdiDrivers();
renderShadowPrices();
</script>

</body>
</html>
"""
    return html.replace("__DATA_JSON__", data_json)


def main() -> None:
    data = build_data()
    html = render_html(data)
    out = ROOT / "dashboard" / "lmdi_dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"  countries: {len(data.get('countries', []))}")
    print(f"  scenarios in EU traj: {list(data.get('eu_trajectory', {}).keys())}")
    print(f"  shadow-price rows: {len(data.get('shadow_prices', []))}")
    h = data.get("headline", {})
    print(f"  headline: {h}")


if __name__ == "__main__":
    main()
