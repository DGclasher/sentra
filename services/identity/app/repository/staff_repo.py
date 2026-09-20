import boto3  # type: ignore[import-untyped]
from typing import Any

from app.core.config import settings
from botocore.exceptions import ClientError  # type: ignore[import-untyped]


class StaffRepository:
    def __init__(self):
        resource_kwargs = {
            "region_name": settings.aws_region
        }

        if settings.dynamodb_endpoint_url:
            resource_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

        dynamodb = boto3.resource(
            "dynamodb",
            **resource_kwargs
        )

        self.staff_table = dynamodb.Table(
            settings.dynamodb_staff_table_name
        )

    # CREATE
    def create_staff(
        self,
        staff: dict[str, Any]
    ) -> dict[str, Any]:

        try:
            response = self.staff_table.put_item(
                Item=staff,
                ConditionExpression="attribute_not_exists(staffId)"
            )

            return staff

        except ClientError as error:
            if (
                error.response.get("Error", {}).get("Code")
                == "ConditionalCheckFailedException"
            ):
                raise ValueError(
                    "Staff with this staff ID already exists"
                ) from error

            raise RuntimeError(
                "Unable to create staff"
            ) from error

    # GET ONE
    def get_staff(
        self,
        staff_id: str
    ) -> dict[str, Any] | None:

        try:
            print("GET_STAFF CALLED WITH:", staff_id)

            response = self.staff_table.get_item(
                Key={"staffId": staff_id}
            )

            print("STAFF TABLE RESPONSE:", response)

            staff = response.get("Item")

            if staff:
                print("FOUND IN STAFF TABLE:", staff)

            return staff

        except ClientError as error:
            print("DYNAMODB ERROR:", error)

            raise RuntimeError(
                "Unable to read staff profile"
            ) from error

    # GET ALL
    def get_all_staffs(self) -> list[dict[str, Any]]:

        staffs: list[dict[str, Any]] = []

        try:
            response = self.staff_table.scan()

            staffs.extend(response.get("Items", []))

            # DynamoDB scan can return paginated results.
            # Continue until there is no LastEvaluatedKey.
            while "LastEvaluatedKey" in response:

                response = self.staff_table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )

                staffs.extend(response.get("Items", []))

            return staffs

        except ClientError as error:
            print("DYNAMODB ERROR:", error)

            raise RuntimeError(
                "Unable to retrieve staff list"
            ) from error

    # UPDATE
    def update_staff(
        self,
        staff_id: str,
        updates: dict[str, Any]
    ) -> dict[str, Any] | None:

        if not updates:
            return self.get_staff(staff_id)

        expression_names = {
            f"#{field}": field
            for field in updates
        }

        expression_values = {
            f":{field}": value
            for field, value in updates.items()
        }

        update_expression = "SET " + ", ".join(
            f"#{field} = :{field}"
            for field in updates
        )

        try:
            response = self.staff_table.update_item(
                Key={"staffId": staff_id},
                ConditionExpression="attribute_exists(staffId)",
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

            raise RuntimeError(
                "Unable to update staff profile"
            ) from error

        return response.get("Attributes")

    # DELETE
    def delete_staff(
        self,
        staff_id: str
    ) -> bool:

        try:
            response = self.staff_table.delete_item(
                Key={"staffId": staff_id},
                ConditionExpression="attribute_exists(staffId)"
            )

            return True

        except ClientError as error:

            if (
                error.response.get("Error", {}).get("Code")
                == "ConditionalCheckFailedException"
            ):
                return False

            raise RuntimeError(
                "Unable to delete staff"
            ) from error

