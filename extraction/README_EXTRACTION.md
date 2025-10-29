# Cryptocurrency Data Extraction

## 📊 Data Sources

This module enables data extraction from multiple cryptocurrency sources with production-ready features.

### ✅ Reddit (Operational)
- **Source**: Cryptocurrency subreddits (r/CryptoCurrency)
- **Data Type**: Posts, comments, engagement metrics
- **Format**: CSV
- **Location**: `data/bronze/reddit/year=YYYY/month=MM/day=DD/`
- **Features**:
  - Date partitioning for efficient data organization
  - Checkpoint system to prevent duplicate extractions
  - Idempotent execution (safe for Airflow DAG retries)
  - Centralized configuration management
  - Schema validation before saving
  - Automatic retry logic with exponential backoff
  - Custom error handling (recoverable vs fatal errors)

### ⚠️ Twitter (Non-Functional)
- **Status**: Twitter API requires paid access (API v2)
- **Issue**: 401 Unauthorized - Invalid credentials
- **Alternative Solution**: Test data available
- **Location**: `data/bronze/twitter/`

## 🏗️ Data Architecture (Medallion)

```
data/
├── bronze/              # Bronze Layer: Raw data
│   ├── reddit/         # Reddit data (CSV) with date partitioning
│   │   └── year=YYYY/
│   │       └── month=MM/
│   │           └── day=DD/
│   │               └── reddit_posts_*.csv
│   └── twitter/        # Twitter data (CSV)
├── silver/             # Silver Layer: Cleaned data (to be implemented)
│   ├── reddit/
│   └── twitter/
└── gold/               # Gold Layer: Enriched data (to be implemented)
```

### Bronze Layer
- **Content**: Raw data extracted from APIs
- **Format**: CSV with date partitioning (`year=YYYY/month=MM/day=DD/`)
- **No transformation**: Data as-is from source
- **Checkpoint**: `.checkpoint.json` tracks extracted post IDs

### Silver Layer
- **Content**: Cleaned and validated data (to be implemented)
- **Format**: CSV/Parquet
- **Transformations**: Cleaning, deduplication, validation

### Gold Layer
- **Content**: Enriched and aggregated data (to be implemented)
- **Format**: Optimized Parquet
- **Usage**: Ready for visualization and ML

## 📦 Module Architecture

The extraction service is organized into modular components for better maintainability and reusability:

```
extraction/
├── models/                    # Core models and utilities
│   ├── __init__.py           # Package exports
│   ├── config.py             # RedditConfig - Configuration management
│   ├── exceptions.py         # Custom exceptions (Fatal vs Recoverable)
│   └── validators.py         # RedditDataValidator - Schema validation
│
├── services/                  # Extraction services
│   ├── __init__.py
│   ├── reddit_extractor.py   # RedditExtractor - Main orchestration
│   └── twitter_extractor.py  # Twitter extraction (non-functional)
│
└── views/                     # Future: API views/endpoints
```

### Module Descriptions

#### **extraction/models/config.py**
- **RedditConfig**: Centralized configuration management
- Loads settings from `.env` file
- Validates configuration on initialization
- Provides default values for optional settings
- Can be passed to extractors for custom configuration

```python
from extraction.models import RedditConfig

# Create config from .env
config = RedditConfig()

# Access configuration
print(config.subreddit)    # 'CryptoCurrency'
print(config.max_posts)    # 100
```

#### **extraction/models/exceptions.py**
- **RedditConfigError**: Fatal configuration errors (no retry)
- **RedditAPIError**: Recoverable API errors (can retry)
- **RedditValidationError**: Data validation errors (fatal)

These exceptions help Airflow decide when to retry tasks:
- `RedditConfigError` → Task fails immediately
- `RedditAPIError` → Task retries with backoff
- `RedditValidationError` → Task fails (data quality issue)

#### **extraction/models/validators.py**
- **RedditDataValidator**: Schema validation and data cleaning
- Validates required columns exist
- Checks data types and formats
- Removes invalid rows with warnings
- Ensures data quality before saving to bronze layer

