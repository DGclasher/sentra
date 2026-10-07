from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"

class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"