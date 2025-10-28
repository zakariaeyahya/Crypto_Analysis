# Cryptocurrency Data Extraction

## 📊 Data Sources

This module enables data extraction from multiple cryptocurrency sources.

### ✅ Reddit (Operational)
- **Source**: Cryptocurrency subreddits (r/CryptoCurrency)
- **Data Type**: Posts, comments, engagement metrics
- **Format**: CSV
- **Location**: `data/bronze/reddit/year=YYYY/month=MM/day=DD/`
- **Features**:
  - Date partitioning for efficient data organization
  - Checkpoint system to prevent duplicate extractions
  - Idempotent execution (safe for Airflow DAG retries)

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

1. ✅ Reddit extraction operational
2. ✅ Date partitioning implemented
3. ✅ Checkpoint system implemented
4. ⏳ Implement Silver layer processing
5. ⏳ Implement Gold layer enrichment
6. ⏳ Fix Twitter authentication or find alternative
7. ⏳ Add more data sources
8. ⏳ Add data validation (Pydantic/Pandera)
9. ⏳ Add retry logic and error handling
10. ⏳ Create Airflow DAG configuration

## 🚀 Ready for Apache Airflow

This extraction service is designed for Apache Airflow:

- ✅ **Idempotent**: Safe to re-run with checkpoint system
- ✅ **Partitioned**: Date-based partitioning for scheduling
- ✅ **Logging**: Detailed logs for monitoring
- ✅ **Execution Date**: Supports custom execution dates
- ⏳ **Configuration**: Centralized config (to be implemented)
- ⏳ **Metrics**: Export metrics (to be implemented)
- ⏳ **Retry Logic**: Custom retry mechanism (to be implemented)

## 👥 Contribution

Branch: `feature/zakariae-twitter-extraction`
Phase: Extraction (Bronze layer with partitioning & checkpointing)
