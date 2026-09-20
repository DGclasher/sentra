from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal


class UserProfileResponse(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    role: str


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)


class AdminCreateStaffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    role: Literal["staff"] = "staff"


class AdminUpdateStaffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    first_name: str | None = Field(default=None, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)


class AdminCreateStaffResponse(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    role: Literal["staff"]
    staff_id: str