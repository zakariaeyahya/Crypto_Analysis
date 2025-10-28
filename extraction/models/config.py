"""
Configuration management for Reddit extraction service
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from .exceptions import RedditConfigError

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class RedditConfig:
    """
    Centralized configuration for Reddit extraction

    Loads configuration from environment variables and provides
    validation to ensure all required settings are present.

    Attributes:
        client_id (str): Reddit API client ID
        client_secret (str): Reddit API client secret
        username (str): Reddit username
        password (str): Reddit password
        subreddit (str): Target subreddit (default: 'CryptoCurrency')
        max_posts (int): Maximum posts to fetch (default: 100)
        query (str): Search query (default: 'bitcoin')
        bronze_path (Path): Path to bronze layer directory
        checkpoint_file (Path): Path to checkpoint file
        user_agent (str): Reddit API user agent
        retry_attempts (int): Number of retry attempts for API calls
        retry_backoff (int): Exponential backoff multiplier
    """

    def __init__(self):
        """
        Load and validate configuration from environment variables

        Raises:
            RedditConfigError: If required configuration is missing or invalid
        """
        # API Credentials
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_SECRET')

        # Extraction parameters
        self.subreddit = os.getenv('REDDIT_SUBREDDIT', 'CryptoCurrency')
        self.max_posts = int(os.getenv('MAX_POSTS', '100'))
        self.query = os.getenv('CRYPTO_KEYWORDS', 'bitcoin').split(',')[0]

        # Paths
        self.bronze_path = Path('data/bronze/reddit')
        self.checkpoint_file = self.bronze_path / '.checkpoint.json'

        # API settings
        self.user_agent = "crypto_analysis_bot/1.0"
        self.retry_attempts = 3
        self.retry_backoff = 2

        # Validate configuration
        self._validate()

    def _validate(self):
        """
        Validate that required configuration is present

        Raises:
            RedditConfigError: If validation fails
        """
        # Check required credentials
        if not all([self.client_id, self.client_secret, self.username, self.password]):
            raise RedditConfigError(
                "Missing required Reddit API credentials in .env file. "
                "Required: CLIENT_ID, CLIENT_SECRET, REDDIT_USERNAME, REDDIT_SECRET"
            )

        # Validate max_posts
        if self.max_posts <= 0:
            raise RedditConfigError(f"MAX_POSTS must be positive, got: {self.max_posts}")

        logger.info(f"[OK] Configuration loaded: subreddit=r/{self.subreddit}, max_posts={self.max_posts}")

    def __repr__(self):
        """String representation (without exposing credentials)"""
        return (
            f"RedditConfig(subreddit='{self.subreddit}', "
            f"max_posts={self.max_posts}, query='{self.query}')"
        )
