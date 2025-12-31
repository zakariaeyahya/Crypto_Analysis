from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.services.data_service import data_service

router = APIRouter()


@router.get("")
async def get_cryptos():
    """Liste des cryptos avec prix actuels et variation 24h"""
    return data_service.get_current_prices()


@router.get("/{symbol}")
async def get_crypto(symbol: str):
    """Détails d'une crypto avec prix"""
    symbol = symbol.upper()
    prices = data_service.get_current_prices()

    for crypto in prices:
        if crypto["symbol"] == symbol:
            return crypto

    raise HTTPException(status_code=404, detail=f"Crypto {symbol} not found")


@router.get("/{symbol}/chart")
async def get_crypto_chart(
    symbol: str,
    days: int = Query(default=7, ge=1, le=365)
):
    """Historique des prix pour le graphique"""
    symbol = symbol.upper()
    data = data_service.get_price_chart(symbol, days)

    if not data:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol}")

    return {
        "symbol": symbol,
        "days": days,
        "data": data
    }
