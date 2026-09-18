import boto3  # type: ignore[import-untyped]
from typing import Any
from app.core.config import settings
from botocore.exceptions import ClientError  # type: ignore[import-untyped]


class UserRepository:
    def __init__(self):
        resource_kwargs = {"region_name": settings.aws_region}
        if settings.dynamodb_endpoint_url:
            resource_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

        self.table = boto3.resource("dynamodb", **resource_kwargs).Table(
            settings.dynamodb_table_name
        )

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        try:
            response = self.table.get_item(Key={"userId": user_id})
        except ClientError as error:
            raise RuntimeError("Unable to read user profile") from error
        return response.get("Item")

    def update_user(
        self, user_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        if not updates:
            return self.get_user(user_id)

        expression_names = {f"#{field}": field for field in updates}
        expression_values = {
            f":{field}": value for field, value in updates.items()}
        update_expression = "SET " + ", ".join(
            f"#{field} = :{field}" for field in updates
        )

        try:
            response = self.table.update_item(
                Key={"userId": user_id},
                ConditionExpression="attribute_exists(userId)",
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values,
                ReturnValues="ALL_NEW",
            )
        except ClientError as error:
            if (
                error.response.get("Error", {}).get("Code")
                == "ConditionalCheckFailedException"
            ):
                return None
            raise RuntimeError("Unable to update user profile") from error
        return response.get("Attributes")
