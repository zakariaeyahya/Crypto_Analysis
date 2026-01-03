from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.rag.rag_service import get_rag_service
from app.rag.logger import get_logger
from app.rag.prompts import SUGGESTED_QUESTIONS

logger = get_logger("chat_router")

# ============= MODELS =============

class ChatRequest(BaseModel):
    message: str
    crypto: Optional[str] = None

class SourceModel(BaseModel):
    id: str
    type: str
    crypto: str
    text: str
    score: float

class MetadataModel(BaseModel):
    num_sources: int
    processing_time: float
    model_used: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceModel]
    metadata: MetadataModel

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, str]

class SuggestionsResponse(BaseModel):
    suggestions: List[str]

# ============= ROUTER =============

router = APIRouter(
    tags=["Chat"],
    responses={500: {"description": "Erreur serveur"}}
)

@router.get("/health", response_model=HealthResponse, summary="Vérifie la santé du module chat")
async def health():
    """Vérifie que tous les composants RAG fonctionnent"""
    logger.info("Health check requested")
    try:
        rag_service = get_rag_service()
        health_info = rag_service.health_check()
        
        return HealthResponse(
            status=health_info.get("overall", "unknown"),
            components=health_info
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/", response_model=ChatResponse, summary="Envoie un message au chatbot")
async def chat(request: ChatRequest):
    """
    Envoie une question au chatbot RAG.
    
    Body:
        - message: La question à poser (obligatoire)
        - crypto: Filtre optionnel (BTC, ETH, SOL)
    """
    logger.info(f"Chat request: {request.message}")
    
    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide")
    
    try:
        rag_service = get_rag_service()
        result = rag_service.process_query(
            question=request.message,
            crypto=request.crypto
        )
        
        return ChatResponse(
            question=result["question"],
            answer=result["answer"],
            sources=[SourceModel(**s) for s in result["sources"]],
            metadata=MetadataModel(**result["metadata"])
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur RAG: {str(e)}")

@router.get("/suggestions", response_model=SuggestionsResponse, summary="Obtient des suggestions de questions")
async def get_suggestions():
    """Retourne une liste de questions suggerees depuis prompts.py"""
    import random
    # Retourne 6 questions aleatoires parmi toutes les suggestions
    selected = random.sample(SUGGESTED_QUESTIONS, min(6, len(SUGGESTED_QUESTIONS)))
    return SuggestionsResponse(suggestions=selected)