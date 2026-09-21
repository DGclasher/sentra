from fastapi import Header, HTTPException

from app.domain.enums import UserRole
from app.domain.models import CurrentUser
from app.repository.identity_repository import IdentityRepository


identity_repository = IdentityRepository()


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id")
) -> CurrentUser:
    if not x_user_id:
        raise HTTPException(
            status_code=401, detail="X-User-Id header is required")

    role = identity_repository.get_role(x_user_id)
    if role is None:
        raise HTTPException(status_code=401, detail="Unknown user")
    return CurrentUser(user_id=x_user_id, role=role)


def require_staff(user: CurrentUser) -> CurrentUser:
    if user.role not in {UserRole.STAFF, UserRole.ADMIN}:
        raise HTTPException(status_code=403, detail="Staff access required")
    return user
