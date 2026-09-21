from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import TicketStatus


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class TicketResponse(BaseModel):
    ticketId: str
    userId: str
    title: str
    description: str
    status: TicketStatus
    assignedStaffId: str | None
    createdAt: datetime
    updatedAt: datetime
