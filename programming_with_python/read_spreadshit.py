# with open("inventory.xlsx") as f:
#     print(f.read())

# import openpyxl as o
# inv_file = o.load_workbook("inventory.xlsx")
# product_list = inv_file["sheet1"]

import pandas as pd
df = pd.read_excel("inventory.xlsx")
# total supplier products
supplier_Product_counts = df.groupby("Supplier")["Product No"].count()
print(supplier_Product_counts)

# total supplier inventory price
df["total_inv"] = df["Inventory"] * df["Price"]
total_supplier_price = df.groupby("Supplier")["total_inv"].sum()
print(total_supplier_price)

# products that have inventory < 10
products_less_than_ten_inv = df[df["Inventory"] < 10]
print(products_less_than_ten_inv)

# write and save spreadsheet
df.to_excel("inventory_output.xlsx", index=False)