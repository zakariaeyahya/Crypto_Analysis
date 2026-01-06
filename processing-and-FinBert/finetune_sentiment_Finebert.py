import pandas as pd
import numpy as np
import torch
import re
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_scheduler
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from tqdm.auto import tqdm
import gc  # Garbage Collector
import logging

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# --- 1. Configuration ---
# Define model and training parameters
# "ProsusAI/finbert" est l'identifiant Hugging Face pour le modèle FinBERT.
MODEL_NAME = "ProsusAI/finbert" 
DATA_PATH = "/kaggle/input/bitcoin-tweets-16m-tweets-with-sentiment-tagged/mbsa.csv"
MAX_LENGTH = 128
BATCH_SIZE = 32 # Réduire si vous avez des erreurs de mémoire (OutOfMemoryError)
EPOCHS = 3
LEARNING_RATE = 2e-5

# --- 2. GPU Configuration ---
def setup_device():
    """Checks for GPU availability and sets the device accordingly."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logging.info(f"GPU available: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logging.info("GPU not available, using CPU.")
    return device

# --- 3. Data Processing Functions ---
def clean_tweet(text):
    """Cleans the text of a tweet."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'\@\w+', '', text)  # Remove mentions
    text = re.sub(r'#', '', text)  # Remove '#' symbol but keep the word
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation and special characters
    text = text.lower()  # Convert to lowercase
    return text.strip()

def load_and_prepare_data(path, sample_size=None):
    """Loads, cleans, and prepares data from the CSV file."""
    logging.info("Loading and cleaning data...")
    # The CSV file has no header, so we name the columns manually
    df = pd.read_csv(path, header=None, names=['text', 'sentiment'])

    # 1. Filter for positive and negative sentiments only
    logging.info(f"Original dataset size: {len(df)}")
    df = df[df['sentiment'].isin([0, 2])].copy()
    logging.info(f"Dataset size after filtering for positive/negative: {len(df)}")

    if sample_size:
        logging.info(f"Using a sample of {sample_size} tweets.")
        df = df.sample(n=sample_size, random_state=42)

    # 2. Map sentiments to new binary labels (0 for negative, 1 for positive)
    label_map = {'negative': 0, 'positive': 1}
    df['label'] = df['sentiment'].map({0: 0, 2: 1}) # 0 -> negative, 2 -> positive
    df['sentiment_label'] = df['label'].map({v: k for k, v in label_map.items()})
    
    df.dropna(subset=['label', 'text'], inplace=True)
    df['label'] = df['label'].astype(int)

    df['cleaned_text'] = df['text'].apply(clean_tweet)

    logging.info("Data preview after cleaning:\n%s", df[['cleaned_text', 'sentiment_label', 'label']].head().to_string())

    return df, label_map

# --- 4. Classe Dataset PyTorch ---
class TweetDataset(Dataset):
    """Classe de Dataset PyTorch personnalisée pour les tweets."""
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# --- 5. Training and Evaluation Functions ---
def train_epoch(model, data_loader, optimizer, device, scheduler, progress_bar):
    """Performs one training epoch."""
    model.train()
    total_loss = 0
    for batch in data_loader:
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()
        scheduler.step()

        progress_bar.update(1)
        progress_bar.set_postfix({'loss': loss.item()})
    return total_loss / len(data_loader)

def eval_model(model, data_loader, device, progress_bar):
    """Evaluates the model on the validation dataset."""
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            predictions = torch.argmax(outputs.logits, dim=-1)

            all_preds.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            progress_bar.update(1)
    return all_labels, all_preds

# --- 6. Main Execution ---
def main():
    device = setup_device()
    df, label_map = load_and_prepare_data(DATA_PATH)

    # Split the dataset
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['cleaned_text'].tolist(), df['label'].tolist(),
        test_size=0.2, random_state=42, stratify=df['label']
    )

    # Tokenization
    logging.info("Tokenizing data...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=MAX_LENGTH)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=MAX_LENGTH)

    # Create Datasets and DataLoaders
    train_dataset = TweetDataset(train_encodings, train_labels)
    val_dataset = TweetDataset(val_encodings, val_labels)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    # Load the model
    logging.info("Loading pre-trained model...")
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(label_map))
    model.to(device)

    # Configure optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    num_training_steps = EPOCHS * len(train_loader)
    lr_scheduler = get_scheduler(
        name="linear", optimizer=optimizer,
        num_warmup_steps=0, num_training_steps=num_training_steps
    )

    # Training and evaluation loop
    logging.info("Starting training...")
    for epoch in range(EPOCHS):
        logging.info(f"--- Epoch {epoch+1}/{EPOCHS} ---")
        # Training
        progress_bar_train = tqdm(total=len(train_loader), desc="Training")
        avg_train_loss = train_epoch(model, train_loader, optimizer, device, lr_scheduler, progress_bar_train)
        progress_bar_train.close()
        logging.info(f"Average training loss: {avg_train_loss:.4f}")

        # Evaluation
        progress_bar_val = tqdm(total=len(val_loader), desc="Evaluating")
        true_labels, predictions = eval_model(model, val_loader, device, progress_bar_val)
        progress_bar_val.close()
        
        accuracy = accuracy_score(true_labels, predictions)
        f1 = f1_score(true_labels, predictions, average='weighted')
        logging.info(f"Validation Accuracy: {accuracy:.4f} | F1-Score (weighted): {f1:.4f}")

    # Final evaluation
    logging.info("--- Final Evaluation ---")
    target_names = [label for label, _ in sorted(label_map.items(), key=lambda item: item[1])]
    report = classification_report(true_labels, predictions, target_names=target_names)
    logging.info("Classification Report:\n%s", report)

    # Free up memory
    del model, train_loader, val_loader
    gc.collect()
    torch.cuda.empty_cache()
    logging.info("Training and evaluation finished!")

if __name__ == "__main__":
    main()
