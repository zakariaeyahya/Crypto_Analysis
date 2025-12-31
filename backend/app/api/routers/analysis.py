from fastapi import APIRouter, HTTPException, Query

from app.services.data_service import data_service

router = APIRouter()


@router.get("/{symbol}/correlation")
async def get_correlation(symbol: str):
    """Corrélation sentiment/prix pour une crypto"""
    symbol = symbol.upper()
    correlation = data_service.get_correlation_by_crypto(symbol)
    
    if not correlation:
        raise HTTPException(status_code=404, detail=f"No correlation data for {symbol}")
    
    return correlation


@router.get("/{symbol}/lag")
async def get_lag_analysis(symbol: str):
    """Analyse de lag (daily, weekly, monthly) pour une crypto"""
    symbol = symbol.upper()
    lag_data = data_service.get_lag_by_crypto(symbol)
    
    if not lag_data:
        raise HTTPException(status_code=404, detail=f"No lag analysis for {symbol}")
    
    return lag_data


@router.get("/{symbol}/stats")
async def get_analysis_stats(symbol: str):
    """Statistiques complètes pour une crypto"""
    symbol = symbol.upper()
    
    correlation = data_service.get_correlation_by_crypto(symbol)
    lag_data = data_service.get_lag_by_crypto(symbol)
    
    if not correlation:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    
    # Déterminer le label de corrélation
    r = abs(correlation.get("pearson_r", 0))
    if r >= 0.7:
        label = "Forte"
    elif r >= 0.4:
        label = "Moyenne"
    elif r >= 0.2:
        label = "Faible"
    else:
        label = "Négligeable"
    
    return {
        "symbol": symbol,
        "correlation": correlation,
        "correlationLabel": label,
        "lagAnalysis": lag_data
    }


@router.get("/{symbol}/scatter")
async def get_scatter_data(
    symbol: str,
    days: int = Query(default=30, ge=1, le=365)
):
    """Données pour le scatter plot: sentiment vs price_change"""
    symbol = symbol.upper()
    data = data_service.get_scatter_data(symbol, days)

    if not data:
        raise HTTPException(status_code=404, detail=f"No scatter data for {symbol}")

    return {
        "symbol": symbol,
        "days": days,
        "data": data
    }
