from datetime import datetime, timezone
import logging
from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.doc_helper import Document, DocumentHelper
from app.domain.enums import DocumentStatus
from app.domain.models import CurrentUser
from app.repository.s3_repository import S3Repository
from app.repository.s3_vector_repository import S3VectorRepository
from app.schemas.document import DocumentResponse
from app.service.embedding_service import EmbeddingError, EmbeddingService

logger = logging.getLogger(__name__)


class VectorStorageError(Exception):
    pass


class AdminDocumentService:
    def __init__(self, object_repository=None, vector_repository=None,
                 embedding_service=None, model=None):
        self.embedding_service = embedding_service or EmbeddingService(
            model=model)
        self.object_repository = object_repository or S3Repository()
        self.vector_repository = vector_repository or S3VectorRepository()

    def _add_chunks(self, chunks, document_id: str, document_name: str, batch_size: int = 500) -> None:
        try:
            vectors = []
            for chunk_number, chunk in enumerate(chunks):
                embedding = self.embedding_service.embed(chunk.page_content)
                source = chunk.metadata.get("source", "unknown")
                page = chunk.metadata.get("page", chunk_number)
                vectors.append({
                    "key": f"{source}-{page}-{chunk_number}",
                    "data": {
                        "float32": embedding,
                    },
                    "metadata": {
                        "source_text": chunk.page_content,
                        "document_name": source,
                        "page": page,
                    },
                })

                if len(vectors) == batch_size:
                    try:
                        logger.info("Uploading %d vectors to %s/%s", len(vectors),
                                    self.vector_repository.vector_bucket,
                                    self.vector_repository.index_name)
                        self.vector_repository.upload_vector(vectors)
                        vectors = []
                    except Exception as error:
                        logger.exception("Vector batch upload failed")
                        raise VectorStorageError from error

            if vectors:
                try:
                    logger.info("Uploading %d vectors to %s/%s", len(vectors),
                                self.vector_repository.vector_bucket,
                                self.vector_repository.index_name)
                    self.vector_repository.upload_vector(vectors)
                except Exception as error:
                    logger.exception("Final vector batch upload failed")
                    raise VectorStorageError from error
        except Exception as error:
            logger.exception("Vector preparation or storage failed")
            raise VectorStorageError("Failed to store vectors") from error

    async def ingest_document(self, file: UploadFile, user: CurrentUser) -> DocumentResponse:
        file_name = PurePosixPath(file.filename or "").name
        if file.content_type != "application/pdf" or not file_name.lower().endswith(".pdf"):
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                                detail="Only PDF documents are supported")
        content = await file.read()
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                                detail="Only PDF documents are supported")

        document_id = str(uuid4())
        s3_key = f"company-policies/{document_id}/{file_name}"
        try:
            self.object_repository.upload_document(
                s3_key, content, "application/pdf")
        except Exception as error:
            raise HTTPException(
                status_code=502, detail="Document upload failed") from error
        try:
            documents = DocumentHelper.load_pdf(content, file_name)
        except Exception as error:
            raise HTTPException(
                status_code=422, detail="The PDF could not be read") from error
        try:
            chunks = DocumentHelper.split_documents(documents)
        except Exception as error:
            raise HTTPException(
                status_code=422, detail="The PDF could not be processed") from error
        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="The PDF contains no extractable text; scanned PDFs are not supported",
            )
        try:
            self._add_chunks(chunks, document_id, file_name)
        except EmbeddingError as error:
            raise HTTPException(
                status_code=502, detail="Document embedding failed") from error
        except VectorStorageError as error:
            logger.exception(
                "Document vector storage failed for %s", document_id)
            raise HTTPException(
                status_code=502, detail="Document vector storage failed") from error
        return DocumentResponse(
            document_id=document_id,
            document_name=file_name,
            status=DocumentStatus.INDEXED.value,
            chunks_created=len(chunks),
            uploaded_by=user.user_id,
            created_at=datetime.now(timezone.utc),
        )
