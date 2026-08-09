"""
aggregate_heat_demand_by_region.py
====================================
Builds per-NUTS-level heat demand tables from the model's NUTS3 building
stock data. Writes:
  - code/data/processed/heat_demand_by_region/heat_demand_NUTS{1,2,3}_all.csv
  - code/data/processed/heat_demand_by_region/{ISO2}.csv (per-country)
  - countries/{Country-Name}/data/heat_demand_regions.csv (per-country copy)

Usage:
    python code/scripts/aggregate_heat_demand_by_region.py

Source: code/data/processed/building_stock_nuts3.csv (Hotmaps 2015 baseline)
Names:  code/data/raw/gisco/NUTS_RG_01M_2021_4326_clean.csv (GISCO 2021)
"""

import pandas as pd
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_BS = REPO_ROOT / "code/data/processed/building_stock_nuts3.csv"
SRC_GISCO = REPO_ROOT / "code/data/raw/gisco/NUTS_RG_01M_2021_4326_clean.csv"
OUT_CENTRAL = REPO_ROOT / "code/data/processed/heat_demand_by_region"
COUNTRIES_DIR = REPO_ROOT / "countries"


COUNTRY_FOLDER = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland",
    "CY": "Cyprus", "CZ": "Czech-Republic", "DE": "Germany", "DK": "Denmark",
    "EE": "Estonia", "ES": "Spain", "FI": "Finland", "FR": "France",
    "GR": "Greece", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland",
    "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "MT": "Malta", "NL": "Netherlands", "PL": "Poland", "PT": "Portugal",
    "RO": "Romania", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "UK": "United-Kingdom",
}


MANUAL_NAMES_2024 = {
    "FRB": "Centre — Val de Loire", "FRC": "Bourgogne-Franche-Comté",
    "FRD": "Normandie", "FRE": "Hauts-de-France", "FRF": "Grand Est",
    "FRG": "Pays de la Loire", "FRH": "Bretagne", "FRI": "Nouvelle-Aquitaine",
    "FRJ": "Occitanie", "FRK": "Auvergne-Rhône-Alpes",
    "FRL": "Provence-Alpes-Côte d'Azur", "FRM": "Corse",
    "FRY": "Régions Ultrapériphériques Françaises",
    "FRB0": "Centre — Val de Loire", "FRC1": "Bourgogne", "FRC2": "Franche-Comté",
    "FRD1": "Basse-Normandie", "FRD2": "Haute-Normandie",
    "FRE1": "Nord-Pas-de-Calais", "FRE2": "Picardie", "FRF1": "Alsace",
    "FRF2": "Champagne-Ardenne", "FRF3": "Lorraine", "FRG0": "Pays de la Loire",
    "FRH0": "Bretagne", "FRI1": "Aquitaine", "FRI2": "Limousin",
    "FRI3": "Poitou-Charentes", "FRJ1": "Languedoc-Roussillon",
    "FRJ2": "Midi-Pyrénées", "FRK1": "Auvergne", "FRK2": "Rhône-Alpes",
    "FRL0": "Provence-Alpes-Côte d'Azur", "FRM0": "Corse",
    "FR71": "Rhône-Alpes", "FR82": "Provence-Alpes-Côte d'Azur",
    "FR10": "Île-de-France",
}


