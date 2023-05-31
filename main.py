import pandas as pd

# ==============================================================================
# Functions
# ==============================================================================


def load_raw_materials(path_to_file):
    # Load CSV, raw data from wiki
    data = pd.read_csv(path_to_file, delimiter=" \t", engine="python")

    # Renaming for homogeneity
    data.rename(
        columns={
            "Chance 1": "Chance 1 (%)",
            "Chance 2": "Chance 2 (%)",
            "Upgrade": "Item",
        },
        inplace=True,
    )

    # Split location into campaign-level-variation
    data[["Campaign", "Level"]] = data["Location"].str.rsplit(" ", n=1, expand=True)
    data[["Campaign", "Variation"]] = data["Campaign"].str.rsplit(" ", n=1, expand=True)
    data["Variation"].fillna("Standard", inplace=True)

    # Remove items not available on maps (e.g. Azrael)
    data.drop(data.loc[data.Level.isnull()].index, inplace=True)

    data["Level"] = data["Level"].astype(int)  # Level is a number
    # Fixing Fall of Cadia name
    data.loc[data["Campaign"] == "Fall of", ["Campaign", "Variation"]] = [
        "Fall of Cadia",
        "Standard",
    ]

    # Get the overall drop rate
    data["Chance 2 (%)"].fillna(0, inplace=True)
    data["Drop rate (%)"] = data["Chance 1 (%)"] + data["Chance 2 (%)"]

    # Set the cost
    data["Cost"] = 6  # Standard cost
    data.loc[data["Variation"] == "Elite", "Cost"] = 10  # Elite
    # Cost for the start of Indomitus (cost 5)
    con = (
        (data["Campaign"] == "Indomitus")
        & (data["Variation"] == "Standard")
        & (data["Level"] <= 29)
    )
    data.loc[con, "Cost"] = 5

    # Average return per energy / Average energy cost for 1 unit
    data["Return per energy"] = data["Drop rate (%)"] / 100 / data["Cost"]
    data["Average energy cost"] = data["Cost"] * 100 / data["Drop rate (%)"]

    # Cleaning up
    data = data[
        [
            "Item",
            "Rarity",
            "Stat",
            "Campaign",
            "Variation",
            "Level",
            "Drop rate (%)",
            "Cost",
            "Average energy cost",
            "Return per energy",
        ]
    ]

    return data


def build_materials_df(path_to_file, df_raw):
    # Load from excel file
    df_mat = pd.read_excel(path_to_file, engine="openpyxl")
    # Homogeneize the columns
    df_mat.rename(columns={"Type": "Stat", "Crafted": "Craftable"}, inplace=True)
    # String to boolean
    df_mat["Craftable"].fillna(False, inplace=True)
    df_mat.loc[df_mat["Craftable"] == "Yes", "Craftable"] = True
    # Fill energy cost of basic items
    df_mat.loc[df_mat["Craftable"] == False, "Average energy cost"] = df_mat.loc[
        df_mat["Craftable"] == False, "Item"
    ].apply(get_average_cost_not_craftable, df_raw=df_raw)
    # Fill energy cost of crafted items
    df_mat.loc[df_mat["Craftable"] == True, "Average energy cost"] = df_mat.loc[
        df_mat["Craftable"] == True, "Item"
    ].apply(get_average_cost_craftable, df_mat=df_mat)
    return df_mat


def get_average_cost_not_craftable(item: str, df_raw) -> float:
    return df_raw.loc[df_raw.Item == item, "Average energy cost"].min()


def get_average_cost_subitem(item: str, df_mat) -> float:
    return df_mat.loc[df_mat.Item == item, "Average energy cost"].values[0]


def get_average_cost_craftable(item, df_mat):
    n = 1
    cost = 0
    subitem_name = df_mat.loc[df_mat.Item == item, "Item " + str(n)].values[0]
    subitem_qty = df_mat.loc[df_mat.Item == item, "Quantity " + str(n)].values[0]

    while (n < 3) and (type(subitem_name) == str):
        cost += get_average_cost_subitem(subitem_name, df_mat) * subitem_qty
        # print(n, subitem_name, cost)
        n += 1
        subitem_name = df_mat.loc[df_mat.Item == item, "Item " + str(n)].values[0]
        subitem_qty = df_mat.loc[df_mat.Item == item, "Quantity " + str(n)].values[0]

    return cost


# ==============================================================================
# Main
# ==============================================================================


def main():
    PATH_TO_RAW = "./data/raw_materials.csv"
    df_raw = load_raw_materials(PATH_TO_RAW)
    PATH_SAVE_RAW = "./data/raw_materials_cleaned.csv"
    df_raw.to_csv(PATH_SAVE_RAW)

    PATH_TO_CLEAN = "./data/materials.xlsx"
    df_mat = build_materials_df(PATH_TO_CLEAN, df_raw)
    PATH_SAVE_CLEAN = "./data/materials_cleaned.csv"
    df_mat.to_csv(PATH_SAVE_CLEAN)


if __name__ == "__main__":
    main()
