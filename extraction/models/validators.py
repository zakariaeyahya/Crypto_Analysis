"""
Data validation utilities for Reddit extraction
"""
import logging
import pandas as pd
from .exceptions import RedditValidationError

logger = logging.getLogger(__name__)


class RedditDataValidator:
    """
    Validator for Reddit data schema and quality

    Validates that extracted Reddit data meets required standards:
    - Required columns exist
    - Data types are correct
    - Values are in valid formats
    - No critical data quality issues
    """

    # Required columns for Reddit posts
    REQUIRED_COLUMNS = ['submission_id', 'title', 'created_utc', 'author', 'subreddit']

    @staticmethod
    def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate data schema before saving to bronze layer

        Checks:
        1. Required columns exist
        2. Data types are correct (submission_id not null, created_utc numeric)
        3. Formats are valid (submission_id alphanumeric)
        4. Removes invalid rows with warnings

        Args:
            df: DataFrame to validate

        Returns:
            Validated DataFrame with invalid rows removed

        Raises:
            RedditValidationError: If critical validation fails (missing columns)
        """
        if df.empty:
            return df

        logger.info("Validating data schema...")

        # Check if required columns exist
        missing_columns = [col for col in RedditDataValidator.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise RedditValidationError(f"Missing required columns: {missing_columns}")

        # Validate data types and formats
        try:
            df = RedditDataValidator._validate_submission_ids(df)
            df = RedditDataValidator._validate_timestamps(df)
            df = RedditDataValidator._validate_id_format(df)

            logger.info(f"[OK] Schema validation passed: {len(df)} valid records")
            return df

        except Exception as e:
            raise RedditValidationError(f"Schema validation failed: {e}")

    @staticmethod
    def _validate_submission_ids(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate submission_id column (should not be null)

        Args:
            df: DataFrame to validate

        Returns:
            DataFrame with null submission_ids removed
        """
        null_ids = df['submission_id'].isnull().sum()
        if null_ids > 0:
            logger.warning(f"Found {null_ids} null submission_ids, removing...")
            df = df[df['submission_id'].notna()]
        return df

    @staticmethod
    def _validate_timestamps(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate created_utc column (should be numeric timestamp)

        Args:
            df: DataFrame to validate

        Returns:
            DataFrame with invalid timestamps removed
        """
        # Check if created_utc is numeric
        if not pd.api.types.is_numeric_dtype(df['created_utc']):
            logger.warning("created_utc is not numeric, attempting conversion...")
            df['created_utc'] = pd.to_numeric(df['created_utc'], errors='coerce')

        # Remove rows with invalid created_utc
        invalid_timestamps = df['created_utc'].isnull().sum()
        if invalid_timestamps > 0:
            logger.warning(f"Removing {invalid_timestamps} rows with invalid timestamps")
            df = df[df['created_utc'].notna()]

        return df

    @staticmethod
    def _validate_id_format(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate submission_id format (should be alphanumeric)

        Args:
            df: DataFrame to validate

        Returns:
            DataFrame with invalid submission_id formats removed
        """
        # Check submission_id format (alphanumeric + underscore)
        valid_pattern = r'^[a-zA-Z0-9_]+$'
        invalid_ids = df[~df['submission_id'].astype(str).str.match(valid_pattern)]

        if len(invalid_ids) > 0:
            logger.warning(f"Found {len(invalid_ids)} invalid submission_id formats, removing...")
            df = df[df['submission_id'].astype(str).str.match(valid_pattern)]

        return df

    @staticmethod
    def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate Reddit data (combines cleaning + validation)

        Args:
            df: Raw DataFrame from Reddit

        Returns:
            Cleaned and validated DataFrame
        """
        if df.empty:
            return df

        logger.info("Cleaning Reddit data...")
        initial_count = len(df)

        # Drop empty comments
        if 'body' in df.columns:
            df = df[df['body'].notna() & (df['body'] != "")]

        # Drop duplicate posts
        df = df.drop_duplicates(subset=['submission_id', 'comment_id'], keep='first')

        final_count = len(df)
        logger.info(f"[OK] Cleaned data: {initial_count} -> {final_count} records")

        # Validate schema
        df = RedditDataValidator.validate_schema(df)

        return df
