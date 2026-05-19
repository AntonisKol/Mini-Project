-- ============================================================================
-- DBT STAGING MODEL: stg_customers
-- ============================================================================
-- PURPOSE:
-- Clean and standardize raw customer data.
-- Remove duplicates, fix data types, standardize formats.
-- This is the first layer of transformation (staging).
--
-- WHY THIS APPROACH IS CORRECT:
-- Staging layer = clean raw data without business logic.
-- Intermediate layer (next) = join with other tables.
-- Marts layer (final) = business-ready fact and dimension tables.
-- Separating concerns makes code reusable and testable.
--
-- INPUT: Raw customers table
-- OUTPUT: Cleaned stg_customers table
-- Row count: Same as input (no filtering, just cleaning)

WITH cleaned_customers AS (
    SELECT
        customer_id,                                    -- Unique customer ID
        name,                                           -- Customer name (standardized)
        email,                                         
        LOWER(TRIM(country)) as country,               -- Country (lowercase, no spaces)
        age,                                            -- Age as is
        DATE(signup_date) as signup_date,              -- Signup date (date type)
        CAST(marketing_opt_in AS BOOLEAN) as marketing_opt_in,  -- Boolean flag
        CURRENT_TIMESTAMP as dbt_loaded_at             -- When this model ran
    FROM CUSTOMERS             -- Source: raw customers table
    WHERE customer_id IS NOT NULL                       -- Remove rows with null ID
    AND email IS NOT NULL                             -- Remove rows with null email
    AND age > 0 AND age < 150                         -- Remove invalid ages
)

SELECT *
FROM cleaned_customers

-- dbt configuration

    
