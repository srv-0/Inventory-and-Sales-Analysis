# Business Problems & KPI Glossary
### Inventory & Sales Analysis — UrbanNest Retail Co. (fictional retail company)

This project turns the raw data + EDA + SQL findings into the 6 business problems and their answers, KPI glossary used consistently across Python, SQL, Excel, and Power BI.

---

## 1. Company & Data Snapshot

UrbanNest Retail Co. is a fictional mid size retailer selling 12 categories of consumer goods (Apparel, Electronics, Home & Kitchen, Grocery & Gourmet, Personal Care, Sports & Fitness, Toys & Games, Stationery & Office, Furniture, Beauty & Cosmetics, Pet Supplies, Automotive Accessories) across 8 stores/fulfillment hubs in India, through both online and offline store channels.

| Table | Rows | Grain |
|---|---|---|
| PRODUCTS | 2,600 | one row per SKU |
| CUSTOMERS | 4,200 | one row per customer |
| SALES | 10,040 | one row per transaction (24 months of history) |
| INVENTORY | 77,280 | one row per product × store × month (12 months) |
| STORES | 8 | one row per store |
| SALESPERSONS | 26 | one row per salesperson |

---

## 2. KPI Glossary 

| KPI | Formula | Why it matters |
|---|---|---|
| **Total Revenue** | `SUM(final_amount)` | Top-line sales performance |
| **Total Units Sold** | `SUM(quantity)` | Volume driver behind revenue |
| **Number of Orders** | `COUNT(DISTINCT sale_id)` | Transaction frequency |
| **Average Order Value (AOV)** | `Total Revenue / Number of Orders` | Basket size / spend per transaction |
| **Average Selling Price (ASP)** | `SUM(unit_price*quantity) / SUM(quantity)` | Pricing level, independent of discounting |
| **Total Discount** | `SUM(discount_amount)` | Cost of promotions/markdowns |
| **Gross Profit** | `SUM((unit_price - unit_cost)*quantity - discount_amount)` | Profit after cost of goods and discount |
| **Gross Margin %** | `Gross Profit / Total Revenue` | Profitability as a % of sales |
| **Inventory Value** | `SUM(closing_stock * unit_cost)` | Capital tied up in stock, at cost |
| **Average Inventory** | `AVG(closing_stock)` over the period | Baseline stock level for turnover calc |
| **Inventory Turnover** | `Units Sold (period) / Average Inventory (period)` | How efficiently stock converts to sales |
| **Stockout Rate** | `Out-of-Stock records / Total inventory records` | % of the time products aren't available to sell |
| **Overstock Rate** | `Overstock records / Total inventory records` | % of the time capital is sitting idle in excess stock |
| **Revenue Growth % (MoM)** | `(Revenue_month − Revenue_prev_month) / Revenue_prev_month` | Trend direction, momentum |
| **Category Contribution %** | `Category Revenue / Total Revenue` | Where the business actually makes its money |
| **Sales per Store** | `Store Revenue / Number of Stores (or per store directly)` | Store-level productivity comparison |

**Actual headline numbers from the generated dataset** (see `EDA_Report.md` for the full breakdown):

- Total Revenue: **₹3.13 Cr** across 24 months
- Total Units Sold: **27,922**
- Number of Orders: **10,034** (valid transactions)
- Average Order Value: **₹3,116**
- Gross Margin: **24.2%**
- Stockout Rate: **0.23%** | Overstock Rate: **16.5%**

# Monthly Revenue
![https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/01_monthly_revenue_trend.png](https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/01_monthly_revenue_trend.png)

# Revenue by Stores
![https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/03_revenue_by_store.png](https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/03_revenue_by_store.png)

# Revenue by Segment
![https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/04_revenue_by_segment.png](https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/04_revenue_by_segment.png)

# Sales channel distribution
![https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/09_sales_channel.png](https://github.com/srv-0/Inventory-and-Sales-Analysis/blob/main/charts/09_sales_channel.png)
