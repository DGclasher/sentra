
from fastapi import APIRouter, Depends

from app.core.auth import get_current_user_id

from app.domain.models import (
    AdminCreateStaffRequest,
    AdminCreateStaffResponse,
    AdminUpdateStaffRequest,
    UserProfileResponse,
)

from app.service.admin_service import AdminService


router = APIRouter(prefix="/api/v1/admin")

admin_service = AdminService()


@router.post(
    "/staff",
    response_model=AdminCreateStaffResponse
)
def create_staff(
    profile: AdminCreateStaffRequest,
    user_id: str = Depends(get_current_user_id),
):
    return admin_service.create_staff(
        user_id,
        profile
    )


@router.get(
    "/staff",
    response_model=list[UserProfileResponse]
)
def list_staff(
    user_id: str = Depends(get_current_user_id),
):
    return admin_service.list_staff(
        user_id
    )


@router.get(
    "/staff/{staff_id}",
    response_model=UserProfileResponse
)
def get_staff(
    staff_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return admin_service.get_staff(
        user_id,
        staff_id
    )


@router.patch(
    "/staff/{staff_id}",
    response_model=UserProfileResponse
)
def update_staff(
    staff_id: str,
    updates: AdminUpdateStaffRequest,
    user_id: str = Depends(get_current_user_id),
):
    return admin_service.update_staff(
        user_id,
        staff_id,
        updates.model_dump(exclude_none=True)
    )


@router.delete(
    "/staff/{staff_id}"
)
def delete_staff(
    staff_id: str,
    user_id: str = Depends(get_current_user_id),
):
    return admin_service.delete_staff(
        user_id,
        staff_id
    )

