-- ============================================================================
-- DBT MART MODEL: dim_customers (DIMENSION TABLE)
-- ============================================================================
-- PURPOSE:
-- Create the customer dimension table for analytical joins.
-- One row per customer with all customer attributes.
-- Dimension tables are joined to fact tables to slice/dice data.
--
-- WHY THIS APPROACH IS CORRECT:
-- Dimension tables store attributes (slowly changing data).
-- Facts are joined to dimensions to answer business questions.
-- Dimension tables are smaller (fewer rows than facts).
-- This is the final layer - ready for dashboards.
--
-- INPUT: stg_customers, int_customer_orders (for aggregation)
-- OUTPUT: dim_customers (one row per customer with metrics)
-- Row count: One row per customer (dimensional grain)
-- Used by: Customer dashboards, segmentation analysis, CRM reports

WITH customer_metrics AS (
    SELECT
        c.customer_id,                                  -- Customer dimension key
        c.name as customer_name,                        -- Full name
        c.email,                                        -- Email address
        c.country,                                      -- Home country
        c.age,                                          -- Age
        c.signup_date,                                  -- When signed up
        c.marketing_opt_in,                             -- Marketing consent
        
        -- Customer segmentation
        CASE
            WHEN c.age < 25 THEN '18-24'
            WHEN c.age < 35 THEN '25-34'
            WHEN c.age < 45 THEN '35-44'
            WHEN c.age < 55 THEN '45-54'
            ELSE '55+'
        END as age_group,                               -- Age segment
        
        -- Customer value metrics (from orders)
        COUNT(DISTINCT co.order_id) as lifetime_order_count,  -- Total orders
        ROUND(SUM(co.total_usd), 2) as lifetime_value_usd,   -- Total $ spent
        
        CASE
            WHEN COUNT(DISTINCT co.order_id) = 0 THEN 'Inactive'
            WHEN COUNT(DISTINCT co.order_id) = 1 THEN 'One-time'
            WHEN COUNT(DISTINCT co.order_id) < 6 THEN 'Regular'
            ELSE 'Loyal'
        END as customer_segment,                        -- Customer classification
        
        -- Order behavior
        CASE
            WHEN COUNT(DISTINCT co.order_id) > 0 
            THEN ROUND(SUM(co.total_usd) / COUNT(DISTINCT co.order_id), 2)
            ELSE 0
        END as avg_order_value_usd,                     -- Average order value
        
        -- Recency (days since last order)
        CASE
            WHEN MAX(co.order_date) IS NULL THEN NULL
            ELSE CAST((CURRENT_DATE - MAX(co.order_date)) AS INTEGER)
        END as days_since_last_order,                   -- Recency metric
        
        -- Metadata
        CURRENT_TIMESTAMP as dbt_loaded_at,            -- When this model ran
        CURRENT_DATE as data_date                       -- Data as of date
        
    FROM {{ ref('stg_customers') }} c                  -- Start with staging customers
    LEFT JOIN {{ ref('int_customer_orders') }} co      -- Join with intermediate orders
        ON c.customer_id = co.customer_id              -- Match by customer ID
    
    GROUP BY
        c.customer_id, c.name, c.email, c.country,
        c.age, c.signup_date, c.marketing_opt_in
)

SELECT *
FROM customer_metrics

-- ============================================================================
-- BUSINESS LOGIC COMMENTS
-- ============================================================================
--
-- This dimension table answers questions like:
-- 1. How many customers do we have?
--    → SELECT COUNT(*) FROM dim_customers
--
-- 2. What's our average customer lifetime value?
--    → SELECT AVG(lifetime_value_usd) FROM dim_customers
--
-- 3. Which customers are at risk of churning?
--    → SELECT * FROM dim_customers WHERE days_since_last_order > 90
--
-- 4. How many loyal customers do we have?
--    → SELECT COUNT(*) FROM dim_customers WHERE customer_segment = 'Loyal'
--
-- 5. What's the age demographic of our customers?
--    → SELECT age_group, COUNT(*) FROM dim_customers GROUP BY age_group
--
-- 6. Join to fact table for analysis:
--    SELECT f.*, d.customer_segment, d.lifetime_value_usd
--    FROM fct_sales f
--    JOIN dim_customers d ON f.customer_id = d.customer_id
--
-- ============================================================================

{% if execute %}
    {{ log("Loaded " ~ this.rows ~ " customer dimensions", info=true) }}
{% endif %}