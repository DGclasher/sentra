from fastapi import HTTPException

from app.domain.models import UserProfileUpdate
from app.repository.user_repo import UserRepository


class UserService:
    allowed_update_fields = {"email", "first_name", "last_name"}

    def __init__(self):
        self.repo = UserRepository()

    @staticmethod
    def _response(user: dict) -> dict:
        return {
            "email": user.get("email"),
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "role": user.get("role"),
        }

    def get_user(self, user_id: str) -> dict:
        user = self.repo.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return self._response(user)

    def update_user(self, user_id: str, profile: UserProfileUpdate) -> dict:
        updates = profile.model_dump(exclude_unset=True)
        updates = {
            field: value
            for field, value in updates.items()
            if field in self.allowed_update_fields
        }
        if any(value is None for value in updates.values()):
            raise HTTPException(
                status_code=422, detail="Profile fields cannot be null")
        if not updates:
            raise HTTPException(
                status_code=422, detail="At least one profile field is required"
            )

        user = self.repo.update_user(user_id, updates)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return self._response(user)
