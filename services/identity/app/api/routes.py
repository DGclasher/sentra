from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.domain.models import UserProfileResponse, UserProfileUpdate
from app.service.auth_service import AuthService
from app.service.user_service import UserService

router = APIRouter(prefix="/api/v1")
auth_service = AuthService()
user_service = UserService()
security = HTTPBearer()


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    try:
        return await auth_service.verify_access_token(credentials.credentials)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error


def get_current_username(token: dict[str, Any] = Depends(get_current_token)) -> str:
    username = token.get("username")
    if not username:
        raise HTTPException(
            status_code=401, detail="Token does not contain a username")
    return username


@router.get("/me", response_model=UserProfileResponse)
def get_me(username: str = Depends(get_current_username)):
    return user_service.get_user(username)


@router.patch("/me", response_model=UserProfileResponse)
def update_me(
    profile: UserProfileUpdate,
    username: str = Depends(get_current_username),
):
    return user_service.update_user(username, profile)
