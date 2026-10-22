from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingError(Exception):
    pass


class EmbeddingService:
    def __init__(self, model=None):
        self.model = model

    def _get_model(self):
        if self.model is None:
            self.model = SentenceTransformer(
                settings.embedding_model, device="cpu")
        return self.model

    def embed(self, text: str) -> list[float]:
        embedding = self._get_model().encode(
            text,
            normalize_embeddings=True,
        ).tolist()
        if len(embedding) != 384:
            raise EmbeddingError("Unexpected embedding dimension")
        return embedding


embedding_service = EmbeddingService()
