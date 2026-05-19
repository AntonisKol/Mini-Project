# ============================================================================
# SECTION C - PYTHON + PANDAS DATA PROCESSING
# Q3. Business KPI Generation
# ============================================================================
# Purpose: Calculate key business metrics and KPIs
# Tasks: 1. Daily sales KPI
#        2. Customer lifetime value
#        3. Category-wise revenue
#        4. Repeat customer percentage

import pandas as pd
import sqlite3

# ============================================================================
# STEP 0: Connect to SQLite database with cleaned data
# ============================================================================

print("=" * 80)
print("CONNECTING TO SQLITE DATABASE")
print("=" * 80)

db_path = 'quickcart.db'
conn = sqlite3.connect(db_path)

print("\n✓ Connected to: {}".format(db_path))

# ============================================================================
# TASK 1:
# ============================================================================

print("\n" + "=" * 80)
print("TASK 1: DAILY SALES KPI")
print("=" * 80)

# Query: Group orders by date and calculate daily metrics/
daily_sales_query = """
SELECT 
    DATE(order_time) as order_date,
    COUNT(DISTINCT order_id) as orders_count,      -- How many orders
    SUM(total_usd) as daily_revenue,               -- Total revenue
    ROUND(AVG(total_usd), 2) as avg_order_value    -- Average order value
FROM orders
GROUP BY order_date
ORDER BY order_date DESC
LIMIT 30
"""

daily_sales = pd.read_sql(daily_sales_query, conn)

print("\nDaily Sales (Last 30 days):")
print(daily_sales.head(10))

print("\n--- Daily Sales Summary ---")
print("Total days with orders: {}".format(len(daily_sales)))
print("Average daily revenue: ${:.2f}".format(daily_sales['daily_revenue'].mean()))
print("Max daily revenue: ${:.2f}".format(daily_sales['daily_revenue'].max()))
print("Min daily revenue: ${:.2f}".format(daily_sales['daily_revenue'].min()))

# ============================================================================
# TASK 2: CUSTOMER LIFETIME VALUE (CLV)
# ============================================================================

print("\n" + "=" * 80)
print("TASK 2: CUSTOMER LIFETIME VALUE (CLV)")
print("=" * 80)

# Query: Calculate total spending per customer
clv_query = """
SELECT 
    c.customer_id,
    c.name,
    c.country,
    COUNT(DISTINCT o.order_id) as total_orders,    -- How many times they ordered
    SUM(o.total_usd) as lifetime_value,            -- Total $ they spent
    ROUND(AVG(o.total_usd), 2) as avg_order_value  -- Average per order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.country
ORDER BY lifetime_value DESC
"""

clv = pd.read_sql(clv_query, conn)

print("\nTop 10 Customers by Lifetime Value:")
print(clv.head(10))

print("\n--- Customer Lifetime Value Summary ---")
print("Total customers: {}".format(len(clv)))
print("Average CLV per customer: ${:.2f}".format(clv['lifetime_value'].mean()))
print("Median CLV per customer: ${:.2f}".format(clv['lifetime_value'].median()))
print("Highest CLV: ${:.2f}".format(clv['lifetime_value'].max()))
print("Lowest CLV: ${:.2f}".format(clv['lifetime_value'].min()))

# Segment customers by spending
print("\n--- Customer Segmentation by Spending ---")
clv['segment'] = pd.cut(clv['lifetime_value'], 
bins=[0, 100, 500, 1000, float('inf')],
labels=['Bronze (<$100)', 'Silver ($100-$500)', 'Gold ($500-$1000)', 'Platinum (>$1000)'])

segment_summary = clv['segment'].value_counts()
print(segment_summary)

# ============================================================================
# TASK 3: CATEGORY-WISE REVENUE
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3: CATEGORY-WISE REVENUE")
print("=" * 80)

