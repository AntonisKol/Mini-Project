-- SECTION B - SQL ENGINEERING
-- b1_customer_analysis.sql
-- Q1. Intermediate SQL Queries

-- QUERY 1: Top 10 customers by revenue
SELECT 
    c.customer_id,
    c.name,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_usd) as total_revenue,
    ROUND(AVG(o.total_usd), 2) as avg_order_value,
    c.country
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.country
ORDER BY total_revenue DESC
LIMIT 10;

-- QUERY 2: Month-over-month sales growth
SELECT 
    CAST(order_year || '-' || PRINTF('%02d', order_month) || '-01' AS DATE) as month,
    SUM(total_usd) as monthly_revenue,
    LAG(SUM(total_usd)) OVER (ORDER BY order_year, order_month) as previous_month_revenue,
    ROUND(
        ((SUM(total_usd) - LAG(SUM(total_usd)) OVER (ORDER BY order_year, order_month)) /
         LAG(SUM(total_usd)) OVER (ORDER BY order_year, order_month) * 100), 
        2
    ) as growth_percentage
FROM orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- QUERY 3: Customers who ordered in consecutive months
WITH monthly_orders AS (
    SELECT DISTINCT
        c.customer_id,
        c.name,
        CAST(o.order_year || '-' || PRINTF('%02d', o.order_month) || '-01' AS DATE) as order_month
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
),
customer_month_sequences AS (
    SELECT 
        customer_id,
        name,
        order_month,
        LAG(order_month) OVER (PARTITION BY customer_id ORDER BY order_month) as prev_month,
        CASE 
            WHEN LAG(order_month) OVER (PARTITION BY customer_id ORDER BY order_month) 
                 = DATE(order_month, '-1 month')
            THEN 1
            ELSE 0
        END as is_consecutive
    FROM monthly_orders
)
SELECT DISTINCT
    customer_id,
    name
FROM customer_month_sequences
WHERE is_consecutive = 1
ORDER BY customer_id;

-- QUERY 4: Products never ordered
SELECT 
    p.product_id,
    p.name,
    p.category,
    p.price_usd,
    p.cost_usd,
    p.margin_usd
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.order_id IS NULL
ORDER BY p.product_id;

-- QUERY 5: Revenue contribution percentage by category
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.line_total_usd) as category_revenue,
    ROUND(
        SUM(oi.line_total_usd) / 
        SUM(SUM(oi.line_total_usd)) OVER () * 100,
        2
    ) as revenue_percentage,
    ROUND(AVG(oi.unit_price_usd), 2) as avg_price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;