from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class UserRole(str, Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"
