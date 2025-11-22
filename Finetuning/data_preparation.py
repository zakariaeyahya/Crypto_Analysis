"""
Chargement et analyse des données pour le fine-tuning
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
    """Classe pour charger et analyser le dataset de tweets"""
    
    def __init__(self, csv_path: str, sample_size: Optional[int] = None):
        """
        Initialiser le DataLoader
        
        Args:
            csv_path: Chemin vers le fichier CSV
            sample_size: Nombre de tweets à charger (None = tout)
        """
        self.csv_path = Path(csv_path)
        self.sample_size = sample_size
        self.df = None
        
    def load_data(self, chunk_size: int = 10000) -> pd.DataFrame:
        """
        Charger les données en chunks (nécessaire pour fichiers volumineux)
        
        Args:
            chunk_size: Taille des chunks pour le chargement
            
        Returns:
            DataFrame avec les données
        """
        logger.info(f"Chargement des donnees depuis: {self.csv_path}")
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Fichier non trouve: {self.csv_path}")
        
        # Si sample_size est défini, charger par chunks et échantillonner
        if self.sample_size:
            logger.info(f"Echantillonnage de {self.sample_size:,} tweets...")
            
            chunks = []
            total_loaded = 0
            
            for chunk in pd.read_csv(self.csv_path, chunksize=chunk_size):
                chunks.append(chunk)
                total_loaded += len(chunk)
                
                if total_loaded >= self.sample_size * 1.5:  # Charger un peu plus pour échantillonnage
                    break
                
                if total_loaded % 100000 == 0:
                    logger.info(f"   Charge {total_loaded:,} lignes...")
            
            # Concaténer et échantillonner
            self.df = pd.concat(chunks, ignore_index=True)
            if len(self.df) > self.sample_size:
                self.df = self.df.sample(n=self.sample_size, random_state=42).reset_index(drop=True)
                logger.info(f"Echantillon de {len(self.df):,} tweets cree")
        else:
            # Charger tout le fichier (attention: peut être très lent pour 3GB)
            logger.warning("Chargement du fichier complet (peut prendre du temps)...")
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"{len(self.df):,} tweets charges")
        
        return self.df
    
    def analyze_data(self) -> dict:
        """
        Analyser les données et retourner des statistiques
        
        Returns:
            Dictionnaire avec statistiques
        """
        if self.df is None:
            raise ValueError("Les données doivent être chargées d'abord (appeler load_data())")
        
        logger.info("=" * 60)
        logger.info("ANALYSE DES DONNÉES")
        logger.info("=" * 60)
        
        stats = {}
        
        # Informations de base
        stats['total_records'] = len(self.df)
        stats['columns'] = list(self.df.columns)
        stats['missing_values'] = self.df.isnull().sum().to_dict()
        
        logger.info(f"Total de tweets: {stats['total_records']:,}")
        logger.info(f"Colonnes: {', '.join(stats['columns'])}")
        
        # Distribution des sentiments
        if 'Sentiment' in self.df.columns:
            sentiment_counts = self.df['Sentiment'].value_counts()
            stats['sentiment_distribution'] = sentiment_counts.to_dict()
            stats['sentiment_percentages'] = (sentiment_counts / len(self.df) * 100).to_dict()
            
            logger.info("Distribution des sentiments:")
            for sentiment, count in sentiment_counts.items():
                percentage = stats['sentiment_percentages'][sentiment]
                logger.info(f"   {sentiment}: {count:,} ({percentage:.2f}%)")
        
        # Statistiques sur les textes
        if 'text' in self.df.columns:
            # Longueur des tweets
            text_lengths = self.df['text'].astype(str).str.len()
            stats['text_length'] = {
                'mean': float(text_lengths.mean()),
                'median': float(text_lengths.median()),
                'min': int(text_lengths.min()),
                'max': int(text_lengths.max()),
                'std': float(text_lengths.std())
            }
            
            logger.info("Statistiques sur les textes:")
            logger.info(f"   Longueur moyenne: {stats['text_length']['mean']:.1f} caracteres")
            logger.info(f"   Longueur mediane: {stats['text_length']['median']:.1f} caracteres")
            logger.info(f"   Min: {stats['text_length']['min']}, Max: {stats['text_length']['max']}")
        
        # Distribution temporelle (si Date disponible)
        if 'Date' in self.df.columns:
            try:
                self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
                stats['date_range'] = {
                    'start': str(self.df['Date'].min()),
                    'end': str(self.df['Date'].max())
                }
                logger.info(f"Periode: {stats['date_range']['start']} a {stats['date_range']['end']}")
            except:
                logger.warning("Impossible de parser les dates")
        
        logger.info("=" * 60)
        
        return stats
    
    def get_data(self) -> pd.DataFrame:
        """
        Retourner le DataFrame chargé
        
        Returns:
            DataFrame
        """
        if self.df is None:
            raise ValueError("Les données doivent être chargées d'abord")
        return self.df


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Charger la configuration depuis le fichier YAML
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Dictionnaire de configuration
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


if __name__ == "__main__":
    # Test du DataLoader
    logging.basicConfig(level=logging.INFO)
    
    config = load_config()
    data_config = config['data']
    
    loader = DataLoader(
        csv_path=data_config['csv_path'],
        sample_size=data_config.get('sample_size')
    )
    
    df = loader.load_data(chunk_size=data_config.get('chunk_size', 10000))
    stats = loader.analyze_data()
    
    logger.info(f"Donnees chargees: {len(df):,} tweets")

