# Business Problems & KPI Glossary
### Inventory & Sales Analysis — UrbanNest Retail Co. (fictional retail company)

This document turns the raw data + EDA + SQL findings into the 6 business
problems the project is built to answer, plus a simple, interview-defensible
KPI glossary used consistently across Python, SQL, Excel, and Power BI.

---

## 1. Company & Data Snapshot

UrbanNest Retail Co. is a fictional mid-sized retailer selling 12 categories
of consumer goods (Apparel, Electronics, Home & Kitchen, Grocery & Gourmet,
Personal Care, Sports & Fitness, Toys & Games, Stationery & Office,
Furniture, Beauty & Cosmetics, Pet Supplies, Automotive Accessories) across
8 stores/fulfillment hubs in India, through both online and in-store channels.

| Table | Rows | Grain |
|---|---|---|
| PRODUCTS | 2,600 | one row per SKU |
| CUSTOMERS | 4,200 | one row per customer |
| SALES | 10,040 | one row per transaction (24 months of history) |
| INVENTORY | 77,280 | one row per product × store × month (12 months) |
| STORES | 8 | one row per store |
| SALESPERSONS | 26 | one row per salesperson |

---

## 2. KPI Glossary (kept simple and interview-defensible)

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

**Actual headline numbers from the generated dataset** (see `EDA_Report.md`
for the full breakdown):

- Total Revenue: **₹3.13 Cr** across 24 months
- Total Units Sold: **27,922**
- Number of Orders: **10,034** (valid transactions)
- Average Order Value: **₹3,116**
- Gross Margin: **24.2%**
- Stockout Rate: **0.23%** | Overstock Rate: **16.5%**

---

## 3. The Six Business Problems

For each problem: business question → relevant data → KPI(s) → analysis
approach → finding (from the actual dataset) → business implication →
recommended action.

### Problem 1 — Which products/categories should receive more inventory?
- **Data:** SALES (demand/velocity), INVENTORY (stockout_months), PRODUCTS
- **KPI:** Stockout Rate, Stockout Months per product, Units Sold
- **Approach:** SQL Q11 (frequent stockouts) joined against SQL Q5 (top sellers by volume) to find high-demand products that are *also* chronically out of stock.
- **Finding:** A small cluster of fast-moving ("Star") products stock out in 8+ of the last 12–36 tracked months despite strong, consistent demand — supply isn't keeping pace with sell-through.
- **Business implication:** Every stockout month on a fast mover is lost revenue that likely shifted to a competitor or was simply not captured.
- **Recommended action:** Raise the reorder level and tighten the replenishment cycle specifically for these SKUs; consider a dedicated fast-mover replenishment lane instead of the standard cycle.

### Problem 2 — Which products are slow-moving or overstocked?
- **Data:** INVENTORY (turnover, overstock_months), SALES (units sold)
- **KPI:** Inventory Turnover, Overstock Rate, Inventory Value
- **Approach:** SQL Q19 (slow-moving inventory) ranks products by turnover ratio; SQL Q10 cross-checks low-sales-high-inventory combinations.
- **Finding:** Overstock accounts for **16.5%** of all monthly inventory snapshots — concentrated in "Slow"/"Dead" velocity products that were over-procured up front and rarely sell through.
- **Business implication:** Capital is tied up in inventory that isn't converting to revenue, and it carries holding-cost and obsolescence risk.
- **Recommended action:** Run a clearance/discount cycle on the worst-turnover SKUs; reduce future purchase order quantities for these categories/suppliers.

### Problem 3 — Which products frequently become out of stock?
- **Data:** INVENTORY (stock_status history)
- **KPI:** Stockout Rate, Stockout Months
- **Approach:** SQL Q11, cross-referenced with product category and store to see if stockouts cluster anywhere.
- **Finding:** Stockouts are rare overall (0.23% of records) but not evenly spread — a handful of specific SKUs account for a disproportionate share of stockout months.
- **Business implication:** This is a supply-chain/procurement-cadence problem for specific SKUs, not a system-wide inventory shortage.
- **Recommended action:** Set SKU-specific safety stock and reorder points instead of a one-size-fits-all reorder rule.

### Problem 4 — Which categories/stores generate the strongest sales performance?
- **Data:** SALES, STORES, PRODUCTS
- **KPI:** Revenue by Category, Revenue by Store, Category Contribution %
- **Approach:** SQL Q4, Q6, Q15 (category %, store revenue, ranked contribution).
- **Finding:** **Furniture** and **Sports & Fitness** are the two largest revenue categories despite lower unit volumes (high average selling price); **Mumbai Flagship** is the top-performing store, roughly 2.5x the lowest-performing store (Pune).
- **Business implication:** Revenue is concentrated — a small number of categories and stores disproportionately drive the topline.
- **Recommended action:** Protect and grow the top categories/stores (inventory priority, staffing, marketing spend); investigate underperforming stores for local demand, staffing, or assortment issues.

### Problem 5 — How are discounts affecting revenue and profitability?
- **Data:** SALES (discount_amount, final_amount)
- **KPI:** Average Discount % by Category, Gross Margin %, Revenue
- **Approach:** SQL Q8 (avg discount by category) plotted against category revenue (see `12_discount_vs_revenue.png`).
- **Finding:** Discount rates are fairly uniform across categories (~18–20% average), and higher discounting doesn't correspond to proportionally higher revenue — categories with similar discount levels show very different revenue outcomes, meaning discount level alone isn't what's driving sales.
- **Business implication:** Blanket discounting isn't an efficient revenue lever here; other factors (demand, price tier, assortment) matter more.
- **Recommended action:** Move from uniform, calendar-driven discounting toward targeted discounting on genuinely slow-moving stock, and protect margin on already-fast-moving products that don't need a discount to sell.

### Problem 6 — Which customer segments and products should receive greater attention?
- **Data:** SALES, CUSTOMERS, PRODUCTS
- **KPI:** Revenue by Segment, Revenue by Product, Margin % by Product
- **Approach:** SQL Q7 (segment contribution), Q9 (margin leaders), Q16 (top products per category).
- **Finding:** The **Regular** segment contributes the largest share of revenue (~57%) simply due to volume, while **Premium** customers contribute disproportionately per-customer (higher AOV) despite being a smaller group.
- **Business implication:** Regular customers are the revenue base to protect; Premium customers are the highest-value segment to grow via retention/loyalty programs.
- **Recommended action:** Build a lightweight loyalty/retention offer for Premium customers, and keep the core value proposition strong for the Regular segment since it's the volume engine.

---

## 4. Analysis Approach (how these were actually derived)

1. **Python/Pandas** — cleaned the raw workbook (deduped, standardized category labels, flagged outliers/mismatches, verified referential integrity), then computed KPIs, trends, and distributions (`eda_analysis.py`, `EDA_Report.md`).
2. **SQL** — 20 business questions run against a normalized relational model, validated for correctness before being finalized (`SQL_Business_Analysis.sql`).
3. **Excel** — a formula-driven KPI/pivot layer for quick, no-code reporting (`Excel_Analysis` sheet inside the raw workbook).
4. **Power BI** — a 3-page dashboard spec + DAX measures to make the above interactive for stakeholders (`PowerBI_Dashboard_Guide_and_DAX.md`).

All findings above are pulled directly from the generated dataset — nothing here was written before running the analysis.
