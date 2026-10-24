import logging

from fastapi import HTTPException, status

from app.repository.s3_vector_repository import S3VectorRepository
from app.schemas.ai import QueryRequest, QueryResponseItem
from app.service.embedding_service import EmbeddingService
from app.service.llm_gateway import LLMError, LLMGateway

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, vector_repository=None, embedding_service=None,
                 llm_gateway=None, model=None):
        self.llm_gateway = llm_gateway or LLMGateway()
        self.embedding_service = embedding_service or EmbeddingService(
            model=model)
        self.vector_repository = vector_repository or S3VectorRepository()

    def _retrieve_vectors(self, query_req: QueryRequest) -> list[dict]:
        query_text = query_req.query.strip()
        if not query_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Query must not be empty",
            )

        try:
            query_embedding = self.embedding_service.embed(query_text)
        except Exception as error:
            logger.exception("Query embedding failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Query embedding failed",
            ) from error

        try:
            return self.vector_repository.search_vectors(
                query_embedding,
                top_k=query_req.top_k,
            )
        except Exception as error:
            logger.exception("Vector search failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Vector search failed",
            ) from error

    def query_vector(self, query_req: QueryRequest) -> list[QueryResponseItem]:
        results = []
        for vector in self._retrieve_vectors(query_req):
            metadata = vector.get("metadata") or {}
            content = metadata.get("source_text")
            distance = vector.get("distance")
            if isinstance(content, str) and distance is not None:
                results.append(QueryResponseItem(
                    content=content, score=distance))
        return results

    def query_ai(self, query_req: QueryRequest, user_id: str) -> dict[str, str]:
        vectors = self._retrieve_vectors(query_req)
        context_parts = []
        for vector in vectors:
            metadata = vector.get("metadata") or {}
            text = metadata.get("source_text")
            if not isinstance(text, str) or not text.strip():
                continue
            document_name = metadata.get("document_name", "Unknown document")
            page = metadata.get("page", "Unknown page")
            context_parts.append(
                f"Document: {document_name}\nPage: {page}\nText:\n{text.strip()}"
            )

        if not context_parts:
            return {"response": "I don't know."}

        context = "\n\n--- Retrieved document chunk ---\n\n".join(
            context_parts)
        try:
            return {
                "response": self.llm_gateway.chatbot(
                    query_req.query,
                    context,
                    user_id,
                )
            }
        except LLMError as error:
            logger.exception("LLM response generation failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Answer generation failed",
            ) from error
