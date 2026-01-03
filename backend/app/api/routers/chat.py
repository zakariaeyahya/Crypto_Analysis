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
    session_id: Optional[str] = None  # ID de session pour la memoire

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
    session_id: Optional[str] = None
    has_history: Optional[bool] = False

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

class ClearSessionRequest(BaseModel):
    session_id: str

class ClearSessionResponse(BaseModel):
    status: str
    session_id: str

# ============= ROUTER =============

router = APIRouter(
    tags=["Chat"],
    responses={500: {"description": "Erreur serveur"}}
)

@router.get("/health", response_model=HealthResponse, summary="Verifie la sante du module chat")
async def health():
    """Verifie que tous les composants RAG fonctionnent"""
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
    Envoie une question au chatbot RAG avec support de memoire conversationnelle.

    Body:
        - message: La question a poser (obligatoire)
        - crypto: Filtre optionnel (BTC, ETH, SOL)
        - session_id: ID de session pour la memoire (optionnel)

    Si session_id est fourni, le chatbot utilisera l'historique de conversation
    pour mieux comprendre le contexte des questions.
    """
    logger.info(f"Chat request: {request.message} (session: {request.session_id})")

    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="Le message ne peut pas etre vide")

    try:
        rag_service = get_rag_service()
        result = rag_service.process_query(
            question=request.message,
            crypto=request.crypto,
            session_id=request.session_id  # Passer le session_id
        )

        # Construire les metadonnees
        metadata = MetadataModel(
            num_sources=result["metadata"]["num_sources"],
            processing_time=result["metadata"]["processing_time"],
            model_used=result["metadata"]["model_used"],
            session_id=result["metadata"].get("session_id"),
            has_history=result["metadata"].get("has_history", False)
        )

        return ChatResponse(
            question=result["question"],
            answer=result["answer"],
            sources=[SourceModel(**s) for s in result["sources"]],
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur RAG: {str(e)}")

@router.post("/clear", response_model=ClearSessionResponse, summary="Efface l'historique d'une session")
async def clear_session(request: ClearSessionRequest):
    """
    Efface l'historique de conversation d'une session.

    Body:
        - session_id: ID de la session a effacer
    """
    logger.info(f"Clear session request: {request.session_id}")

    try:
        rag_service = get_rag_service()
        rag_service.clear_session(request.session_id)

        return ClearSessionResponse(
            status="cleared",
            session_id=request.session_id
        )
    except Exception as e:
        logger.error(f"Clear session error: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.get("/suggestions", response_model=SuggestionsResponse, summary="Obtient des suggestions de questions")
async def get_suggestions():
    """Retourne une liste de questions suggerees depuis prompts.py"""
    import random
    # Retourne 6 questions aleatoires parmi toutes les suggestions
    selected = random.sample(SUGGESTED_QUESTIONS, min(6, len(SUGGESTED_QUESTIONS)))
    return SuggestionsResponse(suggestions=selected)
