# Crypto Sentiment Analysis (Hybrid VADER) 

This project implements an enhanced **Sentiment Analysis** tool specifically tailored for Cryptocurrency tweets.

Standard NLP tools (like default VADER) often fail to capture the sentiment of crypto-slang (e.g., *"HODL"*, *"To the moon"*, *"Rekt"*). This project solves this by using a **Hybrid Approach**:
1.  **Statistical Learning:** Auto-generates sentiment scores from 1 Million tweets based on word frequency distribution.
2.  **Domain Knowledge:** Injects a manual dictionary of specific crypto jargon.

##  Project Structure

| File | Description |
| :--- | :--- |
| `vader.ipynb` | Main Jupyter Notebook containing data cleaning, training, and evaluation logic. |
| `crypto_lexicon_final.json` | The **pre-trained model weights**. A JSON dictionary mapping words to sentiment scores. |
| `train_full.csv` | Processed training dataset (70% of data). |
| `val_full.csv` | Validation dataset (15% of data). |
| `test_full.csv` | Test dataset (15% of data) used for final metrics. |

##  Installation

Make sure you have the required Python libraries installed:


pip install pandas numpy nltk scikit-learn tqdm


##  How to Use (Inference)

You don't need to run the notebook to use the model. You can simply load the generated `crypto_lexicon_final.json` to analyze new texts.

Here is a Python script using **logging** for production-ready output:

import json
import nltk
import logging
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# 1. Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 2. Initialize VADER
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

sid = SentimentIntensityAnalyzer()

# 3. Load the Pre-trained Crypto Lexicon
lexicon_file = 'crypto_lexicon_final.json'

try:
    with open(lexicon_file, 'r') as f:
        crypto_lexicon = json.load(f)
    
    # Update VADER with the new vocabulary
    sid.lexicon.update(crypto_lexicon)
    logging.info(f" Model successfully loaded with {len(crypto_lexicon)} custom terms.")
    
except FileNotFoundError:
    logging.error(f" Error: '{lexicon_file}' not found. Please run the notebook first to generate it.")

# 4. Test on new data
test_sentences = [
    "Just bought the dip, extremely bullish on BTC! HODL.",
    "This project is a total scam, I got rekt.",
    "Bitcoin is stable today."
]

logging.info("--- STARTING PREDICTIONS ---")
for text in test_sentences:
    scores = sid.polarity_scores(text)
    sentiment = "Positive" if scores['compound'] > 0 else "Negative"
    logging.info(f"Text: '{text}' | Score: {scores['compound']} | Sentiment: {sentiment}")
```

##  Performance & Methodology

The model was evaluated on a test set of **148,664 tweets**.

### Methodology Steps:

1.  **Cleaning:** Removed URLs, mentions (@), hashtags (\#), and punctuation.
2.  **Splitting:** Data divided into Train (70%), Validation (15%), and Test (15%).
3.  **Lexicon Generation:** Words appearing \>75% in positive tweets got positive scores; words appearing \<25% got negative scores.

### Results:

  * **Global Accuracy:** **69.80%**
  * **Positive Class Recall:** 0.90 (Very good at detecting hype/bullishness).
  * **Negative Class Recall:** 0.19 (Struggles with subtle negativity/sarcasm).

| Class | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- |
| **Negative** | 0.42 | 0.19 | 0.26 |
| **Positive** | 0.74 | 0.90 | 0.81 |



