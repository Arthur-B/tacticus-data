import pandas as pd
from io import StringIO
import sys

# ==============================================================================
# Functions
# ==============================================================================


def df2wikitable(df):
    # Format Header
    print('{| class="article-table sortable"')
    for col in df.columns:
        print(f"! {col}")
    print("|-")
    # Print the rows
    for _, row in df.iterrows():
        for val in row.values:
            print(f"| {val}")
        print("|-")
    # Close
    print("|}")


def print_wiki_post(item, df_raw):
    # Save location
    filepath = "./items/" + item.replace(" ", "_").lower() + ".txt"
    # Select the data
    df = df_raw.loc[
        df_raw["Item"] == item,
        [
            "Campaign",
            "Variation",
            "Level",
            "Drop rate (%)",
            "Cost",
            "Average energy cost",
            "Return per energy",
        ],
    ]
    # Get the table content
    save_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    df2wikitable(df)
    sys.stdout = save_stdout
    # Other data
    rarity = df_raw.loc[df_raw["Item"] == item, "Rarity"].values[0]
    stat = df_raw.loc[df_raw["Item"] == item, "Stat"].values[0]
    # Make the file
    with open(filepath, "w") as f:
        f.write(f"==={rarity} {stat} upgrade (dropped)===\n\n")
        f.write("==Locations==\n\n")
        f.write(result.getvalue())


# ==============================================================================
# Main
# ==============================================================================


def main():
    PATH_RAW_MAT = "./data/raw_materials_cleaned.csv"
    df_raw = pd.read_csv(PATH_RAW_MAT, index_col=0)

    for item in df_raw["Item"].unique():
        print_wiki_post(item, df_raw)


if __name__ == "__main__":
    main()
