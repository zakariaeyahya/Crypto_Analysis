from fastapi import APIRouter, Query
from typing import List

from app.services.data_service import data_service

router = APIRouter()


@router.get("/global")
async def get_global_sentiment():
    """Sentiment global du marché"""
    return data_service.get_global_sentiment()


@router.get("/{symbol}/timeline")
async def get_sentiment_timeline(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """Timeline sentiment pour une crypto"""
    symbol = symbol.upper()
    data = data_service.get_sentiment_by_crypto(symbol, days)
    
    if not data:
        return {"symbol": symbol, "current": 0, "average": 0, "data": []}
    
    # Calculer current et average
    current = data[0]["sentiment_mean"] if data else 0
    average = sum(d["sentiment_mean"] for d in data) / len(data) if data else 0
    
    return {
        "symbol": symbol,
        "current": round(current, 4),
        "average": round(average, 4),
        "data": data
    }
