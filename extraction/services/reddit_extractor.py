"""
Reddit extraction module for fetching and processing crypto-related posts and comments
"""
import sys
from pathlib import Path

# Add parent directory to sys.path to allow direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import logging
import json
import time
from datetime import datetime
from typing import Set, Optional
from dotenv import load_dotenv
import praw
from prawcore.exceptions import ResponseException, RequestException
import pandas as pd

# Import from extraction.models
from extraction.models.validators import RedditDataValidator
from extraction.models.exceptions import RedditValidationError
from extraction.models.config import RedditConfig
from extraction.models.exceptions import RedditConfigError
from extraction.models.exceptions import RedditAPIError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RedditExtractor:
    """Service to extract cryptocurrency data from Reddit"""

    def __init__(self, config: Optional[RedditConfig] = None):
        """
        Initialize Reddit API connection

        Args:
            config: RedditConfig instance (if None, creates default from .env)
        """
        logger.info("Initializing Reddit API client...")

        # Use provided config or create default
        self.config = config if config is not None else RedditConfig()

        # Set checkpoint file from config
        self.checkpoint_file = self.config.checkpoint_file

        try:
            # Authenticate using OAuth2
            self.reddit = praw.Reddit(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                password=self.config.password,
                user_agent=self.config.user_agent,
                username=self.config.username,
            )
            logger.info("[OK] Reddit API client initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Reddit API client: {e}")
            raise RedditConfigError(f"Failed to authenticate with Reddit API: {e}")

    def _load_checkpoint(self) -> Set[str]:
        """Load checkpoint file with already extracted post IDs"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    extracted_ids = set(data.get('extracted_post_ids', []))
                    logger.info(f"[OK] Loaded checkpoint: {len(extracted_ids)} posts already extracted")
                    return extracted_ids
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")
                return set()
        return set()

    def _save_checkpoint(self, post_ids: Set[str]):
        """Save checkpoint file with extracted post IDs"""
        try:
            # Load existing checkpoint
            existing_ids = self._load_checkpoint()
            # Merge with new IDs
            all_ids = existing_ids.union(post_ids)

            # Ensure directory exists
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

            # Save checkpoint
            with open(self.checkpoint_file, 'w') as f:
                json.dump({
                    'extracted_post_ids': list(all_ids),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
            logger.info(f"[OK] Checkpoint saved: {len(all_ids)} total posts tracked")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def fetch_posts(self,
                   subreddit_name: str = "CryptoCurrency",
                   query: str = "bitcoin",
                   limit: int = 100,
                   sort: str = "new") -> pd.DataFrame:
        """
        Fetch posts from a subreddit matching the query with retry logic

        Args:
            subreddit_name: Name of the subreddit (e.g., "CryptoCurrency")
            query: Search query (e.g., "bitcoin", "ethereum")
            limit: Maximum number of posts to fetch
            sort: Sort method ("new", "hot", "top")

        Returns:
            DataFrame containing posts and comments

        Raises:
            RedditAPIError: If API request fails after all retries
        """
        logger.info(f"Fetching Reddit posts...")
        logger.info(f"  Subreddit: r/{subreddit_name}")
        logger.info(f"  Query: {query}")
        logger.info(f"  Limit: {limit}")
        logger.info(f"  Sort: {sort}")

        # Retry logic
        for attempt in range(self.config.retry_attempts):
            try:
                return self._fetch_posts_with_retry(subreddit_name, query, limit, sort, attempt)
            except RedditAPIError as e:
                if attempt < self.config.retry_attempts - 1:
                    wait_time = self.config.retry_backoff ** attempt
                    logger.warning(f"API error (attempt {attempt + 1}/{self.config.retry_attempts}): {e}")
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.config.retry_attempts} attempts")
                    raise
            except RedditConfigError as e:
                # Fatal error - don't retry
                logger.error(f"Configuration error (fatal): {e}")
                raise

        return pd.DataFrame()

    def _fetch_posts_with_retry(self, subreddit_name: str, query: str, limit: int, sort: str, attempt: int) -> pd.DataFrame:
        """
        Internal method to fetch posts (called by fetch_posts with retry logic)
        NOTE: returns posts_df for backward compatibility, but stores separate
        posts_df and comments_df in self._last_posts_df and self._last_comments_df
        """
        extracted_ids = self._load_checkpoint()

        posts_rows = []
        comments_rows = []
        new_post_ids = set()
        skipped_count = 0
        start_time = datetime.now()

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = subreddit.search(query, sort=sort, limit=limit)

            for i, submission in enumerate(submissions, 1):
                try:
                    if submission.id in extracted_ids:
                        skipped_count += 1
                        logger.debug(f"Skipping already extracted post: {submission.id}")
                        continue

                    new_post_ids.add(submission.id)

                    # ---- Post row (one row per submission)
                    post_row = {
                        "submission_id": submission.id,
                        "title": submission.title,
                        "text": getattr(submission, 'selftext', "") or "",
                        "url": submission.url,
                        "post_author": str(submission.author) if submission.author else "[deleted]",
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "upvote_ratio": submission.upvote_ratio,
                        "subreddit": submission.subreddit.display_name,
                        "query": query,
                        "source": "reddit_post",
                        "created_utc": submission.created_utc,
                        "created_datetime": datetime.fromtimestamp(submission.created_utc).isoformat() if hasattr(submission, 'created_utc') else ""
                    }
                    posts_rows.append(post_row)

                    # ---- Comments (top 20)
                    submission.comments.replace_more(limit=0)
                    for c in submission.comments.list()[:20]:
                        if hasattr(c, "body"):
                            comments_rows.append({
                                "comment_id": c.id,
                                "submission_id": submission.id,  # FK → posts
                                "comment_author": str(getattr(c, "author", None)) if getattr(c, "author", None) else "[deleted]",
                                "comment_body": c.body,
                                "comment_score": c.score,
                                "comment_parent_id": c.parent_id,
                                "comment_created_utc": c.created_utc,
                                "created_datetime": datetime.fromtimestamp(c.created_utc).isoformat() if hasattr(c, 'created_utc') else "",
                                "subreddit": submission.subreddit.display_name,
                                "query": query,
                                "source": "reddit_comment",
                            })

                    if i % 25 == 0:
                        logger.info(f"Progress: {i} posts processed")

                except Exception as e:
                    logger.warning(f"Failed to process post: {e}")
                    continue

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"[OK] Fetched {len(posts_rows)} posts and {len(comments_rows)} comments in {duration:.2f} seconds")
            if skipped_count > 0:
                logger.info(f"[INFO] Skipped {skipped_count} already extracted posts")

            if new_post_ids:
                self._save_checkpoint(new_post_ids)

            # ---- DataFrames (separate schemas)
            posts_df = pd.DataFrame(posts_rows).drop_duplicates("submission_id") if posts_rows else pd.DataFrame()
            comments_df = pd.DataFrame(comments_rows).drop_duplicates("comment_id") if comments_rows else pd.DataFrame()

            # ---- Validation (using existing validator, with warning handling)
            try:
                if not posts_df.empty:
                    posts_df = RedditDataValidator.validate_and_clean(posts_df)
            except Exception as ve:
                logger.warning(f"[Validator] Posts validation warning: {ve}")

            try:
                if not comments_df.empty:
                    comments_df = RedditDataValidator.validate_and_clean(comments_df)
            except Exception as ve:
                logger.warning(f"[Validator] Comments validation warning: {ve}")

            # Store for save methods
            self._last_posts_df = posts_df
            self._last_comments_df = comments_df

            # Backward compatibility: return posts_df
            return posts_df

        except ResponseException as e:
            logger.error(f"[ERROR] Reddit API error: {e}")
            raise RedditAPIError(f"Reddit API returned error: {e}")

        except RequestException as e:
            logger.error(f"[ERROR] Network error: {e}")
            raise RedditAPIError(f"Network error occurred: {e}")

        except RedditValidationError as e:
            logger.error(f"[ERROR] Data validation failed: {e}")
            raise

        except Exception as e:
            logger.error(f"[ERROR] Unexpected error during extraction: {e}")
            raise RedditAPIError(f"Unexpected error: {e}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate the fetched Reddit data

        Uses RedditDataValidator for cleaning and schema validation

        Args:
            df: Raw DataFrame from Reddit

        Returns:
            Cleaned and validated DataFrame
        """
        return RedditDataValidator.validate_and_clean(df)
    
    def save_to_bronze(self, df: pd.DataFrame, filename: str = "reddit_posts", execution_date: datetime = None):
        """
        Save Reddit data to Bronze layer (one single CSV per day).
        If the file already exists for today, append new data instead of creating a new file.

        Args:
            df: DataFrame with Reddit data
            filename: Base filename without extension
            execution_date: Date for partitioning (defaults to today)
        """
        # Skip saving if DataFrame is empty
        if df.empty:
            logger.info("[INFO] No new data to save - skipping file creation")
            return

        if execution_date is None:
            execution_date = datetime.now()

        # Create partitioned directory structure: data/bronze/reddit/year=YYYY/month=MM/day=DD/
        year = execution_date.strftime('%Y')
        month = execution_date.strftime('%m')
        day = execution_date.strftime('%d')
        date_str = execution_date.strftime('%Y%m%d')

        partition_path = Path(f'data/bronze/reddit/year={year}/month={month}/day={day}')
        partition_path.mkdir(parents=True, exist_ok=True)

        # Fixed filename per day (one single file per day)
        csv_path = partition_path / f'{filename}_{date_str}.csv'
        summary_path = partition_path / f'{filename}_{date_str}_summary.json'

        try:
            # Check if file already exists for today
            file_exists = csv_path.exists()

            # Append new rows to the same CSV file
            df.to_csv(
                csv_path,
                mode='a' if file_exists else 'w',   # append if exists
                index=False,
                header=not file_exists,             # no header if appending
                encoding='utf-8'
            )

            logger.info(f"[OK] {len(df)} rows {'appended to' if file_exists else 'written to new'} {csv_path}")

            # Read full daily file to recalculate global summary
            full_df = pd.read_csv(csv_path)

            summary = {
                'total_rows': len(full_df),
                'extraction_date': datetime.now().isoformat(),
                'file_location': str(csv_path),
                'unique_submissions': full_df['submission_id'].nunique() if 'submission_id' in full_df.columns else 0,
                'average_score': full_df['score'].mean() if 'score' in full_df.columns else 0,
                'total_comments': len(full_df[full_df['body'] != ""]) if 'body' in full_df.columns else 0
            }

            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"[OK] Daily summary refreshed: {summary_path}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to save daily Reddit data: {e}")

    def save_posts_to_bronze(self, posts_df: pd.DataFrame, base_filename: str = "reddit_posts", execution_date: datetime = None):
        """
        Save Reddit posts to Bronze layer (one CSV per day with append).

        Args:
            posts_df: DataFrame with Reddit posts
            base_filename: Base filename without extension
            execution_date: Date for partitioning (defaults to today)
        """
        if execution_date is None:
            execution_date = datetime.now()

        year = execution_date.strftime('%Y')
        month = execution_date.strftime('%m')
        day = execution_date.strftime('%d')
        date_str = execution_date.strftime('%Y%m%d')

        partition_path = Path(f"data/bronze/reddit/year={year}/month={month}/day={day}")
        partition_path.mkdir(parents=True, exist_ok=True)

        csv_path = partition_path / f"{base_filename}_{date_str}.csv"
        summary_path = partition_path / f"{base_filename}_{date_str}_summary.json"

        try:
            file_exists = csv_path.exists()

            # Columns in desired order (robust if columns missing)
            cols = [
                "submission_id", "title", "text", "url",
                "post_author", "score", "num_comments", "upvote_ratio",
                "subreddit", "query", "source", "created_utc", "created_datetime"
            ]
            # Reindex/order without breaking
            posts_to_write = posts_df.reindex(columns=cols)

            posts_to_write.to_csv(
                csv_path,
                mode='a' if file_exists else 'w',
                index=False,
                header=not file_exists,
                encoding='utf-8'
            )

            logger.info(f"[OK] {len(posts_to_write)} post rows {'appended to' if file_exists else 'written to new'} {csv_path}")

            # Summary (full daily file)
            full = pd.read_csv(csv_path)
            summary = {
                "total_posts": int(len(full)),
                "extraction_date": datetime.now().isoformat(),
                "file_location": str(csv_path),
                "unique_submissions": int(full['submission_id'].nunique()) if 'submission_id' in full.columns else 0,
                "average_score": float(full['score'].mean()) if 'score' in full.columns and not full.empty else 0.0
            }
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"[OK] Posts daily summary refreshed: {summary_path}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to save posts daily data: {e}")

    def save_comments_to_bronze(self, comments_df: pd.DataFrame, base_filename: str = "reddit_comments", execution_date: datetime = None):
        """
        Save Reddit comments to Bronze layer (one CSV per day with append).

        Args:
            comments_df: DataFrame with Reddit comments
            base_filename: Base filename without extension
            execution_date: Date for partitioning (defaults to today)
        """
        if execution_date is None:
            execution_date = datetime.now()

        year = execution_date.strftime('%Y')
        month = execution_date.strftime('%m')
        day = execution_date.strftime('%d')
        date_str = execution_date.strftime('%Y%m%d')

        partition_path = Path(f"data/bronze/reddit/year={year}/month={month}/day={day}")
        partition_path.mkdir(parents=True, exist_ok=True)

        csv_path = partition_path / f"{base_filename}_{date_str}.csv"
        summary_path = partition_path / f"{base_filename}_{date_str}_summary.json"

        try:
            file_exists = csv_path.exists()

            cols = [
                "comment_id", "submission_id", "comment_author", "comment_body", "comment_score",
                "comment_parent_id", "comment_created_utc", "created_datetime",
                "subreddit", "query", "source"
            ]
            comments_to_write = comments_df.reindex(columns=cols)

            comments_to_write.to_csv(
                csv_path,
                mode='a' if file_exists else 'w',
                index=False,
                header=not file_exists,
                encoding='utf-8'
            )

            logger.info(f"[OK] {len(comments_to_write)} comment rows {'appended to' if file_exists else 'written to new'} {csv_path}")

            full = pd.read_csv(csv_path)
            summary = {
                "total_comments": int(len(full)),
                "extraction_date": datetime.now().isoformat(),
                "file_location": str(csv_path),
                "unique_submissions_ref": int(full['submission_id'].nunique()) if 'submission_id' in full.columns else 0,
                "average_comment_score": float(full['comment_score'].mean()) if 'comment_score' in full.columns and not full.empty else 0.0
            }
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"[OK] Comments daily summary refreshed: {summary_path}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to save comments daily data: {e}")

    def _save_summary(self, df: pd.DataFrame, filepath: str):
        """Save extraction summary"""
        summary = {
            'total_posts': len(df),
            'extraction_date': datetime.now().isoformat(),
            'file_location': filepath,
            'unique_submissions': df['submission_id'].nunique() if 'submission_id' in df.columns and not df.empty else 0,
            'average_score': df['score'].mean() if 'score' in df.columns and not df.empty else 0,
            'total_comments': len(df[df['body'] != ""]) if 'body' in df.columns and not df.empty else 0,
        }
        
        summary_path = filepath.replace('.csv', '_summary.json')
        
        try:
            import json
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)
            logger.info(f"[OK] Summary saved to {summary_path}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")


