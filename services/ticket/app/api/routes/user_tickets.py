from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.domain.models import CurrentUser
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.ticket import TicketCreate, TicketResponse
from app.service.ticket_service import TicketService


router = APIRouter(prefix="/api/v1/user/tickets", tags=["User tickets"])
ticket_service = TicketService()


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(data: TicketCreate, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.create_ticket(user, data)


@router.get("", response_model=list[TicketResponse])
def list_tickets(user: CurrentUser = Depends(get_current_user)):
    return ticket_service.list_user_tickets(user)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.get_user_ticket(user, ticket_id)


@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=201)
def send_message(
    ticket_id: str,
    data: MessageCreate,
    user: CurrentUser = Depends(get_current_user),
):
    return ticket_service.add_user_message(user, ticket_id, data)


@router.get("/{ticket_id}/messages", response_model=list[MessageResponse])
def get_messages(ticket_id: str, user: CurrentUser = Depends(get_current_user)):
    return ticket_service.get_user_messages(user, ticket_id)
