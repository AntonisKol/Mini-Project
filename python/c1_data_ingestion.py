import pandas as pd
import sqlite3
import os

print("=" * 80)
print("TASK 1: READING ALL DATASETS")
print("=" * 80)

# Get the project root directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'quickcart.db')
CSV_DIR = os.path.join(PROJECT_DIR, 'data')

# Load all CSV files
customers_df = pd.read_csv(os.path.join(CSV_DIR, 'customers.csv'))
orders_df = pd.read_csv(os.path.join(CSV_DIR, 'orders.csv'))
order_items_df = pd.read_csv(os.path.join(CSV_DIR, 'order_items.csv'))
products_df = pd.read_csv(os.path.join(CSV_DIR, 'products.csv'))
sessions_df = pd.read_csv(os.path.join(CSV_DIR, 'sessions.csv'))
events_df = pd.read_csv(os.path.join(CSV_DIR, 'events.csv'))
reviews_df = pd.read_csv(os.path.join(CSV_DIR, 'reviews.csv'))

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Load into SQLite
customers_df.to_sql('customers', conn, if_exists='replace', index=False)
orders_df.to_sql('orders', conn, if_exists='replace', index=False)
order_items_df.to_sql('order_items', conn, if_exists='replace', index=False)
products_df.to_sql('products', conn, if_exists='replace', index=False)
sessions_df.to_sql('sessions', conn, if_exists='replace', index=False)
events_df.to_sql('events', conn, if_exists='replace', index=False)
reviews_df.to_sql('reviews', conn, if_exists='replace', index=False)

conn.close()

print(f"✓ Customers: {len(customers_df)} rows")
print(f"✓ Orders: {len(orders_df)} rows")
print(f"✓ Order items: {len(order_items_df)} rows")
print(f"✓ Products: {len(products_df)} rows")
print(f"✓ Sessions: {len(sessions_df)} rows")
print(f"✓ Events: {len(events_df)} rows")
print(f"✓ Reviews: {len(reviews_df)} rows")
print(f"✓ Database saved: {DB_PATH}")
