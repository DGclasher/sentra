from dataclasses import dataclass

from app.domain.enums import UserRole


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: UserRole

    @property
    def is_staff(self) -> bool:
        return self.role in {UserRole.STAFF, UserRole.ADMIN}
