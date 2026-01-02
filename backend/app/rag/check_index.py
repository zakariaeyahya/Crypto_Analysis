import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Charger les variables d'environnement
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_REGION = os.getenv("PINECONE_REGION")  # ex: "us-east-1"

# Créer une instance Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Vérifier si l'index existe
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    print(f"L'index '{PINECONE_INDEX_NAME}' n'existe pas, création en cours...")
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,  # à adapter selon ton embedding model
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION)
    )

# Se connecter à l'index
index = pc.Index(PINECONE_INDEX_NAME)

# Afficher les stats
stats = index.describe_index_stats()
print("Stats de l'index:", stats)