```python
from extraction.models import RedditDataValidator

# Validate and clean data
df_clean = RedditDataValidator.validate_and_clean(df_raw)
```

#### **extraction/services/reddit_extractor.py**
- **RedditExtractor**: Main orchestration service
- Manages Reddit API connection
- Implements checkpoint system
- Handles retry logic with exponential backoff
- Saves data with date partitioning
- Uses validators and config from models

## 🚀 Usage

### Reddit Extraction

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run extraction
python extraction/services/reddit_extractor.py
```

**Configuration in `.env`**:
```env
# Reddit API
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_SECRET=your_password

# Configuration
REDDIT_SUBREDDIT=CryptoCurrency
MAX_POSTS=100
CRYPTO_KEYWORDS=bitcoin,ethereum
```

### Twitter Extraction (Non-Functional)

```powershell
# Note: Requires valid API credentials
python extraction/services/twitter_extractor.py
```

**Issue**: Twitter API requires paid access and provided credentials are invalid (401 error).

**Alternative Solution**: Use test data if available.

## 📁 Extracted Files Structure

### Reddit

**Partitioned Structure** (New):
```
data/bronze/reddit/year=2025/month=10/day=27/reddit_posts_20251027_163945.csv
data/bronze/reddit/year=2025/month=10/day=27/reddit_posts_20251027_163945_summary.json
data/bronze/reddit/.checkpoint.json  # Tracks extracted post IDs
```

**CSV Columns**:
- `submission_id`: Post ID
- `title`: Post title
- `text`: Post content
- `body`: Comment content
- `score`: Post score
- `num_comments`: Number of comments
- `upvote_ratio`: Upvote ratio
- `author`: Author
- `subreddit`: Subreddit name
- `created_datetime`: Creation date
- `source`: Data source
- `comment_id`: Comment ID
- `comment_score`: Comment score
- `parent_id`: Parent comment/post ID
- `comment_created_utc`: Comment creation timestamp

**Checkpoint File** (`.checkpoint.json`):
```json
{
  "extracted_post_ids": ["id1", "id2", "..."],
  "last_updated": "2025-10-27T16:00:00"
}
```

### Twitter
```
data/bronze/twitter/twitter_tweets_YYYYMMDD_HHMMSS.csv
data/bronze/twitter/twitter_tweets_YYYYMMDD_HHMMSS_summary.json
```

**Note**: Twitter extraction currently unavailable.

## 🛠️ Available Services

### `reddit_extractor.py`
- ✅ Extract Reddit posts and comments
- ✅ Automatic data cleaning
- ✅ Date partitioning (year/month/day)
- ✅ Checkpoint system for idempotent execution
- ✅ CSV save to bronze/reddit with partitions
- ✅ Detailed logging
- ✅ Skip already extracted posts (prevents duplicates)

**Key Features**:
- **Partitioning**: Data organized by `year=YYYY/month=MM/day=DD/`
- **Checkpointing**: Tracks extracted `submission_id` to avoid re-extraction
- **Idempotent**: Safe to re-run without creating duplicates
- **Airflow-Ready**: Supports DAG retries and backfills

### `twitter_extractor.py`
- ⚠️ Requires valid API credentials
- ⚠️ Currently non-functional (401 Unauthorized)
- CSV format in bronze/twitter

## 📊 Extraction Statistics

The `_summary.json` files contain:
- Total number of posts/tweets
- Extraction date
- Aggregated statistics (likes, retweets, etc.)
- File metadata
- Unique submissions count
- Average score
- Total comments

## 🔧 Dependencies

```
tweepy          # Twitter API (if functional)
praw            # Reddit API
pandas          # Data processing
python-dotenv   # Configuration
```

## 🔄 Checkpoint System

The checkpoint system ensures idempotent extractions:

1. **Before extraction**: Load `.checkpoint.json` to get already extracted post IDs
2. **During extraction**: Skip posts that are already in checkpoint
3. **After extraction**: Save new post IDs to checkpoint
4. **Benefits**:
   - Prevents duplicate data
   - Safe for Airflow DAG retries
   - Efficient incremental loading
   - Reduces API calls

**Example Log Output**:
```
[OK] Loaded checkpoint: 150 posts already extracted
Progress: 25 posts processed
[INFO] Skipped 15 already extracted posts
[OK] Checkpoint saved: 165 total posts tracked
```

## 📅 Date Partitioning

Data is partitioned using Hive-style partitioning:

**Benefits**:
- Efficient data queries (filter by date)
- Easy data lifecycle management
- Compatible with Spark/Hive
- Supports incremental processing
- Ready for Apache Airflow scheduling

**Partition Format**: `year=YYYY/month=MM/day=DD/`

**Example**:
```python
# Save with specific execution date
extractor.save_to_bronze(df, 'reddit_posts', execution_date=datetime(2025, 10, 27))
# Creates: data/bronze/reddit/year=2025/month=10/day=27/reddit_posts_*.csv
```

## 🔁 Automatic Retry Logic

The extractor implements automatic retry with exponential backoff for recoverable errors:

**Configuration** (in `RedditConfig`):
- `retry_attempts`: 3 (default)
- `retry_backoff`: 2 (exponential multiplier)

**Retry Behavior**:
```
Attempt 1: Immediate
Attempt 2: Wait 2 seconds (2^0)
Attempt 3: Wait 4 seconds (2^1)
Attempt 4: Wait 8 seconds (2^2)
```

**When Retries Happen**:
- ✅ Rate limit errors
- ✅ Network/connection issues
- ✅ Server errors (5xx)
- ✅ Temporary Reddit API failures

**When Retries DON'T Happen**:
- ❌ Configuration errors (missing credentials)
- ❌ Authentication failures
- ❌ Data validation errors

**Example Log Output**:
```
[WARNING] API error (attempt 1/3): Rate limit exceeded
[INFO] Retrying in 2 seconds...
[WARNING] API error (attempt 2/3): Rate limit exceeded
[INFO] Retrying in 4 seconds...
[OK] Fetched 100 posts/comments in 15.23 seconds
```

## ⚠️ Error Handling

Custom exceptions help distinguish between fatal and recoverable errors:

### **RedditConfigError** (Fatal - No Retry)
**When raised**:
- Missing credentials in `.env`
- Invalid configuration values
- Authentication failures

**Airflow behavior**: Task fails immediately

**Example**:
```python
RedditConfigError: Missing required Reddit API credentials in .env file.
Required: CLIENT_ID, CLIENT_SECRET, REDDIT_USERNAME, REDDIT_SECRET
```

### **RedditAPIError** (Recoverable - Retry)
**When raised**:
- Rate limit exceeded
- Network/connection issues
- Server errors (5xx)
- Temporary API failures

**Airflow behavior**: Task retries with exponential backoff

**Example**:
```python
RedditAPIError: Reddit API returned error: 429 Too Many Requests
```

### **RedditValidationError** (Fatal - No Retry)
**When raised**:
- Missing required columns
- Invalid data types
- Data quality issues

**Airflow behavior**: Task fails (data quality problem)

**Example**:
```python
RedditValidationError: Missing required columns: ['submission_id', 'created_utc']
```

## ✅ Schema Validation

Data is validated before saving to bronze layer using `RedditDataValidator`:

**Required Columns**:
- `submission_id`
- `title`
- `created_utc`
- `author`
- `subreddit`

**Validations Performed**:
1. **Column existence**: Check all required columns present
2. **Null values**: Remove rows with null `submission_id`
3. **Data types**: Ensure `created_utc` is numeric
4. **Format validation**: Validate `submission_id` is alphanumeric
5. **Duplicate removal**: Drop duplicate posts/comments

**Example Log Output**:
```
[INFO] Validating data schema...
[WARNING] Found 3 null submission_ids, removing...
[WARNING] Removing 2 rows with invalid timestamps
[WARNING] Found 1 invalid submission_id formats, removing...
[OK] Schema validation passed: 194 valid records
```

**Benefits**:
- Ensures data quality in bronze layer
- Detects issues before they propagate to silver/gold
- Provides clear warnings about data problems
- Prevents corrupted data from entering pipeline

## ⚙️ Centralized Configuration

Configuration is managed through `RedditConfig` class:

**Environment Variables** (`.env`):
```env
# Reddit API Credentials
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_SECRET=your_password

