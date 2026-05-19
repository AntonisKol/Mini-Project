-- ============================================================================
-- DBT INTERMEDIATE MODEL: int_customer_orders
-- ============================================================================
-- PURPOSE:
-- Join customers with their orders.
-- Combine customer info + order info into one enriched table.
-- This is an intermediate layer (not raw, not final business table).
--
-- WHY THIS APPROACH IS CORRECT:
-- Staging models are individual tables (customers, orders, products).
-- Intermediate models join staging tables together.
-- Marts models use intermediate tables to create final business tables.
-- This separation makes transformations reusable and testable.
--
-- INPUT: stg_customers, stg_orders
-- OUTPUT: int_customer_orders (one row per order with customer details)
-- Row count: Same as orders (one order = one row, even if multiple items)

WITH customer_orders AS (
    SELECT
        -- Order information
        o.order_id,                                     -- Unique order ID
        o.customer_id,                                  -- Customer ID
        o.order_date,                                   -- Date order placed
        o.order_year,                                   -- Year (for partitioning)
        o.order_month,                                  -- Month (for partitioning)
        o.order_day,                                    -- Day
        o.payment_method,                               -- How they paid
        o.discount_pct,                                 -- Discount applied
        o.subtotal_usd,                                 -- Before discount
        o.total_usd,                                    -- After discount
        o.device,                                       -- Device used
        o.source,                                       -- Traffic source
        
        -- Customer information (enriched)
        c.name as customer_name,                        -- Customer full name
        c.email as customer_email,                      -- Customer email
        c.country as customer_country,                  -- Customer location
        c.age as customer_age,                          -- Customer age
        c.signup_date,                                  -- When customer signed up
        c.marketing_opt_in,                             -- Marketing consent
        
        -- Calculated fields
        CASE
            WHEN o.discount_pct > 0 THEN 'Yes'
            ELSE 'No'
        END as has_discount,                            -- Was discount applied?
        
        -- Days since signup
        CAST((o.order_date - c.signup_date) AS INTEGER) as days_since_signup,
        
        -- Customer lifetime (in days from signup to order)
        CASE
            WHEN CAST((o.order_date - c.signup_date) AS INTEGER) < 30 THEN 'New'
            WHEN CAST((o.order_date - c.signup_date) AS INTEGER) < 365 THEN 'Regular'
            ELSE 'Loyal'
        END as customer_lifecycle,
        
        -- Metadata
        CURRENT_TIMESTAMP as dbt_loaded_at             -- When this model ran
        
    FROM {{ ref('stg_orders') }} o                      -- Reference staging orders model
    LEFT JOIN {{ ref('stg_customers') }} c              -- Left join with staging customers
        ON o.customer_id = c.customer_id                -- Match by customer ID
)

SELECT *
FROM customer_orders

-- dbt configuration
{% if execute %}
    {{ log("Loaded " ~ this.rows ~ " customer orders", info=true) }}
{% endif %}