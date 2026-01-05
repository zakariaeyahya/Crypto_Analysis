import json
import pandas as pd
import os
import logging


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, "data")

TWEETS_PATH = os.path.join(
    DATA_PATH, "silver", "enriched_data", "enriched_data.json"
)

BTC_PATH = os.path.join(
    DATA_PATH, "bronze", "BTC", "historical_prices.csv"
)

ETH_PATH = os.path.join(
    DATA_PATH, "bronze", "eth", "historical_prices.csv"
)

SOL_PATH = os.path.join(
    DATA_PATH, "bronze", "sol", "historical_prices.csv"
)

OUTPUT_JSON = os.path.join(
    DATA_PATH, "silver", "enriched_data", "crypto_sent_enriched_price.json"
)


with open(TWEETS_PATH, "r", encoding="utf-8") as f:
    tweets = json.load(f)

logging.info(f"Loaded {len(tweets)} tweets")

# LOAD & PREPARE PRICE DATA
def load_price_data(path, crypto_name):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["crypto"] = crypto_name
    df["price_change"] = (df["price_close"] - df["price_open"]) / df["price_open"]
    return df[["date", "crypto", "price_change", "volume"]]

btc = load_price_data(BTC_PATH, "Bitcoin")
eth = load_price_data(ETH_PATH, "Ethereum")
sol = load_price_data(SOL_PATH, "Solana")

price_df = pd.concat([btc, eth, sol], ignore_index=True)

logging.info("Price data loaded and price_change calculated")

# EXPLODE TWEETS (1 CRYPTO = 1 OBJECT)

crypto_suffix = {
    "Bitcoin": "b",
    "Ethereum": "e",
    "Solana": "s"
}

final_records = []

for tweet in tweets:
    tweet_date = pd.to_datetime(tweet["date"]).date()
    cryptos = tweet.get("crypto", [])

    for crypto in cryptos:
        if crypto not in crypto_suffix:
            continue

        price_row = price_df[
            (price_df["date"] == tweet_date) &
            (price_df["crypto"] == crypto)
        ]

        if price_row.empty:
            continue

        price_row = price_row.iloc[0]

        record = {
            "id": f"{tweet['id']}{crypto_suffix[crypto]}",
            "text": tweet["text"],
            "date": tweet["date"],
            "source": tweet["source"],
            "crypto": crypto,
            "sentiment":tweet["sentiment"],
            "sentiment_score": tweet["sentiment_score"],
            "entities": tweet.get("entities", []),
            "events": [e["type"] for e in tweet.get("events", [])],
            "influencers": tweet.get("influencers", []),
            "price_change": float(price_row["price_change"]),
            "volume": float(price_row["volume"])
        }

        final_records.append(record)

logging.info(f"Final dataset size: {len(final_records)} records")

# SAVE FINAL JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(final_records, f, ensure_ascii=False, indent=2)

logging.info(f"Final JSON saved at: {OUTPUT_JSON}")

