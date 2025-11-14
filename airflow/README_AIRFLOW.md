# Apache Airflow - Crypto Data Extraction Automation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [File Structure](#file-structure)
4. [File Descriptions](#file-descriptions)
5. [Installation](#installation)
6. [Execution](#execution)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This project automates cryptocurrency data extraction from Reddit using **Apache Airflow** orchestrated by **Docker Compose**. The architecture follows the **Medallion pattern** (Bronze → Silver → Gold).

### Goals
- Automate daily Reddit posts extraction (r/CryptoCurrency)
- Ensure data quality with schema validation
- Handle errors with automatic retries
- Track metrics in Airflow UI
- Support backfill (re-extraction of past dates)

### Tech Stack
- **Apache Airflow 2.8.1** - Workflow orchestration
- **Docker Compose** - Containerization
- **PostgreSQL** - Airflow metadata storage (NOT extraction data)
- **LocalExecutor** - Task execution (simple, no Redis/Celery)
- **Python 3.11** - Development language

---

## Architecture

**Simple 3-service setup (LocalExecutor):**

```
├── postgres    - Airflow metadata database
├── webserver   - Web UI (http://localhost:8080)
└── scheduler   - DAG scheduling + task execution
```

**Data Flow:**
```
Scheduler → Execute DAGs → extraction/ modules → data/bronze/*.csv
```

**IMPORTANT:** PostgreSQL stores **ONLY Airflow metadata** (DAG runs, logs, states). Extraction data (Reddit) is stored in `data/bronze/` as CSV files.

---

## File Structure

```
Crypto_Analysis/
├── extraction/                      # Extraction modules (existing)
│   ├── models/
│   │   ├── config.py               # RedditConfig
│   │   ├── exceptions.py           # Custom exceptions
│   │   └── validators.py           # Schema validation
│   └── services/
│       ├── reddit_extractor.py     # RedditExtractor
│       └── twitter_extractor.py    # (Non-functional)
│
├── airflow/                         # Airflow configuration
│   ├── dags/
│   │   ├── reddit_extraction_dag.py     # Daily Reddit DAG
│   │   └── config/
│   │       └── dag_config.yaml          # DAG configuration
│   ├── plugins/                          # Airflow plugins (optional)
│   ├── logs/                             # Airflow logs (auto-created)
│   └── config/
│       └── airflow.cfg                   # Advanced config (optional)
│
├── docker/
│   ├── Dockerfile.airflow               # Custom Airflow image
│   └── requirements-airflow.txt         # Python dependencies
│
├── data/                                 # Extracted data (Medallion)
│   ├── bronze/                           # Raw data
│   │   └── reddit/year=YYYY/month=MM/day=DD/
│   ├── silver/                           # Cleaned data
│   └── gold/                             # Enriched data
│
├── .env                                  # Main env vars (existing)
├── .env.airflow                          # Airflow env vars
├── docker-compose.yml                    # Docker orchestration
└── README_AIRFLOW.md                     # This file
```

---

## File Descriptions

### 1. `docker/requirements-airflow.txt`

**Purpose:** Python dependencies for Airflow and extractors.

**Content:**
```txt
apache-airflow
apache-airflow-providers-postgres
praw
pandas
numpy
python-dotenv
pyyaml
psycopg2-binary
requests
pytz
```

---

### 2. `docker/Dockerfile.airflow`

**Purpose:** Custom Airflow Docker image with extraction modules.

**What it does:**
1. Start from official Airflow 2.8.1 image
2. Install gcc (for Python package compilation)
3. Install Python dependencies
4. Copy `extraction/` folder into container
5. Set PYTHONPATH to import modules

---

### 3. `.env.airflow`

**Purpose:** Environment variables for Airflow and credentials.

**Key variables:**
```bash
AIRFLOW_UID=50000
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__WEBSERVER__SECRET_KEY=<GENERATE_ME>

AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_SECRET=your_password

REDDIT_SUBREDDIT=CryptoCurrency
MAX_POSTS=100
CRYPTO_KEYWORDS=bitcoin,ethereum,crypto
```

**IMPORTANT:** Generate secret key with:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 4. `docker-compose.yml`

**Purpose:** Orchestrate 3 Docker services.

**Services:**

1. **postgres** - Airflow metadata database
   - Image: `postgres:13`
   - Volume: `postgres-db-volume`

2. **airflow-webserver** - Web UI
   - Build: `docker/Dockerfile.airflow`
   - Port: `8080`
   - Volumes: dags, logs, plugins, data, .env

3. **airflow-scheduler** - Scheduler + Executor
   - Build: `docker/Dockerfile.airflow`
   - Volumes: dags, logs, plugins, data, .env
   - Executes tasks with LocalExecutor

---

### 5. `airflow/dags/config/dag_config.yaml`

**Purpose:** Centralized DAG configuration.

**Structure:**
```yaml
default_args:
  owner: 'crypto-team'
  depends_on_past: false
  email_on_failure: false
  email_on_retry: false
  retries: 3
  retry_delay_minutes: 5
  execution_timeout_minutes: 30

reddit_extraction:
  dag_id: 'reddit_crypto_extraction'
  description: 'Daily extraction of cryptocurrency posts from r/CryptoCurrency'
  schedule_interval: '0 6 * * *'
  start_date: '2025-01-01'
  catchup: true
  max_active_runs: 1
  subreddit: 'CryptoCurrency'
  max_posts: 100
  sort_by: 'hot'
  time_filter: 'day'
  crypto_keywords:
    - 'bitcoin'
    - 'ethereum'
    - 'crypto'
    - 'cryptocurrency'
    - 'blockchain'
    - 'BTC'
    - 'ETH'
  output_format: 'csv'
  partition_by:
    - 'year'
    - 'month'
    - 'day'
  task_id: 'extract_reddit_crypto_posts'
  pool: 'default_pool'
  priority_weight: 1
```

---

### 6. `airflow/dags/reddit_extraction_dag.py`

**Purpose:** Daily Reddit extraction DAG.

**Implementation:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from extraction.models import RedditConfig
from extraction.services.reddit_extractor import RedditExtractor


def extract_reddit_data(**context):
    config = RedditConfig()
    extractor = RedditExtractor(config)

    df = extractor.fetch_posts(
        subreddit_name='CryptoCurrency',
        query='bitcoin OR ethereum',
        limit=100
    )

    extractor.save_to_bronze(df, 'reddit_posts', execution_date=context['execution_date'])
    return {'posts_extracted': len(df)}


config_path = Path(__file__).parent / 'config' / 'dag_config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

reddit_config = config['reddit_extraction']
default_args = config['default_args']
default_args['retry_delay'] = timedelta(minutes=default_args.pop('retry_delay_minutes'))

with DAG(
    dag_id=reddit_config['dag_id'],
    description=reddit_config['description'],
    schedule_interval=reddit_config['schedule_interval'],
    start_date=datetime.strptime(reddit_config['start_date'], '%Y-%m-%d'),
    catchup=reddit_config['catchup'],
    max_active_runs=reddit_config['max_active_runs'],
    default_args=default_args,
    tags=['reddit', 'crypto', 'extraction']
) as dag:

    extract_task = PythonOperator(
        task_id=reddit_config['task_id'],
        python_callable=extract_reddit_data,
        provide_context=True
    )
```

---

## Installation

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Git
- Reddit API credentials: https://www.reddit.com/prefs/apps

### Steps

**1. Configure credentials**
```bash
notepad .env.airflow

python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**2. Build Docker image**
```bash
docker-compose build
```

**3. Initialize Airflow database**
```bash
docker-compose up airflow-init
```

**4. Start services**
```bash
docker-compose up -d
```

**5. Verify services**
```bash
docker-compose ps
```

---

## Execution

### Access Airflow UI
- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### Activate DAGs
1. In Airflow UI, toggle DAGs ON
2. DAGs will run according to schedule
3. Or trigger manually: Click DAG → Trigger button

### Monitor
- **Graph view**: See task status
- **Logs**: Click task → View Logs
- **XCom**: See returned metrics

### Useful Commands
```bash
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver

docker-compose exec airflow-webserver bash

docker-compose exec airflow-scheduler airflow dags list

docker-compose exec airflow-scheduler airflow dags test reddit_crypto_extraction 2025-01-01

docker-compose restart airflow-scheduler

docker-compose down

docker-compose down -v
```

---

## Configuration

### Schedules (Cron)

Format: `minute hour day_of_month month day_of_week`

Examples:
- `0 6 * * *` - Daily at 6:00 AM
- `*/30 * * * *` - Every 30 minutes
- `0 0 1 * *` - 1st of each month at midnight

### Retries

Configured in `dag_config.yaml`:
```yaml
default_args:
  retries: 3
  retry_delay_minutes: 5
```

### Backfill

Run DAG for past dates:
```bash
docker-compose exec airflow-scheduler airflow dags backfill \
  reddit_crypto_extraction \
  --start-date 2025-01-01 \
  --end-date 2025-01-10
```

---

## Troubleshooting

### 1. DAGs not appearing in UI

**Solutions:**
```bash
docker-compose exec airflow-scheduler ls -la /opt/airflow/dags/
docker-compose exec airflow-scheduler airflow dags list
docker-compose logs airflow-scheduler | grep ERROR
docker-compose restart airflow-scheduler
```

### 2. Module not found error

**Solutions:**
```bash
docker-compose exec airflow-scheduler ls -la /opt/airflow/extraction/
docker-compose exec airflow-scheduler python -c "import sys; print(sys.path)"
docker-compose build --no-cache
docker-compose up -d
```

### 3. Data not saved

**Solutions:**
```bash
docker-compose exec airflow-scheduler ls -la /opt/airflow/data/bronze/
```

---

## Next Steps

**1. Configure credentials in `.env.airflow`**
```bash
notepad .env.airflow
```

**2. Generate secret key**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**3. Build and start**
```bash
docker-compose build
docker-compose up airflow-init
docker-compose up -d
```

**4. Access UI**
```
http://localhost:8080
Username: airflow
Password: airflow
```

**5. Activate DAG in UI and test**

---

**Author:** Zakariae
**Last Updated:** 2025-01-13
