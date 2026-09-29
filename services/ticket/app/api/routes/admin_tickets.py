from fastapi import APIRouter, Depends, Response, status

from app.core.auth import require_admin
from app.domain.models import CurrentUser
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.ticket import TicketResponse
from app.service.admin_ticket_service import AdminTicketService


router = APIRouter(prefix="/api/v1/tickets/admin", tags=["Admin tickets"])
ticket_service = AdminTicketService()


@router.get("", response_model=list[TicketResponse])
def list_tickets(user: CurrentUser = Depends(require_admin)):
    return ticket_service.list_tickets(user)


@router.get("/available", response_model=list[TicketResponse])
def list_available_tickets(user: CurrentUser = Depends(require_admin)):
    return ticket_service.list_available(user)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, user: CurrentUser = Depends(require_admin)):
    return ticket_service.get_ticket(user, ticket_id)


@router.post("/{ticket_id}/accept", response_model=TicketResponse)
def accept_ticket(ticket_id: str, user: CurrentUser = Depends(require_admin)):
    return ticket_service.accept(user, ticket_id)


@router.post("/{ticket_id}/reject", response_model=TicketResponse)
def reject_ticket(ticket_id: str, user: CurrentUser = Depends(require_admin)):
    return ticket_service.reject(user, ticket_id)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: str, user: CurrentUser = Depends(require_admin)):
    ticket_service.delete(user, ticket_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=201)
def send_message(
    ticket_id: str,
    data: MessageCreate,
    user: CurrentUser = Depends(require_admin),
):
    return ticket_service.add_message(user, ticket_id, data)


@router.get("/{ticket_id}/messages", response_model=list[MessageResponse])
def get_messages(ticket_id: str, user: CurrentUser = Depends(require_admin)):
    return ticket_service.get_messages(user, ticket_id)
