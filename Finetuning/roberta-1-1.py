## Block 1: Install Dependencies
# ====== Cellule 2 ======
# Install other packages
# !pip install -q transformers pandas numpy scikit-learn matplotlib seaborn tqdm pyyaml safetensors
# Check GPU availability
import torch
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
# ====== Cellule 3 ======
import torch
print(torch.__version__)
print(torch.version.cuda)
print(torch.cuda.get_device_name(0))
## Block 2: Imports and Setup
# ====== Cellule 5 ======
import os
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torch.optim import AdamW
from transformers import (
    RobertaForSequenceClassification,
    RobertaTokenizer,
    get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
import re
from collections import Counter
from tqdm import tqdm
import json
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import logging
warnings.filterwarnings('ignore')
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.info("All imports successful!")
## Block 3: Configuration
# ====== Cellule 7 ======
# ========== CONFIGURATION ==========
# Dataset settings
CSV_PATH = "/kaggle/input/bitcoin-tweets-16m-tweets-with-sentiment-tagged/mbsa.csv"  # Change this to your dataset path
SAMPLE_SIZE = 500000  # Number of tweets to use (None = use all, but may be slow)
CHUNK_SIZE = 10000  # For loading large files
# Model settings
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"  # Pre-trained model
NUM_LABELS = 2  # Number of classes (2 for Positive/Negative, 3 if including Neutral)
MAX_LENGTH = 128  # Maximum sequence length (reduce to 64 if GPU memory is limited)
# Training settings
BATCH_SIZE = 16  # Adjust based on GPU memory (8-32 typical)
LEARNING_RATE = 1e-5  # Reduced from 2e-5 to prevent overfitting
NUM_EPOCHS = 8  # Increased from 3 to 8 (early stopping will prevent overfitting)
WARMUP_STEPS = 500
WEIGHT_DECAY = 0.01
MAX_GRAD_NORM = 1.0
USE_FP16 = True  # Mixed precision (saves memory)
# Early stopping (to prevent overfitting)
EARLY_STOPPING = True
EARLY_STOPPING_PATIENCE = 3  # Stop if no improvement for 3 epochs
# Data split
TRAIN_SIZE = 0.8
VAL_SIZE = 0.1
TEST_SIZE = 0.1
# Reproducibility
SEED = 42
# Paths (for Kaggle/Colab)
MODELS_DIR = "/kaggle/working/models"
RESULTS_DIR = "/kaggle/working/results"
CHECKPOINTS_DIR = "/kaggle/working/checkpoints"
# Create directories
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
logger.info("Configuration loaded!")
# ====== Cellule 8 ======
# Set random seeds for reproducibility
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
# Setup device
def setup_device():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU")
    return device
# Format time
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
set_seed(SEED)
device = setup_device()
logger.info("Utilities loaded!")
## Block 5: Text Preprocessing
# ====== Cellule 10 ======
class TextPreprocessor:
    """Clean and preprocess tweet texts"""
    def __init__(self, remove_urls=True, handle_mentions=True, 
                 handle_hashtags=True, normalize_spaces=True):
        self.remove_urls = remove_urls
        self.handle_mentions = handle_mentions
        self.handle_hashtags = handle_hashtags
        self.normalize_spaces = normalize_spaces
    def clean_text(self, text):
        if pd.isna(text):
            return ""
        text = str(text)
        if self.remove_urls:
            text = re.sub(r'http\\S+|www\\.\\S+', '', text)
        if self.handle_mentions:
            text = re.sub(r'@(\\w+)', r'\\1', text)
        if self.handle_hashtags:
            text = re.sub(r'#(\\w+)', r'\\1', text)
        if self.normalize_spaces:
            text = re.sub(r'\\s+', ' ', text)
        return text.strip()
    def preprocess_dataframe(self, df, text_column='text'):
        logger.info(f"Preprocessing {len(df):,} texts...")
        df = df.copy()
        df[text_column] = df[text_column].apply(self.clean_text)
        initial_count = len(df)
        df = df[df[text_column].str.len() > 0].reset_index(drop=True)
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"   {removed:,} empty texts removed")
        logger.info(f"Preprocessing completed: {len(df):,} valid texts")
        return df
