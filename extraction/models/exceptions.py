"""
Custom exceptions for Reddit extraction service
"""


class RedditConfigError(Exception):
    """
    Fatal configuration error - no retry

    Raised when:
    - Missing required credentials in .env
    - Invalid configuration parameters
    - Authentication failure

    Airflow behavior: Task fails immediately (no retry)
    """
    pass


class RedditAPIError(Exception):
    """
    Recoverable API error - can retry

    Raised when:
    - Rate limit exceeded
    - Server error (5xx)
    - Network/connection issues
    - Temporary Reddit API failures

    Airflow behavior: Task retries with exponential backoff
    """
    pass


class RedditValidationError(Exception):
    """
    Data validation error - fatal

    Raised when:
    - Missing required columns in data
    - Invalid data types or formats
    - Data quality issues that cannot be fixed

    Airflow behavior: Task fails immediately (data quality issue)
    """
    pass
