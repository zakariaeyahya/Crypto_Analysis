"""
Kaggle dataset download service for fetching Bitcoin tweets with sentiment
"""
import sys
from pathlib import Path

# Add parent directory to sys.path to allow direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import logging
import json
from datetime import datetime
from typing import Optional
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class KaggleDownloader:
    """Service to download cryptocurrency datasets from Kaggle"""

    def __init__(self, dataset_name: str = "gauravduttakiit/bitcoin-tweets-16m-tweets-with-sentiment-tagged"):
        """
        Initialize Kaggle downloader

        Args:
            dataset_name: Full Kaggle dataset identifier (owner/dataset-name)
        """
        logger.info("Initializing Kaggle downloader...")

        self.dataset_name = dataset_name
        self.bronze_path = Path('data/bronze/kaggle')
        self.checkpoint_file = self.bronze_path / 'kaggle_downloads_checkpoint.json'

        # Create bronze directory if it doesn't exist
        self.bronze_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"[OK] Kaggle downloader initialized")
        logger.info(f"  Dataset: {dataset_name}")
        logger.info(f"  Bronze path: {self.bronze_path}")

    def _load_checkpoint(self) -> dict:
        """
        Load checkpoint file with download history

        Returns:
            Dictionary with download metadata
        """
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                    logger.info(f"[OK] Loaded checkpoint: {len(checkpoint.get('downloads', []))} downloads tracked")
                    return checkpoint
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")
                return {'downloads': []}
        return {'downloads': []}

    def _save_checkpoint(self, dataset_name: str, file_path: str, records_count: int):
        """
        Save checkpoint with download metadata

        Args:
            dataset_name: Name of the downloaded dataset
            file_path: Path where data was saved
            records_count: Number of records downloaded
        """
        try:
            checkpoint = self._load_checkpoint()

            # Add new download entry
            download_entry = {
                'dataset_name': dataset_name,
                'file_path': str(file_path),
                'records_count': records_count,
                'download_date': datetime.now().isoformat(),
                'last_checked': datetime.now().isoformat()
            }

            checkpoint['downloads'].append(download_entry)
            checkpoint['last_updated'] = datetime.now().isoformat()

            # Save checkpoint
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)

            logger.info(f"[OK] Checkpoint saved: {len(checkpoint['downloads'])} total downloads tracked")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def _is_already_downloaded(self, dataset_name: str) -> Optional[str]:
        """
        Check if dataset was already downloaded

        Args:
            dataset_name: Name of the dataset to check

        Returns:
            File path if already downloaded, None otherwise
        """
        checkpoint = self._load_checkpoint()

        for download in checkpoint.get('downloads', []):
            if download['dataset_name'] == dataset_name:
                file_path = Path(download['file_path'])
                if file_path.exists():
                    logger.info(f"[INFO] Dataset already downloaded: {file_path}")
                    logger.info(f"  Downloaded on: {download['download_date']}")
                    logger.info(f"  Records: {download['records_count']}")
                    return str(file_path)

        return None

    def download_dataset(self,
                        specific_file: str = None,
                        force_redownload: bool = False) -> pd.DataFrame:
        """
        Download Kaggle dataset with checkpoint system

        Args:
            specific_file: Specific CSV file to load (e.g., 'Bitcoin_tweets.csv')
            force_redownload: If True, download even if already exists

        Returns:
            DataFrame containing the dataset
        """
        logger.info("=" * 60)
        logger.info("Starting Kaggle dataset download")
        logger.info("=" * 60)
        logger.info(f"  Dataset: {self.dataset_name}")
        logger.info(f"  Specific file: {specific_file if specific_file else 'auto-detect'}")

        # Check if already downloaded
        if not force_redownload:
            existing_path = self._is_already_downloaded(self.dataset_name)
            if existing_path:
                logger.info("[INFO] Using existing downloaded dataset")
                try:
                    df = pd.read_csv(existing_path)
                    logger.info(f"[OK] Loaded {len(df)} records from existing file")
                    return df
                except Exception as e:
                    logger.warning(f"Failed to load existing file: {e}. Will re-download.")

        # Download dataset
        start_time = datetime.now()

        try:
            # Import kagglehub here to avoid dependency if not needed
            import kagglehub

            logger.info("[INFO] Downloading dataset from Kaggle...")
            logger.info("  This may take a few minutes depending on dataset size...")

            # Download dataset files to local cache
            download_path = kagglehub.dataset_download(self.dataset_name)
            logger.info(f"[OK] Dataset downloaded to: {download_path}")

            # Find CSV files in the downloaded directory
            download_dir = Path(download_path)
            csv_files = list(download_dir.glob("*.csv"))

            if not csv_files:
                raise ValueError(f"No CSV files found in downloaded dataset at {download_path}")

            logger.info(f"[INFO] Found {len(csv_files)} CSV file(s): {[f.name for f in csv_files]}")

            # Select which file to load
            if specific_file:
                csv_file = download_dir / specific_file
                if not csv_file.exists():
                    raise ValueError(f"Specified file '{specific_file}' not found. Available: {[f.name for f in csv_files]}")
            else:
                # Use the first (or largest) CSV file
                csv_file = max(csv_files, key=lambda f: f.stat().st_size)
                logger.info(f"[INFO] Auto-selected largest file: {csv_file.name}")

            # Load CSV into DataFrame
            logger.info(f"[INFO] Loading CSV file: {csv_file.name}")
            df = pd.read_csv(csv_file)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"[OK] Dataset loaded successfully in {duration:.2f} seconds")
            logger.info(f"  Records: {len(df)}")
            logger.info(f"  Columns: {list(df.columns)}")

            # Save to bronze layer
            bronze_csv_path = self._save_to_bronze(df)

            # Update checkpoint
            self._save_checkpoint(self.dataset_name, bronze_csv_path, len(df))

            logger.info("=" * 60)
            logger.info("[OK] Kaggle download completed successfully")
            logger.info("=" * 60)

            return df

        except ImportError as e:
            logger.error("[ERROR] kagglehub library not installed")
            logger.error("  Please install it with: pip install kagglehub[pandas-datasets]")
            raise

        except Exception as e:
            logger.error(f"[ERROR] Failed to download dataset: {e}")
            raise

    def _save_to_bronze(self, df: pd.DataFrame, filename: str = "bitcoin_tweets") -> Path:
        """
        Save downloaded dataset to Bronze layer

        Args:
            df: DataFrame to save
            filename: Base filename without extension

        Returns:
            Path to saved CSV file
        """
        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f"{filename}_{timestamp}.csv"
            csv_path = self.bronze_path / csv_filename

            # Save CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"[OK] Saved {len(df)} records to {csv_path}")

            # Save summary
            summary_path = self.bronze_path / f"{filename}_{timestamp}_summary.json"
            summary = {
                'total_records': len(df),
                'columns': list(df.columns),
                'dataset_name': self.dataset_name,
                'download_date': datetime.now().isoformat(),
                'file_location': str(csv_path),
                'file_size_mb': round(csv_path.stat().st_size / (1024 * 1024), 2)
            }

            # Add basic statistics if available
            if not df.empty:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    summary['sample_statistics'] = {
                        col: {
                            'mean': float(df[col].mean()),
                            'min': float(df[col].min()),
                            'max': float(df[col].max())
                        }
                        for col in numeric_cols[:3]  # Limit to first 3 numeric columns
                    }

            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            logger.info(f"[OK] Summary saved to {summary_path}")

            return csv_path

        except Exception as e:
            logger.error(f"[ERROR] Failed to save to bronze layer: {e}")
            raise


def main():
    """Main function to run Kaggle download service"""
    logger.info("=" * 60)
    logger.info("Kaggle Download Service - Bitcoin Tweets Dataset")
    logger.info("=" * 60)

    try:
        # Initialize downloader
        downloader = KaggleDownloader(
            dataset_name="gauravduttakiit/bitcoin-tweets-16m-tweets-with-sentiment-tagged"
        )

        # Download dataset (will skip if already downloaded)
        df = downloader.download_dataset(specific_file=None)

        # Display first 5 records
        logger.info("=" * 60)
        logger.info("First 5 records preview:")
        logger.info("=" * 60)
        print(df.head())

        logger.info("=" * 60)
        logger.info("[OK] Kaggle download service completed successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"[FATAL ERROR] Kaggle download service failed: {e}")
        raise
if __name__ == '__main__':
    main()
