from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException

from app.domain.enums import TicketStatus
from app.domain.models import CurrentUser
from app.repository.ticket_repository import TicketRepository
from app.schemas.message import MessageCreate
from app.schemas.ticket import TicketCreate


class TicketService:
    def __init__(self, repository: TicketRepository | None = None):
        self.repository = repository or TicketRepository()

    def create_ticket(self, user: CurrentUser, data: TicketCreate) -> dict:
        now = datetime.now(timezone.utc)
        item = {
            "ticketId": str(uuid4()),
            "userId": user.user_id,
            "title": data.title,
            "description": data.description,
            "status": TicketStatus.OPEN.value,
            "assignedStaffId": None,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
        return self.repository.create_ticket(item)

    def list_user_tickets(self, user: CurrentUser) -> list[dict]:
        self._require_user(user)
        return self.repository.get_user_tickets(user.user_id)

    def list_staff_tickets(self, user: CurrentUser) -> list[dict]:
        self._require_staff(user)
        return self.repository.get_staff_tickets(user.user_id)

    def list_available_tickets(self, user: CurrentUser) -> list[dict]:
        self._require_staff(user)
        return self.repository.get_available_tickets()

    def get_user_ticket(self, user: CurrentUser, ticket_id: str) -> dict:
        self._require_user(user)
        ticket = self._get_ticket(ticket_id)
        if ticket.get("userId") != user.user_id:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket

    def get_staff_ticket(self, user: CurrentUser, ticket_id: str) -> dict:
        self._require_staff(user)
        ticket = self._get_ticket(ticket_id)
        if ticket.get("assignedStaffId") is not None and ticket.get("assignedStaffId") == user.user_id:
            return ticket
        raise HTTPException(status_code=404, detail="Ticket not found")

    def accept_ticket(self, user: CurrentUser, ticket_id: str) -> dict:
        self._require_staff(user)
        ticket = self.repository.accept_ticket(
            ticket_id, user.user_id, self._now())
        if ticket is None:
            raise HTTPException(
                status_code=409, detail="Ticket is no longer available")
        return ticket

    def reject_ticket(self, user: CurrentUser, ticket_id: str) -> dict:
        self._require_staff(user)
        ticket = self.repository.reject_ticket(
            ticket_id, user.user_id, self._now())
        if ticket is None:
            raise HTTPException(
                status_code=409, detail="Ticket is assigned to another staff member"
            )
        return ticket

    def add_user_message(
        self, user: CurrentUser, ticket_id: str, data: MessageCreate
    ) -> dict:
        self.get_user_ticket(user, ticket_id)
        return self._add_message(user, ticket_id, data)

    def add_staff_message(
        self, user: CurrentUser, ticket_id: str, data: MessageCreate
    ) -> dict:
        self.get_staff_ticket(user, ticket_id)
        return self._add_message(user, ticket_id, data)

    def get_user_messages(self, user: CurrentUser, ticket_id: str) -> list[dict]:
        self.get_user_ticket(user, ticket_id)
        return self.repository.get_messages(ticket_id)

    def get_staff_messages(self, user: CurrentUser, ticket_id: str) -> list[dict]:
        self.get_staff_ticket(user, ticket_id)
        return self.repository.get_messages(ticket_id)

    def _add_message(
        self, user: CurrentUser, ticket_id: str, data: MessageCreate
    ) -> dict:
        now = self._now()
        return self.repository.add_message(
            {
                "messageId": str(uuid4()),
                "ticketId": ticket_id,
                "senderId": user.user_id,
                "senderRole": user.role.value,
                "content": data.content,
                "createdAt": now.isoformat(),
            }
        )

    def _get_ticket(self, ticket_id: str) -> dict:
        print(ticket_id)
        ticket = self.repository.get_ticket(ticket_id)
        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket

    @staticmethod
    def _require_staff(user: CurrentUser) -> None:
        if not user.is_staff:
            raise HTTPException(
                status_code=403, detail="Staff access required")

    @staticmethod
    def _require_user(user: CurrentUser) -> None:
        if user.is_staff:
            raise HTTPException(status_code=403, detail="User access required")

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