# Extraction Parameters
REDDIT_SUBREDDIT=CryptoCurrency
MAX_POSTS=100
CRYPTO_KEYWORDS=bitcoin,ethereum
```

**Configuration Class**:
```python
from extraction.models import RedditConfig

# Create config (loads from .env)
config = RedditConfig()

# Access configuration
print(config.subreddit)         # 'CryptoCurrency'
print(config.max_posts)         # 100
print(config.retry_attempts)    # 3
print(config.checkpoint_file)   # Path to .checkpoint.json

# Pass to extractor
extractor = RedditExtractor(config)
```

**Benefits**:
- Single source of truth for configuration
- Validation on initialization
- Easy to test with custom configs
- Airflow DAGs can pass custom configurations

## ⚠️ Limitations

1. **Twitter API**: Requires paid subscription for API v2 access
2. **Rate Limits**:
   - Reddit: 60 requests/minute
   - Twitter: Limited by subscription plan
3. **Data**: Only recent data available
4. **Checkpoint**: Uses local JSON file (not distributed)

## 📝 Logs

All operations are logged to:
- **Console**: Real-time display
- **File**: `extraction.log`

**Log Levels**:
- `INFO`: Normal operations
- `WARNING`: Skipped/failed posts
- `ERROR`: Critical errors

## 🎯 Next Steps

### ✅ Completed
1. ✅ Reddit extraction operational
2. ✅ Date partitioning implemented (Hive-style)
3. ✅ Checkpoint system implemented
4. ✅ Modular architecture (models/services separation)
5. ✅ Centralized configuration (RedditConfig)
6. ✅ Schema validation (RedditDataValidator)
7. ✅ Retry logic with exponential backoff
8. ✅ Custom error handling (Fatal vs Recoverable)

### ⏳ Remaining Tasks
1. ⏳ Implement Silver layer processing
2. ⏳ Implement Gold layer enrichment
3. ⏳ Fix Twitter authentication or find alternative
4. ⏳ Add more data sources
5. ⏳ Add metrics export for monitoring
6. ⏳ Create Airflow DAG configuration files
7. ⏳ Add unit tests for all modules

## 🚀 Ready for Apache Airflow

This extraction service is **production-ready** for Apache Airflow:

### Core Features
- ✅ **Idempotent**: Safe to re-run with checkpoint system
- ✅ **Partitioned**: Date-based partitioning for scheduling
- ✅ **Logging**: Detailed logs for monitoring
- ✅ **Execution Date**: Supports custom execution dates
- ✅ **Configuration**: Centralized config with validation
- ✅ **Retry Logic**: Automatic retry with exponential backoff
- ✅ **Error Handling**: Custom exceptions (Fatal vs Recoverable)
- ✅ **Schema Validation**: Data quality checks before saving
- ✅ **Modular Design**: Clean separation of concerns

### Airflow Integration Benefits

**Task Retries**:
- `RedditAPIError` → Airflow retries task automatically
- `RedditConfigError` → Airflow fails task immediately
- `RedditValidationError` → Airflow fails task (data quality)

**Configuration Management**:
```python
# In Airflow DAG
from extraction.models import RedditConfig
from extraction.services.reddit_extractor import RedditExtractor

# Create custom config for DAG
config = RedditConfig()
extractor = RedditExtractor(config)

# Run extraction with execution date
df = extractor.fetch_posts(
    subreddit_name=config.subreddit,
    query=config.query,
    limit=config.max_posts
)
extractor.save_to_bronze(df, execution_date=context['execution_date'])
```

**What's Still Needed for Airflow**:
- ⏳ DAG file (`dags/reddit_extraction_dag.py`)
- ⏳ Airflow operators/tasks definition
- ⏳ Metrics export for Airflow UI
- ⏳ Airflow configuration file (`config.yaml`)

## 👥 Contribution

Branch: `feature/zakariae-twitter-extraction`
Phase: Extraction (Bronze layer - Production Ready)
Status: Ready for Airflow DAG creation
