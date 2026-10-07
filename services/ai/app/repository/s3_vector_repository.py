import boto3
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3VectorRepository:
    def __init__(self):
        resource_kwargs = {"region_name": settings.aws_region}
        if settings.s3_endpoint_url:
            resource_kwargs["endpoint_url"] = settings.s3_endpoint_url
        self.client = boto3.client("s3vectors", **resource_kwargs)
        self.vector_bucket = settings.s3_bucket_name
        self.index_name = settings.s3_bucket_index

    def upload_vector(self, vectors: list[dict]) -> dict:
        logger.debug("Calling S3 Vectors put_vectors for %d vectors", len(vectors))
        return self.client.put_vectors(
            vectorBucketName=self.vector_bucket,
            indexName=self.index_name,
            vectors=vectors
        )

    def search_vectors(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        response = self.client.query_vectors(
            vectorBucketName=self.vector_bucket,
            indexName=self.index_name,
            queryVector={
                "float32": query_vector
            },
            topK=top_k,
            returnDistance=True,
            returnMetadata=True
        )
        return response.get("vectors", [])
