import json
import pandas as pd
import os
import logging
import warnings

from scipy.stats import pearsonr, spearmanr
from statsmodels.tsa.stattools import grangercausalitytests

warnings.filterwarnings("ignore")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, "data")

SENTIMENT_PATH = os.path.join(
    DATA_PATH, "gold", "sentiment_timeseries.json"
)

PRICE_PATH = os.path.join(
    DATA_PATH, "silver", "enriched_data", "crypto_sent_enriched_price.json"
)

OUTPUT_JSON = os.path.join(
    DATA_PATH, "gold", "lag_analysis.json"
)

with open(SENTIMENT_PATH, "r", encoding="utf-8") as f:
    sentiment = json.load(f)

with open(PRICE_PATH, "r", encoding="utf-8") as f:
    prices = json.load(f)

df_sent = pd.DataFrame(sentiment)
df_price = pd.DataFrame(prices)

logging.info("Data loaded")

# PREPARE DATA

# --- Convert dates ONCE
df_sent["date"] = pd.to_datetime(df_sent["date"], errors="coerce").dt.date
df_price["date"] = pd.to_datetime(df_price["date"], errors="coerce").dt.date

df_sent = df_sent.dropna(subset=["date"])
df_price = df_price.dropna(subset=["date"])

# --- Aggregate price per day
df_price_daily = (
    df_price.groupby(["date", "crypto"])
    .agg(
        price_change=("price_change", "mean"),
        volume=("volume", "mean")
    )
    .reset_index()
)

# --- Merge sentiment + price
df = df_sent.merge(
    df_price_daily,
    on=["date", "crypto"],
    how="inner"
)

df = df.sort_values(["crypto", "date"])
logging.info(f"Merged dataset size: {len(df)}")

# GENERIC LAG FUNCTION
def run_lag_analysis(df, time_col, label):
    results = []

    for crypto, group in df.groupby("crypto"):
        group = group.sort_values(time_col).reset_index(drop=True)

        # sentiment(t) → price(t+1)
        group["sentiment_lag"] = group["sentiment_mean"].shift(1)
        group = group.dropna(subset=["sentiment_lag", "price_change"])

        if len(group) < 10:
            continue

        pearson_r, pearson_p = pearsonr(
            group["sentiment_lag"],
            group["price_change"]
        )

        spearman_r, spearman_p = spearmanr(
            group["sentiment_lag"],
            group["price_change"]
        )

        granger_p = None
        try:
            gdata = group[["price_change", "sentiment_lag"]]
            tests = grangercausalitytests(
                gdata,
                maxlag=2,
                verbose=False
            )
            granger_p = min(
                test[0]["ssr_ftest"][1]
                for test in tests.values()
            )
        except Exception:
            pass

        results.append({
            "crypto": crypto,
            "time_scale": label,
            "pearson_r": round(float(pearson_r), 4),
            "pearson_p": round(float(pearson_p), 6),
            "spearman_r": round(float(spearman_r), 4),
            "spearman_p": round(float(spearman_p), 6),
            "granger_p_value": (
                round(float(granger_p), 6)
                if granger_p is not None else None
            ),
            "n_observations": len(group)
        })

    return results

# DAILY (D → D+1)
daily_results = run_lag_analysis(
    df.copy(),
    time_col="date",
    label="daily (D → D+1)"
)

# 7) WEEKLY (W → W+1)
df["week"] = pd.to_datetime(df["date"]).dt.to_period("W")

weekly_df = (
    df.groupby(["crypto", "week"])
    .agg(
        sentiment_mean=("sentiment_mean", "mean"),
        price_change=("price_change", "mean")
    )
    .reset_index()
)

weekly_results = run_lag_analysis(
    weekly_df,
    time_col="week",
    label="weekly (W → W+1)"
)

# MONTHLY (M → M+1)

df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")

monthly_df = (
    df.groupby(["crypto", "month"])
    .agg(
        sentiment_mean=("sentiment_mean", "mean"),
        price_change=("price_change", "mean")
    )
    .reset_index()
)

monthly_results = run_lag_analysis(
    monthly_df,
    time_col="month",
    label="monthly (M → M+1)"
)

# SAVE RESULTS

all_results = (
    daily_results
    + weekly_results
    + monthly_results
)

os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

logging.info("Lag analysis completed (daily / weekly / monthly)")
logging.info(f"Results saved to: {OUTPUT_JSON}")
