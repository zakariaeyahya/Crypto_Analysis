import json
import csv
import math
from pathlib import Path
from typing import List, Optional
from functools import lru_cache
from datetime import datetime

from app.core.config import settings


def clean_nan(obj):
    """Remplace les NaN par None pour JSON valide"""
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(item) for item in obj]
    return obj


class DataService:
    """Service pour lire les données JSON et CSV"""

    CRYPTO_MAP = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}

    def __init__(self):
        self.gold_dir = settings.DATA_GOLD_DIR
        self.silver_dir = settings.DATA_SILVER_DIR
        self.bronze_dir = settings.DATA_BRONZE_DIR

    def get_sentiment_timeseries(self) -> List[dict]:
        """Charge sentiment_timeseries.json"""
        path = self.gold_dir / "sentiment_timeseries.json"
        with open(path, "r", encoding="utf-8") as f:
            # Gérer les NaN dans le JSON
            content = f.read().replace('NaN', 'null')
            data = json.loads(content)
            return clean_nan(data)

    @lru_cache(maxsize=1)
    def get_correlation(self) -> List[dict]:
        """Charge sentiment_price_correlation.json"""
        path = self.gold_dir / "sentiment_price_correlation.json"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @lru_cache(maxsize=1)
    def get_lag_analysis(self) -> List[dict]:
        """Charge lag_analysis.json"""
        path = self.gold_dir / "lag_analysis.json"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @lru_cache(maxsize=1)
    def get_enriched_posts(self) -> List[dict]:
        """Charge crypto_sent_enriched_price.json"""
        path = self.silver_dir / "crypto_sent_enriched_price.json"
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_sentiment_by_crypto(self, crypto: str, days: int = 30) -> List[dict]:
        """Filtre sentiment par crypto et limite aux N derniers jours"""
        data = self.get_sentiment_timeseries()
        # Map symbol to name
        crypto_map = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}
        crypto_name = crypto_map.get(crypto, crypto)
        
        filtered = [d for d in data if d["crypto"] == crypto_name]
        # Trier par date et prendre les N derniers
        filtered.sort(key=lambda x: x["date"], reverse=True)
        return filtered[:days]

    def get_correlation_by_crypto(self, crypto: str) -> Optional[dict]:
        """Récupère corrélation pour une crypto"""
        crypto_map = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}
        crypto_name = crypto_map.get(crypto, crypto)
        
        data = self.get_correlation()
        for item in data:
            if item["crypto"] == crypto_name:
                return item
        return None

    def get_lag_by_crypto(self, crypto: str) -> List[dict]:
        """Récupère lag analysis pour une crypto"""
        crypto_map = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}
        crypto_name = crypto_map.get(crypto, crypto)
        
        data = self.get_lag_analysis()
        return [d for d in data if d["crypto"] == crypto_name]

    def get_posts_by_crypto(self, crypto: str, limit: int = 50) -> List[dict]:
        """Récupère posts pour une crypto"""
        crypto_map = {"BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana"}
        crypto_name = crypto_map.get(crypto, crypto)
        
        data = self.get_enriched_posts()
        filtered = [d for d in data if d["crypto"] == crypto_name]
        # Trier par date desc
        filtered.sort(key=lambda x: x["date"], reverse=True)
        return filtered[:limit]

    def get_global_sentiment(self) -> dict:
        """Calcule sentiment global (moyenne des dernières valeurs)"""
        data = self.get_sentiment_timeseries()
        if not data:
            return {"score": 0, "label": "Neutral"}
        
        # Prendre les dernières entrées par crypto
        latest = {}
        for item in sorted(data, key=lambda x: x["date"], reverse=True):
            if item["crypto"] not in latest:
                latest[item["crypto"]] = item["sentiment_mean"]
            if len(latest) >= 3:
                break
        
        avg = sum(latest.values()) / len(latest) if latest else 0
        
        # Label basé sur le score (0-1 scale)
        if avg > 0.3:
            label = "Bullish"
        elif avg < -0.1:
            label = "Bearish"
        else:
            label = "Neutral"
        
        return {"score": round(avg, 4), "label": label}

    # ============================================
    # PRICE DATA (from CSV)
    # ============================================

    def _load_price_csv(self, symbol: str) -> List[dict]:
        """Charge le CSV des prix pour une crypto"""
        path = self.bronze_dir / symbol / "historical_prices.csv"
        if not path.exists():
            return []

        data = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "date": row["date"],
                    "price_open": float(row["price_open"]),
                    "price_close": float(row["price_close"]),
                    "volume": float(row["volume"])
                })
        return data

    def get_current_prices(self) -> List[dict]:
        """Récupère le dernier prix pour chaque crypto"""
        result = []
        for symbol, name in self.CRYPTO_MAP.items():
            data = self._load_price_csv(symbol)
            if data:
                # Trier par date et prendre le dernier
                data.sort(key=lambda x: x["date"], reverse=True)
                latest = data[0]
                previous = data[1] if len(data) > 1 else latest

                price = latest["price_close"]
                prev_price = previous["price_close"]
                change = ((price - prev_price) / prev_price) * 100 if prev_price else 0

                result.append({
                    "symbol": symbol,
                    "name": name,
                    "price": round(price, 2),
                    "change24h": round(change, 2)
                })
        return result

    def get_price_chart(self, symbol: str, days: int = 7) -> List[dict]:
        """Récupère l'historique des prix pour le graphique"""
        symbol = symbol.upper()
        data = self._load_price_csv(symbol)

        if not data:
            return []

        # Trier par date desc et prendre les N derniers jours
        data.sort(key=lambda x: x["date"], reverse=True)
        data = data[:days]
        data.reverse()  # Remettre en ordre chronologique

        result = []
        for item in data:
            # Formater la date
            try:
                date_obj = datetime.strptime(item["date"], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %b")
            except:
                formatted_date = item["date"]

            result.append({
                "date": formatted_date,
                "value": round(item["price_close"], 2)
            })

        return result

    def get_scatter_data(self, symbol: str, days: int = 30) -> List[dict]:
        """Données pour le scatter plot: sentiment vs price_change par jour"""
        symbol = symbol.upper()
        crypto_name = self.CRYPTO_MAP.get(symbol, symbol)

        # Charger sentiment timeseries
        sentiment_data = self.get_sentiment_timeseries()
        sentiment_by_date = {}
        for item in sentiment_data:
            if item["crypto"] == crypto_name:
                sentiment_by_date[item["date"]] = item["sentiment_mean"]

        # Charger prix
        price_data = self._load_price_csv(symbol)
        price_data.sort(key=lambda x: x["date"], reverse=True)
        price_data = price_data[:days + 1]  # +1 pour calculer le changement

        result = []
        for i in range(len(price_data) - 1):
            current = price_data[i]
            previous = price_data[i + 1]

            date = current["date"]
            sentiment = sentiment_by_date.get(date)

            if sentiment is not None:
                price_change = ((current["price_close"] - previous["price_close"]) / previous["price_close"]) * 100

                result.append({
                    "date": date,
                    "sentiment": round(sentiment * 100, 2),  # Convertir en -100 à +100
                    "price": round(current["price_close"], 2),
                    "priceChange": round(price_change, 2)
                })

        return result[:days]


# Singleton
data_service = DataService()
