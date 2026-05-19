# ============================================================================
# SECTION C - PYTHON + PANDAS DATA PROCESSING
# Q1. Data Ingestion Pipeline
# ============================================================================
# Purpose: Load all CSV files, validate schemas, detect duplicates
# Tasks: 1. Read all datasets
#        2. Validate schema consistency
#        3. Detect duplicate records

import pandas as pd
import sqlite3
import os

# ============================================================================
# TASK 1: READ ALL DATASETS
# ============================================================================

print("=" * 80)
print("TASK 1: READING ALL DATASETS")
print("=" * 80)

# Load all CSV files into dataframes
customers_df = pd.read_csv('customers.csv')
orders_df = pd.read_csv('orders.csv')
order_items_df = pd.read_csv('order_items.csv')
products_df = pd.read_csv('products.csv')
sessions_df = pd.read_csv('sessions.csv')
events_df = pd.read_csv('events.csv')
reviews_df = pd.read_csv('reviews.csv')

# # Display what was loaded
# print("\n✓ customers.csv loaded: {} rows".format(len(customers_df)))
# print("  Columns: {}".format(list(customers_df.columns)))

# print("\n✓ orders.csv loaded: {} rows".format(len(orders_df)))
# print("  Columns: {}".format(list(orders_df.columns)))

# print("\n✓ order_items.csv loaded: {} rows".format(len(order_items_df)))
# print("  Columns: {}".format(list(order_items_df.columns)))

# print("\n✓ products.csv loaded: {} rows".format(len(products_df)))
# print("  Columns: {}".format(list(products_df.columns)))

# print("\n✓ sessions.csv loaded: {} rows".format(len(sessions_df)))
# print("  Columns: {}".format(list(sessions_df.columns)))

# print("\n✓ events.csv loaded: {} rows".format(len(events_df)))
# print("  Columns: {}".format(list(events_df.columns)))

# print("\n✓ reviews.csv loaded: {} rows".format(len(reviews_df)))
# print("  Columns: {}".format(list(reviews_df.columns)))

# ============================================================================
# TASK 2: VALIDATE SCHEMA CONSISTENCY
# ============================================================================

print("\n" + "=" * 80)
print("TASK 2: VALIDATE SCHEMA CONSISTENCY")
print("=" * 80)

# Define expected schema for each table
expected_schemas = {
    'customers': ['customer_id', 'name', 'email', 'country', 'age', 'signup_date', 'marketing_opt_in'],
    'orders': ['order_id', 'customer_id', 'order_time', 'payment_method', 'discount_pct', 'subtotal_usd', 'total_usd', 'country', 'device', 'source'],
    'order_items': ['order_id', 'product_id', 'unit_price_usd', 'quantity', 'line_total_usd'],
    'products': ['product_id', 'category', 'name', 'price_usd', 'cost_usd', 'margin_usd'],
    'sessions': ['session_id', 'customer_id', 'start_time', 'device', 'source', 'country'],
    'events': ['event_id', 'session_id', 'timestamp', 'event_type', 'product_id', 'qty', 'cart_size', 'payment', 'discount_pct', 'amount_usd'],
    'reviews': ['review_id', 'order_id', 'product_id', 'rating', 'review_text', 'review_time']
}

# Check each dataframe against expected schema
dataframes = {
    'customers': customers_df,
    'orders': orders_df,
    'order_items': order_items_df,
    'products': products_df,
    'sessions': sessions_df,
    'events': events_df,
    'reviews': reviews_df
}

print("\nSchema Validation Results:")
schema_valid = True

for table_name, df in dataframes.items():
    expected_cols = expected_schemas[table_name]
    actual_cols = list(df.columns)
    
    # Check if all expected columns exist
    missing_cols = [col for col in expected_cols if col not in actual_cols]
    extra_cols = [col for col in actual_cols if col not in expected_cols]
    
    if not missing_cols and not extra_cols:
        print("\n✓ {}: Schema VALID".format(table_name))
    else:
        print("\n✗ {}: Schema MISMATCH".format(table_name))
        schema_valid = False
        
        if missing_cols:
            print("  Missing columns: {}".format(missing_cols))
        if extra_cols:
            print("  Extra columns: {}".format(extra_cols))

if schema_valid:
    print("\n✓ ALL SCHEMAS VALID - Data structure is consistent")
else:
    print("\n⚠ SCHEMA ISSUES FOUND - See details above")

# ============================================================================
# TASK 3: DETECT DUPLICATE RECORDS
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3: DETECT DUPLICATE RECORDS")
print("=" * 80)

# Check for duplicates in each table
print("\nDuplicate Detection Results:")

# Customers - check for duplicate emails and IDs
print("\n--- CUSTOMERS ---")
duplicate_emails = customers_df[customers_df.duplicated(subset=['email'], keep=False)]
if len(duplicate_emails) > 0:
    print("⚠ Found {} customers with duplicate emails:".format(len(duplicate_emails)))
    print(duplicate_emails[['customer_id', 'name', 'email']].head())
else:
    print("✓ No duplicate emails found")

duplicate_customer_ids = customers_df[customers_df.duplicated(subset=['customer_id'], keep=False)]
if len(duplicate_customer_ids) > 0:
    print("✗ ERROR: Found {} duplicate customer IDs (should be unique!)".format(len(duplicate_customer_ids)))
else:
    print("✓ All customer IDs are unique")


# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("DATA INGESTION COMPLETE ✓")
print("=" * 80)
print("\nSummary:")
print("✓ Task 1: All datasets read successfully")
print("✓ Task 2: Schema validation completed")
print("✓ Task 3: Duplicate detection completed")
