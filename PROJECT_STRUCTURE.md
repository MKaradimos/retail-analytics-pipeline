# 📂 Project Structure - Visual Guide

## Complete Project Tree

```
retail-analytics-pipeline/
│
├── 📄 README.md                          # Main documentation (START HERE!)
├── 📄 ARCHITECTURE.md                    # Detailed architecture docs
├── 📄 PROJECT_CHECKLIST.md               # Readiness checklist
├── 📄 ΠΑΡΑΔΟΣΗ.md                        # Greek delivery guide
├── 📄 LICENSE                            # MIT License
│
├── ⚙️ Configuration Files
│   ├── .env.example                      # Environment template
│   ├── requirements.txt                  # Python dependencies
│   ├── config.py                         # Configuration management
│   ├── Makefile                          # Common commands
│   └── setup.sh                          # Quick start script
│
├── 🐳 Docker Files
│   ├── Dockerfile                        # Python app container
│   ├── docker-compose.yml                # Multi-service orchestration
│   └── .dockerignore                     # Docker ignore rules
│
├── 🐍 Core Python Modules
│   ├── pipeline.py                       # 🎯 MAIN ORCHESTRATOR
│   ├── database.py                       # Database utilities
│   └── models.py                         # Pydantic validation models
│
├── 📁 ingestion/                         # DATA INGESTION LAYER
│   ├── __init__.py
│   ├── api_ingestion.py                  # API client (REST)
│   └── csv_ingestion.py                  # CSV loader (Pandas)
│
├── 📁 transformations/                   # TRANSFORMATION LAYER
│   ├── __init__.py
│   └── transform.py                      # Business logic & transformations
│
├── 📁 sql/                               # DATABASE LAYER
│   ├── schema.sql                        # DDL: Tables, indexes, views (280 lines)
│   └── analytics_queries.sql             # 14 pre-built queries (200+ lines)
│
├── 📁 data/                              # DATA FILES
│   ├── sales_transactions.csv            # Sample data (500 transactions)
│   └── generate_sample_data.py           # Data generator script
│
├── 📁 docs/                              # DOCUMENTATION
│   └── interview_preparation.docx        # Interview prep guide
│
├── 📁 logs/                              # LOGS (auto-generated)
│   └── pipeline_YYYYMMDD_HHMMSS.log      # Execution logs
│
└── .gitignore                            # Git ignore rules
```

---

## File Purposes - Quick Reference

### 🎯 Critical Files (Must Know)

| File | Purpose | For Interview |
|------|---------|---------------|
| `README.md` | Complete project documentation | Show first - explains everything |
| `pipeline.py` | Main ETL orchestrator | Core logic - walk through this |
| `models.py` | Data validation models | Show data quality approach |
| `sql/schema.sql` | Data warehouse DDL | Explain star schema here |

### 📊 Data Flow Through Files

```
1. Data Sources
   ↓
2. ingestion/api_ingestion.py     ← Fetch from API
   ingestion/csv_ingestion.py     ← Load from CSV
   ↓
3. models.py                      ← Validate with Pydantic
   ↓
4. transformations/transform.py   ← Apply business logic
   ↓
5. database.py                    ← Load to warehouse
   ↓
6. sql/schema.sql                 ← Store in tables
   ↓
7. sql/analytics_queries.sql      ← Analyze data
```

---

## Module Dependencies

```
pipeline.py
    ├── imports config.py
    ├── imports database.py
    ├── imports ingestion/
    │   ├── api_ingestion.py
    │   │   └── imports models.py
    │   └── csv_ingestion.py
    │       └── imports models.py
    └── imports transformations/
        └── transform.py
```

---

## Execution Flow (What Happens When You Run)

```
$ make run
    │
    ├── 1. Reads config.py                    (DB credentials, API URLs)
    │
    ├── 2. Executes pipeline.py
    │   │
    │   ├── Step 1: Initialize Database
    │   │   └── Runs sql/schema.sql           (Creates tables, views)
    │   │
    │   ├── Step 2: Load Products
    │   │   ├── api_ingestion.py              (Fetch from FakeStore API)
    │   │   ├── models.py                     (Validate with ProductModel)
    │   │   ├── transform.py                  (Transform to dim format)
    │   │   └── database.py                   (Insert to dim_product)
    │   │
    │   ├── Step 3: Load Transactions
    │   │   ├── csv_ingestion.py              (Load from CSV)
    │   │   ├── models.py                     (Validate with TransactionModel)
    │   │   ├── transform.py                  (Extract customers & transform)
    │   │   └── database.py                   (Insert to dim_customer, fact_sales)
    │   │
    │   ├── Step 4: Validate Data Quality
    │   │   └── database.py                   (Run quality checks)
    │   │
    │   └── Step 5: Generate Summary
    │       └── Log statistics and results
    │
    └── 3. Writes to logs/pipeline_*.log      (All execution details)
```

