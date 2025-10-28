"""
Reddit extraction module for fetching and processing crypto-related posts and comments
"""
import os
import csv
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Set
from dotenv import load_dotenv
import praw
import pandas as pd

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

    def __init__(self):
        """Initialize Reddit API connection"""
        logger.info("Initializing Reddit API client...")

        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_SECRET')
        self.user_agent = "crypto_analysis_bot/1.0"

        # Checkpoint file path (simple JSON file to track extracted post IDs)
        self.checkpoint_file = Path("data/bronze/reddit/.checkpoint.json")

        # Validate credentials
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            logger.error("[ERROR] Missing Reddit API credentials in .env file")
            raise ValueError("Reddit API credentials are missing")

        try:
            # Authenticate using OAuth2
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                password=self.password,
                user_agent=self.user_agent,
                username=self.username,
            )
            logger.info("[OK] Reddit API client initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Reddit API client: {e}")
            raise

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
        Fetch posts from a subreddit matching the query
        
        Args:
            subreddit_name: Name of the subreddit (e.g., "CryptoCurrency")
            query: Search query (e.g., "bitcoin", "ethereum")
            limit: Maximum number of posts to fetch
            sort: Sort method ("new", "hot", "top")
        
        Returns:
            DataFrame containing posts and comments
        """
        logger.info(f"Fetching Reddit posts...")
        logger.info(f"  Subreddit: r/{subreddit_name}")
        logger.info(f"  Query: {query}")
        logger.info(f"  Limit: {limit}")
        logger.info(f"  Sort: {sort}")

        # Load checkpoint to skip already extracted posts
        extracted_ids = self._load_checkpoint()

        posts_data = []
        new_post_ids = set()
        skipped_count = 0
        start_time = datetime.now()

        try:
            # Get subreddit and search for posts
            subreddit = self.reddit.subreddit(subreddit_name)
            submissions = subreddit.search(query, sort=sort, limit=limit)

            # Process each submission
            for i, submission in enumerate(submissions, 1):
                try:
                    # Skip if already extracted
                    if submission.id in extracted_ids:
                        skipped_count += 1
                        logger.debug(f"Skipping already extracted post: {submission.id}")
                        continue

                    # Track new post ID
                    new_post_ids.add(submission.id)
                    # Extract post data
                    post_data = {
                        "submission_id": submission.id,
                        "title": submission.title,
                        "text": submission.selftext if hasattr(submission, 'selftext') else "",
                        "score": submission.score,
                        "num_comments": submission.num_comments,
                        "upvote_ratio": submission.upvote_ratio,
                        "url": submission.url,
                        "created_utc": submission.created_utc,
                        "author": str(submission.author) if submission.author else "[deleted]",
                        "subreddit": submission.subreddit.display_name,
                        "query": query,
                        "source": "reddit_post",
                        "created_datetime": datetime.fromtimestamp(submission.created_utc).isoformat() if hasattr(submission, 'created_utc') else ""
                    }
                    
                    # Extract top comments (limit to avoid memory issues)
                    comments_data = []
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list()[:20]:  # Get top 20 comments
                        if hasattr(comment, 'body'):
                            comment_data = {
                                **post_data,
                                "comment_id": comment.id,
                                "body": comment.body,
                                "comment_score": comment.score,
                                "parent_id": comment.parent_id,
                                "comment_created_utc": comment.created_utc,
                                "created_datetime": datetime.fromtimestamp(comment.created_utc).isoformat() if hasattr(comment, 'created_utc') else ""
                            }
                            comments_data.append(comment_data)
                    
                    # Store post with its comments
                    if len(comments_data) > 0:
                        posts_data.extend(comments_data)
                    else:
                        # Store post without comments
                        post_data["comment_id"] = ""
                        post_data["body"] = ""
                        post_data["comment_score"] = 0
                        post_data["parent_id"] = ""
                        post_data["comment_created_utc"] = submission.created_utc
                        posts_data.append(post_data)
                    
                    # Log progress every 25 posts
                    if i % 25 == 0:
                        logger.info(f"Progress: {i} posts processed")
                    
                except Exception as e:
                    logger.warning(f"Failed to process post: {e}")
                    continue
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"[OK] Fetched {len(posts_data)} posts/comments in {duration:.2f} seconds")
            if skipped_count > 0:
                logger.info(f"[INFO] Skipped {skipped_count} already extracted posts")

            # Save checkpoint with new post IDs
            if new_post_ids:
                self._save_checkpoint(new_post_ids)

            # Create DataFrame
            df = pd.DataFrame(posts_data)

            # Clean data
            df = self._clean_data(df)

            return df
            
        except Exception as e:
            logger.error(f"[ERROR] Error during Reddit extraction: {e}")
            return pd.DataFrame()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the fetched Reddit data
        
        Args:
            df: Raw DataFrame from Reddit
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
            
        logger.info("Cleaning Reddit data...")
        
        # Drop rows with missing titles or text
        initial_count = len(df)
        
        # Drop empty comments
        if 'body' in df.columns:
            df = df[df['body'].notna() & (df['body'] != "")]
        
        # Drop duplicate posts
        df = df.drop_duplicates(subset=['submission_id', 'comment_id'], keep='first')
        
        final_count = len(df)
        logger.info(f"[OK] Cleaned data: {initial_count} -> {final_count} records")
        
        return df
    
    def save_to_bronze(self, df: pd.DataFrame, filename: str = "reddit_posts", execution_date: datetime = None):
        """
        Save Reddit data to bronze layer as CSV with date partitioning

        Args:
            df: DataFrame with Reddit data
            filename: Base filename without extension
            execution_date: Date for partitioning (defaults to today)
        """
        if execution_date is None:
            execution_date = datetime.now()

        # Create partitioned directory structure: data/bronze/reddit/year=YYYY/month=MM/day=DD/
        year = execution_date.strftime('%Y')
        month = execution_date.strftime('%m')
        day = execution_date.strftime('%d')

        partition_path = Path(f'data/bronze/reddit/year={year}/month={month}/day={day}')
        partition_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = execution_date.strftime('%Y%m%d_%H%M%S')
        filepath = partition_path / f'{filename}_{timestamp}.csv'

        try:
            # Save as CSV
            df.to_csv(filepath, index=False, encoding='utf-8')

            logger.info(f"[OK] Saved {len(df)} Reddit posts to {filepath}")

            # Save summary
            self._save_summary(df, str(filepath))

        except Exception as e:
            logger.error(f"[ERROR] Failed to save Reddit data: {e}")
    
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
    
    # Configuration
    subreddit = os.getenv('REDDIT_SUBREDDIT', 'CryptoCurrency')
    query = os.getenv('CRYPTO_KEYWORDS', 'bitcoin').split(',')[0]  # Use first keyword
    limit = int(os.getenv('MAX_POSTS', '100'))
    
    logger.info(f"Configuration:")
    logger.info(f"  Subreddit: r/{subreddit}")
    logger.info(f"  Query: {query}")
    logger.info(f"  Limit: {limit}")
    
    try:
        # Initialize extractor
        extractor = RedditExtractor()
        
        # Fetch posts
        df = extractor.fetch_posts(
            subreddit_name=subreddit,
            query=query,
            limit=limit,
            sort="new"
        )
        
        # Save to bronze
        if not df.empty:
            extractor.save_to_bronze(df, 'reddit_posts')
            logger.info("=" * 60)
            logger.info("[OK] Reddit extraction completed successfully")
            logger.info("=" * 60)
        else:
            logger.warning("[WARN] No Reddit posts extracted")
            
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()
