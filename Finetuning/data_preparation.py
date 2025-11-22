"""
Data loading and analysis for fine-tuning
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging
from collections import Counter
import yaml

logger = logging.getLogger(__name__)


class DataLoader:
    """Class to load and analyze tweet dataset"""
    
    def __init__(self, csv_path: str, sample_size: Optional[int] = None):
        """
        Initialize DataLoader
        
        Args:
            csv_path: Path to CSV file
            sample_size: Number of tweets to load (None = all)
        """
        self.csv_path = Path(csv_path)
        self.sample_size = sample_size
        self.df = None
        
    def load_data(self, chunk_size: int = 10000) -> pd.DataFrame:
        """
        Load data in chunks (necessary for large files)
        
        Args:
            chunk_size: Chunk size for loading
            
        Returns:
            DataFrame with data
        """
        logger.info(f"Loading data from: {self.csv_path}")
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"File not found: {self.csv_path}")
        
        # If sample_size is defined, load by chunks and sample
        if self.sample_size:
            logger.info(f"Sampling {self.sample_size:,} tweets...")
            
            chunks = []
            total_loaded = 0
            
            for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size):
                chunks.append(chunk)
                total_loaded += len(chunk)
                
                if total_loaded >= self.sample_size * 1.5:  # Load a bit more for sampling
                    break
                
                if total_loaded % 100000 == 0:
                    logger.info(f"   Loaded {total_loaded:,} rows...")
            
            # Concatenate and sample
            self.df = pd.concat(chunks, ignore_index=True)
            if len(self.df) > self.sample_size:
                self.df = self.df.sample(n=self.sample_size, random_state=42).reset_index(drop=True)
                logger.info(f"Sample of {len(self.df):,} tweets created")
        else:
            # Load entire file (warning: can be very slow for 3GB)
            logger.warning("Loading complete file (may take time)...")
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"{len(self.df):,} tweets loaded")
        
        return self.df
    
    def analyze_data(self) -> dict:
        """
        Analyze data and return statistics
        
        Returns:
            Dictionary with statistics
        """
        if self.df is None:
            raise ValueError("Data must be loaded first (call load_data())")
        
        logger.info("=" * 60)
        logger.info("DATA ANALYSIS")
        logger.info("=" * 60)
        
        stats = {}
        
        # Basic information
        stats['total_records'] = len(self.df)
        stats['columns'] = list(self.df.columns)
        stats['missing_values'] = self.df.isnull().sum().to_dict()
        
        logger.info(f"Total tweets: {stats['total_records']:,}")
        logger.info(f"Columns: {', '.join(stats['columns'])}")
        
        # Sentiment distribution
        if 'Sentiment' in self.df.columns:
            sentiment_counts = self.df['Sentiment'].value_counts()
            stats['sentiment_distribution'] = sentiment_counts.to_dict()
            stats['sentiment_percentages'] = (sentiment_counts / len(self.df) * 100).to_dict()
            
            logger.info("Sentiment distribution:")
            for sentiment, count in sentiment_counts.items():
                percentage = stats['sentiment_percentages'][sentiment]
                logger.info(f"   {sentiment}: {count:,} ({percentage:.2f}%)")
        
        # Text statistics
        if 'text' in self.df.columns:
            # Tweet length
            text_lengths = self.df['text'].astype(str).str.len()
            stats['text_length'] = {
                'mean': float(text_lengths.mean()),
                'median': float(text_lengths.median()),
                'min': int(text_lengths.min()),
                'max': int(text_lengths.max()),
                'std': float(text_lengths.std())
            }
            
            logger.info("Text statistics:")
            logger.info(f"   Mean length: {stats['text_length']['mean']:.1f} characters")
            logger.info(f"   Median length: {stats['text_length']['median']:.1f} characters")
            logger.info(f"   Min: {stats['text_length']['min']}, Max: {stats['text_length']['max']}")
        
        # Temporal distribution (if Date available)
        if 'Date' in self.df.columns:
            try:
                self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
                stats['date_range'] = {
                    'start': str(self.df['Date'].min()),
                    'end': str(self.df['Date'].max())
                }
                logger.info(f"Period: {stats['date_range']['start']} to {stats['date_range']['end']}")
            except:
                logger.warning("Unable to parse dates")
        
        logger.info("=" * 60)
        
        return stats
    
    def get_data(self) -> pd.DataFrame:
        """
        Return loaded DataFrame
        
        Returns:
            DataFrame
        """
        if self.df is None:
            raise ValueError("Data must be loaded first")
        return self.df


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


if __name__ == "__main__":
    # Test DataLoader
    logging.basicConfig(level=logging.INFO)
    
    config = load_config()
    data_config = config['data']
    
    loader = DataLoader(
        csv_path=data_config['csv_path'],
        sample_size=data_config.get('sample_size')
    )
    
    df = loader.load_data(chunk_size=data_config.get('chunk_size', 10000))
    stats = loader.analyze_data()
    
    logger.info(f"Data loaded: {len(df):,} tweets")

