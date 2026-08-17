# Power BI Dashboard Guide & DAX Measures
### Inventory & Sales Analysis — UrbanNest Retail Co.

This is a build-guide for a 3-page Power BI dashboard on top of the
`Inventory_Sales_Analysis_RawData.xlsx` workbook (or the SQL tables in
`SQL_Business_Analysis.sql`, if you connect Power BI directly to a database
instead of the Excel file). It covers the data model, every DAX measure,
and what goes on each page — written so you can rebuild it in Power BI
Desktop and also explain the choices in an interview.

---

## 1. Data Model

Import all 6 tables (PRODUCTS, CUSTOMERS, SALES, INVENTORY, STORES,
SALESPERSONS). Set up a **star-schema-style model**:

```
                 PRODUCTS
                     |
        STORES -- SALES -- CUSTOMERS
           |          |
     SALESPERSONS   (also referenced by)
                     INVENTORY -- PRODUCTS
                          |
                        STORES
```

**Relationships to create (all 1-to-many, single direction, from dimension → fact):**

| From | To | Key |
|---|---|---|
| PRODUCTS[product_id] | SALES[product_id] | 1:* |
| CUSTOMERS[customer_id] | SALES[customer_id] | 1:* |
| STORES[store_id] | SALES[store_id] | 1:* |
| SALESPERSONS[salesperson_id] | SALES[salesperson_id] | 1:* |
| PRODUCTS[product_id] | INVENTORY[product_id] | 1:* |
| STORES[store_id] | INVENTORY[store_id] | 1:* |

Add a **Date table** (Power Query → New Table, or `CALENDAR()` DAX) spanning
the min/max of `SALES[sale_date]` and `INVENTORY[stock_date]`, mark it as
the official Date table, and relate it to both `SALES[sale_date]` and
`INVENTORY[stock_date]` (the inventory relationship can stay inactive and
be invoked with `USERELATIONSHIP` where needed, since sale_date is the
primary time axis for most visuals).

```dax
DateTable =
CALENDAR ( DATE(2024,8,1), DATE(2026,8,1) )
```

---

## 2. DAX Measures

Create these in a dedicated **_Measures** table (Modeling → New Table →
`_Measures = {}`) so they're easy to find.

```dax
Total Revenue = SUM ( SALES[final_amount] )

Total Orders = DISTINCTCOUNT ( SALES[sale_id] )

Total Units = SUM ( SALES[quantity] )

Average Order Value = DIVIDE ( [Total Revenue], [Total Orders] )

Total Discount = SUM ( SALES[discount_amount] )

Gross Profit =
SUMX (
    SALES,
    ( SALES[unit_price] - RELATED ( PRODUCTS[unit_cost] ) ) * SALES[quantity]
        - SALES[discount_amount]
)

Gross Margin % = DIVIDE ( [Gross Profit], [Total Revenue] )

Inventory Value =
SUMX ( INVENTORY, INVENTORY[closing_stock] * RELATED ( PRODUCTS[unit_cost] ) )

Average Inventory = AVERAGE ( INVENTORY[closing_stock] )

Units Sold (Inventory Tracked) = SUM ( INVENTORY[sold_quantity] )

Inventory Turnover =
DIVIDE ( [Units Sold (Inventory Tracked)], [Average Inventory] )

Stockout Rate =
DIVIDE (
    CALCULATE ( COUNTROWS ( INVENTORY ), INVENTORY[stock_status] = "Out of Stock" ),
    COUNTROWS ( INVENTORY )
)

Overstock Rate =
DIVIDE (
    CALCULATE ( COUNTROWS ( INVENTORY ), INVENTORY[stock_status] = "Overstock" ),
    COUNTROWS ( INVENTORY )
)

Revenue Growth % (MoM) =
VAR CurrentRevenue = [Total Revenue]
VAR PriorRevenue =
    CALCULATE ( [Total Revenue], DATEADD ( 'DateTable'[Date], -1, MONTH ) )
RETURN
    DIVIDE ( CurrentRevenue - PriorRevenue, PriorRevenue )

Category Contribution % =
DIVIDE ( [Total Revenue], CALCULATE ( [Total Revenue], ALL ( PRODUCTS[category] ) ) )

Cumulative Revenue =
CALCULATE (
    [Total Revenue],
    FILTER ( ALLSELECTED ( 'DateTable' ), 'DateTable'[Date] <= MAX ( 'DateTable'[Date] ) )
)
```

