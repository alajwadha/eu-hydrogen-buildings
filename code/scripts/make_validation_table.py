"""Full 29-country bottom-up validation table (tab:bottomup companion to P03).

Builds the at-a-glance per-country validation table that sits beside the P03
validation figure: EUBUCCO building count, bottom-up residential useful heat,
the Hotmaps 2015 benchmark, the raw (snapshot vs Hotmaps) deviation and the
vintage-matched (backcast-to-2015 vs Hotmaps) deviation, for all 29 countries,
ordered by raw deviation, with an EU aggregate row.

Single source of truth, so every column ties out to figure P03:
  - bottom-up TWh, Hotmaps TWh and the raw deviation are read straight from
    results/benchmark_multi.csv, which is exactly what P03 plots, so the table's
    raw-deviation column reproduces P03(b) row for row (19 of 29 within +/-15 %,
    28 of 29 within +/-25 %, EU aggregate -0.8 %);
  - the vintage-matched deviation is recomputed here on the SAME Hotmaps base as
    the raw column, using each country's historical backcast factor from
    results/reconcile_backcast.csv (Config.backcast_factor, the factor that
    rolls the 2025 stock snapshot back to 2015). Recomputing on the common base
    keeps the two deviation columns directly comparable: their difference is the
    pure vintage effect and nothing else;
  - the EUBUCCO building count is the per-country sum of n_buildings in
    data/processed/building_stock_nuts3_bottomup.csv (the same stock that drives
    the bottom-up demand), so the three illustrative counts already in the paper
    (Luxembourg 186,171; France 52,610,604; Finland 6,633,364) reproduce exactly.

Outputs (both regenerated, never hand-edited):
  - results/bottomup_validation.csv : the full machine-readable companion table
    that the figure and table captions promise as supplementary material;
  - paper/sections/_tab_bottomup.tex : the LaTeX table body \\input by
    methodology.tex.

Run:  cd code && PYTHONUTF8=1 PYTHONPATH=. python -m scripts.make_validation_table
"""
from __future__ import annotations

import pandas as pd

from src.Config import RESULTS_DIR, PROCESSED_DIR, ROOT_DIR

# Eurostat ISO-2 (as used in the result CSVs) -> country name used across the paper.
COUNTRY_NAME = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
    "CY": "Cyprus", "CZ": "Czech Republic", "DE": "Germany", "DK": "Denmark",
    "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
    "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
    "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "MT": "Malta", "NL": "Netherlands", "PL": "Poland", "PT": "Portugal",
    "RO": "Romania", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "UK": "United Kingdom",
}


def _signed(x: float) -> str:
    """siunitx-friendly signed percentage with explicit + and one decimal."""
    return f"{x:+.1f}"


def build() -> pd.DataFrame:
    bm = pd.read_csv(RESULTS_DIR / "benchmark_multi.csv")
    rc = pd.read_csv(RESULTS_DIR / "reconcile_backcast.csv")
    rc = rc[rc["country"] != "EU(sum)"][["country", "backcast_factor_2015"]]

    stock = pd.read_csv(PROCESSED_DIR / "building_stock_nuts3_bottomup.csv")
    nb = (stock.groupby("country")["n_buildings"].sum()
          .astype("int64").rename("n_buildings").reset_index())

    df = (bm.merge(rc, on="country", how="left")
            .merge(nb, on="country", how="left"))

    # Vintage-matched 2015 demand and gap, on the SAME (benchmark_multi) Hotmaps base.
    df["back15_TWh"] = (df["bottomup_TWh"] * df["backcast_factor_2015"]).round(1)
    df["vintage_matched_gap_pct"] = (
        (df["back15_TWh"] - df["hotmaps_TWh"]) / df["hotmaps_TWh"] * 100.0
    ).round(1)
    df = df.rename(columns={"gap_vs_hotmaps_pct": "raw_gap_pct"})
    df["country_name"] = df["country"].map(COUNTRY_NAME)

    df = df.sort_values("raw_gap_pct").reset_index(drop=True)
    return df[["country", "country_name", "n_buildings", "bottomup_TWh",
               "hotmaps_TWh", "back15_TWh", "raw_gap_pct",
               "vintage_matched_gap_pct", "backcast_factor_2015"]]


