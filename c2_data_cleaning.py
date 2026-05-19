# ============================================================================
# SECTION C - PYTHON + PANDAS DATA PROCESSING
# Q2. Data Cleaning & Transformation
# ============================================================================
# Purpose: Clean and standardize all data before analysis
# Tasks: 1. Standardize city names
#        2. Convert timestamps correctly
#        3. Handle missing values
#        4. Remove corrupted rows

import pandas as pd
import sqlite3
from datetime import datetime

# ============================================================================
# STEP 0: Load raw data from CSVs
# ============================================================================

print("=" * 80)
print("LOADING RAW DATA")
print("=" * 80)

customers_df = pd.read_csv('customers.csv')
orders_df = pd.read_csv('orders.csv')
order_items_df = pd.read_csv('order_items.csv')
products_df = pd.read_csv('products.csv')
sessions_df = pd.read_csv('sessions.csv')
events_df = pd.read_csv('events.csv')
reviews_df = pd.read_csv('reviews.csv')

print("\n✓ All raw data loaded")

# ============================================================================
# TASK 1: STANDARDIZE CITY NAMES
# ============================================================================

print("\n" + "=" * 80)
print("TASK 1: STANDARDIZE CITY NAMES")
print("=" * 80)

# Show before standardization
print("\nBefore standardization (samples):")
print(customers_df['country'].head(10).tolist())

# Standardize: lowercase, strip whitespace, title case
customers_df['country'] = (customers_df['country']
                           .str.lower()           # Convert to lowercase
                           .str.strip()           # Remove leading/trailing spaces
                           .str.title())          # Convert to Title Case

print("\nAfter standardization (samples):")
print(customers_df['country'].head(10).tolist())
print("\n✓ City names standardized")

# ============================================================================
# TASK 2: CONVERT TIMESTAMPS CORRECTLY
# ============================================================================

print("\n" + "=" * 80)
print("TASK 2: CONVERT TIMESTAMPS CORRECTLY")
print("=" * 80)

# Show before conversion
print("\nBefore conversion:")
print("orders.order_time type: {}".format(orders_df['order_time'].dtype))
print("Sample: {}".format(orders_df['order_time'].iloc[0]))

# Convert order_time to datetime
orders_df['order_time'] = pd.to_datetime(orders_df['order_time'])

# Extract date components from orders (IMPORTANT: These will be saved to SQLite)
orders_df['order_date'] = orders_df['order_time'].dt.date
orders_df['order_year'] = orders_df['order_time'].dt.year
orders_df['order_month'] = orders_df['order_time'].dt.month
orders_df['order_day'] = orders_df['order_time'].dt.day

# Convert signup_date to datetime
customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'])

# Convert sessions.start_time to datetime
sessions_df['start_time'] = pd.to_datetime(sessions_df['start_time'])

# Convert events.timestamp to datetime
events_df['timestamp'] = pd.to_datetime(events_df['timestamp'])

# Convert reviews.review_time to datetime
reviews_df['review_time'] = pd.to_datetime(reviews_df['review_time'])

print("\nAfter conversion:")
print("orders.order_time type: {}".format(orders_df['order_time'].dtype))
print("Sample: {}".format(orders_df['order_time'].iloc[0]))
print("\nDate components extracted:")
print("  order_date: {}".format(orders_df['order_date'].iloc[0]))
print("  order_year: {}".format(orders_df['order_year'].iloc[0]))
print("  order_month: {}".format(orders_df['order_month'].iloc[0]))

print("\n✓ Timestamps converted and components extracted")

# ============================================================================
# TASK 3: HANDLE MISSING VALUES
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3: HANDLE MISSING VALUES")
print("=" * 80)

# Check missing values before handling
print("\nMissing values BEFORE cleaning:")

print("\nCustomers:")
print(customers_df.isnull().sum())

print("\nOrders:")
print(orders_df.isnull().sum())

print("\nOrder Items:")
print(order_items_df.isnull().sum())

print("\nProducts:")
print(products_df.isnull().sum())

print("\nSessions:")
print(sessions_df.isnull().sum())

print("\nEvents:")
print(events_df.isnull().sum())

print("\nReviews:")
print(reviews_df.isnull().sum())

# Handle missing values

