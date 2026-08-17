import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import json, os

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.titleweight": "bold",
                      "axes.edgecolor": "#444", "figure.facecolor": "white"})
CHART_DIR = "/home/claude/project/charts"
os.makedirs(CHART_DIR, exist_ok=True)

sales_analysis = pd.read_pickle("/home/claude/project/data/sales_analysis_clean.pkl")
products_clean = pd.read_pickle("/home/claude/project/data/products_clean.pkl")
customers_clean = pd.read_pickle("/home/claude/project/data/customers_clean.pkl")
stores = pd.read_pickle("/home/claude/project/data/final_stores.pkl")
inventory = pd.read_pickle("/home/claude/project/data/final_inventory.pkl")

sales_m = sales_analysis.merge(products_clean, on="product_id", how="left") \
                         .merge(stores, on="store_id", how="left") \
                         .merge(customers_clean, on="customer_id", how="left", suffixes=("","_cust"))
sales_m["sale_date"] = pd.to_datetime(sales_m["sale_date"])
sales_m["month"] = sales_m["sale_date"].values.astype("datetime64[M]")
sales_m["gross_profit"] = (sales_m["unit_price"] - sales_m["unit_cost"]) * sales_m["quantity"] - sales_m["discount_amount"]

def money_fmt(ax, axis="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L" if abs(x) >= 1e5 else f"₹{x:,.0f}")
    (ax.yaxis if axis=="y" else ax.xaxis).set_major_formatter(fmt)

COLOR = "#1F4E78"
ACCENT = "#E8963C"

# 1. Monthly revenue trend
monthly = sales_m.groupby("month")["final_amount"].sum().sort_index()
fig, ax = plt.subplots(figsize=(8,4))
ax.plot(monthly.index, monthly.values, color=COLOR, marker="o", markersize=3)
ax.fill_between(monthly.index, monthly.values, color=COLOR, alpha=0.08)
ax.set_title("Monthly Revenue Trend (24 months)")
money_fmt(ax)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/01_monthly_revenue_trend.png"); plt.close()

# 2. Revenue by category
cat_rev = sales_m.groupby("category")["final_amount"].sum().sort_values()
fig, ax = plt.subplots(figsize=(7,5))
ax.barh(cat_rev.index, cat_rev.values, color=COLOR)
ax.set_title("Revenue by Category")
money_fmt(ax, axis="x")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_revenue_by_category.png"); plt.close()

# 3. Revenue by store/region
store_rev = sales_m.groupby("store_name")["final_amount"].sum().sort_values()
fig, ax = plt.subplots(figsize=(7,4.5))
ax.barh(store_rev.index, store_rev.values, color=ACCENT)
ax.set_title("Revenue by Store")
money_fmt(ax, axis="x")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/03_revenue_by_store.png"); plt.close()

# 4. Revenue by customer segment
seg_rev = sales_m.groupby("customer_segment")["final_amount"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(5,4))
ax.pie(seg_rev.values, labels=seg_rev.index, autopct="%1.0f%%",
       colors=["#1F4E78","#4C86B0","#B9D3E8"], startangle=90)
ax.set_title("Revenue Share by Customer Segment")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_revenue_by_segment.png"); plt.close()

# 5. Discount distribution
fig, ax = plt.subplots(figsize=(7,4))
ax.hist(sales_m["discount_pct"]*100, bins=40, color=COLOR, edgecolor="white")
ax.set_title("Discount % Distribution (per transaction)")
ax.set_xlabel("Discount %"); ax.set_ylabel("Number of Transactions")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_discount_distribution.png"); plt.close()

# 6. Revenue distribution (order value)
fig, ax = plt.subplots(figsize=(7,4))
ax.hist(sales_m["final_amount"], bins=50, color=ACCENT, edgecolor="white")
ax.set_title("Order Value Distribution")
ax.set_xlabel("Final Amount (₹)"); ax.set_ylabel("Number of Orders")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/06_order_value_distribution.png"); plt.close()

# 7. Stock status distribution
stock_status = inventory["stock_status"].value_counts()
fig, ax = plt.subplots(figsize=(5.5,4))
colors_map = {"Healthy":"#2E7D32","Low Stock":"#F9A825","Overstock":"#1565C0","Out of Stock":"#C62828"}
ax.bar(stock_status.index, stock_status.values, color=[colors_map.get(s,"#888") for s in stock_status.index])
ax.set_title("Inventory Stock Status Distribution (all monthly snapshots)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/07_stock_status_distribution.png"); plt.close()

# 8. Top 10 products by revenue
prod_rev = sales_m.groupby("product_name")["final_amount"].sum().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(8,5))
ax.barh(prod_rev.index[::-1], prod_rev.values[::-1], color=COLOR)
ax.set_title("Top 10 Products by Revenue")
money_fmt(ax, axis="x")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/08_top10_products_revenue.png"); plt.close()

# 9. Sales channel performance
chan = sales_m.groupby("sales_channel")["final_amount"].sum()
fig, ax = plt.subplots(figsize=(5,4))
ax.bar(chan.index, chan.values, color=[COLOR, ACCENT])
ax.set_title("Revenue by Sales Channel")
money_fmt(ax)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/09_sales_channel.png"); plt.close()

# 10. Monthly units sold
monthly_units = sales_m.groupby("month")["quantity"].sum().sort_index()
fig, ax = plt.subplots(figsize=(8,4))
ax.bar(monthly_units.index, monthly_units.values, color=COLOR, width=20)
ax.set_title("Monthly Units Sold")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/10_monthly_units_sold.png"); plt.close()

# 11. Inventory value by category (latest month)
inv_m = inventory.merge(products_clean, on="product_id", how="left")
latest_month = inventory["stock_date"].max()
inv_latest = inv_m[inv_m["stock_date"] == latest_month].copy()
inv_latest["inventory_value"] = inv_latest["closing_stock"] * inv_latest["unit_cost"]
inv_val_cat = inv_latest.groupby("category")["inventory_value"].sum().sort_values()
fig, ax = plt.subplots(figsize=(7,5))
ax.barh(inv_val_cat.index, inv_val_cat.values, color=ACCENT)
ax.set_title("Inventory Value by Category (latest snapshot)")
money_fmt(ax, axis="x")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/11_inventory_value_by_category.png"); plt.close()

# 12. Discount % vs Revenue by category (scatter-ish bar combo)
disc_rev = sales_m.groupby("category").agg(avg_discount=("discount_pct","mean"), revenue=("final_amount","sum"))
fig, ax1 = plt.subplots(figsize=(8,4.5))
order = disc_rev.sort_values("revenue", ascending=False).index
ax1.bar(order, disc_rev.loc[order,"revenue"], color=COLOR, alpha=0.85, label="Revenue")
money_fmt(ax1)
ax2 = ax1.twinx()
ax2.plot(order, disc_rev.loc[order,"avg_discount"]*100, color="#C62828", marker="o", label="Avg Discount %")
ax2.set_ylabel("Avg Discount %")
ax1.set_title("Revenue vs Average Discount % by Category")
plt.xticks(rotation=45, ha="right")
fig.legend(loc="upper right", bbox_to_anchor=(0.9,0.9))
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/12_discount_vs_revenue.png"); plt.close()

print("Charts saved to", CHART_DIR)
print(os.listdir(CHART_DIR))
