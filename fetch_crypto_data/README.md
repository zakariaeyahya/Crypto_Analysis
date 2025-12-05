# Cryptocurrency Historical Price Data Fetcher

## Description

This Python script fetches historical price data for the following cryptocurrencies using Yahoo Finance:

- **BTC** (Bitcoin)
- **ETH** (Ethereum)
- **SOL** (Solana)

The data is transformed into daily OHLC (Open, High, Low, Close) format and saved to CSV files. Unlike CoinGecko's free API which limits historical data to the last 365 days, Yahoo Finance provides access to full historical data since 2014.

## Prerequisites

### Python Dependencies

The script requires the following libraries:

- `yfinance` : Yahoo Finance API wrapper for fetching cryptocurrency data
- `pandas` : For data manipulation and transformation

### Installation

```bash
pip install yfinance pandas
```

Or use the project's `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Directory Structure

The script automatically creates the following directory structure:

```
data/
└── bronze/
    ├── BTC/
    │   └── historical_prices.csv
    ├── ETH/
    │   └── historical_prices.csv
    └── SOL/
        └── historical_prices.csv
```

## Usage

### Running the Script

From the project root:

```bash
python fetch_crypto_data/fetch_crypto_data_yfinance.py
```

Or from the `fetch_crypto_data` directory:

```bash
cd fetch_crypto_data
python fetch_crypto_data_yfinance.py
```

### Behavior

The script:

1. **Fetches data** from Yahoo Finance for each cryptocurrency starting from the configured start date
2. **Transforms the data** into daily format with the following columns:
   - `date` : Date in YYYY-MM-DD format (UTC)
   - `crypto` : Cryptocurrency symbol (BTC, ETH, SOL)
   - `price_open` : Opening price of the day
   - `price_close` : Closing price of the day
   - `volume` : Total volume for the day
3. **Saves** the data to separate CSV files per cryptocurrency

### Idempotence

The script is **idempotent**: running it multiple times will produce the same result. Existing CSV files will be **overwritten** with new data.

## Data Format

### CSV Schema

Each CSV file contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `date` | string | Date in YYYY-MM-DD format (UTC) |
| `crypto` | string | Cryptocurrency symbol (BTC, ETH, SOL) |
| `price_open` | float | Opening price of the day in USD |
| `price_close` | float | Closing price of the day in USD |
| `volume` | float | Total volume for the day in USD |

### Example Data

```csv
date,crypto,price_open,price_close,volume
2014-01-01,BTC,770.0,770.0,0.0
2014-01-02,BTC,770.0,770.0,0.0
2014-01-03,BTC,770.0,770.0,0.0
```

## Error Handling

### Rate Limiting

Yahoo Finance does not have strict rate limits like CoinGecko, but the script includes error handling for network issues and API failures.

### Retry Mechanism

The script implements basic error handling:

- **Network errors** : Logged with full stack traces
- **Empty data** : Logged as warnings
- **Missing data** : Rows with NaN values are automatically removed

### Logging

The script uses Python's built-in `logging` module to record:

- Script start and end
- Configuration loading
- Data fetching progress for each cryptocurrency
- Number of records fetched per cryptocurrency
- Path of CSV files created
- Errors with stack traces where relevant

Logs are displayed in the console with the format:

```
YYYY-MM-DD HH:MM:SS - LEVEL - Message
```

## Configuration

Configuration parameters are defined in the `config_yfinance.json` file:

```json
{
  "cryptos": {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD"
  },
  "start_date": "2014-01-01"
}
```

### Configuration Parameters

- `cryptos` : Dictionary mapping cryptocurrency symbols to Yahoo Finance ticker symbols
- `start_date` : Start date in "YYYY-MM-DD" format (e.g., "2014-01-01")

**Note** : The script fetches data from the `start_date` until today. Yahoo Finance provides full historical data, so you can set the start date to any date when the cryptocurrency was available.

## Yahoo Finance API

### Ticker Symbols

The script uses Yahoo Finance ticker symbols:

- Bitcoin : `BTC-USD`
- Ethereum : `ETH-USD`
- Solana : `SOL-USD`

### Data Source

Yahoo Finance provides free access to historical cryptocurrency data without API keys or rate limits. The data is fetched using the `yfinance` library which wraps Yahoo Finance's API.

## Main Functions

### `load_config() -> Dict`

Loads configuration from `config_yfinance.json` file.

**Returns:**
- Dictionary containing configuration settings

