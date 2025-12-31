from fastapi import APIRouter, Query
from typing import List, Optional

from app.services.data_service import data_service

router = APIRouter()


@router.get("")
async def get_events(
    crypto: Optional[str] = Query(default=None),
    sentiment: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500)
):
    """Liste des posts/événements avec filtres"""
    if crypto and crypto.upper() != "ALL":
        data = data_service.get_posts_by_crypto(crypto.upper(), limit=limit * 2)
    else:
        data = data_service.get_enriched_posts()[:limit * 2]
    
    # Filtrer par sentiment si spécifié
    if sentiment and sentiment.lower() != "all":
        data = [d for d in data if d.get("sentiment") == sentiment.lower()]
    
    return data[:limit]


@router.get("/stats")
async def get_events_stats(crypto: Optional[str] = Query(default=None)):
    """Statistiques des événements"""
    if crypto and crypto.upper() != "ALL":
        data = data_service.get_posts_by_crypto(crypto.upper(), limit=1000)
    else:
        data = data_service.get_enriched_posts()
    
    stats = {
        "total": len(data),
        "positive": sum(1 for d in data if d.get("sentiment") == "positive"),
        "negative": sum(1 for d in data if d.get("sentiment") == "negative"),
        "neutral": sum(1 for d in data if d.get("sentiment") == "neutral"),
    }
    
    return stats
