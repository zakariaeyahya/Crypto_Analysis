import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline
from sklearn.metrics import classification_report, accuracy_score
import nltk
import os
import logging
from collections import Counter

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ===============================================================
# 1️⃣ INSTALLATION & INITIALIZATION
# ===============================================================
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# ===============================================================
# 2️⃣ PARAMETERS
# ===============================================================
TEXT_COL = 'processed_text'  # text column in both CSV files
OUTPUT_DIR = 'C:/Users/Hiba/Desktop/S9/crypto/'  # output directory

# ===============================================================
# 3️⃣ ANALYSIS FUNCTIONS
# ===============================================================

def get_vader_sentiment(text):
    # Handle cases where text is empty or NaN
    if pd.isna(text) or not str(text).strip():
        return 'neutral'
        
    scores = sia.polarity_scores(str(text))
    compound = scores['compound']
    if compound >= 0.05:
        sentiment = 'positive'
    elif compound <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    return sentiment

def analyze_finbert_sentiment(text):
    try:
        # Split text into chunks of 512 characters (FinBERT has token limit)
        chunks = [text[i:i + 512] for i in range(0, len(text), 512)]
        
        # Process each chunk and get sentiment
        sentiments = []
        for chunk in chunks:
            result = sentiment_pipeline(chunk)[0]
            sentiments.append(result['label'])
        
        # Combine sentiments: majority vote
        if sentiments:
            sentiment_counts = Counter(sentiments)
            most_common_sentiment = sentiment_counts.most_common(1)[0][0]
            return most_common_sentiment.lower()  # Normalize to lowercase (e.g., 'POSITIVE' -> 'positive')
        else:
            return 'neutral'  # No text to analyze
    except Exception as e:
        logging.error(f"Error analyzing sentiment with FinBERT: {e}")
        return 'neutral'  # Return neutral in case of error

# ===============================================================
# 4️⃣ FILE PROCESSING
# ===============================================================

def process_file(input_path, output_path):
    try:
        # Load the CSV
        df = pd.read_csv(input_path, encoding='latin1')  # Use encoding='latin1' if necessary
        logging.info(f"✅ File loaded: {input_path}, shape: {df.shape}")
        
        # Apply VADER
        logging.info("🔍 Applying VADER...")
        df['vader_sentiment'] = df[TEXT_COL].apply(get_vader_sentiment)
        
        # Apply FinBERT
        logging.info("🔍 Applying FinBERT...")
        df['finbert_sentiment'] = df[TEXT_COL].apply(analyze_finbert_sentiment)
        
        # Save the result
        df.to_csv(output_path, index=False)
        logging.info(f"✅ Results saved here: {output_path}")
        
    except FileNotFoundError:
        logging.error(f"Error: File not found at {input_path}")
    except KeyError as e:
        logging.error(f"Error: Column '{TEXT_COL}' not found in {input_path}. Details: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# ===============================================================
# 5️⃣ MAIN EXECUTION
# ===============================================================

if __name__ == "__main__":
    # Input and output file paths
    train_input = "C:/Users/Hiba/Desktop/S9/crypto/processed_train_data.csv"
    test_input = "C:/Users/Hiba/Desktop/S9/crypto/processed_test_data.csv"
    train_output = "C:/Users/Hiba/Desktop/S9/crypto/vader_finBert_train_results.csv"
    test_output = "C:/Users/Hiba/Desktop/S9/crypto/vader_finBert_test_results.csv"
    
    # Process the train file
    logging.info("\n Processing TRAIN file...")
    process_file(train_input, train_output)
    
    # Process the test file
    logging.info("\n Processing TEST file...")
    process_file(test_input, test_output)
    
    logging.info("\n Combined VADER + FinBERT analysis completed successfully on both datasets!")
