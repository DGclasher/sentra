
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

        # Create staff record in DynamoDB
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

    def get_staff(
        self,
        user_id: str,
        staff_id: str
    ) -> dict:

        # Check requesting user
        admin = self.staff_repo.get_staff(user_id)

        if admin is None:
            raise HTTPException(
                status_code=404,
                detail="Admin user not found"
            )

        if admin.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="You are not permitted to view staff"
            )

        staff = self.staff_repo.get_staff(staff_id)

        if staff is None:
            raise HTTPException(
                status_code=404,
                detail="Staff user not found"
            )

        return self._response(staff)

    def list_staff(
        self,
        user_id: str
    ) -> list[dict]:

        # Check requesting user
        admin = self.staff_repo.get_staff(user_id)

        if admin is None:
            raise HTTPException(
                status_code=404,
                detail="Admin user not found"
            )

        if admin.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="You are not permitted to view staff"
            )

        staffs = self.staff_repo.get_all_staffs()

        return [
            self._response(staff)
            for staff in staffs
        ]

    def update_staff(
        self,
        user_id: str,
        staff_id: str,
        updates: dict
    ) -> dict:

        # Check requesting user
        admin = self.staff_repo.get_staff(user_id)

        if admin is None:
            raise HTTPException(
                status_code=404,
                detail="Admin user not found"
            )

        if admin.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="You are not permitted to update staff"
            )

        # Find existing staff
        existing_staff = self.staff_repo.get_staff(staff_id)

        if existing_staff is None:
            raise HTTPException(
                status_code=404,
                detail="Staff user not found"
            )

        cognito_username = existing_staff.get("cognitoUsername")

        if not cognito_username:
            raise HTTPException(
                status_code=500,
                detail="Staff Cognito username is missing"
            )

        # Separate Cognito attributes from DynamoDB fields
        cognito_updates = {}

        if "email" in updates:
            cognito_updates["email"] = updates["email"]

        if "first_name" in updates:
            cognito_updates["first_name"] = updates["first_name"]

        if "last_name" in updates:
            cognito_updates["last_name"] = updates["last_name"]

        # Update Cognito first
        try:
            if cognito_updates:
                self.cognito_repo.update_staff_user(
                    cognito_username=cognito_username,
                    email=cognito_updates.get("email"),
                    first_name=cognito_updates.get("first_name"),
                    last_name=cognito_updates.get("last_name"),
                )

        except ValueError as error:
            raise HTTPException(
                status_code=409,
                detail=str(error)
            ) from error

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail="Unable to update Cognito user"
            ) from error

        # Update DynamoDB
        try:
            updated_staff = self.staff_repo.update_staff(
                staff_id=staff_id,
                updates=updates,
            )

        except Exception as error:

            raise HTTPException(
                status_code=500,
                detail="Cognito was updated but staff profile could not be updated"
            ) from error

        if updated_staff is None:
            raise HTTPException(
                status_code=404,
                detail="Staff user not found"
            )

        return self._response(updated_staff)

    def delete_staff(
        self,
        user_id: str,
        staff_id: str
    ) -> dict:

        # Check requesting user
        admin = self.staff_repo.get_staff(user_id)

        if admin is None:
            raise HTTPException(
                status_code=404,
                detail="Admin user not found"
            )

        if admin.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="You are not permitted to delete staff"
            )

        # Find existing staff
        staff = self.staff_repo.get_staff(staff_id)

        if staff is None:
            raise HTTPException(
                status_code=404,
                detail="Staff user not found"
            )

        cognito_username = staff.get("cognitoUsername")

        if not cognito_username:
            raise HTTPException(
                status_code=500,
                detail="Staff Cognito username is missing"
            )

        # Delete from Cognito first
        try:
            self.cognito_repo.delete_staff_user(
                cognito_username=cognito_username
            )

        except ValueError as error:
            raise HTTPException(
                status_code=404,
                detail=str(error)
            ) from error

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail="Unable to delete Cognito user"
            ) from error

        # Delete from DynamoDB
        try:
            deleted = self.staff_repo.delete_staff(
                staff_id=staff_id
            )

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail="Cognito user was deleted but staff profile could not be deleted"
            ) from error

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Staff user not found"
            )

        return {
            "message": "Staff deleted successfully",
            "staff_id": staff_id,
        }

