-- ============================================================================
-- DBT MART MODEL: fct_sales (FACT TABLE)
-- ============================================================================
-- PURPOSE:
-- Create the core fact table for sales analytics.
-- One row per order with all financial metrics and dimensions.
-- This is the main table dashboards query for sales analysis.
--
-- WHY THIS APPROACH IS CORRECT:
-- Fact tables store transactional events (orders, sales).
-- Dimension tables store attributes (customers, products, dates).
-- Fact tables have many rows (one per transaction).
-- Fact tables are heavily aggregated and queried.
-- This is the final layer - ready for dashboards.
--
-- INPUT: int_customer_orders, int_order_details
-- OUTPUT: fct_sales (one row per order with financial metrics)
-- Row count: One row per order (transactional grain)
-- Used by: Sales dashboards, revenue reports, profitability analysis

WITH order_metrics AS (
    SELECT
        -- Primary keys (for joining to dimensions)
        co.order_id,                                    -- Fact table key
        co.customer_id,                                 -- Customer dimension key
        
        -- Date dimensions
        co.order_date,                                  -- Order date
        co.order_year,                                  -- Year (for partitioning)
        co.order_month,                                 -- Month (for partitioning)
        co.order_day,                                   -- Day
        
        -- Customer attributes
        co.customer_name,
        co.customer_email,
        co.customer_country,
        co.customer_age,
        co.customer_lifecycle,                          -- 'New', 'Regular', 'Loyal'
        co.has_discount,                                -- 'Yes' or 'No'
        
        -- Order attributes
        co.device,                                      -- 'mobile', 'desktop', 'tablet'
        co.source,                                      -- 'organic', 'paid', 'direct'
        co.payment_method,
        
        -- Financial metrics
        co.subtotal_usd,                                -- Revenue before discount
        co.discount_pct,                                -- Discount percentage
        ROUND(co.subtotal_usd * (co.discount_pct / 100), 2) as discount_amount_usd,  -- $ discounted
        co.total_usd as order_total_usd,                -- Revenue after discount
        
        -- Order profitability (aggregate from line items)
        ROUND(SUM(od.line_profit), 2) as order_profit_usd,  -- Total profit
        
        -- Derived metrics
        CASE
            WHEN co.total_usd < 50 THEN 'Small'
            WHEN co.total_usd < 100 THEN 'Medium'
            WHEN co.total_usd < 500 THEN 'Large'
            ELSE 'Enterprise'
        END as order_size_category,                     -- Order size segment
        
        CASE
            WHEN (ROUND(SUM(od.line_profit), 2) / NULLIF(co.total_usd, 0) * 100) > 40 THEN 'High'
            WHEN (ROUND(SUM(od.line_profit), 2) / NULLIF(co.total_usd, 0) * 100) > 20 THEN 'Medium'
            ELSE 'Low'
        END as profitability_tier,                      -- Profitability level
        
        COUNT(DISTINCT od.product_id) as product_count, -- How many products ordered
        
        -- Metadata
        CURRENT_TIMESTAMP as dbt_loaded_at,            -- When this model ran
        CURRENT_DATE as data_date                       -- Data as of date
        
    FROM {{ ref('int_customer_orders') }} co            -- Join with intermediate customer orders
    LEFT JOIN {{ ref('int_order_details') }} od         -- Join with intermediate order details
        ON co.order_id = od.order_id                    -- Match by order ID
    
    GROUP BY
        co.order_id, co.customer_id, co.order_date,
        co.order_year, co.order_month, co.order_day,
        co.customer_name, co.customer_email,
        co.customer_country, co.customer_age,
        co.customer_lifecycle, co.has_discount,
        co.device, co.source, co.payment_method,
        co.subtotal_usd, co.discount_pct, co.total_usd
)

SELECT *
FROM order_metrics

-- ============================================================================
-- BUSINESS LOGIC COMMENTS
-- ============================================================================
--
-- This fact table answers questions like:
-- 1. What's our total revenue by day/month/year?
--    → SELECT SUM(order_total_usd) FROM fct_sales GROUP BY order_date
--
-- 2. Which customers spend the most?
--    → SELECT customer_id, SUM(order_total_usd) FROM fct_sales GROUP BY customer_id
--
-- 3. What's our profit margin?
--    → SELECT SUM(order_profit_usd) / SUM(order_total_usd) * 100 FROM fct_sales
--
-- 4. Do mobile users spend differently?
--    → SELECT device, AVG(order_total_usd) FROM fct_sales GROUP BY device
--
-- 5. Which traffic sources convert best?
--    → SELECT source, COUNT(*), SUM(order_total_usd) FROM fct_sales GROUP BY source
--
-- ============================================================================

{% if execute %}
    {{ log("Loaded " ~ this.rows ~ " sales facts", info=true) }}
{% endif %}