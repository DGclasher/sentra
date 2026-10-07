from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.auth import require_admin
from app.domain.models import CurrentUser
from app.schemas.document import DocumentResponse
from app.service.admin_service import AdminDocumentService

router = APIRouter(prefix="/api/v1/ai/admin", tags=["Admin document endpoints"])

admin_document_service = AdminDocumentService()


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(require_admin),
):
    return await admin_document_service.ingest_document(file=file, user=user)
