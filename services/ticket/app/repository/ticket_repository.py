from datetime import datetime
from typing import Any

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from app.core.config import settings


class TicketRepository:
    def __init__(self):
        resource_kwargs = {"region_name": settings.aws_region}
        if settings.dynamodb_endpoint_url:
            resource_kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        resource = boto3.resource("dynamodb", **resource_kwargs)
        self.tickets = resource.Table(settings.tickets_table_name)
        self.messages = resource.Table(settings.messages_table_name)

    def create_ticket(self, item: dict[str, Any]) -> dict[str, Any]:
        self.tickets.put_item(Item=item)
        return item

    def get_user_tickets(self, user_id: str) -> list[dict[str, Any]]:
        response = self.tickets.scan(
            FilterExpression="userId = :user_id",
            ExpressionAttributeValues={":user_id": user_id},
        )
        return response.get("Items", [])

    def get_staff_tickets(self, staff_id: str) -> list[dict[str, Any]]:
        response = self.tickets.scan(
            FilterExpression="assignedStaffId = :staff_id",
            ExpressionAttributeValues={":staff_id": staff_id},
        )
        return response.get("Items", [])

    def get_available_tickets(self) -> list[dict[str, Any]]:
        response = self.tickets.scan(
            FilterExpression="#status = :open AND (attribute_not_exists(assignedStaffId) OR attribute_type(assignedStaffId, :null_type))",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":open": "OPEN", ":null_type": "NULL"},
        )
        return response.get("Items", [])

    def get_ticket(self, ticket_id: str) -> dict[str, Any] | None:
        print("Ticket ID from get_ticket function call", ticket_id)
        return self.tickets.get_item(Key={"ticketId": ticket_id}).get("Item")

    def accept_ticket(
        self, ticket_id: str, staff_id: str, updated_at: datetime
    ) -> dict[str, Any] | None:
        try:
            response = self.tickets.update_item(
                Key={"ticketId": ticket_id},
                ConditionExpression="#status = :open AND (attribute_not_exists(assignedStaffId) OR attribute_type(assignedStaffId, :null_type))",
                UpdateExpression="SET assignedStaffId = :staff, #status = :in_progress, updatedAt = :updated",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":open": "OPEN",
                    ":in_progress": "IN_PROGRESS",
                    ":staff": staff_id,
                    ":updated": updated_at.isoformat(),
                    ":null_type": "NULL",
                },
                ReturnValues="ALL_NEW",
            )
        except ClientError as error:
            if (
                error.response.get("Error", {}).get("Code")
                == "ConditionalCheckFailedException"
            ):
                return None
            raise
        return response.get("Attributes")

    def reject_ticket(
        self, ticket_id: str, staff_id: str, updated_at: datetime
    ) -> dict[str, Any] | None:
        try:
            response = self.tickets.update_item(
                Key={"ticketId": ticket_id},
                ConditionExpression="attribute_not_exists(assignedStaffId) OR attribute_type(assignedStaffId, :null_type) OR assignedStaffId = :staff",
                UpdateExpression="SET assignedStaffId = :empty, #status = :open, updatedAt = :updated",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":staff": staff_id,
                    ":empty": None,
                    ":open": "OPEN",
                    ":updated": updated_at.isoformat(),
                    ":null_type": "NULL",
                },
                ReturnValues="ALL_NEW",
            )
        except ClientError as error:
            if (
                error.response.get("Error", {}).get("Code")
                == "ConditionalCheckFailedException"
            ):
                return None
            raise
        return response.get("Attributes")

    def add_message(self, item: dict[str, Any]) -> dict[str, Any]:
        self.messages.put_item(Item=item)
        return item

    def get_messages(self, ticket_id: str) -> list[dict[str, Any]]:
        response = self.messages.scan(
            FilterExpression="ticketId = :ticket_id",
            ExpressionAttributeValues={":ticket_id": ticket_id},
        )
        return response.get("Items", [])
