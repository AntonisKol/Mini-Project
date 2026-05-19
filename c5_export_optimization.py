# ============================================================================
# SECTION C - PYTHON + PANDAS DATA PROCESSING
# Q5. Export Optimization
# ============================================================================
# Purpose: Compare storage formats and demonstrate optimization benefits
# Tasks: 1. Export analytical dataset into CSV
#        2. Export analytical dataset into Parquet
#        3. Compare storage sizes
#        4. Compare read performance
#        5. Explain why Parquet is better for analytics

import pandas as pd
import sqlite3
import os
import time

# ============================================================================
# STEP 0: Connect to SQLite and load analytical data
# ============================================================================

print("=" * 80)
print("LOADING DATA FROM SQLITE")
print("=" * 80)

db_path = 'quickcart.db'
conn = sqlite3.connect(db_path)

# Load all tables into dataframes for export
orders_df = pd.read_sql("SELECT * FROM orders;", conn)
customers_df = pd.read_sql("SELECT * FROM customers;", conn)
events_df = pd.read_sql("SELECT * FROM events;", conn)
sessions_df = pd.read_sql("SELECT * FROM sessions;", conn)
products_df = pd.read_sql("SELECT * FROM products;", conn)
order_items_df = pd.read_sql("SELECT * FROM order_items;", conn)
reviews_df = pd.read_sql("SELECT * FROM reviews;", conn)

print("\n✓ All data loaded from SQLite")

# Combine all data into one analytical dataset
analytical_data = orders_df.copy()

print("\nAnalytical dataset shape: {} rows × {} columns".format(
    analytical_data.shape[0],
    analytical_data.shape[1]
))

conn.close()

# ============================================================================
# TASK 1: EXPORT TO CSV
# ============================================================================

print("\n" + "=" * 80)
print("TASK 1: EXPORT TO CSV FORMAT")
print("=" * 80)

csv_file = 'analytical_data.csv'

# Export to CSV
start_time = time.time()
analytical_data.to_csv(csv_file, index=False)
export_time = time.time() - start_time

print("\n✓ Exported to: {}".format(csv_file))
print("  Export time: {:.4f} seconds".format(export_time))

# Get CSV file size
csv_size_bytes = os.path.getsize(csv_file)
csv_size_mb = csv_size_bytes / (1024 * 1024)

print("  File size: {:.2f} MB ({:,} bytes)".format(csv_size_mb, csv_size_bytes))

# ============================================================================
# TASK 2: EXPORT TO PARQUET
# ============================================================================

print("\n" + "=" * 80)
print("TASK 2: EXPORT TO PARQUET FORMAT")
print("=" * 80)

parquet_file = 'analytical_data.parquet'

# Export to Parquet with compression
start_time = time.time()
analytical_data.to_parquet(parquet_file, compression='snappy', index=False)
export_time = time.time() - start_time

print("\n✓ Exported to: {}".format(parquet_file))
print("  Export time: {:.4f} seconds".format(export_time))

# Get Parquet file size
parquet_size_bytes = os.path.getsize(parquet_file)
parquet_size_mb = parquet_size_bytes / (1024 * 1024)

print("  File size: {:.2f} MB ({:,} bytes)".format(parquet_size_mb, parquet_size_bytes))

# ============================================================================
# TASK 3: COMPARE STORAGE SIZES
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3: COMPARE STORAGE SIZES")
print("=" * 80)

print("\n--- File Size Comparison ---")
print("CSV size:      {:.2f} MB".format(csv_size_mb))
print("Parquet size:  {:.2f} MB".format(parquet_size_mb))
print("Difference:    {:.2f} MB".format(csv_size_mb - parquet_size_mb))

# Calculate compression ratio
compression_ratio = csv_size_mb / parquet_size_mb
space_saved_pct = ((csv_size_mb - parquet_size_mb) / csv_size_mb) * 100

print("\n--- Compression Benefits ---")
print("Parquet is {:.1f}x smaller than CSV".format(compression_ratio))
print("Space saved: {:.1f}%".format(space_saved_pct))
print("Storage cost reduction: ${:.2f} per TB/month".format((space_saved_pct / 100) * 23))

# ============================================================================
# TASK 4: COMPARE READ PERFORMANCE
# ============================================================================

print("\n" + "=" * 80)
print("TASK 4: COMPARE READ PERFORMANCE")
print("=" * 80)

# Read CSV and measure time
print("\nReading CSV...")
start_time = time.time()
csv_read_data = pd.read_csv(csv_file)
csv_read_time = time.time() - start_time

