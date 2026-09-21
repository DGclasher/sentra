import boto3  # type: ignore[import-untyped]

from app.core.config import settings
from app.domain.enums import UserRole


class IdentityRepository:
    def __init__(self):
        resource_kwargs = {"region_name": settings.aws_region}
        if settings.dynamodb_endpoint_url:
            resource_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        resource = boto3.resource("dynamodb", **resource_kwargs)
        self.users = resource.Table(settings.users_table_name)
        self.staffs = resource.Table(settings.staffs_table_name)

    def get_role(self, user_id: str) -> UserRole | None:
        user = self.users.get_item(Key={"userId": user_id}).get("Item")
        if user and user.get("role") == UserRole.USER.value:
            return UserRole.USER

        staff_response = self.staffs.scan(
            FilterExpression="staffId = :user_id",
            ExpressionAttributeValues={":user_id": user_id},
        )
        staff_items = staff_response.get("Items", [])
        if staff_items and staff_items[0].get("role") in {
            UserRole.STAFF.value,
            UserRole.ADMIN.value,
        }:
            return UserRole(staff_items[0]["role"])
        return None
