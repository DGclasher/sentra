from app.domain.models import CurrentUser
from app.schemas.message import MessageCreate
from app.service.ticket_service import TicketService


class AdminTicketService(TicketService):
    def list_tickets(self, user: CurrentUser) -> list[dict]:
        return self.list_admin_tickets(user)

    def list_available(self, user: CurrentUser) -> list[dict]:
        self._require_admin(user)
        return self.repository.get_available_tickets()

    def get_ticket(self, user: CurrentUser, ticket_id: str) -> dict:
        return self.get_admin_ticket(user, ticket_id)

    def accept(self, user: CurrentUser, ticket_id: str) -> dict:
        return self.accept_admin_ticket(user, ticket_id)

    def reject(self, user: CurrentUser, ticket_id: str) -> dict:
        return self.reject_admin_ticket(user, ticket_id)

    def delete(self, user: CurrentUser, ticket_id: str) -> None:
        return self.delete_ticket(user, ticket_id)

    def add_message(
        self, user: CurrentUser, ticket_id: str, data: MessageCreate
    ) -> dict:
        return self.add_admin_message(user, ticket_id, data)

    def get_messages(self, user: CurrentUser, ticket_id: str) -> list[dict]:
        return self.get_admin_messages(user, ticket_id)
