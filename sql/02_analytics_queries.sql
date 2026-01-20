-- Analytics Queries for Retail Data Warehouse
-- These queries demonstrate common business intelligence use cases

-- ========================================
-- SALES PERFORMANCE ANALYTICS
-- ========================================

-- 1. Top 10 Best Selling Products by Revenue
SELECT 
    product_id,
    product_name,
    category,
    total_revenue,
    total_quantity_sold,
    total_transactions
FROM vw_product_sales_summary
WHERE total_revenue IS NOT NULL
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Sales Trend by Month (Last 12 Months)
SELECT 
    TO_CHAR(date_key, 'YYYY-MM') as month,
    SUM(total_revenue) as monthly_revenue,
    SUM(total_transactions) as monthly_transactions,
    AVG(avg_transaction_value) as avg_basket_size
FROM vw_daily_sales_summary
WHERE date_key >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY TO_CHAR(date_key, 'YYYY-MM')
ORDER BY month;

-- 3. Category Performance Analysis
SELECT 
    p.category,
    COUNT(DISTINCT f.transaction_id) as total_transactions,
    SUM(f.quantity) as total_items_sold,
    SUM(f.total_amount) as total_revenue,
    AVG(f.total_amount) as avg_transaction_value,
    COUNT(DISTINCT f.customer_id) as unique_customers
FROM dim_product p
INNER JOIN fact_sales f ON p.product_id = f.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 4. Weekend vs Weekday Sales Comparison
SELECT 
    CASE 
        WHEN is_weekend THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    COUNT(*) as number_of_days,
    SUM(total_transactions) as total_transactions,
    SUM(total_revenue) as total_revenue,
    AVG(total_revenue) as avg_daily_revenue
FROM vw_daily_sales_summary
WHERE date_key >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY is_weekend;

-- ========================================
-- CUSTOMER ANALYTICS
-- ========================================

-- 5. Top 20 Most Valuable Customers
SELECT 
    customer_id,
    customer_name,
    city,
    lifetime_value,
    total_transactions,
    avg_transaction_value,
    last_purchase_date,
    days_since_last_purchase
FROM vw_customer_lifetime_value
WHERE lifetime_value IS NOT NULL
ORDER BY lifetime_value DESC
LIMIT 20;

-- 6. Customer Segmentation by Purchase Frequency
SELECT 
    CASE 
        WHEN total_transactions = 1 THEN 'One-time'
        WHEN total_transactions BETWEEN 2 AND 5 THEN 'Occasional'
        WHEN total_transactions BETWEEN 6 AND 10 THEN 'Regular'
        ELSE 'Frequent'
    END as customer_segment,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as segment_revenue,
    AVG(lifetime_value) as avg_customer_value
FROM vw_customer_lifetime_value
WHERE lifetime_value IS NOT NULL
GROUP BY customer_segment
ORDER BY segment_revenue DESC;

-- 7. Customer Retention - Active vs Churned
SELECT 
    CASE 
        WHEN days_since_last_purchase <= 30 THEN 'Active'
        WHEN days_since_last_purchase <= 90 THEN 'At Risk'
        ELSE 'Churned'
    END as customer_status,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as total_value,
    AVG(lifetime_value) as avg_value
FROM vw_customer_lifetime_value
WHERE lifetime_value IS NOT NULL
GROUP BY customer_status;

-- ========================================
-- TIME-BASED ANALYTICS
-- ========================================

-- 8. Sales by Day of Week
SELECT 
    day_name,
    day_of_week,
    COUNT(*) as number_of_days,
    SUM(total_transactions) as total_transactions,
    SUM(total_revenue) as total_revenue,
    AVG(total_revenue) as avg_daily_revenue
FROM vw_daily_sales_summary
WHERE date_key >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY day_name, day_of_week
ORDER BY day_of_week;

-- 9. Monthly Growth Rate
WITH monthly_sales AS (
    SELECT 
        year,
        month,
        month_name,
        SUM(total_revenue) as monthly_revenue
    FROM vw_daily_sales_summary
    WHERE total_revenue IS NOT NULL
    GROUP BY year, month, month_name
)
SELECT 
    year,
    month,
    month_name,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY year, month) as prev_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year, month)) / 
        LAG(monthly_revenue) OVER (ORDER BY year, month)) * 100, 
        2
    ) as growth_rate_pct
FROM monthly_sales
ORDER BY year DESC, month DESC;

-- ========================================
-- LOCATION-BASED ANALYTICS
-- ========================================

-- 10. Store Location Performance
SELECT 
    store_location,
    COUNT(DISTINCT transaction_id) as total_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    SUM(quantity) as total_items_sold
FROM fact_sales
GROUP BY store_location
ORDER BY total_revenue DESC;

-- ========================================
-- PAYMENT METHOD ANALYTICS
-- ========================================

-- 11. Payment Method Preferences
SELECT 
    payment_method,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as pct_of_transactions
FROM fact_sales
GROUP BY payment_method
ORDER BY transaction_count DESC;

-- ========================================
-- PRODUCT ANALYTICS
-- ========================================

-- 12. Products with No Sales (Dead Stock)
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price
FROM dim_product p
LEFT JOIN fact_sales f ON p.product_id = f.product_id
WHERE f.transaction_id IS NULL
ORDER BY p.category, p.product_name;

-- 13. Product Price vs Sales Volume Analysis
SELECT 
    CASE 
        WHEN p.unit_price < 50 THEN 'Budget (<$50)'
        WHEN p.unit_price < 100 THEN 'Mid-range ($50-$100)'
        WHEN p.unit_price < 200 THEN 'Premium ($100-$200)'
        ELSE 'Luxury (>$200)'
    END as price_segment,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(DISTINCT f.transaction_id) as total_transactions,
    SUM(f.quantity) as total_quantity_sold,
    SUM(f.total_amount) as total_revenue
FROM dim_product p
LEFT JOIN fact_sales f ON p.product_id = f.product_id
GROUP BY price_segment
ORDER BY MIN(p.unit_price);

-- ========================================
-- SUMMARY DASHBOARD QUERY
-- ========================================

-- 14. Executive Summary (Last 30 Days)
SELECT 
    COUNT(DISTINCT transaction_id) as total_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_id) as products_sold,
    SUM(quantity) as total_items,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    MAX(transaction_timestamp) as last_transaction_date
FROM fact_sales
WHERE date_key >= CURRENT_DATE - INTERVAL '30 days';
