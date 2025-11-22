"""
Preprocessing and text cleaning for fine-tuning
"""
import re
import pandas as pd
import numpy as np
from typing import List, Tuple
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """Class to clean and preprocess tweet texts"""
    
    def __init__(self, 
                 remove_urls: bool = True,
                 handle_mentions: bool = True,
                 handle_hashtags: bool = True,
                 normalize_spaces: bool = True,
                 handle_emojis: str = "keep"):
        """
        Initialize preprocessor
        
        Args:
            remove_urls: Remove URLs
            handle_mentions: Handle @user mentions
            handle_hashtags: Handle hashtags (keep text, remove #)
            normalize_spaces: Normalize multiple spaces
            handle_emojis: "keep", "remove", or "convert"
        """
        self.remove_urls = remove_urls
        self.handle_mentions = handle_mentions
        self.handle_hashtags = handle_hashtags
        self.normalize_spaces = normalize_spaces
        self.handle_emojis = handle_emojis
        
    def clean_text(self, text: str) -> str:
        """
        Clean text according to configured rules
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Remove URLs
        if self.remove_urls:
            text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Handle @user mentions (keep text)
        if self.handle_mentions:
            text = re.sub(r'@(\w+)', r'\1', text)
        
        # Handle hashtags (keep text, remove #)
        if self.handle_hashtags:
            text = re.sub(r'#(\w+)', r'\1', text)
        
        # Normalize multiple spaces
        if self.normalize_spaces:
            text = re.sub(r'\s+', ' ', text)
        
        # Handle emojis
        if self.handle_emojis == "remove":
            # Remove emojis (simplified pattern)
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map
                u"\U0001F1E0-\U0001F1FF"  # flags
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                "]+", flags=re.UNICODE)
            text = emoji_pattern.sub('', text)
        elif self.handle_emojis == "convert":
            # Convert to text (simplified - could use emoji library)
            pass  # To implement if necessary
        
        # Clean spaces at start/end
        text = text.strip()
        
        return text
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """
        Preprocess all text columns of a DataFrame
        
        Args:
            df: DataFrame to preprocess
            text_column: Name of column containing texts
            
        Returns:
            DataFrame with cleaned texts
        """
        logger.info(f"Preprocessing {len(df):,} texts...")
        
        df = df.copy()
        df[text_column] = df[text_column].apply(self.clean_text)
        
        # Remove empty texts after cleaning
        initial_count = len(df)
        df = df[df[text_column].str.len() > 0].reset_index(drop=True)
        removed = initial_count - len(df)
        
        if removed > 0:
            logger.info(f"   {removed:,} empty texts removed")
        
        logger.info(f"Preprocessing completed: {len(df):,} valid texts")
        
        return df


class LabelEncoderWrapper:
    """Wrapper to encode sentiment labels"""
    
    def __init__(self):
        self.encoder = LabelEncoder()
        self.label_mapping = {}
        self.reverse_mapping = {}
    
    def fit(self, labels: pd.Series):
        """
        Train encoder on labels
        
        Args:
            labels: Pandas Series with labels
        """
        unique_labels = sorted(labels.unique())
        self.encoder.fit(unique_labels)
        
        # Create mapping
        for i, label in enumerate(unique_labels):
            encoded = self.encoder.transform([label])[0]
            self.label_mapping[label] = int(encoded)
            self.reverse_mapping[int(encoded)] = label
        
        logger.info(f"Labels encoded: {self.label_mapping}")
    
    def transform(self, labels: pd.Series) -> np.ndarray:
        """
        Encode labels
        
        Args:
            labels: Pandas Series with labels
            
        Returns:
            NumPy array with encoded labels
        """
        return self.encoder.transform(labels)
    
    def inverse_transform(self, encoded_labels: np.ndarray) -> List[str]:
        """
        Decode labels
        
        Args:
            encoded_labels: NumPy array with encoded labels
            
        Returns:
            List of decoded labels
        """
        return self.encoder.inverse_transform(encoded_labels)
    
    def get_num_classes(self) -> int:
        """Return number of classes"""
        return len(self.label_mapping)


def split_data(df: pd.DataFrame,
               text_column: str = 'text',
               label_column: str = 'Sentiment',
               train_size: float = 0.8,
               val_size: float = 0.1,
               test_size: float = 0.1,
               stratify: bool = True,
               random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split dataset into train/val/test
    
    Args:
        df: DataFrame to split
        text_column: Name of text column
        label_column: Name of label column
        train_size: Proportion for train
        val_size: Proportion for validation
        test_size: Proportion for test
        stratify: If True, stratify by class
        random_state: Seed for reproducibility
        
    Returns:
        Tuple (train_df, val_df, test_df)
    """
    logger.info("=" * 60)
    logger.info("DATA SPLITTING")
    logger.info("=" * 60)
    
    # Check that proportions sum to 1
    total = train_size + val_size + test_size
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Proportions must sum to 1.0, got: {total}")
    
    stratify_col = df[label_column] if stratify else None
    
    # First split: train vs (val + test)
    train_df, temp_df = train_test_split(
        df,
        test_size=(val_size + test_size),
        stratify=stratify_col,
        random_state=random_state
    )
    
    # Second split: val vs test
    val_ratio = val_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - val_ratio),
        stratify=temp_df[label_column] if stratify else None,
        random_state=random_state
    )
    
    logger.info(f"Train: {len(train_df):,} ({len(train_df)/len(df)*100:.1f}%)")
    logger.info(f"Validation: {len(val_df):,} ({len(val_df)/len(df)*100:.1f}%)")
    logger.info(f"Test: {len(test_df):,} ({len(test_df)/len(df)*100:.1f}%)")
    
    # Display distribution by class for each split
    if stratify:
        logger.info("\nClass distribution:")
        for split_name, split_df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
            dist = split_df[label_column].value_counts(normalize=True) * 100
            logger.info(f"   {split_name}: {dict(dist)}")
    
    logger.info("=" * 60)
    
    return train_df, val_df, test_df