---

## Docker Compose Services

```
docker-compose.yml orchestrates:

┌─────────────────────────────────────────────────────────┐
│  Service: postgres                                      │
│  ├── Image: postgres:16-alpine                          │
│  ├── Purpose: Data warehouse                            │
│  └── Port: 5432                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Service: pipeline                                      │
│  ├── Build: Dockerfile                                  │
│  ├── Purpose: ETL application                           │
│  └── Runs: pipeline.py                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Service: pgadmin                                       │
│  ├── Image: dpage/pgadmin4                             │
│  ├── Purpose: Database management UI                    │
│  └── Port: 5050 → http://localhost:5050                │
└─────────────────────────────────────────────────────────┘
```

---

## Code Statistics by File

| File | Lines | Purpose |
|------|-------|---------|
| `sql/schema.sql` | 280 | Database DDL |
| `sql/analytics_queries.sql` | 200+ | Analytics queries |
| `pipeline.py` | 270 | Main orchestrator |
| `api_ingestion.py` | 130 | API client |
| `csv_ingestion.py` | 120 | CSV loader |
| `transform.py` | 150 | Transformations |
| `database.py` | 80 | DB utilities |
| `models.py` | 90 | Validation models |
| `generate_sample_data.py` | 140 | Data generator |
| **TOTAL** | **~1,800** | **Complete project** |

---

## File Groups by Concern

### 📥 Ingestion Layer
- `ingestion/api_ingestion.py`
- `ingestion/csv_ingestion.py`

### ✅ Validation Layer
- `models.py`

### 🔄 Transformation Layer
- `transformations/transform.py`

### 💾 Storage Layer
- `database.py`
- `sql/schema.sql`

### 📊 Analytics Layer
- `sql/analytics_queries.sql`

### 🎭 Orchestration Layer
- `pipeline.py`

### ⚙️ Configuration Layer
- `config.py`
- `.env.example`

### 🐳 Infrastructure Layer
- `Dockerfile`
- `docker-compose.yml`

### 📚 Documentation Layer
- `README.md`
- `ARCHITECTURE.md`
- `docs/interview_preparation.docx`

---

## Which Files to Show in Interview?

### Must Show (Top 3)
1. **README.md** - "This explains the entire project"
2. **pipeline.py** - "This is the main orchestrator"
3. **sql/schema.sql** - "This is the data model"

### Should Show (if asked)
4. **models.py** - For data validation questions
5. **api_ingestion.py** - For API integration questions
6. **analytics_queries.sql** - For analytics questions

### Can Reference (if needed)
7. **docker-compose.yml** - For containerization questions
8. **ARCHITECTURE.md** - For deep technical discussions

---

## Quick Commands Reference

```bash
# See all files
ls -la

# See Python files only
find . -name "*.py"

# See SQL files only
find . -name "*.sql"

# Count lines of code
find . -name "*.py" -o -name "*.sql" | xargs wc -l

# View project tree
make help  # Shows all available commands
```

---

## Development Workflow

```
1. Clone/Download Project
   ↓
2. Run setup.sh (or make quickstart)
   ↓
3. Edit .env if needed
   ↓
4. Run make run
   ↓
5. Check logs/
   ↓
6. Query database (make psql)
   ↓
7. View results in pgAdmin
```

---

## Testing Workflow

```
1. Generate fresh data
   python data/generate_sample_data.py
   ↓
2. Clean database
   make down && make up
   ↓
3. Run pipeline
   make run
   ↓
4. Verify results
   make psql
   SELECT COUNT(*) FROM fact_sales;
```

---

**Remember**: This structure follows **separation of concerns** - each file/folder has ONE clear purpose. Perfect for explaining in interviews! 🎯
