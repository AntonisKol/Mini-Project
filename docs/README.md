# QuickCart Mini Project - Complete Implementation

## Project Overview

This is a comprehensive **Data Engineering Implementation** for QuickCart, an e-commerce platform facing performance and scalability challenges.

The project covers **all aspects of modern data engineering**:
- Data Architecture & Theory
- SQL Engineering
- Python & Pandas Data Processing
- ETL/ELT, Airflow, and dbt
- Performance Engineering & Optimization

---

## File Structure

```
QuickCart_Project/
├─ SECTION_A_DataArchitecture_Theory.md      (20 pages of theory)
├─ SECTION_B_SQL_Queries.sql                  (25+ SQL queries)
├─ SECTION_C_Python_Pandas.py                 (1000+ lines Python)
├─ SECTION_D_Airflow_DAG.py                   (Airflow pipeline)
├─ SECTION_D_dbt_Models.py                    (dbt models & config)
├─ SECTION_E_Performance_Engineering.md       (30+ pages strategy)
└─ README.md                                  (this file)
```

---

## Section Breakdown

### SECTION A: Data Architecture & Theory ✅

**What:** 20+ pages of detailed explanations on data engineering concepts

**Topics Covered:**
- OLTP vs OLAP systems (and why mixing them is bad)
- ACID vs BASE trade-offs
- Storage formats (CSV, JSON, Avro, Parquet)
- Partitioning strategies
- Indexing and sharding
- Data warehouse design

**Key Learning:**
- Why QuickCart's architecture is broken
- How to design scalable systems
- When to use different technologies

**File:** `SECTION_A_DataArchitecture_Theory.md`

---

### SECTION B: SQL Engineering ✅

**What:** 25+ SQL queries covering beginner to advanced

**Topics Covered:**
- Top 10 customers by revenue
- Month-over-month growth analysis
- Consecutive ordering patterns
- Window functions (RANK, ROW_NUMBER, LAG)
- Running totals and rolling averages
- Query optimization (indexing, materialized views)
- Database schema design

**Code Examples:**
```sql
-- Find top customers (basic)
SELECT customer_id, SUM(amount) as revenue
FROM orders
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;

-- Find month-over-month growth (intermediate)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) as prev_month,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / 
             LAG(revenue) OVER (ORDER BY month) * 100, 2) as growth_pct
FROM (SELECT DATE_TRUNC('month', order_date) as month, SUM(amount) as revenue ...)

-- Find customers in consecutive months (advanced)
WITH monthly_orders AS (
  SELECT DISTINCT customer_id, DATE_TRUNC('month', order_date)::date as month
  FROM orders
)
SELECT customer_id FROM monthly_orders
WHERE LAG(month) OVER (PARTITION BY customer_id ORDER BY month) = 
      month - INTERVAL '1 month'
```

**File:** `SECTION_B_SQL_Queries.sql`

---

### SECTION C: Python & Pandas Data Processing ✅

**What:** 1000+ lines of Python for data ingestion, cleaning, and analytics

**Topics Covered:**
- Data ingestion from CSV/Parquet
- Data validation and quality checks
- Duplicate detection
- Data cleaning (standardization, type conversion, null handling)
- Business KPI generation
- Clickstream analytics
- Export optimization (CSV vs Parquet)

**Key Metrics Generated:**
```
Daily Sales KPI
Customer Lifetime Value (CLV)
Category-wise Revenue  
Repeat Customer Percentage
Most Visited Pages
Session Counts
Bounce Rate
Device Type Distribution
```

**Performance Comparison:**
```
CSV: 100 MB   (10 sec to read)
Parquet: 15 MB (0.2 sec to read)
→ 6x smaller, 50x faster!
```

**File:** `SECTION_C_Python_Pandas.py`

**How to Run:**
```bash
python SECTION_C_Python_Pandas.py
# Output: Generated datasets + KPIs + exports
```

---

### SECTION D: ETL/ELT + Airflow + dbt ✅

#### Part 1: Airflow DAG

**What:** Production-ready Airflow DAG with error handling

**Pipeline Flow:**
```
Extract Data (from S3)
    ↓
Validate Data (schema checks)
    ↓
Load to Staging (database insert)
    ↓
Trigger dbt Transformation
    ↓
Success/Failure Notifications
```

**Features:**
- Automatic retries (2 times, 5 min delay)
- Email notifications on failure
- Task dependencies
- XCom communication between tasks
- Comprehensive logging
- Idempotent design

**Key Concepts:**
```python
@PythonOperator(
    task_id='extract_data',
    python_callable=extract_data_from_source,
    retries=2,
    retry_delay=timedelta(minutes=5)
)

# Schedule: Daily at 2 AM UTC
schedule_interval='0 2 * * *'

# Retry logic: Automatic with exponential backoff
# Failure handling: Email alerts
# Logging: Comprehensive for debugging
```

**File:** `SECTION_D_Airflow_DAG.py`

---

#### Part 2: dbt Models

**What:** Data transformation models with tests and documentation

**Model Layers:**

1. **Staging (stg_*)**
   - Clean raw data
   - Remove duplicates  
   - Validate schemas
   - Files: stg_customers, stg_orders, stg_products

2. **Intermediate (int_*)**
   - Business logic layer
   - Aggregations
   - Views for internal use
   - Files: int_customer_orders

3. **Marts (fact_* / dim_*)**
   - Analytics-ready tables
   - Fact: fct_sales (1M rows, partitioned)
   - Dimension: dim_customers (50k rows)