Every measure maps to a KPI already defined in `Business_Problems_and_KPIs.md`
— keep that mapping consistent so numbers match across Excel/SQL/Power BI
in an interview.

---

## 3. Page 1 — Executive Sales Overview

**KPI cards (top row):** Total Revenue · Total Orders · Total Units ·
Average Order Value · Gross Profit · Gross Margin %

**Visuals:**
- Line chart: `DateTable[Date]` (month) → `[Total Revenue]` (Monthly Revenue Trend)
- Column chart: `DateTable[Date]` (month) → `[Total Units]` (Monthly Units Sold)
- Bar chart: `PRODUCTS[category]` → `[Total Revenue]` (Revenue by Category)
- Bar/Map: `STORES[region]` / `STORES[store_name]` → `[Total Revenue]` (Revenue by Store/Region)
- Donut chart: `CUSTOMERS[customer_segment]` → `[Total Revenue]` (Revenue by Customer Segment)

**Slicers:** Date (month/year), Category, Brand, Region, Store, Customer Segment, Sales Channel

---

## 4. Page 2 — Inventory Analysis

**KPI cards:** Inventory Value · Average Inventory · Inventory Turnover ·
Stockout Rate · Overstock Rate

**Visuals:**
- Bar chart: `PRODUCTS[category]` → `[Inventory Value]`
- Donut/Pie: `INVENTORY[stock_status]` → count (Stock Status Distribution)
- Bar chart (Top N filter): `PRODUCTS[product_name]` → `[Average Inventory]`, filtered to `stock_status = "Overstock"` (Top Overstocked Products)
- Bar chart (Top N filter): filtered to `stock_status IN {"Low Stock","Out of Stock"}` (Low-stock Products)
- Bar chart: `PRODUCTS[category]` → `[Inventory Turnover]`
- Bar chart: `STORES[store_name]` → `[Inventory Value]`

**Table** — columns: Product, Category, Avg Closing Stock, Monthly Sales
(`[Units Sold (Inventory Tracked)]`), Inventory Value, Stock Status,
Inventory Turnover.

---

## 5. Page 3 — Product & Customer Analysis

**Visuals:**
- Bar chart (Top N): `PRODUCTS[product_name]` → `[Total Revenue]`
- Bar chart (Top N): `PRODUCTS[product_name]` → `[Total Units]`
- Bar chart: `PRODUCTS[category]` → `[Gross Margin %]` (Category Profitability)
- Donut: `CUSTOMERS[customer_segment]` → `[Total Revenue]`
- Bar chart: `CUSTOMERS[customer_age_group]` → `[Total Revenue]`
- Combo chart: `PRODUCTS[category]` → `[Total Discount]` (columns) + average discount % (line) vs `[Total Revenue]`
- Bar chart: `SALES[sales_channel]` → `[Total Revenue]`

**Slicers:** Category, Customer Segment, Age Group, Sales Channel

---

## 6. Build Notes / Interview Talking Points

- **Why a star schema:** keeps every measure a simple `SUM`/`DIVIDE` over the
  SALES/INVENTORY fact tables, avoids ambiguous relationship paths, and is
  the standard, defensible modeling choice for a BA-level dashboard.
- **Why `DATEADD` for MoM growth instead of a manual LAG-style calc:**
  `DATEADD` respects the active filter context (slicers, drill-downs) so
  the growth % stays correct no matter what the user has filtered to —
  a hard-coded row-offset wouldn't.
- **Why Inventory Turnover uses `INVENTORY[sold_quantity]` and not
  `SALES[quantity]`:** the inventory table's `sold_quantity` is scoped to
  the exact same 12-month window as `closing_stock`, so turnover is
  computed on a like-for-like basis; mixing a 24-month sales figure with
  a 12-month average inventory would inflate the ratio.
- **Why the KPI cards are duplicated per page instead of one global page:**
  each page is meant to support a different conversation (sales
  performance vs. inventory health vs. product/customer mix), so the KPIs
  shown are the ones relevant to that conversation.
