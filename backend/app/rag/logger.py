"""
Configuration du systeme de logging pour tous les modules RAG
"""

import logging
import sys
import os
from pathlib import Path
from logging import StreamHandler, FileHandler

# =====================================================================
# CREER LE DOSSIER LOGS
# =====================================================================
# Chemin absolu vers le dossier logs (backend/logs/)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BACKEND_DIR / "logs"

# Creer le dossier s'il n'existe pas
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    LOG_DIR = Path(".")

LOG_FILE = LOG_DIR / "rag.log"

# =====================================================================
# CREER LOGGER PARENT
# =====================================================================
logger = logging.getLogger("rag")
logger.setLevel(logging.INFO)

# Eviter les doublons si le module est reimporte
if not logger.handlers:
    # =====================================================================
    # FORMAT DES LOGS
    # =====================================================================
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format)

    # =====================================================================
    # HANDLER CONSOLE (stdout)
    # =====================================================================
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # =====================================================================
    # HANDLER FICHIER (backend/logs/rag.log)
    # =====================================================================
    try:
        file_handler = FileHandler(
            str(LOG_FILE),
            mode='a',
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {LOG_FILE}")
    except Exception:
        pass  # Continue without file logging

# =====================================================================
# FONCTION POUR OBTENIR UN LOGGER ENFANT
# =====================================================================
def get_logger(name: str = None):
    """
    Retourne un logger enfant du logger parent "rag"

    Args:
        name (str): Nom du module (ex: "embedding", "retrieval")

    Returns:
        logging.Logger: Logger configure pour le module

    Exemple:
        from app.rag.logger import get_logger
        logger = get_logger("embedding")
        logger.info("Message de test")
    """
    if name:
        return logger.getChild(name)
    return logger


def get_log_file_path() -> str:
    """Retourne le chemin du fichier de log"""
    return str(LOG_FILE)
