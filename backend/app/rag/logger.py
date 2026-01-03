"""
Configuration du système de logging pour tous les modules RAG
"""

import logging
import sys
from pathlib import Path
from logging import StreamHandler, FileHandler

# =====================================================================
# CRÉER LOGGER PARENT
# =====================================================================
logger = logging.getLogger("rag")
logger.setLevel(logging.INFO)

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
logger.addHandler(console_handler)

# =====================================================================
# HANDLER FICHIER (logs/rag.log)
# =====================================================================
log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

file_handler = FileHandler(log_dir / "rag.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# =====================================================================
# FONCTION POUR OBTENIR UN LOGGER ENFANT
# =====================================================================
def get_logger(name):
    """
    Retourne un logger enfant du logger parent "rag"
    
    Args:
        name (str): Nom du module (ex: "embedding", "retrieval")
    
    Returns:
        logging.Logger: Logger configuré pour le module
    
    Exemple:
        from backend.app.rag.logger import get_logger
        logger = get_logger("embedding")
        logger.info("Message de test")
    """
    if name:
        return logger.getChild(name)
    else:
        return logger