from dataclasses import dataclass
from app.domain.enums import UserRole, DocumentStatus

@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: UserRole

    @property
    def is_staff(self) -> bool:
        return self.role in {UserRole.STAFF, UserRole.ADMIN}
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

class Document:
    document_id: str
    file_name: str
    s3_key: str
    status: DocumentStatus
    chunk_count: int
    uploaded_by: str
    created_at: str