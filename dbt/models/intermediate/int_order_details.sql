-- ============================================================================
-- DBT INTERMEDIATE MODEL: int_order_details
-- ============================================================================
-- PURPOSE:
-- Enrich order items with product information.
-- Join order_items with products to create detailed line-by-line view.
-- Calculate product margins and profitability per line item.
--
-- WHY THIS APPROACH IS CORRECT:
-- Order items table has quantity and unit price.
-- Products table has cost and margin information.
-- Joining them creates visibility into profitability per line item.
-- This enables analysis: Which products are most profitable?
--
-- INPUT: stg_order_items, stg_products, stg_orders
-- OUTPUT: int_order_details (one row per line item with full context)
-- Row count: Same as order_items (one item = one row)

WITH order_product_details AS (
    SELECT
        -- Order item information
        oi.order_id,                                    -- Which order
        oi.product_id,                                  -- Which product
        oi.unit_price_usd,                              -- Price per unit
        oi.quantity,                                    -- Units ordered
        oi.line_total_usd,                              -- Total for this line
        
        -- Product information
        p.category as product_category,                 -- Product category
        p.name as product_name,                         -- Product name
        p.cost_usd as product_cost,                     -- Cost to acquire
        p.price_usd as product_list_price,              -- Standard list price
        p.margin_usd as product_margin_per_unit,        -- Margin per unit
        p.margin_percentage,                            -- Margin %
        
        -- Profit calculation (per line item)
        ROUND((p.price_usd - p.cost_usd) * oi.quantity, 2) as line_profit,  -- Total profit
        
        -- Metadata
        CURRENT_TIMESTAMP as dbt_loaded_at             -- When this model ran
        
    FROM {{ ref('stg_order_items') }} oi               -- Reference staging order_items
    LEFT JOIN {{ ref('stg_products') }} p              -- Left join with staging products
        ON oi.product_id = p.product_id                -- Match by product ID
)

SELECT *
FROM order_product_details

-- dbt configuration
{% if execute %}
    {{ log("Loaded " ~ this.rows ~ " order details", info=true) }}
{% endif %}