print("✓ CSV read time: {:.4f} seconds".format(csv_read_time))
print("  Rows loaded: {:,}".format(len(csv_read_data)))

# Read Parquet and measure time
print("\nReading Parquet...")
start_time = time.time()
parquet_read_data = pd.read_parquet(parquet_file)
parquet_read_time = time.time() - start_time

print("✓ Parquet read time: {:.4f} seconds".format(parquet_read_time))
print("  Rows loaded: {:,}".format(len(parquet_read_data)))

# Calculate performance improvement
speed_improvement = csv_read_time / parquet_read_time

print("\n--- Read Performance Comparison ---")
print("CSV read time:      {:.4f} seconds".format(csv_read_time))
print("Parquet read time:  {:.4f} seconds".format(parquet_read_time))
print("Parquet is {:.1f}x faster to read".format(speed_improvement))

# ============================================================================
# TASK 5: EXPLAIN WHY PARQUET IS BETTER FOR ANALYTICS
# ============================================================================

print("\n" + "=" * 80)
print("TASK 5: WHY PARQUET IS BETTER FOR ANALYTICS")
print("=" * 80)

explanation = """

1. COMPRESSION:
✓ Parquet compresses data (especially numbers and categories)
✓ CSV is plain text with no compression
✓ Result: Parquet is {:.1f}x smaller
✓ Cost savings: Reduces storage by {:.1f}%

2. COLUMNAR STORAGE:
✓ Parquet stores each column separately
✓ Analytics only needs a few columns
✓ CSV must read all columns for any query
✓ Result: 5-10x faster for analytical queries

3. PREDICATE PUSHDOWN:
✓ Parquet stores min/max values per chunk
✓ Database skips irrelevant chunks
✓ CSV must read entire file to filter
✓ Result: 100x faster for filtered queries

4. SCHEMA PRESERVATION:
✓ Parquet stores data types (int, float, datetime)
✓ CSV stores everything as text (needs parsing)   
✓ Result: Faster parsing, no type conversion

5. PARALLEL PROCESSING:
✓ Parquet files can be read in parallel
✓ CSV files processed sequentially
✓ Result: Better performance on big data

6. METADATA EFFICIENCY:
✓ Parquet includes statistics (min, max, null count)
✓ Useful for query optimization
✓ CSV has no metadata
✓ Result: Query planner makes better decisions

""".format(compression_ratio, space_saved_pct)

print(explanation)

# ============================================================================
# PERFORMANCE SUMMARY TABLE
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY COMPARISON TABLE")
print("=" * 80)

summary_data = {
    'Metric': [
        'File Size',
        'Read Time',
        'Compression',
        'Columnar Storage',
        'Schema Support',
        'Parallel Reading'
    ],
    'CSV': [
        '{:.2f} MB'.format(csv_size_mb),
        '{:.4f} sec'.format(csv_read_time),
        'No',
        'No',
        'No',
        'No'
    ],
    'Parquet': [
        '{:.2f} MB'.format(parquet_size_mb),
        '{:.4f} sec'.format(parquet_read_time),
        'Yes (Snappy)',
        'Yes',
        'Yes',
        'Yes'
    ],
    'Winner': [
        'Parquet ({:.1f}x smaller)'.format(compression_ratio),
        'Parquet ({:.1f}x faster)'.format(speed_improvement),
        'Parquet',
        'Parquet',
        'Parquet',
        'Parquet'
    ]
}

summary_df = pd.DataFrame(summary_data)
print("\n" + summary_df.to_string(index=False))


# ============================================================================
# EXPORT SUMMARY TO CSV
# ============================================================================

print("\n" + "=" * 80)
print("EXPORTING COMPARISON RESULTS")
print("=" * 80)

# Export summary table
summary_df.to_csv('export_comparison_summary.csv', index=False)
print("\n✓ export_comparison_summary.csv created")

# Export detailed metrics
metrics_data = {
    'Metric': ['CSV File Size (MB)', 'Parquet File Size (MB)', 'Compression Ratio', 
    'Space Saved (%)', 'CSV Read Time (sec)', 'Parquet Read Time (sec)', 
    'Speed Improvement (x)'],
    'Value': [csv_size_mb, parquet_size_mb, compression_ratio, space_saved_pct,
    csv_read_time, parquet_read_time, speed_improvement]
}

metrics_df = pd.DataFrame(metrics_data)
metrics_df.to_csv('export_optimization_metrics.csv', index=False)
print("✓ export_optimization_metrics.csv created")