preprocessor = TextPreprocessor()
logger.info("Preprocessor ready!")
## Block 6: Load and Prepare Data
# ====== Cellule 12 ======
# Load data
logger.info("Loading data...")
if SAMPLE_SIZE:
    # Load in chunks and sample
    chunks = []
    total_loaded = 0
    for chunk in pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE):
        chunks.append(chunk)
        total_loaded += len(chunk)
        if total_loaded >= SAMPLE_SIZE * 1.5:
            break
    df = pd.concat(chunks, ignore_index=True)
    if len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=SEED).reset_index(drop=True)
    logger.info(f"Loaded sample: {len(df):,} tweets")
else:
    df = pd.read_csv(CSV_PATH)
    logger.info(f"Loaded all data: {len(df):,} tweets")
# Check columns
logger.info(f"Columns: {list(df.columns)}")
logger.info(f"Shape: {df.shape}")
# Check sentiment distribution
if 'Sentiment' in df.columns:
    logger.info(f"Sentiment distribution:")
    logger.info(f"{df['Sentiment'].value_counts()}")
    logger.info(f"{df['Sentiment'].value_counts(normalize=True) * 100}")
logger.info("Data loaded successfully!")
## Block 7: Preprocess Data
# ====== Cellule 14 ======
# Suppress sklearn deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='sklearn')
# Preprocess texts
df = preprocessor.preprocess_dataframe(df, text_column='text')
# Encode labels
label_encoder = LabelEncoder()
df['label_encoded'] = label_encoder.fit_transform(df['Sentiment'])
label_mapping = {label: idx for idx, label in enumerate(label_encoder.classes_)}
logger.info(f"Label mapping: {label_mapping}")
# Calculate class weights for imbalanced data
label_counts = Counter(df['label_encoded'])
total = len(df)
class_weights = torch.tensor([
    total / (NUM_LABELS * label_counts[i]) for i in range(NUM_LABELS)
], dtype=torch.float32).to(device)
logger.info(f"Class weights: {class_weights.cpu().numpy()}")
# Split data
logger.info("Splitting data...")
train_df, temp_df = train_test_split(
    df,
    test_size=(VAL_SIZE + TEST_SIZE),
    stratify=df['Sentiment'],
    random_state=SEED
)
val_ratio = VAL_SIZE / (VAL_SIZE + TEST_SIZE)
val_df, test_df = train_test_split(
    temp_df,
    test_size=(1 - val_ratio),
    stratify=temp_df['Sentiment'],
    random_state=SEED
)
logger.info(f"Train: {len(train_df):,} ({len(train_df)/len(df)*100:.1f}%)")
logger.info(f"Validation: {len(val_df):,} ({len(val_df)/len(df)*100:.1f}%)")
logger.info(f"Test: {len(test_df):,} ({len(test_df)/len(df)*100:.1f}%)")
# Save splits
train_df.to_csv(f"{RESULTS_DIR}/train_split.csv", index=False)
val_df.to_csv(f"{RESULTS_DIR}/val_split.csv", index=False)
test_df.to_csv(f"{RESULTS_DIR}/test_split.csv", index=False)
logger.info("Data preprocessing completed!")
## Block 8: Create Dataset and DataLoaders
# ====== Cellule 16 ======
class TweetDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    def __len__(self):
        return len(self.texts)
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }
# Load tokenizer
logger.info("Loading tokenizer...")
tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
logger.info(f"Tokenizer loaded (vocab size: {len(tokenizer)})")
# Create datasets
train_dataset = TweetDataset(
    texts=train_df['text'].tolist(),
    labels=train_df['label_encoded'].tolist(),
    tokenizer=tokenizer,
    max_length=MAX_LENGTH
)
val_dataset = TweetDataset(
    texts=val_df['text'].tolist(),
    labels=val_df['label_encoded'].tolist(),
    tokenizer=tokenizer,
    max_length=MAX_LENGTH
)
# Create weights for each sample (for WeightedRandomSampler)
sample_weights = [class_weights[label].item() for label in train_df['label_encoded']]
sampler = WeightedRandomSampler(
    weights=sample_weights,
    num_samples=len(sample_weights),
    replacement=True
)
# Create DataLoaders
# Use sampler instead of shuffle=True to balance batches
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=sampler)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
logger.info(f"Using WeightedRandomSampler to balance batches")
logger.info(f"Sample weights per class: Negative={class_weights[0].item():.4f}, Positive={class_weights[1].item():.4f}")
logger.info(f"DataLoaders created:")
logger.info(f"  Train batches: {len(train_loader)}")
logger.info(f"  Val batches: {len(val_loader)}")
## Block 9: Load Model
# ====== Cellule 18 ======
# Load model
logger.info(f"Loading model: {MODEL_NAME}")
logger.info(f"Note: Model will be loaded with {NUM_LABELS} labels (ignoring mismatch if pre-trained has different number)")
import warnings
warnings.filterwarnings("ignore", message=".*Some weights of RobertaForSequenceClassification were not initialized.*")
# Check PyTorch version
torch_version = torch.__version__
logger.info(f"PyTorch version: {torch_version}")
# Force safetensors to avoid PyTorch < 2.6 security issue with .bin files
# With PyTorch >= 2.6, both formats work. With < 2.6, we need safetensors only
model = RobertaForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=NUM_LABELS,
    ignore_mismatched_sizes=True,
    use_safetensors=True,  # Prefer safetensors (works with all PyTorch versions)
)
model = model.to(device)
warnings.filterwarnings("default")
# Count parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
logger.info(f"Total parameters: {total_params:,}")
logger.info(f"Trainable parameters: {trainable_params:,}")
logger.info("Model loaded successfully!")
## Block 10: Setup Optimizer and Scheduler
# ====== Cellule 20 ======
# Setup optimizer
param_optimizer = list(model.named_parameters())
no_decay = ['bias', 'LayerNorm.weight']
optimizer_grouped_parameters = [
    {\
        'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
        'weight_decay': WEIGHT_DECAY
    },
    {\
        'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
        'weight_decay': 0.0
    }
]
optimizer = AdamW(optimizer_grouped_parameters, lr=LEARNING_RATE)
# Setup scheduler
num_training_steps = len(train_loader) * NUM_EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=WARMUP_STEPS,
    num_training_steps=num_training_steps
)
# Loss function with class weights to handle imbalance
criterion = nn.CrossEntropyLoss(weight=class_weights)
# Mixed precision scaler (using new API)
scaler = torch.amp.GradScaler('cuda') if USE_FP16 and device.type == 'cuda' else None
logger.info(f"Optimizer: AdamW (lr={LEARNING_RATE})")
logger.info(f"Scheduler: Linear with warmup ({WARMUP_STEPS} steps)")
logger.info(f"Total training steps: {num_training_steps}")
logger.info(f"Mixed precision (FP16): {USE_FP16}")
logger.info(f"Class weights in loss: {class_weights.cpu().numpy()}")
logger.info(f"Using WeightedRandomSampler: True (batches will be balanced ~50/50)")
## Block 11: Training Functions
# ====== Cellule 22 ======
def train_epoch(model, train_loader, optimizer, scheduler, device, criterion, scaler=None):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    num_batches = 0
    progress_bar = tqdm(train_loader, desc="Training")
    for batch in progress_bar:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        optimizer.zero_grad()
        if scaler is not None:
            with torch.amp.autocast(device_type='cuda'):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                # Use our criterion with class weights
                loss = criterion(logits, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
            scaler.step(optimizer)
            scaler.update()
        else:
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            # Use our criterion with class weights
            loss = criterion(logits, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
            optimizer.step()
        scheduler.step()
        total_loss += loss.item()
        num_batches += 1
        progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
    return total_loss / num_batches
def validate(model, val_loader, device):
    """Validate the model"""
    model.eval()
    total_loss = 0
    predictions = []
    true_labels = []
    with torch.no_grad():
        for batch in tqdm(val_loader, desc="Validation"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()
            logits = outputs.logits
            preds = torch.argmax(logits, dim=1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    avg_loss = total_loss / len(val_loader)
    accuracy = accuracy_score(true_labels, predictions)
    f1 = f1_score(true_labels, predictions, average='macro')
    return avg_loss, accuracy, f1
logger.info("Training functions ready!")