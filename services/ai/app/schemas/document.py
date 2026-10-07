from datetime import datetime
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    document_id: str
    document_name: str
    status: str
    chunks_created: int
    uploaded_by: str
    created_at: datetime