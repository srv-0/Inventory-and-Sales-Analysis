"""
Inventory & Sales Analysis - Retail Business
Python / Pandas EDA
=====================================================
Loads the raw Excel workbook, profiles it, cleans it,
and produces the charts + summary stats used in the
EDA report and in the final business insights.

NOTE: Update RAW_PATH / output paths below to match your
local folder structure before running (paths here reflect
the original project working directory).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os, json

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.titleweight": "bold"})
CHART_DIR = "/home/claude/project/charts"
os.makedirs(CHART_DIR, exist_ok=True)

RAW_PATH = "Inventory & Sales Data.xlsx"


# 1. LOAD
xl = pd.ExcelFile(RAW_PATH)
products = xl.parse("PRODUCTS")
customers = xl.parse("CUSTOMERS")
sales = xl.parse("SALES")
inventory = xl.parse("INVENTORY")
stores = xl.parse("STORES")
salespersons = xl.parse("SALESPERSONS")

report = {}

# 2. DATASET OVERVIEW / SHAPE / DTYPES
shapes = {name: df.shape for name, df in
          [("PRODUCTS", products), ("CUSTOMERS", customers), ("SALES", sales),
           ("INVENTORY", inventory), ("STORES", stores), ("SALESPERSONS", salespersons)]}
report["shapes"] = {k: list(v) for k, v in shapes.items()}


# 3. MISSING VALUE ANALYSIS (before cleaning)
missing = {}
for name, df in [("PRODUCTS", products), ("CUSTOMERS", customers), ("SALES", sales),
                  ("INVENTORY", inventory), ("STORES", stores), ("SALESPERSONS", salespersons)]:
    m = df.isna().sum()
    missing[name] = {c: int(v) for c, v in m[m > 0].items()}
report["missing_before_cleaning"] = missing


# 4. DUPLICATE ANALYSIS
exact_dupe_sales = int(sales.duplicated().sum())
# near-duplicate: same customer, product, store, date, quantity but different sale_id
near_dupe_mask = sales.duplicated(subset=["sale_date","product_id","customer_id","store_id","quantity"], keep=False)
near_dupe_count = int(near_dupe_mask.sum())
report["duplicates"] = {"exact_duplicate_rows": exact_dupe_sales,
                         "near_duplicate_rows_flagged": near_dupe_count}


# 5. REFERENTIAL INTEGRITY CHECKS
integrity = {}
integrity["sales_product_id_orphans"] = int((~sales["product_id"].isin(products["product_id"])).sum())
integrity["sales_customer_id_orphans"] = int((~sales["customer_id"].isin(customers["customer_id"])).sum())
integrity["sales_store_id_orphans"] = int((~sales["store_id"].isin(stores["store_id"])).sum())
integrity["sales_salesperson_id_orphans"] = int((~sales["salesperson_id"].isin(salespersons["salesperson_id"])).sum())
integrity["inventory_product_id_orphans"] = int((~inventory["product_id"].isin(products["product_id"])).sum())
integrity["inventory_store_id_orphans"] = int((~inventory["store_id"].isin(stores["store_id"])).sum())
integrity["salespersons_store_id_orphans"] = int((~salespersons["store_id"].isin(stores["store_id"])).sum())
report["referential_integrity"] = integrity

# 6. DATA CLEANING
sales_clean = sales.copy()
products_clean = products.copy()
customers_clean = customers.copy()

# 6a. Standardize category text (strip + title case) -> fixes casing/whitespace inconsistencies
products_clean["category"] = products_clean["category"].astype(str).str.strip().str.title()
# collapse the same category spelled with different casing into canonical form seen most often
canon_map = (products_clean["category"].value_counts().index.tolist())
# (title-casing already unifies MEN'S -> Men'S issues from apostrophes; fix known categories explicitly)
CANONICAL_CATEGORIES = ["Apparel","Electronics","Home & Kitchen","Grocery & Gourmet","Personal Care",
                         "Sports & Fitness","Toys & Games","Stationery & Office","Furniture",
                         "Beauty & Cosmetics","Pet Supplies","Automotive Accessories"]
def fix_category(c):
    for canon in CANONICAL_CATEGORIES:
        if c.strip().lower() == canon.lower():
            return canon
    return c
products_clean["category"] = products_clean["category"].apply(fix_category)

# 6b. Remove exact duplicate rows in SALES
before = len(sales_clean)
sales_clean = sales_clean.drop_duplicates()
exact_removed = before - len(sales_clean)

# 6c. Flag (not silently drop) near-duplicate sales for analyst review
sales_clean["is_potential_duplicate"] = sales_clean.duplicated(
    subset=["sale_date","product_id","customer_id","store_id","quantity"], keep=False)

# 6d. Recompute a validation column: does final_amount match quantity*unit_price - discount?
expected_final = (sales_clean["quantity"] * sales_clean["unit_price"] - sales_clean["discount_amount"]).round(2)
sales_clean["amount_mismatch_flag"] = (expected_final - sales_clean["final_amount"]).abs() > 0.01
mismatch_count = int(sales_clean["amount_mismatch_flag"].sum())

# 6e. Outlier flags (unit_price, quantity) via IQR method, flagged not deleted
def iqr_flags(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
    return (s < lower) | (s > upper)

sales_clean["price_outlier_flag"] = iqr_flags(sales_clean["unit_price"])
sales_clean["quantity_outlier_flag"] = iqr_flags(sales_clean["quantity"])
sales_clean["discount_pct"] = np.where(
    (sales_clean["quantity"]*sales_clean["unit_price"]) > 0,
    sales_clean["discount_amount"] / (sales_clean["quantity"]*sales_clean["unit_price"]), 0)
sales_clean["unusual_discount_flag"] = sales_clean["discount_pct"] > 0.55

# 6f. Zero-quantity rows are invalid transactions -> excluded from revenue analysis (but reported)
zero_qty_rows = int((sales_clean["quantity"] == 0).sum())
sales_analysis = sales_clean[sales_clean["quantity"] > 0].copy()

# 6g. Fill missing categorical values with explicit "Unknown" bucket (BA-friendly, auditable)
for col in ["city", "acquisition_channel"]:
    customers_clean[col] = customers_clean[col].fillna("Unknown")
for col in ["supplier_id", "brand"]:
    products_clean[col] = products_clean[col].fillna("Unknown")
sales_analysis["payment_method"] = sales_analysis["payment_method"].fillna("Unknown")

cleaning_summary = {
    "exact_duplicate_rows_removed": exact_removed,
    "near_duplicate_rows_flagged_for_review": int(sales_clean["is_potential_duplicate"].sum()),
    "amount_formula_mismatches_flagged": mismatch_count,
    "price_outliers_flagged": int(sales_clean["price_outlier_flag"].sum()),
    "quantity_outliers_flagged": int(sales_clean["quantity_outlier_flag"].sum()),
    "unusual_discounts_flagged (>55%)": int(sales_clean["unusual_discount_flag"].sum()),
    "zero_quantity_rows_excluded_from_revenue_analysis": zero_qty_rows,
    "category_labels_standardized": True,
    "missing_categoricals_filled_as_Unknown": True,
}
report["cleaning_summary"] = cleaning_summary

sales_analysis.to_pickle("/home/claude/project/data/sales_analysis_clean.pkl")
products_clean.to_pickle("/home/claude/project/data/products_clean.pkl")
customers_clean.to_pickle("/home/claude/project/data/customers_clean.pkl")


# 7. DESCRIPTIVE STATS

desc = sales_analysis[["quantity","unit_price","discount_amount","final_amount"]].describe().round(2)
report["sales_descriptive_stats"] = desc.to_dict()


# 8. MERGE FOR ANALYSIS

sales_m = sales_analysis.merge(products_clean, on="product_id", how="left") \
                         .merge(stores, on="store_id", how="left", suffixes=("","_store")) \
                         .merge(customers_clean, on="customer_id", how="left", suffixes=("","_cust"))
sales_m["sale_date"] = pd.to_datetime(sales_m["sale_date"])
sales_m["month"] = sales_m["sale_date"].values.astype("datetime64[M]")
sales_m["gross_profit"] = (sales_m["unit_price"] - sales_m["unit_cost"]) * sales_m["quantity"] - sales_m["discount_amount"]

# KPIs -------------------------------------------------
total_revenue = sales_m["final_amount"].sum()
total_units = sales_m["quantity"].sum()
n_orders = sales_m["sale_id"].nunique()
aov = total_revenue / n_orders
total_discount = sales_m["discount_amount"].sum()
gross_profit = sales_m["gross_profit"].sum()
gross_margin_pct = gross_profit / total_revenue

kpis = {
    "Total Revenue": round(total_revenue, 2),
    "Total Units Sold": int(total_units),
    "Number of Orders": int(n_orders),
    "Average Order Value": round(aov, 2),
    "Total Discount": round(total_discount, 2),
    "Gross Profit": round(gross_profit, 2),
    "Gross Margin %": round(gross_margin_pct * 100, 2),
}
report["headline_kpis"] = kpis


# 9-13. CATEGORY / STORE / SEGMENT / DISCOUNT ANALYSIS
cat_rev = sales_m.groupby("category")["final_amount"].sum().sort_values(ascending=False)
store_rev = sales_m.groupby("store_name")["final_amount"].sum().sort_values(ascending=False)
segment_rev = sales_m.groupby("customer_segment")["final_amount"].sum().sort_values(ascending=False)
disc_by_cat = sales_m.groupby("category")["discount_pct"].mean().sort_values(ascending=False)

report["revenue_by_category"] = cat_rev.round(2).to_dict()
report["revenue_by_store"] = store_rev.round(2).to_dict()
report["revenue_by_segment"] = segment_rev.round(2).to_dict()
report["avg_discount_pct_by_category"] = (disc_by_cat*100).round(2).to_dict()


# 14-15. MONTHLY TRENDS + MoM GROWTH
monthly = sales_m.groupby("month")["final_amount"].sum().sort_index()
mom_growth = monthly.pct_change() * 100
report["monthly_revenue"] = {str(k.date()): round(v,2) for k,v in monthly.items()}
report["mom_growth_pct"] = {str(k.date()): (round(v,2) if pd.notna(v) else None) for k,v in mom_growth.items()}


# 16-20. INVENTORY ANALYSIS
inv_m = inventory.merge(products_clean, on="product_id", how="left")
stock_status_counts = inv_m["stock_status"].value_counts()
report["stock_status_distribution"] = stock_status_counts.to_dict()

# latest month snapshot per product-store for turnover / value calcs
latest_month = inventory["stock_date"].max()
inv_latest = inv_m[inv_m["stock_date"] == latest_month].copy()
inv_latest["inventory_value"] = inv_latest["closing_stock"] * inv_latest["unit_cost"]

inv_value_by_cat = inv_latest.groupby("category")["inventory_value"].sum().sort_values(ascending=False)
report["inventory_value_by_category_latest_month"] = inv_value_by_cat.round(2).to_dict()

# inventory turnover (annualized) per product = total units sold (12mo) / avg inventory
sold_12mo = inventory.groupby("product_id")["sold_quantity"].sum()
avg_inv = inventory.groupby("product_id")["closing_stock"].mean()
turnover = (sold_12mo / avg_inv.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
report["overall_inventory_turnover_ratio"] = round(float(sold_12mo.sum() / avg_inv.sum()), 2)

stockout_rate = (stock_status_counts.get("Out of Stock", 0) / stock_status_counts.sum()) * 100
overstock_rate = (stock_status_counts.get("Overstock", 0) / stock_status_counts.sum()) * 100
report["stockout_rate_pct"] = round(stockout_rate, 2)
report["overstock_rate_pct"] = round(overstock_rate, 2)

# slow-moving inventory: bottom turnover products with meaningful stock
prod_turnover_df = pd.DataFrame({"product_id": turnover.index, "turnover": turnover.values}).merge(
    products_clean[["product_id","product_name","category","unit_cost"]], on="product_id", how="left")
prod_turnover_df = prod_turnover_df.merge(avg_inv.rename("avg_inventory"), on="product_id")
slow_movers = prod_turnover_df[(prod_turnover_df["avg_inventory"] > 20)].sort_values("turnover").head(15)
report["top15_slow_moving_products"] = slow_movers[["product_id","product_name","category","turnover","avg_inventory"]].round(2).to_dict("records")

# PRODUCT PROFITABILITY
# Exclude the small number of rows where unit_price is a data-entry outlier (>2x the product's
# catalogue selling_price) so a handful of corrupted rows don't distort the margin ranking --
# this is exactly the kind of check a BA would run before trusting a profitability report.
sales_m_margin = sales_m.merge(products_clean[["product_id","selling_price"]].rename(
    columns={"selling_price":"_catalogue_price"}), on="product_id", how="left")
clean_for_margin = sales_m_margin[sales_m_margin["unit_price"] <= 2 * sales_m_margin["_catalogue_price"]]
price_outliers_excluded_from_margin = len(sales_m_margin) - len(clean_for_margin)

prod_profit = clean_for_margin.groupby(["product_id","product_name","category"]).agg(
    revenue=("final_amount","sum"), units=("quantity","sum"), gross_profit=("gross_profit","sum")
).reset_index()
prod_profit["margin_pct"] = (prod_profit["gross_profit"] / prod_profit["revenue"] * 100).round(2)
top_revenue_products = prod_profit.sort_values("revenue", ascending=False).head(15)
top_margin_products = prod_profit[prod_profit["revenue"] > prod_profit["revenue"].median()].sort_values("margin_pct", ascending=False).head(15)
report["top15_revenue_products"] = top_revenue_products.round(2).to_dict("records")
report["top15_margin_products_above_median_revenue"] = top_margin_products.round(2).to_dict("records")
report["price_outlier_rows_excluded_from_margin_analysis"] = int(price_outliers_excluded_from_margin)

with open("/home/claude/project/data/eda_report.json", "w") as f:
    json.dump(report, f, indent=2, default=str)

print("EDA numeric report saved.")
print(json.dumps(kpis, indent=2))
