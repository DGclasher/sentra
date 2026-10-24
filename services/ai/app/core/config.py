import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    aws_region: str = os.getenv("AWS_REGION") or "us-east-1"
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME") or "sentra-ai-bucket"
    s3_bucket_index: str = os.getenv(
        "S3_BUCKET_INDEX") or "sentra-ai-bucket-index"
    s3_doc_storage_bucket_name: str = os.getenv("S3_DOC_STORAGE_BUCKET_NAME") or "sentra-ai-doc-bucket"
    s3_endpoint_url: str | None = os.getenv("S3_ENDPOINT_URL")
    dynamodb_endpoint_url: str | None = os.getenv("DYNAMODB_ENDPOINT_URL")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L12-v2"
    groq_api_key: str = os.getenv("GROQ_API_KEY") or ""
    staffs_table_name: str = os.getenv("STAFF_TABLE_NAME") or "Staffs"
    users_table_name: str = os.getenv("USERS_TABLE_NAME") or "Users"
    ticket_service_url: str = os.getenv("TICKET_SERVICE_URL") or "http://localhost:8000"


settings = Settings()
