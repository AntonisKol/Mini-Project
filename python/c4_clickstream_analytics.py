# ============================================================================
# SECTION C - PYTHON + PANDAS DATA PROCESSING
# Q4. Clickstream Analytics
# ============================================================================
# Purpose: Analyze user behavior and website traffic patterns
# Tasks: 1. Find most visited pages
#        2. Calculate session counts
#        3. Find bounce rate
#        4. Find mobile vs desktop traffic percentage

import pandas as pd
import sqlite3

db_path = 'quickcart.db'
conn = sqlite3.connect(db_path)

print("\n✓ Connected to: {}".format(db_path))

# ============================================================================
# TASK 1: FIND MOST VISITED PAGES
# ============================================================================

print("\n" + "=" * 80)
print("TASK 1: FIND MOST VISITED PAGES")
print("=" * 80)

# Query: Count page views by page URL
most_visited_query = """
SELECT 
    product_id,
    COUNT(*) as page_views,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM events), 2) as percentage_of_total
FROM events
WHERE product_id IS NOT NULL
GROUP BY product_id
ORDER BY page_views DESC
LIMIT 20
"""

most_visited = pd.read_sql(most_visited_query, conn)

print("\nTop 20 Most Visited Pages (by product_id):")
print(most_visited)

print("\n--- Most Visited Pages Summary ---")
print("Total unique pages visited: {}".format(most_visited['product_id'].nunique()))
print("Top page views: {} views".format(most_visited['page_views'].iloc[0]))
print("Average page views: {:.0f} views".format(most_visited['page_views'].mean()))

# ============================================================================
# TASK 2: CALCULATE SESSION COUNTS
# ============================================================================

print("\n" + "=" * 80)
print("TASK 2: CALCULATE SESSION COUNTS")
print("=" * 80)

# Query: Count total sessions and events per session
# Note: Join with sessions table to get customer_id
session_query = """
SELECT 
    s.session_id,
    s.customer_id,
    COUNT(e.event_id) as events_in_session,
    COUNT(DISTINCT e.event_type) as event_types
FROM sessions s
LEFT JOIN events e ON s.session_id = e.session_id
GROUP BY s.session_id, s.customer_id
"""

sessions_data = pd.read_sql(session_query, conn)

print("\nSession Analysis (first 10 sessions):")
print(sessions_data.head(10))

print("\n--- Session Counts Summary ---")
total_sessions = len(sessions_data)
print("Total sessions: {}".format(total_sessions))
print("Total events across all sessions: {}".format(sessions_data['events_in_session'].sum()))
print("Average events per session: {:.2f}".format(sessions_data['events_in_session'].mean()))
print("Median events per session: {:.0f}".format(sessions_data['events_in_session'].median()))
print("Max events in a session: {}".format(sessions_data['events_in_session'].max()))
print("Min events in a session: {}".format(sessions_data['events_in_session'].min()))

# Distribution of session lengths
print("\n--- Session Length Distribution ---")
sessions_data['session_length_category'] = pd.cut(
    sessions_data['events_in_session'],
    bins=[0, 1, 5, 10, 20, float('inf')],
    labels=['1 event (bounce)', '2-5 events (short)', '6-10 events (medium)', '11-20 events (long)', '20+ events (very long)']
)

session_dist = sessions_data['session_length_category'].value_counts().sort_index()
print(session_dist)
# ============================================================================
# TASK 3: FIND BOUNCE RATE
# ============================================================================

print("\n" + "=" * 80)
print("TASK 3: FIND BOUNCE RATE")
print("=" * 80)

# Query: Sessions with only 1 event (bounces)
bounce_query = """
SELECT 
    session_id,
    COUNT(*) as events_count
FROM events
GROUP BY session_id
HAVING COUNT(*) = 1
"""

bounced_sessions = pd.read_sql(bounce_query, conn)

print("\nBounce Analysis:")
total_sessions_count = len(sessions_data)
bounced_count = len(bounced_sessions)
bounce_rate = (bounced_count / total_sessions_count) * 100

print("Total sessions: {}".format(total_sessions_count))
print("Bounced sessions (1 event only): {}".format(bounced_count))
print("Bounce rate: {:.2f}%".format(bounce_rate))

