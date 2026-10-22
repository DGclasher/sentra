from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.auth import require_admin
from app.domain.models import CurrentUser
from app.schemas.document import DocumentResponse
from app.service.admin_service import AdminDocumentService
from app.service.embedding_service import embedding_service

router = APIRouter(prefix="/api/v1/ai/admin",
                   tags=["Admin document endpoints"])

admin_document_service = AdminDocumentService(
    embedding_service=embedding_service)


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(require_admin),
):
    return await admin_document_service.ingest_document(file=file, user=user)
