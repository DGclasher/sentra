import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    aws_region: str = os.getenv("AWS_REGION") or "us-east-1"
    users_table_name: str = os.getenv("USERS_TABLE_NAME") or "Users"
    staffs_table_name: str = os.getenv("STAFFS_TABLE_NAME") or "Staffs"
    tickets_table_name: str = os.getenv("TICKETS_TABLE_NAME") or "Tickets"
    messages_table_name: str = os.getenv("MESSAGES_TABLE_NAME") or "Messages"
    dynamodb_endpoint_url: str = os.getenv("DYNAMODB_ENDPOINT_URL") or ""


settings = Settings()
