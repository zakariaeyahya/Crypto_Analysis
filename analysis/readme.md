# Sentiment Analysis and Cryptocurrency Price Analysis

## Project Objective

This project aims to analyze the relationship between **sentiment expressed on Twitter** about cryptocurrencies (Bitcoin, Ethereum, Solana) and their **price movements**.  
The main objective is to determine:

- whether a **correlation** exists between sentiment and price variation,
- whether **sentiment can precede (lag)** price movements,
- at which **time scales** (daily, weekly, monthly) these relationships can be observed.


## Step 1 – Tweet Enrichment (entity_extraction.py)

### Objective

Transform raw tweets into **structured and enriched data**.

### Actions Performed

- Load cleaned tweets (`crypto_sent.csv`)
- Automatic detection of:
  - cryptocurrencies (Bitcoin, Ethereum, Solana)
  - exchanges
  - influencers
  - hashtags and mentions
  - events (hack, regulation, pump, crash, etc.)
- Identification of the tweet source (original tweet or retweet)

### Output

- Enriched JSON file:
  ```
    data/silver/enriched_data/enriched_data.json
  ```


Each tweet now contains sentiment, sentiment score, detected entities, events, and mentioned cryptocurrencies.

---

## Step 2 – Sentiment and Price Join (data_price.py)

### Objective

Associate each tweet with the **daily price variation** of the corresponding cryptocurrency.

### Actions Performed

- Load historical price data (open / close / volume)
- Compute daily price variation:

  ```
  price_change = (close - open) / open
  ```


- Join data using:
  - tweet date
  - mentioned cryptocurrency
- Duplicate tweets when multiple cryptocurrencies are mentioned

### Output

- Enriched dataset combining sentiment and price data:

  ```
  data/silver/enriched_data/crypto_sent_enriched_price.json
  ```

---


---

## Step 3 – Sentiment Time Series Aggregation (time_serie_agregation.py)

### Objective

Create **daily sentiment time series** for each cryptocurrency.

### Actions Performed

- Aggregation by day and by cryptocurrency
- Computation of statistics:
  - mean sentiment
  - standard deviation
  - number of positive / negative / neutral tweets
- Computation of moving averages:
  - 7-day moving average
  - 30-day moving average

### Output

- Sentiment time series file:
  ```
  data/gold/sentiment_timeseries.json
  ```


---

## Step 4 – Correlation Analysis (correlation.py)

### Objective

Measure the **direct relationship** between sentiment and price variation.

### Method

- Join:
  - daily mean sentiment
  - daily price variation
- Compute **Pearson correlation** for each cryptocurrency

### Produced Indicators

- correlation coefficient (r)
- statistical p-value
- number of observations

### Output
```bash
data/gold/sentiment_price_correlation.json
```


---

## Step 5 – Lag Analysis (lag_analysis.py)

### Objective

Test whether **sentiment precedes price movements**.

### Analyses Performed

For each cryptocurrency:

- sentiment(t) → price(t+1)
- analysis at three time scales:
  - daily
  - weekly
  - monthly

### Statistical Tests

- Pearson correlation
- Spearman correlation
- Granger causality test

### Output

```bash
data/gold/lag_analysis.json

```
---

## Pipeline Summary

1. Raw tweets → **semantic enrichment**
2. Integration of **price data**
3. **Temporal aggregation** of sentiment
4. **Correlation analysis** between sentiment and price
5. **Lag and causality analysis**