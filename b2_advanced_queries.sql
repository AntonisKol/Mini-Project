-- SECTION B - SQL ENGINEERING
-- b2_advanced_queries.sql
-- Q2. Advanced SQL Queries

-- QUERY 1: Rank customers based on total revenue
SELECT 
    c.customer_id,
    c.name,
    SUM(o.total_usd) as total_revenue,
    RANK() OVER (ORDER BY SUM(o.total_usd) DESC) as revenue_rank,
    ROW_NUMBER() OVER (ORDER BY SUM(o.total_usd) DESC) as unique_rank,
    NTILE(4) OVER (ORDER BY SUM(o.total_usd) DESC) as revenue_quartile
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_revenue DESC;

-- QUERY 2: Find running total sales by month
SELECT 
    CAST(order_year || '-' || PRINTF('%02d', order_month) || '-01' AS DATE) as month,
    SUM(total_usd) as monthly_sales,
    SUM(SUM(total_usd)) OVER (ORDER BY order_year, order_month) as running_total_sales
FROM orders
GROUP BY order_year, order_month
ORDER BY month;

-- QUERY 3: Find highest selling product per category
WITH category_ranked_products AS (
    SELECT 
        p.category,
        p.product_id,
        p.name,
        SUM(oi.quantity) as total_quantity_sold,
        SUM(oi.line_total_usd) as total_revenue,
        ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(oi.quantity) DESC) as rank_in_category
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_id, p.name
)
SELECT 
    category,
    product_id,
    name,
    total_quantity_sold,
    total_revenue
FROM category_ranked_products
WHERE rank_in_category = 1
ORDER BY category;

-- QUERY 4: Find 7-day rolling average sales
SELECT 
    DATE(order_time) as order_day,
    SUM(total_usd) as daily_sales,
    ROUND(
        AVG(SUM(total_usd)) OVER (
            ORDER BY DATE(order_time) 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) as rolling_7_day_avg
FROM orders
GROUP BY DATE(order_time)
ORDER BY order_day;