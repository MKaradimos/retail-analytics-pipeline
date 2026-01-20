-- Retail Analytics Data Warehouse Schema
-- Star Schema Design with Dimension and Fact Tables

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- ========================================
-- DIMENSION TABLES
-- ========================================

-- Product Dimension
CREATE TABLE dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    unit_price NUMERIC(10, 2) NOT NULL,
    image_url VARCHAR(500),
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_category ON dim_product(category);

-- Customer Dimension
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    first_transaction_date TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_city ON dim_customer(city);
CREATE INDEX idx_customer_country ON dim_customer(country);

-- Date Dimension (pre-populated for analytics)
CREATE TABLE dim_date (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Populate date dimension (2023-2025)
INSERT INTO dim_date (date_key, year, quarter, month, month_name, week, day_of_week, day_name, is_weekend)
SELECT 
    date::date as date_key,
    EXTRACT(YEAR FROM date) as year,
    EXTRACT(QUARTER FROM date) as quarter,
    EXTRACT(MONTH FROM date) as month,
    TO_CHAR(date, 'Month') as month_name,
    EXTRACT(WEEK FROM date) as week,
    EXTRACT(DOW FROM date) as day_of_week,
    TO_CHAR(date, 'Day') as day_name,
    EXTRACT(DOW FROM date) IN (0, 6) as is_weekend
FROM generate_series('2023-01-01'::date, '2025-12-31'::date, '1 day'::interval) date;

-- ========================================
-- FACT TABLE
-- ========================================

-- Sales Fact Table
CREATE TABLE fact_sales (
    transaction_id VARCHAR(100) PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    customer_id VARCHAR(50) NOT NULL REFERENCES dim_customer(customer_id),
    transaction_timestamp TIMESTAMP NOT NULL,
    date_key DATE NOT NULL REFERENCES dim_date(date_key),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0),
    store_location VARCHAR(100),
    payment_method VARCHAR(50),
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common query patterns
CREATE INDEX idx_sales_date ON fact_sales(date_key);
CREATE INDEX idx_sales_product ON fact_sales(product_id);
CREATE INDEX idx_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_sales_timestamp ON fact_sales(transaction_timestamp);
CREATE INDEX idx_sales_location ON fact_sales(store_location);

-- ========================================
-- VIEWS FOR ANALYTICS
-- ========================================

-- Sales Summary by Product
CREATE OR REPLACE VIEW vw_product_sales_summary AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    COUNT(DISTINCT f.transaction_id) as total_transactions,
    SUM(f.quantity) as total_quantity_sold,
    SUM(f.total_amount) as total_revenue,
    AVG(f.total_amount) as avg_transaction_value,
    MAX(f.transaction_timestamp) as last_sale_date
FROM dim_product p
LEFT JOIN fact_sales f ON p.product_id = f.product_id
GROUP BY p.product_id, p.product_name, p.category;

-- Daily Sales Summary
CREATE OR REPLACE VIEW vw_daily_sales_summary AS
SELECT 
    d.date_key,
    d.year,
    d.month,
    d.month_name,
    d.day_name,
    d.is_weekend,
    COUNT(DISTINCT f.transaction_id) as total_transactions,
    COUNT(DISTINCT f.customer_id) as unique_customers,
    SUM(f.quantity) as total_items_sold,
    SUM(f.total_amount) as total_revenue,
    AVG(f.total_amount) as avg_transaction_value
FROM dim_date d
LEFT JOIN fact_sales f ON d.date_key = f.date_key
GROUP BY d.date_key, d.year, d.month, d.month_name, d.day_name, d.is_weekend
ORDER BY d.date_key DESC;

-- Customer Lifetime Value
CREATE OR REPLACE VIEW vw_customer_lifetime_value AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    c.country,
    c.first_transaction_date,
    COUNT(DISTINCT f.transaction_id) as total_transactions,
    SUM(f.total_amount) as lifetime_value,
    AVG(f.total_amount) as avg_transaction_value,
    MAX(f.transaction_timestamp) as last_purchase_date,
    CURRENT_DATE - MAX(f.date_key) as days_since_last_purchase
FROM dim_customer c
LEFT JOIN fact_sales f ON c.customer_id = f.customer_id
GROUP BY c.customer_id, c.customer_name, c.city, c.country, c.first_transaction_date;

-- ========================================
-- COMMENTS
-- ========================================

COMMENT ON TABLE dim_product IS 'Product dimension containing product master data';
COMMENT ON TABLE dim_customer IS 'Customer dimension containing customer master data';
COMMENT ON TABLE dim_date IS 'Date dimension for time-based analytics';
COMMENT ON TABLE fact_sales IS 'Sales fact table containing transaction-level data';

COMMENT ON VIEW vw_product_sales_summary IS 'Product sales performance summary';
COMMENT ON VIEW vw_daily_sales_summary IS 'Daily sales aggregations';
COMMENT ON VIEW vw_customer_lifetime_value IS 'Customer lifetime value analysis';
