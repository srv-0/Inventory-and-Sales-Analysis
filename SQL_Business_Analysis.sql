-- =====================================================================
-- INVENTORY & SALES ANALYSIS -- RETAIL BUSINESS
-- SQL Business Analysis -- 20 Questions & Solutions
-- Dialect: MySQL 8.0 (window functions, CTEs)
-- Tables: products, customers, sales, inventory, stores, salespersons
-- =====================================================================
-- All queries were validated against the actual generated dataset
-- (see /data/retail_analysis.db and test_sql.py) before being written
-- here in MySQL syntax. Row-level results are summarized in
-- EDA_Report.md and Final_Insights_and_Recommendations.md.
-- =====================================================================


-- =====================================================================
-- SECTION 1: BASIC (5 questions)
-- =====================================================================

-- Q1. What is the total revenue generated?
SELECT ROUND(SUM(final_amount), 2) AS total_revenue
FROM sales;


-- Q2. What are the total units sold?
SELECT SUM(quantity) AS total_units_sold
FROM sales;


-- Q3. What is the average order value (AOV)?
SELECT ROUND(AVG(final_amount), 2) AS avg_order_value
FROM sales;


-- Q4. Which categories generate the highest revenue?
SELECT p.category,
       ROUND(SUM(s.final_amount), 2) AS revenue
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- Q5. Which products have the highest sales volume (units sold)?
SELECT p.product_id, p.product_name,
       SUM(s.quantity) AS units_sold
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name
ORDER BY units_sold DESC
LIMIT 10;


-- =====================================================================
-- SECTION 2: INTERMEDIATE (8 questions)
-- =====================================================================

-- Q6. Which stores generate the most revenue?
SELECT st.store_name, st.region,
       ROUND(SUM(s.final_amount), 2) AS revenue
FROM sales s
JOIN stores st ON st.store_id = s.store_id
GROUP BY st.store_name, st.region
ORDER BY revenue DESC;


-- Q7. Which customer segments contribute the most revenue?
SELECT c.customer_segment,
       ROUND(SUM(s.final_amount), 2) AS revenue,
       ROUND(100.0 * SUM(s.final_amount) / (SELECT SUM(final_amount) FROM sales), 2) AS pct_of_total
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
GROUP BY c.customer_segment
ORDER BY revenue DESC;


-- Q8. What is the average discount % by category?
SELECT p.category,
       ROUND(AVG(s.discount_amount / NULLIF(s.quantity * s.unit_price, 0)) * 100, 2) AS avg_discount_pct
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY avg_discount_pct DESC;


-- Q9. Which products generate the highest gross margin %?
--     (restricted to products with meaningful revenue so one-off sales don't skew the ranking)
SELECT p.product_id, p.product_name,
       ROUND(SUM((s.unit_price - p.unit_cost) * s.quantity - s.discount_amount), 2) AS gross_profit,
       ROUND(100.0 * SUM((s.unit_price - p.unit_cost) * s.quantity - s.discount_amount)
             / SUM(s.final_amount), 2) AS margin_pct
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.product_id, p.product_name
HAVING SUM(s.final_amount) > 5000
ORDER BY margin_pct DESC
LIMIT 10;


-- Q10. Which products have low sales but high inventory (overstock risk)?
WITH product_sales AS (
    SELECT product_id, SUM(quantity) AS units_sold_12mo
    FROM sales
    GROUP BY product_id
),
product_inventory AS (
    SELECT product_id, AVG(closing_stock) AS avg_inventory
    FROM inventory
    GROUP BY product_id
)
SELECT p.product_id, p.product_name, p.category,
       COALESCE(ps.units_sold_12mo, 0) AS units_sold_12mo,
       ROUND(pi.avg_inventory, 1) AS avg_inventory
FROM products p
JOIN product_inventory pi ON pi.product_id = p.product_id
LEFT JOIN product_sales ps ON ps.product_id = p.product_id
WHERE pi.avg_inventory > 60 AND COALESCE(ps.units_sold_12mo, 0) < 20
ORDER BY pi.avg_inventory DESC
LIMIT 15;


-- Q11. Which products are frequently out of stock?
SELECT product_id,
       SUM(CASE WHEN stock_status = 'Out of Stock' THEN 1 ELSE 0 END) AS stockout_months,
       COUNT(*) AS months_tracked
FROM inventory
GROUP BY product_id
HAVING stockout_months >= 3
ORDER BY stockout_months DESC
LIMIT 15;


-- Q12. Which products have the highest average inventory levels?
SELECT i.product_id, p.product_name, p.category,
       ROUND(AVG(i.closing_stock), 1) AS avg_closing_stock
FROM inventory i
JOIN products p ON p.product_id = i.product_id
GROUP BY i.product_id, p.product_name, p.category
ORDER BY avg_closing_stock DESC
LIMIT 15;


-- Q13. Calculate monthly revenue.
SELECT DATE_FORMAT(sale_date, '%Y-%m') AS sales_month,
       ROUND(SUM(final_amount), 2) AS revenue
FROM sales
GROUP BY sales_month
ORDER BY sales_month;


-- =====================================================================
-- SECTION 3: ADVANCED (7 questions)
-- =====================================================================

-- Q14. Calculate month-over-month (MoM) revenue growth %.
WITH monthly AS (
    SELECT DATE_FORMAT(sale_date, '%Y-%m') AS sales_month,
           SUM(final_amount) AS revenue
    FROM sales
    GROUP BY sales_month
)
SELECT sales_month,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY sales_month))
             / LAG(revenue) OVER (ORDER BY sales_month), 2) AS mom_growth_pct
