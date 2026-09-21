from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    messageId: str
    ticketId: str
    senderId: str
    senderRole: str
    content: str
    createdAt: datetime
