from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
