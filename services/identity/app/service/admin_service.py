from fastapi import HTTPException

from app.domain.models import AdminCreateStaffRequest
from app.repository.staff_repo import StaffRepository
from app.repository.cognito_repo import CognitoRepository


class AdminService:

    def __init__(self):
        self.staff_repo = StaffRepository()
        self.cognito_repo = CognitoRepository()

    @staticmethod
    def _response(staff: dict) -> dict:
        return {
            "email": staff.get("email"),
            "first_name": staff.get("first_name"),
            "last_name": staff.get("last_name"),
            "role": staff.get("role"),
            "staff_id": staff.get("staffId"),
        }

    def create_staff(
        self,
        user_id: str,
        profile: AdminCreateStaffRequest
    ) -> dict:

        # Find the person making the request
        admin = self.staff_repo.get_staff(user_id)

        if admin is None:
            raise HTTPException(
                status_code=404,
                detail="Admin user not found"
            )

        # Check their role
        if admin.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="You are not permitted to create staff"
            )

        # Create staff in Cognito
        try:
            cognito_user = self.cognito_repo.create_staff_user(
                email=str(profile.email),
                first_name=profile.first_name,
                last_name=profile.last_name,
            )

        except ValueError as error:
            raise HTTPException(
                status_code=409,
                detail=str(error)
            ) from error

        staff_id = cognito_user["sub"]

        # Create staff record
        staff = {
            "staffId": staff_id,
            "cognitoUsername": cognito_user["username"],
            "email": str(profile.email),
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "role": profile.role,
        }

        try:
            created_staff = self.staff_repo.create_staff(staff)

        except Exception as error:

            # Roll back Cognito if DynamoDB fails
            try:
                self.cognito_repo.delete_staff_user(
                    cognito_user["username"]
                )
            except Exception:
                pass

            raise HTTPException(
                status_code=500,
                detail="Unable to create staff profile"
            ) from error

        return self._response(created_staff)