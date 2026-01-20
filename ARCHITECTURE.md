# 🏗️ Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
├──────────────────────┬──────────────────────────────────────────┤
│   External API       │          CSV Files                       │
│   (FakeStore)        │      (Sales Transactions)                │
│   - Products         │      - Historical Sales                  │
│   - Real-time data   │      - Batch data                        │
└──────────┬───────────┴────────────┬─────────────────────────────┘
           │                        │
           │                        │
┌──────────▼────────────────────────▼─────────────────────────────┐
│                    INGESTION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  APIIngestion                 CSVIngestion                      │
│  - HTTP requests              - Pandas DataFrame loading        │
│  - Retry logic                - Type conversion                 │
│  - Error handling             - Error handling                  │
│  - Rate limiting aware        - Batch processing                │
└──────────┬────────────────────────┬─────────────────────────────┘
           │                        │
           │                        │
┌──────────▼────────────────────────▼─────────────────────────────┐
│                  VALIDATION LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Pydantic Models                                                │
│  - ProductModel          - SalesTransactionModel                │
│  - Schema validation     - Business rules                       │
│  - Type checking         - Data quality rules                   │
│  - Custom validators     - Error collection                     │
└──────────┬────────────────────────┬─────────────────────────────┘
           │                        │
           │                        │
┌──────────▼────────────────────────▼─────────────────────────────┐
│               TRANSFORMATION LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  DataTransformer                                                │
│  - Dimension formatting      - Fact formatting                  │
│  - Business logic            - Aggregations                     │
│  - Data enrichment           - Calculations                     │
│  - Type conversions          - Denormalization                  │
└──────────┬────────────────────────┬─────────────────────────────┘
           │                        │
           │                        │
┌──────────▼────────────────────────▼─────────────────────────────┐
│                   LOADING LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│  DatabaseConnection                                             │
│  - Connection pooling        - Transaction management           │
│  - Batch inserts             - Error recovery                   │
│  - Idempotent operations     - Logging                          │
│  - Foreign key validation    - Performance optimization         │
└──────────┬────────────────────────┬─────────────────────────────┘
           │                        │
           │                        │
┌──────────▼────────────────────────▼─────────────────────────────┐
│              DATA WAREHOUSE (PostgreSQL)                        │
├─────────────────────────────────────────────────────────────────┤
│  Star Schema Design                                             │
│                                                                 │
│  Dimensions:                  Fact:                             │
│  ├─ dim_product              ├─ fact_sales                      │
│  ├─ dim_customer             │  └─ Transaction details          │
│  └─ dim_date                 │                                  │
│                                                                 │
│  Views:                                                         │
│  ├─ vw_product_sales_summary                                    │
│  ├─ vw_daily_sales_summary                                      │
│  └─ vw_customer_lifetime_value                                  │
└──────────┬──────────────────────────────────────────────────────┘
           │
           │
┌──────────▼──────────────────────────────────────────────────────┐
│                   ANALYTICS LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Pre-built Queries:                                             │
│  - Product performance      - Time-series analysis              │
│  - Customer segmentation    - Location analysis                 │
│  - Sales trends             - Payment analysis                  │
│  - Growth metrics           - Executive summaries               │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Ingestion Layer

**Purpose**: Extract data from source systems

**Components**:
- `APIIngestion`: Fetches product data from REST API
  - Implements retry logic with exponential backoff
  - Handles rate limiting
  - Validates HTTP responses
  
- `CSVIngestion`: Loads sales transactions from CSV files
  - Uses pandas for efficient parsing
  - Handles data type conversions
  - Manages file I/O errors

**Key Features**:
- Error resilience
- Logging all operations
- Configurable batch sizes

### 2. Validation Layer

**Purpose**: Ensure data quality before transformation

**Components**:
- Pydantic models define schemas and business rules
- Custom validators enforce business logic
- Validation errors are logged but don't stop pipeline

**Validation Rules**:

**Products**:
```python
- price > 0
- title not empty
- category required
- valid URL format
```

**Transactions**:
```python
- quantity > 0
- amounts >= 0
- valid payment method
- date consistency
- foreign key integrity
```

### 3. Transformation Layer

**Purpose**: Convert raw data to warehouse-ready format

**Transformations**:

**Products → dim_product**:
```
Raw API format → Dimension table format
- Extract product_id
- Normalize text fields
- Add load timestamp
```

**Transactions → fact_sales**:
```
Raw CSV format → Fact table format
- Parse dates
- Calculate date_key
- Extract dimensions
- Add metrics
```

**Customer Extraction**:
```
Transactions → dim_customer
- Group by customer_id
- Aggregate first purchase date
- Extract location
```

### 4. Loading Layer

**Purpose**: Persist data to warehouse

**Features**:
- **Idempotency**: ON CONFLICT clauses prevent duplicates
- **Transactions**: ACID compliance for data integrity
- **Batch Processing**: Efficient bulk inserts
- **Connection Management**: Context managers for cleanup

**Loading Strategy**:
```sql
-- Products (upsert)
INSERT INTO dim_product (...)
VALUES (...)
ON CONFLICT (product_id) 
DO UPDATE SET ...

-- Transactions (insert only)
INSERT INTO fact_sales (...)
VALUES (...)
ON CONFLICT (transaction_id) 
DO NOTHING
```

## Data Model

### Star Schema Design