def main():
    """Main function to run Reddit extraction"""
    logger.info("=" * 60)
    logger.info("Starting Reddit Extraction Service")
    logger.info("=" * 60)

    try:
        config = RedditConfig()
        extractor = RedditExtractor(config)

        # fetch_posts preserves signature, but _fetch_posts_with_retry populates:
        # extractor._last_posts_df and extractor._last_comments_df
        _ = extractor.fetch_posts(
            subreddit_name=config.subreddit,
            query=config.query,
            limit=config.max_posts,
            sort="new"
        )

        posts_df = getattr(extractor, "_last_posts_df", pd.DataFrame())
        comments_df = getattr(extractor, "_last_comments_df", pd.DataFrame())

        if not posts_df.empty:
            extractor.save_posts_to_bronze(posts_df, base_filename='reddit_posts')
        else:
            logger.warning("[WARN] No Reddit posts extracted")

        if not comments_df.empty:
            extractor.save_comments_to_bronze(comments_df, base_filename='reddit_comments')
        else:
            logger.info("[INFO] No comments found (or limit=0)")

        logger.info("=" * 60)
        logger.info("[OK] Reddit extraction completed successfully")
        logger.info("=" * 60)

    except RedditConfigError as e:
        # Fatal configuration error - cannot proceed
        logger.error(f"[FATAL] Configuration error: {e}")
        logger.error("Please check your .env file and configuration")
        raise

    except RedditAPIError as e:
        # API error after all retries
        logger.error(f"[ERROR] Reddit API error after retries: {e}")
        logger.error("The extraction failed. Please try again later.")
        raise

    except RedditValidationError as e:
        # Data validation failed
        logger.error(f"[ERROR] Data validation failed: {e}")
        logger.error("Data quality issues detected. Check the logs for details.")
        raise

    except Exception as e:
        # Unexpected error
        logger.error(f"[ERROR] Unexpected fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
