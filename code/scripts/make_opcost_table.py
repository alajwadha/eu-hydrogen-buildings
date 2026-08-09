"""EU-mean peaker operating cost (short-run marginal cost, EUR/MWh-e: fuel plus carbon,
no capital) for the gas peaker and the hydrogen turbine, by scenario and year. Emits a LaTeX
table to paper/sections/_tab_opcost.tex.

Run: cd code && PYTHONPATH=. python -m scripts.make_opcost_table
"""
import pandas as pd
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
e = pd.read_csv(REPO / "code" / "results" / "power_peaker_economics.csv")
YEARS = [2025, 2030, 2040, 2050]
SC = [("CURRENT_POLICIES", "Current Policies"), ("STATED_POLICIES", "Stated Policies"),
      ("NET_ZERO", "Net Zero"), ("H2_PUSH", "H2 Push")]

rows = [r"\begin{table}[htbp]", r"\centering", r"\footnotesize",
        r"\caption{Mean peaker operating cost across the EU-27, the United Kingdom and "
        r"Switzerland (short-run marginal cost, EUR/MWh-e: fuel and "
        r"carbon only, no capital), by scenario and year. Hydrogen's cost falls as delivered "
        r"hydrogen cheapens and the turbine improves; the carbon-priced gas peaker rises with the "
        r"carbon path (about 70 to 350 EUR/tCO$_2$ in the two high-carbon scenarios). The two cross "
        r"only late and only under H2 Push (221 versus 239 in 2050 on this MEAN basis; on "
        r"the median the same year is a tie at 238 against 239, and the AE submission "
        r"reports the median because this distribution is bimodal and the mean is dragged "
        r"by the salt-cavern tail, so the sign of the crossing depends on which statistic "
        r"is quoted); in the lower-carbon "
        r"scenarios gas stays cheaper throughout. The EU-27+UK+CH mean understates the salt-cavern "
        r"markets, where the hydrogen cost is far lower (Figure~\ref{fig:crossover}).}",
        r"\label{tab:opcost}", r"\begin{tabular}{llrrrr}", r"\toprule",
        r"Scenario & Peaker & 2025 & 2030 & 2040 & 2050 \\", r"\midrule"]
for sc, lab in SC:
    d = e[e.scenario == sc].groupby("year").agg(H2=("h2_var_eur_mwh", "mean"),
                                                Gas=("gas_var_eur_mwh", "mean"))
    gas = " & ".join(str(int(round(d.Gas[y]))) for y in YEARS)
    h2 = " & ".join(str(int(round(d.H2[y]))) for y in YEARS)
    rows.append(f"{lab} & Gas & {gas} " + r"\\")
    rows.append(r"& H$_2$ & " + h2 + r" \\")
    rows.append(r"\addlinespace")
rows += [r"\bottomrule", r"\end{tabular}",
         r"\\[2pt]{\footnotesize\textit{Source: Authors' contribution.}}",
         r"\end{table}", ""]
(REPO / "paper" / "sections" / "_tab_opcost.tex").write_text("\n".join(rows), encoding="utf8")
print("wrote paper/sections/_tab_opcost.tex")
