"""Per-country comparison: corrected bottom-up snapshot vs NAKED EUBUCCO x TABULA.

Analytical undo of each documented correction (no Colab re-run required):
  - eubucco.area_correction: multiplicative on heated floor area -> undo by 1/area_correction.
  - comfort_regime.deflator: multiplicative on the SH intensity only (DHW unchanged)
    -> undo by 1/deflator on the SH portion.
  - Option B (tabula_reference_hdd): the climate_multiplier in the YAML was changed
    from hdd_country/hdd_proxy to hdd_country/tabula_reference_hdd. To undo, scale
    the SH portion by (hdd_country/hdd_proxy) / climate_multiplier.
  - tabula.class_mix_proxy (EE, LT): different TABULA sources per class with their
    own climate multipliers. Cannot be reversed analytically here; flagged
    APPROXIMATE (the other undos still apply, but the class-mix contribution is
    folded into the existing climate_multiplier handling, so the naked figure is
    a partial undo).

SH/DHW split (sh_share) is HDD-tiered: cold 0.88, temperate 0.85, warm 0.75,
very warm 0.50. These are the only approximations.

Output: code/results/compare_naked.csv + printed table.
For exact values, re-run 03_heat_intensity.py with a future --no-corrections
flag on Colab (work item).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))
import Config as C  # noqa: E402
from CountryConfig import load_country_config  # noqa: E402


def _national_twh(csv_path: Path) -> pd.Series:
    df = pd.read_csv(csv_path)
    return df.groupby("country")["heat_2015_MWh"].sum() / 1e6


def _sh_share(hdd: float) -> float:
    if hdd >= 3000:
        return 0.88
    if hdd >= 2000:
        return 0.85
    if hdd >= 1000:
        return 0.75
    return 0.50


def main() -> None:
    hot = _national_twh(C.PROCESSED_DIR / "building_stock_nuts3.csv")
    snap = _national_twh(C.PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")

    rows = []
    for cc in sorted(snap.index):
        try:
            cfg = load_country_config(cc)
        except Exception as e:
            continue
        area_corr = cfg.eubucco_area_correction or 1.0
        defl = cfg.comfort_regime_deflator or 1.0
        clim_cur = cfg.climate_multiplier
        hdd_c = cfg.hdd_country
        hdd_p = cfg.hdd_proxy
        clim_naked = hdd_c / hdd_p
        sh_share = _sh_share(hdd_c)

        sh_undo = (clim_naked / clim_cur) * (1.0 / defl)
        intensity_undo = sh_share * sh_undo + (1.0 - sh_share) * 1.0
        area_undo = 1.0 / area_corr
        undo_factor = area_undo * intensity_undo

        snapshot = float(snap[cc])
        naked = snapshot * undo_factor
        hotmaps = float(hot.get(cc, float("nan")))

        flags = []
        if abs(area_corr - 1.0) > 1e-6: flags.append("area")
        if abs(defl - 1.0) > 1e-6: flags.append("deflator")
        if abs(clim_naked - clim_cur) > 0.002: flags.append("optionB")
        if cfg.tabula_class_mix: flags.append("class_mix*")  # partial undo
        applied = "+".join(flags) if flags else "(none)"

        gap_corr = (snapshot - hotmaps) / hotmaps * 100 if hotmaps > 0 else float("nan")
        gap_naked = (naked - hotmaps) / hotmaps * 100 if hotmaps > 0 else float("nan")

        rows.append({
            "country": cc,
            "hotmaps_2015_TWh": round(hotmaps, 1),
            "snapshot_corrected_TWh": round(snapshot, 1),
            "snapshot_naked_TWh": round(naked, 1),
            "undo_factor": round(undo_factor, 3),
            "gap_corrected_pct": round(gap_corr, 1),
            "gap_naked_pct": round(gap_naked, 1),
            "corrections_applied": applied,
        })

    out = pd.DataFrame(rows)
    eu_mask = out["hotmaps_2015_TWh"].notna() & (out["hotmaps_2015_TWh"] > 0)
    h = out.loc[eu_mask, "hotmaps_2015_TWh"].sum()
    sc = out.loc[eu_mask, "snapshot_corrected_TWh"].sum()
    sn = out.loc[eu_mask, "snapshot_naked_TWh"].sum()
    out = pd.concat([out, pd.DataFrame([{
        "country": "EU(sum)",
        "hotmaps_2015_TWh": round(h, 1),
        "snapshot_corrected_TWh": round(sc, 1),
        "snapshot_naked_TWh": round(sn, 1),
        "undo_factor": round(sn / sc, 3) if sc else float("nan"),
        "gap_corrected_pct": round((sc - h) / h * 100, 1),
        "gap_naked_pct": round((sn - h) / h * 100, 1),
        "corrections_applied": "",
    }])], ignore_index=True)

    out_path = ROOT / "code" / "results" / "compare_naked.csv"
    out.to_csv(out_path, index=False)
    print(out.to_string(index=False))
    print(f"\nSaved {out_path}")
    print("* class_mix not analytically reversed (EE/LT) -- naked is approximate for those two.")


if __name__ == "__main__":
    main()