def error_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Dispersion of the country-level validation error, on both benchmark bases.

    The paper reported the validation as two counts (19 of 29 within 15 per cent, 28
    within 25) and one aggregate (-0.8 per cent). Counts discard the size of a miss, and
    the aggregate hides it, because the country errors carry both signs and cancel: the
    aggregate is a twelfth of the typical country error. A referee asked for the standard
    dispersion statistics, which is the right question, and they are derived here rather
    than typed into the prose.

    Four statistics, because they fail differently. MAPE is the unweighted mean, so a
    small country counts as much as Germany. Weighted MAPE weights by benchmark demand,
    which is the right basis for a claim about the study area's total heat. RMSE is
    sensitive to the tail, so it separates a few large misses from many small ones.
    The median absolute error ignores the tail entirely. Reporting one alone would let a
    reader draw the wrong picture of the same 29 numbers.

    Both bases are returned because the two are not interchangeable and have been mixed
    up before: the counts and the -0.8 per cent aggregate the paper quotes are on the raw
    2025 snapshot, while the backcast-to-2015 column is a different comparison. Quoting a
    vintage-matched MAPE next to a raw count would be a scope error of exactly the kind
    this table already had to fix once.
    """
    import numpy as np
    rows = []
    for basis, err_col, est_col in (("raw", "raw_gap_pct", "bottomup_TWh"),
                                    ("vintage_matched", "vintage_matched_gap_pct",
                                     "back15_TWh")):
        e = df[err_col].astype(float)
        ae = e.abs()
        rows.append({
            "basis": basis,
            "n_countries": int(len(df)),
            # Unweighted mean of the per-country absolute percentage error.
            "mape_pct": round(float(ae.mean()), 2),
            # Demand-weighted: total absolute deviation over total benchmark demand,
            # which is the aggregate statistic with the signs left in place.
            "weighted_mape_pct": round(
                float((df[est_col] - df.hotmaps_TWh).abs().sum()
                      / df.hotmaps_TWh.sum() * 100.0), 2),
            "rmse_pct": round(float(np.sqrt((e ** 2).mean())), 2),
            "median_abs_err_pct": round(float(ae.median()), 2),
            "max_abs_err_pct": round(float(ae.max()), 2),
            "max_abs_err_country": str(df.loc[ae.idxmax(), "country"]),
            # The signed aggregate the paper already quotes, recomputed here so the
            # dispersion statistics and the aggregate come from one place.
            "signed_aggregate_pct": round(
                float((df[est_col].sum() / df.hotmaps_TWh.sum() - 1) * 100.0), 2),
        })
    return pd.DataFrame(rows)


def eu_row(df: pd.DataFrame) -> dict:
    bu = df["bottomup_TWh"].sum()
    hm = df["hotmaps_TWh"].sum()
    bk = df["back15_TWh"].sum()
    return {
        "n_buildings": int(df["n_buildings"].sum()),
        "bottomup_TWh": round(bu, 1),
        "hotmaps_TWh": round(hm, 1),
        "back15_TWh": round(bk, 1),
        "raw_gap_pct": round((bu - hm) / hm * 100.0, 1),
        "vintage_matched_gap_pct": round((bk - hm) / hm * 100.0, 1),
    }


def write_latex(df: pd.DataFrame, eu: dict, path) -> None:
    lines: list[str] = []
    ap = lines.append
    ap("% Auto-generated by code/scripts/make_validation_table.py -- do not edit by hand.")
    ap("% Regenerate: cd code && PYTHONUTF8=1 PYTHONPATH=. python -m scripts.make_validation_table")
    ap(r"\begin{table}[H]")
    ap(r"\centering")
    ap(r"\footnotesize")
    ap(r"\setlength{\tabcolsep}{2pt}")   # 5pt ran the table past the text block
    ap(r"\caption{Bottom-up heat demand vs Hotmaps 2015, all 29 countries.}")
    ap(r"\label{tab:bottomup}")
    ap(r"\begin{tabularx}{\textwidth}{@{}X r S[table-format=4.1] "
       r"S[table-format=4.1] S[table-format=+3.1] S[table-format=+3.1]@{}}")
    ap(r"\toprule")
    ap(r"Country & {EUBUCCO} & {Bottom-up} & {Hotmaps 2015} & {Raw} & "
       r"{Vintage-matched} \\")
    ap(r" & {buildings} & {(TWh\,yr$^{-1}$)} & {(TWh\,yr$^{-1}$)} & "
       r"{deviation (\%)} & {deviation (\%)} \\")
    ap(r"\midrule")
    for _, r in df.iterrows():
        ap(f"{r.country_name} & {int(r.n_buildings):,} & "
           f"{r.bottomup_TWh:.1f} & {r.hotmaps_TWh:.1f} & "
           f"{_signed(r.raw_gap_pct)} & {_signed(r.vintage_matched_gap_pct)} \\\\"
           .replace(",", "{,}"))
    ap(r"\midrule")
    ap(f"\\textbf{{EU+UK+CH}} & {eu['n_buildings']:,} & "
       f"{eu['bottomup_TWh']:.1f} & {eu['hotmaps_TWh']:.1f} & "
       f"{_signed(eu['raw_gap_pct'])} & {_signed(eu['vintage_matched_gap_pct'])} \\\\"
       .replace(",", "{,}"))
    ap(r"\bottomrule")
    ap(r"\end{tabularx}")
    ap(r"\smallskip")
    ap(r"\raggedright\small")
    ap(r"Bottom-up estimates from EUBUCCO v0.2 building footprints and TABULA "
       r"per-vintage intensities; reported as-is, without calibration. Hotmaps "
       r"figures are the all-class NUTS3 totals for 2015. A positive deviation "
       r"means the bottom-up build is above the benchmark. Of the 29 countries, "
       r"19 fall within $\pm$15\,\% and 28 within $\pm$25\,\% on the raw "
       r"deviation (only Malta, the smallest stock, exceeds the band), and the "
       r"EU+UK+CH aggregate deviates by $-0.8$\,\%; the vintage-matched column "
       r"shifts each country down by the 2015 to 2025 demand trend and is reported "
       r"so the comparison is vintage-consistent. Three illustrative rows "
       r"(Luxembourg, France, Finland) are discussed in the text.")
    ap(r"\\[2pt]{\footnotesize\textit{Source: Authors' contribution.}}")
    ap(r"\end{table}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = build()
    eu = eu_row(df)

    # Machine-readable companion (the file the captions promise).
    out_csv = df.copy()
    # The CSV was 29 country rows with no aggregate, so the two headline figures the paper
    # quotes from it (-0.8 per cent raw, -8.3 per cent vintage-matched) could only be
    # recovered by summing three columns, and a reader could not tell that the +/-15 and
    # +/-25 counts quoted beside them are on the RAW column while the aggregate quoted is
    # the vintage-matched one. Both bases' aggregates and counts are appended.
    agg = {c: "" for c in out_csv.columns}
    agg.update({
        "country": "EU", "country_name": "EU-27+UK+CH aggregate",
        "n_buildings": int(df.n_buildings.sum()),
        "bottomup_TWh": round(df.bottomup_TWh.sum(), 1),
        "hotmaps_TWh": round(df.hotmaps_TWh.sum(), 1),
        "back15_TWh": round(df.back15_TWh.sum(), 1),
        "raw_gap_pct": round((df.bottomup_TWh.sum() / df.hotmaps_TWh.sum() - 1) * 100, 2),
        "vintage_matched_gap_pct": round((df.back15_TWh.sum() / df.hotmaps_TWh.sum() - 1) * 100, 2),
        "backcast_factor_2015": round(df.back15_TWh.sum() / df.bottomup_TWh.sum(), 4),
    })
    out_csv = pd.concat([out_csv, pd.DataFrame([agg])], ignore_index=True)
    out_csv.to_csv(RESULTS_DIR / "bottomup_validation.csv", index=False)

    met = error_metrics(df)
    met.to_csv(RESULTS_DIR / "bottomup_validation_metrics.csv", index=False)

    tex_path = ROOT_DIR / "paper" / "sections" / "_tab_bottomup.tex"
    write_latex(df, eu, tex_path)

    # Console verification block.
    raw = df["raw_gap_pct"]
    vm = df["vintage_matched_gap_pct"]
    print("Full 29-country bottom-up validation table")
    print(df.to_string(index=False))
    print(f"\nEU+UK+CH aggregate: {eu}")
    print(f"\nRaw deviation:            within +/-15% {int((raw.abs() <= 15).sum())}/29, "
          f"within +/-25% {int((raw.abs() <= 25).sum())}/29, "
          f"outside: {sorted(df.loc[raw.abs() > 25, 'country'])}")
    print(f"Vintage-matched deviation: within +/-15% {int((vm.abs() <= 15).sum())}/29, "
          f"within +/-25% {int((vm.abs() <= 25).sum())}/29, "
          f"outside: {sorted(df.loc[vm.abs() > 25, 'country'])}")
    print("\nCountry-level error dispersion (the statistics the prose quotes)")
    print(met.to_string(index=False))

    print(f"\nWrote {RESULTS_DIR / 'bottomup_validation.csv'}")
    print(f"Wrote {RESULTS_DIR / 'bottomup_validation_metrics.csv'}")
    print(f"Wrote {tex_path}")


if __name__ == "__main__":
    main()
