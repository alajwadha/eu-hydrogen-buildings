# Dashboard — D3 interactive country explorer

This folder holds the source of the public dashboard served at:

**https://alajwadha.github.io/eu-hydrogen-buildings/**

## Files

| File | Role |
|---|---|
| `index.html` | The dashboard UI (D3 + TopoJSON + IBM Plex fonts). |
| `data.js` | Per-country data payload (LCOH, tech shares, fuel prices, building stock). Auto-generated. |
| `.nojekyll` | Disables Jekyll processing so the dashboard renders unchanged. |

## How the dashboard is built and deployed

1. `code/scripts/generate_dashboard_data.py` reads `code/results/*.csv` and `code/src/Economics.py`, writes `dashboard/data.js`.
2. The root-level `index.html` and `data.js` and the `docs/` folder are kept in sync with this `dashboard/` folder. GitHub Pages can be configured to serve from any of the three; the live URL is currently served from the **repo root**. Until that changes, every push must keep all three copies in sync.
3. To regenerate after a model rerun:

```bash
python code/scripts/generate_dashboard_data.py     # writes dashboard/data.js
cp dashboard/data.js docs/data.js
cp dashboard/data.js data.js
cp dashboard/index.html docs/index.html
cp dashboard/index.html index.html
```

## Why three copies

Historical: the project moved between three GitHub Pages configurations (root, `/dashboard`, `/docs`) before settling on root. Keeping all three current is cheap insurance and lets us flip between configurations without losing the URL.

## Local preview

```bash
cd dashboard
python -m http.server 8000
# open http://localhost:8000
```
