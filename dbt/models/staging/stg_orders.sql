WITH cleaned_orders AS (
    SELECT
        order_id,
        customer_id,
        order_time,
        payment_method,
        discount_pct,
        subtotal_usd,
        total_usd,
        country,
        device,
        source
    FROM orders
)
SELECT * FROM cleaned_orders