FROM monthly
ORDER BY sales_month;


-- Q15. Calculate each category's percentage contribution to total revenue.
SELECT p.category,
       ROUND(SUM(s.final_amount), 2) AS revenue,
       ROUND(100.0 * SUM(s.final_amount) / SUM(SUM(s.final_amount)) OVER (), 2) AS pct_contribution
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY p.category
ORDER BY revenue DESC;


-- Q16. Rank products within each category by revenue (top 3 per category).
WITH product_revenue AS (
    SELECT p.category, p.product_id, p.product_name,
           SUM(s.final_amount) AS revenue
    FROM sales s
    JOIN products p ON p.product_id = s.product_id
    GROUP BY p.category, p.product_id, p.product_name
),
ranked AS (
    SELECT category, product_id, product_name, revenue,
           RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS category_rank
    FROM product_revenue
)
SELECT *
FROM ranked
WHERE category_rank <= 3
ORDER BY category, category_rank;


-- Q17. Calculate cumulative monthly revenue (running total).
WITH monthly AS (
    SELECT DATE_FORMAT(sale_date, '%Y-%m') AS sales_month,
           SUM(final_amount) AS revenue
    FROM sales
    GROUP BY sales_month
)
SELECT sales_month,
       ROUND(revenue, 2) AS revenue,
       ROUND(SUM(revenue) OVER (ORDER BY sales_month), 2) AS cumulative_revenue
FROM monthly
ORDER BY sales_month;


-- Q18. Identify products whose revenue is above their category average.
WITH product_revenue AS (
    SELECT p.category, p.product_id, p.product_name,
           SUM(s.final_amount) AS revenue
    FROM sales s
    JOIN products p ON p.product_id = s.product_id
    GROUP BY p.category, p.product_id, p.product_name
),
cat_avg AS (
    SELECT category, AVG(revenue) AS avg_category_revenue
    FROM product_revenue
    GROUP BY category
)
SELECT pr.category, pr.product_id, pr.product_name,
       ROUND(pr.revenue, 2) AS revenue,
       ROUND(ca.avg_category_revenue, 2) AS category_avg_revenue
FROM product_revenue pr
JOIN cat_avg ca ON ca.category = pr.category
WHERE pr.revenue > ca.avg_category_revenue
ORDER BY pr.category, pr.revenue DESC;


-- Q19. Identify slow-moving inventory (lowest turnover, meaningful stock on hand).
WITH turnover AS (
    SELECT product_id,
           SUM(sold_quantity) AS units_sold_12mo,
           AVG(closing_stock) AS avg_inventory,
           ROUND(SUM(sold_quantity) * 1.0 / NULLIF(AVG(closing_stock), 0), 2) AS turnover_ratio
    FROM inventory
    GROUP BY product_id
)
SELECT t.product_id, p.product_name, p.category,
       t.units_sold_12mo, ROUND(t.avg_inventory, 1) AS avg_inventory, t.turnover_ratio
FROM turnover t
JOIN products p ON p.product_id = t.product_id
WHERE t.avg_inventory > 15
ORDER BY t.turnover_ratio ASC
LIMIT 15;


-- Q20. Identify products that require inventory / pricing action
--      (chronic stockouts -> expedite replenishment; chronic overstock + weak sales -> clearance).
WITH sales_perf AS (
    SELECT product_id, SUM(quantity) AS units_sold, SUM(final_amount) AS revenue
    FROM sales
    GROUP BY product_id
),
inv_perf AS (
    SELECT product_id,
           AVG(closing_stock) AS avg_inventory,
           SUM(CASE WHEN stock_status = 'Out of Stock' THEN 1 ELSE 0 END) AS stockout_months,
           SUM(CASE WHEN stock_status = 'Overstock' THEN 1 ELSE 0 END) AS overstock_months
    FROM inventory
    GROUP BY product_id
)
SELECT p.product_id, p.product_name, p.category,
       COALESCE(sp.units_sold, 0) AS units_sold,
       ROUND(ip.avg_inventory, 1) AS avg_inventory,
       ip.stockout_months, ip.overstock_months,
       CASE
           WHEN ip.stockout_months >= 3 THEN 'Increase reorder level / expedite replenishment'
           WHEN ip.overstock_months >= 3 AND COALESCE(sp.units_sold, 0) < 30 THEN 'Reduce inventory / run clearance promotion'
           ELSE 'Monitor'
       END AS recommended_action
FROM products p
JOIN inv_perf ip ON ip.product_id = p.product_id
LEFT JOIN sales_perf sp ON sp.product_id = p.product_id
WHERE ip.stockout_months >= 3
   OR (ip.overstock_months >= 3 AND COALESCE(sp.units_sold, 0) < 30)
ORDER BY ip.stockout_months DESC, ip.overstock_months DESC
LIMIT 20;
