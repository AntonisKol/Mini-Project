-- ============================================================================
-- DBT MART MODEL: dim_products (DIMENSION TABLE)
-- ============================================================================
-- PURPOSE:
-- Create the product dimension table for analytical joins.
-- One row per product with all product attributes and metrics.
--
-- WHY THIS APPROACH IS CORRECT:
-- Product dimension stores product attributes.
-- Joined to fact tables to analyze by product category, price, margin.
-- Enables analysis: Which categories are most profitable?
--
-- INPUT: stg_products, int_order_details (for sales metrics)
-- OUTPUT: dim_products (one row per product with sales metrics)
-- Row count: One row per product (dimensional grain)
-- Used by: Product dashboards, category analysis, margin reports

WITH product_metrics AS (
    SELECT
        p.product_id,                                   -- Product dimension key
        p.name as product_name,                         -- Product name
        p.category as product_category,                 -- Product category
        p.price_usd as list_price_usd,                 -- Standard list price
        p.cost_usd as product_cost_usd,                 -- Cost to acquire
        p.margin_usd as margin_per_unit_usd,            -- Profit per unit
        p.margin_percentage as margin_percentage,       -- Profit margin %
        
        -- Sales metrics (from order details)
        COUNT(DISTINCT od.order_id) as order_count,    -- How many orders include this
        SUM(od.quantity) as units_sold,                 -- Total units sold
        ROUND(SUM(od.line_total_usd), 2) as total_revenue_usd,  -- Total revenue
        ROUND(SUM(od.line_profit), 2) as total_profit_usd,      -- Total profit
        
        -- Performance metrics
        CASE
            WHEN SUM(od.units_sold) > 1000 THEN 'Top seller'
            WHEN SUM(od.units_sold) > 100 THEN 'Popular'
            WHEN SUM(od.units_sold) > 10 THEN 'Moderate'
            ELSE 'Slow mover'
        END as sales_performance,                       -- Product performance
        
        CASE
            WHEN p.margin_percentage > 40 THEN 'High margin'
            WHEN p.margin_percentage > 20 THEN 'Medium margin'
            ELSE 'Low margin'
        END as margin_tier,                             -- Profitability tier
        
        -- Metadata
        CURRENT_TIMESTAMP as dbt_loaded_at,            -- When this model ran
        CURRENT_DATE as data_date                       -- Data as of date
        
    FROM {{ ref('stg_products') }} p                   -- Start with staging products
    LEFT JOIN {{ ref('int_order_details') }} od        -- Join with intermediate order details
        ON p.product_id = od.product_id                -- Match by product ID
    
    GROUP BY
        p.product_id, p.name, p.category,
        p.price_usd, p.cost_usd, p.margin_usd,
        p.margin_percentage
)

SELECT *
FROM product_metrics

-- ============================================================================
-- BUSINESS LOGIC COMMENTS
-- ============================================================================
--
-- This dimension table answers questions like:
-- 1. Which products are bestsellers?
--    → SELECT product_name FROM dim_products ORDER BY units_sold DESC
--
-- 2. Which categories are most profitable?
--    → SELECT product_category, SUM(total_profit_usd) 
--      FROM dim_products GROUP BY product_category
--
-- 3. Which products have high margin?
--    → SELECT * FROM dim_products WHERE margin_tier = 'High margin'
--
-- 4. Join to fact table for product-level analysis:
--    SELECT f.order_date, d.product_name, f.order_total_usd
--    FROM fct_sales f
--    JOIN dim_products d ON f.product_id = d.product_id
--
-- ============================================================================

{% if execute %}
    {{ log("Loaded " ~ this.rows ~ " product dimensions", info=true) }}
{% endif %}