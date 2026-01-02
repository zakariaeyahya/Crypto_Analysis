"""
Charge les données depuis les fichiers JSON et CSV pour les transformer
en documents indexables.
"""

import json
import csv
import math
from pathlib import Path
from datetime import datetime, timedelta

from app.rag.config import DATA_PATHS, CRYPTO_MAPPING, FAQ_DATA
from app.rag.logger import get_logger

logger = get_logger("document_loader")


class DocumentLoader:
    """Charge et transforme les données en documents indexables"""

    def __init__(self):
        """Initialise le loader"""
        self.data_paths = DATA_PATHS
        self.documents = []

    def _normalize_crypto(self, crypto):
        """
        Normalise le nom de la crypto
        Exemple: "Bitcoin" -> "BTC"
        """
        return CRYPTO_MAPPING.get(crypto, crypto)

    def _clean_nan(self, value):
        """Remplace NaN par None"""
        if isinstance(value, float) and math.isnan(value):
            return None
        return value

    def load_posts(self):
        """Charge les posts Twitter/Reddit"""
        documents = []
        fichier = self.data_paths.get("posts")

        if not fichier or not fichier.exists():
            logger.warning(f"Fichier posts non trouvé: {fichier}")
            return []

        try:
            with open(fichier, "r", encoding="utf-8") as f:
                posts = json.load(f)

            for post in posts:
                doc = {
                    "id": f"post_{post.get('id', '')}",
                    "type": "post",
                    "crypto": self._normalize_crypto(post.get("crypto", "UNKNOWN")),
                    "date": post.get("date", "")[:10],
                    "source": post.get("source", "unknown"),  # twitter ou reddit
                    "text": post.get("text", ""),
                    "metadata": {
                        "sentiment_score": self._clean_nan(post.get("sentiment_score")),
                        "sentiment_label": post.get("sentiment", "neutral"),
                        "price_change": self._clean_nan(post.get("price_change")),
                    }
                }
                documents.append(doc)

            logger.info(f"✓ Chargé {len(documents)} posts")
            return documents

        except Exception as e:
            logger.error(f"Erreur lors du chargement des posts: {e}")
            return []

    def load_timeseries(self):
        """Charge les résumés quotidiens de sentiment"""
        documents = []
        fichier = self.data_paths.get("timeseries")

        if not fichier or not fichier.exists():
            logger.warning(f"Fichier timeseries non trouvé: {fichier}")
            return []

        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            for entry in data:
                crypto = entry.get("crypto", "UNKNOWN")
                date = entry.get("date", "")
                sentiment_mean = self._clean_nan(entry.get("sentiment_mean"))
                positive_count = entry.get("positive_count", 0)
                negative_count = entry.get("negative_count", 0)

                text = (
                    f"Résumé {crypto} du {date}: "
                    f"Sentiment moyen {sentiment_mean}. "
                    f"{positive_count} positifs, {negative_count} négatifs."
                )

                doc = {
                    "id": f"daily_{crypto}_{date}",
                    "type": "daily_summary",
                    "crypto": crypto,
                    "date": date,
                    "source": "system",
                    "text": text,
                    "metadata": {
                        "sentiment_mean": sentiment_mean,
                        "positive_count": positive_count,
                        "negative_count": negative_count,
                    }
                }
                documents.append(doc)

            logger.info(f"✓ Chargé {len(documents)} résumés quotidiens")
            return documents

        except Exception as e:
            logger.error(f"Erreur lors du chargement des timeseries: {e}")
            return []

    def load_correlations(self):
        """Charge les analyses de corrélation"""
        documents = []
        fichier = self.data_paths.get("correlation")

        if not fichier or not fichier.exists():
            logger.warning(f"Fichier correlation non trouvé: {fichier}")
            return []

        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            for corr in data:
                crypto = corr.get("crypto", "UNKNOWN")
                pearson_r = self._clean_nan(corr.get("pearson_r"))

                # Interpréter la corrélation
                if pearson_r is None:
                    interpretation = "indéterminée"
                elif abs(pearson_r) < 0.3:
                    interpretation = "faible"
                elif abs(pearson_r) < 0.7:
                    interpretation = "modérée"
                else:
                    interpretation = "forte"

                text = (
                    f"Analyse corrélation {crypto}: "
                    f"Coefficient Pearson = {pearson_r}, "
                    f"corrélation {interpretation}."
                )

                doc = {
                    "id": f"correlation_{crypto}",
                    "type": "analysis",
                    "crypto": crypto,
                    "text": text,
                    "metadata": {
                        "pearson_r": pearson_r,
                        "p_value": self._clean_nan(corr.get("p_value")),
                    }
                }
                documents.append(doc)

            logger.info(f"✓ Chargé {len(documents)} analyses de corrélation")
            return documents

        except Exception as e:
            logger.error(f"Erreur lors du chargement des correlations: {e}")
            return []

    def load_lag_analysis(self):
        """Charge les analyses de lag temporel"""
        documents = []
        fichier = self.data_paths.get("lag")

        if not fichier or not fichier.exists():
            logger.warning(f"Fichier lag non trouvé: {fichier}")
            return []

        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            for lag in data:
                crypto = lag.get("crypto", "UNKNOWN")
                lag_hours = self._clean_nan(lag.get("lag_hours"))
                correlation = self._clean_nan(lag.get("correlation"))

                text = (
                    f"Analyse lag pour {crypto}: "
                    f"Délai détecté = {lag_hours} heures, "
                    f"corrélation = {correlation}."
                )

                doc = {
                    "id": f"lag_{crypto}",
                    "type": "lag_analysis",
                    "crypto": crypto,
                    "text": text,
                    "metadata": {
                        "lag_hours": lag_hours,
                        "correlation": correlation,
                    }
                }
                documents.append(doc)

            logger.info(f"✓ Chargé {len(documents)} analyses de lag")
            return documents

        except Exception as e:
            logger.error(f"Erreur lors du chargement du lag analysis: {e}")
            return []

    def load_prices(self):
        """Charge les prix historiques (résumés hebdomadaires)"""
        documents = []

        for crypto in ["BTC", "ETH", "SOL"]:
            key = f"prices_{crypto.lower()}"
            fichier = self.data_paths.get(key)

            if not fichier or not fichier.exists():
                logger.warning(f"Fichier prix {crypto} non trouvé: {fichier}")
                continue

            try:
                with open(fichier, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                # Grouper par semaine (7 jours)
                for i in range(0, len(rows), 7):
                    week = rows[i:i+7]
                    if not week:
                        continue

                    closes = [float(row.get("close", 0)) for row in week if row.get("close")]
                    if not closes:
                        continue

                    avg_price = sum(closes) / len(closes)
                    min_price = min(closes)
                    max_price = max(closes)
                    change = ((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] != 0 else 0

                    week_date = week[0].get("date", "")

                    text = (
                        f"Prix {crypto} semaine du {week_date}: "
                        f"Moyenne ${avg_price:.2f}, Min ${min_price:.2f}, Max ${max_price:.2f}, "
                        f"Variation {change:.2f}%"
                    )

                    doc = {
                        "id": f"price_{crypto}_{week_date}",
                        "type": "price",
                        "crypto": crypto,
                        "date": week_date,
                        "source": "historical",
                        "text": text,
                        "metadata": {
                            "avg_price": round(avg_price, 2),
                            "min_price": round(min_price, 2),
                            "max_price": round(max_price, 2),
                            "change_percent": round(change, 2),
                        }
                    }
                    documents.append(doc)

                logger.info(f"✓ Chargé {len([d for d in documents if d['crypto'] == crypto])} semaines de prix pour {crypto}")

            except Exception as e:
                logger.error(f"Erreur lors du chargement des prix {crypto}: {e}")
                continue

        return documents

    def load_faq(self):
        """Charge les FAQ statiques"""
        documents = []

        for i, faq in enumerate(FAQ_DATA):
            text = f"Question: {faq.get('question', '')}\nRéponse: {faq.get('answer', '')}"

            doc = {
                "id": f"faq_{i}",
                "type": "faq",
                "crypto": "ALL",
                "text": text,
                "metadata": {}
            }
            documents.append(doc)

        logger.info(f"✓ Chargé {len(documents)} FAQs")
        return documents

    def load_all(self):
        """Charge tous les documents de toutes les sources"""
        self.documents = []

        self.documents += self.load_posts()
        self.documents += self.load_timeseries()
        self.documents += self.load_correlations()
        self.documents += self.load_lag_analysis()
        self.documents += self.load_prices()
        self.documents += self.load_faq()

        logger.info(f"✓ TOTAL: {len(self.documents)} documents chargés")
        return self.documents

    def get_stats(self):
        """Retourne les statistiques par type de document"""
        stats = {}

        for doc in self.documents:
            doc_type = doc.get("type", "unknown")
            stats[doc_type] = stats.get(doc_type, 0) + 1

        logger.info(f"Statistiques: {stats}")
        return stats