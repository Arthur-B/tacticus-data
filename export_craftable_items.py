import pandas as pd
from bigtree import Node, levelorder_iter, print_tree, yield_tree
from io import StringIO
import sys


# ==============================================================================
# Functions
# ==============================================================================


def make_root(item, df):
    row = df.loc[df.Item == item]
    root = Node(
        row["Item"].values[0],
        craftable=row["Craftable"].values[0],
        quantity=1,
        quantity_tot=1,
    )
    return root


def add_children(parent, df):
    row = df.loc[df.Item == parent.name]
    for n in range(1, 4):
        subitem = row["Item " + str(n)].values[0]
        if bool(subitem) and (type(subitem) != float):  # Sub-item + ugly check for nan
            child = Node(
                subitem,
                craftable=df.loc[df["Item"] == subitem, "Craftable"].values[0],
                quantity=int(row["Quantity " + str(n)].values[0]),
                quantity_tot=int(
                    row["Quantity " + str(n)].values[0] * parent.quantity_tot
                ),
                parent=parent,
            )


def print_tree_to_file(item, df):
    # Save location
    filepath = "./items/" + item.replace(" ", "_").lower() + ".txt"
    # Get other data
    rarity = df.loc[df["Item"] == item, "Rarity"].values[0]
    stat = df.loc[df["Item"] == item, "Stat"].values[0]
    # Build the tree
    root = make_root(item, df)
    for node in levelorder_iter(root):
        add_children(node, df)
    # Write the file
    with open(filepath, "w") as f:
        f.write(f"==={rarity} {stat} upgrade (crafted)===\n\n")
        f.write("==Required items==\n\n")
        for node in root.children:
            f.write(f"* [[{node.name}]] x{node.quantity}\n")
        if root.max_depth > 2:  # If need more sub-items, print whole recipe
            f.write("\n==Complete recipe==\n\n")
            # Get the data (print_tree goes straight to ouput)
            save_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            for branch, stem, node in yield_tree(root, style="const"):
                print(
                    f' {branch}{stem}{"[[" + node.node_name + "]]"} (per item: {int(node.quantity)} | tot: {int(node.quantity_tot)})'
                )
            sys.stdout = save_stdout
            f.write(result.getvalue())


# ==============================================================================
# Main
# ==============================================================================


def main():
    PATH_MAT = "./data/materials_cleaned.csv"
    df = pd.read_csv(PATH_MAT, index_col=0)
    # Print trees for craftable items
    df.loc[df["Craftable"] == True, "Item"].apply(print_tree_to_file, df=df)


if __name__ == "__main__":
    main()
