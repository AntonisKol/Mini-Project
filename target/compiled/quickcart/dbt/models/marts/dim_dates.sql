-- ============================================================================
-- DBT MART MODEL: dim_dates (DATE DIMENSION TABLE)
-- ============================================================================
-- PURPOSE:
-- Create the date dimension table for time-based analysis.
-- One row per date with fiscal/calendar attributes.
-- Enables easy filtering and grouping by time periods.
--
-- WHY THIS APPROACH IS CORRECT:
-- Date dimensions store temporal attributes.
-- Allows queries like "sales by week" without calculating weeks.
-- Pre-calculated fiscal calendars for reporting.
-- Standard practice in data warehousing.
--
-- INPUT: None (generates dates programmatically)
-- OUTPUT: dim_dates (one row per date from 2020-2026)
-- Row count: ~2190 rows (6 years of dates)
-- Used by: All dashboards needing time-based analysis

WITH date_range AS (
    -- Generate all dates from 2020-01-01 to 2026-12-31
    SELECT DATE('2020-01-01') as date_value
    UNION ALL
    SELECT DATE(date_value, '+1 day') FROM date_range
    WHERE date_value < DATE('2026-12-31')
)

SELECT
    date_value,                                         -- Date key
    
    -- Calendar attributes
    CAST(STRFTIME('%Y', date_value) AS INTEGER) as year,      -- Year
    CAST(STRFTIME('%m', date_value) AS INTEGER) as month,     -- Month (1-12)
    CAST(STRFTIME('%d', date_value) AS INTEGER) as day,       -- Day (1-31)
    CAST(STRFTIME('%w', date_value) AS INTEGER) as day_of_week,  -- Day of week (0=Sunday)
    CAST(STRFTIME('%j', date_value) AS INTEGER) as day_of_year,  -- Day of year (1-366)
    CAST(STRFTIME('%W', date_value) AS INTEGER) as week_of_year,  -- Week number
    
    -- Quarter
    CASE
        WHEN CAST(STRFTIME('%m', date_value) AS INTEGER) IN (1,2,3) THEN 'Q1'
        WHEN CAST(STRFTIME('%m', date_value) AS INTEGER) IN (4,5,6) THEN 'Q2'
        WHEN CAST(STRFTIME('%m', date_value) AS INTEGER) IN (7,8,9) THEN 'Q3'
        ELSE 'Q4'
    END as quarter,
    
    -- Month name
    CASE CAST(STRFTIME('%m', date_value) AS INTEGER)
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        ELSE 'December'
    END as month_name,
    
    -- Day name
    CASE CAST(STRFTIME('%w', date_value) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        ELSE 'Saturday'
    END as day_name,
    
    -- Business flags
    CASE
        WHEN CAST(STRFTIME('%w', date_value) AS INTEGER) IN (0, 6) THEN 'Weekend'
        ELSE 'Weekday'
    END as weekday_flag,
    
    -- Year-month (for grouping)
    STRFTIME('%Y-%m', date_value) as year_month,
    
    -- Metadata
    CURRENT_TIMESTAMP as dbt_loaded_at
    
FROM date_range
ORDER BY date_value

-- ============================================================================
-- BUSINESS LOGIC COMMENTS
-- ============================================================================
--
-- This dimension table enables easy time-based queries:
-- 1. Sales by quarter:
--    SELECT d.quarter, SUM(f.order_total_usd)
--    FROM fct_sales f
--    JOIN dim_dates d ON f.order_date = d.date_value
--    GROUP BY d.quarter
--
-- 2. Compare weekday vs weekend sales:
--    SELECT d.weekday_flag, SUM(f.order_total_usd)
--    FROM fct_sales f
--    JOIN dim_dates d ON f.order_date = d.date_value
--    GROUP BY d.weekday_flag
--
-- 3. Sales by month name:
--    SELECT d.month_name, SUM(f.order_total_usd)
--    FROM fct_sales f
--    JOIN dim_dates d ON f.order_date = d.date_value
--    GROUP BY d.month_name
--
-- ============================================================================


    