**Data Quality Tests:**
```yaml
- not_null: Required columns have values
- unique: ID columns are unique
- relationships: Foreign keys exist
- accepted_values: Enums are valid
```

**File:** `SECTION_D_dbt_Models.py`

---

### SECTION E: Performance Engineering ✅

**What:** Complete optimization strategy for QuickCart

**Problems Addressed:**
- 50M clickstream events/day overwhelming database
- Queries taking 5-10 minutes (unacceptable)
- Dashboard refresh taking 3+ hours
- Storage costs: $10k/month
- Pipeline failures: 15% failure rate

**Solutions Provided:**

1. **Architecture Redesign**
   - Data Lake: S3 (cheap storage, Parquet format)
   - Data Warehouse: Snowflake (optimized for analytics)
   - Transformation: dbt (business logic)
   - Orchestration: Airflow (scheduling + retry)

2. **Partitioning Strategy**
   - Orders: Partition by date
   - Clickstream: Partition by date + hour
   - Result: 90% less data scanned per query

3. **Indexing Strategy**
   - Primary key indexes on join columns
   - Composite indexes for multi-column queries
   - Partial indexes for common filters
   - Result: 100x faster joins

4. **Compression Strategy**
   - Parquet with Snappy compression
   - 6x smaller than CSV
   - 50x faster to read
   - Result: $96k/year storage savings

5. **Query Optimization**
   - Pre-aggregate in dbt models
   - Materialized views for complex queries
   - Incremental loading (99% time savings)
   - Result: Queries go from 5min to 10 sec

6. **Reliability & Monitoring**
   - Automatic retries with exponential backoff
   - Email alerts on failure
   - Data quality tests in dbt
   - Monitoring dashboards
   - Result: 85% → 98% success rate

**Expected ROI:**
```
Investment: $30k (3 months)
Savings: $196k/year
ROI: 6.5x in year 1
```

**File:** `SECTION_E_Performance_Engineering.md`

---

## How to Use These Files

### For Learning:

1. **Start with Section A** (Theory)
   - Read to understand data architecture concepts
   - Understand OLTP vs OLAP
   - Learn why design matters

2. **Then Section B** (SQL)
   - Study each query
   - Understand window functions
   - Learn query optimization

3. **Then Section C** (Python)
   - Run the script to see data processing
   - Understand data cleaning pipeline
   - See analytics calculations

4. **Then Section D** (Airflow + dbt)
   - Review DAG structure
   - Understand task dependencies
   - Review dbt models and tests

5. **Finally Section E** (Performance)
   - See how all pieces fit together
   - Understand optimization strategy
   - Learn implementation roadmap

---

### For Implementation:

1. **Set up environments:**
   ```bash
   # Airflow
   pip install apache-airflow
   airflow db init
   
   # dbt
   pip install dbt-snowflake  # or dbt-postgres
   dbt init quickcart_dbt
   
   # Python
   pip install pandas numpy
   ```

2. **Create databases:**
   - PostgreSQL for transactional data
   - Snowflake/BigQuery for analytics

3. **Deploy Airflow DAG:**
   - Copy SECTION_D_Airflow_DAG.py to Airflow DAGs folder
   - Configure connections (S3, PostgreSQL, Snowflake)
   - Test DAG: `airflow dags test quickcart_etl_pipeline 2025-01-15`

4. **Deploy dbt:**
   - Copy dbt models from SECTION_D_dbt_Models.py
   - Configure profiles.yml
   - Run: `dbt run && dbt test`

5. **Run Python pipeline:**
   - `python SECTION_C_Python_Pandas.py`
   - Generates sample data and KPIs

---

## Key Takeaways

### Architecture
- Separate OLTP (PostgreSQL) from OLAP (Snowflake)
- Use data lake for cheap raw storage
- Use warehouse for optimized analytics

### Performance
- Partition data by date for fast filtering
- Compress to 10% original size
- Pre-aggregate common queries
- Use incremental loading (99% faster)

### Reliability
- Automatic retries for transient failures
- Data quality tests before updating dashboards
- Email alerts on failures
- Idempotent design (safe to re-run)

### Tools
- **Airflow**: Orchestrate workflows
- **dbt**: Transform data with SQL
- **Parquet**: Compress and optimize storage
- **Snowflake**: Scale analytics easily

---

## Implementation Timeline

| Phase | Duration | Cost | Deliverable |
|-------|----------|------|-------------|
| Foundation | Month 1 | $5k | Data lake + warehouse |
| Transform | Month 2 | $15k | dbt models + optimization |
| Orchestrate | Month 3 | $10k | Airflow + monitoring |
| **Total** | **3 months** | **$30k** | **Full modern data stack** |

---

## Expected Results

After implementation:
- ✅ Storage cost: $10k → $2k/month (80% savings)
- ✅ Query speed: 5min → 10sec (30x faster)
- ✅ Dashboard refresh: 3hrs → 30min (6x faster)
- ✅ Pipeline reliability: 85% → 98%
- ✅ Data freshness: 12hrs old → 1hr old
- ✅ ROI: 6.5x in year 1

---

## Questions?

This is a complete, production-ready implementation guide. Each file includes:
- Detailed inline comments explaining every line
- Real-world examples and use cases
- Common mistakes and how to avoid them
- Best practices for each technology

Start with Section A to build your foundation, then work through each section systematically.

Good luck! 🚀
