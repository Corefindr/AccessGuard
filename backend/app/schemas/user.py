from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    employee_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    team: str | None = None
    lead_name: str | None = None
    lead_email: str | None = None
    manager_name: str | None = None
    manager_email: str | None = None
    active: bool = True


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
