# ==========================
# Imports
# ==========================
import pandas as pd
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import re
import os
from tqdm import tqdm
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Allows displaying progress for apply
tqdm.pandas()

# ==========================
# Charger modèle spaCy
# ==========================
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ==========================
# Custom crypto stopwords
# ==========================
def load_stopwords_from_json(file_path):
    """Loads stopwords from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            stopwords_list = json.load(f)
        return set(stopwords_list)
    except FileNotFoundError:
        logging.error(f"Stopwords file '{file_path}' not found. Using an empty list.")
        return set()
    except json.JSONDecodeError:
        logging.error(f"JSON decoding error in file '{file_path}'. Using an empty list.")
        return set()

# Load stopwords from the external file
CRYPTO_STOPWORDS = load_stopwords_from_json("C:\\Users\\Hiba\\Desktop\\S9\\crypto\\crypto_stopwords.json")
# Merge spaCy + crypto stopwords
all_stopwords = STOP_WORDS.union(CRYPTO_STOPWORDS)

# ==========================
# Preprocessing function
# ==========================
def preprocess_text(text):
    if not isinstance(text, str):
        return ""

    # Remove URLs, hashtags, mentions, non-letter punctuation
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[@#]\w+', '', text)
    text = re.sub(r'[^a-zA-Z ]+', ' ', text)
    text = text.lower()
    
    doc = nlp(text)
    
    tokens = [
        token.lemma_.lower() for token in doc
        if token.lemma_.isalpha()
        and len(token.lemma_) > 2
        and token.lemma_.lower() not in all_stopwords
        and not token.is_stop
    ]
    
    return " ".join(tokens)

# ==========================
# Load dataset
# ==========================
input_file = "C:\\Users\\DELL\\Downloads\\train_data.csv"
df = pd.read_csv(input_file)

# ==========================
# Apply cleaning with tqdm
# ==========================
df["processed_text"] = df["text_content"].progress_apply(preprocess_text)

# ==========================
# VADER Sentiment Analysis
# ==========================
analyzer = SentimentIntensityAnalyzer()

# Apply VADER to the processed text
df['vader_scores'] = df['processed_text'].progress_apply(lambda text: analyzer.polarity_scores(text))

# Extract scores into separate columns
df['vader_compound'] = df['vader_scores'].apply(lambda score_dict: score_dict['compound'])
df['vader_pos'] = df['vader_scores'].apply(lambda score_dict: score_dict['pos'])
df['vader_neg'] = df['vader_scores'].apply(lambda score_dict: score_dict['neg'])
df['vader_neu'] = df['vader_scores'].apply(lambda score_dict: score_dict['neu'])

# Convertir le score compound en sentiment
def vader_to_sentiment(compound):
    """Converts VADER compound score to a sentiment label."""
    if compound >= 0.05:
        return 'positive'
    elif compound <= -0.05:
        return 'negative'
    else:
        return 'neutral'

df['vader_sentiment'] = df['vader_compound'].apply(vader_to_sentiment)

# ==========================
# VADER Model Evaluation
# ==========================
# Make sure your CSV has a 'sentiment' column with the true labels
if 'sentiment' in df.columns:
    y_true = df['sentiment']
    y_pred = df['vader_sentiment']

    logging.info("\n VADER Evaluation:")
    logging.info("="*25)
    logging.info(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
    logging.info("\nClassification Report:")
    logging.info(classification_report(y_true, y_pred, digits=4))
    logging.info("\nConfusion Matrix:")
    logging.info(confusion_matrix(y_true, y_pred, labels=['positive', 'neutral', 'negative']))
else:
    logging.info("\n'sentiment' column not found. Performance evaluation is skipped.")

# ==========================
# Save result
# ==========================
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
logging.info(f"Data directory created at: {os.path.abspath(DATA_DIR)}")
logging.info(f"DATA_DIR value: {DATA_DIR}")

# Delete the old .csv file if it exists
old_output_file = os.path.abspath("processed_train_data.csv")
if os.path.exists(old_output_file):
    os.remove(old_output_file)

output_file = os.path.abspath(os.path.join(DATA_DIR, "processed_train_data.csv"))
df.to_csv(output_file, index=False)

logging.info("\nVADER analysis and cleaning finished!")
logging.info(f"New file saved here: {os.path.abspath(output_file)}")