```
         ┌─────────────────┐
         │   dim_product   │
         ├─────────────────┤
         │ product_id (PK) │
         │ product_name    │
         │ category        │
         │ unit_price      │
         └────────┬────────┘
                  │
                  │ 1:N
                  │
    ┌─────────────▼─────────────┐
    │       fact_sales          │
    ├───────────────────────────┤
    │ transaction_id (PK)       │
    │ product_id (FK) ───┐      │
    │ customer_id (FK) ──┼─┐    │
    │ date_key (FK) ─────┼─┼─┐  │
    │ quantity           │ │ │  │
    │ total_amount       │ │ │  │
    └────────────────────┘ │ │  │
                           │ │  │
          ┌────────────────┘ │  │
          │                  │  │
          │ N:1              │  │
          │                  │  │
┌─────────▼────────┐         │  │
│  dim_customer    │         │  │
├──────────────────┤         │  │
│ customer_id (PK) │         │  │
│ customer_name    │         │  │
│ city             │         │  │
│ lifetime_value   │         │  │
└──────────────────┘         │  │
                             │  │
                ┌────────────┘  │
                │               │
                │ N:1           │
                │               │
      ┌─────────▼──────┐        │
      │   dim_date     │        │
      ├────────────────┤        │
      │ date_key (PK)  │◄───────┘
      │ year           │
      │ month          │
      │ day_of_week    │
      └────────────────┘
```

### Dimension Tables

**dim_product** (Slowly Changing Dimension Type 1)
- Contains product master data
- Updated when product info changes
- Current state only (no history)

**dim_customer** (Slowly Changing Dimension Type 1)
- Customer master data
- Extracted from transactions
- Enriched with aggregated metrics

**dim_date** (Static Dimension)
- Pre-populated for 2023-2025
- Enables time-based analytics
- Includes calendar attributes

### Fact Table

**fact_sales** (Transaction Grain)
- One row per transaction
- Atomic level detail
- Links to all dimensions
- Contains metrics (quantity, amount)

## Data Flow

### Pipeline Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                               │
│    └─ Create schema, tables, indexes, views                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 2. PRODUCT DIMENSION LOAD                                       │
│    ├─ Fetch from API                                            │
│    ├─ Validate with Pydantic                                    │
│    ├─ Transform to dimension format                             │
│    └─ Upsert to dim_product                                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 3. TRANSACTION LOAD                                             │
│    ├─ Load from CSV                                             │
│    ├─ Validate with Pydantic                                    │
│    ├─ Extract customer dimension                                │
│    ├─ Insert to dim_customer                                    │
│    ├─ Transform transactions                                    │
│    └─ Insert to fact_sales                                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 4. DATA QUALITY CHECKS                                          │
│    ├─ Check for orphan records                                  │
│    ├─ Validate amounts                                          │
│    └─ Verify date consistency                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ 5. SUMMARY & LOGGING                                            │
│    ├─ Calculate statistics                                      │
│    ├─ Log execution summary                                     │
│    └─ Report errors (if any)                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack Rationale

### Python 3.11
- **Why**: Industry standard for data engineering
- **Benefits**: Rich ecosystem, excellent libraries, readability
- **Trade-offs**: Not as fast as Go/Rust for compute-heavy tasks

### PostgreSQL 16
- **Why**: Robust RDBMS with excellent OLAP capabilities
- **Benefits**: ACID compliance, JSON support, window functions
- **Trade-offs**: Not specialized for OLAP like ClickHouse

### Pydantic
- **Why**: Type safety and validation
- **Benefits**: Runtime validation, clear error messages, IDE support
- **Trade-offs**: Some performance overhead

### Docker
- **Why**: Environment consistency
- **Benefits**: Easy deployment, reproducibility, isolation
- **Trade-offs**: Additional layer of complexity

## Scalability Considerations

### Current Design (Good for)
- Up to 1M transactions per day
- Dozens of concurrent users
- ~100GB data warehouse

### To Scale Further

**Horizontal Scaling**:
```
- Use Apache Airflow for distributed task execution
- Implement partition-wise loading
- Add read replicas for queries
```

**Vertical Scaling**:
```
- Increase database instance size
- Add more memory for caching
- Use faster storage (NVMe)
```

**Cloud Migration**:
```
- Move to cloud data warehouse (Snowflake, BigQuery)
- Use managed Airflow (MWAA, Cloud Composer)
- Implement data lake (S3, GCS)
```

## Security Considerations

### Current Implementation
- Environment variables for credentials
- No hardcoded secrets
- PostgreSQL authentication

### Production Enhancements
- Use secrets manager (AWS Secrets Manager, Vault)
- Implement row-level security
- Add audit logging
- Enable SSL/TLS for connections
- Implement role-based access control

## Monitoring & Observability

### Current Implementation
- Structured logging to files
- Console output for debugging
- Basic error tracking

### Production Enhancements
- CloudWatch/Stackdriver integration
- Metrics (throughput, latency, errors)
- Alerting on failures
- Data quality dashboards
- Cost monitoring

## Future Roadmap

### Phase 1: Production Readiness
- [ ] Add comprehensive unit tests
- [ ] Implement CI/CD pipeline
- [ ] Add integration tests
- [ ] Performance benchmarking

### Phase 2: Advanced Features
- [ ] Apache Airflow orchestration
- [ ] Incremental loading / CDC
- [ ] Data lineage tracking
- [ ] Great Expectations for data quality

### Phase 3: Cloud Native
- [ ] Deploy to AWS/GCP/Azure
- [ ] Use managed services
- [ ] Implement auto-scaling
- [ ] Multi-region deployment

### Phase 4: Analytics Evolution
- [ ] Connect BI tools (Tableau, Looker)
- [ ] Machine learning pipeline
- [ ] Real-time analytics
- [ ] Self-service analytics

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Maintained By**: Project Owner