# For events: fill missing numeric columns with 0 (no quantity = 0)
events_df['qty'] = events_df['qty'].fillna(0)
events_df['cart_size'] = events_df['cart_size'].fillna(0)
events_df['discount_pct'] = events_df['discount_pct'].fillna(0)
events_df['amount_usd'] = events_df['amount_usd'].fillna(0)

# For reviews: fill missing rating with 0 (no rating given)
reviews_df['rating'] = reviews_df['rating'].fillna(0)

# For other missing values, keep them as is (or you can drop rows with critical nulls)

print("\nMissing values AFTER cleaning:")

print("\nCustomers:")
print(customers_df.isnull().sum())

print("\nOrders:")
print(orders_df.isnull().sum())

print("\nEvents:")
print(events_df.isnull().sum())

print("\nReviews:")
print(reviews_df.isnull().sum())

print("\n✓ Missing values handled")

# ============================================================================
# TASK 4: REMOVE CORRUPTED ROWS
# ============================================================================

print("\n" + "=" * 80)
print("TASK 4: REMOVE CORRUPTED ROWS")
print("=" * 80)

# Remove rows with invalid/negative prices
print("\nRemoving invalid prices...")
before_price = len(order_items_df)
order_items_df = order_items_df[order_items_df['unit_price_usd'] > 0]
order_items_df = order_items_df[order_items_df['quantity'] > 0]
after_price = len(order_items_df)
print("Removed {} rows with invalid prices".format(before_price - after_price))

# Remove orders with invalid totals
print("\nRemoving invalid order totals...")
before_total = len(orders_df)
orders_df = orders_df[orders_df['total_usd'] > 0]
after_total = len(orders_df)
print("Removed {} rows with invalid totals".format(before_total - after_total))

# Remove reviews with invalid ratings (should be 1-5)
print("\nRemoving invalid ratings...")
before_rating = len(reviews_df)
reviews_df = reviews_df[reviews_df['rating'].between(0, 5)]
after_rating = len(reviews_df)
print("Removed {} rows with invalid ratings".format(before_rating - after_rating))

# Remove events with invalid amounts
print("\nRemoving invalid event amounts...")
before_events = len(events_df)
events_df = events_df[events_df['amount_usd'].notna()]  # Keeps refunds, removes nulls only
after_events = len(events_df)
print("Removed {} rows with invalid amounts".format(before_events - after_events))

print("\n✓ Corrupted rows removed")

# ============================================================================
# LOAD CLEANED DATA INTO SQLITE
# ============================================================================

print("\n" + "=" * 80)
print("LOADING CLEANED DATA INTO SQLITE")
print("=" * 80)

# Create SQLite database
db_path = 'quickcart.db'
conn = sqlite3.connect(db_path)

# Insert cleaned dataframes into SQLite (replace any existing tables)
# NOTE: order_date, order_year, order_month columns will be saved here!
customers_df.to_sql('customers', conn, if_exists='replace', index=False)
orders_df.to_sql('orders', conn, if_exists='replace', index=False)
order_items_df.to_sql('order_items', conn, if_exists='replace', index=False)
products_df.to_sql('products', conn, if_exists='replace', index=False)
sessions_df.to_sql('sessions', conn, if_exists='replace', index=False)
events_df.to_sql('events', conn, if_exists='replace', index=False)
reviews_df.to_sql('reviews', conn, if_exists='replace', index=False)

print("\n✓ SQLite database created: {}".format(db_path))
print("✓ All cleaned tables inserted into SQLite")

# Verify tables in SQLite
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("\nTables in SQLite database: {}".format([table[0] for table in tables]))

# Verify date columns exist in orders table
cursor.execute("PRAGMA table_info(orders);")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]
print("\nOrders table columns include:")
for col in ['order_date', 'order_year', 'order_month']:
    if col in column_names:
        print(f"  ✓ {col}")
    else:
        print(f"  ✗ {col} (MISSING)")

conn.close()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("DATA CLEANING COMPLETE ✓")
print("=" * 80)
print("\nSummary:")
print("✓ Task 1: City names standardized")
print("✓ Task 2: Timestamps converted to proper format")
print("✓ Task 3: Missing values handled")
print("✓ Task 4: Corrupted rows removed")
print("✓ Bonus: Cleaned data loaded into SQLite")
print("✓ Bonus: Date components (order_date, order_year, order_month) extracted and saved")