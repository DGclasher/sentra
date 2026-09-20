from fastapi import APIRouter, Depends

from app.core.auth import get_current_user_id

from app.domain.models import (
    AdminCreateStaffRequest,
    AdminCreateStaffResponse,
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