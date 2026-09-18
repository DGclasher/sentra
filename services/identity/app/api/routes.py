from fastapi import APIRouter, Depends

from app.core.auth import get_current_user_id
from app.domain.models import UserProfileResponse, UserProfileUpdate
from app.service.user_service import UserService

router = APIRouter(prefix="/api/v1")
user_service = UserService()


@router.get("/me", response_model=UserProfileResponse)
def get_me(user_id: str = Depends(get_current_user_id)):
    return user_service.get_user(user_id)


@router.patch("/me", response_model=UserProfileResponse)
def update_me(
    profile: UserProfileUpdate,
    user_id: str = Depends(get_current_user_id),
):
    return user_service.update_user(user_id, profile)
