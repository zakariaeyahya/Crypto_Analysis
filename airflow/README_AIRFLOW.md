# Apache Airflow - Crypto Analysis Pipeline

## Overview

Complete automated crypto analysis pipeline using **Apache Airflow** in a single unified DAG. Extracts Reddit cryptocurrency data, consolidates with optional Kaggle data, cleans it, creates temporal splits, and performs exploratory analysis.

**Key Features:**
- Single Unified DAG (all pipeline steps in one workflow)
- Medallion Architecture: Bronze (raw) → Silver (cleaned) → Gold (analytics)
- Automatic retries with fault tolerance
- Kaggle auto-detection (optional data source)
- Weekly EDA (Monday only)
- Complete metrics tracking

**Tech Stack:** Airflow 2.8.1 | Docker Compose | PostgreSQL | LocalExecutor | Python 3.11

---

## Architecture

### Docker Services
```
┌─────────────────────────────────────────────┐
│  PostgreSQL  │  Webserver   │  Scheduler   │
│  (Metadata)  │  (Port 8080) │  (Executor)  │
└─────────────────────────────────────────────┘
```

### Data Flow
```
Scheduler → DAG → Tasks → Scripts → CSV Files
                           ↓
           data/bronze/reddit/ | kaggle/
           data/silver/reddit/
           data/gold/eda/
```

**Note:** PostgreSQL stores ONLY Airflow metadata. Data is saved as CSV files.

---

## DAG Structure: complete_crypto_pipeline_unified

**Schedule:** Daily at 6:00 AM (`0 6 * * *`)

**Pipeline (5 Steps, 17 Tasks):**
```
START
  ↓
[1] Reddit Extraction → extract_reddit_data
  ↓
[2] Consolidation → check_bronze_data → consolidate_data → validate_master_dataset
  ↓
[3] Cleaning → clean_reddit_data → validate_cleaned_data
  ↓
[4] Temporal Splits → create_temporal_splits → validate_splits
  ↓
[5] EDA (Monday) → check_eda_schedule → run_eda_analysis → save_eda_plots
  ↓
SUCCESS → pipeline_success
```

---

## Tasks Description

### Step 1: Reddit Extraction
**`extract_reddit_data`** - Fetch r/CryptoCurrency posts (100/run), save to `data/bronze/reddit/year=YYYY/month=MM/day=DD/`

### Step 2: Data Consolidation
**`check_bronze_data`** - Branch: verify Reddit data exists, detect optional Kaggle data
**`consolidate_data`** - Merge Reddit + Kaggle, deduplicate, save to `master_dataset.csv`
**`validate_master_dataset`** - Validate schema and statistics

**Schema:** unified_id | text_content | created_date | author | source_type | source_platform | subreddit | score

### Step 3: Data Cleaning
**`clean_reddit_data`** - Remove bots/spam, filter text length, clean URLs → `cleaned_reddit_dataset.csv`
**`validate_cleaned_data`** - Check quality score and row count

### Step 4: Temporal Splits
**`create_temporal_splits`** - 30-day window: Train (70%) | Val (13%) | Test (17%)
**`validate_splits`** - Verify temporal order, no ID overlap

### Step 5: EDA Analysis
**`check_eda_schedule`** - Branch: run only on Monday
**`run_eda_analysis`** - Generate crypto trends, activity plots
**`save_eda_plots`** - Copy to `data/gold/eda/`

### Control Tasks
**`start_pipeline`** - Entry point
**`pipeline_success`** - Log metrics, create `pipeline_summary.json`
**`pipeline_failure`** - Handle errors

---

## Installation

### Prerequisites
- Docker Desktop
- Reddit API credentials: https://www.reddit.com/prefs/apps

### Setup (5 Steps)

**1. Configure `.env.airflow`:**
```bash
AIRFLOW__WEBSERVER__SECRET_KEY=<generate_with_command_below>
CLIENT_ID=your_reddit_client_id
CLIENT_SECRET=your_reddit_client_secret
REDDIT_USERNAME=your_username
REDDIT_SECRET=your_password
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**2. Build:**
```bash
docker-compose build
```

**3. Initialize database:**
```bash
docker-compose up airflow-init
```

**4. Start services:**
```bash
docker-compose up -d
```

**5. Verify:**
```bash
docker-compose ps
```

---

## Running Airflow

### Access Web UI
- URL: **http://localhost:8080**
- Login: `airflow` / `airflow`

### Activate DAG
1. Find `complete_crypto_pipeline_unified`
2. Toggle switch to **ON**
3. Runs daily at 6 AM or trigger manually

### Monitor Execution
- **Graph View**: Visual pipeline (color-coded states)
- **Task Logs**: Click task → Log tab
- **XCom**: Click task → XCom tab (view metrics)

**Task Colors:**
- 🟢 Green = Success
- 🔵 Blue = Running
- 🔴 Red = Failed
- ⚪ Gray = Pending

---

## Configuration

### Change Schedule
Edit `complete_crypto_pipeline_unified.py`:
```python
schedule_interval='0 6 * * *',  # Daily at 6 AM
```

**Examples:**
- `0 */2 * * *` - Every 2 hours
- `0 0 * * 0` - Weekly Sunday
- `*/30 * * * *` - Every 30 minutes

### Modify Retries
```python
default_args = {
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}
```

### Backfill Past Dates
```bash
docker-compose exec airflow-scheduler airflow dags backfill \
  complete_crypto_pipeline_unified \
  --start-date 2025-01-01 \
  --end-date 2025-01-10
