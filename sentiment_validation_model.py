
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_sentiment(text_content, model_name="ProsusAI/finbert"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Check for GPU and move model to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    inputs = tokenizer(text_content, padding=True, truncation=True, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    # Apply softmax to get probabilities
    probabilities = torch.softmax(outputs.logits, dim=1)
    return probabilities.cpu().numpy()

def process_dataframe(df_path="validation_data.csv", model_name="ProsusAI/finbert"):
    df = pd.read_csv(df_path)
    
    # Ensure 'text_content' column exists
    if 'text_content' not in df.columns:
        raise ValueError("DataFrame must contain a 'text_content' column.")

    # Batch processing
    batch_size = 16  # Adjust based on memory constraints
    all_predictions = []

    for i in range(0, len(df), batch_size):
        batch_texts = df['text_content'].iloc[i:i+batch_size].tolist()
        predictions = analyze_sentiment(batch_texts, model_name)
        all_predictions.extend(predictions)

    # Add predictions to DataFrame
    df[['sentiment_negative', 'sentiment_neutral', 'sentiment_positive']] = pd.DataFrame(all_predictions)

    # Determine final sentiment
    df['sentiment'] = df[['sentiment_negative', 'sentiment_neutral', 'sentiment_positive']].idxmax(axis=1).str.replace('sentiment_', '')

    # Save predictions to a new CSV file
    DATA_DIR = 'data'
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    output_path = os.path.join(DATA_DIR, "validation_data_sentiment.csv")
    df.to_csv(output_path, index=False)
    logging.info(f"Sentiment analysis complete. Results saved to {output_path}")

if __name__ == "__main__":
    # Example usage:
    process_dataframe(df_path="validation_data.csv")
    
    
def determine_sentiment(row):
    if row['sentiment_positive'] > row['sentiment_negative'] and row['sentiment_positive'] > row['sentiment_neutral']:
        return 'positive'
    elif row['sentiment_negative'] > row['sentiment_positive'] and row['sentiment_negative'] > row['sentiment_neutral']:
        return 'negative'
    else:
        return 'neutral'

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("validation_data_sentiment.csv")

# Apply the function to each row to determine the sentiment
df['sentiment'] = df.apply(determine_sentiment, axis=1)

# Save the updated DataFrame back to the CSV file
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
output_file = os.path.join(DATA_DIR, "validation_data_sentiment.csv")
df.to_csv(output_file, index=False)

logging.info("Sentiment column added to validation_data_sentiment.csv")
