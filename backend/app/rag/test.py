# backend/test_pinecone_format.py
import os
import numpy as np
from pinecone import Pinecone
from dotenv import load_dotenv
from app.rag.logger import get_logger

load_dotenv()

logger = get_logger("test_pinecone")

# Configuration
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

logger.info("=== TEST FORMAT PINECONE V3+ ===")

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Stats avant
stats_before = index.describe_index_stats()
logger.info(f"Avant: {stats_before.total_vector_count} vecteurs")

# Deux méthodes pour upsert :

# 1. ANCIENNE MÉTHODE (ne marche plus)
logger.info("1. Test ancienne methode (dict avec 'values'):")
try:
    index.upsert(
        vectors=[{
            "id": "test_old_format",
            "values": np.random.randn(384).tolist(),
            "metadata": {"test": "old"}
        }]
    )
    logger.info("   Ancienne methode marche")
except Exception as e:
    logger.error(f"   Erreur ancienne methode: {e}")

# 2. NOUVELLE MÉTHODE (tuples)
logger.info("2. Test nouvelle methode (tuples):")
try:
    index.upsert(
        vectors=[
            (
                "test_new_format",  # id
                np.random.randn(384).tolist(),  # vector
                {"test": "new", "type": "test"}  # metadata
            )
        ]
    )
    logger.info("   Nouvelle methode marche!")

    # Vérifier
    stats_after = index.describe_index_stats()
    logger.info(f"   Apres: {stats_after.total_vector_count} vecteurs")

    # Nettoyer
    index.delete(ids=["test_new_format"])
    logger.info("   Vecteur nettoye")

except Exception as e:
    logger.error(f"   Erreur nouvelle methode: {e}")

logger.info("=== FIN TEST ===")