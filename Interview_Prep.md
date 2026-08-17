# Interview Preparation
### Inventory & Sales Analysis — UrbanNest Retail Co.

---

## The 2-Minute Explanation

> "I built an end-to-end Business Analyst project simulating a mid-sized
> retail company — 2,600 products, 4,200 customers, 10,000+ transactions,
> and 12 months of inventory snapshots across 8 stores, all synthetic but
> realistic and internally consistent.
>
> I started with the business problem: retail companies need to balance
> sales performance against inventory efficiency — you lose money both
> from stockouts on things people want, and from cash tied up in stock
> that isn't moving. So I built the dataset to actually contain both
> problems, not just clean random numbers.
>
> First, I cleaned the data in Python/Pandas — checked referential
> integrity, flagged duplicates, outliers, and formula mismatches rather
> than silently deleting them, and standardized inconsistent category
> labels. Then I ran EDA to understand revenue trends, seasonality, and
> inventory health.
>
> Next, I wrote 20 SQL queries — from basic aggregations up to window
> functions for ranking and running totals — to answer specific business
> questions: which products chronically stock out, which are overstocked,
> which categories and stores drive revenue.
>
> I also built a formula-driven Excel layer — SUMIFS, COUNTIFS, INDEX/MATCH
> — for quick no-code reporting, and designed a 3-page Power BI dashboard
> with DAX measures so the findings are interactive for stakeholders.
>
> The key findings: a small set of fast-moving products chronically stock
> out despite proven demand — that's lost revenue I can point to directly.
> Overstock is a bigger, more spread-out problem — about 1 in 6 inventory
> snapshots show excess stock, mostly on slow-moving SKUs that were
> over-procured. And discounting turned out to be fairly flat across
> categories, so it's not actually what's driving the revenue differences
> between categories — which changes how I'd recommend using discounts
> going forward.
>
> Every recommendation in the project ties back to one of those findings
> — it's not just charts, it's data leading to specific, defensible
> business decisions."

---

## 20 Likely Interview Questions & Concise Answers

**1. Why did you choose this project?**
Inventory + sales analysis is close to what most retail/e-commerce BA
roles actually do day-to-day, and it let me show the full toolchain —
Python, SQL, Excel, Power BI — on one coherent business problem instead
of four disconnected exercises.

**2. Why did you choose these KPIs?**
I kept them simple and standard (revenue, AOV, margin %, turnover,
stockout/overstock rate) — the kind that show up in almost any retail BA
role, rather than inventing custom metrics that would need extra
justification. Each one maps to a specific business decision.

**3. How did you identify slow-moving inventory?**
I calculated an inventory turnover ratio per product (units sold ÷ average
closing stock over the tracked period) and ranked ascending, restricted to
products with meaningful stock on hand so a near-zero-stock product
doesn't falsely look "efficient."

**4. What would you do if sales suddenly dropped 20%?**
First isolate *where* — category, store, channel, or segment — using the
same breakdowns I already built (Q4, Q6, Q7 in the SQL file), then check
whether it's a demand issue (seasonality, competition) or a supply issue
(stockouts on key SKUs) before recommending any fix.

**5. How would you reduce stockouts?**
Set SKU-specific reorder points instead of one blanket rule — my analysis
showed stockouts are concentrated in a handful of proven fast movers, so a
targeted, tighter replenishment cycle for those specific SKUs is more
effective than raising safety stock everywhere.

**6. How would you handle overstock?**
Run targeted clearance/discount campaigns on the lowest-turnover SKUs
specifically (not category-wide), and tighten future purchase-order
quantities for the suppliers/categories that keep ending up overstocked.

**7. How would you decide which products to reorder?**
A combination of turnover ratio, current stockout/overstock history, and
revenue contribution — a low-turnover, high-revenue product still gets
different treatment than a low-turnover, low-revenue one.

**8. Why use SQL instead of Python for the business questions?**
SQL is the standard tool stakeholders and other analysts expect for
ad-hoc, repeatable business questions against relational data — it's also
what most BA job descriptions explicitly test for. Python was better
suited to the cleaning/EDA/statistical side.

**9. Why use Power BI?**
It turns the SQL/Python findings into something non-technical stakeholders
can filter and explore themselves, instead of static reports — that's the
actual deliverable most BA roles expect at the end of an analysis.

**10. How did you validate the data?**
Referential integrity checks (zero orphaned foreign keys), duplicate
detection, a formula-consistency check on `final_amount`, and IQR-based
outlier flags on price/quantity — all documented in the EDA report before
any downstream analysis ran on the data.

**11. What was the most important insight?**
That overstock (16.5% of inventory records) is a much bigger issue in
aggregate than stockouts (0.23%), even though stockouts feel more urgent —
that reframes where the business should actually focus its inventory
investment.

**12. What business decision would your dashboard support?**
A monthly inventory review meeting — deciding which SKUs to reorder
urgently, which to clear out, and whether discounting is actually needed
in a given category that month.

**13. How would you measure whether your recommendation worked?**
Track the specific KPI tied to the recommendation post-implementation —
e.g., stockout rate on the flagged fast movers should drop toward zero,
and overstock rate should decline after a clearance cycle — compared
month-over-month against the baseline established in this analysis.

**14. Why 12 categories instead of fewer?**
To reflect a realistic mid-sized retailer's breadth, and to make sure the
"revenue concentration in 2 categories" finding was actually meaningful
(concentration only means something if there were many categories to
begin with).

**15. How did you handle missing data?**
Filled missing categorical fields with an explicit "Unknown" bucket rather
than dropping rows — keeps the row (and its revenue/quantity) in the
analysis while making the gap visible and auditable rather than silently
imputed.

**16. Why flag outliers instead of removing them?**
Because I can't be sure from the data alone whether an outlier is a
genuine large/premium order or a data-entry error — flagging keeps the
decision auditable and lets a reviewer make that call, rather than me
silently discarding potentially real revenue.

**17. What's the difference between revenue and margin, and why track both?**
Revenue is total sales value; margin is what's left after cost of goods
and discounts. A category can be a revenue leader and a margin laggard at
the same time (I saw this with a couple of Furniture SKUs) — tracking
only revenue would miss that.

**18. How would you explain inventory turnover to a non-technical stakeholder?**
"It's how many times you sell through your average stock in a period — a
turnover of 4 means you're cycling through your inventory 4 times; a
turnover near 0 means stock is basically just sitting there."

**19. What would you improve if you had more time/real data?**
Add supplier lead-time data to actually model stockout root cause (is it
demand spikes or supplier delay?), and customer-level repeat-purchase
data to build a proper retention/churn view instead of segment-level
aggregates.

**20. Why does your mechanical engineering background matter for this role?**
It's given me a genuine feel for supply chain and inventory dynamics —
reorder points, lead times, stock-vs-demand tradeoffs — which map directly
onto the inventory half of this project, on top of the analytics skill set.
