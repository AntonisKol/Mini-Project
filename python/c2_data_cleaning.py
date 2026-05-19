import pandas as pd
import sqlite3
import os

print("=" * 80)
print("LOADING RAW DATA")
print("=" * 80)

# Get the project root directory
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, 'quickcart.db')

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Load raw data from SQLite
customers_df = pd.read_sql("SELECT * FROM customers;", conn)
orders_df = pd.read_sql("SELECT * FROM orders;", conn)
order_items_df = pd.read_sql("SELECT * FROM order_items;", conn)
products_df = pd.read_sql("SELECT * FROM products;", conn)
sessions_df = pd.read_sql("SELECT * FROM sessions;", conn)
events_df = pd.read_sql("SELECT * FROM events;", conn)
reviews_df = pd.read_sql("SELECT * FROM reviews;", conn)

print("=" * 80)
print("DATA CLEANING")
print("=" * 80)

# Clean customers: standardize country names
customers_df['country'] = (customers_df['country']
                          .str.lower()
                          .str.strip()
                          .str.title())

# Clean orders: convert timestamps
orders_df['order_time'] = pd.to_datetime(orders_df['order_time'])
orders_df['order_date'] = orders_df['order_time'].dt.date
orders_df['order_year'] = orders_df['order_time'].dt.year
orders_df['order_month'] = orders_df['order_time'].dt.month
orders_df['order_day'] = orders_df['order_time'].dt.day

# Clean events: handle missing values
events_df['qty'] = events_df['qty'].fillna(0)
events_df['amount_usd'] = events_df['amount_usd'].fillna(0)

# Clean reviews: handle missing ratings
reviews_df['rating'] = reviews_df['rating'].fillna(0)

# Remove corrupted rows
order_items_df = order_items_df[order_items_df['unit_price_usd'] > 0]
orders_df = orders_df[orders_df['total_usd'] > 0]

# Update SQLite with cleaned data
customers_df.to_sql('customers', conn, if_exists='replace', index=False)
orders_df.to_sql('orders', conn, if_exists='replace', index=False)
order_items_df.to_sql('order_items', conn, if_exists='replace', index=False)
products_df.to_sql('products', conn, if_exists='replace', index=False)
sessions_df.to_sql('sessions', conn, if_exists='replace', index=False)
events_df.to_sql('events', conn, if_exists='replace', index=False)
reviews_df.to_sql('reviews', conn, if_exists='replace', index=False)

conn.close()

print("✓ Country names standardized")
print("✓ Timestamps converted")
print("✓ Missing values handled")
print("✓ Corrupted rows removed")
print(f"✓ Database updated: {DB_PATH}")
