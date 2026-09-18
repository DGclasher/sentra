import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    cognito_user_pool_id: str = os.getenv("COGNITO_USER_POOL_ID") or ""
    cognito_client_id: str = os.getenv("COGNITO_CLIENT_ID") or ""
    cognito_client_secret: str = os.getenv("COGNITO_CLIENT_SECRET") or ""
    dynamodb_user_table_name: str = os.getenv("DYNAMODB_TABLE_NAME") or "Users"
    dynamodb_staff_table_name: str = os.getenv("DYNAMODB_TABLE_NAME") or "Staffs"
    dynamodb_endpoint_url: str = os.getenv("DYNAMODB_ENDPOINT_URL") or ""


settings = Settings()
