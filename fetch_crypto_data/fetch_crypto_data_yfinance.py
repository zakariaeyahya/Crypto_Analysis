"""
Script to fetch historical cryptocurrency price data from Yahoo Finance.

This script fetches full historical data for BTC, ETH, and SOL since 2014,
transforms it into daily OHLC format, and saves to CSV files.
"""

import yfinance as yf
import pandas as pd
import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_config() -> Dict:
    """
    Load configuration from config_yfinance.json file.

    Returns:
        Dictionary containing configuration settings
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config_yfinance.json")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        raise


def fetch_crypto_data(ticker: str, start_date: str) -> Optional[pd.DataFrame]:
    """
    Fetch historical cryptocurrency data from Yahoo Finance.

    Args:
        ticker: Yahoo Finance ticker symbol (e.g., 'BTC-USD')
        start_date: Start date in YYYY-MM-DD format

    Returns:
        DataFrame with historical data, or None if failed
    """
    try:
        logger.info(f"Fetching data for {ticker} from {start_date}")

        # Create a Ticker object
        crypto = yf.Ticker(ticker)

        # Fetch historical data
        df = crypto.history(start=start_date, interval='1d')

        if df.empty:
            logger.error(f"No data retrieved for {ticker}")
            return None

        logger.info(f"Successfully fetched {len(df)} records for {ticker}")
        return df

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}", exc_info=True)
        return None


def transform_to_daily_ohlc(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Transform Yahoo Finance data into the required daily OHLC format.

    Args:
        df: DataFrame from Yahoo Finance with columns: Open, High, Low, Close, Volume
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)

    Returns:
        DataFrame with columns: date, crypto, price_open, price_close, volume
    """
    if df.empty:
        logger.error(f"Empty dataframe for {symbol}")
        return pd.DataFrame()

    # Create a new dataframe with the required columns
    transformed_df = pd.DataFrame({
        'date': df.index.date,
        'crypto': symbol,
        'price_open': df['Open'].values,
        'price_close': df['Close'].values,
        'volume': df['Volume'].values
    })

    # Convert date to string format YYYY-MM-DD
    transformed_df['date'] = transformed_df['date'].astype(str)

    # Remove any rows with NaN values
    transformed_df = transformed_df.dropna()

    # Sort by date
    transformed_df = transformed_df.sort_values('date').reset_index(drop=True)

    logger.info(f"Transformed {len(transformed_df)} daily records for {symbol}")

    return transformed_df


def save_to_csv(df: pd.DataFrame, symbol: str) -> None:
    """
    Save DataFrame to CSV file in data/bronze/{SYMBOL}/historical_prices.csv.

    This function overwrites existing files if they exist.

    Args:
        df: DataFrame to save
        symbol: Cryptocurrency symbol (BTC, ETH, SOL)
    """
    if df.empty:
        logger.warning(f"No data to save for {symbol}")
        return

    # Get the script directory and project root (parent directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Create directory structure relative to project root
    output_dir = os.path.join(project_root, "data", "bronze", symbol)
    os.makedirs(output_dir, exist_ok=True)

    # Define output file path
    output_file = os.path.join(output_dir, "historical_prices.csv")

    # Save to CSV
    df.to_csv(output_file, index=False)

    logger.info(f"Saved {len(df)} records to {output_file}")


def main():
    """
    Main function to orchestrate the data fetching process.
    """
    logger.info("Script started")

    # Load configuration
    config = load_config()
    cryptos = config.get("cryptos", {})
    start_date = config.get("start_date", "2014-01-01")

    for symbol, ticker in cryptos.items():
        logger.info(f"Processing {symbol} ({ticker})")

        # Fetch data from Yahoo Finance
        df = fetch_crypto_data(ticker, start_date)

        if df is None:
            logger.error(f"Failed to fetch data for {symbol}, skipping...")
            continue

        # Transform to required format
        transformed_df = transform_to_daily_ohlc(df, symbol)

        if transformed_df.empty:
            logger.warning(f"No data to save for {symbol}, skipping...")
            continue

        # Save to CSV
        save_to_csv(transformed_df, symbol)

    logger.info("Script completed")


if __name__ == "__main__":
    main()
