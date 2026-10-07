import boto3
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Repository:
    def __init__(self):
        client_kwargs = {"region_name": settings.aws_region}
        if settings.s3_endpoint_url:
            client_kwargs["endpoint_url"] = settings.s3_endpoint_url
        self.client = boto3.client("s3", **client_kwargs)
        self.bucket_name = settings.s3_doc_storage_bucket_name

    def upload_document(self, key: str, content: bytes, content_type: str) -> None:
        logger.debug("Uploading document to S3 with key: %s", key)
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
