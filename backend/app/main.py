from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import cryptos, sentiment, analysis, events, chat
from app.core.config import settings

app = FastAPI(
    title="Crypto Dashboard API",
    description="API pour l'analyse de sentiment des cryptomonnaies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cryptos.router, prefix="/api/cryptos", tags=["Cryptos"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["Sentiment"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Crypto Dashboard API"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
