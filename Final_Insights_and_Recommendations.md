# Final Business Insights & Recommendations
### Inventory & Sales Analysis — UrbanNest Retail Co.

Every insight below follows **METRIC → OBSERVATION → BUSINESS IMPLICATION →
ACTION**, and every number is pulled from the actual generated dataset
(see `EDA_Report.md` and `SQL_Business_Analysis.sql` for the underlying
calculations) — nothing here was written before running the analysis.

---

### Insight 1 — Revenue is concentrated in two categories
**METRIC:** Furniture = ₹1.25 Cr (40% of total revenue), Sports & Fitness = ₹0.55 Cr (17%). Combined, 2 of 12 categories drive ~57% of revenue.
**OBSERVATION:** These are also the two highest average-selling-price categories, not the highest-unit-volume ones.
**BUSINESS IMPLICATION:** The business is more price-point-dependent than volume-dependent — a slowdown in either category has an outsized revenue impact.
**ACTION:** Prioritize inventory availability and marketing spend for these two categories; diversify by growing a third category (Electronics or Home & Kitchen, currently mid-pack) as a hedge.

---

### Insight 2 — Revenue leaders and volume leaders are different products
**METRIC:** Top-10-by-revenue is dominated by Furniture SKUs; top-10-by-units-sold (SQL Q5) is dominated by lower-price categories.
**OBSERVATION:** A small number of high-ticket Furniture items generate revenue disproportionate to how often they actually sell.
**BUSINESS IMPLICATION:** Revenue-based product rankings alone would mislead inventory planning — a high-revenue SKU with low unit velocity still needs a *different* stocking strategy than a high-volume SKU.
**ACTION:** Use both rankings side-by-side when setting reorder policy, not revenue rank alone.

---

### Insight 3 — Overstock is a bigger, more diffuse problem than stockouts
**METRIC:** Overstock Rate = 16.5% of inventory records vs. Stockout Rate = 0.23%.
**OBSERVATION:** Excess stock is spread across "Slow"/"Dead" velocity products in nearly every category, not concentrated in one place.
**BUSINESS IMPLICATION:** A meaningful share of working capital is tied up in stock that isn't converting to sales — this is a cash-flow and warehousing-cost issue, not just a "nice to fix" one.
**ACTION:** Run a systematic clearance program on the bottom-turnover SKUs (SQL Q19) rather than category-wide promotions, and tighten future purchase-order quantities for suppliers/categories with a track record of overstock.

---

### Insight 4 — A small set of fast movers chronically stock out
**METRIC:** SQL Q11 identifies specific SKUs with 8+ stockout months out of 12-36 tracked, despite being top-velocity ("Star") products.
**OBSERVATION:** These products have consistent, strong demand — the problem is supply cadence, not demand uncertainty.
**BUSINESS IMPLICATION:** Every stockout month on these SKUs is close to guaranteed lost revenue, since demand is proven and predictable.
**ACTION:** Give these specific SKUs a tighter, dedicated replenishment cycle (higher reorder level, shorter lead-time buffer) instead of the standard policy applied store-wide.

---

### Insight 5 — Discount level doesn't explain revenue differences between categories
**METRIC:** Average discount % is fairly flat across categories (~18-20%), while category revenue ranges from ₹3.2L (Pet Supplies) to ₹1.25 Cr (Furniture) — a >35x spread.
**OBSERVATION:** Categories that discount similarly perform very differently on revenue.
**BUSINESS IMPLICATION:** Blanket, calendar-driven discounting isn't the lever moving revenue here — price point, assortment, and demand are.
**ACTION:** Shift from uniform seasonal discounting toward targeted discounting on genuinely slow-moving stock (see Insight 3), and avoid discounting already-fast-moving products that don't need it to sell.

---

### Insight 6 — Premium customers spend more per head, but Regular customers are the volume base
**METRIC:** Regular segment ≈ 57% of revenue, Premium ≈ 27% of revenue from a proportionally smaller customer base (20% of customers).
**OBSERVATION:** Premium customers have a materially higher average order value.
**BUSINESS IMPLICATION:** The two segments need different strategies — Regular customers need to be retained at scale (volume engine), Premium customers are worth a higher-touch retention investment (value engine).
**ACTION:** Build a lightweight loyalty/early-access program specifically for Premium customers; keep pricing/value proposition competitive for Regular customers since they're the larger revenue base.

---

### Insight 7 — Store performance varies more than store type alone explains
**METRIC:** Mumbai Flagship (₹63L) generates ~2.5x the revenue of Pune Store (₹24.5L).
**OBSERVATION:** Both are "Standard Store" type in several cases, yet revenue differs substantially by region/city.
**BUSINESS IMPLICATION:** Local market factors (footfall, city-level demand, staffing, or assortment fit) are driving performance more than store format.
**ACTION:** Do a store-level deep dive on Pune (and other underperformers) — check assortment mix vs. Mumbai, staffing levels, and local marketing — before assuming it's simply a smaller market.

---

### Insight 8 — Revenue shows a clear, repeatable seasonal pattern
**METRIC:** October–November revenue peaks at ~₹18-21L/month vs. a January–February trough of ~₹9-10L/month — roughly a 2x swing.
**OBSERVATION:** The pattern repeats consistently across both years of data.
**BUSINESS IMPLICATION:** This is predictable enough to plan around — inventory, staffing, and marketing spend should flex with it rather than stay flat year-round.
**ACTION:** Build the October-November inventory buffer 4-6 weeks ahead of the festive season (informed by the fast-mover stockout pattern in Insight 4), and treat January-February as the window for the clearance push identified in Insight 3.

---

### Insight 9 — Online is the larger channel, but not overwhelmingly so
**METRIC:** Online revenue = ₹1.78 Cr (57%) vs. In-Store = ₹1.35 Cr (43%).
**OBSERVATION:** The split is fairly consistent across categories (see the Excel `Excel_Analysis` category × channel pivot).
**BUSINESS IMPLICATION:** Neither channel can be deprioritized — both are meaningful contributors, and category-level channel mix doesn't show a category that's "gone all-online."
**ACTION:** Keep inventory and fulfillment planning channel-agnostic at the category level rather than treating in-store as a shrinking afterthought.

---

## Summary Priority List (what to act on first)

1. **Fix chronic stockouts on identified fast movers** (Insight 4) — clear, high-confidence revenue recovery.
2. **Run a clearance program on bottom-turnover SKUs** (Insight 3) — frees up working capital.
3. **Build seasonal inventory/staffing buffers ahead of Oct-Nov** (Insight 8) — protects the largest revenue window.
4. **Launch a Premium-segment retention program** (Insight 6) — grows the highest-value customer group.
5. **Investigate underperforming stores (e.g., Pune)** (Insight 7) — medium-term, needs more local data than this dataset alone provides.