# Bounce rate by event type
print("\n--- Bounce Rate Analysis ---")
print("Sessions that bounced (left after 1 action): {:.2f}%".format(bounce_rate))
print("Sessions that continued (2+ actions): {:.2f}%".format(100 - bounce_rate))

# Get event types in bounced sessions
bounce_event_types_query = """
SELECT 
    event_type,
    COUNT(*) as count
FROM events
WHERE session_id IN (
    SELECT session_id FROM events GROUP BY session_id HAVING COUNT(*) = 1
)
GROUP BY event_type
ORDER BY count DESC
"""

bounce_event_types = pd.read_sql(bounce_event_types_query, conn)
print("\nMost common events in bounced sessions:")
print(bounce_event_types)

# ============================================================================
# TASK 4: FIND MOBILE VS DESKTOP TRAFFIC PERCENTAGE
# ============================================================================

print("\n" + "=" * 80)
print("TASK 4: FIND MOBILE VS DESKTOP TRAFFIC PERCENTAGE")
print("=" * 80)

# Query: Device type distribution from sessions
device_query = """
SELECT 
    device,
    COUNT(*) as session_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sessions), 2) as percentage
FROM sessions
GROUP BY device
ORDER BY session_count DESC
"""

device_distribution = pd.read_sql(device_query, conn)

print("\nDevice Type Distribution:")
print(device_distribution)

print("\n--- Traffic by Device Type ---")
for idx, row in device_distribution.iterrows():
    print("{}: {} sessions ({}%)".format(
        row['device'].capitalize(),
        row['session_count'],
        row['percentage']
    ))

# Device breakdown by events
device_events_query = """
SELECT 
    s.device,
    COUNT(e.event_id) as event_count,
    ROUND(COUNT(e.event_id) * 100.0 / (SELECT COUNT(*) FROM events), 2) as percentage_of_events
FROM sessions s
LEFT JOIN events e ON s.session_id = e.session_id
GROUP BY s.device
ORDER BY event_count DESC
"""

device_events = pd.read_sql(device_events_query, conn)

print("\n--- Traffic by Device Type (by events) ---")
for idx, row in device_events.iterrows():
    print("{}: {} events ({}%)".format(
        row['device'].capitalize(),
        row['event_count'],
        row['percentage_of_events']
    ))

# Mobile traffic analysis
mobile_sessions = device_distribution[device_distribution['device'] == 'mobile']['session_count'].sum()
desktop_sessions = device_distribution[device_distribution['device'] == 'desktop']['session_count'].sum()
tablet_sessions = device_distribution[device_distribution['device'] == 'tablet']['session_count'].sum()

total_sessions_check = mobile_sessions + desktop_sessions + tablet_sessions

print("\n--- Mobile vs Desktop Summary ---")
print("Mobile: {} sessions ({:.2f}%)".format(
    mobile_sessions,
    (mobile_sessions / total_sessions_check) * 100
))
print("Desktop: {} sessions ({:.2f}%)".format(
    desktop_sessions,
    (desktop_sessions / total_sessions_check) * 100
))
print("Tablet: {} sessions ({:.2f}%)".format(
    tablet_sessions,
    (tablet_sessions / total_sessions_check) * 100
))

# ============================================================================
# EXPORT CLICKSTREAM RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("EXPORTING CLICKSTREAM DATA")
print("=" * 80)

# Save results to CSV
most_visited.to_csv('analytics_most_visited_pages.csv', index=False)
sessions_data.to_csv('analytics_session_data.csv', index=False)
device_distribution.to_csv('analytics_device_distribution.csv', index=False)

print("\n✓ analytics_most_visited_pages.csv exported")
print("✓ analytics_session_data.csv exported")
print("✓ analytics_device_distribution.csv exported")

# ============================================================================
# CLOSE CONNECTION
# ============================================================================

conn.close()

print("\n" + "=" * 80)
print("CLICKSTREAM ANALYTICS COMPLETE ✓")
print("=" * 80)
print("\nSummary:")
print("✓ Task 1: Most visited pages identified")
print("✓ Task 2: Session counts calculated")
print("✓ Task 3: Bounce rate computed")
print("✓ Task 4: Mobile vs desktop traffic analyzed")
print("✓ Results exported to CSV files")