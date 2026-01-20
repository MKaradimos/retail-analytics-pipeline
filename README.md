# 🏢 Retail Analytics Data Pipeline

A production-ready, cloud-ready data engineering project that implements a complete ETL pipeline for retail business analytics. This project demonstrates modern data engineering practices including data ingestion, validation, transformation, and warehousing.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Business Problem](#-business-problem)
- [Solution Architecture](#-solution-architecture)
- [Technical Stack](#-technical-stack)
- [Data Model](#-data-model)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Data Quality & Validation](#-data-quality--validation)
- [Analytics Capabilities](#-analytics-capabilities)
- [Future Enhancements](#-future-enhancements)

---

## 🎯 Business Problem

A retail company needs to:
- **Consolidate** data from multiple sources (APIs, CSV files)
- **Validate and clean** incoming data to ensure quality
- **Transform** raw data into business-ready formats
- **Enable analytics** for sales performance, customer behavior, and inventory management

### Business Requirements
- Real-time product data synchronization from external APIs
- Historical sales transaction processing
- Customer analytics and segmentation
- Sales trend analysis by time, location, and category
- Data quality monitoring and validation

---

## 🏗️ Solution Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   External API  │         │   CSV Files     │
│  (FakeStore)    │         │  (Sales Data)   │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │     DATA INGESTION        │
         │                           │
         ▼                           ▼
    ┌────────────────────────────────────┐
    │    Python Ingestion Service        │
    │  - API Client (requests)           │
    │  - CSV Parser (pandas)             │
    │  - Retry Logic & Error Handling    │
    └────────────┬───────────────────────┘
                 │
                 │  VALIDATION & TRANSFORMATION
                 │
                 ▼
    ┌────────────────────────────────────┐
    │    Data Validation Layer           │
    │  - Pydantic Models                 │
    │  - Business Rules Validation       │
    │  - Data Quality Checks             │
    └────────────┬───────────────────────┘
                 │
                 │  WAREHOUSING
                 │
                 ▼
    ┌────────────────────────────────────┐
    │    PostgreSQL Data Warehouse       │
    │  - Star Schema Design              │
    │  - Dimension Tables (SCD Type 1)   │
    │  - Fact Table (Transactions)       │
    │  - Pre-built Analytics Views       │
    └────────────────────────────────────┘
```

### Data Flow

1. **Extract**: Fetch products from REST API and load sales from CSV
2. **Validate**: Apply business rules and data quality checks
3. **Transform**: Convert to warehouse-ready format
4. **Load**: Insert into dimensional model
5. **Verify**: Run data quality checks

---

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.11 | ETL logic and orchestration |
| **Data Validation** | Pydantic | Schema validation and data models |
| **Database** | PostgreSQL 16 | Data warehouse |
| **API Client** | Requests | External API integration |
| **Data Processing** | Pandas | CSV processing and transformations |
| **Containerization** | Docker & Docker Compose | Environment consistency |
| **Database Admin** | pgAdmin 4 | Database management UI |
| **Logging** | Python logging | Pipeline monitoring |

---

## 📊 Data Model

### Star Schema Design

#### Dimension Tables

**dim_product** - Product Master Data
- `product_id` (PK)
- `product_name`
- `category`
- `description`
- `unit_price`
- `image_url`

**dim_customer** - Customer Master Data
- `customer_id` (PK)
- `customer_name`
- `email`
- `city`
- `country`
- `first_transaction_date`

**dim_date** - Time Dimension
- `date_key` (PK)
- `year`, `quarter`, `month`
- `week`, `day_of_week`
- `is_weekend`

#### Fact Table

**fact_sales** - Transaction-level Sales Data
- `transaction_id` (PK)
- `product_id` (FK)
- `customer_id` (FK)
- `date_key` (FK)
- `transaction_timestamp`
- `quantity`
- `unit_price`
- `total_amount`
- `store_location`
- `payment_method`

---

## 📁 Project Structure

```
retail-analytics-pipeline/
├── ingestion/                  # Data ingestion modules
│   ├── __init__.py
│   ├── api_ingestion.py       # API data fetching
│   └── csv_ingestion.py       # CSV data loading
├── transformations/            # Data transformation logic
│   ├── __init__.py
│   └── transform.py           # Transformation rules
├── sql/                        # Database scripts
│   ├── schema.sql             # DDL for warehouse
│   └── analytics_queries.sql  # Pre-built analytics
├── data/                       # Data storage
│   ├── sales_transactions.csv # Sample sales data
│   └── generate_sample_data.py
├── logs/                       # Pipeline execution logs
├── config.py                   # Configuration management
├── database.py                 # Database utilities
├── models.py                   # Pydantic validation models
├── pipeline.py                 # Main ETL orchestrator
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── Makefile                    # Common commands
├── .env.example               # Configuration template
└── README.md                  # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python 3.11+** (for local development)
- **Git**

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd retail-analytics-pipeline

# 2. One-command setup and start
make quickstart

# 3. Run the pipeline
make run
```

That's it! The pipeline will:
- ✅ Generate sample data
- ✅ Initialize the database
- ✅ Fetch products from API
- ✅ Load transactions
- ✅ Validate data quality

### Manual Setup (Alternative)

```bash
# 1. Create environment configuration
cp .env.example .env

# 2. Generate sample data
python data/generate_sample_data.py

# 3. Build and start services
docker-compose up -d

# 4. Run pipeline
docker-compose run --rm pipeline python pipeline.py
```

---

## 💻 Usage

### Common Operations

```bash
# View all available commands
make help

# Start all services
make up

# Run the ETL pipeline
make run

# View pipeline logs
make logs

# Access database shell
make psql

# Stop all services
make down

# Clean up everything
make clean
```

### Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | `localhost:5432` | User: `analytics_user`<br>Password: `analytics_pass_2024`<br>Database: `retail_analytics` |
| pgAdmin | `http://localhost:5050` | Email: `admin@analytics.com`<br>Password: `admin` |

### Running Analytics Queries

```bash
# Connect to database
make psql

# Run sample queries
\i /docker-entrypoint-initdb.d/analytics_queries.sql

# Example: Top selling products
SELECT * FROM vw_product_sales_summary ORDER BY total_revenue DESC LIMIT 10;

# Example: Daily sales trend
SELECT * FROM vw_daily_sales_summary ORDER BY date_key DESC LIMIT 30;
```

---

## ✅ Data Quality & Validation

### Validation Rules

**Product Data**
- ✓ Price must be positive
- ✓ Title cannot be empty
- ✓ Category is required
- ✓ Valid URL format for images

**Transaction Data**
- ✓ Quantity must be positive
- ✓ Amounts cannot be negative
- ✓ Valid payment method (cash, credit_card, debit_card, online)
- ✓ Date consistency checks
- ✓ Foreign key integrity

### Automated Quality Checks

The pipeline runs these checks automatically:
1. **Orphan Record Detection** - Verify referential integrity
2. **Negative Amount Validation** - Ensure no negative values
3. **Date Consistency** - Verify date_key matches timestamp
4. **Duplicate Detection** - Identify duplicate transactions

### Logging

All pipeline activities are logged:
- **Location**: `logs/pipeline_YYYYMMDD_HHMMSS.log`
- **Format**: Timestamp, Logger, Level, Message
- **Levels**: INFO (normal operations), WARNING (validation issues), ERROR (failures)

---

## 📈 Analytics Capabilities

### Pre-built Analytics Views

**vw_product_sales_summary**
- Product performance metrics
- Total revenue and quantity sold
- Transaction counts per product

**vw_daily_sales_summary**
- Daily sales aggregations
- Customer counts and basket sizes
- Weekend vs weekday comparison

**vw_customer_lifetime_value**
- Customer purchase history
- Lifetime value calculation
- Recency analysis

### Sample Insights

```sql
-- 1. Top 10 products by revenue
SELECT * FROM vw_product_sales_summary 
ORDER BY total_revenue DESC LIMIT 10;

-- 2. Monthly sales trend
SELECT 
    TO_CHAR(date_key, 'YYYY-MM') as month,
    SUM(total_revenue) as revenue
FROM vw_daily_sales_summary
GROUP BY month
ORDER BY month;

-- 3. Customer segments
SELECT 
    CASE 
        WHEN total_transactions = 1 THEN 'One-time'
        WHEN total_transactions <= 5 THEN 'Occasional'
        ELSE 'Frequent'
    END as segment,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_value
FROM vw_customer_lifetime_value
GROUP BY segment;
```

---

## 🎨 Architecture Highlights

### Scalability Considerations
- **Modular design** - Easy to add new data sources
- **Batch processing** - Configurable batch sizes
- **Connection pooling** - Efficient database connections
- **Error recovery** - Retry logic with exponential backoff

### Data Engineering Best Practices
- ✅ **Separation of concerns** - Ingestion, transformation, loading
- ✅ **Configuration management** - Environment-based config
- ✅ **Logging and monitoring** - Comprehensive logging
- ✅ **Data validation** - Pydantic models for type safety
- ✅ **Idempotency** - ON CONFLICT handling
- ✅ **Documentation** - Code comments and docstrings

---

## 🚀 Future Enhancements

### Phase 2: Cloud Migration
- [ ] Deploy to AWS/GCP/Azure
- [ ] Use cloud-native services (RDS, Cloud SQL)
- [ ] Implement S3/GCS for data lake
- [ ] Add CloudWatch/Stackdriver monitoring

### Phase 3: Advanced Features
- [ ] **Workflow Orchestration** - Apache Airflow integration
- [ ] **Data Quality Framework** - Great Expectations
- [ ] **Incremental Loading** - CDC (Change Data Capture)
- [ ] **Data Lineage** - Track data transformations
- [ ] **Real-time Processing** - Kafka/Pub-Sub integration

### Phase 4: Analytics & BI
- [ ] **Business Intelligence** - Connect Tableau/Power BI/Looker
- [ ] **Machine Learning** - Predictive analytics pipeline
- [ ] **API Layer** - REST API for data access
- [ ] **Automated Reporting** - Scheduled email reports

### Production Readiness Checklist
- [ ] Add unit tests (pytest)
- [ ] Add integration tests
- [ ] Implement CI/CD pipeline (GitHub Actions)
- [ ] Add monitoring and alerting
- [ ] Implement backup and recovery procedures
- [ ] Add performance optimization (indexes, partitioning)
- [ ] Security hardening (secrets management, encryption)
- [ ] Load testing and benchmarking

---

## 📝 Development Guide

### Adding a New Data Source

1. Create ingestion module in `ingestion/`
2. Define Pydantic model in `models.py`
3. Add transformation logic in `transformations/`
4. Update database schema if needed
5. Add to pipeline orchestration

### Adding New Analytics

1. Write SQL query in `sql/analytics_queries.sql`
2. Create view if needed in `schema.sql`
3. Document in README
4. Test with sample data

---

## 🤝 Contributing

This is a personal portfolio project. Feedback and suggestions are welcome!

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Your Name**
- Portfolio: [Your Portfolio URL]
- LinkedIn: [Your LinkedIn]
- GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- **FakeStore API** - Sample product data
- **PostgreSQL** - Powerful open-source database
- **Docker** - Containerization platform
- **Python Community** - Amazing libraries and tools

---

## 📞 Contact

For questions or feedback:
- Email: karadimosmixalis@gmail.com
- LinkedIn: [Your LinkedIn Profile]

---

**Built with ❤️ for demonstrating modern data engineering practices**