# Query: Revenue by product category
category_revenue_query = """
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) as orders,          -- How many orders
    COUNT(oi.product_id) as items_sold,            -- How many items
    SUM(oi.line_total_usd) as total_revenue,       -- Total revenue
    ROUND(AVG(oi.unit_price_usd), 2) as avg_price  -- Average item price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY total_revenue DESC
"""

category_revenue = pd.read_sql(category_revenue_query, conn)

print("\nRevenue by Category:")
print(category_revenue)

# Calculate revenue percentage
category_revenue['revenue_percentage'] = (
    (category_revenue['total_revenue'] / category_revenue['total_revenue'].sum()) * 100
).round(2)

print("\n--- Category Revenue Breakdown ---")
for idx, row in category_revenue.iterrows():
    print("{}: ${:.2f} ({}% of total)".format(
        row['category'], 
        row['total_revenue'], 
        row['revenue_percentage']
    ))

print("\n--- Category Summary ---")
print("Total categories: {}".format(len(category_revenue)))
print("Total revenue across all categories: ${:.2f}".format(category_revenue['total_revenue'].sum()))
print("Top category: {} (${:.2f})".format(
    category_revenue.iloc[0]['category'], 
    category_revenue.iloc[0]['total_revenue']
))

# ============================================================================
# TASK 4: REPEAT CUSTOMER PERCENTAGE
# ============================================================================

print("\n" + "=" * 80)
print("TASK 4: REPEAT CUSTOMER PERCENTAGE")
print("=" * 80)

# Query: Count orders per customer
repeat_query = """
SELECT 
    customer_id,
    COUNT(DISTINCT order_id) as order_count
FROM orders
GROUP BY customer_id
"""

repeat_data = pd.read_sql(repeat_query, conn)

# Categorize customers
repeat_data['customer_type'] = repeat_data['order_count'].apply(
    lambda x: 'One-time buyer' if x == 1 
    else 'Regular buyer (2-5 orders)' if 2 <= x <= 5 
    else 'Loyal customer (6+ orders)'
)

print("\nCustomer Types Distribution:")
customer_type_counts = repeat_data['customer_type'].value_counts()
print(customer_type_counts)

print("\n--- Repeat Customer Analysis ---")
total_customers = len(repeat_data)
one_time = len(repeat_data[repeat_data['order_count'] == 1])
repeat_customers = len(repeat_data[repeat_data['order_count'] > 1])
loyal_customers = len(repeat_data[repeat_data['order_count'] >= 6])

one_time_pct = (one_time / total_customers) * 100
repeat_pct = (repeat_customers / total_customers) * 100
loyal_pct = (loyal_customers / total_customers) * 100

print("Total customers: {}".format(total_customers))
print("One-time buyers: {} ({}%)".format(one_time, round(one_time_pct, 2)))
print("Repeat customers (2+ orders): {} ({}%)".format(repeat_customers, round(repeat_pct, 2)))
print("Loyal customers (6+ orders): {} ({}%)".format(loyal_customers, round(loyal_pct, 2)))

# ============================================================================
# EXPORT KPI SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("KPI SUMMARY EXPORTED")
print("=" * 80)

# Save KPI dataframes to CSV for reference
daily_sales.to_csv('kpi_daily_sales.csv', index=False)
clv.to_csv('kpi_customer_lifetime_value.csv', index=False)
category_revenue.to_csv('kpi_category_revenue.csv', index=False)

print("\n✓ kpi_daily_sales.csv exported")
print("✓ kpi_customer_lifetime_value.csv exported")
print("✓ kpi_category_revenue.csv exported")

# ============================================================================
# CLOSE CONNECTION
# ============================================================================

conn.close()

print("\n" + "=" * 80)
print("KPI GENERATION COMPLETE ✓")
print("=" * 80)
print("\nSummary:")
print("✓ Task 1: Daily sales KPI calculated")
print("✓ Task 2: Customer lifetime value calculated")
print("✓ Task 3: Category-wise revenue analyzed")
print("✓ Task 4: Repeat customer percentage calculated")
print("✓ Results exported to CSV files")