### `fetch_crypto_data(ticker: str, start_date: str) -> Optional[pd.DataFrame]`

Fetches historical cryptocurrency data from Yahoo Finance.

**Parameters:**
- `ticker` : Yahoo Finance ticker symbol (e.g., 'BTC-USD')
- `start_date` : Start date in "YYYY-MM-DD" format

**Returns:**
- DataFrame with historical data (Open, High, Low, Close, Volume), or `None` if failed

### `transform_to_daily_ohlc(df: pd.DataFrame, symbol: str) -> pd.DataFrame`

Transforms Yahoo Finance data into the required daily OHLC format.

**Parameters:**
- `df` : DataFrame from Yahoo Finance with columns: Open, High, Low, Close, Volume
- `symbol` : Cryptocurrency symbol (BTC, ETH, SOL)

**Returns:**
- DataFrame with columns: date, crypto, price_open, price_close, volume

### `save_to_csv(df: pd.DataFrame, symbol: str) -> None`

Saves the DataFrame to a CSV file.

**Parameters:**
- `df` : DataFrame to save
- `symbol` : Cryptocurrency symbol (BTC, ETH, SOL)

**File created:**
- `data/bronze/{SYMBOL}/historical_prices.csv`

## Example Console Output

```
2025-11-28 19:17:13 - INFO - Script started
2025-11-28 19:17:13 - INFO - Configuration loaded from D:\...\config_yfinance.json
2025-11-28 19:17:13 - INFO - Processing BTC (BTC-USD)
2025-11-28 19:17:13 - INFO - Fetching data for BTC-USD from 2014-01-01
2025-11-28 19:17:14 - INFO - Successfully fetched 4091 records for BTC-USD
2025-11-28 19:17:14 - INFO - Transformed 4091 daily records for BTC
2025-11-28 19:17:14 - INFO - Saved 4091 records to data/bronze/BTC/historical_prices.csv
2025-11-28 19:17:14 - INFO - Processing ETH (ETH-USD)
2025-11-28 19:17:14 - INFO - Fetching data for ETH-USD from 2014-01-01
2025-11-28 19:17:15 - INFO - Successfully fetched 2942 records for ETH-USD
2025-11-28 19:17:15 - INFO - Transformed 2942 daily records for ETH
2025-11-28 19:17:15 - INFO - Saved 2942 records to data/bronze/ETH/historical_prices.csv
2025-11-28 19:17:15 - INFO - Processing SOL (SOL-USD)
2025-11-28 19:17:15 - INFO - Fetching data for SOL-USD from 2014-01-01
2025-11-28 19:17:15 - INFO - Successfully fetched 2059 records for SOL-USD
2025-11-28 19:17:15 - INFO - Transformed 2059 daily records for SOL
2025-11-28 19:17:15 - INFO - Saved 2059 records to data/bronze/SOL/historical_prices.csv
2025-11-28 19:17:15 - INFO - Script completed
```

## Important Notes

1. **No API Key Required** : Yahoo Finance provides free access to historical data without requiring API keys

2. **Execution Time** : The script typically completes in a few seconds since it makes direct API calls to Yahoo Finance without rate limiting delays

3. **Historical Data** : Yahoo Finance provides full historical data since the cryptocurrency's launch. For example:
   - Bitcoin: Data available since 2014
   - Ethereum: Data available since 2015
   - Solana: Data available since 2020

4. **CSV Files** : Files are created with UTF-8 encoding and comma separator

5. **Data Quality** : The script automatically removes rows with NaN values to ensure data quality

## Troubleshooting

### Error: ModuleNotFoundError

If you get a `ModuleNotFoundError`, install the dependencies:

```bash
pip install yfinance pandas
```

### Error: No Data Retrieved

If you get "No data retrieved" errors:

1. Check that the ticker symbol is correct in `config_yfinance.json`
2. Verify that the cryptocurrency was available on the specified start date
3. Check your internet connection

### Error: Network Timeout

If requests timeout, check your internet connection. Yahoo Finance may occasionally be slow to respond.

## Advantages Over CoinGecko

This script uses Yahoo Finance instead of CoinGecko because:

1. **Full Historical Access** : Yahoo Finance provides complete historical data, not limited to 365 days
2. **No Rate Limits** : No strict rate limiting like CoinGecko's free tier
3. **No API Key Required** : Free access without registration
4. **Faster Execution** : No delays between API calls needed

## License

This script is part of the Crypto_Analysis project.
