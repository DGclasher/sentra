from fastapi import APIRouter, Depends, status
from app.core.auth import is_authenticated
from app.domain.models import CurrentUser
from app.schemas.ai import QueryRequest, QueryResponse
from app.service.ai_service import AIService
from app.service.embedding_service import embedding_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI endpoints"])

ai_service = AIService(embedding_service=embedding_service)


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_status(user: CurrentUser = Depends(is_authenticated)):
    return {"status": "ok", "user_id": user.user_id, "role": user.role.value}


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_vector_store(query: QueryRequest, user: CurrentUser = Depends(is_authenticated)):
    return ai_service.query_ai(query)