def main():
    bs = pd.read_csv(SRC_BS)
    gisco = pd.read_csv(SRC_GISCO)

    name_lookup = dict(
        zip(gisco.NUTS_ID, gisco.NUTS_NAME.fillna(gisco.NAME_LATN))
    )

    # dwellings_2021 in the Hotmaps benchmark file is a SHARE BASIS, not a dwelling count:
    # for the EU it carries the raw census OBS_VALUE and for the UK an arbitrary share
    # placeholder, and BuildingStock only ever divides it to get dwellings_share per NUTS3.
    # Summed across the file it comes to 1.1 bn, some 3.6x the real ~300M, so this column is
    # named for what it is and must not be read as a count. The bottom-up stock
    # (building_stock_nuts3_bottomup.csv) is the file that carries real dwelling estimates,
    # and it is what the infrastructure bill and the connection charge both use.
    n3 = bs.groupby(["country", "nuts_id"], as_index=False).agg(
        dwelling_share_basis=("dwellings_2021", "sum"),
        heat_MWh=("heat_2015_MWh", "sum"),
    )
    n3["heat_TWh"] = n3["heat_MWh"] / 1e6
    n3["nuts_level"] = 3
    n3["nuts_name"] = n3["nuts_id"].map(name_lookup)
    n3["nuts2"] = n3["nuts_id"].str[:4]
    n3["nuts1"] = n3["nuts_id"].str[:3]

    n2 = n3.groupby(["country", "nuts2"], as_index=False).agg(
        dwelling_share_basis=("dwelling_share_basis", "sum"),
        heat_MWh=("heat_MWh", "sum"),
    )
    n2["heat_TWh"] = n2["heat_MWh"] / 1e6
    n2["nuts_level"] = 2
    n2 = n2.rename(columns={"nuts2": "nuts_id"})
    n2["nuts_name"] = n2["nuts_id"].map(name_lookup)

    n1 = n3.groupby(["country", "nuts1"], as_index=False).agg(
        dwelling_share_basis=("dwelling_share_basis", "sum"),
        heat_MWh=("heat_MWh", "sum"),
    )
    n1["heat_TWh"] = n1["heat_MWh"] / 1e6
    n1["nuts_level"] = 1
    n1 = n1.rename(columns={"nuts1": "nuts_id"})
    n1["nuts_name"] = n1["nuts_id"].map(name_lookup)

    for df in (n1, n2, n3):
        df.loc[df.country == "EL", "country"] = "GR"
        for nuts_id, name in MANUAL_NAMES_2024.items():
            mask = (df.nuts_id == nuts_id) & df.nuts_name.isna()
            df.loc[mask, "nuts_name"] = name
        # remove zero-demand extra-regio rows
        mask_extra = (df.heat_TWh == 0) & df.nuts_id.str.endswith("Z")
        df.drop(df.index[mask_extra], inplace=True)
        # fallback for any unresolved names
        df.loc[df.nuts_name.isna(), "nuts_name"] = df.loc[
            df.nuts_name.isna(), "nuts_id"
        ]

    cols = ["nuts_id", "nuts_name", "nuts_level", "country",
            "dwelling_share_basis", "heat_MWh", "heat_TWh"]

    OUT_CENTRAL.mkdir(parents=True, exist_ok=True)

    # Cross-country files
    for level_df, fname in [(n1, "heat_demand_NUTS1_all.csv"),
                            (n2, "heat_demand_NUTS2_all.csv"),
                            (n3, "heat_demand_NUTS3_all.csv")]:
        level_df[cols].sort_values(["country", "nuts_id"]).to_csv(
            OUT_CENTRAL / fname, index=False
        )

    # Per-country files
    for iso, folder in COUNTRY_FOLDER.items():
        sub = pd.concat([n1[n1.country == iso],
                         n2[n2.country == iso],
                         n3[n3.country == iso]])[cols]
        sub = sub.sort_values(["nuts_level", "nuts_id"])
        sub.to_csv(OUT_CENTRAL / f"{iso}.csv", index=False)

        folder_data = COUNTRIES_DIR / folder / "data"
        if folder_data.exists():
            sub.to_csv(folder_data / "heat_demand_regions.csv", index=False)

    print(f"Wrote NUTS1 ({len(n1)} regions), "
          f"NUTS2 ({len(n2)}), NUTS3 ({len(n3)})")
    print(f"Total heat demand: {n1.heat_TWh.sum():.0f} TWh "
          f"(should equal NUTS2 sum = NUTS3 sum)")


if __name__ == "__main__":
    main()
