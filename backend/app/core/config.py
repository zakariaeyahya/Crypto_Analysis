from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Crypto Dashboard API"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Data paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_GOLD_DIR: Path = BASE_DIR / "data" / "gold"
    DATA_SILVER_DIR: Path = BASE_DIR / "data" / "silver" / "enriched_data"
    DATA_BRONZE_DIR: Path = BASE_DIR / "data" / "bronze"

    # =====================================================================
    # RAG - PINECONE
    # =====================================================================
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "crypto-sentiment-rag")
    PINECONE_CLOUD: str = os.getenv("PINECONE_CLOUD", "aws")
    PINECONE_REGION: str = os.getenv("PINECONE_REGION", "us-east-1")

    # =====================================================================
    # RAG - EMBEDDING
    # =====================================================================
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    # =====================================================================
    # RAG - LLM
    # =====================================================================
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # =====================================================================
    # RAG - PARAMETERS
    # =====================================================================
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_MIN_SCORE: float = float(os.getenv("RAG_MIN_SCORE", "0.5"))

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()