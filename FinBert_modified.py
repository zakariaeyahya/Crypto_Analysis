# ----------------- Imports -----------------
import os
import re
import gc
import logging
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_scheduler
from tqdm.auto import tqdm

# ----------------- Logging Configuration -----------------
# Resetting any existing handlers (useful in interactive environments like Kaggle/Jupyter)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ----------------- Configuration -----------------
MODEL_NAME = "ProsusAI/finbert"
DATA_PATH = "/kaggle/input/bitcoin-tweets-16m-tweets-with-sentiment-tagged/mbsa.csv"
MAX_LENGTH = 128
BATCH_SIZE = 32
EPOCHS = 3
LEARNING_RATE = 2e-5

# ----------------- Device -----------------
if torch.cuda.is_available():
    device = torch.device("cuda")
    logger.info(f"GPU detected: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device("cpu")
    logger.info("Using CPU")

# ----------------- Data Processing (Strict Version) -----------------
def clean_tweet(text):
    if not isinstance(text, str):
        return ""
    
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # 3. Remove mentions (@user)
    # The regex \S* removes the @ and everything attached to it until the next space
    text = re.sub(r'@\S+', '', text)
    
    # 4. Remove residual HTML entities (&amp; etc)
    text = re.sub(r'&\w+;', '', text)
    
    # 5. Remove NUMBERS (To remove prices like $347.86, dates like 2018, etc.)
    text = re.sub(r'\d+', '', text)
    
    # 6. Remove anything that is not a letter (a-z) or a space
    # This automatically removes #, $, :, ;, -, _, emojis, Japanese characters, etc.
    text = re.sub(r'[^\w\s]', '', text)
    
    # 7. Remove underscores (which are considered \w in regex)
    text = re.sub(r'_', '', text)

    # 8. Handle multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def load_and_prepare_data(path, sample_size=None):
    logger.info("Loading dataset...")
    df = pd.read_csv(path, header=None, names=['text', 'sentiment'])
    
    df.dropna(subset=['text', 'sentiment'], inplace=True)

    # Pre-sampling to avoid cleaning 16 million rows if not necessary
    if sample_size:
        # We take a buffer (x1.5) because strict cleaning will create empty rows
        fetch_size = int(sample_size * 1.5)
        if fetch_size < len(df):
            df = df.sample(fetch_size, random_state=42)
            logger.info(f"Raw extraction of {fetch_size} tweets before cleaning...")

    logger.info("Cleaning text (Strict Mode)...")
    tqdm.pandas()
    df['cleaned_text'] = df['text'].progress_apply(clean_tweet)
    
    # Remove tweets that became empty or too short (less than 3 words) after cleaning
    # Example: "Prices:" becomes "" after cleaning -> we remove it
    df = df[df['cleaned_text'].str.split().str.len() >= 3]
    
    # Cut to the exact requested size
    if sample_size and len(df) > sample_size:
        df = df.iloc[:sample_size]
    
    logger.info(f"Final dataset ready: {len(df)} tweets.")
    
    # Visual check for logs
    logger.info("-" * 50)
    logger.info("CLEANING CHECK:")
    # We convert the head to string to log it properly
    logger.info(f"\n{df[['text', 'cleaned_text']].head(5).to_string()}")
    logger.info("-" * 50)

    # Mapping
    label_map = {}
    if set(['Positive', 'Negative']).issubset(df['sentiment'].unique()):
        label_map = {'Negative': 0, 'Positive': 1}
        df = df[df['sentiment'].isin(['Negative', 'Positive'])]
    else:
        unique_labels = sorted(df['sentiment'].unique())
        label_map = {lbl: i for i, lbl in enumerate(unique_labels)}
    
    df['label'] = df['sentiment'].map(label_map)
    return df, label_map

# ----------------- PyTorch Dataset -----------------
class TweetDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# ----------------- Training Functions -----------------
def train_epoch(model, data_loader, optimizer, device, scheduler, progress_bar):
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
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=-1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            progress_bar.update(1)
    return all_labels, all_preds

# ----------------- Main -----------------
def main():
    # 1. Load Data (50,000 examples requested)
    df, label_map = load_and_prepare_data(DATA_PATH, sample_size=50000)
    
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['cleaned_text'].tolist(),
        df['label'].tolist(),
        test_size=0.2,  # 10,000 for test, 40,000 for train
        random_state=42,
        stratify=df['label']
    )

    logger.info("Tokenizing data...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=MAX_LENGTH)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=MAX_LENGTH)

    train_dataset = TweetDataset(train_encodings, train_labels)
    val_dataset = TweetDataset(val_encodings, val_labels)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    logger.info("Loading pre-trained model...")
    # Correction: ignore_mismatched_sizes=True to adapt the layers
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=len(label_map),
        ignore_mismatched_sizes=True 
    )
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    num_training_steps = EPOCHS * len(train_loader)
    lr_scheduler = get_scheduler(
        name="linear",
        optimizer=optimizer,
        num_warmup_steps=0,
        num_training_steps=num_training_steps
    )

    logger.info("Starting training...")
    for epoch in range(EPOCHS):
        logger.info(f"--- Epoch {epoch+1}/{EPOCHS} ---")
        
        progress_train = tqdm(total=len(train_loader), desc="Training")
        avg_loss = train_epoch(model, train_loader, optimizer, device, lr_scheduler, progress_train)
        progress_train.close()
        logger.info(f"Average training loss: {avg_loss:.4f}")
        
        progress_val = tqdm(total=len(val_loader), desc="Evaluating")
        true_labels, predictions = eval_model(model, val_loader, device, progress_val)
        progress_val.close()
        
        acc = accuracy_score(true_labels, predictions)
        f1 = f1_score(true_labels, predictions, average='weighted')
        logger.info(f"Validation Accuracy: {acc:.4f} | F1-weighted: {f1:.4f}")

    logger.info("Final classification report:")
    target_names = [label for label, _ in sorted(label_map.items(), key=lambda x: x[1])]
    
    # Log the report as a single string
    report = classification_report(true_labels, predictions, target_names=target_names)
    logger.info("\n" + report)

    del model, train_loader, val_loader
    gc.collect()
    torch.cuda.empty_cache()
    logger.info("Training finished!")

# ----------------- Run -----------------
if __name__ == "__main__":
    main()