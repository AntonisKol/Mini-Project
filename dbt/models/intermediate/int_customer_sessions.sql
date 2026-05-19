-- ============================================================================
-- DBT INTERMEDIATE MODEL: int_customer_sessions
-- ============================================================================
-- PURPOSE:
-- Join sessions with customer information.
-- Understand: Which customers are browsing? From what devices? Which sources?
--
-- WHY THIS APPROACH IS CORRECT:
-- Sessions table has browsing behavior (device, source, location).
-- Customers table has customer info (age, country, signup date).
-- Joining them enables analysis: Do mobile users convert differently?
-- Do new customers browse differently than loyal customers?
--
-- INPUT: stg_sessions, stg_customers
-- OUTPUT: int_customer_sessions (one row per session with customer context)
-- Row count: Same as sessions (one session = one row)

WITH customer_sessions AS (
    SELECT
        -- Session information
        s.session_id,                                   -- Unique session ID
        s.customer_id,                                  -- Which customer
        s.start_time,                                   -- Session start time
        s.session_date,                                 -- Session date
        s.device,                                       -- Device type
        s.source,                                       -- Traffic source
        s.country as session_country,                   -- Session location
        
        -- Customer information
        c.name as customer_name,                        -- Customer name
        c.email,                                        -- Customer email
        c.country as customer_country,                  -- Customer home country
        c.age,                                          -- Customer age
        c.signup_date,                                  -- When signed up
        c.marketing_opt_in,                             -- Marketing consent
        
        -- Customer segmentation
        CASE
            WHEN c.age < 25 THEN '18-24'
            WHEN c.age < 35 THEN '25-34'
            WHEN c.age < 45 THEN '35-44'
            WHEN c.age < 55 THEN '45-54'
            ELSE '55+'
        END as age_group,                               -- Age segment
        
        CASE
            WHEN CAST((s.session_date - c.signup_date) AS INTEGER) < 30 THEN 'New'
            WHEN CAST((s.session_date - c.signup_date) AS INTEGER) < 365 THEN 'Regular'
            ELSE 'Loyal'
        END as customer_segment,                        -- Customer lifecycle
        
        -- Metadata
        CURRENT_TIMESTAMP as dbt_loaded_at             -- When this model ran
        
    FROM {{ ref('stg_sessions') }} s                   -- Reference staging sessions
    LEFT JOIN {{ ref('stg_customers') }} c             -- Left join with staging customers
        ON s.customer_id = c.customer_id                -- Match by customer ID
)

SELECT *
FROM customer_sessions

-- dbt configuration
{% if execute %}
    {{ log("Loaded " ~ this.rows ~ " customer sessions", info=true) }}
{% endif %}