from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.domain.models import CurrentUser
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.ticket import TicketResponse
from app.service.ticket_service import TicketService


router = APIRouter(prefix="/api/v1/staff/tickets", tags=["Staff tickets"])
ticket_service = TicketService()


@router.get("", response_model=list[TicketResponse])
def list_tickets(user: CurrentUser = Depends(get_current_user)):
    return ticket_service.list_staff_tickets(user)


@router.get("/available", response_model=list[TicketResponse])
def list_available_tickets(user: CurrentUser = Depends(get_current_user)):
    return ticket_service.list_available_tickets(user)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.get_staff_ticket(user, ticket_id)


@router.post("/{ticket_id}/accept", response_model=TicketResponse)
def accept_ticket(ticket_id: str, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.accept_ticket(user, ticket_id)


@router.post("/{ticket_id}/reject", response_model=TicketResponse)
def reject_ticket(ticket_id: str, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.reject_ticket(user, ticket_id)


@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=201)
def send_message(
    ticket_id: str,
    data: MessageCreate,
    user: CurrentUser = Depends(get_current_user),
):
    return ticket_service.add_staff_message(user, ticket_id, data)


@router.get("/{ticket_id}/messages", response_model=list[MessageResponse])
def get_messages(ticket_id: str, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.get_staff_messages(user, ticket_id)
