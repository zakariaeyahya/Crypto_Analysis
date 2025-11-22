# Crypto Analysis - Tweet Extraction

Project for extraction and analysis of cryptocurrency tweets.

## 🚀 Quick Start

### 1. Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file with your Twitter API credentials (see `.env.example`)

### 4. Extraction
```powershell
python extraction/services/twitter_extractor.py
```

## 📁 Structure

- `extraction/` : Tweet extraction code
- `data/bronze/` : Raw extracted data
- `data/silver/` : Cleaned data (coming soon)
- `data/gold/` : Enriched data (coming soon)

## 📖 Documentation

See `README_TWITTER_EXTRACTION.md` for more details.