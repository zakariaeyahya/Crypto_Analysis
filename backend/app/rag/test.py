# backend/test_pinecone_format.py
import os
import numpy as np
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Configuration
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

print("=== TEST FORMAT PINECONE V3+ ===")

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

# Stats avant
stats_before = index.describe_index_stats()
print(f"Avant: {stats_before.total_vector_count} vecteurs")

# Deux méthodes pour upsert :

# 1. ANCIENNE MÉTHODE (ne marche plus)
print("\n1. Test ancienne méthode (dict avec 'values'):")
try:
    index.upsert(
        vectors=[{
            "id": "test_old_format",
            "values": np.random.randn(384).tolist(),
            "metadata": {"test": "old"}
        }]
    )
    print("   ✅ Ancienne méthode marche")
except Exception as e:
    print(f"   ❌ Erreur ancienne méthode: {e}")

# 2. NOUVELLE MÉTHODE (tuples)
print("\n2. Test nouvelle méthode (tuples):")
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
    print("   ✅ Nouvelle méthode marche!")
    
    # Vérifier
    stats_after = index.describe_index_stats()
    print(f"   Après: {stats_after.total_vector_count} vecteurs")
    
    # Nettoyer
    index.delete(ids=["test_new_format"])
    print("   🗑️  Vecteur nettoyé")
    
except Exception as e:
    print(f"   ❌ Erreur nouvelle méthode: {e}")

print("\n=== FIN TEST ===")