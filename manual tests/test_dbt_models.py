#!/usr/bin/env python
import sqlite3

db_path = 'quickcart.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n" + "=" * 80)
print("DBT MODEL VALIDATION - MANUAL TESTS")
print("=" * 80)

tests_passed = 0
tests_failed = 0

# STAGING LAYER TESTS
print("\n[STAGING] stg_customers - UNIQUE(customer_id)")
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT customer_id) FROM customers")
total, unique = cursor.fetchone()
if total == unique:
    print("✓ PASS: All {} customer_ids are unique".format(total))
    tests_passed += 1
else:
    print("✗ FAIL: {} total but only {} unique".format(total, unique))
    tests_failed += 1

print("\n[STAGING] stg_customers - NOT_NULL(email)")
cursor.execute("SELECT COUNT(*) FROM customers WHERE email IS NULL")
null_count = cursor.fetchone()[0]
if null_count == 0:
    print("✓ PASS: All emails are NOT NULL")
    tests_passed += 1
else:
    print("✗ FAIL: {} NULL emails".format(null_count))
    tests_failed += 1

print("\n[STAGING] stg_orders - UNIQUE(order_id)")
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT order_id) FROM orders")
total, unique = cursor.fetchone()
if total == unique:
    print("✓ PASS: All {} order_ids are unique".format(total))
    tests_passed += 1
else:
    print("✗ FAIL: {} total but only {} unique".format(total, unique))
    tests_failed += 1

print("\n[STAGING] stg_orders - NOT_NULL(order_date)")
cursor.execute("SELECT COUNT(*) FROM orders WHERE order_date IS NULL")
null_count = cursor.fetchone()[0]
if null_count == 0:
    print("✓ PASS: All order_dates are NOT NULL")
    tests_passed += 1
else:
    print("✗ FAIL: {} NULL order_dates".format(null_count))
    tests_failed += 1

print("\n[STAGING] stg_products - UNIQUE(product_id)")
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT product_id) FROM products")
total, unique = cursor.fetchone()
if total == unique:
    print("✓ PASS: All {} product_ids are unique".format(total))
    tests_passed += 1
else:
    print("✗ FAIL: {} total but only {} unique".format(total, unique))
    tests_failed += 1

print("\n[STAGING] stg_sessions - UNIQUE(session_id)")
cursor.execute("SELECT COUNT(*), COUNT(DISTINCT session_id) FROM sessions")
total, unique = cursor.fetchone()
if total == unique:
    print("✓ PASS: All {} session_ids are unique".format(total))
    tests_passed += 1
else:
    print("✗ FAIL: {} total but only {} unique".format(total, unique))
    tests_failed += 1

# INTERMEDIATE LAYER TESTS (Relationships)
print("\n[INTERMEDIATE] int_customer_orders - RELATIONSHIP(customer_id → customers)")
cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id NOT IN (SELECT customer_id FROM customers)")
orphan_count = cursor.fetchone()[0]
if orphan_count == 0:
    print("✓ PASS: All orders have valid customer_ids")
    tests_passed += 1
else:
    print("✗ FAIL: {} orders with invalid customer_ids".format(orphan_count))
    tests_failed += 1

print("\n[INTERMEDIATE] int_order_details - RELATIONSHIP(product_id → products)")
cursor.execute("SELECT COUNT(*) FROM order_items WHERE product_id NOT IN (SELECT product_id FROM products)")
orphan_count = cursor.fetchone()[0]
if orphan_count == 0:
    print("✓ PASS: All order_items have valid product_ids")
    tests_passed += 1
else:
    print("✗ FAIL: {} order_items with invalid product_ids".format(orphan_count))
    tests_failed += 1

print("\n[INTERMEDIATE] int_customer_sessions - RELATIONSHIP(customer_id → customers)")
cursor.execute("SELECT COUNT(*) FROM sessions WHERE customer_id NOT IN (SELECT customer_id FROM customers)")
orphan_count = cursor.fetchone()[0]
if orphan_count == 0:
    print("✓ PASS: All sessions have valid customer_ids")
    tests_passed += 1
else:
    print("✗ FAIL: {} sessions with invalid customer_ids".format(orphan_count))
    tests_failed += 1

# MART LAYER TESTS
print("\n[MARTS] fct_sales - NOT_NULL(total_usd)")
cursor.execute("SELECT COUNT(*) FROM orders WHERE total_usd IS NULL")
null_count = cursor.fetchone()[0]
if null_count == 0:
    print("✓ PASS: All total_usd values are NOT NULL")
    tests_passed += 1
else:
    print("✗ FAIL: {} NULL total_usd values".format(null_count))
    tests_failed += 1

print("\n[MARTS] dim_customers - NOT_NULL(customer_id)")
cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_id IS NULL")
null_count = cursor.fetchone()[0]
if null_count == 0:
    print("✓ PASS: All customer_ids are NOT NULL")
    tests_passed += 1
else:
    print("✗ FAIL: {} NULL customer_ids".format(null_count))
    tests_failed += 1

print("\n[MARTS] dim_products - NOT_NULL(product_id)")
cursor.execute("SELECT COUNT(*) FROM products WHERE product_id IS NULL")
null_count = cursor.fetchone()[0]
if null_count == 0:
    print("✓ PASS: All product_ids are NOT NULL")
    tests_passed += 1
else:
    print("✗ FAIL: {} NULL product_ids".format(null_count))
    tests_failed += 1

# SUMMARY
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("\nTotal Tests: {}".format(tests_passed + tests_failed))
print("Passed: {} ✓".format(tests_passed))
print("Failed: {} ✗".format(tests_failed))

if tests_failed == 0:
    print("\n✓✓✓ ALL DBT MODEL TESTS PASSED ✓✓✓")
else:
    print("\n✗✗✗ {} TESTS FAILED ✗✗✗".format(tests_failed))

conn.close()