```

---

## Monitoring

### View Logs
```bash
# Scheduler logs
docker-compose logs -f airflow-scheduler

# Webserver logs
docker-compose logs -f airflow-webserver
```

### Check Pipeline Summary
After run, check: `data/gold/pipeline_summary.json`

Contains extraction, consolidation, cleaning, splits, and EDA metrics.

### Useful Commands
```bash
# List DAGs
docker-compose exec airflow-scheduler airflow dags list

# List tasks
docker-compose exec airflow-scheduler airflow tasks list complete_crypto_pipeline_unified

# Test DAG
docker-compose exec airflow-scheduler airflow dags test complete_crypto_pipeline_unified 2025-01-22

# Check errors
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Restart services
docker-compose restart airflow-scheduler
docker-compose restart airflow-webserver

# Stop
docker-compose down

# Stop + remove data (CAUTION!)
docker-compose down -v
```

---

## Troubleshooting

### 1. DAG Not Appearing
```bash
# Check file exists
docker-compose exec airflow-scheduler ls -la /opt/airflow/dags/

# Check errors
docker-compose exec airflow-scheduler airflow dags list-import-errors

# Restart
docker-compose restart airflow-scheduler
```

### 2. Import Errors
```bash
# Check modules
docker-compose exec airflow-scheduler ls -la /opt/airflow/extraction/

# Verify PYTHONPATH
docker-compose exec airflow-scheduler python -c "import sys; print(sys.path)"

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### 3. Data Not Saved
```bash
# Check directory
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/bronze/reddit/

# Check permissions
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/
```

### 4. Placeholder Warnings
Tasks showing `⚠️ not yet implemented` are expected. Create these modules for full functionality:
- `data_consolidation/consolidate.py`
- `airflow/dags/wrappers/cleaning_wrapper.py`
- `airflow/dags/wrappers/temporal_splits_wrapper.py`
- `airflow/dags/wrappers/eda_wrapper.py`

### 5. Web UI Not Loading
```bash
# Check status
docker-compose ps

# Check logs
docker-compose logs airflow-webserver

# Restart
docker-compose restart airflow-webserver
```

---

## File Structure

```
Crypto_Analysis/
├── airflow/
│   ├── dags/
│   │   └── complete_crypto_pipeline_unified.py  ← SINGLE DAG
│   ├── logs/                                     ← Auto-generated
│   └── plugins/
├── docker/
│   ├── Dockerfile.airflow
│   └── requirements-airflow.txt
├── data/                                         ← Medallion
│   ├── bronze/reddit/                            ← Raw
│   ├── bronze/kaggle/                            ← Optional
│   ├── silver/reddit/                            ← Cleaned
│   └── gold/eda/                                 ← Analytics
├── extraction/                                   ← Extraction modules
├── docker-compose.yml
├── .env.airflow
└── README_AIRFLOW.md
```

---

## Quick Start Checklist

- [ ] Install Docker Desktop
- [ ] Get Reddit API credentials
- [ ] Edit `.env.airflow` with credentials
- [ ] Generate secret: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Build: `docker-compose build`
- [ ] Init: `docker-compose up airflow-init`
- [ ] Start: `docker-compose up -d`
- [ ] Access: http://localhost:8080 (airflow/airflow)
- [ ] Activate DAG toggle
- [ ] Trigger manual run
- [ ] Verify data in `data/bronze/reddit/`

---

## Pipeline Outputs

### Bronze Layer
`data/bronze/reddit/year=YYYY/month=MM/day=DD/*.csv` - Raw Reddit extractions

### Silver Layer
- `data/silver/reddit/cleaned_reddit_dataset.csv` - Cleaned data
- `data/silver/reddit/train_data.csv` - Training split (70%)
- `data/silver/reddit/validation_data.csv` - Validation split (13%)
- `data/silver/reddit/test_data.csv` - Test split (17%)

### Gold Layer
- `data/gold/eda/*.png` - EDA visualizations
- `data/gold/pipeline_summary.json` - Complete metrics

---

## Advanced Configuration

### Environment Variables (.env.airflow)
```bash
# Core
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False

# Database
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# Reddit API
CLIENT_ID=your_id
CLIENT_SECRET=your_secret
REDDIT_USERNAME=username
REDDIT_SECRET=password
```

### DAG Configuration
```python
default_args = {
    'owner': 'crypto-team',
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'execution_timeout': timedelta(hours=4)
}
```

---

**Author:** Zakariae
**Version:** Unified Pipeline v2.0
**Updated:** 2025-01-22
