from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Lock

import pytest
from fastapi import HTTPException

from app.domain.enums import UserRole
from app.domain.models import CurrentUser
from app.schemas.message import MessageCreate
from app.schemas.ticket import TicketCreate
from app.service.ticket_service import TicketService


USER = CurrentUser("user-1", UserRole.USER)
STAFF = CurrentUser("staff-1", UserRole.STAFF)
OTHER_STAFF = CurrentUser("staff-2", UserRole.STAFF)


class FakeRepository:
    def __init__(self):
        self.tickets = {
            "owned": {
                "ticketId": "owned",
                "userId": "user-1",
                "assignedStaffId": None,
                "status": "OPEN",
            },
            "other": {
                "ticketId": "other",
                "userId": "user-2",
                "assignedStaffId": None,
                "status": "OPEN",
            },
            "assigned": {
                "ticketId": "assigned",
                "userId": "user-2",
                "assignedStaffId": "staff-2",
                "status": "IN_PROGRESS",
            },
        }
        self.lock = Lock()
        self.messages = []

    def create_ticket(self, item):
        self.tickets[item["ticketId"]] = item
        return item

    def get_user_tickets(self, user_id):
        return [
            ticket for ticket in self.tickets.values() if ticket["userId"] == user_id
        ]

    def get_staff_tickets(self, staff_id):
        return [
            ticket
            for ticket in self.tickets.values()
            if ticket.get("assignedStaffId") == staff_id
        ]

    def get_available_tickets(self):
        return [
            ticket
            for ticket in self.tickets.values()
            if ticket["status"] == "OPEN" and ticket.get("assignedStaffId") is None
        ]

    def get_ticket(self, ticket_id):
        return self.tickets.get(ticket_id)

    def accept_ticket(self, ticket_id, staff_id, updated_at):
        with self.lock:
            ticket = self.tickets.get(ticket_id)
            if (
                not ticket
                or ticket["status"] != "OPEN"
                or ticket.get("assignedStaffId") is not None
            ):
                return None
            ticket["assignedStaffId"] = staff_id
            ticket["status"] = "IN_PROGRESS"
            return ticket

    def reject_ticket(self, ticket_id, staff_id, updated_at):
        with self.lock:
            ticket = self.tickets.get(ticket_id)
            if not ticket or ticket.get("assignedStaffId") not in (None, staff_id):
                return None
            ticket["assignedStaffId"] = None
            ticket["status"] = "OPEN"
            return ticket

    def add_message(self, item):
        self.messages.append(item)
        return item

    def get_messages(self, ticket_id):
        return [
            message for message in self.messages if message["ticketId"] == ticket_id
        ]


def service():
    repository = FakeRepository()
    return TicketService(repository), repository


def test_user_can_create_and_list_only_own_tickets():
    ticket_service, repository = service()
    created = ticket_service.create_ticket(
        USER, TicketCreate(title="Help", description="Issue")
    )

    assert created["userId"] == "user-1"
    assert ticket_service.list_user_tickets(USER) == [
        repository.tickets["owned"],
        repository.tickets[created["ticketId"]],
    ]


def test_user_cannot_read_or_message_another_users_ticket():
    ticket_service, _ = service()

    with pytest.raises(HTTPException) as read_error:
        ticket_service.get_user_ticket(USER, "other")
    with pytest.raises(HTTPException) as message_error:
        ticket_service.add_user_message(
            USER, "other", MessageCreate(content="hello"))

    assert read_error.value.status_code == 404
    assert message_error.value.status_code == 404


def test_staff_sees_available_and_only_own_assigned_tickets():
    ticket_service, _ = service()

    assert {
        ticket["ticketId"] for ticket in ticket_service.list_available_tickets(STAFF)
    } == {"owned", "other"}
    assert ticket_service.list_staff_tickets(STAFF) == []

    with pytest.raises(HTTPException) as error:
        ticket_service.get_staff_ticket(STAFF, "assigned")
    assert error.value.status_code == 404


def test_only_staff_can_accept_tickets():
    ticket_service, repository = service()

    with pytest.raises(HTTPException) as error:
        ticket_service.accept_ticket(USER, "owned")

    assert error.value.status_code == 403
    assert repository.tickets["owned"]["assignedStaffId"] is None


def test_concurrent_acceptance_claims_ticket_once():
    ticket_service, repository = service()
    staff_two = CurrentUser("staff-2", UserRole.STAFF)

    def accept(user):
        try:
            return ticket_service.accept_ticket(user, "owned")["assignedStaffId"]
        except HTTPException as error:
            return error.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(accept, [STAFF, staff_two]))

    assert set(results) in ({"staff-1", 409}, {"staff-2", 409})
    assert repository.tickets["owned"]["assignedStaffId"] in {
        "staff-1", "staff-2"}


def test_staff_message_access_follows_assignment():
    ticket_service, _ = service()
    message = MessageCreate(content="Update")

    with pytest.raises(HTTPException) as error:
        ticket_service.add_staff_message(STAFF, "assigned", message)
    assert error.value.status_code == 404

    ticket_service.accept_ticket(STAFF, "owned")
    added = ticket_service.add_staff_message(STAFF, "owned", message)
    assert added["senderId"] == "staff-1"
    assert ticket_service.get_staff_messages(STAFF, "owned") == [added]
